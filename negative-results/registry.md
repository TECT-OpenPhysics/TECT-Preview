# Negative-Result Registry

Failures are trust assets. Entries are never deleted. Format:
(branch/claim | failure mode | evidence | consequence). Tags: `R-` retracted
result, `F-` fired falsification gate, `NG-` no-go finding.

| Tag | Branch / claim | Summary |
|---|---|---|
| [NG-2026-legacy-convention](#ng-2026-legacy-convention) | old $r=K(0)$ no-condensation convention | wrong variable convention |
| [NG-2026-legacy-ordered-vacuum](#ng-2026-legacy-ordered-vacuum) | fixed ordered BCC vacuum as ground state | fluctuation restoration |
| [R-2026-legacy-newtonG-label](#r-2026-legacy-newtong-label) | Newton $G$ "independently predicted / T7" label | independent prediction missing … |
| [R-2026-legacy-rh-overclaim](#r-2026-legacy-rh-overclaim) | estimator-only Reading-H claim above T5 | controlled error bound missing |
| [F-2026-04-30-flat-cartan](#f-2026-04-30-flat-cartan) | Pillar-4 sub-task-2 "closure completed" (flat-Cartan forcing, Mechanism A) | falsified by $c_2(E)=-40\neq 0$ on canonical $\mathbb{CP}^2$ |
| [NG-2026-legacy-classical-hbar](#ng-2026-legacy-classical-hbar) | classical-field-theoretic derivation of $\hbar$ (8 routes) | each route fails … |
| [NG-2026-06-07-scscope-endpoint-joint](#ng-2026-06-07-scscope-endpoint-joint) | SC-SCOPE all-orders endpoint (B5/B1) | the individually-positive third-order channels … |
| [NG-2026-06-09-res5-bare-susceptibility-ratio](#ng-2026-06-09-res5-bare-susceptibility-ratio) | RES-5/GAP-2 closure via the BARE susceptibility-ratio bound (B1) | the bare Gaussian-sea ratio … |
| [R-2026-06-09-res5-ca0-doublecount](#r-2026-06-09-res5-ca0-doublecount) | RES-5 a0-skeleton estimate $c\,a_0\sim0.002$ (B1) | the estimate took $\|\Sigma_2^{\rm pd}\|/\Delta F_{\rm margin}\sim0.04$ … |
| [AUDIT-2026-06-09-res5-survival-overclaim](#audit-2026-06-09-res5-survival-overclaim) | RES-5 "survives at STRONG EVIDENCE, thin" (B1; certificate v1.0) | the higher-skeleton tail bound … |
| [F-2026-06-10-res5-projection-route](#f-2026-06-10-res5-projection-route) | RES-5 endpoint closure via the pattern projection $\chi_{\rm proj}\le0.82$ (B1) | the screened response at the BCC $\{110\}$ modulation transfers gives … |

| [R-2026-07-16-N001-BCC-SEED-COLLAPSE](#r-2026-07-16-n001-bcc-seed-collapse) | N-001 q1a BCC-seed sweep | stored fields do not retain q0-shell BCC modulation |
| [AUDIT-2026-07-17-A3-GALERKIN-BALL-UNDERBOUND](#audit-2026-07-17-a3-galerkin-ball-underbound) | A3 full-production discretization T6 v2.1 | continuum H2 ball reused for exact-Galerkin trajectory without proof |
| [AUDIT-2026-07-19-A3-SHARED-BUNDLE-INTEGRITY](#audit-2026-07-19-a3-shared-bundle-integrity) | A3 shared renormalisation bundle | stale MANIFEST listed two absent notes and a mismatched README hash |
| [AUDIT-2026-07-19-A4-VERIFIER-TIER-DRIFT](#audit-2026-07-19-a4-verifier-tier-drift) | A4 constructive one-command verifier | v1.0.0 still emitted its pre-promotion T5-to-T6 boundary after T6 enactment |
| [AUDIT-2026-07-19-A4-Q0-ZERO-SHELL-BOUNDARY](#audit-2026-07-19-a4-q0-zero-shell-boundary) | A4 constructive referee package v2.0 | max-shell trace notation did not isolate the zero mode at the declared q0=0 endpoint |
| [AUDIT-2026-07-19-A5-DEPENDENCY-PIN-DRIFT](#audit-2026-07-19-a5-dependency-pin-drift) | A5 branch-aware synthesis manifest v1.0 | A3/A4 publication work made the frozen component hashes and four-bundle count stale |
| [AUDIT-2026-07-19-A5-BUNDLE-NOTE-PDF-COMPLETENESS](#audit-2026-07-19-a5-bundle-note-pdf-completeness) | A5 scoped T5 capstone initial bundle build | original-path A4 v2.1 source was copied without its paired PDF |
| [AUDIT-2026-07-20-SECTOR-A-BASELINE-STATUS-DRIFT](#audit-2026-07-20-sector-a-baseline-status-drift) | Sector-A live records after A5 publication | stale sign-off, mass-alias, gate, and roadmap wording contradicted enacted claims |
| [NG-2026-07-20-A6-BARE-CLASSII-L1](#ng-2026-07-20-a6-bare-classii-l1) | direct A4-style bare extension to full derivative Class-II | positive linear derivative-pair contraction defeats uniform Gaussian L1 control |
| [NG-2026-07-20-A6-NAIVE-W-SUBTRACTION-NONUNIFORM](#ng-2026-07-20-a6-naive-w-subtraction-nonuniform) | literal fixed-parameter leading-W subtraction | homogeneous amplitudes escape as N^(1/4) and the raw lower bound falls as -N^(3/2) |
| [NG-2026-07-20-A7-W-ZEROSET-BARE-INFERENCE](#ng-2026-07-20-a7-w-zeroset-bare-inference) | pure-third bare concentration inferred from the conditional contraction | a full Class-II plane-wave null has W_eps > 0 |
| [F-2026-07-21-A7-INFINITESIMAL-COMMUTATOR-FORM](#f-2026-07-21-a7-infinitesimal-commutator-form) | A7 commutator-alone all-eta sufficient bound | same-shell resonant translation forces a positive relative-bound threshold |

<a id="audit-2026-07-20-sector-a-baseline-status-drift"></a>
### AUDIT-2026-07-20-SECTOR-A-BASELINE-STATUS-DRIFT -- Sector-A live-record alignment

**Failure mode:** Several current-facing records retained pre-approval or
pre-promotion text: the A1 identity and scalar cards still requested sign-off;
the scalar card incorrectly described the canonical solver field as `mu2=r`;
A2 smoothing and A3 discretization gates were still OPEN despite their
operator-confirmed PUBLISHED T6 packages; A5 retained candidate/fallback text;
and the roadmap/sector README still described already completed work as open.

**Evidence:** Direct comparison of the live `status.json` cards, current
14/14 A1 checker, A2 61/61 package, repaired A3 124/124 package, and A5 35/35
PUBLISHED package against their claim cards, `claims/GATES.md`, `ROADMAP.md`,
`RESULTS-LEDGER.md`, and `theory/sector-A-foundation/README.md`.

**Consequence:** Administrative/provenance repair only. No theorem, tier, or
immutable historical bundle is withdrawn. The canonical N-001 convention is
`mu2_shell` for the shell mass and separately reconstructed `r_zero`; alias
`mu2=r` remains forbidden. A6 imports only the repaired current convention.

<a id="ng-2026-07-20-a6-bare-classii-l1"></a>
### NG-2026-07-20-A6-BARE-CLASSII-L1 -- bare full-Class-II constructive route

**Failure mode:** The A4 scalar bounded-density/dominated-convergence proof
cannot be transferred unchanged to the unrenormalised full derivative
Class-II energy. Under the canonical six-real Gaussian convention and sharp
cube cutoff, the point covariance converges but the derivative covariance has
a positive linear slope. Exact conditional contraction gives
`E F_ClassII,N / N -> kappa_II>0`.

**Evidence:** `A6-CLASSII-UV-POWER-COUNTING`; analytic cube Riemann-sum and
conditional Wick identities; primary 19/19, non-importing independent 12/12,
and integrated 44/44 execution. The field-dependent leading contraction is the
nonconstant rational term `delta_cube*N*W_eps(Psi)`; a vacuum constant cannot
cancel it.

**Consequence:** The unchanged A4 proof route is eliminated, but a bare
degenerate limit concentrated on `W_eps=0` and a renormalised measure are
neither classified nor ruled out. `A6-CLASSII-K-COMPOSITE-DEFINITION` now
closes the fixed-floor current itself; active work is the separate
`A6-CLASSII-COUNTERTERM-CLOSURE` and full-field bare-concentration gates, with
stability and tightness reproved for any proposed renormalised weight.

<a id="ng-2026-07-20-a6-naive-w-subtraction-nonuniform"></a>
### NG-2026-07-20-A6-NAIVE-W-SUBTRACTION-NONUNIFORM -- literal leading-W subtraction

**Failure mode:** The direct prescription
`F_N^naive=F_core+F_II,N-delta_cube*N*int W_eps` with all lower-order
production coefficients fixed is not cutoff-uniformly coercive. A homogeneous
field supported in the first two components has `J_A=K_A=F_II,N=0`, while the
negative local counterterm remains. The sextic term balances it only at
`|Psi_N|=Theta(N^(1/4))`, and the trial energy density is
`-Theta(N^(3/2))`.

**Evidence:** `A6-CLASSII-K-COMPOSITE-DEFINITION`; exact Pauli/Fierz bounds,
homogeneous asymptotics, and primary 29/29 plus non-importing independent
16/16, integrated 64/64 execution. At the production point,
`|Psi_N|/N^(1/4) -> 0.198135127774404` and the trial energy-density coefficient
is `-3.26710156480221e-05` per `N^(3/2)`.

**Consequence:** A vacuum-energy recentering cannot repair the escaping
amplitude. A running family-mass counterterm can restore nonnegativity but
introduces a new renormalisation condition and may force concentration on the
pure-third-component subspace. Counterterm closure remains open. The separate
full-field bare-concentration gate is not decided by this no-go or by either
local proxy.

<a id="ng-2026-07-20-a7-w-zeroset-bare-inference"></a>
### NG-2026-07-20-A7-W-ZEROSET-BARE-INFERENCE -- conditional contraction does not classify bare null branches

**Failure mode:** The zero set of the positive conditional derivative-pair
contraction `W_eps` is not the zero set of the pathwise full Class-II energy.
For a common-phase plane wave `Psi(x)=exp(i*k.x)u`, direct substitution gives
`J_A=K_A=F_II=0` for every generator, including when the first doublet is
active and `W_eps(u)>0`. Therefore a large conditional Gaussian mean cannot by
itself force the unmodified Gibbs law onto the pure-third subspace.

**Evidence:** `A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE`; analytic common-phase
cancellation; primary 29/29, non-importing independent 17/17, and integrated
74/74 execution. The independent route evaluates the currents directly and
finds maximum residual `2.22e-16` while `W_eps=0.0534857142857`.

**Consequence:** The full bare problem must classify and compare all branches
of the Class-II null set, including active-doublet phase configurations. The
two local contraction proxies remain valid as local calculations but cannot
select a global branch. No pure-third concentration, tightness, or scalar A4
reduction is inferred.

<a id="f-2026-07-21-a7-infinitesimal-commutator-form"></a>
### F-2026-07-21-A7-INFINITESIMAL-COMMUTATOR-FORM -- commutator-alone all-eta form bound

**Failure mode:** The proposed
`A7-CLASSII-TILTED-COMMUTATOR-FORM-BOUND` required the exact dyadic
coefficient increment to be infinitesimally form-bounded by entropy and the
sextic norm with the same arbitrary `eta>0`. On the physical scalar ray,
`g_K=cos(Kx)+cos(Ky)-cos(K(x+y))` produces a negative same-shell resonant
increment. Under the covariance-contracted cutoff Gaussian tilt with
Cameron--Martin mean amplitude `A=tK`, the commutator, entropy, and sextic
contributions all scale as
`K^6`. The inequality therefore has a strictly positive necessary
relative-bound threshold and cannot hold for every `eta>0`.

**Evidence:** `A9-CLASSII-SMART-PATH-CANCELLATION` no-go addendum; exact
Fourier averages `<g|grad g|^2>=-1` and
`<g^2|grad g|^2>=5/2`; primary 24/24, non-importing Pauli-current independent
17/17, and integrated 56/56 execution. At the production point with
`epsilon=0.3`, `M_6=4412239/1600000`,
`eta_min=2.48914320732e-4`, and the explicit `eta=1e-4` violation margin is
`8.89605767815e-6` per volume and `K^6`. The covariance trace is only
`O(K^3)`.

**Consequence:** The former sufficient gate is retired as false, but the A9
scoped T5 exact smart-path and frozen-shell theorem remains valid. The same
witness has positive frozen source energy and ratio
`|C_j|/Q_j^fr -> 3/16`; this is its zero-extra-budget neutralisation fraction,
not an absolute lower bound when positive entropy and sextic budgets are
allowed. The active replacement is
`A7-CLASSII-FROZEN-ENERGY-RELATIVE-COMMUTATOR-BOUND`, which must retain a
fixed fraction of the complete covariance-normal frozen term and close the
remaining entropy, quartic, and sextic budgets. The self-coupled Nelson bound
and interacting Gibbs measure remain open.

<a id="ng-2026-legacy-convention"></a>
### NG-2026-legacy-convention — old $r=K(0)$ no-condensation convention

**Failure mode:** wrong variable convention

**Evidence:** legacy: Math426 cascade

**Consequence:** replaced by $r_{\rm braz}=K(q_0)=\mu^2$; A1-KERNEL-CONV registers the corrected convention

<a id="ng-2026-legacy-ordered-vacuum"></a>
### NG-2026-legacy-ordered-vacuum — fixed ordered BCC vacuum as ground state

**Failure mode:** fluctuation restoration

**Evidence:** legacy: Reading-H selection chain

**Consequence:** Reading-H selected instead (B1-RH-ENUM); ordered-vacuum reading retired

<a id="r-2026-legacy-newtong-label"></a>
### R-2026-legacy-newtonG-label — Newton $G$ "independently predicted / T7" label

**Failure mode:** independent prediction missing ($a_{\rm BCC}$ fixed by $G_{\rm obs}$)

**Evidence:** legacy: governance audit

**Consequence:** downgraded to RELATION DERIVED / VALUE MATCHED; managed as T6/T7-SPLIT (C5-NEWTON-G)

<a id="r-2026-legacy-rh-overclaim"></a>
### R-2026-legacy-rh-overclaim — estimator-only Reading-H claim above T5

**Failure mode:** controlled error bound missing

**Evidence:** legacy: estimator chain audits

**Consequence:** remains T5 CLOSED@ESTIMATOR-GRADE until ESTIMATOR-UPGRADE and STEP-5B close (B1-RH-ENUM)

<a id="f-2026-04-30-flat-cartan"></a>
### F-2026-04-30-flat-cartan — Pillar-4 sub-task-2 "closure completed" (flat-Cartan forcing, Mechanism A)

**Failure mode:** falsified by $c_2(E)=-40\neq 0$ on canonical $\mathbb{CP}^2$

**Evidence:** legacy: Math174, Math245 rollback

**Consequence:** sub-task 2 back to T3 (D2-GAUGE-FORCING); Mechanism A refuted; Mechanism B insufficient alone

<a id="ng-2026-legacy-classical-hbar"></a>
### NG-2026-legacy-classical-hbar — classical-field-theoretic derivation of $\hbar$ (8 routes)

**Failure mode:** each route fails (4 Math59 + 3 Math59-v3 + 1 R5)

**Evidence:** legacy: Math59, Math59-v3, R5 record

**Consequence:** $\hbar$ stays an external phenomenological parameter; phase-transition programme registered at T2 (E2-HBAR-ORIGIN)

<a id="ng-2026-06-07-scscope-endpoint-joint"></a>
### NG-2026-06-07-scscope-endpoint-joint — SC-SCOPE all-orders endpoint (B5/B1)

**Failure mode:** the individually-positive third-order channels (sunset x1.13, quartic-difference x1.29, tadpole 0) JOINTLY over-consume the endpoint layer margin by x1.32 -> joint endpoint x0.757 < 1

**Evidence:** scscope_joint_endpoint.py 5/5; scscope-endpoint-joint-assessment v1.0

**Consequence:** SC-SCOPE stays OPEN at the endpoint; B1 T6 selection UNAFFECTED (SC-SCOPE is a named hypothesis); path = joint incompatible-pairing argument or sharper per-transfer bounds.

**UPDATE 2026-06-07** (scscope_joint_pairing.py 4/4, scscope-joint-pairing v1.0): the joint incompatible-pairing was carried out in its MOST FAVOURABLE form and recovers only x0.757 -> x0.905 < 1; the sunset ALONE is x1.076 (near-saturating). Per-transfer/pairing refinements EXHAUSTED. Remaining routes: a sharper STEP-5B endpoint floor (rho >~ 3.9 at I=2e-3) OR accept second-cumulant scope at the I=2e-3 endpoint (all-orders lift is FEASIBLE for I<=1e-3, floor x8.8). B1 T6 unaffected

<a id="ng-2026-06-09-res5-bare-susceptibility-ratio"></a>
### NG-2026-06-09-res5-bare-susceptibility-ratio — RES-5/GAP-2 closure via the BARE susceptibility-ratio bound (B1)

**Failure mode:** the bare Gaussian-sea ratio $\chi^{(3)}/\chi^{(2)}\sim 4\int G^3/\int G^2 = 9.05 > 1/(2a_0)=5.23$, so $r_2(\text{bare})=0.866>1/2$; bare ratios $\int G^{n+1}/\int G^n\to1/\hat r\approx2.5$ (strong-coupling, growing)

**Evidence:** res5_susceptibility_ratio.py 4/4; res5-susceptibility-ratio-bareroute v1.0

**Consequence:** the elementary bare-ratio route is ELIMINATED; B1 T6 on {H-LAYER} UNAFFECTED (no claim withdrawn); the genuine residual is the COMMON-MODE-SUBTRACTED ratio $\chi_{\rm pd}^{(k+1)}/\chi_{\rm pd}^{(k)}$ (SC-SCOPE's ~4% n=3 is the subtracted, not bare, value) -- a strong-coupling research frontier.

**ANNOTATED 2026-06-09** (res5-oneloop-loop-disentangling v1.0): the bare chi^(k)~int G^k are the condensate-expansion coefficients of the EXACT one-loop log-det (converges, peak node 0.574<1), NOT the loop expansion -- so the bare-ratio 9.05 does NOT bear on RES-5; RES-5 is the LOOP expansion (2-loop+, SC-SCOPE=two-loop). Framing conflation self-caught; residual corrected to the higher-loop difference.

<a id="r-2026-06-09-res5-ca0-doublecount"></a>
### R-2026-06-09-res5-ca0-doublecount — RES-5 a0-skeleton estimate $c\,a_0\sim0.002$ (B1)

**Failure mode:** the estimate took $|\Sigma_2^{\rm pd}|/\Delta F_{\rm margin}\sim0.04$ (the FREE-ENERGY sunset ratio) and multiplied by $|\delta G_*^{\rm pd}|=O(a_0)$ -- double-counting $a_0$, since $\Delta\Gamma_2^{\rm pd}=|\Sigma_2^{\rm pd}|\,|\delta G_*^{\rm pd}|$ already IS the free-energy ratio

**Evidence:** res5_sunset_norm_map.py 4/4; res5-sunset-selfenergy-norm-certificate v1.1

**Consequence:** the $c\,a_0\sim0.002$ figure is RETRACTED; the certificate quantity is the free-energy ratio $|\Delta\Gamma_2^{\rm pd}|/\Delta F_{\rm margin}$ directly, whose LEADING (sunset) value IS the SC-SCOPE certified joint $\times1.040\to\times1.13$. B1 T6 on {H-LAYER} UNAFFECTED (no claim withdrawn).

<a id="audit-2026-06-09-res5-survival-overclaim"></a>
### AUDIT-2026-06-09-res5-survival-overclaim — RES-5 "survives at STRONG EVIDENCE, thin" (B1; certificate v1.0)

**Failure mode:** the higher-skeleton tail bound $C_{\rm higher}\le\text{leading}/(1-0.49)\approx2\times\text{leading}$ is SAME-ORDER (screened-finite), NOT sub-dominant; against the thin SC-SCOPE joint $\times1.040$ the slack is only $1-1/1.040\approx3.85\%$ ($C_{\rm higher}$ must be $<0.040\,C_{\rm leading}$), which a same-order tail does not respect

**Evidence:** operator adversarial review 2026-06-09; res5_sunset_norm_map.py 4/4 (slack assert); res5-sunset-selfenergy-norm-certificate v1.1

**Consequence:** v1.0's RES-5-survival / STRONG-EVIDENCE-thin verdict is RETRACTED; RES-5/GAP-2 returns to OPEN. The self-energy/free-energy correction (R-2026-06-09-res5-ca0-doublecount) is RETAINED. B1 T6 on {H-LAYER} UNAFFECTED. Next: res5-tail-budget-closure (prove the SC-SCOPE-joint $\to\Delta\Gamma_2^{\rm pd}$ identity + a tail budget $C_{\rm higher}<0.04\,C_{\rm leading}$).

**ANNOTATED 2026-06-09** (res5-tail-budget-closure v1.0, operator-ACCEPTED): RES-5/GAP-2 OPEN $\to$ ENDPOINT-LOCALISED -- the screened tail $C_{\rm higher}/\Delta F_{\rm margin}\approx C_G a_0(I)$, $a_0\propto I$, fits the third-cumulant slack with $\ge27\times$ margin for $I\le10^{-3}$ (tail/slack $0.012,0.036$; STRONG EVIDENCE CLOSED off endpoint) and is marginal/estimate-undetermined ONLY at the $I=2\times10^{-3}$ endpoint (tail/slack $1.22$). RES-5 is thus a single endpoint boundary problem, not a bulk obstruction (34x localisation). B1 unaffected (T6 on {H-LAYER}). Next: res5-endpoint-2pi-bound (prove $C_{\rm higher}(2\times10^{-3})<0.0385\,\Delta F_{\rm margin}$, i.e. an ~18% tail tightening or a slightly thicker certified slack).

**FURTHER ANNOTATED 2026-06-09** (res5-endpoint-2pi-bound v1.0, 5/5): ENDPOINT-LOCALISED $\to$ STRONG EVIDENCE -- the endpoint tail $C_G a_0=0.047$ is BRACKETED, slack$_{\rm proved}$(0.0385) $<$ tail $<$ slack$_{\rm verified}$(0.0758); it closes at the realized (verified) floor $K_{\rm floor}\le0.52T'$ ($\rho_{\rm lat}=12.6$) with a 38% margin, or at the proved slack whenever $\chi_{\rm proj}<0.82$. The marginalit-y is an ARTEFACT of the over-conservative floor. RES-5's residual UNIFIES with SC-SCOPE's floor sharpening (one inequality $K_{\rm floor}\le0.52T'$ discharges BOTH). B1 unchanged (T6 on {H-LAYER}); rigorous T6 pending the proved $0.52T'$ floor or $\chi_{\rm proj}\le0.82$.

**CORRECTED 2026-06-10** (status reconciliation): SC-SCOPE is LIFTED@THIN-CERTIFIED via the QUARTIC route (scscope-quartic-normalisation-certificate), NOT the floor route (whose standalone lift was retracted); canonical B1={H-LAYER}. So the RES-5 endpoint floor-$\kappa$ tightening unifies with B1's DR-2 (unrestricted-class additive-energy) residual, NOT with SC-SCOPE. Route-A findings (archived): PROVED refinement $K\le T'(1-|a|_4^4/I^2)$ (Cauchy-Schwarz + $t=0$); EXACT complete single-shell scan worst $\kappa=K/T'=0.75$ (corrects the incomplete-sample 0.52); worst-case $\kappa<1$ over the dense admissible class is additive-energy/circle-incidence-adjacent (= DR-2).

**RESOLVED@LATTICE 2026-06-10** (res5-dr2-kappa-bound v1.1): the endpoint closes UNCONDITIONALLY over B1's LATTICE T6 scope -- the lattice additive-energy bound R-026 is T7 UNCONDITIONAL (divisor + Dirichlet class-number, decoupling-free): $E_+\le(1+C_\epsilon R^\epsilon)N^2$, so $K_{\rm floor}\le C_\epsilon R^\epsilon<26.2$ over the admissible range (enumerated $\le12$). The remaining 'dense/arbitrary-Q open' piece is the UNRESTRICTED DR-2 ($E_+\le N^{2+\epsilon}$, T6-cond on Bourgain-Demeter decoupling), which is NOT B1's lattice scope. RES-5/GAP-2 axis DISCHARGED within B1's scope; B1 unchanged (T6 on {H-LAYER}; deepest remaining piece = Prop-A/RES-1).

**GRADE-CORRECTED 2026-06-10** (res5-dr2-kappa-bound v1.2; operator: 'not unconditional T7'): the 'UNCONDITIONAL' above is WITHDRAWN. R-026 is T7 MODULO TEXTBOOK NT, and the $C_\epsilon R^\epsilon<26.2$ admissible-range sufficiency + the carrier-richness $\chi(P)\!\lesssim\!T'$ link are residuals (operator-decisions; R-026/R-027 did NOT flip DR2-SHARE). HONEST grade: ENUMERATED competitors close EXACTLY ($K_{\rm floor}\le12<26.2$, so RES-5 is not an independent B1 blocker); FULL lattice class = STRONG EVIDENCE (R-026 + exact anchor); arbitrary-Q = T6-cond on decoupling. NOT an unconditional theorem. B1 unchanged (T6 on {H-LAYER}).

<a id="f-2026-06-10-res5-projection-route"></a>
### F-2026-06-10-res5-projection-route — RES-5 endpoint closure via the pattern projection $\chi_{\rm proj}\le0.82$ (B1)

**Failure mode:** the screened response at the BCC $\{110\}$ modulation transfers gives $\chi_{\rm proj}=f_{\rm avg}/C_G=0.613/0.492=1.25>1$ -- the bubble $\chi_0(k)$ is forward-peaked, so screening is MAXIMAL at $k=0$ ($C_G=0.49$) and WEAKER at $\{110\}$ ($f=0.57$--$0.73$); the modulation is not in the maximally-screened channel

**Evidence:** res5_projection_factor.py 5/5; res5-projection-factor-bound v1.0

**Consequence:** the projection closure lever is ELIMINATED; the operator-norm tail $C_G a_0=0.047$ is corrected UPWARD to $f_{\rm avg}a_0=0.059$ (the a0-skeleton $C_G$ estimate was forward-channel optimistic); the endpoint closes ONLY at the verified floor ($0.059<0.0758$, 23% margin), NOT conservative, and rests SOLELY on the DR-2 floor route. Off-endpoint ($I\le10^{-3}$) closure UNAFFECTED. B1 T6 on {H-LAYER} UNAFFECTED.



<a id="r-2026-06-23-b3-bcc-structural-selection"></a>
### R-2026-06-23-b3-bcc-structural-selection — fixed-ordered BCC structural selection ($F_{\rm BCC}<F_{\rm FCC}<F_{\rm SC}$)

**Failure mode:** single-shell SMA ranking inversion + disordered collapse

**Evidence:** Math194 re-run (BCC rank 9 of 10; lamellar rank 1); Math400 (T0 binding: at $\mu^2=+0.005$ all lattices collapse to the disordered $F=0$ state, the SMA "BCC minimum" is a saddle; Math383 $K_4/K_6$ table refuted). archive/legacy/notes/Math194, archive/legacy/notes/Math383.

**Consequence:** `B3-BCC-STRUCT` RETIRED/REFUTED (T0). The original "BCC energy condensate structure is selected" claim is withdrawn. The operator (2026-06-23) rejected the reframe of B3 onto B1: B1's $\Delta F_{\rm enum}[\mathcal R]>0$ is only a RELATIVE ranking within the tested ordered-reading ensemble $\mathcal E_{\rm tested}$; it does NOT imply $F[\mathcal R_H]<F[0]$ nor $H_{\mathcal R_H}\succeq0$ under unrestricted variations, and must not be conflated with Math400's disordered-collapse/saddle result. Only the restricted ranking projection survives, carried as the separate B1-dependent card `B3-RH-TESTED-STRUCTURE-RANKING` (T4, estimator grade). Physical BCC condensate existence/stability/global selection is NOT established; re-establishing it requires certifying $F[\Psi_{\min}]<F[0]$, $\lambda_{\min}^\perp\ge0$ under symmetry projection, and $N\to\infty$ on the canonical PDE background.

<a id="audit-2026-07-17-a3-galerkin-ball-underbound"></a>
### AUDIT-2026-07-17-A3-GALERKIN-BALL-UNDERBOUND -- A3 v2.1 exact-Galerkin evolution underbound

**Failure mode:** The v2.1 evolution argument assigned the restarted exact-Galerkin solution the continuum energy-derived $H^2$ envelope without proving $F(P_Nu)\leq F(u)$. The former independent 10/10 audit did not reconstruct this trajectory ball or the downstream Lipschitz/Gronwall chain; selected displayed upper bounds were also rounded inward.

**Evidence:** Adversarial comparison of the v1.0 quantitative-majorant implementation and v2.1 referee note; repaired primary audit 21/21; non-importing full-chain audit 24/24; integrated verifier 124/124; corrected referee note v2.2.

**Consequence:** The v2.1 note and original PUBLISHED bundle are superseded, not deleted. T6 was treated as challenged until the repair derived $F(P_Nu(\tau))\leq E_+(M_2)$, a separate uniform Galerkin $H^2$ envelope, common-ball evolution constants, directed rounding, and a subtraction-free conservative logarithmic Gronwall enclosure. T6 is re-enacted only by replacement bundle `A3-Full-Production-Discretization-T6-Repair-260717`, digest `6d15d165a73d3a2af07e10fce07394ce8b83311e571ba2aae2fbbc61c31d2e41`.

## Process-grade negative results (carried as lessons, enforced in governance)

- Round-summary over-claim incident (legacy 2026-04-24): higher-tier summaries
  may never outrun pillar-level notes → single-source-of-truth rule
  (`status.json` → generated `CLAIMS.md`).
- Five-rollback cluster (legacy 2026-04-28/29): each rollback was catchable by
  one elementary quantitative sanity check → mandatory sanity-check rule
  (`governance/verification-standard.md` §6).
- Tier-overstatement cluster (legacy 2026-05-27): rushed multi-pillar passes
  produce overstatement → one-claim-per-turn and promotion-procedure rules
  (`governance/claim-standard.md` §5).

## History

- 2026-06-05 — Registry seeded from the legacy record during bootstrap.

## AUDIT-2026-06-08-scscope-lift-overclaim

**Type**: AUDIT (self-caught overclaim; result downgraded, not a counterexample).

**Claim withdrawn**: the SC-SCOPE all-orders endpoint LIFT (scscope-floor-sharpening v1.1/v1.2, R-029;
B1 {H-LAYER,SC-SCOPE}->{H-LAYER}).

**Error**: the lift computed the endpoint closure as paired = rho_lat/(1+max[R_s+R_q]) = rho_lat/2.872 (the
joint-PAIRING formula). That formula's linear-in-rho scaling is only a LOCAL approximation at rho=2.6. The
physically-correct ADDITIVE bookkeeping (scscope_joint_endpoint.py) treats the sunset as an ABSOLUTE third-cumulant
cost C_sunset = composed/1.13, which does NOT vanish as the second-order floor thickens; the joint ratio therefore
SATURATES at x1.13 rather than growing linearly. Under it the sharpened floor gives x0.945 (conservative K_floor<=T')
to x1.026 (verified K_floor<=0.52T') -- MARGINAL, not the claimed x2.28; the true threshold is rho>=9.85, not 3.9.

**Disposition**: SC-SCOPE RESTORED as a B1 named hypothesis; B1 {H-LAYER} -> {H-LAYER, SC-SCOPE}, tier UNCHANGED T6.
The PROVED floor sharpening (K_floor <= T'(M), R-029) stands as a real PARTIAL advance (additive endpoint joint
x0.757 -> x0.95-1.03). scscope_joint_correction.py 5/5 verifies the corrected bookkeeping.

**Lesson**: run the conservative/established bookkeeping (not a favorable local formula) before claiming a closure.
This is the adversarial-self-review the meta-feedback requires; it was omitted in the lift and caught during the
follow-up rigorization.

<a id="r-2026-07-16-n001-bcc-seed-collapse"></a>
### R-2026-07-16-N001-BCC-SEED-COLLAPSE ??N-001 q1a BCC-seed sweep does not retain a q0-shell BCC branch

**Failure mode:** all 48 stored `q1a_bcc_search` N32 outputs that contained both
`Psi_star.npy` and `proof_results.json` lost their intended q0-shell/BCC
modulation. The largest audited BCC/total Fourier fraction was approximately
$9.8\times10^{-9}$; the 15 runs that passed the stored Phase-0 and projected
Phase-2 fields had q0-shell fractions at most approximately $2.4\times10^{-12}$.

**Evidence:** 2026-07-16 Fourier audit of the stored fields, recorded in
`reviews/2026-07-16-n001-uniform-condensate-review.md` and its adjacent JSON
evidence manifest. The audit is scoped to the stored q1a seed, parameter,
box, discretisation, and solver setup.

**Consequence:** this is not a nonexistence result for BCC condensates and does
not modify B1-RH-ENUM or the already retired B3-BCC-STRUCT card. It rules out
using these stored fields as BCC evidence. The observed three-grid branch is
recorded separately as a homogeneous-condensate experimental result. Before a
new BCC sweep, evaluate q0/BCC-star projected curvature about the homogeneous
branch.

<a id="audit-2026-07-19-a3-shared-bundle-integrity"></a>
### AUDIT-2026-07-19-A3-SHARED-BUNDLE-INTEGRITY -- stale historical A3 shared bundle manifest

**Failure mode:** `claims/A3-UV-SUPERRENORMALISABILITY/bundle/A3-Renormalisation-Foundation-260623/MANIFEST.json` listed the v1.0 consolidation `.tex.txt` and `.pdf`, but those files were absent from the bundle, and the checked-out `README.md` hash did not match the listed hash. The claimed historical content digest therefore could not be reproduced from that directory.

**Evidence:** direct enumeration and SHA-256 audit on 2026-07-19. The mathematical entry note v1.1 and both entry scripts remained present; this is a packaging-integrity failure, not a theorem refutation.

**Consequence:** the 260623 directory is retained only as defective historical provenance and is not used as current A3 perturbative publication support. A clean claim-level replacement, `claims/A3-PERTURBATIVE-CONTINUUM-CORRELATORS/bundle/A3-Perturbative-Continuum-T6-260719`, was rebuilt from the already operator-approved v1.1 consolidation. Both entry scripts pass (6/6 and 8/8), all 11 listed file hashes match, and bundle digest `6783ee6637936675af9f0b16ede28fa5da91c1daf5c075e43f510625c59b9c0c` recomputes exactly.

<a id="audit-2026-07-19-a4-verifier-tier-drift"></a>
### AUDIT-2026-07-19-A4-VERIFIER-TIER-DRIFT -- stale pre-promotion boundary in the A4 verifier artifact

**Failure mode:** after the A4 scalar constructive theorem was enacted at scoped T6 on 2026-07-18, `a4_scalar_constructive_measure_verify.py` v1.0.0 continued to write the earlier boundary sentence that T5 internal reproduction was complete and independent operator execution was still required before T6 review. The computed audits and 31/31 verdict were correct, but the machine-readable epistemic status contradicted the enacted claim card.

**Evidence:** direct source and result-JSON inspection during the 2026-07-19 publication preflight. The stale sentence was isolated to the `promotion_boundary` field; no formula, input, source-hash test, assertion, or verdict logic depended on it.

**Consequence:** verifier v1.1.0 changes only that boundary field to record the already enacted T6 theorem and retain the T7/excluded-scope prohibition. A fresh primary 17/17 plus non-importing independent 14/14 run passes 31/31 at `runs/2026-07-19-referee-preflight/result.json`, SHA-256 `bc953c71f13f464da2e7d3cf7355204a41f288ad8c500947abf04baa45aa1667`. The old artifacts remain historical evidence; no theorem or tier change results from this correction.

<a id="audit-2026-07-19-a4-q0-zero-shell-boundary"></a>
### AUDIT-2026-07-19-A4-Q0-ZERO-SHELL-BOUNDARY -- zero-mode endpoint omitted from the v2.0 shell notation

**Failure mode:** the operator-confirmed integrated v2.0 referee package declared
`q0>=0` but wrote `m0=ceil(sqrt(2)q0/alpha)` and then applied the nonzero
max-norm shell count `24m^2+2` and inverse-power tail from `m=m0`.  At `q0=0`
this gives `m0=0`; the shell formula is valid only for `m>=1`, and the displayed
`m^-2`/`m^-4` sum is undefined at zero.  The executable primary implementation
already guarded its tail with `max(1,shell_threshold)`, so this was a proof-note
endpoint defect rather than a failed numerical result or false theorem.

**Evidence:** line-by-line adversarial review after the exact v2.0 approval on
2026-07-19, followed by direct comparison with
`weighted_trace_tail_upper`, which already required a start shell of at least
one.  The defect is load-bearing for the declared endpoint and therefore blocks
publication of v2.0 even though the positive production anchors have `q0>0`.

**Consequence:** v2.1 treats the zero Fourier mode in the finite inner set and
defines `m0=max(1,ceil(sqrt(2)q0/alpha))`.  Primary audit v1.1.0 and the
non-importing audit v1.1.0 add separate `q0=0`, `m0=1` assertions; verifier
v1.2.0 passes 18/18 + 15/15 = 33/33 at
`runs/2026-07-19-referee-preflight-v2.1/result.json`, SHA-256
`85da0df0d2b96dbfc98f2ea8a0787bf1bd711228505c671c06cb9d3e036836d8`.
The T6 theorem and scope are unchanged.  v2.0 remains approved review
provenance but is superseded as the publication entry.  Jusang Lee confirmed
exact v2.1 on 2026-07-19; the PUBLISHED bundle
`A4-Scalar-Constructive-T6-260719` passes standalone 33/33, all 18 file hashes,
and digest `b1a215465956443ce22a7dcf42caaa9a3dfb61305759f4be4f55eab630cd3162`.

<a id="audit-2026-07-19-a5-dependency-pin-drift"></a>
### AUDIT-2026-07-19-A5-DEPENDENCY-PIN-DRIFT -- stale A3/A4 pins in the A5 v1.0 synthesis manifest

**Failure mode:** A5 manifest schema 1.0 correctly froze the 2026-07-18 review surface, but the subsequent replacement A3 perturbative T6 bundle and A4 v2.0 publication preflight changed the current A3/A4 status and manifest hashes. The v1.0 verifier also expected only four PUBLISHED support bundles and an OPEN operator gate. Running it against the updated repository would therefore report source drift even though the branch proposition was unchanged.

**Evidence:** direct SHA-256 comparison of all six component cards, four component manifests, evidence artifacts, and support manifests on 2026-07-19. The A3 replacement added a fifth valid PUBLISHED support bundle; the A4 package remained an explicit pending dependency.

**Consequence:** schema 1.1 refreshed the interim pins, attested the fifth A3 bundle, and failed closed on the then-pending A4 publication prerequisite. After corrected A4 v2.1 became PUBLISHED, schema 1.2 refreshed the A4 card/manifest/preflight pins, attested all six support bundles, and recorded the exact A5 v1.2 batch authorization. The primary and non-importing routes remain 16/16 each and the integrated verifier remains 32/32. The final rebuilt A5 T5 PUBLISHED bundle has 155 hashed files and digest `5cf4397c38fb316ec108447404531e649e628d6fcc62d67e613d060b70b24ea5`. This closes the dependency-record defect without changing the branch proposition or promoting it to T6.

<a id="audit-2026-07-19-a5-bundle-note-pdf-completeness"></a>
### AUDIT-2026-07-19-A5-BUNDLE-NOTE-PDF-COMPLETENESS -- paired A4 PDF omitted from initial A5 bundle

**Failure mode:** The first A5 capstone bundle copied the confirmed A4 v2.1
source at its original claim path because the A5 audit reads that source hash,
but copied the A4 PDF only inside the nested A4 support-bundle tree.  The A5
entry scripts and all 154 initial file hashes passed, yet the repository-wide
note-PDF check correctly reported that the original-path A4 source inside the
A5 bundle had no adjacent PDF.

**Evidence:** `verification/scripts/verify_note_pdfs.py` reported exactly one
missing pair inside the initial A5 bundle.  The bundle was still uncommitted and
was not retained as tier history.

**Consequence:** The A5 bundle was rebuilt once with the original-path A4 v2.1
PDF included.  It passes standalone 16/16 + 16/16 = 32/32, all 155 final file
hashes, content digest
`5cf4397c38fb316ec108447404531e649e628d6fcc62d67e613d060b70b24ea5`,
and `NOTE-PDF: PASS (190 current notes, all have fresh PDFs)`.  No claim tier,
proof statement, or approved A5 entry source changed.
