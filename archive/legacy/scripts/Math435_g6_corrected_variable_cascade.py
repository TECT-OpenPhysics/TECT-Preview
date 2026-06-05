#!/usr/bin/env python3
"""Math435_g6_corrected_variable_cascade.py -- G6 gate execution (CLAUDE.md 6.3.8).

G6 (opened by Math426): re-run everything that was computed in the WRONG
(offset) variable r = K(0) = mu2 + Y q0^4, using the production-corrected
Brazovskii shell mass r_braz = K(q0) = mu2 (Math426 code-anchored kernel
identity K(q) = mu2 + Y (q^2 - q0^2)^2).

THREE SUB-TASKS:

 (a) Corrected Math400-AddE sweep: the one-loop disordered gap equation
         r_R = r_bare + 3 u M(r_R) + 15 v M(r_R)^2
     over mu2 in [-1.0, +0.5] (16 points, same grid as the suspended AddE
     sweep) with the CORRECTED identification r_bare = mu2. The gap-equation
     machinery is reused VERBATIM from Math400_AddE_brazovskii_one_loop.py
     (full 20000-pt quadrature; solve_self_consistency unchanged). Key
     structural fact asserted below: the gap equation depends on (r_bare,
     u, v, q0, c) only, so the corrected sweep at mu2 = X probes the same
     physics as the old sweep at r_bare = X; the offset defect was purely a
     mislabeling of which mu2 maps to which r_bare.
     PRE-REGISTERED SIGN-FLIP GATE (Math426 S7 G6): fires iff any corrected
     row has root-count != 1 OR r_R <= 0 OR path != 'alpha'.

 (b) Corrected Math401 lexicon: closed-form re-evaluation at the certified
     Math426 corrected-canonical anchors r_R = 0.30452570866744433,
     M_R = 0.10941432918723439 (Runs/math/Math426/g4_kernel_reconciliation
     .json): sqrt(r_R), correlation length xi = 2 q0 sqrt(c / r_R)
     (DIMENSION-CORRECTED form; the AddE/Math401 written form
     sqrt(c/(4 r_R q0^2)) has dimension length^3, defect documented in
     Math435 S3), a_condensate = 2 pi / q0 (unchanged), M_R, and the
     hand-verifiable gap-equation identity
     r_braz + 3 u M_R + 15 v M_R^2 = r_R.

 (c) Math424-AddA corrected-window re-scan: the 7-point reading-comparison
     window {-0.5, -0.2, 0, +0.005, +0.1, +0.3, +0.5} with r_bare = mu2
     (production convention), using the Math424_AddA machinery verbatim
     (gap_solve / scan_reading / mf_threshold / dF identity). Boundaries:
     CS no-condensation boundary r* = u^2/(4v) = (43/180)^2 = 0.0570679...
     (production convention; old offset image -0.157); per-reading
     zero-phase MF thresholds r_c = J * r* with exact rational J.
     CROSS-CHECK (mandatory, dispatch): corrected canonical row must
     reproduce the Math426 certified r_R, M to <= 1e-6 RELATIVE (same
     pipeline: m424.gap_solve + M_fast).
     RESTORATION GATE: fires iff any reading at any corrected-window row
     has A* > 0 with dF < -1e-9 (fluctuation restoration fails).

EXECUTION STATUS / PROVENANCE: written 2026-06-04 by the G6 agent in a
file-tools-only session (no shell; Math434 precedent). FIRST EXECUTION is
the operator's / dispatcher's step; until then every sweep-row number in
TECT-Math435 S2/S4 marked PENDING-EXECUTION is estimator-grade only
(interpolation of the executed offset-variable table in its r_bare column).
All EXACT-ARITHMETIC claims (r*, J values, thresholds, discriminants,
lexicon closed forms, gap identity at the certified anchors) are asserted
here against hand-derived values and are independent of the sweep.

CHECKPOINTING (sandbox 45-s cap): sub-task (a) full-quadrature rows are
checkpointed one row at a time to Runs/math/Math435/sweep_checkpoint.json;
re-running the script resumes from the checkpoint. Sub-tasks (b), (c) are
cheap (M_fast interpolation pipeline) and run in one pass.

Exit 0 iff ALL asserts pass. JSON artefact:
Runs/math/Math435/g6_corrected_cascade.json
"""
import json, math, os, sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import Math400_AddE_brazovskii_one_loop as addE
import Math424_AddA_reading_uniqueness as m424

