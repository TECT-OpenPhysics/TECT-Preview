# Negative-Result Registry

Failures are trust assets. Entries are never deleted. Format:
(branch/claim | failure mode | evidence | consequence). Tags: `R-` retracted
result, `F-` fired falsification gate, `NG-` no-go finding.

| Tag | Branch / claim | Failure mode | Evidence | Consequence |
|---|---|---|---|---|
| NG-2026-legacy-convention | old $r=K(0)$ no-condensation convention | wrong variable convention | legacy: Math426 cascade | replaced by $r_{\rm braz}=K(q_0)=\mu^2$; A1-KERNEL-CONV registers the corrected convention |
| NG-2026-legacy-ordered-vacuum | fixed ordered BCC vacuum as ground state | fluctuation restoration | legacy: Reading-H selection chain | Reading-H selected instead (B1-RH-ENUM); ordered-vacuum reading retired |
| R-2026-legacy-newtonG-label | Newton $G$ "independently predicted / T7" label | independent prediction missing ($a_{\rm BCC}$ fixed by $G_{\rm obs}$) | legacy: governance audit | downgraded to RELATION DERIVED / VALUE MATCHED; managed as T6/T7-SPLIT (C5-NEWTON-G) |
| R-2026-legacy-rh-overclaim | estimator-only Reading-H claim above T5 | controlled error bound missing | legacy: estimator chain audits | remains T5 CLOSED@ESTIMATOR-GRADE until ESTIMATOR-UPGRADE and STEP-5B close (B1-RH-ENUM) |
| F-2026-04-30-flat-cartan | Pillar-4 sub-task-2 "closure completed" (flat-Cartan forcing, Mechanism A) | falsified by $c_2(E)=-40\neq 0$ on canonical $\mathbb{CP}^2$ | legacy: Math174, Math245 rollback | sub-task 2 back to T3 (D2-GAUGE-FORCING); Mechanism A refuted; Mechanism B insufficient alone |
| NG-2026-legacy-classical-hbar | classical-field-theoretic derivation of $\hbar$ (8 routes) | each route fails (4 Math59 + 3 Math59-v3 + 1 R5) | legacy: Math59, Math59-v3, R5 record | $\hbar$ stays an external phenomenological parameter; phase-transition programme registered at T2 (E2-HBAR-ORIGIN) |
| NG-2026-06-07-scscope-endpoint-joint | SC-SCOPE all-orders endpoint (B5/B1) | the individually-positive third-order channels (sunset x1.13, quartic-difference x1.29, tadpole 0) JOINTLY over-consume the endpoint layer margin by x1.32 -> joint endpoint x0.757 < 1 | scscope_joint_endpoint.py 5/5; scscope-endpoint-joint-assessment v1.0 | SC-SCOPE stays OPEN at the endpoint; B1 T6 selection UNAFFECTED (SC-SCOPE is a named hypothesis); path = joint incompatible-pairing argument or sharper per-transfer bounds. UPDATE 2026-06-07 (scscope_joint_pairing.py 4/4, scscope-joint-pairing v1.0): the joint incompatible-pairing was carried out in its MOST FAVOURABLE form and recovers only x0.757 -> x0.905 < 1; the sunset ALONE is x1.076 (near-saturating). Per-transfer/pairing refinements EXHAUSTED. Remaining routes: a sharper STEP-5B endpoint floor (rho >~ 3.9 at I=2e-3) OR accept second-cumulant scope at the I=2e-3 endpoint (all-orders lift is FEASIBLE for I<=1e-3, floor x8.8). B1 T6 unaffected |

