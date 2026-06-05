#!/usr/bin/env python3
"""Math436_hex_exact_wick_bracket.py -- G1''-3b-HEX execution (CLAUDE.md
6.3.8): HEX exact-Wick Bloch bracket, semi-analytic (2D triangular
reciprocal lattice x 1D transverse continuum) -- the geometric transpose of
the executed LAM engine Math434_lam_exact_wick_bracket.py (22/22, exit 0).

STATUS AT AUTHORING (2026-06-05, Math436 agent session): WRITTEN, NOT YET
EXECUTED -- the authoring session has no shell-execution capability
(Math434/Math435 precedent). No number produced by this script is cited as
executed in Math436; the note labels every value [EXACT] (closed-form hand
arithmetic) or [EST]/PENDING-EXECUTION. FIRST EXECUTION must be logged
(stdout + JSON) before any of its outputs are cited.

PHYSICS. HEX condensate phi_c(x) = A sum_{j=1..6} exp(i k_j.x)
= 2A [cos(k1.x) + cos(k2.x) + cos(k3.x)], k1 + k2 + k3 = 0, |k_j| = q0,
all in-plane, 120 deg apart (Math424-AddA zero-phase convention, n = 3,
N4 = 90, N6 = 2040). Reciprocal lattice = 2D triangular lattice
Lambda* = {m1 b1 + m2 b2}, b1 = k1, b2 = k2, Gram matrix
   g = q0^2 [[1, -1/2], [-1/2, 1]],  |m1 b1 + m2 b2|^2 = q0^2 N(m),
   N(m) = m1^2 - m1 m2 + m2^2   (Loeschian norm form).
The Math424-AddA integer embedding (x, y) with |k|^2 = (q0/2)^2 (x^2+3y^2)
is the same lattice via (m1, m2) -> (x, y) = (2 m1 - m2, m2):
x^2 + 3 y^2 = 4 N(m).  NOTE the Math431 off2_cont HEX channel evaluated
|Q| = (q0/2) sqrt(x^2 + y^2) (EUCLIDEAN integer norm) instead of the
embedding metric -- a metric defect this script measures explicitly
(claims hexM431_*): the replica leg reproduces Math431 bit-identically,
the corrected leg uses |Q| = q0 sqrt(N_Loeschian).

Bloch problem: fluctuation momentum q = k2d + G + kz zhat, k2d in the 2D
BZ of Lambda* (mean over an Nk x Nk shifted mesh), G in Lambda* (Loeschian
cut), kz in R (1D continuum, trapz). Per-(k2d, kz) matrix:

  K_{ab} = [m_H^2 + C(|k2d + G_a|^2 + kz^2 - q0^2)^2] delta_{ab}
           + cou2 p2(G_a - G_b) + cou4 p4(G_a - G_b),
  m_H^2 = r + 3uM + 15vM^2,  cou2 = (3u+30vM) A^2,  cou4 = 5v A^4,
  p2, p4 = exact integer shell-convolution counts in (m1, m2) coords:
  p2(0) = 6 = 2n; on-shell class N=1 (THREE-WAVE RESONANCE, the
  structurally new HEX channel vs LAM): p2 = 2, p4 = 60; sqrt3 class N=3:
  p2 = 2, p4 = 48; 2q0 class N=4: p2 = 1, p4 = 34; sum p2 = 36 = 6^2,
  sum p4 = 1296 = 6^4 (all asserted).

Tr ln per volume: (1/V) Tr ln K = (A_BZ/(2pi)^2) mean_{k2d}
  int dkz/(2pi) [sum-band ln eig],  A_BZ = |det[b1 b2]| = (sqrt3/2) q0^2;
always as the DIFFERENCE exact - diagonal on the SAME (k2d, kz, cut)
quadrature so UV pieces cancel entrywise (bracket protocol, Math429/430).

sigma(x): hat_sigma(d) = (A_BZ/(2pi)^2 / Nk^2) sum_{k2d} int dkz/(2pi)
  sum_a [K^{-1}]_{a, a+d} for difference vectors d within a support cut;
cell averages of sigma^2, sigma^3, phi_c^2 sigma, phi_c^2 sigma^2 computed
EXACTLY on a 48^2 (theta1, theta2) torus FFT grid (band-limited: support
cut N <= 12 has max axis index 4, k_max(sigma^3) = 12 < 24 = Nyquist;
asserted) -- this includes ALL resonant cross-terms (e.g. the on-shell
<phi_c^2 delta_sigma> channel ABSENT in LAM) by construction, answering
the Math436 note's attack-beta surface without hand algebra.

OUTPUTS (JSON: Runs/math/Math436/hex_exact_wick_bracket.json):
 - per-point rows over the Math431 HEX grid (9 A x 6 M):
     estimator(rho=1) replica (Math431 metric), estimator corrected
     metric, exact-Wick bracket, anchored exact dF, mesh-off2, Xnorm sup;
 - argmin block: Gershgorin sup, B(0), |bracket - off2_mesh| vs the
   Math436 hand bound; sigma-hat on-shell magnitude;
 - Math431-HEX metric-defect deltas (replica vs corrected, per point);
 - A = 0 identity; small-A c2 = n r_R sanity; M_fast systematic;
 - cut-12 vs cut-16 and Nk-6 vs Nk-10 convergence at the argmin + one
   mid-amplitude point.
SELF-TEST ASSERTS (6.3.8): every numerical claim of the Math436 note is
asserted here against this script's own computation. Physics verdict
RECORDED, not asserted (6.3.3).
"""
import json, math, os, sys
import numpy as np

