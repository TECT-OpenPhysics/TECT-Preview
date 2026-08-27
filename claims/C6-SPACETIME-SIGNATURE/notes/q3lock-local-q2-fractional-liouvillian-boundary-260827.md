# q3lock-local-q2-fractional-liouvillian-boundary

## Status

R-366 is a T0, claim-nonbearing finite result under EXP-001208.  It supplies
an interpolation inequality for the doubled bond Liouvillian and a finite
Q3 diagnostic.  It does not close the local-Q2 common-alpha gate.

## Exact finite statement

For a finite Hermitian `B=sum_a lambda_a P_a`, `U_t=exp(-i t B)`, and
`0<theta<=1`, define

```text
|| |ad_B|^theta X ||_HS^2
  = sum_(a,b) |lambda_a-lambda_b|^(2 theta) ||P_a X P_b||_HS^2.
```

The spectral identity and the scalar envelope
`min(2,|y|)<=2^(1-theta)|y|^theta` imply

```text
||U_t^* X U_t-X||_HS
  <= 2^(1-theta)|t|^theta || |ad_B|^theta X ||_HS.
```

The density-state trace estimate follows by Hilbert--Schmidt Cauchy.  At
`theta=1/2`, the right side is a square-function target suitable for a
future local Dirichlet or Kubo--Mori comparison.

## Verification and boundary

Primary and independent lanes each pass `3082/3082` assertions over `768`
contexts (all R-362 prefixes, orientations, signs, adjoints, beta values,
sites and `theta=1/2,3/4,1`).  The integrated lane passes `46/46` and Lean
R366 passes.  The maximum primary/independent numeric difference is
`6.661e-16`; the largest finite-time/fractional-bound ratio is `0.999422`.

This remains an unweighted finite norm.  A source-, cutoff-, volume-,
history- and shape-uniform local modular estimate, common core, common
alpha, OS/KMS/GNS reconstruction, mass gap, continuum, C6, Sector-A and
Pre-A remain open.  No PDF is issued at this intermediate checkpoint.

## Adversarial controls

- The interpolation handles both low and high energy differences and does
  not use an out-of-range Taylor expansion.
- Degenerate bond-energy blocks are retained; zero differences contribute
  zero to the fractional seminorm.
- No commutation of the Gibbs density with the bond is assumed.
- Finite ratios are diagnostic only and are not promoted to uniform
  constants.

## Next gate

Run a larger-cutoff/volume `theta=1/2` stress and seek a local Kubo--Mori or
Dirichlet-form comparison.  If the fractional norm grows, register the
growth as a scoped obstruction and retain R-366 only as a reusable finite
interpolation lemma.

