# Verification protocol for the A2/R-157/R-158 manuscript

This is a repository-facing draft protocol.  It points to the canonical P1
source files and does not replace the claim-level reproduction bundles.  A
standalone capstone bundle must be built only after operator confirmation of
the integrated referee note, as required by the repository bundle policy.

Run from `E:\Dev\TECT` with the repository environment:

```powershell
$py = "E:\Dev\TECT.venv\Scripts\python.exe"
& $py codes/foundations/a2_full_production_verify.py
& $py codes/foundations/a2_pinned_functional_unique_zero_global_minimizer.py
& $py codes/foundations/a2_pinned_functional_unique_zero_global_minimizer_independent.py
& $py codes/foundations/a2_pinned_functional_unique_zero_global_minimizer_verify.py
& $py codes/foundations/a2_charge_ensemble_first_order_shell_transition.py
& $py codes/foundations/a2_charge_ensemble_first_order_shell_transition_independent.py
& $py codes/foundations/a2_charge_ensemble_first_order_shell_transition_verify.py
& $py verification/scripts/a2_r472_lean_crosscheck_verify.py --output tmp/r472-integrated.json
& $py publish/papers/a2-r157-r158-ensemble-minimizers/verification/exact_coercivity_audit.py
& $py publish/papers/a2-r157-r158-ensemble-minimizers/verification/classii_sign_audit.py
& $py publish/papers/a2-r157-r158-ensemble-minimizers/verification/ensemble_identity_audit.py
& $py publish/papers/a2-r157-r158-ensemble-minimizers/verification/analytic_dependency_audit.py
& $py publish/papers/a2-r157-r158-ensemble-minimizers/verification/review_packet_audit.py --self-test
& $py publish/papers/a2-r157-r158-ensemble-minimizers/verification/reproduction_manifest.py
```

Expected registered results are:

* full-production evolution audits: `20/20`, `14/14`, `12/12`, and `15/15`
  PASS;
* R-157 primary and independent lanes: `26/26` and `24/24` PASS;
* R-158 primary and independent lanes: `35/35` and `24/24` PASS;
* integrated R-157/R-158 authority, artifact, PDF, and legacy checks: PASS;
* paper-local exact coercivity audit: `13/13` PASS, with an exact 1/5 H2 lower-bound certificate and hostile mutations rejected;
* paper-local Class-II source/sign audit: `8/8` PASS, with both source hashes recorded and the undefined v2.0 Laplacian convention retained as an open gate;
* paper-local ensemble identity/Bregman/coexistence/witness audit: `24/24` PASS, reconstructed from the pinned A1 manifest with hostile mutations rejected;
* paper-local analytic-dependency audit: `50/50` PASS, with exact Sobolev, compactness, kernel, direct-method, floor, and sign-prerequisite checks and hostile mutations rejected;
* review-packet structural/hash audit: `19/19` PASS, checking the three stable theorem labels, `P-01`--`P-15`, nine hostile tests, `N-01`--`N-07`, `D-01`--`D-07`, blank status, signature fields, and current manuscript/PDF hashes without filling either form;
* hash-pinned reproduction manifest: `PAPER-REPRODUCTION-MANIFEST-PASS`, with package file SHA-256 values, audit artifact counts, manuscript-hash consistency, and expected replay commands recorded;
* R-472 exact-core sidecar: primary `30/30`, independent `22/22`, hostile
  `12/12`, integrated `22/22`, with Lean compilation PASS.

