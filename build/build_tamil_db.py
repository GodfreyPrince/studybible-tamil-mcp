#!/usr/bin/env python3
"""
Build study_bible_tamil.db: copy of the English study bible DB enriched with
Tamil scripture (IRV, word-aligned), Tamil study content, and Tamil glosses.

Tables added:
  verses.text_tamil        - Tamil IRV verse text
  verses.text_tamil_trad   - traditional Tamil Bible text (merged separately)
  lexicon.gloss_tamil      - Tamil gloss for Strong's entries
  ta_word_alignment        - Tamil word <-> Strong's alignments (IRV)
  ta_gloss                 - aggregated Tamil renderings per Strong's number
  ta_dictionary            - Tamil translationWords articles (Door43 ta_tw)
  ta_notes                 - Tamil translation notes (Door43 ta_tn)
  ta_questions             - Tamil translation questions (Door43 ta_tq)
  ta_name_aliases          - Tamil name -> canonical English name
  book_names               - book code -> Tamil book name
  book_intros              - Tamil book introductions (IRV)
  ta_verses_fts            - FTS5 index over Tamil verse text

Translation overlays (applied when present in translations/):
  lexicon_gloss_tamil.json  {strongs: "தமிழ் சொற்பொருள்"}
  ane_tamil.json            {entry_id: {title, summary, detail, interpretive_significance}}
  theology_tamil.json       {entry_id: {title, content_summary, content_detail}}
  study_notes_tamil.json    {aquifer_id: "தமிழ் நோட்டு"}
  dictionary_tamil.json     {aquifer_id: "தமிழ் கட்டுரை"}
  key_terms_tamil.json      {aquifer_id: "தமிழ் விளக்கம்"}
"""
import json
import shutil
import sqlite3
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # repo root
BASE = Path(__file__).resolve().parent                  # build/
DATA = ROOT / "data"
TRANS = ROOT / "translations"
OUT_DB = ROOT / "data" / "study_bible_tamil.db"
# External source: prebuilt English DB from https://github.com/djayatillake/studybible-mcp
SRC_DB = ROOT.parent / "study_bible.db"

CANONICAL_BOOKS = [
    "Gen", "Exo", "Lev", "Num", "Deu", "Jos", "Jdg", "Rut", "1Sa", "2Sa",
    "1Ki", "2Ki", "1Ch", "2Ch", "Ezr", "Neh", "Est", "Job", "Psa", "Pro",
    "Ecc", "Sng", "Isa", "Jer", "Lam", "Ezk", "Dan", "Hos", "Jol", "Amo",
    "Oba", "Jon", "Mic", "Nam", "Hab", "Zep", "Hag", "Zec", "Mal",
    "Mat", "Mrk", "Luk", "Jhn", "Act", "Rom", "1Co", "2Co", "Gal", "Eph",
    "Php", "Col", "1Th", "2Th", "1Ti", "2Ti", "Tit", "Phm", "Heb", "Jas",
    "1Pe", "2Pe", "1Jn", "2Jn", "3Jn", "Jud", "Rev",
]

# tw slug -> canonical English name for TIPNR/names-table matching overrides
SLUG_OVERRIDES = {
    "abraham": "Abraham", "abram": "Abram", "moses": "Moses", "david": "David",
    "jesus": "Jesus", "paul": "Paul", "peter": "Peter", "mary": "Mary",
    "jerusalem": "Jerusalem", "egypt": "Egypt", "israel": "Israel",
    "jacob": "Jacob", "isaac": "Isaac", "josephot": "Joseph", "josephnt": "Joseph",
    "jude": "Jude", "judas": "Judas Iscariot", "johnthebaptist": "John the Baptist",
    "johnapostle": "John", "jamesapostle": "James", "jamesbrotherofjesus": "James",
    "satan": "Satan", "holy spirit": "Holy Spirit",
}


def load_json(p: Path, default=None):
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return default


