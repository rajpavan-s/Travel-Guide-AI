<<<<<<< HEAD
# Travel Guide

An AI-powered travel companion that creates spoken guides for destinations. Choose a featured landmark or search for a place, select a summary or detailed guide, and generate a transcript and audio in English, Hindi, Tamil, or Telugu.

## Features

- Browse featured Indian landmarks or search for another destination.
- Generate concise summaries or more detailed, story-style guides with Google Gemini.
- Listen to generated speech with Murf text-to-speech, with male and female voice options.
- Read the generated transcript in the app.
- Search results can show a destination image from Wikipedia when one is available.
- Responsive frontend built with HTML, JavaScript, and Tailwind CSS.

## Tech stack

- **Frontend:** HTML, CSS, JavaScript, Tailwind CSS
- **Backend:** Python, Flask, Flask-CORS
- **AI text generation:** Google Gemini (`google-genai`)
- **Text-to-speech:** Murf API
- **Deployment configuration:** Netlify (frontend) and Render (backend)

## Project structure

```text
.
├── Backend/
│   ├── app.py
│   └── requirements.txt
├── Frontend/
│   ├── config.js
│   ├── index.html
│   └── index.js
├── netlify.toml
└── render.yaml
```

## Run locally

### Prerequisites

- Python 3
- A Google Gemini API key
- A Murf API key

### Install dependencies

From the project root, create and activate a virtual environment, then install the backend requirements:

```powershell
cd Backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On macOS or Linux, activate the environment with:

```bash
source .venv/bin/activate
```

### Configure API keys

Create `Backend/.env` and add your provider credentials:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
MURF_API_KEY=your_murf_api_key
# Optional; defaults to gemini-3.8-flash
GEMINI_MODEL=gemini-3.8-flash
```

Do not commit `.env` or expose API keys in frontend code.

### Start the app

From the `Backend` directory with the virtual environment activated:

```powershell
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). Flask serves both the frontend and the API locally.

## API

### `POST /generate-audio-guide`

Request JSON:

```json
{
  "place": "Taj Mahal",
  "answerType": "Summary",
  "language": "English",
  "voiceId": "Matthew",
  "locale": "en-US"
}
```

`answerType` accepts `Summary` or `Detailed`. The supported languages are English, Hindi, Tamil, and Telugu. A successful response contains the generated `description` and an `audioBase64` MP3 payload. If speech generation is unavailable, `audioBase64` is `null` and the text transcript is still returned.

## Deployment

- **Backend on Render:** `render.yaml` defines the Python web service and its `MURF_API_KEY`, `GEMINI_API_KEY`, and optional `GEMINI_MODEL` environment variables. Set the required secrets in the Render dashboard.
- **Frontend on Netlify:** `netlify.toml` publishes the `Frontend` directory. Before deploying, update `Frontend/config.js` so `apiBaseUrl` points to your deployed Render service URL instead of the placeholder `https://YOUR-RENDER-SERVICE.onrender.com`.

Keep provider API keys on the backend; never place them in `Frontend/config.js` or other client-side files.
=======
# Travel-Guide-AI
An AI-powered travel companion that creates concise or detailed guides to destinations in English, Hindi, Tamil, and Telugu, then turns them into audio.
>>>>>>> c0d19d293d62ee5b934701126ef8e3894f4ed35a
