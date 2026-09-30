"""Apply lexicon_gloss_tamil.json hand-gloss overlay to study_bible_tamil.db.

Two modes:
  python apply_lexicon_gloss_overlay.py check   -> dry-run: print every intended
      insert/update next to the row's current word so glosses can be eyeballed.
  python apply_lexicon_gloss_overlay.py apply   -> do it.

Greek keys are stored unpadded (G444), Hebrew as H + 4 digits (H0430); the
overlay file uses uniform 5-digit padding for Greek, so keys are normalized
here. Object entries (word/translit/def) are INSERTed for terms missing from
the lexicon; plain-string entries UPDATE gloss_tamil on existing rows.
"""
import json
import sqlite3
import sys

DB = "data/study_bible_tamil.db"
SRC = "translations/lexicon_gloss_tamil.json"

data = json.load(open(SRC, encoding="utf-8"))


def normalize(key):
    if key.startswith("G"):
        return "G" + key[1:].lstrip("0") or "G0"
    return key


def alt_keys(key):
    """All padding variants the lexicon might store this Strong's number as.

    The canonical format is 4-digit padded (G0435), but the table also
    contains unpadded (G846), 5-digit padded (G0023-style), and other
    historical formats, so every candidate is tried.
    """
    out = {key}
    if key and key[0] in ("G", "H"):
        num = key[1:]
        for n in (4, 5, 3, 2):
            out.add(key[0] + num.zfill(n))
        out.add(key[0] + num.lstrip("0"))
    return out


conn = sqlite3.connect(DB)
cur = conn.cursor()

inserts, updates = [], []
for k, v in data.items():
    nk = normalize(k)
    if isinstance(v, dict):
        inserts.append((nk, v))
    else:
        updates.append((nk, v))

# --- inserts: only for keys genuinely absent from the lexicon ---
n_ins = 0
for nk, v in inserts:
    existing = None
    for cand in alt_keys(nk):
        existing = cur.execute(
            "SELECT strongs FROM lexicon WHERE strongs=?", (cand,)
        ).fetchone()
        if existing:
            break
    if existing:
        # key exists after all -> treat as update
        updates.append((existing[0], v["gloss_tamil"]))
        continue
    lang = v.get("lang", "greek" if nk.startswith("G") else "hebrew")
    cur.execute(
        "INSERT INTO lexicon (strongs, language, word, transliteration, short_definition, gloss_tamil)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (nk, lang, v["word"], v["translit"], v["def"], v["gloss_tamil"]),
    )
    n_ins += 1

# --- updates: only for keys present; skip silently-absent ones ---
applied, skipped = [], []
for nk, gloss in updates:
    row = None
    for cand in alt_keys(nk):
        row = cur.execute(
            "SELECT strongs, word FROM lexicon WHERE strongs=?", (cand,)
        ).fetchone()
        if row:
            break
    if row:
        cur.execute(
            "UPDATE lexicon SET gloss_tamil=? WHERE strongs=?", (gloss, row[0])
        )
        applied.append((row[0], row[1], gloss))
    else:
        skipped.append(nk)

mode = sys.argv[1] if len(sys.argv) > 1 else "check"
if mode == "apply":
    conn.commit()
    print(f"COMMITTED: {n_ins} inserted, {len(applied)} updated, {len(skipped)} skipped")
else:
    print(f"DRY RUN: {n_ins} would be inserted, {len(applied)} updated, {len(skipped)} skipped")
    print("\n--- INSERTS ---")
    for nk, v in inserts:
        print(f"{nk:8s} {v['word']:18s} {v['gloss_tamil'][:40]}")
    print("\n--- UPDATES (strongs | word | new gloss) ---")
    for s, w, g in sorted(applied, key=lambda x: int(x[0][1:])):
        print(f"{s:8s} {str(w)[:18]:20s} {g[:44]}")
    if skipped:
        print("\n--- SKIPPED (not in lexicon) ---")
        print(", ".join(skipped))
conn.close()
