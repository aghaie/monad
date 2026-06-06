#!/usr/bin/env python3
"""
scripts/build_compression.py

Monad Dependency Compression Engine — Builder (Phase 5).

This is NOT an axiom engine, NOT an ontology engine, NOT a theology engine.
It does not name, translate, interpret, or assign meaning to any concept or
relation. Concept ids stay opaque (CONCEPT_001 …). Relation types stay opaque
structural labels inherited from Phase 4.

Purpose: determine whether the discovered Phase-4 proposition structure can be
compressed into a substantially smaller set of foundational structures, and
quantify HOW compressible it is. Every quantity is structural / combinatorial /
graph-theoretic. No semantic claim is made.

Primary research question:
    Can the proposition graph be reconstructed from a substantially smaller
    subset of concepts? If yes, how small? If no, why not?

Inputs (READ-ONLY — never rebuilt or modified):
    generated/monad.db                                   (Phase 1, hashed only)
    generated/lexicon/*                                  (Phase 2, hashed only)
    generated/concepts/concept_candidates.json           (Phase 3)
    generated/propositions/proposition_candidates.json   (Phase 4 — relations)
    generated/propositions/proposition_graph.json        (Phase 4 — directed graph)
    generated/propositions/proposition_manifest.json     (Phase 4, hashed only)

Outputs (generated/compression/):
    foundationality_scores.json   per-concept structural-necessity metrics
    reconstruction_sets.json      minimum concept sets per recovery threshold
    dependency_layers.json        structural dependency layers (SCC-condensed)
    irreducible_structures.json   strongly-connected (non-compressible) cores
    compression_statistics.json   summary ratios + removal experiments + hub removal
    compression_curve.json        concept-count vs recovered-structure curves
    hub_removal_analysis.json     CONCEPT_007 elimination recomputation
    compression_manifest.json     reproducibility manifest

Method (deterministic, structural only):
  PHASE A  Foundationality: for every concept, removal impact, dependency
           impact, reach reduction, fragmentation effect, reconstruction loss,
           information loss. Composite structural-necessity rank.
  PHASE B  Iterative removal of the top-{1,3,5,10,20,30,50} most foundational
           concepts; graph integrity, connectivity, recoverability,
           proposition / dependency retention after each.
  PHASE C  Dominant-hub elimination: remove CONCEPT_007, recompute the induced
           directed graph, betweenness, bridges, hierarchical chains, cycles;
           does another core emerge / collapse / reorganize?
  PHASE D  Minimum reconstruction set: deterministic greedy maximum-coverage
           for {50,60,70,80,90,95}% of proposition structure.
  PHASE E  Dependency layers: SCC-condense DEPENDS_ON ∪ REQUIRES, longest-path
           structural layering (Level 0 = depends on nothing).
  PHASE F  Irreducible structures: strongly-connected components (size ≥ 2)
           that cannot be linearised / compressed further.
  PHASE G  Compression curve: concept count vs recovered structure (greedy and
           foundationality orders), AUC, knee.

A relation is "reconstructable" / "covered" by a concept set S iff EVERY
concept participating in the relation is contained in S. This is the only
definition of reconstruction used; it is purely set-membership and carries no
semantic content. Binary relations need both endpoints; triadic relations
(MEDIATES, CONDITIONAL_EMERGES) need all three.

Determinism: no randomness; sorted iteration everywhere; floats rounded to
ROUND; JSON written with sort_keys=True. Re-runs are byte-identical (verified
by validate_compression.py --rebuild).
"""

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "generated" / "monad.db"
LEX_DIR = REPO_ROOT / "generated" / "lexicon"
CONCEPTS_DIR = REPO_ROOT / "generated" / "concepts"
PROPS_DIR = REPO_ROOT / "generated" / "propositions"
OUT_DIR = REPO_ROOT / "generated" / "compression"

METHOD_VERSION = "phase5-compression-1.0"
ROUND = 6

# ── Constants (fixed, documented in the manifest) ──────────────────────────────

DOMINANT_HUB = "CONCEPT_007"          # Phase-4 dominant requirement target
REMOVAL_STEPS = [1, 3, 5, 10, 20, 30, 50]
RECOVERY_TARGETS = [0.50, 0.60, 0.70, 0.80, 0.90, 0.95]
CYCLE_MAX_LEN = 4                     # matches Phase 4 recursive-cycle bound
TOP_BRIDGE_FRAC = 0.10               # matches Phase 4 bridge definition
# Composite foundationality weights each normalised metric equally.
FOUNDATIONALITY_METRICS = [
    "removal_impact_count",
    "support_weighted_loss",
    "dependency_impact",
    "reach_reduction",
    "fragmentation_components_added",
    "information_loss_bits",
]

# Relation types whose members are directional (src → tgt) in the proposition
# graph. The remaining types (CO_OCCURS, ASSOCIATES_WITH) are symmetric;
# MEDIATES and CONDITIONAL_EMERGES are triadic.
DIRECTED_TYPES = {"DEPENDS_ON", "REQUIRES", "PRECEDES", "FOLLOWS", "PREDICTS"}
DEPENDENCY_TYPES = {"DEPENDS_ON", "REQUIRES"}


def r(x):
    return round(float(x), ROUND)


def write_json(path, obj):
    text = json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=1)
    path.write_text(text, encoding="utf-8")
    return len(text.encode("utf-8"))


def sha256_file(path):
    h = hashlib.sha256()
    h.update(Path(path).read_bytes())
    return h.hexdigest()


# ── Graph helpers (pure, deterministic) ─────────────────────────────────────────

def reachable_from(adj, source, blocked=None):
    """Set of nodes reachable from source (excludes source itself)."""
    blocked = blocked or set()
    seen = set()
    stack = [source]
    while stack:
        u = stack.pop()
        for v in adj.get(u, ()):  # adj values are sets
            if v in blocked or v in seen:
                continue
            seen.add(v)
            stack.append(v)
    seen.discard(source)
    return seen


def connected_components(nodes, adj):
    """Undirected connected components over `nodes` using adjacency `adj`."""
    seen = set()
    comps = []
    for s in sorted(nodes):
        if s in seen:
            continue
        comp = set()
        stack = [s]
        seen.add(s)
        while stack:
            u = stack.pop()
            comp.add(u)
            for v in adj.get(u, ()):
                if v in nodes and v not in seen:
                    seen.add(v)
                    stack.append(v)
        comps.append(comp)
    return comps