def main():
    t0 = time.time()
    OUT_DB.parent.mkdir(parents=True, exist_ok=True)
    if not OUT_DB.exists():
        print(f"Copying {SRC_DB} -> {OUT_DB} ...")
        shutil.copy2(SRC_DB, OUT_DB)

    conn = sqlite3.connect(OUT_DB)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    cur = conn.cursor()

    # ------------------------------------------------------------------
    # 0. Clean junk rows ingested from TAHOT documentation headers
    # ------------------------------------------------------------------
    junk = cur.execute(
        "SELECT COUNT(*) FROM verses WHERE book NOT IN (%s)"
        % ",".join("?" * len(CANONICAL_BOOKS)),
        CANONICAL_BOOKS,
    ).fetchone()[0]
    cur.execute(
        "DELETE FROM verses WHERE book NOT IN (%s)" % ",".join("?" * len(CANONICAL_BOOKS)),
        CANONICAL_BOOKS,
    )
    print(f"Deleted {junk} junk verse rows")

    # ------------------------------------------------------------------
    # 1. verses: Tamil columns
    # ------------------------------------------------------------------
    cols = {r[1] for r in cur.execute("PRAGMA table_info(verses)")}
    if "text_tamil" not in cols:
        cur.execute("ALTER TABLE verses ADD COLUMN text_tamil TEXT")
    if "text_tamil_trad" not in cols:
        cur.execute("ALTER TABLE verses ADD COLUMN text_tamil_trad TEXT")

    verses_tamil = load_json(DATA / "verses_tamil.json", {})
    db_rows = {(b, c, v): ref for ref, b, c, v in cur.execute(
        "SELECT reference, book, chapter, verse FROM verses")}
    # normalise book casing from DB (they are already canonical)
    matched, missing_irv = 0, []
    for ref, text in verses_tamil.items():
        b, c, v = ref.split(".")
        key = (b, int(c), int(v))
        target = db_rows.get(key)
        if target is None:
            missing_irv.append(ref)
            continue
        cur.execute("UPDATE verses SET text_tamil=? WHERE reference=?", (text, target))
        matched += 1
    # IRV-only verses (not in DB): insert as new rows, Tamil-only
    added = 0
    for ref, text in verses_tamil.items():
        b, c, v = ref.split(".")
        if (b, int(c), int(v)) not in db_rows:
            cur.execute(
                "INSERT OR IGNORE INTO verses(reference, book, chapter, verse, text_tamil) "
                "VALUES (?,?,?,?,?)",
                (ref, b, int(c), int(v), text),
            )
            added += 1
    # Psalm superscriptions (verse 0 rows) <- IRV chapter titles
    titles = load_json(DATA / "chapter_titles.json", {})
    n_title = 0
    for key, title in titles.items():
        b, c = key.split(".")
        rows = cur.execute(
            "SELECT reference FROM verses WHERE book=? AND chapter=? AND verse=0",
            (b, int(c)),
        ).fetchall()
        if rows:
            cur.execute("UPDATE verses SET text_tamil=? WHERE reference=? AND text_tamil IS NULL",
                        (title, rows[0][0]))
            n_title += 1
    n_tamil = cur.execute("SELECT COUNT(*) FROM verses WHERE text_tamil IS NOT NULL").fetchone()[0]
    n_total = cur.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
    print(f"Tamil text: {matched} matched, {added} added (IRV-only), "
          f"{n_title} titles -> verse 0, {n_tamil}/{n_total} rows with Tamil")

    # ------------------------------------------------------------------
    # 2. ta_word_alignment + ta_gloss
    # ------------------------------------------------------------------
    cur.execute("DROP TABLE IF EXISTS ta_word_alignment")
    cur.execute("""
        CREATE TABLE ta_word_alignment (
            reference TEXT NOT NULL,
            book TEXT, chapter INTEGER, verse INTEGER,
            seq INTEGER,
            strongs TEXT, lemma TEXT, morph TEXT, tamil_word TEXT
        )""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_twa_strongs ON ta_word_alignment(strongs)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_twa_ref ON ta_word_alignment(reference)")

    words = load_json(DATA / "verse_words.json", {})
    batch = []
    for ref, pairs in words.items():
        b, c, v = ref.split(".")
        for seq, (s, lemma, morph, tw) in enumerate(pairs):
            batch.append((ref, b, int(c), int(v), seq, s, lemma, morph, tw))
    cur.executemany("INSERT INTO ta_word_alignment VALUES (?,?,?,?,?,?,?,?,?)", batch)
    print(f"ta_word_alignment: {len(batch)} rows")

    # aggregated Tamil renderings per Strong's number
    gloss_counter = {}
    for ref, pairs in words.items():
        for s, lemma, morph, tw in pairs:
            gloss_counter.setdefault(s, Counter())[tw] += 1

    cur.execute("DROP TABLE IF EXISTS ta_gloss")
    cur.execute("""
        CREATE TABLE ta_gloss (
            strongs TEXT PRIMARY KEY,
            gloss_tamil TEXT,
            renderings TEXT,
            source TEXT
        )""")
    gloss_rows = []
    for s, cnt in gloss_counter.items():
        top = cnt.most_common(10)
        # strip common Tamil case-suffixes for a clean lemma-ish form
        def baseform(w):
            suffixes = ("உடைய", "இனாலே", "இனால்", "இல்", "இன்", "ஐ", "ஓடு", "உக்கு", "க்கு", "ஆக", "ஆல்")
            for suf in suffixes:
                if w.endswith(suf) and len(w) > len(suf) + 2:
                    return w[: -len(suf)]
            return w
        gloss_tamil = baseform(top[0][0])
        gloss_rows.append((s, gloss_tamil, json.dumps(
            [{"form": f, "count": n} for f, n in top], ensure_ascii=False), "irv_alignment"))
    cur.executemany("INSERT OR REPLACE INTO ta_gloss VALUES (?,?,?,?)", gloss_rows)
    print(f"ta_gloss (from alignment): {len(gloss_rows)} entries")

    # tw-article Strong's links: Tamil titles as glosses where alignment missing
    tw_articles = load_json(DATA / "tw_articles.json", [])
    n_tw_gloss = 0
    for art in tw_articles:
        for s in art.get("strongs", []):
            has = cur.execute("SELECT 1 FROM ta_gloss WHERE strongs=?", (s,)).fetchone()
            if not has:
                cur.execute("INSERT OR REPLACE INTO ta_gloss VALUES (?,?,?,?)",
                            (s, art["title"].split(",")[0].strip(), None, "tw"))
                n_tw_gloss += 1
    print(f"ta_gloss from tw articles: +{n_tw_gloss}")

    # ------------------------------------------------------------------
    # 3. lexicon.gloss_tamil  (alignment gloss -> then LLM overlay)
    # ------------------------------------------------------------------
    if "gloss_tamil" not in {r[1] for r in cur.execute("PRAGMA table_info(lexicon)")}:
        cur.execute("ALTER TABLE lexicon ADD COLUMN gloss_tamil TEXT")
    cur.execute("""
        UPDATE lexicon SET gloss_tamil = (
            SELECT g.gloss_tamil FROM ta_gloss g WHERE g.strongs = lexicon.strongs
        )
    """)
    n = cur.execute("SELECT COUNT(*) FROM lexicon WHERE gloss_tamil IS NOT NULL").fetchone()[0]
    print(f"lexicon.gloss_tamil populated: {n}")

    # LLM translation overlays
    lex_llm = load_json(TRANS / "lexicon_gloss_tamil.json", {}) if TRANS.exists() else {}
    n_llm = 0
    for s, g in lex_llm.items():
        cur.execute("UPDATE lexicon SET gloss_tamil=? WHERE strongs=? AND (gloss_tamil IS NULL OR gloss_tamil='')", (g, s))
        n_llm += cur.execute("SELECT changes()").fetchone()[0]
    print(f"lexicon.gloss_tamil LLM overlay: +{n_llm} (of {len(lex_llm)} provided)")

    # ------------------------------------------------------------------
    # 4. Tamil study content tables
    # ------------------------------------------------------------------
    cur.execute("DROP TABLE IF EXISTS ta_dictionary")
    cur.execute("""
        CREATE TABLE ta_dictionary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            category TEXT,
            title TEXT,
            aliases TEXT,
            body TEXT,
            strongs TEXT
        )""")
    for art in tw_articles:
        cur.execute("INSERT OR REPLACE INTO ta_dictionary(slug,category,title,aliases,body,strongs) VALUES (?,?,?,?,?,?)",
                    (art["slug"], art["category"], art["title"],
                     json.dumps(art.get("aliases", []), ensure_ascii=False),
                     art["body"], json.dumps(art.get("strongs", []))))
    print(f"ta_dictionary: {len(tw_articles)} articles")

    cur.execute("DROP TABLE IF EXISTS ta_notes")
    cur.execute("""
        CREATE TABLE ta_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book TEXT, chapter INTEGER, verse INTEGER,
            phrase TEXT, body TEXT,
            UNIQUE(book, chapter, verse, phrase)
        )""")
    tn = load_json(DATA / "tn_notes.json", [])
    cur.executemany("INSERT OR IGNORE INTO ta_notes(book,chapter,verse,phrase,body) VALUES (?,?,?,?,?)",
                    [(n["book"], n["chapter"], n["verse"], n["phrase"], n["body"]) for n in tn])
    print(f"ta_notes: {len(tn)} notes")

    cur.execute("DROP TABLE IF EXISTS ta_questions")
    cur.execute("""
        CREATE TABLE ta_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book TEXT, chapter INTEGER, verse INTEGER,
            question TEXT, answer TEXT,
            UNIQUE(book, chapter, verse, question)
        )""")
    tq = load_json(DATA / "tq_questions.json", [])
    cur.executemany("INSERT OR IGNORE INTO ta_questions(book,chapter,verse,question,answer) VALUES (?,?,?,?,?)",
                    [(q["book"], q["chapter"], q["verse"], q["question"], q["answer"]) for q in tq])
    print(f"ta_questions: {len(tq)} questions")

    # book names + intros
    cur.execute("DROP TABLE IF EXISTS book_names")
    cur.execute("CREATE TABLE book_names (book TEXT PRIMARY KEY, tamil TEXT, short TEXT, alt TEXT)")
    bn = load_json(DATA / "book_names.json", {})
    for b, n in bn.items():
        cur.execute("INSERT OR REPLACE INTO book_names VALUES (?,?,?,?)",
                    (b, n.get("tamil"), n.get("short"), json.dumps(n.get("alt", []), ensure_ascii=False)))
    print(f"book_names: {len(bn)}")

    cur.execute("DROP TABLE IF EXISTS book_intros")
    cur.execute("""
        CREATE TABLE book_intros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book TEXT NOT NULL,
            heading TEXT,
            paras TEXT
        )""")
    intros = load_json(DATA / "book_intros.json", {})
    outlines = load_json(DATA / "book_outlines.json", {})
    for b, sections in intros.items():
        for sec in sections:
            cur.execute("INSERT INTO book_intros(book,heading,paras) VALUES (?,?,?)",
                        (b, sec.get("heading", ""),
                         json.dumps(sec.get("paras", []), ensure_ascii=False)))
        if outlines.get(b):
            cur.execute("INSERT INTO book_intros(book,heading,paras) VALUES (?,?,?)",
                        (b, "__outline__", json.dumps(outlines[b], ensure_ascii=False)))
    print(f"book_intros: {cur.execute('SELECT COUNT(*) FROM book_intros').fetchone()[0]} sections")

    # name aliases: Tamil alias -> canonical English name
    cur.execute("DROP TABLE IF EXISTS ta_name_aliases")
    cur.execute("""
        CREATE TABLE ta_name_aliases (
            alias TEXT PRIMARY KEY,
            target_slug TEXT,
            target_name TEXT
        )""")
    aliases = load_json(DATA / "ta_name_aliases.json", [])
    all_names = {r[0].lower(): r[0] for r in cur.execute("SELECT name FROM names")}
    # graph people too (graph tools use graph_people.name)
    graph_names = {r[0].lower(): r[0] for r in cur.execute("SELECT name FROM graph_people")}
    resolved, unresolved = 0, []
    for a in aliases:
        alias, slug = a["alias"], a["target"]
        en = SLUG_OVERRIDES.get(slug)
        if not en:
            en = all_names.get(slug) or all_names.get(slug.replace("_", " "))
        if not en:
            en = graph_names.get(slug) or graph_names.get(slug.replace("_", " "))
        if en:
            cur.execute("INSERT OR REPLACE INTO ta_name_aliases VALUES (?,?,?)", (alias, slug, en))
            resolved += 1
        else:
            unresolved.append((alias, slug))
    print(f"ta_name_aliases: {resolved} resolved, {len(unresolved)} unresolved")
    if unresolved:
        print("  unresolved samples:", unresolved[:15])

    # ------------------------------------------------------------------
    # 5. FTS5 index over Tamil verse text (unique Tamil feature)
    # ------------------------------------------------------------------
    cur.execute("DROP TABLE IF EXISTS ta_verses_fts")
    cur.execute("CREATE VIRTUAL TABLE ta_verses_fts USING fts5(reference UNINDEXED, text_tamil, tokenize='unicode61')")
    cur.execute("INSERT INTO ta_verses_fts(reference, text_tamil) "
                "SELECT reference, text_tamil FROM verses WHERE text_tamil IS NOT NULL")
    n_fts = cur.execute("SELECT COUNT(*) FROM ta_verses_fts").fetchone()[0]
    print(f"ta_verses_fts: {n_fts} rows")

    # ------------------------------------------------------------------
    # 6. Content translation overlays (ANE / theology / aquifer)
    # ------------------------------------------------------------------
    if TRANS.exists():
        ane_t = load_json(TRANS / "ane_tamil.json", {})
        if ane_t:
            cols_ane = {r[1] for r in cur.execute("PRAGMA table_info(ane_entries)")}
            for col in ("title_ta", "summary_ta", "detail_ta", "significance_ta"):
                if col not in cols_ane:
                    cur.execute(f"ALTER TABLE ane_entries ADD COLUMN {col} TEXT")
            n = 0
            for eid, tr in ane_t.items():
                cur.execute("UPDATE ane_entries SET title_ta=?, summary_ta=?, detail_ta=?, significance_ta=? WHERE id=?",
                            (tr.get("title"), tr.get("summary"), tr.get("detail"),
                             tr.get("interpretive_significance"), eid))
                n += cur.execute("SELECT changes()").fetchone()[0]
            print(f"ane_entries Tamil overlay: {n}/{len(ane_t)}")

        theo_t = load_json(TRANS / "theology_tamil.json", {})
        if theo_t:
            cols_t = {r[1] for r in cur.execute("PRAGMA table_info(theology_content)")}
            for col in ("title_ta", "summary_ta", "detail_ta"):
                if col not in cols_t:
                    cur.execute(f"ALTER TABLE theology_content ADD COLUMN {col} TEXT")
            n = 0
            for eid, tr in theo_t.items():
                cur.execute("UPDATE theology_content SET title_ta=?, summary_ta=?, detail_ta=? WHERE id=?",
                            (tr.get("title"), tr.get("content_summary"), tr.get("content_detail"), eid))
                n += cur.execute("SELECT changes()").fetchone()[0]
            print(f"theology_content Tamil overlay: {n}/{len(theo_t)}")

        sn_t = load_json(TRANS / "study_notes_tamil.json", {})
        if sn_t:
            cols_s = {r[1] for r in cur.execute("PRAGMA table_info(aquifer_content)")}
            if "content_plain_ta" not in cols_s:
                cur.execute("ALTER TABLE aquifer_content ADD COLUMN content_plain_ta TEXT")
            n = 0
            for cid, tr in sn_t.items():
                cur.execute("UPDATE aquifer_content SET content_plain_ta=? WHERE id=?", (tr, cid))
                n += cur.execute("SELECT changes()").fetchone()[0]
            print(f"aquifer study_notes Tamil overlay: {n}/{len(sn_t)}")

        dic_t = load_json(TRANS / "dictionary_tamil.json", {})
        if dic_t:
            cols_d = {r[1] for r in cur.execute("PRAGMA table_info(aquifer_content)")}
            if "content_plain_ta" not in cols_d:
                cur.execute("ALTER TABLE aquifer_content ADD COLUMN content_plain_ta TEXT")
            if "title_ta" not in cols_d:
                cur.execute("ALTER TABLE aquifer_content ADD COLUMN title_ta TEXT")
            n = 0
            for cid, tr in dic_t.items():
                body = tr["content_plain"] if isinstance(tr, dict) else tr
                title = tr.get("title") if isinstance(tr, dict) else None
                cur.execute("UPDATE aquifer_content SET content_plain_ta=?, title_ta=COALESCE(?, title_ta) WHERE id=?",
                            (body, title, cid))
                n += cur.execute("SELECT changes()").fetchone()[0]
            print(f"aquifer dictionary Tamil overlay: {n}/{len(dic_t)}")

        kt_t = load_json(TRANS / "key_terms_tamil.json", {})
        if kt_t:
            cols_k = {r[1] for r in cur.execute("PRAGMA table_info(aquifer_content)")}
            if "content_plain_ta" not in cols_k:
                cur.execute("ALTER TABLE aquifer_content ADD COLUMN content_plain_ta TEXT")
            if "title_ta" not in cols_k:
                cur.execute("ALTER TABLE aquifer_content ADD COLUMN title_ta TEXT")
            n = 0
            for cid, tr in kt_t.items():
                body = tr["content_plain"] if isinstance(tr, dict) else tr
                title = tr.get("title") if isinstance(tr, dict) else None
                cur.execute("UPDATE aquifer_content SET content_plain_ta=?, title_ta=COALESCE(?, title_ta) WHERE id=?",
                            (body, title, cid))
                n += cur.execute("SELECT changes()").fetchone()[0]
            print(f"aquifer key_terms Tamil overlay: {n}/{len(kt_t)}")

    conn.commit()
    print(f"\nVACUUMing (may take a minute)...")
    conn.execute("VACUUM")
    conn.commit()
    conn.close()
    print(f"Done in {time.time()-t0:.0f}s -> {OUT_DB}")


if __name__ == "__main__":
    main()
