#!/usr/bin/env python3
"""
scripts/build_L11_stylometry.py

Monad — Layer L11: Stylometric & prosodic self-structure.

Falsifiable reframe of the "balaghi i'jaz" prompt. We measure the Quran's
linguistic STRUCTURE (rhyme/fawasil, intra-sura homogeneity, content<->structure)
and test each claim against a SEEDED PERMUTATION NULL — never against an
arbitrary threshold. No "superhuman" claim is made; that inference is outside
what stylometry can reach and is marked UNKNOWN in the report.

Self-sufficient: all features come from text_diacritics + morphology in
generated/monad.db. No external dictionary, translation, or control corpus.

Four tests (each: observed statistic + permutation null, N=1000, seeded):

  A — FAWASIL COHESION: are ayah-final letters more homogeneous WITHIN suras
      than chance? Null = shuffle fasila labels across the corpus (keep sizes).

  B — MECCAN/MEDINAN SEPARABILITY: does revelation period separate in
      stylometric space? Leave-one-out nearest-centroid balanced accuracy vs a
      label-permutation null. Run twice: with length features and shape-only,
      to see whether separation is "just length". A positive result means style
      EVOLVES over time — the honest opposite of "perfectly uniform style".

  C — HIDDEN HETEROGENEITY: after removing the period+length axes, is there
      latent multi-style cluster structure? 2-means variance-explained vs a
      column-permutation null. No excess => consistent with a single evolving
      idiolect; excess => flagged for inspection.

  D — REGISTER x PERIOD: process/command aspect (IMPF+IMPV) vs static (PERF).
      Confirms the legacy 52.7% process-lean descriptively, and tests whether
      register composition shifts meccan->medinan (label-permutation null).

Deterministic (seeded), offline. Outputs in generated/layers/L11_style/.
"""

import argparse
import json
import math
import random
import sqlite3
import statistics
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB_DEFAULT = REPO / "generated" / "monad.db"
OUT_DEFAULT = REPO / "generated" / "layers" / "L11_style"
SEED = 11
N_NULL = 1000

# ── orthography: classify each character of text_diacritics ──
# Base letters (consonantal skeleton + alef-wasla + alef-maqsura + ta-marbuta).
_LETTERS = set(
    "ءآأؤإئابةتثجحخدذرزسشصضطظعغفقكلمنهوىي"
    "ٱ"  # alef wasla ٱ
)
# Short-vowel / tanwin / dagger-alef marks counted as vocalic.
_VOWEL_MARKS = {
    "ً", "ٌ", "ٍ",  # tanwin (fathatan/dammatan/kasratan)
    "َ", "ُ", "ِ",  # fatha / damma / kasra
    "ٰ",                       # superscript (dagger) alef
}
# Everything else (shadda 0651, sukun 0652, madda 0653-0655, quranic annotation
# marks 06D6-06ED, tatweel 0640, spaces, punctuation) is ignored for letters/vowels.


def analyse_ayah(text):
    """Return per-ayah stylometric features from diacritized text."""
    letters = []          # base letters, in order
    n_vowels = 0
    for ch in text:
        if ch in _LETTERS:
            letters.append(ch)
        elif ch in _VOWEL_MARKS:
            n_vowels += 1
    n_words = len([w for w in text.split() if any(c in _LETTERS for c in w)])
    n_letters = len(letters)
    fasila = letters[-1] if letters else ""
    rhyme = "".join(letters[-2:]) if len(letters) >= 2 else fasila
    return {
        "fasila": fasila,
        "rhyme": rhyme,
        "nw": n_words,
        "nl": n_letters,
        "mwl": (n_letters / n_words) if n_words else 0.0,   # mean word length
        "vc": (n_vowels / n_letters) if n_letters else 0.0,  # vowel/consonant density
    }


def entropy(counter):
    tot = sum(counter.values())
    if tot == 0:
        return 0.0
    return -sum((c / tot) * math.log(c / tot) for c in counter.values() if c)


# ── tiny linear algebra (stdlib only) ──
def solve(A, b):
    """Gaussian elimination, A is n×n list-of-lists, returns x or None if singular."""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-12:
            return None
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        M[col] = [v / pv for v in M[col]]
        for r in range(n):
            if r != col and M[r][col]:
                f = M[r][col]
                M[r] = [a - f * b_ for a, b_ in zip(M[r], M[col])]
    return [M[r][n] for r in range(n)]


def ols_residuals(y, X):
    """Residuals of y on design X (rows = observations, incl. intercept column)."""
    p = len(X[0])
    XtX = [[sum(X[i][a] * X[i][c] for i in range(len(X))) for c in range(p)] for a in range(p)]
    Xty = [sum(X[i][a] * y[i] for i in range(len(X))) for a in range(p)]
    beta = solve(XtX, Xty)
    if beta is None:
        m = statistics.mean(y)
        return [v - m for v in y]
    return [y[i] - sum(beta[a] * X[i][a] for a in range(p)) for i in range(len(X))]


