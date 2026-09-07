# Q3LOCK Simon Feynman--Kac provisional source capture

**Date:** 2026-09-07 UTC  
**Exploration:** EXP-001638  
**Task:** T-054  
**Status:** T0, claim_bearing=false, provisional provenance diagnostic  
**Authority boundary:** EXP-000780 -> EXP-000781 -> EXP-000782 / R-497

## 1. Purpose

The manuscript cites B. Simon, *A Feynman-Kac Formula for Unbounded
Semigroups*, arXiv:math-ph/9907022v1 for the finite-dimensional
Feynman--Kac input.  The citation was present in the manuscript crosswalk but
was not included in the older R-497 byte manifest.  This note records one
fresh raw-byte capture so the missing provenance is explicit before the final
source freeze.

This is not a theorem-application acceptance, a claim-card promotion, or a
replacement for the older R-497 manifest.  The captured PDF was held only in
a temporary directory and is not committed.

## 2. Captured identity

| field | value |
|---|---|
| source | B. Simon, *A Feynman-Kac Formula for Unbounded Semigroups* |
| URL | `https://arxiv.org/pdf/math-ph/9907022v1` |
| locator | Theorem 1.1 and equations (1.1)--(1.3), printed page 2 |
| raw byte length | `110277` |
| raw SHA-256 | `15ef936d49d5dd06333a0987fcf609c516048db3b330d37cff62c14bf7e063ff` |
| retrieval | 2026-09-07 UTC, Python standard-library HTTPS download |

The digest is over the raw PDF bytes; no newline or text normalisation was
applied.  The leading bytes were `%PDF-`.  The companion result is
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-q3lock-simon-source-capture/result.json`.

## 3. Reproduction

The source PDF remains external.  A reviewer with a local copy can reproduce
the byte and mutation checks without changing the repository:

```powershell
& E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_simon_source_capture.py `
  --source C:/path/to/simon-math-ph-9907022v1.pdf `
  --expected-sha256 15ef936d49d5dd06333a0987fcf609c516048db3b330d37cff62c14bf7e063ff `
  --expected-bytes 110277 `
  --retrieval-date 2026-09-07 `
  --self-test
```

The same script accepts the version-pinned URL through `--url`; `--source` is
preferred for a trust-managed local download.  An output path may be supplied
only for a new result because the verifier refuses to overwrite an existing
JSON artifact.

## 4. Scope and non-claims

The captured source is used only for the finite-dimensional Brownian-bridge
identity and the mass-one coordinate scaling described in the source ledger.
It does not establish the harmonic split, monotone-form convergence, mesh
limit, pressure limit, DLR compactness, FKG, infrared bound, strict cusp, or
phase multiplicity.  Those interfaces remain conditional in the theorem-
applicability audit and require independent mathematical acceptance.

The one-byte hostile mutation in the companion run changes the digest and is
rejected.  This is an omission-control check, not mathematical evidence.

## 5. Remaining gate

The final source freeze must capture all cited primary sources together, record
their retrieval conditions, and be reviewed against the manuscript and the
historical R-497 manifest without rewriting that historical record.  Until
then this note advances provenance only; it does not close the signed
literature review, content freeze, hash freeze, external proof audit, or final
PDF gate.
