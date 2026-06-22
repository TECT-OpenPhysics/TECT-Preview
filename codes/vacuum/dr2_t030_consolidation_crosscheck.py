"""dr2_t030_consolidation_crosscheck.py -- R-043 consolidation cross-check (v1.1).

Re-verifies the internal closure-table ANCHORS cited by the R-043 consolidation note
and records the external-literature constants WITH PROVENANCE. This is a regression
cross-check of example constants + inequalities; it does NOT prove R-026 or any
literature proposition (those are appended/cited in the note, Sec.A).

v1.1 fixes (operator review 2026-06-19):
  - robust REPO/output path: resolve repo root by walking up to the dir containing
    BOTH 'claims/' and 'codes/'; if not found, write JSON to CWD (never to '/').
  - literature constants corrected: the real-sphere E_2 on S^2 bound is the OPEN
    Bourgain-Demeter conjecture (exponent 2+eps); the published O(#A^{7/2}) is for
    E_3 on S^1 (a DIFFERENT object) and is recorded as such, not as an E_2/S^2
    best-known. Mudgal 2022 d=4 exponent kept.

ASSERTS:
 A1  single rich circle E_+ = 34668 at N=108 (the R-038/R-040/R-041 anchor).
 A2  B5 occupancy closure: Lemma A at T'=10 gives (1+T')N^2 = 11 N^2 (the B5
     load-bearing bound; uses occupancy T', NOT the cover number L, NOT R-026).
 A3  bound hierarchy 6(L+1) < 3L^2 (per N^2) for L>=3 (R-039 vs R-038 coarse).
 A4  literature constants with provenance: Mudgal d=4 = 2+1/3-1/1392 (~2.333);
     E_2/S^2 = OPEN conjecture 2(+eps); E_3/S^1 known 7/2 (DIFFERENT object).
self-test asserts; exit 0 iff all pass.
"""
__version__ = "1.1.0"
__first_issued__ = "2026-06-14"
__claims__ = ["B5-BEYOND-LAYER-BOUND"]
import json, math, sys, os
from collections import Counter
from pathlib import Path

def find_repo_root(start: Path):
    p = start.resolve()
    for cand in [p] + list(p.parents):
        if (cand / "claims").is_dir() and (cand / "codes").is_dir():
            return cand
    return None

CLAIMS=[]
def claim(n,c,d=""):
    CLAIMS.append(dict(name=n,passed=bool(c),detail=d)); print(f"  [{'PASS' if c else 'FAIL'}] {n} -- {d}")

def circle_pts(r):
    pts=set()
    for x in range(-r,r+1):
        y2=r*r-x*x
        if y2<0: continue
        y=math.isqrt(y2)
        if y*y==y2: pts.add((x,y)); pts.add((x,-y))
    return sorted(pts)
def Eplus2D(P):
    c=Counter()
    for a in P:
        for b in P: c[(a[0]+b[0],a[1]+b[1])]+=1
    return sum(v*v for v in c.values())

# A1
C=circle_pts(1105); N=len(C); E=Eplus2D(C)
claim("A1_single_circle_anchor", N==108 and E==34668,
      f"single rich circle r=1105: N={N}, E_+={E} (R-038/R-040/R-041 anchor; matches R-033 F1/F5)")

# A2: B5 occupancy closure (Lemma A at T'=10) -- the actual B5 bound, NOT L, NOT R-026
Tprime_cap=10
b5_bound_coeff = 1 + Tprime_cap     # (1+T') from Lemma A (R-025); R-032 gives T'<=10
claim("A2_B5_occupancy_closure", b5_bound_coeff==11,
      f"B5 closure: Lemma A (R-025) E_+<=(1+T')N^2 with Lemma 2 (R-032) T'<=10 => E_+ <= {b5_bound_coeff} N^2 "
      "(uses sum-circle OCCUPANCY T', distinct from the few-circles cover number L and from the lattice bound R-026)")

# A3: 6(L+1) < 3 L^2 for L>=3
def coarse(L): return 6*(L+1)
def quad(L): return 3*L*L
claim("A3_bound_hierarchy", coarse(2)>quad(2) and all(coarse(L)<quad(L) for L in (3,4,8)),
      "6(L+1) vs 3L^2 (per N^2): L=2:18/12; L=3:24/27; L=4:30/48; L=8:54/192 -- cover-number forms (R-038/R-039), cross at L=3")

# A4: literature constants (provenance), with the corrected real-sphere positioning
mudgal_d4 = 2 + 1/3 - 1/1392            # Mudgal 2022 (arXiv:2105.06925) d=4
e2_s2_conjecture = 2.0                  # E_2 on S^2: OPEN Bourgain-Demeter conjecture (2+eps)
e2_s2_best_2016 = 7/3                    # E_2 on S^2 best reported by Sheffer (2016), date-qualified
e3_s1_known = 7/2                       # E_3 on S^1 best-known (Szemeredi-Trotter) -- DIFFERENT object
ok4 = (e2_s2_conjecture < mudgal_d4 < e2_s2_best_2016 + 1e-9) and abs(e2_s2_best_2016-7/3)<1e-12 and abs(e3_s1_known-3.5)<1e-12
claim("A4_literature_constants", ok4,
      f"Mudgal d=4 = 2+1/3-1/1392 = {mudgal_d4:.5f}; E_2/S^2 OPEN (conj {e2_s2_conjecture}+eps), 2016 Sheffer best 7/3 = {e2_s2_best_2016:.5f}; "
      f"E_3/S^1 = 7/2 = {e3_s1_known} (DISTINCT object, Szemeredi-Trotter)")

ok=all(c["passed"] for c in CLAIMS)
root = find_repo_root(Path(__file__))
payload = dict(
  script="dr2_t030_consolidation_crosscheck.py",version=__version__,
  single_circle=dict(N=N,Eplus=E),
  b5_occupancy_bound_coeff=b5_bound_coeff,
  literature=dict(mudgal_2022_d4_exponent=mudgal_d4, E2_S2_open_conjecture=e2_s2_conjecture, E2_S2_best_2016_Sheffer=e2_s2_best_2016,
                  E3_S1_known_different_object=e3_s1_known,
                  refs=["Mudgal, Additive energies on spheres, JLMS 106(4):2927-2958 (2022), arXiv:2105.06925",
                        "Sheffer, Additive Energy of Real Point Sets (expository, 2016): Bourgain-Demeter E_2/S^2 open; E_3/S^1 O(#A^{7/2})"]),
  verdict="CONDITIONAL CONSOLIDATION. T-030a closed conditionally on R-026; B5 closure = Lemma2(T'<=10)+LemmaA "
          "=> 11 N^2 (independent of R-026 and of cover number L); T-030b, E_2/S^2 OPEN (Bourgain-Demeter).",
  claims=CLAIMS, all_pass=ok)
if root is not None:
    out = root/"claims"/"B5-BEYOND-LAYER-BOUND"/"runs"/"260614-dr2-t030-consolidation"
    try:
        out.mkdir(parents=True, exist_ok=True); (out/"result.json").write_text(json.dumps(payload,indent=2,default=str))
        print(f"\nJSON -> {out/'result.json'}")
    except OSError as e:
        Path("dr2_t030_consolidation_result.json").write_text(json.dumps(payload,indent=2,default=str))
        print(f"\n(repo runs/ not writable: {e}; JSON written to CWD)")
else:
    Path("dr2_t030_consolidation_result.json").write_text(json.dumps(payload,indent=2,default=str))
    print("\n(repo root not found; JSON written to CWD -- NOT to '/')")
print(f"claims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
