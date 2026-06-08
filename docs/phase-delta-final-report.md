# Phase Δ — Final Report: Quranic Decision Architecture Discovery Engine

**Method version:** `decision-architecture-1.0` · **Date:** 2026-06-08. Deterministic, byte-identical
(`validate_decision_architecture.py --rebuild`). The phase asks "how does the Quran decide?", not "what
does it say." No human decision framework (decision theory, ethics, AI planning, psychology) is imposed.

## 1. Objective
If the Quran were treated as a decision-making system, what decision architecture emerges from the text
itself — decision events, triggers, information use, uncertainty/conflict/priority handling, outcome
evaluation, recursive loops — and does it survive falsification?

## 2. Method (summary)
Decision nodes are corpus structures: COND (conditional particles) + decision-vocabulary root-groups
(choice, action, consequence, uncertainty, knowledge, conflict, resolution, priority, evaluation).
Direction = within-ayah word order + cross-ayah adjacency. Every candidate edge is attacked with a
**frequency** null (exists beyond frequency?) and a **mushaf-order** null (directional beyond order?),
then a **bootstrap + subsampling** stability battery. Verdict from pre-registered thresholds.

## 3. Results (headline)
| metric | value |
|---|--:|
| COND (conditional) tokens | 1,049 |
| candidate decision edges | 45 |
| exist beyond the frequency null | **4 / 45 (8.9%)** |
| directionally stable (bootstrap+subsample) | 13 / 45 |
| **full survivors (all controls)** | **3** |
| largest connected survivor backbone | 3 nodes (no loop) |

---

## The ten final answers

### Q1 — Does a coherent decision architecture emerge? (YES / NO / PARTIAL)
**NO.** Only **8.9%** of candidate decision edges exist beyond the frequency null (below the 10%
threshold), and the survivors form no connected agent. A coherent decision architecture does **not**
emerge — the apparent one is overwhelmingly a frequency artifact. *(Borderline note: 8.9% vs the 10%
cutoff; 3 isolated components do survive — so "NO coherent architecture" with a thin robust residue.)*

### Q2 — How many robust decision components survive?
**3:** `condition → choice`, `knowledge → resolution`, `knowledge → uncertainty`.

### Q3 — How are decisions initiated?
By **conditional structure** — 1,049 COND ("if … then") particles, and the one robust trigger edge is
`condition → choice` (conditionals precede choice/command; support 861, dir 0.60). This is the single
genuinely decision-shaped survivor.

### Q4 — How is uncertainty handled?
**Not robustly.** The strongest "uncertainty" edge, `knowledge → uncertainty`, is the fixed collocation
*عالِم الغيب* ("knower of the unseen"), not a decision-under-uncertainty operation. No distinct
uncertainty-handling architecture survives.

### Q5 — How are conflicts resolved?
**Not by a distinct mechanism.** `conflict → resolution` does not survive; the surviving residue is the
generic `knowledge → resolution` (judgment follows knowledge). No robust conflict-resolution architecture.

### Q6 — How are priorities established?
**No robust priority architecture.** Preference vocabulary (فضل/قدم) is present but every priority edge
collapses under the controls.

### Q7 — What is the minimal reconstructed decision architecture?
Three isolated edges — `condition → choice`, `knowledge → resolution`, `knowledge → uncertainty` — of
which only the first two are decision-shaped and the third is a collocation. **They form no agent loop.**
The minimal "agent" is not an agent: two robust decision motifs (if-then-choose; know-then-judge) in an
otherwise frequency-driven graph.

### Q8 — Does the architecture survive falsification? (YES / NO / PARTIAL)
**PARTIAL.** 3 of 45 components survive; 42 collapse. A few isolated motifs are robust; the architecture
as a whole is not.

### Q9 — What is the strongest reproducible discovery?
**`condition → choice`** — conditional structure precedes choice/command (support 861, survives frequency,
order, bootstrap, and subsampling). It is the corpus's one robust, decision-meaningful structure: the Quran
does robustly link *if/when* to *choose/command*. (The higher-directionality `knowledge → uncertainty` is
the عالِم الغيب collocation, not a decision operation.)

### Q10 — What remains unknown?
The **content** of decisions — *which* specific choice is made — is the irreducible lexical-referential
residual (Phase Ψ). The architecture is **form**, not content. We do not know what is decided, only the
structural shape of deciding; and even that shape reduces, under controls, to two robust motifs.

---

## 4. Interpretation
Treating the Quran as a decision system, the apparent architecture is rich descriptively (45 edges,
1,049 conditionals) but **collapses under controls**: 91% of decision edges are frequency artifacts, no
recursive loop survives, and no coherent agent is reconstructable. What remains is **two robust decision
motifs** — *conditional → choice* ("if … then choose/command") and *knowledge → resolution* ("know then
judge") — plus one collocation. This is fully consistent with the project's arc: Phase X's epistemic
pipeline and Phase Z's self-method also collapsed to a handful of edges under the same controls; Phase R's
*deed → recompense* survived and is the action↔consequence regularity that Δ's evaluation loop does not
add to; Phase P showed the structure is non-predictive. The decision "architecture" is, like the rest, a
thin robust residue in a frequency-dominated text.

## 5. Falsification Attempts
Every component was attacked by frequency and order nulls plus bootstrap/subsampling. 42 of 45 edges
failed; no loop survived; no coherent agent survived. The negative-leaning result is the pre-registered,
honest outcome (the spec accepts both success and collapse).

## 6. Limitations
- Decision nodes are the chosen vocabulary + COND; a different operationalization could shift which 2–3
  edges survive, but the collapse pattern (≈ 9% exist beyond frequency, 3 survivors, no loop) is the
  finding.
- Q1 is borderline NO/PARTIAL (8.9% vs the 10% cutoff); reported as NO per pre-registration, with the 3
  survivors flagged.
- "Decision" is operationalized structurally; the semantic content of decisions is forbidden and unknown.

## 7. Conclusion
**No coherent decision architecture emerges (Q1 = NO); 3 of 45 components survive falsification (Q8 =
PARTIAL).** The robust residue is two decision motifs — **conditional → choice** (the strongest) and
**knowledge → resolution** — isolated, not a loop, not an agent. The Quran links *if* to *choose* and
*knowing* to *judging*; beyond that, its apparent decision architecture is frequency-driven, and what is
actually decided remains the unknown referential content.

---

### Outputs
`generated/decision_architecture/`: 11 data products + `decision_manifest.json`. Tooling:
`scripts/build_decision_architecture.py`, `scripts/validate_decision_architecture.py`. Reports:
`decision-events-report.md`, `decision-triggers-report.md`, `information-usage-report.md`,
`uncertainty-report.md`, `conflict-resolution-report.md`, `priority-report.md`,
`outcome-evaluation-report.md`, `decision-loops-report.md`, `agent-architecture-report.md`,
`decision-falsification-report.md`, `decision-stability-report.md`, this report.

### Reproduce
```bash
python3 scripts/build_decision_architecture.py
python3 scripts/validate_decision_architecture.py --rebuild
```

**Phase Δ complete. No further phase started automatically.**
