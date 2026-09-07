#!/usr/bin/env python3
"""
PersuAId DeckCraft Design Tokens & Geometry
Defines the exact signature Redcomm Indonesia executive aesthetic:
Obsidian Black (#000000), Midnight Navy (#031E45), Electric Cyan (#3EC0C0),
and standard 20" x 11.25" true 16:9 widescreen canvas geometry.
"""

from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

# ==============================================================================
# Canvas Geometry (True 16:9 Widescreen)
# ==============================================================================
CANVAS_WIDTH = Inches(20.0)
CANVAS_HEIGHT = Inches(11.25)

MARGIN_X = Inches(1.1)
MARGIN_Y = Inches(0.75)
CONTENT_WIDTH = CANVAS_WIDTH - (MARGIN_X * 2)  # 17.8 inches
FOOTER_Y = Inches(10.4)

# ==============================================================================
# Signature Redcomm Palette
# ==============================================================================
COLOR_OBSIDIAN = RGBColor(0, 0, 0)          # Primary slide background (#000000)
COLOR_NAVY = RGBColor(3, 30, 69)           # Midnight Navy surface (#031E45)
COLOR_CYAN = RGBColor(62, 192, 192)        # Electric Cyan accent (#3EC0C0)
COLOR_CYAN_DEEP = RGBColor(56, 166, 166)   # Deep Cyan (#38A6A6)
COLOR_CARD_SLATE = RGBColor(13, 17, 23)    # Translucent card container (#0D1117)
COLOR_CARD_BORDER = RGBColor(26, 47, 74)   # Card boundary stroke (#1A2F4A)
COLOR_CARD_MINT = RGBColor(232, 248, 248)  # Pale mint container (#E8F8F8)

COLOR_WHITE = RGBColor(255, 255, 255)      # Primary text (#FFFFFF)
COLOR_OFF_WHITE = RGBColor(249, 249, 249)  # Soft text (#F9F9F9)
COLOR_COOL_GRAY = RGBColor(232, 238, 244)  # Muted body text (#E8EEF4)
COLOR_MUTED_SLATE = RGBColor(139, 168, 200)# Subtitle text (#8BA8C8)
COLOR_DARK_TEXT = RGBColor(3, 30, 69)      # High-contrast dark navy for Cyan banners
COLOR_AMBER_WARN = RGBColor(245, 158, 11)  # Amber warning badge (#F59E0B)

# ==============================================================================
# Typography System
# ==============================================================================
FONT_PRIMARY = "Arial"
FONT_BACKUP = "Helvetica"


SIZE_COVER_TITLE = Pt(56)
SIZE_COVER_SUBTITLE = Pt(20)
SIZE_SECTION_TITLE = Pt(48)
SIZE_ACTION_TITLE = Pt(28)
SIZE_KICKER = Pt(13)
SIZE_HERO_STAT = Pt(64)
SIZE_CARD_HEADER = Pt(18)
SIZE_BODY = Pt(15)
SIZE_BODY_SM = Pt(13)
SIZE_FOOTER = Pt(11)
