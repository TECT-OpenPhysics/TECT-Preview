"""res5_033_ext_adversarial_map.py -- Step 2 of the scope-completion roadmap: map the
additive-energy floor K_floor over the FULL admissible competitor class C_full (lattice +
non-lattice), establish the elementary antipodal lemma, and grade the EXT conjecture honestly.

Key distinction (the operator's "non-lattice" question, resolved). The off-diagonal stability
ratio is R_lead = const*(1+K_floor)*I, const=23.2 (N-indep), R_lead<1 <=> K_floor < K* = 20.55.
TWO different quantities must not be conflated:
  * T'(Q)   = max_{t!=0} #(Q cap C_t)        the max sum-circle occupancy   (L-infinity)
  * K_floor = sum_{t!=0} r(t)^2 / N^2 ... -1  the additive-energy floor      (L-2 average)
and K_floor <= T' (R-025, E_+ <= (1+T')N^2, unconditional).

ELEMENTARY ANTIPODAL LEMMA (proved, general -- any finite antipodal Q, any t!=0):
  if x in C_t = {y: y.t = |t|^2/2} then (-x).t = -|t|^2/2 != |t|^2/2 (t!=0), so -x not in C_t;
  each antipodal pair {x,-x} contributes <= 1 point to C_t => #(Q cap C_t) <= N/2.  Hence
      T'(Q) <= N/2   for every antipodal Q,   and so   K_floor <= T' <= N/2.
With the coherence packing bound N <= n_pack = 16/theta^2 = 40.68 at the endpoint,
      K_floor <= N/2 <= 20 < 20.55 = K*   =>   R_lead < 1  for ALL admissible competitors,
INCLUDING non-lattice -- a THIN margin x1.026 (this is the A_ext universal fallback of
T-022/T-023). So the OFF-DIAGONAL sector for C_full is ALREADY ESTABLISHED (thin), not a
conjecture; the lattice restriction of the enacted T7 bought the COMFORTABLE margin (T'<=13
=> x1.5), not closure.

THE EXT CONJECTURE (margin upgrade, NOT a closure blocker). The probe below maps the ACTUAL
K_floor and finds it ~1-3 across EVERY admissible family -- random non-lattice ~1, latitude-ring
antipodal pairs (T'=N/2 maximal!) ~2.3, rich Z^3 lattice shells (T' up to 16) ~3. So T' (up to
N/2=20) is a hugely LOOSE proxy: the L-2 floor stays ~3 even when the L-infinity occupancy is
maximal. EXT = "max_{C_full} K_floor is attained in the arithmetic subclass, ~3" would upgrade
the thin x1.026 fallback margin to a comfortable ~x5. It remains T2 (strong evidence; operator
2026-06-10: register T2, do NOT promote); a tight L-2 additive-energy bound is the promotion path.

CORRECTION to res5_031 (self-audit, CLAUDE.md 6.3): res5_031's headline "the lattice is the
off-diagonal worst case" used the SMALL BCC 12-shell (K_floor 1.75 excl). The broader map here
shows rich lattice shells (~3) AND latitude-ring antipodal pairs (~2.3) both EXCEED the 12-shell;
the honest statement is "K_floor ~ 1-3 across all admissible classes, far below K*, with T' a
loose proxy", not "lattice strictly worst". res5_031's per-family asserts remain valid.

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-10"
__claims__ = ["B1-RH-ENUM", "B2-PROPA-HLAYER", "B5-BEYOND-LAYER-BOUND"]

import json, sys, math
from collections import Counter
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "archive" / "legacy" / "scripts"))
import Math424_AddA_reading_uniqueness as m424  # noqa: E402
Q0 = m424.Q0
rng = np.random.default_rng(1)
CLAIMS = []
def claim(n, c, d=""):
    CLAIMS.append(dict(name=n, passed=bool(c), detail=d))
    print(f"  [{'PASS' if c else 'FAIL'}] {n} {d}")

const = 23.2; I = 2e-3; Kstar = 1.0/(const*I) - 1.0   # 20.55
n_pack = 40.68

def stats(K):
    N = len(K); scale = Q0*1e-6*max(1.0, float(np.max(np.abs(K)))/Q0)
    s = (K[:, None, :] + K[None, :, :]).reshape(-1, 3)
    g = Counter(map(tuple, np.round(s/scale).astype(np.int64)))
    g.pop(tuple(np.round(np.zeros(3)).astype(np.int64)), None)
    return N, max(g.values()), sum(c*c for c in g.values())/N**2 - 1.0
def is_antipodal(K):
    S = set(map(tuple, np.round(K/(Q0*1e-6)).astype(np.int64)))
    return all(tuple((-np.round(k/(Q0*1e-6))).astype(np.int64)) in S for k in K)
def randanti(M):
    v = rng.standard_normal((M, 3)); v /= np.linalg.norm(v, axis=1, keepdims=True)
    return np.vstack([v, -v])*Q0
def latring(M, h):
    rho = math.sqrt(Q0**2 - h**2); th = 2*np.pi*np.arange(M)/M
    up = np.c_[rho*np.cos(th), rho*np.sin(th), h*np.ones(M)]; return np.vstack([up, -up])
def zshell(R2):
    n = int(math.isqrt(R2))+1; pts = [(x, y, z) for x in range(-n, n+1) for y in range(-n, n+1)
            for z in range(-n, n+1) if x*x+y*y+z*z == R2]
    P = np.array(pts, float); return P/math.sqrt(R2)*Q0

# build the families (admissible: N<=n_pack for the closure claim; larger N to show K_floor bounded)
fam = {}
fam["random_antipodal_N20"] = randanti(10)
fam["random_antipodal_N40"] = randanti(20)
fam["latring_N20_Tmax"] = latring(10, 0.3*Q0)
fam["latring_N40_Tmax"] = latring(20, 0.3*Q0)
fam["zshell_R9_N30"] = zshell(9)
fam["zshell_R18_N36"] = zshell(18)
S = {k: stats(v) for k, v in fam.items()}
for k, (N, T, Kf) in S.items():
    print(f"  {k:24s}: N={N:2d} T'={T:2d} K_floor={Kf:.2f} (T'<=N/2={N/2:.0f}? {T<=N/2})")

# (1) ELEMENTARY ANTIPODAL LEMMA: T' <= N/2 for every antipodal config
lemma_ok = all(is_antipodal(v) and S[k][1] <= S[k][0]/2 + 1e-9 for k, v in fam.items())
claim("antipodal_lemma_Tprime_le_Nhalf", lemma_ok,
      "(elementary lemma: x in C_t => -x not in C_t for t!=0, so each antipodal pair gives <=1 to a "
      "sum-circle => T'<=N/2; verified for every antipodal family (random, latitude-ring, Z^3 shell))")

# (2) THIN CLOSURE: K_floor <= T' <= N/2 <= 20 < K*=20.55 for admissible N<=n_pack => R_lead<1 (C_full)
Nmax_adm = math.floor(n_pack)                     # 40
Kf_loose = Nmax_adm/2.0                            # 20
R_loose = const*(1+Kf_loose)*I
claim("offdiag_Cfull_thin_closure_proved", Kf_loose <= Kstar and R_loose < 1.0,
      f"(K_floor<=T'<=N/2<=n_pack/2={Kf_loose:.0f}<{Kstar:.2f}=K*; R_lead<=23.2*(1+{Kf_loose:.0f})*2e-3={R_loose:.3f}<1 "
      f"(margin x{1/R_loose:.3f}). Off-diagonal for C_full (incl non-lattice) is PROVED via the antipodal lemma + "
      "R-025 + packing -- THIN (A_ext fallback), not a conjecture)")

# (3) ACTUAL K_floor ~ 1-3 across ALL families (EXT strong evidence; T' a loose proxy)
worst = max(Kf for _, _, Kf in S.values())
maxT = max(T for _, T, _ in S.values())
claim("actual_Kfloor_small_Tprime_loose", worst < 3.5 and maxT >= 10,
      f"(actual K_floor in [{min(Kf for *_,Kf in [(0,0,s[2]) for s in S.values()]):.2f},{worst:.2f}] across random/"
      f"latitude-ring/rich-shell; max T'={maxT} (=N/2 for rings) yet K_floor<={worst:.2f}: the L-infinity occupancy "
      "T' is a LOOSE proxy for the L-2 floor K_floor)")

# (4) EXT margin upgrade: actual K_floor ~3 => comfortable margin vs thin loose x1.026
R_actual = const*(1+worst)*I
claim("ext_is_margin_upgrade_not_blocker", R_actual < R_loose < 1.0,
      f"(EXT actual-floor margin: R_lead=23.2*(1+{worst:.2f})*2e-3={R_actual:.3f} (margin x{1/R_actual:.1f}) vs loose "
      f"fallback x{1/R_loose:.3f}. EXT (K_floor~3 maximal) UPGRADES the thin fallback to comfortable; it is NOT a "
      "closure blocker. Stays T2 (operator 2026-06-10: register, do not promote); tight L-2 bound = promotion path)")

# (5) quantitative sanity + EXT falsifier
sane = (Kstar > 20) and (worst < 13) and lemma_ok and (R_loose < 1)
claim("quantitative_sanity_ext", sane,
      f"(K*={Kstar:.2f}; actual max K_floor={worst:.2f}<13 (EXT bound, loose) <{Kstar:.1f}=K*; antipodal lemma holds; "
      "thin closure R_lead<1. EXT falsifier: an admissible Q with K_floor>13. Correction to res5_031 'lattice strictly "
      "worst' headline recorded -- actual extremal ~3 across all classes, T' loose proxy)")

ok = all(c["passed"] for c in CLAIMS)
out = REPO / "claims" / "B1-RH-ENUM" / "runs" / "260610-res5-033-ext-adversarial-map"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="res5_033_ext_adversarial_map.py", version=__version__,
    Kstar=Kstar, n_pack=n_pack, families={k: dict(N=v[0], Tprime=v[1], K_floor=v[2]) for k, v in S.items()},
    Kfloor_loose_bound=Kf_loose, R_lead_loose=R_loose, worst_actual_Kfloor=worst, R_lead_actual=R_actual,
    verdict=("Step 2: elementary antipodal lemma T'<=N/2 (proved) + R-025 (K_floor<=T') + packing (N<=40) => "
             "K_floor<=20<20.55=K* => R_lead<1 for C_full incl non-lattice (THIN x1.026, the A_ext fallback): the "
             "off-diagonal C_full closure is PROVED, not a conjecture. The actual K_floor~1-3 across all families "
             "(T' up to N/2=20 a loose proxy) => EXT (K_floor~3) is a MARGIN UPGRADE (x1.026->~x5), NOT a closure "
             "blocker; stays T2. Corrects res5_031 'lattice strictly worst' -> actual ~3 across all classes."),
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nantipodal lemma T'<=N/2 verified; thin closure R_lead<=%.3f<1 (C_full); actual K_floor<=%.2f (EXT comfort)" % (R_loose, worst))
print(f"claims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
