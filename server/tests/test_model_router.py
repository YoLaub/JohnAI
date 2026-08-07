from server.model_router import is_code_request, choose_model, GENERAL_MODEL, CODER_MODEL, GEMINI_MODEL


def test_is_code_request_detects_keyword():
    assert is_code_request("écris-moi une fonction Python", [])


def test_is_code_request_detects_file_extension():
    assert is_code_request("regarde ça", ["snippet.py"])


def test_is_code_request_false_for_plain_prompt():
    assert not is_code_request("Quel temps fait-il aujourd'hui ?", [])


def test_choose_model_prefers_gemini_for_android():
    choice = choose_model(
        use_cloud=False, device_type="android", requires_code=False,
        available_models=[GENERAL_MODEL], gemini_api_key="secret",
    )
    assert choice.provider == "gemini"
    assert choice.model == GEMINI_MODEL


def test_choose_model_prefers_coder_model_for_code_requests():
    choice = choose_model(
        use_cloud=False, device_type="desktop", requires_code=True,
        available_models=[GENERAL_MODEL, CODER_MODEL], gemini_api_key="",
    )
    assert choice.provider == "ollama"
    assert choice.model == CODER_MODEL


def test_choose_model_falls_back_to_general_model():
    choice = choose_model(
        use_cloud=False, device_type="desktop", requires_code=False,
        available_models=[GENERAL_MODEL], gemini_api_key="",
    )
    assert choice.model == GENERAL_MODEL


def test_choose_model_uses_gemini_when_no_local_models_available():
    choice = choose_model(
        use_cloud=False, device_type="desktop", requires_code=False,
        available_models=[], gemini_api_key="secret",
    )
    assert choice.provider == "gemini"


def test_choose_model_falls_back_to_secours_when_nothing_available():
    choice = choose_model(
        use_cloud=False, device_type="desktop", requires_code=False,
        available_models=[], gemini_api_key="",
    )
    assert choice.model == "JohnAi Engine"
