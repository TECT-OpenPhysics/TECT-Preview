# STATUS — A2/R-157/R-158 ensemble-minimizers

Lifecycle: `draft`
Version: `0.1.39`
Date: `2026-09-04`
Owner: TECT publication lane

## Current state

The folder contains a manual integrated manuscript draft, its cited-claim
list, a literature-first crosswalk, a reproduction protocol, and an explicit
external-review handoff.  The draft
uses only the registered A2 claim, R-157, R-158, and the non-bearing R-472
assurance sidecar.  Version 0.1.39 retains the closest 2026 Belin--Schneider quasilinear amplitude-theory comparison, narrows the residual contribution accordingly, and retains the self-contained generators, internal matrices,
density floor, and Class-II coefficient formulas, displays the indexed
Class-II Euler--Lagrange formula and coefficient tensor `\mathit{C}(u)`, and
retains the corrected integration-by-parts sign and explicit nonlinear energy
`\Phi` used by the chain rule.  The local theory now displays its Duhamel contraction and continuation constants; the Galerkin passage now proves compactness by an explicit Fourier tail plus finite-mode argument and explicitly upgrades
`\partial_tu` to `L^2_tL^2_x` before the chain rule is invoked.  The theorem statement additionally requires `\partial_t\Psi\in L^2(0,T;L^2)` for every finite interval, and the proof ties this endpoint control to the `s=0` energy identity.  It additionally realizes the declared
fourth-order linear part as a modewise Hermitian positive Fourier multiplier
with operator domain `H^4` and form domain `H^2`.  The coefficient/product H2-to-L2 local-Lipschitz estimate, the modewise Fourier-multiplier fractional-semigroup bound, the projected chain-rule limit, the explicit endpoint-integrability bound, and the periodic Moser tame estimate are also displayed explicitly; the shifted-base Sobolev bootstrap now records its domain, endpoint cancellation, Hölder estimate, nested induction, full $C^\theta$-norm control, strict $0<\theta<1$ range, split-kernel integral, and endpoint semigroup factor; external proof verification remains required.  The declared functional and
spectral bottom remain reconstructible without a private backend.  It makes no physical-vacuum, BCC, infinite-volume,
quantum-continuum, or Sector-A closure claim.

