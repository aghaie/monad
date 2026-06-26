"""DomainAdapter برای ریشه‌های قرآنی — تنها کدِ مخصوصِ قرآن."""
import hashlib
import random as _random
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
            "m.token_position t, m.form_buckwalter surface, m.pos, m.tag, "
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
            allay = [(s, a) for (s, a) in
                     c.execute("SELECT surah_number, ayah_number FROM ayahs")]
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
