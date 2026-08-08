from server.categorization import extract_categorize_command


def test_mets_ca_dans():
    assert extract_categorize_command("mets ça dans Famille") == "Famille"


def test_mets_ca_dans_la_categorie():
    assert extract_categorize_command("mets ça dans la catégorie Projet") == "Projet"


def test_classe_cette_note_dans():
    assert extract_categorize_command("classe cette note dans R&D") == "R&D"


def test_range_ca_dans():
    assert extract_categorize_command("range ça dans Philo") == "Philo"


def test_categorise_ca_dans_multi_word_category():
    assert extract_categorize_command("catégorise ça dans Évolution personnelle") == "Évolution personnelle"


def test_is_case_insensitive():
    assert extract_categorize_command("METS ÇA DANS famille") == "famille"


def test_returns_none_without_trigger():
    assert extract_categorize_command("Quel temps fait-il ?") is None


def test_returns_none_when_category_empty():
    assert extract_categorize_command("mets ça dans") is None
