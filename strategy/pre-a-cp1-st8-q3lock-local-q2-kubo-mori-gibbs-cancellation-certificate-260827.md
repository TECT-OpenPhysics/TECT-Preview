# R-371 critical theta-half Gibbs cancellation certificate

## Result-first boundary

R-371 is a T0, claim-nonbearing finite analytic/executable checkpoint under
EXP-001213.  It identifies the exact cancellation hidden in the R-368/R-370
weight at the critical exponent `theta=1/2` and reduces its finite shell to a
local Gibbs second moment.  The required uniform second-moment estimate is
not proved.

## 1. Exact identity

For a finite bond generator with eigenvalues `lambda_i`, Gibbs weights
`p_i=exp(-beta(lambda_i-lambda_min))/Z`, and logarithmic mean
`L_ij=(p_i-p_j)/(log p_i-log p_j)`, the Gibbs relation gives, including the
diagonal limiting convention,

`L_ij |lambda_i-lambda_j| = |p_i-p_j|/beta`.

Consequently, for a Hermitian centered witness with bond-basis entries `X_ij`,

`N_(1/2)^2 = (2/beta) sum_ij |p_i-p_j| |X_ij|^2`

and the scalar inequality `|p_i-p_j| <= p_i+p_j` yields

`N_(1/2)^2 <= (4/beta) sum_i p_i sum_j |X_ij|^2
            = (4/beta) Tr(rho_bond X^2)`.

This is the analytic bridge: the remaining uniformity input is a local Gibbs
second-moment estimate, not an uncontrolled transition-energy moment.

## 2. Verification

The primary and non-importing independent lanes each pass `14235/14235`
assertions over `2816` all-prefix contexts on the actual-Q3 edge and square
fixtures.  The integrated verifier passes `129/129`; Lean R371 compiles; the
largest primary-independent numeric difference is `2.771e-13`.  The maximum
finite Gibbs identity error is `2.689e-17`, and the second-moment bound has no
positive violation (maximum recorded difference `-3.999999999999958`).

The largest sampled local Gibbs second moment is `42.156906839727924` on the
edge at `d=6`, compared with `2.751158478344597`, `3.43464599148746`, and
`4.704458970507892` at `d=3,4,5`.  The corresponding maximum norm-to-bound
ratio is only `0.008664635287302316`, so the universal bound is deliberately
safe rather than sharp.

## 3. Adversarial review

1. **Diagonal convention.**  Equal bond energies use the finite Gibbs weight
   limit; no zero logarithmic gap is divided.
2. **Sign and absolute value.**  The Gibbs relation is checked with absolute
   transition energy and absolute probability difference, so the orientation
   of the energy ordering cannot change the conclusion.
3. **Second-moment trace.**  The finite matrix identity uses the bond Gibbs
   eigenbasis and the row sum `sum_j |X_ij|^2`; it does not commute the full
   interacting Gibbs state through the witness.
4. **Bound sharpness.**  The pairwise inequality is intentionally one-sided;
   a small norm-to-bound ratio is not interpreted as evidence of saturation.
5. **Cutoff behavior.**  The sampled local second moment jumps at `d=6`; this
   keeps the cutoff/volume uniformity gate open and is not called a divergence
   theorem.
6. **Independence.**  The independent lane reconstructs the oscillator, graph,
   Gibbs weights, spectra, witnesses and prefixes without importing the
   primary R-371 module.
7. **Lean scope.**  Lean proves the scalar cancellation hypothesis, the
   positive pair inequality and finite fixture arithmetic; numerical spectra,
   trace passage, common cores and limits remain executable/open analysis.
8. **QFT promotion.**  Common core, common alpha, global KMS transfer,
   OS/KMS/GNS dynamics, mass gap, continuum, C6, Sector-A and Pre-A remain
   open.

## 4. Decision and next gate

R-371 closes the finite critical-theta algebraic reduction and identifies the
precise analytic target for the direct `D,delta D` route: a source-, volume-
and cutoff-uniform local Gibbs second-moment estimate on a Hamiltonian-derived
common core.  Combine that estimate with the R-370 frequency split, then test
the estimate on source-complete exhaustion shapes before any common-alpha
promotion.  No new negative result or PDF is issued.
