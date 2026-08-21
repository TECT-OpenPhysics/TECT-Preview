# R-173: R-163 dyadic-forest Lean cross-check

## Exact checked content

The registered R-163 deterministic dyadic-forest certificate has the exact
margin chain

`4/25 - 3/100 = 13/100 > 1/10`.

Its T-050 coefficient thresholds reduce to

`5/11 - 9/20 = 1/220`,
`-1/110 - 9/10 = -10/11`,
and `3/20 < 27/100`.

The auxiliary rational checks are `(100/97)^4 < 13/10` and
`(27/5)*(3/2)/(1/2)^5 = 1296/5`.

`verification/lean/Tect/R163.lean` proves these identities in the pinned
Lean 4.32.1 environment. The primary lane reads the hash-pinned R-163
manifest and result, compiles Lean, and reports 31/31. The independent lane
uses only `Fraction` and agrees. The integrated lane reports 19/19 and checks
the no-overclaim boundary and hostile mutations.

## Interpretation

This is an arithmetic cross-check of a T4 finite deterministic theorem. The
analytic l2(HS) forest estimate, its A1/A7 hypotheses, and its uniformity claim
remain supplied by R-163 and are not re-proved by Lean. No random or nonlinear
past-dependent law, revisit, complete production owner, T-050, Nelson,
interacting measure, removal, continuum limit, phase selection, or Sector-A
statement is imported.

The checked margins are acceptance thresholds for a future authority-owned
complete production cylinder. They do not themselves provide the missing
owner entries. A13 remains open.
