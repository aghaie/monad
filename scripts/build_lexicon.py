#!/usr/bin/env python3
"""
scripts/build_lexicon.py

Monad Quran Internal Lexicon Engine — Builder (Phase 2).

Discovers how words derive meaning from their usage INSIDE the Quran itself.
The Quran is treated as the primary (and only) semantic universe. No external
dictionaries, tafsir, translations, theology, or pre-trained embeddings are
ever consulted. Every number below is computed purely from Quran-internal
distributional evidence already imported into generated/monad.db.

Usage:
    python scripts/build_lexicon.py [--db PATH] [--out DIR]

Inputs (read-only):
    generated/monad.db          words / roots / lemmas / surahs / ayahs tables

Outputs (generated/lexicon/):
    root_profiles.json          per-root usage profile
    lemma_profiles.json         per-lemma usage profile
    context_windows.json        per-occurrence prev/next windows (sizes 3,5,10)
    cooccurrence_graph.json     weighted root+lemma co-occurrence graph
    semantic_neighbors.json     top-20 internal semantic neighbors + confidence
    distribution_profiles.json  surah / revelation / dispersion statistics
    lexicon_summary.json        global counts + reproducibility manifest

Method (all Quran-internal):
    * Co-occurrence unit = the AYAH (the natural Quranic semantic envelope).
    * Context windows    = positional, within-ayah, never crossing ayah bounds.
    * Association weight  = Positive Pointwise Mutual Information (PPMI) over
                            ayah-level co-occurrence.
    * Semantic similarity = composite confidence in [0,1]:
          SIM_W_DISTRIB * cosine(PPMI context vectors)      [shared contexts]
        + SIM_W_CHAPTER * cosine(surah distribution vectors) [chapter affinity]
      Distributional cosine simultaneously captures "shared contexts" and
      "shared neighbors"; the chapter term adds macro-distribution agreement.

Determinism:
    No randomness. All iteration is over sorted keys. Floats are rounded to
    ROUND decimals. JSON is written with sort_keys=True. Re-running on the same
    database produces byte-identical output (verified by validate_lexicon.py).

STRICTLY LEXICAL/STATISTICAL. Builds no concepts, ontology, propositions,
axioms, contradiction engine, or interpretation. Draws no theological,
divine-origin, or human-origin conclusions.
"""

import argparse
import json
import math
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "generated" / "monad.db"
DEFAULT_OUT = REPO_ROOT / "generated" / "lexicon"

# ── Tunable constants (documented; deterministic) ─────────────────────────────

TOP_NEIGHBORS   = 20     # neighbors stored per root / lemma (profiles + semantic)
TOP_CTX_DIMS    = 100    # PPMI vector truncated to its strongest dimensions
WINDOW_SIZES    = (3, 5, 10)
SIM_W_DISTRIB   = 0.70   # weight: distributional (PPMI cosine) similarity
SIM_W_CHAPTER   = 0.30   # weight: surah-distribution cosine similarity
MIN_SIM         = 0.05   # discard semantic-neighbor pairs below this confidence
GRAPH_EDGES_PER_NODE = 12  # co-occurrence edges retained per node in the graph
GRAPH_MIN_COOC  = 2      # minimum shared-ayah count for a graph co-occ edge
ROUND           = 6      # float rounding for determinism

METHOD_VERSION  = "phase2-lexicon-1.0"

# ── Small helpers ─────────────────────────────────────────────────────────────

def r(x: float) -> float:
    """Deterministic rounding."""
    return round(float(x), ROUND)


def write_json(path: Path, obj) -> int:
    """Write deterministic JSON; return byte size."""
    text = json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=1)
    path.write_text(text, encoding="utf-8")
    return len(text.encode("utf-8"))


# ── Builder ───────────────────────────────────────────────────────────────────

