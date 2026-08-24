# EXP-001090 — actual-Q3 positive-time Kubo–Mori history certificate

## Decision

The Kubo–Mori/Duhamel logarithmic-mean topology gives a valid finite
positive-time history diagnostic for the actual-Q3 cutoff models and is
independently reproduced for both orientations. Its values are smaller than
the arithmetic-mean comparison, but the modular companion still increases
across volumes 2, 4, and 6. This does not provide the source/volume-uniform
history bound required by the projected QFT `D,delta-D` gate. The conclusion
is route-local and finite, not a no-go theorem for every common-core topology.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_kubo_mori_positive_time_history.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_kubo_mori_positive_time_history_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_kubo_mori_positive_time_history_verify.py
lake env lean Tect/R272.lean
```

The primary lane passes 133/133, the independent lane passes 129/129, the
integrated verifier passes 79/79, and R272 compiles without warnings or
forbidden axioms. Canonical JSON artefacts are under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-08-25-primary-pre_a_cp1_st8_q3lock_kubo_mori_positive_time_history/` and its independent sibling directory.

## Model and finite history

The finite models use oscillator dimension three on a two-site edge, a
four-site square face, and a six-site 2x3 rectangular grid. The observable is

\[
A_2=\exp\!\left(i a(q_0+q_1)/\hbar\right),\qquad a=1/3,
\]

and only bond coordinates receive the smooth cosine cutoff. With
`W_L=H-H_L`, the reference is the uncut H history and the two perturbed
histories use `H+sigma W_L`, for `sigma=-1,+1`. At times `0.05` and `0.10`,

`D_sigma(t) = U_(H+sigma W_L)(t) A_2 U_(H+sigma W_L)(t)^* - U_H(t) A_2 U_H(t)^*`,

and the finite modular companion is evaluated as
`delta D_sigma(t)=-beta[H,D_sigma(t)]`. In the uncut H eigenbasis with Gibbs
probabilities `p_i`, the Kubo–Mori weight is
`L(p_i,p_j)=(p_i-p_j)/(log p_i-log p_j)` with diagonal limit `p_i`; the
two-sided square norm is `2*sum L|X_ij|^2`. The arithmetic comparison replaces
`L` by `(p_i+p_j)/2`. R272 checks exact rational coefficient, orientation,
time/radius order, graph, and finite-scope fixtures; it does not formalize
the floating-point propagators or a thermodynamic limit.

## Results

The maxima over both orientations, declared times, and radii are:

| volume | Kubo–Mori D(t) | arithmetic D(t) | Kubo–Mori delta D(t) | arithmetic delta D(t) |
|---:|---:|---:|---:|---:|
| 2 | 0.0080425069 | 0.0093767225 | 0.0175211431 | 0.0213010043 |
| 4 | 0.0118427847 | 0.0168376850 | 0.0474517845 | 0.0729462141 |
| 6 | 0.0131919575 | 0.0206860871 | 0.0670533773 | 0.1166173741 |

The source commutator is below `1e-8` in every row and the radius-two tail is
at the `1e-9` numerical floor. The finite values are reproducible in both
lanes. Their growth is reported as a diagnostic only: it is not an
asymptotic lower bound, a monotonicity theorem, or a proof that no other
topology can close the QFT gate.

## Adversarial review

1. **Positive-time orientation:** both `H+W_L` and `H-W_L` histories are
   compared to the same uncut-H reference at every row. **UPHELD.**
2. **Modular derivative:** `delta D=-beta[H,D]` is computed directly and its
   identity is checked row by row. **UPHELD.**
3. **Kubo–Mori diagonal limit:** equal Gibbs probabilities use the exact
   `p_i` limit; no zero logarithmic gap is divided. **UPHELD.**
4. **Support locality:** `[W_L,A_2]` and the radius-two zero-tail fixture are
   measured rather than inferred. **UPHELD.**
5. **Unitarity:** each perturbed propagator is checked against `U*U=I` within
   the finite tolerance. **UPHELD.**
6. **Mean comparison:** arithmetic-mean values remain a comparison lane and
   do not replace Kubo–Mori in the route decision. **UPHELD.**
7. **Volume interpretation:** only volumes 2, 4, and 6 are used; ratios are
   finite diagnostics, not asymptotic lower bounds. **UPHELD.**
8. **Independent reconstruction:** the independent lane rebuilds the model,
   cutoff, Gibbs state, propagators, commutators, and mean matrices without
   importing primary code. **UPHELD.**
9. **QFT promotion:** uniform history, direct Cauchy, modular domain,
   product/core density, exhaustion, common dynamics/KMS, OS/GNS, gap,
   continuum, C6, Sector A, and Pre-A remain open. **UPHELD.**

## Boundary and next action

Closed here: finite positive-time Kubo–Mori and arithmetic history rows for
both orientations, finite modular identity, support commutation, independent
reproduction, and R272. Open: an analytic source/volume-uniform common-core
history bound and the downstream direct `D,delta-D` Cauchy theorem. The next
route is to derive a local cancellation or alternative state topology with a
uniform multiplier, or enlarge the structured family and formalize only a
route-specific obstruction if the growth persists. No common-alpha or QFT
identification is promoted from this package.

Provenance hashes:

```text
primary       55a0cdafed629955ca4cad31d317c1f4844f38bee41c45f5e8ea3c3106cc0126
independent   d9b63a7b4eb4c2a0e233b01939a7097319d0d8791377b911cc18cf3468c1bb9b
manifest      02bee33706981ee79cb41b605531cfbaf28dd58a6e995d64f9ebac10f42aeba5
R272          99bccb08f97dca6ab9911bf3309ab73dbf67fe05dc5292954212120d94a9b30e
```
