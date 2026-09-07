# Q3LOCK paper verification package

Run from the registered paper worktree, not the canonical integration checkout.
The interpreter below is the shared repository environment; the scripts derive
their source root from their own location, not from that interpreter's path.

    & E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_paper_replay.py --check

The default invocation is also read-only. Its target is selected by the
package manifest's tooling_checkpoint field, confined to public claim runs. It executes the canonical finite
diagnostics, current manuscript checker and non-importing algebra supplement
in memory, compares saved results,
checks the historical output bytes and frozen authority hashes, and compares
the complete new payload with the separate current replay record:

    claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-q3lock-paper-readonly-replay-r7/result.json

The research environment must include the existing symbolic dependencies,
including SymPy. A minimal bundled Python is not an equivalent runtime;
missing dependencies fail without creating or rewriting a result.

No source PDF or network access is needed for this paper-diagnostic command.
It does not compile a PDF, run a release check, or overwrite any result.

## Creating a separate tooling checkpoint

This is an authoring operation, not the reader's reproduction command.
After a reviewed documentation change, replace PATH_TO_NEW_RESULT_JSON with
an absent result path under the public claim runs directory:

    & E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_paper_replay.py --write-new --output PATH_TO_NEW_RESULT_JSON

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

The documentation delta is limited to README.md, external-review-handoff.md,
literature-qps-addendum.md, submission-readiness.md, this README,
package-manifest.json, replay-safety-audit.md and nonimporting-algebra-audit.md. Changes to
assertions, the manuscript, analytic notes, code or other source hashes fail.
The current saved replay additionally pins the resulting document bytes.
The package remains T0, claim_bearing=false, UNFROZEN_CONTENT_REVIEW and
PDF DEFERRED; the entrypoint cannot approve a change to that disposition.

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

## Non-importing algebra supplement and R3 integration

The current R3 record additionally compares every source hash, coefficient
identity and assertion in the separately issued non-importing algebra result.
See nonimporting-algebra-audit.md for its exact scope and standalone command.
It uses only standard-library rational algebra and does not import the
canonical implementation. Same-task authorship is not an independent reviewer.

The R2 checker correctly refused the newly added supplement document under its
closed documentation list. R3 explicitly admits that one document hash and
separately checks the entire algebra payload; it does not waive an assertion,
manuscript or analytic-source change. R2 remains reproducible at its original
fixed commit 0ef6c0d2da2f570755c3e5b645a88170985302a4. Its saved JSON is
preserved, not updated. The integrated current result has nineteen historical
output records to protect. This is still not the final frozen-paper replay.

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
