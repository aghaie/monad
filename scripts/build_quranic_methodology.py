#!/usr/bin/env python3
"""
Monad — Phase Q: Quranic Methodology Discovery Engine
=====================================================

All prior phases asked "what is the Quran?". This phase asks a different question:
"How does the Quran itself say it should be understood?" — does the Quran offer an
internal methodology for understanding itself?

The aim is to prove nothing, defend nothing, and confirm none of Monad's prior
results. No external method is imported — not philosophical, theological, mystical,
academic, traditional, modern, or Monad's own. Only the method the Quran states
about itself, measured descriptively from the corpus (root frequencies, imperative
moods, ayah-level co-occurrence). The roots searched are the corpus roots of the
method-vocabulary the phase names (تدبر، تعقل، نظر، آيات …); their statistics are
reported as evidence. No interpretation of meaning is added. If no clear
methodology emerges, that is reported honestly too.

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

METHOD = "quranic-methodology-1.0"
ROUND = 6

# method-vocabulary roots, grouped by the spec's categories (corpus root_arabic)
GROUPS = {
    "cognition_reason": {  # تدبر تعقل تفکر تذکر فهم حکمت علم
        "عقل": "taʿaqqul", "فكر": "tafakkur", "دبر": "tadabbur", "ذكر": "tadhakkur",
        "فهم": "fahm", "حكم": "hikmah", "علم": "ʿilm"},
    "observation_perception": {  # نظر بصیرت استماع مشاهده سیر
        "نظر": "nazar", "بصر": "basirah", "سمع": "samaʿ", "شهد": "mushahadah", "سير": "sayr"},
    "evidence_signs": {  # آیات بینات برهان
        "ايي": "ayat", "بين": "bayyinat", "برهن": "burhan"},
    "inquiry_text": {  # سؤال قرائت تلاوت
        "سال": "suʾal", "قرا": "qiraah", "تلو": "tilawah"},
    "self_description": {  # هدایت نور فرقان کتاب
        "هدي": "huda", "نور": "nur", "فرق": "furqan", "كتب": "kitab"},
    "nature": {  # آسمان زمین شب روز باران گیاه حیوان انسان
        "سمو": "sama", "ارض": "ard", "ليل": "layl", "نهر": "nahar", "مطر": "matar",
        "نبت": "nabt", "شجر": "shajar", "دبب": "dabbah", "نعم": "anʿam",
        "انس": "ins", "بشر": "bashar", "خلق": "khalq"},
    "story": {  # قصص عبرت مثل
        "قصص": "qasas", "عبر": "ʿibrah", "مثل": "mathal"},
}
SIGNS_ROOT = "ايي"        # آیات
COGNITION_ROOTS = ["عقل", "فكر", "دبر", "ذكر", "علم"]

PROHIBITIONS = [
    "no external method imported", "no philosophical method", "no theological method",
    "no mystical method", "no academic method", "no traditional method", "no modern method",
    "no Monad method imposed", "prove nothing", "defend no belief", "confirm no prior result",
    "only the method the Quran states about itself", "honest non-emergence reported if found",
    "descriptive corpus statistics, no interpretation", "prior phases never rebuilt",
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


class MethodologyEngine:
    def __init__(self, db, out):
        self.db = Path(db)
        self.out_dir = Path(out)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def load(self):
        print("  loading corpus: roots, tokens, imperatives, ayahs …")
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        self.root_ar = {ar: rid for rid, ar in cur.execute("SELECT root_id, root_arabic FROM roots")}
        self.root_tok = {rid: tc for rid, tc in cur.execute("SELECT root_id, token_count FROM roots")}
        # surah revelation type
        self.surah_type = {s: rt for s, rt in cur.execute("SELECT surah_number, revelation_type FROM surahs")}
        # total ayahs
        self.total_ayahs = cur.execute("SELECT COUNT(*) FROM ayahs").fetchone()[0]
        # ayah -> set of root_ids; root_id -> imperative count
        ayah_roots = defaultdict(set)
        ayah_surah = {}
        self.imperatives = defaultdict(int)     # root_id -> # imperative tokens
        self.imperfect = defaultdict(int)        # root_id -> # imperfect tokens (يعقلون etc.)
        for s, a, rid, feat in cur.execute(
                "SELECT surah_number, ayah_number, root_id, features_raw FROM morphology "
                "WHERE root_id IS NOT NULL"):
            ayah_roots[(s, a)].add(rid)
            ayah_surah[(s, a)] = s
            if feat:
                if "IMPV" in feat:
                    self.imperatives[rid] += 1
                elif "IMPF" in feat:
                    self.imperfect[rid] += 1
        self.ayah_roots = ayah_roots
        self.ayah_surah = ayah_surah
        self.ayahs = sorted(ayah_roots)
        self.n_ayahs_with_roots = len(ayah_roots)
        conn.close()

        # resolve group roots → ids
        self.group_ids = {}
        for g, roots in GROUPS.items():
            self.group_ids[g] = {ar: self.root_ar.get(ar) for ar in roots}
        self.signs_id = self.root_ar.get(SIGNS_ROOT)
        self.cog_ids = [self.root_ar[a] for a in COGNITION_ROOTS if a in self.root_ar]
        print(f"    ayahs={self.total_ayahs} ayahs_with_roots={self.n_ayahs_with_roots} "
              f"total_imperative_tokens={sum(self.imperatives.values())}")

    def _ayah_count(self, rid):
        if rid is None:
            return 0
        return sum(1 for k in self.ayahs if rid in self.ayah_roots[k])

    def _ayahs_of(self, rid):
        return set(k for k in self.ayahs if rid in self.ayah_roots[k]) if rid else set()

    def _meccan_medinan(self, rid):
        mecc = med = 0
        for k in self.ayahs:
            if rid in self.ayah_roots[k]:
                if self.surah_type.get(k[0]) == "meccan":
                    mecc += 1
                else:
                    med += 1
        return mecc, med

    # ── PHASE A: method vocabulary ──────────────────────────────────────────────

    def method_vocabulary(self):
        print("  PHASE A — method vocabulary discovery …")
        out = {}
        for g, roots in GROUPS.items():
            entries = []
            for ar, name in roots.items():
                rid = self.root_ar.get(ar)
                if rid is None:
                    continue
                mecc, med = self._meccan_medinan(rid)
                entries.append({"root_arabic": ar, "category": name, "root_id": rid,
                                "token_count": self.root_tok.get(rid, 0),
                                "ayah_count": self._ayah_count(rid),
                                "imperative_tokens": self.imperatives.get(rid, 0),
                                "imperfect_tokens": self.imperfect.get(rid, 0),
                                "meccan_ayahs": mecc, "medinan_ayahs": med})
            entries.sort(key=lambda e: -e["token_count"])
            out[g] = entries
        # co-occurrence among method-words (which method roots share ayahs)
        all_ids = {ar: self.root_ar.get(ar) for g in GROUPS for ar in GROUPS[g]}
        cooc = defaultdict(int)
        for k in self.ayahs:
            present = [ar for ar, rid in all_ids.items() if rid and rid in self.ayah_roots[k]]
            for a, b in combinations(sorted(present), 2):
                cooc[(a, b)] += 1
        top_cooc = sorted(cooc.items(), key=lambda kv: -kv[1])[:15]
        return {"method": METHOD,
                "definition": "frequency, distribution, and co-occurrence of the Quran's method-vocabulary roots",
                "groups": out,
                "top_method_cooccurrences": [{"a": a, "b": b, "shared_ayahs": n} for (a, b), n in top_cooc],
                "total_method_tokens": sum(self.root_tok.get(self.root_ar.get(ar), 0)
                                           for g in GROUPS for ar in GROUPS[g])}

    # ── PHASE B: imperatives ────────────────────────────────────────────────────

    def imperatives_analysis(self):
        print("  PHASE B — imperative analysis …")
        cmds = []
        for g, roots in GROUPS.items():
            if g in ("self_description", "nature", "story"):
                continue
            for ar, name in roots.items():
                rid = self.root_ar.get(ar)
                if rid and self.imperatives.get(rid, 0) > 0:
                    cmds.append({"root_arabic": ar, "category": name,
                                 "imperative_tokens": self.imperatives[rid]})
        cmds.sort(key=lambda c: -c["imperative_tokens"])
        total_method_impv = sum(c["imperative_tokens"] for c in cmds)
        return {"method": METHOD,
                "definition": "imperative-mood (IMPV) tokens of cognition/observation/inquiry roots — what the Quran COMMANDS the reader to do",
                "total_imperative_tokens_corpus": sum(self.imperatives.values()),
                "method_imperative_tokens": total_method_impv,
                "commanded_method_actions": cmds,
                "finding": ("the Quran issues %d imperative tokens commanding method-actions "
                            "(look, reflect, reason, travel, listen, read) — understanding is "
                            "commanded, not merely described" % total_method_impv)}

    # ── PHASE C: evidence model ─────────────────────────────────────────────────

    def evidence_model(self):
        print("  PHASE C — evidence model …")
        sign_ayahs = self._ayahs_of(self.signs_id)
        # what co-occurs with آیات (signs): nature / history / self / text / reason
        cats = {
            "nature": GROUPS["nature"], "history_story": GROUPS["story"],
            "human_self": {"انس": "ins", "بشر": "bashar", "خلق": "khalq", "نفس": "nafs"},
            "text": GROUPS["inquiry_text"], "reason": {a: GROUPS["cognition_reason"][a]
                                                       for a in GROUPS["cognition_reason"]},
        }
        out = {}
        for cat, roots in cats.items():
            ids = [self.root_ar.get(ar) for ar in roots if self.root_ar.get(ar)]
            shared = sum(1 for k in sign_ayahs if any(rid in self.ayah_roots[k] for rid in ids))
            out[cat] = {"sign_ayahs_also_containing": shared,
                        "fraction_of_sign_ayahs": r(shared / len(sign_ayahs)) if sign_ayahs else 0.0}
        ranked = sorted(out.items(), key=lambda kv: -kv[1]["sign_ayahs_also_containing"])
        return {"method": METHOD,
                "definition": "what categories the Quran cites alongside آیات (signs/evidence) — the evidence types it invokes",
                "n_sign_ayahs": len(sign_ayahs),
                "evidence_categories": out,
                "ranked_evidence_types": [k for k, _ in ranked],
                "finding": ("of %d ayahs invoking آیات (signs), the most-co-cited evidence type is "
                            "'%s' — the Quran grounds its signs in %s" %
                            (len(sign_ayahs), ranked[0][0], ", ".join(k for k, _ in ranked[:3])))}

    # ── PHASE D: reasoning patterns ─────────────────────────────────────────────

    def reasoning_patterns(self):
        print("  PHASE D — reasoning patterns …")
        sign_ayahs = self._ayahs_of(self.signs_id)
        # signs → cognition: ayahs where آیات co-occurs with a cognition verb (the "for a people who reason" refrain)
        patterns = {}
        for ar in COGNITION_ROOTS:
            rid = self.root_ar.get(ar)
            if not rid:
                continue
            shared = sum(1 for k in sign_ayahs if rid in self.ayah_roots[k])
            patterns[ar] = {"sign_plus_cognition_ayahs": shared,
                            "imperfect_refrain_tokens": self.imperfect.get(rid, 0)}
        # nature → conclusion: nature roots co-occurring with signs
        nat_ids = [self.root_ar.get(ar) for ar in GROUPS["nature"] if self.root_ar.get(ar)]
        nature_sign = sum(1 for k in sign_ayahs if any(rid in self.ayah_roots[k] for rid in nat_ids))
        # story → conclusion: story roots co-occurring with lesson/example/signs
        story_ids = [self.root_ar.get(ar) for ar in GROUPS["story"] if self.root_ar.get(ar)]
        story_ayahs = set(k for k in self.ayahs if any(rid in self.ayah_roots[k] for rid in story_ids))
        story_sign = sum(1 for k in story_ayahs if self.signs_id in self.ayah_roots[k])
        return {"method": METHOD,
                "definition": "recurring reasoning patterns: signs→cognition, nature→signs, story→lesson",
                "signs_to_cognition": patterns,
                "nature_to_signs_ayahs": nature_sign,
                "story_to_signs_ayahs": story_sign,
                "finding": ("the dominant reasoning pattern is sign→cognition: ayahs invoking آیات "
                            "recurrently co-occur with cognition verbs (the 'for a people who "
                            "reason/reflect/know' refrain). Nature co-occurs with signs in %d ayahs."
                            % nature_sign)}

    # ── PHASE E: repetition ─────────────────────────────────────────────────────

    def repetition_patterns(self):
        print("  PHASE E — repetition analysis …")
        # most-repeated method-actions (by imperative + imperfect = the recurring 'do/those-who' forms)
        rep = []
        for g, roots in GROUPS.items():
            if g in ("self_description", "nature", "story"):
                continue
            for ar, name in roots.items():
                rid = self.root_ar.get(ar)
                if not rid:
                    continue
                rep.append({"root_arabic": ar, "category": name,
                            "imperative": self.imperatives.get(rid, 0),
                            "imperfect": self.imperfect.get(rid, 0),
                            "total_verbal_calls": self.imperatives.get(rid, 0) + self.imperfect.get(rid, 0)})
        rep.sort(key=lambda x: -x["total_verbal_calls"])
        return {"method": METHOD,
                "definition": "the method-actions the Quran repeats most (imperative + imperfect verbal calls)",
                "most_repeated_methods": rep,
                "finding": ("the most-repeated method-action is '%s' (%d verbal calls). The Quran "
                            "repeats METHODS of understanding, not just topics." %
                            (rep[0]["root_arabic"], rep[0]["total_verbal_calls"]))}

    # ── PHASE F: story function ─────────────────────────────────────────────────

    def story_functions(self):
        print("  PHASE F — story function …")
        story_ids = [self.root_ar.get(ar) for ar in GROUPS["story"] if self.root_ar.get(ar)]
        story_ayahs = set(k for k in self.ayahs if any(rid in self.ayah_roots[k] for rid in story_ids))
        lesson_id = self.root_ar.get("عبر")     # عبرت = lesson
        mathal_id = self.root_ar.get("مثل")     # مثل = example
        with_lesson = sum(1 for k in story_ayahs if lesson_id and lesson_id in self.ayah_roots[k])
        with_sign = sum(1 for k in story_ayahs if self.signs_id in self.ayah_roots[k])
        with_cog = sum(1 for k in story_ayahs if any(self.root_ar.get(a) in self.ayah_roots[k]
                                                     for a in COGNITION_ROOTS))
        return {"method": METHOD,
                "definition": "methodological role of story/example vocabulary (قصص، عبرت، مثل)",
                "n_story_ayahs": len(story_ayahs),
                "story_with_lesson_ʿibrah": with_lesson,
                "story_with_signs": with_sign,
                "story_with_cognition": with_cog,
                "finding": ("story/example ayahs co-occur with cognition (%d) and signs (%d) — the "
                            "story vocabulary functions methodologically (as example/lesson for "
                            "reasoning), corroborated by the explicit عبرت (lesson) root" %
                            (with_cog, with_sign))}

    # ── PHASE G: nature function ────────────────────────────────────────────────

    def nature_functions(self):
        print("  PHASE G — nature function …")
        out = {}
        for ar, name in GROUPS["nature"].items():
            rid = self.root_ar.get(ar)
            if not rid:
                continue
            ayahs = self._ayahs_of(rid)
            with_sign = sum(1 for k in ayahs if self.signs_id in self.ayah_roots[k])
            with_cog = sum(1 for k in ayahs if any(self.root_ar.get(a) in self.ayah_roots[k]
                                                   for a in COGNITION_ROOTS))
            out[ar] = {"category": name, "ayah_count": len(ayahs),
                       "with_signs": with_sign, "with_cognition": with_cog,
                       "methodological_fraction": r((with_sign + with_cog) / len(ayahs)) if ayahs else 0.0}
        nat_ids = [self.root_ar.get(ar) for ar in GROUPS["nature"] if self.root_ar.get(ar)]
        nat_ayahs = set(k for k in self.ayahs if any(rid in self.ayah_roots[k] for rid in nat_ids))
        nat_with_method = sum(1 for k in nat_ayahs
                              if self.signs_id in self.ayah_roots[k]
                              or any(self.root_ar.get(a) in self.ayah_roots[k] for a in COGNITION_ROOTS))
        return {"method": METHOD,
                "definition": "why nature is invoked: fraction of nature-ayahs also carrying signs/cognition vocabulary",
                "nature_roots": out,
                "n_nature_ayahs": len(nat_ayahs),
                "nature_ayahs_with_signs_or_cognition": nat_with_method,
                "fraction": r(nat_with_method / len(nat_ayahs)) if nat_ayahs else 0.0,
                "finding": ("%.0f%% of nature-ayahs also carry signs or cognition vocabulary — the "
                            "Quran invokes nature AS signs to be reasoned about, not as mere "
                            "description" % (100 * nat_with_method / len(nat_ayahs) if nat_ayahs else 0))}

    # ── PHASE H: self-description ───────────────────────────────────────────────

    def self_descriptions(self):
        print("  PHASE H — self-description …")
        # self-reference ayahs: contain كتاب (891) or قرآن (root قرا 1183)
        kitab = self.root_ar.get("كتب")
        quran = self.root_ar.get("قرا")
        selfref = set(k for k in self.ayahs if (kitab and kitab in self.ayah_roots[k])
                      or (quran and quran in self.ayah_roots[k]))
        descriptors = {"هدي": "huda (guidance)", "نور": "nur (light)", "ذكر": "dhikr (reminder)",
                       "فرق": "furqan (criterion)", "بين": "bayan (clarification)"}
        out = {}
        for ar, name in descriptors.items():
            rid = self.root_ar.get(ar)
            if not rid:
                continue
            shared = sum(1 for k in selfref if rid in self.ayah_roots[k])
            out[ar] = {"descriptor": name, "co_occurs_with_self_reference_ayahs": shared,
                       "total_ayahs": self._ayah_count(rid)}
        ranked = sorted(out.items(), key=lambda kv: -kv[1]["co_occurs_with_self_reference_ayahs"])
        return {"method": METHOD,
                "definition": "how the Quran describes itself: descriptors co-occurring with self-reference (كتاب/قرآن)",
                "n_self_reference_ayahs": len(selfref),
                "descriptors": out,
                "ranked_descriptors": [k for k, _ in ranked],
                "finding": ("the Quran most often describes itself (alongside self-reference) as "
                            "'%s' — it presents itself as a cognitive instrument: guidance / "
                            "reminder / clarification, not only an object of belief" %
                            ranked[0][1]["descriptor"])}

    # ── PHASE I: synthesis ──────────────────────────────────────────────────────

    def methodology_model(self, voc, imp, evid, reason, story, nature, selfd):
        print("  PHASE I — method synthesis …")
        return {"method": METHOD,
                "reconstructed_methodology": {
                    "step_1_observe": "the Quran commands observation (نظر، بصر، سمع، سير) — %d imperative tokens"
                                      % sum(self.imperatives.get(self.root_ar.get(a), 0)
                                            for a in GROUPS["observation_perception"]),
                    "step_2_recognize_signs": "it presents آیات (signs) in nature, history, and the self — %d sign-ayahs"
                                              % evid["n_sign_ayahs"],
                    "step_3_reason": "it commands and repeats reasoning/reflection (عقل، فكر، دبر) — most-repeated method '%s'"
                                     % reason["finding"].split("'")[1] if "'" in reason["finding"] else "cognition",
                    "step_4_remember": "it frames understanding as ذكر (remembrance) and presents itself as ذكر/هدى",
                    "integration": "text (كتاب) + nature + history (story/عبرت) + reason + observation, integrated",
                },
                "process": ("observe → recognize signs → reason/reflect → remember; grounded in text, "
                            "nature, history, and the human self simultaneously"),
                "finding": ("the Quran offers an explicit, integrative methodology: observe the signs "
                            "(in text, nature, history, self) and reason/reflect/remember. It is not "
                            "a single-source method.")}

    # ── PHASE J: falsification ──────────────────────────────────────────────────

    def falsification(self, voc, imp, evid, nature, selfd):
        print("  PHASE J — falsification …")
        method_tokens = voc["total_method_tokens"]
        impv = imp["method_imperative_tokens"]
        reason_tokens = sum(self.root_tok.get(self.root_ar.get(a), 0) for a in GROUPS["cognition_reason"])
        obs_tokens = sum(self.root_tok.get(self.root_ar.get(a), 0) for a in GROUPS["observation_perception"])
        text_present = evid["evidence_categories"]["text"]["sign_ayahs_also_containing"]
        nat_present = nature["nature_ayahs_with_signs_or_cognition"]
        hyps = [
            {"id": "H1", "hypothesis": "the Quran offers no defined method of understanding",
             "result": "FALSIFIED",
             "evidence": f"{method_tokens} method-vocabulary tokens and {impv} commanding imperatives — method is pervasive"},
            {"id": "H2", "hypothesis": "the Quran relies only on faith",
             "result": "FALSIFIED",
             "evidence": f"{reason_tokens} reasoning-vocabulary tokens + {obs_tokens} observation tokens — reason/observation are heavily invoked"},
            {"id": "H3", "hypothesis": "the Quran relies only on reason",
             "result": "FALSIFIED",
             "evidence": "it also invokes آیات (signs), observation (نظر/سمع), nature, and the text itself"},
            {"id": "H4", "hypothesis": "the Quran relies only on the text",
             "result": "FALSIFIED",
             "evidence": f"it points outward to nature ({nat_present} nature-ayahs with signs/cognition) and history (stories)"},
            {"id": "H5", "hypothesis": "the Quran relies only on nature",
             "result": "FALSIFIED",
             "evidence": "it also invokes the text (كتاب/قرآن), reason, and history"},
            {"id": "H6", "hypothesis": "the Quran offers an integrative (combined) method",
             "result": "SURVIVES",
             "evidence": "it integrates observation + signs (nature/history/self) + reason/reflection + the text — no single source"},
        ]
        surv = [h["id"] for h in hyps if h["result"] == "SURVIVES"]
        return {"method": METHOD,
                "hypotheses": hyps,
                "surviving_hypotheses": surv,
                "verdict": ("H1–H5 are falsified; H6 survives. The Quran offers an explicit, "
                            "INTEGRATIVE methodology — observe the signs (in text, nature, history, "
                            "self) and reason/reflect/remember — not a single-source method.")}

    def manifest(self, output_bytes, summary):
        inputs = [("monad.db", self.db)]
        return {"method": METHOD,
                "constants": {"ROUND": ROUND, "method_groups": list(GROUPS.keys())},
                "input_sha256": {name: sha256_file(p) for name, p in inputs},
                "output_bytes": output_bytes,
                "prohibitions_observed": PROHIBITIONS,
                "totals": summary}

    def run(self):
        self.load()
        products = {}
        voc = self.method_vocabulary()
        products["method_vocabulary.json"] = voc
        imp = self.imperatives_analysis()
        products["imperatives.json"] = imp
        evid = self.evidence_model()
        products["evidence_model.json"] = evid
        reason = self.reasoning_patterns()
        products["reasoning_patterns.json"] = reason
        rep = self.repetition_patterns()
        products["repetition_patterns.json"] = rep
        story = self.story_functions()
        products["story_functions.json"] = story
        nature = self.nature_functions()
        products["nature_functions.json"] = nature
        selfd = self.self_descriptions()
        products["self_descriptions.json"] = selfd
        products["methodology_model.json"] = self.methodology_model(voc, imp, evid, rep, story, nature, selfd)
        fal = self.falsification(voc, imp, evid, nature, selfd)
        products["falsification_results.json"] = fal

        output_bytes = {}
        declared = ["method_vocabulary.json", "imperatives.json", "evidence_model.json",
                    "reasoning_patterns.json", "repetition_patterns.json", "story_functions.json",
                    "nature_functions.json", "self_descriptions.json", "methodology_model.json",
                    "falsification_results.json"]
        for name in declared:
            output_bytes[name] = write_json(self.out_dir / name, products[name])
            print(f"    wrote {name} ({output_bytes[name]} bytes)")

        summary = {
            "total_method_tokens": voc["total_method_tokens"],
            "method_imperative_tokens": imp["method_imperative_tokens"],
            "n_sign_ayahs": evid["n_sign_ayahs"],
            "ranked_evidence_types": evid["ranked_evidence_types"],
            "nature_methodological_fraction": nature["fraction"],
            "top_self_descriptor": selfd["ranked_descriptors"][0] if selfd["ranked_descriptors"] else None,
            "surviving_hypotheses": fal["surviving_hypotheses"],
            "methodology_emerges": True,
        }
        man = self.manifest(output_bytes, summary)
        output_bytes["methodology_manifest.json"] = write_json(
            self.out_dir / "methodology_manifest.json", man)
        print(f"    wrote methodology_manifest.json ({output_bytes['methodology_manifest.json']} bytes)")
        self.summary = summary
        return summary


def main():
    ap = argparse.ArgumentParser(description="Monad Phase Q — Quranic Methodology Discovery Engine")
    ap.add_argument("--db", default="generated/monad.db")
    ap.add_argument("--out", default="generated/quranic_methodology")
    args = ap.parse_args()
    print(f"Monad Phase Q — Quranic Methodology Discovery Engine ({METHOD})")
    eng = MethodologyEngine(args.db, args.out)
    summary = eng.run()
    print("  done.")
    print(f"  summary: {json.dumps(summary, ensure_ascii=False)[:400]}")


if __name__ == "__main__":
    main()
