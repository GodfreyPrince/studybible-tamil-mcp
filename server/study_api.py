"""Study resource HTTP API for the Tamil Bible Android app.

Serves the Tamil study layer of study_bible_tamil.db (the same data layer the
Tamil MCP server uses) over plain REST, so the app can fetch study content
from this PC now and from the VPS later by just changing the URL.

Run:  py -3.11 server/study_api.py          (default port 8787, prints LAN IPs)
Env:  STUDY_BIBLE_TAMIL_DB=/path/to/db      (default: ../data/study_bible_tamil.db)
      STUDY_API_PORT=8787

Endpoints:
  GET /api/verse?ref=Jhn.3.16   full study payload for one verse
  GET /api/word?strongs=G26     word study (lexicon + renderings + articles)
  GET /api/search?q=...         Tamil full-text verse search
  GET /api/health               status
  GET /api/pack                 download the offline study pack (zip)
"""
import asyncio
import json
import os
import secrets
import socket
import sqlite3
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from study_bible_tamil_mcp import database as dbmod  # noqa: E402

DB_PATH = os.environ.get(
    "STUDY_BIBLE_TAMIL_DB", str(ROOT / "data" / "study_bible_tamil.db"))
PORT = int(os.environ.get("STUDY_API_PORT", "8787"))
PACK = ROOT / "data" / "tamil_study_pack.zip"
KEY_FILE = Path(__file__).resolve().parent / "study_key.txt"


def load_api_key():
    """Shared secret: env STUDY_API_KEY, else study_key.txt (created on first run)."""
    k = os.environ.get("STUDY_API_KEY")
    if k:
        return k.strip()
    if KEY_FILE.exists():
        return KEY_FILE.read_text(encoding="utf-8").strip()
    k = secrets.token_hex(16)
    KEY_FILE.write_text(k, encoding="utf-8")
    return k


API_KEY = load_api_key()

# --- simple per-IP rate limiting (in-memory; resets on restart) ---
# General: 120 requests/min per IP. Pack: 6 downloads/hour per IP.
# Limits are deliberately generous — Indian mobile carriers put many users
# behind one IP, so real humans must never hit these.
import time
from collections import defaultdict, deque

RATE_GENERAL = (120, 60)
RATE_PACK = (6, 3600)
_hits = defaultdict(deque)


def rate_ok(ip, path, now):
    limit, window = RATE_PACK if path == "/api/pack" else RATE_GENERAL
    dq = _hits[(ip, limit)]
    while dq and now - dq[0] > window:
        dq.popleft()
    if len(dq) >= limit:
        return False
    dq.append(now)
    return True

db = dbmod.StudyBibleDB(DB_PATH)
loop = asyncio.new_event_loop()
threading.Thread(target=loop.run_forever, daemon=True).start()


def run(coro):
    return asyncio.run_coroutine_threadsafe(coro, loop).result(60)


def verse_parts(ref):
    """'Jhn.3.16' -> ('Jhn', 3, 16)"""
    try:
        book, ch, vs = ref.split(".")
        return book, int(ch), int(vs)
    except Exception:
        return None, None, None


async def api_verse(ref):
    b, c, v = verse_parts(ref)
    out = {"ref": ref, "tamil_ref": dbmod.tamil_reference(ref)}
    row = await db._fetchone(
        "SELECT book, text_english AS english, text_tamil, text_tamil_trad FROM verses WHERE reference=?",
        (ref,))
    if row:
        out["text"] = {"book": row["book"], "english": row["english"],
                       "irv": row["text_tamil"], "bsi": row["text_tamil_trad"]}

    if b:
        out["words"] = (await db._fetchall(
            """SELECT a.tamil_word, a.strongs, a.lemma, a.morph, g.gloss_tamil
               FROM ta_word_alignment a LEFT JOIN ta_gloss g ON g.strongs = a.strongs
               WHERE a.book=? AND a.chapter=? AND a.verse=? AND a.strongs != ''
               ORDER BY a.seq""", (b, c, v)))
        out["notes"] = (await db._fetchall(
            "SELECT phrase, body FROM ta_notes WHERE book=? AND chapter=? AND verse=? ORDER BY id",
            (b, c, v)))
        out["questions"] = (await db._fetchall(
            "SELECT question, answer FROM ta_questions WHERE book=? AND chapter=? AND verse=? ORDER BY id",
            (b, c, v)))
        intro = await db.get_book_intro(b)
        if intro:
            out["intro"] = intro
        out["theology"] = (await db._fetchall(
            """SELECT tc.id, tc.source_author, tc.title, tc.title_ta,
                      tc.summary_ta, tc.detail_ta
               FROM theology_verse_index vi JOIN theology_content tc ON tc.id = vi.content_id
               WHERE vi.reference = ? AND (tc.title_ta IS NOT NULL AND tc.title_ta != '')
               ORDER BY vi.relevance DESC LIMIT 5""", (ref,)))
        out["ane"] = (await db._fetchall(
            """SELECT ae.id, ae.title, ae.title_ta, ae.summary_ta
               FROM ane_book_mappings m JOIN ane_entries ae ON ae.id = m.entry_id
               WHERE m.book = ? AND (m.chapter_start IS NULL OR ? BETWEEN m.chapter_start AND COALESCE(m.chapter_end, m.chapter_start))
                 AND (ae.title_ta IS NOT NULL AND ae.title_ta != '')
               LIMIT 3""", (b, c)))
        strongs = [w["strongs"] for w in out.get("words", []) if w["strongs"]]
        articles, seen = [], set()
        for s in strongs:
            for a in await db.get_ta_dictionary_by_strongs(s):
                if a["id"] not in seen:
                    seen.add(a["id"])
                    articles.append({"slug": a.get("slug"), "title": a.get("title"),
                                     "body": a.get("body")})
        out["dictionary"] = articles[:6]
    return out


