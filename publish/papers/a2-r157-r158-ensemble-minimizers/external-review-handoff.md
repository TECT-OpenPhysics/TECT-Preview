# External-review handoff — A2/R-157/R-158 draft

Status: draft v0.1.40, finite classical side-16 torus only.  This handoff is
an invitation and a review protocol; it is not evidence that an external
mathematician, source owner, operator, or specialist has already reviewed the
paper.

## Requested disposition

Please review the manuscript and return one of `PASS`, `REPAIR`, or
`OUTSIDE-SCOPE` for each numbered item below.  A `PASS` must cite the exact
page/equation and state every hypothesis used.  A `REPAIR` must give a
replacement statement or proof step and identify all dependent equations.
`OUTSIDE-SCOPE` is appropriate when a requested conclusion is not claimed by
the paper.  The reviewer should sign and date the response; no response is
treated as an approval.

## Fixed object and claim boundary

The object is the explicitly displayed three-component complex field on
\(\mathbb T^3_{16}\), realified as six components, with the positive density
floor \(\varepsilon_\rho=10^{-12}\), the pinned scalar coefficients and
internal matrices in `manuscript.tex`, and the real \(L^2\) pairing.  The
linear operator has form domain \(H^2\) and operator domain \(H^4\).  The
ensemble variables \(Q=\|\Psi\|_2^2/2\) and \(\mu\) are imposed mathematical
parameters.

The paper does **not** claim an infinite-volume or continuum limit, a quantum
or KMS construction, a physical vacuum, a derived conserved charge, BCC
selection, a real-time dynamics, or Sector-A/TECT closure.  R-472 is an
assurance-only sidecar and is not load-bearing theorem evidence.

## Theorems to audit

1. **A2 evolution theorem.**  Global well-posedness, continuous dependence,
   exact energy identity, and positive-time smoothness for the displayed
   regularised gradient flow with \(H^2\) data.
2. **R-157 neutral theorem.**  Exact coercivity and radial derivative bounds,
   uniqueness of the zero critical point, and exponential decay for the
   unconstrained functional.
3. **R-158 imposed ensemble theorem.**  The finite-torus \(|n|^2=3\) spectral
   shell, constrained minimisers for \(Q/|\mathbb T^3_{16}|\ge\rho_*\), and
   zero/nonzero grand-potential coexistence at \(\mu_t\).  A one-sided charge
   jump for every \(\mu>\mu_t\) is explicitly not claimed.

## Mandatory mathematical questions

1. Does the displayed Fourier multiplier define a self-adjoint positive
   operator with exactly the stated \(H^4\) domain and \(H^2\) form domain,
   including the finite-torus norm equivalence?
2. Is the indexed Class-II Euler map, including every denominator derivative,
   the raw-Laplacian integration-by-parts sign, and the tensor \(C(u)\), a
   locally Lipschitz map \(H^2\to L^2\) on bounded sets?
3. Do the cited analytic-semigroup estimates and the \(t^{-1/2}\) Volterra
   contraction apply to this operator and nonlinear map with the stated
   initial space?
4. Does the direct Fourier-tail/finite-mode Galerkin argument provide the claimed strong convergence,
   nonlinear passage, explicit Galerkin-limit `L^2_tL^2_x` time-derivative upgrade on every finite interval, including the `s=0` energy endpoint, and exact Gelfand-triple/Hilbert-space chain rule?
5. Is the endpoint cancellation valid with the stated Hölder modulus, and
   does the Moser iteration justify \(C^\infty\) positive-time regularity?
6. Do the exact radial equality cases prove the R-157 uniqueness and decay
   statements without an omitted differentiability or integrability premise?
7. In R-158, are the charge normalization, Bregman equality case, shell
   saturation, weak closure of the fixed-charge constraint, coercive direct method, and the restricted coexistence wording
   all correct?  Does “first-order” require any extra branch-selection claim?
