#!/usr/bin/env python3
"""
scripts/build_concepts.py

Monad Concept Discovery Engine — Builder (Phase 3).

Discovers recurring conceptual STRUCTURES that emerge from Quran-internal usage
patterns. A concept here is NOT a word, root, or lemma; it is an emergent cluster
of statistically coherent lexical behaviour. Concepts are DISCOVERED, never
invented, named, interpreted, or explained. Each carries an opaque id
(CONCEPT_001 …); no human-readable meaning, translation, or label is assigned.

The Quran is the only semantic universe. No external dictionary, tafsir,
translation, theology, or pre-trained embedding is consulted. Phase 1/2 outputs
are read but NOT rebuilt.

Usage:
    python scripts/build_concepts.py [--db PATH] [--lex DIR] [--out DIR]

Inputs (read-only):
    generated/monad.db
    generated/lexicon/semantic_neighbors.json    (primary similarity signal)
    generated/lexicon/root_profiles.json
    generated/lexicon/lemma_profiles.json
    generated/lexicon/distribution_profiles.json

Outputs (generated/concepts/):
    concept_candidates.json     members + cohesion/density/separation/stability
    concept_memberships.json    per-concept member lists + inverse entity->concepts
    concept_graph.json          weighted concept-to-concept graph
    concept_centers.json        most central member roots per concept
    concept_statistics.json     global statistics + discovery classifications
    concept_relationships.json  top related concepts + meta-community structure
    concept_manifest.json       reproducibility manifest

Method (all Quran-internal):
    1. Build a mutual k-nearest-neighbour graph over roots from the Phase-2
       semantic confidence scores (edge iff both roots list each other with
       confidence >= MIN_EDGE; weight = min of the two confidences).
    2. Discover overlapping communities by k=4 CLIQUE PERCOLATION (k-clique
       communities), which naturally yields multi-membership.
    3. Recursively split any community larger than MAX_SIZE by re-percolating
       its induced subgraph at a raised threshold — removes single-linkage
       "chaining" through the dense backbone while preserving tight clusters.
    4. Attach lemmas distributionally: a lemma joins a concept when its
       associated roots (and parent root) fall inside the concept's root set.
    5. Score each concept (cohesion, internal density, external separation,
       stability under threshold perturbation) and its surah distribution.
    6. Build the concept graph (shared members + cross semantic overlap) and run
       degree / betweenness / eigenvector centrality and label-propagation
       community structure.

Determinism: no randomness; sorted iteration; fixed thresholds; floats rounded
to ROUND; JSON written sort_keys=True. Re-running on identical inputs yields
byte-identical output (verified by validate_concepts.py).

STRICTLY structural/statistical. Builds no ontology, propositions, contradiction
engine, axioms, theology, interpretation, doctrine, or origin claims, and assigns
no semantic labels.
"""

import argparse
import hashlib
import json
import math
import sqlite3
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "generated" / "monad.db"
DEFAULT_LEX = REPO_ROOT / "generated" / "lexicon"
DEFAULT_OUT = REPO_ROOT / "generated" / "concepts"

# ── Tunable constants (documented; deterministic) ─────────────────────────────

K_CLIQUE       = 4       # clique-percolation order
MIN_EDGE       = 0.30    # minimum mutual semantic confidence for a root edge
MAX_SIZE       = 40      # communities larger than this are recursively split
THR_STEP       = 0.03    # threshold increase per recursive split
THR_CAP        = 0.60    # stop splitting beyond this threshold
PERTURB        = (0.28, 0.32)   # thresholds for stability estimation
LEMMA_THR      = 0.30    # minimum lemma->concept membership confidence
CENTER_TOP     = 5       # center roots stored per concept
REL_TOP        = 8       # related concepts stored per concept
GRAPH_MIN_EDGE = 0.02    # minimum concept-graph edge weight to retain
EIG_ITERS      = 200     # eigenvector-centrality power iterations
LPA_ITERS      = 100     # label-propagation iterations (meta-communities)
ROUND          = 6

METHOD_VERSION = "phase3-concepts-1.0"


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


# ── Builder ───────────────────────────────────────────────────────────────────

