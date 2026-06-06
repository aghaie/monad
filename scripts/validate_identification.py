#!/usr/bin/env python3
"""
Monad — Phase 6 validator: Concept Identification Engine
========================================================

Verifies structural integrity, internal consistency, evidence grounding, and
(with --rebuild) byte-identical reproducibility of the Phase-6 outputs in
generated/identification/. No meaning is assigned or checked; only evidence
shape and arithmetic.

Usage:
    python3 scripts/validate_identification.py [--rebuild]
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

OUT = Path("generated/identification")
FILES = [
    "concept_profiles.json", "dominant_roots.json", "dominant_lemmas.json",
    "ayah_signatures.json", "surah_signatures.json", "concept_atlas.json",
    "core_investigation.json", "identification_manifest.json",
]


class V:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def check(self, cond, msg):
        if cond:
            self.passed += 1
        else:
            self.failed += 1
            print(f"  ✗ FAIL: {msg}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n  {self.passed}/{total} checks passed.")
        return self.failed == 0


def load(name):
    return json.loads((OUT / name).read_text("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true",
                    help="rebuild and assert byte-identical outputs")
    args = ap.parse_args()
    v = V()

    print("Monad Phase 6 — validating Concept Identification Engine")

    # 0. presence
    for f in FILES:
        v.check((OUT / f).exists(), f"missing output {f}")
    if v.failed:
        print("  aborting: outputs missing — run build_identification.py first")
        sys.exit(1)

    profiles = load("concept_profiles.json")
    droots = load("dominant_roots.json")
    dlemmas = load("dominant_lemmas.json")
    asig = load("ayah_signatures.json")
    ssig = load("surah_signatures.json")
    atlas = load("concept_atlas.json")
    core = load("core_investigation.json")
    man = load("identification_manifest.json")

    cids = sorted(profiles["concepts"].keys())
    v.check(len(cids) == 103, f"expected 103 concepts, got {len(cids)}")
    v.check(profiles["n_concepts"] == 103, "profiles.n_concepts != 103")

    # method tag consistency
    for name, obj in [("profiles", profiles), ("droots", droots), ("dlemmas", dlemmas),
                      ("asig", asig), ("ssig", ssig), ("atlas", atlas), ("core", core),
                      ("man", man)]:
        v.check(obj["method"] == "phase6-identification-1.0", f"{name}.method mismatch")

    # every concept present in every per-concept product
    for prod, label in [(droots["concepts"], "dominant_roots"),
                        (dlemmas["concepts"], "dominant_lemmas"),
                        (asig["concepts"], "ayah_signatures"),
                        (ssig["concepts"], "surah_signatures"),
                        (atlas["concepts"], "concept_atlas")]:
        v.check(sorted(prod.keys()) == cids, f"{label} concept set mismatch")

    # ── per-concept consistency ─────────────────────────────────────────────────
    total_active_ayahs = set()
    for cid in cids:
        p = profiles["concepts"][cid]
        # root/lemma counts match membership lists
        v.check(p["root_count"] == len(p["member_roots"]), f"{cid} root_count mismatch")
        v.check(p["lemma_count"] == len(p["member_lemmas"]), f"{cid} lemma_count mismatch")
        v.check(droots["concepts"][cid]["root_count"] == p["root_count"],
                f"{cid} dominant_roots count mismatch")
        v.check(dlemmas["concepts"][cid]["lemma_count"] == p["lemma_count"],
                f"{cid} dominant_lemmas count mismatch")

        # activation_count consistency: profiles == ayah_sig == surah_sig total
        ac = p["activation_count"]
        v.check(asig["concepts"][cid]["activation_count"] == ac,
                f"{cid} ayah_sig activation_count mismatch")
        v.check(ssig["concepts"][cid]["total_activating_ayahs"] == ac,
                f"{cid} surah_sig total mismatch")
        # surah_distribution sums to activation_count
        v.check(sum(p["surah_distribution"].values()) == ac,
                f"{cid} surah_distribution sum != activation_count")
        v.check(ac <= 6101, f"{cid} activation_count exceeds active-ayah ceiling")

        # ayah-signature ordering: strengths non-increasing; depths bounded by activation
        top = asig["concepts"][cid]["top_100"]
        v.check(len(top) <= min(100, ac), f"{cid} top_100 too long")
        strengths = [a["activation_strength"] for a in top]
        v.check(strengths == sorted(strengths, reverse=True),
                f"{cid} ayah strengths not sorted")
        for a in top:
            v.check(0.0 <= a["confidence"] <= 1.0 + 1e-9, f"{cid} confidence out of range")
            v.check(a["member_token_count"] ==
                    len(a["contributing_roots"]) + len(a["contributing_lemmas"]),
                    f"{cid} member_token_count mismatch")

        # dominant-root ranking monotonic by activation_weight; share sums ~1
        rrows = droots["concepts"][cid]["roots"]
        w = [x["activation_weight"] for x in rrows]
        v.check(w == sorted(w, reverse=True), f"{cid} root activation_weight not sorted")
        if rrows:
            sh = sum(x["activation_share"] for x in rrows)
            v.check(abs(sh - 1.0) < 1e-3, f"{cid} root shares sum {sh} != 1")
            v.check([x["rank"] for x in rrows] == list(range(1, len(rrows) + 1)),
                    f"{cid} root ranks not sequential")

        lrows = dlemmas["concepts"][cid]["lemmas"]
        lw = [x["activation_weight"] for x in lrows]
        v.check(lw == sorted(lw, reverse=True), f"{cid} lemma activation_weight not sorted")

        # surah signature: density <= 1, lift >= 0, present count consistent
        for axis in ("highest_activation_surahs", "highest_density_surahs",
                     "highest_uniqueness_surahs"):
            for s in ssig["concepts"][cid][axis]:
                v.check(0.0 <= s["density"] <= 1.0 + 1e-9, f"{cid} {axis} density range")
                v.check(s["activating_ayahs"] <= s["surah_ayah_count"],
                        f"{cid} {axis} activating > surah size")

        # atlas: closest concepts != self
        for rc in atlas["concepts"][cid]["closest_concepts"]:
            v.check(rc["concept_id"] != cid, f"{cid} closest includes self")

    # ── manifest totals ─────────────────────────────────────────────────────────
    v.check(man["totals"]["concept_count"] == 103, "manifest concept_count")
    v.check(man["totals"]["active_ayahs"] == 6101, "manifest active_ayahs != 6101")
    v.check(man["totals"]["total_ayahs"] == 6236, "manifest total_ayahs != 6236")

    # output_bytes match on-disk sizes
    for f in FILES:
        nbytes = (OUT / f).stat().st_size
        if f in man["output_bytes"]:
            v.check(man["output_bytes"][f] == nbytes, f"manifest output_bytes[{f}] mismatch")

    # ── core investigation grounding ────────────────────────────────────────────
    v.check("CONCEPT_007" in core["deep_profiles"], "core missing CONCEPT_007")
    v.check("CONCEPT_016" in core["deep_profiles"], "core missing CONCEPT_016")
    v.check(len(core["top_foundational_concepts"]) == 20, "core top_foundational != 20")
    sizes = [c["size"] for c in core["largest_scc_structures"]]
    v.check(sizes == sorted(sizes, reverse=True), "SCC structures not size-sorted")
    v.check(sizes and sizes[0] == 9, "largest SCC size != 9")

    # ── byte-identical rebuild ──────────────────────────────────────────────────
    if args.rebuild:
        print("  --rebuild: hashing, rebuilding, re-hashing …")
        before = {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in FILES}
        res = subprocess.run([sys.executable, "scripts/build_identification.py"],
                             capture_output=True, text=True)
        v.check(res.returncode == 0, f"rebuild failed: {res.stderr[-400:]}")
        for f in FILES:
            after = hashlib.sha256((OUT / f).read_bytes()).hexdigest()
            v.check(after == before[f], f"{f} not byte-identical after rebuild")

    ok = v.summary()
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
