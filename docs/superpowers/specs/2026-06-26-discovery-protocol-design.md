# Discovery Protocol v1 — طرحِ معماری (FROZEN)

> سندِ طراحیِ چرخهٔ اولِ موتورِ کشفِ مناد.
> وضعیت: **Frozen 2026-06-26**. پس از Freeze، تا کشفِ موفقِ سه Unit اول هیچ تغییرِ
> معماری مجاز نیست — فقط رفعِ باگ و جمع‌آوریِ داده. «معماری باید خودش را در میدان اثبات
> کند، نه پشتِ میزِ طراحی.»
>
> این سندِ *طراحی* است. سندِ نرماتیوِ `rfc/RFC-000001-discovery-protocol.md` خودش یکی از
> خروجی‌های پیاده‌سازی است که همین معماری را رسمی می‌کند.

---

## 0. هدف، قانونِ پروژه، و معیارِ موفقیت

موتوری بساز که **یک Unit** (در نمونهٔ اول: یک ریشهٔ قرآنی) را کاملاً خودکار،
بازتولیدپذیر و قابل‌ارزیابی، از substrate تا دانشِ ثبت‌شده کشف کند.

> **قانون پروژه:** *First make one root discoverable. Then make all roots scalable.*
> تمرکزِ v1 مقیاس نیست؛ **اثباتِ معماری** است.

معماری از روزِ اول **مدل‌مستقل** و **دامنه‌مستقل** است: قرآن و ریشهٔ «علم» فقط *نمونهٔ
اول*‌اند، نه بخشی از موتور.

> **معیارِ موفقیتِ v1 (نه تعدادِ اسناد):** فرمانِ زیر بدونِ دخالتِ انسان اجرا شود —
> ```
> monad run quran-root علم
> ```
> و به‌صورتِ خودکار: Pipeline اجرا شود · Artifactها تولید شوند · Evidence/Knowledge/Ontology
> Store به‌روزرسانی شوند · Provenance DAG گسترش یابد · Monad Memory ثبت شود · RFC تولید شود ·
> Benchmark محاسبه شود. اگر این یک اجرا موفق شود، مناد از طراحی به سامانهٔ واقعی تبدیل شده است.

---

## 1. واژگانِ عمومی

| واژه | معنا | نمونهٔ اول |
|---|---|---|
| **Substrate** | مرجعِ تغییرناپذیر؛ منبعِ یگانهٔ حقیقت | `generated/monad.db` (قرآن حفص) |
| **Unit** | واحدِ تحتِ کشف | یک ریشه (root) |
| **Evidence** | مشاهدهٔ اتمیِ تغییرناپذیر از substrate، با id پایدار | token با مبدأ `S:A:W:T` |
| **Artifact** | خروجیِ منجمدِ یک مرحله (JSON) | `06_verify.json` |
| **Hypothesis** | ادعای ابطال‌پذیرِ مقیّد به شواهد که یک Reasoning Worker پیشنهاد می‌دهد | — |
| **Knowledge** | فرضیه‌ای که از Verify عبور کرده؛ دارای دو نمایش | — |
| **Evidence Store** | انبارِ سراسریِ تغییرناپذیرِ شواهد | `store/evidence/` |
| **Knowledge Store** | انبارِ گزاره‌های تأییدشده (مرجعِ رسمیِ ماشین) | `store/knowledge/` |
| **Ontology Store** | Primitiveها، Relationها، ساختارِ مفهومی | `store/ontology/` |
| **Monad Memory** | تاریخِ تلاش‌ها: شکست‌ها، ردها، مسیرهای رهاشده | `memory/` |
| **RFC** | نمای انسانی/ممیزیِ تولیدشده از Storeها | `rfc/<domain>/<unit>/…` |
| **DomainAdapter** | تنها جایی که کدِ مخصوصِ یک دامنه زندگی می‌کند | `domains/quran_root/` |
| **Reasoning Worker** | مجریِ استدلالِ قابل‌تعویض (هر موتورِ استدلال) | `ClaudeWorker` |
| **Orchestrator** | کنترلِ جریانِ قطعی | `discovery/orchestrator.py` |
| **Meta-Protocol** | سازوکارِ تکاملِ خودِ پروتکل | `protocol/` |

