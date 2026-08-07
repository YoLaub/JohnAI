import os
import re
from dataclasses import dataclass
from typing import List

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
CODE_EXTENSIONS = {".js", ".ts", ".html", ".css", ".py", ".rs", ".json", ".sql", ".sh", ".c", ".cpp"}


def is_code_request(prompt: str, files: List[str]) -> bool:
    prompt_lower = prompt.lower()
    for kw in CODE_KEYWORDS:
        if re.search(kw, prompt_lower):
            return True
    if any(os.path.splitext(f)[1].lower() in CODE_EXTENSIONS for f in files):
        return True
    return False


@dataclass(frozen=True)
class ModelChoice:
    provider: str  # "gemini" | "ollama"
    model: str
    label: str


def choose_model(
    *,
    use_cloud: bool,
    device_type: str,
    requires_code: bool,
    available_models: List[str],
    gemini_api_key: str,
) -> ModelChoice:
    """Pick which provider/model answers a chat message.

    Priority: explicit/mobile cloud request > code-specialized local model >
    general local model > any other available local model > cloud fallback >
    last-resort local no-op model.
    """
    use_gemini = (use_cloud or device_type == "android" or not available_models) and bool(gemini_api_key)

    if use_gemini:
        return ModelChoice("gemini", GEMINI_MODEL, "Google Gemini 2.5 Flash ⚡ (Cloud)")
    if requires_code and CODER_MODEL in available_models:
        return ModelChoice("ollama", CODER_MODEL, "Mode Code 💻 (Local)")
    if GENERAL_MODEL in available_models:
        return ModelChoice("ollama", GENERAL_MODEL, "Gemma 3 ✦ (Local)")
    if available_models:
        return ModelChoice("ollama", available_models[0], f"{available_models[0]} (Local)")
    if gemini_api_key:
        return ModelChoice("gemini", GEMINI_MODEL, "Google Gemini ⚡ (Cloud)")
    return ModelChoice("ollama", "JohnAi Engine", "Mode Secours")
