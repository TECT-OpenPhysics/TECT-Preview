# A1-PRODUCTION-FUNCTIONAL-REALISATION -- full production functional realisation

**Tier**: T3 (TSv2) -- **Lifecycle**: ACTIVE -- **Last review**: 2026-07-17

## Statement

This card freezes a hash-pinned three-component N-001 working branch, its declared energy, executable residual and Hessian, real torus pairing, Class-II floor, and symmetry conventions.  An independent Torch-autodiff and finite-difference audit tests the three variational identities on zero, homogeneous, random, q0-shell, and Class-II-active fields.  It is a computable scaffold and records the present scalar nonlinear factor-two mismatch and the `cJK` versus `cKK` mismatch; it is not a closure claim.

## Scope

N=4 spectral diagnostic grids only, with the external backend and configuration pinned by SHA-256 in [the manifest](production_functional_manifest.json).  The scalar-core control is separate from the full production activation.  The canonical pure-Brazovskii scalar-slice T5 remains unchanged.

## Dependencies and hypotheses

- Hard dependency: A1-PRODUCTION-KERNEL-MANIFEST
- Soft dependency: A1-KERNEL-IDENTITY
- Hypotheses and open gates: none

## Evidence

The frozen [functional record](notes/a1-production-functional-realisation-260717-v1.0.tex.txt), [manifest](production_functional_manifest.json), [independent audit](../../codes/foundations/a1_production_functional_realisation.py), and persisted [JSON result](runs/2026-07-17-variational-audit/result.json).

## Falsifier

The scaffold fails if source hashes drift, the independent autodiff/finite-difference energy control fails, or the known scalar/full-production mismatches are not detected.

## Reproduction

`python codes/foundations/a1_production_functional_realisation.py --output claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/runs/2026-07-17-variational-audit/result.json`

Expected: `P1 AUDIT PASS` means the audit machinery works and detects the currently pinned scalar and full-production mismatches.  It does not mean full variational closure.

## Devil's-advocate

1. **"A finite-difference mismatch is numerical noise."** DISMISSED only when independent autodiff agrees with finite differences at several steps and the imported residual still differs.
2. **"Complex differentiation may hide a factor of two."** DISMISSED only relative to the explicit real pairing; autodiff is converted to that same pairing before comparison.
3. **"This changes the scalar T5 result."** VALID as a scope risk, with mitigation: the existing T5 card certifies the scalar kernel manifest, not this energy/residual pairing; this card cannot expand or downgrade it.
4. **"Failure proves no Class-II completion exists."** VALID with mitigation: it proves only that the pinned pair is not a single verified variational realisation; a repaired convention remains an open next action.

## No-overclaim

No full variational closure, PDE theorem, BCC selection, Hessian stability, or T5/T6/T7 action is asserted.

## Next required action

First align scalar quartic/sextic coefficients with the frozen real-gradient convention; then choose one authoritative Class-II energy/residual convention and repeat this audit across the full test matrix before any scoped T5 review.
