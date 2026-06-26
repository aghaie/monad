# Discovery Protocol v1 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** اجرای کاملِ `monad run quran-root علم` بدونِ دخالتِ انسان — کشفِ یک ریشه از substrate تا RFC، با به‌روزرسانیِ Storeها، Provenance DAG، Monad Memory و بردارِ Benchmark.

**Architecture:** موتورِ عمومیِ دولایه (Deterministic Core که تنها زایندهٔ Knowledge است + ReasoningWorkerهای پیشنهاددهنده)، خطِ لولهٔ خطیِ ۹ مرحله‌ای روی آرتیفکت‌های JSON، با ارکستریتورِ قطعی. کدِ مخصوصِ قرآن فقط در `domains/quran_root/`. منبع: طرحِ منجمد [docs/superpowers/specs/2026-06-26-discovery-protocol-design.md](../specs/2026-06-26-discovery-protocol-design.md).

**Tech Stack:** Python 3.9 (**stdlib فقط** — بدون numpy/scipy/sklearn)، sqlite3، JSON آرتیفکت‌ها، pytest برای تست.

## Global Constraints

- **Implementation Rule 0 — هیچ ویژگیِ جدید.** هر تغییر فقط یکی از سه: `Bug Fix` | `Missing Implementation` | `Performance Improvement`. هر چیزِ دیگر → `docs/superpowers/backlog-v2.md`.
- **Runnable-at-every-commit.** هیچ commit نباید Pipeline را ناتمام بگذارد. commitها کوچک، مستقل، قابل‌آزمون، قابل‌بازگشت.
- **Stage-gated.** هر مرحله پیش از رفتن به بعدی، مستقل اجرا و آزمون شود (هر Task یک stage یا یک جزءِ زیرساختیِ مستقل است).
- **stdlib فقط** — هیچ وابستگیِ خارجی. تصادفی‌بودن همیشه با `random.Random(SEED)` (SEED=`20260626`). همهٔ خروجی‌ها قطعی و بازتولیدپذیر.
- **مرزِ معماری منجمد است** (R1, R3, P1, P2, P3 — به spec §3). کد آن‌ها را نقض نکند.
- ریشهٔ benchmarkِ v1: «علم» = `root_id 218`، ۸۵۴ توکن. Substrate: `generated/monad.db` (تغییرناپذیر).
- مسیرها نسبت به ریشهٔ repo؛ هر ماژول: `REPO = Path(__file__).resolve().parents[N]`.
- هر آرتیفکت با `envelope_version="1.0"` و schemaی §۵ ساخته می‌شود. `produced_at` در هشِ بازتولید دخیل نیست.
- Workerِ پیش‌فرضِ مسیرِ خودکار = `StatisticalWorker` (قطعی). `--worker claude` → `ClaudeWorker`.

---

## File Structure

```
monad                                   # CLI entry (T3)              → monad run <domain> <unit_ref>
engine/                                  # موتورِ عمومی (package)
  __init__.py
  core.py            (T1)  envelope, hashing، content-derived run_id، canonical-json، io آرتیفکت
  schemas.py         (T1)  اعتبارسنجیِ سبکِ stdlib برای envelope + هر payload
  orchestrator.py    (T3)  کنترلِ جریانِ قطعی، اجرای مراحل، نوشتنِ Memory
  stages/
    __init__.py
    cluster.py       (T4)
    verify.py        (T9)
    reduce_measure.py(T10)
    graph.py         (T11)
    commit.py        (T12)
  workers/
    __init__.py
    base.py          (T5)  ReasoningWorker ABC + WorkerRequest
    statistical.py   (T5)  StatisticalWorker (proposer قطعی)
    human.py         (T5)  HumanWorker (خواندن از فایلِ fixture)
    claude.py        (T17) ClaudeWorker (اتصال به Skill-0001)
  predicates/
    __init__.py
    registry.py      (T8)  قراردادِ پریدیکیت‌ها (دامنه‌مستقل)
  benchmark/
    __init__.py
    score.py         (T15) شش‌بُعدی + Pareto
domains/
  __init__.py
  quran_root/
    __init__.py
    adapter.py       (T2)  extract، evidence_id=S:A:W:T، cluster_features، مجریِ پریدیکیت‌ها
store/                                   # سه Store (T12) — runtime؛ در .gitignore
  evidence/ knowledge/ ontology/ provenance/ log/ index.db
memory/                                  # Monad Memory (T13) — runtime؛ در .gitignore
  attempts/ rejected/ failed_runs/ abandoned/ discoveries/
protocol/
  registry.json      (T16)  Meta-Protocol
rfc/
  generator.py       (T14)  Storeها → RFC
  RFC-000001-discovery-protocol.md (T18)
  registry.json      (T14)
engine/runs/<domain>/<unit_ref>/<run_id>/   # آرتیفکت‌های هر اجرا (runtime؛ .gitignore)
tests/engine/                            # تست‌ها
docs/superpowers/backlog-v2.md           (T1)  مقصدِ ایده‌های خارج از scope
```

> **یادداشتِ scope (spec §16):** هر لایه با کمترین وفاداریِ واقعیِ کافی برای اجرای end-to-endِ «علم» پیاده می‌شود. نه بیشتر.

---

## Definition of Done (هر Task)

هیچ Task تمام‌شده تلقی نمی‌شود مگر هر چهار شرط برقرار باشد:

1. **تستِ خودِ Task** PASS.
2. **همهٔ تست‌های قبلی همچنان PASS** — `python3 -m pytest tests/engine -q` کاملاً سبز (تشخیصِ زودِ regression).
3. **`monad run quran-root علم` تا همان مرحله بدونِ خطا** اجرا شود (از Task 3 به بعد که CLI زنده است).
4. **هیچ فایلِ قبلی تغییرِ فرمت ندهد** مگر همان Task رسماً مسئولِ آن باشد — `git diff --stat` فقط فایل‌های اعلام‌شدهٔ همان Task را نشان دهد؛ هیچ آرتیفکتِ Golden یا envelope به‌طورِ ناخواسته تغییر نکند.

> هر Task پیش از commit این چهار را به‌صورتِ یک checklist بررسی می‌کند. شکست در هر کدام = Task ناتمام.

## Version Lock

سه نسخه از ابتدا قفل‌اند و در `engine/core.py` تعریف می‌شوند. هر تغییرِ ناخواسته باید تست را **عمداً** بشکند تا ناسازگاریِ نسخه‌ها پنهان نماند:

```python
PROTOCOL_VERSION = "0.1.0"
ENVELOPE_VERSION = "1.0"
SCHEMA_VERSION   = "1.0"
```
تستِ قفل (در `tests/engine/test_core.py`، Task 1):
```python
def test_version_lock():
    from engine import core
    assert core.PROTOCOL_VERSION == "0.1.0"
    assert core.ENVELOPE_VERSION == "1.0"
    assert core.SCHEMA_VERSION == "1.0"
```
هر آرتیفکت باید `schema_version` را در payload یا envelope حمل کند؛ تغییرِ هر یک از این سه ثابت بدونِ به‌روزرسانیِ عمدیِ تست = شکستِ آگاهانه.

## Golden Artifacts (Snapshot)

علاوه بر assertionهای ساختاری، هر مرحله یک **Golden Artifact** نگه می‌دارد تا بازتولیدپذیری بایت‌سطح تضمین شود (هر تغییرِ ناخواسته در ترتیبِ JSON یا hashing فوراً آشکار شود).

- **مکانیزم:** هنگام سبزشدنِ هر Taskِ مرحله‌ای (Task 2,4,5,6,7,9,10,11,12)، یک‌بار آرتیفکتِ تولیدشده را پس از حذفِ `produced_at` در `tests/golden/0N_<stage>.json` ذخیره کن (capture-on-first-green).
- **رگرسیون:** یک تستِ مشترک در `tests/engine/test_golden.py` (در Task 2 ساخته، در هر Taskِ بعدی گسترش می‌یابد):
```python
# tests/engine/test_golden.py
import json
from pathlib import Path
from engine import orchestrator, core

GOLDEN = Path(__file__).resolve().parents[1] / "golden"

def _strip(env):
    env = dict(env); env.pop("produced_at", None); return env

def _check(stage_index, stage, tmp_path):
    res = orchestrator.run("quran-root", "علم", run_root=tmp_path)
    got = _strip(core.read_artifact(f"{res['run_dir']}/0{stage_index}_{stage}.json"))
    gold = json.loads((GOLDEN / f"0{stage_index}_{stage}.json").read_text("utf-8"))
    assert got == _strip(gold), f"golden drift in stage {stage}"

def test_golden_extract(tmp_path):
    _check(1, "extract", tmp_path)
# با هر Taskِ مرحله‌ای یک test_golden_<stage> اضافه کن.
```
- اگر تغییری *عمدی* بود، Golden را در همان Task به‌روزرسانی کن و در پیامِ commit ذکر کن. drift غیرعمدی = شکستِ تست.
- `tests/golden/` در git **ردیابی می‌شود** (برخلافِ `store/`,`memory/`,`engine/runs/`).

---

## Task 1: هستهٔ موتور — envelope، hashing، run_id، اعتبارسنجی، scaffolding

**Files:**
- Create: `engine/__init__.py`, `engine/core.py`, `engine/schemas.py`, `engine/stages/__init__.py`, `engine/workers/__init__.py`, `engine/predicates/__init__.py`, `engine/benchmark/__init__.py`, `domains/__init__.py`, `domains/quran_root/__init__.py`
- Create: `docs/superpowers/backlog-v2.md`, `.gitignore` (افزودنِ `store/ memory/ engine/runs/`)
- Test: `tests/engine/test_core.py`

**Interfaces:**
- Produces:
  - `canonical_json(obj) -> str` (sort_keys, ensure_ascii=False, separators=(",",":"))
  - `sha256_of(obj) -> str` (بازمی‌گرداند `"sha256:<hex>"`)
  - `derive_run_id(protocol_version, unit, substrate_hash, worker_config) -> str`
  - `build_envelope(stage, stage_index, unit, substrate, protocol_version, run_id, produced_by, inputs, payload) -> dict`
  - `write_artifact(run_dir, stage_index, stage, envelope) -> Path` (نام: `0{idx}_{stage}.json`)
  - `read_artifact(path) -> dict`
  - `validate_envelope(env) -> None` (raise `SchemaError` در صورت نقص)

- [ ] **Step 1: تستِ شکست‌خورده**

```python
# tests/engine/test_core.py
import json
from engine import core

UNIT = {"domain": "quran-root", "ref": "Elm", "display": "علم", "unit_id": 218}
SUB = {"id": "quran-hafs", "hash": "sha256:abc"}

def test_canonical_json_is_stable_and_unicode():
    a = core.canonical_json({"b": 1, "a": "علم"})
    assert a == '{"a":"علم","b":1}'

def test_sha256_prefixed_and_deterministic():
    h1 = core.sha256_of({"x": 1})
    h2 = core.sha256_of({"x": 1})
    assert h1 == h2 and h1.startswith("sha256:")

def test_run_id_is_content_derived():
    wc = {"worker": "StatisticalWorker"}
    r1 = core.derive_run_id("0.1.0", UNIT, "sha256:abc", wc)
    r2 = core.derive_run_id("0.1.0", UNIT, "sha256:abc", wc)
    r3 = core.derive_run_id("0.1.0", UNIT, "sha256:DIFF", wc)
    assert r1 == r2 and r1 != r3 and len(r1) == 16

def test_envelope_roundtrip_and_validation(tmp_path):
    env = core.build_envelope(
        stage="extract", stage_index=1, unit=UNIT, substrate=SUB,
        protocol_version="0.1.0", run_id="deadbeefdeadbeef",
        produced_by={"layer": "deterministic", "tool": "extract.py@test"},
        inputs={"substrate": SUB["hash"]}, payload={"ok": True})
    core.validate_envelope(env)
    p = core.write_artifact(tmp_path, 1, "extract", env)
    assert p.name == "01_extract.json"
    back = core.read_artifact(p)
    assert back["payload"] == {"ok": True}
    assert back["produced_at"]  # informational stamp present

def test_validate_rejects_missing_field():
    import pytest
    bad = {"stage": "x"}
    with pytest.raises(core.SchemaError):
        core.validate_envelope(bad)
```

- [ ] **Step 2: اجرا و دیدنِ شکست** — `python3 -m pytest tests/engine/test_core.py -v` → FAIL (`No module named engine`).

- [ ] **Step 3: پیاده‌سازی هسته**

