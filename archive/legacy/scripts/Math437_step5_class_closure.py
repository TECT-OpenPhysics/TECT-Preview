#!/usr/bin/env python3
"""Math437_step5_class_closure.py (v1.1, post-Math440 R1 repair) -- Step-5
(H4 exhaustiveness) closure at
the isotropic self-consistent-Hartree comparison layer (CLAUDE.md 6.3.8).

THEOREM A (pattern-universal restoration, Math437 S3). At corrected
canonical (r = mu2 = 0.005, u = -0.86, v = +3.24, C = 1, q0 per Math426),
for ANY real condensate pattern psi (<psi^2> = 1, P4 = <psi^4>, P6 =
<psi^6>, arbitrary spectrum/phases/amplitudes) and ANY isotropic Gaussian
dressing sigma with cell average M > 0 in the PD set, the fixed-dressing
condensate polynomial

  Phi(t; M, P4, P6) = (kap/2) t^2 + (u_eff(M)/4) P4 t^4 + (v/6) P6 t^6,
  kap >= rhat0(M) = r + 3uM + 15vM^2  (kernel bound K >= r),
  u_eff(M) = u + 10 v M,

satisfies:
 [Region I]  M >= -u/(10v) = 43/1620:  u_eff >= 0  =>  Phi > 0 for t > 0
             (all coefficients positive; no discriminant needed);
 [Region II] M <  43/1620:  Phi >= -9|u|^3/(64 v^2)  (Lemma B; uses
             Cauchy-Schwarz P6 >= P4^2 [Math425] and P4 >= <psi^2>^2 = 1).
Combined with the A=0 layer penalty Delta0 = inf_{trials with
M < 43/1620} [F0(trial) - F0(gap point)] > 9|u|^3/(64 v^2)  (claim D)
and the A=0 unique-minimum certification (claim C), this gives
F_var[pattern] >= F_var[R_H] on the WHOLE isotropic-Hartree layer for
EVERY pattern -- the H4 enumeration burden is discharged at this layer.

Closed forms verified here:
  PD-branch roots of rhat0: M_pm = [-3u +- sqrt(9u^2 - 60 v r)]/(30 v);
  u_eff(M_+) = +sqrt(9u^2 - 60 v r)/3 > 0  (upper branch ALWAYS Region I);
  Lemma-B dip bound: inf Phi >= -9|u|^3/(64 v^2).
Self-test asserts cover every numerical claim of the Math437 note.
JSON: Runs/math/Math437/step5_class_closure.json
"""
import json, math, os, sys
import numpy as np

sys.path.insert(0, "Codes/supplementary")
import Math424_AddA_reading_uniqueness as m424

U, V, R = -0.86, 3.24, 0.005
Q0 = 0.6801747616
RSTAR = U * U / (4 * V)
CLAIMS = []
def claim(name, expected, actual, tol, detail=""):
    ok = (abs(actual - expected) <= tol) if tol else (expected == actual)
    CLAIMS.append(dict(name=name, expected=expected, actual=actual,
                       tol=tol, passed=bool(ok), detail=detail))
    assert ok, f"FAIL {name}: {expected} vs {actual}"
def claim_true(name, cond, detail=""):
    CLAIMS.append(dict(name=name, expected=True, actual=bool(cond),
                       tol=0, passed=bool(cond), detail=detail))
    assert cond, f"FAIL {name}: {detail}"
def record(name, value, detail=""):
    CLAIMS.append(dict(name=name, recorded=value, detail=detail,
                       passed=True, tol=None, expected=None, actual=value))

# ---------------- A. exact constants and closed-form lemmas ----------------
claim("rstar_exact", (43/180)**2, RSTAR, 1e-15)
disc = 9*U*U - 60*V*R
claim("PD_disc", 5.6844, disc, 1e-12, "9u^2-60vr")
Mm = (-3*U - math.sqrt(disc)) / (30*V)
Mp = (-3*U + math.sqrt(disc)) / (30*V)
claim("M_minus", 0.0020144240909808326, Mm, 1e-12)
claim("M_plus", 0.051071995662105595, Mp, 1e-12)
MC = -U / (10*V)                       # u_eff sign boundary = 43/1620
claim("Mc_exact_43_over_1620", 43/1620, MC, 1e-15)
claim_true("upper_branch_in_RegionI", Mp > MC,
           f"M_+ = {Mp:.7f} > -u/10v = {MC:.7f}")
