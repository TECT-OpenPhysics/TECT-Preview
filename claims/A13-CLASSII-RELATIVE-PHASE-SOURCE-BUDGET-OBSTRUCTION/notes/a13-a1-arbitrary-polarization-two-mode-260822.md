# R-190 note — arbitrary-polarization A1 two-mode slice

R-190 is a T0 claim-nonbearing Lean cross-check under `EXP-000905`. It
extends the R-189 e3 slice to arbitrary complex internal polarization vectors
for the actual A1 `F_ref` on the side-16 n=1,2 cylinder, while retaining the
positive Class-II quadratic form. The exact lower bound is

`F_ref >= s/16 - 387 s^2/6400 + 27 s^3/800`, `s=||v1||^2+||v2||^2`.

The bound is strictly positive for `s>0` by the Lean factorisation and
negative discriminant. This is only a finite two-mode field-space result.
It does not assemble the complete production cylinder or prove any A13,
T-050, Nelson, measure, Sector-A, Pre-A, physical-empty, or limit theorem.

## Adversarial checks

1. **Convention/sign:** `F_ref`, not `F_decl`, is used; the negative quartic
   is bounded in the adverse direction and the sextic uses Jensen. UPHELD.
2. **Polarization/domain:** the moment identity includes the cross inner
   product and uses only `C^2<=AB`; family/lock and Class-II PSD pieces are
   not silently discarded with a sign reversal. UPHELD.
3. **Coefficient/hardcode:** `r,Z,Y,lambda,gamma`, regularizers, and Machin
   terms are read from the hash-pinned A1 manifest; all reported fractions are
   recomputed by both lanes. UPHELD.
4. **Scope:** arbitrary polarization on two modes is not arbitrary spectrum,
   complete A13 ownership, progressive/revisit control, or a physical claim.
   UPHELD.

The residual action is to use this positive finite slice as a boundary check
while assembling and differentiating the complete A13 production cylinder.
