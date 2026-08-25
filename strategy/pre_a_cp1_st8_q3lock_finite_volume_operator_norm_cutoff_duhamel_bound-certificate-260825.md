# EXP-001092 finite-regulator Duhamel certificate

## Decision

At fixed finite spatial volume and finite oscillator dimension, the full-versus-cutoff unitary histories satisfy the operator-norm Duhamel estimate for both signs of the cutoff tail.  The induced bounded-observable difference and its finite Hamiltonian modular companion therefore have explicit bounds.  This advances the finite regulator subgate only; it does not close the unbounded Q3 comparison, a volume/uniform modular-history estimate, common alpha, OS/KMS/GNS identification, a spectral gap, the continuum limit, C6, Sector A, or Pre-A.

## Mathematical statement

Let `H` and `W_L` be self-adjoint finite matrices, let `A` be a bounded unitary character, and define

`U_sigma(t) = exp(-i t (H + sigma W_L)/hbar)` for `sigma = -1,+1` and `U_0(t) = exp(-i t H/hbar)`.

The finite-dimensional Duhamel identity gives

`||U_sigma(t) - U_0(t)|| <= |t| ||W_L|| / hbar`.

For `D_sigma(t) = U_sigma A U_sigma* - U_0 A U_0*`, the two unitary legs give

`||D_sigma(t)|| <= 2 |t| ||A|| ||W_L|| / hbar`.

Using the same finite reference Hamiltonian modular companion `delta_H(D) = -beta [H,D]`,

`||delta_H(D_sigma(t))|| <= 2 beta ||H|| ||D_sigma(t)|| <= 4 beta |t| ||H|| ||A|| ||W_L|| / hbar`.

The same estimates hold for both signs, and the two-orientation sum is at most twice each displayed bound.  At a fixed finite regulator, `||W_L|| -> 0` implies convergence uniformly on bounded time intervals.

## Reproducible evidence

The primary and independently reconstructed calculations each passed 165/165 assertions.  The fixture uses volumes 2, 4, and 6, oscillator dimension 3, beta/hbar 1, times 0.05 and 0.1, and radii 0.5, 1, and 2.  The largest-radius tail norms were approximately `1.38e-15`, `5.39e-15`, and `9.01e-15` for volumes 2, 4, and 6, respectively, below the `1e-8` tolerance.  The corresponding finite reference Hamiltonian norms were approximately `2.45937`, `9.15164`, and `15.95158`.

Run commands:

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_finite_volume_operator_norm_cutoff_duhamel_bound.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_finite_volume_operator_norm_cutoff_duhamel_bound_independent.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_finite_volume_operator_norm_cutoff_duhamel_bound_verify.py
```

The integrated verifier passed 15/15 checks, including primary/independent derived-data agreement and Lean compilation.  Lean entrypoint `verification/lean/Tect/R274.lean` passed the pinned `lake env lean Tect/R274.lean` check and verifies the exact rational factors `3/50`, `3/25`, `42/25`, and the two-orientation doubles `6/25`, `84/25`.

## Adversarial review

1. **Finite matrices versus the actual unbounded Q3 operator.** UPHELD as a boundary: the theorem assumes bounded finite matrices, so the unbounded comparison remains open.
2. **Duhamel sign and factor.** UPHELD: both `sigma=-1` and `sigma=+1` are evaluated, and the one-leg bound is multiplied by two only when passing to `D`.
3. **Modular factor.** UPHELD: the commutator estimate is `2 beta ||H|| ||D||`, producing the explicit factor 4; Lean checks the fixture arithmetic.
4. **Observable boundedness.** UPHELD: the character is unitary by spectral construction, hence its operator norm is one in the finite fixture.
5. **Two orientations.** UPHELD: every volume/radius/time row contains both signs; no orientation is inferred from the other.
6. **Largest-radius zero tail.** UPHELD as finite-spectrum evidence only: radius 2 contains the dimension-3 oscillator spectrum, so it does not establish convergence for a growing oscillator cutoff.
7. **No volume inference.** UPHELD: the Hamiltonian norms grow across the three finite volumes and no uniform estimate is asserted.
8. **Lean scope.** UPHELD: R274 checks exact rational coefficients only; it does not encode matrix exponentials, domains, limits, or reconstruction.
9. **QFT promotion.** UPHELD as an open gate: this package supplies one bounded finite interface in the Q3-to-QFT route, not KMS/OS/GNS or a mass-gap result.

## Scope ledger

Closed here: finite matrix Duhamel identity, finite two-sign operator-norm bound, finite modular companion bound, and fixed-regulator cutoff limit.

Still open: actual unbounded Q3 tail comparison; source/volume-uniform `D` and `delta-D`; modular history; all-shape exhaustion; common alpha; Hamiltonian OS/KMS identification; beta-infinity ground-state selection; broken-sector GNS gap/coercivity; enlarged-counterterm regular continuum; physical-empty-space reference; C6; Sector A; Pre-A.

No claim/result/negative/changelog authority was added by this certificate.  It is an exploration-level, non-claim-bearing checkpoint.
