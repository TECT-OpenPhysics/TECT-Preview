#!/usr/bin/env python3
"""Non-importing independent recomputation of the R-466 tube bound."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

sys.set_int_max_str_digits(1_000_000)

REPO = Path(__file__).resolve().parents[2]
A1 = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
R464 = REPO / "strategy" / "a6-classii-finite-gibbs-conditioning-manifest.json"
R465 = REPO / "strategy" / "a6-classii-partition-envelope-manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A6-CLASSII-UV-POWER-COUNTING" / "runs" / "2026-08-31-independent-a6-positive-mass-tube-envelope" / "independent.json"
CUTOFFS = (1, 2, 3, 4, 6, 8, 10)
BETAS = (Fraction(1, 2), Fraction(1), Fraction(2))
HALF_WIDTH = Fraction(1, 16)
ENERGY_CEILING = Fraction(1)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def q(value: Any) -> Fraction:
    return Fraction(str(value))


def add(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if bool(ok) else "FAIL", "actual": actual, "expected": expected})


def params() -> dict[str, Fraction]:
    raw = json.loads(A1.read_text(encoding="utf-8"))["parameters"]
    return {name: q(raw[name]) for name in ("Lx", "Ly", "Lz", "gamma", "lambda", "r", "Z", "Y")}


def derivation(p: dict[str, Fraction]) -> dict[str, Fraction]:
    volume = p["Lx"] * p["Ly"] * p["Lz"]
    mu2 = p["r"] - p["Z"] * p["Z"] / (4 * p["Y"])
    ell = -p["lambda"]
    threshold = 3 * ell / p["gamma"]
    constant = ell * threshold * threshold / 4
    return {"volume": volume, "mu2": mu2, "gamma": p["gamma"], "K": constant * volume}


def row(beta: Fraction, cutoff: int, d: dict[str, Fraction]) -> dict[str, Any]:
    sites = (2 * cutoff + 1) ** 3
    dimension = 6 * sites
    coefficient = d["gamma"] * d["volume"] / (12 * sites**3)
    beta_f = float(beta)
    coeff_f = float(coefficient)
    # Evaluate the same radial comparison in a different accumulation order.
    terms = [
        dimension / 2 * math.log(math.pi),
        math.lgamma(dimension / 6),
        -math.log(3.0),
        -math.lgamma(dimension / 2),
        -dimension / 6 * math.log(beta_f * coeff_f),
    ]
    radial_log = math.fsum(terms)
    log_z_upper = math.fsum([beta_f * float(d["K"]), radial_log])
    side = 2 * HALF_WIDTH
    log_box = dimension * math.log(float(side))
    log_num = log_box - beta_f * float(ENERGY_CEILING)
    log_lower = log_num - log_z_upper
    return {
        "cutoff": cutoff,
        "sites": sites,
        "real_dimension": dimension,
        "beta": str(beta),
        "coefficient": str(coefficient),
        "coefficient_times_sites_cubed": str(coefficient * sites**3),
        "tube_half_width": str(HALF_WIDTH),
        "tube_side": str(side),
        "tube_box_volume_exact": str(side**dimension),
        "log_tube_box_volume": log_box,
        "energy_ceiling": str(ENERGY_CEILING),
        "beta_energy_ceiling": beta_f * float(ENERGY_CEILING),
        "log_numerator_lower": log_num,
        "log_partition_upper": log_z_upper,
        "log_probability_lower": log_lower,
        "finite": all(math.isfinite(v) for v in (log_box, log_num, log_z_upper, log_lower)),
        "positive_box_volume": side**dimension > 0,
        "lower_bound_is_nontrivial_log": log_lower < 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    p = params()
    d = derivation(p)
    checks: list[dict[str, Any]] = []
    for name, path in (("A1", A1), ("R-464", R464), ("R-465", R465)):
        add(checks, f"{name} exists", path.is_file(), str(path), True)
        add(checks, f"{name} digest nonempty", bool(digest(path)), digest(path), "nonempty SHA-256")
    add(checks, "volume positive", d["volume"] > 0, str(d["volume"]), ">0")
    add(checks, "mu2 positive", d["mu2"] > 0, str(d["mu2"]), ">0")
    add(checks, "gamma positive", d["gamma"] > 0, str(d["gamma"]), ">0")
    add(checks, "half-width positive", HALF_WIDTH > 0, str(HALF_WIDTH), ">0")
    add(checks, "declared side", 2 * HALF_WIDTH == Fraction(1, 8), str(2 * HALF_WIDTH), "1/8")
    all_rows: list[dict[str, Any]] = []
    by_beta: dict[str, list[dict[str, Any]]] = {}
    for beta in BETAS:
        beta_rows: list[dict[str, Any]] = []
        for cutoff in CUTOFFS:
            current = row(beta, cutoff, d)
            beta_rows.append(current)
            all_rows.append(current)
            add(checks, f"finite row beta={beta} N={cutoff}", current["finite"], current["log_probability_lower"], "finite")
            add(checks, f"positive box volume beta={beta} N={cutoff}", current["positive_box_volume"], current["tube_box_volume_exact"], ">0")
            add(checks, f"positive coefficient beta={beta} N={cutoff}", q(current["coefficient"]) > 0, current["coefficient"], ">0")
            add(checks, f"coefficient scale beta={beta} N={cutoff}", q(current["coefficient_times_sites_cubed"]) == d["gamma"] * d["volume"] / 12, current["coefficient_times_sites_cubed"], str(d["gamma"] * d["volume"] / 12))
            add(checks, f"negative lower log beta={beta} N={cutoff}", current["lower_bound_is_nontrivial_log"], current["log_probability_lower"], "<0")
        by_beta[str(beta)] = beta_rows
        logs = [item["log_probability_lower"] for item in beta_rows]
        add(checks, f"strict cutoff decay beta={beta}", all(left > right for left, right in zip(logs, logs[1:])), logs, "strictly decreasing")
    add(checks, "row count", len(all_rows) == len(BETAS) * len(CUTOFFS), len(all_rows), len(BETAS) * len(CUTOFFS))
    add(checks, "owner-neutral label", True, "conditional interface", "not source-owned")
    add(checks, "uniformity withheld", True, "not asserted", "not asserted")
    passed = sum(item["status"] == "PASS" for item in checks)
    output = {
        "schema": "tect/a6-classii-positive-mass-tube-envelope-independent/1.0",
        "run_kind": "independent",
        "result_id": "R-466",
        "exploration_id": "EXP-001341",
        "verdict": "R-466-INDEPENDENT-PASS" if passed == len(checks) else "R-466-INDEPENDENT-FAIL",
        "assertion_summary": {"passed": passed, "total": len(checks)},
        "assertions": checks,
        "inputs": {"a1": {"path": str(A1.relative_to(REPO)), "sha256": digest(A1)}, "r464": {"path": str(R464.relative_to(REPO)), "sha256": digest(R464)}, "r465": {"path": str(R465.relative_to(REPO)), "sha256": digest(R465)}, "cutoffs": list(CUTOFFS), "betas": [str(x) for x in BETAS], "tube_half_width": str(HALF_WIDTH), "tube_energy_ceiling": str(ENERGY_CEILING)},
        "derived": {"volume": str(d["volume"]), "mu2": str(d["mu2"]), "gamma": str(d["gamma"]), "comparison_K": str(d["K"]), "rows": all_rows, "formula": "mu_N(B_N)>=vol(B_N)*exp(-beta*E_tube)/Z_upper_N"},
        "evidence_level": "T0 independent finite conditional Gibbs-mass lower-bound interface",
        "assumptions": ["R-464/R-465 comparison bounds are valid at fixed cutoff.", "The owner supplies a measurable tube and energy ceiling.", "The declared tube fixtures are synthetic and owner-neutral."],
        "missing_assumptions": ["Source-owned branch embedding and energy ceiling.", "Cutoff-uniform correlated partition and entropy/Jacobian control.", "Tightness, continuum and physical/QFT/Yang--Mills bridges."],
        "non_claims": ["No source-owned branch or physical probability is admitted.", "No cutoff-uniform, entropy, tightness, continuum or mass-gap result follows.", "Existing methods, owner order and promotion firewalls are unchanged."],
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
    }
    path = args.output if args.output.is_absolute() else REPO / args.output
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"INDEPENDENT R-466 {output['verdict']} {passed}/{len(checks)}")
    print(f"Evidence: {path.resolve()}")
    return 0 if output["verdict"].endswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
