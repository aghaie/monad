from app.server.data import db, indexes
from app.server.services.verses import verse_payload


def test_verse_payload_has_text_and_tokens():
    p = verse_payload(1, 1)
    assert p["ref"] == "1:1"
    assert "بِ" in p["text"]["uthmani"] or p["text"]["uthmani"]  # non-empty arabic
    assert len(p["tokens"]) >= 3
    assert all("position" in t and "form" in t for t in p["tokens"])


def test_verse_payload_missing_returns_none():
    assert verse_payload(1, 999) is None


def test_indexes_load():
    assert len(indexes.evidence()["index"]) == 6236
    assert len(indexes.communities()["nodes"]) == 114
