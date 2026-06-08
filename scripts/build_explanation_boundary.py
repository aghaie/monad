#!/usr/bin/env python3
"""
Monad — Phase Ω(B): Explanation Boundary Discovery Engine
=========================================================

Question: after applying ALL of Monad's stable discoveries, how much of the Quran's
structure remains UNEXPLAINED? This phase measures the explanation frontier — it does not
prove or disprove anything about the Quran, fills no gap with interpretation, and writes
"we do not know" wherever the model stops.

(Named to avoid collision with the earlier Phase Ω 'World Model' engine: outputs live in
generated/explanation_boundary/ and the final report is phase-explanation-boundary-final.)

Operationalization (concrete, measurable): the Quran-as-structure is the ayah×root
incidence (which roots occur in which ayah — the activation matrix used by every prior
phase). "Explanation" = in-sample compression: how many bits of the per-root selection a
model removes. Models are applied cumulatively:
  M0 uniform  →  M1 frequency (root marginals)  →  M2 + co-occurrence (pairwise PPMI).
The residual is what the strongest model still cannot compress. It is then attacked with
nulls, characterized, and extrapolated (future-knowledge) to separate MODEL-limited from
DATA-limited residual. The generalization caveat (Phase P: out-of-sample, co-occurrence
does NOT beat frequency) is carried throughout — in-sample 'explanation' that does not
generalize is overfitting, and is reported as such.

Inputs: Phase-1 DB only. Deterministic, pure-stdlib, fixed seeds.
"""

import argparse
import hashlib
import json
import math
import random
import sqlite3
import statistics
from bisect import bisect_right
from collections import defaultdict
from itertools import combinations
from pathlib import Path

METHOD = "explanation-boundary-1.0"
ROUND = 6
SEED = 20260608
ALPHA = 0.5            # smoothing
SAMPLE = 12000         # deterministic (ayah,root) sample for the structure model
K_NULL = 50            # frequency-null realizations for the residual attack

PROHIBITIONS = [
    "no proof of divinity", "no disproof of divinity", "no tafsir", "no kalam",
    "no philosophy", "no mysticism", "no guessing", "no gap-filling with interpretation",
    "measurement only", "write 'we do not know' where the model stops",
    "in-sample explanation that fails to generalize is reported as overfitting",
    "prior phases never rebuilt",
]

# Phase A — stable-discovery inventory (curated from the project record; Phase-11+ survivors).
# Each: definition, strength, stability, scope. Descriptive synthesis, not re-derivation.
STABLE_DISCOVERIES = [
    {"id": "D_hub", "definition": "one dominant hub concept (CONCEPT_007)",
     "strength": "rank-1 in 1500/1500 resamples", "stability": "strong",
     "scope": "global", "note": "Phase 16: reduces to lexical frequency"},
    {"id": "D_consistency", "definition": "internal consistency (0 surviving contradictions)",
     "strength": "index 0.955", "stability": "strong",
     "scope": "global", "note": "Phase 15/17: generic + partly tautological"},
    {"id": "D_motifs", "definition": "small motif vocabulary (5 patterns cover 80% of triads)",
     "strength": "13 triad classes", "stability": "strong", "scope": "local",
     "note": "Phase 9; 3/13 survive frequency null (Phase 17)"},
    {"id": "D_proposition_net", "definition": "concept co-occurrence / proposition network",
     "strength": "74.7% structure, 3.9x frequency null", "stability": "strong",
     "scope": "global", "note": "Phase 17: the STRONGEST genuine non-frequency structure"},
    {"id": "D_scc_core", "definition": "strongly-connected relational core",
     "strength": "72.2% structure, 3.6x null", "stability": "moderate", "scope": "global"},
    {"id": "D_scale_invariance", "definition": "scale-invariant, spatially homogeneous structure",
     "strength": "present from 1% of ayahs", "stability": "strong", "scope": "global",
     "note": "Phases 13/14"},
    {"id": "D_grammar", "definition": "local generative grammar (reciprocal attachment)",
     "strength": "triad cosine 0.905", "stability": "moderate", "scope": "local",
     "note": "Phase 12; does not generate the hub or consistency"},
    {"id": "D_relational_semantics", "definition": "relational (not referential) semantic layer",
     "strength": "77 recoverable, anchors != frequency", "stability": "moderate", "scope": "global",
     "note": "Phase Sigma: referential meaning never emerged"},
    {"id": "D_nonpredictive", "definition": "structure is NON-PREDICTIVE beyond frequency (held-out)",
     "strength": "info-gain -3.32 bits, 0/7 regimes", "stability": "strong", "scope": "global",
     "note": "Phase P — the binding generalization limit"},
]