---

## 2. معماریِ لایه‌ای

| لایه | چه‌کسی | قانون |
|---|---|---|
| **Substrate** | `monad.db` | تغییرناپذیر (Constitution §14). منبعِ یگانه. |
| **Deterministic Core** | اسکریپت‌های پایتون | ۱۰۰٪ بازتولیدپذیر (seed ثابت، بدون شبکه). تنها لایه‌ای که Evidence و Knowledge را **ثبتِ رسمی** می‌کند. اقتدارِ Verify اینجاست. |
| **Discovery Layer (Proposers)** | Reasoning Workerها | فقط **Hypothesis** پیشنهاد می‌دهند. هرگز Knowledge اعلام نمی‌کنند. خروجی همیشه `PROPOSED`. |
| **Orchestrator** | کنترلِ جریان | مراحلِ قطعی را خودکار اجرا می‌کند؛ در مراحلِ اکتشافی Worker را صدا می‌زند؛ Memory را می‌خواند/می‌نویسد. |

### 2.0 اقتدار، نه قطعیت

مرزِ Deterministic/Discovery دربارهٔ **اقتدار** است، نه قطعیت. برخی Workerها خودشان
قطعی‌اند (Statistical, Graph Miner, Solver)، اما باز هم فقط **پیشنهاددهنده**‌اند: خروجی‌شان
`PROPOSED` است و باید از Verify عبور کند. هیچ Worker — هرچقدر قطعی — اجازهٔ زدنِ Knowledge
ندارد. (R1)

### 2.1 Reasoning Worker Interface (اصلِ مدل‌ناوابستگی — Δ3)

Interface برای **هر موتورِ استدلال** طراحی شده، نه فقط LLM. هر Worker یک *قابلیت*
(capability) را تأمین می‌کند؛ هر مرحلهٔ اکتشافی قابلیتِ موردنیازش را اعلام می‌کند و هر
Workerِ دارای آن قابلیت می‌تواند آن را اجرا کند. خروجی، صرف‌نظر از موتور، باید با schemaی
منجمد اعتبارسنجی شود.

```
Orchestrator (قطعی، مالکِ کنترلِ جریان)
   │  WorkerRequest(capability, input_artifact, output_schema, task_spec)
   ▼
ReasoningWorker Interface  (قراردادِ منجمد: reason(request) -> artifact)
   ├── LLMWorker         (ClaudeWorker [v1] · GPTWorker · GeminiWorker · LocalModelWorker)
   ├── HumanWorker       (Debug / Gold — سقفِ کیفیت)
   ├── SymbolicWorker    (موتورِ نمادین)
   ├── GraphMinerWorker  (کاوشِ گراف)
   ├── StatisticalWorker (موتورِ آماری)
   └── SolverWorker      (SAT/SMT)
```

اگر موتورِ استدلال عوض شود، فقط «مجریِ مرحله» عوض می‌شود — نه Orchestrator، نه schemaها،
نه پروتکل.

### 2.2 جریانِ کلانِ سیستم

```
Substrate
  └─▶ Artifacts(1..8) ──▶ Verified Knowledge(Verify) ──▶ [Commit(9)]
                                                            ├──▶ Evidence Store
                                                            ├──▶ Knowledge Store ──▶ RFC Generator ──▶ RFC
                                                            ├──▶ Ontology Store          (نمای انسان/ممیزی)
                                                            └──▶ Provenance DAG
  هر اجرا (موفق یا ناموفق) ─────────────────────────────────▶ Monad Memory
  Builders (آینده) ◀── از Storeها تغذیه می‌شوند، نه از RFC
```

