#!/usr/bin/env python3
"""Independent exact lane for R-456.

This file intentionally reimplements the weighted finite audit instead of
importing the primary lane.  It is an owner-interface check, not a Q3 result.
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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-weighted-transfer-operator-defect-resolvent-manifest.json"
R451 = ROOT / "strategy/pre-a-cp1-st8-q3lock-two-sided-history-cauchy-transfer-manifest.json"
R450 = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_two_orientation_shell_transfer/primary.json"
DEFAULT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-independent-pre_a_cp1_st8_q3lock_weighted_transfer_operator_defect_resolvent/independent.json"

Vec = tuple[Fraction, ...]
Mat = tuple[tuple[Fraction, ...], ...]


def save(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def q(value: object) -> Fraction:
    return Fraction(str(value))


def uniq(values: list[Fraction]) -> list[Fraction]:
    return list(dict.fromkeys(values))


def weights(kind: str, n: int) -> Vec:
    if kind == "unit":
        values = [Fraction(1)] * n
    elif kind == "dyadic":
        values = [Fraction(2**i) for i in range(n)]
    elif kind == "affine":
        values = [Fraction(i + 1) for i in range(n)]
    elif kind == "geometric":
        values = [Fraction(3**i) for i in range(n)]
    elif kind == "alternating":
        values = [Fraction(1 + i % 2) for i in range(n)]
    else:
        raise ValueError(kind)
    return tuple(values)


def make_matrix(kind: str, bound: Fraction, step: int, n: int, w: Vec) -> Mat:
    if kind == "zero":
        scale, mode = Fraction(0), "shift"
    elif kind == "diagonal":
        scale, mode = bound, "diag"
    elif kind == "permutation":
        scale, mode = bound, "shift"
    elif kind == "averaging":
        scale, mode = bound / n, "dense"
    elif kind == "triangular":
        scale, mode = bound, "lower"
    elif kind == "alternating":
        scale, mode = (bound if step % 2 else bound / 3), "shift"
    elif kind == "ramp-four":
        scale, mode = bound * Fraction(step % 4, 3), "shift"
    else:
        raise ValueError(kind)
    rows: list[tuple[Fraction, ...]] = []
    for i in range(n):
        row = [Fraction(0)] * n
        if mode == "diag":
            row[i] = scale
        elif mode == "dense":
            for j in range(n):
                row[j] = scale * w[i] / (n * w[j])
        elif mode == "lower":
            for j in range(i + 1):
                row[j] = scale * w[i] / ((i + 1) * w[j])
        else:
            j = (i + step) % n
            row[j] = scale * w[i] / w[j]
        rows.append(tuple(row))
    return tuple(rows)


def mv(matrix: Mat, vector: Vec) -> Vec:
    return tuple(sum(a * b for a, b in zip(row, vector)) for row in matrix)


def mm(left: Mat, right: Mat) -> Mat:
    n = len(left)
    return tuple(tuple(sum(left[i][k] * right[k][j] for k in range(n)) for j in range(n)) for i in range(n))


def eye(n: int) -> Mat:
    return tuple(tuple(Fraction(int(i == j)) for j in range(n)) for i in range(n))


def wnorm(vector: Vec, w: Vec) -> Fraction:
    return max((abs(a) / b for a, b in zip(vector, w)), default=Fraction(0))


def wrow(matrix: Mat, w: Vec) -> Fraction:
    return max((sum(a * b for a, b in zip(row, w)) / w[i] for i, row in enumerate(matrix)), default=Fraction(0))


def transformed_row(matrix: Mat, w: Vec) -> Fraction:
    return max((sum(abs(a * w[j] / w[i]) for j, a in enumerate(row)) for i, row in enumerate(matrix)), default=Fraction(0))


def kernel(a: Fraction, b: Fraction, radius: int) -> Fraction:
    return sum(a ** (radius - 1 - j) * b**j for j in range(radius))


def closed(a: Fraction, b: Fraction, radius: int) -> Fraction:
    if radius == 0:
        return Fraction(0)
    if a == b:
        return radius * b ** (radius - 1)
    return (a**radius - b**radius) / (a - b)


def run(output: Path = DEFAULT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent = json.loads(R451.read_text(encoding="utf-8"))
    source_run = json.loads(R450.read_text(encoding="utf-8"))
    assert manifest["result_id"] == "R-456"
    assert manifest["exploration_id"] == "EXP-001329"
    assert manifest["claim_bearing"] is False
    assert manifest["status"] == "CONDITIONAL_WEIGHTED_TRANSFER_OPERATOR_RESOLVENT_AUDITED"
    assert parent["result_id"] == "R-451" and parent["claim_bearing"] is False
    assert all(manifest["method_preservation"].values())

    fixture = manifest["finite_fixture"]
    radius = int(fixture["radius_max"])
    dims = [int(x) for x in fixture["dimensions"]]
    weight_kinds = list(fixture["weight_patterns"])
    kinds = list(fixture["matrix_patterns"])
    ratio = q(parent["finite_fixture"]["ratio_q"])
    tail = q(parent["finite_fixture"]["base_tail"])
    c4 = q(source_run["derived"]["C4_edge"])
    source_a = Fraction(2 ** (4 - 1) * int(parent["finite_fixture"]["orientation_count"])) * c4 * tail**4
    decay = ratio**4
    bars = uniq([q(x) for x in fixture["kappa_bar_fixture_values"]] + [decay])
    defect_values = [q(x) for x in fixture["defect_decay_fixture_values"]]
    amp = max(q(x) for x in fixture["defect_amplitude_fixture_values"])

    path_checks = 0
    diagonal_checks = 0
    history_checks = 0
    pair_count = 0
    resonance_a = False
    resonance_d = False
    for bound in bars:
        bases = uniq(defect_values + [decay, bound])
        for defect in bases:
            pair_count += 1
            resonance_a = resonance_a or bound == decay
            resonance_d = resonance_d or bound == defect
            for n in dims:
                for weight_kind in weight_kinds:
                    w = weights(weight_kind, n)
                    assert all(x > 0 for x in w)
                    source_profile = w
                    defect_profile = tuple(value if index % 2 == 0 else value / 2 for index, value in enumerate(w))
                    for matrix_kind in kinds:
                        history = tuple(Fraction(0) for _ in range(n))
                        matrices: list[Mat] = []
                        sources: list[Vec] = []
                        defects: list[Vec] = []
                        for step in range(1, radius + 1):
                            matrix = make_matrix(matrix_kind, bound, step, n, w)
                            matrices.append(matrix)
                            assert all(a >= 0 for row in matrix for a in row)
                            assert wrow(matrix, w) <= bound
                            assert transformed_row(matrix, w) == wrow(matrix, w)
                            diagonal_checks += 1
                            source = tuple(source_a * decay ** (step - 1) * value for value in source_profile)
                            defect_term = tuple(amp * defect ** (step - 1) * value for value in defect_profile)
                            sources.append(source)
                            defects.append(defect_term)
                            propagated = mv(matrix, history)
                            assert wnorm(propagated, w) <= bound * wnorm(history, w)
                            history = tuple(a + b + c for a, b, c in zip(propagated, source, defect_term))
                            expected = source_a * kernel(bound, decay, step) + amp * kernel(bound, defect, step)
                            assert wnorm(history, w) <= expected
                            history_checks += 1
                        suffix = eye(n)
                        for born in reversed(range(radius)):
                            moved = mv(suffix, sources[born])
                            assert wnorm(moved, w) <= bound ** (radius - born - 1) * wnorm(sources[born], w)
                            path_checks += 1
                            suffix = mm(suffix, matrices[born])
                        assert closed(bound, decay, radius) == kernel(bound, decay, radius)
                        assert closed(bound, defect, radius) == kernel(bound, defect, radius)
    expected_pairs = sum(len(uniq(defect_values + [decay, bound])) for bound in bars)
    assert resonance_a and resonance_d and pair_count == expected_pairs
    assert Fraction(0) in [q(x) for x in fixture["defect_amplitude_fixture_values"]]
    assert all(manifest["scope"][key] is True for key in ("positive_weight_contract_closed", "weighted_row_sum_step_closed", "diagonal_conjugation_closed", "weighted_path_product_bound_closed", "weighted_vector_defect_convolution_closed", "weighted_geometric_defect_envelope_closed", "nonresonant_closed_form_closed", "resonant_closed_form_closed", "two_base_less_than_one_threshold_closed"))
    assert manifest["scope"]["actual_q3_history_closed"] is False
    assert manifest["scope"]["pre_a_closed"] is False and manifest["scope"]["sector_a_closed"] is False

    payload: dict[str, Any] = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": manifest["candidate_id"],
        "result_id": manifest["result_id"],
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": manifest["status"],
        "assertion_count": history_checks + diagonal_checks + path_checks,
        "derived": {
            "parent_ratio_q": str(ratio),
            "parent_decay_r": str(decay),
            "source_constant_A": str(source_a),
            "radius_rows_per_pair": radius + 1,
            "dimensions": dims,
            "weight_patterns": weight_kinds,
            "matrix_patterns": kinds,
            "pair_count": pair_count,
            "path_checks": path_checks,
            "diagonal_conjugation_checks": diagonal_checks,
            "history_checks": history_checks,
            "positive_weight_contract_closed": True,
            "weighted_row_sum_step_closed": True,
            "diagonal_conjugation_closed": True,
            "weighted_path_product_bound_closed": True,
            "weighted_vector_defect_convolution_closed": True,
            "weighted_geometric_defect_envelope_closed": True,
            "nonresonant_closed_form_closed": True,
            "resonant_closed_form_closed": True,
            "two_base_less_than_one_threshold_closed": True,
            "actual_q3_history_closed": False,
            "source_owned_transfer_closed": False,
            "source_owned_weight_packet_closed": False,
            "common_weighted_operator_domain_closed": False,
            "pre_a_closed": False,
            "sector_a_closed": False,
        },
        "source_hashes": {"script": sha(Path(__file__)), "manifest": sha(MANIFEST), "r451_manifest": sha(R451), "r450_run": sha(R450)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    if output:
        save(output, payload)
    print(f"R-456 INDEPENDENT {payload['verdict']} assertions={payload['assertion_count']} pairs={pair_count} path_checks={path_checks}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    run(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
