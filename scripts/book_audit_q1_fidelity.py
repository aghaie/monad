#!/usr/bin/env python3
"""
Phase Q1 — Citation fidelity.

For each resolved reference (surah:ayah) from Q0:
  1. EXISTENCE   : does surah:ayah exist in the canonical corpus?
  2. QUOTE-MATCH : is the canonical verse text actually quoted near the citation?
     Measured as recall = (canonical content words found in the ±300-char book
     window) / (canonical content words).  >=0.5 => quotation present & faithful;
     0.2-0.5 => partial/paraphrase; <0.2 => citation only (no verse text quoted).
Outputs generated/book-quran-audit/q1_fidelity.jsonl + prints a summary.
A low quote-match is NOT an error (the book may merely *reference* a verse);
EXISTENCE failures and gross mismatches ARE the integrity signal.
"""
import csv, json, re, unicodedata

REFS = "generated/book-quran-audit/q0_references.jsonl"
QURAN = "corpus/quran/source/qurantexttanzil.csv"
OUT = "generated/book-quran-audit/q1_fidelity.jsonl"

def fold(s):
    s = unicodedata.normalize("NFKC", s)
    for a, b in [("ي","ی"),("ك","ک"),("ة","ه"),("أ","ا"),("إ","ا"),("آ","ا"),
                 ("ؤ","و"),("ئ","ی"),("ٱ","ا"),("ى","ی")]:
        s = s.replace(a, b)
    s = re.sub(r"[ًٌٍَُِّْـٰٓۚۖۗۘۙۛ‌‏‎‪‫‬‌-‏]", "", s)
    s = re.sub(r"[^؀-ۿ\s]", " ", s)
    return s

STOP = set("و یا که از در به با بر را این آن ها های ان من تو او ما شما کس لا ما من فی علی الی عن ان اذ اذا قد لم لن ال هو هی".split())
def toks(s):
    return [t for t in fold(s).split() if len(t) >= 2 and t not in STOP]

# load canonical verses
Q = {}
maxa = {}
with open(QURAN, encoding="utf-8") as f:
    for row in csv.reader(f):
        if len(row) >= 3 and row[0].isdigit():
            s, a = int(row[0]), int(row[1])
            Q[(s, a)] = row[2]
            maxa[s] = max(maxa.get(s, 0), a)

refs = [json.loads(l) for l in open(REFS, encoding="utf-8")]
out = []
for r in refs:
    s, a = r["surah_num"], r["ayah_num"]
    rec = dict(r)
    if a is None:
        rec.update(existence="surah_only", quote_recall=None, verdict="surah_only")
        out.append(rec); continue
    if s not in maxa:
        rec.update(existence="surah_missing", quote_recall=None, verdict="FAIL_existence")
        out.append(rec); continue
    if a > maxa[s]:
        rec.update(existence=f"ayah_out_of_range(max={maxa[s]})", quote_recall=None,
                   verdict="FAIL_existence")
        out.append(rec); continue
    canon = Q[(s, a)]
    ct = toks(canon)
    window = set(toks(r["context"]))
    found = sum(1 for t in set(ct) if t in window)
    recall = round(found / max(1, len(set(ct))), 2)
    if recall >= 0.5: v = "quote_faithful"
    elif recall >= 0.2: v = "quote_partial"
    else: v = "reference_only"
    rec.update(existence="ok", canonical=canon, quote_recall=recall, verdict=v)
    out.append(rec)

with open(OUT, "w", encoding="utf-8") as f:
    for r in out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

# summary
from collections import Counter
c = Counter(r["verdict"] for r in out)
resolved = [r for r in out if r["ayah_num"]]
exist_fail = [r for r in resolved if r["verdict"] == "FAIL_existence"]
print("total references     :", len(out))
print("with surah:ayah      :", len(resolved))
print("verdict breakdown    :", dict(c))
print("EXISTENCE failures   :", len(exist_fail))
for r in exist_fail:
    print(f"   {r['ref_id']} {r['surah_num']}:{r['ayah_num']} ({r['surah_name_raw']}) — {r['existence']}")
faithful = [r for r in resolved if r["verdict"] in ("quote_faithful","quote_partial")]
print(f"verse text quoted    : {len(faithful)}/{len(resolved)} "
      f"({len(faithful)*100//max(1,len(resolved))}%)")