- **Storeها منبعِ رسمیِ ماشین‌اند.** Builderها از آن‌ها تغذیه می‌شوند، نه از RFC.
- **RFC فقط Publication Layer است** — idempotent و بازتولیدپذیر از Storeها.

---

## 3. اصولِ تغییرناپذیر (FROZEN INVARIANTS)

با گیت‌های اعتبارسنجیِ قطعی اجباری می‌شوند.

- **R1 — انحصارِ Verify:** هیچ Worker/مرحلهٔ اکتشافی حق ندارد `status` را به `ACCEPTED`
  ببرد. تنها `verify.py`.
- **R3 — خطی‌بودن و بوکس‌کردنِ Worker:**
  1. هیچ مرحله‌ای خروجیِ *آینده* را نمی‌خواند؛ ورودیِ اصلیِ هر مرحله آرتیفکتِ مرحلهٔ قبل
     است. اجرا کاملاً Replayable (هشِ Substrate/KB در manifest قفل می‌شود).
  2. فقط مراحلِ **قطعی** (Extract, Verify, Graph, Commit) زمینِ منجمد (Substrate / Storeها)
     را می‌خوانند.
  3. مراحلِ **اکتشافی** کاملاً بوکس‌اند: فقط آرتیفکتِ مرحلهٔ قبل. هرگز DB، هرگز Store، هرگز
     Memory، هرگز آینده. (اگر دانشِ گذشته لازم است، Orchestrator آن را به‌صورتِ ورودیِ
     تمیزشده تزریق می‌کند.)
- **P1 — Evidence Immutability:** هیچ آرتیفکتی Evidence را اضافه/حذف/تغییر نمی‌کند. همهٔ
  تبدیل‌ها فقط روی Metadata/Hypothesis/Knowledge.
- **P2 — Complete Provenance:** هر node دانش و هر میدانِ RFC باید از طریقِ DAG به ≥۱ node
  شواهد پیمایش‌پذیر باشد.
- **P3 — Knowledge Never Overwrites:** دانش افزایشی است. تعارض → نسخهٔ نو + یالِ تایپ‌دار
  (`Supersedes`/`Refines`/`Contradicts`)؛ نسخهٔ قبلی دست‌نخورده.

---

## 4. خطِ لولهٔ ۹ مرحله‌ای

`Extract → Cluster → Observe → Hypothesis → Attack → Verify → Reduce → Graph → Commit`

| # | مرحله | لایه | می‌خواند | تغذیهٔ benchmark |
|---|---|---|---|---|
| 1 | Extract | قطعی | Substrate | پایهٔ همه |
| 2 | Cluster | قطعی | مرحلهٔ ۱ | Compression |
| 3 | Observe | اکتشافی (بوکس) | مرحلهٔ ۲ | — |
| 4 | Hypothesis | اکتشافی (بوکس) | مرحلهٔ ۳ | Falsifiability |
| 5 | Attack | اکتشافی (بوکس) | مرحلهٔ ۴ | Falsifiability |
| 6 | Verify | **قطعی — دروازهٔ دانش** | مرحلهٔ ۵ + Substrate + KB | Recoverability, Reproducibility, Coherence |
| 7 | Reduce | اکتشافی پیشنهاد → قطعی می‌سنجد | مرحلهٔ ۶ | Compression |
| 8 | Graph | قطعی | مرحلهٔ ۷ + KB | Coherence, Predictive Power |
| 9 | Commit | قطعی | زنجیرهٔ ۶+۷+۸ → Storeها | — |

### ماشینِ حالتِ فرضیه
```
PROPOSED ──(Attack: SURVIVES|WEAKENED|REFUTED، فقط مشورتی)──▶ (همچنان PROPOSED)
         ──(Verify فقط)──▶ ACCEPTED(+تیر اطمینان) | REJECTED | UNKNOWN
```
`REJECTED`/`REFUTED` → ثبت در Monad Memory.

---

