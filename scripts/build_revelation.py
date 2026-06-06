#!/usr/bin/env python3
"""
Monad — Phase 7: Semantic Revelation Engine
===========================================

Purpose
-------
Allow the Quran to reveal the *identity* of each discovered concept using
Quran-internal evidence ONLY. This is the first phase permitted to investigate
identity — but identity here is never an imported meaning. A concept's identity
and its candidate "names" are expressed strictly as the concept's own dominant
**Arabic** roots and lemmas and the ayah / structural patterns they form. No
token is ever translated, glossed, or interpreted.

Governing rule
--------------
Identity must emerge only from: roots · lemmas · ayahs · surahs · neighbours ·
dependencies · proposition structures. Never import meaning. Only reveal
patterns already present. A "candidate name" is a literal Quran-internal Arabic
lemma/root drawn from the concept's members — it points at the dominant lexical
anchor, it does not explain it. Competing identities are preserved; no single
identity is forced; no certainty, divine origin, or human origin is claimed.

Inputs (read-only)
------------------
    generated/monad.db                                   (Phase 1: POS, lemma→root)
    generated/lexicon/semantic_neighbors.json            (Phase 2)
    generated/concepts/concept_memberships.json          (Phase 3: multi-membership)
    generated/identification/*.json                      (Phase 6: all 7 products)

Outputs
-------
    generated/revelation/
        concept_dossiers.json          (A)
        semantic_fields.json           (B)
        ayah_identity_profiles.json    (C)
        root_consistency.json          (D)
        candidate_names.json           (E)
        core_revelation.json           (F)
        identity_confidence.json       (aggregate)
        falsification_results.json     (G)
        revelation_manifest.json

Method
------
Deterministic, pure-stdlib, byte-identically reproducible. Co-occurrence is taken
over each concept's top-100 signature ayahs (Phase-6 evidence). POS classes are
Phase-1 morphology annotation (structural, not semantic). All "identity" numbers
are concentration / entropy / graph quantities over Arabic surface forms.
"""

import argparse
import hashlib
import json
import math
import sqlite3
from collections import defaultdict, Counter
from itertools import combinations
from pathlib import Path

METHOD = "phase7-revelation-1.0"
ROUND = 6

# field discovery
FIELD_COOCCUR_MIN = 3      # min signature ayahs two member roots co-fire to link them
FIELD_NEIGHBOR_MIN = 0.05  # min Phase-2 semantic-neighbour confidence to link roots
# naming (root-anchored: roots are the stable identity unit in this corpus)
NAME_MIN_CONF = 0.15       # min root activation_share to emit a candidate name
NAME_MAX = 5               # max candidate names per concept
# coherence tiers (root activation_share Herfindahl index, HHI)
HHI_COHERENT = 0.40
HHI_DOMINANT = 0.20
# evidence graph / signature depth
SIG_DEPTH = 100
EG_ROOTS = 8
EG_CONCEPTS = 6
EG_AYAHS = 6
# falsification
NEIGHBOR_LINK_MIN = 0.05   # semantic-neighbour confidence considered a real link

NOMINAL_POS = {"N", "PN", "ADJ"}
VERBAL_POS = {"V"}

