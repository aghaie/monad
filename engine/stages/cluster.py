"""مرحلهٔ ۲ — خوشه‌بندیِ قطعی + هم‌آییِ معنادار vs نولِ بسامد."""
import random
import sqlite3
from collections import Counter, defaultdict

from domains.quran_root.adapter import DB_PATH

SEED = 20260626


def _signature(features):
    return f"pos={features.get('pos')}|aspect={features.get('aspect') or 'NA'}"


def _coroot_counts(evidence):
    """شمار هم‌آییِ ریشه‌های دیگر در آیاتِ حاویِ این unit."""
    ayat = sorted({(e["locus"]["surah"], e["locus"]["ayah"]) for e in evidence})
    co = Counter()
    with sqlite3.connect(str(DB_PATH)) as c:
        for (s, a) in ayat:
            for (rid, ar) in c.execute(
                "SELECT DISTINCT w.root_id, r.root_arabic FROM words w "
                "JOIN roots r ON w.root_id=r.root_id "
                "WHERE w.surah_number=? AND w.ayah_number=? AND w.root_id IS NOT NULL",
                (s, a)):
                co[(rid, ar)] += 1
        total_ayat = c.execute("SELECT COUNT(*) FROM ayahs").fetchone()[0]
        global_doc = {}
        for (rid, ar), _ in co.items():
            n = c.execute("SELECT COUNT(DISTINCT surah_number||':'||ayah_number) "
                          "FROM words WHERE root_id=?", (rid,)).fetchone()[0]
            global_doc[(rid, ar)] = n
    return co, len(ayat), total_ayat, global_doc


def run(extract_payload, seed=SEED):
    evidence = extract_payload["evidence"]
    groups = defaultdict(list)
    for e in evidence:
        groups[_signature(e["features"])].append(e["evidence_id"])
    clusters = [{"cluster_id": f"c{i}", "signature": sig, "members": sorted(mem),
                 "size": len(mem)}
                for i, (sig, mem) in enumerate(sorted(groups.items()))]

    co, n_ayat, total_ayat, gdoc = _coroot_counts(evidence)
    rng = random.Random(seed)
    patterns = []
    for i, ((rid, ar), obs) in enumerate(co.most_common()):
        if obs < 3:
            continue
        expected = n_ayat * (gdoc[(rid, ar)] / total_ayat)
        lift = round(obs / expected, 3) if expected else 0.0
        # نولِ جایگشتیِ ساده و قطعی
        ge = 0
        for _ in range(200):
            sample = rng.sample(range(total_ayat), n_ayat)
            if sum(1 for _ in sample if _ < gdoc[(rid, ar)]) >= obs:
                ge += 1
        patterns.append({"pattern_id": f"p{i}", "type": "cooccurrence",
                         "with": ar, "with_root_id": rid, "observed": obs,
                         "lift": lift, "null_p": round(ge / 200, 4),
                         "support": [ar]})
        if len(patterns) >= 20:
            break
    return {"method": {"algorithm": "feature-signature", "seed": seed,
                       "feature_space": ["pos", "aspect"]},
            "clusters": clusters, "patterns": patterns}
