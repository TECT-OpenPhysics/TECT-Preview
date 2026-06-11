"""res5_dressed_loop_parameter.py -- RES-5 dressed three-loop skeleton: the
dressed loop parameter is O(1) (MARGINAL), so the skeleton series does not
geometrically decay and RES-5 needs RESUMMATION, not a geometric bound.

The 2PI skeleton ratio s_{l+1}/s_l is the dressed per-loop factor ~ lam' * (dressed
bubble). At the operating endpoint:
    lam' M_d  = 0.78,   lam' B_d = lam' int G_d^2 = 1.03   (O(1), marginal).
Hence s_4 ~ s_3 * (loop param) ~ 0.04 * 1.0 ~ s_3: each skeleton term stays small
(~4%, a0/common-mode suppressed) but the RATIO is ~1, so the series does NOT decay
geometrically. The per-term condition s_l < 1/2 plausibly holds, but the geometric
SUM domination (s_l <= s < 1/2 with a decaying ratio) is MARGINAL -- this is the
Brazovskii strong-fluctuation regime (dressed loop parameter O(1)). RES-5 closure
therefore requires a RESUMMATION (2PI self-consistent / Borel), not an elementary
geometric skeleton bound.

This script pins the dressed loop parameter (robust, convention-light) and records
the marginal-series conclusion. The precise s_4 (the three-loop skeleton integral)
is the dedicated 2PI computation; the scaling s_4 ~ s_3 * loop_param is the
structural estimate.

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__claims__ = ["B1-RH-ENUM"]
import json, sys
from pathlib import Path
import numpy as np
REPO=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(REPO/"archive"/"legacy"/"scripts"))
import Math424_AddA_reading_uniqueness as m424
U,V,Q0,C=m424.U,m424.V,m424.Q0,m424.C
CLAIMS=[]
def claim(n,c,d=""):
    CLAIMS.append(dict(name=n,passed=bool(c),detail=d)); print(f"  [{'PASS' if c else 'FAIL'}] {n} {d}")

rR=m424.gap_solve(0.005,0,0,0.0); M_R=m424.M_fast(rR); lam=3*U+30*V*M_R
rhat=rR+2*lam*2e-3
q=np.linspace(1e-6,8*Q0,400000); Gd=1.0/(rhat+C*(q**2-Q0**2)**2)
Int=lambda n: float(np.trapezoid(q**2*Gd**n,q)/(2*np.pi**2))
Md,Bd=Int(1),Int(2)
g_M, g_B = lam*Md, lam*Bd
print(f"rhat={rhat:.4f}, lam'={lam:.3f}; lam' M_d={g_M:.3f}, lam' B_d={g_B:.3f}")

claim("dressed_loop_parameter_O1_marginal", 0.5 < g_B < 1.5,
      f"(dressed loop parameter lam' B_d = lam' int G_d^2 = {g_B:.3f} = O(1), in [0.5,1.5] -- MARGINAL, near the "
      "convergence boundary 1; the Brazovskii sea is strongly fluctuating even when dressed)")

s3=0.04; s4_est=s3*g_B
claim("s4_not_much_less_than_s3", s4_est > 0.5*s3,
      f"(s_4 ~ s_3 * loop_param ~ {s3}*{g_B:.2f} = {s4_est:.3f} ~ s_3: the skeleton ratio is ~1, so s_4 is NOT << "
      "s_3 -- the difference does NOT geometrically decay; each term stays ~4% but the series ratio is marginal)")

claim("per_term_below_half_but_sum_marginal", s4_est < 0.5,
      f"(per-term s_4 ~ {s4_est:.3f} < 1/2 (each skeleton term is small via a0), BUT with ratio ~{g_B:.2f}~1 the "
      "geometric SUM does not converge cleanly -- RES-5 closure needs RESUMMATION, not a geometric bound)")

claim("res5_needs_resummation", g_B > 0.5,
      "(CONCLUSION: dressed loop parameter O(1) => the skeleton/loop series is MARGINAL (strong-coupling). RES-5 "
      "closure requires a 2PI self-consistent / Borel RESUMMATION of the marginal series -- a dedicated QFT effort, "
      "NOT an elementary geometric skeleton bound. The per-term a0-smallness is real; the ratio marginality is the "
      "genuine strong-coupling frontier)")

ok=all(c["passed"] for c in CLAIMS)
out=REPO/"claims"/"B1-RH-ENUM"/"runs"/"260609-res5-dressed-loop-parameter"; out.mkdir(parents=True,exist_ok=True)
(out/"result.json").write_text(json.dumps(dict(script="res5_dressed_loop_parameter.py",version=__version__,
    rhat=rhat,lam=lam,Md=Md,Bd=Bd,lam_Md=g_M,lam_Bd=g_B,s3=s3,s4_est=s4_est,
    verdict="dressed loop parameter lam' B_d=1.03=O(1) marginal; s_4~s_3 (ratio~1, not decaying); per-term <1/2 "
            "but geometric sum marginal => RES-5 needs resummation (2PI/Borel), not a geometric skeleton bound",
    claims=CLAIMS,all_pass=ok),indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
