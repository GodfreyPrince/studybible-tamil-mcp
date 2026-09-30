"""Apply theology_tamil.json overlay to study_bible_tamil.db.

Adds title_ta / summary_ta / detail_ta columns to theology_content and fills
them for every entry present in the translation file (193/193).
"""
import json
import sqlite3

DB = "data/study_bible_tamil.db"
SRC = "translations/theology_tamil.json"

data = json.load(open(SRC, encoding="utf-8"))

conn = sqlite3.connect(DB)
cur = conn.cursor()
for col in ("title_ta", "summary_ta", "detail_ta"):
    try:
        cur.execute(f"ALTER TABLE theology_content ADD COLUMN {col} TEXT")
        print("added column", col)
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("column exists:", col)
        else:
            raise

updated = 0
for k, v in data.items():
    cur.execute(
        "UPDATE theology_content SET title_ta=?, summary_ta=?, detail_ta=? WHERE id=?",
        (v["title"], v["summary"], v["detail"], int(k)),
    )
    updated += cur.rowcount

conn.commit()

total = cur.execute("SELECT COUNT(*) FROM theology_content").fetchone()[0]
covered = cur.execute(
    "SELECT COUNT(*) FROM theology_content WHERE title_ta IS NOT NULL AND title_ta != ''"
).fetchone()[0]
print(f"theology Tamil overlay applied: {updated} rows updated, coverage {covered}/{total}")
conn.close()
