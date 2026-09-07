#!/usr/bin/env python3
"""
PersuAId DeckCraft Presentation Builder
Compiles the complete 21-slide Redcomm executive pitch deck from brand parameters
and audit metrics (from Otterly.ai or Apify search pipelines).
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from pptx import Presentation

from engine.deckcraft.tokens import CANVAS_WIDTH, CANVAS_HEIGHT
from engine.deckcraft.slides import ALL_SLIDE_BUILDERS


class DeckCraftBuilder:
    def __init__(self, brand_data: Dict[str, Any]):
        self.data = self._normalize_data(brand_data)
        self.prs = Presentation()
        self.prs.slide_width = CANVAS_WIDTH
        self.prs.slide_height = CANVAS_HEIGHT
        self.blank_layout = self.prs.slide_layouts[6]

    def _normalize_data(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures all required data keys exist with sensible category defaults."""
        brand = raw.get("brand", "Your Brand")
        category = raw.get("category", "your category")
        competitors = raw.get("competitors", "Competitor A, Competitor B, Competitor C")

        if isinstance(competitors, str):
            comp_list = [c.strip() for c in competitors.split(",") if c.strip()]
        else:
            comp_list = list(competitors)

        # Merge metrics if nested
        metrics = raw.get("metrics", {})
        otterly = raw.get("otterly_intel", {}) or metrics.get("otterly_intel", {})
        kpis = metrics.get("kpis", {})

        hero_stat = raw.get("hero_stat", {})
        if not hero_stat:
            if otterly:
                hero_stat = otterly.get("hero_stat", {})
            else:
                hero_stat = {
                    "share_of_voice_pct": kpis.get("ai_share_of_voice_pct", 9.3),
                    "average_rank": kpis.get("average_rank", "#4"),
                    "sentiment_score": kpis.get("sentiment_score", "63/100"),
                    "win_rate_pct": f"{kpis.get('win_rate_pct', 18)}%",
                }

        competitor_gap = raw.get("competitor_gap", [])
        if not competitor_gap:
            if otterly:
                competitor_gap = otterly.get("competitor_gap", [])
            elif metrics.get("competitor_landscape"):
                for c in metrics.get("competitor_landscape", []):
                    competitor_gap.append({
                        "competitor": c.get("competitor"),
                        "share_of_voice_pct": c.get("presence_rate_pct", 20.0),
                    })
            if not competitor_gap:
                for i, c_name in enumerate(comp_list[:4]):
                    competitor_gap.append({
                        "competitor": c_name,
                        "share_of_voice_pct": round(30.0 - (i * 4.5), 1),
                    })

        return {
            "brand": brand,
            "domain": raw.get("domain", f"{brand.lower().replace(' ', '')}.com"),
            "category": category,
            "competitors": comp_list,
            "geo": raw.get("geo", "Indonesia"),
            "year": raw.get("year", 2026),
            "hero_stat": hero_stat,
            "competitor_gap": competitor_gap,
            "otterly_intel": otterly,
            "metrics": metrics,
        }

    def build(self, output_path: Optional[str] = None) -> Path:
        """Constructs all 21 slides and saves the PowerPoint presentation."""
        for builder_fn in ALL_SLIDE_BUILDERS:
            slide = self.prs.slides.add_slide(self.blank_layout)
            builder_fn(slide, self.data)

        if not output_path:
            brand_slug = self.data["brand"].replace(" ", "_")
            out_file = Path(f"{brand_slug}_GEO_Pitch_Deck_{self.data['year']}.pptx")
        else:
            out_file = Path(output_path)

        out_file.parent.mkdir(parents=True, exist_ok=True)
        self.prs.save(str(out_file))
        return out_file


def compile_deck(
    brand: str,
    category: str,
    competitors: str = "Competitor A, Competitor B",
    domain: Optional[str] = None,
    metrics_path: Optional[str] = None,
    out_dir: str = ".",
    year: int = 2026,
) -> Path:
    """Convenience compilation entry point."""
    data = {
        "brand": brand,
        "category": category,
        "competitors": competitors,
        "domain": domain,
        "year": year,
    }

    if metrics_path and Path(metrics_path).exists():
        try:
            metrics_content = json.loads(Path(metrics_path).read_text(encoding="utf-8"))
            data["metrics"] = metrics_content
            if "otterly_intel" in metrics_content:
                data["otterly_intel"] = metrics_content["otterly_intel"]
        except Exception as e:
            print(f"Warning: Failed to load metrics from {metrics_path}: {e}")

    builder = DeckCraftBuilder(data)
    brand_slug = brand.replace(" ", "_")
    target_path = Path(out_dir) / f"{brand_slug}_GEO_Pitch_Deck_{year}.pptx"
    return builder.build(str(target_path))
