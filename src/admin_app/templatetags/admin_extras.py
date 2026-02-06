# Template tags for admin app
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Common country name -> ISO 3166-1 alpha-2
COUNTRY_CODE_MAP = {
    "norway": "NO",
    "norge": "NO",
    "sweden": "SE",
    "sverige": "SE",
    "denmark": "DK",
    "danmark": "DK",
    "finland": "FI",
    "germany": "DE",
    "tyskland": "DE",
    "united kingdom": "GB",
    "uk": "GB",
    "united states": "US",
    "usa": "US",
    "netherlands": "NL",
    "nederland": "NL",
    "france": "FR",
    "spain": "ES",
    "italy": "IT",
    "iceland": "IS",
    "island": "IS",
    "poland": "PL",
    "belgium": "BE",
    "austria": "AT",
    "switzerland": "CH",
    "portugal": "PT",
}


def _code_to_flag(code: str) -> str:
    """Convert 2-letter ISO country code to flag emoji."""
    if not code or len(code) != 2:
        return ""
    code = code.upper()
    # Regional indicator symbols: A = U+1F1E6, so offset from 'A' (65)
    return chr(0x1F1E6 + ord(code[0]) - 65) + chr(0x1F1E6 + ord(code[1]) - 65)


@register.filter
def country_flag(value):
    """Return flag emoji for country name or 2-letter code. Safe for display."""
    if not value:
        return ""
    s = (value or "").strip()
    if len(s) == 2 and s.upper().isalpha():
        return mark_safe(_code_to_flag(s))
    key = s.lower()
    code = COUNTRY_CODE_MAP.get(key)
    if code:
        return mark_safe(_code_to_flag(code))
    # Try first two letters of single word (e.g. "Norway" -> NO)
    if len(s) >= 2 and " " not in s:
        return mark_safe(_code_to_flag(s[:2].upper()))
    return ""