8. Does the manuscript's displayed Dirichlet density, real pairing, and raw
   componentwise Laplacian convention give exactly the indexed negative
   principal sign used in the gradient flow, and does the text correctly keep
   the later canonical shorthand outside the theorem premises?  The canonical
   source owner, not the mathematical reviewer, separately decides whether the
   v2.0 source used a positive-Laplacian shorthand or needs an authorized
   erratum.  The alternatives, source hashes, and transfer-only response schema
   are fixed in `source-sign-reconciliation.md`.

## Reproduction package

Run from `E:\Dev\TECT` with the repository environment.  Install the Python
dependencies from `requirements.txt` first; the primary R-157/R-158 lanes
require the pinned `sympy==1.14.0`.  The clean-snapshot orchestrator archives
the committed tree rather than copying the working directory.  Its non-bearing
R-472 step additionally requires the pinned Lean toolchain and a resolved
Mathlib `.lake` cache; pass a different cache explicitly with `--lean-cache`
when it is not located at `verification/lean/.lake`.

```powershell
$py = "E:\Dev\TECT.venv\Scripts\python.exe"
& $py -X utf8 codes/foundations/a2_full_production_verify.py
& $py -X utf8 codes/foundations/a2_pinned_functional_unique_zero_global_minimizer.py
& $py -X utf8 codes/foundations/a2_pinned_functional_unique_zero_global_minimizer_independent.py
& $py -X utf8 codes/foundations/a2_pinned_functional_unique_zero_global_minimizer_verify.py
& $py -X utf8 codes/foundations/a2_charge_ensemble_first_order_shell_transition.py
& $py -X utf8 codes/foundations/a2_charge_ensemble_first_order_shell_transition_independent.py
& $py -X utf8 codes/foundations/a2_charge_ensemble_first_order_shell_transition_verify.py
& $py -X utf8 verification/scripts/a2_r472_lean_crosscheck_verify.py --output tmp/r472-integrated.json
& $py -X utf8 publish/papers/a2-r157-r158-ensemble-minimizers/verification/exact_coercivity_audit.py
& $py -X utf8 publish/papers/a2-r157-r158-ensemble-minimizers/verification/classii_sign_audit.py
& $py -X utf8 publish/papers/a2-r157-r158-ensemble-minimizers/verification/ensemble_identity_audit.py
& $py -X utf8 publish/papers/a2-r157-r158-ensemble-minimizers/verification/analytic_dependency_audit.py
& $py -X utf8 publish/papers/a2-r157-r158-ensemble-minimizers/verification/review_packet_audit.py --self-test
& $py -X utf8 publish/papers/a2-r157-r158-ensemble-minimizers/verification/clean_snapshot_replay.py --self-test
& $py -X utf8 publish/papers/a2-r157-r158-ensemble-minimizers/verification/reproduction_manifest.py --self-test
```

