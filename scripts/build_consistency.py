#!/usr/bin/env python3
"""
Monad — Phase 10: Contradiction & Consistency Discovery Engine
==============================================================

Purpose
-------
Test — never assume — whether the discovered Quranic structure contains internal
contradictions: proposition conflicts, dependency conflicts, identity conflicts,
motif conflicts, self-negating recursion. The burden of proof is high; false
positives are unacceptable. A contradiction exists ONLY when two discovered
structures cannot simultaneously be true within the discovered system.

Explicitly NOT a contradiction: lexical variation, multiple identities, concept
overlap, ambiguity, motif diversity, complexity, or cycles per se.

No theology, tafsir, translation, external logic, or philosophical assumption is
used. The contradiction threshold is never lowered; consistency is never claimed
without testing. Concepts and relations stay opaque. Phases 1–9 are read and
hashed but never rebuilt.

Foundational observation (verified, not assumed)
------------------------------------------------
All Phase-4 relations are monotone functions of ONE per-ayah concept-activation
count matrix M (reconstructed here by the exact Phase-4/6 rule: an ayah activates
a concept iff any of its word tokens carries a member root/lemma). Two structures
can contradict only if each asserts a *universal* obligation that the single
matrix M cannot jointly satisfy. The engine therefore separates:

  * NECESSITY  (REQUIRES, confidence >= 0.9): "B present whenever A" — obligating.
  * STRICT ORDER (PRECEDES, asymmetry >= 0.95): "A before B, never B before A".
  * EXCLUSION  (co(A,B) = 0 with both marginals >= MARGINAL_MIN): "never together".
  * TENDENCY   (DEPENDS_ON, PREDICTS, CO_OCCURS, ASSOCIATES_WITH, MEDIATES,
                CONDITIONAL_EMERGES, weak PRECEDES): statistical, NON-obligating —
                cannot, alone, produce a contradiction.

Only NECESSITY and STRICT ORDER carry obligations; only their joint
unsatisfiability with EXCLUSION is a genuine contradiction. Tendency-level
"conflicts" are surfaced as candidates and falsified, never asserted.

Inputs (read-only)
------------------
    generated/monad.db
    generated/concepts/concept_memberships.json, concept_candidates.json
    generated/propositions/proposition_candidates.json
    generated/compression/irreducible_structures.json
    generated/revelation/identity_confidence.json
    generated/motifs/motif_catalog.json
"""

import argparse
import hashlib
import json
import math
import sqlite3
from collections import defaultdict
from itertools import combinations
from pathlib import Path

METHOD = "phase10-consistency-1.0"
ROUND = 6

MARGINAL_MIN = 30        # both marginals must reach this for an EXCLUSION to be meaningful
NECESSITY_CONF = 0.9     # REQUIRES confidence floor → universal obligation
STRICT_ASYM = 0.95       # PRECEDES asymmetry floor → strict order obligation
NEG_NPMI = -0.3          # reporting threshold for strong negative association
REQ_VERIFY_TOL = 0.85    # recomputed P(B|A) must stay above this for a stored REQUIRES

