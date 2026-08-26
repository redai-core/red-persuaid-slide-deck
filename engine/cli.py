import json
import re
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from engine.session_manager import SessionManager
from engine.drivers.chatgpt import ChatGPTDriver
from engine.drivers.gemini import GeminiDriver

app = typer.Typer(help="PersuAId Headless AI GEO Visibility & Citation Auditor (Camoufox)")
console = Console()


def get_driver(platform: str, session_manager: Optional[SessionManager] = None):
    mgr = session_manager or SessionManager()
    plat = platform.lower()
    if plat == "chatgpt":
        return ChatGPTDriver(session_manager=mgr)
    elif plat == "gemini":
        return GeminiDriver(session_manager=mgr)
    else:
        raise typer.BadParameter(f"Unsupported platform: {platform}. Choose 'chatgpt' or 'gemini'.")


@app.command()
def auth(
    platform: str = typer.Option(..., "--platform", "-p", help="Target AI platform (chatgpt, gemini)"),
    account: str = typer.Option(..., "--account", "-a", help="Account identifier (e.g. acc1)"),
):
    """Interactive headed browser login to capture and persist session tokens."""
    console.print(f"[bold green]Starting interactive login flow for {platform} ({account})...[/bold green]")
    mgr = SessionManager()
    driver = get_driver(platform, mgr)
    driver.authenticate(account_name=account)
    console.print(f"[bold green]✓ Session successfully captured and stored in profiles/{platform}/![/bold green]")


@app.command("reverse-prompt")
def reverse_prompt(
    brand: str = typer.Option(..., "--brand", "-b", help="Brand name (e.g. 'Electrum', 'Jotun')"),
    category: str = typer.Option(..., "--category", "-c", help="Category / product line (e.g. 'motor listrik', 'cat tembok interior')"),
    competitors: str = typer.Option("Competitor A, Competitor B", "--competitors", "-comp", help="Comma-separated competitors"),
    geo: str = typer.Option("Indonesia", "--geo", "-g", help="Target geography & language context"),
    platform: str = typer.Option("chatgpt,gemini", "--platform", "-p", help="Target platform(s) to reverse-prompt (e.g. 'chatgpt,gemini')"),
    csv_out: Optional[Path] = typer.Option(None, "--csv-out", "-csv", help="Output CSV path for itemized prompt taxonomy"),
    matrix_csv_out: Optional[Path] = typer.Option(None, "--matrix-csv-out", "-mcsv", help="Output CSV path for matrix grid taxonomy"),
    out: Path = typer.Option(Path("queries.json"), "--out", "-o", help="Output JSON path for sampled audit batch"),
    headless: bool = typer.Option(True, "--headless/--headed", help="Run browser headlessly"),
):
    """Reverse-prompt AI engines (ChatGPT & Gemini) to extract platform-separated queries across ChatGPT and Gemini."""
    console.print(f"[bold cyan]🔍 Executing reverse-prompting across {platform.upper()} for {brand} ({category})...[/bold cyan]")
    from scripts.format_queries import (
        reverse_prompt_queries,
        export_itemized_csv,
        export_matrix_csv,
        sample_audit_queries,
    )

    comp_list = [c.strip() for c in competitors.split(",") if c.strip()]
    brand_slug = brand.replace(" ", "_")
    csv_file = csv_out or Path(f"{brand_slug}_AI_Search_Journey_Prompts.csv")
    matrix_csv_file = matrix_csv_out or Path(f"{brand_slug}_AI_Search_Journey_Matrix.csv")

    parsed_queries = reverse_prompt_queries(
        brand=brand,
        category=category,
        competitors=comp_list,
        geo=geo,
        platforms=platform,
        headless=headless,
    )

    sampled_batch = sample_audit_queries(parsed_queries, samples_per_stage=2)
    export_itemized_csv(parsed_queries, str(csv_file))
    console.print(f"[bold green]✓ Exported itemized search journey CSV with platform separation -> {csv_file}[/bold green]")

    export_matrix_csv(parsed_queries, str(matrix_csv_file))
    console.print(f"[bold green]✓ Exported search journey matrix CSV -> {matrix_csv_file}[/bold green]")

    out.write_text(json.dumps(sampled_batch, indent=2, ensure_ascii=False))
    console.print(f"[bold green]✓ Prepared {len(sampled_batch)} sampled batch audit queries -> {out}[/bold green]")

    table = Table(title=f"Reverse-Prompted AI Search Journey Taxonomy ({brand})")
    table.add_column("ID", justify="center", style="cyan")
    table.add_column("Platform", style="bold blue")
    table.add_column("Stage", style="bold magenta")
    table.add_column("Prompt Query Preview", style="white")

    for q in sampled_batch:
        table.add_row(str(q.get("id", "")), q.get("platform", "All"), q.get("stage", ""), q.get("q", "")[:60] + "...")
    console.print(table)