The current finite replay is A2 `61/61`, R-157 `144/144`, R-158 `155/155`,
paper-local `13/13`, `8/8`, `24/24`, `50/50`, and review-packet `22/22`.  The 17-page v0.1.40 PDF with seventeen references was built
with bundled Tectonic and visually inspected.  The JSON artifacts under
`verification/runs/` contain source hashes and per-assertion outcomes.  The
analytic-dependency artifact checks structural prerequisites only, including the explicit coefficient/product H2-to-L2 local-Lipschitz and modewise fractional-semigroup bounds, the projected chain-rule limit, the endpoint-integrability estimate, the periodic Moser tame bound, the shifted-base endpoint bootstrap, the strict Hölder range, the split-kernel integral, the full Hölder norm, and the endpoint semigroup factor, the explicit temporal Banach-scale map, the $D^jN$ bound, and the four-spatial-derivative temporal induction, and the finite-interval `L^2(0,T;L^2)` endpoint control for the `s=0` energy identity, the projected initial-data/initial-energy convergence, the direct mild contraction, Fourier compactness proof, singular-Grönwall reduction, and the Hilbert-scale `C([0,T];H^2)` quadratic identity through `s=0`; it is not a replacement for this review.  The hypothesis-by-hypothesis external-theorem map is `theorem-applicability-audit.md`. The hash-pinned `source-sign-reconciliation.md` fixes the two convention branches and the source-owner response schema.  The requirement matrix and promotion rules are summarized in `submission-readiness.md`.  `verification/runs/reproduction-manifest.json` records the package file hashes and expected replay outputs for independent reproduction (`EXP-001419`; focused literature crosswalk and v0.1.26 update `EXP-001421`--`EXP-001422`; source-sign aid `EXP-001425`; v0.1.27 Hölder proof repair `EXP-001426`; v0.1.28 shifted-base proof repair `EXP-001430`; v0.1.29 endpoint-estimate repair and governed release recheck `EXP-001432`; v0.1.30 explicit endpoint-constant repair and governed release recheck `EXP-001435`; v0.1.31 temporal-bootstrap repair and governed release recheck `EXP-001436`; v0.1.32 finite-interval time-derivative endpoint repair and governed release recheck `EXP-001437`; v0.1.33 repository-status wording synchronization and governed release recheck `EXP-001439`; v0.1.34 bibliography-layout compaction `EXP-001440` and final manifest/governed release recheck `EXP-001441`; v0.1.35 closest-quasilinear-source boundary `EXP-001442` and synchronized manifest/governed release recheck `EXP-001443`; v0.1.36 Galerkin/Hilbert-scale proof repair `EXP-001444`, provenance-only correction `TC-0015`, and finite replay/manifest/governed release recheck `EXP-001445`; v0.1.37 direct-analytic proof and applicability repair `EXP-001446` and synchronized finite replay/manifest/rendered-PDF/governed release PASS `EXP-001447`; v0.1.38 stable theorem labels, blank signed-review contracts, packet audit and full replay `EXP-001449`, followed by governed regeneration and release PASS `EXP-001450`; historical temporal correction `TC-0014`).

The v0.1.40 coupled-system literature repair, 17-page visual review, and
isolated `14/14` replay are recorded in `EXP-001458`; the subsequent combined
shared-tree repository release PASS is recorded in `EXP-001459`.  Neither is a
signed proof or novelty response.
The watcher-gated local content commit
`7e1de76c06be0d6a43da0459f7ab0b55920a1795` is recorded in `EXP-001460`;
reviewers should report the exact later commit they actually inspect.

## Frozen blank response contracts

The theorem-level response contract is
`independent-proof-review-form.md`.  It maps `P-01`--`P-15` to the three
labelled main theorems and exact equation groups, requires nine hostile tests,
and fixes reviewer independence, repair propagation, signature, manuscript
hash, PDF hash, and toolchain fields.  The distinct literature contract is
`specialist-novelty-review-form.md`; it fixes seven search families and seven
proposition-level novelty decisions.  Both files are deliberately blank and
record no review outcome.  Their structural and hash consistency is checked
by `verification/review_packet_audit.py`; a PASS from that script certifies
only packet completeness, never proof correctness or novelty.

## Reviewer response template

For each question, report:

```text
item: <number>
disposition: PASS | REPAIR | OUTSIDE-SCOPE
evidence: <equation/page/source>
hypotheses: <complete list>
objection_or_repair: <precise statement>
dependent_items: <list>
```

Conclude with the reviewer identity, date, toolchain/commit used for
reproduction, and a statement that the response is an independent review.
Until such a signed response exists, the paper remains `draft` and no
`operator-confirmed` or `PUBLISHED` marker may be added.

## Non-claims of this handoff

Executable PASS counts, a clean PDF, and the repository release check do not
prove the analytic theorem, novelty, or canonical source intent.  This file
does not authorize submission, upload, tagging, publication, or any physical
interpretation.
