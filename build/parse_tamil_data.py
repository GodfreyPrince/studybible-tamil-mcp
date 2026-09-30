#!/usr/bin/env python3
"""
Parse Door43 Tamil resources into clean JSON for the Tamil Study Bible DB build.

Inputs  (tamil_build/):
  ta_irv/*.usfm   - Tamil Indian Revised Version, word-aligned USFM (\zaln markers)
  ta_tw/bible/{kt,names,other}/*.md - Tamil translationWords (dictionary articles)
  ta_tn/BOOK/CH/V.md   - Tamil translationNotes (verse-level, NT)
  ta_tq/BOOK/CH/V.md   - Tamil translationQuestions (Q&A, NT)

Outputs (tamil_build/data/):
  verses_tamil.json     - {ref: text}            ref = "Jhn.3.16"
  verse_words.json      - {ref: [[strongs, lemma, morph, tamil_word], ...]}
  book_names.json       - {book: {tamil, short, alt:[...]}}
  book_intros.json      - {book: [paragraphs]}
  tw_articles.json      - [{slug, category, title, aliases, body, strongs, refs}]
  tn_notes.json         - [{book, chapter, verse, phrase, body}]
  tq_questions.json     - [{book, chapter, verse, question, answer}]
  ta_name_aliases.json  - [{alias, target}]
"""
import json
import re
import unicodedata
from pathlib import Path

BASE = Path(__file__).parent.parent   # repo root (Door43 resources live alongside)
OUT = BASE / "data"
OUT.mkdir(exist_ok=True)

# USFM book code -> DB book abbreviation (they match; DB abbrs are USFM codes)
USFM_TO_DB = {
    "GEN": "Gen", "EXO": "Exo", "LEV": "Lev", "NUM": "Num", "DEU": "Deu",
    "JOS": "Jos", "JDG": "Jdg", "RUT": "Rut", "1SA": "1Sa", "2SA": "2Sa",
    "1KI": "1Ki", "2KI": "2Ki", "1CH": "1Ch", "2CH": "2Ch", "EZR": "Ezr",
    "NEH": "Neh", "EST": "Est", "JOB": "Job", "PSA": "Psa", "PRO": "Pro",
    "ECC": "Ecc", "SNG": "Sng", "ISA": "Isa", "JER": "Jer", "LAM": "Lam",
    "EZK": "Ezk", "DAN": "Dan", "HOS": "Hos", "JOL": "Jol", "AMO": "Amo",
    "OBA": "Oba", "JON": "Jon", "MIC": "Mic", "NAM": "Nam", "HAB": "Hab",
    "ZEP": "Zep", "HAG": "Hag", "ZEC": "Zec", "MAL": "Mal",
    "MAT": "Mat", "MRK": "Mrk", "LUK": "Luk", "JHN": "Jhn", "ACT": "Act",
    "ROM": "Rom", "1CO": "1Co", "2CO": "2Co", "GAL": "Gal", "EPH": "Eph",
    "PHP": "Php", "COL": "Col", "1TH": "1Th", "2TH": "2Th", "1TI": "1Ti",
    "2TI": "2Ti", "TIT": "Tit", "PHM": "Phm", "HEB": "Heb", "JAS": "Jas",
    "1PE": "1Pe", "2PE": "2Pe", "1JN": "1Jn", "2JN": "2Jn", "3JN": "3Jn",
    "JUD": "Jud", "REV": "Rev",
}

# Inline USFM markers whose inner text must be dropped entirely (notes etc.)
DROP_SPANS = re.compile(
    r"\\f\s.*?\\f\*|\\fe\s.*?\\fe\*|\\x\s.*?\\x\*|\\fig\s.*?\\fig\*",
    re.DOTALL,
)
# \zaln alignment spans: marker + attributes up to and including the closing \*
ZALN_SPAN = re.compile(r"\\zaln-[se]\s\|[^\\]*?\\\*|\\zaln-e\*")
# \w markers: keep inner text but strip the |attributes
W_MARK = re.compile(r"\\w\s([^|]*?)(?:\|[^\\]*?)?\\w\*")
# \+w and similar character-level markers: keep inner text
PLUS_W = re.compile(r"\\[\+]w\s([^|]*?)(?:\|[^\\]*?)?\\\+w\*")
# any other marker token (incl. \p, \q1, \s1, \cl, \b, \m, \sp, \pi...)
ANY_MARK = re.compile(r"\\[a-zA-Z]+\d*(?:-\w+)?(?:\s|\*)?")
STRAY_END = re.compile(r"\\\*")
ATTR = re.compile(r'\s*\|x?-?[^\s]*|x-[a-z]+="[^"]*"')

