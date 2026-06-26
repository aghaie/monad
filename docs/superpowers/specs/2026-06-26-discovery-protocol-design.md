# Discovery Protocol v1 — طرحِ معماری (FROZEN)

> سندِ طراحیِ چرخهٔ اولِ موتورِ کشفِ مناد.
> وضعیت: **Frozen 2026-06-26**. پس از Freeze، تا کشفِ سه ریشهٔ اول هیچ تغییرِ
> معماری مجاز نیست — فقط رفعِ باگ و جمع‌آوریِ داده. «معماری باید خودش را در میدان
> اثبات کند، نه پشتِ میزِ طراحی.»
>
> این سندِ *طراحی* است. یکی از خروجی‌های پیاده‌سازی، سندِ نرماتیوِ
> `rfc/RFC-000001-discovery-protocol.md` خواهد بود که همین معماری را رسمی می‌کند.

---

## 0. هدف و قانون پروژه

موتوری بساز که **یک Unit** (در نمونهٔ اول: یک ریشهٔ قرآنی) را به‌صورت کاملاً
خودکار، بازتولیدپذیر و قابل‌ارزیابی، از substrate تا یک سندِ دانشِ کامل کشف کند.

> **قانون پروژه:** *First make one root discoverable. Then make all roots scalable.*
> تمرکزِ v1 مقیاس نیست؛ **اثباتِ معماری** است.

معماری از روزِ اول **مدل‌مستقل** و **دامنه‌مستقل** است: قرآن و ریشهٔ «علم» فقط
*نمونهٔ اول*‌اند، نه بخشی از موتور.

---

## 1. واژگانِ عمومی

| واژه | معنا | نمونهٔ اول |
|---|---|---|
| **Substrate** | مرجعِ تغییرناپذیر؛ منبعِ یگانهٔ حقیقت | `generated/monad.db` (قرآن حفص) |
| **Unit** | واحدِ تحتِ کشف | یک ریشه (root) |
| **Evidence** | مشاهدهٔ اتمیِ تغییرناپذیر از substrate، با id پایدار | یک token با مبدأ `S:A:W:T` |
| **Artifact** | خروجیِ منجمدِ یک مرحله (JSON) | `06_verify.json` |
| **Hypothesis** | ادعای ابطال‌پذیرِ مقیّد به شواهد که مدل پیشنهاد می‌دهد | — |
| **Knowledge** | فرضیه‌ای که از Verify عبور کرده؛ دارای دو نمایش | — |
| **Knowledge Store** | مرجعِ رسمیِ ماشین‌خوانِ همهٔ دانشِ تأییدشده | `store/` |
| **RFC** | نمای انسانی/ممیزیِ تولیدشده از Store | `rfc/<domain>/<unit>/…` |
| **DomainAdapter** | تنها جایی که کدِ مخصوصِ یک دامنه زندگی می‌کند | `domains/quran_root/` |
| **Worker** | مجریِ اکتشافیِ قابل‌تعویض (مدل) | `ClaudeWorker` |
| **Orchestrator** | کنترلِ جریانِ قطعی | `discovery/orchestrator.py` |

---

## 2. معماریِ لایه‌ای

| لایه | چه‌کسی | قانون |
|---|---|---|
| **Substrate** | `monad.db` | تغییرناپذیر (Constitution §14). منبعِ یگانه. |
| **Deterministic Layer** | اسکریپت‌های پایتون | ۱۰۰٪ بازتولیدپذیر (seed ثابت، بدون شبکه، بدون مدل). تنها لایه‌ای که Evidence و Knowledge تولید می‌کند. |
| **Discovery Layer** | Worker (مدل) | فقط **Hypothesis** تولید می‌کند. هرگز به DB دست نمی‌زند، هرگز Knowledge اعلام نمی‌کند. خروجیِ مدل همیشه فرضیه است، نه دانش. |
| **Orchestrator** | کنترلِ جریان | مراحلِ قطعی را خودکار اجرا می‌کند؛ در مراحلِ اکتشافی Worker را صدا می‌زند. |

