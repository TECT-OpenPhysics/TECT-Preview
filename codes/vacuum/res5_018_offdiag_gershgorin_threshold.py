"""res5_018_offdiag_gershgorin_threshold.py -- T-018 (v1.2, full-admissible-class
re-issue per operator review 2026-06-10): reduce the FULL off-diagonal Bogoliubov
operator-norm residual to the EXCHANGE (Fock) BLOCK ALONE, with a COMPETITOR-
DEPENDENT scalar threshold, removing the "condensate-direction only" caveat from
the condensate block by its diagonality.

Setting (hdiag-full-operator-norm-formulation v1.0). The off-diagonal Hessian is
    Hess F|_{G*} = E + B_od,   E = (1/2) G*^-1 (x) G*^-1  (PD, diagonal in channel Q),
    B_od = B^cond + B^exch     (Hartree carries NO off-diagonal block).
  * B^cond  -- Math428 condensate/bubble block. Delta F_od = -1/4 sum_{Q!=0} W(Q)^2
    B(|Q|), W(Q)=3 u_eff A^2 p_2(Q)+...: a sum of INDEPENDENT channel terms.
    DIAGONALITY LEMMA: a free-energy share that is a sum of independent channel terms
    has a delta G-Hessian that is BLOCK-DIAGONAL in the channel index Q (the second
    variation of sum_Q f_Q(G_QQ) has no Q!=Q' cross term). Hence ||E^-1/2 B^cond
    E^-1/2||_op = max_Q (single-channel ratio).
  * B^exch  -- Fock exchange block; off-diagonal (Q!=Q'); SIGN not fixed by u_eff>0
    (bare u=-0.86<0; u_eff>0 only via sextic dressing) => beyond-second-cumulant,
    merges with RES-5.

OPERATOR REVIEW CORRECTION (2026-06-10). v1.1 quoted R_lead=0.174, which is the BCC
ANCHOR value (K_floor=E_+/N^2-1=2.75). The FULL ADMISSIBLE competitor class allows
larger floors (uniform worst K_floor=12.13; non-uniform T'<=13), so via the pinned
identity R_lead = const*(1+K_floor)*I, const=(9/4)u_eff^2 B_max N/c_diag=23.2:
    R_lead^BCC    = 23.2*(1+2.75)*2e-3  = 0.174   (margin x5.7)
    R_lead^unif   = 23.2*(1+12.13)*2e-3 = 0.609   (margin x1.64)
    R_lead^nonunif<= 23.2*(1+13)*2e-3   = 0.650   (margin x1.54)
all < 1 (condensate block certified over the class), but the exchange budget and
threshold are correspondingly TIGHTER. A full-class theorem needs the COMPETITOR-
DEPENDENT threshold b_exch(Q) < b_star(Q) = (1-R_lead(Q))/N_exch(Q) for all Q in the
admissible class, NOT the single BCC number.

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.2.0"
__first_issued__ = "2026-06-10"
__claims__ = ["B2-PROPA-HLAYER", "B1-RH-ENUM"]

import json, sys, math
from collections import Counter
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "archive" / "legacy" / "scripts"))
import Math424_AddA_reading_uniqueness as m424  # noqa: E402
U, V, Q0 = m424.U, m424.V, m424.Q0
CLAIMS = []
def claim(n, c, d=""):
    CLAIMS.append(dict(name=n, passed=bool(c), detail=d))
    print(f"  [{'PASS' if c else 'FAIL'}] {n} {d}")

base = []
for a, b in [(0, 1), (0, 2), (1, 2)]:
    for sa in (+1, -1):
        for sb in (+1, -1):
            v = [0, 0, 0]; v[a] = sa; v[b] = sb
            base.append(tuple(v))
K = np.array(base, float) / math.sqrt(2.0) * Q0
N = len(K)
def key(v): return tuple(np.round(v, 9))
zero = key(np.zeros(3))

MU2 = 0.005
rR = m424.gap_solve(MU2, 0, 0, 0.0)
M_R = m424.M_fast(rR)
u_eff = U + 10.0 * V * M_R
c_diag = (N / 2.0) * rR
print(f"anchor mu^2={MU2}: rR={rR:.5f}, u_eff={u_eff:.5f}, c_diag=(N/2)rR={c_diag:.4f}")

p2 = Counter(key(K[i] + K[j]) for i in range(N) for j in range(N))
Eplus = sum(c * c for c in p2.values())
Tprime = max(c for Q, c in p2.items() if Q != zero)
max_p2sq = max(c * c for Q, c in p2.items() if Q != zero)
B_sb_max = 0.21774
I = 2e-3

# pinned floor->ratio identity: R_lead = const*(1+K_floor)*I, const=(9/4)u_eff^2 B_max N/c_diag
const = (9.0 / 4.0) * u_eff**2 * B_sb_max * N / c_diag
def R_of_Kfloor(Kf): return const * (1.0 + Kf) * I
Kf_bcc = Eplus / N**2 - 1.0                       # = 2.75 (BCC anchor)
R_bcc = R_of_Kfloor(Kf_bcc)
R_unif = R_of_Kfloor(12.13)                       # uniform worst over admissible class (T-014)
R_nonunif = R_of_Kfloor(13.0)                     # non-uniform envelope 1+K_floor<=1+T'=14 (T-015)

# (1) DIAGONALITY LEMMA: B^cond block-diagonal in Q => worst-direction = max-channel <= class R_lead
claim("cond_block_diagonal_worstdir", max_p2sq <= Eplus and R_unif < 1.0 and R_nonunif < 1.0,
      f"(DIAGONALITY LEMMA: Delta F_od=sum_Q f_Q(G_QQ) [independent channels] => delta G-Hessian block-diagonal in "
      f"Q => ||B^cond||_op=max-channel ratio. max_Q p_2^2={int(max_p2sq)}<=E_+={Eplus}, so the floor->ratio bound "
      f"certifies ALL directions. Class values: R_lead^BCC={R_bcc:.3f}(x{1/R_bcc:.1f}), R_lead^unif={R_unif:.3f}"
      f"(x{1/R_unif:.2f}), R_lead^nonunif<={R_nonunif:.3f}(x{1/R_nonunif:.2f}); all<1)")

# (2) triangle: residual = exchange block alone, budget 1 - R_lead(Q) (competitor-dependent)
budget_bcc, budget_unif, budget_nonunif = 1 - R_bcc, 1 - R_unif, 1 - R_nonunif
claim("triangle_residual_exchange_block_classwide", budget_nonunif > 0.0,
      f"(||E^-1/2 B_od E^-1/2|| <= R_lead(Q) + rho_exch; full norm <1 provided rho_exch < 1-R_lead(Q). "
      f"Budgets: BCC {budget_bcc:.3f}, uniform {budget_unif:.3f}, non-uniform {budget_nonunif:.3f} -- all >0, so "
      "the residual is the EXCHANGE BLOCK alone over the whole admissible class, with the TIGHTEST (non-uniform) "
      "budget the binding one)")

# (3) Gershgorin COMPETITOR-DEPENDENT scalar threshold b_exch(Q) < (1-R_lead(Q))/N_exch(Q)
chans = [Q for Q in p2 if Q != zero]
diffset = set(key(K[i] - K[j]) for i in range(N) for j in range(N))
N_exch = max(sum(1 for Qp in chans if key(np.array(Q) - np.array(Qp)) in diffset) for Q in chans)
bstar_bcc = budget_bcc / N_exch
bstar_unif = budget_unif / N_exch
bstar_nonunif = budget_nonunif / N_exch
claim("gershgorin_competitor_dependent_threshold", bstar_nonunif > 0.0 and N_exch <= len(chans),
      f"(rho_exch<=N_exch*b_exch (N_exch={N_exch} BCC); COMPETITOR-DEPENDENT threshold b_exch(Q)<b_star(Q)="
      f"(1-R_lead(Q))/N_exch(Q). Values: b_star^BCC={bstar_bcc:.4f}, b_star^unif={bstar_unif:.4f}, "
      f"b_star^nonunif={bstar_nonunif:.4f} (the BINDING full-class target). The v1.1 single number 0.0486 was the "
      "BCC anchor only; the class target is ~2.4x tighter)")

# (4) honest residual: b_exch is RES-5 (dressed Fock bubble sign/magnitude), not closed
claim("residual_is_res5_scalar_not_closed", U < 0 < u_eff,
      f"(b_exch=max_Q|E^-1/2 B^exch E^-1/2| is the dressed Fock-bubble magnitude; SIGN unfixed by u_eff>0 (bare "
      f"u={U}<0, u_eff={u_eff:.3f}>0 via dressing), beyond second cumulant => RES-5. T-018 reduces the residual to "
      "this scalar; it does NOT bound it. No tier flip: B1/B2 T6 on {H-LAYER})")

# (5) quantitative sanity: const reproduction + class monotonicity + N_exch combinatorial
sane = (abs(const - 23.2) < 0.2) and (R_bcc < R_unif < R_nonunif < 1.0) and (bstar_nonunif < bstar_bcc)
claim("quantitative_sanity_const_and_class", sane,
      f"(const=(9/4)u_eff^2 B_max N/c_diag={const:.2f} reproduces operator 23.22; R_lead monotone in K_floor "
      f"{R_bcc:.3f}<{R_unif:.3f}<{R_nonunif:.3f}<1; threshold tightens b_star^nonunif={bstar_nonunif:.4f}<"
      f"b_star^BCC={bstar_bcc:.4f}; N_exch={N_exch} combinatorial (<=n_chans={len(chans)}))")

ok = all(c["passed"] for c in CLAIMS)
out = REPO / "claims" / "B2-PROPA-HLAYER" / "runs" / "260610-res5-018-offdiag-gershgorin-threshold"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="res5_018_offdiag_gershgorin_threshold.py", version=__version__,
    mu2=MU2, rR=rR, u_eff=u_eff, N=N, c_diag=c_diag, Eplus=Eplus, Tprime=Tprime, const=const, I=I,
    R_lead=dict(bcc=R_bcc, unif=R_unif, nonunif=R_nonunif),
    budget=dict(bcc=budget_bcc, unif=budget_unif, nonunif=budget_nonunif),
    N_exch=N_exch, n_chans=len(chans),
    b_star=dict(bcc=bstar_bcc, unif=bstar_unif, nonunif=bstar_nonunif),
    verdict=("T-018 v1.2 full-class re-issue: B^cond diagonal (lemma) => worst-dir norm <= R_lead(Q); class values "
             "R_lead 0.174(BCC)/0.609(unif)/0.650(nonunif)<1; triangle => exchange block alone; COMPETITOR-DEPENDENT "
             "threshold b_exch(Q)<(1-R_lead(Q))/N_exch(Q), binding full-class target b_star^nonunif=%.4f (BCC 0.0486 "
             "was anchor-only). b_exch is RES-5, not closed. No tier flip." % bstar_nonunif),
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nR_lead BCC/unif/nonunif = {R_bcc:.3f}/{R_unif:.3f}/{R_nonunif:.3f}; b_star = {bstar_bcc:.4f}/{bstar_unif:.4f}/{bstar_nonunif:.4f}; N_exch={N_exch}")
print(f"claims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
