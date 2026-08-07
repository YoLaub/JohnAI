import re

REMEMBER_PATTERN = re.compile(r"^(?:retiens|souviens[- ]toi|n'oublie pas)\s+(?:que\b\s*)?", re.IGNORECASE)
FORGET_PATTERN = re.compile(r"^(?:oublie|efface)\s+que\b\s*", re.IGNORECASE)


def extract_remember_fact(text: str) -> str | None:
    """Return the fact to memorize if `text` opens with a remember trigger phrase
    ("retiens que ...", "souviens-toi que ...", "n'oublie pas que ..."), else None."""
    stripped = text.strip()
    match = REMEMBER_PATTERN.match(stripped)
    if not match:
        return None
    fact = stripped[match.end():].strip()
    return fact or None


def extract_forget_query(text: str) -> str | None:
    """Return the search text to forget if `text` opens with "oublie que ..." /
    "efface que ...", else None. Requires the explicit "que" to avoid deleting
    memorized facts on a loosely-matched phrase."""
    stripped = text.strip()
    match = FORGET_PATTERN.match(stripped)
    if not match:
        return None
    query = stripped[match.end():].strip()
    return query or None