# markers that terminate/segment verse text (never part of the running verse)
HARD_MARK = re.compile(
    r"^\\(c|v|s\d?|sr|is|ip|iot|io\d?|h|mt\d?|ms|mte|cl|ms|mr|d|sp)\b"
)


def clean_usfm_text(s: str) -> str:
    s = DROP_SPANS.sub("", s)
    s = ZALN_SPAN.sub(" ", s)
    s = PLUS_W.sub(r"\1", s)
    s = W_MARK.sub(r"\1", s)  # keep \w inner text
    s = ANY_MARK.sub(" ", s)  # drop remaining marker tokens
    s = STRAY_END.sub(" ", s)
    s = ATTR.sub("", s)
    s = s.replace("~", " ").replace("//", " ")
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def normalize_usfm(raw: str) -> str:
    """Insert newlines before \\v / \\c markers that don't start a line.

    The IRV files frequently continue a verse with inline `... \\v 7 ...`
    markers on the same line; line-based parsing then merges verses.
    """
    raw = re.sub(r"([^\n])(\\v\s+\d+(?:-\d+)?)", r"\1\n\2", raw)
    raw = re.sub(r"([^\n])(\\c\s+\d+\s*)", r"\1\n\2", raw)
    return raw


def parse_usfm(path: Path):
    """Return (book, names, verses dict, words dict, intro_paragraphs, outline)."""
    raw = normalize_usfm(path.read_text(encoding="utf-8"))
    lines = raw.splitlines()
    book = None
    names = {"tamil": None, "short": None, "alt": []}
    verses = {}
    words = {}
    chapter_titles = {}
    intro = []
    outline = []
    cur_ch = None
    cur_v = None
    cur_v_range = (None, None)
    cur_text_parts = []
    in_intro = True
    cur_intro_item = None
    cur_title_parts = []

    def flush_verse():
        nonlocal cur_v, cur_text_parts
        if cur_ch is not None and cur_v is not None and cur_text_parts:
            text = clean_usfm_text(" ".join(cur_text_parts))
            if text:
                v_start, v_end = cur_v_range
                for v in range(v_start, v_end + 1):
                    verses[f"{book}.{cur_ch}.{v}"] = text
        cur_text_parts = []

    def flush_title():
        nonlocal cur_title_parts
        if cur_ch is not None and cur_title_parts:
            title = clean_usfm_text(" ".join(cur_title_parts))
            if title:
                chapter_titles[f"{book}.{cur_ch}"] = title
        cur_title_parts = []

    for line in lines:
        stripped = line.strip()
        # Book/name headers
        if stripped.startswith("\\id "):
            book = USFM_TO_DB.get(stripped.split()[1])
            continue
        if stripped.startswith("\\h "):
            names["tamil"] = stripped[3:].strip()
            continue
        if stripped.startswith("\\toc1 "):
            names["tamil"] = names["tamil"] or stripped[6:].strip()
            continue
        if stripped.startswith("\\toc2 "):
            names["short"] = stripped[6:].strip()
            continue
        if stripped.startswith("\\toc3 "):
            names["alt"].append(stripped[6:].strip())
            continue
        # Chapters
        if stripped.startswith("\\c "):
            flush_verse()
            flush_title()
            cur_ch = int(stripped.split()[1])
            cur_v = None
            in_intro = False
            continue
        # Psalm-style chapter titles (\d / \s1 before the chapter's first verse)
        if cur_ch is not None and cur_v is None and (
            stripped.startswith("\\d ") or stripped.startswith("\\s1 ")
        ):
            cur_title_parts.append(stripped[3:].strip())
            continue
        # Verses (ranges \v 16-18 assign the same text to every covered verse)
        m = re.match(r"^\\v\s+(\d+)(?:-(\d+))?\s?(.*)$", stripped)
        if m:
            flush_verse()
            flush_title()
            v_start = int(m.group(1))
            v_end = int(m.group(2)) if m.group(2) else v_start
            cur_v_range = (v_start, v_end)
            cur_v = v_start
            rest = m.group(3)
            if rest:
                cur_text_parts.append(rest)
            continue
        # Intro/outline sections (before first chapter or intro markers)
        if stripped.startswith("\\is ") or stripped.startswith("\\ip "):
            label = stripped[4:].strip()
            if stripped.startswith("\\is "):
                cur_intro_item = label
                intro.append({"heading": label, "paras": []})
            else:
                if intro and not intro[-1]["paras"] and cur_intro_item:
                    intro[-1]["paras"].append(label)
                    cur_intro_item = None
                elif intro:
                    intro[-1]["paras"].append(label)
            continue
        if stripped.startswith("\\iot ") or stripped.startswith("\\io1 ") or stripped.startswith("\\io2 ") or stripped.startswith("\\io3 "):
            outline.append(clean_usfm_text(stripped[5:]))
            continue
        # Verse continuation: hard markers segment, everything else continues
        if stripped and cur_v is not None and not HARD_MARK.match(stripped):
            cur_text_parts.append(stripped)
        # Text continuation lines (verse text can wrap lines)
        elif stripped and not stripped.startswith("\\"):
            if cur_v is not None:
                cur_text_parts.append(stripped)

    flush_verse()
    flush_title()
    return book, names, verses, words, intro, outline, chapter_titles


