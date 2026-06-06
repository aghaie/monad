#!/usr/bin/env python3
"""
scripts/validate_database.py

Monad Database Validator.
Runs structural, referential, and content integrity checks on generated/monad.db.

Usage:
    python scripts/validate_database.py [--db PATH]

Exit code:
    0  all checks passed
    1  one or more checks failed
"""

import argparse
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "generated" / "monad.db"

EXPECTED = {
    'surahs':  114,
    'ayahs':   6236,
    'tokens':  128219,
    'pages':   604,
}

PASS = '\033[92mPASS\033[0m'
FAIL = '\033[91mFAIL\033[0m'
INFO = '\033[94mINFO\033[0m'


def check(label: str, passed: bool, detail: str = '') -> bool:
    status = PASS if passed else FAIL
    line   = f"  [{status}] {label}"
    if detail:
        line += f"  ({detail})"
    print(line)
    return passed


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--db', default=str(DEFAULT_DB),
                    help=f"Database path (default: {DEFAULT_DB})")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        sys.exit(1)

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")

    failures = 0

    # ── Table existence ───────────────────────────────────────────────────────
    print("\n── Table existence ──────────────────────────────────────────────────")
    required_tables = ['surahs', 'ayahs', 'roots', 'lemmas', 'words', 'morphology', 'pages']
    existing = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    for t in required_tables:
        ok = t in existing
        if not ok: failures += 1
        check(f"Table '{t}' exists", ok)

    # ── Row counts ────────────────────────────────────────────────────────────
    print("\n── Row counts ───────────────────────────────────────────────────────")

    n = con.execute("SELECT COUNT(*) FROM surahs").fetchone()[0]
    if not check("Surah count = 114", n == EXPECTED['surahs'], f"got {n}"): failures += 1

    n = con.execute("SELECT COUNT(*) FROM ayahs").fetchone()[0]
    if not check("Ayah count = 6236", n == EXPECTED['ayahs'], f"got {n}"): failures += 1

    n = con.execute("SELECT COUNT(*) FROM morphology").fetchone()[0]
    if not check("Morphology token count = 128219", n == EXPECTED['tokens'], f"got {n}"): failures += 1

    n = con.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
    if not check("Page count = 604", n == EXPECTED['pages'], f"got {n}"): failures += 1

    n_roots  = con.execute("SELECT COUNT(*) FROM roots").fetchone()[0]
    n_lemmas = con.execute("SELECT COUNT(*) FROM lemmas").fetchone()[0]
    n_words  = con.execute("SELECT COUNT(*) FROM words").fetchone()[0]
    print(f"  [{INFO}] Roots:  {n_roots}")
    print(f"  [{INFO}] Lemmas: {n_lemmas}")
    print(f"  [{INFO}] Words:  {n_words}")

    # ── Content integrity ─────────────────────────────────────────────────────
    print("\n── Content integrity ────────────────────────────────────────────────")

    # Every surah has its correct ayah count
    bad = con.execute("""
        SELECT COUNT(*) FROM surahs s
        WHERE s.ayah_count != (SELECT COUNT(*) FROM ayahs a WHERE a.surah_number = s.surah_number)
    """).fetchone()[0]
    if not check("Surah.ayah_count matches actual ayah rows", bad == 0, f"{bad} mismatches"): failures += 1

    # All ayahs have non-empty hafs text
    bad = con.execute("SELECT COUNT(*) FROM ayahs WHERE text_hafs IS NULL OR text_hafs = ''").fetchone()[0]
    if not check("All ayahs have text_hafs", bad == 0, f"{bad} missing"): failures += 1

    # All surahs have Arabic name
    bad = con.execute("SELECT COUNT(*) FROM surahs WHERE name_arabic IS NULL OR name_arabic = ''").fetchone()[0]
    if not check("All surahs have name_arabic", bad == 0, f"{bad} missing"): failures += 1

    # All surahs have revelation_type
    bad = con.execute("SELECT COUNT(*) FROM surahs WHERE revelation_type IS NULL").fetchone()[0]
    if not check("All surahs have revelation_type", bad == 0, f"{bad} NULL"): failures += 1

    # Page ayah sum
    total = con.execute("SELECT SUM(ayah_count_on_page) FROM pages").fetchone()[0]
    if not check("Page ayah sum = 6236", total == EXPECTED['ayahs'], f"sum = {total}"): failures += 1

    # Ayah sequential numbers cover 1..6236
    seq_min = con.execute("SELECT MIN(ayah_sequential) FROM ayahs").fetchone()[0]
    seq_max = con.execute("SELECT MAX(ayah_sequential) FROM ayahs").fetchone()[0]
    seq_cnt = con.execute("SELECT COUNT(DISTINCT ayah_sequential) FROM ayahs WHERE ayah_sequential IS NOT NULL").fetchone()[0]
    if not check("Ayah sequential covers 1..6236", seq_min == 1 and seq_max == 6236 and seq_cnt == 6236,
                 f"min={seq_min} max={seq_max} distinct={seq_cnt}"): failures += 1

    # ── Referential integrity ─────────────────────────────────────────────────
    print("\n── Referential integrity ────────────────────────────────────────────")

    # Orphan words (no parent ayah)
    n = con.execute("""
        SELECT COUNT(*) FROM words w
        WHERE NOT EXISTS (
            SELECT 1 FROM ayahs a
            WHERE a.surah_number = w.surah_number AND a.ayah_number = w.ayah_number
        )
    """).fetchone()[0]
    if not check("No orphan words", n == 0, f"{n} orphans"): failures += 1

    # Orphan morphology tokens
    n = con.execute("""
        SELECT COUNT(*) FROM morphology m
        WHERE NOT EXISTS (
            SELECT 1 FROM ayahs a
            WHERE a.surah_number = m.surah_number AND a.ayah_number = m.ayah_number
        )
    """).fetchone()[0]
    if not check("No orphan morphology tokens", n == 0, f"{n} orphans"): failures += 1

    # Broken root FK in morphology
    n = con.execute("""
        SELECT COUNT(*) FROM morphology
        WHERE root_id IS NOT NULL AND root_id NOT IN (SELECT root_id FROM roots)
    """).fetchone()[0]
    if not check("Morphology root_id FK valid", n == 0, f"{n} broken"): failures += 1

    # Broken lemma FK in morphology
    n = con.execute("""
        SELECT COUNT(*) FROM morphology
        WHERE lemma_id IS NOT NULL AND lemma_id NOT IN (SELECT lemma_id FROM lemmas)
    """).fetchone()[0]
    if not check("Morphology lemma_id FK valid", n == 0, f"{n} broken"): failures += 1

    # Broken root FK in words
    n = con.execute("""
        SELECT COUNT(*) FROM words
        WHERE root_id IS NOT NULL AND root_id NOT IN (SELECT root_id FROM roots)
    """).fetchone()[0]
    if not check("Words root_id FK valid", n == 0, f"{n} broken"): failures += 1

    # Broken lemma FK in words
    n = con.execute("""
        SELECT COUNT(*) FROM words
        WHERE lemma_id IS NOT NULL AND lemma_id NOT IN (SELECT lemma_id FROM lemmas)
    """).fetchone()[0]
    if not check("Words lemma_id FK valid", n == 0, f"{n} broken"): failures += 1

    # Lemma root FK valid
    n = con.execute("""
        SELECT COUNT(*) FROM lemmas
        WHERE root_id IS NOT NULL AND root_id NOT IN (SELECT root_id FROM roots)
    """).fetchone()[0]
    if not check("Lemma root_id FK valid", n == 0, f"{n} broken"): failures += 1

    # ── Uniqueness ────────────────────────────────────────────────────────────
    print("\n── Uniqueness ───────────────────────────────────────────────────────")

    dup = con.execute("SELECT COUNT(*) FROM roots GROUP BY root_buckwalter HAVING COUNT(*) > 1").fetchone()
    if not check("Root buckwalter values unique", dup is None): failures += 1

    dup = con.execute("SELECT COUNT(*) FROM lemmas GROUP BY lemma_buckwalter HAVING COUNT(*) > 1").fetchone()
    if not check("Lemma buckwalter values unique", dup is None): failures += 1

    dup = con.execute("""
        SELECT COUNT(*) FROM words
        GROUP BY surah_number, ayah_number, word_position HAVING COUNT(*) > 1
    """).fetchone()
    if not check("Word positions unique per ayah", dup is None): failures += 1

    # ── Root consistency ──────────────────────────────────────────────────────
    print("\n── Root / lemma statistics ──────────────────────────────────────────")

    top_roots = con.execute("""
        SELECT root_arabic, root_buckwalter, token_count
        FROM roots ORDER BY token_count DESC LIMIT 5
    """).fetchall()
    print(f"  [{INFO}] Top 5 roots by token count:")
    for r in top_roots:
        print(f"           {r['root_arabic']:12s} ({r['root_buckwalter']:8s})  {r['token_count']} tokens")

    roots_without_tokens = con.execute(
        "SELECT COUNT(*) FROM roots WHERE token_count = 0"
    ).fetchone()[0]
    check("Roots with zero token_count", roots_without_tokens == 0,
          f"{roots_without_tokens} roots have no tokens")

    lemmas_without_root = con.execute(
        "SELECT COUNT(*) FROM lemmas WHERE root_id IS NULL"
    ).fetchone()[0]
    print(f"  [{INFO}] Lemmas without root:  {lemmas_without_root} "
          f"(particles, proper nouns expected to lack ROOT)")

    words_without_lemma = con.execute(
        "SELECT COUNT(*) FROM words WHERE lemma_id IS NULL"
    ).fetchone()[0]
    print(f"  [{INFO}] Words without lemma:  {words_without_lemma}")

    words_without_root = con.execute(
        "SELECT COUNT(*) FROM words WHERE root_id IS NULL"
    ).fetchone()[0]
    print(f"  [{INFO}] Words without root:   {words_without_root}")

    # ── Traceability spot check ───────────────────────────────────────────────
    print("\n── Traceability spot check ──────────────────────────────────────────")

    # Can we trace word (1,1,1) back to its surah and ayah?
    row = con.execute("""
        SELECT w.surah_number, w.ayah_number, w.word_position,
               w.form_arabic, r.root_arabic, l.lemma_arabic,
               a.text_hafs, s.name_arabic
        FROM words w
        LEFT JOIN roots r ON r.root_id = w.root_id
        LEFT JOIN lemmas l ON l.lemma_id = w.lemma_id
        JOIN ayahs a ON a.surah_number = w.surah_number AND a.ayah_number = w.ayah_number
        JOIN surahs s ON s.surah_number = w.surah_number
        WHERE w.surah_number = 1 AND w.ayah_number = 1 AND w.word_position = 2
    """).fetchone()
    if row:
        check("Word 1:1:2 traceable to surah+ayah", True,
              f"'{row['form_arabic']}' root='{row['root_arabic']}' "
              f"surah='{row['name_arabic']}'")
    else:
        check("Word 1:1:2 traceable to surah+ayah", False, "record not found")
        failures += 1

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n── Summary ──────────────────────────────────────────────────────────")
    total_checks = len([l for l in failures.__class__.__mro__])  # placeholder
    if failures == 0:
        print(f"  All checks passed.\n")
    else:
        print(f"  {failures} check(s) FAILED.\n")

    con.close()
    return 0 if failures == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
