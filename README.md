# Quinn Q Monorepo

This repository is organized as a monorepo with separate areas for the Python backend, React frontend, and Rancher/Kubernetes infrastructure.

## Structure
- `backend/` — Python backend (Gemini client, rulebook ingestion)
- `frontend/` — React (Vite + TS) app scaffold
- `infrastructure/rancher/` — Rancher/K8s manifests

## Quickstart

### Backend
1. Create `.env` in `backend/` with `GOOGLE_API_KEY=...`.
2. Install deps (in `backend/`):
   - Poetry: `poetry install`
3. Run (in `backend/`):
   ```bash
   python -m gemini.request
   ```

### Frontend
1. In `frontend/` run `npm i` (or `pnpm i`, `yarn`).
2. Start dev server: `npm run dev`.

### Infrastructure
Templates under `infrastructure/rancher/k8s/`. Update image names and secrets before deploying.