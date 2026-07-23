# TECT 6-Stage Roadmap — v2

**Issued**: 2026-06-05 · **Source of stage definitions**: GOVERNANCE.md
**Current-status source**: live `claims/*/status.json`, rendered `CLAIMS.md`,
`RESULTS-LEDGER.md`, and `TODO.md`. The legacy `TOE-FACT-SHEET.md` snapshot is
bootstrap provenance only and is not a current-status authority.

Stages are sequential in their exit conditions but parallel in day-to-day work.
A stage is closed only when its exit condition is met at the stated tier with a
verification package. The publication-complete deliverable of each claim is a
self-contained referee **reproduction bundle** (note + reproducible code + environment
+ expected output + hashes + README), per `governance/reproduction-bundle-policy.md`
(binding 2026-06-10); reference instance `claims/B1-RH-ENUM/Reading-H/bundle/reading-h-cfull-260610/`.

---

## Stage 0 — Repository bootstrap & migration (meta-stage, NEW)

**Goal**: this repository becomes the single canonical record; the legacy corpus
is migrated pull-based and re-validated.

**Close**: governance docs in force; claim ledger seeded and linted; CI running
`lint_claims.py`; migration ledger active; legacy repo frozen as read-only
reference.

**Exit condition**: every claim cited by any P2 artefact has its evidence
migrated out of `legacy:` pointers.

**Status 2026-06-05**: IN PROGRESS (this commit bootstraps the structure).

## Stage 1 — Define the microscopic theory (Sector A)

**Goal**: $\mathcal F_{\rm TECT}$ is fixed — fields, kernel, regularisation,
counterterms, PDE well-posedness.

**Exit condition**: no convention ambiguity remains; the convention registry is
the single normative source.

**Status — Sector A refreshed 2026-07-22**: the convention and exact kernel
identity are fixed, with `r_zero` and `mu2_shell` kept distinct. The canonical
full-production branch is

```text
A1-PRODUCTION-FUNCTIONAL-REALISATION (scoped T5)
  -> A2-FULL-PRODUCTION-WELLPOSED (conditional T6)
  -> A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM (conditional T6).
```

The separate scalar-continuum branch contains the positive scalar kernel,
order-by-order perturbative cutoff removal, and the finite-volume scalar
constructive measure at T6. `A5-SECTOR-A-SYNTHESIS` is a PUBLISHED T6
conditional-composition theorem under exactly seven named hypotheses; it
preserves the scalar/full functional fork and the `0.005` versus
`0.260000000009475` shell-mass fork.

The binding reviewer hierarchy is
`governance/sector-a-theorem-map.json`: 21 immutable Sector-A claim cards are
classified into five theorem families. The A6--A13 cards form one full
derivative Class-II constructive-measure programme, not eight peer-level
Sector-A endpoint theorems. A7 is its long-term theorem anchor and A13 is its
current subproof host. New coefficient-jet and one-use work remains under
A13; any A14+ claim requires a separate independent-capstone decision.

