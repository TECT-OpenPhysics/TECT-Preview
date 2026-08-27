# R-373 exact capped-Gibbs-kernel certificate

## Result-first boundary

R-373 is a T0, claim-nonbearing finite checkpoint under EXP-001215.  It
keeps the exact Gibbs difference in the critical theta-half Kubo--Mori shell
instead of replacing it immediately by `p_i+p_j`.  The result is a single
saturating transition kernel that interpolates between a low-gap Dirichlet
form and a high-gap variance cap.  No uniform estimate is claimed.

## 1. Exact kernel

For Gibbs weights `p_i=exp(-beta lambda_i)/Z` and
`Delta=|lambda_i-lambda_j|`,

```text
(2/beta)|p_i-p_j|
  = (p_i+p_j) kappa_beta(Delta),
kappa_beta(Delta) = (2/beta) tanh(beta Delta/2).
```

The elementary envelopes are

```text
0 <= kappa_beta(Delta) <= min(Delta, 2/beta).
```

For a Hermitian witness `X` (or its bond-Gibbs-centered version), the
theta-half shell has the exact pair form

```text
N_(1/2)^2
 = sum_ij (p_i+p_j) kappa_beta(Delta_ij) |X_ij|^2
 = 2 sum_i p_i sum_j kappa_beta(Delta_ij)|X_ij|^2,
```

and hence the capped local form is a valid finite upper bound after replacing
`kappa_beta` by `min(Delta,2/beta)`.  This avoids a false uniform spectral-gap
assumption: low gaps are paid linearly, while high gaps saturate at `2/beta`.

## 2. Verification

Primary and non-importing independent lanes each pass `17001/17001`
assertions over `2816` all-prefix contexts.  The integrated verifier passes
`115/115`; Lean R373 compiles; the largest primary-independent difference is
`1.110e-14`.

The maximum exact-kernel identity error is `2.776e-17`, the cap envelope has
no positive violation, row symmetrization error is `2.221e-16`, and the
capped-bound residual is `4.202e-16`.  The maximum capped shell is
`1.4610968881346746`, with capped row form `1.5463623505129311`.  Edge shell
maxima by cutoff are `0.008029308807322853`, `0.040206939213245196`,
`0.1172316154764435` and `1.4610968881346746` for `d=3,4,5,6`; square
`d=2` values are roundoff-sized.

Reproduce with:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_local_q2_kubo_mori_capped_gibbs_kernel.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_local_q2_kubo_mori_capped_gibbs_kernel_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_local_q2_kubo_mori_capped_gibbs_kernel_verify.py
```

## 3. Lean cross-check

`verification/lean/Tect/R373.lean` proves nonnegativity and both cap bounds,
the scalar Gibbs-kernel equality under its explicit relation hypothesis, the
finite pair cap inequality, row nonnegativity, and the row symmetrization
identity.  It does not formalize `tanh` evaluation, numerical spectra, the
trace passage, a common core, or regulator limits.

## 4. Adversarial review

1. **Gibbs ratio.**  The executable identity uses the same finite Gibbs
   probabilities and doubled-bond eigenvalues; no external spectrum is used.
2. **Diagonal limit.**  At `Delta=0`, `kappa=0`; the logarithmic-mean diagonal
   convention is separate and no zero division occurs.
3. **Envelope direction.**  The cap is an upper bound, not an asserted
   equality; all residuals are checked with one-sided tolerances.
4. **Row symmetry.**  The kernel and matrix-entry square are symmetric, so the
   factor-two row form is checked directly rather than assumed from
   commutation.
5. **Centering.**  Bond-Gibbs scalar centering is applied before the form; it
   changes only zero-gap diagonal entries and leaves the shell unchanged.
6. **Cutoff uniformity.**  The edge shell still grows by two orders of
   magnitude between `d=3` and `d=6`; no uniform capped-form theorem is
   inferred.
7. **Proxy state.**  The finite doubled-bond Gibbs state is not the full
   interacting KMS state or a thermodynamic limit.
8. **Independence.**  The independent lane reconstructs the model through the
   separate R-372 independent helpers and does not import the primary R-373
   module.
9. **QFT promotion.**  Capped-form uniformity, common core, common alpha,
   OS/KMS/GNS dynamics, mass gap, continuum, C6, Sector-A and Pre-A remain
   open.

## 5. Decision and next gate

R-373 supplies the new analytic interface: prove one source/volume/cutoff-
uniform capped Dirichlet estimate, rather than separately proving a uniform
low-gap spectral collar and a uniform high-gap Gibbs tail.  The finite edge
growth keeps that estimate open.  No new negative result or PDF is issued.
