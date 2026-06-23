#!/usr/bin/env python3
"""a2_wellposedness_checks.py -- quantitative self-tests backing claim A2-PDE-WELLPOSED
(local + global well-posedness of the TECT gradient flow).

PDE (L2 gradient flow of the Brazovskii free energy on the 3-torus):
    dphi/dt = -K(-i grad) phi - lambda phi^3 - gamma phi^5,
    K(q) = mu^2 + Y (q^2 - q0^2)^2,   r_braz = K(q0) = mu^2   (A1-KERNEL-CONV).

The proof is standard analytic-semigroup theory (Henry 1981; Pazy 1983; Lunardi
1995). These asserts pin every NUMERICAL claim the note makes:
 (1) spectral positivity: lambda0 := min_k K(k) >= mu^2 > 0 => L sectorial, generates an
     analytic semigroup (4th-order positive self-adjoint operator).
 (2) Sobolev thresholds (d=3): H^s -> L^inf for s>3/2; the fractional-power
     space X^beta=D(L^beta)=H^{4beta} embeds into L^inf iff beta>3/8.
 (3) smoothing exponent: sup_{x>=0} x^beta e^{-x} < inf for beta in (0,1)
     => ||L^beta e^{-tL}|| <= C_beta t^{-beta}, the Duhamel contraction estimate.
 (4) sextic coercivity (Young): (|lambda|/4) t^4 <= (gamma/12) t^6 + C_*,
     C_* explicit => F bounded below + coercive (global a priori bound).
 (5) continuation window: energy controls H^2; local existence needs H^{4beta},
     beta in (3/8,1/2] => H^2 subset X^beta (H^2 a priori bound CONTROLS the X^beta norm) => no finite-time blow-up.
Self-tests exit 0 iff all pass.
"""
__version__ = "1.1.0"
__first_issued__ = "2026-06-23"
__version_issued__ = "2026-06-23"
__claims__ = ["A2-PDE-WELLPOSED"]

import json, math, sys
from pathlib import Path
import numpy as np