The remaining Stage-1 frontier is not another full variational/PDE closure.
`A6-CLASSII-UV-POWER-COUNTING` records at T4 that the bare full derivative
Class-II Gaussian energy has a positive linear cutoff contraction.
`A6-CLASSII-K-COMPOSITE-DEFINITION` closes at scoped T5 the fixed-floor
canonical geometric `K_A` current within the declared common real-even scalar
spectral regulator class. `A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE` now closes
at scoped T5 the exact covariance-normal-ordered joint `J^2`, `J*K`, and `K^2`
energy composite and its `L2(Omega;H^(-1-kappa))` continuum limit. The same
split review eliminates literal fixed-parameter `-delta_cube*N*W_eps`
subtraction as a uniform-coercivity route and exhibits a pathwise Class-II
plane-wave null with `W_eps>0`. `A8-CLASSII-DECOUPLED-NELSON-BOUND` closes a
separate scoped T5 control theorem: arbitrary deterministic spatial PSD
backgrounds satisfy a cutoff-uniform `det_2`/Schatten estimate, and independent
Gaussian coefficient and derivative fields have all fixed-p Nelson moments and
a full-sequence finite-volume product-measure limit. The required `M_R^4`
regulator factor is explicit. This does not identify the two Gaussian fields.
`A9-CLASSII-SMART-PATH-CANCELLATION` then closes at scoped T5 the exact
independent-to-self-coupled interpolation algebra, removes the apparent
Schatten-1 terms, and proves an arbitrary-source noncentral frozen-shell bound
with summable `2^(-j)` cost. The 2026-07-21 resonant-ray audit falsifies the
former commutator-alone infinitesimal form-bound follow-up: the commutator,
entropy, and sextic terms share the same `K^6` scaling under an admissible
covariance-contracted Gaussian tilt with a Cameron--Martin mean. This does not
withdraw A9 T5, because the
discarded covariance-normal frozen term has positive source energy on the
witness. The later `A10-CLASSII-RELATIVE-COMMUTATOR-REDUCTION` fixes that
successor problem at T4 structural depth. It proves the exact action mismatch
and closes a sharp rectangular-cube filtration subgate. The follow-up
`A11-CLASSII-TRUE-INCREMENT-DETERMINANT-REDUCTION` proves that the direct
past-energy upper form is impossible already at the base Gaussian, retires
that branch, and exactly reconstructs the endpoint with
`I_j=Q_j^fr-q_(B(phi_(j-1)))(D phi_(j-1))`. The finite-cutoff noncentral
determinant is closed, but it contains a positive adapted source-square. The
new `A12-CLASSII-SOURCE-SQUARE-REDUCTION` proves the cutoff-uniform analytic
bound with the sharp Pauli/Fierz coefficient and exact one-leg shell decay.
Its constant is
`C_src=0.016570372383568618 M_R^2 M_6^4 Q_6^2`. The proposed separated
enclosure is now closed negatively: dyadic Riesz boundary modulation gives
`M_6>=8`, `Q_6>=8sqrt(3)`, and `M_6^4Q_6^2>=786432`, while the isolated target
was `29.62571266025876`. The coefficient-blind scalar six-linear route fails
on the same witness. A13 then restores the exact coefficient and proves
separate local doublet/singlet phase nulls plus the output-shell commutator.
Its opposite-corner SU(2) polynomial nevertheless gives
`C_rel>0.9>gamma/3=0.54`; the determinant resolvent tends to the identity on
that carrier. Thus T-049 is also closed negatively. The corrected joint-source v1.1
package now reduces, but does not close, the broad joint log-Laplace gate:
exact principal-symbol source doubling gives an asymptotic factor four on the
registered carrier and refutes coefficient-one conditioning plus the
precisely scoped finite-bank local Bellman class. The terminal/past split and
one-shell crossover leave a nonlocal full-action route. Exact
Boue--Dupuis analysis makes the candidate one-use inequality equivalent to
the still-open `q=10/9` Nelson moment. A coefficient-blind endpoint-only
timewise Young enclosure and the direct nonfrozen one-shot Ramer map at
`t=5/9` are now also closed negatively; the latter has a production
determinant sign change near amplitude `3.49230586`. The sole canonical
objective remains `A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE`, which must
spend Cameron--Martin energy once and retain a signed global cancellation.
The translation-model reduction now proves the flexible sufficient field
range `epsilon_6<gamma/6`, the exact finite-cutoff translation and Cartan
identities, and deterministic-shift expectation positivity.  It also shows
that A7's contracted `L^2` composite does not supply the universal translated
model.  `A13-CLASSII-UNIVERSAL-Q-ALL-MOMENTS-AND-CM-TRANSLATION` now closes
the centered tensor in every finite `Lp(H^(-1-kappa))` and its deterministic
`H2` translation.  Adversarial analysis refutes the literal full-product jet
reading in the required `L2` model topology.  A cone-localized subdiagram of
the unnormalised nested resonance has a fixed negative coefficient whose
magnitude accumulates like `c log Lambda`; this shows that lower-chaos terms
cannot be omitted, but it does not prove noncancellation of the total
symmetric tree. The finite-cutoff forest theorem classifies the exact
`2`, `4+2`, `5+2`, and `3+0` contractions for both complete non-aliased
sharp-cube parenthesisations. Entrywise parity of the six-real A1 covariance
makes all complete-sector value--derivative and double-cross terms cancel,
while raw `XXQ` retains the finite tensor `Sigma_Lambda Q_Lambda`. This does
not improve the literal full-product regularity.
`A13-CLASSII-BALANCED-COEFFICIENT-JET-CONTINUUM-AND-A7-RECONSTRUCTION`
now closes the coefficient-jet and parent model-lift gates at scoped T4. Its
high-against-root-shell `P3/P4` variances obey `<n>^(-2+epsilon)` and
`<n>^(-3+epsilon)`; the coupled-cutoff limits exist in every finite moment at
the target Sobolev orders. An exact second-order chart reconstructs the full
rational translated coefficient in the A7 covariance-normal scheme, retaining
every grouped lower chaos and finite `Sigma Q`. `A13-CLASSII-STRICT-PAST-RESOLVENT-SIGNED-CHARGE-REDUCTION` now closes
the causal/PSD completion at scoped T4. It derives `q=10/9` from the one-use
control allocation and reduces the remaining problem exactly to
`sum_j[(q/2)<ell_j,(I+qT_j)^(-1)ell_j>-C_j]`.
The joint-score continuation now replaces the separated charge by the exact
center `ell_j+m_j`, recovers factor four, and derives the conditional
heat-current identity while refuting shellwise positivity of `C_j`. The
backward-heat continuation keeps the completed square inside the exact Gibbs
charge and constructs a terminal-backward Doob coefficient. Its controlled
telescope removes the apparent order-one heat drift before inequalities;
the finite low block and high covariance-trace channels are below arbitrary
budgets for regular mutually orthogonal one-shot controls. The current child
is `A13-CLASSII-AVERAGED-RAW-CURRENT-CARTAN-JACOBI-FORM-BOUND`, which must
bound the global raw-current secant with its positive square retained and then
extend the result to the declared finite-energy control class.
The historical `A11-CLASSII-TRUE-INCREMENT-STABILISED-LOG-LAPLACE` formulation
is blocked pending that redesign. The separate
branch-aware bare-concentration theorem also remains open. Parameter identity,
regulariser removal, infinite volume, phase transition, BCC, and T7 remain
outside the current Sector-A theorem.

