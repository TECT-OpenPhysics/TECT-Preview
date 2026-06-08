"""dr2_cross_energy_lemma.py -- Tier-3 verification of the cross-energy lemma used
in the DR-2 (sphere additive-energy) reduction, WITH a devil's-advocate correction
to the external research's stated constant.

For finite point sets A, B on circles on the unit sphere S^2, define the
representation function r_P(w) = #{(p,p') in P^2 : p-p' = w} and the cross
additive energy E_+(A,B) = #{(a,a',b,b') : a+b = a'+b'} = sum_w r_A(w) r_B(-w).

RIGOROUS CORE (universal, any circles, parallel or not): for w != 0,
    r_P(w) <= 2,
because a circle C and its translate C+w meet in at most two points
(C ∩ (C+w) has <= 2 points). At w = 0, r_P(0) = |P| (the diagonal), NOT <= 2.

CORRECTION to the external research (Math447-469, Pass 4). That pass states
E_+(A,B) <= 2|A||B|, applying r <= 2 to ALL w including w = 0. That over-counts:
the w = 0 term contributes r_A(0) r_B(0) = |A||B|, which is NOT <= 2. The clean
universal bound is on the OFF-DIAGONAL energy
    E_off(A,B) := E_+(A,B) - |A||B|
                = sum_{w != 0} r_A(w) r_B(-w)
                <= 2 sum_{w != 0} r_A(w)
                =  2 (|A|^2 - |A|),
and symmetrically <= 2(|B|^2 - |B|). Hence
    E_off(A,B) <= 2 min(|A|^2-|A|, |B|^2-|B|),   (rigorous, universal)
    E_+(A,B)   <= |A||B| + 2 min(|A|^2-|A|, |B|^2-|B|) <= 3|A||B|.
So the qualitative bound E_+(A,B) = O(|A||B|) STANDS; only the external constant
2 (for the FULL energy) is corrected to 3, and the load-bearing object for the
DR-2 cluster-decomposition reduction is E_off with constant 2. The structured
witness below (A = B = 16 equally-spaced great-circle points, E_+ = 720) FALSIFIES
the literal "E_+ <= 2|A||B| = 512" and CONFIRMS E_off = 464 <= 480 = 2(|A|^2-|A|).

self-test asserts (exit 0 iff all pass) cover every numerical claim.
"""
__version__ = "1.1.0"
__first_issued__ = "2026-06-08"
__claims__ = ["B5-BEYOND-LAYER-BOUND"]

import json, sys
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
CLAIMS = []