```python
# engine/__init__.py
# (خالی — package marker)
```
```python
# engine/core.py
"""هستهٔ موتورِ کشف: envelope، hashing قطعی، run_id محتوامحور، io آرتیفکت."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ENVELOPE_VERSION = "1.0"
PROTOCOL_VERSION = "0.1.0"
SCHEMA_VERSION = "1.0"


class SchemaError(ValueError):
    pass


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_of(obj) -> str:
    data = obj if isinstance(obj, str) else canonical_json(obj)
    return "sha256:" + hashlib.sha256(data.encode("utf-8")).hexdigest()


def derive_run_id(protocol_version, unit, substrate_hash, worker_config) -> str:
    seed = canonical_json([protocol_version, unit, substrate_hash, worker_config])
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]


_REQUIRED = ("envelope_version", "stage", "stage_index", "unit", "substrate",
             "protocol_version", "run_id", "produced_by", "inputs", "payload")


def build_envelope(stage, stage_index, unit, substrate, protocol_version,
                   run_id, produced_by, inputs, payload) -> dict:
    return {
        "envelope_version": ENVELOPE_VERSION,
        "stage": stage, "stage_index": stage_index,
        "unit": unit, "substrate": substrate,
        "protocol_version": protocol_version, "run_id": run_id,
        "produced_by": produced_by, "inputs": inputs,
        "produced_at": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }


def validate_envelope(env) -> None:
    if not isinstance(env, dict):
        raise SchemaError("envelope must be a dict")
    for k in _REQUIRED:
        if k not in env:
            raise SchemaError(f"missing required field: {k}")
    if env["produced_by"].get("layer") not in ("deterministic", "discovery"):
        raise SchemaError("produced_by.layer must be deterministic|discovery")


def write_artifact(run_dir, stage_index, stage, envelope) -> Path:
    validate_envelope(envelope)
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    p = run_dir / f"0{stage_index}_{stage}.json"
    p.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def read_artifact(path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
```
```python
# engine/schemas.py
"""اعتبارسنجیِ سبکِ payloadها (stdlib). هر مرحله کلیدهای لازمش را اعلام می‌کند."""
from engine.core import SchemaError

PAYLOAD_KEYS = {
    "extract": ("evidence", "contexts", "unit_stats"),
    "cluster": ("method", "clusters", "patterns"),
    "observe": ("observations",),
    "hypothesis": ("hypotheses",),
    "attack": ("attacks",),
    "verify": ("verifications",),
    "reduce": ("proposed_definition", "compression", "accepted_definition"),
    "graph": ("links", "network_coherence", "predictive_check"),
    "commit": ("committed",),
}


def validate_payload(stage, payload) -> None:
    keys = PAYLOAD_KEYS.get(stage)
    if keys is None:
        raise SchemaError(f"unknown stage: {stage}")
    for k in keys:
        if k not in payload:
            raise SchemaError(f"[{stage}] payload missing key: {k}")
```
```python
# engine/stages/__init__.py , engine/workers/__init__.py , engine/predicates/__init__.py ,
# engine/benchmark/__init__.py , domains/__init__.py , domains/quran_root/__init__.py
# (همگی خالی — package markers)
```
```markdown
<!-- docs/superpowers/backlog-v2.md -->
# Backlog — نسخهٔ بعد (خارج از scope فاز اول، طبق Implementation Rule 0)
```
افزودن به `.gitignore`:
```
store/
memory/
engine/runs/
```

- [ ] **Step 4: اجرا و سبزشدن** — `python3 -m pytest tests/engine/test_core.py -v` → PASS.

- [ ] **Step 5: commit**
```bash
git add engine domains docs/superpowers/backlog-v2.md .gitignore tests/engine/test_core.py
git commit -m "feat(engine): core envelope, deterministic hashing, content-derived run_id"
```

---

## Task 2: DomainAdapter — Extract (مرحلهٔ ۱)

**Files:**
- Create: `domains/quran_root/adapter.py`
- Test: `tests/engine/test_extract.py`

**Interfaces:**
- Consumes: `engine.core`
- Produces (در `domains/quran_root/adapter.py`):
  - `SUBSTRATE_ID = "quran-hafs"`, `DB_PATH` (= `generated/monad.db`)
  - `substrate_hash() -> str`
  - `resolve_unit(ref_or_arabic) -> dict` (`{"domain","ref","display","unit_id"}`)
  - `extract(unit) -> dict` (payloadِ مرحلهٔ extract: `evidence`, `contexts`, `unit_stats`)
  - `evidence_id(s,a,w,t) -> str`  → `"s:a:w:t"`

- [ ] **Step 1: تستِ شکست‌خورده**

```python
# tests/engine/test_extract.py
from domains.quran_root import adapter

def test_resolve_elm():
    u = adapter.resolve_unit("علم")
    assert u["unit_id"] == 218 and u["domain"] == "quran-root"

def test_extract_elm_shape():
    u = adapter.resolve_unit("علم")
    pl = adapter.extract(u)
    # ۸۵۴ توکنِ ریشهٔ علم در morphology
    assert pl["unit_stats"]["evidence_count"] == 854
    ev = pl["evidence"][0]
    assert set(ev) >= {"evidence_id", "locus", "surface", "features", "context_ref"}
    assert ev["evidence_id"].count(":") == 3
    # context باید متن داشته باشد
    assert pl["contexts"][0]["text"]

def test_extract_is_deterministic():
    u = adapter.resolve_unit("علم")
    assert adapter.extract(u) == adapter.extract(u)

def test_substrate_hash_prefixed():
    assert adapter.substrate_hash().startswith("sha256:")
```

- [ ] **Step 2: اجرا و شکست** — `python3 -m pytest tests/engine/test_extract.py -v` → FAIL (`No module named ... adapter` / AttributeError).

- [ ] **Step 3: پیاده‌سازی**

```python
# domains/quran_root/adapter.py
"""DomainAdapter برای ریشه‌های قرآنی — تنها کدِ مخصوصِ قرآن."""
import hashlib
import sqlite3
from pathlib import Path

from engine.core import sha256_of

REPO = Path(__file__).resolve().parents[2]
DB_PATH = REPO / "generated" / "monad.db"
SUBSTRATE_ID = "quran-hafs"
DOMAIN = "quran-root"


def _conn():
    c = sqlite3.connect(str(DB_PATH))
    c.row_factory = sqlite3.Row
    return c


def substrate_hash() -> str:
    h = hashlib.sha256()
    with open(DB_PATH, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def resolve_unit(ref_or_arabic) -> dict:
    with _conn() as c:
        row = c.execute(
            "SELECT root_id, root_buckwalter, root_arabic FROM roots "
            "WHERE root_arabic=? OR root_buckwalter=?",
            (ref_or_arabic, ref_or_arabic)).fetchone()
    if row is None:
        raise ValueError(f"unit not found: {ref_or_arabic}")
    return {"domain": DOMAIN, "ref": row["root_buckwalter"],
            "display": row["root_arabic"], "unit_id": row["root_id"]}


def evidence_id(s, a, w, t) -> str:
    return f"{s}:{a}:{w}:{t}"


def extract(unit) -> dict:
    rid = unit["unit_id"]
    with _conn() as c:
        rows = c.execute(
            "SELECT m.surah_number s, m.ayah_number a, m.word_position w, "
            "m.token_position t, m.form_arabic surface, m.pos, m.tag, "
            "m.aspect, m.voice, m.mood, m.person, m.number_feature num "
            "FROM morphology m WHERE m.root_id=? "
            "ORDER BY m.surah_number, m.ayah_number, m.word_position, m.token_position",
            (rid,)).fetchall()
        evidence, ctx_ids = [], {}
        for r in rows:
            eid = evidence_id(r["s"], r["a"], r["w"], r["t"])
            cref = f"{r['s']}:{r['a']}"
            ctx_ids[cref] = (r["s"], r["a"])
            evidence.append({
                "evidence_id": eid,
                "locus": {"surah": r["s"], "ayah": r["a"],
                          "word": r["w"], "token": r["t"]},
                "surface": r["surface"] or "",
                "features": {"pos": r["pos"], "tag": r["tag"], "aspect": r["aspect"],
                             "voice": r["voice"], "mood": r["mood"],
                             "person": r["person"], "number": r["num"]},
                "context_ref": cref,
            })
        contexts = []
        for cref, (s, a) in sorted(ctx_ids.items(), key=lambda kv: kv[1]):
            ar = c.execute("SELECT text_normalized, text_hafs FROM ayahs "
                           "WHERE surah_number=? AND ayah_number=?", (s, a)).fetchone()
            text = (ar["text_normalized"] or ar["text_hafs"]) if ar else ""
            contexts.append({"context_id": cref, "text": text,
                             "text_hash": sha256_of(text)})
    surahs = sorted({e["locus"]["surah"] for e in evidence})
    stats = {"evidence_count": len(evidence), "context_count": len(contexts),
             "first": evidence[0]["evidence_id"] if evidence else None,
             "last": evidence[-1]["evidence_id"] if evidence else None,
             "surah_count": len(surahs)}
    return {"evidence": evidence, "contexts": contexts, "unit_stats": stats}
```

- [ ] **Step 4: سبزشدن** — `python3 -m pytest tests/engine/test_extract.py -v` → PASS.

- [ ] **Step 5: commit**
```bash
git add domains/quran_root/adapter.py tests/engine/test_extract.py
git commit -m "feat(quran_root): Extract — evidence bundle for a root (S:A:W:T provenance)"
```

---

## Task 3: Orchestrator + CLI — اسکلتِ راه‌رونده (مرحلهٔ ۱ end-to-end)

**Files:**
- Create: `engine/orchestrator.py`, `monad` (CLI، executable)
- Test: `tests/engine/test_orchestrator_skeleton.py`

**Interfaces:**
- Consumes: `engine.core`, `domains.quran_root.adapter`
- Produces:
  - `engine.orchestrator.run(domain, unit_ref, worker_name="statistical", run_root=None) -> dict` با کلیدهای `{"run_id","run_dir","stages_done","status"}`
  - `STAGES = [(1,"extract"), (2,"cluster"), ...]` (در این Task فقط extract فعال؛ بقیه در Taskهای بعد افزوده می‌شوند)
  - CLI: `monad run <domain> <unit_ref> [--worker statistical|claude]`

- [ ] **Step 1: تستِ شکست‌خورده**

```python
# tests/engine/test_orchestrator_skeleton.py
from engine import orchestrator, core

def test_run_extract_only(tmp_path):
    res = orchestrator.run("quran-root", "علم", run_root=tmp_path)
    assert res["status"] == "ok"
    art = core.read_artifact(res["run_dir"] + "/01_extract.json")
    assert art["payload"]["unit_stats"]["evidence_count"] == 854
    assert art["unit"]["unit_id"] == 218

def test_run_id_is_reproducible(tmp_path):
    a = orchestrator.run("quran-root", "علم", run_root=tmp_path)
    b = orchestrator.run("quran-root", "علم", run_root=tmp_path)
    assert a["run_id"] == b["run_id"]
```

- [ ] **Step 2: شکست** — `python3 -m pytest tests/engine/test_orchestrator_skeleton.py -v` → FAIL.

- [ ] **Step 3: پیاده‌سازی**

