#!/usr/bin/env python3
"""SERAPH Phase 1 — extract observable response-behavior events from the Quran text.

Everything here is a *structural* extraction from generated/monad.db:
no external dictionary, translation, or tafsir is consulted. The only
anchoring assumption (declared openly in the report) is the grammatical
function of a small set of high-frequency function patterns (imperative
'qul', interrogative particles), which the morphology table itself tags.

Outputs: generated/seraph/phase1_evidence.json
"""
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "generated" / "monad.db"
OUT_DIR = Path(__file__).resolve().parent.parent / "generated" / "seraph"
OUT_DIR.mkdir(parents=True, exist_ok=True)

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()

# dagger alif used in normalized text
DA = "ٰ"

def strip_marks(s: str) -> str:
    """Remove dagger alif for plain matching."""
    return s.replace(DA, "")

# ---- load all ayahs (normalized text) --------------------------------------
ayahs = {}
for r in cur.execute("SELECT surah_number s, ayah_number a, text_normalized t FROM ayahs"):
    ayahs[(r["s"], r["a"])] = strip_marks(r["t"])

def ref(s, a):
    return f"{s}:{a}"

evidence = {}

# ============================================================================
# E1 — explicit question->answer events: yas'alu(-naka/-ka) / yastaftunaka
#      normalized orthography drops hamza: يسلونك / يسلك / يستفتونك
# ============================================================================
# ayahs that actually contain the root sAl (1299) — kills slk false positives
sal_ayahs = {(r["s"], r["a"]) for r in cur.execute(
    "SELECT DISTINCT surah_number s, ayah_number a FROM words WHERE root_id=1299")}

qa_events = []
seen = set()
QA_PAT = re.compile(r"(يسلونك|ويسلونك|يسلك|ويسلك|يستفتونك|ويستفتونك)")
for (s, a), t in sorted(ayahs.items()):
    if (s, a) not in sal_ayahs:
        continue
    for m in QA_PAT.finditer(t):
        rest = t[m.end():]
        nxt = ayahs.get((s, a + 1), "")
        # classify the question construction
        if re.match(r"\s*(عن|في)\s", rest):
            kind = "info_question"
            topic = rest.split()[1] if len(rest.split()) > 1 else ""
        elif re.match(r"\s*ماذا\s", rest):
            kind = "info_question"
            topic = "ماذا " + (rest.split()[1] if len(rest.split()) > 1 else "")
        elif re.match(r"\s*ان\s", rest):
            kind = "demand"
            topic = " ".join(rest.split()[:4])
        elif re.match(r"\s*الناس عن\s", rest):
            kind = "info_question"
            topic = rest.split()[2] if len(rest.split()) > 2 else ""
        else:
            kind = "other_construction"
            topic = " ".join(rest.split()[:3])
        key = (s, a, kind, topic)
        if key in seen:
            continue
        seen.add(key)
        has_qul_same = bool(re.search(r"\b(قل|فقل)\b", rest))
        has_qul_next = bool(re.search(r"\b(قل|فقل)\b", nxt[:40]))
        qa_events.append({
            "ref": ref(s, a),
            "trigger": m.group(1),
            "kind": kind,
            "topic": topic,
            "text": t,
            "qul_in_same_ayah_after": has_qul_same,
            "qul_at_next_ayah_start": has_qul_next,
        })
evidence["E1_question_events"] = qa_events

# ============================================================================
# E2 — the 'qul' (imperative of qwl root, 2nd person) channel: how often the
#      speaker routes speech through the addressee-messenger
# ============================================================================
row = cur.execute(
    "SELECT COUNT(*) c FROM morphology WHERE root_id=1205 AND aspect='IMPV'"
).fetchone()
qul_impv_total = row["c"]
row = cur.execute(
    "SELECT COUNT(DISTINCT surah_number || ':' || ayah_number) c "
    "FROM morphology WHERE root_id=1205 AND aspect='IMPV' AND form_buckwalter='qul'"
).fetchone()
qul_exact_ayahs = row["c"]
evidence["E2_qul_channel"] = {
    "qwl_imperative_tokens_total": qul_impv_total,
    "ayahs_containing_exact_qul": qul_exact_ayahs,
}

