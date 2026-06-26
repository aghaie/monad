from engine.workers import get_worker
from engine.workers.base import WorkerRequest
from engine.stages import cluster
from domains.quran_root import adapter


def _cluster_payload():
    return cluster.run(adapter.extract(adapter.resolve_unit("علم")))


def test_statistical_observe_cites_existing_ids():
    w = get_worker("statistical")
    cpay = _cluster_payload()
    req = WorkerRequest("observe", cpay, "cluster")
    out = w.reason(req)
    ids = {c["cluster_id"] for c in cpay["clusters"]} | {p["pattern_id"] for p in cpay["patterns"]}
    assert out["observations"]
    for o in out["observations"]:
        assert o["cites"] and all(cid in ids for cid in o["cites"])
        assert "hypothesis" not in o  # بدون فرضیه در Observe


def test_statistical_is_deterministic():
    w = get_worker("statistical")
    cpay = _cluster_payload()
    r1 = w.reason(WorkerRequest("observe", cpay, "cluster"))
    r2 = w.reason(WorkerRequest("observe", cpay, "cluster"))
    assert r1 == r2
