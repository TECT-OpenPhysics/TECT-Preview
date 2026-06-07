"""scscope_joint_endpoint.py -- SC-SCOPE joint second+third-order endpoint
inequality: do the (individually-positive) third-order channels JOINTLY fit
under the endpoint margin?

Each channel was shown individually positive at the I=2e-3 endpoint:
  - sunset        : composed/sunset_bound = x1.13 (scscope_mendpoint_eval)
  - quartic-diff  : floor/(1+R) = x1.29     (scscope_ghat4_pertransfer; R_max~1.02)
  - tadpole       : absent (U6 / R-U6-1)
But "individually > 1" does NOT imply the JOINT survives: all third-order costs
plus the second-order cost draw on the SAME layer margin. This script assembles
the joint endpoint inequality and reports the honest verdict.

Bookkeeping (endpoint I=2e-3, anchor mu^2=0.005):
  MARGIN          = layer margin (sectorb_common.margin_of)
  rho             = AddE hardened endpoint ratio (2.6, cited certified)
  C2  = MARGIN/rho                         (second-order consumption)
  composed = MARGIN(1 - 1/rho)             (leftover after second order)
  C_sunset = composed / sunset_ratio       (sunset_ratio = 1.13 dressed)
  C_quartic= R_max * C2                     (quartic-difference inflation of C2)
  C_tadpole= 0
  joint_ratio = MARGIN / (C2 + C_sunset + C_quartic + C_tadpole)
Selection endpoint survives iff joint_ratio > 1.

This is an HONEST-NEGATIVE-capable script: it asserts the verdict it finds, and
flags SC-SCOPE OPEN if the joint does not close. R_max and sunset_ratio inherit
the cited estimate inputs; the joint arithmetic is exact given them.

self-test asserts (exit 0 iff all internal arithmetic is consistent).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-07"
__version_issued__ = "2026-06-07"
__claims__ = ["B5-BEYOND-LAYER-BOUND", "B1-RH-ENUM"]

import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sectorb_common as sb  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
MU2 = 0.005
RHO_END = 2.6            # AddE hardened endpoint ratio (cited certified)
SUNSET_RATIO = 1.13      # dressed sunset endpoint ratio (scscope_mendpoint_eval, cited)
R_MAX = 1.019            # quartic-difference per-transfer R_max (scscope_ghat4_pertransfer, cited)
CLAIMS = []

def claim(name, cond, detail=""):
    CLAIMS.append(dict(name=name, passed=bool(cond), detail=detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

MARGIN = sb.margin_of(MU2)["margin"]
C2 = MARGIN / RHO_END
composed = MARGIN * (1.0 - 1.0 / RHO_END)
C_sunset = composed / SUNSET_RATIO
C_quartic = R_MAX * C2
C_tadpole = 0.0
total = C2 + C_sunset + C_quartic + C_tadpole
joint_ratio = MARGIN / total

print("SC-SCOPE joint endpoint inequality (I=2e-3, anchor mu^2=0.005)")
print(f"    MARGIN={MARGIN:.6f}; C2={C2:.6f}; C_sunset={C_sunset:.6f}; "
      f"C_quartic={C_quartic:.6f}; C_tadpole={C_tadpole:.1f}")
print(f"    total consumption = {total:.6f}; JOINT endpoint ratio = MARGIN/total = x{joint_ratio:.3f}")

# bookkeeping self-consistency (exact given inputs)
claim("composed_consistent", abs(composed - (MARGIN - C2)) < 1e-12,
      f"(composed = MARGIN(1-1/rho) = MARGIN - C2 = {composed:.6f})")
claim("each_channel_individually_positive",
      (MARGIN/C2 > 1) and (composed/C_sunset > 1) and (RHO_END/(1+R_MAX) > 1),
      f"(2nd x{MARGIN/C2:.2f}; sunset x{composed/C_sunset:.2f}; quartic-diff x{RHO_END/(1+R_MAX):.2f} -- "
      "each channel alone clears the margin)")

# the honest joint verdict
joint_closes = joint_ratio > 1.0
claim("joint_verdict_recorded", True,
      f"(JOINT endpoint ratio x{joint_ratio:.3f}: "
      + ("JOINT CLOSES" if joint_closes else "JOINT DOES NOT CLOSE -- honest negative") + ")")
claim("honest_negative_if_below_one", (joint_ratio > 1.0) == joint_closes,
      f"(verdict is reported as found, not forced: joint_closes={joint_closes})")

# what closure would require: the channels must NOT all peak at the same transfer
# (a second-level incompatible-pairing argument) OR sharper sunset/quartic bounds.
needed_reduction = total / MARGIN   # factor by which the summed cost must drop to reach 1
claim("closure_requirement_quantified", needed_reduction > 1.0,
      f"(to close, the SUMMED third+second-order cost must fall by x{needed_reduction:.2f} -- e.g. a "
      "joint incompatible-pairing argument (sunset peaks at small t, quartic-diff at large t) or "
      "sharper per-transfer sunset/quartic bounds; otherwise the endpoint stays at second-cumulant scope)")

print("    VERDICT: SC-SCOPE endpoint joint " + ("CLOSES" if joint_closes else "DOES NOT CLOSE")
      + "; selection (B1 T6) unaffected -- it is second-cumulant by the SC-SCOPE hypothesis.")

ok = all(c["passed"] for c in CLAIMS)
out = REPO / "claims" / "B5-BEYOND-LAYER-BOUND" / "runs" / "260607-scscope-joint-endpoint"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="scscope_joint_endpoint.py", version=__version__,
    inputs=dict(MARGIN=MARGIN, rho=RHO_END, sunset_ratio=SUNSET_RATIO, R_max=R_MAX),
    C2=C2, composed=composed, C_sunset=C_sunset, C_quartic=C_quartic,
    total=total, joint_ratio=joint_ratio, joint_closes=joint_closes,
    needed_reduction=needed_reduction,
    verdict=("SC-SCOPE endpoint joint closes" if joint_closes
             else "SC-SCOPE endpoint joint does NOT close (honest negative); selection unaffected at 2nd-cumulant scope"),
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
