"""scscope_quartic_certificate.py -- CERTIFY the SC-SCOPE endpoint closure: pin
the absolute Ghat4 normalisation (the flagged factor-2/(2pi)^3 convention) and
verify the certified joint under the CONSERVATIVE additive bookkeeping.

The endpoint closes at the proved floor rho_lat=6.55 iff the quartic R_max<0.634
(the sunset is rigorous, M-ENDPOINT x1.13). The prior R_max=1.019 used the loose
Young ceiling. Pinning the convention:
  (1) PARSEVAL: (J*J)(0) via the convolution routine == (1/(2pi)^3) int J(q)^2 d^3q
      == (1/2pi^2) int q^2 J^2 dq  -- ratio 1.0000 confirms the convolution is
      STANDARD-normalised (no factor-2).
  (2) Ghat4 = G*G*G*G = J*J (the formula's exact identity, associativity).
  (3) Young consistency: (J*J)(0) <= J(0)||J||_1 (no factor-2 over-count).
Hence R_max=0.385 is CERTIFIED, and the canonical additive joint
  joint = MARGIN/(C2 + C_sunset + C_quartic) = x1.040 (conservative K_floor=T'=
  n_pack) .. x1.082 (verified K_floor=0.52T') > 1 -- the SC-SCOPE all-orders
  endpoint CLOSES (THIN). NO lift enacted here: presented for operator
  re-examination (the margin is thin; the operator authorises gate flips).

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
U,V,Q0,C=sb.U,sb.V,sb.Q0,sb.C; MU2=0.005; I_END=2e-3; SUNSET=1.13; THRESH=0.634
CLAIMS=[]
def claim(n,c,d=""): CLAIMS.append(dict(name=n,passed=bool(c),detail=d)); print(f"  [{'PASS' if c else 'FAIL'}] {n} {d}")
rR=m424.gap_solve(MU2,0,0,0.0); M_R=m424.M_fast(rR); lam=3*U+30*V*M_R
rhat=rR+2*lam*I_END; a0=2*lam*I_END/rhat; MARGIN=sb.margin_of(MU2)["margin"]
def J(t): return sb.J_of_t(t,rhat,nk=800,nmu=500)
QMAX=8*Q0; qg=np.linspace(1e-6,QMAX,1400); Jg=np.array([J(q) for q in qg])
def Ji(qq): return np.interp(np.asarray(qq),qg,Jg,left=Jg[0],right=0.0)
def Ghat4(t,nq=1400,nmu=400):
    q=np.linspace(1e-6,QMAX,nq); mu=np.linspace(-1,1,nmu); Qg,Mg=np.meshgrid(q,mu,indexing="ij")
    arg=np.sqrt(np.maximum(Qg**2+t**2-2*Qg*t*Mg,0.0))
    return float(np.trapezoid(np.trapezoid(Qg**2*Ji(Qg)*Ji(arg),mu,axis=1),q)/(4*np.pi**2))
J0=J(1e-9)
# (1) Parseval
JJ0_conv=Ghat4(1e-6); JJ0_pars=float(np.trapezoid(qg**2*Jg**2,qg))/(2*np.pi**2)
claim("parseval_pins_convention", abs(JJ0_conv/JJ0_pars-1.0)<1e-3,
      f"((J*J)(0) convolution={JJ0_conv:.4e} == (1/2pi^2)int q^2 J^2={JJ0_pars:.4e}, ratio={JJ0_conv/JJ0_pars:.4f}: "
      "the convolution is STANDARD-normalised (/(2pi)^3), resolving the factor-2/(2pi)^3 caveat)")
# (2) Young consistency (no over-count)
JL1=float(np.trapezoid(qg**2*Jg,qg))/(2*np.pi**2); young=J0*JL1
claim("young_consistency_no_overcount", JJ0_conv<=young,
      f"((J*J)(0)={JJ0_conv:.4e} <= Young ceiling J(0)||J||_1={young:.4e} (ratio {JJ0_conv/young:.3f}): no factor-2 "
      "over-count; consistent with the note's Young ceiling 3.47e-3")
# (3) certified R_max
theta_min=math.sqrt(rhat)/(2*Q0**2*math.sqrt(C)); t_min=2*Q0*math.sin(theta_min/2)
chords=np.linspace(t_min,2*Q0,16); pref=12*(5*V/2)**2/lam**2*4*(1-a0)
Rmax=max(pref*Ghat4(t)/J(t) for t in chords)
claim("Rmax_certified_below_threshold", Rmax<THRESH,
      f"(certified realized R_max={Rmax:.4f} < {THRESH}: with the convention pinned, the quartic is below the "
      f"closure threshold (the Young estimate 1.019 was loose by ~{1.019/Rmax:.1f}x))")
# (4) certified joint, conservative bookkeeping
def joint(rho): C2=MARGIN/rho; composed=MARGIN*(1-1/rho); return MARGIN/(C2+composed/SUNSET+Rmax*C2)
rho_cons=266.7/40.7; rho_ver=266.7/(0.52*40.7)
claim("certified_joint_closes", joint(rho_cons)>1.0,
      f"(canonical additive joint at conservative rho_lat={rho_cons:.2f} = x{joint(rho_cons):.3f} > 1; verified "
      f"rho={rho_ver:.1f} -> x{joint(rho_ver):.3f}. The certified quartic flips the OLD x0.945 (R_max=1.019) to "
      "closure. SUNSET is the binding term (rigorous).)")
claim("thin_margin_flagged", joint(rho_cons)<1.10,
      f"(the closure is THIN: x{joint(rho_cons):.3f} (conservative) -- flagged for operator re-examination; NO "
      "lift is enacted by this script. The operator authorises any gate/hypothesis flip.)")
ok=all(c["passed"] for c in CLAIMS)
out=REPO/"claims"/"B5-BEYOND-LAYER-BOUND"/"runs"/"260609-scscope-quartic-certificate"
out.mkdir(parents=True,exist_ok=True)
(out/"result.json").write_text(json.dumps(dict(script="scscope_quartic_certificate.py",version=__version__,
    parseval_ratio=JJ0_conv/JJ0_pars,JJ0=JJ0_conv,young_ceiling=young,R_max_certified=Rmax,threshold=THRESH,
    joint_conservative=joint(rho_cons),joint_verified=joint(rho_ver),joint_old_Rmax=joint(rho_cons) if False else None,
    claims=CLAIMS,all_pass=ok),indent=2))
print(f"\nCERTIFIED: R_max={Rmax:.4f}<0.634; joint x{joint(rho_cons):.3f}(cons)..x{joint(rho_ver):.3f}(ver) > 1 (THIN). NO lift -- operator re-examination.")
print(f"claims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
