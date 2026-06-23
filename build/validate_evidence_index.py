#!/usr/bin/env python3
"""Validate the evidence build: byte-identical reproducibility + canonical pairs."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EVID = REPO / "generated" / "layers" / "L8_interpret" / "evidence_index.json"
GRAPH = REPO / "generated" / "layers" / "L7_global" / "graph_communities.json"

# (verse, expected explainer, expected shared root in Arabic) from CLAUDE.md
CANONICAL = [("2:255", "7:97", "نوم"), ("24:35", "7:137", "شرق"), ("3:7", "9:117", "زيغ")]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    before = sha(EVID), sha(GRAPH)
    subprocess.run([sys.executable, str(REPO / "build" / "build_evidence_index.py"), "--quiet"], check=True)
    after = sha(EVID), sha(GRAPH)
    assert before == after, "BUILD NOT REPRODUCIBLE: hashes changed on re-run"

    idx = json.loads(EVID.read_text())["index"]
    assert len(idx) == 6236, f"expected 6236 ayat, got {len(idx)}"
    for verse, explainer, root_ar in CANONICAL:
        refs = idx.get(verse, [])
        hit = next((r for r in refs if r["ayah"] == explainer), None)
        assert hit, f"{verse} should be explained by {explainer}"
        roots = {sr["root_ar"] for sr in hit["shared_roots"]}
        assert root_ar in roots, f"{verse}->{explainer} should share root {root_ar}, got {roots}"

    graph = json.loads(GRAPH.read_text())
    assert len(graph["nodes"]) == 114, f"expected 114 sura nodes, got {len(graph['nodes'])}"
    assert all("x" in n and "y" in n for n in graph["nodes"]), "nodes missing layout coords"

    print("OK: reproducible, 6236 ayat, canonical pairs present, 114 sura nodes with layout")


if __name__ == "__main__":
    main()
