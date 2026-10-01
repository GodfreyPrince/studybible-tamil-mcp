"""Extract unfoldingWord OT translation notes for a book/chapter range.

Usage:  py -3.11 tamil_build/tn_ot_extract.py Gen 4 6
Writes  tamil_build/tn_ot_<book><firstch>_<lastch>_source.json
        tamil_build/tn_ot_<book><firstch>_<lastch>_text.txt  (reading dump)
"""
import json
import sqlite3
import sys

BOOK = sys.argv[1]  # canonical code as in DB: Gen, Exo, Lev, Num, Deu, 1Sa, 1Ki, Psa, Pro, Isa ...
CH1, CH2 = int(sys.argv[2]), int(sys.argv[3])

conn = sqlite3.connect(r"studybible-tamil/data/study_bible_tamil.db")
conn.row_factory = sqlite3.Row
rows = conn.execute(
    """SELECT id, book, chapter_start AS ch, verse_start AS vs, title, content_plain
       FROM aquifer_content
       WHERE resource_type='translation_notes_uw' AND book=?
         AND chapter_start BETWEEN ? AND ? AND verse_start > 0
       ORDER BY chapter_start, verse_start, id""",
    (BOOK, CH1, CH2),
).fetchall()
sel = [dict(r) for r in rows]
tag = f"{BOOK.lower()}{CH1}" + (f"_{CH2}" if CH2 != CH1 else "")
json.dump(sel, open(f"tamil_build/tn_ot_{tag}_source.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
out = []
for n in sel:
    c = (n["content_plain"] or "").strip()
    c = "\n".join(line for line in c.splitlines() if line.strip())
    out.append(f"### {n['id']} | {n['ch']}:{n['vs']}\n{c[:850]}\n")
open(f"tamil_build/tn_ot_{tag}_text.txt", "w", encoding="utf-8").write("\n".join(out))
total = conn.execute(
    "SELECT COUNT(*) FROM aquifer_content WHERE resource_type='translation_notes_uw' AND book=? AND verse_start>0",
    (BOOK,),
).fetchone()[0]
print(f"{BOOK} {CH1}-{CH2}: {len(sel)} notes extracted (book total {total})")
print(f"saved: tn_ot_{tag}_source.json + tn_ot_{tag}_text.txt")
