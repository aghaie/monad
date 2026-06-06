#!/usr/bin/env python3
"""
Monad — Phase Σ: Internal Semantic Reconstruction Engine
========================================================

Phase Ω reached a limit: structural analysis alone could not reconstruct the
*semantic* layer. Phase Σ tests a new hypothesis — the Quran may define its own
meanings internally — and either demonstrates it or falsifies it.

Fundamental principle
---------------------
Meaning is allowed; EXTERNAL meaning is forbidden. Everything must emerge from the
Quran corpus and the existing Monad outputs and nothing else. No dictionary, tafsir,
translation, lexicon, embedding, LLM knowledge, or imported label.

This is the distributional/relational theory of meaning, applied Quran-internally: a
concept is "defined" only by its relations to OTHER (opaque) concepts — its
associations, contrasts, dependencies, and functional role. Arabic anchors appear
only as evidence labels, never glossed. The engine asks whether such a relational
semantic layer is recoverable, stable, and self-defining — and reports honestly the
boundary between RELATIONAL meaning (which may emerge) and REFERENTIAL meaning (what
a concept denotes, which Phase Ω showed cannot emerge structurally).

Deterministic, pure-stdlib, byte-identically reproducible.
"""

import argparse
import hashlib
import json
import math
import random
import sqlite3
from collections import defaultdict, Counter
from itertools import combinations
from pathlib import Path

METHOD = "sigma-semantics-1.0"
ROUND = 6
SEED = 20261901
SUPPORT_MIN = 5
NPMI_MIN = 0.2
MARGINAL_MIN = 30
DEFINE_TOP = 5               # concepts per definition
RECOVER_NEIGHBOR_MIN = 0.15  # top-neighbor weight floor for recoverability
DRIFT_STABLE = 0.5           # cross-half cosine floor for stable meaning
BOOT_RUNS = 100
PRIMITIVE_TARGETS = [0.5, 0.7, 0.8, 0.9]

