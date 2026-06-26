# RFC-000001 — Discovery Protocol v1 (سندِ نرماتیو)

> **وضعیت:** ACCEPTED — Frozen 2026-06-26  
> **نسخهٔ پروتکل:** 0.1.0  
> **سندِ طراحی:** [`docs/superpowers/specs/2026-06-26-discovery-protocol-design.md`](../docs/superpowers/specs/2026-06-26-discovery-protocol-design.md)  
> **تولیدشده پس از:** `monad run quran-root علم` — run_id `0b4891b72a439663`

---

## ۱. هدف

Discovery Protocol v1 چارچوبِ معماریِ موتورِ کشفِ مناد است: یک Unit (مثلاً یک ریشهٔ قرآنی)
را کاملاً خودکار، بازتولیدپذیر و قابل‌ارزیابی از substrate تا دانشِ ثبت‌شده کشف می‌کند.

**معیارِ موفقیتِ v1:** فرمانِ `monad run quran-root علم` بدونِ هیچ دخالتِ انسانی اجرا شود
و pipeline، Stores، Provenance DAG، Monad Memory، RFC، و Benchmark شش‌بُعدی تولید کند.

معماری از روزِ اول **مدل‌مستقل** و **دامنه‌مستقل** است. ریشهٔ «علم» فقط نمونهٔ اول است.

---

## ۲. معماریِ لایه‌ای

| لایه | مجری | قانون |
|---|---|---|
| **Substrate** | `generated/monad.db` | تغییرناپذیر؛ منبعِ یگانهٔ حقیقت |
| **Deterministic Core** | اسکریپت‌های پایتون | ۱۰۰٪ بازتولیدپذیر؛ تنها لایهٔ مجازِ ثبتِ Evidence/Knowledge |
| **Discovery Layer** | Reasoning Workers | فقط Hypothesis پیشنهاد می‌دهند؛ خروجی همیشه `PROPOSED` |
| **Orchestrator** | `engine/orchestrator.py` | جریانِ قطعی + صداکردنِ Workers + نوشتنِ Memory |

### ۲.۱ Reasoning Worker Interface

قراردادِ منجمد: `reason(WorkerRequest) -> artifact`. هر موتورِ استدلال (Statistical، Claude،
Human، Symbolic، GraphMiner، Solver) می‌تواند جایگزین شود بدونِ تغییرِ Orchestrator یا
schemaها. هیچ Worker مجاز به اعلامِ Knowledge نیست (اصلِ R1).

---

## ۳. اصولِ تغییرناپذیر

- **R1 — انحصارِ Verify:** تنها `engine/stages/verify.py` می‌تواند `status` را به `ACCEPTED` ببرد.
- **R3 — خطی‌بودن و بوکس‌کردنِ Worker:** مراحلِ اکتشافی فقط آرتیفکتِ مرحلهٔ قبل را می‌خوانند — هرگز DB، Store، یا Memory.
- **P1 — Evidence Immutability:** هیچ مرحله‌ای Evidence را تغییر نمی‌دهد.
- **P2 — Complete Provenance:** هر node دانش باید از طریقِ DAG به ≥۱ node شواهد برسد.
- **P3 — Knowledge Never Overwrites:** تعارض → نسخهٔ نو + یالِ `Supersedes`/`Refines`/`Contradicts`.

---

## ۴. خطِ لولهٔ ۹ مرحله‌ای

`Extract → Cluster → Observe → Hypothesis → Attack → Verify → Reduce → Graph → Commit`

| # | مرحله | لایه | خروجیِ کلیدی |
|---|---|---|---|
| 1 | **Extract** | قطعی·Substrate | Evidence اتمیِ تغییرناپذیر |
| 2 | **Cluster** | قطعی·۱ | خوشه‌ها + Patterns با lift/null_p |
| 3 | **Observe** | اکتشافی·بوکس·۲ | مشاهدات با cites (بدونِ فرضیه) |
| 4 | **Hypothesis** | اکتشافی·بوکس·۳ | ≤۵ فرضیهٔ PROPOSED با predicate از رجیستری |
| 5 | **Attack** | اکتشافی·بوکس·۴ | نقدِ مشورتی؛ status را تغییر نمی‌دهد |
| 6 | **Verify** | **قطعی·دروازه** | ACCEPTED/REJECTED/UNKNOWN — تنها زایندهٔ Knowledge |
| 7 | **Reduce** | قطعی·۶ | تعریفِ فشرده با MDL و coverage |
| 8 | **Graph** | قطعی·۷+KB | پیوندها + network_coherence + predictive_check |
| 9 | **Commit** | قطعی → Stores+DAG | ثبتِ رسمیِ Evidence/Knowledge/Ontology |

