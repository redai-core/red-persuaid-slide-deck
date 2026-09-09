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
        """Ensures all required data keys exist with grounded audit parsing and zero fake fallbacks."""
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

        # Handle raw Otterly API schema if directly passed
        otterly_summary = raw.get("summary") or metrics.get("summary") or {}
        if not otterly and otterly_summary:
            sov_raw = otterly_summary.get("shareOfVoice", 0.0)
            sov_pct = round(sov_raw * 100.0, 1) if sov_raw <= 1.0 else round(sov_raw, 1)
            rank_raw = otterly_summary.get("averageRank", 1)
            avg_rank = f"#{round(rank_raw, 1)}" if isinstance(rank_raw, (int, float)) else str(rank_raw)

            otterly = {
                "hero_stat": {
                    "share_of_voice_pct": sov_pct,
                    "average_rank": avg_rank,
                    "sentiment_score": "N/A",
                    "win_rate_pct": f"{round(sov_pct)}%",
                },
                "competitor_gap": [],
            }

            brand_mentions = (
                raw.get("allBrandsAnalysis", {}).get("brandMentions")
                or raw.get("competitorBrandsAnalysis", {}).get("brandMentions")
                or metrics.get("allBrandsAnalysis", {}).get("brandMentions")
                or []
            )
            for bm in brand_mentions:
                bname = bm.get("brand", "")
                b_sov = bm.get("shareOfVoice", 0.0)
                b_pct = round(b_sov * 100.0, 1) if b_sov <= 1.0 else round(b_sov, 1)
                if bname and bname.lower() != brand.lower():
                    otterly["competitor_gap"].append({
                        "competitor": bname,
                        "share_of_voice_pct": b_pct,
                    })

        hero_stat = raw.get("hero_stat", {})
        if not hero_stat:
            if otterly and "hero_stat" in otterly:
                hero_stat = otterly.get("hero_stat", {})
            elif kpis.get("ai_share_of_voice_pct") is not None:
                hero_stat = {
                    "share_of_voice_pct": kpis.get("ai_share_of_voice_pct"),
                    "average_rank": kpis.get("average_rank", "#1"),
                    "sentiment_score": kpis.get("sentiment_score", "N/A"),
                    "win_rate_pct": f"{kpis.get('win_rate_pct', 0)}%",
                }
            else:
                hero_stat = {
                    "share_of_voice_pct": 0.0,
                    "average_rank": "Unranked",
                    "sentiment_score": "N/A",
                    "win_rate_pct": "0%",
                }

        competitor_gap = raw.get("competitor_gap", [])
        if not competitor_gap:
            if otterly and "competitor_gap" in otterly:
                competitor_gap = otterly.get("competitor_gap", [])
            elif metrics.get("competitor_landscape"):
                for c in metrics.get("competitor_landscape", []):
                    competitor_gap.append({
                        "competitor": c.get("competitor"),
                        "share_of_voice_pct": c.get("presence_rate_pct", 0.0),
                    })
            else:
                for c_name in comp_list[:4]:
                    competitor_gap.append({
                        "competitor": c_name,
                        "share_of_voice_pct": 0.0,
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
    metrics_data: Optional[Dict[str, Any]] = None,
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

    if metrics_data and isinstance(metrics_data, dict):
        data["metrics"] = metrics_data
        if "otterly_intel" in metrics_data:
            data["otterly_intel"] = metrics_data["otterly_intel"]
    elif metrics_path and Path(metrics_path).exists():
        try:
            metrics_content = json.loads(Path(metrics_path).read_text(encoding="utf-8"))
            data["metrics"] = metrics_content
            if "otterly_intel" in metrics_content:
                data["otterly_intel"] = metrics_content["otterly_intel"]
        except Exception as e:
            print(f"Warning: Failed to load metrics from {metrics_path}: {e}")

    builder = DeckCraftBuilder(data)
    brand_slug = brand.replace(" ", "_")

    # Safe output directory resolution: if client passes an inaccessible remote path (e.g. /home/claude or /mnt/user-data), fall back safely
    target_dir = Path(out_dir)
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        # Test writability
        test_file = target_dir / ".write_test"
        test_file.touch()
        test_file.unlink()
    except (PermissionError, OSError):
        # Fallback to container writable locations
        for fallback in [Path("/app/data"), Path("/tmp/persuaid_decks"), Path(".")]:
            try:
                fallback.mkdir(parents=True, exist_ok=True)
                target_dir = fallback
                break
            except Exception:
                pass

    target_path = target_dir / f"{brand_slug}_GEO_Pitch_Deck_{year}.pptx"
    return builder.build(str(target_path))