# ============================================================================
# E3 — knowledge-relocation on hidden-timing questions:
#      ayahs with الساعة + علم + عند (knowledge placed with God)
# ============================================================================
sa_events = []
for (s, a), t in sorted(ayahs.items()):
    if "الساعه" in t or "الساعة" in t:
        if re.search(r"علم", t) and re.search(r"عند الله|عند ربي|الي ربك|اليه يرد", t):
            sa_events.append({"ref": ref(s, a), "text": t})
evidence["E3_hour_knowledge_relocation"] = sa_events

# ============================================================================
# E4 — observation imperatives: forms of n-Z-r as imperative (انظر/انظروا/فانظر…)
#      and the سيروا في الارض فانظروا chain
# ============================================================================
rows = cur.execute(
    "SELECT m.surah_number s, m.ayah_number a, m.form_buckwalter f "
    "FROM morphology m WHERE m.root_id=1056 AND m.aspect='IMPV'"
).fetchall()
nzr_impv = [{"ref": ref(r["s"], r["a"]), "form": r["f"]} for r in rows]
siru_unzuru = []
for (s, a), t in sorted(ayahs.items()):
    if re.search(r"سيروا في الارض", t):
        siru_unzuru.append({"ref": ref(s, a), "has_unzuru": bool(re.search(r"انظروا", t)), "text": t})
# rhetorical افلا + cognition verbs
afala = Counter()
afala_refs = defaultdict(list)
for (s, a), t in sorted(ayahs.items()):
    for m in re.finditer(r"افلا (تعقلون|يعقلون|تتفكرون|يتفكرون|ينظرون|تنظرون|يتدبرون|تتذكرون|يذكرون|تذكرون|تبصرون|يبصرون|يسمعون|تسمعون)", t):
        afala[m.group(1)] += 1
        afala_refs[m.group(1)].append(ref(s, a))
alam_tara = [ref(s, a) for (s, a), t in sorted(ayahs.items()) if re.search(r"\bالم تر\b", t)]
awalam_yaraw = [ref(s, a) for (s, a), t in sorted(ayahs.items()) if re.search(r"اولم ير|افلم ير", t)]
evidence["E4_observation_activation"] = {
    "nzr_imperatives": nzr_impv,
    "nzr_imperative_count": len(nzr_impv),
    "siru_fil_ard": siru_unzuru,
    "afala_cognition": {k: {"count": v, "refs": afala_refs[k]} for k, v in afala.items()},
    "alam_tara_refs": alam_tara,
    "awalam_yaraw_refs": awalam_yaraw,
}

# ============================================================================
# E5 — the delegation formula: ان في ذلك لايه/لايات لقوم/لاولي/لكل <faculty>
#      the conclusion is audience-gated: which faculty is named?
# ============================================================================
delegation = []
DELEG = re.compile(r"ان في ذلك (لايه|لايات|لعبره|لذكري|لايت)\s*(?:لقوم|لاولي|لكل|لمن)?\s*(\S+)?")
for (s, a), t in sorted(ayahs.items()):
    m = re.search(r"ان في ذلك (لايه|لايت|لايات|لعبره|لذكري)( لقوم| لاولي| لكل| لمن)?( \S+)?", t)
    if m:
        delegation.append({
            "ref": ref(s, a),
            "marker": m.group(1),
            "gate": (m.group(2) or "").strip(),
            "faculty": (m.group(3) or "").strip(),
        })
gate_counter = Counter((d["gate"], d["faculty"]) for d in delegation if d["gate"])
evidence["E5_delegated_conclusion"] = {
    "events": delegation,
    "total": len(delegation),
    "gated_total": sum(1 for d in delegation if d["gate"]),
    "gate_distribution": [
        {"gate": g, "faculty": f, "count": c} for (g, f), c in gate_counter.most_common()
    ],
}

# ============================================================================
# E6 — masal (example/parable) policy: darb al-mathal events + self-declared
#      universality (صرفنا/ضربنا من كل مثل) + comprehension gating
# ============================================================================
masal_events = []
for (s, a), t in sorted(ayahs.items()):
    if re.search(r"مثل", t) and re.search(r"ضرب|يضرب|نضرب|اضرب|صرفنا", t):
        masal_events.append({"ref": ref(s, a), "text": t})