### 2.1 Worker Interface (اصلِ مدل‌ناوابستگی)

```
Orchestrator  (قطعی، مالکِ کنترلِ جریان)
   │  هر مرحلهٔ اکتشافی → WorkerRequest(input_artifact, output_schema, prompt)
   ▼
Worker Interface  (قراردادِ منجمد: run(request) -> artifact)
   ├── ClaudeWorker      (v1 — اکنون)
   ├── GPTWorker         (v2)
   ├── GeminiWorker      (v3)
   ├── HumanWorker       (Debug / Gold — سقفِ کیفیت)
   └── LocalModelWorker  (آینده)
```

اگر فردا مدل عوض شود، فقط «مجریِ مرحله» عوض می‌شود، نه Orchestrator، نه schemaها،
نه پروتکل. مدل اولین عاملِ اجراست، نه هستهٔ مناد.

### 2.2 جریانِ کلانِ سیستم (اصلاحِ Δ4)

```
Substrate → Artifacts(1..8) → Verified Knowledge(Verify) → [Commit(9)] → Knowledge Store
                                                                              ├─→ RFC Generator → RFC   (نمای انسان/ممیزی)
                                                                              └─→ Builders             (آینده — مرجعِ ماشین)
```

- **Knowledge Store منبعِ رسمیِ ماشین است.** Builderها از آن تغذیه می‌شوند، نه از RFC.
- **RFC فقط Publication Layer است.** idempotent و قابلِ بازتولید از Store بدون اجرای مجددِ کشف.

---

## 3. اصولِ تغییرناپذیر (FROZEN INVARIANTS)

با گیت‌های اعتبارسنجیِ قطعی اجباری می‌شوند.

- **R1 — انحصارِ Verify:** هیچ مرحلهٔ اکتشافی حق ندارد `status` فرضیه را به `ACCEPTED`
  ببرد. تنها `verify.py` این انتقال را می‌نویسد.
- **R3 — خطی‌بودن و بوکس‌کردنِ مدل:**
  1. هیچ مرحله‌ای خروجیِ مرحلهٔ *آینده* را نمی‌خواند؛ ورودیِ اصلیِ هر مرحله آرتیفکتِ
     مرحلهٔ قبل است. اجرا کاملاً Replayable است (هشِ Substrate و KB در manifest قفل می‌شود).
  2. فقط مراحلِ **قطعی** (Extract, Verify, Graph, Commit) مجازند زمینِ منجمد
     (Substrate / Knowledge Store) را بخوانند — چون لازم است و چون تغییرناپذیر است.
  3. مراحلِ **اکتشافی** (Observe, Hypothesis, Attack, Reduce-propose) کاملاً بوکس‌اند:
     فقط آرتیفکتِ مرحلهٔ قبل. هرگز DB، هرگز KB، هرگز آینده.
- **P1 — Evidence Immutability:** هیچ آرتیفکتی Evidence را اضافه/حذف/تغییر نمی‌کند. همهٔ
  تبدیل‌ها فقط روی Metadata، Hypothesis و Knowledge انجام می‌شوند. (گیتِ CI هشِ آرایهٔ
  evidence را در طولِ مراحل diff می‌کند.)
- **P2 — Complete Provenance:** هر node دانش و هر میدانِ RFC باید از طریقِ DAG به ≥۱ node
  شواهد قابل‌پیمایش باشد. گزارهٔ بدونِ زنجیرهٔ معتبر → رد می‌شود.
- **P3 — Knowledge Never Overwrites:** دانش افزایشی است. تعارض → RFC/Knowledgeِ نو + یالِ
  تایپ‌دار (`Supersedes` / `Refines` / `Contradicts`)؛ نسخهٔ قبلی دست‌نخورده.

---

## 4. خطِ لولهٔ ۹ مرحله‌ای

