#!/usr/bin/env python3
"""
PersuAId Local MCP (Model Context Protocol) Server
Exposes PersuAId's multi-platform GEO audit engine, query formatter, metric aggregator,
and secure credentials manager as standardized MCP tools over stdio.

Runs with pure Python standard library (zero external pip dependencies).
Compatible with all MCP clients: ZCode, Claude Desktop, Cursor, Zed, Goose, Roo Code.
Includes in-flight request deduplication and result caching to prevent double actor charges on client retries.
"""

import sys
import os
import json
import logging
import hashlib
import time
import threading
from typing import Dict, Any, List, Optional
from pathlib import Path

# Configure stderr logging (keeping stdout clean for JSON-RPC 2.0 communication)
logging.basicConfig(
    level=logging.INFO,
    format="[persuaid-mcp] %(levelname)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("persuaid-mcp")

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.credentials import resolve_apify_token, store_token, get_stored_token, has_apify_token
from engine.apify_client import ApifyClient
from scripts.format_queries import (
    reverse_prompt_queries,
    generate_platform_journey_queries,
    sample_audit_queries,
    export_itemized_csv,
    export_matrix_csv,
)
from scripts.aggregate_metrics import aggregate_audit_results
from scripts.run_audit_pipeline import run_pipeline


SERVER_INFO = {
    "name": "persuaid-mcp",
    "version": "1.3.0",
}

SERVER_CAPABILITIES = {
    "tools": {},
}

TOOLS = [
    {
        "name": "persuaid_audit_query",
        "description": "Audits a single search query on ChatGPT, Google Gemini (AI Overviews), or both to evaluate brand presence, citation domains, and competitor mentions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search prompt or question to audit (e.g. 'Rekomendasi motor listrik terbaik di Indonesia').",
                },
                "platform": {
                    "type": "string",
                    "enum": ["chatgpt", "gemini", "all"],
                    "default": "chatgpt",
                    "description": "Target AI platform ('chatgpt', 'gemini', or 'all').",
                },
                "brand_name": {
                    "type": "string",
                    "description": "The client brand name to track for presence and citations.",
                },
                "brand_domain": {
                    "type": "string",
                    "description": "The client website domain (e.g. 'electrum.id') to check in grounding sources.",
                },
                "competitors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of competitor brand names to detect.",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "persuaid_run_pipeline",
        "description": "Runs the complete Step 1.5 GEO audit pipeline in one command: generates 5-stage search journey query taxonomy, exports CSV matrix, audits ChatGPT and Gemini via cloud Apify actors, and calculates comprehensive metrics and CSV content inline.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand": {
                    "type": "string",
                    "description": "The client brand name (e.g. 'Electrum', 'Siloam International Hospital').",
                },
                "category": {
                    "type": "string",
                    "description": "Product or service category (e.g. 'motor listrik', 'healthcare network').",
                },
                "competitors": {
                    "type": "string",
                    "description": "Comma-separated list of top competitors to benchmark against.",
                },
                "geo": {
                    "type": "string",
                    "default": "Indonesia",
                    "description": "Geographic market (e.g. 'Indonesia', 'Global').",
                },
                "domain": {
                    "type": "string",
                    "description": "Official brand website domain (e.g. 'electrum.id', 'siloamhospitals.com').",
                },
                "platform": {
                    "type": "string",
                    "default": "chatgpt,gemini",
                    "description": "Target AI platforms ('chatgpt', 'gemini', or 'chatgpt,gemini').",
                },
                "samples_per_stage": {
                    "type": "integer",
                    "default": 1,
                    "description": "Number of sample queries to audit per stage (default: 1 for fast 30s response).",
                },
                "reverse_prompt": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to reverse-prompt authentic queries or use template taxonomy.",
                },
            },
            "required": ["brand", "category", "competitors"],
        },
    },
    {
        "name": "persuaid_format_queries",
        "description": "Generates a structured 5-stage AI Search Journey query taxonomy (Discovery, Interest, Consideration, Purchase, After-Purchase) across ChatGPT and Gemini.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand": {
                    "type": "string",
                    "description": "The client brand name.",
                },
                "category": {
                    "type": "string",
                    "description": "Product or service category.",
                },
                "competitors": {
                    "type": "string",
                    "description": "Comma-separated list of competitors.",
                },
                "geo": {
                    "type": "string",
                    "default": "Indonesia",
                    "description": "Geographic scope.",
                },
                "out": {
                    "type": "string",
                    "description": "Optional output filepath to save queries JSON.",
                },
            },
            "required": ["brand", "category", "competitors"],
        },
    },
    {
        "name": "persuaid_aggregate_metrics",
        "description": "Computes analytical GEO benchmarks (Share of Voice %, #1 recommendation Win Rate %, 5-stage funnel visibility, citation domains) from audit results.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "results_file": {
                    "type": "string",
                    "description": "Path to results.json or raw list of audit items.",
                },
                "brand": {
                    "type": "string",
                    "description": "Target brand name.",
                },
                "brand_domain": {
                    "type": "string",
                    "description": "Optional official website domain.",
                },
                "out": {
                    "type": "string",
                    "description": "Optional output filepath to save metrics.json.",
                },
            },
            "required": ["results_file", "brand"],
        },
    },
    {
        "name": "persuaid_configure_credentials",
        "description": "Checks, tests, or configures the Apify API token stored securely in ~/.persuaid/credentials.json.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "apify_token": {
                    "type": "string",
                    "description": "Apify API token (starts with apify_api_...). If omitted, checks existing credentials.",
                },
                "test_connection": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to test the token validity against Apify API.",
                },
            },
        },
    },
]


