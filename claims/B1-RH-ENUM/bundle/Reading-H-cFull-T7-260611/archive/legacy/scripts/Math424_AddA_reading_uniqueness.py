#!/usr/bin/env python3
"""Math424_AddA_reading_uniqueness.py -- Path A Step 1-4 implementation.

Constructs the explicit variational-Hartree TECT free-energy functional
F_var(A, r_hat; reading) for the four enumerated admissible readings of
Math424 Step 2 (LAM n=1, HEX n=3, FCC n=4, BCC n=6 single-shell condensates
vs Reading H disordered) and compares F_TECT[R] at the canonical operating
point mu^2 = +0.005 and across the Math400-AddE sweep window.

Conventions locked to Math400-AddE (theory-currency audit 2026-06-04):
    F[phi] = int d^3r [ (r/2) phi^2 + (c/2)((q^2-q0^2) structure) phi^2
                        + (u/4) phi^4 + (v/6) phi^6 ],
    r = mu^2 + Y q0^4,  c = Y = 1,  u = 2 lambda = -0.86,
    v = 2 gamma = +3.24,  q0 = 0.6801747616.

Single-shell ansatz (per-signed-vector amplitude convention):
    phi_n(x) = A * sum_{j=1}^{2n} exp(i k_j . x),   |k_j| = q0,  zero phases,
so cell averages <phi^m> = N_m A^m with N_m = #{ordered m-tuples of shell
vectors summing to zero} (exact integer enumeration below).

Variational (Gibbs-Bogoliubov / Hartree) free energy relative to the
disordered solution at the same mu^2 (M_hat = M(r_hat), M_R = M(r_R)):

  dF_n(A)/V = (1/2) dI(r_hat, r_R) - (1/2)(r_hat M_hat - r_R M_R)
            + (r/2)(2 n A^2 + M_hat - M_R) + 3 u n A^2 M_hat
            + (3u/4)(M_hat^2 - M_R^2) + (u/4) N4 A^4
            + (5v/2) N4 A^4 M_hat + 15 v n A^2 M_hat^2
            + (5v/2)(M_hat^3 - M_R^3) + (v/6) N6 A^6,

with the stationarity (gap) equation minimised over the isotropic trial mass
    r_hat = r + 3 u M + 15 v M^2 + 6 u n A^2 + 60 v n A^2 M + 5 v N4 A^4,
which reduces at A=0 to the Math400-AddE disordered gap equation
    r_R = r + 3 u M(r_R) + 15 v M(r_R)^2.

Self-tests (CLAUDE.md 6.3.8) cover every numerical claim of the Math note:
combinatorial N_m values (exact real-space cross-check), Math400-AddE
canonical reproduction, dF(0)=0 identity, gap residuals, and the headline
dF_n > 0 verdicts. Exits 0 only if ALL asserts pass; emits JSON artefact
Runs/math/Math424-AddA/reading_uniqueness_scan.json.
"""
import json, math, os, sys, itertools
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import Math400_AddE_brazovskii_one_loop as addE   # quadrature consistency

# ---------------------------------------------------------------- constants
LAM_COEFF = -0.43          # lambda (TECT canonical, locked)
GAM_COEFF = +1.62          # gamma
Y_COEFF   = 1.0
Q0        = 0.6801747616
U  = 2.0 * LAM_COEFF       # -0.86  (attractive quartic)
V  = 2.0 * GAM_COEFF       # +3.24  (repulsive sextic)
C  = Y_COEFF
MU2_CANON = +0.005
R_OF = lambda mu2: mu2 + Y_COEFF * Q0**4

CLAIMS = []   # (name, expected, actual, tol, passed)

def claim(name, expected, actual, tol):
    ok = abs(actual - expected) <= tol
    CLAIMS.append(dict(name=name, expected=expected, actual=actual,
                       tol=tol, passed=bool(ok)))
    assert ok, f"CLAIM FAIL {name}: expected {expected} got {actual} tol {tol}"

