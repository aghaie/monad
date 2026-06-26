"""اعتبارسنجیِ سبکِ payloadها (stdlib). هر مرحله کلیدهای لازمش را اعلام می‌کند."""
from engine.core import SchemaError

PAYLOAD_KEYS = {
    "extract": ("evidence", "contexts", "unit_stats"),
    "cluster": ("method", "clusters", "patterns"),
    "observe": ("observations",),
    "hypothesis": ("hypotheses",),
    "attack": ("attacks",),
    "verify": ("verifications",),
    "reduce": ("proposed_definition", "compression", "accepted_definition"),
    "graph": ("links", "network_coherence", "predictive_check"),
    "commit": ("committed",),
}


def validate_payload(stage, payload) -> None:
    keys = PAYLOAD_KEYS.get(stage)
    if keys is None:
        raise SchemaError(f"unknown stage: {stage}")
    for k in keys:
        if k not in payload:
            raise SchemaError(f"[{stage}] payload missing key: {k}")
