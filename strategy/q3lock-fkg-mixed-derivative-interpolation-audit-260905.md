# Q3LOCK FKG mixed-derivative and interpolation audit

**Status:** T0 finite association audit; P-06 remains open  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Related audits:** strategy/q3lock-fkg-continuous-association-discretization-audit-260905.md; strategy/q3lock-p06-continuous-loop-association-independent-audit-260905.md  
**PDF:** deferred until mathematical content freeze, external review, and final release review

## 1. Question and strict boundary

This note isolates the finite algebra that feeds the P-06 continuous-loop FKG
route.  It rechecks the nonradial Q3 mixed derivative, the differential to
lattice condition, order-preserving periodic interpolation, and the clipped
coordinate-product device.  The audit is deliberately narrower than a
path-space theorem: it does not prove the fixed-volume Gaussian/residual
convergence, the KP/Feynman--Kac topology, spatial weighted-tempered
accumulation, a source cusp, or DLR multiplicity.

The only external association result used by this route is the finite
distributive-lattice proposition of Fortuin--Kasteleyn--Ginibre.  The
continuous-variable and loop passages below are Q3LOCK-local arguments and
remain conditional on their explicitly named hypotheses.

## 2. Exact Q3 mixed derivative

For one Q3 edge, the onsite interaction is

    W(x,y) = (lambda/4) (x-y)^2 (x^2+y^2).

Expansion and differentiation give

    -partial_x partial_y W
      = (lambda/4) (6*x^2 - 8*x*y + 6*y^2)
      = (lambda/4) ((x+y)^2 + 5*(x-y)^2) >= 0

for lambda >= 0.  The Euclidean log density contains -W, so this is the
off-diagonal mixed derivative of its log density.  Unary quartic, harmonic,
counterterm, and source-linear terms have zero mixed derivative.  A quadratic
difference term -(kappa/2)(x-y)^2 contributes +kappa to the mixed derivative.
Nonedges contribute zero.  Thus the finite Q3LOCK time-grid log density has
nonnegative mixed derivatives at every distinct coordinate pair, without an
O(8) rotation-invariance assumption.

The identity is pointwise.  It does not by itself provide a volume-uniform
lower bound, a path-space order, or a phase statement.

## 3. Differential-to-lattice implication

Let Phi be a C2 function on a finite coordinate space and suppose
partial_i partial_j Phi >= 0 for i != j.  For two points x and y, interchange
one inverted coordinate pair at a time.  The change in Phi is a double
integral of partial_i partial_j Phi over the corresponding coordinate
rectangle, hence is nonnegative.  A finite sequence of these interchanges
turns (x,y) into (x meet y, x join y), where meet and join are coordinatewise.
Therefore

    Phi(x meet y) + Phi(x join y) >= Phi(x) + Phi(y).

For f=exp(Phi), this is the finite FKG lattice condition

    f(x meet y) f(x join y) >= f(x) f(y).

On a compact cube, a rectangular coordinate grid inherits the same
condition with weights f(z) times the cell volume.  The finite FKG
proposition then gives covariance nonnegativity for bounded increasing grid
functions.  Riemann sums pass the mesh spacing to zero for bounded continuous
tests.  Increasing compact cubes pass to the full finite-dimensional law by
dominated convergence.  This sequence uses finite lattices only; it does not
silently cite FKG as an infinite-dimensional loop theorem.

## 4. Periodic interpolation is order preserving

For a periodic time grid with N sites, define on each cell

    I_N(x)(t_n + theta Delta)
       = (1-theta) x_n + theta x_(n+1),
    0 <= theta <= 1,

with n+1 read modulo N.  If x_n <= y_n at every grid site, both coefficients
are nonnegative and hence I_N(x)(t) <= I_N(y)(t) for every t, including the
wrap cell.  Thus composing bounded pointwise-increasing loop functionals with
I_N preserves monotonicity.  If the interpolated laws converge weakly in a
topology where the chosen functionals and their product are bounded
continuous, the finite-mesh association inequality passes to the loop law.
This is a conditional weak-limit step, not a total-variation assertion.

