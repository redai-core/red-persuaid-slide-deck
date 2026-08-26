#!/usr/bin/env python3
"""
PersuAId Metric Aggregator & GEO Analytics Engine
Zero-dependency CLI tool to parse raw audit results (from ai-geo-camoufox or other GEO audit engines),
calculate quantitative benchmarks (SoV, Win Rate, Funnel Stages, Citations, Competitors),
and generate slide-ready metric payloads for PersuAId's 17 slide archetypes.

Usage:
  python3 scripts/aggregate_metrics.py --file results.json --brand "Samsung" --out metrics.json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict
from urllib.parse import urlparse


def classify_funnel_stage(query_text: str, intent: str = "") -> str:
    """Classifies a search query into one of the 5 search & buying journey stages."""
    text = (query_text + " " + intent).lower()

    # Stage 5: After-Purchase (troubleshooting, maintenance, how to use)
    if any(k in text for k in ["how to", "cara", "perawatan", "maintenance", "repair", "service", "garansi", "troubleshoot", "problem", "rusak", "fix", "clean", "noda", "stain", "after purchase"]):
        return "after_purchase"

    # Stage 4: Purchase (pricing, calculator, buy, store, dealers, promo)
    if any(k in text for k in ["where to buy", "toko", "beli", "dealer", "official store", "calculator", "kalkulator", "harga berapa", "biaya", "cost", "promo", "diskon", "distributor", "purchase"]):
        return "purchase"

    # Stage 3: Consideration (vs, comparison, review, is it worth, pros cons)
    if any(k in text for k in [" vs ", "versus", "bandingkan", "compare", "review", "worth buying", "kelebihan", "kekurangan", "difference", "better for", "consideration"]):
        return "consideration"

    # Stage 2: Interest (brand-specific product specs, features, catalog)
    if any(k in text for k in ["specs", "spesifikasi", "katalog", "catalog", "features", "fitur", "lineup", "series", "interest"]):
        return "interest"

    # Stage 1: Discovery (broad category, best of, recommendations)
    return "discovery"


def extract_domain(url_or_text: str) -> str:
    """Extracts a clean domain name from a URL or text string."""
    if not url_or_text:
        return ""
    url = url_or_text.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def normalize_publisher_to_domain(text: str) -> str:
    """Normalizes publisher names or partial text tokens to canonical domains."""
    mapping = {
        "android central": "androidcentral.com",
        "techradar": "techradar.com",
        "the guardian": "theguardian.com",
        "wired": "wired.com",
        "91mobiles": "91mobiles.com",
        "phonearena": "phonearena.com",
        "creative bloq": "creativebloq.com",
        "apple support": "support.apple.com",
        "samsung ch": "samsung.com",
        "samsung": "samsung.com",
        "vivo": "vivo.com",
        "oppo": "oppo.com",
        "mi": "mi.com",
        "honor": "honor.com",
        "sogi": "sogi.com.tw",
        "gsmarena": "gsmarena.com",
        "the verge": "theverge.com",
        "cnet": "cnet.com",
        "toms guide": "tomsguide.com",
        "digital trends": "digitaltrends.com",
        "kompas": "kompas.com",
        "detik": "detik.com",
        "reddit": "reddit.com",
        "quora": "quora.com",
    }
    cleaned = text.strip().lower()
    return mapping.get(cleaned, "")


def extract_citations_from_text(raw_text: str) -> list:
    """Extracts domains and publisher citations from raw LLM markdown output."""
    found = []
    
    # 1. Match full URLs or domain patterns like blog.google or example.com
    domains = re.findall(r"\b([a-zA-Z0-9-]+\.(?:com|org|net|io|co|google|id|tv|tw|app|tech|dev|me)(?:\.[a-zA-Z]{2})?)\b", raw_text, re.IGNORECASE)
    for d in domains:
        found.append(d.lower())

    # 2. Match standalone citation lines in markdown (e.g. "\nAndroid Central\n" or "\nTechRadar\n+1\n")
    known_publishers = [
        "Android Central", "TechRadar", "The Guardian", "WIRED", "91mobiles",
        "PhoneArena", "Creative Bloq", "Apple Support", "Samsung ch", "Vivo",
        "OPPO", "Mi", "Honor", "Sogi", "GSMArena", "The Verge", "CNET",
        "Tom's Guide", "Kompas", "Detik", "Reddit", "Quora"
    ]
    for pub in known_publishers:
        # Check for publisher appearing as citation badge or reference line
        if re.search(rf"(?:\n|\r|^|\s){re.escape(pub)}(?:\s*\+\d+|\n|\r|$)", raw_text, re.IGNORECASE):
            canonical = normalize_publisher_to_domain(pub)
            if canonical:
                found.append(canonical)

    return found


def categorize_domain(domain: str, brand_name: str, brand_domain: str = None) -> str:
    """Categorizes a citation domain into strategic source tiers."""
    domain_lower = domain.lower()
    brand_lower = brand_name.lower().replace(" ", "")

    if brand_domain:
        clean_bd = extract_domain(brand_domain)
        if clean_bd and clean_bd in domain_lower:
            return "Official Brand Channel"

    if brand_lower in domain_lower:
        return "Official Brand Channel"

    media_domains = [
        "techradar.com", "theverge.com", "androidcentral.com", "gsmarena.com",
        "cnet.com", "wired.com", "tomsguide.com", "phonearena.com", "91mobiles.com",
        "digitaltrends.com", "engadget.com", "kompas.com", "detik.com", "idntimes.com",
        "kumparan.com", "liputan6.com", "sogi.com.tw", "creativebloq.com"
    ]
    if any(m in domain_lower for m in media_domains):
        return "Editorial Tech & Trade Media"

    community_domains = ["reddit.com", "quora.com", "kaskus.co.id", "x.com", "twitter.com", "youtube.com", "tiktok.com"]
    if any(c in domain_lower for m in community_domains if (c := m) in domain_lower):
        return "Community & Discussion Forums"

    retail_domains = ["amazon.", "tokopedia.com", "shopee.", "blibli.com", "lazada.", "bestbuy.com", "maujual.com", "myhartono.com"]
    if any(r in domain_lower for r in retail_domains):
        return "E-Commerce & Retail Marketplace"

    news_domains = ["theguardian.com", "bbc.com", "nytimes.com", "cnn.com", "bloomberg.com", "reuters.com", "cnbc.com", "blog.google"]
    if any(n in domain_lower for n in news_domains):
        return "Authoritative News & Publisher"

    return "General Web & Blogs"


def is_win_recommendation(text: str, brand_name: str) -> bool:
    """Detects if the brand was recommended as #1 / best pick / winner in the response."""
    if not text or not brand_name:
        return False
    
    brand_lower = brand_name.lower()
    first_chunk = text[:1500].lower()

    # Look for top position indicators associated with brand
    patterns = [
        rf"(🥇|#1|1\.|rank\s*1|best overall|top pick|winner).*?{re.escape(brand_lower)}",
        rf"{re.escape(brand_lower)}.*?(is my #1|best overall|top pick|winner|🥇|#1 pick)",
        rf"(pick|recommend)\s*:\s*{re.escape(brand_lower)}",
    ]
    for pat in patterns:
        if re.search(pat, first_chunk, re.DOTALL):
            return True

    return False


