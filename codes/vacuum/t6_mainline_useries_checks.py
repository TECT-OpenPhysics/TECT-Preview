"""Consolidated machine checks for the Reading-H T6 mainline U-series notes.

DRAFT STATUS — NOT YET EXECUTED. This script was authored in an agent
session without shell access (2026-06-06); every assert below encodes the
closed-form/estimate arithmetic of the U-series notes and MUST be executed
and reviewed before any of those numbers are cited as machine-verified.
First successful run: record the JSON artefact under
claims/B1-RH-ENUM/runs/<date>-useries-checks/ and flip __status__.

Covers (one section per registered check):
  S1  G-A0-VER        (U2: ha0-removal-pathway)        m_w, m* identities, x7.8 window
  S2  M-ENDPOINT      (U7: sunset-endpoint-refinement) M(r_hat(I)) values + bracket
  S3  U4/U7 tables    (third-cumulant sunset/tadpole bounds, dressed couplings, ratios)
  S4  R-U6-2          (U6: tadpole-reabsorption)       3 u_eff M coefficient identity
  S5  R-U10-3         (U10/U11: near-gap protection)   first-order trace coefficient +
                                                       convention remainder scaling
  S6  U8 angle table  (enumeration-amended-class-recheck) exact geometry + theta_min(I)
  S7  U12 ceiling     (dyadic-lift-log-sharpening)     log^{3/2} vs log^2 comparison

Exit code 0 iff all claims pass. Runtime target: < 20 s (M_fast/J calls only;
no sweeps).
"""

__version__ = "0.1.0"
__first_issued__ = "2026-06-06"
__version_issued__ = "2026-06-06"
__status__ = "DRAFT - NOT YET EXECUTED (authored without shell access; run + review required)"
__claims__ = [
    "B1-RH-ENUM (U2 G-A0-VER, U8 angle table, U10/U11 R-U10-3)",
    "B2-PROPA-HLAYER (U2 ha0-removal-pathway arithmetic)",
    "B5-BEYOND-LAYER-BOUND (U4/U6/U7 third-cumulant, U12 sharpened ceiling)",
]

import json
import math
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "archive" / "legacy" / "scripts"))
import Math424_AddA_reading_uniqueness as m424  # noqa: E402

CLAIMS = []


def claim(name, expected, actual, tol):
    ok = abs(actual - expected) <= tol
    CLAIMS.append(dict(name=name, expected=float(expected), actual=float(actual),
                       tol=float(tol), passed=bool(ok)))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {actual:.6g} (exp {expected:.6g} +/- {tol:.1g})")


