#!/usr/bin/env python3
"""
Monad — Phase 9: Structural Motif Discovery Engine
==================================================

Purpose
-------
Test — never assume — whether the Quranic network is organised around recurring
*structural motifs*: recurring directed subgraph patterns over the discovered
relational network. The goal is NOT concepts, NOT principles, NOT meanings — only
recurring relational structures. Motifs carry opaque ids `MOTIF_001…`; none is
named, translated, or interpreted. No theology, doctrine, ontology, apologetics,
intention, authorship, or origin claim is produced. Significance is never claimed
without evidence. Phases 1–8 are read and hashed but never rebuilt.

Operational definition (standard network-motif analysis)
--------------------------------------------------------
A motif is an **isomorphism class of small connected directed subgraph** over the
Phase-4 proposition graph (the discovered relational network), collapsed to a
simple directed graph (A→B iff any directed relation A→B exists; symmetric
relations such as ASSOCIATES_WITH yield mutual edges). Two motif sizes are
catalogued:
  * **dyads (2 nodes):** mutual (A↔B), asymmetric (A→B).
  * **triads (3 nodes):** the connected directed 3-node isomorphism classes,
    classified by canonical (minimum-permutation) adjacency code.

Each class is described by a neutral *structural* signature (edge/dyad profile,
cycle/triangle/path role) — a graph-theoretic descriptor, not a name or meaning.

Inputs (read-only)
------------------
    generated/propositions/proposition_graph.json        (the relational network)
    generated/compression/irreducible_structures.json    (concept SCCs)
    generated/principles/principle_candidates.json        (concept→principle)
    generated/principles/irreducible_principles.json      (principle SCC)

Method
------
Deterministic, pure-stdlib, byte-identically reproducible. Significance uses a
fixed-seed degree-preserving directed null model; stability uses deterministic
edge-subsampling perturbation.
"""

import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

METHOD = "phase9-motifs-1.0"
ROUND = 6

HUB = "CONCEPT_007"
NULL_SAMPLES = 20
NULL_SWAP_FACTOR = 10
SEED = 20260606
PERTURB_LEVELS = [0.05, 0.10]
TARGETS = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
# falsification thresholds
MIN_FREQUENCY = 30          # a motif must recur at least this many times
MIN_DISTINCT_CONCEPTS = 10  # must recur across at least this many distinct concepts
MIN_STABILITY = 0.5         # retained-fraction-vs-expected under perturbation
MIN_HUB_SURVIVAL = 0.1      # fraction of instances surviving hub removal

PROHIBITIONS = [
    "no meanings assigned",
    "no motif names",
    "no motif translation",
    "no theology",
    "no doctrine",
    "no ontology",
    "no apologetics",
    "no divine origin inferred",
    "no human origin inferred",
    "no intention inferred",
    "no authorship inferred",
    "no significance claimed without evidence",
    "motifs are opaque structural patterns only",
    "prior phases never rebuilt or modified",
]


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


# ── triad canonical classification ──────────────────────────────────────────────

_PERM3 = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
_ORDERED = [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]


def triad_code(triple, D):
    """Canonical 6-bit code (min over the 6 node permutations) of the directed
    adjacency among the 3 nodes. Order of bits: e01,e02,e10,e12,e20,e21."""
    a, b, c = triple
    # directed adjacency among the three actual nodes
    nodes = (a, b, c)
    edge = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    Da, Db, Dc = D.get(a, ()), D.get(b, ()), D.get(c, ())
    Ds = (Da, Db, Dc)
    for i in range(3):
        di = Ds[i]
        for j in range(3):
            if i != j and nodes[j] in di:
                edge[i][j] = 1
    best = None
    for p in _PERM3:
        bits = 0
        for (i, j) in _ORDERED:
            bits = (bits << 1) | edge[p[i]][p[j]]
        if best is None or bits < best:
            best = bits
    return best


