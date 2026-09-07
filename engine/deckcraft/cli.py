#!/usr/bin/env python3
"""
PersuAId DeckCraft Command-Line Interface
Generates a complete 21-slide Redcomm executive GEO presentation deck directly from CLI.
"""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.deckcraft.builder import compile_deck


def main():
    parser = argparse.ArgumentParser(description="PersuAId DeckCraft Executive Presentation Generator")
    parser.add_argument("--brand", "-b", required=True, help="Target client brand name")
    parser.add_argument("--category", "-c", required=True, help="Product category or industry")
    parser.add_argument("--competitors", "-comp", default="Competitor A, Competitor B, Competitor C", help="Comma-separated competitors")
    parser.add_argument("--domain", "-d", default=None, help="Official client domain")
    parser.add_argument("--metrics", "-m", default=None, help="Path to metrics.json from audit pipeline")
    parser.add_argument("--out-dir", "-o", default=".", help="Directory to save generated presentation")
    parser.add_argument("--year", "-y", type=int, default=2026, help="Target year")
    args = parser.parse_args()

    print(f"\n🎨 PERSUAID DECKCRAFT COMPILER")
    print(f"==================================================")
    print(f"   Brand:        {args.brand}")
    print(f"   Category:     {args.category}")
    print(f"   Competitors:  {args.competitors}")
    print(f"   Domain:       {args.domain or 'auto'}")
    print(f"   Metrics:      {args.metrics or 'default models'}")
    print(f"   Output Dir:   {args.out_dir}")
    print(f"==================================================\n")

    print(f"[*] Compiling full 21-slide executive presentation deck...")
    out_file = compile_deck(
        brand=args.brand,
        category=args.category,
        competitors=args.competitors,
        domain=args.domain,
        metrics_path=args.metrics,
        out_dir=args.out_dir,
        year=args.year,
    )

    print(f"[✓] Successfully compiled: {out_file.resolve()}")
    print(f"    - Slides: 21 (True 16:9 Widescreen 20\" x 11.25\")")
    print(f"    - Theme: Redcomm Obsidian & Electric Cyan (#3EC0C0)")
    print(f"    - Native: 100% editable OpenXML shapes\n")


if __name__ == "__main__":
    main()
