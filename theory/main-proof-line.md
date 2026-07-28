# Main proof line -- referee-package work list (CONFIRMED by operator 2026-06-11)

Per `governance/reproduction-bundle-policy.md` sec.12, a PUBLISHED referee package
is written only for the MAIN PROOF LINE of the published claim, not for every
sub-proof folder. The published result is the Reading-H full-class vacuum
selection (B1/B2, T7-SCOPE_{C_full}, given the A1 kernel convention). Its headline
package cites, as load-bearing dependencies: A1 kernel convention; Lemma 1
(sum-circle additive-energy bound); Lemma 2 (coherence circle-packing, in-document);
(D) T-016 diagonal isotropy; (S) SC-SCOPE selection floor; the layer K-budget;
res5_032--036.

## Main proof line (referee package each -- PUBLISHED, operator-confirmed)

| # | result | folder | role in the published theorem | status |
|---|---|---|---|---|
| 1 | Reading-H C_full | `claims/B1-RH-ENUM/Reading-H` | the comparison theorem (D)(O)(S) + window | **PUBLISHED** -- bundle `B1-RH-ENUM/bundle/Reading-H-cFull-T7-260611` |
| 2 | Prop-A | `claims/B2-PROPA-HLAYER/Prop-A` | (D) diagonal isotropy + (O) class-wide closure (T-016..T-024) | **PUBLISHED** (v1.2, T6) -- bundle `B2-PROPA-HLAYER/bundle/Prop-A-T6-260611` (9/9, 44/44 asserts PASS); scope A_adm T'<=13 |
| 3 | additive-energy / DR-2 | `claims/B5-BEYOND-LAYER-BOUND/DR-2` | Lemma 1: the sum-circle / lattice additive-energy bound (R-025/026) | **PUBLISHED, T7 CONFIRMED on lattice shells** (v1.5, standard NT import) -- bundle `B5-BEYOND-LAYER-BOUND/bundle/DR2-Lattice-T7-NTstandard-260612` (8/8 scripts, 38/38 asserts, operator promotion 2026-06-12; pin note in-bundle; T7Candidate bundle retained as tier history); lattice shells only, arbitrary-Q OPEN, not full C_full |
| 4 | SC-SCOPE | `claims/B5-BEYOND-LAYER-BOUND/SC-SCOPE` | (S) the third-cumulant selection floor | **PUBLISHED** (v1.3, T5 thin-certified) -- bundle `B5-BEYOND-LAYER-BOUND/bundle/SC-SCOPE-T5-260612` (4/4 entry scripts, 29/29 asserts PASS, operator clean-run CONFIRMED 2026-06-12); endpoint I=2e-3 + window W_SC only; NOT T6/T7, NOT full C_full |
| 5 | K-budget / STEP-5B | `claims/B5-BEYOND-LAYER-BOUND/STEP-5B` | the rectangle constant K(n) the off-diagonal const rests on | **PUBLISHED** (v1.2, T6) -- bundle `B5-BEYOND-LAYER-BOUND/bundle/STEP-5B-Rectangle-T6-260612` (192/192 asserts PASS, operator clean-run CONFIRMED 2026-06-12); rectangle prefactor + official threshold 1.59e5 only, NOT full STEP-5B closure; uses H-LAYER-AUX RES-4 as input |

(A1-KERNEL-CONV is the named definitional input; it is legacy and has no in-repo
notes folder yet, so no referee package is due until it is migrated.)

## Sector-A production-functional verification line (operator-confirmed 2026-07-17)

This line is a main-line support result for the future full-production-functional
implementation track.  It does not alter, supply a missing premise for, or enlarge
the published Reading-H C_full theorem above.

