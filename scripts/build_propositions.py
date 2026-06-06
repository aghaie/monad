#!/usr/bin/env python3
"""
scripts/build_propositions.py

Monad Proposition Discovery Engine — Builder (Phase 4).

Discovers recurring proposition-like STRUCTURES between Phase-3 concept
candidates. A proposition here is NOT a word, root, lemma, or concept; it is an
emergent *relation* — a statistical regularity in how Phase-3 concepts co-occur,
order, depend on each other, mediate each other, or jointly enable a third — as
observed inside the Quran. Concept ids stay opaque; no human-readable meaning,
translation, theology, label, or interpretation is assigned at any layer.

The Quran is the only semantic universe. No external dictionary, tafsir,
translation, theology, or pre-trained embedding is consulted. Phase 1/2/3
outputs are read but NOT rebuilt.

Usage:
    python3 scripts/build_propositions.py [--db PATH] [--lex DIR] [--concepts DIR] [--out DIR]

Inputs (read-only):
    generated/monad.db
    generated/lexicon/{root_profiles,lemma_profiles,distribution_profiles,
                      semantic_neighbors}.json
    generated/concepts/{concept_memberships,concept_candidates,concept_graph,
                       concept_manifest}.json

Outputs (generated/propositions/):
    proposition_candidates.json   all candidate relations, grouped by type
    proposition_graph.json        directed multi-relation graph + per-node metrics
    dependency_candidates.json    DEPENDS_ON + REQUIRES subset
    implication_candidates.json   PREDICTS subset (sequence window 1..3)
    conditional_patterns.json     synergy triples (A and B together enable E)
    bridge_patterns.json          MEDIATES triples + BRIDGES (high-betweenness)
    proposition_manifest.json     reproducibility manifest

Method (all Quran-internal, deterministic):
    1. Concept-activation matrix per ayah from Phase-3 root- and lemma-level
       memberships (union over the words of the ayah). Earliest word position
       of any active member retained for intra-ayah ordering.
    2. Pairwise and (filtered) triple ayah-level joint counts.
    3. CO_OCCURS and ASSOCIATES_WITH from PMI / NPMI on pair counts.
    4. DEPENDS_ON / REQUIRES from directed conditional probability and lift.
    5. PRECEDES / FOLLOWS from intra-ayah word-position asymmetry.
    6. PREDICTS from sequence-window (w=1,2,3) conditional probability across
       consecutive ayahs within the same surah.
    7. MEDIATES from triadic mediation strength (P(M | A and D) plus isolation
       lift — fraction of A and D evidence carried by M-bearing ayahs).
    8. Conditional emergence triples — synergy(A,B,E) = P(E|A,B) - max(P(E|A),
       P(E|B)).
    9. Proposition graph (directed multigraph over 103 concept ids) +
       per-node topology metrics (degree, relation diversity, betweenness on
       undirected projection). BRIDGES = top-decile betweenness.
   10. Stability under support-threshold perturbation +/- 1.
   11. Classifications: highly_connected / stable / rare / global / localized /
       concept_hubs / dependency_hubs / bridge_propositions / potential
       hierarchical / causal / recursive structures (sets of opaque ids).

Determinism: no randomness; sorted iteration everywhere; floats rounded to
ROUND; JSON written with sort_keys=True. Re-runs are byte-identical
(verified by validate_propositions.py --rebuild).

STRICTLY structural / statistical. Builds no ontology, no axioms, no
contradiction engine, no theology, no interpretation, no doctrine, no origin
claims. Concept ids are opaque and remain opaque.
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
DEFAULT_CONCEPTS = REPO_ROOT / "generated" / "concepts"
DEFAULT_OUT = REPO_ROOT / "generated" / "propositions"

# ── Tunable constants (documented; deterministic) ─────────────────────────────

NPMI_MIN = 0.20
SUPPORT_MIN = 5
DEPENDS_LIFT_MIN = 2.0
DEPENDS_CONF_MIN = 0.30
REQUIRES_CONF_MIN = 0.90
ORDER_ASYM_MIN = 0.30
ORDER_SUPPORT_MIN = 10
PREDICT_WINDOWS = (1, 2, 3)
PREDICT_LIFT_MIN = 1.5
PREDICT_CONF_MIN = 0.20
PREDICT_SUPPORT_MIN = 5
MED_LIFT_MIN = 2.0           # not used directly; kept for traceability
MED_SUPPORT_MIN = 5
MED_CONF_MIN = 0.70          # P(M | A and D)
MED_ISO_MIN = 0.50           # isolation share carried by M
SYNERGY_MIN = 0.15
SYNERGY_SUPPORT_MIN = 5
TRIPLE_PREFILTER = 3
EVIDENCE_TOP = 5
PERTURB = (-1, +1)
ROUND = 6
TOP_BRIDGE_FRAC = 0.10
METHOD_VERSION = "phase4-propositions-1.0"


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


class PropositionBuilder:

    def __init__(self, db_path, lex_dir, concepts_dir, out_dir):
        self.db_path = Path(db_path)
        self.lex_dir = Path(lex_dir)
        self.concepts_dir = Path(concepts_dir)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    # ── Stage 1: load Phase-1/2/3 inputs ─────────────────────────────────────

    def load(self):
        print("  loading Phase-3 memberships and concept set …")
        memberships = json.loads(
            (self.concepts_dir / "concept_memberships.json").read_text("utf-8"))

        # root_id -> tuple(sorted concept ids)
        self.root_to_concepts = {}
        for rid, members in memberships["root_memberships"].items():
            cs = tuple(sorted(m["concept_id"] for m in members))
            if cs:
                self.root_to_concepts[int(rid)] = cs

        self.lemma_to_concepts = {}
        for lid, members in memberships["lemma_memberships"].items():
            cs = tuple(sorted(m["concept_id"] for m in members))
            if cs:
                self.lemma_to_concepts[int(lid)] = cs

        # canonical sorted concept id list
        self.concept_ids = sorted(memberships["concepts"].keys())
        self.concept_index = {cid: i for i, cid in enumerate(self.concept_ids)}
        self.n_concepts = len(self.concept_ids)
        print(f"    concepts          : {self.n_concepts}")
        print(f"    rooted entities   : {len(self.root_to_concepts)} roots")
        print(f"    lemma entities    : {len(self.lemma_to_concepts)} lemmas")

        # surah lookup for evidence formatting and global counts
        print("  loading Phase-1 ayah index …")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT ayah_sequential, surah_number, ayah_number "
                    "FROM ayahs ORDER BY ayah_sequential")
        self.ayah_meta = {}     # seq -> (surah, ayah)
        self.seq_by_surah = defaultdict(list)
        for seq, surah, ayah in cur.fetchall():
            self.ayah_meta[seq] = (surah, ayah)
            self.seq_by_surah[surah].append(seq)
        self.n_ayahs = len(self.ayah_meta)
        print(f"    ayahs             : {self.n_ayahs}")
        for surah in self.seq_by_surah:
            self.seq_by_surah[surah].sort()

        # per-ayah words: (root_id, lemma_id, word_position)
        cur.execute("SELECT surah_number, ayah_number, word_position, "
                    "root_id, lemma_id FROM words "
                    "ORDER BY surah_number, ayah_number, word_position")
        # build ayah_seq from (surah, ayah)
        seq_lookup = {v: k for k, v in self.ayah_meta.items()}
        # ayah_concepts: seq -> sorted tuple of concept ids
        # ayah_concept_pos: seq -> dict concept_id -> earliest pos
        ayah_pos = defaultdict(dict)
        for surah, ayah, pos, rid, lid in cur.fetchall():
            seq = seq_lookup[(surah, ayah)]
            cs = set()
            if rid is not None and rid in self.root_to_concepts:
                cs.update(self.root_to_concepts[rid])
            if lid is not None and lid in self.lemma_to_concepts:
                cs.update(self.lemma_to_concepts[lid])
            if not cs:
                continue
            dpos = ayah_pos[seq]
            for c in cs:
                if c not in dpos or pos < dpos[c]:
                    dpos[c] = pos
        conn.close()

        # finalize per-ayah structures (sorted by concept id)
        self.ayah_concepts = {}
        self.ayah_concept_pos = {}
        for seq, dpos in ayah_pos.items():
            ordered = sorted(dpos.keys())
            self.ayah_concepts[seq] = tuple(ordered)
            self.ayah_concept_pos[seq] = {c: dpos[c] for c in ordered}

        self.n_active_ayahs = len(self.ayah_concepts)
        print(f"    ayahs with concept activation : {self.n_active_ayahs}")

    # ── Stage 2: marginal + pair + (filtered) triple counts ──────────────────

    def count(self):
        print("  counting concept marginals, pairs, triples …")
        cnt1 = defaultdict(int)
        cnt2 = defaultdict(int)
        # joint evidence for evidence_paths (per pair only — triples skipped to bound size)
        evidence2 = defaultdict(list)
        # support per concept for which ayahs it appears in (used by triples + surah stats)
        ayahs_per_concept = defaultdict(list)

        for seq in sorted(self.ayah_concepts.keys()):
            cs = self.ayah_concepts[seq]
            for a in cs:
                cnt1[a] += 1
                ayahs_per_concept[a].append(seq)
            for a, b in combinations(cs, 2):
                cnt2[(a, b)] += 1
                # cap evidence list at EVIDENCE_TOP early to bound memory
                if len(evidence2[(a, b)]) < EVIDENCE_TOP:
                    evidence2[(a, b)].append(seq)

        self.cnt1 = dict(cnt1)
        self.cnt2 = dict(cnt2)
        self.evidence2 = {k: tuple(v) for k, v in evidence2.items()}
        self.ayahs_per_concept = {k: tuple(v) for k, v in ayahs_per_concept.items()}
        print(f"    marginals      : {len(self.cnt1)}")
        print(f"    pairs (>= 1)   : {len(self.cnt2)}")

        # Triples: only consider triples (a,b,c) where each pair occurs >= TRIPLE_PREFILTER
        print("  counting triples with pair pre-filter …")
        cnt3 = defaultdict(int)
        for seq in sorted(self.ayah_concepts.keys()):
            cs = self.ayah_concepts[seq]
            if len(cs) < 3:
                continue
            # filter to concepts whose pair counts are all big enough for relevance
            for a, b, c in combinations(cs, 3):
                # cheap pair-filter
                if self.cnt2.get((a, b), 0) < TRIPLE_PREFILTER:
                    continue
                if self.cnt2.get((a, c), 0) < TRIPLE_PREFILTER:
                    continue
                if self.cnt2.get((b, c), 0) < TRIPLE_PREFILTER:
                    continue
                cnt3[(a, b, c)] += 1
        self.cnt3 = {k: v for k, v in cnt3.items() if v >= TRIPLE_PREFILTER}
        print(f"    triples (>= {TRIPLE_PREFILTER}) : {len(self.cnt3)}")

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _p(self, a):
        return self.cnt1.get(a, 0) / self.n_active_ayahs

    def _pair_cnt(self, a, b):
        if a == b:
            return self.cnt1.get(a, 0)
        if a < b:
            return self.cnt2.get((a, b), 0)
        return self.cnt2.get((b, a), 0)

    def _triple_cnt(self, a, b, c):
        key = tuple(sorted((a, b, c)))
        return self.cnt3.get(key, 0)

    def _evidence(self, a, b):
        key = (a, b) if a < b else (b, a)
        seqs = self.evidence2.get(key, ())
        return [{"surah": self.ayah_meta[s][0],
                 "ayah": self.ayah_meta[s][1]} for s in seqs]

    def _surah_span(self, seqs):
        return sorted({self.ayah_meta[s][0] for s in seqs})

    def _stability(self, support, threshold):
        # support-threshold perturbation: edge survives at threshold+d iff support >= threshold+d
        kept_low = 1 if support >= threshold + PERTURB[0] else 0
        kept_high = 1 if support >= threshold + PERTURB[1] else 0
        return r((kept_low + kept_high) / 2.0)

    # ── Stage 3: ASSOCIATES_WITH / CO_OCCURS ─────────────────────────────────

    def assoc(self):
        print("  ASSOCIATES_WITH / CO_OCCURS …")
        self.associates = []
        self.cooccurs = []
        n = self.n_active_ayahs
        for (a, b), c_ab in self.cnt2.items():
            if c_ab < SUPPORT_MIN:
                continue
            ca = self.cnt1[a]
            cb = self.cnt1[b]
            p_ab = c_ab / n
            p_a = ca / n
            p_b = cb / n
            # PMI / NPMI
            denom = p_a * p_b
            if denom <= 0 or p_ab <= 0:
                continue
            pmi = math.log(p_ab / denom)
            npmi = pmi / -math.log(p_ab)
            evi = self._evidence(a, b)
            # CO_OCCURS — symmetric, threshold is just support
            self.cooccurs.append({
                "concept_a": a,
                "concept_b": b,
                "relation_type": "CO_OCCURS",
                "support_count": c_ab,
                "confidence": r(min(c_ab / ca, c_ab / cb)),
                "stability_score": self._stability(c_ab, SUPPORT_MIN),
                "evidence_paths": evi,
            })
            if npmi >= NPMI_MIN:
                self.associates.append({
                    "concept_a": a,
                    "concept_b": b,
                    "relation_type": "ASSOCIATES_WITH",
                    "npmi": r(npmi),
                    "pmi": r(pmi),
                    "support_count": c_ab,
                    "confidence": r(npmi),
                    "stability_score": self._stability(c_ab, SUPPORT_MIN),
                    "evidence_paths": evi,
                })
        self.associates.sort(key=lambda e: (-e["confidence"], -e["support_count"],
                                             e["concept_a"], e["concept_b"]))
        self.cooccurs.sort(key=lambda e: (-e["support_count"], -e["confidence"],
                                            e["concept_a"], e["concept_b"]))
        print(f"    ASSOCIATES_WITH: {len(self.associates)}")
        print(f"    CO_OCCURS      : {len(self.cooccurs)}")

    # ── Stage 4: DEPENDS_ON / REQUIRES ───────────────────────────────────────

    def dependency(self):
        print("  DEPENDS_ON / REQUIRES …")
        self.depends_on = []
        self.requires = []
        n = self.n_active_ayahs
        # use unordered pair counts, then test both directions
        for (a, b), c_ab in self.cnt2.items():
            if c_ab < SUPPORT_MIN:
                continue
            ca = self.cnt1[a]
            cb = self.cnt1[b]
            p_a = ca / n
            p_b = cb / n
            evi = self._evidence(a, b)
            # direction A->B: "A depends on B" means seeing B raises chance of A
            # P(A|B) = c_ab / cb; lift = P(A|B) / P(A)
            for src, tgt, c_src, c_tgt, p_src in [(a, b, ca, cb, p_a),
                                                   (b, a, cb, ca, p_b)]:
                p_src_given_tgt = c_ab / c_tgt
                lift_src_given_tgt = p_src_given_tgt / p_src
                p_tgt_given_src = c_ab / c_src
                # DEPENDS_ON: src depends on tgt
                if (p_src_given_tgt >= DEPENDS_CONF_MIN
                        and lift_src_given_tgt >= DEPENDS_LIFT_MIN):
                    self.depends_on.append({
                        "concept_src": src,
                        "concept_tgt": tgt,
                        "relation_type": "DEPENDS_ON",
                        "p_src_given_tgt": r(p_src_given_tgt),
                        "lift": r(lift_src_given_tgt),
                        "confidence": r(p_src_given_tgt),
                        "support_count": c_ab,
                        "stability_score": self._stability(c_ab, SUPPORT_MIN),
                        "evidence_paths": evi,
                    })
                # REQUIRES: src almost never appears without tgt -> P(tgt|src) very high
                if p_tgt_given_src >= REQUIRES_CONF_MIN:
                    self.requires.append({
                        "concept_src": src,
                        "concept_tgt": tgt,
                        "relation_type": "REQUIRES",
                        "p_tgt_given_src": r(p_tgt_given_src),
                        "confidence": r(p_tgt_given_src),
                        "support_count": c_ab,
                        "stability_score": self._stability(c_ab, SUPPORT_MIN),
                        "evidence_paths": evi,
                    })
        self.depends_on.sort(key=lambda e: (-e["lift"], -e["confidence"],
                                             -e["support_count"],
                                             e["concept_src"], e["concept_tgt"]))
        self.requires.sort(key=lambda e: (-e["confidence"], -e["support_count"],
                                           e["concept_src"], e["concept_tgt"]))
        print(f"    DEPENDS_ON     : {len(self.depends_on)}")
        print(f"    REQUIRES       : {len(self.requires)}")

    # ── Stage 5: PRECEDES / FOLLOWS ──────────────────────────────────────────

    def ordering(self):
        print("  PRECEDES / FOLLOWS …")
        precedes_cnt = defaultdict(int)   # (a, b) -> #ayahs pos_a < pos_b
        co_pair = defaultdict(int)        # (a, b) symmetric co-occurrence in pos sense

        for seq in sorted(self.ayah_concept_pos.keys()):
            dpos = self.ayah_concept_pos[seq]
            cs = sorted(dpos.keys())
            for a, b in combinations(cs, 2):
                pa = dpos[a]
                pb = dpos[b]
                if pa == pb:
                    continue
                co_pair[(a, b)] += 1
                if pa < pb:
                    precedes_cnt[(a, b)] += 1
                else:
                    precedes_cnt[(b, a)] += 1

        self.precedes = []
        self.follows = []
        for (a, b), c_ab in self.cnt2.items():
            total = co_pair.get((a, b), 0)
            if total < ORDER_SUPPORT_MIN:
                continue
            n_ab = precedes_cnt.get((a, b), 0)
            n_ba = precedes_cnt.get((b, a), 0)
            asym = (n_ab - n_ba) / total
            evi = self._evidence(a, b)
            if asym >= ORDER_ASYM_MIN:
                self.precedes.append({
                    "concept_src": a,
                    "concept_tgt": b,
                    "relation_type": "PRECEDES",
                    "support_count": total,
                    "precedes_count": n_ab,
                    "follows_count": n_ba,
                    "asymmetry": r(asym),
                    "confidence": r(asym),
                    "stability_score": self._stability(total, ORDER_SUPPORT_MIN),
                    "evidence_paths": evi,
                })
                self.follows.append({
                    "concept_src": b,
                    "concept_tgt": a,
                    "relation_type": "FOLLOWS",
                    "support_count": total,
                    "precedes_count": n_ab,
                    "follows_count": n_ba,
                    "asymmetry": r(asym),
                    "confidence": r(asym),
                    "stability_score": self._stability(total, ORDER_SUPPORT_MIN),
                    "evidence_paths": evi,
                })
            elif asym <= -ORDER_ASYM_MIN:
                self.precedes.append({
                    "concept_src": b,
                    "concept_tgt": a,
                    "relation_type": "PRECEDES",
                    "support_count": total,
                    "precedes_count": n_ba,
                    "follows_count": n_ab,
                    "asymmetry": r(-asym),
                    "confidence": r(-asym),
                    "stability_score": self._stability(total, ORDER_SUPPORT_MIN),
                    "evidence_paths": evi,
                })
                self.follows.append({
                    "concept_src": a,
                    "concept_tgt": b,
                    "relation_type": "FOLLOWS",
                    "support_count": total,
                    "precedes_count": n_ba,
                    "follows_count": n_ab,
                    "asymmetry": r(-asym),
                    "confidence": r(-asym),
                    "stability_score": self._stability(total, ORDER_SUPPORT_MIN),
                    "evidence_paths": evi,
                })
        self.precedes.sort(key=lambda e: (-e["confidence"], -e["support_count"],
                                           e["concept_src"], e["concept_tgt"]))
        self.follows.sort(key=lambda e: (-e["confidence"], -e["support_count"],
                                          e["concept_src"], e["concept_tgt"]))
        print(f"    PRECEDES       : {len(self.precedes)}")
        print(f"    FOLLOWS        : {len(self.follows)}")

    # ── Stage 6: PREDICTS (sequence window 1..3) ─────────────────────────────

    def predicts(self):
        print("  PREDICTS (sequence window) …")
        self.predicts_by_window = {}
        all_preds = []
        for w in PREDICT_WINDOWS:
            print(f"    window = {w} …")
            co = defaultdict(int)         # (a, b) -> #i where a@i and b@i+w in same surah
            first_cnt = defaultdict(int)  # a -> #i with a@i and i+w in same surah
            for surah in sorted(self.seq_by_surah.keys()):
                seqs = self.seq_by_surah[surah]
                for i in range(len(seqs) - w):
                    seq_i = seqs[i]
                    seq_j = seqs[i + w]
                    cs_i = self.ayah_concepts.get(seq_i, ())
                    cs_j = self.ayah_concepts.get(seq_j, ())
                    if not cs_i or not cs_j:
                        continue
                    for a in cs_i:
                        first_cnt[a] += 1
                    set_j = set(cs_j)
                    for a in cs_i:
                        for b in set_j:
                            if a == b:
                                continue
                            co[(a, b)] += 1
            edges = []
            n = self.n_active_ayahs
            for (a, b), c_ab in co.items():
                if c_ab < PREDICT_SUPPORT_MIN:
                    continue
                first_a = first_cnt[a]
                if first_a == 0:
                    continue
                p_b_given_a = c_ab / first_a
                p_b = self.cnt1.get(b, 0) / n
                if p_b <= 0:
                    continue
                lift = p_b_given_a / p_b
                if (p_b_given_a >= PREDICT_CONF_MIN
                        and lift >= PREDICT_LIFT_MIN):
                    edges.append({
                        "concept_src": a,
                        "concept_tgt": b,
                        "relation_type": "PREDICTS",
                        "window": w,
                        "support_count": c_ab,
                        "p_tgt_given_src": r(p_b_given_a),
                        "lift": r(lift),
                        "confidence": r(p_b_given_a),
                        "stability_score": self._stability(c_ab, PREDICT_SUPPORT_MIN),
                    })
            edges.sort(key=lambda e: (-e["lift"], -e["confidence"],
                                       -e["support_count"],
                                       e["concept_src"], e["concept_tgt"]))
            self.predicts_by_window[w] = edges
            all_preds.extend(edges)
            print(f"      edges: {len(edges)}")
        self.predicts = all_preds

    # ── Stage 7: MEDIATES (triadic) ──────────────────────────────────────────

    def mediates(self):
        print("  MEDIATES (triadic mediation) …")
        # need cnt[A and D] >= MED_SUPPORT_MIN
        # for each (a,d), enumerate all M with cnt(a,m,d) >= MED_SUPPORT_MIN
        # store P(M | A and D), isolation
        self.med_triples = []
        # index triples by unordered base pair: pair -> list of (m, cnt)
        pair_to_meds = defaultdict(list)
        for (a, b, c), cnt in self.cnt3.items():
            if cnt < MED_SUPPORT_MIN:
                continue
            # treat each of (a,b), (a,c), (b,c) as candidate base pair
            for base, mediator in (((a, b), c), ((a, c), b), ((b, c), a)):
                pair_to_meds[base].append((mediator, cnt))

        for (a, d), meds in pair_to_meds.items():
            c_ad = self.cnt2.get((a, d), 0)
            if c_ad < MED_SUPPORT_MIN:
                continue
            for m, c_amd in meds:
                p_m_given_ad = c_amd / c_ad
                if p_m_given_ad < MED_CONF_MIN:
                    continue
                iso = c_amd / c_ad
                if iso < MED_ISO_MIN:
                    continue
                self.med_triples.append({
                    "concept_mediator": m,
                    "concept_a": a,
                    "concept_d": d,
                    "relation_type": "MEDIATES",
                    "support_count_a_and_d": c_ad,
                    "support_count_with_mediator": c_amd,
                    "p_mediator_given_a_and_d": r(p_m_given_ad),
                    "isolation": r(iso),
                    "confidence": r(p_m_given_ad),
                    "stability_score": self._stability(c_amd, MED_SUPPORT_MIN),
                    "evidence_paths": self._evidence(a, d),
                })
        self.med_triples.sort(key=lambda e: (-e["confidence"],
                                              -e["support_count_with_mediator"],
                                              e["concept_mediator"],
                                              e["concept_a"], e["concept_d"]))
        print(f"    MEDIATES       : {len(self.med_triples)}")

    # ── Stage 8: conditional emergence (synergy A and B -> E) ────────────────

    def conditional(self):
        print("  CONDITIONAL_EMERGES (synergy) …")
        self.conditional = []
        for (a, b, c), c_abc in self.cnt3.items():
            if c_abc < SYNERGY_SUPPORT_MIN:
                continue
            # consider each of the three as "E" emerging from the other two
            triple = [a, b, c]
            for e in triple:
                pair_left = tuple(x for x in triple if x != e)
                pa, pb_ = pair_left
                c_pair = self._pair_cnt(pa, pb_)
                if c_pair < SYNERGY_SUPPORT_MIN:
                    continue
                p_e_given_ab = c_abc / c_pair
                p_e_given_a = self._pair_cnt(pa, e) / self.cnt1.get(pa, 1)
                p_e_given_b = self._pair_cnt(pb_, e) / self.cnt1.get(pb_, 1)
                synergy = p_e_given_ab - max(p_e_given_a, p_e_given_b)
                if synergy >= SYNERGY_MIN:
                    self.conditional.append({
                        "concept_a": pa,
                        "concept_b": pb_,
                        "concept_e": e,
                        "relation_type": "CONDITIONAL_EMERGES",
                        "support_count": c_abc,
                        "p_e_given_a_and_b": r(p_e_given_ab),
                        "p_e_given_a": r(p_e_given_a),
                        "p_e_given_b": r(p_e_given_b),
                        "synergy": r(synergy),
                        "confidence": r(p_e_given_ab),
                        "stability_score": self._stability(c_abc, SYNERGY_SUPPORT_MIN),
                    })
        self.conditional.sort(key=lambda e: (-e["synergy"], -e["support_count"],
                                              e["concept_a"], e["concept_b"],
                                              e["concept_e"]))
        print(f"    CONDITIONAL    : {len(self.conditional)}")

    # ── Stage 9: proposition graph + topology ────────────────────────────────

    def graph(self):
        print("  building proposition graph …")
        # Directed multigraph: edges keyed by (src, tgt, type)
        # nodes are all 103 Phase-3 concept ids (kept even if isolated)
        edge_list = []
        # directional edges
        for e in self.depends_on:
            edge_list.append({"src": e["concept_src"], "tgt": e["concept_tgt"],
                              "type": "DEPENDS_ON",
                              "weight": e["confidence"],
                              "support": e["support_count"],
                              "stability": e["stability_score"]})
        for e in self.requires:
            edge_list.append({"src": e["concept_src"], "tgt": e["concept_tgt"],
                              "type": "REQUIRES",
                              "weight": e["confidence"],
                              "support": e["support_count"],
                              "stability": e["stability_score"]})
        for e in self.precedes:
            edge_list.append({"src": e["concept_src"], "tgt": e["concept_tgt"],
                              "type": "PRECEDES",
                              "weight": e["confidence"],
                              "support": e["support_count"],
                              "stability": e["stability_score"]})
        for e in self.predicts:
            edge_list.append({"src": e["concept_src"], "tgt": e["concept_tgt"],
                              "type": f"PREDICTS_W{e['window']}",
                              "weight": e["confidence"],
                              "support": e["support_count"],
                              "stability": e["stability_score"]})
        # symmetric edges materialised both ways for topology metrics
        for e in self.associates:
            edge_list.append({"src": e["concept_a"], "tgt": e["concept_b"],
                              "type": "ASSOCIATES_WITH",
                              "weight": e["confidence"],
                              "support": e["support_count"],
                              "stability": e["stability_score"]})
            edge_list.append({"src": e["concept_b"], "tgt": e["concept_a"],
                              "type": "ASSOCIATES_WITH",
                              "weight": e["confidence"],
                              "support": e["support_count"],
                              "stability": e["stability_score"]})

        self.graph_edges = sorted(
            edge_list,
            key=lambda x: (x["src"], x["tgt"], x["type"], -x["weight"]))

        # per-node aggregates
        out_deg = defaultdict(int)
        in_deg = defaultdict(int)
        type_in = defaultdict(set)
        type_out = defaultdict(set)
        partners_out = defaultdict(lambda: defaultdict(float))
        partners_in = defaultdict(lambda: defaultdict(float))
        for e in self.graph_edges:
            out_deg[e["src"]] += 1
            in_deg[e["tgt"]] += 1
            type_out[e["src"]].add(e["type"])
            type_in[e["tgt"]].add(e["type"])
            partners_out[e["src"]][e["tgt"]] = max(
                partners_out[e["src"]][e["tgt"]], e["weight"])
            partners_in[e["tgt"]][e["src"]] = max(
                partners_in[e["tgt"]][e["src"]], e["weight"])

        # undirected projection — boolean adjacency for unweighted topology.
        # Using unweighted shortest paths keeps betweenness interpretable when
        # individual relation confidences span [0.2, 1.0] (a small set of
        # weight=1.0 REQUIRES / PRECEDES edges would otherwise collapse the
        # geometry onto a single hub).
        und = set()
        for e in self.graph_edges:
            key = tuple(sorted((e["src"], e["tgt"])))
            und.add(key)
        adj = defaultdict(set)
        for a, b in und:
            adj[a].add(b)
            adj[b].add(a)
        for c in self.concept_ids:
            adj.setdefault(c, set())

        # Brandes betweenness on the unweighted undirected projection.
        # Deterministic: BFS queue follows sorted-node insertion order.
        nodes = list(self.concept_ids)
        bet = {c: 0.0 for c in nodes}
        for s in nodes:
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
                for v in sorted(adj[u]):
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
        # undirected normalisation: each unordered pair counted twice
        for c in bet:
            bet[c] = bet[c] / 2.0

        # assemble per-node attributes
        self.node_attrs = {}
        for c in self.concept_ids:
            self.node_attrs[c] = {
                "out_degree": out_deg.get(c, 0),
                "in_degree": in_deg.get(c, 0),
                "relation_diversity": len(type_in[c] | type_out[c]),
                "betweenness_centrality": r(bet[c]),
                "top_out_partners": [
                    {"concept_id": t, "weight": r(w)}
                    for t, w in sorted(partners_out[c].items(),
                                       key=lambda kv: (-kv[1], kv[0]))[:10]],
                "top_in_partners": [
                    {"concept_id": t, "weight": r(w)}
                    for t, w in sorted(partners_in[c].items(),
                                       key=lambda kv: (-kv[1], kv[0]))[:10]],
            }

        # BRIDGES = top decile by betweenness (ties broken lex)
        ranked = sorted(self.concept_ids,
                        key=lambda c: (-self.node_attrs[c]["betweenness_centrality"], c))
        n_top = max(1, int(round(self.n_concepts * TOP_BRIDGE_FRAC)))
        self.bridges = ranked[:n_top]
        print(f"    graph edges    : {len(self.graph_edges)}")
        print(f"    bridges        : {len(self.bridges)}")

    # ── Stage 10: classifications ───────────────────────────────────────────

    def classify(self):
        print("  classifying …")
        # highly connected = top 10% by (in_deg + out_deg)
        ranked_conn = sorted(
            self.concept_ids,
            key=lambda c: (-(self.node_attrs[c]["in_degree"] + self.node_attrs[c]["out_degree"]),
                           c))
        n_top = max(1, int(round(self.n_concepts * 0.10)))
        highly_connected = ranked_conn[:n_top]
        # concept_hubs = same definition (alias kept for clarity in spec)
        concept_hubs = highly_connected
        # dependency_hubs = top by outgoing DEPENDS_ON + REQUIRES
        out_dep = defaultdict(int)
        for e in self.depends_on:
            out_dep[e["concept_src"]] += 1
        for e in self.requires:
            out_dep[e["concept_src"]] += 1
        ranked_dep = sorted(self.concept_ids,
                             key=lambda c: (-out_dep.get(c, 0), c))
        dependency_hubs = [c for c in ranked_dep[:n_top] if out_dep.get(c, 0) > 0]
        bridge_propositions = list(self.bridges)
        # highly stable edges = stability_score == 1.0
        all_edges = (self.associates + self.depends_on + self.requires
                     + self.precedes + self.follows + self.predicts)
        highly_stable_count = sum(1 for e in all_edges
                                   if e.get("stability_score", 0) == 1.0)
        # rare propositions = bottom quartile by support (still passing thresholds)
        sups = sorted(e["support_count"] for e in all_edges)
        if sups:
            q1 = sups[len(sups) // 4]
            rare_count = sum(1 for e in all_edges if e["support_count"] <= q1)
        else:
            q1 = 0
            rare_count = 0
        # global vs localized — by surah-span of evidence in cnt2 ayahs for the pair
        global_relations = []
        localized_relations = []
        for e in self.associates + self.depends_on + self.requires:
            # use evidence_paths (top 5) — for span we look at ALL co-occurring ayahs
            a = e.get("concept_a") or e.get("concept_src")
            b = e.get("concept_b") or e.get("concept_tgt")
            seqs_a = set(self.ayahs_per_concept.get(a, ()))
            seqs_b = set(self.ayahs_per_concept.get(b, ()))
            both = seqs_a & seqs_b
            surahs = self._surah_span(both)
            if len(surahs) >= 57:  # >= 50% of 114
                global_relations.append(
                    {"concept_a": a, "concept_b": b,
                     "relation_type": e["relation_type"],
                     "surah_count": len(surahs)})
            if len(surahs) <= 3 and len(surahs) > 0:
                localized_relations.append(
                    {"concept_a": a, "concept_b": b,
                     "relation_type": e["relation_type"],
                     "surahs": surahs,
                     "surah_count": len(surahs)})
        global_relations.sort(key=lambda x: (-x["surah_count"], x["concept_a"],
                                               x["concept_b"], x["relation_type"]))
        localized_relations.sort(key=lambda x: (x["surah_count"], x["concept_a"],
                                                  x["concept_b"], x["relation_type"]))

        # potential hierarchical = chains a -REQUIRES-> b -REQUIRES-> c (length >= 2)
        req_adj = defaultdict(set)
        for e in self.requires:
            req_adj[e["concept_src"]].add(e["concept_tgt"])
        hierarchical_chains = []
        for a in sorted(req_adj):
            for b in sorted(req_adj[a]):
                for c in sorted(req_adj.get(b, ())):
                    if c == a:
                        continue
                    hierarchical_chains.append([a, b, c])
        # potential causal = PRECEDES edges also present in DEPENDS_ON
        dep_pairs = {(e["concept_src"], e["concept_tgt"]) for e in self.depends_on}
        causal_pairs = []
        for e in self.precedes:
            if (e["concept_src"], e["concept_tgt"]) in dep_pairs:
                causal_pairs.append([e["concept_src"], e["concept_tgt"]])
        causal_pairs.sort()

        # potential recursive = directed cycles up to length 4 over DEPENDS_ON union REQUIRES union PRECEDES
        dir_adj = defaultdict(set)
        for e in self.depends_on:
            dir_adj[e["concept_src"]].add(e["concept_tgt"])
        for e in self.requires:
            dir_adj[e["concept_src"]].add(e["concept_tgt"])
        for e in self.precedes:
            dir_adj[e["concept_src"]].add(e["concept_tgt"])
        recursive_cycles_set = set()
        def find_cycles(start, current, depth, path):
            if depth > 4:
                return
            for nxt in sorted(dir_adj.get(current, ())):
                if nxt == start and 2 <= len(path) <= 4:
                    cyc = tuple(path + [nxt])
                    # canonicalise by rotation
                    rot = min(tuple(cyc[i:-1] + cyc[:i]) for i in range(len(cyc) - 1))
                    recursive_cycles_set.add(rot)
                elif nxt not in path:
                    find_cycles(start, nxt, depth + 1, path + [nxt])
        # bound: 103 concepts, fine to brute force depth-4 cycles
        for s in sorted(dir_adj):
            find_cycles(s, s, 1, [s])
        recursive_cycles = sorted([list(c) + [c[0]] for c in recursive_cycles_set])

        self.classifications = {
            "highly_connected_propositions": highly_connected,
            "concept_hubs": concept_hubs,
            "dependency_hubs": dependency_hubs,
            "bridge_propositions": bridge_propositions,
            "highly_stable_edge_count": highly_stable_count,
            "rare_edge_count": rare_count,
            "rare_threshold_support": q1,
            "global_relations": global_relations,
            "localized_relations": localized_relations,
            "potential_hierarchical_chains": hierarchical_chains,
            "potential_causal_pairs": causal_pairs,
            "potential_recursive_cycles": recursive_cycles,
        }
        # statistics block
        self.statistics = {
            "n_active_ayahs": self.n_active_ayahs,
            "n_concepts": self.n_concepts,
            "edge_counts": {
                "ASSOCIATES_WITH": len(self.associates),
                "CO_OCCURS": len(self.cooccurs),
                "DEPENDS_ON": len(self.depends_on),
                "REQUIRES": len(self.requires),
                "PRECEDES": len(self.precedes),
                "FOLLOWS": len(self.follows),
                "PREDICTS": len(self.predicts),
                "MEDIATES": len(self.med_triples),
                "CONDITIONAL_EMERGES": len(self.conditional),
            },
            "predicts_by_window": {str(w): len(self.predicts_by_window[w])
                                    for w in PREDICT_WINDOWS},
            "graph": {
                "node_count": self.n_concepts,
                "edge_count": len(self.graph_edges),
            },
            "averages": {
                "out_degree": r(sum(a["out_degree"] for a in self.node_attrs.values())
                                / self.n_concepts),
                "in_degree": r(sum(a["in_degree"] for a in self.node_attrs.values())
                                / self.n_concepts),
                "relation_diversity": r(sum(a["relation_diversity"]
                                             for a in self.node_attrs.values())
                                         / self.n_concepts),
                "betweenness": r(sum(a["betweenness_centrality"]
                                      for a in self.node_attrs.values())
                                  / self.n_concepts),
            },
        }

    # ── Stage 11: write outputs ──────────────────────────────────────────────

    def write(self):
        print("  writing outputs …")
        files = {}

        files["proposition_candidates.json"] = write_json(
            self.out_dir / "proposition_candidates.json",
            {
                "method": METHOD_VERSION,
                "n_concepts": self.n_concepts,
                "n_active_ayahs": self.n_active_ayahs,
                "relations": {
                    "ASSOCIATES_WITH": self.associates,
                    "CO_OCCURS": self.cooccurs,
                    "DEPENDS_ON": self.depends_on,
                    "REQUIRES": self.requires,
                    "PRECEDES": self.precedes,
                    "FOLLOWS": self.follows,
                    "PREDICTS": self.predicts,
                    "MEDIATES": self.med_triples,
                    "CONDITIONAL_EMERGES": self.conditional,
                },
                "statistics": self.statistics,
                "classifications": self.classifications,
            })

        files["proposition_graph.json"] = write_json(
            self.out_dir / "proposition_graph.json",
            {
                "method": METHOD_VERSION,
                "directed": True,
                "node_count": self.n_concepts,
                "edge_count": len(self.graph_edges),
                "edge_attributes": ["weight", "support", "stability", "type"],
                "nodes": [
                    {"concept_id": c, **self.node_attrs[c]}
                    for c in self.concept_ids
                ],
                "edges": self.graph_edges,
                "bridges": self.bridges,
            })

        files["dependency_candidates.json"] = write_json(
            self.out_dir / "dependency_candidates.json",
            {
                "method": METHOD_VERSION,
                "constants": {
                    "DEPENDS_LIFT_MIN": DEPENDS_LIFT_MIN,
                    "DEPENDS_CONF_MIN": DEPENDS_CONF_MIN,
                    "REQUIRES_CONF_MIN": REQUIRES_CONF_MIN,
                    "SUPPORT_MIN": SUPPORT_MIN,
                },
                "depends_on": self.depends_on,
                "requires": self.requires,
                "hierarchical_chains": self.classifications["potential_hierarchical_chains"],
            })

        files["implication_candidates.json"] = write_json(
            self.out_dir / "implication_candidates.json",
            {
                "method": METHOD_VERSION,
                "constants": {
                    "PREDICT_WINDOWS": list(PREDICT_WINDOWS),
                    "PREDICT_CONF_MIN": PREDICT_CONF_MIN,
                    "PREDICT_LIFT_MIN": PREDICT_LIFT_MIN,
                    "PREDICT_SUPPORT_MIN": PREDICT_SUPPORT_MIN,
                },
                "predicts_by_window": {
                    str(w): self.predicts_by_window[w] for w in PREDICT_WINDOWS
                },
            })

        files["conditional_patterns.json"] = write_json(
            self.out_dir / "conditional_patterns.json",
            {
                "method": METHOD_VERSION,
                "constants": {
                    "SYNERGY_MIN": SYNERGY_MIN,
                    "SYNERGY_SUPPORT_MIN": SYNERGY_SUPPORT_MIN,
                },
                "conditional_emerges": self.conditional,
            })

        files["bridge_patterns.json"] = write_json(
            self.out_dir / "bridge_patterns.json",
            {
                "method": METHOD_VERSION,
                "constants": {
                    "MED_CONF_MIN": MED_CONF_MIN,
                    "MED_ISO_MIN": MED_ISO_MIN,
                    "MED_SUPPORT_MIN": MED_SUPPORT_MIN,
                    "TOP_BRIDGE_FRAC": TOP_BRIDGE_FRAC,
                },
                "mediates": self.med_triples,
                "bridges": self.bridges,
                "bridge_betweenness": [
                    {"concept_id": c,
                     "betweenness_centrality": self.node_attrs[c]["betweenness_centrality"]}
                    for c in self.bridges
                ],
            })

        # manifest LAST (depends on byte sizes of above)
        manifest_input_files = [
            ("monad.db", self.db_path),
            ("root_profiles.json", self.lex_dir / "root_profiles.json"),
            ("lemma_profiles.json", self.lex_dir / "lemma_profiles.json"),
            ("distribution_profiles.json", self.lex_dir / "distribution_profiles.json"),
            ("semantic_neighbors.json", self.lex_dir / "semantic_neighbors.json"),
            ("concept_memberships.json",
             self.concepts_dir / "concept_memberships.json"),
            ("concept_candidates.json",
             self.concepts_dir / "concept_candidates.json"),
            ("concept_graph.json", self.concepts_dir / "concept_graph.json"),
            ("concept_manifest.json", self.concepts_dir / "concept_manifest.json"),
        ]
        input_sha = {name: sha256_file(p) for name, p in manifest_input_files}

        manifest = {
            "method": METHOD_VERSION,
            "constants": {
                "NPMI_MIN": NPMI_MIN,
                "SUPPORT_MIN": SUPPORT_MIN,
                "DEPENDS_LIFT_MIN": DEPENDS_LIFT_MIN,
                "DEPENDS_CONF_MIN": DEPENDS_CONF_MIN,
                "REQUIRES_CONF_MIN": REQUIRES_CONF_MIN,
                "ORDER_ASYM_MIN": ORDER_ASYM_MIN,
                "ORDER_SUPPORT_MIN": ORDER_SUPPORT_MIN,
                "PREDICT_WINDOWS": list(PREDICT_WINDOWS),
                "PREDICT_LIFT_MIN": PREDICT_LIFT_MIN,
                "PREDICT_CONF_MIN": PREDICT_CONF_MIN,
                "PREDICT_SUPPORT_MIN": PREDICT_SUPPORT_MIN,
                "MED_CONF_MIN": MED_CONF_MIN,
                "MED_ISO_MIN": MED_ISO_MIN,
                "MED_SUPPORT_MIN": MED_SUPPORT_MIN,
                "SYNERGY_MIN": SYNERGY_MIN,
                "SYNERGY_SUPPORT_MIN": SYNERGY_SUPPORT_MIN,
                "TRIPLE_PREFILTER": TRIPLE_PREFILTER,
                "EVIDENCE_TOP": EVIDENCE_TOP,
                "PERTURB": list(PERTURB),
                "ROUND": ROUND,
                "TOP_BRIDGE_FRAC": TOP_BRIDGE_FRAC,
            },
            "input_sha256": input_sha,
            "totals": {
                "concept_count": self.n_concepts,
                "active_ayahs": self.n_active_ayahs,
                "edges_total": sum(self.statistics["edge_counts"].values()),
                **{f"edges_{k}": v
                    for k, v in self.statistics["edge_counts"].items()},
                "graph_edges": len(self.graph_edges),
                "bridges": len(self.bridges),
                "hierarchical_chains":
                    len(self.classifications["potential_hierarchical_chains"]),
                "causal_pairs":
                    len(self.classifications["potential_causal_pairs"]),
                "recursive_cycles":
                    len(self.classifications["potential_recursive_cycles"]),
            },
            "prohibitions_observed": [
                "no ontology", "no axioms", "no contradiction engine",
                "no theology", "no interpretation", "no doctrine",
                "no origin claims", "no concept translation",
                "no proposition naming", "no semantic labels",
                "no external knowledge",
                "propositions discovered not invented",
            ],
            "output_bytes": files,
        }
        files["proposition_manifest.json"] = write_json(
            self.out_dir / "proposition_manifest.json", manifest)

        for name in sorted(files):
            print(f"    {name:35s} {files[name]:>11,d} bytes")

    # ── Orchestration ────────────────────────────────────────────────────────

    def run(self):
        print(f"\nBuilding Proposition Discovery Engine from {self.concepts_dir} …\n")
        self.load()
        self.count()
        self.assoc()
        self.dependency()
        self.ordering()
        self.predicts()
        self.mediates()
        self.conditional()
        self.graph()
        self.classify()
        self.write()
        print("\nProposition discovery complete.\n")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--lex", default=str(DEFAULT_LEX))
    ap.add_argument("--concepts", default=str(DEFAULT_CONCEPTS))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    for p in (Path(args.db),
              Path(args.lex) / "root_profiles.json",
              Path(args.concepts) / "concept_memberships.json"):
        if not p.exists():
            print(f"Required input not found: {p}")
            sys.exit(1)

    PropositionBuilder(args.db, args.lex, args.concepts, args.out).run()


if __name__ == "__main__":
    main()
