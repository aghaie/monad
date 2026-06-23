"""Graph structure: sura constellation + per-sura verse subgraph."""
from collections import defaultdict

from app.server.data import indexes


def graph_communities():
    return indexes.communities()


def sura_subgraph(s):
    idx = indexes.evidence()["index"]
    prefix = f"{s}:"
    edges = []
    degree = defaultdict(int)
    seen_nodes = set()
    seen_edges = set()
    for ref, links in idx.items():
        if not ref.startswith(prefix):
            continue
        seen_nodes.add(ref)
        for link in links:
            tgt = link["ayah"]
            if not tgt.startswith(prefix):
                continue  # intra-sura only
            key = tuple(sorted((ref, tgt)))
            seen_nodes.add(tgt)
            degree[ref] += 1
            if key in seen_edges:
                continue
            seen_edges.add(key)
            edges.append({"source": key[0], "target": key[1], "weight": link["weight"]})
    nodes = [{"ref": r, "ayah": int(r.split(":")[1]), "degree": degree[r]}
             for r in sorted(seen_nodes, key=lambda r: int(r.split(":")[1]))]
    return {"sura": s, "nodes": nodes, "edges": edges}
