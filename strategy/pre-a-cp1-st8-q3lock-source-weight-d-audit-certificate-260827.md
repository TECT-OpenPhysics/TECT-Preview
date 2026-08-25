# EXP-001148 certificate: actual Q3 source-weight calibration

## Result

The finite actual-Q3 history was evaluated with the local edge-energy weight

\[
K_X=H_X-\min(H_X)I+I
\]

and the candidate entire source weight

\[
w_\sigma(a)=(1+|a|)\exp(\sigma |a|^4),\qquad \sigma=1/5.
\]

The grid contains volumes `2,4,6`, beta values `0.5,1,2`, source amplitudes
`0,1,2,5`, radii `0.5,1`, time `0.05`, and both cutoff orientations.  The
primary lane passes `414/414`, the independent trace lane passes `293/293`,
the integrated verifier passes `14/14`, and Lean R318 compiles without
warnings.

The raw local four-leg norm maxima by volume are

\[
(0.0117833200,\;0.0241826418,\;0.0315388112).
\]

After division by `w_sigma(a)`, the corresponding maxima are

\[
(0.0048236832,\;0.0098995363,\;0.0129108973),
\]

with finite endpoint ratio `2.6765641`.  The full shifted-H baseline has
normalized maxima `(0.0048236832, 0.0155316708, 0.0259965445)`.  At amplitude
`5`, the normalized local maxima are approximately
`1.59e-58`, `3.50e-58`, and `4.54e-58`, showing strong source-amplitude
suppression on this grid.

## Interpretation and boundary

The candidate weight is effective against the tested source-amplitude growth,
but it does not remove the finite-volume growth of the actual Q3 local
four-leg norm.  This is an advanced finite calibration of the bridge between
the prescribed-word envelope of EXP-001032 and the actual Q3 interface of
EXP-001147.  It is not a source/volume-uniform entire seminorm theorem, an
actual Q3 word-incidence theorem, or a thermodynamic QFT result.

The common-core domain, six-neighbour and reverse-orientation history sum,
modular transfer, direct `D`/`delta-D` Cauchy, product/core density,
exhaustion independence, common alpha, OS/KMS/GNS identification, broken
sector gap, continuum, C6, Sector A, and Pre-A remain open.

## Adversarial review

- **Source normalization — UPHELD:** squared four-leg sums and their
  norm-level division by one declared scalar `w_sigma(a)` are both retained.
- **Noncommuting local weight — UPHELD:** `K_X` remains a matrix in the
  full-H representation; no commutation with the Gibbs state or history is
  assumed.
- **Finite amplitude and volume — UPHELD-OPEN:** source suppression and the
  endpoint ratio are finite diagnostics, not asymptotic statements.
- **Entire-series transfer — UPHELD-OPEN:** Lean checks the prescribed-family
  rate, margin, prefactor, and normalization fixture; actual Q3 word
  incidence, cancellations, domain, and volume-uniform history remain open.
- **Independent reconstruction — UPHELD:** all four legs are rebuilt from
  trace identities without inserting `rho^(1/2)` and agree within tolerance.
- **QFT promotion — UPHELD-OPEN:** no common-core, exhaustion, OS/KMS/GNS,
  gap, continuum, C6, Sector A, or Pre-A promotion is made.

## Next gate

Define the actual Q3 entire source seminorm on the declared common core and
prove or refute a six-neighbour, two-orientation, source- and volume-uniform
history bound.  If a centered/local refinement still leaves a certified
volume factor, record that exact obstruction before attempting exhaustion or
QFT promotion.
