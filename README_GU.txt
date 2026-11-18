# NIFTY SCANNER PRO V1.0

A Streamlit dashboard prototype for a NIFTY 50 5-minute option scanner.

## What is included
- Overview dashboard
- Current and next expiry tabs
- Top candidate tables (illustrative sample data only)
- Manual data-entry scoring prototype
- Placeholder Entry / Stop Loss / Target columns
- Risk and live-integration checklist

## Important
This V1.0 does NOT connect to Groww. It does NOT display live prices. Sample data is illustrative and must not be used to trade. The candidate score is a screening prototype, not a validated strategy. Stop loss and targets are placeholders, not recommendations. No orders are placed.

Groww API credentials must never be committed to source code or shared. Live integration should only be added after confirming current API entitlement, endpoint schemas, rate limits, authentication requirements and data licensing.

## Run locally
Python 3.10+ recommended:
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Cloud deployment outline
A Streamlit-compatible host can deploy this repository from GitHub. Keep secrets in the host's Secrets manager. A scheduled worker / scheduler is required for reliable 5-minute scans; a dashboard page alone does not run continuously in the background.

## Next version
- Confirm Groww live-data subscription.
- Validate current Groww API docs and payload schemas.
- Add secure TOTP/access-token refresh.
- Add live option-chain + historical candle ingestion.
- Add completed-candle volume spike calculations.
- Add current + next expiry instrument selection.
- Add scheduled scanning, cache/database, logs and stale-data guards.
- Paper-trade and backtest before displaying actionable candidates.
