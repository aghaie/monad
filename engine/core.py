"""هستهٔ موتورِ کشف: envelope، hashing قطعی، run_id محتوامحور، io آرتیفکت."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ENVELOPE_VERSION = "1.0"
PROTOCOL_VERSION = "0.1.0"
SCHEMA_VERSION = "1.0"


class SchemaError(ValueError):
    pass


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_of(obj) -> str:
    data = obj if isinstance(obj, str) else canonical_json(obj)
    return "sha256:" + hashlib.sha256(data.encode("utf-8")).hexdigest()


def derive_run_id(protocol_version, unit, substrate_hash, worker_config) -> str:
    seed = canonical_json([protocol_version, unit, substrate_hash, worker_config])
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]


_REQUIRED = ("envelope_version", "stage", "stage_index", "unit", "substrate",
             "protocol_version", "run_id", "produced_by", "inputs", "payload")


def build_envelope(stage, stage_index, unit, substrate, protocol_version,
                   run_id, produced_by, inputs, payload) -> dict:
    return {
        "envelope_version": ENVELOPE_VERSION,
        "stage": stage, "stage_index": stage_index,
        "unit": unit, "substrate": substrate,
        "protocol_version": protocol_version, "run_id": run_id,
        "produced_by": produced_by, "inputs": inputs,
        "produced_at": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }


def validate_envelope(env) -> None:
    if not isinstance(env, dict):
        raise SchemaError("envelope must be a dict")
    for k in _REQUIRED:
        if k not in env:
            raise SchemaError(f"missing required field: {k}")
    if env["produced_by"].get("layer") not in ("deterministic", "discovery"):
        raise SchemaError("produced_by.layer must be deterministic|discovery")


def write_artifact(run_dir, stage_index, stage, envelope) -> Path:
    validate_envelope(envelope)
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    p = run_dir / f"0{stage_index}_{stage}.json"
    p.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def read_artifact(path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
