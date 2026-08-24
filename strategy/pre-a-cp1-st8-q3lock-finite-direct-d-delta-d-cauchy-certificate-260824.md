# EXP-001085 — finite direct (D,δD) Cauchy audit

## Scope and reproduction

This claim-nonbearing T-054 package evaluates the direct finite Gibbs
difference

```text
D_sigma(t) = tau_(H+sigma W_L)(t)(A) - tau_H(t)(A),
delta D_sigma = [-beta H, D_sigma]
```

for both signs of `sigma`, with a finite-support configuration character `A`.
The reference state is the full uncut finite Q3 Gibbs state. The cutoff is
applied only in the bond coordinates, and the two-sided Gibbs seminorm is
`Tr(rho X*X)+Tr(rho XX*)`.

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_finite_direct_d_delta_d_cauchy.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_finite_direct_d_delta_d_cauchy_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_finite_direct_d_delta_d_cauchy_verify.py
```

Primary: 45/45. Independent: 45/45. Integrated: 54/54 with Lean R267.

## Findings

The largest finite direct norms are:

| volume | radius | time | sum of two orientation `D_norm` | sum of two orientation `delta_D_norm` |
|---:|---:|---:|---:|---:|
| 2 | 0.5 | 0.05 | 0.00167307 | 0.00392868 |
| 2 | 0.5 | 0.10 | 0.00667525 | 0.01567462 |
| 4 face | 0.5 | 0.05 | 0.00299345 | 0.01300158 |
| 4 face | 0.5 | 0.10 | 0.01187804 | 0.05155844 |

At radius 1.0 and time 0.10 the corresponding sums are 0.00173654 and
0.00410474 for volume 2, versus 0.00310143 and 0.01349134 for volume 4. At
radius 2.0 the coordinate cutoff equals the n=3 coordinate matrix up to
roundoff: the tail norms are below `6e-15` and the direct norms are at the
same numerical floor.

The direct quantities therefore decay with the cutoff in these finite rows,
but the modular derivative grows more strongly with the face volume. This is
evidence for the direct route as a finite interface, not a volume-uniform
estimate.

## Decision and next action

`EXP-001085` advances the direct projected route only at finite Gibbs-member
level. It does not establish a common separating local class, a source/volume/
cutoff/beta-uniform bound, product/core density, exhaustion independence, a
group law, or Hamiltonian-to-OS identification. The next proof obligation is a
structured local test family with a controlled volume comparison; if the
observed `delta_D` growth persists at larger support/cutoff, it must be
registered as a scaling obstruction rather than hidden by the (L=2) zero-tail
row.

## Devil's-advocate review

1. **Reference state:** both lanes use the uncut finite Hamiltonian Gibbs state;
   no local Gibbs replacement is made. **UPHELD.**
2. **Two orientations:** `H+W_L` and `H-W_L` are evaluated separately, and
   their direct norms are not identified by parity. **UPHELD.**
3. **Modular derivative:** `delta D` is computed as the explicit finite Gibbs
   commutator with `-beta H`; it is not inferred from `D`. **UPHELD.**
4. **Cutoff:** the largest-radius row is checked as a zero-tail fixture, while
   smaller radii retain nonzero tails. **UPHELD.**
5. **Volume:** the two-site and square-face rows are finite members only; the
   growth of the face row is reported, not suppressed. **UPHELD.**
6. **Independence:** the second lane reconstructs oscillator, Hamiltonian,
   Gibbs state, cutoff, and unitary evolution without importing primary code.
   **UPHELD.**
7. **Lean:** R267 checks only rational direct-bound and scope fixtures, not
   spectral convergence or a QFT theorem. **UPHELD.**
8. **QFT promotion:** direct finite decay does not close thermodynamic D,δD,
   common alpha, OS/KMS/GNS, gap, continuum, C6, Sector A, or Pre-A. **UPHELD.**

