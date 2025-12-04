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
   # Optional: location of the templates store
   ZENOTI_TEMPLATES_PATH="/path/to/templates.json"
   ```
   Values already in the environment take precedence over `.env.local`.

## Fetch an auth token
Use the Typer CLI to confirm credentials and fetch an access token (via `python main.py` or `python -m zenoti_tool.cli`):
```bash
python main.py auth-token --mask False
```
To keep the token masked (default):
```bash
python main.py auth-token
```

## List invoices (defaults to "Open")
```bash
python main.py list-invoices <LOCATION_ID>
```
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
python main.py create-invoice <LOCATION_ID> "My Invoice" --overrides-file overrides.json
```
`overrides.json` is optional and merged into the stored template payload.

## Book an appointment from a template
```bash
python main.py book-appointment <LOCATION_ID> "My Appointment" --overrides-file overrides.json
```

## Optional Streamlit UI
If you prefer a UI, run:
```bash
streamlit run zenoti_tool/ui.py
```
This exposes template management plus invoice and booking actions via a web interface.
