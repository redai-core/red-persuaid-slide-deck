#!/usr/bin/env python3
"""
PersuAId Dual-Platform 5-Stage Journey Query Generator & Reverse-Prompting Interface
Formulates authentic, platform-specific search journey queries across Discovery,
Interest, Consideration, Purchase, and After-Purchase with strict platform separation:
- ChatGPT (Conversational, advisory, persona-based, problem-solving, recommendation queries)
- Gemini (Search-grounded, practical, spec comparison, ecosystem and how-to queries)

Exports:
  1. [Brand]_AI_Search_Journey_Prompts.csv (Itemized table with platform separation)
  2. [Brand]_AI_Search_Journey_Matrix.csv (Grid matching client reference CSV)
  3. queries.json (Sampled batch audit file)
"""

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path

# Add project root to sys.path so engine can be imported directly
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def generate_platform_journey_queries(brand: str, category: str, competitors: list, geo: str = "Indonesia", year: int = 2026) -> list:
    """
    Curated baseline search journey queries tailored to how users actually query
    each specific AI platform (ChatGPT & Gemini) across all 5 buying stages.
    """
    queries = []
    qid = 1
    comp_a = competitors[0] if len(competitors) > 0 else "Competitor A"
    comp_b = competitors[1] if len(competitors) > 1 else (competitors[0] if len(competitors) > 0 else "Competitor B")
    is_id = any(term in geo.lower() for term in ["indonesia", "indo", "id", "jakarta"])

    # -------------------------------------------------------------
    # -------------------------------------------------------------
    # 1. CHATGPT (Conversational, advisory, persona & problem solving)
    # -------------------------------------------------------------
    if is_id:
        chatgpt_data = {
            "DISCOVERY": [
                f"Saya sedang mencari {category} yang bagus, awet, dan ramah lingkungan untuk keluarga, ada rekomendasi merk apa?",
                f"Rekomendasi {category} terbaik tahun {year} yang hemat biaya operasional dan tidak gampang rusak",
                f"Tips memilih {category} untuk pemula agar tidak salah beli",
                f"Apa saja faktor terpenting saat memilih {category} untuk penggunaan harian?",
                f"Perbandingan {category} entry level vs premium di Indonesia",
            ],
            "INTEREST": [
                f"Apa saja keunggulan dan teknologi utama dari {brand} dibanding merk konvensional?",
                f"Bisa jelaskan varian produk {brand} beserta kelebihan masing-masing untuk kebutuhan sehari-hari?",
                f"Apakah {brand} aman digunakan dan bagaimana kualitas materialnya?",
                f"Berapa estimasi biaya operasional dan efisiensi menggunakan {brand}?",
                f"Fitur andalan {brand} yang membuatnya berbeda dari brand sejenis",
            ],
            "CONSIDERATION": [
                f"Tolong bandingkan {brand} vs {comp_a}: dari segi daya tahan, kenyamanan, dan biaya, lebih worth it mana?",
                f"Review jujur pengguna {brand}: apa kelebihan dan kekurangannya dibanding {comp_b}?",
                f"Apakah {brand} benar-benar layak dibeli untuk pemakaian jangka panjang 3-5 tahun?",
                f"Kelebihan {brand} jika dibandingkan dengan {comp_a} dan {comp_b}",
                f"Opini pengguna dan pakar mengenai keandalan {brand}",
            ],
            "PURCHASE": [
                f"Dimana tempat beli {brand} yang resmi dan terpercaya di Indonesia agar dapat garansi penuh dan promo?",
                f"Berapa estimasi harga {brand} dan apakah ada skema cicilan atau subsidi?",
                f"Bagaimana cara coba atau beli {brand} resmi di dealer terdekat?",
                f"Apakah ada promo diskon atau cashback untuk pembelian {brand} bulan ini?",
                f"Syarat dan simulasi pembiayaan cicilan untuk membeli {brand}",
            ],
            "AFTER_PURCHASE": [
                f"Bagaimana cara merawat {brand} agar performanya tetap maksimal dan tahan bertahun-tahun?",
                f"Apa keluhan paling umum dari pemilik {brand} dan bagaimana solusi mengatasinya?",
                f"Bagaimana prosedur klaim garansi resmi {brand} jika terjadi kerusakan?",
                f"Dimana bengkel resmi atau pusat servis terdekat untuk {brand} di Indonesia?",
                f"Ketersediaan suku cadang dan biaya servis berkala untuk {brand}",
            ]
        }
    else:
        chatgpt_data = {
            "DISCOVERY": [
                f"I'm looking for the best {category} that is durable, safe for family, and cost-effective. What do you recommend?",
                f"Top {category} recommendations in {year} with great value and low maintenance",
                f"Beginner guide: what factors should I look for when choosing {category}?",
                f"Best {category} brands for daily commute and heavy usage",
                f"How to choose the right {category} based on budget and durability",
            ],
            "INTEREST": [
                f"What are the proprietary features and advantages of {brand} compared to other brands?",
                f"Explain the different models in the {brand} lineup and their target use cases",
                f"How is the build quality, safety ratings, and reliability of {brand}?",
                f"What is the estimated cost of ownership for {brand}?",
                f"Key innovations that make {brand} stand out in {category}",
            ],
            "CONSIDERATION": [
                f"Compare {brand} vs {comp_a}: which is better for heavy daily use and long-term durability?",
                f"Honest review of {brand}: pros and cons compared to {comp_b}",
                f"Is {brand} truly worth buying over traditional alternatives in {year}?",
                f"Head-to-head showdown: {brand} vs {comp_a} on specs, price, and warranty",
                f"What do real owners say about {brand} after 1 year of ownership?",
            ],
            "PURCHASE": [
                f"Where can I buy official {brand} products with full manufacturer warranty and current promos?",
                f"What is the official pricing and financing options for {brand}?",
                f"How can I test drive or sample {brand} before purchasing?",
                f"Current discounts, government incentives, and rebates for {brand}",
                f"Authorized dealer network and online purchase options for {brand}",
            ],
            "AFTER_PURCHASE": [
                f"Step-by-step maintenance guide for {brand} to ensure maximum lifespan",
                f"What are the most common issues reported by {brand} owners and how to fix them?",
                f"What is the official warranty claim process for {brand}?",
                f"Availability of replacement parts and certified service centers for {brand}",
                f"How to protect and extend the lifecycle of {brand}",
            ]
        }

    stage_numbers = {"DISCOVERY": 1, "INTEREST": 2, "CONSIDERATION": 3, "PURCHASE": 4, "AFTER_PURCHASE": 5}
    for stage, items in chatgpt_data.items():
        s_num = stage_numbers[stage]
        for prompt in items:
            queries.append({
                "id": qid,
                "platform": "ChatGPT",
                "stage_number": s_num,
                "stage": stage,
                "intent": f"{stage.lower()}_query",
                "brand": brand,
                "q": prompt
            })
            qid += 1

    # -------------------------------------------------------------
    # 2. GEMINI (Search-grounded, practical, spec comparison, ecosystem)
    # -------------------------------------------------------------
    if is_id:
        gemini_data = {
            "DISCOVERY": [
                f"Rekomendasi {category} terbaik untuk rumah dan aktivitas harian di {geo}",
                f"Daftar hal yang wajib diperhatikan saat memilih {category} berkualitas",
                f"{category} yang paling hemat dan efisien untuk operasional harian",
                f"Pilihan {category} paling populer dan irit di {geo}",
                f"Panduan spesifikasi teknis penting saat membeli {category}",
            ],
            "INTEREST": [
                f"Katalog produk {brand} {category} lengkap dengan fitur dan varian model {year}",
                f"Fitur unggulan {brand} untuk kenyamanan dan keamanan pengguna",
                f"Harga resmi {brand} dan paket yang tersedia di pasaran",
                f"Spesifikasi teknis, efisiensi energi, dan performa {brand}",
                f"Review teknologi baterai dan sistem pintar pada {brand}",
            ],
            "CONSIDERATION": [
                f"{brand} vs {comp_a}: perbandingan langsung spesifikasi, kelebihan, dan harga",
                f"{brand} vs {comp_b}: mana yang lebih cocok untuk pemakaian keluarga dan jangka panjang?",
                f"Kelebihan dan kekurangan {brand} menurut ulasan otomotif dan pengguna",
                f"Komparasi {brand} vs {comp_a} vs {comp_b} untuk penggunaan harian",
                f"Apakah {brand} lebih hemat biaya dibanding kompetitor sekelas?",
            ],
            "PURCHASE": [
                f"Lokasi dealer resmi {brand} dan service center terdekat di {geo}",
                f"Harga promo dan diskon subsidi {brand} terbaru",
                f"Beli {brand} resmi di marketplace dan showroom authorized",
                f"Cara klaim subsidi dan simulasi kredit bunga rendah {brand}",
                f"Daftar kontak sales authorized showroom {brand}",
            ],
            "AFTER_PURCHASE": [
                f"Panduan perawatan rutin {brand} agar tidak cepat rusak dan awet",
                f"Solusi jika {brand} mengalami kendala teknis saat digunakan",
                f"Layanan purna jual, suku cadang, dan garansi resmi {brand}",
                f"Daftar alamat bengkel resmi dan hotline servis {brand}",
                f"Estimasi biaya ganti suku cadang dan servis berkala {brand}",
            ]
        }
    else:
        gemini_data = {
            "DISCOVERY": [
                f"Best {category} recommendations for daily use in {geo}",
                f"Essential checklist when buying {category}",
                f"Most efficient and cost-effective {category} options",
                f"Top rated {category} models for reliability in {year}",
                f"Key specifications to evaluate when shopping for {category}",
            ],
            "INTEREST": [
                f"Complete {brand} {category} catalog with features and trim options {year}",
                f"Key features of {brand} for safety and performance",
                f"Pricing guide and trim packages for {brand}",
                f"Detailed technical specs and operating efficiency of {brand}",
                f"Smart connectivity and ecosystem integrations in {brand}",
            ],
            "CONSIDERATION": [
                f"{brand} vs {comp_a}: direct comparison of specs, features, and price",
                f"{brand} vs {comp_b}: which is better for daily needs?",
                f"Pros and cons of {brand} according to industry reviews",
                f"Total cost of ownership comparison: {brand} vs {comp_a}",
                f"Expert and consumer comparison between {brand} and rival models",
            ],
            "PURCHASE": [
                f"Authorized showroom and dealer locations for {brand} in {geo}",
                f"Latest price list, financing promotions, and deals for {brand}",
                f"Official online store and authorized retailers for {brand}",
                f"How to apply for tax incentives or rebates on {brand}",
                f"Certified dealership contact list and inventory for {brand}",
            ],
            "AFTER_PURCHASE": [
                f"Routine maintenance guide for {brand}",
                f"How to fix common issues on {brand}",
                f"Customer service and warranty coverage for {brand}",
                f"Authorized service centers and OEM replacement parts for {brand}",
                f"Long-term reliability and battery health tips for {brand}",
            ]
        }

    for stage, items in gemini_data.items():
        s_num = stage_numbers[stage]
        for prompt in items:
            queries.append({
                "id": qid,
                "platform": "Gemini",
                "stage_number": s_num,
                "stage": stage,
                "intent": f"{stage.lower()}_query",
                "brand": brand,
                "q": prompt
            })
            qid += 1

    return queries


