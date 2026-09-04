# Submission-readiness matrix — A2/R-157/R-158

Status: `DRAFT / NOT SUBMISSION-AUTHORIZED` (v0.1.38, 2026-09-04).
This matrix is a decision aid for the finite side-16 classical paper and its
reproduction package.  It is not a referee report, a novelty certificate, a
source-owner response, an operator approval, or a publication record.

## Declared scope

The handoff covers only the explicitly printed three-component complex field,
realified as six components, on the periodic torus `T^3_16`, with the pinned
coefficients, positive density floor, raw componentwise Laplacian convention,
`H^2` evolution domain, and `H^4` linear-operator domain in `manuscript.tex`.
It covers the unconstrained gradient flow (A2/R-157) and the separately
imposed fixed-charge/grand-potential problem (R-158).  It does not cover an
infinite-volume or quantum limit, a derived physical charge, BCC selection, a
physical vacuum, or any TECT cosmological conclusion.

## Requirement matrix

| objective condition | current evidence | status | completion authority still required |
|---|---|---|---|
| Scope and closest prior work | Self-contained functional and spectral data in `manuscript.tex`; bounded primary-source crosswalk including the 2026 Belin--Schneider quasilinear amplitude results (`EXP-001442`); explicit non-subsumption and no-general-method language | `PARTIAL` | Specialist literature/novelty review and any required crosswalk repair |
| Self-contained proof | A2/R-157/R-158 proof text with stable theorem labels; indexed Class-II variation; direct-method and chain-rule dependencies; direct fixed-point, Fourier compactness, and singular-Grönwall reductions; hypothesis map in `theorem-applicability-audit.md`; paper-local structural audit `50/50` | `INTERNAL-READY` | Independent mathematician must complete and sign `independent-proof-review-form.md` |
| Independent/adversarial audit | Exact audits `13/13`, `8/8`, `24/24`, `50/50`; integrated replays A2 `61/61`, R-157 `144/144`, R-158 `155/155`; blank proof and novelty contracts fix itemized hostile tests and signed response fields | `FINITE-AUDIT-PASS` | Signed mathematician proof audit, signed specialist novelty disposition, operator adversarial response, and canonical source-sign disposition |
| Reproducible package | Hash-pinned `verification/runs/reproduction-manifest.json`; bundled commands and source hashes; strict note-PDF check | `PACKAGE-PASS` | Operator-confirmed integrated referee/capstone bundle after external review |
| Manuscript and registration | 16-page v0.1.38 Tectonic PDF with fifteen references, stable main-theorem labels, rendered-page review, `README.md`, `STATUS.md`, `claims-cited.md`, source-sign aid, and two blank signed-review contracts under `publish/papers/` | `DRAFT-REGISTERED` | Actual signed responses, repaired version if needed, and explicit submission authorization |
| Final quality gate | v0.1.38 passes review-packet audit `19/19`, complete finite replay, hash-pinned manifest, 16-page rendered-PDF review, governed regeneration, exploration/time verification, strict PDF validation, and release check at `EXP-001450` after the packet checkpoint `EXP-001449` | `REPOSITORY-PASS` | Operator-side commit/backup confirmation and the dedicated `PUBLISHED` capstone; no public submission is implied |

## Required signed dispositions

The paper must remain `draft` until each applicable response is recorded with
identity, date, toolchain or source hash, evidence locations, and disposition.

1. **Canonical source owner:** choose `POSITIVE-LAPLACIAN`, authorize
   `RAW-LAPLACIAN-ERRATUM`, or return `UNRESOLVED` as specified in
   `source-sign-reconciliation.md` (`EXP-001386` remains open).
2. **Independent mathematician:** answer all eight questions in
   `external-review-handoff.md`; a `PASS` must list hypotheses and exact
   equations, while a `REPAIR` must identify every dependent statement.
3. **Specialist reviewer:** complete the search and decision matrix in
   `specialist-novelty-review-form.md`; no world-first claim may be
   inferred from a clean search.
4. **Operator:** confirm the integrated referee package, source hashes, fresh
   PDF, manifest, and commit/backup state before any `PUBLISHED` marker.

## Current finite evidence

The current package records the following finite-scope evidence only:

- A2 full-production wrapper: `61/61` PASS.
- R-157 integrated replay: `144/144` PASS, including the A2 `61/61` regression.
- R-158 integrated replay: `155/155` PASS, including the R-157/A2 regression.
- Paper-local audits: exact coercivity `13/13`, Class-II sign `8/8`, ensemble
  identity `24/24`, analytic dependencies `50/50`.
- Manifest: `PAPER-REPRODUCTION-MANIFEST-PASS` with package hashes and matching
  manuscript hashes.
- PDF: 16 A4 pages, bundled Tectonic exit 0, changed-page visual review
  (`EXP-001447`; direct-analytic/applicability repair EXP-001446; preceding v0.1.36 governed checkpoint EXP-001445 and proof-text repair EXP-001444 and provenance-only TC-0015; preceding v0.1.35 governed checkpoint EXP-001443 and closest-source boundary EXP-001442; preceding v0.1.34 final checkpoint EXP-001441 and bibliography-layout repair EXP-001440, plus v0.1.33 repository-status synchronization EXP-001439, finite-interval endpoint checkpoint EXP-001437 and temporal-bootstrap checkpoint EXP-001436 and endpoint-constant checkpoint EXP-001435 and endpoint-estimate checkpoint EXP-001432), and strict note-PDF validation PASS.
- Repository: `release_check.py` PASS with only pre-existing large-file
  warnings.

These checks establish finite replay and repository integrity.  They do not
establish an analytic proof, source intent, novelty, operator approval,
physical interpretation, or publication readiness.

## Promotion rules and re-review triggers

Do not change lifecycle or claim tier when a check merely passes again.  Reopen
this matrix and rerun the affected audits after any of the following:

- a canonical source edit, erratum, or changed source hash;
- a reviewer objection to a sign, domain, constant, endpoint estimate,
  compactness passage, equality case, or charge normalization;
- discovery of a closer or subsuming result;
- any manuscript, package, script, artifact, or generated-surface change;
- a failed replay, stale manifest, PDF drift, or release-check failure;
- an operator request for a different commit, backup, tag, upload, or venue.

A `PUBLISHED` or submission marker may be added only after the signed
responses, repaired-and-replayed package, operator capstone, and separate
explicit authorization all exist.  Until then the correct disposition is
`DRAFT / NOT SUBMISSION-AUTHORIZED`.
