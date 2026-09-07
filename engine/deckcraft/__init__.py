#!/usr/bin/env python3
"""
PersuAId DeckCraft Presentation Generation Engine
A first-principles, pure-code declarative PowerPoint compiler.
"""

from engine.deckcraft.builder import DeckCraftBuilder, compile_deck
from engine.deckcraft.tokens import (
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
    COLOR_OBSIDIAN,
    COLOR_NAVY,
    COLOR_CYAN,
    COLOR_WHITE,
    COLOR_MUTED_SLATE,
)

__all__ = [
    "DeckCraftBuilder",
    "compile_deck",
    "CANVAS_WIDTH",
    "CANVAS_HEIGHT",
    "COLOR_OBSIDIAN",
    "COLOR_NAVY",
    "COLOR_CYAN",
    "COLOR_WHITE",
    "COLOR_MUTED_SLATE",
]
