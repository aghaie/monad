#!/usr/bin/env python3
"""
Monad — Phase P: Structural Predictivity / Held-Out Information Engine
=====================================================================

The first GENERALIZATION test in the project. Every prior phase was descriptive on the
full corpus. Phase P asks the one question that separates a genuine discovery from an
elaborate redescription:

    Does the structure Monad discovered carry PREDICTIVE information about held-out
    Quranic content that lexical frequency alone does NOT?

Method (see docs/*-report.md for the full design): masked-unit completion under
leakage-free, whole-ayah holdout. For a held-out ayah, mask a unit (root, or concept)
and predict it from the remaining context using ONLY training-ayah statistics. A
context-blind frequency baseline (B0) is the bar; a context-aware structure model (S1)
must beat it AND must beat a frequency-preserving configuration null (N). The structure
model is an additive extension of the baseline (P1 = P0 when there is no association
evidence), so any win is attributable to relational information by construction.

This engine optimizes for TRUTH, not for a positive result. The pre-registered decision
criteria (§9 of the spec) are fixed below as constants and evaluated mechanically; a
negative outcome is a first-class result and is reported as such.

Inputs: the Quran corpus (Phase-1 DB) + Phase-3 concept memberships (secondary test).
Deterministic, pure-stdlib, fixed seeds. The manifest is byte-identical reproducible;
volatile provenance (timestamp, git hash, runtime) lives in a separate run_metadata.json.
"""

import argparse
import hashlib
import json
import math
import os
import platform
import random
import sqlite3
import statistics
import subprocess
import time
from bisect import bisect_right
from collections import defaultdict
from itertools import combinations
from pathlib import Path

METHOD = "predictivity-discovery-1.0"
ROUND = 6

# ── pre-registered constants (FIXED before any run — §9; no tuning after results) ──
SEED = 20260607
ALPHA = 0.5                # add-α smoothing for the unigram prior P0
LAMBDA = 1.0               # PPMI feature weight in the log-linear structure model (fixed)
K_NULL = 30               # frequency-null configuration realizations
FOLDS_PRIMARY = 5
FOLDS_ROBUST = 10
FORWARD_SPLITS = [0.25, 0.50, 0.75]
N_BLOCKS = 5              # contiguous-block folds (R2)
BOOT = 1000               # bootstrap resamples for the primary decision cell
NULL_EVAL_CAP = 8000      # deterministic instance sample size for null evaluation
SWAP_MULT = 5             # curveball swaps per edge, per null realization
# pre-registered minimum meaningful effect (anti-triviality floor)
MIN_BITS_GAIN = 0.05      # predictive information gain, bits/unit
MIN_HITS10_GAIN = 0.02    # absolute Hits@10 improvement over B0
CI_Z = 1.959963984540054  # 95% normal z

PROHIBITIONS = [
    "no external source", "no tafsir/translation/dictionary/theology", "no ML library",
    "no pretrained embedding", "leakage-free: whole-ayah holdout, training-only statistics",
    "fair baseline: structure==baseline when association evidence is zero",
    "frequency-null control is decisive (criterion 2)", "units stay opaque",
    "no prior result protected", "pre-registered thresholds, no post-hoc tuning",
    "negative outcome is a first-class result", "optimize for truth not for success",
    "prior phases never rebuilt",
]

VERDICTS = ["GENUINE_STRUCTURE", "FREQUENCY_SHAPED", "NON_PREDICTIVE",
            "ORDER_ONLY", "CO_PRESENCE_ONLY"]


def r(x):
    return round(float(x), ROUND)


def write_json(path, obj):
    text = json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=1)
    Path(path).write_text(text, encoding="utf-8")
    return len(text.encode("utf-8"))


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ── training statistics over a set of training ayahs (leakage-free) ─────────────────

