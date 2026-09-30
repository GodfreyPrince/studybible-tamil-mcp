"""Consolidate lexicon stub rows onto canonical padded Strong's keys.

Fixes two format issues found during verification:
1. The gloss overlay inserted unpadded Greek keys (G26) while the lexicon's
   canonical format is 4-digit padded (G0026, as _normalize_strongs expects).
   -> copy gloss_tamil from each stub to its canonical sibling, delete stub.
2. ta_gloss / ta_word_alignment carry alignment-format strongs (unpadded for
   numbers < 1000), so `JOIN lexicon l ON l.strongs = g.strongs` misses those
   canonical rows. -> normalize both tables' strongs to the padded form
   (ta_gloss has no padded/unpadded twins - verified - so the PK is safe).
"""
import json
import sqlite3

DB = "data/study_bible_tamil.db"
OVERLAY = "translations/lexicon_gloss_tamil.json"

overlay = json.load(open(OVERLAY, encoding="utf-8"))

# my stub keys = object-entry keys (inserted) as unpadded G/H numbers
stub_keys = set()
for k, v in overlay.items():
    if isinstance(v, dict):
        stub_keys.add(k[0] + k[1:].lstrip("0"))

conn = sqlite3.connect(DB)
cur = conn.cursor()

# --- 1. consolidate stubs onto canonical padded rows ---
merged, kept = 0, 0
for sk in sorted(stub_keys):
    canon = sk[0] + sk[1:].zfill(4)
    stub = cur.execute(
        "SELECT id, gloss_tamil FROM lexicon WHERE strongs=?", (sk,)
    ).fetchone()
    if not stub:
        kept += 1
        continue
    canon_row = cur.execute(
        "SELECT id, word, gloss_tamil FROM lexicon WHERE strongs=?", (canon,)
    ).fetchone()
    if not canon_row:
        # true gap: promote the stub to canonical format instead of deleting
        cur.execute("UPDATE lexicon SET strongs=? WHERE id=?", (canon, stub[0]))
        kept += 1
        print(f"promoted stub {sk} -> {canon}")
        continue
    gloss = (stub[1] or "").strip() or (overlay_key_gloss := None)
    if not gloss:
        # stub unglossed (update landed elsewhere); pull from overlay by number
        for k, v in overlay.items():
            if isinstance(v, str) and k[0] + k[1:].lstrip("0") == sk:
                gloss = v
                break
            if isinstance(v, dict) and k[0] + k[1:].lstrip("0") == sk:
                gloss = v["gloss_tamil"]
                break
    if gloss and not (canon_row[2] or "").strip():
        cur.execute("UPDATE lexicon SET gloss_tamil=? WHERE id=?", (gloss, canon_row[0]))
    cur.execute("DELETE FROM lexicon WHERE id=?", (stub[0],))
    merged += 1

conn.commit()
print(f"consolidated {merged} stubs onto canonical rows, kept/promoted {kept}")

# --- 2. normalize strongs in derived tables ---
def canon(s):
    if len(s) >= 2 and s[0] in ("G", "H") and s[1:].isdigit():
        return s[0] + s[1:].zfill(4)
    return s

n1 = cur.execute(
    "UPDATE ta_gloss SET strongs = printf('%s%04d', substr(strongs,1,1), CAST(substr(strongs,2) AS INTEGER))"
    " WHERE strongs GLOB '[GH][0-9]*'"
    " AND strongs != printf('%s%04d', substr(strongs,1,1), CAST(substr(strongs,2) AS INTEGER))",
    (),
).rowcount
n2 = cur.execute(
    "UPDATE ta_word_alignment SET strongs = ? WHERE strongs GLOB '[GH][0-9]*' AND strongs != printf('%s%04d', substr(strongs,1,1), CAST(substr(strongs,2) AS INTEGER))",
    (),
).rowcount
conn.commit()
print(f"normalized strongs: ta_gloss {n1} rows, ta_word_alignment {n2} rows")
conn.close()