## 5. Clipped coordinate products

For a coordinate Y define

    phi_R(Y) = max(-R, min(Y,R)),
    F_R(Y) = phi_R(Y) + R.

Then F_R takes values in [0,2R] and is increasing.  For two coordinates Y and
Z, the product F_R(Y) F_R(Z) is therefore an increasing nonnegative test on
the finite coordinate lattice.  At zero source, parity supplies the
zero one-point means needed to convert the clipped association inequality to
a nonnegative clipped covariance.

Removing the clips is a separate integrability statement.  Pointwise,
phi_R(Y) phi_R(Z) tends to YZ and

    |phi_R(Y) phi_R(Z)| <= |Y Z|
      <= (Y^2 + Z^2)/2.

A finite second-moment bound, or a uniform-integrability replacement, is
therefore required.  Weak convergence alone is insufficient.  The
source-uniform quartic and normalizer estimates recorded in the companion
P-06 audits are the intended Q3LOCK input; this note does not reprove their
volume-uniform form-domain or thermodynamic parts.

## 6. Executable finite diagnostic

The independent verifier is

    verification/scripts/q3lock_fkg_mixed_derivative_interpolation_audit.py

Run from the repository root with

    E:\Dev\TECT.venv\Scripts\python.exe verification/scripts/q3lock_fkg_mixed_derivative_interpolation_audit.py

It recomputes the polynomial mixed derivative using exact rational arithmetic,
checks rectangle supermodularity for the Q3 and quadratic pair terms, tests
periodic interpolation on all wrap cells, rejects a negative interpolation
coefficient, and checks the clip range, product monotonicity, domination, and
parity-symmetric covariance fixtures.  Inputs are declared once; all reported
counts and bounds are derived.  The JSON artifact records every assertion and
the verifier hash.  It is diagnostic evidence, not a proof of the analytic
hypotheses.

## 7. Adversarial checks

| Objection | Disposition |
|---|---|
| The mixed derivative calculation needs O(8) internal rotation symmetry | **UPHELD AS FALSE:** the Q3 identity is pointwise and nonradial. |
| A finite FKG citation already proves association on continuous loops | **UPHELD AS FALSE:** only the finite grid proposition is imported; interpolation and weak passage are separate. |
| A sign-changing coordinate product can be inserted directly into FKG | **UPHELD AS FALSE:** constant-shifted nonnegative clips are used first. |
| Weak convergence automatically passes unbounded products | **UPHELD AS FALSE:** a second-moment or uniform-integrability bound is explicit. |
| A negative interpolation coefficient still preserves order | **UPHELD AS FALSE:** the hostile verifier produces a reversed interpolated order. |
| Fixed-volume association closes the strict cusp or DLR phase theorem | **UPHELD AS FALSE:** pressure, infrared, source-window, compactness, and DLR gates remain open. |

## 8. Disposition and next gate

The Q3 mixed-derivative sign, finite-grid supermodularity route, periodic
order-preserving interpolation, and clipped-product logic are internally
consistent under their stated finite and integrability hypotheses.  This is an
advanced T0 proof-text audit only.  The next gate is an independent
line-by-line review of the actual KP/Feynman--Kac topology, fixed-volume
Gaussian/residual convergence, and the source-uniform moment estimates needed
to instantiate the conditional steps above.  P-06, P-09, pressure, KKK,
source-window, claim registration, external referee, and content-freeze gates
remain open.

## 9. Explicit nonclaims

No path-space MTP2 theorem, unconditional continuous-loop FKG theorem,
strict source cusp, positive infrared zero mode, phase coexistence, DLR
multiplicity, extremality, purity, clustering, KMS state, real-time dynamics,
ground-state phase, spectral gap, continuum limit, physical-vacuum,
cosmological, Sector A, CP1, C6, Pre-A, Yang--Mills, or mass-gap conclusion is
asserted.  No claim card, manuscript, submission, upload, release, tag, or PDF
is created.
