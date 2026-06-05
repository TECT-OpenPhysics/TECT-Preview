#!/usr/bin/env python3
"""Math431_g1pp3_lam_hex_fcc.py -- G1''-3 execution (CLAUDE.md 6.3.8):
LAM/HEX/FCC repetition of the Bloch off-diagonal race at the corrected
canonical point (operator spec from the Math430 audit).

Two-tier protocol (honest scoping):
 FCC  -- FULL exact-Wick Bloch treatment (Math429/430 machinery): the
         {111} shell generates the 3D same-parity integer lattice
         (s = q0/sqrt(3)), so the Engine generalises directly.
 LAM/ -- continuum-anchored estimator at Math428-accepted grade: exact
 HEX     continuum diagonal (Math424-AddA machinery, per-lattice N4/N6)
         + WORST-CASE (rho = 1) second-order off-diagonal bubble; their
         Bloch blocks involve transverse-continuum directions (1D/2D
         lattices), so the exact-Wick bracket is registered as the
         residual sub-gate G1''-3b. LAM is additionally excluded as a
         vacuum candidate by the cosmological isotropy filter
         (Math400-AddA) independently of this race.
Physics verdicts RECORDED, not asserted.
"""
import json, math, os, sys, itertools
import numpy as np

sys.path.insert(0, 'Codes/supplementary')
import Math424_AddA_reading_uniqueness as m424

U, V, Q0, C = -0.86, 3.24, 0.6801747616, 1.0
R = 0.005
CLAIMS = []
def claim(name, expected, actual, tol):
    ok = abs(actual-expected) <= tol
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

rR = m424.gap_solve(R,0,0,0.0); MR = m424.M_fast(rR)
claim("r_R", 0.3045, rR, 5e-3)

LAT = dict(
    LAM=dict(shell=[(0,0,1),(0,0,-1)], n=1, N4=6, N6=20, s=Q0),
    HEX=dict(shell=[(2,0,0),(-1,1,0),(-1,-1,0),(-2,0,0),(1,-1,0),(1,1,0)],
             n=3, N4=90, N6=2040, s=Q0/2.0),
    FCC=dict(shell=[t for t in itertools.product((1,-1),repeat=3)],
             n=4, N4=216, N6=8000, s=Q0/math.sqrt(3.0)),
)
def conv(shell, m):
    s = {(0,0,0):1}
    for _ in range(m):
        t = {}
        for k0,c0 in s.items():
            for w in shell:
                kk = (k0[0]+w[0],k0[1]+w[1],k0[2]+w[2])
                t[kk] = t.get(kk,0)+c0
        s = t
    return s
for nm,L in LAT.items():
    L["P2"] = conv(L["shell"],2); L["P4"] = conv(L["shell"],4)
    claim(f"{nm}_p2_0", 2*L["n"], L["P2"][(0,0,0)], 0)
    claim(f"{nm}_p4_0", L["N4"], L["P4"][(0,0,0)], 0)

def F_diag_cont_rel(L, A, M):
    n,N4,N6 = L["n"], L["N4"], L["N6"]
    mH2 = R + 3*U*M + 15*V*M*M
    rhat = mH2 + (3*U+30*V*M)*2*n*A*A + 5*V*N4*A**4
    Mt = m424.M_fast(rhat)
    Fcl = R*n*A*A + 0.25*U*N4*A**4 + (V/6)*N6*A**6
    rem = (-(0.5)*(3*U*M+15*V*M*M)*Mt - 15*V*M*(2*n*A*A)*Mt
           + 0.75*U*Mt*Mt + 7.5*V*(2*n*A*A)*Mt*Mt + 2.5*V*Mt**3)
    ref = (-(0.5)*(3*U*MR+15*V*MR*MR)*MR + 0.75*U*MR*MR + 2.5*V*MR**3)
    return Fcl + 0.5*m424.dI(rhat, rR) + rem - ref, rhat
claim("cont_ref_zero", 0.0, F_diag_cont_rel(LAT["FCC"],0.0,MR)[0], 1e-9)

# ---- continuum bubble (worst-case rho = 1) ----
_qg = np.concatenate([np.linspace(1e-4,0.5*Q0,500,endpoint=False),
                      np.linspace(0.5*Q0,1.5*Q0,1500,endpoint=False),
                      np.linspace(1.5*Q0,40*Q0,1200)])
