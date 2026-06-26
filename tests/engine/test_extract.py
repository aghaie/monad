# tests/engine/test_extract.py
from domains.quran_root import adapter

def test_resolve_elm():
    u = adapter.resolve_unit("علم")
    assert u["unit_id"] == 218 and u["domain"] == "quran-root"

def test_extract_elm_shape():
    u = adapter.resolve_unit("علم")
    pl = adapter.extract(u)
    # ۸۵۴ توکنِ ریشهٔ علم در morphology
    assert pl["unit_stats"]["evidence_count"] == 854
    ev = pl["evidence"][0]
    assert set(ev) >= {"evidence_id", "locus", "surface", "features", "context_ref"}
    assert ev["evidence_id"].count(":") == 3
    # context باید متن داشته باشد
    assert pl["contexts"][0]["text"]

def test_extract_is_deterministic():
    u = adapter.resolve_unit("علم")
    assert adapter.extract(u) == adapter.extract(u)

def test_substrate_hash_prefixed():
    assert adapter.substrate_hash().startswith("sha256:")
