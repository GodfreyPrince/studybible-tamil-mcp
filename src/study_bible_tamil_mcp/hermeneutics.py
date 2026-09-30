"""
Hermeneutical framework for Bible interpretation.

Based on Fee & Stuart's "How to Read the Bible for All Its Worth"
methodology for genre-specific, context-aware interpretation.
"""

from typing import Literal

from .database import TA_BOOK_REVERSE

# Type alias for biblical genres
Genre = Literal[
    "epistle",
    "ot_narrative",
    "acts",
    "gospel",
    "parable",
    "law",
    "prophet",
    "psalm",
    "wisdom",
    "apocalyptic",
]

# Book to genre mapping
BOOK_GENRES: dict[str, Genre] = {
    # Old Testament Narrative
    "Gen": "ot_narrative",
    "Exo": "ot_narrative",
    "Num": "ot_narrative",
    "Jos": "ot_narrative",
    "Jdg": "ot_narrative",
    "Rut": "ot_narrative",
    "1Sa": "ot_narrative",
    "2Sa": "ot_narrative",
    "1Ki": "ot_narrative",
    "2Ki": "ot_narrative",
    "1Ch": "ot_narrative",
    "2Ch": "ot_narrative",
    "Ezr": "ot_narrative",
    "Neh": "ot_narrative",
    "Est": "ot_narrative",
    "Jon": "ot_narrative",

    # Law (Torah/Pentateuch sections)
    "Lev": "law",
    "Deu": "law",

    # Wisdom Literature
    "Job": "wisdom",
    "Pro": "wisdom",
    "Ecc": "wisdom",
    "Sng": "wisdom",

    # Psalms
    "Psa": "psalm",

    # Prophets
    "Isa": "prophet",
    "Jer": "prophet",
    "Lam": "prophet",
    "Ezk": "prophet",
    "Dan": "prophet",
    "Hos": "prophet",
    "Jol": "prophet",
    "Amo": "prophet",
    "Oba": "prophet",
    "Mic": "prophet",
    "Nam": "prophet",
    "Hab": "prophet",
    "Zep": "prophet",
    "Hag": "prophet",
    "Zec": "prophet",
    "Mal": "prophet",

    # Gospels
    "Mat": "gospel",
    "Mrk": "gospel",
    "Luk": "gospel",
    "Jhn": "gospel",

    # Acts
    "Act": "acts",

    # Epistles (Pauline)
    "Rom": "epistle",
    "1Co": "epistle",
    "2Co": "epistle",
    "Gal": "epistle",
    "Eph": "epistle",
    "Php": "epistle",
    "Col": "epistle",
    "1Th": "epistle",
    "2Th": "epistle",
    "1Ti": "epistle",
    "2Ti": "epistle",
    "Tit": "epistle",
    "Phm": "epistle",

    # Epistles (General)
    "Heb": "epistle",
    "Jas": "epistle",
    "1Pe": "epistle",
    "2Pe": "epistle",
    "1Jn": "epistle",
    "2Jn": "epistle",
    "3Jn": "epistle",
    "Jud": "epistle",

    # Apocalyptic
    "Rev": "apocalyptic",
}

