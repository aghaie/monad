# Identity Confidence Report — Phase 7

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase7-revelation-1.0`.

This report grades, but does not assert, the Quran-internal identity of each
concept. Confidence is a concentration / agreement / survival statistic over the
concept's own Arabic evidence — **never a truth value, and never a meaning.** No
certainty is claimed.

---

## 1. How confidence is computed

For each concept with a candidate identity:

```
overall_identity_confidence =
    mean( name_confidence,                  # anchor root activation share
          identity_coherence_hhi,           # Herfindahl of root weights
          1 - identity_ambiguity_entropy,   # 1 - normalised entropy of root weights
          1 - falsification_pressure )       # 1 - how falsifiable the anchor is
```

**Tiers:**

| Tier | Rule |
|---|---|
| `strong` | name_confidence ≥ 0.30 **and** HHI ≥ 0.30 **and** survives falsification |
| `moderate` | name_confidence ≥ 0.15 **and** survives falsification |
| `weak` | a candidate exists but is falsified by its own evidence |
| `resists` | no member root reaches the dominance floor (share ≥ 0.15) |

---

## 2. Distribution

| Tier | Count | Share |
|---|---:|---:|
| strong | 43 | 41.7% |
| moderate | 51 | 49.5% |
| weak | 3 | 2.9% |
| resists | 6 | 5.8% |

`overall_identity_confidence`: min 0.000 · median **0.382** · max **0.731**
(`CONCEPT_095`, anchor `صَيْحَة`).

**Answering the success criteria:**

- *Identities strongly supported* — **43 concepts** (tier `strong`). The clearest:
  `CONCEPT_095` (`صَيْحَة`), `063` (`سِحْر`), `091` (`مَّعْرُوف`), `066` (`صَفّ`),
  `082` (`ءَالَا^ء`), `081` (`ٱللَّه`), `078` (`زَوْج`).
- *Identities that remain ambiguous* — the **51 moderate** concepts, plus the
  **42 concepts that carry competing names**, plus the four shared anchors
  (`اله`, `رسل`, `كفي`, `قمص`) that head more than one concept.
- *Concepts that resist identification* — **6 concepts** (`001`–`004`, `013`,
  `017`): large, lexically flat fields with no dominant root.
- *Competing explanations* — preserved verbatim in `candidate_names.json`; e.g.
  `CONCEPT_053` carries `عَذَاب`/`كَفَرَ`/`يَوْم`/`ا^خِر` as four near-equal
  anchors.

---

## 3. Most-likely identities — the two flagship concepts

| Concept | Most-likely anchor (Quran-internal) | Confidence | Tier | Note |
|---|---|---:|---|---|
| `CONCEPT_007` | `ٱللَّه` / root `اله` | 0.240 | moderate | broad diffuse field; survives falsification |
| `CONCEPT_016` | `جَنَّة` / root `جنن` | 0.168 | moderate | single connected field; survives falsification |

These are reported as the dominant Quran-internal anchors, not as meanings.

---

## 4. Consistency verdicts (Phase D)

| Verdict | Count | Definition |
|---|---:|---|
| `coherent_single` | 15 | one root dominates (HHI ≥ 0.40) |
| `coherent_dominant` | 55 | a clear lead root (HHI ≥ 0.20) |
| `diffuse_unified` | 33 | one connected field, no single dominant root |
| `fragmented` | 0 | multiple disconnected fields with no lead — none observed |

Notably, no concept is *fragmented*: every concept's member roots form one (or
two) connected semantic fields. Identity weakness here is **diffusion**, not
**fragmentation** — concepts are unified but sometimes flat.

---

## 5. Confidence vs structural centrality

The Phase-5 foundational core is inversely correlated with identity confidence:
the highest-reach concepts (`007`, `003`, `004`) are among the lowest in lexical
concentration (`003`, `004` resist entirely). Conversely, the strongest single
identities are small, peripheral, tightly-anchored concepts. Reach and namability
trade off.

---

## 6. Limitations

- Confidence is a statistic over Arabic evidence, not a claim of correctness.
- The tier thresholds (0.15 / 0.30) are deterministic choices; raw per-component
  numbers are published in `identity_confidence.json` for re-grading.
- A concept may have a true distributed identity that no single anchor captures;
  `resists` records exactly that, without forcing a name.

---

## 7. Reproduce

```bash
python3 scripts/build_revelation.py
python3 scripts/validate_revelation.py --rebuild
```

**No certainty claimed. No meaning assigned.**
