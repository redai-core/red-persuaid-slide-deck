"""
Deterministic copy repair so truncated or duplicate cells never ship.
Ported and adapted from quick-slide-be for PersuAId slide deck engine.
"""

from __future__ import annotations

import re
from typing import List
from engine.copy_guard import sanitize_generated_copy
from engine.text_budget import drop_truncated_tail

_HALF_WORD = re.compile(r"\b[a-z]{5,}(an|io|to|ti|ly|ed)\s*$", re.I)
_DANGLING = (" an", " to", " of", " and", " the", " a", " for", " with", " in", " on")
_CLAUSE_SPLIT = re.compile(r"(?<=[.;—–])\s+")


def finish_claim(text: str) -> str:
    """Drop sliced tails and dangling prepositions. Ensures proper terminal punctuation."""
    cleaned = sanitize_generated_copy(text)
    if not cleaned:
        return ""
    out = drop_truncated_tail(cleaned).rstrip(" ,;:—-")

    while out.lower().endswith(_DANGLING):
        out = out.rsplit(" ", 1)[0].rstrip(" ,;:—-")

    if _HALF_WORD.search(out) and " " in out:
        out = out.rsplit(" ", 1)[0].rstrip(" ,;:—-")

    if len(out) >= 20 and " " in out and out[-1] not in ".!?…":
        out = out + "."
    return out


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def uniquify_texts(values: List[str]) -> List[str]:
    """Ensures repeating cards or slot values have distinct text rather than exact repeats."""
    seen: dict[str, int] = {}
    out: List[str] = []
    for raw in values:
        text = finish_claim(raw)
        if not text:
            out.append("")
            continue
        key = _norm(text)
        if len(key) >= 40 and key in seen:
            seen[key] += 1
            words = text.split()
            if len(words) >= 8:
                # Provide a distinct clause/variant if duplicate
                slice_start = max(2, len(words) // 3)
                sub_text = " ".join(words[slice_start:])
                text = finish_claim(sub_text[0].upper() + sub_text[1:])
        seen[key] = seen.get(key, 0) + 1
        out.append(text)
    return out
