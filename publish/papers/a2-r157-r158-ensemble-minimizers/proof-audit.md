# Proof-audit record — A2/R-157/R-158

Status: `INTERNAL-AUDIT-DRAFT` (2026-09-04).  This document is a structured
adversarial checklist for an eventual independent mathematician.  It is not
an external referee report, an operator sign-off, or a claim-tier promotion.

## Audit scope

The audit covers the explicitly declared side-16 periodic three-torus,
six-real-component field, positive density floor, pinned coefficients, and
`eta_shell=0` functional in `manuscript.tex`.  Version 0.1.38 retains the closest 2026 Belin--Schneider quasilinear amplitude-theory comparison, narrows the residual novelty boundary, and retains the three embedded Hermitian generators, internal matrix
data, density floor, and Class-II coefficient formulas; it also displays the
indexed Class-II Euler--Lagrange formula and coefficient tensor so the order-two
map, variation sign, and normalization can be checked without a private backend.
It realizes the declared fourth-order linear part as a modewise Hermitian positive
Fourier multiplier with operator domain `H^4` and form domain `H^2`.  The declared
functional and shell bottom remain reconstructible from the source.  The external
review questions and signed response protocol are consolidated in
`external-review-handoff.md`; the hypothesis-by-hypothesis analytic theorem map is `theorem-applicability-audit.md`; the exact canonical Class-II sign alternatives
and source-owner response schema are fixed in `source-sign-reconciliation.md` as
a transfer-only gate; no external response has yet been received.
It does not audit a removed
regulariser, a historical backend, a thermodynamic or continuum limit, a
quantum/KMS construction, a physical charge, a physical vacuum, BCC selection,
or any Sector-A interpretation.

The source claims are `A2-FULL-PRODUCTION-WELLPOSED`, `R-157`, and `R-158`.
`R-472` is an assurance-only exact/Lean sidecar and is not load-bearing.

Version 0.1.39 changes only the gate classification: the canonical A2 source
sign remains open for TECT/P1 transfer but is not a premise of the explicitly
defined standalone theorem.  `EXP-001452` records the unchanged finite results,
the `22/22` packet audit, passing manifest, and 16-page PDF review;
`EXP-001453` records the governed regeneration and repository release PASS.

## Theorem-by-theorem checklist

