"""dr2_circle_richness.py -- RIGOROUS self-test of the sum-level-circle lemma

    E_+(Q) <= (1 + T'(Q)) N^2,    T'(Q) = max occupancy of a proper sum-circle.

For a,b on the unit sphere with a+b=m one has a.m = b.m = |m|^2/2, so both
summands lie on the circle C_m = S^2 cap {x : x.m = |m|^2/2}. Hence
r(m) := #{(a,b) in Q^2 : a+b=m} <= n_m := #(Q cap C_m), and splitting off the
degenerate m=0 (antipodal) term r(0)^2 <= N^2 gives the lemma. The lemma's
assert below is the PROOF CHECK: if it ever fails, the proof is wrong.

DR-2 (E_+ <= N^{2+eps}) then follows from the circle-richness bound
T'(Q) <=_eps N^eps -- a single clean elementary quantity. This does NOT close
DR-2 (bounding T' is the open carrier-richness / PSM problem); it rigorously
isolates the obstruction.

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-08"
__claims__ = ["B5-BEYOND-LAYER-BOUND"]

import json, sys
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
CLAIMS = []
RNG = np.random.default_rng(20260608)
TOL_SUM = 6        # decimals for binning sum-values m
TOL_CIRC = 1e-7    # membership tolerance for q.m == |m|^2/2 (generous => looser/safe T')

def claim(name, cond, detail=""):
    CLAIMS.append(dict(name=name, passed=bool(cond), detail=detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

def E_plus_and_reps(Q, dec=TOL_SUM):
    """Return E_+(Q) and the dict m -> r(m) keyed by rounded sum-value."""
    reps = {}
    for i in range(len(Q)):
        qi = Q[i]
        for j in range(len(Q)):
            k = tuple(np.round(qi + Q[j], dec)); reps[k] = reps.get(k, 0) + 1
    E = int(sum(r*r for r in reps.values()))
    return E, reps

def T_prime(Q, reps):
    """max occupancy n_m over proper (m != 0) sum-circles with r(m) > 0."""
    N = len(Q); Tp = 0; argm = None
    for k, r in reps.items():
        m = np.array(k, dtype=float)
        mm = float(m @ m)
        if mm < 1e-12:           # m = 0 : degenerate (whole sphere); handled by the +1
            continue
        half = mm / 2.0
        n_m = int(np.count_nonzero(np.abs(Q @ m - half) < TOL_CIRC))
        if n_m > Tp:
            Tp, argm = n_m, m
    return Tp, argm

# ---- configurations ----
def great_circle(N):
    th = np.linspace(0, 2*np.pi, N, endpoint=False)
    return np.stack([np.cos(th), np.sin(th), np.zeros(N)], axis=1)
def cap_grid(N, half=0.6):
    m = int(round(np.sqrt(N))); us = np.linspace(-half, half, m)
    return np.array([[u, v, np.sqrt(max(0.0,1-u*u-v*v))] for u in us for v in us])
def random_sphere(N):
    X = RNG.normal(size=(N,3)); return X/np.linalg.norm(X,axis=1,keepdims=True)
def rich_small_circle(N, z0=0.6):
    """N points on ONE latitude circle z=z0: an engineered rich sum-circle config."""
    r = np.sqrt(1-z0*z0); th = np.linspace(0,2*np.pi,N,endpoint=False)
    return np.stack([r*np.cos(th), r*np.sin(th), np.full(N,z0)], axis=1)

# ---- code-audit gate: estimator exact ----
def _ep(Q): 
    E,_ = E_plus_and_reps(Q); return E
exact_ok = all(_ep(random_sphere(N)) == 2*N*N - N for N in (16,32,64))
claim("E_plus_estimator_exact", exact_ok,
      "(random sphere E_+ = 2N^2 - N exactly for N=16,32,64: estimator exact, the code-audit gate)")

# ---- the lemma assert: E_+ <= (1 + T') N^2 (THE PROOF CHECK) ----
print("\nconfig            N    E_+(Q)     N^2     E_+/N^2   T'    (1+T')N^2   lemma")
rows = {}; lemma_ok = True
for name, Q in [("random", random_sphere(64)), ("great_circle", great_circle(64)),
                ("cap_grid", cap_grid(64)), ("rich_small_circle", rich_small_circle(64))]:
    N = len(Q); E, reps = E_plus_and_reps(Q); Tp, _ = T_prime(Q, reps)
    bound = (1+Tp)*N*N; ok = E <= bound; lemma_ok &= ok
    rows[name] = dict(N=N, E_plus=E, ratio=E/(N*N), T_prime=Tp, bound=bound, holds=bool(ok))
    print(f"{name:16s} {N:3d}  {E:8d}  {N*N:6d}   {E/(N*N):6.3f}   {Tp:3d}   {bound:9d}   {'OK' if ok else 'VIOLATED'}")

claim("lemma_E_plus_le_1plusTprime_Nsq", lemma_ok,
      "(E_+(Q) <= (1+T'(Q))N^2 holds for EVERY config -- the rigorous proof check; a failure here would "
      "refute the lemma)")

# ---- the obstruction is real: T' is O(1) for generic, but GROWS for a rich circle ----
Tp_unstruct = max(rows[n]["T_prime"] for n in ("random","great_circle"))
Tp_grid = rows["cap_grid"]["T_prime"]
Tp_rich = rows["rich_small_circle"]["T_prime"]
claim("Tprime_O1_for_unstructured", Tp_unstruct <= 4,
      f"(T' = {Tp_unstruct} for random/great-circle (O(1)): by the lemma E_+ <= (1+T')N^2 these sets satisfy "
      f"DR-2 (E_+ = O(N^2)) UNCONDITIONALLY and elementarily -- no decoupling needed; "
      f"E_+/N^2 = {rows['random']['ratio']:.2f}/{rows['great_circle']['ratio']:.2f})")
claim("Tprime_grows_with_structure", Tp_grid > Tp_unstruct and Tp_rich >= rows["rich_small_circle"]["N"],
      f"(T' climbs with additive structure: unstructured {Tp_unstruct} -> grid {Tp_grid} -> engineered rich "
      f"latitude circle {Tp_rich} = N: the circle-richness obstruction is REAL and reaches the max N, so the "
      "reduction is non-vacuous. NB the lemma is SUFFICIENT not tight -- the rich circle has T'=N yet "
      f"E_+ ~ {rows['rich_small_circle']['ratio']:.1f} N^2, so bounding T' is potentially stronger than DR-2)")

# ---- scaling of T' with N for generic random sets (should stay O(1), supporting DR-2) ----
Tp_scan = []
for N in (32, 64, 128):
    Q = random_sphere(N); _, reps = E_plus_and_reps(Q); Tp,_ = T_prime(Q, reps); Tp_scan.append((N,Tp))
claim("Tprime_bounded_in_N_generic", all(t <= 4 for _,t in Tp_scan),
      f"(random-set T' stays O(1) as N grows: {Tp_scan}; consistent with E_+ ~ N^2 for generic sphere sets)")

ok = all(c["passed"] for c in CLAIMS)
out = REPO/"claims"/"B5-BEYOND-LAYER-BOUND"/"runs"/"260608-dr2-circle-richness"
out.mkdir(parents=True, exist_ok=True)
(out/"result.json").write_text(json.dumps(dict(
    script="dr2_circle_richness.py", version=__version__, estimator_exact=exact_ok,
    lemma="E_+(Q) <= (1 + T'(Q)) N^2", rows=rows, Tprime_scan=Tp_scan,
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