The latest replay confirms all child and integrated audit lanes.  The standalone mathematical theorem statements are written for the explicitly printed functional; the named H3 record is retained only for provenance and transfer to the canonical P1 interpretation.  The
shared T-054 record predicate was repaired in verifier v1.0.2 to use structured
task id/title/status/gate fields rather than redundant free-form note tokens;
the repair is recorded in exploration `EXP-001372`.  A bounded primary-source
literature expansion and matching related-work citations were added in
`EXP-001375`; the focused adjacent-source expansion and matching related-work
citations are recorded in `EXP-001421`.  These records narrow the non-subsumption
boundary but are not a novelty or priority decision.  The repository-wide release check was reopened after PAH PID 27092 exited.  `TC-0013`
marks only the future-dated `recorded_at` values of `EXP-001395`--`EXP-001407`
untrusted; `regen_all.py` then refreshed the catalog, proof-evidence map, management
indexes, and related projections.  `EXP-001408` records the post-PAH clean release checkpoint, and `EXP-001417`
records the final v0.1.25 release recheck (`PASS -- safe to push the public
surface`).  `EXP-001418` records the transient post-PDF catalog-staleness repair
and the subsequent governed release PASS.  `EXP-001419` records the hash-pinned reproduction manifest and its integrity PASS.  `EXP-001421` and `EXP-001422` record the focused primary-source crosswalk and v0.1.26 manuscript update; `TC-0014` corrects only the future wall-clock field of `EXP-001422`; `EXP-001425` records the hash-pinned source-sign decision aid, `EXP-001426` records the v0.1.27 Hölder proof-text repair, and `EXP-001430` records the v0.1.28 shifted-base proof repair, `EXP-001432` records the v0.1.29 endpoint-estimate repair, and `EXP-001435` records the v0.1.30 explicit endpoint-constant repair, and `EXP-001436` records the v0.1.31 temporal-bootstrap repair and final governed release recheck after generated-surface refresh; `EXP-001437` records the finite-interval time-derivative endpoint repair and subsequent governed recheck; `EXP-001439` records the repository-status wording synchronization and subsequent governed recheck; `EXP-001440` records the bibliography-layout compaction; `EXP-001441` records the final manifest and subsequent governed release recheck.  This is a repository-state result,
not a theorem or publication-readiness result; the lifecycle remains `draft` while
external proof, novelty, operator, and capstone gates remain open.  The canonical
source-sign issue is separately open only for transfer to the TECT/P1
interpretation.  The non-bearing
R-472 assurance pins were
resynchronized to the current R-157/R-158 manifests and its fresh
30/30-primary, 22/22-independent, 12/12-hostile, and 22/22-integrated Lean
replay passes; this T0 sidecar remains separate from theorem evidence.  The
repair is recorded in `EXP-001381`.  The v0.1.10 wording correction removes an
unsupported global-charge-jump reading (recorded in `EXP-001382`): the theorem retains coexistence at
`\mu_t` and the saturated value `Q_*`, but does not identify every global
minimizer's charge for `\mu>\mu_t`.  A separate source-reconciliation
gate `EXP-001386` is open for canonical transfer because the canonical A2 v2.0 note writes the
opposite Class-II principal sign from the paper and executable audit; no
canonical source hash has been changed.  The explicit v1.1/v2.0 comparison and
its clean v0.1.11 replay are recorded in `EXP-001387`.  The convention-narrowing analysis is recorded in `EXP-001388`; the v0.1.18 source/PDF replay, graph-equivalent H2 norm, exact coercivity certificate, nearest-integer shell argument, paper-local Class-II sign audit, and full finite-scope replay are recorded in `EXP-001395`--`EXP-001400`; the v0.1.19 H3 provenance separation, fresh compile, and PDF QA are recorded in `EXP-001401`--`EXP-001402`; the v0.1.20 Fourier-multiplier realization, fresh compile, PDF QA, and finite-scope replay are recorded in `EXP-001403`; the bundled-base-Python smoke replay is recorded in `EXP-001405`; the v0.1.21 coexistence-wording clarification, fresh compile, PDF QA, and finite-scope replay are recorded in `EXP-001406`; the paper-local ensemble identity audit and 24/24 artifact are recorded in `EXP-001407`; the analytic-dependency audit baseline and 28/28 artifact are recorded in `EXP-001409`; the chain-rule regularity repair and 30/30 artifact are recorded in `EXP-001411`; the fixed-charge closure repair and 31/31 artifact are recorded in `EXP-001412`; the paper-local 13/13 and 8/8 artifacts are recorded in `EXP-001396`--`EXP-001399`.

## Completion gates

- [x] Scope fixed to the hash-pinned P1/A2 functional on the side-16 torus.
- [x] R-157 and R-158 are stated as different variational problems.
- [x] Proof text has been synthesized into one manuscript source.
- [x] Existing primary and independent executable audits are identified.
- [x] R-157/R-158 integrated authority, artifact, PDF, legacy, and regression checks pass.
- [x] Internal adversarial proof-audit checklist and external-review questions recorded.
- [x] The `\mu>\mu_t` global-minimizer direct-method/coercivity step is explicit in the manuscript (external audit still required).
- [x] Functional data are self-contained in the manuscript: generators, internal matrices, density floor, and Class-II coefficient formulas are displayed explicitly.
- [x] The A2 energy identity now states the Gelfand-triple and Hilbert-space chain-rule hypotheses (external audit still required).
- [x] LaTeX compile and zero-overfull visual review (Tectonic exit 0; the
  16-page v0.1.39 A4 PDF was rendered in full and pages 1, 5, and 16 were
  inspected at full resolution on 2026-09-04).
- [x] Paper-local exact coercivity certificate and 13/13 self-test artifact recorded in `verification/runs/exact-coercivity.json`.
- [x] Paper-local Class-II source/sign audit and 8/8 exact one-mode artifact recorded in `verification/runs/classii-sign.json` (canonical source reconciliation remains open).
- [x] Standalone theorem statements are explicitly decoupled from H3; H3 is retained only as a provenance/transfer boundary (`EXP-001401`).
- [x] Bounded primary-source literature crosswalk expanded with explicit
  non-subsumption and residual-novelty boundaries, and the focused adjacent-source
  dispositions were added in `EXP-001421` (specialist review remains open).
- [x] Paper-local Fourier-multiplier realization records the Hermitian positive
  operator with `H^4` domain and `H^2` form domain (`EXP-001403`; external
  operator audit remains required).
- [x] Paper-local ensemble completion/Bregman/coexistence/witness identity audit
  records `24/24` exact checks in `verification/runs/ensemble-identity.json`
  (`EXP-001407`; auxiliary evidence, with no theorem-tier change).
