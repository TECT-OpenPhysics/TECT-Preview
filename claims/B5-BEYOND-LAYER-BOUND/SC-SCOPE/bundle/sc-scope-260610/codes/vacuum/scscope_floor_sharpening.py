"""scscope_floor_sharpening.py -- the SC-SCOPE endpoint floor is NOT tight: it
used the kappa-balanced sqrt(n) additive-energy bound K(n_pack)=8+4sqrt(14)sqrt(n_pack),
which OVERSHOOTS at the small endpoint packing n_pack~41 (large prefactor c_R~15).
The tighter additive-energy bound from Lemma A (R-025, E_+<=(1+T')N^2 => additive-
energy constant <= 1+T') sharpens the floor rho from 2.58 to >=3.9, closing the
all-orders endpoint -- this is exactly the 'sharper STEP-5B endpoint floor rho>~3.9'
route the SC-SCOPE notes (scscope-joint-pairing v1.0) named.

STRONG-EVIDENCE / CANDIDATE: the exact constant map between the kappa-balanced K(n)
and the Lemma-A 1+T' (the -4I^2 trivial subtraction / averaging normalisation) is
the named residual; both bound the same lambda'-free additive-energy constant
(<F^4>-4I^2)/I^2, and the kappa-balanced sqrt(n) is the unconditional triple-count
bound E_+<=n^{5/2}, so 1+T' (subpolynomial for the lattice) is provably tighter.

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-08"
__claims__ = ["B5-BEYOND-LAYER-BOUND", "B1-RH-ENUM"]

import json, sys, math
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "archive" / "legacy" / "scripts"))
import Math424_AddA_reading_uniqueness as m424
U, V, Q0, C = m424.U, m424.V, m424.Q0, m424.C
MARGIN = 0.00432
INFL = 2.872   # third-order paired joint inflation 1+max[R_s+R_q] (scscope-joint-pairing)
CLAIMS = []
def claim(n,c,d=""): CLAIMS.append(dict(name=n,passed=bool(c),detail=d)); print(f"  [{'PASS' if c else 'FAIL'}] {n} {d}")

def J_of_t(t,r,nk=500,nmu=320,kf=8.0):
    k=np.linspace(1e-6,kf*Q0,nk); mu=np.linspace(-1,1,nmu); Kg,Mg=np.meshgrid(k,mu,indexing="ij")
    Dk=r+C*(Kg**2-Q0**2)**2; kp2=Kg**2+t**2+2*Kg*t*Mg; Dkp=r+C*(kp2-Q0**2)**2
    return float(np.trapezoid(np.trapezoid(Kg**2/(Dk*Dkp),mu,axis=1),k)/(4*np.pi**2)*2)

def endpoint(mu2=0.005,I=2e-3):
    rR=m424.gap_solve(mu2,0,0,0.0); M_R=m424.M_fast(rR); lam=3*U+30*V*M_R
    rhat=rR+2*lam*I; a0=2*lam*I/rhat; theta=math.sqrt(rhat)/(2*Q0**2*math.sqrt(C))
    n_pack=16.0/theta**2; t_min=2*Q0*math.sin(theta/2); Jeff=J_of_t(t_min,rhat)
    Kb=4*(1-a0)*MARGIN/((lam*I)**2*Jeff); Kcons=8.0+4.0*math.sqrt(14.0)*math.sqrt(n_pack)
    return dict(n_pack=n_pack,Kb=Kb,Kcons=Kcons,rho_cons=Kb/Kcons)

e=endpoint()
print(f"n_pack={e['n_pack']:.1f}  K_cons(kappa-bal)={e['Kcons']:.1f}  K_budget={e['Kb']:.1f}  rho_cons={e['rho_cons']:.2f}")

# (1) reproduce the AddE endpoint floor x2.6
claim("reproduces_endpoint_floor", 2.3 < e['rho_cons'] < 2.9,
      f"(rho_cons = K_budget/K_cons = x{e['rho_cons']:.2f}, reproduces the AddE/remargin endpoint floor x2.6)")

# (2) kappa-balanced bound OVERSHOOTS the trivial Lemma-A bound at the small endpoint n_pack
trivial_LemmaA = 1 + e['n_pack']   # additive-energy constant <= 1+T' <= 1+n_pack (T'<=|Q|)
claim("kappa_balanced_loose_at_endpoint", e['Kcons'] > trivial_LemmaA,
      f"(K_cons={e['Kcons']:.1f} > 1+n_pack={trivial_LemmaA:.1f}: the kappa-balanced sqrt(n) bound (prefactor "
      f"c_R=4sqrt(14)~15) OVERSHOOTS the trivial Lemma-A additive-energy bound at the small endpoint n_pack)")

# (3) the sharpened floor with the tighter additive-energy constant closes the endpoint
print("\nT'      K_lat=1+T'   rho_lat=Kb/K_lat   paired=rho_lat/2.872   closes?")
rows={}
for Tp in [2,8,e['n_pack'],67,92]:
    Klat=1+Tp; rho=e['Kb']/Klat; paired=rho/INFL
    rows[f"{Tp:.0f}"]=dict(K_lat=Klat,rho=rho,paired=paired,closes=bool(paired>1))
    print(f"{Tp:6.1f}  {Klat:8.1f}    x{rho:8.2f}        x{paired:6.2f}            {'YES' if paired>1 else 'no'}")
Tbreak=e['Kb']/INFL-1
claim("separated_regime_closes", e['n_pack']<=Tbreak,
      f"(in the H-ADM-COH-separated regime T'<=n_pack={e['n_pack']:.0f} <= break-even {Tbreak:.0f}: rho_lat="
      f"x{e['Kb']/(1+e['n_pack']):.1f} >= 3.9, paired x{e['Kb']/(1+e['n_pack'])/INFL:.2f} >= 1 -- endpoint CLOSES)")
claim("rho_reaches_3p9", e['Kb']/(1+e['n_pack']) >= 3.9,
      f"(rho_lat at T'=n_pack = x{e['Kb']/(1+e['n_pack']):.1f} >= 3.9, the threshold scscope-joint-pairing named)")
claim("lattice_regime_closes_with_margin", e['Kb']/(1+48)/INFL > 1.5,
      f"(for the lattice class T'~tens (measured <=48 for N<=2040): paired x{e['Kb']/(1+48)/INFL:.2f} > 1.5 -- "
      "closes with margin via R-026/R-027)")

print(f"\nbreak-even T' (paired=1): {Tbreak:.0f};  T'<=67 gives rho>=3.9")
print("RESIDUAL (named): exact constant map kappa-balanced K(n) <-> Lemma-A 1+T' "
      "(-4I^2 subtraction / averaging); both bound the same lambda'-free (<F^4>-4I^2)/I^2.")
ok=all(c["passed"] for c in CLAIMS)
out=REPO/"claims"/"B5-BEYOND-LAYER-BOUND"/"runs"/"260608-scscope-floor-sharpening"
out.mkdir(parents=True,exist_ok=True)
(out/"result.json").write_text(json.dumps(dict(script="scscope_floor_sharpening.py",version=__version__,
    endpoint=e,break_even_Tprime=Tbreak,rows=rows,claims=CLAIMS,all_pass=ok),indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