# ------------------------------------------------------------- constants
U, V, C, Q0 = -0.86, 3.24, 1.0, 0.6801747616
MU2_CANON = 0.005
Q0SQ = Q0 * Q0
Q0P4 = Q0SQ * Q0SQ                       # = 0.2140336473068255
RSTAR = U * U / (4.0 * V)                # = (43/180)^2 = 0.05706790123456790

# Math426 certified corrected-canonical anchors (executed ground truth,
# Runs/math/Math426/g4_kernel_reconciliation.json)
RR_426 = 0.30452570866744433
MR_426 = 0.10941432918723439

CLAIMS = []

def claim(name, expected, actual, tol):
    ok = abs(actual - expected) <= tol
    CLAIMS.append(dict(name=name, expected=expected, actual=actual,
                       tol=tol, passed=bool(ok)))
    assert ok, f"FAIL {name}: expected {expected} got {actual} (tol {tol})"

def claim_true(name, cond, detail=""):
    CLAIMS.append(dict(name=name, expected=True, actual=bool(cond),
                       tol=0, passed=bool(cond), detail=detail))
    assert cond, f"FAIL {name}: {detail}"

OUT_DIR = "Runs/math/Math435"
os.makedirs(OUT_DIR, exist_ok=True)
CKPT = os.path.join(OUT_DIR, "sweep_checkpoint.json")

# =====================================================================
# Sub-task (b) first: exact-arithmetic layer (no quadrature dependence)
# =====================================================================
print("=" * 76)
print(" Math435 G6 -- corrected-variable recomputation cascade")
print("=" * 76)

# kernel-identity bookkeeping (Math426 anchor reproduction)
claim("q0^4_offset", 0.2140336473068255, Q0P4, 1e-12)
claim("rstar_exact_rational_(43/180)^2", (43.0 / 180.0) ** 2, RSTAR, 1e-15)
claim("rstar_value", 0.05706790123456790, RSTAR, 1e-12)
claim_true("corrected_canonical_below_rstar_MF_condensation_allowed",
           MU2_CANON < RSTAR, f"mu2={MU2_CANON} < r*={RSTAR:.6f}")

# exact rational J per reading (J = N4^2 / (N2 N6), zero phases)
J_EXACT = dict(LAM=36.0 / 40.0, HEX=8100.0 / 12240.0,
               FCC=46656.0 / 64000.0, BCC=291600.0 / 506880.0)
claim("J_LAM_9/10", 0.9, J_EXACT["LAM"], 1e-15)
claim("J_HEX_45/68", 45.0 / 68.0, J_EXACT["HEX"], 1e-15)
claim("J_FCC_0.729", 0.729, J_EXACT["FCC"], 1e-15)
claim("J_BCC_405/704", 405.0 / 704.0, J_EXACT["BCC"], 1e-15)
# cross-check J against the Math424-AddA combinatorial enumeration
for nm in ("LAM", "HEX", "FCC", "BCC"):
    c = m424.COMB[nm]
    claim(f"J_{nm}_from_enumeration",
          J_EXACT[nm], c["N4"] ** 2 / (c["N2"] * c["N6"]), 1e-12)

# per-reading zero-phase MF condensation thresholds r_c = J r*
RC = {nm: J_EXACT[nm] * RSTAR for nm in J_EXACT}
claim("rc_LAM", 0.0513611, RC["LAM"], 1e-6)
claim("rc_HEX", 0.0377655, RC["HEX"], 1e-6)
claim("rc_FCC", 0.0416025, RC["FCC"], 1e-6)
claim("rc_BCC", 0.0328303, RC["BCC"], 1e-6)
claim_true("canonical_below_every_rc_all_readings_condense_MF",
           all(MU2_CANON < RC[nm] for nm in RC), f"{RC}")

