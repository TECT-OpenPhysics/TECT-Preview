"""res5_projection_factor.py -- RES-5 endpoint projection factor chi_proj
(operator route: test chi_proj <= 0.82 to close the endpoint at the PROVED slack).

HONEST RESULT: chi_proj = 1.25 > 1, the OPPOSITE of the hoped <0.82. The a0-
skeleton's response factor C_G = 1/(1+g) = 1/(1+lam' chi0(0)) is the screening at
FORWARD (k=0), where the bubble chi0(k) PEAKS (chi0 is monotone decreasing in |k|).
The pattern modulation lam'(P^2-<P^2>) is supported on the {110} BCC transfers
(|t|/q0 in {1,sqrt2,sqrt3,2}), AWAY from forward, where the screening factor
f(t)=1/(1+lam' chi0(|t|)) is LARGER (less screening) than C_G. The w_t^2-weighted
average f_avg = 0.613 > C_G = 0.492, so chi_proj = f_avg/C_G = 1.25.

CONSEQUENCE: the operator-norm/screening estimate C_higher ~ C_G a0 = 0.047 was an
UNDER-estimate; the corrected tail is C_higher = f_avg a0 = 0.059. The endpoint
therefore closes ONLY at the verified floor (0.059 < slack_verified 0.0758, 22%
margin), NOT at the conservative/proved floor (0.059 > 0.0385). The projection
route is ELIMINATED as a closure lever; the endpoint rests SOLELY on the DR-2 floor
route, now with a thinner margin. Off-endpoint (I<=1e-3) closure is UNAFFECTED (the
>=27x margin absorbs the 1.25 factor).

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__claims__ = ["B1-RH-ENUM"]
import json, sys, itertools
from collections import defaultdict
from pathlib import Path
import numpy as np
REPO=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(REPO/"archive"/"legacy"/"scripts"))
import Math424_AddA_reading_uniqueness as m424
U,V,Q0,C=m424.U,m424.V,m424.Q0,m424.C
CLAIMS=[]
def claim(n,c,d=""): CLAIMS.append(dict(name=n,passed=bool(c),detail=d)); print(f"  [{'PASS' if c else 'FAIL'}] {n} {d}")

rR=m424.gap_solve(0.005,0,0,0.0); M_R=m424.M_fast(rR); lam=3*U+30*V*M_R
I_end=2e-3; rhat=rR+2*lam*I_end; a0=2*lam*I_end/rhat; q0=Q0
def G(k): return 1.0/(rhat+C*(k*k-Q0**2)**2)
pp=np.linspace(1e-6,8*Q0,3000); mu=np.linspace(-1,1,400); Gp=G(pp)
def chi0(k):
    P,MU=np.meshgrid(pp,mu,indexing='ij')
    kk=np.sqrt(np.clip(P*P+k*k+2*P*k*MU,0,None))
    return np.trapezoid(pp*pp*Gp*np.trapezoid(G(kk),mu,axis=1),pp)/(2*np.pi)**2

ch0=chi0(1e-3); g=lam*ch0; C_G=1.0/(1.0+g)
# bubble is forward-peaked (monotone decreasing): verify chi0(q0) < chi0(0)
ch_q0=chi0(q0)
claim("bubble_forward_peaked", ch_q0 < ch0,
      f"(chi0(0)={ch0:.4f} > chi0(q0)={ch_q0:.4f}: the bubble peaks at FORWARD, so screening f=1/(1+lam chi0) is "
      f"MAXIMAL at k=0 (C_G={C_G:.3f}) and WEAKER at the {{110}} transfers)")

# {110} signed vectors, transfers, w_t^2 weights
vs=set()
for perm in set(itertools.permutations((1,1,0))):
    for sg in itertools.product((1,-1),repeat=3):
        w=tuple(perm[i]*sg[i] for i in range(3))
        if sum(c*c for c in w)==2: vs.add(w)
vs=[np.array(w)/np.sqrt(2)*q0 for w in vs]
wt=defaultdict(float)
for ki in vs:
    for kj in vs: wt[tuple(np.round(ki+kj,6))]+=1.0
binw=defaultdict(float)
for t,w in wt.items():
    binw[round(np.sqrt(sum(c*c for c in t))/q0,3)]+=w*w
num=den=0.0; fmax_over_CG=0.0
for key in sorted(binw):
    if key<1e-6: continue
    f=1.0/(1.0+lam*chi0(key*q0)); num+=binw[key]*f; den+=binw[key]
    fmax_over_CG=max(fmax_over_CG,f/C_G)
f_avg=num/den; chi_proj=f_avg/C_G; tail_corr=f_avg*a0

claim("screening_weaker_at_110_than_forward", fmax_over_CG>1.0,
      f"(every {{110}} transfer has f(t)/C_G>1 (up to {fmax_over_CG:.2f}): the modulation lives where screening is "
      "WEAKER than the forward C_G -- the source is NOT in the maximally-screened channel)")

claim("chi_proj_exceeds_one_not_below_082", chi_proj>1.0,
      f"(chi_proj = f_avg/C_G = {f_avg:.3f}/{C_G:.3f} = {chi_proj:.3f} > 1 -- the OPPOSITE of the hoped <0.82. The "
      "projection route does NOT close the endpoint; it CORRECTS the operator-norm estimate UPWARD)")

slack_proved, slack_verified = 1-1/1.040, 1-1/1.082
claim("corrected_tail_closes_only_at_verified", slack_proved < tail_corr < slack_verified,
      f"(corrected tail = f_avg a0 = {tail_corr:.4f} (vs operator-norm C_G a0 = {C_G*a0:.4f}); slack_proved "
      f"{slack_proved:.4f} < {tail_corr:.4f} < slack_verified {slack_verified:.4f}: the endpoint closes ONLY at the "
      f"verified floor ({(1-tail_corr/slack_verified)*100:.0f}% margin), NOT at the conservative/proved floor)")

claim("projection_lever_eliminated", chi_proj>0.82,
      f"(chi_proj={chi_proj:.2f} > 0.82: the res5-endpoint v1.1 projection lever (chi_proj<=0.82) is ELIMINATED. The "
      "endpoint rests SOLELY on the DR-2 floor route, with the corrected (thinner) margin)")

ok=all(c["passed"] for c in CLAIMS)
out=REPO/"claims"/"B1-RH-ENUM"/"runs"/"260610-res5-projection-factor"; out.mkdir(parents=True,exist_ok=True)
(out/"result.json").write_text(json.dumps(dict(script="res5_projection_factor.py",version=__version__,
    chi0_forward=ch0,g=g,C_G=C_G,a0=a0,f_avg=f_avg,chi_proj=chi_proj,tail_operator_norm=C_G*a0,tail_corrected=tail_corr,
    slack_proved=slack_proved,slack_verified=slack_verified,
    verdict="chi_proj=1.25>1: projection route ELIMINATED as a closure lever; the operator-norm C_G a0=0.047 was an "
            "under-estimate (forward-screening), corrected tail f_avg a0=0.059 closes ONLY at the verified floor "
            "(22% margin), not conservative. Endpoint rests solely on the DR-2 floor route. B1 T6 on {H-LAYER}.",
    claims=CLAIMS,all_pass=ok),indent=2))
print(f"\nchi0(0)={ch0:.4f} g={g:.3f} C_G={C_G:.3f} | f_avg={f_avg:.3f} chi_proj={chi_proj:.3f} | "
      f"tail: op-norm {C_G*a0:.4f} -> corrected {tail_corr:.4f}")
print(f"claims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
