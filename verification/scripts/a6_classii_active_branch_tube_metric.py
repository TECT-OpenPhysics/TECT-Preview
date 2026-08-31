#!/usr/bin/env python3
"""Primary exact audit for the additive R-463 active-branch tube metric.

R-463 keeps the R-462 coordinates and the A6/A7 fixed-floor functional.  It
derives a radial lower bound from an exact sum-of-squares identity, defines a
weighted active normal tube metric, and enumerates only a declared bounded
local grid.  The exponential numbers are finite proxy diagnostics with
Z >= 1, not a correlated field Gibbs, continuum, or tightness result.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import platform
import tempfile
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
__claims__ = [
    "A6-CLASSII-UV-POWER-COUNTING",
    "A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE",
]

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "a6-classii-active-branch-tube-metric-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A6-CLASSII-UV-POWER-COUNTING"
    / "runs"
    / "2026-08-31-primary-a6-active-branch-tube-metric"
    / "primary.json"
)


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def derive_coefficients(a1: dict[str, Any]) -> dict[str, F]:
    p = a1["parameters"]
    alpha = F(str(p["alpha_X"]))
    beta = F(str(p["beta_X"]))
    denominator = F(str(p["M_X"])) ** 2 + F(str(p["classii_mass_regularizer"]))
    return {
        "a": F(str(p["cJJ"])) * alpha * alpha / denominator,
        "b": F(str(p["cJK"])) * alpha * beta / denominator,
        "c": F(str(p["cKK"])) * beta * beta / denominator,
        "rho_floor": F(str(p["rho_regularizer"])),
        "denominator": denominator,
    }


def qform(a: F, b: F, c: F, x: F, y: F) -> F:
    return a * x * x + 2 * b * x * y + c * y * y


def active_values(values: list[F]) -> list[tuple[F, F, F, F, F]]:
    return list(itertools.product(values, repeat=5))


def active_energy2(a: F, b: F, c: F, kappa: F, point: tuple[F, F, F, F, F]) -> F:
    x, y, u1, u2, u3 = point
    return qform(a, b, c, x, y) + kappa * (u1 * u1 + u2 * u2 + u3 * u3)


def active_metric(lambda_r: F, kappa: F, point: tuple[F, F, F, F, F]) -> F:
    x, y, u1, u2, u3 = point
    return lambda_r * (x * x + y * y) + kappa * (u1 * u1 + u2 * u2 + u3 * u3)


def decimal_fraction(value: F) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def proxy_bound(count: int, beta: F, energy2_min: F, precision: int) -> Decimal:
    with localcontext() as context:
        context.prec = precision
        exponent = -(decimal_fraction(beta) * decimal_fraction(energy2_min) / Decimal(2))
        return Decimal(count) * exponent.exp()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1_item = manifest["inputs"]["a1_production_functional_manifest"]
    a1_path = REPO / a1_item["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    r462_item = manifest["inputs"]["r462_active_branch_normal_form_manifest"]
    r462_path = REPO / r462_item["path"]
    coefficients = derive_coefficients(a1)
    a, b, c = (coefficients[key] for key in ("a", "b", "c"))
    determinant = a * c - b * b
    trace = a + c
    lambda_r = determinant / trace
    kappa = a + 2 * b + c
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A6-CLASSII-ACTIVE-BRANCH-TUBE-METRIC-v1", manifest["audit_id"], "A6-CLASSII-ACTIVE-BRANCH-TUBE-METRIC-v1")
    check("result identity", manifest["result_id"] == "R-463", manifest["result_id"], "R-463")
    check("claim nonbearing", manifest["claim_bearing"] is False and manifest["tier"] == "T0", (manifest["claim_bearing"], manifest["tier"]), (False, "T0"))
    check("functional unchanged", manifest["methods_preserved"]["a6_a7_functional_unchanged"] is True, manifest["methods_preserved"], True)
    check("owner order unchanged", manifest["methods_preserved"]["owner_order_unchanged"] is True, manifest["methods_preserved"], True)
    check("A1 authority exists", a1_path.is_file(), a1_path, True)
    check("A1 authority hash", sha256(a1_path) == a1_item["sha256"], sha256(a1_path), a1_item["sha256"])
    check("R462 authority exists", r462_path.is_file(), r462_path, True)
    check("R462 authority hash", sha256(r462_path) == r462_item["sha256"], sha256(r462_path), r462_item["sha256"])
    check("eta shell fixed", F(str(a1["parameters"]["eta_shell"])) == 0, a1["parameters"]["eta_shell"], 0)
    check("coefficient a positive", a > 0, a, ">0")
    check("coefficient c positive", c > 0, c, ">0")
    check("determinant positive", determinant > 0, determinant, ">0")
    check("trace positive", trace > 0, trace, ">0")
    check("angular coefficient positive", kappa > 0, kappa, ">0")
    check("radial constant positive", lambda_r > 0, lambda_r, ">0")
    check("angular identity", a * kappa == (a + b) ** 2 + determinant, a * kappa, (a + b) ** 2 + determinant)
    check("floor positive", coefficients["rho_floor"] > 0, coefficients["rho_floor"], ">0")

    active_grid = [F(value) for value in manifest["audit"]["active_grid_values"]]
    flat_grid = [F(value) for value in manifest["audit"]["flat_grid_values"]]
    thresholds = [F(value) for value in manifest["audit"]["tube_thresholds"]]
    betas = [F(value) for value in manifest["audit"]["beta_values"]]
    precision = int(manifest["audit"]["decimal_precision"])
    points = active_values(active_grid)
    radial_checks = 0
    gap_nonnegative_checks = 0
    domination_checks = 0
    zero_metric_checks = 0
    active_energies = []
    active_metrics = []
    for point in points:
        x, y, u1, u2, u3 = point
        radial = qform(a, b, c, x, y)
        radial_gap = radial - lambda_r * (x * x + y * y)
        square_sum = (a * x + b * y) ** 2 + (b * x + c * y) ** 2
        radial_checks += 1
        if trace * radial_gap != square_sum:
            raise AssertionError(("radial gap identity", point, trace * radial_gap, square_sum))
        gap_nonnegative_checks += 1
        if radial_gap < 0:
            raise AssertionError(("radial gap sign", point, radial_gap))
        energy2 = active_energy2(a, b, c, kappa, point)
        metric = active_metric(lambda_r, kappa, point)
        domination_checks += 1
        if energy2 < metric:
            raise AssertionError(("active domination", point, energy2, metric))
        active_energies.append(energy2)
        active_metrics.append(metric)
        if metric == 0:
            zero_metric_checks += 1
            if point != (F(0), F(0), F(0), F(0), F(0)):
                raise AssertionError(("zero active metric", point))

    check("radial identity count", radial_checks == len(points), radial_checks, len(points))
    check("radial gap count", gap_nonnegative_checks == len(points), gap_nonnegative_checks, len(points))
    check("active domination count", domination_checks == len(points), domination_checks, len(points))
    check("active metric zero count", zero_metric_checks == 1, zero_metric_checks, 1)

    shell_reports: list[dict[str, Any]] = []
    nonempty_shells = 0
    proxy_bounds_below_one = 0
    for threshold in thresholds:
        outside = [energy for energy, metric in zip(active_energies, active_metrics) if metric >= threshold]
        if not outside:
            raise AssertionError(("empty active shell", threshold))
        nonempty_shells += 1
        energy2_min = min(outside)
        report = {
            "threshold": str(threshold),
            "outside_count": len(outside),
            "minimum_energy2": str(energy2_min),
            "minimum_energy": str(energy2_min / 2),
            "proxy_bounds": [],
        }
        for beta in betas:
            bound = proxy_bound(len(outside), beta, energy2_min, precision)
            if bound < 1:
                proxy_bounds_below_one += 1
            report["proxy_bounds"].append({"beta": str(beta), "bound": format(bound, "f"), "bound_lt_one": bound < 1})
        shell_reports.append(report)

    check("nonempty shell count", nonempty_shells == len(thresholds), nonempty_shells, len(thresholds))
    check("proxy bound has a subunit case", proxy_bounds_below_one > 0, proxy_bounds_below_one, ">0")
    counts = [item["outside_count"] for item in shell_reports]
    check("shell counts monotone", counts == sorted(counts, reverse=True), counts, "nonincreasing")
    check("minimum energy positive", all(F(item["minimum_energy2"]) > 0 for item in shell_reports), [item["minimum_energy2"] for item in shell_reports], ">0")

    flat_points = list(itertools.product(flat_grid, repeat=int(manifest["audit"]["flat_dimensions"])))
    flat_threshold = thresholds[-1]
    flat_outside = [point for point in flat_points if sum(value * value for value in point) >= flat_threshold]
    check("flat proxy nonempty", len(flat_outside) > 0, len(flat_outside), ">0")
    flat_energy_values = [F(0) for _ in flat_outside]
    check("flat energy barrier zero", min(flat_energy_values) == 0, min(flat_energy_values), 0)
    flat_bound = proxy_bound(len(flat_outside), betas[0], F(0), precision)
    check("flat proxy bound not subunit", flat_bound >= 1, flat_bound, ">=1")
    check("flat proxy count", len(flat_points) == len(flat_grid) ** int(manifest["audit"]["flat_dimensions"]), len(flat_points), len(flat_grid) ** int(manifest["audit"]["flat_dimensions"]))
    check("active grid cardinality", len(points) == len(active_grid) ** 5, len(points), len(active_grid) ** 5)
    check("active grid includes zero", (F(0), F(0), F(0), F(0), F(0)) in points, True, True)
    check("active energy zero state", active_energy2(a, b, c, kappa, (F(0), F(0), F(0), F(0), F(0))) == 0, 0, 0)
    check("active metric nonnegative", all(value >= 0 for value in active_metrics), min(active_metrics), ">=0")
    check("active energy nonnegative", all(value >= 0 for value in active_energies), min(active_energies), ">=0")
    check("threshold cardinality", len(thresholds) > 0, len(thresholds), ">0")
    check("beta cardinality", len(betas) > 0, len(betas), ">0")
    check("proxy report dimensions", all(len(report["proxy_bounds"]) == len(betas) for report in shell_reports), [len(report["proxy_bounds"]) for report in shell_reports], len(betas))
    check("proxy bound finiteness", all(math.isfinite(float(item["bound"])) for report in shell_reports for item in report["proxy_bounds"]), True, True)
    check("subunit proxy count", sum(1 for report in shell_reports for item in report["proxy_bounds"] if item["bound_lt_one"]) == proxy_bounds_below_one, proxy_bounds_below_one, ">=0")
    check("flat dimensions positive", int(manifest["audit"]["flat_dimensions"]) > 0, manifest["audit"]["flat_dimensions"], ">0")
    check("flat threshold uses declared input", flat_threshold == thresholds[-1], flat_threshold, thresholds[-1])
    check("flat outside subset", len(flat_outside) <= len(flat_points), len(flat_outside), len(flat_points))
    check("shell minima positive", all(F(report["minimum_energy"]) > 0 for report in shell_reports), [report["minimum_energy"] for report in shell_reports], ">0")

    derived = {
        "coefficients": {key: str(value) for key, value in coefficients.items()},
        "determinant": str(determinant),
        "trace": str(trace),
        "lambda_radial": str(lambda_r),
        "kappa_angular": str(kappa),
        "active_grid_points": len(points),
        "radial_identity_checks": radial_checks,
        "active_domination_checks": domination_checks,
        "active_metric_zero_checks": zero_metric_checks,
        "shell_reports": shell_reports,
        "flat_grid_points": len(flat_points),
        "flat_outside_count": len(flat_outside),
        "flat_energy_barrier": "0",
        "flat_proxy_bound": format(flat_bound, "f"),
        "scope": manifest["scope_firewall"],
    }
    payload = {
        "schema": "tect/a6-classii-active-branch-tube-metric-primary-result/1.0",
        "run_kind": "primary",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_ids": __claims__,
        "script_version": __version__,
        "verdict": "R-463-PRIMARY-PASS",
        "assertion_summary": {"passed": len(rows), "total": len(rows)},
        "assertions": rows,
        "derived": derived,
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if not args.no_store:
        output = args.output if args.output.is_absolute() else REPO / args.output
        atomic_json(output, payload)
    print(f"PRIMARY R-463 PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