def zscore_columns(rows):
    """Standardize each column across rows; constant columns -> zeros."""
    cols = list(zip(*rows))
    out = []
    for col in cols:
        m = statistics.mean(col)
        sd = statistics.pstdev(col)
        out.append([0.0] * len(col) if sd < 1e-12 else [(v - m) / sd for v in col])
    return [list(r) for r in zip(*out)]


def dist2(p, q):
    return sum((a - b) ** 2 for a, b in zip(p, q))


# ── Test B: leave-one-out nearest-centroid balanced accuracy ──
def loo_balanced_accuracy(points, labels):
    classes = sorted(set(labels))
    correct = {c: 0 for c in classes}
    total = {c: 0 for c in classes}
    for i in range(len(points)):
        cents = {}
        for c in classes:
            grp = [points[j] for j in range(len(points)) if j != i and labels[j] == c]
            if grp:
                cents[c] = [statistics.mean(f) for f in zip(*grp)]
        if len(cents) < len(classes):
            continue
        pred = min(cents, key=lambda c: dist2(points[i], cents[c]))
        total[labels[i]] += 1
        if pred == labels[i]:
            correct[labels[i]] += 1
    recalls = [correct[c] / total[c] for c in classes if total[c]]
    return sum(recalls) / len(recalls) if recalls else 0.0


# ── Test C: 2-means variance explained ──
def kmeans2_varexp(points, rnd):
    n = len(points)
    gm = [statistics.mean(f) for f in zip(*points)]
    wss1 = sum(dist2(p, gm) for p in points)
    if wss1 < 1e-12:
        return 0.0
    best = None
    for _ in range(10):
        c = [list(points[rnd.randrange(n)]), list(points[rnd.randrange(n)])]
        assign = [0] * n
        for _ in range(50):
            new = [0 if dist2(points[i], c[0]) <= dist2(points[i], c[1]) else 1 for i in range(n)]
            if new == assign:
                break
            assign = new
            for k in (0, 1):
                grp = [points[i] for i in range(n) if assign[i] == k]
                if grp:
                    c[k] = [statistics.mean(f) for f in zip(*grp)]
        wss2 = sum(dist2(points[i], c[assign[i]]) for i in range(n))
        if best is None or wss2 < best:
            best = wss2
    return 1.0 - best / wss1


def pval(null, observed):
    return (sum(1 for x in null if x >= observed) + 1) / (len(null) + 1)


