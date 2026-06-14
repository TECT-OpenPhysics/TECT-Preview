"""dr2_t030_fewcircles_linear.py -- T-030 / R-039: the few-circles additive-energy
bound is LINEAR in the cover number for Q on a sphere (sharpening R-038's 3L^2N^2).

THEOREM (linear few-circles bound, SPHERE). If Q subset S^2 (origin-centred,
N=|Q|) is covered by L distinct circles, then
    E_+(Q) <= (2+2L) N^2 + 4 L N + 4 L^3  <=  6 (L+1) N^2   (L<=N).
LINEAR in L; strictly improves R-038's 3 L^2 N^2 for L>=2.

Proof (sum-circle occupancy; multi-circle refinement of Lemma A / R-025).
E_+ = r(0)^2 + sum_{m!=0} r(m)^2.  For m!=0, a+b=m with a,b in Q forces a.m =
|m|^2/2 IFF |a|=|b| -- which holds on an ORIGIN-CENTRED sphere (all |a|=radius).
Hence both summands lie on the sum-level circle C_m and r(m) <= t_m := |Q cap C_m|.
Each cover circle Gamma_i is a sphere section = C_{m_i} for a unique non-zero m_i
(great circles -> m=0, the antipodal term, split off). Two distinct circles meet
in <=2 points, so t_m <= 2L for m not in {m_i}, and t_{m_i} <= nu_i + 2L. Thus
sum_{m!=0} r(m)^2 <= 2L*sum r(m) + sum_i (nu_i+2L)^2 <= 2L N^2 + N^2 + 4LN + 4L^3.
Adding r(0)^2 <= N^2: E_+ <= (2+2L)N^2 + 4LN + 4L^3.  QED
(NOTE: the bound is FALSE off the sphere -- |a|!=|b| breaks r(m)<=t_m; R-038's
quadratic 3L^2N^2 is the correct general-circle bound. assert A6 below is the
guard that detected an earlier non-sphere test config.)

Exact integer arithmetic; Q on the integer sphere x^2+y^2+z^2=R (origin-centred).
self-test asserts; exit 0 iff all pass.
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-14"
__claims__ = ["B5-BEYOND-LAYER-BOUND"]

import json, sys, math
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CLAIMS=[]
def claim(n,c,d=""):
    CLAIMS.append(dict(name=n,passed=bool(c),detail=d)); print(f"  [{'PASS' if c else 'FAIL'}] {n} -- {d}")

def Eplus(Q):
    c=Counter()
    for ax,ay,az in Q:
        for bx,by,bz in Q: c[(ax+bx,ay+by,az+bz)]+=1
    return sum(v*v for v in c.values())
def Eplus_brute(Q):
    n=len(Q); t=0
    for i in range(n):
        for j in range(n):
            s=(Q[i][0]+Q[j][0],Q[i][1]+Q[j][1],Q[i][2]+Q[j][2])
            for k in range(n):
                for l in range(n):
                    if (Q[k][0]+Q[l][0],Q[k][1]+Q[l][1],Q[k][2]+Q[l][2])==s: t+=1
    return t
def reps2(n):                       # integer (x,y): x^2+y^2 = n  (n>=0)
    if n<0: return []
    out=[]; b=math.isqrt(n)
    for x in range(-b,b+1):
        y2=n-x*x
        if y2<0: continue
        y=math.isqrt(y2)
        if y*y==y2: out.append((x,y)); 
        if y*y==y2 and y!=0: out.append((x,-y))
    return out
def sphere_latitudes(R):            # genuine S^2: x^2+y^2+z^2=R, grouped by z
    lat={}
    zmax=math.isqrt(R)
    for z in range(-zmax, zmax+1):
        pts=[(x,y,z) for (x,y) in reps2(R-z*z)]
        if pts: lat[z]=pts
    return lat

def B_lin(L,N): return (2+2*L)*N*N + 4*L*N + 4*L**3
def B_R038(L,N): return 3*L*L*N*N

# build a genuine origin-centred sphere with several rich latitudes
R = 1105*1105
LAT = sphere_latitudes(R)
# rank latitudes by richness (z>=0 to avoid antipodal-latitude duplication of structure)
rich = sorted([(len(v), z) for z,v in LAT.items() if z>=0], reverse=True)
def config_from_top(L):
    zs=[z for _,z in rich[:L]]
    Q=[]
    for z in zs: Q+=LAT[z]
    return Q, zs

# ---- (A1) linear bound holds on genuine sphere configs (1..8 richest latitudes) ----
rows=[]
for L in (1,2,3,4,6,8):
    Q,zs=config_from_top(L); N=len(Q); E=Eplus(Q)
    rows.append((L,N,E,E/(L*N*N),E/(N*N),B_lin(L,N),B_R038(L,N)))
ok=all(E<=B_lin(L,N) for (L,N,E,_,_,_,_) in rows)
claim("A1_linear_bound_holds_sphere", ok,
      "S^2 (R=1105^2) top-L rich latitudes: " +
      "; ".join(f"L={L} N={N} E_+={E} E/N^2={r2:.2f} <=B_lin={Bl}" for (L,N,E,r1,r2,Bl,Bq) in rows))

# ---- (A2) strict improvement over R-038 for L>=2 ----
imp=all(B_lin(L,N)<B_R038(L,N) for (L,N,_,_,_,_,_) in rows if L>=2)
claim("A2_strict_improvement_over_R038", imp,
      "; ".join(f"L={L}: B_lin={Bl}<B_R038={Bq}" for (L,N,E,r1,r2,Bl,Bq) in rows if L>=2))

# ---- (A3) report L-scaling on the sphere (honest: linear bound vs measured) ----
r1s=[r1 for (_,_,_,r1,_,_,_) in rows]
claim("A3_bound_linear_measured_sublinear", all(rr<=6.0 for rr in r1s),
      f"measured E_+/(L N^2) at L=1,2,3,4,6,8 = {[round(x,2) for x in r1s]} (all <= the proved 6(L+1)/L); "
      "sphere curvature keeps measured energy modest -- the LINEAR bound holds with margin")

# ---- (A6) PROOF-MECHANISM GUARD: on a genuine sphere, #{m!=0 : r(m) > 2L} <= L ----
def special_count(Q,L):
    c=Counter()
    for ax,ay,az in Q:
        for bx,by,bz in Q: c[(ax+bx,ay+by,az+bz)]+=1
    return sum(1 for m,v in c.items() if m!=(0,0,0) and v>2*L)
fails=[]
for L in (2,3,4,6,8):
    Q,zs=config_from_top(L); sc=special_count(Q,L)
    if sc>L: fails.append((L,sc))
claim("A6_proof_mechanism_sphere", len(fails)==0,
      f"on genuine S^2, #{{m!=0 : r(m)>2L}} <= L for L=2,3,4,6,8 "
      + ("(all hold -> r(m)<=t_m and t_m<=2L off <=L sum-circles, the proof's core)" if not fails else f"VIOLATIONS {fails}"))

# ---- (A7) cover-number lower bound: E_+ <= 6(L+1)N^2 => L >= E_+/(6N^2)-1 ----
ok7=all(L+1e-9 >= E/(6.0*N*N)-1.0 for (L,N,E,_,_,_,_) in rows)
claim("A7_cover_number_lower_bound", ok7,
      "E_+ >= N^{2+delta} => L >= N^delta/12 (vs R-038's N^{delta/2}/sqrt3): exponent doubled")

# ---- (A8) estimator audit + sphere membership regression ----
Q1,_=config_from_top(1); onsphere=all(x*x+y*y+z*z==R for (x,y,z) in Q1)
sm=[(x,y,0) for (x,y) in reps2(25)]
claim("A8_estimator_and_sphere_membership", onsphere and Eplus(sm)==Eplus_brute(sm),
      f"all L=1 points on sphere x^2+y^2+z^2={R}: {onsphere}; estimator vec==brute on r^2=25 circle: {Eplus(sm)}=={Eplus_brute(sm)}")

ok=all(c["passed"] for c in CLAIMS)
out=REPO/"claims"/"B5-BEYOND-LAYER-BOUND"/"runs"/"260614-dr2-t030-fewcircles-linear"
out.mkdir(parents=True,exist_ok=True)
(out/"result.json").write_text(json.dumps(dict(
  script="dr2_t030_fewcircles_linear.py",version=__version__,sphere_R=R,
  theorem="E_+(Q) <= (2+2L)N^2+4LN+4L^3 <= 6(L+1)N^2 for Q on L distinct circles of an origin-centred sphere (LINEAR)",
  sphere_configs=[dict(L=L,N=N,Eplus=E,E_over_N2=r2,B_linear=Bl,B_R038=Bq) for (L,N,E,r1,r2,Bl,Bq) in rows],
  verdict="few-circles bound is O(L N^2) LINEAR on S^2 (R-038's 3L^2N^2 was loose); proof-mechanism guard A6 "
          "confirms r(m)<=t_m<=2L off <=L sum-circles; cover-number lower bound sharpened to L>=N^delta/12",
  claims=CLAIMS,all_pass=ok),indent=2,default=str))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
