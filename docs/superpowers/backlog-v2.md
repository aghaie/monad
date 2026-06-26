# Backlog — نسخهٔ بعد (خارج از scope فاز اول، طبق Implementation Rule 0)

- **Golden artifact scaling:** stage-1 golden is ~618KB for one root. Per-unit golden at scale (1,642 roots) is unviable (~1GB). Switch to hash-based or single canonical-fixture-root golden policy before scaling beyond the v1 benchmark root.
- **two_half_stability — real replication test:** replace presence check with a proper split-half effect-size / replication test (e.g., Fisher's exact or permutation null on co-occurrence counts in each half), so null_p is a real significance value rather than None.
- **engine/store.py add_dag_edges — dedup edges:** the provenance graph bloats on re-runs because duplicate edges are inserted; add deduplication logic.
- **engine/store.py put_knowledge — enforce P3:** on multi-unit runs, apply supersede/refine/contradict logic (P3) instead of silent overwrite when a knowledge entry already exists.
- **engine/benchmark/score.py — honor n_repro:** either average Jaccard over N re-runs as documented or drop the n_repro param so the interface matches the implementation.
- **double RFC generation — skip in run():** skip the RFC write in run() when run_and_score will regenerate it with benchmark data; currently the RFC is written twice per pipeline execution.
- **rfc/generator.py generate() — filter by unit:** the generator currently lists ALL store knowledge; it should filter to only the knowledge entries belonging to the current unit.
- **determinism hardening:** add explicit secondary sort keys at adapter.py max(co.items()) and cluster most_common() tie points; currently tie-breaking relies on SQLite/dict iteration order which is not guaranteed.
