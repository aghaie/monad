# L6 — Inter-ayah Network Report  (the result we were searching for)

- **Layer:** L6 (Monad v2) — the network of connections between verses; the heart of the thesis.
- **Claim tested:** "the network of connections between all verses interprets itself" — do verses explain one another?
- **Source:** `generated/monad.db`. Outputs: `generated/layers/L6_network/`.
- **Reproducibility:** `validate_L6_network.py` passes 9/9, byte-identical re-run.

## The decisive, leakage-controlled test

For each ayah (≥ 4 content roots, 4,509 ayat):

1. Split its content roots into **KEY** and **TARGET** halves (deterministic).
2. Find its top-10 **neighbours** using **only the KEY roots**, and **only from
   other suras** (so neither the target roots nor mere proximity can leak).
3. Ask: do those neighbours contain the **TARGET** roots — which were never used
   to find them — more than 10 **random** ayat do?

If knowing half a verse lets the network find verses that supply the other half,
verses genuinely explain one another.

## Result — strongly positive

| Target roots | Network neighbours | Random ayat | p |
|--------------|-------------------:|------------:|---:|
| All | **0.545** | 0.325 ± 0.003 (max 0.334) | 0.005 |
| **Rare** (≤ 20 ayat) | **0.200** | 0.019 ± 0.003 (max 0.030) | 0.005 |

The network beats the random null beyond every one of 200 permutations
(p = 0.005). The strict test is the **rare** target roots: random pools almost
never contain them (1.9%), but the verses found through half of an ayah contain
its other-half rare content **20% of the time — about 10×.**

**Verses explain one another.** Knowing part of a verse lets the corpus's own
relational network locate other verses, across sura boundaries, that supply the
rest — especially the rare, meaningful content. This is the first strong,
leakage-controlled evidence for the project's central thesis: **the Quran's
inter-verse network carries real self-interpreting structure.**

## Where this sits in the honest picture

After several honest negatives, this is the real signal:

| Layer | Finding |
|-------|---------|
| L1 letters | no signal |
| L2 names-as-axes | not supported (2 fair tests) |
| **L3 roots** | **robust** (masked-root recovery) |
| L4 word-forms | no signal beyond root |
| **L6 inter-ayah network** | **strong** — verses explain one another (~10× on rare content) |

The meaning lives in the **relational network of roots across verses** — exactly
the self-interpreting structure the project set out to find, now measured and
leakage-controlled.

## Honest calibration

This is recovery of related **content** (lexical/relational relatedness across
verses), which is the *foundation* of interpretation, not finished interpretation
itself. The effect is large, robust, and controlled — strong support for the
thesis at the network level — but turning "verses that supply related content"
into actual self-translation remains the work of L7–L8. The artifact
`ayah_network.json` records each ayah's top cross-sura connections.

## Prohibitions observed

No external glosses, dictionaries, tafsir, translations, or pretrained models.
Entirely internal; cross-sura + key/target splitting remove proximity and target
leakage.