| # | result | folder | role | status |
|---|---|---|---|---|
| A1-PFR | Production-functional discrete variational matrix | `claims/A1-PRODUCTION-FUNCTIONAL-REALISATION` | reproducible standalone all-coupling functional implementation; future full-production-functional support only | **PUBLISHED** (T5 CLOSED@DISCRETE-VARIATIONAL-MATRIX) -- bundle `A1-PRODUCTION-FUNCTIONAL-REALISATION/bundle/A1-Production-Functional-T5-260717`; N=4,6,8 only; no historical-solver, continuum, BCC, minimizer, or stability claim |
| A2-FULL | Full-production three-component gradient-flow well-posedness | `claims/A2-FULL-PRODUCTION-WELLPOSED` | continuum PDE theorem for the canonical P1 functional: unique global H2 flow, continuous dependence, exact energy identity, and positive-time smoothing | **PUBLISHED** (T6 CONDITIONAL-THEOREM on `A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL`) -- bundle `A2-FULL-PRODUCTION-WELLPOSED/bundle/A2-Full-Production-WellPosedness-T6-260717`; 22 files, 5/5 entry scripts PASS, aggregate 61/61; excludes historical backend, eta_shell nonzero, infinite volume, minimizer/BCC selection, stability, and T7 |
| A3-PERT | Scalar spectral perturbative continuum limit | `claims/A3-PERTURBATIVE-CONTINUUM-CORRELATORS` | order-by-order fixed-external-momentum cutoff removal for the scalar Brazovskii branch, supported jointly by the A3 UV theorem | **PUBLISHED** (T6 PROVED CONDITIONAL, operator-approved 2026-06-23) -- bundle `A3-PERTURBATIVE-CONTINUUM-CORRELATORS/bundle/A3-Perturbative-Continuum-T6-260719`; 2/2 entry scripts PASS (6/6 + 8/8), all 11 hashes and digest `6783ee6637936675...` verify; spectral/Galerkin only, not Route B, constructive, full Class-II, or T7 |
| A4-SCALAR | Finite-volume scalar spectral constructive Gibbs measure | `claims/A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE` | non-perturbative cutoff removal for the separate real-scalar branch: weak full-sequence convergence, lifted L1/TV density convergence, and smeared cylinder-polynomial correlations | **T6 PUBLISHED** -- operator-confirmed corrected v2.1 uses `m0=max(1,ceil(sqrt(2)q0/alpha))`; claim-level bundle `claims/A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE/bundle/A4-Scalar-Constructive-T6-260719` passes 18/18 + 15/15 = 33/33 standalone, all 18 file hashes, and digest `b1a215465956443ce22a7dcf42caaa9a3dfb61305759f4be4f55eab630cd3162`; excludes derivative Class-II, infinite volume, phase transition, Route B, BCC, parameter identity, and T7 |
| A5-T5 | Branch-aware Sector-A synthesis and termination package | `claims/A5-SECTOR-A-SYNTHESIS` | dependency and non-implication capstone joining the full-production P1/P2/P3 chain with the separate scalar perturbative/constructive arms without identifying their mass or functional scopes | **T5 PUBLISHED** -- exact v1.2 entry operator-confirmed by explicit batch authorization after initial form validation; six support bundles attested; direct and standalone bundle runs pass 16/16 + 16/16 = 32/32; bundle `A5-SECTOR-A-SYNTHESIS/bundle/A5-Sector-A-Synthesis-T5-260719` has 155 hashed files, note-PDF completeness PASS, and digest `5cf4397c38fb316ec108447404531e649e628d6fcc62d67e613d060b70b24ea5`; excludes parameter identity, full derivative Class-II construction, BCC, physical closure, T6, and T7 |
| A5-T6 | Branch-aware Sector-A conditional-composition theorem | `claims/A5-SECTOR-A-SYNTHESIS` | conditional theorem composing the full-production variational/PDE/positive-time exact-Galerkin implication chain and the separate scalar perturbative/constructive conjunction under exactly seven named hypotheses | **T6 PUBLISHED CONDITIONAL** -- exact v1.0 candidate confirmed by Jusang Lee on 2026-07-20; v1.1 binds candidate commit and reviewed hashes; direct and standalone runs pass 22/22 + 13/13 = 35/35; bundle `A5-SECTOR-A-SYNTHESIS/bundle/A5-Sector-A-Conditional-Composition-T6-260720` has 307 hashed files and digest `7779f98a945cf1b393023ab7d41cd30af6e68572797ab698368265a392f4a526`; immutable T5 history retained; excludes parameter identity, full derivative Class-II construction, BCC, physical closure, and T7 |

