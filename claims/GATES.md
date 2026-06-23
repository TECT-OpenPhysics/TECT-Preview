# Gate & Hypothesis Registry

Gates are promotion conditions; hypotheses are named assumptions that T6 claims
may rest on. Every `open_gates` / `hypotheses` entry in any `status.json` must
exist here. Last updated: 2026-06-05.

## Umbrella gates (GAPs)

| Gate | Summary |
|---|---|
| [**GAP-1**](#gap-1) | DISCHARGED@T7-lattice-Reading-H … |
| [**GAP-2**](#gap-2) | CLOSED@T7-domain … |
| [**GAP-3**](#gap-3) | OPEN … |
| [**GAP-4**](#gap-4) | OPEN |

<a id="gap-1"></a>
### **GAP-1**

**Statement:** Vacuum uniqueness: $\mathcal R_H=\operatorname{arg\,min}_{\mathcal A_{\rm adm}}F_{\rm TECT}$ over the full admissible class

**Status:** DISCHARGED@T7-lattice-Reading-H (operator-enacted 2026-06-10): vacuum uniqueness CLOSED over the physical class C_phys (crystallographic lattice, packing-bounded, coherence-resolved, antipodal; operating endpoint I=2e-3, [x0.5,x2]) by the T7 proposition (t7-proposition-assembly v1.1: F[Q]>F[G_*] for all C_phys; off-shell domination non-circular rho_off^ext=0.572<1 + on-shell T'<=13 + certified thresholds). Arbitrary-Q (non-lattice) remains OPEN as a legacy fallback (DR-2).

<a id="gap-2"></a>
### **GAP-2**

**Statement:** Error control: $\lvert\Delta F_{\rm true}-\Delta F_{\rm est}\rvert\le\varepsilon_{\rm ctrl}$ with $\Delta F_{\rm est}-\varepsilon_{\rm ctrl}>0$

**Status:** CLOSED@T7-domain (2026-06-10): ESTIMATOR-UPGRADE controlled-error (2026-06-07) + the SC-SCOPE thresholds now theorem-grade (blocker-b-hardening v1.1: R_max interval-enclosed<=0.391<0.634, Ghat4 convention DERIVED from the (2pi)^3 measure, anchoring monotone). The selection error is controlled within the T7 domain.

<a id="gap-3"></a>
### **GAP-3**

**Statement:** Constants firewall complete: every constant labelled derived/matched/inserted/predicted with ledger row

**Status:** OPEN (ledger seeded)

<a id="gap-4"></a>
### **GAP-4**

**Statement:** Falsifiability: at least one observable deviation predicted before fitting

**Status:** OPEN


## Named gates

| Gate | Summary |
|---|---|
| [**STEP-5B**](#step-5b) | CLOSED-CONDITIONAL … |
| [**G3PB-III**](#g3pb-iii) | CLOSED@CROSS-CHECK |
| [**G1PP-3B-HEX**](#g1pp-3b-hex) | CLOSED within H-layer scope … |
| [**ESTIMATOR-UPGRADE**](#estimator-upgrade) | CLOSED@CONTROLLED-ERROR … |
| [**ROBUSTNESS-MU2**](#robustness-mu2) | CLOSED@[x0.5,x2]-2ND-CUMULANT |
| [**H-SUPPRESSION-DISCHARGE**](#h-suppression-discharge) | OPEN |
| [**G-A0-DUI**](#g-a0-dui) | CLOSED |
| [**M-ENDPOINT**](#m-endpoint) | RESOLVED |
| [**GHAT3-Q0**](#ghat3-q0) | OPEN … |
| [**GHAT4-PERTRANSFER**](#ghat4-pertransfer) | OPEN |
| [**R-U6-1**](#r-u6-1) | DISCHARGED 2026-06-12 … |
| [**H-ENDPOINT-THINNESS-ACCEPTED**](#h-endpoint-thinness-accepted) | REMOVED 2026-06-12 … |
| [**H-NONLATTICE-REMAINDER-EXCLUDED**](#h-nonlattice-remainder-excluded) | RECLASSIFIED 2026-06-13 … |
| [**R-U6-2**](#r-u6-2) | DISCHARGED 2026-06-12 … |
| [**DR2-SHARE**](#dr2-share) | MOOT for the lattice mainline … |
| [**CP-UNITARITY**](#cp-unitarity) | OPEN |
| [**SCHEME-2LOOP**](#scheme-2loop) | OPEN … |
| [**PRED-G-FREEZE**](#pred-g-freeze) | OPEN |

<a id="step-5b"></a>
### **STEP-5B**

**Statement:** Beyond-layer class-wide bound (admissible-class exhaustiveness step; pattern-generic Gershgorin attack designated). **The gateway for any whole-Reading-H T6 discussion.** Progress 2026-06-05 (claim B5-BEYOND-LAYER-BOUND, **T4**): Lemmas A/B/C'/D rigorous; **closed-region theorem DERIVED** — holds for all single-shell patterns with $n \le n_{\max}(I)$ (62/31/16/6/3 at $I=10^{-4}..2{\times}10^{-3}$). Residual after AddD: **verdict-#14 confirmation only — the adoption record is WRITTEN (operator-directed per verdict #13), the cross-reading lemma is certified, and the assembled closure holds at x55.6/x8.8/x2.1; gate-row flip + B5 tier action await the confirmation**. Previously: **operator sign-off on the now LEMMA-BACKED H-ADM-COH (indistinguishability: sub-resolution restructuring shifts F by $\le c_{\rm ind}I^2$ = margin/x33+ everywhere; de-thinned closure margins x55.6/x8.8/x2.1)** — DR-2 off the critical path. Previously: **operator sign-off on H-ADM-COH (derived: $n_{\rm adm}\approx35$, margins x32.4/x5.1/x1.2 — CLOSURE-READY) OR DR-2** — H-ADM now DERIVED from the dressed propagator's coherence resolution (T3 sketch, class-amendment proposal). Previously: **{H-ADM} + DR-2 only — H-KBAL structurally LIFTED** (unconditional-amplitude theorem $64\sqrt7\,I^2\sqrt n\log^2$; kappa-balance now affects constants only; ledger threshold $1.59{\times}10^5$ keeps the sharp-constant balanced form). Previously: **conditionality {H-KBAL, H-ADM} with the VERIFIED threshold $n_{\rm adm}\lesssim1.59{\times}10^5$** (sqrt-n route official; 20/9 incidence route provisional at $2.2{\times}10^{10}$, constant unpinned; 7.9e16 withdrawn; DR-2 dichotomy = designated route to sharp $O(N^2)$). Previously: **conditionality only — named {H-KBAL, H-ADM}** ($c_R=4\sqrt{14}$ THEOREM-grade by operator derivation; incidence route $O(N^{28/13})$ pushes the reach to $7.9{\times}10^{16}$ modes at the anchor — ANY admissibility cutoff below that closes the gate; sharp $O(n^2)$ conjecture pre-registered with measured exponents 2.04--2.08). Previously: **extreme-$n$ rich-carrier corner only** ($n\gtrsim10^6$ at anchor; $\kappa$-balanced $\sqrt n$ rectangle corollary closes everything below: $R=O(n^{5/2})$ unconditional via triple count; coaxial lemma $H^*$-explicit after the verdict-#8 audit) + first-principles $c_R$. Previously: **the carrier-richness bound $p_0(P)$** (antipodal-carrier partition exact; $\nu^*=\mu_C$ one-parameter identity; COAXIAL CLASS CLOSED $K\le30$; single-circle universal $K=14$ sharp; H-GEN(2) falsified honestly). Previously: **G1'''-AE as the discrete sphere $L^4$-extension problem** (Stein--Tomas $q=4$, $d=3$; Parseval: $\sum w^2=\lambda'^2(\langle F^4\rangle-4I^2)$); corner narrowed to high-$n$ multi-circle non-transversal patterns (UNIVERSAL single-circle theorem $K=14$ sharp removes ALL single-circle patterns, any amplitudes; Nambu objection DISCHARGED — real scalar, $W$ = multiplication operator). Previously: **G1'''-AE only** — the class-wide weighted sphere additive-energy bound $\sum w_t^2 \le K(\lambda'I)^2$ on the extreme corner {$n>N_{\max}(I)$, non-transversal, non-ring} (G-DEC demoted to sub-route). **G1''-M4: CLOSED BY STRUCTURE** ($P^2$-representation theorem, v1.7: $W=\lambda'(P^2-2I)$, $D+W\ge D_0>0$ unconditional, spectral floor $a_0=2\lambda'I/\hat r$ n-free — Gershgorin obsolete; enlarged region $N_{\max}(I)=12133/3017/746/115/27$ vs $62/31/16/6/3$). **G2: CLOSED at second-cumulant bookkeeping level** (sextic $\varepsilon_4\le0.16$; $\sigma$-channel exact; two-shell floor $\times1.70$). Transversal $n$-free + ring exact + glue $\ell^2$ all stand. **G1'b ring family: CLOSED for the canonical equal-amplitude two-ring family** — exact $c_{\rm ring}(n)=14-18/n$ (even) / $8-6/n$ (odd) $<14$, five-orbit proof, verified $10^{-10}$ at $n=7..64$.

**Status:** **CLOSED-CONDITIONAL** (OPERATOR VERDICT #14, 2026-06-05: "H-ADM-COH is accepted as the admissible-competitor definition within the matched second-cumulant B5 scope. AddD v1.0 passes as the closure record for STEP-5B on the amended admissible class. The STEP-5B gate row is flipped to CLOSED-CONDITIONAL with margins 55.6x/8.8x/2.1x. B5 is promoted from T4+ to T5-candidate. Unrestricted-class closure remains open via DR-2, and cross-reading analytic pin plus endpoint hardening remain polish items.")

**Source:** `archive/legacy/notes/Math442/TECT-Math442-F10-Closure-Math437v1p2-CERTIFIED-260605-v1.0.tex.txt`

<a id="g3pb-iii"></a>
### **G3PB-III**

**Statement:** G3′-b(iii): the {200}/{110} amplitude-ratio cross-check of the two-shell Reading-H selection

**Status:** CLOSED@CROSS-CHECK

**Source:** g3pb3-ratio-closure v1.0 (g3pb3_ratio_extraction.py 6/6, operator-directed 2026-06-08): the physical {200} response A2*(A1)=argmin_{A2,M} dF_anchored at r=0.219 is on the negative (sextic-driven) branch with |A2*|<=0.08, |rho|<=0.57, INSIDE the continuum-certified box |A1|,|A2|<=0.16; dF_anchored>0 along the physical-ratio trajectory. Combined with the whole-box exact-Wick continuum no-condensate (twoshell-anchored-continuum v1.0), Reading-H wins at the physical ratio. Scope {110}+{200} truncation (AddF N=64 raw not migrated); higher shells = separate G3'-b(i)/(ii). B1 T6 tier unchanged.

<a id="g1pp-3b-hex"></a>
### **G1PP-3B-HEX**

**Statement:** G1″-3b-HEX exact-Wick bracket (HEX competitor margin)

**Status:** CLOSED within H-layer scope — Math437 v1.2 F10-REPAIR RESOLVED, verified by dual audit

**Source:** `archive/legacy/notes/` Math437 v1.2 / Math440 / Math441 / Math442

<a id="estimator-upgrade"></a>
### **ESTIMATOR-UPGRADE**

**Statement:** GAP-2 instance for Reading-H: estimator-grade $\Delta F$ → controlled error bound

**Status:** CLOSED@CONTROLLED-ERROR (operator-authorized 2026-06-07)

**Source:** `archive/legacy/notes/` Math427–Math436 enumerated-reading chain (migrated batch 2).

**ADVANCE 2026-06-07** (estimator_upgrade_enumerated.py 7/7, estimator-upgrade-enumerated v1.0): single-shell readings (LAM/HEX/FCC/BCC) at mu^2=0.005 upgraded to CONTROLLED-ERROR -- A=0 is a strict minimum, curvature kappa_R = dF_R''(0) >= 0.85 (binding LAM 0.851), M-quadrature envelope < 0.1% of kappa (N_PT 6000 vs 20000), no condensate at either resolution. REMAINING: two-shell ensemble + dI/grid knobs (same method); gate stays OPEN pending those + operator sign-off.

**OPERATOR REVIEW 2026-06-07** (reviews/2026-06-07-estimator-upgrade-and-scscope-acceptance-review.md): the single-shell M-quadrature SUBGATE is marked CONTROLLED-ERROR ADVANCED; the enumerated margins are controlled w.r.t. the dominant M-quadrature knob ONLY (NOT a full estimator closure). Remaining knobs {two-shell ensemble, dI quadrature, amplitude grid} keep the gate OPEN; a no-condensate interval/Lipschitz continuum bound is a registered publication-grade follow-up (T-010).

**KNOB CLOSURE 2026-06-07** (estimator_upgrade_knobs.py 13/13, estimator-upgrade-knobs v1.0): the dI-quadrature + amplitude-grid knobs are now also controlled (kappa moves <0.1% under dI refinement (6000,50)->(12000,100); no-condensate grid-monotone at NG=121/241/481), the no-condensate verdict is upgraded to a curvature-chord CONTINUUM bound (min(v_i,v_{i+1})-(1/8)M_i delta^2 > 0 on every A>0 interval), and the two-shell {110}+{200} (0,0) Hessian certified positive-definite (kappa_12=0 by orthogonality; both eigenvalues>0).

**TWO-SHELL GLOBAL ADVANCE 2026-06-07** (twoshell_continuum_bound.py 10/10, twoshell-continuum-bound v1.0): the two-shell GLOBAL no-condensate is established as a DIAGONAL-continuum bound AT THE B1 POINT r=0.219 (M-minimised surface min +3.9e-5>0; 2D curvature-chord continuum lower bound +1.2e-4>0; PD (0,0) Hessian), via a diagonal evaluator validated vs Math432 to 1.6e-7. TWO CORRECTIONS to the knob-closure note: (1) the cited Math432 evidence runs at a DIFFERENT operating point r=0.005 (not the B1 point r=0.219); (2) the soft (0,0) eigenvalue is kappa_{200}=3.86 NOT kappa_BCC({110})=5.116 ({200} is the SOFTER direction; PD still holds).

**EXACT-WICK BRACKET CLOSED 2026-06-07** (twoshell_anchored_bracket.py 7/7, twoshell-anchored-bracket v1.0): with the EXACT slogdet engine (Math432 neuter-imported, validated to 5e-8), the anchored two-shell dF = diagonal + bracket at r=0.219 has min over (A1,A2)!=(0,0) = +6.7e-4>0; the bracket is O(A^4) near origin (|bracket|(0.005)=3.9e-8) so the anchored (0,0) Hessian = diagonal (kappa_{110}=5.16, kappa_{200}=3.86, PD). The off-diagonal bracket does NOT overturn the no-condensate. BULK CONTINUUM +

**CLOSURE 2026-06-07** (twoshell_anchored_continuum.py 7/7, twoshell-anchored-continuum v1.0): the exact anchored two-shell surface at r=0.219 has a 2D curvature-chord continuum lower bound +1.34e-3>0 away from the origin cell (node-free no-condensate) and an anchored (0,0) PD Hessian covering the origin cell -- the exact-Wick no-condensate is CONTINUUM on the whole domain. CLOSED@CONTROLLED-ERROR (operator-authorized 'close cleanly' 2026-06-07; consolidation: estimator-upgrade-closure-consolidation v1.0). Single-shell (M/dI/amplitude knobs + curvature-chord continuum) and two-shell (exact-Wick anchored continuum) margins are controlled-error/strong-evidence; a T7 interval-arithmetic upgrade is optional. B1 T6 tier unchanged (margins gate, not the SIGN).

<a id="robustness-mu2"></a>
### **ROBUSTNESS-MU2**

**Statement:** Open-neighbourhood robustness of the selection result in $\mu^2$ around $\mu^2=0.005$

**Status:** CLOSED@[x0.5,x2]-2ND-CUMULANT

**Source:** governance draft §15

**ADVANCE 2026-06-06** (robustness-mu2-offanchor v1.0, 9/9): A=0-uniqueness component ROBUST on mu^2 in [0.001,0.05] (x0.2..x10; sign-decomp lemmas mu^2-independent; m*>m_w x5.74 / M_R>M_c x4.08 across x4; m*-m_w = 3uM_R+15v(M_R^2-M_c^2) mu^2-cancels). OPEN, with numerically-supported off-anchor advance on mu^2 in [x0.5,x2] (operator review 2026-06-06, FINAL): the STEP-5B beyond-layer margin recomputed off-anchor stays >1 across mu^2 in [x0.5,x2] (endpoint x2.55..x2.64; anchor reproduces AddE x59.4/x2.6); A=0 uniqueness robust on [x0.2,x10]; Prop-A floor preserved (M_R/M_c>4.1). The gate is NOT closed: the exact layer margin m(mu^2) is bounded positive but NOT recomputed (does not meet the closure bar), the evidence is second-cumulant scope only, and the mu^2-monotonicity is a sampled-sweep observation. robustness-mu2-step5b-remargin v1.3.

**ADVANCE 2026-06-07** (robustness-mu2-margin-recompute v1.0, 11/11): the EXACT layer margin m(mu^2) = PB(M_+(mu^2)) - DIP_BAND(mu^2) recomputed across [x0.5,x2] (closed form reproduces 0.00432 at anchor); min m(mu^2) = 0.004082 = 0.945 m_anchor (>= 0.4 m_anchor, drift 16.7% over x4); STEP-5B ratio with the RECOMPUTED margin worst x2.41 > 1; J_eff envelope converged (nk 500 vs 1100 < 0.1%). The closure bar is MET; CLOSE@[x0.5,x2]-2ND-CUMULANT RECOMMENDED pending operator sign-off. v1.1 reinforced (robustness-mu2-margin-recompute v1.1, 9/9; operator review 2026-06-07): derivative-sign monotonicity certificate (dm/dmu2>0 => min at mu2=0.0025), full-grid J_eff envelope (<0.01%), Prop-A branch invariance; MARGIN now derived from sectorb_common (de-hardcoded).

**FLIP 2026-06-07**: CLOSED@[x0.5,x2]-2ND-CUMULANT by operator authorization (reviews/2026-06-07-robustness-close-authorization-review.md).

<a id="h-suppression-discharge"></a>
### **H-SUPPRESSION-DISCHARGE**

**Statement:** Discharge of the (H-suppression) hypothesis (full TECT-Hessian + Wetterich projection + negative-eigenvalue derivation)

**Status:** OPEN

**Source:** legacy: Pillar-2 record

<a id="g-a0-dui"></a>
### **G-A0-DUI**

**Statement:** Differentiation under the integral for $M(m)$.

**CLOSED 2026-06-06**: explicit dominated-convergence argument with dominating function $k^2/[m_0+C(k^2-q_0^2)^2]^2$ (integrable, $k^{-6}$ tail; pointwise domination max ratio $1.000$); machine-confirmed ha0_sign_decomposition.py v1.1.0 23/23 ($M'=-\int k^2/D^2$ vs FD $<0.6\%$).

**Status:** CLOSED

**Source:** note ga0-dui-closure-260606-v1.0

<a id="m-endpoint"></a>
### **M-ENDPOINT**

**Statement:** The convexity-honest endpoint dressing variance $M(0.33675)$ (the dressed mass at $I=2\times10^{-3}$): the named missing constant for the sunset endpoint. Until machine-evaluated, the $\times1.34$ endpoint ratio is a linear-response ESTIMATE (M convex $\Rightarrow$ not a proven floor), i.e. candidate removal, not removed failure.

**Status:** RESOLVED

**Source:** sunset-endpoint-refinement v1.0.

**ADVANCE 2026-06-07** (scscope-mendpoint-evaluation v1.0, 11/11): M-ENDPOINT = M(0.33675) = 0.10495 evaluated by DIRECT quadrature (two quadratures agree 0.20%), bypassing the factor-2 linearisation; the directly-dressed sunset endpoint ratio is x1.13 > 1 (frozen-coupling x0.97 = U4 reproduced). Value RESOLVED; recommend RESOLVED pending operator sign-off. v1.1 reinforced (scscope-mendpoint-evaluation v1.1, 12/12; operator review 2026-06-07): convergence certificate (two quadratures agree 0.61%, analytic tail bound 8.4e-4; EXECUTED value cross-checked ~1%), single-J0 conservatism table J(rhat(I))<=J0, wording restricted to the sunset axis.

<a id="ghat3-q0"></a>
### **GHAT3-Q0**

**Statement:** The cubic vertex form factor $\widehat{G^3}(q_0)$ at the on-shell transfer (optional): quantifies the kernel-axis yield the sunset-endpoint note assessed as low by phase-space argument only.

**Status:** OPEN (optional)

**Source:** sunset-endpoint-refinement v1.0

<a id="ghat4-pertransfer"></a>
### **GHAT4-PERTRANSFER**

**Statement:** The per-transfer quartic-difference form factor $\widehat{G^4}(\lvert t\rvert)$ (NOT the sup-kernel): required to decide the quartic-difference endpoint, where the sup-grade inflation eats almost the whole $\times2.6$ margin. Until computed, the third-order lift is UNDETERMINED at the endpoint, not merely marginal.

**Status:** OPEN

**Source:** quartic-difference-channel v1.0.

**EVALUATED 2026-06-07** (scscope_ghat4_pertransfer.py 7/7, scscope-endpoint-joint-assessment v1.0): per-transfer Ghat4(t)=(J*J)(t) on the realized chords; convention-free shape reduction max Phi/Phi_sup = 0.64 (Ghat4 broad, only down to 0.64 at t=2q0), so R_max ~ R_sup*0.64 ~ 1.02. Quartic-difference ALONE x1.29 > 1, but R_max >= 1 triggers the joint re-derivation; does NOT resolve the endpoint alone. OPEN.

<a id="r-u6-1"></a>
### **R-U6-1**

**Statement:** Tadpole formal alignment: a written proof that normal-ordered matched bookkeeping removes the tadpole, that competitors are evaluated at their own stationarity points (off-optimum residual absorbed in-layer), and that $O(F^3)$ resonant triples are inside the production $N_4$ accounting. Caps the tadpole lemma at T3 until closed.

**Status:** DISCHARGED 2026-06-12 (operator CONFIRM, Tadpole-Reabsorption-Lemma-RU61-RU62-260612): written proof via the Hermite normal-ordering identity, aligned term-by-term with the production bookkeeping (j=0 reproduces the 0.25U+2.5VM line; j=1 the 3uM+15vM^2 gap dressing = m_R-r; j=3 leaves g_3 = u_eff c + (10v/3)c^3 normal-ordered BY CONSTRUCTION); <:d^3::d^3:> = 6G^3, tadpole 9M^2G absent identically; off-optimum + resonant-O(I^2) cases written out; v1.0's '3M g_3' mechanism self-caught as over-counting by exactly 15vM^2 (double self-loop symmetry factor) and corrected. U4 tadpole rows struck; sunset = the sole remaining third-cumulant channel. NO tier change (B5 stays T5 pending T-031).

**Source:** tadpole-reabsorption-lemma v1.1

<a id="h-endpoint-thinness-accepted"></a>
### **H-ENDPOINT-THINNESS-ACCEPTED**

**Statement:** B5 T6-conditional acceptance hypothesis (operator verdict D3-A, 2026-06-12): the SC-SCOPE endpoint closure is structurally THIN (certified joint x1.040-x1.082 > 1 on W_SC, sunset-capped at x1.13) and this thinness is ACCEPTED as sufficient for the B5 closure statement. Removing this hypothesis (hardening the sunset accounting beyond thin, e.g. a proved K_floor <= 0.52 T' floor) is the registered B5 T7 path.

**Status:** REMOVED 2026-06-12 (operator verdict after the clean-run CONFIRM of scscope_sunset_pertransfer.py 8/8): the per-transfer sunset hardening (SC-SCOPE-SunsetHardened-T6-260612) replaces the single-J0 sup anchor by the realized D-weighted loop average on the admissible chords -- S x1.129 -> x2.994 (shape 0.377), endpoint joint x1.040 -> x2.023 (rho=6.55) / x1.082 -> x2.396 (rho=12.6), saturation cap x1.13 -> x2.994. The endpoint closure is COMFORTABLE, SUNSET-HARDENED; the thinness classification is retired. B5's hypothesis set shrinks to {H-NONLATTICE-REMAINDER-EXCLUDED}; the single remaining B5 T7 blocker is T-030. REFINED VERDICT (same day, operator adversarial review): the removal is CONDITIONALLY accepted -- the final stamp requires the mixed-dressing justification. DELIVERED (v1.2 + script v1.1.0, 10/10): monotonicity argument (J and 1/D both decrease with dressing -> lightest assignment is the adversarial corner) + machine worst-case (anchor,anchor): shape_worst = 0.4247, S_worst = x2.659 > 2, joint = x1.886 -- the removal survives the worst dressing assignment.

**FINAL-STAMPED 2026-06-12**: the operator ratified the v1.2 addendum after an independent clean-run (1/1 script, 10/10 asserts, 0 FAIL); all four operator attacks resolved (derivation compatibility / mixed-dressing worst case / t_min corner / no-T7-overreach). REMOVAL FINAL; PUBLISHED-BUNDLE CONFIRMED as SC-SCOPE-SunsetHardened-T6-260612.

**Source:** scscope-sunset-pertransfer-hardening v1.3; SC-SCOPE-SunsetHardened-T6-260612 bundle

<a id="h-nonlattice-remainder-excluded"></a>
### **H-NONLATTICE-REMAINDER-EXCLUDED**

**Statement:** B5 T6-conditional scope hypothesis (operator verdicts D1-A/D2-A/D3-A, 2026-06-12): arbitrary non-lattice competitors are explicitly EXCLUDED from the B5 closure scope and tracked at the T-030 frontier (non-load-bearing for the published C_full head, which caps T' <= 10 elementarily by Lemma 2). H-ADM-COH stands DISCHARGED for the lattice class (certificate-backed, residual (a) pinned). Closing T-030 removes this hypothesis.

**Status:** RECLASSIFIED 2026-06-13 (route-3, R-037, operator promotion): from CONDITIONAL HYPOTHESIS to DEFINITIONAL SCOPE. The beyond-layer bound depends on the competitor only through (T',n); the coherence circle-packing Lemma 2 (pure geometry, res5_036) caps T'<=floor(2pi/theta_min)<=10 for EVERY admissible competitor, lattice OR non-lattice, so the non-lattice remainder is covered and arbitrary-Q DR-2 only removes the admissibility cap (frontier strengthening). H-NONLATTICE is NON-LOAD-BEARING for the admissibility-bounded statement; B5 promoted T6-conditional -> T7-SCOPE_{admissibility-bounded} (substantive hypothesis set now empty; Attack-4 (T',n)-only chain audit 6/6). Load-bearing ONLY for the strictly stronger admissibility-discharged unrestricted statement = T-030 (OPEN).

**Source:** b5-t7scope-assignment-260613-v1.0; b5-nonlattice-nonloadbearing-route3-260613-v1.0

<a id="r-u6-2"></a>
### **R-U6-2**

**Statement:** Tadpole/cubic coefficient script: machine/symbolic verification of the dressed-coupling Wick coefficients ($u_{\rm eff}=u+10vM$), without which all third-cumulant coefficients are estimate-grade.

**Status:** DISCHARGED 2026-06-12 (operator clean-run CONFIRM, same package): ru61_tadpole_alignment.py 8/8 asserts PASS, exit 0 -- pairing split 15=6+9 brute-forced; exact Hermite coefficients; j=0 identity u/4+(5/2)vM = u_eff/4 = 0.671256066417 (1e-15); j=1 source 3uM+15vM^2 = m_R-r = 0.29952571 (independent gap solver); Lemma-1 boxed identity u_eff(M_+) = (1/3)sqrt(9u^2-60vr) (1e-12); the 15vM^2 over-count quantified (0.58181468); HEX argmin 0.3093733 oracle reproduced; endpoint remainder 4.34e-10 < 1e-6; u_eff(M_R) = 2.685 matches the certified value. JSON artefact runs/260612-ru61-tadpole-alignment/.

**Source:** tadpole-reabsorption-lemma v1.1 + ru61_tadpole_alignment.py

<a id="dr2-share"></a>
### **DR2-SHARE**

**Statement:** The DR-2 extraction obstruction: adjoining rich circles breaks $\sum_s I_{C_s}^2\le I^2$ through point-sharing, so the extraction iteration cannot keep the homogeneous cap. The formal bottleneck of the elementary DR-2 route; equivalent to bounding the carrier-richness $\chi(P)=O(\mathrm{polylog})$ for the extraction route only (NOT all polynomial/incidence methods).

**Status:** MOOT for the lattice mainline (H-ADM-COH discharged 2026-06-08 for the crystallographic class via R-026/R-027/R-028); OPEN for arbitrary real-point Q (off critical path, legacy fallback)

**Source:** dr2-extraction-lemmas v1.0; strategy/dr2-impact-analysis-260606.md; strategy/dr2-external-research-assessment-260608.md (external research Math447-469, operator-supplied 2026-06-08: DR-2 reduces to the Pencil Rigidity / Pair-Sum Surface Multiplicity conjecture -- a sound CONDITIONAL reduction at proof-sketch grade, NOT a closure; the residual is sharpened from carrier-richness polylog to one named conjecture; gate stays OPEN off critical path; the external T7_conditional-robust tier label is NOT adopted -- repo B5 T5 / B1 T6 are canonical).

**FORMALISED 2026-06-08** (dr2-pencil-rigidity-reduction v1.0, dr2_cross_energy_lemma.py 6/6): the DR-2 residual is reduced to ONE named conjecture -- (a) cross-energy lemma R-021 (T7, verified + a constant correction to the external 2|A||B|); (b) Pencil Rigidity / Pair-Sum Surface Multiplicity CONJECTURE (T2, falsification gate E_+(Q_N)>=N^{2+delta}); (c) PSM => DR-2 reduction (T3 sketch, gaps alpha/beta marked). DR-2 stays OPEN off critical path; no tier change..

**DECOUPLING ROUTE 2026-06-08**, CORRECTED after operator audit (dr2-decoupling-closure v1.1, dr2_decoupling_exponent.py 4/4; reviews/2026-06-08-dr2-decoupling-critical-audit.md): the l2-decoupling route to DR-2 is PROMISING but NOT a closure as first drafted. The operator audit found the E_+ = integral|f|^4 TORUS identity FALSE for non-integer q in S^2 (corrected to the Besicovitch limit / Schwartz majorant), the non-separated multi-scale reduction OMITTED (now written, cross-scale energy step marked OPEN), and N^{2+eps} conflated with N^2 log^B. Honest grade: SEPARATED Q is T6 PROVED CONDITIONAL on Bourgain-Demeter decoupling (d=3, p=4); ARBITRARY finite Q (DR-2 proper) is T3 PROOF SKETCH. Numerics stand (exponent ~2 sphere vs ~3 flat; curvature/R-007 mechanism). R-022 (downgraded T6->T4). NO flip: DR2-SHARE stays OPEN, B5 stays T5, B1 stays T6, and H-ADM-COH STAYS in the B1 hypothesis set. Next: write the cross-scale energy bound to complete the multi-scale reduction; then operator may consider the flip.

**AFFINE-INVARIANCE 2026-06-08** (dr2-affine-invariance, dr2_affine_invariance.py 4/4): the clustering / cross-scale concern is RESOLVED in principle -- additive energy is EXACTLY affine-invariant (R-023), and the paraboloid's parabolic rescaling unfolds any cap-cluster to a unit-scale config of identical energy, so clustering cannot beat N^2; extreme-clustering numerics confirm exponent ~2 uniformly down to 0.05-rad caps. This lifts the UNRESTRICTED DR-2 from T3 PROOF SKETCH to T4 STRONG EVIDENCE (separated case stays T6 PROVED CONDITIONAL on decoupling). STILL NO FLIP: the full induction-on-scales is cited not reproduced, so this is not yet T6; DR2-SHARE stays OPEN, B5 T5, B1 T6, H-ADM-COH retained. v1.1

**RE-ISSUE 2026-06-08** (proper versioning; operator review): Section 2.1 resolves the four Schwartz-majorant rigor points -- the upper bound is gap-independent (hat-eta>=0), so the separated-case majorant->decoupling link is clean modulo decoupling. v1.0 superseded. Grades + no-flip unchanged.

**CROSS-SCALE INDUCTION 2026-06-08** (dr2-cross-scale-induction v1.0, dr2_decoupling_iteration.py 3/3, R-024): the cross-scale energy step is now WRITTEN -- the decoupling-iteration inequality E_+(Q) <=_eps delta^{-eps} (sum_theta sqrt E_+(Q_theta))^2 (derived from decoupling + the majorant) + the R-023 recursion reduce arbitrary finite Q to the separated base case; iteration constant numerically bounded (K<=1.94, scale-stable). The single CITED-not-reproduced step is the tight per-level constant bookkeeping (Bourgain-Demeter). This lifts the UNRESTRICTED DR-2 from T4 to T5 (structurally-complete reduction). STILL NO FLIP: whether T5 + the cited bookkeeping warrants T6 + a DR2-SHARE flip + removing H-ADM-COH is an OPERATOR DECISION. DR2-SHARE OPEN, B5 T5, B1 T6, H-ADM-COH retained. CROSS-SCALE INDUCTION v1.1

**REPAIR 2026-06-08** (dr2-cross-scale-induction v1.1, dr2_decoupling_iteration.py v1.1 4/4; reviews/2026-06-08-dr2-cross-scale-induction-audit.md): operator audit found v1.0's iteration lemma RE-USED the false ||f_theta||_4^4=E_+(Q_theta) identity (same class as the corrected torus identity) and described the cap rescaling as landing exactly on the paraboloid. v1.1 repairs both -- the bridge is the BESICOVITCH MEAN M(|f_Q|^4)=E_+(Q) (exact for non-integer q in S^2), and the rescaled cap is a uniformly-curved C^2 graph patch handled by decoupling STABILITY for nondegenerate C^2 perturbations (NOT the literal paraboloid). The residual is now TWO cited ingredients: R1 local-to-global translate-averaging (local cap norm -> E_+(Q_theta)), R2 multi-scale eps-bookkeeping. v1.0's T5 is WITHDRAWN; honest grade T4+ STRONG EVIDENCE / T5-candidate pending operator acceptance of R1+R2. Numerics ILLUSTRATIVE (exact-E_+ audit gate + explicit PROXY-partition caveat). STILL NO FLIP: DR2-SHARE OPEN, B5 T5, B1 T6, H-ADM-COH retained.

**CIRCLE-RICHNESS REDUCTION 2026-06-08** (dr2-circle-richness-reduction v1.0, dr2_circle_richness.py 5/5, R-025): an UNCONDITIONAL (decoupling-free, conjecture-free) result -- the sphere additive energy obeys E_+(Q) <= (1+T'(Q))N^2, where T'(Q) is the max occupancy of a proper sum-level circle C_m = S^2 cap {x.m=|m|^2/2} (both summands of a+b=m lie on C_m; the m=0 antipodal term is split off). This makes the carrier-richness chi(P) EXACT (= T', constant 1) and proves the easy direction rigorously: sets with T'=O(1) (random, great-circle: T'=2) satisfy DR-2 ELEMENTARILY with no decoupling; DR-2 in general follows from T'<=_eps N^eps (Cor 2). Honest scope: the condition is SUFFICIENT not tight -- the rich latitude circle has T'=N yet E_+~3N^2 -- so bounding T' is the open carrier-richness problem and may be stronger than DR-2. Grades: Lemma A + Cor 1 are T7 UNCONDITIONAL; general DR-2 unchanged. NO flip: DR2-SHARE OPEN, B5 T5, B1 T6, H-ADM-COH retained. LATTICE-CLASS CLOSURE (Route A) 2026-06-08 (dr2-lattice-divisor-closure v1.0, dr2_lattice_divisor.py 5/5, R-026): the configurations DR-2 must handle in TECT are NOT adversarial -- they are BCC/FCC momentum-shell LATTICE points on a sphere. For Q = Lambda cap {|x|^2=R}, every sum-level circle C_m lies in a rational plane, so #(Q cap C_m) is a binary-quadratic-form representation count, bounded by the CLASSICAL circle-divisor bound [DIV-CIRC]: #lattice points on a circle of sq-radius <=R is O_eps(R^eps). Hence T'(Q) <<_eps R^eps and, by Lemma A (R-025), E_+(Q) <= (1+C_eps R^eps)N^2 = N^{2+eps} for Gauss-typical shells (R~N^2) -- DR-2 for the lattice class, DECOUPLING-FREE (no Bourgain-Demeter, no R1/R2). Verified exactly on Z^3 shells R=101..9974: T'/N falls 0.107->0.024 (log-log slope 0.177, R^o(1)), E_+/N^2<=5.3, lemma holds; Z^3=FCC (lattice-independent). Grade T6 CONDITIONAL on [DIV-CIRC] (textbook; operator may elevate to T7). HONEST SCOPE: closes the ADDITIVE-ENERGY DR-2 for the LATTICE class only; arbitrary-Q DR-2 stays OPEN, and whether the T'-to-chi(P) (carrier-richness) equivalence discharges H-ADM-COH in B1 is an OPERATOR integration decision. NO flip made here: DR2-SHARE OPEN, B5 T5, B1 T6, H-ADM-COH retained. LATTICE-CLASS T7 (full [DIV-CIRC] proof) 2026-06-08 (dr2-lattice-divisor-closure v1.1, dr2_divcirc_proof.py 4/4, R-026 v1.0 T6 -> v1.1 T7): [DIV-CIRC] is now PROVED, upgrading the lattice-class DR-2 from T6 CONDITIONAL to T7 UNCONDITIONAL (operator pre-authorised on full expansion). Key step: the sum-circle C_m has centre m/2, so the substitution y=2x-m sends Z^3 cap C_m injectively into {y in Lambda_m=Z^3 cap m^perp : |y|^2=4R-|m|^2}, a HOMOGENEOUS rank-2 representation count <= 6 d(4R-|m|^2) by the Dirichlet class-number formula (single class <= sum over classes = w sum chi(d) <= 6d, UNIFORM in m), <<_eps R^eps by the divisor bound. So T'(Q) <<_eps R^eps and E_+(Q) <= (1+C_eps R^eps)N^2 = N^{2+eps} for typical shells -- DR-2 for the lattice class, DECOUPLING-FREE, modulo only TEXTBOOK number theory. Verified exactly (substitution + T'<=6d, T'/6d<=0.25). HONEST SCOPE unchanged: additive-energy DR-2 for the LATTICE class only; arbitrary-Q OPEN; the chi(P)<~T' carrier-richness link and any H-ADM-COH discharge remain an OPERATOR integration decision. NO flip: DR2-SHARE OPEN, B5 T5, B1 T6, H-ADM-COH retained.

**STEP-5B INTEGRATION 2026-06-08** (dr2-step5b-integration v1.0, dr2_weighted_energy.py 3/3, R-027): the operator-requested DR2-SHARE integration. G1'''-AE is the WEIGHTED additive energy sum_t w_t^2 <= K(lambda'I)^2; the 'carrier' of a+b=t is the sum-level circle C_t (occupancy T'); H-ADM-COH is the angular-SEPARATION restriction. WEIGHTED Lemma A (Cauchy-Schwarz + t=0 split): sum_t w_t^2 <= (1+T'(Q))||c||_2^4 for ANY amplitudes. With R-026 (lattice T'<<_eps R^eps): for any subset Q of a crystallographic shell, sum_t w_t^2 <= (1+C_eps R^eps)||c||_2^4 -- the G1'''-AE bound with SUBPOLYNOMIAL K~R^eps, NO separation. So the lattice arithmetic REPLACES H-ADM-COH for the physical class, and the chi(P) extraction obstruction is BYPASSED (additive energy bounded directly, not via the iteration). Both weighted Lemma A and the integration bound are T7. HONEST RESIDUALS (operator-level, all that remain for an actual H-ADM-COH discharge): (a) K is subpolynomial R^eps not constant (consistent with measured 2.04-2.08 + margins x55.6/x8.8/x2.1, but the gate-keeper confirms margin survival); (b) modeling: competitors are exactly crystallographic-shell subsets; (c) the non-transversal high-n corner is a lattice subset, hence covered. NO flip enacted: DR2-SHARE OPEN, B5 T5, B1 T6, H-ADM-COH retained -- the discharge + B1 re-tier is the OPERATOR decision.

**DISCHARGE DECISION 2026-06-08** (dr2-hadmcoh-discharge-decision v1.0, dr2_hadmcoh_margin.py 3/3, R-028; R-027 re-issued v1.1 complex-amplitude notation; lattice note v1.2): residual (a) is SETTLED as a NUMERICAL INEQUALITY (operator point 3) -- K_adm=1+T'(Q) <= K_allowed(n)=8+4sqrt(14)sqrt(n) on every crystallographic shell and sub-pattern (margin 10.6x-15.8x, GROWING; worst sub-pattern 0.307), replacing the subpolynomial-K judgment; (b) competitor class = crystallographic-shell subsets (operator-affirmed); (c) the non-transversal high-n corner is a lattice subset, covered. So H-ADM-COH (which only secured G1'''-AE via angular separation) is a DISCHARGE-CANDIDATE for the lattice class, with proposed B1 reduction {H-LAYER,H-ADM-COH,SC-SCOPE}->{H-LAYER,SC-SCOPE}. LEDGER STATUS (operator-endorsed): G1'''-AE_lattice CLOSED@T7, H-ADM-COH DISCHARGE-CANDIDATE, DR2-SHARE OPEN pending operator integration. NO flip enacted: B1 T6, B5 T5, H-ADM-COH retained pending the operator discharge decision.

**DISCHARGE ENACTED 2026-06-08** (operator decision, reviews/2026-06-08-hadmcoh-discharge-authorization.md; dr2-hadmcoh-discharge-decision v1.2): the operator ACCEPTED residuals (a)-(c); H-ADM-COH is DISCHARGED for the crystallographic lattice class and B1's active hypothesis set is reduced {H-LAYER,H-ADM-COH,SC-SCOPE} -> {H-LAYER,SC-SCOPE} (B1 tier UNCHANGED T6). DR2-SHARE is thus MOOT for the lattice mainline; arbitrary-Q DR-2 stays OPEN as legacy fallback. Ledger status: G1'''-AE_lattice CLOSED@T7, H-ADM-COH DISCHARGED@lattice, DR2-SHARE MOOT@lattice/OPEN@arbitrary. ===

**D2-A RESCOPED 2026-06-12** (T-031 verdicts): DR2-SHARE -> RESCOPED-TO-T030-NONLOADBEARING. Basis: the published C_full head theorem caps T' <= floor(2pi/theta_min) = 10 elementarily (Lemma 2 of the Reading-H package), so arbitrary-Q DR-2 is a FRONTIER STRENGTHENING (task T-030), not a hole in any published claim; keeping the gate OPEN invited that misreading. The mathematical content of the arbitrary-Q problem is unchanged and tracked at T-030 (Bourgain-Demeter-conditional T6 for separated Q; PSM conjecture route T2). ===

**FRONTIER ADVANCE 2026-06-12** (overnight dispatch, operator-ACCEPTED; dr2-t030-frontier-consolidation v1.1): R-033 -- the unconditional record improves to E_+(Q) <= C N^{9/4} for EVERY finite Q in S^2 (dyadic occupancy + classical circle incidence, PROVED MODULO [CIRC-INC]; 9/9 clean-run); R-034 -- the conditional chain's R1 local-to-global bridge is a WRITTEN PROOF (3/3 clean-run), residuals {R1,R2} -> {R2}. T-030 itself remains OPEN for N^{2+eps}. (Dispatch defect parent-caught and repaired: the draft used the TAKEN ledger IDs R-030/R-031 without the numbering pre-check.)

<a id="cp-unitarity"></a>
### **CP-UNITARITY**

**Statement:** CP structure and unitarity completion of the per-generation quantum-consistency closure

**Status:** OPEN

**Source:** legacy: Pillar-7 record

<a id="scheme-2loop"></a>
### **SCHEME-2LOOP**

**Statement:** 2-loop scheme-independence audit of the gravity 1-loop closure

**Status:** OPEN (recommended)

**Source:** legacy: Pillar-3 record

<a id="pred-g-freeze"></a>
### **PRED-G-FREEZE**

**Statement:** Pre-registered input freeze for an independent $a_{\rm BCC}$ → $G$ prediction

**Status:** OPEN

**Source:** `predictions/prediction-ledger.md`


## Named hypotheses

| Hypothesis | Summary |
|---|---|
| [**H-LAYER**](#h-layer) | DISCHARGED@T7 … |
| [**A1-KERNEL-CONV**](#a1-kernel-conv) | DEFINITIONAL INPUT … |
| [**G1-OFFDIAG-MARGIN**](#g1-offdiag-margin) | CLOSED@2026-06-10 … |
| [**G2-EXTERNAL-REFEREE**](#g2-external-referee) | OPEN … |
| [**G3-OPERATOR-SIGNOFF**](#g3-operator-signoff) | CLOSED@2026-06-10 … |
| [**EXT-EXTREMAL**](#ext-extremal) | T2 CONJECTURE … |
| [**H-ADM-COH**](#h-adm-coh) | Unrestricted-class closure via DR-2 … |
| [**H-ANCHOR**](#h-anchor) | Off-anchor neighbourhood = ROBUSTNESS-MU2 … |
| [**SC-SCOPE**](#sc-scope) | The all-orders lift is OPEN until ALL FOUR named inputs are completed … |
| [**H-A0**](#h-a0) | REPLACED 2026-06-06 by H-ANCHOR + G-A0-DUI via the sign-decomposition theorem … |
| [**H-SUPPRESSION**](#h-suppression) | H-SUPPRESSION-DISCHARGE |
| [**H-LEGACY-CHAIN**](#h-legacy-chain) | `governance/migration-plan.md` M2 |
| [**H-CP2-BUNDLE-DATA**](#h-cp2-bundle-data) | Migration … |
| [**A2-H1-KERNEL-POSITIVITY**](#a2-h1-kernel-positivity) | SATISFIED@anchor (mu^2>0) … |
| [**A2-H2-SEXTIC-COERCIVITY**](#a2-h2-sextic-coercivity) | SATISFIED@anchor (gamma>0) … |
| [**C6-BCC-PREMISE-BLOCKED**](#c6-bcc-premise-blocked) | BLOCKED -- BCC-structure premise unavailable … |
| [**A3-H1-DIM3-Q4-KERNEL**](#a3-h1-dim3-q4-kernel) | d=3 with q^4 kernel => D<0 … |
| [**A3-H2-IR-POSITIVITY**](#a3-h2-ir-positivity) | mu^2>0 => K>=mu^2>0 (IR finite) … |
| [**A3-GRAPHWISE-CONVERGENCE**](#a3-graphwise-convergence) | CLOSED@spectral (T6 ratified 2026-06-23); lattice=Route B open … |

<a id="h-layer"></a>
### **H-LAYER**

**Statement:** Transcribed from Math437 v1.2 §Hypotheses (`archive/legacy/notes/Math437/TECT-Math437-Step5-Pattern-Universal-Restoration-Isotropic-Layer-260604-v1.2.tex.txt`): the comparison is the **isotropic Gaussian–Hartree variational layer**. Within the diagonal-Gaussian class the isotropic dressing is the infimum (Math427, T6 conditional on H-diag); beyond-diagonal refinements (Bloch off-diagonal, $\sigma(x)$ inhomogeneity) are EXECUTED for the five enumerated readings (Math428–432, Math434, Math436) but remain unexecuted for non-enumerated patterns — that residual is exactly STEP-5B.

**Discharge path:** DISCHARGED@T7 (operator-enacted 2026-06-10): H-LAYER is no longer a hypothesis -- the isotropic Gaussian-Hartree layer G_* is the strict comparison infimum over C_phys (T7 proposition, t7-proposition-assembly v1.1). STEP-5B closed class-wide (T-016 isotropy / T-017 chi(P) floor / T-018-020 off-diagonal R_lead<1 / T-021 SC-SCOPE third-cumulant); off-shell excluded non-circularly (offshell-domination-theorem v1.1, rho_off^ext=0.572<1); thresholds theorem-grade (blocker-b-hardening v1.1). Internal route audit t7-route-internal-audit v1.0 (61/61 chain asserts, 17/17 constants). B1/B2 -> T7.

<a id="a1-kernel-conv"></a>
### **A1-KERNEL-CONV**

**Statement:** The microscopic-theory DEFINITION on which every TECT result rests: the production-kernel convention $r_{\rm braz}=K(q_0)=\mu^2$ (claim A1-KERNEL-CONV, T5 PINNED-CLOSURE). Named as the sole definitional input of the B1/B2 T7 comparison theorem after H-LAYER is discharged: the T7 reads 'GIVEN the A1 kernel convention, Reading-H is selected unconditionally over C_phys'. This is a DEFINITION (pinned), not an unproven assumption -- the theory being compared.

**Discharge path:** DEFINITIONAL INPUT (T5 PINNED; carried as a named hypothesis of B1/B2 T7 per TSv2 sub-T6-dep rule)

<a id="g1-offdiag-margin"></a>
### **G1-OFFDIAG-MARGIN**

**Statement:** C_full off-diagonal margin: accept the thin R_lead<=0.974<1 (x1.026, antipodal lemma fallback) OR promote EXT to x5.39.

**Discharge path:** CLOSED@2026-06-10 -- UPGRADED: the coherence circle-packing lemma (T'<=floor(2pi/theta_min)=10, res5_036 5/5) makes the off-diagonal margin COMFORTABLE (x1.96, R_lead<=0.510<1) for the full admissible class; selection binds (I_off^coh=3.92e-3>I_c^sel) => full Step-1 window (20% headroom). The thin x1.026 acceptance is SUPERSEDED by proof; EXT no longer needed for comfort (stays T2 optional).

<a id="g2-external-referee"></a>
### **G2-EXTERNAL-REFEREE**

**Statement:** Fully-external / second-author reproduction of the C_full route.

**Discharge path:** OPEN -- validation/publication gate, NOT an internal proof blocker (standing).

<a id="g3-operator-signoff"></a>
### **G3-OPERATOR-SIGNOFF**

**Statement:** Operator enactment of the C_full scope widening (no-auto-T7).

**Discharge path:** CLOSED@2026-06-10 (operator-enacted T7-SCOPE_{C_full, thin O}).

<a id="ext-extremal"></a>
### **EXT-EXTREMAL**

**Statement:** Tight additive-energy extremal theorem K_floor<=~3 (Freiman-type), max attained in the arithmetic subclass.

**Discharge path:** T2 CONJECTURE (strong evidence; optional margin upgrade x1.026->x5.39; operator: do NOT promote). Falsifier: admissible Q with K_floor>13.

<a id="h-adm-coh"></a>
### **H-ADM-COH**

**Statement:** Coherence-resolution admissibility amendment (operator verdict #14, 2026-06-05): an admissible competitor pattern is a finite set of shell readings with pairwise angular separations $\ge \theta_{\min}(\hat r)=\sqrt{\hat r}/(2q_0^2\sqrt C)$; spectral mass at finer scales belongs to the Gaussian-sea sector. Energy-faithful (coherence indistinguishability lemma, AddC: restructuring shifts $F$ by $\le c_{\rm ind}I^2$ = margin/$\times33$+); this is the class on which STEP-5B is CLOSED-CONDITIONAL.

**Discharge path:** Unrestricted-class closure via DR-2 (research-grade), or an all-amplitude indistinguishability proof

**DISCHARGE-CANDIDATE 2026-06-08** (dr2-hadmcoh-discharge-decision v1.0, R-028): for the physical crystallographic momentum-shell competitor class, the lattice arithmetic (R-026 T7 + R-027 T7) secures G1'''-AE WITHOUT angular separation, with finite margin K_adm=1+T'(Q) <= K_allowed(n)=8+4sqrt(14)sqrt(n) (10.6x-15.8x, growing). H-ADM-COH is therefore a DISCHARGE-CANDIDATE -- removable from the active B1 set for the lattice class (legacy fallback for hypothetical non-lattice competitors) upon operator acceptance of residuals (a)-(c). NOT yet discharged; B1 stays T6 CONDITIONAL on {H-LAYER,H-ADM-COH,SC-SCOPE}. === DISCHARGED@lattice class 2026-06-08 (operator decision ENACTED): the discharge condition ('unrestricted-class closure via DR-2') is MET for the crystallographic momentum-shell competitor class -- R-026 (lattice additive-energy DR-2, T7) + R-027 (weighted G1'''-AE bridge, T7) + R-028 (finite margin K_adm<=K_allowed(n), 10.6x-15.8x) secure G1'''-AE without angular separation. H-ADM-COH is removed from the active B1 hypothesis set; retained here as a LEGACY FALLBACK for hypothetical non-lattice (arbitrary real-point) competitors, which are not part of the TECT mainline. === D1-A RE-AFFIRMED + RESIDUAL (a)

**PINNED 2026-06-12** (T-031 verdicts; t6-conditional-assignment-260612-v1.0): R-026 is now T7-NTstandard (Lemma NT pinned in-bundle, DR2-Lattice-T7-NTstandard-260612) and the residual-(a) subpolynomial-K sufficiency -- previously an asserted judgment -- is PINNED by the exhaustive applied check (2,644,976 sums across R=101..9974, worst ratio 0.250; enumerated competitors K_floor<=12). H-ADM-COH stands DISCHARGED for the lattice class with the discharge now certificate-backed; the non-lattice remainder is the T-030 frontier (non-load-bearing for the C_full head, which caps T'<=10 by Lemma 2). Enters B5's T6-conditional hypothesis set H_B5^T6 as a SCOPE FACT.

<a id="h-anchor"></a>
### **H-ANCHOR**

**Statement:** VERIFIED ANCHOR FACT (demoted from hypothesis 2026-06-06): at $\mu^2=0.005$, $m^*>m_w$ ($m_w=r+15vM_c^2=0.0392407$; $\times7.76$) and $M_R>M_c$ ($\times4.12$), closed-form on the anchor constants and machine-verified (G-A0-VER 14/14). With G-A0-DUI closed, the $A=0$ uniqueness is unconditional at the anchor, so this is a verified DEPENDENCY, not an assumption; removed from B2/B1 hypothesis sets.

**Discharge path:** Off-anchor neighbourhood = ROBUSTNESS-MU2 (the sole residual of the former H-A0)

<a id="sc-scope"></a>
### **SC-SCOPE**

**Statement:** Second-cumulant bookkeeping scope: the whole Sector-B fluctuation analysis is at matched second-cumulant order (the $P^2$-representation, the layer comparison, STEP-5B). Substantive, not a formality: the third-cumulant endpoint corrections (sunset + quartic-difference, U4/U15) are marginal ($\times0.97$/$\times1.0$ under sup-kernels at $I=2\times10^{-3}$). The selection SIGN holds at this scope; the all-orders lift is open.

**Discharge path:** The all-orders lift is OPEN until ALL FOUR named inputs are completed (operator review 2026-06-06): M-ENDPOINT + GHAT3-Q0 (optional) + GHAT4-PERTRANSFER + R-U6-1 (tadpole alignment), re-assembled as a JOINT second+third-order inequality. At sup-kernel grade the endpoint third-order lift FAILS (sunset x0.97, quartic-difference x1.0, tadpole-if-uncancelled x0.53); per-transfer kernels are load-bearing.

**ADVANCE 2026-06-07** (scscope-mendpoint-evaluation v1.0): the SUNSET axis is resolved POSITIVE -- M-ENDPOINT = M(0.33675) = 0.10495 evaluated directly, dressed endpoint x1.13 > 1 (the U4 x0.97 was a frozen-coupling artefact, not a real obstruction). SC-SCOPE stays OPEN on the two remaining load-bearing inputs GHAT4-PERTRANSFER (per-transfer quartic-difference) + R-U6-1 (tadpole alignment), to be re-assembled as the joint second+third-order inequality. v1.1 (operator review 2026-06-07): sunset axis reinforced (M-ENDPOINT certificate + single-J0 conservatism); the U4 SUNSET-AXIS failure was a frozen-coupling artefact (NOT the third-cumulant endpoint, which stays open).

**HONEST NEGATIVE 2026-06-07** (scscope_joint_endpoint.py 5/5, scscope-endpoint-joint-assessment v1.0; NG-2026-06-07-scscope-endpoint-joint): the JOINT second+third-order endpoint inequality does NOT close -- the individually-positive channels (2nd x2.60, sunset x1.13, quartic-difference x1.29) jointly over-consume the layer margin by x1.32 -> joint endpoint x0.757 < 1. SC-SCOPE stays OPEN at the endpoint; B1 T6 UNAFFECTED (SC-SCOPE is a named hypothesis). Path: joint incompatible-pairing argument or sharper per-transfer bounds.

**PAIRING EXHAUSTED 2026-06-07** (scscope_joint_pairing.py 4/4, scscope-joint-pairing v1.0): the most-favourable joint pairing gives only x0.905 < 1 (sunset alone x1.076 near-saturating); per-transfer refinements done. Remaining: STEP-5B endpoint floor rho>~3.9 at I=2e-3, OR accept 2nd-cumulant at the endpoint (all-orders FEASIBLE for I<=1e-3).

**DECISION 2026-06-07** (operator-authorized, scscope-scope-decision v1.0): second-cumulant scope ACCEPTED at the I=2e-3 endpoint; all-orders third-order lift ESTIMATE-FEASIBLE (estimate-grade, not proved) for I<=1e-3 (paired joint x3.1 at 1e-3, x20.7 at 4e-4). The endpoint is a recorded SCOPE, not an open research action. B1 T6 UNCHANGED (SC-SCOPE remains the named second-cumulant hypothesis). Optional reopening: STEP-5B endpoint floor rho>~3.9. FLOOR SHARPENING (candidate lift) 2026-06-08 (scscope-floor-sharpening v1.0, scscope_floor_sharpening.py 5/5, R-029): the named 'sharper STEP-5B endpoint floor rho>~3.9' route is COMPLETED. The endpoint floor rho=2.58 used the kappa-balanced additive-energy bound K(n_pack)=8+4sqrt(14)sqrt(n_pack)=103.5, which OVERSHOOTS the Lemma-A bound 1+T'<=1+n_pack=41.7 at the SMALL endpoint n_pack=40.7 (prefactor c_R~15). Substituting the tighter additive-energy constant (R-025 Lemma A; R-026 lattice T'~tens) gives rho_lat>=6.4 (separated T'<=n_pack=41), paired=rho_lat/2.872>=2.23>1 -- the all-orders endpoint CLOSES (break-even T'<=67 for rho>=3.9; T'<=92 for paired>=1). T4 STRONG EVIDENCE. NAMED RESIDUAL: the exact constant map between the kappa-balanced K(n) and the Lemma-A 1+T' (the -4I^2 trivial subtraction / averaging; both bound the same lambda'-free (<F^4>-4I^2)/I^2, and the kappa-balanced sqrt(n) is the unconditional triple-count bound that 1+T' refines). NO flip pending the reconciliation: SC-SCOPE stays B1's named hypothesis, B1 T6 on {H-LAYER,SC-SCOPE} unchanged. This supersedes the 'recorded scope, not open' status of scscope-scope-decision v1.0: the endpoint now has a strong-evidence lift route, not just I<=1e-3 feasibility.

**LIFTED 2026-06-08** (operator-authorised on the reconciliation; scscope-floor-sharpening v1.2, R-029, scscope_constant_map.py 3/3): the named residual (constant map) is RESOLVED -- in the STEP-5B convention K_floor=sum_{t!=0}w_t^2/(lambda'I)^2, and the weighted Lemma A (R-027) t!=0 part gives sum_{t!=0}|w_t|^2<=T'(M)I^2, so K_floor<=T'(M) EXACTLY (verified K_floor/T'<=0.52, w_0=I; the -4I^2 is conservative). With K_floor<=T'<=n_pack =40.7 (separated) or T'~tens (lattice), rho_lat>=6.55>=3.9, paired>=2.28>1 -- the all-orders endpoint floor obstruction is PROVED removed. SC-SCOPE (the 2nd-cumulant restriction) is LIFTED from B1's active set: {H-LAYER,SC-SCOPE}->{H-LAYER}, B1 tier UNCHANGED T6. HONEST CAVEAT: the all-orders selection's THIRD cumulant rests on the estimate-grade inflation (2.872; R_s,R_q -- the operator-accepted basis), NOT rigorously proved; the second-order floor and the selection sign are rigorous. This supersedes the scscope-scope-decision v1.0 '2nd-cumulant accepted at endpoint' status.

**LIFT RETRACTED 2026-06-08** (self-caught error; scscope_joint_correction.py 5/5; negative-results AUDIT-2026-06-08-scscope-lift-overclaim): the preceding 'LIFTED' annotation is WITHDRAWN. The floor-sharpening lift used the joint-PAIRING formula paired=rho/(1+max[R_s+R_q])=rho/2.872, whose linear-in-rho scaling is a LOCAL approximation at rho=2.6 only. The physically-correct ADDITIVE bookkeeping (scscope_joint_endpoint: the sunset is an absolute third-cumulant cost C_sunset=composed/1.13) SATURATES at x1.13 and gives only x0.945 (conservative K_floor<=T') .. x1.026 (verified K_floor<=0.52T') at the sharpened floor rho_lat -- MARGINAL, NOT a clean closure; the real threshold is rho>=9.85 (K_floor<=27), not 3.9. SC-SCOPE STAYS OPEN / remains a B1 named hypothesis; B1 active set RESTORED {H-LAYER} -> {H-LAYER, SC-SCOPE}, tier UNCHANGED T6. The PROVED floor sharpening (K_floor=sum_{t!=0}w_t^2/(lambda'I)^2 <= T'(M)) is a real PARTIAL advance: it moves the additive endpoint joint from x0.757 to x0.95-1.03, so the endpoint is now MARGINAL rather than clearly-failing -- a genuine step toward closure, but not closure. REALIZED QUARTIC (strong evidence, not certified) 2026-06-08 (scscope-floor-sharpening v1.6 5b, scscope_quartic_realized.py 4/4): under the canonical additive bookkeeping the endpoint closes at rho_lat=6.55 iff the quartic R_max<0.634 (the sunset is rigorous, caps the joint at x1.13). The prior R_max=1.019 inherited the Young-ceiling estimate R_sup=1.59. Computing R(t)=12(5v/2)^2 lam'^-2 Ghat4(t) 4(1-a0)/J(t) DIRECTLY gives R_max~0.385 << 0.634 -- the Young ceiling was loose by ~2.6x -- STRONG EVIDENCE the SC-SCOPE all-orders endpoint CLOSES. NOT certified: the absolute Ghat4 normalisation carries a factor-2/(2pi)^3 convention (the 'M'=-J(0) vs -J(0)/2' error class) that is load-bearing (survives +50% slack, not x2). The convolution SHAPE is rigorous; only the absolute normalisation is open. NO lift: SC-SCOPE stays a B1 named hypothesis, B1 T6 on {H-LAYER,SC-SCOPE}. Next: pin the Ghat4 convention to certify. CONVENTION PINNED / ENDPOINT CLOSURE CERTIFIED (thin) 2026-06-09 (scscope-quartic-normalisation-certificate v1.0, scscope_quartic_certificate.py 5/5): the factor-2/(2pi)^3 Ghat4 caveat is RESOLVED -- the Parseval identity (J*J)(0) [convolution] = (2pi^2)^-1 int q^2 J^2 holds to ratio 1.0000, so the convolution is standard-normalised. With Ghat4=G*G*G*G=J*J (exact) and Young consistency (ratio 0.27), R_max=0.385<0.634 is CERTIFIED (the Young estimate 1.019 was loose by ~2.6x). Under the CONSERVATIVE additive bookkeeping the certified joint = x1.040 (conservative K_floor=T'=n_pack, rho_lat=6.55) .. x1.082 (verified K_floor=0.52T', rho_lat=12.6) > 1 -- the SC-SCOPE all-orders endpoint CLOSES. The certified quartic flips the prior x0.945 (loose R_max=1.019). CLOSURE IS THIN (x1.04 worst case; sunset-binding). NO lift enacted: presented for OPERATOR RE-EXAMINATION per the standing instruction. B1 T6 on {H-LAYER, SC-SCOPE} unchanged.

**OPERATOR DECISION 2026-06-09**: HOLD the lift. The certified (thin x1.04) closure is RETAINED as the record (R-029 + scscope-quartic-normalisation-certificate v1.0), but the lift is NOT enacted -- the thin margin does not warrant flipping the gate. SC-SCOPE STAYS a B1 named hypothesis; B1 T6 on {H-LAYER, SC-SCOPE} unchanged. Re-open if the margin is hardened (real-shell T'<n_pack giving rho_lat>6.55, or a tighter sunset accounting).

**LIFTED@THIN-CERTIFIED 2026-06-09** (operator-authorised after re-examination; supersedes the same-day HOLD; scscope_endpoint_sweep.py 4/4): the convention is PINNED (Parseval ratio 1.0000) so R_max=0.385<0.634 is CERTIFIED, and the CORRECTED additive joint = x1.040-x1.082>1 -- the all-orders endpoint CLOSES. The thinness is STRUCTURAL, not an artefact: the joint SATURATES at x1.13 (sunset cap) as rho->inf, and the closure is SIGN-STABLE -- across I the endpoint I=2e-3 is the thinnest with the critical I~2.5e-3 BEYOND it (joint x1.126/x1.104/x1.040 at 4e-4/1e-3/2e-3), and across mu^2 [x0.5,x2] the worst is x1.034. A near-critical selection boundary. SC-SCOPE is LIFTED: B1 {H-LAYER,SC-SCOPE}->{H-LAYER}, tier UNCHANGED T6. Ledger flag LIFTED@THIN-CERTIFIED. B1 now rests on H-LAYER alone.

<a id="h-a0"></a>
### **H-A0**

**Statement:** Transcribed from Math437 v1.2 §Hypotheses (slimmed in v1.1): the $A=0$ uniqueness and zero-at-gap structure are certified numerically on a consistent quadrature scheme (internal convergence $3.1\times10^{-5}$; the $5.5\times10^{-3}$ scheme-gap offset is a recorded measure-convention systematic). PENALTY constants do **not** rest on this hypothesis: Lemma 3's $P_B$ floors are quadrature-free closed forms at the production anchors ($M_R=0.109414>M_c$, $4.1\times$ margin).

**Discharge path:** **REPLACED 2026-06-06** by H-ANCHOR + G-A0-DUI via the sign-decomposition theorem (ha0_sign_decomposition.py 14/14): uniqueness/zero-at-gap DERIVED from L1/L2/L3 closed forms + the anchor inequality; quadrature-scheme dependence + 5.5e-3 systematic exit the chain. Original path: quadrature-scheme unification or analytic $A=0$ proof.

<a id="h-suppression"></a>
### **H-SUPPRESSION**

**Statement:** Suppression hypothesis of the kinematic-Lorentz theorem (legacy PC-3C form).

**Discharge path:** H-SUPPRESSION-DISCHARGE

<a id="h-legacy-chain"></a>
### **H-LEGACY-CHAIN**

**Statement:** The cited legacy evidence chain is sound as recorded; TSv2 re-validation pending (migration plan M1/M2). Carried by every legacy-translated T6 entry until its pointers are migration-clean.

**Discharge path:** `governance/migration-plan.md` M2

<a id="h-cp2-bundle-data"></a>
### **H-CP2-BUNDLE-DATA**

**Statement:** The three-patch Čech bundle data on $\mathbb{CP}^2$ as constructed in legacy Math162/Math167.

**Discharge path:** Migration (plan phase M1) + re-verification of cocycle closure


<a id="a2-h1-kernel-positivity"></a>
### **A2-H1-KERNEL-POSITIVITY**

**Statement:** $Y>0$ and $\mu^2>0$ in the production kernel $K(q)=\mu^2+Y(q^2-q_0^2)^2$ (A1-KERNEL-CONV). $Y>0$ gives the fourth-order ellipticity / $q^{-4}$ decay; then $\lambda_0:=\min_k K(k)\ge\mu^2>0$, so $L=K(-i\nabla)$ is a positive self-adjoint fourth-order operator, hence sectorial and the generator of an analytic semigroup. This is the standing hypothesis for A2 LOCAL well-posedness (analytic-semigroup machinery) and for the $H^2$ a priori bound.

**Discharge path:** SATISFIED@anchor (textbook sectoriality hypothesis; $\mu^2=5\times10^{-3}>0$ at the production point; verified \texttt{spec\_inf\_equals\_mu2\_positive} in codes/foundations/a2_wellposedness_checks.py). Carried as a named hypothesis of A2 (T6).

<a id="a2-h2-sextic-coercivity"></a>
### **A2-H2-SEXTIC-COERCIVITY**

**Statement:** $\gamma>0$ (sextic stabiliser). Then by Young $\tfrac{|\lambda|}{4}t^4\le\tfrac{\gamma}{12}t^6+C_*$ with explicit $C_*$, so $F_{\rm TECT}$ is bounded below and coercive in $H^2\cap L^6$; combined with energy dissipation this gives the global a priori bound. Standing hypothesis for A2 GLOBAL existence (local existence does not need it).

**Discharge path:** SATISFIED@anchor (textbook coercivity hypothesis; $\gamma=1.62>0$, $C_*=1.01\times10^{-2}$; verified \texttt{sextic\_dominates\_quartic\_coercive}). If $\gamma\le0$ the functional is unbounded below and global existence is not claimed. Carried as a named hypothesis of A2 (T6).


<a id="c6-bcc-premise-blocked"></a>
### **C6-BCC-PREMISE-BLOCKED**

**Statement:** C6-SPACETIME-SIGNATURE previously depended on B3-BCC-STRUCT for a physical BCC-structure premise. B3-BCC-STRUCT is REFUTED/RETIRED (R-2026-06-23-b3-bcc-structural-selection); its only survivor B3-RH-TESTED-STRUCTURE-RANKING supplies a restricted relative ranking within the tested ensemble, which does NOT supply a BCC-structure premise. C6 therefore has no valid structural input.

**Discharge path:** BLOCKED -- operator review required (2026-06-23). To unblock, a physical BCC structure must be re-established (F[Psi_min]<F[0], lambda_min^perp>=0 symmetry-projected, N->inf on the canonical PDE background); only then may C6 depend on it.


<a id="a3-h1-dim3-q4-kernel"></a>
### **A3-H1-DIM3-Q4-KERNEL**

**Statement:** spatial dimension $d=3$ with the quartic kernel $K(q)=\mu^2+Y(q^2-q_0^2)^2$, $Y>0$ (propagator $\sim q^{-4}$; $Y>0$ is required for the $q^{-4}$ decay). Then the superficial degree of divergence is $D=(d-4)I-dV+d=3-3V-I<0$ for every connected diagram with $V\ge1,I\ge1$ (super-renormalisability). Standing hypothesis for A3 UV-finiteness.

**Discharge path:** SATISFIED (TECT is a $d=3$ theory with the A1 quartic kernel; $d=4$ would be only marginal). Carried as a named hypothesis of A3 (T6).

<a id="a3-h2-ir-positivity"></a>
### **A3-H2-IR-POSITIVITY**

**Statement:** $\mu^2>0$, so $K(q)\ge\mu^2>0$ and $G(q)=1/K\le1/\mu^2$ is bounded -- no infrared divergence (the shell $|q|=q_0$ is a finite enhancement). Standing hypothesis for A3 IR finiteness. Same underlying condition as A2-H1-KERNEL-POSITIVITY.

**Discharge path:** SATISFIED@anchor ($\mu^2=5\times10^{-3}>0$; verified \texttt{no\_ir\_divergence\_mu2\_positive}). Carried as a named hypothesis of A3 (T6).


<a id="a3-graphwise-convergence"></a>
### **A3-GRAPHWISE-CONVERGENCE**

**Statement:** For the perturbative measure $d\nu_{\Lambda,a}=Z^{-1}e^{-F_{\Lambda,a}}D\phi$, every connected amplitude must converge graphwise: $\lim_{a\to0}\mathcal A_{\mathcal G,a}(p_1,\ldots,p_n)=\mathcal A_{\mathcal G}(p_1,\ldots,p_n)$, via dominated convergence (lattice-propagator pointwise convergence + uniform $q^{-4}$ UV bound + Weinberg uniform integrability), with a defined regulator family $K_a$ matching the Brillouin-zone cutoff to the continuum kernel.

**Discharge path:** PROVED 2026-06-23 via the SPECTRAL/Galerkin regulator G_a=1_{|q|<=pi/a}/K (Route A; v1.3 -- the v1.1/v1.2 finite-difference-lattice domination was refuted by aliasing/folding). Genuine lattice (Reisz power counting) = Route B, OPEN. Operator T6 RATIFIED 2026-06-23 (spectral/fixed-p scope). Genuine finite-difference lattice = Route B (Reisz), OPEN refinement. Originally via the lattice regulator $\hat q_j=\tfrac2a\sin\tfrac{aq_j}2$ + dominated convergence (pointwise $G_a\to G$ + uniform $(1+|q|)^{-4}$ bound from $|\hat q|\ge\tfrac2\pi|q|$ on BZ + Weinberg integrability), with $\Lambda=\pi/a$ tying $a\to0\equiv\Lambda\to\infty$ (claims/A3-PERTURBATIVE-CONTINUUM-CORRELATORS/notes/a3-graphwise-convergence-lemma-260623-260623-v1.1.tex.txt; codes/foundations/a3_graphwise_convergence_checks.py 7/7). A3-PERTURBATIVE-CONTINUUM-CORRELATORS -> T6.

## Gate lifecycle

OPEN → CLOSED (with closing evidence + date) or RETIRED (statement absorbed
elsewhere; pointer mandatory). Closing a gate never silently promotes a claim;
promotions follow `governance/claim-standard.md` §5.

## History

- 2026-06-07: ROBUSTNESS-MU2 CLOSED@[x0.5,x2]-2ND-CUMULANT per operator authorization (reviews/2026-06-07-robustness-close-authorization-review.md). Closure bar met by robustness-mu2-margin-recompute v1.1 (9/9): exact m(mu^2)=PB(M_+)-DIP_BAND recomputed across [x0.5,x2], min 0.945 m_anchor; derivative-sign monotonicity certificate (min at mu^2=0.0025); full-grid J_eff envelope <0.01%; worst STEP-5B ratio x2.41. Scope: second-cumulant order, three certified intensities. Removed from B1 open_gates.

- 2026-06-07: M-ENDPOINT RESOLVED per operator authorization (same review). M(0.33675)=0.104953 by direct quadrature (cross-check 0.61%, tail bound 8.4e-4); sunset axis positive at sign level (x1.13). SC-SCOPE stays OPEN on GHAT4-PERTRANSFER + R-U6-1.

- 2026-06-06: ROBUSTNESS-MU2 set to OPEN (FINAL) per the explicit operator review; the earlier scoped-closure/closed wordings are WITHDRAWN; the gate carries numerically-supported off-anchor advance only (m(mu^2) not recomputed).

- 2026-06-06: ROBUSTNESS-MU2 reconciled to SCOPED CLOSURE CLOSED@[x0.5,x2]-2ND-CUMULANT per the operator robustness review (more specific than the H-A0-docs 'OPEN'); mandatory qualifier: m(mu^2) bounded-not-recomputed, second-cumulant scope only.

- 2026-06-06: ROBUSTNESS-MU2 RE-OPENED per operator adversarial review of the H-A0 documents (the [x0.5,x2] closure rested on a bounded-not-recomputed m(mu^2); reclassified to numerically-supported ADVANCE). Official status OPEN.

- 2026-06-06: OPERATOR ADVERSARIAL REVIEW (reviews/2026-06-06-b5-adversarial-review.md) — tiers FROZEN; registered the SC-SCOPE lift inputs (M-ENDPOINT, GHAT3-Q0, GHAT4-PERTRANSFER, R-U6-1, R-U6-2) and DR2-SHARE; SC-SCOPE tightened to require all four lift inputs; B5 stays T5 PINNED-CLOSURE @ H-ADM-COH amended class.

- 2026-06-06: ROBUSTNESS-MU2 CLOSED for mu^2 in [x0.5,x2] (STEP-5B re-margin off-anchor 5/5; A=0 uniqueness robust x0.2..x10; Prop-A floor preserved). Removed from B1 open_gates.

- 2026-06-06: ROBUSTNESS-MU2 ADVANCED (not closed): A=0-uniqueness robust on x0.2..x10 mu^2 neighbourhood (structural lemmas + verified inequalities); STEP-5B off-anchor re-margin = narrowed residual.

- 2026-06-06: G-A0-DUI CLOSED (explicit dominated convergence, 23/23); H-ANCHOR demoted hypothesis -> verified anchor fact; B2 {H-LAYER,H-ANCHOR}->{H-LAYER}, B1 drops H-ANCHOR. Former H-A0 residual is now only ROBUSTNESS-MU2 (off-anchor).

- 2026-06-06: H-A0 REPLACED by H-ANCHOR + G-A0-DUI (sign-decomposition theorem, ha0_sign_decomposition.py 14/14, operator-authorized); B2/B1 hypothesis sets updated.

- 2026-06-06: registered **H-ADM-COH** and **SC-SCOPE** as named hypotheses for the B1 Reading-H class-wide T6-CONDITIONAL promotion (operator-authorized).

- 2026-06-05 — Registry created (bootstrap).
- 2026-06-05 — Migration batch 1 (plan phase M1): H-LAYER / H-A0 placeholder entries replaced by
  verbatim transcriptions from Math437 v1.2; STEP-5B and G1PP-3B-HEX source
  pointers resolved to `archive/legacy/` paths.
- 2026-06-05 — Archive per-tag reorganisation: source pointers updated to
  `archive/legacy/notes/<Tag>/` layout.
- 2026-06-05 — Migration batch 2: the H-LAYER justification chain and the
  estimator chain (Math427–432, Math434+AddA, Math436) migrated and
  re-validated (167/167); ESTIMATOR-UPGRADE source pointer resolved.
- 2026-06-05 — STEP-5B partial reduction registered (B5-BEYOND-LAYER-BOUND,
  T3): gate stays OPEN; closure reduced to named gaps G1 + G2.
- 2026-06-05 — G1 attack landed (B5 v1.1, T3->T4): closed-region theorem
  derived (n <= n_max(I)); residual narrowed to G1' (thin-spread) + G2;
  gate stays OPEN.
- 2026-06-05 — Operator review verdict: B1 migration PASS (batch-2 rows
  signed); B5 = "T4 valid reduction, not closure" (tier confirmed); v1.2
  consistency re-issue of the B5 note; STEP-5B remains OPEN.
- 2026-06-05 — closing sweep (B5 v1.6, script v1.4.4, 111/111): G2 bookkeeping
  CLOSED (Lemmas H/I/J); composite-glue l2 theorem validated; row route
  REFUTED with the provable constant (registered negative result; verify-loop
  catches #4/#5); residual reduced to G1''-M4 (E_4 moment) + G-DEC.
  STEP-5B remains OPEN.
- 2026-06-05 — OPERATOR REVIEW VERDICT #5: v1.6 = PASS as strengthened T4;
  STEP-5B not closed; Reading-H unchanged; two stale sentences flagged
  (repaired in v1.7).
- 2026-06-05 — P^2-REPRESENTATION THEOREM (B5 v1.7, script v1.5.0, 126/126):
  W = lam(P^2 - 2I Id) => D+W >= D_0 > 0 unconditional; spectral floor
  a_0 = 2*lam*I/r_hat n-free/pattern-free; G1''-M4 CLOSED BY STRUCTURE;
  N_max(I) enlarged x46 at anchor (746 vs 16). Residual = G1'''-AE corner
  (+ G-DEC sub-route). T5-candidacy flagged for operator. STEP-5B remains
  OPEN.
- 2026-06-05 — OPERATOR REVIEW VERDICT #6: v1.7 = PASS as major strengthened
  T4; section-4 Gershgorin-led statement flagged (rewritten in v1.8).
- 2026-06-05 — v1.8 (script v1.6.0, 132/132): position-space multiplication
  structure (floor pointwise; Nambu DISCHARGED); Parseval => G1'''-AE =
  discrete sphere L^4 (Stein-Tomas q=4 d=3); UNIVERSAL single-circle
  theorem K=14 SHARP (any amplitudes; equal-amplitude caveat removed);
  coaxial falsification probe bounded (10.7 at 2x32). STEP-5B remains OPEN
  on the multi-circle corner.
- 2026-06-05 — OPERATOR REVIEW VERDICT #7: v1.8 = PASS as major strengthened
  T4; footer/sec-6(alpha) stale spots flagged (repaired in v1.9).
- 2026-06-05 — v1.9 (script v1.7.1, 145/145): antipodal-carrier partition
  theorem (l1/l2 exact); nu* = mu_C identity; COAXIAL-CLASS CLOSURE
  (K <= 30 absolute; measured 9.4/10.7; suspected-hard class CLOSED);
  H-GEN(2) FALSIFIED honestly (10 ordered pairs observed; verify-loop
  catch #6 documented); G1'''-AE sharpened to the carrier-richness bound
  p_0. STEP-5B remains OPEN.
- 2026-06-05 — OPERATOR REVIEW VERDICT #8: v1.9 = PASS as major strengthened
  T4; audit requests (height-coincidence multiplicity; weighted coaxial).
- 2026-06-05 — v2.0 MAJOR re-issue (script v1.8.0, 155/155): coaxial lemma
  repaired with explicit H* (AP-height audit: H*=1, in-plane separation;
  K decreasing 9.25/8.75/8.54; weighted 8.31); RECTANGLE REFORMULATION;
  TRIPLE-COUNT theorem => R = O(n^{5/2}) UNCONDITIONAL; kappa-balanced
  sqrt(n) corollary upgrades the closed region to ~2.2e6/5.3e4/2.8e3 modes.
  Residual: extreme-n rich-carrier corner + first-principles c_R.
  STEP-5B remains OPEN.
- 2026-06-05 — OPERATOR REVIEW VERDICT #9: v2.0 = PASS as major strengthened
  T4; operator SUPPLIED the theorem-grade c_R derivation (4 sqrt 14) and
  the Route-A/Route-B closure analysis — archived in the AddA note.
- 2026-06-05 — AddA note (rectangle-constant-closure-260605-v1.0, script
  v1.9.0, 166/166): operator derivation verified; NEW INCIDENCE ROUTE
  (stereographic transfer + planar rich-circle bounds): exponent 28/13,
  reach 7.9e16 modes at anchor; CONDITIONAL CLOSURE registered under named
  {H-KBAL, H-ADM}; sharp O(n^2) conjecture pre-registered (exponents
  2.04-2.08 measured). STEP-5B: closure now CONDITIONAL-ONLY — tier
  proposal (T5 / T6-conditional) submitted for operator review.
- 2026-06-05 — OPERATOR REVIEW VERDICT #10: AddA v1.0 = PARTIAL PASS;
  c_R = 4 sqrt(14) ACCEPTED theorem-grade; 28/13 exponent REJECTED
  (operator-caught arithmetic slip, catch #7; correct = 20/9).
- 2026-06-05 — AddA v1.1 (script v1.9.1, 167/167): exponent repaired to
  20/9 with dyadic self-check (ratio 1.1); 7.9e16 WITHDRAWN; incidence
  route demoted to PROVISIONAL (2.2e10, constant unpinned); ledger
  threshold = sqrt-n route (1.59e5); dichotomy program DR-1/DR-2
  registered (designated multi-turn route to sharp O(N^2)). B5 = T4+
  per verdict-#10 ledger. STEP-5B remains OPEN.
- 2026-06-05 — OPERATOR REVIEW VERDICT #11: AddA v1.1 = PASS as repaired
  T4+ support; three stale spots flagged (repaired in v1.2).
- 2026-06-05 — AddA v1.2 (script v1.10.0, 170/170): H-KBAL LIFT theorem —
  unconditional amplitudes at 64 sqrt(7) sqrt(n) log^2 cost; kappa-balance
  no longer load-bearing (verified: worst unbalanced ratio 0.03 vs ceiling
  2929); ledger threshold unchanged. Residual = {H-ADM} + DR-2 (sharp
  route) + constant-sharpening follow-ups. STEP-5B remains OPEN.
- 2026-06-05 — AddB (coherence-admissibility-cutoff-260605-v1.0, script
  v1.11.0, 175/175): H-ADM DERIVED from microphysics — xi = 2.44,
  theta_min = 0.603 rad, n_adm ~ 35 (x4: 140), nearly I-independent;
  K(4 n_adm) = 184 < budget at ALL anchor intensities (x32.4/x5.1/x1.2;
  I=2e-3 thin). T3 PROOF SKETCH + proposed class amendment H-ADM-COH —
  STEP-5B is CLOSURE-READY pending operator sign-off (or DR-2). Suite
  vectorized to 24.5 s. Commit-watcher infrastructure added (operator
  directive).
- 2026-06-05 — OPERATOR REVIEW VERDICT #12: AddA v1.2 PASS (T4+); AddB =
  T3 amendment proposal; directed: indistinguishability lemma (AddC) /
  DR-2 review.
- 2026-06-05 — AddC (coherence-indistinguishability-lemma-260605-v1.0,
  script v1.12.0, 185/185): EXACT splitting fibers 6/9/(12-6/n) I^2 —
  fragmentation gain SATURATES; |F[P']-F[P]| <= c_ind I^2 = margin/x898/
  x139/x33 — sub-resolution restructuring ENERGY-FAITHFUL; H-ADM-COH
  upgraded proposal -> DERIVED quotient statement; de-thinned closure
  margins x55.6/x8.8/x2.1 (thin corner repaired). AddA v1.3 stale fixes.
  STEP-5B: awaiting operator sign-off on the lemma-backed amendment.
- 2026-06-05 — OPERATOR REVIEW VERDICT #13: AddA v1.3 PASS; AddC PASS (T4);
  operator DIRECTED the AddD adoption note with its core statement.
- 2026-06-05 — AddD (hadmcoh-adoption-step5b-closure-260605-v1.0, script
  v1.13.1, 189/189): adoption record (scope-fenced) + CROSS-READING LEMMA
  (verdict-#13 condition (b): whole-pattern splitting Delta E = +0.67/
  +0.40 I^2, an order below the 6 I^2 budget; catch #8 self-caught: draft
  l1 assert contradicted Lemma C' and was replaced by exact identity
  checks) + assembled closure theorem (margins x55.6/x8.8/x2.1).
  STATUS: DRAFT-CLOSED — gate-row flip + B5 tier action (T5 candidate)
  await OPERATOR VERDICT #14.
- 2026-06-05 — OPERATOR VERDICT #14 DELIVERED (verbatim text supplied in
  the review): H-ADM-COH accepted; AddD passes as the closure record;
  GATE ROW FLIPPED to CLOSED-CONDITIONAL (margins x55.6/x8.8/x2.1);
  B5 promoted T4+ -> T5-CANDIDATE; unrestricted class stays OPEN via
  DR-2; polish items: c_cross analytic pin, endpoint hardening.
- 2026-06-05 — DR-2 seed lemma registered (one-line pigeonhole): if
  sum_C p_C^2 >= K N^2 with sum_C p_C <= N^2 then max_C p_C >= K — energy
  K N^2 forces a single circle with >= K antipodal pairs; combined with
  the universal single-circle theorem (K=14 sharp) and mu_C = nu*, this
  yields K <= c*min(mu_C, sqrt(n) polylog) as the elementary-method
  ceiling. Full DR-2 (unconditional O(N^2)) assessed RESEARCH-GRADE
  (adjacent to the open circle-incidence conjecture); registered as the
  publication-strength alternative, NOT on the critical path.
- 2026-06-05 — AddE (cross-pin-endpoint-hardening-260605-v1.0, script
  v1.14.0, 192/192): BOTH verdict-#14 polish items CLOSED. (a) c_cross
  ANALYTIC PIN: exact recombination forces co-circularity; curvature
  splits all other alignments (adversarial audit: exact multiplicity 2);
  co-circular absorbed by the universal K=14 (control: 12.20 = 14-18/10
  exact, zero slack) => c_total <= 20 I^2 DEPTH-FREE. (b) ENDPOINT
  HARDENING: amended-class minimum transfer gives J_eff = 0.256/0.226;
  closure margins lifted to x59.4 / x2.6 FLOORS (criterion band tops
  x290.9 / x12.7). No unpinned constant remains in the closure path.
  Next mainline: Reading-H T6 discussion.
- 2026-06-05 — Second operator verdict: B2 migration v1.3 PASS (batch-1 rows
  signed); G1' attack directed. B5 v1.3: Lemma E additive-energy split +
  transversal n-free corollary; residual restructured to G1''(row) + G1'b +
  G1''(glue) + G2; gate stays OPEN.
- 2026-06-05 — Third operator verdict (v1.3 strengthened-T4 PASS; footer flag).
  v1.4: G1''(ring) CLOSED for the canonical family (exact closed forms,
  five-orbit proof); footer repaired; residual = G1''(row) + G1''(glue) + G2;
  gate stays OPEN.