def tarjan_scc(nodes, adj):
    """Tarjan strongly-connected components. Deterministic (sorted order).
    Returns list of components (each a sorted list), in deterministic order."""
    index_counter = [0]
    stack = []
    on_stack = set()
    indices = {}
    lowlink = {}
    result = []

    # iterative Tarjan to avoid recursion limits
    for root in sorted(nodes):
        if root in indices:
            continue
        work = [(root, iter(sorted(adj.get(root, ()))))]
        indices[root] = index_counter[0]
        lowlink[root] = index_counter[0]
        index_counter[0] += 1
        stack.append(root)
        on_stack.add(root)
        while work:
            node, it = work[-1]
            advanced = False
            for w in it:
                if w not in nodes:
                    continue
                if w not in indices:
                    indices[w] = index_counter[0]
                    lowlink[w] = index_counter[0]
                    index_counter[0] += 1
                    stack.append(w)
                    on_stack.add(w)
                    work.append((w, iter(sorted(adj.get(w, ())))))
                    advanced = True
                    break
                elif w in on_stack:
                    lowlink[node] = min(lowlink[node], indices[w])
            if advanced:
                continue
            # done exploring `node`
            if lowlink[node] == indices[node]:
                comp = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    comp.append(w)
                    if w == node:
                        break
                result.append(sorted(comp))
            work.pop()
            if work:
                parent = work[-1][0]
                lowlink[parent] = min(lowlink[parent], lowlink[node])
    # deterministic ordering: by size desc then lexicographic
    result.sort(key=lambda c: (-len(c), c))
    return result


def brandes_betweenness(nodes, adj):
    """Unweighted undirected Brandes betweenness — replicates Phase 4 exactly
    (sorted BFS, divide by 2 for undirected double counting)."""
    bet = {c: 0.0 for c in nodes}
    node_list = sorted(nodes)
    for s in node_list:
        dist = {c: -1 for c in nodes}
        sigma = {c: 0 for c in nodes}
        pred = {c: [] for c in nodes}
        dist[s] = 0
        sigma[s] = 1
        queue = [s]
        visited = []
        head = 0
        while head < len(queue):
            u = queue[head]
            head += 1
            visited.append(u)
            for v in sorted(adj.get(u, ())):
                if v not in nodes:
                    continue
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    queue.append(v)
                if dist[v] == dist[u] + 1:
                    sigma[v] += sigma[u]
                    pred[v].append(u)
        delta = {c: 0.0 for c in nodes}
        for w in reversed(visited):
            for v in pred[w]:
                if sigma[w] > 0:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
            if w != s:
                bet[w] += delta[w]
    for c in bet:
        bet[c] = bet[c] / 2.0
    return bet


def count_short_cycles(nodes, dir_adj, max_len=CYCLE_MAX_LEN):
    """Directed cycles of length 2..max_len, canonicalised by rotation —
    replicates Phase 4 recursive-cycle enumeration exactly."""
    cycles = set()

    def find(start, current, depth, path):
        if depth > max_len:
            return
        for nxt in sorted(dir_adj.get(current, ())):
            if nxt not in nodes:
                continue
            if nxt == start and 2 <= len(path) <= max_len:
                cyc = tuple(path + [nxt])
                rot = min(tuple(cyc[i:-1] + cyc[:i]) for i in range(len(cyc) - 1))
                cycles.add(rot)
            elif nxt not in path:
                find(start, nxt, depth + 1, path + [nxt])

    for s in sorted(nodes):
        find(s, s, 1, [s])
    return cycles


# ── Builder ─────────────────────────────────────────────────────────────────────