ترتیبِ canonical:
`Extract → Cluster → Observe → Hypothesis → Attack → Verify → Reduce → Graph → Commit`

| # | مرحله | لایه | می‌خواند | تغذیهٔ بُعدِ benchmark |
|---|---|---|---|---|
| 1 | Extract | قطعی | Substrate | پایهٔ همه |
| 2 | Cluster | قطعی | مرحلهٔ ۱ | Compression |
| 3 | Observe | اکتشافی (بوکس) | مرحلهٔ ۲ | — |
| 4 | Hypothesis | اکتشافی (بوکس) | مرحلهٔ ۳ | Falsifiability |
| 5 | Attack | اکتشافی (بوکس) | مرحلهٔ ۴ | Falsifiability |
| 6 | Verify | **قطعی — دروازهٔ تولّدِ دانش** | مرحلهٔ ۵ + Substrate + KB | Recoverability, Reproducibility, Coherence |
| 7 | Reduce | اکتشافی پیشنهاد → قطعی می‌سنجد | مرحلهٔ ۶ | Compression |
| 8 | Graph | قطعی | مرحلهٔ ۷ + KB | Coherence, Predictive Power |
| 9 | Commit | قطعی | زنجیرهٔ منجمدِ ۶+۷+۸ | — |

### ماشینِ حالتِ فرضیه

```
PROPOSED ──(Attack: SURVIVES|WEAKENED|REFUTED، فقط مشورتی)──▶ (همچنان PROPOSED)
         ──(Verify فقط)──▶ ACCEPTED(+تیر اطمینان) | REJECTED | UNKNOWN
```

---

## 5. پاکتِ استانداردِ همهٔ آرتیفکت‌ها

```jsonc
{
  "envelope_version": "1.0",
  "stage": "verify", "stage_index": 6,
  "unit":      { "domain":"quran-root", "ref":"Elm", "display":"علم", "unit_id":42 },
  "substrate": { "id":"quran-hafs", "hash":"sha256:…" },
  "protocol_version": "0.1.0",
  "run_id": "<content-derived → بازتولیدپذیر>",
  "produced_by": {                       // دقیقاً یکی از دو حالت:
    "layer":"deterministic", "tool":"verify.py@<git_sha>"
    // یا "layer":"discovery","worker":"ClaudeWorker","worker_model":"…","worker_config_hash":"…"
  },
  "inputs": {
    "prev_artifact":"sha256:…",          // آرتیفکتِ مرحلهٔ قبل (همیشه)
    "substrate":"sha256:…",              // فقط مراحلِ قطعی
    "kb_snapshot":"sha256:…"             // فقط Verify و Graph
  },
  "produced_at":"<iso — فقط اطلاعاتی؛ در هشِ بازتولید دخیل نیست>",
  "payload": { … }
}
```

- **Evidence-id** = رشتهٔ مبدأشناسیِ آداپتر. در این دامنه: `S:A:W:T`.
- `run_id` محتوامحور است → بازتولیدپذیر. `produced_at` از هشِ هویتِ بازتولید حذف می‌شود.

---

## 6. Schemaی payload هر مرحله

### مرحلهٔ ۱ — EXTRACT [قطعی · Substrate] — پایهٔ Evidenceِ تغییرناپذیر
```jsonc
{ "evidence":[ { "evidence_id":"2:31:2:1", "locus":{"surah":2,"ayah":31,"word":2,"token":1},
                 "surface":"عَلَّمَ", "features":{…صرف، عیناً…}, "context_ref":"2:31" } ],
  "contexts":[ { "context_id":"2:31", "text":"…", "text_hash":"…" } ],
  "unit_stats":{ "evidence_count":…, "context_count":…, "first":…, "last":…, "subunits":[…lemmas…] } }
```