def aggregate_audit_results(results, brand_name: str, known_competitors: list = None, brand_domain: str = None) -> dict:
    """Aggregates raw audit results into quantitative GEO metrics. Supports list of dicts or JSON filepath."""
    if isinstance(results, (str, Path)):
        p = Path(results)
        if not p.exists():
            return {"error": f"Results file '{results}' does not exist"}
        with open(p, "r", encoding="utf-8") as f:
            results = json.load(f)

    if not isinstance(results, list):
        return {"error": "Invalid results format: expected list of audit items"}

    total_queries = len(results)
    if total_queries == 0:
        return {"error": "Empty audit results list"}

    brand_cited_count = 0
    win_count = 0
    total_citations_count = 0
    
    platform_counts = defaultdict(lambda: {"total": 0, "cited": 0, "wins": 0})
    funnel_counts = {
        "discovery": {"total": 0, "cited": 0, "wins": 0},
        "interest": {"total": 0, "cited": 0, "wins": 0},
        "consideration": {"total": 0, "cited": 0, "wins": 0},
        "purchase": {"total": 0, "cited": 0, "wins": 0},
        "after_purchase": {"total": 0, "cited": 0, "wins": 0},
    }

    all_citations = []
    competitor_mentions = Counter()
    
    if not known_competitors:
        known_competitors = ["Apple", "iPhone", "OPPO", "HONOR", "Google", "Pixel", "Xiaomi", "Vivo", "Motorola", "OnePlus", "Sony", "Dulux", "Nippon Paint", "Avian", "Mowilex", "Honda", "Yamaha", "Gesits"]

    for item in results:
        query = item.get("query", "")
        intent = item.get("intent", "")
        platform = item.get("platform", "unknown")
        raw_text = item.get("raw_response_text", "")
        citations = item.get("citations", [])
        
        # Check brand citation
        cited = item.get("brand_cited", False)
        if not cited:
            if brand_name.lower() in raw_text.lower():
                cited = True
            elif brand_domain and extract_domain(brand_domain) and extract_domain(brand_domain) in raw_text.lower():
                cited = True
        
        if cited:
            brand_cited_count += 1

        is_win = is_win_recommendation(raw_text, brand_name)
        if is_win:
            win_count += 1

        # Funnel stage normalization
        raw_stage = item.get("stage")
        stage_num = item.get("stage_number") or item.get("stage_num")
        stage_slug = None

        if raw_stage is not None:
            s = str(raw_stage).lower().strip().replace("-", "_").replace(" ", "_")
            if any(k in s for k in ["after", "post", "maint", "care", "support", "trouble", "sales", "retention", "loyalty", "5"]):
                stage_slug = "after_purchase"
            elif any(k in s for k in ["purchas", "buy", "beli", "dealer", "store", "toko", "harga", "price", "cost", "promo", "4"]):
                stage_slug = "purchase"
            elif any(k in s for k in ["consid", "compar", "vs", "versus", "banding", "review", "worth", "layak", "3"]):
                stage_slug = "consideration"
            elif any(k in s for k in ["interest", "spec", "spesifikasi", "feature", "fitur", "catalog", "katalog", "lineup", "2"]):
                stage_slug = "interest"
            elif any(k in s for k in ["discov", "aware", "unbrand", "trend", "recom", "rekomendasi", "best", "terbaik", "1"]):
                stage_slug = "discovery"

        if not stage_slug and stage_num:
            num_map = {1: "discovery", 2: "interest", 3: "consideration", 4: "purchase", 5: "after_purchase"}
            try:
                stage_slug = num_map.get(int(stage_num))
            except Exception:
                pass

        if not stage_slug or stage_slug not in funnel_counts:
            stage_slug = classify_funnel_stage(query, intent)

        if stage_slug in funnel_counts:
            funnel_counts[stage_slug]["total"] += 1
            if cited:
                funnel_counts[stage_slug]["cited"] += 1
            if is_win:
                funnel_counts[stage_slug]["wins"] += 1

        # Platform metrics
        platform_counts[platform]["total"] += 1
        if cited:
            platform_counts[platform]["cited"] += 1
        if is_win:
            platform_counts[platform]["wins"] += 1

        # Parse direct citations array if present
        for c in citations:
            url = c.get("url") if isinstance(c, dict) else str(c)
            domain = extract_domain(url)
            if domain:
                all_citations.append(domain)

        # Extract domains and publisher citations from raw markdown output
        text_citations = extract_citations_from_text(raw_text)
        all_citations.extend(text_citations)

        # Scan competitor mentions
        for comp in known_competitors:
            if comp.lower() != brand_name.lower() and re.search(rf"\b{re.escape(comp)}\b", raw_text, re.IGNORECASE):
                competitor_mentions[comp] += 1

    total_citations_count = len(all_citations)
    domain_counter = Counter(all_citations)
    
    # Calculate percentages
    sov_percent = round((brand_cited_count / total_queries) * 100, 1) if total_queries else 0.0
    win_rate_percent = round((win_count / total_queries) * 100, 1) if total_queries else 0.0

    # Calculate funnel stage percentages
    funnel_summary = {}
    for stage, data in funnel_counts.items():
        t = data["total"]
        c = data["cited"]
        funnel_summary[stage] = {
            "total_queries": t,
            "brand_cited": c,
            "citation_rate_pct": round((c / t) * 100, 1) if t else 0.0,
            "wins": data["wins"]
        }

    # Top citation sources
    top_sources = []
    for domain, count in domain_counter.most_common(10):
        category = categorize_domain(domain, brand_name, brand_domain=brand_domain)
        pct = round((count / total_citations_count) * 100, 1) if total_citations_count else 0.0
        top_sources.append({
            "domain": domain,
            "category": category,
            "citation_count": count,
            "share_pct": pct
        })

    # Competitor rankings
    competitor_summary = []
    for comp, count in competitor_mentions.most_common(6):
        pct = round((count / total_queries) * 100, 1) if total_queries else 0.0
        competitor_summary.append({
            "competitor": comp,
            "mention_count": count,
            "presence_rate_pct": pct
        })

    # Build Archetype Payloads
    archetype_payloads = {
        "ARCH_HERO_STAT": {
            "metric_1": {"value": f"{sov_percent}%", "label": "AI Share of Voice", "subtext": f"{brand_cited_count}/{total_queries} queries cited brand"},
            "metric_2": {"value": f"{win_rate_percent}%", "label": "#1 Recommendation Win Rate", "subtext": f"{win_count}/{total_queries} top organic recommendations"},
            "metric_3": {"value": str(len(domain_counter)), "label": "Unique Citation Domains", "subtext": f"{total_citations_count} total references parsed"},
            "metric_4": {"value": f"{len(competitor_summary)}", "label": "Direct Competitors Detected", "subtext": "Challengers appearing in answers"},
            "synthesis": f"{brand_name} achieves {sov_percent}% Share of Voice across audited queries, but competitors actively split top recommendations in high-intent consideration stages."
        },
        "ARCH_JOURNEY_MAP": {
            "stages": [
                {"stage": "Discovery", "score": f"{funnel_summary['discovery']['citation_rate_pct']}%", "queries": funnel_summary['discovery']['total_queries']},
                {"stage": "Interest", "score": f"{funnel_summary['interest']['citation_rate_pct']}%", "queries": funnel_summary['interest']['total_queries']},
                {"stage": "Consideration", "score": f"{funnel_summary['consideration']['citation_rate_pct']}%", "queries": funnel_summary['consideration']['total_queries']},
                {"stage": "Purchase", "score": f"{funnel_summary['purchase']['citation_rate_pct']}%", "queries": funnel_summary['purchase']['total_queries']},
                {"stage": "After-Purchase", "score": f"{funnel_summary['after_purchase']['citation_rate_pct']}%", "queries": funnel_summary['after_purchase']['total_queries']},
            ],
            "synthesis": "Search visibility remains strongest during direct comparisons but requires reinforcement across broad unprompted discovery."
        },
        "ARCH_GAP_BAR": {
            "client_brand": brand_name,
            "client_rate": sov_percent,
            "competitors": competitor_summary
        },
        "ARCH_SOURCE_MATRIX": {
            "sources": top_sources
        }
    }

    return {
        "brand_name": brand_name,
        "total_queries_audited": total_queries,
        "kpis": {
            "ai_share_of_voice_pct": sov_percent,
            "win_rate_pct": win_rate_percent,
            "total_brand_citations": brand_cited_count,
            "total_citations_extracted": total_citations_count,
            "unique_domains": len(domain_counter)
        },
        "platform_breakdown": dict(platform_counts),
        "funnel_journey_breakdown": funnel_summary,
        "competitor_landscape": competitor_summary,
        "top_citation_sources": top_sources,
        "archetype_payloads": archetype_payloads
    }


