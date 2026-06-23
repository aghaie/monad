# Self-Interpretation Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Quran self-interpretation engine — a local web app where a user explores how the Quran explains itself via a network graph wired to an evidence panel — as the first module of an extensible platform.

**Architecture:** A deterministic build pass materializes a complete evidence index (every ayah → ranked explaining verses + the shared concept-roots) plus a sura-community graph layout, all from `generated/monad.db` using the *exact* validated L7/L8 method. A zero-dependency Python stdlib HTTP server exposes read-only JSON endpoints over shared data services. A vanilla-JS single-page shell renders a 3-tier graph (constellation → sura → verse-focus) with an evidence panel; new feature modules register via a two-file contract without touching the core.

**Tech Stack:** Python 3.9 stdlib (`http.server`, `sqlite3`, `json`) — no third-party backend deps. Frontend: vanilla ES modules + Sigma.js & graphology loaded from CDN. Tests: `pytest` (backend + build + integration).

## Global Constraints

- **Evidence-only (charter):** never emit any external translation, gloss, or meaning. Endpoints return verse text (from the corpus), shared roots (Arabic/Buckwalter form + id + count), and relation weights — nothing interpretive. Abstention (verses with no explainers) must be representable and visible, never hidden.
- **Validated method, unchanged:** the build mirrors `scripts/build_L7_global.py` / `scripts/build_L8_interpret.py` exactly — `ALLAH = "{ll~ah"`, rare-root band `DF_LO,DF_HI = 3,40`, `SEED = 11`, stems only (`segment_type == "STEM"` and `pos in ("N","ADJ","V")`, `root_id is not None`, `lemma_id != allah`).
- **Phase discipline:** the build is byte-identical on re-run (seeded, no wall-clock, no unseeded randomness). A `validate_*` script proves it.
- **Read-only data:** all DB access opens SQLite in read-only mode (`file:...?mode=ro`). The app never writes to `generated/`.
- **No new pip dependencies for the backend.** Frontend libs come from CDN; no npm/build step.
- **Paths:** repo root is the parent of `app/`. All generated artifacts live under `generated/layers/`.

---

### Task 1: Deterministic build — evidence index + community graph