The separate full derivative Class-II successor is now one theorem family,
not a sequence of peer-level capstones. A6 closes the fixed-floor canonical
$K_A$ definition after its UV power-counting obstruction; A7 closes the
covariance-normal energy composite; A8 and A9 close the decoupled reference
and interpolation identities. A10--A13 retain the exact replacement/no-go
lineage. A13 is the active subproof host: its universal $Q$, finite-cutoff
coefficient-jet forest, balanced-jet continuum, exact grouped A7
reconstruction, backward-heat, NPC-cone, tip-safe grouped-harvest,
off-diagonal telescope, resonant phase-root, invariant-current principal
one-form, and fixed-cutoff graph-recovery reductions are closed at scoped T4.
R-076 adds the nonduplicating endpoint ledger and the sharp maximal-input
`X^(2/5)Y^(8/15)` Besov payment, closing the control-independent cubic and
both nonresonant paraproducts. R-077 replaces its proposed raw three-class
root taxonomy by complete fresh-Gaussian Doob packets and a disjoint scale
orientation. The complete packets cancel in signed expectation, and the full
payload-comparable `m<=r+L` shifted-resonance form closes with the fifteenth
moment. R-078,
`A13-CLASSII-HESSIAN-DIFFERENCE-SAFE-PACKET-DOOB-BRACKET-REDUCTION`,
reassembles the exact transport through a bounded Hessian difference with
`A^2 DA` payload and moment `30/7`, defines the canonical safe packet by
subtraction followed by one causal projection, and identifies the exact
future-control innovation-bracket mechanism for each factorised bilinear
component. Its unweighted coefficient square function is one-use and the
declared high-`U` principal closes with moment `60/19`. R-079,
`A13-CLASSII-FULL-SAFE-PACKET-FRAME-CURRENT-DOOB-DECOMPOSITION`, now closes
the exact full-current algebra: one conditional low-current term, present-
control increments, and future-control innovations reconstruct the complete
safe packet, with the present/future cross term and the complete low endpoint
retained. It also proves a spatially weighted Cameron--Martin square function
that spends control energy once and an exact backward-heat projection for the
base or predictably translated current. The terminal feedback commutator still
contains coefficient and derivative-feedback channels. Generic weighted
shortcuts fail. R-097--R-102 terminalise the heat-lifted Gram form, identify
the exact complete owner, separate the fixed-low raw-Wick endpoint from its
future residual, and close the regular shifted current `K_R` with its terminal
square unspent. R-103 then proves the disjoint expectation-level complete-
owner partition. Its seven modules close complete regular `H_N`, and adding
the R-083/R-092 FAR owners gives the eight-module regular `REG` bound. The
literal naked posterior bracket remains unproved and is non-load-bearing for
this regular conclusion. R-104 then transports the exact owner incidence to
each declared temporally faithful fixed source chart: the endpoint-owner
defect is zero, representation-preserving subdivision invariance applies only
after complete recombination, and
`A_phys,J(u)=A_J(h)+D_CM(u,h)` with `D_CM>=0`. The exact current child remains
`A13-CLASSII-FULL-PROGRESSIVE-REVISIT-EXTENSION`, now narrowed to the uniform
`OVERLAP_src` source-action lower bound, which R-089/R-093 identify with the
`q=10/9` Nelson theorem. The anticipative-heat fixture is only a no-automatic-
extension boundary, not an action or Nelson counterexample.
R-105 completes the common-root representation audit: only the complete
value-plus-heat endpoint is subdivision invariant, while the historical
rational owners are not. It retires generic A9 monotonicity, the registered
full-budget pathwise/absolute critical-Young extraction, and the all-law
pointwise relative bracket; the last fails at one fixed production cutoff by
forcing `b(t)>=3/t`. Its exact one-pair determinant theorem is confined to an
artificial scalar quadratic mode-diagonal model because the physical field has
sign-indefinite cross-mode resonances. The proof line therefore returns to the
uniform complete source action through either a complete signed cross-mode/
forest packet or a Gibbs-specific/time-integrated A9 cancellation. Sector A
remains open.
R-106 proves the exact Gibbs endpoint likelihood, both KL orientations, and
the thermodynamic-integration identity. The total time integral is only the
endpoint target until an independent root-local estimate is supplied. A
constant production ray rules out pointwise endpoint-likelihood coercivity,
and the exact same-root `1:2` production merge rules out bounded raw input-mode
leaf tensorization and its leafwise sextic repair. R-082's complete coherent
output-frequency square is a legal prioritized coordinate, not yet a bound and
not claimed unique; the equivalent direct complete source-action route remains
live. Uniform `OVERLAP_src`, Nelson, removals, the interacting measure, and
Sector A remain open.
R-107 closes the multi-row coherent-output likelihood only for jointly frozen
maps and closes the whole-output determinant for one fresh root with a past-
measurable map and mixed baseline. Rowwise predictability does not license one
global frozen backward resolvent: an exact bounded two-root fixture has mass
`1.070433115292664...>1`, and a smooth `tanh` companion has a strict defect.
R-107 also proves positive output trace allocation and the exact complete
predictable-baseline source-action normal form. Exact fixtures retire output
singletons, independent row normalizers, termwise adapted second-jet bounds,
and a pure carrier-KL diagonal bridge. The live theorem is a subdivision-
invariant same-root adapted contraction-closed cluster or equivalent matrix-
Carleson lower bound retaining heat, trace, mixed baseline, future feedback,
rational recovery, the complete R-063 forest, and one terminal root sextic.
Uniform `OVERLAP_src`, Nelson, removals, the interacting measure, and Sector A
remain open.
R-108 identifies the quotient-safe and order-correct version of that frontier.
Historical `F_6.5` and visitwise `K_R` fail representation-preserving
subdivision, whereas the complete endpoint has exact conditional mean/
covariance and CM-minimized identities with no sign. A complete cluster has
the corresponding signed normal form. The one-pair fixture rules out only a
bare average-before-square ledger unless its explicit nonlinear/sextic repair
is paid; square-before-average remains merely viable there. An oscillatory
selector rules out only an absolute arbitrary-selector positive future-
feedback HS/PSD ledger paid solely from source energy and one sextic because
the complete signed second jet cancels. A determinant successor may square the realized
conditional cluster covariance before outer averaging. The cutoff/chart/
control/subdivision-uniform signed complete-cluster lower bound,
`OVERLAP_src`, Nelson, removals, the interacting measure, and Sector A remain
open.
R-080,
`A13-CLASSII-LOW-OBJECT-FAR-SQUARE-PROGRESSIVE-BOUNDARY`, closes both low
objects for the declared no-revisit one-shot class, reduces far feedback to
one localized predictable base-current tail, and narrows the near residual to
a predictable explicit payload plus a hidden future-adapted coefficient. It
also corrects the downstream scope: R-075 graph recovery covers its specified
regular graph, not all progressive/revisit controls. R-081,
`A13-CLASSII-CARTAN-TAIL-ADAPTED-NEAR-TEMPORAL-REDUCTION`, then proves the
exact polynomial/Cartan current split, removes the polynomial far channel,
and proves deterministic relative-gap decay. The remaining FAR theorem is
root-resolved because a shellwise root sum is half-derivative critical. In
NEAR, vector-valued Doob--Burkholder interpolation closes the stochastic input
budget and exact gain ledger only for an explicitly factorised first-order
response. A two-root witness and the exact secant--Jensen split expose an
upper-triangular nonlinear defect invisible to `D_jA`; that defect, the
adapted complete-forest operator, and the signed control--control branch
remain. Temporal Douglas factorisation extends
the complete packet algebra to overlapping bounded-simple packets, while a
  one-mode witness proves that the R-075 graph is not progressive-dense. R-082,
  `A13-CLASSII-STOPPED-CURRENT-FAR-COMPLETE-CURRENT-NEAR-COORDINATE-REDUCTION`,
  then rewrites the complete FAR wedge as one deterministic stopped-current
  square with both predictable drifts retained and closes the uncontrolled
  production FAR contribution by the support-refined R-050
  `C^(3 alpha-1)` remainder. Its orthogonal causal Carleson route is sharp at
  `s=1/2`, but the balanced controlled production decomposition is open. The
  complete current also has a global four-row Pauli--Fierz Gram coordinate;
  state-dependent compression is not rootwise, target heat acts on `C^T C`,
  and future conditional covariance defects remain signed. R-083,
  `A13-CLASSII-CONTROLLED-POLYNOMIAL-CFAR-LINEAR-PAULI-FIERZ-FOREST-REDUCTION`,
  closes every controlled polynomial stopped-FAR row for `C>=3`, including
  both endpoints and both predictable drifts, and leaves exactly three Cartan
  input-scale telescope squares with coefficient `3/(80P)`. The canonical
  `K_k` input ledger is one-use, but an exact production-floor harmonic
  fixture shows that nonlinear output orthogonality does not follow. On the
  NEAR side, the exact linear Pauli--Fierz Gram/heat/secant/nine-block forest
  is now explicit; an adapted zero-rational-row fixture has negative zero chaos
  in a linear row. Correlated or signed Cartan CFAR, recombined complete signed
  NEAR, and an overlap-stable full-progressive extension are required before
  the umbrella one-use/`q=10/9` Nelson bound. R-084,
  `A13-CLASSII-ROOT-DIAGONAL-CARTAN-OU-LINEAR-PAULI-FIERZ-ABSORPTION`,
  now gives the exact root-diagonal Cartan identity and conditional far-
  projected OU-gradient representation. A cumulative-tree witness excludes
  root orthogonality alone as a one-use proof. In parallel, all three linear
  Pauli--Fierz NEAR rows are form-absorbed for regular mutually orthogonal
  strict-past one-shot controls. R-085,
  `A13-CLASSII-NONORTHOGONAL-CARTAN-SCHUR-RATIONAL-HESSIAN-BOUNDARY`,
  replaces the failed output-orthogonality route by a nonorthogonal weighted
  Schur theorem conditional on complete mixed production atoms with `s>1/2`.
  It also expands the rational endpoint exactly and form-absorbs its five
  unshifted families. The remaining analytic order is now precise: prove the
  mixed Cartan atom estimates (4.10)--(4.11), prove the coupled signed
  shifted-Hessian-plus-positive-square bound (6.5), reassemble REG, then prove
  OVERLAP, CORE, controlled-shell one-use, and `q=10/9` Nelson. R-086,
  `A13-CLASSII-RATIONAL-TRANSLATED-WICK-PAYLOAD-COMPARABLE-REDUCTION`,
  now rewrites (6.5) as an exact translated-Wick normal form and pays its
  base-frozen, nonresonant, and payload-comparable branches. The only rational
  term still needing proof is the coefficient-dominant high--high-to-low
  packet with endpoint square, Wick trace, and lower-chaos forest retained.
  R-087,
  A13-CLASSII-CARTAN-SPATIAL-DECAY-RATIONAL-TRACE-VARIATIONAL-CORE-REDUCTION,
  proves the spatial Cartan atom estimate (4.10) for 1/3<alpha<1/2 and every
  1/2<s<3alpha-1/2; the production choice alpha=2/5, s=7/12 has margins 7/30
  and 13/30. Its Cartan one-use ledger (4.11) remains open. The exact rational
  eta-completion exposes rather than pays the trace debt and leaves the
  coefficient-dominant packet. At fixed cutoff, its variational CORE reduces
  the all-control Boue--Dupuis infimum to bounded smooth cylindrical-simple
  controls. The remaining order is Cartan (4.11), the rational packet, REG,
  uniform OVERLAP on that core, invocation of R-087 CORE, controlled-shell
  one-use, and q=10/9 Nelson.
  R-088,
  A13-CLASSII-DIRECT-ROOT-CARTAN-SCHUR-SEQUENTIAL-SECANT-RATIONAL-CONDITIONAL-TRACE-REDUCTION,
  corrects the application-level normalization without retracting R-085: the
  exact R-084 root sum has no outer `2^j`, so its direct nonorthogonal Schur
  summation needs only `s>0` and the unweighted ledger `sum_k q_k`. At
  `s=eta=7/12` its constant is `16.30295538482827` and its gap is
  `2^(-7C/6)`. R-088 also proves the exact three-channel sequential Cartan
  secant and the quartic Besov payload, while leaving the expectation-inside
  two-point far estimate and its unweighted production ledger open. On the
  rational branch it proves the exact pointwise three-term square--Wick--debt null identity and the
  conditional mean/covariance formula; only the centered covariance-matched
  branch closes. The complete same-root square/trace/heat/Jensen/forest packet
  remains inseparable. The remaining order is the sequential Cartan bridge or
  a direct integrated CFAR theorem, that complete rational packet, REG,
  uniform OVERLAP, invocation of R-087 CORE, R-066 controlled-shell one-use,
  and `q=10/9` Nelson.
  R-089,
  A13-CLASSII-PROGRESSIVE-COVARIANCE-COMPRESSION-RATIONAL-MEAN-SPECTRAL-BOUNDARY,
  proves global progressive covariance compression and removes the one-shot
  restriction from the pure-control quartic terminal bridge. Its Hilbert
  martingale ledger spends the terminal coordinate once despite range overlap
  or revisit. Summing every physical shell before squaring gives the exact
  complete-cross-shell Cartan Fourier trace and proposed the global nonlinear
  coefficient-tail energy (3.12). The `s=1/4` ledger
  has slack `1/8`, while an exact harmonic rules out a homogeneous
  quartic-only replacement. The rational Taylor-coordinate criterion and the
  production value `L/e=-1/432` show that eta alone cannot replace the
  complete same-root endpoint. Full OVERLAP is
  exactly equivalent through R-087 CORE to `q=10/9` Nelson; R-066 one-use and
  all complete temporal packets therefore belong inside/before OVERLAP.
  R-090,
  A13-CLASSII-GLOBAL-UNPROJECTED-CARTAN-COEFFICIENT-LEDGER-NOGO-RATIONAL-FOREST-BOUNDARY,
  claimed `b=grad c`; R-092 audits that transpose step as false and replaces
  the conservative compression by the exact R-089 two-tail trace.
  It falsifies only the global unprojected R-089 ledger (3.12) for every
  `s>0`; the root-diagonal witness is removed by the relative FAR projector,
  so projected CFAR remains open. It corrects the branch conditioning,
  proves the local raw rational endpoint sign
  `-(35840/13689)c1 e phi(1)<0`, and enforces R-063 forest nonduplication with
  R-079 as the canonical temporal decomposition. The remaining chain is
  projected Cartan `H_C`, complete signed rational/linear NEAR `H_N`,
  progressive assembly `H_A` inside full OVERLAP, R-087 CORE, and Nelson.
  These are non-interchangeable sufficient obligations, not an iff
  decomposition.
  R-092,
  A13-CLASSII-NORMALIZED-CARTAN-COMPENSATED-PERSPECTIVE-TRIANGULAR-COVARIANCE-FRONTIER,
  closes regular mutually orthogonal no-revisit one-shot `H_C` by a bounded
  normalized-lift whole-product estimate, with root surplus `7/30`, Young
  slack `1/30`, and gap `2^(-(C-5)/2)`. It augments the `H_N` perspective
  density with the Doob increments of the terminal positive energy, closing
  frozen and coefficient-conditioned moment-matched one-reveal subcases but
  not multistep derivative feedback. Exact covariance/entropy union removes
   overlap multiplicity and retains kernel cost as fibre entropy, but its
   remaining free energy is exactly Nelson.
  R-093,
  A13-CLASSII-AUGMENTED-PERSPECTIVE-GIBBS-GAP-INFORMATION-BOUNDARY,
  identifies the centered symmetric even augmented defect exactly as a
  coefficient/quadratic covariance. Its bounded smooth production fixture is
  locally negative for every fixed payment, while the genuine cutoff-two
  torus action stays coercive on bounded smooth predictable shell-two sources.
  Same-root coefficient revelation costs mutual information, fixed charts do
  not generally attain Nelson, and causal orthogonal triangularisation cannot
  mix time blocks. Under the R-087 payoff and finite-entropy hypotheses, the
  directed union of temporally faithful charts equals fixed-cutoff CORE and
  near minimisers close both Gibbs gaps. The remaining analytic step is the
  coefficient-unconditioned root-local `H_N` bound; `H_A` then only assembles
  complete packets losslessly into `OVERLAP_src`, already the Nelson
  objective. Sector A remains open.
  R-094,
  A13-CLASSII-ROOT-LOCAL-GRAM-SECANT-FEEDBACK-BOUNDARY,
  proves the regular centered Gram-secant theorem and two one-use feedback
  subchannels. The strong `2^(j-4k)` scale is valid only for positive
  quadratic curvature; the complete mixed secant starts at `2^(j-2k)` but
  closes by weighted Hardy and product-space interpolation with slack `1/3`.
  Conditional Gaussian Poincare pays the combined value--heat control prefix
  from a declared fraction of the retained feedback square. R-095 proves that
  the corresponding rootwise future reserve is not the same fraction of the
  global terminal square: their exact moving-prefix defect has no sign and a
  scalar value `-1/4`. The reduced perspective is positive exactly under
  `2R>=theta B`, conditioning produces a resolvent and transformed-mean debt,
  and the present absolute ledgers admit no root-decaying fraction window.
  Near `T_G^>` retains bounded Cartan curvature outside regular Cartan FAR
  ownership. R-096 now proves that complete R-077 fresh-root cancellation
  must precede rational projection. On each resulting predictable baseline,
  the genuine R-086 coefficient-dominant `T_Q^>,T_G^>` region is support-
  empty after a fixed widened payable collar. Raw Wick compresses exactly to
  coordinate Hermite ranks zero through two, but this provides no spatial
  gain and Stein differentiation exposes adapted-selector derivatives. The
  R-097--R-102 terminalise the global Gram form, prove complete-owner payment-
  gauge invariance and exact row additivity, separate the fixed-low raw-Wick
  endpoint from its future reveal, and replace the old rational (6.5)
  frontier by a closed regular `K_R=G^T L c+c^T B_1 c/2` estimate. R-103
  supplies the missing once-only owner audit: fixed-low raw Wick stays in the
  R-080/R-063 low objects, only the future reveal is a separate residual, one
  signed R-078 paid difference is bounded under the R-096 collar, and the
  separate R-086 `Q` orientations and `T_G^<=` charge are refunded. Seven
  modules close complete regular `H_N`; eight close regular `REG`, while the
  terminal square remains reserved. Progressive/revisit `H_A`,
  `OVERLAP_src`, Nelson, and Sector A remain open.
