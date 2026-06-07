# Methodology-Discovery Report — Phase Z (A)

**Phase:** Z — Quran Self-Method Discovery Engine (falsification study) ·
**Method version:** `self-methodology-1.0` · **Date:** 2026-06-07.

## 1. Objective

Test — not assume — whether the Quran describes within itself a stable internal method for
reaching knowledge. Phase A establishes the raw material: the Quran's own epistemic
vocabulary and the candidate associative graph among it. **Phases Q and X are treated as
hypotheses, not findings.** Everything is rebuilt from the corpus; no Q/X output is read.

## 2. Method

The epistemic vocabulary is the spec's own list — see/observe, listen, read, reflect
(عقل), ponder (دبر), think (فكر), remember (ذكر), ask (سؤال), judge (حكم), knowledge (علم),
understanding (فقه/فهم), certainty (یقین), conjecture (ظن), guidance (هدایت), misguidance
(گمراهی), denial (تکذیب) — mapped to corpus roots (16 opaque nodes). For each ayah we
record which nodes are present and their within-ayah word order. A node pair is a
**candidate edge** if the two nodes co-occur (within-ayah or adjacent-ayah) at directed
support ≥ 8.

## 3. Results

- Method-vocabulary nodes appear in **2,678 ayahs** (≈ 43% of the 6,214 root-bearing
  ayahs); **16/16 nodes are present** in the corpus.
- **85 candidate edges** (node pairs at support ≥ 8) form a connected associative field
  over the 16 nodes.

(Whether these 85 associations are *real* beyond frequency, and whether they carry
*direction*, is tested in the falsification report — not here.)

## 4. Interpretation

The Quran does contain a rich, connected epistemic vocabulary, and the nodes co-occur
densely (85 candidate edges over 16 nodes). At the descriptive level this reproduces the
starting point of Phases Q and X. But "the vocabulary exists and co-occurs" is a weak
claim; the strong claims — that the associations are non-random and that they form a
*directed method* — are exactly what later phases of Phase Z attack. Phase A asserts only
that the field exists.

## 5. Falsification Attempts

None at this stage by design; Phase A only enumerates. Every association here is provisional
and is passed to the falsification battery (frequency / order / length nulls) and the
stability battery (bootstrap / subsampling), where most of it is expected — given Phase P —
to dissolve.

## 6. Limitations

- The node-to-root mapping is the spec's vocabulary, not a discovered clustering; a
  different vocabulary choice would change the node set (though the falsification logic is
  invariant to that choice).
- Presence is binary per ayah; intensity is not modelled.

## 7. Conclusion

The Quran has a connected epistemic-vocabulary field: 16 nodes, 85 candidate associations,
in 2,678 ayahs. This is the raw graph whose *reality* and *directionality* the rest of
Phase Z tests.

Source: `generated/self_methodology/methodology_graph.json`.
