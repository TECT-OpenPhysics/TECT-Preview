# EXP-001088 — weighted triple-commutator volume stress certificate

## Decision

The declared (s=3/4) four-leg weighted Gibbs seminorm is a valid finite
matrix diagnostic for the actual Q3 coordinate-cutoff difference, but it does
not supply the volume-uniform multiplier required by the projected
`D,delta-D` gate. Both the support-local and full-volume shifted energy weights
show strong finite-volume growth. This is a route-local obstruction to this
candidate topology, not a no-go theorem for every possible Q3 common-core
topology.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress_verify.py
lake env lean Tect/R270.lean
```

The primary lane passes 65/65, the independent lane passes 56/56, the
integrated verifier passes 46/46, and R270 compiles with no warnings or
axioms. The canonical JSON artefacts are under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-08-25-primary-pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress/`.

## Model and exact identity

The finite models use oscillator dimension three on a two-site edge, a
four-site square face, and a six-site 2x3 rectangular grid. The observable is

\[
A_2=\exp\!\left(i a(q_0+q_1)/\hbar\right),\qquad a=1/3,
\]

and the smooth coordinate cutoff changes only bond coordinates. Writing
`W_L=H-H_L` and `B=[W_L,[H,A_2]]`, the direct second coefficient is
`D''(0)=-B/hbar^2` for the positive orientation. The modular companion is

\[
\delta D''(0)=-\beta[H,D''(0)]
 =\frac{\beta}{\hbar^2}[H,[W_L,[H,A_2]]],
\]

where the displayed nested commutator is evaluated in the code as
`[H,[W_L,[H,A_2]]]`; the intermediate bracket is not reordered by a Jacobi
shortcut. R270 checks the sign and scalar coefficient convention.

For a shifted positive weight `K`, the diagnostic norm is the square root of
the four Hilbert–Schmidt legs
`K^s X rho^(1/2)`, `K^s X* rho^(1/2)`, `X K^s rho^(1/2)`, and
`X* K^s rho^(1/2)`, with `s=3/4`. Two weights are tested: the local
`I+H_{0,1,(0,1)}` weight and the full-volume `I+H` weight.

## Results

The maxima over the declared radii are:

| volume | local modular weighted | full-volume modular weighted | local direct weighted | full-volume direct weighted |
|---:|---:|---:|---:|---:|
| 2 | 6.2135874113 | 6.2135874113 | 2.5613260830 | 2.5613260830 |
| 4 | 21.1841912659 | 30.4046432745 | 4.6560548858 | 6.7717433187 |
| 6 | 33.9749450217 | 61.8549607811 | 5.7753940867 | 10.5685520687 |

Relative to volume two, the volume-six ratio is `5.4678469574` for the
support-local modular companion and `9.9547904755` for the full-volume
weight. The direct weighted coefficient ratios are `2.254865...` and
`4.126...`, respectively. The source commutator and disjoint-tail
commutator remain below the declared tolerance, and the radius-two tail is at
the numerical floor in every volume.

## Adversarial review

1. **Nested-commutator sign:** the direct and modular identities are checked
   in both code lanes and R270; no Jacobi reordering is silently used. **UPHELD.**
2. **Configuration locality:** `[W_L,A_2]` and the disjoint-tail commutator
   are measured, not inferred from graph labels. **UPHELD.**
3. **Weight positivity:** each shifted local and full weight is spectrally
   checked before taking the (3/4) power. **UPHELD.**
4. **Two-sidedness:** all four left/right and adjoint Gibbs legs are included;
   one-sided norm control is not substituted. **UPHELD.**
5. **Independent reconstruction:** the independent lane rebuilds the model,
   cutoff, thermal state, commutators, and weighted legs without importing the
   primary module. **UPHELD.**
6. **Volume interpretation:** the ratios compare only volumes 2, 4, and 6;
   they are not asserted to be an asymptotic lower bound. **UPHELD.**
7. **Truncated oscillator:** finite-dimensional CCR defects are not hidden;
   the result is explicitly a matrix diagnostic, not an exact infinite-core
   theorem. **UPHELD.**
8. **QFT promotion:** direct `D,delta-D` Cauchy, modular domain, product/core
   density, exhaustion, group law, common dynamics/KMS, OS/GNS, gap,
   continuum, C6, Sector A, and Pre-A remain open. **UPHELD.**

## Boundary and next action

Closed here: finite actual-Q3 triple-commutator identity, finite four-leg
weighted rows, and the candidate-weight scaling diagnostic. Open: a
source/volume-uniform weighted common-core theorem. The next route is either
to derive a different local cancellation/weight whose multiplier is proved
uniform analytically, or to prove a lower-bound obstruction for this candidate
and register it as a route-specific negative result. No common-alpha or QFT
identification is promoted from this package.

Provenance hashes:

```text
primary       dea3190153b769a9241652f7a2eb8fe8be0755ff78d299990dd099f70e22cd7a
independent   db9bfc3eaca7c83dbd667a995c198e9efc3c4f360bab646cce0c87cd21058fdc
manifest      787429a09faa1535da0394899d1d503fca53d518fdefd88b10614f17568b92a7
R270          f3176f62e6eb4527009a263cd117f81fb0a2849e0198984572421b063c1960fd
```