class LexiconBuilder:

    def __init__(self, db_path: Path, out_dir: Path):
        self.db_path = db_path
        self.out_dir = out_dir
        self.con = sqlite3.connect(db_path)
        self.con.row_factory = sqlite3.Row
        self.manifest = {}

    # ── 1. Load canonical data from the database ──────────────────────────────

    def load(self):
        con = self.con
        print("  loading roots / lemmas / surahs / words …")

        self.roots = {}      # root_id -> {buckwalter, arabic, token_count}
        for row in con.execute(
                "SELECT root_id, root_buckwalter, root_arabic, token_count FROM roots"):
            self.roots[row["root_id"]] = {
                "buckwalter": row["root_buckwalter"],
                "arabic": row["root_arabic"],
                "token_count": row["token_count"],
            }

        self.lemmas = {}     # lemma_id -> {buckwalter, arabic, root_id}
        for row in con.execute(
                "SELECT lemma_id, lemma_buckwalter, lemma_arabic, root_id FROM lemmas"):
            self.lemmas[row["lemma_id"]] = {
                "buckwalter": row["lemma_buckwalter"],
                "arabic": row["lemma_arabic"],
                "root_id": row["root_id"],
            }

        self.surahs = {}     # surah_number -> {name, revelation_type, ayah_count}
        for row in con.execute(
                "SELECT surah_number, name_arabic, revelation_type, ayah_count FROM surahs"):
            self.surahs[row["surah_number"]] = {
                "name": row["name_arabic"],
                "revelation_type": row["revelation_type"],
                "ayah_count": row["ayah_count"],
            }

        # Global ayah sequence for first/last-occurrence ordering.
        self.ayah_seq = {}   # (surah, ayah) -> sequential
        for row in con.execute(
                "SELECT surah_number, ayah_number, ayah_sequential FROM ayahs"):
            self.ayah_seq[(row["surah_number"], row["ayah_number"])] = row["ayah_sequential"]

        # Ordered token stream. word_id is allocated in reading order, but we
        # order explicitly to be safe and reproducible.
        self.words = []      # list of dicts in reading order
        for row in con.execute(
                "SELECT word_id, surah_number, ayah_number, word_position, "
                "form_arabic, lemma_id, root_id FROM words "
                "ORDER BY surah_number, ayah_number, word_position"):
            self.words.append({
                "word_id": row["word_id"],
                "surah": row["surah_number"],
                "ayah": row["ayah_number"],
                "pos": row["word_position"],
                "form": row["form_arabic"],
                "lemma_id": row["lemma_id"],
                "root_id": row["root_id"],
            })

        # Group words by ayah (reading order preserved).
        self.ayah_words = defaultdict(list)
        for w in self.words:
            self.ayah_words[(w["surah"], w["ayah"])].append(w)

        print(f"    roots={len(self.roots)} lemmas={len(self.lemmas)} "
              f"surahs={len(self.surahs)} words={len(self.words)}")

    # ── 2. Occurrences, document-frequency, co-occurrence ─────────────────────

    def build_cooccurrence(self):
        print("  building occurrences + ayah-level co-occurrence …")

        # Occurrences (every token position) per entity.
        self.root_occ = defaultdict(list)   # root_id -> [(surah,ayah,pos), ...]
        self.lemma_occ = defaultdict(list)  # lemma_id -> [(surah,ayah,pos), ...]
        # Surah distribution (token counts).
        self.root_surah = defaultdict(lambda: defaultdict(int))
        self.lemma_surah = defaultdict(lambda: defaultdict(int))

        for w in self.words:
            key = (w["surah"], w["ayah"], w["pos"])
            if w["root_id"] is not None:
                self.root_occ[w["root_id"]].append(key)
                self.root_surah[w["root_id"]][w["surah"]] += 1
            if w["lemma_id"] is not None:
                self.lemma_occ[w["lemma_id"]].append(key)
                self.lemma_surah[w["lemma_id"]][w["surah"]] += 1

        # Ayah-level document frequency (distinct entities per ayah) and
        # symmetric co-occurrence counts (# of ayahs sharing the pair).
        self.root_df = defaultdict(int)
        self.lemma_df = defaultdict(int)
        self.root_cooc = defaultdict(lambda: defaultdict(int))
        self.lemma_cooc = defaultdict(lambda: defaultdict(int))
        self.n_ayahs = len(self.ayah_words)

        for key in sorted(self.ayah_words.keys()):
            ws = self.ayah_words[key]
            rset = sorted({w["root_id"] for w in ws if w["root_id"] is not None})
            lset = sorted({w["lemma_id"] for w in ws if w["lemma_id"] is not None})
            for rid in rset:
                self.root_df[rid] += 1
            for lid in lset:
                self.lemma_df[lid] += 1
            for i in range(len(rset)):
                a = rset[i]
                for j in range(i + 1, len(rset)):
                    b = rset[j]
                    self.root_cooc[a][b] += 1
                    self.root_cooc[b][a] += 1
            for i in range(len(lset)):
                a = lset[i]
                for j in range(i + 1, len(lset)):
                    b = lset[j]
                    self.lemma_cooc[a][b] += 1
                    self.lemma_cooc[b][a] += 1

        print(f"    ayahs={self.n_ayahs} "
              f"root_pairs={sum(len(v) for v in self.root_cooc.values())//2} "
              f"lemma_pairs={sum(len(v) for v in self.lemma_cooc.values())//2}")

    # ── 3. PPMI vectors (shared-context distributional model) ─────────────────

    def _ppmi_vectors(self, df, cooc, n):
        """Truncated PPMI vector per entity. Returns (vectors, norms).

        PMI(a,b)  = log2( cooc(a,b) * N / (df(a) * df(b)) )
        PPMI(a,b) = max(0, PMI)
        Vector(a) = top TOP_CTX_DIMS dimensions of a by PPMI.
        """
        vectors = {}
        norms = {}
        for a in sorted(cooc.keys()):
            dfa = df[a]
            row = {}
            for b, c in cooc[a].items():
                pmi = math.log2((c * n) / (dfa * df[b]))
                if pmi > 0.0:
                    row[b] = pmi
            if not row:
                continue
            # Truncate to strongest dimensions (denoise + bound cost).
            if len(row) > TOP_CTX_DIMS:
                kept = sorted(row.items(), key=lambda kv: (-kv[1], kv[0]))[:TOP_CTX_DIMS]
                row = dict(kept)
            norm = math.sqrt(sum(v * v for v in row.values()))
            vectors[a] = row
            norms[a] = norm
        return vectors, norms

    def _chapter_vectors(self, surah_dist):
        """L2-normalised surah-distribution vectors (token counts over 114)."""
        vecs = {}
        for a in sorted(surah_dist.keys()):
            d = surah_dist[a]
            norm = math.sqrt(sum(v * v for v in d.values()))
            vecs[a] = (d, norm)
        return vecs

    def _semantic_neighbors(self, vectors, norms, chap_vecs):
        """All-pairs top-k composite similarity via inverted-index cosine.

        Distributional cosine is accumulated only for pairs that share at least
        one PPMI dimension (inverted index). The chapter cosine is then blended
        in for those candidate pairs only.
        """
        # Inverted index: dimension -> [(entity, weight), ...]
        inverted = defaultdict(list)
        for a, row in vectors.items():
            for dim, w in row.items():
                inverted[dim].append((a, w))

        # Accumulate distributional dot products for co-dimensional pairs.
        dots = defaultdict(float)   # (min,max) -> dot
        for dim in sorted(inverted.keys()):
            members = inverted[dim]
            for i in range(len(members)):
                ai, wi = members[i]
                for j in range(i + 1, len(members)):
                    aj, wj = members[j]
                    pair = (ai, aj) if ai < aj else (aj, ai)
                    dots[pair] += wi * wj

        neighbors = defaultdict(list)
        for (a, b), dot in dots.items():
            na, nb = norms[a], norms[b]
            if na == 0.0 or nb == 0.0:
                continue
            distrib = dot / (na * nb)
            # Chapter cosine (cheap, computed only for candidate pairs).
            (da, nca) = chap_vecs.get(a, ({}, 0.0))
            (db, ncb) = chap_vecs.get(b, ({}, 0.0))
            chapter = 0.0
            if nca > 0.0 and ncb > 0.0:
                if len(da) <= len(db):
                    cdot = sum(v * db.get(k, 0) for k, v in da.items())
                else:
                    cdot = sum(v * da.get(k, 0) for k, v in db.items())
                chapter = cdot / (nca * ncb)
            sim = SIM_W_DISTRIB * distrib + SIM_W_CHAPTER * chapter
            if sim < MIN_SIM:
                continue
            neighbors[a].append((b, sim, distrib, chapter))
            neighbors[b].append((a, sim, distrib, chapter))

        # Keep top-k per entity (sorted by sim desc, id asc for determinism).
        result = {}
        for a in sorted(neighbors.keys()):
            ranked = sorted(neighbors[a], key=lambda t: (-t[1], t[0]))[:TOP_NEIGHBORS]
            result[a] = ranked
        return result

    def build_semantics(self):
        print("  computing PPMI vectors + semantic neighbors (roots) …")
        self.root_vecs, self.root_norms = self._ppmi_vectors(
            self.root_df, self.root_cooc, self.n_ayahs)
        self.root_chap = self._chapter_vectors(self.root_surah)
        self.root_neighbors = self._semantic_neighbors(
            self.root_vecs, self.root_norms, self.root_chap)

        print("  computing PPMI vectors + semantic neighbors (lemmas) …")
        self.lemma_vecs, self.lemma_norms = self._ppmi_vectors(
            self.lemma_df, self.lemma_cooc, self.n_ayahs)
        self.lemma_chap = self._chapter_vectors(self.lemma_surah)
        self.lemma_neighbors = self._semantic_neighbors(
            self.lemma_vecs, self.lemma_norms, self.lemma_chap)

    # ── 4. Distribution statistics ────────────────────────────────────────────

    @staticmethod
    def _dist_stats(surah_counts: dict, n_total: int):
        """Spread statistics over surahs for one entity (Quran-internal only)."""
        surah_count = len(surah_counts)
        counts = sorted(surah_counts.values(), reverse=True)
        total = sum(counts)
        # Shannon entropy (bits) over surah distribution -> semantic breadth.
        entropy = 0.0
        for c in counts:
            p = c / total
            entropy -= p * math.log2(p)
        max_entropy = math.log2(surah_count) if surah_count > 1 else 0.0
        evenness = (entropy / max_entropy) if max_entropy > 0 else 0.0
        # Concentration: share carried by the single most-frequent surah.
        top_share = counts[0] / total if total else 0.0
        # Coverage: fraction of all 114 surahs touched.
        coverage = surah_count / 114.0
        return {
            "surah_count": surah_count,
            "total_occurrences": total,
            "entropy_bits": r(entropy),
            "evenness": r(evenness),       # 0 = single surah, 1 = perfectly even
            "top_surah_share": r(top_share),
            "surah_coverage": r(coverage),
        }

    # ── 5. Context windows ────────────────────────────────────────────────────

    def build_context_windows(self):
        """Per-occurrence positional windows within the ayah (sizes 3/5/10)."""
        print("  building context windows (sizes 3/5/10) …")
        self.context_windows = []
        maxw = max(WINDOW_SIZES)
        for key in sorted(self.ayah_words.keys()):
            ws = self.ayah_words[key]
            for idx, w in enumerate(ws):
                prev = ws[max(0, idx - maxw): idx]
                nxt = ws[idx + 1: idx + 1 + maxw]
                neighbor_roots = {}
                neighbor_lemmas = {}
                for size in WINDOW_SIZES:
                    p = ws[max(0, idx - size): idx]
                    n = ws[idx + 1: idx + 1 + size]
                    ctx = p + n
                    nr = sorted({x["root_id"] for x in ctx if x["root_id"] is not None})
                    nl = sorted({x["lemma_id"] for x in ctx if x["lemma_id"] is not None})
                    neighbor_roots[str(size)] = nr
                    neighbor_lemmas[str(size)] = nl
                self.context_windows.append({
                    "surah": w["surah"],
                    "ayah": w["ayah"],
                    "position": w["pos"],
                    "form": w["form"],
                    "root_id": w["root_id"],
                    "lemma_id": w["lemma_id"],
                    "prev_forms": [x["form"] for x in prev],
                    "next_forms": [x["form"] for x in nxt],
                    "neighbor_roots": neighbor_roots,
                    "neighbor_lemmas": neighbor_lemmas,
                })

    # ── 6. Representative contexts ────────────────────────────────────────────

    def _contexts_for(self, occ, limit=5):
        """First `limit` occurrences rendered as readable verse snippets."""
        out = []
        seen = set()
        for (s, a, p) in occ:
            if (s, a) in seen:
                continue
            seen.add((s, a))
            forms = [w["form"] for w in self.ayah_words[(s, a)]]
            out.append({
                "surah": s,
                "ayah": a,
                "surah_name": self.surahs[s]["name"],
                "text": " ".join(forms),
            })
            if len(out) >= limit:
                break
        return out

    # ── 7. Neighbor ranking from co-occurrence (PPMI-weighted) ────────────────

    def _top_neighbors_cooc(self, eid, cooc, df, n, limit=TOP_NEIGHBORS):
        """PPMI-ranked co-occurrence neighbors with a frequency-scaled support
        floor. Raw PPMI over-rewards rare pairs (a single shared ayah maxes the
        score); requiring a minimum number of shared ayahs that scales with the
        entity's own frequency removes those artifacts while staying populated
        for genuinely rare entities. Ranked by PPMI, then support, then id."""
        dfa = df[eid]
        floor = max(2, min(6, round(0.02 * dfa)))
        scored = []
        for b, c in cooc[eid].items():
            if c < floor:
                continue
            pmi = math.log2((c * n) / (dfa * df[b]))
            scored.append((b, c, max(0.0, pmi)))
        # Fall back to no floor only if the floor emptied the list.
        if not scored:
            for b, c in cooc[eid].items():
                pmi = math.log2((c * n) / (dfa * df[b]))
                scored.append((b, c, max(0.0, pmi)))
        scored.sort(key=lambda t: (-t[2], -t[1], t[0]))
        return scored[:limit]

    # ── 8. Assemble + write outputs ───────────────────────────────────────────

    def build_profiles(self):
        print("  assembling root + lemma profiles …")

        # ---- Root profiles ----
        self.root_profiles = {}
        self.root_dist = {}
        for rid in sorted(self.root_occ.keys()):
            occ = self.root_occ[rid]
            occ_sorted = sorted(occ, key=lambda k: self.ayah_seq[(k[0], k[1])])
            first = occ_sorted[0]
            last = occ_sorted[-1]
            lemmas_of_root = sorted(
                lid for lid, lm in self.lemmas.items() if lm["root_id"] == rid)
            # neighbor roots / lemmas via PPMI-weighted co-occurrence
            nbr_roots = self._top_neighbors_cooc(
                rid, self.root_cooc, self.root_df, self.n_ayahs)
            # neighbor lemmas: aggregate lemma co-occurrence for this root's tokens
            lem_co = defaultdict(int)
            occ_ayahs = {(s, a) for (s, a, p) in occ}
            for (s, a) in occ_ayahs:
                for w in self.ayah_words[(s, a)]:
                    if w["lemma_id"] is not None:
                        lem_co[w["lemma_id"]] += 1
            nbr_lemmas = sorted(lem_co.items(), key=lambda kv: (-kv[1], kv[0]))[:TOP_NEIGHBORS]

            stats = self._dist_stats(self.root_surah[rid], len(occ))
            self.root_dist[rid] = stats

            self.root_profiles[str(rid)] = {
                "root_id": rid,
                "root_buckwalter": self.roots[rid]["buckwalter"],
                "root_arabic": self.roots[rid]["arabic"],
                "occurrence_count": len(occ),
                "lemma_count": len(lemmas_of_root),
                "lemma_ids": lemmas_of_root,
                "surah_count": stats["surah_count"],
                "first_occurrence": {"surah": first[0], "ayah": first[1],
                                     "position": first[2]},
                "last_occurrence": {"surah": last[0], "ayah": last[1],
                                    "position": last[2]},
                "top_neighbor_roots": [
                    {"root_id": b, "root_arabic": self.roots[b]["arabic"],
                     "shared_ayahs": c, "ppmi": r(p)} for (b, c, p) in nbr_roots],
                "top_neighbor_lemmas": [
                    {"lemma_id": b, "lemma_arabic": self.lemmas[b]["arabic"],
                     "shared_ayahs": c} for (b, c) in nbr_lemmas],
                "most_common_contexts": self._contexts_for(occ_sorted),
                "distribution_statistics": stats,
            }

        # ---- Lemma profiles ----
        self.lemma_profiles = {}
        self.lemma_dist = {}
        for lid in sorted(self.lemma_occ.keys()):
            occ = self.lemma_occ[lid]
            occ_sorted = sorted(occ, key=lambda k: self.ayah_seq[(k[0], k[1])])
            rid = self.lemmas[lid]["root_id"]
            nbr_lemmas = self._top_neighbors_cooc(
                lid, self.lemma_cooc, self.lemma_df, self.n_ayahs)
            # neighbor roots: aggregate root co-occurrence for this lemma's ayahs
            root_co = defaultdict(int)
            occ_ayahs = {(s, a) for (s, a, p) in occ}
            for (s, a) in occ_ayahs:
                for w in self.ayah_words[(s, a)]:
                    if w["root_id"] is not None:
                        root_co[w["root_id"]] += 1
            nbr_roots = sorted(root_co.items(), key=lambda kv: (-kv[1], kv[0]))[:TOP_NEIGHBORS]

            stats = self._dist_stats(self.lemma_surah[lid], len(occ))
            self.lemma_dist[lid] = stats

            self.lemma_profiles[str(lid)] = {
                "lemma_id": lid,
                "lemma_buckwalter": self.lemmas[lid]["buckwalter"],
                "lemma_arabic": self.lemmas[lid]["arabic"],
                "root_id": rid,
                "root_arabic": self.roots[rid]["arabic"] if rid in self.roots else None,
                "occurrence_count": len(occ),
                "surah_count": stats["surah_count"],
                "top_neighbor_lemmas": [
                    {"lemma_id": b, "lemma_arabic": self.lemmas[b]["arabic"],
                     "shared_ayahs": c, "ppmi": r(p)} for (b, c, p) in nbr_lemmas],
                "top_neighbor_roots": [
                    {"root_id": b, "root_arabic": self.roots[b]["arabic"],
                     "shared_ayahs": c} for (b, c) in nbr_roots],
                "representative_contexts": self._contexts_for(occ_sorted),
                "surah_distribution": {str(s): c for s, c
                                       in sorted(self.lemma_surah[lid].items())},
                "distribution_statistics": stats,
            }

    def build_semantic_output(self):
        print("  assembling semantic_neighbors output …")
        roots_out = {}
        for rid in sorted(self.root_neighbors.keys()):
            roots_out[str(rid)] = {
                "root_id": rid,
                "root_arabic": self.roots[rid]["arabic"],
                "neighbors": [
                    {"root_id": b, "root_arabic": self.roots[b]["arabic"],
                     "confidence": r(sim), "distributional": r(d),
                     "chapter": r(ch)}
                    for (b, sim, d, ch) in self.root_neighbors[rid]],
            }
        lemmas_out = {}
        for lid in sorted(self.lemma_neighbors.keys()):
            lemmas_out[str(lid)] = {
                "lemma_id": lid,
                "lemma_arabic": self.lemmas[lid]["arabic"],
                "neighbors": [
                    {"lemma_id": b, "lemma_arabic": self.lemmas[b]["arabic"],
                     "confidence": r(sim), "distributional": r(d),
                     "chapter": r(ch)}
                    for (b, sim, d, ch) in self.lemma_neighbors[lid]],
            }
        self.semantic_output = {
            "method": METHOD_VERSION,
            "weights": {"distributional": SIM_W_DISTRIB, "chapter": SIM_W_CHAPTER},
            "top_k": TOP_NEIGHBORS,
            "min_confidence": MIN_SIM,
            "roots": roots_out,
            "lemmas": lemmas_out,
        }

    def build_graph(self):
        print("  assembling co-occurrence graph …")
        nodes = []
        for rid in sorted(self.root_occ.keys()):
            nodes.append({
                "id": f"root:{rid}",
                "type": "root",
                "ref_id": rid,
                "label": self.roots[rid]["arabic"],
                "occurrence_count": len(self.root_occ[rid]),
            })
        for lid in sorted(self.lemma_occ.keys()):
            nodes.append({
                "id": f"lemma:{lid}",
                "type": "lemma",
                "ref_id": lid,
                "label": self.lemmas[lid]["arabic"],
                "occurrence_count": len(self.lemma_occ[lid]),
            })

        edges = []
        emitted = set()

        def cooc_edges(cooc, df, prefix, neighbors):
            for a in sorted(cooc.keys()):
                dfa = df[a]
                # top co-occurrence partners for node a (PPMI-weighted)
                ranked = sorted(
                    cooc[a].items(),
                    key=lambda kv: (-(math.log2((kv[1] * self.n_ayahs) / (dfa * df[kv[0]]))),
                                    -kv[1], kv[0]))
                kept = 0
                # semantic proximity lookup for this node
                sem = {b: sim for (b, sim, d, ch) in neighbors.get(a, [])}
                for b, c in ranked:
                    if c < GRAPH_MIN_COOC:
                        continue
                    if kept >= GRAPH_EDGES_PER_NODE:
                        break
                    lo, hi = (a, b) if a < b else (b, a)
                    ekey = (prefix, lo, hi)
                    if ekey in emitted:
                        continue
                    emitted.add(ekey)
                    pmi = math.log2((c * self.n_ayahs) / (dfa * df[b]))
                    edges.append({
                        "source": f"{prefix}:{lo}",
                        "target": f"{prefix}:{hi}",
                        "type": f"{prefix}_cooccurrence",
                        "cooccurrence": c,
                        "ppmi": r(max(0.0, pmi)),
                        "semantic_proximity": r(sem.get(b, 0.0)),
                    })
                    kept += 1

        cooc_edges(self.root_cooc, self.root_df, "root", self.root_neighbors)
        cooc_edges(self.lemma_cooc, self.lemma_df, "lemma", self.lemma_neighbors)

        self.graph = {
            "method": METHOD_VERSION,
            "directed": False,
            "node_types": ["root", "lemma"],
            "edge_types": ["root_cooccurrence", "lemma_cooccurrence"],
            "edge_attributes": ["cooccurrence", "ppmi", "semantic_proximity"],
            "edges_per_node": GRAPH_EDGES_PER_NODE,
            "min_cooccurrence": GRAPH_MIN_COOC,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "nodes": nodes,
            "edges": edges,
        }

    def build_distribution_output(self):
        print("  assembling distribution_profiles …")
        roots_out = {}
        for rid in sorted(self.root_dist.keys()):
            s = self.root_dist[rid]
            mec = sum(c for sn, c in self.root_surah[rid].items()
                      if self.surahs[sn]["revelation_type"] == "meccan")
            med = sum(c for sn, c in self.root_surah[rid].items()
                      if self.surahs[sn]["revelation_type"] == "medinan")
            roots_out[str(rid)] = {
                "root_id": rid,
                "root_arabic": self.roots[rid]["arabic"],
                **s,
                "meccan_occurrences": mec,
                "medinan_occurrences": med,
                "surah_distribution": {str(k): v for k, v
                                       in sorted(self.root_surah[rid].items())},
            }
        lemmas_out = {}
        for lid in sorted(self.lemma_dist.keys()):
            s = self.lemma_dist[lid]
            mec = sum(c for sn, c in self.lemma_surah[lid].items()
                      if self.surahs[sn]["revelation_type"] == "meccan")
            med = sum(c for sn, c in self.lemma_surah[lid].items()
                      if self.surahs[sn]["revelation_type"] == "medinan")
            lemmas_out[str(lid)] = {
                "lemma_id": lid,
                "lemma_arabic": self.lemmas[lid]["arabic"],
                **s,
                "meccan_occurrences": mec,
                "medinan_occurrences": med,
            }
        self.distribution_output = {
            "method": METHOD_VERSION,
            "roots": roots_out,
            "lemmas": lemmas_out,
        }

    # ── 9. Write everything ───────────────────────────────────────────────────

    def write(self):
        self.out_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n  writing outputs to {self.out_dir} …")

        files = {}
        files["root_profiles.json"] = write_json(
            self.out_dir / "root_profiles.json", self.root_profiles)
        files["lemma_profiles.json"] = write_json(
            self.out_dir / "lemma_profiles.json", self.lemma_profiles)
        files["context_windows.json"] = write_json(
            self.out_dir / "context_windows.json", {
                "method": METHOD_VERSION,
                "window_sizes": list(WINDOW_SIZES),
                "occurrence_count": len(self.context_windows),
                "windows": self.context_windows,
            })
        files["cooccurrence_graph.json"] = write_json(
            self.out_dir / "cooccurrence_graph.json", self.graph)
        files["semantic_neighbors.json"] = write_json(
            self.out_dir / "semantic_neighbors.json", self.semantic_output)
        files["distribution_profiles.json"] = write_json(
            self.out_dir / "distribution_profiles.json", self.distribution_output)

        # ---- Global summary + reproducibility manifest ----
        summary = {
            "method": METHOD_VERSION,
            "source_database": str(self.db_path.name),
            "constants": {
                "TOP_NEIGHBORS": TOP_NEIGHBORS,
                "TOP_CTX_DIMS": TOP_CTX_DIMS,
                "WINDOW_SIZES": list(WINDOW_SIZES),
                "SIM_W_DISTRIB": SIM_W_DISTRIB,
                "SIM_W_CHAPTER": SIM_W_CHAPTER,
                "MIN_SIM": MIN_SIM,
                "GRAPH_EDGES_PER_NODE": GRAPH_EDGES_PER_NODE,
                "GRAPH_MIN_COOC": GRAPH_MIN_COOC,
                "ROUND": ROUND,
            },
            "totals": {
                "roots": len(self.root_profiles),
                "lemmas": len(self.lemma_profiles),
                "surahs": len(self.surahs),
                "ayahs": self.n_ayahs,
                "word_tokens": len(self.words),
                "tokens_with_root": sum(len(v) for v in self.root_occ.values()),
                "tokens_with_lemma": sum(len(v) for v in self.lemma_occ.values()),
                "context_windows": len(self.context_windows),
                "graph_nodes": self.graph["node_count"],
                "graph_edges": self.graph["edge_count"],
                "roots_with_neighbors": len(self.root_neighbors),
                "lemmas_with_neighbors": len(self.lemma_neighbors),
            },
            "output_bytes": files,
            "prohibitions_observed": [
                "no external dictionaries", "no tafsir", "no translations",
                "no theology", "no pretrained embeddings", "no concepts",
                "no ontology", "no propositions", "no axioms",
                "no contradiction engine", "no interpretation",
                "no origin claims",
            ],
        }
        files["lexicon_summary.json"] = write_json(
            self.out_dir / "lexicon_summary.json", summary)
        self.summary = summary

        total = sum(files.values())
        for name in sorted(files):
            print(f"    {name:28s} {files[name]:>12,d} bytes")
        print(f"    {'TOTAL':28s} {total:>12,d} bytes")

    # ── Orchestration ─────────────────────────────────────────────────────────

    def run(self):
        print(f"\nBuilding Quran Internal Lexicon from {self.db_path} …\n")
        self.load()
        self.build_cooccurrence()
        self.build_semantics()
        self.build_context_windows()
        self.build_profiles()
        self.build_semantic_output()
        self.build_graph()
        self.build_distribution_output()
        self.write()
        self.con.close()
        print("\nLexicon build complete.\n")
        return self.summary


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=str(DEFAULT_DB),
                    help=f"Source database (default: {DEFAULT_DB})")
    ap.add_argument("--out", default=str(DEFAULT_OUT),
                    help=f"Output directory (default: {DEFAULT_OUT})")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        sys.exit(1)

    builder = LexiconBuilder(db_path, Path(args.out))
    builder.run()


if __name__ == "__main__":
    main()
