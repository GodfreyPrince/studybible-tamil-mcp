"""Build the slim offline study pack for the Tamil Bible Android app.

Copies only the Tamil study tables (plus the theology/ANE Tamil columns) from
the full study_bible_tamil.db into a compact tamil_study.db, indexes it for
per-verse lookups, and zips it for distribution via the study API (/api/pack).
"""
import json
import sqlite3
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # studybible-tamil/
SRC = ROOT / "data" / "study_bible_tamil.db"
OUT_DB = ROOT / "data" / "tamil_study.db"
OUT_ZIP = ROOT / "data" / "tamil_study_pack.zip"

WHOLESALE = [
    "ta_word_alignment", "ta_gloss", "ta_notes", "ta_questions",
    "ta_dictionary", "book_intros", "book_names", "ta_name_aliases",
    "theology_verse_index", "ane_book_mappings",
]
# id + every *_ta column + small metadata columns
SUBSET = {
    "theology_content": ["id", "source_author", "title"],
    "ane_entries": ["id"],
}
META = ["source_author", "author", "title", "name", "book"]

src = sqlite3.connect(SRC)
if OUT_DB.exists():
    OUT_DB.unlink()
dst = sqlite3.connect(OUT_DB)
dst.execute("ATTACH DATABASE ? AS s", (str(SRC),))

copied = []
for table in WHOLESALE:
    cols = [r[1] for r in src.execute(f"PRAGMA table_info({table})")]
    dst.execute(f"CREATE TABLE {table} AS SELECT * FROM s.{table}")
    dst.commit()
    copied.append((table, len(cols), dst.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]))

for table, keep in SUBSET.items():
    cols = [r[1] for r in src.execute(f"PRAGMA table_info({table})")]
    want = [c for c in cols if c in keep or c.endswith("_ta")
            or (c in META and c not in ("content", "content_plain", "summary", "detail", "content_summary", "content_detail", "interpretive_significance"))]
    sel = ", ".join(want)
    dst.execute(f"CREATE TABLE {table} AS SELECT {sel} FROM s.{table}")
    dst.commit()
    copied.append((table, len(want), dst.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]))
dst.execute("DETACH DATABASE s")

# index every copied table on reference/book/chapter/verse columns where present
for table, _, _ in copied:
    cols = {r[1] for r in dst.execute(f"PRAGMA table_info({table})")}
    for candidate in (["reference"], ["book", "chapter", "verse"], ["book"], ["content_id"]):
        if candidate and all(c in cols for c in candidate):
            name = "idx_" + table + "_" + "_".join(candidate)
            try:
                dst.execute(f"CREATE INDEX {name} ON {table}({','.join(candidate)})")
            except sqlite3.OperationalError:
                pass
            break
dst.execute("ANALYZE")
dst.commit()

print("=== copied tables ===")
for table, ncols, n in copied:
    cols = [r[1] for r in dst.execute(f"PRAGMA table_info({table})")]
    print(f"{table}: {n} rows | cols: {cols}")

dst.close()
src.close()

size_db = OUT_DB.stat().st_size
with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    z.write(OUT_DB, "tamil_study.db")
size_zip = OUT_ZIP.stat().st_size
print(f"\ntamil_study.db: {size_db/1048576:.1f} MB | pack zip: {size_zip/1048576:.1f} MB")
