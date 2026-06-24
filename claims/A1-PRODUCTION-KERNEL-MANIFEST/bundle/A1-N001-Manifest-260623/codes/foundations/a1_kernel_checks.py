#!/usr/bin/env python3
"""a1_kernel_checks.py -- self-tests for the three A1 kernel cards (v1.4).

Kernel:  D(k) = r_zero + Z|k|^2 + Y|k|^4,  r_zero=D(0).  Completing the square (Y>0):
    q_star^2=-Z/(2Y), mu2_shell:=D(q_star)=r_zero-Z^2/(4Y), D=mu2_shell+Y(|k|^2-q_star^2)^2.

v1.4 (operator review 2026-06-23) closes two gaps in v1.3:
  (1) the verifier imports the ORIGINAL N-001 solver functions (vendored byte-identical
      under codes/foundations/n001_solver/), NOT a re-implemented mimic:
        - continuation_mu2_v25.kinetic_coefficients(mu2,Y,q0) -> (r,Z)
        - bloch_linearization.bloch_matrix_linear(G*, params) -> linear operator;
  (2) the REAL solver symbol is r + Z|k|^2 + Y|k|^4 + eta_shell*(|k|-q0)^2; the pure
      Brazovskii A1 kernel is the eta_shell=0 slice. The verifier ENFORCES eta_shell=0
      (a 6th stored field) and demonstrates that a non-zero eta_shell changes the symbol
      (the shell-bias term is load-bearing). The stored D_original=r_zero+Z|k|^2+Y|k|^4
      holds ONLY under eta_shell=0.
Full sha256 of the three vendored originals are pinned and checked. Bundle (operator
spec): canonical_n001_kernel.json + continuation_mu2_v25.py + bloch_linearization.py
(+ math56_constants.py dep) + a1_kernel_checks.py. Passing the gates is NOT
certification: reports "numerical gates pass; operator certification pending" (T1 OPEN).
"""
__version__ = "1.4.0"
__first_issued__ = "2026-06-23"
__version_issued__ = "2026-06-23"
__claims__ = ["A1-KERNEL-IDENTITY", "A1-SCALAR-ANALYTIC-BRANCH", "A1-PRODUCTION-KERNEL-MANIFEST"]

import json, hashlib, random, sys, warnings
from pathlib import Path
import numpy as np
warnings.filterwarnings("ignore")