async def api_word(strongs):
    entry = await db.get_lexicon_entry(strongs)
    g = await db._fetchone(
        "SELECT gloss_tamil, renderings FROM ta_gloss WHERE strongs=?", (strongs,))
    articles = await db.get_ta_dictionary_by_strongs(strongs)
    out = {"strongs": strongs}
    if entry:
        out.update({k: entry.get(k) for k in
                    ("word", "transliteration", "short_definition", "full_definition",
                     "gloss_tamil", "language")})
    if g:
        out["gloss_tamil"] = g["gloss_tamil"]
        try:
            out["renderings"] = json.loads(g["renderings"] or "[]")[:12]
        except Exception:
            out["renderings"] = []
    out["articles"] = [{"slug": a.get("slug"), "title": a.get("title"),
                        "body": a.get("body")} for a in articles[:3]]
    return out


async def api_search(q):
    return await db.search_tamil_verses(q, limit=40)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        # /api/health stays open for uptime checks; everything else needs the key
        if u.path != "/api/health":
            ip = self.headers.get("CF-Connecting-IP") or self.client_address[0]
            if not rate_ok(ip, u.path, time.time()):
                self._json({"error": "rate_limited"}, 429)
                return
            given = self.headers.get("X-Study-Key") or (q.get("key") or [""])[0]
            if not given or not secrets.compare_digest(given, API_KEY):
                self._json({"error": "unauthorized"}, 401)
                return
        try:
            if u.path == "/api/health":
                n = run(db._fetchone("SELECT COUNT(*) n FROM verses"))["n"]
                self._json({"ok": True, "verses": n,
                            "pack": PACK.stat().st_size if PACK.exists() else 0})
            elif u.path == "/api/verse":
                ref = (q.get("ref") or [""])[0]
                if not ref:
                    return self._json({"error": "ref required"}, 400)
                self._json(run(api_verse(ref)))
            elif u.path == "/api/word":
                s = (q.get("strongs") or [""])[0]
                if not s:
                    return self._json({"error": "strongs required"}, 400)
                self._json(run(api_word(s)))
            elif u.path == "/api/search":
                term = (q.get("q") or [""])[0]
                if not term:
                    return self._json({"error": "q required"}, 400)
                self._json({"results": run(api_search(term))})
            elif u.path == "/api/pack":
                if not PACK.exists():
                    return self._json({"error": "pack not built"}, 404)
                body = PACK.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Content-Disposition",
                                 'attachment; filename="tamil_study_pack.zip"')
                self.end_headers()
                self.wfile.write(body)
            else:
                self._json({"error": "unknown endpoint"}, 404)
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def log_message(self, fmt, *args):
        print("[api]", fmt % args)


def lan_ips():
    ips = set()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None):
            ip = info[4][0]
            if ip.startswith(("192.168.", "10.", "172.")) and "." in ip:
                ips.add(ip)
    except Exception:
        pass
    return sorted(ips)


if __name__ == "__main__":
    run(db.connect())
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Study API on port {PORT} — db: {DB_PATH}")
    print(f"  shared key: {API_KEY}   (file: {KEY_FILE.name} — edit + restart to rotate)")
    for ip in lan_ips():
        print(f"  phone URL (same Wi-Fi): http://{ip}:{PORT}")
    print("  emulator URL          : http://10.0.2.2:{PORT}")
    srv.serve_forever()
