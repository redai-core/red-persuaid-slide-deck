"""
Character budgets derived from presentation shape geometry.
Ported and adapted from quick-slide-be for PersuAId slide deck engine.
"""

from __future__ import annotations

import re
from typing import Optional

EMU_PER_INCH = 914400
POINTS_PER_INCH = 72

# Fallback font sizes when shape inherits sizing from master layout
_DEFAULT_PT_BY_ROLE = {
    "title": 32,
    "subtitle": 20,
    "headline": 24,
    "kicker": 12,
    "body": 15,
    "stat": 48,
    "text": 15,
    "other": 15,
}

_AVG_GLYPH_WIDTH_EM = 0.52
_LINE_HEIGHT_EM = 1.2
_SAFETY = 0.74

_MIN_BUDGET = 12
_MAX_BUDGET = 800

_CUTOFF_PUNCT = re.compile(r"[\s,;:\-—–]+$")
_HALF_WORD_RE = re.compile(r"\b[a-z]{4,}(an|io|to|ti|ing|ed|ly)\s*$", re.I)


def default_font_size_pt(role: str) -> int:
    return _DEFAULT_PT_BY_ROLE.get(role.lower(), 15)


def estimate_char_budget(
    *,
    width_emu: Optional[int] = None,
    height_emu: Optional[int] = None,
    font_size_pt: Optional[int] = None,
    role: str = "text",
) -> Optional[int]:
    """
    Approximate how many characters fit in a physical container shape.
    Returns None if dimensions are missing or invalid.
    """
    if not width_emu or not height_emu or width_emu <= 0 or height_emu <= 0:
        return None

    if font_size_pt and font_size_pt > 0:
        size_pt = max(2, int(font_size_pt))
    else:
        size_pt = default_font_size_pt(role)

    width_pt = (width_emu / EMU_PER_INCH) * POINTS_PER_INCH
    height_pt = (height_emu / EMU_PER_INCH) * POINTS_PER_INCH

    chars_per_line = max(1, int(width_pt / (size_pt * _AVG_GLYPH_WIDTH_EM)))
    lines = max(1, int(height_pt / (size_pt * _LINE_HEIGHT_EM)))
    raw = chars_per_line * lines
    return max(_MIN_BUDGET, min(_MAX_BUDGET, int(raw * _SAFETY)))


def drop_truncated_tail(text: str) -> str:
    """Drops incomplete token fragments, half-words, or trailing punctuation."""
    out = (text or "").strip()
    out = _CUTOFF_PUNCT.sub("", out)
    return out


def trim_to_char_budget(text: str, max_chars: int) -> str:
    """
    Trims a text string to stay under max_chars without cutting words in half.
    Appends terminal punctuation if appropriate.
    """
    cleaned = (text or "").strip()
    if len(cleaned) <= max_chars:
        return cleaned

    # Find the last space before max_chars
    truncated = cleaned[:max_chars]
    last_space = truncated.rfind(" ")
    if last_space > int(max_chars * 0.6):
        truncated = truncated[:last_space]

    truncated = _CUTOFF_PUNCT.sub("", truncated)
    if len(truncated) >= 20 and truncated[-1] not in ".!?…":
        truncated += "."
    return truncated
