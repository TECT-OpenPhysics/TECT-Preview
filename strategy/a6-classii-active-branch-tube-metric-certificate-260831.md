# R-463 certificate — fixed-floor active-branch tube metric

## Route role

R-463 is an additive T0 interface for the existing A6/A7 fixed-floor
Class-II programme. It follows R-461's branch dichotomy and R-462's active
radial/angular normal form. It does not replace the T-054 forward method, the
T-059/T-061 observation-first inverse lane, the owner order, or any promotion
firewall.

## Exact statement

Let `Q=[[a,b],[b,c]]` be the A1-derived positive coefficient matrix, set
`Delta=a*c-b^2`, `trace=a+c`, `lambda_r=Delta/trace`, and
`kappa=a+2*b+c`. For active jet coordinates
`x=d_s`, `y=delta`, and `u=s*t` in three spatial components, define

`E2 = 2 e_II = q_Q(x,y) + kappa*|u|^2` and
`T_active^2 = lambda_r*(x^2+y^2) + kappa*|u|^2`.

The exact identity

`trace*(q_Q-lambda_r*(x^2+y^2)) = (a*x+b*y)^2+(b*x+c*y)^2`

gives `E2 >= T_active^2`. A separate two-coordinate flat proxy has
`T_flat^2=|f|^2` and `E_flat=0`; its outside-tube energy barrier is therefore
zero.

## Finite diagnostic scope

The primary audit enumerates the declared `{-1,0,1}^5` active local grid. For
each declared threshold and inverse temperature it records the exact outside
count and minimum `E2`, then evaluates the finite proxy
`N*exp(-beta*E2_min/2)` using the unit lower bound `Z>=1`. The independent audit
uses a denser `{-2,-1,0,1,2}^5` grid. These are bounded combinatorial stress
tests, not samples of the correlated finite-cutoff field measure.

## Assumptions and missing inputs

The A1 coefficients, R-462 coordinates, fixed positive rho floor, and the
existing functional are controlling. The grid, thresholds, inverse
temperatures, and two flat proxy coordinates are explicit audit inputs. A
source-owned correlated Gibbs law, branch-conditioned probability map, entropy
density, Jacobian/volume scaling, partition and tightness estimates, floor
removal, ordered limits, Q3LOCK dynamics, physical identity, and QFT/Yang--Mills
bridge are still missing.

## Reproduction

```text
python -X utf8 verification/scripts/a6_classii_active_branch_tube_metric.py
python -X utf8 codes/foundations/a6_classii_active_branch_tube_metric_independent.py
python -X utf8 codes/foundations/a6_classii_active_branch_tube_metric_hostile.py
python -X utf8 verification/scripts/a6_classii_active_branch_tube_metric_verify.py
```

The algebraic kernel is `verification/lean/Tect/R463.lean` and is compiled with
the pinned Lean toolchain through `lake env lean Tect/R463.lean`.

## Adversarial disposition

Eight hostile mutations reject a wrong radial sign, wrong angular coefficient,
omitted mixed term, altered gap identity, strict-shell convention, missing
factor of two, false flat-direction coercivity, and premature tightness
promotion. No mutation is allowed to alter the canonical functional or promote
the bounded proxy.

## Boundary and next gate

The active metric is a reusable local lower-bound interface only. The flat
proxy demonstrates why a full-field entropy/tightness proof needs an additional
phase/singlet control mechanism. R-463 does not close a Gibbs tube probability,
entropy, partition, tightness, continuum, physical branch, Pre-A, Sector A,
QFT, Yang--Mills, or mass-gap claim. The next gate is a source-owned
branch-conditioned finite-cutoff estimate with explicit flat-direction entropy
accounting; absent that owner input, this route remains T0 and non-claim-bearing.
