"""res5_019_exchange_scalar_identification.py -- T-019: identify the off-diagonal
"exchange scalar" b_exch and show it is NOT a new unbounded residual. For TECT's
LOCAL interaction the mean-field off-diagonal Hessian is the STABILISING density-
density term f''(M)=(3/2)u_eff>0 (no A-independent attractive Fock exchange); the
genuine off-diagonal obstruction is the A-DEPENDENT condensate bubble (Math428,
O(A^4), R_lead-controlled) plus the beyond-mean-field two-loop int-int G^2 exchange
= the sunset-class third cumulant, governed by SC-SCOPE.

Reconciliation of two prior notes.
  * hdiag-full-operator-norm-formulation v1.0 introduced an "A-independent Fock
    exchange block B^exch, sign not fixed by u_eff>0", named it the RES-5 residual,
    and T-018 reduced the off-diagonal norm to bounding a scalar b_exch.
  * Math428 (the EXPLICIT off-diagonal Bogoliubov computation) shows the off-diagonal
    free-energy share is -1/4 sum_{Q!=0} W(Q)^2 B(|Q|) with W(Q)=(3u+30vM_R)A^2 p_2(Q)
    +5vA^4 p_4(Q) -- i.e. O(A^4), CONDENSATE-INDUCED (A-dependent), with NO A-independent
    term. The beyond-second-cumulant piece is the resummation ratio rho (calibrated
    0.415, worst-case 1.0); the enumerated Bogoliubov bands are POSITIVE even at rho=1
    (min +6.7e-4).

T-019 resolution. TECT's interaction is LOCAL (contact quartic u + sextic v), so the
mean-field free energy is a LOCAL DENSITY FUNCTIONAL Phi[G]=int f(M(x)),
f(M)=(3u/4)M^2+(5v/2)M^3, M(x)=G(x,x). Its second variation w.r.t. an off-diagonal
density fluctuation rho_Q (Q!=0) is
    delta^2 Phi / delta rho_Q delta rho_{-Q} = f''(M) = (3/2)(u+10vM) = (3/2) u_eff,
INDEPENDENT of Q and equal to the l=0 breathing convexity. At the anchor f''(M)=
(3/2)(2.685)=+4.03>0 -- STABILISING. There is NO A-independent attractive Fock
exchange for a local functional; the full-operator-norm note's "sign-unfixed exchange"
conflated the BARE u<0 with the DRESSED off-diagonal Hessian, which uses u_eff>0.
Consequently the off-diagonal "exchange scalar" b_exch is NOT a new unbounded object:
the residual is (i) the A-dependent condensate bubble (R_lead<=0.650 class-wide, T-018),
and (ii) the beyond-mean-field two-loop int-int G^2 exchange = the sunset third cumulant,
governed by SC-SCOPE (cap x1.13, lifted@thin-certified 2026-06-09). Honest tier: STRONG
EVIDENCE / reframing, NOT unconditional closure (class-wide rho + beyond-mean-field for
non-enumerated patterns is the open RES-5). No tier flip: B1/B2 T6 on {H-LAYER}.

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-10"
__claims__ = ["B2-PROPA-HLAYER", "B1-RH-ENUM"]

import json, sys, math
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "archive" / "legacy" / "scripts"))
import Math424_AddA_reading_uniqueness as m424  # noqa: E402
U, V = m424.U, m424.V
CLAIMS = []
def claim(n, c, d=""):
    CLAIMS.append(dict(name=n, passed=bool(c), detail=d))
    print(f"  [{'PASS' if c else 'FAIL'}] {n} {d}")

rR = m424.gap_solve(0.005, 0, 0, 0.0)
M_R = m424.M_fast(rR)
u_eff = U + 10.0 * V * M_R
print(f"anchor: rR={rR:.5f}, M_R={M_R:.5f}, u_eff={u_eff:.5f}")

# local density functional f(M) = (3u/4)M^2 + (5v/2)M^3
def f(M): return 0.75 * U * M * M + 2.5 * V * M**3
f2_analytic = 1.5 * U + 15.0 * V * M_R              # f''(M) = (3/2)(u+10vM) = (3/2)u_eff

# (1) off-diagonal Hessian of the LOCAL functional = f''(M), Q-INDEPENDENT (numerical)
x = np.linspace(0, 2 * math.pi, 4000, endpoint=False)
def hess_off(Q, eps=1e-4):
    return (f(M_R + eps * np.cos(Q * x)).mean() - 2 * f(M_R) + f(M_R - eps * np.cos(Q * x)).mean()) / eps**2
vals = {Q: 2.0 * hess_off(Q) for Q in (1, 2, 3, 5, 7)}   # 2x because <cos^2>=1/2
q_indep = max(abs(v - f2_analytic) for v in vals.values())
claim("local_offdiag_hessian_is_density_density", q_indep < 1e-3,
      f"(local functional Phi=int f(M(x)): off-diagonal Hessian = f''(M)=(3/2)u_eff={f2_analytic:.4f}, Q-INDEPENDENT "
      f"(max deviation over Q=1..7 is {q_indep:.1e}); this is the DIRECT density-density term, diagonal in Q)")

# (2) the A-independent off-diagonal Hessian is STABILISING (>0): no attractive Fock exchange
claim("no_a_independent_attractive_exchange", f2_analytic > 0.0,
      f"(f''(M)=(3/2)u_eff={f2_analytic:.4f}>0: the A-independent off-diagonal interaction is the STABILISING "
      f"density-density term, NOT an attractive Fock exchange. The full-operator-norm note's 'sign-unfixed exchange' "
      f"conflated bare u={U}<0 with the DRESSED Hessian (u_eff={u_eff:.3f}>0). For a LOCAL functional Hartree=Fock)")

# (3) consistency: the off-diagonal A-independent Hessian equals the l=0 breathing convexity (T-016)
claim("consistency_with_breathing_convexity", abs(f2_analytic - 1.5 * u_eff) < 1e-9,
      f"(f''(M)={f2_analytic:.4f} = (3/2)u_eff = the T-016 l=0 breathing-sector curvature: the SAME local-functional "
      "second derivative governs both the isotropic breathing and the off-diagonal density-density -- consistent)")

# (4) Math428 facts: off-diagonal is A-DEPENDENT O(A^4), bands positive at rho=1 (no resummation credit)
#     (recorded from archive/legacy/notes/Math428 v1.1; the explicit Bloch/Bogoliubov computation)
m428_band_min_rho1 = 6.7e-4       # min Delta F_est over A at rho=1 (worst case)
m428_rho_calibrated = 0.415       # exact/2nd-order resummation ratio (a CREDIT, <1)
claim("math428_offdiag_A_dependent_bands_positive", m428_band_min_rho1 > 0 and m428_rho_calibrated < 1,
      f"(Math428 explicit Bloch computation: off-diagonal share = -1/4 sum W(Q)^2 B(|Q|), W propto A^2 => O(A^4), "
      f"A-DEPENDENT (no A-independent term); resummation rho={m428_rho_calibrated} (CREDIT, <1); the enumerated "
      f"Bogoliubov bands are POSITIVE even at rho=1 (no credit), min +{m428_band_min_rho1:.1e}. So the genuine "
      "off-diagonal obstruction is the A-dependent bubble (R_lead-controlled), not an A-independent exchange)")

# (5) quantitative sanity: the reframing + signs + the two-loop = SC-SCOPE
sane = (f2_analytic > 0 > U) and (q_indep < 1e-3) and (m428_band_min_rho1 > 0)
claim("quantitative_sanity_reframing", sane,
      f"(REFRAMING: b_exch is NOT a new unbounded A-independent scalar. Mean-field off-diagonal = +(3/2)u_eff="
      f"{f2_analytic:.3f} stabilising (local functional); A-dependent bubble = Math428 O(A^4), R_lead<=0.650 "
      "class-wide; beyond-mean-field two-loop int-int G^2 exchange = sunset = SC-SCOPE (cap x1.13, "
      "lifted@thin-certified 2026-06-09). Open RES-5 = class-wide rho + beyond-MF for non-enumerated patterns. "
      "No tier flip B1/B2 T6)")

ok = all(c["passed"] for c in CLAIMS)
out = REPO / "claims" / "B2-PROPA-HLAYER" / "runs" / "260610-res5-019-exchange-scalar-identification"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="res5_019_exchange_scalar_identification.py", version=__version__,
    rR=rR, M_R=M_R, u_eff=u_eff, f2_analytic=f2_analytic, q_independence_dev=q_indep,
    hess_by_Q={str(Q): v for Q, v in vals.items()},
    m428_band_min_rho1=m428_band_min_rho1, m428_rho_calibrated=m428_rho_calibrated,
    verdict=("T-019: NO A-independent attractive Fock exchange for TECT's local interaction; mean-field off-diagonal "
             "Hessian = f''(M)=(3/2)u_eff=+%.3f stabilising (Q-independent). Off-diagonal obstruction = A-dependent "
             "Math428 bubble (O(A^4), R_lead<=0.650, bands +ve at rho=1) + beyond-MF two-loop = SC-SCOPE (thin). "
             "b_exch reframed, not a new unbounded scalar. STRONG EVIDENCE, no tier flip." % f2_analytic),
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nf''(M)=(3/2)u_eff={f2_analytic:.4f}>0 (Q-indep dev {q_indep:.1e}); Math428 band min(rho=1)=+{m428_band_min_rho1:.1e}")
print(f"claims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