@app.command("pipeline")
def pipeline_cmd(
    brand: str = typer.Option(..., "--brand", "-b", help="Target brand name (e.g. 'Electrum', 'Jotun')"),
    category: str = typer.Option(..., "--category", "-c", help="Category or product line (e.g. 'motor listrik', 'cat interior')"),
    competitors: str = typer.Option("Competitor A, Competitor B", "--competitors", "-comp", help="Comma-separated competitors"),
    geo: str = typer.Option("Indonesia", "--geo", "-g", help="Target geography & language context"),
    platform: str = typer.Option("chatgpt,gemini", "--platform", "-p", help="Target AI platform(s) (e.g. 'chatgpt,gemini')"),
    account: Optional[str] = typer.Option(None, "--account", "-a", help="Specific account profile identifier"),
    out_dir: Path = typer.Option(Path("."), "--out-dir", "-o", help="Output directory for generated files"),
    year: int = typer.Option(2026, "--year", "-y", help="Target year"),
    headless: bool = typer.Option(True, "--headless/--headed", help="Run browser headlessly"),
):
    """Execute the complete Step 1.5 end-to-end audit pipeline (Prompts + CSVs + Batch Audit + Metrics)."""
    from scripts.run_audit_pipeline import run_pipeline
    run_pipeline(
        brand=brand,
        category=category,
        competitors=competitors,
        geo=geo,
        platform=platform,
        account=account,
        out_dir=str(out_dir),
        headless=headless,
        year=year,
    )


@app.command()
def audit(
    platform: str = typer.Option(..., "--platform", "-p", help="Target AI platform (chatgpt, gemini)"),
    query: str = typer.Option(..., "--query", "-q", help="Search prompt query"),
    brand: Optional[str] = typer.Option(None, "--brand", "-b", help="Brand name to check for citations"),
    account: Optional[str] = typer.Option(None, "--account", "-a", help="Specific account to use"),
    headless: bool = typer.Option(True, "--headless/--headed", help="Run browser in headless mode"),
):
    """Run a single audit query headlessly and display results."""
    console.print(f"[cyan]Executing audit on {platform} for: '{query}'...[/cyan]")
    mgr = SessionManager()
    driver = get_driver(platform, mgr)
    result = driver.run_query(query=query, brand_name=brand, account_name=account, headless=headless)

    table = Table(title=f"GEO Audit Result - {platform.upper()}")
    table.add_column("Field", style="bold")
    table.add_column("Value")

    table.add_row("Account", result.account_id)
    table.add_row("Brand Cited", "[green]YES[/green]" if result.brand_cited else "[red]NO[/red]")
    table.add_row("Citations Found", str(len(result.citations)))
    table.add_row("Duration", f"{result.duration_seconds}s")
    table.add_row("Response Preview", result.raw_response_text[:300] + "...")

    console.print(table)

    if result.citations:
        console.print("\n[bold]Extracted Sources:[/bold]")
        for c in result.citations:
            console.print(f" • [blue]{c.domain}[/blue] - {c.url}")


@app.command()
def batch(
    file: Path = typer.Option(..., "--file", "-f", help="JSON file with list of {id, q, brand}"),
    platform: str = typer.Option(..., "--platform", "-p", help="Target platform (chatgpt, gemini)"),
    out: Path = typer.Option(Path("results.json"), "--out", "-o", help="Output JSON results file"),
    headless: bool = typer.Option(True, "--headless/--headed", help="Run browser in headless mode"),
):
    """Execute a batch sweep of audit queries from a JSON input file."""
    if not file.exists():
        console.print(f"[red]Error: Input file {file} not found.[/red]")
        raise typer.Exit(1)

    queries = json.loads(file.read_text())
    results = []
    mgr = SessionManager()
    driver = get_driver(platform, mgr)

    for item in queries:
        q = item.get("q") or item.get("query")
        brand = item.get("brand")
        console.print(f"[yellow]Running: {q}[/yellow]")
        res = driver.run_query(query=q, brand_name=brand, headless=headless)
        results.append(res.model_dump(mode="json"))

    out.write_text(json.dumps(results, indent=2))
    console.print(f"[green]✓ Batch audit complete! Results saved to {out}[/green]")


if __name__ == "__main__":
    app()
