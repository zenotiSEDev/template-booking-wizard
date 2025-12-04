"""Optional Streamlit UI for managing invoices and templates."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import streamlit as st

from .booking import BookingManager
from .client import ZenotiApiClient
from .config import ZenotiConfig
from .invoices import InvoiceManager
from .templates import Template, TemplateStore


def load_services(templates_path: Optional[Path] = None):
    config = ZenotiConfig.from_env()
    if templates_path:
        config.templates_path = templates_path
    store = TemplateStore(config.templates_path)
    client = ZenotiApiClient(config)
    return store, client


def main():
    st.title("Zenoti Booking & Invoice Helper")

    templates_path = st.text_input("Templates file", value=str(Path.cwd() / "data" / "templates.json"))
    store, client = load_services(Path(templates_path))
    invoice_manager = InvoiceManager(client, store)
    booking_manager = BookingManager(client, store)

    tab_templates, tab_invoices, tab_booking = st.tabs(["Templates", "Invoices", "Bookings"])

    with tab_templates:
        st.subheader("Stored templates")
        templates = store.list()
        st.json([template.__dict__ for template in templates])

        with st.form("add_template"):
            st.write("Add a new template")
            name = st.text_input("Name")
            payload_text = st.text_area("Payload (JSON)", value="{}")
            submitted = st.form_submit_button("Save")
            if submitted:
                try:
                    payload = json.loads(payload_text)
                    store.add(Template(name=name, payload=payload))
                    st.success(f"Added template '{name}'.")
                except Exception as exc:  # noqa: BLE001
                    st.error(str(exc))

    with tab_invoices:
        st.subheader("Create invoice from template")
        location_id = st.text_input("Location ID", key="invoice_location")
        template_name = st.selectbox("Template", [t.name for t in store.list()]) if store.list() else None
        overrides_text = st.text_area("Overrides (JSON)", value="{}", key="invoice_overrides")
        if st.button("Create invoice"):
            try:
                overrides = json.loads(overrides_text) if overrides_text.strip() else None
                response = invoice_manager.create_from_template(location_id, template_name, overrides=overrides)
                st.json(response)
            except Exception as exc:  # noqa: BLE001
                st.error(str(exc))

    with tab_booking:
        st.subheader("Book appointment from template")
        location_id = st.text_input("Location ID", key="booking_location")
        template_name = (
            st.selectbox("Template", [t.name for t in store.list()], key="booking_template") if store.list() else None
        )
        overrides_text = st.text_area("Overrides (JSON)", value="{}", key="booking_overrides")
        if st.button("Book appointment"):
            try:
                overrides = json.loads(overrides_text) if overrides_text.strip() else None
                response = booking_manager.book_from_template(location_id, template_name, overrides=overrides)
                st.json(response)
            except Exception as exc:  # noqa: BLE001
                st.error(str(exc))


if __name__ == "__main__":
    main()