ueff_Mp = U + 10*V*Mp
claim("ueff_Mp_closed_form", math.sqrt(disc)/3, ueff_Mp, 1e-12,
      "u_eff(M_+) = sqrt(9u^2-60vr)/3 -- positive for ANY r in the "
      "two-branch regime: upper PD branch is ALWAYS Region I")
DIP = 9 * abs(U)**3 / (64 * V * V)
claim("LemmaB_dip_bound", 0.0085206, DIP, 1e-6, "9|u|^3/(64 v^2)")
# dressed-CS margin at the self-consistent point (belt-and-braces)
rR_expect = 0.30452570866744433
claim("dressed_CS_margin", 5.3361995461466725, 4*rR_expect*V/(U*U), 1e-9,
      "4 r_R v/u^2 >> 1: CS no-condensation criterion holds at the "
      "self-consistent dressing even where positivity is not used")

# ---------------- B. gap point + Math436 rhat cross-anchor -----------------
rR = m424.gap_solve(R, 0, 0, 0.0)
claim("gap_rR", rR_expect, rR, 5e-9)
MR = m424.M_fast(rR)
claim("gap_MR", 0.10941432918723439, MR, 2e-5)
claim_true("MR_in_RegionI", MR > MC, f"M_R = {MR:.6f} > {MC:.6f}")
rhat_hex = rR + 6*U*3*1e-4 + 60*V*3*1e-4*MR + 5*V*90*1e-8
claim("Math436_rhat_argmin_reproduced", 0.30937333234566977, rhat_hex, 5e-5,
      "HEX argmin dressed mass from the gap-source formula")

# ---------------- C. A=0 layer: unique minimum (consistent quadrature) ----
# dI and M must share ONE quadrature (same _QG grid + same analytic tail),
# otherwise the exact stationarity-zero structure breaks at the 1e-6 level
# (diagnosed on first execution: mixed-grid dip -9.1e-7; root cause
# quadrature inconsistency, NOT physics -- documented in note S6).
_QG, _DEN0 = m424._QG, m424._DEN0
_TAIL = 1.0 / (1.0 * _QG[-1]) / (2 * np.pi ** 2)   # d/dm of dI tail, C=1
def M_qg(m):
    val = np.trapz(_QG**2 / (m + _DEN0), _QG) / (2 * np.pi**2)
    return float(val + _TAIL)
def gap_qg():
    lo, hi = 1e-3, 5.0
    f = lambda m: m - (R + 3*U*M_qg(m) + 15*V*M_qg(m)**2)
    for _ in range(200):
        mid = math.sqrt(lo*hi)
        if f(mid) > 0: hi = mid
        else: lo = mid
    return math.sqrt(lo*hi)
rRq = gap_qg(); MRq = M_qg(rRq)
claim_true("gap_scheme_offset_bounded", abs(rRq - rR) < 7e-3,
           f"coarse-_QG scheme gap {rRq:.6f} vs production {rR:.6f}: "
           f"offset {abs(rRq-rR):.2e} (scheme-internal layer; converges "
           f"under refinement -- next claims)")
record("MRq_consistent", MRq, "")
# refinement convergence: 6x denser grid, same tail treatment
_QG2 = m424._grid_q(n_points=24000)
_DEN02 = (_QG2**2 - Q0**2)**2
_TAIL2 = 1.0 / _QG2[-1] / (2*np.pi**2)
def M_qg2(m):
    return float(np.trapz(_QG2**2/(m + _DEN02), _QG2)/(2*np.pi**2) + _TAIL2)
def dI2(m, ref):
    v = np.trapz(_QG2**2*np.log((m + _DEN02)/(ref + _DEN02)), _QG2)/(2*np.pi**2)
    return float(v + (m - ref)/_QG2[-1]/(2*np.pi**2))