## 5. پاکتِ استانداردِ همهٔ آرتیفکت‌ها

```jsonc
{ "envelope_version":"1.0", "stage":"verify", "stage_index":6,
  "unit":{ "domain":"quran-root", "ref":"Elm", "display":"علم", "unit_id":42 },
  "substrate":{ "id":"quran-hafs", "hash":"sha256:…" },
  "protocol_version":"0.1.0", "run_id":"<content-derived → بازتولیدپذیر>",
  "produced_by":{ "layer":"deterministic", "tool":"verify.py@<git_sha>" },
  //  یا { "layer":"discovery","worker":"ClaudeWorker","capability":"hypothesize","worker_model":"…","worker_config_hash":"…" }
  "inputs":{ "prev_artifact":"sha256:…", "substrate":"sha256:…", "kb_snapshot":"sha256:…" },
  "produced_at":"<iso — اطلاعاتی؛ در هشِ بازتولید دخیل نیست>",
  "payload":{ … } }
```
Evidence-id = رشتهٔ مبدأشناسیِ آداپتر (`S:A:W:T`). `run_id` محتوامحور → بازتولیدپذیر.

---

## 6. Schemaی payload هر مرحله (فشرده)

```jsonc
// 1 EXTRACT [قطعی·Substrate] — پایهٔ Evidenceِ تغییرناپذیر
{ "evidence":[ {"evidence_id":"2:31:2:1","locus":{…},"surface":"عَلَّمَ","features":{…},"context_ref":"2:31"} ],
  "contexts":[ {"context_id":"2:31","text":"…","text_hash":"…"} ],
  "unit_stats":{ "evidence_count":…,"context_count":…,"first":…,"last":…,"subunits":[…] } }

// 2 CLUSTER [قطعی·۱]
{ "method":{"algorithm":"…","params":{…},"seed":12345,"feature_space":[…]},
  "clusters":[ {"cluster_id":"c1","members":[…],"profile":{…}} ],
  "patterns":[ {"pattern_id":"p1","type":"cooccurrence","with":"<ref>","lift":3.2,"null_p":0.004,"support":[…]} ] }

// 3 OBSERVE [اکتشافی·بوکس·۲] — هر مشاهده باید cite کند؛ بدون فرضیه
{ "observations":[ {"observation_id":"o1","type":"description","statement":"…","cites":["c1","p1","2:31:2:1"]} ] }

// 4 HYPOTHESIS [اکتشافی·بوکس·۳] — ≤۵؛ predicate از رجیستریِ پروتکل
{ "hypotheses":[ {"hypothesis_id":"h1","status":"PROPOSED","claim":"…","supported_by":["o1","c1"],
                  "prediction":{"predicate":"masked_recovery","params":{…}}} ] }

// 5 ATTACK [اکتشافی·بوکس·۴] — مشورتی؛ status را تغییر نمی‌دهد
{ "attacks":[ {"hypothesis_id":"h1","refutations":[{"argument":"…","counter_evidence":[…]}],"worker_verdict":"SURVIVES"} ] }

// 6 VERIFY [قطعی·دروازه·۵+Substrate+KB] — تنها زایندهٔ Knowledge
{ "verifications":[ {"hypothesis_id":"h1",
    "tests":{"masked_recovery":{"score":0.21,"baseline":0.02,"null_p":0.005,"passed":true},
             "two_half":{"a":0.19,"b":0.20,"passed":true},"coherence":{"conflicts":[],"passed":true}},
    "decision":"ACCEPTED","confidence_tier":"قوی","knowledge_id":"k1"} ] }

// 7 REDUCE [اکتشافی پیشنهاد → قطعی می‌سنجد·۶] — دو زیرـآرتیفکت 07a.propose → 07b.measure
{ "proposed_definition":{"statement":"…","primitives":[…],"relations":[…]},
  "compression":{"n_primitives":3,"coverage":0.95,"mdl_bits":…,"predicts_heldout":{"score":…,"passed":true}},
  "accepted_definition":{"statement":"…","primitives":[…],"covers_knowledge":["k1","k2"]} }

// 8 GRAPH [قطعی·۷+KB]
{ "links":[ {"to_unit":"<ref>","relation":"co-defines|contrasts|specializes","weight":…,"evidence":[…]} ],
  "network_coherence":{"conflicts":[],"passed":true},
  "predictive_check":{"applied_to":[…واحدهای held-out…],"hits":…,"score":…} }

// 9 COMMIT [قطعی·زنجیرهٔ ۶+۷+۸ → Storeها + DAG + Memory]
```

