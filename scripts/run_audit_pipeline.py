#!/usr/bin/env python3
"""
PersuAId All-In-One GEO Audit Pipeline Runner
Executes the complete Step 1.5 audit loop in a single command:
1. Dual-Platform AI Reverse-Prompting across ChatGPT and Gemini (Cloud Apify or Local Camoufox)
2. Exports [Brand]_AI_Search_Journey_Prompts.csv (Itemized) and [Brand]_AI_Search_Journey_Matrix.csv (Grid)
3. Executes live headless batch audit sweep across AI platforms (ChatGPT & Gemini)
4. Aggregates quantitative metrics into metrics.json and prints executive summary

Usage:
  python3 scripts/run_audit_pipeline.py \
    --brand "Electrum" \
    --category "motor listrik" \
    --competitors "Alva,Gesits,Polytron" \
    --geo "Indonesia" \
    --out-dir "."
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.format_queries import (
    reverse_prompt_queries,
    generate_platform_journey_queries,
    sample_audit_queries,
    export_itemized_csv,
    export_matrix_csv,
)
from scripts.aggregate_metrics import aggregate_audit_results
from engine.credentials import resolve_apify_token, has_apify_token, resolve_otterly_key, has_otterly_key
from engine.otterly_client import OtterlyClient


def run_pipeline(
    brand: str,
    category: str,
    competitors: str,
    geo: str = "Indonesia",
    domain: str = None,
    platform: str = "chatgpt,gemini",
    account: str = None,
    out_dir: str = ".",
    headless: bool = True,
    year: int = 2026,
    reverse_prompt: bool = True,
    provider: str = "auto",
    apify_token: str = None,
    max_per_stage: int = 5,
    samples_per_stage: int = 2,
    audit_all: bool = False,
    otterly_key: str = None,
    no_otterly: bool = False,
    generate_deck: bool = False,
):

    out_path = Path(out_dir).resolve()
    out_path.mkdir(parents=True, exist_ok=True)

    active_token = resolve_apify_token(apify_token)
    active_otterly_key = resolve_otterly_key(otterly_key)

    brand_slug = brand.strip().replace(" ", "_")
    csv_itemized = out_path / f"{brand_slug}_AI_Search_Journey_Prompts.csv"
    csv_matrix = out_path / f"{brand_slug}_AI_Search_Journey_Matrix.csv"
    queries_json = out_path / "queries.json"
    results_json = out_path / "results.json"
    metrics_json = out_path / "metrics.json"

    comp_list = [c.strip() for c in competitors.split(",") if c.strip()]
    platforms_list = [p.strip().lower() for p in platform.split(",") if p.strip()]

    # -------------------------------------------------------------
    # Step 0: Otterly.ai Pre-Configured Pitch Intelligence Check
    # -------------------------------------------------------------
    otterly_intel = None
    if not no_otterly and (active_otterly_key or has_otterly_key()):
        try:
            otterly_client = OtterlyClient(api_key=active_otterly_key)
            print(f"[*] Checking Otterly API for pre-configured report for '{brand}'...")
            otterly_intel = otterly_client.fetch_pitch_intel(brand, domain)
            if otterly_intel:
                print(f"[✓] Ingested Otterly pitch intelligence for '{brand}' (SoV: {otterly_intel['hero_stat']['share_of_voice_pct']}%)")
                intel_path = out_path / "otterly_intel.json"
                intel_path.write_text(json.dumps(otterly_intel, indent=2, ensure_ascii=False), encoding="utf-8")
            else:
                print(f"[Otterly API: No pre-configured report found for '{brand}'. Preserving credits and proceeding with standard live Apify audit.]")
        except Exception as e:
            print(f"[Otterly API Notice: {e}. Proceeding with standard live Apify audit.]")

    print(f"\n========================================================")
    print(f"🚀 PERSUAID ALL-IN-ONE GEO AUDIT PIPELINE")
    print(f"========================================================")
    print(f"   Brand:             {brand}")
    if domain:
        print(f"   Domain:            {domain}")
    print(f"   Category:          {category}")
    print(f"   Competitors:       {', '.join(comp_list)}")
    print(f"   Geography:         {geo} ({year})")
    print(f"   Platforms:         {', '.join(p.upper() for p in platforms_list)}")
    print(f"   Max Qs / Stage:    {max_per_stage}")
    print(f"   Audit Mode:        {'ALL Prompts' if audit_all else f'Sample ({samples_per_stage}/stage)'}")
    print(f"   Engine Mode:       {'Headless (Unauthenticated)' if headless else 'Headed'}")
    print(f"   Provider:          {provider.upper()} (Token: {'AUTHENTICATED' if active_token else 'NOT CONFIGURED'})")
    print(f"   Otterly Intel:     {'ATTACHED' if otterly_intel else ('AVAILABLE (No Report)' if active_otterly_key else 'NOT CONFIGURED')}")
    print(f"   Output Dir:        {out_path}")
    print(f"========================================================\n")


    # -------------------------------------------------------------
    # Step 1: Reverse-Prompting & CSV Deliverables Generation
    # -------------------------------------------------------------
    print(f"🔍 [1/3] Generating platform-separated 5-stage search journey...")
    if reverse_prompt:
        queries = reverse_prompt_queries(
            brand=brand,
            category=category,
            competitors=comp_list,
            geo=geo,
            platforms=platforms_list,
            account=account,
            headless=headless,
            year=year,
            max_per_stage=max_per_stage,
        )
    else:
        print("   ℹ��� Reverse prompting skipped by flag. Using template generator.")
        queries = generate_platform_journey_queries(
            brand=brand,
            category=category,
            competitors=comp_list,
            geo=geo,
            year=year,
        )

    sampled_batch = sample_audit_queries(
        queries, 
        samples_per_stage=samples_per_stage,
        audit_all=audit_all
    )

    export_itemized_csv(queries, str(csv_itemized))
    print(f"   ✓ Exported itemized CSV ({len(queries)} queries) -> {csv_itemized}")

    export_matrix_csv(queries, str(csv_matrix))
    print(f"   ✓ Exported matrix grid CSV -> {csv_matrix}")

    queries_json.write_text(json.dumps(sampled_batch, indent=2, ensure_ascii=False))
    print(f"   ✓ Prepared {len(sampled_batch)} batch audit queries -> {queries_json}\n")

    export_matrix_csv(queries, str(csv_matrix))
    print(f"   ✓ Exported matrix grid CSV -> {csv_matrix}")

    queries_json.write_text(json.dumps(sampled_batch, indent=2, ensure_ascii=False))
    print(f"   ✓ Prepared {len(sampled_batch)} sampled batch audit queries -> {queries_json}\n")

    # -------------------------------------------------------------
    # Step 2: Execute Live Multi-Platform Batch Audit (Concurrent)
    # -------------------------------------------------------------
    import concurrent.futures
    all_results = []
    has_apify = provider in ["auto", "apify"]

    def audit_single_platform(plat: str) -> List[dict]:
        plat_items = [item for item in sampled_batch if item.get("platform", "").lower() == plat.lower()]
        if not plat_items:
            plat_items = sampled_batch

        print(f"🌐 [2/3] Executing live batch audit on {plat.upper()} ({len(plat_items)} queries)...")
        plat_results_file = out_path / f"results_{plat}.json"
        plat_results = []

        # 1. Try Apify Cloud Batch Execution
        if has_apify:
            try:
                from engine.apify_client import ApifyClient
                ap_client = ApifyClient()
                print(f"   ☁️ Running batch audit via Apify Cloud ({plat.upper()})...")
                query_strings = [item.get("q") for item in plat_items]
                audit_objs = ap_client.batch_audit(platform=plat, queries=query_strings, brand_name=brand)
                
                for idx, res in enumerate(audit_objs):
                    res_dict = res.model_dump(mode="json")
                    if idx < len(plat_items):
                        res_dict["stage"] = plat_items[idx].get("stage")
                        res_dict["intent"] = plat_items[idx].get("intent")
                    plat_results.append(res_dict)
                    status = "✓ CITED" if res.brand_cited else "✗ NOT CITED"
                    print(f"        [{plat.upper()} {idx+1}/{len(audit_objs)}] {status} | {len(res.citations)} citations | {res.duration_seconds:.1f}s")

                plat_results_file.write_text(json.dumps(plat_results, indent=2, ensure_ascii=False))
                print(f"   ✓ Saved {plat.upper()} audit results -> {plat_results_file}\n")
                return plat_results
            except Exception as e:
                print(f"   ⚠️ Apify batch audit on {plat.upper()} failed: {e}. Falling back to local Camoufox.")

        # 2. Try Local Camoufox Driver
        try:
            from engine.session_manager import SessionManager
            from engine.cli import get_driver
            mgr = SessionManager()
            driver = get_driver(plat, mgr)
            for i, item in enumerate(plat_items, start=1):
                q = item.get("q")
                print(f"   [{plat.upper()} {i}/{len(plat_items)}] Query: '{q[:70]}...'")
                try:
                    res = driver.run_query(
                        query=q,
                        brand_name=brand,
                        account_name=account,
                        headless=headless,
                    )
                    res_dict = res.model_dump(mode="json")
                    res_dict["platform"] = plat
                    res_dict["stage"] = item.get("stage")
                    res_dict["intent"] = item.get("intent")
                    plat_results.append(res_dict)
                    status = "✓ CITED" if res.brand_cited else "✗ NOT CITED"
                    print(f"        └─ {status} | {len(res.citations)} citations | {res.duration_seconds:.1f}s")
                except Exception as q_err:
                    print(f"        └─ ⚠️ Query error on {plat}: {q_err}")

            plat_results_file.write_text(json.dumps(plat_results, indent=2, ensure_ascii=False))
            print(f"   ✓ Saved {plat.upper()} audit results -> {plat_results_file}\n")
            return plat_results
        except Exception as e:
            print(f"   ⚠️ Batch audit on {plat.upper()} encountered an error: {e}")
            if plat_results_file.exists():
                try:
                    return json.loads(plat_results_file.read_text())
                except Exception:
                    pass
            return []

    # Run platforms in parallel to fit within MCP client tool timeout
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, len(platforms_list))) as executor:
        future_to_plat = {executor.submit(audit_single_platform, p): p for p in platforms_list}
        for future in concurrent.futures.as_completed(future_to_plat):
            p_res = future.result()
            all_results.extend(p_res)

    if not all_results:
        print(f"❌ No audit results collected across target platforms", file=sys.stderr)
        sys.exit(1)

    results_json.write_text(json.dumps(all_results, indent=2, ensure_ascii=False))
    print(f"   ✓ Combined audit results saved -> {results_json}\n")

    # -------------------------------------------------------------
    # Step 3: Calculate Quantitative Metrics & Archetype Payloads
    # -------------------------------------------------------------
    print(f"📊 [3/3] Aggregating quantitative GEO benchmarks & archetype payloads...")
    try:
        metrics = aggregate_audit_results(
            results=all_results,
            brand_name=brand,
            known_competitors=comp_list,
            brand_domain=domain,
        )
        if otterly_intel:
            metrics["otterly_intel"] = otterly_intel
        metrics_json.write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
        print(f"   ✓ Quantitative metrics aggregated -> {metrics_json}\n")

        # Compile Full 21-Slide Executive Presentation Deck
        deck_path = None
        if generate_deck:
            try:
                from engine.deckcraft.builder import compile_deck
                print(f"🎨 Compiling 21-slide Redcomm executive GEO pitch deck...")
                deck_path = compile_deck(
                    brand=brand,
                    category=category,
                    competitors=competitors,
                    domain=domain,
                    metrics_path=str(metrics_json),
                    out_dir=str(out_path),
                    year=year,
                )
                print(f"   ✓ 21-slide executive presentation generated -> {deck_path}\n")
            except Exception as e:
                print(f"   ⚠ Warning: Failed to generate deck: {e}", file=sys.stderr)



        # Executive Summary Printout
        kpis = metrics.get("kpis", {})
        print(f"========================================================")
        print(f"📈 EXECUTIVE GEO BENCHMARK SUMMARY: {brand.upper()}")
        print(f"========================================================")
        print(f"   Brand Share of Voice:   {kpis.get('ai_share_of_voice_pct', 0)}%")
        print(f"   Win Rate (#1 Rec):      {kpis.get('win_rate_pct', 0)}%")
        print(f"   Brand Citations:        {kpis.get('total_brand_citations', 0)}")
        print(f"   Total Citations Mapped: {kpis.get('total_citations_extracted', 0)}")
        print(f"   Unique Domains:         {kpis.get('unique_domains', 0)}")
        print(f"\n   Funnel Visibility:")
        for stage, data in metrics.get("funnel_journey_breakdown", {}).items():
            print(f"     • {stage.capitalize():<15}: {data.get('citation_rate_pct', 0)}% ({data.get('brand_cited', 0)}/{data.get('total_queries', 0)}) | Wins: {data.get('wins', 0)}")
        print(f"\n   Top Competitor Presence:")
        for comp in metrics.get("competitor_landscape", [])[:3]:
            print(f"     • {comp.get('competitor'):<15}: {comp.get('presence_rate_pct', 0)}% ({comp.get('mention_count', 0)} mentions)")
        print(f"\n   Top Citation Domains:")
        for dom in metrics.get("top_citation_sources", [])[:3]:
            print(f"     • {dom.get('domain'):<20}: {dom.get('citation_count', 0)} citations ({dom.get('share_pct', 0)}%)")
        print(f"========================================================\n")

        return {
            "metrics": metrics,
            "otterly_intel": otterly_intel,
            "deck_path": str(deck_path) if deck_path else None,
            "queries": sampled_batch,
            "all_queries": queries,
            "results": all_results,
            "csv_itemized_content": csv_itemized.read_text(encoding="utf-8") if csv_itemized.exists() else "",
            "csv_matrix_content": csv_matrix.read_text(encoding="utf-8") if csv_matrix.exists() else "",
        }



    except Exception as e:
        print(f"❌ Error calculating metrics: {e}", file=sys.stderr)
        raise e


def main():
    parser = argparse.ArgumentParser(description="PersuAId All-In-One GEO Audit Pipeline Runner")
    parser.add_argument("--brand", "-b", required=True, help="Target brand name")
    parser.add_argument("--domain", "-d", default=None, help="Target brand web domain (e.g. 'jotun.com', 'electrum.id')")
    parser.add_argument("--category", "-c", required=True, help="Category or product line")
    parser.add_argument("--competitors", "-comp", default="Competitor A,Competitor B", help="Comma-separated competitors")
    parser.add_argument("--geo", "-g", default="Indonesia", help="Target geography (default: 'Indonesia')")
    parser.add_argument("--platform", "-p", default="chatgpt,gemini", help="Target AI platform(s) (e.g. 'chatgpt,gemini')")
    parser.add_argument("--platforms", default=None, help="Comma-separated platforms (e.g. 'chatgpt,gemini')")
    parser.add_argument("--account", "-a", default=None, help="Specific account profile identifier")
    parser.add_argument("--out-dir", "-o", default=".", help="Output directory for generated files")
    parser.add_argument("--year", "-y", type=int, default=2026, help="Target year")
    parser.add_argument("--headed", action="store_true", help="Run browser in headed mode")
    parser.add_argument("--no-reverse-prompt", action="store_true", help="Skip live reverse prompting and use template generation")
    parser.add_argument("--provider", default="auto", choices=["auto", "apify", "camoufox"], help="Execution engine provider (default: auto)")
    parser.add_argument("--apify-token", default=None, help="Apify API token for cloud execution")
    parser.add_argument("--otterly-key", default=None, help="Otterly API key override")
    parser.add_argument("--no-otterly", action="store_true", help="Skip Otterly check even if API key is configured")
    parser.add_argument("--max-per-stage", type=int, default=5, help="Max queries to gather per stage (default: 5)")

    parser.add_argument("--samples-per-stage", type=int, default=2, help="Number of queries to sample per stage for live audit (default: 2)")
    parser.add_argument("--audit-all", action="store_true", help="Audit all gathered queries instead of sampling")
    parser.add_argument("--generate-deck", action="store_true", help="Generate 21-slide Redcomm executive GEO presentation (.pptx)")

    args = parser.parse_args()
    target_platform = args.platforms or args.platform

    run_pipeline(
        brand=args.brand,
        domain=args.domain,
        category=args.category,
        competitors=args.competitors,
        geo=args.geo,
        platform=target_platform,
        account=args.account,
        out_dir=args.out_dir,
        headless=not args.headed,
        year=args.year,
        reverse_prompt=not args.no_reverse_prompt,
        provider=args.provider,
        apify_token=args.apify_token,
        otterly_key=args.otterly_key,
        no_otterly=args.no_otterly,
        generate_deck=args.generate_deck,
        max_per_stage=args.max_per_stage,
        samples_per_stage=args.samples_per_stage,
        audit_all=args.audit_all,
    )



if __name__ == "__main__":
    main()