sys.path.insert(0, 'Codes/supplementary')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import Math424_AddA_reading_uniqueness as m424

U, V, Q0, C = -0.86, 3.24, 0.6801747616, 1.0
R = 0.005
N_HEX, N4_HEX, N6_HEX = 3, 90, 2040
CLAIMS = []

def claim(name, expected, actual, tol):
    ok = abs(actual - expected) <= tol
    CLAIMS.append(dict(name=name, expected=expected, actual=actual,
                       tol=tol, passed=bool(ok)))
    assert ok, f"FAIL {name}: {expected} vs {actual}"

def claim_true(name, cond, detail=""):
    CLAIMS.append(dict(name=name, expected=True, actual=bool(cond),
                       tol=0, passed=bool(cond), detail=detail))
    assert cond, f"FAIL {name}: {detail}"

def record(name, value, detail=""):
    CLAIMS.append(dict(name=name, recorded=value, detail=detail,
                       passed=True, tol=None, expected=None, actual=value))

# ---- checkpoint/resume infrastructure (Math434 pattern): sandbox caps
# each shell call at 45 s; memoise expensive results to a state file and
# exit 3 at a 30-s budget; rerun until exit 0. Performance scaffolding
# only -- no formula touched.
import time as _time
_T0 = _time.time()
_STATE_PATH = "Runs/math/Math436/state.json"
try:
    _STATE = json.load(open(_STATE_PATH))
except Exception:
    _STATE = {}
def _save_state():
    os.makedirs("Runs/math/Math436", exist_ok=True)
    json.dump(_STATE, open(_STATE_PATH, "w"))
def memo(key, fn):
    if key in _STATE:
        return _STATE[key]
    if _time.time() - _T0 > 30.0:
        _save_state()
        print(f"[CHECKPOINT] budget reached before {key}; rerun to resume",
              flush=True)
        sys.exit(3)
    val = fn()
    _STATE[key] = val
    _save_state()
    return val

# ===================== geometry and exact combinatorics ====================
# shell in (m1, m2): +-k1 = +-(1,0); +-k2 = +-(0,1); +-k3 = -+(1,1)
SHELL = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)]
def nloesch(d):
    return d[0] * d[0] - d[0] * d[1] + d[1] * d[1]
for s in SHELL:
    assert nloesch(s) == 1
def conv(m):
    s = {(0, 0): 1}
    for _ in range(m):
        t = {}
        for k0, c0 in s.items():
            for w in SHELL:
                kk = (k0[0] + w[0], k0[1] + w[1])
                t[kk] = t.get(kk, 0) + c0
        s = t
    return s
P2, P4 = conv(2), conv(4)
claim("hex_p2_0", 2 * N_HEX, P2[(0, 0)], 0)
claim("hex_p4_0", N4_HEX, P4[(0, 0)], 0)
claim("hex_p2_sum", 36, sum(P2.values()), 0)
claim("hex_p4_sum", 1296, sum(P4.values()), 0)
# hand-derived class values of the Math436 note section 2 (on-shell
# resonance class N=1; sqrt3 class N=3; 2q0 class N=4)
claim("hex_p2_onshell", 2, P2[(1, 1)], 0)
claim("hex_p4_onshell", 60, P4[(1, 1)], 0)
claim("hex_p2_sqrt3", 2, P2[(1, -1)], 0)
claim("hex_p4_sqrt3", 48, P4[(1, -1)], 0)  # dispatcher calibration: agent hand value 44 was a mis-count; independent brute-force enumeration (and this script) give 48; logged in Math436 note S6
claim("hex_p2_2q0", 1, P2[(2, 0)], 0)
claim("hex_p4_2q0", 34, P4[(2, 0)], 0)
# N3 = 12 (the SHG-like triad count; ordered triples summing to zero)
P3 = conv(3)
claim("hex_N3_triads", 12, P3.get((0, 0), 0), 0)
# embedding consistency: (m1,m2)->(x,y)=(2m1-m2,m2), x^2+3y^2 = 4 N(m)
for d in [(1, 0), (0, 1), (1, 1), (1, -1), (2, 0), (2, 1), (3, -1)]:
    x, y = 2 * d[0] - d[1], d[1]
    assert x * x + 3 * y * y == 4 * nloesch(d), d
record("embedding_identity", True, "x^2+3y^2 = 4 N_Loeschian verified")