| item | proof obligation | current evidence | internal disposition | external review |
|---|---|---|---|---|
| A2-1 | The fourth-order symbol is positive and the form domain is `H^2`, operator domain `H^4`. | `manuscript.tex`, Sec. 4.1; A2 full-production audits | exact constants and operator statement are recorded; the manuscript now defines the graph-equivalent H2 norm, proves the explicit 1/5 lower bound by a negative discriminant, and realizes the modewise Hermitian positive multiplier with operator domain `H^4` and form domain `H^2`, independently replayed by `verification/exact_coercivity_audit.py` (13/13); the paper-local source/sign audit also passes 8/8 with source hashes recorded, while canonical sign intent remains open | required: check self-adjoint realization and norm equivalence |
| A2-2 | The regularised Class-II Euler map has order two and is locally Lipschitz `H^2 -> L^2`. | `manuscript.tex`, Sec. 4.2; nonlinear-mapping audit; explicit `N=N_loc+N_II` definition and indexed Eq. `eq:euler-classii` | the integration-by-parts sign, component formula, coefficient tensor, and full lower-order map are displayed; the coefficient/product H2-to-L2 local-Lipschitz estimate is now written explicitly, while the product exponents and coefficient dependence remain subject to external verification. `EXP-001386` records the separate canonical-transfer discrepancy, and `EXP-001388` narrows it to a possible undocumented positive-Laplacian shorthand. | required for the paper: verify every product exponent, coefficient dependence, denominator derivative, and the raw-Laplacian sign; separately required for canonical transfer: decide whether the canonical note needs an authorized erratum |
| A2-3 | Analytic-semigroup mild theory gives local existence and continuation. | `manuscript.tex`, Sec. 4.2; A2 wrapper; paper-local analytic-dependency audit `50/50` | the multiplier, Duhamel map, `T^{1/2}` contraction, and continuation alternative are displayed directly; structural presence is checked | required: check sectorial hypotheses and the singular-kernel contraction |
| A2-4 | Galerkin solutions pass to a global weak/strong solution and satisfy the exact energy identity. | `manuscript.tex`, Sec. 4.3; energy-continuation audit; explicit Gelfand-triple/Hilbert-space chain-rule statement; analytic-dependency audit `50/50` | Fourier high-mode tails, finite-mode `H^1_t` compactness, the diagonal strong-convergence argument, and chain-rule prerequisites are displayed and structurally checked, including the explicit Galerkin-limit `L^2_tL^2_x` time-derivative upgrade on every finite interval, its `s=0` energy-identity endpoint control, and the weak closure of the fixed-charge constraint; the analytic passage is not machine-proved | required: audit projection, compactness, and chain-rule passage |
| A2-5 | Endpoint Duhamel cancellation yields `H^4` for positive time and Moser iteration yields smoothness. | `manuscript.tex`, Sec. 4.4; smoothing audit; analytic-dependency audit `50/50` | positive-time Hölder interpolation and the shifted-base endpoint bootstrap are now explicit structural dependencies, including the strict $0<\theta<1$ range, split-kernel integral, full $C^\theta$ norm, and endpoint semigroup factor; cancellation, Hölder propagation, and iteration remain subject to signed review | required: verify endpoint integrability, shifted-base domain, Hölder estimate, and iteration domains |
| A2-6 | Uniqueness and finite-time continuous dependence hold in `H^2`. | `manuscript.tex`, Secs. 4.2 and 4.4 | the kernel is iterated twice, `k*k=pi` is evaluated, and the estimate is reduced to ordinary Gronwall | required: check common energy ball and time-uniform constants |
| R-157-1 | Exact quadratic/polynomial completion gives `F >= g ||Psi||_2^2`, with `g>1/8`. | R-157 primary `26/26`, independent `24/24`, integrated `144/144` | PASS at declared finite scope | required: independently recompute coefficient matching and equality case |
| R-157-2 | The Class-II radial derivative matrix is positive for every `theta in [0,1]`. | exact rational primary/independent lanes | PASS; concave determinant endpoint test | required: check scaling from `y=t^2` and floor derivative |
| R-157-3 | No nonzero critical point exists and the canonical flow decays exponentially. | R-157 integrated result and manuscript Sec. 5 | PASS at declared unconstrained scope | required: verify differentiability along rays and decay identity |
| R-158-1 | The finite-torus spectral bottom lies on the `|n|^2=3` shell. | R-158 primary/independent lanes | PASS with exact Sturm and rational `pi` enclosure | required: check integer-shell comparison and internal eigenvalue isolation |
| R-158-2 | The polynomial/Bregman decomposition is nonnegative and plane-wave saturation is exact. | R-158 primary/independent lanes; paper-local ensemble identity audit `24/24`; manuscript Sec. 6 | PASS for `Q/|T| >= rho_*`; below `Q_*` intentionally not claimed | required: audit constraint normalization and equality conditions |
| R-158-3 | The imposed grand potential has zero/nonzero coexistence at `mu_t` and strict ordering with the saddle-node and linear spinodal. | R-158 integrated `155/155`, R-157/A2 regression, and the explicit direct-method paragraph in `manuscript.tex` | PASS for the imposed mathematical ensemble; direct-method coercivity and weak lower semicontinuity are now stated. Version 0.1.17 limits the charge statement to the saturated value `Q_*` at `mu_t`; it does not claim the exact charge of every global minimizer for `mu>mu_t`. | required: verify the high-frequency coercivity split, polynomial absorption, first-order terminology, and whether any stronger one-sided charge jump needs a separate selection/stability proof |

## Cross-cutting adversarial questions

1. **Could the optional H3 provenance hypothesis be silently treated as an
   analytic premise or an unconditional physical law?**  No.  The manuscript
   states the theorems for the explicit functional and uses H3 only to delimit
   any transfer to the canonical P1 interpretation.
2. **Could R-158's nonzero plane wave be reported as an R-157 equilibrium?**
   No.  Section 6.3 distinguishes `D F(Psi_*) = mu_t Psi_*` from
   `D F(Psi_*) = 0` and records that the original neutral energy remains higher
   or equal in the stated direction.
3. **Could executable PASS counts be mistaken for analytic proof?**  No.  The
   verification section explicitly says that semigroup, compactness, chain
   rule, and literature steps remain proof-text obligations.
4. **Could finite shell coexistence be promoted to infinite-volume or BCC
   selection?**  No.  The scope and falsifier sections exclude both.
5. **Could the positive density floor be removed without changing the theorem?**
   No.  Its removal is explicitly a different theorem and is outside scope.