| NG-2026-06-09-res5-bare-susceptibility-ratio | RES-5/GAP-2 closure via the BARE susceptibility-ratio bound (B1) | the bare Gaussian-sea ratio $\chi^{(3)}/\chi^{(2)}\sim 4\int G^3/\int G^2 = 9.05 > 1/(2a_0)=5.23$, so $r_2(\text{bare})=0.866>1/2$; bare ratios $\int G^{n+1}/\int G^n\to1/\hat r\approx2.5$ (strong-coupling, growing) | res5_susceptibility_ratio.py 4/4; res5-susceptibility-ratio-bareroute v1.0 | the elementary bare-ratio route is ELIMINATED; B1 T6 on {H-LAYER} UNAFFECTED (no claim withdrawn); the genuine residual is the COMMON-MODE-SUBTRACTED ratio $\chi_{\rm pd}^{(k+1)}/\chi_{\rm pd}^{(k)}$ (SC-SCOPE's ~4% n=3 is the subtracted, not bare, value) -- a strong-coupling research frontier. ANNOTATED 2026-06-09 (res5-oneloop-loop-disentangling v1.0): the bare chi^(k)~int G^k are the condensate-expansion coefficients of the EXACT one-loop log-det (converges, peak node 0.574<1), NOT the loop expansion -- so the bare-ratio 9.05 does NOT bear on RES-5; RES-5 is the LOOP expansion (2-loop+, SC-SCOPE=two-loop). Framing conflation self-caught; residual corrected to the higher-loop difference. |
| R-2026-06-09-res5-ca0-doublecount | RES-5 a0-skeleton estimate $c\,a_0\sim0.002$ (B1) | the estimate took $\|\Sigma_2^{\rm pd}\|/\Delta F_{\rm margin}\sim0.04$ (the FREE-ENERGY sunset ratio) and multiplied by $\|\delta G_*^{\rm pd}\|=O(a_0)$ -- double-counting $a_0$, since $\Delta\Gamma_2^{\rm pd}=\|\Sigma_2^{\rm pd}\|\,\|\delta G_*^{\rm pd}\|$ already IS the free-energy ratio | res5_sunset_norm_map.py 4/4; res5-sunset-selfenergy-norm-certificate v1.1 | the $c\,a_0\sim0.002$ figure is RETRACTED; the certificate quantity is the free-energy ratio $|\Delta\Gamma_2^{\rm pd}|/\Delta F_{\rm margin}$ directly, whose LEADING (sunset) value IS the SC-SCOPE certified joint $\times1.040\to\times1.13$. B1 T6 on {H-LAYER} UNAFFECTED (no claim withdrawn). |
| AUDIT-2026-06-09-res5-survival-overclaim | RES-5 "survives at STRONG EVIDENCE, thin" (B1; certificate v1.0) | the higher-skeleton tail bound $C_{\rm higher}\le\text{leading}/(1-0.49)\approx2\times\text{leading}$ is SAME-ORDER (screened-finite), NOT sub-dominant; against the thin SC-SCOPE joint $\times1.040$ the slack is only $1-1/1.040\approx3.85\%$ ($C_{\rm higher}$ must be $<0.040\,C_{\rm leading}$), which a same-order tail does not respect | operator adversarial review 2026-06-09; res5_sunset_norm_map.py 4/4 (slack assert); res5-sunset-selfenergy-norm-certificate v1.1 | v1.0's RES-5-survival / STRONG-EVIDENCE-thin verdict is RETRACTED; RES-5/GAP-2 returns to OPEN. The self-energy/free-energy correction (R-2026-06-09-res5-ca0-doublecount) is RETAINED. B1 T6 on {H-LAYER} UNAFFECTED. Next: res5-tail-budget-closure (prove the SC-SCOPE-joint $\to\Delta\Gamma_2^{\rm pd}$ identity + a tail budget $C_{\rm higher}<0.04\,C_{\rm leading}$). ANNOTATED 2026-06-09 (res5-tail-budget-closure v1.0, operator-ACCEPTED): RES-5/GAP-2 OPEN $\to$ ENDPOINT-LOCALISED -- the screened tail $C_{\rm higher}/\Delta F_{\rm margin}\approx C_G a_0(I)$, $a_0\propto I$, fits the third-cumulant slack with $\ge27\times$ margin for $I\le10^{-3}$ (tail/slack $0.012,0.036$; STRONG EVIDENCE CLOSED off endpoint) and is marginal/estimate-undetermined ONLY at the $I=2\times10^{-3}$ endpoint (tail/slack $1.22$). RES-5 is thus a single endpoint boundary problem, not a bulk obstruction (34x localisation). B1 unaffected (T6 on {H-LAYER}). Next: res5-endpoint-2pi-bound (prove $C_{\rm higher}(2\times10^{-3})<0.0385\,\Delta F_{\rm margin}$, i.e. an ~18% tail tightening or a slightly thicker certified slack). FURTHER ANNOTATED 2026-06-09 (res5-endpoint-2pi-bound v1.0, 5/5): ENDPOINT-LOCALISED $\to$ STRONG EVIDENCE -- the endpoint tail $C_G a_0=0.047$ is BRACKETED, slack$_{\rm proved}$(0.0385) $<$ tail $<$ slack$_{\rm verified}$(0.0758); it closes at the realized (verified) floor $K_{\rm floor}\le0.52T'$ ($\rho_{\rm lat}=12.6$) with a 38% margin, or at the proved slack whenever $\chi_{\rm proj}<0.82$. The marginalit-y is an ARTEFACT of the over-conservative floor. RES-5's residual UNIFIES with SC-SCOPE's floor sharpening (one inequality $K_{\rm floor}\le0.52T'$ discharges BOTH). B1 unchanged (T6 on {H-LAYER}); rigorous T6 pending the proved $0.52T'$ floor or $\chi_{\rm proj}\le0.82$. CORRECTED 2026-06-10 (status reconciliation): SC-SCOPE is LIFTED@THIN-CERTIFIED via the QUARTIC route (scscope-quartic-normalisation-certificate), NOT the floor route (whose standalone lift was retracted); canonical B1={H-LAYER}. So the RES-5 endpoint floor-$\kappa$ tightening unifies with B1's DR-2 (unrestricted-class additive-energy) residual, NOT with SC-SCOPE. Route-A findings (archived): PROVED refinement $K\le T'(1-\|a\|_4^4/I^2)$ (Cauchy-Schwarz + $t=0$); EXACT complete single-shell scan worst $\kappa=K/T'=0.75$ (corrects the incomplete-sample 0.52); worst-case $\kappa<1$ over the dense admissible class is additive-energy/circle-incidence-adjacent (= DR-2). |
| F-2026-06-10-res5-projection-route | RES-5 endpoint closure via the pattern projection $\chi_{\rm proj}\le0.82$ (B1) | the screened response at the BCC $\{110\}$ modulation transfers gives $\chi_{\rm proj}=f_{\rm avg}/C_G=0.613/0.492=1.25>1$ -- the bubble $\chi_0(k)$ is forward-peaked, so screening is MAXIMAL at $k=0$ ($C_G=0.49$) and WEAKER at $\{110\}$ ($f=0.57$--$0.73$); the modulation is not in the maximally-screened channel | res5_projection_factor.py 5/5; res5-projection-factor-bound v1.0 | the projection closure lever is ELIMINATED; the operator-norm tail $C_G a_0=0.047$ is corrected UPWARD to $f_{\rm avg}a_0=0.059$ (the a0-skeleton $C_G$ estimate was forward-channel optimistic); the endpoint closes ONLY at the verified floor ($0.059<0.0758$, 23% margin), NOT conservative, and rests SOLELY on the DR-2 floor route. Off-endpoint ($I\le10^{-3}$) closure UNAFFECTED. B1 T6 on {H-LAYER} UNAFFECTED. |

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