آستانه‌های تصمیمِ Verify در پروتکل ثابت‌اند (مثلاً عبور از همهٔ آزمون‌های لازم + `null_p<0.05`
→ `ACCEPTED`؛ تیر بر اساسِ اندازهٔ اثر). کاملاً قطعی.

---

## 7. Knowledge — دو نمایش (Δ1)

```jsonc
{ "knowledge_id":"k1", "unit":{…}, "protocol_version":"…", "run_id":"…", "status":"ACCEPTED",
  "formal_representation":{                       // مرجعِ ماشین — به Ontology Store ارجاع می‌دهد
     "definition_primitives":["<onto:prim>"], "relations":[{"type":"<onto:rel>","to_unit":"<ref>"}],
     "verified_by":[ {"predicate":"masked_recovery","params":{…},"score":0.21,"null_p":0.005} ],
     "scope":{…}, "confidence_tier":"قوی" },
  "natural_explanation":"…توضیحِ انسانی…",          // فقط نمایش
  "provenance_nodes":["ev:2:31:2:1","art:<run>/s6","hyp:<run>/h1","def:<run>"],
  "relations_to_knowledge":[ {"type":"Refines","target":"k_prev"} ] }   // P3
```

---

## 8. Predicate Registry — سطحِ پروتکل (Δ2)

پریدیکیت‌ها جزوِ Discovery Protocol‌اند، نه DomainAdapter. رجیستری *قرارداد* را تعریف
می‌کند؛ DomainAdapter *مجری* را پیاده می‌کند.

```jsonc
// discovery/predicates/registry.json — دامنه‌مستقل
{ "masked_recovery":       {"params_schema":{…},"tests":"بازیابیِ unitِ ماسک‌شده از بافت","pass":"score>baseline ∧ null_p<0.05"},
  "cooccurrence_constraint":{"params_schema":{…},"tests":"هم‌آییِ پایدارِ معنادار","pass":"lift>τ ∧ null_p<0.05"},
  "morph_constraint":       {"params_schema":{…},"tests":"قیدِ صرفیِ پایدار","pass":"…"},
  "distributional_contrast":{"params_schema":{…},"tests":"تباینِ توزیعیِ دو خوشه","pass":"…"},
  "two_half_stability":     {"params_schema":{…},"tests":"تکرار روی دو نیمهٔ مستقل","pass":"…"} }
```
> *Primitiveها و Relationهای* مفهومی به **Ontology Store** می‌روند (نه پروتکل، نه Knowledge)؛
> *قراردادِ پریدیکیت* در پروتکل می‌ماند؛ *مجریِ پریدیکیت* در DomainAdapter.

---

## 9. Provenance DAG (Δ3-قبلی)

گرافِ جهت‌دارِ بدونِ دورِ سراسری (در Store).
- **Node** ∈ `{ evidence, artifact, observation, hypothesis, knowledge, definition, primitive }`
- **Edge** ∈ `{ cites, derived_from, supports, refutes, verifies, reduces_to, expressed_in, Supersedes, Refines, Contradicts }`

