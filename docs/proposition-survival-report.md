# Proposition Survival Report — Phase 17 (C)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase17-frequency-null-1.0`.

Phase C re-evaluates the Phase-4 proposition discoveries against the concept-
frequency null (1,000 realizations).

---

## 1. Results

| Measure | Observed | Null mean | z-score | Ratio | Structure % |
|---|---:|---:|---:|---:|---:|
| **Directed edges** | 438 | 110 | high | **3.9×** | **74.7%** |
| **Strong associations (NPMI≥0.2)** | 170 | 53 | **+19.7** | **3.2×** | **68.7%** |
| REQUIRES (necessity) edges | — | — | — | (frequency-driven) | — |

---

## 2. Findings

- **The proposition network strongly survives frequency control.** The observed
  directed graph has **3.9× more edges** than the frequency null, and **3.2× more
  strong associations** (z = +19.7). The relational structure Monad discovered in
  Phase 4 is genuine — concepts co-occur and associate far more specifically than
  their frequencies alone predict.
- **This is the strongest surviving discovery in Monad** (74.7% structure for
  edges). The co-occurrence/association network carries the most information beyond
  frequency of any discovered structure.
- **REQUIRES (necessity) is the exception** — it is frequency-driven: 96% of
  REQUIRES target the ubiquitous hub (Phase 15/16), so necessity reflects the hub's
  frequency, not specific structure.

---

## 3. Interpretation

The Phase-4 finding that the Quranic concepts form a dense, specific relational web
is **not** a frequency artifact. While a frequency-only null produces some
co-occurrence (concepts that are both frequent will sometimes co-occur), the
observed network has 3–4× more structure than that baseline. The associations are
**specific**: particular concepts associate with particular others far beyond
chance. **Hypothesis H2 survives.**

---

## 4. Verdict

> **Proposition structure survives frequency control** — edges 3.9× and strong
> associations 3.2× above the frequency null (z = +19.7). The relational network is
> Monad's strongest genuine structure (74.7% structure for edges). Necessity
> (REQUIRES) is the one frequency-driven exception. Hypothesis H2 survives.

---

## 5. Reproduce

```bash
python3 scripts/build_frequency_null.py
python3 scripts/validate_frequency_null.py --rebuild
```

Source: `generated/frequency_null/proposition_survival.json`.
