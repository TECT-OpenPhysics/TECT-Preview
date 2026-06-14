"""dr2_t030_sidon_decoupling.py -- T-030 / R-041 (R-033 advance): Sidon-height
latitude unions obey E_+ <= 6 N^2 (PROVED, incidence-free), upgrading R-040's
EMPIRICAL O(N^2) to a theorem for Sidon heights. The non-Sidon residual is genuinely
height-aware (it does NOT reduce to a bounded 2D concentric-circle energy) -- the
open incidence frontier (R-033).

THEOREM (Sidon heights, proved). Q = union of L latitude circles (ANY radii) at heights z_i forming a SIDON
set. Then E_+(Q) <= 6 N^2. (The Sidon condition is on the HEIGHTS only; distinct
radii are NOT required -- contrast R-040, whose (2p_max+1)N^2 bound needs distinct radii.)
Proof. In E_+=#{(a,b,c,d):a+b=c+d}, the height equation z_a+z_b=z_c+z_d + Sidon =>
{z_a,z_b}={z_c,z_d}, i.e. the circle-index multiset {i_a,i_b}={i_c,i_d}. Indexing by
the ordered pair (i_a,i_b), the matched (i_c,i_d) in {(i_a,i_b),(i_b,i_a)} (<=2
arrangements). Each arrangement's in-plane count is a rectangular energy
E_+(C_i,C_j) (arrangement (i,j,i,j)) or a difference-correlation corr(C_i,C_j)
(arrangement (i,j,j,i)); both are <= 3 nu_i nu_j (R-021 / Cauchy-Schwarz with
E_+(C)<=3 nu^2). Summing over ordered (i,j): E_+ <= sum_{i,j} [E_+(C_i,C_j) +
corr(C_i,C_j)] <= 6 sum_{i,j} nu_i nu_j = 6 N^2.  QED
(NOTE: the proved constant is 6, not 3 -- BOTH index-arrangements contribute; the
measured value is ~2.6 N^2. The non-Sidon case keeps mismatched-height quadruples
that are NOT captured by within-pair energies and do NOT reduce to a bounded 2D
concentric-circle energy -- that 2D energy grows with L -- so heights are essential
and the residual is the height-aware incidence problem of R-033.)

self-test asserts (exact integer arithmetic); exit 0 iff all pass.
"""
__version__ = "1.1.0"
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
def Eplus2D(P):
    c=Counter()
    for a in P:
        for b in P: c[(a[0]+b[0],a[1]+b[1])]+=1
    return sum(v*v for v in c.values())
def Erect(A,B):                   # rectangular E_+(A,B) = sum_m (#{a+b=m})^2 = (i,j,i,j)
    c=Counter()
    for a in A:
        for b in B: c[(a[0]+b[0],a[1]+b[1],a[2]+b[2])]+=1
    return sum(v*v for v in c.values())
def corr(A,B):                    # (i,j,j,i): #{a,d in A, b,c in B: a+b=c+d} = sum_v dd_A(v) dd_B(v)
    dA=Counter(); dB=Counter()
    for a in A:
        for d in A: dA[(a[0]-d[0],a[1]-d[1],a[2]-d[2])]+=1
    for b in B:
        for c in B: dB[(c[0]-b[0],c[1]-b[1],c[2]-b[2])]+=1
    return sum(dA[v]*dB[v] for v in dA if v in dB)
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
def mismatched(Q):
    sums={}
    for a in Q:
        for b in Q:
            s=(a[0]+b[0],a[1]+b[1],a[2]+b[2]); hm=tuple(sorted((a[2],b[2])))
            sums.setdefault(s,Counter())[hm]+=1
    v=0
    for s,hmc in sums.items():
        n=sum(hmc.values()); v+= n*n - sum(x*x for x in hmc.values())
    return v

# (A1) Sidon decoupling exact: 0 mismatched-height quadruples
hs=mian_chowla(6); Q=flat(by_circle(hs)); N=len(Q)
claim("A1_sidon_decoupling_exact", mismatched(Q)==0,
      f"Sidon L=6 N={N}: #{{a+b=c+d with mismatched height-pair}} = {mismatched(Q)} == 0 (height-pairing decouples)")

# (A2) Sidon => E_+ <= 6 N^2 (PROVED bound); report measured
rows=[]
for L in (2,3,4,5,6,7,8):
    hs=mian_chowla(L); Q=flat(by_circle(hs)); N=len(Q); E=Eplus(Q); rows.append((L,N,E,E/(N*N)))
