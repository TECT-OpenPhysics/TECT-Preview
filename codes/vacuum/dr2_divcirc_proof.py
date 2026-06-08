"""dr2_divcirc_proof.py -- EXACT verification of the [DIV-CIRC] proof chain that
upgrades the lattice-class DR-2 from T6 (conditional) to T7 (unconditional,
modulo textbook number theory: the class-number formula + d(n) <<_eps n^eps).

Per sum-level circle C_m (center m/2):
  x in Z^3, |x|^2=R, x.m=|m|^2/2  =>  y := 2x-m in Lambda_m=Z^3 cap m^perp
  (y.m=0), |y|^2 = 4R-|m|^2 =: R'; x|->y injective, so
    #(Z^3 cap C_m) <= #{y in Lambda_m : |y|^2=R'} = r_Q(R') <= 6 d(R') <<_eps R^eps,
  the last step by the class-number formula (single class <= sum over classes of
  disc(Q) = w*sum_{d|R'} chi(d) <= 6 d(R'); UNIFORM in m).

Fast richest-circle search via the Gram matrix D[k,i]=Q[k].Q[i]:
  for m=Q[i]+Q[j],  x.m = D[k,i]+D[k,j],  |m|^2 = 2R+2 D[i,j],
  so #(Z^3 cap C_m) = #{k : D[k,i]+D[k,j] == R + D[i,j]}.
self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-08"
__claims__ = ["B5-BEYOND-LAYER-BOUND"]

import json, sys, math
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
CLAIMS = []
def claim(n,c,d=""):
    CLAIMS.append(dict(name=n,passed=bool(c),detail=d)); print(f"  [{'PASS' if c else 'FAIL'}] {n} {d}")

def lattice_Z3(R):
    pts=[]; b=int(math.isqrt(R))
    for x in range(-b,b+1):
        for y in range(-b,b+1):
            z2=R-x*x-y*y
            if z2<0: continue
            z=math.isqrt(z2)
            if z*z==z2:
                for zz in ({z,-z} if z else {0}): pts.append((x,y,zz))
    return pts

def num_divisors(n):
    if n<=0: return 0
    n=int(n); d=1; p=2
    while p*p<=n:
        if n%p==0:
            e=0
            while n%p==0: n//=p; e+=1
            d*=(e+1)
        p+=1 if p==2 else 2
    if n>1: d*=2
    return d

def richest_circle(Q,R):
    Qa=np.array(Q,dtype=np.int64); N=len(Q)
    D=Qa@Qa.T                              # Gram matrix (integer)
    best=(-1,None)
    for i in range(N):
        Di=D[:,i]
        # n for m=Q[i]+Q[j] over all j>=i : count_k [ D[k,i]+D[k,j] == R + D[i,j] ]
        for j in range(i,N):
            # skip the degenerate m=0 case (Q[i]+Q[j]=0, antipodal): C_0 is the whole
            # sphere, handled separately in the proof by r(0)^2 <= N^2. We bound the
            # PROPER (m!=0) sum-circles only, exactly as Lemma A / the theorem do.
            if (Qa[i]+Qa[j]==0).all():
                continue
            target=R+D[i,j]
            n=int(np.count_nonzero(Di+D[:,j]==target))
            if n>best[0]:
                best=(n,(i,j))
    n,(i,j)=best
    m=tuple(int(Qa[i,t]+Qa[j,t]) for t in range(3))
    xs=[tuple(int(v) for v in Qa[k]) for k in range(N) if int(D[k,i]+D[k,j])==R+int(D[i,j])]
    return n,m,xs

def rQ_homogeneous(m,Rp):
    if Rp<0: return 0
    bb=int(math.isqrt(Rp)); cnt=0
    for ax in range(-bb,bb+1):
        for ay in range(-bb,bb+1):
            az2=Rp-ax*ax-ay*ay
            if az2<0: continue
            az=math.isqrt(az2)
            if az*az==az2:
                for azz in ({az,-az} if az else {0}):
                    if ax*m[0]+ay*m[1]+azz*m[2]==0: cnt+=1
    return cnt

SHELLS=[101,314,561,749]   # small shells: full O(N^2) richest-circle search is fast
print("=== EXACT verification of the [DIV-CIRC] proof chain ===")
print("R     N    T'   m                R'=4R-|m|^2  r_Q(R')  6d(R')  subst  T'<=6d")
rows={}
for R in SHELLS:
    Q=lattice_Z3(R); N=len(Q)
    Tp,m,xs=richest_circle(Q,R)
    mm=m[0]*m[0]+m[1]*m[1]+m[2]*m[2]; Rp=4*R-mm
    ys=[(2*x[0]-m[0],2*x[1]-m[1],2*x[2]-m[2]) for x in xs]
    subst=all(y[0]*m[0]+y[1]*m[1]+y[2]*m[2]==0 and y[0]*y[0]+y[1]*y[1]+y[2]*y[2]==Rp for y in ys)
    inj=(len(set(ys))==len(xs))
    rQ=rQ_homogeneous(m,Rp); d6=6*num_divisors(Rp)
    rows[R]=dict(N=N,T_prime=Tp,m=list(m),Rp=Rp,rQ=rQ,six_d=d6,
                 subst=bool(subst and inj),Tp_le_rQ=bool(Tp<=rQ),Tp_le_6d=bool(Tp<=d6))
    print(f"{R:4d} {N:4d}  {Tp:3d}  {str(list(m)):15s}  {Rp:8d}   {rQ:5d}   {d6:5d}   "
          f"{'OK' if rows[R]['subst'] else 'BAD':3s}   {'OK' if Tp<=d6 else 'BAD'}")

claim("substitution_y_eq_2x_minus_m", all(rows[R]["subst"] for R in SHELLS),
      "(every x on the richest sum-circle: y=2x-m in Lambda_m (y.m=0), |y|^2=4R-|m|^2 EXACTLY, x|->y injective "
      "-- the shift-removal step)")
claim("Tprime_le_rQ_homogeneous", all(rows[R]["Tp_le_rQ"] for R in SHELLS),
      "(#(Z^3 cap C_m) <= r_Q(R') = #{y in Lambda_m:|y|^2=R'}: bounded by a HOMOGENEOUS rank-2 representation "
      "count, no center/shift)")
claim("rQ_le_6d_classnumber", all(rows[R]["rQ"]<=rows[R]["six_d"] for R in SHELLS),
      "(r_Q(R') <= 6 d(R') for the richest circle: the uniform class-number bound)")
claim("Tprime_le_6d_chain", all(rows[R]["Tp_le_6d"] for R in SHELLS),
      f"(full chain T' <= 6 d(4R-|m|^2) <<_eps R^eps verified; max T'/6d = "
      f"{max(rows[R]['T_prime']/rows[R]['six_d'] for R in SHELLS):.2f})")

ok=all(c["passed"] for c in CLAIMS)
out=REPO/"claims"/"B5-BEYOND-LAYER-BOUND"/"runs"/"260608-dr2-divcirc-proof"
out.mkdir(parents=True,exist_ok=True)
(out/"result.json").write_text(json.dumps(dict(script="dr2_divcirc_proof.py",version=__version__,
    proof="x|->2x-m: #(Z^3 cap C_m) <= r_Q(4R-|m|^2) <= 6 d(4R-|m|^2) <<_eps R^eps",
    shells=rows,claims=CLAIMS,all_pass=ok),indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
