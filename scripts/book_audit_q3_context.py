#!/usr/bin/env python3
"""
Phase Q3 — Contextual fidelity (anti-proof-texting test).

Idea: a faithful, in-context use of scripture groups verses the way the text's OWN
structure groups them; arbitrary proof-texting yokes together verses that are unrelated
in the source. We test this with NO human tafsir, using only:
  - ground-truth roots per verse (Quranic Arabic Corpus morphology), and
  - this repo's validated rare-root relational network (L6 ayah_network).

Test 1 (root coherence): for every pair of DISTINCT verses the book co-cites inside the
same argument (citations within WINDOW chars), score the pair by shared rare-root weight
(sum of idf of shared roots). Compare the mean to two null baselines:
  (a) random pairs drawn from the same set of book-cited verses,
  (b) random pairs drawn from the whole Quran.
If book co-citations score above (a) and (b), the book groups verses that are genuinely
related in the Quran's own lexical fabric -> contextual reading, not arbitrary proof-texting.

Test 2 (network adjacency): fraction of co-cited pairs where one verse is in the other's
L6 rare-root neighbour list, vs the same fraction for random cited-verse pairs.
"""
import json, re, math, random, statistics
from collections import defaultdict, Counter

random.seed(20260620)
MORPH = "corpus/quran/morphology/quranic-corpus-morphology-0.4.txt"
REFS  = "generated/book-quran-audit/q0_references.jsonl"
NET   = "generated/layers/L6_network/ayah_network.json"
OUT   = "generated/book-quran-audit/q3_context.json"
WINDOW = 2500   # chars: ~ one argument / page span

# --- verse -> roots ---
verse_roots = defaultdict(set)
loc_re = re.compile(r"\((\d+):(\d+):\d+:\d+\)")
root_re = re.compile(r"ROOT:([^|]+)")
with open(MORPH, encoding="utf-8") as f:
    for line in f:
        if line.startswith("#") or line.startswith("LOCATION"): continue
        m = loc_re.match(line)
        if not m: continue
        rm = root_re.search(line)
        if rm:
            verse_roots[(int(m.group(1)), int(m.group(2)))].add(rm.group(1))

# --- root idf (rarity) over all verses ---
df = Counter()
for rs in verse_roots.values():
    for r in rs: df[r]+=1
N = len(verse_roots)
idf = {r: math.log(N/df[r]) for r in df}

def pair_weight(a, b):
    """shared rare-root weight between two verses (surah,ayah tuples)."""
    shared = verse_roots.get(a,set()) & verse_roots.get(b,set())
    return sum(idf[r] for r in shared)

# --- book co-cited verse pairs (within WINDOW chars, distinct verses) ---
refs = [json.loads(l) for l in open(REFS, encoding="utf-8")]
cited = [(r["surah_num"], r["ayah_num"], r["char_pos"]) for r in refs if r["ayah_num"]]
cited.sort(key=lambda x: x[2])
cited_verses = sorted({(s,a) for s,a,_ in cited})

def co_cited(window):
    s=set()
    for i in range(len(cited)):
        for j in range(i+1, len(cited)):
            if cited[j][2]-cited[i][2] > window: break
            vi, vj = (cited[i][0],cited[i][1]), (cited[j][0],cited[j][1])
            if vi!=vj: s.add(tuple(sorted([vi,vj])))
    return list(s)
co_pairs = co_cited(WINDOW)

# --- Test 1: root coherence vs baselines ---
def mean_w(pairs):
    return statistics.mean(pair_weight(a,b) for a,b in pairs) if pairs else 0.0

obs = mean_w(co_pairs)

def sample_baseline(pool, n, trials=2000):
    means=[]
    pool=list(pool)
    for _ in range(trials):
        ps=[]
        for _ in range(n):
            a,b=random.sample(pool,2)
            ps.append((a,b))
        means.append(mean_w(ps))
    return means

baseA = sample_baseline(cited_verses, len(co_pairs))           # random pairs of cited verses
all_verses = list(verse_roots.keys())
baseB = sample_baseline(all_verses, len(co_pairs))             # random pairs from whole Quran

def pval(obs, dist):  # one-sided: P(baseline >= obs)
    return (sum(1 for x in dist if x>=obs)+1)/(len(dist)+1)

# --- Test 2: L6 network adjacency ---
net = json.load(open(NET))
neigh = {c["ayah"]: set(c["neighbours"]) for c in net["connections"]}
def adj(a,b):
    ka,kb=f"{a[0]}:{a[1]}",f"{b[0]}:{b[1]}"
    return (kb in neigh.get(ka,())) or (ka in neigh.get(kb,()))
obs_adj = (sum(1 for a,b in co_pairs if adj(a,b))/len(co_pairs)) if co_pairs else 0
# baseline adjacency among random cited-verse pairs
rnd_adj=[]
for _ in range(2000):
    a,b=random.sample(cited_verses,2)
    rnd_adj.append(1 if adj(a,b) else 0)
base_adj = statistics.mean(rnd_adj)

# --- Test 3: whole cited-set coherence vs random same-size sets ---
def set_mean_weight(vs):
    vs=list(vs); tot=[];
    for i in range(len(vs)):
        for j in range(i+1,len(vs)):
            tot.append(pair_weight(vs[i],vs[j]))
    return statistics.mean(tot) if tot else 0.0
obs_set = set_mean_weight(cited_verses)
rnd_sets=[]
for _ in range(3000):
    samp=random.sample(all_verses, len(cited_verses))
    rnd_sets.append(set_mean_weight(samp))
set_p = (sum(1 for x in rnd_sets if x>=obs_set)+1)/(len(rnd_sets)+1)

# --- Test 1 across multiple windows ---
win_sweep={}
for w in (2500, 6000, 12000):
    cp=co_cited(w)
    if cp:
        win_sweep[w]={"pairs":len(cp),
                      "obs":round(mean_w(cp),3),
                      "ratio_vs_quran_random":round(mean_w(cp)/max(1e-9,statistics.mean(baseB)),2)}

res = {
  "window_chars": WINDOW,
  "cited_verses": len(cited_verses),
  "co_cited_pairs": len(co_pairs),
  "test3_set_coherence": {
     "observed_mean_pairwise_weight": round(obs_set,4),
     "random_sets_mean": round(statistics.mean(rnd_sets),4),
     "ratio": round(obs_set/max(1e-9,statistics.mean(rnd_sets)),2),
     "p_value": round(set_p,4),
     "interpretation": "are the book's 34 chosen verses more lexically coherent than a random 34?",
  },
  "test1_window_sweep": win_sweep,
  "test1_root_coherence": {
     "observed_mean_shared_rare_root_weight": round(obs,4),
     "baselineA_cited_random_mean": round(statistics.mean(baseA),4),
     "baselineB_quran_random_mean": round(statistics.mean(baseB),4),
     "ratio_vs_A": round(obs/max(1e-9,statistics.mean(baseA)),2),
     "ratio_vs_B": round(obs/max(1e-9,statistics.mean(baseB)),2),
     "p_vs_A": round(pval(obs,baseA),4),
     "p_vs_B": round(pval(obs,baseB),4),
  },
  "test2_network_adjacency": {
     "observed_adjacent_fraction": round(obs_adj,4),
     "baseline_random_cited_fraction": round(base_adj,4),
  },
}
json.dump(res, open(OUT,"w"), ensure_ascii=False, indent=2)
print(json.dumps(res, ensure_ascii=False, indent=2))