rR = m424.gap_solve(R, 0, 0, 0.0)
MR = m424.M_fast(rR)
claim("r_R", 0.30452570866744433, rR, 1e-9)
claim("M_R", 0.10941432918723439, MR, 1e-9)
C2_HEX = N_HEX * rR          # lattice-independent small-A coefficient
claim("c2_hex_n_rR", 0.91357712600233, C2_HEX, 1e-9)

# =================== continuum diagonal anchor (per-lattice) ===============
def F_diag_cont_rel(A, M):
    mH2 = R + 3 * U * M + 15 * V * M * M
    rhat = (mH2 + (3 * U + 30 * V * M) * 2 * N_HEX * A * A
            + 5 * V * N4_HEX * A ** 4)
    Mt = m424.M_fast(rhat)
    Fcl = (R * N_HEX * A * A + 0.25 * U * N4_HEX * A ** 4
           + (V / 6) * N6_HEX * A ** 6)
    rem = (-(0.5) * (3 * U * M + 15 * V * M * M) * Mt
           - 15 * V * M * (2 * N_HEX * A * A) * Mt
           + 0.75 * U * Mt * Mt + 7.5 * V * (2 * N_HEX * A * A) * Mt * Mt
           + 2.5 * V * Mt ** 3)
    ref = (-(0.5) * (3 * U * MR + 15 * V * MR * MR) * MR
           + 0.75 * U * MR * MR + 2.5 * V * MR ** 3)
    return Fcl + 0.5 * m424.dI(rhat, rR) + rem - ref

claim("continuum_ref_zero", 0.0, F_diag_cont_rel(0.0, MR), 1e-9)

# ============ Math431 rho=1 estimator: replica + corrected metric ==========
# Replica leg reproduces Math431's off2_cont BIT-FOR-BIT (same grids, same
# trapz, same class construction on the Math424-AddA 3D integer embedding
# with s = Q0/2 and EUCLIDEAN integer norm) -> regression target
# 9.486768603217552e-05. Corrected leg replaces |Q| by the embedding
# metric q0 sqrt(N_Loeschian) = (q0/2) sqrt(x^2 + 3 y^2).
SHELL431 = [(2, 0, 0), (-1, 1, 0), (-1, -1, 0), (-2, 0, 0), (1, -1, 0),
            (1, 1, 0)]
def conv431(m):
    s = {(0, 0, 0): 1}
    for _ in range(m):
        t = {}
        for k0, c0 in s.items():
            for w in SHELL431:
                kk = (k0[0] + w[0], k0[1] + w[1], k0[2] + w[2])
                t[kk] = t.get(kk, 0) + c0
        s = t
    return s
P2_431, P4_431 = conv431(2), conv431(4)
claim("hex431_p2_0", 6, P2_431[(0, 0, 0)], 0)
claim("hex431_p4_0", 90, P4_431[(0, 0, 0)], 0)
S431 = Q0 / 2.0
_qg = np.concatenate([np.linspace(1e-4, 0.5 * Q0, 500, endpoint=False),
                      np.linspace(0.5 * Q0, 1.5 * Q0, 1500, endpoint=False),
                      np.linspace(1.5 * Q0, 40 * Q0, 1200)])
_mu = np.linspace(-1, 1, 121)

def off2_cont_hex(A, M, rhat, metric):
    """metric = 'euclid431' (Math431 replica: |Q| = s sqrt(x^2+y^2+z^2))
    or 'loeschian' (corrected: |Q| = s sqrt(x^2+3y^2) = q0 sqrt(N))."""
    cou2 = (3 * U + 30 * V * M) * A * A
    cou4 = 5 * V * A ** 4
    cls = {}
    def qlen2(Qv):
        if metric == "euclid431":
            return Qv[0] ** 2 + Qv[1] ** 2 + Qv[2] ** 2
        return Qv[0] ** 2 + 3 * Qv[1] ** 2 + Qv[2] ** 2
    for Qv, c2v in P2_431.items():
        if Qv == (0, 0, 0):
            continue
        w = cou2 * c2v + cou4 * P4_431.get(Qv, 0)
        n2 = qlen2(Qv)
        cls[n2] = cls.get(n2, 0.0) + w * w
    for Qv, c4v in P4_431.items():
        if Qv == (0, 0, 0) or Qv in P2_431:
            continue
        w = cou4 * c4v
        n2 = qlen2(Qv)
        cls[n2] = cls.get(n2, 0.0) + w * w
    qq = _qg[:, None]; mm = _mu[None, :]; q2 = qq * qq
    Gq = q2 / (rhat + C * (q2 - Q0 * Q0) ** 2)
    tot = 0.0
    for n2, w2 in cls.items():
        Qp = S431 * math.sqrt(n2)
        qp2 = q2 + Qp * Qp + 2 * qq * Qp * mm
        Bv = float(np.trapz(np.trapz(
            Gq / (rhat + C * (qp2 - Q0 * Q0) ** 2), _mu, axis=1),
            _qg)) / (4 * math.pi ** 2)
        tot += -(0.25) * w2 * Bv
    return tot

