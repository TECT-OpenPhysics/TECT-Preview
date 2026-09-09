# Q3LOCK submission-preparation package v0.1.38-s1

Package contract: 9 September 2026. The author requested a submission-preparation
package without obtaining external reviewers first. This replaces that
packaging prerequisite, not the evidence standard for a mathematical claim.
Actual journal submission, upload, publication and release tags are not authorized.

Start with `manuscript.pdf` and `submission-guide.pdf`. The adjacent ZIP is the
portable package; it additionally contains the complete bounded research
snapshot needed by the documented diagnostic replay. `manuscript.tex` is
self-contained LaTeX, including its bibliography. No external source PDFs are
redistributed. `submission-cover-letter.txt` is an unsent, editable letter;
`author-confirmations.md` separates the remaining personal and journal choices
from completed package preparation.

## What this edition means

- Scientific content: conditional seven-block Q3LOCK composition, R-497,
  T0, claim_bearing=false. No theorem, tier or sector promotion.
- Internal review: complete-source reread and exact finite/provenance replay;
  details and limitations in `internal-review.md`.
- Independent mathematical review: NOT PERFORMED. Specialist novelty review:
  NOT PERFORMED. Neither is represented as passed or required before this
  package can be prepared.
- Package freeze: identified by `MANIFEST.json`, `build-report.json` and
  `render-review.json`. Their checks cover the delivered bytes, reproducibility
  and layout, not mathematical correctness or editorial acceptance.
- Transmission: NOT AUTHORIZED / NOT PERFORMED. No journal-specific compliance
  is claimed until a journal is selected and its current rules are checked.

## Provenance and reproduction

The research source remains v0.1.38. The preceding review distribution
`q3lock-v0138-r1` and every original audit remain unchanged. This s1 edition
changes presentation/status passages only. The entire model, proofs,
comparison discussion and diagnostic section are compared for equality after
newline normalization; the bibliography is separately compared. Historical
PDF-DEFERRED and signed-review prerequisites inside the snapshot describe its
earlier contract, not this author's later packaging instruction.

After extracting the ZIP into an empty directory:

    python verify-package.py
    cd research-snapshot
    python -X utf8 verification/scripts/q3lock_manuscript_integrated_replay.py --check

The hash verifier uses only the Python standard library. The research replay
uses Python 3.12 and SymPy 1.14.0 (tested versions in `build-report.json`). It
requires no Git metadata, network or TeX runtime. Its independent child is a
separate finite implementation, not an external referee. Never run old
standalone result writers over the frozen research snapshot.

For PDF reconstruction use a TeX installation with the packages listed in
`manuscript.tex`, e.g. `tectonic -X compile --untrusted manuscript.tex`.
The exact tested compiler/hash is recorded in `render-review.json`. Rebuilt
PDF bytes may differ with engines and fonts; the delivered hash identifies
this edition. Re-render any modified PDF. The repository build command is
`python verification/scripts/build_q3lock_submission.py --self-test` followed
by its documented prepare, QA and seal steps in a fresh workspace.
`build-package.py` is a provenance copy of that repository builder, not a
standalone command from the archive root; its preparation mode needs the
previous review archive in a complete repository checkout. The delivered
manuscript's TeX rebuild and the documented extracted diagnostic replay do
not need that older archive.

The package manifest excludes itself and archive receipts to avoid circular
hashing. The sibling `archive-sha256.txt` identifies the ZIP. SHA-256 provides
integrity, not authorship authentication. Keep the original ZIP recoverable.
