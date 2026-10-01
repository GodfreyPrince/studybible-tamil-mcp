import sqlite3, json

conn = sqlite3.connect(r"data/study_bible_tamil.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# verse-level notes only (exclude book/chapter intros: verse_start = 0)
rows = cur.execute("""
    SELECT id, book, chapter_start AS ch, verse_start AS vs, title, content_plain
    FROM aquifer_content
    WHERE resource_type='translation_notes_uw' AND book='Gen'
      AND chapter_start > 0 AND verse_start > 0
    ORDER BY chapter_start, verse_start, id
""").fetchall()
print("Gen verse notes:", len(rows))
per_ch = {}
for r in rows:
    per_ch[r["ch"]] = per_ch.get(r["ch"], 0) + 1
print("notes per chapter (1-10):", {k: per_ch.get(k, 0) for k in range(1, 11)})

# save source for translation: first 3 chapters to start
sel = [dict(r) for r in rows if r["ch"] <= 3]
print("Gen 1-3 notes:", len(sel))
for s in sel[:4]:
    print("---", s["id"], f'Gen{s["ch"]}:{s["vs"]}', "|", s["title"])
    print((s["content_plain"] or "")[:260])
json.dump(sel, open(r"..\tamil_build\tn_ot_gen1_3_source.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("saved tn_ot_gen1_3_source.json")
