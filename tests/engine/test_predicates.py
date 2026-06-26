"""تستِ پریدیکیت‌ها — Registry (پروتکل) + مجریِ آن در Adapter."""
from engine.predicates import registry
from domains.quran_root import adapter


def test_registry_is_domain_independent():
    assert registry.known("masked_recovery")
    assert "params_schema" in registry.REGISTRY["cooccurrence_constraint"]


def test_cooccurrence_executor_passes_for_strong_pair():
    u = adapter.resolve_unit("علم")
    # «كتب» (کتاب/نوشتن) همراهیِ شناخته‌شده با علم
    kt = adapter.resolve_unit("كتب")
    res = adapter.execute_predicate("cooccurrence_constraint",
                                    {"with_root_id": kt["unit_id"]}, u)
    assert set(res) >= {"score", "null_p", "passed"}
    assert isinstance(res["passed"], bool)


def test_masked_recovery_beats_baseline_is_bool():
    u = adapter.resolve_unit("علم")
    res = adapter.execute_predicate("masked_recovery", {}, u)
    assert "score" in res and "baseline" in res and isinstance(res["passed"], bool)