# Genre-specific interpretation guidelines
GENRE_GUIDELINES: dict[Genre, dict] = {
    "epistle": {
        "name": "Epistles (Letters)",
        "key_principle": "Think contextually - what problem was being addressed?",
        "approach": [
            "Identify the occasion: What problem or situation prompted this letter?",
            "Understand the relationship between author and recipients",
            "Read the whole letter at once to grasp the argument flow",
            "Pay attention to logical connectors (therefore, because, so that)",
            "Distinguish between the central argument and supporting points",
        ],
        "common_errors": [
            "Taking verses out of their argumentative context",
            "Ignoring the historical situation being addressed",
            "Treating every statement as universally prescriptive",
            "Missing the logical flow by reading only isolated passages",
        ],
        "application_questions": [
            "Is this addressing a specific first-century issue or a timeless principle?",
            "Does the broader biblical witness inform this teaching?",
            "Is the instruction tied to creation order or cultural context?",
        ],
    },
    "ot_narrative": {
        "name": "Old Testament Narratives",
        "key_principle": "Three levels of narrative (meta, national, individual); descriptive not prescriptive",
        "approach": [
            "Remember: narratives describe what happened, not necessarily what should happen",
            "Look for the three levels: God's universal plan, Israel's story, individual accounts",
            "Characters are not always examples to follow - observe their flaws",
            "The narrator rarely makes direct theological statements",
            "God is the ultimate hero of every narrative",
        ],
        "common_errors": [
            "Treating every character's action as a model to follow",
            "Allegorizing details that are simply historical facts",
            "Missing the larger redemptive-historical purpose",
            "Moralizing: 'Be brave like David' without seeing God's work",
        ],
        "application_questions": [
            "What does this reveal about God's character and purposes?",
            "How does this fit into the larger story of redemption?",
            "Is this action approved, disapproved, or simply recorded?",
        ],
    },
    "acts": {
        "name": "Acts (Historical Narrative)",
        "key_principle": "Historical precedent vs normative teaching - not everything repeated is required",
        "approach": [
            "Acts is theological history - Luke is making a point",
            "Distinguish between what the church DID and what we MUST do",
            "Look for patterns repeated multiple times as potentially normative",
            "Unique events may not be meant as patterns for all time",
            "Read alongside the Epistles for doctrinal understanding",
        ],
        "common_errors": [
            "Requiring every practice in Acts for churches today",
            "Taking unique events (Pentecost) as repeatable patterns",
            "Missing the transitional nature of this period",
            "Ignoring Luke's theological agenda in selecting what to report",
        ],
        "application_questions": [
            "Is this event presented as a pattern or as a unique occurrence?",
            "Does the rest of the NT confirm this as normative?",
            "What was Luke's purpose in including this account?",
        ],
    },
    "gospel": {
        "name": "Gospels",
        "key_principle": "Two-level documents (Jesus' original context + evangelist's purpose)",
        "approach": [
            "Consider both Jesus' original meaning and the Gospel writer's purpose",
            "Each Gospel has a specific audience and theological emphasis",
            "Context in Jesus' ministry: Who is he speaking to?",
            "How does this teaching function in the Gospel's overall narrative?",
            "Compare parallel accounts to see each writer's emphasis",
        ],
        "common_errors": [
            "Harmonizing too quickly without hearing each Gospel's voice",
            "Ignoring Jesus' audience (Pharisees, disciples, crowds)",
            "Missing the already/not-yet tension of the Kingdom",
            "Applying everything directly without considering the cross",
        ],
        "application_questions": [
            "Who was Jesus addressing and what was their situation?",
            "How does the cross and resurrection affect this teaching?",
            "What does this tell us about Jesus and his Kingdom?",
        ],
    },
    "parable": {
        "name": "Parables",
        "key_principle": "Find the main point; don't allegorize every detail",
        "approach": [
            "Identify the one or two main points - parables are not allegories",
            "Consider the audience: Who is Jesus speaking to and why?",
            "Look for cultural background that illuminates meaning",
            "The unexpected twist often carries the main message",
            "Let the context determine the interpretation",
        ],
        "common_errors": [
            "Allegorizing every detail (the donkey represents X...)",
            "Missing the shock value for the original audience",
            "Ignoring the immediate context of why Jesus told this",
            "Creating theological systems from parabolic details",
        ],
        "application_questions": [
            "What is the one main point Jesus is making?",
            "What would have surprised or challenged the original hearers?",
            "How does this teach us about the Kingdom of God?",
        ],
    },
    "law": {
        "name": "Law (Torah)",
        "key_principle": "Covenant stipulations; distinguish civil/ritual/ethical categories",
        "approach": [
            "The Law is Israel's covenant document, not a universal law code",
            "Distinguish: Apodictic (absolute) vs. Case law (situational)",
            "Categories: Civil (Israel's government), Ritual (worship), Ethical (moral)",
            "The Law reveals God's character even when specific commands don't apply",
            "Christ fulfills the Law - consider its purpose in light of the gospel",
        ],
        "common_errors": [
            "Applying Israel's civil laws directly to modern nations",
            "Ignoring the ritual laws entirely instead of finding their purpose",
            "Cherry-picking laws without consistent hermeneutic",
            "Moralizing without seeing the redemptive purpose",
        ],
        "application_questions": [
            "What does this reveal about God's character and values?",
            "How is this fulfilled or transformed in Christ?",
            "What principle stands behind this specific regulation?",
        ],
    },
    "prophet": {
        "name": "Prophets",
        "key_principle": "Covenant enforcement; check if 'future' is now past",
        "approach": [
            "Prophets were covenant enforcement officers - calling Israel back",
            "Most 'predictions' were about events now in our past",
            "The prophetic lawsuit: accusation, judgment, hope",
            "Distinguish near fulfillment from ultimate/eschatological fulfillment",
            "Poetry and metaphor are the normal mode of prophetic speech",
        ],
        "common_errors": [
            "Reading all prophecy as about the end times",
            "Literalizing poetic and metaphorical language",
            "Ignoring the historical context of the original prophecy",
            "Creating detailed end-times timelines from prophetic poetry",
        ],
        "application_questions": [
            "What covenant violation was being addressed?",
            "Has this prophecy been fulfilled, or does it await fulfillment?",
            "What does this reveal about God's character and purposes?",
        ],
    },
    "psalm": {
        "name": "Psalms",
        "key_principle": "Poetry/prayer; understand the types (lament, thanksgiving, praise)",
        "approach": [
            "Psalms are inspired responses to God - poetry, not doctrine",
            "Identify the type: Lament, Thanksgiving, Praise, Royal, Wisdom, etc.",
            "Poetry uses metaphor, hyperbole, and parallelism",
            "The emotions are real and God-given - even the difficult ones",
            "Many psalms find their ultimate fulfillment in Christ",
        ],
        "common_errors": [
            "Treating poetic expressions as doctrinal statements",
            "Ignoring the emotional dimension of the psalms",
            "Literalizing metaphorical language",
            "Skipping the imprecatory psalms or sanitizing them",
        ],
        "application_questions": [
            "What type of psalm is this and what is its function?",
            "What honest emotion is being expressed to God?",
            "How does this psalm find fulfillment in Christ?",
        ],
    },
    "wisdom": {
        "name": "Wisdom Literature",
        "key_principle": "General truths, not guarantees; compare with full canon",
        "approach": [
            "Proverbs are general truths, not absolute promises",
            "Wisdom literature wrestles with life's complexity",
            "Job and Ecclesiastes challenge simplistic interpretations",
            "The fear of the Lord is the foundation of all wisdom",
            "Compare individual proverbs with the full biblical witness",
        ],
        "common_errors": [
            "Treating Proverbs as unconditional promises (e.g., child-training)",
            "Ignoring the dialogue format in Job (not all speeches are true)",
            "Missing the 'under the sun' perspective in Ecclesiastes",
            "Applying isolated proverbs without considering counter-proverbs",
        ],
        "application_questions": [
            "Is this a general principle or being stated as an absolute?",
            "How does the rest of Scripture nuance this teaching?",
            "What does this reveal about living skillfully before God?",
        ],
    },
    "apocalyptic": {
        "name": "Revelation/Apocalyptic",
        "key_principle": "Apocalyptic imagery; already/not yet eschatology",
        "approach": [
            "Apocalyptic is a literary genre with its own conventions",
            "Symbols are stock imagery (beasts, numbers) with recognized meanings",
            "The primary message is: God wins, evil is judged, Christ reigns",
            "Read in light of OT prophets and the already/not yet tension",
            "Multiple valid interpretive approaches exist (preterist, futurist, idealist)",
        ],
        "common_errors": [
            "Literalizing symbolic imagery (666 as a barcode, locusts as helicopters)",
            "Creating detailed chronological timelines",
            "Ignoring the first-century context and audience",
            "Missing the pastoral purpose: encouragement for suffering believers",
        ],
        "application_questions": [
            "What comfort or challenge did this offer the original readers?",
            "What does this reveal about God's sovereignty and Christ's victory?",
            "Am I interpreting symbols consistently with OT usage?",
        ],
    },
}

