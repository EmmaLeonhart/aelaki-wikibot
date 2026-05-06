"""Regenerate the 60 sexagenary cycle pages with lore-fitting content.

The previous content was scraped from real-world Wikipedia and was full of
calendar tables and Japanese/Chinese historical events that don't belong in
the Aelaki ringworld setting. This script replaces each page with a short,
lore-fitting entry that:

  * frames the entry as one of the 60 nodes of the Divine 60 cycle
  * preserves the heavenly-stem + earthly-branch identity
  * keeps the wikidata Q-number that was already on the page
  * adds prev/next navigation around the cycle
  * removes calendar tables, real-world events, and red links to Earth topics

Run from the repository root:

    python wiki-scripts/regenerate_sexagenary_pages.py
"""
from __future__ import annotations

import re
from pathlib import Path

GRAMMAR_DIR = Path(__file__).resolve().parent.parent / "grammar"

# 10 Heavenly Stems: char, romaji (Kunyomi+stem), polarity ("Yang"/"Yin"), element
STEMS = [
    ("甲", "Kinoe",      "Yang", "Wood"),
    ("乙", "Kinoto",     "Yin",  "Wood"),
    ("丙", "Hinoe",      "Yang", "Fire"),
    ("丁", "Hinoto",     "Yin",  "Fire"),
    ("戊", "Tsuchinoe",  "Yang", "Earth"),
    ("己", "Tsuchinoto", "Yin",  "Earth"),
    ("庚", "Kanoe",      "Yang", "Metal"),
    ("辛", "Kanoto",     "Yin",  "Metal"),
    ("壬", "Mizunoe",    "Yang", "Water"),
    ("癸", "Mizunoto",   "Yin",  "Water"),
]

# 12 Earthly Branches: char, romaji, animal, polarity, element
BRANCHES = [
    ("子", "Ne",       "Rat",     "Yang", "Water"),
    ("丑", "Ushi",     "Ox",      "Yin",  "Earth"),
    ("寅", "Tora",     "Tiger",   "Yang", "Wood"),
    ("卯", "U",        "Rabbit",  "Yin",  "Wood"),
    ("辰", "Tatsu",    "Dragon",  "Yang", "Earth"),
    ("巳", "Mi",       "Snake",   "Yin",  "Fire"),
    ("午", "Uma",      "Horse",   "Yang", "Fire"),
    ("未", "Hitsuji",  "Goat",    "Yin",  "Earth"),
    ("申", "Saru",     "Monkey",  "Yang", "Metal"),
    ("酉", "Tori",     "Rooster", "Yin",  "Metal"),
    ("戌", "Inu",      "Dog",     "Yang", "Earth"),
    ("亥", "I",        "Pig",     "Yin",  "Water"),
]

# Aelaki cosmological mappings (from The_divine_60.wiki)
POLARITY_BODY = {"Yang": "Gaia", "Yin": "Luna"}  # celestial body of the Divine 60
ELEMENT_SEASON = {
    "Metal": "occultation",
    "Water": "winter",
    "Wood":  "spring",
    "Fire":  "summer",
    "Earth": "autumn",
}

# Wuxing relations: "<src> -> <dst>" => "generates" (sheng) or "overcomes" (ke)
GENERATES = {"Wood": "Fire", "Fire": "Earth", "Earth": "Metal", "Metal": "Water", "Water": "Wood"}
OVERCOMES = {"Wood": "Earth", "Earth": "Water", "Water": "Fire", "Fire": "Metal", "Metal": "Wood"}


def wuxing_relation(stem_el: str, branch_el: str) -> str:
    if stem_el == branch_el:
        return f"both stem and branch share the {stem_el.lower()} element, doubling its weight in this node."
    if GENERATES.get(stem_el) == branch_el:
        return f"the stem's {stem_el.lower()} generates the branch's {branch_el.lower()}, a relationship of nourishment."
    if GENERATES.get(branch_el) == stem_el:
        return f"the branch's {branch_el.lower()} generates the stem's {stem_el.lower()}, feeding the heavens from below."
    if OVERCOMES.get(stem_el) == branch_el:
        return f"the stem's {stem_el.lower()} overcomes the branch's {branch_el.lower()}, a relationship of restraint."
    if OVERCOMES.get(branch_el) == stem_el:
        return f"the branch's {branch_el.lower()} overcomes the stem's {stem_el.lower()}, the lower restraining the high."
    return f"the {stem_el.lower()} of the stem and {branch_el.lower()} of the branch stand in balanced tension."


