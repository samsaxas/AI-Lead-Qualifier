"""Simple keyword-rule baseline: the thing the LLM has to beat.

Deliberately generic. It was written once and NOT tuned on the test set.
"""
import re

COLD_PATTERNS = [
    r"just browsing", r"not interested", r"remove my number", r"\bhiring\b", r"\bvacancy\b",
    r"\bjob\b", r"\bseo\b", r"digital marketing", r"college project", r"\bprize\b",
    r"\bignore\b", r"\bplumber\b", r"electricity", r"weather", r"lead lists?",
    r"couple of years", r"\d-\d years", r"no rush",
]
HOT_PATTERNS = [
    r"site visit", r"\bvisit (this|tomorrow|today|on)\b", r"come tomorrow", r"call me (today|now)",
    r"\bbook\b", r"\bbooking\b", r"\btoken\b", r"down ?payment", r"pre-?approved", r"sanctioned",
    r"ready to (buy|book|pay)", r"\bimmediate(ly)?\b", r"this (week|weekend|month)",
    r"within \d+ (days|weeks)", r"\bcheque\b", r"show me flats tomorrow",
]


def classify(message: str) -> dict:
    text = message.lower()
    if any(re.search(p, text) for p in COLD_PATTERNS):
        return {"intent": "cold", "score": 10, "reason": "matched a cold keyword rule"}
    if any(re.search(p, text) for p in HOT_PATTERNS):
        return {"intent": "hot", "score": 85, "reason": "matched a hot keyword rule"}
    return {"intent": "warm", "score": 50, "reason": "no rule matched (default)"}
