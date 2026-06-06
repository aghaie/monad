#!/usr/bin/env python3
"""
Monad — Phase 8: Foundational Principle Discovery Engine
========================================================

Purpose
-------
Test — not assume — whether the discovered Quranic structure can be explained by
a small set of *foundational principles*. A foundational principle is NOT a word,
root, lemma, or concept. It is a **structural pattern** capable of explaining,
generating, or constraining many discovered concepts and propositions. Principles
must emerge from the discovered structure itself; none is invented, imported,
named, translated, or interpreted.

Operational definition (evidence-derived, opaque)
-------------------------------------------------
A principle candidate is a **maximal cohesive structural module** of the
integrated concept graph — the graph whose nodes are the 103 discovered concepts
and whose undirected edge weights combine Phase-3 semantic overlap with Phase-4
proposition weight (each min-max normalised). Modules are discovered by
deterministic greedy modularity maximisation (Clauset–Newman–Moore). Each module
is a higher-order pattern: it constrains the concepts it contains and explains the
propositions internal to it. Modules carry opaque ids `PRINCIPLE_001…`; no module
is named.

Two explanatory senses are reported, never conflated:
  * **internal / self-contained** — a relation is *generated* by a principle iff
    every participating concept lies inside it (Phase-5-style full membership).
  * **incidence / governing** — a principle *governs* a relation iff it contains
    at least one participating concept.

Inputs (read-only)
------------------
    generated/concepts/{concept_graph,concept_relationships}.json
    generated/propositions/{proposition_graph,proposition_candidates}.json
    generated/compression/foundationality_scores.json
    generated/revelation/identity_confidence.json

Outputs
-------
    generated/principles/
        principle_candidates.json      (A)
        principle_coverage.json        (B)
        principle_removal.json         (C)
        principle_reconstruction.json  (D)
        principle_hierarchy.json       (E)
        principle_dependencies.json    (E)
        irreducible_principles.json    (F)
        principle_falsification.json   (G)
        principle_manifest.json

Method
------
Deterministic, pure-stdlib, byte-identically reproducible. No meaning, theology,
doctrine, ontology, apologetics, or origin claim is produced. Success is not
claimed before testing; a small principle set is not forced.
"""

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

METHOD = "phase8-principles-1.0"
ROUND = 6

TARGETS = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
SURVIVE_RETENTION = 0.5    # falsification: a principle survives iff internal relation
                           # retention of its members >= this
DEPENDENCY_TYPES = {"DEPENDS_ON", "REQUIRES"}

