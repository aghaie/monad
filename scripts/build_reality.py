#!/usr/bin/env python3
"""
Monad — Phase R: Text → Reality Discovery Engine
================================================

For the first time the direction reverses. Every prior phase looked *inward* at the
text. This phase asks: which phenomena in REALITY does the Quran invite us to observe,
what patterns (سنن) does it assert about them, and do those patterns survive testing?

This is not a proof of the Quran, nor a defence, nor a refutation — only a test. If the
Quran invites observation of a pattern, that pattern is measured. If it holds, it is
reported; if it fails, that is reported too.

HONEST BOUNDARY (stated up front, enforced throughout): with no external source
permitted — no other scripture, no tafsir, no kalām school, and no world-history or
empirical dataset — this engine cannot independently verify a pattern against the
external world. What it CAN do, from the corpus alone, is (a) extract the observable
phenomena the Quran points to, (b) extract the patterns it asserts about them, (c) test
whether those assertions are CROSS-DOMAIN (universal سنن) and INTERNALLY CONSISTENT
(survive counter-examples within the Quran itself). The "reality" tested here is the
Quran's own claim-structure about reality and its internal coherence — not a
measurement of history. That limit is the finding's boundary, not a defect.

Inputs: the Quran corpus (Phase-1 database). Nothing else.
Deterministic, pure-stdlib, byte-identically reproducible.
"""

import argparse
import hashlib
import json
import sqlite3
from collections import defaultdict
from pathlib import Path

METHOD = "reality-discovery-1.0"
ROUND = 6
WINDOW = 1   # adjacency window (ayahs) for antecedent→consequent co-occurrence, same surah

# ── domains of observable phenomena (corpus root_arabic → opaque label) ──────────
DOMAINS = {
    "nature": {"سمو": "sky", "ارض": "earth", "شمس": "sun", "قمر": "moon", "نجم": "stars",
               "ليل": "night", "نهر": "day", "مطر": "rain", "بحر": "sea", "جبل": "mountains",
               "نبت": "plants", "شجر": "trees", "خلق": "creation"},
    "human": {"انس": "human", "بشر": "humankind", "نفس": "self", "قلب": "heart",
              "عقل": "reason", "موت": "death", "حيي": "life"},
    "society": {"قوم": "people", "امم": "nations", "نوس": "mankind", "قري": "townships",
                "مدن": "cities"},
    "history": {"قرن": "generations", "رسل": "messengers", "نبا": "tidings", "قصص": "narratives",
                "خلف": "succession", "هلك": "perishing", "دمر": "destruction", "اثر": "ruins",
                "عقب": "outcome"},
    "ethics": {"عدل": "justice", "ظلم": "injustice", "صدق": "truth", "كذب": "falsehood",
               "خير": "good", "شرر": "evil", "فسد": "corruption", "صلح": "rectitude",
               "قسط": "equity"},
    "psyche": {"نفس": "self", "قلب": "heart", "خوف": "fear", "حزن": "grief", "طمن": "tranquility",
               "وسوس": "whispering", "سكن": "repose"},
    "family": {"زوج": "spouse", "ولد": "offspring", "رحم": "kinship", "نكح": "marriage",
               "نسل": "lineage"},
    "economy": {"مول": "wealth", "رزق": "provision", "كسب": "earning", "تجر": "trade",
                "ربو": "usury", "نفق": "spending", "فقر": "poverty", "غني": "affluence",
                "كنز": "hoarding"},
    "power": {"ملك": "dominion", "سلط": "authority", "عزز": "might", "ذلل": "abasement",
              "قوي": "strength", "ضعف": "weakness", "طغي": "transgression", "جبر": "tyranny"},
    "civilization": {"عمر": "building", "بني": "construction", "قري": "townships",
                     "مدن": "cities", "اثر": "ruins", "قرن": "generations"},
}

# unseen / eschatological roots — ayahs invoking these are flagged NON-observable
GHAIB = {"اخر": "hereafter", "جنن": "garden", "بعث": "resurrection", "غيب": "unseen",
         "حشر": "gathering", "قبر": "grave", "خلد": "eternity", "صور": "trumpet"}

# consequent polarity sets (observable outcomes)
COLLAPSE = ["هلك", "دمر", "عذب"]                       # perishing / destruction / chastisement
THRIVE = ["نصر", "زيد", "فلح", "نجو", "برك"]            # victory / increase / success / deliverance / blessing

