# EXP-000992 / current R-200 authority revalidation

## Scope

This is a T0, claim-nonbearing append-only freshness revalidation. The
historical R-200 package remains unchanged. This package repins the current
R-193 manifest after the later Lean-registry additions and reruns the same
finite diagnostic.

## Exact witness

For `F=(x^2+y^2)/2`, beta `=1`, and a positive diagonal mobility `M`,

`L_M f = -<M grad F,grad f> + beta^-1 tr(M Hess f)`.

The density proportional to `exp(-beta F)` has the same stationary density and
zero stationary current for
both `M_A=diag(1,1)` and `M_B=diag(2,3)`. The static Hessian and Gibbs
covariance are therefore identical, while the coordinate heat rates are
`(1,1)` and `(2,3)` after assigning `x` to `k` and `y` to `2k`.

## Revalidation result

The current R-193 authority hash is
`ae48ade9d11e3f47955ef4837e26d6cf106d2427570fe886c2eb33b0607d6b43`.
Primary, independent, and integrated lanes derive the same stationary
current cancellation and the same different heat rates, and Lean `R200.lean`
compiles. This repairs only the historical hash mismatch; it does not change
the mathematical scope.

## Adversarial boundary

Same stationary density does not select mobility. The quadratic witness is not
the complete A1 `F_ref`, and different heat rates do not prove that a future
production map cannot exist. The current R-192 first missing
`heat_root_incidence` slot, root filtration/conditional replicas,
`raw-current spatial intertwiner`, and once-owned nonnegative `q`-ledger remain
open. No A13/T-050, Sector-A, Pre-A, physical-empty, continuum,
thermodynamic, KMS/OS, or real-time conclusion follows. No PDF is issued.

## Reproduction

```text
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/a13_fref_r200_current_revalidation.py --no-store
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/a13_fref_r200_current_revalidation_independent.py --no-store
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/a13_fref_r200_current_revalidation_verify.py --no-store
```
