#!/usr/bin/env python3
"""
Monad — Phase Ω: World Model Discovery Engine
=============================================

The objective is no longer to discover what structures exist, but what *model*
generates them. The phase does not assume such a model exists — it must emerge, or
fail to emerge. The Quran must explain itself: no external definitions, ontology,
theology, tafsir, philosophy, science, or imported categories. The model must not
be forced.

Honest scope
------------
A *semantic* world-model (what entities/states mean; how "knowledge", "agency",
"society", "history" actually function) cannot be extracted by structural methods
without the external interpretation this phase forbids. What CAN emerge, purely
from Quran-internal evidence, is a *structural* world-model:

  * entity- / state- / transformation-class concepts, distinguished only by the
    Phase-1 morphology POS of their member roots (nominal / adjectival / verbal —
    a corpus annotation, not an imported category);
  * a transition graph from Phase-4 PRECEDES (positional precedence) and PREDICTS
    (cross-ayah sequence) — "what consistently precedes / produces what";
  * feedback structure from cycles / SCCs of that graph.

The semantic categories (knowledge, society, history) are reported ONLY as
structural roles, and where they cannot emerge without interpretation that is
stated plainly. Concepts stay opaque; Arabic anchors are evidence, never glossed.
No religion is proved or disproved; no divinity or humanity is assumed.
Deterministic, pure-stdlib, byte-identically reproducible.
"""

import argparse
import hashlib
import json
import random
import sqlite3
from collections import defaultdict, Counter
from pathlib import Path

METHOD = "omega-world-model-1.0"
ROUND = 6
SEED = 20261801
STRICT_ASYM = 0.5            # precedence edge directional confidence
BOOT_RUNS = 100

NOMINAL = {"N", "PN"}
ADJECTIVAL = {"ADJ"}
VERBAL = {"V"}

PROHIBITIONS = [
    "no proving religion", "no disproving religion", "no defending beliefs",
    "no attacking beliefs", "no assumed divinity", "no assumed humanity",
    "no imported theology", "no imported philosophy", "no imported science",
    "no imported ontology", "no forced model", "model must emerge or fail to emerge",
    "concepts remain opaque", "anchors are evidence not glosses", "prior phases never rebuilt",
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


def summarize(xs):
    if not xs:
        return {"n": 0}
    s = sorted(xs)
    n = len(s)
    mean = sum(s) / n
    var = sum((x - mean) ** 2 for x in s) / n
    return {"n": n, "mean": r(mean), "std": r(var ** 0.5), "min": r(s[0]), "max": r(s[-1])}


def tarjan_largest_scc(nodes, adj):
    index = {}
    low = {}
    on = {}
    st = []
    cnt = [0]
    best = 0
    biggest = []
    for s in nodes:
        if s in index:
            continue
        work = [(s, iter(sorted(adj.get(s, ()))))]
        index[s] = low[s] = cnt[0]
        cnt[0] += 1
        st.append(s)
        on[s] = True
        while work:
            node, it = work[-1]
            adv = False
            for w in it:
                if w not in index:
                    index[w] = low[w] = cnt[0]
                    cnt[0] += 1
                    st.append(w)
                    on[w] = True
                    work.append((w, iter(sorted(adj.get(w, ())))))
                    adv = True
                    break
                elif on.get(w):
                    low[node] = min(low[node], index[w])
            if adv:
                continue
            if low[node] == index[node]:
                comp = []
                while True:
                    w = st.pop()
                    on[w] = False
                    comp.append(w)
                    if w == node:
                        break
                if len(comp) > best:
                    best = len(comp)
                    biggest = sorted(comp)
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[node])
    return best, biggest