### مرحلهٔ ۲ — CLUSTER [قطعی · مرحلهٔ ۱]
```jsonc
{ "method":{ "algorithm":"…", "params":{…}, "seed":12345, "feature_space":[…] },
  "clusters":[ { "cluster_id":"c1", "members":["2:31:2:1",…], "profile":{…} } ],
  "patterns":[ { "pattern_id":"p1", "type":"cooccurrence", "with":"<ref>",
                 "lift":3.2, "null_p":0.004, "support":[…ev…] } ] }   // معناداری vs نولِ بسامد؛ بدون معنا
```

### مرحلهٔ ۳ — OBSERVE [اکتشافی · بوکس · مرحلهٔ ۲]
```jsonc
{ "observations":[ { "observation_id":"o1", "type":"description",
                     "statement":"…", "cites":["c1","p1","2:31:2:1"] } ] }  // هر مشاهده باید cite کند؛ بدون فرضیه
```

### مرحلهٔ ۴ — HYPOTHESIS [اکتشافی · بوکس · مرحلهٔ ۳]
```jsonc
{ "hypotheses":[ { "hypothesis_id":"h1", "status":"PROPOSED",
   "claim":"…گزارهٔ معناییِ ابطال‌پذیر…", "supported_by":["o1","c1"],
   "prediction":{ "predicate":"masked_recovery", "params":{…} } } ] }   // ≤۵؛ predicate از رجیستریِ پروتکل
```

### مرحلهٔ ۵ — ATTACK [اکتشافی · بوکس · مرحلهٔ ۴]
```jsonc
{ "attacks":[ { "hypothesis_id":"h1",
   "refutations":[ { "argument":"…", "counter_evidence":[…ev…] } ],
   "worker_verdict":"SURVIVES" } ] }   // مشورتی؛ status را تغییر نمی‌دهد
```

### مرحلهٔ ۶ — VERIFY [قطعی · دروازه · مرحلهٔ ۵ + Substrate + KB]
```jsonc
{ "verifications":[ { "hypothesis_id":"h1",
    "tests":{ "masked_recovery":{ "score":0.21,"baseline":0.02,"null_p":0.005,"passed":true },
              "two_half":{ "a":0.19,"b":0.20,"passed":true },
              "coherence":{ "conflicts":[], "passed":true } },
    "decision":"ACCEPTED", "confidence_tier":"قوی", "knowledge_id":"k1" } ] }
```
آستانه‌های تصمیم در پروتکل ثابت‌اند (مثلاً عبور از همهٔ آزمون‌های لازم + `null_p<0.05` →
`ACCEPTED`؛ تیر بر اساسِ اندازهٔ اثر). کاملاً قطعی.

### مرحلهٔ ۷ — REDUCE [اکتشافی پیشنهاد → قطعی می‌سنجد · مرحلهٔ ۶]
دو زیرـآرتیفکت، هرکدام تک‌لایه: `07a.propose` (discovery) → `07b.measure` (deterministic):
```jsonc
{ "proposed_definition":{ "statement":"…", "primitives":[…], "relations":[…] },   // از Worker
  "compression":{ "n_primitives":3, "coverage":0.95, "mdl_bits":…, "predicts_heldout":{"score":…,"passed":true} },
  "accepted_definition":{ "statement":"…", "primitives":[…], "covers_knowledge":["k1","k2"] } }  // فقط اگر گیتِ پوشش عبور کند
```

### مرحلهٔ ۸ — GRAPH [قطعی · مرحلهٔ ۷ + KB]
```jsonc
{ "links":[ { "to_unit":"<ref>", "relation":"co-defines"|"contrasts"|"specializes", "weight":…, "evidence":[…] } ],
  "network_coherence":{ "conflicts":[], "passed":true },
  "predictive_check":{ "applied_to":[…واحدهای held-outِ دیگر…], "hits":…, "score":… } }
```

### مرحلهٔ ۹ — COMMIT [قطعی · زنجیرهٔ ۶+۷+۸ → Knowledge Store]
گردآوریِ knowledge از Verify + definition از Reduce + links از Graph، به‌صورتِ
اشیاءِ دانشِ دونمایشی، و نوشتنِ آن‌ها به Knowledge Store + افزودنِ یال‌ها به DAG.

