"""ارکستریتورِ قطعی — کنترلِ جریانِ خطیِ مراحل."""
from pathlib import Path

from engine import core
from engine.schemas import validate_payload
from domains.quran_root import adapter as quran_root

ADAPTERS = {"quran-root": quran_root}
REPO = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ROOT = REPO / "engine" / "runs"

# مراحل به‌ترتیب فعال می‌شوند؛ هر Task یک ردیف را روشن می‌کند.
STAGES = [(1, "extract"), (2, "cluster"), (3, "observe"), (4, "hypothesis")]


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

    return {"run_id": run_id, "run_dir": str(run_dir),
            "stages_done": done, "status": "ok"}
