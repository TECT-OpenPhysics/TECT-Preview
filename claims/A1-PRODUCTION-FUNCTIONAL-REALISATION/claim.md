# A1-PRODUCTION-FUNCTIONAL-REALISATION -- full production functional realisation

**Tier**: T3 (TSv2) -- **Lifecycle**: ACTIVE -- **Last review**: 2026-07-17

## Statement

This card separates two objects.  The hash-pinned external working branch fails the variational audit: its scalar nonlinear energy is factor-two inconsistent with the residual and its Class-II energy uses `cKK` while residual uses `cJK`.  The manifest also defines an explicit all-coupling reference functional.  That reference closes the three discrete variational identities on zero, homogeneous, random, q0-shell, and Class-II-active fields; it is not an external-source repair claim.

## Scope

N=4 spectral diagnostic grids only.  The source audit uses the external backend and configuration pinned by SHA-256 in [the manifest](production_functional_manifest.json).  The reference closure applies only to the manifest-defined candidate functional.  The canonical pure-Brazovskii scalar-slice T5 remains unchanged.

## Dependencies and hypotheses

- Hard dependency: A1-PRODUCTION-KERNEL-MANIFEST
- Soft dependency: A1-KERNEL-IDENTITY
- Hypotheses and open gates: none

## Evidence

The source [audit record](notes/a1-production-functional-realisation-260717-v1.0.tex.txt), current [reference-closure record](notes/a1-production-functional-realisation-260717-v1.1.tex.txt), [manifest](production_functional_manifest.json), [independent verifier](../../codes/foundations/a1_production_functional_realisation.py), source [audit JSON](runs/2026-07-17-variational-audit/result.json), and [reference-closure JSON](runs/2026-07-17-reference-functional-closure/result.json).

## Falsifier

The scaffold fails if source hashes drift, the independent autodiff/finite-difference energy control fails, the known source mismatches are not detected, or any reference functional identity fails.

## Reproduction

`python codes/foundations/a1_production_functional_realisation.py --reference-closure --output claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/runs/2026-07-17-variational-audit/result.json --reference-output claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/runs/2026-07-17-reference-functional-closure/result.json`

Expected: source mismatch detected and `REFERENCE-CLOSURE-PASS`.  The latter means only the manifest-defined reference functional closes, not the external production backend.

## Devil's-advocate

1. **"A finite-difference mismatch is numerical noise."** DISMISSED only when independent autodiff agrees with finite differences at several steps and the imported residual still differs.
2. **"Complex differentiation may hide a factor of two."** DISMISSED only relative to the explicit real pairing; autodiff is converted to that same pairing before comparison.
3. **"This changes the scalar T5 result."** VALID as a scope risk, with mitigation: the existing T5 card certifies the scalar kernel manifest, not this energy/residual pairing; this card cannot expand or downgrade it.
4. **"Reference closure repairs production."** UPHELD as an invalid reading: the external source remains hash-pinned and failed; implementing the reference convention is still a separate task.

## No-overclaim

No external production closure, PDE theorem, BCC selection, Hessian stability, or T5/T6/T7 action is asserted.

## Next required action

Implement the manifest-defined reference convention in a separately hash-pinned production backend, then repeat this audit on the full test matrix and larger grids before any scoped T5 review.
