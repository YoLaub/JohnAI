import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Loaded before any internal import below: security.py, model_router.py etc. all
# read their config from os.getenv() at import time.
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

try:
    from server.database import init_db, save_message, get_recent_history, save_memory_fact
    from server.security import require_api_key, check_websocket_api_key, sanitize_filename
    from server.model_router import is_code_request, choose_model
    from server.providers import get_available_ollama_models, stream_from_gemini, stream_from_ollama
    from server.connection_manager import ConnectionManager
except ModuleNotFoundError:
    from database import init_db, save_message, get_recent_history, save_memory_fact
    from security import require_api_key, check_websocket_api_key, sanitize_filename
    from model_router import is_code_request, choose_model
    from providers import get_available_ollama_models, stream_from_gemini, stream_from_ollama
    from connection_manager import ConnectionManager

app = FastAPI(
    title="JohnAi VPS Central Server",
    description="Hybrid Central Backend: Local Ollama (Gemma 3/Qwen) + Google Gemini Cloud + Centralized SQLite Memory",
    version="1.1.0"
)

CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    # No cookies/session are used — auth is a bearer-style API key header/query
    # param, so credentialed CORS (which forbids a wildcard origin anyway) isn't needed.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(os.path.dirname(__file__), "data", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


@app.on_event("startup")
def startup_event():
    init_db()


manager = ConnectionManager()


@app.get("/api/health")
async def health_check():
    models = await get_available_ollama_models(OLLAMA_URL)
    return {
        "status": "online",
        "service": "JohnAi VPS Engine (Hybrid Local + Gemini Cloud)",
        "gemini_configured": bool(GEMINI_API_KEY),
        "ollama_connected": len(models) > 0,
        "available_local_models": models,
        "active_clients": len(manager.active_connections)
    }


@app.get("/api/memory/history", dependencies=[Depends(require_api_key)])
async def get_memory_history():
    return {"history": get_recent_history(limit=50)}


# Initialize local Whisper Speech-to-Text engine (OpenWhispr / OpenAI Whisper)
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")
whisper_model = None
try:
    from faster_whisper import WhisperModel
    whisper_model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
    print(f"✓ Moteur Whisper Local Speech-to-Text ({WHISPER_MODEL_SIZE}) chargé avec succès !")
except Exception as e:
    print("Whisper local non chargé:", e)


@app.post("/api/upload", dependencies=[Depends(require_api_key)])
async def upload_document(file: UploadFile = File(...)):
    safe_filename = sanitize_filename(file.filename)
    file_location = os.path.join(UPLOAD_DIR, safe_filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())
    return {"filename": safe_filename, "status": "uploaded", "size_bytes": os.path.getsize(file_location)}


@app.post("/api/transcribe", dependencies=[Depends(require_api_key)])
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe recorded voice note audio blob using local Whisper engine"""
    safe_filename = sanitize_filename(file.filename)
    file_location = os.path.join(UPLOAD_DIR, safe_filename)
    content = await file.read()
    with open(file_location, "wb+") as file_object:
        file_object.write(content)

    file_size = os.path.getsize(file_location)
    print(f"🎙️ Audio reçu pour transcription: {safe_filename} ({file_size} octets)")

    transcribed_text = ""
    if whisper_model and file_size > 200:
        try:
            segments, info = whisper_model.transcribe(
                file_location, language="fr", beam_size=5, vad_filter=True
            )
            transcribed_text = " ".join([segment.text for segment in segments]).strip()
            print(f"✨ Transcription Whisper réussie: '{transcribed_text}'")
        except Exception as err:
            print("Erreur transcription Whisper:", err)

    if not transcribed_text:
        transcribed_text = f"Note vocale enregistrée le {datetime.now().strftime('%H:%M')}"

    return {
        "text": transcribed_text,
        "filename": safe_filename,
        "status": "transcribed"
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    supplied_key = websocket.query_params.get("api_key", "")
    if not check_websocket_api_key(supplied_key):
        await websocket.close(code=1008)  # policy violation
        return

    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_content = payload.get("content", "").strip()
            files = payload.get("files", [])
            device_type = payload.get("device_type", "desktop")  # desktop / android / windows / mac
            use_cloud = payload.get("use_cloud", False)  # explicit trigger for cloud

            if not user_content and not files:
                continue

            prompt_text = user_content
            if files:
                prompt_text += f"\n[Documents joints: {', '.join(files)}]"

            # Save user message to central SQLite memory
            save_message(device_type=device_type, role="user", content=prompt_text)

            # If Mode Note: Instant confirmation without triggering LLM generation
            if payload.get("mode") == "note":
                await manager.send_json({
                    "type": "done",
                    "full_text": "✓ **Pensée enregistrée dans votre mémoire centralisée** 📝"
                }, websocket)
                continue

            recent_context = get_recent_history(limit=20)
            messages_payload = [
                {
                    "role": "system",
                    "content": "Tu es JohnAi, un assistant IA personnel omniprésent, intelligent, concis et utile."
                }
            ] + recent_context

            available_models = await get_available_ollama_models(OLLAMA_URL)
            requires_code = is_code_request(user_content, files)

            choice = choose_model(
                use_cloud=use_cloud,
                device_type=device_type,
                requires_code=requires_code,
                available_models=available_models,
                gemini_api_key=GEMINI_API_KEY,
            )

            await manager.send_json({
                "type": "status",
                "content": f"JohnAi [{choice.label}] réfléchit..."
            }, websocket)

            accumulated_response = ""

            try:
                if choice.provider == "gemini":
                    stream = stream_from_gemini(messages_payload, GEMINI_API_KEY)
                else:
                    stream = stream_from_ollama(OLLAMA_URL, choice.model, messages_payload)

                async for chunk in stream:
                    accumulated_response += chunk
                    await manager.send_json({"type": "stream", "chunk": accumulated_response}, websocket)

            except Exception as err:
                print("Inference Exception:", err)
                if not accumulated_response:
                    accumulated_response = f"JohnAi: J'ai bien reçu votre message '{user_content}'."
                    await manager.send_json({"type": "done", "full_text": accumulated_response}, websocket)
                continue

            if accumulated_response:
                save_message(device_type=device_type, role="assistant", content=accumulated_response, model_used=choice.model)

            await manager.send_json({"type": "done", "full_text": accumulated_response}, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