def claim(name, cond, detail=""):
    CLAIMS.append(dict(name=name, passed=bool(cond), detail=detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

def circle_points(normal, h, thetas):
    n = np.asarray(normal, float); n = n / np.linalg.norm(n)
    a = np.array([1.0, 0.0, 0.0]) if abs(n[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    e1 = a - (a @ n) * n; e1 /= np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    rho = float(np.sqrt(max(0.0, 1.0 - h * h)))
    return np.array([h * n + rho * (np.cos(t) * e1 + np.sin(t) * e2) for t in thetas])

def bin_key(v, dec=8):
    return tuple(np.round(v, dec))

def r_max_offdiag(P):
    cnt = {}
    for i in range(len(P)):
        for j in range(len(P)):
            if i == j:
                continue
            k = bin_key(P[i] - P[j]); cnt[k] = cnt.get(k, 0) + 1
    return max(cnt.values()) if cnt else 0

def E_plus(A, B):
    cnt = {}
    for a in A:
        for b in B:
            k = bin_key(a + b); cnt[k] = cnt.get(k, 0) + 1
    return int(sum(c * c for c in cnt.values()))

m = 16
unif = np.linspace(0, 2 * np.pi, m, endpoint=False)
configs = {
    "non_parallel": (circle_points([0, 0, 1], 0.3, unif), circle_points([1, 1, 0], 0.1, unif + 0.137)),
    "parallel_same_plane": (circle_points([0, 0, 1], 0.3, unif), circle_points([0, 0, 1], 0.3, unif + 0.21)),
    "parallel_diff_plane": (circle_points([0, 0, 1], 0.3, unif), circle_points([0, 0, 1], -0.4, unif + 0.05)),
    "structured_witness": (circle_points([0, 0, 1], 0.0, unif), circle_points([0, 0, 1], 0.0, unif)),  # A=B great circle
}

print("config                |A| |B|  r_max(off)  E_+(full)  E_off   2*min(n^2-n)  2|A||B|(WRONG)  3|A||B|")
rows = {}
for name, (A, B) in configs.items():
    nA, nB = len(A), len(B)
    rmo = max(r_max_offdiag(A), r_max_offdiag(B))
    Ef = E_plus(A, B)
    Eoff = Ef - nA * nB
    bnd_off = 2 * min(nA * nA - nA, nB * nB - nB)
    bnd_wrong = 2 * nA * nB
    bnd_full = nA * nB + bnd_off
    rows[name] = dict(nA=nA, nB=nB, r_max_offdiag=rmo, E_plus_full=Ef, E_off=Eoff,
                      bound_offdiag=bnd_off, external_wrong_2nAnB=bnd_wrong, bound_full=bnd_full)
    print(f"{name:21s} {nA:3d} {nB:3d}    {rmo:3d}      {Ef:7d}  {Eoff:6d}    {bnd_off:7d}      {bnd_wrong:7d}        {bnd_full:6d}")

# (1) rigorous core
claim("r_offdiag_le_2", all(rows[n]["r_max_offdiag"] <= 2 for n in rows),
      "(r_P(w) <= 2 for every w != 0 on every test circle (parallel AND non-parallel): circle ∩ translate <= 2)")
# (2) corrected universal bound on the off-diagonal energy
claim("E_off_bound_universal", all(rows[n]["E_off"] <= rows[n]["bound_offdiag"] for n in rows),
      "(E_off(A,B) <= 2 min(|A|^2-|A|, |B|^2-|B|) for EVERY config, including the A=B great circle: the clean "
      "rigorous cross-energy bound)")
# (3) corrected full-energy bound
claim("E_full_bound_3nAnB", all(rows[n]["E_plus_full"] <= rows[n]["bound_full"] for n in rows),
      "(E_+(A,B) <= |A||B| + 2 min(|A|^2-|A|,...) <= 3|A||B| for every config: the corrected full-energy bound)")
# (4) the external constant-2 full-energy bound is FALSIFIED by the witness (the correction)
sw = rows["structured_witness"]
claim("external_2nAnB_falsified_by_witness", sw["E_plus_full"] > sw["external_wrong_2nAnB"],
      f"(structured witness E_+={sw['E_plus_full']} > 2|A||B|={sw['external_wrong_2nAnB']}: the external "
      "'E_+ <= 2|A||B|' (full energy) is off by the w=0 diagonal; corrected to E_off<=2min^2 / full<=3|A||B|)")
# (5) non-triviality
claim("offdiag_nontrivial", sw["E_off"] > 0,
      f"(structured witness E_off={sw['E_off']} > 0: additive coincidences occur, so the off-diagonal bound "
      "is a real constraint -- the witness sits at E_off=464 just under the ceiling 480)")
# (6) reduction-robustness: the qualitative O(|A||B|) is unaffected by the constant correction
claim("reduction_robust_O_nAnB", all(rows[n]["E_plus_full"] <= 3 * rows[n]["nA"] * rows[n]["nB"] for n in rows),
      "(every E_+ <= 3|A||B| = O(|A||B|): the DR-2 cluster-decomposition reduction (Cauchy-Schwarz cross-terms) "
      "is robust to the 2->3 constant correction)")

ok = all(c["passed"] for c in CLAIMS)
out = REPO / "claims" / "B5-BEYOND-LAYER-BOUND" / "runs" / "260608-dr2-cross-energy-lemma"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="dr2_cross_energy_lemma.py", version=__version__,
    correction="external Pass-4 'E_+ <= 2|A||B|' (full energy) is off by the w=0 diagonal; corrected: "
               "E_off <= 2 min(|A|^2-|A|, |B|^2-|B|), full E_+ <= 3|A||B|. Qualitative O(|A||B|) and the "
               "reduction are unaffected.",
    configs=rows, claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
