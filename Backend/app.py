import os
import time
import base64

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from google import genai

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "Frontend")

load_dotenv(os.path.join(BASE_DIR, ".env"))

MURF_API_KEY = os.getenv("MURF_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
# Free-tier quota is per model, so fall back through siblings when one is exhausted
FALLBACK_MODELS = [GEMINI_MODEL, "gemini-3.7-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]

if not MURF_API_KEY or not GEMINI_API_KEY:
    raise RuntimeError("Set MURF_API_KEY and GEMINI_API_KEY in Backend/.env (see .env.example)")

# Flask serves the Frontend folder too, so the whole app runs from one server
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

client = genai.Client(api_key=GEMINI_API_KEY)

PROMPTS = {
    "Summary": """
You are a professional tourist guide.
Provide a high-level overview of "{place}" in {language}.

Focus on:
- The historical significance
- Why the place is famous
- Key architectural or cultural highlights

Keep the explanation concise, engaging, and easy to follow.
Avoid excessive details and dates.
Limit the response to around 200 words.

Respond ONLY in {language}.
""",

    "Detailed": """
You are a professional tourist guide.
Provide a detailed and immersive explanation of "{place}" in {language}.

Cover:
- Historical background and timeline
- Architectural design and unique features
- Cultural importance and notable events
- Interesting facts and visitor insights

Explain concepts clearly and in a storytelling manner.
Include relevant details and examples to create a rich experience.
Limit the response to around 400 words.

Respond ONLY in {language}.
"""
}

REQUIRED_FIELDS = ["place", "answerType", "language", "voiceId", "locale"]


def generate_speech(text, voice_id, locale):
    url = "https://global.api.murf.ai/v1/speech/stream"
    headers = {
        "api-key": MURF_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "voice_id": voice_id,
        "text": text,
        "locale": locale,
        "model": "FALCON",
        "format": "MP3",
        "sampleRate": 24000,
        "channelType": "MONO"
    }

    response = requests.post(url, headers=headers, json=data, timeout=120)
    if response.status_code != 200:
        print(f"Murf error {response.status_code}: {response.text[:500]}", flush=True)
        return None
    return response.content


def generate_description(place, answer_type, language, attempts=3):
    prompt = PROMPTS[answer_type].format(place=place, language=language)
    last_error = None
    # 503 = momentary load (retry same model); 429 = daily quota gone (move to the next one)
    for model in FALLBACK_MODELS:
        for attempt in range(attempts):
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                return response.text
            except Exception as e:
                last_error = e
                message = str(e)
                if "429" in message:
                    print(f"{model} quota exhausted, trying next model", flush=True)
                    break
                if "503" in message:
                    if attempt < attempts - 1:
                        print(f"{model} busy, retrying ({attempt + 1}/{attempts})", flush=True)
                        time.sleep(2 * (attempt + 1))
                        continue
                    print(f"{model} still busy, trying next model", flush=True)
                    break
                raise
    raise last_error


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/generate-audio-guide", methods=["POST"])
def generate_audio_guide():
    data = request.get_json(silent=True) or {}
    missing = [field for field in REQUIRED_FIELDS if not data.get(field)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400
    if data["answerType"] not in PROMPTS:
        return jsonify({"error": f"answerType must be one of {list(PROMPTS)}"}), 400

    try:
        text_description = generate_description(data["place"], data["answerType"], data["language"])
    except Exception as e:
        print(f"Gemini error: {e}", flush=True)
        return jsonify({"error": f"Failed to generate description: {e}"}), 502

    try:
        audio_bytes = generate_speech(text_description, data["voiceId"], data["locale"])
    except requests.RequestException as e:
        print(f"Murf request failed: {e}", flush=True)
        audio_bytes = None

    # Still return the transcript if only the audio step failed
    return jsonify({
        "description": text_description,
        "audioBase64": base64.b64encode(audio_bytes).decode("utf-8") if audio_bytes else None
    })


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "true").lower() == "true",
    )