def rhat_of(A, M):
    mH2 = R + 3 * U * M + 15 * V * M * M
    return (mH2 + (3 * U + 30 * V * M) * 2 * N_HEX * A * A
            + 5 * V * N4_HEX * A ** 4)

# regression: Math431 recorded HEX minimum (replica metric)
def _hex431_min():
    A_grid = [0.01, 0.02, 0.04, 0.06, 0.08, 0.10, 0.13, 0.16, 0.20]
    M_grid = [0.4, 0.7, 1.0, 1.5, 2.0, 2.5]
    mn = (np.inf, None)
    for A in A_grid:
        for mf in M_grid:
            M = mf * MR
            d = F_diag_cont_rel(A, M)
            est = d + off2_cont_hex(A, M, rhat_of(A, M), "euclid431")
            if est < mn[0]:
                mn = (est, (A, mf))
    return [mn[0], list(mn[1])]
hex431 = memo("hex431_min_replica", _hex431_min)
# bit-identical replication expected (same module, grids, formulas);
# tolerance 1e-12 abs; if FIRST EXECUTION shows a platform-level float
# delta, calibrate per documented protocol (note section 4) -- never
# beyond 1e-10 without a finding.
claim("hexM431_min_replica", 9.486768603217552e-05, hex431[0], 1e-12)
claim_true("hexM431_argmin_replica",
           tuple(hex431[1]) == (0.01, 1.0), f"argmin {hex431[1]}")

# ====================== Bloch bracket engine (2D x 1D) =====================
def lattice_pts(cut):
    r = int(math.isqrt(4 * cut)) + 2
    o = [(a, b) for a in range(-r, r + 1) for b in range(-r, r + 1)
         if nloesch((a, b)) <= cut]
    o.sort(key=lambda t: (nloesch(t), t))
    return o

# physical 2D vectors: b1 = q0 (1, 0); b2 = q0 (-1/2, sqrt3/2)
B1 = Q0 * np.array([1.0, 0.0])
B2 = Q0 * np.array([-0.5, math.sqrt(3.0) / 2.0])
A_BZ = abs(B1[0] * B2[1] - B1[1] * B2[0])           # = (sqrt3/2) q0^2
claim("A_BZ", math.sqrt(3.0) / 2.0 * Q0 * Q0, A_BZ, 1e-12)

# kz continuum grid (even integrand; integrate [0, kz_max] x 2)
KZ_GRID = np.concatenate([
    np.linspace(0.0, 1.2 * Q0, 160, endpoint=False),
    np.linspace(1.2 * Q0, 3.0 * Q0, 60, endpoint=False),
    np.linspace(3.0 * Q0, 8.0 * Q0, 31)])
_KZW = np.zeros_like(KZ_GRID)
_KZW[1:-1] = 0.5 * (KZ_GRID[2:] - KZ_GRID[:-2])
_KZW[0] = 0.5 * (KZ_GRID[1] - KZ_GRID[0])
_KZW[-1] = 0.5 * (KZ_GRID[-1] - KZ_GRID[-2])

SUPP_CUT = 12     # sigma-hat support: Loeschian N(d) <= 12, max axis 4
GRID2 = 48        # theta-torus FFT grid; Nyquist 24 > 3*4 = 12 (asserted)
# Nyquist exactness, registered deterministically at module level (the
# sigma support is SUPP_CUT-limited regardless of basis cut): max axis
# index over {d : N(d) <= 12} is 4 (e.g. (4, 2): N = 12), so
# k_max(sigma^3) = 12 < 24 and k_max(phi_c^2 sigma^2) = 2 + 8 = 10 < 24.
_supp_maxax = max(max(abs(a), abs(b))
                  for a in range(-5, 6) for b in range(-5, 6)
                  if nloesch((a, b)) <= SUPP_CUT)
claim("supp_max_axis_index", 4, _supp_maxax, 0)
claim_true("nyq_hex_supp12_grid48", 3 * _supp_maxax < GRID2 // 2,
           f"3*{_supp_maxax} < {GRID2 // 2}")

