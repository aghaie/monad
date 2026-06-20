# L2 — Divine Names / Anchors Report (keystone)

- **Layer:** L2 (Monad v2 self-interpreting pipeline)
- **Claim level:** anchor discovery — a RANKED candidate set with confidence tiers (not a closed assertion).
- **Confidence tiers:** صریح/قوی/محتمل/نامشخص.
- **Source:** `generated/monad.db`. Outputs: `generated/layers/L2_names/`.
- **Reproducibility:** `validate_L2_names.py` passes 11/11, byte-identical re-run.

## Why this layer is the keystone

Per the Self-Interpretation Charter (Article B), the divine names are the
internal semantic anchors — the axes by which every other concept is located.
This layer discovers them **purely from the text** (the traditional 99-name list
is quarantined for the L8 scorecard and is **not** used here) and runs the first
test of the central thesis: *do concepts cohere with the names?*

## Discovery method (internal, documented)

No syntactic treebank exists in QAC v0.4, so perfectly extracting "what is
predicated of God" is not possible automatically. We therefore **rank** by three
convergent internal signals and assign confidence tiers, flagging confounds
honestly rather than asserting a closed list:

1. **predicate-of-Allah** — a STEM ADJ/N, indefinite, NOM/ACC, within 5 words
   after an "Allah" token (counted over distinct ayat). *(seed)*
2. **name-community** — names sit adjacent to other names (عزيزٌ حكيم); a
   candidate is reinforced by the average seed of its pair-partners.
3. **predicate-dominance** — a true name is predominantly used as a divine
   predicate (seed / total-frequency ratio); common nouns are not.

`name_score = seed × avg_partner_seed × (seed / frequency)`. The قوی cut places
`avg_partner_seed ≥ 12` at the natural gap in the data (genuine names ≥ 14;
rare fixed-collocation confounds such as قرض/ثمن ≤ 9.3).

## Discovered names — قوی/strong (16)

غفور · علیم · رحیم · حکیم · سمیع · خبیر · واسع · قدیر · حلیم · بصیر · عفوّ · رؤوف · قوی · محیط · شهید · وکیل

All 16 are genuine divine attributes. The unambiguous core (غفور، علیم، رحیم،
حکیم، سمیع، بصیر، قدیر) is recovered with no external input.

### Honest errors and limits

- **Famous names demoted to محتمل** (an honest finding, not a bug): عزیز، عظیم،
  حمید، توّاب، لطیف، إله، غنی، حسیب. These *are* names but have substantial
  non-divine usage (e.g. عزیز = "mighty/dear" of humans), so their
  predicate-dominance ratio is lower. The method correctly reports lower
  confidence rather than over-asserting.
- **Confounds correctly kept out of قوی** (flagged in محتمل): شیء (thing), قرض
  (loan), ثمن (price), کثیر (much), خیر (good) — high-frequency words that share
  the epithet slot ("على كل شيء قدير") but are not predicated of God.

## Anchor signatures (the axes)

Each قوی name's characteristic content roots (ayah-level co-occurrence, PPMI,
co-occurrence ≥ 3). Examples:

| Name | Top characteristic roots |
|------|--------------------------|
| غفور (forgiving) | توب×15 (repent), غفر, لحم/خنزر/دم (the 5:3 prohibitions), هجر |
| رحیم (merciful) | توب×26, غفر×23, لحم, هجر |
| علیم (knowing) | صدر×12 (what is in the breasts), فرض, جنح |
| قدیر (powerful) | کل×35 + شیء×41 ("over **all things** powerful"), ملک, موت (life/death) |
| بصیر (seeing) | عمل×20 ("seeing of what you **do**"), عمی (blindness), وجه |

These are coherent and characteristic — the anchor space is meaningful.

## THESIS TEST — do concepts cohere with the names?

**Task:** held-out (5-fold), predict which divine name seals an ayah **from the
ayah's content roots alone** (744 sealed instances, 16 names).

| Predictor | top-1 | top-3 |
|-----------|------:|------:|
| **Model** (Σ PPMI(name, content-root)) | **30.91%** | **68.55%** |
| Baseline (most frequent name) | 21.64% | 50.13% |
| Random floor | 6.25% | ~18.75% |

**Verdict: model beats baseline and random.** The content of a verse genuinely
predicts which divine name concludes it, well above chance and above the
frequency baseline. This is the **first internal empirical support for the
thesis that concepts cohere with the divine names** (Charter Article B) — the
law of interpretation, now with a measured signal behind it.

**Honest caveat:** 30.91% top-1 is far from perfect — the names overlap (many
mercy-themed ayat could end in غفور *or* رحیم), and this is a single, simple
model. It is evidence *for* the thesis, not proof; it will be strengthened (or
bounded) by L3–L8 and the final held-out scorecard.

## Prohibitions observed

No traditional name list, no external dictionaries, no tafsir, no translations,
no pretrained models. Discovery and validation are entirely internal.
