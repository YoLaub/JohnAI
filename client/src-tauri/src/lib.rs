#[cfg(not(target_os = "android"))]
mod whisper_stt;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let builder = tauri::Builder::default();

    #[cfg(not(target_os = "android"))]
    let builder = builder
        .manage(whisper_stt::WhisperState::default())
        .invoke_handler(tauri::generate_handler![
            whisper_stt::is_model_ready,
            whisper_stt::download_model,
            whisper_stt::transcribe_audio,
        ]);

    builder
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
