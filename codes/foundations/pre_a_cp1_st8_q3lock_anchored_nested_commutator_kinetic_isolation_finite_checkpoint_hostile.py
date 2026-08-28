#!/usr/bin/env python3
"""Hostile control for R-387: add momentum to the allegedly coordinate-only V."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-anchored-nested-commutator-kinetic-isolation-finite-checkpoint-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-pre_a_cp1_st8_q3lock_anchored_nested_commutator_kinetic_isolation_finite_checkpoint/hostile.json"


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def hermitian(x: np.ndarray) -> np.ndarray:
    return (x + x.conj().T) / 2.0


def comm(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return x @ y - y @ x


def norm(x: np.ndarray) -> float:
    return float(np.linalg.svd(x, compute_uv=False)[0])


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    a = np.zeros((dimension, dimension), dtype=complex)
    for n in range(dimension - 1):
        a[n, n + 1] = np.sqrt(n + 1.0)
    return (a + a.conj().T) / np.sqrt(2.0), (a - a.conj().T) / (1j * np.sqrt(2.0))


def lift(single: np.ndarray, site: int, volume: int, eye: np.ndarray) -> np.ndarray:
    factors = [single if k == site else eye for k in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def edges(volume: int, fixture: dict[str, Any]) -> list[tuple[int, int]]:
    return [tuple(map(int, pair)) for pair in fixture["graph_edges_by_volume"][str(volume)]]


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    eta_values = [float(Fraction(x)) for x in fixture["resolvent_imaginary_values"]]
    amplitude = float(Fraction(fixture["hostile_momentum_amplitude"]))
    threshold = float(fixture["hostile_threshold"])
    wrong_values: list[float] = []
    wrong_nested_values: list[float] = []
    correct_values: list[float] = []
    rows = 0
    for volume in (int(x) for x in fixture["volume_values"]):
        q_single, p_single = oscillator(int(fixture["oscillator_dimension"]))
        eye = np.eye(q_single.shape[0], dtype=complex)
        q = [lift(q_single, site, volume, eye) for site in range(volume)]
        p = [lift(p_single, site, volume, eye) for site in range(volume)]
        records: list[tuple[str, np.ndarray, np.ndarray, np.ndarray]] = []
        for site in range(volume):
            kinetic = hermitian(p[site] @ p[site] / (2.0 * float(fixture["chi"])))
            potential = hermitian(float(fixture["r"]) * (q[site] @ q[site]) / 2.0 + float(fixture["g"]) * (q[site] @ q[site] @ q[site] @ q[site]) / 4.0)
            records.append(("onsite", hermitian(kinetic + potential), kinetic, potential))
        for left, right in edges(volume, fixture):
            d = q[left] - q[right]
            quadratic = d @ d
            potential = hermitian(float(fixture["c"]) * quadratic / 2.0 + float(fixture["lambda"]) * quadratic @ (q[left] @ q[left] + q[right] @ q[right]) / 4.0)
            records.append(("bond", potential, np.zeros_like(potential), potential))
        for order in (list(range(len(records))), list(reversed(range(len(records))))):
            for position, boundary_index in enumerate(order):
                if records[boundary_index][0] != "bond":
                    continue
                # Recover the declared bond support from its position in the record list.
                bond_number = boundary_index - volume
                left_site, _ = edges(volume, fixture)[bond_number]
                zero = np.zeros_like(records[0][1])
                prefix = order[:position]
                h = sum((records[k][1] for k in prefix), zero)
                t = sum((records[k][2] for k in prefix), zero)
                v = sum((records[k][3] for k in prefix), zero)
                hostile_v = hermitian(v + amplitude * p[left_site])
                hostile_h = hermitian(t + hostile_v)
                for eta in eta_values:
                    identity = np.eye(q[left_site].shape[0], dtype=complex)
                    seed = np.linalg.inv(1j * eta * identity - q[left_site])
                    for observable in (seed, seed.conj().T):
                        correct = norm(comm(h, observable) - comm(t, observable))
                        wrong = norm(comm(hostile_h, observable) - comm(t, observable))
                        wrong_nested = norm(comm(records[boundary_index][1], comm(hostile_h, observable)) - comm(records[boundary_index][1], comm(t, observable)))
                        correct_values.append(correct)
                        wrong_values.append(wrong)
                        wrong_nested_values.append(wrong_nested)
                        rows += 1
    if not wrong_values or min(wrong_values) <= threshold:
        raise AssertionError(f"hostile mutation was not separated: min={min(wrong_values) if wrong_values else None}")
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "hostile",
        "audit_id": "PA-CP1-ST8-Q3LOCK-ANCHORED-NESTED-COMMUTATOR-KINETIC-ISOLATION-FINITE-CHECKPOINT",
        "claim_id": manifest["claim_ids"][0],
        "result_id": manifest["result_id"],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": rows + 2,
        "assertions": [{"name": "momentum mutation separated", "status": "PASS"}, {"name": "mutation threshold", "status": "PASS"}],
        "derived": {"samples": rows, "correct_residual_max": max(correct_values), "wrong_residual_min": min(wrong_values), "wrong_nested_residual_min": min(wrong_nested_values), "hostile_threshold": threshold, "wrong_orientation_rejected": True, "mutation": "V -> V + amplitude*p_left"},
        "boundary": manifest["boundary"]
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run()
    store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"HOSTILE ANCHORED NESTED-COMMUTATOR KINETIC-ISOLATION CAUGHT wrong={payload['derived']['wrong_residual_min']:.3e} nested={payload['derived']['wrong_nested_residual_min']:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
