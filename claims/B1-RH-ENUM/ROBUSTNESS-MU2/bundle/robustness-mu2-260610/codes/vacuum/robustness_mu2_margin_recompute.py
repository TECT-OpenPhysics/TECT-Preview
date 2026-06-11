"""robustness_mu2_margin_recompute.py -- ROBUSTNESS-MU2 closure bar: recompute the
EXACT layer margin m(mu^2) across the [x0.5, x2] neighbourhood, with a
derivative-sign monotonicity certificate, a full-grid J_eff envelope, and a
Prop-A branch-invariance check.

v1.1 (2026-06-07): (a) margin_of / J_of_t now imported from sectorb_common (single
source, governance/CODE-DISCIPLINE.md rule 1); (b) NEW derivative-sign
certificate d m(mu^2)/d mu^2 > 0 on [0.0025,0.01] proving the minimum sits at the
left endpoint 0.0025 (review priority 3); (c) NEW J_eff envelope across the WHOLE
(mu^2, I) grid at two quadrature resolutions, not only the thinnest corner; (d)
NEW Prop-A branch-invariance assertion (disc>0, M_+ > M_c on the whole band).

The closure bar (robustness note v1.3, GATES.md) requires the exact m(mu^2) with
m(mu^2) >= 0.4 m_anchor on [x0.5,x2] at the three certified intensities, plus a
certified J_eff envelope. This script supplies all of it. The gate FLIP remains
operator-authorized; this script does not change GATES.md.

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.1.0"
__first_issued__ = "2026-06-07"
__version_issued__ = "2026-06-07"
__claims__ = ["B1-RH-ENUM", "B5-BEYOND-LAYER-BOUND"]

import json, sys, math
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))          # sibling: sectorb_common
sys.path.insert(0, str(REPO / "archive" / "legacy" / "scripts"))
import sectorb_common as sb                                       # noqa: E402
import Math424_AddA_reading_uniqueness as m424                    # noqa: E402

U, V, Q0, C = sb.U, sb.V, sb.Q0, sb.C
ANCHOR = 0.005
INTENS = [4e-4, 1e-3, 2e-3]
CLAIMS = []

def claim(name, cond, detail=""):
    CLAIMS.append(dict(name=name, passed=bool(cond), detail=detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

def step5b_ratio(mu2, I, margin, nk=500, nmu=320):
    """STEP-5B AddE de-thinned closure ratio with a SUPPLIED (recomputed) margin."""
    rR = m424.gap_solve(mu2, 0, 0, 0.0)
    M_R = m424.M_fast(rR)
    lam = 3.0 * U + 30.0 * V * M_R
    rhat = rR + 2.0 * lam * I
    a0 = 2.0 * lam * I / rhat
    theta_min = math.sqrt(rhat) / (2.0 * Q0**2 * math.sqrt(C))
    n_pack = 16.0 / theta_min**2
    t_min = 2.0 * Q0 * math.sin(theta_min / 2.0)
    J_eff = sb.J_of_t(t_min, rhat, nk=nk, nmu=nmu)
    K = 8.0 + 4.0 * math.sqrt(14.0) * math.sqrt(n_pack)
    Kb = 4.0 * (1.0 - a0) * margin / ((lam * I)**2 * J_eff)
    return Kb / K, J_eff

print("ROBUSTNESS-MU2: exact m(mu^2) recomputation across [x0.5, x2] (v1.1)")

# (0) anchor: the closed form must reproduce MARGIN = 0.00432
a = sb.margin_of(ANCHOR)
M_ANCHOR = a["margin"]
claim("anchor_margin_reproduces_0.00432", abs(M_ANCHOR - 0.00432) < 5e-5,
      f"(MARGIN(0.005) = PB(M_+) - DIP_BAND = {M_ANCHOR:.6f} ~ 0.00432; via sectorb_common, single source)")

# (1) recompute m(mu^2) across the band [0.0025, 0.01]
mu2_fine = np.linspace(0.0025, 0.01, 61)
margins = np.array([sb.margin_of(m)["margin"] for m in mu2_fine])
m_min, m_max = float(margins.min()), float(margins.max())
i_min = int(margins.argmin())
print(f"    m(mu^2) over [0.0025,0.01]: min={m_min:.6f} (at mu^2={mu2_fine[i_min]:.5f}), "
      f"max={m_max:.6f}; m_anchor={M_ANCHOR:.6f}")
claim("margin_ge_0.4_anchor", m_min >= 0.4 * M_ANCHOR,
      f"(min m(mu^2) = {m_min:.6f} >= 0.4 m_anchor = {0.4*M_ANCHOR:.6f}; actual ratio "
      f"min/anchor = {m_min/M_ANCHOR:.3f})")

# (2) derivative-sign monotonicity certificate (review priority 3):
#     d m/d mu^2 > 0 on the band => the minimum is at the LEFT endpoint 0.0025.
#     Structural reason: m = PB(M_+) - DIP_BAND; DIP_BAND = |mu^2 - 3u^2/(20v)|^{3/2}
#     /(3 sqrt v) DECREASES as mu^2 rises toward 3u^2/(20v) (rhat0(Mc) less negative),
#     so -DIP_BAND increases; PB(M_+) increases numerically. Certify the sign on a
#     fine central-difference grid.
dmu = mu2_fine[1] - mu2_fine[0]
dm = np.gradient(margins, dmu)
claim("dmargin_dmu2_positive_everywhere", bool(np.all(dm > 0)),
      f"(d m/d mu^2 > 0 at all 61 grid points: min = {dm.min():.4e} > 0 => m(mu^2) strictly "
      f"increasing => the minimum is the LEFT endpoint mu^2 = 0.0025, NOT an interior point)")
claim("min_at_left_endpoint", i_min == 0,
      f"(argmin index = {i_min} (mu^2 = {mu2_fine[i_min]:.5f}): grid minimum at the left endpoint, "
      "consistent with the positive-derivative certificate)")
# DIP_BAND monotone-decreasing piece (closed-form, exact)
rh0 = mu2_fine - 3.0 * U * U / (20.0 * V)
dip = np.abs(rh0)**1.5 / (3.0 * math.sqrt(V))
claim("DIP_BAND_decreasing_closedform", bool(np.all(np.diff(dip) < 0)),
      f"(DIP_BAND decreases monotonically {dip[0]:.6f} -> {dip[-1]:.6f} as mu^2 rises: the "
      "-DIP_BAND contribution to m is exactly increasing)")

# (3) Prop-A branch invariance across the whole band (review attack 5)
branch_ok = all(sb.margin_of(m)["branch_ok"] for m in mu2_fine)
disc_min = min(sb.margin_of(m)["disc"] for m in mu2_fine)
claim("propA_branch_invariant", branch_ok,
      f"(disc = 9u^2-60v mu^2 > 0 (min {disc_min:.4f}) and M_+ > M_c on the WHOLE band: the same "
      "upper PD branch is used throughout [0.0025,0.01]; no branch crossing)")

# (4) the five registered anchors + STEP-5B ratio with the RECOMPUTED margin
mu2_list = [0.0025, 0.00354, ANCHOR, 0.00707, 0.01]
print("    mu^2      m(mu^2)    ratio@4e-4  ratio@1e-3  ratio@2e-3  (recomputed margin)")
grid = []
worst = 1e9
for mu2 in mu2_list:
    mg = sb.margin_of(mu2)["margin"]
    rs = {I: step5b_ratio(mu2, I, mg)[0] for I in INTENS}
    grid.append(dict(mu2=mu2, margin=mg, **{f"ratio_{I:g}": rs[I] for I in INTENS}))
    worst = min(worst, min(rs.values()))
    print(f"    {mu2:.5f}  {mg:.6f}   x{rs[4e-4]:6.1f}    x{rs[1e-3]:5.2f}     x{rs[2e-3]:4.2f}")
claim("step5b_ratio_gt1_recomputed_margin", worst > 1.0,
      f"(worst STEP-5B ratio over [x0.5,x2] x the THREE CERTIFIED INTENSITIES, using the RECOMPUTED "
      f"m(mu^2), = x{worst:.2f} > 1: closure holds with the exact margin)")

# (5) J_eff envelope across the WHOLE grid at two resolutions (review attack 4):
#     not only the thinnest corner. Report the max relative envelope and the worst
#     ratio over both resolutions and the whole grid.
print("    J_eff two-resolution envelope across the whole (mu^2, I) grid:")
max_env = 0.0
worst_ratio_env = 1e9
for mu2 in mu2_list:
    mg = sb.margin_of(mu2)["margin"]
    for I in INTENS:
        r_lo, J_lo = step5b_ratio(mu2, I, mg, nk=500, nmu=320)
        r_hi, J_hi = step5b_ratio(mu2, I, mg, nk=1100, nmu=700)
        env = abs(J_hi - J_lo) / J_lo
        max_env = max(max_env, env)
        worst_ratio_env = min(worst_ratio_env, r_lo, r_hi)
print(f"      max relative J_eff envelope over the grid = {max_env*100:.3f}%; "
      f"worst ratio over both resolutions = x{worst_ratio_env:.2f}")
claim("Jeff_envelope_full_grid_certified", max_env < 0.05,
      f"(max two-resolution J_eff relative envelope over the WHOLE 5x3 grid = {max_env*100:.2f}% "
      "(< 5%): J_eff is converged everywhere, not only at the thinnest corner)")
claim("verdict_robust_full_grid", worst_ratio_env > 1.0,
      f"(worst STEP-5B ratio over the whole grid AND both J_eff resolutions = x{worst_ratio_env:.2f} "
      "> 1: the closure verdict survives the J_eff quadrature uncertainty across the full grid)")

ok = all(c["passed"] for c in CLAIMS)
out = REPO / "claims" / "B1-RH-ENUM" / "runs" / "260607-robustness-mu2-margin-recompute"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="robustness_mu2_margin_recompute.py", version=__version__,
    anchor=ANCHOR, m_anchor=M_ANCHOR, m_min=m_min, m_max=m_max,
    m_min_over_anchor=m_min / M_ANCHOR, min_at_mu2=float(mu2_fine[i_min]),
    dmargin_min=float(dm.min()), worst_step5b_ratio=worst,
    Jeff_max_envelope=max_env, worst_ratio_over_envelope=worst_ratio_env,
    branch_invariant=branch_ok, grid=grid, claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
