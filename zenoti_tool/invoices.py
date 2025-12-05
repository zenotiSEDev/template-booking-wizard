"""Invoice utilities built on top of the Zenoti client."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .client import ZenotiApiClient
from .templates import TemplateStore


@dataclass
class InvoiceManager:
    client: ZenotiApiClient
    templates: TemplateStore

    def list(
        self,
        location_id: str,
        *,
        start_date: str,
        end_date: str,
        include_no_show_cancel: bool = False,
        therapist_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Use appointments list endpoint instead of invoices.
        return self.client.list_appointments(
            location_id,
            start_date=start_date,
            end_date=end_date,
            include_no_show_cancel=include_no_show_cancel,
            therapist_id=therapist_id,
        )

    def create_from_template(
        self, location_id: str, template_name: str, *, overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        payload = template.payload.copy()
        if overrides:
            payload.update(overrides)
        return self.client.create_invoice(location_id, payload)
