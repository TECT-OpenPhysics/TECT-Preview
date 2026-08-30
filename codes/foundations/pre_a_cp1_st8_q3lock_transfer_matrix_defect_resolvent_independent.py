#!/usr/bin/env python3
"""Non-importing independent lane for R-455.

The implementation deliberately reconstructs the matrix recurrence and its
infinity-norm envelope without importing the primary script.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-transfer-matrix-defect-resolvent-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-independent-pre_a_cp1_st8_q3lock_transfer_matrix_defect_resolvent/independent.json"
Vector = tuple[Fraction, ...]
Matrix = tuple[tuple[Fraction, ...], ...]


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def q(value: object) -> Fraction:
    return Fraction(str(value))


def add(a: Vector, b: Vector) -> Vector:
    return tuple(x + y for x, y in zip(a, b))


def scale(scalar: Fraction, value: Vector) -> Vector:
    return tuple(scalar * x for x in value)


def norm(value: Vector) -> Fraction:
    return max((abs(x) for x in value), default=Fraction(0))


def mv(matrix: Matrix, value: Vector) -> Vector:
    return tuple(sum(a * b for a, b in zip(row, value)) for row in matrix)


def mm(left: Matrix, right: Matrix) -> Matrix:
    dimension = len(left)
    return tuple(
        tuple(sum(left[row][inner] * right[inner][column] for inner in range(dimension)) for column in range(dimension))
        for row in range(dimension)
    )


def identity(dimension: int) -> Matrix:
    return tuple(tuple(Fraction(int(row == column)) for column in range(dimension)) for row in range(dimension))


def row_norm(matrix: Matrix) -> Fraction:
    return max((sum(abs(x) for x in row) for row in matrix), default=Fraction(0))


def nonnegative(matrix: Matrix) -> bool:
    return all(x >= 0 for row in matrix for x in row)


def make_matrix(name: str, upper: Fraction, step: int, dimension: int) -> Matrix:
    if name == "zero":
        scale_value, kind = Fraction(0), "cycle"
    elif name == "diagonal":
        scale_value, kind = upper, "diag"
    elif name == "permutation":
        scale_value, kind = upper, "cycle"
    elif name == "averaging":
        scale_value, kind = upper / dimension, "dense"
    elif name == "triangular":
        scale_value, kind = upper, "tri"
    elif name == "alternating":
        scale_value, kind = (upper if step % 2 else upper / 3), "cycle"
    elif name == "ramp-four":
        scale_value, kind = upper * Fraction(step % 4, 3), "cycle"
    else:
        raise ValueError(name)
    result: list[tuple[Fraction, ...]] = []
    for row_index in range(dimension):
        row = [Fraction(0) for _ in range(dimension)]
        if kind == "diag":
            row[row_index] = scale_value
        elif kind == "dense":
            row = [scale_value for _ in range(dimension)]
        elif kind == "tri":
            share = scale_value / (row_index + 1)
            row[: row_index + 1] = [share for _ in range(row_index + 1)]
        else:
            row[(row_index + step) % dimension] = scale_value
        result.append(tuple(row))
    return tuple(result)


def apply_path(matrices: list[Matrix], value: Vector) -> Vector:
    for matrix in matrices:
        value = mv(matrix, value)
    return value


def kernel(kappa: Fraction, base: Fraction, radius: int) -> Fraction:
    return sum(kappa ** (radius - 1 - j) * base**j for j in range(radius))


def closed(kappa: Fraction, base: Fraction, radius: int) -> Fraction:
    if radius == 0:
        return Fraction(0)
    if kappa == base:
        return Fraction(radius) * base ** (radius - 1)
    return (kappa**radius - base**radius) / (kappa - base)


def unique(values: list[Fraction]) -> list[Fraction]:
    output: list[Fraction] = []
    for value in values:
        if value not in output:
            output.append(value)
    return output


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]] == ["R-455", "EXP-001328", False], [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], ["R-455", "EXP-001328", False])
    finite = manifest["finite_fixture"]
    lo, hi = int(finite["radius_min"]), int(finite["radius_max"])
    dimensions = [int(x) for x in finite["dimensions"]]
    patterns = list(finite["matrix_patterns"])
    check("fixture", [lo, hi, dimensions, patterns] == [0, 64, [1, 2, 3], ["zero", "diagonal", "permutation", "averaging", "triangular", "alternating", "ramp-four"]], [lo, hi, dimensions, patterns], [0, 64, [1, 2, 3], ["zero", "diagonal", "permutation", "averaging", "triangular", "alternating", "ramp-four"]])

    parent_decay = Fraction(23, 26) ** 4
    parent_r450 = json.loads((ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_two_orientation_shell_transfer/primary.json").read_text(encoding="utf-8"))
    orientations = int(json.loads((ROOT / "strategy/pre-a-cp1-st8-q3lock-two-sided-history-cauchy-transfer-manifest.json").read_text(encoding="utf-8"))["finite_fixture"]["orientation_count"])
    source_constant = q(str(2 ** (4 - 1) * orientations)) * q(str(parent_r450["derived"]["C4_edge"])) * q("78") ** 4
    bars = unique([q(x) for x in finite["kappa_bar_fixture_values"]] + [parent_decay])
    defect_bases = [q(x) for x in finite["defect_decay_fixture_values"]]
    max_defect = max(q(x) for x in finite["defect_amplitude_fixture_values"])
    check("parent decay", parent_decay == Fraction(279841, 456976) and 0 < parent_decay < 1, parent_decay, Fraction(279841, 456976))
    check("source constant input", source_constant > 0, source_constant, ">0")

    pair_rows: list[dict[str, Any]] = []
    path_checks = 0
    for upper in bars:
        for defect_base in unique(defect_bases + [parent_decay, upper]):
            admissible = 0 <= upper < 1 and 0 <= defect_base < 1
            for dimension in dimensions:
                source_profile = tuple(Fraction(i + 1, dimension) for i in range(dimension))
                defect_profile = tuple(Fraction(dimension - i, dimension) for i in range(dimension))
                for pattern in patterns:
                    matrices = [make_matrix(pattern, upper, step, dimension) for step in range(1, hi + 1)]
                    history = tuple(Fraction(0) for _ in range(dimension))
                    source_terms: list[Vector] = []
                    defect_terms: list[Vector] = []
                    for step, matrix in enumerate(matrices, start=1):
                        check(f"matrix domain {pattern}/{dimension}/{upper}/{step}", nonnegative(matrix) and row_norm(matrix) <= upper, [nonnegative(matrix), row_norm(matrix)], [True, f"<={upper}"])
                        source = scale(source_constant * parent_decay ** (step - 1), source_profile)
                        defect = scale(max_defect * defect_base ** (step - 1), defect_profile)
                        source_terms.append(source)
                        defect_terms.append(defect)
                        previous = history
                        history = add(mv(matrix, previous), add(source, defect))
                        check(f"one-step norm {pattern}/{dimension}/{upper}/{step}", norm(mv(matrix, previous)) <= upper * norm(previous), [norm(mv(matrix, previous)), upper * norm(previous)], "dominated")
                        bound = source_constant * kernel(upper, parent_decay, step) + max_defect * kernel(upper, defect_base, step)
                        check(f"envelope {pattern}/{dimension}/{upper}/{step}", norm(history) <= bound, norm(history), f"<={bound}")
                        if step in {1, hi // 2, hi}:
                            suffix = identity(dimension)
                            expanded = tuple(Fraction(0) for _ in range(dimension))
                            for born in reversed(range(step)):
                                expanded = add(expanded, mv(suffix, add(source_terms[born], defect_terms[born])))
                                suffix = mm(suffix, matrices[born])
                            check(f"path identity {pattern}/{dimension}/{upper}/{step}", history == expanded, history, expanded)
                    suffix = identity(dimension)
                    for born in reversed(range(hi)):
                        transported = mv(suffix, source_terms[born])
                        bound = upper ** (hi - born - 1) * norm(source_terms[born])
                        check(f"product bound {pattern}/{dimension}/{upper}/{born + 1}", norm(transported) <= bound, norm(transported), f"<={bound}")
                        path_checks += 1
                        suffix = mm(suffix, matrices[born])
            check(f"threshold/{upper}/{defect_base}", max(upper, parent_decay, defect_base) < 1 if admissible else (upper >= 1 or defect_base >= 1), [upper, defect_base], "threshold control")
            check(f"closed-form/{upper}/{defect_base}", closed(upper, defect_base, hi) == kernel(upper, defect_base, hi), "identity", "identity")
            pair_rows.append({"kappa_bar": str(upper), "defect_base_s": str(defect_base), "admissible": admissible})

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": manifest["candidate_id"],
        "result_id": manifest["result_id"],
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": manifest["status"],
        "assertion_count": len(checks),
        "assertions": checks[:280],
        "assertion_samples_truncated": len(checks) > 280,
        "derived": {"radius_rows_per_pair": hi - lo + 1, "dimensions": dimensions, "matrix_patterns": patterns, "pair_rows": pair_rows, "pair_count": len(pair_rows), "path_checks": path_checks, "source_constant_A": str(source_constant), "parent_decay_r": str(parent_decay), "independence": True},
        "source_hashes": {"script": digest(Path(__file__)), "manifest": digest(MANIFEST)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    save(output, payload)
    print(f"R-455 INDEPENDENT {payload['verdict']} {len(checks)}/{len(checks)} pairs={len(pair_rows)} dims={dimensions} patterns={len(patterns)} path_checks={path_checks}", flush=True)
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    run(parser.parse_args().output)
