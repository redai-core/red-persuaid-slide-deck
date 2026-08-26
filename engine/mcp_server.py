#!/usr/bin/env python3
"""
PersuAId Local MCP (Model Context Protocol) Server
Exposes PersuAId's multi-platform GEO audit engine, query formatter, metric aggregator,
and secure credentials manager as standardized MCP tools over stdio.

Runs with pure Python standard library (zero external pip dependencies).
Compatible with all MCP clients: ZCode, Claude Desktop, Cursor, Zed, Goose, Roo Code.
"""

import sys
import os
import json
import logging
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
        "description": "Runs the complete Step 1.5 GEO audit pipeline in one command: generates 5-stage search journey query taxonomy, exports CSV matrix, audits ChatGPT and Gemini via cloud Apify actors (with local Camoufox fallback), and calculates comprehensive metrics.json.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand": {
                    "type": "string",
                    "description": "The client brand name (e.g. 'Electrum').",
                },
                "category": {
                    "type": "string",
                    "description": "Product or service category (e.g. 'motor listrik').",
                },
                "competitors": {
                    "type": "string",
                    "description": "Comma-separated list of competitors (e.g. 'Alva,Gesits,Polytron').",
                },
                "geo": {
                    "type": "string",
                    "default": "Indonesia",
                    "description": "Geographic target market.",
                },
                "domain": {
                    "type": "string",
                    "description": "Brand website domain (e.g. 'electrum.id').",
                },
                "platform": {
                    "type": "string",
                    "default": "chatgpt,gemini",
                    "description": "Platforms to audit ('chatgpt', 'gemini', or 'chatgpt,gemini').",
                },
                "out_dir": {
                    "type": "string",
                    "default": ".",
                    "description": "Directory to save generated CSV matrix and metrics.json.",
                },
                "samples_per_stage": {
                    "type": "integer",
                    "default": 2,
                    "description": "Number of sample queries to audit per journey stage.",
                },
                "reverse_prompt": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to use LLM reverse-prompting to discover organic user search queries.",
                },
            },
            "required": ["brand", "category", "competitors"],
        },
    },
    {
        "name": "persuaid_format_queries",
        "description": "Generates a structured 5-stage AI Search Journey query taxonomy (Discovery, Interest, Consideration, Purchase, After-Purchase) tailored for ChatGPT and Gemini.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand": {
                    "type": "string",
                    "description": "Brand name.",
                },
                "category": {
                    "type": "string",
                    "description": "Category or industry domain.",
                },
                "competitors": {
                    "type": "string",
                    "description": "Comma-separated competitor names.",
                },
                "geo": {
                    "type": "string",
                    "default": "Indonesia",
                    "description": "Target geographic region.",
                },
                "out": {
                    "type": "string",
                    "description": "Optional file path to export queries JSON.",
                },
            },
            "required": ["brand", "category", "competitors"],
        },
    },
    {
        "name": "persuaid_aggregate_metrics",
        "description": "Computes analytical GEO benchmarks (Share of Voice %, #1 recommendation win rate, funnel visibility by stage, citation domain breakdown, and slide archetype data) from an audit results file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "results_file": {
                    "type": "string",
                    "description": "Path to results.json or results_chatgpt.json.",
                },
                "brand": {
                    "type": "string",
                    "description": "Client brand name.",
                },
                "brand_domain": {
                    "type": "string",
                    "description": "Client domain.",
                },
                "out": {
                    "type": "string",
                    "description": "Optional path to write computed metrics.json.",
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
                    "description": "Apify API token (starts with 'apify_api_') to store securely with 0600 file permissions.",
                },
                "test_connection": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to test token validity against Apify's live API.",
                },
            },
        },
    },
]


def handle_persuaid_audit_query(args: Dict[str, Any]) -> Dict[str, Any]:
    query = args["query"]
    platform = args.get("platform", "chatgpt").lower()
    brand_name = args.get("brand_name", "")
    brand_domain = args.get("brand_domain", "")
    competitors = args.get("competitors", [])

    token = resolve_apify_token()
    if not token:
        return {
            "error": "Apify token not found. Please run persuaid_configure_credentials to set your Apify API token."
        }

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

    return {
        "status": "success",
        "query": query,
        "results": results_data,
    }


def handle_persuaid_run_pipeline(args: Dict[str, Any]) -> Dict[str, Any]:
    brand = args["brand"]
    category = args["category"]
    competitors = args["competitors"]
    geo = args.get("geo", "Indonesia")
    domain = args.get("domain")
    platform = args.get("platform", "chatgpt,gemini")
    out_dir = args.get("out_dir", ".")
    samples_per_stage = args.get("samples_per_stage", 2)
    reverse_prompt = args.get("reverse_prompt", True)

    try:
        metrics = run_pipeline(
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
        return {
            "status": "success",
            "message": f"GEO audit pipeline completed successfully for {brand}.",
            "brand": brand,
            "metrics": metrics,
            "artifacts": {
                "itemized_prompts_csv": f"{out_dir}/{brand}_AI_Search_Journey_Prompts.csv",
                "matrix_csv": f"{out_dir}/{brand}_AI_Search_Journey_Matrix.csv",
                "metrics_json": f"{out_dir}/metrics.json",
                "results_json": f"{out_dir}/results.json",
            },
        }
    except Exception as e:
        logger.error(f"Pipeline execution error: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
        }


def handle_persuaid_format_queries(args: Dict[str, Any]) -> Dict[str, Any]:
    brand = args["brand"]
    category = args["category"]
    competitors = args["competitors"]
    geo = args.get("geo", "Indonesia")
    out_file = args.get("out")

    comp_list = [c.strip() for c in competitors.split(",") if c.strip()] if isinstance(competitors, str) else competitors
    
    # Try reverse-prompting first if token available, fallback to template generation
    token = resolve_apify_token()
    queries = None
    if token:
        try:
            queries = reverse_prompt_queries(brand, category, comp_list, geo, token=token)
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
                    "isError": False if result_data.get("status") != "error" else True,
                },
            }
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
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
            except json.JSONDecodeError as err:
                logger.error(f"Malformed JSON: {err}")
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {err}"},
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()
                continue

            response = process_json_rpc(request)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

        except (KeyboardInterrupt, SystemExit):
            logger.info("Shutting down MCP server.")
            break
        except Exception as e:
            logger.error(f"Unexpected server exception: {e}", exc_info=True)


if __name__ == "__main__":
    run_stdio_server()
