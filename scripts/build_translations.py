#!/usr/bin/env python3
"""
scripts/build_translations.py

Load the external Persian translation corpus into generated/monad.db as a
QUARANTINED reference layer.

╔══════════════════════════════════════════════════════════════════════════╗
║  SELF-SUFFICIENCY QUARANTINE (researcher-agent-charter.md)                ║
║                                                                            ║
║  These tables hold EXTERNAL human translations. They are an OUTPUT /       ║
║  scorecard layer ONLY. They MUST NEVER be read as input to any meaning-    ║
║  derivation pipeline (L1–L9 induction, network, lexicon). They exist so a  ║
║  human can read derived results against a familiar gloss, and so failed    ║
║  derivations can be audited — not to seed derivation.                      ║
║                                                                            ║
║  Every table created here is prefixed `ext_` to make the boundary visible  ║
║  in `.tables` and in any query.                                            ║
╚══════════════════════════════════════════════════════════════════════════╝

Inputs:
    external/translate/translator_meta.csv    13 Persian translators (meta)
    external/translate/translations.csv        13 × 6236 = 81068 verse rows
                                               verse_id == ayahs.ayah_sequential

Outputs (in generated/monad.db):
    ext_translators     one row per translator (id, lang, name, priority, …)
    ext_translations    one row per (translator, ayah); FK → ayahs

Usage:
    python scripts/build_translations.py [--db PATH] [--force]
"""

import argparse
import csv
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXT = REPO_ROOT / "external" / "translate"
DEFAULT_DB = REPO_ROOT / "generated" / "monad.db"

META_CSV = EXT / "translator_meta.csv"
TRANS_CSV = EXT / "translations.csv"

EXPECTED_AYAT = 6236

DDL = """
DROP TABLE IF EXISTS ext_translations;
DROP TABLE IF EXISTS ext_translators;

-- QUARANTINED external reference layer — never a derivation input.
CREATE TABLE ext_translators (
    id          INTEGER PRIMARY KEY,   -- as given in translator_meta.csv
    lang        TEXT    NOT NULL,
    translator  TEXT    NOT NULL UNIQUE,
    priority    INTEGER,
    style       TEXT,                  -- literal | balanced | literary
    notes       TEXT
);

-- QUARANTINED external reference layer — never a derivation input.
CREATE TABLE ext_translations (
    ayah_sequential INTEGER NOT NULL,  -- == external verse_id, 1..6236
    surah_number    INTEGER NOT NULL,
    ayah_number     INTEGER NOT NULL,
    lang            TEXT    NOT NULL,
    translator      TEXT    NOT NULL REFERENCES ext_translators(translator),
    trans_literal   TEXT    NOT NULL,
    PRIMARY KEY (translator, surah_number, ayah_number),
    FOREIGN KEY (surah_number, ayah_number)
        REFERENCES ayahs(surah_number, ayah_number)
);

CREATE INDEX idx_ext_trans_ayah ON ext_translations(surah_number, ayah_number);
CREATE INDEX idx_ext_trans_seq  ON ext_translations(ayah_sequential);
CREATE INDEX idx_ext_trans_who  ON ext_translations(translator);
"""


def load_meta(rows_out):
    with open(META_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows_out.append((
                int(row["id"]),
                row["lang"],
                row["translator"],
                int(row["priority"]) if row["priority"] not in (None, "", "NULL") else None,
                None if row["style"] in (None, "", "NULL") else row["style"],
                None if row["notes"] in (None, "", "NULL") else row["notes"],
            ))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    ap.add_argument("--force", action="store_true",
                    help="rebuild even if ext_translations already populated")
    args = ap.parse_args()

    for p in (META_CSV, TRANS_CSV):
        if not p.exists():
            sys.exit(f"missing input: {p}")
    if not args.db.exists():
        sys.exit(f"database not found: {args.db} (build_database.py first)")

    con = sqlite3.connect(args.db)
    con.execute("PRAGMA foreign_keys = ON;")
    cur = con.cursor()

    # seq -> (surah, ayah) map from the authoritative ayahs table
    seq_map = {
        seq: (s, a)
        for s, a, seq in cur.execute(
            "SELECT surah_number, ayah_number, ayah_sequential FROM ayahs"
        )
    }
    if len(seq_map) != EXPECTED_AYAT:
        sys.exit(f"ayahs has {len(seq_map)} rows, expected {EXPECTED_AYAT}")

    if not args.force:
        exists = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='ext_translations'"
        ).fetchone()
        if exists and cur.execute("SELECT COUNT(*) FROM ext_translations").fetchone()[0]:
            sys.exit("ext_translations already populated; use --force to rebuild")

    cur.executescript(DDL)

    meta = []
    load_meta(meta)
    cur.executemany(
        "INSERT INTO ext_translators VALUES (?,?,?,?,?,?)", meta
    )
    print(f"ext_translators: {len(meta)} rows")

    inserted = 0
    bad_seq = 0
    batch = []
    with open(TRANS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            seq = int(row["verse_id"])
            sa = seq_map.get(seq)
            if sa is None:
                bad_seq += 1
                continue
            batch.append((
                seq, sa[0], sa[1], row["lang"], row["translator"], row["trans_literal"]
            ))
            if len(batch) >= 5000:
                cur.executemany(
                    "INSERT INTO ext_translations VALUES (?,?,?,?,?,?)", batch
                )
                inserted += len(batch)
                batch = []
    if batch:
        cur.executemany("INSERT INTO ext_translations VALUES (?,?,?,?,?,?)", batch)
        inserted += len(batch)

    con.commit()
    print(f"ext_translations: {inserted} rows inserted"
          + (f"  ({bad_seq} skipped — unknown verse_id)" if bad_seq else ""))
    con.close()


if __name__ == "__main__":
    main()
