# Monad — Project Context

> Auto-loaded into every session. Concise by design; full detail in
> [`reference/`](reference/). This file is the durable basis for new chats.

## What this project is

Monad is a **self-interpreting analysis of the Quran**: it tries to understand the
Quran **from itself alone** — meaning induced purely from the text's internal
relations, with **no external dictionary, translation, or tafsir as input**. The
governing rules live in `constitution/` (the user-authored
`researcher-agent-charter.md` is supreme; `self-interpretation-charter.md` is
technical). Working history is in `journal/discovery-log.md`.

## The validated phenomenon — the Quran's self-interpreting network

The central claim — *"the network of connections between all verses interprets
itself"* — was **tested and confirmed**, internally, with leakage controls and
permutation nulls. Four independent, reproducible positives:

| Finding | Result |
|---|---|
| **Roots carry relational meaning** (L3) | a masked root is recoverable from its ayah context far above chance (matched 4.93% vs mismatched 0.18%, p=0.048) |
| **Verses explain one another** (L6) | knowing half a verse finds verses elsewhere supplying the other half — **~10× chance on rare content** (0.20 vs 0.019, p=0.005), cross-sura, leakage-controlled |
| **Suras are coherent communities** (L7) | connections concentrate within suras **~3× chance** (0.052 vs 0.017, p=0.005) |
| **Self-derived meanings are stable** (L8) | a concept's neighbourhood replicates across two independent halves of the Quran **~10×** (0.119 vs 0.012, p=0.005) |

Plus a real **Quran-by-Quran cross-reference map** (`generated/layers/L7_global/crossref_index.json`,
all 6,236 ayat) and concrete self-tafsir, e.g. 2:255↔7:97 (نوم/sleep), 24:35↔7:137
(شرق/غرب), 3:7↔9:117 (زیغ) — all discovered with zero external input.

**Bottom line for future work:** meaning lives in the **relational network of
roots across verses**. Build on this, not on the items below.

## What was tested and FAILED (do not rebuild on these)

- **Divine names as the "axes of meaning" / "law of interpretation"** — the
  user's founding premise. Tested **twice fairly** (distributional + structural,
  both leakage-controlled); **no signal beyond word frequency.** Honestly
  **downgraded** to an unconfirmed hypothesis (Charter Art. B). *Not declared
  false* — it may be non-distributional; the text remains the criterion. Names are
  kept as a studied feature, not the organizing axis.
- **Letters** (L1) — no semantic signal (structural/phonological only; OCP is
  real, meaning is not at letter level).
- **Word-forms** (L4) — add no meaning beyond the root.

## Related validated finding — book audit

A separate audit (`reference/` + `docs/book-quran-grounding-audit/`) tested
Jannatkhah's *نظریهٔ آزادی، ایران و دین* against its claim that its axioms are
Quran-based. Verdict: **rationally axiomatized and Quran-confirmed, not
Quran-axiomatized** (citations 42/42 real & in-context, p=0.0003; but 3 underived
axioms are secular-rational; "formal system" overstated — proto-formal 31/100).

## Legacy track — use with caution

`docs/` also holds ~200 reports from an **older 30-engine track** (Greek-letter /
numbered phases, `q1–q14`, `Phase ΩΣ`, etc.) predating the current discipline.
These were **not** held to the leakage-control + permutation-null standard. Treat
them as suggestive, **not validated**. (One interesting legacy observation worth
re-testing: the Quran leans "process/command register" over "static repository" —
52.7% process verb-aspect.)

## How to work here (operating principles)

Distilled in [`docs/هستهٔ-مولد.md`](docs/هستهٔ-مولد.md) (the "Generative Kernel"):

1. **Self-sufficiency first** — derive from the corpus; external refs only as a
   final, quarantined scorecard (`external/`), never as input.
2. **Falsification-first** — for every result: baseline, permutation null,
   leakage check, held-out. Keep only survivors. Report negatives honestly.
3. **Abstention over error** — mark UNKNOWN rather than assert beyond evidence;
   confidence tiers صریح/قوی/محتمل/نامشخص.
4. **Phase discipline** — build → validate (byte-identical reproducible) → report
   → commit. Each layer = `scripts/build_*.py` + `validate_*.py` + a report.
5. **The criterion governs** — the text/data is the measure, not the tool or the
   wish; downgrade even cherished hypotheses when data doesn't support them.

## Key locations

- Substrate DB: `generated/monad.db` (114 suras, 6,236 ayat, 128,219 tokens,
  1,642 roots; built by `scripts/build_database.py`).
- Validated pipeline outputs: `generated/layers/L1_letters … L8_interpret`,
  `L6_network`, `L7_global`, `scorecard`.
- Per-layer reports: `docs/L1-…` through `docs/L8-…`, `docs/L2-L3-robustness-report.md`,
  `docs/scorecard-report.md`.
- **Full findings reference:** [`reference/FINDINGS.md`](reference/FINDINGS.md).
- Method & worked examples: `docs/هستهٔ-مولد.md`, `docs/مثال-کاربرد-*.md`,
  `docs/گزارش-ساده-برای-روحانی.md`.
