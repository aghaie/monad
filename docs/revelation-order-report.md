# Revelation-Order Report — Phase 19X (F)

**Phase:** 19X · **Method version:** `numerics-discovery-1.0` · **Date:** 2026-06-07.

## 1. Objective

Test whether any order-dependent numerical finding depends on the specific sequence ordering
of the corpus — i.e. whether results are an artifact of mushaf order.

## 2. Method

The only order-dependent feature is **root first-occurrence position** (mushaf order). Its
best divisibility p (over divisors 2–500) is recomputed under (a) mushaf order and (b) a
random permutation of the ordering, and the two are compared.

**Documented limitation:** the canonical **revelation (nuzul) order is NOT present in the
corpus**; introducing it would require external data, which is forbidden. Order-dependence is
therefore tested by mushaf-vs-random permutation, the only corpus-internal control (the same
stance as Phase 13).

## 3. Results

| ordering | best divisor | best p |
|---|--:|--:|
| mushaf | 444 | 0.00046 |
| random permutation | 444 | 0.00046 |

**Order-dependent: No** (identical results).

## 4. Interpretation

The first-occurrence finding is **identical** under mushaf and random ordering, because the
divisibility statistic is a function of the **multiset** of first-occurrence positions, which
a permutation leaves unchanged. So the apparent "best divisor 444" finding is **not**
order-dependent and not special to mushaf order — it is, like the sequence findings, a
property of a value multiset and subject to the same frequency-null caveat (and it does not
survive multiple-testing correction; p = 0.00046 ≫ Bonferroni threshold 0.0001).

## 5. Falsification Attempts

The order-dependence hypothesis is falsified: shuffling the order changes nothing. Any
order-sensitivity a numerical claim might assert is absent here.

## 6. Limitations

- True nuzul order is unavailable in the corpus; the test is mushaf-vs-random, which is
  sufficient to show order-independence but cannot compare against a historical chronology.
- Only one order-dependent feature was constructed; others (e.g. inter-occurrence gaps) would
  inherit the same multiset-invariance.

## 7. Conclusion

**No numerical finding is order-dependent.** First-occurrence divisibility is invariant to
ordering (mushaf = random), so results do not depend on the sequence of the text.

Source: `generated/numerics/revelation_order_results.json`.