**ماشینِ حالتِ فرضیه:**
```
PROPOSED ──(Attack: مشورتی)──► (همچنان PROPOSED)
         ──(Verify فقط)──────► ACCEPTED | REJECTED | UNKNOWN
```

---

## ۵. پاکتِ استانداردِ آرتیفکت

هر خروجیِ مرحله یک envelope منجمد دارد:

```jsonc
{
  "envelope_version": "1.0",
  "stage": "<نام>", "stage_index": <1-9>,
  "unit": {"domain":"quran-root","ref":"Elm","display":"علم","unit_id":218},
  "substrate": {"id":"quran-hafs","hash":"sha256:…"},
  "protocol_version": "0.1.0",
  "run_id": "<content-derived — بازتولیدپذیر>",
  "produced_by": {"layer":"deterministic|discovery","tool":"…"},
  "inputs": {"prev_artifact":"sha256:…"},
  "produced_at": "<iso — اطلاعاتی؛ در هشِ بازتولید دخیل نیست>",
  "payload": {…}
}
```

---

## ۶. Knowledge — دو نمایش

```jsonc
{
  "knowledge_id": "k1",
  "formal_representation": {
    "definition_primitives": ["<onto:prim>"],
    "relations": [{"type":"<onto:rel>","to_unit":"<ref>"}],
    "verified_by": [{"predicate":"masked_recovery","score":0.21,"null_p":0.005}],
    "confidence_tier": "قوی"
  },
  "natural_explanation": "توضیحِ انسانی",
  "provenance_nodes": ["ev:2:31:2:1","art:<run>/s6","hyp:<run>/h1"]
}
```

---

## ۷. Predicate Registry

پریدیکیت‌ها جزوِ پروتکل‌اند، نه DomainAdapter. رجیستری *قرارداد* را تعریف می‌کند؛
DomainAdapter *مجری* را پیاده‌سازی می‌کند. پریدیکیت‌های v1:

| predicate | آزمون | شرطِ قبولی |
|---|---|---|
| `masked_recovery` | بازیابیِ unitِ ماسک‌شده از بافت | score > baseline ∧ null_p < 0.05 |
| `cooccurrence_constraint` | هم‌آییِ پایدارِ معنادار | lift > τ ∧ null_p < 0.05 |
| `two_half_stability` | تکرار روی دو نیمهٔ مستقل | |b−a| < ε |

---

## ۸. Provenance DAG

گرافِ جهت‌دارِ بدونِ دورِ سراسری در `store/provenance/`.

- **Node** ∈ `{evidence, artifact, observation, hypothesis, knowledge, definition, primitive}`
- **Edge** ∈ `{cites, derived_from, supports, refutes, verifies, reduces_to, Supersedes, Refines, Contradicts}`

**P2** با `store.provenance_complete(knowledge_id)` پیش از نوشتنِ RFC اجباری می‌شود.

---

## ۹. سه Store

```
store/
  evidence/    # مشاهداتِ اتمیِ تغییرناپذیر — سراسری، dedup با evidence_id (P1)
  knowledge/   # گزاره‌های تأییدشده — مرجعِ رسمیِ ماشین
  ontology/    # Primitiveها، Relationها، ساختارِ مفهومی
  provenance/  # DAG که هر سه را به هم می‌بندد
  log/         # append-only JSONL — منبعِ حقیقت
```

Storeها منبعِ رسمیِ ماشین‌اند. Builderهای آینده از آن‌ها تغذیه می‌شوند، نه از RFC.
RFC فقط Publication Layer است — idempotent و بازتولیدپذیر از Storeها.

