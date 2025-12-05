"""Command line entrypoints using Typer."""
from __future__ import annotations

import json
from datetime import date, timedelta
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


def resolve_location_id(location_id: Optional[str], client: ZenotiApiClient) -> str:
    resolved = location_id or client.config.center_id
    if not resolved:
        raise typer.BadParameter("location_id is required; set ZENOTI_CENTER_ID or pass it as an argument.")
    return resolved


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
    location_id: Optional[str] = typer.Argument(None, help="Location/center identifier."),
    start_date: Optional[str] = typer.Option(None, help="Start date (YYYY-MM-DD). Defaults to today."),
    end_date: Optional[str] = typer.Option(None, help="End date (YYYY-MM-DD). Defaults to start_date + 1 day."),
    include_no_show_cancel: bool = typer.Option(False, help="Include No Show and Cancel statuses."),
    therapist_id: Optional[str] = typer.Option(None, help="Filter by therapist id."),
    templates_path: Optional[Path] = typer.Option(None),
):
    """List appointments for a location (uses appointments endpoint)."""
    store, client = get_services(templates_path)
    resolved_location = resolve_location_id(location_id, client)
    try:
        start = date.fromisoformat(start_date) if start_date else date.today()
    except ValueError:
        raise typer.BadParameter("start_date must be in YYYY-MM-DD format")

    try:
        end = date.fromisoformat(end_date) if end_date else (start + timedelta(days=1))
    except ValueError:
        raise typer.BadParameter("end_date must be in YYYY-MM-DD format")

    if end <= start:
        raise typer.BadParameter("end_date must be after start_date")
    if (end - start).days > 7:
        raise typer.BadParameter("The range between start_date and end_date cannot exceed 7 days")
    appointments = InvoiceManager(client, store).list(
        resolved_location,
        start_date=start.isoformat(),
        end_date=end.isoformat(),
        include_no_show_cancel=include_no_show_cancel,
        therapist_id=therapist_id,
    )
    typer.echo(json.dumps(appointments, indent=2))


@app.command()
def create_invoice(
    template_name: str,
    location_id: Optional[str] = typer.Option(None, "--location-id", "-l", help="Location/center identifier."),
    overrides_file: Optional[Path] = typer.Option(None, help="Optional JSON file with overrides."),
    templates_path: Optional[Path] = typer.Option(None),
):
    """Create an invoice from a stored template."""
    store, client = get_services(templates_path)
    resolved_location = resolve_location_id(location_id, client)
    overrides = json.loads(overrides_file.read_text()) if overrides_file else None
    invoice = InvoiceManager(client, store).create_from_template(resolved_location, template_name, overrides=overrides)
    typer.echo(json.dumps(invoice, indent=2))


@app.command()
def book_appointment(
    template_name: str,
    location_id: Optional[str] = typer.Option(None, "--location-id", "-l", help="Location/center identifier."),
    overrides_file: Optional[Path] = typer.Option(None, help="Optional JSON file with overrides."),
    templates_path: Optional[Path] = typer.Option(None),
):
    """Book an appointment from a template."""
    store, client = get_services(templates_path)
    resolved_location = resolve_location_id(location_id, client)
    overrides = json.loads(overrides_file.read_text()) if overrides_file else None
    booking = BookingManager(client, store).book_from_template(resolved_location, template_name, overrides=overrides)
    typer.echo(json.dumps(booking, indent=2))


if __name__ == "__main__":
    app()