## Stage 2 — Prove the vacuum (Sector B) ← **critical path**

**Goal**: $\mathcal R_H=\operatorname{arg\,min}_{\mathcal A_{\rm adm}}F_{\rm TECT}$.

**Exit condition**: GAP-1 closed (admissible-class minimiser theorem) and GAP-2
closed (estimator → controlled error bound), i.e. Reading-H selection at T6
without estimator-only inputs.

**Status 2026-06-05** (operator verdict, Math442):
- Reading-H selection: **T5 CLOSED@ESTIMATOR-GRADE** within enumerated
  single-shell and two-shell condensate ensembles at $r_{\rm braz}=\mu^2=0.005$
  (claim `B1-RH-ENUM`).
- Proposition A: **T6 CERTIFIED** conditional on {H-layer, H-A0} via dual
  independent audit + operator sign-off (claim `B2-PROPA-HLAYER`).
- **Step-5b (beyond-layer class-wide bound) is THE gateway** for any
  whole-Reading-H T6 discussion. No unilateral promotion.

**Open gates** (see `claims/GATES.md`): STEP-5B, G3PB-III (higher-shell /
anisotropic harmonic dominance, AddF ratio extraction), ESTIMATOR-UPGRADE
(GAP-2), open-neighbourhood robustness in $\mu^2$.

## Stage 3 — Derive the IR field theory (Sector C)

**Goal**: TECT IR → Lorentz + gauge + gravity effective theory.

**Exit condition**: Lorentz attractor, spin-2 mode, Einstein–Hilbert limit,
gauge connection — each at T6+ with verification packages.

**Status**: kinematic Lorentz T6 (H-suppression hypothesis, `C1-LORENTZ-KIN`);
emergent Lorentz isotropy legacy-PROVED via 1-loop interval enclosure, enters
as T6/T7-candidate pending verification package (`C2-LORENTZ-EMERGENT`);
equivalence principle likewise (`C3-EP`); gravity sector CLOSED@1-loop = T5
(`C4-GRAVITY-1LOOP`); Newton $G$ relation derived / value matched / not yet
predicted (`C5-NEWTON-G`, T6/T7-SPLIT management).

## Stage 4 — Derive matter and quantum structure (Sector D)

**Goal**: SM matter spectrum and quantum rules emerge — families, chirality,
anomalies, quantisation, fermion masses.

**Status**: SO(10)/bundle emergence T6 conditional (`D1-SO10-BUNDLE`);
gauge-group forcing T3 after the Math245 audit-rollback (`D2-GAUGE-FORCING`);
chirality legacy-PROVED → T6/T7-candidate (`D3-CHIRALITY`); quantum consistency
PROVED per-generation = T5 pinned, CP/unitarity gates open
(`D4-QUANTUM-CONSISTENCY`). Sector-D tiers are capped while GAP-1 is open
(gauge/matter topology may depend on vacuum selection).

## Stage 5 — Compute constants and cosmology (Sectors E, F)

**Goal**: TECT predicts or tightly constrains $G$, $\Lambda$, $m_i$,
$\theta_{\rm CKM}$, $\theta_{\rm PMNS}$, $\Omega_{\rm DM}$.