---

## 7. Knowledge — دو نمایش (Δ1)

هر Knowledge **دانش** است، نه متن. متن صرفاً یک نمایش است.

```jsonc
{ "knowledge_id":"k1", "unit":{…}, "protocol_version":"…", "run_id":"…",
  "status":"ACCEPTED",
  "formal_representation":{                       // مرجعِ ماشین
     "definition_primitives":[…],
     "relations":[ { "type":"contrasts", "to_unit":"<ref>" } ],
     "verified_by":[ { "predicate":"masked_recovery", "params":{…}, "score":0.21, "null_p":0.005 } ],
     "scope":{…}, "confidence_tier":"قوی" },
  "natural_explanation":"…توضیحِ انسانی…",          // فقط نمایش
  "provenance_nodes":[ "ev:2:31:2:1", "art:<run>/s6", "hyp:<run>/h1", "def:<run>" ],
  "relations_to_knowledge":[ { "type":"Refines", "target":"k_prev" } ] }   // P3
```

---

## 8. Predicate Registry — سطحِ پروتکل (Δ2)

پریدیکیت‌ها **جزوِ Discovery Protocol**‌اند، نه DomainAdapter. رجیستری، *قرارداد* را
تعریف می‌کند؛ DomainAdapter، *مجری* را پیاده می‌کند.

```jsonc
// discovery/predicates/registry.json — دامنه‌مستقل
{ "masked_recovery":       { "params_schema":{…}, "tests":"بازیابیِ unitِ ماسک‌شده از بافت", "pass":"score>baseline ∧ null_p<0.05" },
  "cooccurrence_constraint":{ "params_schema":{…}, "tests":"هم‌آییِ پایدارِ معنادار", "pass":"lift>τ ∧ null_p<0.05" },
  "morph_constraint":       { "params_schema":{…}, "tests":"قیدِ صرفیِ پایدار", "pass":"…" },
  "distributional_contrast":{ "params_schema":{…}, "tests":"تباینِ توزیعیِ دو خوشه", "pass":"…" },
  "two_half_stability":     { "params_schema":{…}, "tests":"تکرار روی دو نیمهٔ مستقل", "pass":"…" } }
```
```python
# domains/quran_root/adapter.py — تنها کدِ مخصوصِ قرآن
def execute_predicate(name, params) -> PredicateResult: ...   # روی monad.db
def extract(unit_ref) -> EvidenceBundle: ...
def evidence_id(locus) -> str: ...                            # "S:A:W:T"
def cluster_features(evidence) -> FeatureVectors: ...
```

---

## 9. Provenance DAG (Δ3)

به‌جای لیست، یک گرافِ جهت‌دارِ بدونِ دور (سراسری، در Knowledge Store).

- **Node** ∈ `{ evidence, artifact, observation, hypothesis, knowledge, definition }`
- **Edge** ∈ `{ cites, derived_from, supports, refutes, verifies, reduces_to, Supersedes, Refines, Contradicts }`

```jsonc
{ "nodes":[ {"id":"ev:2:31:2:1","type":"evidence"},
            {"id":"art:<run>/s6","type":"artifact"},
            {"id":"hyp:<run>/h1","type":"hypothesis"},
            {"id":"k1","type":"knowledge"} ],
  "edges":[ {"from":"hyp:<run>/h1","to":"ev:2:31:2:1","type":"cites"},
            {"from":"k1","to":"hyp:<run>/h1","type":"verifies"},
            {"from":"k1","to":"art:<run>/s6","type":"derived_from"},
            {"from":"k1","to":"k_prev","type":"Refines"} ] }
```
**P2** = هر node دانش باید مسیری به ≥۱ node شواهد داشته باشد. کلِ تاریخِ کشف پیمایش‌پذیر و
قابلِ تحلیلِ وابستگی است.