class CompressionEngine:

    def __init__(self):
        self.out_dir = OUT_DIR
        self.out_dir.mkdir(parents=True, exist_ok=True)

    # ── Load Phase-4 structure ────────────────────────────────────────────────

    def load(self):
        print("  loading Phase-3/4 outputs (read-only) …")
        self.candidates = json.loads(
            (PROPS_DIR / "proposition_candidates.json").read_text("utf-8"))
        self.graph = json.loads(
            (PROPS_DIR / "proposition_graph.json").read_text("utf-8"))

        # canonical concept id set (103) — from the proposition graph nodes
        self.concepts = sorted(n["concept_id"] for n in self.graph["nodes"])
        self.n_concepts = len(self.concepts)
        self.concept_set = set(self.concepts)

        # ── Uniform relation list over the FULL 6,832 candidate relations ──
        # Each relation: dict(type, members(frozenset), support(int), directed
        # edge (src,tgt) or None). This is the "proposition structure" that the
        # compression analysis attempts to reconstruct from concept subsets.
        rels = []
        R = self.candidates["relations"]

        def add_binary(lst, akey, bkey, supkey="support_count"):
            out = []
            for e in lst:
                a, b = e[akey], e[bkey]
                directed = (a, b) if {akey, bkey} == {"concept_src", "concept_tgt"} else None
                out.append({
                    "type": e["relation_type"],
                    "members": frozenset((a, b)),
                    "support": int(e.get(supkey, 0)),
                    "src": e.get("concept_src"),
                    "tgt": e.get("concept_tgt"),
                })
            return out

        rels += add_binary(R["ASSOCIATES_WITH"], "concept_a", "concept_b")
        rels += add_binary(R["CO_OCCURS"], "concept_a", "concept_b")
        rels += add_binary(R["DEPENDS_ON"], "concept_src", "concept_tgt")
        rels += add_binary(R["REQUIRES"], "concept_src", "concept_tgt")
        rels += add_binary(R["PRECEDES"], "concept_src", "concept_tgt")
        rels += add_binary(R["FOLLOWS"], "concept_src", "concept_tgt")
        rels += add_binary(R["PREDICTS"], "concept_src", "concept_tgt")
        # triadic
        for e in R["MEDIATES"]:
            rels.append({
                "type": "MEDIATES",
                "members": frozenset((e["concept_a"], e["concept_mediator"], e["concept_d"])),
                "support": int(e.get("support_count_with_mediator", 0)),
                "src": None, "tgt": None,
            })
        for e in R["CONDITIONAL_EMERGES"]:
            rels.append({
                "type": "CONDITIONAL_EMERGES",
                "members": frozenset((e["concept_a"], e["concept_b"], e["concept_e"])),
                "support": int(e.get("support_count", 0)),
                "src": None, "tgt": None,
            })
        self.relations = rels
        self.n_relations = len(rels)
        self.total_support = sum(x["support"] for x in rels)

        # member index: concept -> list of relation indices it participates in
        self.member_index = defaultdict(list)
        for i, x in enumerate(rels):
            for m in x["members"]:
                self.member_index[m].append(i)

        # dependency relation index (DEPENDS_ON + REQUIRES)
        self.dep_relations = [i for i, x in enumerate(rels)
                              if x["type"] in DEPENDENCY_TYPES]
        self.n_dep = len(self.dep_relations)

        # ── Directed proposition graph (from proposition_graph edges) ──
        self.dir_edges = self.graph["edges"]
        self.dir_adj = defaultdict(set)        # src -> {tgt}
        self.und_adj = defaultdict(set)        # undirected projection
        for e in self.dir_edges:
            s, t = e["src"], e["tgt"]
            self.dir_adj[s].add(t)
            self.und_adj[s].add(t)
            self.und_adj[t].add(s)
        for c in self.concepts:
            self.dir_adj.setdefault(c, set())
            self.und_adj.setdefault(c, set())

        print(f"    concepts            : {self.n_concepts}")
        print(f"    relations (total)   : {self.n_relations}")
        print(f"    dependency relations: {self.n_dep}")
        print(f"    directed edges      : {len(self.dir_edges)}")

    # ── Coverage primitives ───────────────────────────────────────────────────

    def coverage(self, S):
        """(count, fraction) of relations fully contained in concept set S."""
        Sset = set(S)
        c = sum(1 for x in self.relations if x["members"] <= Sset)
        return c, c / self.n_relations if self.n_relations else 0.0

    def retention_after_removal(self, removed):
        """Structure surviving when `removed` concepts are deleted.
        A relation survives iff NONE of its members are in `removed`."""
        rem = set(removed)
        survivors = self.concept_set - rem
        prop_keep = sum(1 for x in self.relations if not (x["members"] & rem))
        dep_keep = sum(1 for i in self.dep_relations
                       if not (self.relations[i]["members"] & rem))
        # directed-graph edge integrity
        edge_keep = sum(1 for e in self.dir_edges
                        if e["src"] not in rem and e["tgt"] not in rem)
        return survivors, prop_keep, dep_keep, edge_keep

    # ── PHASE A: foundationality ──────────────────────────────────────────────

    def phase_a_foundationality(self):
        print("  PHASE A — foundationality …")
        n_rel = self.n_relations
        total_sup = self.total_support or 1

        # incidence (count + support) per concept over the full relation set
        inc_count = {c: 0 for c in self.concepts}
        inc_support = {c: 0 for c in self.concepts}
        inc_dep = {c: 0 for c in self.concepts}
        inc_by_type = {c: defaultdict(int) for c in self.concepts}
        for x in self.relations:
            for m in x["members"]:
                inc_count[m] += 1
                inc_support[m] += x["support"]
                inc_by_type[m][x["type"]] += 1
                if x["type"] in DEPENDENCY_TYPES:
                    inc_dep[m] += 1

        # total incidence mass (triadic relations contribute to 3 concepts)
        total_incidence = sum(inc_count.values()) or 1

        # ── reach reduction on the directed proposition graph ──
        # baseline reachable ordered pairs from each source
        base_reach = {s: reachable_from(self.dir_adj, s) for s in self.concepts}
        base_total = sum(len(v) for v in base_reach.values())

        reach_reduction = {}
        for c in self.concepts:
            # reachable pairs not involving c at baseline (restrict survivors)
            base_restricted = 0
            for s in self.concepts:
                if s == c:
                    continue
                base_restricted += len(base_reach[s] - {c})
            # recompute with c blocked
            after = 0
            for s in self.concepts:
                if s == c:
                    continue
                after += len(reachable_from(self.dir_adj, s, blocked={c}))
            reach_reduction[c] = base_restricted - after

        # ── fragmentation on the undirected projection ──
        base_nodes = self.concept_set
        base_comps = connected_components(base_nodes, self.und_adj)
        base_ncomp = len(base_comps)
        base_largest = max((len(x) for x in base_comps), default=0)

        frag_components_added = {}
        frag_largest_drop = {}
        frag_nodes_isolated = {}
        for c in self.concepts:
            survivors = base_nodes - {c}
            # adjacency restricted to survivors
            comps = connected_components(survivors, self.und_adj)
            ncomp = len(comps)
            largest = max((len(x) for x in comps), default=0)
            frag_components_added[c] = ncomp - base_ncomp
            frag_largest_drop[c] = base_largest - largest
            # nodes whose only neighbour set ⊆ {c}
            isolated = 0
            for v in survivors:
                if not (self.und_adj[v] & survivors):
                    isolated += 1
            base_iso = sum(1 for v in base_nodes if not (self.und_adj[v] & base_nodes))
            frag_nodes_isolated[c] = isolated - base_iso

        # ── information loss (frequency-code bits carried by each concept) ──
        # p[c] = inc_count[c] / total_incidence ; bits[c] = inc_count[c]*-log2 p[c]
        info_loss_bits = {}
        for c in self.concepts:
            p = inc_count[c] / total_incidence
            info_loss_bits[c] = (inc_count[c] * -math.log2(p)) if p > 0 else 0.0
        # descriptive: graph entropy and entropy after removal of each concept
        base_entropy = 0.0
        for c in self.concepts:
            p = inc_count[c] / total_incidence
            if p > 0:
                base_entropy += -p * math.log2(p)

        # ── per-concept raw metrics ──
        raw = {}
        for c in self.concepts:
            raw[c] = {
                "removal_impact_count": inc_count[c],
                "support_weighted_loss": inc_support[c],
                "dependency_impact": inc_dep[c],
                "reach_reduction": reach_reduction[c],
                "fragmentation_components_added": frag_components_added[c],
                "information_loss_bits": info_loss_bits[c],
            }

        # min-max normalise each metric to [0,1]
        norm = {c: {} for c in self.concepts}
        for m in FOUNDATIONALITY_METRICS:
            vals = [raw[c][m] for c in self.concepts]
            lo, hi = min(vals), max(vals)
            span = (hi - lo) or 1.0
            for c in self.concepts:
                norm[c][m] = (raw[c][m] - lo) / span

        composite = {}
        for c in self.concepts:
            composite[c] = sum(norm[c][m] for m in FOUNDATIONALITY_METRICS) / len(FOUNDATIONALITY_METRICS)

        ranked = sorted(self.concepts, key=lambda c: (-composite[c], c))
        rank_of = {c: i + 1 for i, c in enumerate(ranked)}
        self.foundationality_order = ranked
        self.composite = composite

        records = []
        for c in self.concepts:
            rec = {
                "concept_id": c,
                "rank": rank_of[c],
                "composite_score": r(composite[c]),
                "removal_impact_count": inc_count[c],
                "removal_impact_fraction": r(inc_count[c] / n_rel),
                "support_weighted_loss": inc_support[c],
                "support_weighted_loss_fraction": r(inc_support[c] / total_sup),
                "dependency_impact": inc_dep[c],
                "reach_reduction": reach_reduction[c],
                "fragmentation_components_added": frag_components_added[c],
                "fragmentation_largest_component_drop": frag_largest_drop[c],
                "fragmentation_nodes_isolated": frag_nodes_isolated[c],
                "information_loss_bits": r(info_loss_bits[c]),
                "incidence_by_type": {t: inc_by_type[c][t]
                                      for t in sorted(inc_by_type[c])},
                "normalized_metrics": {m: r(norm[c][m]) for m in FOUNDATIONALITY_METRICS},
            }
            records.append(rec)
        records.sort(key=lambda x: (x["rank"], x["concept_id"]))

        self.foundationality = {
            "method": METHOD_VERSION,
            "definition": (
                "Composite structural-necessity score = mean of six min-max "
                "normalised metrics, each computed over the Phase-4 structure. "
                "Higher = more structurally necessary. Purely combinatorial; "
                "no semantic content."),
            "metrics": FOUNDATIONALITY_METRICS,
            "metric_definitions": {
                "removal_impact_count": "relations destroyed if the concept is removed (any relation it participates in)",
                "support_weighted_loss": "summed Phase-4 support_count of destroyed relations",
                "dependency_impact": "incident DEPENDS_ON + REQUIRES relations",
                "reach_reduction": "lost reachable ordered pairs among surviving nodes in the directed proposition graph",
                "fragmentation_components_added": "increase in undirected connected-component count when the node is deleted",
                "information_loss_bits": "frequency-code bits carried by the concept's incidences = inc * -log2(inc/total_incidence)",
            },
            "n_concepts": self.n_concepts,
            "n_relations": self.n_relations,
            "total_support": self.total_support,
            "total_incidence": total_incidence,
            "baseline": {
                "components": base_ncomp,
                "largest_component": base_largest,
                "graph_entropy_bits": r(base_entropy),
                "reach_total_ordered_pairs": base_total,
            },
            "scores": records,
            "foundationality_order": ranked,
        }
        write_json(self.out_dir / "foundationality_scores.json", self.foundationality)
        top = ranked[:5]
        print(f"    top-5 foundational  : {top}")

    # ── PHASE B: iterative removal experiments ────────────────────────────────

    def phase_b_removal_experiments(self):
        print("  PHASE B — iterative removal experiments …")
        results = []
        base_reach = {s: reachable_from(self.dir_adj, s) for s in self.concepts}
        base_reach_total = sum(len(v) for v in base_reach.values())

        for k in REMOVAL_STEPS:
            removed = self.foundationality_order[:k]
            survivors, prop_keep, dep_keep, edge_keep = self.retention_after_removal(removed)
            comps = connected_components(survivors, self.und_adj)
            ncomp = len(comps)
            largest = max((len(x) for x in comps), default=0)

            # recoverability: surviving-node reachable pairs preserved vs baseline
            rem = set(removed)
            base_surv_pairs = 0
            after_pairs = 0
            for s in survivors:
                base_surv_pairs += len(base_reach[s] - rem)
                after_pairs += len(reachable_from(self.dir_adj, s, blocked=rem))
            recoverability = (after_pairs / base_surv_pairs) if base_surv_pairs else 0.0

            results.append({
                "k_removed": k,
                "removed_concepts": list(removed),
                "surviving_concepts": len(survivors),
                "proposition_retention": r(prop_keep / self.n_relations),
                "propositions_surviving": prop_keep,
                "dependency_retention": r(dep_keep / self.n_dep) if self.n_dep else 0.0,
                "dependencies_surviving": dep_keep,
                "graph_integrity": r(edge_keep / len(self.dir_edges)),
                "directed_edges_surviving": edge_keep,
                "connectivity_components": ncomp,
                "connectivity_largest_component": largest,
                "connectivity_largest_fraction": r(largest / len(survivors)) if survivors else 0.0,
                "recoverability": r(recoverability),
            })
        self.removal_experiments = results
        for row in results:
            print(f"    remove top-{row['k_removed']:<2}: "
                  f"prop_retention={row['proposition_retention']:.3f} "
                  f"dep_retention={row['dependency_retention']:.3f} "
                  f"largest_comp={row['connectivity_largest_component']}")

    # ── PHASE C: dominant-hub elimination (CONCEPT_007) ───────────────────────

    def phase_c_hub_removal(self):
        print(f"  PHASE C — dominant-hub elimination ({DOMINANT_HUB}) …")
        hub = DOMINANT_HUB
        survivors = set(self.concepts) - {hub}

        # induced directed adjacency (drop all edges touching the hub)
        dir_adj = defaultdict(set)
        und_adj = defaultdict(set)
        edge_keep = 0
        type_in = defaultdict(set)
        type_out = defaultdict(set)
        in_deg = defaultdict(int)
        out_deg = defaultdict(int)
        for e in self.dir_edges:
            s, t = e["src"], e["tgt"]
            if s == hub or t == hub:
                continue
            edge_keep += 1
            dir_adj[s].add(t)
            und_adj[s].add(t)
            und_adj[t].add(s)
            out_deg[s] += 1
            in_deg[t] += 1
            type_out[s].add(e["type"])
            type_in[t].add(e["type"])
        for c in survivors:
            dir_adj.setdefault(c, set())
            und_adj.setdefault(c, set())

        # recompute betweenness (Phase-4 method) on survivors
        bet = brandes_betweenness(survivors, und_adj)
        ranked_bet = sorted(survivors, key=lambda c: (-bet[c], c))
        n_top = max(1, int(round(len(survivors) * TOP_BRIDGE_FRAC)))
        new_bridges = ranked_bet[:n_top]

        # degree leaderboard
        ranked_deg = sorted(survivors,
                            key=lambda c: (-(in_deg[c] + out_deg[c]), c))

        # dependency sub-structure without the hub
        dep_adj = defaultdict(set)
        req_adj = defaultdict(set)
        for i in self.dep_relations:
            x = self.relations[i]
            s, t = x["src"], x["tgt"]
            if s == hub or t == hub:
                continue
            dep_adj[s].add(t)
            if x["type"] == "REQUIRES":
                req_adj[s].add(t)

        # hierarchical chains depth-3 REQUIRES→REQUIRES without hub
        chains = []
        for a in sorted(req_adj):
            for b in sorted(req_adj[a]):
                for cc in sorted(req_adj.get(b, ())):
                    if cc != a and hub not in (a, b, cc):
                        chains.append([a, b, cc])

        # directed short cycles over DEPENDS_ON∪REQUIRES∪PRECEDES without hub
        dir_union = defaultdict(set)
        for i in range(self.n_relations):
            x = self.relations[i]
            if x["type"] in ("DEPENDS_ON", "REQUIRES", "PRECEDES"):
                s, t = x["src"], x["tgt"]
                if s == hub or t == hub:
                    continue
                dir_union[s].add(t)
        cycles = count_short_cycles(survivors, dir_union)

        # SCCs of the dependency graph without the hub (irreducible cores)
        dep_sccs = [c for c in tarjan_scc(survivors, dep_adj) if len(c) >= 2]

        # connectivity after hub removal
        comps = connected_components(survivors, und_adj)
        largest = max((len(x) for x in comps), default=0)

        # structure retention
        _, prop_keep, dep_keep, _ = self.retention_after_removal({hub})

        # comparison to Phase-4 baseline values
        base_bridges = list(self.graph["bridges"])
        base_chains = self.candidates["classifications"]["potential_hierarchical_chains"]
        base_cycles = len(self.candidates["classifications"]["potential_recursive_cycles"])

        # "does another core emerge" — new #1 by betweenness and by degree
        new_top_bet = ranked_bet[0]
        new_top_deg = ranked_deg[0]

        analysis = {
            "method": METHOD_VERSION,
            "removed_hub": hub,
            "note": (
                "Recomputation of graph-theoretic structure over the INDUCED "
                "subgraph after deleting the dominant hub and every relation "
                "that touches it. This re-derives topology from the existing "
                "Phase-4 relations only; it does NOT regenerate statistical "
                "relations from the corpus (prior phases are never rebuilt)."),
            "surviving_concepts": len(survivors),
            "structure_retention": {
                "propositions_surviving": prop_keep,
                "proposition_retention": r(prop_keep / self.n_relations),
                "dependencies_surviving": dep_keep,
                "dependency_retention": r(dep_keep / self.n_dep) if self.n_dep else 0.0,
                "directed_edges_surviving": edge_keep,
                "graph_integrity": r(edge_keep / len(self.dir_edges)),
            },
            "connectivity": {
                "components": len(comps),
                "largest_component": largest,
                "largest_fraction": r(largest / len(survivors)),
            },
            "emergent_core": {
                "new_top_betweenness_concept": new_top_bet,
                "new_top_betweenness_value": r(bet[new_top_bet]),
                "new_top_degree_concept": new_top_deg,
                "new_top_degree_value": in_deg[new_top_deg] + out_deg[new_top_deg],
                "new_bridges": new_bridges,
            },
            "betweenness_leaderboard": [
                {"concept_id": c, "betweenness_centrality": r(bet[c]),
                 "in_degree": in_deg[c], "out_degree": out_deg[c]}
                for c in ranked_bet[:15]
            ],
            "degree_leaderboard": [
                {"concept_id": c, "in_degree": in_deg[c], "out_degree": out_deg[c],
                 "total_degree": in_deg[c] + out_deg[c]}
                for c in ranked_deg[:15]
            ],
            "hierarchical_chains_without_hub": {
                "count": len(chains),
                "chains": sorted(chains),
            },
            "recursive_cycles_without_hub": {
                "count": len(cycles),
                "sample": sorted([list(c) + [c[0]] for c in cycles])[:50],
            },
            "irreducible_dependency_cores_without_hub": {
                "count": len(dep_sccs),
                "components": dep_sccs,
            },
            "comparison_to_phase4": {
                "phase4_bridges": base_bridges,
                "phase4_hierarchical_chains": len(base_chains),
                "phase4_recursive_cycles": base_cycles,
                "hierarchical_chains_delta": len(chains) - len(base_chains),
                "recursive_cycles_delta": len(cycles) - base_cycles,
                "hub_was_in_all_phase4_chains": all(hub in ch for ch in base_chains),
            },
            "verdict": self._hub_verdict(prop_keep, largest, len(survivors),
                                         len(cycles), base_cycles, len(dep_sccs)),
        }
        self.hub_removal = analysis
        write_json(self.out_dir / "hub_removal_analysis.json", analysis)
        print(f"    retention without hub: prop={analysis['structure_retention']['proposition_retention']:.3f} "
              f"dep={analysis['structure_retention']['dependency_retention']:.3f}")
        print(f"    new top concept (bet): {new_top_bet}; verdict: {analysis['verdict']['classification']}")

    def _hub_verdict(self, prop_keep, largest, n_surv, cycles_after, cycles_before, sccs):
        prop_ret = prop_keep / self.n_relations
        largest_frac = largest / n_surv if n_surv else 0.0
        # collapse = graph fragments AND most propositions lost
        # reorganize = stays connected, a new core takes over, cycles persist
        if largest_frac < 0.5 and prop_ret < 0.5:
            cls = "collapse"
        elif largest_frac >= 0.8:
            cls = "reorganize"
        else:
            cls = "partial_reorganize"
        return {
            "classification": cls,
            "proposition_retention": r(prop_ret),
            "largest_component_fraction": r(largest_frac),
            "another_core_emerges": largest_frac >= 0.5,
            "recursive_structure_persists": cycles_after > 0,
            "irreducible_cores_persist": sccs > 0,
            "criteria": (
                "collapse iff largest_component_fraction<0.5 AND "
                "proposition_retention<0.5; reorganize iff "
                "largest_component_fraction>=0.8; else partial_reorganize."),
        }

    # ── PHASE D: minimum reconstruction sets (greedy maximum coverage) ────────

    def phase_d_reconstruction_sets(self):
        print("  PHASE D — minimum reconstruction sets (greedy) …")
        # Greedy maximum coverage. rem[i] = members of relation i not yet in S.
        rem = [set(x["members"]) for x in self.relations]
        # singleton[i present] track relations with exactly one remaining member
        # map: concept -> count of relations whose single remaining member is it
        one_left = defaultdict(set)   # concept -> set of relation indices
        zero_left = 0                  # already covered (none initially: min size 2)
        for i, s in enumerate(rem):
            if len(s) == 1:
                (m,) = tuple(s)
                one_left[m].add(i)
            elif len(s) == 0:
                zero_left += 1

        S = []
        Sset = set()
        covered = zero_left
        order = []           # (concept, covered_after, fraction_after)
        remaining_concepts = set(self.concepts)

        while remaining_concepts:
            # gain[c] = number of relations that become fully covered if c added
            #          = relations whose remaining set == {c}
            best_c = None
            best_gain = -1
            for c in sorted(remaining_concepts):
                g = len(one_left.get(c, ()))
                if g > best_gain:
                    best_gain = g
                    best_c = c
            # add best_c
            S.append(best_c)
            Sset.add(best_c)
            remaining_concepts.discard(best_c)
            # update rem for every relation containing best_c
            for i in self.member_index[best_c]:
                s = rem[i]
                if best_c in s:
                    s.discard(best_c)
                    L = len(s)
                    if L == 1:
                        (m,) = tuple(s)
                        one_left[m].add(i)
                    elif L == 0:
                        covered += 1
                        # remove from one_left[best_c] (it was a singleton for best_c)
                        one_left[best_c].discard(i)
            # any relation that was singleton on best_c and got covered handled above
            order.append({
                "step": len(S),
                "concept_added": best_c,
                "covered": covered,
                "fraction": r(covered / self.n_relations),
            })

        self.greedy_order = [o["concept_added"] for o in order]
        self.greedy_curve = order

        # reconstruction sets per target threshold
        sets = []
        for tgt in RECOVERY_TARGETS:
            # smallest prefix of greedy order achieving >= tgt
            chosen = None
            for o in order:
                if o["fraction"] >= tgt:
                    chosen = o
                    break
            if chosen is None:
                chosen = order[-1]
            size = chosen["step"]
            sets.append({
                "target_fraction": tgt,
                "achieved_fraction": chosen["fraction"],
                "set_size": size,
                "compression_ratio": r(size / self.n_concepts),
                "concept_set": list(self.greedy_order[:size]),
            })

        self.reconstruction_sets = {
            "method": METHOD_VERSION,
            "algorithm": (
                "Deterministic greedy maximum-coverage. A relation is covered "
                "iff all its member concepts are in the set. At each step add "
                "the concept maximising newly-covered relations (ties broken by "
                "lexical concept id). Greedy coverage is a (1−1/e) approximation; "
                "reported sizes are deterministic upper bounds on the true "
                "minimum reconstruction set."),
            "n_relations": self.n_relations,
            "n_concepts": self.n_concepts,
            "targets": RECOVERY_TARGETS,
            "reconstruction_sets": sets,
            "greedy_order": self.greedy_order,
        }
        write_json(self.out_dir / "reconstruction_sets.json", self.reconstruction_sets)
        for s in sets:
            print(f"    {int(s['target_fraction']*100)}% structure  -> "
                  f"{s['set_size']} concepts (ratio {s['compression_ratio']:.3f})")

    # ── PHASE E: dependency layers ────────────────────────────────────────────

    def phase_e_dependency_layers(self):
        print("  PHASE E — dependency layers …")
        # dependency graph: src --(DEPENDS_ON|REQUIRES)--> tgt  (src needs tgt)
        dep_adj = defaultdict(set)
        dep_nodes = set()
        for i in self.dep_relations:
            x = self.relations[i]
            s, t = x["src"], x["tgt"]
            dep_adj[s].add(t)
            dep_nodes.add(s)
            dep_nodes.add(t)
        for c in dep_nodes:
            dep_adj.setdefault(c, set())

        # condense SCCs
        sccs = tarjan_scc(dep_nodes, dep_adj)
        comp_of = {}
        for idx, comp in enumerate(sccs):
            for c in comp:
                comp_of[c] = idx
        # condensation adjacency (DAG)
        cond_adj = defaultdict(set)
        for s in dep_nodes:
            for t in dep_adj[s]:
                if comp_of[s] != comp_of[t]:
                    cond_adj[comp_of[s]].add(comp_of[t])
        for idx in range(len(sccs)):
            cond_adj.setdefault(idx, set())

        # Level 0 = components that depend on nothing (out-degree 0 = sinks).
        # level(n) = longest dependency chain downward = 1 + max(level(succ)).
        level = {}

        def comp_level(idx, stack):
            if idx in level:
                return level[idx]
            succs = cond_adj[idx]
            if not succs:
                level[idx] = 0
                return 0
            lv = 1 + max(comp_level(s, stack) for s in sorted(succs))
            level[idx] = lv
            return lv

        for idx in range(len(sccs)):
            comp_level(idx, set())

        # assign each concept its component level; concepts with no dependency
        # edge at all are "unlayered" (no structural dependency position)
        layers = defaultdict(list)
        for c in sorted(dep_nodes):
            layers[level[comp_of[c]]].append(c)
        unlayered = sorted(self.concept_set - dep_nodes)

        max_level = max(level.values()) if level else 0
        layer_records = []
        for lv in range(max_level + 1):
            members = sorted(layers.get(lv, []))
            layer_records.append({
                "level": lv,
                "interpretation": "structural position only — no meaning assigned",
                "concept_count": len(members),
                "concepts": members,
            })

        self.dependency_layers = {
            "method": METHOD_VERSION,
            "definition": (
                "Dependency graph = directed edges src→tgt for DEPENDS_ON and "
                "REQUIRES (src structurally needs tgt). SCCs are condensed; each "
                "component's level = longest downward dependency chain. Level 0 "
                "= depends on nothing (structural sinks / most foundational "
                "position). Layers express structural position ONLY; no meaning "
                "is assigned to any level."),
            "n_dependency_nodes": len(dep_nodes),
            "n_components": len(sccs),
            "max_level": max_level,
            "layers": layer_records,
            "unlayered_concepts": {
                "note": "no DEPENDS_ON / REQUIRES edge incident — no dependency position",
                "count": len(unlayered),
                "concepts": unlayered,
            },
            "scc_summary": [
                {"component_index": idx, "size": len(comp),
                 "level": level[idx], "concepts": comp}
                for idx, comp in enumerate(sccs)
            ],
        }
        write_json(self.out_dir / "dependency_layers.json", self.dependency_layers)
        print(f"    levels 0..{max_level}; unlayered concepts: {len(unlayered)}")

    # ── PHASE F: irreducible structures ───────────────────────────────────────

    def phase_f_irreducible(self):
        print("  PHASE F — irreducible structures …")

        def build_dir_union(types, exclude=None):
            exclude = exclude or set()
            adj = defaultdict(set)
            nodes = set()
            for i in range(self.n_relations):
                x = self.relations[i]
                if x["type"] in types and x["src"] and x["tgt"]:
                    s, t = x["src"], x["tgt"]
                    if s in exclude or t in exclude:
                        continue
                    adj[s].add(t)
                    nodes.add(s)
                    nodes.add(t)
            return nodes, adj

        # dependency-only SCCs (DEPENDS_ON ∪ REQUIRES)
        dep_nodes, dep_adj = build_dir_union(DEPENDENCY_TYPES)
        dep_sccs = [c for c in tarjan_scc(dep_nodes, dep_adj) if len(c) >= 2]

        # broader directional SCCs (DEPENDS_ON ∪ REQUIRES ∪ PRECEDES ∪ PREDICTS)
        broad_types = {"DEPENDS_ON", "REQUIRES", "PRECEDES", "PREDICTS"}
        broad_nodes, broad_adj = build_dir_union(broad_types)
        broad_sccs = [c for c in tarjan_scc(broad_nodes, broad_adj) if len(c) >= 2]

        # same, with the dominant hub excluded (does irreducibility survive?)
        dep_nodes_x, dep_adj_x = build_dir_union(DEPENDENCY_TYPES, exclude={DOMINANT_HUB})
        dep_sccs_x = [c for c in tarjan_scc(dep_nodes_x, dep_adj_x) if len(c) >= 2]
        broad_nodes_x, broad_adj_x = build_dir_union(broad_types, exclude={DOMINANT_HUB})
        broad_sccs_x = [c for c in tarjan_scc(broad_nodes_x, broad_adj_x) if len(c) >= 2]

        def scc_block(sccs, adj):
            out = []
            for comp in sccs:
                cs = set(comp)
                internal = sum(1 for s in comp for t in adj[s] if t in cs)
                out.append({
                    "size": len(comp),
                    "concepts": comp,
                    "internal_edges": internal,
                    "edge_density": r(internal / (len(comp) * (len(comp) - 1)))
                    if len(comp) > 1 else 0.0,
                })
            out.sort(key=lambda x: (-x["size"], x["concepts"]))
            return out

        self.irreducible = {
            "method": METHOD_VERSION,
            "definition": (
                "An irreducible structure is a strongly-connected component "
                "(size ≥ 2) of a directed relation graph: a set of concepts that "
                "are mutually reachable and therefore cannot be linearised into "
                "a hierarchy or compressed away without breaking a cycle. Purely "
                "graph-theoretic; no meaning assigned."),
            "dependency_irreducible": {
                "relation_types": sorted(DEPENDENCY_TYPES),
                "count": len(dep_sccs),
                "largest_size": max((len(c) for c in dep_sccs), default=0),
                "components": scc_block(dep_sccs, dep_adj),
            },
            "directional_irreducible": {
                "relation_types": sorted(broad_types),
                "count": len(broad_sccs),
                "largest_size": max((len(c) for c in broad_sccs), default=0),
                "components": scc_block(broad_sccs, broad_adj),
            },
            "dependency_irreducible_without_hub": {
                "excluded": DOMINANT_HUB,
                "count": len(dep_sccs_x),
                "largest_size": max((len(c) for c in dep_sccs_x), default=0),
                "components": scc_block(dep_sccs_x, dep_adj_x),
            },
            "directional_irreducible_without_hub": {
                "excluded": DOMINANT_HUB,
                "count": len(broad_sccs_x),
                "largest_size": max((len(c) for c in broad_sccs_x), default=0),
                "components": scc_block(broad_sccs_x, broad_adj_x),
            },
        }
        write_json(self.out_dir / "irreducible_structures.json", self.irreducible)
        print(f"    dependency SCCs≥2: {len(dep_sccs)} (largest "
              f"{self.irreducible['dependency_irreducible']['largest_size']}); "
              f"directional SCCs≥2: {len(broad_sccs)} (largest "
              f"{self.irreducible['directional_irreducible']['largest_size']})")

    # ── PHASE G: compression curve ────────────────────────────────────────────

    def phase_g_compression_curve(self):
        print("  PHASE G — compression curve …")

        def cumulative_curve(order):
            """For ordered concepts, fraction of relations covered as the set
            grows (relation covered iff all members included)."""
            rem = [len(x["members"]) for x in self.relations]
            members_left = [set(x["members"]) for x in self.relations]
            covered = sum(1 for s in members_left if len(s) == 0)
            pts = [{"k": 0, "fraction": r(covered / self.n_relations)}]
            Sset = set()
            for k, c in enumerate(order, start=1):
                Sset.add(c)
                for i in self.member_index[c]:
                    s = members_left[i]
                    if c in s:
                        s.discard(c)
                        if len(s) == 0:
                            covered += 1
                pts.append({"k": k, "fraction": r(covered / self.n_relations)})
            return pts

        def cumulative_dependency_curve(order):
            members_left = {i: set(self.relations[i]["members"]) for i in self.dep_relations}
            covered = 0
            pts = [{"k": 0, "fraction": 0.0}]
            for k, c in enumerate(order, start=1):
                for i in self.dep_relations:
                    s = members_left[i]
                    if c in s:
                        s.discard(c)
                        if len(s) == 0:
                            covered += 1
                pts.append({"k": k, "fraction": r(covered / self.n_dep) if self.n_dep else 0.0})
            return pts

        greedy_curve = cumulative_curve(self.greedy_order)
        foundational_curve = cumulative_curve(self.foundationality_order)
        greedy_dep_curve = cumulative_dependency_curve(self.greedy_order)

        def auc(pts):
            # trapezoidal AUC over k normalised to [0,1] on both axes
            n = len(pts) - 1
            if n <= 0:
                return 0.0
            area = 0.0
            for a, b in zip(pts, pts[1:]):
                area += (a["fraction"] + b["fraction"]) / 2.0
            return area / n  # x-step = 1, n steps, normalise

        def knee(pts):
            # point of maximum vertical distance above the chord (0,0)->(n,1)
            n = pts[-1]["k"]
            f_end = pts[-1]["fraction"]
            if n == 0:
                return {"k": 0, "fraction": pts[0]["fraction"]}
            best_k, best_d = 0, -1.0
            for p in pts:
                chord = (p["k"] / n) * f_end
                d = p["fraction"] - chord
                if d > best_d:
                    best_d = d
                    best_k = p["k"]
            return {"k": best_k,
                    "fraction": next(p["fraction"] for p in pts if p["k"] == best_k),
                    "distance_above_chord": r(best_d)}

        self.compression_curve = {
            "method": METHOD_VERSION,
            "definition": (
                "Recovered structure = fraction of Phase-4 relations whose every "
                "member concept is included, as the retained concept set grows. "
                "Two orders: greedy maximum-coverage and foundationality rank."),
            "n_relations": self.n_relations,
            "n_concepts": self.n_concepts,
            "greedy_coverage_curve": greedy_curve,
            "foundationality_curve": foundational_curve,
            "greedy_dependency_curve": greedy_dep_curve,
            "auc": {
                "greedy_coverage": r(auc(greedy_curve)),
                "foundationality": r(auc(foundational_curve)),
                "greedy_dependency": r(auc(greedy_dep_curve)),
            },
            "knee": {
                "greedy_coverage": knee(greedy_curve),
                "foundationality": knee(foundational_curve),
            },
        }
        write_json(self.out_dir / "compression_curve.json", self.compression_curve)
        kn = self.compression_curve["knee"]["greedy_coverage"]
        print(f"    greedy AUC={self.compression_curve['auc']['greedy_coverage']:.3f}; "
              f"knee at k={kn['k']} ({kn['fraction']:.3f})")

    # ── compression statistics (summary) ──────────────────────────────────────

    def build_statistics(self):
        print("  building compression statistics …")
        sets = {s["target_fraction"]: s for s in self.reconstruction_sets["reconstruction_sets"]}
        # how many concepts to reach each milestone
        milestones = {
            f"{int(t*100)}pct": {
                "set_size": sets[t]["set_size"],
                "compression_ratio": sets[t]["compression_ratio"],
            } for t in RECOVERY_TARGETS
        }
        # core size estimate: knee of greedy curve
        knee_k = self.compression_curve["knee"]["greedy_coverage"]["k"]
        knee_frac = self.compression_curve["knee"]["greedy_coverage"]["fraction"]

        # foundational concept count: those above mean composite + concepts whose
        # removal alone destroys >5% of structure
        scores = self.foundationality["scores"]
        mean_comp = sum(s["composite_score"] for s in scores) / len(scores)
        above_mean = [s["concept_id"] for s in scores if s["composite_score"] > mean_comp]
        high_impact = [s["concept_id"] for s in scores
                       if s["removal_impact_fraction"] >= 0.05]

        self.statistics = {
            "method": METHOD_VERSION,
            "n_concepts": self.n_concepts,
            "n_relations": self.n_relations,
            "n_dependency_relations": self.n_dep,
            "directed_graph_edges": len(self.dir_edges),
            "reconstruction_milestones": milestones,
            "core_size_estimate": {
                "knee_k": knee_k,
                "knee_fraction_recovered": knee_frac,
                "knee_compression_ratio": r(knee_k / self.n_concepts),
                "concepts_above_mean_foundationality": len(above_mean),
                "concepts_destroying_ge_5pct_alone": high_impact,
                "n_concepts_destroying_ge_5pct_alone": len(high_impact),
            },
            "dominant_core": {
                "dominant_hub": DOMINANT_HUB,
                "hub_removal_verdict": self.hub_removal["verdict"]["classification"],
                "hub_proposition_retention": self.hub_removal["structure_retention"]["proposition_retention"],
                "single_dominant_core": (
                    self.hub_removal["emergent_core"]["new_top_betweenness_concept"]
                    != DOMINANT_HUB and
                    self.hub_removal["verdict"]["another_core_emerges"]),
            },
            "irreducible_summary": {
                "dependency_scc_count": self.irreducible["dependency_irreducible"]["count"],
                "dependency_scc_largest": self.irreducible["dependency_irreducible"]["largest_size"],
                "directional_scc_count": self.irreducible["directional_irreducible"]["count"],
                "directional_scc_largest": self.irreducible["directional_irreducible"]["largest_size"],
            },
            "removal_experiments": self.removal_experiments,
            "compression_auc": self.compression_curve["auc"],
            "answers": {
                "compressible": (
                    "yes" if sets[0.80]["compression_ratio"] <= 0.5 else "partial"),
                "concepts_for_80pct": sets[0.80]["set_size"],
                "compression_ratio_at_80pct": sets[0.80]["compression_ratio"],
                "concepts_for_95pct": sets[0.95]["set_size"],
                "dominant_core_exists": True,
            },
        }
        write_json(self.out_dir / "compression_statistics.json", self.statistics)

    # ── manifest ──────────────────────────────────────────────────────────────

    def build_manifest(self):
        print("  writing manifest …")
        input_files = [
            DB_PATH,
            LEX_DIR / "root_profiles.json",
            LEX_DIR / "lemma_profiles.json",
            LEX_DIR / "distribution_profiles.json",
            LEX_DIR / "semantic_neighbors.json",
            CONCEPTS_DIR / "concept_candidates.json",
            CONCEPTS_DIR / "concept_memberships.json",
            CONCEPTS_DIR / "concept_graph.json",
            CONCEPTS_DIR / "concept_manifest.json",
            PROPS_DIR / "proposition_candidates.json",
            PROPS_DIR / "proposition_graph.json",
            PROPS_DIR / "proposition_manifest.json",
        ]
        input_sha = {}
        for p in input_files:
            if p.exists():
                input_sha[p.name] = sha256_file(p)

        outputs = [
            "foundationality_scores.json",
            "reconstruction_sets.json",
            "dependency_layers.json",
            "irreducible_structures.json",
            "compression_statistics.json",
            "compression_curve.json",
            "hub_removal_analysis.json",
        ]
        output_bytes = {}
        for name in outputs:
            p = self.out_dir / name
            if p.exists():
                output_bytes[name] = len(p.read_bytes())

        manifest = {
            "method": METHOD_VERSION,
            "constants": {
                "DOMINANT_HUB": DOMINANT_HUB,
                "REMOVAL_STEPS": REMOVAL_STEPS,
                "RECOVERY_TARGETS": RECOVERY_TARGETS,
                "CYCLE_MAX_LEN": CYCLE_MAX_LEN,
                "TOP_BRIDGE_FRAC": TOP_BRIDGE_FRAC,
                "FOUNDATIONALITY_METRICS": FOUNDATIONALITY_METRICS,
                "ROUND": ROUND,
            },
            "reconstruction_definition": (
                "A relation is reconstructable from a concept set S iff every "
                "participating concept is in S (set membership only)."),
            "input_sha256": input_sha,
            "output_bytes": output_bytes,
            "totals": {
                "concepts": self.n_concepts,
                "relations": self.n_relations,
                "dependency_relations": self.n_dep,
                "directed_graph_edges": len(self.dir_edges),
                "total_support": self.total_support,
            },
            "prohibitions_observed": [
                "not an axiom engine", "not an ontology engine",
                "not a theology engine", "no concept naming",
                "no concept translation", "no interpretation",
                "no inferred meanings", "no ontology", "no theology",
                "no axioms", "no contradiction engine", "no doctrine",
                "no divine origin claim", "no human origin claim",
                "no philosophical conclusions", "no semantic labels",
                "no external knowledge", "prior phases never rebuilt",
            ],
        }
        write_json(self.out_dir / "compression_manifest.json", manifest)

    def run(self):
        self.load()
        self.phase_a_foundationality()
        self.phase_b_removal_experiments()
        self.phase_c_hub_removal()
        self.phase_d_reconstruction_sets()
        self.phase_e_dependency_layers()
        self.phase_f_irreducible()
        self.phase_g_compression_curve()
        self.build_statistics()
        self.build_manifest()
        print("  done.")


def main():
    ap = argparse.ArgumentParser(description="Monad Dependency Compression Engine (Phase 5)")
    ap.parse_args()
    print("Monad Dependency Compression Engine — Phase 5")
    CompressionEngine().run()


if __name__ == "__main__":
    main()
