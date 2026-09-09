# Q3LOCK paper verification package

The current v0.1.38 source-only delimiter regression can be run without
compiling a PDF:

    & E:/Dev/TECT.venv/Scripts/python.exe -X utf8 -m unittest discover -s verification/tests -p test_q3lock_manuscript_math_delimiters.py -v

Its lexical coverage is limited to the supported math delimiters and the
two reported bare-infinity faults. It is not a TeX engine or layout audit.
The bounded remaining-block review is recorded in
strategy/q3lock-remaining-blocks-and-source-review-260908.md (EXP-001685).

Run from the registered paper worktree, not the canonical integration checkout.
The interpreter below is the shared repository environment; the scripts derive
their source root from their own location, not from that interpreter's path.

    & E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_manuscript_integrated_replay.py --check

The default invocation is also read-only. Its script-level default and the
package manifest's tooling_checkpoint identify the same current public claim run. It executes the seven current manuscript auditors, canonical finite diagnostics,
A1-A23 packet validator, EXP-000782 independent replay and finite form audit in
memory, compares the saved source-review-v1 and source-review-v1 checkpoints, and checks historical output
bytes. The integrated result is:

    claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-q3lock-paper-integrated-replay-source-review-v1/result.json

The research environment must include the existing symbolic dependencies,
including SymPy. The interpreter location is not a dependency guarantee;
missing dependencies fail without creating or rewriting a result. Replay
portability is tested on the named installed runtimes, not every Python/OS.

No source PDF or network access is needed for this paper-diagnostic command.
It does not compile a PDF, run a release check, or overwrite any result.
EXP-001652 rechecks the primary FSS Section 2 theorem at the finite mesh;
its disposition remains conditional and does not change the following
comparison-only boundary. The EXP-001645 literature boundary is recorded
as comparison-only: FSS
Theorem 3.3 concerns a classical finite-dimensional lattice gas and does not
replace the Q3LOCK loop/DLR/cusp proof obligations. EXP-001646 records the
exact KP general-vector finite-range crosswalk and keeps only fixed-source
Theorem 3.1 as an imported conclusion.

EXP-001657 rechecks the KP source-window topology, finite-M-before-Holder order, compact-boundary source continuity, and the two-stage source-to-zero DLR limit. It finds no new local defect, but signed DLR applicability review and PDF deferral remain open.

EXP-001658 records a current finite-fixture refresh for the A1-A5 pressure and
even-tiling diagnostics. The saved outputs are
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-q3lock-pressure-seam-minmax-audit-r2-current-v016/result.json`
(64/64) and
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-q3lock-fekete-convex-equicontinuity-audit-r2-current-v016/result.json`
(69/69). They refresh finite arithmetic only; A1-A5 analytic acceptance and signed review remain open.

EXP-001662 records a model-side KP envelope and finite-range weight audit. Run
it read-only with:

    & E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_kp_envelope_audit.py --check

The saved result contains 168 exact/derived checks and four hostile
substitution rejections. It supports the internal A6 formula map only; it does
not reprove KP, close the DLR source window, or generate a PDF.

EXP-001663 records a primary-source literature boundary for the closest
asymmetric quantum-crystal theorem. It confirms that Kargol--Kozitsky
Theorem 1.4 is scalar and therefore is not a direct import for the non-radial
positive-lambda R^8 Q3LOCK result. This is comparison-only evidence; it does
not certify novelty, theorem applicability, or a PDF.

EXP-001664 records the primary Kargol--Kondratiev--Kozitsky separation between
the symmetry-free multiplicity definition, the rotation-invariant vector phase
route and the scalar asymmetric route. It is comparison-only and does not
certify an anisotropic Q3LOCK phase theorem, novelty, or a PDF.

EXP-001665 records the bounded R-497 claim/result-lineage decision. The result
remains a standalone T0 registration; no duplicate Sector A--F claim card is
created, C6 is routing metadata only, and the PDF remains deferred pending
external review and content freeze.
EXP-001668 records the extended primary-source comparison boundary. It keeps
general-vector Euclidean-DLR results as infrastructure only and the checked
phase-transition results as scalar or radial; it does not certify an
anisotropic Q3LOCK theorem, novelty or priority, and it does not generate a
PDF.

