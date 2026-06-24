#!/usr/bin/env python3
"""a1_kernel_checks.py -- self-tests for the three A1 kernel cards (v1.5).

Kernel:  D(k) = r_zero + Z|k|^2 + Y|k|^4,  r_zero=D(0).  Completing the square (Y>0):
    q_star^2=-Z/(2Y), mu2_shell:=D(q_star)=r_zero-Z^2/(4Y), D=mu2_shell+Y(|k|^2-q_star^2)^2.

v1.5 (operator review 2026-06-23) closes the v1.4 gaps:
  (1) the verifier asserts the config SCHEMA is complete BEFORE using it (a stale/v1.2
      config fails a NAMED claim, not a raw KeyError);
  (2) the original bloch_matrix_linear scalar diagonal depends on MORE than eta_shell:
      laplacian_mode, bcc_mix_epsilon, a_bcc, family_masses, k_lock (function DEFAULT
      0.15), eta_shell. v1.4 hardcoded family_masses=[0,0,0], k_lock=0; v1.5 reads the
      FULL scalar-slice param set from canonical_n001_kernel.json["scalar_slice"] and
      passes it verbatim to the ORIGINAL function, so the verified symbol IS the runtime
      symbol. Each setting is shown load-bearing (k_lock=0.15 shifts the diagonal by 0.1,
      eta_shell=0.1 adds shell-bias, mixed_bcc changes s2).
The three original solver sources are vendored byte-identical under n001_solver/ with full
sha256 pinned + checked. Bundle: canonical_n001_kernel.json + the 3 sources + this checker.
Passing the gates is NOT certification: reports "gates pass; certification pending" (T1 OPEN).
"""
__version__ = "1.5.0"
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

# ---------- config present + SCHEMA complete (no raw KeyError) ----------
cfg_path = REPO/"claims"/"A1-PRODUCTION-KERNEL-MANIFEST"/"canonical_n001_kernel.json"
if not cfg_path.exists():
    claim("canonical_config_present", False, f"canonical_n001_kernel.json NOT FOUND at {cfg_path} (must be bundled)")
    print(f"\nA1 kernel checks v{__version__}: FAIL (config missing)"); sys.exit(1)
claim("canonical_config_present", True, "canonical_n001_kernel.json located")
cfg = json.loads(cfg_path.read_text())
req_top = ["r_zero", "mu2_shell", "q0", "Z", "Y", "eta_shell", "eps_Z", "eps_m", "eps_r",
           "scalar_slice", "origin_n001_solver", "backend_sha256"]
req_slice = ["laplacian_mode", "bcc_mix_epsilon", "a_bcc", "family_masses", "k_lock", "z0", "eta_shell"]
missing = [k for k in req_top if k not in cfg] + \
          ([f"scalar_slice.{k}" for k in req_slice if k not in cfg.get("scalar_slice", {})] if "scalar_slice" in cfg else [])
claim("config_schema_v15_complete", not missing,
      f"config has all required keys {req_top} + scalar_slice{req_slice}" if not missing
      else f"STALE/INCOMPLETE config -- missing keys: {missing} (this is NOT a v1.5 canonical_n001_kernel.json)")
if missing:
    print(f"\nA1 kernel checks v{__version__}: FAIL (config schema incomplete)"); sys.exit(1)

R0, MSH, Q0, Z, Y = cfg["r_zero"], cfg["mu2_shell"], cfg["q0"], cfg["Z"], cfg["Y"]
ETA = cfg["eta_shell"]; eps_Z, eps_m, eps_r = cfg["eps_Z"], cfg["eps_m"], cfg["eps_r"]
SLICE = cfg["scalar_slice"]

claim("eta_shell_is_zero_pure_brazovskii", ETA == 0.0 and SLICE["eta_shell"] == 0.0,
      f"eta_shell={ETA}: A1/A2/A3 certify the PURE Brazovskii scalar kernel, the eta_shell=0 slice of "
      "r+Z|k|^2+Y|k|^4+eta_shell*(|k|-q0)^2")

# ---------- import the ORIGINAL N-001 solver functions ----------
SOLV = REPO/"codes"/"foundations"/"n001_solver"
sys.path.insert(0, str(SOLV))
import continuation_mu2_v25 as cont
import bloch_linearization as bl
r_o, Z_o = cont.kinetic_coefficients(MSH, Y, Q0)
claim("n001_original_kinetic_coefficients_match_stored", abs(r_o-R0) < 1e-12 and abs(Z_o-Z) < 1e-12,
      f"ORIGINAL kinetic_coefficients({MSH},{Y},{Q0}) -> (r={r_o:.7f}, Z={Z_o:.7f}) REPRODUCES stored "
      f"(r_zero={R0:.7f}, Z={Z:.7f})")

def D_orig(k, params):
    return float(bl.bloch_matrix_linear(np.array([k, 0.0, 0.0]), params)[0, 0].real)
# build the runtime params from the JSON scalar_slice (NO hardcoding)
params = {"r": R0, "Z": Z, "Y": Y, "q0": Q0, **SLICE}
ktest = [0.0, 0.31, Q0, 0.93, 1.4, 2.2]
sym = max(abs(D_orig(k, params) - (R0 + Z*k*k + Y*k**4)) for k in ktest)
claim("n001_original_symbol_matches_stored_under_full_scalar_slice", sym < 1e-12,
      f"ORIGINAL bloch_matrix_linear with the FULL JSON scalar_slice {SLICE} at k={ktest} equals stored "
      f"r_zero+Z|k|^2+Y|k|^4 to {sym:.2e}: the verified symbol IS the runtime symbol")