def extract_queries_from_stage_text(raw_text: str, platform: str, brand: str, max_per_stage: int = 5) -> list:
    """
    Simultaneously simple and robust plain-text parser:
    Splits the AI's response by standard stage section headers ([DISCOVERY], [INTEREST], etc.)
    and extracts clean bullet/numbered query lines under each section up to max_per_stage.
    """
    if not raw_text or not raw_text.strip():
        return []

    # 1. Try splitting by bracketed or styled headers: [DISCOVERY], **DISCOVERY**, # DISCOVERY
    pattern = r'(?:^|\n)\s*(?:\[|\*\*|###?\s*|\b)(DISCOVERY|INTEREST|CONSIDERATION|PURCHASE|AFTER[-_ ]?PURCHASE|AFTER[-_ ]?SALES|MAINTENANCE|TROUBLESHOOTING)(?:\]|\*\*|:|\b)'
    sections = re.split(pattern, raw_text, flags=re.IGNORECASE)

    queries = []
    seen = set()
    stage_counts = {}

    if len(sections) >= 3:
        for i in range(1, len(sections), 2):
            header_raw = sections[i].upper().replace("-", "_").replace(" ", "_")
            body = sections[i + 1] if i + 1 < len(sections) else ""

            if any(k in header_raw for k in ["AFTER", "MAINT", "SALES", "TROUBLE"]):
                stage_name, stage_num = "AFTER_PURCHASE", 5
            elif "PURCHASE" in header_raw or "BUY" in header_raw:
                stage_name, stage_num = "PURCHASE", 4
            elif "CONSIDERATION" in header_raw or "COMPARE" in header_raw:
                stage_name, stage_num = "CONSIDERATION", 3
            elif "INTEREST" in header_raw or "SPEC" in header_raw:
                stage_name, stage_num = "INTEREST", 2
            elif "DISCOVERY" in header_raw:
                stage_name, stage_num = "DISCOVERY", 1
            else:
                stage_name, stage_num = "DISCOVERY", 1

            for line in body.strip().splitlines():
                if stage_counts.get(stage_name, 0) >= max_per_stage:
                    break
                line = line.strip()
                if not line:
                    continue
                # Clean leading bullets, numbers, dashes
                cleaned = re.sub(r'^(?:[-*•–—]|\d+[.)])\s*', '', line).strip()
                # Strip all leading/trailing quote, backtick, and comma artifacts
                while cleaned and (cleaned[0] in '"\'`,' or cleaned[-1] in '"\'`,'):
                    cleaned = cleaned.strip('"\'`, ')
                # Skip instructional notes in parentheses
                if cleaned.startswith("(") and cleaned.endswith(")"):
                    continue
                if len(cleaned) >= 8 and not cleaned.lower().startswith("act as") and cleaned.lower() not in seen:
                    seen.add(cleaned.lower())
                    stage_counts[stage_name] = stage_counts.get(stage_name, 0) + 1
                    queries.append({
                        "platform": platform,
                        "stage_number": stage_num,
                        "stage": stage_name,
                        "intent": f"{stage_name.lower()}_query",
                        "brand": brand,
                        "q": cleaned,
                    })

    # 2. Fallback: Line-by-line inspection if header regex didn't split
    if not queries:
        current_stage, current_num = "DISCOVERY", 1
        for line in raw_text.splitlines():
            line_str = line.strip()
            if not line_str:
                continue

            low = line_str.lower()
            if any(k in low for k in ["after_purchase", "after purchase", "after sales", "maintenance", "troubleshoot", "stage 5", "5."]):
                current_stage, current_num = "AFTER_PURCHASE", 5
                continue
            elif any(k in low for k in ["purchase", "buying", "where to buy", "stage 4", "4."]):
                current_stage, current_num = "PURCHASE", 4
                continue
            elif any(k in low for k in ["consideration", "comparison", "stage 3", "3."]):
                current_stage, current_num = "CONSIDERATION", 3
                continue
            elif any(k in low for k in ["interest", "specs", "features", "stage 2", "2."]):
                current_stage, current_num = "INTEREST", 2
                continue
            elif any(k in low for k in ["discovery", "stage 1", "1."]):
                current_stage, current_num = "DISCOVERY", 1
                continue

            if stage_counts.get(current_stage, 0) >= max_per_stage:
                continue

            cleaned = re.sub(r'^(?:[-*•–—]|\d+[.)])\s*', '', line_str).strip()
            while cleaned and (cleaned[0] in '"\'`,' or cleaned[-1] in '"\'`,'):
                cleaned = cleaned.strip('"\'`, ')
            if len(cleaned) >= 8 and not cleaned.startswith("(") and not cleaned.lower().startswith("act as") and cleaned.lower() not in seen:
                seen.add(cleaned.lower())
                stage_counts[current_stage] = stage_counts.get(current_stage, 0) + 1
                queries.append({
                    "platform": platform,
                    "stage_number": current_num,
                    "stage": current_stage,
                    "intent": f"{current_stage.lower()}_query",
                    "brand": brand,
                    "q": cleaned,
                })

    return queries


