from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path

from gemini.request import setup_gemini, upload_rulebook, create_chat_session
from google.genai import types
import uvicorn

app = FastAPI(title="Quinn Q Backend")

# CORS for local dev frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    rulebook: Optional[str] = None


@app.get("/api/health")
async def health():
    return {"status": "ok"}


RULEBOOKS_DIR = Path(__file__).resolve().parent / "rulebooks"


@app.get("/api/rulebooks")
async def list_rulebooks() -> List[str]:
    RULEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
    items = [p.name for p in RULEBOOKS_DIR.glob("*.pdf") if p.is_file()]
    return items


@app.post("/api/rulebooks")
async def upload_rulebook_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    RULEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
    target = RULEBOOKS_DIR / file.filename
    content = await file.read()
    try:
        with open(target, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    return {"filename": file.filename}


@app.post("/api/chat")
async def chat(payload: ChatRequest):
    client = setup_gemini()

    # Upload rulebook; create chat session configured with system prompt
    try:
        # Determine which rulebook to use
        RULEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
        selected = payload.rulebook or "Rising_Sun_Rulebook.pdf"
        file_path = RULEBOOKS_DIR / selected
        file = upload_rulebook(client, file_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))

    chat = create_chat_session(client)

    # Prime the chat with instruction + PDF, then user's message
    try:
        initial_parts = [
            types.Part.from_text(
                text=(
                    "Use the uploaded Rising Sun rulebook as the core knowledge "
                    "base for all responses."
                )
            ),
            types.Part.from_uri(file_uri=file.uri, mime_type="application/pdf"),
        ]
        # Send initial setup and user's message in sequence
        chat.send_message(initial_parts)
        response = chat.send_message(payload.message)
        return {"reply": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {e}")
    finally:
        # Clean up uploaded file
        try:
            client.files.delete(name=file.name)
        except Exception:
            pass


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
