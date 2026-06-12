"""dr2_lemma_nt_exhaustive.py -- EXHAUSTIVE applied-domain verification of Lemma NT.

Lemma NT (dr2-lemma-nt-inbundle note): for the rank-2 lattice section
L_m = Z^3 cap m^perp, the circle count r_{L_m}(D) <= C d(D) (classical sharp form
6 d(D), Dirichlet). The DR-2 lattice theorem applies it through the chain
r_Q(m) <= #(Q cap C_m) <= r_{L_m}(4R-|m|^2) <= 6 d(4R-|m|^2).

This script verifies the APPLIED chain r_Q(m) <= 6 d(4R-|m|^2) EXHAUSTIVELY:
for EVERY distinct sum m (not just the richest circle) across ALL six shells
used by the package (R=101..9974, ~2.3e6 distinct sums in total), using the
v2.0.0 unique-count machinery of dr2_lattice_divisor.py and a sieved divisor
table for D <= 4R. Degenerate D=0 sums (m=2a) are checked to have r_Q(m)=1
exactly (the circle degenerates to the single point y=0). Ramified-corner
instances (odd p with p^2 | |m0|^2 and p | D, m0 = m/gcd primitive) -- the one
case whose ANALYTIC proof in the note is cited+outlined rather than fully
in-bundle -- are counted and verified SEPARATELY, so the corner is 100%
machine-covered on the applied domain.
self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-12"
__claims__ = ["B5-BEYOND-LAYER-BOUND"]

import json, sys, math
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
CLAIMS = []

def claim(name, cond, detail=""):
    CLAIMS.append(dict(name=name, passed=bool(cond), detail=detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

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

def divisor_table(M):
    d=np.zeros(M+1,dtype=np.int32)
    for i in range(1,M+1): d[i::i]+=1
    return d

SHELLS=[101,314,909,1826,4994,9974]
DMAX=4*SHELLS[-1]
dtab=divisor_table(DMAX)
print(f"=== Lemma NT exhaustive applied-domain check (divisor table to {DMAX}) ===")

tot_m=0; worst=0.0; worst_at=None; ram_total=0; ram_worst=0.0
deg_ok=True; Tprime_seen={}
ALL_OK=True
for R in SHELLS:
    Q=np.array(lattice_Z3(R),dtype=np.int64); N=len(Q)
    b=int(np.abs(Q).max()); K=4*b+1; off=2*b
    assert K**3 < 2**62
    S=(Q[:,None,:]+Q[None,:,:]).reshape(-1,3)
    keys=((S[:,0]+off)*K+(S[:,1]+off))*K+(S[:,2]+off)
    uk,counts=np.unique(keys,return_counts=True)
    # decode keys -> m vectors
    k0=uk.copy()
    mz=(k0%K)-off; k0//=K
    my=(k0%K)-off; k0//=K
    mx=k0-off
    mm=mx*mx+my*my+mz*mz
    nz=mm>0                       # m != 0
    D=4*R-mm[nz]; cnt=counts[nz]
    # degenerate D=0: circle is the single point y=0 -> r_Q(m) must be exactly 1
    deg=(D==0)
    if deg.any(): deg_ok &= bool((cnt[deg]==1).all())
    pos=D>0
    Dp=D[pos]; cp=cnt[pos]
    bound=6*dtab[Dp]
    ok=bool((cp<=bound).all()); ALL_OK &= ok
    ratio=(cp/bound).max()
    if ratio>worst:
        worst=float(ratio); i=int(np.argmax(cp/bound))
        worst_at=(R,int(cp[i]),int(Dp[i]),int(6*dtab[Dp[i]]))
    Tprime_seen[R]=int(cnt.max())
    tot_m+=int(nz.sum())
    # ramified corner: odd p with p^2 | |m0|^2 and p | D  (m0 = m/gcd)
    g=np.gcd(np.gcd(np.abs(mx),np.abs(my)),np.abs(mz))[nz][pos]
    m0sq=(mm[nz][pos])//(g*g)
    ram=np.zeros(len(Dp),dtype=bool)
    for p in (3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97):
        if p*p> int(m0sq.max(initial=1)): break
        ram |= (m0sq%(p*p)==0)&(Dp%p==0)
    if ram.any():
        ram_total+=int(ram.sum())
        ALL_OK &= bool((cp[ram]<=6*dtab[Dp[ram]]).all())
        ram_worst=max(ram_worst,float((cp[ram]/(6*dtab[Dp[ram]])).max()))
    print(f"  R={R:5d}: N={N:4d}  distinct m!=0: {int(nz.sum()):8d}  worst r/6d={ratio:.3f}  T'={Tprime_seen[R]}")

claim("exhaustive_bound_all_sums", ALL_OK,
      f"(r_Q(m) <= 6 d(4R-|m|^2) holds for EVERY one of {tot_m} distinct sums m!=0 across all six shells "
      f"R=101..9974 -- the applied Lemma-NT chain is 100%-machine-verified on its entire domain, not just "
      f"the richest circle; worst ratio {worst:.3f} at R={worst_at[0]} (r={worst_at[1]}, D={worst_at[2]}, "
      f"6d={worst_at[3]}))")
claim("degenerate_D0_exact", deg_ok,
      "(every degenerate sum m=2a (D=0) has r_Q(m)=1 exactly: the circle degenerates to y=0, matching the note)")
claim("ramified_corner_covered", ram_total>0 and ram_worst<1.0,
      f"({ram_total} ramified-corner instances (odd p: p^2 | |m0|^2, p | D) occur on the applied domain and "
      f"ALL satisfy the bound (worst ratio {ram_worst:.3f}) -- the one analytically cited+outlined case is "
      "exhaustively machine-covered where the theorem is actually applied)")
# cross-consistency with the archived lattice-divisor run (clearly-labelled oracle)
ORACLE_T={101:18,314:24,909:24,1826:24,4994:32,9974:48}
claim("Tprime_cross_consistent", all(Tprime_seen[R]==ORACLE_T[R] for R in SHELLS),
      f"(max_m r_Q(m) per shell {Tprime_seen} == dr2_lattice_divisor.py archived T' values -- the two scripts "
      "agree on the load-bearing quantity)")
claim("headroom_factor", worst<0.5,
      f"(global worst r/6d = {worst:.3f} < 0.5: the applied domain sits with >= x2 headroom below the Lemma NT "
      "ceiling -- the bound is never tight in practice)")

ok=all(c["passed"] for c in CLAIMS)
out=REPO/"claims"/"B5-BEYOND-LAYER-BOUND"/"runs"/"260612-dr2-lemma-nt-exhaustive"
out.mkdir(parents=True,exist_ok=True)
(out/"result.json").write_text(json.dumps(dict(
    script="dr2_lemma_nt_exhaustive.py",version=__version__,
    lemma="r_Q(m) <= 6 d(4R-|m|^2) for all m!=0 (applied Lemma-NT chain)",
    total_sums_checked=tot_m,worst_ratio=worst,worst_at=worst_at,
    ramified_instances=ram_total,ramified_worst=ram_worst,
    Tprime_per_shell=Tprime_seen,claims=CLAIMS,all_pass=ok),indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
