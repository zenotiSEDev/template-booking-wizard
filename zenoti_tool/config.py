"""Configuration utilities for the Zenoti tooling."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class ZenotiConfig:
    """Configuration values derived from environment variables.

    Attributes:
        base_url: Base URL for the Zenoti API.
        app_id: OAuth client identifier / application id.
        app_secret: OAuth client secret / application secret.
        api_key: API key used for Zenoti authentication headers.
        token_url: OAuth token endpoint.
        templates_path: Path to the JSON file storing appointment templates.
        center_id: Optional default location/center identifier.
        account_name: Optional account/tenant identifier for password grant.
        user_name: Optional username for password grant.
        password: Optional password for password grant.
        device_id: Optional device identifier for password grant.
    """

    base_url: str
    app_id: str
    app_secret: str
    api_key: str
    token_url: str
    templates_path: Path
    center_id: Optional[str] = None
    account_name: Optional[str] = None
    user_name: Optional[str] = None
    password: Optional[str] = None
    device_id: Optional[str] = None

    @classmethod
    def from_env(
        cls,
        *,
        base_url_var: str = "ZENOTI_BASE_URL",
        app_id_var: str = "ZENOTI_APP_ID",
        app_secret_var: str = "ZENOTI_APP_SECRET",
        api_key_var: str = "ZENOTI_API_KEY",
        token_url_var: str = "ZENOTI_TOKEN_URL",
        templates_path_var: str = "ZENOTI_TEMPLATES_PATH",
        default_templates_path: Optional[Path] = None,
        legacy_client_id_var: str = "ZENOTI_CLIENT_ID",
        legacy_client_secret_var: str = "ZENOTI_CLIENT_SECRET",
        center_id_var: str = "ZENOTI_CENTER_ID",
        account_name_var: str = "ZENOTI_ACCOUNT_ID",
        user_name_var: str = "ZENOTI_USERNAME",
        password_var: str = "ZENOTI_PASSWORD",
        device_id_var: str = "ZENOTI_DEVICE_ID",
    ) -> "ZenotiConfig":
        """Create configuration from environment variables.

        Raises:
            EnvironmentError: If required environment variables are missing.
        """

        load_dotenv(Path.cwd() / ".env.local", override=False)

        base_url = os.environ.get(base_url_var)
        app_id = os.environ.get(app_id_var) or os.environ.get(legacy_client_id_var)
        app_secret = os.environ.get(app_secret_var) or os.environ.get(legacy_client_secret_var)
        api_key = os.environ.get(api_key_var)
        token_url = os.environ.get(token_url_var)
        templates_path_str = os.environ.get(templates_path_var)
        center_id = os.environ.get(center_id_var)
        account_name = os.environ.get(account_name_var)
        user_name = os.environ.get(user_name_var)
        password = os.environ.get(password_var)
        device_id = os.environ.get(device_id_var)

        if not default_templates_path:
            default_templates_path = Path.cwd() / "data" / "templates.json"

        missing = [
            name
            for name, value in {
                base_url_var: base_url,
                app_id_var: app_id,
                app_secret_var: app_secret,
                token_url_var: token_url,
                account_name_var: account_name,
                user_name_var: user_name,
                password_var: password,
            }.items()
            if not value
        ]
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        base_url = re.sub(r"/v\d+$", "", base_url.rstrip("/"))

        templates_path = Path(templates_path_str) if templates_path_str else default_templates_path
        templates_path.parent.mkdir(parents=True, exist_ok=True)

        return cls(
            base_url=base_url,
            app_id=app_id,
            app_secret=app_secret,
            api_key=api_key,
            token_url=token_url,
            templates_path=templates_path,
            center_id=center_id,
            account_name=account_name,
            user_name=user_name,
            password=password,
            device_id=device_id,
        )

    def as_headers(self) -> dict:
        """Return base headers for Zenoti API requests."""

        return {
            "Accept": "application/json",
            "Zenoti-Api-Key": self.api_key,
            "X-API-Key": self.api_key,
        }
