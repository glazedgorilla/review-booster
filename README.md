# Review Booster

Flask app: store owners make a QR code; customers scan it, rate, add a note, and get an AI-polished Google review (Gemini free tier, with offline mock fallback).

## Run locally
    python3 -m venv venv
    source venv/bin/activate        # Windows: venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    cp .env.example .env            # add your Gemini key from https://aistudio.google.com/apikey
    python app.py                   # http://localhost:5050

## Phone testing (free)
    cloudflared tunnel --url http://localhost:5050
Open the printed trycloudflare.com URL on your laptop, then generate the QR code there.

## Deploy free on Render
Build: `pip install -r requirements.txt`  |  Start: `gunicorn app:app`
Env vars: GEMINI_API_KEY, GEMINI_MODELS, PUBLIC_BASE_URL (your onrender.com URL).

## Notes
- If reviews show source "mock", run `python check_models.py` and update GEMINI_MODELS.
- Only post reviews reflecting genuine customer experiences (Google policy).
