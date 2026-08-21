# R-186 R-081 temporal packet algebra Lean cross-check

R-186 / EXP-000901 is a T0, claim-nonbearing kernel cross-check of two
finite algebraic pieces used in the R-081 temporal route.  It is deliberately
smaller than the production theorem and does not change the A13 gate state.

## 1. Temporal weighted and Douglas fixture

The registered weights are `(1/2, 1/2)`, the temporal indices are `(1, 2)`,
the interval length is `1`, and the control value is `3`.  Exact rational
arithmetic gives

* weighted mean `sum_j w_j j_j = 3/2`;
* weighted covariance `sum_j w_j j_j^2 = 5/2`;
* displacement `(sum_j w_j j_j) * 3 = 9/2`;
* Douglas value `h^2 = (9/2)^2/(5/2) = 81/10`.

The weighted Cauchy inequality is therefore `(3/2)^2 <= 5/2`, and the
Douglas contraction is `81/10 <= 9`.  `verification/lean/Tect/R186.lean`
proves both fixture propositions by `norm_num` over `Rat`.

## 2. Complete-packet identity

For each row with base, fresh, future, traceFresh, and traceFuture, Lean proves
the exact identity

`((base+fresh+future)^2-base^2)/2-traceFresh/2-traceFuture/2`

`= base*fresh+fresh^2/2-traceFresh/2`

`  + (base+fresh)*future+future^2/2-traceFuture/2`.

The registered two-row fixture evaluates both the endpoint and the expanded
packet sum to `29/200`, so the residual is exactly zero.  The expanded form
retains the fresh-times-future cross term; its exact total is `6/25`, strictly
positive.  Erasing that term is not an equivalent packet identity.

## 3. Independent and adversarial verification

The primary lane derives every value from the manifest with `Fraction`, checks
the pinned R-081/A13/toolchain/Lake hashes, compiles Lean 4.32.1 with the
locked Mathlib manifest, and rejects nonempty Lean escape tokens.  The
independent lane is standard-library-only and recomputes all values without
importing the primary lane.  The integrated verifier checks exact child
agreement, source ASTs and import discipline, eight hostile mutations,
append-only EXP/event linkage, generated counts, and stored-versus-fresh
results.

The hostile mutations cover each exact scalar, endpoint/cross-term deletion,
gate promotion, and `sorry`/`admit`/`axiom`/`unsafe` insertion.  All must be
rejected.  The package has no new negative result and no PDF.

## 4. Scope boundary

This package does not identify the production temporal map, prove arbitrary
progressive or revisit uniformity, prove the complete same-root lower bound,
close `OVERLAP_src` or Nelson, construct an interacting measure, or close any
Sector-A, Pre-A, continuum, thermodynamic, or physical gate.  A Lean PASS
certifies only the encoded finite propositions; it is not a tier promotion or
gate closure.

Reproduction commands:

`E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 verification/scripts/lean_a13_temporal_packet_algebra_crosscheck.py --no-store`

`E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/lean_a13_temporal_packet_algebra_crosscheck_independent.py --output %TEMP%\r186-independent.json`

`E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/lean_a13_temporal_packet_algebra_crosscheck_verify.py --staged --no-store`

No R-186 PDF is issued.
