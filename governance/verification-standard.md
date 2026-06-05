# Verification Standard (binding)

**Issued**: 2026-06-05. A theory becomes credible only when outsiders can try
to falsify it. Every claim at T5+ must converge to the package defined here.

## 1. Verification package

$$
\text{Claim} + \text{Assumptions} + \text{Proof} + \text{Code} + \text{Data}
+ \text{Expected Output} + \text{Falsification Condition}.
$$

Concretely: claim card (`claims/<ID>/`), proof note (`theory/sector-X/`),
script(s) (`codes/` or `verification/`), artefacts (`claims/<ID>/runs/result.json`),
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
ARTEFACT: claims/B1-RH-ENUM/runs/result.json
```

or on failure:

```
CLAIM: B1-RH-ENUM
STATUS: FAIL
FAILED_GATE: HEX_EXACT_WICK_NEGATIVE_MARGIN
COUNTEREXAMPLE: claims/B1-RH-ENUM/runs/hex_case_017.json
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
`claims/<ID>/runs/<YYMMDD>-<descriptive-tag>/result.json` containing: config,
constants check, per-step time series where applicable, summary, seeds,
environment, **the producing scripts' `__version__` values (+ git commit when
available)**, and per-assert pass/fail with expected/actual values. Runs are
immutable: corrections produce a new run folder, never an edit. Large binaries are
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

## 8. Derived catalog — the "no primary database" rule

The repository needs database-grade querying (every artefact with versions,
dates, claim links, lifecycle) but MUST NOT acquire a second source of truth.
Binding rule: any catalog/index/database over the corpus is a **derived
index** generated from the files (+ `claims/*/status.json` + git history) and
is disposable — if wrong, delete and regenerate. Authoritative stores other
than the files and git are forbidden (this is the same single-source-of-truth
principle that generates `CLAIMS.md` and `BY-CLAIM.md`, and it removes the
legacy mirror-drift failure class by construction).

Implementation: `verification/scripts/build_catalog.py` emits `CATALOG.md`
(human view, grouped by artefact kind) and `verification/catalog.json`
(machine twin: path, kind, claim links, theory tag, two-date fields, version,
lifecycle incl. SUPERSEDED detection, size, sha256/12). Regenerate after any
file add/move/version bump; CI runs `--check`. The JSON loads directly into
pandas/SQLite for ad-hoc queries; if the corpus outgrows JSON (>10^4 entries),
the generator may emit SQLite instead — the derived-index rule is unchanged.

## 9. External review interface

`REVIEWING.md` is the entry point. Review rounds are archived under
`reviews/<YYYY-MM-DD>-<reviewer-or-topic>/` with: what was reviewed (commit
hash), verdicts, and resulting actions. Confirmed defects produce errata in
`reviews/errata/` linked to claim IDs, plus `negative-results/` rows when a
claim is retired. Reviewer-found defects are credited.
