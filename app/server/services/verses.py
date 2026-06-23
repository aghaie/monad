"""Verse payloads — text + tokens with roots. Evidence-only; no external glosses."""
from app.server.data import db


def verse_payload(s, a):
    con = db.connect()
    try:
        ayah = db.get_ayah(con, s, a)
        if ayah is None:
            return None
        tokens = db.get_ayah_tokens(con, s, a)
    finally:
        con.close()
    return {"ref": ayah["ref"], "surah": s, "ayah": a,
            "text": {"uthmani": ayah["text_uthmani"], "normalized": ayah["text_normalized"]},
            "tokens": tokens}
