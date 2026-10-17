"""Input compliance filter (data minimisation, GDPR Art. 5(1)(c) and Art. 9).

Two tiers:
  * BLOCKED  - direct identifiers or secrets. The message is rejected: it is never stored
               and never sent to any AI provider.
  * FLAGGED  - possible special-category data (Art. 9) or indirect identifiers. The message
               is processed but queued for human review.

Limits (documented in docs/fr/): pattern matching cannot recognise free-text names or
deliberately obfuscated data. It reduces risk; it does not eliminate it.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff"))


def _luhn(digits: str) -> bool:
    total, alt = 0, False
    for ch in reversed(digits):
        n = int(ch)
        if alt:
            n = n * 2 - 9 if n > 4 else n * 2
        total += n
        alt = not alt
    return total % 10 == 0


def _is_card(match: str) -> bool:
    digits = re.sub(r"\D", "", match)
    return 13 <= len(digits) <= 19 and _luhn(digits)


def _is_iban(match: str) -> bool:
    s = re.sub(r"\s", "", match).upper()
    if not 15 <= len(s) <= 34:
        return False
    rearranged = s[4:] + s[:4]
    return int("".join(str(int(c, 36)) for c in rearranged)) % 97 == 1


# (label, regex, optional validator)
BLOCKED_DETECTORS = [
    ("email address", re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"), None),
    ("obfuscated email address", re.compile(r"[\w.+\-]+\s*[\[(]\s*at\s*[\])]\s*[\w\-]+\s*[\[(]?\s*(?:dot|\.)\s*[\])]?\s*\w{2,}", re.I), None),
    ("phone number", re.compile(r"(?<!\d)0[1-9](?:[ .\-]?\d{2}){4}(?!\d)"), None),
    ("international phone number", re.compile(r"(?<![\w+])(?:\+|00)\d{1,3}[ .\-]?\(?\d{1,4}\)?(?:[ .\-]?\d{2,4}){2,4}(?!\d)"), None),
    ("national ID number (Moroccan CIN format)", re.compile(r"\b[A-Z]{1,2}\d{5,6}\b"), None),
    ("payment card number", re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"), _is_card),
    ("IBAN", re.compile(r"\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]{4}){2,7}(?:[ ]?[A-Z0-9]{1,3})?\b"), _is_iban),
    ("bank account number (RIB)", re.compile(r"(?<!\d)(?:\d[ -]?){24}(?!\d)"), None),
    ("French social security number", re.compile(r"\b[12]\s?\d{2}\s?(?:0[1-9]|1[0-2])\s?\d{2}\s?\d{3}\s?\d{3}\s?\d{2}\b"), None),
    ("credential or password", re.compile(r"\b(?:password|passwd|pwd|mot de passe|mdp)\s*(?:is|est|:|=)\s*\S+", re.I), None),
    ("API key or secret token", re.compile(r"\b(?:gsk_|sk-|ghp_|AKIA)[A-Za-z0-9_\-]{16,}"), None),
    ("GPS coordinates", re.compile(r"-?\d{1,3}\.\d{4,},\s*-?\d{1,3}\.\d{4,}"), None),
]

SENSITIVE_TERMS = {
    "health data": r"health|medical|illness|disease|diagnos\w+|disabilit\w+|sant[ée]|maladie|handicap\w*|diagnostic",
    "religious belief": r"religio\w+|muslim|christian|jewish|atheis\w+|croyance",
    "political opinion": r"political (?:opinion|view|affiliation)s?|opinions? politiques?|orientation politique",
    "sexual orientation": r"sexual orientation|sexuality|orientation sexuelle",
    "ethnic or racial origin": r"ethnic\w*|racial origin|origine ethnique|origine raciale",
    "criminal record": r"criminal record|convictions?|casier judiciaire|condamnation",
    "trade-union membership": r"trade[- ]union|syndicat\w*",
    "biometric or genetic data": r"biometric\w*|genetic\w*|fingerprint|g[ée]n[ée]tique|biom[ée]trique",
}
SENSITIVE_RE = {label: re.compile(rf"\b(?:{terms})\b", re.I) for label, terms in SENSITIVE_TERMS.items()}

INDIRECT_RE = {
    "physical address": re.compile(r"\b(?:\d{1,4}\s+)?(?:rue|avenue|bd|boulevard|street|st\.|road|quartier|hay)\s+\w+", re.I),
    "date of birth": re.compile(r"\b(?:born|n[ée]e?|date of birth|date de naissance|naissance)\b[^\n]{0,40}\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}", re.I),
}


@dataclass
class ComplianceResult:
    blocked: bool = False
    flagged: bool = False
    reason: str = ""
    categories: list[str] = field(default_factory=list)


def normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text).translate(ZERO_WIDTH)


def _matches(label: str, regex: re.Pattern, validator, text: str) -> bool:
    return any(validator is None or validator(m.group(0)) for m in regex.finditer(text))


def check_compliance(text: str) -> ComplianceResult:
    text = normalize(text)
    for label, regex, validator in BLOCKED_DETECTORS:
        if _matches(label, regex, validator, text):
            return ComplianceResult(blocked=True, reason=f"Personal data or secret detected: {label}.", categories=[label])
    categories = [label for label, rx in SENSITIVE_RE.items() if rx.search(text)]
    categories += [label for label, rx in INDIRECT_RE.items() if rx.search(text)]
    if categories:
        return ComplianceResult(
            flagged=True, categories=categories,
            reason="Possible sensitive content (" + ", ".join(categories) + "). Queued for human review.",
        )
    return ComplianceResult()


def redact(text: str) -> str:
    """Mask identifiers in AI output (a model may hallucinate or echo personal data)."""
    for label, regex, validator in BLOCKED_DETECTORS:
        text = regex.sub(lambda m, v=validator, l=label: f"[redacted: {l}]" if v is None or v(m.group(0)) else m.group(0), text)
    return text