def dyad_code(a, b, D):
    """'mutual' or 'asym' for an adjacent pair."""
    ab = b in D.get(a, ())
    ba = a in D.get(b, ())
    return "mutual" if (ab and ba) else "asym"


def decode_signature(code):
    """Neutral structural descriptor of a triad canonical code."""
    bits = [(code >> (5 - i)) & 1 for i in range(6)]
    e01, e02, e10, e12, e20, e21 = bits
    pairs = [(e01, e10), (e02, e20), (e12, e21)]
    mutual = sum(1 for x, y in pairs if x and y)
    asym = sum(1 for x, y in pairs if (x ^ y))
    adjacent = sum(1 for x, y in pairs if x or y)
    edges = sum(bits)
    out_deg = [e01 + e02, e10 + e12, e20 + e21]
    in_deg = [e10 + e20, e01 + e21, e02 + e12]
    cycle = (e01 and e12 and e20) or (e02 and e21 and e10)
    is_triangle = adjacent == 3
    is_path = adjacent == 2
    # descriptor
    if is_triangle:
        if cycle and mutual == 0:
            desc = "triad:triangle:3-cycle"
        elif mutual == 3:
            desc = "triad:triangle:fully-mutual"
        elif cycle:
            desc = "triad:triangle:cyclic-mixed"
        else:
            desc = "triad:triangle:transitive"
    elif is_path:
        # center = node touching both adjacent pairs
        deg_adj = [0, 0, 0]
        for (x, y), (i, j) in zip(pairs, [(0, 1), (0, 2), (1, 2)]):
            if x or y:
                deg_adj[i] += 1
                deg_adj[j] += 1
        center = deg_adj.index(2)
        if mutual == 2:
            desc = "triad:path:mutual"
        elif out_deg[center] == 2:
            desc = "triad:path:out-fork"
        elif in_deg[center] == 2:
            desc = "triad:path:in-merge"
        else:
            desc = "triad:path:chain"
    else:
        desc = "triad:disconnected"
    return {"edges": edges, "mutual_dyads": mutual, "asym_dyads": asym,
            "adjacent_pairs": adjacent, "has_directed_3cycle": bool(cycle),
            "is_triangle": is_triangle, "is_path": is_path,
            "max_out_degree": max(out_deg), "max_in_degree": max(in_deg),
            "descriptor": desc}


