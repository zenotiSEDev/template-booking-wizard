"""Booking helpers built on top of templates."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .client import ZenotiApiClient
from .templates import Template, TemplateStore


@dataclass
class BookingManager:
    client: ZenotiApiClient
    templates: TemplateStore

    def book_from_template(
        self, location_id: str, template_name: str, *, overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        payload = template.payload.copy()
        if overrides:
            payload.update(overrides)
        return self.client.book_appointment(location_id, payload)

    def save_booking_template(self, name: str, payload: Dict[str, Any]) -> None:
        self.templates.add(Template(name=name, payload=payload))
