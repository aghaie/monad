#!/usr/bin/env python3
"""
Phase Q2 — Grounding coverage.

Question: are the book's *postulates* grounded in the Quran, or are the postulates
rational/formal with the Quran entering downstream as confirmation?

Inputs (vendored from the author's own Phase-0.9 extraction,
github.com/aghaie/Theory-of-Liberty-Religion-Iran):
  source_from_repo/32_axiom_audit.json    — 15 named axioms + dependencies + tiers
  source_from_repo/41_minimum_axiom_set.json — BFS coverage of axiom subsets
Plus this audit's q0 references (which axioms get a direct verse anchor).

We do three things:
  1. UNDERIVED test: which axioms are genuinely foundational (depends_on == [])?
  2. GROUNDING type: classify each axiom secular-rational / theological-Quranic / bridge.
  3. LOAD test: how much of the theory is reachable from the secular-only kernel?
"""
import json

BASE = "generated/book-quran-audit"
SRC = f"{BASE}/source_from_repo"

axioms = json.load(open(f"{SRC}/32_axiom_audit.json"))["named_axiom_audit"]
minset = json.load(open(f"{SRC}/41_minimum_axiom_set.json"))

# Grounding classification. "theological_quranic" = content is a claim about God /
# afterlife / revelation, sourced from scripture; "secular_rational" = free will, logic,
# natural-law property; "bridge" = links the two. verse_anchor: a direct verse the book
# attaches (from Q0/Q1 + manual identification of the canonical proof-text).
GROUND = {
 "A-000001": ("secular_rational",   None,    "free will — self-evident, presupposed by all"),
 "A-000002": ("secular_rational",   None,    "property from body — natural-law"),
 "A-000003": ("bridge",             None,    "liberty needs divine grounding (the pivot claim)"),
 "A-000004": ("theological_quranic","Tawhid theme (e.g. 3:64, 39 al-Zumar)", "no servitude but to God"),
 "A-000005": ("theological_quranic","2:256", "no compulsion in religion — la ikraha"),
 "A-000006": ("theological_quranic","resurrection theme (e.g. 7:187, 2 al-Baqara)", "resurrection stabilizes liberty"),
 "A-000007": ("theological_quranic","prophethood/khatam theme (e.g. 33:40)", "prophethood blocks false messiahs"),
 "A-000008": ("bridge",             None,    "taslit — sovereignty over property"),
 "A-000009": ("theological_quranic","49:13", "dignitary equality before God"),
 "A-000010": ("theological_quranic","accountability theme", "each accountable to God"),
 "A-000011": ("secular_rational",   None,    "finite & minimal axioms — meta-logic"),
 "A-000012": ("secular_rational",   None,    "internal consistency (Godel) — meta-logic"),
 "A-000013": ("secular_rational",   None,    "normative priority over science"),
 "A-000014": ("secular_rational",   None,    "theory primacy over data"),
 "A-000015": ("theological_quranic","Mahdism/terminal-condition theme", "terminal completion"),
}

print("="*78)
print("Q2.1  UNDERIVED TEST — what are the genuine (axiomatic) foundations?")
print("="*78)
underived = [a for a in axioms if not a["depends_on"]]
for a in underived:
    g = GROUND[a["axiom_id"]]
    print(f"  {a['axiom_id']}  [{g[0]:18}]  {a['text']}")
print(f"\n  -> {len(underived)} underived axioms; grounding types: "
      f"{sorted(set(GROUND[a['axiom_id']][0] for a in underived))}")

print("\n"+"="*78)
print("Q2.2  GROUNDING TYPE of all 15 named axioms")
print("="*78)
from collections import Counter
c = Counter(GROUND[a["axiom_id"]][0] for a in axioms)
for a in axioms:
    g = GROUND[a["axiom_id"]]
    anc = f"  <verse: {g[1]}>" if g[1] else ""
    dep = ",".join(a["depends_on"]) or "[]"
    print(f"  {a['axiom_id']}  T{a['tier']}  {g[0]:18} dep={dep:<28}{anc}")
print(f"\n  totals: {dict(c)}")

print("\n"+"="*78)
print("Q2.3  LOAD TEST — coverage reachable from each axiom subset (author's own BFS)")
print("="*78)
for e in minset["experiments"]:
    print(f"  {e['coverage']*100:5.1f}%  ({e['reachable_nodes']}/{minset['total_backbone_nodes']} nodes)  "
          f"set={e['set_size']:<2}  {e['label']}")

# the secular-only minimum kernel
sec_kernel = [a["axiom_id"] for a in underived
              if GROUND[a["axiom_id"]][0] == "secular_rational"]
print(f"\n  secular-only underived kernel = {sec_kernel}")
m = next((e for e in minset["experiments"] if set(e["axiom_set"]) == set(sec_kernel)), None)
if m:
    print(f"  -> already reaches {m['coverage']*100:.1f}% of the theory with NO theological axiom.")

# how many of the theological axioms carry a direct verse anchor
theo = [a for a in axioms if GROUND[a["axiom_id"]][0] == "theological_quranic"]
anchored = [a for a in theo if GROUND[a["axiom_id"]][1]]
print("\n"+"="*78)
print("Q2.4  Of theological axioms, how many have a direct Quran anchor?")
print("="*78)
print(f"  {len(anchored)}/{len(theo)} theological axioms are tied to specific verse(s).")
print("  Two carry a verifiable, faithfully-quoted verse (Q1): A-000005=2:256, A-000009=49:13.")

out = {
  "underived_axioms": [a["axiom_id"] for a in underived],
  "underived_all_secular": all(GROUND[a["axiom_id"]][0]=="secular_rational" for a in underived),
  "grounding_counts": dict(c),
  "secular_only_kernel": sec_kernel,
  "secular_kernel_coverage": (m["coverage"] if m else None),
  "theological_axioms": [a["axiom_id"] for a in theo],
  "theological_with_verse_anchor": [a["axiom_id"] for a in anchored],
}
json.dump(out, open(f"{BASE}/q2_grounding.json","w"), ensure_ascii=False, indent=2)
print("\nwrote", f"{BASE}/q2_grounding.json")