# Conditions that suggest checking Greek/Hebrew
GREEK_HEBREW_TRIGGERS = [
    "Multiple translations disagree significantly on a key term",
    "A word carries significant theological weight",
    "Understanding word morphology would clarify meaning",
    "Cross-references depend on shared vocabulary",
    "The user asks about original language meaning",
    "A hapax legomenon (word appearing only once) is involved",
    "The word has a technical theological meaning",
]


def get_genre(book_abbrev: str) -> Genre | None:
    """
    Get the genre for a biblical book.

    Args:
        book_abbrev: Three-letter book abbreviation (e.g., 'Gen', 'Rom')

    Returns:
        The Genre for the book, or None if not found
    """
    return BOOK_GENRES.get(book_abbrev)


def get_genre_from_reference(reference: str) -> Genre | None:
    """
    Extract genre from a Bible reference.

    Args:
        reference: A Bible reference like 'John 3:16' or 'Rom.3.21'

    Returns:
        The Genre for the book, or None if not determinable
    """
    import re

    # Handle format like "Jhn.3.16"
    match = re.match(r'^(\w{3})\.\d+\.\d+', reference)
    if match:
        return BOOK_GENRES.get(match.group(1))

    # Handle format like "John 3:16" or "1 Corinthians 13:4"
    book_map = {
        "genesis": "Gen", "gen": "Gen",
        "exodus": "Exo", "exod": "Exo", "ex": "Exo",
        "leviticus": "Lev", "lev": "Lev",
        "numbers": "Num", "num": "Num",
        "deuteronomy": "Deu", "deut": "Deu",
        "joshua": "Jos", "josh": "Jos",
        "judges": "Jdg", "judg": "Jdg",
        "ruth": "Rut",
        "1 samuel": "1Sa", "1sam": "1Sa",
        "2 samuel": "2Sa", "2sam": "2Sa",
        "1 kings": "1Ki", "1kgs": "1Ki",
        "2 kings": "2Ki", "2kgs": "2Ki",
        "1 chronicles": "1Ch", "1chr": "1Ch",
        "2 chronicles": "2Ch", "2chr": "2Ch",
        "ezra": "Ezr",
        "nehemiah": "Neh", "neh": "Neh",
        "esther": "Est", "esth": "Est",
        "job": "Job",
        "psalms": "Psa", "psalm": "Psa", "ps": "Psa",
        "proverbs": "Pro", "prov": "Pro",
        "ecclesiastes": "Ecc", "eccl": "Ecc",
        "song of solomon": "Sng", "song": "Sng",
        "isaiah": "Isa", "isa": "Isa",
        "jeremiah": "Jer", "jer": "Jer",
        "lamentations": "Lam", "lam": "Lam",
        "ezekiel": "Ezk", "ezek": "Ezk",
        "daniel": "Dan", "dan": "Dan",
        "hosea": "Hos", "hos": "Hos",
        "joel": "Jol",
        "amos": "Amo",
        "obadiah": "Oba", "obad": "Oba",
        "jonah": "Jon",
        "micah": "Mic", "mic": "Mic",
        "nahum": "Nam", "nah": "Nam",
        "habakkuk": "Hab", "hab": "Hab",
        "zephaniah": "Zep", "zeph": "Zep",
        "haggai": "Hag", "hag": "Hag",
        "zechariah": "Zec", "zech": "Zec",
        "malachi": "Mal", "mal": "Mal",
        "matthew": "Mat", "matt": "Mat", "mt": "Mat",
        "mark": "Mrk", "mk": "Mrk",
        "luke": "Luk", "lk": "Luk",
        "john": "Jhn", "jn": "Jhn",
        "acts": "Act",
        "romans": "Rom", "rom": "Rom",
        "1 corinthians": "1Co", "1cor": "1Co",
        "2 corinthians": "2Co", "2cor": "2Co",
        "galatians": "Gal", "gal": "Gal",
        "ephesians": "Eph", "eph": "Eph",
        "philippians": "Php", "phil": "Php",
        "colossians": "Col", "col": "Col",
        "1 thessalonians": "1Th", "1thess": "1Th",
        "2 thessalonians": "2Th", "2thess": "2Th",
        "1 timothy": "1Ti", "1tim": "1Ti",
        "2 timothy": "2Ti", "2tim": "2Ti",
        "titus": "Tit",
        "philemon": "Phm", "phlm": "Phm",
        "hebrews": "Heb", "heb": "Heb",
        "james": "Jas", "jas": "Jas",
        "1 peter": "1Pe", "1pet": "1Pe",
        "2 peter": "2Pe", "2pet": "2Pe",
        "1 john": "1Jn", "1jn": "1Jn",
        "2 john": "2Jn", "2jn": "2Jn",
        "3 john": "3Jn", "3jn": "3Jn",
        "jude": "Jud",
        "revelation": "Rev", "rev": "Rev",
    }

    match = re.match(r'^(\d?\s*[\w\u0b80-\u0bff ]+?)\s*\d+\s*[:.]\s*\d+', reference.strip())
    if match:
        book_name = match.group(1).lower().strip().translate(str.maketrans("௦௧௨௩௪௫௬௭௮௯", "0123456789"))
        abbrev = TA_BOOK_REVERSE.get(book_name) or book_map.get(book_name)
        if abbrev:
            return BOOK_GENRES.get(abbrev)

    return None


def get_interpretation_guidelines(genre: Genre) -> dict:
    """
    Get the interpretation guidelines for a specific genre.

    Args:
        genre: The biblical genre

    Returns:
        Dictionary with name, key_principle, approach, common_errors, and application_questions
    """
    return GENRE_GUIDELINES.get(genre, {})


