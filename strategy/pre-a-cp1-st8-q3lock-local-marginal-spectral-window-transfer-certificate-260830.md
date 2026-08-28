# R-390 -- Local-marginal spectral-window transfer

## Result

R-390 is a T0, claim-nonbearing finite checkpoint for EXP-001233. It tests a
different order of operations from R-389: first take the partial trace of a
finite-volume Gibbs state to an adjacent local pair, then apply the fixed local
spectral projector. This separates the global volume partition function from
the local spectral complement.

The declared zero-source chain fixture contains 12 admissible `(volume,cutoff)`
systems: volumes `2,3,4,5` with the manifest's rectangular subset of oscillator
dimensions `3,4,5,6`. All adjacent pair supports, beta values
`1/4,1/2,1,2`, local resolvent imaginary value `1`, both local sites and both
adjoint seeds are included. The local windows are `E=1/2,2,4`.

The primary lane passes `3249/3249` assertions and the non-importing
independent lane passes `1950/1950`. The integrated verifier passes `65/65`,
including pinned Lean R390. There are 108 volume/beta/pair rows, 432 duality
seed rows and 1296 projected window rows. The largest full-to-local trace
duality residual is `6.938893903907228e-17` for the target and
`4.440892098500626e-16` for its positive square. Local window masses range
from `0.14660173565938922` to `1.0000000000000004`, and the minimum window rank
is `2`.

Within the finite grid, the maximum volume spread ratio is
`1.1556230972701549` for the projected seminorm and
`1.1553378882734897` for the conditional seminorm, below the declared `1.5`
finite threshold. The cutoff stress is retained rather than hidden: its
maximum projected and conditional spread ratios are
`3.0050241824524666` and `3.3442508882643422`. Thus the local-marginal order
removes the observed global-volume partition penalty on this finite grid, but
it does not remove the cutoff problem.

The hostile replacement of every local marginal by the maximally mixed state is
caught. Its minimum duality residual is `0.0021074932288045467` and its maximum
is `19.617534608077666`, while the correct marginal's maximum residual is
`8.881784197001252e-16`.

## Analytic and QFT boundary

Lean R390 proves the scalar Gibbs-tail term inequality

`exp(-beta*value) <= exp(-(beta-alpha)*energy) * exp(-alpha*value)`

when `0 <= alpha <= beta` and `energy <= value`, together with the mass split
and scalar trace-duality residual identities. The matrix partial traces and
spectral data remain executed finite evidence.

The next analytic step is a boundary-conditioned local Gibbs-tail estimate for
`Q_{U,E} rho_{V,U} Q_{U,E}` and a cutoff-independent invariant form-core
embedding. A volume-stable finite marginal does not imply cutoff or source
uniformity, beta/eta independence, shell summability, Cook/common-alpha
convergence, OS/KMS/GNS reconstruction, a gap, a continuum, C6, Sector-A or
Pre-A closure.

## Adversarial review

1. **Order of reduction:** the primary and independent lanes reduce the global
   Gibbs state before projection; no commutation between a local projector and
   the global state is assumed. UPHELD-FINITE.
2. **Boundary versus interior:** pair positions are labelled as boundary or
   interior and are not pooled into an unlabelled translation theorem.
   UPHELD-FINITE, UNIFORMITY OPEN.
3. **Trace duality:** both the target and its positive square are checked by
   full-state embedding against the reduced state. UPHELD-FINITE.
4. **Window normalization:** projected and conditional seminorms, mass, tail
   and rank are reported separately. UPHELD-FINITE.
5. **Cutoff interpretation:** the finite cutoff spread above `1.5` is retained
   as a stress signal; no cutoff limit is claimed. UPHELD-OPEN.
6. **Hostile mutation:** replacing the reduced state by `I/d^2` is separated by
   a positive probe and fails the declared threshold. UPHELD-FINITE.
7. **Independent reconstruction:** the second lane uses an einsum partial trace
   and rebuilds the oscillator and Hamiltonian without importing the primary
   module. UPHELD-FINITE.
8. **QFT promotion:** Gibbs complement control, common core, source/shape
   uniformity, beta/eta independence, Cook/common-alpha, OS/KMS/GNS, gap,
   continuum, C6, Sector-A and Pre-A remain open. UPHELD-OPEN.

## Reproducibility

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_local_marginal_spectral_window_transfer.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-pre_a_cp1_st8_q3lock_local_marginal_spectral_window_transfer/primary.json
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_local_marginal_spectral_window_transfer_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-pre_a_cp1_st8_q3lock_local_marginal_spectral_window_transfer/independent.json
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_local_marginal_spectral_window_transfer_hostile.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-pre_a_cp1_st8_q3lock_local_marginal_spectral_window_transfer/hostile.json
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_local_marginal_spectral_window_transfer_verify.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-pre_a_cp1_st8_q3lock_local_marginal_spectral_window_transfer/integrated.json
lake env lean Tect/R390.lean
```