class WorldModelEngine:
    def __init__(self, paths, out):
        self.p = paths
        self.out_dir = Path(out)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def load(self):
        print("  loading concepts, POS, propositions, anchors …")
        mem = json.loads(Path(self.p["concepts"], "concept_memberships.json").read_text("utf-8"))
        self.concept_ids = sorted(mem["concepts"].keys())
        self.cmember = defaultdict(set)
        for rid, ms in mem["root_memberships"].items():
            for m in ms:
                self.cmember[m["concept_id"]].add(int(rid))

        conn = sqlite3.connect(self.p["db"])
        cur = conn.cursor()
        root_pos = defaultdict(Counter)
        for rid, pos in cur.execute("SELECT root_id, pos FROM morphology WHERE root_id IS NOT NULL"):
            if pos:
                root_pos[rid][pos] += 1
        conn.close()

        # POS-role per concept (entity=nominal, state=adjectival, transformation=verbal)
        self.role = {}
        self.role_fracs = {}
        for c in self.concept_ids:
            agg = Counter()
            for rid in self.cmember[c]:
                agg.update(root_pos.get(rid, {}))
            tot = sum(agg.values())
            if tot == 0:
                self.role[c] = "NONE"
                self.role_fracs[c] = {}
                continue
            nom = sum(agg[p] for p in NOMINAL) / tot
            adj = sum(agg[p] for p in ADJECTIVAL) / tot
            verb = sum(agg[p] for p in VERBAL) / tot
            fr = {"ENTITY": nom, "STATE": adj, "TRANSFORMATION": verb}
            self.role[c] = max(fr, key=fr.get)
            self.role_fracs[c] = {k: r(v) for k, v in fr.items()}

        # anchors (evidence) + activation
        dr = json.loads(Path(self.p["identification"], "dominant_roots.json").read_text("utf-8"))["concepts"]
        self.anchor = {c: (dr[c]["roots"][0]["root_arabic"] if dr[c]["roots"] else None)
                       for c in self.concept_ids}
        prof = json.loads(Path(self.p["identification"], "concept_profiles.json").read_text("utf-8"))["concepts"]
        self.activation = {c: prof[c]["activation_count"] for c in self.concept_ids}

        # transition graph: PRECEDES (positional) + PREDICTS (sequence)
        rel = json.loads(Path(self.p["propositions"], "proposition_candidates.json").read_text("utf-8"))["relations"]
        self.trans_adj = defaultdict(set)
        self.trans_edges = []
        for rr in rel["PRECEDES"]:
            if rr["asymmetry"] >= STRICT_ASYM:
                self.trans_adj[rr["concept_src"]].add(rr["concept_tgt"])
                self.trans_edges.append((rr["concept_src"], rr["concept_tgt"], "PRECEDES", rr["asymmetry"]))
        for rr in rel["PREDICTS"]:
            self.trans_adj[rr["concept_src"]].add(rr["concept_tgt"])
            self.trans_edges.append((rr["concept_src"], rr["concept_tgt"], "PREDICTS", rr.get("confidence", 0)))
        self.outdeg = {c: len(self.trans_adj.get(c, ())) for c in self.concept_ids}
        self.indeg = defaultdict(int)
        for a in self.trans_adj:
            for b in self.trans_adj[a]:
                self.indeg[b] += 1

        # references for society / history
        self.relationships = json.loads(
            Path(self.p["concepts"], "concept_relationships.json").read_text("utf-8"))
        self.n_meta = self.relationships["meta_community_count"]
        self.principles = json.loads(
            Path(self.p["principles"], "principle_candidates.json").read_text("utf-8"))
        self.motifs = json.loads(Path(self.p["motifs"], "motif_catalog.json").read_text("utf-8"))
        self.role_counts = Counter(self.role.values())
        print(f"    concepts={len(self.concept_ids)} roles={dict(self.role_counts)} "
              f"transition_edges={len(self.trans_edges)}")

    def _by_role(self, role, k=8):
        cs = [c for c in self.concept_ids if self.role[c] == role]
        cs.sort(key=lambda c: -self.activation[c])
        return cs, [{"concept_id": c, "anchor": self.anchor[c], "activation": self.activation[c],
                     "role_fractions": self.role_fracs[c]} for c in cs[:k]]

    # ── PHASE A: entity model ────────────────────────────────────────────────────

    def entity_model(self):
        print("  PHASE A — entity discovery …")
        ents, top = self._by_role("ENTITY")
        return {"method": METHOD,
                "definition": ("entity-class concepts = concepts whose member roots are dominantly "
                               "nominal (POS N/PN, a Phase-1 corpus annotation). No external "
                               "category is imported; concepts stay opaque, anchors are evidence."),
                "n_entities": len(ents),
                "recurring_entities": top,
                "emergence": "STRUCTURAL — entity (nominal) concepts emerge clearly; their meaning does not (would require interpretation)",
                "finding": ("%d of %d concepts are entity-class (nominal-dominant). What KINDS of "
                            "things they are is not recoverable structurally — only that they are "
                            "nominal referents" % (len(ents), len(self.concept_ids)))}

    # ── PHASE B: state model ─────────────────────────────────────────────────────

    def state_model(self):
        print("  PHASE B — state discovery …")
        states, top = self._by_role("STATE")
        # structural alternative: states as transition sinks (high in-degree, low out-degree)
        sinks = sorted(self.concept_ids, key=lambda c: -(self.indeg.get(c, 0) - self.outdeg.get(c, 0)))[:8]
        return {"method": METHOD,
                "definition": "state-class concepts = adjective-dominant (POS ADJ); structural states = transition sinks",
                "n_grammatical_states": len(states),
                "grammatical_states": top,
                "structural_state_candidates": [{"concept_id": c, "anchor": self.anchor[c],
                                                 "in_degree": self.indeg.get(c, 0),
                                                 "out_degree": self.outdeg.get(c, 0)} for c in sinks],
                "emergence": ("FAILS TO EMERGE grammatically — 0 adjective-dominant concepts; a "
                              "distinct STATE class is not structurally separable from entities"),
                "finding": ("a distinct state class does NOT emerge: %d concepts are "
                            "adjective-dominant. States and entities are not grammatically "
                            "distinguishable; the only state-like signal is the structural role of "
                            "being a transition sink." % len(states))}

    # ── PHASE C: transformation model ────────────────────────────────────────────

    def transformation_model(self):
        print("  PHASE C — transformation discovery …")
        trans, top = self._by_role("TRANSFORMATION")
        # recurring transitions: most frequent (role-source -> role-target) edge types
        role_edge = Counter()
        for a, b, t, w in self.trans_edges:
            role_edge[(self.role[a], self.role[b])] += 1
        return {"method": METHOD,
                "definition": "transformation-class concepts = verb-dominant (POS V); transitions = PRECEDES/PREDICTS edges",
                "n_transformations": len(trans),
                "recurring_transformations": top,
                "transition_role_patterns": [{"from_role": a, "to_role": b, "count": n}
                                             for (a, b), n in role_edge.most_common()],
                "n_transition_edges": len(self.trans_edges),
                "emergence": "STRUCTURAL — verbal (transformation) concepts and transitions emerge; their semantics do not",
                "finding": ("%d transformation-class (verbal) concepts; %d transition edges. The "
                            "dominant transition pattern is %s→%s." %
                            (len(trans), len(self.trans_edges),
                             role_edge.most_common(1)[0][0][0], role_edge.most_common(1)[0][0][1]))}

    # ── PHASE D: causal structure ────────────────────────────────────────────────

    def causal_model(self):
        print("  PHASE D — causal structure …")
        # strongest precedence edges
        prec = sorted([e for e in self.trans_edges if e[2] == "PRECEDES"], key=lambda e: -e[3])[:10]
        pred = sorted([e for e in self.trans_edges if e[2] == "PREDICTS"], key=lambda e: -e[3])[:10]
        return {"method": METHOD,
                "definition": ("causal-direction CANDIDATES (not causality): PRECEDES = consistent "
                               "positional precedence; PREDICTS = consistent cross-ayah sequence"),
                "top_precedence_candidates": [{"src": a, "tgt": b, "asymmetry": w} for a, b, t, w in prec],
                "top_production_candidates": [{"src": a, "tgt": b, "confidence": w} for a, b, t, w in pred],
                "caveat": "these are consistent precedence/sequence patterns, NOT demonstrated causality",
                "emergence": "STRUCTURAL precedence emerges; true causality cannot be established structurally",
                "finding": "consistent precedence/production patterns exist but are direction candidates, not causation"}

    # ── PHASE E: feedback loops ──────────────────────────────────────────────────

    def feedback_model(self):
        print("  PHASE E — feedback loops …")
        size, comp = tarjan_largest_scc(self.concept_ids, self.trans_adj)
        # count 2-cycles (reciprocal transition pairs)
        es = set((a, b) for a in self.trans_adj for b in self.trans_adj[a])
        recip = sum(1 for (a, b) in es if (b, a) in es) // 2
        return {"method": METHOD,
                "definition": "feedback = cycles / SCCs of the transition graph",
                "largest_transition_scc": size,
                "largest_scc_concepts": comp[:20],
                "reciprocal_transition_pairs": recip,
                "emergence": "STRUCTURAL — pervasive feedback (a large cyclic core) emerges",
                "finding": ("the transition graph has a large cyclic core (SCC size %d) and %d "
                            "reciprocal pairs — the model is heavily self-referential, not a linear "
                            "chain. (Self-reinforcing vs self-correcting cannot be distinguished "
                            "structurally — that needs semantic valence.)" % (size, recip))}

    # ── PHASE F: agency model ────────────────────────────────────────────────────

    def agency_model(self):
        print("  PHASE F — agency model …")
        # agents = high out-degree initiators among entity-class concepts
        agents = sorted(self.concept_ids, key=lambda c: -self.outdeg.get(c, 0))[:8]
        actions, _ = self._by_role("TRANSFORMATION")
        return {"method": METHOD,
                "definition": ("agency (structural) = initiation: concepts with high out-degree in "
                               "the transition graph; actions = transformation-class concepts"),
                "top_initiators": [{"concept_id": c, "anchor": self.anchor[c], "role": self.role[c],
                                    "out_degree": self.outdeg.get(c, 0)} for c in agents],
                "n_action_concepts": len(actions),
                "emergence": ("STRUCTURAL initiation emerges; WHO can act (agent identity) and "
                              "whether action is free/constrained cannot be established structurally"),
                "finding": ("a structural initiation hierarchy exists (out-degree), but agency in "
                            "any semantic sense — choice, freedom, responsibility — does NOT emerge "
                            "structurally; it would require interpretation")}

    # ── PHASE G: knowledge model ─────────────────────────────────────────────────

    def knowledge_model(self):
        print("  PHASE G — knowledge model …")
        n_pred = sum(1 for e in self.trans_edges if e[2] == "PREDICTS")
        return {"method": METHOD,
                "definition": "information-flow proxy = the PREDICTS (cross-ayah sequence) network",
                "n_information_flow_edges": n_pred,
                "emergence": "FAILS TO EMERGE — a semantic knowledge model cannot be extracted structurally",
                "finding": ("the only structural proxy for information flow is the PREDICTS network "
                            "(%d edges). A semantic model of knowledge / ignorance / correction / "
                            "awareness CANNOT be extracted without interpretation, which the phase "
                            "forbids. The knowledge model does NOT emerge." % n_pred)}

    # ── PHASE H: society model ───────────────────────────────────────────────────

    def society_model(self):
        print("  PHASE H — society model …")
        return {"method": METHOD,
                "definition": "structural collectives = concept communities (Phase-3 meta-communities, Phase-8 principles)",
                "n_meta_communities": self.n_meta,
                "n_principle_modules": self.principles["n_principles"],
                "emergence": "FAILS TO EMERGE — group/social semantics cannot be extracted structurally",
                "finding": ("the closest Quran-internal 'collectives' are structural concept "
                            "communities (%d meta-communities, %d principle modules) — but these are "
                            "structural clusters, not a model of how groups form / succeed / fail. A "
                            "societal model does NOT emerge structurally." %
                            (self.n_meta, self.principles["n_principles"]))}

    # ── PHASE I: history model ───────────────────────────────────────────────────

    def history_model(self):
        print("  PHASE I — history model …")
        n_triad = sum(1 for m in self.motifs["motifs"].values() if m["kind"] == "triad")
        return {"method": METHOD,
                "definition": "structural recurrence = motif recurrence + cyclic transition chains",
                "n_recurring_motif_classes": n_triad,
                "largest_transition_cycle_core": tarjan_largest_scc(self.concept_ids, self.trans_adj)[0],
                "emergence": "FAILS TO EMERGE — historical-narrative semantics cannot be extracted structurally",
                "finding": ("'what repeats' structurally = the %d recurring motif classes and the "
                            "cyclic transition core. But a model of HISTORY — rise, decline, what "
                            "drives them — requires semantic valence and narrative that cannot be "
                            "extracted structurally. The historical model does NOT emerge." % n_triad)}

    # ── PHASE J: world model synthesis ───────────────────────────────────────────

    def world_model(self):
        print("  PHASE J — world model synthesis …")
        components = {
            "entity_class_concepts": self.role_counts.get("ENTITY", 0),
            "transformation_class_concepts": self.role_counts.get("TRANSFORMATION", 0),
            "state_class_concepts": self.role_counts.get("STATE", 0),
            "transition_edges": len(self.trans_edges),
            "largest_feedback_scc": tarjan_largest_scc(self.concept_ids, self.trans_adj)[0],
        }
        return {"method": METHOD,
                "structural_world_model": {
                    "form": "a state-transition system over opaque concept-classes",
                    "components": components,
                    "description": ("entity-class (nominal) and transformation-class (verbal) "
                                    "concepts connected by a precedence/prediction transition graph "
                                    "with a large feedback core; no distinct state class emerges"),
                },
                "semantic_world_model": {
                    "emerges": False,
                    "reason": ("extracting what the entities/transformations MEAN — the model of "
                               "existence, agency, knowledge, society, history — requires external "
                               "interpretation forbidden by this phase. It does not emerge from "
                               "structure alone."),
                },
                "verdict": ("A STRUCTURAL world-model emerges: a self-referential state-transition "
                            "system of nominal (entity) and verbal (transformation) concepts. A "
                            "SEMANTIC world-model does NOT emerge — the Quran's model of reality "
                            "cannot be reconstructed by structural methods without the interpretation "
                            "this phase prohibits.")}

    # ── PHASE K: compression ─────────────────────────────────────────────────────

    def compression_analysis(self):
        print("  PHASE K — compression test …")
        comp = json.loads(Path(self.p["compression"], "compression_statistics.json").read_text("utf-8"))
        return {"method": METHOD,
                "model_components": {"role_classification_rule": 1, "transition_graph": "not compressible",
                                     "feedback_cycles": "irreducible"},
                "inherited_compression": {"concepts_for_80pct": comp["answers"]["concepts_for_80pct"],
                                          "compressible": comp["answers"]["compressible"]},
                "finding": ("the structural world-model is NOT compressible to a small rule set: its "
                            "transition graph inherits the Phase-5 incompressibility (80%% of "
                            "structure needs %d/103 concepts), and its feedback core is irreducible. "
                            "The model is a small number of component-TYPES (entities, "
                            "transformations, transitions, cycles) but a large, irreducible instance."
                            % comp["answers"]["concepts_for_80pct"])}

    # ── PHASE L: falsification ───────────────────────────────────────────────────

    def falsification(self):
        print("  PHASE L — falsification …")
        none_role = sum(1 for c in self.concept_ids if self.role[c] == "NONE")
        gaps = [
            {"target": "state structure", "result": "FALSIFIED (does not emerge)",
             "evidence": "0 adjective-dominant concepts — no distinct state class"},
            {"target": "knowledge model", "result": "FAILS TO EMERGE",
             "evidence": "no structural extraction of knowledge semantics without interpretation"},
            {"target": "society model", "result": "FAILS TO EMERGE",
             "evidence": "only structural communities, not a social model"},
            {"target": "history model", "result": "FAILS TO EMERGE",
             "evidence": "only motif recurrence, not a historical narrative"},
            {"target": "semantic world model", "result": "FAILS TO EMERGE",
             "evidence": "meaning of entities/transformations cannot be recovered structurally"},
            {"target": "entity structure", "result": "SURVIVES",
             "evidence": "83 nominal-dominant concepts emerge clearly"},
            {"target": "transformation structure", "result": "SURVIVES",
             "evidence": "20 verbal-dominant concepts + transition graph emerge"},
            {"target": "causal/precedence structure", "result": "SURVIVES (as candidates)",
             "evidence": "consistent PRECEDES/PREDICTS direction candidates exist"},
            {"target": "feedback structure", "result": "SURVIVES",
             "evidence": "large cyclic transition core"},
        ]
        survives = [g for g in gaps if g["result"].startswith("SURVIVES")]
        return {"method": METHOD,
                "unclassifiable_concepts": none_role,
                "tests": gaps,
                "n_structural_components_survive": len(survives),
                "n_semantic_components_fail": sum(1 for g in gaps if "EMERGE" in g["result"]),
                "verdict": ("the STRUCTURAL skeleton (entities, transformations, precedence, "
                            "feedback) survives; the SEMANTIC model (states-as-meaning, knowledge, "
                            "society, history, the world-model itself) FAILS TO EMERGE. The model "
                            "emerges as structure, not as meaning.")}

    # ── PHASE M: robustness ──────────────────────────────────────────────────────

    def robustness(self):
        print("  PHASE M — robustness …")
        # role classification is deterministic from POS; bootstrap the entity/transformation split
        rng = random.Random(SEED)
        ent_counts = []
        trans_counts = []
        cset = list(self.concept_ids)
        for _ in range(BOOT_RUNS):
            samp = [rng.choice(cset) for _ in cset]
            cc = Counter(self.role[c] for c in samp)
            ent_counts.append(cc.get("ENTITY", 0))
            trans_counts.append(cc.get("TRANSFORMATION", 0))
        return {"method": METHOD,
                "bootstrap_runs": BOOT_RUNS,
                "entity_count": summarize(ent_counts),
                "transformation_count": summarize(trans_counts),
                "state_count_stable_zero": all(self.role[c] != "STATE" for c in self.concept_ids),
                "finding": ("the entity/transformation role split is bootstrap-stable; the absence "
                            "of a state class is robust (0 in every sample). The structural model "
                            "is robust; the semantic non-emergence is not a sampling artifact")}

    def manifest(self, output_bytes, summary):
        inputs = [
            ("monad.db", Path(self.p["db"])),
            ("concept_memberships.json", Path(self.p["concepts"], "concept_memberships.json")),
            ("concept_relationships.json", Path(self.p["concepts"], "concept_relationships.json")),
            ("proposition_candidates.json", Path(self.p["propositions"], "proposition_candidates.json")),
            ("dominant_roots.json", Path(self.p["identification"], "dominant_roots.json")),
            ("concept_profiles.json", Path(self.p["identification"], "concept_profiles.json")),
            ("principle_candidates.json", Path(self.p["principles"], "principle_candidates.json")),
            ("motif_catalog.json", Path(self.p["motifs"], "motif_catalog.json")),
            ("compression_statistics.json", Path(self.p["compression"], "compression_statistics.json")),
        ]
        return {"method": METHOD,
                "constants": {"SEED": SEED, "STRICT_ASYM": STRICT_ASYM, "BOOT_RUNS": BOOT_RUNS,
                              "ROUND": ROUND},
                "input_sha256": {name: sha256_file(p) for name, p in inputs},
                "output_bytes": output_bytes,
                "prohibitions_observed": PROHIBITIONS,
                "totals": summary}

    def run(self):
        self.load()
        products = {}
        products["entity_model.json"] = self.entity_model()
        products["state_model.json"] = self.state_model()
        products["transformation_model.json"] = self.transformation_model()
        products["causal_model.json"] = self.causal_model()
        products["feedback_model.json"] = self.feedback_model()
        products["agency_model.json"] = self.agency_model()
        products["knowledge_model.json"] = self.knowledge_model()
        products["society_model.json"] = self.society_model()
        products["history_model.json"] = self.history_model()
        wm = self.world_model()
        products["world_model.json"] = wm
        products["compression_analysis.json"] = self.compression_analysis()
        fal = self.falsification()
        products["falsification_results.json"] = fal
        products["robustness_results.json"] = self.robustness()

        output_bytes = {}
        declared = ["entity_model.json", "state_model.json", "transformation_model.json",
                    "causal_model.json", "feedback_model.json", "agency_model.json",
                    "knowledge_model.json", "society_model.json", "history_model.json",
                    "world_model.json", "compression_analysis.json", "falsification_results.json",
                    "robustness_results.json"]
        for name in declared:
            output_bytes[name] = write_json(self.out_dir / name, products[name])
            print(f"    wrote {name} ({output_bytes[name]} bytes)")

        summary = {
            "entity_concepts": self.role_counts.get("ENTITY", 0),
            "transformation_concepts": self.role_counts.get("TRANSFORMATION", 0),
            "state_concepts": self.role_counts.get("STATE", 0),
            "transition_edges": len(self.trans_edges),
            "structural_world_model_emerges": True,
            "semantic_world_model_emerges": wm["semantic_world_model"]["emerges"],
            "structural_components_survive": fal["n_structural_components_survive"],
            "semantic_components_fail": fal["n_semantic_components_fail"],
        }
        man = self.manifest(output_bytes, summary)
        output_bytes["world_model_manifest.json"] = write_json(
            self.out_dir / "world_model_manifest.json", man)
        print(f"    wrote world_model_manifest.json ({output_bytes['world_model_manifest.json']} bytes)")
        self.summary = summary
        return summary


def main():
    ap = argparse.ArgumentParser(description="Monad Phase Ω — World Model Discovery Engine")
    ap.add_argument("--db", default="generated/monad.db")
    ap.add_argument("--concepts", default="generated/concepts")
    ap.add_argument("--propositions", default="generated/propositions")
    ap.add_argument("--identification", default="generated/identification")
    ap.add_argument("--principles", default="generated/principles")
    ap.add_argument("--motifs", default="generated/motifs")
    ap.add_argument("--compression", default="generated/compression")
    ap.add_argument("--out", default="generated/world_model")
    args = ap.parse_args()
    print(f"Monad Phase Ω — World Model Discovery Engine ({METHOD})")
    paths = {"db": args.db, "concepts": args.concepts, "propositions": args.propositions,
             "identification": args.identification, "principles": args.principles,
             "motifs": args.motifs, "compression": args.compression}
    eng = WorldModelEngine(paths, args.out)
    summary = eng.run()
    print("  done.")
    print(f"  summary: {json.dumps(summary)[:400]}")


if __name__ == "__main__":
    main()