6. **Could the bounded literature search be mistaken for a novelty or priority proof?**
   No.  It records only primary-source applicability dispositions and an explicit
   residual proposition; specialist review and broader database coverage remain
   required.

7. **Could the printed constants be confused with independently verified
normalizations?**  No.  The formulas, matrices, indexed first variation, and
coefficient tensor are now visible in the paper, but their self-adjoint,
Hermitian, and coefficient-normalization consequences remain explicit questions
for the external audit.

8. **Could the saturated value $Q_*$ at coexistence be misread as the charge of
 every global minimizer for every $\mu>\mu_t$?**  No.  Version 0.1.17 states
 only the coexistence value and leaves branch selection or a one-sided global
 charge theorem as an open external-review question.

9. **Could the paper silently diverge from the registered A2 source convention?**
 No.  `EXP-001386` names the canonical-note `+B\nabla^2u` versus
 executable/paper `-B\nabla^2u` discrepancy.  `EXP-001388` shows that the
 displays are compatible only if the v2.0 symbol denotes `-Delta`, but v2.0
 does not define that symbol; promotion remains blocked until an independent
 mathematician and the operator reconcile it.

## Required external review questions

An independent mathematician should either answer these questions in writing
or identify a precise repair:

* Is the displayed indexed Class-II first variation (including the tensor
  `C(u)`) well-defined as an `L^2` map on the stated `H^2` domain, including all
  denominator derivatives and the integration-by-parts sign, and how does it
  reconcile with the opposite principal sign printed in the canonical A2 v2.0
  note?
* Do the claimed semigroup and quasilinear estimates apply to the exact
  self-adjoint fourth-order operator with the displayed domains?
* Does the Galerkin/Aubin–Lions argument provide the stated strong convergence
  and justify the nonlinear chain rule on every finite interval including the
  `s=0` energy endpoint without an unlisted time-regularity hypothesis?
* Is the endpoint cancellation formula valid with the stated Hölder modulus,
  and does its iteration really imply `C^infty` positive-time regularity?
* Are the equality cases in the neutral completion and the ensemble Bregman
  completion exactly as claimed, including the finite-volume normalization?
* Does the global-minimizer argument for `mu>mu_t` use a coercivity statement
  strong enough to prevent loss of mass on the fixed torus?
* Do the displayed generator matrices, internal projection, density floor, and
  Class-II coefficient formulas match the canonical A2/P1 normalization and
  preserve the stated Hermitian and positive-definite properties?

## Current acceptance decision

The repository-local executable and exact-arithmetic gates are passing, and the
two former integrated record failures were repaired in verifier v1.0.2 and
recorded as `EXP-001372`.  The bounded primary-source literature expansion
recorded as `EXP-001375` improves the crosswalk but does not establish novelty
or replace specialist review.  The v0.1.8 sign, nonlinear-energy, and self-contained spectral repairs, followed
by the v0.1.9 indexed Euler--Lagrange/tensor display, the v0.1.10
charge-jump wording correction recorded in `EXP-001382`, and the source-sign
reconciliation gate in `EXP-001386` together with the convention analysis in
`EXP-001388`, the exact Young-constant repair in `EXP-001392`, the exact H2 coercivity certificate in `EXP-001395`, the paper-local source/sign audit in `EXP-001399`, and the full finite-scope replay in `EXP-001400`, improve auditability but do
not close the analytic proof audit; the sign/Phi repairs and indexed-variation
follow-up are recorded as `EXP-001379` and `EXP-001380`.  The non-bearing R-472
sidecar hash resynchronization is recorded as `EXP-001381` and its fresh replay
passes.  The historical release recheck `EXP-001391` exited 1 while the PAH writer was live; it is superseded for current repository state by the clean checkpoints `EXP-001408` and `EXP-001415`, with the latter recording the final v0.1.24 `release_check.py` exit 0 after generated-surface refresh; the current pre-literature v0.1.25 checkpoint is `EXP-001417`; the focused-source expansion is `EXP-001421` and the v0.1.26 manuscript update is `EXP-001422` (with temporal provenance correction `TC-0014`); `EXP-001423` records the prior v0.1.26 governed release recheck; `EXP-001425` records the source-sign decision aid, `EXP-001426` records the v0.1.27 Hölder proof-text repair, and `EXP-001430` records the v0.1.28 shifted-base proof repair and `EXP-001432` records the v0.1.29 endpoint-estimate repair, while `EXP-001435` records the v0.1.30 explicit endpoint-constant repair and `EXP-001436` records the v0.1.31 temporal-bootstrap repair and subsequent governed release recheck.  This remains separate from the paper theorem evidence.  The current manuscript version (v0.1.38, with the `EXP-001442` closest-source update, source-convention disclosure,
paper-local source/sign and ensemble-identity audits, theorem/provenance separation, convention-narrowing analysis, H2 replay, shell-selection clarification, Fourier-multiplier realization, explicit local-Lipschitz and fractional-semigroup proof dependencies, shifted-base endpoint bootstrap,
and full finite-scope replay recorded in `EXP-001387`--`EXP-001414`)
remains a presentation refinement
with no tier or scope change.
This is sufficient to advance the package from
`REPRODUCTION-SYNC-OPEN` to `INTERNAL-AUDIT-READY`; it is not sufficient to
mark the paper `internal-review`, `submitted`, or `published`.

