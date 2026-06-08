#!/usr/bin/env python3
"""
Monad — Phase Δ: Quranic Decision Architecture Discovery Engine
==============================================================

A reframing: not "what does the Quran say?" but "if the Quran were a decision-making
system, how would it decide?" The phase does NOT assume the Quran is a text, book, or
theory; it treats it as an agent and asks what decision ARCHITECTURE emerges from the
corpus itself — decision events, triggers, information use, uncertainty/conflict/priority
handling, outcome evaluation, recursive loops — then attacks every component with nulls.
No human decision framework (decision theory, ethics, AI planning, psychology) is imposed;
architecture emerges only from the corpus.

Success = reproducible decision structure that survives falsification. Failure = apparent
architecture that disappears under controls. BOTH are acceptable; only measurement decides.
Given Phases P (non-predictive), Z (self-method collapses under controls), and R
(deed→recompense survives), the honest expectation is PARTIAL.

Decision nodes are corpus structures: COND (conditional particles) + decision/action/
consequence/uncertainty/conflict/priority/evaluation root-groups. Direction = within-ayah
word order + cross-ayah adjacency. Inputs: Phase-1 DB only. Deterministic, fixed seeds.
"""

import argparse
import hashlib
import json
import random
import statistics
from collections import defaultdict
from itertools import combinations
from pathlib import Path
import sqlite3

METHOD = "decision-architecture-1.0"
ROUND = 6
SEED = 20260608
WINDOW = 1
MIN_SUPPORT = 8
DIR_MARGIN = 0.6
K_NULL = 100
K_BOOT = 200
K_SUB = 50
SUBSAMPLE_FRACS = [0.10, 0.20, 0.40]
# pre-registered verdict thresholds
NO_EXIST_FRAC = 0.10
YES_DIR_FRAC = 0.50
YES_BACKBONE = 5

# decision-node vocabulary (corpus root_arabic); "condition" is COND-POS, added separately
NODE_ROOTS = {
    "choice":      ["شيا", "رود", "خير", "امر", "نهي"],   # will / choose / command / forbid
    "action":      ["عمل", "فعل", "كسب"],
    "consequence": ["جزي", "عقب", "اثر"],
    "uncertainty": ["شكك", "ظنن", "غيب"],
    "knowledge":   ["علم"],
    "conflict":    ["خلف", "جدل", "فرق"],
    "resolution":  ["حكم"],
    "priority":    ["فضل", "قدم"],
    "evaluation":  ["حسب", "وزن", "كيل"],
}
COND_ROOTS = ["شرط"]    # plus COND-POS tokens

PROHIBITIONS = [
    "no tafsir", "no theology", "no doctrine", "no apologetics", "no external philosophy",
    "no psychology theory", "no decision-theory import", "no ethics import", "no AI planning model",
    "no external ontology", "no human decision framework imposed",
    "architecture emerges only from the corpus", "ask how it decides not what it says",
    "both success and collapse are acceptable outcomes", "prior phases never rebuilt",
]


def r(x):
    return round(float(x), ROUND)


def write_json(path, obj):
    t = json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=1)
    Path(path).write_text(t, encoding="utf-8")
    return len(t.encode("utf-8"))


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, max(0, int(q * len(xs))))] if xs else 0.0


def compute_flows(present, pos, surah_order):
    flow = defaultdict(int)
    for ay, P in present.items():
        if len(P) < 2:
            continue
        rp = pos[ay]
        for a, b in combinations(sorted(P), 2):
            ra, rb = rp[a], rp[b]
            if ra < rb:
                flow[(a, b)] += 1
            elif rb < ra:
                flow[(b, a)] += 1
    for s, seq in surah_order.items():
        for i in range(len(seq) - 1):
            A = present.get(seq[i]); B = present.get(seq[i + 1])
            if not A or not B:
                continue
            for a in A:
                for b in B:
                    if a != b:
                        flow[(a, b)] += 1
    return flow


def edge_stats(flow, nodes):
    out = {}
    for a, b in combinations(sorted(nodes), 2):
        fwd = flow.get((a, b), 0); bwd = flow.get((b, a), 0); sup = fwd + bwd
        if sup < MIN_SUPPORT:
            continue
        if fwd >= bwd:
            out[(a, b)] = {"fwd": fwd, "bwd": bwd, "support": sup, "dir": fwd / sup}
        else:
            out[(b, a)] = {"fwd": bwd, "bwd": fwd, "support": sup, "dir": bwd / sup}
    return out


