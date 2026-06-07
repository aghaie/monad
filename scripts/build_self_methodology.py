#!/usr/bin/env python3
"""
Monad — Phase Z: Quran Self-Method Discovery Engine (FALSIFICATION STUDY)
========================================================================

Question: does the Quran, within its own text, describe a STABLE INTERNAL METHOD for
reaching knowledge — and does that conclusion survive rigorous controls?

This phase treats the Phase-Q ("integrative method") and Phase-X ("directed epistemic
pipeline") conclusions as HYPOTHESES to be attacked, not findings to preserve. It is run
in the shadow of Phase P, whose verdict (NON_PREDICTIVE) showed the discovered structure,
though real, carries no predictive power beyond lexical frequency — and whose directional
(S2) model was the weakest of all. Phase Z therefore asks the narrower, decisive question
those phases never tested: does the *directional method* survive frequency, surah-length,
and mushaf-order nulls plus bootstrap and subsampling?

Everything is rebuilt from the corpus (Phase-1 DB) only. No outputs from Q or X are read.
No tafsir, translation, hadith, philosophy, or external model. The verdict (YES/NO/
PARTIAL) is computed mechanically from pre-registered thresholds. A negative or partial
outcome is a first-class result.
"""

import argparse
import hashlib
import json
import math
import random
import sqlite3
import statistics
from collections import defaultdict
from itertools import combinations
from pathlib import Path

METHOD = "self-methodology-1.0"
ROUND = 6

# ── pre-registered constants (fixed before any run) ────────────────────────────────
SEED = 20260607
WINDOW = 1                 # cross-ayah adjacency window (same surah)
MIN_SUPPORT = 8            # minimum directed observations for a candidate edge
DIR_MARGIN = 0.6           # directionality margin (reference)
K_FREQ_NULL = 100          # node-level configuration-null realizations (existence test)
K_ORDER_NULL = 100         # mushaf-order-null realizations (directionality test)
K_BOOT = 200               # bootstrap resamples (directionality CI)
K_SUB = 50                 # subsampling repeats per fraction
SUBSAMPLE_FRACS = [0.10, 0.20, 0.40]
THRESH_SUPPORT = [5, 8, 12, 20]
THRESH_DIR = [0.55, 0.60, 0.65]
# pre-registered verdict thresholds
NO_EXIST_FRAC = 0.10       # below this fraction of edges surviving the EXISTENCE null -> NO
YES_DIR_FRAC = 0.50        # at/above this fraction of edges surviving DIRECTIONALITY -> YES candidate
YES_BACKBONE_NODES = 6     # connected directional-survivor backbone size for YES

# ── epistemic vocabulary (corpus root_arabic; the spec's own list; roles opaque) ───
NODES = {
    "observe":      ["نظر", "بصر", "راي", "شهد"],   # دیدن / مشاهده
    "listen":       ["سمع"],                         # شنیدن
    "read":         ["قرا", "تلو"],                  # خواندن
    "reflect":      ["عقل"],                         # تعقل
    "ponder":       ["دبر"],                         # تدبر
    "think":        ["فكر"],                         # تفکر
    "remember":     ["ذكر"],                         # تذکر
    "ask":          ["سال"],                         # سؤال
    "judge":        ["حكم"],                         # داوری
    "knowledge":    ["علم"],                         # علم / یادگیری / تعلیم
    "understanding":["فقه", "فهم", "نهي", "لبب"],    # فهم
    "certainty":    ["يقن"],                         # یقین
    "conjecture":   ["ظنن"],                         # ظن
    "guidance":     ["هدي"],                         # هدایت
    "misguidance":  ["ضلل"],                         # گمراهی
    "denial":       ["كذب", "كفر"],                  # تکذیب
}
COGNITION = ["reflect", "ponder", "think", "remember", "knowledge", "understanding"]
KNOW_OUT = ["knowledge", "certainty", "guidance", "understanding"]
IGN_OUT = ["misguidance", "denial", "conjecture"]