The paper-local analytic-dependency audit in `EXP-001409` independently reconstructs the displayed necessary exponent and compactness prerequisites and rejects four hostile premise mutations; the follow-up `EXP-001411` adds explicit checks for the Galerkin-limit `L^2_tL^2_x` time-derivative upgrade and the valid Hilbert-pivot pairing, while `EXP-001412` adds the weak closure of the fixed-charge constraint, the fixed-charge closure repair, `EXP-001414` adds the explicit local-Lipschitz and fractional-semigroup dependencies, and `EXP-001416` adds the projected chain-rule limit, endpoint-integrability estimate, periodic Moser tame bound, and their structural assertions, bringing the current artifact to 50/50 after the positive-time $H^2$ Hölder interpolation check in `EXP-001426`, the shifted-base bootstrap check in `EXP-001430`, the endpoint-estimate checks in `EXP-001432`, the explicit interval/integral constant check in `EXP-001435`, and the temporal Banach-scale induction check in `EXP-001436`, and the finite-interval derivative endpoint check in `EXP-001437`.  These are auxiliary structural checks, not a signed proof.  The signed external-review request and routing template are in `external-review-handoff.md`; the blank theorem-level response contract is `independent-proof-review-form.md`, and the separate literature contract is `specialist-novelty-review-form.md`. Their structural completeness does not constitute a signed response. The original handoff is recorded in `EXP-001410`.  The following remain open by design: canonical A2 sign reconciliation
(`EXP-001386`), an independent mathematician's signed proof audit, specialist
novelty/literature review, operator adversarial confirmation, and the operator-gated
PUBLISHED capstone bundle.  The preceding v0.1.36 finite replay, manifest, PDF and governed release recheck pass at `EXP-001445`; the v0.1.37 direct-analytic proof and applicability-audit repair is recorded in `EXP-001446`, and its complete finite replay, manifest, rendered-PDF review, regeneration, and governed release PASS are recorded in `EXP-001447` after the proof-text repair in `EXP-001444` and provenance-only correction `TC-0015`; the v0.1.38 stable-theorem-label and blank signed-review-contract packet, `19/19` structural audit, complete finite replay, and rendered-PDF review are recorded in `EXP-001449`, with governed regeneration and release PASS in `EXP-001450`; the preceding v0.1.35 checkpoint is `EXP-001443` after the closest-source update in `EXP-001442`; `EXP-001441` is the preceding v0.1.34 checkpoint, `EXP-001440` records its bibliography layout repair, and `EXP-001439` the v0.1.33 repository-status synchronization; `EXP-001435` records the preceding v0.1.30 endpoint-constant checkpoint and `EXP-001432` the v0.1.29 endpoint-estimate checkpoint; `EXP-001418` records the historical transient post-PDF catalog-staleness repair, and the check must be rerun after any later source or generated-surface change.  The external audit must also decide whether a
full one-sided global-charge discontinuity can be proved from the current
ensemble estimates or must remain outside scope.  Any objection from those reviews must be recorded
here and in the appropriate governed ledger before the lifecycle advances.

Gate classification clarification (v0.1.39): the independent-paper gates are
the signed mathematical audit, specialist novelty review, operator adversarial
confirmation, and capstone package.  The unresolved canonical A2 sign is a
separate TECT/P1 transfer gate, because the standalone manuscript prints its
functional and raw-Laplacian convention explicitly.  It must be resolved before
canonical transfer, but it is not an analytic premise or submission gate for
the independent mathematical paper.