class TrainStats:
    """Document-frequency, pairwise co-occurrence, PPMI, unigram prior — all from the
    training ayahs ONLY. Units are integer ids (root_id or concept index)."""

    def __init__(self, train_unitsets):
        # train_unitsets: list of frozensets of unit ids (one per training ayah)
        self.n_ayahs = len(train_unitsets)
        df = defaultdict(int)
        co = defaultdict(lambda: defaultdict(int))
        for us in train_unitsets:
            for u in us:
                df[u] += 1
            for a, b in combinations(sorted(us), 2):
                co[a][b] += 1
                co[b][a] += 1
        self.df = dict(df)
        self.vocab = sorted(df)
        self.V = len(self.vocab)
        T = sum(df.values())
        self.T = T
        # unigram prior P0(u) = (df+α)/(T+αV) in probability; log2 for scoring
        denom = T + ALPHA * self.V
        self.p0 = {u: (df[u] + ALPHA) / denom for u in self.vocab}
        self.log2p0 = {u: math.log2(self.p0[u]) for u in self.vocab}
        # degree baseline (number of distinct co-occurrence partners)
        self.degree = {u: len(co[u]) for u in self.vocab}
        # min-rank (ties share the optimistic rank) — used IDENTICALLY for base, degree,
        # and structure so the predictors are tie-convention-symmetric (fairness)
        self._sorted_deg = sorted(self.degree.values())
        # positive-PPMI neighbour weights (bits): ppmi[c][u]
        self.ppmi = defaultdict(dict)
        for a in co:
            for b, c_ab in co[a].items():
                if b <= a:
                    continue
                p_ab = c_ab / self.n_ayahs
                p_a = df[a] / self.n_ayahs
                p_b = df[b] / self.n_ayahs
                val = math.log2(p_ab / (p_a * p_b)) if p_ab > 0 and p_a > 0 and p_b > 0 else 0.0
                if val > 0:
                    w = LAMBDA * val
                    self.ppmi[a][b] = w
                    self.ppmi[b][a] = w
        self.ppmi = {k: v for k, v in self.ppmi.items()}
        # sorted log2p0 values for fast non-evidence rank counting
        self._sorted_log2p0 = sorted(self.log2p0.values())

        # directional (ordered) PPMI for S2: built lazily via set_directional()
        self.dir_ppmi = None

    def set_directional(self, ordered_pairs_counts, before_counts):
        """ordered_pairs_counts[(a,b)] = #train ayahs where a appears before b.
        Directional association uses asymmetry; built once per fold if S2 requested."""
        self.dir_ppmi = ordered_pairs_counts  # already-weighted dict (a,b)->w

    def count_higher_log2p0(self, threshold):
        # number of vocab units with log2p0 strictly greater than threshold
        return self.V - bisect_right(self._sorted_log2p0, threshold)

    def count_higher_deg(self, d):
        # number of vocab units with degree strictly greater than d
        return self.V - bisect_right(self._sorted_deg, d)


def score_instance(ts, context, true_u):
    """Return per-instance prediction stats for B0 (frequency), B1 (degree),
    S1 (PPMI structure). context: list of training-vocab unit ids; true_u: id.
    Assumes true_u in ts.vocab (OOV handled by caller). Fair-by-construction:
    structure score = prior + evidence; evidence=0 -> equals baseline."""
    log2p0 = ts.log2p0
    base_s = log2p0[true_u]
    # evidence accumulation over context (sparse)
    ev = defaultdict(float)
    for c in context:
        nb = ts.ppmi.get(c)
        if nb:
            for u, w in nb.items():
                ev[u] += w
    ev_true = ev.get(true_u, 0.0)
    struct_s = base_s + ev_true

    # ---- NLL (bits) under base and structure (normalized over vocab) ----
    nll_base = -base_s
    # Z_struct = sum_u p0(u) * 2^ev(u) = (1 - sum_E p0) + sum_E p0*2^ev
    sum_E_p0 = 0.0
    sum_E_p0_2ev = 0.0
    for u, e in ev.items():
        p0u = ts.p0[u]
        sum_E_p0 += p0u
        sum_E_p0_2ev += p0u * (2.0 ** e)
    z_struct = (1.0 - sum_E_p0) + sum_E_p0_2ev
    p_struct_true = ts.p0[true_u] * (2.0 ** ev_true) / z_struct
    nll_struct = -math.log2(p_struct_true) if p_struct_true > 0 else nll_base

    # ---- ranks (1 = best); min-rank tie convention, IDENTICAL across predictors ----
    rank_base = 1 + ts.count_higher_log2p0(base_s)
    rank_deg = 1 + ts.count_higher_deg(ts.degree[true_u])
    # struct rank: count units with struct score strictly greater than struct_s
    higher = 0
    # among evidence units E (exact)
    e_higher_log2p0 = 0
    for u, e in ev.items():
        su = log2p0[u] + e
        if u != true_u and su > struct_s:
            higher += 1
        if log2p0[u] > struct_s:
            e_higher_log2p0 += 1
    # among non-evidence units: score = log2p0; count log2p0 > struct_s, minus those in E
    nonE_higher = ts.count_higher_log2p0(struct_s) - e_higher_log2p0
    # true_u: if not in E it was counted in count_higher_log2p0 iff log2p0[true_u]>struct_s
    if true_u not in ev and log2p0[true_u] > struct_s:
        nonE_higher -= 1
    rank_struct = 1 + higher + nonE_higher

    return {
        "nll_base": nll_base, "nll_struct": nll_struct,
        "rank_base": rank_base, "rank_struct": rank_struct, "rank_deg": rank_deg,
        "V": ts.V,
    }


def score_instance_null(ts_null, context, true_u):
    """NLL + rank for true_u under a null TrainStats (same p0/vocab as real, null PPMI).
    Only needs struct metrics (the null's predictive power)."""
    if true_u not in ts_null.vocab:
        return None
    return score_instance(ts_null, context, true_u)


# ── metric aggregation ──────────────────────────────────────────────────────────────

