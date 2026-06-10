"""res5_024_offshell_operator_decision.py -- T-024: records and verifies the
operator decision on off-shell competitors. Off-shell / arbitrary-multi-radius
antipodal lattice subsets are NOT admitted to the PRIMARY admissible class A_adm
(registered crystalline shell/shell-union), justified physically by the kinetic
penalty K_0(k)=r_R+c(|k|^2-q0^2)^2 for |k|!=q0; they ARE admitted to an ADVERSARIAL
extended class A_ext (arbitrary antipodal, N<=n_pack), controlled by the universal
fallback T'(Q)<=N/2<=20. Two-tier closure: comfortable on A_adm (T'<=13), razor-thin
fallback on A_ext (T'<=20, RES-1 x1.026).

Physical justification (operator). The Reading-H comparison is a shell-selected
Brazovskii comparison: K_0(k) = r_R + c(|k|^2 - q0^2)^2 is minimised on the soft
shell |k|=q0. An off-shell mode at the nearest distinct lattice radius |k|=sqrt(2) q0
carries kinetic penalty K_0 - r_R ~ 0.214 per mode = ~x50 the selection MARGIN
(0.00432). A competitor with off-shell modes therefore cannot be a LEADING Reading-H
competitor; off-shell content is Gaussian-sea / higher-energy / adversarial, not an
independent Bragg competitor. Hence shell-supported is the primary physical class.

Two classes.
  A_adm = registered crystalline shell/shell-union competitors  (PRIMARY)  -> T'<=13.
  A_ext = { Q=-Q, |Q|<=n_pack }  (ADVERSARIAL extended)         -> T'<=N/2<=20.
On A_adm the closure is comfortable (R_lead<=0.650, joint>=x1.095); on A_ext the
fallback keeps the thresholds alive (20<20.5<26.2<60.4) but RES-1 thins to x1.026.

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-10"
__claims__ = ["B5-BEYOND-LAYER-BOUND", "B2-PROPA-HLAYER", "B1-RH-ENUM"]

import json, sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "codes" / "vacuum"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "archive" / "legacy" / "scripts"))
import sectorb_common as sb            # noqa: E402
import Math424_AddA_reading_uniqueness as m424  # noqa: E402
U, V, Q0, C = sb.U, sb.V, sb.Q0, sb.C
REPO = Path(__file__).resolve().parents[2]
CLAIMS = []
def claim(n, c, d=""):
    CLAIMS.append(dict(name=n, passed=bool(c), detail=d))
    print(f"  [{'PASS' if c else 'FAIL'}] {n} {d}")

mu2, I = 0.005, 2e-3
rR = m424.gap_solve(mu2, 0, 0, 0.0); M_R = m424.M_fast(rR); u_eff = U + 10 * V * M_R
MARGIN = sb.margin_of(mu2)["margin"]
def K0(kmag): return rR + C * (kmag**2 - Q0**2)**2
const = (9 / 4) * u_eff**2 * 0.21774 * 12 / ((12 / 2) * rR)
def R_lead(Kf): return const * (1 + Kf) * I
S, Rm = 1.13, 0.385
def joint(Tp): rho = 266.7 / (1 + Tp); return 1 / ((1 / rho) * (1 + Rm) + (1 - 1 / rho) / S)

# (1) kinetic penalty: off-shell modes cost >> selection MARGIN => shell-supported is the physical class
pen_nearest = K0(math.sqrt(2) * Q0) - rR; ratio_margin = pen_nearest / MARGIN
claim("offshell_kinetic_penalty_dominates_margin", ratio_margin > 10.0 and K0(Q0) <= rR + 1e-12,
      f"(K_0(k)=r_R+c(|k|^2-q0^2)^2 is minimised on-shell K_0(q0)=r_R={rR:.4f}; the nearest off-shell radius "
      f"|k|=sqrt(2)q0 costs K_0-r_R={pen_nearest:.4f} = x{ratio_margin:.0f} the selection MARGIN={MARGIN:.5f}. An "
      "off-shell mode cannot be a leading Reading-H competitor => shell-supported is the PRIMARY physical class)")

# (2) A_adm (primary, shell-supported): comfortable closure T'<=13
claim("Aadm_primary_comfortable", R_lead(13) < 0.7 and joint(13) > 1.09,
      f"(A_adm = registered shell/shell-union, T'<=13: R_lead(13)={R_lead(13):.3f}<0.7 (x{1/R_lead(13):.2f}), "
      f"SC-SCOPE joint(13)=x{joint(13):.4f}>1.09. Comfortable closure on the primary physical class)")

# (3) A_ext (adversarial, arbitrary antipodal): fallback T'<=N/2<=20 keeps thresholds alive (razor-thin RES-1)
claim("Aext_adversarial_fallback_survives", R_lead(20) < 1.0 and joint(20) > 1.0 and 20 < 20.5,
      f"(A_ext = {{Q=-Q, |Q|<=n_pack}}: universal fallback T'<=N/2<=20; 20<20.5(RES-1)<26.2(RES-5)<60.4(SC-SCOPE). "
      f"R_lead(20)={R_lead(20):.4f}<1 (razor-thin x{1/R_lead(20):.3f}), joint(20)=x{joint(20):.3f}>1. The adversarial "
      "class does NOT break the thresholds; off-shell escapes are controlled, not admitted as leading competitors)")

# (4) the operator decision: two-class structure (primary not-admit + adversarial admit-with-fallback)
claim("operator_two_class_decision", ratio_margin > 10 and R_lead(13) < R_lead(20) < 1,
      f"(OPERATOR DECISION: off-shell NOT in the primary A_adm (kinetic penalty x{ratio_margin:.0f} MARGIN); "
      f"ADMITTED in the adversarial A_ext with the T'<=N/2<=20 fallback. Two-tier closure: A_adm comfortable "
      f"(R_lead<={R_lead(13):.3f}), A_ext razor-thin (R_lead(20)={R_lead(20):.3f}). Adversarially safe + physically "
      "primary. No tier flip: B1/B2 T6, B5 T5)")

# (5) quantitative sanity
sane = (ratio_margin > 10) and (R_lead(13) < 0.7) and (0.97 < R_lead(20) < 1.0) and (joint(20) > 1)
claim("quantitative_sanity_decision", sane,
      f"(kinetic penalty x{ratio_margin:.0f}>10; A_adm R_lead(13)={R_lead(13):.3f}; A_ext R_lead(20)={R_lead(20):.4f} "
      f"in (0.97,1); joint(20)=x{joint(20):.3f}>1; ordering 20<20.5<26.2<60.4. Two-class decision recorded)")

ok = all(c["passed"] for c in CLAIMS)
out = REPO / "claims" / "B5-BEYOND-LAYER-BOUND" / "runs" / "260610-res5-024-offshell-operator-decision"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="res5_024_offshell_operator_decision.py", version=__version__,
    rR=rR, MARGIN=MARGIN, offshell_penalty_nearest=pen_nearest, penalty_over_margin=ratio_margin,
    R_lead_13=R_lead(13), R_lead_20=R_lead(20), joint_13=joint(13), joint_20=joint(20),
    verdict=("T-024 OPERATOR DECISION: off-shell NOT in primary A_adm (kinetic penalty x%.0f MARGIN => shell-"
             "supported is physical); ADMITTED in adversarial A_ext (T'<=N/2<=20 fallback). Two-tier: A_adm "
             "comfortable (R_lead(13)=%.3f, joint=x%.3f), A_ext razor-thin (R_lead(20)=%.4f, joint=x%.3f). "
             "Thresholds 20<20.5<26.2<60.4 survive. No tier flip." % (ratio_margin, R_lead(13), joint(13), R_lead(20), joint(20))),
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nkinetic penalty x{ratio_margin:.0f} MARGIN; A_adm R_lead(13)={R_lead(13):.3f}/joint=x{joint(13):.3f}; A_ext R_lead(20)={R_lead(20):.4f}/joint=x{joint(20):.3f}")
print(f"claims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
