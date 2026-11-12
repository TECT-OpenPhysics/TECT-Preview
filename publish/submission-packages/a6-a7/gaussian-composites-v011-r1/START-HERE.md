# Review distribution: start here

The seven-page manuscript.pdf and its TeX source are the main deliverables.
The fixed model, current/energy limit proofs and explicit stability boundaries
are printed in the manuscript. dependency-audit.md and proof-audit.md explain
the source crosswalk and corrections. PLAN.md tracks the full acceptance scope.

External mathematical and specialist novelty reviews are NOT PERFORMED.
The package is prepared for such a review; no signature or acceptance is implied.
Use external-review-handoff.md and the blank independent-review-form.md.
The venue-neutral cover-letter.md is unsent.
external-review-plan.md identifies potential specialist readers and the
evidence required for actual review. review-request-drafts.md contains unsent
targeted invitations; transmission requires explicit author direction.

After extracting the ZIP into a new directory, with Python3.10+ and NumPy:

```text
python verify-package.py --self-test
python verification/verify.py --self-test --check verification/runs/algebra.json
```

Expected: all inventoried file sizes/hashes agree;9 package scope/path mutations
are rejected;80 finite algebra/diagnostic checks pass and13 hostile finite
mutations are rejected. Exact rational/provenance fields compare exactly;
floating diagnostics use relative tolerance1e-12 and absolute tolerance1e-14.
No Git checkout or TECT history is needed for these two commands.

The legacy-replay command is optional full-repository work. Its retained
results are supplied, but its code explicitly requires the wider historical
source registry. It is not the extracted standalone command above.

verification/rendered-v011 contains all seven current PNG pages actually
inspected. Current text/geometry and visual receipts are pdf-qa-v011.json and
render-review-v011.json under verification/runs. The older rendered/ pages
and unsuffixed receipts describe immutable edition0.1.0, not this revision.
The original input snapshot is hash-pinned; it is not a claim that the older
historical solver residual equals the standalone reference functional.

Keep a trusted outer ZIP SHA-256 with transmission. A hash inventory checks
integrity relative to that manifest, not author identity or proof validity.
Any mathematical correction must issue a new source/PDF/review package.