Sector A remains open. This family is not a new premise of A5 and has no
current PUBLISHED measure theorem.

## Auxiliary / cited (DRAFT bundle only -- NO referee package, NOT a coverage obligation)

| folder | why auxiliary |
|---|---|
| `claims/B1-RH-ENUM/ESTIMATOR-UPGRADE` | T4 controlled-error numerical robustness of the enumerated estimator; cited, not load-bearing |
| `claims/B1-RH-ENUM/ROBUSTNESS-MU2` | off-anchor robustness evidence across the mu^2 band |
| `claims/B1-RH-ENUM/enumerated` | migration / provenance re-validation record (not a result) |
| `claims/B1-RH-ENUM/near-gap` | convention exactness + a self-caught retraction |
| `claims/B5-BEYOND-LAYER-BOUND/H-LAYER-AUX` | RES-4 layer-ratio; supports STEP-5B's K-budget |
| `claims/B2-PROPA-HLAYER/G-A0-DUI` | A=0 uniqueness sub-lemma (supports the A1 reference) -- candidate fold into Prop-A / A1 |
| `claims/B2-PROPA-HLAYER/H-A0-removal` | A=0 uniqueness sub-lemma (supports the A1 reference) -- candidate fold into Prop-A / A1 |

The DRAFT referee documents already written for the auxiliary folders remain as
internal consolidation notes; they are NOT promoted to PUBLISHED and are not
coverage obligations.