_mu = np.linspace(-1,1,121)
def off2_cont(L, A, M, rhat):
    cou2 = (3*U+30*V*M)*A*A; cou4 = 5*V*A**4
    cls = {}
    for Q,c2v in L["P2"].items():
        if Q==(0,0,0): continue
        w = cou2*c2v + cou4*L["P4"].get(Q,0)
        n2 = Q[0]**2+Q[1]**2+Q[2]**2
        cls[n2] = cls.get(n2,0.0) + w*w
    for Q,c4v in L["P4"].items():
        if Q==(0,0,0) or Q in L["P2"]: continue
        w = cou4*c4v
        n2 = Q[0]**2+Q[1]**2+Q[2]**2
        cls[n2] = cls.get(n2,0.0) + w*w
    qq = _qg[:,None]; m = _mu[None,:]; q2 = qq*qq
    Gq = q2/(rhat + C*(q2-Q0*Q0)**2)
    tot = 0.0
    for n2, w2 in cls.items():
        Qp = L["s"]*math.sqrt(n2)
        qp2 = q2 + Qp*Qp + 2*qq*Qp*m
        Bv = float(np.trapz(np.trapz(Gq/(rhat + C*(qp2-Q0*Q0)**2), _mu, axis=1), _qg))/(4*math.pi**2)
        tot += -(0.25)*w2*Bv
    return tot

results = {}
A_grid = [0.01,0.02,0.04,0.06,0.08,0.10,0.13,0.16,0.20]
M_grid = [0.4,0.7,1.0,1.5,2.0,2.5]
for nm in ("LAM","HEX","FCC"):
    L = LAT[nm]
    mn = (np.inf, None)
    for A in A_grid:
        for mf in M_grid:
            M = mf*MR
            d, rhat = F_diag_cont_rel(L, A, M)
            est = d + 1.0*off2_cont(L, A, M, rhat)   # worst-case rho = 1
            if est < mn[0]: mn = (est, (A, mf))
    results[nm] = dict(min_est_worstcase=mn[0], at=mn[1])
    record(f"{nm}_estimator_min_rho1", mn[0], f"at {mn[1]}")

# ---- FCC: full exact-Wick bracket at its estimator minimum region ----
FCCL = LAT["FCC"]
def d3_parity(cut2):
    r = int(math.isqrt(cut2))+1
    o = [(a,b,c3) for a in range(-r,r+1) for b in range(-r,r+1)
         for c3 in range(-r,r+1)
         if (a%2==b%2==c3%2) and a*a+b*b+c3*c3<=cut2]
    o.sort(key=lambda t:(t[0]**2+t[1]**2+t[2]**2,t)); return o
S = FCCL["s"]
Bmat = S*np.array([[1,1,1],[1,1,-1],[1,-1,1]],dtype=float).T
V_CELL = (2*math.pi)**3/abs(np.linalg.det(Bmat))
def kmesh(nk):
    f = (np.arange(nk)+0.5)/nk
    return [Bmat@np.array([x,y,z]) for x in f for y in f for z in f]