class EngineHex:
    def __init__(self, cut, nk):
        self.cut, self.nk = cut, nk
        self.Gs = lattice_pts(cut)
        nG = len(self.Gs)
        self.nG = nG
        self.W2 = np.zeros((nG, nG))
        self.W4 = np.zeros((nG, nG))
        dmap = {}
        for i, Gi in enumerate(self.Gs):
            for j, Gj in enumerate(self.Gs):
                d = (Gi[0] - Gj[0], Gi[1] - Gj[1])
                self.W2[i, j] = P2.get(d, 0)
                self.W4[i, j] = P4.get(d, 0)
                if nloesch(d) <= SUPP_CUT:
                    dmap.setdefault(d, []).append((i, j))
        self.dlist = list(dmap)
        self.iidx = [np.array([p[0] for p in dmap[d]]) for d in self.dlist]
        self.jidx = [np.array([p[1] for p in dmap[d]]) for d in self.dlist]
        # physical in-plane lattice vectors
        self.Gp = (np.array([g[0] for g in self.Gs])[:, None] * B1[None, :]
                   + np.array([g[1] for g in self.Gs])[:, None] * B2[None, :])
        # shifted BZ mesh
        f = (np.arange(nk) + 0.5) / nk
        self.kpts = np.array([x * B1 + y * B2 for x in f for y in f])
        # theta-torus condensate field (A = 1): phi1 = 2[cos t1 + cos t2
        # + cos(t1+t2)]; band-limited, exact on GRID2^2
        ax = np.arange(GRID2) * (2 * np.pi / GRID2)
        T1, T2 = np.meshgrid(ax, ax, indexing="ij")
        self.phi1 = 2.0 * (np.cos(T1) + np.cos(T2) + np.cos(T1 + T2))
        # quadrature prefactor per (k2d, kz) sample:
        #   (A_BZ/(2pi)^2)/Nk^2  *  w_kz * 2/(2pi)   (even kz extension)
        self.pref2d = A_BZ / (2 * math.pi) ** 2 / (nk * nk)

    def F_pieces(self, A, M):
        """bracket = (1/V)[F_exact - F_diag_basis] on the SAME quadrature:
        0.5*(trln_exact - trln_diag) + (rem_exact - rem_diag); plus
        mesh-off2 (second order on the same mesh), Gershgorin sup, and
        the on-shell |sigma_hat| diagnostics."""
        cou2 = (3 * U + 30 * V * M) * A * A
        cou4 = 5 * V * A ** 4
        W = cou2 * self.W2 + cou4 * self.W4
        Woff = W.copy()
        np.fill_diagonal(Woff, 0.0)
        mH2 = R + 3 * U * M + 15 * V * M * M
        rhat = mH2 + cou2 * P2[(0, 0)] + cou4 * P4[(0, 0)]
        W2sq = Woff * Woff
        absW = np.abs(Woff)
        nG = self.nG
        ii = np.arange(nG)
        dtr = 0.0
        sig_acc = np.zeros(len(self.dlist))
        sig_diag = 0.0
        off2 = 0.0
        xnorm_max = 0.0
        for kv in self.kpts:                       # Nk^2 BZ points
            q2d = self.Gp + kv[None, :]            # (nG, 2)
            t2d = np.einsum("ij,ij->i", q2d, q2d)  # |k2d + G|^2
            # batch over kz: den (NKZ, nG)
            den = C * (t2d[None, :] + KZ_GRID[:, None] ** 2 - Q0 * Q0) ** 2
            D = rhat + den
            K = np.broadcast_to(Woff, (len(KZ_GRID), nG, nG)).copy()
            K[:, ii, ii] = D
            sgn, ld = np.linalg.slogdet(K)
            if np.any(sgn <= 0):
                return None
            wkz = _KZW * (2.0 / (2 * math.pi)) * self.pref2d
            dtr += float(np.sum(wkz * (ld - np.sum(np.log(D), axis=-1))))
            Ki = np.linalg.inv(K)
            for t, (ia, ja) in enumerate(zip(self.iidx, self.jidx)):
                sig_acc[t] += float(np.sum(wkz * np.sum(
                    Ki[:, ia, ja], axis=-1)))
            sig_diag += float(np.sum(wkz * np.sum(1.0 / D, axis=-1)))
            Gd = 1.0 / D
            off2 += float(np.sum(wkz * (-0.5) *
                                 np.einsum("ki,ij,kj->k", Gd, W2sq, Gd)))
            sD = 1.0 / np.sqrt(D)
            X = absW[None] * sD[:, :, None] * sD[:, None, :]
            xnorm_max = max(xnorm_max, float(np.max(np.sum(X, axis=-1))))
        # ---- exact cell averages on the theta torus ----
        arr = np.zeros((GRID2, GRID2), dtype=complex)
        for t, d in enumerate(self.dlist):
            arr[d[0] % GRID2, d[1] % GRID2] += sig_acc[t]
        sig = np.real(np.fft.ifft2(arr)) * GRID2 * GRID2
        p1 = self.phi1
        sbar = float(sig.mean())
        p2s = float((A * A * p1 * p1 * sig).mean())
        s2 = float((sig * sig).mean())
        p2s2 = float((A * A * p1 * p1 * sig * sig).mean())
        s3 = float((sig ** 3).mean())
        Mt_basis = sig_diag
        rem_ex = (-(0.5) * (3 * U * M + 15 * V * M * M) * sbar
                  - 15 * V * M * p2s + 0.75 * U * s2
                  + 7.5 * V * p2s2 + 2.5 * V * s3)
        rem_di = (-(0.5) * (3 * U * M + 15 * V * M * M) * Mt_basis
                  - 15 * V * M * (2 * N_HEX * A * A) * Mt_basis
                  + 0.75 * U * Mt_basis ** 2
                  + 7.5 * V * (2 * N_HEX * A * A) * Mt_basis ** 2
                  + 2.5 * V * Mt_basis ** 3)
        bracket = 0.5 * dtr + (rem_ex - rem_di)
        # diagnostics: on-shell sigma-hat magnitude (largest N=1 class)
        sig_onshell = 0.0
        for t, d in enumerate(self.dlist):
            if nloesch(d) == 1:
                sig_onshell = max(sig_onshell, float(abs(sig_acc[t])))
        return dict(bracket=bracket, dtr=0.5 * dtr,
                    drem=rem_ex - rem_di, sbar=sbar,
                    Mt_basis=Mt_basis, off2=0.5 * off2,
                    xnorm=xnorm_max, rhat=rhat,
                    sig_onshell=sig_onshell, s2=s2)