```jsonc
{ "nodes":[ {"id":"ev:2:31:2:1","type":"evidence"}, {"id":"art:<run>/s6","type":"artifact"},
            {"id":"hyp:<run>/h1","type":"hypothesis"}, {"id":"k1","type":"knowledge"} ],
  "edges":[ {"from":"hyp:<run>/h1","to":"ev:2:31:2:1","type":"cites"},
            {"from":"k1","to":"hyp:<run>/h1","type":"verifies"},
            {"from":"k1","to":"art:<run>/s6","type":"derived_from"},
            {"from":"k1","to":"k_prev","type":"Refines"} ] }
```
**P2** = هر node دانش باید مسیری به ≥۱ node شواهد داشته باشد.

---

## 10. سه Store (Δ2-جدید — تفکیکِ موجودیت‌ها)

به‌جای یک Store، سه موجودیتِ مستقل. Ontology هرگز با گزاره‌های تأییدشده مخلوط نمی‌شود.

```
store/
  evidence/        # Evidence Store — مشاهداتِ اتمیِ تغییرناپذیر؛ سراسری و dedup با evidence_id (P1)
  knowledge/       # Knowledge Store — گزاره‌های تأییدشده (اشیاءِ دانشِ دونمایشی)
  ontology/        # Ontology Store — Primitiveها، Relationها، ساختارِ مفهومی
  provenance/      # DAG که هر سه را به هم می‌بندد
  log/             # append-only؛ رویدادهای commit (JSONL، تغییرناپذیر) — منبعِ حقیقت
  index.db         # ایندکسِ SQLite، قابلِ بازسازیِ قطعی از log
  rebuild_index.py # log → index.db (بازتولیدپذیر)
```
- **Evidence Store** سراسری و مشترک بین Unitها/runهاست (یک token می‌تواند شواهدِ چند ریشه
  باشد). Extract آن را idempotent به‌روزرسانی می‌کند.
- **Knowledge Store** مرجعِ رسمیِ ماشین؛ Builderها از آن می‌خوانند.
- **Ontology Store** واژگانِ مفهومیِ روبه‌تکامل که Knowledge در آن بیان می‌شود (Constitution
  §7, §11). Reduce آن را تغذیه می‌کند.

---

## 11. Monad Memory (Δ4 — تاریخِ تلاش‌ها)

Storeها فقط *محصول* را نگه می‌دارند؛ Memory *فرایند* را — تا از تکرارِ مسیرهای شکست‌خورده
جلوگیری شود و تجربهٔ مناد شکل بگیرد.

```
memory/
  attempts/        # هر اجرای پروتکل (موفق یا ناموفق)
  rejected/        # فرضیه‌های رد/ابطال‌شده (Verify REJECTED + Attack REFUTED)
  failed_runs/     # اجراهای شکست‌خوردهٔ پروتکل
  abandoned/       # مسیرهای رهاشده
  discoveries/     # اشاره به کشف‌های موفق (→ Knowledge Store)
```
- Memory **افزایشی و فقط‌نوشتنی** است.
- مراحلِ بوکس‌شده آن را نمی‌خوانند (R3). **Orchestrator** آن را می‌خواند و در صورتِ لزوم
  به‌صورتِ ورودیِ تمیزشده به Worker تزریق می‌کند، یا برای ساختِ red-team set و هدایتِ
  Meta-Protocol استفاده می‌کند.

---

## 12. Meta-Protocol — تکاملِ خودِ پروتکل (Δ1-جدید)

Discovery Protocol اجرای کشف را تعریف می‌کند؛ Meta-Protocol تعریف می‌کند که خودِ پروتکل
چگونه نسخه‌بندی، ارزیابی و تکامل پیدا کند.