PROHIBITIONS = [
    "no tafsir", "no translation as evidence", "no hadith", "no kalam", "no philosophy",
    "no mysticism", "no human sciences", "no theories of cognition", "no external model",
    "no prior-phase outputs (Q/X/P JSON never read)", "Q/X conclusions are hypotheses not findings",
    "no proposition accepted for resembling a human theory", "units/roots stay opaque",
    "verdict from pre-registered thresholds only", "negative/partial outcome is first-class",
    "prior phases never rebuilt",
]


def r(x):
    return round(float(x), ROUND)


def write_json(path, obj):
    text = json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=1)
    Path(path).write_text(text, encoding="utf-8")
    return len(text.encode("utf-8"))


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pct(xs, q):
    xs = sorted(xs)
    if not xs:
        return 0.0
    i = min(len(xs) - 1, max(0, int(q * len(xs))))
    return xs[i]


# ── directed-flow computation (within-ayah word order + cross-ayah adjacency) ──────

def compute_flows(present, pos, surah_order, nodes):
    """present: ayah->frozenset(node) ; pos: ayah->{node:rank} (lower=earlier) ;
    surah_order: surah->ordered list of ayahs (for adjacency). Returns flow[(a,b)] =
    count of 'a precedes/predicts b' over ordered node pairs."""
    flow = defaultdict(int)
    # within-ayah word order
    for ay, P in present.items():
        if len(P) < 2:
            continue
        rp = pos[ay]
        Pl = sorted(P)
        for a, b in combinations(Pl, 2):
            ra, rb = rp[a], rp[b]
            if ra < rb:
                flow[(a, b)] += 1
            elif rb < ra:
                flow[(b, a)] += 1
    # cross-ayah adjacency
    for s, seq in surah_order.items():
        for i in range(len(seq) - WINDOW):
            for d in range(1, WINDOW + 1):
                if i + d >= len(seq):
                    break
                A = present.get(seq[i])
                B = present.get(seq[i + d])
                if not A or not B:
                    continue
                for a in A:
                    for b in B:
                        if a != b:
                            flow[(a, b)] += 1
    return flow


def edge_stats(flow, nodes):
    """Return oriented candidate edges (support>=MIN_SUPPORT) as dict
    (src,dst)->{fwd,bwd,support,dir}."""
    out = {}
    for a, b in combinations(sorted(nodes), 2):
        fwd = flow.get((a, b), 0)
        bwd = flow.get((b, a), 0)
        sup = fwd + bwd
        if sup < MIN_SUPPORT:
            continue
        if fwd >= bwd:
            out[(a, b)] = {"fwd": fwd, "bwd": bwd, "support": sup, "dir": fwd / sup}
        else:
            out[(b, a)] = {"fwd": bwd, "bwd": fwd, "support": sup, "dir": bwd / sup}
    return out


