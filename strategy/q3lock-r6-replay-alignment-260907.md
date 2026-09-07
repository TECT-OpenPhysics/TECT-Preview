# Q3LOCK R6 replay alignment after readiness-matrix documentation update

Date: 2026-09-07. Exploration: EXP-001625. Task: T-054.
Status: T0, claim_bearing=false, provenance and reader-surface checkpoint only.
The sole Q3LOCK authority remains EXP-000780 -> EXP-000781 -> EXP-000782 / R-497.
No analytic theorem tier, publication status, or PDF status changes.

## Why a new checkpoint was required

The R6 row in `publish/papers/q3lock-phase-coexistence/submission-readiness.md`
was updated from a stale "existing runs" description to the validated
immutable fresh-checkpoint status.  The protected replay guard then correctly
rejected the earlier checkpoint because its source map still contained the old
readiness-document hash.  The old checkpoint and historical replay records
were not overwritten.

## Non-overwriting repair

`verification/scripts/q3lock_fresh_audit_checkpoint.py` now accepts a safe
`--label` and derives the result/source-map pair under the public claim-runs
directory.  The default historical path remains overwrite-protected.  The
current checkpoint is:

`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-q3lock-manuscript-fresh-audit-r6-alignment/`

The paper replay entrypoint now treats `submission-readiness.md` as an
explicit documentation delta, and the package manifest points to the new
non-overwriting integrated replay:

`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-q3lock-paper-readonly-replay-r4/result.json`

The verification README records both the current r4 path and the expanded
documentation-delta list.  The current test selects the immutable r6-alignment
checkpoint and still checks overwrite refusal.

## Recorded checks

The fresh checkpoint validates with seven PASS audit payloads and 1171 total
assertions.  The integrated paper replay passes with seven canonical groups,
seven manuscript groups, nineteen preserved historical records, and 46
non-importing algebra checks.  The replay guard and its six hostile tooling
fixtures pass.  The paper PDF count remains zero.

These are internal provenance and regression results.  They do not certify
the unbounded loop, DLR, infrared, collective, cusp, or source-tangent
arguments; they do not replace independent mathematics or specialist
literature review; and they do not close the content/hash-freeze or final PDF
gates.

## Reproduction commands

```text
E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_fresh_audit_checkpoint.py --label 2026-09-07-q3lock-manuscript-fresh-audit-r6-alignment
E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_paper_replay.py --check
E:/Dev/TECT.venv/Scripts/python.exe -X utf8 -m unittest discover -s verification/tests -p 'test_q3lock_fresh_audit_checkpoint.py' -v
```

## Next gate

Continue the A1--A23 proof audit and external mathematics/literature review.
After any manuscript, source, or accepted documentation change, create a new
immutable checkpoint rather than rewriting a prior result.  Perform the final
content and hash freeze before creating the first paper PDF.
