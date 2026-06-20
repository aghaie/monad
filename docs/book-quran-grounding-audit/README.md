# Quran-Grounding Audit of *نظریهٔ آزادی، ایران و دین* (Jannatkhah)

**Claim under test.** The book asserts that its *اصول موضوعه* (postulates/axioms) are
written **based on Quran reference** (بر اساس رفرنس قرآن). This audit tests that claim
against the actual Quran, using only this repo's internal, leakage-controlled corpus and
self-interpreting network — no human tafsir, no external translation as input.

**Subject.** 817-page Persian edition (`azadi din iran _ Jannatkhah.pdf`).
**Cross-reference.** The author's own formal/logical reconstruction lives at
`github.com/aghaie/Theory-of-Liberty-Religion-Iran`; the relevant axiom tables are vendored
into `generated/book-quran-audit/source_from_repo/`. That repo audited *logical soundness*;
**this audit tests the distinct, previously-untested claim of Quranic grounding.**

---

## Phases & findings

| phase | question | verdict |
|-------|----------|---------|
| **Q0** | extract every Quran reference | 61 references, 25 surahs, 42 with `surah:ayah`; all surah names resolved |
| **Q1** | do the citations exist & quote faithfully? | **42/42 real verses, 0 fabrication, 0 misattribution**; faithful Arabic or Persian-translation quotes |
| **Q2** | do the *postulates* rest on the Quran? | **No at the foundation, yes at the religious layer.** All 3 underived axioms are secular-rational; 67% of theory derivable with no theology; the 7 theological axioms are derived & verse-anchored |
| **Q3** | are verses read in context or proof-texted? | **In context.** Cited-verse set 4.17× more coherent than chance (p=0.0003); co-citations 8–12×; 33× network adjacency |

See `Q0-Q1-citation-fidelity.md`, `Q2-grounding-coverage.md`, `Q3-contextual-fidelity.md`.

### Part II — the CFS claim (phases F1–F5)

The author further claims the book **is a consistent formal axiomatic system (CFS) because
the Quran is one and the book references the Quran**. Tested in `F1-F5-CFS-claim-audit.md`:

| leg | verdict |
|-----|---------|
| Quran is **consistent** | ✅ SUPPORTED (index 0.95, 0 surviving contradictions / 6832 relations) |
| Quran is **axiomatic** | 🟡 PARTIAL — proto-axiomatic (90% irreducible residue; needs 57% of concepts for 80%) |
| Quran is **formal** | ❌ NO — 31/100, no language/inference/calculus, no arithmetic encoding |
| book **inherits** CFS by reference | ❌ NOT SUPPORTED — invalid inference; book's load-bearing axioms (free will, consistency, property) are exogenous to the Quran's kernel (secular axioms 0/6 on a Quran hub) |

**Bottom line:** the Quran is a *consistent, proto-formal, axiom-structured* system; the
book faithfully mirrors that same type (also proto-formal, also consistent) and genuinely
anchors its theological axioms (5/7) on the Quran's hubs — but *"formal"* over-states it for
both, and CFS-ness is not inherited by citation.

## Overall verdict

The book's claim is **substantially honest, with one precise correction**:

1. **Citation integrity — clean.** Every verse the book cites is real, correctly numbered,
   and faithfully reproduced. No fabricated or out-of-range references; no detectable
   misattributions. This already places it above the norm for religious-political polemic.

2. **The Quran is used in genuine context.** By three independent structural measures the
   book groups and selects verses the way the Quran's *own* rare-root fabric groups them —
   it does not abuse scripture by arbitrary proof-texting.

3. **But "postulates based on Quran" is, strictly, inverted.** The book's load-bearing,
   *underived* axioms are **rational/formal** — free will and two meta-logical requirements
   (finite-minimal axioms, internal consistency). Two-thirds of the theory follows from
   these alone. The Quran is the book's source for the **content of true religion** (Tawhid,
   no-compulsion 2:256, equality 49:13, resurrection, prophethood), which the book presents
   as **derived** from the rational kernel, not assumed from scripture.

**Most accurate restatement of what the book actually does:**
> *Rationally axiomatized, Quran-confirmed — not Quran-axiomatized.* Where it speaks of
> religion it reads the Quran directly, faithfully, and in context (rejecting mysticism,
> tradition, and clergy); but its first principles are reason, not revelation.

So the claim holds in its **defensible/weak reading** (the religious content is genuinely
and faithfully sourced from the Quran) and is **misleading only if read strongly** (that the
axioms themselves are *derived from* the Quran — the book's own architecture derives the
*necessity* of religion from secular axioms).

### What this audit deliberately does NOT claim

It does not judge whether the book's specific inferences (e.g. *liberty = individual
property rights*, *true Islam = the unique consistent formal system for liberty*) are the
**uniquely correct** reading of the Quran. No internal method can settle that, and per
Charter Article F the audit abstains there. The audit answers only the testable question —
*are the references real, faithful, and contextual?* — and the answer is **yes**.

## Reproduce

```bash
pdftotext -enc UTF-8 -layout "azadi din iran _ Jannatkhah.pdf" \
    generated/book-quran-audit/raw/book_fa.txt
python3 scripts/book_audit_q0_extract.py     # Q0  references
python3 scripts/book_audit_q1_fidelity.py    # Q1  citation fidelity
python3 scripts/book_audit_q2_grounding.py   # Q2  grounding coverage
python3 scripts/book_audit_q3_context.py     # Q3  contextual fidelity
```
Ground truth: `corpus/quran/source/qurantexttanzil.csv` (6236 verses),
`corpus/quran/morphology/quranic-corpus-morphology-0.4.txt`,
`generated/layers/L6_network/ayah_network.json`.