class SelfMethodologyEngine:
    def __init__(self, db, out):
        self.db = Path(db)
        self.out_dir = Path(out)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def load(self):
        print("  loading corpus (rebuilt from DB; no Q/X outputs) …")
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        root_ar = {ar: rid for rid, ar in cur.execute("SELECT root_id, root_arabic FROM roots")}
        rid2ar = {rid: ar for ar, rid in root_ar.items()}
        # node membership: root_id -> node name
        self.node_names = sorted(NODES)
        self.node_idx = {n: i for i, n in enumerate(self.node_names)}
        root2node = {}
        for n, roots in NODES.items():
            for ar in roots:
                if ar in root_ar:
                    root2node[root_ar[ar]] = self.node_idx[n]
        # per ayah: surah, node->min word_position
        seq_surah = {}
        node_minpos = defaultdict(dict)
        for s, seq, wp, rid in cur.execute(
                "SELECT a.surah_number, a.ayah_sequential, m.word_position, m.root_id "
                "FROM ayahs a JOIN morphology m "
                "ON a.surah_number=m.surah_number AND a.ayah_number=m.ayah_number "
                "WHERE m.root_id IS NOT NULL"):
            ni = root2node.get(rid)
            if ni is None:
                continue
            seq_surah[seq] = s
            d = node_minpos[seq]
            if ni not in d or wp < d[ni]:
                d[ni] = wp
        conn.close()
        self.seqs = sorted(node_minpos)
        self.seq_surah = seq_surah
        # presence + order-rank (rank from sorted min positions)
        self.present = {}
        self.pos = {}
        for ay in self.seqs:
            d = node_minpos[ay]
            self.present[ay] = frozenset(d)
            order = sorted(d, key=lambda n: d[n])
            self.pos[ay] = {n: i for i, n in enumerate(order)}
        # surah -> ordered ayah list
        self.surah_order = defaultdict(list)
        for ay in self.seqs:
            self.surah_order[self.seq_surah[ay]].append(ay)
        for s in self.surah_order:
            self.surah_order[s].sort()
        # node document frequency (ayah count)
        self.node_df = defaultdict(int)
        for ay in self.seqs:
            for n in self.present[ay]:
                self.node_df[n] += 1
        # ayah length (distinct roots, for surah-length control) — separate query
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        alen = defaultdict(set)
        for seq, rid in cur.execute(
                "SELECT a.ayah_sequential, m.root_id FROM ayahs a JOIN morphology m "
                "ON a.surah_number=m.surah_number AND a.ayah_number=m.ayah_number "
                "WHERE m.root_id IS NOT NULL"):
            alen[seq].add(rid)
        conn.close()
        self.ayah_len = {seq: len(s) for seq, s in alen.items()}
        n_nodes_present = len([n for n in self.node_idx.values() if self.node_df.get(n, 0) > 0])
        print(f"    ayahs_with_method_nodes={len(self.seqs)} nodes={n_nodes_present}/{len(NODES)}")

    # ── real graph ─────────────────────────────────────────────────────────────────

    def build_real(self):
        flow = compute_flows(self.present, self.pos, self.surah_order, self.node_idx.values())
        self.real_edges = edge_stats(flow, self.node_idx.values())
        self.real_flow = flow
        return self.real_edges

    def _name(self, i):
        return self.node_names[i]

    # ── PHASE A: vocabulary discovery ───────────────────────────────────────────────

    def discovery(self):
        print("  A — methodological vocabulary …")
        ent = []
        for n, idx in sorted(self.node_idx.items(), key=lambda kv: kv[0]):
            ent.append({"node": n, "roots": [a for a in NODES[n]],
                        "ayah_count": self.node_df.get(idx, 0)})
        ent.sort(key=lambda e: -e["ayah_count"])
        # node co-occurrence field (how many node pairs co-occur >= MIN_SUPPORT)
        npairs = len(self.real_edges)
        return {"method": METHOD,
                "definition": "the Quran's own epistemic vocabulary (the spec's list), rebuilt from corpus roots",
                "nodes": ent, "n_nodes": len(ent),
                "candidate_edges": npairs,
                "finding": ("%d epistemic nodes; %d node pairs co-occur at support>=%d — the "
                            "vocabulary forms a connected associative field (tested for reality in I)"
                            % (len(ent), npairs, MIN_SUPPORT))}

    # ── PHASE B/C/G: chains, prerequisites, architecture (the directed graph) ────────

    def chains(self):
        print("  B/C/G — directed chains + architecture …")
        edges = [{"from": self._name(a), "to": self._name(b), **v}
                 for (a, b), v in self.real_edges.items()]
        for e in edges:
            e["dir"] = r(e["dir"])
        edges.sort(key=lambda e: (-e["dir"], -e["support"]))
        # net outflow per node
        net = defaultdict(float)
        for (a, b), v in self.real_edges.items():
            w = v["fwd"] - v["bwd"]
            net[a] += w
            net[b] -= w
        order = sorted(self.node_idx.values(), key=lambda n: -net.get(n, 0))
        # prerequisites of cognition (in-edges) / outcomes (out-edges)
        cog_idx = {self.node_idx[c] for c in COGNITION if c in self.node_idx}
        pre, post = defaultdict(list), defaultdict(list)
        for (a, b), v in self.real_edges.items():
            if b in cog_idx:
                pre[self._name(b)].append({"from": self._name(a), "dir": r(v["dir"]), "support": v["support"]})
            if a in cog_idx:
                post[self._name(a)].append({"to": self._name(b), "dir": r(v["dir"]), "support": v["support"]})
        return {"method": METHOD, "n_edges": len(edges), "edges": edges,
                "net_outflow_order": [{"node": self._name(n), "net": r(net.get(n, 0))} for n in order],
                "prerequisites_of_cognition": {k: sorted(v, key=lambda x: -x["support"]) for k, v in pre.items()},
                "outcomes_of_cognition": {k: sorted(v, key=lambda x: -x["support"]) for k, v in post.items()},
                "finding": ("directed method graph: %d edges; source-most node '%s', sink-most '%s'"
                            % (len(edges), self._name(order[0]), self._name(order[-1])))}

    def obstacles(self):
        print("  D — obstacles …")
        ign = {self.node_idx[n] for n in IGN_OUT if n in self.node_idx}
        rows = []
        for (a, b), v in self.real_edges.items():
            if b in ign:
                rows.append({"from": self._name(a), "to": self._name(b),
                             "dir": r(v["dir"]), "support": v["support"]})
        rows.sort(key=lambda x: -x["support"])
        return {"method": METHOD,
                "definition": "structures flowing INTO not-knowing / misguidance / denial / conjecture",
                "edges_into_ignorance": rows,
                "finding": ("%d directed edges flow into ignorance-states (misguidance/denial/conjecture)"
                            % len(rows))}

    def outcomes(self):
        print("  E — outcomes …")
        kn = {self.node_idx[n] for n in KNOW_OUT if n in self.node_idx}
        rows = []
        for (a, b), v in self.real_edges.items():
            if a in kn:
                rows.append({"from": self._name(a), "to": self._name(b),
                             "dir": r(v["dir"]), "support": v["support"]})
        rows.sort(key=lambda x: -x["support"])
        return {"method": METHOD,
                "definition": "structures flowing OUT OF knowledge / certainty / guidance / understanding",
                "edges_from_knowledge": rows,
                "finding": "%d directed edges flow out of knowledge-states" % len(rows)}

    def cycles(self):
        print("  F — cycles …")
        # build adjacency of oriented edges, find simple directed cycles up to length 4
        adj = defaultdict(set)
        for (a, b) in self.real_edges:
            adj[a].add(b)
        found = set()
        nodes = sorted(adj)
        def dfs(start, cur, path):
            if len(path) > 4:
                return
            for nx in sorted(adj[cur]):
                if nx == start and len(path) >= 2:
                    found.add(tuple(sorted(path)))
                elif nx not in path and nx > start:
                    dfs(start, nx, path + [nx])
        for s in nodes:
            dfs(s, s, [s])
        cyc = [[self._name(i) for i in c] for c in sorted(found)]
        return {"method": METHOD,
                "definition": "directed cycles (length 2-4) in the method graph",
                "n_cycles": len(cyc), "cycles": cyc,
                "finding": ("%d directed cycles among epistemic nodes" % len(cyc))}

    # ── PHASE I: falsification battery ──────────────────────────────────────────────

    def _freq_null_presence(self, rng):
        """Node-level configuration null: preserve each ayah's node-count and each node's
        df via curveball swaps. Returns present-like dict + random order ranks."""
        rows = {ay: set(self.present[ay]) for ay in self.seqs}
        keys = self.seqs
        nnz = sum(len(rows[a]) for a in keys)
        swaps = 5 * nnz
        for _ in range(swaps):
            i = keys[rng.randrange(len(keys))]
            j = keys[rng.randrange(len(keys))]
            if i == j:
                continue
            Ri, Rj = rows[i], rows[j]
            oi = Ri - Rj
            oj = Rj - Ri
            if not oi or not oj:
                continue
            a = sorted(oi)[rng.randrange(len(oi))]
            b = sorted(oj)[rng.randrange(len(oj))]
            Ri.discard(a); Ri.add(b)
            Rj.discard(b); Rj.add(a)
        present = {ay: frozenset(rows[ay]) for ay in keys}
        pos = {ay: {n: k for k, n in enumerate(rng.sample(sorted(present[ay]), len(present[ay])))}
               for ay in keys}
        return present, pos

    def _order_null(self, rng):
        """Mushaf-order null: preserve co-occurrence (presence) but destroy ALL order —
        random word order within ayahs AND shuffled ayah order within surahs."""
        pos = {ay: {n: k for k, n in enumerate(rng.sample(sorted(self.present[ay]), len(self.present[ay])))}
               for ay in self.seqs}
        surah_order = {}
        for s, seq in self.surah_order.items():
            sq = seq[:]
            rng.shuffle(sq)
            surah_order[s] = sq
        return pos, surah_order

    def _word_order_null(self, rng):
        pos = {ay: {n: k for k, n in enumerate(rng.sample(sorted(self.present[ay]), len(self.present[ay])))}
               for ay in self.seqs}
        return pos, self.surah_order

    def _ayah_order_null(self, rng):
        surah_order = {}
        for s, seq in self.surah_order.items():
            sq = seq[:]
            rng.shuffle(sq)
            surah_order[s] = sq
        return self.pos, surah_order

    def _edge_d_under(self, present, pos, surah_order):
        flow = compute_flows(present, pos, surah_order, self.node_idx.values())
        out = {}
        for (a, b), v in self.real_edges.items():
            fwd = flow.get((a, b), 0)
            bwd = flow.get((b, a), 0)
            sup = fwd + bwd
            out[(a, b)] = (fwd / sup if sup else 0.5, sup)
        return out

    def falsification(self):
        print("  I — falsification battery (frequency / order / length nulls) …")
        edges = list(self.real_edges)
        # frequency-null existence: support distribution
        rng = random.Random(SEED + 11)
        freq_sup = {e: [] for e in edges}
        for _ in range(K_FREQ_NULL):
            present, pos = self._freq_null_presence(rng)
            du = self._edge_d_under(present, pos, self.surah_order)
            for e in edges:
                freq_sup[e].append(du[e][1])
        # mushaf-order-null directionality: d distribution (co-occurrence preserved)
        rng = random.Random(SEED + 22)
        order_d = {e: [] for e in edges}
        for _ in range(K_ORDER_NULL):
            pos, so = self._order_null(rng)
            du = self._edge_d_under(self.present, pos, so)
            for e in edges:
                order_d[e].append(du[e][0])
        # word-order-only and ayah-order-only (reported separately)
        rng = random.Random(SEED + 33)
        word_d = {e: [] for e in edges}
        for _ in range(K_ORDER_NULL):
            pos, so = self._word_order_null(rng)
            du = self._edge_d_under(self.present, pos, so)
            for e in edges:
                word_d[e].append(du[e][0])
        rng = random.Random(SEED + 44)
        ayah_d = {e: [] for e in edges}
        for _ in range(K_ORDER_NULL):
            pos, so = self._ayah_order_null(rng)
            du = self._edge_d_under(self.present, pos, so)
            for e in edges:
                ayah_d[e].append(du[e][0])
        # surah-length control: split ayahs by length median, recompute orientation
        med = statistics.median(self.ayah_len[a] for a in self.seqs)
        short = {a for a in self.seqs if self.ayah_len[a] <= med}
        def half_d(subset):
            pres = {a: self.present[a] for a in subset}
            so = {s: [a for a in seq if a in subset] for s, seq in self.surah_order.items()}
            flow = compute_flows(pres, {a: self.pos[a] for a in subset}, so, self.node_idx.values())
            out = {}
            for (a, b), v in self.real_edges.items():
                fwd = flow.get((a, b), 0); bwd = flow.get((b, a), 0); sup = fwd + bwd
                out[(a, b)] = (fwd / sup if sup else 0.5, sup)
            return out
        d_short = half_d(short)
        d_long = half_d(set(self.seqs) - short)

        results = []
        for e in edges:
            v = self.real_edges[e]
            sup_p95 = pct(freq_sup[e], 0.95)
            od_p95 = pct(order_d[e], 0.95)
            wd_p95 = pct(word_d[e], 0.95)
            ad_p95 = pct(ayah_d[e], 0.95)
            exists = v["support"] > sup_p95                      # beats frequency-null support
            directional = v["dir"] > od_p95                      # beats mushaf-order null
            length_stable = d_short[e][0] > 0.5 and d_long[e][0] > 0.5
            results.append({
                "edge": f"{self._name(e[0])}->{self._name(e[1])}",
                "real_support": v["support"], "real_dir": r(v["dir"]),
                "freq_null_support_p95": r(sup_p95), "exists_beyond_frequency": exists,
                "order_null_dir_p95": r(od_p95), "directional_beyond_order": directional,
                "word_order_null_dir_p95": r(wd_p95), "ayah_order_null_dir_p95": r(ad_p95),
                "dir_short_ayahs": r(d_short[e][0]), "dir_long_ayahs": r(d_long[e][0]),
                "length_stable": length_stable,
            })
        results.sort(key=lambda x: (-x["real_dir"], -x["real_support"]))
        self.falsif = {res["edge"]: res for res in results}
        n_exist = sum(1 for x in results if x["exists_beyond_frequency"])
        n_dir = sum(1 for x in results if x["directional_beyond_order"])
        return {"method": METHOD,
                "n_candidate_edges": len(edges),
                "nulls": {"frequency": K_FREQ_NULL, "mushaf_order": K_ORDER_NULL,
                          "word_order": K_ORDER_NULL, "ayah_order": K_ORDER_NULL,
                          "surah_length": "median split"},
                "results": results,
                "edges_existing_beyond_frequency": n_exist,
                "edges_directional_beyond_order": n_dir,
                "finding": ("of %d candidate edges, %d co-occur beyond the frequency null but only "
                            "%d keep their DIRECTION beyond the mushaf-order null"
                            % (len(edges), n_exist, n_dir))}

    # ── PHASE H: stability (bootstrap, subsampling, threshold sweep) ────────────────

    def stability(self):
        print("  H — stability (bootstrap / subsampling / threshold sweep) …")
        edges = list(self.real_edges)
        # bootstrap CI of directionality
        rng = random.Random(SEED + 55)
        boot_d = {e: [] for e in edges}
        seqs = self.seqs
        n = len(seqs)
        for _ in range(K_BOOT):
            samp = [seqs[rng.randrange(n)] for _ in range(n)]
            pres = {}
            cnt = defaultdict(int)
            for a in samp:
                cnt[a] += 1
            # weighted recompute: approximate by including each sampled ayah (dup allowed)
            so = defaultdict(list)
            pos = {}
            present = {}
            # build a multiset graph by counting flows with multiplicity
            flow = defaultdict(int)
            for a in samp:
                P = self.present[a]
                rp = self.pos[a]
                for x, y in combinations(sorted(P), 2):
                    if rp[x] < rp[y]:
                        flow[(x, y)] += 1
                    elif rp[y] < rp[x]:
                        flow[(y, x)] += 1
            for e in edges:
                a, b = e
                fwd = flow.get((a, b), 0); bwd = flow.get((b, a), 0); s = fwd + bwd
                boot_d[e].append(fwd / s if s else 0.5)
        # subsampling persistence
        sub = {e: {f: 0 for f in SUBSAMPLE_FRACS} for e in edges}
        rng = random.Random(SEED + 66)
        for f in SUBSAMPLE_FRACS:
            keep_n = int((1 - f) * n)
            for _ in range(K_SUB):
                subset = set(rng.sample(seqs, keep_n))
                pres = {a: self.present[a] for a in subset}
                so = {s: [a for a in seq if a in subset] for s, seq in self.surah_order.items()}
                flow = compute_flows(pres, {a: self.pos[a] for a in subset}, so, self.node_idx.values())
                for e in edges:
                    a, b = e
                    fwd = flow.get((a, b), 0); bwd = flow.get((b, a), 0); s = fwd + bwd
                    if s and fwd / s > 0.5:
                        sub[e][f] += 1
        # threshold sweep: number of candidate edges at each (support,dir)
        sweep = []
        for ms in THRESH_SUPPORT:
            for dm in THRESH_DIR:
                c = sum(1 for v in self.real_edges.values() if v["support"] >= ms and v["dir"] >= dm)
                sweep.append({"min_support": ms, "dir_margin": dm, "n_edges": c})
        rows = []
        for e in edges:
            bd = sorted(boot_d[e])
            lo = pct(bd, 0.025); hi = pct(bd, 0.975)
            ci_excludes_half = lo > 0.5
            persist = {f: r(sub[e][f] / K_SUB) for f in SUBSAMPLE_FRACS}
            min_persist = min(persist.values())
            rows.append({"edge": f"{self._name(e[0])}->{self._name(e[1])}",
                         "real_dir": r(self.real_edges[e]["dir"]),
                         "boot_ci_lo": r(lo), "boot_ci_hi": r(hi),
                         "dir_ci_excludes_0.5": ci_excludes_half,
                         "subsample_persistence": persist,
                         "stable": ci_excludes_half and min_persist >= 0.9})
        rows.sort(key=lambda x: -x["real_dir"])
        self.stab = {x["edge"]: x for x in rows}
        n_stable = sum(1 for x in rows if x["stable"])
        return {"method": METHOD,
                "bootstrap": K_BOOT, "subsampling_fracs": SUBSAMPLE_FRACS, "k_sub": K_SUB,
                "results": rows, "threshold_sweep": sweep,
                "n_stable_directionality": n_stable,
                "finding": ("%d/%d edges have bootstrap directionality CI excluding 0.5 AND persist "
                            "(>=90%%) under subsampling" % (n_stable, len(rows)))}

    # ── PHASE J: verdict ────────────────────────────────────────────────────────────

    def verdict(self, falsif, stab):
        print("  J — verdict …")
        edges = [e["edge"] for e in falsif["results"]]
        n = len(edges)
        exist = {e["edge"]: e["exists_beyond_frequency"] for e in falsif["results"]}
        direc = {e["edge"]: e["directional_beyond_order"] for e in falsif["results"]}
        lenstab = {e["edge"]: e["length_stable"] for e in falsif["results"]}
        stable = {x["edge"]: x["stable"] for x in stab["results"]}
        # FULL survivor = exists beyond freq AND directional beyond order AND length-stable AND bootstrap/subsample-stable
        survivors = [e for e in edges if exist[e] and direc[e] and lenstab[e] and stable.get(e, False)]
        exist_frac = sum(exist.values()) / n if n else 0.0
        dir_frac = sum(1 for e in edges if direc[e] and stable.get(e, False)) / n if n else 0.0
        # connected backbone among survivors (undirected connectivity)
        adj = defaultdict(set)
        for e in survivors:
            a, b = e.split("->")
            adj[a].add(b); adj[b].add(a)
        seen = set()
        best = 0
        for start in list(adj):
            if start in seen:
                continue
            stack = [start]; comp = set()
            while stack:
                x = stack.pop()
                if x in comp:
                    continue
                comp.add(x); seen.add(x)
                stack.extend(adj[x] - comp)
            best = max(best, len(comp))
        # pre-registered verdict
        if exist_frac < NO_EXIST_FRAC:
            v = "NO"
        elif dir_frac >= YES_DIR_FRAC and best >= YES_BACKBONE_NODES:
            v = "YES"
        else:
            v = "PARTIAL"
        return {"method": METHOD,
                "verdict": v,
                "n_candidate_edges": n,
                "existence_survivor_fraction": r(exist_frac),
                "directionality_survivor_fraction": r(dir_frac),
                "full_survivor_edges": survivors,
                "n_full_survivors": len(survivors),
                "largest_connected_backbone_nodes": best,
                "pre_registered_thresholds": {
                    "NO_EXIST_FRAC": NO_EXIST_FRAC, "YES_DIR_FRAC": YES_DIR_FRAC,
                    "YES_BACKBONE_NODES": YES_BACKBONE_NODES, "MIN_SUPPORT": MIN_SUPPORT,
                    "K_FREQ_NULL": K_FREQ_NULL, "K_ORDER_NULL": K_ORDER_NULL,
                    "K_BOOT": K_BOOT, "SEED": SEED},
                "comparison": {
                    "Q_claim": "integrative method (observe signs -> reason -> remember) — accepted in Phase Q on raw counts, NO frequency/order nulls",
                    "X_claim": "directed epistemic pipeline (perceive -> reflect -> know -> certainty) — Phase X used reverse-sequence + Meccan/Medinan only, NO frequency/length/order nulls",
                    "P_result": "NON_PREDICTIVE — directional structure (S2) was the weakest predictor; structure real but not predictive beyond frequency",
                    "Z_test": "subjects the directional method to frequency + surah-length + mushaf-order nulls + bootstrap + subsampling"},
                "interpretation": (
                    "YES = a connected directional method survives ALL controls; "
                    "PARTIAL = the epistemic vocabulary co-occurs beyond chance (real associative field) "
                    "but its DIRECTIONALITY (the 'pipeline'/sequence claim of Q and X) does not robustly "
                    "survive the order nulls; NO = even the vocabulary co-occurrence is not beyond frequency")}

    def manifest(self, output_bytes, summary):
        return {"method": METHOD,
                "constants": {"SEED": SEED, "WINDOW": WINDOW, "MIN_SUPPORT": MIN_SUPPORT,
                              "DIR_MARGIN": DIR_MARGIN, "K_FREQ_NULL": K_FREQ_NULL,
                              "K_ORDER_NULL": K_ORDER_NULL, "K_BOOT": K_BOOT, "K_SUB": K_SUB,
                              "SUBSAMPLE_FRACS": SUBSAMPLE_FRACS,
                              "NO_EXIST_FRAC": NO_EXIST_FRAC, "YES_DIR_FRAC": YES_DIR_FRAC,
                              "YES_BACKBONE_NODES": YES_BACKBONE_NODES,
                              "nodes": list(NODES.keys())},
                "input_sha256": {"monad.db": sha256_file(self.db)},
                "output_bytes": output_bytes,
                "prohibitions_observed": PROHIBITIONS,
                "verdict": summary["verdict"],
                "totals": summary}

    def run(self):
        self.load()
        self.build_real()
        # compute everything first, then fold verdict in, then write once
        graph = {"method": METHOD, **self.discovery()}
        ch = self.chains()
        prereq = {"method": METHOD,
                  "prerequisites_of_cognition": ch["prerequisites_of_cognition"],
                  "outcomes_of_cognition": ch["outcomes_of_cognition"]}
        obs = self.obstacles()
        outc = self.outcomes()
        cyc = self.cycles()
        fal = self.falsification()
        stab = self.stability()
        verd = self.verdict(fal, stab)
        graph["verdict"] = verd
        fal["verdict"] = verd

        products = {
            "methodology_graph.json": graph,
            "methodology_chains.json": ch,
            "methodology_prerequisites.json": prereq,
            "methodology_obstacles.json": obs,
            "methodology_outcomes.json": outc,
            "methodology_cycles.json": cyc,
            "methodology_falsification.json": fal,
            "methodology_stability.json": stab,
        }
        declared = list(products)
        output_bytes = {}
        for name in declared:
            output_bytes[name] = write_json(self.out_dir / name, products[name])
            print(f"    wrote {name} ({output_bytes[name]} bytes)")

        summary = {
            "verdict": verd["verdict"],
            "n_candidate_edges": verd["n_candidate_edges"],
            "existence_survivor_fraction": verd["existence_survivor_fraction"],
            "directionality_survivor_fraction": verd["directionality_survivor_fraction"],
            "n_full_survivors": verd["n_full_survivors"],
            "largest_backbone": verd["largest_connected_backbone_nodes"],
            "edges_existing_beyond_frequency": fal["edges_existing_beyond_frequency"],
            "edges_directional_beyond_order": fal["edges_directional_beyond_order"],
            "n_stable_directionality": stab["n_stable_directionality"],
        }
        man = self.manifest(output_bytes, summary)
        output_bytes["methodology_manifest.json"] = write_json(
            self.out_dir / "methodology_manifest.json", man)
        print("    wrote methodology_manifest.json")
        self.summary = summary
        self.verdict_obj = verd
        return summary


def sha_len(path):
    return len(Path(path).read_bytes())


def main():
    ap = argparse.ArgumentParser(description="Monad Phase Z — Quran Self-Method Discovery (falsification)")
    ap.add_argument("--db", default="generated/monad.db")
    ap.add_argument("--out", default="generated/self_methodology")
    args = ap.parse_args()
    print(f"Monad Phase Z — Quran Self-Method Discovery Engine ({METHOD})")
    eng = SelfMethodologyEngine(args.db, args.out)
    summary = eng.run()
    print("  done.")
    print(f"  VERDICT: {summary['verdict']}")
    print(f"  summary: {json.dumps(summary, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
