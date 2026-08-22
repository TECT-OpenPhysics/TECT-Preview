# verification/ — harness

- `scripts/lint_claims.py` — ledger validation + `--render` generates `CLAIMS.md` + `archive/legacy/BY-CLAIM.md`.
- `scripts/build_catalog.py` — derived catalog: `CATALOG.md` + `catalog.json` (`--check` in CI).
- `scripts/build_proof_evidence_map.py` — deterministic global proof-route projection: `theory/proof-evidence-map.md` plus a compact `proof-evidence-map.json` index and hash-pinned shards under `proof-evidence-map/`, with registry coverage, graph, and staleness checks.
- `scripts/proof_evidence_map_io.py` — verifies the index/shard hashes and losslessly reconstructs the complete logical map for consumers that need it.
- `scripts/release_check.py` — pre-push publication gate (P0 fence, English-only, no-overclaim, P2 citation rule, hygiene); mandatory before every push.
- `scripts/verify_claim.py` — one-command claim verification (contract fixed in
  `governance/verification-standard.md` §2; implementation pending).
- `tests/` — pytest suite.
- `requirements.txt` — pinned environment.
