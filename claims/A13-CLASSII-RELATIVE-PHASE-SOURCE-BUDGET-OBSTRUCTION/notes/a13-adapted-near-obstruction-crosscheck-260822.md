# R-187 adapted NEAR obstruction cross-check

R-187 / EXP-000902 is a T0, claim-nonbearing Lean and independent Fraction
cross-check of finite diagnostics from the R-081 adapted NEAR route.

The nonlinear fixture has zero conditional first variation at both roots but
root-square innovations `+4/5` and `-4/5`.  At `gamma=1/20` the adapted ledger
is `(39/80,121/240,1/120,120)`, while all registered control-control pair
slacks are negative: `-19/120`, `-23/120`, and `-13/40`.  The finite Doob
witness has square sum `2`, terminal `L2=2`, terminal `L6=32`, and square-L6
value `8`, so the bounded `L6` inequality holds.

The Lean entrypoint, primary Fraction lane, stdlib-only independent lane, and
integrated mutation verifier are pinned.  Boundary: these fixtures do not
identify the production adapted operator or close the complete same-root,
progressive/revisit, `OVERLAP_src`, Nelson, Sector-A, Pre-A, or limit routes.
No new negative, tier change, gate closure, or PDF follows.
