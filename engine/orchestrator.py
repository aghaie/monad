"""ارکستریتورِ قطعی — کنترلِ جریانِ خطیِ مراحل."""
from pathlib import Path

from engine import core
from engine.schemas import validate_payload
from domains.quran_root import adapter as quran_root

ADAPTERS = {"quran-root": quran_root}
REPO = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ROOT = REPO / "engine" / "runs"

# مراحل به‌ترتیب فعال می‌شوند؛ هر Task یک ردیف را روشن می‌کند.
STAGES = [(1, "extract"), (2, "cluster"), (3, "observe"), (4, "hypothesis"), (5, "attack"), (6, "verify"), (7, "reduce"), (8, "graph"), (9, "commit")]


def _worker_config(worker_name):
    return {"worker": worker_name}


def run(domain, unit_ref, worker_name="statistical", run_root=None):
    adp = ADAPTERS[domain]
    unit = adp.resolve_unit(unit_ref)
    substrate = {"id": adp.SUBSTRATE_ID, "hash": adp.substrate_hash()}
    run_id = core.derive_run_id(core.PROTOCOL_VERSION, unit, substrate["hash"],
                                _worker_config(worker_name))
    run_root = Path(run_root) if run_root else DEFAULT_RUN_ROOT
    run_dir = run_root / domain / unit["ref"] / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    done = []
    # مرحلهٔ ۱ — Extract (قطعی)
    payload = adp.extract(unit)
    validate_payload("extract", payload)
    env = core.build_envelope(
        "extract", 1, unit, substrate, core.PROTOCOL_VERSION, run_id,
        {"layer": "deterministic", "tool": "quran_root.adapter.extract"},
        {"substrate": substrate["hash"]}, payload)
    core.write_artifact(run_dir, 1, "extract", env)
    done.append("extract")

    from engine.stages import cluster as _cluster
    cpay = _cluster.run(payload)
    validate_payload("cluster", cpay)
    cenv = core.build_envelope(
        "cluster", 2, unit, substrate, core.PROTOCOL_VERSION, run_id,
        {"layer": "deterministic", "tool": "engine.stages.cluster"},
        {"prev_artifact": core.sha256_of(env["payload"])}, cpay)
    core.write_artifact(run_dir, 2, "cluster", cenv)
    done.append("cluster")

    from engine.workers import get_worker
    from engine.workers.base import WorkerRequest
    worker = get_worker(worker_name)
    opay = worker.reason(WorkerRequest("observe", cpay, "cluster"))
    validate_payload("observe", opay)
    oenv = core.build_envelope(
        "observe", 3, unit, substrate, core.PROTOCOL_VERSION, run_id,
        {"layer": "discovery", "worker": worker.name, "capability": "observe"},
        {"prev_artifact": core.sha256_of(cpay)}, opay)
    core.write_artifact(run_dir, 3, "observe", oenv)
    done.append("observe")

    hin = {"observations": opay["observations"],
           "_clusters": cpay["clusters"], "_patterns": cpay["patterns"]}
    hpay = worker.reason(WorkerRequest("hypothesize", hin, "observe"))
    validate_payload("hypothesis", hpay)
    henv = core.build_envelope(
        "hypothesis", 4, unit, substrate, core.PROTOCOL_VERSION, run_id,
        {"layer": "discovery", "worker": worker.name, "capability": "hypothesize"},
        {"prev_artifact": core.sha256_of(opay)}, hpay)
    core.write_artifact(run_dir, 4, "hypothesis", henv)
    done.append("hypothesis")

    apay = worker.reason(WorkerRequest("attack",
        {"hypotheses": hpay["hypotheses"], "_patterns": cpay["patterns"]}, "hypothesis"))
    validate_payload("attack", apay)
    aenv = core.build_envelope(
        "attack", 5, unit, substrate, core.PROTOCOL_VERSION, run_id,
        {"layer": "discovery", "worker": worker.name, "capability": "attack"},
        {"prev_artifact": core.sha256_of(hpay)}, apay)
    core.write_artifact(run_dir, 5, "attack", aenv)
    done.append("attack")

    from engine.stages import verify as _verify
    vpay = _verify.run(hpay["hypotheses"], apay["attacks"], unit, adp)
    validate_payload("verify", vpay)
    venv = core.build_envelope(
        "verify", 6, unit, substrate, core.PROTOCOL_VERSION, run_id,
        {"layer": "deterministic", "tool": "engine.stages.verify"},
        {"prev_artifact": core.sha256_of(apay), "substrate": substrate["hash"]}, vpay)
    core.write_artifact(run_dir, 6, "verify", venv)
    done.append("verify")

    top_co = [p["with"] for p in sorted(cpay["patterns"], key=lambda x: -x["lift"])[:3]]
    rprop = worker.reason(WorkerRequest("reduce_propose", {"_top_coroots": top_co}, "verify"))
    from engine.stages import reduce_measure as _rm
    rpay = _rm.run(rprop, vpay["verifications"], unit, adp)
    validate_payload("reduce", rpay)
    renv = core.build_envelope(
        "reduce", 7, unit, substrate, core.PROTOCOL_VERSION, run_id,
        {"layer": "deterministic", "tool": "engine.stages.reduce_measure"},
        {"prev_artifact": core.sha256_of(venv["payload"])}, rpay)
    core.write_artifact(run_dir, 7, "reduce", renv)
    done.append("reduce")

    from engine.stages import graph as _graph
    gpay = _graph.run(rpay, cpay["patterns"], unit)
    validate_payload("graph", gpay)
    genv = core.build_envelope(
        "graph", 8, unit, substrate, core.PROTOCOL_VERSION, run_id,
        {"layer": "deterministic", "tool": "engine.stages.graph"},
        {"prev_artifact": core.sha256_of(rpay), "kb_snapshot": "sha256:empty"}, gpay)
    core.write_artifact(run_dir, 8, "graph", genv)
    done.append("graph")

    from engine.store import Store
    from engine.stages import commit as _commit
    store = Store(REPO / "store")
    arts = {"extract": env, "verify": venv, "reduce": renv, "graph": genv}
    cmt = _commit.run(store, unit, run_id, arts)
    validate_payload("commit", cmt)
    cmenv = core.build_envelope(
        "commit", 9, unit, substrate, core.PROTOCOL_VERSION, run_id,
        {"layer": "deterministic", "tool": "engine.stages.commit"},
        {"prev_artifact": core.sha256_of(genv["payload"])}, cmt)
    core.write_artifact(run_dir, 9, "commit", cmenv)
    done.append("commit")

    return {"run_id": run_id, "run_dir": str(run_dir),
            "stages_done": done, "status": "ok", "committed": cmt["committed"]}