**Files:**
- Create: `build/build_evidence_index.py`
- Create: `build/validate_evidence_index.py`
- Output (generated, not committed by this task's code but produced): `generated/layers/L8_interpret/evidence_index.json`, `generated/layers/L7_global/graph_communities.json`
- Test: `build/validate_evidence_index.py` IS the test (run twice + canonical-pair assertions).

**Interfaces:**
- Produces: `generated/layers/L8_interpret/evidence_index.json` with shape
  `{"method": "engine-evidence-1.0", "note": str, "index": { "<s>:<a>": [ {"ayah": "<s>:<a>", "weight": float, "cross_sura": bool, "shared_roots": [ {"root_id": int, "root_bw": str, "root_ar": str} ] } ] } }` — one entry per all 6236 ayat (empty list when no explainers).
- Produces: `generated/layers/L7_global/graph_communities.json` with shape
  `{"method": "engine-graph-1.0", "nodes": [ {"sura": int, "name_ar": str, "ayah_count": int, "x": float, "y": float} ], "edges": [ {"source": int, "target": int, "weight": float} ] }` (114 nodes; edges = top inter-sura aggregate weights).

- [ ] **Step 1: Write the build script**

Create `build/build_evidence_index.py`:

```python
#!/usr/bin/env python3
"""
build/build_evidence_index.py

Materializes the validated self-interpreting network into two artifacts the
engine serves:

  1. evidence_index.json — for EVERY ayah, the verses that most explain it
     (rare-root idf-weighted) AND the shared concept-roots that justify each
     link. Same method as scripts/build_L7_global.py + build_L8_interpret.py,
     extended to all 6236 ayat and enriched with shared roots per link.

  2. graph_communities.json — 114 suras as graph nodes with a deterministic
     force-directed layout, and the strongest inter-sura aggregate edges.

Deterministic (seeded), offline, no external semantics.
"""

import argparse
import json
import math
import random
import sqlite3
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB_DEFAULT = REPO / "generated" / "monad.db"
EVID_OUT = REPO / "generated" / "layers" / "L8_interpret" / "evidence_index.json"
GRAPH_OUT = REPO / "generated" / "layers" / "L7_global" / "graph_communities.json"

ALLAH = "{ll~ah"
DF_LO, DF_HI = 3, 40
SEED = 11
TOPN = 12          # explainers kept per ayah (vs L7's 5) — same method, less truncation
TOP_EDGES = 400    # strongest inter-sura edges kept for the constellation
LAYOUT_ITERS = 400


def load_ayah_roots(db):
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    allah = con.execute("SELECT lemma_id FROM lemmas WHERE lemma_buckwalter=?", (ALLAH,)).fetchone()[0]
    root_bw = {r: b for r, b in con.execute("SELECT root_id,root_buckwalter FROM roots")}
    root_ar = {r: a for r, a in con.execute("SELECT root_id,root_arabic FROM roots")}
    suras = {n: (nm, c) for n, nm, c in
             con.execute("SELECT surah_number,name_arabic,ayah_count FROM surahs")}
    rows = con.execute("SELECT surah_number s,ayah_number a,pos,segment_type st,lemma_id,root_id "
                       "FROM morphology ORDER BY surah_number,ayah_number").fetchall()
    con.close()
    by = defaultdict(list)
    for r in rows:
        by[(r["s"], r["a"])].append(r)
    ayah_roots = {}
    for key, toks in by.items():
        ayah_roots[key] = {t["root_id"] for t in toks
                           if t["st"] == "STEM" and t["pos"] in ("N", "ADJ", "V")
                           and t["root_id"] is not None and t["lemma_id"] != allah}
    return ayah_roots, root_bw, root_ar, suras


def fr_layout(nodes, edges, seed, iters):
    """Compact deterministic Fruchterman-Reingold on a small node set."""
    rnd = random.Random(seed)
    pos = {n: [rnd.uniform(-1.0, 1.0), rnd.uniform(-1.0, 1.0)] for n in nodes}
    area = 1.0
    k = math.sqrt(area / max(1, len(nodes)))
    t = 0.1
    adj = [(e["source"], e["target"]) for e in edges]
    for _ in range(iters):
        disp = {n: [0.0, 0.0] for n in nodes}
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                a, b = nodes[i], nodes[j]
                dx = pos[a][0] - pos[b][0]
                dy = pos[a][1] - pos[b][1]
                dist = math.hypot(dx, dy) or 1e-4
                rep = (k * k) / dist
                ux, uy = dx / dist, dy / dist
                disp[a][0] += ux * rep; disp[a][1] += uy * rep
                disp[b][0] -= ux * rep; disp[b][1] -= uy * rep
        for a, b in adj:
            dx = pos[a][0] - pos[b][0]
            dy = pos[a][1] - pos[b][1]
            dist = math.hypot(dx, dy) or 1e-4
            att = (dist * dist) / k
            ux, uy = dx / dist, dy / dist
            disp[a][0] -= ux * att; disp[a][1] -= uy * att
            disp[b][0] += ux * att; disp[b][1] += uy * att
        for n in nodes:
            d = math.hypot(*disp[n]) or 1e-4
            pos[n][0] += (disp[n][0] / d) * min(d, t)
            pos[n][1] += (disp[n][1] / d) * min(d, t)
        t = max(t * 0.985, 0.001)
    return {n: [round(pos[n][0], 5), round(pos[n][1], 5)] for n in nodes}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(DB_DEFAULT))
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    ayah_roots, root_bw, root_ar, suras = load_ayah_roots(args.db)
    keys = sorted(ayah_roots)
    N = len(keys)

    df = Counter()
    for k in keys:
        for r in ayah_roots[k]:
            df[r] += 1
    rare = {r for r, d in df.items() if DF_LO <= d <= DF_HI}

    def idf(r):
        return math.log(N / df[r])

    inv = defaultdict(list)
    for k in keys:
        for r in ayah_roots[k]:
            if r in rare:
                inv[r].append(k)

    nbr = defaultdict(Counter)
    shared = defaultdict(lambda: defaultdict(list))
    inter = defaultdict(float)  # (sura_a, sura_b) with sura_a < sura_b
    for r in rare:
        wv = idf(r)
        ays = inv[r]
        for a, b in combinations(ays, 2):
            nbr[a][b] += wv; nbr[b][a] += wv
            shared[a][b].append(r); shared[b][a].append(r)
            if a[0] != b[0]:
                lo, hi = (a[0], b[0]) if a[0] < b[0] else (b[0], a[0])
                inter[(lo, hi)] += wv

    # evidence index — every ayah, even those with no explainers (empty list)
    index = {}
    for k in keys:
        refs = nbr[k].most_common(TOPN)
        index[f"{k[0]}:{k[1]}"] = [
            {"ayah": f"{b[0]}:{b[1]}", "weight": round(w, 3), "cross_sura": b[0] != k[0],
             "shared_roots": [{"root_id": r, "root_bw": root_bw[r], "root_ar": root_ar[r]}
                              for r in sorted(set(shared[k][b]))]}
            for b, w in refs]

    EVID_OUT.parent.mkdir(parents=True, exist_ok=True)
    EVID_OUT.write_text(json.dumps(
        {"method": "engine-evidence-1.0",
         "note": "for each ayah, verses that most explain it (rare-root idf-weighted) + shared concept-roots",
         "index": index}, ensure_ascii=False, indent=1), encoding="utf-8")

    # community graph — 114 sura nodes + strongest inter-sura edges + layout
    node_ids = sorted(suras)
    top_edges = sorted(inter.items(), key=lambda kv: -kv[1])[:TOP_EDGES]
    edges = [{"source": a, "target": b, "weight": round(w, 3)} for (a, b), w in top_edges]
    pos = fr_layout(node_ids, edges, SEED, LAYOUT_ITERS)
    nodes = [{"sura": s, "name_ar": suras[s][0], "ayah_count": suras[s][1],
              "x": pos[s][0], "y": pos[s][1]} for s in node_ids]

    GRAPH_OUT.parent.mkdir(parents=True, exist_ok=True)
    GRAPH_OUT.write_text(json.dumps(
        {"method": "engine-graph-1.0", "nodes": nodes, "edges": edges},
        ensure_ascii=False, indent=1), encoding="utf-8")

    if not args.quiet:
        nonempty = sum(1 for v in index.values() if v)
        print(f"evidence_index: {N} ayat ({nonempty} with explainers, {N - nonempty} abstaining)")
        print(f"graph_communities: {len(nodes)} suras, {len(edges)} edges")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the build**

Run: `python3 build/build_evidence_index.py`
Expected: prints `evidence_index: 6236 ayat (... with explainers, ... abstaining)` and `graph_communities: 114 suras, 400 edges`. Two JSON files written.

- [ ] **Step 3: Write the validation script**

Create `build/validate_evidence_index.py`:

```python
#!/usr/bin/env python3
"""Validate the evidence build: byte-identical reproducibility + canonical pairs."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EVID = REPO / "generated" / "layers" / "L8_interpret" / "evidence_index.json"
GRAPH = REPO / "generated" / "layers" / "L7_global" / "graph_communities.json"

# (verse, expected explainer, expected shared root in Arabic) from CLAUDE.md
CANONICAL = [("2:255", "7:97", "نوم"), ("24:35", "7:137", "شرق"), ("3:7", "9:117", "زیغ")]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    before = sha(EVID), sha(GRAPH)
    subprocess.run([sys.executable, str(REPO / "build" / "build_evidence_index.py"), "--quiet"], check=True)
    after = sha(EVID), sha(GRAPH)
    assert before == after, "BUILD NOT REPRODUCIBLE: hashes changed on re-run"

    idx = json.loads(EVID.read_text())["index"]
    assert len(idx) == 6236, f"expected 6236 ayat, got {len(idx)}"
    for verse, explainer, root_ar in CANONICAL:
        refs = idx.get(verse, [])
        hit = next((r for r in refs if r["ayah"] == explainer), None)
        assert hit, f"{verse} should be explained by {explainer}"
        roots = {sr["root_ar"] for sr in hit["shared_roots"]}
        assert root_ar in roots, f"{verse}->{explainer} should share root {root_ar}, got {roots}"

    graph = json.loads(GRAPH.read_text())
    assert len(graph["nodes"]) == 114, f"expected 114 sura nodes, got {len(graph['nodes'])}"
    assert all("x" in n and "y" in n for n in graph["nodes"]), "nodes missing layout coords"

    print("OK: reproducible, 6236 ayat, canonical pairs present, 114 sura nodes with layout")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run validation — expect PASS**

Run: `python3 build/validate_evidence_index.py`
Expected: `OK: reproducible, 6236 ayat, canonical pairs present, 114 sura nodes with layout`
(If a canonical assertion fails, the build deviates from the validated method — stop and reconcile against `scripts/build_L7_global.py` before continuing.)

- [ ] **Step 5: Commit**

```bash
git add build/build_evidence_index.py build/validate_evidence_index.py generated/layers/L8_interpret/evidence_index.json generated/layers/L7_global/graph_communities.json
git commit -m "feat: build complete evidence index + community graph (validated method)"
```

---

### Task 2: Backend data layer + verses service

**Files:**
- Create: `app/__init__.py` (empty), `app/server/__init__.py` (empty), `app/server/data/__init__.py` (empty), `app/server/services/__init__.py` (empty)
- Create: `app/server/data/db.py`
- Create: `app/server/data/indexes.py`
- Create: `app/server/services/verses.py`
- Test: `tests/test_verses.py`

**Interfaces:**
- Produces `app/server/data/db.py`: `connect() -> sqlite3.Connection` (read-only, `row_factory=Row`); `get_ayah(con, s: int, a: int) -> dict | None` (keys: `ref, surah, ayah, text_uthmani, text_normalized`); `get_ayah_tokens(con, s, a) -> list[dict]` (keys: `position, form, root_id, root_ar, root_bw`).
- Produces `app/server/data/indexes.py`: `evidence() -> dict` and `communities() -> dict` (each lazy-loads its JSON once and caches it).
- Produces `app/server/services/verses.py`: `verse_payload(s: int, a: int) -> dict | None` with shape `{"ref": "s:a", "surah": int, "ayah": int, "text": {"uthmani": str, "normalized": str}, "tokens": [{"position": int, "form": str, "root_id": int|None, "root_ar": str|None, "root_bw": str|None}]}`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_verses.py`:

```python
from app.server.data import db, indexes
from app.server.services.verses import verse_payload


def test_verse_payload_has_text_and_tokens():
    p = verse_payload(1, 1)
    assert p["ref"] == "1:1"
    assert "بِ" in p["text"]["uthmani"] or p["text"]["uthmani"]  # non-empty arabic
    assert len(p["tokens"]) >= 3
    assert all("position" in t and "form" in t for t in p["tokens"])


def test_verse_payload_missing_returns_none():
    assert verse_payload(1, 999) is None


def test_indexes_load():
    assert len(indexes.evidence()["index"]) == 6236
    assert len(indexes.communities()["nodes"]) == 114
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_verses.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app'`.

- [ ] **Step 3: Write the implementation**

Create the four empty `__init__.py` files listed above.

Create `app/server/data/db.py`:

```python
"""Read-only access to generated/monad.db."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[3] / "generated" / "monad.db"


def connect():
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def get_ayah(con, s, a):
    row = con.execute(
        "SELECT surah_number, ayah_number, text_uthmani, text_normalized "
        "FROM ayahs WHERE surah_number=? AND ayah_number=?", (s, a)).fetchone()
    if row is None:
        return None
    return {"ref": f"{s}:{a}", "surah": s, "ayah": a,
            "text_uthmani": row["text_uthmani"], "text_normalized": row["text_normalized"]}


def get_ayah_tokens(con, s, a):
    rows = con.execute(
        "SELECT w.word_position pos, w.form_arabic form, w.root_id, "
        "       r.root_arabic root_ar, r.root_buckwalter root_bw "
        "FROM words w LEFT JOIN roots r ON w.root_id = r.root_id "
        "WHERE w.surah_number=? AND w.ayah_number=? ORDER BY w.word_position", (s, a)).fetchall()
    return [{"position": x["pos"], "form": x["form"], "root_id": x["root_id"],
             "root_ar": x["root_ar"], "root_bw": x["root_bw"]} for x in rows]
```

Create `app/server/data/indexes.py`:

```python
"""Lazy, cached loaders for the generated JSON indexes."""
import json
from pathlib import Path

GEN = Path(__file__).resolve().parents[3] / "generated" / "layers"
EVID_PATH = GEN / "L8_interpret" / "evidence_index.json"
GRAPH_PATH = GEN / "L7_global" / "graph_communities.json"

_cache = {}


def evidence():
    if "evidence" not in _cache:
        _cache["evidence"] = json.loads(EVID_PATH.read_text(encoding="utf-8"))
    return _cache["evidence"]


def communities():
    if "communities" not in _cache:
        _cache["communities"] = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    return _cache["communities"]
```

Create `app/server/services/verses.py`:

```python
"""Verse payloads — text + tokens with roots. Evidence-only; no external glosses."""
from app.server.data import db


def verse_payload(s, a):
    con = db.connect()
    try:
        ayah = db.get_ayah(con, s, a)
        if ayah is None:
            return None
        tokens = db.get_ayah_tokens(con, s, a)
    finally:
        con.close()
    return {"ref": ayah["ref"], "surah": s, "ayah": a,
            "text": {"uthmani": ayah["text_uthmani"], "normalized": ayah["text_normalized"]},
            "tokens": tokens}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_verses.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add app/ tests/test_verses.py
git commit -m "feat: backend data layer + verses service"
```

---

### Task 3: Network + communities services

**Files:**
- Create: `app/server/services/network.py`
- Create: `app/server/services/communities.py`
- Test: `tests/test_network.py`

**Interfaces:**
- Consumes: `indexes.evidence()`, `indexes.communities()`, `db.get_ayah` (Task 2).
- Produces `app/server/services/network.py`: `interpret(s: int, a: int) -> list[dict]` — the evidence entries for `s:a`, each enriched with the explainer's `text_uthmani`: `[{"ayah": str, "weight": float, "cross_sura": bool, "shared_roots": [...], "text": str}]`. Returns `[]` for abstaining or out-of-range verses.
- Produces `app/server/services/communities.py`: `graph_communities() -> dict` (passes through the communities index); `sura_subgraph(s: int) -> dict` with shape `{"sura": int, "nodes": [{"ref": str, "ayah": int, "degree": int}], "edges": [{"source": str, "target": str, "weight": float}]}` — verse nodes of sura `s` and the intra-sura explanation edges among them.

- [ ] **Step 1: Write the failing test**

Create `tests/test_network.py`:

```python
from app.server.services.network import interpret
from app.server.services.communities import graph_communities, sura_subgraph


def test_interpret_canonical_pair():
    refs = interpret(2, 255)
    hit = next((r for r in refs if r["ayah"] == "7:97"), None)
    assert hit is not None
    assert any(sr["root_ar"] == "نوم" for sr in hit["shared_roots"])
    assert hit["text"]  # explainer text included


def test_interpret_abstention_is_empty_list():
    # 112:1 has no rare-root explainers in the validated demo
    assert interpret(112, 1) == []


def test_graph_communities_shape():
    g = graph_communities()
    assert len(g["nodes"]) == 114
    assert g["edges"]


def test_sura_subgraph_intra_only():
    sg = sura_subgraph(2)
    assert sg["sura"] == 2
    assert all(e["source"].startswith("2:") and e["target"].startswith("2:") for e in sg["edges"])
    assert sg["nodes"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_network.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.server.services.network'`.

- [ ] **Step 3: Write the implementation**

Create `app/server/services/network.py`:

```python
"""Self-interpretation: a verse's explaining verses + shared roots (evidence-only)."""
from app.server.data import db, indexes


def interpret(s, a):
    refs = indexes.evidence()["index"].get(f"{s}:{a}", [])
    if not refs:
        return []
    con = db.connect()
    try:
        out = []
        for r in refs:
            es, ea = (int(x) for x in r["ayah"].split(":"))
            ayah = db.get_ayah(con, es, ea)
            out.append({**r, "text": ayah["text_uthmani"] if ayah else ""})
        return out
    finally:
        con.close()
```

Create `app/server/services/communities.py`:

```python
"""Graph structure: sura constellation + per-sura verse subgraph."""
from collections import defaultdict

from app.server.data import indexes


def graph_communities():
    return indexes.communities()


def sura_subgraph(s):
    idx = indexes.evidence()["index"]
    prefix = f"{s}:"
    edges = []
    degree = defaultdict(int)
    seen_nodes = set()
    seen_edges = set()
    for ref, links in idx.items():
        if not ref.startswith(prefix):
            continue
        seen_nodes.add(ref)
        for link in links:
            tgt = link["ayah"]
            if not tgt.startswith(prefix):
                continue  # intra-sura only
            key = tuple(sorted((ref, tgt)))
            seen_nodes.add(tgt)
            degree[ref] += 1
            if key in seen_edges:
                continue
            seen_edges.add(key)
            edges.append({"source": key[0], "target": key[1], "weight": link["weight"]})
    nodes = [{"ref": r, "ayah": int(r.split(":")[1]), "degree": degree[r]}
             for r in sorted(seen_nodes, key=lambda r: int(r.split(":")[1]))]
    return {"sura": s, "nodes": nodes, "edges": edges}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_network.py -v`
Expected: 4 passed.
(If `test_interpret_abstention_is_empty_list` fails because 112:1 now has explainers under TOPN=12, replace it with a verse whose `index` entry is `[]` — find one via `python3 -c "import json;d=json.load(open('generated/layers/L8_interpret/evidence_index.json'))['index'];print(next(k for k,v in d.items() if not v))"` and use that ref in the test.)

- [ ] **Step 5: Commit**

```bash
git add app/server/services/network.py app/server/services/communities.py tests/test_network.py
git commit -m "feat: network + communities services"
```

---

### Task 4: HTTP server, router, and module registry

**Files:**
- Create: `app/server/modules/__init__.py`
- Create: `app/server/modules/self_interpret.py`
- Create: `app/server/main.py`
- Test: `tests/test_server.py`

**Interfaces:**
- Consumes: `verse_payload` (Task 2), `interpret`, `graph_communities`, `sura_subgraph` (Task 3).
- Produces `app/server/modules/__init__.py`: `MODULE_REGISTRY: list[dict]` — each `{"id": str, "title": str, "icon": str, "routes": [(method, pattern, handler)]}`. `pattern` is a regex string with named groups; `handler(match) -> (status:int, payload:obj)`.
- Produces `app/server/main.py`: `build_routes() -> list[tuple]` (core routes + every module's routes); `Handler` (a `BaseHTTPRequestHandler` subclass); `run(port=8000)`. Core routes: `GET /api/modules`, `GET /api/verse/{s}:{a}`, `GET /api/graph/communities`, `GET /api/graph/sura/{s}`. Static files under `app/web/` served from `/`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_server.py`:

```python
import json

from app.server.main import build_routes, dispatch


def call(method, path):
    routes = build_routes()
    return dispatch(routes, method, path)


def test_modules_endpoint_lists_self_interpret():
    status, payload = call("GET", "/api/modules")
    assert status == 200
    assert any(m["id"] == "self-interpret" for m in payload)


def test_verse_endpoint():
    status, payload = call("GET", "/api/verse/1:1")
    assert status == 200
    assert payload["ref"] == "1:1"


def test_interpret_endpoint_canonical():
    status, payload = call("GET", "/api/interpret/2:255")
    assert status == 200
    assert any(r["ayah"] == "7:97" for r in payload)


def test_communities_endpoint():
    status, payload = call("GET", "/api/graph/communities")
    assert status == 200
    assert len(payload["nodes"]) == 114


def test_unknown_route_404():
    status, _ = call("GET", "/api/nope")
    assert status == 404
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_server.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.server.main'`.

- [ ] **Step 3: Write the module + registry**

Create `app/server/modules/self_interpret.py`:

```python
"""Module 1: the self-interpretation engine — its module-specific routes."""
from app.server.services.network import interpret

MODULE = {"id": "self-interpret", "title": "خودتفسیر", "icon": "🕸"}


def _interpret(m):
    return 200, interpret(int(m["s"]), int(m["a"]))


ROUTES = [("GET", r"^/api/interpret/(?P<s>\d+):(?P<a>\d+)$", _interpret)]


def spec():
    return {**MODULE, "routes": ROUTES}
```

Create `app/server/modules/__init__.py`:

```python
"""Module registry. Add a module: create modules/<name>.py exposing spec(),
then append its spec() here. The server mounts every route automatically."""
from app.server.modules import self_interpret

MODULE_REGISTRY = [self_interpret.spec()]
```

- [ ] **Step 4: Write the server**

Create `app/server/main.py`:

```python
"""Zero-dependency HTTP server: JSON API + static frontend. Read-only."""
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from app.server.modules import MODULE_REGISTRY
from app.server.services.communities import graph_communities, sura_subgraph
from app.server.services.verses import verse_payload

WEB_DIR = Path(__file__).resolve().parents[1] / "web"
CONTENT_TYPES = {".html": "text/html", ".js": "text/javascript",
                 ".css": "text/css", ".json": "application/json"}


def _modules(m):
    return 200, [{"id": s["id"], "title": s["title"], "icon": s["icon"]} for s in MODULE_REGISTRY]


def _verse(m):
    p = verse_payload(int(m["s"]), int(m["a"]))
    return (200, p) if p else (404, {"error": "no such ayah"})


def _communities(m):
    return 200, graph_communities()


def _sura(m):
    return 200, sura_subgraph(int(m["s"]))


def build_routes():
    routes = [
        ("GET", r"^/api/modules$", _modules),
        ("GET", r"^/api/verse/(?P<s>\d+):(?P<a>\d+)$", _verse),
        ("GET", r"^/api/graph/communities$", _communities),
        ("GET", r"^/api/graph/sura/(?P<s>\d+)$", _sura),
    ]
    for spec in MODULE_REGISTRY:
        routes.extend(spec["routes"])
    return [(method, re.compile(pat), fn) for method, pat, fn in routes]


def dispatch(routes, method, path):
    for rmethod, rx, fn in routes:
        if rmethod == method:
            mt = rx.match(path)
            if mt:
                return fn(mt.groupdict())
    return 404, {"error": "not found"}


class Handler(BaseHTTPRequestHandler):
    routes = build_routes()

    def log_message(self, *a):
        pass

    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_static(self):
        rel = self.path.split("?")[0].lstrip("/") or "index.html"
        target = (WEB_DIR / rel).resolve()
        if WEB_DIR not in target.parents and target != WEB_DIR or not target.is_file():
            target = WEB_DIR / "index.html"
        if not target.is_file():
            self._send_json(404, {"error": "not found"})
            return
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPES.get(target.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path.startswith("/api/"):
            status, payload = dispatch(self.routes, "GET", path)
            self._send_json(status, payload)
        else:
            self._send_static()


def run(port=8000):
    print(f"Monad engine → http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    run()
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 -m pytest tests/test_server.py -v`
Expected: 5 passed.

- [ ] **Step 6: Commit**

```bash
git add app/server/modules/ app/server/main.py tests/test_server.py
git commit -m "feat: stdlib HTTP server, router, and module registry"
```

---

### Task 5: Frontend shell + API client

**Files:**
- Create: `app/web/index.html`
- Create: `app/web/src/lib/api.js`
- Create: `app/web/src/shell/registry.js`
- Create: `app/web/src/shell/layout.js`
- Create: `app/web/src/styles.css`
- Test: `tests/test_static.py` (server serves the shell) + manual smoke

**Interfaces:**
- Produces `registry.js`: `register(module)` where `module = {id, title, icon, mount(container, api)}`; `getModules() -> module[]`.
- Produces `api.js`: default-exported object `api` with `modules()`, `verse(ref)`, `interpret(ref)`, `communities()`, `sura(s)` — each returns a `Promise` of parsed JSON.
- Produces `layout.js`: on load, fetches `/api/modules`, builds the sidebar, and mounts the first registered module into `#canvas`. Consumes `registry.getModules()`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_static.py`:

```python
from app.server.main import WEB_DIR


def test_shell_files_exist_and_reference_entry():
    index = (WEB_DIR / "index.html")
    assert index.is_file(), "app/web/index.html must exist"
    html = index.read_text(encoding="utf-8")
    assert "shell/layout.js" in html
    assert (WEB_DIR / "src" / "lib" / "api.js").is_file()
    assert (WEB_DIR / "src" / "shell" / "registry.js").is_file()
    assert (WEB_DIR / "src" / "shell" / "layout.js").is_file()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_static.py -v`
Expected: FAIL on `app/web/index.html must exist`.

- [ ] **Step 3: Write the shell files**

Create `app/web/index.html`:

```html
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>مونـاد — موتور خودتفسیر قرآن</title>
  <link rel="stylesheet" href="/src/styles.css">
  <script type="importmap">
  {
    "imports": {
      "graphology": "https://cdn.jsdelivr.net/npm/graphology@0.25.4/dist/graphology.umd.min.js",
      "sigma": "https://cdn.jsdelivr.net/npm/sigma@3.0.0/dist/sigma.esm.min.js"
    }
  }
  </script>
</head>
<body>
  <aside id="sidebar"><div id="brand">مونـاد</div><nav id="modules"></nav></aside>
  <main id="canvas"></main>
  <script type="module" src="/src/shell/layout.js"></script>
</body>
</html>
```

Create `app/web/src/lib/api.js`:

```javascript
async function get(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${path} → ${res.status}`);
  return res.json();
}

const api = {
  modules: () => get("/api/modules"),
  verse: (ref) => get(`/api/verse/${ref}`),
  interpret: (ref) => get(`/api/interpret/${ref}`),
  communities: () => get("/api/graph/communities"),
  sura: (s) => get(`/api/graph/sura/${s}`),
};

export default api;
```

Create `app/web/src/shell/registry.js`:

```javascript
const _modules = [];

export function register(module) {
  if (!_modules.find((m) => m.id === module.id)) _modules.push(module);
}

export function getModules() {
  return _modules.slice();
}
```

Create `app/web/src/shell/layout.js`:

```javascript
import api from "../lib/api.js";
import { getModules, register } from "./registry.js";
import selfInterpret from "../modules/self-interpret/index.js";

register(selfInterpret);

const canvas = document.getElementById("canvas");
const nav = document.getElementById("modules");
let active = null;

function mount(module) {
  if (active === module.id) return;
  active = module.id;
  canvas.innerHTML = "";
  [...nav.children].forEach((b) => b.classList.toggle("active", b.dataset.id === module.id));
  module.mount(canvas, api);
}

function buildSidebar() {
  const mods = getModules();
  nav.innerHTML = "";
  mods.forEach((m) => {
    const btn = document.createElement("button");
    btn.dataset.id = m.id;
    btn.textContent = `${m.icon} ${m.title}`;
    btn.onclick = () => mount(m);
    nav.appendChild(btn);
  });
  if (mods.length) mount(mods[0]);
}

buildSidebar();
```

Create `app/web/src/styles.css`:

```css
* { box-sizing: border-box; }
body { margin: 0; display: flex; height: 100vh; font-family: "Vazirmatn", system-ui, sans-serif;
       background: #0d1117; color: #e6edf3; }
#sidebar { width: 200px; background: #161b22; padding: 16px; border-left: 1px solid #30363d;
           display: flex; flex-direction: column; gap: 8px; }
#brand { font-size: 22px; font-weight: 700; margin-bottom: 16px; color: #d2a8ff; }
#modules button { background: transparent; color: #e6edf3; border: 1px solid #30363d;
                  border-radius: 8px; padding: 10px; text-align: right; cursor: pointer; font-size: 15px; }
#modules button.active { background: #1f6feb33; border-color: #1f6feb; }
#canvas { flex: 1; position: relative; overflow: hidden; }
#graph { width: 100%; height: 100%; }
#panel { position: absolute; top: 0; left: 0; width: 380px; height: 100%; overflow-y: auto;
         background: #161b22ee; border-left: 1px solid #30363d; padding: 20px; transform: translateX(-100%);
         transition: transform .2s; }
#panel.open { transform: translateX(0); }
.verse-main { font-size: 26px; line-height: 2; text-align: center; margin-bottom: 8px; }
.explainer { border-top: 1px solid #30363d; padding: 12px 0; }
.explainer .ref { color: #58a6ff; cursor: pointer; font-weight: 700; }
.root-chip { display: inline-block; background: #d2a8ff22; border: 1px solid #d2a8ff66;
             border-radius: 6px; padding: 1px 8px; margin: 2px; font-size: 14px; }
.hl { color: #d2a8ff; font-weight: 700; }
.dim { opacity: .35; }
.crumbs { padding: 8px 12px; color: #8b949e; }
.crumbs a { color: #58a6ff; cursor: pointer; }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_static.py -v`
Expected: 1 passed.
(`layout.js` imports the Task 6 module; that file is created in Task 6. The Python test only checks files exist, so it passes now. Do not open the browser until Task 6 is done.)

- [ ] **Step 5: Commit**

```bash
git add app/web/index.html app/web/src/lib/api.js app/web/src/shell/ app/web/src/styles.css tests/test_static.py
git commit -m "feat: frontend shell, sidebar, module registry, API client"
```

---

### Task 6: Self-interpret module — graph + evidence panel (the centerpiece)

**Files:**
- Create: `app/web/src/modules/self-interpret/index.js`
- Create: `app/web/src/modules/self-interpret/graph.js`
- Create: `app/web/src/modules/self-interpret/evidence-panel.js`
- Test: manual UI smoke (documented below) + reuse `tests/test_server.py`

**Interfaces:**
- Consumes: `api` (Task 5), Sigma + graphology (CDN via importmap).
- Produces `index.js`: default export `{ id: "self-interpret", title: "خودتفسیر", icon: "🕸", mount(container, api) }`.
- Produces `graph.js`: `createGraph(container, api, onVerseFocus)` — renders the constellation; clicking a sura node loads its subgraph; clicking a verse node calls `onVerseFocus(ref)`. Returns `{ focusVerse(ref) }`.
- Produces `evidence-panel.js`: `createPanel(container)` returning `{ show(ref, api, onFollow), hide() }` where `onFollow(ref)` is called when the user clicks an explainer reference.

- [ ] **Step 1: Write the module entry**

Create `app/web/src/modules/self-interpret/index.js`:

```javascript
import { createGraph } from "./graph.js";
import { createPanel } from "./evidence-panel.js";

export default {
  id: "self-interpret",
  title: "خودتفسیر",
  icon: "🕸",
  mount(container, api) {
    container.innerHTML = `
      <div class="crumbs" id="crumbs">صورت‌فلکی سوره‌ها — روی یک سوره بزنید</div>
      <div id="graph"></div>
      <div id="panel"></div>`;
    const panel = createPanel(document.getElementById("panel"));
    const graph = createGraph(
      document.getElementById("graph"),
      api,
      (ref) => panel.show(ref, api, (next) => graph.focusVerse(next))
    );
  },
};
```

- [ ] **Step 2: Write the graph**

Create `app/web/src/modules/self-interpret/graph.js`:

```javascript
import Graph from "graphology";
import Sigma from "sigma";

const PURPLE = "#d2a8ff", BLUE = "#58a6ff", DIM = "#30363d";

export function createGraph(container, api, onVerseFocus) {
  let renderer = null;
  const crumbs = document.getElementById("crumbs");

  function render(graph) {
    if (renderer) renderer.kill();
    renderer = new Sigma(graph, container, { renderEdgeLabels: false });
    return renderer;
  }

  async function showConstellation() {
    const data = await api.communities();
    const g = new Graph();
    data.nodes.forEach((n) => g.addNode(`s${n.sura}`, {
      label: `${n.sura} ${n.name_ar}`, x: n.x, y: n.y,
      size: 3 + Math.sqrt(n.ayah_count), color: PURPLE, sura: n.sura, kind: "sura",
    }));
    data.edges.forEach((e, i) => {
      try { g.addEdgeWithKey(`e${i}`, `s${e.source}`, `s${e.target}`,
        { size: Math.max(0.3, Math.log(1 + e.weight) / 4), color: DIM }); } catch (_) {}
    });
    const r = render(g);
    r.on("clickNode", ({ node }) => showSura(g.getNodeAttribute(node, "sura")));
    crumbs.innerHTML = "صورت‌فلکی سوره‌ها — روی یک سوره بزنید";
  }

  async function showSura(s) {
    const data = await api.sura(s);
    const g = new Graph();
    const n = data.nodes.length || 1;
    data.nodes.forEach((nd, i) => {
      const ang = (2 * Math.PI * i) / n;
      g.addNode(nd.ref, { label: nd.ref, x: Math.cos(ang), y: Math.sin(ang),
        size: 2 + Math.sqrt(nd.degree), color: BLUE, kind: "verse" });
    });
    data.edges.forEach((e, i) => {
      try { g.addEdgeWithKey(`e${i}`, e.source, e.target,
        { size: Math.max(0.3, Math.log(1 + e.weight) / 4), color: DIM }); } catch (_) {}
    });
    const r = render(g);
    r.on("clickNode", ({ node }) => onVerseFocus(node));
    crumbs.innerHTML = `<a id="back">← صورت‌فلکی</a> &nbsp;/&nbsp; سوره ${s} — روی یک آیه بزنید`;
    document.getElementById("back").onclick = showConstellation;
  }

  async function focusVerse(ref) {
    const s = ref.split(":")[0];
    await showSura(Number(s));
    onVerseFocus(ref);
  }

  showConstellation();
  return { focusVerse };
}
```

- [ ] **Step 3: Write the evidence panel**

Create `app/web/src/modules/self-interpret/evidence-panel.js`:

```javascript
function highlight(text, rootForms) {
  // shared roots are surfaced as chips; the verse text itself is shown verbatim.
  return text;
}

export function createPanel(el) {
  function hide() { el.classList.remove("open"); el.innerHTML = ""; }

  async function show(ref, api, onFollow) {
    el.classList.add("open");
    el.innerHTML = `<div class="crumbs">${ref}</div><div>در حال بارگذاری…</div>`;
    const [verse, refs] = await Promise.all([api.verse(ref), api.interpret(ref)]);
    const head = `<button onclick="this.closest('#panel').classList.remove('open')"
                   style="float:left;background:none;border:none;color:#8b949e;cursor:pointer">✕</button>
      <div class="verse-main">${verse.text.uthmani}</div>
      <div class="crumbs">${ref}</div>`;
    if (!refs.length) {
      el.innerHTML = head + `<p class="dim">هیچ آیه‌ی روشن‌گری با شاهدِ ریشه‌ی مشترک یافت نشد — امتناع.</p>`;
      return;
    }
    const body = refs.map((r) => {
      const chips = r.shared_roots.map((sr) =>
        `<span class="root-chip">${sr.root_ar}</span>`).join("");
      const tag = r.cross_sura ? "بینا‌سوره‌ای" : "درون‌سوره‌ای";
      return `<div class="explainer">
        <span class="ref" data-ref="${r.ayah}">${r.ayah}</span>
        <span class="dim"> · ${tag} · وزن ${r.weight}</span>
        <div class="verse-main" style="font-size:20px">${r.text}</div>
        <div>ریشه‌های مشترک: ${chips}</div></div>`;
    }).join("");
    el.innerHTML = head + body;
    el.querySelectorAll(".ref").forEach((node) =>
      node.addEventListener("click", () => onFollow(node.dataset.ref)));
  }

  return { show, hide };
}
```

- [ ] **Step 4: Run the full backend test suite**

Run: `python3 -m pytest tests/ -v`
Expected: all tests pass (verses, network, server, static).

- [ ] **Step 5: Manual UI smoke test**

Run: `python3 -m app.server.main`
Then open `http://localhost:8000` in a browser and verify:
1. The constellation renders 114 purple sura nodes with edges.
2. Clicking a sura node expands to its verse nodes (blue) with intra-sura edges; breadcrumb shows a "← صورت‌فلکی" back link that returns to the constellation.
3. Clicking a verse node opens the evidence panel with the verse text, its explainer verses, weights, cross/intra tags, and shared-root chips.
4. Navigate to sura 2, click verse 2:255 → panel lists 7:97 with a نوم root chip.
5. Clicking an explainer reference in the panel re-focuses the graph on that verse's sura and re-opens the panel for it ("follow the thread").
6. Pick a verse known to abstain (e.g. the ref printed by the abstention one-liner in Task 3 Step 4) → panel shows the explicit "امتناع" message, not an empty silence.

Stop the server with Ctrl-C.

- [ ] **Step 6: Commit**

```bash
git add app/web/src/modules/self-interpret/
git commit -m "feat: self-interpret module — 3-tier graph + evidence panel"
```

---

### Task 7: Extensibility proof + run docs

**Files:**
- Create: `tests/test_extensibility.py`
- Create: `app/README.md`

**Interfaces:**
- Consumes: `MODULE_REGISTRY`, `build_routes` (Task 4), `register`/`getModules` contract (Task 5).

- [ ] **Step 1: Write the test that proves the two-file contract**

Create `tests/test_extensibility.py`:

```python
"""A new module must mount with no change to the core (server, shell, services)."""
import re

from app.server.main import build_routes, dispatch


def test_adding_a_module_spec_adds_its_routes():
    # Simulate a second module's spec() — the same shape modules/__init__.py collects.
    def _ping(m):
        return 200, {"pong": True}

    fake = {"id": "atlas", "title": "اطلس ریشه", "icon": "📚",
            "routes": [("GET", r"^/api/atlas/ping$", _ping)]}
    routes = [(meth, re.compile(pat), fn) for meth, pat, fn in fake["routes"]]
    status, payload = dispatch(routes, "GET", "/api/atlas/ping")
    assert status == 200 and payload["pong"] is True


def test_core_routes_are_registry_driven():
    # Every module in the registry contributes its routes to build_routes().
    from app.server.modules import MODULE_REGISTRY
    routes = build_routes()
    patterns = [rx.pattern for _, rx, _ in routes]
    for spec in MODULE_REGISTRY:
        for _, pat, _ in spec["routes"]:
            assert pat in patterns, f"route {pat} from module {spec['id']} not mounted"
```

- [ ] **Step 2: Run test to verify it passes**

Run: `python3 -m pytest tests/test_extensibility.py -v`
Expected: 2 passed.

- [ ] **Step 3: Write the run/extend docs**

Create `app/README.md`:

```markdown
# Monad Engine — local web app

موتور خودتفسیر قرآن: نقشه‌ی شبکه + پنل شاهد. اولین ماژولِ یک سکوی توسعه‌پذیر.

## اجرا

```bash
python3 build/build_evidence_index.py      # یک‌بار: ساخت ایندکس شاهد + گراف
python3 -m app.server.main                 # سرور: http://localhost:8000
```

تست‌ها: `python3 -m pytest tests/ -v`
وارسیِ بازتولیدپذیری ساخت: `python3 build/validate_evidence_index.py`

## افزودن یک ماژول جدید (قرارداد دو-فایلی)

1. **بک‌اند:** `app/server/modules/<name>.py` بساز که `spec()` را با شکلِ
   `{"id","title","icon","routes":[(method, regex, handler)]}` برمی‌گرداند؛ سپس آن را در
   `app/server/modules/__init__.py` به `MODULE_REGISTRY` بیفزای. هندلر امضای
   `handler(match_groupdict) -> (status, payload)` دارد و فقط از `services/*` داده می‌گیرد.
2. **فرانت:** `app/web/src/modules/<name>/index.js` بساز که
   `{id,title,icon,mount(container, api)}` صادر می‌کند؛ آن را در `app/web/src/shell/layout.js`
   `register(...)` کن. پوسته خودکار در نوار کناری نشانش می‌دهد.

هسته (سرور، روتر، پوسته، سرویس‌ها) دست‌نخورده می‌ماند. `tests/test_extensibility.py`
این قرارداد را تضمین می‌کند.

## اصل صداقت

هیچ ترجمه/تفسیر/معنای بیرونی نمایش داده نمی‌شود — تنها متنِ آیات، ریشه‌های مشترک، و
وزنِ رابطه. آیاتِ بی‌شاهد صریحاً «امتناع» علامت می‌خورند.
```

- [ ] **Step 4: Run the whole suite once more**

Run: `python3 -m pytest tests/ -v`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add tests/test_extensibility.py app/README.md
git commit -m "feat: extensibility test + run/extend docs"
```

---

## Self-Review

**Spec coverage:**
- §1 evidence-only → Global Constraints + Task 3 (interpret returns only text/roots/weights) + Task 6 panel (chips + verbatim text, abstention shown). ✓
- §2 architecture (server/services/modules + web shell) → Tasks 2–6. ✓
- §3 data layer + API endpoints (modules, verse, interpret, graph/communities, graph/sura) → Tasks 2–4. ✓
- §4 build step (full evidence + shared roots, validated method, byte-identical validate, canonical pairs) → Task 1. ✓
- §5 3-tier graph + honesty cues (edge weight, shared-root justification, abstention dimming) → Task 6. ✓ (verse-level layout computed client-side per sura; constellation precomputed — matches "instant + deterministic" intent.)
- §6 testing (canonical pair, cross_sura, abstention empty, 114 nodes, static serve, frontend smoke) → Tasks 1–6. ✓
- §7 module extensibility (two-file add) → Task 7. ✓
- §8 success criteria → covered by Task 6 smoke (1,2,5) and Tasks 1/7 (3,4). ✓

**Placeholder scan:** No TBD/TODO; every code step is complete. `highlight()` in evidence-panel.js intentionally returns text verbatim (chips carry the shared-root evidence) — documented, not a stub.

**Type consistency:** `spec()` shape `{id,title,icon,routes}` consistent across `self_interpret.py`, `__init__.py`, `main.build_routes`, and `test_extensibility.py`. `interpret()` return shape (adds `text`) consistent between Task 3 and Task 6 consumption. `evidence_index.json` shape consistent between Task 1 producer and Task 2/3 consumers. Node/edge key shapes (`s<sura>` vs verse `ref`) consistent within graph.js.

**Note for executor:** Task 4/5 tests do not exercise the browser; Sigma/graphology rendering is verified only by the Task 6 manual smoke. That is the one non-automated gate — do not skip it.
