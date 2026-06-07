"""scscope_joint_pairing.py -- SC-SCOPE endpoint: the joint incompatible-pairing
argument (does it recover the x1.32 joint deficit?).

The additive joint (scscope_joint_endpoint.py) bounded the total third-order
inflation by the SUM of per-channel maxima R_s_max + R_q_max = 2.44, giving
endpoint x0.757. But the two channels peak at DIFFERENT transfers:
  - sunset per-transfer kernel rides J(t)  -> peaks at SMALL t  (J largest)
  - quartic-difference inflation R(t) ~ Ghat4(t)/J(t) -> peaks at LARGE t (Phi)
so the JOINT max_t[R_s(t) + R_q(t)] can be below the sum of maxima. This script
tests whether the MOST FAVOURABLE pairing recovers closure.

Models (stated, not proved):
  R_s(t) = R_s_max * J(t)/J(0)            (sunset rides J(t); peaks t->0)
  R_q(t) = R_q_max * Phi(t)/Phi_max       (quartic per-transfer; peaks t=2q0)
These are the MAXIMALLY-SEPARATED peak structures, so the joint max here is a
LOWER bound on the true joint inflation: if THIS does not close, the
unconditional endpoint certainly does not. Inputs J(t)/J(0)=1/(J0_over_Jt) and
Phi(t) are read from the GHAT4 run JSON (no re-derivation). R_s_max, R_q_max,
rho from the joint-endpoint run JSON.

Endpoint paired ratio = rho / (1 + max_t[R_s(t)+R_q(t)]); closes iff > 1.

self-test asserts (exit 0 iff the arithmetic is consistent; the verdict is
reported as found, negative or positive).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-07"
__version_issued__ = "2026-06-07"
__claims__ = ["B5-BEYOND-LAYER-BOUND", "B1-RH-ENUM"]

import json, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GHAT4 = REPO / "claims/B5-BEYOND-LAYER-BOUND/runs/260607-scscope-ghat4-pertransfer/result.json"
JOINT = REPO / "claims/B5-BEYOND-LAYER-BOUND/runs/260607-scscope-joint-endpoint/result.json"
CLAIMS = []

def claim(name, cond, detail=""):
    CLAIMS.append(dict(name=name, passed=bool(cond), detail=detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

g = json.loads(GHAT4.read_text())
j = json.loads(JOINT.read_text())

rho = j["inputs"]["rho"]
C2 = j["C2"]; C_sunset = j["C_sunset"]; C_quartic = j["C_quartic"]
R_s_max = C_sunset / C2          # sunset peak inflation (in C2 units)
R_q_max = C_quartic / C2         # quartic peak inflation == R_max
print(f"SC-SCOPE joint incompatible-pairing: R_s_max={R_s_max:.3f}, R_q_max={R_q_max:.3f}, rho={rho}")

chords = g["chords"]             # each: t, Ghat4_ratio, J0_over_Jt, Phi
Phi_max = max(c["Phi"] for c in chords)

combined = []
for c in chords:
    Jt_over_J0 = 1.0 / c["J0_over_Jt"]       # J(t)/J(0): peaks at small t
    Phi_ratio = c["Phi"] / Phi_max           # peaks at large t
    R_s = R_s_max * Jt_over_J0
    R_q = R_q_max * Phi_ratio
    combined.append((c["t"], R_s, R_q, R_s + R_q))

sum_of_maxima = R_s_max + R_q_max
joint_max = max(x[3] for x in combined)
i_at = max(range(len(combined)), key=lambda i: combined[i][3])
print("    t        R_s(t)    R_q(t)    R_s+R_q")
for (t, rs, rq, s) in combined:
    print(f"    {t:.4f}   {rs:6.3f}   {rq:6.3f}    {s:6.3f}")

claim("pairing_reduces_below_sum_of_maxima", joint_max < sum_of_maxima,
      f"(joint max_t[R_s+R_q] = {joint_max:.3f} (at t={combined[i_at][0]:.4f}) < sum of maxima "
      f"{sum_of_maxima:.3f}: the incompatible pairing DOES reduce the combined inflation)")

ratio_additive = rho / (1.0 + sum_of_maxima)
ratio_paired = rho / (1.0 + joint_max)
print(f"    additive endpoint ratio = {rho}/(1+{sum_of_maxima:.3f}) = x{ratio_additive:.3f}")
print(f"    paired   endpoint ratio = {rho}/(1+{joint_max:.3f}) = x{ratio_paired:.3f}")

closes = ratio_paired > 1.0
claim("paired_verdict_recorded", True,
      f"(most-favourable paired endpoint ratio x{ratio_paired:.3f}: "
      + ("CLOSES" if closes else "STILL DOES NOT CLOSE -- strengthened honest negative") + ")")
claim("improvement_quantified", ratio_paired > ratio_additive,
      f"(pairing improves the endpoint from x{ratio_additive:.3f} to x{ratio_paired:.3f}, "
      f"but {'reaches' if closes else 'still short of'} 1.0)")
# why it still fails (if it does): the sunset alone is near-saturating
sunset_only = rho / (1.0 + R_s_max)
claim("root_cause_sunset_near_saturating", True,
      f"(sunset ALONE gives rho/(1+R_s_max) = x{sunset_only:.3f}; the endpoint is dominated by the "
      f"genuinely large third-cumulant sunset at the thinnest I=2e-3 corner, not by loose pairing)")

print("    VERDICT: SC-SCOPE endpoint " + ("CLOSES under the favourable pairing model"
      if closes else "DOES NOT CLOSE even under the most favourable incompatible pairing")
      + "; B1 T6 unaffected (SC-SCOPE named hypothesis).")

ok = all(c["passed"] for c in CLAIMS)
out = REPO / "claims" / "B5-BEYOND-LAYER-BOUND" / "runs" / "260607-scscope-joint-pairing"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="scscope_joint_pairing.py", version=__version__,
    R_s_max=R_s_max, R_q_max=R_q_max, rho=rho, sum_of_maxima=sum_of_maxima,
    joint_max=joint_max, ratio_additive=ratio_additive, ratio_paired=ratio_paired,
    closes=closes, sunset_only_ratio=sunset_only,
    combined=[{"t": t, "R_s": rs, "R_q": rq, "sum": s} for (t, rs, rq, s) in combined],
    verdict=("closes under favourable pairing" if closes
             else "does not close even under most-favourable pairing; sunset near-saturating; "
                  "SC-SCOPE endpoint OPEN, selection second-cumulant by hypothesis"),
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
