// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod whisper_stt;

fn main() {
    tauri::Builder::default()
        .manage(whisper_stt::WhisperState::default())
        .invoke_handler(tauri::generate_handler![
            whisper_stt::is_model_ready,
            whisper_stt::download_model,
            whisper_stt::transcribe_audio,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
