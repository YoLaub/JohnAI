import pytest

from server.database import (
    list_categories,
    create_category,
    save_message,
    get_message_history,
    set_message_category,
    set_category_for_last_message,
)


@pytest.fixture(autouse=True)
def _db_ready(client):
    """`client` triggers the FastAPI startup event, which runs init_db()."""
    return client


def test_default_categories_are_seeded():
    names = list_categories()
    for expected in ["Famille", "R&D", "Évolution personnelle", "Philo", "Projet"]:
        assert expected in names


def test_create_category_is_idempotent():
    before = len(list_categories())
    create_category("Voyage")
    create_category("Voyage")
    after = list_categories()
    assert after.count("Voyage") == 1
    assert len(after) == before + 1


def test_create_category_ignores_case_duplicates():
    create_category("Sport")
    create_category("sport")
    names = [n.lower() for n in list_categories()]
    assert names.count("sport") == 1


def test_save_message_without_category_defaults_to_none():
    save_message(device_type="desktop", role="user", content="pensée sans catégorie")
    history = get_message_history(limit=1)
    assert history[-1]["category"] is None


def test_save_message_with_category():
    save_message(device_type="desktop", role="user", content="pensée famille", category="Famille")
    history = get_message_history(limit=1)
    assert history[-1]["category"] == "Famille"


def test_set_message_category_updates_existing_message():
    save_message(device_type="desktop", role="user", content="à reclasser")
    history = get_message_history(limit=1)
    message_id = history[-1]["id"]

    updated = set_message_category(message_id, "Projet")

    assert updated is True
    new_history = get_message_history(limit=1)
    assert new_history[-1]["category"] == "Projet"


def test_set_message_category_returns_false_for_unknown_id():
    assert set_message_category(999999999, "Projet") is False


def test_set_category_for_last_message_targets_most_recent_user_message():
    save_message(device_type="desktop", role="user", content="premier")
    save_message(device_type="desktop", role="assistant", content="réponse")
    save_message(device_type="desktop", role="user", content="dernier message utilisateur")

    updated = set_category_for_last_message("Philo")

    assert updated is True
    history = get_message_history(limit=5)
    last_user = [m for m in history if m["role"] == "user"][-1]
    assert last_user["content"] == "dernier message utilisateur"
    assert last_user["category"] == "Philo"
