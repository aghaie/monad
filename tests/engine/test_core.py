# tests/engine/test_core.py
import json
from engine import core

UNIT = {"domain": "quran-root", "ref": "Elm", "display": "علم", "unit_id": 218}
SUB = {"id": "quran-hafs", "hash": "sha256:abc"}

def test_canonical_json_is_stable_and_unicode():
    a = core.canonical_json({"b": 1, "a": "علم"})
    assert a == '{"a":"علم","b":1}'

def test_sha256_prefixed_and_deterministic():
    h1 = core.sha256_of({"x": 1})
    h2 = core.sha256_of({"x": 1})
    assert h1 == h2 and h1.startswith("sha256:")

def test_run_id_is_content_derived():
    wc = {"worker": "StatisticalWorker"}
    r1 = core.derive_run_id("0.1.0", UNIT, "sha256:abc", wc)
    r2 = core.derive_run_id("0.1.0", UNIT, "sha256:abc", wc)
    r3 = core.derive_run_id("0.1.0", UNIT, "sha256:DIFF", wc)
    assert r1 == r2 and r1 != r3 and len(r1) == 16

def test_envelope_roundtrip_and_validation(tmp_path):
    env = core.build_envelope(
        stage="extract", stage_index=1, unit=UNIT, substrate=SUB,
        protocol_version="0.1.0", run_id="deadbeefdeadbeef",
        produced_by={"layer": "deterministic", "tool": "extract.py@test"},
        inputs={"substrate": SUB["hash"]}, payload={"ok": True})
    core.validate_envelope(env)
    p = core.write_artifact(tmp_path, 1, "extract", env)
    assert p.name == "01_extract.json"
    back = core.read_artifact(p)
    assert back["payload"] == {"ok": True}
    assert back["produced_at"]  # informational stamp present

def test_validate_rejects_missing_field():
    import pytest
    bad = {"stage": "x"}
    with pytest.raises(core.SchemaError):
        core.validate_envelope(bad)

def test_version_lock():
    assert core.PROTOCOL_VERSION == "0.1.0"
    assert core.ENVELOPE_VERSION == "1.0"
    assert core.SCHEMA_VERSION == "1.0"