claim("A2_sidon_le_6Nsq", all(E<=6*N*N for (L,N,E,r) in rows),
      "Sidon: " + "; ".join(f"L={L} E_+/N^2={r:.2f}" for (L,N,E,r) in rows) + " (all <= 6 PROVED; measured ~2.6)")

# (A3) the proved decomposition: E_+ <= sum_{i,j}[E_+(C_i,C_j)+corr(C_i,C_j)] <= 6N^2
hs=mian_chowla(5); bc=by_circle(hs); Q=flat(bc); N=len(Q); E=Eplus(Q)
S=0
for A in bc:
    for B in bc: S+=Erect(A,B)+corr(A,B)
claim("A3_arrangement_bound", E<=S<=6*N*N,
      f"Sidon L=5: E_+={E} <= sum_(i,j)[E_+(C_i,C_j)+corr] = {S} <= 6N^2={6*N*N} (both arrangements; each term <= 3 nu_i nu_j)")

# (A4) non-Sidon (AP) residual: mismatched quadruples > 0 (the open part)
ha=list(range(5)); Qa=flat(by_circle(ha))
claim("A4_nonsidon_residual", mismatched(Qa)>0,
      f"AP heights L=5: #{{mismatched-height quadruples}} = {mismatched(Qa)} > 0 -- non-Sidon residual (height-aware; not captured by within-pair energies)")

# (A5) heights ESSENTIAL: the 2D concentric-circle energy GROWS with L (so the residual
#      does NOT reduce to a bounded 2D concentric energy; the 3D heights suppress it)
crows=[]
for L in (2,4,6,8):
    P=[]
    for i in range(L): P+=circle_pts(RADII[i])
    M=len(P); crows.append((L,M,Eplus2D(P)/(M*M)))
grows=crows[-1][2] > crows[0][2] + 1.0
claim("A5_heights_essential_2D_grows", grows,
      "2D concentric-circle energy E2/N^2 = " + ", ".join(f"{r:.2f}" for (L,M,r) in crows) +
      " GROWS with L -> the residual is height-AWARE (3D heights suppress what 2D overcounts); not a bounded 2D reduction")

# (A6) R-033 consistency: all Sidon configs satisfy E_+ <= 3 N^{9/4}
claim("A6_R033_consistency", all(E<=3*N**2.25 for (L,N,E,r) in rows),
      "all Sidon configs satisfy E_+ <= 3 N^{9/4} (R-033 record consistency)")

# (A7) RADIUS-AGNOSTIC: equal-radius circles + SIDON heights also obey E_+ <= 6 N^2
#      (the Sidon decoupling depends only on heights, not radii)
hs7=mian_chowla(6)
Qeq=[]
for z in hs7: Qeq+=[(x,y,z) for (x,y) in circle_pts(25)]   # ALL radius 25, Sidon heights
Neq=len(Qeq); Eeq=Eplus(Qeq); mis_eq=mismatched(Qeq)
claim("A7_sidon_radius_agnostic", mis_eq==0 and Eeq<=6*Neq*Neq,
      f"EQUAL-radius (r=25) + Sidon heights L=6 N={Neq}: mismatched={mis_eq}==0, E_+={Eeq} <= 6N^2={6*Neq*Neq} "
      f"(E_+/N^2={Eeq/(Neq*Neq):.2f}) -- the Sidon bound is RADIUS-AGNOSTIC (no distinct-radius needed)")

ok=all(c["passed"] for c in CLAIMS)
out=REPO/"claims"/"B5-BEYOND-LAYER-BOUND"/"runs"/"260614-dr2-t030-sidon-decoupling"
out.mkdir(parents=True,exist_ok=True)
(out/"result.json").write_text(json.dumps(dict(
  script="dr2_t030_sidon_decoupling.py",version=__version__,
  theorem="Sidon heights => E_+ <= 6 N^2 (PROVED, incidence-free; height decoupling + R-021, two arrangements)",
  sidon=[dict(L=L,N=N,Eplus=E,E_over_N2=r) for (L,N,E,r) in rows],
  concentric_2D_ratio=[dict(L=L,N=M,E_over_N2=r) for (L,M,r) in crows],
  verdict="Sidon-height latitude unions PROVED E_+ <= 6 N^2 (incidence-free), upgrading R-040 empirical to theorem "
          "for Sidon; non-Sidon residual is height-aware (2D concentric energy grows with L, so no bounded 2D "
          "reduction) = the R-033 circle-incidence frontier",
  claims=CLAIMS,all_pass=ok),indent=2,default=str))
print(f"\nSidon heights => E_+ <= 6 N^2 PROVED (incidence-free); non-Sidon residual = height-aware incidence (R-033)")
print(f"claims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