def summarise(null):
    return {"mean": round(statistics.mean(null), 4),
            "sd": round(statistics.pstdev(null), 4),
            "max": round(max(null), 4)}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=str(DB_DEFAULT))
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    db = Path(args.db); out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(db); con.row_factory = sqlite3.Row
    suras = {r["surah_number"]: {"type": r["revelation_type"], "nayat": r["ayah_count"]}
             for r in con.execute("SELECT surah_number,revelation_type,ayah_count FROM surahs")}
    ayah_rows = con.execute(
        "SELECT surah_number s,ayah_number a,text_diacritics t FROM ayahs "
        "ORDER BY surah_number,ayah_number").fetchall()
    aspect_rows = con.execute(
        "SELECT surah_number s,aspect,COUNT(*) c FROM morphology "
        "WHERE aspect IN ('IMPF','IMPV','PERF') GROUP BY surah_number,aspect").fetchall()
    con.close()

    # ── per-ayah features ──
    feats = {}
    by_sura = defaultdict(list)
    for r in ayah_rows:
        f = analyse_ayah(r["t"] or "")
        feats[(r["s"], r["a"])] = f
        by_sura[r["s"]].append(f)
    keys = sorted(feats)

    # ── per-sura aggregates ──
    sura_feat = {}
    for s, fs in by_sura.items():
        fasilas = Counter(f["fasila"] for f in fs)
        n = len(fs)
        sura_feat[s] = {
            "type": suras[s]["type"],
            "n_ayat": n,
            "mean_nw": statistics.mean(f["nw"] for f in fs),
            "mean_nl": statistics.mean(f["nl"] for f in fs),
            "mean_mwl": statistics.mean(f["mwl"] for f in fs),
            "mean_vc": statistics.mean(f["vc"] for f in fs),
            "fvi": len(fasilas) / n,                       # Fasila Variety Index
            "fasila_entropy": entropy(fasilas),
            "modal_fasila": fasilas.most_common(1)[0][0],
            "modal_share": fasilas.most_common(1)[0][1] / n,
        }
    sura_ids = sorted(sura_feat)
    rnd = random.Random(SEED)

    # ── TEST A — fawasil cohesion within suras ──
    sura_sizes = [len(by_sura[s]) for s in sura_ids]
    flat_fasila = [f["fasila"] for s in sura_ids for f in by_sura[s]]
    total_ayat = len(flat_fasila)

    def cohesion(flat):
        i = 0; hits = 0
        for sz in sura_sizes:
            seg = flat[i:i + sz]; i += sz
            hits += Counter(seg).most_common(1)[0][1]
        return hits / total_ayat

    obs_A = cohesion(flat_fasila)
    null_A = []
    for _ in range(N_NULL):
        perm = flat_fasila[:]; rnd.shuffle(perm)
        null_A.append(cohesion(perm))
    test_A = {
        "question": "are ayah-final letters more homogeneous within suras than chance?",
        "statistic": "corpus mean within-sura modal-fasila share",
        "observed": round(obs_A, 4), "null": summarise(null_A),
        "p": round(pval(null_A, obs_A), 4),
        "fold": round(obs_A / statistics.mean(null_A), 2),
        "verdict": "fawasil cohere within suras" if obs_A > max(null_A) else "no advantage",
        "confidence": "صریح" if obs_A > max(null_A) and pval(null_A, obs_A) <= 0.01 else "نامشخص",
    }

    # ── feature matrices for B/C ──
    shape_keys = ["mean_mwl", "mean_vc", "fvi", "fasila_entropy"]
    length_keys = ["mean_nw", "mean_nl"]
    labels = [sura_feat[s]["type"] for s in sura_ids]
    shape_rows = [[sura_feat[s][k] for k in shape_keys] for s in sura_ids]
    full_rows = [[sura_feat[s][k] for k in shape_keys + length_keys] for s in sura_ids]
    Zshape = zscore_columns(shape_rows)
    Zfull = zscore_columns(full_rows)

    # ── TEST B — meccan/medinan separability ──
    def sep_test(Z, name):
        obs = loo_balanced_accuracy(Z, labels)
        null = []
        for _ in range(N_NULL):
            perm = labels[:]; rnd.shuffle(perm)
            null.append(loo_balanced_accuracy(Z, perm))
        maj = max(labels.count("meccan"), labels.count("medinan")) / len(labels)
        return {
            "feature_set": name,
            "balanced_accuracy": round(obs, 4),
            "null": summarise(null), "p": round(pval(null, obs), 4),
            "majority_baseline": round(maj, 4),
            "separates": bool(obs > max(null)),
        }
    B_full = sep_test(Zfull, "shape+length")
    B_shape = sep_test(Zshape, "shape-only")
    test_B = {
        "question": "does revelation period (meccan/medinan) separate in stylometric space?",
        "with_length": B_full, "shape_only": B_shape,
        "interpretation": ("style EVOLVES meccan->medinan; this is the honest opposite of "
                           "'perfectly uniform style'. Shape-only result shows whether the "
                           "separation survives removing raw length."),
        "confidence": "قوی" if B_full["p"] <= 0.01 and B_shape["p"] <= 0.05 else
                      ("محتمل" if B_full["p"] <= 0.05 else "نامشخص"),
    }

    # ── TEST C — hidden heterogeneity beyond period+length ──
    type_dummy = [1.0 if sura_feat[s]["type"] == "medinan" else 0.0 for s in sura_ids]
    logn = [math.log(sura_feat[s]["n_ayat"]) for s in sura_ids]
    design = [[1.0, type_dummy[i], logn[i]] for i in range(len(sura_ids))]
    resid_cols = []
    for k in shape_keys:
        y = [sura_feat[s][k] for s in sura_ids]
        resid_cols.append(ols_residuals(y, design))
    resid_rows = zscore_columns([list(r) for r in zip(*resid_cols)])
    obs_C = kmeans2_varexp(resid_rows, random.Random(SEED))
    null_C = []
    for _ in range(N_NULL):
        cols = [c[:] for c in zip(*resid_rows)]
        for c in cols:
            rnd.shuffle(c)
        permrows = [list(r) for r in zip(*cols)]
        null_C.append(kmeans2_varexp(permrows, random.Random(SEED)))
    test_C = {
        "question": "after removing period+length, is there latent multi-style structure?",
        "statistic": "2-means variance explained on residual shape features",
        "observed": round(obs_C, 4), "null": summarise(null_C),
        "p": round(pval(null_C, obs_C), 4),
        "verdict": ("excess latent clustering — inspect" if obs_C > max(null_C)
                    else "no structure beyond period+length — consistent with a single evolving idiolect"),
        "confidence": "محتمل" if obs_C > max(null_C) else "قوی",
    }

    # ── TEST D — register x period ──
    asp = defaultdict(lambda: Counter())
    for r in aspect_rows:
        asp[r["s"]][r["aspect"]] = r["c"]
    g = Counter()
    for s in asp:
        g.update(asp[s])
    proc_total = g["IMPF"] + g["IMPV"]
    overall_share = proc_total / (proc_total + g["PERF"])

    def proc_share(s):
        c = asp[s]; pr = c["IMPF"] + c["IMPV"]; tot = pr + c["PERF"]
        return pr / tot if tot else None
    per_sura = {s: proc_share(s) for s in sura_ids if proc_share(s) is not None}
    mec = [v for s, v in per_sura.items() if sura_feat[s]["type"] == "meccan"]
    med = [v for s, v in per_sura.items() if sura_feat[s]["type"] == "medinan"]
    obs_D = statistics.mean(mec) - statistics.mean(med)
    pooled = list(per_sura.items())
    types = [sura_feat[s]["type"] for s, _ in pooled]
    vals = [v for _, v in pooled]
    null_D = []
    for _ in range(N_NULL):
        perm = types[:]; rnd.shuffle(perm)
        a = [vals[i] for i in range(len(vals)) if perm[i] == "meccan"]
        b = [vals[i] for i in range(len(vals)) if perm[i] == "medinan"]
        null_D.append(abs(statistics.mean(a) - statistics.mean(b)))
    p_D = (sum(1 for x in null_D if x >= abs(obs_D)) + 1) / (N_NULL + 1)
    test_D = {
        "question": "is the corpus process/command-leaning, and does register shift by period?",
        "overall_process_share": round(overall_share, 4),
        "legacy_claim_52_7pct": "confirmed" if abs(overall_share - 0.527) < 0.01 else "differs",
        "meccan_mean_process_share": round(statistics.mean(mec), 4),
        "medinan_mean_process_share": round(statistics.mean(med), 4),
        "diff_meccan_minus_medinan": round(obs_D, 4),
        "null_abs_diff": summarise(null_D), "p": round(p_D, 4),
        "verdict": ("register differs by period" if p_D <= 0.05 else "no period difference in register"),
        "note": ("overall share confirms the legacy 52.7% descriptively; '>0.5' alone is a neutral "
                 "reference, not a 'static text' model — a true distinctiveness test needs control corpora (deferred)."),
        "confidence": "قوی" if p_D <= 0.01 else ("محتمل" if p_D <= 0.05 else "نامشخص"),
    }

    # ── write artifacts ──
    results = {
        "method": "L11-stylometry-1.0", "seed": SEED, "n_null": N_NULL,
        "ayat": total_ayat, "suras": len(sura_ids),
        "scope_note": ("Internal-only. No control corpus => NO claim of distinctiveness from human "
                       "writing. 'Superhuman/i'jaz' is OUT OF SCOPE and marked UNKNOWN — stylometry "
                       "cannot reach it."),
        "test_A_fawasil_cohesion": test_A,
        "test_B_meccan_medinan_separability": test_B,
        "test_C_hidden_heterogeneity": test_C,
        "test_D_register_by_period": test_D,
    }
    (out / "stylometry_tests.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "ayah_features.json").write_text(
        json.dumps({"method": "L11-stylometry-1.0",
                    "features": {f"{s}:{a}": feats[(s, a)] for (s, a) in keys}},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "sura_features.json").write_text(
        json.dumps({"method": "L11-stylometry-1.0",
                    "suras": {str(s): sura_feat[s] for s in sura_ids}},
                   ensure_ascii=False, indent=1), encoding="utf-8")

    if not args.quiet:
        print("L11 — Stylometric & prosodic self-structure\n")
        print(f"  ayat: {total_ayat}   suras: {len(sura_ids)}   null: {N_NULL}\n")
        a = test_A
        print(f"  A FAWASIL COHESION:  obs={a['observed']}  null={a['null']['mean']}±{a['null']['sd']}"
              f" (max {a['null']['max']})  p={a['p']}  fold={a['fold']}x  → {a['verdict']} [{a['confidence']}]")
        b1, b2 = B_full, B_shape
        print(f"  B MECCAN/MEDINAN:    +len bal-acc={b1['balanced_accuracy']} (null max {b1['null']['max']}, "
              f"p={b1['p']});  shape-only bal-acc={b2['balanced_accuracy']} (p={b2['p']})  [{test_B['confidence']}]")
        c = test_C
        print(f"  C HIDDEN STRUCTURE:  obs={c['observed']}  null max={c['null']['max']}  p={c['p']}  → {c['verdict']} [{c['confidence']}]")
        d = test_D
        print(f"  D REGISTER x PERIOD: process={d['overall_process_share']} (legacy {d['legacy_claim_52_7pct']}); "
              f"meccan {d['meccan_mean_process_share']} vs medinan {d['medinan_mean_process_share']}  "
              f"p={d['p']}  → {d['verdict']} [{d['confidence']}]")
        print("\n  Scope: internal-only; no control corpus; 'superhuman' = UNKNOWN (out of scope).")


if __name__ == "__main__":
    main()
