"""مرحلهٔ ۹ — نوشتنِ knowledgeِ دونمایشی + evidence + ontology + DAG به Store."""


def run(store, unit, run_id, artifacts):
    ev = artifacts["extract"]["payload"]["evidence"]
    store.put_evidence(ev)
    store.add_dag_nodes([{"id": f"ev:{e['evidence_id']}", "type": "evidence"} for e in ev])

    accepted = [v for v in artifacts["verify"]["payload"]["verifications"]
                if v["decision"] == "ACCEPTED"]
    adef = artifacts["reduce"]["payload"]["accepted_definition"]
    links = artifacts["graph"]["payload"]["links"]
    for prim in adef.get("primitives", []):
        store.put_ontology_primitive({"id": f"prim:{prim}", "primitive": prim})

    n = 0
    sample_ev = f"ev:{ev[0]['evidence_id']}" if ev else None
    for v in accepted:
        kid = v["knowledge_id"]
        obj = {
            "knowledge_id": kid, "unit": unit, "run_id": run_id, "status": "ACCEPTED",
            "formal_representation": {
                "definition_primitives": adef.get("primitives", []),
                "relations": [{"type": l["relation"], "to_unit": l["to_unit"]}
                              for l in links[:3]],
                "verified_by": [v["tests"]], "scope": {"unit": unit["ref"]},
                "confidence_tier": v["confidence_tier"]},
            "natural_explanation": adef.get("statement", ""),
            "provenance_nodes": [kid, f"hyp:{v['hypothesis_id']}"]
                                + ([sample_ev] if sample_ev else []),
            "relations_to_knowledge": []}
        store.put_knowledge(obj)
        store.add_dag_nodes([{"id": kid, "type": "knowledge"},
                             {"id": f"hyp:{v['hypothesis_id']}", "type": "hypothesis"}])
        store.add_dag_edges([{"from": kid, "to": f"hyp:{v['hypothesis_id']}",
                              "type": "verifies"}])
        if sample_ev:
            store.add_dag_edges([{"from": f"hyp:{v['hypothesis_id']}",
                                  "to": sample_ev, "type": "cites"}])
        store.append_log({"event": "knowledge_committed", "knowledge_id": kid,
                          "run_id": run_id})
        n += 1
    return {"committed": {"knowledge": n, "evidence": len(ev),
                          "primitives": len(adef.get("primitives", []))}}
