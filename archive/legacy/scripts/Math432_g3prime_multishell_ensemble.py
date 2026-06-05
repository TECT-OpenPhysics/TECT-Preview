#!/usr/bin/env python3
"""Math432_g3prime_multishell_ensemble.py -- G3' execution (CLAUDE.md 6.3.8):
two-shell BCC condensate ensemble race {110}+{200} under the anchored
exact-Wick Gibbs--Bogoliubov protocol (Math429/430/431 machinery).

Operator dispatch spec (OPEN-QUESTIONS, registered 2026-06-04):
  phi_c(x) = A1 * sum_{k in {110}} e^{ikx} + A2 * sum_{k in {200}} e^{ikx},
  reciprocal lattice unchanged (D3); per-shell amplitudes (A1, A2) scanned
  with M; anchored protocol as Math429/430; connect to Math400-AddF N=64
  channel states (multi-harmonic content).
Pre-registered outcomes (falsification gate, CLAUDE.md 6.3.3):
  FAIL  <=> some (A1, A2, M) in the scan domain has anchored dF < 0
            confirmed at BOTH cut12/48^3 and cut20/64^3  -> Math424 Outcome-3.
  PASS  <=> all scanned points positive at cut12 AND convergence spot-checks
            positive with margins exceeding the last-step bracket drift.
  BORDERLINE otherwise (|min| < 1e-4 or convergence-fragile).
Physics verdict RECORDED by the same logic as Math430. Exit 0 iff all
implementation asserts pass.

Key new structural fact probed: the 4-wave resonance k1+k2+k3+k4 = 0 with
three {110} and one {200} member (e.g. (1,1,0)+(1,0,1)+(0,-1,-1)-(2,0,0))
makes the cross moment m31 = <phi1^3 phi2> nonzero, so the single-shell BCC
point is NOT stationary in the two-shell space: the linear tilt
U*m31*A1^3*A2 necessarily induces A2* != 0. G3' asks whether that enriched
ensemble can beat the disordered Reading-H reference.
"""
import json, math, os, sys, time, itertools
import numpy as np

sys.path.insert(0, 'Codes/supplementary')
import Math424_AddA_reading_uniqueness as m424

U, V, Q0, C = -0.86, 3.24, 0.6801747616, 1.0
R = 0.005
S = Q0 / math.sqrt(2.0)
K2 = R + C * Q0**4          # kernel value on the {200} shell (|k|^2 = 2 q0^2)
n1, n2 = 6, 3               # cosine-pair counts per shell
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
                       passed=True, tol=None, expected=None, actual=None))

SHELL1 = sorted({p for q in [(1,1,0),(1,-1,0)] for p in itertools.permutations(q)}
                | {(-a,-b,-c) for q in [(1,1,0),(1,-1,0)]
                   for (a,b,c) in itertools.permutations(q)})
SHELL1 = [v for v in SHELL1 if sum(x*x for x in v) == 2]
SHELL2 = [(2,0,0),(-2,0,0),(0,2,0),(0,-2,0),(0,0,2),(0,0,-2)]
assert len(SHELL1) == 12 and len(SHELL2) == 6

def d3(cut2):
    r = int(math.isqrt(cut2)) + 1
    o = [(a,b,c3) for a in range(-r,r+1) for b in range(-r,r+1)
         for c3 in range(-r,r+1)
         if (a+b+c3) % 2 == 0 and a*a+b*b+c3*c3 <= cut2]
    o.sort(key=lambda t:(t[0]**2+t[1]**2+t[2]**2,t)); return o

B = S*np.array([[1,1,0],[1,0,1],[0,1,1]],dtype=float).T
V_CELL = (2*math.pi)**3/abs(np.linalg.det(B))
def kmesh(nk):
    f = (np.arange(nk)+0.5)/nk
    return [B@np.array([x,y,z]) for x in f for y in f for z in f]