---

## 10. Knowledge Store — مرجعِ رسمیِ ماشین (Δ4)

```
store/
  log/                     # append-only؛ رویدادهای commitِ دانش (JSONL، تغییرناپذیر) — منبعِ حقیقت
  knowledge.db             # ایندکسِ SQLite، قابلِ بازسازیِ قطعی از log
  provenance/graph.json    # گرافِ provenance سراسری (افزایشی)
  registry.json            # units → knowledge → RFCs + گرافِ supersedes/refines/contradicts
  rebuild_index.py         # log → knowledge.db (بازتولیدپذیر)
```
- **log** منبعِ حقیقتِ تغییرناپذیر است؛ **knowledge.db** صرفاً ایندکسِ پرس‌وجو، از log
  بازسازی‌پذیر.
- Builderها از Store می‌خوانند. RFC Generator هم از Store می‌خواند.

---

## 11. Schemaی رسمیِ RFC (نمای انسان/ممیزی)

```jsonc
{ "rfc_id":"RFC-quran-root-Elm-v0.1.0-<run_id>",   // تغییرناپذیر، یکتا
  "unit":{…}, "substrate":{…}, "protocol_version":"0.1.0", "run_id":"…", "produced_at":"…",
  "status":"ACCEPTED"|"SUPERSEDED",
  "supersedes":"<rfc_id|null>", "relation_to_prior":"Supersedes"|"Refines"|"Contradicts"|null,   // P3
  "definition":{ …accepted_definition از Reduce… },
  "knowledge":[ { "knowledge_id":"k1",
                  "formal_representation":{…}, "natural_explanation":"…",
                  "confidence_tier":"قوی", "provenance_nodes":[…] } ],
  "fields":{
    "evidence":     { ev_ids + نحوهٔ نمونه‌گیری },
    "reasoning":    { زنجیرهٔ cluster→observe→hypothesis→attack→verify برای هر knowledge },
    "confidence":   { تیرِ هر knowledge + کلی },
    "scope":        { کجا/کِی برقرار است — contextها، subunitها },
    "limitations":  { آنچه بازیابی نشد، UNKNOWNها، خودداری‌ها },
    "relationships":{ لینک‌های گراف + روابط با RFCهای دیگر },
    "history":      { protocol_version، زنجیرهٔ supersedes }
  },
  "benchmark_score":{ بردارِ شش‌بُعدیِ همین run },
  "hashes":{ substrate, kb_snapshot, هر ۹ آرتیفکت } }
```
**P2** با گیتِ `validate_provenance.py` پیش از نوشتنِ RFC اجباری می‌شود.
هفت میدانِ `fields` همان هفت میدانِ Constitution §۶ است.

---

## 12. Harnessِ شش‌بُعدیِ Benchmark (TDD)

`discovery/benchmark/score_run.py <run_dir> → بردار`. هر بُعد تابعِ خالصِ آرتیفکت‌های
منجمد است؛ دامنه‌مستقل.

| بُعد | تعریفِ عملیاتی (۰..۱) | منبع |
|---|---|---|
| **Recoverability** | بازیابیِ ماسک‌شدهٔ `accepted_definition` روی Evidenceِ held-out، نرمال با baseline | Verify/Reduce |
| **Reproducibility** | Jaccardِ `knowledge_id`های ACCEPTED در N اجرای مستقل (همان substrate+worker_config) | N-run |
| **Falsifiability** | نسبتِ فرضیه‌های known-false از red-team که درست `REJECTED` شدند | redteam set |
| **Compression** | `coverage / n_primitives` نرمال‌شده (نسبتِ MDL) | Reduce |
| **Coherence** | `1 − conflicts/checks` در برابرِ KB | Verify+Graph |
| **Predictive Power** | دقتِ اعمالِ پریدیکیت‌ها روی واحدهای held-outِ دیگر | Graph |