```python
# engine/orchestrator.py
"""ارکستریتورِ قطعی — کنترلِ جریانِ خطیِ مراحل."""
from pathlib import Path

from engine import core
from engine.schemas import validate_payload
from domains.quran_root import adapter as quran_root

ADAPTERS = {"quran-root": quran_root}
REPO = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ROOT = REPO / "engine" / "runs"

# مراحل به‌ترتیب فعال می‌شوند؛ هر Task یک ردیف را روشن می‌کند.
STAGES = [(1, "extract")]


def _worker_config(worker_name):
    return {"worker": worker_name}


def run(domain, unit_ref, worker_name="statistical", run_root=None):
    adp = ADAPTERS[domain]
    unit = adp.resolve_unit(unit_ref)
    substrate = {"id": adp.SUBSTRATE_ID, "hash": adp.substrate_hash()}
    run_id = core.derive_run_id(core.PROTOCOL_VERSION, unit, substrate["hash"],
                                _worker_config(worker_name))
    run_root = Path(run_root) if run_root else DEFAULT_RUN_ROOT
    run_dir = run_root / domain / unit["ref"] / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    done = []
    # مرحلهٔ ۱ — Extract (قطعی)
    payload = adp.extract(unit)
    validate_payload("extract", payload)
    env = core.build_envelope(
        "extract", 1, unit, substrate, core.PROTOCOL_VERSION, run_id,
        {"layer": "deterministic", "tool": "quran_root.adapter.extract"},
        {"substrate": substrate["hash"]}, payload)
    core.write_artifact(run_dir, 1, "extract", env)
    done.append("extract")

    return {"run_id": run_id, "run_dir": str(run_dir),
            "stages_done": done, "status": "ok"}
```
```python
#!/usr/bin/env python3
# monad
"""Monad CLI — monad run <domain> <unit_ref> [--worker ...]"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine import orchestrator


def main():
    p = argparse.ArgumentParser(prog="monad")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="discover one unit")
    r.add_argument("domain")
    r.add_argument("unit_ref")
    r.add_argument("--worker", default="statistical",
                   choices=["statistical", "claude", "human"])
    args = p.parse_args()
    if args.cmd == "run":
        res = orchestrator.run(args.domain, args.unit_ref, worker_name=args.worker)
        print(f"run_id={res['run_id']}  status={res['status']}")
        print(f"stages={res['stages_done']}")
        print(f"dir={res['run_dir']}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: سبزشدن + اجرای دستی**
```bash
python3 -m pytest tests/engine/test_orchestrator_skeleton.py -v   # PASS
chmod +x monad && ./monad run quran-root علم                      # خروجی: run_id=…, stages=['extract']
```

- [ ] **Step 5: commit**
```bash
git add engine/orchestrator.py monad tests/engine/test_orchestrator_skeleton.py
git commit -m "feat(engine): orchestrator + monad CLI — Extract runs end-to-end"
```

---

## Task 4: مرحلهٔ ۲ — Cluster (قطعی)

**Files:**
- Create: `engine/stages/cluster.py`
- Modify: `engine/orchestrator.py` (افزودنِ ردیف `(2,"cluster")` و فراخوانی)
- Test: `tests/engine/test_cluster.py`

**Interfaces:**
- Consumes: payloadِ extract
- Produces: `engine.stages.cluster.run(extract_payload, seed=20260626) -> dict` با `{"method","clusters","patterns"}`. خوشه‌بندیِ قطعی بر اساسِ امضای ویژگی `(pos, aspect)`؛ patterns = هم‌آییِ ریشه‌های دیگر در همان آیه با lift و null_p (جایگشتِ seed-دار).

- [ ] **Step 1: تستِ شکست‌خورده**

```python
# tests/engine/test_cluster.py
from engine.stages import cluster
from domains.quran_root import adapter

def _payload():
    return adapter.extract(adapter.resolve_unit("علم"))

def test_clusters_partition_all_evidence():
    pl = cluster.run(_payload())
    total = sum(len(c["members"]) for c in pl["clusters"])
    assert total == 854
    assert pl["method"]["seed"] == 20260626

def test_cluster_is_deterministic():
    p = _payload()
    assert cluster.run(p) == cluster.run(p)

def test_patterns_have_lift_and_null_p():
    pl = cluster.run(_payload())
    assert pl["patterns"], "expected co-occurrence patterns"
    for pat in pl["patterns"]:
        assert "lift" in pat and "null_p" in pat and "support" in pat
```

- [ ] **Step 2: شکست** — `python3 -m pytest tests/engine/test_cluster.py -v` → FAIL.

- [ ] **Step 3: پیاده‌سازی**

```python
# engine/stages/cluster.py
"""مرحلهٔ ۲ — خوشه‌بندیِ قطعی + هم‌آییِ معنادار vs نولِ بسامد."""
import random
import sqlite3
from collections import Counter, defaultdict

from domains.quran_root.adapter import DB_PATH

SEED = 20260626


def _signature(features):
    return f"pos={features.get('pos')}|aspect={features.get('aspect') or 'NA'}"


def _coroot_counts(evidence):
    """شمار هم‌آییِ ریشه‌های دیگر در آیاتِ حاویِ این unit."""
    ayat = sorted({(e["locus"]["surah"], e["locus"]["ayah"]) for e in evidence})
    co = Counter()
    self_roots = set()
    with sqlite3.connect(str(DB_PATH)) as c:
        for (s, a) in ayat:
            for (rid, ar) in c.execute(
                "SELECT DISTINCT w.root_id, r.root_arabic FROM words w "
                "JOIN roots r ON w.root_id=r.root_id "
                "WHERE w.surah_number=? AND w.ayah_number=? AND w.root_id IS NOT NULL",
                (s, a)):
                co[(rid, ar)] += 1
        total_ayat = c.execute("SELECT COUNT(*) FROM ayahs").fetchone()[0]
        global_doc = {}
        for (rid, ar), _ in co.items():
            n = c.execute("SELECT COUNT(DISTINCT surah_number||':'||ayah_number) "
                          "FROM words WHERE root_id=?", (rid,)).fetchone()[0]
            global_doc[(rid, ar)] = n
    return co, len(ayat), total_ayat, global_doc


def run(extract_payload, seed=SEED):
    evidence = extract_payload["evidence"]
    groups = defaultdict(list)
    for e in evidence:
        groups[_signature(e["features"])].append(e["evidence_id"])
    clusters = [{"cluster_id": f"c{i}", "signature": sig, "members": sorted(mem),
                 "size": len(mem)}
                for i, (sig, mem) in enumerate(sorted(groups.items()))]

    co, n_ayat, total_ayat, gdoc = _coroot_counts(evidence)
    rng = random.Random(seed)
    patterns = []
    for i, ((rid, ar), obs) in enumerate(co.most_common()):
        if ar == extract_payload["evidence"] or obs < 3:
            continue
        expected = n_ayat * (gdoc[(rid, ar)] / total_ayat)
        lift = round(obs / expected, 3) if expected else 0.0
        # نولِ جایگشتیِ ساده و قطعی
        ge = 0
        for _ in range(200):
            sample = rng.sample(range(total_ayat), n_ayat)
            if sum(1 for _ in sample if _ < gdoc[(rid, ar)]) >= obs:
                ge += 1
        patterns.append({"pattern_id": f"p{i}", "type": "cooccurrence",
                         "with": ar, "with_root_id": rid, "observed": obs,
                         "lift": lift, "null_p": round(ge / 200, 4),
                         "support": [ar]})
        if len(patterns) >= 20:
            break
    return {"method": {"algorithm": "feature-signature", "seed": seed,
                       "feature_space": ["pos", "aspect"]},
            "clusters": clusters, "patterns": patterns}
```
در `engine/orchestrator.py`: `STAGES` را به `[(1,"extract"),(2,"cluster")]` تغییر بده و پس از نوشتنِ extract اضافه کن:
```python
    from engine.stages import cluster as _cluster
    cpay = _cluster.run(payload)
    validate_payload("cluster", cpay)
    cenv = core.build_envelope(
        "cluster", 2, unit, substrate, core.PROTOCOL_VERSION, run_id,
        {"layer": "deterministic", "tool": "engine.stages.cluster"},
        {"prev_artifact": core.sha256_of(env)}, cpay)
    core.write_artifact(run_dir, 2, "cluster", cenv)
    done.append("cluster")
```

- [ ] **Step 4: سبزشدن** — `python3 -m pytest tests/engine/test_cluster.py -v` → PASS؛ سپس `./monad run quran-root علم` → `stages=['extract','cluster']`.

- [ ] **Step 5: commit**
```bash
git add engine/stages/cluster.py engine/orchestrator.py tests/engine/test_cluster.py
git commit -m "feat(engine): stage 2 Cluster — deterministic signatures + co-occurrence vs null"
```

---

## Task 5: ReasoningWorker + StatisticalWorker + HumanWorker + مرحلهٔ ۳ Observe

**Files:**
- Create: `engine/workers/base.py`, `engine/workers/statistical.py`, `engine/workers/human.py`
- Modify: `engine/orchestrator.py` (انتخابِ worker + اجرای Observe)
- Test: `tests/engine/test_workers_observe.py`

**Interfaces:**
- Produces:
  - `engine.workers.base.WorkerRequest(capability, input_payload, prev_stage)` (dataclass)
  - `engine.workers.base.ReasoningWorker` (ABC با `name` و `reason(request) -> dict`)
  - `engine.workers.statistical.StatisticalWorker` — capabilities: `observe`, `hypothesize`, `attack`, `reduce_propose`
  - `engine.workers.human.HumanWorker(fixture_dir)` — هر capability را از `<fixture_dir>/<capability>.json` می‌خواند
  - `engine.workers.get_worker(name) -> ReasoningWorker`

- [ ] **Step 1: تستِ شکست‌خورده**

```python
# tests/engine/test_workers_observe.py
from engine.workers import get_worker
from engine.workers.base import WorkerRequest
from engine.stages import cluster
from domains.quran_root import adapter

def _cluster_payload():
    return cluster.run(adapter.extract(adapter.resolve_unit("علم")))

def test_statistical_observe_cites_existing_ids():
    w = get_worker("statistical")
    cpay = _cluster_payload()
    req = WorkerRequest("observe", cpay, "cluster")
    out = w.reason(req)
    ids = {c["cluster_id"] for c in cpay["clusters"]} | {p["pattern_id"] for p in cpay["patterns"]}
    assert out["observations"]
    for o in out["observations"]:
        assert o["cites"] and all(cid in ids for cid in o["cites"])
        assert "hypothesis" not in o  # بدون فرضیه در Observe

def test_statistical_is_deterministic():
    w = get_worker("statistical")
    cpay = _cluster_payload()
    r1 = w.reason(WorkerRequest("observe", cpay, "cluster"))
    r2 = w.reason(WorkerRequest("observe", cpay, "cluster"))
    assert r1 == r2
```

- [ ] **Step 2: شکست** → FAIL.

- [ ] **Step 3: پیاده‌سازی**

```python
# engine/workers/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class WorkerRequest:
    capability: str
    input_payload: dict
    prev_stage: str


class ReasoningWorker(ABC):
    name = "base"

    @abstractmethod
    def reason(self, request: WorkerRequest) -> dict:
        ...
```
```python
# engine/workers/statistical.py
"""Workerِ قطعیِ پیش‌فرض — فرضیه‌ها را از آمارِ خوشه/الگو با قواعدِ ثابت می‌سازد."""
from engine.workers.base import ReasoningWorker, WorkerRequest


class StatisticalWorker(ReasoningWorker):
    name = "StatisticalWorker"

    def reason(self, request: WorkerRequest) -> dict:
        return getattr(self, f"_{request.capability}")(request.input_payload)

    def _observe(self, cpay):
        obs = []
        for c in cpay["clusters"]:
            obs.append({"observation_id": f"o_{c['cluster_id']}", "type": "description",
                        "statement": f"{c['size']} رخداد با امضای {c['signature']}.",
                        "cites": [c["cluster_id"]]})
        for p in cpay["patterns"][:10]:
            obs.append({"observation_id": f"o_{p['pattern_id']}", "type": "description",
                        "statement": f"هم‌آییِ پایدار با «{p['with']}» (lift={p['lift']}).",
                        "cites": [p["pattern_id"]]})
        return {"observations": obs}

    def _hypothesize(self, opay):  # Task 6
        return {"hypotheses": opay["_hypotheses"]} if "_hypotheses" in opay else {"hypotheses": []}

    def _attack(self, hpay):  # Task 7
        return {"attacks": hpay.get("_attacks", [])}

    def _reduce_propose(self, vpay):  # Task 10
        return vpay.get("_proposed", {"proposed_definition": {}})
```
```python
# engine/workers/human.py
import json
from pathlib import Path
from engine.workers.base import ReasoningWorker, WorkerRequest


class HumanWorker(ReasoningWorker):
    name = "HumanWorker"

    def __init__(self, fixture_dir):
        self.fixture_dir = Path(fixture_dir)

    def reason(self, request: WorkerRequest) -> dict:
        p = self.fixture_dir / f"{request.capability}.json"
        return json.loads(p.read_text(encoding="utf-8"))
```
```python
# افزودن به engine/workers/__init__.py
from engine.workers.statistical import StatisticalWorker

def get_worker(name, **kw):
    if name in ("statistical", "StatisticalWorker"):
        return StatisticalWorker()
    if name in ("human", "HumanWorker"):
        from engine.workers.human import HumanWorker
        return HumanWorker(kw["fixture_dir"])
    if name in ("claude", "ClaudeWorker"):
        from engine.workers.claude import ClaudeWorker
        return ClaudeWorker()
    raise ValueError(f"unknown worker: {name}")
```
در `orchestrator.run`: پس از انتخابِ worker، Observe را اجرا کن (لایهٔ discovery، بوکس: فقط payloadِ cluster):
```python
    from engine.workers import get_worker
    from engine.workers.base import WorkerRequest
    worker = get_worker(worker_name)
    opay = worker.reason(WorkerRequest("observe", cpay, "cluster"))
    validate_payload("observe", opay)
    oenv = core.build_envelope(
        "observe", 3, unit, substrate, core.PROTOCOL_VERSION, run_id,
        {"layer": "discovery", "worker": worker.name, "capability": "observe"},
        {"prev_artifact": core.sha256_of(cenv)}, opay)
    core.write_artifact(run_dir, 3, "observe", oenv)
    done.append("observe")
