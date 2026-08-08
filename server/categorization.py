import re

CATEGORIZE_PATTERN = re.compile(
    r"^(?:mets|classe|range|cat[ée]gorise)\s+"
    r"(?:ça|ca|cette (?:note|pens[ée]e|r[ée]flexion))\s+"
    r"dans\s+(?:la\s+)?(?:cat[ée]gorie\s+)?",
    re.IGNORECASE,
)


def extract_categorize_command(text: str) -> str | None:
    """Return the target category if `text` opens with a categorize trigger
    phrase ("mets ça dans ...", "classe cette note dans ...", "range ça dans
    la catégorie ...", "catégorise ça dans ..."), else None."""
    stripped = text.strip()
    match = CATEGORIZE_PATTERN.match(stripped)
    if not match:
        return None
    category = stripped[match.end():].strip()
    return category or None
