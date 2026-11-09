import base64
import io
import os
from urllib.parse import urlencode

import qrcode
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix

from mock_ai import mock_review

load_dotenv()

app = Flask(__name__)
# Lets Flask see the real https URL when behind cloudflared/ngrok/Render
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODELS = [m.strip() for m in os.getenv(
    "GEMINI_MODELS", "gemini-3.5-flash,gemini-3.1-flash-lite").split(",") if m.strip()]
TONES = ["Friendly", "Professional", "Concise"]

client = None
if API_KEY and API_KEY != "your_key_here":
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=API_KEY)
    except Exception as e:
        print("Gemini setup failed, using mock only:", e)


def build_review_link(value: str) -> str:
    """Accept a Place ID or a full Google review URL."""
    value = value.strip()
    if value.lower().startswith(("http://", "https://")):
        return value
    return f"https://search.google.com/local/writereview?placeid={value}"


def make_qr_data_uri(url: str) -> str:
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def ai_review(store, rating, notes, tone):
    """Returns (text, source). Falls back to mock on any error or rate limit."""
    if client:
        prompt = (
            f"Write a Google review for a business called '{store or 'a local business'}'.\n"
            f"Star rating: {rating} out of 5.\n"
            f"Customer's notes: {notes}\n"
            f"Tone: {tone}.\n\n"
            "Rules: 2-3 sentences, first person, sounds like a real customer, "
            "use ONLY details from the notes (do not invent facts), "
            "match the sentiment of the star rating, no hashtags or emojis. "
            "Output only the review text."
        )
        for model in MODELS:
            try:
                resp = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.8),
                )
                text = (resp.text or "").strip().strip('"')
                if text:
                    return text, f"gemini:{model}"
            except Exception as e:
                print(f"[{model}] failed: {e}")
    return mock_review(store, rating, notes, tone), "mock"


@app.route("/", methods=["GET", "POST"])
def owner():
    ctx = {"qr": None, "error": None, "store": "", "value": ""}
    if request.method == "POST":
        store = request.form.get("store", "").strip()[:80]
        value = request.form.get("place", "").strip()
        ctx.update(store=store, value=value)
        if not value:
            ctx["error"] = "Please enter a Place ID or a Google review URL."
        else:
            link = build_review_link(value)
            base = os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/") or request.url_root.rstrip("/")
            customer_url = f"{base}/r?" + urlencode({"n": store, "g": link})
            ctx.update(qr=make_qr_data_uri(customer_url), customer_url=customer_url)
    return render_template("owner.html", **ctx)


@app.route("/r")
def customer():
    store = request.args.get("n", "")[:80]
    link = request.args.get("g", "")
    if not link.lower().startswith(("http://", "https://")):
        return "Invalid review link.", 400
    return render_template("review.html", store=store, link=link, tones=TONES)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    try:
        rating = max(1, min(5, int(data.get("rating", 5))))
    except (TypeError, ValueError):
        rating = 5
    notes = str(data.get("notes", "")).strip()[:300]
    tone = data.get("tone") if data.get("tone") in TONES else "Friendly"
    store = str(data.get("store", ""))[:80]
    if not notes:
        return jsonify(error="Please add a short note first."), 400
    text, source = ai_review(store, rating, notes, tone)
    return jsonify(review=text, source=source)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
