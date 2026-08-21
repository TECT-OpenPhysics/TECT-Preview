# R-186 temporal packet algebra cross-check

R-186 / EXP-000901 is a T0, claim-nonbearing Lean and independent Fraction
cross-check of the finite algebra used by R-081.  The exact temporal fixture
has weighted mean `3/2`, covariance `5/2`, displacement `9/2`, and Douglas
value `81/10`; the weighted Cauchy and Douglas inequalities both hold.

The complete-packet fixture has endpoint `29/200`, expanded packet sum
`29/200`, residual `0`, and retained fresh-times-future cross term `6/25`.
The Lean entrypoint proves the general packet identity over `Rat`, so the
cross term cannot be silently dropped.

The primary lane compiles the pinned Lean 4.32.1 entrypoint and derives all
values from the manifest.  The independent lane uses only the Python standard
library and exact `Fraction` arithmetic.  The integrated lane checks source
hashes, AST/import separation, Lean escape tokens, eight hostile mutations,
event and exploration linkage, counts, and stored freshness.

Boundary: this result does not identify the production temporal map, prove
progressive/revisit uniformity, prove the complete same-root lower bound, or
close `OVERLAP_src`, Nelson, Sector-A, Pre-A, or any limit.  No new negative,
tier change, gate closure, or PDF follows.