- **قاعدهٔ پذیرش (پارتو):** `v_new` جایگزینِ `v_old` می‌شود **اگروفقط‌اگر** روی هر ۶ بُعد
  `≥` و دستِ‌کم روی یکی `>` باشد — روی مجموعهٔ benchmarkِ منجمد (v1 = `{علم}`). هیچ بُعدی
  قربانیِ بُعدِ دیگر نمی‌شود.
- **دفترچهٔ TDD:** `discovery/benchmark/ledger/<protocol_version>.json` — هر بُعد ثبت می‌شود.
- **red-team:** `discovery/benchmark/redteam/<unit_ref>.json` — فرضیه‌های known-false که
  پروتکل باید ردشان کند (تزریق در مرحلهٔ ۴).

---

## 13. ساختار پوشه‌ها

```
rfc/
  RFC-000001-discovery-protocol.md          # سندِ نرماتیوِ پروتکل (deliverable)
  generator.py                              # RFC Generator: Store → RFC (idempotent)
  registry.json                             # ایندکسِ RFCها + گرافِ supersedes
  <domain>/<unit_ref>/RFC-…-v<ver>-<run>.{md,json}  +  manifest.json   # snapshotِ تغییرناپذیر
discovery/                                  # موتورِ عمومی — هیچ کدِ قرآنی اینجا نیست
  orchestrator.py                           # کنترلِ جریانِ قطعی (run_unit)
  stages/        extract · cluster · verify · reduce_measure · graph · commit   # قطعی
  workers/       worker_interface.py · claude_worker.py · human_worker.py
  prompts/       observe · hypothesis · attack · reduce        # متنِ worker-مستقل
  predicates/    registry.json (+ executor contracts)          # سطحِ پروتکل، دامنه‌مستقل
  schemas/       envelope + ۹ مرحله + knowledge + rfc          # JSON Schema
  benchmark/     score_run.py · ledger/ · redteam/ · units.json
  runs/<domain>/<unit_ref>/<run_id>/        # ۹ آرتیفکتِ هر اجرا
store/                                      # مرجعِ رسمیِ ماشین (Δ4)
  log/ · knowledge.db · provenance/graph.json · registry.json · rebuild_index.py
domains/
  quran_root/adapter.py                     # تنها کدِ مخصوصِ قرآن: extract، ev-id، featureها، مجریِ پریدیکیت‌ها
.claude/skills/discover-one-unit/SKILL.md   # Skill-0001 = اتصالِ ClaudeWorker به Worker Interface
```

---

## 14. Deliverables چرخهٔ اول

1. `rfc/RFC-000001-discovery-protocol.md` — سندِ نرماتیوِ پروتکل.
2. `Skill-0001` (Discover One Unit) — اتصالِ ClaudeWorker.
3. تمام اسکریپت‌های لایهٔ قطعی (stages 1,2,6,7b,8,9 + generator + validators).
4. Worker Interface + ClaudeWorker + HumanWorker.
5. Predicate Registry + مجریِ آن در `domains/quran_root`.
6. Knowledge Store + Provenance DAG.
7. Harness و Benchmark شش‌بُعدی + red-team set برای «علم».
8. فرمتِ استانداردِ خروجیِ هر مرحله (JSON Schemas).
9. **اجرای کاملِ end-to-end روی ریشهٔ «علم» → یک RFC + ورودیِ Knowledge Store + بردارِ benchmark.**

تا این چرخه روی یک ریشه کاملاً خودکار، قابل‌تکرار و قابل‌ارزیابی اجرا نشود، واردِ ریشهٔ
دوم نمی‌شویم.

---

## 15. سیاستِ Freeze

- معماری در **2026-06-26** منجمد شد.
- پس از Freeze، تا کشفِ **سه ریشهٔ اول**، هیچ تغییرِ معماری مجاز نیست — فقط رفعِ باگ و
  جمع‌آوریِ داده.
- معماری باید خودش را در میدان اثبات کند.