EXP-001673 records the primary Kozitsky--Pasurek split between general-vector
Euclidean-DLR infrastructure and the separately stated `nu=1`, attractive
FKG/low-temperature phase route. It is comparison-only and does not certify an
anisotropic Q3LOCK theorem, novelty or priority.

EXP-001674 records the collective Jensen precision repair. The manuscript uses
the second derivative at the (t=0) translation minimum, not a global
convexity assertion. It remains an internal T0 repair and does not sign A14--A17
or generate a PDF.

EXP-001675 makes the beta-scaled Cauchy--Schwarz step in the DLR boundary
coercivity estimate explicit and records a bounded A1--A9 reread with no new
local defect. It remains an internal T0 proof-text clarification; A1--A9 and
the later rows still require signed review and no PDF is generated.

EXP-001676 records earlier radial/isotropic vector normal-fluctuation and
quantum-stabilization comparators by Kozitsky. This comparison-only record
does not import a phase theorem, establish absence or novelty, or generate a
PDF; specialist literature review remains open.

EXP-001678 adds the bounded Faris--Minlos/Froehlich--Lieb primary-source supplement; it is comparison-only and does not generate a PDF.

EXP-001679 rechecks the KKK radial/rotation-invariant vector threshold and scalar
asymmetric boundary. It is comparison-only, leaves A20 and specialist review open,
and does not generate a PDF.

EXP-001680 adds the finite-volume positive spectral form-trace lemma for the collective Jensen block. It is a proof-text repair only, leaves A14--A17 and signed review open, and does not generate a PDF.

EXP-001669 records a separate finite collective/Falk--Bruch load-bearing
audit. Run it read-only with:

    & E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_collective_block_audit.py

The saved output has 93 finite assertions. It checks the normalized
translation curvature, Q3 graph factor, clipping envelope, threshold
cancellation and finite spectral factors only; it does not sign A14--A17,
close a thermodynamic limit, or generate a PDF.

## Creating a separate tooling checkpoint

This is an authoring operation, not the reader's reproduction command.
After a reviewed content repair, first create a fresh manuscript checkpoint and
then replace PATH_TO_NEW_RESULT_JSON with an absent result path under the public
claim runs directory:

    & E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_manuscript_integrated_replay.py --write-new --output PATH_TO_NEW_RESULT_JSON

The writer serializes to a temporary file on the same volume and publishes it
with an atomic, no-replace hard link. An existing destination, including a
concurrent winner, is refused. There is no overwrite option or fallback.
A changed saved result must be investigated, not replaced to obtain PASS.

For ordinary verification, omit --write-new. A missing checkpoint is a failure,
not permission to create one. Historical writers must not be invoked on this
revised draft; they are retained unchanged for their original snapshots.

## Coverage and historical results

The current entrypoint calls build_payload() only, never a historical main().
All counts describe finite diagnostics, including structural/provenance checks;
they must not be added up and called independent theorem proofs.

| Canonical builder | Existing diagnostic count |
|---|---:|
| q3lock_absolute_partition_audit.py | 120 |
| q3lock_thermodynamic_pressure_audit.py | 55 |
| q3lock_dlr_tangent_content_audit.py | 70 |
| q3lock_fkg_content_audit.py | 504 |
| q3lock_reflection_infrared_content_audit.py | 90 |
| q3lock_collective_falk_bruch_content_audit.py | 40 |
| q3lock_strict_cusp_tangent_content_audit.py | 42 |

The manuscript chain is replayed from q3lock_manuscript_source_audit.py through
its six predecessors. Its seven groups retain the registered counts: source
34, composition 59, collective 150, infrared 612, DLR 81, loop 203 and content
32. Their original JSON files remain historical and byte-preserved.

