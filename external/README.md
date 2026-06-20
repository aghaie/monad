# external/ — QUARANTINED reference data (scorecard only)

**These files are NOT part of the self-interpreting pipeline.** Per the
Self-Interpretation Charter (Article C / F), external resources are *quarantined*:
the L0–L8 build never reads this folder. Only `scripts/build_scorecard.py` touches
it, once, to compare the internally-derived network against a human reference —
never as input.

## Contents

- `mutashabiha_data.json` — human-curated list of *mutashābihāt* (textually
  similar / parallel verses), absolute ayah numbering (1–6236), grouped by juzʾ.
  Record form: `{"src": {"ayah": N}, "muts": [{"ayah": M}, …], "ctx"?}`.
  **Source / credit:** [Waqar144/Quran_Mutashabihat_Data](https://github.com/Waqar144/Quran_Mutashabihat_Data),
  based on the work of the late Qari Idrees Al Asim. License: free to use with
  acknowledgement.

## How it is used

`build_scorecard.py` maps absolute ayah numbers → `(sura:ayah)` via the substrate's
`ayah_sequential`, then measures how well the internal inter-ayah network (L6/L7)
recovers these human-identified parallels (recall vs a random baseline). Per the
charter, links our network finds that are *not* in this list are flagged as
potential discoveries, **not** errors — the text remains the criterion.
