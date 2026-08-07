use std::path::PathBuf;
use std::sync::Mutex;

use futures_util::StreamExt;
use tauri::{AppHandle, Emitter, Manager, State};
use whisper_rs::{FullParams, SamplingStrategy, WhisperContext, WhisperContextParameters};

const MODEL_URL: &str =
    "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin";
const MODEL_FILENAME: &str = "ggml-small.bin";

#[derive(Default)]
pub struct WhisperState {
    context: Mutex<Option<WhisperContext>>,
}

fn model_path(app: &AppHandle) -> Result<PathBuf, String> {
    let dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Impossible de résoudre le dossier de données de l'app: {e}"))?;
    std::fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    Ok(dir.join(MODEL_FILENAME))
}

#[tauri::command]
pub fn is_model_ready(app: AppHandle) -> bool {
    match model_path(&app) {
        Ok(path) => path.exists(),
        Err(_) => false,
    }
}

#[tauri::command]
pub async fn download_model(app: AppHandle) -> Result<(), String> {
    let path = model_path(&app)?;
    if path.exists() {
        return Ok(());
    }

    let response = reqwest::get(MODEL_URL)
        .await
        .map_err(|e| format!("Échec de la requête de téléchargement: {e}"))?;

    let total_size = response.content_length().unwrap_or(0);
    let tmp_path = path.with_extension("part");
    let mut file =
        std::fs::File::create(&tmp_path).map_err(|e| format!("Impossible de créer le fichier modèle: {e}"))?;

    let mut downloaded: u64 = 0;
    let mut stream = response.bytes_stream();

    use std::io::Write;
    while let Some(chunk) = stream.next().await {
        let chunk = chunk.map_err(|e| format!("Erreur pendant le téléchargement: {e}"))?;
        file.write_all(&chunk).map_err(|e| e.to_string())?;
        downloaded += chunk.len() as u64;

        let _ = app.emit(
            "whisper-model-download-progress",
            serde_json::json!({ "downloaded": downloaded, "total": total_size }),
        );
    }

    std::fs::rename(&tmp_path, &path).map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
pub fn transcribe_audio(
    app: AppHandle,
    state: State<'_, WhisperState>,
    samples: Vec<f32>,
) -> Result<String, String> {
    let mut ctx_guard = state.context.lock().map_err(|e| e.to_string())?;

    if ctx_guard.is_none() {
        let path = model_path(&app)?;
        if !path.exists() {
            return Err("Modèle Whisper local absent — lancez le téléchargement d'abord".into());
        }
        let ctx = WhisperContext::new_with_params(
            path.to_str().ok_or("Chemin de modèle invalide")?,
            WhisperContextParameters::default(),
        )
        .map_err(|e| format!("Échec du chargement du modèle Whisper: {e}"))?;
        *ctx_guard = Some(ctx);
    }

    let ctx = ctx_guard.as_ref().unwrap();
    let mut whisper_state = ctx
        .create_state()
        .map_err(|e| format!("Échec de création de l'état Whisper: {e}"))?;

    let mut params = FullParams::new(SamplingStrategy::Greedy { best_of: 1 });
    params.set_language(Some("fr"));
    params.set_print_progress(false);
    params.set_print_special(false);
    params.set_print_realtime(false);
    params.set_print_timestamps(false);

    whisper_state
        .full(params, &samples)
        .map_err(|e| format!("Échec de la transcription: {e}"))?;

    let num_segments = whisper_state.full_n_segments();
    let mut text = String::new();
    for i in 0..num_segments {
        if let Some(segment) = whisper_state.get_segment(i) {
            text.push_str(&segment.to_str_lossy().map_err(|e| e.to_string())?);
        }
    }

    Ok(text.trim().to_string())
}
