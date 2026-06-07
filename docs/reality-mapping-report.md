# Reality-Mapping Report — Phase R (H)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`reality-discovery-1.0`.

For each *surviving* law, Phase H asks where in reality the Quran displays it — which
domains carry the witness.

---

## 1. Where the surviving laws are shown

Aggregate domain-witness counts across the 9 surviving laws:

| Domain | Witness count |
|---|--:|
| ethics | 163 |
| history | 92 |
| human (person) | 80 |
| nature | 64 |
| society | 63 |
| psyche | 62 |
| power | 40 |
| economy | 29 |
| civilization | 25 |
| family | 21 |

---

## 2. Finding

> The Quran displays its surviving سنن **most through ethics, history, and the human
> person**, then nature, society, and the psyche. The downfall laws are shown above all
> in the **fate of peoples** (history) and the **moral field** (ethics); the
> deed→recompense law reaches into every domain. The Quran's preferred theatre for its
> reality-laws is the **rise and fall of nations and the moral life of the person** —
> not abstract doctrine, but the visible record of conduct and consequence.

The breadth (all ten domains carry some witness) confirms the cross-domain character;
the concentration (ethics + history + person) shows where the Quran chooses to make the
laws visible.

---

## 3. Reproduce

```bash
python3 scripts/build_reality.py
python3 scripts/validate_reality.py --rebuild
```

Source: `generated/reality/reality_mapping.json`.
