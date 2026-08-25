# Six-site actual-Q3 generator-pairing certificate

## Scope

This is a claim-nonbearing finite checkpoint for EXP-001141. It extends the
actual Q3 full-generator Kubo-Mori pairing audit from the edge and square to
the registered six-site 2x3 graph. It does not assert a uniform estimate or a
QFT reconstruction.

## Finite result

The primary lane evaluates 16 rows: beta 1, times 0.05 and 0.1, cutoff radii
0.5, 1, 2, and 4, and both cutoff orientations. The independent eigenbasis
lane rebuilds the same rows. Primary, independent, and integrated checks pass
59/59, 56/56, and 13/13 respectively. Lean R311 passes the exact rational
graph, cutoff-order, generator-pairing, and volume-ratio fixtures.

For every row, with

`delta_H(X)=i[H,X]/hbar`,

the complete finite identity

`<delta_H^2 D,D>_KM + <delta_H D,delta_H D>_KM = 0`

holds within the declared `1e-8` numerical tolerance. The largest primary
cancellation error is `2.1684090494798863e-19`; the independent lane agrees
within the same tolerance.

The maximum state-weighted delta-D norm is `0.03381877701977454` at radius
0.5, `0.008803291366292517` at radius 1, and `1.7361322766689837e-14` at
radii 2 and 4. Relative to the committed four-site beta-1 baseline
`0.02382746805088884`, the six-site value is
`1.4193189535517179` times larger.

## Adversarial review

1. **Graph and support — UPHELD.** The seven-bond six-site fixture and the
   observable support `{0,1}` are checked by both numerical lanes.
2. **Cutoff and signs — UPHELD.** The same bond-coordinate cutoff and both
   orientations are used; the primary commutator and independent spectral
   delta share the `i[H,·]/hbar` convention, with R311 checking the exact
   scalar cancellation.
3. **Numerical tolerance — OPEN.** Agreement at `1e-8` is a finite numerical
   contract, not a representation-independent analytic error estimate.
4. **Volume trend — OPEN.** The ratio to the four-site artifact is a diagnostic
   from two volumes, not a monotonicity theorem, divergence proof, or no-go.
5. **Uniformity and domains — OPEN.** Only one beta, one oscillator
   dimension, one graph, and four cutoffs are sampled. Source/volume/beta
   uniformity, modular domains, common cores, and exhaustion independence are
   not established.
6. **QFT promotion — OPEN.** Common alpha, OS/KMS/GNS identification, gap,
   continuum, C6, Sector A, and Pre-A remain open.

## Next gate

The next proof-bearing task is an analytic volume- and beta-uniform bound for
the Kubo-Mori delta-D norm on a declared common core. If a certified
lower-bound family is eventually proved instead, record only that route
obstruction and move to the exact common-core carrier; numerical growth alone
does not fire the obstruction gate.

## Non-claims

This certificate does not prove a thermodynamic limit, a QFT, a mass gap, a
continuum limit, C6, Sector A, Pre-A, or any Clay result.
