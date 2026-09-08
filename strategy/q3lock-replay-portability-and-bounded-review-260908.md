# Q3LOCK replay portability and bounded independent reread

Date: 2026-09-08. Status: internal tooling repair and bounded AI review.
R-497 remains T0, claim_bearing=false, RESEARCH_ONLY. The sole research
authority chain remains EXP-000780 -> EXP-000781 -> EXP-000782.
No final content freeze, signed review, PDF, submission, or promotion occurs.

## Confirmed reproduction fault

The previously current independent wrapper (0.1.1) put sys.version, Python
implementation and OS platform inside its deterministic replay object. It
also serialized the current manuscript's absolute path in an assertion row.
Its strict comparison therefore rejected an otherwise equal computation
when the runtime or checkout location changed.

The same paper sources and stored v057-readme-sync result were checked using
the repository CPython 3.12.9 and bundled CPython 3.12.14 on Windows 11.
The former failed, the latter passed. A complete top-level payload comparison
under 3.12.9 found only producer.python different; no scientific field differed.
This was a tooling portability fault, not a changed mathematical result.

## Repair and reproducible checks

Wrapper 0.1.2 records the manuscript path relative to the repository and
emits producer_environment only in the outer result envelope. The full
scientific replay remains exactly compared without normalization or ignored
keys at comparison time. The actual manuscript existence check and all
original source hashes, child payload equality, counts, and scope checks stay.
An assertion-enabled guard also protects direct build_payload callers.

The new independent result is
claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-q3lock-independent-replay-portability-v1/result.json.
It was generated once using the repository runtime, then checked read-only
with both CPython 3.12.9 and 3.12.14: the child retained 306/306 assertions
and the wrapper retained 14/14 checks. These are finite diagnostics, not
analytic proofs. Old result JSON files were not rewritten.

From the registered paper worktree:

```powershell
& E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_independent_replay.py --check
& E:/Dev/TECT.venv/Scripts/python.exe -X utf8 -m unittest discover -s verification/tests -p test_q3lock_independent_replay_portability.py -v
& E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_manuscript_integrated_replay.py --check
```

The eight portability tests cover an actual relocated exact-byte dependency
copy in a path with spaces and a non-ASCII character, changed environment
strings, relative locators, read-only byte preservation, strict scientific
mutation rejection, fresh child-result corruption, no-overwrite publication,
and optimized-Python refusal. The mutation test includes ten distinct hostile
subcases, including unchanged PASS/counts with a corrupted hash. Test oracles
are tooling controls; no derived physical constants are introduced.

New current fresh, integrated, locator and completion checkpoints use the
portability-v1 label. Finite-form v038 and algebra v039 are unchanged inputs.
The integrated record explicitly protects the displaced independent v057,
integrated v110 and fresh v115 result/source-map bytes and includes this note
and the new tests in its source hashes. Its saved result records actual
replay counts; this note does not predeclare a new integrated PASS.

## Adversarial review

1. Objection: dropping environment metadata could hide changed mathematics.
   DISMISSED within the tested tooling scope: metadata is outside replay;
   every replay key is still compared exactly. Changes to child/source hashes,
   assertion rows, scope, missing keys, and extra keys are rejected.
2. Objection: relative paths could mask a missing or different manuscript.
   DISMISSED within the tested scope: is_file and content hashes remain;
   the test executes a real relocated copy, not a substituted path string.
3. Objection: provenance becomes unverifiable after separating metadata.
   DISMISSED for the integrated envelope: its complete stored JSON is hashed.
   Separate new envelopes may differ by environment; portability means
   rechecking the same saved envelope, not universal byte-identical builds.
4. Objection: one OS and two Python releases establish universal portability.
   UPHELD as a limit: the child uses math floating-point operations. Only
   these tested runtimes and the relocation fixture are supported evidence;
   no cross-OS or all-version claim is made.
5. Objection: the relocated subset is the goal's clean-snapshot release test.
   UPHELD as a limit: it tests the independent dependency closure only. A clean
   tracked snapshot, full reproduction, release and final hash freeze remain.

Sign, normalization, units, convergence, and numerical lower bounds are not
changed by this repair. The frozen child is replayed exactly; no tolerance
or expected numerical value was changed to achieve PASS. External reviewers
are invited to rerun and attack the commands above.

## Bounded independent manuscript reread

Two separately dispatched read-only AI reviewers examined the unchanged
manuscript SHA-256
3b119cce87d3e80c72abee6d224cc91afdc48563ad74e0659e309e313aed0b51.
Neither reported a confirmed local mathematical defect in its assigned block.
This is a bounded negative search outcome, not mathematical certification.

- Lines 809-1350: tempered metric, KP vector envelope, finite-M-before-Holder
  closure, weighted-tail compactness, boundary normalizer and kernel continuity,
  source-window tangent limits, finite FKG and closed-upper-set Borel passage.
  The reviewer checked KP Assumption (A), (B), and (2.47)-(2.49) against
  https://arxiv.org/pdf/math-ph/0609045v1. The interacting finite-mesh loop
  limit, pressure derivative theorem, and later collective/cusp block were
  outside this review's independent scope.
- Lines 1660-2228: translated forms and scalar Jensen, the collective Hessian,
  FKG moment substitution, spectral cutoff followed by coordinate cutoff in
  Falk--Bruch, squared-tail Griffiths and pressure normalization. The reviewer
  checked KKK Propositions 3.18 and 3.9 at
  https://arxiv.org/html/0710.2303v1. Earlier loop/FKG/infrared/DLR inputs remain
  dependencies, not newly certified conclusions of this reread.
- Optional notation: the polynomial-integrability lemma's bracket
  <psi,P psi> can be explicitly described as the multiplication-form integral.
  The current text already says positive form trace and later defines d_i as
  a multiplication form; no assertion that P psi is in L2 was needed. This
  is a reader-clarity suggestion, not an established proof failure. The
  manuscript was not changed merely to force another proof checkpoint.

All A1-A23 signed-review obligations stay open. No reviewer signature is
supplied by these AI passes. Fixed finite beta, selected DLR states, and the
declared sufficient-parameter region must not be extended to KMS, ground
states, extremality, continuum, cosmology, or Sector A closure.

## Next gate

Check the new integrated family under both installed runtimes, retain all
failure evidence if any, and run repository consistency checks. Final clean
tracked-snapshot reproduction and signed mathematical/literature review are
still required. Generate and visually review the paper PDF only after the
content-review and final-organization gate; do not use a watcher to bypass it.
