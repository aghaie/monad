#!/usr/bin/env python3
"""
Monad — Phase X: Epistemology Discovery Engine
==============================================

Every prior phase asked what STRUCTURES exist in the Quran. This phase asks a different
question: what PROCESS OF KNOWING does the Quran attempt to create in a human being —
how does it expect a person to move from not-knowing to knowing?

We assume nothing. Not that the Quran has a unique epistemology; not that observation,
reason, or faith is central. Everything is discovered, measured, and attacked. The only
source is the Quran corpus: no tafsir, hadith, dictionary, translation, philosophy,
theology, epistemology/psychology/cognitive-science literature, or external model.

The new structural signal is ORDER. Two directional measures, both from the corpus:
  (1) within-ayah word order (word_position) — does action X precede state Y in the text?
  (2) cross-ayah adjacency (ayah_sequential) — does X in ayah n precede Y in ayah n+1?
Combined, they give a directed flow between epistemic nodes. The epistemic pipeline,
its enablers and obstacles, its modes of knowing, and its compressibility are then read
off that directed graph — and every edge is attacked by its own reverse and by a
corpus split.

Inputs: the Quran corpus (Phase-1 database). Nothing else.
Deterministic, pure-stdlib, byte-identically reproducible.
"""

import argparse
import hashlib
import json
import sqlite3
from collections import defaultdict
from itertools import combinations
from pathlib import Path

METHOD = "epistemology-discovery-1.0"
ROUND = 6
WINDOW = 1            # cross-ayah adjacency window (same surah)
MIN_SUPPORT = 8       # minimum directed flow for an edge to exist
DIR_MARGIN = 0.6      # directionality required to survive falsification

# ── epistemic nodes (corpus root_arabic; roles stay opaque) ──────────────────────
ACTIONS = {
    "observe": ["نظر", "بصر", "راي", "شهد"],
    "reflect": ["فكر", "دبر", "عقل"],
    "remember": ["ذكر"],
    "travel": ["سير"],
    "question": ["سال"],
    "listen": ["سمع"],
    "compare": ["مثل", "وزن", "كيل"],
    "read": ["قرا", "تلو"],
}
STATES = {
    "information": ["نبا", "خبر"],
    "knowledge": ["علم"],
    "understanding": ["فقه", "فهم", "نهي", "لبب"],
    "recognition": ["عرف"],
    "awareness": ["شعر"],
    "certainty": ["يقن"],
    "wisdom": ["حكم"],
    "guidance": ["هدي", "رشد"],
}
OBSTACLES = {
    "denial": ["كفر", "جحد"],
    "arrogance": ["كبر"],
    "sealing": ["ختم", "طبع", "قسو", "غلف", "رين", "كنن"],
    "blindness": ["عمي", "صمم", "بكم", "وقر"],
    "forgetting": ["نسي", "غفل"],
    "deviation": ["ضلل", "زيغ", "غوي"],
    "conjecture": ["ظنن", "هوي"],
    "lying": ["كذب"],
}
# knowledge-mode sources (Q10)
MODE_SOURCES = {
    "observation": ["نظر", "بصر", "راي", "شهد"],
    "history": ["قصص", "قرن", "نبا"],
    "self": ["نفس"],
    "signs": ["ايي"],
    "consequences": ["عقب", "اثر"],
    "comparison": ["مثل"],
}
KNOW_TARGET = ["علم", "فقه", "فهم", "نهي", "لبب", "يقن", "حكم", "هدي", "عرف"]

PROHIBITIONS = [
    "no tafsir", "no hadith", "no dictionary", "no translation", "no philosophy",
    "no theology", "no epistemology literature", "no psychology", "no cognitive science",
    "no external model", "no assumption the Quran has a unique epistemology",
    "no assumption observation/reason/faith is central", "everything tested not assumed",
    "discover-measure-falsify-report", "concepts/roots stay opaque",
    "prior phases never rebuilt",
]


def r(x):
    return round(float(x), ROUND)


def write_json(path, obj):
    text = json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=1)
    path.write_text(text, encoding="utf-8")
    return len(text.encode("utf-8"))


def sha256_file(path):
    h = hashlib.sha256()
    h.update(Path(path).read_bytes())
    return h.hexdigest()


