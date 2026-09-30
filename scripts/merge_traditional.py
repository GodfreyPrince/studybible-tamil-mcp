#!/usr/bin/env python3
"""
Merge the traditional Tamil Bible text (BSI Tamil — the classic church
translation, public domain) into study_bible_tamil.db as verses.text_tamil_trad.

Input: TamilBible/app/src/main/assets/tamil_bsi.json (from the TamilBible app
asset prepared in a companion session):
  { "books": [ { "n": name, "s": abbr, "t": 0|1, "c": [[verse, ...], ...] } ],
    "ptitles": { "<psalm#>": title, ... } }

Also merges the traditional Tamil book names into ta_data/book_names.json alt
lists so the reference parser accepts them (e.g. 'தொடக்க நூல் 1:1').
"""
import json
import re
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WS = ROOT.parent
BSI_JSON = WS / "TamilBible" / "app" / "src" / "main" / "assets" / "tamil_bsi.json"
DB = ROOT / "data" / "study_bible_tamil.db"
BOOK_NAMES = ROOT / "src" / "study_bible_tamil_mcp" / "ta_data" / "book_names.json"

# canonical book codes in BSI file order (Genesis .. Revelation)
BOOK_CODES = [
    "Gen", "Exo", "Lev", "Num", "Deu", "Jos", "Jdg", "Rut", "1Sa", "2Sa",
    "1Ki", "2Ki", "1Ch", "2Ch", "Ezr", "Neh", "Est", "Job", "Psa", "Pro",
    "Ecc", "Sng", "Isa", "Jer", "Lam", "Ezk", "Dan", "Hos", "Jol", "Amo",
    "Oba", "Jon", "Mic", "Nam", "Hab", "Zep", "Hag", "Zec", "Mal",
    "Mat", "Mrk", "Luk", "Jhn", "Act", "Rom", "1Co", "2Co", "Gal", "Eph",
    "Php", "Col", "1Th", "2Th", "1Ti", "2Ti", "Tit", "Phm", "Heb", "Jas",
    "1Pe", "2Pe", "1Jn", "2Jn", "3Jn", "Jud", "Rev",
]


def clean(s: str) -> str:
    s = s.replace("\r", " ").replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def main():
    t0 = time.time()
    data = json.loads(BSI_JSON.read_text(encoding="utf-8"))
    books = data["books"]
    ptitles = data.get("ptitles", {})
    assert len(books) == 66, f"expected 66 books, got {len(books)}"

    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA journal_mode=WAL")
    cur = conn.cursor()
    cols = {r[1] for r in cur.execute("PRAGMA table_info(verses)")}
    if "text_tamil_trad" not in cols:
        cur.execute("ALTER TABLE verses ADD COLUMN text_tamil_trad TEXT")

    db_keys = {}
    for ref, b, c, v in cur.execute("SELECT reference, book, chapter, verse FROM verses"):
        db_keys[(b, c, v)] = ref

    merged = added = 0
    unmatched = []
    for i, b in enumerate(books):
        code = BOOK_CODES[i]
        for ch_idx, chapter in enumerate(b["c"], start=1):
            for v_idx, text in enumerate(chapter, start=1):
                key = (code, ch_idx, v_idx)
                cleaned = clean(text)
                if not cleaned:
                    continue
                if key in db_keys:
                    cur.execute("UPDATE verses SET text_tamil_trad=? WHERE reference=?",
                                (cleaned, db_keys[key]))
                    merged += 1
                else:
                    unmatched.append(key)

    # Psalm superscriptions (verse 0 rows) <- ptitles
    n_title = 0
    if ptitles:
        for k, title in ptitles.items():
            ps = re.sub(r"\D", "", str(k))
            if not ps:
                continue
            rows = cur.execute(
                "SELECT reference FROM verses WHERE book='Psa' AND chapter=? AND verse=0",
                (int(ps),)).fetchall()
            if rows:
                cur.execute(
                    "UPDATE verses SET text_tamil_trad=? WHERE reference=? AND text_tamil_trad IS NULL",
                    (clean(str(title)), rows[0][0]))
                n_title += 1

    n_trad = cur.execute(
        "SELECT COUNT(*) FROM verses WHERE text_tamil_trad IS NOT NULL").fetchone()[0]
    n_total = cur.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
    conn.commit()
    print(f"traditional text merged: {merged} verses, +{n_title} psalm titles -> verse 0")
    print(f"coverage: {n_trad}/{n_total} verse rows have text_tamil_trad")
    if unmatched:
        print(f"BSI verses with no DB target: {len(unmatched)} e.g. {unmatched[:8]}")

    # ---- book names: add traditional BSI names as accepted aliases --------
    bn = json.loads(BOOK_NAMES.read_text(encoding="utf-8"))
    changed = 0
    for i, b in enumerate(books):
        code = BOOK_CODES[i]
        entry = bn.setdefault(code, {"tamil": b["n"], "short": b["s"], "alt": []})
        alts = entry.setdefault("alt", [])
        for form in (b["n"], b["s"]):
            form = form.strip()
            if form and form != entry["tamil"] and form not in alts:
                alts.append(form)
                changed += 1
    BOOK_NAMES.write_text(json.dumps(bn, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"book_names.json: +{changed} traditional aliases")

    conn.execute("VACUUM")
    conn.close()
    print(f"done in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
