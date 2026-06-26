# گزارشِ تکمیلِ Discovery Protocol v1

> تاریخ: ۲۰۲۶-۰۶-۲۷ · وضعیت: **کامل، بازبینی‌شده، و merge‌شده به `main`**
> Tag مرجع: `v0.1.0-discovery-protocol` (سنگ‌بنای آغازین / genesis prelude)

---

## ۱. خلاصهٔ یک‌خطی

موتورِ کشفِ مناد ساخته شد و **معیارِ موفقیتِ v1 محقق شد**:

```
./monad run quran-root علم
```

بدونِ هیچ دخالتِ انسان، کلِ خطِ لولهٔ ۹ مرحله‌ای را اجرا می‌کند و دانشِ تأییدشده،
Provenance، حافظه، RFC و بردارِ benchmark تولید می‌کند.

---

## ۲. مسیری که طی شد (از ایده تا سامانه)

۱. **منشور ثابت ماند** — تصمیم گرفتید دیگر Constitution ننویسیم.
۲. **brainstorming → طرحِ منجمد** — معماری در ۶ ایست‌گاهِ تأیید ساخته و در
   [`docs/superpowers/specs/2026-06-26-discovery-protocol-design.md`](superpowers/specs/2026-06-26-discovery-protocol-design.md) منجمد شد.
۳. **writing-plans → پلنِ ۱۸ Taskی** — در
   [`docs/superpowers/plans/2026-06-26-discovery-protocol-v1.md`](superpowers/plans/2026-06-26-discovery-protocol-v1.md).
۴. **subagent-driven execution** — هر Task: یک عاملِ مستقل → یک Commit → یک Review.
۵. **بازبینیِ کلِ شاخه (opus)** → یک اصلاحِ صداقتی.
۶. **Tag + merge محلی به main + اجرای مجددِ تست‌ها (۱۰۰٪ سبز).**

---

## ۳. معماریِ ساخته‌شده (منجمد)

- **دو لایه با مرزِ اقتدار:** هستهٔ قطعی (تنها زایندهٔ Knowledge) ↔ Reasoning Workerها
  (فقط پیشنهادِ فرضیه؛ خروجی همیشه `PROPOSED`).
- **خطِ لولهٔ خطیِ ۹ مرحله‌ای:**
  `Extract → Cluster → Observe → Hypothesis → Attack → Verify → Reduce → Graph → Commit`.
- **مدل‌ناوابستگی:** `ReasoningWorker` (پیش‌فرض `StatisticalWorker` قطعی؛
  `ClaudeWorker`/`HumanWorker` قابل‌تعویض پشتِ قراردادِ منجمد).
- **ناوردایی‌های منجمد:** R1 (تنها Verify دانش می‌زند) · R3 (خطی‌بودن و بوکس‌کردنِ مدل) ·
  P1 (تغییرناپذیریِ Evidence) · P2 (Provenance کامل) · P3 (دانش بازنویسی نمی‌شود).
- **سه Store + Provenance DAG + Monad Memory + Meta-Protocol + benchmark شش‌بُعدیِ پارتو.**
- **RFC = لایهٔ انتشار** (نه خروجیِ نهایی؛ از Store بازتولیدپذیر).

---

## ۴. نتیجهٔ واقعی برای ریشهٔ «علم»

| سنجه | مقدار |
|---|---|
| مراحلِ اجراشده | هر ۹ مرحله، بی‌خطا |
| دانشِ تأییدشده | **۵** — `h_p0` (صریح، lift=8.57)، `h_p13` (صریح، 3.22)، `h_p14` (قوی، 1.87)، `h_recover` (محتمل)، `h_stable` (محتمل) |
| ردِّ نمونهٔ غلط | علم↔فيل → `REJECTED` (Falsifiability) |
| بردارِ benchmark | Recoverability 0.56 · Reproducibility 1.0 · Falsifiability 1.0 · Compression 1.0 · Coherence 1.0 · PredictivePower 1.0 |
| نسخهٔ پروتکل | به `stable 0.1.0` ارتقا یافت |