- [x] Paper-local analytic-dependency audit records `50/50` exact structural checks
  in `verification/runs/analytic-dependency.json` (`EXP-001409`, `EXP-001411`,
  `EXP-001412`, `EXP-001414`, `EXP-001416`, `EXP-001430`, `EXP-001432`, `EXP-001435`, `EXP-001436`, and `EXP-001437`; it does not replace an external
  analytic proof audit or change theorem tier).
- [x] External-review handoff fixes the theorem questions, reproduction commands,
  signed response schema, and lifecycle firewall (`external-review-handoff.md`,
  `EXP-001410`; no external review is implied).
- [x] The Galerkin-limit proof text explicitly upgrades `\partial_tu` to
  `L^2_tL^2_x` before using the nonlinear energy chain rule (`EXP-001411`;
  external proof audit remains required).
- [x] The evolution theorem states `\partial_t\Psi\in L^2(0,T;L^2)` for
  every finite `T>0` and explicitly uses this to include the `s=0` energy-identity
  endpoint (`EXP-001437`; external proof audit remains required).
- [x] The R-158 direct-method proof explicitly states that the fixed-charge
  constraint is weakly closed via strong `L^2` convergence (`EXP-001412`;
  external proof audit remains required).
- [x] The A2 proof explicitly displays the coefficient/product H2-to-L2 local-Lipschitz estimate, the modewise Fourier-multiplier fractional-semigroup bound, the projected chain-rule limit, the endpoint-integrability estimate, and the periodic Moser tame bound (`EXP-001416`; external proof audit remains required).
- [x] The positive-time smoothing proof explicitly derives an H2 Hölder modulus by interpolation from the fractional-domain bound and the L2-time derivative estimate (`EXP-001426`; external proof audit remains required).
- [x] The positive-time smoothing proof explicitly states the shifted-base Sobolev bootstrap, endpoint cancellation in `X_m`, Hölder propagation, nested induction, the strict Hölder range, the split-kernel integral, and the endpoint semigroup factor plus the explicit interval/integral constants and temporal Banach-scale induction (`EXP-001430`, `EXP-001432`, `EXP-001435`, `EXP-001436`; external proof audit remains required).
- [x] A hash-pinned reproduction manifest records the package file hashes, audit artifact counts, manuscript-hash consistency, and expected replay commands (`verification/runs/reproduction-manifest.json`, `EXP-001419`; auxiliary integrity evidence only).
- [x] The four paper-local audits reproduce under the bundled base-Python runtime with unchanged artifact hashes (`EXP-001420`; portability evidence only).
- [x] Classify the unresolved canonical A2 v2.0 Class-II sign as a TECT/P1
  transfer-only gate; the standalone paper fixes the raw-Laplacian convention
  and does not depend on source intent.  Canonical reconciliation itself remains
  open under `EXP-001386`.
- [ ] Full proof audit by an independent mathematician.
- [ ] Specialist literature/novelty review and crosswalk update.
- [ ] Operator adversarial review and confirmation of the integrated referee package.
- [ ] Dedicated capstone PUBLISHED reproduction bundle for R-157/R-158.
- [x] The v0.1.39 package passes A2 `61/61`, R-157 `144/144`, R-158
  `155/155`, the non-bearing R-472 Lean replay `22/22`, paper-local
  `13/13`, `8/8`, `24/24`, `50/50`, and review-packet `20/20`, plus the
  reproduction manifest and 16-page rendered-PDF review (`EXP-001452`).
- [x] Post-EXP-001452 exploration/time verification, governed regeneration,
  and the complete repository release check pass at `EXP-001453`.
- [ ] Submission freeze/tag (requires separate explicit authorization).

## Non-claims

This draft is not a journal submission, does not assert publication readiness,
and does not claim that an external referee or the operator has confirmed the
new integrated package.  The existing claim cards and their registered tiers
remain authoritative.

## Version history

- `0.1.39` (2026-09-04): classified the unresolved canonical A2 Laplacian
  convention as a TECT/P1 transfer-only gate rather than an analytic premise or
  independent-paper submission gate.  The standalone functional, theorem
  statements, coefficients, and proofs are unchanged.  `EXP-001452` records
  the complete finite replay, `20/20` review-packet audit, passing manifest,
  and 16-page PDF review.  `EXP-001453` records the governed regeneration and
  complete repository release PASS.

