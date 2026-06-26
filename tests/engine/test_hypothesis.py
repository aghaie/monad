"""تستِ مرحلهٔ ۴ — Hypothesis."""
from engine.workers import get_worker
from engine.workers.base import WorkerRequest
from engine.stages import cluster
from domains.quran_root import adapter


def _inputs():
    cpay = cluster.run(adapter.extract(adapter.resolve_unit("علم")))
    w = get_worker("statistical")
    opay = w.reason(WorkerRequest("observe", cpay, "cluster"))
    return w, {"observations": opay["observations"],
               "_clusters": cpay["clusters"], "_patterns": cpay["patterns"]}


def test_hypotheses_max_five_and_well_formed():
    w, inp = _inputs()
    out = w.reason(WorkerRequest("hypothesize", inp, "observe"))
    hs = out["hypotheses"]
    assert 1 <= len(hs) <= 5
    for h in hs:
        assert h["status"] == "PROPOSED"
        assert h["prediction"]["predicate"] in {
            "masked_recovery", "cooccurrence_constraint", "two_half_stability"}
        assert h["supported_by"]
