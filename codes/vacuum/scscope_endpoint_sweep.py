"""scscope_endpoint_sweep.py -- is the THIN-CERTIFIED SC-SCOPE endpoint closure
STRUCTURAL (near-critical) or an accident? Operator points 4-5: nearby-parameter
sign stability + a structural explanation of the thinness.

Findings (certified R_max=0.385, sunset x1.13, conservative floor K_floor<=T'<=n_pack):
  * I-sweep (mu^2=0.005): joint rises as I falls (x1.126 @4e-4 -> x1.040 @2e-3 ->
    x1.000 @2.5e-3). The certified endpoint I=2e-3 is the thinnest WITHIN the
    certified band and is positively closed; the critical boundary is at
    I~2.5e-3, BEYOND it.
  * mu^2-sweep at the endpoint ([x0.5,x2], ROBUSTNESS-MU2 band): joint stays
    x1.034-x1.051 > 1 -- sign-stable.
  * Structural: joint(rho) SATURATES at x1.13 (the sunset cap) as rho->inf. The
    thinness is a genuine sunset-limited near-critical balance, NOT a numerical
    artefact: no floor sharpening can exceed x1.13, and the endpoint sits at
    x1.04 just below it.
self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-09"
__claims__ = ["B5-BEYOND-LAYER-BOUND", "B1-RH-ENUM"]
import json, sys, math
from pathlib import Path
import numpy as np
REPO=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(REPO/"codes"/"vacuum")); sys.path.insert(0,str(REPO/"archive"/"legacy"/"scripts"))
import sectorb_common as sb, Math424_AddA_reading_uniqueness as m424
U,V,Q0,C=sb.U,sb.V,sb.Q0,sb.C; SUNSET=1.13; RMAX=0.385
CLAIMS=[]
def claim(n,c,d=""): CLAIMS.append(dict(name=n,passed=bool(c),detail=d)); print(f"  [{'PASS' if c else 'FAIL'}] {n} {d}")
def joint(mu2,I,Rmax=RMAX):
    rR=m424.gap_solve(mu2,0,0,0.0); M_R=m424.M_fast(rR); lam=3*U+30*V*M_R
    rhat=rR+2*lam*I; a0=2*lam*I/rhat; MARGIN=sb.margin_of(mu2)["margin"]
    theta=math.sqrt(rhat)/(2*Q0**2*math.sqrt(C)); n_pack=16/theta**2
    Jeff=sb.J_of_t(2*Q0*math.sin(theta/2),rhat,nk=600,nmu=400)
    rho=4*(1-a0)*MARGIN/((lam*I)**2*Jeff)/n_pack
    C2=MARGIN/rho; composed=MARGIN*(1-1/rho); return MARGIN/(C2+composed/SUNSET+Rmax*C2), rho
Iend=2e-3
jI={I:joint(0.005,I)[0] for I in [4e-4,1e-3,1.5e-3,Iend]}
claim("I_band_positive_endpoint_thinnest", all(j>1 for j in jI.values()) and jI[Iend]==min(jI.values()),
      f"(joint>1 across I in [4e-4,2e-3] and the endpoint I=2e-3 is the thinnest: "
      f"{ {f'{I:.0e}':round(j,3) for I,j in jI.items()} }; the certified band is positively closed, binding at the endpoint)")
jmu={mu2:joint(mu2,Iend)[0] for mu2 in [0.0025,0.00354,0.005,0.00707,0.01]}
claim("mu2_band_sign_stable", min(jmu.values())>1.0,
      f"(joint>1 across mu^2 in [x0.5,x2] at the endpoint; worst x{min(jmu.values()):.3f} -- sign-stable, "
      "consistent with ROBUSTNESS-MU2)")
# structural saturation
MARGIN=sb.margin_of(0.005)["margin"]
def joint_rho(rho): C2=MARGIN/rho; composed=MARGIN*(1-1/rho); return MARGIN/(C2+composed/SUNSET+RMAX*C2)
sat=joint_rho(1e7)
claim("structural_sunset_saturation", abs(sat-1/(1/SUNSET+RMAX*0))<0.01 and joint_rho(100)>1.12 and sat<1.14,
      f"(joint(rho) saturates at x{sat:.3f} (=1/(1/1.13)) as rho->inf: the SUNSET caps the joint -- the thinness "
      "is a genuine near-critical balance, not a numerical artefact; no floor sharpening can exceed x1.13)")
claim("endpoint_below_critical_I", joint(0.005,2.5e-3)[0] <= 1.0 + 0.01,
      f"(the critical I (joint=1) is ~2.5e-3 > the certified endpoint 2e-3: joint(2.5e-3)=x{joint(0.005,2.5e-3)[0]:.3f}; "
      "the endpoint sits inside the closed region, near the structural boundary)")
ok=all(c["passed"] for c in CLAIMS)
out=REPO/"claims"/"B5-BEYOND-LAYER-BOUND"/"runs"/"260609-scscope-endpoint-sweep"
out.mkdir(parents=True,exist_ok=True)
(out/"result.json").write_text(json.dumps(dict(script="scscope_endpoint_sweep.py",version=__version__,
    I_sweep={f"{I:.1e}":j for I,j in jI.items()},mu2_sweep={f"{m:.5f}":j for m,j in jmu.items()},
    saturation=sat,critical_I_approx=2.5e-3,claims=CLAIMS,all_pass=ok),indent=2))
print(f"\nstructural: joint sunset-saturates at x{sat:.3f}; endpoint x{jI[Iend]:.3f}; mu^2-band worst x{min(jmu.values()):.3f}")
print(f"claims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