PROHIBITIONS = [
    "no semantic meaning assigned",
    "no principle names",
    "no principle translation",
    "no theology",
    "no doctrine",
    "no ontology",
    "no apologetics",
    "no contradiction engine",
    "no divine origin inferred",
    "no human origin inferred",
    "no success claimed before testing",
    "no small principle set forced",
    "principles emerge from discovered structure, never invented or imported",
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


def tarjan_scc(nodes, adj):
    """Iterative Tarjan SCC. Returns list of components (lists), deterministic."""
    index = {}
    low = {}
    onstack = {}
    stack = []
    result = []
    counter = [0]
    for start in nodes:
        if start in index:
            continue
        work = [(start, iter(sorted(adj.get(start, ()))))]
        index[start] = low[start] = counter[0]
        counter[0] += 1
        stack.append(start)
        onstack[start] = True
        while work:
            node, it = work[-1]
            advanced = False
            for w in it:
                if w not in index:
                    index[w] = low[w] = counter[0]
                    counter[0] += 1
                    stack.append(w)
                    onstack[w] = True
                    work.append((w, iter(sorted(adj.get(w, ())))))
                    advanced = True
                    break
                elif onstack.get(w):
                    low[node] = min(low[node], index[w])
            if advanced:
                continue
            if low[node] == index[node]:
                comp = []
                while True:
                    w = stack.pop()
                    onstack[w] = False
                    comp.append(w)
                    if w == node:
                        break
                result.append(sorted(comp))
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
    return result


class PrincipleEngine:
    def __init__(self, concepts, props, comp, revelation, out):
        self.concepts_dir = Path(concepts)
        self.props_dir = Path(props)
        self.comp_dir = Path(comp)
        self.rev_dir = Path(revelation)
        self.out_dir = Path(out)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    # ── load ────────────────────────────────────────────────────────────────────

    def load(self):
        print("  loading Phase-3 concept graph …")
        self.cgraph = json.loads((self.concepts_dir / "concept_graph.json").read_text("utf-8"))
        self.concepts = sorted(n["id"] for n in self.cgraph["nodes"])
        self.n_concepts = len(self.concepts)
        # concept-graph adjacency (semantic overlap) for fragmentation tests
        self.cg_adj = defaultdict(set)
        for e in self.cgraph["edges"]:
            self.cg_adj[e["source"]].add(e["target"])
            self.cg_adj[e["target"]].add(e["source"])

        print("  loading Phase-4 proposition graph + relations …")
        self.pgraph = json.loads((self.props_dir / "proposition_graph.json").read_text("utf-8"))
        self.pcand = json.loads((self.props_dir / "proposition_candidates.json").read_text("utf-8"))

        print("  loading Phase-5 foundationality …")
        found = json.loads((self.comp_dir / "foundationality_scores.json").read_text("utf-8"))
        self.found = {s["concept_id"]: s for s in found["scores"]}

        print("  loading Phase-7 identity anchors (evidence) …")
        self.identity = json.loads(
            (self.rev_dir / "identity_confidence.json").read_text("utf-8"))["concepts"]

        # flatten relations: list of (rtype, participants:tuple)
        self.relations = []
        self.dep_relations = []   # directed (src_concept, tgt_concept) for DEPENDS_ON/REQUIRES
        for rtype, lst in self.pcand["relations"].items():
            for rel in lst:
                ps = tuple(rel[k] for k in rel if k.startswith("concept"))
                self.relations.append((rtype, ps))
                if rtype in DEPENDENCY_TYPES:
                    self.dep_relations.append((rel["concept_src"], rel["concept_tgt"]))
        self.n_relations = len(self.relations)
        print(f"    concepts={self.n_concepts}  relations={self.n_relations}")

    # ── PHASE A: principle discovery (CNM modularity modules) ───────────────────

    def discover(self):
        print("  PHASE A — discovering principle candidates (modularity modules) …")
        # integrated undirected weighted graph
        w = defaultdict(float)
        co_max = max(e["weight"] for e in self.cgraph["edges"])
        for e in self.cgraph["edges"]:
            a, b = e["source"], e["target"]
            w[(min(a, b), max(a, b))] += e["weight"] / co_max
        pw = defaultdict(float)
        for e in self.pgraph["edges"]:
            a, b = e["src"], e["tgt"]
            if a == b:
                continue
            pw[(min(a, b), max(a, b))] += e["weight"]
        pw_max = max(pw.values())
        for k, v in pw.items():
            w[k] += v / pw_max
        self.edge_weight = dict(w)
        self.W = w

        adj = defaultdict(dict)
        for (a, b), v in w.items():
            adj[a][b] = v
            adj[b][a] = v
        m = sum(w.values())
        deg = {c: sum(adj[c].values()) for c in self.concepts}

        comm = {c: c for c in self.concepts}
        members = {c: {c} for c in self.concepts}
        cdeg = dict(deg)

        improved = True
        while improved:
            improved = False
            ce = defaultdict(float)
            for (a, b), v in w.items():
                ca, cb = comm[a], comm[b]
                if ca != cb:
                    ce[(min(ca, cb), max(ca, cb))] += v
            best_gain = 1e-12
            best = None
            for (ca, cb) in sorted(ce.keys()):
                eij = ce[(ca, cb)]
                gain = eij / (2 * m) - 2 * (cdeg[ca] * cdeg[cb]) / ((2 * m) ** 2)
                if gain > best_gain + 1e-15:
                    best_gain = gain
                    best = (ca, cb)
            if best:
                ca, cb = best
                keep, drop = min(ca, cb), max(ca, cb)
                for c in members[drop]:
                    comm[c] = keep
                members[keep] |= members[drop]
                del members[drop]
                cdeg[keep] += cdeg[drop]
                del cdeg[drop]
                improved = True

        # order principles by size desc, then smallest member
        groups = sorted(members.values(), key=lambda s: (-len(s), sorted(s)[0]))
        self.principle_ids = []
        self.principle_members = {}
        self.concept_principle = {}
        for i, g in enumerate(groups):
            pid = f"PRINCIPLE_{i + 1:03d}"
            self.principle_ids.append(pid)
            self.principle_members[pid] = sorted(g)
            for c in g:
                self.concept_principle[c] = pid
        self.n_principles = len(self.principle_ids)

        # modularity of the partition
        deg_comm = defaultdict(float)
        for c in self.concepts:
            deg_comm[self.concept_principle[c]] += deg[c]
        q_intra = sum(2 * v for (a, b), v in w.items()
                      if self.concept_principle[a] == self.concept_principle[b])
        q = q_intra / (2 * m) - sum((d / (2 * m)) ** 2 for d in deg_comm.values())
        self.modularity = r(q)
        self.total_edge_weight = m
        print(f"    principles={self.n_principles}  modularity={self.modularity}")

    # ── relation incidence helpers ──────────────────────────────────────────────

    def _index_relations(self):
        # incident[pid] = set(relation indices touching pid); internal[pid] = fully inside
        self.incident = defaultdict(set)
        self.internal = defaultdict(set)
        self.intra_count = 0
        self.inter_count = 0
        self.rel_principles = []
        for i, (rtype, ps) in enumerate(self.relations):
            pset = {self.concept_principle[p] for p in ps}
            self.rel_principles.append(pset)
            for pid in pset:
                self.incident[pid].add(i)
            if len(pset) == 1:
                pid = next(iter(pset))
                self.internal[pid].add(i)
                self.intra_count += 1
            else:
                self.inter_count += 1
        # dependency incidence
        self.dep_incident = defaultdict(set)
        self.dep_internal = defaultdict(set)
        for j, (s, t) in enumerate(self.dep_relations):
            ps, pt = self.concept_principle[s], self.concept_principle[t]
            self.dep_incident[ps].add(j)
            self.dep_incident[pt].add(j)
            if ps == pt:
                self.dep_internal[ps].add(j)

    # ── PHASE A output ──────────────────────────────────────────────────────────

    def principle_candidates(self):
        out = {}
        for pid in self.principle_ids:
            members = self.principle_members[pid]
            # internal edge weight
            internal_w = sum(v for (a, b), v in self.W.items()
                             if self.concept_principle[a] == pid and self.concept_principle[b] == pid)
            boundary_w = sum(v for (a, b), v in self.W.items()
                             if (self.concept_principle[a] == pid) ^ (self.concept_principle[b] == pid))
            # dominant member concepts by Phase-5 foundationality
            dom = sorted(members, key=lambda c: -self.found.get(c, {}).get("composite_score", 0.0))[:5]
            out[pid] = {
                "size": len(members),
                "member_concepts": members,
                "internal_edge_weight": r(internal_w),
                "boundary_edge_weight": r(boundary_w),
                "dominant_member_concepts": [
                    {"concept_id": c,
                     "foundationality_rank": self.found.get(c, {}).get("rank"),
                     "foundationality_composite": self.found.get(c, {}).get("composite_score"),
                     "identity_anchor_arabic": self.identity.get(c, {}).get("anchor_root_arabic"),
                     "identity_tier": self.identity.get(c, {}).get("tier")}
                    for c in dom],
            }
        return {"method": METHOD,
                "definition": ("A principle is a maximal cohesive structural module of the "
                               "integrated concept graph (Phase-3 semantic overlap ⊕ Phase-4 "
                               "proposition weight), discovered by deterministic greedy modularity "
                               "maximisation. Opaque ids; no names. member-concept anchors are "
                               "evidence, not principle names."),
                "n_principles": self.n_principles,
                "modularity": self.modularity,
                "principles": out}

    # ── PHASE B: explanatory power ──────────────────────────────────────────────

    def coverage(self):
        print("  PHASE B — explanatory power …")
        out = {}
        total_found = sum(s.get("composite_score", 0.0) for s in self.found.values()) or 1.0
        for pid in self.principle_ids:
            members = self.principle_members[pid]
            inc = len(self.incident[pid])
            intern = len(self.internal[pid])
            dep_inc = len(self.dep_incident[pid])
            dep_int = len(self.dep_internal[pid])
            found_sum = sum(self.found.get(c, {}).get("composite_score", 0.0) for c in members)
            # internal cohesion / conductance over relation incidences
            internal_retention = (intern / inc) if inc else 0.0
            out[pid] = {
                "size": len(members),
                "concept_coverage": r(len(members) / self.n_concepts),
                "proposition_coverage_incident": r(inc / self.n_relations),
                "proposition_coverage_internal": r(intern / self.n_relations),
                "relations_incident": inc,
                "relations_internal": intern,
                "dependency_coverage_incident": r(dep_inc / max(1, len(self.dep_relations))),
                "dependency_coverage_internal": r(dep_int / max(1, len(self.dep_relations))),
                "reconstruction_power_internal": r(intern / self.n_relations),
                "compression_contribution": r(found_sum / total_found),
                "internal_relation_retention": r(internal_retention),
            }
        ranked = sorted(self.principle_ids,
                        key=lambda p: -out[p]["proposition_coverage_incident"])
        return {"method": METHOD,
                "n_relations": self.n_relations,
                "global_intra_principle_relations": self.intra_count,
                "global_inter_principle_relations": self.inter_count,
                "global_intra_fraction": r(self.intra_count / self.n_relations),
                "global_inter_fraction": r(self.inter_count / self.n_relations),
                "definition": ("incident = principle contains >=1 participant (governs); internal "
                               "= principle contains all participants (generates). "
                               "compression_contribution = summed Phase-5 foundationality of "
                               "members, normalised."),
                "ranking_by_incident_coverage": ranked,
                "principles": out}

    # ── PHASE C: principle removal ──────────────────────────────────────────────

    def _components_after_removal(self, removed):
        """Connected components in concept-graph after deleting `removed` concepts."""
        present = [c for c in self.concepts if c not in removed]
        seen = set()
        comps = 0
        for c in present:
            if c in seen:
                continue
            comps += 1
            stack = [c]
            seen.add(c)
            while stack:
                u = stack.pop()
                for v in self.cg_adj[u]:
                    if v not in removed and v not in seen:
                        seen.add(v)
                        stack.append(v)
        return comps

    def removal(self):
        print("  PHASE C — principle removal …")
        base_components = self._components_after_removal(set())
        total_support = 0
        rel_support = []
        for (rtype, ps) in self.relations:
            rel_support.append(1)  # uniform structural count
        out = {}
        for pid in self.principle_ids:
            members = set(self.principle_members[pid])
            inc = self.incident[pid]
            dep_inc = self.dep_incident[pid]
            comps = self._components_after_removal(members)
            out[pid] = {
                "size": len(members),
                "relations_lost": len(inc),
                "relations_lost_fraction": r(len(inc) / self.n_relations),
                "dependencies_lost": len(dep_inc),
                "dependencies_lost_fraction": r(len(dep_inc) / max(1, len(self.dep_relations))),
                "reconstruction_loss_internal": len(self.internal[pid]),
                "components_before": base_components,
                "components_after": comps,
                "fragmentation_added": comps - base_components,
            }
        ranked = sorted(self.principle_ids, key=lambda p: (-out[p]["relations_lost"], p))
        return {"method": METHOD,
                "definition": ("Removing a principle deletes all its member concepts; "
                               "relations_lost = relations incident to any member; "
                               "fragmentation_added = increase in concept-graph components."),
                "base_components": base_components,
                "ranking_by_impact": ranked,
                "principles": out}

    # ── PHASE D: minimum principle sets ─────────────────────────────────────────

    def _greedy_curve(self, sets_by_pid, universe_size):
        covered = set()
        order = []
        remaining = set(self.principle_ids)
        while remaining:
            best = max(sorted(remaining),
                       key=lambda p: len(sets_by_pid[p] - covered))
            gain = len(sets_by_pid[best] - covered)
            if gain == 0:
                break
            covered |= sets_by_pid[best]
            order.append({"principle_id": best,
                          "cumulative_fraction": r(len(covered) / universe_size),
                          "set_size": len(order) + 1})
            remaining.discard(best)
        return order

    def reconstruction(self):
        print("  PHASE D — minimum principle sets …")
        inc_order = self._greedy_curve(self.incident, self.n_relations)
        int_order = self._greedy_curve(self.internal, self.n_relations)
        inc_ceiling = inc_order[-1]["cumulative_fraction"] if inc_order else 0.0
        int_ceiling = int_order[-1]["cumulative_fraction"] if int_order else 0.0

        def sets_for(order, ceiling):
            res = []
            for t in TARGETS:
                k = next((o["set_size"] for o in order if o["cumulative_fraction"] >= t), None)
                if k is None:
                    res.append({"target_fraction": t, "reachable": False,
                                "ceiling": ceiling, "set_size": None, "principle_set": None})
                else:
                    res.append({"target_fraction": t, "reachable": True,
                                "set_size": k,
                                "compression_ratio": r(k / self.n_principles),
                                "principle_set": [o["principle_id"] for o in order[:k]]})
            return res

        return {"method": METHOD,
                "n_relations": self.n_relations,
                "n_principles": self.n_principles,
                "definition": ("Greedy maximum-coverage over principles. incidence = relations "
                               "governed (>=1 participant in a chosen principle); internal = "
                               "relations generated (all participants inside one chosen "
                               "principle). The internal ceiling bounds self-contained "
                               "explanation."),
                "targets": TARGETS,
                "incidence_coverage_ceiling": inc_ceiling,
                "internal_coverage_ceiling": int_ceiling,
                "incidence_greedy_order": inc_order,
                "internal_greedy_order": int_order,
                "incidence_minimum_sets": sets_for(inc_order, inc_ceiling),
                "internal_minimum_sets": sets_for(int_order, int_ceiling)}

    # ── PHASE E: hierarchy & dependencies ───────────────────────────────────────

    def _principle_dep_graph(self):
        """Directed principle graph from cross-principle DEPENDS_ON/REQUIRES."""
        edges = defaultdict(int)
        self_loops = defaultdict(int)
        for (s, t) in self.dep_relations:
            ps, pt = self.concept_principle[s], self.concept_principle[t]
            if ps == pt:
                self_loops[ps] += 1
            else:
                edges[(ps, pt)] += 1
        adj = defaultdict(set)
        for (ps, pt) in edges:
            adj[ps].add(pt)
        return edges, dict(self_loops), adj

    def hierarchy(self):
        print("  PHASE E — hierarchy analysis …")
        edges, self_loops, adj = self._principle_dep_graph()
        sccs = tarjan_scc(self.principle_ids, adj)
        scc_of = {}
        for i, comp in enumerate(sccs):
            for p in comp:
                scc_of[p] = i
        # condensation DAG
        cond_adj = defaultdict(set)
        for (ps, pt) in edges:
            if scc_of[ps] != scc_of[pt]:
                cond_adj[scc_of[ps]].add(scc_of[pt])
        # longest-path layering on DAG (level = longest path from a source)
        indeg = defaultdict(int)
        comp_ids = list(range(len(sccs)))
        for u in cond_adj:
            for v in cond_adj[u]:
                indeg[v] += 1
        level = {i: 0 for i in comp_ids}
        # topological order via Kahn
        from collections import deque
        q = deque(sorted(i for i in comp_ids if indeg[i] == 0))
        indeg2 = dict(indeg)
        topo = []
        while q:
            u = q.popleft()
            topo.append(u)
            for v in sorted(cond_adj[u]):
                level[v] = max(level[v], level[u] + 1)
                indeg2[v] -= 1
                if indeg2[v] == 0:
                    q.append(v)
        # cyclic principles = SCCs of size >= 2
        cyclic = [sorted(c) for c in sccs if len(c) >= 2]
        recursive = sorted(self_loops.keys())  # principles with intra-principle dependencies
        layers = defaultdict(list)
        for i in comp_ids:
            layers[level[i]].append(i)
        layer_out = []
        for lv in sorted(layers):
            comp_list = []
            for ci in sorted(layers[lv]):
                comp_list.append({"component_index": ci, "principles": sccs[ci],
                                  "size": len(sccs[ci])})
            layer_out.append({"level": lv, "components": comp_list,
                              "n_principles": sum(len(sccs[ci]) for ci in layers[lv])})
        self.principle_dep_edges = edges
        self.principle_sccs = sccs
        return {"method": METHOD,
                "definition": ("Principle dependency graph lifts Phase-4 DEPENDS_ON/REQUIRES to "
                               "the principle level; SCC condensation + longest-path layering. "
                               "Cyclic principles = SCCs (size>=2); recursive = principles with "
                               "intra-principle dependencies; hierarchy = layers."),
                "n_principle_dependency_edges": len(edges),
                "max_level": max(level.values()) if level else 0,
                "n_layers": len(layer_out),
                "cyclic_principle_clusters": cyclic,
                "recursive_principles": recursive,
                "self_dependency_counts": self_loops,
                "layers": layer_out}

    def dependencies(self):
        edges, self_loops, adj = self._principle_dep_graph()
        edge_list = sorted(
            ({"src": ps, "tgt": pt, "weight": cnt} for (ps, pt), cnt in edges.items()),
            key=lambda d: (-d["weight"], d["src"], d["tgt"]))
        outdeg = defaultdict(int)
        indeg = defaultdict(int)
        for (ps, pt), cnt in edges.items():
            outdeg[ps] += 1
            indeg[pt] += 1
        nodes = []
        for pid in self.principle_ids:
            nodes.append({"principle_id": pid, "in_degree": indeg[pid],
                          "out_degree": outdeg[pid],
                          "self_dependencies": self_loops.get(pid, 0)})
        return {"method": METHOD,
                "directed": True,
                "definition": "principle-level DEPENDS_ON/REQUIRES dependency graph",
                "edge_count": len(edge_list),
                "edges": edge_list,
                "nodes": nodes}

    # ── PHASE F: irreducible principles ─────────────────────────────────────────

    def irreducible(self):
        print("  PHASE F — irreducible principles …")
        sccs = self.principle_sccs
        edges = self.principle_dep_edges
        irr = []
        for comp in sccs:
            if len(comp) >= 2:
                internal = sum(cnt for (ps, pt), cnt in edges.items()
                               if ps in comp and pt in comp)
                irr.append({"principles": sorted(comp), "size": len(comp),
                            "internal_dependency_edges": internal})
        irr.sort(key=lambda d: (-d["size"], d["principles"][0]))
        # irreducible explanatory residue: relations no single principle generates
        residue = self.inter_count
        return {"method": METHOD,
                "definition": ("Irreducible principle clusters = strongly-connected components "
                               "(size>=2) of the principle dependency graph — mutually dependent "
                               "principles that cannot be ordered or reduced. Irreducible "
                               "explanatory residue = relations no single principle generates "
                               "(inter-principle)."),
                "irreducible_principle_clusters": irr,
                "n_irreducible_clusters": len(irr),
                "largest_irreducible_size": irr[0]["size"] if irr else 0,
                "irreducible_explanatory_residue_relations": residue,
                "irreducible_explanatory_residue_fraction": r(residue / self.n_relations)}

    # ── PHASE G: falsification ──────────────────────────────────────────────────

    def falsification(self):
        print("  PHASE G — falsification …")
        out = {}
        survive = fail = 0
        for pid in self.principle_ids:
            members = set(self.principle_members[pid])
            inc = len(self.incident[pid])
            intern = len(self.internal[pid])
            retention = (intern / inc) if inc else 0.0
            leakage = 1.0 - retention
            survives = retention >= SURVIVE_RETENTION
            # contradictory concepts: members whose strongest proposition partner is outside
            contra_concepts = []
            for n in self.pgraph["nodes"]:
                c = n["concept_id"]
                if c not in members:
                    continue
                partners = (n.get("top_out_partners", []) + n.get("top_in_partners", []))
                if partners:
                    strongest = max(partners, key=lambda d: d["weight"])
                    if strongest["concept_id"] not in members:
                        contra_concepts.append({"concept_id": c,
                                                "strongest_partner": strongest["concept_id"],
                                                "partner_principle": self.concept_principle.get(
                                                    strongest["concept_id"]),
                                                "weight": strongest["weight"]})
            contra_concepts.sort(key=lambda d: -d["weight"])
            if survives:
                survive += 1
            else:
                fail += 1
            out[pid] = {
                "size": len(members),
                "internal_relation_retention": r(retention),
                "boundary_leakage": r(leakage),
                "relations_internal": intern,
                "relations_incident": inc,
                "contradicting_member_count": len(contra_concepts),
                "contradicting_member_fraction": r(len(contra_concepts) / len(members)) if members else 0.0,
                "contradicting_members": contra_concepts[:8],
                "survives": survives,
            }
        return {"method": METHOD,
                "definition": ("A principle is falsified as a self-contained constraining pattern "
                               "if its members' relations leak outside more than they stay inside "
                               "(internal_relation_retention < %.2f). contradicting_members = "
                               "members whose strongest proposition partner lies in another "
                               "principle." % SURVIVE_RETENTION),
                "constant_survive_retention": SURVIVE_RETENTION,
                "n_survive": survive,
                "n_fail": fail,
                "principles": out}

    # ── manifest ────────────────────────────────────────────────────────────────

    def manifest(self, output_bytes, summary):
        inputs = [
            ("concept_graph.json", self.concepts_dir / "concept_graph.json"),
            ("concept_relationships.json", self.concepts_dir / "concept_relationships.json"),
            ("proposition_graph.json", self.props_dir / "proposition_graph.json"),
            ("proposition_candidates.json", self.props_dir / "proposition_candidates.json"),
            ("foundationality_scores.json", self.comp_dir / "foundationality_scores.json"),
            ("identity_confidence.json", self.rev_dir / "identity_confidence.json"),
        ]
        return {
            "method": METHOD,
            "constants": {"TARGETS": TARGETS, "SURVIVE_RETENTION": SURVIVE_RETENTION,
                          "ROUND": ROUND},
            "input_sha256": {name: sha256_file(p) for name, p in inputs},
            "output_bytes": output_bytes,
            "prohibitions_observed": PROHIBITIONS,
            "totals": summary,
        }

    # ── orchestration ───────────────────────────────────────────────────────────

    def run(self):
        self.load()
        self.discover()
        self._index_relations()
        products = {}
        products["principle_candidates.json"] = self.principle_candidates()
        cov = self.coverage()
        products["principle_coverage.json"] = cov
        products["principle_removal.json"] = self.removal()
        recon = self.reconstruction()
        products["principle_reconstruction.json"] = recon
        products["principle_hierarchy.json"] = self.hierarchy()
        products["principle_dependencies.json"] = self.dependencies()
        irr = self.irreducible()
        products["irreducible_principles.json"] = irr
        fal = self.falsification()
        products["principle_falsification.json"] = fal

        output_bytes = {}
        for name, obj in products.items():
            output_bytes[name] = write_json(self.out_dir / name, obj)
            print(f"    wrote {name} ({output_bytes[name]} bytes)")

        summary = {
            "n_principles": self.n_principles,
            "modularity": self.modularity,
            "n_relations": self.n_relations,
            "intra_principle_fraction": r(self.intra_count / self.n_relations),
            "inter_principle_fraction": r(self.inter_count / self.n_relations),
            "internal_coverage_ceiling": recon["internal_coverage_ceiling"],
            "incidence_coverage_ceiling": recon["incidence_coverage_ceiling"],
            "n_irreducible_principle_clusters": irr["n_irreducible_clusters"],
            "largest_irreducible_size": irr["largest_irreducible_size"],
            "falsification_survive": fal["n_survive"],
            "falsification_fail": fal["n_fail"],
        }
        man = self.manifest(output_bytes, summary)
        output_bytes["principle_manifest.json"] = write_json(
            self.out_dir / "principle_manifest.json", man)
        print(f"    wrote principle_manifest.json ({output_bytes['principle_manifest.json']} bytes)")
        self.summary = summary
        return summary


def main():
    ap = argparse.ArgumentParser(description="Monad Phase 8 — Foundational Principle Discovery")
    ap.add_argument("--concepts", default="generated/concepts")
    ap.add_argument("--propositions", default="generated/propositions")
    ap.add_argument("--compression", default="generated/compression")
    ap.add_argument("--revelation", default="generated/revelation")
    ap.add_argument("--out", default="generated/principles")
    args = ap.parse_args()
    print(f"Monad Phase 8 — Foundational Principle Discovery Engine ({METHOD})")
    eng = PrincipleEngine(args.concepts, args.propositions, args.compression,
                          args.revelation, args.out)
    summary = eng.run()
    print("  done.")
    print(f"  summary: {json.dumps(summary)}")


if __name__ == "__main__":
    main()
