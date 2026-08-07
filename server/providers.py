import json
from typing import AsyncGenerator, List

import httpx


async def get_available_ollama_models(ollama_url: str) -> List[str]:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(f"{ollama_url}/api/tags")
            if res.status_code == 200:
                return [m["name"] for m in res.json().get("models", [])]
    except Exception:
        pass
    return []


async def stream_from_gemini(messages_payload: list, api_key: str) -> AsyncGenerator[str, None]:
    """Stream response text chunks from Google Gemini 2.5 Flash REST API."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?key={api_key}&alt=sse"

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


async def stream_from_ollama(ollama_url: str, model: str, messages_payload: list) -> AsyncGenerator[str, None]:
    """Stream response text chunks from a local Ollama /api/chat model."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            f"{ollama_url}/api/chat",
            json={"model": model, "messages": messages_payload, "stream": True}
        ) as response:
            if response.status_code == 200:
                async for line in response.aiter_lines():
                    if line:
                        chunk_data = json.loads(line)
                        chunk_text = chunk_data.get("message", {}).get("content", "")
                        yield chunk_text
