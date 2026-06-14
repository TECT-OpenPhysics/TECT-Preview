"""dr2_t030_fewcircles.py -- T-030 / [NEST-DEPTH]: a few-circles sufficient
condition for arbitrary-Q DR-2 additive energy.

THEOREM (few-circles bound). If a finite set Q in R^3 (in the T-030 application,
Q subset S^2) is covered by L circles Gamma_1..Gamma_L (each a planar section),
then  E_+(Q) <= 3 L^2 N^2,  N=|Q|, where E_+(Q)=#{(a,b,c,d) in Q^4: a+b=c+d}.

Proof. Partition Q = ⊔_i Q_i with Q_i subset Gamma_i. Then r(m):=#{(a,b):a+b=m}
= sum_{i,j} r_{ij}(m), r_{ij}(m)=#{(a,b) in Q_i x Q_j: a+b=m}. For fixed m,
a+b=m with a in Gamma_i forces a in Gamma_i ∩ (m - Gamma_j); m - Gamma_j is a
circle (reflection then translation), and two DISTINCT circles in R^3 meet in
<= 2 points. m - Gamma_j = Gamma_i can hold for at most ONE m_0 (it forces equal
radius + parallel planes, fixing the translation). Hence r_{ij}(m) <= 2 for all
m != m_0, and r_{ij}(m_0) <= min(|Q_i|,|Q_j|). So the rectangular energy
E_+(Q_i,Q_j)=sum_m r_{ij}(m)^2 <= min(|Q_i|,|Q_j|)^2 + 2|Q_i||Q_j| <= 3|Q_i||Q_j|.
Cauchy-Schwarz over the L^2 index pairs: r(m)^2 <= L^2 sum_{ij} r_{ij}(m)^2, so
E_+(Q) <= L^2 sum_{ij} E_+(Q_i,Q_j) <= 3 L^2 (sum_i|Q_i|)^2 = 3 L^2 N^2.  QED

CONSEQUENCES.
 - L <=_eps N^eps  =>  E_+ <=_eps N^{2+eps}: DR-2 closed UNCONDITIONALLY for the
   few-circles class -- no decoupling, no circle-incidence bound.
 - L=1: any single circle, however rich, has E_+ <= 3 N^2; the rich-latitude
   obstruction (T'=N; frontier-consolidation Sec.2.3) is benign.
 - The [NEST-DEPTH] lacunary witness lies on ONE great circle (L=1) => E_+ <= 3N^2
   INDEPENDENT of nesting depth log2(1/s). The exp(depth) fixed-scale telescoping
   loss is an artifact of the decoupling technique, not the bound.
 - Open core (sharp): T-030 stays open only for Q requiring L = N^{Omega(1)}
   circles to cover with the energy spread across them (super-polynomially-many
   simultaneously-rich circles; consistent with R-033 Cor.1.2).

Exact integer arithmetic throughout. self-test asserts; exit 0 iff all pass.
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-14"
__claims__ = ["B5-BEYOND-LAYER-BOUND"]

import json, sys, math
from collections import Counter
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CLAIMS = []
def claim(name, cond, detail=""):
    CLAIMS.append(dict(name=name, passed=bool(cond), detail=detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} -- {detail}")

# ---------- exact additive-energy primitives (integer tuples) ----------
def Eplus(Q):
    c = Counter()
    for ax,ay,az in Q:
        for bx,by,bz in Q:
            c[(ax+bx, ay+by, az+bz)] += 1
    return sum(v*v for v in c.values())

def Eplus_brute(Q):
    n=len(Q); tot=0
    for i in range(n):
        for j in range(n):
            sx=Q[i][0]+Q[j][0]; sy=Q[i][1]+Q[j][1]; sz=Q[i][2]+Q[j][2]
            for k in range(n):
                for l in range(n):
                    if Q[k][0]+Q[l][0]==sx and Q[k][1]+Q[l][1]==sy and Q[k][2]+Q[l][2]==sz:
                        tot+=1
    return tot

def Erect_maxmult(A,B):
    c=Counter()
    for ax,ay,az in A:
        for bx,by,bz in B:
            c[(ax+bx,ay+by,az+bz)]+=1
    vals=sorted(c.values(), reverse=True)
    return vals, sum(v*v for v in vals)

# ---------- circle generators (exact integer coordinates) ----------
def gauss_circle(r):
    pts=set()
    for x in range(-r, r+1):
        y2=r*r-x*x
        if y2<0: continue
        y=math.isqrt(y2)
        if y*y==y2:
            pts.add((x,y)); pts.add((x,-y))
    return sorted(pts)

def latitude(r, z):
    return [(x,y,z) for (x,y) in gauss_circle(r)]

def lacunary_great_circle(J):
    # rational points on the unit (great) circle x^2+y^2=1, z=0, parameter t=2^-j
    fr=[]
    for j in range(J+1):
        t=Fraction(1, 2**j)
        x=(1-t*t)/(1+t*t); y=(2*t)/(1+t*t)
        fr.append((x,y,Fraction(0)))
    D=1
    for (x,y,z) in fr:
        D=math.lcm(D, x.denominator, y.denominator, z.denominator)
    pts=[(int(x*D), int(y*D), int(z*D)) for (x,y,z) in fr]
    # min separation (squared, integer) and dyadic nesting depth
    n=len(pts); dmin2=None
    for i in range(n):
        for k in range(i+1,n):
            d2=sum((pts[i][q]-pts[k][q])**2 for q in range(3))
            if dmin2 is None or d2<dmin2: dmin2=d2
    s=math.sqrt(dmin2)/D            # min chord length on the unit circle
    depth=int(round(math.log2(1.0/s))) if s>0 else 0
    return pts, depth, s

# ============================ ASSERTS ============================
print("== few-circles bound E_+(Q) <= 3 L^2 N^2 ==")

# (A1) single rich latitude (L=1): R-033 F1/F5 cross-check + theorem
C1105 = latitude(1105, 47)                 # x^2+y^2=1105^2, z=47
N1 = len(C1105); E1 = Eplus(C1105)
claim("A1_single_circle_L1_and_R033_crosscheck",
      N1==108 and E1==34668 and E1 <= 3*1*1*N1*N1,
      f"1105-latitude@z=47: N={N1}, E_+={E1} (R-033 F1/F5 published 34668 -> MATCH), "
      f"3 L^2 N^2 = {3*N1*N1} (L=1), ratio E_+/N^2={E1/N1**2:.3f} (~3, near-tight constant)")

# (A2) L=4 same-radius stack (adversarial alignment), exact product structure
stack = []
for z in (0,1,2,3): stack += latitude(1105, z)
Nst=len(stack); Est=Eplus(stack)
# product set C x {0,1,2,3}: E_+ = E_+(C) * E_+(AP4); AP4 energy = 44
E_C = Eplus([(x,y,0) for (x,y) in gauss_circle(1105)])
E_AP4 = Eplus([(0,0,z) for z in (0,1,2,3)])
claim("A2_L4_stack_product_and_bound",
      Nst==432 and Est==E_C*E_AP4 and Est <= 3*16*Nst*Nst,
      f"1105-circle at z=0,1,2,3 (L=4): N={Nst}, E_+={Est} = E_+(C)*E_+(AP4)={E_C}*{E_AP4}; "
      f"3 L^2 N^2 = {3*16*Nst*Nst}, ratio E_+/N^2={Est/Nst**2:.2f} (<= 48 bound w/ margin)")

# (A3) L=3 distinct-radius union (no global alignment)
uni = latitude(65,0) + latitude(85,40) + latitude(125,90)   # 65,85,125 all rich Gaussian radii
Nu=len(uni); Eu=Eplus(uni)
claim("A3_L3_distinct_radius_union_bound",
      Eu <= 3*9*Nu*Nu,
      f"radii 65@z0,85@z40,125@z90 (L=3): N={Nu}, E_+={Eu}, 3 L^2 N^2={3*9*Nu*Nu}, "
      f"ratio E_+/N^2={Eu/Nu**2:.2f} (<= 27 bound)")

# (A4) per-pair lemma: distinct radii => max multiplicity <= 2 (two circles meet in <=2 pts)
A = latitude(1105,0); B = latitude(65,10)
valsAB, _ = Erect_maxmult(A,B)
claim("A4_pairlemma_distinct_radius_mult_le2",
      valsAB[0] <= 2,
      f"r_AB(m) for distinct-radius circles 1105@z0 x 65@z10: max multiplicity = {valsAB[0]} (<= 2, "
      f"the two-circles-meet-in-<=2-points bound; no aligned m_0)")

# (A5) per-pair lemma: single circle => exactly one aligned m_0 with mult=N, rest <= 2
S5 = latitude(1105,5)
valsS5,_ = Erect_maxmult(S5,S5)
n_big = sum(1 for v in valsS5 if v>2)
claim("A5_pairlemma_single_circle_one_m0",
      n_big==1 and valsS5[0]==len(S5) and valsS5[1] <= 2,
      f"single 1105-latitude@z=5: exactly {n_big} sum m_0 with r>2; r(m_0)={valsS5[0]}=N "
      f"(center-reflection pairs at m_0=2*center=(0,0,10)); next largest r={valsS5[1]} (<= 2)")

# (A6) [NEST-DEPTH] witness benign: lacunary on great circle, depth grows, E_+/N^2 bounded
rows=[]
for J in (4,5,6,7):
    P, depth, s = lacunary_great_circle(J)
    N=len(P); E=Eplus(P)
    rows.append((J, N, depth, E, E/(N*N), s))
ratios=[r[4] for r in rows]; depths=[r[2] for r in rows]
depth_grows = all(depths[i] < depths[i+1] for i in range(len(depths)-1))
ratio_bounded = all(rr <= 3.0 for rr in ratios)
ratio_flat = abs(ratios[-1]-ratios[0]) <= 0.30      # ratio ~ 2 - 1/N, essentially depth-independent
claim("A6_nestdepth_witness_benign",
      depth_grows and ratio_bounded and ratio_flat,
      "lacunary witness on great circle (L=1): " +
      "; ".join(f"J={J} N={N} depth={d} E_+/N^2={rr:.3f}" for (J,N,d,E,rr,s) in rows) +
      f" -- depth grows {depths} while E_+/N^2 stays <= 3 (theorem L=1) and ~flat: depth-INDEPENDENT energy")

# (A7) estimator audit: brute O(N^4) == Eplus on a small circle
small = latitude(5,0)        # x^2+y^2=25: 12 integer points
claim("A7_estimator_audit_brute",
      Eplus(small)==Eplus_brute(small),
      f"12-point circle (r=5): vectorized E_+={Eplus(small)} == brute O(N^4) count {Eplus_brute(small)}")

# (A8) theorem constant sanity across all configs: measured E_+ <= 3 L^2 N^2 always
configs = [("L1",1,N1,E1), ("L4stack",4,Nst,Est), ("L3uni",3,Nu,Eu)]
allbound = all(E <= 3*L*L*N*N for (_,L,N,E) in configs)
claim("A8_theorem_bound_holds_all_configs",
      allbound,
      "; ".join(f"{nm}: E_+={E} <= 3*{L}^2*{N}^2={3*L*L*N*N} (ratio/N^2={E/N**2:.2f})" for (nm,L,N,E) in configs))

# ---------------- persist JSON artefact ----------------
ok = all(c["passed"] for c in CLAIMS)
out = REPO/"claims"/"B5-BEYOND-LAYER-BOUND"/"runs"/"260614-dr2-t030-fewcircles"
out.mkdir(parents=True, exist_ok=True)
(out/"result.json").write_text(json.dumps(dict(
    script="dr2_t030_fewcircles.py", version=__version__,
    theorem="E_+(Q) <= 3 L^2 N^2 for Q covered by L circles",
    single_circle=dict(N=N1, Eplus=E1, ratio=E1/N1**2, R033_published=34668),
    L4_stack=dict(N=Nst, Eplus=Est, E_C=E_C, E_AP4=E_AP4, bound=3*16*Nst*Nst),
    L3_union=dict(N=Nu, Eplus=Eu, bound=3*9*Nu*Nu),
    pair_distinct_maxmult=valsAB[0],
    pair_single_m0=dict(n_big=n_big, r_m0=valsS5[0], next=valsS5[1]),
    nestdepth_witness=[dict(J=J,N=N,depth=d,Eplus=E,ratio=rr) for (J,N,d,E,rr,s) in rows],
    verdict="few-circles theorem PROVED unconditional; DR-2 closed for L<=N^eps class; "
            "[NEST-DEPTH] witness benign at L=1 (technique-only); open core = super-poly-many circles",
    claims=CLAIMS, all_pass=ok), indent=2, default=str))
print(f"\nfew-circles bound verified; [NEST-DEPTH] witness benign at L=1")
print(f"claims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