# offset image of the CS boundary (Math425 historical -0.157)
claim("old_offset_image_of_rstar", -0.1569657, RSTAR - Q0P4, 1e-6)

# corrected-canonical MF discriminants (exact linear arithmetic; must
# reproduce the Math426 JSON values to all printed digits)
def disc(nm, r):
    c = m424.COMB[nm]
    return U * U * c["N4"] ** 2 - 8.0 * c["n"] * r * V * c["N6"]

claim("disc_LAM_canonical", 24.0336, disc("LAM", MU2_CANON), 1e-9)
claim("disc_HEX_canonical", 5197.608, disc("HEX", MU2_CANON), 1e-8)
claim("disc_FCC_canonical", 30359.5776, disc("FCC", MU2_CANON), 1e-7)
claim("disc_BCC_canonical", 182821.536, disc("BCC", MU2_CANON), 1e-6)

# ---- corrected Math401 lexicon (closed forms at certified anchors) ----
sqrt_rR_new = math.sqrt(RR_426)
sqrt_rR_old = math.sqrt(0.41925)
xi_new = 2.0 * Q0 * math.sqrt(C / RR_426)     # dimension-corrected form
xi_old = 2.0 * Q0 * math.sqrt(C / 0.41925)
xi_addE_form_old = math.sqrt(C / (4.0 * 0.41925 * Q0SQ))  # defective form
a_cond = 2.0 * math.pi / Q0

claim("lexicon_sqrt_rR_corrected", 0.551838, sqrt_rR_new, 2e-6)
claim("lexicon_sqrt_rR_old_offset", 0.647495, sqrt_rR_old, 2e-6)
claim("lexicon_xi_corrected_2q0_sqrt_c_over_rR", 2.46512, xi_new, 2e-5)
claim("lexicon_xi_old_offset_same_formula", 2.10094, xi_old, 2e-5)
claim("lexicon_xi_addE_written_form_value", 1.135306, xi_addE_form_old, 2e-5)
claim("lexicon_a_condensate_2pi_over_q0", 9.237604, a_cond, 2e-5)
claim("lexicon_M_R_corrected", 0.1094143, MR_426, 1e-6)
claim("lexicon_xi_over_a_corrected", 0.26686, xi_new / a_cond, 2e-5)

# hand-verifiable gap identity at the certified anchors:
#   r_braz + 3 u M_R + 15 v M_R^2 = r_R
shift_q = 3.0 * U * MR_426
shift_s = 15.0 * V * MR_426 * MR_426
claim("gap_identity_quartic_shift", -0.2822890, shift_q, 1e-6)
claim("gap_identity_sextic_shift", +0.5818146, shift_s, 1e-6)
claim("gap_identity_closes_at_anchors",
      RR_426, MU2_CANON + shift_q + shift_s, 5e-6)
claim("sextic_over_quartic_ratio_corrected", 2.0611,
      abs(shift_s / shift_q), 2e-4)
claim("rR_over_rbraz_corrected", 60.905, RR_426 / MU2_CANON, 2e-2)

print("[exact-arithmetic layer] all hand-derived claims PASS")

# =====================================================================
# Sub-task (c): Math424-AddA corrected-window re-scan (fast pipeline)
# =====================================================================
print("-" * 76)
print(" Sub-task (c): Math424-AddA corrected-window re-scan (r_bare = mu2)")
print("-" * 76)

