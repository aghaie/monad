# tests/engine/test_cluster.py
from engine.stages import cluster
from domains.quran_root import adapter


def _payload():
    return adapter.extract(adapter.resolve_unit("علم"))


def test_clusters_partition_all_evidence():
    pl = cluster.run(_payload())
    total = sum(len(c["members"]) for c in pl["clusters"])
    assert total == 854
    assert pl["method"]["seed"] == 20260626


def test_cluster_is_deterministic():
    p = _payload()
    assert cluster.run(p) == cluster.run(p)


def test_patterns_have_lift_and_null_p():
    pl = cluster.run(_payload())
    assert pl["patterns"], "expected co-occurrence patterns"
    for pat in pl["patterns"]:
        assert "lift" in pat and "null_p" in pat and "support" in pat