def reverse_prompt_queries(
    brand: str,
    category: str,
    competitors: list,
    geo: str = "Indonesia",
    platforms: list | str = "chatgpt,gemini",
    account: str = None,
    headless: bool = True,
    year: int = 2026,
    max_per_stage: int = 5,
) -> list:
    """
    Executes simple plain-text reverse-prompting across both AI engines (ChatGPT & Gemini).
    Extracts authentic user queries per stage without fragile JSON schemas (capped to max_per_stage).
    Guarantees all 5 stages (including Stage 5: After-Purchase) are fully populated.
    """
    comp_list = [c.strip() for c in competitors] if isinstance(competitors, list) else [c.strip() for c in competitors.split(",") if c.strip()]
    comp_str = ", ".join(comp_list)

    if isinstance(platforms, str):
        plat_list = [p.strip().lower() for p in platforms.split(",") if p.strip()]
    else:
        plat_list = [p.strip().lower() for p in platforms if p.strip()]

    if not plat_list:
        plat_list = ["chatgpt", "gemini"]

    all_queries = []
    seen_prompts = set()
    fallback_templates = generate_platform_journey_queries(brand=brand, category=category, competitors=comp_list, geo=geo, year=year)

    for plat in plat_list:
        plat_name = "ChatGPT" if plat == "chatgpt" else "Gemini"
        plat_desc = (
            "conversational, advisory, persona-based, problem-solving, and comparative questions"
            if plat == "chatgpt"
            else "search-grounded, practical, specification-focused, ecosystem, and troubleshooting queries"
        )
        
        meta_prompt = f"""Act as a senior search intent and AI query behavior researcher in {geo}.
List the authentic questions, prompts, and search queries that real everyday consumers and buyers submit directly to {plat_name} ({plat_desc}) regarding "{brand}" and "{category}" in {geo} (comparing against competitors: {comp_str}).

Provide exactly {max_per_stage} distinct, natural user queries under each stage header below:

[DISCOVERY]
- (Unbranded category recommendations, best picks, buyer guides, trends)

[INTEREST]
- (Brand features, technical specifications, model lineup, pricing overview)

[CONSIDERATION]
- (Head-to-head comparisons: {brand} vs competitors, user reviews, is it worth buying)

[PURCHASE]
- (Where to buy, authorized dealers, official stores, financing, subsidies, promos)

[AFTER_PURCHASE]
- (Maintenance guide, durability, troubleshooting, service centers, warranty claims)

CRITICAL INSTRUCTIONS:
- Use authentic local phrasing and natural language as real buyers speak in {geo}.
- Return ONLY the stage headers and bullet-pointed queries. No conversational introduction or closing remarks.
"""
        try:
            raw = ""
            
            # 1. Try Apify Cloud Provider (Zero local browser overhead, bundled cloud token)
            try:
                from engine.apify_client import ApifyClient
                client = ApifyClient()
                print(f"   ☁️ Sending reverse-prompting meta-prompt to {plat.upper()} via Apify Cloud...")
                raw = client.reverse_prompt(platform=plat, meta_prompt=meta_prompt).strip()
            except Exception as e:
                print(f"   ⚠️ Apify Cloud reverse-prompting for {plat.upper()} failed: {e}. Falling back to local Camoufox.")

            # 2. Try Local Camoufox Driver (if Apify was not used or failed)
            if not raw:
                try:
                    from engine.session_manager import SessionManager
                    from engine.cli import get_driver
                    mgr = SessionManager()
                    driver = get_driver(plat, mgr)
                    print(f"   🤖 Sending reverse-prompting meta-prompt to {plat.upper()} via local Camoufox...")
                    res = driver.run_query(query=meta_prompt, brand_name=brand, account_name=account, headless=headless)
                    raw = res.raw_response_text.strip()
                except Exception as e:
                    print(f"   ⚠️ Local Camoufox reverse-prompting on {plat.upper()} failed: {e}")
            
            parsed_queries = extract_queries_from_stage_text(raw, platform=plat_name, brand=brand, max_per_stage=max_per_stage) if raw else []
            
            if parsed_queries and len(parsed_queries) >= 5:
                count_added = 0
                for q in parsed_queries:
                    prompt_text = q.get("q", "").strip()
                    if not prompt_text or prompt_text.lower() in seen_prompts:
                        continue
                    seen_prompts.add(prompt_text.lower())
                    all_queries.append(q)
                    count_added += 1
                print(f"   ✓ Extracted {count_added} unique queries from {plat.upper()}!")
            else:
                print(f"   ⚠️ Could not extract sufficient stage queries from {plat.upper()} response. Backfilling platform templates.")
                for t in fallback_templates:
                    if t.get("platform") == plat_name and t.get("q", "").lower() not in seen_prompts:
                        seen_prompts.add(t["q"].lower())
                        all_queries.append(dict(t))
        except Exception as e:
            print(f"   ⚠️ Reverse-prompting on {plat.upper()} failed: {e}. Backfilling platform templates.")
            for t in fallback_templates:
                if t.get("platform") == plat_name and t.get("q", "").lower() not in seen_prompts:
                    seen_prompts.add(t["q"].lower())
                    all_queries.append(dict(t))

    # Guarantee each stage has exactly max_per_stage queries for each target platform
    stages_to_check = ["DISCOVERY", "INTEREST", "CONSIDERATION", "PURCHASE", "AFTER_PURCHASE"]
    for plat in plat_list:
        plat_name = "ChatGPT" if plat == "chatgpt" else "Gemini"
        for st in stages_to_check:
            stage_qs = [
                q for q in all_queries
                if q.get("platform") == plat_name and q.get("stage") == st
            ]
            deficit = max_per_stage - len(stage_qs)
            if deficit > 0:
                for t in fallback_templates:
                    if deficit <= 0:
                        break
                    if t.get("platform") == plat_name and t.get("stage") == st:
                        if t.get("q", "").lower() not in seen_prompts:
                            seen_prompts.add(t["q"].lower())
                            all_queries.append(dict(t))
                            deficit -= 1

    # Sort queries logically: Platform (ChatGPT -> Gemini) then Stage (1 -> 5)
    plat_order = {"ChatGPT": 1, "Gemini": 2}
    all_queries.sort(key=lambda x: (plat_order.get(x.get("platform", "ChatGPT"), 99), x.get("stage_number", 1)))

    # Assign sequential IDs
    for i, q in enumerate(all_queries, 1):
        q["id"] = i

    print(f"   ✓ Multi-platform reverse-prompting complete: {len(all_queries)} total authentic queries gathered across {', '.join(p.upper() for p in plat_list)}!")
    return all_queries