دانش‌ها **دونمایشی** ذخیره شدند (`formal_representation` + `natural_explanation`) و هر کدام
زنجیرهٔ Provenance کامل تا Evidence-id دارند.

---

## ۵. کیفیت و انضباط

- **۷۱/۷۱ تست سبز** روی `main`؛ شاملِ **۹ Golden Artifact** بایت‌سطح.
- **stdlib خالص** (Python 3.9؛ بدون numpy/scipy/sklearn)؛ کاملاً قطعی (seed `20260626`).
- **هر Commit قابل‌اجرا** و **stage-gated**؛ کنوانسیونِ `prev_artifact = hash(payload)` که
  نشتِ timestamp را حذف می‌کند (در اصلاحِ نهایی هم خودش را اثبات کرد).
- **۳ باگِ واقعی در حینِ اجرا کشف و اصلاح شد** (همه Bug Fix، طبقِ Rule 0):
  1. `prev_artifact` نباید envelope را هش کند (timestamp → بی‌قطعیتی).
  2. `evaluate_candidate` باید idempotent باشد (اجرای مجددِ نسخهٔ stable نباید آن را تنزل دهد).
  3. **اصلاحِ صداقتی:** `two_half_stability` یک «بررسیِ حضور» است نه آزمونِ تکرارِ آماری —
     `null_p:0.0`ِ گمراه‌کننده حذف و به `null` + `method:"presence_in_both_halves"` تغییر کرد و
     در limitationsِ RFC ثبت شد. (هم‌خط با «خودداری بر خطا» در منشور.)

---

## ۶. آنچه به نسخهٔ بعد موکول شد (backlog-v2)

در [`docs/superpowers/backlog-v2.md`](superpowers/backlog-v2.md):
- جایگزینیِ `two_half_stability` با آزمونِ واقعیِ split-half.
- dedup یال‌های DAG؛ اجبارِ P3 در `put_knowledge` برای چند-Unit.
- honor کردنِ `n_repro`؛ حذفِ تولیدِ دوبارهٔ RFC؛ فیلترِ knowledge بر اساسِ Unit.
- سیاستِ Golden مقیاس‌پذیر (هش/fixture به‌جای ۶۱۸KB در هر ریشه).
- سخت‌سازیِ قطعیت با کلیدِ مرتب‌سازیِ ثانویه در نقاطِ tie.

---

## ۷. وضعیتِ مخزن

- **`main`** اکنون روی `9821858` (fast-forward؛ شاملِ کلِ کارِ v1).
- **Tag** `v0.1.0-discovery-protocol` نقطهٔ مرجعِ تاریخی را علامت زده.
- شاخهٔ `feat/self-interpretation-engine` **حفظ شد** (فقط برای Bug Fix باز می‌ماند).
- **push نشد** (merge محلی بود). برای انتشار: `git push origin main --tags`.

نقشهٔ کد:
```
monad                       # CLI
engine/                     # موتورِ عمومی: orchestrator, stages/, workers/,
                            #   predicates/, benchmark/, store.py, memory.py, metaprotocol.py
domains/quran_root/adapter.py   # تنها کدِ مخصوصِ قرآن
rfc/generator.py + RFC-000001-discovery-protocol.md
protocol/registry.json      # Meta-Protocol (current_stable: 0.1.0)
tests/engine/ + tests/golden/   # ۷۱ تست + ۹ Golden
```

---

## ۸. سیاستِ Freeze (مهم)

> **از این لحظه Discovery Protocol v1 تغییر نمی‌کند.** هر ایدهٔ جدید → Backlog v2 یا یک
> Protocol Candidate v0.2. v1 سنگ‌بنای تاریخیِ مناد است و دست‌نخورده می‌ماند.

قدمِ منطقیِ بعدی (هر وقت خواستید): کشفِ **ریشهٔ دوم و سوم** با همین پروتکلِ بدونِ تغییر —
طبق قانونِ پروژه: *«First make one root discoverable. Then make all roots scalable.»*
تعمیم، اکنون یک مسئلهٔ مهندسی است، نه مفهومی.
