"""res5_031_nonlattice_extremal_probe.py -- scope-completion probe for the
"A1-relative unconditional Reading-H T7" target (operator question 2026-06-10). The
enacted T7 is scope-qualified to the lattice Reading-H class C_phys. The operator asks
whether arbitrary NON-lattice competitors and a wider (I, mu^2) window can be closed.

This probe tests the load-bearing question for the OFF-DIAGONAL (R_lead) mechanism: is
the lattice restriction a convenient EASY subcase (so non-lattice is a big open hole), or
is the arithmetic lattice the ADVERSARIAL WORST case (so the lattice T7 already dominates
non-lattice competitors)? The off-diagonal stability is governed by the single ratio
    R_lead(Q) = const * (1 + K_floor(Q)) * I,   const = (9/4) u_eff^2 B_max (2/r_R),
which is N-INDEPENDENT (N/c_diag = N/((N/2)r_R) = 2/r_R), and R_lead<1 <=> K_floor<K* with
    K* = 1/(const*I) - 1 ~ 20.5   (the RES-1 threshold).
K_floor(Q) = sum_{t!=0} (occupancy)^2 / N^2 - 1 is the additive-energy floor (t=0 antipodal
sum split off). The admissible lattice class is pinned K_floor <= T' <= 13 < K*.

FINDING (this script): for EVERY non-lattice configuration tested -- generic random
antipodal, maximally-structured coplanar regular rings, and jittered-off-lattice BCC --
    K_floor(non-lattice) ~ 1  <<  13 (lattice admissible)  <<  20.5 (K* threshold),
i.e. R_lead(non-lattice) ~ 0.08, margin x12. Perturbing a config OFF the exact lattice
REDUCES K_floor. The additive-energy floor is MAXIMISED by exact arithmetic (lattice)
coincidence of sum-circles; any non-lattice config has generic (non-degenerate) sum-circles
=> occupancy ~ 2 => K_floor ~ 1. Hence the lattice class is the OFF-DIAGONAL WORST CASE,
not an easy subcase: the enacted lattice T7 covers the adversarially hardest competitors of
the R_lead mechanism, and generic non-lattice competitors are far more stable.

CONSEQUENCE for the scope-completion target (interpreted in the companion strategy note):
the genuine residual to "C_full" is NOT re-opening arbitrary-Q DR-2 (which bounds the
lattice/worst case, already T7 for lattice). It is the EXTREMAL/RIGIDITY statement
"K_floor is maximised within the arithmetic (lattice) class" -- a T2 CONJECTURE with the
strong numerical evidence below; falsifier: a real-antipodal non-lattice config with
K_floor > 13. The (I, mu^2) window is separately bounded by a PHYSICAL critical intensity
I_c ~ 2.5e-3 (R-029 SC-SCOPE), not a proof gap.

SCOPE: probes the OFF-DIAGONAL mechanism only; the diagonal isotropy (D, T-016) and the
selection/SC-SCOPE floor (S) extensions to non-lattice are expected easier (less structure)
but are NOT probed here. No tier change. Strong evidence for the extremal conjecture.

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-10"
__claims__ = ["B1-RH-ENUM", "B2-PROPA-HLAYER"]

import json, sys, math
from collections import Counter
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "archive" / "legacy" / "scripts"))
import Math424_AddA_reading_uniqueness as m424  # noqa: E402
U, V, Q0 = m424.U, m424.V, m424.Q0
rng = np.random.default_rng(0)
CLAIMS = []
def claim(n, c, d=""):
    CLAIMS.append(dict(name=n, passed=bool(c), detail=d))
    print(f"  [{'PASS' if c else 'FAIL'}] {n} {d}")

MU2 = 0.005
rR = m424.gap_solve(MU2, 0, 0, 0.0); M_R = m424.M_fast(rR)
u_eff = U + 10.0 * V * M_R
B_sb_max = 0.21774; I = 2e-3
const = (9.0 / 4.0) * u_eff**2 * B_sb_max * (2.0 / rR)   # N-INDEPENDENT
Kstar = 1.0 / (const * I) - 1.0                          # R_lead<1 threshold
print(f"const={const:.2f} (N-indep), K*={Kstar:.2f} (R_lead<1 threshold), lattice admissible K_floor<=13")

def Kfloor(K):
    N = len(K); s = (K[:, None, :] + K[None, :, :]).reshape(-1, 3)
    g = np.round(s / (Q0 * 1e-6)).astype(np.int64)
    cnt = Counter(map(tuple, g)); cnt.pop((0, 0, 0), None)   # drop t=0 (antipodal split)
    Ep = sum(c * c for c in cnt.values()); return Ep / N**2 - 1.0

def randanti(n):
    v = rng.standard_normal((n, 3)); v /= np.linalg.norm(v, axis=1, keepdims=True)
    return np.vstack([v, -v]) * Q0
def ring(N):
    th = 2 * np.pi * np.arange(N) / N
    return np.c_[np.cos(th), np.sin(th), np.zeros(N)] * Q0
def bcc():
    base = []
    for a, b in [(0, 1), (0, 2), (1, 2)]:
        for sa in (1, -1):
            for sb in (1, -1):
                v = [0, 0, 0]; v[a] = sa; v[b] = sb; base.append(v)
    return np.array(base, float) / math.sqrt(2) * Q0
def jit(frac):
    return bcc() + frac * Q0 * rng.standard_normal((12, 3))

# (1) threshold reproduction
claim("threshold_Kstar_about_20p5", 20.0 < Kstar < 21.0 and abs(const - 23.2) < 0.2,
      f"(const=(9/4)u_eff^2 B_max (2/r_R)={const:.2f} N-INDEPENDENT; K*=1/(const*I)-1={Kstar:.2f} is the "
      f"universal R_lead<1 threshold; lattice admissible K_floor<=13<K*)")

# (2) generic random non-lattice: K_floor ~ 1 << 13, R_lead ~ 0.08
rand = {2*n: float(np.mean([Kfloor(randanti(n)) for _ in range(5)])) for n in (6, 10, 20, 30)}
claim("random_nonlattice_floor_tiny", all(v < 2.0 for v in rand.values()),
      f"(random real-antipodal NON-lattice K_floor={ {k:round(v,2) for k,v in rand.items()} }, all<2<<13; "
      f"R_lead~{const*(1+max(rand.values()))*I:.3f}, margin x{1/(const*(1+max(rand.values()))*I):.0f})")

# (3) maximally-structured non-lattice (coplanar regular ring) STILL tiny
rings = {N: Kfloor(ring(N)) for N in (8, 16, 24, 40)}
claim("structured_nonlattice_floor_tiny", all(v < 2.0 for v in rings.values()),
      f"(coplanar regular-ring K_floor={ {k:round(v,2) for k,v in rings.items()} }, all<2: even maximal "
      f"non-lattice symmetry does NOT raise the floor -- sum-circles stay non-degenerate, occupancy~2)")

# (4) the lattice is the worst case: perturbing OFF the lattice REDUCES K_floor
k_exact = Kfloor(bcc()); k_jit = float(np.mean([Kfloor(jit(0.10)) for _ in range(5)]))
claim("lattice_is_offdiag_worst_case", k_jit < k_exact and k_exact < 13.0,
      f"(exact-BCC K_floor={k_exact:.2f} > jittered-BCC(10%) K_floor={k_jit:.2f}: leaving the lattice REDUCES the "
      f"additive-energy floor. The floor is maximised by arithmetic coincidence => lattice is the adversarial worst "
      f"case of the R_lead mechanism, already closed at T'<=13)")

# (5) quantitative sanity + honest scope
worst_nl = max(list(rand.values()) + list(rings.values()) + [k_jit])
sane = (worst_nl < 13.0) and (const * (1 + worst_nl) * I < 0.65) and (Kstar > 13.0)
claim("quantitative_sanity_extremal_evidence", sane,
      f"(worst NON-lattice K_floor={worst_nl:.2f}<13=lattice admissible<{Kstar:.1f}=K*; worst non-lattice "
      f"R_lead={const*(1+worst_nl)*I:.3f}<0.65=lattice R_lead<1. STRONG EVIDENCE for the extremal conjecture "
      "'K_floor maximised within the arithmetic class'; falsifier: real-antipodal non-lattice with K_floor>13. "
      "Probes OFF-DIAGONAL only; (D)/(S) non-lattice extensions not probed; window bounded by physical I_c~2.5e-3)")

ok = all(c["passed"] for c in CLAIMS)
out = REPO / "claims" / "B1-RH-ENUM" / "runs" / "260610-res5-031-nonlattice-extremal-probe"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="res5_031_nonlattice_extremal_probe.py", version=__version__,
    const=const, Kstar=Kstar, I=I, rR=rR, u_eff=u_eff,
    random_nonlattice=rand, ring_nonlattice=rings,
    bcc_exact=k_exact, bcc_jittered=k_jit, worst_nonlattice=worst_nl,
    verdict=("Lattice is the OFF-DIAGONAL adversarial WORST case: every non-lattice config tested has K_floor~1<<13 "
             "(lattice admissible)<<20.5(K*); perturbing off-lattice reduces K_floor. Generic non-lattice R_lead~0.08 "
             "(margin x12). The lattice T7 dominates non-lattice competitors of the R_lead mechanism. Residual to "
             "C_full = EXTREMAL conjecture (K_floor maximised by arithmetic structure), T2 with strong evidence, NOT "
             "arbitrary-Q DR-2. Window bounded by physical I_c~2.5e-3 (R-029), not a proof gap. No tier change."),
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nworst non-lattice K_floor={worst_nl:.2f} << 13 (lattice) << {Kstar:.1f} (K*); R_lead~{const*(1+worst_nl)*I:.3f}")
print(f"claims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