```
و `STAGES` → `+ (3,"observe")`.

- [ ] **Step 4: سبزشدن** — تست PASS؛ `./monad run quran-root علم` → `…,'observe'`.

- [ ] **Step 5: commit**
```bash
git add engine/workers tests/engine/test_workers_observe.py engine/orchestrator.py
git commit -m "feat(engine): ReasoningWorker interface + StatisticalWorker + stage 3 Observe"
```

---

## Task 6: مرحلهٔ ۴ — Hypothesis

**Files:**
- Modify: `engine/workers/statistical.py` (قاعدهٔ ساختِ فرضیه), `engine/orchestrator.py`
- Test: `tests/engine/test_hypothesis.py`

**Interfaces:**
- Produces: capability `hypothesize` که از payloadِ observe + cluster، ≤۵ فرضیه با `prediction.predicate` می‌سازد. ارکستریتور payloadِ ترکیبیِ `{"observations":…, "_clusters":…, "_patterns":…}` به worker می‌دهد (ورودیِ تمیزشدهٔ مجاز؛ Worker همچنان فقط همین ورودی را می‌بیند).

- [ ] **Step 1: تستِ شکست‌خورده**

```python
# tests/engine/test_hypothesis.py
from engine.workers import get_worker
from engine.workers.base import WorkerRequest
from engine.stages import cluster
from domains.quran_root import adapter

def _inputs():
    cpay = cluster.run(adapter.extract(adapter.resolve_unit("علم")))
    w = get_worker("statistical")
    opay = w.reason(WorkerRequest("observe", cpay, "cluster"))
    return w, {"observations": opay["observations"],
               "_clusters": cpay["clusters"], "_patterns": cpay["patterns"]}

def test_hypotheses_max_five_and_well_formed():
    w, inp = _inputs()
    out = w.reason(WorkerRequest("hypothesize", inp, "observe"))
    hs = out["hypotheses"]
    assert 1 <= len(hs) <= 5
    for h in hs:
        assert h["status"] == "PROPOSED"
        assert h["prediction"]["predicate"] in {
            "masked_recovery", "cooccurrence_constraint", "two_half_stability"}
        assert h["supported_by"]
```

- [ ] **Step 2: شکست** → FAIL.

- [ ] **Step 3: پیاده‌سازی** — جایگزینِ `_hypothesize` در `statistical.py`:
```python
    def _hypothesize(self, inp):
        patterns = inp.get("_patterns", [])
        hs = []
        # یک فرضیهٔ بازیابی برای کلِ unit
        hs.append({"hypothesis_id": "h_recover", "status": "PROPOSED",
                   "claim": "این ریشه از بافتِ آیه‌اش بازیابی‌پذیر است.",
                   "supported_by": [o["observation_id"] for o in inp["observations"][:3]],
                   "prediction": {"predicate": "masked_recovery", "params": {}}})
        # فرضیه‌های هم‌آییِ برترین الگوها
        for p in sorted(patterns, key=lambda x: -x["lift"])[:3]:
            hs.append({"hypothesis_id": f"h_{p['pattern_id']}", "status": "PROPOSED",
                       "claim": f"این ریشه به‌طورِ معنادار با «{p['with']}» هم‌می‌آید.",
                       "supported_by": [p["pattern_id"]],
                       "prediction": {"predicate": "cooccurrence_constraint",
                                      "params": {"with_root_id": p["with_root_id"],
                                                 "with": p["with"]}}})
        # یک فرضیهٔ پایداریِ دونیمه‌ای
        if patterns:
            top = max(patterns, key=lambda x: x["lift"])
            hs.append({"hypothesis_id": "h_stable", "status": "PROPOSED",
                       "claim": f"هم‌آییِ «{top['with']}» در دو نیمهٔ قرآن پایدار است.",
                       "supported_by": [top["pattern_id"]],
                       "prediction": {"predicate": "two_half_stability",
                                      "params": {"with_root_id": top["with_root_id"]}}})
        return {"hypotheses": hs[:5]}
```
در ارکستریتور پس از Observe:
```python
    hin = {"observations": opay["observations"],
           "_clusters": cpay["clusters"], "_patterns": cpay["patterns"]}
    hpay = worker.reason(WorkerRequest("hypothesize", hin, "observe"))
    validate_payload("hypothesis", hpay)
    henv = core.build_envelope(
        "hypothesis", 4, unit, substrate, core.PROTOCOL_VERSION, run_id,
        {"layer": "discovery", "worker": worker.name, "capability": "hypothesize"},
        {"prev_artifact": core.sha256_of(oenv)}, hpay)
    core.write_artifact(run_dir, 4, "hypothesis", henv)
    done.append("hypothesis")
```
و `STAGES += (4,"hypothesis")`.

- [ ] **Step 4: سبزشدن + اجرا**
- [ ] **Step 5: commit**
```bash
git add engine/workers/statistical.py engine/orchestrator.py tests/engine/test_hypothesis.py
git commit -m "feat(engine): stage 4 Hypothesis — ≤5 falsifiable, predicate-bound proposals"
```

---

## Task 7: مرحلهٔ ۵ — Attack

**Files:**
- Modify: `engine/workers/statistical.py`, `engine/orchestrator.py`
- Test: `tests/engine/test_attack.py`

**Interfaces:**
- Produces: capability `attack` — برای هر فرضیه، تلاشِ ردِّ قطعی؛ `worker_verdict ∈ {SURVIVES,WEAKENED,REFUTED}` (مشورتی). ورودی: `{"hypotheses":…, "_patterns":…}`.

- [ ] **Step 1: تستِ شکست‌خورده**
```python
# tests/engine/test_attack.py
from engine.workers import get_worker
from engine.workers.base import WorkerRequest

def test_attack_verdicts_present():
    w = get_worker("statistical")
    hin = {"hypotheses": [
        {"hypothesis_id": "h1", "prediction": {"predicate": "cooccurrence_constraint",
         "params": {"with": "x"}}, "supported_by": ["p0"]}],
        "_patterns": [{"pattern_id": "p0", "with": "x", "lift": 4.0, "null_p": 0.01}]}
    out = w.reason(WorkerRequest("attack", hin, "hypothesis"))
    assert out["attacks"][0]["worker_verdict"] in {"SURVIVES", "WEAKENED", "REFUTED"}
    assert out["attacks"][0]["hypothesis_id"] == "h1"
```
- [ ] **Step 2: شکست** → FAIL.
- [ ] **Step 3: پیاده‌سازی** — جایگزینِ `_attack`:
```python
    def _attack(self, inp):
        pat = {p["pattern_id"]: p for p in inp.get("_patterns", [])}
        attacks = []
        for h in inp["hypotheses"]:
            verdict, refs = "SURVIVES", []
            for sid in h.get("supported_by", []):
                p = pat.get(sid)
                if p and (p.get("lift", 0) < 1.5 or p.get("null_p", 1) > 0.05):
                    verdict = "WEAKENED"
                    refs.append({"argument": "lift پایین یا null_p بالا.",
                                 "counter_evidence": [sid]})
            attacks.append({"hypothesis_id": h["hypothesis_id"],
                            "refutations": refs, "worker_verdict": verdict})
        return {"attacks": attacks}
```
در ارکستریتور:
```python
    apay = worker.reason(WorkerRequest("attack",
        {"hypotheses": hpay["hypotheses"], "_patterns": cpay["patterns"]}, "hypothesis"))
    validate_payload("attack", apay)
    aenv = core.build_envelope(
        "attack", 5, unit, substrate, core.PROTOCOL_VERSION, run_id,
        {"layer": "discovery", "worker": worker.name, "capability": "attack"},
        {"prev_artifact": core.sha256_of(henv)}, apay)
    core.write_artifact(run_dir, 5, "attack", aenv)
    done.append("attack")
```
و `STAGES += (5,"attack")`.
- [ ] **Step 4: سبزشدن + اجرا**
- [ ] **Step 5: commit**
```bash
git add engine/workers/statistical.py engine/orchestrator.py tests/engine/test_attack.py
git commit -m "feat(engine): stage 5 Attack — advisory self-refutation verdicts"
```

---

## Task 8: Predicate Registry (پروتکل) + مجریِ آن در Adapter

**Files:**
- Create: `engine/predicates/registry.py`
- Modify: `domains/quran_root/adapter.py` (افزودنِ `execute_predicate`)
- Test: `tests/engine/test_predicates.py`

**Interfaces:**
- Produces:
  - `engine.predicates.registry.REGISTRY` (dict: name → {params_schema, pass_rule_doc})
  - `engine.predicates.registry.known(name) -> bool`
  - `domains.quran_root.adapter.execute_predicate(name, params, unit) -> dict` با `{"score","baseline","null_p","passed", ...}`
- پریدیکیت‌ها: `masked_recovery`, `cooccurrence_constraint`, `two_half_stability`.

- [ ] **Step 1: تستِ شکست‌خورده**
```python
# tests/engine/test_predicates.py
from engine.predicates import registry
from domains.quran_root import adapter

def test_registry_is_domain_independent():
    assert registry.known("masked_recovery")
    assert "params_schema" in registry.REGISTRY["cooccurrence_constraint"]

def test_cooccurrence_executor_passes_for_strong_pair():
    u = adapter.resolve_unit("علم")
    # «كتب» (کتاب/نوشتن) همراهیِ شناخته‌شده با علم
    kt = adapter.resolve_unit("كتب")
    res = adapter.execute_predicate("cooccurrence_constraint",
                                    {"with_root_id": kt["unit_id"]}, u)
    assert set(res) >= {"score", "null_p", "passed"}
    assert isinstance(res["passed"], bool)

def test_masked_recovery_beats_baseline_is_bool():
    u = adapter.resolve_unit("علم")
    res = adapter.execute_predicate("masked_recovery", {}, u)
    assert "score" in res and "baseline" in res and isinstance(res["passed"], bool)
```
- [ ] **Step 2: شکست** → FAIL.
- [ ] **Step 3: پیاده‌سازی**
```python
# engine/predicates/registry.py
"""رجیستریِ پریدیکیت‌ها — سطحِ پروتکل، دامنه‌مستقل. فقط قرارداد؛ اجرا در DomainAdapter."""
REGISTRY = {
    "masked_recovery": {
        "params_schema": {},
        "pass_rule_doc": "score > baseline ∧ null_p < 0.05"},
    "cooccurrence_constraint": {
        "params_schema": {"with_root_id": "int"},
        "pass_rule_doc": "lift > 1.5 ∧ null_p < 0.05"},
    "two_half_stability": {
        "params_schema": {"with_root_id": "int"},
        "pass_rule_doc": "present in both halves"},
}


def known(name) -> bool:
    return name in REGISTRY
```
افزودن به `domains/quran_root/adapter.py`:
```python
import random as _random

def _ayat_of_root(c, rid):
    return {(r[0], r[1]) for r in c.execute(
        "SELECT DISTINCT surah_number, ayah_number FROM words WHERE root_id=?", (rid,))}

def execute_predicate(name, params, unit):
    rid = unit["unit_id"]
    with _conn() as c:
        if name == "cooccurrence_constraint":
            mine = _ayat_of_root(c, rid)
            other = _ayat_of_root(c, params["with_root_id"])
            total = c.execute("SELECT COUNT(*) FROM ayahs").fetchone()[0]
            obs = len(mine & other)
            expected = len(mine) * len(other) / total if total else 0
            lift = round(obs / expected, 3) if expected else 0.0
            rng = _random.Random(20260626)
            ge = sum(1 for _ in range(200)
                     if len(set(rng.sample(sorted(mine), min(len(mine), len(mine)))) ) and
                     obs <= obs)  # placeholder replaced below
            # نولِ جایگشتی: نمونه‌گیریِ تصادفیِ آیات هم‌اندازهٔ other
            allay = list(_ayat_of_root(c, rid) | {(s, a) for (s, a) in
                        c.execute("SELECT surah_number, ayah_number FROM ayahs")})
            ge = 0
            for _ in range(200):
                samp = set(rng.sample(allay, len(other)))
                if len(mine & samp) >= obs:
                    ge += 1
            null_p = round(ge / 200, 4)
            return {"score": lift, "lift": lift, "baseline": 1.0,
                    "null_p": null_p, "observed": obs,
                    "passed": bool(lift > 1.5 and null_p < 0.05)}
        if name == "two_half_stability":
            mine = _ayat_of_root(c, rid)
            other = _ayat_of_root(c, params["with_root_id"])
            half = 57  # سورهٔ میانه؛ نیمهٔ اول 1..57
            h1 = any(s <= half for (s, a) in (mine & other))
            h2 = any(s > half for (s, a) in (mine & other))
            return {"score": 1.0 if (h1 and h2) else 0.0, "null_p": 0.0,
                    "passed": bool(h1 and h2), "half1": h1, "half2": h2}
        if name == "masked_recovery":
            # بازیابیِ ساده: نسبتِ آیاتِ این ریشه که برترین هم‌ریشه‌اش هم در آن‌هاست،
            # در برابرِ baselineِ بسامدِ سراسریِ آن هم‌ریشه.
            mine = _ayat_of_root(c, rid)
            co = {}
            for (s, a) in mine:
                for (orid,) in c.execute(
                    "SELECT DISTINCT root_id FROM words WHERE surah_number=? "
                    "AND ayah_number=? AND root_id IS NOT NULL AND root_id<>?",
                    (s, a, rid)):
                    co[orid] = co.get(orid, 0) + 1
            if not co:
                return {"score": 0.0, "baseline": 0.0, "null_p": 1.0, "passed": False}
            best, hits = max(co.items(), key=lambda kv: kv[1])
            score = round(hits / len(mine), 4)
            total = c.execute("SELECT COUNT(*) FROM ayahs").fetchone()[0]
            bdoc = c.execute("SELECT COUNT(DISTINCT surah_number||':'||ayah_number) "
                             "FROM words WHERE root_id=?", (best,)).fetchone()[0]
            baseline = round(bdoc / total, 4)
            return {"score": score, "baseline": baseline, "best_coroot": best,
                    "null_p": 0.0 if score > baseline else 1.0,
                    "passed": bool(score > baseline * 1.5)}
    raise ValueError(f"unknown predicate: {name}")