lo2, hi2 = 1e-3, 5.0
f2 = lambda m: m - (R + 3*U*M_qg2(m) + 15*V*M_qg2(m)**2)
for _ in range(200):
    mid = math.sqrt(lo2*hi2)
    if f2(mid) > 0: hi2 = mid
    else: lo2 = mid
rRq2 = math.sqrt(lo2*hi2); MRq2 = M_qg2(rRq2)
claim_true("scheme_internally_converged",
           abs(rRq2 - rRq) < 5e-5,
           f"coarse vs 4x-refined scheme gap: {rRq:.6f} vs {rRq2:.6f} "
           f"(internal drift {abs(rRq2-rRq):.1e})")
record("scheme_vs_production_systematic",
       dict(gap_offset=rRq2 - rR, M_at_rR_scheme=M_qg2(rR),
            M_at_rR_production=MR),
       "measure-convention delta of loop_integral_full vs plain "
       "trapz+tail; scheme-internal layer structure unaffected; "
       "load-bearing Region claims use PRODUCTION anchors")
def dF0_2(rhat):
    M = M_qg2(rhat)
    return (0.5*dI2(rhat, rRq2) + 0.5*((R - rhat)*M - (R - rRq2)*MRq2)
            + 0.75*U*(M*M - MRq2*MRq2) + 2.5*V*(M**3 - MRq2**3))
def dF0(rhat):
    """A=0 isotropic GB energy difference vs the gap point (consistent)."""
    M = M_qg(rhat)
    return (0.5*m424.dI(rhat, rRq) + 0.5*((R - rhat)*M - (R - rRq)*MRq)
            + 0.75*U*(M*M - MRq*MRq) + 2.5*V*(M**3 - MRq**3))
rh_grid = np.geomspace(2e-3, 39.0, 400)
vals = np.array([dF0(r) for r in rh_grid])
claim_true("A0_layer_nonnegative", float(vals.min()) >= -1e-9,
           f"min dF0 = {vals.min():.3e} (consistent quadrature)")
i0 = int(np.argmin(np.abs(rh_grid - rRq)))
claim_true("A0_zero_at_gap", abs(dF0(rRq)) <= 1e-12,
           f"dF0(gap) = {dF0(rRq):.3e}")
left = vals[:i0]; right = vals[i0:]
claim_true("A0_monotone_flanks",
           bool(np.all(np.diff(left) <= 1e-9) and
                np.all(np.diff(right) >= -1e-9)),
           "dF0 decreasing then increasing (unique minimum)")

# ---------------- D. Region-II penalty Delta0 ------------------------------
# Region II trials have sigma-bar = M_qg(rhat) < Mc  <=>  rhat > r_c.
lo, hi = rRq, 39.0
for _ in range(200):
    mid = math.sqrt(lo*hi)
    if M_qg(mid) > MC: lo = mid
    else: hi = mid
r_c = math.sqrt(lo*hi)
record("r_c_RegionII_boundary", r_c, "M_qg(r_c) = 43/1620")
claim("Mc_at_rc", MC, M_qg(r_c), 2e-9)
d0_rc = dF0(r_c)
rh2 = np.geomspace(r_c, 39.0, 200)
d0_min = min(dF0(r) for r in rh2)
claim_true("Delta0_exceeds_dip",
           d0_min > DIP * 1.5,
           f"inf RegionII dF0 = {d0_min:.5f} > 1.5 x dip {DIP:.5f}")
record("Delta0_RegionII", d0_min, f"at boundary r_c: {d0_rc:.5f}")
# refined-scheme stability of the Region-II penalty conclusion
lo3, hi3 = rRq2, 39.0
for _ in range(200):
    mid = math.sqrt(lo3*hi3)
    if M_qg2(mid) > MC: lo3 = mid
    else: hi3 = mid
r_c2 = math.sqrt(lo3*hi3)
d0_min2 = min(dF0_2(r) for r in np.geomspace(r_c2, 39.0, 40))
claim_true("Delta0_refined_stable", d0_min2 > DIP * 1.5,
           f"refined-scheme inf RegionII dF0 = {d0_min2:.5f}")