# each scalar-slice setting is load-bearing (vs the original function DEFAULTS)
def shift(mod): return max(abs(D_orig(k, {**params, **mod}) - D_orig(k, params)) for k in ktest)
s_klock = shift({"k_lock": 0.15})          # function default
s_eta   = shift({"eta_shell": 0.1})
s_mix   = shift({"laplacian_mode": "mixed_bcc", "bcc_mix_epsilon": 0.5})
s_fam   = shift({"family_masses": [0.05, 0.0, 0.0]})
claim("scalar_slice_settings_are_load_bearing",
      s_klock > 1e-3 and s_eta > 1e-3 and s_mix > 1e-3 and s_fam > 1e-3,
      f"reverting each scalar_slice setting changes the ORIGINAL diagonal: k_lock=0.15(default)->{s_klock:.4f}, "
      f"eta_shell=0.1->{s_eta:.4f}, mixed_bcc(eps=.5)->{s_mix:.4f}, family_masses->{s_fam:.4f}; ALL load-bearing, "
      "so fixing them in the config (not the checker) is essential")

# full sha256 of the 3 vendored originals match PROVENANCE.json + config
prov = json.loads((SOLV/"PROVENANCE.json").read_text())
hh = {f: sha256(SOLV/f) for f in ("continuation_mu2_v25.py", "bloch_linearization.py", "math56_constants.py")}
ok_h = all(hh[f] == prov[f]["sha256"] for f in hh) and hh["bloch_linearization.py"] == cfg["backend_sha256"] \
       and all(hh[f] == cfg["origin_n001_solver"][f]["sha256"] for f in hh)
claim("n001_original_sources_sha256_pinned", ok_h,
      f"full sha256 of the 3 vendored ORIGINAL sources match PROVENANCE.json + config (continuation "
      f"{hh['continuation_mu2_v25.py'][:16]}.., bloch {hh['bloch_linearization.py'][:16]}.., math56 "
      f"{hh['math56_constants.py'][:16]}..)")

r_bad, Z_bad = cont.kinetic_coefficients(MSH, Y, Q0*1.01)
claim("stored_field_error_is_detected", abs(r_bad-R0) > 1e-3 or abs(Z_bad-Z) > 1e-3,
      f"corrupting stored q0 by +1% -> original coefficients (r={r_bad:.5f}, Z={Z_bad:.5f}) diverge from stored")

# ---------- A1-SCALAR-ANALYTIC-BRANCH ----------
ks = np.linspace(0, 4, 400001); Dvals = MSH + Y*(ks*ks - Q0*Q0)**2
claim("analytic_branch_D_ge_mu2shell_positive",
      MSH > 0 and Y > 0 and Z < 0 and float(Dvals.min()) >= MSH - 1e-12,
      f"mu2_shell={MSH}>0, Y={Y}>0, Z={Z:.4f}<0 => D(k)>=mu2_shell>0 (min={float(Dvals.min()):.6g}) [A1-SCALAR-ANALYTIC-BRANCH]")
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
branch = consistency and (MSH > 0) and (ETA == 0.0) and (sym < 1e-12)
claim("canonical_n001_passes_gates_certification_pending", branch,
      f"canonical N-001 (r_zero={R0:.5f}, mu2_shell={MSH}, q0={Q0}, Z={Z:.5f}, Y={Y}, eta_shell={ETA}): "
      f"delta_Z={dZ:.2e}, delta_m={dm:.2e}, delta_r={dr:.2e} <= eps; mu2_shell>0; scalar_slice matches solver => "
      "NUMERICAL GATES PASS; OPERATOR CERTIFICATION PENDING (T1 OPEN; not yet A2/A3-citable)")
r_t, Z_t, Y_t = 0.35, -1.0, 0.50; ms2_t = mu2_shell_of(r_t, Z_t, Y_t)
claim("legacy_template_FAILS_and_alias_forbidden", (d_Z(Z_t, Y_t, Q0) > eps_Z or ms2_t <= 0) and ms2_t < 0,
      f"template (0.35,-1,0.50): delta_Z={d_Z(Z_t,Y_t,Q0):.3f}>eps; mu2_shell_derived={ms2_t:.3f}<0; alias FORBIDDEN. FAILS")

ok = all(c["passed"] for c in CLAIMS)
cert = dict(version=__version__, config_source=str(cfg_path.relative_to(REPO)), eta_shell=ETA, scalar_slice=SLICE,
    n001_solver_dir="codes/foundations/n001_solver", original_sha256=hh, runtime_symbol_residual=sym,
    load_bearing=dict(k_lock_0p15=s_klock, eta_shell_0p1=s_eta, mixed_bcc=s_mix, family_masses=s_fam),
    gates=dict(delta_Z=dZ, delta_m=dm, delta_r=dr, mu2_shell_positive=MSH > 0, eta_shell_zero=ETA == 0.0,
               consistency_manifest=bool(consistency), analytic_branch_manifest=bool(branch),
               certification="operator certification pending (T1 OPEN)"),
    subset_map=dict(identity=["kernel_identity_complete_square"],
                    analytic_branch=["analytic_branch_D_ge_mu2shell_positive", "lambda0_ge_mu2shell_equality_onshell_only"]),
    claims=CLAIMS, all_pass=ok)
out = REPO/"claims"/"A1-KERNEL-IDENTITY"/"runs"/"a1_kernel_checks.json"
out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(cert, indent=2))
print(f"\nA1 kernel checks v1.5: {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
