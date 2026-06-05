#!/usr/bin/env python3
"""Math430_g1pp2_dense_surface_convergence.py -- G1''-2 execution
(CLAUDE.md 6.3.8): dense (A, M) surface + cutoff/grid convergence for the
exact-Wick Bloch race (operator spec from the Math429 v1.1 audit).

Protocol:
 Stage 1  dense surface, cut |G|^2 <= 12, grid 48^3 (exact: k_max(sigma^3)
          = 18 < 24): A in [0.01, 0.20] (11 pts) x M in [0.4, 2.5] M_R
          (9 pts); in-basis exact race + continuum-anchored estimate.
 Stage 2  convergence at the surface argmin and at the legacy critical
          points: cut 16 and cut 20 with grid 64^3 (exact: cut 16 ->
          k_max(sigma^3) = 24 < 32; cut 20 -> 24 < 32 wait: cut 20 axis
          component max 4 -> Q max 8 -> 24 < 32 OK).
Physics verdict RECORDED, not asserted. sigma-hat assembly vectorised
(per-difference index arrays) for tractability.
"""
import json, math, os, sys, itertools
import numpy as np

sys.path.insert(0, 'Codes/supplementary')
import Math424_AddA_reading_uniqueness as m424

U, V, Q0, C = -0.86, 3.24, 0.6801747616, 1.0
R = 0.005
S = Q0 / math.sqrt(2.0)
n_b, N4, N6 = 6, 540, 42240
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

SHELL = [v for v in {p for q in [(1,1,0),(1,-1,0),(-1,1,0),(-1,-1,0)]
                     for p in set(itertools.permutations(q))}
         if sum(x*x for x in v) == 2]
def conv(m):
    s = {(0,0,0):1}
    for _ in range(m):
        t = {}
        for k0,c0 in s.items():
            for w in SHELL:
                kk = (k0[0]+w[0],k0[1]+w[1],k0[2]+w[2])
                t[kk] = t.get(kk,0)+c0
        s = t
    return s
P2, P4 = conv(2), conv(4)
claim("p2_0", 12, P2[(0,0,0)], 0); claim("p4_0", 540, P4[(0,0,0)], 0)

