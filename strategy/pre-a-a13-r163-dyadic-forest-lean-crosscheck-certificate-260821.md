# R-173: R-163 deterministic dyadic-forest Lean cross-check

## Status

This is a T0, claim-nonbearing kernel cross-check. It does not promote A13,
T-050, Sector A, or any physical claim.

## Exact result

The R-163 certificate supplies an origin gap of `4/25`. Its registered loss
`3/100` leaves

`4/25 - 3/100 = 13/100 > 1/10`.

The T-050 coefficient bookkeeping gives

`5/11 - 9/20 = 1/220`,
`-2*(1/220) = -1/110`, and
`-1/110 - 9/10 = -10/11`.

The sextic allocation is admissible at `3/20 < 27/100`. The recursive tangent
guard `(100/97)^4 < 13/10` and the source third-derivative fixture `1296/5`
are also checked exactly.

These statements are proved by the Lean kernel over `Rat` using
`norm_num`. The independent lane recomputes the same values with only the
Python standard library `Fraction` type. The integrated lane hashes the
R-163 manifest, children, current A13 status, Lean toolchain, Lake files, and
the Lean source, and rejects eight hostile mutations.

## Boundary

The Lean file checks only rational consequences of the registered R-163
certificate. It does not prove the analytic dyadic-forest estimates, the A1 or
A7 operator hypotheses, random or nonlinear past-dependent laws, revisit or
branching control, the complete A13 owner, T-050, Nelson or measure
construction, floor/removal or continuum limits, phase selection, or Sector-A
closure. The R-163 deterministic finite-forest theorem remains at its
registered T4 scope.

No new negative result, tier change, gate closure, PDF, or physical conclusion
follows.

## Reproduction

```text
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 verification/scripts/lean_r163_dyadic_forest_crosscheck.py --no-store
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/lean_r163_dyadic_forest_crosscheck_independent.py --output %TEMP%\r163-independent.json
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/lean_r163_dyadic_forest_crosscheck_verify.py --staged --no-store
```

Expected output: `PRIMARY R-163 LEAN PASS 31/31`,
`INDEPENDENT R-163 LEAN CROSSCHECK PASS`, and
`INTEGRATED R-163 LEAN PASS 25/25`.
