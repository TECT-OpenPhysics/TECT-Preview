# Q3LOCK submission-preparation checkpoint without prior external review

Date: 2026-09-09. Result context: R-497, T0, claim_bearing=false. Task: T-054.
This is a packaging and bounded internal-review checkpoint, not a new theorem.

## Author instruction and disposition

The author cannot arrange external review and explicitly requests completion
of a submission-preparation package anyway. The requirement to obtain signed
mathematics and specialist literature reviews before producing that package
is superseded. The reviews themselves are NOT PERFORMED, not passed. The
conditional theorem, registered result scope and nonclaims are unchanged.
No actual submission, email, upload, tag or public release is authorized.

Current distribution:
`publish/submission-packages/q3lock/submission-v0138-s1/` and its adjacent
ZIP. The paper register and `submission-distribution.txt` point to this edition.
The original v0.1.38 source and the old q3lock-v0138-r1 review archive remain
byte-preserved. Historical PDF-DEFERRED notices are not the current package
contract. No later A6/A7 project is started by this checkpoint.

## Internal review and content preservation

The complete v0.1.38 manuscript was reread, including all seven proof blocks,
the conditional main theorem, source roles and comparison section. No new
confirmed local mathematical defect was identified. This is an internal AI
assessment, not external acceptance or a guarantee of completeness. Detailed
row-group coverage is in the package's `internal-review.md`.

The submission source changes status/presentation passages only. Exact
comparison after newline normalization preserves the entire model-through-
diagnostic body and the bibliography, not merely selected theorem statements.
The conditional hypotheses and all numerical coefficients are untouched.
No broader anisotropic literature absence, novelty, priority or journal-value
certificate is asserted. The original unsigned A1-A23 questions remain intact.

## Reproduction and PDF checkpoint

`build_q3lock_submission.py` prepares a derived edition using the preserved
review archive's inventoried dependency closure; it validates all original
archive hashes before extracting. It compares the scientific body, builds a
guide, requires hash-bound all-page visual review before sealing, and checks
the delivered archive. Counts and hashes are computed from actual artifacts.