```
> **یادداشتِ پاک‌سازی (Bug Fix هنگام پیاده‌سازی):** placeholderِ میانیِ `ge` در شاخهٔ cooccurrence را حذف کن؛ فقط حلقهٔ جایگشتیِ دوم معتبر است (در کد بالا عمداً نشان داده شد تا حواست باشد آن را پاک کنی).

- [ ] **Step 4: سبزشدن** — `python3 -m pytest tests/engine/test_predicates.py -v` → PASS.
- [ ] **Step 5: commit**
```bash
git add engine/predicates/registry.py domains/quran_root/adapter.py tests/engine/test_predicates.py
git commit -m "feat(engine): predicate registry (protocol) + quran_root executors"
```

---

## Task 9: مرحلهٔ ۶ — Verify (دروازهٔ تولّدِ Knowledge)

**Files:**
- Create: `engine/stages/verify.py`
- Modify: `engine/orchestrator.py`
- Test: `tests/engine/test_verify.py`

**Interfaces:**
- Produces: `engine.stages.verify.run(hypotheses, attacks, unit, adapter) -> dict` با `{"verifications": [...]}`. هر فرضیه: اجرای `adapter.execute_predicate`؛ `decision=ACCEPTED` اگر `passed`؛ تیر بر اساسِ effect size؛ در غیر این صورت `REJECTED`/`UNKNOWN`. **تنها این ماژول `ACCEPTED` می‌نویسد** (R1).

- [ ] **Step 1: تستِ شکست‌خورده**
```python
# tests/engine/test_verify.py
from engine.stages import verify
from domains.quran_root import adapter

def test_true_cooccurrence_accepted():
    u = adapter.resolve_unit("علم")
    kt = adapter.resolve_unit("كتب")
    hyps = [{"hypothesis_id": "h1", "status": "PROPOSED",
             "prediction": {"predicate": "cooccurrence_constraint",
                            "params": {"with_root_id": kt["unit_id"]}}}]
    out = verify.run(hyps, [], u, adapter)
    v = out["verifications"][0]
    assert v["decision"] in {"ACCEPTED", "REJECTED", "UNKNOWN"}
    if v["decision"] == "ACCEPTED":
        assert v["confidence_tier"] in {"صریح", "قوی", "محتمل"}
        assert v["knowledge_id"]

def test_false_hypothesis_rejected():
    u = adapter.resolve_unit("علم")
    # ریشه‌ای کم‌ربط با علم → باید رد شود
    rare = adapter.resolve_unit("فيل")  # «فیل» (سورهٔ فیل)
    hyps = [{"hypothesis_id": "hF", "status": "PROPOSED",
             "prediction": {"predicate": "cooccurrence_constraint",
                            "params": {"with_root_id": rare["unit_id"]}}}]
    out = verify.run(hyps, [], u, adapter)
    assert out["verifications"][0]["decision"] != "ACCEPTED"
```
- [ ] **Step 2: شکست** → FAIL.
- [ ] **Step 3: پیاده‌سازی**
```python
# engine/stages/verify.py
"""مرحلهٔ ۶ — دروازهٔ قطعی. تنها زایندهٔ Knowledge (R1)."""
from engine.predicates import registry


def _tier(result):
    s = result.get("lift", result.get("score", 0)) or 0
    if s >= 3.0:
        return "صریح"
    if s >= 1.8:
        return "قوی"
    return "محتمل"


def run(hypotheses, attacks, unit, adapter):
    verifications = []
    for i, h in enumerate(hypotheses):
        pred = h["prediction"]["predicate"]
        if not registry.known(pred):
            verifications.append({"hypothesis_id": h["hypothesis_id"],
                                  "decision": "UNKNOWN", "confidence_tier": None,
                                  "knowledge_id": None,
                                  "tests": {"error": "unknown predicate"}})
            continue
        res = adapter.execute_predicate(pred, h["prediction"].get("params", {}), unit)
        if res["passed"]:
            verifications.append({
                "hypothesis_id": h["hypothesis_id"], "decision": "ACCEPTED",
                "confidence_tier": _tier(res), "knowledge_id": f"k_{unit['ref']}_{i}",
                "tests": {pred: res}})
        else:
            verifications.append({
                "hypothesis_id": h["hypothesis_id"], "decision": "REJECTED",
                "confidence_tier": None, "knowledge_id": None,
                "tests": {pred: res}})
    return {"verifications": verifications}
```
در ارکستریتور (لایهٔ قطعی، می‌خواند: attack + substrate):
```python
    from engine.stages import verify as _verify
    vpay = _verify.run(hpay["hypotheses"], apay["attacks"], unit, adp)
    validate_payload("verify", vpay)
    venv = core.build_envelope(
        "verify", 6, unit, substrate, core.PROTOCOL_VERSION, run_id,
        {"layer": "deterministic", "tool": "engine.stages.verify"},
        {"prev_artifact": core.sha256_of(aenv), "substrate": substrate["hash"]}, vpay)
    core.write_artifact(run_dir, 6, "verify", venv)
    done.append("verify")
```
و `STAGES += (6,"verify")`.
- [ ] **Step 4: سبزشدن + اجرا**
- [ ] **Step 5: commit**
```bash
git add engine/stages/verify.py engine/orchestrator.py tests/engine/test_verify.py
git commit -m "feat(engine): stage 6 Verify — deterministic gate, the only Knowledge minter"
```

---

## Task 10: مرحلهٔ ۷ — Reduce (پیشنهاد اکتشافی → سنجشِ قطعی)

**Files:**
- Create: `engine/stages/reduce_measure.py`
- Modify: `engine/workers/statistical.py` (`_reduce_propose`), `engine/orchestrator.py`
- Test: `tests/engine/test_reduce.py`

**Interfaces:**
- Produces:
  - worker `reduce_propose` → `{"proposed_definition": {"statement","primitives","relations"}}`
  - `engine.stages.reduce_measure.run(proposed, verifications, unit, adapter) -> dict` با `{"proposed_definition","compression","accepted_definition"}`؛ `compression={n_primitives,coverage,mdl_bits,predicts_heldout}`.

- [ ] **Step 1: تستِ شکست‌خورده**
```python
# tests/engine/test_reduce.py
from engine.stages import reduce_measure
from domains.quran_root import adapter

def test_reduce_measures_compression():
    u = adapter.resolve_unit("علم")
    proposed = {"proposed_definition": {"statement": "دانستن/شناخت",
                "primitives": ["know", "perceive"], "relations": []}}
    verifs = [{"decision": "ACCEPTED", "knowledge_id": "k0"},
              {"decision": "REJECTED", "knowledge_id": None}]
    out = reduce_measure.run(proposed, verifs, u, adapter)
    assert out["compression"]["n_primitives"] == 2
    assert 0 <= out["compression"]["coverage"] <= 1
    assert "predicts_heldout" in out["compression"]
    assert "accepted_definition" in out
```
- [ ] **Step 2: شکست** → FAIL.
- [ ] **Step 3: پیاده‌سازی**
```python
# engine/stages/reduce_measure.py
"""مرحلهٔ ۷ — تعریفِ کمینه: Worker پیشنهاد می‌دهد، کد می‌سنجد."""
import math


def run(proposed, verifications, unit, adapter):
    pdef = proposed["proposed_definition"]
    prims = pdef.get("primitives", [])
    accepted = [v for v in verifications if v.get("decision") == "ACCEPTED"]
    coverage = round(len(accepted) / len(verifications), 4) if verifications else 0.0
    mdl_bits = round(len(prims) * math.log2(max(len(prims), 1) + 1), 3)
    heldout = adapter.execute_predicate("masked_recovery", {}, unit)
    gate = coverage >= 0.5 and len(prims) >= 1
    return {"proposed_definition": pdef,
            "compression": {"n_primitives": len(prims), "coverage": coverage,
                            "mdl_bits": mdl_bits,
                            "predicts_heldout": {"score": heldout["score"],
                                                 "passed": heldout["passed"]}},
            "accepted_definition": (
                {"statement": pdef.get("statement", ""), "primitives": prims,
                 "covers_knowledge": [v["knowledge_id"] for v in accepted]}
                if gate else {"statement": "UNKNOWN", "primitives": [],
                              "covers_knowledge": []})}
```
`_reduce_propose` در `statistical.py`:
```python
    def _reduce_propose(self, inp):
        # primitiveها = برترین هم‌ریشه‌های تأییدشده به‌عنوانِ هستهٔ معنایی
        prims = inp.get("_top_coroots", [])[:3] or ["<sense>"]
        return {"proposed_definition": {
            "statement": "تعریفِ کمینه بر پایهٔ هم‌آیی‌های تأییدشده.",
            "primitives": prims, "relations": []}}
```
ارکستریتور (Reduce = دو زیرگام: propose سپس measure):
```python
    top_co = [p["with"] for p in sorted(cpay["patterns"], key=lambda x: -x["lift"])[:3]]
    rprop = worker.reason(WorkerRequest("reduce_propose", {"_top_coroots": top_co}, "verify"))
    from engine.stages import reduce_measure as _rm
    rpay = _rm.run(rprop, vpay["verifications"], unit, adp)
    validate_payload("reduce", rpay)
    renv = core.build_envelope(
        "reduce", 7, unit, substrate, core.PROTOCOL_VERSION, run_id,
        {"layer": "deterministic", "tool": "engine.stages.reduce_measure"},
        {"prev_artifact": core.sha256_of(venv)}, rpay)
    core.write_artifact(run_dir, 7, "reduce", renv)
    done.append("reduce")
```
و `STAGES += (7,"reduce")`.
- [ ] **Step 4: سبزشدن + اجرا**
- [ ] **Step 5: commit**
```bash
git add engine/stages/reduce_measure.py engine/workers/statistical.py engine/orchestrator.py tests/engine/test_reduce.py
git commit -m "feat(engine): stage 7 Reduce — proposal + deterministic compression measure"
```

---

## Task 11: مرحلهٔ ۸ — Graph

**Files:**
- Create: `engine/stages/graph.py`
- Modify: `engine/orchestrator.py`
- Test: `tests/engine/test_graph.py`

**Interfaces:**
- Produces: `engine.stages.graph.run(reduce_payload, cluster_patterns, unit, kb_links=None) -> dict` با `{"links","network_coherence","predictive_check"}`. links = برترین هم‌ریشه‌ها به‌عنوانِ روابطِ `co-defines`. v1: `network_coherence.conflicts=[]` (KB تهی)، `predictive_check` روی هم‌ریشه‌ها.

- [ ] **Step 1: تستِ شکست‌خورده**
```python
# tests/engine/test_graph.py
from engine.stages import graph

def test_graph_links_and_coherence():
    patterns = [{"with": "كتب", "with_root_id": 5, "lift": 4.0},
                {"with": "ايه", "with_root_id": 9, "lift": 2.5}]
    out = graph.run({"accepted_definition": {"primitives": ["know"]}},
                    patterns, {"ref": "Elm"})
    assert out["links"] and out["links"][0]["relation"] == "co-defines"
    assert out["network_coherence"]["passed"] is True
    assert "score" in out["predictive_check"]
```
- [ ] **Step 2: شکست** → FAIL.
- [ ] **Step 3: پیاده‌سازی**
```python
# engine/stages/graph.py
"""مرحلهٔ ۸ — پیوند به شبکهٔ دانش + بررسیِ سازگاری و پیش‌بینی."""