```
Protocol Candidate (vNext)
        ↓  اجرا روی مجموعهٔ benchmarkِ منجمد
   6-D Benchmark
        ↓
   Pareto Evaluation  (در برابرِ Current Stable)
        ↓  غلبه؟
   Protocol Registry  ── بله → ارتقا به Current Stable
        ↓               ── خیر → بایگانی به‌عنوان rejected candidate (→ Monad Memory)
   Current Stable  (اشاره‌گرِ نسخهٔ پایدارِ فعلی)
```
```
protocol/
  registry.json    # همهٔ نسخه‌ها: protocol_version، بردارِ benchmark، وضعیت (candidate|stable|superseded)
  current_stable   # اشاره‌گر به نسخهٔ پایدارِ فعلی
  candidates/      # نسخه‌های نامزد + نتایجِ ارزیابی
```
- هیچ نسخهٔ نامزد جایگزینِ Stable نمی‌شود مگر با **غلبهٔ پارتو** روی هر ۶ بُعد (≥) و دستِ‌کم
  یکی (>).
- Meta-Protocol خودش از Monad Memory و دفترچهٔ benchmark تغذیه می‌شود.

---

## 13. Schemaی رسمیِ RFC (نمای انسان/ممیزی)

```jsonc
{ "rfc_id":"RFC-quran-root-Elm-v0.1.0-<run_id>",   // تغییرناپذیر، یکتا
  "unit":{…}, "substrate":{…}, "protocol_version":"0.1.0", "run_id":"…", "produced_at":"…",
  "status":"ACCEPTED"|"SUPERSEDED",
  "supersedes":"<rfc_id|null>", "relation_to_prior":"Supersedes"|"Refines"|"Contradicts"|null,   // P3
  "definition":{ …accepted_definition از Reduce… },
  "knowledge":[ {"knowledge_id":"k1","formal_representation":{…},"natural_explanation":"…",
                 "confidence_tier":"قوی","provenance_nodes":[…]} ],
  "fields":{
    "evidence":     {…}, "reasoning":    {…}, "confidence":   {…},
    "scope":        {…}, "limitations":  {…}, "relationships":{…}, "history": {…}
  },
  "benchmark_score":{ بردارِ شش‌بُعدیِ همین run },
  "hashes":{ substrate, kb_snapshot, هر ۹ آرتیفکت } }
```
هفت میدانِ `fields` = هفت میدانِ Constitution §۶. **P2** با گیتِ `validate_provenance.py`
پیش از نوشتنِ RFC اجباری می‌شود.

---

## 14. Harnessِ شش‌بُعدیِ Benchmark (TDD)

`discovery/benchmark/score_run.py <run_dir> → بردار`. هر بُعد تابعِ خالصِ آرتیفکت‌های
منجمد؛ دامنه‌مستقل.

| بُعد | تعریفِ عملیاتی (۰..۱) | منبع |
|---|---|---|
| **Recoverability** | بازیابیِ ماسک‌شدهٔ `accepted_definition` روی held-out، نرمال با baseline | Verify/Reduce |
| **Reproducibility** | Jaccardِ `knowledge_id`های ACCEPTED در N اجرا (همان substrate+worker_config) | N-run |
| **Falsifiability** | نسبتِ فرضیه‌های known-false از red-team که درست REJECTED شدند | redteam |
| **Compression** | `coverage / n_primitives` نرمال (نسبتِ MDL) | Reduce |
| **Coherence** | `1 − conflicts/checks` در برابرِ KB | Verify+Graph |
| **Predictive Power** | دقتِ اعمالِ پریدیکیت‌ها روی واحدهای held-outِ دیگر | Graph |

- **قاعدهٔ پذیرش (پارتو):** هر بُعد `≥` و دستِ‌کم یکی `>`، روی مجموعهٔ منجمد (v1 = `{علم}`).
- **دفترچهٔ TDD:** `discovery/benchmark/ledger/<protocol_version>.json`.
- **red-team:** `discovery/benchmark/redteam/<unit_ref>.json` (تزریق در مرحلهٔ ۴؛ تغذیه از
  Monad Memory).

---

## 15. ساختار پوشه‌ها

