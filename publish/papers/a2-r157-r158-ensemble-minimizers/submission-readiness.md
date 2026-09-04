# Submission-readiness matrix — A2/R-157/R-158

Status: `DRAFT / NOT SUBMISSION-AUTHORIZED` (v0.1.40, 2026-09-04).
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
| Scope and closest prior work | Self-contained functional and spectral data in `manuscript.tex`; bounded primary-source crosswalk including the 2026 Belin--Schneider quasilinear amplitude results, Hilder--Kuehn's rigorous coupled near-instability theorem, and Becker et al.'s coupled dynamical-pattern study; explicit non-subsumption and no-general-method language | `PARTIAL` | Specialist literature/novelty review, citation-chain search, and any required crosswalk repair |
| Self-contained proof | A2/R-157/R-158 proof text with stable theorem labels; indexed Class-II variation; direct-method and chain-rule dependencies; direct fixed-point, Fourier compactness, and singular-Grönwall reductions; hypothesis map in `theorem-applicability-audit.md`; paper-local structural audit `50/50` | `INTERNAL-READY` | Independent mathematician must complete and sign `independent-proof-review-form.md` |
| Independent/adversarial audit | Exact audits `13/13`, `8/8`, `24/24`, `50/50`; integrated replays A2 `61/61`, R-157 `144/144`, R-158 `155/155`; blank proof and novelty contracts fix itemized hostile tests and signed response fields; the canonical source-sign issue is classified as transfer-only | `FINITE-AUDIT-PASS` | Signed mathematician proof audit, signed specialist novelty disposition, and operator adversarial response |
| Reproducible package | Schema-1.1 hash-pinned `verification/runs/reproduction-manifest.json`; fifteen documented commands/input hashes (fourteen nested checks plus the clean-snapshot orchestrator); `14/14` isolated v0.1.40 replay at `EXP-001458`; exact README command-surface match; single-section handoff guard; strict note-PDF check | `PACKAGE-PASS` | Operator-confirmed integrated referee/capstone bundle after external review |
| Manuscript and registration | 17-page v0.1.40 Tectonic PDF with seventeen references, stable main-theorem labels, `README.md`, `STATUS.md`, `claims-cited.md`, transfer-only source-sign aid, and two blank signed-review contracts under `publish/papers/`; full render and pages 14--17 visually inspected at `EXP-001458` | `DRAFT-REGISTERED` | Genuine signed proof and novelty responses, repaired version if needed, and explicit submission authorization |
| Final quality gate | v0.1.40 passes review-packet audit `22/22`, all four paper-local audits, the hash-pinned manifest, a 17-page rendered-PDF review, and the isolated clean replay at `EXP-001458`; the combined shared-tree release check passes at `EXP-001459`; watcher-gated local content commit `7e1de76c06be0d6a43da0459f7ab0b55920a1795` is recorded at `EXP-001460`. | `REPOSITORY-PASS / LOCAL-COMMIT-PASS` | Obtain explicit remote-backup confirmation and create the dedicated `PUBLISHED` capstone after genuine external reviews; no public submission is implied |

## Required signed dispositions for the independent paper

The paper must remain `draft` until each applicable response is recorded with
identity, date, toolchain or source hash, evidence locations, and disposition.

1. **Independent mathematician:** answer all eight questions in
   `external-review-handoff.md`; a `PASS` must list hypotheses and exact
   equations, while a `REPAIR` must identify every dependent statement.
2. **Specialist reviewer:** complete the search and decision matrix in
   `specialist-novelty-review-form.md`; no world-first claim may be
   inferred from a clean search.
3. **Operator:** confirm the integrated referee package, source hashes, fresh
   PDF, manifest, and commit/backup state before any `PUBLISHED` marker.

## Separate transfer-only disposition

The **canonical source owner** must choose `POSITIVE-LAPLACIAN`, authorize
`RAW-LAPLACIAN-ERRATUM`, or return `UNRESOLVED` as specified in
`source-sign-reconciliation.md` before any theorem is transferred to the
canonical TECT/P1 interpretation (`EXP-001386` remains open).  This disposition
is not a premise of the standalone theorem for the explicitly printed
raw-Laplacian functional and is not an independent-paper submission gate.

## Current finite evidence

The current package records the following finite-scope evidence only:

- A2 full-production wrapper: `61/61` PASS.
- R-157 integrated replay: `144/144` PASS, including the A2 `61/61` regression.
- R-158 integrated replay: `155/155` PASS, including the R-157/A2 regression.
- Paper-local audits: exact coercivity `13/13`, Class-II sign `8/8`, ensemble
  identity `24/24`, analytic dependencies `50/50`, review packet `22/22`.
- Manifest: `PAPER-REPRODUCTION-MANIFEST-PASS` with package hashes, matching
  manuscript hashes, fifteen command/input hashes, and README command-surface
  equality.
- PDF: v0.1.40, 17 A4 pages, bundled Tectonic exit 0, full-render contact-sheet review and full-resolution pages 14--17 at `EXP-001458`; preceding v0.1.39 all-page review at `EXP-001452` and changed-page review
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

A `PUBLISHED` or submission marker may be added only after the applicable
paper-review responses, repaired-and-replayed package, operator capstone, and
separate explicit authorization all exist.  Until then the correct disposition
is `DRAFT / NOT SUBMISSION-AUTHORIZED`.  Canonical transfer additionally
requires the separate source-owner disposition above.
