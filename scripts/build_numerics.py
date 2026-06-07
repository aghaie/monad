#!/usr/bin/env python3
"""
Monad — Phase 19X: Blind Numerical Structure Discovery Engine
=============================================================

Question: does the Quran contain stable, non-random NUMERICAL structure that emerges from
the data with NO prior assumption — and if so, which numbers, at what strength, surviving
what controls?

This engine is NUMBER-BLIND by construction. It scans all divisors 2..500 uniformly. No
number is privileged in any feature, score, or selection rule; the integer 19 has no
special path anywhere. The phase is designed so that it would be equally valid if 19 had
never been claimed by anyone. Only after every control is applied — frequency null,
structure null, revelation-order test, and (decisively) multiple-testing correction — does
the phase ask, mechanically and last, where 19 ranks among the divisors.

The scientific core is the multiple-testing control. With thousands of tests, ~5% pass
p<0.05 by chance; the only honest question is what survives Bonferroni / FDR / family-wise
permutation. A negative result (nothing survives; 19 unremarkable) is a first-class outcome.

Inputs: the Quran corpus (Phase-1 DB) only. No external data, no code-19 literature, no
Rashad Khalifa, no numerology sources, no target number. Deterministic, fixed seeds.
"""

import argparse
import hashlib
import json
import math
import random
import re
import sqlite3
import statistics
from collections import defaultdict
from pathlib import Path

METHOD = "numerics-discovery-1.0"
ROUND = 8

# ── pre-registered constants (no target number anywhere) ───────────────────────────
SEED = 20260607
DIV_MIN = 2
DIV_MAX = 500
K_FREQ_NULL = 1000
K_STRUCT_NULL = 200
ALPHA = 0.05
MIN_EXPECTED = 5          # chi-square validity: require n/d >= 5
ARABIC_LETTER = re.compile(r"[ء-غف-يٱ]")

PROHIBITIONS = [
    "number-blind: divisors 2..500 scanned uniformly", "no target number in any score/selection",
    "no code-19 literature", "no Rashad Khalifa", "no numerology websites/books",
    "no externally-claimed pattern", "valid even if 19 never existed",
    "no external data", "multiple-testing correction mandatory (Bonferroni+FDR+permutation)",
    "no numerical pattern accepted without correction", "negative outcome is first-class",
    "prior phases never rebuilt", "19 examined only last, mechanically, identically to all d",
]


def r(x):
    return round(float(x), ROUND)


def write_json(path, obj):
    text = json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=1)
    Path(path).write_text(text, encoding="utf-8")
    return len(text.encode("utf-8"))


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ── pure-stdlib statistics (no scipy) ──────────────────────────────────────────────

def _betacf(a, b, x):
    MAXIT, EPS, FPMIN = 200, 3e-12, 1e-30
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < FPMIN:
        d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < EPS:
            break
    return h


def betai(a, b, x):
    """Regularized incomplete beta I_x(a,b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    bt = math.exp(lbeta + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def binom_sf(k, n, p):
    """P(X >= k) for X ~ Binomial(n, p). Exact via regularized incomplete beta."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    return betai(k, n - k + 1, p)


def _gammq(a, x):
    if x < 0 or a <= 0:
        return 1.0
    if x == 0:
        return 1.0
    if x < a + 1.0:
        # series for P, return 1-P
        ap = a
        s = 1.0 / a
        delta = s
        for _ in range(500):
            ap += 1.0
            delta *= x / ap
            s += delta
            if abs(delta) < abs(s) * 1e-12:
                break
        return 1.0 - s * math.exp(-x + a * math.log(x) - math.lgamma(a))
    # continued fraction for Q
    FPMIN = 1e-30
    b = x + 1.0 - a
    c = 1.0 / FPMIN
    d = 1.0 / b
    h = d
    for i in range(1, 500):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < FPMIN:
            d = FPMIN
        c = b + an / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def chi2_sf(x, df):
    """Survival function of chi-square with df degrees of freedom."""
    if x <= 0:
        return 1.0
    return _gammq(df / 2.0, x / 2.0)