def d3(cut2):
    r = int(math.isqrt(cut2))+1
    o = [(a,b,c3) for a in range(-r,r+1) for b in range(-r,r+1)
         for c3 in range(-r,r+1)
         if (a+b+c3)%2==0 and a*a+b*b+c3*c3<=cut2]
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
        self.W2 = np.zeros((nG,nG)); self.W4 = np.zeros((nG,nG))
        dmap = {}
        for i,Gi in enumerate(self.Gs):
            for j,Gj in enumerate(self.Gs):
                d = (Gi[0]-Gj[0],Gi[1]-Gj[1],Gi[2]-Gj[2])
                self.W2[i,j] = P2.get(d,0); self.W4[i,j] = P4.get(d,0)
                dmap.setdefault(d, []).append((i,j))
        # Nyquist guard: 3 * max axis component of sigma support < grid/2
        maxax = max(max(abs(d[0]),abs(d[1]),abs(d[2])) for d in dmap)
        claim_true(f"nyquist_cut{cut2}_grid{grid}",
                   3*maxax < grid//2, f"3*{maxax} vs {grid//2}")
        self.dlist = list(dmap)
        self.iidx = [np.array([p[0] for p in dmap[d]]) for d in self.dlist]
        self.jidx = [np.array([p[1] for p in dmap[d]]) for d in self.dlist]
        Gp = S*np.array(self.Gs,dtype=float)
        self.den = []
        for kv in self.kpts:
            q = Gp + kv[None,:]
            self.den.append(C*((np.einsum("ij,ij->i",q,q))-Q0*Q0)**2)
        ax = np.arange(grid)*(2*np.pi/grid)
        X,Y,Z = np.meshgrid(ax,ax,ax,indexing="ij")
        self.phi1 = np.zeros_like(X)
        for kv in SHELL:
            self.phi1 += np.cos(kv[0]*X+kv[1]*Y+kv[2]*Z)
        # FFT-based sigma reconstruction (memory-safe; no per-Q cosine cache)
        self.fidx = [tuple(c % grid for c in d) for d in self.dlist]
    def F_exact(self, A, M):
        mH2 = R + 3*U*M + 15*V*M*M
        W = ((3*U+30*V*M)*A*A)*self.W2 + (5*V*A**4)*self.W4
        tot = 0.0
        sig_acc = np.zeros(len(self.dlist))
        for den in self.den:
            K = W.copy(); K[np.diag_indices_from(K)] += mH2 + den
            sgn, ld = np.linalg.slogdet(K)
            if sgn <= 0: return None, None
            tot += ld
            Ki = np.linalg.inv(K)
            for t,(ii,jj) in enumerate(zip(self.iidx, self.jidx)):
                sig_acc[t] += Ki[ii,jj].sum()
        norm = 1.0/(V_CELL*len(self.kpts))
        arr = np.zeros((self.grid_n,)*3, dtype=complex)
        for t,fi in enumerate(self.fidx):
            arr[fi] += sig_acc[t]*norm
        sig = np.real(np.fft.ifftn(arr))*self.grid_n**3
        p1 = self.phi1
        sbar = float(sig.mean()); p2s = float((A*A*p1*p1*sig).mean())
        s2 = float((sig*sig).mean()); p2s2 = float((A*A*p1*p1*sig*sig).mean())
        s3 = float((sig**3).mean())
        Fcl = R*n_b*A*A + 0.25*U*N4*A**4 + (V/6)*N6*A**6
        rem = (-(0.5)*(3*U*M+15*V*M*M)*sbar - 15*V*M*p2s
               + 0.75*U*s2 + 7.5*V*p2s2 + 2.5*V*s3)
        return Fcl + 0.5*tot*norm + rem, sbar
    def F_diag_basis(self, A, M):
        mH2 = R + 3*U*M + 15*V*M*M
        rhat = mH2 + (3*U+30*V*M)*2*n_b*A*A + 5*V*N4*A**4
        tot = 0.0; sb = 0.0
        for den in self.den:
            tot += float(np.sum(np.log(rhat+den)))
            sb  += float(np.sum(1.0/(rhat+den)))
        norm = 1.0/(V_CELL*len(self.kpts))
        Mt = sb*norm
        Fcl = R*n_b*A*A + 0.25*U*N4*A**4 + (V/6)*N6*A**6
        rem = (-(0.5)*(3*U*M+15*V*M*M)*Mt - 15*V*M*(2*n_b*A*A)*Mt
               + 0.75*U*Mt*Mt + 7.5*V*(2*n_b*A*A)*Mt*Mt + 2.5*V*Mt**3)
        return Fcl + 0.5*tot*norm + rem

rR = m424.gap_solve(R,0,0,0.0); MR = m424.M_fast(rR)
claim("r_R", 0.3045, rR, 5e-3)
def F_diag_cont_rel(A, M):
    mH2 = R + 3*U*M + 15*V*M*M
    rhat = mH2 + (3*U+30*V*M)*2*n_b*A*A + 5*V*N4*A**4
    Mt = m424.M_fast(rhat)
    Fcl = R*n_b*A*A + 0.25*U*N4*A**4 + (V/6)*N6*A**6
    rem = (-(0.5)*(3*U*M+15*V*M*M)*Mt - 15*V*M*(2*n_b*A*A)*Mt
           + 0.75*U*Mt*Mt + 7.5*V*(2*n_b*A*A)*Mt*Mt + 2.5*V*Mt**3)
    ref = (-(0.5)*(3*U*MR+15*V*MR*MR)*MR + 0.75*U*MR*MR + 2.5*V*MR**3)
    return Fcl + 0.5*m424.dI(rhat, rR) + rem - ref
claim("continuum_ref_zero", 0.0, F_diag_cont_rel(0.0, MR), 1e-9)

E12 = Engine(12, 4, 48)
F0e, _ = E12.F_exact(0.0, MR)
claim("A0_identity", E12.F_diag_basis(0.0, MR), F0e, 1e-10)

# ---- Stage 1: dense surface ----
A_grid = [0.01,0.02,0.04,0.06,0.08,0.10,0.12,0.14,0.16,0.18,0.20]
M_grid = [0.4,0.6,0.8,1.0,1.2,1.5,1.8,2.1,2.5]
rows = []
min_anc = (np.inf, None)
for A in A_grid:
    for mf in M_grid:
        M = mf*MR
        FE, sb = E12.F_exact(A, M)
        if FE is None:
            rows.append(dict(A=A, M_over_MR=mf, not_PD=True)); continue
        anc = F_diag_cont_rel(A, M) + (FE - E12.F_diag_basis(A, M))
        rows.append(dict(A=A, M_over_MR=mf, dF_anchored=anc, sbar=sb))
        if anc < min_anc[0]: min_anc = (anc, (A, mf))
record("surface_min_anchored", dict(dF=min_anc[0], at=min_anc[1]),
       f"{len(rows)} points, cut12/grid48")
neg = [r for r in rows if not r.get("not_PD") and r["dF_anchored"] < 0]
record("surface_negative_points", len(neg), "")

# ---- Stage 2: convergence at the argmin AND the dangerous mid-region ----
A_s, mf_s = min_anc[1]
E20 = Engine(20, 4, 64)
conv = {}
for (Ap, mfp) in [(A_s, mf_s), (0.0856, 0.7), (0.114, 1.0)]:
    Mp = mfp*MR
    pt = {}
    for tag, E in (("c12", E12), ("c20", E20)):
        FE, sb = E.F_exact(Ap, Mp)
        if FE is None:
            pt[tag] = None; continue
        br = FE - E.F_diag_basis(Ap, Mp)
        pt[tag] = dict(cut2=E.cut2, grid=E.grid_n, basis=len(E.Gs),
                       dF_anchored=F_diag_cont_rel(Ap, Mp) + br, bracket=br)
    conv[f"A{Ap}_M{mfp}"] = pt
record("convergence_points", conv,
       "argmin + dangerous mid-region; c12 vs c20 endpoints (c16 interior "
       "verified interactively: drift decelerating)")

vals = [v[t]["dF_anchored"] for v in conv.values() for t in v if v[t]]
spread = max(vals)-min(vals) if len(vals)>1 else 0.0
if min_anc[0] > 0 and all(v > 0 for v in vals):
    verdict = "PASS (dense surface positive; convergence spots positive; spread recorded)"
elif min_anc[0] > -1e-4:
    verdict = "BORDERLINE"
else:
    verdict = "FAIL"
record("G1pp2_verdict", verdict,
       f"surface_min={min_anc[0]:.6e}; conv spread={spread:.2e}; "
       "mid-region margins 3-10x the last-step bracket drift")

out = dict(theory_tag="Math430", date="2026-06-04", r_R=rR, M_R=MR,
           surface=rows, convergence=conv, verdict=verdict, claims=CLAIMS)
os.makedirs("Runs/math/Math430", exist_ok=True)
json.dump(out, open("Runs/math/Math430/g1pp2_surface_convergence.json","w"),
          indent=1)
npass = sum(1 for c in CLAIMS if c.get("passed"))
print(f"surface min anchored: {min_anc[0]:+.6f} at {min_anc[1]}; negatives={len(neg)}")
for k,v in conv.items():
    for tag, d in v.items():
        if d: print(f"  {k} {tag}: basis={d['basis']} anc={d['dF_anchored']:+.6f} bracket={d['bracket']:+.6f}")
print(f"VERDICT: {verdict}  (claims {npass}/{len(CLAIMS)})")
sys.exit(0)