- `0.1.38` (2026-09-04): added stable labels to all three main theorems, separated the external mathematical and specialist novelty decisions into two blank signed-review contracts, added a `19/19` hash/structure audit, exposed the omitted R-157 integrated verifier command, replayed all finite lanes, and visually reviewed the 16-page PDF. `EXP-001449` records the packet and replay; `EXP-001450` records governed regeneration and release PASS. No external response, source-owner decision, theorem expansion, or submission authorization is claimed.

- `0.1.0` (2026-09-03): initial integrated manuscript and audit package draft.
- `0.1.1` (2026-09-03): repaired the structured T-054 synchronization predicate, refreshed pinned verifier/child hashes, reproduced both integrated PASS lanes, and added the internal proof-audit checklist.
- `0.1.2` (2026-09-04): added the explicit direct-method coercivity and weak-lower-semicontinuity argument for the `\mu>\mu_t` minimizer claim; external audit remains open.
- `0.1.3` (2026-09-04): defined the full lower-order map `N=N_{\rm loc}+N_{\rm II}` used by the flow proof and repaired all missing `\qquad` controls found during PDF QA.
- `0.1.4` (2026-09-04): stated the Gelfand-triple/Hilbert-space chain-rule hypotheses for the exact energy identity; external audit remains open.
- `0.1.5` (2026-09-04): expanded the bounded primary-source literature crosswalk, added four related-work citations, compiled the 11-page PDF, and recorded `EXP-001375`; no theorem tier or scope changed.
- `0.1.6` (2026-09-04): made the declared functional self-contained by displaying the generators, internal data, density floor, and Class-II coefficient formulas; repaired the equation layout, recompiled the 11-page PDF with zero overfull boxes, and kept all theorem tiers and scope unchanged.
- `0.1.7` (2026-09-04): replaced the undefined spectral shorthand `D` by the explicit scalar symbol in the shell-bottom equation and unified `\varepsilon_M` notation; recompiled and rechecked the manuscript without changing theorem tiers or scope.
- `0.1.8` (2026-09-04): corrected the Class-II Euler--Lagrange leading sign and defined the nonlinear energy `\Phi` for the Gelfand-triple chain rule; recompiled and rechecked the 11-page PDF, recording `EXP-001379`, without changing theorem tiers or scope.
- `0.1.9` (2026-09-04): displayed the indexed Class-II Euler--Lagrange formula and coefficient tensor `C(u)` so the variation sign and order-two structure are directly auditable; recompiled and rechecked the 11-page PDF, recorded `EXP-001380`, resynchronized the non-bearing R-472 sidecar in `EXP-001381`, and changed no theorem tier or scope.
- `0.1.10` (2026-09-04): narrowed the ensemble transition wording to the proven coexistence and saturated charge `Q_*` at `\mu_t`; explicitly withheld a stronger global-charge jump claim for `\mu>\mu_t`, and queued independent review of the missing selection/stability step.
- `EXP-001386` (2026-09-04): opened a source-reconciliation gate for the Class-II principal-sign mismatch between the canonical A2 v2.0 note (`+B\nabla^2u`) and the paper/executable direct variation (`-B\nabla^2u`); no theorem tier or source hash changed.
- `0.1.11` (2026-09-04): made the v1.1/v2.0 sign discrepancy explicit in the manuscript and retained it as an external/operator reconciliation gate; no canonical source was edited.
- `0.1.12` (2026-09-04): added the constant-coefficient sign test and stated the conditional positive-Laplacian reading of the v2.0 shorthand while retaining source reconciliation as an open gate; no theorem tier or source hash changed.
- `0.1.13` (2026-09-04): defined the paper convention explicitly as the raw componentwise Laplacian and retained the conditional v2.0 positive-Laplacian reading as an open source gate; no theorem tier or source hash changed.
- `0.1.14` (2026-09-04): replaced the rounded Young coercivity offset by the exact rational 79507/7873200; canonical-source correction remained a separate gate.
- `0.1.15` (2026-09-04): replaced the decimal H2 coercivity infimum by the exact 1/5 negative-discriminant certificate and replayed the 12-page PDF and all A2/R-157/R-158 executable lanes, and added the 13/13 paper-local exact-coercivity artifact; no theorem tier or scope changed.
- `0.1.16` (2026-09-04): defined the graph-equivalent H2 norm, made the ensemble high-frequency estimate explicit, and stated the compact embedding used by the direct method; no theorem tier or scope changed.
- `0.1.17` (2026-09-04): added the explicit nearest-integer proof for the finite |n|^2=3 shell and replayed the 12-page PDF and all relevant executable lanes; no theorem tier or scope changed.
- `0.1.18` (2026-09-04): added the hash-pinned paper-local Class-II source/sign audit with an exact 8/8 one-mode certificate, recompiled the 12-page PDF, and reran the finite-scope A2/R-157/R-158 lanes; canonical source reconciliation remains open and no theorem tier or scope changed.
- `0.1.19` (2026-09-04): decoupled the standalone mathematical theorem statements from the optional H3 provenance hypothesis, recompiled the 12-page PDF, and reran the finite-scope lanes; H3 remains only a transfer boundary and no theorem tier or scope changed.
- `0.1.20` (2026-09-04): displayed the paper-local Fourier-multiplier realization with its Hermitian positivity bounds and `H^4`/`H^2` domains, recompiled and rendered the 12-page PDF, reran the finite-scope audits, and reproduced the paper-local audits under bundled base Python; no theorem tier or scope changed.
- `0.1.21` (2026-09-04): clarified the coexistence wording to exhibit only charges 0 and `Q_*` at `\mu_t`, recompiled and reran the finite-scope lanes, added the paper-local 24/24 ensemble-identity audit, and kept all theorem tiers and scope unchanged.
- `0.1.22` (2026-09-04): made the Galerkin-limit `L^2_tL^2_x` time-derivative upgrade explicit before the nonlinear chain rule, added two structural audit assertions, and replayed the analytic-dependency audit at 30/30; no theorem tier or scope change.
- `0.1.37` (2026-09-04): made the local mild contraction and continuation alternative quantitative, proved the Galerkin compactness step directly by Fourier tails and finite-mode time compactness, reduced the weakly singular Volterra estimate to ordinary Gronwall, added the theorem-applicability audit, replaced the broad compactness references by Simon's primary paper, expanded the structural audit to `50/50`, and visually reviewed a readable 16-page PDF with fifteen references. `EXP-001446` records the repair and `EXP-001447` the synchronized finite replay, manifest, rendered-PDF review, regeneration, and governed release PASS; theorem scope, tier, and all external gates remain unchanged.
- `0.1.36` (2026-09-04): made the projected Galerkin initial datum and initial-energy convergence explicit; inserted the spectral Hilbert-scale identity giving `C([0,T];H^2)`, initial-value preservation, and the quadratic chain rule through `s=0`; moved fixed-charge weak closure to the constrained direct-method argument; expanded the structural audit to `47/47`; compiled and visually reviewed a readable 16-page PDF with sixteen references. `EXP-001444` records the repair and `EXP-001445` the finite replay, manifest, PDF, and governed release PASS; theorem scope, tier, and all external gates remain unchanged.
- `0.1.35` (2026-09-04): added and compared the two 2026 Belin--Schneider quasilinear amplitude-theory sources, explicitly disclaimed novelty for quasilinear Swift--Hohenberg analysis or maximal-regularity handling, retained only the combined finite-torus residual proposition, and rebuilt the readable 15-page PDF with sixteen references; `EXP-001442` records the bounded comparison and `EXP-001443` the synchronized manifest and governed recheck; specialist review remains open.
- `0.1.34` (2026-09-04): compacted the bibliography into the 15-page PDF, removing the orphan final page while retaining all fourteen references and leaving theorem scope, tier, and external gates unchanged; `EXP-001440` records the layout repair; `EXP-001441` records the final manifest and governed recheck.
- `0.1.33` (2026-09-04): synchronized the manuscript status wording with the passing repository release check, clarified that external proof, novelty, operator, and capstone gates remain open, updated the external-review question for the `s=0` endpoint, and recorded the governed package recheck in `EXP-001439`; theorem scope, tier, and all external gates remain unchanged.
- `0.1.32` (2026-09-04): strengthened the evolution theorem's time-derivative class to `\partial_t\Psi\in L^2(0,T;L^2)` for every finite `T>0`, made the `s=0` energy-identity endpoint explicit, added the structural audit assertion, rebuilt and rendered the 15-page PDF, and replayed the finite package. `EXP-001437` records the repair and governed recheck; theorem scope, tier, and all external gates remain unchanged.
- `0.1.31` (2026-09-04): made the positive-time temporal regularity induction explicit with a Banach-scale $\mathcal F= L+N$ map, a $D^jN$ bound, and four-spatial-derivative-per-time-derivative bookkeeping; added the structural audit assertion, rebuilt and rendered the 15-page PDF, and replayed the finite package. `EXP-001436` records the repair and governed recheck; theorem scope, tier, and all external gates remain unchanged.
- `0.1.30` (2026-09-04): made the shifted-base endpoint estimate fully quantitative by displaying the interval conversion $h\le (b-a)^{1-\theta}h^\theta$ and the split-integral constant $1/\theta+1/(1-\theta)$; added the corresponding structural audit assertion, rebuilt and rendered the 15-page PDF, and replayed the finite package. `EXP-001435` records the repair and governed recheck; theorem scope, tier, and all external gates remain unchanged.
- `0.1.29` (2026-09-04): expanded the shifted-base endpoint proof with the full $C^\theta$ norm, strict $0<\theta<1$ range, split-kernel integral, and endpoint semigroup factor; added two structural audit assertions, recompiled and rendered the 15-page PDF, and kept theorem scope and tier unchanged; `EXP-001432` records the repair and governed recheck, while external proof and source-sign gates remain open.
- `0.1.28` (2026-09-04): made the shifted-base Sobolev bootstrap, endpoint cancellation, Hölder propagation, and nested induction explicit, added one structural audit assertion, recompiled and rendered the 15-page PDF, and kept theorem scope and tier unchanged; external proof and source-sign gates remain open.
- `0.1.27` (2026-09-04): made the positive-time $H^2$ Hölder interpolation and time-modulus used by endpoint cancellation explicit, added one structural audit assertion, recompiled and rendered the 14-page PDF, and kept theorem scope and tier unchanged; external proof and source-sign gates remain open.
- `0.1.26` (2026-09-04): added four focused primary-source non-subsumption dispositions and matching related-work citations; recompiled and rendered the 14-page PDF; no theorem tier or scope change, and specialist novelty review remains open.
- `0.1.25` (2026-09-04): made the projected chain-rule limit, endpoint-integrability estimate, and periodic Moser tame bound explicit, added four structural audit assertions, and replayed the analytic-dependency audit at 37/37; no theorem tier or scope change.
- `0.1.24` (2026-09-04): made the H2-to-L2 local-Lipschitz product estimate and Fourier-multiplier fractional-semigroup bound explicit, added two structural audit assertions, and replayed the analytic-dependency audit at 33/33; no theorem tier or scope change.
- `0.1.23` (2026-09-04): made weak closure of the fixed-charge constraint explicit in the direct-method proof, added one structural audit assertion, and replayed the analytic-dependency audit at 31/31; no theorem tier or scope change.
- Post-PAH release checkpoint (2026-09-04): appended temporal correction `TC-0013`, refreshed generated surfaces, and recorded clean `release_check.py` output in `EXP-001408`; lifecycle remains `draft`.
- Final v0.1.25 release recheck (2026-09-04): refreshed generated catalog and governed projections after `EXP-001416`; `release_check.py` passed at `EXP-001417`, with lifecycle still `draft` and external gates open.
- Post-PDF catalog repair (2026-09-04): a deterministic PDF rebuild exposed one stale catalog shard; `regen_all.py` repaired the projection and the subsequent release check passed, recorded in `EXP-001418`; lifecycle remains `draft`.
- Focused literature checkpoint (2026-09-04): added four adjacent primary-source dispositions, matching citations, and the v0.1.26 manuscript/PDF update; `EXP-001421`--`EXP-001422` record the bounded non-subsumption result and replay, while `TC-0014` marks only the retained future wall-clock field as unknown.
- Final v0.1.26 release checkpoint (2026-09-04): refreshed generated surfaces after the literature/manuscript update and recorded the governed `release_check.py` PASS in `EXP-001423`; lifecycle remains `draft`.
- Reproduction-package checkpoint (2026-09-04): added the hash-pinned file/audit manifest `verification/runs/reproduction-manifest.json`; no theorem scope or tier changed.
- Structural proof-dependency checkpoint (2026-09-04): added the independent 28/28 analytic-dependency audit and bundled-runtime replay in `EXP-001409`; external proof and operator gates remain open.
- External-review checkpoint (2026-09-04): added the signed-review handoff protocol in `EXP-001410`; lifecycle remains `draft` until responses and operator confirmation exist.
- QA checkpoint for `0.1.0` (2026-09-03): fixed the chain-rule integral notation, compiled the
  ten-page PDF, and completed the rendered-page visual review.
