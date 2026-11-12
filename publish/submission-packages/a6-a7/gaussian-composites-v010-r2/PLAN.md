# A6/A7 independent paper plan and acceptance contract

Goal owner: task 019fa909-8f53-7923-8928-879358abc5f3; task ledger T-098.
Source checkpoint: 924d069708066e5c4c40e93fff9c4ce001e4b0f8.
Version 0.1.0; first content checkpoint 2026-11-12.

## Intended deliverable

A standalone mathematical-physics manuscript constructing the canonical
derivative current and the covariance-normal energy for the pinned Gaussian
model, proving their common-regulator convergence, and specifying explicit
stability bounds and obstructions. It includes the full written proofs,
source/hypothesis audit, finite reproducibility and hostile checks, a PDF
reviewed on every page, and a sealed external-review handoff package.
The final checkpoint must be committed, integrated by the current controller,
pushed normally, and verified against the live remote branch head.

## Acceptance matrix

| Requirement | Authority / test | Current disposition |
|---|---|---|
| Fixed Gaussian reference, six-real factor, density floor, regulator quantifiers | manuscript section 2; sources/provenance.json; finite audit | Draft and exact checks available |
| Canonical nonlinear current | full reconstruction and second-level argument in section 3 | Internally reviewed; revised quantifiers |
| Rational coefficient energy convergence | finite tensor IBP plus strong weighted kernel convergence in section 4 | Internally reviewed |
| Explicit stability bounds | sharp lower/upper slopes, subcritical escape, critical noncoercivity, deterministic-background estimate | Internally reviewed; finite checks available |
| Prior-art and dependency audit | dependency-audit.md; exact primary-source locators | Bounded primary-source audit recorded |
| Independent finite routes and hostile mutations | verification/verify.py; fresh legacy replay; saved run JSON | Executed; analytic scope separated |
| Final content lock | proof-audit.md plus source/version hashes | Revised TeX internally reviewed and hash-pinned |
| Final PDF and every-page render review | PDF QA record tied to final TeX/PDF hashes | Seven pages rendered and visually reviewed; PASS |
| External review materials and sealed archive | handoff, cover letter, review form, manifest, extraction check | Materials complete; archive/extraction result in adjacent build report |
| Actual external mathematical / specialist review | signed response from an identified independent reviewer | NOT PERFORMED; never inferred from AI audit |
| Commit, integration, normal push, remote equality | watcher/controller/remote receipts | Pending |

## Ordered work

1. Audit the legacy proof and primary comparators before writing the claims.
2. Write the complete proof for the same Gaussian reference and scope.
3. Reproduce exact conventions and connection families; try hostile variants.
4. Apply separate internal reviews of the current, energy and bibliography.
5. Freeze content, compile, render every page, correct layout and recheck.
6. Package the reviewed PDF, TeX, frozen input snapshot, audits and handoff.
7. Extract into a new directory and run the portable verification command.
8. Regenerate repository readers, release/PDF-check, commit and submit a fixed
   lane checkpoint to the integration owner. Verify the resulting remote head.

## Scope and redesign

No interacting Gibbs measure, A13 closure, physical vacuum, floor removal,
thermodynamic limit or novelty priority is asserted. If a load-bearing proof
gap appears, record it in the exploration ledger and redesign the statement
without relabelling a frozen-background result as the original random-coefficient
target. If specialist review finds the contribution already available in
the literature, reframe as an explicit model application or technical note.

The paper's core remains the random-coefficient energy theorem. Passing only
finite checks or only the deterministic-background lemma is not completion.
External review status and review readiness are separate fields. Any final
completion audit must account explicitly for both.