# ==============================================================================
# Idempotency & In-Flight Request Deduplication Layer
# Prevents duplicate Apify Actor runs and double charges when MCP clients retry
# ==============================================================================

_RESULT_CACHE: Dict[str, tuple] = {}
_IN_FLIGHT: Dict[str, tuple] = {}
_IDEMPOTENCY_LOCK = threading.Lock()
CACHE_TTL_SECONDS = 7200  # Cache valid for 2 hours


def _get_cache_key(prefix: str, data: dict) -> str:
    canonical = json.dumps(data, sort_keys=True)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"


def handle_persuaid_audit_query(args: Dict[str, Any]) -> Dict[str, Any]:
    query = args["query"]
    platform = args.get("platform", "chatgpt").lower()
    brand_name = args.get("brand_name", "")
    brand_domain = args.get("brand_domain", "")
    competitors = args.get("competitors", [])

    cache_key = _get_cache_key("audit", {
        "query": query.strip().lower(),
        "platform": platform,
        "brand_name": brand_name.strip().lower(),
        "brand_domain": brand_domain.strip().lower(),
    })

    now = time.time()

    # 1. Check completed cache
    with _IDEMPOTENCY_LOCK:
        if cache_key in _RESULT_CACHE:
            ts, cached_res = _RESULT_CACHE[cache_key]
            if now - ts < CACHE_TTL_SECONDS:
                logger.info(f"⚡ [IDEMPOTENT] Returning cached audit result for key: {cache_key}")
                return cached_res

        # 2. Check in-flight run
        if cache_key in _IN_FLIGHT:
            event, container = _IN_FLIGHT[cache_key]
            is_worker = False
        else:
            event = threading.Event()
            container = {}
            _IN_FLIGHT[cache_key] = (event, container)
            is_worker = True

    # If already running elsewhere, wait for completion
    if not is_worker:
        logger.info(f"⏳ [IN-FLIGHT DEDUP] Waiting for existing audit run: {cache_key}")
        event.wait(timeout=180)
        return container.get("result", {"status": "error", "error": "In-flight audit timed out."})

    # Main worker execution
    try:
        token = resolve_apify_token()
        if not token:
            res_val = {"error": "Apify token not found. Please run persuaid_configure_credentials to set your Apify API token."}
            container["result"] = res_val
            return res_val

        client = ApifyClient(token=token)
        platforms_to_audit = ["chatgpt", "gemini"] if platform == "all" else [platform]

        results_data = []
        for plat in platforms_to_audit:
            try:
                if plat == "gemini":
                    res = client.audit_gemini_overviews(queries=[query], brand_name=brand_name)
                else:
                    res = client.audit_chatgpt(queries=[query], brand_name=brand_name)

                for r in res:
                    if hasattr(r, "to_dict"):
                        results_data.append(r.to_dict())
                    elif hasattr(r, "model_dump"):
                        results_data.append(r.model_dump(mode="json"))
                    elif isinstance(r, dict):
                        results_data.append(r)
                    else:
                        results_data.append(vars(r))
            except Exception as e:
                logger.error(f"Error auditing {plat} query: {e}")
                results_data.append({
                    "platform": plat,
                    "query": query,
                    "error": str(e),
                })

        final_res = {
            "status": "success",
            "query": query,
            "results": results_data,
        }

        container["result"] = final_res
        with _IDEMPOTENCY_LOCK:
            _RESULT_CACHE[cache_key] = (time.time(), final_res)
        return final_res

    finally:
        with _IDEMPOTENCY_LOCK:
            event.set()
            _IN_FLIGHT.pop(cache_key, None)