WINDOW = [-0.5, -0.2, 0.0, MU2_CANON, 0.1, 0.3, 0.5]
window_out = []
restoration_ok = True
for mu2 in WINDOW:
    r_bare = mu2                              # PRODUCTION CONVENTION
    rR = m424.gap_solve(r_bare, 0, 0, 0.0)
    claim_true(f"window_disordered_gap_exists_mu2={mu2:+.3f}", rR is not None)
    MR = m424.M_fast(rR)
    v0, _ = m424.dF_reading(r_bare, "BCC", 0.0, rR, MR)
    claim(f"window_dF(A=0)_identity_mu2={mu2:+.3f}", 0.0, v0, 1e-9)
    entry = dict(mu2=mu2, r_bare=r_bare, r_R=rR, M_R=MR, readings={})
    for nm in ("LAM", "HEX", "FCC", "BCC"):
        (dF, Astar, rh), rows = m424.scan_reading(r_bare, nm, rR, MR)
        mf = m424.mf_threshold(nm, r_bare)
        # discriminant sign must match the exact-arithmetic prediction
        claim_true(f"window_disc_sign_{nm}_mu2={mu2:+.3f}",
                   (mf > 0) == (r_bare < RC[nm]),
                   f"disc={mf:+.3e} vs r_c={RC[nm]:.5f}")
        entry["readings"][nm] = dict(dF_min=dF, A_star=Astar, r_hat=rh,
                                     mf_discriminant=mf)
        if Astar > 0 and dF < -1e-9:
            restoration_ok = False
        print(f"  mu2={mu2:+.3f} {nm}: disc={mf:+.3e}  A*={Astar:.4f}  "
              f"dF={dF:+.3e}")
    window_out.append(entry)

# MANDATORY dispatch cross-check: corrected canonical reproduces Math426
can = [e for e in window_out if e["mu2"] == MU2_CANON][0]
claim_true("CROSSCHECK_canonical_rR_vs_Math426_1e-6_relative",
           abs(can["r_R"] - RR_426) / RR_426 <= 1e-6,
           f"r_R={can['r_R']!r} vs {RR_426!r}")
claim_true("CROSSCHECK_canonical_MR_vs_Math426_1e-6_relative",
           abs(can["M_R"] - MR_426) / MR_426 <= 1e-6,
           f"M_R={can['M_R']!r} vs {MR_426!r}")

# pre-registered RESTORATION GATE
claim_true("RESTORATION_GATE_all_window_rows_Astar_zero",
           restoration_ok,
           "fluctuation restoration must hold at every corrected-window row")

print("[sub-task (c)] corrected-window scan complete; restoration gate "
      + ("PASS" if restoration_ok else "FIRED"))

# =====================================================================
# Sub-task (a): corrected AddE sweep (full 20000-pt quadrature, AddE
# machinery verbatim), checkpointed per row for the sandbox 45-s cap.
# =====================================================================
print("-" * 76)
print(" Sub-task (a): corrected Math400-AddE sweep, r_bare = mu2,")
print("               mu2 in [-1.0, +0.5], 16 points (resumable)")
print("-" * 76)

MU2_GRID = [round(-1.0 + 0.1 * i, 10) for i in range(16)]
# include canonical as a 17th tagged row for the executed-anchor record
MU2_GRID_FULL = MU2_GRID + [MU2_CANON]

ckpt = {}
if os.path.exists(CKPT):
    try:
        ckpt = json.load(open(CKPT))
    except Exception:
        ckpt = {}

sweep_rows = []
for mu2 in MU2_GRID_FULL:
    key = f"{mu2:+.6f}"
    if key in ckpt:
        res = ckpt[key]
        print(f"  [ckpt] mu2={mu2:+.4f}  resumed")
    else:
        r_bare = mu2                          # PRODUCTION CONVENTION
        res_full = addE.solve_self_consistency(
            r_bare, U, V, Q0, C, use_shell=False, verbose=False)
        res = dict(mu2=mu2, r_bare=r_bare,
                   n_roots=len(res_full["roots"]),
                   path=res_full["path"],
                   roots=res_full["roots"])
        ckpt[key] = res
        json.dump(ckpt, open(CKPT, "w"), indent=1)
        rr = res["roots"][0]["r_R"] if res["roots"] else float("nan")
        mm = res["roots"][0]["M"] if res["roots"] else float("nan")
        print(f"  mu2={mu2:+.4f}  r_R={rr:+.6f}  M={mm:.6f}  "
              f"path={res['path']}  roots={res['n_roots']}")
    sweep_rows.append(res)