def claim_true(name, cond, detail=""):
    CLAIMS.append(dict(name=name, expected=True, actual=bool(cond),
                       tol=0, passed=bool(cond), detail=detail))
    assert cond, f"CLAIM FAIL {name}: {detail}"

# ------------------------------------------------- shell sets (integer coords)
# Coordinates are exact integer tuples; HEX uses (x, y) with y in sqrt(3)/2
# units doubled so all entries are integers: a=(2,0), b=(-1,1), c=(-1,-1),
# |a|^2 = 4 = x^2 + 3 y^2 of b,c. Zero-sum detection is exact integer.
SHELLS = {
    "LAM": [(0, 0, 1), (0, 0, -1)],
    "HEX": [(2, 0, 0), (-1, 1, 0), (-1, -1, 0),
            (-2, 0, 0), (1, -1, 0), (1, 1, 0)],
    "FCC": [tuple(s) for s in itertools.product((1, -1), repeat=3)],
    "BCC": [p for p in set(itertools.permutations((1, 1, 0)))
            for p in ()] ,  # placeholder replaced below
}
# BCC {110}: all permutations of (+-1, +-1, 0)
bcc = set()
for sx in (1, -1):
    for sy in (1, -1):
        for pos in ((0, 1), (0, 2), (1, 2)):
            vvec = [0, 0, 0]
            vvec[pos[0]] = sx
            vvec[pos[1]] = sy
            bcc.add(tuple(vvec))
SHELLS["BCC"] = sorted(bcc)

def n_tuples_zero_sum(vectors, m):
    """Exact count of ordered m-tuples of shell vectors summing to zero."""
    sums = {(0, 0, 0): 1}
    for _ in range(m):
        new = {}
        for s, cnt in sums.items():
            for w in vectors:
                t = (s[0] + w[0], s[1] + w[1], s[2] + w[2])
                new[t] = new.get(t, 0) + cnt
        sums = new
    return sums.get((0, 0, 0), 0)

def realspace_check(vectors, m, metric):
    """Exact real-space cell average of phi^m for A=1 via periodic FFT grid.

    All integer coordinates -> exp(i k.x) periodic in each axis with period
    2*pi (HEX: y-axis period 2*pi/sqrt(3), same grid trick). A uniform grid
    with G > m * max|coord| points per axis integrates band-limited
    trigonometric polynomials exactly.
    """
    G = 32
    ax = np.arange(G) * (2 * np.pi / G)
    X, Yg, Z = np.meshgrid(ax, ax, ax, indexing="ij")
    phi = np.zeros_like(X)
    for (a, b, c3) in vectors:
        phi += np.cos(a * X + b * Yg + c3 * Z)   # zero phases, real field
    return float(np.mean(phi ** m))

READINGS = ["LAM", "HEX", "FCC", "BCC"]
COMB = {}
for name in READINGS:
    vecs = SHELLS[name]
    n_pairs = len(vecs) // 2
    N2 = n_tuples_zero_sum(vecs, 2)
    N3 = n_tuples_zero_sum(vecs, 3)
    N4 = n_tuples_zero_sum(vecs, 4)
    N6 = n_tuples_zero_sum(vecs, 6)
    COMB[name] = dict(n=n_pairs, N2=N2, N3=N3, N4=N4, N6=N6)
    # exact real-space cross-check of the enumeration (combinatorial claims)
    for m, Nm in ((2, N2), (4, N4), (6, N6)):
        rs = realspace_check(vecs, m, name)
        claim(f"{name}_realspace_phi^{m}", Nm, rs, 1e-8 * max(1, Nm))