The last command is assurance-only: R-472 is explicitly non-bearing and must
not be used to promote the A2/R-157/R-158 theorem claims.  The manuscript
version 0.1.38 records the self-contained functional and spectral specification, the closest 2026 Belin--Schneider quasilinear amplitude-theory comparison and narrowed residual-contribution language,
the indexed Class-II Euler--Lagrange formula and coefficient tensor, the paper-local
Fourier-multiplier realization with `H^4`/`H^2` domains, and a bounded primary-source
literature crosswalk; the displayed data and those sources are
context and audit inputs, not new proof claims.  The registered H3 record is provenance/transfer metadata only; the executable checks target the explicit functional printed in the manuscript.  The paper-local exact-coercivity command reads the pinned manifest, writes `verification/runs/exact-coercivity.json`, and is auxiliary evidence rather than a claim-tier promotion.  The paper-local Class-II sign command reads the two pinned A2 notes, writes `verification/runs/classii-sign.json`, and is likewise auxiliary evidence rather than a canonical-source correction or claim-tier promotion.  The ensemble-identity command independently reads the pinned A1 manifest, writes `verification/runs/ensemble-identity.json`, and checks exact completion, Bregman, coexistence-sign, and constant-observable saturation identities; it is also auxiliary evidence.  The analytic-dependency command parses the pinned manifest and manuscript declarations, writes `verification/runs/analytic-dependency.json`, and checks only structural prerequisites for the analytic proof, including the direct mild contraction, Fourier compactness, and singular-Grönwall reduction; it is not a theorem proof or external review.  The current artifact also checks that the Galerkin-limit text explicitly upgrades the time derivative to the `$L^2_tL^2_x$` pivot before the nonlinear chain rule, that the fixed-charge constraint is weakly closed by strong `$L^2$` convergence, and that the coefficient/product local-Lipschitz and Fourier fractional-semigroup bounds are displayed, together with the projected chain-rule limit, endpoint-integrability estimate, periodic Moser tame bound, and shifted-base endpoint bootstrap, including the strict Hölder range, split-kernel integral, full Hölder norm, endpoint semigroup factor, and temporal Banach-scale induction, and the finite-interval `L^2(0,T;L^2)` endpoint control used for the `s=0` energy identity, plus the direct fixed-point, Fourier-tail compactness, and ordinary-Grönwall reduction; this remains a structural audit, not a signed proof.  The signed external-review request and response template are in `external-review-handoff.md`; `verification/runs/reproduction-manifest.json` is the hash-pinned package index for that handoff.  The bundled base-Python portability replay is recorded in `EXP-001420`.  No external response is implied until a reviewer returns the signed schema recorded in `EXP-001410`.

These executable checks recompute the exact constants, signs, spectral
intervals, normalizations, and hostile mutations recorded by the claim.  They
are not substitutes for the analytic proof, the literature crosswalk, or an
external referee audit.

## Current replay boundary

On 2026-09-03 the A2 wrapper and all four R-157/R-158 child lanes reproduced
their registered PASS counts.  A shared record predicate in the two integrated
verifiers was then repaired in v1.0.2: the lookup key, structured title, status,
and exact gate are authoritative, while the free-form task note is no longer
required to repeat those tokens.  The repair and its adversarial boundary are
recorded as `EXP-001372`, correcting the earlier replay boundary `EXP-001370`.

