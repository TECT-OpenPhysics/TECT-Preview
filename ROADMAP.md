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

**Status — Sector A refreshed 2026-07-20**: the convention and exact kernel
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

The remaining Stage-1 frontier is not another full variational/PDE closure.
`A6-CLASSII-UV-POWER-COUNTING` records at T4 that the bare full derivative
Class-II Gaussian energy has a positive linear cutoff contraction.
`A6-CLASSII-K-COMPOSITE-DEFINITION` now closes at scoped T5 the fixed-floor
canonical geometric `K_A` current within the declared common real-even scalar
spectral regulator class. The same split review eliminates literal
fixed-parameter `-delta_cube*N*W_eps` subtraction as a uniform-coercivity route
and solves two local bare proxies without identifying either with the spatial
Gibbs law. Open work is running-counterterm closure and a separate full-field
bare-concentration theorem. Parameter identity, regulariser removal, infinite
volume, phase transition, BCC, and T7 remain outside the current Sector-A
theorem.

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

## Current priority view (refreshed 2026-07-20)

The live task source is `TODO.md`; historical 2026-06-05 priorities are
preserved in git/changelog rather than treated as current gates.

1. **Repository control task T-006** — finish code-discipline automation.
2. **A6-CLASSII-COUNTERTERM-CLOSURE** — replace the falsified literal
   fixed-parameter subtraction by a running, symmetry-preserving
   renormalisation prescription; close `J*K`, `|K|^2`, lower bounds,
   partition control, and tightness at fixed positive floors.
3. **A6-CLASSII-FULL-FIELD-BARE-CONCENTRATION** — separately decide whether
   the unmodified spatial Gibbs laws concentrate on `W_eps=0`; local proxy
   limits are not sufficient.
4. **A6 constructive successor** — open only if the counterterm route closes;
   begin below T6 and keep regulariser removal separate.
5. **Backlog T-030** — arbitrary-Q DR-2 remains a non-load-bearing Sector-B
   frontier as recorded in `TODO.md`.

## Standing rule

Work on any stage may proceed in parallel, but **status promotion order is
strict**: nothing in Sectors C–F rises above T6 while GAP-1 and GAP-2 are open,
unless its statement is manifestly vacuum-independent and says so explicitly.
