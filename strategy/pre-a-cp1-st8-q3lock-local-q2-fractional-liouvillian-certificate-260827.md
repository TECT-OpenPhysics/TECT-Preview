# R-366 finite fractional Liouvillian square-function shell bound

## Result-first boundary

R-366 is a T0, claim-nonbearing finite result under EXP-001208.  It
interpolates the R-365 Duhamel estimate with a fractional spectral
Liouvillian norm.  The finite inequality is exact; the modular or
volume-uniform estimate needed for the Q3 common-alpha gate is not proved.

## 1. Fractional spectral statement

Let `B=sum_a lambda_a P_a` be finite Hermitian and let
`U_t=exp(-i t B)`.  For `0 < theta <= 1`, define the block seminorm

```text
|| |ad_B|^theta X ||_HS^2
  = sum_(a,b) |lambda_a-lambda_b|^(2 theta) ||P_a X P_b||_HS^2.
```

The spectral block identity gives

```text
||U_t^* X U_t-X||_HS^2
 = sum_(a,b) |exp(i t(lambda_a-lambda_b))-1|^2 ||P_a X P_b||_HS^2.
```

Since `min(2,|y|) <= 2^(1-theta)|y|^theta`,

```text
||U_t^* X U_t-X||_HS
 <= 2^(1-theta) |t|^theta || |ad_B|^theta X ||_HS.
```

At `theta=1` this is R-365.  At `theta=1/2` the target is a square
function rather than a full first derivative, making a local Dirichlet or
Kubo--Mori estimate a plausible successor target.

## 2. Finite Q3 audit

The primary and non-importing independent lanes reconstruct the R-362
`V=2`, cutoff `3,4` Q3 fixture, both split orders, both time signs, every
prefix, both history adjoints, both beta values and both local sites.  Each
context is checked for `theta=1/2,3/4,1`, the spectral phase identity, the
fractional envelope, the fractional bound and its density-state trace
corollary.  The integrated lane compares all derived fields and compiles
Lean R366.

The audit is diagnostic only.  It does not replace the unweighted norm by a
modular norm, does not provide a local Lieb--Robinson constant, and does not
take a cutoff, volume, source, history or exhaustion limit.

## 3. Adversarial review

1. **Interpolation direction.**  The envelope uses the concavity-compatible
   `min(2,|y|)` interpolation, not an asserted high-frequency Taylor bound.
2. **Zero spectral gaps.**  Zero differences contribute zero to the
   fractional seminorm and are harmless; degenerate blocks are retained.
3. **State ordering.**  The trace corollary is Hilbert--Schmidt Cauchy and
   assumes no commutation of `omega` and `B`.
4. **Finite-to-uniform promotion.**  Finite ratios are not treated as a
   uniform constant; a local modular comparison remains OPEN.
5. **Lean scope.**  Lean checks the scalar `theta=1/2` envelope and scope
   firewall; matrix exponentials and QFT limits remain in the executable
   lanes.
6. **QFT boundary.**  Common core, common alpha, OS/KMS/GNS reconstruction,
   mass gap, continuum, C6, Sector-A and Pre-A remain OPEN.

## 4. Promotion and stop conditions

Promote only after a non-importing proof or exact counterfixture for a
source/cutoff/volume/history-uniform local Kubo--Mori or Dirichlet estimate.
If the fractional norm grows with cutoff or volume, register that growth as
a scoped obstruction and retain the finite interpolation lemma as reusable
only.  No R-366 PDF is issued.

