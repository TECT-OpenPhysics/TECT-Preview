# Energy-moment norm-transfer correction certificate

## Scope

EXP-001144 is an append-only route correction for EXP-001143. The finite Q3
rows from EXP-001143 remain valid numerical diagnostics, but their passing
values cannot be promoted to an unweighted matrix inequality of the form

`S <= 8 Tr(rho K^2) ||D||^2`.

## Exact two-level counterexample

Take

`p_0=100/101`, `p_1=1/101`,

an energy gap of `100`, and the shifted energies `k_0=1`, `k_1=101`. These
probabilities are Gibbs for `beta=log(100)/100`. Let `D=|0><1|`; both its
operator norm and Hilbert--Schmidt norm equal one.

The logarithmic mean is

`L=(99/101)/log(100)=0.21284729558624718...`.

Since `log(100)<5`, `L>99/505`. The shifted Gibbs moment is exactly

`M2=(100/101)1^2+(1/101)101^2=10301/101`.

Therefore

`S=2 L 100^2=4256.9459117249435...`,

whereas

`8 M2 ||D||^2=815.9207920792079...`.

The proposed bound fails for both tested norms, with no norm-conversion issue.
Lean R314 proves the exact rational threshold once the elementary logarithmic
mean lower bound is supplied by the independent numerical lane.

## Corrected interface

The arithmetic-mean and square-gap steps retain only the D-weighted expansion

`S <= 2(A+B+C+D)`,

where

`A=sum p_i k_i^2 |D_ij|^2`,
`B=sum p_i k_j^2 |D_ij|^2`,
`C=sum p_j k_i^2 |D_ij|^2`, and
`D=sum p_j k_j^2 |D_ij|^2`.

For the counterexample the right side is `20404`. The cross terms `B` and
`C` retain the orientation of `D` relative to the Gibbs energy and cannot be
replaced by the unweighted scalar `M2` without an additional structural
theorem. A coarse fallback using the unweighted trace `Tr(K^2)` is finite in
this two-level example but is not volume-uniform and is not the desired QFT
estimate.

## Verification

The primary lane passes 13/13, the independent high-precision Decimal lane
passes 11/11, the integrated verifier passes 12/12, and Lean R314 compiles.

## Adversarial review

1. **Gibbs consistency — UPHELD.** The probability ratio is exactly the
   exponential of the declared beta times the energy gap.
2. **Norm scope — UPHELD.** The rank-one matrix has both norms equal to one.
3. **Logarithmic mean — UPHELD.** The exact numerical value and the strict
   elementary lower bound agree.
4. **Energy shift — UPHELD.** The positive shift is included in `M2` and does
   not alter the gap.
5. **Route boundary — UPHELD-OPEN.** Only the unweighted shortcut is rejected;
   D-weighted contexts and direct two-sided estimates remain viable.
6. **QFT promotion — OPEN.** Common core, modular transfer, exhaustion,
   common alpha, OS/KMS/GNS, gap, continuum, C6, Sector A and Pre-A remain open.

## Next gate

Prove a source/volume/beta-uniform bound for the four D-weighted energy
contexts, or establish a direct two-sided `D,delta D` estimate on the actual
Q3 common core. The unweighted `8 M2` norm shortcut must not be reused.

## Non-claims

This certificate is not a no-go theorem for Q3 dynamics, QFT reconstruction,
mass gap, continuum, C6, Sector A or Pre-A.
