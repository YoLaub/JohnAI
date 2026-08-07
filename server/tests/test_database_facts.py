import pytest

from server.database import add_memory_fact, get_all_memory_facts, delete_memory_facts_matching


@pytest.fixture(autouse=True)
def _db_ready(client):
    """`client` triggers the FastAPI startup event, which runs init_db()."""
    return client


def test_add_memory_fact_appends_a_new_row():
    before = len(get_all_memory_facts())
    add_memory_fact("mon SIRET est 123456789")
    after = get_all_memory_facts()
    assert len(after) == before + 1
    assert after[-1]["fact_value"] == "mon SIRET est 123456789"


def test_add_memory_fact_never_overwrites_existing_facts():
    add_memory_fact("fait unique A")
    add_memory_fact("fait unique A")
    values = [f["fact_value"] for f in get_all_memory_facts()]
    assert values.count("fait unique A") == 2


def test_delete_memory_facts_matching_removes_matching_rows_case_insensitive():
    add_memory_fact("j'habite à Lyon")
    deleted = delete_memory_facts_matching("LYON")
    assert "j'habite à Lyon" in deleted
    remaining = [f["fact_value"] for f in get_all_memory_facts()]
    assert "j'habite à Lyon" not in remaining


def test_delete_memory_facts_matching_returns_empty_when_no_match():
    deleted = delete_memory_facts_matching("texte qui n'existe nulle part xyz")
    assert deleted == []