# textbook anchors
claim("LAM_N4", 6, COMB["LAM"]["N4"], 0)
claim("LAM_N6", 20, COMB["LAM"]["N6"], 0)
claim_true("LAM_no_triads", COMB["LAM"]["N3"] == 0)
claim_true("FCC_no_triads(odd-parity)", COMB["FCC"]["N3"] == 0)
claim_true("HEX_has_triads", COMB["HEX"]["N3"] > 0)
claim_true("BCC_has_triads", COMB["BCC"]["N3"] > 0)
for nm in READINGS:
    claim(f"{nm}_N2_eq_2n", 2 * COMB[nm]["n"], COMB[nm]["N2"], 0)

# ------------------------------------------------------------ loop integrals
N_PT_FAST = 6000
def M_of(r_hat, n_points=N_PT_FAST):
    return addE.loop_integral_full(r_hat, Q0, C, n_points=n_points)

# memoised dense table + interpolation for speed inside scans
_r_grid = np.geomspace(1e-4, 40.0, 480)
_M_grid = np.array([M_of(r) for r in _r_grid])
def M_fast(r_hat):
    if r_hat <= _r_grid[0]:
        return float(_M_grid[0])
    if r_hat >= _r_grid[-1]:
        return float(_M_grid[-1])
    return float(np.interp(np.log(r_hat), np.log(_r_grid), _M_grid))

def _grid_q(n_points=N_PT_FAST, q_max_factor=50.0):
    n_dense = int(0.6 * n_points)
    n_lo = (n_points - n_dense) // 2
    n_hi = n_points - n_dense - n_lo
    q_lo = np.linspace(0.0, 0.5 * Q0, n_lo + 1)[:-1]
    q_d = np.linspace(0.5 * Q0, 1.5 * Q0, n_dense)
    q_hi = np.linspace(1.5 * Q0, q_max_factor * Q0, n_hi + 1)[1:]
    return np.concatenate([q_lo, q_d, q_hi])

_QG = _grid_q()
_DEN0 = (_QG ** 2 - Q0 ** 2) ** 2 * C
def dI(r_hat, r_ref):
    """(1/2pi^2) int q^2 ln[(r_hat + c(q^2-q0^2)^2)/(r_ref + ...)] dq.
    Convergent difference of two UV-divergent ln-integrals; same grid as M."""
    integrand = _QG ** 2 * np.log((r_hat + _DEN0) / (r_ref + _DEN0))
    val = np.trapz(integrand, _QG) / (2 * np.pi ** 2)
    # analytic 1/q^2 tail of the log-difference integrand
    qmax = _QG[-1]
    val += (r_hat - r_ref) / (C * qmax) / (2 * np.pi ** 2)
    return float(val)

# ------------------------------------------------------- gap + free energy
def gap_solve(r_bare, n, N4, A):
    """Solve r_hat = r + 3uM + 15vM^2 + 6unA^2 + 60vnA^2 M + 5vN4 A^4."""
    A2, A4 = A * A, A ** 4
    def f(rh):
        M = M_fast(rh)
        return rh - (r_bare + 3 * U * M + 15 * V * M * M
                     + 6 * U * n * A2 + 60 * V * n * A2 * M + 5 * V * N4 * A4)
    lo, hi = 1e-4, 40.0
    flo, fhi = f(lo), f(hi)
    if flo > 0 and fhi > 0:
        return None        # no solution above lo: trial mass collapses
    if flo < 0 and fhi < 0:
        return None
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
        if hi / lo - 1 < 1e-12:
            break
    return math.sqrt(lo * hi)

def dF_reading(r_bare, name, A, r_R, M_R):
    cmb = COMB[name]
    n, N4, N6 = cmb["n"], cmb["N4"], cmb["N6"]
    rh = gap_solve(r_bare, n, N4, A)
    if rh is None:
        return None, None
    M = M_fast(rh)
    A2, A4, A6 = A * A, A ** 4, A ** 6
    val = (0.5 * dI(rh, r_R) - 0.5 * (rh * M - r_R * M_R)
           + 0.5 * r_bare * (2 * n * A2 + M - M_R)
           + 3 * U * n * A2 * M + 0.75 * U * (M * M - M_R * M_R)
           + 0.25 * U * N4 * A4 + 2.5 * V * N4 * A4 * M
           + 15 * V * n * A2 * M * M + 2.5 * V * (M ** 3 - M_R ** 3)
           + (V / 6.0) * N6 * A6)
    return val, rh