def aggregate(instances):
    """instances: list of dicts from score_instance. Returns aggregate metrics."""
    n = len(instances)
    if n == 0:
        return {"n_instances": 0}
    rr_base = [1.0 / x["rank_base"] for x in instances]
    rr_str = [1.0 / x["rank_struct"] for x in instances]
    rr_deg = [1.0 / x["rank_deg"] for x in instances]
    def hits(ranks, k):
        return sum(1 for r_ in ranks if r_ <= k) / n
    rb = [x["rank_base"] for x in instances]
    rs = [x["rank_struct"] for x in instances]
    rd = [x["rank_deg"] for x in instances]
    nb = [x["nll_base"] for x in instances]
    nsr = [x["nll_struct"] for x in instances]
    gains = [x["nll_base"] - x["nll_struct"] for x in instances]   # bits/unit, paired
    Vmean = statistics.fmean(x["V"] for x in instances)
    out = {
        "n_instances": n,
        "mrr_base": r(statistics.fmean(rr_base)),
        "mrr_struct": r(statistics.fmean(rr_str)),
        "mrr_degree": r(statistics.fmean(rr_deg)),
        "hits1_base": r(hits(rb, 1)), "hits1_struct": r(hits(rs, 1)),
        "hits5_base": r(hits(rb, 5)), "hits5_struct": r(hits(rs, 5)),
        "hits10_base": r(hits(rb, 10)), "hits10_struct": r(hits(rs, 10)),
        "hits10_degree": r(hits(rd, 10)),
        "mean_rankpct_base": r(statistics.fmean(rb) / Vmean),
        "mean_rankpct_struct": r(statistics.fmean(rs) / Vmean),
        "ppl_base": r(2.0 ** statistics.fmean(nb)),
        "ppl_struct": r(2.0 ** statistics.fmean(nsr)),
        "mean_nll_base": r(statistics.fmean(nb)),
        "mean_nll_struct": r(statistics.fmean(nsr)),
        "info_gain_bits": r(statistics.fmean(gains)),
        "vocab_mean": r(Vmean),
    }
    # SE-based 95% CI for info_gain (paired)
    if n > 1:
        sd = statistics.stdev(gains)
        se = sd / math.sqrt(n)
        out["info_gain_ci_lo"] = r(out["info_gain_bits"] - CI_Z * se)
        out["info_gain_ci_hi"] = r(out["info_gain_bits"] + CI_Z * se)
        # MRR struct-minus-base paired
        d = [a - b for a, b in zip(rr_str, rr_base)]
        sed = statistics.stdev(d) / math.sqrt(n)
        out["mrr_gain"] = r(statistics.fmean(d))
        out["mrr_gain_ci_lo"] = r(out["mrr_gain"] - CI_Z * sed)
        out["mrr_gain_ci_hi"] = r(out["mrr_gain"] + CI_Z * sed)
    return out


def bootstrap_gain(gains, rng, B):
    """Bootstrap 95% CI of the mean of `gains` (paired info-gain)."""
    n = len(gains)
    if n == 0:
        return (0.0, 0.0)
    means = []
    for _ in range(B):
        s = 0.0
        for _ in range(n):
            s += gains[rng.randrange(n)]
        means.append(s / n)
    means.sort()
    lo = means[int(0.025 * B)]
    hi = means[int(0.975 * B)]
    return (r(lo), r(hi))


