"""scscope_mendpoint_eval.py -- SC-SCOPE / M-ENDPOINT: direct evaluation of the
sunset-endpoint dressing variance M(r_hat(I)) and the corrected sunset-axis
ratio, bypassing the factor-2 linearisation that previously made the endpoint a
candidate.

Background. The sunset-endpoint note (sunset-endpoint-refinement v1.0) estimated
the endpoint coupling via a linear-response slope M'(r_hat) and was found to have
used M' = -J(0) where the correct relation is M' = -J(0)/2 (useries-triage), so
the x1.34 estimate was invalidated. M-ENDPOINT is the registered missing
constant: the convexity-honest value M(r_hat(2e-3)) = M(0.33675). This script
evaluates it DIRECTLY by the dressing-variance quadrature (no linearisation, so
the factor-2 issue does not arise), cross-checks two independent quadratures, and
recomputes the sunset-axis ratio with the directly-dressed coupling.

Convention (production, identical to robustness_mu2_*.py and t6_mainline):
  r_hat(I) = r_R + 2 lam' I,  lam' = 3u + 30v M_R,  M_R = M(r_R),
  r_R = gap_solve(mu2),  M(m) = (1/2pi^2) int_0^inf k^2/D dk,  D = m + C(k^2-q0^2)^2.
Sunset endpoint bound (matched to the certified U4/U7 tables, single J0):
  b(I) = 1/2 u_eff(M)^2 (2I) * 6 J0 M,  u_eff(M) = u + 10 v M,
  composed margin = MARGIN (1 - 1/rho(I)),  ratio = composed / b.

The frozen-coupling U4 bound uses M = M_R (over-conservative); the physically
correct endpoint uses M = M(r_hat(I)) (each competitor at its OWN dressed kernel).

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-07"
__version_issued__ = "2026-06-07"
__claims__ = ["B5-BEYOND-LAYER-BOUND", "B1-RH-ENUM"]

import json, sys, math
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "archive" / "legacy" / "scripts"))
import Math424_AddA_reading_uniqueness as m424  # noqa: E402

U, V, Q0, C = m424.U, m424.V, m424.Q0, m424.C
MU2 = 0.005
MARGIN = 0.00432                      # Prop-A band layer margin (anchor)
RHO = {4e-4: 59.4, 1e-3: 8.8, 2e-3: 2.6}   # AddE de-thinned hardened ratios
CLAIMS = []

def claim(name, cond, detail=""):
    CLAIMS.append(dict(name=name, passed=bool(cond), detail=detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

def M_radial(m, kmax=40.0, n=600000):
    """Independent radial quadrature of M(m) = (1/2pi^2) int k^2/D dk."""
    k = np.linspace(1e-6, kmax, n)
    D = m + C * (k**2 - Q0**2)**2
    return float(np.trapezoid(k**2 / D, k) / (2.0 * np.pi**2))

def J_of_t(t, r_diag, nk=900, nmu=540, kmax_fac=8.0):
    k = np.linspace(1e-6, kmax_fac * Q0, nk)
    mu = np.linspace(-1.0, 1.0, nmu)
    Kg, MUg = np.meshgrid(k, mu, indexing="ij")
    Dk = r_diag + C * (Kg**2 - Q0**2)**2
    kp2 = Kg**2 + t**2 + 2.0 * Kg * t * MUg
    Dkp = r_diag + C * (kp2 - Q0**2)**2
    inner = np.trapezoid(Kg**2 / (Dk * Dkp), mu, axis=1)
    return float(np.trapezoid(inner, k) / (4.0 * np.pi**2) * 2.0)

def u_eff(M):
    return U + 10.0 * V * M

print("SC-SCOPE / M-ENDPOINT: direct dressing-variance evaluation")
rR = m424.gap_solve(MU2, 0, 0, 0.0)
M_R = m424.M_fast(rR)
lam = 3.0 * U + 30.0 * V * M_R
print(f"    anchor: r_R={rR:.6f}, M_R={M_R:.6f}, lam'={lam:.4f}")

# (1) endpoint dressed masses r_hat(I) and the M-ENDPOINT constants
r_hat = {I: rR + 2.0 * lam * I for I in (1e-3, 2e-3)}
claim("rhat_endpoint_2e-3", abs(r_hat[2e-3] - 0.33675) < 5e-4,
      f"(r_hat(2e-3) = r_R + 2 lam' I = {r_hat[2e-3]:.5f} vs registered 0.33675)")
claim("rhat_1e-3", abs(r_hat[1e-3] - 0.3206) < 5e-4,
      f"(r_hat(1e-3) = {r_hat[1e-3]:.5f} vs registered 0.3206)")

M_end = {}
for I in (1e-3, 2e-3):
    Mf = m424.M_fast(r_hat[I]); Mq = M_radial(r_hat[I])
    M_end[I] = Mf
    claim(f"M_ENDPOINT_quadratures_agree_I={I:g}", abs(Mf - Mq) < 1.5e-2 * abs(Mf),
          f"(M({r_hat[I]:.5f}): M_fast={Mf:.6f} vs radial={Mq:.6f}, "
          f"agree to {abs(Mf-Mq)/Mf*100:.2f}% -- M-ENDPOINT resolved by direct quadrature)")
# M-ENDPOINT (the named missing constant): M(0.33675)
M_ENDPOINT = M_end[2e-3]
claim("M_ENDPOINT_below_M_R", M_ENDPOINT < M_R,
      f"(M-ENDPOINT = M(0.33675) = {M_ENDPOINT:.6f} < M_R = {M_R:.6f}: dressing at higher "
      "mass lowers the variance, as convexity/monotonicity require)")
# convex/secant bracket sanity: M_ENDPOINT in (linear-J0/2 estimate, M_R)
lin_est = M_R - 0.5 * 0.290 * (r_hat[2e-3] - rR)   # corrected slope -J(0)/2
claim("M_ENDPOINT_in_corrected_bracket", lin_est - 1e-3 <= M_ENDPOINT <= M_R,
      f"(M-ENDPOINT {M_ENDPOINT:.5f} in corrected bracket [{lin_est:.5f}, {M_R:.5f}]; "
      "the old [0.1001,0.1094] bracket used the factor-2 slope)")

# (2) single J0 at the anchor dressing (matches certified U4/U7 tables)
J0 = J_of_t(1e-9, rR + 2.0 * lam * 4e-4)
claim("J0_value", abs(J0 - 0.290) < 0.01, f"(J(0) at anchor dressing = {J0:.4f} vs certified 0.290)")

# (3) sunset-axis ratios: frozen-coupling (U4, M=M_R) vs dressed (M=M-ENDPOINT)
def composed(I):
    return MARGIN * (1.0 - 1.0 / RHO[I])
def sunset_bound(I, M):
    return 0.5 * u_eff(M)**2 * (2.0 * I) * 6.0 * J0 * M

print("    sunset-axis ratios (composed margin / sunset bound):")
results = {}
for I in (1e-3, 2e-3):
    b_frozen = sunset_bound(I, M_R)
    b_dressed = sunset_bound(I, M_end[I])
    r_frozen = composed(I) / b_frozen
    r_dressed = composed(I) / b_dressed
    results[I] = dict(I=I, r_hat=r_hat[I], M_endpoint=M_end[I],
                      u_eff_dressed=u_eff(M_end[I]), composed=composed(I),
                      ratio_frozen_U4=r_frozen, ratio_dressed=r_dressed)
    print(f"      I={I:.0e}: frozen(U4,M_R) x{r_frozen:.3f}  ->  dressed(M-ENDPOINT) x{r_dressed:.3f}")

# (4) the resolution: frozen endpoint reproduces U4 x0.97 (marginal), dressed > 1
claim("frozen_U4_endpoint_reproduced", abs(results[2e-3]["ratio_frozen_U4"] - 0.97) <= 0.08 * 0.97,
      f"(frozen-coupling endpoint = x{results[2e-3]['ratio_frozen_U4']:.3f} reproduces U4 x0.97: "
      "the over-conservative bound that froze u_eff at M_R)")
claim("dressed_endpoint_positive", results[2e-3]["ratio_dressed"] > 1.0,
      f"(dressed endpoint = x{results[2e-3]['ratio_dressed']:.3f} > 1: with the directly-evaluated "
      "M-ENDPOINT the sunset-axis endpoint is POSITIVE -- the U4 marginal failure was a "
      "frozen-coupling artefact, not a real third-cumulant obstruction)")
claim("dressed_endpoint_matches_triage_est", abs(results[2e-3]["ratio_dressed"] - 1.13) <= 0.10,
      f"(dressed endpoint x{results[2e-3]['ratio_dressed']:.3f} ~ triage estimate x1.13; "
      "supersedes the invalidated x1.34 linear estimate)")
claim("I1e-3_dressed_comfortable", results[1e-3]["ratio_dressed"] > 2.5,
      f"(I=1e-3 dressed ratio x{results[1e-3]['ratio_dressed']:.2f} > 2.5: comfortable)")

# (5) honest scope: this resolves the SUNSET axis only; SC-SCOPE needs the other inputs
print("    SCOPE: M-ENDPOINT resolved + sunset axis POSITIVE; SC-SCOPE still OPEN on")
print("           GHAT4-PERTRANSFER (quartic-difference) and R-U6-1 (tadpole alignment).")

ok = all(c["passed"] for c in CLAIMS)
out = REPO / "claims" / "B5-BEYOND-LAYER-BOUND" / "runs" / "260607-scscope-mendpoint"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="scscope_mendpoint_eval.py", version=__version__,
    constants=dict(mu2=MU2, rR=rR, M_R=M_R, lam=lam, J0=J0,
                   M_ENDPOINT=M_ENDPOINT, rhat_2e3=r_hat[2e-3], rhat_1e3=r_hat[1e-3]),
    results={f"{I:g}": results[I] for I in results},
    scope="sunset axis resolved; SC-SCOPE OPEN on GHAT4-PERTRANSFER + R-U6-1",
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