record("Delta0_refined", dict(r_c2=r_c2, d0_min2=d0_min2), "")

# ---------------- D2. Math440-R1 band repair: M in (Mc, M_plus) -----------
# Math440 F1 (UPHELD): the v1.0 proof asserted all-positive coefficients on
# M >= Mc, but rhat0(M) < 0 on (M_minus, M_plus); on the band (Mc, M_plus)
# u_eff > 0 yet kappa >= rhat0 can be negative. Repair (auditor-supplied,
# independently re-derived here):
#   band kappa floor:  rhat0 decreasing on (0, Mc] and increasing on
#                      [Mc, inf) (d rhat0/dM = 3 u_eff), so
#                      min_{band} rhat0 = rhat0(Mc) = r - 3u^2/(20v)... :
rh0_Mc = R + 3*U*MC + 15*V*MC*MC
claim("rhat0_Mc_exact", -0.029240740740740737, rh0_Mc, 1e-12,
      "= r - 9u^2/(40v) + 9u^2/(108.. ) closed-form band minimum")
claim("rhat0_stationary_at_Mc", 0.0, 3*U + 30*V*MC, 1e-12,
      "d rhat0/dM = 3(u + 10vM) vanishes exactly at Mc")
#   band dip (u_eff >= 0, kappa >= rh0_Mc, sextic term only):
#   min_x [ (kappa/2) x + (v/6) P6 x^3 ] >= -(1/3)|kappa|^{3/2}/sqrt(v)
#   (P6 >= P4^2 >= 1; the u_eff P4 x^2 term is nonnegative on the band)
DIP_BAND = abs(rh0_Mc)**1.5 / (3.0*math.sqrt(V))
claim("band_dip_closed_form", 9.259526852124812e-04, DIP_BAND, 1e-12,
      "(1/3)|rhat0(Mc)|^{3/2}/sqrt(v); rhat0(Mc) = r - 3u^2/(20v) exact; "
      "this closed form UPPER-bounds the auditor scan value 9.249e-4 "
      "(P6 >= 1 stiffens the sextic - safe direction)")
#   anchor inequality: ln((m+D)/(rR+D)) >= 1 - (rR+D)/(m+D) pointwise =>
#   dI(m, rR) >= (m - rR) M(m) => the trial-mass term cancels EXACTLY:
#   dF0(m) >= PB(M) := (1/2)(r-rR)(M-MR) + (3/4)u(M^2-MR^2)
#                      + (5/2)v(M^3-MR^3)   for m >= rR (M <= MR).
def PB(M):
    return (0.5*(R - rR)*(M - MR) + 0.75*U*(M*M - MR*MR)
            + 2.5*V*(M**3 - MR**3))
claim("PB_at_Mplus", 0.0052459635246063716, PB(Mp), 1e-12,
      "anchor-only penalty floor at the band's right edge")
claim("PB_at_Mc", 0.0092198664169367995, PB(MC), 1e-12,
      "anchor-only penalty floor at the band's left edge / Region-II edge")
# PB is decreasing in M on (0, M_plus]: dPB/dM = (1/2)(r-rR) + (3/2)uM
# + 7.5vM^2 < 0 there (numeric sweep):
_Ms = np.linspace(1e-6, Mp, 400)
_dPB = 0.5*(R - rR) + 1.5*U*_Ms + 7.5*V*_Ms*_Ms
claim_true("PB_decreasing_on_0_Mplus", bool(np.all(_dPB < 0)),
           f"max dPB/dM = {_dPB.max():.4e}")
# anchor ln-inequality spot check: dI(m,rR) >= (m-rR) M_qg(m), 3 spots
for _m in (1.0, 5.0, 24.353):
    lhs = m424.dI(_m, rRq); rhs = (_m - rRq)*M_qg(_m)
    claim_true(f"anchor_ln_ineq_m{_m}", lhs >= rhs - 1e-12,
               f"dI={lhs:.6f} >= (m-rR)M={rhs:.6f}")
