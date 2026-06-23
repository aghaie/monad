from app.server.services.network import interpret
from app.server.services.communities import graph_communities, sura_subgraph


def test_interpret_canonical_pair():
    refs = interpret(2, 255)
    hit = next((r for r in refs if r["ayah"] == "7:97"), None)
    assert hit is not None
    assert any(sr["root_ar"] == "نوم" for sr in hit["shared_roots"])
    assert hit["text"]  # explainer text included


def test_interpret_abstention_is_empty_list():
    # 112:1 has no rare-root explainers in the validated demo
    assert interpret(112, 1) == []


def test_graph_communities_shape():
    g = graph_communities()
    assert len(g["nodes"]) == 114
    assert g["edges"]


def test_sura_subgraph_intra_only():
    sg = sura_subgraph(2)
    assert sg["sura"] == 2
    assert all(e["source"].startswith("2:") and e["target"].startswith("2:") for e in sg["edges"])
    assert sg["nodes"]