## Status (operator-confirmed 2026-06-11)

The main-line set (rows 2--5) and the auxiliary classification are CONFIRMED. The
main-line packages are refined to publication grade, operator-confirmed per result
(sec.11 gate), and bundled at `claims/<ID>/bundle/<Result>-<Tier>-<YYMMDD>/` (sec.13).
The auxiliary folders keep DRAFT bundles only; their referee DRAFTs are marked
AUXILIARY and are NOT promoted.

**Progress (2026-06-11)**: Reading-H and Prop-A are PUBLISHED. Prop-A v1.2 was
operator-confirmed after a reconstructed clean-run (9/9 scripts, 44/44 asserts
PASS) and published as `B2-PROPA-HLAYER/bundle/Prop-A-T6-260611` (T6, scope
A_adm T'<=13; does NOT independently enact full C_full). Per policy sec.14 (2026-06-11) bundles are main-line-only, claim-level, and built
only post-confirmation (no DRAFT bundle; packaging is the LAST step, followed by
the final integrity check). All per-sub-folder bundles and the pre-confirmation
DRAFT bundles are being removed Windows-side; only the two main-line PUBLISHED
bundles (`Reading-H-cFull-T7-260611`, `Prop-A-T6-260611`) remain. Remaining review
queue: T-013 COMPLETE AND CONFIRMED -- all four synthesis notes are PUBLISHED and operator-registered: `Main-Line-Synthesis-T013-260612` (v1.2, aggregate count corrected to the MANIFEST-derived 27 scripts / 330 asserts with inline provenance), `B1-RH-ENUM-Synthesis-T013-260612`, `B2-PROPA-HLAYER-Synthesis-T013-260612`, `B5-BEYOND-LAYER-BOUND-Synthesis-T013-260612` (all v1.1). The synthesis layer is FREEZE-READY. The Reading-H main line is a single claim-level theorem archive (head + five published bundles + four registered synthesis documents). Remaining tracks: T-004 R-U6-1 proof delivered (operator review pending), T-031 STEP-5B exhaustiveness decision layer, T-030 arbitrary-Q DR-2 (frontier), T-006 infra.
