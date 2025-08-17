# Backend (Python)

This is the Python backend for the Quinn Q project.

## Prerequisites
- Python 3.13+
- Poetry (if you use the provided `pyproject.toml`)
- A `.env` file containing `GOOGLE_API_KEY`

## Setup
1. Ensure dependencies are installed (from this directory):
   - With Poetry: `poetry install`
   - Or with pip: `pip install -r requirements.txt` (not provided; prefer Poetry)

2. Prepare the rulebook file at `backend/rulebooks/Rising_Sun_Rulebook.pdf` (already included in repo).

## Run (API Server)
From this `backend/` directory:

```bash
# Option A: pip
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000 --reload

# Option B: Poetry
poetry install
poetry run uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

Then visit `http://localhost:8000/api/health`.

The API exposes:
- `GET /api/health` – basic health check
- `POST /api/chat` – body `{ "message": "..." }`, responds with `{ "reply": "..." }`

## Project layout
- `gemini/` — Gemini client and prompt assets
- `rulebooks/` — PDF assets used by the backend
- `server.py` — FastAPI app exposing `/api/*`
- `pyproject.toml` / `poetry.lock` — Python dependencies