def scan_reading(r_bare, name, r_R, M_R):
    cmb = COMB[name]
    n, N4, N6 = cmb["n"], cmb["N4"], cmb["N6"]
    # amplitude scale from sextic balance; generous factor 3
    A_scale = math.sqrt(max(abs(U) * N4 / (V * N6), 1e-6)) if N6 else 0.3
    grid = np.linspace(0.0, 3.0 * A_scale, 121)
    best = (0.0, 0.0, None)   # (dF, A, r_hat) ; A=0 reference = 0 exactly
    rows = []
    for A in grid:
        val, rh = dF_reading(r_bare, name, float(A), r_R, M_R)
        if val is None:
            continue
        rows.append((float(A), val, rh))
        if val < best[0]:
            best = (val, float(A), rh)
    # golden-section refine around the best grid point if interior minimum
    if best[1] > 0:
        lo = max(best[1] - grid[1], 0.0)
        hi = best[1] + grid[1]
        for _ in range(40):
            m1 = lo + 0.382 * (hi - lo)
            m2 = lo + 0.618 * (hi - lo)
            f1, _ = dF_reading(r_bare, name, m1, r_R, M_R)
            f2, _ = dF_reading(r_bare, name, m2, r_R, M_R)
            f1 = f1 if f1 is not None else 1e9
            f2 = f2 if f2 is not None else 1e9
            if f1 < f2:
                hi = m2
            else:
                lo = m1
        Aref = 0.5 * (lo + hi)
        vref, rhref = dF_reading(r_bare, name, Aref, r_R, M_R)
        if vref is not None and vref < best[0]:
            best = (vref, Aref, rhref)
    return best, rows

def mf_threshold(name, r_bare):
    """Mean-field condensation discriminant u^2 N4^2 - 8 n r v N6 (M->0)."""
    cmb = COMB[name]
    return U * U * cmb["N4"] ** 2 - 8 * cmb["n"] * r_bare * V * cmb["N6"]

