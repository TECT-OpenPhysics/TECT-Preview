# Review distribution: start here

The eight-page manuscript.pdf and its TeX source are the main deliverables.
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
python verification/strengthened_audit.py --check verification/runs/strengthened-v012.json
python verification/package_gates.py --self-test
```

Expected: all inventoried sizes/hashes agree;14 package scope/path mutations
are rejected. Baseline80 and strengthened59 finite checks pass, rejecting13
and14 hostile finite mutations respectively. Visual/output gates reject35
mutations. Exact rational/provenance fields compare exactly;
floating diagnostics use relative tolerance1e-12 and absolute tolerance1e-14.
No Git checkout or TECT history is needed for these four commands.

The legacy-replay command is optional full-repository work. Its retained
results are supplied, but its code explicitly requires the wider historical
source registry. It is not the extracted standalone command above.

verification/rendered-v012 contains all eight current PNG pages actually
inspected. Current receipts are pdf-qa-v012.json and render-review-v012.json
under verification/runs. Earlier rendered/ and rendered-v011/ pages and their
receipts describe immutable historical editions, not this revision.

The operator authorizes package completion with external reviews remaining
NOT_PERFORMED. self-review-v012.md describes the internal repair cycle and
bounded stop rule, not independent human acceptance.
The original input snapshot is hash-pinned; it is not a claim that the older
historical solver residual equals the standalone reference functional.

Keep a trusted outer ZIP SHA-256 with transmission. A hash inventory checks
integrity relative to that manifest, not author identity or proof validity.
Any mathematical correction must issue a new source/PDF/review package.