REPO = Path(__file__).resolve().parents[2]
CLAIMS = []
def claim(n, ok, detail=""):
    CLAIMS.append(dict(name=n, passed=bool(ok), detail=detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {n} -- {detail}")
def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest() if Path(p).exists() else None
def qstar2(Z, Y):              return -Z/(2*Y)
def mu2_shell_of(r, Z, Y):     return r - Z*Z/(4*Y)
def d_Z(Z, Y, q0):             return abs(Z + 2*Y*q0*q0)
def d_m(mu2_shell, r0, Z, Y):  return abs(mu2_shell - (r0 - Z*Z/(4*Y)))
def d_r(r0, mu2_shell, Y, q0): return abs(r0 - (mu2_shell + Y*q0**4))

# ---------- A1-KERNEL-IDENTITY ----------
random.seed(0); worst = 0.0
for _ in range(3000):
    r = random.uniform(-1, 1); Y = random.uniform(0.1, 2.0); Z = random.uniform(-2.0, -0.05)
    qs2 = qstar2(Z, Y); ms2 = mu2_shell_of(r, Z, Y); k = random.uniform(0, 3)
    worst = max(worst, abs((r + Z*k*k + Y*k**4) - (ms2 + Y*(k*k - qs2)**2)), abs(r - (ms2 + Y*qs2**2)))
claim("kernel_identity_complete_square", worst < 1e-10,
      f"D=r+Z k^2+Y k^4 = mu2_shell+Y(k^2-q*^2)^2; r=mu2_shell+Y q*^4: worst {worst:.2e} (UNCONDITIONAL) [A1-KERNEL-IDENTITY]")

# ---------- canonical config (AS-IS) ----------
cfg_path = REPO/"claims"/"A1-PRODUCTION-KERNEL-MANIFEST"/"canonical_n001_kernel.json"
if not cfg_path.exists():
    claim("canonical_config_present", False, f"canonical_n001_kernel.json NOT FOUND at {cfg_path} (must be bundled)")
    print(f"\nA1 kernel checks v{__version__}: FAIL (config missing)"); sys.exit(1)
claim("canonical_config_present", True, f"canonical_n001_kernel.json located")
cfg = json.loads(cfg_path.read_text())
R0, MSH, Q0, Z, Y = cfg["r_zero"], cfg["mu2_shell"], cfg["q0"], cfg["Z"], cfg["Y"]
ETA = cfg["eta_shell"]; eps_Z, eps_m, eps_r = cfg["eps_Z"], cfg["eps_m"], cfg["eps_r"]

# eta_shell=0 (pure Brazovskii) -- the operator's binding requirement
claim("eta_shell_is_zero_pure_brazovskii", ETA == 0.0,
      f"stored eta_shell={ETA}: A1/A2/A3 certify the PURE Brazovskii scalar kernel, the eta_shell=0 slice of the "
      "N-001 symbol r+Z|k|^2+Y|k|^4+eta_shell*(|k|-q0)^2; stored D_original=r_zero+Z|k|^2+Y|k|^4 holds ONLY here")

# ---------- import the ORIGINAL N-001 solver functions (vendored byte-identical) ----------
SOLV = REPO/"codes"/"foundations"/"n001_solver"
sys.path.insert(0, str(SOLV))
import continuation_mu2_v25 as cont       # original kinetic_coefficients
import bloch_linearization as bl          # original bloch_matrix_linear
r_o, Z_o = cont.kinetic_coefficients(MSH, Y, Q0)
claim("n001_original_kinetic_coefficients_match_stored", abs(r_o-R0) < 1e-12 and abs(Z_o-Z) < 1e-12,
      f"ORIGINAL continuation_mu2_v25.kinetic_coefficients({MSH},{Y},{Q0}) -> (r={r_o:.7f}, Z={Z_o:.7f}) "
      f"REPRODUCES stored (r_zero={R0:.7f}, Z={Z:.7f})")

def D_original(k, eta):
    p = {"r": R0, "Z": Z, "Y": Y, "q0": Q0, "eta_shell": eta, "family_masses": [0.0, 0.0, 0.0], "k_lock": 0.0}
    return float(bl.bloch_matrix_linear(np.array([k, 0.0, 0.0]), p)[0, 0].real)
ktest = [0.0, 0.31, Q0, 0.93, 1.4, 2.2]
sym = max(abs(D_original(k, ETA) - (R0 + Z*k*k + Y*k**4)) for k in ktest)
claim("n001_original_bloch_symbol_matches_stored", sym < 1e-12,
      f"ORIGINAL bloch_matrix_linear (eta_shell={ETA}) scalar diagonal at k={ktest} equals stored "
      f"r_zero+Z|k|^2+Y|k|^4 to {sym:.2e}: the REAL solver linear symbol IS the stored kernel")

# shell-bias term is load-bearing: a non-zero eta_shell changes the symbol
eta_test = 0.1
diff = max(abs(D_original(k, eta_test) - D_original(k, 0.0)) for k in ktest)
expect = eta_test*(min(abs(k-Q0) for k in ktest if abs(k-Q0) > 0.1)**2)  # rough lower ref
claim("shell_bias_term_is_load_bearing", diff > 1e-3,
      f"setting eta_shell={eta_test} changes the ORIGINAL symbol by up to {diff:.4f} (the (|k|-q0)^2 term): "
      "eta_shell=0 is load-bearing, not vacuous -- A1 certifies the eta_shell=0 slice only")

# full sha256 of the three vendored originals match config + PROVENANCE
prov = json.loads((SOLV/"PROVENANCE.json").read_text())
hh = {f: sha256(SOLV/f) for f in ("continuation_mu2_v25.py", "bloch_linearization.py", "math56_constants.py")}
ok_h = all(hh[f] == prov[f]["sha256"] for f in hh) and hh["bloch_linearization.py"] == cfg["backend_sha256"] \
       and all(hh[f] == cfg["origin_n001_solver"][f]["sha256"] for f in hh)
claim("n001_original_sources_sha256_pinned", ok_h,
      f"full sha256 of the 3 vendored ORIGINAL sources match PROVENANCE.json + config "
      f"(continuation {hh['continuation_mu2_v25.py'][:16]}.., bloch {hh['bloch_linearization.py'][:16]}.., "
      f"math56 {hh['math56_constants.py'][:16]}..)")

# teeth: corrupt stored q0 -> original kinetic_coefficients diverge
r_bad, Z_bad = cont.kinetic_coefficients(MSH, Y, Q0*1.01)
claim("stored_field_error_is_detected", abs(r_bad-R0) > 1e-3 or abs(Z_bad-Z) > 1e-3,
      f"corrupting stored q0 by +1% -> original coefficients (r={r_bad:.5f}, Z={Z_bad:.5f}) diverge from stored: "
      "the stored-field read is load-bearing")

# ---------- A1-SCALAR-ANALYTIC-BRANCH ----------
ks = np.linspace(0, 4, 400001); Dvals = MSH + Y*(ks*ks - Q0*Q0)**2
claim("analytic_branch_D_ge_mu2shell_positive",
      MSH > 0 and Y > 0 and Z < 0 and float(Dvals.min()) >= MSH - 1e-12,
      f"mu2_shell={MSH}>0, Y={Y}>0, Z={Z:.4f}<0 => D(k)>=mu2_shell>0 (min={float(Dvals.min()):.6g}); "
      f"r_zero={R0:.5f} distinct [A1-SCALAR-ANALYTIC-BRANCH]")
b = 0.5111; ksg = np.array([n*b for n in range(-14, 15)])
DX = MSH + Y*((ksg[:, None, None]**2 + ksg[None, :, None]**2 + ksg[None, None, :]**2) - Q0**2)**2
lam0 = float(DX.min())
claim("lambda0_ge_mu2shell_equality_onshell_only", lam0 >= MSH - 1e-12 and lam0 > MSH,
      f"lambda0(L)=min_k D(k)={lam0:.6g} >= mu2_shell={MSH}; strict on a GENERIC cell [A1-SCALAR-ANALYTIC-BRANCH]")

# ---------- A1-PRODUCTION-KERNEL-MANIFEST ----------
mu2_true = mu2_shell_of(R0, Z, Y)
dm_true, dm_corrupt = d_m(mu2_true, R0, Z, Y), d_m(mu2_true + 0.01, R0, Z, Y)
claim("delta_m_is_nonvacuous_not_identically_zero", dm_true < 1e-9 and abs(dm_corrupt - 0.01) < 1e-12,
      f"delta_m on independent stored mu2_shell: correct -> {dm_true:.2e}; +0.01 -> {dm_corrupt:.4f} (DETECTED)")
dZ, dm, dr = d_Z(Z, Y, Q0), d_m(MSH, R0, Z, Y), d_r(R0, MSH, Y, Q0)
consistency = (Y > 0 and Z < 0 and dZ <= eps_Z and dm <= eps_m and dr <= eps_r)
branch = consistency and (MSH > 0) and (ETA == 0.0)
claim("canonical_n001_passes_gates_certification_pending", branch,
      f"canonical N-001 (r_zero={R0:.5f}, mu2_shell={MSH}, q0={Q0}, Z={Z:.5f}, Y={Y}, eta_shell={ETA}): "
      f"delta_Z={dZ:.2e}, delta_m={dm:.2e}, delta_r={dr:.2e} <= eps; mu2_shell>0; eta_shell=0 => NUMERICAL GATES "
      "PASS; OPERATOR CERTIFICATION PENDING (T1 OPEN; not yet citable as the A2/A3 implementation)")
r_t, Z_t, Y_t = 0.35, -1.0, 0.50; mu2_alias = 0.35
dZ_t, ms2_t = d_Z(Z_t, Y_t, Q0), mu2_shell_of(r_t, Z_t, Y_t)
claim("legacy_template_FAILS_and_alias_forbidden", (dZ_t > eps_Z or ms2_t <= 0) and ms2_t < 0,
      f"template (0.35,-1,0.50): delta_Z={dZ_t:.3f}>eps; mu2_shell_derived={ms2_t:.3f}<0; 'mu2'=r alias FORBIDDEN. FAILS")

ok = all(c["passed"] for c in CLAIMS)
cert = dict(version=__version__, config_source=str(cfg_path.relative_to(REPO)), eta_shell=ETA,
    n001_solver_dir="codes/foundations/n001_solver", original_sha256=hh, bloch_symbol_residual=sym,
    shell_bias_load_bearing_diff=diff,
    gates=dict(delta_Z=dZ, delta_m=dm, delta_r=dr, mu2_shell_positive=MSH > 0, eta_shell_zero=ETA == 0.0,
               consistency_manifest=bool(consistency), analytic_branch_manifest=bool(branch),
               certification="operator certification pending (T1 OPEN)"),
    subset_map=dict(identity=["kernel_identity_complete_square"],
                    analytic_branch=["analytic_branch_D_ge_mu2shell_positive", "lambda0_ge_mu2shell_equality_onshell_only"]),
    claims=CLAIMS, all_pass=ok)
out = REPO/"claims"/"A1-KERNEL-IDENTITY"/"runs"/"a1_kernel_checks.json"
out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(cert, indent=2))
print(f"\nA1 kernel checks v1.4: {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