# ------------------------------------------------------------------- main
def main():
    out = dict(theory_tag="Math424-AddA", date="2026-06-04",
               constants=dict(LAM=LAM_COEFF, GAM=GAM_COEFF, Y=Y_COEFF, q0=Q0,
                              u=U, v=V, mu2_canonical=MU2_CANON),
               combinatorics=COMB, points=[], claims=None)

    # --- Math400-AddE canonical reproduction (full 20000-pt quadrature) ---
    r_can = R_OF(MU2_CANON)
    res = addE.solve_self_consistency(r_can, U, V, Q0, C, verbose=False)
    roots = res.get("roots", [])
    assert len(roots) == 1, f"expected unique root, got {len(roots)}"
    rR_full = float(roots[0]["r_R"])
    M_full = addE.loop_integral_full(rR_full, Q0, C, n_points=20000)
    claim("AddE_canonical_r_R_reproduction", 0.41925, rR_full, 2e-3)
    claim("AddE_canonical_M_reproduction", 0.09600, M_full, 2e-3)

    sweep = [-0.5, -0.2, 0.0, MU2_CANON, 0.1, 0.3, 0.5]
    verdict_all = True
    for mu2 in sweep:
        r_bare = R_OF(mu2)
        # disordered solution on the fast pipeline
        rR = gap_solve(r_bare, 0, 0, 0.0)
        claim_true(f"disordered_gap_exists_mu2={mu2:+.3f}", rR is not None)
        MR = M_fast(rR)
        # built-in identity dF(0)=0
        v0, _ = dF_reading(r_bare, "BCC", 0.0, rR, MR)
        claim(f"dF(A=0)_identity_mu2={mu2:+.3f}", 0.0, v0, 1e-9)
        entry = dict(mu2=mu2, r_bare=r_bare, r_R=rR, M_R=MR, readings={})
        for name in READINGS:
            (dF, Astar, rh), rows = scan_reading(r_bare, name, rR, MR)
            mf = mf_threshold(name, r_bare)
            entry["readings"][name] = dict(
                dF_min=dF, A_star=Astar, r_hat=rh,
                mf_discriminant=mf,
                collapses_to_disordered=bool(Astar == 0.0))
            if mu2 == MU2_CANON:
                tag = f"canonical_dF_{name}_nonnegative"
                claim_true(tag, dF >= -1e-9,
                           f"dF={dF} A*={Astar} (reading must NOT undercut R_H)")
                if Astar > 0 and dF < -1e-9:
                    verdict_all = False
        out["points"].append(entry)

    # --- analytic sub-result (a): canonical MF condensation criterion ---
    # condensation (any A>0 MF stationary point) iff N4^2/N6 > 8 n r v / u^2.
    r_c = R_OF(MU2_CANON)
    thr_unit = 8.0 * r_c * V / (U * U)          # = 7.677 per unit n
    claim("canonical_threshold_per_n", 7.6770, thr_unit, 1e-3)
    for nm in READINGS:
        c = COMB[nm]
        ratio = c["N4"] ** 2 / c["N6"]
        shortfall = (thr_unit * c["n"]) / ratio
        claim_true(f"canonical_MF_inequality_{nm}",
                   ratio < thr_unit * c["n"],
                   f"N4^2/N6={ratio:.3f} vs threshold {thr_unit*c['n']:.3f}")
        out.setdefault("canonical_inequality", {})[nm] = dict(
            ratio=ratio, threshold=thr_unit * c["n"], shortfall=shortfall)

    # canonical-window summary verdict
    claim_true("PathA_step3_canonical_verdict",
               verdict_all, "R_H global among enumerated readings at canonical")
    out["claims"] = CLAIMS
    os.makedirs("Runs/math/Math424-AddA", exist_ok=True)
    with open("Runs/math/Math424-AddA/reading_uniqueness_scan.json", "w",
              encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)

    # ---------------- console report ----------------
    print("=" * 76)
    print("Math424-AddA  Path A Steps 1-4: variational-Hartree reading comparison")
    print("=" * 76)
    print(f"constants: u={U}  v={V}  q0={Q0}  c={C}")
    print(f"combinatorics (exact enumeration, zero phases):")
    for nm in READINGS:
        c = COMB[nm]
        print(f"  {nm}: n={c['n']:2d}  N2={c['N2']:3d}  N3={c['N3']:4d}  "
              f"N4={c['N4']:5d}  N6={c['N6']:7d}")
    for entry in out["points"]:
        mu2 = entry["mu2"]
        star = "  <== CANONICAL" if mu2 == MU2_CANON else ""
        print(f"\nmu^2={mu2:+.3f}  r={entry['r_bare']:+.4f}  "
              f"r_R={entry['r_R']:+.4f}  M_R={entry['M_R']:.4f}{star}")
        for nm in READINGS:
            d = entry["readings"][nm]
            if d["collapses_to_disordered"]:
                print(f"  {nm}: A*=0 (collapses to R_H; no condensate "
                      f"stationary point lowers F)   MF disc={d['mf_discriminant']:+.3f}")
            else:
                print(f"  {nm}: A*={d['A_star']:.4f}  r_hat={d['r_hat']:.4f}  "
                      f"dF={d['dF_min']:+.6e}   MF disc={d['mf_discriminant']:+.3f}")
    npass = sum(1 for c in CLAIMS if c["passed"])
    print(f"\nclaims: {npass}/{len(CLAIMS)} PASS")
    print("JSON: Runs/math/Math424-AddA/reading_uniqueness_scan.json")
    return 0

if __name__ == "__main__":
    sys.exit(main())
