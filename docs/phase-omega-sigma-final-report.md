# Phase ΩΣ — Final Report: Foundational Question Discovery Engine

**Method version:** `foundational-questions-1.0` · **Date:** 2026-06-09. Deterministic, pure-stdlib,
byte-identical (`validate_foundational_questions.py --rebuild`). Corpus-only; no theology, tafsir,
translation, tradition, interpretation, or external data. **UNKNOWN is a first-class answer.** Arabic root
anchors are evidence, never glossed.

## 1. Objective
Previous phases asked *"what structures exist in the Quran?"*. This phase asks *"what are the deepest
questions the Quran itself appears to be answering?"* — by turning fourteen foundational questions into
measurable structural hypotheses and answering them only from the corpus, reporting UNKNOWN wherever the
evidence is insufficient or the question requires meaning the method forbids.

## 2. Method (summary)
Each question is operationalized on the Phase-1 DB: person frame (`features_raw`), verb aspect, POS classes,
co-occurrence graph, proper-noun removal, interrogative/negation association, and ring-symmetry geometry.
Quantitative directional claims are attacked with the project's nulls (configuration null, within-surah
order-shuffle null, frequency baseline) and a subsample stability check; the structural invariants are
re-verified at root/lemma/word. The pre-registered stance: well-posed structural questions get numbers;
semantic or externally-dependent ones get UNKNOWN.

## 3. Results (headline)
| | result |
|---|---|
| questions with measurable structural answers | **7 / 14** (Q3, Q7, Q8, Q9, Q11, Q12, Q13/Q14-structural) |
| questions UNKNOWN or reduced to the frequency core | **7 / 14** (Q1, Q2, Q5, Q6-content, Q10, Q13/Q14-semantic) |
| genuine null tests | Q9 **survives** · Q12 **falsified** (z = −1.46) |
| representation agreement (root/lemma/word) | **3 / 3** invariants |
| honest verdict | **PARTIAL SUCCESS** |

---

## The fourteen answers

**Q1 — What does the Quran minimize?** **UNKNOWN as a semantic principle.** The only defensible structural
reading is **lexical description length** (Zipfian compression); negation targets hardship-shaped roots
(حرج، ضيع …) — evidence only.

**Q2 — What does the Quran maximize?** **UNKNOWN as a semantic principle.** Structurally it maximizes
**redundancy / repetition of its central anchors** (Gini ≈ 0.80) — the mirror of Q1.

**Q3 — Human model or world model?** **BOTH.** A 3rd-person world (59.5% of person-marked tokens) delivered
in a 2nd/1st-person human **address** frame (40.5%). Neither reduces to the other.

**Q4 — Minimal generative core?** The **high-frequency hub** (اله، قول، كون، ربب، علم …). It maximizes
coverage but leaves ~80% of specific content irreducible (root 0.796 / lemma 0.751 / word 0.724).

**Q5 — Hidden reality (observable/inferable/hidden)?** **UNKNOWN.** Requires world knowledge; only the
3rd-person reference frame is structural.

**Q6 — Omission architecture?** **PARTIAL.** Anaphora is structurally present (PRON-to-N ≈ 0.13) — silence is
real, but its content is UNKNOWN.

**Q7 — Object vs relation priority?** **RELATIONS.** More token mass (51.3% vs 48.7%) *and* a strongly
edge-dense graph (45 edges/node). Objects organize neither surface nor structure.

**Q8 — Book or engine?** **ENGINE-leaning.** Process aspect 52.7%, plus 1,876 imperatives and 1,049
conditionals — a command/conditional register, not a static repository.

**Q9 — How much survives name removal?** **~95%.** Proper nouns are 5.0% of tokens; removing them leaves
frequency skew, the ~80% residual, and coherence-beyond-null unchanged. Structure is **name-independent**.

**Q10 — Revelation order vs canonical order?** **UNKNOWN — chronology is external and forbidden.** Only the
intrinsic meccan/medinan partition is available, and it shows near-identical residual (0.807 vs 0.821).

**Q11 — How is time modelled?** **ASPECTUAL / RECURRENT**, not linear-chronological: balanced
completed (47.3%) vs ongoing (43.0%) aspect, heavy imperative load, pervasive recurrence (573 roots in ≥10
ayahs).

