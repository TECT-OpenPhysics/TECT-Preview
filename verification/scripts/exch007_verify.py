"""Replay exact scalar certificates, the R-579 trial and the partial Lean proof."""
import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path

import sympy as s
import pah_v2_gd001_lean as lean_runner

ROOT = Path(__file__).resolve().parents[2]
CARD = ROOT / "strategy/physical-candidates/TECT-EXCH-007-contract-v1.json"
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-11-20-exch007.json"
LEAN = ROOT / "verification/lean/Tect/UniformMixing.lean"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def replay(cache, elan):
    contract = load(CARD)
    erratum = load(CARD.with_name("TECT-EXCH-007-source-erratum.json"))
    pins = dict(contract["source_hashes"])
    field = erratum["field"]
    assert digest(CARD) == erratum["contract_sha256"] and len(pins[field]) == 63
    original = ROOT / "strategy/physical-candidates/TECT-EXCH-001-contract-v1.json"
    pins[field] = erratum["correct_source_sha256"]
    assert pins[field] == load(original)["source_hashes"][field]
    files = list(pins)
    for name, h in pins.items():
        assert digest(ROOT / name) == h, name
    def record(suffix):
        matches = [name for name in files if name.endswith(suffix)]
        assert len(matches) == 1
        return load(ROOT / matches[0])
    a = record("production_functional_manifest.json")["parameters"]
    b = record("TECT-EXCH-001-contract-v1.json")["model"]["inserted_parameters"]
    src = record("charge_ensemble_first_order_shell_transition_manifest.json")["exact_constants"]
    rat = lambda v: F(str(v))
    gamma, lam = rat(a["gamma"]), rat(a["lambda"])
    eps, omega, u4 = (rat(b[k]) for k in ("epsilon", "omega", "u"))
    V = rat(a["Lx"])*rat(a["Ly"])*rat(a["Lz"])
    rho = -3*lam/(4*gamma)
    q, c = rho/2, gamma/6
    lo, hi = map(rat, src["transition_chemical_potential_interval_decimal"])
    gap = rat(contract["gap_per_unit_volume"])
    d = rho+F(1,4)
    absorb = eps**2/(4*c)
    margin = gap**2/(2*eps**2*d*q**2)
    r = eps*rho
    p = rho-2*r*r
    trial_upper = (omega/2-F(1,4))*r*r+u4*r**4/4+c*p*(p-rho)**2-eps*r*p
    # Independent direct plane-energy calculation at the same charge:
    # Evaluate the bulk potential and spectral bottom at trial and pure plane.
    mu = s.symbols("mu", real=True)
    lambda0 = mu+3*lam**2/(16*gamma)
    bulk = lambda t: lambda0*t/2+lam*t**2/4+gamma*t**3/6
    plane = bulk(p)-bulk(rho)+omega*r*r/2+u4*r**4/4-eps*r*p
    t, h, v, k, X = s.symbols("t h v k X", real=True)
    checks = {}
    def check(label, value):
        if not bool(value):
            raise AssertionError(label)
        checks[label] = True
    check("charge_and_density", V*q == rat(src["coexistence_charge"]) and rho == rat(src["coexistence_density"]))
    check("positive_input_and_mu_window", eps > 0 and c > 0 and u4 > 0 and F(1,4) < lo < hi < F(1,3))
    check("pinned_Lean_coefficients", (eps,c,omega,absorb) == (F(1,16),F(27,100),1,F(25,6912)))  # Lean bridge oracles
    check("trial_positive_and_fixed_charge", p > 0 and p/2+r*r == q)
    check("strict_nonempty_gap_in_trial", 0 < gap < -trial_upper)
    check("direct_plane_expression", s.expand(plane-(trial_upper-(mu-F(1,4))*r*r)) == 0)
    trial_mode = (1,1,1)  # R-579 designated witness, not a momentum scan
    check("spectral_shell_and_doubled_mode_admitted", sum(i*i for i in trial_mode) == src["torus_radial_shell_norm_squared"] and
          max(map(abs,trial_mode)) <= 1 and max(abs(2*i) for i in trial_mode) <= 2)
    check("pointwise_exact_square", s.expand(d*t+t*(t-rho)**2-t**2-t*(t-rho-F(1,2))**2) == 0)
    check("Young_exact_square", s.expand(c*v**2+absorb*h**2-eps*h*v-(2*c*v-eps*h)**2/(4*c)) == 0)
    residual = omega/2-F(1,3)-absorb
    check("positive_reservoir_remainder", residual > 0)
    check("weighted_product_identity", s.expand((2*k*X)*(k*(1-X))-2*k**2*X*(1-X)) == 0)
    # Independent certificate: pointwise Young before spatial integration.
    independent = rat(src["coexistence_charge"])/V
    rb = rat(src["coexistence_density"])
    independent_margin = (gap/eps)**2 / ((rb+F(1,4))*2*independent**2)
    check("independent_charge_normalization", independent_margin == margin)
    check("nontrivial_and_feasible", 0 < margin < F(1,4))
    check("pure_ends_excluded", all(x*(1-x) < margin for x in (0,1)))
    check("reject_missing_factor_two", independent_margin != (gap/eps)**2/(d*q*q))
    check("reject_insufficient_Young_coefficient", (c*(eps/(2*c))**2+(absorb/2)-eps*(eps/(2*c))) < 0)
    check("trial_energy_satisfies_fraction_bound", (p/(2*q))*(r*r/q) >= margin)
    lean_runner.SOURCE = LEAN
    lean = lean_runner.run(cache, elan)
    return {"scope":"R-583; fixed-volume integrated charge fractions only",
            "contract_sha256":digest(CARD), "verifier_sha256":digest(Path(__file__)),
            "lean_source_sha256":digest(LEAN),
            "exact":{n:str(v) for n,v in {"q":q,"volume":V,"rho_star":rho,"c":c,"d":d,
                "delta":gap,"trial_gap_upper":trial_upper,"residual_lower":residual,"product_floor":margin}.items()},
            "checks":checks,
            "lean":{k:lean[k] for k in ("source_sha256","compiler_version","package_revisions","declarations","exit_code")},
            "not_formalized":"Spatial integrals/Cauchy-Schwarz, source Hamiltonian decomposition, admissibility of the original shell and ODE conservation/completeness are analytic, not Lean results."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean-cache", type=Path, default=ROOT/"verification/lean/.lake/packages")
    parser.add_argument("--elan-home", type=Path, default=Path.home()/".elan")
    parser.add_argument("--write-run", action="store_true")
    args = parser.parse_args()
    report = replay(args.lean_cache, args.elan_home)
    if args.write_run:
        with RUN.open("x", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(report, indent=2)+"\n")
    elif report != load(RUN):
        raise ValueError("Published run does not reproduce")
    print("EXCH007: PASS;", len(report["checks"]), "checks;", len(report["lean"]["declarations"]),
          "Lean lemmas; product floor =", report["exact"]["product_floor"])
