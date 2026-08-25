# EXP-001149 certificate: source-weighted direct D and delta-H D

## Result

On the actual Q3 edge, square, and six-site finite Hamiltonians, define

\[
D_\sigma(t,a)=U(H+\sigma W_L,t)A_aU(H+\sigma W_L,t)^*
             -U(H,t)A_aU(H,t)^*,
\]

and the full-generator derivative

\[
\delta_H D_\sigma(t,a)=i[H,D_\sigma(t,a)]/\hbar.
\]

The grid uses volumes `2,4,6`, beta `0.5,1,2`, amplitudes `0,1,2,5`,
radii `0.5,1`, time `0.05`, and both cutoff orientations.  Both the Gibbs
seminorm and the four local-energy legs are normalized by

\[
w_\sigma(a)=(1+|a|)\exp(|a|^4/5).
\]

The primary lane passes `409/409`, the independent trace lane `293/293`, the
integrated verifier `16/16`, and Lean R319 compiles without warnings.

The normalized Gibbs maxima for `D` over volumes `2,4,6` are

\[
(0.0014327605,\;0.0027173447,\;0.0035070978),
\]

and for `delta_H D` they are

\[
(0.0032618640,\;0.0122918794,\;0.0214541745).
\]

The corresponding normalized local four-leg maxima are

\[
D: (0.0048236832,\;0.0098995363,\;0.0129108973),
\]

\[
\delta_H D: (0.0125666336,\;0.0473999567,\;0.0821981509).
\]

The endpoint ratios are `2.44779` and `6.57727` in the Gibbs seminorm, and
`2.67656` and `6.54098` in the local four-leg norm.  The derivative therefore
has the larger finite volume sensitivity.  These are finite diagnostics, not
asymptotic lower bounds.

## Interpretation and boundary

The candidate entire source weight remains effective against high source
amplitudes, but it does not make either `D` or `delta_H D` volume-uniform on
the tested grid.  This closes a finite, independently reconstructed
interface for the direct Cauchy route and identifies the derivative as the
sharper analytic target.  It does not prove a common-core estimate, direct
Cauchy theorem, modular transfer, exhaustion independence, common alpha,
OS/KMS/GNS reconstruction, a gap, continuum, C6, Sector A, or Pre-A.

## Adversarial review

- **Derivative convention — UPHELD:** the audited derivative is explicitly
  `i[H,D]/hbar`; no beta-scaled modular commutator is silently substituted.
- **Source normalization — UPHELD:** unnormalized values and norm-level
  division by one declared `w_sigma(a)` are both retained.
- **Noncommuting weight — UPHELD:** `K_X` is a full-H matrix and the trace
  formulas preserve all four orientations.
- **Finite volume — UPHELD-OPEN:** endpoint ratios are finite-grid diagnostics
  only, not divergence or no-go results.
- **Cauchy promotion — UPHELD-OPEN:** finite rows do not establish a uniform
  common-core D/delta-D Cauchy estimate or exhaustion independence.
- **QFT promotion — UPHELD-OPEN:** modular transfer, products, OS/KMS/GNS,
  gap, continuum, C6, Sector A, and Pre-A remain open.

## Next gate

Define the actual Q3 local entire source seminorm on a common core and seek a
simultaneous source-, volume-, cutoff-, and beta-uniform bound for `D` and
`delta_H D`.  The first analytic bridge to test is a certified local energy
moment or centered-weight estimate for the derivative; absent that, register
the exact route-local obstruction rather than promoting the finite trend.
