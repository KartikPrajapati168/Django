# restaurants/utils.py
import re

CUISINES = [
    'Spots', 'Legendary', 'Buffets', 'Gujarati Thali',
    'Asian Restaurant', 'Rollins With Dosas'
]
CITIES = ['Ahmedabad']


def extract_from_text(text: str, options: list[str]) -> str | None:
    """
    1. Try to match the *last comma-separated token* exactly.
    2. If that fails, match the first option that appears anywhere
       (case-insensitive).
    """
    if not text:
        return None

    # 1) last token rule
    last_token = text.split(',')[-1].strip().lower()
    for opt in options:
        if opt.lower() == last_token:
            return opt

    # 2) fallback: contains
    lowered = text.lower()
    for opt in options:
        if opt.lower() in lowered:
            return opt
    return None
