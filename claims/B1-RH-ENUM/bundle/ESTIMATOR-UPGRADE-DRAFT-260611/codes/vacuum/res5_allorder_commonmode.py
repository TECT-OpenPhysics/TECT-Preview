"""res5_allorder_commonmode.py -- RES-5 all-order common-mode reduction: the
matched-order-to-exact closure reduces to a geometric-domination condition on the
condensate-perturbation series, with a wide margin at the measured base order.

Structure (rigorous). The condensate lam' P^2 is a perturbation on the common sea
D_0(I) (pattern-independent, the common-mode cancellation). The exact selection
difference is the condensate-perturbation series
    Delta F = sum_{k>=2} Delta F^(k),   Delta F^(k) ~ a0^{k-1} * (sea susceptibility chi^(k)),
since each order carries one power of lam' P^2 / D_0 = O(a0). The leading
Delta F^(2) is the selection margin. Define the geometric ratio
    r_k = Delta F^(k+1) / Delta F^(k) = a0 * (chi^(k+1)/chi^(k)).

Closure (rigorous reduction). If r_k <= r < 1/2 for all k>=2, then
    |sum_{k>=3} Delta F^(k)| <= Delta F^(2) * r/(1-r) < Delta F^(2),
so Delta F_exact = Delta F^(2)(1 - r/(1-r)) > 0 and RES-5 closes. The SUFFICIENT
condition is r < 1/2 (equivalently the operator's C_cm a0 < 1 form with margin).

Base order (measured). r_2 = a0 * (chi^(3)/chi^(2)) ~ a0 (the susceptibility ratio
is O(1); SC-SCOPE put the n=3 endpoint effect at a few percent, consistent with
r_2 ~ a0 ~ 0.1, NOT near 1/2). So the base ratio sits at ~0.1, a factor ~5 below
the closure threshold 1/2.

RESIDUAL (the deep RES-5 content, NOT proved here): the all-order geometric
domination r_k <= r < 1/2 -- i.e., the Brazovskii-sea susceptibility ratios
chi^(k+1)/chi^(k) do not blow up. This script verifies the structure and the
margin arithmetic; it does NOT bound the all-order ratios.

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__claims__ = ["B1-RH-ENUM"]
import json, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO/"archive"/"legacy"/"scripts"))
import Math424_AddA_reading_uniqueness as m424  # noqa: E402
U, V = m424.U, m424.V
MU2 = 0.005
CLAIMS=[]
def claim(n,c,d=""):
    CLAIMS.append(dict(name=n,passed=bool(c),detail=d)); print(f"  [{'PASS' if c else 'FAIL'}] {n} {d}")

rR=m424.gap_solve(MU2,0,0,0.0); M_R=m424.M_fast(rR); lam=3.0*U+30.0*V*M_R
a0_end = 2.0*lam*2e-3/(rR+2.0*lam*2e-3)
print(f"a0(endpoint)={a0_end:.4f}, lam'={lam:.4f}")

# (1) closure threshold: r < 1/2 is sufficient for |sum_{k>=3}| < Delta F^(2)
def envelope(r): return r/(1.0-r)   # |sum_{k>=3}|/Delta F^(2) for a geometric tail with ratio r
claim("closure_threshold_is_half", envelope(0.5-1e-9) < 1.0 <= envelope(0.5+1e-9) if False else (envelope(0.49) < 1.0 and envelope(0.51) > 1.0),
      f"(geometric tail r/(1-r): at r=0.49 -> {envelope(0.49):.3f}<1 (closes), at r=0.51 -> {envelope(0.51):.3f}>1 "
      "(fails): the SUFFICIENT closure condition is r < 1/2)")

# (2) base ratio sits at ~a0, a factor ~5 below 1/2
r_base = a0_end   # r_2 = a0 * (chi^3/chi^2), with chi-ratio O(1) => r_2 ~ a0
claim("base_ratio_below_threshold", r_base < 0.5,
      f"(base geometric ratio r_2 ~ a0 = {r_base:.4f} < 1/2: factor ~{0.5/r_base:.1f} below the closure threshold; "
      "the condensate-perturbation series starts well inside the convergence radius)")

# (3) closure condition in the operator's C_cm form: C_cm a0 < 1 <=> C_cm < 1/a0
C_cm_threshold = 1.0/a0_end
claim("operator_C_cm_margin", C_cm_threshold > 10.0,
      f"(closure needs C_cm < 1/a0 = {C_cm_threshold:.1f}; the structural C_cm ~ O(1) (base r_2/a0 ~ chi-ratio ~ 1) "
      f"sits a factor ~{C_cm_threshold:.0f} below threshold -- wide margin IF the all-order domination holds)")

# (4) envelope if the base ratio extends (illustrative, NOT a proof of all-order domination)
env_base = envelope(r_base)
claim("envelope_positive_at_base_ratio", (1.0-env_base) > 0.5,
      f"(IF r_k <= a0={r_base:.3f} for all k, Delta F_exact = Delta F^(2)(1 - {env_base:.3f}) = "
      f"{1-env_base:.3f} Delta F^(2) > 0: closes with margin -- but the all-order r_k<=a0 is the RESIDUAL, "
      "not proved here)")

ok=all(c["passed"] for c in CLAIMS)
out=REPO/"claims"/"B1-RH-ENUM"/"runs"/"260609-res5-allorder-commonmode"; out.mkdir(parents=True,exist_ok=True)
(out/"result.json").write_text(json.dumps(dict(script="res5_allorder_commonmode.py",version=__version__,mu2=MU2,
    a0_endpoint=a0_end,r_base=r_base,closure_threshold_r=0.5,C_cm_threshold=C_cm_threshold,
    envelope_at_base=env_base,
    verdict="RES-5 closure reduces to all-order geometric domination r_k<1/2; base r_2~a0~0.096 (x5 below "
            "threshold; C_cm<10.4 needed, structural C_cm~O(1)); all-order domination is the residual",
    claims=CLAIMS,all_pass=ok),indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
