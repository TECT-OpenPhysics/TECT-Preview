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
