# Book Quran-Grounding Audit — Phase Q2 (Grounding Coverage)

**Question.** The book claims its *اصول موضوعه* (postulates) are written "based on Quran
reference." Q1 showed the citations are real and faithful. Q2 asks the harder thing:
do the *postulates* actually **rest on** the Quran, or are the postulates rational/formal
with the Quran entering downstream as confirmation?

**Inputs.** The author's own formal reconstruction (15 named axioms, dependencies, tiers,
and an axiom-subset coverage BFS), vendored from
`github.com/aghaie/Theory-of-Liberty-Religion-Iran` into
`generated/book-quran-audit/source_from_repo/`, cross-linked with this audit's Q0/Q1
citation set. Script: `scripts/book_audit_q2_grounding.py`.

---

## Q2.1 — Which axioms are genuinely foundational (underived)?

Only **three** axioms have no dependencies (`depends_on == []`):

| id | axiom | grounding |
|----|-------|-----------|
| A-000001 | Human free will exists and is universally presupposed | secular-rational |
| A-000011 | A valid formal system must have finite & minimal axioms | secular-rational (meta-logic) |
| A-000012 | A valid system must be internally consistent (Gödel) | secular-rational (meta-logic) |

**All three underived foundations are secular-rational. None is Quran-derived.**
This matches the book's *own* self-statement: free will is "اصلی که همه … ناگزیر آن را
پیش‌فرض می‌گیرند" and "گام‌به‌گام به آزادی، حقوق مالکیت فردی، **دین** … رسیده‌ام" — i.e.
religion is reached *by derivation from* free will, not assumed from scripture.

## Q2.2 — Grounding type of all 15 named axioms

| grounding | count | axioms |
|-----------|-------|--------|
| secular-rational | 6 | A-1, A-2, A-11, A-12, A-13, A-14 |
| bridge | 2 | A-3 (liberty needs divine grounding), A-8 (taslīṭ) |
| theological-Quranic | 7 | A-4 Tawhid, A-5 no-compulsion, A-6 Resurrection, A-7 Prophethood, A-9 equality, A-10 accountability, A-15 Mahdism |

Every one of the 7 theological axioms is a **derived proposition** (tier ≥ 1), and each
chains back to the secular kernel through A-4 Tawhid → A-1 free will.

## Q2.3 — Load test: how much rests on the secular kernel alone?

Using the author's own breadth-first coverage over the validated backbone:

| coverage | axiom set | note |
|----------|-----------|------|
| **67.3 %** | {free will, finite-axioms, consistency} | secular only, **no theology** |
| 67.3 % | + Tawhid | Tawhid adds **0 %** reachable nodes |
| 89.8 % | all 15 | theology lifts 67 % → 90 % |

**Two-thirds of the theory is derivable with no theological axiom.** The Quranic axioms
are load-bearing only for the final third (the last-round / false-messiah / terminal-
condition arguments — Resurrection, Prophethood, Mahdism).

## Q2.4 — Do the theological axioms have real verse anchors?

**7/7** theological axioms are tied to specific verse(s); **2** carry a verifiably and
faithfully quoted proof-text from Q1: **A-5 = 2:256** («لا إكراه في الدين») and
**A-9 = 49:13** (equality/«إن أكرمكم عند الله أتقاكم»). The rest rest on Quranic *themes*
(Tawhid, resurrection, khatam al-nubuwwa) rather than a single decisive verse.

---

## Verdict (Q2)

The claim "*the postulates are based on Quran reference*" is **structurally inverted at the
foundation and true at the religious layer**:

- **Foundation (load-bearing axioms): NOT Quran-based.** The underived axioms are free
  will + two meta-logical requirements. The book derives the *necessity* of religion
  rationally; it does not postulate religion from scripture.
- **Religious content: genuinely Quran-anchored.** Where the book specifies *what* true
  religion says (no compulsion, Tawhid, equality, resurrection, prophethood), it ties each
  to real, faithfully-quoted Quran references — not to mysticism, tradition, or clergy,
  which it explicitly rejects.

Most accurate one-line characterization: **the book is rationally axiomatized and
Quran-confirmed, not Quran-axiomatized.** Its honest claim is the weaker, defensible one
(religious content read from the Quran directly); the strong reading (postulates *derived
from* the Quran) is not supported by the book's own architecture.

Open question for Q3: where the book *does* attach a verse to a claim, is the verse read in
context, or proof-texted? Tested next via this repo's self-interpreting relational network.
