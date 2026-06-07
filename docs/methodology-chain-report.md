# Methodology-Chain Report — Phase Z (B, C, G)

**Phase:** Z · **Method version:** `self-methodology-1.0` · **Date:** 2026-06-07.

## 1. Objective

Build the directed method graph (process chains A→B→C), its prerequisites/outcomes of
cognition, and its overall architecture — **on the raw data** — so that the falsification
and stability phases have a concrete structure to attack. This is the structure that
Phases Q and X reported as a finding; here it is a hypothesis.

## 2. Method

Direction between two nodes is the net of within-ayah word-order precedence plus cross-ayah
(window-1) adjacency: `dir = forward / (forward + backward)`, oriented by the majority
direction, over candidate edges (support ≥ 8). Net outflow (Σ forward − Σ backward) ranks
nodes from source to sink. Prerequisites of a cognition node = its in-edges; outcomes = its
out-edges.

## 3. Results

**Net-outflow ordering (source → sink):**

| node | net | role |
|---|--:|---|
| observe | +71 | source |
| read | +65 | source |
| listen | +57 | source |
| ask | +26 | source |
| denial | +6 | — |
| ponder | +3 | — |
| reflect | 0 | — |
| think | −1 | — |
| remember | −2 | — |
| judge | −11 | sink |
| conjecture | −13 | sink |
| certainty | −18 | sink |
| understanding | −19 | sink |
| guidance | −29 | sink |
| misguidance | −56 | sink |
| **knowledge** | **−79** | **deepest sink** |

85 directed candidate edges. Perception acts (observe/read/listen/ask) are sources;
knowledge/guidance/misguidance are sinks; knowledge is the deepest attractor.

## 4. Interpretation

**On the raw data, the graph reproduces Phases Q and X** — perception acts flow toward
knowledge; knowledge is the terminal attractor. This is reassuring as a replication (the
rebuild, using no Q/X output, recovers their qualitative pipeline). **But replication of
the raw pattern is not the test.** The same net-outflow ordering would arise from any
process where frequent "doing" words appear early in ayahs and frequent "knowing" words
appear later — including pure frequency-and-order regularities with no methodological
content. Whether this architecture is *real beyond frequency* and *directional beyond text
order* is decided in `self-methodology-falsification-report.md`, where most of it does not
survive.

## 5. Falsification Attempts

The architecture here is the object of attack, not yet attacked. Note in advance: net
outflow is a sum over edges, most of which (see falsification) fail the frequency and order
nulls, so the ordering itself inherits their fragility.

## 6. Limitations

- Net outflow aggregates edges of very different reliability; a clean-looking ordering can
  rest on edges that individually fail the nulls.
- Window-1 adjacency and within-ayah min-position are the only order signals; richer
  syntax is not modelled.

## 7. Conclusion

The raw directed method graph (85 edges) reproduces the Q/X pipeline shape — perception →
… → knowledge — but this is a descriptive starting point. Its reality and directionality
are adjudicated by the null battery, not by this ordering.

Source: `generated/self_methodology/methodology_chains.json`,
`methodology_prerequisites.json`.