**Exit condition**: GAP-3 closed — every number labelled
derived / matched / inserted / predicted; at least one entry moves to
PREDICTED with a pre-registered freeze.

**Status**: Higgs/EW scale T4 (`E1-HIGGS-EW`); origin of $\hbar$ — classical
routes REFUTED (8 failed routes), phase-transition origin programme T2
(`E2-HBAR-ORIGIN`); cosmological sector T4 programme (`F1-COSMO-DARK-SECTOR`).
Prediction ledger seeded in `predictions/prediction-ledger.md` (all entries
OPEN or SCAFFOLD; none official yet).

## Stage 6 — Robustness, falsifiability, publication

**Goal**: no hidden assumption, no circular parameter fixing, at least one
falsifiable prediction; external review.

**Close**: independent audit; negative-result registry active; parameter-
neighbourhood robustness; observational tests; Minimal Review Packets A–D
released through `publish/`.

**Packets** (target order):
A — Vacuum selection ($\mathcal R_H$ vs ordered condensates);
B — BCC/Brazovskii structural selection;
C — Newton $G$ relation (relation derived, value not independently predicted);
D — Gauge/matter topology.

---

## Current priority view (refreshed 2026-07-23)

The live task source is `TODO.md`; historical 2026-06-05 priorities are
preserved in git/changelog rather than treated as current gates.

1. **Repository control task T-006** — finish code-discipline automation.
2. **A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE** — the broad joint gate is
   `REDUCED-NOT-CLOSED`. Exact principal-symbol doubling produces an
   asymptotic factor four on the relative-phase carrier and excludes the
   coefficient-one and precisely scoped finite-bank local Bellman routes.
   v1.1 also excludes coefficient-blind endpoint-only timewise Young and the
   direct nonfrozen one-shot Ramer map; it does not exclude all transports.
   The flexible potential lemma enlarges the sufficient field range from the
   conservative `epsilon_6<0.135` to `epsilon_6<gamma/6=0.27`; the current
   stress candidate is `epsilon_6=0.15`, `delta=0.06`,
   `epsilon_v=0.45`, with final sextic margin `0.06`. The universal centered
   `Q` tensor, all finite moments, and deterministic `H2` Cameron--Martin
   action are closed. The finite forest and balanced continuum classifications
   are also closed at scoped T4. The latter proves the top-jet `-2/-3`
   variance rates, every-finite-moment coupled-cutoff convergence, and the
   exact grouped full-rational A7 reconstruction while retaining `Sigma Q`.
   The strict-past causal/PSD-resolvent continuation is also closed: at
   `epsilon_v=0.45`, `q=10/9`, and one-use is reduced to the global charge
   `sum_j[(q/2)<ell_j,R_q,j ell_j>-C_j]` without repeated past-energy payment.
   `A13-CLASSII-BACKWARD-HEAT-MARTINGALE-SQUARE-COUPLED-CARTAN-REDUCTION`
   now proves the exact retained-square/Gibbs charge, terminal-backward heat
   martingale, controlled telescope, averaged PSD frame secant, and the
   strongest regular-control reduction
   `E V_J^ren >= -zeta E||Z_J||_6^6-eta E sum||h_j||^2-C
   +E sum_(j>=j0)R_j`. Next prove
   `A13-CLASSII-AVERAGED-RAW-CURRENT-CARTAN-JACOBI-FORM-BOUND`, retain the
   positive square, and extend from regular one-shot controls to the declared
   finite-energy class. Do not use termwise absolute values, paraproduct Young
   absorption, or the shellwise `-|w|_Q^2/2` bound.
3. **A11-CLASSII-TRUE-INCREMENT-STABILISED-LOG-LAPLACE** — blocked until the
   A13 redesign fixes the relative variable and budget. Do not reuse a
   standalone source-square antecedent or the historical
   `theta Q_j^fr+C_j` variable.
4. **A6-CLASSII-FULL-FIELD-BARE-CONCENTRATION** — separately classify the
   unmodified spatial Gibbs law across all Class-II null branches; the
   conditional `W_eps=0` branch and local proxy limits are not sufficient.
5. **A7 constructive successor** — only after both A11 analytic gates close,
   package the resulting fixed-floor finite-volume measure below T6 first;
   keep floor removal and infinite volume separate.
6. **Backlog T-030** — arbitrary-Q DR-2 remains a non-load-bearing Sector-B
   frontier as recorded in `TODO.md`.

## Standing rule

Work on any stage may proceed in parallel, but **status promotion order is
strict**: nothing in Sectors C–F rises above T6 while GAP-1 and GAP-2 are open,
unless its statement is manifestly vacuum-independent and says so explicitly.
