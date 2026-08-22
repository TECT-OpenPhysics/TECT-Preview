# R-195 - Spatial constant-field lift of the A6 running-mass escape

## 1. Result and scope

EXP-000933 establishes R-195 as a T0, claim-nonbearing spatial lift of the
R-194 local running-mass boundary. The statement is restricted to constant
fields on the finite side-16 torus and to the leading pinned A6 algebra. It is
not a full-field Gibbs theorem.

## 2. Constant-field embedding

Let `T^3_L` be the declared finite torus with volume
`V=Lx*Ly*Lz`, and let
`Psi_(s,r)(x)=sqrt(s)e_1+sqrt(r)e_3` be a constant real field with
`s>0` and `r>=0`. Its pointwise A6 variables are
`|Psi_1|^2+|Psi_2|^2=s` and `|Psi_3|^2=r`, so the integrated running-mass
correction is exactly `V*D(h;s,r)`. No Fourier approximation or one-point
conditional proxy is used in this identity.

For the pinned coefficients, `h_min=9*(a+2*b+c)` and R-194 gives

```text
D(h_min;s,r) = 6*b*s^2/(s+r+eps)
             + 3*c*s^2*(s+r+2*eps)/(s+r+eps)^2.
```

Therefore, for `V>0` and `s>0`,

```text
(V*D(h_min;s,r))/(V*s)
 = 6*b*s/(s+r+eps)
   + 3*c*s*(s+r+2*eps)/(s+r+eps)^2.
```

## 3. Explicit field-space noncoercivity

For `b,c>=0`, `eps>0`, and `r>=s+2*eps`, the exact bound is

```text
D(h_min;s,r)/s <= 6*s*(b+c)/r.
```

Given any `kappa>0`, choose
`r=s+2*eps+6*s*(b+c)/kappa+1`. Then the constant-field ratio is strictly
below `kappa`. Thus no positive volume-uniform coercivity constant can hold
for this running correction even on the constant-field subspace of the
finite torus. The volume factor cancels; increasing the torus volume cannot
repair this escape.

## 4. Cross-check lanes

`verification/lean/Tect/R195.lean` compiles without `sorry`, `admit`, `axiom`,
or `unsafe`. It proves the integrated identity, volume-cancelled ratio, and
explicit `O(1/r)` bound. The primary and non-importing independent Fraction
lanes derive `a,b,c,eps` from the hash-pinned A1 manifest, derive the torus
volume from `Lx,Ly,Lz`, and check the exact witness construction. The
integrated verifier checks hashes, child agreement, Lean markers, hostile
mutations, and the no-overclaim boundary.

## 5. Adversarial review

1. **Volume objection - UPHELD against a missing factor.** The integrated
   correction must be `V*D`; the ratio check proves the volume cancellation
   rather than silently dropping the spatial integral.
2. **Domain objection - UPHELD.** The result uses only constant fields on the
   declared finite torus; it does not identify them with all Gibbs fields.
3. **Uniformity objection - UPHELD.** The explicit `r(kappa)` family rules out
   a positive uniform coercivity constant on that subspace.
4. **Local-to-global objection - UPHELD.** This is not partition-function,
   tightness, rho-floor removal, or infinite-volume control.

## 6. Boundary and next obligation

R-195 strengthens R-194's route boundary but registers no new negative and
closes no gate. A full counterterm route still needs a complete coefficient
trajectory and spatially correlated partition/tightness estimates controlling
all field directions. A6 full-field concentration, A7 self-coupling, A13,
Sector A, Pre-A, physical-empty comparison, and continuum/removal routes
remain open.

No R-195 PDF is issued.
