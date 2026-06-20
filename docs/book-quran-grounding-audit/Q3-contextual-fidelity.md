# Book Quran-Grounding Audit — Phase Q3 (Contextual Fidelity)

**Question.** Where the book attaches a verse to a claim, does it read the verse in its
Quranic context, or proof-text — yoking together verses that are unrelated in the source?

**Method (no human tafsir).** A faithful, in-context use of scripture groups verses the way
the source's *own* structure groups them; arbitrary proof-texting groups unrelated verses.
We measure "relatedness in the source" two independent ways, both internal to this repo:
- **ground-truth roots per verse** (Quranic Arabic Corpus morphology), with each shared
  root weighted by its rarity (idf), and
- the repo's validated **L6 rare-root relational network** (`ayah_network.json`).

Script: `scripts/book_audit_q3_context.py`. Seed fixed; reproducible.

---

## Test 3 — Verse-selection coherence (highest-powered)

Are the **34 distinct verses** the book cites more lexically coherent *among themselves*
than a random 34 verses drawn from the Quran?

| | mean pairwise shared-rare-root weight |
|---|---|
| book's 34 cited verses | **3.44** |
| random 34-verse sets (3000 draws) | 0.83 |
| **ratio** | **4.17×**  (p = 0.0003) |

**The book's verse selection is not scattered cherry-picking.** Its citations concentrate
on a genuinely interrelated region of the Quran — the *covenant / community / revelation /
servitude / property* semantic field — far above chance.

## Test 1 — Within-argument co-citation (window sweep)

Verses the book co-cites inside the **same argument** (citations within W chars), scored vs
random Quran pairs:

| window | co-cited pairs | obs weight | ratio vs random Quran pair |
|--------|----------------|-----------|----------------------------|
| 2 500  | 3  | 10.17 | **12.1×** |
| 6 000  | 7  | 8.02  | 9.5× |
| 12 000 | 11 | 7.03  | 8.3× |

(p = 0.0005 at the tightest window vs whole-Quran baseline; 2.95× and p = 0.02 even against
the harder baseline of random pairs drawn from the book's *own* cited set.) The ratio decays
smoothly as the window widens — exactly the signature of real argument-local grouping.

## Test 2 — Direct network adjacency

| | fraction of pairs where one verse is the other's L6 rare-root neighbour |
|---|---|
| book co-cited pairs | **33 %** |
| random cited-verse pairs | 1 % |

A 33× enrichment: a third of co-cited pairs are *direct* neighbours in the validated network.

## Concrete examples (shared rare roots)

| co-cited pair | shared rare roots | shared theme |
|---|---|---|
| 2:213 ~ 5:48 | wḥd, ʾmm, ḫlf, nbʾ, ḥkm, nzl | one community → prophets → revealed scripture to judge differences |
| 2:213 ~ 3:19 | bġy, ḫlf, byn, ktb | religion/division-after-knowledge |
| 5:48 ~ 7:157 | ʾmm, nbʾ, tbʿ, nzl, ktb | following the sent prophet & the Book |

These are not arbitrary pairings; the verses share the Quran's own load-bearing vocabulary.

---

## Verdict (Q3)

At the structural/lexical level, **the book reads verses in context, not as arbitrary
proof-texts.** Its verse *selection* (4.17×, p = 0.0003) and its *argument-local groupings*
(8–12×; 33× network adjacency) track the Quran's own rare-root relational fabric far above
chance, by three independent measures.

### Boundary of this finding (stated honestly)

This test establishes that the cited verses are **genuinely related and on-topic** for the
book's themes. It does **not** — and no internal method can — establish that the book's
specific liberty-theoretic *inferences* (e.g. "2:256 ⇒ individual property rights",
"true Islam = the unique consistent formal system for liberty") are the uniquely correct
reading rather than one defensible reading. Per this project's standard (Charter Art. F; the
L8 result that the network yields stable *relational* meaning but not unique theological
conclusions), the audit abstains on that last question. The book passes the test that *can*
be run: it does not abuse the Quran's structure.
