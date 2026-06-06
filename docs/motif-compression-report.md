# Motif Compression Report — Phase 9 (D)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase9-motifs-1.0`.

Can a small set of motifs explain most observed structure? Phase D measures how
many motif classes are required to cover the 17,345 connected triad instances.
Structural counts only; no meaning.

---

## 1. Minimum motif sets

Greedy maximum-coverage over the 13 triad classes (universe = all connected triad
instances):

| Target | Motifs required | Compression ratio | Motif set (descriptors) |
|---:|---:|---:|---|
| 50% | **3** | 0.23 | mutual-path, in-merge, in-merge |
| 60% | 3 | 0.23 | (same 3 reach 60%) |
| 70% | 4 | 0.31 | + chain |
| 80% | **5** | 0.38 | + out-fork |
| 90% | 7 | 0.54 | + out-fork, cyclic-mixed triangle |
| 95% | 8 | 0.62 | + fully-mutual triangle |

**Three motif classes explain half of all triadic structure; five explain 80%;
eight explain 95%.** The Quranic relational network has an extremely small
*structural vocabulary*: almost all of its local connection patterns are one of a
few recurring shapes (reciprocal paths, convergences, divergences, chains).

**Answer — can a small motif set explain most structure? Yes.** This is the
strongest compressibility result in the project so far, *at the level of local
relational pattern*.

---

## 2. Comparison with Phase 8 (principles)

| Question | Phase 8 — principles | Phase 9 — motifs |
|---|---|---|
| Small set explains 50% of structure? | no (internal ceiling 9.9%) | **yes — 3 motifs** |
| Small set explains 80%? | no | **yes — 5 motifs** |
| Small set explains 95%? | no | **yes — 8 motifs** |
| Unit of explanation | global module (container) | local pattern (vocabulary) |

The contrast is the central Phase-9 finding. **Principles failed to compress the
structure; motifs succeed — but they explain a different thing.** A principle
tried to *contain* relations inside a module and could hold only 9.9% of them. A
motif does not contain relations; it *describes the shape* of how concepts
connect, and the network reuses only ~5 shapes for 80% of its triads.

**Are motifs more explanatory than principles?** For the *form* of the relational
structure, decisively yes: the network is built from a tiny pattern vocabulary.
For a *generative foundation*, no — motifs are a descriptive vocabulary, not a
small core from which the structure can be regenerated. The two results together
say: the Quranic network is **structurally repetitive but not reducible** — the
same few local patterns everywhere, woven into one irreducible global web.

---

## 3. What the compression does and does not claim

- **Does claim:** 5 of 13 directed-triad shapes account for 80% of the network's
  triads — a strong, evidence-based structural regularity.
- **Does not claim:** that these shapes have meaning, intention, or origin; that
  the network can be *generated* from them; or that 5 patterns "explain the Quran."
  They describe local relational form, nothing more.

---

## 4. Limitations

- Universe is triad instances; a 4-node motif basis would enlarge the vocabulary.
- Greedy coverage over disjoint isomorphism classes is exact here (classes
  partition the triad population), so the minimum sets are exact, not approximate.

---

## 5. Reproduce

```bash
python3 scripts/build_motifs.py
python3 scripts/validate_motifs.py --rebuild
```