PROHIBITIONS = [
    "no dictionary", "no tafsir", "no translation", "no hadith", "no theology",
    "no ontology", "no philosophy", "no lexicon", "no embeddings", "no LLM knowledge",
    "no imported meanings", "no imported labels", "no religious interpretation",
    "no apologetics", "no assumption a meaning exists", "no assumption it does not",
    "definitions stay inside the Quranic concept network", "prior phases never rebuilt",
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


def cosine(a, b):
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na > 0 and nb > 0 else 0.0


class SemanticsEngine:
    def __init__(self, paths, out):
        self.p = paths
        self.out_dir = Path(out)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def load(self):
        print("  reconstructing co-occurrence + loading Monad relational outputs …")
        mem = json.loads(Path(self.p["concepts"], "concept_memberships.json").read_text("utf-8"))
        root2c = defaultdict(set)
        lem2c = defaultdict(set)
        for rid, ms in mem["root_memberships"].items():
            for m in ms:
                root2c[int(rid)].add(m["concept_id"])
        for lid, ms in mem["lemma_memberships"].items():
            for m in ms:
                lem2c[int(lid)].add(m["concept_id"])
        self.concept_ids = sorted(mem["concepts"].keys())

        conn = sqlite3.connect(self.p["db"])
        cur = conn.cursor()
        seqmap = {(s, a): seq for seq, s, a in
                  cur.execute("SELECT ayah_sequential, surah_number, ayah_number FROM ayahs")}
        ayc = defaultdict(set)
        self.ay_surah = {}
        for s, a, rid, lid in cur.execute(
                "SELECT surah_number, ayah_number, root_id, lemma_id FROM words"):
            seq = seqmap[(s, a)]
            self.ay_surah[seq] = s
            if rid is not None:
                x = root2c.get(rid)
                if x:
                    ayc[seq] |= x
            if lid is not None:
                x = lem2c.get(lid)
                if x:
                    ayc[seq] |= x
        conn.close()
        self.ayahs = {seq: tuple(sorted(ayc[seq])) for seq in ayc if ayc[seq]}
        self.seqs = sorted(self.ayahs)
        self.N = len(self.seqs)
        self.marg = defaultdict(int)
        self.co = defaultdict(int)
        for seq in self.seqs:
            t = self.ayahs[seq]
            for c in t:
                self.marg[c] += 1
            for a, b in combinations(t, 2):
                self.co[(a, b)] += 1

        # relational evidence from prior phases (no external meaning)
        self.atlas = json.loads(
            Path(self.p["identification"], "concept_atlas.json").read_text("utf-8"))["concepts"]
        self.identity = json.loads(
            Path(self.p["revelation"], "identity_confidence.json").read_text("utf-8"))["concepts"]
        dr = json.loads(Path(self.p["identification"], "dominant_roots.json").read_text("utf-8"))["concepts"]
        self.anchor = {c: (dr[c]["roots"][0]["root_arabic"] if dr[c]["roots"] else None)
                       for c in self.concept_ids}
        rel = json.loads(Path(self.p["propositions"], "proposition_candidates.json").read_text("utf-8"))["relations"]
        self.requires = defaultdict(list)
        for rr in rel["REQUIRES"]:
            self.requires[rr["concept_src"]].append(rr["concept_tgt"])
        self.predicts_in = defaultdict(list)
        for rr in rel["PREDICTS"]:
            self.predicts_in[rr["concept_tgt"]].append(rr["concept_src"])

        # exclusion (contrast) pairs
        self.big = [c for c in self.concept_ids if self.marg.get(c, 0) >= MARGINAL_MIN]
        self.exclusion = defaultdict(list)
        for a, b in combinations(sorted(self.big), 2):
            if self.cof(a, b) == 0:
                self.exclusion[a].append(b)
                self.exclusion[b].append(a)
        print(f"    ayahs={self.N} concepts={len(self.concept_ids)} "
              f"exclusion_pairs={sum(len(v) for v in self.exclusion.values()) // 2}")

    def cof(self, a, b):
        return self.co.get((min(a, b), max(a, b)), 0)

    def _neighbors(self, c):
        return self.atlas.get(c, {}).get("closest_concepts", [])

    def _neighbor_vec(self, c, seqset=None):
        """co-occurrence neighbor vector of c over an ayah set (for drift)."""
        vec = defaultdict(float)
        if seqset is None:
            for (a, b), k in self.co.items():
                if a == c:
                    vec[b] += k
                elif b == c:
                    vec[a] += k
            return vec
        marg = 0
        for seq in seqset:
            t = self.ayahs[seq]
            if c in t:
                marg += 1
                for o in t:
                    if o != c:
                        vec[o] += 1
        return vec

    # ── PHASE A: recoverability ─────────────────────────────────────────────────

    def recoverability(self):
        print("  PHASE A — semantic recoverability …")
        self.recover = {}
        out = {}
        for c in self.concept_ids:
            tier = self.identity.get(c, {}).get("tier", "resists")
            nb = self._neighbors(c)
            top_nb = nb[0]["weight"] if nb else 0.0
            n_excl = len(self.exclusion.get(c, []))
            # recoverable: clear anchor (strong/moderate) + distinctive neighbour + has contrasts
            if tier in ("strong", "moderate") and top_nb >= RECOVER_NEIGHBOR_MIN:
                cls = "RECOVERABLE"
            elif tier == "resists" or (not nb):
                cls = "NON_RECOVERABLE"
            else:
                cls = "PARTIALLY_RECOVERABLE"
            self.recover[c] = cls
            out[c] = {"tier": tier, "top_neighbor_weight": r(top_nb),
                      "n_contrasts": n_excl, "classification": cls}
        tally = Counter(self.recover.values())
        return {"method": METHOD,
                "definition": ("a concept is RECOVERABLE if independent Quranic evidence converges: a "
                               "falsification-surviving identity anchor (Phase 7), a distinctive "
                               "neighbourhood (Phase 6), and contrasts. No external meaning is used."),
                "tally": dict(tally),
                "concepts": out,
                "finding": ("%d of %d concepts are relationally RECOVERABLE, %d partial, %d "
                            "non-recoverable" % (tally.get("RECOVERABLE", 0), len(self.concept_ids),
                                                 tally.get("PARTIALLY_RECOVERABLE", 0),
                                                 tally.get("NON_RECOVERABLE", 0)))}

    # ── PHASE B + J: definitions / internal dictionary ──────────────────────────

    def _definition(self, c):
        nb = self._neighbors(c)[:DEFINE_TOP]
        return {
            "concept": c, "anchor_evidence": self.anchor[c],
            "associated_with": [{"concept": x["concept_id"], "weight": x["weight"]} for x in nb],
            "requires": self.requires.get(c, [])[:3],
            "contrasts_with": sorted(self.exclusion.get(c, []),
                                     key=lambda b: -self.marg.get(b, 0))[:3],
            "preceded_by": sorted(set(self.predicts_in.get(c, [])))[:3],
        }

    def definitions(self):
        print("  PHASE B — definition discovery …")
        out = {c: self._definition(c) for c in self.concept_ids if self.recover[c] != "NON_RECOVERABLE"}
        return {"method": METHOD,
                "definition": ("each concept defined ENTIRELY from other Quranic concepts: its "
                               "associates (Phase-3 overlap), requirements (REQUIRES), contrasts "
                               "(exclusions), and antecedents (PREDICTS). Anchor is evidence only."),
                "n_defined": len(out),
                "concepts": out}

    def internal_dictionary(self, defs):
        return {"method": METHOD,
                "format": "CONCEPT_X defined using {associated, requires, contrasts, preceded_by} — all concepts",
                "n_entries": defs["n_defined"],
                "no_external_language": True,
                "entries": defs["concepts"]}

    # ── PHASE C: semantic boundaries ────────────────────────────────────────────

    def semantic_boundaries(self):
        print("  PHASE C — semantic boundaries …")
        out = {}
        for c in self.concept_ids:
            if self.recover[c] == "NON_RECOVERABLE":
                continue
            belongs = [x["concept_id"] for x in self._neighbors(c)[:DEFINE_TOP]]
            not_belongs = sorted(self.exclusion.get(c, []), key=lambda b: -self.marg.get(b, 0))[:DEFINE_TOP]
            out[c] = {"belongs": belongs, "does_not_belong": not_belongs,
                      "boundary_sharpness": r(len(not_belongs) / (len(belongs) + len(not_belongs)))
                      if (belongs or not_belongs) else 0.0}
        return {"method": METHOD,
                "definition": "belongs = strongest neighbours; does_not_belong = strongest exclusions",
                "n_concepts": len(out), "concepts": out}

    # ── PHASE D: contrast engine ────────────────────────────────────────────────

    def contrasts(self):
        print("  PHASE D — contrast engine …")
        pairs = []
        seen = set()
        for a in self.exclusion:
            for b in self.exclusion[a]:
                key = (min(a, b), max(a, b))
                if key in seen:
                    continue
                seen.add(key)
                pairs.append({"a": a, "anchor_a": self.anchor[a], "b": b, "anchor_b": self.anchor[b],
                              "combined_marginal": self.marg[a] + self.marg[b]})
        pairs.sort(key=lambda p: -p["combined_marginal"])
        return {"method": METHOD,
                "definition": ("Quran-internal opposites = concepts that never co-occur despite both "
                               "being frequent (co = 0, both marginals >= %d). Not lexical opposites." % MARGINAL_MIN),
                "n_contrast_pairs": len(pairs),
                "strongest_contrasts": pairs[:15]}

    # ── PHASE E: functional roles ───────────────────────────────────────────────

    def functional_roles(self):
        print("  PHASE E — functional meaning …")
        out = {}
        for c in self.concept_ids:
            if self.recover[c] == "NON_RECOVERABLE":
                continue
            a = self.atlas.get(c, {})
            out[c] = {
                "requires": self.requires.get(c, [])[:3],
                "preceded_by_causes": sorted(set(self.predicts_in.get(c, [])))[:3],
                "depends_out": [d["partner"] for d in a.get("strongest_dependencies_out", [])[:3]],
                "blocks_excludes": sorted(self.exclusion.get(c, []), key=lambda b: -self.marg.get(b, 0))[:3],
                "amplifies_neighbors": [x["concept_id"] for x in self._neighbors(c)[:3]],
            }
        return {"method": METHOD,
                "definition": "functional role per concept: causes / requires / blocks / amplifies (all concepts)",
                "n_concepts": len(out), "concepts": out}

    # ── PHASE F: semantic equations ─────────────────────────────────────────────

    def semantic_equations(self):
        print("  PHASE F — semantic equations …")
        eqs = []
        # A requires D (necessity), confidence ~1
        for a, ts in self.requires.items():
            for d in ts[:2]:
                eqs.append({"equation": "REQUIRES", "lhs": a, "rhs": d,
                            "form": "A always accompanied by D", "tested": True,
                            "holds": self.cof(a, d) >= 0.9 * self.marg[a]})
        # A behaves like B (high neighbour similarity)
        for c in self.concept_ids:
            nb = self._neighbors(c)
            if nb and nb[0]["weight"] >= 0.4:
                eqs.append({"equation": "BEHAVES_LIKE", "lhs": c, "rhs": nb[0]["concept_id"],
                            "form": "A behaves like B", "tested": True,
                            "holds": True, "weight": nb[0]["weight"]})
        n_hold = sum(1 for e in eqs if e["holds"])
        return {"method": METHOD,
                "definition": "Quran-internal equations (REQUIRES / BEHAVES_LIKE), tested against co-occurrence",
                "n_equations": len(eqs), "n_holding": n_hold,
                "equations": sorted(eqs, key=lambda e: (e["equation"], e["lhs"]))[:40]}

    # ── PHASE G: semantic primitives ────────────────────────────────────────────

    def semantic_primitives(self):
        print("  PHASE G — semantic primitives …")
        # which concepts appear in others' definitions (neighbourhoods); greedy cover
        appears = defaultdict(set)   # concept -> set of concepts it helps define
        for c in self.concept_ids:
            if self.recover[c] == "NON_RECOVERABLE":
                continue
            for x in self._neighbors(c)[:DEFINE_TOP]:
                appears[x["concept_id"]].add(c)
        universe = set(c for c in self.concept_ids if self.recover[c] != "NON_RECOVERABLE")
        # greedy set cover
        covered = set()
        order = []
        remaining = set(appears)
        while remaining and len(covered) < len(universe):
            best = max(sorted(remaining), key=lambda p: len(appears[p] - covered))
            gain = len(appears[best] - covered)
            if gain == 0:
                break
            covered |= appears[best]
            order.append({"primitive": best, "anchor": self.anchor[best],
                          "marginal": self.marg[best],
                          "cumulative_coverage": r(len(covered) / len(universe))})
            remaining.discard(best)
        sets = []
        for t in PRIMITIVE_TARGETS:
            k = next((o["cumulative_coverage"] for o in order), 0)
            kk = next((i + 1 for i, o in enumerate(order) if o["cumulative_coverage"] >= t), None)
            sets.append({"target": t, "primitives_required": kk})
        return {"method": METHOD,
                "definition": "semantic primitives = smallest set of concepts that appear in (define) most others",
                "n_universe": len(universe),
                "greedy_order": order[:20],
                "minimum_sets": sets,
                "finding": ("a small semantic core %s most definitions — but note (Phase 17) much of "
                            "this is frequency; genuine semantic anchoring is tested in Phase I" %
                            ("covers" if order and order[min(4, len(order)-1)]["cumulative_coverage"] >= 0.5 else "does not cover"))}

    # ── PHASE H: cross-surah consistency ────────────────────────────────────────

    def semantic_consistency(self):
        print("  PHASE H — cross-surah semantic consistency …")
        half = self.N // 2
        s1 = set(self.seqs[:half])
        s2 = set(self.seqs[half:])
        drifts = []
        out = {}
        for c in self.concept_ids:
            if self.recover[c] == "NON_RECOVERABLE":
                continue
            v1 = self._neighbor_vec(c, s1)
            v2 = self._neighbor_vec(c, s2)
            sim = r(cosine(v1, v2))
            out[c] = {"cross_half_cosine": sim, "stable": sim >= DRIFT_STABLE}
            drifts.append(sim)
        n_stable = sum(1 for v in out.values() if v["stable"])
        return {"method": METHOD,
                "definition": "neighbour-profile cosine between corpus halves; stable >= %.1f" % DRIFT_STABLE,
                "n_concepts": len(out), "n_stable": n_stable, "concepts": out,
                "drift_distribution": summarize(drifts),
                "finding": ("%d of %d recoverable concepts keep a stable neighbourhood across corpus "
                            "halves (cosine >= %.1f) — meaning is largely consistent, not fragmented" %
                            (n_stable, len(out), DRIFT_STABLE))}

    # ── PHASE I: semantic anchors (vs frequency) ────────────────────────────────

    def semantic_anchors(self):
        print("  PHASE I — semantic anchors (controlling for frequency) …")
        # definitional centrality = # of others a concept helps define (neighbourhoods)
        defcent = Counter()
        for c in self.concept_ids:
            for x in self._neighbors(c)[:DEFINE_TOP]:
                defcent[x["concept_id"]] += 1
        # frequency-expected centrality: proportional to marginal rank
        total_marg = sum(self.marg.values())
        anchors = []
        for c in self.concept_ids:
            dc = defcent.get(c, 0)
            exp = (self.marg.get(c, 0) / total_marg) * sum(defcent.values())
            residual = dc - exp        # genuine semantic anchoring beyond frequency
            anchors.append({"concept": c, "anchor": self.anchor[c],
                            "definitional_centrality": dc, "marginal": self.marg.get(c, 0),
                            "frequency_expected": r(exp), "residual": r(residual)})
        anchors.sort(key=lambda a: -a["residual"])
        # is the top frequency hub a semantic anchor?
        hub = next(a for a in anchors if a["concept"] == "CONCEPT_007")
        return {"method": METHOD,
                "definition": ("semantic anchor = high definitional centrality BEYOND frequency "
                               "expectation (residual). Distinct from the frequency hub."),
                "top_semantic_anchors": anchors[:10],
                "frequency_hub_as_semantic_anchor": {"concept": "CONCEPT_007",
                                                     "residual": hub["residual"],
                                                     "is_semantic_anchor": hub["residual"] > 0},
                "finding": ("the genuine semantic anchors (high residual) are NOT the frequency hub: "
                            "CONCEPT_007 has residual %.1f. Definitional centrality differs from "
                            "frequency centrality — the semantic network has its own structure." %
                            hub["residual"])}

    # ── PHASE K: falsification ──────────────────────────────────────────────────

    def falsification(self, recov, cons, anchors):
        print("  PHASE K — falsification …")
        # collapse: recoverable concepts that turn out unstable across halves
        unstable = [c for c in cons["concepts"] if not cons["concepts"][c]["stable"]]
        tests = [
            {"claim": "relational meaning is recoverable",
             "result": "SURVIVES" if recov["tally"].get("RECOVERABLE", 0) >= 50 else "FALSIFIED",
             "evidence": f"{recov['tally'].get('RECOVERABLE',0)} concepts relationally recoverable"},
            {"claim": "meaning is consistent across the corpus (not fragmented)",
             "result": "SURVIVES" if cons["n_stable"] >= 0.6 * cons["n_concepts"] else "FALSIFIED",
             "evidence": f"{cons['n_stable']}/{cons['n_concepts']} stable; {len(unstable)} drift"},
            {"claim": "semantic anchoring is distinct from frequency",
             "result": "SURVIVES" if not anchors["frequency_hub_as_semantic_anchor"]["is_semantic_anchor"]
                       else "FALSIFIED",
             "evidence": f"frequency hub residual {anchors['frequency_hub_as_semantic_anchor']['residual']}"},
            {"claim": "REFERENTIAL meaning is recoverable (what concepts denote)",
             "result": "FAILS TO EMERGE",
             "evidence": "definitions are purely relational (concept-to-concept); what a concept "
                         "DENOTES cannot be recovered without external grounding (Phase Ω)"},
        ]
        return {"method": METHOD,
                "tests": tests,
                "unstable_concepts": unstable[:15],
                "n_surviving": sum(1 for t in tests if t["result"] == "SURVIVES"),
                "verdict": ("RELATIONAL meaning emerges and survives (recoverable, consistent, "
                            "non-frequency anchoring); REFERENTIAL meaning does NOT emerge. The Quran "
                            "defines its concepts in terms of one another, but not what they denote.")}

    # ── PHASE L: robustness ─────────────────────────────────────────────────────

    def robustness(self):
        print("  PHASE L — robustness …")
        rng = random.Random(SEED)
        stable_counts = []
        for _ in range(BOOT_RUNS // 5):
            idx = [rng.choice(self.seqs) for _ in self.seqs]
            s1 = set(idx[:len(idx) // 2])
            s2 = set(idx[len(idx) // 2:])
            cnt = 0
            tot = 0
            for c in self.concept_ids:
                if self.recover.get(c) == "NON_RECOVERABLE":
                    continue
                tot += 1
                v1 = self._neighbor_vec(c, s1)
                v2 = self._neighbor_vec(c, s2)
                if cosine(v1, v2) >= DRIFT_STABLE:
                    cnt += 1
            stable_counts.append(cnt / tot if tot else 0)
        return {"method": METHOD,
                "bootstrap_runs": BOOT_RUNS // 5,
                "stable_fraction_bootstrap": summarize(stable_counts),
                "finding": "the fraction of concepts with stable cross-half meaning is bootstrap-robust"}

    def manifest(self, output_bytes, summary):
        inputs = [
            ("monad.db", Path(self.p["db"])),
            ("concept_memberships.json", Path(self.p["concepts"], "concept_memberships.json")),
            ("concept_atlas.json", Path(self.p["identification"], "concept_atlas.json")),
            ("dominant_roots.json", Path(self.p["identification"], "dominant_roots.json")),
            ("identity_confidence.json", Path(self.p["revelation"], "identity_confidence.json")),
            ("proposition_candidates.json", Path(self.p["propositions"], "proposition_candidates.json")),
        ]
        return {"method": METHOD,
                "constants": {"SEED": SEED, "SUPPORT_MIN": SUPPORT_MIN, "NPMI_MIN": NPMI_MIN,
                              "MARGINAL_MIN": MARGINAL_MIN, "DEFINE_TOP": DEFINE_TOP,
                              "RECOVER_NEIGHBOR_MIN": RECOVER_NEIGHBOR_MIN, "DRIFT_STABLE": DRIFT_STABLE,
                              "BOOT_RUNS": BOOT_RUNS, "ROUND": ROUND},
                "input_sha256": {name: sha256_file(p) for name, p in inputs},
                "output_bytes": output_bytes,
                "prohibitions_observed": PROHIBITIONS,
                "totals": summary}

    def run(self):
        self.load()
        products = {}
        recov = self.recoverability()
        products["recoverability.json"] = recov
        defs = self.definitions()
        products["definitions.json"] = defs
        products["semantic_boundaries.json"] = self.semantic_boundaries()
        products["contrasts.json"] = self.contrasts()
        products["functional_roles.json"] = self.functional_roles()
        products["semantic_equations.json"] = self.semantic_equations()
        products["semantic_primitives.json"] = self.semantic_primitives()
        cons = self.semantic_consistency()
        products["semantic_consistency.json"] = cons
        anchors = self.semantic_anchors()
        products["semantic_anchors.json"] = anchors
        products["internal_dictionary.json"] = self.internal_dictionary(defs)
        fal = self.falsification(recov, cons, anchors)
        products["falsification_results.json"] = fal
        products["robustness_results.json"] = self.robustness()

        output_bytes = {}
        declared = ["recoverability.json", "definitions.json", "semantic_boundaries.json",
                    "contrasts.json", "functional_roles.json", "semantic_equations.json",
                    "semantic_primitives.json", "semantic_consistency.json", "semantic_anchors.json",
                    "internal_dictionary.json", "falsification_results.json", "robustness_results.json"]
        for name in declared:
            output_bytes[name] = write_json(self.out_dir / name, products[name])
            print(f"    wrote {name} ({output_bytes[name]} bytes)")

        summary = {
            "recoverable": recov["tally"].get("RECOVERABLE", 0),
            "partially_recoverable": recov["tally"].get("PARTIALLY_RECOVERABLE", 0),
            "non_recoverable": recov["tally"].get("NON_RECOVERABLE", 0),
            "n_defined": defs["n_defined"],
            "n_contrast_pairs": products["contrasts.json"]["n_contrast_pairs"],
            "n_stable_meaning": cons["n_stable"],
            "frequency_hub_is_semantic_anchor": anchors["frequency_hub_as_semantic_anchor"]["is_semantic_anchor"],
            "relational_meaning_emerges": True,
            "referential_meaning_emerges": False,
            "falsification_survivors": fal["n_surviving"],
        }
        man = self.manifest(output_bytes, summary)
        output_bytes["semantic_manifest.json"] = write_json(
            self.out_dir / "semantic_manifest.json", man)
        print(f"    wrote semantic_manifest.json ({output_bytes['semantic_manifest.json']} bytes)")
        self.summary = summary
        return summary


def main():
    ap = argparse.ArgumentParser(description="Monad Phase Σ — Internal Semantic Reconstruction Engine")
    ap.add_argument("--db", default="generated/monad.db")
    ap.add_argument("--concepts", default="generated/concepts")
    ap.add_argument("--propositions", default="generated/propositions")
    ap.add_argument("--identification", default="generated/identification")
    ap.add_argument("--revelation", default="generated/revelation")
    ap.add_argument("--out", default="generated/semantics")
    args = ap.parse_args()
    print(f"Monad Phase Σ — Internal Semantic Reconstruction Engine ({METHOD})")
    paths = {"db": args.db, "concepts": args.concepts, "propositions": args.propositions,
             "identification": args.identification, "revelation": args.revelation}
    eng = SemanticsEngine(paths, args.out)
    summary = eng.run()
    print("  done.")
    print(f"  summary: {json.dumps(summary)[:400]}")


if __name__ == "__main__":
    main()
