"""RFC Generator — Publication Layer. Store → سندِ انسان/ممیزی (idempotent)."""
import json
from pathlib import Path


class ProvenanceError(ValueError):
    pass


def _list_knowledge(store):
    out = []
    for p in sorted((store.root / "knowledge").glob("*.json")):
        out.append(json.loads(p.read_text("utf-8")))
    return out


def generate(store, unit, run_id, protocol_version, benchmark=None, out_root=None):
    knowledge = _list_knowledge(store)
    for k in knowledge:
        if not store.provenance_complete(k["knowledge_id"]):
            raise ProvenanceError(f"P2 violated: {k['knowledge_id']}")
    rfc_id = f"RFC-{unit['domain']}-{unit['ref']}-v{protocol_version}-{run_id}"
    rfc = {
        "rfc_id": rfc_id, "unit": unit, "protocol_version": protocol_version,
        "run_id": run_id, "status": "ACCEPTED", "supersedes": None,
        "relation_to_prior": None, "knowledge": knowledge,
        "fields": {
            "evidence": {"count": len(list((store.root / "evidence").glob("*.json")))},
            "reasoning": {"chain": "cluster→observe→hypothesis→attack→verify→reduce→graph"},
            "confidence": {k["knowledge_id"]: k["formal_representation"]["confidence_tier"]
                           for k in knowledge},
            "scope": {"unit": unit["ref"]},
            "limitations": {"note": "v1 minimal-fidelity; KB empty. two_half_stability is a presence check across mushaf halves, not a statistical replication test; knowledge resting on it is bounded accordingly."},
            "relationships": {"links": [r for k in knowledge
                                        for r in k["formal_representation"]["relations"]]},
            "history": {"protocol_version": protocol_version, "supersedes": None}},
        "benchmark_score": benchmark or {}}
    out_root = Path(out_root) if out_root else Path(__file__).resolve().parent
    d = out_root / unit["domain"] / unit["ref"]
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{rfc_id}.json").write_text(json.dumps(rfc, ensure_ascii=False, indent=2), "utf-8")
    md = [f"# {rfc_id}", "", f"**واحد:** {unit.get('display', unit['ref'])}",
          "", "## دانشِ تأییدشده"]
    for k in knowledge:
        md.append(f"- **{k['knowledge_id']}** ({k['formal_representation']['confidence_tier']}): "
                  f"{k['natural_explanation']}")
    (d / f"{rfc_id}.md").write_text("\n".join(md), "utf-8")
    return rfc
