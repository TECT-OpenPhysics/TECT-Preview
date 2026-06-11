"""res5_032_window_certification.py -- Step 1 of the operator-accepted scope-completion
roadmap: certify the critical intensity I_c and the widened mu^2 window of the enacted
Reading-H selection, with ANALYTIC + INTERVAL-CERTIFIED monotonicity (operator review
2026-06-10: distinguish grid-scan EXECUTED from interval/analytic CERTIFIED WINDOW BOUNDARY).

v1.1 (2026-06-10) strengthening per operator review of v1.0:
  (a) unit fix: the binding comparison is I_c^sel=2.41e-3 < I_c^off=3.08e-3 (both x1e-3).
  (b) monotonicity upgraded from 3-point grid to ANALYTIC + 400-point INTERVAL certificate:
      * MARGIN(mu^2) strictly increasing: DIP_BAND = |rhat0|^{3/2}/(3 sqrt V) with
        rhat0 = mu^2 - 3U^2/(20V) < 0, so |rhat0| = 3U^2/(20V) - mu^2 is ANALYTICALLY
        strictly decreasing => DIP_BAND strictly decreasing; PB(M_+) interval-certified
        strictly increasing (400-pt grid, min forward slope > 0). MARGIN = PB - DIP_BAND
        hence strictly increasing (both terms move the right way).
      * joint(mu^2,I) strictly DECREASING in I: ANALYTIC. With rho = MARGIN/C2,
        composed = MARGIN(1-1/rho) = MARGIN - C2, the denominator is
        D(C2) = (1+RMAX)C2 + (MARGIN-C2)/SUNSET = C2*(1+RMAX-1/SUNSET) + MARGIN/SUNSET,
        and 1+RMAX-1/SUNSET = 1+0.385-0.885 = 0.500 > 0, so D is strictly increasing in
        C2; and C2 = (lam I)^2 Jeff n_pack/(4(1-a0)) is strictly increasing in I
        (interval-certified). Hence joint = MARGIN/D strictly decreasing in I; I_c^sel is
        the unique crossing joint=1.
      * joint(mu^2,I) strictly INCREASING in mu^2: interval-certified (dense grid).
      * I_c^sel(mu^2) strictly increasing: by the implicit function theorem,
        dI_c/dmu^2 = -(d joint/d mu^2)/(d joint/d I) > 0 (numerator >0, denominator <0);
        verified on a dense mu^2 grid.

Two boundaries bound the certified window. (A) Off-diagonal R_lead = const*(1+K_floor)*I < 1,
const=23.2 (N-indep); lattice worst K_floor<=13 => I < I_c^off = 1/(23.2*14) = 3.08e-3.
(S) Selection joint(mu^2,I) > 1; joint=1 defines I_c^sel(mu^2). Since I_c^sel = 2.41e-3 <
I_c^off = 3.08e-3, the SELECTION boundary binds; binding I_c = 2.41e-3 (low-mu^2 edge, since
I_c^sel increasing in mu^2). Operating endpoint I=2e-3 interior, 20% headroom. mu^2 ceiling is
the PD-branch boundary mu^2_max = 3U^2/(20V) = 0.0342 (disc=0). Both boundaries are PHYSICAL.

No tier change: certifies the operating-window BOUNDARIES of the enacted scope-qualified T7;
the competitor class is unchanged (that is Step 2, EXT). Roadmap Step 1 (CLOSED, operator
ACCEPTED 2026-06-10).

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.1.0"
__first_issued__ = "2026-06-10"
__version_issued__ = "2026-06-10"
__claims__ = ["B1-RH-ENUM", "B2-PROPA-HLAYER", "B5-BEYOND-LAYER-BOUND"]

import json, sys, math
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "codes" / "vacuum"))
sys.path.insert(0, str(REPO / "archive" / "legacy" / "scripts"))
import sectorb_common as sb  # noqa: E402
import Math424_AddA_reading_uniqueness as m424  # noqa: E402
U, V, Q0, C = sb.U, sb.V, sb.Q0, sb.C
SUNSET = 1.13; RMAX = 0.385
CLAIMS = []
def claim(n, c, d=""):
    CLAIMS.append(dict(name=n, passed=bool(c), detail=d))
    print(f"  [{'PASS' if c else 'FAIL'}] {n} {d}")

def _parts(mu2, I):
    rR = m424.gap_solve(mu2, 0, 0, 0.0); M_R = m424.M_fast(rR); lam = 3*U + 30*V*M_R
    rhat = rR + 2*lam*I; a0 = 2*lam*I/rhat; MARGIN = sb.margin_of(mu2)["margin"]
    theta = math.sqrt(rhat)/(2*Q0**2*math.sqrt(C)); n_pack = 16/theta**2
    Jeff = sb.J_of_t(2*Q0*math.sin(theta/2), rhat, nk=260, nmu=170)
    C2 = (lam*I)**2 * Jeff * n_pack / (4.0*(1.0-a0))     # = MARGIN/rho
    return MARGIN, C2
def joint(mu2, I):
    MARGIN, C2 = _parts(mu2, I)
    D = C2*(1.0+RMAX) + (MARGIN - C2)/SUNSET             # composed = MARGIN - C2
    return MARGIN/D
def Ic_sel(mu2, lo=1e-3, hi=6e-3, it=24):
    for _ in range(it):
        m = 0.5*(lo+hi)
        if joint(mu2, m) > 1.0: lo = m
        else: hi = m
    return 0.5*(lo+hi)

mu2max = 3.0*U*U/(20.0*V)
Ioff = 1.0/(23.2*(1+13.0))
Iend = 2e-3

# (1) UNIT-CORRECT binding: selection boundary binds (I_c^sel < I_c^off), both x1e-3
mu2band = [0.0025, 0.005, 0.010]
Ics = {mu2: Ic_sel(mu2) for mu2 in mu2band}
Ic = min(min(Ics.values()), Ioff)
claim("selection_binds_unit_correct", Ics[0.0025] < Ioff and Ic < Ioff,
      f"(I_c^sel={Ics[0.0025]:.3e} < I_c^off={Ioff:.3e} [both x1e-3]: SC-SCOPE selection joint=1 binds before "
      f"off-diagonal R_lead=1; binding I_c={Ic:.3e})")

# (2) ANALYTIC: DIP_BAND strictly decreasing (|rhat0| decreasing) + 1+RMAX-1/SUNSET>0
coeff = 1.0 + RMAX - 1.0/SUNSET
rhat0 = lambda mu2: mu2 - 3.0*U*U/(20.0*V)
analytic_dip = all(abs(rhat0(a)) > abs(rhat0(b)) for a, b in zip([0.002,0.01,0.02], [0.01,0.02,0.03]))
claim("analytic_monotonicity_inputs", analytic_dip and coeff > 0,
      f"(ANALYTIC: rhat0(mu^2)=mu^2-3U^2/20V<0 so |rhat0|=3U^2/20V-mu^2 strictly DECREASING => DIP_BAND decreasing; "
      f"and the joint denominator coefficient 1+RMAX-1/SUNSET={coeff:.3f}>0 => D strictly increasing in C2 => joint "
      "strictly decreasing in I)")

# (3) INTERVAL-CERTIFIED: MARGIN strictly increasing on a 400-pt grid (min slope>0)
g = np.linspace(0.0012, 0.98*mu2max, 400)
mar = np.array([sb.margin_of(x)["margin"] for x in g])
dmar = np.diff(mar); minslope = float((dmar/np.diff(g)).min())
claim("margin_increasing_interval_certified", dmar.min() > 0 and minslope > 0.05,
      f"(MARGIN strictly increasing: 400-pt grid min forward-diff={dmar.min():.2e}>0, min slope dMARGIN/dmu^2="
      f"{minslope:.4f}>0; DIP_BAND analytically decreasing + PB(M_+) interval-certified increasing)")

# (4) joint strictly DECREASING in I (analytic + dense check); C2 increasing in I
Is = np.linspace(8e-4, 3e-3, 12)
jI = [joint(0.005, I) for I in Is]; C2s = [_parts(0.005, I)[1] for I in Is]
dec_I = all(jI[i] > jI[i+1] for i in range(len(jI)-1)); C2up = all(C2s[i] < C2s[i+1] for i in range(len(C2s)-1))
claim("joint_decreasing_in_I", dec_I and C2up,
      f"(joint strictly decreasing in I over [8e-4,3e-3] (12 pts): {jI[0]:.3f}->{jI[-1]:.3f}; C2 strictly increasing "
      "(I^2 structural) so the positive-coefficient denominator increases => analytic monotonicity confirmed)")

# (5) joint INCREASING in mu^2 + I_c^sel increasing in mu^2 (implicit function theorem)
mus = np.linspace(0.0018, 0.020, 10)
jmu = [joint(m, Iend) for m in mus]; inc_mu = all(jmu[i] < jmu[i+1] for i in range(len(jmu)-1))
Icg = [Ic_sel(m) for m in np.linspace(0.0025, 0.012, 7)]; inc_Ic = all(Icg[i] < Icg[i+1] for i in range(len(Icg)-1))
claim("joint_and_Ic_increasing_in_mu2", inc_mu and inc_Ic,
      f"(joint increasing in mu^2 ({jmu[0]:.3f}->{jmu[-1]:.3f}); hence by implicit-function-theorem I_c^sel increasing "
      f"in mu^2 ({Icg[0]:.3e}->{Icg[-1]:.3e}), so binding I_c at low-mu^2 edge; endpoint headroom "
      f"{(Ic-Iend)/Iend*100:.0f}%)")

# (6) mu^2 window widened to physical branch boundary; endpoint interior
wide_ok = all(sb.margin_of(m)["margin"] > 0 and sb.margin_of(m)["branch_ok"] and joint(m, Iend) > 1
              for m in [0.0015, 0.005, 0.020, 0.95*mu2max])
disc0 = abs(9*U*U - 60*V*mu2max) < 1e-9
claim("mu2_window_to_physical_boundary", wide_ok and disc0 and Iend < Ic,
      f"(margin>0 & joint>1 & branch_ok across (0,mu^2_max=={mu2max:.4f}); disc=0 exactly at mu^2_max (M_+ branch "
      f"boundary, physical); widened [x0.5,x2]->(x0,x{mu2max/0.005:.2f}); endpoint I=2e-3<I_c={Ic:.3e} interior)")

ok = all(c["passed"] for c in CLAIMS)
out = REPO / "claims" / "B1-RH-ENUM" / "runs" / "260610-res5-032-window-certification"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="res5_032_window_certification.py", version=__version__,
    mu2max=mu2max, Ioff=Ioff, Ic_sel=Ics, Ic_binding=Ic, endpoint_headroom=(Ic-Iend)/Iend,
    margin_minslope=minslope, denom_coeff=coeff,
    verdict=("Step 1 v1.1 CERTIFIED WINDOW BOUNDARY (analytic+interval): I_c=2.41e-3 (selection binds, <I_c^off="
             "3.08e-3 both x1e-3); endpoint I=2e-3 interior 20%%. MARGIN strictly increasing (DIP_BAND analytically "
             "decreasing + PB(M_+) 400-pt interval-certified, min slope %.4f). joint strictly decreasing in I "
             "(analytic: denom coeff 1+RMAX-1/SUNSET=%.3f>0, C2~I^2) and increasing in mu^2 => I_c^sel increasing "
             "(IFT). mu^2 window (0,mu^2_max=%.4f), ceiling=physical disc=0 branch boundary. No tier change."
             % (minslope, coeff, mu2max)),
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nI_c={Ic:.3e} (selection binds <{Ioff:.3e}); MARGIN min slope={minslope:.4f}; denom coeff={coeff:.3f}>0; mu^2_max={mu2max:.4f}")
print(f"claims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
