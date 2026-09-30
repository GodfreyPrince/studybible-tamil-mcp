#!/usr/bin/env python3
"""In-process exercise of every Tamil Study Bible MCP tool handler."""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
os.environ["STUDY_BIBLE_TAMIL_DB"] = str(
    Path(__file__).resolve().parent.parent / "data" / "study_bible_tamil.db")

import study_bible_tamil_mcp.server as srv

PASS, FAIL = [], []


def check(name: str, text: str, must_contain: list[str] | None = None,
          min_len: int = 20):
    ok = text and len(text) >= min_len
    missing = []
    if ok and must_contain:
        for token in must_contain:
            if token not in text:
                missing.append(token)
        ok = not missing
    if ok:
        PASS.append(name)
        print(f"  PASS  {name}")
    else:
        FAIL.append(name)
        snippet = (text or "<empty>")[:160].replace("\n", " ")
        print(f"  FAIL  {name} | missing={missing} | snippet: {snippet}")


async def main():
    results = {}

    # initialize the module-level db (call_tool does this lazily in production)
    srv.db = srv.StudyBibleDB(os.environ["STUDY_BIBLE_TAMIL_DB"])
    await srv.db.connect()

    async def run(name, handler, args):
        try:
            out = await handler(args)
            results[name] = out[0].text
        except Exception as e:
            results[name] = ""
            print(f"  ERROR {name}: {e!r}")

    H = srv._TOOL_HANDLERS

    print("== Scripture & language ==")
    await run("lookup_verse_tamil", H["lookup_verse"], {"reference": "யோவான் 3:16"})
    check("lookup_verse_tamil", results["lookup_verse_tamil"],
          ["யோவான்", "தமிழ்", "Original Text"])
    await run("lookup_verse_english", H["lookup_verse"], {"reference": "Genesis 1:1"})
    check("lookup_verse_english", results["lookup_verse_english"], ["ஆதியாகமம்"])
    await run("lookup_verse_morph", H["lookup_verse"],
              {"reference": "Romans 8:28", "include_morphology": True})
    check("lookup_verse_morph", results["lookup_verse_morph"], ["Word Analysis"])
    await run("word_study_strongs", H["word_study"], {"strongs": "G26"})
    check("word_study_strongs", results["word_study_strongs"], ["தமிழ்", "agap", "LSJ"])
    await run("word_study_tamil", H["word_study"], {"word": "கிருபை"})
    check("word_study_tamil", results["word_study_tamil"], ["தமிழ்"])
    await run("search_lexicon_tamil", H["search_lexicon"], {"query": "அன்பு", "limit": 5})
    check("search_lexicon_tamil", results["search_lexicon_tamil"], ["தமிழ்"])
    await run("search_lexicon_english", H["search_lexicon"], {"query": "love", "limit": 5})
    check("search_lexicon_english", results["search_lexicon_english"], ["G"])
    await run("parse_morphology", H["parse_morphology"], {"code": "V-AAI-3S"})
    check("parse_morphology", results["parse_morphology"], ["Aorist", "தமிழ்"])
    await run("search_by_strongs", H["search_by_strongs"], {"strongs": "H2617", "limit": 6})
    check("search_by_strongs", results["search_by_strongs"], ["தமிழ்"])

    print("== Cross references & themes ==")
    await run("xref_verse", H["get_cross_references"], {"reference": "John 3:16", "limit": 6})
    check("xref_verse", results["xref_verse"], ["குறுக்குப்பாடங்கள்"])
    await run("xref_theme", H["get_cross_references"], {"theme": "salvation_by_grace"})
    check("xref_theme", results["xref_theme"], ["கிருபையால் இரட்சிப்பு"])

    print("== Names & graph ==")
    await run("lookup_name_tamil", H["lookup_name"], {"name": "ஆபிரகாம்"})
    check("lookup_name_tamil", results["lookup_name_tamil"], ["Abraham", "ஆபிரகாம்"])
    await run("lookup_name_english", H["lookup_name"], {"name": "David"})
    check("lookup_name_english", results["lookup_name_english"], ["David"])
    await run("explore_genealogy_tamil", H["explore_genealogy"],
              {"person": "தாவீது", "generations": 3})
    check("explore_genealogy_tamil", results["explore_genealogy_tamil"], ["Genealogy"])
    await run("explore_person_events", H["explore_person_events"], {"person": "Paul"})
    check("explore_person_events", results["explore_person_events"], ["Timeline"])
    await run("explore_place_tamil", H["explore_place"], {"place": "எருசலேம்"})
    check("explore_place_tamil", results["explore_place_tamil"], ["Jerusalem"])
    await run("find_connection", H["find_connection"], {"person1": "Ruth", "person2": "Jesus"})
    check("find_connection", results["find_connection"], ["Ruth", "Obed"])
    await run("people_in_passage", H["people_in_passage"], {"reference": "Genesis 22"})
    check("people_in_passage", results["people_in_passage"], ["Abraham"])
    await run("graph_enriched_search", H["graph_enriched_search"], {"reference": "Matthew 1:1"})
    check("graph_enriched_search", results["graph_enriched_search"], ["Jesus"])

    print("== Study content ==")
    await run("study_notes_tamil", H["get_study_notes"], {"reference": "ரோமர்கள் 8:28"})
    check("study_notes_tamil", results["study_notes_tamil"], ["தமிழ்", "படிப்பு"])
    await run("study_notes_chapter", H["get_study_notes"],
              {"reference": "Genesis 1", "chapter_only": True})
    check("study_notes_chapter", results["study_notes_chapter"], ["அறிமுகம்"])
    await run("bible_dictionary_tamil", H["get_bible_dictionary"], {"topic": "உடன்படிக்கை"})
    check("bible_dictionary_tamil", results["bible_dictionary_tamil"], ["தமிழ்"])
    await run("bible_dictionary_english", H["get_bible_dictionary"], {"topic": "Pharisees"})
    check("bible_dictionary_english", results["bible_dictionary_english"], ["Pharis"])
    await run("key_terms_tamil", H["get_key_terms"], {"term": "பரிகாரம்"})
    check("key_terms_tamil", results["key_terms_tamil"], ["தமிழ்"])
    await run("key_terms_english", H["get_key_terms"], {"term": "atonement"})
    check("key_terms_english", results["key_terms_english"], ["tonement"])

    print("== ANE / theology / weave / variants ==")
    await run("ane_context", H["get_ane_context"], {"reference": "Genesis 15:1"})
    check("ane_context", results["ane_context"], ["covenant"])
    await run("ane_dimensions", H["get_ane_context"], {})
    check("ane_dimensions", results["ane_dimensions"], ["Dimension"])
    await run("theology_context", H["get_theology_context"], {"reference": "Psalm 82:1"})
    check("theology_context", results["theology_context"], ["Heiser"])
    await run("torah_weave", H["get_torah_weave"], {"reference": "Genesis 6:1"})
    check("torah_weave", results["torah_weave"], ["weave"])
    await run("textual_variant", H["get_textual_variant"], {"reference": "Hebrews 10:5"})
    check("textual_variant", results["textual_variant"], ["variant", "LXX"])

    print("== Semantic search & unique Tamil features ==")
    await run("find_similar_passages", H["find_similar_passages"],
              {"reference": "Daniel 7:7", "limit": 4})
    ok = "similar" in results["find_similar_passages"]
    if ok:
        PASS.append("find_similar_passages"); print("  PASS  find_similar_passages")
    else:
        FAIL.append("find_similar_passages")
        print("  FAIL  find_similar_passages (vector extension?)",
              results["find_similar_passages"][:120])
    await run("search_tamil_verses", H["search_tamil_verses"], {"query": "அன்பு", "limit": 5})
    check("search_tamil_verses", results["search_tamil_verses"], ["தமிழ் வேதாகம தேடல்"])
    await run("search_tamil_verses_phrase", H["search_tamil_verses"],
              {"query": "பரலோகராஜ்யம்", "limit": 3})
    check("search_tamil_verses_phrase", results["search_tamil_verses_phrase"], ["தேடல்"])

    print(f"\n{'='*60}\nPASS: {len(PASS)}  FAIL: {len(FAIL)}")
    if FAIL:
        print("Failed:", FAIL)
        sys.exit(1)


asyncio.run(main())