# ---- pre-registered SIGN-FLIP GATE (Math426 S7 G6) ----
sign_flip_fired = False
flip_detail = []
for res in sweep_rows:
    ok = (res["n_roots"] == 1 and res["path"] == "alpha"
          and res["roots"][0]["r_R"] > 0)
    if not ok:
        sign_flip_fired = True
        flip_detail.append(res["mu2"])
    claim_true(f"sweep_path_alpha_unique_root_mu2={res['mu2']:+.4f}",
               ok, f"path={res['path']} roots={res['n_roots']}")

claim_true("SIGN_FLIP_GATE_not_fired", not sign_flip_fired,
           f"fired at mu2={flip_detail}" if flip_detail else "")

# monotonicity sanity (CLAUDE.md 6.3.4): r_R increases with mu2
rRs = [r["roots"][0]["r_R"] for r in sweep_rows[:16] if r["roots"]]
claim_true("sweep_rR_monotone_increasing",
           all(b > a for a, b in zip(rRs, rRs[1:])), f"{rRs}")

# the corrected sweep canonical row (full 20000-pt pipeline) must agree
# with the M_fast-pipeline anchor within the known pipeline delta 2e-3
can_sw = sweep_rows[-1]
claim("sweep_canonical_rR_vs_Math426_pipeline_delta",
      RR_426, can_sw["roots"][0]["r_R"], 2e-3)

# structural identity: the corrected row at mu2 = X equals the OLD AddE
# sweep at r_bare = X. Verify on one overlap point: old row mu2_old = -0.2
# had r_bare = -0.186 +- (q0^4 rounding) ... exact overlap point:
# old mu2_old = -0.2 gives r_bare_old = -0.2 + q0^4 = +0.0140336473;
# corrected row at mu2 = +0.0140336473 must reproduce the old published
# r_R = +0.3086 (offset-table row) within quadrature reproducibility.
res_overlap = addE.solve_self_consistency(
    -0.2 + Q0P4, U, V, Q0, C, use_shell=False, verbose=False)
claim("relabeling_identity_old_row_-0.2_reproduced",
      0.3086, res_overlap["roots"][0]["r_R"], 5e-4)

print("[sub-task (a)] corrected sweep complete; sign-flip gate "
      + ("FIRED" if sign_flip_fired else "PASS"))

# =====================================================================
# JSON artefact
# =====================================================================
out = dict(
    theory_tag="Math435", date="2026-06-04",
    constants=dict(u=U, v=V, c=C, q0=Q0, q0p4=Q0P4, mu2_canonical=MU2_CANON,
                   rstar=RSTAR, rc_per_reading=RC, J_exact=J_EXACT),
    anchors_Math426=dict(r_R=RR_426, M_R=MR_426),
    lexicon_corrected=dict(
        sqrt_rR=dict(old_offset=sqrt_rR_old, corrected=sqrt_rR_new),
        xi_2q0_sqrt_c_over_rR=dict(old_offset=xi_old, corrected=xi_new,
                                   addE_written_form_old=xi_addE_form_old),
        a_condensate=a_cond,
        M_R=dict(old_offset=0.0960, corrected=MR_426),
        r_R=dict(old_offset=0.41925, corrected=RR_426),
        bare_mass=dict(old_offset_K0=0.2190336473068255,
                       corrected_Kq0=MU2_CANON),
        gap_identity=dict(quartic_shift=shift_q, sextic_shift=shift_s,
                          closes_to=MU2_CANON + shift_q + shift_s)),
    corrected_window=window_out,
    corrected_sweep=sweep_rows,
    gates=dict(sign_flip_fired=sign_flip_fired,
               restoration_fired=not restoration_ok),
    claims=CLAIMS)
json.dump(out, open(os.path.join(OUT_DIR, "g6_corrected_cascade.json"), "w"),
          indent=1)

npass = sum(1 for c in CLAIMS if c["passed"])
print("=" * 76)
print(f" claims: {npass}/{len(CLAIMS)} PASS")
print(f" JSON: {OUT_DIR}/g6_corrected_cascade.json")
print(f" gates: sign-flip {'FIRED' if sign_flip_fired else 'pass'}; "
      f"restoration {'FIRED' if not restoration_ok else 'pass'}")
sys.exit(0)
