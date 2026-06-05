# Verification Standard (binding)

**Issued**: 2026-06-05. A theory becomes credible only when outsiders can try
to falsify it. Every claim at T5+ must converge to the package defined here.

## 1. Verification package

$$
\text{Claim} + \text{Assumptions} + \text{Proof} + \text{Code} + \text{Data}
+ \text{Expected Output} + \text{Falsification Condition}.
$$

Concretely: claim card (`claims/<ID>/`), proof note (`theory/sector-X/`),
script(s) (`codes/` or `verification/`), artefacts (`runs/<ID>/result.json`),
and the reproduction block on the card.

## 2. One-command reproduction

Target interface (script to be implemented; contract fixed now):

```bash
python verification/scripts/verify_claim.py --claim B1-RH-ENUM
```

Standard output contract:

```
CLAIM: B1-RH-ENUM
STATUS: PASS
ASSERTS: 101/101
MAX_ERROR: 3.2e-08
FALSIFICATION_GATE: NOT FIRED
ARTEFACT: runs/B1-RH-ENUM/result.json
```

or on failure:

```
CLAIM: B1-RH-ENUM
STATUS: FAIL
FAILED_GATE: HEX_EXACT_WICK_NEGATIVE_MARGIN
COUNTEREXAMPLE: runs/B1-RH-ENUM/hex_case_017.json
```

Exit code 0 iff STATUS PASS. `run_all_claims.py` iterates over every claim with
`reproduction.status == AVAILABLE`.

## 3. Determinism and environment pinning

- Every verification script fixes its random seeds and records them in the
  artefact.
- Expected outputs are **tolerance windows**, never exact float equality;
  the tolerance is declared on the claim card.
- `verification/requirements.txt` pins package versions; the artefact records
  python/package versions, platform, and the git commit hash.
- Self-test asserts inside the script cover **every** numerical claim of the
  associated note, not a representative subset; assert failure = the note is
  wrong and must be fixed before commit.

## 4. Run recording

Every script that produces evidence writes
`runs/<claim-id>/<YYMMDD>-<tag>/result.json` containing: config, constants
check, per-step time series where applicable, summary, seeds, environment, and
per-assert pass/fail with expected/actual values. Large binaries are
git-ignored; the JSON plus the script must suffice to regenerate them. A run
cited as evidence without its JSON artefact is not citable.

## 5. Triple internal verification

Each core result requires at least **two of three**:

1. analytic proof,
2. independent numerical script,
3. alternative formulation / limiting-case check.

The card records which routes exist. One-route results cap at T4.

## 6. Quantitative sanity checks (mandatory with any numerical claim)

At least one explicit check from: dimensional analysis; order-of-magnitude;
limit case; exponential-magnitude sanity; distribution well-definedness;
sign/direction physics; conservation cross-check; numerical reproducibility;
compactness ratio when GR/horizon-scale objects are involved. (Carried over
from the legacy post-mortem record: each of the five 2026-04 rollbacks would
have been caught by one elementary check from this list.)

## 7. Continuous integration

`.github/workflows/verify.yml` runs on every push:

1. `python verification/scripts/lint_claims.py` (ledger validity), and
2. `python verification/scripts/lint_claims.py --render --check` (generated
   `CLAIMS.md` is in sync with `status.json` sources).

When `verify_claim.py` exists, quick-mode claim verification joins CI;
long-running numerical verification runs nightly or on demand, with artefacts
uploaded. The README badge reflecting CI status is part of the public
verification surface.

## 8. External review interface

`REVIEWING.md` is the entry point. Review rounds are archived under
`reviews/<YYYY-MM-DD>-<reviewer-or-topic>/` with: what was reviewed (commit
hash), verdicts, and resulting actions. Confirmed defects produce errata in
`reviews/errata/` linked to claim IDs, plus `negative-results/` rows when a
claim is retired. Reviewer-found defects are credited.
