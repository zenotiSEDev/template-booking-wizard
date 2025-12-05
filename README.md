# Zenoti Booking & Invoice Tooling

CLI and optional Streamlit UI for managing Zenoti invoice and appointment workflows with JSON-backed templates.

## Quickstart
1. Install dependencies (Python 3.11+ recommended):
   ```bash
   pip install -r requirements.txt
   ```
2. Provide required credentials via environment variables or an `.env.local` file in the project root. Example `.env.local`:
   ```bash
   ZENOTI_BASE_URL="https://your-subdomain.zenoti.com"
   ZENOTI_TOKEN_URL="https://your-subdomain.zenoti.com/oauth/token"
   ZENOTI_APP_ID="your-app-id"
   ZENOTI_APP_SECRET="your-app-secret"
   ZENOTI_API_KEY="your-api-key"
   ZENOTI_ACCOUNT_ID="your-account"
   ZENOTI_USERNAME="your-username"
   ZENOTI_PASSWORD="your-password"
   # Optional: stable device identifier for password grant (else leave empty)
   ZENOTI_DEVICE_ID="your-device-id"
   # Optional: default location/center id used when not passed on the CLI
   ZENOTI_CENTER_ID="your-center-id"
   # Optional: location of the templates store
   ZENOTI_TEMPLATES_PATH="/path/to/templates.json"
   ```
   Values already in the environment take precedence over `.env.local`.
   Note: `ZENOTI_BASE_URL` should be the root domain (e.g., `https://your-subdomain.zenoti.com`); any trailing `/v1` is stripped automatically.

## Fetch an auth token
Use the Typer CLI to confirm credentials and fetch an access token (via `python main.py` or `python -m zenoti_tool.cli`):
```bash
python main.py auth-token --no-mask
```
To keep the token masked (default):
```bash
python main.py auth-token
```

## List invoices (defaults to "Open")
```bash
python main.py list-invoices <LOCATION_ID>
# or rely on ZENOTI_CENTER_ID:
python main.py list-invoices
```
The client first fetches a token via `POST https://api.zenoti.com/v1/tokens` with:
```
Headers:
  X-Application-Id: <ZENOTI_APP_ID>
Body (JSON):
  {
    "account_name": "<ZENOTI_ACCOUNT_ID>",
    "user_name": "<ZENOTI_USERNAME>",
    "password": "<ZENOTI_PASSWORD>",
    "grant_type": "password",
    "app_id": "<ZENOTI_APP_ID>",
    "app_secret": "<ZENOTI_APP_SECRET>",
    "device_id": "<ZENOTI_DEVICE_ID>"  // optional
  }
```
Requests then use `Authorization: Bearer <token>` plus `X-Application-Id`, `X-API-Key`/`Zenoti-Api-Key`, and optional `X-Center-Id`.
To return all invoices (no status filter):
```bash
python main.py list-invoices <LOCATION_ID> --status all
```
To request another status value (e.g., Closed):
```bash
python main.py list-invoices <LOCATION_ID> --status Closed
```

## Manage templates
Templates are stored in `data/templates.json` by default.
- List: `python main.py list-templates`
- Add from file: `python main.py add-template "My Invoice" payload.json`
- Remove: `python main.py remove-template "My Invoice"`

## Create an invoice from a template
```bash
python main.py create-invoice --location-id <LOCATION_ID> "My Invoice" --overrides-file overrides.json
# or with ZENOTI_CENTER_ID:
python main.py create-invoice "My Invoice" --overrides-file overrides.json
```
`overrides.json` is optional and merged into the stored template payload.

## Book an appointment from a template
```bash
python main.py book-appointment --location-id <LOCATION_ID> "My Appointment" --overrides-file overrides.json
# or with ZENOTI_CENTER_ID:
python main.py book-appointment "My Appointment" --overrides-file overrides.json
```

## Optional Streamlit UI
If you prefer a UI, run:
```bash
streamlit run zenoti_tool/ui.py
```
This exposes template management plus invoice and booking actions via a web interface.