class PredictivityEngine:
    def __init__(self, db, concepts_path, out):
        self.db = Path(db)
        self.concepts_path = Path(concepts_path)
        self.out_dir = Path(out)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.t0 = time.time()

    def load(self):
        print("  loading corpus: ayah root-sets (with order) + concept memberships …")
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        seq_surah = {}
        seq_minpos = defaultdict(dict)   # seq -> {root_id: min word_position}
        for s, seq, wp, rid in cur.execute(
                "SELECT a.surah_number, a.ayah_sequential, m.word_position, m.root_id "
                "FROM ayahs a JOIN morphology m "
                "ON a.surah_number=m.surah_number AND a.ayah_number=m.ayah_number "
                "WHERE m.root_id IS NOT NULL"):
            seq_surah[seq] = s
            d = seq_minpos[seq]
            if rid not in d or wp < d[rid]:
                d[rid] = wp
        conn.close()
        self.seq_surah = seq_surah
        self.seqs = sorted(seq_minpos)
        # root unit-set per ayah (ids) + ordered list by position
        self.ayah_roots = {seq: frozenset(seq_minpos[seq]) for seq in self.seqs}
        self.ayah_root_order = {seq: [r_ for r_, _ in sorted(seq_minpos[seq].items(),
                                                             key=lambda kv: kv[1])]
                                for seq in self.seqs}
        # concept memberships: root_id -> set(concept_idx)
        cm = json.loads(self.concepts_path.read_text(encoding="utf-8"))
        concept_ids = sorted(cm["concepts"].keys())
        self.concept_index = {c: i for i, c in enumerate(concept_ids)}
        root2concepts = defaultdict(set)
        for rid_str, lst in cm["root_memberships"].items():
            rid = int(rid_str)
            for e in lst:
                root2concepts[rid].add(self.concept_index[e["concept_id"]])
        self.root2concepts = root2concepts
        # concept unit-set per ayah (frozen full-corpus memberships = variant 2a)
        self.ayah_concepts = {}
        for seq in self.seqs:
            cs = set()
            for rid in self.ayah_roots[seq]:
                x = root2concepts.get(rid)
                if x:
                    cs |= x
            self.ayah_concepts[seq] = frozenset(cs)
        print(f"    ayahs={len(self.seqs)} roots/ayah(mean)="
              f"{statistics.fmean(len(self.ayah_roots[s]) for s in self.seqs):.2f} "
              f"concepts={len(concept_ids)}")

    # ── fold builders (return list of (name, train_seqs, test_seqs)) ────────────────

    def folds_random(self, k):
        rng = random.Random(SEED + k)
        shuffled = self.seqs[:]
        rng.shuffle(shuffled)
        folds = [shuffled[i::k] for i in range(k)]
        out = []
        for i in range(k):
            test = set(folds[i])
            train = [s for s in self.seqs if s not in test]
            out.append((f"R1_k{k}_fold{i}", train, sorted(test)))
        return out

    def folds_blocks(self, k):
        # contiguous by ayah_sequential, k blocks
        n = len(self.seqs)
        out = []
        for i in range(k):
            lo = i * n // k
            hi = (i + 1) * n // k
            test = set(self.seqs[lo:hi])
            train = [s for s in self.seqs if s not in test]
            out.append((f"R2_block{i}", train, sorted(test)))
        return out

    def folds_forward(self, frac):
        n = len(self.seqs)
        cut = int(frac * n)
        train = self.seqs[:cut]
        test = self.seqs[cut:]
        return [(f"R3_fwd{int(frac*100)}", train, test)]

    def folds_length_strat(self, k):
        # stratify by distinct-root count, assign round-robin within strata
        by_len = sorted(self.seqs, key=lambda s: (len(self.ayah_roots[s]), s))
        rng = random.Random(SEED + 999)
        folds = [[] for _ in range(k)]
        for i, s in enumerate(by_len):
            folds[i % k].append(s)
        out = []
        for i in range(k):
            test = set(folds[i])
            train = [s for s in self.seqs if s not in test]
            out.append((f"R4_lenfold{i}", train, sorted(test)))
        return out

    # ── instance generation (masked-unit completion) ────────────────────────────────

    def gen_instances(self, test_seqs, ayah_units, mask_mode):
        """Yield (context_list, true_unit) for each masked unit. Leakage-free: context
        from the test ayah, prediction stats supplied by caller (training only)."""
        inst = []
        for seq in test_seqs:
            U = sorted(ayah_units[seq])
            n = len(U)
            if n < 2:
                continue
            if mask_mode == "single":
                for i in range(n):
                    true_u = U[i]
                    ctx = U[:i] + U[i + 1:]
                    inst.append((ctx, true_u, seq))
            else:
                frac = 0.25 if mask_mode == "p25" else 0.50
                kk = max(1, round(frac * n))
                rng = random.Random((SEED ^ seq) & 0x7fffffff)
                M = set(rng.sample(U, kk))
                ctx = [u for u in U if u not in M]
                if not ctx:
                    continue
                for true_u in sorted(M):
                    inst.append((ctx, true_u, seq))
        return inst

    # ── evaluate a single (fold-set, units, mask) cell ──────────────────────────────

    def eval_cell(self, foldset, ayah_units, mask_mode, want_boot=False):
        all_inst = []
        oov = 0
        for name, train_seqs, test_seqs in foldset:
            train_unitsets = [ayah_units[s] for s in train_seqs]
            ts = TrainStats(train_unitsets)
            vocab = set(ts.vocab)
            for ctx, true_u, seq in self.gen_instances(test_seqs, ayah_units, mask_mode):
                if true_u not in vocab:
                    oov += 1
                    continue
                c2 = [c for c in ctx if c in vocab]
                all_inst.append(score_instance(ts, c2, true_u))
        agg = aggregate(all_inst)
        agg["oov_excluded"] = oov
        agg["coverage"] = r(len(all_inst) / (len(all_inst) + oov)) if (len(all_inst) + oov) else 0.0
        if want_boot and all_inst:
            gains = [x["nll_base"] - x["nll_struct"] for x in all_inst]
            rng = random.Random(SEED + 7)
            lo, hi = bootstrap_gain(gains, rng, BOOT)
            agg["info_gain_boot_ci_lo"] = lo
            agg["info_gain_boot_ci_hi"] = hi
            agg["bootstrap_resamples"] = BOOT
        return agg

    # ── frequency-null control for a cell (criterion 2) ─────────────────────────────

    def _null_unitsets(self, train_unitsets, rng):
        """Configuration null: preserve each ayah's size and each unit's df, destroy
        co-occurrence, via curveball (checkerboard) swaps on the incidence."""
        # build incidence as list of sets (mutable) + unit positions
        rows = [set(us) for us in train_unitsets]
        nnz = sum(len(s) for s in rows)
        swaps = SWAP_MULT * nnz
        nrow = len(rows)
        for _ in range(swaps):
            i = rng.randrange(nrow)
            j = rng.randrange(nrow)
            if i == j:
                continue
            Ri, Rj = rows[i], rows[j]
            only_i = Ri - Rj
            only_j = Rj - Ri
            if not only_i or not only_j:
                continue
            a = rng.choice(tuple(only_i))
            b = rng.choice(tuple(only_j))
            # swap: i gives a takes b ; j gives b takes a (preserves row sizes + col sums)
            Ri.discard(a); Ri.add(b)
            Rj.discard(b); Rj.add(a)
        return [frozenset(s) for s in rows]

    def eval_null_cell(self, foldset, ayah_units, mask_mode, k_null):
        """Run the null structure model on a deterministic instance sample; return the
        per-realization struct metrics distribution and the matched real-structure value
        on the SAME sample."""
        # build the matched real-structure value + the fixed instance sample first
        rng_samp = random.Random(SEED + 131)
        sample = []   # (train_index, ctx, true_u)
        real_inst = []
        per_fold_ts = []
        for name, train_seqs, test_seqs in foldset:
            ts = TrainStats([ayah_units[s] for s in train_seqs])
            per_fold_ts.append((ts, train_seqs))
        # gather candidate instances across folds with their fold index
        cand = []
        for fi, (name, train_seqs, test_seqs) in enumerate(foldset):
            ts = per_fold_ts[fi][0]
            vocab = set(ts.vocab)
            for ctx, true_u, seq in self.gen_instances(test_seqs, ayah_units, mask_mode):
                if true_u not in vocab:
                    continue
                cand.append((fi, [c for c in ctx if c in vocab], true_u))
        if len(cand) > NULL_EVAL_CAP:
            idx = sorted(rng_samp.sample(range(len(cand)), NULL_EVAL_CAP))
            cand = [cand[i] for i in idx]
        # real-structure metric on the sample
        for fi, ctx, true_u in cand:
            real_inst.append(score_instance(per_fold_ts[fi][0], ctx, true_u))
        real_agg = aggregate(real_inst)
        # null realizations
        rng_null = random.Random(SEED + 271)
        null_mrr = []
        null_gain = []
        null_ppl = []
        for kk in range(k_null):
            # build null TrainStats per fold (share vocab/p0 with real via same df)
            null_ts_by_fold = []
            for fi, (name, train_seqs, test_seqs) in enumerate(foldset):
                base_us = [ayah_units[s] for s in train_seqs]
                nus = self._null_unitsets(base_us, rng_null)
                null_ts_by_fold.append(TrainStats(nus))
            ninst = []
            for fi, ctx, true_u in cand:
                ts_n = null_ts_by_fold[fi]
                if true_u not in ts_n.vocab:
                    # null vocab == real vocab (same df marginals) so this shouldn't happen
                    continue
                c2 = [c for c in ctx if c in ts_n.vocab]
                ninst.append(score_instance(ts_n, c2, true_u))
            na = aggregate(ninst)
            null_mrr.append(na["mrr_struct"])
            null_gain.append(na["info_gain_bits"])
            null_ppl.append(na["ppl_struct"])
        def band(xs):
            xs = sorted(xs)
            return {"mean": r(statistics.fmean(xs)),
                    "ci_lo": r(xs[max(0, int(0.025 * len(xs)) - 0)]),
                    "ci_hi": r(xs[min(len(xs) - 1, int(0.975 * len(xs)))]),
                    "min": r(xs[0]), "max": r(xs[-1])}
        return {
            "n_sample": len(cand), "k_null": k_null,
            "real_mrr_struct": real_agg["mrr_struct"],
            "real_info_gain_bits": real_agg["info_gain_bits"],
            "real_ppl_struct": real_agg["ppl_struct"],
            "real_mrr_base": real_agg["mrr_base"],
            "null_mrr_struct": band(null_mrr),
            "null_info_gain_bits": band(null_gain),
            "null_ppl_struct": band(null_ppl),
            # decisive deltas
            "delta_mrr_real_minus_null": r(real_agg["mrr_struct"] - statistics.fmean(null_mrr)),
            "real_beats_null_mrr": real_agg["mrr_struct"] > sorted(null_mrr)[min(len(null_mrr) - 1, int(0.975 * len(null_mrr)))],
        }

    # ── pre-registered decision (§9) ─────────────────────────────────────────────────

    def decide(self, primary, null_primary, s2_primary, regime_agreement):
        c1 = (primary["info_gain_bits"] > 0 and primary.get("info_gain_boot_ci_lo", primary.get("info_gain_ci_lo", 0)) > 0
              and primary["ppl_struct"] < primary["ppl_base"]
              and primary["mrr_struct"] > primary["mrr_base"])
        c2 = null_primary["real_beats_null_mrr"] and null_primary["delta_mrr_real_minus_null"] > 0
        c3 = primary["mrr_struct"] > primary["mrr_degree"]
        hits10_gain = primary["hits10_struct"] - primary["hits10_base"]
        c4 = (primary["info_gain_bits"] >= MIN_BITS_GAIN and hits10_gain >= MIN_HITS10_GAIN)
        c5 = regime_agreement >= 3
        criteria = {"c1_beats_frequency": c1, "c2_beats_null": c2, "c3_not_degree": c3,
                    "c4_min_effect": c4, "c5_stable_regimes": c5,
                    "hits10_gain": r(hits10_gain), "regimes_passing": regime_agreement}
        # verdict logic
        if c1 and c2 and c3 and c4 and c5:
            verdict = "GENUINE_STRUCTURE"
        elif c1 and not c2:
            verdict = "FREQUENCY_SHAPED"
        elif not c1:
            verdict = "NON_PREDICTIVE"
        else:
            # c1 & c2 hold but effect/degree/stability fails -> shaped/marginal; classify conservatively
            verdict = "FREQUENCY_SHAPED"
        # order-vs-copresence note from S2
        order_note = None
        if s2_primary is not None:
            s2_better = s2_primary["info_gain_bits"] > primary["info_gain_bits"]
            order_note = {"s2_info_gain_bits": s2_primary["info_gain_bits"],
                          "s1_info_gain_bits": primary["info_gain_bits"],
                          "order_adds_over_copresence": s2_better}
        return {"criteria": criteria, "verdict": verdict, "order_note": order_note,
                "pre_registered_thresholds": {
                    "ALPHA": ALPHA, "LAMBDA": LAMBDA, "MIN_BITS_GAIN": MIN_BITS_GAIN,
                    "MIN_HITS10_GAIN": MIN_HITS10_GAIN, "K_NULL": K_NULL,
                    "BOOT": BOOT, "NULL_EVAL_CAP": NULL_EVAL_CAP, "SEED": SEED}}

    # ── S2 directional cell (order structure) ────────────────────────────────────────

    def eval_s2_cell(self, foldset, mask_mode):
        """Directional structure: PPMI computed on ORDERED root pairs (a-before-b).
        Reuses root order; context split into before/after the masked position is
        approximated by global directional association (a precedes b in training)."""
        all_inst = []
        for name, train_seqs, test_seqs in foldset:
            # directional co-occurrence: count ayahs where a appears before b
            dco = defaultdict(lambda: defaultdict(int))
            df = defaultdict(int)
            for s in train_seqs:
                order = self.ayah_root_order[s]
                seen = set()
                for u in order:
                    if u not in seen:
                        df[u] += 1
                        seen.add(u)
                for i in range(len(order)):
                    for j in range(i + 1, len(order)):
                        a, b = order[i], order[j]
                        if a != b:
                            dco[a][b] += 1   # a before b
            nA = len(train_seqs)
            vocab = set(df)
            # directional PPMI weight dir_w[c][u] = ppmi of (c before u)
            dir_w = defaultdict(dict)
            for a in dco:
                for b, cab in dco[a].items():
                    p_ab = cab / nA
                    p_a = df[a] / nA
                    p_b = df[b] / nA
                    v = math.log2(p_ab / (p_a * p_b)) if p_ab > 0 and p_a > 0 and p_b > 0 else 0.0
                    if v > 0:
                        dir_w[a][b] = LAMBDA * v
            # build a TrainStats for p0/ranks (undirected df identical)
            ts = TrainStats([self.ayah_roots[s] for s in train_seqs])
            ts.ppmi = {c: d for c, d in dir_w.items()}  # override with directional (c precedes u)
            ts._sorted_log2p0 = sorted(ts.log2p0.values())
            for ctx, true_u, seq in self.gen_instances(test_seqs, self.ayah_roots, mask_mode):
                if true_u not in vocab:
                    continue
                c2 = [c for c in ctx if c in vocab]
                all_inst.append(score_instance(ts, c2, true_u))
        return aggregate(all_inst)

    # ── concept-stability (variant 2b proxy) ─────────────────────────────────────────

    def concept_stability(self, foldset):
        """Cross-fold stability of concept co-occurrence profiles (frozen memberships).
        Reports mean pairwise cosine of per-fold concept df-vectors — a bound on how
        much concept-level predictive results can be trusted."""
        vecs = []
        allc = set()
        for name, train_seqs, test_seqs in foldset:
            df = defaultdict(int)
            for s in train_seqs:
                for c in self.ayah_concepts[s]:
                    df[c] += 1
            vecs.append(df)
            allc |= set(df)
        allc = sorted(allc)
        def cos(a, b):
            dot = sum(a.get(c, 0) * b.get(c, 0) for c in allc)
            na = math.sqrt(sum(v * v for v in a.values()))
            nb = math.sqrt(sum(v * v for v in b.values()))
            return dot / (na * nb) if na and nb else 0.0
        cs = [cos(vecs[i], vecs[j]) for i in range(len(vecs)) for j in range(i + 1, len(vecs))]
        return {"mean_pairwise_cosine": r(statistics.fmean(cs)) if cs else 0.0,
                "min_pairwise_cosine": r(min(cs)) if cs else 0.0,
                "note": "frozen full-corpus memberships (variant 2a); per-fold re-clustering "
                        "(2b) not performed — Phase-11 concept ARI=0.22 bounds concept-level trust"}

    # ── run ──────────────────────────────────────────────────────────────────────────

    def run(self):
        self.load()
        products = {}

        # fold sets
        r1_5 = self.folds_random(FOLDS_PRIMARY)
        r1_10 = self.folds_random(FOLDS_ROBUST)
        r2 = self.folds_blocks(N_BLOCKS)
        r3 = [f for frac in FORWARD_SPLITS for f in self.folds_forward(frac)]
        r4 = self.folds_length_strat(FOLDS_PRIMARY)

        print("  ROOT primary — R1 5-fold, masks single/p25/p50 …")
        root_R1 = {m: self.eval_cell(r1_5, self.ayah_roots, m, want_boot=(m == "single"))
                   for m in ["single", "p25", "p50"]}
        print("  ROOT regimes — single mask across R1-10 / R2 / R3 / R4 …")
        root_regimes = {
            "R1_k10": self.eval_cell(r1_10, self.ayah_roots, "single"),
            "R2_blocks": self.eval_cell(r2, self.ayah_roots, "single"),
            "R4_lenstrat": self.eval_cell(r4, self.ayah_roots, "single"),
        }
        for f in r3:
            root_regimes[f[0]] = self.eval_cell([f], self.ayah_roots, "single")

        print("  ROOT S2 directional — R1 5-fold single …")
        s2 = self.eval_s2_cell(r1_5, "single")

        print("  NULL control — R1 5-fold (single/p25/p50) + all regimes (single) …")
        null_R1 = {m: self.eval_null_cell(r1_5, self.ayah_roots, m, K_NULL)
                   for m in ["single", "p25", "p50"]}
        null_regimes = {
            "R1_k10": self.eval_null_cell(r1_10, self.ayah_roots, "single", K_NULL),
            "R2_blocks": self.eval_null_cell(r2, self.ayah_roots, "single", K_NULL),
            "R4_lenstrat": self.eval_null_cell(r4, self.ayah_roots, "single", K_NULL),
        }
        for f in r3:
            null_regimes[f[0]] = self.eval_null_cell([f], self.ayah_roots, "single", K_NULL)

        print("  CONCEPT secondary — R1 5-fold (frozen memberships) + stability …")
        concept_R1 = {m: self.eval_cell(r1_5, self.ayah_concepts, m, want_boot=(m == "single"))
                      for m in ["single", "p25", "p50"]}
        concept_null = self.eval_null_cell(r1_5, self.ayah_concepts, "single", K_NULL)
        cstab = self.concept_stability(r1_5)

        # regime agreement: count regimes where struct beats base on MRR and info_gain>0
        regime_pass = 0
        for cell in [root_R1["single"]] + list(root_regimes.values()):
            if cell.get("mrr_struct", 0) > cell.get("mrr_base", 1) and cell.get("info_gain_bits", 0) > 0:
                regime_pass += 1
        regime_total = 1 + len(root_regimes)

        decision = self.decide(root_R1["single"], null_R1["single"], s2, regime_pass)

        # ── assemble products ──
        products["prediction_task.json"] = {
            "method": METHOD,
            "task": "masked-unit completion under leakage-free whole-ayah holdout",
            "primary_unit": "root", "secondary_unit": "concept (frozen memberships, 2a)",
            "predictors": {
                "B0_frequency": "smoothed unigram prior P0 (context-blind)",
                "B1_degree": "co-occurrence degree rank (anti-frequency-as-degree guard)",
                "S1_structure": "log-linear P1 ∝ P0·2^(Σ PPMI(u,c)); == B0 when evidence 0",
                "S2_directional": "S1 with ORDERED (a-before-b) PPMI features",
                "N_null": "S1 on a configuration null (df+size preserved, co-occurrence destroyed)"},
            "metrics": ["MRR", "Hits@1/5/10", "rank_percentile", "perplexity",
                        "info_gain_bits = NLL_base - NLL_struct (paired)"],
            "fairness_lock": "structure score is additive over the baseline prior; "
                             "evidence=0 ⇒ score==baseline ⇒ wins attributable to relational info",
        }
        products["holdout_folds.json"] = {
            "method": METHOD,
            "regimes": {
                "R1_random": {"k": [FOLDS_PRIMARY, FOLDS_ROBUST], "seed": SEED},
                "R2_contiguous_blocks": {"k": N_BLOCKS},
                "R3_forward": {"splits": FORWARD_SPLITS},
                "R4_length_stratified": {"k": FOLDS_PRIMARY}},
            "mask_modes": {"single": "leave-one-unit-out", "p25": "mask 25%", "p50": "mask 50%"},
            "leakage_controls": [
                "whole-ayah holdout: test ayahs excluded from all training statistics",
                "training-only df/co-occurrence/PPMI, rebuilt per fold",
                "context observed from test ayah; associations learned from training only",
                "OOV units excluded symmetrically for all predictors, counted as coverage"],
            "n_ayahs": len(self.seqs),
        }
        products["root_predictivity.json"] = {
            "method": METHOD, "unit": "root",
            "R1_5fold": root_R1, "regimes": root_regimes, "s2_directional_R1": s2}
        products["concept_predictivity.json"] = {
            "method": METHOD, "unit": "concept", "variant": "2a frozen memberships",
            "R1_5fold": concept_R1}
        products["concept_stability.json"] = {
            "method": METHOD, "stability": cstab,
            "concept_null_control_R1": concept_null,
            "interpretation_guard": "concept-level predictive results are conditioned on this "
                                    "stability and on the frozen-membership definitional caveat"}
        products["frequency_null_control.json"] = {
            "method": METHOD, "k_null": K_NULL,
            "R1_5fold": null_R1, "regimes": null_regimes, "concept_R1": concept_null,
            "decisive_criterion": "C2: real S1 must beat the frequency null S1 (MRR, CI-separated)"}
        products["information_decomposition.json"] = {
            "method": METHOD,
            "primary_cell": "root / R1_5fold / single-mask",
            "info_gain_bits": root_R1["single"]["info_gain_bits"],
            "info_gain_boot_ci": [root_R1["single"].get("info_gain_boot_ci_lo"),
                                  root_R1["single"].get("info_gain_boot_ci_hi")],
            "ppl_base": root_R1["single"]["ppl_base"],
            "ppl_struct": root_R1["single"]["ppl_struct"],
            "null_info_gain_band": null_R1["single"]["null_info_gain_bits"],
            "real_minus_null_mrr": null_R1["single"]["delta_mrr_real_minus_null"]}
        products["robustness_results.json"] = {
            "method": METHOD,
            "regime_agreement": {"regimes_passing": regime_pass, "regimes_total": regime_total},
            "mask_fraction_sensitivity": {m: root_R1[m]["info_gain_bits"] for m in ["single", "p25", "p50"]},
            "fold_count_sensitivity": {"R1_k5": root_R1["single"]["info_gain_bits"],
                                       "R1_k10": root_regimes["R1_k10"]["info_gain_bits"]},
            "cross_regime_info_gain": {k: v["info_gain_bits"] for k, v in root_regimes.items()},
            "concept_stability_cosine": cstab["mean_pairwise_cosine"]}
        products["falsification_results.json"] = {
            "method": METHOD,
            "pre_registered_criteria": decision["criteria"],
            "verdict": decision["verdict"],
            "order_vs_copresence": decision["order_note"],
            "thresholds": decision["pre_registered_thresholds"],
            "negative_outcome_policy": "NON_PREDICTIVE/FREQUENCY_SHAPED are first-class results; "
                                       "no re-running with weaker baselines or tuned thresholds"}

        declared = ["prediction_task.json", "holdout_folds.json", "root_predictivity.json",
                    "concept_predictivity.json", "concept_stability.json",
                    "frequency_null_control.json", "information_decomposition.json",
                    "robustness_results.json", "falsification_results.json"]
        output_bytes = {}
        for name in declared:
            output_bytes[name] = write_json(self.out_dir / name, products[name])
            print(f"    wrote {name} ({output_bytes[name]} bytes)")

        # ── deterministic manifest (byte-identical) ──
        manifest = {
            "method": METHOD,
            "constants": {"SEED": SEED, "ALPHA": ALPHA, "LAMBDA": LAMBDA, "K_NULL": K_NULL,
                          "FOLDS_PRIMARY": FOLDS_PRIMARY, "FOLDS_ROBUST": FOLDS_ROBUST,
                          "FORWARD_SPLITS": FORWARD_SPLITS, "N_BLOCKS": N_BLOCKS, "BOOT": BOOT,
                          "NULL_EVAL_CAP": NULL_EVAL_CAP, "SWAP_MULT": SWAP_MULT,
                          "MIN_BITS_GAIN": MIN_BITS_GAIN, "MIN_HITS10_GAIN": MIN_HITS10_GAIN},
            "pre_registered_thresholds": decision["pre_registered_thresholds"],
            "input_sha256": {"monad.db": sha256_file(self.db),
                             "concept_memberships.json": sha256_file(self.concepts_path)},
            "output_sha256": {name: sha256_file(self.out_dir / name) for name in declared},
            "output_bytes": output_bytes,
            "verdict": decision["verdict"],
            "prohibitions_observed": PROHIBITIONS,
        }
        mbytes = write_json(self.out_dir / "predictivity_manifest.json", manifest)
        print(f"    wrote predictivity_manifest.json ({mbytes} bytes)")

        # ── volatile provenance (NOT byte-identical checked) ──
        try:
            commit = subprocess.run(["git", "-C", str(self.db.parent.parent), "rev-parse", "HEAD"],
                                    capture_output=True, text=True).stdout.strip()
        except Exception:
            commit = "unknown"
        run_meta = {
            "method": METHOD,
            "git_commit": commit,
            "build_timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "runtime_seconds": round(time.time() - self.t0, 2),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "note": "volatile provenance; intentionally EXCLUDED from byte-identical rebuild check",
        }
        write_json(self.out_dir / "run_metadata.json", run_meta)
        print(f"    wrote run_metadata.json (volatile, runtime={run_meta['runtime_seconds']}s)")

        self.decision = decision
        self.summary = {
            "verdict": decision["verdict"],
            "primary_info_gain_bits": root_R1["single"]["info_gain_bits"],
            "primary_info_gain_boot_ci": [root_R1["single"].get("info_gain_boot_ci_lo"),
                                          root_R1["single"].get("info_gain_boot_ci_hi")],
            "mrr_base": root_R1["single"]["mrr_base"],
            "mrr_struct": root_R1["single"]["mrr_struct"],
            "null_mrr_band": null_R1["single"]["null_mrr_struct"],
            "real_beats_null": null_R1["single"]["real_beats_null_mrr"],
            "regimes_passing": f"{regime_pass}/{regime_total}",
            "concept_stability_cosine": cstab["mean_pairwise_cosine"],
        }
        return self.summary


def main():
    ap = argparse.ArgumentParser(description="Monad Phase P — Structural Predictivity Engine")
    ap.add_argument("--db", default="generated/monad.db")
    ap.add_argument("--concepts", default="generated/concepts/concept_memberships.json")
    ap.add_argument("--out", default="generated/predictivity")
    args = ap.parse_args()
    print(f"Monad Phase P — Structural Predictivity / Held-Out Information Engine ({METHOD})")
    eng = PredictivityEngine(args.db, args.concepts, args.out)
    summary = eng.run()
    print("  done.")
    print(f"  VERDICT: {summary['verdict']}")
    print(f"  summary: {json.dumps(summary, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
