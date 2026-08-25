# Finite Q3 energy-moment transfer certificate

## Scope

EXP-001143 is a claim-nonbearing finite checkpoint. It tests the energy
moment needed to carry the actual Q3 Kubo-Mori derivative seminorm toward a
common-core/QFT estimate. The finite Hilbert-Schmidt inequality is retained as
the rigorous bridge; the sharper operator-norm expression is labelled an
empirical candidate.

## Finite transfer

For a finite Hamiltonian eigenbasis, let `p_i` be the Gibbs probabilities,
`L(p_i,p_j)` the logarithmic mean, and

`K = H - min(spec(H)) I + I`, so `k_i >= 1`.

With

`S = 2 sum_ij L(p_i,p_j) ((E_i-E_j)/hbar)^2 |D_hat_ij|^2`,

the exact finite inequalities

`L(p_i,p_j) <= (p_i+p_j)/2`

and

`(k_i-k_j)^2 <= 2(k_i^2+k_j^2)`

give the safe finite-dimensional estimate

`S <= 8 Tr(rho K^2) ||D||_HS^2`.

The declared Q3 rows also satisfy the sharper candidate

`S <= 8 Tr(rho K^2) ||D||_operator^2`,

but this checkpoint does not claim that the candidate is a general theorem:
the Gibbs-weighted cross terms require an additional structural argument
before an operator-norm replacement can enter the common-core proof.

## Reproducible result

The primary lane passes 115/115 assertions, the independent eigenbasis lane
passes 103/103, the integrated verifier passes 13/13, and Lean R313 compiles.
There are 18 rows: volumes 2, 4, and 6; beta values 0.5, 1, and 2; radius
0.5; time 0.05; and both cutoff orientations.

Across these rows the shifted Gibbs moment `M2` ranges from
`1.9205583860609077` to `33.286943994754964`. The largest observed
operator-candidate ratio is
`S/(M2 ||D||_operator^2) = 3.4553020779615164`, while the largest safe
Hilbert-Schmidt ratio is `0.38662982758364417`. The minimum square-gap slack
is `4.0` up to floating-point roundoff, and the smallest logarithmic-mean
slack is `-1.554481482245992e-17`.

## Lean cross-check

R313 proves the rational square-gap inequality, the logarithmic-mean
arithmetic transfer, the factor-eight fixture, and positivity after the
declared spectral shift. It does not encode matrix limits, common domains, or
QFT reconstruction.

## Adversarial review

1. **Energy shift — UPHELD.** The shift uses the actual finite spectral
   minimum and a positive constant; all gap differences are unchanged.
2. **Logarithmic mean — UPHELD.** Equal-probability entries use the continuous
   diagonal value, and the arithmetic upper bound is checked on each spectrum.
3. **Norm substitution — UPHELD-OPEN.** The proven finite bridge uses the
   Hilbert-Schmidt norm. The operator-norm candidate is not promoted from row
   agreement because its aggregate cross terms are not controlled in general.
4. **Uniformity — OPEN.** Finite `M2` values do not establish a local,
   volume-, beta-, cutoff-, or exhaustion-uniform common-core estimate.
5. **QFT promotion — OPEN.** Modular-domain transfer, product/core density,
   exhaustion independence, common alpha, OS/KMS/GNS identification, gap,
   continuum, C6, Sector A, and Pre-A remain open.

## Next gate

Establish or refute a source/volume/beta-uniform local `M2` and high-energy
tail estimate for the actual Q3 history on a declared unbounded common core.
If the operator-norm route is required, prove a separate structural estimate
for its Gibbs-weighted cross terms; otherwise carry the Hilbert-Schmidt norm
through the direct Cauchy route and quantify its dimension dependence.

## Non-claims

This certificate does not prove thermodynamic Q3 dynamics, a QFT, a mass gap,
a continuum limit, C6, Sector A, Pre-A, or any Clay statement.