def format_genre_guidance(genre: Genre) -> str:
    """
    Format genre guidance as a readable string for agent consumption.

    Args:
        genre: The biblical genre

    Returns:
        Formatted string with interpretation guidelines
    """
    guidelines = GENRE_GUIDELINES.get(genre)
    if not guidelines:
        return ""

    lines = [
        f"## Genre: {guidelines['name']}",
        "",
        f"**Key Principle**: {guidelines['key_principle']}",
        "",
        "### Interpretive Approach:",
    ]

    for item in guidelines["approach"]:
        lines.append(f"- {item}")

    lines.extend([
        "",
        "### Common Errors to Avoid:",
    ])

    for item in guidelines["common_errors"]:
        lines.append(f"- {item}")

    lines.extend([
        "",
        "### Questions for Application:",
    ])

    for item in guidelines["application_questions"]:
        lines.append(f"- {item}")

    return "\n".join(lines)


# =========================================================================
# Tamil genre guidance — faithful translations of the Fee & Stuart-derived
# guidelines above, so Tamil readers receive the interpretive framework in
# Tamil. The English original remains authoritative for verification.
# =========================================================================

GENRE_GUIDELINES_TA: dict[str, dict] = {
    "epistle": {
        "name": "நிருபங்கள் (திருமுகங்கள்)",
        "key_principle": "சூழலோடு சிந்தியுங்கள் — இந்த மடல் எந்தப் பிரச்சினையை எதிர்கொண்டது?",
        "approach": [
            "நிகழ்வை அறியுங்கள்: இந்த மடலை எழுத வைத்த பிரச்சினை அல்லது சூழ்நிலை என்ன?",
            "எழுதியவருக்கும் பெற்றுக்கொண்டவர்களுக்கும் இடையிலான உறவைப் புரிந்துகொள்ளுங்கள்",
            "வாதத்தின் ஓட்டத்தை உணர முழு மடலையும் ஒரே வாசிப்பில் படியுங்கள்",
            "தர்க்க இணைப்புச் சொற்களுக்குக் கவனம் தருங்கள் (ஆகையால், ஏனெனில், அப்படியிருக்கையில்)",
            "மைய வாதத்தையும் துணை வாதங்களையும் வேறுபடுத்திக் காணுங்கள்",
        ],
        "common_errors": [
            "வசனங்களை அவற்றின் வாதச் சூழலிலிருந்து பிரித்தெடுத்துப் பயன்படுத்துதல்",
            "உரையாற்றப்பட்ட வரலாற்றுச் சூழ்நிலையைப் புறக்கணித்தல்",
            "ஒவ்வொரு கூற்றையும் எல்லாக் காலத்துக்குமான கட்டளையாக நடத்துதல்",
            "தனித்தனி பகுதிகளாக மட்டும் வாசித்து தர்க்க ஓட்டத்தை இழத்தல்",
        ],
        "application_questions": [
            "இது முதலாம் நூற்றாண்டின் குறிப்பிட்ட பிரச்சினையை உரைக்கிறதா, அல்லது எல்லாக் காலத்துக்குமான தத்துவமா?",
            "வேதாகமம் முழுவதின் சாட்சி இந்தப் போதனையை உறுதிப்படுத்துகிறதா?",
            "இந்த அறிவுறுத்தல் படைப்பு ஒழுங்குடன் தொடர்புடையதா, அல்லது கால-கலாச்சாரச் சூழலுடனா?",
        ],
    },
    "ot_narrative": {
        "name": "பழைய ஏற்பாட்டு வரலாற்றுக் கதைகள்",
        "key_principle": "மூன்று நிலைகள் (மேல்நிலை, தேசிய, தனிநபர்); விளக்குவதே ஒழிய கட்டளையிடுவதல்ல",
        "approach": [
            "நினைவில் கொள்ளுங்கள்: கதைகள் என்ன நடந்தது என்று விளக்குகின்றன; என்ன நடக்கவேண்டும் என்று அறிவுறுத்துவதில்லை",
            "மூன்று நிலைகளைப் பாருங்கள்: தேவனுடைய எல்லாத் திட்டம், இஸ்ரவேலின் கதை, தனிநபர்களின் வரலாறு",
            "கதாபாத்திரங்கள் எப்போதும் பின்பற்றத்தக்க மாதிரிகளல்ல — அவர்களுடைய குறைபாடுகளையும் காணுங்கள்",
            "கதை சொல்பவர் நேரடியாக இறையியல் கூற்றுகளைச் சொல்வதில்லை",
            "ஒவ்வொரு கதையிலும் உண்மையான நாயகன் தேவனே",
        ],
        "common_errors": [
            "ஒவ்வொரு கதாபாத்திரத்தின் செயலையும் பின்பற்ற வேண்டிய மாதிரியாக நடத்துதல்",
            "வெறும் வரலாற்று உண்மைகளை உவமையாக்குதல்",
            "இரட்சிப்பு-வரலாற்றின் பெரிய நோக்கத்தைக் காணாமல் இருத்தல்",
            "தேவனுடைய செயலைக் காணாமல் 'தாவீது போல் தைரியமாயிரு' என்று நீதிபாடமாக்குதல்",
        ],
        "application_questions": [
            "தேவனுடைய சுபாவத்தையும் நோக்கங்களையும் இது எப்படி வெளிப்படுத்துகிறது?",
            "இரட்சிப்பின் பெரிய கதையில் இது எங்குப் பொருந்துகிறது?",
            "இந்தச் செயல் அங்கீகரிக்கப்பட்டதா, கண்டிக்கப்பட்டதா, அல்லது வெறுமனே பதிவு செய்யப்பட்டதா?",
        ],
    },
    "acts": {
        "name": "அப்போஸ்தலர் பணிகள் (வரலாற்று நாடகக் கதை)",
        "key_principle": "வரலாற்று முன்னுதாரணம் vs கட்டாயப் போதனை — திரும்பத் திரும்ப நடப்பதெல்லாம் கட்டாயமல்ல",
        "approach": [
            "அப்போஸ்தலர் பணிகள் இறையியல் வரலாறு — லூக்கா ஒரு கருத்தை வலியுறுத்துகிறார்",
            "சபை 'செய்ததையும்' நாம் 'செய்யவேண்டியதையும்' வேறுபடுத்துங்கள்",
            "பலமுறை திரும்பத் திரும்ப வரும் முறைகள் கட்டாயப் போதனையாக இருக்கலாம்",
            "ஒரேமுறை நடந்த நிகழ்வுகள் எல்லாக் காலத்துக்குமான முறையாக இருக்கவேண்டியதில்லை",
            "சித்தாந்தத்தைப் புரிந்துகொள்ள நிருபங்களோடு இணைத்துப் படியுங்கள்",
        ],
        "common_errors": [
            "அப்போஸ்தலர் பணிகளில் உள்ள ஒவ்வொரு முறையையும் இன்றைய சபைகளுக்குக் கட்டாயப்படுத்துதல்",
            "ஒரேமுறை நடந்த நிகழ்வுகளை (பெந்தகோஸ்து) திரும்ப நடக்கக்கூடிய முறையாக எடுத்துக்கொள்ளல்",
            "இந்தக் காலத்தின் மாற்றுத் தன்மையைக் காணாமல் இருத்தல்",
            "லூக்கா என்ன சேர்க்கையாகத் தேர்ந்தெடுத்தார் என்பதில் அவருடைய இறையியல் நோக்கத்தை மறத்தல்",
        ],
        "application_questions": [
            "இந்த நிகழ்வு முறையாகச் சொல்லப்பட்டதா, அல்லது ஒரு தனித்த நிகழ்வாக?",
            "நியாயப்பிரமாணத்தின் மற்ற பகுதிகள் இதைக் கட்டாயப் போதனையாக உறுதிப்படுத்துகின்றனவா?",
            "இந்தச் சம்பவத்தைச் சேர்த்ததில் லூக்காவின் நோக்கம் என்ன?",
        ],
    },
    "gospel": {
        "name": "சுவிஷேசங்கள்",
        "key_principle": "இரு நிலை ஆவணங்கள் (இயேசுவின் மூலச் சூழல் + சுவிஷேச எழுத்தாளரின் நோக்கம்)",
        "approach": [
            "இயேசுவின் மூல அர்த்தத்தையும் சுவிஷேச எழுத்தாளரின் நோக்கத்தையும் இரண்டையும் கருதுங்கள்",
            "ஒவ்வொரு சுவிஷேசத்திற்கும் குறிப்பிட்ட இலக்கு வாசகர்களும் இறையியல் வலியுறுத்தல்களும் உண்டு",
            "இயேசுவின் பணிச் சூழல்: அவர் யாருக்குப் பேசுகிறார்?",
            "இந்தப் போதனை சுவிஷேசத்தின் மொத்தக் கதையில் எப்படி இடம்பெறுகிறது?",
            "இணை விவரணங்களை ஒப்பிட்டு ஒவ்வொரு எழுத்தாளரின் வலியுறுத்தலையும் காணுங்கள்",
        ],
        "common_errors": [
            "ஒவ்வொரு சுவிஷேசத்தின் குரலைக் கேட்காமல் விரைவில் சேர்த்து இணைத்தல்",
            "இயேசு யாருக்குப் பேசினார் என்பதை (பரிசேயர், சீடர்கள், ஜனங்கள்) மறத்தல்",
            "ராஜ்யத்தின் 'ஏற்கனவே வந்தது / இன்னும் வரவில்லை' பதற்றத்தைக் காணாமல் இருத்தல்",
            "சிலுவையைக் கருதாமல் எல்லாவற்றையும் நேரடியாகப் பயன்படுத்திக்கொள்ளல்",
        ],
        "application_questions": [
            "இயேசு யாரை உரையாற்றினார், அவர்களுடைய நிலை என்ன?",
            "சிலுவையும் உயிர்த்தெழுதலும் இந்தப் போதனையை எப்படி மாற்றுகின்றன?",
            "இயேசுவையும் அவருடைய ராஜ்யத்தையும் பற்றி இது என்ன சொல்கிறது?",
        ],
    },
    "parable": {
        "name": "உவமைகள்",
        "key_principle": "மையக் கருத்தைக் கண்டுபிடி; ஒவ்வொரு விவரத்தையும் உவமையாக்காதே",
        "approach": [
            "ஒன்று அல்லது இரண்டு மையக் கருத்துகளை அறிந்துகொள்ளுங்கள் — உவமைகள் ஒவ்வொரு விவரமும் அர்த்தமுடைய கதைகளல்ல",
            "கேட்போரைக் கருதுங்கள்: இயேசு யாருக்குப் பேசுகிறார், ஏன்?",
            "அர்த்தத்தை வெளிக்காட்டும் கலாச்சாரப் பின்னணியைப் பாருங்கள்",
            "எதிர்பாராத திருப்பமே பெரும்பாலும் மையச் செய்தியைத் தாங்குகிறது",
            "விளக்கத்தை சூழலே தீர்மானிக்கட்டும்",
        ],
        "common_errors": [
            "ஒவ்வொரு விவரத்தையும் உவமையாக்குதல் (கழுதை என்பது அத்தனை...)",
            "மூலக் கேட்போருக்கு இருந்த அதிர்ச்சியைக் காணாமல் இருத்தல்",
            "இயேசு ஏன் இதைச் சொன்னார் என்ற உடனடிச் சூழலைப் புறக்கணித்தல்",
            "உவமை விவரங்களிலிருந்து சித்தாந்த அமைப்புகளைக் கட்டமைத்தல்",
        ],
        "application_questions": [
            "இயேசு சொல்லும் ஒரே மையக் கருத்து என்ன?",
            "மூலக் கேட்போரை எது வியப்படுத்தியிருக்கும் அல்லது சவால் விடும்?",
            "தேவனுடைய ராஜ்யத்தைப் பற்றி இது எதைக் கற்பிக்கிறது?",
        ],
    },
    "law": {
        "name": "வேத நியமங்கள் (தோரா)",
        "key_principle": "உடன்படிக்கை நியமங்கள்; குடிமை/ஆராதனை/நீதி வகைகளை வேறுபடுத்துங்கள்",
        "approach": [
            "வேதம் இஸ்ரவேலின் உடன்படிக்கை ஆவணம்; உலகளாவிய சட்டத் தொகுப்பல்ல",
            "கட்டளை வகைகளை வேறுபடுத்துங்கள்: நிபந்தனையற்ற (முற்றான) கட்டளைகள் vs நிகழ்வு சார்ந்த வழக்கு நியமங்கள்",
            "பிரிவுகள்: குடிமை (இஸ்ரவேல் ஆட்சி), ஆராதனை (வழிபாடு), நீதி (தார்மீகம்)",
            "குறிப்பிட்ட கட்டளைகள் இன்று பொருந்தாவிட்டாலும், வேதம் தேவனுடைய சுபாவத்தை வெளிப்படுத்துகிறது",
            "கிறிஸ்து வேதத்தை நிறைவுசெய்கிறார் — சுவிஷேசத்தின் வெளிச்சத்தில் அதன் நோக்கத்தைக் கருதுங்கள்",
        ],
        "common_errors": [
            "இஸ்ரவேலின் குடிமைச் சட்டங்களை நேரடியாக நவீன தேசங்களுக்குப் பயன்படுத்துதல்",
            "ஆராதனை நியமங்களின் நோக்கத்தைத் தேடாமல் முழுவதையும் நிராகரித்தல்",
            "நிலையான விளக்கக் கொள்கை இல்லாமல் சில நியமங்களை மட்டும் தேர்ந்தெடுத்தல்",
            "இரட்சிப்பு நோக்கத்தைக் காணாமல் வெறும் நீதிபாடங்களாக்குதல்",
        ],
        "application_questions": [
            "தேவனுடைய சுபாவத்தையும் மதிப்புகளையும் இது எப்படி வெளிப்படுத்துகிறது?",
            "இது கிறிஸ்துவில் எப்படி நிறைவுறுகிறது அல்லது மாற்றம் பெறுகிறது?",
            "இந்தக் குறிப்பிட்ட நியமத்திற்குப் பின்னால் இருக்கும் தத்துவம் என்ன?",
        ],
    },
    "prophet": {
        "name": "தீர்க்கதரிசிகள்",
        "key_principle": "உடன்படிக்கையை அமல்படுத்துதல்; 'எதிர்காலம்' இப்போது கடந்த காலமாகிவிட்டதா என்று பாருங்கள்",
        "approach": [
            "தீர்க்கதரிசிகள் உடன்படிக்கையை அமல்படுத்துபவர்கள் — இஸ்ரவேலை மீண்டும் திரும்ப அழைப்பவர்கள்",
            "'பிரவசனங்கள்' பெரும்பாலும் இப்போது நம் கடந்த காலத்தில் நிறைவேறிய நிகழ்வுகளைப் பற்றியவை",
            "தீர்க்கதரிசன வழக்கு முறை: குற்றச்சாட்டு, தீர்ப்பு, நம்பிக்கை",
            "அண்மைய நிறைவேற்றத்தையும் இறுதி/இறையியல் நிறைவேற்றத்தையும் வேறுபடுத்துங்கள்",
            "கவிதையும் உவமையுமே தீர்க்கதரிசன மொழியின் இயல்பான வடிவம்",
        ],
        "common_errors": [
            "எல்லா பிரவசனங்களையும் இறுதிக்காலம் பற்றியதாகப் படித்தல்",
            "கவிதை மற்றும் உவமை மொழியை எழுத்துப்படி எடுத்தல்",
            "மூல பிரவசனத்தின் வரலாற்றுச் சூழலைப் புறக்கணித்தல்",
            "தீர்க்கதரிசனக் கவிதையிலிருந்து விரிவான இறுதிக்கால நாள்காட்டிகளை உருவாக்குதல்",
        ],
        "application_questions": [
            "எந்த உடன்படிக்கை மீறல் இங்கே உரைக்கப்படுகிறது?",
            "இந்தப் பிரவசனம் நிறைவேறியதா, அல்லது நிறைவேற இருக்கிறதா?",
            "தேவனுடைய சுபாவத்தையும் நோக்கங்களையும் இது எப்படி வெளிப்படுத்துகிறது?",
        ],
    },
    "psalm": {
        "name": "சங்கீதங்கள் (கீதங்கள்)",
        "key_principle": "கவிதை/ஜெபம்; வகைகளைப் புரிந்துகொள்ளுங்கள் (புலம்பல், நன்றி, ஸ்தோத்திரம்)",
        "approach": [
            "சங்கீதங்கள் தேவனுக்கு உள்ளத்தால் செய்யப்படும் பிரதிபலிப்புகள் — போதனை நூல்களல்ல, கவிதை",
            "வகையை அறிந்துகொள்ளுங்கள்: புலம்பல், நன்றி, ஸ்தோத்திரம், ராஜகீதம், ஞானக் கீதம்",
            "கவிதை உவமை, மிகைப்பேச்சு, இணைச்சொற்கோவை (parallelism) ஆகியவற்றைப் பயன்படுத்துகிறது",
            "உணர்ச்சிகள் உண்மையானவை; தேவனால் கொடுக்கப்பட்டவை — கடினமானவையாக இருந்தாலும்",
            "பல சங்கீதங்கள் கிறிஸ்துவில் தங்களுடைய இறுதி நிறைவைக் காண்கின்றன",
        ],
        "common_errors": [
            "கவிதை வெளிப்பாடுகளைச் சித்தாந்தக் கூற்றுகளாக நடத்துதல்",
            "சங்கீதங்களின் உணர்ச்சிப் பரிமாணத்தைப் புறக்கணித்தல்",
            "உவமை மொழியை எழுத்துப்படி எடுத்தல்",
            "சபத சங்கீதங்களை (imprecatory psalms) தாண்டிச் செல்வது அல்லது மென்மையாக்குவது",
        ],
        "application_questions": [
            "இது எந்த வகை சங்கீதம், அதன் பணி என்ன?",
            "தேவனுக்கு எந்த உண்மையான உணர்ச்சி இங்கே வெளிப்படுத்தப்படுகிறது?",
            "இந்த சங்கீதம் கிறிஸ்துவில் எப்படி நிறைவு பெறுகிறது?",
        ],
    },
    "wisdom": {
        "name": "ஞான இலக்கியம்",
        "key_principle": "பொதுவான உண்மைகளே ஒழிய பூரண வாக்குறுதிகளல்ல; முழு வேதாகமத்தோடு ஒப்பிடுங்கள்",
        "approach": [
            "நீதிமொழிகள் பொதுவான உண்மைகள்; நிபந்தனையற்ற வாக்குறுதிகளல்ல",
            "ஞான இலக்கியம் வாழ்க்கையின் சிக்கல்களுடன் போராடுகிறது",
            "யோபும் பிரசங்கியும் எளிமையான விளக்கங்களைச் சவால் செய்கின்றன",
            "கர்த்தருக்குப் பயமுறுதலே எல்லா ஞானத்தினுடைய அடிப்படை",
            "ஒவ்வொரு நீதிமொழியையும் முழு வேதாகமச் சாட்சியோடு ஒப்பிடுங்கள்",
        ],
        "common_errors": [
            "நீதிமொழிகளை நிபந்தனையற்ற வாக்குறுதிகளாக நடத்துதல் (உதா: குழந்தைப் பரிபாலனம்)",
            "யோபுவின் உரையாடல் அமைப்பைப் புறக்கணித்தல் (எல்லா பேச்சுகளும் உண்மையல்ல)",
            "பிரசங்கியின் 'சூரியனுக்குக் கீழ்' பார்வையைக் காணாமல் இருத்தல்",
            "எதிர்-நீதிமொழிகளைக் கருதாமல் தனித்த நீதிமொழிகளைப் பயன்படுத்துதல்",
        ],
        "application_questions": [
            "இது பொதுத் தத்துவமா, அல்லது முற்றான உண்மையாகச் சொல்லப்படுகிறதா?",
            "வேதாகமத்தின் மற்ற பகுதிகள் இந்தப் போதனையை எப்படி நுட்பமாக்குகின்றன?",
            "தேவனுடைய முன்னிலையில் ஞானமாக வாழ்வது பற்றி இது என்ன வெளிப்படுத்துகிறது?",
        ],
    },
    "apocalyptic": {
        "name": "வெளிப்படைப் பிரவசனம் (திருவெளிப்பாடு)",
        "key_principle": "வெளிப்படைப் பிம்பங்கள்; 'ஏற்கனவே / இன்னும் இல்லை' இறுதிகாலவியல்",
        "approach": [
            "வெளிப்படைப் பிரவசனம் சொந்த மரபுகளுடைய ஒரு இலக்கிய வகை",
            "சின்னங்கள் அறியப்பட்ட அர்த்தமுடைய வழக்கமான பிம்பங்கள் (மிருகங்கள், எண்கள்)",
            "மையச் செய்தி: தேவனே வெல்கிறார், தீமை தீர்ப்புக்குள்ளாகிறது, கிறிஸ்து ராஜ்யம் செய்கிறார்",
            "பழைய ஏற்பாட்டு தீர்க்கதரிசிகளின் வெளிச்சத்திலும் 'ஏற்கனவே/இன்னும் இல்லை' பதற்றத்திலும் படியுங்கள்",
            "பல செல்லத்தக்க விளக்க அணுகுமுறைகள் உண்டு (preterist, futurist, idealist)",
        ],
        "common_errors": [
            "சின்னப் பிம்பங்களை எழுத்துப்படி எடுத்தல் (666 ஐ பார்கோடாக, வெட்டுக்கிளிகளை ஹெலிகாப்டர்களாக)",
            "விரிவான காலவரிசை நாள்காட்டிகளை உருவாக்குதல்",
            "முதலாம் நூற்றாண்டுச் சூழலையும் இலக்கு வாசகர்களையும் புறக்கணித்தல்",
            "பணிவாய்ந்த நோக்கத்தைக் காணாமல் இருத்தல்: துன்பப்படும் விசுவாசிகளுக்கு ஆறுதல்",
        ],
        "application_questions": [
            "மூல வாசகர்களுக்கு இது எந்த ஆறுதலை அல்லது சவாலைக் கொடுத்தது?",
            "தேவனுடைய ஆட்சியையும் கிறிஸ்துவின் வெற்றியையும் பற்றி இது என்ன வெளிப்படுத்துகிறது?",
            "பழைய ஏற்பாட்டு பயன்பாட்டோடு இசைவாக சின்னங்களை நான் விளக்குகிறேனா?",
        ],
    },
}


