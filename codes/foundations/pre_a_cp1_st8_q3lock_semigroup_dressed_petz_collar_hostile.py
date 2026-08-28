#!/usr/bin/env python3
"""Hostile mutation lane for the R-397 smooth collar.

The lane intentionally removes normalization, replaces the smooth filter by
a hard ground-state projector, changes one exponential leg, and drops the
two displacement terms from the transport budget.  A final order sentinel
records that the genuine scalar semigroup is commutative; reversing its
parameters is therefore harmless and must not be mislabelled as a failure.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-semigroup-dressed-petz-collar-finite-discriminator-manifest.json"
PARENT_PATH = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_quantum_markov_blanket_boundary_transfer.py"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_semigroup_dressed_petz_collar" / "hostile.json"


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location("r391_semigroup_hostile_parent", PARENT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load finite Gibbs/Petz parent")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PARENT = load_parent()


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def distance(left: np.ndarray, right: np.ndarray) -> float:
    return float(0.5 * np.sum(np.abs(np.linalg.eigvalsh(PARENT.hermitian(left - right)).real)))


def local_filter(dimension: int, width: int, scale: float, fixture: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    values, vectors = np.linalg.eigh(PARENT.build_system(dimension, width, fixture))
    shifted = values - float(values.min())
    smooth = PARENT.hermitian((vectors * np.exp(-scale * shifted / 2.0)) @ vectors.conj().T)
    one_leg = PARENT.hermitian((vectors * np.exp(-scale * shifted)) @ vectors.conj().T)
    hard = PARENT.hermitian(np.outer(vectors[:, 0], vectors[:, 0].conj()))
    return shifted, smooth, one_leg, hard


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    tolerance = float(fixture["numerical_tolerance"])
    semigroup_tolerance = float(fixture["semigroup_tolerance"])
    threshold = float(fixture["hostile_threshold"])
    scales = [float(Fraction(value)) for value in fixture["filter_scales"]]
    scale = max(scales)
    dimension, volume, beta = 3, 3, max(float(Fraction(value)) for value in fixture["beta_values"])
    partition = PARENT.tripartitions(volume, [1, 2], [1, 2])[0]
    values, vectors = np.linalg.eigh(PARENT.build_system(dimension, volume, fixture))
    rho = PARENT.gibbs_from_spectrum(values, vectors, beta)
    core, buffer, environment = partition["core"], partition["buffer"], partition["environment"]
    dimensions = (dimension**len(core), dimension**len(buffer), dimension**len(environment))
    rho_abc = PARENT.partial_trace_sites(rho, dimension, volume, core + buffer + environment)
    rho_ab = PARENT.partial_trace_groups(rho_abc, list(dimensions), [0, 1])
    shifted, smooth, one_leg, hard = local_filter(dimension, int(partition["core_width"]), scale, fixture)
    identity_bc = np.eye(dimensions[1] * dimensions[2], dtype=complex)
    smooth_lift = np.kron(smooth, identity_bc)
    raw = PARENT.hermitian(smooth_lift @ rho_abc @ smooth_lift)
    mass = float(np.trace(raw).real)
    sigma = PARENT.hermitian(raw / mass)
    sigma_ab = PARENT.partial_trace_groups(sigma, list(dimensions), [0, 1])
    sigma_b = PARENT.partial_trace_groups(sigma, list(dimensions), [1])
    sigma_bc = PARENT.partial_trace_groups(sigma, list(dimensions), [1, 2])
    rec_sigma = PARENT.petz_recovery(sigma_ab, sigma_bc, sigma_b, dimensions, float(fixture["positivity_tolerance"]))
    rec_rho = PARENT.petz_recovery(rho_ab, sigma_bc, sigma_b, dimensions, float(fixture["positivity_tolerance"]))
    delta_abc = distance(rho_abc, sigma)
    delta_ab = distance(rho_ab, sigma_ab)
    projected = distance(sigma, rec_sigma)
    transported = distance(rho_abc, rec_rho)
    genuine_budget = projected + delta_abc + delta_ab
    mutated_budget = projected
    wrong_leg_residual = float(np.linalg.norm(smooth - one_leg, ord="fro"))
    hard_residual = float(np.linalg.norm(smooth - hard, ord="fro"))
    _, smaller_s, _, _ = local_filter(dimension, int(partition["core_width"]), min(scales), fixture)
    order_residual = float(np.linalg.norm(smooth @ smaller_s - smaller_s @ smooth, ord="fro"))
    checks = [
        {"name": "normalization omission caught", "status": "PASS" if 1.0 - mass > threshold else "FAIL", "actual": 1.0 - mass, "expected": f">{threshold}"},
        {"name": "one-leg exponential mutation caught", "status": "PASS" if wrong_leg_residual > threshold else "FAIL", "actual": wrong_leg_residual, "expected": f">{threshold}"},
        {"name": "hard-projector substitution caught", "status": "PASS" if hard_residual > threshold else "FAIL", "actual": hard_residual, "expected": f">{threshold}"},
        {"name": "genuine triangle budget", "status": "PASS" if transported <= genuine_budget + tolerance else "FAIL", "actual": [transported, genuine_budget], "expected": "transported <= genuine budget"},
        {"name": "omitted displacement terms caught", "status": "PASS" if transported > mutated_budget + threshold else "FAIL", "actual": [transported, mutated_budget, transported - mutated_budget], "expected": "transported > projected-only budget"},
        {"name": "reverse-order sentinel", "status": "PASS" if order_residual <= semigroup_tolerance else "FAIL", "actual": order_residual, "expected": f"<={semigroup_tolerance} because scalar semigroup commutes"}
    ]
    if any(item["status"] != "PASS" for item in checks):
        raise AssertionError(checks)
    derived = {"volume": volume, "dimension": dimension, "beta": beta, "core": core, "buffer": buffer, "environment": environment, "scale": scale, "shifted_max": float(np.max(shifted)), "projection_mass": mass, "normalization_trace_gap": 1.0 - mass, "delta_abc": delta_abc, "delta_ab": delta_ab, "projected_error": projected, "transported_error": transported, "genuine_budget": genuine_budget, "mutated_budget_without_displacements": mutated_budget, "mutation_gap": transported - mutated_budget, "one_leg_residual": wrong_leg_residual, "hard_projector_residual": hard_residual, "reverse_order_residual": order_residual}
    payload = {"schema": "tect/pre-a-r397-hostile/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-397", "exploration_id": "EXP-001241", "verdict": "PASS", "checks": checks, "derived": derived}
    save(output, payload)
    print(f"R-397 HOSTILE PASS {len(checks)}/{len(checks)} normalization_gap={derived['normalization_trace_gap']:.6g} one_leg={wrong_leg_residual:.6g} hard={hard_residual:.6g} mutation_gap={derived['mutation_gap']:.6g}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    run(parser.parse_args().output)


if __name__ == "__main__":
    main()
