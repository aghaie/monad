# Understanding-Obstacles Report — Phase X (E)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`epistemology-discovery-1.0`.

Phase E measures what *obstructs* understanding: which nodes carry net forward flow into
the combined target **blindness + deviation + forgetting** (عمى، صمم، بكم، وقر، ضلال،
زيغ، غيّ، نسيان، غفلة).

---

## 1. Obstacles, by net forward flow

| Node | Net forward | Directionality | Support |
|---|--:|--:|--:|
| **observe** | +33 | 0.60 | 159 |
| lying | +15 | 0.71 | 35 |
| compare | +14 | 0.72 | 32 |
| denial | +13 | 0.57 | 89 |
| read | +13 | 0.76 | 25 |
| listen | +9 | 0.59 | 49 |
| sealing | +5 | 0.67 | 15 |
| travel | +1 | 0.67 | 3 |

---

## 2. The decisive discovery: perception is bivalent

The most important — and most counter-intuitive — result of Phase X:

> **Observation is the top *obstacle* as well as the top *enabler*.** The very act of
> looking (نظر/بصر) flows into **blindness** (عمى) almost as strongly as into
> understanding. The same is true of read and listen. This is the Quran's own recurring
> figure — *"they look at you but do not see"*, *"deaf, dumb, blind"* — made structural:
> **perception does not determine the outcome.**

What separates the two outcomes is **not** a perceptual act but a **moral/volitional**
one. The nodes that flow into blindness with **no enabling counterpart** are **lying
(0.71), denial (0.57), sealing of the heart (0.67)** — and these appear *only* on the
obstacle side. Observation, listening, reading are **bivalent**; lying, denial, and
sealing are **purely obstructive**.

---

## 3. Finding

> **The obstacle to knowing is not a deficit of perception but a disposition of the
> will.** Looking, hearing, and reading lead to understanding *or* to blindness — the
> structure does not decide. What decides is whether the moral layer (lying, denial,
> arrogance, the sealed heart) intervenes. The Quran locates the failure of knowledge in
> **refusal, not in incapacity**: the eyes work; it is the heart that is sealed.
>
> This is the structural counterpart of Phase Q's caveat that method alone does not
> guarantee truth — and it emerged here independently, from directed flow, not from
> interpretation.

---

## 4. Reproduce

```bash
python3 scripts/build_epistemology.py
python3 scripts/validate_epistemology.py --rebuild
```

Source: `generated/epistemology/obstacles.json`.
