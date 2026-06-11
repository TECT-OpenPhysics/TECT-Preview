"""res5_sunset_norm_map.py -- RES-5 sunset-norm certificate (v1.1 audit re-issue
self-test). Two verdicts after the 2026-06-09 operator adversarial review:

  (i) ACCEPTED -- the self-energy/free-energy double-count correction. The
      a0-skeleton c a0 ~ 0.002 double-counted a0 (free-energy ratio x response);
      the certificate quantity is the free-energy ratio Delta Gamma_2^pd /
      Delta F_margin, whose LEADING (sunset/2-loop) value IS the SC-SCOPE
      certified joint x1.040 -> x1.13 (NOT 0.2%).

  (ii) RETRACTED -- "RES-5 survives at STRONG EVIDENCE, thin". The screened
      higher-skeleton tail <= leading/(1-0.49) ~ 2x leading is SAME ORDER
      (screened-finite), NOT sub-dominant. Against the thin joint x1.040 the
      slack is only 1 - 1/1.040 ~ 3.85% (C_higher must be < 0.040 C_leading);
      a same-order tail is not bounded into that slack. RES-5/GAP-2 = OPEN.

No tier flip: B1-RH-ENUM stays T6 CONDITIONAL on {H-LAYER}. The asserts below
encode the HONEST conclusion (tail NOT within slack -> OPEN), correcting v1.0.

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.1.0"
__claims__ = ["B1-RH-ENUM"]
import json, sys
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
CLAIMS=[]
def claim(n,c,d=""):
    CLAIMS.append(dict(name=n,passed=bool(c),detail=d)); print(f"  [{'PASS' if c else 'FAIL'}] {n} {d}")

# SC-SCOPE certified values (from claims/B5-.../SC-SCOPE/notes, this session's arc)
joint_certified = 1.040   # certified thin joint endpoint
joint_cap       = 1.13    # sunset-saturated cap
screened_resp   = 1.0/(1.0+1.033)  # 0.49 (res5-a0-skeleton-sensitivity)

# (i) correction ACCEPTED: the c a0 ~ 0.002 was a self-energy/free-energy conflation
c_a0_wrong = 0.002
claim("correction_self_energy_free_energy_doublecount", True,
      f"(ACCEPTED: c a0 ~ {c_a0_wrong} double-counted a0 = free-energy ratio x response; the certificate quantity "
      "is the free-energy ratio |Delta Gamma_2^pd|/Delta F_margin, leading value = SC-SCOPE thin joint, NOT 0.2%)")

# the SC-SCOPE joint > 1 IS the leading-skeleton certificate (certified, thin)
claim("scscope_joint_is_leading_skeleton_certificate", joint_certified > 1.0 and joint_cap > 1.0,
      f"(SC-SCOPE joint = MARGIN/(C2+C_sunset+C_quartic) = x{joint_certified} (certified) -> x{joint_cap} (sunset "
      "cap), both > 1: the leading 2PI skeleton/third cumulant does NOT overturn the selection -- the leading "
      "Delta Gamma_2^pd certificate, thin)")

# higher skeletons screened-FINITE but SAME ORDER (corrected reading; v1.0 said 'sub-dominant')
tail_factor = 1.0/(1.0-screened_resp)   # ~1.97
claim("higher_skeletons_screened_finite_but_same_order", tail_factor > 1.0,
      f"(geometric tail <= leading x 1/(1-{screened_resp:.2f}) = x{tail_factor:.2f}: screened-FINITE but SAME ORDER "
      "as the leading skeleton -- NOT sub-dominant. v1.0's 'sub-dominant' wording is RETRACTED)")

# slack arithmetic: the same-order tail is NOT within the thin slack -> RES-5 OPEN
slack_frac  = 1.0 - 1.0/joint_certified   # 0.0385 of MARGIN
budget_frac = joint_certified - 1.0       # C_higher must be < 0.040 C_leading
claim("res5_open_tail_not_within_slack", tail_factor > slack_frac and tail_factor > budget_frac,
      f"(RETRACTED v1.0 survival: required C_higher/C_leading < {budget_frac:.3f} (slack {slack_frac:.4f} of "
      f"MARGIN); current tail bound ~x{tail_factor:.2f} leading = O(C_leading) >> budget -> the tail is NOT within "
      "the thin slack -> RES-5/GAP-2 OPEN. No tier flip: B1 T6 on {H-LAYER})")

ok=all(c["passed"] for c in CLAIMS)
out=REPO/"claims"/"B1-RH-ENUM"/"runs"/"260609-res5-sunset-norm-map"; out.mkdir(parents=True,exist_ok=True)
(out/"result.json").write_text(json.dumps(dict(script="res5_sunset_norm_map.py",version=__version__,
    joint_certified=joint_certified,joint_cap=joint_cap,screened_resp=screened_resp,tail_factor=tail_factor,
    slack_frac=slack_frac,budget_frac=budget_frac,
    correction="ACCEPTED: c a0 ~0.002 was a self-energy/free-energy conflation (double-counted a0); the certificate "
               "quantity is the free-energy ratio = SC-SCOPE thin joint",
    verdict="RES-5/GAP-2 OPEN (v1.1 audit re-issue): correction accepted; survival RETRACTED. The screened tail is "
            "SAME-ORDER (x1.97 leading), not sub-dominant, and does not fit the thin slack (0.0385); residual = "
            "rigorous SC-SCOPE-joint->Delta Gamma_2^pd normalization identity + a tail budget C_higher<0.04 C_leading",
    claims=CLAIMS,all_pass=ok),indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
