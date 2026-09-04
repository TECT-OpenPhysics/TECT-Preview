# PAH-OMC-014 legacy sector-weight semantic firewall

## Purpose

This note records a read-only audit of legacy references that contain the words
"sector weights".  It is a semantic exclusion record, not a PAH sector-weight
law and not a model change.  The maintained source remains `E:/Dev/Contents`.

## Required PAH meaning

PAH-OMC-014 needs a source-owned family `w_(n,R,Q)` indexed by finite
refinement `n`, regulator/volume `R`, and PAH charge grade `Q`, with
nonnegativity, normalization over the finite charge grades, a declared
source/beta/phase policy, and a projective cross-Q relation compatible with the
fixed PAH-001 component Gibbs states.  A reference is admissible only if it
provides that typed object or an equivalent full-Q probability kernel.

## Audited legacy references

| Source | SHA-256 | Relevant content | PAH disposition |
|---|---|---|---|
| `E:/Dev/Contents/Github/note/TECT-Math298-GAP1-Hidden-SM-Loop-Coupling-Interpretation.tex.txt` | `29628d1ee25783d172333ce9f14f33fecbf72e8f31dbc41173cf6e83d2b03300` | Theorem 298.1 and Definition `three-sector-matching` use `c_1,c_2,c_3` to weight the U(1)_Y, SU(2)_L and SU(3)_c terms in an empirical one-loop matching residual; the values are extracted by least-squares over `mu` scales. | **Excluded**: these are SM coupling/matching coefficients, not PAH charge-grade weights; the source defines no `Q_n`, no `pi_(rho,Q)`, no PAH cylinder projection, and no cross-Q Gibbs kernel. They are explicitly observation-fitted and cannot satisfy the PAH no-fitting rule. |
| `E:/Dev/Contents/Docs/status/EVIDENCE-INDEX.md` | `318db14462ce618bacc5a4791030ae63d34bd850b7b8d67db227247803ad8c70` | Index prose repeats the Math298 empirical three-sector matching ansatz and its prior/scenario labels. | **Excluded**: status index only; no PAH law or typed probability object. |
| `E:/Dev/Contents/CHANGELOG.md` | `2c8339a23c0e405909b54e30c26fa6ac69528e96da1cef8642f8a6da399e9a31` | Changelog records the same Math298 matching result. | **Excluded**: historical record only; no PAH law or source authorization. |

## Exact search and classification

The read-only search was:

```powershell
rg -n -i --glob '*.json' --glob '*.md' --glob '*.tex' --glob '*.txt' "PAH-OMC-014|full-Q|sector[ -]?weight|w_\s*\(\s*n\s*,\s*R\s*,\s*Q\s*\)|global_normalized_gibbs|projective cross-Q" E:\Dev\Contents
```

The only apparent legacy "sector weights" are the Math298 SM matching
coefficients above.  No source-owned PAH full-Q law was found.  The existing
PAH-OMC-014 source audit remains authoritative for the `HOLD_FOR_EVIDENCE`
verdict.

## Boundary and non-claims

This firewall does not refute the possibility that a future source owner can
supply a correctly typed PAH law.  It only prevents semantic transplantation of
legacy matching coefficients into `w_(n,R,Q)`.  It does not define
`mu_(n,R)` or `omega`, prove projective consistency, supply a Cauchy bound, or
close positivity, normalization, R-488, stationarity, infinite-volume,
continuum, Pre-A, spacetime, QFT, gravity, Yang--Mills, mass-gap or TOE claims.

## Reproduction

Re-run the search command above and compare the three pinned SHA-256 values.
No file under `E:/Dev/Contents` was modified or copied into the TECT source
set by this audit.
