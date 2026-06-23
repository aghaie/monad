"""Read-only access to generated/monad.db."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[3] / "generated" / "monad.db"


def connect():
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def get_ayah(con, s, a):
    row = con.execute(
        "SELECT surah_number, ayah_number, text_uthmani, text_normalized "
        "FROM ayahs WHERE surah_number=? AND ayah_number=?", (s, a)).fetchone()
    if row is None:
        return None
    return {"ref": f"{s}:{a}", "surah": s, "ayah": a,
            "text_uthmani": row["text_uthmani"], "text_normalized": row["text_normalized"]}


def get_ayah_tokens(con, s, a):
    rows = con.execute(
        "SELECT w.word_position pos, w.form_arabic form, w.root_id, "
        "       r.root_arabic root_ar, r.root_buckwalter root_bw "
        "FROM words w LEFT JOIN roots r ON w.root_id = r.root_id "
        "WHERE w.surah_number=? AND w.ayah_number=? ORDER BY w.word_position", (s, a)).fetchall()
    return [{"position": x["pos"], "form": x["form"], "root_id": x["root_id"],
             "root_ar": x["root_ar"], "root_bw": x["root_bw"]} for x in rows]
