# R-370 Kubo-Mori Liouvillian energy-window certificate

## Result-first boundary

R-370 is a T0, claim-nonbearing finite diagnostic under EXP-001212.  It
splits the R-369 doubled-bond Kubo--Mori theta-half shell by the transition
energy `|lambda_i-lambda_j|`.  The split is exact on the registered matrices,
but it does not close a cutoff-independent low-gap estimate or a Gibbs-tail
theorem.

## 1. New perspective and fixture

This is a Liouvillian-frequency decomposition, not a repeat of the earlier
state-energy spectral-window audit.  For a centered witness with bond-basis
entries `X_ij`, define

`N^2 = 2 sum L_ij |lambda_i-lambda_j| |X_ij|^2`.

For each fixed `E` in `{1,2,4}`, the low-gap part keeps
`|lambda_i-lambda_j| <= E` and the high-gap part keeps the complement.  The
two nonnegative sums therefore satisfy the finite identity
`N^2 = N_low(E)^2 + N_high(E)^2`.  The same finite-time phase envelope is
checked separately on both parts.

The actual-Q3 `V=2` edge uses cutoffs `d=3,4,5,6`, both measured sites and
its bond.  The `V=4` square uses `d=2`, all four measured sites and all four
bonds.  Both beta values, forward/reverse split orders, both time signs,
history adjoints and every prefix position are retained.

## 2. Verification

The primary and non-importing independent lanes each pass `50845/50845`
assertions over `2816` contexts and three transition-energy windows.  The
integrated verifier passes `236/236`; Lean R370 compiles; the largest
primary-independent numeric difference is `4.219e-15`.

The exact decomposition residual is at most `4.441e-16`.  The global R-369
maximum remains `1.208758407679001`.  At the largest edge cutoff `d=6`, the
high-gap component carries at most `0.891744980249774` of the squared norm at
`E=1`, `0.7429364350925435` at `E=2`, and `0.49969239659272124` at `E=4`.
Its norm maxima are respectively `1.1400602287279082`,
`1.0418743270642477`, and `0.8544583112628602`; the corresponding low-gap
maxima are `0.4016958588379324`, `0.6128578748283287`, and
`0.8549841416356769`.  The square has zero high-gap contribution for `E>=2`
and only roundoff (`5.16e-16`) at `E=1`.

## 3. Adversarial review

1. **Not the old state window.**  The mask is on doubled-bond transition
   energy, not on the full local Hamiltonian eigenvalue; the two routes are
   kept distinct.
2. **Exact split versus asymptotic claim.**  The Pythagorean identity is a
   finite sum identity only.  Neither the low part nor the high part is
   declared cutoff-uniform.
3. **High-gap interpretation.**  A large high-gap fraction is a diagnostic of
   where the sampled norm lives, not a proof that a Gibbs tail diverges or
   vanishes.  High-high pairs with small gap are outside this mask's claim.
4. **Bound validity.**  The scalar half-envelope is applied separately to
   each nonnegative masked sum; no cancellation between low and high sectors
   is used.
5. **Independence and formal scope.**  The independent lane reconstructs the
   oscillator, graph, witnesses, spectra and prefixes without importing the
   primary R-370 module.  Lean checks the scalar envelope, split arithmetic
   and scope markers only; numerical spectra remain executable evidence.
6. **QFT promotion.**  Common core, common alpha, global KMS transfer,
   OS/KMS/GNS dynamics, gap, continuum, C6, Sector-A and Pre-A remain open.

## 4. Decision and next gate

The edge data show that the R-369 growth is substantially carried by
high-transition-energy pairs, while the square row is already low-gap at the
declared scale.  This makes a weighted low-frequency collar plus an explicit
high-frequency tail estimate a live analytic route.  The finite split itself
does not supply either estimate.  The next gate is to prove a
cutoff-independent local Dirichlet comparison on the low-gap sector and a
separate Gibbs-tail bound for the complement, then repeat both on
source-complete exhaustion shapes.  No new negative result or PDF is issued.