def parse_tn_tq(folder: Path, kind: str):
    """Parse ta_tn / ta_tq markdown files BOOK/CH/V.md."""
    items = []
    pat = re.compile(r"^(\d?[A-Z]{2,3})$")
    for bookdir in sorted(folder.iterdir()):
        if not bookdir.is_dir() or not pat.match(bookdir.name):
            continue
        book = USFM_TO_DB.get(bookdir.name)
        if not book:
            continue
        for chdir in sorted(bookdir.iterdir()):
            if not chdir.is_dir():
                continue
            try:
                ch = int(chdir.name)
            except ValueError:
                continue
            for f in sorted(chdir.glob("*.md")):
                try:
                    v = int(f.stem)
                except ValueError:
                    continue
                blocks = []
                cur = None
                for line in f.read_text(encoding="utf-8").splitlines():
                    if line.startswith("# ") or line.startswith("## "):
                        if cur:
                            blocks.append(cur)
                        cur = {"head": line.lstrip("# ").strip(), "body": []}
                    elif cur is not None:
                        cur["body"].append(line)
                if cur:
                    blocks.append(cur)
                for b in blocks:
                    head = unicodedata.normalize("NFC", b["head"]).strip()
                    body = unicodedata.normalize("NFC", "\n".join(b["body"])).strip()
                    if kind == "tn":
                        items.append({"book": book, "chapter": ch, "verse": v,
                                      "phrase": head, "body": body})
                    else:
                        # tq: head = question, body = answer
                        items.append({"book": book, "chapter": ch, "verse": v,
                                      "question": head, "answer": body})
    return items


TW_SLUG_OVERRIDES = {}  # slug -> canonical English target (filled from data)


def parse_tw(tw_dir: Path):
    """Parse translationWords markdown into articles + name aliases."""
    articles = []
    aliases = []
    for cat in ["kt", "names", "other"]:
        d = tw_dir / "bible" / cat
        if not d.exists():
            continue
        for f in sorted(d.glob("*.md")):
            slug = f.stem
            text = f.read_text(encoding="utf-8")
            text = unicodedata.normalize("NFC", text)
            lines = text.splitlines()
            title = ""
            strongs = []
            # first '# ' heading = title
            for ln in lines:
                if ln.startswith("# "):
                    title = ln[2:].strip()
                    break
            # strongs
            m = re.search(r"Strong'?s?:\s*([HG]\d+[^)\n]*)", text)
            if m:
                strongs = re.findall(r"[HG]\d+", m.group(1))
            # name aliases: title split on comma / slash; also quoted names
            forms = []
            if cat == "names":
                parts = re.split(r"[,،]|/", title)
                for p in parts:
                    p = p.strip().strip("\"“”")
                    # remove trailing annotations like "(என்ற பெயருக்கு...)"
                    p = re.sub(r"\s*\([^)]*\)\s*$", "", p).strip()
                    if p:
                        forms.append(p)
            # body: everything after title heading, cleaned of rc links kept as-is
            body = "\n".join(lines)
            articles.append({
                "slug": slug, "category": cat, "title": title,
                "aliases": forms, "body": body, "strongs": strongs,
            })
            for p in forms:
                aliases.append({"alias": p, "target": slug})
    return articles, aliases