```
monad                                       # CLI entry point → monad run <domain> <unit_ref>
protocol/                                   # Meta-Protocol
  registry.json · current_stable · candidates/
rfc/
  RFC-000001-discovery-protocol.md          # سندِ نرماتیوِ پروتکل (deliverable)
  generator.py                              # RFC Generator: Storeها → RFC (idempotent)
  registry.json                             # ایندکسِ RFCها + گرافِ supersedes
  <domain>/<unit_ref>/RFC-…-v<ver>-<run>.{md,json} + manifest.json   # snapshotِ تغییرناپذیر
discovery/                                  # موتورِ عمومی — هیچ کدِ قرآنی اینجا نیست
  orchestrator.py                           # کنترلِ جریانِ قطعی (run_unit)
  stages/        extract·cluster·verify·reduce_measure·graph·commit
  workers/       reasoning_worker.py (Interface) · claude_worker.py · human_worker.py
  prompts/       observe·hypothesis·attack·reduce
  predicates/    registry.json (+ executor contracts)
  schemas/       envelope + ۹ مرحله + knowledge + rfc
  benchmark/     score_run.py · ledger/ · redteam/ · units.json
  runs/<domain>/<unit_ref>/<run_id>/        # ۹ آرتیفکتِ هر اجرا
store/                                      # سه Store + DAG + log/index
  evidence/ · knowledge/ · ontology/ · provenance/ · log/ · index.db · rebuild_index.py
memory/                                     # Monad Memory
  attempts/ · rejected/ · failed_runs/ · abandoned/ · discoveries/
domains/
  quran_root/adapter.py                     # تنها کدِ مخصوصِ قرآن: extract، ev-id، featureها، مجریِ پریدیکیت‌ها
.claude/skills/discover-one-unit/SKILL.md   # Skill-0001 = اتصالِ ClaudeWorker به Interface
```

---

## 16. Deliverables چرخهٔ اول

1. `rfc/RFC-000001-discovery-protocol.md` — سندِ نرماتیوِ پروتکل.
2. `monad` CLI + `Skill-0001` (Discover One Unit) — اتصالِ ClaudeWorker.
3. تمام اسکریپت‌های لایهٔ قطعی (مراحلِ ۱،۲،۶،۷b،۸،۹ + generator + validators).
4. ReasoningWorker Interface + ClaudeWorker + HumanWorker.
5. Predicate Registry (پروتکل) + مجریِ آن در `domains/quran_root`.
6. سه Store (Evidence/Knowledge/Ontology) + Provenance DAG + log/index.
7. Monad Memory (پنج بخش).
8. Meta-Protocol (registry + current_stable + Pareto evaluation).
9. Harness و Benchmark شش‌بُعدی + red-team set برای «علم».
10. JSON Schemas هر مرحله/Store/RFC.
11. **اجرای کاملِ end-to-end:** `monad run quran-root علم` → Artifactها + سه Store + DAG +
    Memory + RFC + بردارِ benchmark، بدونِ دخالتِ انسان.

> **یادداشتِ scope:** این لایه‌ها در سطحِ معماری منجمد‌اند؛ v1 هرکدام را با **کمترین
> وفاداریِ واقعی** پیاده می‌کند که برای اجرای end-to-endِ «علم» کافی باشد (مثلاً Memory =
> یک append-logِ ساده؛ Meta-Protocol = registry با یک نسخهٔ Stable). نه بیشتر.

تا این چرخه روی یک ریشه کاملاً خودکار، قابل‌تکرار و قابل‌ارزیابی اجرا نشود، واردِ ریشهٔ
دوم نمی‌شویم.

---

## 17. سیاستِ Freeze

- معماری در **2026-06-26** منجمد شد.
- پس از Freeze، تا کشفِ موفقِ **سه Unit اول**، هیچ تغییرِ معماری مجاز نیست — فقط رفعِ باگ و
  جمع‌آوریِ داده.
- معیارِ پیشرفت دیگر تعدادِ اسناد نیست؛ اولین معیارِ موفقیت اجرای بی‌نقصِ
  `monad run quran-root علم` است.
- معماری باید خودش را در میدان اثبات کند.