ENG = EngineHex(12, 6)
record("basis_cut12_size", ENG.nG, "Loeschian N <= 12 lattice points")

# A = 0 identity: exact == diagonal on the same quadrature (bracket = 0)
z0 = memo("z0", lambda: ENG.F_pieces(0.0, MR))
claim("A0_bracket_zero", 0.0, z0["bracket"], 1e-10)

# ---------------- audit-bound block at the expected argmin -----------------
A0, M0 = 0.01, MR
pc = memo("pc_argmin", lambda: ENG.F_pieces(A0, M0))
cou2_0 = (3 * U + 30 * V * MR) * A0 * A0
cou4_0 = 5 * V * A0 ** 4
w1_0 = cou2_0 * 2 + cou4_0 * 60          # on-shell class coupling
ws3_0 = cou2_0 * 2 + cou4_0 * 48         # sqrt3 class (48: dispatcher-corrected exact count; was mis-derived 44)
w2_0 = cou2_0 * 1 + cou4_0 * 34          # 2q0 class
claim("audit_w1_argmin", 1.62073e-3, w1_0, 2e-7)
rhat_0 = pc["rhat"]
claim("audit_rhat_argmin", 0.3093733, rhat_0, 5e-6)
# Gershgorin hand bound (note section 3): every coupled neighbour at the
# degenerate denominator rhat -> ||X|| <= (30 cou2 + 1206 cou4) / rhat
xbound = (30 * cou2_0 + 1206 * cou4_0) / rhat_0
claim("audit_Xbound_hand", 7.874e-2, xbound, 2e-4)
claim_true("audit_Xnorm_below_hand_bound", pc["xnorm"] <= xbound * 1.0001,
           f"computed sup ||X||_Gersh = {pc['xnorm']:.4e} vs {xbound:.4e}")
# B(0) = -M'(rhat): central difference
hh = 1e-4
B0 = -(m424.M_of(rhat_0 + hh) - m424.M_of(rhat_0 - hh)) / (2 * hh)
claim_true("audit_B0_below_0p2", 0 < B0 < 0.2, f"B(0) = {B0:.4f}")
# off2 magnitude bound: |off2| <= (1/4) B(0) sum_{d!=0} w_d^2
sumw2 = 0.0
for d, c2v in P2.items():
    if d == (0, 0):
        continue
    w = cou2_0 * c2v + cou4_0 * P4.get(d, 0)
    sumw2 += w * w
for d, c4v in P4.items():
    if d == (0, 0) or d in P2:
        continue
    sumw2 += (cou4_0 * c4v) ** 2
claim_true("audit_off2_bound", abs(pc["off2"]) <= 0.25 * sumw2 * B0
           * 1.0001 + 1e-12,
           f"off2 = {pc['off2']:.3e} vs bound {0.25 * sumw2 * B0:.3e}")
# on-shell sigma-hat envelope check: |sig1| <= w1 B(0) / (1 - ||X||);
# the (1-a)^-1 dressing carries an O(1) envelope slack (Math434 objection
# beta, VALID-with-mitigation: the EXACT value is the certification, the
# envelope is a consistency check) -> 1.5x documented safety factor.
sig1_bound = w1_0 * B0 / (1 - xbound)
claim_true("audit_sig_onshell_envelope",
           pc["sig_onshell"] <= sig1_bound * 1.5 + 1e-12,
           f"sig_onshell = {pc['sig_onshell']:.3e} vs envelope "
           f"{sig1_bound:.3e} (x1.5)")
# headline two-sided consistency bound (note section 3, hand-derived
# budget ~1.5e-5: logdet excess (a/(3(1-a)))*2|off2| <= 1.0e-7 +
# sigma-remainder two-sided budget <= 1.5e-5; the DOWNWARD-only analytic
# budget is ~1.3e-6 -- the sign-definite remainder pieces are favorable):
# pre-registered combined two-sided gate 2e-5.
corr = abs(pc["bracket"] - pc["off2"])
claim_true("audit_directional_bound_2e-5", corr <= 2e-5,
           f"|bracket - off2| = {corr:.3e}")
record("argmin_corr_vs_margin", dict(corr=corr),
       "ratio to the HEX margin reported in the note")
record("argmin_block", dict(w1=w1_0, ws3=ws3_0, w2=w2_0, rhat=rhat_0,
                            Xnorm=pc["xnorm"], Xbound=xbound, B0=B0,
                            off2=pc["off2"], bracket=pc["bracket"],
                            sig_onshell=pc["sig_onshell"], corr=corr),
       "Math436 sec.3 numbers")