def main():
    # 1. USFM
    all_verses = {}
    all_words = {}
    chapter_titles = {}
    book_names = {}
    book_intros = {}
    outlines = {}
    stats = {}
    for f in sorted((BASE / "ta_irv").glob("*.usfm")):
        book, names, verses, words, intro, outline, titles = parse_usfm(f)
        if not book:
            continue
        all_verses.update(verses)
        chapter_titles.update(titles)
        book_names[book] = names
        book_intros[book] = intro
        outlines[book] = outline
        stats[book] = len(verses)
    print(f"Parsed {len(all_verses)} verses from {len(stats)} books")
    for k in ["Gen", "Psa", "Jol", "Mal", "Mat", "Jhn", "Rev"]:
        print(f"  {k}: {stats.get(k)} verses")

    # word alignment extraction: NT files align Tamil \w words to Greek via
    # \zaln-s | x-strong=".." x-lemma=".." x-morph=".." ... \* ... \w WORD|...\w*
    # Strategy: within each verse blob, for every \w token take the nearest
    # preceding x-strong / x-lemma / x-morph attribute values.
    w_tok = re.compile(r"\\w\s(?P<tw>[^|]*?)\|")
    strong_any = re.compile(r'x-strong="([HG]\d+)?"')
    lemma_any = re.compile(r'x-lemma="([^"]*)"')
    morph_any = re.compile(r'x-morph="([^"]*)"')
    for f in sorted((BASE / "ta_irv").glob("*.usfm")):
        raw = normalize_usfm(f.read_text(encoding="utf-8"))
        book_code = USFM_TO_DB.get(re.search(r"\\id\s+(\w+)", raw).group(1))
        cur_ch = cur_v = None
        blob = []  # lines of current verse
        def flush_blob():
            nonlocal blob
            if cur_ch is None or cur_v is None or not blob:
                blob = []
                return
            text = "\n".join(blob)
            for wm in w_tok.finditer(text):
                tamil = wm.group("tw").strip()
                if not tamil:
                    continue
                head = text[: wm.start()]
                # nearest preceding strong — including empty — so words never
                # inherit a previous word's Strong's number across markers
                sm = None
                for sm in strong_any.finditer(head):
                    pass
                strongs = sm.group(1) if (sm and sm.group(1)) else ""
                if not strongs:
                    continue
                lm = None
                for lm in lemma_any.finditer(head):
                    pass
                mm = None
                for mm in morph_any.finditer(head):
                    pass
                # x-strong format is 5-digit with trailing pad digit (G23160 = G2316)
                strongs = strongs[0] + str(int(strongs[1:5]))
                all_words.setdefault(f"{book_code}.{cur_ch}.{cur_v}", []).append(
                    [strongs, lm.group(1) if lm else "", mm.group(1) if mm else "", tamil]
                )
            blob = []
        for line in raw.splitlines():
            s = line.strip()
            if s.startswith("\\c "):
                flush_blob()
                try:
                    cur_ch = int(s.split()[1])
                except ValueError:
                    cur_ch = None
                cur_v = None
                continue
            m = re.match(r"^\\v\s+(\d+)", s)
            if m:
                flush_blob()
                cur_v = int(m.group(1))
                rest = s[m.end():]
                blob = [rest] if rest else []
                continue
            if s.startswith("\\") or not s:
                # structural marker line inside a verse? (rare) keep scanning
                if s.startswith("\\p") or s.startswith("\\q") or s.startswith("\\m"):
                    continue
                if cur_v is not None and s and not s.startswith("\\v"):
                    # verse continuation with markers/attributes (zaln chains)
                    blob.append(s)
                continue
            blob.append(s)
        flush_blob()
    print(f"Extracted word alignments for {len(all_words)} verses, "
          f"{sum(len(v) for v in all_words.values())} word pairs")

    json.dump(all_verses, open(OUT / "verses_tamil.json", "w", encoding="utf-8"),
              ensure_ascii=False)
    json.dump(all_words, open(OUT / "verse_words.json", "w", encoding="utf-8"),
              ensure_ascii=False)
    json.dump(book_names, open(OUT / "book_names.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump(book_intros, open(OUT / "book_intros.json", "w", encoding="utf-8"),
              ensure_ascii=False)
    json.dump(outlines, open(OUT / "book_outlines.json", "w", encoding="utf-8"),
              ensure_ascii=False)
    json.dump(chapter_titles, open(OUT / "chapter_titles.json", "w", encoding="utf-8"),
              ensure_ascii=False)

    # 2. tn / tq
    tn = parse_tn_tq(BASE / "ta_tn", "tn")
    tq = parse_tn_tq(BASE / "ta_tq", "tq")
    json.dump(tn, open(OUT / "tn_notes.json", "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(tq, open(OUT / "tq_questions.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(f"tn notes: {len(tn)}, tq questions: {len(tq)}")

    # 3. tw
    articles, aliases = parse_tw(BASE / "ta_tw")
    json.dump(articles, open(OUT / "tw_articles.json", "w", encoding="utf-8"),
              ensure_ascii=False)
    json.dump(aliases, open(OUT / "ta_name_aliases.json", "w", encoding="utf-8"),
              ensure_ascii=False)
    print(f"tw articles: {len(articles)}, aliases: {len(aliases)}")

    # 4. Verification samples
    print("\n=== Sample verses ===")
    for ref in ["Gen.1.1", "Jhn.3.16", "Psa.23.1", "Mat.5.3", "Rom.8.28", "Rev.21.4"]:
        print(f"{ref}: {all_verses.get(ref, 'MISSING')[:90]}")
    print("\n=== Jhn.3.16 words ===")
    print(all_words.get("Jhn.3.16", [])[:6])
    print("\n=== Book names ===")
    for b in ["Gen", "Exo", "Psa", "Sng", "Mat", "Rev"]:
        print(b, book_names.get(b))


if __name__ == "__main__":
    main()
