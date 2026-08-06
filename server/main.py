import asyncio
import os
import json
import re
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import httpx

try:
    from server.database import init_db, save_message, get_recent_history, save_memory_fact
except ModuleNotFoundError:
    from database import init_db, save_message, get_recent_history, save_memory_fact

app = FastAPI(
    title="JohnAi VPS Central Server",
    description="Hybrid Central Backend: Local Ollama (Gemma 3/Qwen) + Google Gemini Cloud + Centralized SQLite Memory",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(os.path.dirname(__file__), "data", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Preferred Local Models
GENERAL_MODEL = os.getenv("GENERAL_MODEL", "gemma3:12b")
CODER_MODEL = os.getenv("CODER_MODEL", "qwen2.5-coder:14b")
GEMINI_MODEL = "gemini-2.5-flash"

CODE_KEYWORDS = [
    r"\bcode\b", r"\bcomposant\b", r"\bfonction\b", r"\bscript\b", r"\bhtml\b", r"\bcss\b",
    r"\bjs\b", r"\bjavascript\b", r"\btypescript\b", r"\bpython\b", r"\breact\b", r"\bvue\b",
    r"\bfastapi\b", r"\btauri\b", r"\brust\b", r"\bsql\b", r"\bbug\b", r"\bdebug\b",
    r"\brefactor\b", r"\bapi\b", r"\bjson\b", r"\bsnippet\b", r"\berreur\b", r"\balgorithme\b",
    r"programme", r"écris un code", r"créer un composant", r"générer du code"
]

def is_code_request(prompt: str, files: List[str]) -> bool:
    prompt_lower = prompt.lower()
    for kw in CODE_KEYWORDS:
        if re.search(kw, prompt_lower):
            return True
    code_exts = {".js", ".ts", ".html", ".css", ".py", ".rs", ".json", ".sql", ".sh", ".c", ".cpp"}
    if any(os.path.splitext(f)[1].lower() in code_exts for f in files):
        return True
    return False

@app.on_event("startup")
def startup_event():
    init_db()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_json(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            print("Erreur d'envoi WebSocket:", e)

manager = ConnectionManager()

async def get_available_ollama_models() -> List[str]:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(f"{OLLAMA_URL}/api/tags")
            if res.status_code == 200:
                return [m["name"] for m in res.json().get("models", [])]
    except Exception:
        pass
    return []

@app.get("/api/health")
async def health_check():
    models = await get_available_ollama_models()
    return {
        "status": "online",
        "service": "JohnAi VPS Engine (Hybrid Local + Gemini Cloud)",
        "gemini_configured": bool(GEMINI_API_KEY),
        "ollama_connected": len(models) > 0,
        "available_local_models": models,
        "active_clients": len(manager.active_connections)
    }

@app.get("/api/memory/history")
async def get_memory_history():
    return {"history": get_recent_history(limit=50)}

# Initialize local Whisper Speech-to-Text engine (OpenWhispr / OpenAI Whisper)
whisper_model = None
try:
    from faster_whisper import WhisperModel
    # Using 'base' model for ultrafast transcription in French
    whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    print("✓ Moteur Whisper Local Speech-to-Text chargé avec succès !")
except Exception as e:
    print("Whisper local non chargé:", e)

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())
    return {"filename": file.filename, "status": "uploaded", "size_bytes": os.path.getsize(file_location)}

@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe recorded voice note audio blob using local Whisper engine"""
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    content = await file.read()
    with open(file_location, "wb+") as file_object:
        file_object.write(content)
    
    file_size = os.path.getsize(file_location)
    print(f"🎙️ Audio reçu pour transcription: {file.filename} ({file_size} octets)")

    transcribed_text = ""
    if whisper_model and file_size > 200:
        try:
            segments, info = whisper_model.transcribe(file_location, language="fr", beam_size=5)
            transcribed_text = " ".join([segment.text for segment in segments]).strip()
            print(f"✨ Transcription Whisper réussie: '{transcribed_text}'")
        except Exception as err:
            print("Erreur transcription Whisper:", err)

    if not transcribed_text:
        transcribed_text = f"Note vocale enregistrée le {datetime.now().strftime('%H:%M')}"
        
    return {
        "text": transcribed_text,
        "filename": file.filename,
        "status": "transcribed"
    }

async def stream_from_gemini(messages_payload: list, api_key: str):
    """Stream response from Google Gemini 2.5 Flash REST API"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?key={api_key}&alt=sse"
    
    # Format messages for Gemini API
    contents = []
    for msg in messages_payload:
        role = "user" if msg["role"] == "user" else "model"
        if msg["role"] == "system":
            contents.append({"role": "user", "parts": [{"text": f"SYSTEM INSTRUCTION: {msg['content']}"}]})
            contents.append({"role": "model", "parts": [{"text": "Compris."}]})
        else:
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", url, json={"contents": contents}) as response:
            if response.status_code == 200:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str:
                            try:
                                json_data = json.loads(data_str)
                                candidates = json_data.get("candidates", [])
                                if candidates:
                                    parts = candidates[0].get("content", {}).get("parts", [])
                                    for part in parts:
                                        if "text" in part:
                                            yield part["text"]
                            except Exception:
                                pass

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_content = payload.get("content", "").strip()
            files = payload.get("files", [])
            device_type = payload.get("device_type", "desktop") # desktop / android / windows / mac
            use_cloud = payload.get("use_cloud", False) # explicit trigger for cloud

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
            messages_payload = [
                {
                    "role": "system",
                    "content": "Tu es JohnAi, un assistant IA personnel omniprésent, intelligent, concis et utile."
                }
            ] + recent_context

            available_models = await get_available_ollama_models()
            requires_code = is_code_request(user_content, files)

            # Determine Provider & Model
            use_gemini = (use_cloud or device_type == "android" or len(available_models) == 0) and bool(GEMINI_API_KEY)

            if use_gemini:
                selected_model = GEMINI_MODEL
                mode_label = "Google Gemini 2.5 Flash ⚡ (Cloud)"
            elif requires_code and CODER_MODEL in available_models:
                selected_model = CODER_MODEL
                mode_label = "Mode Code 💻 (Local)"
            elif GENERAL_MODEL in available_models:
                selected_model = GENERAL_MODEL
                mode_label = "Gemma 3 ✦ (Local)"
            elif available_models:
                selected_model = available_models[0]
                mode_label = f"{selected_model} (Local)"
            elif GEMINI_API_KEY:
                selected_model = GEMINI_MODEL
                mode_label = "Google Gemini ⚡ (Cloud)"
            else:
                selected_model = "JohnAi Engine"
                mode_label = "Mode Secours"

            await manager.send_json({
                "type": "status",
                "content": f"JohnAi [{mode_label}] réfléchit..."
            }, websocket)

            accumulated_response = ""

            try:
                if use_gemini:
                    async for chunk in stream_from_gemini(messages_payload, GEMINI_API_KEY):
                        accumulated_response += chunk
                        await manager.send_json({"type": "stream", "chunk": accumulated_response}, websocket)
                else:
                    async with httpx.AsyncClient(timeout=120.0) as client:
                        async with client.stream(
                            "POST",
                            f"{OLLAMA_URL}/api/chat",
                            json={"model": selected_model, "messages": messages_payload, "stream": True}
                        ) as response:
                            if response.status_code == 200:
                                async for line in response.aiter_lines():
                                    if line:
                                        chunk_data = json.loads(line)
                                        chunk_text = chunk_data.get("message", {}).get("content", "")
                                        accumulated_response += chunk_text
                                        await manager.send_json({"type": "stream", "chunk": accumulated_response}, websocket)

            except Exception as err:
                print("Inference Exception:", err)
                if not accumulated_response:
                    accumulated_response = f"JohnAi: J'ai bien reçu votre message '{user_content}'."
                    await manager.send_json({"type": "done", "full_text": accumulated_response}, websocket)
                continue

            if accumulated_response:
                save_message(device_type=device_type, role="assistant", content=accumulated_response, model_used=selected_model)

            await manager.send_json({"type": "done", "full_text": accumulated_response}, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