kull_masal = [e for e in masal_events if re.search(r"من كل مثل", e["text"])]
evidence["E6_masal_policy"] = {
    "darb_masal_events": [e["ref"] for e in masal_events],
    "count": len(masal_events),
    "min_kulli_masal": [e["ref"] for e in kull_masal],
    "comprehension_gate_29_43": ayahs.get((29, 43)),
}

# ============================================================================
# E7 — story (qasas) deployment + self-declared function
# ============================================================================
qasas_rows = cur.execute(
    "SELECT DISTINCT surah_number s, ayah_number a FROM morphology WHERE root_id=1140"
).fetchall()
qasas_refs = [ref(r["s"], r["a"]) for r in qasas_rows]
evidence["E7_story_policy"] = {
    "qss_root_ayahs": qasas_refs,
    "declared_function_11_120": ayahs.get((11, 120)),
    "declared_function_12_111": ayahs.get((12, 111)),
    "declared_function_7_176": ayahs.get((7, 176)),
    "story_as_answer_18_83": ayahs.get((18, 83)),
}

# ============================================================================
# E8 — tasrif (variation) self-declared policy: root Srf + ayat
# ============================================================================
tasrif = []
for (s, a), t in sorted(ayahs.items()):
    if re.search(r"نصرف الاي|صرفنا", t):
        tasrif.append({"ref": ref(s, a), "text": t})
evidence["E8_tasrif_policy"] = tasrif

# ============================================================================
# E9 — gradual-delivery self-declared policy (25:32-33, 17:106, 16:101, 2:106)
# ============================================================================
evidence["E9_gradualism_declared"] = {
    "25:32": ayahs.get((25, 32)),
    "25:33": ayahs.get((25, 33)),
    "17:106": ayahs.get((17, 106)),
    "16:101": ayahs.get((16, 101)),
    "2:106": ayahs.get((2, 106)),
}

# ============================================================================
# E10 — hope/warning pairing and ORDER inside single ayahs
#   (a) bashir/nadhir order where both roots appear in one ayah
#   (b) maghfira-attr vs punishment-attr order in one ayah
# ============================================================================
def order_in_ayah(pat_a, pat_b):
    both, a_first, b_first, refs = 0, 0, 0, []
    for (s, a), t in sorted(ayahs.items()):
        ma, mb = re.search(pat_a, t), re.search(pat_b, t)
        if ma and mb:
            both += 1
            first = "A" if ma.start() < mb.start() else "B"
            if first == "A":
                a_first += 1
            else:
                b_first += 1
            refs.append({"ref": ref(s, a), "first": first})
    return {"both": both, "A_first": a_first, "B_first": b_first, "refs": refs}

def binom_p_geq(k, n):
    """one-sided P(X>=k) for X~Bin(n,0.5)"""
    from math import comb
    return sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n

bashir_nadhir = order_in_ayah(r"بشير|بشيرا|مبشر|بشري|يبشر|نبشر|بشرن", r"نذير|نذيرا|منذر|انذر|ينذر")
bashir_nadhir["p_one_sided"] = binom_p_geq(max(bashir_nadhir["A_first"], bashir_nadhir["B_first"]), bashir_nadhir["both"])
ghafur_iqab = order_in_ayah(r"غفور|غفار|غافر|يغفر|مغفره|غفران", r"شديد العقاب|عقاب|عذاب اليم|العذاب الاليم|شديد العذاب")
evidence["E10_hope_warning_order"] = {
    "bashir_vs_nadhir": {k: bashir_nadhir[k] for k in ("both", "A_first", "B_first", "p_one_sided")},
    "bashir_vs_nadhir_refs": bashir_nadhir["refs"],
    "forgiveness_vs_punishment": {k: ghafur_iqab[k] for k in ("both", "A_first", "B_first")},
    "forgiveness_vs_punishment_refs": ghafur_iqab["refs"],
    "self_described_dual_tone_39_23": ayahs.get((39, 23)),
    "policy_pair_15_49_50": [ayahs.get((15, 49)), ayahs.get((15, 50))],
}

# ============================================================================
# E11 — argue vs remind: burhan-demand events + fa-dhakkir gating
# ============================================================================
burhan = [{"ref": ref(s, a), "text": t} for (s, a), t in sorted(ayahs.items())
          if re.search(r"هاتوا برهنكم", t)]
