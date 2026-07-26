"""PromptForge CLI entrypoint."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .archive import extract_zip_stripped
from .client import ApiError, Client
from .config import DEFAULT_API_URL, config_file, load_config, save_config

# Windows consoles default to cp1252, which can't encode prompt/kit text (or our
# status glyphs). Prefer UTF-8 and never crash on an odd character.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    except (AttributeError, ValueError):  # pragma: no cover - non-reconfigurable stream
        pass

app = typer.Typer(
    help="PromptForge — pull starter kits and prompts from your terminal.",
    no_args_is_help=True,
    add_completion=False,
)
kits_app = typer.Typer(help="Browse and pull starter kits.", no_args_is_help=True)
prompts_app = typer.Typer(help="Search and fetch prompts.", no_args_is_help=True)
app.add_typer(kits_app, name="kits")
app.add_typer(prompts_app, name="prompts")

console = Console()


def _fail(message: str) -> None:
    console.print(f"[red][x][/red] {message}")
    raise typer.Exit(1)


def _client() -> Client:
    return Client()


# --- Auth -------------------------------------------------------------------
@app.command()
def login(
    api_url: str = typer.Option(None, "--api-url", help="PromptForge base URL"),
    api_key: str = typer.Option(None, "--api-key", help="Your API key"),
) -> None:
    """Save your API key after verifying it against the server."""
    cfg = load_config()
    api_url = api_url or typer.prompt(
        "PromptForge API URL", default=str(cfg["api_url"]) or DEFAULT_API_URL
    )
    api_key = api_key or typer.prompt(
        "API key (Settings → API keys)", hide_input=True
    )
    try:
        me = Client(api_url, api_key).get("/me")
    except ApiError as exc:
        _fail(str(exc))
    save_config(api_url, api_key)
    console.print(
        f"[green][ok][/green] Logged in as [bold]@{me.get('username')}[/bold]. "
        f"Saved to {config_file()}"
    )


@app.command()
def whoami() -> None:
    """Show who the configured key belongs to."""
    try:
        me = _client().get("/me")
    except ApiError as exc:
        _fail(str(exc))
    console.print(
        f"[bold]@{me.get('username')}[/bold] "
        f"{me.get('full_name') or ''} ({me.get('role')})"
    )


# --- Kits -------------------------------------------------------------------
@kits_app.command("list")
def kits_list(
    category: str = typer.Option(None, "--category", "-c", help="Filter by kit category"),
) -> None:
    """List starter kits."""
    try:
        page = _client().get("/templates", params={"category": category} if category else None)
    except ApiError as exc:
        _fail(str(exc))
    items = page.get("items", [])
    if not items:
        console.print("No starter kits found.")
        return
    table = Table(show_lines=False)
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("Name", style="bold")
    table.add_column("Category")
    table.add_column("Stack")
    table.add_column("Prompts", justify="right")
    for kit in items:
        table.add_row(
            kit["project_id"],
            kit["name"],
            kit.get("category") or "-",
            kit.get("stack") or "-",
            str(kit["prompt_count"]),
        )
    console.print(table)
    console.print("\nPull one with: [cyan]promptforge kits pull <ID>[/cyan]")


@kits_app.command("pull")
def kits_pull(
    project_id: str = typer.Argument(..., help="Kit ID (from 'kits list')"),
    ref: str = typer.Option("main", "--ref", help="Branch, tag, or commit"),
    dest: str = typer.Option(None, "--dir", "-d", help="Target folder (default: kit slug)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite a non-empty folder"),
) -> None:
    """Pull a kit's codebase into a local folder."""
    client = _client()
    try:
        manifest = client.get(f"/templates/{project_id}")
    except ApiError as exc:
        _fail(str(exc))

    target = Path(dest or manifest["slug"]).resolve()
    if target.exists() and any(target.iterdir()) and not force:
        _fail(f"{target} isn't empty. Re-run with --force to overwrite.")

    console.print(f"Pulling [bold]{manifest['name']}[/bold] -> {target}")
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "kit.zip"
        try:
            client.download(f"/templates/{project_id}/download?ref={ref}", zip_path)
            extract_zip_stripped(zip_path, target)
        except ApiError as exc:
            _fail(str(exc))
        except Exception as exc:  # noqa: BLE001 - surface unzip errors cleanly
            _fail(f"Couldn't unpack the archive: {exc}")

    _write_prompts_doc(target, manifest)
    console.print(
        f"[green][ok][/green] Pulled {manifest['prompt_count']} prompt(s) worth of scaffolding."
    )
    console.print("  See [bold]PROMPTFORGE.md[/bold] for the prompts behind this kit.")
    if manifest.get("setup_command"):
        console.print(f"  Next: [cyan]{manifest['setup_command']}[/cyan]")


def _write_prompts_doc(target: Path, manifest: dict) -> None:
    """Drop a PROMPTFORGE.md listing the prompts that built this kit."""
    lines = [
        f"# {manifest['name']} — prompts",
        "",
        (manifest.get("description") or "").strip(),
        "",
        f"Pulled from PromptForge. Stack: {manifest.get('stack') or 'n/a'}.",
        "",
        "Fetch any prompt's full content with:",
        "```",
        "promptforge prompts get <PROMPT_ID>",
        "```",
        "",
    ]
    for module in manifest.get("modules", []):
        lines.append(f"## {module['name']}")
        for comp in module.get("components", []):
            lines.append(f"### {comp['name']}")
            for prompt in comp.get("prompts", []):
                lines.append(f"- {prompt['title']}  \n  `{prompt['id']}`")
        lines.append("")
    (target / "PROMPTFORGE.md").write_text("\n".join(lines), encoding="utf-8")


# --- Prompts ----------------------------------------------------------------
@prompts_app.command("search")
def prompts_search(
    query: str = typer.Argument(..., help="Search text"),
    limit: int = typer.Option(10, "--limit", "-n"),
) -> None:
    """Search published prompts."""
    try:
        page = _client().get("/prompts", params={"q": query, "size": limit})
    except ApiError as exc:
        _fail(str(exc))
    items = page.get("items", [])
    if not items:
        console.print("No prompts matched.")
        return
    table = Table()
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("Title", style="bold")
    table.add_column("Type")
    for prompt in items:
        table.add_row(prompt["id"], prompt["title"], prompt.get("prompt_type") or "-")
    console.print(table)


@prompts_app.command("get")
def prompts_get(prompt_id: str = typer.Argument(..., help="Prompt ID")) -> None:
    """Print a prompt's full content."""
    try:
        prompt = _client().get(f"/prompts/{prompt_id}")
    except ApiError as exc:
        _fail(str(exc))
    console.print(f"[bold]{prompt['title']}[/bold]")
    if prompt.get("description"):
        console.print(f"[dim]{prompt['description']}[/dim]")
    console.print()
    console.print(prompt["content"])


if __name__ == "__main__":
    app()
