"""ارکستریتورِ قطعی — کنترلِ جریانِ خطیِ مراحل."""
from pathlib import Path

from engine import core
from engine.schemas import validate_payload
from domains.quran_root import adapter as quran_root

ADAPTERS = {"quran-root": quran_root}
REPO = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ROOT = REPO / "engine" / "runs"

# مراحل به‌ترتیب فعال می‌شوند؛ هر Task یک ردیف را روشن می‌کند.
STAGES = [(1, "extract")]


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

    return {"run_id": run_id, "run_dir": str(run_dir),
            "stages_done": done, "status": "ok"}
