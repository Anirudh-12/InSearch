"""India eligibility classifier.

Uses deterministic keyword-based rules to classify whether an internship
listing is likely available for applicants based in India.

Returns one of: "likely", "unclear", "unlikely"
"""

import re

from app.models.internship import IndiaEligibility

# ---------------------------------------------------------------------------
# Keyword sets
# ---------------------------------------------------------------------------

# Signals that India applicants are explicitly welcomed
INDIA_POSITIVE_PATTERNS = [
    r"\bindia\b",
    r"\bindian\b",
    r"\bIN\b",  # ISO country code used in some listings
    r"\bapac\b",  # Asia-Pacific often includes India
    r"\basia[- ]pacific\b",
    r"\bsouth[- ]asia\b",
]

# Signals that the role is open worldwide / location-agnostic
WORLDWIDE_PATTERNS = [
    r"\bworldwide\b",
    r"\bglobal\b",
    r"\banywhere\b",
    r"\bfully remote\b",
    r"\b100%\s*remote\b",
    r"\bwork from anywhere\b",
    r"\blocation[- ]independent\b",
    r"\bno[- ]location[- ]restriction\b",
    r"\binternational\b",
    r"\bremote[,\s]*worldwide\b",
]

# Strong signals that the role is NOT available from India
INDIA_NEGATIVE_PATTERNS = [
    r"\bus[- ]+only\b",
    r"\bunited\s+states\s+only\b",
    r"\bunited\s+states\s+of\s+america\s+only\b",
    r"\bbased\s+in\s+the\s+us\b",
    r"\bbased\s+in\s+the\s+united\s+states\b",
    r"\bbased\s+in\s+north\s+america\b",
    r"\bmust\s+be\s+located\s+(in\s+)?(the\s+)?us\b",
    r"\bmust\s+be\s+located\s+(in\s+)?(the\s+)?united\s+states\b",
    r"\bmust\s+be\s+(a\s+)?us\s+(citizen|resident|national)\b",
    r"\bmust\s+be\s+(a\s+)?united\s+states\s+(citizen|resident|national)\b",
    r"\bnorth\s+america\s+only\b",
    r"\bcanada\s+only\b",
    r"\buk\s+only\b",
    r"\beurope\s+only\b",
    r"\beu\s+only\b",
    r"\bwork\s+authoriz(ation|ation)\s+required\b",
    r"\bus\s+work\s+authoriz(ation|ation)\b",
    r"\bunited\s+states\s+work\s+authoriz(ation|ation)\b",
    r"\bmust\s+have\s+(valid\s+)?us\s+work\s+authoriz(ation|e)\b",
    r"\bmust\s+have\s+(valid\s+)?united\s+states\s+work\s+authoriz(ation|e)\b",
    r"\bcitizenship\s+required\b",
    r"\bgreen\s+card\b",
    r"\bsecurity\s+clearance\b",
    r"\bclearance\s+required\b",
    r"\bremote\s+(within\s+)?(the\s+)?us(a)?\b",
    r"\bremote\s+(within\s+)?(the\s+)?united\s+states\b",
    r"\bremote\s+(within\s+)?north\s+america\b",
    r"\bremote\s+(within\s+)?europe\b",
    r"\bremote\s+(within\s+)?uk\b",
    r"\bno\s+international\s+(applicants|candidates)\b",
    r"\bdomestic\s+only\b",
    # "Remote – North America" style with em-dash or hyphen separator
    r"remote\s*[–\-]\s*north\s+america",
    r"remote\s*[–\-]\s*(us|usa|united\s+states)\b",
]


def _compile(patterns: list[str]) -> list[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


_POSITIVE = _compile(INDIA_POSITIVE_PATTERNS)
_WORLDWIDE = _compile(WORLDWIDE_PATTERNS)
_NEGATIVE = _compile(INDIA_NEGATIVE_PATTERNS)


def _text_matches(text: str, patterns: list[re.Pattern]) -> bool:
    return any(p.search(text) for p in patterns)


def classify(
    location: str | None = None,
    description: str | None = None,
    title: str | None = None,
) -> IndiaEligibility:
    """Classify India eligibility from available text fields.

    Priority:
    1. Explicit negative signals → unlikely
    2. Explicit India-positive signals → likely
    3. Worldwide / global signals → unclear (optimistic)
    4. Default → unclear
    """
    combined = " ".join(filter(None, [location or "", description or "", title or ""]))

    if _text_matches(combined, _NEGATIVE):
        return IndiaEligibility.UNLIKELY

    if _text_matches(combined, _POSITIVE):
        return IndiaEligibility.LIKELY

    if _text_matches(combined, _WORLDWIDE):
        return IndiaEligibility.UNCLEAR

    # No geo-restriction signals at all → assume unclear (not unlikely)
    return IndiaEligibility.UNCLEAR
