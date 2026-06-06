# Core Revelation Report — Phase 7

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase7-revelation-1.0`.

Deep Quran-internal identity investigation of the structures Phase 5 found
central: `CONCEPT_007`, `CONCEPT_016`, `CONCEPT_081`, the size-9 dependency SCC,
and the top-20 foundational concepts. Every identity hypothesis is a dominant
**Arabic** anchor drawn from the concept's own members; competing hypotheses are
preserved; confidence is a concentration statistic; ambiguity is entropy. **No
meaning, certainty, divine origin, or human origin is claimed.**

---

## 1. `CONCEPT_007` — the dominant hub

| Evidence axis | Value |
|---|---|
| Identity hypothesis | anchor **`اله`** / lemma **`ٱللَّه`**, confidence 0.240 |
| Competing hypotheses | none reach the floor — single anchor in a broad field |
| Coherence (HHI) | 0.100 (low — one connected field, no single dominant root) |
| Ambiguity (entropy) | **0.852** (very high) |
| Consistency verdict | `diffuse_unified` |
| Semantic fields | **1 field of all 24 roots** (everything interlinks), anchor `اله`, support 100/100 signature ayahs |
| Recurring nominal anchors (POS N/PN/ADJ) | `اله` · `امن` · `شيا` · `حقق` · `علم` |
| Recurring verbal anchors (POS V) | `كون` · `قول` · `علم` · `اتي` · `نزل` |
| Structural "outcomes" (downstream anchors) | `شفع` · `رفت` · `اله` · `عوم` |
| Falsification | **survives** — only 4% of signature ayahs lack `اله` (pressure 0.02) |
| Evidence graph | 39 nodes / 135 edges |

**Reading (evidence only):** `CONCEPT_007` is one large connected lexical field
anchored on `اله` / `ٱللَّه`, but so broad that no single root dominates its
weight (entropy 0.85). The single anchor survives falsification — it is present in
almost every signature ayah — yet the identity is `moderate`, not `strong`,
because the field is diffuse. The most-likely Quran-internal anchor for
`CONCEPT_007` is **`ٱللَّه` (root `اله`)**.

---

## 2. `CONCEPT_016` — the secondary core

| Evidence axis | Value |
|---|---|
| Identity hypothesis | anchor **`جنن`** / lemma **`جَنَّة`**, confidence 0.168 |
| Coherence (HHI) | 0.093 · Ambiguity 0.905 · verdict `diffuse_unified` |
| Semantic fields | 1 field of all 16 roots, anchor `جنن`, support 100/100 |
| Recurring nominal anchors | `نهر` · `جنن` · `تحت` · `خلد` · `نور` |
| Recurring verbal anchors | `جري` · `دخل` · `وعد` · `وقي` · `قطع` |
| Structural outcomes | `اله` · `شرب` · `جري` · `نقذ` |
| Falsification | **survives** (pressure 0.07) |
| Evidence graph | 39 nodes / 118 edges |

**Reading:** `CONCEPT_016` is a single connected field anchored on `جنن` /
`جَنَّة`, with a recurring co-cluster of `نهر`, `خلد`, `نور`, `جري`, `وعد`,
`وقي`. The anchor survives falsification. Most-likely Quran-internal anchor:
**`جَنَّة` (root `جنن`)** — diffuse but coherent.

---

## 3. `CONCEPT_081` — the hub partner

| Evidence axis | Value |
|---|---|
| Identity hypothesis | anchor **`اله`** / lemma **`ٱللَّه`**, confidence **0.629** |
| Coherence (HHI) | **0.442** · Ambiguity 0.768 · verdict `coherent_single` |
| Semantic fields | 1 field of all 4 roots, anchor `اله`, support 100/100 |
| Recurring nominal anchors | `اله` · `كفر` · `يوم` · `بين` |
| Recurring verbal anchors | `كفر` · `بين` |
| Falsification | **survives** — only 2% of signature ayahs lack `اله` (pressure 0.01) |
| Tier | **strong** (the clearest single identity in the dataset) |

**Reading:** `CONCEPT_081` is a tight 4-root field overwhelmingly anchored on
`اله` / `ٱللَّه` (63% of activation weight). It is the strongest single identity
Monad finds.

---

## 4. The `اله` overlap (an honest ambiguity)

Both `CONCEPT_007` and `CONCEPT_081` resolve to the same anchor `اله` / `ٱللَّه`.
The engine reports this overlap rather than resolving it. They are separated by
their *other* evidence:

| | `CONCEPT_007` | `CONCEPT_081` |
|---|---|---|
| Anchor confidence | 0.240 | 0.629 |
| Roots | 24 | 4 |
| Activation | 5,906 ayahs (corpus-wide) | 2,553 ayahs |
| Field breadth | diffuse (entropy 0.85) | tight (entropy 0.77) |
| Co-anchors | `كون قول علم امن` | `يوم كفر بين` |

Same dominant root, two structurally distinct concepts. No meaning is assigned to
either; the overlap is preserved as evidence.

---

## 5. The size-9 dependency core (anchors)

The size-9 irreducible SCC (`003 004 034 053 060 061 084 085 088`, all layer 6):

| Concept | Anchor | Top name | Tier | Conf |
|---|---|---|---|---:|
| `CONCEPT_003` | — | — | resists | 0.0 |
| `CONCEPT_004` | — | — | resists | 0.0 |
| `CONCEPT_034` | `رحم` | `رَّحِيم` | moderate | 0.240 |
| `CONCEPT_053` | `عذب` | `عَذَاب` (competing `كفر`/`يوم`/`اخر`) | moderate | 0.276 |
| `CONCEPT_060` | `سوا` | `سُو^ء` | moderate | 0.450 |
| `CONCEPT_061` | `رسل` | `رَسُول` | moderate | 0.375 |
| `CONCEPT_084` | `قوم` | `قَوْم` | strong | 0.468 |
| `CONCEPT_085` | `رسل` | `رَسُول` | strong | 0.451 |
| `CONCEPT_088` | `رسل` | `رَسُول` | strong | 0.384 |

**Reading:** three of the nine (`061`, `085`, `088`) share the anchor `رسل`; two
(`003`, `004`) resist identification entirely (they are the most diffuse concepts
in the corpus). The irreducible core mixes strongly-anchored and identity-
resistant concepts — a structural fact reported without interpretation.

---

## 6. Top-20 foundational concepts (identity summary)

Of the 20 most foundational concepts (Phase 5), identity tiers are: 2 strong
(`084`, `085`), 11 moderate (incl. `007`, `016`, `081`, `034`, `053`, `060`,
`061`, `008`, `025`, `010`, `090`/`091`), and **5 resist** (`001`, `002`, `003`,
`004`, `013`). The most structurally central concepts are disproportionately the
hardest to name — foundationality and lexical concentration pull in opposite
directions.

---

## 7. Evidence graphs

Each deep dossier in `core_revelation.json` carries an `evidence_graph`: nodes are
the top-8 member roots, top-6 closest concepts, and top-6 signature ayahs; edges
are root↔root Phase-2 neighbour links and root→ayah "fires" links. These are
small, inspectable provenance graphs (35–39 nodes each) — the literal evidence
behind each identity hypothesis, with no gloss.

---

## 8. Reproduce

Source: `generated/revelation/core_revelation.json`, built by
`scripts/build_revelation.py`, validated by
`scripts/validate_revelation.py --rebuild`.

```bash
python3 scripts/build_revelation.py
python3 scripts/validate_revelation.py --rebuild
```

**No meaning assigned. Competing identities preserved. Concepts remain opaque
beyond their own Arabic evidence.**
