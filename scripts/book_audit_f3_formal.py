#!/usr/bin/env python3
"""
Phase F3 — The "formal" leg of the CFS claim.

Claim component: "the Quran is a FORMAL system." We apply the six standard requirements
of a formal axiomatic system (the same checklist the author's own GitHub audit applied to
the book) to the QURAN, scoring each from this repo's validated layers. A "formal system"
in mathematical logic needs: formal language, explicit axioms, inference rules, proof
calculus, derivable theorems, consistency (+ arithmetic encodability for Gödel to bite).
"""
import json

# evidence pulled from validated layers
L6 = json.load(open("generated/layers/L6_network/intertextual_test.json"))
NUM = json.load(open("generated/numerics/significance_results.json"))
F1 = json.load(open("generated/book-quran-audit/f1_consistency.json"))
F2 = json.load(open("generated/book-quran-audit/f2_axiomatic.json"))

criteria = [
 ("FR-01 formal language / alphabet / grammar", "ABSENT", 10,
  "Natural-language Arabic; no formal symbolic alphabet or WFF grammar. L1 letter-layer "
  "test was a negative finding (letters carry no recoverable structure)."),
 ("FR-02 explicit, finite, minimal axioms", "PARTIAL", 40,
  f"A single dominant generative core exists, but no explicit axiom list and recovering "
  f"80% of structure needs 57% of concepts (F2: proto-axiomatic, residue "
  f"{F2['evidence']['irreducible_residue_fraction']})."),
 ("FR-03 explicit inference rules", "ABSENT", 5,
  "No stated inference rules; none are formalised in the text."),
 ("FR-04 proof calculus / derivation system", "ABSENT", 5,
  "No proof calculus (no Hilbert / natural-deduction / sequent structure)."),
 ("FR-05 derivable theorems (verses entail/explain others)", "PARTIAL", 55,
  f"Derivation-LIKE structure is real and validated: the L6 network predicts a verse's "
  f"content from related verses at {L6['all_target_roots']['network_hit']:.3f} vs random "
  f"{L6['all_target_roots']['random_null']['mean']:.3f} (p={L6['all_target_roots']['p']}); "
  f"rare-content {L6['rare_target_roots']['network_hit']:.2f} vs "
  f"{L6['rare_target_roots']['random_null']['mean']:.3f}. But this is semantic entailment, "
  "not formal proof."),
 ("FR-06 consistency", "MET", 95,
  f"F1: global consistency {F1['evidence']['global_consistency_index']:.2f}, "
  f"0 surviving genuine contradictions across "
  f"{F1['evidence']['n_relations_tested']} relations."),
 ("FR-09 arithmetic encodability (Gödel eligibility)", "ABSENT", 5,
  f"Numerics layer: {NUM['n_survive_bonferroni']} of 499 well-posed tests survive "
  f"Bonferroni/FDR (min p={NUM['min_p_value']:.4f}); number-blind protocol. No robust "
  "arithmetic structure -> Gödel's theorems do not apply."),
]

score = round(sum(c[2] for c in criteria)/len(criteria))
met = sum(1 for _,st,_,_ in criteria if st=="MET")
partial = sum(1 for _,st,_,_ in criteria if st=="PARTIAL")
absent = sum(1 for _,st,_,_ in criteria if st=="ABSENT")

res = {
 "leg": "formal",
 "criteria": [{"requirement": c[0], "status": c[1], "score": c[2], "evidence": c[3]} for c in criteria],
 "summary": {"met": met, "partial": partial, "absent": absent,
             "mean_score_0_100": score},
 "verdict": (
   "NOT A FORMAL SYSTEM (in the mathematical-logic sense). The Quran MEETS consistency "
   "(strong) and shows real, validated derivation-LIKE semantic structure, but lacks a "
   "formal language, explicit inference rules, and a proof calculus, and has no arithmetic "
   "encoding. Correct classification: a CONSISTENT, PROTO-FORMAL semantic system with a "
   "coherent generative core — the same class the author's own audit assigned to the book "
   "(Proto-Formal Axiomatic System). The word 'formal' in the author's claim is an "
   "over-statement; 'consistent and axiom-structured' is accurate."
 ),
}
json.dump(res, open("generated/book-quran-audit/f3_formal.json","w"),
          ensure_ascii=False, indent=2)
print(json.dumps(res, ensure_ascii=False, indent=2))