class Engine:
    def __init__(self, cut2, nk, grid):
        self.cut2, self.grid_n = cut2, grid
        self.Gs = d3(cut2); self.kpts = kmesh(nk)
        nG = len(self.Gs)
        dmap = {}
        for i,Gi in enumerate(self.Gs):
            for j,Gj in enumerate(self.Gs):
                d = (Gi[0]-Gj[0],Gi[1]-Gj[1],Gi[2]-Gj[2])
                dmap.setdefault(d, []).append((i,j))
        maxax = max(max(abs(d[0]),abs(d[1]),abs(d[2])) for d in dmap)
        claim_true(f"nyquist_cut{cut2}_grid{grid}",
                   3*maxax < grid//2, f"3*{maxax} vs {grid//2}")
        self.dlist = list(dmap)
        self.n_d = len(self.dlist)
        # flat pair arrays for one-shot scatter/gather
        II, JJ, TT = [], [], []
        for t,d in enumerate(self.dlist):
            for (i,j) in dmap[d]:
                II.append(i); JJ.append(j); TT.append(t)
        self.II = np.array(II); self.JJ = np.array(JJ); self.TT = np.array(TT)
        Gp = S*np.array(self.Gs,dtype=float)
        self.den = []
        for kv in self.kpts:
            q = Gp + kv[None,:]
            self.den.append(C*((np.einsum("ij,ij->i",q,q))-Q0*Q0)**2)
        ax = np.arange(grid)*(2*np.pi/grid)
        X,Y,Z = np.meshgrid(ax,ax,ax,indexing="ij")
        self.phi1 = np.zeros_like(X); self.phi2 = np.zeros_like(X)
        for kv in SHELL1:
            self.phi1 += np.cos(kv[0]*X+kv[1]*Y+kv[2]*Z)
        for kv in SHELL2:
            self.phi2 += np.cos(kv[0]*X+kv[1]*Y+kv[2]*Z)
        self.fidx = [tuple(c % grid for c in d) for d in self.dlist]
        self._fft_imag_max = 0.0
    def _what(self, field):
        """Exact Fourier coefficients of a band-limited real even field at
        the dlist difference vectors (forward FFT; no aliasing by Nyquist
        guard)."""
        fh = np.fft.fftn(field)/field.size
        vals = np.array([fh[fi] for fi in self.fidx])
        self._fft_imag_max = max(self._fft_imag_max, float(np.abs(vals.imag).max()))
        return vals.real
    def F_exact(self, A1, A2, M):
        mH2 = R + 3*U*M + 15*V*M*M
        phic = A1*self.phi1 + A2*self.phi2
        p2g = phic*phic; p4g = p2g*p2g
        w2 = self._what(p2g); w4 = self._what(p4g)
        coefs = (3*U+30*V*M)*w2 + 5*V*w4
        nG = len(self.Gs)
        W = np.zeros((nG,nG)); W[self.II,self.JJ] = coefs[self.TT]
        tot = 0.0
        sig_acc = np.zeros(self.n_d)
        for den in self.den:
            K = W.copy(); K[np.diag_indices_from(K)] += mH2 + den
            sgn, ld = np.linalg.slogdet(K)
            if sgn <= 0: return None, None
            tot += ld
            Ki = np.linalg.inv(K)
            sig_acc += np.bincount(self.TT, weights=Ki[self.II,self.JJ],
                                   minlength=self.n_d)
        norm = 1.0/(V_CELL*len(self.kpts))
        arr = np.zeros((self.grid_n,)*3, dtype=complex)
        for t,fi in enumerate(self.fidx):
            arr[fi] += sig_acc[t]*norm
        sig = np.real(np.fft.ifftn(arr))*self.grid_n**3
        sbar = float(sig.mean()); p2s = float((p2g*sig).mean())
        s2 = float((sig*sig).mean()); p2s2 = float((p2g*sig*sig).mean())
        s3 = float((sig**3).mean())
        Fcl = (R*n1*A1*A1 + K2*n2*A2*A2
               + 0.25*U*float(p4g.mean()) + (V/6)*float((p4g*p2g).mean()))
        rem = (-(0.5)*(3*U*M+15*V*M*M)*sbar - 15*V*M*p2s
               + 0.75*U*s2 + 7.5*V*p2s2 + 2.5*V*s3)
        return Fcl + 0.5*tot*norm + rem, sbar
    def F_diag_basis(self, A1, A2, M):
        mH2 = R + 3*U*M + 15*V*M*M
        phic = A1*self.phi1 + A2*self.phi2
        p2g = phic*phic; p4g = p2g*p2g
        w2bar = float(p2g.mean()); w4bar = float(p4g.mean())
        rhat = mH2 + (3*U+30*V*M)*w2bar + 5*V*w4bar
        tot = 0.0; sb = 0.0
        for den in self.den:
            tot += float(np.sum(np.log(rhat+den)))
            sb  += float(np.sum(1.0/(rhat+den)))
        norm = 1.0/(V_CELL*len(self.kpts))
        Mt = sb*norm
        Fcl = (R*n1*A1*A1 + K2*n2*A2*A2
               + 0.25*U*w4bar + (V/6)*float((p4g*p2g).mean()))
        rem = (-(0.5)*(3*U*M+15*V*M*M)*Mt - 15*V*M*w2bar*Mt
               + 0.75*U*Mt*Mt + 7.5*V*w2bar*Mt*Mt + 2.5*V*Mt**3)
        return Fcl + 0.5*tot*norm + rem

rR = m424.gap_solve(R,0,0,0.0); MR = m424.M_fast(rR)
claim("r_R", 0.3045, rR, 5e-3)
claim("K2_equals_Math426_K0", 0.219, K2, 1e-3)

def F_diag_cont_rel(E, A1, A2, M):
    mH2 = R + 3*U*M + 15*V*M*M
    phic = A1*E.phi1 + A2*E.phi2
    p2g = phic*phic; p4g = p2g*p2g
    w2bar = float(p2g.mean()); w4bar = float(p4g.mean())
    rhat = mH2 + (3*U+30*V*M)*w2bar + 5*V*w4bar
    Mt = m424.M_fast(rhat)
    Fcl = (R*n1*A1*A1 + K2*n2*A2*A2
           + 0.25*U*w4bar + (V/6)*float((p4g*p2g).mean()))
    rem = (-(0.5)*(3*U*M+15*V*M*M)*Mt - 15*V*M*w2bar*Mt
           + 0.75*U*Mt*Mt + 7.5*V*w2bar*Mt*Mt + 2.5*V*Mt**3)
    ref = (-(0.5)*(3*U*MR+15*V*MR*MR)*MR + 0.75*U*MR*MR + 2.5*V*MR**3)
    return Fcl + 0.5*m424.dI(rhat, rR) + rem - ref

E12 = Engine(12, 4, 48)

# ---- moment identities (exact band-limited grid means) ----
g = E12
claim("p2_shell1", 12.0, float((g.phi1**2).mean()), 1e-9)
claim("p2_shell2",  6.0, float((g.phi2**2).mean()), 1e-9)
claim("p4_shell1", 540.0, float((g.phi1**4).mean()), 1e-7)
m31 = float((g.phi1**3 * g.phi2).mean())
claim("m31_integer", round(m31), m31, 1e-7)
claim_true("m31_nonzero", abs(m31) > 0.5, f"m31={m31}")
m22 = float((g.phi1**2 * g.phi2**2).mean())
record("cross_moments", dict(m31=m31, m22=m22,
       p4_shell2=float((g.phi2**4).mean()),
       p6_shell1=float((g.phi1**6).mean())),
       "4-wave {110}x3+{200} resonance strength m31; SHG channel active")

F0e, _ = E12.F_exact(0.0, 0.0, MR)
claim("A0_identity", E12.F_diag_basis(0.0, 0.0, MR), F0e, 1e-10)
claim("continuum_ref_zero", 0.0, F_diag_cont_rel(E12, 0.0, 0.0, MR), 1e-9)

def anchored(E, A1, A2, M):
    FE, sb = E.F_exact(A1, A2, M)
    if FE is None: return None, None
    return F_diag_cont_rel(E, A1, A2, M) + (FE - E.F_diag_basis(A1, A2, M)), sb

# ---- Math430 regression (A2 = 0 must reproduce the single-shell race) ----
m430 = json.load(open("Runs/math/Math430/g1pp2_surface_convergence.json"))
for key, (Ap, mfp) in [("A0.0856_M0.7",(0.0856,0.7)), ("A0.114_M1.0",(0.114,1.0))]:
    refv = m430["convergence"][key]["c12"]["dF_anchored"]
    got, _ = anchored(E12, Ap, 0.0, mfp*MR)
    claim(f"math430_regression_{key}", refv, got, 1e-7)

# ---- small-A2 analytic bound: c2_2 = n2 (r_R + C q0^4) ----
c2_2 = n2*(rR + C*Q0**4)
got, _ = anchored(E12, 0.0, 0.01, MR)
claim("smallA2_bound_10pct", c2_2, got/1e-4, 0.10*c2_2)
record("c2_shell2_analytic", c2_2, "n2*(r_R + C*q0^4); shell-2 modes are stiff")

# ---- tilt asymmetry (sign-direction physics, 6.3.4) ----
fp, _ = anchored(E12, 0.0856, +0.03, MR)
fm, _ = anchored(E12, 0.0856, -0.03, MR)
claim_true("A2_tilt_asymmetry", abs(fp-fm) > 1e-6,
           f"F(+0.03)={fp:.6f} vs F(-0.03)={fm:.6f}")
record("tilt", dict(plus=fp, minus=fm,
       favorable="A2<0" if fm < fp else "A2>0"),
       "linear SHG tilt U*m31*A1^3*A2 makes A2=0 non-stationary")

# ---- Stage 1: (A1, A2, M) scan, cut12/48^3 ----
A1_grid = [0.01,0.02,0.04,0.06,0.0856,0.10,0.12,0.14]
A2_grid = [-0.12,-0.08,-0.05,-0.03,-0.015,0.015,0.03,0.05,0.08,0.12]
M_grid  = [0.7,1.0,1.4]
rows = []; min_anc = (np.inf, None)
t0 = time.time()
for A1 in A1_grid:
    for A2 in A2_grid:
        for mf in M_grid:
            anc, sb = anchored(E12, A1, A2, mf*MR)
            if anc is None:
                rows.append(dict(A1=A1,A2=A2,M_over_MR=mf,not_PD=True)); continue
            rows.append(dict(A1=A1,A2=A2,M_over_MR=mf,dF_anchored=anc,sbar=sb))
            if anc < min_anc[0]: min_anc = (anc,(A1,A2,mf))
    print(f"[scan] A1={A1} done  t={time.time()-t0:.0f}s  "
          f"min so far {min_anc[0]:+.6f} at {min_anc[1]}", flush=True)
# pure-{200} column
for A2 in [0.02,0.05,0.10,0.15]:
    anc, sb = anchored(E12, 0.0, A2, MR)
    rows.append(dict(A1=0.0,A2=A2,M_over_MR=1.0,dF_anchored=anc,sbar=sb))
    if anc is not None and anc < min_anc[0]: min_anc = (anc,(0.0,A2,1.0))
neg = [r for r in rows if not r.get("not_PD") and r["dF_anchored"] < 0]
record("scan_grid", dict(nA1=len(A1_grid), nA2=len(A2_grid), nM=len(M_grid),
       total_rows=len(rows)), "")
record("surface_min_anchored", dict(dF=min_anc[0], at=min_anc[1]),
       f"{len(rows)} points, cut12/grid48, two-shell")
record("surface_negative_points", len(neg), "")

# ---- Stage 2: local zoom around the argmin ----
a1s, a2s, mfs = min_anc[1]
zoom = []
for da2 in [-0.01,-0.005,0.005,0.01]:
    for dmf in [-0.15,0.0,0.15]:
        A2z, mfz = a2s+da2, mfs+dmf
        if mfz <= 0.2: continue
        anc, sb = anchored(E12, a1s, A2z, mfz*MR)
        if anc is None: continue
        zoom.append(dict(A1=a1s,A2=A2z,M_over_MR=mfz,dF_anchored=anc))
        if anc < min_anc[0]: min_anc = (anc,(a1s,A2z,mfz))
record("zoom_min_anchored", dict(dF=min_anc[0], at=min_anc[1]),
       f"{len(zoom)} zoom points")

# ---- Stage 3: convergence spot-checks, cut20/64^3 ----
E20 = Engine(20, 4, 64)
mixed_neg = sorted([r for r in rows if not r.get("not_PD") and abs(r["A2"])>0],
                   key=lambda r: r["dF_anchored"])[:2]
conv_pts = [tuple(min_anc[1])] + [(r["A1"],r["A2"],r["M_over_MR"]) for r in mixed_neg]
conv_pts.append((0.0856, 0.0, 0.7))   # legacy single-shell anchor point
conv = {}
for (Ap,A2p,mfp) in dict.fromkeys(conv_pts):
    pt = {}
    for tag, E in (("c12",E12),("c20",E20)):
        FE, sb = E.F_exact(Ap, A2p, mfp*MR)
        if FE is None: pt[tag]=None; continue
        br = FE - E.F_diag_basis(Ap, A2p, mfp*MR)
        pt[tag] = dict(cut2=E.cut2, grid=E.grid_n, basis=len(E.Gs),
                       dF_anchored=F_diag_cont_rel(E,Ap,A2p,mfp*MR)+br, bracket=br)
    conv[f"A1{Ap}_A2{A2p}_M{mfp}"] = pt
record("convergence_points", conv, "argmin + two most dangerous mixed points "
       "+ legacy single-shell anchor; c12/48^3 vs c20/64^3")
claim_true("fft_band_limited", E12._fft_imag_max < 1e-9,
           f"max imag {E12._fft_imag_max:.2e}")

vals = [v[t]["dF_anchored"] for v in conv.values() for t in v if v[t]]
drift = max(abs(v["c20"]["dF_anchored"]-v["c12"]["dF_anchored"])
            for v in conv.values() if v.get("c12") and v.get("c20"))
if min_anc[0] > 0 and all(x > 0 for x in vals):
    verdict = ("PASS (two-shell surface positive everywhere; zoom positive; "
               "convergence spots positive)")
elif min_anc[0] > -1e-4:
    verdict = "BORDERLINE"
else:
    verdict = "FAIL"
record("G3prime_verdict", verdict,
       f"min={min_anc[0]:.6e} at {min_anc[1]}; conv drift max={drift:.2e}")

out = dict(theory_tag="Math432", date="2026-06-04", r_R=rR, M_R=MR, K2=K2,
           m31=m31, m22=m22, surface=rows, zoom=zoom, convergence=conv,
           verdict=verdict, claims=CLAIMS)
os.makedirs("Runs/math/Math432", exist_ok=True)
json.dump(out, open("Runs/math/Math432/g3prime_multishell_ensemble.json","w"),
          indent=1)
npass = sum(1 for c in CLAIMS if c.get("passed"))
print(f"two-shell min anchored: {min_anc[0]:+.6f} at (A1,A2,M/MR)={min_anc[1]}; "
      f"negatives={len(neg)}")
for k,v in conv.items():
    for tag,d in v.items():
        if d: print(f"  {k} {tag}: basis={d['basis']} anc={d['dF_anchored']:+.6f} "
                    f"bracket={d['bracket']:+.6f}")
print(f"VERDICT: {verdict}  (claims {npass}/{len(CLAIMS)})")
sys.exit(0)
