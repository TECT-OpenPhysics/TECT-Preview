# EXP-000965 / finite Gibbs mobility and heat-root non-identifiability

## Status and scope

This is a T0, claim-nonbearing finite witness. It is a QFT-interface audit,
not a production stochastic-quantization theorem. The witness energy
`F=(x^2+y^2)/2` is deliberately separated from the complete hash-pinned A1
`F_ref`; the point is to test what static energy and Gibbs data can identify.

## Exact construction

For a constant positive diagonal mobility `M`, use

`L_M f = -<M grad F,grad f> + beta^-1 tr(M Hess f)`.

The formal adjoint current is
`M(rho grad F + beta^-1 grad rho)`. For
`rho_beta proportional to exp(-beta F)`, `grad rho_beta=-beta rho_beta grad F`,
so the current vanishes pointwise for every such `M`. Thus
`M_A=diag(1,1)` and `M_B=diag(2,3)` have the same stationary density and the
same static Hessian/covariance.

These are different heat rates despite the shared stationary density.

On the coordinate observables, however,
`L_M x=-M_11 x` and `L_M y=-M_22 y`. The two exact rate vectors are therefore
`(1,1)` and `(2,3)`. Assigning `x` to `k` and `y` to `2k` changes the heat
semigroup factors and the root-labelled incidence while leaving the static
Gibbs data unchanged. This is the required counterpair to an automatic
static-to-dynamic identification.

## Verification

The primary and non-importing independent lanes derive all rates from the
registered mobility and Hessian inputs using exact `Fraction` arithmetic.
Lean R200 checks the stationary-current cancellation and the distinct rate
identities. The integrated lane checks source hashes, AST independence,
derived agreement, the eight hostile mutations, and the finite-only boundary.

## Adversarial review

* A reversible Gibbs density selects a unique mobility: UPHELD false; the two
  explicit positive mobilities are a counterpair.
* The witness is the complete A1 functional: UPHELD false; it is explicitly
  only a finite quadratic diagnostic.
* Different rates alone prove the canonical production map is absent: UPHELD
  false; they prove only that static data do not select it.
* Lean algebra implies the A13 estimate: UPHELD false; no q-ledger or reserve
  bound is supplied.

## Boundary and next action

R-192's first missing `heat_root_incidence` slot remains open. A production
owner must provide the mobility, heat/root map, filtration, and raw-current
spatial intertwiner in one hash-pinned cylinder. No A13/T-050, Sector-A,
Pre-A, physical-empty, continuum, thermodynamic, or real-time conclusion
follows. No PDF is issued.

## Reproduction

```text
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/a13_fref_mobility_heat_root_nonidentifiability.py --no-store
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/a13_fref_mobility_heat_root_nonidentifiability_independent.py --no-store
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/a13_fref_mobility_heat_root_nonidentifiability_verify.py --no-store
```
