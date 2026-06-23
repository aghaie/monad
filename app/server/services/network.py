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
