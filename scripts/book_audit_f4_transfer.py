#!/usr/bin/env python3
"""
Phase F4 — The inheritance/transfer claim.

Author's syllogism: "(1) the Quran is a consistent formal axiomatic system (CFS);
(2) this book's reference is the Quran; therefore (3) this book is a CFS."

Two independent tests:
  (A) LOGICAL VALIDITY of the inference.
  (B) STRUCTURAL: does the book's axiom kernel actually coincide with the Quran's own
      generative kernel? If the book grafts axioms that are exogenous to the Quran's
      structure, it is a different (larger) system and cannot inherit the Quran's
      properties; CFS-ness would have to be earned independently.
We also note where the book's documented formal defects live (its own apparatus vs the
Quran).
"""
import json
from collections import Counter

cc = json.load(open("generated/concepts/concept_candidates.json"))["concepts"]
byid = {x["concept_id"]: x for x in cc}
fo = json.load(open("generated/compression/foundationality_scores.json"))["foundationality_order"][:15]
quran_hub_roots = []
for cid in fo:
    quran_hub_roots += [r["root_arabic"] for r in byid[cid].get("center_roots", [])[:5]]
hub_set = set(quran_hub_roots)

# Book's 15 named axioms -> grounding type (from Q2) + nearest Quranic root(s) + whether
# that theme is a Quran GENERATIVE HUB.  roots use the same orthography as the corpus.
AX = [
 ("A-000001","free will (ROOT axiom)",        "secular", []),
 ("A-000002","property from body",            "secular", ["ملك"]),
 ("A-000003","liberty needs divine grounding","bridge",  ["اله"]),
 ("A-000004","Tawhid",                         "theo",    ["اله","وحد"]),
 ("A-000005","no compulsion in religion",      "theo",    ["كره","دين"]),
 ("A-000006","resurrection",                   "theo",    ["بعث","قوم","يوم"]),
 ("A-000007","prophethood",                    "theo",    ["رسل","نبا"]),
 ("A-000008","property sovereignty (taslit)",  "bridge",  ["ملك","سلط"]),
 ("A-000009","dignitary equality",             "theo",    ["كرم","شعب"]),
 ("A-000010","accountability to God",          "theo",    ["حسب","يوم"]),
 ("A-000011","finite & minimal axioms",        "secular", []),
 ("A-000012","internal consistency (Godel)",   "secular", []),
 ("A-000013","normative priority over science","secular", []),
 ("A-000014","theory primacy over data",       "secular", []),
 ("A-000015","Mahdism / terminal condition",   "theo",    ["مهد","رسل"]),
]

rows = []
for aid, label, kind, roots in AX:
    on_hub = any(r in hub_set for r in roots)
    rows.append({"axiom": aid, "label": label, "kind": kind,
                 "nearest_roots": roots,
                 "maps_to_quran_generative_hub": bool(on_hub)})

theo = [r for r in rows if r["kind"]=="theo"]
secular = [r for r in rows if r["kind"]=="secular"]
theo_on_hub = sum(r["maps_to_quran_generative_hub"] for r in theo)
secular_on_hub = sum(r["maps_to_quran_generative_hub"] for r in secular)

res = {
 "claim": "Quran is CFS  AND  book references Quran  =>  book is CFS",
 "testA_logical_validity": {
   "valid": False,
   "reason": ("Invalid form. 'X references / is consistent-with a consistent system S' "
              "does not entail 'X is consistent' or 'X is formal'. Consistency and "
              "formality are properties of a system's OWN axioms+rules, not inherited by "
              "citation. Adding any axiom to S can break consistency; quoting S confers "
              "nothing. (Reference is not entailment; the conclusion does not follow.)"),
 },
 "testB_structural_overlap": {
   "quran_generative_hub_roots": sorted(hub_set),
   "book_axioms": rows,
   "theological_axioms_on_a_quran_hub": f"{theo_on_hub}/{len(theo)}",
   "secular_axioms_on_a_quran_hub": f"{secular_on_hub}/{len(secular)}",
   "root_axiom_free_will_on_quran_hub": False,
   "finding": ("The book's THEOLOGICAL axioms (Tawhid, prophethood, resurrection, "
               "accountability) sit on the Quran's own generative hubs — there the book "
               "really is Quran-anchored. But the book's ROOT axiom (free will) and its "
               "formal-system requirements (finite-axioms, consistency, theory-primacy, "
               "property=liberty) are EXOGENOUS to the Quran's generative kernel. The book "
               "is therefore a HYBRID system = Quran-derived theological content + imported "
               "secular-rational foundations, not 'the Quran's axiom system'."),
 },
 "testC_where_defects_live": {
   "quran_surviving_contradictions": 0,
   "book_formal_status_own_audit": "Proto-Formal, 39/100; CIRC-001 critical circularity "
       "('mysticism' defined as 'anti-liberty') — a book construct absent from the Quran.",
   "implication": ("The book's documented formal defects live in its OWN imported "
                   "apparatus, not in the Quran. So the book cannot be said to inherit the "
                   "Quran's consistency; it adds material, and the added material is exactly "
                   "where its formal problems are."),
 },
 "verdict": ("NOT SUPPORTED. The inference is logically invalid, and structurally the book "
             "adds load-bearing axioms exogenous to the Quran's kernel, so it is a distinct "
             "system that must earn CFS status on its own — which, by its own audit and by "
             "F3, neither it nor the Quran attains in the strict 'formal' sense. The book "
             "DOES faithfully inherit the Quran's real type: consistent + proto-formal."),
}
json.dump(res, open("generated/book-quran-audit/f4_transfer.json","w"),
          ensure_ascii=False, indent=2)
print(json.dumps(res, ensure_ascii=False, indent=2)[:2600])
