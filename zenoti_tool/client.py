"""Zenoti API client with token management."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import requests

from .config import ZenotiConfig


@dataclass
class TokenInfo:
    access_token: str
    expires_at: float

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "TokenInfo":
        expires_in = data.get("expires_in", 3600)
        return cls(
            access_token=data["access_token"],
            expires_at=time.time() + expires_in - 60,  # Refresh 1 minute early
        )

    def is_valid(self) -> bool:
        return time.time() < self.expires_at


@dataclass
class ZenotiApiClient:
    """Simple Zenoti API client with automatic token refresh."""

    config: ZenotiConfig
    session: requests.Session = field(default_factory=requests.Session)
    token: Optional[TokenInfo] = None

    def _ensure_token(self) -> str:
        if self.token and self.token.is_valid():
            return self.token.access_token

        response = self.session.post(
            self.config.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.config.app_id,
                "client_secret": self.config.app_secret,
            },
            headers=self.config.as_headers(),
            timeout=30,
        )
        response.raise_for_status()
        self.token = TokenInfo.from_response(response.json())
        return self.token.access_token

    def get_access_token(self, *, force_refresh: bool = False) -> str:
        """Return a valid access token, refreshing if needed."""

        if force_refresh:
            self.token = None
        return self._ensure_token()

    def _headers(self) -> Dict[str, str]:
        token = self._ensure_token()
        headers = self.config.as_headers()
        headers.update({"Authorization": f"Bearer {token}"})
        return headers

    def request(
        self, method: str, path: str, *, params: Optional[Dict[str, Any]] = None, json: Any = None
    ) -> requests.Response:
        url = f"{self.config.base_url}/{path.lstrip('/')}"
        response = self.session.request(
            method,
            url,
            params=params,
            json=json,
            headers=self._headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response

    def list_invoices(self, location_id: str) -> Dict[str, Any]:
        response = self.request("GET", f"v1/locations/{location_id}/invoices")
        return response.json()

    def create_invoice(self, location_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self.request("POST", f"v1/locations/{location_id}/invoices", json=payload)
        return response.json()

    def book_appointment(self, location_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self.request("POST", f"v1/locations/{location_id}/appointments", json=payload)
        return response.json()
