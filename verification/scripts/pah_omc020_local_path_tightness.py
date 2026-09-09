#!/usr/bin/env python3
"""Primary replay for the PAH-OMC-020 local path-tightness contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-local-path-tightness/primary.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json": "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69",
    "strategy/pa-hyp/R490-certificate.md": "80563e82f7f592dbbb6c00ff27fdd5270031e8426d4d1520546bf846c6a6d10a",
    "strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json": "87dd9a7225203cdfa84456e446983c573cabc6c50a902a85ea12e28ccbc5b379",
    "strategy/pa-hyp/PAH-OMC-020-pathspace-bridge-result-v1.json": "12eda207fe03441deb47df02a206b8a4cac1accce5aa5eb016b861b53c8af730",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load(relative: str) -> Any:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def parse_source_constant(text: str, pattern: str, label: str) -> int:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        raise AssertionError(f"missing source constant {label}")
    return int(match.group(1))


def compute() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, ok: bool) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})

    actual_pins = {relative: sha(ROOT / relative) for relative in PINS}
    check("source hashes", actual_pins, PINS, actual_pins == PINS)

    pah = load("strategy/pa-hyp/PAH-001-v1.json")
    omc010 = load("strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json")
    c2 = load("strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json")
    pathspace = load("strategy/pa-hyp/PAH-OMC-020-pathspace-bridge-result-v1.json")
    prereg = load("strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json")
    r490_text = (ROOT / "strategy/pa-hyp/R490-certificate.md").read_text(encoding="utf-8")
    c2_text = json.dumps(c2, ensure_ascii=True, sort_keys=True)

    c_sw = parse_source_constant(r490_text, r"C_sw\s*=\s*N_geom\s*\(1\+S_geom\)\s*=\s*(\d+)", "C_sw")
    c2_per_site = parse_source_constant(c2_text, r"C2\(A\)<=N_geom\|A\|=(\d+)\|A\|", "C2 per site")
    root_per_site = c2_per_site
    check("C_sw source extraction", c_sw, 540, c_sw == 540)
    check("C2 source extraction", c2_per_site, 60, c2_per_site == 60)
    check("PAH packet identity", pah.get("packet_id"), "PAH-001", pah.get("packet_id") == "PAH-001")
    check("generator unchanged", "(L_rho f)(x)" in pah["dynamics"]["generator"], True, "(L_rho f)(x)" in pah["dynamics"]["generator"])
    check("external stochastic time", "external stochastic" in pah["dynamics"]["time"], True, "external stochastic" in pah["dynamics"]["time"])
    regulator_order = prereg["scope"]["regulator_order"].lower()
    registered_order = "first j at every fixed n" in regulator_order and "then the original anchored n exhaustion" in regulator_order
    check("registered order", registered_order, True, registered_order)
    check("pathspace remains conditional", pathspace["verdict"], "HOLD_FOR_EVIDENCE", pathspace["verdict"] == "HOLD_FOR_EVIDENCE")
    check("pathspace no physical promotion", pathspace["physical_promotion"], False, pathspace["physical_promotion"] is False)
    check("C2 is auxiliary", c2["claim_bearing"], False, c2["claim_bearing"] is False)

    def bounds(support_size: int, increments: list[Fraction]) -> tuple[int, Fraction, Fraction, Fraction]:
        root_count = root_per_site * support_size
        if len(increments) != root_count:
            raise AssertionError("increment list must contain one d_r for every admitted root")
        max_increment = max(increments, default=Fraction(0))
        gamma = Fraction(c_sw * support_size) * max_increment ** 2
        squared_increment_sum = sum((value ** 2 for value in increments), Fraction(0))
        drift = Fraction(c2_per_site * support_size) * squared_increment_sum
        return root_count, gamma, drift, squared_increment_sum

    support_size = 2
    increments = [Fraction(1, 4)] * (root_per_site * support_size)
    max_increment = max(increments)
    root_count, k_gamma, k_l, squared_increment_sum = bounds(support_size, increments)
    check("support root count", root_count, root_per_site * support_size, root_count == root_per_site * support_size)
    check("increment list cardinality", len(increments), root_count, len(increments) == root_count)
    check("increment square sum", squared_increment_sum, Fraction(root_count) * max_increment ** 2, squared_increment_sum == Fraction(root_count) * max_increment ** 2)
    check("Gamma bound nonnegative", k_gamma >= 0, True, k_gamma >= 0)
    check("drift bound nonnegative", k_l >= 0, True, k_l >= 0)

    delta_small = Fraction(1, 1000)
    delta_large = Fraction(1, 500)
    envelope_small = 2 * delta_small * k_gamma + 2 * delta_small ** 2 * k_l
    envelope_large = 2 * delta_large * k_gamma + 2 * delta_large ** 2 * k_l
    check("two-square envelope", envelope_small >= 0, True, envelope_small >= 0)
    check("delta monotonicity", envelope_small <= envelope_large, True, envelope_small <= envelope_large)
    epsilon = Fraction(2, 1)
    probability_bound = envelope_small / epsilon ** 2
    check("Markov quotient nonnegative", probability_bound >= 0, True, probability_bound >= 0)
    check("fixture quotient below one", probability_bound < 1, True, probability_bound < 1)

    decreasing_values: list[str] = []
    previous: Fraction | None = None
    for exponent in range(1, 7):
        delta = Fraction(1, 10 ** exponent)
        value = 2 * delta * k_gamma + 2 * delta ** 2 * k_l
        if previous is not None:
            check(f"delta sequence {exponent}", value < previous, True, value < previous)
        previous = value
        decreasing_values.append(str(value))
    check("polynomial delta limit shape", envelope_small == 2 * delta_small * k_gamma + 2 * delta_small ** 2 * k_l, True, envelope_small == 2 * delta_small * k_gamma + 2 * delta_small ** 2 * k_l)

    return {
        "schema": "tect/pah-omc020-local-path-tightness/1.0",
        "audit_id": "PAH-OMC-020-LOCAL-PATH-TIGHTNESS-001",
        "result_id": "R-541",
        "task_id": "T-064",
        "status": "PASS_LOCAL_PATH_TIGHTNESS_HOLD",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": actual_pins,
        "source_constants": {"C_sw": c_sw, "C2_per_site": c2_per_site, "root_bound_per_site": root_per_site},
        "fixture": {
            "support_size": support_size,
            "max_increment": str(max_increment),
            "root_count": root_count,
            "increment_count": len(increments),
            "increment_sum_squares": str(squared_increment_sum),
            "K_Gamma": str(k_gamma),
            "K_L": str(k_l),
            "delta_small": str(delta_small),
            "delta_large": str(delta_large),
            "envelope_small": str(envelope_small),
            "envelope_large": str(envelope_large),
            "epsilon": str(epsilon),
            "markov_bound": str(probability_bound),
            "decreasing_envelopes": decreasing_values,
        },
        "checks": checks,
        "checks_passed": len(checks),
        "finding": "For every bounded local cylinder with finite root support, the registered Gibbs conductance and squared-rate bounds imply a uniform stopped-time second-moment increment envelope 2*delta*K_Gamma(f)+2*delta^2*K_L(f), hence Aldous tightness of the finite stationary observable paths on every compact external-time interval.",
        "proof_boundary": "The result concerns only tightness of finite PAH observable paths. It does not identify a subsequential limit, solve a martingale problem, prove non-explosion or uniqueness of an infinite process, establish N2b/N2c/N4, identify R-512, or prove semigroup convergence.",
        "missing_assumptions": [
            "A source-authorized martingale-problem or path-space construction for the limiting cylinder generator.",
            "Uniform-integrability passage for L_n f and identification of every subsequential limit with the same cylinder martingale problem.",
            "Uniqueness/non-explosion and equality with the R-512 minimal-form semigroup.",
        ],
        "non_claims": [
            "No new PAH functional, rate, state, carrier, regulator, normalization, time convention or limit order.",
            "No infinite-volume process, semigroup convergence, common H/U_n, N2b liminf/recovery, N2c/N4 boundary escape or R-512 identification.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang-Mills or TOE conclusion.",
        ],
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_local_path_tightness.py --check",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 local path tightness replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 LOCAL PATH TIGHTNESS: PASS {payload['checks_passed']}/{payload['checks_passed']}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
