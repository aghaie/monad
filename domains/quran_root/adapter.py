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
