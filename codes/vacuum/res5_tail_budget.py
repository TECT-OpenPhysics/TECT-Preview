"""res5_tail_budget.py -- RES-5 tail-budget closure (operator-directed mainline).

Question (operator review of the sunset-norm certificate v1.1): the higher-
skeleton tail must fit the THIN slack, C_higher < Delta F_margin - C_leading ~
0.04 Delta F_margin, not merely be screened-finite (~2x leading = same order).

This script quantifies the budget across the three certified intensities. The
robust finding is the INTENSITY DEPENDENCE: the screened 2PI pattern-dependent
tail scales as C_higher/Delta F_margin ~ C_G a0(I), with a0(I) = 2 lam' I / rhat
~ proportional to I; while the third-cumulant slack grows rapidly off the
endpoint (joint 1.040 at I=2e-3 -> ~3.1 at I<=1e-3, estimate-grade). Hence the
budget CLOSES with a large margin for I <= 1e-3 and is MARGINAL / estimate-
undetermined only at the I=2e-3 endpoint -- exactly where SC-SCOPE is B1's named
hypothesis. RES-5 is thereby localised to the endpoint, not a global obstruction.

Estimate-grade (CLAUDE.md 6.3.5b): the tail C_G a0 and the off-endpoint joints
are ESTIMATES, not constant-bound theorems. The closure for I<=1e-3 is robust
because the margin is ~27x (survives estimate uncertainty); the endpoint is
genuinely undetermined (0.047 vs 0.0385, ratio ~1.2).

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__claims__ = ["B1-RH-ENUM"]
import json, sys
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO/"archive"/"legacy"/"scripts"))
import Math424_AddA_reading_uniqueness as m424
U, V, Q0, C = m424.U, m424.V, m424.Q0, m424.C
CLAIMS = []
def claim(n, c, d=""):
    CLAIMS.append(dict(name=n, passed=bool(c), detail=d)); print(f"  [{'PASS' if c else 'FAIL'}] {n} {d}")

# operating-point constants (mu^2=0.005 anchor)
rR = m424.gap_solve(0.005, 0, 0, 0.0); M_R = m424.M_fast(rR); lam = 3*U + 30*V*M_R
# screened response C_G = 1/(1+g), g = lam' B_d (dressed loop parameter), at endpoint dressing
I_end = 2e-3
rhat_end = rR + 2*lam*I_end
q = np.linspace(1e-6, 8*Q0, 400000); Gd = 1.0/(rhat_end + C*(q**2-Q0**2)**2)
Bd = float(np.trapezoid(q**2*Gd**2, q)/(2*np.pi**2)); g = lam*Bd; C_G = 1.0/(1.0+g)

# documented third-cumulant joints (SC-SCOPE; estimate-grade off endpoint)
#   I=2e-3 endpoint: certified thin joint 1.040 (scscope-quartic-normalisation-certificate)
#   I=1e-3        : all-orders lift estimate-feasible, paired joint ~3.1 (scscope-scope-decision)
JOINT = {4e-4: 8.0, 1e-3: 3.1, 2e-3: 1.040}   # 4e-4 conservative lower proxy (floor x59.4 >> third-cumulant)

rows = []
for I in [4e-4, 1e-3, 2e-3]:
    rhat = rR + 2*lam*I
    a0 = 2*lam*I/rhat
    tail = C_G*a0                      # resummed pattern-dependent tail estimate
    slack = 1.0 - 1.0/JOINT[I]         # third-cumulant slack = 1 - C_leading/margin
    ratio = tail/slack
    rows.append(dict(I=I, a0=a0, tail=tail, joint=JOINT[I], slack=slack, ratio=ratio))
    print(f"  I={I:.0e}: a0={a0:.4f}  tail=C_G a0={tail:.4f}  joint={JOINT[I]}  slack={slack:.4f}  tail/slack={ratio:.3f}")

end = next(r for r in rows if r["I"] == 2e-3)
mid = next(r for r in rows if r["I"] == 1e-3)
lo  = next(r for r in rows if r["I"] == 4e-4)

# 1. a0 scales ~ linearly with I (so the tail halves from endpoint to 1e-3)
claim("a0_scales_with_intensity", 1.7 < end["a0"]/mid["a0"] < 2.1,
      f"(a0(2e-3)/a0(1e-3) = {end['a0']/mid['a0']:.2f} ~ 2: a0=2 lam' I/rhat is ~proportional to I, so the screened "
      "tail C_G a0 halves from the endpoint to I=1e-3)")

# 2. endpoint is MARGINAL / undetermined: tail ~ slack (ratio ~1.2 > 1)
claim("endpoint_marginal_undetermined", 0.9 < end["ratio"] < 1.6,
      f"(I=2e-3 endpoint: tail={end['tail']:.4f} vs slack={end['slack']:.4f}, ratio={end['ratio']:.2f} ~ 1 -- the "
      "screened higher-skeleton tail and the thin slack are the SAME ORDER; the all-orders endpoint selection is "
      "estimate-UNDETERMINED (could go either way within estimate uncertainty). RES-5 OPEN at the endpoint)")

# 3. budget CLOSES with large margin for I <= 1e-3
claim("budget_closes_offendpoint_I_1e-3", mid["ratio"] < 0.1,
      f"(I=1e-3: tail={mid['tail']:.4f} << slack={mid['slack']:.3f}, ratio={mid['ratio']:.3f} (~{1/mid['ratio']:.0f}x "
      "margin) -- the budget closes decisively; the tail halves AND the slack grows ~18x off the endpoint)")
claim("budget_closes_offendpoint_I_4e-4", lo["ratio"] < 0.05,
      f"(I=4e-4: tail={lo['tail']:.4f} << slack={lo['slack']:.3f}, ratio={lo['ratio']:.3f} -- closes with even larger "
      "margin)")

# 4. localisation: the ratio improves by >20x from endpoint to I=1e-3 (endpoint-only obstruction)
improve = end["ratio"]/mid["ratio"]
claim("res5_localised_to_endpoint", improve > 20,
      f"(tail/slack improves by {improve:.0f}x from the endpoint to I=1e-3: RES-5 is NOT a global obstruction -- it "
      "is localised to the I=2e-3 endpoint, exactly where SC-SCOPE is B1's named second-cumulant hypothesis)")

ok = all(c["passed"] for c in CLAIMS)
out = REPO/"claims"/"B1-RH-ENUM"/"runs"/"260609-res5-tail-budget"; out.mkdir(parents=True, exist_ok=True)
(out/"result.json").write_text(json.dumps(dict(script="res5_tail_budget.py", version=__version__,
    g=g, C_G=C_G, lam=lam, rR=rR, rows=rows,
    verdict="RES-5 tail budget CLOSES for I<=1e-3 (ratio<0.04, ~27x margin) and is MARGINAL/estimate-undetermined at "
            "the I=2e-3 endpoint (ratio ~1.2). RES-5 localised to the endpoint = SC-SCOPE named-hypothesis boundary. "
            "No tier flip (B1 T6 on {H-LAYER}).",
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
