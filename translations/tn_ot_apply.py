"""Apply OT translation-note overlays into ta_notes.

Source refs come from tn_ot_*_source.json files (aquifer ids -> chapter/verse);
translations live in tamil_build/translations/tn_ot_*.json as
{"<aquifer_id>": {"phrase": ..., "body": ...}}.

An applied-ids ledger (tn_ot_applied_ids.json) keeps re-runs idempotent.
Run from studybible-tamil/:  py -3.11 ../tamil_build/tn_ot_apply.py
"""
import glob
import json
import sqlite3
from pathlib import Path

WS = Path(__file__).resolve().parent.parent          # workspace/default
ROOT = WS / "studybible-tamil"
TRANS = WS / "tamil_build" / "translations"
LEDGER = WS / "tamil_build" / "tn_ot_applied_ids.json"

applied = set(json.load(open(LEDGER, encoding="utf-8"))) if LEDGER.exists() else set()

# source refs: collect every tn_ot_*_source.json
refs = {}
for f in glob.glob(str(WS / "tamil_build" / "tn_ot_*_source.json")):
    for n in json.load(open(f, encoding="utf-8")):
        refs[str(n["id"])] = (n["book"], n["ch"], n["vs"])

conn = sqlite3.connect(ROOT / "data" / "study_bible_tamil.db")
cur = conn.cursor()

inserted, skipped, collisions = 0, 0, []
for f in sorted(glob.glob(str(TRANS / "tn_ot_*.json"))):
    data = json.load(open(f, encoding="utf-8"))
    for aid, v in data.items():
        if aid in applied:
            skipped += 1
            continue
        if aid not in refs:
            print("WARN no source ref for", aid, "in", f)
            continue
        book, ch, vs = refs[aid]
        # ta_notes has UNIQUE(book, chapter, verse, phrase): an existing row
        # (my earlier batch or Door43) wins; report for phrase adjustment
        dup = cur.execute(
            "SELECT 1 FROM ta_notes WHERE book=? AND chapter=? AND verse=? AND phrase=?",
            (book, ch, vs, v["phrase"]),
        ).fetchone()
        if dup:
            collisions.append((aid, f"{book} {ch}:{vs}", v["phrase"]))
            applied.add(aid)  # don't retry forever
            continue
        cur.execute(
            "INSERT INTO ta_notes (book, chapter, verse, phrase, body) VALUES (?, ?, ?, ?, ?)",
            (book, ch, vs, v["phrase"], v["body"]),
        )
        applied.add(aid)
        inserted += 1

conn.commit()
conn.close()
json.dump(sorted(applied, key=int), open(LEDGER, "w", encoding="utf-8"))
print(f"OT notes applied: {inserted} inserted, {skipped} already done, {len(collisions)} phrase-collisions skipped; ledger {len(applied)} ids")
for c in collisions:
    print("  collision:", c)