# M_fast interpolation spot check at the HEX argmin (Math434 protocol)
Mdirect = m424.M_of(rhat_0, n_points=20000)
claim_true("Mfast_interp_spot_raw",
           abs(Mdirect - m424.M_fast(rhat_0)) < 2e-5,
           f"direct {Mdirect:.7f} vs table {m424.M_fast(rhat_0):.7f}")
_d_tab_ref = F_diag_cont_rel(0.01, MR)
_rR_dir = None
_MR_dir = None
def _F_cont_dir(A, M):
    mH2 = R + 3 * U * M + 15 * V * M * M
    rhat = (mH2 + (3 * U + 30 * V * M) * 2 * N_HEX * A * A
            + 5 * V * N4_HEX * A ** 4)
    Mt = m424.M_fast(rhat)
    Fcl = (R * N_HEX * A * A + 0.25 * U * N4_HEX * A ** 4
           + (V / 6) * N6_HEX * A ** 6)
    rem = (-(0.5) * (3 * U * M + 15 * V * M * M) * Mt
           - 15 * V * M * (2 * N_HEX * A * A) * Mt
           + 0.75 * U * Mt * Mt + 7.5 * V * (2 * N_HEX * A * A) * Mt * Mt
           + 2.5 * V * Mt ** 3)
    ref = (-(0.5) * (3 * U * _MR_dir + 15 * V * _MR_dir * _MR_dir) * _MR_dir
           + 0.75 * U * _MR_dir * _MR_dir + 2.5 * V * _MR_dir ** 3)
    return Fcl + 0.5 * m424.dI(rhat, _rR_dir) + rem - ref
def _dF_impact_compute():
    global _rR_dir, _MR_dir
    _orig = m424.M_fast
    m424.M_fast = lambda r: m424.M_of(r, n_points=20000)
    _rR_dir = m424.gap_solve(R, 0, 0, 0.0)
    _MR_dir = m424.M_fast(_rR_dir)
    try:
        return abs(_F_cont_dir(0.01, _MR_dir) - _d_tab_ref)
    finally:
        m424.M_fast = _orig
_dF_impact = memo("dF_impact", _dF_impact_compute)
claim_true("Mfast_dF_level_impact_lt_1e-7", _dF_impact < 1e-7,
           f"consistent-scheme dF impact {_dF_impact:.3e}")
record("Mfast_systematic",
       dict(raw_err=abs(Mdirect - m424.M_fast(rhat_0)),
            dF_impact=_dF_impact),
       "reference-difference cancellation, HEX argmin")

# ---------------- per-point race over the Math431 HEX grid -----------------
A_grid = [0.01, 0.02, 0.04, 0.06, 0.08, 0.10, 0.13, 0.16, 0.20]
M_grid = [0.4, 0.7, 1.0, 1.5, 2.0, 2.5]
rows = []
mn_est_rep = (np.inf, None)
mn_est_cor = (np.inf, None)
mn_exact = (np.inf, None)
max_metric_delta = 0.0
for A in A_grid:
    for mf in M_grid:
        M = mf * MR
        def _pt(A=A, M=M):
            pcs = ENG.F_pieces(A, M)
            if pcs is None:
                return None
            rh = rhat_of(A, M)
            o_rep = off2_cont_hex(A, M, rh, "euclid431")
            o_cor = off2_cont_hex(A, M, rh, "loeschian")
            return dict(pcs=pcs, o_rep=o_rep, o_cor=o_cor)
        cell = memo(f"pt_{A}_{mf}", _pt)
        if cell is None:
            rows.append(dict(A=A, M_over_MR=mf, not_PD=True))
            continue
        pcs, o_rep, o_cor = cell["pcs"], cell["o_rep"], cell["o_cor"]
        d_cont = F_diag_cont_rel(A, M)
        est_rep = d_cont + o_rep            # Math431-replica metric
        est_cor = d_cont + o_cor            # corrected triangular metric
        exact = d_cont + pcs["bracket"]     # exact-Wick anchored
        rows.append(dict(A=A, M_over_MR=mf,
                         dF_est_rho1_replica=est_rep,
                         dF_est_rho1_corrected=est_cor,
                         dF_exact_anchored=exact,
                         bracket=pcs["bracket"], off2_mesh=pcs["off2"],
                         xnorm=pcs["xnorm"],
                         metric_delta=o_cor - o_rep))
        max_metric_delta = max(max_metric_delta, abs(o_cor - o_rep))
        if est_rep < mn_est_rep[0]:
            mn_est_rep = (est_rep, (A, mf))
        if est_cor < mn_est_cor[0]:
            mn_est_cor = (est_cor, (A, mf))
        if exact < mn_exact[0]:
            mn_exact = (exact, (A, mf))
record("hex_min_estimator_rho1_replica",
       dict(dF=mn_est_rep[0], at=mn_est_rep[1]),
       "must equal Math431 +9.486768603217552e-05 at (0.01, 1.0)")
