#!/usr/bin/env python3
"""Hostile mutation for the R-386 coordinate-resolvent commutation anchor."""

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
SLUG = "pre_a_cp1_st8_q3lock_relative_cocycle_coordinate_resolvent_zero_time_anchor_finite_checkpoint"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-relative-cocycle-coordinate-resolvent-zero-time-anchor-finite-checkpoint-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "hostile.json"


def save_json(path: Path, payload: dict[str, Any]) -> None:
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


def sym(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) * 0.5


def oscillator(size: int) -> tuple[np.ndarray, np.ndarray]:
    ladder = np.diag(np.sqrt(np.arange(1.0, float(size))), 1).astype(complex)
    return (ladder + ladder.conj().T) / np.sqrt(2.0), (ladder - ladder.conj().T) / (1j * np.sqrt(2.0))


def tensor(local: np.ndarray, site: int, volume: int, size: int) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    eye = np.eye(size, dtype=complex)
    for index in range(volume):
        result = np.kron(result, local if index == site else eye)
    return result


def edges(volume: int, fixture: dict[str, Any]) -> list[tuple[int, int]]:
    return [tuple(map(int, edge)) for edge in fixture["graph_edges_by_volume"][str(volume)]]


def build(volume: int, size: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], list[np.ndarray], list[dict[str, Any]]]:
    q_local, p_local = oscillator(size)
    q = [tensor(q_local, site, volume, size) for site in range(volume)]
    p = [tensor(p_local, site, volume, size) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    terms = [sym(p_i @ p_i / (2.0 * chi) + r * (q_i @ q_i) / 2.0 + g * (q_i @ q_i @ q_i @ q_i) / 4.0) for q_i, p_i in zip(q, p)]
    specs = [{"kind": "onsite", "support": [site]} for site in range(volume)]
    for left, right in edges(volume, fixture):
        d = q[left] - q[right]
        terms.append(sym(c * (d @ d) / 2.0 + lam * (d @ d) @ (q[left] @ q[left] + q[right] @ q[right]) / 4.0))
        specs.append({"kind": "bond", "support": [left, right]})
    return q, p, [{"kind": spec["kind"], "support": spec["support"], "term": term} for spec, term in zip(specs, terms)]


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    eta_values = [float(Fraction(item)) for item in fixture["resolvent_imaginary_values"]]
    hbar = float(Fraction(fixture["hbar"]))
    mutation = float(Fraction(fixture["hostile_momentum_amplitude"]))
    threshold = float(fixture["hostile_threshold"])
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001229" and manifest["result_id"] == "R-386" and not manifest["claim_bearing"], [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"],], "EXP-001229/R-386/false", "provenance")
    correct_max = 0.0
    wrong_min = float("inf")
    wrong_first_min = float("inf")
    samples = 0
    for volume in map(int, fixture["volume_values"]):
        q_ops, p_ops, term_specs = build(volume, int(fixture["oscillator_dimension"]), fixture)
        for order_name, order in (("forward", list(range(len(term_specs)))), ("reverse", list(reversed(range(len(term_specs)))))):
            for position, term_index in enumerate(order):
                if term_specs[term_index]["kind"] != "bond":
                    continue
                base = np.zeros_like(term_specs[0]["term"])
                for index in order[:position]:
                    base = base + term_specs[index]["term"]
                boundary = term_specs[term_index]["term"]
                for site in range(volume):
                    for eta in eta_values:
                        identity = np.eye(q_ops[site].shape[0], dtype=complex)
                        seed = np.linalg.inv(1j * eta * identity - q_ops[site])
                        for seed_name, observable in (("A", seed), ("A_star", seed.conj().T)):
                            correct = norm(boundary @ observable - observable @ boundary)
                            bad_boundary = boundary + mutation * p_ops[site]
                            wrong = norm(bad_boundary @ observable - observable @ bad_boundary)
                            wrong_first = norm((1j / hbar) * (bad_boundary @ observable - observable @ bad_boundary))
                            correct_max = max(correct_max, correct)
                            wrong_min = min(wrong_min, wrong)
                            wrong_first_min = min(wrong_first_min, wrong_first)
                            samples += 1
                            check(f"V={volume} {order_name} pos={position} site={site} eta={eta} {seed_name} wrong mutation", wrong > threshold, wrong, f">{threshold}", "hostile mutation")
    check("correct coordinate anchor", correct_max <= threshold, correct_max, f"<={threshold}", "hostile control")
    check("wrong first variation", wrong_first_min > threshold, wrong_first_min, f">{threshold}", "hostile mutation")
    derived = {"correct_residual_max": correct_max, "wrong_residual_min": wrong_min, "wrong_first_variation_min": wrong_first_min, "mutation_amplitude": mutation, "mutation_threshold": threshold, "samples": samples, "finite_only": True, "wrong_orientation_rejected": bool(wrong_min > threshold and wrong_first_min > threshold)}
    check("mutation rejected", derived["wrong_orientation_rejected"], derived["wrong_orientation_rejected"], True, "hostile mutation")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "hostile", "audit_id": "PA-CP1-ST8-Q3LOCK-RELATIVE-COCYCLE-COORDINATE-RESOLVENT-ZERO-TIME-ANCHOR-FINITE-CHECKPOINT", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": derived, "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        save_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"HOSTILE RELATIVE-COCYCLE ZERO-TIME-ANCHOR CAUGHT wrong={payload['derived']['wrong_residual_min']:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
