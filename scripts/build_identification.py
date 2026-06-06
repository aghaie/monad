#!/usr/bin/env python3
"""
Monad — Phase 6: Concept Identification Engine
==============================================

Purpose
-------
Reveal *what evidence* defines each discovered concept structure inside the
Quranic corpus. This engine assigns **no meaning**. It does not rename, label,
translate, or interpret any concept, root, or lemma. It only exposes the raw
Quran-internal evidence that defines each opaque concept:

    * dominant member roots
    * dominant member lemmas
    * most strongly activating ayahs
    * surahs carrying the concept's activity
    * neighbouring concepts and the structures that depend on / surround it

The Quran is the only semantic universe. No external dictionary, tafsir,
translation, theology, ontology, embedding, or interpretation is used. Phases
1–5 are read and hashed but never rebuilt or modified.

Inputs (read-only)
------------------
    generated/monad.db
    generated/lexicon/semantic_neighbors.json
    generated/concepts/{concept_candidates,concept_centers,concept_graph,
                        concept_memberships,concept_relationships}.json
    generated/propositions/{proposition_candidates,proposition_graph,
                            dependency_candidates}.json
    generated/compression/{foundationality_scores,dependency_layers,
                           irreducible_structures,reconstruction_sets,
                           hub_removal_analysis,compression_statistics}.json

Outputs
-------
    generated/identification/
        concept_profiles.json
        dominant_roots.json
        dominant_lemmas.json
        ayah_signatures.json
        surah_signatures.json
        concept_atlas.json
        core_investigation.json
        identification_manifest.json

Method
------
Concept activation reuses the Phase-4 rule exactly: an ayah activates a concept
iff any of the ayah's word tokens carries a root_id or lemma_id that is a member
of that concept. On top of that binary rule this engine computes an evidence-
weighted *activation strength* per (concept, ayah): the summed Phase-3 membership
confidence of the member tokens that fire in the ayah (each word counted once at
its strongest membership). All rankings derive from corpus counts and Phase-3/4/5
statistics only. Deterministic, pure-stdlib, byte-identically reproducible.
"""

import argparse
import hashlib
import json
import sqlite3
from collections import defaultdict
from pathlib import Path

METHOD = "phase6-identification-1.0"
ROUND = 6

# Ranking / reporting constants
AYAH_TOPS = [25, 50, 100]      # ayah-signature depths
ATLAS_TOP = 10                 # neighbours / partners per axis in the atlas
PROP_TOP = 15                  # strongest incident propositions per concept
SURAH_TOP = 10                 # surahs per ranking axis
CORE_AYAH_TOP = 25             # ayah evidence depth inside core investigation
CORE_ENTITY_TOP = 20           # roots / lemmas depth inside core investigation
TOP_FOUNDATIONAL = 20          # size of the foundational deep-dive set

PROHIBITIONS = [
    "no concept renaming",
    "no concept labels",
    "no assigned meanings",
    "no root translation",
    "no lemma translation",
    "no ontology",
    "no axioms",
    "no contradiction engine",
    "no theology",
    "no doctrine",
    "no divine origin claim",
    "no human origin claim",
    "no interpretation",
    "no external knowledge",
    "concepts remain opaque",
    "prior phases never rebuilt",
]

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


