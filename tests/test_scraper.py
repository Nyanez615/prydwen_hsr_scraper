# tests/test_scraper.py
import pytest
from scraper.main import scrape_star_rail_characters

def test_scrape_star_rail_characters():
    """
    Basic test to ensure scraper returns a list and 
    doesn't raise exceptions for the first few characters.
    """
    # Let's just test with limit=2 to keep it quick
    characters = scrape_star_rail_characters(limit=2)
    assert isinstance(characters, list), "Scraper should return a list"
    assert len(characters) == 2, "Should scrape exactly 2 characters"
    # Check required keys
    for char in characters:
        assert "name" in char, "Character entry missing 'name'"
        assert "element" in char, "Character entry missing 'element'"
        assert "path" in char, "Character entry missing 'path'"
        assert "rarity" in char, "Character entry missing 'rarity'"
        assert "role" in char, "Character entry missing 'role'"
        assert "moc_rating" in char, "Character entry missing 'moc_rating'"
        assert "pf_rating" in char, "Character entry missing 'pf_rating'"
        assert "as_rating" in char, "Character entry missing 'as_rating'"