**Q12 — Does a geometric architecture exist?** **NO** (beyond chance). Mirror-symmetric ayah pairs are not
more similar than order-shuffled pairs (z = −1.46). The only "geometry" is distributional self-similarity
(scale-invariance), a frequency property.

**Q13 — What survives longest under deletion (essentiality)?** The **frequency hub** — essentiality ≡
frequency dominance; no separate structural skeleton.

**Q14 — The Quran's own central question?** **UNKNOWN as semantics.** Structurally = maximal discourse
allocation on the central hub; interrogatives concentrate on *how/whence/know/observe* roots (كيف، اني، دلل …
— evidence only).

**Unified picture (synthesis).** Stripped of imposed meaning, the Quran is a **strongly frequency-skewed
lexical field** (Gini ≈ 0.80, ~80% irreducible residual) delivered in a **2nd/1st-person address** frame
about a 3rd-person world, in an **engine register** (imperatives + conditionals + process aspect), with
**aspectual/recurrent** rather than linear time, and a **name-independent, relation-dense** structure. Every
"deep" question that is answerable converges on the same information-theoretic core; the rest are UNKNOWN
because they need semantics or external chronology the method forbids.

---

## 4. Interpretation
Phase ΩΣ inverts the project's usual direction — instead of hunting new structure, it asks the Quran the
fourteen biggest questions and lets the corpus answer or refuse. The result is sober and consistent with the
whole arc: **half the questions are genuinely answerable and half are not.** The answerable half delivers a
coherent structural portrait (address-frame, engine register, aspectual time, relation-density,
name-independence). The unanswerable half (minimize/maximize as principles, hidden reality, omission content,
chronology, the "central question" as meaning) is honestly returned as UNKNOWN — and the apparently profound
ones (Q1, Q2, Q13, Q14) collapse onto the single frequency hub that survived Phase Ξ. The corpus answers what
is structural and refuses what is semantic.

## 5. Falsification Attempts
Only two answers carry genuine nulls: Q9 (name-removal) **survives** its configuration null; Q12 (geometry)
is **actively falsified** (z = −1.46). Census facts (Q3, Q7, Q8, Q11) are exact and flagged as
non-inferential. Semantic claims were not allowed to stand: Q1/Q2/Q13/Q14 reduce to frequency or UNKNOWN.
Nothing was protected.

## 6. Limitations
- Several headline questions are unanswerable by construction (semantics: Q1, Q2, Q5, Q6-content, Q14;
  external chronology: Q10) — reported as UNKNOWN rather than forced.
- Operationalizations (POS partitions, aspect-as-time, ring-as-lexical-symmetry) are defensible but not
  unique; the strong results (name-independence, no-geometry, frequency convergence) are robust to the choice.
- Non-lexical representations (phonological/syntactic) are untested.

## 7. Conclusion
**PARTIAL SUCCESS (pre-registered acceptable outcome).** Seven of fourteen foundational questions receive
measurable, representation-independent structural answers; seven are UNKNOWN or reduce to the frequency core.
The Quran, measured structurally, is a frequency-dominated, human-addressed, engine-register, aspectual,
name-independent, relation-dense lexical field — and the deepest-sounding questions about it converge on that
same information-theoretic core. The corpus answered what could be measured and, honestly, refused the rest.

---

### Outputs
`generated/foundational_questions/`: 8 data products + `foundational_manifest.json`. Tooling:
`scripts/build_foundational_questions.py`, `scripts/validate_foundational_questions.py`. Reports:
`q1-…` through `q14-central-question-report.md`, `question-integration-report.md`,
`omega-sigma-falsification-report.md`, `omega-sigma-stability-report.md`,
`omega-sigma-representation-report.md`, this report, and `omega-sigma-executive-summary.md`.

*Note on naming:* the spec's `falsification-report.md` and `executive-summary.md` already exist (prior
phases, immutable), so this phase's copies are `omega-sigma-falsification-report.md` and
`omega-sigma-executive-summary.md`.

### Reproduce
```bash
python3 scripts/build_foundational_questions.py
python3 scripts/validate_foundational_questions.py --rebuild
```

**Phase ΩΣ complete. No further phase started automatically.**