class IdentificationEngine:
    def __init__(self, db_path, lex_dir, concepts_dir, props_dir, comp_dir, out_dir):
        self.db_path = Path(db_path)
        self.lex_dir = Path(lex_dir)
        self.concepts_dir = Path(concepts_dir)
        self.props_dir = Path(props_dir)
        self.comp_dir = Path(comp_dir)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    # ── Stage 1: load all prior-phase products ──────────────────────────────────

    def load(self):
        print("  loading Phase-3 concept set & memberships …")
        self.memberships = json.loads(
            (self.concepts_dir / "concept_memberships.json").read_text("utf-8"))
        self.candidates = json.loads(
            (self.concepts_dir / "concept_candidates.json").read_text("utf-8"))
        self.centers = json.loads(
            (self.concepts_dir / "concept_centers.json").read_text("utf-8"))["concepts"]
        self.cgraph = json.loads(
            (self.concepts_dir / "concept_graph.json").read_text("utf-8"))
        self.crel = json.loads(
            (self.concepts_dir / "concept_relationships.json").read_text("utf-8"))["relationships"]

        self.concept_ids = sorted(self.memberships["concepts"].keys())
        self.n_concepts = len(self.concept_ids)

        # per-concept candidate record (distribution, density, stability, …)
        self.cand = {c["concept_id"]: c for c in self.candidates["concepts"]}
        self.cgraph_node = {n["id"]: n for n in self.cgraph["nodes"]}

        # root_id -> {concept_id: confidence}, lemma_id -> {concept_id: confidence}
        self.root_concept_conf = {}
        for rid, members in self.memberships["root_memberships"].items():
            self.root_concept_conf[int(rid)] = {m["concept_id"]: m["membership_confidence"]
                                                for m in members}
        self.lemma_concept_conf = {}
        for lid, members in self.memberships["lemma_memberships"].items():
            self.lemma_concept_conf[int(lid)] = {m["concept_id"]: m["membership_confidence"]
                                                 for m in members}

        # concept -> ordered member roots / lemmas (id + confidence)
        self.concept_member_roots = {}
        self.concept_member_lemmas = {}
        for cid, rec in self.memberships["concepts"].items():
            self.concept_member_roots[cid] = {m["root_id"]: m["membership_confidence"]
                                              for m in rec["member_roots"]}
            self.concept_member_lemmas[cid] = {m["lemma_id"]: m["membership_confidence"]
                                               for m in rec["member_lemmas"]}

        print("  loading Phase-2 semantic-neighbour adjacency …")
        sn = json.loads((self.lex_dir / "semantic_neighbors.json").read_text("utf-8"))
        self.root_adj = {}
        for rid, v in sn["roots"].items():
            self.root_adj[int(rid)] = {n["root_id"]: n["confidence"] for n in v["neighbors"]}
        self.lemma_adj = {}
        for lid, v in sn["lemmas"].items():
            self.lemma_adj[int(lid)] = {n["lemma_id"]: n["confidence"] for n in v["neighbors"]}

        print("  loading Phase-4 propositions …")
        self.prop_cand = json.loads(
            (self.props_dir / "proposition_candidates.json").read_text("utf-8"))
        self.prop_graph = json.loads(
            (self.props_dir / "proposition_graph.json").read_text("utf-8"))
        self.prop_node = {n["concept_id"]: n for n in self.prop_graph["nodes"]}
        self.prop_bridges = set(self.prop_graph["bridges"])
        self.dep_cand = json.loads(
            (self.props_dir / "dependency_candidates.json").read_text("utf-8"))

        print("  loading Phase-5 compression …")
        self.found = json.loads(
            (self.comp_dir / "foundationality_scores.json").read_text("utf-8"))
        self.found_by_cid = {s["concept_id"]: s for s in self.found["scores"]}
        self.found_order = self.found["foundationality_order"]
        self.dep_layers = json.loads(
            (self.comp_dir / "dependency_layers.json").read_text("utf-8"))
        self.irreducible = json.loads(
            (self.comp_dir / "irreducible_structures.json").read_text("utf-8"))
        self.recon = json.loads(
            (self.comp_dir / "reconstruction_sets.json").read_text("utf-8"))
        self.hub_removal = json.loads(
            (self.comp_dir / "hub_removal_analysis.json").read_text("utf-8"))
        self.comp_stats = json.loads(
            (self.comp_dir / "compression_statistics.json").read_text("utf-8"))

        # concept -> dependency-layer level, and concept -> SCC component index
        self.concept_layer = {}
        for layer in self.dep_layers["layers"]:
            for c in layer["concepts"]:
                self.concept_layer[c] = layer["level"]
        self.concept_scc = {}
        self.scc_components = self.dep_layers["scc_summary"]
        for comp in self.scc_components:
            for c in comp["concepts"]:
                self.concept_scc[c] = comp["component_index"]
        # dependency-irreducible (SCC size >= 2) components containing each concept
        self.concept_irr = {}
        for comp in self.irreducible["dependency_irreducible"]["components"]:
            for c in comp["concepts"]:
                self.concept_irr[c] = comp
        self.directional_scc = set(
            self.irreducible["directional_irreducible"]["components"][0]["concepts"]
        ) if self.irreducible["directional_irreducible"]["components"] else set()

        # Phase-3 classifications (bridge / global / localized …)
        self.concept_classes = defaultdict(list)
        stats = json.loads(
            (self.concepts_dir / "concept_statistics.json").read_text("utf-8"))
        for cls, members in stats["classifications"].items():
            for c in members:
                self.concept_classes[c].append(cls)

        # ── corpus tables ──────────────────────────────────────────────────────
        print("  loading Phase-1 corpus tables …")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("SELECT root_id, root_arabic, token_count FROM roots")
        self.root_ar = {}
        self.root_token_count = {}
        for rid, ar, tc in cur.fetchall():
            self.root_ar[rid] = ar
            self.root_token_count[rid] = tc

        cur.execute("SELECT lemma_id, lemma_arabic FROM lemmas")
        self.lemma_ar = {lid: ar for lid, ar in cur.fetchall()}

        cur.execute("SELECT surah_number, ayah_count, revelation_type FROM surahs")
        self.surah_ayah_count = {}
        self.surah_revelation = {}
        for sn_, ac, rt in cur.fetchall():
            self.surah_ayah_count[sn_] = ac
            self.surah_revelation[sn_] = rt

        cur.execute("SELECT ayah_sequential, surah_number, ayah_number "
                    "FROM ayahs ORDER BY ayah_sequential")
        self.ayah_meta = {}
        for seq, surah, ayah in cur.fetchall():
            self.ayah_meta[seq] = (surah, ayah)
        self.n_ayahs = len(self.ayah_meta)
        seq_lookup = {v: k for k, v in self.ayah_meta.items()}

        # per-ayah word tokens (root_id, lemma_id)
        cur.execute("SELECT surah_number, ayah_number, word_position, root_id, lemma_id "
                    "FROM words ORDER BY surah_number, ayah_number, word_position")
        self.ayah_words = defaultdict(list)
        for surah, ayah, pos, rid, lid in cur.fetchall():
            seq = seq_lookup[(surah, ayah)]
            self.ayah_words[seq].append((rid, lid))
        conn.close()
        print(f"    concepts={self.n_concepts}  ayahs={self.n_ayahs}")

    # ── Stage 2: concept activation (Phase-4-consistent) ────────────────────────

    def activate(self):
        print("  computing per-ayah concept activation strength …")
        # activation[cid] -> list of (seq, strength, contrib_roots:set, contrib_lemmas:set)
        self.activation = defaultdict(list)
        # per concept, per member root/lemma: ayah & token contribution counts
        self.root_ayahs = defaultdict(lambda: defaultdict(int))   # cid -> rid -> #ayahs
        self.root_tokens = defaultdict(lambda: defaultdict(int))  # cid -> rid -> #tokens
        self.lemma_ayahs = defaultdict(lambda: defaultdict(int))
        self.lemma_tokens = defaultdict(lambda: defaultdict(int))
        # per concept, per surah: #activating ayahs
        self.surah_ayahs = defaultdict(lambda: defaultdict(int))

        for seq in sorted(self.ayah_words.keys()):
            surah = self.ayah_meta[seq][0]
            # accumulate strength per concept for this ayah
            strength = defaultdict(float)
            croots = defaultdict(set)
            clemmas = defaultdict(set)
            rt_seen = defaultdict(set)   # cid -> set(rid) firing in this ayah
            lm_seen = defaultdict(set)
            rt_tok = defaultdict(lambda: defaultdict(int))
            lm_tok = defaultdict(lambda: defaultdict(int))
            for rid, lid in self.ayah_words[seq]:
                rconf = self.root_concept_conf.get(rid, {}) if rid is not None else {}
                lconf = self.lemma_concept_conf.get(lid, {}) if lid is not None else {}
                # candidate concepts this word touches
                touched = set(rconf) | set(lconf)
                for cid in touched:
                    # each word contributes once, at its strongest membership
                    contrib = max(rconf.get(cid, 0.0), lconf.get(cid, 0.0))
                    strength[cid] += contrib
                    if cid in rconf:
                        croots[cid].add(rid)
                        rt_seen[cid].add(rid)
                        rt_tok[cid][rid] += 1
                    if cid in lconf:
                        clemmas[cid].add(lid)
                        lm_seen[cid].add(lid)
                        lm_tok[cid][lid] += 1
            for cid, s in strength.items():
                self.activation[cid].append(
                    (seq, r(s), sorted(croots[cid]), sorted(clemmas[cid])))
                self.surah_ayahs[cid][surah] += 1
                for rid in rt_seen[cid]:
                    self.root_ayahs[cid][rid] += 1
                    self.root_tokens[cid][rid] += rt_tok[cid][rid]
                for lid in lm_seen[cid]:
                    self.lemma_ayahs[cid][lid] += 1
                    self.lemma_tokens[cid][lid] += lm_tok[cid][lid]

        self.activation_count = {cid: len(v) for cid, v in self.activation.items()}
        for cid in self.concept_ids:
            self.activation_count.setdefault(cid, 0)
        print(f"    active concepts: {sum(1 for c in self.activation_count.values() if c)}")

    # ── helpers ─────────────────────────────────────────────────────────────────

    def _neighbour_influence(self, eid, member_set, adj):
        """Summed Phase-2 semantic-neighbour confidence from entity `eid` to the
        co-members of its concept (extends the Phase-3 center metric to all
        members). Evidence-only graph quantity; no meaning."""
        nbrs = adj.get(eid, {})
        return r(sum(w for v, w in nbrs.items() if v in member_set and v != eid))

    def _surah_str(self, seq):
        s, a = self.ayah_meta[seq]
        return {"surah": s, "ayah": a}

    # ── PHASE B: dominant roots ─────────────────────────────────────────────────

    def dominant_roots(self):
        print("  PHASE B — dominant roots …")
        out = {}
        for cid in self.concept_ids:
            members = self.concept_member_roots[cid]
            member_set = set(members)
            rows = []
            for rid, conf in members.items():
                in_tokens = self.root_tokens[cid].get(rid, 0)
                in_ayahs = self.root_ayahs[cid].get(rid, 0)
                act_weight = in_tokens * conf
                rows.append({
                    "root_id": rid,
                    "root_arabic": self.root_ar.get(rid, ""),
                    "membership_confidence": r(conf),
                    "corpus_token_count": self.root_token_count.get(rid, 0),
                    "in_concept_token_count": in_tokens,
                    "in_concept_ayah_count": in_ayahs,
                    "activation_weight": r(act_weight),
                    "neighborhood_influence": self._neighbour_influence(
                        rid, member_set, self.root_adj),
                    "stability_contribution": r(conf),
                })
            tot = sum(x["activation_weight"] for x in rows) or 1.0
            for x in rows:
                x["activation_share"] = r(x["activation_weight"] / tot)
            rows.sort(key=lambda d: (-d["activation_weight"], -d["membership_confidence"],
                                     -d["corpus_token_count"], d["root_id"]))
            for i, x in enumerate(rows):
                x["rank"] = i + 1
            out[cid] = {"root_count": len(rows), "roots": rows}
        self.dom_roots = out
        return {
            "method": METHOD,
            "metric_definitions": {
                "corpus_token_count": "total token occurrences of the root in the whole corpus (Phase-1 roots.token_count)",
                "in_concept_token_count": "root tokens occurring inside ayahs that activate this concept",
                "in_concept_ayah_count": "distinct concept-activating ayahs containing the root",
                "activation_weight": "in_concept_token_count * membership_confidence",
                "activation_share": "activation_weight normalised to sum 1 across the concept's roots",
                "neighborhood_influence": "summed Phase-2 semantic-neighbour confidence from the root to its concept co-member roots",
                "stability_contribution": "Phase-3 membership_confidence (fraction of perturbation runs the root stayed in the concept)",
            },
            "concepts": out,
        }

    # ── PHASE C: dominant lemmas ────────────────────────────────────────────────

    def dominant_lemmas(self):
        print("  PHASE C — dominant lemmas …")
        out = {}
        for cid in self.concept_ids:
            members = self.concept_member_lemmas[cid]
            member_set = set(members)
            rows = []
            for lid, conf in members.items():
                in_tokens = self.lemma_tokens[cid].get(lid, 0)
                in_ayahs = self.lemma_ayahs[cid].get(lid, 0)
                act_weight = in_tokens * conf
                rows.append({
                    "lemma_id": lid,
                    "lemma_arabic": self.lemma_ar.get(lid, ""),
                    "membership_confidence": r(conf),
                    "in_concept_token_count": in_tokens,
                    "in_concept_ayah_count": in_ayahs,
                    "activation_weight": r(act_weight),
                    "graph_influence": self._neighbour_influence(
                        lid, member_set, self.lemma_adj),
                })
            tot = sum(x["activation_weight"] for x in rows) or 1.0
            for x in rows:
                x["activation_share"] = r(x["activation_weight"] / tot)
            rows.sort(key=lambda d: (-d["activation_weight"], -d["membership_confidence"],
                                     d["lemma_id"]))
            for i, x in enumerate(rows):
                x["rank"] = i + 1
            out[cid] = {"lemma_count": len(rows), "lemmas": rows}
        self.dom_lemmas = out
        return {
            "method": METHOD,
            "metric_definitions": {
                "in_concept_token_count": "lemma tokens occurring inside ayahs that activate this concept",
                "in_concept_ayah_count": "distinct concept-activating ayahs containing the lemma",
                "activation_weight": "in_concept_token_count * membership_confidence",
                "activation_share": "activation_weight normalised to sum 1 across the concept's lemmas",
                "graph_influence": "summed Phase-2 semantic-neighbour confidence from the lemma to its concept co-member lemmas",
            },
            "concepts": out,
        }

    # ── PHASE D: ayah signatures ────────────────────────────────────────────────

    def ayah_signatures(self):
        print("  PHASE D — ayah signatures …")
        out = {}
        for cid in self.concept_ids:
            acts = self.activation.get(cid, [])
            # sort by strength desc, then n_member_tokens desc, then ayah order
            ranked = sorted(
                acts,
                key=lambda t: (-t[1], -(len(t[2]) + len(t[3])), t[0]))
            max_s = ranked[0][1] if ranked else 0.0
            entry = {"activation_count": len(acts)}
            for depth in AYAH_TOPS:
                lst = []
                for seq, s, croots, clemmas in ranked[:depth]:
                    surah, ayah = self.ayah_meta[seq]
                    lst.append({
                        "surah": surah,
                        "ayah": ayah,
                        "activation_strength": s,
                        "confidence": r(s / max_s) if max_s else 0.0,
                        "member_token_count": len(croots) + len(clemmas),
                        "contributing_roots": [
                            {"root_id": rid, "root_arabic": self.root_ar.get(rid, "")}
                            for rid in croots],
                        "contributing_lemmas": [
                            {"lemma_id": lid, "lemma_arabic": self.lemma_ar.get(lid, "")}
                            for lid in clemmas],
                    })
                entry[f"top_{depth}"] = lst
            out[cid] = entry
        self.ayah_sig = out
        return {
            "method": METHOD,
            "definition": ("activation_strength = summed Phase-3 membership confidence of the "
                           "member tokens firing in the ayah (each word counted once at its "
                           "strongest membership). confidence = activation_strength / the "
                           "concept's maximum activation_strength. Evidence only; no meaning."),
            "depths": AYAH_TOPS,
            "concepts": out,
        }

    # ── PHASE E: surah signatures ───────────────────────────────────────────────

    def surah_signatures(self):
        print("  PHASE E — surah signatures …")
        out = {}
        for cid in self.concept_ids:
            total = self.activation_count[cid]
            base = (total / self.n_ayahs) if total else 0.0
            rows = []
            for surah, cnt in self.surah_ayahs[cid].items():
                sac = self.surah_ayah_count.get(surah, 0) or 1
                density = cnt / sac
                share = (cnt / total) if total else 0.0
                lift = (density / base) if base else 0.0
                rows.append({
                    "surah": surah,
                    "revelation_type": self.surah_revelation.get(surah, ""),
                    "surah_ayah_count": self.surah_ayah_count.get(surah, 0),
                    "activating_ayahs": cnt,
                    "density": r(density),
                    "share": r(share),
                    "uniqueness_lift": r(lift),
                })
            by_count = sorted(rows, key=lambda d: (-d["activating_ayahs"], d["surah"]))
            by_density = sorted(rows, key=lambda d: (-d["density"], d["surah"]))
            by_uniq = sorted(rows, key=lambda d: (-d["uniqueness_lift"], d["surah"]))
            out[cid] = {
                "total_activating_ayahs": total,
                "surahs_present": len(rows),
                "highest_activation_surahs": by_count[:SURAH_TOP],
                "highest_density_surahs": by_density[:SURAH_TOP],
                "highest_uniqueness_surahs": by_uniq[:SURAH_TOP],
            }
        self.surah_sig = out
        return {
            "method": METHOD,
            "metric_definitions": {
                "activating_ayahs": "distinct ayahs of the surah that activate the concept",
                "density": "activating_ayahs / surah_ayah_count",
                "share": "activating_ayahs / concept's total activating ayahs",
                "uniqueness_lift": "density divided by the concept's corpus-wide activation rate "
                                   "(total activating ayahs / total ayahs); >1 = over-represented",
            },
            "concepts": out,
        }

    # ── proposition indexing (incident relations per concept) ───────────────────

    def _index_propositions(self):
        """Build per-concept incident-relation lists from Phase-4 candidates."""
        incident = defaultdict(list)
        rels = self.prop_cand["relations"]

        def add(cid, rec):
            incident[cid].append(rec)

        for rel in rels["ASSOCIATES_WITH"] + rels["CO_OCCURS"]:
            a, b = rel["concept_a"], rel["concept_b"]
            base = {"relation_type": rel["relation_type"], "direction": "undirected",
                    "support_count": rel["support_count"], "confidence": rel["confidence"]}
            add(a, dict(base, partner=b))
            add(b, dict(base, partner=a))
        for key in ("DEPENDS_ON", "REQUIRES", "PRECEDES", "FOLLOWS", "PREDICTS"):
            for rel in rels[key]:
                s, t = rel["concept_src"], rel["concept_tgt"]
                base = {"relation_type": rel["relation_type"],
                        "support_count": rel["support_count"], "confidence": rel["confidence"]}
                add(s, dict(base, direction="out", partner=t))
                add(t, dict(base, direction="in", partner=s))
        for rel in rels["MEDIATES"]:
            m = rel["concept_mediator"]
            add(m, {"relation_type": "MEDIATES", "direction": "mediator",
                    "partner": f'{rel["concept_a"]}->{rel["concept_d"]}',
                    "support_count": rel["support_count_with_mediator"],
                    "confidence": rel["confidence"]})
        for rel in rels["CONDITIONAL_EMERGES"]:
            e = rel["concept_e"]
            add(e, {"relation_type": "CONDITIONAL_EMERGES", "direction": "emerges",
                    "partner": f'{rel["concept_a"]}+{rel["concept_b"]}',
                    "support_count": rel["support_count"], "confidence": rel["confidence"]})
        self.incident = incident

    # ── PHASE F: concept atlas ──────────────────────────────────────────────────

    def concept_atlas(self):
        print("  PHASE F — concept atlas …")
        self._index_propositions()
        rels = self.prop_cand["relations"]

        # dependency relations indexed by concept and direction
        dep_in = defaultdict(list)
        dep_out = defaultdict(list)
        for key in ("DEPENDS_ON", "REQUIRES"):
            for rel in rels[key]:
                s, t = rel["concept_src"], rel["concept_tgt"]
                rec = {"relation_type": rel["relation_type"], "partner": t,
                       "confidence": rel["confidence"],
                       "support_count": rel["support_count"]}
                if "lift" in rel:
                    rec["lift"] = rel["lift"]
                dep_out[s].append(rec)
                dep_in[t].append({"relation_type": rel["relation_type"], "partner": s,
                                  "confidence": rel["confidence"],
                                  "support_count": rel["support_count"],
                                  **({"lift": rel["lift"]} if "lift" in rel else {})})

        # mediation where concept is mediator
        med_by = defaultdict(list)
        for rel in rels["MEDIATES"]:
            med_by[rel["concept_mediator"]].append({
                "between": f'{rel["concept_a"]}->{rel["concept_d"]}',
                "support_count": rel["support_count_with_mediator"],
                "confidence": rel["confidence"],
                "isolation": rel.get("isolation")})

        out = {}
        for cid in self.concept_ids:
            # closest concepts (Phase-3 semantic overlap)
            closest = [{"concept_id": rc["concept_id"], "weight": rc["weight"]}
                       for rc in self.crel.get(cid, {}).get("related_concepts", [])][:ATLAS_TOP]
            node = self.prop_node.get(cid, {})
            # strongest dependencies
            deps_out = sorted(dep_out.get(cid, []),
                              key=lambda d: (-d["confidence"], -d["support_count"], d["partner"]))[:ATLAS_TOP]
            deps_in = sorted(dep_in.get(cid, []),
                             key=lambda d: (-d["confidence"], -d["support_count"], d["partner"]))[:ATLAS_TOP]
            # strongest propositions (any incident relation, by support then confidence)
            props = sorted(self.incident.get(cid, []),
                           key=lambda d: (-d["support_count"], -d["confidence"],
                                          d["relation_type"], str(d["partner"])))[:PROP_TOP]
            # strongest bridges (mediation by this concept)
            bridges = sorted(med_by.get(cid, []),
                             key=lambda d: (-d["support_count"], -d["confidence"], d["between"]))[:ATLAS_TOP]
            # strongest cycles: dependency-irreducible SCC membership + directional SCC
            irr = self.concept_irr.get(cid)
            cycles = {
                "dependency_scc": (
                    {"concepts": irr["concepts"], "size": irr["size"],
                     "internal_edges": irr["internal_edges"],
                     "edge_density": irr["edge_density"]}
                    if irr else None),
                "in_directional_core": cid in self.directional_scc,
            }
            out[cid] = {
                "closest_concepts": closest,
                "proposition_top_in_partners": node.get("top_in_partners", [])[:ATLAS_TOP],
                "proposition_top_out_partners": node.get("top_out_partners", [])[:ATLAS_TOP],
                "strongest_dependencies_out": deps_out,
                "strongest_dependencies_in": deps_in,
                "strongest_propositions": props,
                "strongest_bridges": bridges,
                "strongest_cycles": cycles,
                "dependency_layer": self.concept_layer.get(cid),
                "scc_component_index": self.concept_scc.get(cid),
                "is_proposition_bridge": cid in self.prop_bridges,
            }
        self.atlas = out
        return {"method": METHOD,
                "definition": ("closest_concepts = Phase-3 semantic-overlap neighbours; "
                               "strongest_* = highest-support / highest-confidence incident "
                               "Phase-4 relations; strongest_cycles = the Phase-5 irreducible "
                               "(strongly-connected) structures the concept belongs to. "
                               "Evidence only; no meaning."),
                "concepts": out}

    # ── PHASE A: concept profiles ───────────────────────────────────────────────

    def concept_profiles(self):
        print("  PHASE A — concept profiles …")
        out = {}
        for cid in self.concept_ids:
            cand = self.cand[cid]
            cnode = self.cgraph_node.get(cid, {})
            cen = self.centers.get(cid, {})
            pnode = self.prop_node.get(cid, {})
            fnd = self.found_by_cid.get(cid, {})
            dist = cand["distribution_profile"]
            acts = self.activation.get(cid, [])
            strengths = [a[1] for a in acts]
            # incident dependency counts
            inc = fnd.get("incidence_by_type", {})
            out[cid] = {
                "concept_id": cid,
                "root_count": cand["size_roots"],
                "lemma_count": cand["size_lemmas"],
                "member_roots": [{"root_id": m["root_id"],
                                  "root_arabic": self.root_ar.get(m["root_id"], ""),
                                  "membership_confidence": m["membership_confidence"]}
                                 for m in self.memberships["concepts"][cid]["member_roots"]],
                "member_lemmas": [{"lemma_id": m["lemma_id"],
                                   "lemma_arabic": self.lemma_ar.get(m["lemma_id"], ""),
                                   "membership_confidence": m["membership_confidence"]}
                                  for m in self.memberships["concepts"][cid]["member_lemmas"]],
                "activation_count": self.activation_count[cid],
                "activation_strength_total": r(sum(strengths)),
                "activation_strength_max": r(max(strengths)) if strengths else 0.0,
                "activation_strength_mean": r(sum(strengths) / len(strengths)) if strengths else 0.0,
                "surah_distribution": {str(s): c for s, c in sorted(self.surah_ayahs[cid].items())},
                "ayah_distribution": {
                    "total_token_occurrences": dist["total_occurrences"],
                    "surah_count": dist["surah_count"],
                    "surah_coverage": dist["surah_coverage"],
                    "top_surah_share": dist["top_surah_share"],
                    "evenness": dist["evenness"],
                    "meccan_occurrences": dist["meccan_occurrences"],
                    "medinan_occurrences": dist["medinan_occurrences"],
                    "medinan_fraction": dist["medinan_fraction"],
                },
                "centrality_metrics": {
                    "concept_graph": {
                        "degree_centrality": cnode.get("degree_centrality"),
                        "betweenness_centrality": cnode.get("betweenness_centrality"),
                        "eigenvector_centrality": cnode.get("eigenvector_centrality"),
                        "meta_community": cnode.get("meta_community"),
                    },
                    "proposition_graph": {
                        "in_degree": pnode.get("in_degree"),
                        "out_degree": pnode.get("out_degree"),
                        "betweenness_centrality": pnode.get("betweenness_centrality"),
                        "relation_diversity": pnode.get("relation_diversity"),
                    },
                },
                "compression_metrics": {
                    "foundationality_composite": fnd.get("composite_score"),
                    "foundationality_rank": fnd.get("rank"),
                    "removal_impact_count": fnd.get("removal_impact_count"),
                    "removal_impact_fraction": fnd.get("removal_impact_fraction"),
                    "support_weighted_loss": fnd.get("support_weighted_loss"),
                    "dependency_impact": fnd.get("dependency_impact"),
                    "reach_reduction": fnd.get("reach_reduction"),
                    "fragmentation_components_added": fnd.get("fragmentation_components_added"),
                    "information_loss_bits": fnd.get("information_loss_bits"),
                },
                "dependency_metrics": {
                    "dependency_layer": self.concept_layer.get(cid),
                    "scc_component_index": self.concept_scc.get(cid),
                    "in_dependency_irreducible_core": cid in self.concept_irr,
                    "in_directional_core": cid in self.directional_scc,
                    "incident_DEPENDS_ON": inc.get("DEPENDS_ON", 0),
                    "incident_REQUIRES": inc.get("REQUIRES", 0),
                },
                "internal_structure": {
                    "internal_density": cand["internal_density"],
                    "external_separation": cand["external_separation"],
                    "cohesion_score": cand["cohesion_score"],
                    "cluster_stability": cand["cluster_stability"],
                    "boundary_weight": cand["boundary_weight"],
                    "internal_edges": cand["internal_edges"],
                },
                "phase3_classifications": sorted(self.concept_classes.get(cid, [])),
                "is_proposition_bridge": cid in self.prop_bridges,
            }
        self.profiles = out
        return {"method": METHOD, "n_concepts": self.n_concepts, "concepts": out}

    # ── PHASE G: dominant-core investigation ────────────────────────────────────

    def _deep_profile(self, cid):
        """Evidence-only deep profile of a single concept (no interpretation)."""
        return {
            "concept_id": cid,
            "profile": self.profiles[cid],
            "dominant_roots": self.dom_roots[cid]["roots"][:CORE_ENTITY_TOP],
            "dominant_lemmas": self.dom_lemmas[cid]["lemmas"][:CORE_ENTITY_TOP],
            "top_ayahs": self.ayah_sig[cid][f"top_{CORE_AYAH_TOP}"],
            "highest_activation_surahs": self.surah_sig[cid]["highest_activation_surahs"],
            "highest_uniqueness_surahs": self.surah_sig[cid]["highest_uniqueness_surahs"],
            "atlas": self.atlas[cid],
        }

    def core_investigation(self):
        print("  PHASE G — dominant-core investigation …")
        focus = ["CONCEPT_007", "CONCEPT_016"]
        top20 = self.found_order[:TOP_FOUNDATIONAL]

        deep_targets = []
        for c in focus + top20:
            if c not in deep_targets:
                deep_targets.append(c)

        deep = {c: self._deep_profile(c) for c in deep_targets}

        # largest SCC structures (dependency-irreducible components, size desc)
        scc_struct = []
        comps = sorted(self.irreducible["dependency_irreducible"]["components"],
                       key=lambda c: (-c["size"], c["concepts"][0]))
        for comp in comps:
            members = []
            for c in comp["concepts"]:
                fnd = self.found_by_cid.get(c, {})
                members.append({
                    "concept_id": c,
                    "foundationality_rank": fnd.get("rank"),
                    "foundationality_composite": fnd.get("composite_score"),
                    "activation_count": self.activation_count[c],
                    "dependency_layer": self.concept_layer.get(c),
                    "top_roots": [
                        {"root_id": x["root_id"], "root_arabic": x["root_arabic"],
                         "activation_weight": x["activation_weight"]}
                        for x in self.dom_roots[c]["roots"][:5]],
                })
            scc_struct.append({
                "size": comp["size"],
                "internal_edges": comp["internal_edges"],
                "edge_density": comp["edge_density"],
                "concepts": comp["concepts"],
                "members": members,
            })

        return {
            "method": METHOD,
            "note": ("Evidence-only deep profiles. No meaning, label, translation, or "
                     "interpretation is assigned to any concept, root, lemma, surah, or "
                     "structure. Targets selected purely by Phase-5 foundationality rank and "
                     "Phase-5 dominant-/secondary-core identity."),
            "focus_concepts": focus,
            "top_foundational_concepts": top20,
            "dominant_core": {
                "dominant_hub": self.comp_stats["dominant_core"]["dominant_hub"],
                "hub_proposition_retention": self.comp_stats["dominant_core"]["hub_proposition_retention"],
                "secondary_core_concept": self.hub_removal["emergent_core"]["new_top_betweenness_concept"],
            },
            "deep_profiles": deep,
            "largest_scc_structures": scc_struct,
        }

    # ── manifest ────────────────────────────────────────────────────────────────

    def manifest(self, output_bytes):
        inputs = [
            ("monad.db", self.db_path),
            ("semantic_neighbors.json", self.lex_dir / "semantic_neighbors.json"),
            ("concept_candidates.json", self.concepts_dir / "concept_candidates.json"),
            ("concept_centers.json", self.concepts_dir / "concept_centers.json"),
            ("concept_graph.json", self.concepts_dir / "concept_graph.json"),
            ("concept_memberships.json", self.concepts_dir / "concept_memberships.json"),
            ("concept_relationships.json", self.concepts_dir / "concept_relationships.json"),
            ("concept_statistics.json", self.concepts_dir / "concept_statistics.json"),
            ("proposition_candidates.json", self.props_dir / "proposition_candidates.json"),
            ("proposition_graph.json", self.props_dir / "proposition_graph.json"),
            ("dependency_candidates.json", self.props_dir / "dependency_candidates.json"),
            ("foundationality_scores.json", self.comp_dir / "foundationality_scores.json"),
            ("dependency_layers.json", self.comp_dir / "dependency_layers.json"),
            ("irreducible_structures.json", self.comp_dir / "irreducible_structures.json"),
            ("reconstruction_sets.json", self.comp_dir / "reconstruction_sets.json"),
            ("hub_removal_analysis.json", self.comp_dir / "hub_removal_analysis.json"),
            ("compression_statistics.json", self.comp_dir / "compression_statistics.json"),
        ]
        return {
            "method": METHOD,
            "constants": {
                "AYAH_TOPS": AYAH_TOPS,
                "ATLAS_TOP": ATLAS_TOP,
                "PROP_TOP": PROP_TOP,
                "SURAH_TOP": SURAH_TOP,
                "CORE_AYAH_TOP": CORE_AYAH_TOP,
                "CORE_ENTITY_TOP": CORE_ENTITY_TOP,
                "TOP_FOUNDATIONAL": TOP_FOUNDATIONAL,
                "ROUND": ROUND,
            },
            "input_sha256": {name: sha256_file(p) for name, p in inputs},
            "output_bytes": output_bytes,
            "prohibitions_observed": PROHIBITIONS,
            "totals": {
                "concept_count": self.n_concepts,
                "active_concepts": sum(1 for c in self.activation_count.values() if c),
                "total_ayahs": self.n_ayahs,
                "active_ayahs": len({seq for cid in self.activation
                                     for seq, *_ in self.activation[cid]}),
            },
        }

    # ── orchestration ───────────────────────────────────────────────────────────

    def run(self):
        self.load()
        self.activate()
        products = {}
        products["dominant_roots.json"] = self.dominant_roots()
        products["dominant_lemmas.json"] = self.dominant_lemmas()
        products["ayah_signatures.json"] = self.ayah_signatures()
        products["surah_signatures.json"] = self.surah_signatures()
        products["concept_atlas.json"] = self.concept_atlas()
        products["concept_profiles.json"] = self.concept_profiles()
        products["core_investigation.json"] = self.core_investigation()

        output_bytes = {}
        for name, obj in products.items():
            output_bytes[name] = write_json(self.out_dir / name, obj)
            print(f"    wrote {name} ({output_bytes[name]} bytes)")

        man = self.manifest(output_bytes)
        man_name = "identification_manifest.json"
        output_bytes[man_name] = write_json(self.out_dir / man_name, man)
        print(f"    wrote {man_name} ({output_bytes[man_name]} bytes)")
        return man


def main():
    ap = argparse.ArgumentParser(description="Monad Phase 6 — Concept Identification Engine")
    ap.add_argument("--db", default="generated/monad.db")
    ap.add_argument("--lexicon", default="generated/lexicon")
    ap.add_argument("--concepts", default="generated/concepts")
    ap.add_argument("--propositions", default="generated/propositions")
    ap.add_argument("--compression", default="generated/compression")
    ap.add_argument("--out", default="generated/identification")
    args = ap.parse_args()

    print(f"Monad Phase 6 — Concept Identification Engine ({METHOD})")
    eng = IdentificationEngine(args.db, args.lexicon, args.concepts,
                               args.propositions, args.compression, args.out)
    man = eng.run()
    print("  done.")
    print(f"  totals: {json.dumps(man['totals'])}")


if __name__ == "__main__":
    main()
