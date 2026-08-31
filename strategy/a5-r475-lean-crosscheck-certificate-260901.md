# R-475 — Lean cross-check of the A5 branch-aware contract

## Verdict and boundary

`R-475` (`EXP-001354`) is a T0, claim-nonbearing auxiliary audit of the
already operator-confirmed A5 T6 conditional-composition package.  It checks
the frozen seven-hypothesis list, the disjoint full-production/scalar-
continuum branch topology, and the shell-mass numeric firewall with a pinned
Lean sidecar, a non-importing independent lane, and a fail-closed hostile
mutation suite.

This result does not change the A5 tier or the T-054 route.  It does not
provide a source-owned TECT generator or transfer, a common core or norm,
cutoff/volume uniform estimates, an ordered limit, a physical-sector map,
Pre-A/Sector-A closure, QFT, Yang--Mills, gravity or mass gap.

## Fixed source and scope

The source contract is
`claims/A5-SECTOR-A-SYNTHESIS/conditional_composition_manifest.json`, whose
theorem-contract digest is
`df01a1a3606d979307ac0bb8c9de14a4ab2d68fd83d228ed38f9e470eba823fc`.
The exact hypotheses and branch arrays are read from that source by both
Python lanes.  The scalar shell mass is read from the canonical A1 kernel
manifest and the full shell mass is re-derived from the canonical A1
functional parameters.  Lean's rational constants are explicitly test
oracles for those source-derived values; they are not calibrated physical
parameters.

The sidecar keeps the existing method order intact: forward T-054 remains the
owner-first mainline, observation-first T-059/T-061 remains an additive
inverse lane, and no TECT-YM or finite physical-empty/BCC result is imported
as a premise.

## Verification record

The integrated command runs the following in temporary child-output paths and
writes the durable JSON only after all checks have been collected:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/a5_r475_lean_crosscheck.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/a5_r475_lean_crosscheck_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/a5_r475_lean_crosscheck_hostile.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/a5_r475_lean_crosscheck_verify.py
```

The pinned formal command is:

```powershell
Push-Location verification/lean
C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lake.exe env lean Tect/R475.lean
Pop-Location
```

The expected child outcomes are primary `13/13`, independent `9/9`, hostile
`11/11` checks with all 10 mutations rejected, and Lean exit code 0.  The
integrated JSON is
`claims/A5-SECTOR-A-SYNTHESIS/runs/2026-09-01-a5-r475-lean-crosscheck/integrated.json`.

## Adversarial review

1. **Canonical placement.**  The weakness map is a top-level source-manifest
   field, not a field inside `theorem_contract`; the validator checks that
   placement and rejects removal or duplication.
2. **Branch conflation.**  Appending a full-production claim to the scalar
   branch changes the contract digest and fails the branch-topology mutation.
3. **Numeric copying.**  Both Python lanes recompute the masses from pinned
   source files; a collapsed mass fork fails the source-derived tolerance and
   separation checks.  Lean constants are labelled test oracles.
4. **Promotion.**  Tier, publication, method flags and scope firewalls are
   checked independently; mutation of any one fails closed.
5. **Lean overreach.**  The entrypoint contains only conjunction, separation,
   rational inequality and method-preservation propositions.  Analytic and
   physical assumptions remain outside the formal sidecar.

## Review condition

If a source hash changes, a child lane fails, a hostile mutation is accepted,
or Lean no longer compiles, retain the failing JSON and issue a new versioned
sidecar.  If a real source-owned production dynamics packet and common-core
uniform estimates arrive, instantiate the ordered-limit contract in a new
mainline result; do not revise R-475 into that theorem.
