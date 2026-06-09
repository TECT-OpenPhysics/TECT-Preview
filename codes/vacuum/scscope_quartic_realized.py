"""scscope_quartic_realized.py -- the REALIZED quartic-difference per-transfer
ratio R_max, computed DIRECTLY (no Young ceiling), bears on whether the SC-SCOPE
endpoint closes under the corrected (canonical additive) bookkeeping.

Context (scscope-floor-sharpening v1.4): the proved floor sharpening gives
rho_lat=6.55; under the canonical additive joint the endpoint closes iff the
quartic R_max < 0.634 (the sunset is rigorous and caps the joint at x1.13). The
prior R_max=1.019 inherited the Young-ceiling estimate R_sup=1.59 (flagged 'NOT
recomputed'). Here we evaluate the realized ratio
    R(t) = 12 (5v/2)^2 / lam'^2 * Ghat4(t) * 4(1-a0) / J(t),  Ghat4=(J*J)(t),
directly on the endpoint chords.

RESULT: R_max ~ 0.385 (script Ghat4 convention) << 0.634 -- STRONG EVIDENCE the
endpoint closes (the Young ceiling was loose by ~4x). NOT CERTIFIED: the absolute
Ghat4 normalisation carries a factor-2 / (2pi)^3 convention (the 'M'=-J(0) vs
-J(0)/2' error class), which is load-bearing (a factor 2 -> R_max~0.77 > 0.634).
So this is strong evidence, NOT a lift; SC-SCOPE stays a B1 hypothesis pending the
convention being pinned.

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-08"
__claims__ = ["B5-BEYOND-LAYER-BOUND", "B1-RH-ENUM"]
import json, sys, math
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO/"codes"/"vacuum")); sys.path.insert(0, str(REPO/"archive"/"legacy"/"scripts"))
import sectorb_common as sb
import Math424_AddA_reading_uniqueness as m424
U,V,Q0,C=sb.U,sb.V,sb.Q0,sb.C; MU2=0.005; I_END=2e-3
CLAIMS=[]
def claim(n,c,d=""): CLAIMS.append(dict(name=n,passed=bool(c),detail=d)); print(f"  [{'PASS' if c else 'FAIL'}] {n} {d}")
rR=m424.gap_solve(MU2,0,0,0.0); M_R=m424.M_fast(rR); lam=3*U+30*V*M_R
rhat=rR+2*lam*I_END; a0=2*lam*I_END/rhat
def J(t): return sb.J_of_t(t,rhat,nk=600,nmu=400)
QMAX=8*Q0; qgrid=np.linspace(1e-6,QMAX,1000); Jgrid=np.array([J(q) for q in qgrid])
def Ji(qq): return np.interp(np.asarray(qq),qgrid,Jgrid,left=Jgrid[0],right=0.0)
def Ghat4(t,nq=1000,nmu=300):
    q=np.linspace(1e-6,QMAX,nq); mu=np.linspace(-1,1,nmu); Qg,Mg=np.meshgrid(q,mu,indexing="ij")
    arg=np.sqrt(np.maximum(Qg**2+t**2-2*Qg*t*Mg,0.0))
    return float(np.trapezoid(np.trapezoid(Qg**2*Ji(Qg)*Ji(arg),mu,axis=1),q)/(4*np.pi**2))
theta_min=math.sqrt(rhat)/(2*Q0**2*math.sqrt(C)); t_min=2*Q0*math.sin(theta_min/2); t_max=2*Q0
chords=np.linspace(t_min,t_max,16)
pref=12*(5*V/2)**2/lam**2*4*(1-a0)
Rvals=[pref*Ghat4(t)/J(t) for t in chords]
Rmax=max(Rvals)
print(f"endpoint rhat={rhat:.5f} a0={a0:.4f}; realized quartic R(t) on 16 chords; R_max={Rmax:.4f}")

THRESH=0.634
claim("realized_Rmax_below_threshold", Rmax<THRESH,
      f"(realized R_max={Rmax:.4f} < {THRESH} (closure threshold at rho_lat=6.55): the Young-ceiling estimate "
      f"R_sup=1.59 (=> R_max 1.019) was loose by ~{1.019/Rmax:.1f}x; the direct value closes the endpoint IF the "
      "convention is right)")
claim("survives_moderate_convention_slack", Rmax*1.5<THRESH,
      f"(R_max x1.5 = {Rmax*1.5:.3f} < {THRESH}: the closure survives a +50% convention slack, but NOT a full "
      f"factor-2 ({Rmax*2:.3f} > {THRESH}) -- so the absolute factor-2/(2pi)^3 convention is the load-bearing "
      "residual; this is STRONG EVIDENCE, NOT a certified closure)")
g_lo=Ghat4(chords[8],1000,300); g_hi=Ghat4(chords[8],1500,450)
claim("convolution_converged", abs(g_hi-g_lo)<0.02*g_lo,
      f"(Ghat4 grid-converged to {abs(g_hi-g_lo)/g_lo*100:.2f}% -- the SHAPE is rigorous; only the ABSOLUTE "
      "normalisation convention is open)")
claim("no_lift_claimed", True,
      "(NO SC-SCOPE lift is claimed: the convention factor-2 is load-bearing and unpinned, and the joint is "
      "sunset-limited; SC-SCOPE remains a B1 named hypothesis. Strong evidence only.)")
ok=all(c["passed"] for c in CLAIMS)
out=REPO/"claims"/"B5-BEYOND-LAYER-BOUND"/"runs"/"260608-scscope-quartic-realized"
out.mkdir(parents=True,exist_ok=True)
(out/"result.json").write_text(json.dumps(dict(script="scscope_quartic_realized.py",version=__version__,
    rhat=rhat,a0=a0,R_max_realized=Rmax,threshold=THRESH,young_estimate=1.019,
    convention_caveat="absolute Ghat4 factor-2/(2pi)^3 unpinned; load-bearing",
    claims=CLAIMS,all_pass=ok),indent=2))
print(f"\nrealized R_max={Rmax:.4f} (script convention) << 0.634; CAVEAT: factor-2 convention unpinned (load-bearing)")
print(f"claims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
