# Structure-Null Report — Phase 19X (E)

**Phase:** 19X · **Method version:** `numerics-discovery-1.0` · **Date:** 2026-06-07.

## 1. Objective

Test whether any numerical finding depends on the actual textual *arrangement* of the Quran,
by destroying that arrangement (shuffling ayahs, surahs, roots, words) while preserving the
underlying distributions, and checking whether the finding persists.

## 2. Method

**Key invariance (stated and used):** shuffling which ayah belongs to which surah, or which
root token sits in which ayah, leaves **every total** (n_ayahs, n_words, …) and **every value
multiset** (and hence every divisibility/residue statistic) **identical.** So a literal
structural shuffle is the *identity* for these statistics. The only non-trivial structural
degree of freedom is the **surah-size partition**: we therefore test whether the actual
partition of 6,236 ayahs into 114 surahs is unusually divisible versus **random partitions**
of the same total into the same number of parts (200 realizations).

## 3. Results

- **Invariance:** every divisibility/residue statistic is unchanged by ayah/surah/root/word
  shuffling (by construction — they are functions of totals and multisets only).
- **Random-partition null:** the actual surah-size partition's best divisibility excess is
  matched or exceeded by **36.0%** of 200 random partitions of 6,236 ayahs into 114 surahs.

## 4. Interpretation

The invariance is itself the central finding: **numerical divisibility is not a property of
the Quran's textual arrangement.** It cannot be created or destroyed by rearranging the text,
because it depends only on counts and value multisets. The one place arrangement could matter
— the surah-size partition — shows the real partition is **ordinary** (matched by 36% of
random partitions; far above the 5% bar). There is no arrangement-dependent numerical
structure.

## 5. Falsification Attempts

This report attacks every finding by removing textual structure. Divisibility findings are
invariant (so they were never about structure), and the one structural test (partition)
returns non-significance. No finding survives as a property of arrangement.

## 6. Limitations

- Random partitions are sampled via stars-and-bars (uniform over compositions into positive
  parts); a different partition prior (e.g. matching the real size distribution) would make
  the real partition even *less* unusual, not more.
- The invariance argument is exact for divisibility/residue but does not cover hypothetical
  order-sensitive statistics, which are addressed in `revelation-order-report.md`.

## 7. Conclusion

**No finding depends on textual structure.** Divisibility is invariant to rearrangement, and
the actual surah-size partition is statistically ordinary (matched by 36% of random
partitions). Numerical divisibility is a property of counts, not of design.

Source: `generated/numerics/structure_null_results.json`.
