# R-382 increasing-cutoff endpoint modular moment stress certificate

## Result-first boundary

R-382 is a T0, claim-nonbearing finite stress checkpoint under EXP-001224.
It extends the R-381 endpoint-energy bridge over an increasing actual-Q3 edge
cutoff sweep and records the per-cutoff maxima of the endpoint moment, M_0 and
M_2.  The successive ratios are diagnostics only; no cutoff limit or
uniform bound is inferred.

## 1. New diagnostic viewpoint

R-381 reduced the endpoint modular debt to

`D_1 <= beta sqrt(M_0 M_2)`.

The missing analytic premise is a source-local, cutoff-uniform estimate for
the two moments on one Hamiltonian-derived common core.  R-382 tests that
premise directly instead of inspecting only the largest cutoff: the edge
fixture is evaluated at d=3,4,5,6, with all translated sites, both bond-term
orders, both time signs, every prefix position and both history adjoints.  A
V=4 square at d=2 remains as the cross-shape control.  For each cutoff the
maximum finite M_0, M_2, endpoint energy moment and Cauchy envelope are saved,
and consecutive-cutoff ratios are reported without a monotonicity assumption.

## 2. Finite verification

The primary lane passes `19,729/19,729` assertions and the non-importing
independent lane passes `17/17` aggregate assertions over `2,816` contexts
(edge d=3,4,5,6: 512; square d=2: 2,304).  The integrated verifier passes
`130/130`; Lean R382 compiles with the pinned toolchain.  Primary and
independent numeric fields agree within `1.918465386552270e-13`.

The edge per-cutoff maxima are:

| cutoff | max M_0 | max M_2 | max endpoint | max Cauchy envelope |
|---:|---:|---:|---:|---:|
| 3 | 2.733031855844076 | 0.008378198414559081 | 0.004114253036840313 | 0.14167751530698108 |
| 4 | 3.4283208579615874 | 0.06491749177608952 | 0.022778768600647783 | 0.4506642029725953 |
| 5 | 4.703343964629605 | 0.4870620188494611 | 0.09831198953294297 | 1.5135455747204718 |
| 6 | 41.64826651661874 | 17.719559304500326 | 2.153583814589319 | 27.165951639338186 |

The edge successive ratios for `(d=3,d=4,d=5,d=6)` are M_0
`1.2544020848607258`, `1.371908919699576`, `8.855033106195243` and M_2
`7.748383192176516`, `7.502785543985794`, `36.38049903040583`.  The declared
finite growth-warning threshold is `1.05`, so the diagnostic flag is true.
The square control has max M_0 `0.9999999999999996` and max M_2
`1.725572363131804e-30` at d=2.  These are finite-grid observations, not a
divergence statement.

## 3. Adversarial review

1. **Monotonicity.**  No monotonicity is assumed; profiles and ratios are
   recorded in declared cutoff order and only flagged as a finite warning.
2. **Growth interpretation.**  The d=5 to d=6 jump is retained, but a finite
   jump does not prove divergence or rule out a renormalized common core.
3. **Beta coverage.**  Both beta values `1/2` and `1` are included at every
   cutoff; no beta-uniform conclusion is drawn.
4. **History coverage.**  Both time signs, term orders, all prefixes and both
   adjoints are included, so a favorable orientation cannot hide the profile.
5. **Gibbs identity.**  The logarithmic endpoint is checked against beta times
   the absolute energy difference on every finite spectrum, including shifts.
6. **Degenerate gaps.**  Zero and near-zero gaps remain in the sums; no ratio
   divides by a zero moment, and the Kubo weight uses its continuous diagonal.
7. **State weighting.**  M_0 and M_2 are computed in both Gibbs orientations;
   Hermitian symmetry and the endpoint reconstruction are separately checked.
8. **Coverage and independence.**  Per-cutoff context counts are asserted and
   an independent builder reconstructs the oscillator, graph, spectrum and
   prefix histories without importing the primary audit.
9. **Lean scope.**  R382 formalizes nonnegative profile ratios and the
   diagnostic dichotomy only; it does not formalize the matrix numerics or a
   cutoff trend theorem.
10. **QFT promotion.**  Source/volume/cutoff/beta uniformity, common core,
    common alpha, OS/KMS/GNS dynamics, gap, continuum, C6, Sector-A and
    Pre-A remain open.

## 4. Decision and next gate

R-382 advances R-381 by exposing the cutoff dependence that a putative
uniform M_0/M_2 premise must control.  The edge profile is compatible with a
finite-growth warning, especially at d=5 to d=6, while the square control is
nearly diagonal in this fixture.  Because this is not an increasing-volume or
large-cutoff theorem, no negative result is registered.  The next analytic
step is to prove a Hamiltonian-derived common-core estimate that explains or
controls the edge profile; if a further validated sweep confirms growth, the
obstruction must be stated as a separate named gate.  Any proved premise can
then be inserted into the R-380 interpolation and the R-377 resolvent
telescope.

Source/volume/cutoff/beta uniformity, common core, common alpha, OS/KMS/GNS
dynamics, mass gap, continuum, C6, Sector-A and Pre-A remain open.  No new
negative result, tier change or R-382 proof-note PDF is issued.
