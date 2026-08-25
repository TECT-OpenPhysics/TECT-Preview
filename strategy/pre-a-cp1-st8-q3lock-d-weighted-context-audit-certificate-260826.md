# Actual Q3 D-weighted context audit certificate

## Scope

EXP-001145 implements the corrected interface identified by EXP-001144 on
the actual finite Q3 histories. It keeps the energy-index orientation of the
source difference instead of replacing the cross terms by an unweighted Gibbs
moment.

## Correct finite inequality

For shifted energies `k_i>=1`, Gibbs probabilities `p_i`, logarithmic mean
`L(p_i,p_j)`, and spectral matrix entries `D_hat_ij`, define

`S=2 sum_ij L(p_i,p_j) ((E_i-E_j)/hbar)^2 |D_hat_ij|^2`.

The arithmetic-mean and square-gap inequalities give

`S <= 2(A+B+C+D)`,

where

`A=sum p_i k_i^2 |D_hat_ij|^2`,
`B=sum p_i k_j^2 |D_hat_ij|^2`,
`C=sum p_j k_i^2 |D_hat_ij|^2`, and
`D=sum p_j k_j^2 |D_hat_ij|^2`.

The cross terms are retained explicitly. EXP-001144 proves that an
unweighted `M2` times operator or Hilbert--Schmidt norm cannot replace them in
general.

## Actual Q3 result

The primary lane passes 88/88 assertions, the independent lane 76/76, the
integrated verifier 13/13, and Lean R315 compiles. The audit covers volumes 2,
4, and 6; beta values 0.5, 1, and 2; radius 0.5; time 0.05; and both cutoff
orientations.

The largest weighted right side is `0.0014187271094517294`. The ratio

`2(A+B+C+D)/(M2 ||D||_operator^2)`

reaches `64.32828297725494` at volume 6 and beta 2, compared with
`2.807699917079624` at volume 2 and beta 0.5. The global finite `M2` values
range from `1.9205583860609077` to `33.286943994754964`, while `Tr(K^2)`
increases from `60.30727720796911` to `46421.121419896044` over the same volume
family. In the audited rows, the cross contexts `B` and `C` dominate `A` and
`D`; this is a finite diagnostic only.

## Adversarial review

1. **Index orientation — UPHELD.** Both lanes compute all four contexts
   directly; the observed `B=C` is not used as an assumption.
2. **Logarithmic mean — UPHELD.** The equal-probability limit and arithmetic
   upper bound are explicit for each finite spectrum.
3. **Energy shift — UPHELD.** The shift enters all contexts and cancels from
   the gap in `S`.
4. **Norm shortcut — UPHELD.** No unweighted norm replacement is used after
   the EXP-001144 correction.
5. **Finite growth — OPEN.** Three volumes and one cutoff/time do not prove
   divergence or a no-go theorem.
6. **QFT promotion — OPEN.** Uniform common-core control, modular transfer,
   exhaustion, common alpha, OS/KMS/GNS, gap, continuum, C6, Sector A and
   Pre-A remain open.

## Next gate

Prove a source/volume/beta-uniform estimate for `B` and `C`, or an equivalent
state-weighted direct `D,delta D` estimate, on the declared common core. If
that estimate fails, identify the precise topology and certify the lower bound;
finite growth alone is not sufficient.

## Non-claims

This certificate does not prove thermodynamic Q3 dynamics, a QFT, a mass gap,
a continuum limit, C6, Sector A, Pre-A, or any Clay statement.