A fresh replay now passes R-157 integrated verification `144/144` (including
legacy A2 `61/61`) and R-158 integrated verification `155/155` (including the
R-157/A2 regression).  Manuscript v0.1.38 additionally displays the generators,
internal matrices, density floor, Class-II coefficient formulas, explicit
shell-bottom scalar symbol, the indexed Euler--Lagrange formula and coefficient
tensor, the integration-by-parts sign in `N_II`, and the nonlinear energy `Phi`,
alongside the direct-method
coercivity/weak-lower-semicontinuity route for the `mu>mu_t` minimizer, the full
lower-order map `N=N_loc+N_II`, the Gelfand-triple chain-rule hypotheses, the projected chain-rule limit,
the endpoint-integrability estimate, the periodic Moser tame bound, the shifted-base endpoint bootstrap, its strict Hölder range, split-kernel integral, full Hölder norm, endpoint semigroup factor, and
the bounded primary-source crosswalk.  These are self-containedness and
proof-text/literature-boundary clarifications, not a new claim or tier change;
the sign/Phi repair is recorded as `EXP-001379` and the indexed-variation
follow-up as `EXP-001380`; the charge-jump wording correction is recorded as `EXP-001382`, a separate
proof-scope repair that does not change any executable result.  `EXP-001386`
records the unresolved canonical A2 Class-II principal-sign mismatch; no
source hash is changed and the discrepancy remains an external/operator gate;
the disclosure and replay are recorded in `EXP-001387`; the narrowed notation analysis is recorded in `EXP-001388`; the explicit raw-Laplacian convention and v0.1.17 replay are recorded in `EXP-001390`; the exact Young-constant defect audit is recorded in `EXP-001392`, and the exact-constant repair/replay in `EXP-001394`; the exact 1/5 H2 coercivity certificate, graph-equivalent H2 norm, nearest-integer shell clarification, and v0.1.17 replay are recorded in `EXP-001395` and `EXP-001398`; the v0.1.18 source/PDF replay and source/sign audit are recorded in `EXP-001399`; the full finite-scope A2/R-157/R-158 replay is recorded in `EXP-001400`; the v0.1.19 theorem/provenance separation, fresh compile, and PDF QA are recorded in `EXP-001401`--`EXP-001402`; the v0.1.20 Fourier-multiplier realization, fresh compile, PDF QA, and finite-scope replay are recorded in `EXP-001403`; the bundled-base-Python smoke replay is recorded in `EXP-001405`; the v0.1.21 coexistence-wording clarification, fresh compile, PDF QA, and finite-scope replay are recorded in `EXP-001406`; the paper-local ensemble identity audit and 24/24 artifact are recorded in `EXP-001407`; the analytic-dependency audit baseline and 28/28 artifact are recorded in `EXP-001409`; the chain-rule regularity repair and 30/30 artifact are recorded in `EXP-001411`; the fixed-charge closure repair and 31/31 artifact are recorded in `EXP-001412`; the external-review handoff protocol and signed response schema are recorded in `EXP-001410`; the executable paper-local coercivity and source/sign audits and JSON artifacts are recorded in `EXP-001396`--`EXP-001399`.  The non-bearing R-472 authority pins were then
resynchronized to the current R-157/R-158 manifests in `EXP-001381`; its fresh
primary `30/30`, independent `22/22`, hostile `12/12`, and integrated `22/22`
Lean replay now pass.  R-472 remains assurance-only and is not load-bearing
theorem evidence.
The repository synchronization gate is now passing: after PAH PID 27092 exited, `TC-0013` corrected only the untrusted wall-clock provenance for `EXP-001395`--`EXP-001407`, `regen_all.py` refreshed the governed surfaces; `EXP-001408` records the post-PAH `release_check.py` exit 0, `EXP-001416` records the v0.1.25 proof-text repair, `EXP-001417` records the final v0.1.25 recheck after generated-surface refresh, and `EXP-001418` records the post-PDF catalog-staleness repair and governed recheck; `EXP-001419` records the hash-pinned reproduction manifest, and `EXP-001421`--`EXP-001422` record the focused primary-source crosswalk and v0.1.26 update; `TC-0014` corrects only the retained future wall-clock field of `EXP-001422`.  `EXP-001425` records the source-sign decision aid, `EXP-001426` records the v0.1.27 positive-time Hölder proof repair, and `EXP-001430` records the v0.1.28 shifted-base proof repair; `EXP-001432` records the v0.1.29 endpoint-estimate repair; `EXP-001435` records the v0.1.30 explicit endpoint-constant repair; `EXP-001436` records the v0.1.31 temporal-bootstrap repair, fresh governed regeneration, and release recheck; `EXP-001437` records the finite-interval time-derivative endpoint repair and subsequent governed recheck; `EXP-001439` records the repository-status wording synchronization and subsequent governed recheck; `EXP-001440` records the bibliography-layout compaction; `EXP-001441` records the final v0.1.34 manifest and governed recheck; `EXP-001442` records the v0.1.35 closest-quasilinear-source update and `EXP-001443` its synchronized manifest and governed release recheck; `EXP-001444` records the v0.1.36 Galerkin/Hilbert-scale proof-text repair and 47/47 structural replay; `TC-0015` corrects only its retained wall-clock provenance; `EXP-001445` records the v0.1.36 complete finite replay, hash manifest, rendered PDF, and governed release PASS; `EXP-001446` records the v0.1.37 direct-analytic proof and applicability-audit repair, and `EXP-001447` records the synchronized finite replay, manifest, rendered-PDF review, regeneration, and governed release PASS. `EXP-001449` records the v0.1.38 stable labels, blank proof/novelty contracts, `19/19` packet audit, complete finite replay, and rendered-PDF review; `EXP-001450` records governed regeneration and release PASS.  The historical `EXP-001391` failure remains immutable context and is superseded for current state.  This does not replace the analytic proof, specialist literature review, external proof audit, operator confirmation, or capstone bundle; rerun the release check after any later source or generated-surface change.

## Canonical evidence paths

* `claims/A2-FULL-PRODUCTION-WELLPOSED/claim.md`
* `claims/A2-FULL-PRODUCTION-WELLPOSED/status.json`
* `claims/A2-FULL-PRODUCTION-WELLPOSED/notes/a2-full-production-wellposedness-260717-v2.0.tex.txt`
* `claims/A2-FULL-PRODUCTION-WELLPOSED/notes/a2-pinned-functional-unique-zero-global-minimizer-260803-v1.0.tex.txt`
* `claims/A2-FULL-PRODUCTION-WELLPOSED/notes/a2-charge-ensemble-first-order-shell-transition-260803-v1.0.tex.txt`
* `claims/A2-FULL-PRODUCTION-WELLPOSED/bundle/A2-Full-Production-WellPosedness-T6-260717/`
* `publish/papers/a2-r157-r158-ensemble-minimizers/proof-audit.md`
* `publish/papers/a2-r157-r158-ensemble-minimizers/external-review-handoff.md`
* `publish/papers/a2-r157-r158-ensemble-minimizers/source-sign-reconciliation.md`
* `publish/papers/a2-r157-r158-ensemble-minimizers/submission-readiness.md`

The manuscript's numerical table is valid only at the registered scope.  Any
failed command, source-hash drift, or proof-audit objection must stop the
publication lane and be recorded before the status can advance beyond draft.
