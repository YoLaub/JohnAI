import os
import json
import contextlib
from datetime import datetime
from dotenv import load_dotenv

# Loaded before any internal import below: security.py, model_router.py etc. all
# read their config from os.getenv() at import time.
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from fastapi import Body, Depends, FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

try:
    from server.database import (
        init_db, save_message, get_recent_history, get_message_history,
        add_memory_fact, get_all_memory_facts, delete_memory_facts_matching,
        list_categories, create_category, set_message_category, set_category_for_last_message,
        set_message_content, delete_message,
        create_note_link, get_links_for_message, delete_note_link, get_linked_notes_context,
        get_related_notes,
    )
    from server.security import require_api_key, check_websocket_api_key, sanitize_filename
    from server.model_router import is_code_request, choose_model
    from server.providers import get_available_ollama_models, stream_from_gemini, stream_from_ollama
    from server.connection_manager import ConnectionManager
    from server.memory_facts import extract_remember_fact, extract_forget_query
    from server.categorization import extract_categorize_command
    from server.mcp_server import build_mcp_asgi_app
except ModuleNotFoundError:
    from database import (
        init_db, save_message, get_recent_history, get_message_history,
        add_memory_fact, get_all_memory_facts, delete_memory_facts_matching,
        list_categories, create_category, set_message_category, set_category_for_last_message,
        set_message_content, delete_message,
        create_note_link, get_links_for_message, delete_note_link, get_linked_notes_context,
        get_related_notes,
    )
    from security import require_api_key, check_websocket_api_key, sanitize_filename
    from model_router import is_code_request, choose_model
    from providers import get_available_ollama_models, stream_from_gemini, stream_from_ollama
    from connection_manager import ConnectionManager
    from memory_facts import extract_remember_fact, extract_forget_query
    from categorization import extract_categorize_command
    from mcp_server import build_mcp_asgi_app

# Built before the FastAPI app: its own lifespan (session manager) needs to be
# entered from ours below, and add_middleware/mount need the same instance.
mcp_asgi_app = build_mcp_asgi_app()


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    async with mcp_asgi_app.router.lifespan_context(mcp_asgi_app):
        yield


