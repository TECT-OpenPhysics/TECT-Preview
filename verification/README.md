# verification/ — harness

- `scripts/lint_claims.py` — ledger validation + `--render` generates `CLAIMS.md` + `archive/legacy/BY-CLAIM.md`.
- `scripts/build_catalog.py` — derived catalog: `CATALOG.md` + `catalog.json` (`--check` in CI).
- `scripts/verify_claim.py` — one-command claim verification (contract fixed in
  `governance/verification-standard.md` §2; implementation pending).
- `tests/` — pytest suite.
- `requirements.txt` — pinned environment.