# coverage: band dip vs band floor; Region-II dip vs Region-II floor
claim_true("band_covered", DIP_BAND < PB(Mp),
           f"band dip {DIP_BAND:.6e} < PB(M+) = {PB(Mp):.6e} "
           f"(margin {PB(Mp)/DIP_BAND:.2f}x)")
DIP_CLEAN_Q = abs(U)**3/(12.0*V*V)   # coupled quartic+sextic clean bound
claim("dip_clean_coupled_bound", 0.005049217598943249, DIP_CLEAN_Q, 1e-12)
claim_true("regionII_covered", DIP_CLEAN_Q + DIP_BAND < PB(MC),
           f"dip(coupled {DIP_CLEAN_Q:.6e} + kappa-part {DIP_BAND:.6e}) "
           f"< PB(Mc) = {PB(MC):.6e}")
record("Delta0_demoted", dict(Delta0=0.126465, role="comfort margin 13.7x"),
       "Math440 F7: load-bearing floor is now the anchor-only PB chain")

rng = np.random.default_rng(437)
worst = 0.0
for _ in range(4000):
    M = float(rng.uniform(1e-6, Mp))           # v1.1: cover the band too
    kap = R + 3*U*M + 15*V*M*M                 # v1.1 un-clipped: kappa floor
                                               # = rhat0(M), MAY be negative
    P4 = float(np.exp(rng.uniform(0, 6)))      # P4 >= 1
    P6 = P4*P4*float(np.exp(rng.uniform(0, 3)))  # P6 >= P4^2 (CS)
    ue = U + 10*V*M
    t2 = np.geomspace(1e-6, 50.0, 800)
    phi = 0.5*kap*t2 + 0.25*ue*P4*t2**2 + (V/6.0)*P6*t2**3
    worst = min(worst, float(phi.min()))
claim_true("LemmaB_adversary_within_bound",
           worst >= -(DIP_CLEAN_Q + DIP_BAND) - 1e-9,
           f"worst sampled dip {worst:.6f} vs coupled+band bound "
           f"{-(DIP_CLEAN_Q + DIP_BAND):.6f} (v1.1 un-clipped sampler)")
record("LemmaB_worst_sampled", worst, "4000 adversarial (M,P4,P6) draws")

# ---------------- F. gallery: enumerated + exotic spherical codes ----------
# Exact zero-sum counting requires EXACT arithmetic. Crystallographic sets:
# integer coordinates (m424 convention). Non-crystallographic: icosahedron
# in Q(sqrt5) component pairs (p, q) <-> p + q*sqrt5 (vertices x2); decagon
# via the Z[zeta_10] lift (zeta^j -> e_j in Z^5, zeta^{j+5} = -zeta^j;
# a sum vanishes iff the lifted vector is m*(1,1,1,1,1) -- minimal
# polynomial 1+x+x^2+x^3+x^4).
def count_zero(vectors, m, is_zero):
    sums = {tuple([0]*len(vectors[0])): 1}
    for _ in range(m):
        new = {}
        for s, cnt in sums.items():
            for w in vectors:
                t = tuple(si + wi for si, wi in zip(s, w))
                new[t] = new.get(t, 0) + cnt
        sums = new
    return sum(c for s, c in sums.items() if is_zero(s))