def build_cycle() -> list[dict]:
    """Return a list of 60 dicts, one per cycle position (1-60)."""
    cycle = []
    for n in range(60):
        stem = STEMS[n % 10]
        branch = BRANCHES[n % 12]
        page_name = f"{stem[2]} {stem[3]} {branch[2]}"  # e.g. "Yang Wood Rat"
        cycle.append({
            "n": n + 1,
            "page": page_name,
            "stem_char": stem[0],
            "stem_romaji": stem[1],
            "stem_pol": stem[2],
            "stem_el": stem[3],
            "branch_char": branch[0],
            "branch_romaji": branch[1],
            "branch_animal": branch[2],
            "branch_pol": branch[3],
            "branch_el": branch[4],
        })
    return cycle


def extract_qid(text: str) -> str | None:
    m = re.search(r"\{\{wikidata link\|(Q\d+)\}\}", text)
    return m.group(1) if m else None


def render_page(entry: dict, prev_entry: dict, next_entry: dict, qid: str | None) -> str:
    page = entry["page"]
    stem_full = f"{entry['stem_char']} {entry['stem_romaji']}"
    branch_full = f"{entry['branch_char']} {entry['branch_romaji']}"
    body = POLARITY_BODY[entry["stem_pol"]]
    season = ELEMENT_SEASON[entry["stem_el"]]
    relation = wuxing_relation(entry["stem_el"], entry["branch_el"])

    parts = []
    parts.append(
        f"'''{page}''' is the {ordinal(entry['n'])} of the sixty nodes of the [[Sexagenary cycle|Divine Sixty]], "
        f"the great cycle that the [[Heavenly stems|heavenly stems]] and [[Earthly Branches|earthly branches]] "
        f"trace across the ringworld's calendar of [[Gaia]] and [[Luna]]."
    )
    parts.append(
        f"Its stem is {stem_full} ({entry['stem_pol'].lower()} {entry['stem_el'].lower()}, "
        f"the {body.lower()}-aligned face of {season}), and its branch is {branch_full}, "
        f"the [[{entry['branch_animal']} (zodiac)|{entry['branch_animal']}]] hour. "
        f"Within the [[Wuxing]] reading of the node, {relation}"
    )
    parts.append(
        f"On the [[The divine 60|Divine Sixty]] lattice this position falls between "
        f"[[{prev_entry['page']}]] (node {prev_entry['n']}) and [[{next_entry['page']}]] (node {next_entry['n']})."
    )

    text = "\n\n".join(parts) + "\n"

    text += "\n== Stem and branch ==\n"
    text += (
        f"* '''Stem:''' [[{entry['stem_romaji']} ({entry['stem_char']})]] — {entry['stem_pol'].lower()} {entry['stem_el'].lower()}\n"
        f"* '''Branch:''' [[{entry['branch_animal']} (zodiac)|{entry['branch_animal']} ({entry['branch_char']})]] — {entry['branch_pol'].lower()} {entry['branch_el'].lower()}\n"
        f"* '''Celestial body:''' [[{body}]]\n"
        f"* '''Element-season:''' {season}\n"
    )

    text += "\n== See also ==\n"
    text += (
        "* [[The divine 60]]\n"
        "* [[Sexagenary cycle]]\n"
        "* [[Heavenly stems]]\n"
        "* [[Earthly Branches]]\n"
        f"* [[{prev_entry['page']}]] — preceding node\n"
        f"* [[{next_entry['page']}]] — following node\n"
    )

    text += "\n"
    if qid:
        text += "{{wikidata link|" + qid + "}}\n"
    text += "[[Category:Sexagenary cycle]]\n"
    text += "[[Category:Sexagenary cycle members]]\n"
    text += "[[Category:Ringworld]]\n"
    text += "[[Category:Git synced pages]]\n"

    return text


def ordinal(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        return f"{n}th"
    return f"{n}{ {1:'st', 2:'nd', 3:'rd'}.get(n % 10, 'th') }"


def main() -> None:
    cycle = build_cycle()
    by_name = {e["page"]: e for e in cycle}
    written = 0
    skipped = []
    for i, entry in enumerate(cycle):
        prev_entry = cycle[(i - 1) % 60]
        next_entry = cycle[(i + 1) % 60]
        path = GRAMMAR_DIR / (entry["page"].replace(" ", "_") + ".wiki")
        if not path.exists():
            skipped.append(entry["page"])
            continue
        old_text = path.read_text(encoding="utf-8")
        qid = extract_qid(old_text)
        new_text = render_page(entry, prev_entry, next_entry, qid)
        path.write_text(new_text, encoding="utf-8")
        written += 1
    print(f"Rewrote {written} sexagenary pages.")
    if skipped:
        print(f"Skipped {len(skipped)} (file not found): {skipped}")


if __name__ == "__main__":
    main()
