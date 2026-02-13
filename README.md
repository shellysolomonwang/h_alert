# Hermès Bag Email Alert App

This app monitors the Hermès women's bags page and emails subscribers whenever their selected bag appears to be in stock.

## Features
- Subscription form with bag selection and email.
- Polls Hermès every 30 seconds (configurable).
- Sends alerts via SMTP.
- Deduplicates repeated alerts for the same bag/email within a configurable time window.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Configuration
Set environment variables (or use `.env` with your process manager):
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_USE_TLS`, `EMAIL_FROM`
- `CHECK_INTERVAL_SECONDS` default `30`
- `DEDUP_MINUTES` default `120`

## Notes on drop timing
You mentioned drops usually happen on weekdays. This app runs continuously and checks every 30 seconds regardless of weekday/weekend, so it can catch both expected weekday drops and unexpected weekend drops.

## Run tests
```bash
pytest -q
```