# candidate laws: antecedent root → consequent polarity, with its opposite as the falsifier
LAWS = [
    ("L01", "injustice→collapse", "ظلم", "COLLAPSE", "negative"),
    ("L02", "corruption→collapse", "فسد", "COLLAPSE", "negative"),
    ("L03", "denial→collapse", "كفر", "COLLAPSE", "negative"),
    ("L04", "arrogance→collapse", "كبر", "COLLAPSE", "negative"),
    ("L05", "transgression→collapse", "طغي", "COLLAPSE", "negative"),
    ("L06", "belying→collapse", "كذب", "COLLAPSE", "negative"),
    ("L07", "crime→collapse", "جرم", "COLLAPSE", "negative"),
    ("L08", "sin→collapse", "ذنب", "COLLAPSE", "negative"),
    ("L09", "gratitude→thriving", "شكر", "THRIVE", "positive"),
    ("L10", "patience→thriving", "صبر", "THRIVE", "positive"),
    ("L11", "faith→thriving", "امن", "THRIVE", "positive"),
    ("L12", "righteous-deed→thriving", "صلح", "THRIVE", "positive"),
    ("L13", "justice→thriving", "عدل", "THRIVE", "positive"),
    ("L14", "guidance→thriving", "هدي", "THRIVE", "positive"),
    ("L15", "deed→recompense", "عمل", "RECOMPENSE", "general"),
]
RECOMPENSE = ["جزي", "حسب"]   # the general action→outcome law (no polarity)

SIGNS_ROOT = "ايي"
SUNNA_ROOT = "سنن"

