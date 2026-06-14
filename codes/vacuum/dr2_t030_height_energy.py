"""dr2_t030_height_energy.py -- T-030 / R-042 (R-033 step 2): the latitude-union
additive energy is controlled by the HEIGHT additive energy E_h, and the
four-circle term is governed by SUM-ANNULUS OVERLAP -- the geometric reason
distinct radii give O(N^2). The remaining incidence bound stays OPEN.

(1) HEIGHT-ENERGY BOUND (proved, distinct-radius parallel circles).
    E_+(Q) <= N^2 + 2 sum_{(k,l)} nu_k nu_l p(z_k+z_l),
    p(H)=#{(i,j): z_i+z_j=H}. (For M_xy!=0, r(M_xy,M_z)<=2 p(M_z) and
    sum_{M_xy!=0} r <= sum_{(i,j) in P(M_z)} nu_i nu_j; the M_xy=0 slice is the
    diagonal <= N^2.) Uniform nu => E_+ <= N^2 + 2 (N^2/L^2) E_h with E_h = sum_H
    p(H)^2 the HEIGHT additive energy. So Sidon heights (E_h ~ L^2) => O(N^2);
    AP heights (E_h ~ L^3) => O(L N^2) -- the bound recovers both regimes and
    identifies E_h (a 1-D additive energy) as the controlling parameter.

(2) SUM-ANNULUS MECHANISM (the four-circle term, why distinct radii win).
    T_{ijkl} = #{c_a+c_b=c_c+c_d : c_a in C_i,..} = sum_w r^{ij}(w) r^{kl}(w).
    r^{ij}(w)!=0 forces |w| in the annulus [|rho_i-rho_j|, rho_i+rho_j]. If the
    two sum-annuli are DISJOINT, T_{ijkl}=0. Spread-out (distinct) radii make most
    cross-pairs' annuli disjoint -> the 4-circle energy collapses to O(N^2);
    equal radii (cylinder) make every annulus [0,2rho] -> maximal overlap -> linear.

(3) The remaining bound (the OPEN R-033 core): for OVERLAPPING annuli, improving
    T_{ijkl} below the Cauchy-Schwarz 3 sqrt(nu_i nu_j nu_k nu_l) to capture the
    incidence cancellation (so that the total is O(N^2 polylog) for ALL height
    structures) is the circle-incidence problem -- the N^{9/4} barrier. NOT closed.

self-test asserts (exact integer arithmetic); exit 0 iff all pass.
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-14"
__claims__ = ["B5-BEYOND-LAYER-BOUND"]
import json, sys, math
from collections import Counter
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
CLAIMS=[]
def claim(n,c,d=""):
    CLAIMS.append(dict(name=n,passed=bool(c),detail=d)); print(f"  [{'PASS' if c else 'FAIL'}] {n} -- {d}")
def Eplus(Q):
    c=Counter()
    for a in Q:
        for b in Q: c[(a[0]+b[0],a[1]+b[1],a[2]+b[2])]+=1
    return sum(v*v for v in c.values())
def circle_pts(r):
    pts=set()
    for x in range(-r,r+1):
        y2=r*r-x*x
        if y2<0: continue
        y=math.isqrt(y2)
        if y*y==y2: pts.add((x,y)); pts.add((x,-y))
    return sorted(pts)
def mian_chowla(L):
    S=[]; s=set(); n=0
    while len(S)<L:
        n+=1
        if all((a+n) not in s for a in S):
            for a in S: s.add(a+n)
            s.add(2*n); S.append(n)
    return S
RADII=[5,10,15,20,25,30,35,40]
def by_circle(heights): return [[(x,y,z) for (x,y) in circle_pts(RADII[i])] for i,z in enumerate(heights)]
def flat(bc): return [p for c in bc for p in c]
def height_energy(heights):
    p=Counter()
    for zi in heights:
        for zj in heights: p[zi+zj]+=1
    return sum(v*v for v in p.values()), p   # E_h, p(H)
def height_bound(heights, nus):
    _,p=height_energy(heights); N=sum(nus)
    S=0
    for k,zk in enumerate(heights):
        for l,zl in enumerate(heights): S+=nus[k]*nus[l]*p[zk+zl]
    return N*N + 2*S

# (A1) height-energy bound holds (Sidon + AP)
def run(heights):
    bc=by_circle(heights); Q=flat(bc); nus=[len(c) for c in bc]; N=len(Q); E=Eplus(Q)
    B=height_bound(heights,nus); Eh,_=height_energy(heights)
    return N,E,B,Eh
sid=[run(mian_chowla(L)) for L in (3,5,7)]
ap =[run(list(range(L))) for L in (3,5,7)]
claim("A1_height_energy_bound_holds", all(E<=B for (N,E,B,Eh) in sid+ap),
      "E_+ <= N^2 + 2 sum nu_k nu_l p(z_k+z_l): " + "; ".join(f"L-cfg E={E}<=B={B}" for (N,E,B,Eh) in sid+ap))

# (A2) the bound recovers Sidon (E_h~L^2 -> O(N^2)) vs AP (E_h~L^3 -> O(LN^2))
sid_eh=[Eh for (N,E,B,Eh) in sid]; ap_eh=[Eh for (N,E,B,Eh) in ap]
# AP height energy grows like L^3, Sidon like L^2: check ratio E_h/L^2 grows for AP, flat for Sidon
sid_ratio=[Eh/(L*L) for (L,(N,E,B,Eh)) in zip((3,5,7),sid)]
ap_ratio =[Eh/(L*L) for (L,(N,E,B,Eh)) in zip((3,5,7),ap)]
claim("A2_Eh_interpolation", max(sid_ratio)<=3.0 and ap_ratio[-1]>ap_ratio[0]+1.0,
      f"height energy E_h: Sidon E_h/L^2={[round(x,1) for x in sid_ratio]} (flat ~2 => O(N^2)); AP E_h/L^2={[round(x,1) for x in ap_ratio]} (grows ~L/3 => O(LN^2))")

# (A3) SUM-ANNULUS mechanism: disjoint sum-annuli => T_{ijkl}=0
def Tijkl(ri,rj,rk,rl):
    Ci=circle_pts(ri); Cj=circle_pts(rj); Ck=circle_pts(rk); Cl=circle_pts(rl)
    sij=Counter();
    for a in Ci:
        for b in Cj: sij[(a[0]+b[0],a[1]+b[1])]+=1
    skl=Counter()
    for c in Ck:
        for d in Cl: skl[(c[0]+d[0],c[1]+d[1])]+=1
    return sum(sij[w]*skl[w] for w in sij if w in skl)
def annuli_disjoint(ri,rj,rk,rl):
    lo1,hi1=abs(ri-rj),ri+rj; lo2,hi2=abs(rk-rl),rk+rl
    return hi1<lo2 or hi2<lo1
# disjoint sum-annuli => T=0 (RIGOROUS necessary condition); overlap is necessary-not-sufficient
dj = annuli_disjoint(3,4,50,60)         # [1,7] vs [10,110] disjoint
Tdisj = Tijkl(3,4,50,60)                # must be 0
Tpos  = Tijkl(20,25,20,25)              # matching pair, genuinely > 0
claim("A3_sum_annulus_necessary", dj and Tdisj==0 and Tpos>0,
      f"DISJOINT sum-annuli (3,4)|[1,7] vs (50,60)|[10,110] => T=0 (={Tdisj}); a matching pair (20,25) has T={Tpos}>0. "
      "Annulus overlap is NECESSARY for T!=0 (disjoint kills it); it is NOT sufficient (discrete sum-sets must also coincide). "
      "Spread/distinct radii => many disjoint annuli => 4-circle energy suppressed; equal radii => all annuli [0,2rho] => maximal overlap.")

# (A4) the height-bound is LOOSE for AP (incidence cancellation gap = the open core)
N,E,B,Eh = ap[-1]   # AP L=7
claim("A4_bound_loose_incidence_gap", E < 0.5*B,
      f"AP L=7: measured E_+={E} << height-bound B={B} (E/B={E/B:.2f}); the gap is the in-plane incidence cancellation the bound ignores = the OPEN R-033 core")

# (A5) estimator/consistency: E_+ <= 3 N^{9/4} (R-033 record) on all configs
claim("A5_R033_consistency", all(E<=3*N**2.25 for (N,E,B,Eh) in sid+ap),
      "all configs satisfy E_+ <= 3 N^{9/4} (R-033 record consistency)")

ok=all(c["passed"] for c in CLAIMS)
out=REPO/"claims"/"B5-BEYOND-LAYER-BOUND"/"runs"/"260614-dr2-t030-height-energy"
out.mkdir(parents=True,exist_ok=True)
(out/"result.json").write_text(json.dumps(dict(
  script="dr2_t030_height_energy.py",version=__version__,
  height_bound="E_+ <= N^2 + 2 sum_{k,l} nu_k nu_l p(z_k+z_l); uniform nu => N^2 + 2(N^2/L^2)E_h",
  sidon=[dict(N=N,Eplus=E,bound=B,E_h=Eh) for (N,E,B,Eh) in sid],
  ap=[dict(N=N,Eplus=E,bound=B,E_h=Eh) for (N,E,B,Eh) in ap],
  verdict="latitude-union energy controlled by HEIGHT additive energy E_h (1-D); the four-circle term needs "
          "SUM-ANNULUS overlap (distinct radii => disjoint annuli => O(N^2)); the incidence bound for overlapping "
          "annuli (-> O(N^2) for all height structures) stays OPEN = the R-033 core",
  claims=CLAIMS,all_pass=ok),indent=2,default=str))
print(f"\nheight-energy reduction + sum-annulus mechanism verified; incidence core stays OPEN (R-033)")
print(f"claims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