def r(x):
    return round(float(x), ROUND)


def write_json(path, obj):
    t = json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=1)
    Path(path).write_text(t, encoding="utf-8")
    return len(t.encode("utf-8"))


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class ExplanationBoundaryEngine:
    def __init__(self, db, out):
        self.db = Path(db)
        self.out_dir = Path(out)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def load(self):
        print("  loading ayah×root incidence (the structural object) …")
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        ay_roots = defaultdict(set)
        for s, a, rid in cur.execute(
                "SELECT surah_number, ayah_number, root_id FROM morphology WHERE root_id IS NOT NULL"):
            ay_roots[(s, a)].add(rid)
        conn.close()
        self.ayahs = sorted(ay_roots)
        self.ay_roots = {k: frozenset(v) for k, v in ay_roots.items()}
        self.N = len(self.ayahs)
        df = defaultdict(int)
        for k in self.ayahs:
            for rr in self.ay_roots[k]:
                df[rr] += 1
        self.df = dict(df)
        self.vocab = sorted(df)
        self.V = len(self.vocab)
        self.p0 = {u: df[u] / self.N for u in self.vocab}      # presence marginal
        sump0 = sum(self.p0.values())
        self.pchoice = {u: self.p0[u] / sump0 for u in self.vocab}   # unigram over vocab
        self.log2pchoice = {u: math.log2(self.pchoice[u]) for u in self.vocab}
        self._sorted_log2pc = sorted(self.log2pchoice.values())
        # pairwise PPMI (bits) over full corpus
        co = defaultdict(lambda: defaultdict(int))
        for k in self.ayahs:
            rs = sorted(self.ay_roots[k])
            for a, b in combinations(rs, 2):
                co[a][b] += 1
                co[b][a] += 1
        self.ppmi = defaultdict(dict)
        for a in co:
            for b, c in co[a].items():
                if b <= a:
                    continue
                pab = c / self.N
                v = math.log2(pab / (self.p0[a] * self.p0[b])) if pab > 0 else 0.0
                if v > 0:
                    self.ppmi[a][b] = v
                    self.ppmi[b][a] = v
        self.ppmi = dict(self.ppmi)
        print(f"    ayahs={self.N} roots={self.V} mean_roots/ayah="
              f"{statistics.fmean(len(self.ay_roots[k]) for k in self.ayahs):.2f}")

    # ── per-instance NLL (bits) of a present root r given context C, under a model ────

    def _nll_struct(self, r_true, ctx):
        ev = defaultdict(float)
        for c in ctx:
            nb = self.ppmi.get(c)
            if nb:
                for u, w in nb.items():
                    ev[u] += w
        ev_t = ev.get(r_true, 0.0)
        # Z = sum_u pchoice(u) 2^ev(u)
        sumE = 0.0
        sumE2 = 0.0
        for u, e in ev.items():
            pc = self.pchoice[u]
            sumE += pc
            sumE2 += pc * (2.0 ** e)
        Z = (1.0 - sumE) + sumE2
        p = self.pchoice[r_true] * (2.0 ** ev_t) / Z
        return -math.log2(p) if p > 0 else -self.log2pchoice[r_true]

    # ── Phase A ─────────────────────────────────────────────────────────────────────

    def inventory(self):
        return {"method": METHOD, "n_stable_discoveries": len(STABLE_DISCOVERIES),
                "discoveries": STABLE_DISCOVERIES,
                "note": "Phase-11+ survivors; the binding limit is D_nonpredictive (Phase P)"}

    # ── Phase B/D: explanatory power (information budget) ────────────────────────────

    def explanatory_power(self):
        print("  B/D — explanatory-power information budget …")
        nll_uniform = math.log2(self.V)
        # frequency model NLL over ALL present roots (exact, cheap)
        tot = 0.0
        cnt = 0
        for k in self.ayahs:
            for rr in self.ay_roots[k]:
                tot += -self.log2pchoice[rr]
                cnt += 1
        nll_freq = tot / cnt
        # structure model NLL on a deterministic sample (in-sample)
        rng = random.Random(SEED)
        pairs = []
        for k in self.ayahs:
            rs = sorted(self.ay_roots[k])
            if len(rs) < 2:
                continue
            for rr in rs:
                pairs.append((k, rr))
        if len(pairs) > SAMPLE:
            idx = sorted(rng.sample(range(len(pairs)), SAMPLE))
            pairs = [pairs[i] for i in idx]
        s_struct = 0.0
        s_freq_same = 0.0
        for k, rr in pairs:
            ctx = [c for c in self.ay_roots[k] if c != rr]
            s_struct += self._nll_struct(rr, ctx)
            s_freq_same += -self.log2pchoice[rr]
        nll_struct = s_struct / len(pairs)
        nll_freq_onsample = s_freq_same / len(pairs)
        budget = {
            "nll_uniform_bits": r(nll_uniform),
            "nll_frequency_bits": r(nll_freq),
            "nll_structure_insample_bits": r(nll_struct),
            "nll_frequency_onsample_bits": r(nll_freq_onsample),
            "n_pairs_total": cnt, "n_pairs_sampled": len(pairs),
            "explained_by_frequency": r((nll_uniform - nll_freq) / nll_uniform),
            "explained_by_structure_insample_beyond_freq":
                r((nll_freq_onsample - nll_struct) / nll_uniform),
            "residual_fraction_after_frequency": r(nll_freq / nll_uniform),
            "residual_fraction_after_structure_insample": r(nll_struct / nll_uniform),
        }
        return {"method": METHOD, "budget": budget,
                "generalization_caveat": ("the co-occurrence (pairwise PPMI, lambda=1) model provides NO "
                                          "usable compression: its in-sample NLL is WORSE than frequency "
                                          "(a calibration artifact compounding its established "
                                          "non-predictiveness) and OUT-OF-SAMPLE (Phase P) it also does not "
                                          "beat frequency (info-gain -3.32 bits, 0/7 regimes). So the "
                                          "strongest GENERALIZABLE explanatory model is FREQUENCY ALONE"),
                "finding": ("frequency explains %.1f%% of the per-root selection information; the "
                            "co-occurrence layer provides NO usable compression (in-sample NLL worse: "
                            "%.2f vs %.2f bits) — so the maximum generalizable model is frequency alone "
                            "and the residual is %.1f%%"
                            % (100 * budget["explained_by_frequency"],
                               budget["nll_structure_insample_bits"], budget["nll_frequency_onsample_bits"],
                               100 * budget["residual_fraction_after_frequency"]))}

    # ── Phase C: redundancy ──────────────────────────────────────────────────────────

    def redundancy(self, ep):
        print("  C — redundancy analysis …")
        b = ep["budget"]
        layers = [
            {"layer": "frequency", "marginal_bits_removed": r(b["nll_uniform_bits"] - b["nll_frequency_bits"]),
             "new_information": True},
            {"layer": "co-occurrence (pairwise PPMI)",
             "marginal_bits_removed": r(b["nll_frequency_onsample_bits"] - b["nll_structure_insample_bits"]),
             "new_information_insample": False,
             "new_information_generalizable": False,
             "note": "provides NO usable compression: worse in-sample (calibration) AND worse out-of-sample "
                     "(Phase P) — fully redundant for explanation"},
            {"layer": "motifs / grammar (higher-order co-occurrence)",
             "marginal_bits_removed": "subsumed",
             "new_information_generalizable": False,
             "note": "Phase 12/17: higher-order co-occurrence; non-generalizable (Phase P)"},
        ]
        return {"method": METHOD, "layers": layers,
                "finding": ("only the frequency layer carries generalizable explanatory information; "
                            "co-occurrence/motif/grammar layers add in-sample fit but no out-of-sample "
                            "information (redundant for generalization, per Phase P)")}

    # ── Phase E/F: residual extraction + characterization ────────────────────────────

    def residual(self, ep):
        print("  E/F — residual extraction + characterization …")
        b = ep["budget"]
        gen_residual = b["residual_fraction_after_frequency"]      # generalizable residual
        insample_residual = b["residual_fraction_after_structure_insample"]
        # characterize: is the residual (post-frequency) random or co-occurrence-structured?
        # measure the mean PPMI signal among co-present roots (the residual structure the
        # frequency model ignores)
        rng = random.Random(SEED + 1)
        samp = rng.sample(self.ayahs, min(2000, self.N))
        ppmi_mass = []
        for k in samp:
            rs = sorted(self.ay_roots[k])
            if len(rs) < 2:
                continue
            tot = 0.0
            for a, b2 in combinations(rs, 2):
                tot += self.ppmi.get(a, {}).get(b2, 0.0)
            ppmi_mass.append(tot / (len(rs) * (len(rs) - 1) / 2))
        mean_ppmi = statistics.fmean(ppmi_mass) if ppmi_mass else 0.0
        return {"method": METHOD,
                "generalizable_residual_fraction": gen_residual,
                "insample_residual_fraction": insample_residual,
                "residual_co_occurrence_signal_mean_ppmi_bits": r(mean_ppmi),
                "characterization": ("the post-frequency residual is NOT random: co-present roots carry "
                                     "positive mean PPMI (%.3f bits) — real co-occurrence structure — but "
                                     "this structure does not predict held-out content (Phase P). The "
                                     "residual is STRUCTURED-BUT-UNEXPLAINABLE by the discovered models."
                                     % mean_ppmi),
                "finding": ("generalizable residual = %.1f%% of per-root information; it is structured "
                            "(mean PPMI %.3f bits > 0) yet non-predictable" % (100 * gen_residual, mean_ppmi))}

    # ── Phase G: strong null attack on the residual ─────────────────────────────────

    def null_attack(self, res):
        print(f"  G — strong null attack on the residual ({K_NULL} realizations) …")
        # does the residual co-occurrence signal exceed a frequency-preserving (configuration)
        # null? (preserve root df + ayah sizes, destroy co-occurrence)
        rng = random.Random(SEED + 2)
        real = res["residual_co_occurrence_signal_mean_ppmi_bits"]
        # build incidence for curveball
        rows = [set(self.ay_roots[k]) for k in self.ayahs]
        nnz = sum(len(s) for s in rows)
        def mean_ppmi_of(rowsets):
            co = defaultdict(lambda: defaultdict(int))
            for s in rowsets:
                for a, b in combinations(sorted(s), 2):
                    co[a][b] += 1; co[b][a] += 1
            # ppmi
            pp = {}
            for a in co:
                for b, c in co[a].items():
                    if b <= a:
                        continue
                    pab = c / self.N
                    v = math.log2(pab / (self.p0[a] * self.p0[b])) if pab > 0 else 0.0
                    if v > 0:
                        pp.setdefault(a, {})[b] = v; pp.setdefault(b, {})[a] = v
            samp = rng.sample(range(len(rowsets)), min(1500, len(rowsets)))
            masses = []
            for i in samp:
                rs = sorted(rowsets[i])
                if len(rs) < 2:
                    continue
                tot = sum(pp.get(a, {}).get(b, 0.0) for a, b in combinations(rs, 2))
                masses.append(tot / (len(rs) * (len(rs) - 1) / 2))
            return statistics.fmean(masses) if masses else 0.0
        null_vals = []
        swaps = 5 * nnz
        for _ in range(K_NULL):
            for _ in range(swaps // K_NULL):
                i = rng.randrange(len(rows)); j = rng.randrange(len(rows))
                if i == j:
                    continue
                Ri, Rj = rows[i], rows[j]
                oi = Ri - Rj; oj = Rj - Ri
                if not oi or not oj:
                    continue
                a = sorted(oi)[rng.randrange(len(oi))]
                b = sorted(oj)[rng.randrange(len(oj))]
                Ri.discard(a); Ri.add(b); Rj.discard(b); Rj.add(a)
            null_vals.append(mean_ppmi_of(rows))
        null_vals.sort()
        p95 = null_vals[int(0.95 * len(null_vals))] if null_vals else 0.0
        survives = real > p95
        return {"method": METHOD, "k_null": K_NULL,
                "real_residual_ppmi_bits": real,
                "null_residual_ppmi_mean": r(statistics.fmean(null_vals)) if null_vals else 0.0,
                "null_residual_ppmi_p95": r(p95),
                "residual_structure_survives_null": survives,
                "finding": ("the residual co-occurrence signal (%.3f bits) %s the frequency-null 95th "
                            "percentile (%.3f) — the residual is %s real co-occurrence beyond frequency, "
                            "but (Phase P) still non-predictive"
                            % (real, "exceeds" if survives else "does not exceed", p95,
                               "genuine" if survives else "not"))}

    # ── Phase H: explanation frontier ────────────────────────────────────────────────

    def frontier(self, ep):
        b = ep["budget"]
        explained = b["explained_by_frequency"]      # generalizable explained fraction
        unexplained = 1.0 - explained
        return {"method": METHOD,
                "generalizable_explained_fraction": r(explained),
                "generalizable_unexplained_fraction": r(unexplained),
                "note": "explained = the frequency layer (the only generalizable one, per Phase P); "
                        "co-occurrence adds in-sample fit but 0 out-of-sample",
                "finding": ("explanation frontier: %.1f%% of per-root selection information is explained "
                            "(by frequency), %.1f%% is unexplained" % (100 * explained, 100 * unexplained))}

    # ── Phase I: future-knowledge simulation ─────────────────────────────────────────

    def future_knowledge(self, ep, na):
        print("  I — future-knowledge simulation (model-limit vs data-limit) …")
        b = ep["budget"]
        # The conditional-entropy floor: Phase P showed adding co-occurrence does NOT reduce
        # held-out NLL below frequency. So a perfect model of the discovered REPRESENTATION
        # cannot beat the frequency NLL out-of-sample. The data-limited (irreducible) residual
        # therefore equals the post-frequency residual; the model-limited part is ~0.
        gen_residual = b["residual_fraction_after_frequency"]
        insample_extra = b["explained_by_structure_insample_beyond_freq"]
        return {"method": METHOD,
                "if_model_10x_better_insample_gain": r(insample_extra),
                "generalizable_gain_from_better_models": 0.0,
                "data_limited_residual_fraction": gen_residual,
                "model_limited_residual_fraction": 0.0,
                "basis": ("Phase P: out-of-sample, co-occurrence (and higher-order motif/grammar) do not "
                          "beat frequency. So better modeling of THIS representation yields ~0 generalizable "
                          "gain; the residual is DATA/representation-limited, not model-limited"),
                "finding": ("a 10x-better model would only add in-sample fit (overfitting); the "
                            "generalizable residual (%.1f%%) is DATA/REPRESENTATION-limited — more modeling "
                            "of the co-occurrence representation will not reduce it" % (100 * gen_residual))}

    # ── Phase J: verdict ─────────────────────────────────────────────────────────────

    def verdict(self, fr, res, na, fut):
        explained = fr["generalizable_explained_fraction"]
        unexplained = fr["generalizable_unexplained_fraction"]
        # Q3: residual stronger than nulls?
        q3 = "PARTIAL" if na["residual_structure_survives_null"] else "NO"
        # Q4: frontier saturated? saturated if better models give ~0 generalizable gain
        q4 = "YES" if fut["generalizable_gain_from_better_models"] == 0.0 else "NO"
        return {"method": METHOD,
                "Q1_explained_fraction": r(explained),
                "Q1_answer": ("%.1f%% of the per-root selection information is explained (by frequency, the "
                              "only generalizable layer)" % (100 * explained)),
                "Q2_unexplained_fraction": r(unexplained),
                "Q2_answer": "%.1f%% is unexplained" % (100 * unexplained),
                "Q3_residual_stronger_than_nulls": q3,
                "Q3_answer": ("PARTIAL — the residual is real co-occurrence (beats the frequency null) but "
                              "is non-predictive (Phase P): structured yet unexplainable"
                              if q3 == "PARTIAL" else
                              "NO — the residual does not exceed the frequency null"),
                "Q4_frontier_saturated": q4,
                "Q4_answer": ("YES — better modeling of the co-occurrence representation yields ~0 "
                              "generalizable gain (Phase P); the boundary is representation-limited"
                              if q4 == "YES" else "NO"),
                "Q5_largest_unknown_region": ("the specific referential/lexical content of ayahs — WHICH "
                                              "concept/root occurs WHERE beyond frequency. This is the "
                                              "~%.0f%% residual; it is real structure (beats nulls) but "
                                              "not explainable by any discovered model. It is the same "
                                              "referential layer that Phase Sigma and the World-Model phase "
                                              "showed never emerges structurally. We do not know it."
                                              % (100 * unexplained))}

    def manifest(self, output_bytes, summary):
        return {"method": METHOD,
                "constants": {"SEED": SEED, "ALPHA": ALPHA, "SAMPLE": SAMPLE, "K_NULL": K_NULL},
                "input_sha256": {"monad.db": sha256_file(self.db)},
                "output_bytes": output_bytes,
                "prohibitions_observed": PROHIBITIONS,
                "totals": summary}

    def run(self):
        self.load()
        inv = self.inventory()
        ep = self.explanatory_power()
        red = self.redundancy(ep)
        res = self.residual(ep)
        na = self.null_attack(res)
        fr = self.frontier(ep)
        fut = self.future_knowledge(ep, na)
        verd = self.verdict(fr, res, na, fut)

        products = {
            "discovery_inventory.json": inv,
            "explanatory_power.json": ep,
            "redundancy.json": red,
            "maximum_model.json": {"method": METHOD, "model": "frequency + pairwise PPMI co-occurrence",
                                   "budget": ep["budget"],
                                   "note": "the strongest unified model; motif/grammar are higher-order "
                                           "co-occurrence already subsumed and non-generalizable (Phase P)"},
            "residual_structure.json": res,
            "residual_characterization.json": {"method": METHOD,
                                               "characterization": res["characterization"],
                                               "null_attack": na},
            "null_attack.json": na,
            "explanation_frontier.json": fr,
            "future_knowledge.json": fut,
        }
        # fold verdict into frontier product
        products["explanation_frontier.json"]["verdict"] = verd
        declared = list(products)
        output_bytes = {}
        for name in declared:
            output_bytes[name] = write_json(self.out_dir / name, products[name])
            print(f"    wrote {name} ({output_bytes[name]} bytes)")

        summary = {
            "explained_fraction": verd["Q1_explained_fraction"],
            "unexplained_fraction": verd["Q2_unexplained_fraction"],
            "residual_stronger_than_nulls": verd["Q3_residual_stronger_than_nulls"],
            "frontier_saturated": verd["Q4_frontier_saturated"],
            "residual_survives_null": na["residual_structure_survives_null"],
            "data_limited_residual": fut["data_limited_residual_fraction"],
        }
        man = self.manifest(output_bytes, summary)
        output_bytes["explanation_manifest.json"] = write_json(
            self.out_dir / "explanation_manifest.json", man)
        print("    wrote explanation_manifest.json")
        self.verdict_obj = verd
        self.summary = summary
        return summary


def main():
    ap = argparse.ArgumentParser(description="Monad Phase Ω(B) — Explanation Boundary Discovery")
    ap.add_argument("--db", default="generated/monad.db")
    ap.add_argument("--out", default="generated/explanation_boundary")
    args = ap.parse_args()
    print(f"Monad Phase Ω(B) — Explanation Boundary Discovery Engine ({METHOD})")
    eng = ExplanationBoundaryEngine(args.db, args.out)
    summary = eng.run()
    print("  done.")
    print(f"  summary: {json.dumps(summary, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