`q3lock_submission_package_audit.py` then extracts the new sealed archive into
another absent directory and runs its actual delivered verifier and integrated
replay. The registered receipt is:
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-09-q3lock-submission-package/result.json`.
It describes the initial successful portable-archive replay. The subsequent
layout-only relocation is rechecked in a separate no-overwrite receipt under
`2026-09-09-q3lock-submission-relocation/` (see the following disposition).

The new ZIP has 349 members: 348 hashed files plus its non-self-hashed manifest.
The research snapshot has 327 files. The extracted integrated replay passes
seven manuscript groups and seven canonical groups, with the independent
finite child passing 306/306 and all 90 protected historical result records
unchanged. These are diagnostic/provenance facts, not infinite-dimensional
mathematical verification. Four actual verifier fixtures reject a fabricated
external signature, a missing file, path escape and altered bytes. Optimized
Python is also refused. Source/coefficient, marker, incomplete-page and stale
PDF mutation checks pass in the builder self-test.

The manuscript was compiled with bundled Tectonic 0.17.0 in untrusted mode.
All 30 manuscript pages and both submission-guide pages were rendered with
Poppler and visually inspected. The final compile has no overfull boxes or
undefined references; retained underfull spacing warnings were visually
checked, including the source table and bibliography. The guide's page break
was adjusted and both final pages reinspected. The hashes, exact page coverage
and compiler identity are in `render-review.json`; automated page geometry
checks remain separate in `pdf-qa.json`.

Read-only integrity and self-tests, from the repository root:

    python -X utf8 verification/scripts/build_q3lock_submission.py --self-test
    python -X utf8 verification/scripts/build_q3lock_submission.py --check
    python -X utf8 verification/scripts/q3lock_fresh_audit_checkpoint.py --label 2026-09-09-q3lock-submission-locator-audit

To independently repeat extraction and hostile tests, choose an ABSENT bounded
scratch directory and a NEW result path, preserving earlier receipts:

    python -X utf8 verification/scripts/q3lock_submission_package_audit.py --work ABSENT_ABSOLUTE_SCRATCH --write-new NEW_RESULT_JSON

The ZIP's root `verify-package.py` uses the standard library; the extracted
research replay uses Python 3.12 and SymPy 1.14.0. CPython 3.12.14 was used for
this final archive test. No TeX, network or Git metadata is required to replay
the finite diagnostic snapshot. No third-party source PDFs are redistributed.

## Devil's-advocate review of both packaging scripts

1. **Changed scientific signs/factors/units hidden by typesetting: DISMISSED
   within the equality check's scope.** The whole scientific region and
   bibliography are compared, and a coefficient mutation is rejected. No new
   scientific quantity is computed by these scripts. This cannot certify the
   unchanged proof's signs, conventions, units or convergence arguments.
2. **Runtime constants or pasted derived counts mask failure: DISMISSED within
   the tests.** File counts, page counts, hashes and replay results come from
   actual inputs. Literal scope fields, edition IDs and rendering tolerances
   are declared tooling inputs, not derived physical data.
3. **Copied archive passes while the delivered artifact cannot run: VALID
   risk, mitigated by the second actual extraction and execution of its own
   verifier and full saved integrated comparison.** Every inventoried file is
   rehashed afterward. This does not prove portability on untested runtimes.
4. **External review silently marked PASS: DISMISSED by the declared scope
   guard and its executed hostile test.** Neither an AI reread nor a finite
   replay is called external peer review. Hashes are integrity evidence, not
   cryptographic author authentication or proof certificates.
5. **Private data or destructive overwrite: DISMISSED within the bounded
   inventory.** Archive paths are validated, private/transient components are
   refused, old artifacts and scratch snapshots are retained, result outputs
   refuse overwrite, and no transmission or Git operation is implemented.
6. **Layout PASS inferred from compilation: DISMISSED for these delivered
   PDFs.** Every actual final page was inspected; geometry checks alone never
   assign the visual verdict. A later modified PDF invalidates the hash-bound
   inspection and requires a new edition.

Independent criticism remains invited. If an analytic gap is found, record
the exact affected statement and downstream consequence, repair at the
research-authority level and issue a new frozen edition. Do not edit hashes
or retroactively sign the previous review table.

## Remaining author and integration decisions

The package is complete for a venue-neutral author-controlled submission
decision. Journal choice and current requirements, metadata, authorship,
originality/overlap, exclusivity, funding/conflicts, licensing and AI disclosure
require truthful author confirmation. They are not missing proof paragraphs
or a requirement to find external reviewers before preparing the package.
Actual transmission remains a separate explicit instruction.

The lane-local release-gated checkpoint and canonical integration/backup are
operationally distinct from the sealed package. The paper lane does not push
or modify the integration controller's checkout. A stale pending integration
base must be reconciled by the controller without overwriting other lanes.

## Recursive PDF guard and distribution relocation

After the sealed archive passed its actual extraction, a live repository
replay exposed a placement conflict: `q3lock_manuscript_content_audit.py`
checks `PAPER.rglob("*.pdf")`, not just top-level PDFs. Consequently the
new nested distribution caused the historical `pdf-deferred` assertion to
fail, although the frozen research snapshot and mathematics were unchanged.

The repair moves the complete sealed directory and ZIP, byte for byte, to
the separate distribution path above. No legacy checker, expected hash or
analytic assertion is weakened. The current builder's destination constant
alone changes. The builder copy inside the sealed package remains its
original provenance copy; it is not advertised as a standalone rebuild
command. Five byte-preserved evidence documents remain at the initial path
for EXP-001688's append-only locators, with an explicit SOURCE-SNAPSHOT-ONLY
notice. The original receipt remains historical. The second receipt tests
the relocated ZIP with the amended current builder. This is a packaging-path
repair, not a mathematical finding or change to the conditional theorem.

The live historical default then correctly detected a source-inventory change:
its content auditor hashes every Markdown file recursively. The two retained
Markdown locator documents enlarge that inventory even without PDFs. Rather
than changing its saved payload, a new no-overwrite current checkpoint is
registered as `2026-09-09-q3lock-submission-locator-audit`. All seven current
manuscript builders replay against it. The final current audit additionally
requires every old source hash unchanged, exactly those two new source paths,
all seven canonical saved payloads, the matrix/independent/finite-form/algebra
saved payloads and preservation of all 90 historical records. It also repeats
the actual relocated archive extraction and diagnostic replay.

Final receipt:
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-09-q3lock-submission-current/result.json`.
This passes both current-repository and extracted-snapshot replays. The
historical integrated default remains an old snapshot comparator and is
expected to report a full-payload source-inventory mismatch on this expanded
checkout; it still passes unchanged inside the delivered research snapshot.
Use the new current package auditor for this checkout, not a rewritten old
expected result. No scientific assertion or historical hash was waived.