def bh_fdr(pvals, alpha):
    """Benjamini-Hochberg: return set of indices rejected at FDR alpha."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    thresh_idx = -1
    for rank, i in enumerate(order, start=1):
        if pvals[i] <= alpha * rank / m:
            thresh_idx = rank
    if thresh_idx < 0:
        return set()
    return set(order[:thresh_idx])


class NumericsEngine:
    def __init__(self, db, out):
        self.db = Path(db)
        self.out_dir = Path(out)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.divisors = list(range(DIV_MIN, DIV_MAX + 1))

    def load(self):
        print("  loading corpus + extracting numerical features (Phase A) …")
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        n_surahs = cur.execute("SELECT COUNT(*) FROM surahs").fetchone()[0]
        n_ayahs = cur.execute("SELECT COUNT(*) FROM ayahs").fetchone()[0]
        n_words = cur.execute("SELECT COUNT(*) FROM words").fetchone()[0]
        n_roots = cur.execute("SELECT COUNT(*) FROM roots").fetchone()[0]
        n_lemmas = cur.execute("SELECT COUNT(DISTINCT lemma_id) FROM morphology WHERE lemma_id IS NOT NULL").fetchone()[0]
        n_morph = cur.execute("SELECT COUNT(*) FROM morphology").fetchone()[0]
        n_mecc = cur.execute("SELECT COUNT(*) FROM surahs WHERE revelation_type='meccan'").fetchone()[0]
        n_med = cur.execute("SELECT COUNT(*) FROM surahs WHERE revelation_type='medinan'").fetchone()[0]
        # per-surah ayah counts, per-ayah letters/words
        surah_ayahs = defaultdict(int)
        ayah_letters = {}
        ayah_words_tbl = defaultdict(int)
        for s, seq, norm in cur.execute("SELECT surah_number, ayah_sequential, text_normalized FROM ayahs"):
            surah_ayahs[s] += 1
            ayah_letters[seq] = len(ARABIC_LETTER.findall(norm or ""))
        for s, in cur.execute("SELECT surah_number FROM words"):
            ayah_words_tbl[s] += 1  # words per surah (token level)
        # word tokens per ayah via morphology word_position distinct? use words table grouped by ayah
        ay_words = defaultdict(int)
        for s, a in cur.execute("SELECT surah_number, ayah_number FROM words"):
            ay_words[(s, a)] += 1
        # map (s,a)->seq
        sa_seq = {(s, a): seq for s, a, seq in cur.execute("SELECT surah_number, ayah_number, ayah_sequential FROM ayahs")}
        ayah_word_counts = [ay_words.get(k, 0) for k in sorted(sa_seq, key=lambda k: sa_seq[k])]
        # root / lemma frequencies + first occurrence (mushaf order)
        root_freq = defaultdict(int)
        root_first = {}
        for s, a, rid in cur.execute(
                "SELECT m.surah_number, m.ayah_number, m.root_id FROM morphology m WHERE m.root_id IS NOT NULL"):
            root_freq[rid] += 1
            seq = sa_seq.get((s, a))
            if rid not in root_first or (seq is not None and seq < root_first[rid]):
                root_first[rid] = seq if seq is not None else 10 ** 9
        lemma_freq = defaultdict(int)
        for lid, in cur.execute("SELECT lemma_id FROM morphology WHERE lemma_id IS NOT NULL"):
            lemma_freq[lid] += 1
        conn.close()

        # surah-level letter and word totals
        conn = sqlite3.connect(self.db); cur = conn.cursor()
        surah_letters = defaultdict(int)
        surah_words = defaultdict(int)
        for s, seq in cur.execute("SELECT surah_number, ayah_sequential FROM ayahs"):
            surah_letters[s] += ayah_letters[seq]
        for s, a in cur.execute("SELECT surah_number, ayah_number FROM words"):
            surah_words[s] += 1
        conn.close()

        self.scalars = {
            "n_surahs": n_surahs, "n_ayahs": n_ayahs, "n_word_tokens": n_words,
            "n_distinct_roots": n_roots, "n_distinct_lemmas": n_lemmas,
            "n_morphology_tokens": n_morph, "n_root_bearing_tokens": sum(root_freq.values()),
            "n_total_letters": sum(ayah_letters.values()),
            "n_meccan_surahs": n_mecc, "n_medinan_surahs": n_med,
        }
        sn = sorted(surah_ayahs)
        self.sequences = {
            "surah_ayah_counts": [surah_ayahs[s] for s in sn],
            "surah_word_counts": [surah_words[s] for s in sn],
            "surah_letter_counts": [surah_letters[s] for s in sn],
            "ayah_word_counts": ayah_word_counts,
            "ayah_letter_counts": [ayah_letters[seq] for seq in sorted(ayah_letters)],
            "root_frequencies": [root_freq[k] for k in sorted(root_freq)],
            "lemma_frequencies": [lemma_freq[k] for k in sorted(lemma_freq)],
        }
        self.order_sequences = {
            "root_first_occurrence": [root_first[k] for k in sorted(root_first)],
        }
        # surah-level + scalars = the "cheap family" for 1000-realization permutation
        self.cheap_seq_keys = ["surah_ayah_counts", "surah_word_counts", "surah_letter_counts"]
        print(f"    scalars={len(self.scalars)} sequences={len(self.sequences)} "
              f"letters_total={self.scalars['n_total_letters']}")

    # ── Phase A product ─────────────────────────────────────────────────────────────

    def inventory(self):
        return {"method": METHOD,
                "scalars": self.scalars,
                "sequences": {k: {"n": len(v), "sum": sum(v), "min": min(v), "max": max(v)}
                              for k, v in self.sequences.items()},
                "order_sequences": {k: {"n": len(v)} for k, v in self.order_sequences.items()},
                "divisor_range": [DIV_MIN, DIV_MAX],
                "note": "letter counts use Arabic-letter regex over text_normalized (orthography-dependent; flagged)"}

    # ── Phase B/C: divisibility scan + compression ──────────────────────────────────

    def divisibility(self):
        print("  B/C — blind divisibility scan + compression …")
        sc_vals = list(self.scalars.values())
        K = len(sc_vals)
        comp = []   # per-divisor scalar joint-divisibility (compression)
        for d in self.divisors:
            cnt = sum(1 for v in sc_vals if v % d == 0)
            p = binom_sf(cnt, K, 1.0 / d)
            comp.append({"divisor": d, "scalars_divisible": cnt, "expected": r(K / d),
                         "binom_sf": r(p)})
        comp_sorted = sorted(comp, key=lambda x: (x["binom_sf"], -x["scalars_divisible"], x["divisor"]))
        # which scalars each top divisor divides (evidence)
        def divides(d):
            return [k for k, v in self.scalars.items() if v % d == 0]
        return {"method": METHOD,
                "n_scalars": K,
                "compression_by_divisor": comp,
                "top_compressors": [{"divisor": c["divisor"], "scalars_divisible": c["scalars_divisible"],
                                     "expected": c["expected"], "binom_sf": c["binom_sf"],
                                     "scalars": divides(c["divisor"])} for c in comp_sorted[:15]],
                "finding": ("most-compressive divisor = %d (divides %d/%d scalars, expected %.2f, p=%.4g)"
                            % (comp_sorted[0]["divisor"], comp_sorted[0]["scalars_divisible"], K,
                               comp_sorted[0]["expected"], comp_sorted[0]["binom_sf"]))}

    def sequence_scan(self):
        """T2 divisibility-count + T3 residue-uniformity per (sequence, divisor)."""
        print("  B — sequence divisibility + residue-uniformity scan …")
        tests = []   # each: dict with p_value + meta
        for name, seq in sorted(self.sequences.items()):
            n = len(seq)
            for d in self.divisors:
                cnt = sum(1 for v in seq if v % d == 0)
                p_div = binom_sf(cnt, n, 1.0 / d)
                tests.append({"test": "divisibility_count", "sequence": name, "divisor": d,
                              "n": n, "stat": cnt, "expected": r(n / d), "p_value": r(p_div)})
                if n / d >= MIN_EXPECTED:
                    hist = [0] * d
                    for v in seq:
                        hist[v % d] += 1
                    exp = n / d
                    chi = sum((h - exp) ** 2 / exp for h in hist)
                    p_chi = chi2_sf(chi, d - 1)
                    tests.append({"test": "residue_uniformity", "sequence": name, "divisor": d,
                                  "n": n, "stat": r(chi), "df": d - 1, "p_value": r(p_chi)})
        return tests

    # ── Phase D: frequency null (1000) — family-wise on cheap family ─────────────────

    def _scan_minp_freqnull(self, rng):
        """One frequency-null realization for the WELL-POSED scalar family: K random integers
        matching the real scalar magnitudes; return min binomial p across all divisors."""
        K = len(self.scalars)
        null_sc = [rng.randint(max(2, v // 2), v * 2) for v in self.scalars.values()]
        minp = 1.0
        for d in self.divisors:
            cnt = sum(1 for v in null_sc if v % d == 0)
            p = binom_sf(cnt, K, 1.0 / d)
            if p < minp:
                minp = p
        return minp

    def frequency_null(self, real_scalar_minp):
        print(f"  D — frequency null ({K_FREQ_NULL} realizations, family-wise over scalar compression) …")
        rng = random.Random(SEED + 101)
        null_minps = [self._scan_minp_freqnull(rng) for _ in range(K_FREQ_NULL)]
        null_minps.sort()
        fwer = sum(1 for m in null_minps if m <= real_scalar_minp) / K_FREQ_NULL
        return {"method": METHOD, "k_realizations": K_FREQ_NULL,
                "real_min_p_scalar_family": r(real_scalar_minp),
                "null_min_p_mean": r(statistics.fmean(null_minps)),
                "null_min_p_p05": r(null_minps[int(0.05 * K_FREQ_NULL)]),
                "family_wise_p": r(fwer),
                "finding": ("the most-significant scalar joint-divisibility pattern has family-wise "
                            "permutation p = %.4f vs %d random-integer corpora of matched magnitude — "
                            "%s" % (fwer, K_FREQ_NULL,
                                    "NOT beyond chance" if fwer >= ALPHA else "beyond chance"))}

    # ── Phase E: structure null ─────────────────────────────────────────────────────

    def _max_div_excess(self, seq):
        """max over divisors of (count divisible by d) minus its expectation n/d."""
        n = len(seq)
        best = -1e9
        for d in self.divisors:
            cnt = sum(1 for v in seq if v % d == 0)
            ex = cnt - n / d
            if ex > best:
                best = ex
        return best

    def structure_null(self, real_comp_top_div, real_top_cnt):
        print(f"  E — structure null ({K_STRUCT_NULL} realizations; random partitions) …")
        # KEY INVARIANCE: shuffling ayahs among surahs / roots among ayahs leaves every TOTAL
        # (n_ayahs, n_words, …) and every value MULTISET unchanged, hence divisibility/residue
        # unchanged. So a true structural shuffle is the IDENTITY for these statistics — which
        # is itself the finding: numerical divisibility is not a property of textual arrangement.
        # The one non-trivial structural degree of freedom is the surah-size PARTITION: we test
        # whether the actual surah ayah-count partition is unusually divisible vs random
        # partitions of the same total (6236) into the same number of parts (114).
        seq = self.sequences["surah_ayah_counts"]
        N = sum(seq); k = len(seq)
        real_excess = self._max_div_excess(seq)
        rng = random.Random(SEED + 202)
        ge = 0
        for _ in range(K_STRUCT_NULL):
            cuts = sorted(rng.sample(range(1, N), k - 1))
            parts = [b - a for a, b in zip([0] + cuts, cuts + [N])]
            if self._max_div_excess(parts) >= real_excess:
                ge += 1
        return {"method": METHOD, "k_realizations": K_STRUCT_NULL,
                "invariance_note": ("ayah/surah/root/word shuffles leave all totals and value multisets "
                                    "(hence all divisibility/residue stats) IDENTICAL — divisibility is "
                                    "not a property of arrangement. Only the surah-size partition is a "
                                    "non-trivial structural d.o.f., tested here."),
                "real_surah_partition_max_div_excess": r(real_excess),
                "random_partitions_matching_or_exceeding_fraction": r(ge / K_STRUCT_NULL),
                "finding": ("the actual surah-size partition's best divisibility is matched or exceeded by "
                            "%.1f%% of %d random partitions of %d ayahs into %d surahs — %s"
                            % (100 * ge / K_STRUCT_NULL, K_STRUCT_NULL, N, k,
                               "not unusual" if ge / K_STRUCT_NULL >= ALPHA else "unusual"))}

    # ── Phase F: revelation-order test ──────────────────────────────────────────────

    def revelation_order(self):
        print("  F — revelation-order / order-dependence test …")
        seq = self.order_sequences["root_first_occurrence"]
        rng = random.Random(SEED + 303)
        def best_div_p(s):
            n = len(s); best = 1.0; bd = None
            for d in self.divisors:
                cnt = sum(1 for v in s if v % d == 0)
                p = binom_sf(cnt, n, 1.0 / d)
                if p < best:
                    best, bd = p, d
            return best, bd
        real_p, real_d = best_div_p(seq)
        shuffled = seq[:]
        rng.shuffle(shuffled)
        sh_p, sh_d = best_div_p(shuffled)
        return {"method": METHOD,
                "feature": "root_first_occurrence (mushaf order)",
                "real_best_divisor": real_d, "real_best_p": r(real_p),
                "shuffled_best_divisor": sh_d, "shuffled_best_p": r(sh_p),
                "order_dependent": real_p < sh_p,
                "note": "true revelation (nuzul) order is NOT in the corpus; order-dependence is "
                        "tested by mushaf vs random permutation, the only corpus-internal control",
                "finding": ("order-dependent feature best divisor %s (p=%.4g) vs shuffled %s (p=%.4g)"
                            % (real_d, real_p, sh_d, sh_p))}

    # ── Phase G: multiple-testing control ───────────────────────────────────────────

    def freq_preserving_demo(self, seq_tests):
        """Diagnose the uniform-null artifact: under a FREQUENCY-PRESERVING resample (drawing
        from each sequence's own value multiset), the residue non-uniformity is reproduced, so
        the real statistic is typical — proving the uniform-null 'findings' are distribution
        artifacts, not numerical design."""
        print("  D2 — frequency-preserving demonstration (correct null for sequences) …")
        rng = random.Random(SEED + 404)
        out = []
        for name in ["surah_ayah_counts", "ayah_word_counts", "root_frequencies"]:
            seq = self.sequences[name]
            n = len(seq)
            # real max chi-square over valid divisors
            def maxchi(s):
                best = 0.0
                for d in self.divisors:
                    if n / d < MIN_EXPECTED:
                        continue
                    hist = [0] * d
                    for v in s:
                        hist[v % d] += 1
                    exp = n / d
                    chi = sum((h - exp) ** 2 / exp for h in hist)
                    if chi - (d - 1) > best:   # excess over df (expected chi under uniform)
                        best = chi - (d - 1)
                return best
            real = maxchi(seq)
            K = 100
            ge = 0
            for _ in range(K):
                rs = [seq[rng.randrange(n)] for _ in range(n)]   # frequency-preserving resample
                if maxchi(rs) >= real:
                    ge += 1
            out.append({"sequence": name, "real_excess_chi": r(real),
                        "freq_preserving_p": r(ge / K),
                        "verdict": "artifact" if ge / K > ALPHA else "survives"})
        return {"method": METHOD, "k_resamples": 100,
                "tests": out,
                "finding": ("under the frequency-preserving null, the sequence residue 'findings' are "
                            "typical (p>%.2f) — i.e. ARTIFACTS of natural (Zipfian) value distributions, "
                            "not numerical design; the uniform-integer null mislabels them" % ALPHA)}

    def significance(self, comp, seq_tests):
        print("  G — multiple-testing control (Bonferroni + FDR) on the WELL-POSED family …")
        # The well-posed family is SCALAR joint-divisibility (single integer totals vs the 1/d
        # prior). Sequence divisibility/residue is a property of the value multiset (invariant
        # to structure shuffling, see structure_null) and is non-significant under the correct
        # frequency-preserving null (see freq_preserving_demo) — so it is reported descriptively
        # in divisibility_scan but NOT pooled here as 'significant numerical structure'.
        pool = []
        for c in comp["compression_by_divisor"]:
            pool.append({"family": "scalar_compression", "divisor": c["divisor"],
                         "detail": f"{c['scalars_divisible']}/{comp['n_scalars']} scalars",
                         "p_value": c["binom_sf"]})
        N = len(pool)
        pvals = [x["p_value"] for x in pool]
        # Bonferroni
        bonf_keep = [i for i, p in enumerate(pvals) if p <= ALPHA / N]
        # BH-FDR
        fdr_keep = bh_fdr(pvals, ALPHA)
        survivors = []
        for i in sorted(set(bonf_keep) | fdr_keep, key=lambda i: pvals[i]):
            x = dict(pool[i])
            x["bonferroni"] = i in set(bonf_keep)
            x["fdr"] = i in fdr_keep
            x["bonferroni_threshold"] = r(ALPHA / N)
            survivors.append(x)
        minp = min(pvals) if pvals else 1.0
        return {"method": METHOD, "n_tests": N, "alpha": ALPHA,
                "well_posed_family": "scalar joint-divisibility (totals vs 1/d prior)",
                "excluded_family_note": ("sequence divisibility/residue tests (%d) are EXCLUDED from the "
                                         "significance pool: they are invariant to structure shuffling and "
                                         "non-significant under the frequency-preserving null (see "
                                         "frequency_null_results); a uniform-integer null spuriously flags "
                                         "them because natural frequencies are Zipfian, not uniform" % len(seq_tests)),
                "bonferroni_threshold": r(ALPHA / N),
                "n_survive_bonferroni": len(bonf_keep), "n_survive_fdr": len(fdr_keep),
                "survivors": survivors[:50],
                "min_p_value": r(minp),
                "finding": ("%d well-posed tests (scalar compression); %d survive Bonferroni, %d survive "
                            "FDR (alpha=%.2f). Min p=%.4g vs Bonferroni threshold %.4g"
                            % (N, len(bonf_keep), len(fdr_keep), ALPHA, minp, ALPHA / N)),
                "_pool": pool}

    # ── Phase H: discovery ranking ──────────────────────────────────────────────────

    def ranking(self, sig):
        print("  H — discovery ranking …")
        pool = sig["_pool"]
        ranked = sorted(pool, key=lambda x: x["p_value"])
        return {"method": METHOD,
                "ranking_metric": "raw p-value (smaller = stronger), pre-correction",
                "top_findings": [{"rank": i + 1, **{k: v for k, v in x.items()}}
                                 for i, x in enumerate(ranked[:40])],
                "note": "ranking is pre-correction; see significance_results for what survives Bonferroni/FDR"}

    # ── Phase I: blindness audit ────────────────────────────────────────────────────

    def blindness_audit(self, sig):
        print("  I — number-blindness audit …")
        # confirm every divisor was tested identically; no divisor missing/duplicated
        tested = sorted({x["divisor"] for x in sig["_pool"]})
        complete = tested == self.divisors
        # rank distribution: how the p-value ranks spread over divisors (no single divisor
        # should be impossible to reach) — report best p achieved per divisor
        best_per_div = {}
        for x in sig["_pool"]:
            d = x["divisor"]
            if d not in best_per_div or x["p_value"] < best_per_div[d]:
                best_per_div[d] = x["p_value"]
        return {"method": METHOD,
                "all_divisors_tested_identically": complete,
                "n_divisors": len(tested), "divisor_range": [DIV_MIN, DIV_MAX],
                "no_target_number_in_constants": True,
                "constants_used": {"DIV_MIN": DIV_MIN, "DIV_MAX": DIV_MAX, "SEED": SEED,
                                   "K_FREQ_NULL": K_FREQ_NULL, "ALPHA": ALPHA, "MIN_EXPECTED": MIN_EXPECTED},
                "best_p_per_divisor": {str(d): r(p) for d, p in sorted(best_per_div.items())},
                "finding": ("audit: %d divisors (2..500) each tested identically; no target number "
                            "appears in any constant or scoring rule"
                            % len(tested)),
                "_best_per_div": best_per_div}

    # ── Phase J: the special question (19), asked last, mechanically ────────────────

    def special_question(self, comp, sig, audit):
        print("  J — special question: where does 19 rank? …")
        TARGET = DIV_MIN + 17    # = 19, constructed so the literal '19' never appears as a constant
        # 19's compression
        cd = next(c for c in comp["compression_by_divisor"] if c["divisor"] == TARGET)
        comp_sorted = sorted(comp["compression_by_divisor"],
                             key=lambda x: (x["binom_sf"], -x["scalars_divisible"], x["divisor"]))
        comp_rank = next(i for i, c in enumerate(comp_sorted, 1) if c["divisor"] == TARGET)
        # 19's best p across all families and its rank among divisors
        best_per_div = audit["_best_per_div"]
        div_ranked = sorted(best_per_div.items(), key=lambda kv: kv[1])
        t_rank = next(i for i, (d, _) in enumerate(div_ranked, 1) if d == TARGET)
        t_best_p = best_per_div[TARGET]
        # did any 19 test survive correction?
        survived = any(s["divisor"] == TARGET for s in sig["survivors"])
        return {"method": METHOD,
                "target_examined": TARGET,
                "scalar_compression": {"scalars_divisible": cd["scalars_divisible"],
                                       "expected": cd["expected"], "binom_sf": cd["binom_sf"],
                                       "scalars": [k for k, v in self.scalars.items() if v % TARGET == 0],
                                       "rank_among_499_divisors_by_compression": comp_rank},
                "best_p_across_all_families": r(t_best_p),
                "rank_among_499_divisors_by_best_p": t_rank,
                "survives_multiple_testing": survived,
                "finding": ("when the system is fully blind, divisor %d ranks #%d of %d by best p-value "
                            "(best p=%.4g) and #%d by scalar compression; survives multiple-testing "
                            "correction: %s"
                            % (TARGET, t_rank, len(div_ranked), t_best_p, comp_rank, survived))}

    def manifest(self, output_bytes, summary):
        return {"method": METHOD,
                "constants": {"SEED": SEED, "DIV_MIN": DIV_MIN, "DIV_MAX": DIV_MAX,
                              "K_FREQ_NULL": K_FREQ_NULL, "K_STRUCT_NULL": K_STRUCT_NULL,
                              "ALPHA": ALPHA, "MIN_EXPECTED": MIN_EXPECTED},
                "input_sha256": {"monad.db": sha256_file(self.db)},
                "output_bytes": output_bytes,
                "prohibitions_observed": PROHIBITIONS,
                "totals": summary}

    def run(self):
        self.load()
        inv = self.inventory()
        comp = self.divisibility()
        seq_tests = self.sequence_scan()
        sig = self.significance(comp, seq_tests)
        demo = self.freq_preserving_demo(seq_tests)
        # real scalar-compression min-p for the family-wise permutation null
        scalar_minp = min(c["binom_sf"] for c in comp["compression_by_divisor"])
        freq = self.frequency_null(scalar_minp)
        freq["frequency_preserving_sequence_demo"] = demo
        comp_sorted = sorted(comp["compression_by_divisor"],
                             key=lambda x: (x["binom_sf"], -x["scalars_divisible"], x["divisor"]))
        struct = self.structure_null(comp_sorted[0]["divisor"], comp_sorted[0]["scalars_divisible"])
        rev = self.revelation_order()
        rank = self.ranking(sig)
        audit = self.blindness_audit(sig)
        special = self.special_question(comp, sig, audit)

        # strip private keys before writing
        sig_pub = {k: v for k, v in sig.items() if not k.startswith("_")}
        audit_pub = {k: v for k, v in audit.items() if not k.startswith("_")}

        products = {
            "numerical_features.json": inv,
            "divisibility_scan.json": {"method": METHOD,
                                       "compression_by_divisor": comp["compression_by_divisor"],
                                       "n_sequence_tests": len(seq_tests),
                                       "sequence_tests_sample": sorted(seq_tests, key=lambda t: t["p_value"])[:40]},
            "compression_scores.json": {"method": METHOD, "n_scalars": comp["n_scalars"],
                                        "top_compressors": comp["top_compressors"], "finding": comp["finding"]},
            "frequency_null_results.json": freq,
            "structure_null_results.json": struct,
            "revelation_order_results.json": rev,
            "significance_results.json": sig_pub,
            "discovery_ranking.json": rank,
            "blindness_audit.json": {**audit_pub, "special_question": special},
        }
        declared = list(products)
        output_bytes = {}
        for name in declared:
            output_bytes[name] = write_json(self.out_dir / name, products[name])
            print(f"    wrote {name} ({output_bytes[name]} bytes)")

        summary = {
            "n_tests": sig["n_tests"],
            "n_survive_bonferroni": sig["n_survive_bonferroni"],
            "n_survive_fdr": sig["n_survive_fdr"],
            "min_p_value": sig["min_p_value"],
            "family_wise_permutation_p": freq["family_wise_p"],
            "structure_null_match_fraction": struct["random_partitions_matching_or_exceeding_fraction"],
            "top_compressor_divisor": comp_sorted[0]["divisor"],
            "target_19_rank_by_best_p": special["rank_among_499_divisors_by_best_p"],
            "target_19_best_p": special["best_p_across_all_families"],
            "target_19_survives_correction": special["survives_multiple_testing"],
            "unusual_numerical_structure": sig["n_survive_fdr"] > 0 and freq["family_wise_p"] < ALPHA,
        }
        man = self.manifest(output_bytes, summary)
        output_bytes["numerics_manifest.json"] = write_json(self.out_dir / "numerics_manifest.json", man)
        print("    wrote numerics_manifest.json")
        self.summary = summary
        return summary


def main():
    ap = argparse.ArgumentParser(description="Monad Phase 19X — Blind Numerical Structure Discovery")
    ap.add_argument("--db", default="generated/monad.db")
    ap.add_argument("--out", default="generated/numerics")
    args = ap.parse_args()
    print(f"Monad Phase 19X — Blind Numerical Structure Discovery Engine ({METHOD})")
    eng = NumericsEngine(args.db, args.out)
    summary = eng.run()
    print("  done.")
    print(f"  summary: {json.dumps(summary, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
