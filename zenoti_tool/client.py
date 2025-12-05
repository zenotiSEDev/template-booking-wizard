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
        credentials = data.get("credentials") or {}
        access_token = data.get("access_token") or credentials.get("access_token")
        expires_in = data.get("expires_in", credentials.get("expires_in", 3600))
        if not access_token:
            raise KeyError("access_token")
        return cls(
            access_token=access_token,
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
            json={
                "account_name": self.config.account_name,
                "user_name": self.config.user_name,
                "password": self.config.password,
                "grant_type": "password",
                "app_id": self.config.app_id,
                "app_secret": self.config.app_secret,
                "device_id": self.config.device_id,
            },
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Application-Id": self.config.app_id,
            },
            timeout=30,
        )

        print("Token status:", response.status_code)
        print("Token body:", response.text)

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
        headers.update(
            {
                "Authorization": f"Bearer {token}",
                "X-Application-Id": self.config.app_id,
            }
        )
        if self.config.center_id:
            headers["X-Center-Id"] = self.config.center_id
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

    def list_appointments(
        self,
        location_id: str,
        *,
        start_date: str,
        end_date: str,
        include_no_show_cancel: bool = False,
        therapist_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "center_id": location_id,
            "start_date": start_date,
            "end_date": end_date,
            "include_no_show_cancel": str(include_no_show_cancel).lower(),
        }
        if therapist_id:
            params["therapist_id"] = therapist_id
        response = self.request("GET", "v1/appointments", params=params)
        return response.json()

    def create_invoice(self, location_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self.request("POST", f"v1/locations/{location_id}/invoices", json=payload)
        return response.json()

    def book_appointment(self, location_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self.request("POST", f"v1/locations/{location_id}/appointments", json=payload)
        return response.json()
