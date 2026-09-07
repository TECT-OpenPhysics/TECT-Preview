# Read-only replay and historical-output preservation

Date: 2026-09-07. Manuscript v0.1.7, R-497, T0, claim_bearing=false.
Scope: tooling and reproduction instructions, not a new mathematical result.
The sole paper research authority remains EXP-000780 -> EXP-000781 ->
EXP-000782. Independent mathematical and literature acceptance remain OPEN.
No paper PDF, final freeze, submission or claim promotion is supplied here.

## Finding

At checkpoint fb3f2e5c003fcb9e33e8eb2231528d0ccd2fd7e0, the top-level
verification README and package command list still recommended the standalone
q3lock_manuscript_source_audit.py writer. It writes to the already registered
EXP-001611 result.json with os.replace. A read-only build_payload comparison
found differences for README.md, external-review-handoff.md and
literature-qps-addendum.md after the documentation supplements.

Following that stale command would rewrite historical provenance even though
the diagnostics passed. The diagnostic and all historical output files were
preserved during diagnosis. No deliberate overwrite was needed to establish
the behavior: the writer code and the unequal in-memory payload suffice.

## Repair contract

The new q3lock_paper_replay.py entrypoint is read-only by default. It checks
the preserved QPS/source snapshot chain and the frozen R-497 authority before
executing old builders in memory. Canonical payloads must equal their saved
JSON. The entire manuscript payload is compared with the old source checkpoint;
only explicitly listed documentation hash changes or additions are permitted.
All other assertion, manuscript, analytic-source and code differences fail.

The resulting compact checkpoint deduplicates manuscript diagnostic groups,
captures source hashes, and records preserved historical outputs. A reader
checks against that checkpoint without writing it. A stale or missing output
fails; it is never repaired automatically. Assertion-disabled Python is refused.

Explicit --write-new publishes to an absent output only. Same-volume hard-link
publication makes a complete serialized file visible without replacing a
concurrent winner. Unsupported hard-link publication fails without an unsafe
overwrite fallback. No old result or code file is modified.

## Adversarial tooling review

1. Sign/factor mutation: a changed nested assertion cannot pass as a changed
   documentation hash. UPHELD as a rejection test; no new physics arithmetic.
2. Source identity: matching a leaf filename is insufficient; full relative
   paths and current hashes must match the explicit allowance. UPHELD.
3. Missing/null keys: adding or removing a JSON key is not equality merely
   because its value is null. UPHELD as a rejection test.
4. Scope: a tier/claim-bearing or PDF-state promotion is not a tooling change.
   UPHELD; draft scope is checked separately.
5. Output safety: missing, stale and matching reader checkpoints remain
   unwritten; existing write destinations are refused before builder execution.
   UPHELD, including a concurrent publication test.
6. Limit and units: finite checks do not establish infinite-volume or
   unbounded-operator arguments; no new physical number or unit is introduced.
   UPHELD. Counts are read from executed diagnostic payloads, not proof counts.

The standalone guard fixtures are also included in the tooling result JSON.
The separate unittest suite exercises the CLI and actual temporary-file
publication, including simultaneous writers and optimized Python.
External operational review of this preservation contract is invited.

## R1 release-preflight finding and R2 correction

The first tooling checkpoint passed its finite diagnostics and tooling tests,
but repository release preflight rejected its public README example because
the example pointed to a private result filename. That was a documentation
defect, not a passed release gate. R1 result bytes and five changed source
files are preserved under its run directory; source-map.json compares each
raw archive with the original R1 source hash. R2 does not replace that record.

The corrected example uses an explicit output placeholder, not a private
filename. The default reader target now comes from the package manifest
and must resolve to a JSON file within public claim runs. Absolute, parent
traversal and out-of-scope manifest targets are rejected. A missing research
dependency produces a clear nonzero failure with no result write; the tested
shared research environment includes SymPy, whereas the app's minimal bundled
interpreter did not. This is not a successful cross-runtime replay.

R2 checks the R1 archive before and after builder execution and includes
its source map and raw copies in the new fingerprint. The tooling tests
also exercise changed archive hashes, manifest routing, path rejection and
the missing-dependency branch. A tooling PASS still does not close any
mathematical, source-applicability, external-review or publication gate.

## Workspace and release boundary

The first isolated paper checkout lacked four gitignored tmp evidence files
referenced by older, non-Q3 exploration records. Exact-byte copies from the
canonical checkout restored its readiness; no original evidence reference,
expected hash or tracked file was changed. This bootstrap is not proof that
every fresh clone is self-contained. The integration owner was informed so
portable preservation can be addressed in the operational lane.

The new replay needs no private reference PDF, compiler or network. It is not
the outstanding final frozen replay, non-importing mathematical implementation,
or signed review. The phase theorem, nonclaims and manuscript bytes are
unchanged. Source-content review, specialist disposition and final PDF review
remain required before publication readiness can be accepted.
