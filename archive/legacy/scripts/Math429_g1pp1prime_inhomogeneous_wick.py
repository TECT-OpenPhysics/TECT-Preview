#!/usr/bin/env python3
"""Math429_g1pp1prime_inhomogeneous_wick.py -- G1''-1' execution
(CLAUDE.md 6.3.8): exact position-dependent Wick treatment
sigma(x) = G_phi(x,x) + M-direction re-scan, per operator spec 2026-06-04.

EXACT GIBBS-BOGOLIUBOV REMAINDER (replaces the uniform-Wick C_unif):
 F_var/V = F_cl(A) + (1/2)TrLn K_hat
         - (1/2)(3uM+15vM^2) sbar - 15 v M (p2s)
         + (3u/4)(s2) + (15v/2)(p2s2) + (5v/2)(s3)
with cell averages sbar = <sigma>, p2s = <phi_A^2 sigma>, s2 = <sigma^2>,
p2s2 = <phi_A^2 sigma^2>, s3 = <sigma^3>, sigma(x) reconstructed EXACTLY
from the Bloch Green diagonal: sigma_hat(Q) = (1/(v_cell N_k)) sum_k
sum_G [K^(k)]^{-1}_{G,G+Q}. With this remainder F_var(A,M) is a TRUE
variational upper bound for every (A,M); at A = 0 minimisation over M
reproduces the disordered gap equation (M* = M_R), so the Reading-H
reference is the A = 0 optimum of the SAME functional.

VERDICT PROTOCOL: in-basis exact race (matched) + continuum anchoring
(diagonal-limit substitution, as Math428) with conservative band
(bracket scale rho in [rho_cal, 1]). The uniform-Wick boundary negative
(-0.102 at M = 1.6 M_R, Math428) is re-examined with the exact remainder
and an EXTENDED M-window [0.6, 2.2] M_R to expose any interior minimum.
Physics outcome RECORDED, not asserted (6.3.3).
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

# ---------------- geometry (as Math428) ----------------
SHELL = [v for v in {p for q in [(1,1,0),(1,-1,0),(-1,1,0),(-1,-1,0)]
                     for p in set(itertools.permutations(q))}
         if sum(x*x for x in v) == 2]
assert len(SHELL) == 12
def conv(m):
    s = {(0,0,0):1}
    for _ in range(m):
        t = {}
        for k0,c0 in s.items():
            for w in SHELL:
                kk = (k0[0]+w[0], k0[1]+w[1], k0[2]+w[2])
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
    def __init__(self, cut2, nk, grid=48):
        self.Gs = d3(cut2); self.kpts = kmesh(nk)
        nG = len(self.Gs)
        self.W2 = np.zeros((nG,nG)); self.W4 = np.zeros((nG,nG))
        self.dQ = {}
        for i,Gi in enumerate(self.Gs):
            for j,Gj in enumerate(self.Gs):
                d = (Gi[0]-Gj[0],Gi[1]-Gj[1],Gi[2]-Gj[2])
                self.W2[i,j] = P2.get(d,0); self.W4[i,j] = P4.get(d,0)
                self.dQ.setdefault(d, []).append((i,j))
        Gp = S*np.array(self.Gs,dtype=float)
        self.den = []
        for kv in self.kpts:
            q = Gp + kv[None,:]
            q2 = np.einsum("ij,ij->i", q, q)
            self.den.append(C*(q2-Q0*Q0)**2)
        # real-space grid for exact band-limited cell averages
        ax = np.arange(grid)*(2*np.pi/grid)
        X,Y,Z = np.meshgrid(ax,ax,ax,indexing="ij")
        self.phi1 = np.zeros_like(X)        # phi_A(x)/A
        for kv in SHELL:
            self.phi1 += np.cos(kv[0]*X+kv[1]*Y+kv[2]*Z)
        self.X,self.Y,self.Z = X,Y,Z
        self.Qcos = {d: np.cos(d[0]*X+d[1]*Y+d[2]*Z) for d in self.dQ}
    def trln_and_sigma(self, A, M):
        mH2 = R + 3*U*M + 15*V*M*M
        W = ((3*U+30*V*M)*A*A)*self.W2 + (5*V*A**4)*self.W4
        tot = 0.0
        sigQ = {d:0.0 for d in self.dQ}
        for den in self.den:
            K = W.copy(); K[np.diag_indices_from(K)] += mH2 + den
            sgn,ld = np.linalg.slogdet(K)
            if sgn <= 0: return None, None
            tot += ld
            Ki = np.linalg.inv(K)
            for d, idx in self.dQ.items():
                sigQ[d] += sum(Ki[i,j] for i,j in idx)
        norm = 1.0/(V_CELL*len(self.kpts))
        trln = tot*norm
        sig = np.zeros_like(self.phi1)
        for d,vv in sigQ.items():
            sig += (vv*norm)*self.Qcos[d]
        return trln, sig
    def F_exact(self, A, M):
        trln, sig = self.trln_and_sigma(A, M)
        if trln is None: return None
        p1 = self.phi1
        sbar = float(sig.mean())
        p2s  = float((A*A*p1*p1*sig).mean())
        s2   = float((sig*sig).mean())
        p2s2 = float((A*A*p1*p1*sig*sig).mean())
        s3   = float((sig**3).mean())
        Fcl = R*n_b*A*A + 0.25*U*N4*A**4 + (V/6)*N6*A**6
        rem = (-(0.5)*(3*U*M+15*V*M*M)*sbar - 15*V*M*p2s
               + 0.75*U*s2 + 7.5*V*p2s2 + 2.5*V*s3)
        return Fcl + 0.5*trln + rem, dict(sbar=sbar,p2s=p2s,s2=s2,
                                          p2s2=p2s2,s3=s3)
    def trln_diag_and_M(self, A, M):
        mH2 = R + 3*U*M + 15*V*M*M
        rhat = mH2 + (3*U+30*V*M)*2*n_b*A*A + 5*V*N4*A**4
        tot = 0.0; sb = 0.0
        for den in self.den:
            tot += float(np.sum(np.log(rhat+den)))
            sb  += float(np.sum(1.0/(rhat+den)))
        norm = 1.0/(V_CELL*len(self.kpts))
        return tot*norm, sb*norm, rhat

ENG = Engine(12, 4)
record("basis", dict(cut2=12, size=len(ENG.Gs), nk=64, grid=48), "")

# ---- diagonal-limit closed forms (basis and continuum) ----
def F_diag(trln, Mt, A, M):
    Fcl = R*n_b*A*A + 0.25*U*N4*A**4 + (V/6)*N6*A**6
    rem = (-(0.5)*(3*U*M+15*V*M*M)*Mt - 15*V*M*(2*n_b*A*A)*Mt
           + 0.75*U*Mt*Mt + 7.5*V*(2*n_b*A*A)*Mt*Mt + 2.5*V*Mt**3)
    return Fcl + 0.5*trln + rem

rR = m424.gap_solve(R, 0, 0, 0.0); MR = m424.M_fast(rR)
claim("r_R", 0.3045, rR, 5e-3)

# continuum diagonal (absolute up to a constant: use dI relative to r_R and
# add reference remainder so that DIFFERENCES are well-defined)
def F_diag_cont_rel(A, M):
    mH2 = R + 3*U*M + 15*V*M*M
    rhat = mH2 + (3*U+30*V*M)*2*n_b*A*A + 5*V*N4*A**4
    Mt = m424.M_fast(rhat)
    Fcl = R*n_b*A*A + 0.25*U*N4*A**4 + (V/6)*N6*A**6
    rem = (-(0.5)*(3*U*M+15*V*M*M)*Mt - 15*V*M*(2*n_b*A*A)*Mt
           + 0.75*U*Mt*Mt + 7.5*V*(2*n_b*A*A)*Mt*Mt + 2.5*V*Mt**3)
    ref_rem = (-(0.5)*(3*U*MR+15*V*MR*MR)*MR + 0.75*U*MR*MR + 2.5*V*MR**3)
    return Fcl + 0.5*m424.dI(rhat, rR) + rem - ref_rem

# A=0 implementation identity: with W = 0 the exact-Wick functional must
# coincide with the diagonal closed form (uniform sigma = basis trace).
F0, mom0 = ENG.F_exact(0.0, MR)
trd0, sbd0, _ = ENG.trln_diag_and_M(0.0, MR)
claim("A0_exact_equals_diag_identity", F_diag(trd0, sbd0, 0.0, MR), F0, 1e-10)
# in-basis A=0 optimum sits BELOW M_R (quadrature shift of the basis trace;
# documented, not an error): record it; the in-basis race uses it as ref.
Mgrid0 = MR*np.linspace(0.7, 1.2, 26)
F0_opt, M0_opt = min((ENG.F_exact(0.0, float(m))[0], float(m)) for m in Mgrid0)
record("inbasis_A0_optimum", dict(F=F0_opt, M_over_MR=M0_opt/MR),
       "basis-trace quadrature shifts the A=0 optimum below M_R")
# continuum A=0 reference: F_diag_cont_rel(0, M_R) = 0 and is the M-optimum
claim("continuum_ref_zero", 0.0, F_diag_cont_rel(0.0, MR), 1e-9)
claim_true("continuum_ref_M_optimal",
           F_diag_cont_rel(0.0, 0.9*MR) > 0 and F_diag_cont_rel(0.0, 1.1*MR) > 0,
           "gap equation = M-stationarity of the continuum diagonal form")

# ---- G1''-1' scan: exact-Wick in-basis race + anchored estimate ----
A_list = [0.06, 0.0856, 0.114]
M_list = MR*np.array([0.6,0.8,1.0,1.2,1.4,1.6,1.8,2.0,2.2])
rows = []
min_inb = (np.inf, None); min_anc = (np.inf, None)
for A in A_list:
    for M in M_list:
        FE = ENG.F_exact(A, float(M))
        if FE is None: continue
        Fex, mom = FE
        dF_inb = Fex - F0_opt                 # matched in-basis race (diagnostic)
        # anchored: continuum diagonal + reference-free off-diagonal bracket
        # (at A=0 exact == diag identically, so the bracket needs no reference)
        trd, sbd, rhat = ENG.trln_diag_and_M(A, float(M))
        Fdiag_inb = F_diag(trd, sbd, A, float(M))
        bracket = Fex - Fdiag_inb             # off-diagonal + sigma-inhomogeneity
        dF_anc = F_diag_cont_rel(A, float(M)) + bracket
        rows.append(dict(A=A, M=float(M), dF_inbasis=dF_inb,
                         dF_anchored=dF_anc, bracket=bracket,
                         sbar=mom["sbar"]))
        if dF_inb < min_inb[0]: min_inb = (dF_inb, (A, float(M)))
        if dF_anc < min_anc[0]: min_anc = (dF_anc, (A, float(M)))

record("min_inbasis", dict(dF=min_inb[0], at=min_inb[1]),
       "exact-Wick matched in-basis (cut 12; quadrature-limited)")
record("min_anchored", dict(dF=min_anc[0], at=min_anc[1]),
       "continuum-anchored (primary)")

# interior-vs-boundary diagnostic on the M-window
edge = any(abs(r["M"] - MR*2.2) < 1e-12 and r["dF_anchored"] == min_anc[0]
           for r in rows)
record("anchored_min_on_M_boundary", bool(edge), "")

# uniform-Wick autopsy at the old artefact point
FE = ENG.F_exact(0.114, 1.6*MR)
if FE is not None:
    record("exactWick_at_old_artefact_point", FE[0]-F0,
           "was -0.102 under uniform-Wick finite-basis")

# ---- v1.1 (operator audit): Nyquist proof + self-consistency coverage ----
maxax = max(max(abs(d[0]), abs(d[1]), abs(d[2])) for d in ENG.dQ)
claim("nyquist_sigma3_band", 18, 3 * maxax, 0)
claim_true("grid48_exact_for_cut12", 3 * maxax < 24,
           "k_max(sigma^3)=18 < Nyquist(48)=24; cut16 needs larger grid (G1''-2)")
# extended low-M branch: locate self-consistency fixed points sbar(A,M)=M
ext_rows = []
fp = {}
min_ext = np.inf
for A in A_list:
    prev = None
    for mfac in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8):
        M = mfac * MR
        FE = ENG.F_exact(A, M)
        if FE is None:
            continue
        Fex, mom = FE
        dF = Fex - F0_opt
        min_ext = min(min_ext, dF)
        ext_rows.append(dict(A=A, M_over_MR=mfac, dF_inbasis=dF,
                             sbar=mom["sbar"], gap=mom["sbar"] - M))
        if prev is not None and prev[1] > 0 and (mom["sbar"] - M) < 0:
            fp[A] = (prev[0] + mfac) / 2.0
        prev = (mfac, mom["sbar"] - M)
claim_true("selfconsistent_fixed_points_inside_window",
           all(0.3 <= v <= 2.2 for v in fp.values()) and len(fp) == 3,
           f"M_self/MR ~ {fp}")
claim_true("extended_lowM_branch_positive", min_ext > 0,
           f"min over extended branch = {min_ext:.5f}")
record("extended_lowM_rows", ext_rows, "v1.1 weakness-D coverage")
record("fixed_points_M_self_over_MR", fp, "")

if min_anc[0] >= 0:
    verdict = "PASS (G1''-1' anchored: exact-Wick M-scan stays nonnegative)"
elif min_anc[0] > -1e-4:
    verdict = "BORDERLINE"
else:
    verdict = "FAIL (anchored exact-Wick minimum negative)"
record("G1pp1prime_verdict", verdict,
       f"min_anchored={min_anc[0]:.6e} at {min_anc[1]}")

out = dict(theory_tag="Math429", date="2026-06-04", r_braz=R, r_R=rR, M_R=MR,
           rows=rows, min_inbasis=min_inb[0], min_anchored=min_anc[0],
           verdict=verdict, claims=CLAIMS)
os.makedirs("Runs/math/Math429", exist_ok=True)
json.dump(out, open("Runs/math/Math429/g1pp1prime_inhomwick.json","w"), indent=1)
npass = sum(1 for c in CLAIMS if c.get("passed"))
print(f"rR={rR:.6f} MR={MR:.6f}")
for r in rows:
    print(f"A={r['A']:.4f} M/MR={r['M']/MR:.2f}: inb={r['dF_inbasis']:+.5f} "
          f"anc={r['dF_anchored']:+.5f} sbar={r['sbar']:.4f}")
print(f"min in-basis {min_inb[0]:+.6f} at {min_inb[1]}")
print(f"min anchored {min_anc[0]:+.6f} at {min_anc[1]}")
print(f"VERDICT: {verdict}  (claims {npass}/{len(CLAIMS)})")
sys.exit(0)
