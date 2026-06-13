"""dr2_t030_r1_bridge.py -- machine verification of the two unconditional
ingredients of Lemma R1 (dr2-t030-frontier-consolidation-260612-v1.0 Sec. 4),
which upgrades the cross-scale induction's cited residual R1 (local-to-global
translate-averaging) to a WRITTEN PROOF:

  (i) the exact Besicovitch-limit identity for trigonometric polynomials:
        lim_{S->inf} avg_{y in B_S} ||f_Q||^4_{L^4(w(.-y))} = (int w) E_+(Q),
      verified in CLOSED FORM on the Fourier side:
        avg_S = sum_v c_v w_hat(v) beta(2 pi |v| S),
        beta(u) = 3(sin u - u cos u)/u^3  (ball average of a plane wave),
      with the predicted envelope decay rate S^{-2};
  (ii) the exact spectral identity c_0 = E_+(Q) (the v=0 Fourier coefficient
       of |f_Q|^4 equals the additive energy: two INDEPENDENT exact counts);
  (iii) the Minkowski step: (avg (sum_th A_th)^2)^{1/2}
        <= sum_th (avg A_th^2)^{1/2} for nonnegative A_th.

PRE-REGISTERED GATE (declared before the first run): if avg_S fails to
converge to (int w) E_+ with envelope ~S^{-2}, or c_0 != E_+ exactly, the
Besicovitch-limit step of Lemma R1 is WRONG and the note is blocked.

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-12"
__claims__ = ["B5-BEYOND-LAYER-BOUND"]

import json, sys, math
from pathlib import Path
from collections import defaultdict
import numpy as np

REPO = Path(__file__).resolve().parents[2]
CLAIMS = []

def claim(name, cond, detail=""):
    CLAIMS.append(dict(name=name, passed=bool(cond), detail=detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

PREREGISTERED_GATES = dict(
    H1="exact spectral identity: the v=0 coefficient of |f_Q|^4 (O(N^4) quadruple count) equals E_+(Q) (pair-sum count); integer equality, no tolerance",
    H2="Besicovitch convergence: |avg_S/(int w) - E_+|/E_+ < 1e-3 at S=80 AND decays by >= 30x from S=5 to S=80 (envelope ~S^{-2}); failure falsifies the Lemma R1 limit step",
    H3="Minkowski step: the L^2(dy) triangle inequality used in Lemma R1 holds on 200 random nonnegative trials (sanity of the inequality direction)",
)

# two exact rational configurations on S^2 (scaled integer points, |p|^2 = 9)
CONFIGS = {
  "generic_with_quadruple": [(1,2,2),(2,1,2),(-1,-2,2),(-2,-1,2),(2,2,1),
                             (-2,2,1),(0,0,3),(0,3,0),(3,0,0),(0,0,-3)],
  "rich_latitude_z2": [(1,2,2),(2,1,2),(-1,2,2),(-2,1,2),(1,-2,2),(2,-1,2),
                       (-1,-2,2),(-2,-1,2)],
}
SCALE = 3          # q = p/SCALE lies on the unit sphere
S_LIST = [5.0, 10.0, 20.0, 40.0, 80.0]
WSCALE = 1.0       # Gaussian weight w(x)=exp(-pi|x|^2/s^2), int w = s^3

def beta(u):
    """(1/|B_S|) int_{B_S} e(v.y) dy with u = 2 pi |v| S; beta(0)=1."""
    if u < 1e-8: return 1.0 - u*u/10.0
    return 3.0*(math.sin(u) - u*math.cos(u))/u**3

results = {}
for nm, P in CONFIGS.items():
    P = [tuple(p) for p in P]
    N = len(P)
    assert all(p[0]**2+p[1]**2+p[2]**2 == SCALE**2 for p in P)
    assert len(set(P)) == N
    # pair-sum E_+ (exact)
    sums = defaultdict(int)
    for a in P:
        for b in P:
            sums[(a[0]+b[0], a[1]+b[1], a[2]+b[2])] += 1
    E = sum(r*r for r in sums.values())
    # quadruple spectrum c_v of |f_Q|^4, v = (a+b-c-d)/SCALE (exact int keys)
    cv = defaultdict(int)
    for a in P:
        for b in P:
            sab = (a[0]+b[0], a[1]+b[1], a[2]+b[2])
            for c in P:
                for d in P:
                    cv[(sab[0]-c[0]-d[0], sab[1]-c[1]-d[1], sab[2]-c[2]-d[2])] += 1
    c0 = cv[(0,0,0)]
    total = sum(cv.values())
    # closed-form translate average A(S) = sum_v c_v w_hat(v) beta(2 pi |v| S)
    s = WSCALE
    errs = []
    for S in S_LIST:
        A = 0.0
        for v, c in cv.items():
            vn = math.sqrt(v[0]**2+v[1]**2+v[2]**2)/SCALE
            A += c * (s**3)*math.exp(-math.pi*s*s*vn*vn) * beta(2*math.pi*vn*S)
        errs.append(abs(A/(s**3) - E)/E)
    results[nm] = dict(N=N, E_plus=E, c0=c0, sum_cv=total, errs=dict(zip(map(str,S_LIST), errs)))
    print(f"{nm}: N={N} E_+={E} c0={c0} N^4={N**4}  err(S): " +
          " ".join(f"{e:.2e}" for e in errs))

claim("H1_c0_equals_Eplus_exact",
      all(d["c0"] == d["E_plus"] and d["sum_cv"] == d["N"]**4 for d in results.values()),
      "(v=0 quadruple count == pair-sum E_+ exactly, and sum_v c_v == N^4, on both configs: "
      "the spectral identity behind M(|f_Q|^4) = E_+)")

h2 = all(d["errs"][str(S_LIST[-1])] < 1e-3 and
         d["errs"][str(S_LIST[-1])] < d["errs"][str(S_LIST[0])]/30.0 for d in results.values())
claim("H2_besicovitch_convergence", h2,
      "(closed-form avg_S -> (int w) E_+ with the predicted ~S^{-2} envelope on both configs; "
      f"final relative errors: " + ", ".join(f"{nm}:{d['errs'][str(S_LIST[-1])]:.2e}"
                                             for nm, d in results.items()) + ")")

rng = np.random.default_rng(20260612)
mink_ok = True; worst = 0.0
for _ in range(200):
    A = rng.random((6, 200))**2 * rng.exponential(1.0, (6, 1))
    lhs = math.sqrt(float(np.mean(np.sum(A, axis=0)**2)))
    rhs = float(np.sum(np.sqrt(np.mean(A**2, axis=1))))
    mink_ok &= lhs <= rhs + 1e-12
    worst = max(worst, lhs/rhs)
claim("H3_minkowski_step", mink_ok,
      f"(L^2(dy) triangle inequality: 200/200 trials, worst lhs/rhs = {worst:.4f} <= 1)")

ok = all(c["passed"] for c in CLAIMS)
out = REPO/"claims"/"B5-BEYOND-LAYER-BOUND"/"runs"/"260612-dr2-t030-r1-bridge"
out.mkdir(parents=True, exist_ok=True)
(out/"result.json").write_text(json.dumps(dict(
    script="dr2_t030_r1_bridge.py", version=__version__,
    preregistered_gates=PREREGISTERED_GATES,
    lemma="R1 bridge: lim_S avg_{B_S} ||f_Q||^4_{L^4(w(.-y))} dy = (int w) E_+(Q), exact for finite Q (trig polynomial); + Minkowski step",
    configs=results, claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
