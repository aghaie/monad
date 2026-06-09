# Monad — Project Status

**Last updated:** 2026-06-09. **Current phase complete:** Phase ΩΣ (Foundational Question
Discovery) — **PARTIAL SUCCESS; 7/14 foundational questions get measurable structural answers,
7 are UNKNOWN or reduce to the frequency core**. **Next phase:** none — awaiting explicit
instruction.

Monad derives everything from the Quranic corpus itself. No external dictionary,
tafsir, translation, theology, or pre-trained embedding is used at any layer. Each
phase reads the previous phase's outputs and never rebuilds them.

---

## Phase ledger

| Phase | Title | Status | Primary outputs |
|---|---|---|---|
| 1 | Canonical Quran Database | ✅ complete | `generated/monad.db` |
| 2 | Quran Internal Lexicon Engine | ✅ complete | `generated/lexicon/*.json` |
| 3 | Concept Discovery Engine | ✅ complete | `generated/concepts/*.json` |
| 4 | Proposition Discovery Engine | ✅ complete | `generated/propositions/*.json` |
| 5 | Dependency Compression Engine | ✅ complete | `generated/compression/*.json` |
| 6 | Concept Identification Engine | ✅ complete | `generated/identification/*.json` |
| 7 | Semantic Revelation Engine | ✅ complete | `generated/revelation/*.json` |
| 8 | Foundational Principle Discovery Engine | ✅ complete | `generated/principles/*.json` |
| 9 | Structural Motif Discovery Engine | ✅ complete | `generated/motifs/*.json` |
| 10 | Contradiction & Consistency Discovery Engine | ✅ complete | `generated/consistency/*.json` |
| 11 | Discovery Stability & Robustness Engine (validation) | ✅ complete | `generated/validation/*.json` |
| 12 | Generative Grammar Discovery Engine | ✅ complete | `generated/grammar/*.json` |
| 13 | Revelation Evolution Engine | ✅ complete | `generated/evolution/*.json` |
| 14 | Structural Locality & Distribution Engine | ✅ complete | `generated/locality/*.json` |
| 15 | Consistency Propagation Engine | ✅ complete | `generated/consistency_propagation/*.json` |
| 16 | Hub Origin Discovery Engine | ✅ complete | `generated/hub_origin/*.json` |
| 17 | Frequency Null Model Engine | ✅ complete | `generated/frequency_null/*.json` |
| Ω | World Model Discovery Engine | ✅ complete | `generated/world_model/*.json` |
| Σ | Internal Semantic Reconstruction Engine | ✅ complete | `generated/semantics/*.json` |
| Q | Quranic Methodology Discovery Engine | ✅ complete | `generated/quranic_methodology/*.json` |
| R | Text → Reality Discovery Engine | ✅ complete | `generated/reality/*.json` |
| X | Epistemology Discovery Engine | ✅ complete | `generated/epistemology/*.json` |
| P | Structural Predictivity / Held-Out Information Engine | ✅ complete — **NON_PREDICTIVE** | `generated/predictivity/*.json` |
| Z | Quran Self-Method Discovery (falsification study) | ✅ complete — **PARTIAL (weak)** | `generated/self_methodology/*.json` |
| 19X | Blind Numerical Structure Discovery | ✅ complete — **no significant structure** | `generated/numerics/*.json` |
| Ω(B) | Explanation Boundary Discovery | ✅ complete — **~20% explained / ~80% residual** | `generated/explanation_boundary/*.json` |
| Ψ | Residual Nature Discovery | ✅ complete — **residual = lexical-referential specificity** | `generated/residual_nature/*.json` |
| Φ | Counterfactual Quran Discovery | ✅ complete — **TYPE_B weakly-constrained free selection** | `generated/counterfactual/*.json` |
| Δ | Quranic Decision Architecture | ✅ complete — **no coherent architecture; 3/45 survive** | `generated/decision_architecture/*.json` |
| Ξ | Foundation Audit & Representation Collapse | ✅ complete — **stable core PARTIAL; ~30% invariant** | `generated/foundation_audit/*.json` |
| ΩΣ | Foundational Question Discovery | ✅ complete — **PARTIAL; 7/14 answerable, 7 UNKNOWN/reduced** | `generated/foundational_questions/*.json` |

---

## Phase ΩΣ — Foundational Question Discovery Engine

Direction reversed: instead of hunting new structure, the engine asks the Quran **fourteen foundational
questions about itself** and answers each only from the corpus — reporting **UNKNOWN** wherever the question
needs semantics or external data the method forbids. Arabic anchors are evidence, never glossed.

- 8 data products + manifest. Operationalized on person frame (`features_raw`), verb aspect, POS classes,
  co-occurrence graph, proper-noun removal, interrogative/negation lift, ring-symmetry geometry. Nulls:
  configuration null (Q9 coherence), within-surah order-shuffle null (Q12 geometry), frequency baselines;
  subsample stability; invariants re-verified at root/lemma/word (**3/3 agree**).
- **Answers.** Q3 human-or-world = **BOTH** (3rd-person world 59.5% in a 2nd/1st-person address frame
  40.5%); Q7 object-or-relation = **RELATIONS** (51.3% token mass, 45 edges/node); Q8 book-or-engine =
  **ENGINE** (process aspect 52.7%, 1,876 imperatives, 1,049 conditionals); Q9 name removal = **~95%
  survives** (PN = 5.0% of tokens; invariants unchanged → name-independent); Q11 time = **ASPECTUAL/
  RECURRENT** (PERF 47.3% ≈ IMPF 43.0%, 573 recurring roots); Q12 geometry = **NO ring-symmetry** beyond the
  order-null (z = −1.46, falsified); Q4/Q13 minimal core/essentiality = **the frequency hub**; Q1/Q2/Q14 =
  **UNKNOWN as semantics**, structurally = compression / redundancy / maximal allocation on the hub; Q5/Q6
  content = **UNKNOWN** (anaphora present, ratio 0.13); Q10 = **UNKNOWN** (chronology is external/forbidden;
  meccan 0.807 ≈ medinan 0.821 residual).
- **Convergence.** The deepest-sounding questions (Q1, Q2, Q13, Q14) collapse onto one structure — the
  frequency hub that survived Phase Ξ. A small distinct set is genuinely structural (Q3 address frame, Q7/Q8
  relational/engine, Q9 name-independence, Q11 aspectual time). **Verdict: PARTIAL SUCCESS** — the corpus
  answers what is structural and refuses what is semantic.
- Reports: `q1-minimization`…`q14-central-question`, `question-integration-report.md`,
  `omega-sigma-falsification-report.md`, `omega-sigma-stability-report.md`,
  `omega-sigma-representation-report.md`, `phase-omega-sigma-final-report.md`,
  `omega-sigma-executive-summary.md`. (Spec's `falsification-report.md`/`executive-summary.md` already exist
  and are immutable, so this phase's copies are `omega-sigma-*`.)
- Reproduce: `python3 scripts/build_foundational_questions.py` ·
  `python3 scripts/validate_foundational_questions.py --rebuild` (**68/68 checks, byte-identical**).

---

## Phase Ξ — Foundation Audit & Representation Collapse Engine

The project audits **its own foundations**: if the root→similarity→concept→proposition chain (Phases 2–4)
is wrong, what survives? **Nothing protected** — every discovery must re-earn survival across alternative
representations (root/lemma/word) and prior controls. Success = identify what remains true when the
original representation is removed, NOT confirm/protect prior work.

- 9 data products + manifest. 5 explicit assumptions (A1 roots · A2 similarity · A3 clustering · A4 edges
  · A5 graph); 3 information-theoretic invariants **measured** at root/lemma/word; 20 major discoveries
  classified by representation-dependence (TYPE_A/B/C/D); combined stress test
- **RESULT — most of Monad is representation-dependent; a small core survives:**
  - **3/3 invariants agree** across root/lemma/word: frequency skew (Gini 0.80/0.83/0.83), large residual
    (0.796/0.751/0.724), coherence-beyond-null (all levels) — measured, not asserted
  - **6/20 discoveries (30%) representation-invariant (TYPE_D):** frequency dominance, ~80% residual,
    non-predictivity, scale-invariance, coherence-beyond-null, lexical freedom — all **information-theoretic**
  - **11/20 (55%) representation-dependent or artifact:** the entire **conceptual edifice** (concepts,
    propositions, compression, identities, grammar, semantics, world-model, methodology — TYPE_C, 8) +
    failed/deflated phases (principles, decision architecture, numerical structure — TYPE_A, 3)
  - the load-bearing assumption is **A3 (concept clustering)** — method-relative (Phase 11 ARI 0.22);
    removing it collapses the conceptual canopy. The core survives removal of all five + combined stress
  - **Q-answers:** Q1 6 invariants · Q2 conceptual edifice + failed phases · Q3 HIGH dependence on 2–4 ·
    Q4 the 6 info-theoretic findings · Q5 **the ~80% residual / non-predictivity** (strongest invariant) ·
    Q6 stable core **PARTIAL** · Q7 ~30% survive / ~55% dependent · Q8 minimal trusted set = {frequency,
    ~80% residual, non-predictivity, scale-invariance, coherence-beyond-null}
- Builder: `scripts/build_foundation_audit.py`; Validator: `scripts/validate_foundation_audit.py` (57
  checks, byte-identical rebuild). Reports: `dependency-map-report.md`, `assumption-inventory-report.md`,
  `assumption-removal-report.md`, `representation-rebuild-report.md`, `representation-agreement-report.md`,
  `discovery-survival-report.md`, `invariant-discoveries-report.md`, `collapse-analysis-report.md`,
  `stress-test-report.md`, `phase-xi-final-report.md`

Foundation-audit verdict: the project's trustworthy residue is **small and information-theoretic** — when
Monad's own assumptions are removed, ~30% of discoveries survive (frequency dominance, the ~80% irreducible
residual, non-predictivity, scale-invariance, real-coherence-beyond-null), and the conceptual edifice (the
majority of the phases) does **not**. The audit confirms from the inside what the frequency-null arc
(15→16→17→P→Ω(B)→Ψ→Φ) already showed: the durable findings are the deflationary ones.

---

## Phase Δ — Quranic Decision Architecture Discovery Engine

Reframes the corpus as a **decision system**: "how does the Quran decide?" (not "what does it say?").
No human decision framework imposed (no decision theory / ethics / AI planning / psychology). Decision
nodes = COND (conditional particles) + decision-vocabulary root-groups; directed graph + the
Phase-Z-grade falsification (frequency + mushaf-order nulls) and stability (bootstrap + subsampling)
battery. Spec accepts collapse as a valid outcome.