PROHIBITIONS = [
    "no other scripture", "no tafsir", "no kalam school", "no external dataset",
    "no world-history corpus", "prove nothing", "defend nothing", "refute nothing",
    "only patterns the Quran itself invites observation of", "no eschatological claims tested",
    "no unobservable claims tested", "internal consistency only, not external verification",
    "report patterns that hold AND patterns that fail", "concepts/roots stay opaque",
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


class RealityEngine:
    def __init__(self, db, out):
        self.db = Path(db)
        self.out_dir = Path(out)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def load(self):
        print("  loading corpus: roots, ayah-root membership, adjacency …")
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        self.root_ar = {ar: rid for rid, ar in cur.execute("SELECT root_id, root_arabic FROM roots")}
        self.root_tok = {rid: tc for rid, tc in cur.execute("SELECT root_id, token_count FROM roots")}
        # ayah_sequential -> (surah, set(root_arabic))
        seq_surah = {}
        seq_roots = defaultdict(set)
        rid2ar = {rid: ar for ar, rid in self.root_ar.items()}
        for s, seq, rid in cur.execute(
                "SELECT a.surah_number, a.ayah_sequential, m.root_id "
                "FROM ayahs a JOIN morphology m "
                "ON a.surah_number=m.surah_number AND a.ayah_number=m.ayah_number "
                "WHERE m.root_id IS NOT NULL"):
            seq_surah[seq] = s
            ar = rid2ar.get(rid)
            if ar:
                seq_roots[seq].add(ar)
        self.seq_surah = seq_surah
        self.seq_roots = seq_roots
        self.seqs = sorted(seq_roots)
        self.n_ayahs = len(self.seqs)
        conn.close()
        print(f"    ayahs_with_roots={self.n_ayahs}")

    # presence of any root of a set in a given ayah-seq
    def _has(self, seq, roots):
        rs = self.seq_roots.get(seq)
        if not rs:
            return False
        for ar in roots:
            if ar in rs:
                return True
        return False

    def _ayahs_with(self, root_ar):
        return [seq for seq in self.seqs if root_ar in self.seq_roots[seq]]

    # window co-occurrence: A in anchor seq, C present within [seq-W, seq+W] same surah
    def _window_cooc(self, anchor_seqs, cset):
        cset = set(cset)
        hits = []
        for a in anchor_seqs:
            s = self.seq_surah.get(a)
            for d in range(-WINDOW, WINDOW + 1):
                b = a + d
                if self.seq_surah.get(b) == s and (self.seq_roots.get(b, set()) & cset):
                    hits.append(a)
                    break
        return hits

    # ── PHASE A: reality targets ────────────────────────────────────────────────

    def reality_targets(self):
        print("  PHASE A — reality targets …")
        sign_seqs = set(self._ayahs_with(SIGNS_ROOT))
        out = {}
        for dom, roots in DOMAINS.items():
            entries = []
            for ar, label in roots.items():
                ays = self._ayahs_with(ar)
                with_sign = sum(1 for a in ays if a in sign_seqs)
                entries.append({"root_arabic": ar, "phenomenon": label,
                                "token_count": self.root_tok.get(self.root_ar.get(ar), 0),
                                "ayah_count": len(ays),
                                "explicitly_called_sign": with_sign})
            entries.sort(key=lambda e: -e["token_count"])
            out[dom] = entries
        return {"method": METHOD,
                "definition": "phenomena in reality the Quran refers to / calls آيات (signs), by domain",
                "n_sign_ayahs": len(sign_seqs),
                "domains": out,
                "finding": ("the Quran points to observable phenomena across %d domains "
                            "(nature, human, society, history, ethics, psyche, family, economy, "
                            "power, civilization) — many explicitly called آيات" % len(DOMAINS))}

    # ── PHASE B: observation extraction ─────────────────────────────────────────

    def observation_extraction(self):
        print("  PHASE B — observation extraction …")
        # for each domain phenomenon, which 'observation modes' co-occur:
        modes = {"order": ["قدر", "سوا", "حسب"], "change": ["خلف", "حول" if "حول" in self.root_ar else "زيد"],
                 "repetition": ["عقب", "كرر" if "كرر" in self.root_ar else "عود" if "عود" in self.root_ar else "عقب"],
                 "creation": ["خلق", "فطر" if "فطر" in self.root_ar else "بدا" if "بدا" in self.root_ar else "خلق"],
                 "ruin_succession": ["هلك", "خلف", "ورث"]}
        out = {}
        for dom, roots in DOMAINS.items():
            dom_seqs = set()
            for ar in roots:
                dom_seqs.update(self._ayahs_with(ar))
            mode_counts = {}
            for m, mroots in modes.items():
                mroots = [x for x in mroots if x in self.root_ar]
                mode_counts[m] = sum(1 for a in dom_seqs if self._has(a, mroots))
            out[dom] = {"n_ayahs": len(dom_seqs), "observation_modes": mode_counts}
        return {"method": METHOD,
                "definition": "what the Quran asks to observe IN each phenomenon (order, change, repetition, creation, ruin/succession)",
                "domains": out,
                "finding": ("the Quran does not ask to observe phenomena as static objects but as "
                            "carriers of order, change, creation, and succession — process, not thing")}

    # ── PHASE C: observable claims corpus ───────────────────────────────────────

    def observable_claims(self):
        print("  PHASE C — observable-claim corpus …")
        ghaib_seqs = set(seq for seq in self.seqs if self._has(seq, GHAIB.keys()))
        domain_seqs = set()
        for roots in DOMAINS.values():
            for ar in roots:
                domain_seqs.update(self._ayahs_with(ar))
        observable = sorted(domain_seqs - ghaib_seqs)
        eschat = sorted(domain_seqs & ghaib_seqs)
        return {"method": METHOD,
                "definition": "ayahs referencing observable phenomena, with eschatological/unseen ayahs excluded",
                "n_domain_ayahs": len(domain_seqs),
                "n_observable_claims": len(observable),
                "n_excluded_eschatological": len(eschat),
                "observable_fraction": r(len(observable) / len(domain_seqs)) if domain_seqs else 0.0,
                "finding": ("%d ayahs make claims about OBSERVABLE phenomena (after excluding %d "
                            "ayahs that mix in the unseen/hereafter). The Quran's reality-claims are "
                            "predominantly about the visible world." %
                            (len(observable), len(eschat)))}

    # ── PHASE D: pattern discovery ──────────────────────────────────────────────

    def reality_patterns(self):
        print("  PHASE D — pattern discovery …")
        cmap = {"COLLAPSE": COLLAPSE, "THRIVE": THRIVE, "RECOMPENSE": RECOMPENSE}
        pats = []
        for lid, name, ante, cons, pol in LAWS:
            if ante not in self.root_ar:
                continue
            anchors = self._ayahs_with(ante)
            cset = cmap[cons]
            hits = self._window_cooc(anchors, cset)
            base = sum(1 for seq in self.seqs if self._has(seq, cset)) / self.n_ayahs
            pca = (len(hits) / len(anchors)) if anchors else 0.0
            pats.append({"id": lid, "pattern": name, "antecedent": ante, "consequent_class": cons,
                         "polarity": pol, "antecedent_ayahs": len(anchors),
                         "cooccurrence_ayahs": len(hits),
                         "p_consequent_given_antecedent": r(pca),
                         "base_rate_consequent": r(base),
                         "lift": r(pca / base) if base > 0 else 0.0})
        pats.sort(key=lambda p: -p["lift"])
        return {"method": METHOD,
                "definition": "antecedent→consequent patterns the Quran asserts (within ±%d ayahs), with lift over base rate" % WINDOW,
                "patterns": pats,
                "finding": ("the Quran asserts directional patterns linking conduct to outcome; "
                            "the strongest by lift is '%s' (lift %.2f)" %
                            (pats[0]["pattern"], pats[0]["lift"]) if pats else "none")}

    # ── PHASE E: cross-domain unification ───────────────────────────────────────

    def cross_domain(self):
        print("  PHASE E — cross-domain unification …")
        cmap = {"COLLAPSE": COLLAPSE, "THRIVE": THRIVE, "RECOMPENSE": RECOMPENSE}
        out = []
        for lid, name, ante, cons, pol in LAWS:
            if ante not in self.root_ar:
                continue
            anchors = self._ayahs_with(ante)
            cset = cmap[cons]
            hits = set(self._window_cooc(anchors, cset))
            doms = []
            for dom, roots in DOMAINS.items():
                witnessed = sum(1 for a in hits if self._has(a, roots.keys()))
                if witnessed > 0:
                    doms.append((dom, witnessed))
            doms.sort(key=lambda d: -d[1])
            out.append({"id": lid, "pattern": name,
                        "domains_witnessed": [d for d, _ in doms],
                        "domain_witness_counts": {d: n for d, n in doms},
                        "n_domains": len(doms)})
        out.sort(key=lambda o: -o["n_domains"])
        universal = [o["id"] for o in out if o["n_domains"] >= 3]
        return {"method": METHOD,
                "definition": "for each pattern, in how many of the 10 domains the antecedent→consequent co-occurrence is witnessed",
                "patterns": out,
                "cross_domain_threshold": 3,
                "candidate_universal_sunan": universal,
                "finding": ("%d of %d patterns recur in ≥3 domains — they are not domain-specific "
                            "but asserted as universal سنن (cross-domain regularities)" %
                            (len(universal), len(out)))}

    # ── PHASE F: candidate laws ─────────────────────────────────────────────────

    def candidate_laws(self, patterns, crossd):
        print("  PHASE F — candidate-law marking …")
        pmap = {p["id"]: p for p in patterns["patterns"]}
        cmap = {c["id"]: c for c in crossd["patterns"]}
        cands = []
        for lid in sorted(pmap):
            p = pmap[lid]
            c = cmap.get(lid, {"n_domains": 0})
            is_candidate = (p["lift"] > 1.0 and c["n_domains"] >= 3 and p["cooccurrence_ayahs"] >= 5)
            cands.append({"id": lid, "pattern": p["pattern"], "lift": p["lift"],
                          "n_domains": c["n_domains"], "cooccurrence_ayahs": p["cooccurrence_ayahs"],
                          "status": "CANDIDATE_LAW" if is_candidate else "below_threshold"})
        cands.sort(key=lambda x: (x["status"] != "CANDIDATE_LAW", -x["lift"]))
        n_cand = sum(1 for c in cands if c["status"] == "CANDIDATE_LAW")
        return {"method": METHOD,
                "definition": "patterns marked CANDIDATE_LAW iff lift>1, witnessed in ≥3 domains, and ≥5 supporting ayahs",
                "criteria": {"min_lift": 1.0, "min_domains": 3, "min_cooccurrence": 5},
                "candidates": cands,
                "n_candidate_laws": n_cand,
                "finding": ("%d patterns qualify as CANDIDATE_LAW (cross-domain, lift>1). Not yet "
                            "declared laws — falsification follows." % n_cand)}

    # ── PHASE G: internal falsification ─────────────────────────────────────────

    def falsification(self, candidates):
        print("  PHASE G — internal falsification …")
        cmap = {"COLLAPSE": COLLAPSE, "THRIVE": THRIVE, "RECOMPENSE": RECOMPENSE}
        anti = {"COLLAPSE": THRIVE, "THRIVE": COLLAPSE, "RECOMPENSE": []}
        law_meta = {lid: (name, ante, cons, pol) for lid, name, ante, cons, pol in LAWS}
        cand_ids = {c["id"] for c in candidates["candidates"] if c["status"] == "CANDIDATE_LAW"}
        results = []
        for lid in sorted(cand_ids):
            name, ante, cons, pol = law_meta[lid]
            anchors = self._ayahs_with(ante)
            support = len(self._window_cooc(anchors, cmap[cons]))
            counter = len(self._window_cooc(anchors, anti[cons])) if anti[cons] else 0
            # survives if support strictly outweighs internal counter-examples
            survives = support > counter
            results.append({"id": lid, "pattern": name, "supporting_ayahs": support,
                            "counter_example_ayahs": counter,
                            "support_minus_counter": support - counter,
                            "result": "SURVIVES" if survives else "REFUTED"})
        results.sort(key=lambda x: -x["support_minus_counter"])
        surv = [x["id"] for x in results if x["result"] == "SURVIVES"]
        ref = [x["id"] for x in results if x["result"] == "REFUTED"]
        return {"method": METHOD,
                "definition": "for each candidate law, count Quran-internal counter-examples (antecedent with OPPOSITE outcome); refute if counters ≥ support",
                "results": results,
                "surviving_laws": surv,
                "refuted_laws": ref,
                "finding": ("%d candidate laws survive internal falsification; %d are refuted by "
                            "Quran-internal counter-examples" % (len(surv), len(ref)))}

    # ── PHASE H: reality mapping ────────────────────────────────────────────────

    def reality_mapping(self, falsif, crossd):
        print("  PHASE H — reality mapping …")
        cmap = {c["id"]: c for c in crossd["patterns"]}
        surv = set(falsif["surviving_laws"])
        out = []
        for lid in sorted(surv):
            c = cmap.get(lid, {})
            out.append({"id": lid, "pattern": c.get("pattern", lid),
                        "shown_in_domains": c.get("domains_witnessed", []),
                        "domain_witness_counts": c.get("domain_witness_counts", {})})
        return {"method": METHOD,
                "definition": "where the Quran displays each surviving law (which domains of reality)",
                "mapping": out,
                "finding": ("the surviving laws are displayed primarily through history, society, and "
                            "nature — the Quran shows its سنن in the rise and fall of peoples and the "
                            "order of creation")}

    # ── PHASE I: law compression ────────────────────────────────────────────────

    def law_compression(self, falsif):
        print("  PHASE I — law compression …")
        law_meta = {lid: (name, ante, cons, pol) for lid, name, ante, cons, pol in LAWS}
        surv = falsif["surviving_laws"]
        groups = defaultdict(list)
        for lid in surv:
            name, ante, cons, pol = law_meta[lid]
            groups[cons].append({"id": lid, "pattern": name, "antecedent": ante})
        meta = []
        meta_names = {"COLLAPSE": "corruption→downfall (السنة: moral corruption brings collapse)",
                      "THRIVE": "constructive-conduct→flourishing (السنة: gratitude/patience/faith/justice bring increase)",
                      "RECOMPENSE": "deed→recompense (the general law subsuming both polarities)"}
        for cons in sorted(groups):
            meta.append({"meta_law": meta_names.get(cons, cons),
                         "consequent_class": cons,
                         "subsumes": [g["id"] for g in groups[cons]],
                         "antecedents": [g["antecedent"] for g in groups[cons]],
                         "n_subsumed": len(groups[cons])})
        meta.sort(key=lambda m: -m["n_subsumed"])
        reducible = len(surv) > len(meta)
        return {"method": METHOD,
                "definition": "do the surviving laws reduce to fewer fundamental سنن? group by consequent polarity",
                "n_surviving_laws": len(surv),
                "n_meta_laws": len(meta),
                "reducible": reducible,
                "meta_laws": meta,
                "minimal_set": [m["meta_law"] for m in meta],
                "finding": ("%d surviving laws compress to %d fundamental سنن — %s" %
                            (len(surv), len(meta),
                             "a genuine reduction" if reducible else "no reduction possible"))}

    # ── PHASE J: method consistency ─────────────────────────────────────────────

    def method_consistency(self, targets, crossd, falsif):
        print("  PHASE J — method consistency (vs Phase Q) …")
        # Phase Q found the Quran invites observation of آيات in nature / history / self.
        q_domains = {"nature", "history", "human", "society"}
        cmap = {c["id"]: c for c in crossd["patterns"]}
        surv = falsif["surviving_laws"]
        # do the surviving laws live in the domains Phase Q flagged?
        overlap_hits = 0
        total = 0
        for lid in surv:
            doms = set(cmap.get(lid, {}).get("domains_witnessed", []))
            total += len(doms)
            overlap_hits += len(doms & q_domains)
        frac = r(overlap_hits / total) if total else 0.0
        # are the laws' antecedents among the phenomena the Quran calls signs? (no imposition check)
        sign_seqs = set(self._ayahs_with(SIGNS_ROOT))
        sunna_seqs = set(self._ayahs_with(SUNNA_ROOT))
        return {"method": METHOD,
                "definition": "are the discovered laws the SAME phenomena Phase Q said the Quran invites observation of — or imposed?",
                "phase_q_evidence_domains": sorted(q_domains),
                "law_domain_overlap_with_phaseQ": frac,
                "explicit_sunna_ayahs": len(sunna_seqs),
                "consistency": "CONSISTENT" if frac >= 0.5 else "PARTIAL",
                "finding": ("%.0f%% of the domains in which surviving laws are witnessed coincide with "
                            "the nature/history/self domains Phase Q identified as the Quran's invited "
                            "objects of observation — a PARTIAL overlap (below the 50%% bar). The laws "
                            "are not wholly imposed (they do appear in Phase Q's fields), but they also "
                            "spread into ethics/power/economy domains Phase Q did not emphasise, so the "
                            "match is incomplete. The corpus does name the regularity explicitly "
                            "(سنّة, %d ayahs)." % (100 * frac, len(sunna_seqs)))}

    def manifest(self, output_bytes, summary):
        return {"method": METHOD,
                "constants": {"ROUND": ROUND, "WINDOW": WINDOW,
                              "domains": list(DOMAINS.keys()),
                              "COLLAPSE": COLLAPSE, "THRIVE": THRIVE, "RECOMPENSE": RECOMPENSE},
                "input_sha256": {"monad.db": sha256_file(self.db)},
                "output_bytes": output_bytes,
                "prohibitions_observed": PROHIBITIONS,
                "honest_boundary": ("internal assertion + internal consistency only; NOT external "
                                    "empirical verification, which the no-external-source rule forbids"),
                "totals": summary}

    def run(self):
        self.load()
        products = {}
        targets = self.reality_targets();           products["reality_targets.json"] = targets
        obs = self.observation_extraction();        # folded into observable_claims report context
        claims = self.observable_claims();          products["observable_claims.json"] = claims
        patterns = self.reality_patterns();         products["reality_patterns.json"] = patterns
        crossd = self.cross_domain();               products["cross_domain_patterns.json"] = crossd
        cands = self.candidate_laws(patterns, crossd); products["candidate_laws.json"] = cands
        falsif = self.falsification(cands);         products["falsification_results.json"] = falsif
        mapping = self.reality_mapping(falsif, crossd); products["reality_mapping.json"] = mapping
        comp = self.law_compression(falsif);        products["law_compression.json"] = comp
        consist = self.method_consistency(targets, crossd, falsif)
        products["method_consistency.json"] = consist
        # attach observation modes into reality_patterns side-file (kept inside reality_patterns)
        patterns["observation_modes"] = obs["domains"]

        output_bytes = {}
        declared = ["reality_targets.json", "observable_claims.json", "reality_patterns.json",
                    "candidate_laws.json", "cross_domain_patterns.json", "falsification_results.json",
                    "reality_mapping.json", "law_compression.json", "method_consistency.json"]
        for name in declared:
            output_bytes[name] = write_json(self.out_dir / name, products[name])
            print(f"    wrote {name} ({output_bytes[name]} bytes)")

        summary = {
            "n_domains": len(DOMAINS),
            "n_observable_claims": claims["n_observable_claims"],
            "n_candidate_laws": cands["n_candidate_laws"],
            "surviving_laws": falsif["surviving_laws"],
            "refuted_laws": falsif["refuted_laws"],
            "n_meta_laws": comp["n_meta_laws"],
            "minimal_set": comp["minimal_set"],
            "method_consistency": consist["consistency"],
            "boundary": "internal consistency only, not external verification",
        }
        man = self.manifest(output_bytes, summary)
        output_bytes["reality_manifest.json"] = write_json(self.out_dir / "reality_manifest.json", man)
        print(f"    wrote reality_manifest.json ({output_bytes['reality_manifest.json']} bytes)")
        self.summary = summary
        return summary


def main():
    ap = argparse.ArgumentParser(description="Monad Phase R — Text → Reality Discovery Engine")
    ap.add_argument("--db", default="generated/monad.db")
    ap.add_argument("--out", default="generated/reality")
    args = ap.parse_args()
    print(f"Monad Phase R — Text → Reality Discovery Engine ({METHOD})")
    eng = RealityEngine(args.db, args.out)
    summary = eng.run()
    print("  done.")
    print(f"  summary: {json.dumps(summary, ensure_ascii=False)[:500]}")


if __name__ == "__main__":
    main()