def handle_persuaid_run_pipeline(args: Dict[str, Any]) -> Dict[str, Any]:
    brand = args["brand"]
    category = args["category"]
    competitors = args["competitors"]
    geo = args.get("geo", "Indonesia")
    domain = args.get("domain")
    platform = args.get("platform", "chatgpt,gemini")
    out_dir = args.get("out_dir", "/tmp/persuaid_runs")
    samples_per_stage = args.get("samples_per_stage", 1)
    reverse_prompt = args.get("reverse_prompt", True)
    brand_slug = brand.strip().replace(" ", "_")

    cache_key = _get_cache_key("pipeline", {
        "brand": brand.strip().lower(),
        "domain": (domain or "").strip().lower(),
        "category": category.strip().lower(),
        "competitors": sorted([c.strip().lower() for c in competitors.split(",") if c.strip()]),
        "geo": geo.strip().lower(),
        "platform": platform.strip().lower(),
        "samples_per_stage": samples_per_stage,
    })

    now = time.time()

    # 1. Check completed cache
    with _IDEMPOTENCY_LOCK:
        if cache_key in _RESULT_CACHE:
            ts, cached_res = _RESULT_CACHE[cache_key]
            if now - ts < CACHE_TTL_SECONDS:
                logger.info(f"⚡ [IDEMPOTENT] Returning cached pipeline result for: {brand} ({cache_key})")
                return cached_res

        # 2. Check in-flight run
        if cache_key in _IN_FLIGHT:
            event, container = _IN_FLIGHT[cache_key]
            is_worker = False
        else:
            event = threading.Event()
            container = {}
            _IN_FLIGHT[cache_key] = (event, container)
            is_worker = True

    # If already running elsewhere (e.g. client timeout retry), wait for the active run
    if not is_worker:
        logger.info(f"⏳ [IN-FLIGHT DEDUP] Client retry detected for pipeline '{brand}'. Waiting on active cloud run ({cache_key})...")
        event.wait(timeout=180)
        return container.get("result", {"status": "error", "error": "In-flight pipeline run timed out."})

    # Main worker execution
    try:
        pipeline_output = run_pipeline(
            brand=brand,
            category=category,
            competitors=competitors,
            geo=geo,
            domain=domain,
            platform=platform,
            out_dir=out_dir,
            reverse_prompt=reverse_prompt,
            samples_per_stage=samples_per_stage,
            provider="auto",
        )

        metrics = pipeline_output.get("metrics") if isinstance(pipeline_output, dict) else pipeline_output
        csv_itemized = pipeline_output.get("csv_itemized_content", "") if isinstance(pipeline_output, dict) else ""
        csv_matrix = pipeline_output.get("csv_matrix_content", "") if isinstance(pipeline_output, dict) else ""

        final_res = {
            "status": "success",
            "message": f"GEO audit pipeline completed successfully for {brand}.",
            "brand": brand,
            "domain": domain,
            "category": category,
            "metrics": metrics,
            "csv_itemized_content": csv_itemized,
            "csv_matrix_content": csv_matrix,
            "itemized_csv_filename": f"{brand_slug}_AI_Search_Journey_Prompts.csv",
            "matrix_csv_filename": f"{brand_slug}_AI_Search_Journey_Matrix.csv",
            "total_queries_audited": len(pipeline_output.get("results", [])) if isinstance(pipeline_output, dict) else 0,
        }

        container["result"] = final_res
        with _IDEMPOTENCY_LOCK:
            _RESULT_CACHE[cache_key] = (time.time(), final_res)
        return final_res

    except Exception as e:
        logger.error(f"Pipeline execution error: {e}", exc_info=True)
        err_res = {
            "status": "error",
            "error": str(e),
        }
        container["result"] = err_res
        return err_res

    finally:
        with _IDEMPOTENCY_LOCK:
            event.set()
            _IN_FLIGHT.pop(cache_key, None)


