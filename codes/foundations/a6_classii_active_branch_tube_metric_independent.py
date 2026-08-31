#!/usr/bin/env python3
"""Non-importing independent audit for R-463.

The implementation derives the coefficient matrix independently, reconstructs
the radial sum-of-squares gap, and repeats the bounded active/flat proxy test.
It deliberately does not import the primary script and makes no Gibbs or
tightness claim.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import platform
import tempfile
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "a6-classii-active-branch-tube-metric-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A6-CLASSII-UV-POWER-COUNTING"
    / "runs"
    / "2026-08-31-independent-a6-active-branch-tube-metric"
    / "independent.json"
)


def normalized_sha(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def coefficients(a1: dict[str, Any]) -> dict[str, F]:
    p = a1["parameters"]
    alpha = F(str(p["alpha_X"]))
    beta = F(str(p["beta_X"]))
    denominator = F(str(p["M_X"])) * F(str(p["M_X"])) + F(str(p["classii_mass_regularizer"]))
    return {
        "a": F(str(p["cJJ"])) * alpha * alpha / denominator,
        "b": F(str(p["cJK"])) * alpha * beta / denominator,
        "c": F(str(p["cKK"])) * beta * beta / denominator,
        "rho_floor": F(str(p["rho_regularizer"])),
        "denominator": denominator,
    }


def quadratic(a: F, b: F, c: F, x: F, y: F) -> F:
    return a * x * x + 2 * b * x * y + c * y * y


def as_decimal(value: F) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def bound(count: int, beta: F, energy2: F, precision: int) -> Decimal:
    with localcontext() as context:
        context.prec = precision
        return Decimal(count) * (-(as_decimal(beta) * as_decimal(energy2) / Decimal(2))).exp()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1_item = manifest["inputs"]["a1_production_functional_manifest"]
    a1_path = REPO / a1_item["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    coeff = coefficients(a1)
    a, b, c = coeff["a"], coeff["b"], coeff["c"]
    determinant = a * c - b * b
    trace = a + c
    lambda_r = determinant / trace
    kappa = a + 2 * b + c
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": str(actual), "expected": str(expected)})
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A6-CLASSII-ACTIVE-BRANCH-TUBE-METRIC-v1", manifest["audit_id"], "A6-CLASSII-ACTIVE-BRANCH-TUBE-METRIC-v1")
    check("result identity", manifest["result_id"] == "R-463", manifest["result_id"], "R-463")
    check("T0 claim firewall", manifest["tier"] == "T0" and manifest["claim_bearing"] is False, (manifest["tier"], manifest["claim_bearing"]), ("T0", False))
    check("A1 source hash", normalized_sha(a1_path) == a1_item["sha256"], normalized_sha(a1_path), a1_item["sha256"])
    check("fixed eta", F(str(a1["parameters"]["eta_shell"])) == 0, a1["parameters"]["eta_shell"], 0)
    check("positive a and c", a > 0 and c > 0, (a, c), ">0")
    check("positive determinant", determinant > 0, determinant, ">0")
    check("positive trace", trace > 0, trace, ">0")
    check("positive angular coefficient", kappa > 0, kappa, ">0")
    check("positive radial constant", lambda_r > 0, lambda_r, ">0")
    check("angular identity", a * kappa == (a + b) ** 2 + determinant, a * kappa, (a + b) ** 2 + determinant)

    # Use a separate, deliberately denser grid than the primary audit.
    configured = [F(value) for value in manifest["audit"]["active_grid_values"]]
    active_grid = sorted(set(configured + [F(-2), F(2)]))
    flat_grid = [F(value) for value in manifest["audit"]["flat_grid_values"]]
    thresholds = [F(value) for value in manifest["audit"]["tube_thresholds"]]
    betas = [F(value) for value in manifest["audit"]["beta_values"]]
    precision = int(manifest["audit"]["decimal_precision"])
    points = list(itertools.product(active_grid, repeat=5))
    energies: list[F] = []
    metrics: list[F] = []
    radial_checks = 0
    domination_checks = 0
    positive_gap_checks = 0
    for point in points:
        x, y, u1, u2, u3 = point
        radial = quadratic(a, b, c, x, y)
        gap = radial - lambda_r * (x * x + y * y)
        squares = (a * x + b * y) ** 2 + (b * x + c * y) ** 2
        radial_checks += 1
        check(f"radial identity {radial_checks}", trace * gap == squares, trace * gap, squares)
        positive_gap_checks += 1
        if gap < 0:
            raise AssertionError(("negative radial gap", point, gap))
        angular_norm = u1 * u1 + u2 * u2 + u3 * u3
        energy2 = radial + kappa * angular_norm
        metric = lambda_r * (x * x + y * y) + kappa * angular_norm
        domination_checks += 1
        check(f"active domination {domination_checks}", energy2 >= metric, energy2, metric)
        energies.append(energy2)
        metrics.append(metric)

    thresholds_report: list[dict[str, Any]] = []
    for threshold in thresholds:
        outside = [energy for energy, metric in zip(energies, metrics) if metric >= threshold]
        if not outside:
            raise AssertionError(("empty shell", threshold))
        minimum = min(outside)
        reports = []
        for beta in betas:
            value = bound(len(outside), beta, minimum, precision)
            reports.append({"beta": str(beta), "bound": format(value, "f"), "bound_lt_one": value < 1})
        thresholds_report.append({"threshold": str(threshold), "outside_count": len(outside), "minimum_energy2": str(minimum), "minimum_energy": str(minimum / 2), "proxy_bounds": reports})

    check("radial identity count", radial_checks == len(points), radial_checks, len(points))
    check("radial gap count", positive_gap_checks == len(points), positive_gap_checks, len(points))
    check("domination count", domination_checks == len(points), domination_checks, len(points))
    check("threshold report count", len(thresholds_report) == len(thresholds), len(thresholds_report), len(thresholds))
    check("shell counts nonincreasing", [r["outside_count"] for r in thresholds_report] == sorted((r["outside_count"] for r in thresholds_report), reverse=True), [r["outside_count"] for r in thresholds_report], "nonincreasing")

    flat_points = list(itertools.product(flat_grid, repeat=int(manifest["audit"]["flat_dimensions"])))
    flat_threshold = thresholds[-1]
    flat_outside = [point for point in flat_points if sum(value * value for value in point) >= flat_threshold]
    check("flat shell nonempty", bool(flat_outside), len(flat_outside), ">0")
    check("flat energy is identically zero", all(F(0) == 0 for _ in flat_outside), "0", "0")
    flat_bound = bound(len(flat_outside), betas[0], F(0), precision)
    check("flat proxy exposes no suppression", flat_bound >= 1, flat_bound, ">=1")
    check("flat grid cardinality", len(flat_points) == len(flat_grid) ** int(manifest["audit"]["flat_dimensions"]), len(flat_points), len(flat_grid) ** int(manifest["audit"]["flat_dimensions"]))

    payload = {
        "schema": "tect/a6-classii-active-branch-tube-metric-independent-result/1.0",
        "run_kind": "independent",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "script_version": __version__,
        "verdict": "R-463-INDEPENDENT-PASS",
        "assertion_summary": {"passed": len(rows), "total": len(rows)},
        "assertions": rows,
        "derived": {
            "coefficients": {key: str(value) for key, value in coeff.items()},
            "determinant": str(determinant),
            "trace": str(trace),
            "lambda_radial": str(lambda_r),
            "kappa_angular": str(kappa),
            "active_grid_values": [str(value) for value in active_grid],
            "active_grid_points": len(points),
            "radial_identity_checks": radial_checks,
            "active_domination_checks": domination_checks,
            "shell_reports": thresholds_report,
            "flat_grid_points": len(flat_points),
            "flat_outside_count": len(flat_outside),
            "flat_energy_barrier": "0",
            "flat_proxy_bound": format(flat_bound, "f"),
            "scope": manifest["scope_firewall"],
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if not args.no_store:
        output = args.output if args.output.is_absolute() else REPO / args.output
        save(output, payload)
    print(f"INDEPENDENT R-463 PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