def claim_true(name, cond, detail=""):
    CLAIMS.append(dict(name=name, expected=True, actual=bool(cond), passed=bool(cond),
                       detail=detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")


U, V, Q0, C = m424.U, m424.V, m424.Q0, m424.C
MU2 = 0.005
MARGIN = 0.00432
LAM_ANCHORS = [4e-4, 1e-3, 2e-3]

print("S0 shared anchors")
rR = m424.gap_solve(MU2, 0, 0, 0.0)
claim("rR_anchor", 0.3045257087, rR, 1e-8)
M_R = m424.M_fast(rR)
claim("M_R_anchor", 0.109414, M_R, 5e-5)
lam = 3.0 * U + 30.0 * V * M_R
claim("lambda_prime", 8.0554, lam, 5e-3)

print("S1 G-A0-VER (U2): sign-decomposition window arithmetic")
M_c = -U / (10.0 * V)
claim("M_c_exact", 43.0 / 1620.0, M_c, 1e-12)
m_w = MU2 + 15.0 * V * M_c**2
claim("m_w_window_constant", 0.0392414, m_w, 5e-7)
m_star_from_gap = MU2 + 3.0 * U * M_R + 15.0 * V * M_R**2
claim("m_star_gap_identity_vs_rR", rR, m_star_from_gap, 2e-5)
claim_true("window_margin_x7p7", m_star_from_gap / m_w > 7.0,
           f"(m*/m_w = {m_star_from_gap / m_w:.2f})")
claim_true("anchor_inequality_MR_gt_Mc_x4", M_R / M_c > 4.0,
           f"(M_R/M_c = {M_R / M_c:.2f})")

print("S2 M-ENDPOINT (U7): intensity-dressed M values + a-priori bracket")
J0_anchor = None  # computed in S5 via the derivative identity check
M_endpoint = {}
for I in LAM_ANCHORS:
    r_hat = rR + 2.0 * lam * I
    M_h = m424.M_fast(r_hat)
    M_endpoint[I] = (r_hat, M_h)
    claim_true(f"M_monotone_at_I={I:g}", M_h < M_R, f"(M({r_hat:.5f}) = {M_h:.6f} < {M_R:.6f})")
r_hat_end, M_end = M_endpoint[2e-3]
claim_true("M_ENDPOINT_in_bracket", 0.1001 - 0.0015 <= M_end <= M_R,
           f"(M(0.33675) = {M_end:.6f}; U7 bracket [0.1001, 0.1094] with convexity allowance)")

print("S3 U4/U7 third-cumulant tables (sunset/tadpole, dressed couplings, ratios)")
J0 = None
# J(0) at the anchor dressing (same integral form as the main script)
def J_of_t(t, r_diag, nk=900, nmu=540, kmax_fac=8.0):
    k = np.linspace(1e-6, kmax_fac * Q0, nk)
    mu = np.linspace(-1.0, 1.0, nmu)
    K, MUg = np.meshgrid(k, mu, indexing="ij")
    Dk = r_diag + C * (K**2 - Q0**2)**2
    kp2 = K**2 + t**2 + 2.0 * K * t * MUg
    Dkp = r_diag + C * (kp2 - Q0**2)**2
    integ = K**2 / (Dk * Dkp)
    inner = np.trapezoid(integ, mu, axis=1)
    return float(np.trapezoid(inner, k) / (4.0 * np.pi**2) * 2.0)

r_hat_anchor = rR + 2.0 * lam * 4e-4
J0 = J_of_t(1e-9, r_hat_anchor)
claim("J0_addc_value", 0.290, J0, 0.01)

# U1 composed margins (band floor x hardened/AddD ratios)
rho = {4e-4: 59.4, 1e-3: 8.8, 2e-3: 2.6}
composed = {I: MARGIN * (1.0 - 1.0 / rho[I]) for I in LAM_ANCHORS}
claim("composed_margin_anchor", 4.247e-3, composed[4e-4], 5e-6)
claim("composed_margin_endpoint", 2.658e-3, composed[2e-3], 5e-6)

# U4 frozen-coupling table (u_eff at M_R) and U7 intensity-dressed table
u_eff_R = U + 10.0 * V * M_R
claim("u_eff_at_MR", 2.685, u_eff_R, 5e-3)
sunset_kernel = 6.0 * J0 * M_R
for I in LAM_ANCHORS:
    b_u4 = 0.5 * u_eff_R**2 * 2.0 * I * sunset_kernel
    ratio_u4 = composed[I] / b_u4
    # U4 quoted ratios: 7.7 / 2.8 / 0.97 (tolerate 8% for J0/M rounding)
    quoted = {4e-4: 7.7, 1e-3: 2.8, 2e-3: 0.97}[I]
    claim_true(f"U4_sunset_ratio_I={I:g}", abs(ratio_u4 - quoted) <= 0.08 * quoted,
               f"(ratio = {ratio_u4:.2f}, quoted {quoted})")
for I in LAM_ANCHORS[1:]:
    r_hat_I, M_I = M_endpoint[I]
    u_eff_I = U + 10.0 * V * M_I
    b_u7 = 0.5 * u_eff_I**2 * 2.0 * I * 6.0 * J0 * M_I
    ratio_u7 = composed[I] / b_u7
    quoted = {1e-3: 3.2, 2e-3: 1.34}[I]
    claim_true(f"U7_dressed_ratio_I={I:g}", abs(ratio_u7 - quoted) <= 0.15 * quoted,
               f"(ratio = {ratio_u7:.2f}, quoted ~{quoted} est)")
claim_true("U7_endpoint_positive", composed[2e-3] >
           0.5 * (U + 10.0 * V * M_endpoint[2e-3][1])**2 * 2.0 * 2e-3 * 6.0 * J0 * M_endpoint[2e-3][1],
           "(the intensity-dressed endpoint sunset bound sits below the composed margin)")

print("S4 R-U6-2 (U6): stationarity-source coefficient identity")
# The tadpole linear-source coefficient must equal the Hartree quartic line 3 u_eff M.
coeff_lemma = 3.0 * (U + 10.0 * V * M_R) * M_R
coeff_engine = 3.0 * U * M_R + 30.0 * V * M_R**2
claim("tadpole_source_eq_stationarity_line", coeff_engine, coeff_lemma, 1e-12)

print("S5 R-U10-3 (U10/U11): near-gap protection first order + convention remainder")
# Exact identity M'(r_hat) = -J(0): finite-difference check.
h = 1e-5
Mp_fd = (m424.M_fast(r_hat_anchor + h) - m424.M_fast(r_hat_anchor - h)) / (2.0 * h)
claim_true("Mprime_equals_minus_J0", abs(-Mp_fd - J0) <= 0.02 * J0,
           f"(-M' = {-Mp_fd:.4f} vs J0 = {J0:.4f})")
# First-order trace gain coefficient ~ 2 lam M_R per unit I (U10 sanity figure 1.76).
gain_lin = 2.0 * lam * M_R
claim("neargap_linear_gain_coeff", 1.763, gain_lin, 0.02)
claim_true("linear_gain_dominates_envelope_at_endpoint",
           gain_lin * 2e-3 > MARGIN / 2.6,
           f"(gain {gain_lin * 2e-3:.4e} vs envelope {MARGIN / 2.6:.4e})")
# Convention remainder: solve the LAM-style self-consistency at the endpoint
# and compare with the linear convention (U11 expectation ~2.7e-5 +/- cubic 10%).
I_end = 2e-3
rp = rR
for _ in range(80):
    Mh = m424.M_fast(rp)
    rp_new = rR + 2.0 * (3.0 * U + 30.0 * V * Mh) * I_end
    if abs(rp_new - rp) < 1e-14:
        break
    rp = rp_new
remainder_end = abs(rp - (rR + 2.0 * lam * I_end))
claim_true("convention_remainder_endpoint", remainder_end <= 3.3e-5,
           f"(remainder = {remainder_end:.2e}; U11 scaled expectation 2.7e-5 + 10% cubic + tol)")
claim_true("remainder_x100_below_protection", gain_lin * I_end / max(remainder_end, 1e-12) > 100.0,
           f"(protection/remainder = {gain_lin * I_end / max(remainder_end, 1e-12):.0f})")

print("S6 U8 angle table (exact geometry + theta_min(I))")
angles = {
    "square": math.pi / 2,
    "SC100": math.pi / 2,
    "HEX": math.pi / 3,
    "FCC": math.acos(1.0 / 3.0),
    "BCC": math.pi / 3,
    "icosahedral": math.atan(2.0),
    "decagonal": math.pi / 5,
}
claim("FCC_min_angle_deg", 70.5288, math.degrees(angles["FCC"]), 1e-3)
claim("icosa_min_angle_deg", 63.4349, math.degrees(angles["icosahedral"]), 1e-3)
for I in LAM_ANCHORS:
    r_hat_I = rR + 2.0 * lam * I
    theta_min = math.sqrt(r_hat_I) / (2.0 * Q0**2 * math.sqrt(C))
    if I == 4e-4:
        claim("theta_min_anchor", 0.6027, theta_min, 2e-3)
    if I == 2e-3:
        claim("theta_min_endpoint", 0.62716, theta_min, 2e-3)
    for name, ang in angles.items():
        claim_true(f"inclass_{name}_I={I:g}", ang >= theta_min,
                   f"({math.degrees(ang):.2f} deg vs theta_min {math.degrees(theta_min):.2f} deg)")
theta_end = math.sqrt(rR + 2.0 * lam * 2e-3) / (2.0 * Q0**2)
claim_true("decagonal_extremal_margin_lt_1pc", angles["decagonal"] / theta_end - 1.0 < 0.01,
           f"(margin = {(angles['decagonal'] / theta_end - 1.0) * 100:.2f}%)")

print("S7 U12 sharpened ceiling comparison")
n_pack = 44
Jlog = math.log2(2 * n_pack)
claim("log2_88", 6.4594, Jlog, 1e-3)
improve = Jlog**2 / Jlog**1.5
claim("log_sharpening_factor_at_44", 2.54, improve, 0.02)
claim_true("sharpened_below_original", Jlog**1.5 < Jlog**2, "(log^{3/2} < log^2 for J > 1)")

n_pass = sum(1 for c in CLAIMS if c["passed"])
print(f"\nclaims {n_pass}/{len(CLAIMS)} {'PASS' if n_pass == len(CLAIMS) else 'FAIL'}")
out_dir = REPO / "claims" / "B1-RH-ENUM" / "runs" / "260606-useries-checks"
out_dir.mkdir(parents=True, exist_ok=True)
artefact = dict(script="t6_mainline_useries_checks.py", version=__version__,
                status=__status__, date="2026-06-06", claims=CLAIMS)
(out_dir / "result.json").write_text(json.dumps(artefact, indent=2))
print(f"artefact: {out_dir / 'result.json'}")
sys.exit(0 if n_pass == len(CLAIMS) else 1)