def handle_persuaid_format_queries(args: Dict[str, Any]) -> Dict[str, Any]:
    brand = args["brand"]
    category = args["category"]
    competitors = args["competitors"]
    geo = args.get("geo", "Indonesia")
    out_file = args.get("out")

    comp_list = [c.strip() for c in competitors.split(",") if c.strip()] if isinstance(competitors, str) else competitors
    
    token = resolve_apify_token()
    queries = None
    if token:
        try:
            queries = reverse_prompt_queries(brand, category, comp_list, geo)
        except Exception as e:
            logger.warning(f"Reverse prompting failed, generating standard journey taxonomy: {e}")

    if not queries:
        queries = generate_platform_journey_queries(brand, category, comp_list, geo)

    if out_file:
        Path(out_file).write_text(json.dumps(queries, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "status": "success",
        "brand": brand,
        "category": category,
        "total_queries": sum(len(q_list) for q_list in queries.values()) if isinstance(queries, dict) else len(queries),
        "taxonomy": queries,
    }


def handle_persuaid_aggregate_metrics(args: Dict[str, Any]) -> Dict[str, Any]:
    results_file = args["results_file"]
    brand = args["brand"]
    brand_domain = args.get("brand_domain")
    out_file = args.get("out")

    try:
        metrics = aggregate_audit_results(
            results=results_file,
            brand_name=brand,
            brand_domain=brand_domain,
        )
        if out_file and metrics and "error" not in metrics:
            Path(out_file).write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
        return {
            "status": "success",
            "metrics": metrics,
        }
    except Exception as e:
        logger.error(f"Error aggregating metrics: {e}")
        return {
            "status": "error",
            "error": str(e),
        }


def handle_persuaid_configure_credentials(args: Dict[str, Any]) -> Dict[str, Any]:
    new_token = args.get("apify_token")
    test_conn = args.get("test_connection", True)

    if new_token:
        store_token(new_token)
        token_to_use = new_token
        action_note = "New Apify token stored securely in ~/.persuaid/credentials.json (0600)."
    else:
        token_to_use = resolve_apify_token()
        action_note = "Using currently resolved Apify token."

    if not token_to_use:
        return {
            "status": "not_configured",
            "message": "No Apify token is currently configured. Provide 'apify_token' to authenticate.",
            "credentials_file": str(Path.home() / ".persuaid" / "credentials.json"),
        }

    token_masked = token_to_use[:10] + "..." + token_to_use[-4:] if len(token_to_use) > 15 else "***"
    conn_status = "untested"
    user_info = None

    if test_conn:
        try:
            import urllib.request
            req = urllib.request.Request(f"https://api.apify.com/v2/users/me?token={token_to_use}")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())["data"]
                user_info = {
                    "username": data.get("username"),
                    "email": data.get("email"),
                    "plan": data.get("plan", {}).get("name"),
                }
                conn_status = "valid"
        except Exception as e:
            conn_status = f"invalid: {e}"

    return {
        "status": "configured",
        "action": action_note,
        "token_preview": token_masked,
        "connection_test": conn_status,
        "user_info": user_info,
        "credentials_file": str(Path.home() / ".persuaid" / "credentials.json"),
    }


TOOL_HANDLERS = {
    "persuaid_audit_query": handle_persuaid_audit_query,
    "persuaid_run_pipeline": handle_persuaid_run_pipeline,
    "persuaid_format_queries": handle_persuaid_format_queries,
    "persuaid_aggregate_metrics": handle_persuaid_aggregate_metrics,
    "persuaid_configure_credentials": handle_persuaid_configure_credentials,
}


def process_json_rpc(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Processes incoming JSON-RPC 2.0 requests according to MCP Specification."""
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    if not method:
        return None

    # Handle JSON-RPC Notifications (no response needed)
    if method == "notifications/initialized":
        logger.info("Client MCP handshake completed.")
        return None

    # 1. initialize
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": SERVER_CAPABILITIES,
                "serverInfo": SERVER_INFO,
            },
        }

    # 2. ping
    if method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {},
        }

    # 3. tools/list
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS,
            },
        }

    # 4. tools/call
    if method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})

        handler = TOOL_HANDLERS.get(tool_name)
        if not handler:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Tool '{tool_name}' not found.",
                },
            }

        try:
            result_data = handler(tool_args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result_data, indent=2, ensure_ascii=False),
                        }
                    ],
                    "isError": result_data.get("status") == "error" or "error" in result_data,
                },
            }
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"status": "error", "error": str(e)}),
                        }
                    ],
                    "isError": True,
                },
            }

    # Unknown method
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {
            "code": -32601,
            "message": f"Method '{method}' not recognized.",
        },
    }


# Expose both function names for compatibility
handle_jsonrpc_request = process_json_rpc


def run_stdio_server():
    """Main stdio loop reading JSON-RPC 2.0 lines from stdin and writing responses to stdout."""
    logger.info("PersuAId MCP Server v1.3.0 started on stdio.")
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            line_str = line.strip()
            if not line_str:
                continue

            try:
                request = json.loads(line_str)
            except json.JSONDecodeError as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {e}",
                    },
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()
                continue

            response = process_json_rpc(request)
            if response is not None:
                sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
                sys.stdout.flush()

        except Exception as e:
            logger.error(f"Stdio server loop error: {e}", exc_info=True)
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal JSON-RPC error: {e}",
                },
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


def main():
    run_stdio_server()


if __name__ == "__main__":
    main()