- 11 data products + manifest. 1,049 COND tokens; 10 decision nodes; **45 candidate directed edges**
- **RESULT — no coherent decision architecture (deflation, as P/Z/Φ predicted):**
  - **only 4/45 edges (8.9%) exist beyond the frequency null** → **Q1 = NO** (a coherent architecture
    does not emerge; 91% are frequency artifacts)
  - 13/45 are bootstrap-stable, but **only 3 are also real beyond frequency** (stability over-credits ~4×)
  - **3 full survivors**, isolated (no agent loop): **`condition→choice`** (if→choose/command, support
    861 — the one genuinely decision-shaped, strongest robust discovery), **`knowledge→resolution`**
    (know→judge), **`knowledge→uncertainty`** (the *عالِم الغيب* "knower of the unseen" collocation, not
    a decision step)
  - no robust uncertainty-handling, conflict-resolution, priority, or recursive loop; no reconstructable
    agent
  - **Q-answers:** Q1 NO · Q2 3 · Q3 conditional structure · Q4 not robust (collocation) · Q5 no distinct
    mechanism (residue: knowledge→resolution) · Q6 no robust priority · Q7 two motifs, no loop · Q8
    survives-falsification PARTIAL · Q9 **condition→choice** · Q10 the decided CONTENT (Ψ referential
    residual) is unknown
- Builder: `scripts/build_decision_architecture.py`; Validator:
  `scripts/validate_decision_architecture.py` (283 checks, byte-identical rebuild). Reports:
  `decision-events-report.md`, `decision-triggers-report.md`, `information-usage-report.md`,
  `uncertainty-report.md`, `conflict-resolution-report.md`, `priority-report.md`,
  `outcome-evaluation-report.md`, `decision-loops-report.md`, `agent-architecture-report.md`,
  `decision-falsification-report.md`, `decision-stability-report.md`, `phase-delta-final-report.md`

Decision-architecture verdict: treated as a decision system, the Quran shows **no coherent architecture**
under controls — 91% of decision edges are frequency artifacts and no agent loop survives. The robust
residue is **two decision motifs** (conditional→choice; knowledge→resolution) plus one collocation,
isolated — fully consistent with X/Z (collapse), R (deed→recompense survives elsewhere), and P
(non-predictive). The Quran robustly links *if→choose* and *know→judge*; what is actually decided stays
the unknown referential content.

---

## Phase Φ — Counterfactual Quran Discovery Engine

Measures **selection**, not structure: given the discovered constraints, how large is the space of
alternative Quran-like texts, and how typical is the actual one? Reframes Ψ's ~80% residual as the
geometry of choice. Never evaluates truth/theology/revelation/origin — only selection/information/
alternatives. (Alternative counts computed **analytically/exactly** as typical-set 2^(N·H), not
Monte-Carlo.)

- 8 data products + manifest. Constraint set from Phase-11+ survivors; max-entropy alternative space;
  selection pressure on two axes (co-occurrence FORM vs lexical IDENTITY); typicality via 1000 generated
  frequency-valid alternatives
- **RESULT — weakly-constrained free selection:**
  - **alternative space ≈ 2^377,803** (frequency-valid; uniform 2^474,654) — astronomically large
  - **frequency** reduces the uniform per-draw choice by **20.4%**; **structure** reduces lexical-identity
    freedom by **0 generalizable bits** (Phase P)
  - **two axes (key nuance):** the actual Quran is **lexically TYPICAL** (specific words = ordinary draw
    from its own frequencies) but **structurally EXTREME** — z ≈ 306 more clustered than frequency-random
    text. The structural extremity is just *coherence* (the property of any real text vs word-salad),
    real (Phase 17) but non-generalizable (Phase P); it constrains co-occurrence FORM, not word IDENTITY
  - **Q-answers:** Q1 ~2^377,803 · Q2 form strongly / identity weakly constrained · Q3 lexically typical,
    structurally extreme · Q4 constraints explain lexical choices **NO** · Q5 ~8.50 bits/draw (~80%) free
    · Q6 **TYPE_B weakly-constrained selection** · Q7 the precise two-axis statement
  - **choice-residual = Phase Ψ residual:** the irreducible 80% IS the free lexical choice the constraints
    do not determine
- Builder: `scripts/build_counterfactual.py`; Validator: `scripts/validate_counterfactual.py` (48 checks,
  byte-identical rebuild). Reports: `constraint-inventory-report.md`, `alternative-space-report.md`,
  `selection-pressure-report.md`, `rare-choice-report.md`, `local-counterfactual-report.md`,
  `global-counterfactual-report.md`, `choice-residual-report.md`, `selection-classification-report.md`,
  `phase-phi-final-report.md`

Counterfactual verdict (selection geometry): the discovered constraints define an astronomically large
space (~2^377,803) of coherent alternative texts; the actual Quran is a **typical** member on lexical
identity (a coherent outlier only vs random word-salad); the constraints do **NOT** explain its specific
word choices — ~80% of the identity choice is free (weakly-constrained selection, TYPE_B). Monad
quantifies how much choice remained and how coherent the text is, but cannot derive which words were
chosen — and says nothing about why.

---

## Phase Ψ — Residual Nature Discovery Engine

Drills into the Ω(B) residual: **what KIND of thing is the unexplained ~80%?** Measurement only —
no interpretation, no theology, no imported meaning; success = the sentence "we do not know" becomes
**more precise**, not that the residual disappears.

- 9 data products + manifest. Decomposes the residual (surah-topical vs irreducible lexical),
  profiles long-range recurrence, tests lexical-vs-structural carriage, searches higher-order,
  attempts structure-only reconstruction, varies representation (root/lemma/word), measures
  compressibility, null-assaults, and classifies from evidence
- **RESULT — the residual is irreducible LEXICAL-REFERENTIAL specificity (TYPE_003):**
  - residual = 79.6% of uniform; **surah-topic does NOT compress it** (per-surah NLL 8.92 > global
    8.50, gain −0.42 bits) → **~100% irreducible lexical** at the per-ayah level
  - **carrier = lexical** (8.50 bits/root); structure adds **0 generalizable** bits (Phase P); a real
    in-sample association (1.72 bits) is non-predictive
  - **long-range: PARTIAL** — recurrence-lift 27.8× (d1) → 18.3× (d25) → 20.9× (d100): real long-range
    lexical recurrence (characteristic vocabulary repeats, beats surah-shuffle null) but **decays, not
    increasing** — lexical cohesion, not structural dependency
  - **higher-order: 0**; **reconstruction:** in-sample 0.280 > freq 0.207 (**overfitting**), out-of-sample
    fails (P) → not generalizably recoverable
  - **representation-independent:** residual 79.6% (root) / 75.1% (lemma) / 72.4% (word) — not a
    root-space artifact; **largely incompressible**
  - **Q-answers:** Q1 ~100% irreducible-lexical · Q2 lexical/referential · Q3 long-range PARTIAL · Q4
    compressible NO · Q5 referential specificity · Q6 remains-unexplained YES · Q7 the precise statement
    (below)
- Builder: `scripts/build_residual_nature.py`; Validator: `scripts/validate_residual_nature.py` (54
  checks, byte-identical rebuild). Reports: `residual-decomposition-report.md`, `long-range-report.md`,
  `referentiality-report.md`, `combinatorial-report.md`, `reconstruction-report.md`,
  `representation-sensitivity-report.md`, `compression-boundary-report.md`,
  `residual-taxonomy-report.md`, `residual-null-assault-report.md`, `phase-psi-final-report.md`

Residual-nature verdict (precise): the unexplained ~80% is **irreducible lexical-referential
specificity** — the identity of which root/concept occurs in each ayah; real (survives nulls), lexical
(not structural/higher-order/long-range), incompressible, representation-independent, non-derivable. It
is the same referential layer Σ and the World-Model phase could not recover, now measured in bits.
Monad can locate and bound it but cannot derive it — "we do not know" what it refers to, only that it
is referential specificity carried by lexical identity.

---

## Phase Ω(B) — Explanation Boundary Discovery Engine

Measures the **explanation frontier**: after all stable discoveries, how much of the Quran's
structure is explained vs unexplained? Measurement only — proves/disproves nothing, fills no
gap with interpretation, writes "we do not know" where the model stops. *(Named Ω(B) to avoid
collision with the earlier Phase Ω "World Model"; outputs in `generated/explanation_boundary/`,
final report `phase-explanation-boundary-final-report.md`.)*

- 9 data products + manifest. Object = ayah×root incidence; explanation = in-sample
  compression (bits) of per-root selection under cumulative models (uniform → frequency →
  co-occurrence); residual extracted, characterized, null-attacked, and extrapolated via Phase
  P as the out-of-sample ceiling
- **RESULT — the boundary is measured at frequency:**
  - NLL uniform 10.68 / frequency 8.50 / co-occurrence 14.53 bits → **frequency explains 20.4%**;
    the co-occurrence layer provides **NO usable compression** (worse in-sample by calibration;
    0 out-of-sample, Phase P) — so the maximum *generalizable* model is **frequency alone**
  - **Q1 explained ≈ 20.4%** (frequency); **Q2 unexplained ≈ 79.6%**
  - **Q3 residual stronger than nulls? PARTIAL** — residual co-occurrence signal 1.73 bits >
    frequency-null p95 1.28 (real structure) BUT non-predictive (Phase P): **structured yet
    unexplainable**
  - **Q4 frontier saturated? YES** — a 10× better model of this representation yields ~0
    generalizable gain (Phase P); the residual is **data/representation-limited, not
    model-limited**
  - **Q5 largest unknown region:** the specific referential/lexical content (which root/concept
    occurs where, beyond frequency) — the ~80% residual; real structure, no explanation; the
    same referential layer Σ and the World-Model phase showed never emerges. **We do not know it.**
- Builder: `scripts/build_explanation_boundary.py`; Validator:
  `scripts/validate_explanation_boundary.py` (51 checks, byte-identical rebuild). Reports:
  `discovery-inventory-report.md`, `explanatory-power-report.md`,
  `explanation-redundancy-report.md`, `residual-structure-report.md`,
  `residual-characterization-report.md`, `null-attack-report.md`,
  `explanation-frontier-report.md`, `future-knowledge-report.md`,
  `phase-explanation-boundary-final-report.md`

Explanation-boundary verdict: **~20% of the Quran's per-root structure is explained (by
frequency); ~80% is unexplained** — real co-occurrence structure (beats nulls) that is
non-predictive (P) and representation-limited (frontier saturated). The largest unknown is the
referential content of the text, measured precisely and left, by design, as "we do not know."

---

## Phase 19X — Blind Numerical Structure Discovery Engine

A **number-blind** search for non-random numerical structure, with the special (last,
mechanical) question of where 19 ranks — designed to be valid even if 19 had never been
claimed. No external data, no code-19 literature, no target number in any score or selection;
divisors **2..500 scanned uniformly**; 19 constructed indirectly (`DIV_MIN+17`) and examined
only after all controls. The scientific core is multiple-testing correction.

- 9 data products in `generated/numerics/` + manifest. 10 integer totals + 7 integer
  sequences; divisor scan 2..500 for divisibility / compression / residue structure; controls:
  **frequency null** (1000 realizations), **structure null** (invariance + random partitions),
  **mushaf-order test**, **Bonferroni + FDR + family-wise permutation**
- **RESULT — no unusual numerical structure beyond chance:**
  - well-posed family (scalar joint-divisibility, 499 tests): **0 survive Bonferroni, 0
    survive FDR**; strongest raw finding divisor 86 (p=0.0057) fails all corrections
  - **family-wise permutation p = 0.227** — random integers match the best pattern 22.7% of
    the time
  - structure null: real surah-size partition matched by 36% of random partitions;
    divisibility is **invariant** to ayah/surah/root shuffling (a property of counts, not
    arrangement)
  - frequency-preserving demo: the ~1800 naïve "Bonferroni survivors" are **artifacts** of a
    uniform-integer null applied to natural Zipfian frequencies (p 0.56–1.00 under the correct
    null) — the exact mechanism behind numerological claims, diagnosed and excluded
  - **19:** divides exactly **one** total — n_surahs=114 (114=6×19, the famous anchor) — but
    p=0.418 (expected 0.53), **rank #29/499**, and **survives no correction**. 114 is also
    divisible by 2,3,6,38,57; 19 is ordinary
