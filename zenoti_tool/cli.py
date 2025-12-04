"""Command line entrypoints using Typer."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .booking import BookingManager
from .client import ZenotiApiClient
from .config import ZenotiConfig
from .invoices import InvoiceManager
from .templates import Template, TemplateStore

app = typer.Typer(help="Utilities for Zenoti invoice and booking workflows.")


def get_services(templates_path: Optional[Path] = None):
    config = ZenotiConfig.from_env()
    if templates_path:
        config.templates_path = templates_path
    template_store = TemplateStore(config.templates_path)
    client = ZenotiApiClient(config)
    return template_store, client


@app.command()
def auth_token(mask: bool = typer.Option(True, help="Mask the token output for safety.")):
    """Fetch and display an access token using configured credentials."""

    _, client = get_services()
    token = client.get_access_token(force_refresh=True)
    if mask:
        masked = f"{token[:6]}...{token[-4:]}" if len(token) > 10 else "***"
        typer.echo(f"Token acquired (masked): {masked}")
    else:
        typer.echo(token)


@app.command()
def list_templates(templates_path: Optional[Path] = typer.Option(None, help="Path to templates file.")):
    """List available templates."""
    store, _ = get_services(templates_path)
    for template in store.list():
        typer.echo(f"- {template.name}")


@app.command()
def add_template(
    name: str,
    payload_file: Path = typer.Argument(..., exists=True, readable=True, help="Path to JSON payload."),
    templates_path: Optional[Path] = typer.Option(None, help="Path to templates file."),
):
    """Add a template from a JSON file."""
    store, _ = get_services(templates_path)
    payload = json.loads(payload_file.read_text())
    store.add(Template(name=name, payload=payload))
    typer.echo(f"Added template '{name}'.")


@app.command()
def remove_template(name: str, templates_path: Optional[Path] = typer.Option(None, help="Path to templates file.")):
    """Remove a template by name."""
    store, _ = get_services(templates_path)
    store.remove(name)
    typer.echo(f"Removed template '{name}'.")


@app.command()
def list_invoices(
    location_id: str,
    status: Optional[str] = typer.Option(
        "open",
        help="Invoice status filter. Use 'all' to return every invoice.",
    ),
    templates_path: Optional[Path] = typer.Option(None),
):
    """List invoices for a location."""
    store, client = get_services(templates_path)
    status_filter = None if status is None or status.lower() == "all" else status
    invoices = InvoiceManager(client, store).list(location_id, status=status_filter)
    typer.echo(json.dumps(invoices, indent=2))


@app.command()
def create_invoice(
    location_id: str,
    template_name: str,
    overrides_file: Optional[Path] = typer.Option(None, help="Optional JSON file with overrides."),
    templates_path: Optional[Path] = typer.Option(None),
):
    """Create an invoice from a stored template."""
    store, client = get_services(templates_path)
    overrides = json.loads(overrides_file.read_text()) if overrides_file else None
    invoice = InvoiceManager(client, store).create_from_template(location_id, template_name, overrides=overrides)
    typer.echo(json.dumps(invoice, indent=2))


@app.command()
def book_appointment(
    location_id: str,
    template_name: str,
    overrides_file: Optional[Path] = typer.Option(None, help="Optional JSON file with overrides."),
    templates_path: Optional[Path] = typer.Option(None),
):
    """Book an appointment from a template."""
    store, client = get_services(templates_path)
    overrides = json.loads(overrides_file.read_text()) if overrides_file else None
    booking = BookingManager(client, store).book_from_template(location_id, template_name, overrides=overrides)
    typer.echo(json.dumps(booking, indent=2))


if __name__ == "__main__":
    app()
