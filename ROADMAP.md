# TECT 6-Stage Roadmap — v2

**Issued**: 2026-06-05 · **Source of stage definitions**: GOVERNANCE.md
**Current-status source**: live `claims/*/status.json`, rendered `CLAIMS.md`,
`RESULTS-LEDGER.md`, and `TODO.md`. The legacy `TOE-FACT-SHEET.md` snapshot is
bootstrap provenance only and is not a current-status authority.

The generated cross-route view is `theory/proof-evidence-map.md`: it joins
accepted results, failed routes and reasons, open gates, live tasks, lineages,
and reproduction entrypoints by reference without becoming a status authority.

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

**Status — Sector A refreshed 2026-07-28**: the convention and exact kernel
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
budgets for regular mutually orthogonal one-shot controls. The subsequent
`A13-CLASSII-NPC-CONE-MARTINGALE-INJECTION-REDUCTION` gives the exact
Nelson-aligned current factorisation, aggregate CAT(0) cone, strong Jacobi
remainder, and raw-energy/injection telescope. It refutes shellwise positivity
at a positive floor, proves the isolated adapted `1:2` and `1:3` losses
summable, and uses a flat CAT(0) reset model to retire geometry-only one-use
without producing a production counterexample. The parent gate is
`A13-CLASSII-NPC-CONE-MARTINGALE-INJECTION-BALANCE`.  The tip-safe grouped-
harvest reduction proves the nonlinear harvest, conservative-score Carleson
bound, uncontrolled-Gaussian tails, CAT(0) whole secant, and global centered-
form lemma. `A13-CLASSII-ENDPOINT-LIFTED-SCHUR-CAUSAL-GROUPING-REDUCTION` now
closes the local production Schur step and pure-control bookkeeping: the old-
endpoint affine tangent is falsified by rotating phase kernels, while the
hybrid endpoint lift is uniform in derivative displacement and coherent
frozen-value causal grouping telescopes pure-control current creation.  A
two-shell scaling fixture also retires separate payment of that pure-control
defect.  R-070,
`A13-CLASSII-WICK-DOOB-TERMINAL-RESOLVENT-REDUCTION`, now terminalizes the
complete Wick current: the CC/GG/mixed channels become one terminal
covariance-normal current, raw-to-Wick conversion restores exactly the R-066
trace, Abel--Hardy summation pays its transported tail, and the R-069 endpoint
defect is the single R-068 centered form.  Terminal Schur completion pays the
Hilbert--Schmidt trace but cannot center an adapted terminal coefficient; the
scalar diagnostic and the derivative-demanding Stein route retire those two
  shortcuts. R-071 corrects the false raw linear regularity attribution and
  closes the full fixed-floor symmetric--Cartan frame through the R-050
  enhanced one-form. R-072 then classifies the exact production phase-gauge
  kernel, proves an inverse-free regularized completion, and pays the matched
  strict-past same-shell nonlinear leakage with one accumulated integrable
  random constant and an `O(N_j0^-3)` sixth-moment tail. Exact terminal shell
  expansion nevertheless leaves three load-bearing off-diagonal families; an
  independent production fixture makes their combined magnitude more than
  4087 times the diagonal. R-073 reassembles all three families and the R-071
  linear term into the R-069 raw current telescope exactly. Restoring both
  separated first variations gives a projector-free terminal square and
  cancels every phase-kernel component across the kernel-projector rank-2/3/6
  strata. R-074 proves that the bare mismatched nonlinear coefficient has an
  exact nondecaying high--high-to-low resonance and that strict-past Wick
  centering is not automatic. It closes genuine local phase orbits by exact
  raw-current invariance and a cutoff-uniform relative-phase Wick anomaly with
  `O(Lambda^-3)` tail, and supplies the deterministic Besov sixth-moment
  payment for the remaining horizontal cubic payload. R-075 then proves the
  projector-free invariant-current Taylor chart, closes the principal
  unshifted one-form with a cutoff-uniform sixth moment, and establishes the
  declared fixed-cutoff predictable graph-norm recovery. R-076 gives the
  nonduplicating signed endpoint ledger and corrects the R-075 coarse
  criticality verdict: the bare cubic payload obeys the sharper
  `X^(2/5)Y^(8/15)` estimate with `1/15` Young slack, so its fifteenth moment
  closes the control-independent cubic one-form and both nonresonant Bony
  branches. Exact affine-Bregman, path, and equal-frequency fixtures exclude
  positivity and a separated shifted-current multiplier estimate. R-076
  records a three-class largest-root successor decomposition but proves no
  causal branch estimate. R-077,
  `A13-CLASSII-CAUSAL-PACKET-PAYLOAD-RESONANCE-REDUCTION`, replaces that raw
  taxonomy by a canonical sequential packet split. Complete fresh-Gaussian endpoint packets are exact
  Doob differences and cancel in signed expectation, and the whole
  payload-comparable `m<=r+L` shifted-resonance orientation is paid by the
  R-076 fifteenth moment after one global Young inequality. R-078,
  `A13-CLASSII-HESSIAN-DIFFERENCE-SAFE-PACKET-DOOB-BRACKET-REDUCTION`,
  reassembles the same exact transport through the bounded Hessian difference
  with `A^2 DA` payload, improving the comparable payment to
  `X^(2/5)Y^(11/30)`, slack `7/30`, and moment `30/7`. It defines the
  remaining packet canonically by subtraction from the complete endpoint and
  one causal projection. For each factorised bilinear component, exact Doob
  algebra identifies a future-control innovation bracket; the unweighted
  coefficient coordinate has one square-function bound and the declared
  high-`U` principal closes with moment `60/19`. R-079,
  `A13-CLASSII-FULL-SAFE-PACKET-FRAME-CURRENT-DOOB-DECOMPOSITION`, closes the
  exact full-current and canonical safe-packet reconstruction with the
  conditional low-current block, present-control increments, future-feedback
  innovations, cross term, squares, traces, forest, paid difference, and
  complete low endpoint retained. It proves a spatially weighted Cameron--
  Martin control square function and the predictable base-current heat
  projection. R-097--R-102 terminalise and recoordinate this regular-control
  algebra in the exact complete-owner coordinate. R-101 separates the fixed-
  low raw-Wick endpoint from the future residual, and R-102 closes the whole
  regular shifted current `K_R=G^T L c+c^T B_1 c/2` uniformly in the cutoff
  and deterministic PSD target/future heat, with the terminal square unspent.
  R-103 now proves the disjoint expectation-level owner partition: the two
  R-080/R-063 low objects retain the fixed-low raw-Wick difference, only the
  R-100/R-101 future reveal is a separate residual, the single signed R-078
  paid difference is bounded under the R-096 collar, and all duplicate R-086
  orientations/current charges are refunded. Seven modules close complete
  regular `H_N` and eight modules close `REG`; the allocation
  `eta*=1/440`, `zeta*=3/100` leaves reserves `197/440`, `3/25` and preserves
  the terminal square. The literal naked posterior bracket remains unproved
  and is non-load-bearing for this regular closure. R-104 now closes the
  fixed-chart algebraic assembly step: the R-079/R-091 endpoint has zero
  defect against the recombined R-103 incidence template after the exact
  R-083 and R-100--R-102 algebra is reapplied on each chart. A representation-
  preserving subdivision preserves only the recombined total, and
  `A_phys,J(u)=A_J(h)+D_CM(u,h)` with `D_CM>=0`. The active child remains
  `A13-CLASSII-FULL-PROGRESSIVE-REVISIT-EXTENSION`, narrowed to the uniform
  `OVERLAP_src` source-action lower bound, equivalently `q=10/9` Nelson.
  R-105 now completes the common-root representation audit: only the complete
  value-plus-heat endpoint survives subdivision, while the normalized rational
  owners do not. Generic monotonicity, the registered pathwise/absolute
  critical-Young extraction, and the all-law pointwise relative bracket are
  retired; the last forces `b(t)>=3/t` at one fixed production cutoff. The
  positive one-pair theorem is only an artificial mode-diagonal model and
  physical cross-mode resonance blocks tensorization. The live routes are a
  complete signed cross-mode/forest packet or a Gibbs-specific/time-integrated
  A9 argument. Sector A remains open. R-080,
  R-106 now makes the Gibbs branch exact at its endpoint: the log-likelihood,
  both KL orientations, and thermodynamic-integration identity are proved, but
  the total time integral alone is circular without an independent local
  estimate. A constant production ray retires pointwise endpoint-likelihood
  coercivity, and an exact same-root `1:2` production merge retires bounded
  raw input-leaf tensorization and its leafwise sextic repair. The R-082
  complete coherent output-frequency square is therefore a prioritized legal
  candidate coordinate, not a proved or unique bound; the direct complete
  source-action route remains live. Uniform `OVERLAP_src`, Nelson, removals,
  the interacting measure, and Sector A remain open. R-107 now closes the
  multi-row likelihood only for jointly frozen coefficients and closes one
  fresh-root determinant for a past-measurable map and mixed baseline. Rowwise
  predictability does not license the global frozen resolvent: an exact bounded
  two-root fixture has mass `1.070433115292664...>1`, with a smooth companion.
  Positive trace allocation remains subdivision compatible.
  Singleton output frequencies and independently normalized output rows fail;
  contraction-connected output clusters are mandatory. The direct action is
  reduced exactly to the complete predictable-baseline sum, one root sextic,
  and one source-energy payment, but its same-root adapted lower bound is still
  open. Termwise second-jet estimates and a pure carrier-KL diagonal bridge are
  retired. The narrowed target is a subdivision-invariant adapted complete-
  cluster/matrix-Carleson estimate with the full R-063 forest and rational
  recovery retained once. R-108 now proves that historical `F_6.5` and
  visitwise `K_R` do not descend to the subdivision quotient, while the
  complete endpoint has exact conditional mean/covariance and CM-minimized
  identities with no sign. A bare average-before-square covariance ledger
  fails unless its explicit nonlinear/sextic repair is paid. An absolute
  arbitrary-selector future-feedback HS/PSD ledger paid solely by source
  energy and one terminal sextic also fails, while the signed jet cancels.
  Square-before-average remains viable only on the one-pair fixture. The required uniform
  signed complete-cluster lower bound remains open, as do `OVERLAP_src`,
  Nelson, removals, the interacting measure, and Sector A.
  R-109 now proves the exact one-pair square-before-average normalizer at all
  amplitudes and its legal fresh-pair supermartingale, repairs the R-108
  realized-covariance filtration order, and proves a fixed-predictable-PSD
  signed second-jet score-transfer form bound. The centered diagonal quartic
  floor is uniform, but the full mixed-baseline floor diverges and physical
  cross-mode resonances prohibit tensorization. Stein transfer is expectation-
  only and cannot replace the raw Wick coordinate inside an exponential. The
  remaining target is one adapted raw complete production cluster coupling
  Cameron--Martin mean, realized covariance, trace, baseline, rational
  recovery, all visits, and the random-W forest with source and one terminal
  sextic paid once. `OVERLAP_src`, Nelson, removals, the interacting measure,
  and Sector A remain open. R-110 now assembles a same-root random covariance
  exactly through its Gaussian double divergence and derives a trace-corrected
  diagonal-to-decoupled interpolation. Static covariance norms and an
  unowned nonlinear tangent square are retired. R-111 proves the exact
  degenerate faces, and R-112 now places the genuinely mixed stationary scalar
  `k:2k` problem on one closed covariance simplex. It proves an exact compact
  semialgebraic residual domain and analytic radial tail, a factored uniform
  projective expansion through the positive second correction, an existential
  large-amplitude theorem, an origin cusp, and slice-wise face patches. The
  exact negative third coefficient retires all-order sign induction without
  refuting the target. R-113 now makes four projective wedges, eight origin
  cones, and both covariance-face widths explicit; sharpens the phase floor
  through the full zero-amplitude `tau>=13` theorem; and certifies one complete
  genuinely mixed box by two non-importing outward-rounded Arb programs. The
  residual was separated from both covariance faces and `tau=0`. R-114 closes
  the complete `x=0` axis and the cone `0<=b=x/tau<=643/200`. R-115 now
  closes the complementary half-line and therefore the original R-112
  stationary scalar theorem for every covariance shape, amplitude, and
  `tau>=0`, strictly away from `tau=0`. Its four-moment left Gauss--Radau
  majorant and exact three-atom skew lemma are certified both by a complete
  outward Arb cover and by a structurally independent exact Bernstein/radical
  proof. R-116 proves the exact same-root endpoint quotient and owner firewall.
  R-117 extends its tail theorem to the full finite-dimensional rational
  horizon, proves uniform fixed-cutoff convergence of the R-082 positive-floor
  root to that horizon, and computes the sharp joint homogeneous Pauli--Fierz
  trace constant. Exact finite-shell arithmetic plus an analytic N^{-3} tail
  give strict all-direction canonical dyadic-root margins at q=10/9 and
  2q=20/9, so both frozen bare-root normalizers exist. A same-shell phase
  modulation simultaneously retires every local Lipschitz metric error-bound
  route; the trace proof does not need one. R-118 proves the exact finite-visit
  quotient criterion `ker L subset ker K` iff `K=L* B L` and extends the R-068
  centered-form estimate to spatially constant selfadjoint operator families
  with bounded absolute spectral variation, without a visit-count loss. Its
  exact opposite-visit and Hermite fixtures show separately that a diagonal
  visit square does not automatically descend to the terminal sextic and that
  a universal PSD random-`W` double-divergence owner is false. R-119
  reconstructs the minimum genuine two-block/two-visit adapted test and proves
  the exact aggregate zero/first-chaos trace criteria. R-120 now diagonalizes
  the complete A1 six-current coefficient, closes the covariance-horizontal
  `H2`/endpoint-`L6` synthesis for the fixed-matrix R-118 form, proves the
  conditional order-two variable-multiplier remainder, and proves stationary
  common-real-even low-chaos cancellation for all six raw-current rows. Its
  exact linear/rational Hessian inventory reduces the zeroth-order matrix
  burden to 21 fixed generators, but a genuine first-order Cartan block
  survives. Both implementations reproduce `-40/729`; the required
  `+40/729` complete-owner companion is not observed. Continue by
  reconstructing the complete rational owner on the R-119 adapted chart,
  computing its `D0,D1` coefficients, and either cancelling that checksum or
  directly bounding the surviving Cartan form before invoking R-120 once over
  the R-093 directed source union. Strict per-shell normalizer existence alone
  does not imply this once-only global burden.
  `OVERLAP_src`, Nelson, removals, the interacting measure, and Sector A
  remain open. R-080,
  `A13-CLASSII-LOW-OBJECT-FAR-SQUARE-PROGRESSIVE-BOUNDARY`, closes both low
  objects for the declared no-revisit one-shot class, reduces the far feedback
  loss to one localized predictable base-current tail, and narrows the near
  residual to a predictable explicit payload plus a hidden future-adapted
  coefficient. R-081,
  `A13-CLASSII-CARTAN-TAIL-ADAPTED-NEAR-TEMPORAL-REDUCTION`, splits the
  production current exactly into a far-vanishing quadratic channel and one
  nonlinear Cartan channel. It proves a deterministic relative-gap tail but
  shows that rootwise summation is half-derivative critical; FAR is now the
  complete root-resolved FAR martingale paracomposition estimate. It also proves
  the vector-valued input budget and exact positive-gain ledger for an
  explicitly factorised first-order NEAR response. A two-root witness has
  `d_jA=d_jDA=0` but nonzero nonlinear coefficient innovation, so the exact
  secant--Jensen split leaves an upper-triangular Jensen defect inside the
  adapted lower-chaos-complete signed packet. Absolute control--control pair-
  high payment is also excluded. R-082,
  `A13-CLASSII-STOPPED-CURRENT-FAR-COMPLETE-CURRENT-NEAR-COORDINATE-REDUCTION`,
  rewrites the whole FAR wedge as one deterministic stopped-current square,
  retaining the moving endpoint and both predictable control drifts. It
  corrects the centering ledger: raw value innovation centers only with its
  heat compensator. The uncontrolled production FAR subbranch is now closed
  cutoff-uniformly by the support-refined R-050 remainder, with decay
  `2^(-2 beta C)` for every `beta<3 alpha-1`. An orthogonal causal Carleson
  lemma identifies the sharp `s>1/2` sufficient threshold, but the balanced
  production decomposition needed for controlled CFAR is open. R-082 also
  gives a global four-row Pauli--Fierz square for the complete current. Only
  one row is rational, but state-dependent compression is not rootwise,
  target heat must average the Gram matrix, and future conditional covariance
  defects remain signed. Complete heat-lifted signed NEAR is therefore still
  open. R-083,
  `A13-CLASSII-CONTROLLED-POLYNOMIAL-CFAR-LINEAR-PAULI-FIERZ-FOREST-REDUCTION`,
  closes all three controlled polynomial `J_A` FAR rows in the complete
  stopped object for `C>=3`, with both endpoints and both predictable drifts
  retained. The exact remaining controlled CFAR object is the sum of three
  Cartan input-scale telescope squares with factor `3/(80P)`. The canonical
  `K_k` estimate spends the input coordinate once, but a production-floor-
  rescaled exact-harmonic witness refutes automatic global nonlinear-output
  orthogonality without excluding far-only or correlated martingale routes.
  R-083 also closes the exact linear Pauli--Fierz Gram/heat/secant/covariance/
  nine-block forest algebra. An adapted rational-zero fixture has negative
  linear-row zero chaos, so NEAR must keep the linear and rational rows
  recombined with the paid packet.
  R-084,
  `A13-CLASSII-ROOT-DIAGONAL-CARTAN-OU-LINEAR-PAULI-FIERZ-ABSORPTION`,
  diagonalises that Cartan square over complete probability roots and gives
  the exact far-projected OU-gradient target with all three derivative
  channels retained. A cumulative-tree model shows that root orthogonality or
  unweighted Poincare alone is not one-use; production spatial paracomposition
  remains essential. R-084 also form-absorbs the complete three-row linear
  Pauli--Fierz NEAR endpoint for regular orthogonal strict-past one-shot
  controls, with worst moment `30/7`. R-085,
  `A13-CLASSII-NONORTHOGONAL-CARTAN-SCHUR-RATIONAL-HESSIAN-BOUNDARY`,
  replaces the false output-orthogonality step by a nonorthogonal weighted
  causal Schur theorem. It would spend the triangular Cartan root/input sum
  once from a complete mixed production atom estimate with `s>1/2`; at
  `s=7/12`, `eta=1/12` its constant is `572.4472106721531...` and its gap
  factor is `2^(-7C/6)`. The atom estimates (4.10)--(4.11) remain unproved.
  R-085 also expands the rational endpoint exactly, form-absorbs its five
  unshifted families, and isolates the remaining coupled target (6.5): the
  signed shifted-Hessian pair plus the retained positive translated square.
  Third-derivative and rational-only fixtures rule out deletion, positivity,
  and fixed-square Schur shortcuts without refuting that coupled form bound.
  R-086,
  `A13-CLASSII-RATIONAL-TRANSLATED-WICK-PAYLOAD-COMPARABLE-REDUCTION`,
  rewrites that coupled target as one exact translated-Wick third-remainder
  normal form. A sharp cubic Sobolev theorem pays the base-frozen `Q` model
  with total `13/15` and moment `15/2`; all nonresonant and payload-comparable
  shifted branches are form-absorbed with `Q/G` totals `7/10` and `23/30`.
  The rational frontier is now only the coefficient-dominant high--high-to-low
  packet coupled to its endpoint square, Wick trace, and lower-chaos forest.
  Exact Taylor-Gram, endpoint-kernel, and vanishing-heat fixtures prohibit
  splitting it by positivity or a uniform inverse-Gram Schur complement.
  R-087 proves the complete mixed Cartan remainder's spatial estimate for
  `1/3<alpha<1/2` and `1/2<s<3alpha-1/2`, gives the exact rational
  eta-completion, and identifies the fixed-cutoff bounded smooth
  cylindrical-simple Boue--Dupuis core. R-088 then audits the exact R-084
  normalization: no outer `2^j` is present, so direct nonorthogonal Schur
  needs only `s>0` and `sum_k q_k`; at `s=eta=7/12` its constant is
  `16.30295538482827...`. Its exact sequential three-channel Cartan secant
  removes later control shells from the kth coefficient path, and its
  quartic Besov lemma gives the pure-control critical payload for `0<s<1`.
  The production two-point secant-to-quartic bridge or direct integrated CFAR
  remains open. On the rational branch, the eta debt cancels through the
  retained square only on centered covariance-matched predictable blocks;
  mean/covariance defects and the complete same-root causal packet survive.
  R-089,
  `A13-CLASSII-PROGRESSIVE-COVARIANCE-COMPRESSION-RATIONAL-MEAN-SPECTRAL-BOUNDARY`,
  proves the global polar/Douglas terminal contraction for every finite-cutoff
  cylindrical-simple progressive control, regardless of range overlap or
  revisit multiplicity. Hilbert martingale orthogonality gives the weighted
  terminal-shell one-use ledger and extends R-088's pure-control quartic
  terminal bridge to the general progressive class. Summing all physical
  control shells before squaring also gives an exact first-order Cartan
  Fourier trace and proposed a reduction through the global nonlinear
  coefficient-tail energy (3.12). At `s=1/4` the quartic subledger has powers
  `5/16,9/16` and slack `1/8`, but an exact harmonic rules out deleting the
  lower-order coefficient tails. On the rational branch, the
  Taylor-coordinate conditional form is universally nonnegative under
  covariance matching iff `L>=0` and `B_T+2 eta I>=0`. The production ray has
  `L/e=-1/432`, and a centered same-root fixture is negative before the
  complete endpoint is assembled.
  Finally, R-087 CORE makes full OVERLAP exactly equivalent to the `q=10/9`
  Nelson estimate. Complete temporal packets and controlled-shell assembly
  must therefore occur inside/before full OVERLAP, not after it.
  Sector A remains open.
  R-090,
  `A13-CLASSII-GLOBAL-UNPROJECTED-CARTAN-COEFFICIENT-LEDGER-NOGO-RATIONAL-FOREST-BOUNDARY`,
  claimed `b=grad c` and a conservative one-coefficient trace. R-092 audits
  that step as false for nonsymmetric production Jacobians: actual `b` uses
  transposed Jacobians while `grad c` does not. The independent R-090 witness
  still falsifies the global unprojected cutoff-uniform
  Sobolev relaxation R-089 (3.12) for every `s>0`: a fixed active-shell,
  current-root first-chaos component contributes once per root. That witness
  is root-diagonal and removed by the relative FAR projector, so projected
  CFAR remains viable and open. R-090 also corrects the R-089 branch
  conditioning (the two conditional variances are not one), proves the local
  raw rational endpoint expectation
  `-(35840/13689)c1 e phi(1)<0`, and enforces R-063 forest nonduplication.
  The sufficient frontier is now `H_C` for projected Cartan FAR, `H_N` for
  the complete nonduplicating signed rational/linear NEAR packet, and `H_A`
  for progressive complete-packet assembly inside OVERLAP. These are
  non-interchangeable obligations, not an iff decomposition. No gate status
  flips; Sector A remains open.
  R-091,
  `A13-CLASSII-PROJECTED-CARTAN-FULL-FRAME-SCHUR-JENSEN-TEMPORAL-BOUNDARY`,
  now proves the exact output-projected `C-5` gap ledger. At
  `alpha=2/5`, `gamma=7/12`, its weighted margins are `13/30` and `37/30`,
  and `H_C(C)<=2^(-7(C-5)/6)B_(7/12)^out`. The inherited cumulative `Z^6`
  upper majorant fails on a predictable rare fixture (`N^3` versus `O(1)`
  budgets), but the exact scalar one-mode production series repairs the same
  fixture with fixed-gap expectation `O(N^-4)` and a superexponential
  arbitrary-gap tail. The next Cartan theorem is therefore a saturation-aware,
  expectation-inside cumulative vector paracomposition bound, not another
  extracted translated-model norm.
  On NEAR, R-091 proves the complete linear+rational conditional Schur identity
  and the same-root Jensen residual retaining `r_C` and `J_D`. No fixed eta
  yields universal positivity, and the exact local full-frame loss is
  `-(3708/(21125P))e phi(1)<0`, without producing a post-paid counterexample.
  The next NEAR theorem is a signed Schur--Carleson estimate for the complete
  R-079 future/low/paid packet. Terminal paid nonduplication is now exact
  algebra; its uniform progressive estimate is not closed.
  R-080--R-091 also expose the separate
  `A13-CLASSII-FULL-PROGRESSIVE-REVISIT-EXTENSION`: R-075 graph recovery does
  not promote the regular lower bound to every Boue--Dupuis progressive
  control, and an exact one-mode witness proves non-density. Temporal Douglas
  factorisation preserves the complete packet algebra, while R-089 removes
  terminal CM revisit multiplicity altogether. The remaining PROG input is
  the nonlinear complete-packet lower bound, uniformly over the R-087 core.
  Projected Cartan `H_C`, complete signed NEAR `H_N`, assembly `H_A`, REG,
  and full OVERLAP remain. Once full OVERLAP is proved, R-087 CORE gives
  `q=10/9` Nelson directly.
  R-092,
  `A13-CLASSII-NORMALIZED-CARTAN-COMPENSATED-PERSPECTIVE-TRIANGULAR-COVARIANCE-FRONTIER`,
  repairs the transpose audit with the exact R-089 two-tail trace. The actual
  transposed `b` and `g=grad c` obey the same finite normalized-lift
  whole-product estimate; the `g` channel gains `2^(-2(m-j))`. At
  `(gamma,sigma,theta,p,q)=(1/4,4/15,3/10,6,3)`, root surplus `7/30` and
  Young slack `1/30`, the R-075/R-079 physical-prefix ledger proves the
  cutoff-uniform arbitrary-budget regular no-revisit one-shot `H_C` bound
  with gap `2^(-(C-5)/2)`. General progressive/revisit Cartan remains in
  `H_A`.
  On NEAR, R-092 Doob-decomposes the terminal `Theta_R(B_1)` energy and
  replaces the incomplete signed density by
  `K_k+P_(k-1)|d_k y|^2-B_(k-1):DeltaGamma_k`. The frozen and
  coefficient-conditioned moment-matched one-reveal branches close; the
  multistep derivative-feedback target is a weighted conditional-covariance
  deficit inside the complete packet. On assembly, exact covariance union
  and triangular entropy disintegration remove overlap multiplicity and
  retain kernel/revisit cost as fibre entropy, but the remaining free energy
  is exactly Nelson. Thus regular `H_C` is closed; complete `H_N`, triangular
  `H_A`, full OVERLAP, Nelson, and Sector A remain open.
  R-093,
  `A13-CLASSII-AUGMENTED-PERSPECTIVE-GIBBS-GAP-INFORMATION-BOUNDARY`,
  puts the augmented one-reveal density in an exact unconditional normal form;
  for centered symmetric even reveals it is precisely a coefficient/quadratic
  covariance. The production coefficient admits a bounded smooth local
  negative fixture for every fixed payment, but the genuine cutoff-two torus
  action is coercive on bounded smooth predictable shell-two sources, so this
  is not a paid counterexample. Same-root coefficient revelation costs mutual
  information (infinite for the smooth deterministic reveal), fixed source
  charts need not attain the Nelson value, and causal orthogonal triangular
  mixing is block diagonal. Under the R-087 payoff and finite-entropy
  hypotheses, the directed union of temporally faithful source charts equals
  the fixed-cutoff CORE value; near minimisers force both physical and fibre
  entropy gaps to zero. This retires only an independent uniform fibre reserve,
  not coupled use of the actual fibre term. The coefficient-unconditioned
  root-local `H_N` estimate and lossless `H_A` packet assembly into
  `OVERLAP_src` remain open; that source-union inequality is already the
  Nelson objective, not a separate downstream theorem.
  R-094,
  `A13-CLASSII-ROOT-LOCAL-GRAM-SECANT-FEEDBACK-BOUNDARY`, proves the regular
  centered Gram-secant estimate and two one-use feedback subchannels. It
  confines `2^(j-4k)` to positive quadratic curvature, pays the complete
  mixed secant by weighted Hardy with slack `1/3`, and pays the combined
  value--heat control prefix from only a fraction of the feedback square.
  R-095,
  `A13-CLASSII-FRACTIONAL-FEEDBACK-SQUARE-PERSPECTIVE-DOMINATION-BOUNDARY`,
  corrects the proposed reduced-global-square successor. The rootwise future
  reserve differs from the terminal square by an exact sign-indefinite
  moving-prefix defect, with scalar value `-1/4`. Fractional perspective
  positivity holds exactly under `2R>=theta B`; conditioning produces a
  resolvent-gap and terminal-mean debt, and the present absolute ledgers give
  incompatible `alpha<1` and `alpha>1` schedule requirements. Near `T_G^>`
  retains bounded Cartan curvature and is not paid by regular Cartan FAR.
  R-096,
  `A13-CLASSII-LOW-HERMITE-WICK-PREDICTABLE-BASELINE-REDUCTION`, now fixes
  the order: perform the complete R-077 fresh-root cancellation before
  rational projection, then analyze each predictable baseline. With
  `L_gap>C_supp+L_res`, its genuine coefficient-dominant `T_Q^>,T_G^>`
  region is support-empty and the fixed boundary collar is payable. Raw Wick
  also compresses exactly to coordinate Hermite ranks zero through two, but
  this supplies no spatial gain and direct Stein differentiation exposes
  adapted-selector derivatives. The next target is therefore one global
  moving adapted-base payment with all non-rational owners retained once.
  The two R-093 coarse critical rows and absolute per-revisit sixth-moment
  summation remain retired; complete `H_N`, REG, `OVERLAP_src`, Nelson, and
  Sector A remain open.
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

