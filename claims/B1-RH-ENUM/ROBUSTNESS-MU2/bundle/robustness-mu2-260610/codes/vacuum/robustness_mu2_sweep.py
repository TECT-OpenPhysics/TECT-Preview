"""robustness_mu2_sweep.py — ROBUSTNESS-MU2: off-anchor (mu^2-neighbourhood)
robustness of the A=0 uniqueness inequalities and the Sector-B constants.

The sign-decomposition lemmas L1/L2/L3 are mu^2-INDEPENDENT in structure
(M_c = -u/(10v) has no mu^2; the lemmas use only u<0, v>0, M'<0, and
u_eff(M_c)=0). Only the two anchor inequalities m* > m_w and M_R > M_c carry
mu^2, and only through M_R(mu^2). Moreover m* - m_w = 3u M_R + 15v(M_R^2 - M_c^2)
(mu^2 cancels in the difference). This script sweeps mu^2 over a wide
neighbourhood, verifies both inequalities hold with margin, finds the
robustness radius, and records the smooth mu^2-variation of the load-bearing
constants (lambda', M_R) that the STEP-5B / layer margins depend on.

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-06"
__version_issued__ = "2026-06-06"
__claims__ = ["B1-RH-ENUM", "B2-PROPA-HLAYER"]

import json, sys
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "archive" / "legacy" / "scripts"))
import Math424_AddA_reading_uniqueness as m424  # noqa: E402

U, V, Q0, C = m424.U, m424.V, m424.Q0, m424.C
M_c = -U / (10.0 * V)
CLAIMS = []
def claim(name, cond, detail=""):
    CLAIMS.append(dict(name=name, passed=bool(cond), detail=detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

def at(mu2):
    rR = m424.gap_solve(mu2, 0, 0, 0.0)
    M_R = m424.M_fast(rR)
    m_w = mu2 + 15.0 * V * M_c**2
    lam = 3.0 * U + 30.0 * V * M_R
    return dict(mu2=mu2, m_star=rR, M_R=M_R, m_w=m_w, lam=lam,
                ratio_mw=rR / m_w, ratio_Mc=M_R / M_c)

ANCHOR = 0.005
print("ROBUSTNESS-MU2: off-anchor sweep of the A=0 uniqueness inequalities")
# wide neighbourhood: x4 each way around the anchor
mu2_grid = np.geomspace(ANCHOR / 4.0, ANCHOR * 4.0, 25)
rows = [at(m) for m in mu2_grid]
print("    mu^2       m*        M_R       m_w       m*/m_w   M_R/M_c   lambda'")
for r in rows:
    print(f"    {r['mu2']:.5f}  {r['m_star']:.5f}  {r['M_R']:.5f}  {r['m_w']:.5f}  "
          f"{r['ratio_mw']:6.2f}   {r['ratio_Mc']:5.2f}    {r['lam']:.4f}")

# (1) both inequalities hold across the whole x4 neighbourhood
claim("MR_gt_Mc_all", all(r["M_R"] > M_c for r in rows),
      f"(M_R > M_c on [{mu2_grid[0]:.4f}, {mu2_grid[-1]:.4f}]: min ratio {min(r['ratio_Mc'] for r in rows):.2f})")
claim("mstar_gt_mw_all", all(r["m_star"] > r["m_w"] for r in rows),
      f"(m* > m_w on the whole x4 neighbourhood: min ratio {min(r['ratio_mw'] for r in rows):.2f})")

# (2) m* - m_w = 3u M_R + 15v(M_R^2 - M_c^2): the mu^2-cancellation identity
for r in [rows[0], rows[12], rows[-1]]:
    diff_direct = r["m_star"] - r["m_w"]
    diff_formula = 3.0 * U * r["M_R"] + 15.0 * V * (r["M_R"]**2 - M_c**2)
    claim(f"mu2_cancellation_identity [mu2={r['mu2']:.4f}]", abs(diff_direct - diff_formula) < 1e-6,
          f"(m*-m_w = {diff_direct:.5f} = 3uM_R+15v(M_R^2-M_c^2) = {diff_formula:.5f}: mu^2 cancels)")

# (3) robustness radius: find where m*/m_w first drops below a safety factor (say 2x)
mu2_fine = np.geomspace(0.001, 0.05, 200)
ratios = np.array([at(m)["ratio_mw"] for m in mu2_fine])
mc_ratios = np.array([at(m)["ratio_Mc"] for m in mu2_fine])
# m*/m_w is large at small mu2, decreases as mu2 grows
safe = mu2_fine[(ratios > 2.0) & (mc_ratios > 1.5)]
claim("robustness_radius_generous", safe[0] < ANCHOR * 0.5 and safe[-1] > ANCHOR * 2.0,
      f"(m*/m_w > 2 AND M_R/M_c > 1.5 holds on mu^2 in [{safe[0]:.4f}, {safe[-1]:.4f}] "
      f"= [{safe[0]/ANCHOR:.2f}x, {safe[-1]/ANCHOR:.2f}x] of the anchor)")

# (4) load-bearing constants vary smoothly (C^1) across the neighbourhood:
# lambda'(mu^2) and M_R(mu^2) monotone + bounded variation (no pathology that
# could break the STEP-5B / layer margins, which depend on these)
lams = np.array([r["lam"] for r in rows]); MRs = np.array([r["M_R"] for r in rows])
claim("lambda_smooth_monotone", np.all(np.diff(lams) < 0) and lams.min() > 0,
      f"(lambda' decreases smoothly {lams[0]:.3f} -> {lams[-1]:.3f} > 0 across x4: no sign change)")
claim("MR_smooth_monotone", np.all(np.diff(MRs) < 0),
      f"(M_R decreases monotonically {MRs[0]:.4f} -> {MRs[-1]:.4f}: smooth)")
# at the anchor the constants reproduce the certified values
a = at(ANCHOR)
claim("anchor_reproduces_certified", abs(a["M_R"] - 0.109414) < 5e-5 and abs(a["m_star"] - 0.3045257) < 1e-5,
      f"(at mu^2=0.005: M_R={a['M_R']:.6f}, m*={a['m_star']:.6f} match certified)")

ok = all(c["passed"] for c in CLAIMS)
out = REPO / "claims" / "B1-RH-ENUM" / "runs" / "260606-robustness-mu2"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="robustness_mu2_sweep.py", version=__version__, anchor=ANCHOR, M_c=M_c,
    neighbourhood=[float(mu2_grid[0]), float(mu2_grid[-1])],
    sweep=[{k: float(v) for k, v in r.items()} for r in rows],
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
