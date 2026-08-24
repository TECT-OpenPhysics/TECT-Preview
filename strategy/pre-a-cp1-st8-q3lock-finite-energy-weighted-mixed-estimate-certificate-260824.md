# EXP-001082 / Finite Q3 energy-weighted mixed estimate

## Finding

The actual finite two-site Q3 oscillator matrices admit a corrected
two-sided energy-weighted estimate for the mixed multiplier
`M_L=W_L partial_q B` and momentum `p_1`.  Set

`A = I + H - min(spec(H)) I`,

and use the positive spectral powers of `A` to define

`u_E = ||M_L A^(-3/4)||`,
`v_E = ||Mdot_L A^(-3/4)||`,
`K_+ = ||A^(3/4) p_1 rho^(1/2)||_2`, and
`K_0 = ||A^(3/4) rho^(1/2)||_2`.

The exact finite matrix factorization gives the right-leg estimate

`||M_L p_1 rho^(1/2)||_2 <= u_E K_+`.

Because a truncated oscillator does not satisfy exact CCR, retain

`R_L = p_1 M_L - M_L p_1 + i*hbar*Mdot_L`.

The left leg then obeys

`||p_1 M_L rho^(1/2)||_2 <= u_E K_+ + hbar*v_E*K_0 + r_E*K_0`,

where `r_E=||R_L A^(-3/4)||`.  Therefore

`N_(rho,#)(M_L p_1)^2 <= (u_E K_+)^2 +
 (u_E K_+ + hbar*v_E*K_0 + r_E*K_0)^2`.

The residual-free formula is recovered only when the relevant CCR/domain
transfer proves `R_L=0` (or supplies an equivalent bound).  The finite
commutator derivative `(i/hbar)[p_1,M_L]` independently satisfies the same
residual-free algebraic estimate, but it is not silently identified with the
coordinate derivative `Mdot_L`.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_finite_energy_weighted_mixed_estimate.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_finite_energy_weighted_mixed_estimate_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_finite_energy_weighted_mixed_estimate_verify.py
```

The primary lane passes `87/87`, the independent lane passes `47/47`, and
the integrated lane passes `34/34` with Lean `R264` compiling successfully.
At fixed `L=1`, the energy-weighted multiplier norms for `n=4,6,8,10,12`
are approximately

`7.51206, 16.54081, 28.13984, 42.94394, 61.10019`,

while the corresponding unweighted norms are

`33.26946, 169.78779, 508.62726, 1189.60993, 2381.66869`.

The global shifted-H weight therefore improves the finite constants, but its
weighted constants still grow across this finite cutoff sequence.  The
coordinate-derivative energy norm grows from about `12.34647` to `47.78027`,
and the retained finite-CCR residual norm grows from about `22.73783` to
`174.28868`.  These are diagnostics, not asymptotic lower bounds.

## Adversarial review

1. **Noncommuting weight — UPHELD.**  The factorization uses
   `M A^(-3/4)` and `A^(3/4) p rho^(1/2)` without commuting `A` through
   `M`, `p`, or `rho`.
2. **Truncated CCR — UPHELD.**  The residual `R_L` is explicitly included;
   the residual-free coordinate formula is not claimed for the truncated
   matrices.
3. **Derivative convention — UPHELD.**  The coordinate derivative and the
   finite commutator derivative are both recorded and kept distinct.
4. **Two-sided state — UPHELD.**  Both Gibbs seminorm legs use the same full-H
   Gibbs state, with separate `K_+` and `K_0` factors.
5. **Spectral positivity — UPHELD.**  The shifted weight has spectrum at
   least one, so the fractional powers are defined in every finite row.
6. **Uniformity — UPHELD.**  No volume, source, cutoff, beta, CCR-domain or
   modular-domain uniformity is inferred from five finite oscillator sizes.
7. **Independent reproduction — UPHELD.**  The independent lane reconstructs
   the matrix model and agrees with the primary lane within `1e-7` relative
   tolerance.
8. **Lean scope — UPHELD.**  `R264` proves only exact rational bound fixtures
   and the scope firewall; it does not formalize spectral calculus or QFT
   limits.
9. **QFT promotion — UPHELD.**  Direct `D`/`delta-D` Cauchy, history,
   exhaustion, common alpha, Hamiltonian-to-OS identification, KMS/GNS,
   gap, continuum, C6, Sector A and Pre-A remain open.

## Boundary and next gate

This is a T0, claim-nonbearing finite QFT-facing checkpoint.  It closes the
corrected finite energy-weighted inequality and measures the finite CCR
residual.  It does not close the ideal residual-free Q3 common-core estimate.

The next load-bearing gate is a local source- and volume-uniform control of
`u_E`, `v_E` and the residual/domain transfer on the actual Q3 core.  Only
after that input is proved can the estimate enter the direct projected
`D,delta-D` history argument.  The TECT A1/R-192 production owner remains
separate.
