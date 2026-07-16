# A1-PRODUCTION-KERNEL-MANIFEST -- canonical N-001 scalar-slice consistency gates

**Tier**: T5 VERIFIED (TSv2) -- **Lifecycle**: ACTIVE -- **Last review**: 2026-07-16

## Statement

The canonical N-001 config stores `(r_zero, mu2_shell, q0, Z, Y, eta_shell)`, three independent tolerances, and the complete seven-key runtime `scalar_slice`.  With those JSON values passed verbatim to the original N-001 `kinetic_coefficients` and `bloch_matrix_linear`, the pure-Brazovskii scalar symbol equals `r_zero + Z|k|^2 + Y|k|^4`; the separate `delta_Z`, `delta_m`, and `delta_r` gates, `Y>0`, `Z<0`, `mu2_shell>0`, `eta_shell=0`, and pinned source hashes all pass.  The legacy template `(r,Z,Y)=(0.35,-1,0.50)` remains a failing mock and is not the canonical config.

## Scope

This is a parameter-consistency and runtime-faithfulness claim for the pure-Brazovskii scalar slice only.  The full anisotropic, locked, shell-biased, or condensate/Hessian operator is excluded.

## Dependencies and hypotheses

- Hard dependencies: A1-KERNEL-IDENTITY, A1-SCALAR-ANALYTIC-BRANCH
- Hypotheses: none -- Open gates: none

## Evidence

Grades: ANALYTIC, EXECUTED, INDEPENDENT-REPRODUCED.  [v1.6 manifest note](notes/a1-production-kernel-manifest-260623-260716-v1.6.tex.txt), [canonical config](canonical_n001_kernel.json), [verifier](../../codes/foundations/a1_kernel_checks.py), the persisted result at `runs/a1_kernel_checks.json`, and the independent operator evidence package at `runs/promotion-evidence/20260716-operator-01/`.

The verifier runs 14 self-tests: schema completeness; original coefficients and runtime symbol; load-bearing scalar-slice settings; three source SHA-256 values; stored-field corruption detection; analytic positivity; non-vacuous `delta_m`; the canonical manifest pass; and legacy mock failure.

## Falsifier

Any required JSON field missing; a scalar-slice setting differing from the stored value; nonzero `eta_shell`; source-hash mismatch; a stored-field edit that breaks a delta; or a failure of `kinetic_coefficients` to reproduce `(r_zero,Z)` invalidates this scoped manifest.

## Reproduction

Status: **INDEPENDENTLY REPRODUCED**.  `python codes/foundations/a1_promotion_evidence.py --mode independent --run-id 20260716-operator-01 --reviewer "Justin"` -> `REPRODUCTION-PASS`; the nested checker reports `A1 kernel checks v1.6.0: 14/14 PASS`.

## Devil's-advocate

1. **"The checker silently chooses runtime settings."** DISMISSED: all seven scalar-slice keys are read from JSON and their reversions are shown load-bearing.
2. **"The vendored code is only a mimic."** DISMISSED: the checker imports the three vendored original N-001 sources and checks their full SHA-256 values against both provenance and config records.
3. **"The scalar slice proves the full production operator."** VALID with mitigation: the card, note, and future T5 scope exclude anisotropic, locked, shell-biased, and condensate/Hessian effects.
4. **"Numerical gates passing is equivalent to unrestricted operator certification."** VALID with mitigation: the independent operator reproduction ratifies the tolerances, config, hashes, and main-proof-line status only for this canonical pure-Brazovskii scalar slice; unrestricted operator, PDE, BCC, T6, and T7 claims remain excluded.

## No-overclaim

The canonical scalar-slice config is T5 only for the constrained N-001 pure-Brazovskii scalar-slice manifest.  No claim is made about the full N-001 operator, PDE behavior, BCC selection, Hessian stability, or a theorem-level A2/A3 implementation.  This is not T6 or T7.

## History

- 2026-06-23 -- A1 split created the manifest card; the legacy solver template was recorded as a failing mock.
- 2026-06-23 -- v1.1--v1.5 successively removed the vacuous gate, stored-field hardcoding, wrong backend, omitted shell-bias term, and incomplete scalar-slice configuration.
- 2026-07-16 -- promotion-package reconciliation: evidence artefact ownership moved to this claim; pre-certification bundle and withdrawn certificate explicitly excluded from T5 evidence.
- 2026-07-16 -- T5 promotion: Justin independently reproduced the 14/14 checker result, ratified the tolerances/config/source hashes, accepted the constrained scalar-slice scope, and recorded main-proof-line status in `runs/promotion-evidence/20260716-operator-01/REVIEW.md`.

## Next required action

Use this T5 claim only within its stated scalar-slice scope.  Any future T6/T7 path must add a separate theorem-level argument and supporting evidence for the excluded operator/PDE/BCC/Hessian components.
