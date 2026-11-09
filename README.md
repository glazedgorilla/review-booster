# Review Booster

AI-powered Google review helper. Store owners create a QR code, customers scan it, rate and add a quick note, and Gemini turns it into a polished review. Flask + Gemini free tier, with an offline fallback.

**Live demo:** (https://review-booster-m0b1.onrender.com)  (may take ~1 minute to wake up)

## Run it yourself (free, no credit card)

1. Install Python 3.9+
2. Clone and install:
       git clone https://github.com/glazedgorilla/review-booster.git
       cd review-booster
       python -m venv venv
       venv\Scripts\activate        (macOS/Linux: source venv/bin/activate)
       pip install -r requirements.txt
3. Copy `.env.example` to `.env` and add your own free Gemini API key
   from https://aistudio.google.com/apikey
4. Start it: `python app.py`, then open http://localhost:5050

No key? It still works with mock reviews.

## Tech
Python, Flask, Gemini API, qrcode + Pillow, Tailwind CSS