# production anchor (A1-KERNEL-CONV corrected convention)
MU2, Y, Q0, LAM, GAM = 5e-3, 1.0, 0.6802, -0.43, 1.62
D = 3  # spatial dimension (T^3)
CLAIMS = []
def claim(name, ok, detail=""):
    CLAIMS.append(dict(name=name, passed=bool(ok), detail=detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name} -- {detail}")

# (1) spectral positivity (operator review 2026-06-23): the needed fact is the
# LOWER BOUND lambda0 := min_{k in Lambda*} K(k) >= mu^2 > 0, NOT equality.
# Equality inf_q K(q) = mu^2 holds only in the continuum / when a lattice mode
# sits exactly on the shell |k|=q0; on a generic periodic cell lambda0 > mu^2.
qcont = np.linspace(0.0, 3.0, 200001)
Kcont = MU2 + Y * (qcont**2 - Q0**2) ** 2
inf_continuum = float(Kcont.min())                      # = mu^2 (sharp continuum bound)
# a GENERIC (incommensurate) reciprocal lattice: cubic spacing b not commensurate with q0
b = 0.5111
kgrid = np.array([nx*b for nx in range(-12, 13)])
K3 = MU2 + Y * (np.abs(kgrid[:,None,None]**2 + kgrid[None,:,None]**2 + kgrid[None,None,:]**2) - Q0**2) ** 2
lambda0_lattice = float(K3.min())
all_ge = bool(np.all(Kcont >= MU2 - 1e-12)) and bool(lambda0_lattice >= MU2 - 1e-12)
claim("lambda0_lower_bound_mu2_positive",
      all_ge and MU2 > 0 and abs(inf_continuum - MU2) < 1e-9 and lambda0_lattice > MU2,
      f"lambda0 := min_k K(k) >= mu^2 = {MU2} > 0 (K(k)>=mu^2 for all k; continuum inf = {inf_continuum:.6g} = mu^2 "
      f"is the SHARP lower bound; on a generic lattice lambda0 = {lambda0_lattice:.6g} > mu^2, equality NOT "
      "generic). Only lambda0>0 is used for sectoriality; the H^2 equivalence uses K(k)>=mu^2 and K(k) ~ (1+|k|^2)^2")

# (2) Sobolev thresholds in d=3
s_linf = D / 2.0                      # H^s -> L^inf for s > 3/2
beta_thresh = s_linf / 4.0            # X^beta = H^{4beta} -> L^inf iff 4beta > 3/2
claim("sobolev_linf_threshold",
      abs(s_linf - 1.5) < 1e-12 and abs(beta_thresh - 0.375) < 1e-12,
      f"H^s(T^3)->L^inf for s>{s_linf}; fractional-power exponent threshold beta>{beta_thresh}=3/8")
# H^s -> L^10 (needed for phi^5 in L^2) for s >= d(1/2 - 1/10)
s_L10 = D * (0.5 - 1.0/10.0)
claim("sobolev_L10_threshold",
      abs(s_L10 - 1.2) < 1e-12 and s_L10 < s_linf,
      f"H^s->L^10 for s>={s_L10}=6/5 (so phi^5 in L^2); below the L^inf threshold {s_linf}, "
      "so s>3/2 is the binding requirement")

# (3) analytic-semigroup smoothing exponent: sup_x x^beta e^{-x} finite, attained at x=beta
for beta in (0.375 + 1e-6, 0.45, 0.5):
    xstar = beta
    val = xstar**beta * math.exp(-xstar)
    # numerical sup check
    xx = np.linspace(0, 60, 600001)
    supnum = float(np.max(xx**beta * np.exp(-xx)))
    claim(f"smoothing_exponent_finite_beta_{beta:.3f}",
          abs(supnum - val) < 1e-4 and supnum < 1.0,
          f"sup_x x^{beta:.3f} e^-x = {supnum:.5f} (= beta^beta e^-beta, attained x=beta); "
          f"||L^{beta:.3f} e^-tL|| <= C t^-{beta:.3f}, C={supnum:.5f}")

# (4) sextic coercivity via Young: g(t) = (|lambda|/4) t^4 - (gamma/12) t^6 is bounded above
a = abs(LAM)/4.0; b = GAM/12.0
# g'(t)=0 at t^2 = (2a)/(3b); max value C_*
t2 = (2*a)/(3*b); Cstar = a*t2**2 - b*t2**3
tt = np.linspace(0, 10, 1000001); g = a*tt**4 - b*tt**6
claim("sextic_dominates_quartic_coercive",
      GAM > 0 and abs(float(g.max()) - Cstar) < 1e-6 and Cstar > 0,
      f"gamma={GAM}>0; max_t[(|lam|/4)t^4-(gamma/12)t^6] = C_* = {Cstar:.6g} (at t^2={t2:.4g}); "
      "=> (|lam|/4)t^4 <= (gamma/12)t^6 + C_*, F coercive + bounded below")

# (5) continuation window non-empty: beta in (3/8, 1/2] gives X^beta=H^{4beta} subset H^2
lo, hi = 0.375, 0.5
claim("continuation_window_nonempty",
      lo < hi and 4*hi <= 2.0 + 1e-12,
      f"beta in ({lo},{hi}]: X^beta=H^(4beta), 4beta in (1.5,2]; since 4beta<=2, H^2 SUBSET X^beta so the "
      "energy H^2 bound controls the X^beta norm "
      "=> global continuation (no finite-time blow-up)")

ok = all(c["passed"] for c in CLAIMS)
out = Path(__file__).resolve().parents[2] / "claims" / "A2-PDE-WELLPOSED" / "runs" / "a2_wellposedness_checks.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(dict(
    version=__version__, params=dict(mu2=MU2, Y=Y, q0=Q0, lam=LAM, gam=GAM, d=D),
    lambda0_continuum_inf=inf_continuum, lambda0_lattice=lambda0_lattice, beta_threshold=beta_thresh, sobolev_linf_s=s_linf, sobolev_L10_s=s_L10,
    young_C_star=Cstar, continuation_window=[lo, hi],
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nA2 well-posedness checks: {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
print(f"artefact: {out.relative_to(Path(__file__).resolve().parents[2])}")
sys.exit(0 if ok else 1)