# Backwards compatibility alias
calculate_metrics = aggregate_audit_results


def print_terminal_summary(metrics: dict):
    """Prints an executive summary table to terminal stdout."""
    brand = metrics.get("brand_name", "Brand")
    kpis = metrics.get("kpis", {})
    funnel = metrics.get("funnel_journey_breakdown", {})
    sources = metrics.get("top_citation_sources", [])
    competitors = metrics.get("competitor_landscape", [])

    print("\n" + "=" * 70)
    print(f"📊 PERSUAID GEO AUDIT EXECUTIVE SUMMARY: {brand.upper()}")
    print("=" * 70)
    print(f"• Total Queries Audited     : {metrics.get('total_queries_audited', 0)}")
    print(f"• AI Share of Voice (SoV)   : {kpis.get('ai_share_of_voice_pct', 0)}%")
    print(f"• #1 Recommendation Win Rate: {kpis.get('win_rate_pct', 0)}%")
    print(f"• Total External Citations  : {kpis.get('total_citations_extracted', 0)} ({kpis.get('unique_domains', 0)} unique domains)")
    print("-" * 70)
    
    print("\n📍 5-STAGE SEARCH & BUYING JOURNEY FUNNEL:")
    print(f"  {'Stage':<18} | {'Queries':<8} | {'Brand Cited':<12} | {'Visibility %':<12}")
    print("  " + "-" * 56)
    for stage, data in funnel.items():
        print(f"  {stage.replace('_', ' ').title():<18} | {data['total_queries']:<8} | {data['brand_cited']:<12} | {data['citation_rate_pct']:<12}%")

    if competitors:
        print("\n⚔️ TOP COMPETITOR PRESENCE IN RESPONSES:")
        print(f"  {'Competitor':<18} | {'Mentions':<10} | {'Presence Rate %':<15}")
        print("  " + "-" * 48)
        for c in competitors:
            print(f"  {c['competitor']:<18} | {c['mention_count']:<10} | {c['presence_rate_pct']:<15}%")

    if sources:
        print("\n🌐 TOP AI CITATION SOURCES & DOMAINS:")
        print(f"  {'Domain':<24} | {'Category':<28} | {'Citations':<10}")
        print("  " + "-" * 66)
        for s in sources[:6]:
            print(f"  {s['domain']:<24} | {s['category']:<28} | {s['citation_count']:<10}")

    print("\n" + "=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="PersuAId Metric Aggregator & GEO Analytics Engine")
    parser.add_argument("--file", "-f", required=True, help="Path to raw audit results JSON file (from ai-geo-camoufox)")
    parser.add_argument("--brand", "-b", default="Samsung", help="Brand name to audit (default: Samsung)")
    parser.add_argument("--competitors", "-c", nargs="*", help="Optional list of known competitor names")
    parser.add_argument("--out", "-o", help="Optional path to output aggregated metrics JSON file")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress terminal printout")

    args = parser.parse_args()

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading results file '{args.file}': {e}", file=sys.stderr)
        sys.exit(1)

    metrics = aggregate_audit_results(raw_data, brand_name=args.brand, known_competitors=args.competitors)

    if not args.quiet:
        print_terminal_summary(metrics)

    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(metrics, f, indent=2)
            print(f"✓ Saved aggregated metrics to: {args.out}")
        except Exception as e:
            print(f"❌ Error saving output to '{args.out}': {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