def format_genre_guidance(genre: Genre) -> str:
    """
    Format genre guidance as a readable string — Tamil guidance first (faithful
    translation of the Fee & Stuart-derived framework), with the English key
    principle retained beneath for verification.

    Args:
        genre: The biblical genre

    Returns:
        Formatted string with interpretation guidelines
    """
    guidelines = GENRE_GUIDELINES.get(genre)
    if not guidelines:
        return ""

    ta = GENRE_GUIDELINES_TA.get(genre, {})
    lines = []

    if ta:
        lines.append(f"## வகை (Genre): {ta['name']} — {guidelines['name']}")
        lines.append("")
        lines.append(f"**முக்கியக் கொள்கை**: {ta['key_principle']}")
        lines.append(f"*Key Principle (EN)*: {guidelines['key_principle']}")
        lines.append("")
        lines.append("### விளக்க அணுகுமுறை:")
        for item in ta["approach"]:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("### தவிர்க்கவேண்டிய பொதுவான தவறுகள்:")
        for item in ta["common_errors"]:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("### பிரயோகத்திற்கான கேள்விகள்:")
        for item in ta["application_questions"]:
            lines.append(f"- {item}")
    else:
        lines = [
            f"## Genre: {guidelines['name']}",
            "",
            f"**Key Principle**: {guidelines['key_principle']}",
            "",
            "### Interpretive Approach:",
        ]
        for item in guidelines["approach"]:
            lines.append(f"- {item}")
        lines.extend(["", "### Common Errors to Avoid:"])
        for item in guidelines["common_errors"]:
            lines.append(f"- {item}")
        lines.extend(["", "### Questions for Application:"])
        for item in guidelines["application_questions"]:
            lines.append(f"- {item}")

    return "\n".join(lines)


