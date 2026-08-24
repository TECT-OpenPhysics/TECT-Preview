#!/usr/bin/env python3
"""Primary audit for the bounded-cutoff Dyson shell and modular scale bridge.

The package separates the bounded interaction-picture first-passage estimate
from the still-open exact-Q3 modular-history and unbounded-tail hypotheses.
All numerical rows are derived from the manifest fixture.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_bounded_cutoff_dyson_shell_modular_scale"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-primary-{SLUG}" / "primary.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
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


def rat(value: str | int | float) -> Fraction:
    return Fraction(str(value))


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    scope = manifest["scope"]
    audit = Audit()

    audit.check("identity", manifest["exploration_id"] == "EXP-001091" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001091/T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("scope firewall", scope["bounded_cutoff_dyson_envelope_closed"] and scope["scale_balance_closed"] and not scope["actual_q3_modular_history_envelope_closed"] and not scope["common_alpha_closed"], scope, "bounded bridge only", "scope")

    degree = rat(fixture["degree"])
    hbar = rat(fixture["hbar"])
    time = rat(fixture["time"])
    v0 = rat(fixture["v0"])
    v2 = rat(fixture["v2"])
    modular_multiplier = rat(fixture["modular_multiplier"])
    base = rat(fixture["weight_base"])
    alpha = rat(fixture["alpha"])
    dimension = int(fixture["dimension"])
    static_a = [rat(fixture["static_a0"]), rat(fixture["static_a1"])]
    static_m = [int(fixture["static_m0"]), int(fixture["static_m1"])]
    static_c = [rat(fixture["static_constant0"]), rat(fixture["static_constant1"])]
    orientation_factor = rat(fixture["orientation_factor"])
    radii = [int(value) for value in fixture["radius_values"]]

    audit.check("positive graph degree", degree == 6 and degree > 0, degree, 6, "fixture")
    audit.check("positive interaction coefficients", v0 > 0 and v2 > 0, [v0, v2], ">0", "fixture")
    audit.check("weight base", base > 1, base, ">1", "fixture")
    audit.check("sublinear scale", 0 < alpha and 2 * alpha < 1, alpha, "0<alpha<1/2", "scale")
    audit.check("orientation count", orientation_factor == 2, orientation_factor, 2, "two orientations")

    # The coefficient of L^2 in b*lambda_L and in the modular comparison.
    kappa0 = base * 2 * degree * time * v2 / hbar
    kappa1 = kappa0 * modular_multiplier
    margins = [static_a[0] - kappa0, static_a[1] - kappa1]
    audit.check("static margin D", margins[0] > 0, margins[0], ">0", "scale balance")
    audit.check("static margin delta-D", margins[1] > 0, margins[1], ">0", "scale balance")
    audit.check("factorial exponent", 2 * alpha - 1 < 0, 2 * alpha - 1, "<0", "scale balance")

    rows: list[dict[str, Any]] = []
    for radius in radii:
        root = round(radius ** (1.0 / dimension))
        audit.check(f"R={radius} perfect scale", root**dimension == radius, root**dimension, radius, "scale fixture")
        L = rat(root)
        volume_factor = rat(radius) ** int(dimension)
        interaction_bound = v0 + v2 * L * L
        lambda_l = 2 * degree * time * interaction_bound / hbar
        lambda_modular = modular_multiplier * lambda_l
        # Weighted first-passage tail: sum_{n>=R} lambda^n/n! <= b^{-R} exp(b lambda).
        dynamic_log = math.log(float(orientation_factor)) + float(base * lambda_l - rat(radius) * rat(base).numerator / rat(base).denominator)
        # The preceding expression is intentionally evaluated from exact rationals;
        # use the equivalent real logarithmic form for non-unit bases below.
        dynamic_log = math.log(float(orientation_factor)) + float(base * lambda_l) - float(radius) * math.log(float(base))
        modular_dynamic_log = math.log(float(orientation_factor)) + float(base * lambda_modular) - float(radius) * math.log(float(base))
        static_logs = []
        for index in range(2):
            exponent = -(float(margins[index]) * float(L * L))
            static_logs.append(math.log(float(static_c[index]) * float(orientation_factor)) + float(dimension) * math.log(radius) + static_m[index] * math.log(root) + exponent)
        all_logs = [dynamic_log, modular_dynamic_log, *static_logs]
        audit.check(f"R={radius} finite logs", all(math.isfinite(value) for value in all_logs), all_logs, "finite", "arithmetic")
        rows.append({
            "radius": radius,
            "cutoff": root,
            "interaction_bound": float(interaction_bound),
            "lambda_L": float(lambda_l),
            "lambda_modular_L": float(lambda_modular),
            "D_dynamic_log_bound": dynamic_log,
            "delta_D_dynamic_log_bound": modular_dynamic_log,
            "D_static_log_bound": static_logs[0],
            "delta_D_static_log_bound": static_logs[1],
            "D_dynamic_bound": math.exp(dynamic_log),
            "delta_D_dynamic_bound": math.exp(modular_dynamic_log),
            "D_static_bound": math.exp(static_logs[0]),
            "delta_D_static_bound": math.exp(static_logs[1]),
        })

    audit.check("radius sequence", [row["radius"] for row in rows] == radii, [row["radius"] for row in rows], radii, "scale fixture")
    audit.check("large-scale decay fixture", rows[-1]["D_dynamic_log_bound"] < rows[0]["D_dynamic_log_bound"] and rows[-1]["delta_D_dynamic_log_bound"] < rows[0]["delta_D_dynamic_log_bound"], [rows[0]["D_dynamic_log_bound"], rows[-1]["D_dynamic_log_bound"], rows[0]["delta_D_dynamic_log_bound"], rows[-1]["delta_D_dynamic_log_bound"]], "decreasing", "arithmetic")
    audit.check("static decay fixture", rows[-1]["D_static_log_bound"] < rows[0]["D_static_log_bound"] and rows[-1]["delta_D_static_log_bound"] < rows[0]["delta_D_static_log_bound"], [rows[0]["D_static_log_bound"], rows[-1]["D_static_log_bound"], rows[0]["delta_D_static_log_bound"], rows[-1]["delta_D_static_log_bound"]], "decreasing", "arithmetic")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-BOUNDED-CUTOFF-DYSON-SHELL-MODULAR-SCALE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "derived": {
            "degree": str(degree),
            "lambda_L_formula": "2*Delta*T*(v0+v2*L^2)/hbar",
            "kappa0": str(kappa0),
            "kappa1": str(kappa1),
            "static_margins": [str(value) for value in margins],
            "alpha": str(alpha),
            "two_alpha_minus_one": str(2 * alpha - 1),
            "rows": rows,
            "bounded_cutoff_dyson_envelope_closed": True,
            "scale_balance_closed": True,
            "actual_q3_modular_history_envelope_closed": False,
            "actual_q3_unbounded_tail_comparison_closed": False,
            "volume_uniform_direct_d_delta_d_closed": False,
            "common_alpha_closed": False,
        },
        "hypotheses": manifest["bounded_cutoff_hypotheses"],
        "boundary": scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY BOUNDED-CUTOFF-DYSON-SHELL PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
