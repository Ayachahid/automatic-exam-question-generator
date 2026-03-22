import pytest
from src.data.cleaner import TextCleaner

@pytest.fixture
def cleaner():
    return TextCleaner()

def test_clean_empty(cleaner):
    assert cleaner.clean("") == ""
    assert cleaner.clean(None) == ""

def test_clean_whitespace(cleaner):
    text = "  Hello   World  \n"
    # cleaner logic: _collapse_whitespace replaces [ \t]+ with " ", and strip() removes ends
    assert cleaner.clean(text) == "Hello World"

def test_fix_hyphenation(cleaner):
    text = "This is a hyp-\nhenated word."
    expected = "This is a hyphenated word."
    assert cleaner.clean(text) == expected

def test_remove_page_numbers(cleaner):
    text = "Page content.\n 12 \nNext page."
    # _remove_page_numbers replaces \n\s*\d{1,4}\s*\n with \n
    # Then whitespace collapsing happens
    cleaned = cleaner.clean(text)
    assert "12" not in cleaned
    assert "Page content.\nNext page." in cleaned or "Page content.\n\nNext page." in cleaned

def test_unicode_normalization(cleaner):
    text = "café" # Depending on encoding, might need normalization
    # Python source is utf-8, so this is already normalized usually, but function should handle it
    assert cleaner.clean(text) == "café"