class EngineF:
    def __init__(self, cut2, nk, grid):
        self.grid_n = grid
        self.Gs = d3_parity(cut2); self.kpts = kmesh(nk)
        nG = len(self.Gs)
        self.W2 = np.zeros((nG,nG)); self.W4 = np.zeros((nG,nG))
        dmap = {}
        for i,Gi in enumerate(self.Gs):
            for j,Gj in enumerate(self.Gs):
                d = (Gi[0]-Gj[0],Gi[1]-Gj[1],Gi[2]-Gj[2])
                self.W2[i,j] = FCCL["P2"].get(d,0)
                self.W4[i,j] = FCCL["P4"].get(d,0)
                dmap.setdefault(d, []).append((i,j))
        maxax = max(max(abs(d[0]),abs(d[1]),abs(d[2])) for d in dmap)
        claim_true(f"nyq_fcc_grid{grid}", 3*maxax < grid//2,
                   f"3*{maxax} < {grid//2}")
        self.dlist = list(dmap)
        self.iidx = [np.array([p[0] for p in dmap[d]]) for d in self.dlist]
        self.jidx = [np.array([p[1] for p in dmap[d]]) for d in self.dlist]
        self.fidx = [tuple(c % grid for c in d) for d in self.dlist]
        Gp = S*np.array(self.Gs,dtype=float)
        self.den = []
        for kv in self.kpts:
            q = Gp + kv[None,:]
            self.den.append(C*((np.einsum("ij,ij->i",q,q))-Q0*Q0)**2)
        ax = np.arange(grid)*(2*np.pi/grid)
        X,Y,Z = np.meshgrid(ax,ax,ax,indexing="ij")
        self.phi1 = np.zeros_like(X)
        for kv in FCCL["shell"]:
            self.phi1 += np.cos(kv[0]*X+kv[1]*Y+kv[2]*Z)
    def F_exact(self, A, M):
        n,N4,N6 = FCCL["n"],FCCL["N4"],FCCL["N6"]
        mH2 = R + 3*U*M + 15*V*M*M
        W = ((3*U+30*V*M)*A*A)*self.W2 + (5*V*A**4)*self.W4
        tot = 0.0
        acc = np.zeros(len(self.dlist))
        for den in self.den:
            K = W.copy(); K[np.diag_indices_from(K)] += mH2 + den
            sgn, ld = np.linalg.slogdet(K)
            if sgn <= 0: return None
            tot += ld
            Ki = np.linalg.inv(K)
            for t,(ii,jj) in enumerate(zip(self.iidx,self.jidx)):
                acc[t] += Ki[ii,jj].sum()
        norm = 1.0/(V_CELL*len(self.kpts))
        arr = np.zeros((self.grid_n,)*3, dtype=complex)
        for t,fi in enumerate(self.fidx):
            arr[fi] += acc[t]*norm
        sig = np.real(np.fft.ifftn(arr))*self.grid_n**3
        p1 = self.phi1
        sbar=float(sig.mean()); p2s=float((A*A*p1*p1*sig).mean())
        s2=float((sig*sig).mean()); p2s2=float((A*A*p1*p1*sig*sig).mean())
        s3=float((sig**3).mean())
        Fcl = R*n*A*A + 0.25*U*N4*A**4 + (V/6)*N6*A**6
        rem = (-(0.5)*(3*U*M+15*V*M*M)*sbar - 15*V*M*p2s
               + 0.75*U*s2 + 7.5*V*p2s2 + 2.5*V*s3)
        return Fcl + 0.5*tot*norm + rem
    def F_diag_basis(self, A, M):
        n,N4,N6 = FCCL["n"],FCCL["N4"],FCCL["N6"]
        mH2 = R + 3*U*M + 15*V*M*M
        rhat = mH2 + (3*U+30*V*M)*2*n*A*A + 5*V*N4*A**4
        tot=0.0; sb=0.0
        for den in self.den:
            tot += float(np.sum(np.log(rhat+den)))
            sb  += float(np.sum(1.0/(rhat+den)))
        norm = 1.0/(V_CELL*len(self.kpts))
        Mt = sb*norm
        Fcl = R*n*A*A + 0.25*U*N4*A**4 + (V/6)*N6*A**6
        rem = (-(0.5)*(3*U*M+15*V*M*M)*Mt - 15*V*M*(2*n*A*A)*Mt
               + 0.75*U*Mt*Mt + 7.5*V*(2*n*A*A)*Mt*Mt + 2.5*V*Mt**3)
        return Fcl + 0.5*tot*norm + rem

EF = EngineF(9, 4, 48)   # parity lattice: norms 3,4,8,9... cut 9 first shells
F0e = EF.F_exact(0.0, MR)
claim("fcc_A0_identity", EF.F_diag_basis(0.0, MR), F0e, 1e-10)
fcc_rows = []
mn_fcc = (np.inf, None)
for A in (0.02, 0.05, 0.08, 0.11, 0.14):
    for mf in (0.5, 0.7, 1.0, 1.5, 2.0):
        M = mf*MR
        Fex = EF.F_exact(A, M)
        if Fex is None: continue
        d, rhat = F_diag_cont_rel(FCCL, A, M)
        anc = d + (Fex - EF.F_diag_basis(A, M))
        fcc_rows.append(dict(A=A, M_over_MR=mf, dF_anchored=anc))
        if anc < mn_fcc[0]: mn_fcc = (anc, (A, mf))
record("FCC_exactWick_min_anchored", dict(dF=mn_fcc[0], at=mn_fcc[1]),
       f"{len(fcc_rows)} points, parity-lattice cut 9 / grid 48")

verdicts = {}
for nm in ("LAM","HEX","FCC"):
    v = results[nm]["min_est_worstcase"]
    verdicts[nm] = "PASS" if v > 0 else ("BORDERLINE" if v > -1e-4 else "FAIL")
verdicts["FCC_exactWick"] = ("PASS" if mn_fcc[0] > 0 else
                             ("BORDERLINE" if mn_fcc[0] > -1e-4 else "FAIL"))
record("G1pp3_verdicts", verdicts, "estimator rho=1 (all) + exact-Wick (FCC)")

out = dict(theory_tag="Math431", date="2026-06-04", r_R=rR, M_R=MR,
           estimator=results, fcc_exact=fcc_rows, verdicts=verdicts,
           claims=CLAIMS)
os.makedirs("Runs/math/Math431", exist_ok=True)
json.dump(out, open("Runs/math/Math431/g1pp3_lam_hex_fcc.json","w"), indent=1)
npass = sum(1 for c in CLAIMS if c.get("passed"))
for nm in ("LAM","HEX","FCC"):
    print(f"{nm}: estimator(rho=1) min = {results[nm]['min_est_worstcase']:+.6f} at {results[nm]['at']}")
print(f"FCC exact-Wick anchored min = {mn_fcc[0]:+.6f} at {mn_fcc[1]}")
print(f"VERDICTS: {verdicts}  (claims {npass}/{len(CLAIMS)})")
sys.exit(0)