class MotifEngine:
    def __init__(self, props, comp, principles, out):
        self.props_dir = Path(props)
        self.comp_dir = Path(comp)
        self.princ_dir = Path(principles)
        self.out_dir = Path(out)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    # ── load + build graph ──────────────────────────────────────────────────────

    def load(self):
        print("  loading Phase-4 proposition graph …")
        pg = json.loads((self.props_dir / "proposition_graph.json").read_text("utf-8"))
        self.edges_typed = pg["edges"]
        self.D = defaultdict(set)
        self.dep_D = defaultdict(set)        # DEPENDS_ON ∪ REQUIRES directed
        for e in self.edges_typed:
            self.D[e["src"]].add(e["tgt"])
            if e["type"] in ("DEPENDS_ON", "REQUIRES"):
                self.dep_D[e["src"]].add(e["tgt"])
        self.nodes = sorted(set(self.D) | {t for s in self.D for t in self.D[s]})
        self.U = defaultdict(set)
        for a in self.D:
            for b in self.D[a]:
                self.U[a].add(b)
                self.U[b].add(a)
        self.n_directed_pairs = sum(len(v) for v in self.D.values())
        self.und_pairs = sorted({(min(a, b), max(a, b)) for a in self.U for b in self.U[a]})

        print("  loading Phase-5 concept SCCs …")
        irr = json.loads((self.comp_dir / "irreducible_structures.json").read_text("utf-8"))
        self.concept_sccs = [c["concepts"] for c in irr["dependency_irreducible"]["components"]]
        self.directional_scc = (irr["directional_irreducible"]["components"][0]["concepts"]
                                if irr["directional_irreducible"]["components"] else [])

        print("  loading Phase-8 principles …")
        pc = json.loads((self.princ_dir / "principle_candidates.json").read_text("utf-8"))["principles"]
        self.concept_principle = {}
        for pid, rec in pc.items():
            for c in rec["member_concepts"]:
                self.concept_principle[c] = pid
        self.n_principles = len(pc)
        irrp = json.loads((self.princ_dir / "irreducible_principles.json").read_text("utf-8"))
        # union of concepts in the largest irreducible principle cluster
        self.principle_scc_concepts = []
        if irrp["irreducible_principle_clusters"]:
            cluster = irrp["irreducible_principle_clusters"][0]["principles"]
            self.principle_scc_concepts = sorted(
                c for c in self.nodes if self.concept_principle.get(c) in set(cluster))
        print(f"    nodes={len(self.nodes)} directed-pairs={self.n_directed_pairs} "
              f"undirected-pairs={len(self.und_pairs)}")

    # ── census helpers ──────────────────────────────────────────────────────────

    def triad_census(self, D, U, nodeset=None, want_instances=False):
        """Return Counter(code->freq), and optionally code->list of triples."""
        if nodeset is None:
            allowed = set(U.keys())
        else:
            allowed = set(nodeset)
        seen = set()
        cnt = Counter()
        inst = defaultdict(list) if want_instances else None
        for a in sorted(allowed):
            nbrs = sorted(x for x in U.get(a, ()) if x in allowed)
            for b, c in combinations(nbrs, 2):
                key = tuple(sorted((a, b, c)))
                if key in seen:
                    continue
                seen.add(key)
                code = triad_code(key, D)
                cnt[code] += 1
                if want_instances:
                    inst[code].append(key)
        return cnt, inst

    def dyad_census(self, D, und_pairs):
        cnt = Counter()
        inst = defaultdict(list)
        for (a, b) in und_pairs:
            code = dyad_code(a, b, D)
            cnt[code] += 1
            inst[code].append((a, b))
        return cnt, inst

    # ── randomization (degree-preserving directed null) ─────────────────────────

    def _randomized_D(self, rng):
        edges = sorted((a, b) for a in self.D for b in self.D[a])
        eset = set(edges)
        m = len(edges)
        swaps = NULL_SWAP_FACTOR * m
        for _ in range(swaps):
            i = rng.randrange(m)
            j = rng.randrange(m)
            if i == j:
                continue
            a, b = edges[i]
            c, d = edges[j]
            if len({a, b, c, d}) < 4:
                continue
            if (a, d) in eset or (c, b) in eset:
                continue
            eset.discard((a, b))
            eset.discard((c, d))
            eset.add((a, d))
            eset.add((c, b))
            edges[i] = (a, d)
            edges[j] = (c, b)
        D = defaultdict(set)
        U = defaultdict(set)
        for (a, b) in eset:
            D[a].add(b)
            U[a].add(b)
            U[b].add(a)
        return D, U

    def significance(self, observed):
        print("  computing significance vs degree-preserving null …")
        rng = random.Random(SEED)
        sums = defaultdict(float)
        sqs = defaultdict(float)
        for s in range(NULL_SAMPLES):
            D, U = self._randomized_D(rng)
            cnt, _ = self.triad_census(D, U)
            for code in observed:
                v = cnt.get(code, 0)
                sums[code] += v
                sqs[code] += v * v
        z = {}
        for code in observed:
            mean = sums[code] / NULL_SAMPLES
            var = max(0.0, sqs[code] / NULL_SAMPLES - mean * mean)
            std = var ** 0.5
            z[code] = r((observed[code] - mean) / std) if std > 1e-9 else None
            z[code + 1000000] = (r(mean), r(std))  # stash null stats under offset key
        return z

    # ── stability (perturbation) ────────────────────────────────────────────────

    def stability(self, observed_triad):
        print("  computing stability under edge-subsampling perturbation …")
        edges = sorted((a, b) for a in self.D for b in self.D[a])
        result = {}
        per_level = {}
        for p in PERTURB_LEVELS:
            keep_n = int(round(len(edges) * (1 - p)))
            # deterministic subsample: keep every edge except a strided drop set
            drop_every = max(2, int(round(1 / p)))
            kept = [e for i, e in enumerate(edges) if i % drop_every != 0]
            D = defaultdict(set)
            U = defaultdict(set)
            for (a, b) in kept:
                D[a].add(b)
                U[a].add(b)
                U[b].add(a)
            cnt, _ = self.triad_census(D, U)
            per_level[p] = cnt
        for code, obs in observed_triad.items():
            # expected retention if instances were independent of perturbation:
            # a triad with k edges survives with prob ~ (1-p)^k; use mean edges of class
            sig = decode_signature(code)
            k = sig["edges"]
            retained = []
            for p in PERTURB_LEVELS:
                exp = obs * ((1 - p) ** k)
                got = per_level[p].get(code, 0)
                retained.append(min(2.0, got / exp) if exp > 0 else 0.0)
            result[code] = r(sum(retained) / len(retained))
        return result

    # ── PHASE A/B: catalog ──────────────────────────────────────────────────────

    def catalog(self):
        print("  PHASE A/B — motif extraction & catalog …")
        self.triad_cnt, self.triad_inst = self.triad_census(self.D, self.U, want_instances=True)
        self.dyad_cnt, self.dyad_inst = self.dyad_census(self.D, self.und_pairs)
        self.total_triads = sum(self.triad_cnt.values())
        self.total_dyads = sum(self.dyad_cnt.values())

        self.z = self.significance(self.triad_cnt)
        self.stab = self.stability(self.triad_cnt)

        # build ordered motif list: all triad classes + 2 dyad classes, by frequency desc
        entries = []
        for code, freq in self.triad_cnt.items():
            entries.append(("triad", code, freq))
        for code, freq in self.dyad_cnt.items():
            entries.append(("dyad", code, freq))
        entries.sort(key=lambda t: (-t[2], 0 if t[0] == "triad" else 1, str(t[1])))

        self.motifs = {}        # motif_id -> record
        self.motif_code = {}    # motif_id -> ("triad"/"dyad", code)
        catalog = {}
        for i, (kind, code, freq) in enumerate(entries):
            mid = f"MOTIF_{i + 1:03d}"
            self.motif_code[mid] = (kind, code)
            if kind == "triad":
                instances = self.triad_inst[code]
                size = 3
                sig = decode_signature(code)
                edges_involved = self._triad_edges(instances)
                z = self.z.get(code)
                stab = self.stab.get(code)
            else:
                instances = self.dyad_inst[code]
                size = 2
                sig = {"descriptor": f"dyad:{'mutual' if code == 'mutual' else 'asymmetric'}",
                       "edges": 2 if code == "mutual" else 1}
                edges_involved = self._dyad_edges(instances)
                z = None
                stab = None
            concepts = sorted({c for inst in instances for c in inst})
            principles = sorted({self.concept_principle.get(c) for c in concepts
                                 if self.concept_principle.get(c)})
            dep_edges = sum(1 for (u, v) in edges_involved if v in self.dep_D.get(u, ()))
            rec = {
                "size": size,
                "kind": kind,
                "canonical_code": code if kind == "dyad" else f"{code:06b}",
                "structural_signature": sig,
                "frequency": freq,
                "support": freq,
                "stability": stab,
                "significance_zscore": z,
                "n_participating_concepts": len(concepts),
                "n_participating_propositions": len(edges_involved),
                "n_participating_dependencies": dep_edges,
                "participating_concepts": concepts,
                "participating_principles": principles,
                "example_instances": [list(x) for x in instances[:5]],
            }
            self.motifs[mid] = rec
            catalog[mid] = rec
        self.motif_ids = list(self.motifs.keys())
        return {"method": METHOD,
                "definition": ("Motifs are isomorphism classes of connected directed subgraphs "
                               "(2-node dyads, 3-node triads) over the Phase-4 proposition graph. "
                               "Opaque ids; structural_signature is a graph descriptor, not a "
                               "name or meaning."),
                "n_motifs": len(catalog),
                "n_triad_classes": len(self.triad_cnt),
                "n_dyad_classes": len(self.dyad_cnt),
                "total_triad_instances": self.total_triads,
                "total_dyad_instances": self.total_dyads,
                "motifs": catalog}

    def _triad_edges(self, instances):
        es = set()
        for (a, b, c) in instances:
            for u, v in ((a, b), (b, a), (a, c), (c, a), (b, c), (c, b)):
                if v in self.D.get(u, ()):
                    es.add((u, v))
        return es

    def _dyad_edges(self, instances):
        es = set()
        for (a, b) in instances:
            if b in self.D.get(a, ()):
                es.add((a, b))
            if a in self.D.get(b, ()):
                es.add((b, a))
        return es

    # ── statistics ───────────────────────────────────────────────────────────────

    def statistics(self):
        # secondary censuses: dependency graph + concept-undirected
        dep_U = defaultdict(set)
        for a in self.dep_D:
            for b in self.dep_D[a]:
                dep_U[a].add(b)
                dep_U[b].add(a)
        dep_triads, _ = self.triad_census(self.dep_D, dep_U)
        return {"method": METHOD,
                "proposition_graph": {
                    "nodes": len(self.nodes),
                    "directed_pairs": self.n_directed_pairs,
                    "undirected_pairs": len(self.und_pairs),
                    "mutual_dyads": self.dyad_cnt.get("mutual", 0),
                    "asymmetric_dyads": self.dyad_cnt.get("asym", 0),
                    "connected_triads": self.total_triads,
                    "triad_classes": len(self.triad_cnt),
                },
                "dependency_subgraph": {
                    "directed_pairs": sum(len(v) for v in self.dep_D.values()),
                    "connected_triads": sum(dep_triads.values()),
                    "triad_classes": len(dep_triads),
                },
                "triad_class_frequencies": {f"{c:06b}": f for c, f in
                                            sorted(self.triad_cnt.items(), key=lambda t: -t[1])},
                "most_common_motif": max(self.motif_ids,
                                         key=lambda m: self.motifs[m]["frequency"]),
                "most_stable_triad_motif": max(
                    (m for m in self.motif_ids if self.motifs[m]["kind"] == "triad"),
                    key=lambda m: self.motifs[m]["stability"] or 0)}

    # ── PHASE C: coverage ─────────────────────────────────────────────────────────

    def coverage(self):
        print("  PHASE C — motif coverage …")
        n_concepts = 103
        n_props = self.n_directed_pairs
        n_deps = sum(len(v) for v in self.dep_D.values())
        out = {}
        for mid in self.motif_ids:
            rec = self.motifs[mid]
            out[mid] = {
                "size": rec["size"],
                "concept_coverage": r(rec["n_participating_concepts"] / n_concepts),
                "proposition_coverage": r(rec["n_participating_propositions"] / n_props),
                "dependency_coverage": r(rec["n_participating_dependencies"] / n_deps) if n_deps else 0.0,
                "principle_coverage": r(len(rec["participating_principles"]) / self.n_principles),
            }
        # collective coverage by all motifs
        all_concepts = set()
        all_props = set()
        for mid in self.motif_ids:
            all_concepts.update(self.motifs[mid]["participating_concepts"])
        return {"method": METHOD,
                "n_concepts": n_concepts, "n_propositions": n_props, "n_dependencies": n_deps,
                "collective_concept_coverage": r(len(all_concepts) / n_concepts),
                "principles": None,
                "motifs": out}

    # ── PHASE D: compression ───────────────────────────────────────────────────────

    def compression(self):
        print("  PHASE D — motif compression …")
        # universe = connected triad instances; rank triad motifs by frequency
        triad_motifs = [m for m in self.motif_ids if self.motifs[m]["kind"] == "triad"]
        triad_motifs.sort(key=lambda m: -self.motifs[m]["frequency"])
        cum = 0
        order = []
        for m in triad_motifs:
            cum += self.motifs[m]["frequency"]
            order.append({"motif_id": m, "cumulative_fraction": r(cum / self.total_triads),
                          "set_size": len(order) + 1})
        sets = []
        for t in TARGETS:
            k = next((o["set_size"] for o in order if o["cumulative_fraction"] >= t), None)
            sets.append({"target_fraction": t, "motifs_required": k,
                         "compression_ratio": r(k / len(triad_motifs)) if k else None,
                         "motif_set": [o["motif_id"] for o in order[:k]] if k else None})
        return {"method": METHOD,
                "universe": "connected triad instances",
                "total_triad_instances": self.total_triads,
                "n_triad_classes": len(triad_motifs),
                "targets": TARGETS,
                "greedy_order": order,
                "minimum_sets": sets}

    # ── PHASE E: replacement test ─────────────────────────────────────────────────

    def replacement(self):
        print("  PHASE E — motif replacement test …")
        out = {}
        for mid in self.motif_ids:
            rec = self.motifs[mid]
            if rec["kind"] == "triad":
                instances = self.triad_inst[self.motif_code[mid][1]]
            else:
                instances = self.dyad_inst[self.motif_code[mid][1]]
            node_freq = Counter(c for inst in instances for c in inst)
            n_inst = len(instances)
            max_share = (max(node_freq.values()) / n_inst) if n_inst else 0.0
            distinct = len(node_freq)
            # instances avoiding the single most frequent participant
            top_node = max(node_freq, key=lambda c: node_freq[c]) if node_freq else None
            without_top = sum(1 for inst in instances if top_node not in inst)
            survives = (distinct >= MIN_DISTINCT_CONCEPTS and max_share < 0.5)
            out[mid] = {
                "instances": n_inst,
                "distinct_concepts": distinct,
                "max_single_concept_share": r(max_share),
                "most_frequent_participant": top_node,
                "instances_without_top_participant": without_top,
                "instances_without_top_fraction": r(without_top / n_inst) if n_inst else 0.0,
                "survives_replacement": survives,
            }
        return {"method": METHOD,
                "definition": ("Motifs are concept-agnostic isomorphism classes; a motif survives "
                               "replacement iff it recurs across many distinct concepts "
                               "(>=%d) with no single concept dominating its instances "
                               "(<50%%)." % MIN_DISTINCT_CONCEPTS),
                "motifs": out}

    # ── PHASE F: hub removal ───────────────────────────────────────────────────────

    def hub_removal(self):
        print("  PHASE F — hub removal test …")
        nodeset = [n for n in self.nodes if n != HUB]
        cnt, _ = self.triad_census(self.D, self.U, nodeset=nodeset)
        out = {}
        for mid in self.motif_ids:
            kind, code = self.motif_code[mid]
            if kind != "triad":
                continue
            before = self.triad_cnt.get(code, 0)
            after = cnt.get(code, 0)
            retained = (after / before) if before else 0.0
            if retained >= 0.5:
                status = "survives"
            elif retained <= 0.05:
                status = "collapses"
            else:
                status = "weakened"
            out[mid] = {"frequency_with_hub": before, "frequency_without_hub": after,
                        "retained_fraction": r(retained), "status": status}
        # share of relative composition shift
        total_after = sum(cnt.values())
        emergent = []
        for mid in out:
            code = self.motif_code[mid][1]
            share_before = self.triad_cnt.get(code, 0) / self.total_triads
            share_after = cnt.get(code, 0) / total_after if total_after else 0.0
            if share_after > share_before * 1.25:
                emergent.append(mid)
        return {"method": METHOD,
                "removed": HUB,
                "total_triads_with_hub": self.total_triads,
                "total_triads_without_hub": total_after,
                "triads_lost": self.total_triads - total_after,
                "triads_lost_fraction": r((self.total_triads - total_after) / self.total_triads),
                "emergent_motifs": sorted(emergent),
                "motifs": out}

    # ── PHASE G: SCC test ──────────────────────────────────────────────────────────

    def scc_analysis(self):
        print("  PHASE G — SCC persistence test …")
        scopes = {}
        # largest concept dependency SCC
        big = max(self.concept_sccs, key=len) if self.concept_sccs else []
        scopes["concept_scc_largest"] = big
        scopes["directional_scc"] = self.directional_scc
        scopes["principle_scc_concepts"] = self.principle_scc_concepts
        out = {}
        for name, nodeset in scopes.items():
            if not nodeset:
                out[name] = {"size": 0, "connected_triads": 0, "triad_classes": 0, "motifs": {}}
                continue
            cnt, _ = self.triad_census(self.D, self.U, nodeset=set(nodeset))
            total = sum(cnt.values())
            motif_freq = {}
            for mid in self.motif_ids:
                kind, code = self.motif_code[mid]
                if kind == "triad" and code in cnt:
                    motif_freq[mid] = cnt[code]
            out[name] = {"size": len(nodeset),
                         "connected_triads": total,
                         "triad_classes_present": len(cnt),
                         "motif_frequencies": dict(sorted(motif_freq.items(),
                                                          key=lambda t: -t[1]))}
        # per-motif persistence: fraction of triad classes appearing in the largest SCC
        return {"method": METHOD,
                "definition": ("Triad census restricted to irreducible SCC node sets. "
                               "Persistence = which motif classes still occur inside each SCC."),
                "scopes": out}

    # ── PHASE H: falsification ──────────────────────────────────────────────────────

    def falsification(self, hub, replace):
        print("  PHASE H — falsification …")
        out = {}
        surv = 0
        for mid in self.motif_ids:
            rec = self.motifs[mid]
            freq = rec["frequency"]
            distinct = rec["n_participating_concepts"]
            stab = rec["stability"]
            kind = rec["kind"]
            # criteria
            recurs = freq >= MIN_FREQUENCY
            broad = distinct >= MIN_DISTINCT_CONCEPTS
            stable = (stab is None) or (stab >= MIN_STABILITY)
            if kind == "triad":
                hub_ret = hub["motifs"].get(mid, {}).get("retained_fraction", 0.0)
                hub_ok = hub_ret >= MIN_HUB_SURVIVAL
            else:
                hub_ok = True
            replaceable = replace["motifs"][mid]["survives_replacement"]
            failures = []
            if not recurs:
                failures.append("non_recurrence")
            if not broad:
                failures.append("narrow_concept_support")
            if not stable:
                failures.append("instability")
            if not hub_ok:
                failures.append("structural_collapse_on_hub_removal")
            if not replaceable:
                failures.append("concept_bound")
            survives = len(failures) == 0
            if survives:
                surv += 1
            out[mid] = {
                "frequency": freq,
                "distinct_concepts": distinct,
                "stability": stab,
                "recurs": recurs,
                "broad_concept_support": broad,
                "stable": stable,
                "survives_hub_removal": hub_ok,
                "survives_replacement": replaceable,
                "failures": failures,
                "survives": survives,
            }
        return {"method": METHOD,
                "definition": ("A motif is falsified as a genuine recurring structural pattern if "
                               "it fails any of: recurrence (freq>=%d), broad concept support "
                               "(>=%d concepts), stability (>=%.2f), hub-removal survival "
                               "(>=%.2f), concept replaceability." %
                               (MIN_FREQUENCY, MIN_DISTINCT_CONCEPTS, MIN_STABILITY, MIN_HUB_SURVIVAL)),
                "n_survive": surv,
                "n_fail": len(self.motif_ids) - surv,
                "motifs": out}

    # ── manifest ───────────────────────────────────────────────────────────────────

    def manifest(self, output_bytes, summary):
        inputs = [
            ("proposition_graph.json", self.props_dir / "proposition_graph.json"),
            ("irreducible_structures.json", self.comp_dir / "irreducible_structures.json"),
            ("principle_candidates.json", self.princ_dir / "principle_candidates.json"),
            ("irreducible_principles.json", self.princ_dir / "irreducible_principles.json"),
        ]
        return {"method": METHOD,
                "constants": {"HUB": HUB, "NULL_SAMPLES": NULL_SAMPLES,
                              "NULL_SWAP_FACTOR": NULL_SWAP_FACTOR, "SEED": SEED,
                              "PERTURB_LEVELS": PERTURB_LEVELS, "TARGETS": TARGETS,
                              "MIN_FREQUENCY": MIN_FREQUENCY,
                              "MIN_DISTINCT_CONCEPTS": MIN_DISTINCT_CONCEPTS,
                              "MIN_STABILITY": MIN_STABILITY,
                              "MIN_HUB_SURVIVAL": MIN_HUB_SURVIVAL, "ROUND": ROUND},
                "input_sha256": {name: sha256_file(p) for name, p in inputs},
                "output_bytes": output_bytes,
                "prohibitions_observed": PROHIBITIONS,
                "totals": summary}

    # ── orchestration ──────────────────────────────────────────────────────────────

    def run(self):
        self.load()
        products = {}
        products["motif_catalog.json"] = self.catalog()
        products["motif_statistics.json"] = self.statistics()
        products["motif_coverage.json"] = self.coverage()
        comp = self.compression()
        products["motif_compression.json"] = comp
        repl = self.replacement()
        products["motif_replacement.json"] = repl
        hub = self.hub_removal()
        products["motif_survival.json"] = hub
        products["motif_scc_analysis.json"] = self.scc_analysis()
        fal = self.falsification(hub, repl)
        products["motif_falsification.json"] = fal

        output_bytes = {}
        for name, obj in products.items():
            output_bytes[name] = write_json(self.out_dir / name, obj)
            print(f"    wrote {name} ({output_bytes[name]} bytes)")

        comp80 = next((s["motifs_required"] for s in comp["minimum_sets"]
                       if s["target_fraction"] == 0.8), None)
        summary = {
            "n_motifs": len(self.motif_ids),
            "n_triad_classes": len(self.triad_cnt),
            "n_dyad_classes": len(self.dyad_cnt),
            "total_triad_instances": self.total_triads,
            "most_common_motif": max(self.motif_ids,
                                     key=lambda m: self.motifs[m]["frequency"]),
            "motifs_for_80pct_triads": comp80,
            "hub_removal_triads_lost_fraction": hub["triads_lost_fraction"],
            "falsification_survive": fal["n_survive"],
            "falsification_fail": fal["n_fail"],
        }
        man = self.manifest(output_bytes, summary)
        output_bytes["motif_manifest.json"] = write_json(
            self.out_dir / "motif_manifest.json", man)
        print(f"    wrote motif_manifest.json ({output_bytes['motif_manifest.json']} bytes)")
        self.summary = summary
        return summary


def main():
    ap = argparse.ArgumentParser(description="Monad Phase 9 — Structural Motif Discovery Engine")
    ap.add_argument("--propositions", default="generated/propositions")
    ap.add_argument("--compression", default="generated/compression")
    ap.add_argument("--principles", default="generated/principles")
    ap.add_argument("--out", default="generated/motifs")
    args = ap.parse_args()
    print(f"Monad Phase 9 — Structural Motif Discovery Engine ({METHOD})")
    eng = MotifEngine(args.propositions, args.compression, args.principles, args.out)
    summary = eng.run()
    print("  done.")
    print(f"  summary: {json.dumps(summary)}")


if __name__ == "__main__":
    main()