- **The five final answers:** (1) unusual structure? **NO**; (2) strongest findings? coincidences
  (86 self-divisibility, 2=even) failing all controls; (3) 19 among top findings? **no**; (4)
  19's rank? **#29/499**; (5) survive multiple-testing? **none**
- Builder: `scripts/build_numerics.py`; Validator: `scripts/validate_numerics.py` (53 checks
  incl. number-blindness probes + byte-identical rebuild). Reports:
  `numerical-inventory-report.md`, `divisibility-report.md`, `compression-report.md`,
  `frequency-null-report.md`, `structure-null-report.md`, `revelation-order-report.md`,
  `significance-report.md`, `blindness-audit-report.md`, `phase-19x-final-report.md`

Numerical verdict (blind, corrected): **no significant numerical structure** in the Quran's
counts beyond chance and natural distribution. The famous 114=6×19 is real arithmetic but
statistically ordinary; treated blindly and corrected for multiple testing, 19 ranks #29/499
and survives no control. Proves nothing about any number's "correctness"; only measures.

---

## Phase Z — Quran Self-Method Discovery Engine (falsification study)

A deliberate **falsification re-test**, not a fresh question: Phases Q ("integrative
method") and X ("directed epistemic pipeline") answered "does the Quran describe its own
method?" affirmatively but **never applied frequency/length/order nulls**. Phase Z treats
those conclusions as **hypotheses** and subjects the directional method to the controls they
lacked. Rebuilt from the corpus only (**no Q/X outputs read**); no external source. Verdict
from pre-registered thresholds; negative/partial outcome is first-class.

- 8 data products in `generated/self_methodology/` + manifest. 16 epistemic nodes (the
  spec's vocabulary) → directed graph (within-ayah word order + cross-ayah adjacency) → 85
  candidate edges. Battery: **frequency** configuration null (K=100), **mushaf-order** null
  (word+ayah shuffle, K=100), **surah-length** median split, **bootstrap** (K=200),
  **subsampling** (10/20/40%), threshold sweep
- **VERDICT — `PARTIAL` (weak, bordering NO):**
  - raw graph **reproduces Q/X** (sources observe/read/listen/ask; deepest sink knowledge
    −79) — replication without importing Q/X
  - **but under controls it collapses:** only **10/85 edges (11.8%)** exist beyond the
    frequency null (**88% of the "method" associations are frequency artifacts**); the
    directional pipeline does **not** survive the order null; only **2 edges** pass the FULL
    battery — `ask→knowledge` and `observe→misguidance` — and they are **isolated** (backbone
    = 2 nodes, no chain, no cycle)
  - the one surviving *perception* edge is **observe→misguidance**, not observe→knowledge —
    anti-confirmatory for a clean method; echoes Phase X's bivalent perception
  - stability ≠ reality: 10 edges are bootstrap/subsample-stable, but 8 of them do not beat
    the frequency/order nulls
- **Comparison:** Q's integrative method is **not supported as a controlled structure**; X's
  directed pipeline's **directionality does not survive**; fully **consistent with Phase P**
  (the directional structure is both non-predictive and non-robust to nulls). The strong
  "internal methodology" reading of Q/X is, under controls, **not supported** — only a real
  vocabulary field + 2 isolated regularities remain
- Builder: `scripts/build_self_methodology.py`; Validator:
  `scripts/validate_self_methodology.py` (981 checks incl. verdict-logic + null-battery
  structure + byte-identical rebuild)
- **Immutability note:** falsification report written as
  `self-methodology-falsification-report.md` (Phase Q owns `methodology-falsification-report.md`).
  Reports: `methodology-discovery-report.md`, `methodology-chain-report.md`,
  `methodology-obstacle-report.md`, `methodology-outcome-report.md`,
  `methodology-cycle-report.md`, `methodology-stability-report.md`,
  `self-methodology-falsification-report.md`, `phase-z-final-report.md`

Self-method verdict (honest): the Quran has a real epistemic-vocabulary field and two
isolated directional regularities (`ask→knowledge`, `observe→misguidance`), but **a stable,
connected, directional method does NOT survive** frequency/order/length controls. The strong
Q/X "the Quran describes its own method" conclusion is **not supported** once the missing
controls are applied — converging with Phase P's NON_PREDICTIVE terminus.

---

## Phase P — Structural Predictivity / Held-Out Information Engine

The first **generalization** test in the project. Every prior phase was descriptive on
the full corpus; Phase P asks whether the discovered structure **predicts held-out
Quranic content beyond lexical frequency** — the test that separates a genuine discovery
from an elaborate redescription. Designed to optimize for truth, not for a positive
result: leakage-free, frequency-controlled, with all decision thresholds **pre-registered**
in code before running. Manifest split as agreed: `predictivity_manifest.json`
deterministic + byte-identical, `run_metadata.json` volatile provenance.

- 9 data products in `generated/predictivity/` + deterministic manifest + volatile
  run_metadata. Task: **masked-unit completion** under whole-ayah holdout — mask a unit
  (root primary; concept secondary), predict from the remaining context using
  training-only statistics
- Predictors: B0 frequency (smoothed unigram, context-blind) · B1 degree · S1 log-linear
  PPMI co-occurrence (== B0 when evidence 0; identical min-rank tie convention) · S2
  directional (ordered PPMI) · N frequency-preserving configuration null. Metrics: MRR,
  Hits@k, perplexity, info-gain (bits). 4 regimes (random/contiguous/forward/length-strat),
  3 mask fractions, K=30 null in **all** regimes
- **VERDICT — `NON_PREDICTIVE`** (pre-registered ¬C1 ⇒ NON_PREDICTIVE):
  - **Beats frequency? NO.** Root primary cell: MRR 0.087 < 0.099 (B0), Hits@10 0.182 <
    0.199, **info-gain −3.316 bits** [boot CI −3.391,−3.242]. Structure **loses to
    frequency in 0/7 regimes**; order (S2) worse; degree ≈ frequency
  - **Beats the frequency null? YES.** Real S1 MRR ≈ 0.087 vs null ≈ 0.018 in every
    regime — the co-occurrence is **real** (corroborates Phase-17 D1), just not useful
  - **So:** the structure sits *between* the null and frequency — **more than random
    co-occurrence, less than the unigram prior.** Real but not predictive
  - **Concept level (secondary):** S1 beats B0 on *ranking* (MRR 0.316→0.370) but is
    confounded by **membership circularity** (concepts are co-occurrence clusters) and an
    **untested clustering** (Phase-11 ARI 0.22; the 0.9999 stability cosine is
    near-tautological) — cannot reverse the verdict
- **Recommendation (pre-registered negative-outcome policy): HALT further semantic/content
  phases.** The surviving structure (D1) is real but carries no held-out predictive
  advantage over frequency; Phases Q/R/X and any successor read as **frequency-mediated
  descriptions**. The deflation arc 15→16→17→P has reached its evidential terminus. The
  only warranted continuations are *harder tests of the representation itself* (a
  syntactic/word-order null, or a genuinely different representation — phonological,
  higher-order — under this same predictive bar), not more content
- Builder: `scripts/build_predictivity.py`; Validator: `scripts/validate_predictivity.py`
  (173 fast checks incl. leakage/fairness/pre-registration probes + byte-identical rebuild)
- **Immutability notes:** spec's `robustness`/`falsification` deliverables written as
  `predictivity-robustness-report.md` / `predictivity-falsification-report.md` (Phases
  14/7 own the generic names). Reports: `prediction-task-report.md`,
  `holdout-design-report.md`, `root-predictivity-report.md`, `concept-predictivity-report.md`,
  `frequency-null-control-report.md`, `information-gain-report.md`,
  `predictivity-robustness-report.md`, `predictivity-falsification-report.md`,
  `phase-p-final-report.md`, plus `executive-summary.md`

Predictivity verdict (honest terminus): **the structure Monad discovered is real but not
predictive** — it beats a frequency-preserving null yet loses to lexical frequency on every
pre-registered metric in all 7 regimes. There is no positive predictive discovery to
strengthen; the project has reached its evidential limit under this representation.

---

## Phase 1 — Canonical Quran Database

Immutable, reproducible SQLite database from the read-only corpus.

- 114 surahs · 6,236 ayahs · 77,429 word tokens · 128,219 morphology tokens
- 1,642 roots · 4,831 lemmas
- Builder: `scripts/build_database.py`; Validator: `scripts/validate_database.py`
- Docs: `database-schema.md`, `data-inventory.md`, `import-report.md`,
  `source-priority.md`, `data-quality-report.md`

---

## Phase 2 — Quran Internal Lexicon Engine

Complete internal lexical layer: how words derive meaning from Quran-internal
usage. PPMI over ayah-level co-occurrence; composite distributional + chapter
similarity.

- 7 data products in `generated/lexicon/` (root/lemma profiles, context windows,
  co-occurrence graph, semantic neighbors, distribution profiles, summary)
- 1,642 root profiles · 4,831 lemma profiles · 77,429 context-window records ·
  6,473-node / 28,968-edge co-occurrence graph · top-20 semantic neighbors per
  entity
- Builder: `scripts/build_lexicon.py`; Validator: `scripts/validate_lexicon.py`
  (26 checks, byte-identical rebuild)
- Reports: `root-analysis-report.md`, `lemma-analysis-report.md`,
  `semantic-neighborhood-report.md`, `distribution-analysis-report.md`,
  `phase2-final-report.md`

---

## Phase 3 — Concept Discovery Engine

Discovery of emergent conceptual structures (clusters of co-behaving roots and
lemmas) from the Phase-2 lexicon. Concepts carry opaque ids; **no meaning,
name, translation, or interpretation is assigned.**

- 7 data products in `generated/concepts/` (candidates, memberships, graph,
  centers, statistics, relationships, manifest)
- **103 concept candidates** · 735/1,633 roots clustered · 2,264 lemmas attached
- Multi-membership: 159 roots, 536 lemmas in >1 concept
- Concept graph: 103 nodes / 329 edges / 42 meta-communities / 8 isolated
- Mean internal density 0.81 · cohesion 0.41 · separation 0.37 · stability 0.78
- Method: mutual-kNN + recursive k=4 clique percolation; degree / betweenness /
  eigenvector centrality; deterministic label-propagation communities
- Builder: `scripts/build_concepts.py`; Validator: `scripts/validate_concepts.py`
  (30 checks, byte-identical rebuild)
- Reports: `concept-discovery-report.md`, `concept-topology-report.md`,
  `concept-centrality-report.md`, `concept-cluster-report.md`,
  `phase3-final-report.md`

---

## Phase 4 — Proposition Discovery Engine

Discovery of emergent *relational* structures between Phase-3 concepts.
Propositions carry opaque relation types over opaque concept ids; **no meaning,
name, theology, or interpretation is assigned.**

- 7 data products in `generated/propositions/` (candidates, graph, dependency,
  implication, conditional, bridge, manifest)
- **6,832 candidate relations** across 9 relation types over 103 concepts
- ASSOCIATES_WITH 170 · CO_OCCURS 1,215 · DEPENDS_ON 184 · REQUIRES 100 ·
  PRECEDES / FOLLOWS 303 / 303 · PREDICTS 547 (windows 1/2/3) · MEDIATES 2,347
  · CONDITIONAL_EMERGES 1,663
- Proposition graph: 103 nodes / 1,474 directed edges / 14.0 % pairwise density
  / 3 isolated / 10 bridges (top-decile betweenness)
- Mean (in + out) degree 28.6 · max 185 · mean relation diversity 5.48 / 9 ·
  mean unweighted betweenness 40.92
- 4 depth-3 hierarchical chains · 28 potential causal pairs · 2,570 directed
  cycles of length ≤ 4 · 59 global / 65 localized relations
- Method: per-ayah concept-activation matrix → marginal / pair / triple counts;
  PMI / NPMI; conditional probability + lift; intra-ayah positional asymmetry;
  sequence-window conditional probability; triadic mediation; synergy triples;
  unweighted Brandes betweenness on the undirected projection
- Builder: `scripts/build_propositions.py`; Validator:
  `scripts/validate_propositions.py` (99 checks, byte-identical rebuild)
- Reports: `proposition-discovery-report.md`, `dependency-analysis-report.md`,
  `implication-analysis-report.md`, `proposition-topology-report.md`,
  `phase4-final-report.md`

Monad can now answer, without assigning meanings: which concepts are
structurally related, which appear dependent, which act as bridges, which
appear foundational, which appear derivative, and which structures are stable
across the Quran.

---

## Phase 5 — Dependency Compression Engine

Measures whether the Phase-4 proposition structure compresses into a smaller set
of foundational structures. **Not** an axiom / ontology / theology engine.
Concept ids and relation types stay opaque; no meaning, ontology, axiom, or
origin claim is produced. Reconstruction = full set membership (a relation is
recovered iff every participating concept is retained).

- 8 data products in `generated/compression/` (foundationality, reconstruction
  sets, dependency layers, irreducible structures, statistics, curve, hub
  removal, manifest)
- **Primary finding:** only *partially* compressible — 80% of structure needs
  **59 / 103 concepts** (ratio 0.573); 50% needs 39; 95% needs 76. Convex
  compression curve (knee at k ≈ 66 → 88%); greedy AUC 0.612
- **Single dominant core:** `CONCEPT_007` (composite 1.000 vs 0.402 next; 22.2%
  of relations incident; sole fragmenting node). 15 concepts each destroy ≥ 5%
  alone; 27 above mean necessity
- **Hub removal → reorganize, not collapse:** 77.8% of relations survive,
  `CONCEPT_016` + a size-9 SCC become the new core; all 4 hierarchical chains
  (hub-terminated) vanish; short cycles fall 2,570 → 219
- **8 dependency layers** (0–7, wide base / thin spire) · **7 irreducible
  dependency cores** (largest size 9, all hub-independent) · one 94-node
  directional SCC (ordering is globally cyclic)
- Method: set-coverage reconstruction; six-metric composite foundationality;
  greedy maximum-coverage; Tarjan SCC condensation + longest-path layering;
  Brandes betweenness (Phase-4-consistent) on the hub-removed induced subgraph
- Builder: `scripts/build_compression.py`; Validator:
  `scripts/validate_compression.py` (byte-identical rebuild, all checks pass)
- Reports: `foundationality-report.md`, `compression-analysis-report.md`,
  `hub-removal-report.md`, `dependency-layer-report.md`,
  `irreducibility-report.md`, `phase5-final-report.md`

---

## Phase 6 — Concept Identification Engine

Reveals *what Quran-internal evidence defines each discovered concept* — dominant
roots, dominant lemmas, activating ayahs, carrying surahs, and surrounding
structures. **Not** a meaning, ontology, or theology engine. Concept ids and
relation types stay opaque; **no meaning, name, translation, or interpretation is
assigned.** Activation reuses the Phase-4 membership-union rule exactly.

- 8 data products in `generated/identification/` (concept profiles, dominant
  roots, dominant lemmas, ayah signatures, surah signatures, concept atlas, core
  investigation, manifest)
- **All 103 concepts profiled.** Activation cross-checks Phase 4 exactly: 6,101
  active ayahs; `CONCEPT_081` activates 2,553 ayahs (= its Phase-4 `REQUIRES`
  support). Activation skew: min 3 · median 53 · **max 5,906** (`CONCEPT_007`,
  96.8% of active ayahs)
- **Dominant evidence (no meaning):** strongest single activation = ayah 2:282
  (`CONCEPT_007`); 2:282 and 47:15 each head 3 concepts; surah 2 carries the most
  activity (top for 35 concepts); uniqueness peaks in short surahs
  (`CONCEPT_102` lift 346 in surah 49); `CONCEPT_007` alone has no distinctive
  surah
- **Core investigation:** deep evidence dossiers for the dominant hub
  (`CONCEPT_007`, layer 0, requires-in only), the secondary core (`CONCEPT_016`,
  layer 7, depends-out, relation-diversity 7/9), the top-20 foundational
  concepts, and the size-9 irreducible core (`003 004 034 053 060 061 084 085
  088`, all layer 6)
- Method: Phase-4-consistent per-ayah activation + summed-membership-confidence
  strength; activation-weight ranking of members; neighbourhood/graph influence
  from Phase-2 semantic neighbours; incident-relation indexing; Phase-5
  SCC/layer reuse
- Builder: `scripts/build_identification.py`; Validator:
  `scripts/validate_identification.py` (18,839 checks, byte-identical rebuild)
- Reports: `concept-identification-report.md`, `core-investigation-report.md`,
  `ayah-signature-report.md`, `surah-signature-report.md`,
  `phase6-final-report.md`

Monad can now answer, without assigning meanings: what evidence defines each
concept, which Quranic regions activate it, which roots and lemmas dominate it,
and which structures depend on and surround it.

---

## Phase 7 — Semantic Revelation Engine

The first phase permitted to investigate concept *identity* — but identity is
revealed, never imported. A concept's identity and candidate "names" are
expressed **only** as the concept's own dominant **Arabic** roots/lemmas and the
ayah / structural patterns they form. **No translation, gloss, dictionary,
tafsir, theology, or interpretation is used; no certainty or origin is claimed;
competing identities are preserved.** The validator enforces the core invariant:
every candidate name is a literal Quran-internal member token.

- 9 data products in `generated/revelation/` (concept dossiers, semantic fields,
  ayah identity profiles, root consistency, candidate names, core revelation,
  identity confidence, falsification results, manifest)
- **Identity tiers across 103 concepts:** 43 strong · 51 moderate · 3 weak · **6
  resist** (the most lexically diffuse: `001`–`004`, `013`, `017`). Verdicts: 15
  coherent_single · 55 coherent_dominant · 33 diffuse_unified · 0 fragmented
- **Flagship answers (evidence only):** `CONCEPT_007` → anchor `ٱللَّه`/`اله`
  (present in 96% of its signature ayahs, broad diffuse field); `CONCEPT_016` →
  `جَنَّة`/`جنن`; `CONCEPT_081` → `ٱللَّه`/`اله` (strongest single identity, conf
  0.629)
- **Ambiguity preserved:** 42 concepts carry competing anchors; 4 anchors head
  >1 concept (`اله`→`007/081`, `رسل`→`061/085/088`, `كفي`, `قمص`). Most
  structurally central concepts are the hardest to name
- **Falsification:** each identity attacked; 97 tested, **94 survive, 3
  falsified** (`011` `نصح`, `041` `حدب`, `043` `رفد` — fail to explain ≥78% of
  their own signature ayahs)
- Method: root-anchored naming over Phase-6 activation; semantic fields by intra-
  concept co-occurrence + Phase-2 neighbours; POS-based actors/actions (Phase-1
  morphology); HHI/entropy coherence; evidence-graph dossiers; self-falsification
- Builder: `scripts/build_revelation.py`; Validator:
  `scripts/validate_revelation.py` (3,299 checks incl. no-imported-meaning
  invariant, byte-identical rebuild)
- Reports: `semantic-revelation-report.md`, `concept-identity-report.md`,
  `core-revelation-report.md`, `identity-confidence-report.md`,
  `falsification-report.md`, `phase7-final-report.md`

Monad can now answer, using Quran-internal evidence only and without claiming
certainty: what each concept is most likely anchored on, which identities are
strongly supported, which remain ambiguous, which concepts resist identification,
and what competing explanations coexist.

---

## Phase 8 — Foundational Principle Discovery Engine

Tests — never assumes — whether the discovered structure reduces to a small set of
**foundational principles** (structural patterns, not words/roots/lemmas/concepts).
Principles emerge from the structure, carry opaque ids, and are never named,
translated, or interpreted. **No theology, doctrine, ontology, apologetics, or
origin claim; success is not claimed before testing; no small set is forced.**

- 9 data products in `generated/principles/` (candidates, coverage, removal,
  reconstruction, hierarchy, dependencies, irreducible, falsification, manifest)
- **Principle = maximal cohesive module** of the integrated concept graph
  (Phase-3 overlap ⊕ Phase-4 propositions) via deterministic greedy modularity →
  **16 principles** (modularity 0.294)
- **Primary finding — hypothesis tested, NOT supported:** only **9.9% of the
  6,832 relations are internal to a single principle; 90.1% are inter-principle.**
  No principle generates > 3.7%; the internal (generating) coverage ceiling is
  **9.9%** at any set size. A small set *governs* most structure (4→80%, 8→95%)
  only because large modules hold the most-connected concepts
- **No dominant principle** (top governs 36.8%, generates 3.7%). **One irreducible
  size-11 cyclic principle cluster**; the principle layer is globally cyclic
  (shallow 4-layer hierarchy, 14/16 recursive). The Phase-5 size-9 concept SCC is
  split across 5 principles — modules and dependency cycles are orthogonal
- **Falsification: 0 of 16 principles survive** as self-contained patterns
  (internal retention 0.000–0.100; every module leaks ≥ 90%)
- Method: integrated-graph modularity (CNM); incidence vs internal coverage;
  greedy minimum sets; principle-level dependency lift + Tarjan SCC + longest-path
  layering; self-containment falsification
- Builder: `scripts/build_principles.py`; Validator:
  `scripts/validate_principles.py` (189 checks incl. partition + emerge-not-invent
  invariants, byte-identical rebuild)
- Reports: `principle-discovery-report.md`, `principle-coverage-report.md`,
  `principle-hierarchy-report.md`, `principle-falsification-report.md`,
  `irreducible-principles-report.md`, `phase8-final-report.md`

Verdict (structural, no meaning): the discovered Quranic structure does **not**
reduce to a small set of self-contained foundational principles — it is a dense,
globally interwoven relational web at the principle level too, confirming Phase 5
one level up.

---

## Phase 9 — Structural Motif Discovery Engine

Tests the Phase-8 follow-up hypothesis: that the structure is organised around
recurring **structural motifs** (recurring directed subgraph patterns) rather than
foundational principles. Motifs carry opaque ids and a neutral graph-theoretic
descriptor; **none is named, translated, or interpreted. No theology, doctrine,
ontology, apologetics, intention, authorship, or origin claim; no significance
without evidence.**

- 9 data products in `generated/motifs/` (catalog, statistics, coverage,
  compression, replacement, survival, scc_analysis, falsification, manifest)
- **Motif = isomorphism class of small connected directed subgraph** over the
  Phase-4 proposition graph → the 17,345 connected triads fall into exactly the
  **13 canonical directed triad classes** + 2 dyad classes = **15 motifs**
- **Primary finding — hypothesis SUPPORTED (with caveat):** recurring motifs
  exist and are highly explanatory. **3 motifs cover 50% of triads, 5 cover 80%,
  8 cover 95%** — a tiny structural vocabulary, vs Phase 8's 9.9% principle
  ceiling. Top motifs touch 88–96% of concepts
- **Significance vs degree-preserving null:** reciprocity & convergence
  over-represented (fully-mutual triangle z=+29, mutual-path +10, out-fork +9,
  in-merge +6); long directed chains under-represented. Directed 3-cycles nearly
  absent (3 instances)
- **Robustness:** 10/13 triad motifs survive hub removal (72% of triads retained,
  0 collapse); all 13 classes persist inside the 94-node directional SCC and the
  61-concept principle SCC; **10/15 motifs survive falsification** (vs 0/16
  principles). Caveat: the single most-common motif (mutual-path) is hub-bound
  (74% via CONCEPT_007)
- Method: canonical triad/dyad census; fixed-seed degree-preserving null z-scores;
  edge-subsampling stability; greedy motif compression; hub-removal & SCC-restricted
  censuses; multi-criterion falsification
- Builder: `scripts/build_motifs.py`; Validator: `scripts/validate_motifs.py`
  (299 checks incl. structural-only invariant, byte-identical rebuild)
- Reports: `motif-discovery-report.md`, `motif-coverage-report.md`,
  `motif-compression-report.md`, `motif-survival-report.md`,
  `motif-falsification-report.md`, `phase9-final-report.md`

Verdict (structural, no meaning): the Quranic network is **structurally repetitive
but not reducible** — built from ~5 recurring local relational patterns woven into
one irreducible global web. Motifs explain relational *form* far better than
principles explained relational *substance*, but they are a descriptive vocabulary,
not a generative foundation.

---

## Phase 10 — Contradiction & Consistency Discovery Engine

Tests — never assumes — whether the discovered structure contains internal
contradictions. **High burden of proof; false positives unacceptable.** Ambiguity,
complexity, overlap, multiple identities, and cycles are explicitly **not**
contradictions. No theology, tafsir, translation, external logic, or imported
philosophy; the threshold is never lowered; consistency is never claimed without
testing.

- 9 data products in `generated/consistency/` (model, proposition/dependency/
  identity/motif conflicts, recursive consistency, scores, contradiction
  candidates, manifest)
- **Formal model:** all Phase-4 relations are monotone functions of one per-ayah
  activation matrix M (reconstructed, 6,101 active ayahs = Phase 4/6). Obligation
  classes — NECESSITY (`REQUIRES`≥0.9), STRICT ORDER (`PRECEDES`≥0.95), EXCLUSION
  (co=0, marg≥30), TENDENCY (rest) — with 6 explicit contradiction rules C1–C6.
  Only NECESSITY/STRICT can contradict; TENDENCIES cannot
- **Primary finding — hypothesis tested, structure is CONSISTENT:** **51
  contradiction candidates surfaced, 0 survive falsification, 51 falsified.**
  Global consistency index **0.955**. The structure appears internally coherent
- **Evidence:** 0 necessity conflicts (no concept REQUIRES two mutually-exclusive
  targets); all 100 `REQUIRES` matrix-verified; `REQUIRES` graph acyclic; **401
  EXCLUSION pairs disjoint from every positive relation**; 0 strict-order cycles
  (9 `PRECEDES` cycles all weak, min asymmetry 0.30–0.50); 0 identity inversions
  (3 instability candidates falsified); **all 18 mutual dependencies + 7
  dependency SCCs self-supporting, 0 self-negating**
- Falsified candidates: 39 dependency-tendency (`DEPENDS_ON`≠necessity), 9 weak
  order-cycles, 3 identity-instability — each rejected on explicit structural
  grounds. Least stable: `CONCEPT_011/041/043` (Phase-7 unstable identities, not
  contradictions)
- Builder: `scripts/build_consistency.py`; Validator:
  `scripts/validate_consistency.py` (585 checks incl. high-burden invariant,
  byte-identical rebuild)
- Reports: `consistency-model-report.md`, `proposition-conflict-report.md`,
  `dependency-conflict-report.md`, `identity-conflict-report.md`,
  `motif-conflict-report.md`, `recursive-consistency-report.md`,
  `phase10-final-report.md`

Verdict (structural, no meaning): the discovered Quranic structure is **internally
consistent** — no genuine proposition, dependency, identity, motif, or recursive
contradiction survives a high-burden falsification test; its cycles are
self-supporting and its negative (exclusion) layer is disjoint from its positive
obligations.

---

## Phase 11 — Discovery Stability & Robustness Engine (validation)

The first **validation** phase: discovers nothing, instead attempts to *destroy*
prior discoveries by methodological perturbation and reports only what survives.
Burden of proof reversed; failures documented, not hidden; prior conclusions not
protected. No new concepts/principles/motifs/identities/theories; no
reinterpretation; no cherry-picking.

- 10 data products in `generated/validation/` (threshold sweeps, bootstrap,
  subsampling, noise, hub/motif/consistency validation, reproducibility audit,
  survivor analysis, manifest)
- Method: resample the activation matrix M (1,000 bootstraps; 500 subsamples at
  5–40% removal); re-derive concepts by 5 clustering families (ARI/NMI);
  noise-inject the proposition graph; sweep all thresholds; rebuild 7 engines to
  temp + hash. All fixed-seed deterministic; full stats (mean/median/std/95% CI)
- **Survivor tally: 4 SURVIVES STRONGLY · 2 MODERATELY · 2 WEAKLY · 0 FAILS**
  - **STRONG (use freely):** CONCEPT_007 dominance (rank-1 in 1,500/1,500
    resamples, share CI [0.963,0.972]); Phase-10 consistency (0 contradictions
    under every regime, exclusion/positive overlap 0 at all thresholds); Phase-9
    motif vocabulary (13/13 classes + 5-for-80% invariant under noise); Phase-5
    compression (byte-identical, threshold-robust verdict)
  - **MODERATE:** size-9 SCC (large core persists under noise); Phase-7 identity
    anchors (top-10 concept Jaccard 0.92)
  - **WEAK (method-relative):** the exact 103-concept partition (NMI 0.74 but ARI
    0.22; counts 38–471 across methods) and the exact 16-principle decomposition —
    structure exists, precise boundaries do not
- **Reproducibility:** 7/7 `--out`-capable engines rebuild byte-identically;
  pipeline deterministic; effectively seed-free
- **Documented methodological risks:** concept/principle *counts* are method
  artifacts; hub-leaning findings (dominant motif `MOTIF_001`) inherit the hub and
  are fragile; all results conditional on the inherited Phase-4 relation population
- Builder: `scripts/build_validation.py`; Validator:
  `scripts/validate_validation.py` (112 checks incl. statistical-completeness +
  no-protection invariants, byte-identical rebuild)
- Reports: `validation-overview-report.md`, `threshold-sweep-report.md`,
  `bootstrap-report.md`, `subsampling-report.md`, `hub-validation-report.md`,
  `motif-validation-report.md`, `consistency-validation-report.md`,
  `reproducibility-report.md`, `survivor-analysis-report.md`,
  `phase11-final-report.md`

Validation verdict: the headline discoveries (hub dominance, consistency,
compression verdict, motif vocabulary) are **robust corpus properties**; the exact
concept/principle counts are **method-relative** and must be cited as structure,
not as fixed facts.

---

## Phase 12 — Generative Grammar Discovery Engine

Tests whether the observed proposition network can be *generated* by a small set
of structural production rules (measured transformations, not concepts/motifs).
Rules carry opaque ids; none named. **No meaning, theology, translation, or tafsir;
no external graph theory cited as explanation; generation claimed only where
simulation confirms it.**

- 8 data products in `generated/grammar/` (rule candidates, statistics,
  generation, simulation, ablation, falsification, robustness, manifest)
- **3 production rules discovered, parameters measured from the graph (N=100,
  M=1059):** RULE_001 degree-proportional attachment (γ=1.0); RULE_002 reciprocity
  (frac 0.38, target 0.612); RULE_003 transitive closure (frac 0.15, target 0.250)
- **Primary finding — generation is PARTIAL and LOCAL:** from an empty graph the
  rules regenerate the **13-class motif vocabulary at triad cosine 0.905** [0.887,
  0.922] (all 13 classes), reciprocity (ratio 0.97), transitivity (1.04), and the
  giant-SCC size (ratio 0.97). But they do **NOT** generate the extreme hub (ratio
  **0.39** — super-linear attachment never closes the gap → hub is an irreducible
  primitive) or Phase-10 consistency (a property of the activation matrix, not
  topology — out of scope)
- **Minimum set:** {attachment + reciprocity} = 2 rules reach ~100% of achievable
  cosine; transitive closure near-redundant. **Ablation:** RULE_002 (reciprocity)
  essential (cosine drop 0.357), RULE_001 0.027, RULE_003 0.005 — the local
  structure is dominated by one reciprocity process. **More compressive than the
  motif description** for local structure
- **Falsification:** 1 claim SURVIVES (motif vocabulary), 2 FALSIFIED (hub,
  consistency), 1 PARTIAL (SCC). **Robustness:** rule parameters stable under
  10–20% edge removal
- Builder: `scripts/build_grammar.py`; Validator: `scripts/validate_grammar.py`
  (70 checks incl. simulation-confirms-generation invariant, byte-identical rebuild)
- Reports: `rule-discovery-report.md`, `rule-generation-report.md`,
  `rule-simulation-report.md`, `rule-ablation-report.md`,
  `rule-falsification-report.md`, `phase12-final-report.md`

Grammar verdict: the network's **local form** is the output of a simple robust
generative process (degree-biased reciprocal edge formation, ~90% reproduced); its
**global hub** and its **consistency** are irreducible primitives no local rule
generates.

---

## Phase 13 — Revelation Evolution Engine

Analyses the structure as *evolving*: verses introduced in a documented order,
leakage-free snapshots, emergence of hub/motifs/consistency/SCC/identity measured
over "revelation time." **No external chronology exists in the corpus, so two
corpus-internal orderings are used, documented + SHA-256 hashed, analysed
separately** (canonical mushaf order; Meccan→Medinan period proxy) plus a control
shuffle. **No theology, tafsir, translation, origin/historical inference; no
future verses in earlier snapshots.**

- 9 data products in `generated/evolution/` (snapshot statistics, hub/motif/
  consistency/scc/identity evolution, predictability, phase transitions, manifest)
- Method: snapshots at 1–100% of revealed ayahs; per snapshot rebuild a
  leakage-free graph (co-occurrence + positional `PRECEDES` over revealed ayahs
  only) and recompute every structure
- **Primary finding — the structure does NOT emerge gradually; it is present
  almost in full from the first verses, under every order:** at **1% revealed** the
  hub is already rank-1 (share **1.000**, it *dilutes* to 0.968 by 100%), the motif
  vocabulary is complete (12/12 classes), consistency holds (0 overlap), 82% of
  final top concepts present. **Composite predictability ≥0.80 from 1%, 0.93 at
  10%**
- **Timelines:** hub present-from-start (no competing hub ever); motifs stabilize
  by **5%**; consistency 0-overlap at all 36 snapshots×orders; SCC born at 1%
  (size 40 ≥ Phase-5 core), grows gradually to 91 by ~70%; identity the only
  gradual structure (0.30→0.59, proxy)
- **Robustness/falsification:** all four headline findings hold across both
  traditions AND the random control → order-independent (content-driven). The
  naive "emergence over revelation time" hypothesis is itself **falsified** — the
  structure is scale-invariant, so apparent emergence is sampling, not development.
  Chronology limitation explicitly acknowledged (orderings are accumulation orders,
  not history)
- Builder: `scripts/build_evolution.py`; Validator:
  `scripts/validate_evolution.py` (136 checks incl. no-leakage + separate-hashed-
  traditions invariants, byte-identical rebuild)
- Reports: `revelation-evolution-report.md`, `hub-evolution-report.md`,
  `motif-evolution-report.md`, `consistency-evolution-report.md`,
  `predictability-report.md`, `phase-transition-report.md`,
  `phase13-final-report.md`

Evolution verdict (structural, not historical): the robust core (hub, consistency,
motif vocabulary) is **scale-invariant and content-intrinsic** — present in any
sufficiently large sample under any order; only SCC size and identity grow
gradually.

---

## Phase 14 — Structural Locality & Distribution Engine

Investigates *where* the structure lives and *how evenly* it is distributed.
Regions are defined only by measurable structural behaviour — **never by surah
name, topic, chronology, meaning, or human label.** No theology, tafsir,
translation, chronology, or origin claim; no conclusion without measurement.

- 12 data products in `generated/locality/` (density maps, fingerprints, region
  candidates, similarity, specialization, ablation, redundancy, inequality,
  locality, falsification, robustness, manifest)
- Method: per-surah/window structural densities; fingerprints (concept-activation
  profiles); region discovery by modularity on discriminative (TF-IDF) fingerprint
  similarity; specialization, ablation, redundancy, inequality, local-vs-global
  window recovery, falsification, robustness
- **Primary finding — the corpus is ONE homogeneous structural field:** raw
  fingerprint similarity is near-uniform (mean cosine **0.835**); no structurally
  distinct regions emerge (discriminative clustering yields only ~54 *weak*
  clusters, cohesion ~0.28, mostly grouping short surahs — a size gradient)
- **Distribution:** moderately concentrated by volume (Gini **0.58**; 15% of
  surahs carry 50%) but **even per-ayah density (Gini 0.275)** — concentration is a
  length effect. Effective number of regions ≈ 43.6/114
- **Redundancy/ablation:** consistency is in 114/114 surahs, hub support in
  104/114 — both ubiquitous; **no single region is indispensable** (0 of 54
  ablations break the hub or consistency). Motif generation is rare (21/114,
  concentrated in large surahs)
- **Locality gradient:** hub & consistency **fully local** (recovered in 100% of
  all random windows ≥1%); motif vocabulary **mostly local** (full by 20%); the
  **giant SCC is global** (recovery 0.41 at 10%, 0.84 at 50%)
- **Falsification:** "uniform" FALSIFIED, "tiny-minority" PARTIALLY FALSIFIED,
  "specialized regions" WEAKLY SUPPORTED, "interchangeable regions" SUPPORTED,
  "local windows reproduce global" SUPPORTED at scale. All survive bootstrap +
  threshold sweeps
- Builder: `scripts/build_locality.py`; Validator: `scripts/validate_locality.py`
  (347 checks incl. regions-from-structure-only invariant, byte-identical rebuild)
- Reports: `structural-density-report.md`, `region-discovery-report.md`,
  `specialization-report.md`, `ablation-report.md`, `redundancy-report.md`,
  `locality-report.md`, `locality-falsification-report.md`, `robustness-report.md`,
  `phase14-final-report.md` (the spec's generic `falsification-report.md` collided
  with Phase 7's, so the Phase-14 one was named distinctly to keep Phase 7 immutable)

Locality verdict: the network is a **scale-invariant, content-intrinsic,
spatially homogeneous** structure — the hub and consistency live in essentially
every verse, the motif vocabulary is local, only the giant SCC is global, and no
region is indispensable; the only spatial variation is a length-driven density
gradient.

---

## Phase 15 — Consistency Propagation Engine

Investigates *how* consistency is maintained — with an explicit mandate to
**destroy** it. Consistency is not assumed, not protected, not assumed special or
meaningful. No theology, tafsir, translation, external logic, or imported
explanation.

- 11 data products in `generated/consistency_propagation/` (support, hub
  dependence, core, pathways, motif/SCC/redundancy contribution, counterfactual
  destruction, generative, hypothesis falsification, manifest)
- Method: recompute consistency as a contradiction count over the activation
  matrix M; map support; challenge the hub; search for a core/pathways; ablate
  motifs/SCCs; test redundancy; run counterfactual destruction (structural removal
  + null model + data corruption); generative test; falsify H1–H7
- **Primary finding — NO structure maintains consistency; it is IRREDUCIBLE (only
  H7 survives):** every consistency-support weight is **0** (removing any
  concept/SCC/motif/region creates 0 contradictions); survives full hub removal;
  **no consistency core** (every subset down to 10% is consistent); **30 null-model
  shuffles are equally consistent** (CI [0,0] → generic, not special); broken
  **only** by direct data corruption (linear curve 5%→20 … 100%→401)
- **The hub mediates but does not maintain:** 96% of REQUIRES (necessity) edges
  target the hub (which co-occurs with everything → necessity never conflicts), but
  consistency survives hub removal → H1 falsified (mediator, not maintainer)
- **Deflationary conclusion (honest, unprotected):** consistency is partly
  **tautological** (a pair cannot have co=0 and co≥5) and partly **generic**
  (hub-dominated sparse co-occurrence); it is a property of the activation matrix's
  internal coherence, not a maintained structural achievement; the Phase-12 grammar
  cannot generate it (topology-only)
- **Hypotheses:** H1 hub FALSIFIED · H2 core FALSIFIED · H3 SCCs FALSIFIED · H4
  motifs FALSIFIED · H5 redundancy FALSIFIED · H6 emergent FALSIFIED · **H7
  irreducible SURVIVES**
- Builder: `scripts/build_consistency_propagation.py`; Validator:
  `scripts/validate_consistency_propagation.py` (81 checks incl. destruction-
  attempted + only-H7-survives invariants, byte-identical rebuild)
- Reports: `consistency-support-report.md`, `hub-dependence-report.md`,
  `consistency-core-report.md`, `consistency-pathways-report.md`,
  `motif-contribution-report.md`, `recursive-stability-report.md`,
  `consistency-redundancy-report.md`, `counterfactual-destruction-report.md`,
  `generative-consistency-report.md`, `hypothesis-falsification-report.md`,
  `phase15-final-report.md` (the spec's generic `redundancy-report.md` collided
  with Phase 14's, so the Phase-15 one was named distinctly to keep Phase 14
  immutable)

Consistency verdict (deflationary, unprotected): consistency is **irreducible** —
not maintained by any removable structure, generic to the data type, partly
tautological; the hub mediates necessity but is not required; destroyable only by
corrupting the data itself.

---

## Phase 16 — Hub Origin Discovery Engine

Investigates the **structural origin** of CONCEPT_007's dominance — not its meaning.
The hub is not protected; it must earn survival. No theology, tafsir, translation,
meaning, semantic interpretation, or origin claim.

- 10 data products in `generated/hub_origin/` (decomposition, reconstruction,
  necessity, uniqueness, simulation, predictability, redundancy, falsification,
  robustness, manifest)
- Method: decompose hub dominance across axes; correlate with frequency; reconstruct
  from lexical frequency; test Zipf necessity; simulate (frequency vs uniform vs
  topology); measure uniqueness/predictability; falsify H1–H6; bootstrap
- **Primary finding — the hub is FREQUENCY-DRIVEN, not an irreducible primitive:**
  it is rank-1 on every axis (activation, degree, REQUIRES-in, lexical frequency),
  but these are *one cause expressed many ways* — frequency predicts degree
  (**Spearman 0.966**), and frequency is predicted by lexical frequency (**Spearman
  0.998**). Every other dominance axis (motif, SCC, connectivity) is a mechanical
  consequence
- **Reconstructible & generable:** the lexical-frequency rank-1 concept is exactly
  CONCEPT_007 (its member root has 2851 corpus tokens, the most of any). A
  frequency-weighted simulation reproduces the hub (**~0.88** share) while uniform
  frequencies do not (**0.21**) and the Phase-12 topology grammar cannot (**0.034**)
  — locating the origin Phase 12 couldn't: **lexical frequency, not topology**
- **Necessary** (Zipfian lexical tail required: uniform → no hub), **unique** (0.968
  vs next 0.418, gap 0.55), **inevitable** (rank-1 from 1% of ayahs), **robust**
  (top concept in 100% of 200 bootstraps)
- **Hypotheses:** H1 frequency SURVIVES · H2 motif FALSIFIED · H3 grammar FALSIFIED
  · H4 SCC FALSIFIED · H5 activation SURVIVES (=H1) · **H6 irreducible FALSIFIED**
  (reduces to lexical frequency; irreducible only relative to topology)
- Builder: `scripts/build_hub_origin.py`; Validator: `scripts/validate_hub_origin.py`
  (75 checks incl. hub-earns-survival invariant, byte-identical rebuild)
- Reports: `hub-decomposition-report.md`, `hub-reconstruction-report.md`,
  `hub-necessity-report.md`, `hub-uniqueness-report.md`, `hub-simulation-report.md`,
  `hub-predictability-report.md`, `hub-falsification-report.md`,
  `hub-robustness-report.md`, `phase16-final-report.md`

Hub-origin verdict (deflationary): the hub is the concept that aggregates the
corpus's most frequent lexical items; its dominance, connectivity, necessity- and
consistency-mediation, motif and SCC participation are all *consequences* of that
one lexical fact. It is **not** an irreducible structural primitive — it reduces to
the Zipfian lexical frequency distribution (irreducible only relative to topology).

---

## Phase 17 — Frequency Null Model Engine

Asks the deepest validation question: **how much of Monad is genuine structure vs a
consequence of lexical frequency?** Frequency is the strongest known confounder.
No discovery is protected; any may fail or survive — both reported. No theology,
tafsir, translation, meaning, or apologetics.

- 13 data products in `generated/frequency_null/` (null corpora, concept/
  proposition/motif/consistency/identity/scc/grammar survival, information
  decomposition, survivor analysis, falsification, robustness, manifest)
- Method: two frequency-preserving configuration nulls — concept-level (1,000
  realizations) and root-level (200) — preserve root/lemma/concept frequencies +
  ayah sizes, destroy co-occurrence/proposition/motif structure. Recompute every
  discovery; compare by z-score, ratio, structure-fraction
- **Primary finding — Monad is ~35% structure, ~65% frequency:**
  - **GENUINE STRUCTURE (survives, 3–4× null):** proposition edges (**74.7%
    structure, 3.9×**), strongly-connected core (**72.2%, 3.6×**), strong
    associations (**68.7%, z=+19.7, 3.2×**); concept clustering significant
    (**z=+29.8**, moderate magnitude). **Strongest surviving discovery: the
    proposition/co-occurrence network**
  - **FREQUENCY ONLY (0% structure, null reproduces exactly):** consistency
    (every null equally consistent — confirms Phase 15), hub dominance (Phase 16),
    grammar reciprocity
  - **MOSTLY FREQUENCY:** identity anchors (69% = most-frequent member root),
    motif distribution (3/13 classes survive), grammar transitivity
- **Hypotheses:** H1 concept SURVIVES · H2 proposition SURVIVES · H3 motif SURVIVES
  · H4 consistency FALSIFIED · H5 identity FALSIFIED (mostly) · H6 grammar MIXED ·
  **H7 irreducible structure SURVIVES**. Robust under bootstrap
- Builder: `scripts/build_frequency_null.py`; Validator:
  `scripts/validate_frequency_null.py` (126 checks incl. no-protection invariant,
  byte-identical rebuild)
- Reports: `frequency-null-model-report.md`, `concept-survival-report.md`,
  `proposition-survival-report.md`, `motif-frequency-survival-report.md`,
  `consistency-survival-report.md`, `identity-survival-report.md`,
  `scc-survival-report.md`, `grammar-survival-report.md`,
  `information-decomposition-report.md`, `frequency-survivor-analysis-report.md`,
  `phase17-final-report.md` (two generic spec names collided with Phase 9/11, so
  the Phase-17 motif-survival and survivor-analysis reports were renamed to keep
  those phases immutable)

Frequency-null verdict (honest): Monad is part frequency, part structure. The hub,
consistency, identity anchors, and generative grammar are largely/wholly frequency
artifacts; but the **proposition/co-occurrence network and the strongly-connected
core are genuine structure (3–4× the frequency null)** — Monad's real contribution
is the discovery of a specific relational web beyond word frequency.

---

## Phase Ω — World Model Discovery Engine (capstone)

Asks whether a coherent **world-model** can be reconstructed from the Quran itself —
only from the Quran, with **no theology, tafsir, philosophy, ontology, science, or
imported categories.** The model must emerge or fail to emerge; it is not forced.
No religion is proved or disproved; no divinity or humanity assumed.

- 14 data products in `generated/world_model/` (entity/state/transformation/causal/
  feedback/agency/knowledge/society/history models, world model, compression,
  falsification, robustness, manifest)
- Method: classify concepts by the dominant Phase-1 morphology POS of their member
  roots (entity=nominal, state=adjectival, transformation=verbal — a corpus
  annotation, not an imported category); build a transition graph from Phase-4
  PRECEDES + PREDICTS; feedback from its cycles; keep concepts opaque
- **Primary finding — a STRUCTURAL world-model emerges; a SEMANTIC one does not:**
  - **Structural (emerges):** a self-referential **state-transition system** — **83
    entity-class** (nominal) concepts, **20 transformation-class** (verbal), **0
    state-class** (states do not separate grammatically), a **720-edge** transition
    graph (dominant pattern ENTITY→ENTITY), a **42-concept feedback core**. This is
    the relational structure that survived frequency control in Phase 17
  - **Semantic (does NOT emerge):** what the entities/transformations MEAN — the
    model of existence, agency, knowledge, society, history — cannot be
    reconstructed structurally without the interpretation the project forbids
- **Falsification:** 4 structural components survive (entity, transformation,
  precedence-candidate, feedback); 5 semantic components fail to emerge (state,
  knowledge, society, history, the semantic world-model). Gaps reported, not
  concealed. **Robustness:** entity/transformation split bootstrap-stable; absent
  state class robust (0 in every resample)
- **Compression:** simple component-*types* but a large irreducible *instance*
  (inherits Phase-5 incompressibility)
- Builder: `scripts/build_world_model.py`; Validator:
  `scripts/validate_world_model.py` (87 checks incl. model-emerges-or-fails +
  opacity invariants, byte-identical rebuild)
- Reports: `entity-model-report.md`, `state-model-report.md`,
  `transformation-report.md`, `causal-structure-report.md`, `feedback-report.md`,
  `agency-report.md`, `knowledge-report.md`, `society-report.md`,
  `history-report.md`, `world-model-report.md`,
  `world-model-falsification-report.md`, `phase-omega-final-report.md`

World-model verdict (honest, bounded): Monad maps the **shape** of the Quran's
conceptual world with precision — a coherent structural state-transition system —
but it cannot and does not read its **meaning**. The model emerges as structure, not
as meaning; the semantic non-emergence is the appropriate terminus of a purely
structural analysis.

---

## Phase Σ — Internal Semantic Reconstruction Engine

Tests whether the Quran can define its **own** meanings internally. Meaning is
allowed; **external** meaning is forbidden — no dictionary, tafsir, translation,
lexicon, embedding, or imported label. Distributional meaning applied
Quran-internally: a concept is defined only by its relations to **other opaque
concepts**; anchors are evidence, never glossed.

- 13 data products in `generated/semantics/` (recoverability, definitions,
  boundaries, contrasts, functional roles, equations, primitives, consistency,
  anchors, internal dictionary, falsification, robustness, manifest)
- Method: reconstruct co-occurrence; classify recoverability (Phase-7 anchor +
  Phase-6 neighbourhood + contrasts); build Quran→Quran definitions; measure
  contrasts (exclusions), functional roles, cross-corpus drift, definitional
  centrality vs frequency
- **Primary finding — a RELATIONAL semantic layer EMERGES; a REFERENTIAL one does
  NOT:**
  - **77 of 103 concepts relationally RECOVERABLE**; **89 defined Quran→Quran** (no
    external word); **401 internal contrasts** (opposites that never co-occur);
    **80/89 meaning-stable across corpus halves** (mean cosine 0.81)
  - **Decisive positive result — semantic anchors are NOT the frequency hub:**
    definitional centrality is its own structure. Low-frequency `CONCEPT_027`
    (`ربو`, marginal 52) defines 12 concepts (residual **+11.2**), while the
    frequency hub `CONCEPT_007` has residual **−81.4** (not a semantic anchor). The
    semantic layer is genuine, not a frequency artifact — recovering ground that
    Phases 16–17 appeared to remove
  - **Referential meaning FAILS TO EMERGE:** the internal dictionary is
    self-contained but referentially circular (concept→concepts only) — it never
    grounds anything externally (the Phase-Ω limit)
- **Falsification:** 3 relational claims SURVIVE (recoverable, consistent,
  non-frequency anchoring); referential FAILS TO EMERGE. Robust under bootstrap
- Builder: `scripts/build_semantics.py`; Validator: `scripts/validate_semantics.py`
  (344 checks incl. no-external-meaning invariant, byte-identical rebuild)
- Reports: `semantic-recoverability-report.md`, `definition-discovery-report.md`,
  `semantic-boundary-report.md`, `contrast-report.md`, `functional-meaning-report.md`,
  `semantic-equations-report.md`, `semantic-primitives-report.md`,
  `semantic-consistency-report.md`, `semantic-anchor-report.md`,
  `internal-dictionary-report.md`, `semantic-falsification-report.md`,
  `phase-sigma-final-report.md`

Semantic verdict (genuine, bounded): the Quran **does** define its concepts in terms
of one another — a recoverable, stable, self-contained internal semantic network
whose anchors are **not** the frequency hubs (genuine structure beyond frequency).
But it is **relational** meaning (position), not **referential** meaning (reference).
Meaning emerges from the Quran alone — as relation, not as reference. That is the
precise limit of internal semantic reconstruction.

---

## Phase X — Epistemology Discovery Engine

Asks not what structures exist in the Quran but **what process of knowing the Quran tries
to create in a human being** — how it moves a person from not-knowing to knowing. Nothing
assumed central (not observation, reason, or faith); everything discovered, measured,
attacked. Only the corpus — no tafsir, hadith, dictionary, translation, philosophy,
theology, or epistemology/psychology/cognitive-science literature. **New signal: ORDER**
— within-ayah word position + cross-ayah adjacency give a *directed* graph of knowing.

- 10 data products in `generated/epistemology/` (epistemic actions, knowledge pathways,
  ignorance pathways, enablers, obstacles, epistemic sequence, compression,
  falsification, robustness, manifest)
- Method: 24 epistemic nodes (8 actions, 8 states, 8 obstacles); directed flow =
  within-ayah precedence + cross-ayah adjacency; net-outflow ranking (source→sink);
  enabler/obstacle flow into understanding vs blindness; modes of knowing; gap-based
  stage compression; reverse-sequence falsification (margin 0.60); Meccan/Medinan
  robustness split
- **Primary finding — a robust DIRECTED PIPELINE of knowing:**
  - every epistemic **action is a source**, every **state a sink**; **knowledge (علم) is
    the deep attractor** (net −111); **certainty (يقين) the terminus** (knowledge→certainty
    0.80, strongest edge in the corpus)
  - **reflection is LATE, not early** (net −18, beside understanding) — the bridge from
    perception to understanding; never imperative
  - **perception is BIVALENT** — observation tops *both* enablers AND obstacles (→
    understanding 0.54, → blindness 0.60); the same look precedes seeing and not-seeing
  - **the obstacle to knowing is MORAL, not perceptual** — the purely-obstructive nodes
    are lying (0.71), denial, sealing-of-the-heart (0.67); ignorance is a self-feeding
    cascade denial/conjecture→lying→arrogance→deviation→forgetting
  - **real state-gradient:** information → understanding → knowledge → certainty/wisdom
  - **4 genuine modes of knowing** (observation, signs, comparison, history); **2 fail
    honestly** — self (0.50 non-directional) and consequences (0.45 reversed)
- **Falsification + robustness:** only **46 of 89 edges survive** reverse-sequence attack
  (margin 0.60) — the weak half is dominated by non-directional observation;
  independently, **77% of edges keep direction across Meccan/Medinan**. Both attacks
  discard the *same* observation edges — raw perception is non-directional by two measures
- **Compression:** 78% inter-stage forward consistency, but a *gradient* into one extreme
  attractor, not tidy equal stages (reported as-is, not forced)
- Builder: `scripts/build_epistemology.py`; Validator: `scripts/validate_epistemology.py`
  (464 checks, byte-identical rebuild)
- **Immutability note:** falsification deliverable written as
  `epistemology-falsification-report.md` (Phase 7 owns `falsification-report.md`)
- Reports: `epistemic-actions-report.md`, `knowledge-pathway-report.md`,
  `ignorance-pathway-report.md`, `enablers-report.md`, `obstacles-report.md`,
  `epistemic-sequence-report.md`, `epistemic-compression-report.md`,
  `epistemology-falsification-report.md`, `epistemic-robustness-report.md`,
  `phase-x-final-report.md`

Epistemology verdict: if a human had only the Quran, they would be taught to know through
a directed pipeline — **perceive → reflect → understand → know → become certain** — fed by
four modes (observation, signs, comparison, history). But perception alone is bivalent and
non-directional; the real gate is moral — knowledge fails exactly when lying/denial/
arrogance/the-sealed-heart intervene. The directional core is robust across both
revelation halves; half the naïve graph is order-less co-occurrence, honestly discarded.

---

## Phase R — Text → Reality Discovery Engine

The first phase to reverse direction: from *what the Quran is* to **which patterns in
reality the Quran invites observation of, and whether they survive testing**. Not a
proof, defence, or refutation — only a test, reported whichever way it falls. No
external source: no other scripture, tafsir, kalām school, or world-history/empirical
dataset. **Honest boundary (enforced throughout):** with no external data permitted, the
engine cannot verify a pattern against the world — it tests only the Quran's *internal*
claim-structure (cross-domain breadth + survival of Quran-internal counter-examples).
"Holds in reality" = the Quran asserts it consistently, NOT that it is measured in
history.

- 10 data products in `generated/reality/` (reality targets, observable claims, reality
  patterns, candidate laws, cross-domain patterns, falsification, reality mapping, law
  compression, method consistency, manifest)
- Method: extract observable phenomena across 10 domains; isolate observable claims
  (exclude unseen/hereafter); measure antecedent→outcome co-occurrence **lift** within
  ±1 ayah; mark CANDIDATE_LAW (lift>1, ≥3 domains, ≥5 support); falsify with
  Quran-internal counter-examples (antecedent + OPPOSITE outcome); compress; check vs
  Phase Q
- **Primary finding — a small, asymmetric, internally-bounded set of سنن emerges:**
  - **3,402 observable claims** (88% of domain-ayahs); 10 domains; 353 آيات-ayahs
  - all 15 conduct→outcome patterns show **positive lift**; 13 strong (3.2×–7.1×);
    strongest is deed→recompense (عمل→جزاء, 7.13×)
  - **9 of 13 candidate laws SURVIVE internal falsification; 4 REFUTED** — incl. the
    intuitive **injustice→collapse** and three positive laws (faith/guidance/
    righteous-deed→thriving), defeated by the Quran's **antithetical style** (each
    antecedent flanked by both outcomes within a window)
  - **collapse direction far cleaner than flourishing** (6/8 negative laws survive; only
    2/5 positive) — the internally clearest law is *corruption→ruin*; runs against an
    apologetic reading, reported as-is
  - survivors compress **9 → 3 fundamental سنن**: corruption→downfall (6 antecedents),
    constructive-conduct→flourishing (thin, 2), deed→recompense (general)
- **Consistency with Phase Q: PARTIAL (45% domain overlap).** Laws anchored in Phase Q's
  nature/history/self fields (and سنّة الله named explicitly, 15 ayahs) — not fabricated —
  but spread into ethics/power/economy beyond Q's core; compatible, not coextensive
- Builder: `scripts/build_reality.py`; Validator: `scripts/validate_reality.py` (105
  checks, byte-identical rebuild)
- **Immutability note:** spec's `docs/falsification-report.md` collides with Phase 7;
  Phase R's is written as `reality-falsification-report.md` (no prior file touched)
- Reports: `reality-targets-report.md`, `observable-claims-report.md`,
  `reality-pattern-report.md`, `cross-domain-report.md`, `candidate-laws-report.md`,
  `reality-falsification-report.md`, `reality-mapping-report.md`,
  `law-compression-report.md`, `method-consistency-report.md`, `phase-r-final-report.md`

Reality verdict (bounded): if a person read only the Quran and looked at the world, the
Quran would expect them to see one regularity above all — **conduct determines outcome,
and corruption ends in collapse** — with gratitude/patience→increase and deed→recompense
alongside. A stable set of سنن emerges (3, cross-domain, falsification-surviving), but it
is small, asymmetric (downfall robust, flourishing thin), and provable only as the
Quran's *internal assertion*, not as external fact.

---

## Phase Q — Quranic Methodology Discovery Engine

Shifts the question from *what the Quran is* to **how the Quran says it should be
understood**. No method is imported from outside — not philosophical, theological,
mystical, academic, traditional, modern, or even Monad's own. Only the method the
Quran states *about itself*, measured descriptively from the corpus (root frequencies,
imperative moods, ayah-level co-occurrence). Nothing is proved or defended; concepts
stay opaque; Arabic roots are evidence, never glossed.

- 11 data products in `generated/quranic_methodology/` (method vocabulary,
  imperatives, evidence model, reasoning patterns, repetition, story function, nature
  function, self-descriptions, methodology model, falsification, manifest)
- Method: locate the corpus's own method-vocabulary roots (cognition, observation,
  evidence/signs, inquiry, self-description, nature, story); count imperative (IMPV)
  and imperfect (IMPF) moods from `features_raw`; measure ayah-level co-occurrence of
  آيات (signs) with each evidence category; test six competing hypotheses
- **Primary finding — the Quran DOES state an internal, INTEGRATIVE methodology:**
  - **6,173 method-vocabulary tokens; 208 imperatives** commanding method-actions
    (ذكر 56, نظر 48, علم 31, سؤال 16, سمع 13 …) — understanding is *commanded*
  - The signs (آيات, 353 ayahs) are grounded in a **plurality** of evidence: reason
    (94), nature (77), text (44), the human self (38), history (18) — no single source
  - Recurring inference: **sign → cognition** (the "for a people who reason/reflect/
    know" refrain — 334 imperfect tokens for علم, 71 for ذكر, 48 for عقل)
  - Nature is cast **as sign** (25.5% of 1,141 nature-ayahs carry signs/cognition;
    night 0.49, sky 0.37, earth 0.33); story is cast **as lesson** (عبرة, مثل); the
    text describes itself **functionally** (clarification 64, guidance 34, reminder 33)
- **Falsification:** H1 (no method), H2 (faith only), H3 (reason only), H4 (text
  only), H5 (nature only) **all FALSIFIED**; **H6 (integrative method) SURVIVES**
- **Honest limits:** descriptive co-occurrence only — states a method, does not judge
  its validity; the contemplative roots (تدبّر 8, تفکّر 17 verbal calls) are *rare*,
  the method's weight falls on knowing/remembering/looking/asking; nature-as-sign
  concentrates in cosmological roots, not all of nature
- Builder: `scripts/build_quranic_methodology.py`; Validator:
  `scripts/validate_quranic_methodology.py` (133 checks, byte-identical rebuild)
- Reports: `method-vocabulary-report.md`, `imperative-method-report.md`,
  `evidence-model-report.md`, `reasoning-pattern-report.md`,
  `method-repetition-report.md`, `story-function-report.md`,
  `nature-function-report.md`, `quran-self-description-report.md`,
  `methodology-falsification-report.md`, `phase-q-final-report.md`

Methodology verdict: a reader with **only** the Quran — importing nothing — would be
told *how to read it*: observe the signs (in text, nature, history, and the self), and
reason / reflect / remember. The method is **integrative**, not single-source. This is
the Quran's own stated method, recovered from the Quran alone.

---

## Invariants held across all phases

- The Quran is the only semantic universe; no external knowledge is imported.
- Source datasets, the database schema, and prior-phase outputs are never
  modified or rebuilt by a later phase.
- Every engine is deterministic, reproducible, and byte-identically rebuildable,
  with a dedicated validator.
- No ontology, contradiction engine, axioms, theology, interpretation, doctrine,
  or origin claims have been produced. Work remains at the lexical /
  statistical / structural layer. Relation types stay opaque throughout. From
  Phase 7, a concept's *identity* may be revealed — but only as its own dominant
  Quran-internal Arabic roots/lemmas and ayah/structure patterns; never as a
  translation, gloss, meaning, or origin claim, and never with claimed certainty.

---

## Reproduce the full stack

```bash
python3 scripts/build_database.py     && python3 scripts/validate_database.py
python3 scripts/build_lexicon.py      && python3 scripts/validate_lexicon.py     --rebuild
python3 scripts/build_concepts.py     && python3 scripts/validate_concepts.py    --rebuild
python3 scripts/build_propositions.py && python3 scripts/validate_propositions.py --rebuild
python3 scripts/build_compression.py  && python3 scripts/validate_compression.py  --rebuild
python3 scripts/build_identification.py && python3 scripts/validate_identification.py --rebuild
python3 scripts/build_revelation.py     && python3 scripts/validate_revelation.py     --rebuild
python3 scripts/build_principles.py     && python3 scripts/validate_principles.py     --rebuild
python3 scripts/build_motifs.py         && python3 scripts/validate_motifs.py         --rebuild
python3 scripts/build_consistency.py    && python3 scripts/validate_consistency.py    --rebuild
python3 scripts/build_validation.py     && python3 scripts/validate_validation.py     --rebuild
python3 scripts/build_grammar.py        && python3 scripts/validate_grammar.py        --rebuild
python3 scripts/build_evolution.py      && python3 scripts/validate_evolution.py      --rebuild
python3 scripts/build_locality.py       && python3 scripts/validate_locality.py       --rebuild
python3 scripts/build_consistency_propagation.py && python3 scripts/validate_consistency_propagation.py --rebuild
python3 scripts/build_hub_origin.py     && python3 scripts/validate_hub_origin.py     --rebuild
python3 scripts/build_frequency_null.py && python3 scripts/validate_frequency_null.py --rebuild
python3 scripts/build_world_model.py    && python3 scripts/validate_world_model.py    --rebuild
python3 scripts/build_semantics.py      && python3 scripts/validate_semantics.py      --rebuild
python3 scripts/build_quranic_methodology.py && python3 scripts/validate_quranic_methodology.py --rebuild
python3 scripts/build_reality.py        && python3 scripts/validate_reality.py        --rebuild
python3 scripts/build_epistemology.py   && python3 scripts/validate_epistemology.py   --rebuild
python3 scripts/build_predictivity.py   && python3 scripts/validate_predictivity.py   --rebuild
python3 scripts/build_self_methodology.py && python3 scripts/validate_self_methodology.py --rebuild
python3 scripts/build_numerics.py        && python3 scripts/validate_numerics.py        --rebuild
python3 scripts/build_explanation_boundary.py && python3 scripts/validate_explanation_boundary.py --rebuild
python3 scripts/build_residual_nature.py && python3 scripts/validate_residual_nature.py --rebuild
python3 scripts/build_counterfactual.py && python3 scripts/validate_counterfactual.py --rebuild
python3 scripts/build_decision_architecture.py && python3 scripts/validate_decision_architecture.py --rebuild
python3 scripts/build_foundation_audit.py && python3 scripts/validate_foundation_audit.py --rebuild
```

---

## Next

No further phase is started by design. **Phase P (the predictivity test) returned
`NON_PREDICTIVE` and recommends halting further semantic/content phases**: the surviving
structure is real but carries no held-out predictive advantage over lexical frequency, so
the project has reached its evidential terminus under the co-occurrence representation. The
only scientifically-warranted continuations are harder tests of the representation itself —
a syntactic/word-order-preserving null, or a genuinely different representation
(phonological, higher-order) under Phase P's predictive bar — not additional content
phases. See `phase-p-final-report.md` (Q5) and `executive-summary.md`. Awaiting explicit
instruction.