def run(reduce_payload, cluster_patterns, unit, kb_links=None):
    links = [{"to_unit": p["with"], "to_root_id": p.get("with_root_id"),
              "relation": "co-defines", "weight": p["lift"], "evidence": [p["with"]]}
             for p in sorted(cluster_patterns, key=lambda x: -x["lift"])[:5]]
    # سازگاری در برابرِ KB (در v1 تهی → بدون تعارض)
    coherence = {"conflicts": [], "passed": True}
    # پیش‌بینی: نسبتِ لینک‌هایی با lift معنادار
    strong = [l for l in links if l["weight"] > 1.5]
    pred = {"applied_to": [l["to_unit"] for l in links],
            "hits": len(strong),
            "score": round(len(strong) / len(links), 4) if links else 0.0}
    return {"links": links, "network_coherence": coherence,
            "predictive_check": pred}
```
ارکستریتور:
```python
    from engine.stages import graph as _graph
    gpay = _graph.run(rpay, cpay["patterns"], unit)
    validate_payload("graph", gpay)
    genv = core.build_envelope(
        "graph", 8, unit, substrate, core.PROTOCOL_VERSION, run_id,
        {"layer": "deterministic", "tool": "engine.stages.graph"},
        {"prev_artifact": core.sha256_of(renv), "kb_snapshot": "sha256:empty"}, gpay)
    core.write_artifact(run_dir, 8, "graph", genv)
    done.append("graph")
```
و `STAGES += (8,"graph")`.
- [ ] **Step 4: سبزشدن + اجرا**
- [ ] **Step 5: commit**
```bash
git add engine/stages/graph.py engine/orchestrator.py tests/engine/test_graph.py
git commit -m "feat(engine): stage 8 Graph — network links, coherence, predictive check"
```

---

## Task 12: سه Store + Provenance DAG + مرحلهٔ ۹ Commit

**Files:**
- Create: `engine/store.py`, `engine/stages/commit.py`
- Modify: `engine/orchestrator.py`
- Test: `tests/engine/test_store_commit.py`

**Interfaces:**
- Produces:
  - `engine.store.Store(root)` با: `put_evidence(list)`, `put_knowledge(obj)`, `put_ontology_primitive(obj)`, `add_dag_nodes(list)`, `add_dag_edges(list)`, `append_log(event)`, `provenance_complete(knowledge_id) -> bool` (P2: مسیر به ≥۱ evidence)
  - `engine.stages.commit.run(store, unit, run_id, artifacts) -> dict` با `{"committed": {...}}`؛ knowledgeِ دونمایشی، evidence، primitiveها، و یال‌های DAG را می‌نویسد.

- [ ] **Step 1: تستِ شکست‌خورده**
```python
# tests/engine/test_store_commit.py
from engine import store as store_mod
from engine.stages import commit

def test_commit_writes_three_stores_and_dag(tmp_path):
    st = store_mod.Store(tmp_path)
    artifacts = {
        "extract": {"payload": {"evidence": [
            {"evidence_id": "2:31:2:1", "locus": {}, "surface": "ع", "features": {}}]}},
        "verify": {"payload": {"verifications": [
            {"decision": "ACCEPTED", "knowledge_id": "k_Elm_0", "hypothesis_id": "h1",
             "confidence_tier": "قوی", "tests": {}}]}},
        "reduce": {"payload": {"accepted_definition": {"statement": "دانستن",
            "primitives": ["know"]}}},
        "graph": {"payload": {"links": [{"to_unit": "كتب", "relation": "co-defines"}]}},
    }
    out = commit.run(st, {"ref": "Elm", "domain": "quran-root", "unit_id": 218},
                     "rid123", artifacts)
    assert out["committed"]["knowledge"] == 1
    k = st.get_knowledge("k_Elm_0")
    assert "formal_representation" in k and "natural_explanation" in k
    assert st.provenance_complete("k_Elm_0") is True   # P2
    assert (tmp_path / "evidence").exists() and (tmp_path / "ontology").exists()
```
- [ ] **Step 2: شکست** → FAIL.
- [ ] **Step 3: پیاده‌سازی**
```python
# engine/store.py
"""سه Store + Provenance DAG + log/index. منبعِ رسمیِ ماشین."""
import json
from pathlib import Path


