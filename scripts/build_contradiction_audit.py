#!/usr/bin/env python3
"""L10 — Adversarial internal-contradiction audit → database table.

Loads the canonical audit (generated/layers/L10_contradiction/contradiction_audit.json)
and writes it into a `contradiction_audit` table in generated/monad.db.

Method (adversarial, text-internal):
  External critics pick the targets — the 30 most famous alleged internal
  contradictions of the Quran. A claim counts as RESOLVED only if the TEXT ITSELF
  supplies a concrete distinguishing word/phrase (the "hinge") establishing a
  different referent, condition, time, or scope. Where resolution would require an
  external assumption (tradition/tafsir/science), the verdict is UNRESOLVED_FROM_TEXT.
  A genuine, unresolvable clash is SURVIVES. Default to UNRESOLVED. Honesty over
  apologetics — per the Charter (the criterion governs; abstention over error).

NB: monad.db is the substrate, rebuilt by build_database.py. This table is an
analysis layer; re-run this script after any substrate rebuild to restore it.

Reproducible: reads only the committed JSON; output is deterministic.
"""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "generated" / "monad.db"
AUDIT = ROOT / "generated" / "layers" / "L10_contradiction" / "contradiction_audit.json"

DDL = """
CREATE TABLE IF NOT EXISTS contradiction_audit (
    claim_id        INTEGER PRIMARY KEY,
    category        TEXT NOT NULL,
    title           TEXT NOT NULL,
    claim_en        TEXT NOT NULL,
    refs            TEXT NOT NULL,   -- JSON array of "s:a" verse refs
    verdict         TEXT NOT NULL,   -- RESOLVED | UNRESOLVED_FROM_TEXT | SURVIVES
    confidence      TEXT NOT NULL,   -- صریح | قوی | محتمل | نامشخص
    hinge_arabic    TEXT,            -- the in-text word/phrase doing the resolving work
    analysis_fa     TEXT NOT NULL,
    residual_doubt_fa TEXT,
    verses_json     TEXT NOT NULL    -- JSON: [{ref,text}] actual Arabic pulled from substrate
);
"""


def main():
    data = json.loads(AUDIT.read_text(encoding="utf-8"))
    cases = data["cases"]

    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS contradiction_audit")
    cur.executescript(DDL)

    for c in cases:
        cur.execute(
            """INSERT INTO contradiction_audit
               (claim_id, category, title, claim_en, refs, verdict, confidence,
                hinge_arabic, analysis_fa, residual_doubt_fa, verses_json)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                c["id"],
                c.get("category", ""),
                c["title"],
                c.get("claim_en", ""),
                json.dumps(c.get("refs", []), ensure_ascii=False),
                c["verdict"],
                c.get("confidence", ""),
                c.get("hinge_arabic", ""),
                c.get("analysis_fa", ""),
                c.get("residual_doubt_fa", ""),
                json.dumps(c.get("verses", []), ensure_ascii=False),
            ),
        )
    con.commit()

    # summary
    n = cur.execute("SELECT COUNT(*) FROM contradiction_audit").fetchone()[0]
    print(f"inserted {n} cases into contradiction_audit")
    for verdict, cnt in cur.execute(
        "SELECT verdict, COUNT(*) FROM contradiction_audit GROUP BY verdict ORDER BY 2 DESC"
    ):
        print(f"  {verdict:<22} {cnt}")
    survives = cur.execute(
        "SELECT COUNT(*) FROM contradiction_audit WHERE verdict='SURVIVES'"
    ).fetchone()[0]
    print(f"genuine surviving contradictions: {survives}")
    con.close()


if __name__ == "__main__":
    main()
