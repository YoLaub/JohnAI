use std::time::Duration;

use serde::{Deserialize, Serialize};

const OLLAMA_URL: &str = "http://localhost:11434";
const GENERAL_MODEL: &str = "gemma3:12b"; // matches server/model_router.py::GENERAL_MODEL

#[derive(Deserialize, Serialize)]
pub struct OllamaMessage {
    role: String,
    content: String,
}

#[derive(Serialize)]
struct ChatRequest<'a> {
    model: &'a str,
    messages: &'a [OllamaMessage],
    stream: bool,
}

#[derive(Deserialize)]
struct ChatResponseMessage {
    content: String,
}

#[derive(Deserialize)]
struct ChatResponse {
    message: ChatResponseMessage,
}

#[derive(Deserialize)]
struct TagsResponse {
    models: Vec<TagsModel>,
}

#[derive(Deserialize)]
struct TagsModel {
    name: String,
}

#[tauri::command]
pub async fn is_ollama_ready() -> bool {
    let client = match reqwest::Client::builder()
        .timeout(Duration::from_millis(1500))
        .build()
    {
        Ok(c) => c,
        Err(_) => return false,
    };

    let response = match client.get(format!("{OLLAMA_URL}/api/tags")).send().await {
        Ok(r) => r,
        Err(_) => return false,
    };

    match response.json::<TagsResponse>().await {
        Ok(tags) => tags.models.iter().any(|m| m.name == GENERAL_MODEL),
        Err(_) => false,
    }
}

#[tauri::command]
pub async fn ollama_generate(messages: Vec<OllamaMessage>) -> Result<String, String> {
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(120))
        .build()
        .map_err(|e| e.to_string())?;

    let body = ChatRequest {
        model: GENERAL_MODEL,
        messages: &messages,
        stream: false,
    };

    let response = client
        .post(format!("{OLLAMA_URL}/api/chat"))
        .json(&body)
        .send()
        .await
        .map_err(|e| format!("Ollama injoignable: {e}"))?;

    let parsed = response
        .json::<ChatResponse>()
        .await
        .map_err(|e| format!("Réponse Ollama invalide: {e}"))?;

    Ok(parsed.message.content)
}