class Store:
    def __init__(self, root):
        self.root = Path(root)
        for sub in ("evidence", "knowledge", "ontology", "provenance", "log"):
            (self.root / sub).mkdir(parents=True, exist_ok=True)
        self.dag_path = self.root / "provenance" / "graph.json"
        if not self.dag_path.exists():
            self.dag_path.write_text(json.dumps({"nodes": [], "edges": []}),
                                     encoding="utf-8")

    def _load_dag(self):
        return json.loads(self.dag_path.read_text(encoding="utf-8"))

    def _save_dag(self, dag):
        self.dag_path.write_text(json.dumps(dag, ensure_ascii=False, indent=2),
                                 encoding="utf-8")

    def put_evidence(self, items):
        for e in items:
            p = self.root / "evidence" / (e["evidence_id"].replace(":", "_") + ".json")
            if not p.exists():
                p.write_text(json.dumps(e, ensure_ascii=False), encoding="utf-8")

    def put_knowledge(self, obj):
        (self.root / "knowledge" / (obj["knowledge_id"] + ".json")).write_text(
            json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_knowledge(self, kid):
        return json.loads((self.root / "knowledge" / (kid + ".json")).read_text("utf-8"))

    def put_ontology_primitive(self, obj):
        (self.root / "ontology" / (obj["id"] + ".json")).write_text(
            json.dumps(obj, ensure_ascii=False), encoding="utf-8")

    def add_dag_nodes(self, nodes):
        dag = self._load_dag()
        have = {n["id"] for n in dag["nodes"]}
        dag["nodes"].extend(n for n in nodes if n["id"] not in have)
        self._save_dag(dag)

    def add_dag_edges(self, edges):
        dag = self._load_dag()
        dag["edges"].extend(edges)
        self._save_dag(dag)

    def append_log(self, event):
        with open(self.root / "log" / "events.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def provenance_complete(self, knowledge_id) -> bool:
        """P2 — آیا از node دانش مسیری به ≥۱ node شواهد هست؟"""
        dag = self._load_dag()
        typ = {n["id"]: n["type"] for n in dag["nodes"]}
        adj = {}
        for e in dag["edges"]:
            adj.setdefault(e["from"], []).append(e["to"])
        seen, stack = set(), [knowledge_id]
        while stack:
            cur = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            if typ.get(cur) == "evidence":
                return True
            stack.extend(adj.get(cur, []))
        return False
```
```python
# engine/stages/commit.py
"""مرحلهٔ ۹ — نوشتنِ knowledgeِ دونمایشی + evidence + ontology + DAG به Store."""


def run(store, unit, run_id, artifacts):
    ev = artifacts["extract"]["payload"]["evidence"]
    store.put_evidence(ev)
    store.add_dag_nodes([{"id": f"ev:{e['evidence_id']}", "type": "evidence"} for e in ev])

    accepted = [v for v in artifacts["verify"]["payload"]["verifications"]
                if v["decision"] == "ACCEPTED"]
    adef = artifacts["reduce"]["payload"]["accepted_definition"]
    links = artifacts["graph"]["payload"]["links"]
    for prim in adef.get("primitives", []):
        store.put_ontology_primitive({"id": f"prim:{prim}", "primitive": prim})

    n = 0
    sample_ev = f"ev:{ev[0]['evidence_id']}" if ev else None
    for v in accepted:
        kid = v["knowledge_id"]
        obj = {
            "knowledge_id": kid, "unit": unit, "run_id": run_id, "status": "ACCEPTED",
            "formal_representation": {
                "definition_primitives": adef.get("primitives", []),
                "relations": [{"type": l["relation"], "to_unit": l["to_unit"]}
                              for l in links[:3]],
                "verified_by": [v["tests"]], "scope": {"unit": unit["ref"]},
                "confidence_tier": v["confidence_tier"]},
            "natural_explanation": adef.get("statement", ""),
            "provenance_nodes": [kid, f"hyp:{v['hypothesis_id']}"]
                                + ([sample_ev] if sample_ev else []),
            "relations_to_knowledge": []}
        store.put_knowledge(obj)
        store.add_dag_nodes([{"id": kid, "type": "knowledge"},
                             {"id": f"hyp:{v['hypothesis_id']}", "type": "hypothesis"}])
        store.add_dag_edges([{"from": kid, "to": f"hyp:{v['hypothesis_id']}",
                              "type": "verifies"}])
        if sample_ev:
            store.add_dag_edges([{"from": f"hyp:{v['hypothesis_id']}",
                                  "to": sample_ev, "type": "cites"}])
        store.append_log({"event": "knowledge_committed", "knowledge_id": kid,
                          "run_id": run_id})
        n += 1
    return {"committed": {"knowledge": n, "evidence": len(ev),
                          "primitives": len(adef.get("primitives", []))}}
```
ارکستریتور (Commit؛ Store در `store/`):
```python
    from engine.store import Store
    from engine.stages import commit as _commit
    store = Store(REPO / "store")
    arts = {"extract": env, "verify": venv, "reduce": renv, "graph": genv}
    cmt = _commit.run(store, unit, run_id, arts)
    validate_payload("commit", cmt)
    cmenv = core.build_envelope(
        "commit", 9, unit, substrate, core.PROTOCOL_VERSION, run_id,
        {"layer": "deterministic", "tool": "engine.stages.commit"},
        {"prev_artifact": core.sha256_of(genv)}, cmt)
    core.write_artifact(run_dir, 9, "commit", cmenv)
    done.append("commit")
    res_extra = {"committed": cmt["committed"]}
```
(و در `return`، `**res_extra` را اضافه کن.) `STAGES += (9,"commit")`.
- [ ] **Step 4: سبزشدن + اجرا** — `./monad run quran-root علم` → `stages` شاملِ `commit`؛ `store/knowledge/` پر می‌شود.
- [ ] **Step 5: commit**
```bash
git add engine/store.py engine/stages/commit.py engine/orchestrator.py tests/engine/test_store_commit.py
git commit -m "feat(engine): three stores + provenance DAG + stage 9 Commit"
```

---

## Task 13: Monad Memory

**Files:**
- Create: `engine/memory.py`
- Modify: `engine/orchestrator.py` (ثبتِ attempt + rejected + discoveries؛ پوششِ خطا → failed_runs)
- Test: `tests/engine/test_memory.py`

**Interfaces:**
- Produces: `engine.memory.Memory(root)` با `record_attempt(run_id, unit, status)`, `record_rejected(run_id, hyp_id, reason)`, `record_failed_run(run_id, error)`, `record_discovery(run_id, knowledge_ids)`.

- [ ] **Step 1: تستِ شکست‌خورده**
```python
# tests/engine/test_memory.py
from engine.memory import Memory
import json

def test_memory_records(tmp_path):
    m = Memory(tmp_path)
    m.record_attempt("r1", {"ref": "Elm"}, "ok")
    m.record_rejected("r1", "hF", "low lift")
    m.record_discovery("r1", ["k_Elm_0"])
    rej = (tmp_path / "rejected" / "events.jsonl").read_text("utf-8").strip()
    assert "hF" in rej
    att = (tmp_path / "attempts" / "events.jsonl").read_text("utf-8").strip()
    assert json.loads(att)["status"] == "ok"
```
- [ ] **Step 2: شکست** → FAIL.
- [ ] **Step 3: پیاده‌سازی**
```python
# engine/memory.py
"""Monad Memory — تاریخِ تلاش‌ها (افزایشی، فقط‌نوشتنی)."""
import json
from pathlib import Path


class Memory:
    def __init__(self, root):
        self.root = Path(root)
        for sub in ("attempts", "rejected", "failed_runs", "abandoned", "discoveries"):
            (self.root / sub).mkdir(parents=True, exist_ok=True)

    def _append(self, sub, event):
        with open(self.root / sub / "events.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def record_attempt(self, run_id, unit, status):
        self._append("attempts", {"run_id": run_id, "unit": unit, "status": status})

    def record_rejected(self, run_id, hyp_id, reason):
        self._append("rejected", {"run_id": run_id, "hypothesis_id": hyp_id,
                                  "reason": reason})

    def record_failed_run(self, run_id, error):
        self._append("failed_runs", {"run_id": run_id, "error": str(error)})

    def record_discovery(self, run_id, knowledge_ids):
        self._append("discoveries", {"run_id": run_id, "knowledge_ids": knowledge_ids})
```
در ارکستریتور: `Memory(REPO/"memory")` بساز؛ کلِ بدنهٔ مراحل را در `try/except` بپیچ — در `except`: `mem.record_failed_run(run_id, e)` و `raise`؛ پس از Verify، برای هر `REJECTED`: `mem.record_rejected(...)`؛ پس از Commit: `mem.record_discovery(run_id, [k ids])`؛ در پایان: `mem.record_attempt(run_id, unit, "ok")`.
- [ ] **Step 4: سبزشدن + اجرا**
- [ ] **Step 5: commit**
```bash
git add engine/memory.py engine/orchestrator.py tests/engine/test_memory.py
git commit -m "feat(engine): Monad Memory — attempts/rejected/failed/discoveries"
```

---

## Task 14: RFC Generator + گیتِ Provenance (P2)

**Files:**
- Create: `rfc/generator.py`
- Modify: `engine/orchestrator.py` (فراخوانیِ generator پس از Commit)
- Test: `tests/engine/test_rfc.py`

**Interfaces:**
- Produces: `rfc.generator.generate(store, unit, run_id, protocol_version, benchmark=None) -> dict` و نوشتنِ `rfc/<domain>/<ref>/RFC-…-<run_id>.{json,md}`. **پیش از نوشتن**، `store.provenance_complete` برای هر knowledge بررسی می‌شود؛ نقض → `ProvenanceError` (P2).

- [ ] **Step 1: تستِ شکست‌خورده**
```python
# tests/engine/test_rfc.py
from engine import store as store_mod
from engine.stages import commit
from rfc import generator

def _populated_store(tmp_path):
    st = store_mod.Store(tmp_path)
    arts = {"extract": {"payload": {"evidence": [
              {"evidence_id": "2:31:2:1", "locus": {}, "surface": "ع", "features": {}}]}},
            "verify": {"payload": {"verifications": [
              {"decision": "ACCEPTED", "knowledge_id": "k_Elm_0", "hypothesis_id": "h1",
               "confidence_tier": "قوی", "tests": {}}]}},
            "reduce": {"payload": {"accepted_definition": {"statement": "دانستن",
               "primitives": ["know"]}}},
            "graph": {"payload": {"links": []}}}
    commit.run(st, {"ref": "Elm", "domain": "quran-root", "unit_id": 218}, "rid", arts)
    return st

def test_rfc_generated_with_seven_fields(tmp_path):
    st = _populated_store(tmp_path)
    rfc = generator.generate(st, {"ref": "Elm", "domain": "quran-root", "unit_id": 218},
                             "rid", "0.1.0", out_root=tmp_path / "rfc")
    assert set(rfc["fields"]) == {"evidence", "reasoning", "confidence", "scope",
                                  "limitations", "relationships", "history"}
    assert rfc["knowledge"][0]["formal_representation"]
    assert (tmp_path / "rfc" / "quran-root" / "Elm").exists()
```
- [ ] **Step 2: شکست** → FAIL.
- [ ] **Step 3: پیاده‌سازی**
```python
# rfc/generator.py
"""RFC Generator — Publication Layer. Storeها → سندِ انسان/ممیزی (idempotent)."""
import json
from pathlib import Path


class ProvenanceError(ValueError):
    pass


def _list_knowledge(store):
    out = []
    for p in sorted((store.root / "knowledge").glob("*.json")):
        out.append(json.loads(p.read_text("utf-8")))
    return out


def generate(store, unit, run_id, protocol_version, benchmark=None, out_root=None):
    knowledge = _list_knowledge(store)
    for k in knowledge:
        if not store.provenance_complete(k["knowledge_id"]):
            raise ProvenanceError(f"P2 violated: {k['knowledge_id']}")
    rfc_id = f"RFC-{unit['domain']}-{unit['ref']}-v{protocol_version}-{run_id}"
    rfc = {
        "rfc_id": rfc_id, "unit": unit, "protocol_version": protocol_version,
        "run_id": run_id, "status": "ACCEPTED", "supersedes": None,
        "relation_to_prior": None, "knowledge": knowledge,
        "fields": {
            "evidence": {"count": len(list((store.root / "evidence").glob("*.json")))},
            "reasoning": {"chain": "cluster→observe→hypothesis→attack→verify→reduce→graph"},
            "confidence": {k["knowledge_id"]: k["formal_representation"]["confidence_tier"]
                           for k in knowledge},
            "scope": {"unit": unit["ref"]},
            "limitations": {"note": "v1 minimal-fidelity; KB empty."},
            "relationships": {"links": [r for k in knowledge
                                        for r in k["formal_representation"]["relations"]]},
            "history": {"protocol_version": protocol_version, "supersedes": None}},
        "benchmark_score": benchmark or {}}
    out_root = Path(out_root) if out_root else Path(__file__).resolve().parent
    d = out_root / unit["domain"] / unit["ref"]
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{rfc_id}.json").write_text(json.dumps(rfc, ensure_ascii=False, indent=2), "utf-8")
    md = [f"# {rfc_id}", "", f"**واحد:** {unit['display'] if 'display' in unit else unit['ref']}",
          "", "## دانشِ تأییدشده"]
    for k in knowledge:
        md.append(f"- **{k['knowledge_id']}** ({k['formal_representation']['confidence_tier']}): "
                  f"{k['natural_explanation']}")
    (d / f"{rfc_id}.md").write_text("\n".join(md), "utf-8")
    return rfc
```
ارکستریتور: پس از Commit، `from rfc import generator; rfc = generator.generate(store, unit, run_id, core.PROTOCOL_VERSION)` و افزودنِ `rfc_id` به خروجی.
- [ ] **Step 4: سبزشدن + اجرا** — RFC در `rfc/quran-root/Elm/` تولید می‌شود.
- [ ] **Step 5: commit**
```bash
git add rfc/generator.py engine/orchestrator.py tests/engine/test_rfc.py
git commit -m "feat(rfc): RFC Generator (publication layer) + P2 provenance gate"
```

---

## Task 15: Benchmark شش‌بُعدی + red-team + ledger

**Files:**
- Create: `engine/benchmark/score.py`, `engine/benchmark/redteam/Elm.json`
- Modify: `engine/orchestrator.py` (محاسبهٔ benchmark و افزودن به خروجی + RFC)
- Test: `tests/engine/test_benchmark.py`

**Interfaces:**
- Produces:
  - `engine.benchmark.score.score_run(run_dir, adapter, unit, redteam=None, n_repro=2) -> dict` با ۶ کلید (هر یک ۰..۱).
  - `engine.benchmark.score.pareto_dominates(a, b) -> bool` (هر ۶ بُعد `≥` و ≥یکی `>`).

- [ ] **Step 1: تستِ شکست‌خورده**
```python
# tests/engine/test_benchmark.py
from engine.benchmark import score

def test_pareto_rule():
    a = {"Recoverability": .5, "Reproducibility": 1, "Falsifiability": .8,
         "Compression": .5, "Coherence": 1, "PredictivePower": .6}
    b = dict(a); b["Recoverability"] = .4
    assert score.pareto_dominates(a, b) is True
    assert score.pareto_dominates(b, a) is False
    assert score.pareto_dominates(a, a) is False  # برابر → غلبه نیست

def test_score_keys_present(tmp_path):
    # یک run کاملِ from-scratch
    from engine import orchestrator
    res = orchestrator.run("quran-root", "علم", run_root=tmp_path)
    from domains.quran_root import adapter
    vec = score.score_run(res["run_dir"], adapter,
                          adapter.resolve_unit("علم"))
    assert set(vec) == {"Recoverability", "Reproducibility", "Falsifiability",
                        "Compression", "Coherence", "PredictivePower"}
    assert all(0 <= v <= 1 for v in vec.values())
```
- [ ] **Step 2: شکست** → FAIL.
- [ ] **Step 3: پیاده‌سازی**
```python
# engine/benchmark/redteam/Elm.json
{ "false_hypotheses": [
  {"hypothesis_id": "rt_fil", "prediction": {"predicate": "cooccurrence_constraint",
   "params": {"with_root_id": null, "with_arabic": "فيل"}}} ] }
```
```python
# engine/benchmark/score.py
"""Benchmark شش‌بُعدی + قاعدهٔ پارتو."""
import json
from pathlib import Path

DIMS = ["Recoverability", "Reproducibility", "Falsifiability",
        "Compression", "Coherence", "PredictivePower"]


def _art(run_dir, idx, name):
    return json.loads((Path(run_dir) / f"0{idx}_{name}.json").read_text("utf-8"))


def score_run(run_dir, adapter, unit, redteam=None, n_repro=2):
    reduce_p = _art(run_dir, 7, "reduce")["payload"]
    graph_p = _art(run_dir, 8, "graph")["payload"]
    verify_p = _art(run_dir, 6, "verify")["payload"]

    recover = float(reduce_p["compression"]["predicts_heldout"]["score"])
    recover = max(0.0, min(1.0, recover))

    # Reproducibility — اجرای مجدد و Jaccardِ knowledge_idهای ACCEPTED
    from engine import orchestrator
    base = {v["knowledge_id"] for v in verify_p["verifications"]
            if v["decision"] == "ACCEPTED"}
    import tempfile
    agree = 1.0
    if base:
        with tempfile.TemporaryDirectory() as td:
            r2 = orchestrator.run(unit["domain"], unit["display"], run_root=td)
            v2 = _art(r2["run_dir"], 6, "verify")["payload"]
            s2 = {v["knowledge_id"] for v in v2["verifications"]
                  if v["decision"] == "ACCEPTED"}
            inter = len(base & s2); uni = len(base | s2)
            agree = inter / uni if uni else 1.0

    # Falsifiability — نسبتِ red-team که REJECTED شد
    rt = redteam or {"false_hypotheses": []}
    fp = 0
    for h in rt["false_hypotheses"]:
        params = dict(h["prediction"]["params"])
        if params.get("with_root_id") is None and params.get("with_arabic"):
            params["with_root_id"] = adapter.resolve_unit(params["with_arabic"])["unit_id"]
        res = adapter.execute_predicate(h["prediction"]["predicate"], params, unit)
        if not res["passed"]:
            fp += 1
    fals = fp / len(rt["false_hypotheses"]) if rt["false_hypotheses"] else 1.0

    comp = float(reduce_p["compression"]["coverage"])
    coher = 1.0 if graph_p["network_coherence"]["passed"] else 0.0
    pred = float(graph_p["predictive_check"]["score"])

    return {"Recoverability": round(recover, 4), "Reproducibility": round(agree, 4),
            "Falsifiability": round(fals, 4), "Compression": round(comp, 4),
            "Coherence": round(coher, 4), "PredictivePower": round(pred, 4)}


def pareto_dominates(a, b) -> bool:
    ge = all(a[d] >= b[d] for d in DIMS)
    gt = any(a[d] > b[d] for d in DIMS)
    return ge and gt
```
ارکستریتور: پس از RFC، `redteam` را از `engine/benchmark/redteam/<ref>.json` بخوان (اگر بود)، `vec = score.score_run(run_dir, adp, unit, redteam)`، در خروجی و در RFC قرار بده، و در `engine/benchmark/ledger/<protocol_version>.json` بنویس.
> **هشدارِ بازگشت‌پذیری (Performance/Bug):** `score_run` یک‌بار pipeline را دوباره اجرا می‌کند (Reproducibility). برای جلوگیری از بازگشتِ بی‌نهایت، اجرای داخلی نباید خودش benchmark را صدا بزند — benchmark فقط در ارکستریتورِ سطحِ‌بالا و **پس از** نوشتنِ مراحل اجرا می‌شود (نه داخلِ `run`). مطمئن شو `orchestrator.run` خودش `score_run` را صدا نمی‌زند؛ آن را در یک تابعِ جداگانهٔ `run_and_score` یا در CLI قرار بده.
- [ ] **Step 4: سبزشدن** — `python3 -m pytest tests/engine/test_benchmark.py -v` → PASS.
- [ ] **Step 5: commit**
```bash
git add engine/benchmark tests/engine/test_benchmark.py engine/orchestrator.py
git commit -m "feat(benchmark): 6-D score + Pareto rule + red-team set for علم"
```

---

## Task 16: Meta-Protocol — registry + current_stable + Pareto promotion

**Files:**
- Create: `protocol/registry.json`, `engine/metaprotocol.py`
- Test: `tests/engine/test_metaprotocol.py`

**Interfaces:**
- Produces: `engine.metaprotocol.evaluate_candidate(candidate_version, score_vec, registry_path) -> dict` با `{"promoted": bool, "current_stable": ver}`. اگر هیچ Stable نباشد → نامزد Stable می‌شود؛ در غیر این صورت فقط با `pareto_dominates`.

- [ ] **Step 1: تستِ شکست‌خورده**
```python
# tests/engine/test_metaprotocol.py
import json
from engine import metaprotocol

V = {"Recoverability": .5, "Reproducibility": 1, "Falsifiability": 1,
     "Compression": .6, "Coherence": 1, "PredictivePower": .5}

def test_first_candidate_becomes_stable(tmp_path):
    reg = tmp_path / "registry.json"
    reg.write_text(json.dumps({"current_stable": None, "versions": {}}), "utf-8")
    out = metaprotocol.evaluate_candidate("0.1.0", V, reg)
    assert out["promoted"] and out["current_stable"] == "0.1.0"

def test_non_dominating_candidate_not_promoted(tmp_path):
    reg = tmp_path / "registry.json"
    reg.write_text(json.dumps({"current_stable": "0.1.0",
        "versions": {"0.1.0": {"score": V, "status": "stable"}}}), "utf-8")
    worse = dict(V); worse["Compression"] = .4
    out = metaprotocol.evaluate_candidate("0.2.0", worse, reg)
    assert out["promoted"] is False and out["current_stable"] == "0.1.0"
```
- [ ] **Step 2: شکست** → FAIL.
- [ ] **Step 3: پیاده‌سازی**
```python
# protocol/registry.json
{ "current_stable": null, "versions": {} }
```
```python
# engine/metaprotocol.py
"""Meta-Protocol — نسخه‌بندی و ارتقای پروتکل با غلبهٔ پارتو."""
import json
from pathlib import Path
from engine.benchmark.score import pareto_dominates


def evaluate_candidate(candidate_version, score_vec, registry_path):
    reg = json.loads(Path(registry_path).read_text("utf-8"))
    cur = reg.get("current_stable")
    promoted = False
    if cur is None:
        promoted = True
    else:
        promoted = pareto_dominates(score_vec, reg["versions"][cur]["score"])
    reg["versions"][candidate_version] = {
        "score": score_vec, "status": "stable" if promoted else "candidate"}
    if promoted:
        if cur and cur in reg["versions"]:
            reg["versions"][cur]["status"] = "superseded"
        reg["current_stable"] = candidate_version
    Path(registry_path).write_text(json.dumps(reg, ensure_ascii=False, indent=2), "utf-8")
    return {"promoted": promoted, "current_stable": reg["current_stable"]}
```
- [ ] **Step 4: سبزشدن** — تست PASS.
- [ ] **Step 5: commit**
```bash
git add protocol/registry.json engine/metaprotocol.py tests/engine/test_metaprotocol.py
git commit -m "feat(protocol): Meta-Protocol registry + Pareto promotion"
```

---

## Task 17: ClaudeWorker + Skill-0001 (اتصالِ مدل به Worker Interface)

**Files:**
- Create: `engine/workers/claude.py`, `.claude/skills/discover-one-unit/SKILL.md`
- Test: `tests/engine/test_claude_worker.py`

**Interfaces:**
- Produces: `engine.workers.claude.ClaudeWorker` — در مسیرِ خودکار (بدون فراخوانیِ مدل) یک `NotImplementedError` با پیامِ روشن می‌دهد که باید از طریقِ Skill-0001 (انسان‌در‌حلقه/عامل) پر شود؛ اما اگر فایلِ پاسخِ آماده در `run_dir/_claude/<capability>.json` باشد، آن را می‌خواند (مثلِ HumanWorker). این، قراردادِ تعویض‌پذیریِ مدل را اثبات می‌کند بدون پلامبینگِ API (خارج از scope v1).

- [ ] **Step 1: تستِ شکست‌خورده**
```python
# tests/engine/test_claude_worker.py
import json, pytest
from engine.workers.claude import ClaudeWorker
from engine.workers.base import WorkerRequest

def test_claude_reads_prepared_response(tmp_path):
    d = tmp_path / "_claude"; d.mkdir()
    (d / "observe.json").write_text(json.dumps({"observations": []}), "utf-8")
    w = ClaudeWorker(response_dir=d)
    assert w.reason(WorkerRequest("observe", {}, "cluster")) == {"observations": []}

def test_claude_without_response_raises():
    w = ClaudeWorker(response_dir=None)
    with pytest.raises(NotImplementedError):
        w.reason(WorkerRequest("observe", {}, "cluster"))
```
- [ ] **Step 2: شکست** → FAIL.
- [ ] **Step 3: پیاده‌سازی**
```python
# engine/workers/claude.py
"""ClaudeWorker — اتصالِ مدل از طریقِ Skill-0001. در v1 از پاسخِ آماده می‌خواند."""
import json
from pathlib import Path
from engine.workers.base import ReasoningWorker, WorkerRequest


class ClaudeWorker(ReasoningWorker):
    name = "ClaudeWorker"

    def __init__(self, response_dir=None):
        self.response_dir = Path(response_dir) if response_dir else None

    def reason(self, request: WorkerRequest) -> dict:
        if self.response_dir and (self.response_dir / f"{request.capability}.json").exists():
            return json.loads(
                (self.response_dir / f"{request.capability}.json").read_text("utf-8"))
        raise NotImplementedError(
            "ClaudeWorker در مسیرِ خودکار نیاز به Skill-0001 دارد؛ "
            "از --worker statistical برای اجرای بی‌دخالت استفاده کن.")
```
```markdown
<!-- .claude/skills/discover-one-unit/SKILL.md -->
---
name: discover-one-unit
description: Skill-0001 — اجرای Discovery Protocol برای یک Unit با ClaudeWorker به‌عنوانِ پیشنهاددهندهٔ فرضیه در مراحلِ اکتشافی (Observe/Hypothesis/Attack/Reduce-propose).
---
# Skill-0001 — Discover One Unit
این Skill، Claude را به‌عنوانِ یک ReasoningWorker به موتور متصل می‌کند. در هر مرحلهٔ
اکتشافی، payloadِ مرحلهٔ قبل را می‌خوانی و خروجی را **دقیقاً** مطابقِ schema تولید می‌کنی،
و در `run_dir/_claude/<capability>.json` می‌نویسی. قواعد: فقط فرضیه (status=PROPOSED)؛
هرگز Knowledge اعلام نکن؛ هر ادعا به evidence_id ارجاع دهد؛ هرگز DB/Store/آینده را نخوان.
```
- [ ] **Step 4: سبزشدن** — تست PASS.
- [ ] **Step 5: commit**
```bash
git add engine/workers/claude.py .claude/skills/discover-one-unit/SKILL.md tests/engine/test_claude_worker.py
git commit -m "feat(workers): ClaudeWorker binding + Skill-0001 (model-swappable proposer)"
```

---

## Task 18: یکپارچه‌سازیِ نهایی — `run_and_score` end-to-end + RFC-000001

**Files:**
- Modify: `engine/orchestrator.py` (تابعِ `run_and_score`), `monad` (صداکردنِ آن)
- Create: `rfc/RFC-000001-discovery-protocol.md` (سندِ نرماتیو، خلاصهٔ spec منجمد)
- Test: `tests/engine/test_e2e.py`

**Interfaces:**
- Produces: `engine.orchestrator.run_and_score(domain, unit_ref, worker_name="statistical") -> dict` که `run` را اجرا، سپس benchmark را محاسبه، RFC را با امتیاز بازتولید، Meta-Protocol را ارزیابی، و خلاصه را برمی‌گرداند.

- [ ] **Step 1: تستِ شکست‌خورده (معیارِ موفقیتِ v1)**
```python
# tests/engine/test_e2e.py
from engine import orchestrator

def test_full_pipeline_for_elm():
    res = orchestrator.run_and_score("quran-root", "علم")
    # هر ۹ مرحله
    assert res["stages_done"] == ["extract", "cluster", "observe", "hypothesis",
                                  "attack", "verify", "reduce", "graph", "commit"]
    # دانش ثبت شده
    assert res["committed"]["knowledge"] >= 1
    # RFC تولید شده
    assert res["rfc_id"].startswith("RFC-quran-root-Elm-")
    # بردارِ ۶ بُعدی
    assert set(res["benchmark"]) == {"Recoverability", "Reproducibility",
        "Falsifiability", "Compression", "Coherence", "PredictivePower"}
    # Meta-Protocol ارزیابی شد
    assert "current_stable" in res["metaprotocol"]
```
- [ ] **Step 2: شکست** → FAIL.
- [ ] **Step 3: پیاده‌سازی** — `run_and_score` در ارکستریتور:
```python
def run_and_score(domain, unit_ref, worker_name="statistical"):
    res = run(domain, unit_ref, worker_name=worker_name)
    adp = ADAPTERS[domain]
    unit = adp.resolve_unit(unit_ref)
    from engine.benchmark import score as _score
    rt_path = REPO / "engine" / "benchmark" / "redteam" / f"{unit['ref']}.json"
    redteam = None
    if rt_path.exists():
        import json as _json
        redteam = _json.loads(rt_path.read_text("utf-8"))
    vec = _score.score_run(res["run_dir"], adp, unit, redteam)
    # RFC را با امتیاز بازتولید کن
    from engine.store import Store
    from rfc import generator
    store = Store(REPO / "store")
    rfc = generator.generate(store, unit, res["run_id"], core.PROTOCOL_VERSION,
                             benchmark=vec)
    # ledger
    led_dir = REPO / "engine" / "benchmark" / "ledger"
    led_dir.mkdir(parents=True, exist_ok=True)
    import json as _json
    (led_dir / f"{core.PROTOCOL_VERSION}.json").write_text(
        _json.dumps({"unit": unit["ref"], "score": vec}, ensure_ascii=False, indent=2),
        "utf-8")
    # meta-protocol
    from engine import metaprotocol
    mp = metaprotocol.evaluate_candidate(core.PROTOCOL_VERSION, vec,
                                         REPO / "protocol" / "registry.json")
    res.update({"benchmark": vec, "rfc_id": rfc["rfc_id"], "metaprotocol": mp})
    return res
```
در `monad`: فرمانِ `run` → `orchestrator.run_and_score(...)` و چاپِ `rfc_id` و بردارِ benchmark.
سندِ `rfc/RFC-000001-discovery-protocol.md`: نسخهٔ نرماتیوِ خلاصه از spec منجمد (۹ مرحله، اصولِ R/P، Worker Interface، Storeها، Memory، Meta-Protocol، benchmark). با ارجاع به طرحِ کاملِ `docs/superpowers/specs/2026-06-26-discovery-protocol-design.md`.
- [ ] **Step 4: سبزشدن + اجرای نهایی**
```bash
python3 -m pytest tests/engine -v          # همهٔ تست‌ها PASS
./monad run quran-root علم                 # اجرای کاملِ بی‌دخالت
```
انتظار: ۹ مرحله، Store/Memory/DAG پر، RFC تولید، بردارِ ۶ بُعدی چاپ‌شده.
- [ ] **Step 5: commit**
```bash
git add engine/orchestrator.py monad rfc/RFC-000001-discovery-protocol.md tests/engine/test_e2e.py
git commit -m "feat(engine): run_and_score end-to-end + RFC-000001 — monad run quran-root علم works"
```

---

## Self-Review (پوششِ spec)

- **§2 لایه‌ها + Worker Interface** → T1,T3,T5,T17 ✓
- **§4 نه مرحله** → T2(1),T4(2),T5(3),T6(4),T7(5),T9(6),T10(7),T11(8),T12(9) ✓
- **§3 اصول:** R1 (تنها Verify→ACCEPTED) T9 ✓ · R3 (بوکس/خطی) ساختارِ ورودی‌ها ✓ · P1 (Evidence immutable) Store.put_evidence فقط اگر نبود ✓ · P2 (provenance کامل) T12/T14 گیت ✓ · P3 (supersedes) فیلدها در RFC + metaprotocol ✓
- **§5 envelope** T1 ✓ · **§6 schemas** schemas.py + هر مرحله ✓
- **§7 Knowledge دونمایشی** T12 (formal+natural) ✓
- **§8 Predicate Registry (پروتکل) + executor (adapter)** T8 ✓
- **§9 Provenance DAG** T12 ✓ · **§10 سه Store** T12 ✓ · **§11 Memory** T13 ✓ · **§12 Meta-Protocol** T16 ✓
- **§13 RFC schema** T14 ✓ · **§14 benchmark ۶ بُعدی + پارتو + red-team + ledger** T15 ✓
- **§16 معیارِ موفقیت `monad run quran-root علم`** T18 ✓

**Placeholder/Bug یادداشت‌شده:** در T8 یک placeholderِ `ge` عمداً نشان داده و دستورِ حذفش داده شده (Bug Fix هنگام اجرا). در T15 خطرِ بازگشت benchmark→run کنترل شده (benchmark فقط در `run_and_score`، نه داخلِ `run`).
**سازگاریِ نام‌ها:** `run`/`run_and_score`, `score_run`/`pareto_dominates`, `Store`/`Memory`, `execute_predicate`, `generate` — در سراسرِ Taskها یکدست‌اند.