class ConceptBuilder:

    def __init__(self, db_path, lex_dir, out_dir):
        self.db_path = Path(db_path)
        self.lex_dir = Path(lex_dir)
        self.out_dir = Path(out_dir)

    # ── Load Phase-1/2 inputs ─────────────────────────────────────────────────

    def load(self):
        print("  loading lexicon + database …")
        sem = json.loads((self.lex_dir / "semantic_neighbors.json").read_text("utf-8"))
        self.root_ar = {}
        self.adj = {}            # root_id -> {neighbor_id: confidence}
        for rid, v in sem["roots"].items():
            self.root_ar[int(rid)] = v["root_arabic"]
            self.adj[int(rid)] = {n["root_id"]: n["confidence"] for n in v["neighbors"]}

        rp = json.loads((self.lex_dir / "root_profiles.json").read_text("utf-8"))
        for rid, v in rp.items():
            self.root_ar.setdefault(int(rid), v["root_arabic"])
        self.root_occ = {int(k): v["occurrence_count"] for k, v in rp.items()}

        lp = json.loads((self.lex_dir / "lemma_profiles.json").read_text("utf-8"))
        self.lemmas = {}
        for lid, v in lp.items():
            self.lemmas[int(lid)] = {
                "arabic": v["lemma_arabic"],
                "root_id": v["root_id"],
                "occ": v["occurrence_count"],
                "neighbor_roots": [(n["root_id"], n["shared_ayahs"])
                                   for n in v["top_neighbor_roots"]],
            }

        dist = json.loads((self.lex_dir / "distribution_profiles.json").read_text("utf-8"))
        self.root_dist = {}
        for rid, v in dist["roots"].items():
            self.root_dist[int(rid)] = {
                "surah": {int(s): c for s, c in v["surah_distribution"].items()},
                "meccan": v["meccan_occurrences"],
                "medinan": v["medinan_occurrences"],
            }

        # input hashes for the manifest
        self.input_hashes = {
            f: sha256_file(self.lex_dir / f) for f in (
                "semantic_neighbors.json", "root_profiles.json",
                "lemma_profiles.json", "distribution_profiles.json")}
        self.input_hashes["monad.db"] = sha256_file(self.db_path)
        print(f"    roots={len(self.adj)} lemmas={len(self.lemmas)}")

    # ── Clustering: mutual-kNN + recursive k-clique percolation ───────────────

    def _mutual_graph(self, members, thr):
        mset = set(members)
        G = defaultdict(dict)
        for a in members:
            for b, c in self.adj.get(a, {}).items():
                if b in mset and c >= thr and self.adj.get(b, {}).get(a, 0.0) >= thr:
                    w = min(c, self.adj[b][a])
                    G[a][b] = w
                    G[b][a] = w
        return G

    @staticmethod
    def _cpm(G, k):
        nodes = sorted(G)
        adjset = {n: set(G[n]) for n in nodes}
        cliques = set()
        for a in nodes:
            na = sorted(x for x in adjset[a] if x > a)
            for combo in combinations(na, k - 1):
                ok = all(combo[j] in adjset[combo[i]]
                         for i in range(len(combo)) for j in range(i + 1, len(combo)))
                if ok:
                    cliques.add(frozenset((a,) + combo))
        cliques = [tuple(sorted(c)) for c in cliques]
        if not cliques:
            return []
        sub_to_clq = defaultdict(list)
        for idx, c in enumerate(cliques):
            for s in combinations(c, k - 1):
                sub_to_clq[s].append(idx)
        parent = list(range(len(cliques)))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for s, cl in sub_to_clq.items():
            for i in range(1, len(cl)):
                rx, ry = find(cl[0]), find(cl[i])
                if rx != ry:
                    parent[max(rx, ry)] = min(rx, ry)
        comms = defaultdict(set)
        for idx, c in enumerate(cliques):
            comms[find(idx)] |= set(c)
        return [sorted(c) for c in comms.values()]

    def _recurse(self, members, thr):
        """Split an oversized community at a raised threshold; keep as-is if it
        cannot be split further."""
        if thr > THR_CAP:
            return [sorted(members)]
        comms = self._cpm(self._mutual_graph(members, thr), K_CLIQUE)
        if not comms:
            return [sorted(members)]
        out = []
        for c in comms:
            if len(c) > MAX_SIZE:
                out.extend(self._recurse(c, round(thr + THR_STEP, 2)))
            else:
                out.append(sorted(c))
        return out

    def _cluster(self, base_thr):
        base = self._cpm(self._mutual_graph(list(self.adj), base_thr), K_CLIQUE)
        final = []
        for c in base:
            if len(c) > MAX_SIZE:
                final.extend(self._recurse(c, round(base_thr + THR_STEP, 2)))
            else:
                final.append(c)
        # de-duplicate identical member sets, deterministic order
        seen, uniq = set(), []
        for c in sorted(final, key=lambda c: (-len(c), c)):
            key = tuple(c)
            if key not in seen:
                seen.add(key)
                uniq.append(c)
        return sorted(uniq, key=lambda c: (-len(c), c))

    def cluster(self):
        print("  discovering concept cores (mutual-kNN + recursive k=4 CPM) …")
        self.base_graph = self._mutual_graph(list(self.adj), MIN_EDGE)
        self.concepts = self._cluster(MIN_EDGE)
        print(f"    concepts={len(self.concepts)} "
              f"covered_roots={len(set().union(*self.concepts)) if self.concepts else 0}")
        # stability: recover under perturbed thresholds
        print("  estimating cluster stability (threshold perturbation) …")
        self.variants = [self._cluster(t) for t in PERTURB]

    # ── Concept metrics ───────────────────────────────────────────────────────

    @staticmethod
    def _jaccard(a, b):
        sa, sb = set(a), set(b)
        u = sa | sb
        return len(sa & sb) / len(u) if u else 0.0

    def _stability(self, members):
        scores = []
        for var in self.variants:
            best = 0.0
            for c in var:
                j = self._jaccard(members, c)
                if j > best:
                    best = j
            scores.append(best)
        return sum(scores) / len(scores) if scores else 0.0

    def _internal_metrics(self, members):
        mset = set(members)
        n = len(members)
        possible = n * (n - 1) / 2 if n > 1 else 1
        internal_w = 0.0
        internal_e = 0
        cut_w = 0.0
        for u in members:
            for v, w in self.base_graph.get(u, {}).items():
                if v in mset:
                    if u < v:
                        internal_w += w
                        internal_e += 1
                else:
                    cut_w += w
        density = internal_e / possible
        cohesion = (internal_w / internal_e) if internal_e else 0.0
        separation = internal_w / (internal_w + cut_w) if (internal_w + cut_w) else 0.0
        return {
            "internal_density": r(density),
            "cohesion_score": r(cohesion),
            "external_separation": r(separation),
            "internal_edges": internal_e,
            "internal_weight": r(internal_w),
            "boundary_weight": r(cut_w),
        }

    def _distribution_profile(self, members):
        surah = defaultdict(int)
        mec = med = 0
        for rid in members:
            d = self.root_dist.get(rid)
            if not d:
                continue
            for s, c in d["surah"].items():
                surah[s] += c
            mec += d["meccan"]
            med += d["medinan"]
        total = sum(surah.values())
        counts = sorted(surah.values(), reverse=True)
        entropy = 0.0
        for c in counts:
            p = c / total
            entropy -= p * math.log2(p)
        sc = len(surah)
        maxe = math.log2(sc) if sc > 1 else 0.0
        return {
            "total_occurrences": total,
            "surah_count": sc,
            "surah_coverage": r(sc / 114.0),
            "evenness": r(entropy / maxe if maxe > 0 else 0.0),
            "top_surah_share": r(counts[0] / total if total else 0.0),
            "meccan_occurrences": mec,
            "medinan_occurrences": med,
            "medinan_fraction": r(med / (mec + med) if (mec + med) else 0.0),
            "surah_distribution": {str(s): surah[s] for s in sorted(surah)},
        }

    def _root_membership_conf(self, rid, members):
        """How much of a root's similarity mass lies inside the concept."""
        mset = set(members)
        total = sum(self.base_graph.get(rid, {}).values())
        inside = sum(w for v, w in self.base_graph.get(rid, {}).items() if v in mset)
        return inside / total if total else 1.0

    def _center_roots(self, members):
        mset = set(members)
        scored = []
        for rid in members:
            strength = sum(w for v, w in self.base_graph.get(rid, {}).items() if v in mset)
            scored.append((rid, strength))
        scored.sort(key=lambda t: (-t[1], t[0]))
        return scored[:CENTER_TOP]

    # ── Lemma attachment ──────────────────────────────────────────────────────

    def attach_lemmas(self):
        print("  attaching lemmas to concepts (distributional + structural) …")
        # root -> set of concept indices
        root_to_concepts = defaultdict(set)
        for i, members in enumerate(self.concepts):
            for rid in members:
                root_to_concepts[rid].add(i)

        self.concept_lemmas = defaultdict(list)   # cid -> [(lemma_id, conf)]
        self.lemma_to_concepts = defaultdict(list)
        concept_rootsets = [set(m) for m in self.concepts]

        for lid, lm in self.lemmas.items():
            parent = lm["root_id"]
            nbrs = lm["neighbor_roots"]
            tot = sum(w for _, w in nbrs)
            # candidate concepts: those containing the parent root or any neighbour root
            cand = set()
            if parent in root_to_concepts:
                cand |= root_to_concepts[parent]
            for nb, _ in nbrs:
                if nb in root_to_concepts:
                    cand |= root_to_concepts[nb]
            for ci in sorted(cand):
                R = concept_rootsets[ci]
                overlap = sum(w for nb, w in nbrs if nb in R)
                align = (overlap / tot) if tot else 0.0
                parent_in = 1.0 if parent in R else 0.0
                conf = 0.5 * align + 0.5 * parent_in
                if conf >= LEMMA_THR:
                    self.concept_lemmas[ci].append((lid, r(conf)))
                    self.lemma_to_concepts[lid].append((ci, r(conf)))
        for ci in self.concept_lemmas:
            self.concept_lemmas[ci].sort(key=lambda t: (-t[1], t[0]))

    # ── Assemble per-concept records ──────────────────────────────────────────

    def assemble_concepts(self):
        print("  assembling concept candidates …")
        self.ids = [f"CONCEPT_{i+1:03d}" for i in range(len(self.concepts))]
        self.records = []
        self.root_to_cids = defaultdict(list)
        for i, members in enumerate(self.concepts):
            cid = self.ids[i]
            metrics = self._internal_metrics(members)
            metrics["cluster_stability"] = r(self._stability(members))
            dist = self._distribution_profile(members)
            centers = self._center_roots(members)
            member_roots = []
            for rid in members:
                conf = r(self._root_membership_conf(rid, members))
                member_roots.append({"root_id": rid, "root_arabic": self.root_ar[rid],
                                     "membership_confidence": conf})
                self.root_to_cids[rid].append((cid, conf))
            member_roots.sort(key=lambda d: (-d["membership_confidence"], d["root_id"]))
            lemmas = self.concept_lemmas.get(i, [])
            self.records.append({
                "concept_id": cid,
                "size_roots": len(members),
                "size_lemmas": len(lemmas),
                "member_roots": member_roots,
                "member_lemmas": [{"lemma_id": lid, "lemma_arabic": self.lemmas[lid]["arabic"],
                                   "membership_confidence": c} for lid, c in lemmas],
                "internal_density": metrics["internal_density"],
                "external_separation": metrics["external_separation"],
                "cluster_stability": metrics["cluster_stability"],
                "cohesion_score": metrics["cohesion_score"],
                "internal_edges": metrics["internal_edges"],
                "boundary_weight": metrics["boundary_weight"],
                "center_roots": [{"root_id": rid, "root_arabic": self.root_ar[rid],
                                  "internal_strength": r(s)} for rid, s in centers],
                "distribution_profile": dist,
            })

    # ── Concept graph ─────────────────────────────────────────────────────────

    def build_concept_graph(self):
        print("  building concept graph + centrality …")
        n = len(self.concepts)
        rootsets = [set(m) for m in self.concepts]
        # cross semantic weight between concepts via base-graph edges
        cross = defaultdict(float)
        root_in = defaultdict(list)
        for i, R in enumerate(rootsets):
            for rid in R:
                root_in[rid].append(i)
        seen_edge = set()
        for u in self.base_graph:
            for v, w in self.base_graph[u].items():
                if u >= v:
                    continue
                cu, cv = root_in.get(u, []), root_in.get(v, [])
                for a in cu:
                    for b in cv:
                        if a == b:
                            continue
                        lo, hi = (a, b) if a < b else (b, a)
                        cross[(lo, hi)] += w

        edges = []
        adjw = defaultdict(dict)
        for i in range(n):
            for j in range(i + 1, n):
                shared = self._jaccard(self.concepts[i], self.concepts[j])
                cw = cross.get((i, j), 0.0)
                only = len(rootsets[i] - rootsets[j]) + len(rootsets[j] - rootsets[i])
                sem_overlap = cw / only if only else 0.0
                weight = 0.5 * shared + 0.5 * min(1.0, sem_overlap)
                if weight < GRAPH_MIN_EDGE:
                    continue
                edges.append({
                    "source": self.ids[i], "target": self.ids[j],
                    "weight": r(weight),
                    "shared_members": r(shared),
                    "semantic_overlap": r(min(1.0, sem_overlap)),
                })
                adjw[i][j] = weight
                adjw[j][i] = weight
        self.cgraph_edges = edges
        self.adjw = adjw

        # ---- centrality ----
        deg = {i: sum(adjw[i].values()) for i in range(n)}
        self.degree_cent = deg
        self.betweenness = self._betweenness(n, adjw)
        self.eigen = self._eigenvector(n, adjw)
        self.meta_comm = self._label_propagation(n, adjw)

    @staticmethod
    def _betweenness(n, adjw):
        """Brandes' algorithm on the weighted graph (distance = 1/weight)."""
        import heapq
        bc = {i: 0.0 for i in range(n)}
        for s in range(n):
            S = []
            P = defaultdict(list)
            sigma = defaultdict(float)
            sigma[s] = 1.0
            dist = {s: 0.0}
            Q = [(0.0, s)]
            visited_order = {}
            while Q:
                d, v = heapq.heappop(Q)
                if v in visited_order:
                    continue
                visited_order[v] = d
                S.append(v)
                for w_, weight in sorted(adjw[v].items()):
                    nd = d + 1.0 / weight
                    if w_ not in dist or nd < dist[w_] - 1e-12:
                        dist[w_] = nd
                        heapq.heappush(Q, (nd, w_))
                        sigma[w_] = sigma[v]
                        P[w_] = [v]
                    elif abs(nd - dist[w_]) <= 1e-12:
                        sigma[w_] += sigma[v]
                        P[w_].append(v)
            delta = defaultdict(float)
            for w_ in reversed(S):
                for v in P[w_]:
                    if sigma[w_] > 0:
                        delta[v] += (sigma[v] / sigma[w_]) * (1.0 + delta[w_])
                if w_ != s:
                    bc[w_] += delta[w_]
        # undirected normalisation
        norm = ((n - 1) * (n - 2)) if n > 2 else 1
        return {i: r(bc[i] / norm) for i in range(n)}

    @staticmethod
    def _eigenvector(n, adjw):
        if n == 0:
            return {}
        x = {i: 1.0 / n for i in range(n)}
        for _ in range(EIG_ITERS):
            nx = {i: 0.0 for i in range(n)}
            for i in range(n):
                for j, w in adjw[i].items():
                    nx[i] += w * x[j]
            norm = math.sqrt(sum(v * v for v in nx.values()))
            if norm == 0:
                break
            nx = {i: nx[i] / norm for i in range(n)}
            if max(abs(nx[i] - x[i]) for i in range(n)) < 1e-12:
                x = nx
                break
            x = nx
        return {i: r(x[i]) for i in range(n)}

    @staticmethod
    def _label_propagation(n, adjw):
        """Deterministic synchronous label propagation; tie-break by lowest
        label. Returns node -> community label."""
        label = {i: i for i in range(n)}
        for _ in range(LPA_ITERS):
            changed = False
            new = dict(label)
            for i in range(n):
                if not adjw[i]:
                    continue
                weights = defaultdict(float)
                for j, w in adjw[i].items():
                    weights[label[j]] += w
                best = max(weights.items(), key=lambda kv: (kv[1], -kv[0]))[0]
                if best != label[i]:
                    new[i] = best
                    changed = True
            label = new
            if not changed:
                break
        # renumber communities deterministically
        remap = {}
        out = {}
        for i in range(n):
            lbl = label[i]
            if lbl not in remap:
                remap[lbl] = len(remap)
            out[i] = remap[lbl]
        return out

    # ── Relationships ─────────────────────────────────────────────────────────

    def build_relationships(self):
        rel = {}
        for i in range(len(self.concepts)):
            partners = sorted(self.adjw[i].items(), key=lambda kv: (-kv[1], kv[0]))[:REL_TOP]
            rel[self.ids[i]] = {
                "meta_community": self.meta_comm[i],
                "related_concepts": [
                    {"concept_id": self.ids[j], "weight": r(w)} for j, w in partners],
            }
        self.relationships = rel

    # ── Discovery classifications ─────────────────────────────────────────────

    def classify(self):
        n = len(self.concepts)
        recs = self.records

        def top_by(key, count=12, reverse=True):
            idx = sorted(range(n), key=lambda i: key(i), reverse=reverse)
            return [self.ids[i] for i in idx[:count]]

        deg = self.degree_cent
        bet = self.betweenness
        cohesive = top_by(lambda i: recs[i]["cohesion_score"])
        connected = top_by(lambda i: deg[i])
        # bridges: high betweenness relative to modest degree
        bridges = sorted(range(n),
                         key=lambda i: (-bet[i], deg[i]))
        bridges = [self.ids[i] for i in bridges if bet[i] > 0][:12]
        isolated = [self.ids[i] for i in range(n) if deg[i] == 0]
        stable = top_by(lambda i: recs[i]["cluster_stability"])
        # global vs localized by surah coverage
        glob = top_by(lambda i: recs[i]["distribution_profile"]["surah_coverage"])
        localized = top_by(lambda i: recs[i]["distribution_profile"]["surah_coverage"],
                           reverse=False)
        rare = top_by(lambda i: recs[i]["distribution_profile"]["total_occurrences"],
                      reverse=False)
        self.classifications = {
            "highly_cohesive": cohesive,
            "highly_connected": connected,
            "bridge_concepts": bridges,
            "isolated_concepts": isolated,
            "highly_stable": stable,
            "global_concepts": glob,
            "localized_concepts": localized,
            "rare_concepts": rare,
        }

    # ── Write everything ──────────────────────────────────────────────────────

    def write(self):
        self.out_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n  writing outputs to {self.out_dir} …")
        n = len(self.concepts)
        files = {}

        files["concept_candidates.json"] = write_json(
            self.out_dir / "concept_candidates.json",
            {"method": METHOD_VERSION, "concept_count": n, "concepts": self.records})

        # memberships: per-concept + inverse entity->concepts
        memberships = {
            "method": METHOD_VERSION,
            "concepts": {
                self.ids[i]: {
                    "member_roots": [
                        {"root_id": d["root_id"], "membership_confidence":
                         d["membership_confidence"]}
                        for d in self.records[i]["member_roots"]],
                    "member_lemmas": [
                        {"lemma_id": d["lemma_id"], "membership_confidence":
                         d["membership_confidence"]}
                        for d in self.records[i]["member_lemmas"]],
                } for i in range(n)},
            "root_memberships": {
                str(rid): [{"concept_id": cid, "membership_confidence": c}
                           for cid, c in sorted(v, key=lambda t: (-t[1], t[0]))]
                for rid, v in sorted(self.root_to_cids.items())},
            "lemma_memberships": {
                str(lid): [{"concept_id": self.ids[ci], "membership_confidence": c}
                           for ci, c in sorted(v, key=lambda t: (-t[1], self.ids[t[0]]))]
                for lid, v in sorted(self.lemma_to_concepts.items())},
        }
        files["concept_memberships.json"] = write_json(
            self.out_dir / "concept_memberships.json", memberships)

        graph = {
            "method": METHOD_VERSION,
            "directed": False,
            "node_count": n,
            "edge_count": len(self.cgraph_edges),
            "edge_attributes": ["weight", "shared_members", "semantic_overlap"],
            "nodes": [
                {"id": self.ids[i], "size_roots": self.records[i]["size_roots"],
                 "size_lemmas": self.records[i]["size_lemmas"],
                 "degree_centrality": r(self.degree_cent[i]),
                 "betweenness_centrality": self.betweenness[i],
                 "eigenvector_centrality": self.eigen[i],
                 "meta_community": self.meta_comm[i]} for i in range(n)],
            "edges": self.cgraph_edges,
        }
        files["concept_graph.json"] = write_json(
            self.out_dir / "concept_graph.json", graph)

        centers = {
            "method": METHOD_VERSION,
            "concepts": {
                self.ids[i]: {
                    "center_roots": self.records[i]["center_roots"],
                    "degree_centrality": r(self.degree_cent[i]),
                    "betweenness_centrality": self.betweenness[i],
                    "eigenvector_centrality": self.eigen[i],
                } for i in range(n)},
        }
        files["concept_centers.json"] = write_json(
            self.out_dir / "concept_centers.json", centers)

        files["concept_relationships.json"] = write_json(
            self.out_dir / "concept_relationships.json",
            {"method": METHOD_VERSION,
             "meta_community_count": len(set(self.meta_comm.values())),
             "relationships": self.relationships})

        # ---- statistics ----
        recs = self.records
        sizes = sorted((rr["size_roots"] for rr in recs), reverse=True)
        covered = set().union(*self.concepts) if self.concepts else set()
        multi_roots = sum(1 for v in self.root_to_cids.values() if len(v) > 1)
        multi_lemmas = sum(1 for v in self.lemma_to_concepts.values() if len(v) > 1)

        def avg(key):
            return r(sum(key(rr) for rr in recs) / len(recs)) if recs else 0.0

        stats = {
            "method": METHOD_VERSION,
            "concept_count": n,
            "roots_clustered": len(covered),
            "roots_total": len(self.adj),
            "root_coverage": r(len(covered) / len(self.adj)) if self.adj else 0.0,
            "lemmas_attached": len(self.lemma_to_concepts),
            "lemmas_total": len(self.lemmas),
            "multi_membership_roots": multi_roots,
            "multi_membership_lemmas": multi_lemmas,
            "size_roots": {"max": sizes[0] if sizes else 0,
                           "min": sizes[-1] if sizes else 0,
                           "mean": r(sum(sizes) / len(sizes)) if sizes else 0,
                           "distribution": sizes},
            "averages": {
                "cohesion_score": avg(lambda x: x["cohesion_score"]),
                "internal_density": avg(lambda x: x["internal_density"]),
                "external_separation": avg(lambda x: x["external_separation"]),
                "cluster_stability": avg(lambda x: x["cluster_stability"]),
                "surah_coverage": avg(lambda x: x["distribution_profile"]["surah_coverage"]),
            },
            "graph": {
                "edge_count": len(self.cgraph_edges),
                "meta_community_count": len(set(self.meta_comm.values())),
                "isolated_concepts": sum(1 for i in range(n) if self.degree_cent[i] == 0),
            },
            "classifications": self.classifications,
        }
        files["concept_statistics.json"] = write_json(
            self.out_dir / "concept_statistics.json", stats)
        self.stats = stats

        manifest = {
            "method": METHOD_VERSION,
            "constants": {
                "K_CLIQUE": K_CLIQUE, "MIN_EDGE": MIN_EDGE, "MAX_SIZE": MAX_SIZE,
                "THR_STEP": THR_STEP, "THR_CAP": THR_CAP, "PERTURB": list(PERTURB),
                "LEMMA_THR": LEMMA_THR, "CENTER_TOP": CENTER_TOP, "REL_TOP": REL_TOP,
                "GRAPH_MIN_EDGE": GRAPH_MIN_EDGE, "EIG_ITERS": EIG_ITERS,
                "LPA_ITERS": LPA_ITERS, "ROUND": ROUND,
            },
            "input_sha256": self.input_hashes,
            "totals": {
                "concept_count": n,
                "roots_clustered": len(covered),
                "lemmas_attached": len(self.lemma_to_concepts),
                "concept_graph_edges": len(self.cgraph_edges),
            },
            "prohibitions_observed": [
                "no ontology", "no propositions", "no contradiction engine",
                "no axioms", "no theology", "no interpretation", "no doctrine",
                "no origin claims", "no concept translation", "no semantic labels",
                "no external knowledge", "concepts discovered not invented",
            ],
            "output_bytes": files,
        }
        files["concept_manifest.json"] = write_json(
            self.out_dir / "concept_manifest.json", manifest)

        for name in sorted(files):
            print(f"    {name:30s} {files[name]:>11,d} bytes")

    # ── Orchestration ─────────────────────────────────────────────────────────

    def run(self):
        print(f"\nBuilding Concept Discovery Engine from {self.lex_dir} …\n")
        self.load()
        self.cluster()
        self.attach_lemmas()
        self.assemble_concepts()
        self.build_concept_graph()
        self.build_relationships()
        self.classify()
        self.write()
        print("\nConcept discovery complete.\n")
        return self.stats


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--lex", default=str(DEFAULT_LEX))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    for p in (Path(args.db), Path(args.lex) / "semantic_neighbors.json"):
        if not p.exists():
            print(f"Required input not found: {p}")
            sys.exit(1)

    ConceptBuilder(args.db, args.lex, args.out).run()


if __name__ == "__main__":
    main()
