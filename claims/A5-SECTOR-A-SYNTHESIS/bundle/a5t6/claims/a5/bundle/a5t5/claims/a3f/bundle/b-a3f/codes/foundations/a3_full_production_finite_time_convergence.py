#!/usr/bin/env python3
"""Stage-2 finite-time convergence audit for the full-production P3 claim.

Two error sources are deliberately separated.  A forced manufactured
semidiscrete trajectory checks the declared RK4 time order.  An unforced
gradient-flow trajectory on several Fourier grids checks spatial self-
convergence and energy decay at a fixed small time step.  The spatial reference
uses the same backend at two higher resolutions and is not an independent
continuum-residual implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Any, Callable

import numpy as np

import a3_full_production_spatial_consistency as spatial

__version__ = "1.0.0"
__first_issued__ = "2026-07-17"
__version_issued__ = "2026-07-17"

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"
MANIFEST = CLAIM / "discretization_manifest.json"
P1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
BACKEND_PATH = REPO / "codes" / "foundations" / "n001_variational_backend.py"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-17-finite-time-convergence" / "result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_backend() -> Any:
    spec = importlib.util.spec_from_file_location("p3_time_backend", BACKEND_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load pinned P1 backend")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def manufactured_time_field(n: int, time: float, params: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    initial = spatial.manufactured_field(n, params)
    mean = np.mean(initial, axis=(-3, -2, -1), keepdims=True)
    transient = math.exp(-time) * (initial - mean)
    return mean + transient, -transient


def rk4_step(value: np.ndarray, time: float, step: float, rhs: Callable[[float, np.ndarray], np.ndarray]) -> np.ndarray:
    k1 = rhs(time, value)
    k2 = rhs(time + 0.5 * step, value + 0.5 * step * k1)
    k3 = rhs(time + 0.5 * step, value + 0.5 * step * k2)
    k4 = rhs(time + step, value + step * k3)
    return value + (step / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def integrate(value: np.ndarray, final_time: float, step: float, rhs: Callable[[float, np.ndarray], np.ndarray], energy: Callable[[np.ndarray], float] | None = None) -> tuple[np.ndarray, list[float]]:
    count_float = final_time / step
    count = int(round(count_float))
    if not math.isclose(count * step, final_time, rel_tol=0.0, abs_tol=1e-14):
        raise ValueError("final_time must be an integer multiple of step")
    energies = [energy(value)] if energy is not None else []
    time = 0.0
    for _ in range(count):
        value = rk4_step(value, time, step, rhs)
        time += step
        if energy is not None:
            energies.append(energy(value))
    return value, energies


def orders(steps_or_grids: list[float], errors: list[float], inverse: bool) -> list[float]:
    output = []
    for i in range(len(errors) - 1):
        ratio = steps_or_grids[i] / steps_or_grids[i + 1] if inverse else steps_or_grids[i + 1] / steps_or_grids[i]
        output.append(math.log(errors[i] / errors[i + 1]) / math.log(ratio))
    return output


def check(name: str, passed: bool, detail: str, assertions: list[dict[str, Any]]) -> None:
    assertions.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    p1 = json.loads(P1_MANIFEST.read_text(encoding="utf-8"))
    params = dict(p1["parameters"])
    params["eta_shell"] = 0.0
    backend = load_backend()
    stage = manifest["stage2"]
    acceptance = stage["acceptance"]

    time_case = stage["time_manufactured"]
    time_grid = int(time_case["grid"])
    final_time = float(time_case["final_time"])
    initial, _ = manufactured_time_field(time_grid, 0.0, params)

    def forced_rhs(time: float, value: np.ndarray) -> np.ndarray:
        exact, exact_dt = manufactured_time_field(time_grid, time, params)
        source = exact_dt + backend.residual(exact, params)
        return -backend.residual(value, params) + source

    time_rows = []
    time_errors = []
    for step_value in time_case["time_steps"]:
        step = float(step_value)
        numerical, _ = integrate(initial.copy(), final_time, step, forced_rhs)
        exact, _ = manufactured_time_field(time_grid, final_time, params)
        error = spatial.relative_l2(numerical, exact, params)
        time_errors.append(error)
        time_rows.append({"step": step, "steps": int(round(final_time / step)), "relative_l2_error": error})
    time_orders = orders([float(value) for value in time_case["time_steps"]], time_errors, inverse=True)

    spatial_case = stage["unforced_cross_grid"]
    grids = [int(n) for n in spatial_case["grids"]]
    references = [int(n) for n in spatial_case["reference_grids"]]
    trajectory_time = float(spatial_case["final_time"])
    trajectory_step = float(spatial_case["time_step"])
    trajectories: dict[int, np.ndarray] = {}
    energy_histories: dict[int, list[float]] = {}
    for n in grids + references:
        start = spatial.manufactured_field(n, params)
        rhs = lambda _time, value: -backend.residual(value, params)
        trajectory, energies = integrate(start, trajectory_time, trajectory_step, rhs, energy=lambda value: backend.energy(value, params))
        trajectories[n] = trajectory
        energy_histories[n] = energies

    finest = references[-1]
    coarser = references[-2]
    spatial_rows = []
    spatial_errors = []
    reference_errors = []
    for n in grids:
        target = trajectories[n]
        projected_finest = spatial.project(trajectories[finest], n)
        projected_coarser = spatial.project(trajectories[coarser], n)
        error = spatial.relative_l2(target, projected_finest, params)
        reference_error = spatial.relative_l2(projected_coarser, projected_finest, params)
        spatial_errors.append(error)
        reference_errors.append(reference_error)
        spatial_rows.append({"grid": n, "trajectory_relative_l2_error": error, "reference_trajectory_relative_l2_error": reference_error})
    spatial_orders = orders([float(n) for n in grids], spatial_errors, inverse=False)

    energy_rows = []
    energy_monotone = True
    for n, values in energy_histories.items():
        scale = max(abs(values[0]), 1.0)
        slack = float(acceptance["energy_relative_slack"]) * scale
        maximum_increase = max((values[i + 1] - values[i] for i in range(len(values) - 1)), default=0.0)
        passed_here = maximum_increase <= slack
        energy_monotone = energy_monotone and passed_here
        energy_rows.append({"grid": n, "initial": values[0], "final": values[-1], "maximum_step_increase": maximum_increase, "allowed_slack": slack, "status": "PASS" if passed_here else "FAIL"})

    assertions: list[dict[str, Any]] = []
    check("backend_hash", sha256(BACKEND_PATH) == manifest["authority"]["p1_backend"]["sha256"], sha256(BACKEND_PATH), assertions)
    check("time_error_monotone", all(time_errors[i + 1] < time_errors[i] for i in range(len(time_errors) - 1)), f"errors={time_errors}", assertions)
    check("rk4_time_order", min(time_orders) >= float(acceptance["minimum_time_order"]), f"orders={time_orders}", assertions)
    check("final_time_error", time_errors[-1] <= float(acceptance["final_time_relative_error_max"]), f"final={time_errors[-1]:.6e}", assertions)
    check("trajectory_error_monotone", all(spatial_errors[i + 1] < spatial_errors[i] for i in range(len(spatial_errors) - 1)), f"errors={spatial_errors}", assertions)
    check("trajectory_spatial_order", min(spatial_orders) >= float(acceptance["minimum_spatial_order"]), f"orders={spatial_orders}", assertions)
    check("final_trajectory_error", spatial_errors[-1] <= float(acceptance["final_trajectory_relative_error_max"]), f"final={spatial_errors[-1]:.6e}", assertions)
    check("reference_trajectory_stable", max(reference_errors) <= float(acceptance["reference_trajectory_relative_error_max"]), f"max={max(reference_errors):.6e}", assertions)
    check("unforced_energy_nonincreasing", energy_monotone, f"rows={energy_rows}", assertions)
    check("time_and_space_errors_separated", "this isolates temporal order" in time_case["forcing"] and "report reference-grid uncertainty separately" in spatial_case["comparison"], "manifest records two distinct experiments", assertions)

    passed = sum(item["status"] == "PASS" for item in assertions)
    output = {
        "schema": "tect/a3-full-production-finite-time-result/1.0",
        "claim_id": manifest["claim_id"],
        "script_version": __version__,
        "verdict": "A3-FULL-FINITE-TIME-CONVERGENCE-PASS" if passed == len(assertions) else "A3-FULL-FINITE-TIME-CONVERGENCE-FAIL",
        "scope": "forced semidiscrete manufactured time-order test plus same-backend unforced cross-grid trajectory self-convergence; CPU complex128",
        "not_closed_here": ["independent continuum-residual implementation", "Hessian/Ritz convergence", "CPU/GPU and precision cross-check", "uniform continuum error theorem"],
        "time_manufactured": {"rows": time_rows, "observed_orders": time_orders},
        "unforced_cross_grid": {"rows": spatial_rows, "observed_orders": spatial_orders, "energy_rows": energy_rows},
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)}
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(assertions)} PASS")
    print(output["verdict"])
    print(f"Time errors: {time_errors}; orders: {time_orders}")
    print(f"Trajectory errors: {spatial_errors}; orders: {spatial_orders}")
    print(f"Evidence: {args.output.resolve()}")
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
