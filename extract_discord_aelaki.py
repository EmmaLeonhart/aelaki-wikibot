"""Extract all Aelaki-related content from Discord message exports.

Reads all JSON files in discord/ and produces organized documentation
in discord/extracted/ with vocabulary, grammar notes, and examples.
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime


DISCORD_DIR = Path("discord")
OUTPUT_DIR = Path("discord/extracted")


def load_all_messages():
    """Load all messages from all Discord JSON files."""
    messages = []
    for root, dirs, files in os.walk(DISCORD_DIR):
        for fname in files:
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(root, fname)
            # Skip output dir
            if "extracted" in fpath:
                continue
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            channel = Path(root).parent.name + "/" + Path(root).name
            for msg in data:
                msg["_source_channel"] = channel
                msg["_source_file"] = fname
            messages.extend(data)
    # Sort by timestamp
    messages.sort(key=lambda m: m.get("timestamp", ""))
    return messages


def is_aelaki_related(text):
    """Check if a message mentions Aelaki or related conlang terms."""
    if not text:
        return False
    lower = text.lower()
    keywords = [
        "aelaki", "conlang", "triconsonantal", "tetraconsonantal",
        "stative", "evidential", "gnomic", "inchoative", "cessative",
        "resumptive", "hodiernal", "hesternal", "crastinal",
        "zoduk", "dedik", "dapaz", "kmdr", "debh", "sugh",
        "ringworld", "non-concatenative", "templatic",
        "ki syllable", "ki-syllable", "ki clitic",
        "gender vowel", "person consonant",
        "child gender", "inanimate gender",
        "collective shift", "umlaut", "zero-infix",
        "pseudopronoun", "polypersonal",
        "converb", "adverbial number", "partitive",
        "base-12", "base-60", "dozenal", "sexagesimal",
        "maomao", "thijith", "thishith", "thikith",
        "abugida", "my conlang", "my language", "my lang",
        "in my lang", "in aelaki",
    ]
    return any(kw in lower for kw in keywords)


def has_aelaki_wordforms(text):
    """Check if text contains likely Aelaki word forms (capitalized exotic words)."""
    if not text:
        return False
    # Look for words with special chars common in Aelaki
    aelaki_chars = ["ë", "ü", "ï", "ə", "æ", "ŋ", "zh", "kx", "ng"]
    for ch in aelaki_chars:
        if ch in text.lower():
            return True
    return False


def extract_word_forms(text):
    """Extract potential Aelaki word forms from a message."""
    forms = []
    # Look for words with Aelaki-specific characters
    words = re.findall(r'\b\S+\b', text)
    aelaki_chars = set("ëüïəæŋ")
    for word in words:
        # Skip URLs and common English
        if word.startswith("http") or word.startswith("<") or word.startswith("@"):
            continue
        if any(c in word.lower() for c in aelaki_chars):
            forms.append(word)
    return forms


def extract_glosses(text):
    """Extract word = meaning pairs."""
    glosses = []
    # Pattern: Word = "meaning" or Word = meaning
    patterns = [
        r'(\w[\wëüïəæŋ]+)\s*=\s*["\']([^"\']+)["\']',
        r'(\w[\wëüïəæŋ]+)\s*=\s*(\w[\w\s,/]+?)(?:\n|$|\.|;)',
        r'(\w[\wëüïəæŋ]+)\s*[-–]\s*["\']([^"\']+)["\']',
        r'["\'](\w[\wëüïəæŋ]+)["\']\s*(?:means?|is)\s*["\']([^"\']+)["\']',
    ]
    for pat in patterns:
        for match in re.finditer(pat, text):
            glosses.append((match.group(1), match.group(2).strip()))
    return glosses


def format_message(msg):
    """Format a single message for output."""
    ts = msg.get("timestamp", "")
    if ts:
        try:
            dt = datetime.fromisoformat(ts.replace("+00:00", "+00:00"))
            ts = dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass
    content = msg.get("content", "")
    channel = msg.get("_source_channel", "")
    attachments = msg.get("attachments", [])
    att_note = ""
    if attachments:
        att_names = [a.get("filename", "?") for a in attachments]
        att_note = f" [attachments: {', '.join(att_names)}]"
    return f"[{ts}] #{channel}{att_note}\n{content}"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading all Discord messages...")
    messages = load_all_messages()
    print(f"  Total messages: {len(messages)}")

    # ── Filter Aelaki-related messages ──
    aelaki_msgs = []
    for msg in messages:
        content = msg.get("content", "")
        if is_aelaki_related(content) or has_aelaki_wordforms(content):
            aelaki_msgs.append(msg)

    print(f"  Aelaki-related messages: {len(aelaki_msgs)}")

    # ── 1. Full chronological dump of all Aelaki messages ──
    with open(OUTPUT_DIR / "all_aelaki_messages.md", "w", encoding="utf-8") as f:
        f.write("# All Aelaki-Related Discord Messages\n\n")
        f.write(f"Extracted from {len(messages)} total messages. "
                f"Found {len(aelaki_msgs)} Aelaki-related messages.\n\n")
        f.write("---\n\n")
        for msg in aelaki_msgs:
            f.write(format_message(msg))
            f.write("\n\n---\n\n")

    # ── 2. Extract vocabulary/glosses ──
    all_glosses = {}
    for msg in aelaki_msgs:
        content = msg.get("content", "")
        for word, meaning in extract_glosses(content):
            if word not in all_glosses:
                all_glosses[word] = []
            all_glosses[word].append({
                "meaning": meaning,
                "timestamp": msg.get("timestamp", ""),
                "context": content[:200],
            })

    with open(OUTPUT_DIR / "vocabulary_glosses.md", "w", encoding="utf-8") as f:
        f.write("# Vocabulary and Glosses from Discord\n\n")
        f.write("Word-meaning pairs extracted automatically from `word = meaning` patterns.\n\n")
        if all_glosses:
            f.write("| Word | Meaning(s) | Date |\n")
            f.write("|------|-----------|------|\n")
            for word, entries in sorted(all_glosses.items()):
                meanings = "; ".join(set(e["meaning"] for e in entries))
                date = entries[0]["timestamp"][:10] if entries[0]["timestamp"] else "?"
                f.write(f"| {word} | {meanings} | {date} |\n")
        else:
            f.write("No explicit `word = meaning` glosses found. "
                    "Check all_aelaki_messages.md for inline definitions.\n")

    # ── 3. Categorize by topic ──
    categories = {
        "morphology": [],
        "phonology": [],
        "syntax": [],
        "numerals": [],
        "gender_number": [],
        "verbs": [],
        "nouns": [],
        "worldbuilding": [],
        "writing_system": [],
        "other": [],
    }

    cat_keywords = {
        "morphology": ["morpholog", "template", "non-concatenative", "templatic",
                       "affix", "prefix", "suffix", "infix", "reduplicat"],
        "phonology": ["phonolog", "phonem", "consonant", "vowel", "phonotactic",
                       "allophone", "tone", "stress", "syllable", "abugida",
                       "writing system", "script"],
        "syntax": ["syntax", "word order", "sov", "vso", "osv", "clause",
                   "relative clause", "subordinat", "coordin"],
        "numerals": ["number", "numeral", "dozenal", "base-12", "base-60",
                     "sexagesimal", "cardinal", "ordinal", "partitive", "fraction"],
        "gender_number": ["gender", "feminine", "masculine", "inanimate", "child gender",
                          "singular", "plural", "collective", "zero number", "paucal"],
        "verbs": ["verb", "conjugat", "stative", "evidential", "tense", "aspect",
                  "mood", "gnomic", "inchoative", "cessative", "resumptive",
                  "hodiernal", "hesternal", "crastinal", "imperative",
                  "polypersonal", "converb", "zoduk", "dedik"],
        "nouns": ["noun", "case", "ergative", "accusative", "dative",
                  "instrumental", "possessive", "inalienable", "alienable",
                  "ki syllable", "ki-syllable", "ki clitic"],
        "worldbuilding": ["ringworld", "religion", "culture", "god", "goddess",
                          "creation", "myth", "society", "aelaki people"],
    }

    for msg in aelaki_msgs:
        content = msg.get("content", "").lower()
        categorized = False
        for cat, kws in cat_keywords.items():
            if any(kw in content for kw in kws):
                categories[cat].append(msg)
                categorized = True
                break  # First match wins
        if not categorized:
            categories["other"].append(msg)

    # Write per-category files
    for cat, msgs in categories.items():
        if not msgs:
            continue
        with open(OUTPUT_DIR / f"topic_{cat}.md", "w", encoding="utf-8") as f:
            f.write(f"# Discord Messages: {cat.replace('_', ' ').title()}\n\n")
            f.write(f"{len(msgs)} messages in this category.\n\n---\n\n")
            for msg in msgs:
                f.write(format_message(msg))
                f.write("\n\n---\n\n")

    # ── 4. Extract all unique Aelaki word forms ──
    all_forms = set()
    for msg in aelaki_msgs:
        content = msg.get("content", "")
        forms = extract_word_forms(content)
        all_forms.update(forms)

    with open(OUTPUT_DIR / "unique_word_forms.md", "w", encoding="utf-8") as f:
        f.write("# Unique Aelaki Word Forms from Discord\n\n")
        f.write(f"Words containing Aelaki-specific characters (ë, ü, ï, ə, æ, ŋ).\n")
        f.write(f"Total unique forms: {len(all_forms)}\n\n")
        for form in sorted(all_forms, key=str.lower):
            f.write(f"- {form}\n")

    # ── 5. Summary/index ──
    with open(OUTPUT_DIR / "INDEX.md", "w", encoding="utf-8") as f:
        f.write("# Discord Extract Index\n\n")
        f.write(f"Source: {len(messages)} messages from Discord exports\n")
        f.write(f"Aelaki-related: {len(aelaki_msgs)} messages\n\n")
        f.write("## Files\n\n")
        f.write("| File | Description | Count |\n")
        f.write("|------|-------------|-------|\n")
        f.write(f"| all_aelaki_messages.md | Every Aelaki message, chronological | {len(aelaki_msgs)} |\n")
        f.write(f"| vocabulary_glosses.md | Extracted word=meaning pairs | {len(all_glosses)} entries |\n")
        f.write(f"| unique_word_forms.md | All unique Aelaki word forms | {len(all_forms)} forms |\n")
        for cat, msgs in sorted(categories.items()):
            if msgs:
                f.write(f"| topic_{cat}.md | {cat.replace('_', ' ').title()} discussions | {len(msgs)} |\n")

    print(f"\nOutput written to {OUTPUT_DIR}/")
    print(f"  all_aelaki_messages.md  ({len(aelaki_msgs)} messages)")
    print(f"  vocabulary_glosses.md   ({len(all_glosses)} glosses)")
    print(f"  unique_word_forms.md    ({len(all_forms)} forms)")
    for cat, msgs in sorted(categories.items()):
        if msgs:
            print(f"  topic_{cat}.md          ({len(msgs)} messages)")
    print(f"  INDEX.md")


if __name__ == "__main__":
    main()
