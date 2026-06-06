#!/usr/bin/env python3
"""
Monad — Phase 7 validator: Semantic Revelation Engine
=====================================================

Verifies structural integrity, internal consistency, evidence grounding, the
no-imported-meaning invariant (names must be Quran-internal Arabic tokens that
appear among the concept's own members), and — with --rebuild — byte-identical
reproducibility of generated/revelation/.

Usage:
    python3 scripts/validate_revelation.py [--rebuild]
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

OUT = Path("generated/revelation")
IDENT = Path("generated/identification")
FILES = [
    "concept_dossiers.json", "semantic_fields.json", "ayah_identity_profiles.json",
    "root_consistency.json", "candidate_names.json", "core_revelation.json",
    "identity_confidence.json", "falsification_results.json", "revelation_manifest.json",
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


def load(d, name):
    return json.loads((d / name).read_text("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    v = V()
    print("Monad Phase 7 — validating Semantic Revelation Engine")

    for f in FILES:
        v.check((OUT / f).exists(), f"missing output {f}")
    if v.failed:
        print("  aborting: outputs missing — run build_revelation.py first")
        sys.exit(1)

    dossiers = load(OUT, "concept_dossiers.json")
    fields = load(OUT, "semantic_fields.json")
    aprof = load(OUT, "ayah_identity_profiles.json")
    cons = load(OUT, "root_consistency.json")
    names = load(OUT, "candidate_names.json")
    core = load(OUT, "core_revelation.json")
    conf = load(OUT, "identity_confidence.json")
    fal = load(OUT, "falsification_results.json")
    man = load(OUT, "revelation_manifest.json")

    # reference: each concept's member roots/lemmas (for no-imported-meaning check)
    dom_roots = load(IDENT, "dominant_roots.json")["concepts"]
    dom_lemmas = load(IDENT, "dominant_lemmas.json")["concepts"]

    cids = sorted(dossiers["concepts"].keys())
    v.check(len(cids) == 103, f"expected 103 concepts, got {len(cids)}")

    for name, obj in [("dossiers", dossiers), ("fields", fields), ("aprof", aprof),
                      ("cons", cons), ("names", names), ("core", core), ("conf", conf),
                      ("fal", fal), ("man", man)]:
        v.check(obj["method"] == "phase7-revelation-1.0", f"{name}.method mismatch")

    for prod, label in [(fields["concepts"], "semantic_fields"),
                        (aprof["concepts"], "ayah_identity_profiles"),
                        (cons["concepts"], "root_consistency"),
                        (names["concepts"], "candidate_names"),
                        (conf["concepts"], "identity_confidence"),
                        (fal["concepts"], "falsification")]:
        v.check(sorted(prod.keys()) == cids, f"{label} concept set mismatch")

    tier_count = {"strong": 0, "moderate": 0, "weak": 0, "resists": 0}
    for cid in cids:
        # member arabic sets — names must come only from these (no imported meaning)
        member_root_ar = {x["root_arabic"] for x in dom_roots[cid]["roots"]}
        member_lemma_ar = {x["lemma_arabic"] for x in dom_lemmas[cid]["lemmas"]}

        nm = names["concepts"][cid]
        v.check(nm["n_candidates"] == len(nm["candidates"]), f"{cid} n_candidates mismatch")
        v.check(nm["n_candidates"] <= 5, f"{cid} more than 5 candidates")
        prev = 1.01
        for c in nm["candidates"]:
            # NO IMPORTED MEANING: the name and its anchor must be Quran-internal members
            v.check(c["anchor_root_arabic"] in member_root_ar,
                    f"{cid} candidate anchor root not a member root (imported meaning?)")
            v.check(c["name_arabic"] in member_lemma_ar or c["name_arabic"] in member_root_ar,
                    f"{cid} candidate name not a member lemma/root (imported meaning?)")
            v.check(c["confidence"] >= 0.15 - 1e-9, f"{cid} candidate below NAME_MIN_CONF")
            v.check(c["confidence"] <= prev + 1e-9, f"{cid} candidates not confidence-sorted")
            prev = c["confidence"]
        v.check(nm["resists_identification"] == (nm["n_candidates"] == 0),
                f"{cid} resists flag inconsistent")

        # identity_confidence consistency with names + falsification
        cf = conf["concepts"][cid]
        tier_count[cf["tier"]] = tier_count.get(cf["tier"], 0) + 1
        if nm["n_candidates"] == 0:
            v.check(cf["tier"] == "resists", f"{cid} 0 names but tier != resists")
            v.check(cf["top_candidate_name"] is None, f"{cid} resists but has top name")
        else:
            v.check(cf["top_candidate_name"] == nm["candidates"][0]["name_arabic"],
                    f"{cid} identity top name mismatch")
            v.check(cf["tier"] in ("strong", "moderate", "weak"), f"{cid} bad tier")

        # falsification: tested iff has candidates
        fr = fal["concepts"][cid]
        v.check(fr.get("tested", False) == (nm["n_candidates"] > 0),
                f"{cid} falsification tested flag mismatch")
        if fr.get("tested"):
            v.check(0.0 <= fr["contradicting_ayah_fraction"] <= 1.0, f"{cid} ayah fraction range")
            v.check(0.0 <= fr["falsification_pressure"] <= 1.0, f"{cid} pressure range")
            v.check(fr["survives"] == (fr["falsification_pressure"] < 0.5),
                    f"{cid} survives/pressure inconsistent")

        # root_consistency ranges
        rc = cons["concepts"][cid]
        v.check(0.0 <= rc["identity_coherence_hhi"] <= 1.0, f"{cid} HHI range")
        v.check(0.0 <= rc["identity_ambiguity_entropy"] <= 1.0 + 1e-9, f"{cid} entropy range")
        v.check(rc["verdict"] in ("coherent_single", "coherent_dominant",
                                  "diffuse_unified", "fragmented"), f"{cid} bad verdict")

        # semantic fields: members are member roots; sizes sum to root_count
        sf = fields["concepts"][cid]
        total_in_fields = sum(f["size"] for f in sf["semantic_fields"])
        v.check(total_in_fields == len(dom_roots[cid]["roots"]),
                f"{cid} field sizes do not partition roots")
        for f_ in sf["semantic_fields"]:
            for mr in f_["member_roots"]:
                v.check(mr["root_arabic"] in member_root_ar, f"{cid} field root not a member")

        # dossier present
        v.check(dossiers["concepts"][cid]["concept_id"] == cid, f"{cid} dossier id mismatch")

    # tier totals match manifest
    v.check(man["totals"]["identity_tiers"] == conf["tier_counts"],
            "manifest tiers != identity_confidence tiers")
    v.check(sum(tier_count.values()) == 103, "tier totals != 103")
    v.check(man["totals"]["resists_identification"] == tier_count["resists"],
            "manifest resists count mismatch")

    # core revelation grounding
    for c in ("CONCEPT_007", "CONCEPT_016", "CONCEPT_081"):
        v.check(c in core["deep_revelation"], f"core missing {c}")
    v.check(len(core["largest_scc_members"]) == 9, "core SCC members != 9")
    v.check(len(core["top_foundational_concepts"]) == 20, "core top foundational != 20")
    for cid, d in core["deep_revelation"].items():
        v.check("evidence_graph" in d and "nodes" in d["evidence_graph"],
                f"{cid} missing evidence graph")

    # output_bytes match disk
    for f in FILES:
        if f in man["output_bytes"]:
            v.check(man["output_bytes"][f] == (OUT / f).stat().st_size,
                    f"manifest output_bytes[{f}] mismatch")

    if args.rebuild:
        print("  --rebuild: hashing, rebuilding, re-hashing …")
        before = {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in FILES}
        res = subprocess.run([sys.executable, "scripts/build_revelation.py"],
                             capture_output=True, text=True)
        v.check(res.returncode == 0, f"rebuild failed: {res.stderr[-400:]}")
        for f in FILES:
            after = hashlib.sha256((OUT / f).read_bytes()).hexdigest()
            v.check(after == before[f], f"{f} not byte-identical after rebuild")

    ok = v.summary()
    print("  identity tiers:", tier_count)
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
