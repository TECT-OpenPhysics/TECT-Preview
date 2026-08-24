#!/usr/bin/env python3
"""Independent reconstruction of the EXP-001091 scale bridge."""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre_a_cp1_st8_q3lock_bounded_cutoff_dyson_shell_modular_scale_manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-26-independent-pre_a_cp1_st8_q3lock_bounded_cutoff_dyson_shell_modular_scale/independent.json"


def f(value: str | int | float) -> Fraction:
    return Fraction(str(value))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def run() -> dict[str, Any]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cfg = data["fixture"]
    rows: list[dict[str, Any]] = []

    def ok(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    ok("identity", data["exploration_id"] == "EXP-001091" and data["task_id"] == "T-054", [data["exploration_id"], data["task_id"]], "EXP-001091/T-054", "provenance")
    ok("finite-only scope", data["claim_bearing"] is False and not data["scope"]["actual_q3_modular_history_envelope_closed"], data["scope"], "claim-nonbearing/open modular input", "scope")

    delta = f(cfg["degree"])
    hbar = f(cfg["hbar"])
    horizon = f(cfg["time"])
    base = f(cfg["weight_base"])
    v0 = f(cfg["v0"])
    v2 = f(cfg["v2"])
    modular_factor = f(cfg["modular_multiplier"])
    alpha = f(cfg["alpha"])
    dim = int(cfg["dimension"])
    a0, a1 = f(cfg["static_a0"]), f(cfg["static_a1"])
    m0, m1 = int(cfg["static_m0"]), int(cfg["static_m1"])
    radii = [int(x) for x in cfg["radius_values"]]

    ok("degree fixture", delta == 6, delta, 6, "fixture")
    ok("scale interval", 0 < alpha < f("1/2"), alpha, "(0,1/2)", "scale")
    coefficient = base * 2 * delta * horizon * v2 / hbar
    modular_coefficient = coefficient * modular_factor
    ok("D margin", a0 > coefficient, a0 - coefficient, ">0", "scale")
    ok("delta-D margin", a1 > modular_coefficient, a1 - modular_coefficient, ">0", "scale")
    ok("factorial exponent", 2 * alpha - 1 < 0, 2 * alpha - 1, "<0", "scale")

    computed: list[dict[str, Any]] = []
    for radius in radii:
        cutoff = int(round(radius ** (1.0 / dim)))
        ok(f"R={radius} cube", cutoff**dim == radius, cutoff**dim, radius, "scale fixture")
        L = f(cutoff)
        V = v0 + v2 * L * L
        lam = 2 * delta * horizon * V / hbar
        lam1 = modular_factor * lam
        log_d = math.log(2.0) + float(base * lam) - radius * math.log(float(base))
        log_1 = math.log(2.0) + float(base * lam1) - radius * math.log(float(base))
        static_d = math.log(float(f(cfg["orientation_factor"]))) + dim * math.log(radius) + m0 * math.log(cutoff) - float((a0 - coefficient) * L * L)
        static_1 = math.log(float(f(cfg["orientation_factor"]))) + dim * math.log(radius) + m1 * math.log(cutoff) - float((a1 - modular_coefficient) * L * L)
        values = [log_d, log_1, static_d, static_1]
        ok(f"R={radius} logs finite", all(math.isfinite(x) for x in values), values, "finite", "arithmetic")
        computed.append({"radius": radius, "cutoff": cutoff, "interaction_bound": float(V), "lambda_L": float(lam), "lambda_modular_L": float(lam1), "D_dynamic_log_bound": log_d, "delta_D_dynamic_log_bound": log_1, "D_static_log_bound": static_d, "delta_D_static_log_bound": static_1, "D_dynamic_bound": math.exp(log_d), "delta_D_dynamic_bound": math.exp(log_1), "D_static_bound": math.exp(static_d), "delta_D_static_bound": math.exp(static_1)})

    scale_rows = computed
    ok("dynamic decay", scale_rows[-1]["D_dynamic_log_bound"] < scale_rows[0]["D_dynamic_log_bound"] and scale_rows[-1]["delta_D_dynamic_log_bound"] < scale_rows[0]["delta_D_dynamic_log_bound"], [scale_rows[0]["D_dynamic_log_bound"], scale_rows[-1]["D_dynamic_log_bound"]], "decreasing", "arithmetic")
    ok("static decay", scale_rows[-1]["D_static_log_bound"] < scale_rows[0]["D_static_log_bound"] and scale_rows[-1]["delta_D_static_log_bound"] < scale_rows[0]["delta_D_static_log_bound"], [scale_rows[0]["D_static_log_bound"], scale_rows[-1]["D_static_log_bound"]], "decreasing", "arithmetic")

    passed = len(rows)
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-BOUNDED-CUTOFF-DYSON-SHELL-MODULAR-SCALE", "claim_id": data["claim_ids"][0], "task_id": data["task_id"], "exploration_id": data["exploration_id"], "verdict": "PASS", "passed": passed, "total": passed, "failed": 0, "assertions": rows, "derived": {"kappa0": str(coefficient), "kappa1": str(modular_coefficient), "alpha": str(alpha), "two_alpha_minus_one": str(2 * alpha - 1), "rows": scale_rows, "bounded_cutoff_dyson_envelope_closed": True, "scale_balance_closed": True, "actual_q3_modular_history_envelope_closed": False, "actual_q3_unbounded_tail_comparison_closed": False, "volume_uniform_direct_d_delta_d_closed": False, "common_alpha_closed": False}, "boundary": data["scope"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        write_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INDEPENDENT BOUNDED-CUTOFF-DYSON-SHELL PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