def should_check_original_language(context: str) -> list[str]:
    """
    Determine if checking Greek/Hebrew would be valuable.

    Args:
        context: The current study context or question

    Returns:
        List of reasons why original language study would be valuable
    """
    context_lower = context.lower()
    triggers = []

    # Check for explicit requests
    if any(word in context_lower for word in ["greek", "hebrew", "original", "strongs", "strong's"]):
        triggers.append("User is asking about original language meaning")

    # Check for word study indicators
    if any(phrase in context_lower for phrase in ["what does the word mean", "meaning of", "definition of"]):
        triggers.append("Word study would clarify meaning")

    # Check for theological terms
    theological_terms = [
        "love", "faith", "grace", "sin", "salvation", "justification", "righteousness",
        "sanctification", "atonement", "covenant", "holy", "spirit", "baptism", "lord",
        "kingdom", "gospel", "peace", "glory", "redemption", "propitiation", "reconciliation"
    ]
    for term in theological_terms:
        if term in context_lower:
            triggers.append(f"The term '{term}' has significant theological weight")
            break

    # Check for translation comparison
    if any(phrase in context_lower for phrase in ["translations differ", "some translations", "different version"]):
        triggers.append("Multiple translations disagree - original language would clarify")

    return triggers


def get_reasoning_pattern() -> str:
    """
    Get the hermeneutical reasoning pattern for agent use — bilingual
    (Tamil first, English beneath).
    """
    return """
## வேதாகம விளக்கத்தின் சிந்தனை முறை / Hermeneutical Reasoning Pattern

ஒரு வேதாகமப் பாடத்தைப் படிக்கும்போது இந்த வரிசையைப் பின்பற்றுங்கள்:

1. **அறிதல் (IDENTIFY)**: இந்தக் கேள்விக்கு எந்த வேதாகமப் பாடங்கள் தொடர்புடையவை?
   - குறிப்பிட்ட பாடத்தைத் தேடிப் பாருங்கள்
   - உடனடிச் சூழலைக் கருதுங்கள்

2. **இலக்கிய வகை (GENRE)**: இது எந்த வகை இலக்கியம்?
   - வகைக்கு ஏற்ற விளக்க முறைகளைப் பயன்படுத்துங்கள்
   - ஒரு வகைக்கான முறைகளை இன்னொரு வகையின் மேல் திணிக்காதீர்கள்

3. **சூழல் (CONTEXT)**:
   - **வரலாறு**: யார் யாருக்கு, எப்போது, ஏன் எழுதினார்கள்?
   - **இலக்கியம்**: முன்னும் பின்னும் என்ன இருக்கிறது? புத்தகத்தின் நோக்கம் என்ன?
   - **முழு வேதாகமம்**: வேதாகமம் முழுவதின் கதையில் இது எங்குப் பொருந்துகிறது?

4. **உள்ளடக்கம் (CONTENT)**:
   - உரை உண்மையில் என்ன சொல்கிறது?
   - சந்தேகமிருந்தால் பல மொழிபெயர்ப்புகளை ஒப்பிடுங்கள்
   - முக்கியமான சொற்களை கிரேக்கம்/எபிரேயத்தில் ஆராயுங்கள்

5. **குறுக்குப்பாடங்கள் (CROSS-REFERENCES)**: எந்தத் தொடர்புடைய பாடங்கள் இதற்கு ஒளி வீசுகின்றன?
   - வேதாகமத்தை வேதாகமமே விளக்குகிறது
   - கருப்பொருள் மற்றும் சொல்லாடல் தொடர்புகளைப் பாருங்கள்

6. **பிரயோகம் (APPLICATION)**: இன்றைக்கு நமக்கு இது எப்படிப் பொருந்துகிறது?
   - அக்காலத்திற்கும் இன்றைக்கும் உள்ள கலாச்சார வேறுபாடுகளைக் கருதுங்கள்
   - காலத்திற்குரிய கட்டளைகளுக்குப் பின்னால் இருக்கும் எல்லாக் காலத் தத்துவத்தைக் காணுங்கள்
   - சுவிஷேசத்தின் வெளிச்சத்தில் பிரயோகியுங்கள்

7. **நாகரிகம் (HUMILITY)**: விளக்கம் ஐயத்திற்குரியதாக இருக்கும் இடங்களைக் குறித்துக்கொள்ளுங்கள்
   - விசுவாசமான கிறிஸ்தவர்கள் கூட வேறுபடும் இடங்களை ஒப்புக்கொள்ளுங்கள்
   - தெளிவான போதனைக்கும் விவாதத்திற்குரிய விஷயங்களுக்கும் வேறுபாடு காண்பியுங்கள்
   - உண்மைகளை ஏற்றத்தாழ்வோடு வைத்திருங்கள்

---

When studying a biblical passage, follow this sequence:

1. **IDENTIFY**: What biblical text(s) are relevant to this question?
2. **GENRE**: What type of literature is this? Apply genre-specific methods.
3. **CONTEXT**: Historical, literary, canonical.
4. **CONTENT**: What does the text actually say? Check Greek/Hebrew when significant.
5. **CROSS-REFERENCES**: Scripture interprets Scripture.
6. **APPLICATION**: Find the timeless principle behind temporal commands.
7. **HUMILITY**: Note where interpretation is uncertain.
"""