def export_itemized_csv(queries: list, csv_path: str):
    """Exports itemized query taxonomy with explicit platform separation (ChatGPT & Gemini)."""
    fieldnames = ["ID", "Platform", "Stage_Number", "Stage", "Intent", "Brand", "User_Prompt", "Audited_In_Sample"]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in queries:
            writer.writerow({
                "ID": item.get("id"),
                "Platform": item.get("platform", "ChatGPT"),
                "Stage_Number": item.get("stage_number", 1),
                "Stage": item.get("stage", "DISCOVERY").upper(),
                "Intent": item.get("intent", f"{item.get('stage', 'discovery').lower()}_query"),
                "Brand": item.get("brand", ""),
                "User_Prompt": item.get("q", ""),
                "Audited_In_Sample": "YES" if item.get("audited_in_sample", False) else "NO"
            })


def export_matrix_csv(queries: list, matrix_csv_path: str):
    """
    Exports a grid matrix matching the client's reference spreadsheet format:
    Platform / LLM | Discovery | Interest | Consideration | Purchase | After Purchase
    Strictly covers ChatGPT and Gemini across all 5 stages.
    """
    platforms = ["ChatGPT", "Gemini"]
    stages = [
        ("DISCOVERY", "Discovery"),
        ("INTEREST", "Interest"),
        ("CONSIDERATION", "Consideration"),
        ("PURCHASE", "Purchase"),
        ("AFTER_PURCHASE", "After Purchase"),
    ]

    rows = []
    for plat in platforms:
        row = {"Platform / LLM": plat}
        for stage_key, stage_col in stages:
            stage_qs = [
                q["q"] for q in queries 
                if q.get("platform", "").lower() == plat.lower()
                and (
                    q.get("stage", "").upper().replace("-", "_").replace(" ", "_") == stage_key
                    or (stage_key == "AFTER_PURCHASE" and any(k in q.get("stage", "").upper() for k in ["AFTER", "MAINT", "SALES"]))
                )
            ]
            row[stage_col] = " · \n".join(f'"{q}"' for q in stage_qs)
        rows.append(row)

    fieldnames = ["Platform / LLM", "Discovery", "Interest", "Consideration", "Purchase", "After Purchase"]
    with open(matrix_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def sample_audit_queries(queries: list, samples_per_stage: int = 2, audit_all: bool = False) -> list:
    """
    Samples queries for the live batch audit sweep across ALL 5 stages
    (Discovery, Interest, Consideration, Purchase, After Purchase).
    If audit_all is True or samples_per_stage is None/0, returns all queries.
    Otherwise samples up to samples_per_stage from each stage (default: 2 per stage).
    """
    for i, q in enumerate(queries, 1):
        if "id" not in q:
            q["id"] = i

    sampled = []
    stages = ["DISCOVERY", "INTEREST", "CONSIDERATION", "PURCHASE", "AFTER_PURCHASE"]
    
    if audit_all or samples_per_stage is None or samples_per_stage <= 0:
        for q in queries:
            q_copy = dict(q)
            q_copy["audited_in_sample"] = True
            sampled.append(q_copy)
    else:
        for stage in stages:
            stage_queries = [
                q for q in queries 
                if q.get("stage", "").upper().replace("-", "_").replace(" ", "_") == stage
                or (stage == "AFTER_PURCHASE" and any(k in q.get("stage", "").upper() for k in ["AFTER", "MAINT", "SALES"]))
            ]
            for q in stage_queries[:samples_per_stage]:
                q_copy = dict(q)
                q_copy["audited_in_sample"] = True
                sampled.append(q_copy)
    
    sampled_ids = {q.get("id") for q in sampled}
    for q in queries:
        q["audited_in_sample"] = q.get("id") in sampled_ids

    return sampled


def main():
    parser = argparse.ArgumentParser(description="PersuAId Dual-Platform Query Generator & CSV Exporter")
    parser.add_argument("--brand", "-b", required=True, help="Brand name (e.g. 'Electrum', 'Jotun')")
    parser.add_argument("--category", "-c", required=True, help="Category or product line (e.g. 'motor listrik', 'cat tembok')")
    parser.add_argument("--competitors", "-comp", default="Competitor A,Competitor B", help="Comma-separated competitors")
    parser.add_argument("--geo", "-g", default="Indonesia", help="Target geography (default: 'Indonesia')")
    parser.add_argument("--year", "-y", type=int, default=2026, help="Target year (default: 2026)")
    parser.add_argument("--platform", "-p", default="chatgpt,gemini", help="Target platform(s) for live reverse-prompting (default: 'chatgpt,gemini')")
    parser.add_argument("--platforms", default=None, help="Comma-separated target platforms (default: 'chatgpt,gemini')")
    parser.add_argument("--reverse-prompt", action="store_true", help="Execute live reverse-prompting query on AI platform")
    parser.add_argument("--max-per-stage", type=int, default=5, help="Maximum queries to gather per stage (default: 5)")
    parser.add_argument("--samples-per-stage", type=int, default=2, help="Number of queries to sample per stage for live audit (default: 2)")
    parser.add_argument("--audit-all", action="store_true", help="Audit all gathered queries instead of sampling")
    parser.add_argument("--csv-out", "-csv", default=None, help="Output CSV path for itemized prompt taxonomy")
    parser.add_argument("--matrix-csv-out", "-mcsv", default=None, help="Output CSV path for matrix grid taxonomy")
    parser.add_argument("--out", "-o", default="queries.json", help="Output JSON path for sampled audit batch (default: 'queries.json')")

    args = parser.parse_args()
    competitor_list = [c.strip() for c in args.competitors.split(",") if c.strip()]
    brand_slug = args.brand.replace(" ", "_")
    csv_file = args.csv_out or f"{brand_slug}_AI_Search_Journey_Prompts.csv"
    matrix_csv_file = args.matrix_csv_out or f"{brand_slug}_AI_Search_Journey_Matrix.csv"
    target_platforms = args.platforms or args.platform

    if args.reverse_prompt:
        print(f"🔍 Reverse-prompting live from {target_platforms.upper()} with platform-separated query modeling...")
        full_queries = reverse_prompt_queries(
            brand=args.brand,
            category=args.category,
            competitors=competitor_list,
            geo=args.geo,
            platforms=target_platforms,
            year=args.year,
            headless=True,
            max_per_stage=args.max_per_stage,
        )
    else:
        full_queries = generate_platform_journey_queries(
            brand=args.brand,
            category=args.category,
            competitors=competitor_list,
            geo=args.geo,
            year=args.year
        )

    sampled_batch = sample_audit_queries(
        full_queries, 
        samples_per_stage=args.samples_per_stage, 
        audit_all=args.audit_all
    )

    # Export itemized CSV deliverable with platform separation
    export_itemized_csv(full_queries, csv_file)
    print(f"✓ Exported itemized search journey CSV with platform separation -> {csv_file}")

    # Export matrix grid CSV deliverable
    export_matrix_csv(full_queries, matrix_csv_file)
    print(f"✓ Exported search journey matrix CSV -> {matrix_csv_file}")

    # Export sampled JSON for live audit
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(sampled_batch, f, indent=2, ensure_ascii=False)
    print(f"✓ Exported {len(sampled_batch)} audit queries -> {args.out}")


if __name__ == "__main__":
    main()
