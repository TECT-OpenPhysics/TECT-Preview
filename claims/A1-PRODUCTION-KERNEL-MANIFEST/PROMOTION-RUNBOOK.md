# A1 manifest promotion evidence runbook

This runbook records how to collect reproducible evidence for
`A1-PRODUCTION-KERNEL-MANIFEST`.  After the 2026-07-16 scoped T5 promotion, it
is also the checklist for refreshing the independent evidence before any future
package re-issue.  The tool itself still does not approve or modify a tier.

## Preconditions

- The checkout is the source tree intended for review.
- The current A1 scope is the canonical N-001 pure-Brazovskii scalar slice.
- Full PDE, BCC structure, and operator-theorem claims are out of scope here.
- Any later tier or scope change still requires the normal claim-card update,
  devil's-advocate objections, changelog entry, generated ledgers, and release
  gate.

## One-command evidence collection

PowerShell:

```powershell
python codes/foundations/a1_promotion_evidence.py `
  --mode independent `
  --run-id 20260716-operator-01 `
  --reviewer "Full Name or Organisation"
```

Bundled Python, if plain `python` is not available:

```powershell
C:\Users\jtkor\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe codes/foundations/a1_promotion_evidence.py `
  --mode independent `
  --run-id 20260716-operator-01 `
  --reviewer "Full Name or Organisation"
```

For a non-certifying local check before independent review, replace
`--mode independent` with `--mode preflight`.

## Expected result

The command exits with code `0` when the technical gate passes and prints the
evidence directory. In independent mode, the terminal verdict should be
`REPRODUCTION-PASS`. In preflight mode, the terminal verdict should be
`TECHNICAL-PASS`.

The current checker version for post-promotion runs is `1.7.0`.

## Persistent result files

Each run creates a never-overwritten directory under:

```text
claims/A1-PRODUCTION-KERNEL-MANIFEST/runs/promotion-evidence/<run-id>/
```

The durable files are:

- `environment.json`: command, runtime, git state, reviewer, mode, and input
  hashes.
- `a1_kernel_checks.json`: canonical checker result for the same run.
- `a1_kernel_checks.stdout.txt`: checker standard output.
- `a1_kernel_checks.stderr.txt`: checker standard error.
- `promotion_evidence.json`: summary verdict and gate status.
- `REVIEW.md`: reviewer checklist for deciding whether the run can support a
  package re-issue.
- `FILE-SHA256.json`: hashes of the saved evidence files.

## Promotion boundary

Passing this evidence package supports only the already pinned scalar-slice T5
scope after human review ratifies the exact scope, tolerances, source hashes,
and proof-line relevance.  It cannot support T6 or T7 by itself because this
package does not prove a conditional theorem or discharge the full
theorem/prohibition list.