---

## ۱۰. Monad Memory

```
memory/
  attempts/      # هر اجرا (موفق یا ناموفق)
  rejected/      # فرضیه‌های رد/ابطال‌شده
  failed_runs/   # اجراهای شکست‌خورده
  abandoned/     # مسیرهای رهاشده
  discoveries/   # اشاره به کشف‌های موفق (→ Knowledge Store)
```

Memory افزایشی و فقط‌نوشتنی است. مراحلِ بوکس‌شده آن را نمی‌خوانند (R3).

---

## ۱۱. Meta-Protocol

```
Protocol Candidate (vNext)
    ↓  اجرا روی مجموعهٔ benchmark منجمد
6-D Benchmark
    ↓
Pareto Evaluation (در برابرِ Current Stable)
    ↓  غلبه؟
Protocol Registry  ── بله → ارتقا به Current Stable
                   ── خیر → بایگانی (→ Monad Memory)
```

هیچ نسخهٔ نامزد جایگزینِ Stable نمی‌شود مگر با **غلبهٔ پارتو** (همه ≥، دستِ‌کم یکی >).

```
protocol/
  registry.json    # همهٔ نسخه‌ها: بردارِ benchmark + وضعیت (candidate|stable|superseded)
```

---

## ۱۲. Benchmark شش‌بُعدی

| بُعد | تعریفِ عملیاتی (۰..۱) | منبعِ داده |
|---|---|---|
| **Recoverability** | بازیابیِ `accepted_definition` روی held-out | Reduce → `predicts_heldout.score` |
| **Reproducibility** | Jaccardِ `knowledge_id`های ACCEPTED در N اجرا | N-run |
| **Falsifiability** | نسبتِ known-false از red-team که REJECTED شدند | redteam |
| **Compression** | `coverage` نرمال‌شده (MDL) | Reduce → `coverage` |
| **Coherence** | قبولیِ `network_coherence` | Graph |
| **PredictivePower** | دقتِ پریدیکیت روی واحدهای held-out | Graph → `predictive_check.score` |

**نتیجهٔ اولین اجرا (run_id: `0b4891b72a439663`, protocol_version: 0.1.0):**

| Recoverability | Reproducibility | Falsifiability | Compression | Coherence | PredictivePower |
|---|---|---|---|---|---|
| 0.5604 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |

وضعیتِ Meta-Protocol: نسخهٔ 0.1.0 ارتقا یافت به **current_stable** (اولین نسخه؛ null → stable).

---

## ۱۳. RFC Schema (نمای انسان/ممیزی)

```jsonc
{
  "rfc_id": "RFC-quran-root-Elm-v0.1.0-<run_id>",
  "unit": {…}, "protocol_version": "0.1.0", "run_id": "…",
  "status": "ACCEPTED",
  "supersedes": null, "relation_to_prior": null,
  "knowledge": [{
    "knowledge_id": "k1",
    "formal_representation": {…},
    "natural_explanation": "…",
    "confidence_tier": "قوی"
  }],
  "fields": {
    "evidence": {…}, "reasoning": {…}, "confidence": {…},
    "scope": {…}, "limitations": {…}, "relationships": {…}, "history": {…}
  },
  "benchmark_score": {… بردارِ ۶ بُعدی …}
}
```

---

## ۱۴. سیاستِ Freeze

- معماری در **2026-06-26** منجمد شد.
- تا کشفِ موفقِ **سه Unit اول**، هیچ تغییرِ معماری مجاز نیست — فقط رفعِ باگ.
- معیارِ پیشرفت دیگر تعدادِ اسناد نیست؛ `monad run quran-root علم` معیارِ نخست است.
- **معماری باید خودش را در میدان اثبات کند، نه پشتِ میزِ طراحی.**

---

## ۱۵. ارجاعِ کاملِ طراحی

طرحِ کاملِ معماری (همهٔ تعریف‌ها، diagrams، schemaها، سیاست‌ها) در:

```
docs/superpowers/specs/2026-06-26-discovery-protocol-design.md
```
