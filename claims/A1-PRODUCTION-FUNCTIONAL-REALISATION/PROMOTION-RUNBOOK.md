# A1 production-functional promotion evidence runbook

This runbook records the independent reproduction procedure for
`A1-PRODUCTION-FUNCTIONAL-REALISATION`.  The result is T5 only within the
discrete spectral-torus scope recorded in the current T5 enactment note.

## Independent reproduction

```powershell
C:\Users\jtkor\AppData\Local\Programs\Python\Python312\python.exe codes/foundations/a1_functional_promotion_evidence.py `
  --run-id <stable-id> `
  --reviewer "Full Name or Organisation" `
  --mode independent `
  --grids 4 6 8
```

The expected terminal verdict is `REPRODUCTION-PASS`.  The new run directory
contains the command, environment, source hashes, full verifier JSON, output
logs, review checklist, and per-file SHA-256 record.

## Review boundary

The reviewer must confirm the command, frozen hashes, all required fields and
grids, numerical thresholds, and the no-overclaim boundary.  The result does
not assert historical-solver repair, continuum convergence, PDE behavior,
minimizer selection, BCC structure, stability, T6, or T7.

## Re-issue rule

Any changed backend, verifier, manifest, test matrix, or scope requires a new
independent run, a new note version, and a new tier decision.  The existing
T5 bundle is historical evidence for its frozen source commit only.