PROHIBITIONS = [
    "no tafsir",
    "no translations",
    "no dictionaries",
    "no theology",
    "no external sources",
    "no pretrained embeddings",
    "no human labels",
    "no imported interpretation",
    "no certainty claimed",
    "no divine origin claimed",
    "no human origin claimed",
    "no doctrine",
    "no apologetics",
    "no single identity forced",
    "competing identities preserved",
    "names are Quran-internal Arabic tokens only",
    "concepts remain opaque unless evidence reveals them",
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


def entropy(weights):
    """Shannon entropy (bits) of a weight vector, normalised to [0,1] by log2(n)."""
    tot = sum(weights)
    if tot <= 0 or len(weights) <= 1:
        return 0.0
    ps = [w / tot for w in weights if w > 0]
    h = -sum(p * math.log2(p) for p in ps)
    return h / math.log2(len(weights))


class RevelationEngine:
    def __init__(self, db, lex, concepts, ident, out):
        self.db = Path(db)
        self.lex = Path(lex)
        self.concepts_dir = Path(concepts)
        self.ident_dir = Path(ident)
        self.out_dir = Path(out)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    # ── load ────────────────────────────────────────────────────────────────────

    def load(self):
        print("  loading Phase-6 identification products …")
        self.profiles = json.loads((self.ident_dir / "concept_profiles.json").read_text("utf-8"))["concepts"]
        self.dom_roots = json.loads((self.ident_dir / "dominant_roots.json").read_text("utf-8"))["concepts"]
        self.dom_lemmas = json.loads((self.ident_dir / "dominant_lemmas.json").read_text("utf-8"))["concepts"]
        self.ayah_sig = json.loads((self.ident_dir / "ayah_signatures.json").read_text("utf-8"))["concepts"]
        self.surah_sig = json.loads((self.ident_dir / "surah_signatures.json").read_text("utf-8"))["concepts"]
        self.atlas = json.loads((self.ident_dir / "concept_atlas.json").read_text("utf-8"))["concepts"]
        self.core_inv = json.loads((self.ident_dir / "core_investigation.json").read_text("utf-8"))

        self.concept_ids = sorted(self.profiles.keys())
        self.n_concepts = len(self.concept_ids)

        print("  loading Phase-2 semantic-neighbour adjacency …")
        sn = json.loads((self.lex / "semantic_neighbors.json").read_text("utf-8"))
        self.root_adj = {int(rid): {n["root_id"]: n["confidence"] for n in v["neighbors"]}
                         for rid, v in sn["roots"].items()}

        print("  loading Phase-3 multi-membership …")
        mem = json.loads((self.concepts_dir / "concept_memberships.json").read_text("utf-8"))
        self.root_membership_count = {int(rid): len(v) for rid, v in mem["root_memberships"].items()}

        print("  loading Phase-1 lemma→root and POS …")
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        self.lemma_root = {lid: rid for lid, rid in
                           cur.execute("SELECT lemma_id, root_id FROM lemmas")}
        self.root_ar = {rid: ar for rid, ar in cur.execute("SELECT root_id, root_arabic FROM roots")}
        # POS index: (surah,ayah) -> list of (root_id, pos)
        self.ayah_pos = defaultdict(list)
        for s, a, rid, pos in cur.execute(
                "SELECT surah_number, ayah_number, root_id, pos FROM morphology "
                "WHERE root_id IS NOT NULL"):
            self.ayah_pos[(s, a)].append((rid, pos))
        conn.close()

        # concept -> dominant top root id + arabic (rank 1)
        self.top_root = {}
        for cid in self.concept_ids:
            roots = self.dom_roots[cid]["roots"]
            self.top_root[cid] = roots[0] if roots else None
        print(f"    concepts={self.n_concepts}")

    # ── helpers over signature ayahs ────────────────────────────────────────────

    def _sig_entries(self, cid, depth=SIG_DEPTH):
        return self.ayah_sig[cid].get(f"top_{depth}", self.ayah_sig[cid].get("top_25", []))

    def _root_cooccurrence(self, cid):
        """Counts over the concept's signature ayahs: per member root #ayahs it
        fires in, and per unordered pair #ayahs both fire in."""
        single = Counter()
        pair = Counter()
        cover = defaultdict(set)   # root -> set of ayah indices it fires in
        for i, e in enumerate(self._sig_entries(cid)):
            rs = sorted(x["root_id"] for x in e["contributing_roots"])
            for rid in rs:
                single[rid] += 1
                cover[rid].add(i)
            for a, b in combinations(rs, 2):
                pair[(a, b)] += 1
        return single, pair, cover

    # ── PHASE A: concept dossiers ───────────────────────────────────────────────

    def concept_dossiers(self):
        print("  PHASE A — concept dossiers …")
        out = {}
        for cid in self.concept_ids:
            p = self.profiles[cid]
            a = self.atlas[cid]
            out[cid] = {
                "concept_id": cid,
                "roots": [{"root_id": x["root_id"], "root_arabic": x["root_arabic"],
                           "activation_weight": x["activation_weight"],
                           "activation_share": x["activation_share"],
                           "membership_confidence": x["membership_confidence"]}
                          for x in self.dom_roots[cid]["roots"]],
                "lemmas": [{"lemma_id": x["lemma_id"], "lemma_arabic": x["lemma_arabic"],
                            "activation_weight": x["activation_weight"],
                            "activation_share": x["activation_share"]}
                           for x in self.dom_lemmas[cid]["lemmas"][:30]],
                "signature_ayahs": [{"surah": e["surah"], "ayah": e["ayah"],
                                     "activation_strength": e["activation_strength"],
                                     "confidence": e["confidence"]}
                                    for e in self._sig_entries(cid, 25)],
                "signature_surahs": self.surah_sig[cid]["highest_activation_surahs"][:5],
                "uniqueness_surahs": self.surah_sig[cid]["highest_uniqueness_surahs"][:5],
                "closest_concepts": a["closest_concepts"],
                "dependency_roles": {
                    "dependency_layer": a["dependency_layer"],
                    "scc_component_index": a["scc_component_index"],
                    "is_proposition_bridge": a["is_proposition_bridge"],
                    "strongest_dependencies_out": a["strongest_dependencies_out"][:5],
                    "strongest_dependencies_in": a["strongest_dependencies_in"][:5],
                    "strongest_cycles": a["strongest_cycles"],
                },
                "graph_metrics": p["centrality_metrics"],
                "activation_profile": {
                    "activation_count": p["activation_count"],
                    "activation_strength_total": p["activation_strength_total"],
                    "activation_strength_max": p["activation_strength_max"],
                    "activation_strength_mean": p["activation_strength_mean"],
                    "ayah_distribution": p["ayah_distribution"],
                },
                "compression_profile": p["compression_metrics"],
                "internal_structure": p["internal_structure"],
                "phase3_classifications": p["phase3_classifications"],
            }
        self.dossiers = out
        return {"method": METHOD, "n_concepts": self.n_concepts,
                "note": "Consolidated Phase-6 evidence per concept. No meaning assigned.",
                "concepts": out}

    # ── PHASE B: semantic field discovery ───────────────────────────────────────

    def semantic_fields(self):
        print("  PHASE B — semantic field discovery …")
        out = {}
        for cid in self.concept_ids:
            roots = [x["root_id"] for x in self.dom_roots[cid]["roots"]]
            rset = set(roots)
            weight = {x["root_id"]: x["activation_weight"] for x in self.dom_roots[cid]["roots"]}
            single, pair, cover = self._root_cooccurrence(cid)

            # adjacency: link member roots by co-occurrence OR semantic-neighbour
            adj = defaultdict(set)
            edge_strength = {}
            for a, b in combinations(sorted(rset), 2):
                co = pair.get((a, b), 0)
                nb = max(self.root_adj.get(a, {}).get(b, 0.0),
                         self.root_adj.get(b, {}).get(a, 0.0))
                if co >= FIELD_COOCCUR_MIN or nb >= FIELD_NEIGHBOR_MIN:
                    adj[a].add(b)
                    adj[b].add(a)
                    edge_strength[(a, b)] = {"cooccurrence_ayahs": co, "neighbour_confidence": r(nb)}

            # connected components → fields
            seen = set()
            fields = []
            for rid in roots:
                if rid in seen:
                    continue
                # BFS
                comp = []
                stack = [rid]
                seen.add(rid)
                while stack:
                    u = stack.pop()
                    comp.append(u)
                    for v in sorted(adj[u]):
                        if v not in seen:
                            seen.add(v)
                            stack.append(v)
                comp.sort(key=lambda x: (-weight.get(x, 0.0), x))
                # field cohesion = mean strength of internal edges present
                internal = [e for (x, y), e in edge_strength.items() if x in comp and y in comp]
                cohesion = (sum(max(e["cooccurrence_ayahs"] / max(1, len(self._sig_entries(cid))),
                                    e["neighbour_confidence"]) for e in internal) / len(internal)
                            if internal else 0.0)
                # support = signature ayahs covering any field root
                covered = set()
                for x in comp:
                    covered |= cover.get(x, set())
                anchor = comp[0]
                fields.append({
                    "anchor_root_id": anchor,
                    "anchor_root_arabic": self.root_ar.get(anchor, ""),
                    "size": len(comp),
                    "member_roots": [{"root_id": x, "root_arabic": self.root_ar.get(x, "")}
                                     for x in comp],
                    "internal_edges": len(internal),
                    "cohesion": r(cohesion),
                    "support_ayahs": len(covered),
                    "confidence": r(min(1.0, cohesion)),
                    "evidence_ayahs": [
                        {"surah": self._sig_entries(cid)[i]["surah"],
                         "ayah": self._sig_entries(cid)[i]["ayah"]}
                        for i in sorted(covered)[:5]],
                })
            fields.sort(key=lambda f: (-f["size"], -f["support_ayahs"], f["anchor_root_id"]))

            # lexical fields: member lemmas grouped by their root (Quran-internal family)
            lemma_fams = defaultdict(list)
            for x in self.dom_lemmas[cid]["lemmas"]:
                root = self.lemma_root.get(x["lemma_id"])
                lemma_fams[root].append(x)
            lexical = []
            for root, lems in lemma_fams.items():
                lems.sort(key=lambda d: -d["activation_weight"])
                lexical.append({
                    "root_id": root,
                    "root_arabic": self.root_ar.get(root, "") if root is not None else "",
                    "lemma_count": len(lems),
                    "lemmas": [{"lemma_id": l["lemma_id"], "lemma_arabic": l["lemma_arabic"]}
                               for l in lems[:8]],
                    "activation_weight": r(sum(l["activation_weight"] for l in lems)),
                })
            lexical.sort(key=lambda d: (-d["activation_weight"], -d["lemma_count"],
                                        d["root_id"] if d["root_id"] is not None else -1))

            out[cid] = {
                "n_semantic_fields": len(fields),
                "semantic_fields": fields,
                "n_lexical_families": len(lexical),
                "lexical_families": lexical[:15],
            }
        self.fields = out
        return {"method": METHOD,
                "definition": ("semantic_fields = connected groups of member roots linked by "
                               "intra-concept signature-ayah co-occurrence or Phase-2 semantic-"
                               "neighbour confidence; lexical_families = member lemmas grouped by "
                               "their shared root. Anchors and members are raw Arabic forms; no "
                               "meaning is assigned."),
                "constants": {"FIELD_COOCCUR_MIN": FIELD_COOCCUR_MIN,
                              "FIELD_NEIGHBOR_MIN": FIELD_NEIGHBOR_MIN},
                "concepts": out}

    # ── PHASE C: ayah-driven identification ─────────────────────────────────────

    def ayah_identity_profiles(self):
        print("  PHASE C — ayah-driven identification …")
        out = {}
        for cid in self.concept_ids:
            mset = {x["root_id"] for x in self.dom_roots[cid]["roots"]}
            entry = {}
            for depth in (25, 50, 100):
                ents = self._sig_entries(cid, depth)
                n = len(ents)
                theme = Counter()          # member root -> #signature ayahs present
                nominal = Counter()        # member root -> #(nominal occurrences) in sig ayahs
                verbal = Counter()
                lemma_theme = Counter()
                for e in ents:
                    present = set()
                    for x in e["contributing_roots"]:
                        theme[x["root_id"]] += 1
                        present.add(x["root_id"])
                    for x in e["contributing_lemmas"]:
                        lemma_theme[x["lemma_id"]] += 1
                    # POS of member roots firing in this ayah
                    for rid, pos in self.ayah_pos.get((e["surah"], e["ayah"]), ()):
                        if rid in mset and rid in present:
                            if pos in NOMINAL_POS:
                                nominal[rid] += 1
                            elif pos in VERBAL_POS:
                                verbal[rid] += 1

                def top(counter, k=8):
                    items = sorted(counter.items(), key=lambda t: (-t[1], t[0]))[:k]
                    return [{"root_id": rid, "root_arabic": self.root_ar.get(rid, ""),
                             "signature_ayahs": c} for rid, c in items]

                def topl(counter, k=8):
                    items = sorted(counter.items(), key=lambda t: (-t[1], t[0]))[:k]
                    lam = {x["lemma_id"]: x["lemma_arabic"] for x in self.dom_lemmas[cid]["lemmas"]}
                    return [{"lemma_id": lid, "lemma_arabic": lam.get(lid, ""),
                             "signature_ayahs": c} for lid, c in items]

                # structurally-subsequent fields: dominant roots of concepts this concept PRECEDES/PREDICTS
                subsequent = []
                for rec in self.atlas[cid].get("proposition_top_out_partners", [])[:5]:
                    pc = rec["concept_id"]
                    tr = self.top_root.get(pc)
                    if tr:
                        subsequent.append({"concept_id": pc,
                                           "anchor_root_arabic": tr["root_arabic"],
                                           "weight": rec["weight"]})

                entry[f"top_{depth}"] = {
                    "n_ayahs": n,
                    "recurring_themes_roots": top(theme),
                    "recurring_themes_lemmas": topl(lemma_theme),
                    "recurring_actors_nominal": top(nominal),
                    "recurring_actions_verbal": top(verbal),
                    "recurring_outcomes_structural": subsequent,
                }
            out[cid] = entry
        self.ayah_profiles = out
        return {"method": METHOD,
                "definition": ("Over each depth of signature ayahs: recurring_themes = member "
                               "roots/lemmas by signature-ayah frequency; recurring_actors = "
                               "member roots firing under nominal POS (N/PN/ADJ); "
                               "recurring_actions = member roots firing under verbal POS (V); "
                               "recurring_outcomes_structural = anchor roots of concepts this "
                               "concept structurally precedes/predicts. POS is Phase-1 morphology; "
                               "no meaning assigned."),
                "concepts": out}

    # ── PHASE D: root consistency analysis ──────────────────────────────────────

    def root_consistency(self):
        print("  PHASE D — root consistency analysis …")
        out = {}
        for cid in self.concept_ids:
            roots = self.dom_roots[cid]["roots"]
            shares = [x["activation_share"] for x in roots]
            ids = [x["root_id"] for x in roots]
            hhi = sum(s * s for s in shares)
            ent = entropy([x["activation_weight"] for x in roots])
            # semantic agreement among top-5 roots: mean pairwise neighbour confidence
            top5 = ids[:5]
            pairs = list(combinations(top5, 2))
            if pairs:
                agree = sum(max(self.root_adj.get(a, {}).get(b, 0.0),
                                self.root_adj.get(b, {}).get(a, 0.0)) for a, b in pairs) / len(pairs)
            else:
                agree = 0.0
            n_fields = self.fields[cid]["n_semantic_fields"]
            largest_field = self.fields[cid]["semantic_fields"][0]["size"] if n_fields else 0
            frag = 1.0 - (largest_field / len(ids)) if ids else 0.0
            # multi-membership ambiguity: share of member roots that belong to >1 concept
            shared = sum(1 for rid in ids if self.root_membership_count.get(rid, 1) > 1)
            multi_ratio = shared / len(ids) if ids else 0.0

            if hhi >= HHI_COHERENT:
                verdict = "coherent_single"
            elif hhi >= HHI_DOMINANT:
                verdict = "coherent_dominant"
            elif n_fields <= 2:
                verdict = "diffuse_unified"
            else:
                verdict = "fragmented"

            out[cid] = {
                "root_count": len(ids),
                "identity_coherence_hhi": r(hhi),
                "top_root_share": r(shares[0]) if shares else 0.0,
                "semantic_agreement_top5": r(agree),
                "identity_fragmentation": r(frag),
                "n_semantic_fields": n_fields,
                "largest_field_size": largest_field,
                "identity_ambiguity_entropy": r(ent),
                "multi_membership_ratio": r(multi_ratio),
                "verdict": verdict,
            }
        self.consistency = out
        return {"method": METHOD,
                "definition": ("identity_coherence_hhi = Herfindahl index of root activation "
                               "shares (high=one root dominates); semantic_agreement_top5 = mean "
                               "pairwise Phase-2 neighbour confidence among top-5 roots; "
                               "fragmentation = 1 - largest_field/root_count; ambiguity = "
                               "normalised entropy of root weights; multi_membership_ratio = "
                               "fraction of member roots shared with other concepts."),
                "constants": {"HHI_COHERENT": HHI_COHERENT, "HHI_DOMINANT": HHI_DOMINANT},
                "concepts": out}

    # ── PHASE E: candidate naming experiment ────────────────────────────────────

    def _representative_lemma(self, cid, root_id):
        """Highest-activation member lemma whose root is root_id (the surface form
        of a root-anchored name); falls back to the root's Arabic if none."""
        best = None
        for lem in self.dom_lemmas[cid]["lemmas"]:
            if self.lemma_root.get(lem["lemma_id"]) == root_id:
                if best is None or lem["activation_weight"] > best["activation_weight"]:
                    best = lem
        return best

    def candidate_names(self):
        print("  PHASE E — candidate naming experiment …")
        out = {}
        for cid in self.concept_ids:
            roots = self.dom_roots[cid]["roots"]
            top_share = roots[0]["activation_share"] if roots else 0.0
            candidates = []
            for root in roots:
                if root["activation_share"] < NAME_MIN_CONF:
                    continue
                if len(candidates) >= NAME_MAX:
                    break
                rid = root["root_id"]
                rep = self._representative_lemma(cid, rid)
                name = rep["lemma_arabic"] if rep else root["root_arabic"]
                # supporting ayahs: signature ayahs where this root fires
                supp_ayahs = []
                for e in self._sig_entries(cid, 50):
                    if any(x["root_id"] == rid for x in e["contributing_roots"]):
                        supp_ayahs.append({"surah": e["surah"], "ayah": e["ayah"]})
                    if len(supp_ayahs) >= 5:
                        break
                # supporting neighbours: closest concepts that also contain this root
                supp_neighbors = []
                for rc in self.atlas[cid]["closest_concepts"]:
                    nc = rc["concept_id"]
                    if any(rr["root_id"] == rid for rr in self.dom_roots[nc]["roots"]):
                        supp_neighbors.append({"concept_id": nc, "weight": rc["weight"]})
                    if len(supp_neighbors) >= 5:
                        break
                candidates.append({
                    "name_arabic": name,
                    "name_type": "root-anchored-lemma" if rep else "root",
                    "anchor_root_id": rid,
                    "anchor_root_arabic": root["root_arabic"],
                    "representative_lemma_id": rep["lemma_id"] if rep else None,
                    "confidence": r(root["activation_share"]),
                    "relative_dominance": r(root["activation_share"] / top_share) if top_share else 0.0,
                    "supporting_roots": [{"root_id": x["root_id"], "root_arabic": x["root_arabic"]}
                                         for x in roots[:3]],
                    "supporting_ayahs": supp_ayahs,
                    "supporting_propositions": self.atlas[cid]["strongest_propositions"][:3],
                    "supporting_neighbors": supp_neighbors,
                })
            competition = (len(candidates) >= 2 and
                           candidates[1]["confidence"] >= 0.6 * candidates[0]["confidence"])
            out[cid] = {
                "n_candidates": len(candidates),
                "resists_identification": len(candidates) == 0,
                "competing_names": competition,
                "candidates": candidates,
            }
        self.names = out
        return {"method": METHOD,
                "definition": ("Candidate names are root-anchored: each is the dominant Arabic "
                               "member lemma of a top member root (its surface form), drawn from "
                               "the concept's own members and ranked by root activation share. "
                               "They point at the dominant lexical anchor; no translation or "
                               "meaning is attached. 0 names = resists identification (no root "
                               "reaches the dominance floor). Competing names are preserved; none "
                               "is privileged."),
                "constants": {"NAME_MIN_CONF": NAME_MIN_CONF, "NAME_MAX": NAME_MAX},
                "concepts": out}

    # ── PHASE G: falsification ──────────────────────────────────────────────────

    def falsification(self):
        print("  PHASE G — falsification / consistency test …")
        out = {}
        for cid in self.concept_ids:
            cands = self.names[cid]["candidates"]
            if not cands:
                out[cid] = {"tested": False, "reason": "resists_identification — no identity to falsify"}
                continue
            top = cands[0]
            R = top["anchor_root_id"]
            roots = self.dom_roots[cid]["roots"]
            rset = {x["root_id"] for x in roots}

            # contradicting roots: notable member roots with ~0 neighbour link to R
            contra_roots = []
            for x in roots[1:]:
                rid = x["root_id"]
                link = max(self.root_adj.get(R, {}).get(rid, 0.0),
                           self.root_adj.get(rid, {}).get(R, 0.0)) if R is not None else 0.0
                if link < NEIGHBOR_LINK_MIN and x["activation_share"] >= 0.05:
                    contra_roots.append({"root_id": rid, "root_arabic": x["root_arabic"],
                                         "activation_share": x["activation_share"],
                                         "neighbour_link_to_anchor": r(link)})
            contra_roots.sort(key=lambda d: -d["activation_share"])

            # contradicting ayahs: signature ayahs where anchor root R does NOT fire
            sig = self._sig_entries(cid, 50)
            absent = [e for e in sig if R is not None and
                      not any(x["root_id"] == R for x in e["contributing_roots"])]
            ayah_pressure = len(absent) / len(sig) if sig else 0.0

            # contradicting neighbours: closest concepts whose top root has ~0 link to R
            contra_nb = []
            for rc in self.atlas[cid]["closest_concepts"][:8]:
                nc = rc["concept_id"]
                tr = self.top_root.get(nc)
                if not tr:
                    continue
                link = max(self.root_adj.get(R, {}).get(tr["root_id"], 0.0),
                           self.root_adj.get(tr["root_id"], {}).get(R, 0.0)) if R is not None else 0.0
                if link < NEIGHBOR_LINK_MIN:
                    contra_nb.append({"concept_id": nc, "anchor_root_arabic": tr["root_arabic"],
                                      "weight": rc["weight"], "neighbour_link_to_anchor": r(link)})

            # contradicting propositions: dependency partners with anchor root unlinked to R
            contra_props = []
            for rec in (self.atlas[cid]["strongest_dependencies_out"] +
                        self.atlas[cid]["strongest_dependencies_in"]):
                pc = rec["partner"]
                tr = self.top_root.get(pc)
                if not tr:
                    continue
                link = max(self.root_adj.get(R, {}).get(tr["root_id"], 0.0),
                           self.root_adj.get(tr["root_id"], {}).get(R, 0.0)) if R is not None else 0.0
                if link < NEIGHBOR_LINK_MIN:
                    contra_props.append({"relation_type": rec["relation_type"], "partner": pc,
                                         "anchor_root_arabic": tr["root_arabic"]})

            root_pressure = (len(contra_roots) / max(1, len(roots) - 1))
            falsification_pressure = r(0.5 * ayah_pressure + 0.5 * root_pressure)
            survives = falsification_pressure < 0.5

            out[cid] = {
                "tested": True,
                "proposed_identity": {"name_arabic": top["name_arabic"],
                                      "anchor_root_arabic": top["anchor_root_arabic"],
                                      "confidence": top["confidence"]},
                "contradicting_roots": contra_roots[:8],
                "contradicting_ayah_fraction": r(ayah_pressure),
                "contradicting_ayahs_sample": [{"surah": e["surah"], "ayah": e["ayah"]}
                                               for e in absent[:5]],
                "contradicting_neighbors": contra_nb[:6],
                "contradicting_propositions": contra_props[:6],
                "falsification_pressure": falsification_pressure,
                "survives": survives,
            }
        self.falsify = out
        return {"method": METHOD,
                "definition": ("For each concept's top candidate identity (anchor root R), search "
                               "for contradicting evidence: member roots not neighbour-linked to R, "
                               "signature ayahs where R does not fire, closest concepts and "
                               "dependency partners whose anchor root is unlinked to R. "
                               "falsification_pressure = mean(ayah_absence_fraction, "
                               "contradicting_root_fraction); survives iff < 0.5. The identity is "
                               "attacked, not defended."),
                "constants": {"NEIGHBOR_LINK_MIN": NEIGHBOR_LINK_MIN},
                "concepts": out}

    # ── identity confidence (aggregate) ─────────────────────────────────────────

    def identity_confidence(self):
        print("  aggregate — identity confidence …")
        out = {}
        tiers = Counter()
        for cid in self.concept_ids:
            cons = self.consistency[cid]
            nm = self.names[cid]
            fal = self.falsify[cid]
            if nm["n_candidates"] == 0:
                tier = "resists"
                overall = 0.0
                top = None
                survives = None
            else:
                top = nm["candidates"][0]
                survives = fal.get("survives", False)
                pressure = fal.get("falsification_pressure", 1.0)
                # overall = mean of (name confidence, coherence, 1-ambiguity, 1-pressure)
                overall = r((top["confidence"] + cons["identity_coherence_hhi"] +
                             (1 - cons["identity_ambiguity_entropy"]) + (1 - pressure)) / 4.0)
                if top["confidence"] >= 0.30 and cons["identity_coherence_hhi"] >= 0.30 and survives:
                    tier = "strong"
                elif top["confidence"] >= 0.15 and survives:
                    tier = "moderate"
                else:
                    tier = "weak"
            tiers[tier] += 1
            out[cid] = {
                "tier": tier,
                "overall_identity_confidence": overall,
                "top_candidate_name": top["name_arabic"] if top else None,
                "anchor_root_arabic": top["anchor_root_arabic"] if top else None,
                "name_confidence": top["confidence"] if top else 0.0,
                "identity_coherence_hhi": cons["identity_coherence_hhi"],
                "identity_ambiguity_entropy": cons["identity_ambiguity_entropy"],
                "consistency_verdict": cons["verdict"],
                "competing_names": nm["competing_names"],
                "falsification_survives": survives,
                "falsification_pressure": fal.get("falsification_pressure"),
            }
        self.confidence = out
        self.tier_counts = dict(tiers)
        return {"method": METHOD,
                "definition": ("overall_identity_confidence = mean(name_confidence, coherence_hhi, "
                               "1-ambiguity_entropy, 1-falsification_pressure). Tiers: strong / "
                               "moderate / weak / resists. No certainty is claimed."),
                "tier_counts": dict(tiers),
                "concepts": out}

    # ── PHASE F: core revelation ────────────────────────────────────────────────

    def _evidence_graph(self, cid):
        roots = self.dom_roots[cid]["roots"][:EG_ROOTS]
        rids = [x["root_id"] for x in roots]
        nodes = []
        for x in roots:
            nodes.append({"id": f"root:{x['root_id']}", "type": "root",
                          "label": x["root_arabic"], "weight": x["activation_weight"]})
        for rc in self.atlas[cid]["closest_concepts"][:EG_CONCEPTS]:
            nodes.append({"id": rc["concept_id"], "type": "concept",
                          "label": rc["concept_id"], "weight": rc["weight"]})
        for e in self._sig_entries(cid, EG_AYAHS):
            nodes.append({"id": f"ayah:{e['surah']}:{e['ayah']}", "type": "ayah",
                          "label": f"{e['surah']}:{e['ayah']}", "weight": e["activation_strength"]})
        edges = []
        # root-root semantic neighbour links
        for a, b in combinations(rids, 2):
            nb = max(self.root_adj.get(a, {}).get(b, 0.0), self.root_adj.get(b, {}).get(a, 0.0))
            if nb >= FIELD_NEIGHBOR_MIN:
                edges.append({"src": f"root:{a}", "tgt": f"root:{b}",
                              "type": "neighbour", "weight": r(nb)})
        # root-in-ayah fires
        for e in self._sig_entries(cid, EG_AYAHS):
            fired = {x["root_id"] for x in e["contributing_roots"]}
            for rid in rids:
                if rid in fired:
                    edges.append({"src": f"root:{rid}", "tgt": f"ayah:{e['surah']}:{e['ayah']}",
                                  "type": "fires", "weight": 1})
        return {"nodes": nodes, "edges": edges}

    def core_revelation(self):
        print("  PHASE F — core revelation …")
        focus = ["CONCEPT_007", "CONCEPT_016", "CONCEPT_081"]
        scc9 = self.core_inv["largest_scc_structures"][0]["concepts"]
        top_found = self.core_inv["top_foundational_concepts"]
        targets = []
        for c in focus + scc9 + top_found:
            if c not in targets:
                targets.append(c)

        deep = {}
        for cid in targets:
            cons = self.consistency[cid]
            nm = self.names[cid]
            fal = self.falsify[cid]
            hyps = []
            for c in nm["candidates"]:
                hyps.append({"identity_anchor_arabic": c["name_arabic"],
                             "anchor_root_arabic": c["anchor_root_arabic"],
                             "confidence": c["confidence"],
                             "relative_dominance": c["relative_dominance"]})
            deep[cid] = {
                "concept_id": cid,
                "identity_hypotheses": hyps[:3],
                "competing_hypotheses": hyps[1:3],
                "primary_confidence": hyps[0]["confidence"] if hyps else 0.0,
                "ambiguity_score": cons["identity_ambiguity_entropy"],
                "coherence_hhi": cons["identity_coherence_hhi"],
                "consistency_verdict": cons["verdict"],
                "falsification": {"survives": fal.get("survives"),
                                  "pressure": fal.get("falsification_pressure")},
                "semantic_fields": self.fields[cid]["semantic_fields"][:4],
                "evidence_graph": self._evidence_graph(cid),
            }
        return {"method": METHOD,
                "note": ("Deep evidence-only identity investigation. Hypotheses are dominant "
                         "Arabic anchors; competing hypotheses are preserved; confidence is "
                         "concentration-based; ambiguity is entropy-based. No meaning, certainty, "
                         "or origin is claimed."),
                "focus_concepts": focus,
                "largest_scc_members": scc9,
                "top_foundational_concepts": top_found,
                "deep_revelation": deep}

    # ── manifest ────────────────────────────────────────────────────────────────

    def manifest(self, output_bytes):
        inputs = [
            ("monad.db", self.db),
            ("semantic_neighbors.json", self.lex / "semantic_neighbors.json"),
            ("concept_memberships.json", self.concepts_dir / "concept_memberships.json"),
            ("concept_profiles.json", self.ident_dir / "concept_profiles.json"),
            ("dominant_roots.json", self.ident_dir / "dominant_roots.json"),
            ("dominant_lemmas.json", self.ident_dir / "dominant_lemmas.json"),
            ("ayah_signatures.json", self.ident_dir / "ayah_signatures.json"),
            ("surah_signatures.json", self.ident_dir / "surah_signatures.json"),
            ("concept_atlas.json", self.ident_dir / "concept_atlas.json"),
            ("core_investigation.json", self.ident_dir / "core_investigation.json"),
        ]
        return {
            "method": METHOD,
            "constants": {
                "FIELD_COOCCUR_MIN": FIELD_COOCCUR_MIN, "FIELD_NEIGHBOR_MIN": FIELD_NEIGHBOR_MIN,
                "NAME_MIN_CONF": NAME_MIN_CONF, "NAME_MAX": NAME_MAX,
                "HHI_COHERENT": HHI_COHERENT, "HHI_DOMINANT": HHI_DOMINANT,
                "SIG_DEPTH": SIG_DEPTH, "NEIGHBOR_LINK_MIN": NEIGHBOR_LINK_MIN, "ROUND": ROUND,
            },
            "input_sha256": {name: sha256_file(p) for name, p in inputs},
            "output_bytes": output_bytes,
            "prohibitions_observed": PROHIBITIONS,
            "totals": {
                "concept_count": self.n_concepts,
                "identity_tiers": self.tier_counts,
                "resists_identification": self.tier_counts.get("resists", 0),
            },
        }

    # ── orchestration ───────────────────────────────────────────────────────────

    def run(self):
        self.load()
        products = {}
        products["concept_dossiers.json"] = self.concept_dossiers()
        products["semantic_fields.json"] = self.semantic_fields()
        products["ayah_identity_profiles.json"] = self.ayah_identity_profiles()
        products["root_consistency.json"] = self.root_consistency()
        products["candidate_names.json"] = self.candidate_names()
        products["falsification_results.json"] = self.falsification()
        products["identity_confidence.json"] = self.identity_confidence()
        products["core_revelation.json"] = self.core_revelation()

        output_bytes = {}
        for name, obj in products.items():
            output_bytes[name] = write_json(self.out_dir / name, obj)
            print(f"    wrote {name} ({output_bytes[name]} bytes)")
        man = self.manifest(output_bytes)
        output_bytes["revelation_manifest.json"] = write_json(
            self.out_dir / "revelation_manifest.json", man)
        print(f"    wrote revelation_manifest.json ({output_bytes['revelation_manifest.json']} bytes)")
        return man


def main():
    ap = argparse.ArgumentParser(description="Monad Phase 7 — Semantic Revelation Engine")
    ap.add_argument("--db", default="generated/monad.db")
    ap.add_argument("--lexicon", default="generated/lexicon")
    ap.add_argument("--concepts", default="generated/concepts")
    ap.add_argument("--identification", default="generated/identification")
    ap.add_argument("--out", default="generated/revelation")
    args = ap.parse_args()
    print(f"Monad Phase 7 — Semantic Revelation Engine ({METHOD})")
    eng = RevelationEngine(args.db, args.lexicon, args.concepts, args.identification, args.out)
    man = eng.run()
    print("  done.")
    print(f"  identity tiers: {json.dumps(man['totals']['identity_tiers'])}")


if __name__ == "__main__":
    main()