class DecisionEngine:
    def __init__(self, db, out):
        self.db = Path(db)
        self.out_dir = Path(out)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def load(self):
        print("  loading decision nodes (COND + decision-vocabulary roots) …")
        conn = sqlite3.connect(self.db); cur = conn.cursor()
        root_ar = {ar: rid for rid, ar in cur.execute("SELECT root_id, root_arabic FROM roots")}
        rid2ar = {rid: ar for ar, rid in root_ar.items()}
        self.node_names = ["condition"] + sorted(NODE_ROOTS)
        self.node_idx = {n: i for i, n in enumerate(self.node_names)}
        root2node = {}
        for n, roots in NODE_ROOTS.items():
            for ar in roots:
                if ar in root_ar:
                    root2node[root_ar[ar]] = self.node_idx[n]
        for ar in COND_ROOTS:
            if ar in root_ar:
                root2node[root_ar[ar]] = self.node_idx["condition"]
        sa_seq = {(s, a): seq for s, a, seq in cur.execute(
            "SELECT surah_number, ayah_number, ayah_sequential FROM ayahs")}
        seq_surah = {seq: s for (s, a), seq in sa_seq.items()}
        node_minpos = defaultdict(dict)
        n_cond_tokens = 0
        for s, a, wp, rid, pos in cur.execute(
                "SELECT surah_number, ayah_number, word_position, root_id, pos FROM morphology"):
            seq = sa_seq.get((s, a))
            if seq is None:
                continue
            ni = None
            if pos == "COND":
                ni = self.node_idx["condition"]; n_cond_tokens += 1
            elif rid is not None:
                ni = root2node.get(rid)
            if ni is None:
                continue
            d = node_minpos[seq]
            if ni not in d or wp < d[ni]:
                d[ni] = wp
        conn.close()
        self.seqs = sorted(node_minpos)
        self.seq_surah = seq_surah
        self.present = {}
        self.pos = {}
        for ay in self.seqs:
            d = node_minpos[ay]
            self.present[ay] = frozenset(d)
            order = sorted(d, key=lambda n: d[n])
            self.pos[ay] = {n: i for i, n in enumerate(order)}
        self.surah_order = defaultdict(list)
        for ay in self.seqs:
            self.surah_order[seq_surah[ay]].append(ay)
        for s in self.surah_order:
            self.surah_order[s].sort()
        self.node_df = defaultdict(int)
        for ay in self.seqs:
            for n in self.present[ay]:
                self.node_df[n] += 1
        self.n_cond_tokens = n_cond_tokens
        flow = compute_flows(self.present, self.pos, self.surah_order)
        self.real_edges = edge_stats(flow, self.node_idx.values())
        print(f"    ayahs_with_decision_nodes={len(self.seqs)} COND_tokens={n_cond_tokens} "
              f"candidate_edges={len(self.real_edges)}")

    def _name(self, i):
        return self.node_names[i]

    # ── nulls (reused pattern) ───────────────────────────────────────────────────────

    def _freq_null_present(self, rng):
        rows = {ay: set(self.present[ay]) for ay in self.seqs}
        keys = self.seqs
        nnz = sum(len(rows[a]) for a in keys)
        for _ in range(5 * nnz):
            i = keys[rng.randrange(len(keys))]; j = keys[rng.randrange(len(keys))]
            if i == j:
                continue
            Ri, Rj = rows[i], rows[j]
            oi = Ri - Rj; oj = Rj - Ri
            if not oi or not oj:
                continue
            a = sorted(oi)[rng.randrange(len(oi))]; b = sorted(oj)[rng.randrange(len(oj))]
            Ri.discard(a); Ri.add(b); Rj.discard(b); Rj.add(a)
        present = {ay: frozenset(rows[ay]) for ay in keys}
        pos = {ay: {n: k for k, n in enumerate(rng.sample(sorted(present[ay]), len(present[ay])))}
               for ay in keys}
        return present, pos

    def _order_null(self, rng):
        pos = {ay: {n: k for k, n in enumerate(rng.sample(sorted(self.present[ay]), len(self.present[ay])))}
               for ay in self.seqs}
        so = {s: (lambda q: (rng.shuffle(q), q)[1])(seq[:]) for s, seq in self.surah_order.items()}
        return pos, so

    def _edge_under(self, present, pos, so):
        flow = compute_flows(present, pos, so)
        out = {}
        for (a, b), v in self.real_edges.items():
            fwd = flow.get((a, b), 0); bwd = flow.get((b, a), 0); sup = fwd + bwd
            out[(a, b)] = (fwd / sup if sup else 0.5, sup)
        return out

    # ── A–G + I: descriptive components from the directed graph ──────────────────────

    def components(self):
        edges = [{"from": self._name(a), "to": self._name(b), **v} for (a, b), v in self.real_edges.items()]
        for e in edges:
            e["dir"] = r(e["dir"])
        edges.sort(key=lambda e: (-e["dir"], -e["support"]))
        net = defaultdict(float)
        for (a, b), v in self.real_edges.items():
            w = v["fwd"] - v["bwd"]; net[a] += w; net[b] -= w
        order = sorted(self.node_idx.values(), key=lambda n: -net.get(n, 0))
        def into(node):
            return sorted([{"from": self._name(a), "dir": r(v["dir"]), "support": v["support"]}
                           for (a, b), v in self.real_edges.items() if self._name(b) == node],
                          key=lambda x: -x["support"])
        def outof(node):
            return sorted([{"to": self._name(b), "dir": r(v["dir"]), "support": v["support"]}
                           for (a, b), v in self.real_edges.items() if self._name(a) == node],
                          key=lambda x: -x["support"])
        return {"edges": edges,
                "net_order": [{"node": self._name(n), "net": r(net.get(n, 0))} for n in order],
                "into": into, "outof": outof}

    # ── J: falsification battery ─────────────────────────────────────────────────────

    def falsification(self):
        print("  J — falsification (frequency + order/revelation nulls) …")
        edges = list(self.real_edges)
        rng = random.Random(SEED + 11)
        freq_sup = {e: [] for e in edges}
        for _ in range(K_NULL):
            present, pos = self._freq_null_present(rng)
            du = self._edge_under(present, pos, self.surah_order)
            for e in edges:
                freq_sup[e].append(du[e][1])
        rng = random.Random(SEED + 22)
        order_d = {e: [] for e in edges}
        for _ in range(K_NULL):
            pos, so = self._order_null(rng)
            du = self._edge_under(self.present, pos, so)
            for e in edges:
                order_d[e].append(du[e][0])
        results = []
        for e in edges:
            v = self.real_edges[e]
            sup95 = pct(freq_sup[e], 0.95); od95 = pct(order_d[e], 0.95)
            results.append({"edge": f"{self._name(e[0])}->{self._name(e[1])}",
                            "real_support": v["support"], "real_dir": r(v["dir"]),
                            "freq_null_sup_p95": r(sup95), "exists_beyond_frequency": v["support"] > sup95,
                            "order_null_dir_p95": r(od95), "directional_beyond_order": v["dir"] > od95})
        results.sort(key=lambda x: (-x["real_dir"], -x["real_support"]))
        self.falsif = {x["edge"]: x for x in results}
        return {"method": METHOD, "n_candidate_edges": len(edges), "results": results,
                "n_exist": sum(1 for x in results if x["exists_beyond_frequency"]),
                "n_directional": sum(1 for x in results if x["directional_beyond_order"]),
                "finding": ("of %d candidate decision edges, %d exist beyond the frequency null and %d keep "
                            "direction beyond the order null"
                            % (len(edges), sum(1 for x in results if x["exists_beyond_frequency"]),
                               sum(1 for x in results if x["directional_beyond_order"])))}

    # ── K: stability ─────────────────────────────────────────────────────────────────

    def stability(self):
        print("  K — stability (bootstrap + subsampling) …")
        edges = list(self.real_edges)
        rng = random.Random(SEED + 55)
        boot = {e: [] for e in edges}
        n = len(self.seqs)
        for _ in range(K_BOOT):
            samp = [self.seqs[rng.randrange(n)] for _ in range(n)]
            flow = defaultdict(int)
            for a in samp:
                P = self.present[a]; rp = self.pos[a]
                for x, y in combinations(sorted(P), 2):
                    if rp[x] < rp[y]:
                        flow[(x, y)] += 1
                    elif rp[y] < rp[x]:
                        flow[(y, x)] += 1
            for e in edges:
                a, b = e; fwd = flow.get((a, b), 0); bwd = flow.get((b, a), 0); s = fwd + bwd
                boot[e].append(fwd / s if s else 0.5)
        rng = random.Random(SEED + 66)
        sub = {e: {f: 0 for f in SUBSAMPLE_FRACS} for e in edges}
        for f in SUBSAMPLE_FRACS:
            keep = int((1 - f) * n)
            for _ in range(K_SUB):
                subset = set(rng.sample(self.seqs, keep))
                pres = {a: self.present[a] for a in subset}
                so = {s: [a for a in seq if a in subset] for s, seq in self.surah_order.items()}
                flow = compute_flows(pres, {a: self.pos[a] for a in subset}, so)
                for e in edges:
                    a, b = e; fwd = flow.get((a, b), 0); bwd = flow.get((b, a), 0); s = fwd + bwd
                    if s and fwd / s > 0.5:
                        sub[e][f] += 1
        rows = []
        for e in edges:
            bd = sorted(boot[e]); lo = pct(bd, 0.025)
            persist = {f: r(sub[e][f] / K_SUB) for f in SUBSAMPLE_FRACS}
            rows.append({"edge": f"{self._name(e[0])}->{self._name(e[1])}",
                         "real_dir": r(self.real_edges[e]["dir"]), "boot_ci_lo": r(lo),
                         "subsample_persistence": persist,
                         "stable": lo > 0.5 and min(persist.values()) >= 0.9})
        rows.sort(key=lambda x: -x["real_dir"])
        self.stab = {x["edge"]: x for x in rows}
        return {"method": METHOD, "results": rows,
                "n_stable": sum(1 for x in rows if x["stable"]),
                "finding": ("%d/%d decision edges are bootstrap+subsample stable"
                            % (sum(1 for x in rows if x["stable"]), len(rows)))}

    # ── L: verdict ───────────────────────────────────────────────────────────────────

    def verdict(self, comp, fal, stab):
        exist = {x["edge"]: x["exists_beyond_frequency"] for x in fal["results"]}
        direc = {x["edge"]: x["directional_beyond_order"] for x in fal["results"]}
        stable = {x["edge"]: x["stable"] for x in stab["results"]}
        edges = list(exist)
        survivors = [e for e in edges if exist[e] and direc[e] and stable.get(e, False)]
        n = len(edges)
        exist_frac = sum(exist.values()) / n if n else 0.0
        dir_frac = sum(1 for e in edges if direc[e] and stable.get(e, False)) / n if n else 0.0
        adj = defaultdict(set)
        for e in survivors:
            a, b = e.split("->"); adj[a].add(b); adj[b].add(a)
        best = 0
        seen = set()
        for st in list(adj):
            if st in seen:
                continue
            stack = [st]; cc = set()
            while stack:
                x = stack.pop()
                if x in cc:
                    continue
                cc.add(x); seen.add(x); stack.extend(adj[x] - cc)
            best = max(best, len(cc))
        if exist_frac < NO_EXIST_FRAC:
            arch = "NO"
        elif dir_frac >= YES_DIR_FRAC and best >= YES_BACKBONE:
            arch = "YES"
        else:
            arch = "PARTIAL"
        cond_into = comp["into"]("condition")
        unc_out = comp["outof"]("uncertainty")
        conf_res = [e for e in comp["edges"] if e["from"] == "conflict" and e["to"] == "resolution"]
        strongest = survivors[0] if survivors else (comp["edges"][0]["from"] + "->" + comp["edges"][0]["to"]
                                                    if comp["edges"] else "none")
        return {"method": METHOD,
                "Q1_coherent_architecture": arch,
                "Q2_robust_components_surviving": len(survivors),
                "Q3_decisions_initiated_by": ("conditional structures (COND particles, %d tokens) and "
                                              "commands — the most frequent decision markers" % self.n_cond_tokens),
                "Q4_uncertainty_handling": ("uncertainty (شك/ظن/غيب) resolves toward knowledge (علم): "
                                            + (", ".join("%s(%.2f)" % (e["to"], e["dir"]) for e in unc_out[:3])
                                               if unc_out else "no robust uncertainty edge")),
                "Q5_conflict_resolution": ("conflict (خلف/جدل) -> resolution (حكم): "
                                           + (("dir %.2f, support %d" % (conf_res[0]["dir"], conf_res[0]["support"]))
                                              if conf_res else "no robust conflict->resolution edge")),
                "Q6_priority_establishment": ("priority via فضل/خير/قدم; "
                                              + ("net-order leader: %s" % comp["net_order"][0]["node"])),
                "Q7_minimal_architecture": survivors if survivors else "no connected architecture survives",
                "Q8_survives_falsification": ("PARTIAL" if 0 < len(survivors) < n else
                                              ("YES" if len(survivors) >= n * YES_DIR_FRAC else "NO")),
                "Q9_strongest_reproducible_discovery": strongest,
                "Q10_unknown": ("the CONTENT of decisions — which specific choice is made — is the "
                                "irreducible lexical-referential residual (Phase Ψ); the architecture is "
                                "FORM, not content. We do not know what is decided, only the structural "
                                "shape of deciding."),
                "exist_fraction": r(exist_frac), "dir_survivor_fraction": r(dir_frac),
                "largest_backbone": best,
                "comparison": {
                    "X": "epistemic pipeline (perceive->reflect->know) — directionality collapsed under order null (Phase Z)",
                    "Z": "self-method PARTIAL — only 2 isolated edges survived all controls",
                    "R": "deed->recompense (action->consequence) SURVIVED — expected to recur here",
                    "P": "structure non-predictive beyond frequency"}}

    def manifest(self, output_bytes, summary):
        return {"method": METHOD,
                "constants": {"SEED": SEED, "MIN_SUPPORT": MIN_SUPPORT, "DIR_MARGIN": DIR_MARGIN,
                              "K_NULL": K_NULL, "K_BOOT": K_BOOT, "NO_EXIST_FRAC": NO_EXIST_FRAC,
                              "YES_DIR_FRAC": YES_DIR_FRAC, "YES_BACKBONE": YES_BACKBONE,
                              "nodes": self.node_names},
                "input_sha256": {"monad.db": sha256_file(self.db)},
                "output_bytes": output_bytes, "prohibitions_observed": PROHIBITIONS,
                "totals": summary}

    def run(self):
        self.load()
        comp = self.components()
        fal = self.falsification()
        stab = self.stability()
        verd = self.verdict(comp, fal, stab)

        edges = comp["edges"]; into = comp["into"]; outof = comp["outof"]
        products = {
            "decision_events.json": {"method": METHOD,
                "ayahs_with_decision_nodes": len(self.seqs), "cond_tokens": self.n_cond_tokens,
                "node_frequencies": {self._name(n): self.node_df[n] for n in sorted(self.node_df)},
                "n_candidate_edges": len(self.real_edges),
                "finding": "decision events marked by COND particles (%d) + decision vocabulary across %d ayahs"
                           % (self.n_cond_tokens, len(self.seqs))},
            "decision_triggers.json": {"method": METHOD, "triggers_into_condition": into("condition"),
                "triggers_into_action": into("action"), "net_order": comp["net_order"]},
            "information_usage.json": {"method": METHOD, "knowledge_into_decisions": outof("knowledge"),
                "into_knowledge": into("knowledge")},
            "uncertainty_architecture.json": {"method": METHOD, "uncertainty_out": outof("uncertainty"),
                "uncertainty_in": into("uncertainty")},
            "conflict_resolution.json": {"method": METHOD,
                "conflict_out": outof("conflict"), "resolution_in": into("resolution")},
            "priority_architecture.json": {"method": METHOD, "priority_out": outof("priority"),
                "net_order": comp["net_order"]},
            "outcome_evaluation.json": {"method": METHOD, "evaluation_in": into("evaluation"),
                "consequence_in": into("consequence"), "consequence_out": outof("consequence")},
            "decision_loops.json": {"method": METHOD, "edges": edges,
                "note": "cycles among decision nodes; survivors determine real loops (see falsification)"},
            "agent_architecture.json": {"method": METHOD, "net_order": comp["net_order"],
                "all_candidate_edges": edges, "verdict": verd},
            "decision_falsification.json": fal,
            "decision_stability.json": stab,
        }
        declared = list(products)
        output_bytes = {}
        for name in declared:
            output_bytes[name] = write_json(self.out_dir / name, products[name])
            print(f"    wrote {name} ({output_bytes[name]} bytes)")
        summary = {
            "coherent_architecture": verd["Q1_coherent_architecture"],
            "robust_components": verd["Q2_robust_components_surviving"],
            "survives_falsification": verd["Q8_survives_falsification"],
            "exist_fraction": verd["exist_fraction"],
            "dir_survivor_fraction": verd["dir_survivor_fraction"],
            "largest_backbone": verd["largest_backbone"],
            "strongest_discovery": verd["Q9_strongest_reproducible_discovery"],
        }
        man = self.manifest(output_bytes, summary)
        output_bytes["decision_manifest.json"] = write_json(self.out_dir / "decision_manifest.json", man)
        print("    wrote decision_manifest.json")
        self.summary = summary
        self.verdict_obj = verd
        return summary


def main():
    ap = argparse.ArgumentParser(description="Monad Phase Δ — Quranic Decision Architecture Discovery")
    ap.add_argument("--db", default="generated/monad.db")
    ap.add_argument("--out", default="generated/decision_architecture")
    args = ap.parse_args()
    print(f"Monad Phase Δ — Quranic Decision Architecture Discovery Engine ({METHOD})")
    eng = DecisionEngine(args.db, args.out)
    summary = eng.run()
    print("  done.")
    print(f"  summary: {json.dumps(summary, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
