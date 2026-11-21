"""Exact replay of the EXCH-008 initial low-mode drift obstruction."""

import argparse
from collections import defaultdict
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path

import sympy as s

ROOT = Path(__file__).resolve().parents[2]
CARD = ROOT / "strategy/physical-candidates/TECT-EXCH-008-witness-v1.json"
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-11-21-exch008.json"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def mul(a, b):
    out = defaultdict(int)
    for i, x in a.items():
        for j, y in b.items():
            out[i + j] += x * y
    return {j: s.expand(x) for j, x in out.items()}


def star(a):
    return {-j: s.conjugate(x) for j, x in a.items()}


def replay():
    contract = load(CARD)
    pins = contract["source_sha256"]
    for name, pin in pins.items():
        if digest(ROOT / name) != pin:
            raise ValueError(f"Changed pinned source: {name}")

    def source(suffix):
        name, = [name for name in pins if name.endswith(suffix)]
        return load(ROOT / name)

    base = source("production_functional_manifest.json")["parameters"]
    p1 = source("charge_ensemble_first_order_shell_transition_manifest.json")["exact_constants"]
    ex = source("TECT-EXCH-001-contract-v1.json")["model"]["inserted_parameters"]
    rat = lambda x: F(str(x))
    gamma, lam = map(rat, (base["gamma"], base["lambda"]))
    volume = rat(base["Lx"]) * rat(base["Ly"]) * rat(base["Lz"])
    omega, u, eps = (rat(ex[name]) for name in ("omega", "u", "epsilon"))
    delta = rat(source("TECT-EXCH-007-contract-v1.json")["gap_per_unit_volume"])
    lo, hi = map(rat, p1["transition_chemical_potential_interval_decimal"])
    rho = -3 * lam / (4 * gamma)
    r = eps * rho
    b = r * rat(contract["witness_input"]["relative_high_amplitude"])
    n = r*r + 2*b*b
    p = rho - 2*n
    k = contract["witness_input"]["order_shell_index"]
    fourth = r**4 + 8*r*r*b*b + 6*b**4
    e_upper = (omega/2-F(1, 4))*n + u*fourth/4 + gamma*p*(p-rho)**2/6 - eps*r*p
    drift = 2*u*r*b**3

    checks = {}

    def check(name, condition):
        if not bool(condition):
            raise AssertionError(name)
        checks[name] = True

    check("shell_and_real_positive_amplitude", len(k) == 3 and max(map(abs, k)) == 1
          and sum(j*j for j in k) == p1["torus_radial_shell_norm_squared"] and p > 0)
    check("exact_charge", volume*(p/2+n) == rat(p1["coexistence_charge"])
          and p/2+n == rho/2 and rho == rat(p1["coexistence_density"]))
    check("positive_parameters_and_mu_enclosure", all(v > 0 for v in (r, b, u, omega))
          and F(1, 4) < lo < hi < F(1, 3))
    check("strict_low_energy", e_upper < -delta < 0)
    mu = s.Symbol("mu", real=True)
    bulk = lambda x: (mu+3*lam**2/(16*gamma))*x/2 + lam*x*x/4 + gamma*x**3/6
    check("direct_full_plane_energy_subtraction", s.expand(
        bulk(p)-bulk(rho) + omega*n/2 + u*fourth/4 - eps*r*p
        - (e_upper + (F(1, 4)-mu)*n)) == 0)

    x, y = s.symbols("r b", real=True)
    fprime = {}
    for sign in (1, -1):
        a = {0: x, 1: y, 2: sign*s.I*y}
        power = mul(a, star(a))
        cubic = mul(power, a)
        check(f"quadratic_{sign}", power[0] == x*x + 2*y*y)
        check(f"quartic_{sign}", mul(power, power)[0] == x**4 + 8*x*x*y*y + 6*y**4)
        check(f"cubic_resonant_mode_{sign}", cubic[0] == x**3 + 4*x*y*y - sign*s.I*y**3)
        cprime = -s.I*(omega*r + u*cubic[0].subs({x:r, y:b}) - eps*p)
        fprime[str(sign)] = F(2*r*s.re(cprime))
        check(f"invariant_drift_{sign}", fprime[str(sign)] == -sign*drift)

    m = s.Symbol("N", integer=True, positive=True)
    indices = [2+0*m, 2+m, 2+2*m]
    check("original_cutoff_and_nonaliasing", indices[-1] == 2*(m+1)
          and all((j-2).is_nonnegative for j in indices)
          and all((j-i).is_positive for i, j in zip(indices, indices[1:])))
    check("off_sector_weak_limit", volume*(rho/2-p/2-r*r) == 2*volume*b*b > 0)
    check("separation_and_minimax", drift > 0 and abs(fprime["1"]-fprime["-1"]) == 2*drift)
    # Control: removing either high mode eliminates the phase-sensitive term.
    check("one_high_mode_no_resonance", s.im(mul(mul({0:x, 1:y}, {0:x, -1:y}),
          {0:x, 1:y})[0]) == 0)
    exact = {"volume": volume, "q": rho/2, "r": r, "b": b, "p": p,
             "gap": delta, "energy_upper": e_upper, "tail_density": 2*b*b,
             "missing_charge_in_weak_limit": 2*volume*b*b, "worst_case_error_floor": drift,
             "positive_sign_drift": fprime["1"], "negative_sign_drift": fprime["-1"]}
    return {"id": contract["id"], "contract_sha256": digest(CARD),
            "verifier_sha256": digest(Path(__file__)), "checks": checks,
            "exact": {k: str(v) for k, v in exact.items()},
            "limit_boundary": "Initial derivative only, at common ambient weak limit with a charge defect."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-run", action="store_true")
    args = parser.parse_args()
    record = replay()
    if args.write_run:
        with RUN.open("x", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(record, indent=2) + "\n")
    elif record != load(RUN):
        raise ValueError("Published run does not reproduce")
    print(f"EXCH008: PASS ({len(record['checks'])} checks; worst-case error floor "
          f"{record['exact']['worst_case_error_floor']})")