## Current priority view (refreshed 2026-07-28)

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
   proves the exact retained-square/Gibbs charge, terminal-backward heat
   martingale, controlled telescope, averaged PSD frame secant, and the
   strongest regular-control raw-current reduction. The new
   `A13-CLASSII-NPC-CONE-MARTINGALE-INJECTION-REDUCTION` diagonalises that
   current at `alpha=5/9`, identifies its aggregate CAT(0) cone, proves the
   strong Jacobi remainder and exact injection telescope, and records both a
   positive-floor shellwise no-go and a geometry-only flat-model no-go. The
   isolated `1:2` and `1:3` adapted losses are summable rather than global
   falsifiers.  `A13-CLASSII-TIP-SAFE-GROUPED-HARVEST-CARLESON-REDUCTION`
   closes the nonlinear harvest, full-score Carleson, uncontrolled Gaussian-
   tail, CAT(0) tip-secant, physical-distance, and global centered-form
   sublemmas. `A13-CLASSII-ENDPOINT-LIFTED-SCHUR-CAUSAL-GROUPING-REDUCTION`
   then proves the hybrid endpoint-lifted good/bad and global Schur bounds and
   coherent frozen-value causal grouping. It retires the literal affine full-
   score tangent and separate pure-control-defect payment, telescopes pure-
   control current creation exactly, and transfers only the centered scalar
   Gaussian defect to R-068. R-070 then proves the full Wick--Doob
   terminalization, exact raw/Wick trace restoration, Abel--Hardy covariance-
   tail payment, endpoint-defect equivalence, terminal Schur completion, and
   exact full weighted linear-frame symmetric--Cartan split. It also proves
   that automatic adapted resolver centering and a derivative-free Stein
   closure are invalid. R-071 corrects the false raw regularity attribution
   and closes the complete fixed-floor linear frame. R-072 classifies the
   phase-gauge kernel, avoids a singular frame inverse, and closes the matched
   strict-past same-shell diagonal with a single cutoff-independent random
   constant. Its exact terminal expansion proves that three off-diagonal
   families remain load-bearing. R-073 returns those families and the R-071
   linear term exactly to the R-069 telescope; after both first variations are
   restored the rank-jumping phase kernel cancels inside a projector-free
   terminal square. R-074 isolates the exact bare resonance, refutes automatic
   adapted Wick centering, closes the genuine local phase-orbit channel
   including its finite Wick anomaly, and proves the Besov sixth-moment
   payment. R-075 proves the projector-free invariant-current Taylor chart,
   the principal unshifted one-form and its sixth moment, and fixed-cutoff
   predictable graph recovery. R-076 then reconstructs the complete signed
   endpoint without duplication, sharpens the bare cubic payment to
   `X^(2/5)Y^(8/15)` with fifteenth-moment slack, and closes the
   control-independent cubic and nonresonant paraproduct branches. R-077
   replaces the proposed raw three-class root ownership by an exact Doob
   packet decomposition. It closes complete fresh-Gaussian packets in signed
   expectation and every payload-comparable `m<=r+L` orientation with the
   fifteenth moment, including ties and payload high--high-to-low outputs.
   R-078 reassembles the R-076 transport in the exact bounded
   Hessian-difference coordinate with `A^2 DA` payload and moment `30/7`.
   Canonical subtraction plus one causal projection defines the safe packet.
   The exact bilinear Doob lemma identifies the future-control innovation-
   bracket mechanism only for components admitting its factorisation. Its
   unweighted coefficient coordinate has one square-function bound, and the
   declared high-`U` principal closes with moment `60/19`. R-079 closes the
   exact expectation-level full-current and canonical safe-packet Doob
   decomposition, proves one weighted Cameron--Martin control square-function
   use, and proves the predictable base-current heat projection. The current
   child is `A13-CLASSII-FULL-PROGRESSIVE-REVISIT-EXTENSION`, after R-103
   closed complete regular `H_N` and `REG` and R-104 closed only the fixed-
   chart endpoint-owner defect with an explicit nonnegative Douglas slack.
   R-105 then retires generic monotonicity, the registered pathwise/absolute
   critical-Young route, and the all-law pointwise relative bracket while
   preserving a Gibbs-specific/time-integrated A9 successor. R-106 proves its
   exact endpoint-likelihood/KL and thermodynamic identities, retires total
   time integration as a standalone estimate, and rules out the tested
   pointwise-likelihood and raw input-leaf merge repairs. The prioritized
   coordinate is now a complete coherent output-frequency packet, with the
   direct complete source action still live. The uniform source-action/Nelson
   inequality remains open. R-107 closes the jointly frozen multi-row
   likelihood and the one-fresh-root past-measurable determinant. Rowwise
   predictability does not license their replacement by one global frozen
   resolvent. R-107 also proves that singleton output atoms and independent row
   normalizers are invalid and reduces the direct action to the complete
   predictable-baseline sum. Its adapted same-root
   complete-cluster/matrix-Carleson estimate remains the active target; the
   exact second-jet and carrier fixtures rule out only termwise or pure-KL
   shortcuts. R-108 sharpens that target: use the quotient-safe complete
   endpoint, keep mean and covariance debts coupled, and square the realized
   conditional cluster covariance before outer averaging. A bare average-first
   ledger needs the explicit remainder/sextic tradeoff; only the arbitrary-
   selector absolute PSD ledger paid solely from source energy plus one sextic
   is rejected. The uniform signed
   complete-cluster estimate, `OVERLAP_src`, Nelson, and Sector A remain open.
   The route to the regular closure was narrowed by
   R-080--R-102.
   R-080 closes the two distinct low objects for regular
   no-revisit controls. Far-shell square completion retains both feedback
   channels and leaves the localized predictable base-current tail `S_C`;
   target heat and the CM square function alone supply no root/shell decay.
   In the near region the explicit residual `A^2 DA` payload is predictable,
   but a hidden future high--high-to-low coefficient remains; bounded width
   has zero Young slack and universal rootwise positivity is false. R-081
   eliminates the polynomial far channel and proves genuine deterministic
   relative-gap decay for the Cartan current, but summing it rootwise repeats
   the critical `X^(1/2)Y^(1/2)` budget and the fixed-coefficient injection
   norm is `H^(1/2)`-critical. Its vector-valued Doob--Burkholder theorem closes
   the explicitly factorised first-order NEAR input budget, not the complete
   nonlinear coefficient: an exact secant--Jensen split exposes an upper-
    triangular defect invisible to `D_jA`. R-082 sums the FAR wedge first as
    one deterministic stopped-current square and closes its uncontrolled
    production part with support-refined `3 alpha-1` regularity. The exact
    remaining CFAR object contains the controlled moving endpoint and both
    predictable drifts. Its verified orthogonal causal Carleson route requires
    strict `s>1/2`; proving the balanced production input-scale decomposition
    is the next FAR task. For NEAR, R-082 compresses the complete production
    current to four global Pauli--Fierz rows, only one rational, but proves that
    this state-dependent compression does not preserve individual root blocks
    and that target heat must act on `C^T C`, not on `C` before squaring.
     R-083 removes every controlled polynomial row from this stopped object and
     identifies the exact three-Cartan input telescope with factor `3/(80P)`.
     Its production-floor harmonic fixture shows that `K_k` input smoothing
     does not supply global pairwise output orthogonality, so prove a correlated
     or signed Cartan CFAR estimate instead. R-083 also gives the complete
     linear Pauli--Fierz heat/forest algebra, while an adapted rational-zero
     fixture has negative linear-row zero chaos. At R-083 the NEAR target was
     the recombined linear-plus-rational heat-lifted adapted/signed estimate,
     retaining every present/future block, square, trace, innovation,
     compensator, forest term, and paid subtraction. R-084 now gives the exact
     root-diagonal Cartan and conditional OU-gradient formulation; root
     orthogonality alone is insufficient. Its arbitrary-budget theorem closes all three
     linear Pauli--Fierz rows for the regular orthogonal one-shot class, so the
     remaining NEAR target was the nonlinear rational row. R-085 now replaces
     the orthogonality route by a conditional nonorthogonal Schur theorem:
     prove the complete mixed production atom estimates (4.10)--(4.11) with
     `s>1/2`. It also form-absorbs all five unshifted rational families. R-086
     gives the exact translated-Wick normal form and pays every nonresonant or
     payload-comparable shifted branch. Prove only its coefficient-dominant
     high--high-to-low remainder with the endpoint square, Wick trace, and
     lower-chaos forest retained, then reassemble REG with the full paid
     packet. R-087 now proves the spatial half (4.10) of the complete mixed
     Cartan atom for 1/3<alpha<1/2 and every 1/2<s<3alpha-1/2; at alpha=2/5,
     s=7/12 has margins 7/30 and 13/30. Prove its directly averaged
     Cartan one-use ledger (4.11)
     without extracting a pathwise translated model norm. R-087 also gives an
     exact rational eta-completion, but its trace debt and coefficient-
     dominant packet remain open. R-088 corrects the exact target
     normalization: use the direct unweighted `s>0` Schur theorem, not the
     stronger outer-`2^j` sufficient architecture. Its sequential shell
     secant and quartic Besov lemma reduce the Cartan target to an
     expectation-inside production two-point bridge, or an equivalent direct
     integrated CFAR bound. For the rational target, keep the endpoint square,
     transformed Wick term, trace, backward heat, matrix-fractional Jensen
     defect, and lower-chaos forest inseparable; standalone eta-debt payment
     is a registered no-go. Then apply
   R-089's global progressive covariance compression and Hilbert martingale
   ledger, not one-shot density. The pure-control quartic terminal bridge is
   now valid on the full cylindrical-simple progressive class. Apply R-091:
   for Cartan, use the exact output ledger and prove
   `B_(7/12)^out <= 1+E sqrt(XY)`, or a form-sufficient variant with an
   absorbable `E X`, by a saturation-aware expectation-inside cumulative
   vector paracomposition estimate. Retain target heat, coherent multimode
   outputs, and the exact `q` multiplier; do not use either the falsified
   global unprojected R-089 ledger or the cumulative extracted `Z^6` majorant.
   For rational/linear NEAR, use R-094's proved regular centered-secant and
   value--heat control-prefix sublemmas inside one coefficient-unconditioned
   root-local identity for the complete R-079 future/low/paid packet. The
   factor `2^(j-4k)` is now certified only for positive quadratic Gram
   curvature; the complete mixed secant uses `2^(j-2k)` and weighted Hardy.
   Apply R-095: retain the full rootwise square through the perspective
   reconstruction and carry the sign-indefinite moving-prefix defect. Do not
   replace the rootwise reserve by a global terminal-square fraction unless
   the pure-future identity or predictable domination `2R>=theta B` is proved;
   a decaying `theta_j` does not repair the current separate absolute ledgers.
    R-097--R-102 complete the heat-lifted Gram and regular rational-current
   route. The complete heat-lifted Gram row telescopes to its
   terminal value, and the full R-099 owner
   `S_R+C_post/2-P_R-W_0` is exactly the ridge-independent terminal Wick
   increment. Under matching row/payment/baseline splits it is row-additive:
   the R-098 posterior Schur gap cancels against the R-100 complete-square
   gap, so never count both. Finer coefficient revelation only exchanges
    covariance and posterior-mean mass. In the regular strict-past no-revisit
    class, R-101 uses same-point value-gradient independence to prove
    `E_(j-1)<L_j,Delta Q_j>=0`. Cross-Doob terminalization assigns the complete
    raw-Wick block to the fixed low endpoint plus the already-paid R-100
    residual. Do not reuse the two raw Taylor families or apply another R-094
    secant. R-084 pays the three linear rows and R-071/R-085 pay the three
    unshifted rational current families. R-102 now closes the remaining
    `K_R=G^T L c+c^T B_1 c/2` row on the regular class: refund the separate
    base-cubic and R-086 `T_G^<=` current allocations, swap the exact `j<k`
    future-feedback sum into its later insertion index, condition the complete
    product at the strict past, and apply the proved annular shell/prefix
    ledger. The derivative column has slack `1/6`. The high-prefix
    coefficient branch has decay `2^(-k/14)` and limiting slack `1/14`;
    the separately retained fixed-low branch
    `X^(1/7)(1+Y)^(19/42)` has slack `17/42` and moment `42/17`.
    The estimate is uniform in cutoff and deterministic PSD target and future
    heat and leaves the complete heat-lifted
    terminal square unused. R-103 then performs the exact nonduplicating
   reassembly. The fixed-low raw-Wick difference remains in the two R-080/
   R-063 low owners and only its future reveal is a separate residual; the
   single signed R-078 paid difference is bounded under the fixed R-096
   collar; the separate R-086 `Q` orientations and `T_G^<=` current charge
   have zero extra multiplicity. Seven modules close complete regular `H_N`
   and eight modules close `REG`, with per-module shares `1/3080`, `3/700`
   and `1/3520`, `3/800`, respectively. Absolute balanced summation,
   separated multipliers, inverse-Gram Schur, and predictable-baseline
   deletion remain invalid shortcuts.
   Do not condition on the same-root coefficient for
   free, use a fixed source chart as a Nelson minimiser, posit an independent
   uniform fibre-entropy reserve, causally orthogonalise a nontrivial lower
   triangular source map, or amplify the local sign fixture into a paid
   counterexample. R-104 now proves the fixed-chart endpoint-owner identity:
   every active owner is recomputed once, the Cartan FAR row is the eighth REG
   module, and the terminal rational square stays internal to the shifted
   module. Representation-preserving subdivisions keep only the recombined
   endpoint; the source cost may be strictly smaller by the Douglas slack.
   The uniform directed source-union inequality is already the `q=10/9`
   Nelson objective through R-087/R-093, not an additional entropy theorem.
   Predictable heat is sufficient for disintegration, but same-root PSD heat
   admits no automatic extension. R-105 shows that common-root endpoints, not
   edgewise owners, are the invariant coordinates and that an artificial
   one-pair estimate cannot bypass physical cross-mode coupling. The exact
   successor is the uniform complete source action through a signed packet or
   Gibbs-specific/time-integrated A9 cancellation. Sector A remains open.
   R-106 proves the exact endpoint-likelihood/KL and thermodynamic identities,
   but shows that the total time integral by itself merely restates the open
   endpoint gap. Pointwise endpoint coercivity and bounded raw input-leaf
   merge tensorization, including the leafwise sextic repair, are now retired.
   R-107 proves the jointly frozen complete-output likelihood, the one-fresh-
   root past-measurable determinant, positive trace allocation, and exact
   direct source-action normal form. Rowwise predictability does not license a
   global frozen determinant. It also proves that legal atoms must be contraction-connected output
   clusters, that their determinant must be sequential/global, and that the
   adapted second jet cannot be split termwise. Continue with the same-root
   adapted complete-cluster/matrix-Carleson lower bound, retaining heat, trace,
   baseline, future feedback, rational recovery, the complete R-063 forest,
   and exactly one terminal root sextic. `OVERLAP_src`, Nelson, removals, the
   interacting measure, and Sector A remain open. R-108 additionally proves
   the exact subdivision-quotient and conditional mean/covariance identities.
   A bare average-before-square ledger fails without the explicit repair, and
   an absolute arbitrary-selector future-feedback HS/PSD ledger paid only by
   source energy plus one sextic fails; square-before-average is merely viable
   on the one-pair fixture. R-108 rewrites the successor as a nonvacuous uniform
   square-before-average or direct signed complete-cluster bound. It does not
   prove that bound; Sector A remains open.
   R-109 upgrades the one-pair square-before-average coordinate to an all-
   amplitude conditional theorem and fresh-pair supermartingale, repairs the
   strict-past covariance-cost placement, and closes the fixed-predictable-W
   signed second-jet owner. It simultaneously records the divergent full-pair
   direct floor and the exponential Stein-substitution no-go. Continue with
   one raw adapted same-root diagonal-to-decoupled or direct signed cluster
   estimate retaining cross-mode baseline/current, rational recovery, every
   visit, the full random-W forest, and one-use source/sextic ownership.
   `OVERLAP_src`, Nelson, removals, the interacting measure, and Sector A
   remain open. R-110 gives the exact random-W double-divergence and trace-
   corrected interpolation coordinates, while static-HS and uncentred
   nonlinear tangent-square shortcuts fail. R-111 proves the exact covariance
   faces, and R-112 proves the closed covariance-simplex compactification,
   factored uniform projective boundary through `D2`, analytic tail, origin
   cusp, and slice-wise face patches. The negative exact `D3` retires only
   coefficient-sign induction. R-113 adds effective rational projective,
   origin, and face classifiers, the sharper zero-amplitude `tau>=13` region,
   and two independent directed-rounding certificates for one strict mixed
   box. R-114 closes the entire zero-amplitude axis and the exact cone
   `0<=b=x/tau<=643/200`. R-115 closes `b>=643/200` by the moment-sharp
   four-moment left Radau majorant and packet-specific all-tilt skew geometry,
   proved once by a zero-pending outward Arb cover and independently by exact
   Bernstein/radical signs. The complete stationary scalar theorem is now
   closed. R-116 supplies the exact same-root endpoint quotient and owner
   firewall. R-117 supplies the full finite-dimensional rational-horizon
   classifier, uniform fixed-cutoff R-082 floor horizon, sharp joint frame
   constant, and strict canonical all-shell trace margins at q and 2q; the
   frozen bare-root normalizers therefore exist. Its exact same-shell phase
   fixture rules out local Lipschitz metric regularity without harming that
   trace route. R-118 supplies the finite-visit quotient theorem and a
   visit-count-free operator-valued R-068 estimate under absolute spectral
   variation. It also retires automatic diagonal-visit-to-terminal ownership
   and universal PSD random-`W` factorisation. R-119 reconstructs the minimum
   legal two-block/two-visit adapted test and gives the exact low-chaos trace
   criteria and strict bare-heat no-go. R-120 diagonalizes the complete A1
   coefficient, proves the covariance-horizontal `H2`/endpoint-`L6` bridge,
   pins the conditional variable-multiplier remainder, proves stationary
   six-row raw-current low-chaos cancellation, and flattens the rational
   Hessian into 21 fixed generators. The adapted `D0,D1` owner and first-order
   Cartan curvature remain: `-40/729` is reproduced, while its required
   `+40/729` companion is not observed. Continue by reconstructing the full
   rational square/trace/heat/low/R-063 owner on the R-119 chart, testing the
   companion, and cancelling or directly bounding the Cartan form before
   spending source energy and terminal sextic exactly once over the R-093
   directed union. Do
   not mistake strict per-shell normalizer existence for summability, and do
   not substitute a centered
   abstract tensor, full-Wick tensor normalizer, derivative-range test, or
   standalone gauge plane wave for the production root.
   Do not spatially differentiate the heat dummy, reuse uncontrolled tails for
   an adapted coefficient, separate the shifted multiplier from its signed
   endpoint block, pay terminal raw energy and injection separately, assume
   automatic centering or unproved Malliavin regularity, call the principal
   tensor gauge-complete, freeze an arbitrary adapted coefficient as finite
   chaos, or suppress the R-074 resonant branch.
   Do not spend the weighted control square function by a global Cauchy
   estimate, infer predictable BMO/Carleson control from expected budgets,
   manufacture spatial gain from an unweighted bracket, or assert generic
   adapted Wick carre-du-champ positivity. Do not identify target-space heat
   with spatial smoothing, treat bounded near width as positive Young slack,
   or infer a full progressive lower bound from the restricted R-075 graph.
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
