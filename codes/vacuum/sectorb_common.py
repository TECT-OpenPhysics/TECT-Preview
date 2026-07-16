"""sectorb_common.py -- single source of truth for Sector-B closed-form
quantities shared by the SC-SCOPE and ROBUSTNESS-MU2 scripts.

Created (2026-06-07) per governance/CODE-DISCIPLINE.md rule 1 (no hardcoded
derived numbers): the Prop-A layer margin and the minimum-transfer envelope
were being recomputed (robustness_mu2_margin_recompute.py) in one script and
PASTED as a literal (MARGIN=0.00432) in another. Both now import from here, so
a change to an INPUT propagates and no derived number is duplicated.

This is a LIBRARY module: definitions only, no top-level side effects. Run
`python codes/vacuum/sectorb_common.py --selftest` to reproduce the certified
anchor margin (0.00432) and exercise the helpers.

Convention (production; bare parameter R = mu^2; gap point r_R = gap_solve(mu^2)):
  M(m)      = (1/2pi^2) int_0^inf k^2 / D dk,   D = m + C(k^2 - q0^2)^2
  M_+(mu^2) = (-3u + sqrt(9u^2 - 60 v mu^2)) / (30 v)         (upper PD branch)
  M_c       = -u/(10 v)                                       (mu^2-independent)
  PB(M)     = 1/2 (mu^2 - r_R)(M - M_R) + 3/4 u (M^2 - M_R^2) + 5/2 v (M^3 - M_R^3)
  rhat0(Mc) = mu^2 - 3 u^2 / (20 v)
  DIP_BAND  = |rhat0(Mc)|^{3/2} / (3 sqrt(v))
  MARGIN(mu^2) = PB(M_+(mu^2)) - DIP_BAND(mu^2)   (Math437 v1.2 / Math440)
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-07"
__version_issued__ = "2026-06-07"

import math
import sys
from functools import lru_cache
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "archive" / "legacy" / "scripts"))
import Math424_AddA_reading_uniqueness as m424  # noqa: E402

# physical / Lagrangian INPUTS (single source: the legacy constants module).
U, V, Q0, C = m424.U, m424.V, m424.Q0, m424.C
M_c = -U / (10.0 * V)

# Registered evaluation points for the STEP-5B certificate.  These are inputs
# defining the certified band, not outputs pasted from a prior run.
ANCHOR_MU2 = 0.005
CERTIFIED_INTENSITIES = (4e-4, 1e-3, 2e-3)
ENDPOINT_HARDENED_INTENSITIES = frozenset((4e-4, 2e-3))


def M_radial(m, kmax=40.0, n=600000):
    """Independent radial quadrature of M(m) = (1/2pi^2) int k^2/D dk."""
    k = np.linspace(1e-6, kmax, n)
    D = m + C * (k**2 - Q0**2)**2
    return float(np.trapezoid(k**2 / D, k) / (2.0 * np.pi**2))


def margin_of(mu2):
    """Exact closed-form Prop-A layer margin MARGIN(mu2) = PB(M_+) - DIP_BAND,
    plus the branch diagnostics needed to certify the band is the same PD branch."""
    rR = m424.gap_solve(mu2, 0, 0, 0.0)
    MR = m424.M_fast(rR)
    disc = 9.0 * U * U - 60.0 * V * mu2            # > 0 required (two-branch regime)
    Mp = (-3.0 * U + math.sqrt(disc)) / (30.0 * V) if disc > 0 else float("nan")

    def PB(M):
        return (0.5 * (mu2 - rR) * (M - MR) + 0.75 * U * (M * M - MR * MR)
                + 2.5 * V * (M**3 - MR**3))

    rh0_Mc = mu2 - 3.0 * U * U / (20.0 * V)
    DIP_BAND = abs(rh0_Mc)**1.5 / (3.0 * math.sqrt(V))
    return dict(mu2=mu2, rR=rR, MR=MR, Mp=Mp, M_c=M_c, disc=disc,
                PB_Mp=PB(Mp), DIP_BAND=DIP_BAND, margin=PB(Mp) - DIP_BAND,
                branch_ok=(disc > 0 and Mp > M_c))


def J_of_t(t, r_diag, nk=500, nmu=320, kmax_fac=8.0):
    """Minimum-transfer envelope J(t) at diagonal dressing r_diag."""
    k = np.linspace(1e-6, kmax_fac * Q0, nk)
    mu = np.linspace(-1.0, 1.0, nmu)
    Kg, MUg = np.meshgrid(k, mu, indexing="ij")
    Dk = r_diag + C * (Kg**2 - Q0**2)**2
    kp2 = Kg**2 + t**2 + 2.0 * Kg * t * MUg
    Dkp = r_diag + C * (kp2 - Q0**2)**2
    inner = np.trapezoid(Kg**2 / (Dk * Dkp), mu, axis=1)
    return float(np.trapezoid(inner, k) / (4.0 * np.pi**2) * 2.0)


@lru_cache(maxsize=None)
def _conservative_J_max(mu2):
    """AddC/S18 conservative transfer envelope, derived at ``mu2``."""
    rR = m424.gap_solve(mu2, 0, 0, 0.0)
    chords = (0.5 * Q0, Q0, math.sqrt(2.0) * Q0,
              math.sqrt(3.0) * Q0, 2.0 * Q0)
    return max(J_of_t(t, rR) for t in chords)


@lru_cache(maxsize=None)
def step5b_budget(mu2, intensity, minimum_transfer=True):
    """Derive the STEP-5B budget and closure ratio from physical inputs.

    ``minimum_transfer=True`` is the AddE endpoint-hardening prescription.
    ``False`` retains the conservative AddC transfer envelope.  The returned
    dictionary exposes every intermediate so callers and tests can audit the
    convention rather than consuming an opaque derived number.
    """
    margin = margin_of(mu2)["margin"]
    rR = m424.gap_solve(mu2, 0, 0, 0.0)
    MR = m424.M_fast(rR)
    lam = 3.0 * U + 30.0 * V * MR
    rhat = rR + 2.0 * lam * intensity
    a0 = 2.0 * lam * intensity / rhat
    theta_min = math.sqrt(rhat) / (2.0 * Q0**2 * math.sqrt(C))
    n_pack = 16.0 / theta_min**2
    t_min = 2.0 * Q0 * math.sin(theta_min / 2.0)
    J_budget = (J_of_t(t_min, rhat) if minimum_transfer
                else _conservative_J_max(mu2))
    K_bound = 8.0 + 4.0 * math.sqrt(14.0) * math.sqrt(n_pack)
    K_budget = (4.0 * (1.0 - a0) * margin
                / ((lam * intensity)**2 * J_budget))
    return dict(mu2=mu2, intensity=intensity, margin=margin, rR=rR,
                MR=MR, lambda_prime=lam, rhat=rhat, a0=a0,
                theta_min=theta_min, n_pack=n_pack, t_min=t_min,
                J_budget=J_budget, K_bound=K_bound, K_budget=K_budget,
                rho=K_budget / K_bound,
                minimum_transfer=bool(minimum_transfer))


def rho_for_transfer_cap(Tprime, mu2=ANCHOR_MU2, intensity=2e-3):
    """Endpoint SC-SCOPE ratio ``K_budget/(1+T')``, derived not pasted.

    The budget is rounded to the one-decimal precision registered by the
    original certificate (266.7) before forming the ratio.
    """
    budget = step5b_budget(mu2, intensity, minimum_transfer=True)["K_budget"]
    return round(budget, 1) / (1.0 + Tprime)


# Public compatibility map used by the SC-SCOPE scripts.  Values are computed
# from the AddC/AddE prescriptions and rounded only to the precision carried by
# the registered certificate (59.4 / 8.8 / 2.6).
RHO = {
    intensity: round(step5b_budget(
        ANCHOR_MU2,
        intensity,
        minimum_transfer=(intensity in ENDPOINT_HARDENED_INTENSITIES),
    )["rho"], 1)
    for intensity in CERTIFIED_INTENSITIES
}


def u_eff(M):
    return U + 10.0 * V * M


def _selftest():
    a = margin_of(ANCHOR_MU2)
    # reproduce the certified Math437 anchor constants (test oracles)
    assert abs(a["Mp"] - 0.051071995662105595) < 1e-9, "M_+ anchor"
    assert abs(a["PB_Mp"] - 0.0052459635246063716) < 1e-7, "PB(M_+) anchor"
    assert abs(a["DIP_BAND"] - 9.259526852124812e-04) < 1e-9, "DIP_BAND anchor"
    assert abs(a["margin"] - 0.00432) < 5e-5, "MARGIN reproduces 0.00432"
    assert a["branch_ok"], "anchor on the upper PD branch"
    # M quadratures agree
    assert abs(M_radial(a["rR"]) - m424.M_fast(a["rR"])) < 1.5e-2 * a["MR"], "M quadrature"
    # J positive and finite
    j = J_of_t(1e-9, a["rR"] + 2.0 * (3 * U + 30 * V * a["MR"]) * 4e-4)
    assert 0.2 < j < 0.4, "J(0) anchor magnitude"
    # independently reproduce the registered STEP-5B ratios.  These are test
    # oracles; production values above are recomputed from the physical inputs.
    assert RHO == {4e-4: 59.4, 1e-3: 8.8, 2e-3: 2.6}, "RHO certificate"
    assert abs(rho_for_transfer_cap(13.0) - 266.7 / 14.0) < 1e-12, "endpoint budget"
    print(f"SECTORB-COMMON-SELFTEST: PASS (MARGIN(0.005)={a['margin']:.6f}, "
          f"M_c={M_c:.6f}, J0~{j:.4f}, RHO={RHO})")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
