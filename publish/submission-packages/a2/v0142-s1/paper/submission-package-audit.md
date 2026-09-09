# Submission-package audit - 2026-09-09

Scope: v0.1.42 document identity, transport and internal QA only.
External mathematical/specialist review remains NOT PERFORMED. No new
mathematical result, tier, canonical transfer or actual submission is recorded.

## Change boundary

The manuscript changes only the date/version, publication-status paragraphs,
AI-assistance disclosure and conclusion's review-status wording. The new
package checker compares the complete introduction, functional, main results,
proofs and related-work body against committed v0.1.41, plus the complete
limitations section and appendix/bibliography. All compare exactly after
newline decoding. A package-only status edit cannot pass this test if it also
alters those protected mathematical sections.

## Reproduction and presentation

The four current paper audits pass 13/13, 8/8, 24/24 and 50/50; the blank
review-packet checker passes 22/22 and the supplemental re-review passes
34/34. The new submission checker passes 19/19 identity/disclosure checks.
These are counts of executed finite/structural assertions, not counts of
proved analytic propositions. The dated v0.1.41 claim-run records remain
unchanged. The supplemental check now defaults to the paper-local current
run, preventing a later paper replay from replacing that historical claim run.

The manuscript was compiled with bundled Tectonic 0.17.0. Its 18 pages were
rendered at 120 dpi and all nine spreads were visually inspected. The
submission notes were reduced from a three-page draft with an orphan closing
paragraph to two complete pages; both final pages were reinspected. The
main PDF retains two readable underfull bibliography-spacing warnings and
no overfull box was identified. The PDF helper now derives Poppler's filename
padding from the actual page count, covering both short notes and the paper.
Current SHA-256 identities live in the QA/visual records and blank forms.
The final release and clean-source replay are separate executed gates;
historical receipts must not be relabelled as a new run.

## Adversarial tooling review

1. **Wrong identity / hardcode masking. DISMISSED within tooling scope.**
   Current file hashes, byte counts, PDF identities, manifest inputs and
   protected-body equality are computed from bytes. The baseline commit and
   version are declared provenance inputs. A transcribed PDF hash was caught
   by the review-packet test (20/22); the forms were corrected to the actual
   computed PDF hash and the test replayed at 22/22. No source expectation
   or scientific assertion was relaxed.
2. **Silent or simulated external approval. DISMISSED within tooling scope.**
   Both forms retain their blank status, reviewer-name placeholder and
   signature placeholder. The checker rejects a filled-signature fixture.
   Missing review is disclosed, not converted into PASS. Author-only facts
   and actual submission remain separate manual actions.
3. **Missing dependency / wrong source snapshot. MITIGATED.**
   Export requires a successful clean replay of the exact current commit,
   a clean worktree and passing current paper QA. The reproduction archive
   contains the entire committed source to retain all transitive legacy
   registry context. It is deliberately broader than the paper's claim set.
   Python, TeX and Lean caches are environment inputs, not bundled source.
4. **Unsafe or corrupt transport. DISMISSED for checked fixtures.**
   Archive paths reject traversal, absolute/drive paths, private/internal
   entries and Git metadata. Entry inventory, SHA-256, size and ZIP CRC are
   checked after writing. Changed-content fixtures fail. Export is limited
   to this workspace's scratch tree and refuses nonempty destinations.
5. **Overclaim from numerics, units or limits. NOT APPLICABLE as proof.**
   The new checker evaluates no physical quantities, rates, limits or
   convergence. No analytic assumption is discharged. The original
   mathematical audit and independent review questions remain applicable.

External inspection of these checks is welcome; none is presented as an
independent mathematician's opinion. Reproduce from the repository root:

```text
python -X utf8 publish/papers/a2-r157-r158-ensemble-minimizers/verification/submission_package.py --self-test
```

For a final transport build, first run the existing clean-snapshot runner on
the exact committed HEAD and keep its JSON receipt outside tracked source.
Then pass that receipt to `submission_package.py --export <empty-directory-under-tmp> --replay <receipt>`.
Both archives contain a complete transport inventory. The smaller archive
contains the current paper, supplements and final replay receipt; the larger
archive is the complete committed repository source, not additional claims.