The external-review handoff also includes the complete A1--A23 review matrix
and its hostile-coverage validator. The integrated command above calls this
validator's build_payload() in memory and compares its frozen result. Do not
invoke its historical standalone writer on the current manuscript.

Its result is a packet-coverage diagnostic, not an independent proof review or
theorem certificate.

The current package-level independent replay is separate from the integrated
replay. Run the current source-review-v1 checkpoint read-only with:

    & E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_independent_replay.py --check --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-q3lock-independent-replay-source-review-v1/result.json

The replay runs the EXP-000782 standard-library independent verifier in a
temporary output directory, compares the complete payload with its frozen
306-assertion result, checks current manuscript scope and PDF deferral, and
rejects hostile forbidden-import, claim-promotion, and assertion-mutation
fixtures. The source-review-v1 result records the current manuscript/package-source confirmation after the KP envelope, scalar-boundary, lineage, FKG cone-text, vector/phase-scope, collective-Jensen and A1-A9 coercivity audits;
r1 through r19 results remain immutable history. It is reproducibility evidence,
not a signed mathematical review.

The finite form checkpoint is a separate algebra/provenance
diagnostic at `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-q3lock-finite-form-closure-audit-source-review-v1/result.json`. It tests the declared finite envelopes and truncation direction after the FKG cone-text, vector/phase-scope, collective-Jensen and A1-A9 coercivity audits; it does not certify the closed-form, semigroup or infinite-volume passage.

