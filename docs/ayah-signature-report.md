# Ayah Signature Report — Phase 6

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase6-identification-1.0`.

This report summarises `generated/identification/ayah_signatures.json`: for each
of the 103 concepts, the top-25 / 50 / 100 ayahs that most strongly activate it,
with the firing member roots and lemmas as evidence. **No ayah is interpreted,
translated, or assigned meaning.** Concept ids stay opaque.

---

## 1. Definition

For each `(concept, ayah)`, **activation strength** = the summed Phase-3
membership confidence of the concept's member tokens that fire in the ayah, each
word counted once at its strongest membership. **Confidence** = activation
strength ÷ the concept's own maximum activation strength (a per-concept 0–1
scale). Ayahs are ranked by strength, then by member-token count, then by
position. Each entry stores `surah`, `ayah`, `activation_strength`, `confidence`,
`member_token_count`, and the `contributing_roots` / `contributing_lemmas`.

This is the Phase-4 activation rule, made quantitative. The active-ayah
population (6,101) is identical to Phase 4.

---

## 2. Aggregate evidence

- **Highest single activation strength anywhere:** ayah **2:282** for
  `CONCEPT_007`, strength 48.54 across 48 member tokens — the corpus's longest
  ayah and the strongest concept activation in the dataset.
- **Most-shared #1 ayahs.** Two ayahs are the single strongest activator for
  three different concepts each: **2:282** (`CONCEPT_007`, `CONCEPT_013`,
  `CONCEPT_081`) and **47:15** (`CONCEPT_016`, `CONCEPT_036`, `CONCEPT_072`).
  Ayahs that head two concepts include 4:102, 7:150, 22:73, 57:20, 24:35, 48:29.
- **Signature ayahs are dense, multi-root ayahs.** Top-ranked ayahs concentrate
  many member roots; e.g. `CONCEPT_016`'s top ayah 47:15 fires 11 distinct member
  roots (`صفو جنن مثل موه نهر نور قطع ثمر وعد وقي خلد`).

---

## 3. Representative ayah signatures (raw evidence)

### `CONCEPT_007` — top 10 ayahs

2:282 · 3:154 · 73:20 · 2:102 · 4:92 · 2:213 · 5:48 · 4:12 · 5:41 · 74:31
Dominant firing roots across these: `اله كون قول علم امن اتي بين شيا`.

### `CONCEPT_016` — top 8 ayahs

47:15 (str 10.71, conf 1.00, 22 tokens) · 65:11 · 9:72 · 13:35 · 4:57 · 64:9 ·
4:122 · 61:12. Firing roots: `جنن وعد نور وقي نهر خلد مثل دخل`.

### `CONCEPT_053` — top ayahs

57:20 (top) · concentrated in surah 2; firing roots `عذب كفر يوم اخر`.

### `CONCEPT_081` — top ayahs

2:282 (top) · firing roots `اله يوم كفر بين`; 2,553 activating ayahs total.

### `CONCEPT_102` — all 3 ayahs (rarest)

49:11 · 49:12 · (one further) — entirely within surah 49; firing roots
`جسس ليت لقب نبز`.

---

## 4. How to read the file

```jsonc
"CONCEPT_016": {
  "activation_count": 1199,
  "top_25":  [ { "surah":47, "ayah":15, "activation_strength":10.71,
                 "confidence":1.0, "member_token_count":22,
                 "contributing_roots":[…], "contributing_lemmas":[…] }, … ],
  "top_50":  [ … ],
  "top_100": [ … ]
}
```

Depths are capped at the concept's `activation_count` (concepts activating fewer
than 100 ayahs have shorter lists). Within each entry, `contributing_roots` and
`contributing_lemmas` are the literal members that fired — the evidence, with no
gloss.

---

## 5. Limitations

- Strength is one deterministic weighting (summed membership confidence); raw
  token counts are recoverable from `dominant_roots.json` / `dominant_lemmas.json`.
- A long ayah with many member tokens scores high by construction; `confidence`
  is normalised per concept to expose relative, not absolute, prominence.
- No ayah is read, translated, or interpreted. The signature is a count, not a
  reading.

---

## 6. Reproduce

```bash
python3 scripts/build_identification.py
python3 scripts/validate_identification.py --rebuild
```

**No meaning assigned. Concepts remain opaque.**
