"""Lazy, cached loaders for the generated JSON indexes."""
import json
from pathlib import Path

GEN = Path(__file__).resolve().parents[3] / "generated" / "layers"
EVID_PATH = GEN / "L8_interpret" / "evidence_index.json"
GRAPH_PATH = GEN / "L7_global" / "graph_communities.json"

_cache = {}


def evidence():
    if "evidence" not in _cache:
        _cache["evidence"] = json.loads(EVID_PATH.read_text(encoding="utf-8"))
    return _cache["evidence"]


def communities():
    if "communities" not in _cache:
        _cache["communities"] = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    return _cache["communities"]