The non-importing algebra checkpoint is
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-q3lock-nonimporting-algebra-source-review-v1/result.json`.
It checks the exact coefficient identities and package-source hashes without
importing the independent implementation; it remains a finite diagnostic and
does not certify the analytic passage or any proof row.

The older r10 paper replay remains a historical reader and intentionally rejects
manuscript/analytic changes. The current kp-vector-phase-scope integrated replay is the explicit
repair lane and admits only the named current checkpoints; it still cannot admit
a theorem or PDF. The package remains T0, claim_bearing=false,
UNFROZEN_CONTENT_REVIEW and PDF DEFERRED; the entrypoint cannot approve a change
to that disposition.

The first tooling checkpoint (EXP-001614) is retained as a pre-release
snapshot. Its source-map.json and raw source copies preserve the five files
changed during release-preflight correction; the R2 checker validates those
copies against the original result hashes. R1 is not the current reader target.

The EXP-001612 QPS and EXP-001613 DFFR source snapshots are historical comparison
audits. Their original standalone commands require their original checkout
(e.g. fb3f2e5c003fcb9e33e8eb2231528d0ccd2fd7e0 for EXP-001613).
Do not run those writers on this revised package. The current entrypoint checks
their preserved identities but does not rerun the separate harmonic-comparison
fixtures or certify the manually inspected source pages.

## Non-importing algebra supplement and current refresh

The current kp-vector-phase-scope package also consumes the separately issued non-importing
algebra result. It compares every source hash, coefficient identity and
assertion in the current v019 payload. See nonimporting-algebra-audit.md for its
exact scope and standalone command. The checker uses only standard-library
rational algebra and does not import the canonical implementation. Same-task
authorship is not an independent reviewer.

## A1--A23 locator provenance

The package also contains a read-only locator audit for the external-review
matrix.

It also contains a read-only objective-coverage audit for the complete requested
artifact chain; run `verification/scripts/q3lock_completion_gate_audit.py --check`
after the current v061 replay inputs exist. This audit intentionally cannot
promote R-497, close A1--A23 or generate a PDF. Run:

    & E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_review_locator_audit.py --check

The current result resolves all 23 rows and 57 manuscript locators, and rejects
missing-row, duplicate-row and missing-label mutations. It checks handoff
provenance only; it does not sign a proof row or replace the required reviewer
response.

The original R2-era algebra result, the first current-manuscript refresh and
the earlier locator refreshes remain byte-preserved historical records. The r19
result is a new no-overwrite checkpoint after the exploration, package and
reader-document sync; it does not waive an assertion, manuscript or
analytic-source change. The integrated current result records its protected
historical output count in the JSON payload; this count is intentionally not
duplicated as a mutable prose constant. The objective-coverage audit is a
separate T0 readiness check and reports INCOMPLETE_EXTERNAL_REVIEW_AND_FREEZE.

## Tooling tests and remaining scientific review

    & E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_paper_replay.py --self-test
    & E:/Dev/TECT.venv/Scripts/python.exe -X utf8 -m unittest discover -s verification/tests -p test_q3lock_paper_replay.py -v

The tests attack changed assertions, unlisted hashes, missing/null-key changes,
scope promotion, optimized Python, read-only CLI behavior, overwrite attempts
and concurrent publication. See replay-safety-audit.md for the evidence boundary.

This is internal integrated replay, not the required independent mathematical
or literature signature, a new non-importing mathematical implementation, or
the final clean frozen-tree replay. No script proves infinite-dimensional
Feynman--Kac passage, thermodynamic compactness, a DLR phase, a source cusp,
theorem applicability or novelty. The canonical content and manuscript
arguments remain subject to the explicit proof-audit obligations.

## Frozen replay protocol

After the remaining source/content review and any repairs, freeze a clean
tracked snapshot and run the required primary, independent and integrated
lanes. Fill the final release manifest with fresh source and output hashes
only then. These dated tooling fingerprints do not freeze the paper.
Only after the final content gate may its first PDF be compiled and visually
inspected. Canonical integration and push belong to the integration controller.

## EXP-001681 literature boundary

The package now includes
strategy/q3lock-targeted-literature-recheck-260908.md.  Its inspected
primary records are comparison-only and add no theorem import.  The bounded
search is not an absence or novelty certificate; later anisotropic literature
and signed specialist review remain open.  The package remains T0,
claim-non-bearing, content-unfrozen, and PDF-deferred.

EXP-001682 records a provisional byte capture of Simon arXiv:math-ph/9907022v1
(110277 bytes, SHA-256
`15ef936d49d5dd06333a0987fcf609c516048db3b330d37cff62c14bf7e063ff`). It
confirms the Theorem 1.1 source role but does not replace signed theorem
applicability review or final hash freeze. No PDF is generated by this reader.

## EXP-001683 Schneider--Beck--Stoll source audit

The package includes `strategy/q3lock-schneider-beck-stoll-source-audit-260908.md`
and its registered EXP-001683 record. The eight-page publisher PDF was captured
at 516155 bytes with SHA-256
`4063397ab5af4502b69f2f030192fbd98b5ecc0ffb115b481dccee2ae2f0793c`. Its radial
model, explicit n=1,2,infinity inequality range, and displacive/large-n
conclusion boundary are comparison-only and do not replace signed applicability
review. The source-access gap is resolved, but final recapture remains required
at content/hash freeze. No PDF is generated by this reader.

Current no-overwrite family: fresh source-review-v1, integrated source-review-v1, independent source-review-v1,
finite-form source-review-v1, algebra source-review-v1, locator source-review-v1 and completion-gate source-review-v1.

## Portability repair and test boundary

The independent replay now records the manuscript locator relative to the
repository and keeps producer_environment outside the deterministic replay.
The complete scientific replay is still compared exactly; there is no field
filter, hash substitution, float tolerance, or historical-result overwrite.
The integrated checker also hashes the complete stored independent envelope,
so its original producer metadata remains byte-pinned provenance. Separately
generated envelopes on different hosts need not be byte-identical.

Run the relocated-copy and hostile-mutation tests with:

    & E:/Dev/TECT.venv/Scripts/python.exe -X utf8 -m unittest discover -s verification/tests -p test_q3lock_independent_replay_portability.py -v

The test copies the independent dependency closure byte for byte into a
temporary path with spaces and a non-ASCII character and executes that copy.
This is not the final clean tracked-snapshot replay or an external signature.
See strategy/q3lock-replay-portability-and-bounded-review-260908.md for the
diagnosis, tested runtime versions, adversarial review, and scope limits.

\n