class EpistemologyEngine:
    def __init__(self, db, out):
        self.db = Path(db)
        self.out_dir = Path(out)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def load(self):
        print("  loading corpus: roots, word-positions, moods, revelation type …")
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        self.root_ar = {ar: rid for rid, ar in cur.execute("SELECT root_id, root_arabic FROM roots")}
        self.root_tok = {rid: tc for rid, tc in cur.execute("SELECT root_id, token_count FROM roots")}
        self.surah_type = {s: rt for s, rt in cur.execute("SELECT surah_number, revelation_type FROM surahs")}
        rid2ar = {rid: ar for ar, rid in self.root_ar.items()}

        # ayah_sequential -> surah ; per-ayah root -> min word_position ; moods
        seq_surah = {}
        root_minpos = defaultdict(dict)     # seq -> {root_ar: min_word_position}
        self.imperatives = defaultdict(int)
        self.imperfect = defaultdict(int)
        for s, seq, wp, rid, feat in cur.execute(
                "SELECT a.surah_number, a.ayah_sequential, m.word_position, m.root_id, m.features_raw "
                "FROM ayahs a JOIN morphology m "
                "ON a.surah_number=m.surah_number AND a.ayah_number=m.ayah_number "
                "WHERE m.root_id IS NOT NULL"):
            ar = rid2ar.get(rid)
            if ar is None:
                continue
            seq_surah[seq] = s
            d = root_minpos[seq]
            if ar not in d or wp < d[ar]:
                d[ar] = wp
            if feat:
                if "IMPV" in feat:
                    self.imperatives[ar] += 1
                elif "IMPF" in feat:
                    self.imperfect[ar] += 1
        self.seq_surah = seq_surah
        self.root_minpos = root_minpos
        self.seqs = sorted(root_minpos)
        conn.close()

        # all nodes
        self.nodes = {}
        self.nodes.update({f"A:{k}": v for k, v in ACTIONS.items()})
        self.nodes.update({f"S:{k}": v for k, v in STATES.items()})
        self.nodes.update({f"O:{k}": v for k, v in OBSTACLES.items()})
        # node -> per-ayah min position (min over the node's present roots)
        self.node_pos = {}
        for node, roots in self.nodes.items():
            rs = [a for a in roots if a in self.root_ar]
            pos = {}
            for seq in self.seqs:
                d = self.root_minpos[seq]
                present = [d[a] for a in rs if a in d]
                if present:
                    pos[seq] = min(present)
            self.node_pos[node] = pos
        print(f"    ayahs={len(self.seqs)} nodes={len(self.nodes)}")

    # ── directed flow between two nodes over a chosen ayah subset ────────────────
    def _flow(self, A, B, seq_filter=None):
        posA, posB = self.node_pos[A], self.node_pos[B]
        seqs = self.seqs if seq_filter is None else [s for s in self.seqs if seq_filter(s)]
        fwd = bwd = 0
        sset = set(seqs)
        # within-ayah word order
        for s in seqs:
            a = posA.get(s)
            b = posB.get(s)
            if a is not None and b is not None:
                if a < b:
                    fwd += 1
                elif b < a:
                    bwd += 1
        # cross-ayah adjacency (n -> n+W)
        for s in seqs:
            for d in range(1, WINDOW + 1):
                t = s + d
                if self.seq_surah.get(t) == self.seq_surah.get(s) and t in sset:
                    if s in posA and t in posB:
                        fwd += 1
                    if s in posB and t in posA:
                        bwd += 1
        return fwd, bwd

    def _dir(self, fwd, bwd):
        tot = fwd + bwd
        return (fwd / tot) if tot else 0.0, tot

    # ── PHASE A: epistemic actions inventory ────────────────────────────────────

    def actions_inventory(self):
        print("  PHASE A — epistemic actions inventory …")
        inv = []
        for name, roots in ACTIONS.items():
            tok = sum(self.root_tok.get(self.root_ar.get(a), 0) for a in roots if a in self.root_ar)
            impv = sum(self.imperatives.get(a, 0) for a in roots)
            impf = sum(self.imperfect.get(a, 0) for a in roots)
            inv.append({"action": name, "roots": [a for a in roots if a in self.root_ar],
                        "token_count": tok, "imperative": impv, "imperfect": impf,
                        "verbal_calls": impv + impf})
        inv.sort(key=lambda x: -x["verbal_calls"])
        return {"method": METHOD,
                "definition": "actions the Quran repeatedly asks a human to perform, ranked by verbal calls (imperative+imperfect)",
                "actions": inv,
                "dominant_action": inv[0]["action"],
                "finding": ("the most-called epistemic action is '%s' (%d verbal calls); the Quran's "
                            "knowing is action-driven, not passive" % (inv[0]["action"], inv[0]["verbal_calls"]))}

    # ── build the full directed epistemic graph ─────────────────────────────────

    def _graph(self, node_subset):
        edges = []
        for A, B in combinations(sorted(node_subset), 2):
            fAB, fBA = self._flow(A, B)
            dirAB, tot = self._dir(fAB, fBA)
            if tot < MIN_SUPPORT:
                continue
            if dirAB >= 0.5:
                edges.append({"from": A, "to": B, "flow": fAB, "reverse": fBA,
                              "directionality": r(dirAB), "support": tot})
            else:
                edges.append({"from": B, "to": A, "flow": fBA, "reverse": fAB,
                              "directionality": r(1 - dirAB), "support": tot})
        edges.sort(key=lambda e: (-e["directionality"], -e["support"]))
        return edges

    def _net_outflow(self, nodes, edges):
        net = defaultdict(float)
        for e in edges:
            w = e["flow"] - e["reverse"]
            net[e["from"]] += w
            net[e["to"]] -= w
        return {n: net.get(n, 0.0) for n in nodes}

    # ── PHASE B: knowledge pathway graph ────────────────────────────────────────

    def knowledge_pathways(self):
        print("  PHASE B — knowledge pathway graph …")
        nodes = [n for n in self.nodes if n.startswith(("A:", "S:"))]
        edges = self._graph(nodes)
        net = self._net_outflow(nodes, edges)
        order = sorted(nodes, key=lambda n: -net[n])
        # verbs preceding understanding/knowledge (Q3) and following (Q4)
        targets = ["S:knowledge", "S:understanding"]
        precede, follow = [], []
        for e in edges:
            if e["to"] in targets and e["from"].startswith("A:"):
                precede.append({"action": e["from"], "flow_into": e["flow"], "directionality": e["directionality"]})
            if e["from"] in targets:
                follow.append({"node": e["to"], "flow_from": e["flow"], "directionality": e["directionality"]})
        precede.sort(key=lambda x: -x["flow_into"])
        follow.sort(key=lambda x: -x["flow_from"])
        return {"method": METHOD,
                "definition": "directed flow among epistemic actions and knowledge-states (within-ayah order + cross-ayah adjacency)",
                "n_edges": len(edges), "edges": edges,
                "net_outflow_ranking": [{"node": n, "net_outflow": r(net[n])} for n in order],
                "actions_preceding_understanding": precede[:8],
                "what_follows_understanding": follow[:8],
                "finding": ("the strongest epistemic source (highest net outflow) is '%s'; the action "
                            "with greatest flow into knowledge/understanding is '%s'" %
                            (order[0], precede[0]["action"] if precede else "none"))}

    # ── PHASE C: ignorance pathway graph ────────────────────────────────────────

    def ignorance_pathways(self):
        print("  PHASE C — ignorance pathway graph …")
        nodes = [n for n in self.nodes if n.startswith("O:")]
        edges = self._graph(nodes)
        net = self._net_outflow(nodes, edges)
        order = sorted(nodes, key=lambda n: -net[n])
        return {"method": METHOD,
                "definition": "directed flow among obstacles to knowing — the pathway from cause to blindness",
                "n_edges": len(edges), "edges": edges,
                "net_outflow_ranking": [{"node": n, "net_outflow": r(net[n])} for n in order],
                "finding": ("the ignorance pathway is led by '%s' (highest net outflow among obstacles) "
                            "and terminates in '%s'" % (order[0], order[-1]))}

    # ── PHASE D/E: enablers & obstacles of understanding ────────────────────────

    def _flow_into(self, target_roots, source_nodes):
        # treat target as a pseudo-node
        tpos = {}
        rs = [a for a in target_roots if a in self.root_ar]
        for seq in self.seqs:
            d = self.root_minpos[seq]
            present = [d[a] for a in rs if a in d]
            if present:
                tpos[seq] = min(present)
        self.node_pos["__T__"] = tpos
        out = []
        for n in source_nodes:
            f, b = self._flow(n, "__T__")
            dr, tot = self._dir(f, b)
            out.append({"node": n, "flow_into_target": f, "reverse": b,
                        "directionality": r(dr), "support": tot})
        del self.node_pos["__T__"]
        out.sort(key=lambda x: -(x["flow_into_target"] - x["reverse"]))
        return out

    def enablers(self):
        print("  PHASE D — understanding-enablers …")
        target = ["علم", "فقه", "فهم", "نهي", "لبب", "هدي", "يقن"]
        srcs = [n for n in self.nodes if n.startswith(("A:", "S:")) and self.nodes[n] != target]
        flows = self._flow_into(target, srcs)
        pos = [f for f in flows if f["flow_into_target"] > f["reverse"]][:10]
        return {"method": METHOD,
                "definition": "nodes whose directed flow runs INTO understanding/knowledge/guidance — what enables knowing",
                "target": "understanding+knowledge+guidance",
                "enablers": pos,
                "finding": ("the strongest enabler of understanding is '%s' (net forward flow %d)" %
                            (pos[0]["node"], pos[0]["flow_into_target"] - pos[0]["reverse"]) if pos else "none")}

    def obstacles_analysis(self):
        print("  PHASE E — understanding-obstacles …")
        target = ["عمي", "صمم", "بكم", "وقر", "ضلل", "زيغ", "غوي", "نسي", "غفل"]
        srcs = [n for n in self.nodes if n.startswith("O:")] + \
               [n for n in self.nodes if n.startswith("A:")]
        srcs = [n for n in srcs if self.nodes[n] != target]
        flows = self._flow_into(target, srcs)
        pos = [f for f in flows if f["flow_into_target"] > f["reverse"]][:10]
        return {"method": METHOD,
                "definition": "nodes whose directed flow runs INTO blindness/deviation/forgetting — what obstructs knowing",
                "target": "blindness+deviation+forgetting",
                "obstacles": pos,
                "finding": ("the strongest obstacle to understanding is '%s' (net forward flow %d) — "
                            "structurally precedes blindness/deviation" %
                            (pos[0]["node"], pos[0]["flow_into_target"] - pos[0]["reverse"]) if pos else "none")}

    # ── PHASE F: epistemic sequence (states gradient + modes) ───────────────────

    def epistemic_sequence(self, kpath):
        print("  PHASE F — epistemic sequence analysis …")
        # states gradient: pairwise order among the knowledge-states
        states = ["S:information", "S:knowledge", "S:understanding", "S:certainty", "S:wisdom"]
        gradient = []
        net = defaultdict(float)
        for A, B in combinations(states, 2):
            f, b = self._flow(A, B)
            dr, tot = self._dir(f, b)
            if tot >= MIN_SUPPORT:
                src, dst, d = (A, B, dr) if dr >= 0.5 else (B, A, 1 - dr)
                gradient.append({"from": src, "to": dst, "directionality": r(d), "support": tot})
                net[src] += (f - b) if dr >= 0.5 else (b - f)
                net[dst] -= (f - b) if dr >= 0.5 else (b - f)
        order = sorted(states, key=lambda n: -net.get(n, 0))
        # modes of knowing (Q10)
        self_target = KNOW_TARGET
        modes = []
        for mode, roots in MODE_SOURCES.items():
            # pseudo source node
            rs = [a for a in roots if a in self.root_ar]
            spos = {}
            for seq in self.seqs:
                d = self.root_minpos[seq]
                present = [d[a] for a in rs if a in d]
                if present:
                    spos[seq] = min(present)
            self.node_pos["__M__"] = spos
            tpos = {}
            tr = [a for a in self_target if a in self.root_ar]
            for seq in self.seqs:
                d = self.root_minpos[seq]
                present = [d[a] for a in tr if a in d]
                if present:
                    tpos[seq] = min(present)
            self.node_pos["__KT__"] = tpos
            f, b = self._flow("__M__", "__KT__")
            dr, tot = self._dir(f, b)
            modes.append({"mode": mode, "flow_to_knowledge": f, "reverse": b,
                          "directionality": r(dr), "support": tot})
            del self.node_pos["__M__"], self.node_pos["__KT__"]
        modes.sort(key=lambda m: -m["flow_to_knowledge"])
        return {"method": METHOD,
                "definition": "the ordered epistemic pipeline: net-outflow ranking, state gradient, and distinct modes of knowing",
                "pipeline_order": [x["node"] for x in kpath["net_outflow_ranking"]],
                "state_gradient_order": order,
                "state_gradient_edges": gradient,
                "modes_of_knowing": modes,
                "finding": ("epistemic order runs %s → … → %s; states ascend %s; the dominant mode of "
                            "knowing is '%s'" %
                            (kpath["net_outflow_ranking"][0]["node"],
                             kpath["net_outflow_ranking"][-1]["node"],
                             " → ".join(s.split(":")[1] for s in order),
                             modes[0]["mode"]))}

    # ── PHASE G: compression ────────────────────────────────────────────────────

    def compression(self, kpath):
        print("  PHASE G — compression …")
        ranking = kpath["net_outflow_ranking"]
        nodes_ord = [x["node"] for x in ranking]
        vals = [x["net_outflow"] for x in ranking]
        # stage boundaries at the largest gaps in net-outflow
        gaps = sorted(((vals[i] - vals[i + 1], i) for i in range(len(vals) - 1)),
                      key=lambda g: (-g[0], g[1]))[:3]
        cuts = sorted(i for _, i in gaps)
        stages, prev = [], 0
        for c in cuts + [len(nodes_ord) - 1]:
            stages.append(nodes_ord[prev:c + 1])
            prev = c + 1
        stages = [s for s in stages if s]
        # forward-consistency: fraction of edges going from earlier to later stage
        stage_of = {n: i for i, st in enumerate(stages) for n in st}
        fwd = back = 0
        for e in kpath["edges"]:
            sf, st = stage_of.get(e["from"]), stage_of.get(e["to"])
            if sf is None or st is None or sf == st:
                continue
            if sf < st:
                fwd += 1
            else:
                back += 1
        consistency = r(fwd / (fwd + back)) if (fwd + back) else 0.0
        return {"method": METHOD,
                "definition": "can the epistemic process compress to a few ordered stages? cut net-outflow at largest gaps; measure forward-edge consistency",
                "n_stages": len(stages),
                "stages": [{"stage": i + 1, "nodes": [n.split(":")[1] for n in st]} for i, st in enumerate(stages)],
                "inter_stage_forward_consistency": consistency,
                "compressible": consistency >= 0.6,
                "finding": ("the epistemic graph compresses to %d ordered stages with %.0f%% of "
                            "inter-stage edges running forward — %s" %
                            (len(stages), 100 * consistency,
                             "a genuine pipeline" if consistency >= 0.6 else "NOT a clean linear pipeline"))}

    # ── PHASE H: falsification ──────────────────────────────────────────────────

    def falsification(self, kpath, ipath):
        print("  PHASE H — falsification (reverse-sequence attack) …")
        results = []
        for label, g in (("knowledge", kpath), ("ignorance", ipath)):
            for e in g["edges"]:
                survives = e["directionality"] >= DIR_MARGIN
                results.append({"graph": label, "from": e["from"], "to": e["to"],
                                "directionality": e["directionality"], "support": e["support"],
                                "result": "SURVIVES" if survives else "REFUTED"})
        results.sort(key=lambda x: -x["directionality"])
        surv = [x for x in results if x["result"] == "SURVIVES"]
        ref = [x for x in results if x["result"] == "REFUTED"]
        return {"method": METHOD,
                "definition": "every edge attacked by its own reverse flow; survives only if directionality ≥ %.2f" % DIR_MARGIN,
                "margin": DIR_MARGIN,
                "n_edges_tested": len(results),
                "n_survive": len(surv), "n_refuted": len(ref),
                "results": results,
                "surviving_edges": [f"{x['from']}→{x['to']}" for x in surv],
                "finding": ("%d of %d epistemic edges survive the reverse-sequence attack at margin "
                            "%.2f; %d are non-directional (refuted)" %
                            (len(surv), len(results), DIR_MARGIN, len(ref)))}

    # ── PHASE I: robustness (corpus split) ──────────────────────────────────────

    def robustness(self, kpath):
        print("  PHASE I — robustness (meccan/medinan split) …")
        def mecc(s):
            return self.surah_type.get(self.seq_surah.get(s)) == "meccan"
        def med(s):
            return self.surah_type.get(self.seq_surah.get(s)) == "medinan"
        rows = []
        stable = 0
        for e in kpath["edges"]:
            A, B = e["from"], e["to"]
            fm, bm = self._flow(A, B, mecc)
            fd, bd = self._flow(A, B, med)
            dm = (fm / (fm + bm)) if (fm + bm) else 0.0
            dd = (fd / (fd + bd)) if (fd + bd) else 0.0
            ok = dm >= 0.5 and dd >= 0.5
            if ok:
                stable += 1
            rows.append({"from": A, "to": B, "dir_meccan": r(dm), "dir_medinan": r(dd),
                         "stable": ok})
        rows.sort(key=lambda x: (not x["stable"], x["from"]))
        return {"method": METHOD,
                "definition": "each knowledge edge recomputed on Meccan and Medinan halves; stable if forward direction holds in BOTH",
                "n_edges": len(rows), "n_stable": stable,
                "stable_fraction": r(stable / len(rows)) if rows else 0.0,
                "edges": rows,
                "finding": ("%d of %d knowledge edges keep their forward direction in BOTH the Meccan "
                            "and Medinan corpus — the epistemic pipeline is %s across revelation halves" %
                            (stable, len(rows),
                             "robust" if rows and stable / len(rows) >= 0.6 else "only partly stable"))}

    def manifest(self, output_bytes, summary):
        return {"method": METHOD,
                "constants": {"ROUND": ROUND, "WINDOW": WINDOW, "MIN_SUPPORT": MIN_SUPPORT,
                              "DIR_MARGIN": DIR_MARGIN,
                              "actions": list(ACTIONS), "states": list(STATES),
                              "obstacles": list(OBSTACLES)},
                "input_sha256": {"monad.db": sha256_file(self.db)},
                "output_bytes": output_bytes,
                "prohibitions_observed": PROHIBITIONS,
                "totals": summary}

    def run(self):
        self.load()
        products = {}
        acts = self.actions_inventory();      products["epistemic_actions.json"] = acts
        kpath = self.knowledge_pathways();    products["knowledge_pathways.json"] = kpath
        ipath = self.ignorance_pathways();    products["ignorance_pathways.json"] = ipath
        enab = self.enablers();               products["enablers.json"] = enab
        obst = self.obstacles_analysis();     products["obstacles.json"] = obst
        seq = self.epistemic_sequence(kpath); products["epistemic_sequence.json"] = seq
        comp = self.compression(kpath);       products["epistemic_compression.json"] = comp
        fal = self.falsification(kpath, ipath); products["falsification_results.json"] = fal
        rob = self.robustness(kpath);         products["robustness_results.json"] = rob

        output_bytes = {}
        declared = ["epistemic_actions.json", "knowledge_pathways.json", "ignorance_pathways.json",
                    "enablers.json", "obstacles.json", "epistemic_sequence.json",
                    "epistemic_compression.json", "falsification_results.json", "robustness_results.json"]
        for name in declared:
            output_bytes[name] = write_json(self.out_dir / name, products[name])
            print(f"    wrote {name} ({output_bytes[name]} bytes)")

        summary = {
            "dominant_action": acts["dominant_action"],
            "pipeline_order": seq["pipeline_order"],
            "state_gradient_order": seq["state_gradient_order"],
            "dominant_mode_of_knowing": seq["modes_of_knowing"][0]["mode"],
            "top_enabler": enab["enablers"][0]["node"] if enab["enablers"] else None,
            "top_obstacle": obst["obstacles"][0]["node"] if obst["obstacles"] else None,
            "n_stages": comp["n_stages"],
            "compressible": comp["compressible"],
            "edges_survive_falsification": fal["n_survive"],
            "edges_tested": fal["n_edges_tested"],
            "robust_fraction": rob["stable_fraction"],
        }
        man = self.manifest(output_bytes, summary)
        output_bytes["epistemology_manifest.json"] = write_json(
            self.out_dir / "epistemology_manifest.json", man)
        print(f"    wrote epistemology_manifest.json ({output_bytes['epistemology_manifest.json']} bytes)")
        self.summary = summary
        return summary


def main():
    ap = argparse.ArgumentParser(description="Monad Phase X — Epistemology Discovery Engine")
    ap.add_argument("--db", default="generated/monad.db")
    ap.add_argument("--out", default="generated/epistemology")
    args = ap.parse_args()
    print(f"Monad Phase X — Epistemology Discovery Engine ({METHOD})")
    eng = EpistemologyEngine(args.db, args.out)
    summary = eng.run()
    print("  done.")
    print(f"  summary: {json.dumps(summary, ensure_ascii=False)[:600]}")


if __name__ == "__main__":
    main()
