# Q3LOCK A1--A5 current finite-fixture refresh

Date: 2026-09-07. Exploration: EXP-001658. Task: T-054.
Status: T0 internal diagnostic refresh, claim_bearing=false, not a signed
independent review. The paper PDF remains deferred.

## Scope

This refresh reruns the existing finite diagnostics for the current paper lane:

* `q3lock_pressure_seam_minmax_audit.py`, covering the periodic/open edge
  multiset, the corrected onsite allocation, the incidence Young split and the
  `eta=L^(-1/2)` density scale;
* `q3lock_fekete_convex_equicontinuity_audit.py`, covering explicit even-box
  tilings, remainder-volume bounds, convex secants and the moving-temperature
  seam scale.

The runs are provenance refreshes of the registered finite diagnostic scope. They
do not add a continuous family theorem, an operator/form-domain proof, a
thermodynamic-limit proof, or any phase conclusion.

## Reproduction

Run from the paper worktree:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/q3lock_pressure_seam_minmax_audit.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-q3lock-pressure-seam-minmax-audit-r2-current-v016/result.json
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/q3lock_fekete_convex_equicontinuity_audit.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-q3lock-fekete-convex-equicontinuity-audit-r2-current-v016/result.json
```

The first output passes 64/64 registered finite assertions and the second
passes 69/69. The exact diagnostic payloads are retained at the two paths above.

## Finding and boundary

The refresh reproduces the existing finite findings: the positive-direction
periodic edge convention gives `3 L^2` seam bonds and `48 L^2` scalar endpoint
occurrences, the incidence Young coefficient is `288 c^2 L^2/(eta g)`, and
`eta=L^(-1/2)` has the stated `O(L^(-1/2))` density scale. The even-box tiling
keeps every remainder side even, and the convex secant bound controls the
interior moving-beta comparison. No new arithmetic or convention defect was
isolated.

These finite fixtures are evidence for the displayed algebra only. They do not
certify the common form core, the min--max trace passage, the multidimensional
Fekete hypotheses for the actual Q3LOCK forms, the source-window DLR theorem,
the cusp, or the parity-related DLR pair. A1--A5 remain OPEN in the proof audit
until an independent reviewer gives location-specific dispositions.

## Next gate

Place the two current outputs in the A1--A5 review packet, obtain signed review
of the form/kernel and pressure-limit interfaces, and preserve the current T0,
claim-nonbearing and PDF-deferred boundaries. Any repair requires a new
source-hash capture and integrated replay.