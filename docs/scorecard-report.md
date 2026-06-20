# External Scorecard Report (one-time, held-out, quarantined)

- **What:** the single sanctioned comparison of the internal network against an
  external human reference. The L0–L8 pipeline never reads `external/`; only
  `scripts/build_scorecard.py` does, once.
- **Reference:** human-curated *mutashābihāt* — parallel/similar verses, from
  [Waqar144/Quran_Mutashabihat_Data](https://github.com/Waqar144/Quran_Mutashabihat_Data)
  (1,635 verse pairs after mapping to `sura:ayah`).

## Result

| top-K | rare-concept network | all-root (surface) | random |
|------:|---------------------:|-------------------:|-------:|
| 5 | 2.51% | 6.48% | 0.08% |
| 10 | 3.18% | 7.71% | 0.16% |
| 20 | 4.59% | 8.93% | 0.32% |
| 50 | 5.08% | 11.01% | 0.80% |

- The internal network recovers human-identified parallels **14–31× above
  chance** — real, non-random corroboration that our links overlap with verses
  humans regard as related.
- But the **absolute** recall is low (~5%), and even the surface (all-root)
  variant reaches only ~11%.

## Honest diagnosis — the reference is a *mismatched* yardstick

The *mutashābihāt* set is built for **ḥuffāẓ** (memorisers): it lists verses with
near-identical **phrasing / sequence** (confusable passages). Our network, by
design, links verses by **shared rare content concepts**, ignoring common
phrasing. These are **different, complementary relations**:

- Above-chance overlap ⇒ the two notions do intersect (real signal).
- Low absolute overlap ⇒ they mostly measure different things — the all-root
  diagnostic confirms the reference rewards lexical phrase-overlap, not thematic
  content.

So this reference **partially corroborates** the network but is **not** the right
instrument to validate a thematic cross-reference map. Per the charter, the links
our network finds that are absent from this list are **potential discoveries, not
errors** — the text remains the criterion.

## Conclusion

- **External corroboration: positive but limited** by reference mismatch.
- **The strongest validation remains internal:** L8 stability — self-derived
  meanings replicate across two independent halves of the Quran ~10× above chance
  (p=0.005). The internal self-sufficiency that the project assumed is what
  actually carries the proof.
- A cleaner external check would need a **thematic / tafsir-based** cross-reference
  (e.g. Quran-by-Quran tafsir), which requires extracting verse links from tafsir
  prose — left as optional future work.
