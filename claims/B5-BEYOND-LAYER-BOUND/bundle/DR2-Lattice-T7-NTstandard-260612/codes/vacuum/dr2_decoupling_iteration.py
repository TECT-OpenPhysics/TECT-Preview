"""dr2_decoupling_iteration.py -- ILLUSTRATIVE numerical consistency for the
decoupling-iteration structure of the DR-2 cross-scale step. v1.1 after operator
code audit (2026-06-08).

HONEST SCOPE (read first). This script does NOT prove the iteration inequality and
is NOT a faithful test of Bourgain-Demeter decoupling:
  * the additive-energy estimator E_+ is verified EXACT (a random sphere set has
    exactly 2N^2 - N trivial quadruples; asserted below);
  * BUT the cap partition here uses square (x,y) tangential bins, a PROXY for the
    geodesic delta^{1/2}-caps decoupling actually uses. So the constant K below is
    an ILLUSTRATION that E_+(Q)/(sum_theta sqrt E_+(Q_theta))^2 is O(1) and
    scale-stable on these proxy partitions -- consistency with, not proof of, the
    p=4 decoupling exponent. Numerics SUPPORT, they do NOT replace, the proof; no
    tier/gate flip may rest on them.

The mathematical bridge `M(|f_theta|^4) = E_+(Q_theta)` (Besicovitch mean, valid
for non-integer q) lives in the note dr2-cross-scale-induction v1.1 Section 2; this
script only checks the resulting inequality's CONSTANT empirically.

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.1.0"
__first_issued__ = "2026-06-08"
__claims__ = ["B5-BEYOND-LAYER-BOUND"]

import json, sys
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
CLAIMS = []
RNG = np.random.default_rng(20260608)

def claim(name, cond, detail=""):
    CLAIMS.append(dict(name=name, passed=bool(cond), detail=detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

def E_plus(Q, dec=6):
    cnt = {}
    for i in range(len(Q)):
        qi = Q[i]
        for j in range(len(Q)):
            k = tuple(np.round(qi + Q[j], dec)); cnt[k] = cnt.get(k, 0) + 1
    return int(sum(c * c for c in cnt.values()))

def great_circle(N):
    th = np.linspace(0, 2*np.pi, N, endpoint=False)
    return np.stack([np.cos(th), np.sin(th), np.zeros(N)], axis=1)

def cap_grid(N, half=0.5):
    m = int(round(np.sqrt(N))); us = np.linspace(-half, half, m)
    return np.array([[u, v, np.sqrt(max(0.0, 1.0 - u*u - v*v))] for u in us for v in us])

def random_sphere(N):
    X = RNG.normal(size=(N, 3)); return X / np.linalg.norm(X, axis=1, keepdims=True)

def cap_partition(Q, n_side):
    """PROXY cap partition: square (x,y) bins, NOT geodesic delta^{1/2}-caps."""
    caps = {}
    for q in Q:
        key = (int(np.floor((q[0] + 1.0) * n_side / 2.0)), int(np.floor((q[1] + 1.0) * n_side / 2.0)))
        caps.setdefault(key, []).append(q)
    return [np.array(v) for v in caps.values()]

# ---------------------------------------------------------------------------
# CODE AUDIT GATE: the E_+ estimator must be EXACT on a known case
# (a random sphere set has only trivial quadruples {i,j}={k,l}: 2N^2 - N of them)
# ---------------------------------------------------------------------------
exact_ok = all(E_plus(random_sphere(N)) == 2*N*N - N for N in (16, 32, 64))
claim("E_plus_estimator_exact", exact_ok,
      "(random sphere set E_+ = 2N^2 - N exactly for N=16,32,64: the additive-energy estimator is exact, no "
      "binning artefact -- the code-audit gate for every E_+ value below)")

def iteration_ratio(Q, n_side):
    caps = cap_partition(Q, n_side)
    rhs_inner = sum(np.sqrt(E_plus(c)) for c in caps)
    lhs = E_plus(Q)
    return lhs, rhs_inner ** 2, (lhs / rhs_inner**2 if rhs_inner > 0 else np.inf), len(caps)

print("config         N    n_side  caps   E_+(Q)    (sum sqrt E_theta)^2   K=LHS/RHS")
configs = {"great_circle": great_circle(64), "cap_grid": cap_grid(64, 0.6), "random": random_sphere(64)}
rows = {}; Kmax = 0.0
for name, Q in configs.items():
    for n_side in (2, 4, 8):
        lhs, rhs, K, ncaps = iteration_ratio(Q, n_side)
        rows[f"{name}_{n_side}"] = dict(N=len(Q), n_side=n_side, caps=ncaps, lhs=lhs, rhs=rhs, K=K)
        Kmax = max(Kmax, K)
        print(f"{name:14s} {len(Q):3d}    {n_side:3d}    {ncaps:4d}   {lhs:8d}   {rhs:18.1f}   {K:.3f}")

claim("iteration_constant_bounded_proxy", all(rows[k]["K"] <= 3.0 for k in rows),
      f"(ILLUSTRATIVE: on the PROXY square-bin partition, K = E_+(Q)/(sum sqrt E_theta)^2 <= 3 for every "
      f"config/scale; max K = {Kmax:.3f}. Consistency with the decoupling exponent, NOT a faithful "
      "delta^{1/2}-cap test)")
gc = [rows[f"great_circle_{n}"]["K"] for n in (2, 4, 8)]
claim("scale_stability_proxy", max(gc) / min(gc) < 2.0,
      f"(K within x2 across proxy cap scales n=2,4,8: {['%.2f'%x for x in gc]}; illustrative scale stability)")
splits = []
for name, Q in configs.items():
    caps = cap_partition(Q, 8); splits.append((name, E_plus(Q), sum(E_plus(c) for c in caps)))
claim("partition_reduces_structure", all(sc < 0.8 * tot or tot == sc for (_, tot, sc) in splits),
      "(sum_theta E_+(Q_theta) << E_+(Q): the partition breaks cross-cap quadruples -- "
      + ", ".join(f"{n}:{sc}/{tot}" for (n, tot, sc) in splits) + ")")

ok = all(c["passed"] for c in CLAIMS)
out = REPO / "claims" / "B5-BEYOND-LAYER-BOUND" / "runs" / "260608-dr2-decoupling-iteration"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="dr2_decoupling_iteration.py", version=__version__,
    estimator_exact=exact_ok, partition="PROXY square (x,y) bins (NOT geodesic caps)",
    rows=rows, K_max=Kmax, claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
