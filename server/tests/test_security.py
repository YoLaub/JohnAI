from server.security import sanitize_filename


def test_sanitize_filename_strips_path_traversal():
    assert sanitize_filename("../../evil.txt") == "evil.txt"


def test_sanitize_filename_strips_directories():
    assert sanitize_filename("a/b/c.txt") == "c.txt"


def test_sanitize_filename_replaces_unsafe_characters():
    assert sanitize_filename("note vocale (1)!.wav") == "note_vocale__1__.wav"


def test_sanitize_filename_falls_back_when_empty():
    assert sanitize_filename("") == "upload"
    assert sanitize_filename("..") == "upload"