record("hex_min_estimator_rho1_corrected",
       dict(dF=mn_est_cor[0], at=mn_est_cor[1]),
       "corrected triangular-metric rho=1 estimator minimum")
record("hex_min_exact_anchored", dict(dF=mn_exact[0], at=mn_exact[1]),
       "G1''-3b HEX closure candidate value")
record("hexM431_metric_defect_max_abs_dF", max_metric_delta,
       "max |off2(corrected) - off2(replica)| over the 54-pt grid")
neg = [r for r in rows if not r.get("not_PD")
       and r["dF_exact_anchored"] < 0]
record("hex_exact_negative_points", len(neg), "")
# regression sanity: grid minimum of the replica leg = the memoised
# replica-scan minimum (same functions; bitwise)
claim_true("replica_grid_consistency",
           abs(mn_est_rep[0] - hex431[0]) <= 1e-15,
           f"{mn_est_rep[0]} vs {hex431[0]}")
# small-A sanity (6.3.4): corrected estimator at (0.01, M_R) within 10% of
# c2 A^2 = n r_R A^2 (Math431 found 4-8% across lattices)
cA2 = C2_HEX * 1e-4
pt_small = [r for r in rows if r.get("A") == 0.01
            and r.get("M_over_MR") == 1.0][0]
claim_true("smallA_c2_sanity",
           abs(pt_small["dF_est_rho1_corrected"] - cA2) <= 0.10 * cA2,
           f"est {pt_small['dF_est_rho1_corrected']:.4e} vs c2A^2 "
           f"{cA2:.4e}")

# ---------------- convergence checks (cut and BZ mesh) ---------------------
def _conv_block():
    out = {}
    E16 = EngineHex(16, 6)
    for (A, mf, tag) in [(0.01, 1.0, "argmin"), (0.10, 1.0, "mid")]:
        M = mf * MR
        b12 = ENG.F_pieces(A, M)["bracket"]
        b16 = E16.F_pieces(A, M)["bracket"]
        out[f"cut_drift_{tag}"] = b16 - b12
    E10 = EngineHex(12, 10)
    for (A, mf, tag) in [(0.01, 1.0, "argmin"), (0.10, 1.0, "mid")]:
        M = mf * MR
        b6 = ENG.F_pieces(A, M)["bracket"]
        b10 = E10.F_pieces(A, M)["bracket"]
        out[f"nk_drift_{tag}"] = b10 - b6
    return out
convs = memo("conv_block", _conv_block)
record("convergence_block", convs,
       "cut 12->16 and Nk 6->10 bracket drifts at argmin + mid")
# gates: drifts at the argmin must stay below 10% of the corrected margin
margin0 = pt_small["dF_est_rho1_corrected"]
claim_true("conv_cut_argmin_small",
           abs(convs["cut_drift_argmin"]) <= 0.10 * margin0,
           f"cut drift {convs['cut_drift_argmin']:.3e} vs margin "
           f"{margin0:.3e}")
claim_true("conv_nk_argmin_small",
           abs(convs["nk_drift_argmin"]) <= 0.10 * margin0,
           f"Nk drift {convs['nk_drift_argmin']:.3e}")

verdict = ("PASS (HEX exact-Wick anchored positive at every grid point)"
           if (not neg) and mn_exact[0] > 0 else
           ("BORDERLINE" if mn_exact[0] > -1e-4 else
            "FAIL (HEX exact-Wick anchored minimum negative)"))
record("G1pp3b_HEX_verdict", verdict,
       f"min_exact={mn_exact[0]:.6e} at {mn_exact[1]}")

out = dict(theory_tag="Math436", date="2026-06-05", r_R=rR, M_R=MR,
           grid=dict(A=A_grid, M_over_MR=M_grid, cut=12, nk=6,
                     nkz=len(KZ_GRID), supp_cut=SUPP_CUT, grid2=GRID2),
           rows=rows, verdict=verdict,
           metric_defect=dict(max_abs_dF=max_metric_delta,
                              replica_min=hex431[0],
                              corrected_min=mn_est_cor[0]),
           claims=CLAIMS)
os.makedirs("Runs/math/Math436", exist_ok=True)
json.dump(out, open("Runs/math/Math436/hex_exact_wick_bracket.json", "w"),
          indent=1)
npass = sum(1 for c in CLAIMS if c.get("passed"))
print(f"rR={rR:.6f} MR={MR:.6f}  argmin corr={corr:.3e}")
print(f"HEX min est(rho=1, replica)   {mn_est_rep[0]:+.6e} at "
      f"{mn_est_rep[1]}")
print(f"HEX min est(rho=1, corrected) {mn_est_cor[0]:+.6e} at "
      f"{mn_est_cor[1]}")
print(f"HEX min exact-anchored        {mn_exact[0]:+.6e} at {mn_exact[1]}")
print(f"Math431-HEX metric-defect max |dF| = {max_metric_delta:.3e}")
print(f"VERDICT: {verdict}  (claims {npass}/{len(CLAIMS)})")
sys.exit(0)