def is_zero_plain(s): return all(x == 0 for x in s)
def is_zero_qc10(s):  return len(set(s)) == 1          # m*(1,..,1)
TRIV4 = lambda n: 12*n*n - 6*n                          # trivial-pairing count
def gallery(name, pairs, is_zero=is_zero_plain):
    vs = []
    for p in pairs:
        vs.append(tuple(p)); vs.append(tuple(-x for x in p))
    n = len(pairs)
    N4 = count_zero(vs, 4, is_zero); N6 = count_zero(vs, 6, is_zero)
    P4 = N4/(4.0*n*n); P6 = N6/(8.0*n**3)
    Jl = N4*N4/(2.0*n*N6) if N6 else 0.0
    claim_true(f"gallery_{name}_P4_ge_1", P4 >= 1.0 - 1e-12, f"P4={P4:.4f}")
    claim_true(f"gallery_{name}_CS", P6 >= P4*P4 - 1e-12,
               f"P6={P6:.4f} >= P4^2={P4*P4:.4f} (J_latt={Jl:.4f})")
    claim_true(f"gallery_{name}_N4_ge_trivial", N4 >= TRIV4(n),
               f"N4={N4} >= 12n^2-6n={TRIV4(n)} (excess = resonant)")
    ue = U + 10*V*MR
    t2 = np.geomspace(1e-8, 25.0, 600)
    phi = 0.5*rR*t2 + 0.25*ue*P4*t2**2 + (V/6.0)*P6*t2**3
    claim_true(f"gallery_{name}_RegionI_positive", float(phi.min()) >= 0.0,
               f"min Phi = {phi.min():.3e} (all-positive coefficients)")
    record(f"gallery_{name}", dict(n=n, N4=N4, N6=N6,
                                   N4_resonant_excess=N4-TRIV4(n),
                                   P4=P4, P6=P6, J_latt=Jl))
    return N4, N6
# production four: reuse the m424 exact enumeration (integer coords)
for nm in ("LAM", "HEX", "FCC", "BCC"):
    c = m424.COMB[nm]
    pairs = []
    seen = set()
    for v in m424.SHELLS[nm]:
        if tuple(-x for x in v) not in seen:
            seen.add(tuple(v)); pairs.append(tuple(v))
    N4, N6 = gallery(nm, pairs)
    claim(f"{nm}_N4_matches_m424", c["N4"], N4, 0)
    claim(f"{nm}_N6_matches_m424", c["N6"], N6, 0)
claim("BCC_resonant_excess_is_144", 144,
      m424.COMB["BCC"]["N4"] - TRIV4(6), 0,
      "= the Math432 m31 4-wave SHG count, independent cross-check")
# exotic: simple cubic {100} and square (integer)
gallery("SC100", [(1,0,0),(0,1,0),(0,0,1)])
gallery("SQUARE", [(1,0,0),(0,1,0)])
# icosahedron vertices x2 in Q(sqrt5): coords {0,+-2,+-(1+sqrt5)} as (p,q)
Z, T, G = (0,0), (2,0), (1,1)
def neg(c): return (-c[0], -c[1])
ico = [(Z, T, G), (Z, T, neg(G)), (T, G, Z), (T, neg(G), Z),
       (G, Z, T), (neg(G), Z, T)]
ico_flat = [tuple(x for comp in v for x in comp) for v in ico]
gallery("ICOSA", ico_flat)
# decagon (n=5) via Z[zeta_10] lift: zeta^j -> e_j, j = 0..4
dec = [tuple(1 if i == j else 0 for i in range(5)) for j in range(5)]
gallery("QC10", dec, is_zero=is_zero_qc10)

# ---------------- summary ---------------------------------------------------
verdict = ("Step-5 layer closure HOLDS (v1.1 four-interval proof): "
           "I-prime all-positivity + band/Region-II anchor-only floors "
           "PB(M) vs closed-form dips + A=0 uniqueness; Delta0 demoted "
           "to comfort margin; pattern-universal")
record("Step5_verdict", verdict, "")
out = dict(theory_tag="Math437", date="2026-06-04",
           constants=dict(u=U, v=V, r=R, q0=Q0, rstar=RSTAR,
                          Mc=MC, M_minus=Mm, M_plus=Mp,
                          dip_bound=DIP, r_R=rR, M_R=MR, r_c=r_c),
           claims=CLAIMS)
os.makedirs("Runs/math/Math437", exist_ok=True)
json.dump(out, open("Runs/math/Math437/step5_class_closure.json","w"),
          indent=1)
npass = sum(1 for c in CLAIMS if c.get("passed"))
print(f"r_R={rR:.9f} M_R={MR:.6f} r_c={r_c:.4f} Delta0={d0_min:.5f} "
      f"dip={DIP:.6f}")
print(f"VERDICT: {verdict}")
print(f"claims {npass}/{len(CLAIMS)}")
sys.exit(0)
