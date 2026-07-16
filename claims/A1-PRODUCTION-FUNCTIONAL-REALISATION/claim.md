# A1-PRODUCTION-FUNCTIONAL-REALISATION -- full production functional realisation

**Tier**: T5 (TSv2) -- **Lifecycle**: ACTIVE -- **Last review**: 2026-07-17

## Statement

This card separates two objects.  The hash-pinned external working branch fails the variational audit: its scalar nonlinear energy is factor-two inconsistent with the residual and its Class-II energy uses `cKK` while the residual uses `cJK`.  Separately, a hash-pinned standalone backend implements the manifest-defined all-coupling functional and, after independent operator reproduction, is closed at T5 for the declared discrete variational matrix only.  This is not an external-source repair claim.

## Scope

**CLOSED@DISCRETE-VARIATIONAL-MATRIX**: discrete spectral torus grids N=4,6,8; zero, homogeneous, random, q0-shell, and Class-II-active fields; finite-difference steps 1e-4, 1e-5, and 1e-6; pinned parameters plus the manifest-declared shell-bias activation.  The source audit applies only to the separately SHA-256-pinned external working branch.  This T5 applies only to the in-repository standalone backend.  The canonical pure-Brazovskii scalar-slice T5 remains separate and unchanged.

## Dependencies and hypotheses

- Hard dependency: A1-PRODUCTION-KERNEL-MANIFEST
- Soft dependency: A1-KERNEL-IDENTITY
- Hypotheses and open gates: none

## Evidence

The source [audit record](notes/a1-production-functional-realisation-260717-v1.0.tex.txt), reference derivation [record](notes/a1-production-functional-realisation-260717-v1.1.tex.txt), T5 [enactment note](notes/a1-production-functional-realisation-260717-v1.3.tex.txt), [manifest](production_functional_manifest.json), [standalone backend](../../codes/foundations/n001_variational_backend.py), [independent verifier](../../codes/foundations/a1_production_backend_verify.py), [multi-grid result](runs/2026-07-17-production-backend-multigrid/result.json), operator [independent reproduction](runs/promotion-evidence/2026-07-17-jusang-independent/promotion-evidence.json), and the [published T5 bundle](bundle/A1-Production-Functional-T5-260717/README.md).

## Falsifier

This T5 record fails if a pinned hash or version drifts, any required grid or field class is omitted, any listed coupling is inactive, any variational/Hessian/symmetry threshold fails, the independently defined scalar reduction ceases to agree, or independent reproduction no longer passes.

## Reproduction

`python codes/foundations/a1_production_backend_verify.py --grids 4 6 8 --output claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/runs/2026-07-17-production-backend-multigrid/result.json`

Expected: `PRODUCTION-BACKEND-MULTIGRID-PASS`, with every assertion marked PASS.  The T5 confirmation record is `runs/promotion-evidence/2026-07-17-jusang-independent/`; future refreshes use [PROMOTION-RUNBOOK.md](PROMOTION-RUNBOOK.md).

## Devil's-advocate

1. **"The Class-II cross coupling is omitted or conflated with the K square."** DISMISSED: `cJJ`, `cJK`, and `cKK` enter distinct quadratic coefficients and the verifier requires all couplings to be nonzero.
2. **"Autodiff makes the checks tautological."** VALID with mitigation: the verifier independently defines energy finite differences, outer residual differences, the real pairing, and the analytic scalar reduction.
3. **"Three small grids prove the continuum functional."** UPHELD as an invalid reading: this is a discrete spectral implementation result with no grid-convergence or continuum theorem.
4. **"This silently validates the historical solver."** UPHELD as an invalid reading: the historical source remains hash-pinned and failed; solver integration is separate.
5. **"The local preflight is an independent T5 reproduction."** UPHELD as an invalid reading: only the operator-named `2026-07-17-jusang-independent` run is the recorded independent reproduction.

## No-overclaim

No external-source repair, historical-solver integration, continuum/PDE theorem, minimizer, BCC selection, stability, T6, or T7 action is asserted.

## Next required action

Use this claim only within `CLOSED@DISCRETE-VARIATIONAL-MATRIX`.  Backend integration into the historical solver, grid convergence, continuum behavior, and physical vacuum selection require separate claims.
