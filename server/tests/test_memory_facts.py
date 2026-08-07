from server.memory_facts import extract_remember_fact, extract_forget_query


def test_extract_remember_fact_with_retiens_que():
    assert extract_remember_fact("Retiens que mon SIRET est 123456789") == "mon SIRET est 123456789"


def test_extract_remember_fact_with_souviens_toi_que():
    assert extract_remember_fact("souviens-toi que j'habite à Lyon") == "j'habite à Lyon"


def test_extract_remember_fact_with_n_oublie_pas_que():
    assert extract_remember_fact("n'oublie pas que mon anniversaire est le 4 mars") == "mon anniversaire est le 4 mars"


def test_extract_remember_fact_is_case_insensitive():
    assert extract_remember_fact("RETIENS QUE test") == "test"


def test_extract_remember_fact_returns_none_without_trigger():
    assert extract_remember_fact("Quel temps fait-il ?") is None


def test_extract_remember_fact_returns_none_when_empty_after_trigger():
    assert extract_remember_fact("retiens que") is None


def test_extract_forget_query_requires_que():
    assert extract_forget_query("oublie mon adresse") is None
    assert extract_forget_query("oublie que mon adresse est fausse") == "mon adresse est fausse"


def test_extract_forget_query_with_efface_que():
    assert extract_forget_query("efface que j'habite à Lyon") == "j'habite à Lyon"


def test_extract_forget_query_returns_none_without_trigger():
    assert extract_forget_query("raconte-moi une blague") is None
