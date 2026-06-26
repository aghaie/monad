---
name: discover-one-unit
description: Skill-0001 — اجرای Discovery Protocol برای یک Unit با ClaudeWorker به‌عنوانِ پیشنهاددهندهٔ فرضیه در مراحلِ اکتشافی (Observe/Hypothesis/Attack/Reduce-propose).
---
# Skill-0001 — Discover One Unit

این Skill، Claude را به‌عنوانِ یک ReasoningWorker به موتور متصل می‌کند. در هر مرحلهٔ
اکتشافی، payloadِ مرحلهٔ قبل را می‌خوانی و خروجی را **دقیقاً** مطابقِ schema تولید می‌کنی،
و در `run_dir/_claude/<capability>.json` می‌نویسی.

## مراحل

| مرحله | capability | ورودی | خروجی |
|---|---|---|---|
| Observe | `observe` | `{unit, context}` | `{observations: [...]}` |
| Hypothesis | `hypothesis` | `{unit, observations}` | `{hypotheses: [{text, evidence_ids, status}]}` |
| Attack | `attack` | `{unit, hypotheses}` | `{attacks: [{hypothesis_id, attack_text, severity}]}` |
| Reduce-propose | `reduce` | `{unit, hypotheses, attacks}` | `{proposed: [{text, evidence_ids, status}]}` |

## قواعد

1. **فقط فرضیه** — همهٔ `status` باید `PROPOSED` باشد؛ هرگز `KNOWLEDGE` یا `CONFIRMED` اعلام نکن.
2. **هر ادعا به evidence_id ارجاع دهد** — هر فرضیه باید حداقل یک `evidence_id` داشته باشد که به داده‌های corpus اشاره کند.
3. **هرگز DB/Store/آینده را نخوان** — فقط payloadِ جاری و فایل‌های `run_dir/_claude/` در دسترسِ مجاز هستند.
4. **schema رعایت شود** — هر capability یک فایل JSON در `run_dir/_claude/<capability>.json` می‌نویسد که با schema بالا مطابقت دارد.
5. **نوشتن، نه خواندن** — این Skill داده تولید می‌کند؛ تصمیم‌گیری با Orchestrator است.

## نحوهٔ اجرا

```bash
# اپراتور: پس از اجرای هر مرحله با ClaudeWorker از طریقِ این Skill،
# فایلِ خروجی را در مسیرِ run_dir/_claude/<capability>.json قرار بده.
# سپس Orchestrator با --worker claude دوباره اجرا می‌شود.
./monad run quran-root علم --worker claude --run-dir /path/to/run_dir
```

## نکتهٔ مهم

اگر `--worker statistical` باشد، ClaudeWorker فراخوانی نمی‌شود. این Skill فقط برای
اجراهای انسان‌در‌حلقه (human-in-the-loop) یا عامل‌محور (agent-driven) کاربرد دارد.