app = FastAPI(
    title="JohnAi VPS Central Server",
    description="Hybrid Central Backend: Local Ollama (Gemma 3/Qwen) + Google Gemini Cloud + Centralized SQLite Memory",
    version="1.1.0",
    lifespan=lifespan,
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


app.mount("/mcp", mcp_asgi_app)

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
    return {"history": get_message_history(limit=50)}


@app.get("/api/categories", dependencies=[Depends(require_api_key)])
async def get_categories():
    return {"categories": list_categories()}


@app.post("/api/categories", dependencies=[Depends(require_api_key)])
async def post_category(payload: dict = Body(...)):
    name = (payload.get("name") or "").strip()
    if not name:
        return {"status": "error", "detail": "name manquant"}
    create_category(name)
    return {"status": "ok", "name": name}


@app.patch("/api/memory/{message_id}/category", dependencies=[Depends(require_api_key)])
async def patch_message_category(message_id: int, payload: dict = Body(...)):
    # Empty/missing category means "clear it back to Non classé" (NULL), not an
    # error — the picker exposes that as a real choice, not just an omission.
    category = (payload.get("category") or "").strip() or None
    if category:
        create_category(category)
    updated = set_message_category(message_id, category)
    if not updated:
        return {"status": "error", "detail": "message introuvable"}
    return {"status": "ok", "id": message_id, "category": category}


@app.patch("/api/memory/{message_id}/content", dependencies=[Depends(require_api_key)])
async def patch_message_content(message_id: int, payload: dict = Body(...)):
    content = (payload.get("content") or "").strip()
    if not content:
        return {"status": "error", "detail": "contenu manquant"}
    updated = set_message_content(message_id, content)
    if not updated:
        return {"status": "error", "detail": "message introuvable"}
    return {"status": "ok", "id": message_id, "content": content}


@app.delete("/api/memory/{message_id}", dependencies=[Depends(require_api_key)])
async def delete_message_route(message_id: int):
    deleted = delete_message(message_id)
    if not deleted:
        return {"status": "error", "detail": "message introuvable"}
    return {"status": "ok", "id": message_id}


@app.get("/api/memory/{message_id}/links", dependencies=[Depends(require_api_key)])
async def get_message_links(message_id: int):
    return {"links": get_links_for_message(message_id)}


@app.post("/api/memory/{message_id}/links", dependencies=[Depends(require_api_key)])
async def post_message_link(message_id: int, payload: dict = Body(...)):
    to_id = payload.get("to_id")
    if not isinstance(to_id, int):
        return {"status": "error", "detail": "to_id manquant"}
    if to_id == message_id:
        return {"status": "error", "detail": "une note ne peut pas se lier à elle-même"}
    link_id = create_note_link(message_id, to_id)
    if link_id is None:
        return {"status": "error", "detail": "note cible introuvable"}
    return {"status": "ok", "link_id": link_id}


@app.delete("/api/memory/links/{link_id}", dependencies=[Depends(require_api_key)])
async def delete_message_link(link_id: int):
    deleted = delete_note_link(link_id)
    if not deleted:
        return {"status": "error", "detail": "lien introuvable"}
    return {"status": "ok", "id": link_id}


@app.get("/api/memory/{message_id}/related", dependencies=[Depends(require_api_key)])
async def get_message_related(message_id: int):
    return {"related": get_related_notes(message_id, max_hops=2)}


# Initialize local Whisper Speech-to-Text engine (OpenWhispr / OpenAI Whisper)
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")
whisper_model = None
try:
    from faster_whisper import WhisperModel
    whisper_model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
    print(f"✓ Moteur Whisper Local Speech-to-Text ({WHISPER_MODEL_SIZE}) chargé avec succès !")
except Exception as e:
    print("Whisper local non chargé:", e)


@app.post("/api/reformulate", dependencies=[Depends(require_api_key)])
async def reformulate_text(payload: dict = Body(...)):
    text = (payload.get("text") or "").strip()
    if not text:
        return {"status": "error", "detail": "texte manquant"}

    device_type = payload.get("device_type", "desktop")
    use_cloud = payload.get("use_cloud", False)

    system_prompt = (
        "Tu reformules la note suivante pour la rendre plus claire et correcte, "
        "sans changer son sens ni ajouter d'information. Réponds uniquement avec "
        "le texte reformulé, sans commentaire ni guillemets."
    )
    messages_payload = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]

    available_models = await get_available_ollama_models(OLLAMA_URL)
    choice = choose_model(
        use_cloud=use_cloud,
        device_type=device_type,
        requires_code=False,
        available_models=available_models,
        gemini_api_key=GEMINI_API_KEY,
    )

    reformulated = ""
    try:
        if choice.provider == "gemini":
            stream = stream_from_gemini(messages_payload, GEMINI_API_KEY)
        else:
            stream = stream_from_ollama(OLLAMA_URL, choice.model, messages_payload)
        async for chunk in stream:
            reformulated += chunk
    except Exception as err:
        print("Reformulate Exception:", err)

    reformulated = reformulated.strip()
    if not reformulated:
        return {"status": "error", "reformulated": text, "detail": "reformulation indisponible"}

    return {"status": "ok", "reformulated": reformulated}


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

    # Set by the "generate_locally" delegation below when a desktop Tauri
    # client is asked to run inference itself (see client/src/local-ollama.js)
    # — holds what's needed to either save the client's result or, if local
    # Ollama isn't available there, fall back to generating server-side.
    # Per-connection state only: safe across this coroutine's iterations.
    pending_local_context = None

    async def generate_and_reply(device_type, messages_payload, requires_code, use_cloud, user_content):
        available_models = await get_available_ollama_models(OLLAMA_URL)
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
            return

        if accumulated_response:
            save_message(device_type=device_type, role="assistant", content=accumulated_response, model_used=choice.model)

        await manager.send_json({"type": "done", "full_text": accumulated_response}, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            # Desktop Tauri client's reply to a prior "generate_locally" delegation.
            if payload.get("type") == "local_generation_result":
                context = pending_local_context
                pending_local_context = None
                content = (payload.get("content") or "").strip()
                device_type = context["device_type"] if context else "desktop"
                if content:
                    save_message(device_type=device_type, role="assistant", content=content, model_used="ollama-local")
                await manager.send_json({"type": "done", "full_text": content}, websocket)
                continue

            # Client couldn't generate locally (Ollama not running/installed) —
            # finish the still-pending request the old way (Gemini).
            if payload.get("type") == "request_cloud_fallback":
                context = pending_local_context
                pending_local_context = None
                if context:
                    await generate_and_reply(**context)
                continue

            user_content = payload.get("content", "").strip()
            files = payload.get("files", [])
            device_type = payload.get("device_type", "desktop")  # desktop / android / windows / mac
            use_cloud = payload.get("use_cloud", False)  # explicit trigger for cloud
            category = (payload.get("category") or "").strip() or None

            if not user_content and not files:
                continue

            prompt_text = user_content
            if files:
                prompt_text += f"\n[Documents joints: {', '.join(files)}]"

            if category:
                create_category(category)

            # "mets ça dans ..." must be checked *before* saving this utterance —
            # it targets the previous message, not itself. It isn't stored as a
            # conversation row: it's a command, not content.
            categorize_target = extract_categorize_command(user_content)
            if categorize_target:
                create_category(categorize_target)
                moved = set_category_for_last_message(categorize_target)
                if moved:
                    confirmation = f"✓ **Classé dans « {categorize_target} »**"
                else:
                    confirmation = "⚠️ Rien à classer pour l'instant."
                await manager.send_json({"type": "done", "full_text": confirmation}, websocket)
                continue

            # Save user message to central SQLite memory
            save_message(device_type=device_type, role="user", content=prompt_text, category=category)

            # Explicit fact commands take priority over Mode Note/Chat: "retiens
            # que ..." memorizes a durable fact, "oublie que ..." removes matching ones.
            remember_fact = extract_remember_fact(user_content)
            if remember_fact:
                add_memory_fact(remember_fact)
                await manager.send_json({
                    "type": "done",
                    "full_text": f"✓ **Fait mémorisé** : {remember_fact}"
                }, websocket)
                continue

            forget_query = extract_forget_query(user_content)
            if forget_query:
                deleted = delete_memory_facts_matching(forget_query)
                if deleted:
                    forgotten_list = "\n".join(f"- {v}" for v in deleted)
                    confirmation = f"✓ **{len(deleted)} fait(s) oublié(s)** :\n{forgotten_list}"
                else:
                    confirmation = f"⚠️ Aucun fait mémorisé ne correspond à « {forget_query} »."
                await manager.send_json({"type": "done", "full_text": confirmation}, websocket)
                continue

            # If Mode Note: Instant confirmation without triggering LLM generation
            if payload.get("mode") == "note":
                await manager.send_json({
                    "type": "done",
                    "full_text": "✓ **Pensée enregistrée dans votre mémoire centralisée** 📝"
                }, websocket)
                continue

            recent_context = get_recent_history(limit=20)
            system_prompt = "Tu es JohnAi, un assistant IA personnel omniprésent, intelligent, concis et utile."
            memorized_facts = get_all_memory_facts()
            if memorized_facts:
                facts_list = "\n".join(f"- {f['fact_value']}" for f in memorized_facts)
                system_prompt += f"\n\nFaits mémorisés sur l'utilisateur à prendre en compte :\n{facts_list}"

            # Graph layer: notes explicitly linked (note_links) to anything in
            # the recent window, even ones that have scrolled out of it —
            # "what's connected to what, and since when".
            recent_ids = [m["id"] for m in recent_context]
            linked_notes = get_linked_notes_context(recent_ids)
            if linked_notes:
                linked_list = "\n".join(
                    f"- (reliée depuis le {n['created_at']}) {n['content']}" for n in linked_notes
                )
                system_prompt += f"\n\nNotes liées à la conversation en cours à prendre en compte :\n{linked_list}"

            messages_payload = [
                {"role": "system", "content": system_prompt}
            ] + [{"role": m["role"], "content": m["content"]} for m in recent_context]

            requires_code = is_code_request(user_content, files)

            # Desktop Tauri client capable of running Ollama itself (see
            # client/src/local-ollama.js): hand it the raw context instead of
            # generating server-side. Mobile never gets this — battery/architecture
            # rule (CLAUDE.md) — regardless of what it claims to support.
            if payload.get("supports_local_generation") and device_type != "android":
                pending_local_context = {
                    "device_type": device_type,
                    "messages_payload": messages_payload,
                    "requires_code": requires_code,
                    "use_cloud": use_cloud,
                    "user_content": user_content,
                }
                await manager.send_json({"type": "generate_locally", "messages": messages_payload}, websocket)
                continue

            await generate_and_reply(device_type, messages_payload, requires_code, use_cloud, user_content)

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# PWA static assets (client/dist, built into ./static by the Docker image — see
# server/Dockerfile). Mounted last: Starlette matches routes in registration
# order, and a "/" mount would otherwise shadow every /api/... route above it.
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="pwa")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