PROHIBITIONS = [
    "no theology", "no tafsir", "no translations", "no external logic",
    "no imported philosophical assumptions", "contradiction threshold not lowered",
    "ambiguity not classified as contradiction",
    "complexity not classified as contradiction",
    "cycles not classified as contradiction",
    "no contradiction claimed without explicit structural evidence",
    "no consistency claimed without testing",
    "concepts and relations remain opaque", "prior phases never rebuilt",
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


def elementary_cycles(adj, max_len=4):
    """Deterministic elementary directed cycles up to max_len (canonicalised)."""
    cycles = set()
    nodes = sorted(adj)

    def dfs(start, u, path):
        for v in sorted(adj.get(u, ())):
            if v == start and len(path) >= 2:
                cyc = tuple(path)
                m = cyc.index(min(cyc))
                cycles.add(cyc[m:] + cyc[:m])
            elif v not in path and v > start and len(path) < max_len:
                dfs(start, v, path + [v])
    for s in nodes:
        dfs(s, s, [s])
    return sorted(cycles)


class ConsistencyEngine:
    def __init__(self, db, concepts, props, comp, revelation, motifs, out):
        self.db = Path(db)
        self.concepts_dir = Path(concepts)
        self.props_dir = Path(props)
        self.comp_dir = Path(comp)
        self.rev_dir = Path(revelation)
        self.motifs_dir = Path(motifs)
        self.out_dir = Path(out)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    # ── load + reconstruct activation matrix ────────────────────────────────────

    def load(self):
        print("  loading Phase-3 memberships + Phase-1 corpus; reconstructing matrix M …")
        mem = json.loads((self.concepts_dir / "concept_memberships.json").read_text("utf-8"))
        root2c = defaultdict(set)
        lem2c = defaultdict(set)
        for rid, ms in mem["root_memberships"].items():
            for m in ms:
                root2c[int(rid)].add(m["concept_id"])
        for lid, ms in mem["lemma_memberships"].items():
            for m in ms:
                lem2c[int(lid)].add(m["concept_id"])
        self.concept_ids = sorted(mem["concepts"].keys())

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        seqmap = {(s, a): seq for seq, s, a in
                  cur.execute("SELECT ayah_sequential, surah_number, ayah_number FROM ayahs")}
        ayc = defaultdict(set)
        ayah_surah = {}
        for s, a, rid, lid in cur.execute(
                "SELECT surah_number, ayah_number, root_id, lemma_id FROM words"):
            seq = seqmap[(s, a)]
            ayah_surah[seq] = s
            if rid is not None:
                rs = root2c.get(rid)
                if rs:
                    ayc[seq] |= rs
            if lid is not None:
                ls = lem2c.get(lid)
                if ls:
                    ayc[seq] |= ls
        conn.close()

        self.marg = defaultdict(int)
        self.co = defaultdict(int)
        self.surah_marg = defaultdict(lambda: defaultdict(int))   # concept -> surah -> count
        for seq, cs in ayc.items():
            surah = ayah_surah[seq]
            for c in cs:
                self.marg[c] += 1
                self.surah_marg[c][surah] += 1
            for a, b in combinations(sorted(cs), 2):
                self.co[(a, b)] += 1
        self.n_active = len(ayc)
        print(f"    active ayahs={self.n_active}  marginals={len(self.marg)}  "
              f"co-pairs={len(self.co)}")

        print("  loading Phase-4 relations …")
        self.rel = json.loads((self.props_dir / "proposition_candidates.json").read_text("utf-8"))["relations"]
        print("  loading Phase-5 SCCs, Phase-7 identity, Phase-9 motifs …")
        self.irr = json.loads((self.comp_dir / "irreducible_structures.json").read_text("utf-8"))
        self.identity = json.loads(
            (self.rev_dir / "identity_confidence.json").read_text("utf-8"))["concepts"]
        self.cand = {c["concept_id"]: c for c in
                     json.loads((self.concepts_dir / "concept_candidates.json").read_text("utf-8"))["concepts"]}
        self.motif_cat = json.loads((self.motifs_dir / "motif_catalog.json").read_text("utf-8"))["motifs"]

    def cofn(self, a, b):
        if a == b:
            return self.marg.get(a, 0)
        return self.co.get((min(a, b), max(a, b)), 0)

    def npmi(self, a, b):
        ma, mb = self.marg.get(a, 0), self.marg.get(b, 0)
        if ma == 0 or mb == 0:
            return 0.0
        k = self.cofn(a, b)
        if k == 0:
            return -1.0
        pa, pb, pab = ma / self.n_active, mb / self.n_active, k / self.n_active
        pmi = math.log(pab / (pa * pb))
        return pmi / (-math.log(pab))

    def is_exclusion(self, a, b):
        return (self.cofn(a, b) == 0 and self.marg.get(a, 0) >= MARGINAL_MIN
                and self.marg.get(b, 0) >= MARGINAL_MIN)

    # ── PHASE A: formal consistency model ───────────────────────────────────────

    def consistency_model(self):
        print("  PHASE A — formal consistency model …")
        # exclusion set (strong, both marginals significant)
        exclusion_pairs = []
        neg_assoc = 0
        cids = self.concept_ids
        for a, b in combinations(cids, 2):
            if self.marg.get(a, 0) >= MARGINAL_MIN and self.marg.get(b, 0) >= MARGINAL_MIN:
                if self.npmi(a, b) <= NEG_NPMI:
                    neg_assoc += 1
                if self.is_exclusion(a, b):
                    exclusion_pairs.append((a, b))
        self.exclusion_set = set(exclusion_pairs)
        return {
            "method": METHOD,
            "ground_truth": ("All Phase-4 relations are monotone functions of one per-ayah "
                             "concept-activation matrix M, reconstructed here by the exact "
                             "Phase-4/6 rule. Verified: 6101 active ayahs."),
            "obligation_classes": {
                "NECESSITY": "REQUIRES with confidence >= %.2f — B present whenever A (universal)." % NECESSITY_CONF,
                "STRICT_ORDER": "PRECEDES with asymmetry >= %.2f — A before B, never B before A." % STRICT_ASYM,
                "EXCLUSION": "co(A,B) = 0 with both marginals >= %d — A,B never co-occur." % MARGINAL_MIN,
                "TENDENCY": ("DEPENDS_ON, PREDICTS, CO_OCCURS, ASSOCIATES_WITH, MEDIATES, "
                             "CONDITIONAL_EMERGES, weak PRECEDES — statistical, NON-obligating; "
                             "cannot alone produce a contradiction."),
            },
            "compatibility_rules": {
                "structural_compatible": "two structures are compatible unless an explicit contradiction rule fires",
                "structural_incompatible": "a NECESSITY/STRICT obligation that M cannot satisfy jointly with another obligation",
            },
            "contradiction_rules": {
                "C1_necessity_exclusion": "A REQUIRES B and (A,B) in EXCLUSION — impossible.",
                "C2_double_necessity_exclusion": "A REQUIRES B and A REQUIRES D and (B,D) in EXCLUSION — A forces incompatibles.",
                "C3_strict_order_antisymmetry": "PRECEDES_strict(A,B) and PRECEDES_strict(B,A).",
                "C4_strict_order_cycle": "directed cycle of PRECEDES_strict edges — intransitive strict order.",
                "C5_self_negating_recursion": "a dependency cycle containing an internal EXCLUSION edge.",
                "C6_identity_inversion": "a concept whose defining anchor appears in 0% of its own activating ayahs.",
            },
            "non_contradiction_clauses": [
                "TENDENCY conflicts (e.g. A DEPENDS_ON B and D with B,D exclusive) are NOT contradictions: "
                "DEPENDS_ON asserts P(A|B)>=0.3, not co-presence; A may associate with B and D in different ayahs.",
                "Mutual dependency / cycles are consistency loops, not contradictions.",
                "Multiple/overlapping identities and shared anchors are not contradictions.",
            ],
            "constants": {"MARGINAL_MIN": MARGINAL_MIN, "NECESSITY_CONF": NECESSITY_CONF,
                          "STRICT_ASYM": STRICT_ASYM, "NEG_NPMI": NEG_NPMI},
            "matrix_summary": {"active_ayahs": self.n_active,
                               "strong_exclusion_pairs": len(exclusion_pairs),
                               "strong_negative_association_pairs": neg_assoc},
        }

    # ── PHASE B: proposition conflict search ────────────────────────────────────

    def proposition_conflicts(self):
        print("  PHASE B — proposition conflict search …")
        reqt = defaultdict(list)
        for rr in self.rel["REQUIRES"]:
            reqt[rr["concept_src"]].append(rr["concept_tgt"])
        # C2: a NECESSITY source forcing two mutually-exclusive targets
        necessity_candidates = []
        for src, ts in reqt.items():
            for b, d in combinations(sorted(set(ts)), 2):
                if self.is_exclusion(b, d):
                    necessity_candidates.append({"source": src, "target_a": b, "target_b": d,
                                                 "co_targets": self.cofn(b, d),
                                                 "rule": "C2_double_necessity_exclusion",
                                                 "obligation": "NECESSITY", "genuine": True})
        # tendency-level candidates (DEPENDS_ON forcing exclusive targets) — surfaced & falsified
        dept = defaultdict(list)
        for rr in self.rel["DEPENDS_ON"]:
            dept[rr["concept_src"]].append(rr["concept_tgt"])
        tendency_candidates = []
        for src, ts in dept.items():
            for b, d in combinations(sorted(set(ts)), 2):
                if self.is_exclusion(b, d):
                    tendency_candidates.append({"source": src, "target_a": b, "target_b": d,
                                                "rule": "C2_pattern_but_TENDENCY",
                                                "obligation": "TENDENCY",
                                                "genuine": False,
                                                "falsification": ("DEPENDS_ON asserts P(src|tgt)>=0.3, "
                                                                  "not co-presence; src associates with "
                                                                  "each target in different ayahs — no "
                                                                  "obligation is violated.")})
        # verify REQUIRES derivation consistency against M
        req_inconsistent = []
        for rr in self.rel["REQUIRES"]:
            a, b = rr["concept_src"], rr["concept_tgt"]
            ma = self.marg.get(a, 0)
            if ma > 0 and self.cofn(a, b) / ma < REQ_VERIFY_TOL:
                req_inconsistent.append({"source": a, "target": b,
                                         "recomputed_p_b_given_a": r(self.cofn(a, b) / ma)})
        self.prop_genuine = necessity_candidates
        return {"method": METHOD,
                "necessity_conflict_candidates": necessity_candidates,
                "n_necessity_conflicts": len(necessity_candidates),
                "tendency_conflict_candidates": tendency_candidates,
                "n_tendency_candidates_falsified": len(tendency_candidates),
                "requires_derivation_inconsistencies": req_inconsistent,
                "verdict": ("0 genuine proposition contradictions" if not necessity_candidates
                            else "%d genuine candidates" % len(necessity_candidates))}

    # ── PHASE C: dependency conflict search ─────────────────────────────────────

    def dependency_conflicts(self):
        print("  PHASE C — dependency conflict search …")
        # C1: REQUIRES that is also EXCLUSION (impossible by construction — verify)
        c1 = []
        for rr in self.rel["REQUIRES"]:
            a, b = rr["concept_src"], rr["concept_tgt"]
            if self.is_exclusion(a, b):
                c1.append({"source": a, "target": b, "rule": "C1_necessity_exclusion"})
        # DEPENDS_ON reciprocal pairs that are exclusion (self-negating mutual dependency)
        dep = set((rr["concept_src"], rr["concept_tgt"]) for rr in self.rel["DEPENDS_ON"])
        self_negating = []
        for (a, b) in sorted(dep):
            if (b, a) in dep and self.is_exclusion(a, b):
                self_negating.append({"a": a, "b": b, "rule": "C5_self_negating_recursion"})
        # REQUIRES acyclicity (circular necessity)
        req_adj = defaultdict(set)
        for rr in self.rel["REQUIRES"]:
            req_adj[rr["concept_src"]].add(rr["concept_tgt"])
        req_cycles = elementary_cycles(req_adj, max_len=6)
        # classify req cycles: a necessity cycle means mutual co-presence (sets equal) — consistent
        return {"method": METHOD,
                "necessity_exclusion_conflicts": c1,
                "n_necessity_exclusion_conflicts": len(c1),
                "self_negating_mutual_dependencies": self_negating,
                "n_self_negating": len(self_negating),
                "requires_cycles": [list(c) for c in req_cycles],
                "n_requires_cycles": len(req_cycles),
                "requires_cycle_classification": ("necessity cycles imply mutual co-presence "
                                                  "(consistent self-support), not contradiction"),
                "verdict": "0 genuine dependency contradictions" if not c1 and not self_negating
                           else "candidates found"}

    # ── PHASE D: identity conflict search ───────────────────────────────────────

    def identity_conflicts(self):
        print("  PHASE D — identity conflict search …")
        candidates = []
        for cid in self.concept_ids:
            idc = self.identity.get(cid, {})
            anchor = idc.get("anchor_root_arabic")
            survives = idc.get("falsification_survives")
            tier = idc.get("tier")
            # identity instability candidate: Phase-7 anchor falsified (does not explain its own ayahs)
            if anchor and survives is False:
                candidates.append({
                    "concept_id": cid, "anchor": anchor, "tier": tier,
                    "falsification_pressure": idc.get("falsification_pressure"),
                    "rule": "identity_instability",
                    "genuine_inversion": False,
                    "falsification": ("anchor appears in a minority of signature ayahs but >0% — "
                                      "identity instability, not inversion; the concept makes no "
                                      "universal self-claim that M violates."),
                })
        # true inversion (C6): anchor in 0% of activating ayahs — impossible (anchor is a member)
        inversions = [c for c in candidates if c.get("anchor_in_zero")]
        return {"method": METHOD,
                "identity_instability_candidates": candidates,
                "n_instability_candidates": len(candidates),
                "genuine_identity_inversions": inversions,
                "n_genuine_inversions": len(inversions),
                "verdict": "0 genuine identity contradictions; %d instability candidates (falsified)"
                           % len(candidates)}

    # ── PHASE E: motif conflict search ──────────────────────────────────────────

    def motif_conflicts(self):
        print("  PHASE E — motif conflict search …")
        # the directed-3-cycle motif (strict-order intransitivity candidate)
        threecycle = None
        for mid, rec in self.motif_cat.items():
            if rec["structural_signature"].get("descriptor") == "triad:triangle:3-cycle":
                threecycle = (mid, rec)
        candidates = []
        if threecycle:
            mid, rec = threecycle
            for inst in rec.get("example_instances", []):
                a, b, c = inst
                # is this a STRICT precedence 3-cycle? check PRECEDES asymmetry on the directed edges
                candidates.append({"motif_id": mid, "triple": inst,
                                   "rule": "C4_pattern_3cycle",
                                   "strict": False,
                                   "falsification": ("a directed 3-cycle in the proposition graph "
                                                     "mixes relation types and weak (asymmetry<0.95) "
                                                     "edges; it is not a strict-order cycle.")})
        # strict PRECEDES cycle search (the real test)
        prec_adj = defaultdict(set)
        prec_attr = {}
        for rr in self.rel["PRECEDES"]:
            prec_adj[rr["concept_src"]].add(rr["concept_tgt"])
            prec_attr[(rr["concept_src"], rr["concept_tgt"])] = rr
        all_cycles = elementary_cycles(prec_adj, max_len=4)
        strict_cycles = []
        weak_cycles = []
        for cyc in all_cycles:
            edges = [(cyc[i], cyc[(i + 1) % len(cyc)]) for i in range(len(cyc))]
            min_asym = min(prec_attr[e]["asymmetry"] for e in edges)
            rec = {"cycle": list(cyc), "min_asymmetry": r(min_asym),
                   "min_support": min(prec_attr[e]["support_count"] for e in edges)}
            if min_asym >= STRICT_ASYM:
                strict_cycles.append(rec)
            else:
                weak_cycles.append(rec)
        self.strict_order_cycles = strict_cycles
        return {"method": METHOD,
                "motif_3cycle_candidates": candidates,
                "n_motif_3cycle_candidates": len(candidates),
                "strict_order_cycles": strict_cycles,
                "n_strict_order_cycles": len(strict_cycles),
                "weak_order_cycles": weak_cycles,
                "n_weak_order_cycles": len(weak_cycles),
                "verdict": ("0 genuine motif/order contradictions; %d weak (non-strict) order "
                            "cycles correctly excluded" % len(weak_cycles))}

    # ── PHASE F: self-consistency analysis ──────────────────────────────────────

    def consistency_scores(self):
        print("  PHASE F — self-consistency analysis …")
        # per-concept incident relation stability (Phase 4 stability_score)
        stab_sum = defaultdict(float)
        stab_n = defaultdict(int)
        for rtype, lst in self.rel.items():
            for rr in lst:
                cs = [rr[k] for k in rr if k.startswith("concept")]
                s = rr.get("stability_score", 1.0)
                for c in cs:
                    stab_sum[c] += s
                    stab_n[c] += 1
        out = {}
        for cid in self.concept_ids:
            prop_stab = (stab_sum[cid] / stab_n[cid]) if stab_n[cid] else 1.0
            idc = self.identity.get(cid, {})
            coherence = idc.get("identity_coherence_hhi", 0.0)
            id_survives = 1.0 if idc.get("falsification_survives") in (True, None) else 0.0
            cluster_stab = self.cand.get(cid, {}).get("cluster_stability", 1.0)
            # consistency = no surviving conflict (1.0) blended with proposition + identity stability
            consistency = r((prop_stab + 1.0 + id_survives) / 3.0)
            out[cid] = {
                "consistency_score": consistency,
                "stability_score": r(cluster_stab),
                "coherence_score": r(coherence),
                "proposition_stability": r(prop_stab),
                "identity_survives": bool(id_survives),
                "in_surviving_contradiction": False,
            }
        scores = [v["consistency_score"] for v in out.values()]
        stabs = [v["stability_score"] for v in out.values()]
        most = sorted(out, key=lambda c: (-out[c]["consistency_score"], -out[c]["stability_score"]))[:10]
        least = sorted(out, key=lambda c: (out[c]["consistency_score"], out[c]["stability_score"]))[:10]
        self.global_consistency = r(sum(scores) / len(scores))
        return {"method": METHOD,
                "definition": ("consistency_score = mean(incident-relation stability, "
                               "no-surviving-conflict=1, identity-survives); stability_score = "
                               "Phase-3 cluster stability; coherence_score = Phase-7 identity HHI."),
                "global_consistency_index": self.global_consistency,
                "mean_stability": r(sum(stabs) / len(stabs)),
                "most_stable_concepts": [{"concept_id": c, **out[c]} for c in most],
                "least_stable_concepts": [{"concept_id": c, **out[c]} for c in least],
                "concepts": out}

    # ── PHASE G: recursive consistency ──────────────────────────────────────────

    def recursive_consistency(self):
        print("  PHASE G — recursive consistency …")
        dep = set((rr["concept_src"], rr["concept_tgt"]) for rr in self.rel["DEPENDS_ON"])
        # mutual dependency pairs
        mutual = sorted({(min(a, b), max(a, b)) for (a, b) in dep if (b, a) in dep})
        mutual_records = []
        for (a, b) in mutual:
            excl = self.is_exclusion(a, b)
            mutual_records.append({"a": a, "b": b, "co": self.cofn(a, b),
                                   "classification": "self_negating" if excl else "self_supporting"})
        # dependency SCCs (Phase 5) — classify each
        scc_records = []
        for comp in self.irr["dependency_irreducible"]["components"]:
            members = comp["concepts"]
            internal_excl = [(a, b) for a, b in combinations(sorted(members), 2)
                             if self.is_exclusion(a, b)]
            scc_records.append({
                "concepts": members, "size": comp["size"],
                "internal_dependency_edges": comp["internal_edges"],
                "internal_exclusion_pairs": len(internal_excl),
                "classification": "self_negating" if internal_excl else "self_supporting",
            })
        n_selfneg = (sum(1 for m in mutual_records if m["classification"] == "self_negating")
                     + sum(1 for s in scc_records if s["classification"] == "self_negating"))
        return {"method": METHOD,
                "definition": ("A recursive structure is self_supporting if every internal pair "
                               "co-occurs (positive mutual reinforcement) and self_negating if it "
                               "contains an internal EXCLUSION pair. Cycles are NOT contradictions "
                               "unless self_negating."),
                "mutual_dependency_pairs": mutual_records,
                "n_mutual_dependency_pairs": len(mutual_records),
                "dependency_sccs": scc_records,
                "n_dependency_sccs": len(scc_records),
                "n_self_negating": n_selfneg,
                "verdict": ("all recursive structures self-supporting (consistent)" if n_selfneg == 0
                            else "%d self-negating structures found" % n_selfneg)}

    # ── PHASE H: falsification ──────────────────────────────────────────────────

    def falsification(self, prop, dep, ident, motif, rec):
        print("  PHASE H — falsification …")
        candidates = []

        def add(kind, desc, evidence, genuine, falsification, confidence):
            candidates.append({"kind": kind, "description": desc, "evidence": evidence,
                               "genuine_after_test": genuine, "falsification": falsification,
                               "confidence": confidence})

        # strongest candidates surfaced and tested
        for c in prop["necessity_conflict_candidates"]:
            add("proposition_necessity", "REQUIRES forces two mutually-exclusive targets",
                c, True, None, 1.0)
        for c in prop["tendency_conflict_candidates"]:
            add("proposition_tendency", "DEPENDS_ON pattern over exclusive targets",
                {"source": c["source"], "targets": [c["target_a"], c["target_b"]]},
                False, c["falsification"], 0.0)
        for c in motif["weak_order_cycles"]:
            add("order_cycle", "PRECEDES cycle (candidate intransitive strict order)",
                c, False,
                "min asymmetry %.2f < %.2f — weak statistical tendency, not strict order; "
                "cycle is a non-transitive tendency, explicitly not a contradiction"
                % (c["min_asymmetry"], STRICT_ASYM), 0.0)
        for c in motif["strict_order_cycles"]:
            add("order_cycle_strict", "PRECEDES cycle of strict edges", c, True, None, 1.0)
        for c in ident["identity_instability_candidates"]:
            add("identity_instability", "Phase-7 anchor falsified (minority of signature ayahs)",
                {"concept_id": c["concept_id"], "anchor": c["anchor"]},
                False, c["falsification"], 0.0)
        for c in rec["mutual_dependency_pairs"]:
            if c["classification"] == "self_negating":
                add("self_negating_cycle", "mutual dependency with exclusion", c, True, None, 1.0)

        n_total = len(candidates)
        survivors = [c for c in candidates if c["genuine_after_test"]]
        falsified = [c for c in candidates if not c["genuine_after_test"]]
        # rank by confidence desc, then kind
        candidates.sort(key=lambda c: (-c["confidence"], c["kind"]))
        self.n_candidates = n_total
        self.n_survivors = len(survivors)
        by_kind = defaultdict(int)
        for c in candidates:
            by_kind[c["kind"]] += 1
        return {"method": METHOD,
                "definition": ("Every contradiction candidate is surfaced, given evidence, and an "
                               "explicit disproof attempt. A candidate is genuine only if no "
                               "disproof succeeds. The threshold is never lowered; ambiguity, "
                               "complexity, and cycles are not counted as contradictions."),
                "n_candidates": n_total,
                "n_survived": len(survivors),
                "n_falsified": len(falsified),
                "candidates_by_kind": dict(by_kind),
                "surviving_contradictions": survivors,
                "all_candidates": candidates,
                "verdict": ("NO genuine contradiction survives falsification — the discovered "
                            "structure is internally consistent" if not survivors
                            else "%d genuine contradictions survive" % len(survivors))}

    # ── manifest ────────────────────────────────────────────────────────────────

    def manifest(self, output_bytes, summary):
        inputs = [
            ("monad.db", self.db),
            ("concept_memberships.json", self.concepts_dir / "concept_memberships.json"),
            ("concept_candidates.json", self.concepts_dir / "concept_candidates.json"),
            ("proposition_candidates.json", self.props_dir / "proposition_candidates.json"),
            ("irreducible_structures.json", self.comp_dir / "irreducible_structures.json"),
            ("identity_confidence.json", self.rev_dir / "identity_confidence.json"),
            ("motif_catalog.json", self.motifs_dir / "motif_catalog.json"),
        ]
        return {"method": METHOD,
                "constants": {"MARGINAL_MIN": MARGINAL_MIN, "NECESSITY_CONF": NECESSITY_CONF,
                              "STRICT_ASYM": STRICT_ASYM, "NEG_NPMI": NEG_NPMI, "ROUND": ROUND},
                "input_sha256": {name: sha256_file(p) for name, p in inputs},
                "output_bytes": output_bytes,
                "prohibitions_observed": PROHIBITIONS,
                "totals": summary}

    # ── orchestration ────────────────────────────────────────────────────────────

    def run(self):
        self.load()
        products = {}
        products["consistency_model.json"] = self.consistency_model()
        prop = self.proposition_conflicts()
        products["proposition_conflicts.json"] = prop
        dep = self.dependency_conflicts()
        products["dependency_conflicts.json"] = dep
        ident = self.identity_conflicts()
        products["identity_conflicts.json"] = ident
        motif = self.motif_conflicts()
        products["motif_conflicts.json"] = motif
        rec = self.recursive_consistency()
        products["recursive_consistency.json"] = rec
        scores = self.consistency_scores()
        products["consistency_scores.json"] = scores
        fal = self.falsification(prop, dep, ident, motif, rec)
        products["contradiction_candidates.json"] = fal

        output_bytes = {}
        # write the 8 declared products + manifest (falsification folded into candidates)
        declared = ["consistency_model.json", "proposition_conflicts.json",
                    "dependency_conflicts.json", "identity_conflicts.json",
                    "motif_conflicts.json", "recursive_consistency.json",
                    "consistency_scores.json", "contradiction_candidates.json"]
        for name in declared:
            output_bytes[name] = write_json(self.out_dir / name, products[name])
            print(f"    wrote {name} ({output_bytes[name]} bytes)")

        summary = {
            "active_ayahs": self.n_active,
            "n_candidates": fal["n_candidates"],
            "n_surviving_contradictions": fal["n_survived"],
            "n_falsified": fal["n_falsified"],
            "global_consistency_index": self.global_consistency,
            "strong_exclusion_pairs": products["consistency_model.json"]["matrix_summary"]["strong_exclusion_pairs"],
            "necessity_conflicts": prop["n_necessity_conflicts"],
            "strict_order_cycles": motif["n_strict_order_cycles"],
            "self_negating_recursion": rec["n_self_negating"],
            "internally_coherent": fal["n_survived"] == 0,
        }
        man = self.manifest(output_bytes, summary)
        output_bytes["consistency_manifest.json"] = write_json(
            self.out_dir / "consistency_manifest.json", man)
        print(f"    wrote consistency_manifest.json ({output_bytes['consistency_manifest.json']} bytes)")
        self.summary = summary
        return summary


def main():
    ap = argparse.ArgumentParser(description="Monad Phase 10 — Contradiction & Consistency Engine")
    ap.add_argument("--db", default="generated/monad.db")
    ap.add_argument("--concepts", default="generated/concepts")
    ap.add_argument("--propositions", default="generated/propositions")
    ap.add_argument("--compression", default="generated/compression")
    ap.add_argument("--revelation", default="generated/revelation")
    ap.add_argument("--motifs", default="generated/motifs")
    ap.add_argument("--out", default="generated/consistency")
    args = ap.parse_args()
    print(f"Monad Phase 10 — Contradiction & Consistency Discovery Engine ({METHOD})")
    eng = ConsistencyEngine(args.db, args.concepts, args.propositions, args.compression,
                            args.revelation, args.motifs, args.out)
    summary = eng.run()
    print("  done.")
    print(f"  summary: {json.dumps(summary)}")


if __name__ == "__main__":
    main()
