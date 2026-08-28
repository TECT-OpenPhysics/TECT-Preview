#!/usr/bin/env python3
"""Hostile control for R-390: replace the local Gibbs marginal by I/d^2."""

from __future__ import annotations

import argparse
import json
import os
import string
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_local_marginal_spectral_window_transfer"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-marginal-spectral-window-transfer-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "hostile.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
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


def sym(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def ladder(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    lower = np.zeros((dimension, dimension), dtype=complex)
    for column in range(1, dimension):
        lower[column - 1, column] = np.sqrt(float(column))
    return (lower + lower.conj().T) / np.sqrt(2.0), (lower - lower.conj().T) / (1j * np.sqrt(2.0))


def site_operator(single: np.ndarray, site: int, volume: int, dimension: int) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    identity = np.eye(dimension, dtype=complex)
    for index in range(volume):
        result = np.kron(result, single if index == site else identity)
    return result


def system(dimension: int, volume: int, fixture: dict[str, Any]) -> tuple[np.ndarray, list[np.ndarray], list[np.ndarray]]:
    q_single, p_single = ladder(dimension)
    qs = [site_operator(q_single, site, volume, dimension) for site in range(volume)]
    ps = [site_operator(p_single, site, volume, dimension) for site in range(volume)]
    hamiltonian = np.zeros((dimension**volume, dimension**volume), dtype=complex)
    for q, p in zip(qs, ps):
        hamiltonian += p @ p / (2.0 * float(fixture["chi"])) + float(fixture["r"]) * q @ q / 2.0 + float(fixture["g"]) * q @ q @ q @ q / 4.0
    for site in range(volume - 1):
        delta = qs[site] - qs[site + 1]
        delta2 = delta @ delta
        hamiltonian += float(fixture["c"]) * delta2 / 2.0 + float(fixture["lambda"]) * delta2 @ (qs[site] @ qs[site] + qs[site + 1] @ qs[site + 1]) / 4.0
    return sym(hamiltonian), qs, ps


def reduce_pair(state: np.ndarray, dimension: int, volume: int, start: int) -> np.ndarray:
    keep = [start, start + 1]
    rest = [index for index in range(volume) if index not in keep]
    labels = list(string.ascii_letters[: 2 * volume])
    for index in rest:
        labels[index + volume] = labels[index]
    subs = "".join(labels)
    output = "".join(labels[index] for index in keep) + "".join(labels[index + volume] for index in keep)
    tensor = np.einsum(f"{subs}->{output}", state.reshape([dimension] * (2 * volume)), optimize=True)
    return tensor.reshape(dimension * dimension, dimension * dimension)


def pair_embed(operator: np.ndarray, dimension: int, volume: int, start: int) -> np.ndarray:
    return np.kron(np.kron(np.eye(dimension**start, dtype=complex), operator), np.eye(dimension ** (volume - start - 2), dtype=complex))


def local_targets(dimension: int, fixture: dict[str, Any]) -> dict[tuple[float, int, int], np.ndarray]:
    _, qs, ps = system(dimension, 2, fixture)
    kinetic = sym((ps[0] @ ps[0] + ps[1] @ ps[1]) / (2.0 * float(fixture["chi"])))
    delta = qs[0] - qs[1]
    delta2 = delta @ delta
    boundary = sym(float(fixture["c"]) * delta2 / 2.0 + float(fixture["lambda"]) * delta2 @ (qs[0] @ qs[0] + qs[1] @ qs[1]) / 4.0)
    identity = np.eye(dimension * dimension, dtype=complex)
    targets: dict[tuple[float, int, int], np.ndarray] = {}
    for raw_eta in fixture["resolvent_imaginary_values"]:
        eta = float(Fraction(raw_eta))
        for site, q in enumerate(qs):
            resolvent = np.linalg.inv(1j * eta * identity - q)
            for adjoint in range(2):
                observable = resolvent if adjoint == 0 else resolvent.conj().T
                inner = kinetic @ observable - observable @ kinetic
                targets[(eta, site, adjoint)] = boundary @ inner - inner @ boundary
    return targets


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, coverage = manifest["finite_fixture"], manifest["coverage"]
    threshold = float(fixture["hostile_threshold"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001233" and manifest["result_id"] == "R-390" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001233/R-390/false", "provenance")
    check("coverage", all(coverage.values()), coverage, "declared coverage", "coverage")
    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    betas = [float(Fraction(raw)) for raw in fixture["beta_values"]]
    correct_residuals: list[float] = []
    wrong_residuals: list[float] = []
    samples = 0
    for volume, dimension in pairs:
        H, _, _ = system(dimension, volume, fixture)
        values, vectors = np.linalg.eigh(H)
        targets = local_targets(dimension, fixture)
        for beta in betas:
            weights = np.exp(-beta * (values - float(np.min(values))))
            state = sym((vectors * (weights / float(np.sum(weights)))) @ vectors.conj().T)
            for start in range(volume - 1):
                local_state = sym(reduce_pair(state, dimension, volume, start))
                wrong_state = np.eye(dimension * dimension, dtype=complex) / float(dimension * dimension)
                for target in targets.values():
                    positive_probe = target.conj().T @ target + target @ target.conj().T
                    full_value = complex(np.trace(state @ pair_embed(positive_probe, dimension, volume, start)))
                    correct_value = complex(np.trace(local_state @ positive_probe))
                    wrong_value = complex(np.trace(wrong_state @ positive_probe))
                    correct_residuals.append(abs(full_value - correct_value))
                    wrong_residuals.append(abs(full_value - wrong_value))
                    samples += 1
    check("correct duality anchor", max(correct_residuals) <= float(fixture["partial_trace_tolerance"]), max(correct_residuals), f"<={fixture['partial_trace_tolerance']}", "anchor")
    check("hostile maximally-mixed mutation caught", min(wrong_residuals) > threshold, min(wrong_residuals), f">{threshold}", "hostile")
    check("hostile sample count", samples == sum((volume - 1) for volume, _ in pairs) * len(betas) * len(targets), samples, "declared pair x beta x seed count", "coverage")
    derived = {"sample_count": samples, "maximum_correct_duality_residual": max(correct_residuals), "minimum_wrong_duality_residual": min(wrong_residuals), "maximum_wrong_duality_residual": max(wrong_residuals), "hostile_threshold": threshold, "mutation": "replace each local Gibbs marginal by I/d^2 before testing Tr(rho A_U)=Tr(rho_U A)", "caught": True}
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "hostile", "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-MARGINAL-SPECTRAL-WINDOW-TRANSFER", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "CAUGHT", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "derived": derived, "boundary": "The maximally-mixed local-state mutation is a hostile control and is not part of the proof route."}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"HOSTILE LOCAL-MARGINAL MUTATION CAUGHT {payload['passed']}/{payload['assertion_count']} min_wrong={payload['derived']['minimum_wrong_duality_residual']:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