fadhakkir = [{"ref": ref(s, a), "text": t} for (s, a), t in sorted(ayahs.items())
             if re.search(r"\bفذكر\b", t)]
evidence["E11_argue_vs_remind"] = {
    "hatu_burhanakum": burhan,
    "fa_dhakkir": fadhakkir,
    "reminder_gate_87_9_10": [ayahs.get((87, 9)), ayahs.get((87, 10))],
    "reminder_gate_50_45": ayahs.get((50, 45)),
    "no_coercion_88_21_22": [ayahs.get((88, 21)), ayahs.get((88, 22))],
    "no_coercion_10_99": ayahs.get((10, 99)),
}

# ============================================================================
# E12 — question management policy (5:101-102) & redirect (79:42-44, 29:50-51)
# ============================================================================
evidence["E12_question_management"] = {
    "5:101": ayahs.get((5, 101)),
    "5:102": ayahs.get((5, 102)),
    "79:42-44": [ayahs.get((79, 42)), ayahs.get((79, 43)), ayahs.get((79, 44))],
    "29:50": ayahs.get((29, 50)),
    "29:51": ayahs.get((29, 51)),
}

# ============================================================================
# E13 — knowledge-limit statements: وما اوتيتم من العلم / لا يعلم الغيب
# ============================================================================
limits = [{"ref": ref(s, a), "text": t} for (s, a), t in sorted(ayahs.items())
          if re.search(r"وما اوتيتم من العلم|قل لا يعلم من في السموت والارض الغيب|لا اعلم الغيب|ولو كنت اعلم الغيب", t)]
evidence["E13_knowledge_limits"] = limits

json_path = OUT_DIR / "phase1_evidence.json"
json_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=1), encoding="utf-8")

# ---- console summary --------------------------------------------------------
print(f"E1  question events (yas'alunaka/yastaftunaka): {len(qa_events)}")
qul_ok = sum(1 for e in qa_events if e["qul_in_same_ayah_after"] or e["qul_at_next_ayah_start"])
print(f"    routed through qul: {qul_ok}/{len(qa_events)}")
for e in qa_events:
    print(f"    {e['ref']:>7}  {e['trigger']}  qul_same={e['qul_in_same_ayah_after']} qul_next={e['qul_at_next_ayah_start']}")
print(f"E2  qwl imperatives total tokens: {qul_impv_total}; ayahs with exact 'qul': {qul_exact_ayahs}")
print(f"E3  hour-knowledge-relocation ayahs: {len(sa_events)} -> {[e['ref'] for e in sa_events]}")
print(f"E4  nzr imperatives: {len(nzr_impv)}; siru-fil-ard: {len(siru_unzuru)}; alam-tara: {len(alam_tara)}; awalam/afalam-yaraw: {len(awalam_yaraw)}")
print(f"    afala+cognition: {dict(afala)}")
print(f"E5  delegated-conclusion formula: total={len(delegation)}, gated={sum(1 for d in delegation if d['gate'])}")
for (g, f), c in gate_counter.most_common(12):
    print(f"    {g} {f}: {c}")
print(f"E6  darb-masal events: {len(masal_events)}; min-kulli-masal: {[e['ref'] for e in kull_masal]}")
print(f"E7  qss-root ayahs: {len(qasas_refs)}")
print(f"E8  tasrif ayahs: {len(tasrif)} -> {[e['ref'] for e in tasrif]}")
print(f"E10 bashir/nadhir both-in-ayah: {bashir_nadhir['both']} (bashir first: {bashir_nadhir['A_first']}, nadhir first: {bashir_nadhir['B_first']})")
print(f"    forgiveness/punishment both-in-ayah: {ghafur_iqab['both']} (forgiveness first: {ghafur_iqab['A_first']}, punishment first: {ghafur_iqab['B_first']})")
print(f"E11 hatu-burhanakum: {[e['ref'] for e in burhan]}; fa-dhakkir: {[e['ref'] for e in fadhakkir]}")
print(f"E13 knowledge-limit ayahs: {[e['ref'] for e in limits]}")
print(f"\nwrote {json_path}")
