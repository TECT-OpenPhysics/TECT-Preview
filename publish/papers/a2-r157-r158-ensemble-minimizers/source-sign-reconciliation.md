# Canonical Class-II sign reconciliation

Status: `OPEN` (2026-09-04).  This document fixes the exact source snapshots,
the two possible Laplacian conventions, and the decision required from the
canonical source owner.  It is a review input, not an erratum or a claim-tier
promotion.

## Scope and source snapshots

The comparison concerns the Class-II part of the explicitly displayed
side-16, six-real-component functional in `manuscript.tex`:

\[
 G_{\rm II}(u,\nabla u)=\frac12\sum_{j=1}^3
       (\partial_j u)^T B(u)(\partial_j u).
\]

The source files are read-only snapshots in the A2 claim card:

| snapshot | relevant display | SHA-256 |
|---|---|---|
| `a2-full-production-wellposedness-260717-v1.1.tex.txt` | indexed component formula with `-B_{\gamma\beta}(u)\Delta u_\beta` | `6c0cd7de1142c742f2f77a1b2cdec179a5b67a8eaaa866bf47ab758373676452` |
| `a2-full-production-wellposedness-260717-v2.0.tex.txt` | schematic `N_{II}(u)=B(u)\nabla^2u+C(u)[\nabla u,\nabla u]` | `e60b1b7640329bae4b5e2a9ac753705e8714921acff22f483d7cc59d0eeb8c34` |

The v2.0 file does not define the symbol `\nabla^2` in or near that display.
The hashes and observations are independently reproduced by
`verification/runs/classii-sign.json` (`8/8`,
`PAPER-CLASSII-SIGN-AUDIT-PASS`).

## Convention-independent variation

For a constant symmetric matrix `B`, periodic integration by parts gives

\[
 D\!\left[\frac12\int |\nabla u|_B^2\right]
       =-B\Delta u,
 \qquad \Delta=\sum_{j=1}^3\partial_j^2,
\]

where `\Delta` is the raw componentwise Laplacian.  For field-dependent `B`,
the same calculation gives

\[
 [N_{II}(u)]_\alpha=
 \frac12\partial_\alpha B_{\beta\gamma}(u)
 \partial_j u_\beta\partial_j u_\gamma
 -\partial_j\!\left(B_{\alpha\gamma}(u)\partial_j u_\gamma\right).
\]

Consequently the principal term is `-B(u)\Delta u`; all remaining terms are
quadratic in first derivatives.  The one-mode test with `|k|^2=1` makes the
sign observable: raw `\Delta` has eigenvalue `-1`, so `-\Delta` pairs with the
mode as `+1`, while `+\Delta` pairs as `-1`.

## Two possible readings of v2.0

1. **Raw-Laplacian reading.**  If `\nabla^2` means the componentwise
   `\Delta`, v2.0 has the opposite sign from the variational derivative and
   requires an authorized correction.
2. **Positive-Laplacian reading.**  If `\nabla^2` is shorthand for
   `\Delta_+:=-\Delta`, then `+B(u)\nabla^2u` is compatible with the raw
   formula.  The canonical note must define this convention explicitly for
   the compatibility to be auditable.

The paper fixes the raw-Laplacian convention and therefore writes
`-B(u)\Delta u`.  It does not silently edit either canonical snapshot.

## Required source-owner disposition

The canonical source owner should return exactly one of the following signed
dispositions:

* `POSITIVE-LAPLACIAN`: v2.0 defines `\nabla^2=-\Delta`; provide the exact
  definition and confirm that no erratum is needed.
* `RAW-LAPLACIAN-ERRATUM`: v2.0 intended the raw componentwise Laplacian;
  authorize a corrected source note with the negative principal sign.
* `UNRESOLVED`: retain the gate and do not promote the integrated paper.

Until a signed disposition and, where necessary, an authorized source update
exist, the A2/R-157/R-158 paper remains `draft` and the source-sign gate is
open.

## Reviewer response template

```text
source_owner: <name and affiliation>
disposition: POSITIVE-LAPLACIAN | RAW-LAPLACIAN-ERRATUM | UNRESOLVED
definition_or_erratum: <exact equation and convention>
source_hashes_checked: <v1.1 hash; v2.0 hash>
date: <YYYY-MM-DD>
signature: <signed response or verifiable review record>
```

This file records no analytic proof closure, novelty decision, operator
approval, physical interpretation, submission, upload, tag, or publication.
