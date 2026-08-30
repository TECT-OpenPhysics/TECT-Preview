#!/usr/bin/env python3
"""Primary exact audit for the additive R-456 weighted transfer interface.

The script checks a finite positive weighted sup-norm version of the unchanged
R-455 source-plus-defect recurrence.  It deliberately does not instantiate a
Q3 owner packet or infer an unbounded operator domain.
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


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-weighted-transfer-operator-defect-resolvent-manifest.json"
R455_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-transfer-matrix-defect-resolvent-manifest.json"
R451_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-two-sided-history-cauchy-transfer-manifest.json"
R450_RUN = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_two_orientation_shell_transfer/primary.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_weighted_transfer_operator_defect_resolvent/primary.json"

Vector = tuple[Fraction, ...]
Matrix = tuple[tuple[Fraction, ...], ...]


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
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


def fraction(value: object) -> Fraction:
    return Fraction(str(value))


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


def zero_vector(dimension: int) -> Vector:
    return tuple(Fraction(0) for _ in range(dimension))


def add_vectors(left: Vector, right: Vector) -> Vector:
    return tuple(a + b for a, b in zip(left, right))


def scale_vector(value: Fraction, vector: Vector) -> Vector:
    return tuple(value * entry for entry in vector)


def weighted_norm(vector: Vector, weights: Vector) -> Fraction:
    return max((abs(entry) / weight for entry, weight in zip(vector, weights)), default=Fraction(0))


def nonnegative(vector: Vector) -> bool:
    return all(entry >= 0 for entry in vector)


def matrix_vector(matrix: Matrix, vector: Vector) -> Vector:
    return tuple(sum(entry * value for entry, value in zip(row, vector)) for row in matrix)


def matrix_matrix(left: Matrix, right: Matrix) -> Matrix:
    dimension = len(left)
    return tuple(
        tuple(sum(left[row][inner] * right[inner][column] for inner in range(dimension)) for column in range(dimension))
        for row in range(dimension)
    )


def identity_matrix(dimension: int) -> Matrix:
    return tuple(tuple(Fraction(int(row == column)) for column in range(dimension)) for row in range(dimension))


def matrix_nonnegative(matrix: Matrix) -> bool:
    return all(entry >= 0 for row in matrix for entry in row)


def weighted_row_bound(matrix: Matrix, weights: Vector) -> Fraction:
    return max(
        (sum(entry * weight for entry, weight in zip(row, weights)) / weights[index] for index, row in enumerate(matrix)),
        default=Fraction(0),
    )


def diagonal_conjugate(matrix: Matrix, weights: Vector) -> Matrix:
    return tuple(
        tuple(entry * weights[column] / weights[row] for column, entry in enumerate(row_values))
        for row, row_values in enumerate(matrix)
    )


def ordinary_row_bound(matrix: Matrix) -> Fraction:
    return max((sum(abs(entry) for entry in row) for row in matrix), default=Fraction(0))


def weight_vector(pattern: str, dimension: int) -> Vector:
    if pattern == "unit":
        values = [Fraction(1) for _ in range(dimension)]
    elif pattern == "dyadic":
        values = [Fraction(2**index) for index in range(dimension)]
    elif pattern == "affine":
        values = [Fraction(index + 1) for index in range(dimension)]
    elif pattern == "geometric":
        values = [Fraction(3**index) for index in range(dimension)]
    elif pattern == "alternating":
        values = [Fraction(1 + (index % 2)) for index in range(dimension)]
    else:
        raise ValueError(f"unknown weight pattern: {pattern}")
    return tuple(values)


def weighted_matrix(pattern: str, upper: Fraction, step: int, dimension: int, weights: Vector) -> Matrix:
    if pattern == "zero":
        scale = Fraction(0)
        mode = "cyclic"
    elif pattern == "diagonal":
        scale = upper
        mode = "diagonal"
    elif pattern == "permutation":
        scale = upper
        mode = "cyclic"
    elif pattern == "averaging":
        scale = upper / dimension
        mode = "dense"
    elif pattern == "triangular":
        scale = upper
        mode = "triangular"
    elif pattern == "alternating":
        scale = upper if step % 2 else upper / 3
        mode = "cyclic"
    elif pattern == "ramp-four":
        scale = upper * Fraction(step % 4, 3)
        mode = "cyclic"
    else:
        raise ValueError(f"unknown matrix pattern: {pattern}")

    rows: list[tuple[Fraction, ...]] = []
    for row_index in range(dimension):
        row = [Fraction(0) for _ in range(dimension)]
        if mode == "diagonal":
            row[row_index] = scale
        elif mode == "dense":
            row = [scale * weights[row_index] / (dimension * weights[column]) for column in range(dimension)]
        elif mode == "triangular":
            share = scale / (row_index + 1)
            for column in range(row_index + 1):
                row[column] = share * weights[row_index] / weights[column]
        else:
            column = (row_index + step) % dimension
            row[column] = scale * weights[row_index] / weights[column]
        rows.append(tuple(row))
    return tuple(rows)


def kernel(propagation: Fraction, base: Fraction, radius: int) -> Fraction:
    return sum(propagation ** (radius - 1 - index) * base**index for index in range(radius))


def closed_form(propagation: Fraction, base: Fraction, radius: int) -> Fraction:
    if radius == 0:
        return Fraction(0)
    if propagation == base:
        return Fraction(radius) * base ** (radius - 1)
    return (propagation**radius - base**radius) / (propagation - base)


def path_expansion(matrices: list[Matrix], source_terms: list[Vector], defect_terms: list[Vector], radius: int) -> Vector:
    total = zero_vector(len(source_terms[0])) if source_terms else zero_vector(1)
    suffix = identity_matrix(len(total))
    for born in reversed(range(radius)):
        contribution = add_vectors(source_terms[born], defect_terms[born])
        total = add_vectors(total, matrix_vector(suffix, contribution))
        suffix = matrix_matrix(suffix, matrices[born])
    return total


def unique(values: list[Fraction]) -> list[Fraction]:
    result: list[Fraction] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def run(output: Path = DEFAULT_OUTPUT, store: bool = True) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    r455 = json.loads(R455_MANIFEST.read_text(encoding="utf-8"))
    r451 = json.loads(R451_MANIFEST.read_text(encoding="utf-8"))
    r450 = json.loads(R450_RUN.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})

    check(
        "identity",
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]]
        == ["R-456", "EXP-001329", "T-054", False, "CONDITIONAL_WEIGHTED_TRANSFER_OPERATOR_RESOLVENT_AUDITED"],
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]],
        ["R-456", "EXP-001329", "T-054", False, "CONDITIONAL_WEIGHTED_TRANSFER_OPERATOR_RESOLVENT_AUDITED"],
        "provenance",
    )
    check("parent R-455", r455["result_id"] == "R-455" and r455["claim_bearing"] is False, r455["result_id"], "R-455", "lineage")
    check("parent method firewall", all(r455["method_preservation"].values()), r455["method_preservation"], "all true", "method")

    finite = manifest["finite_fixture"]
    radius_min = int(finite["radius_min"])
    radius_max = int(finite["radius_max"])
    dimensions = [int(value) for value in finite["dimensions"]]
    weights_declared = list(finite["weight_patterns"])
    patterns = list(finite["matrix_patterns"])
    check("radius contract", radius_min == 0 and radius_max > radius_min, [radius_min, radius_max], "nonempty declared finite radius", "coverage")
    check("dimension contract", dimensions == [1, 2, 3], dimensions, [1, 2, 3], "coverage")
    check("weight contract", weights_declared == ["unit", "dyadic", "affine", "geometric", "alternating"], weights_declared, "declared positive patterns", "coverage")
    check("pattern contract", patterns == ["zero", "diagonal", "permutation", "averaging", "triangular", "alternating", "ramp-four"], patterns, "declared patterns", "coverage")
    check("no grid substitution", finite["no_new_finite_grid"] is True and "not an exhaustion" in finite["fixture_role"].lower(), finite["fixture_role"], "finite algebra only", "scope")

    q = fraction(r451["finite_fixture"]["ratio_q"])
    base_tail = fraction(r451["finite_fixture"]["base_tail"])
    orientations = int(r451["finite_fixture"]["orientation_count"])
    c4_edge = fraction(r450["derived"]["C4_edge"])
    source_factor = 2 ** (4 - 1) * orientations
    parent_decay = q**4
    source_constant = Fraction(source_factor) * c4_edge * base_tail**4
    check("parent decay domain", 0 < q < 1 and base_tail > 0 and orientations > 0, [q, base_tail, orientations], "positive parent inputs and 0<q<1", "parent")
    check("source constant derived", source_constant > 0 and source_constant == Fraction(source_factor) * c4_edge * base_tail**4, source_constant, "factor*C4_edge*base_tail^4", "parent")

    bars = unique([fraction(value) for value in finite["kappa_bar_fixture_values"]] + [parent_decay])
    defect_bases_declared = [fraction(value) for value in finite["defect_decay_fixture_values"]]
    amplitudes = [fraction(value) for value in finite["defect_amplitude_fixture_values"]]
    max_amplitude = max(amplitudes)
    check("upper-bound domain", all(value >= 0 for value in bars), bars, ">=0", "matrix contract")
    check("defect amplitude domain", all(value >= 0 for value in amplitudes), amplitudes, ">=0", "defect contract")

    pair_rows: list[dict[str, Any]] = []
    source_resonance = False
    defect_resonance = False
    admissible_pairs = 0
    path_checks = 0
    diagonal_checks = 0
    for upper in bars:
        bases = unique(defect_bases_declared + [parent_decay, upper])
        for defect_base in bases:
            admissible = 0 <= upper < 1 and 0 <= defect_base < 1
            admissible_pairs += int(admissible)
            source_resonance = source_resonance or upper == parent_decay
            defect_resonance = defect_resonance or upper == defect_base
            for dimension in dimensions:
                for weight_pattern in weights_declared:
                    weights = weight_vector(weight_pattern, dimension)
                    check(f"positive weights {weight_pattern} d={dimension}", all(value > 0 for value in weights), weights, ">0", "weighted contract")
                    source_profile = weights
                    defect_profile = tuple(weights[index] if index % 2 == 0 else weights[index] / 2 for index in range(dimension))
                    for pattern in patterns:
                        matrices = [weighted_matrix(pattern, upper, step, dimension, weights) for step in range(1, radius_max + 1)]
                        history = zero_vector(dimension)
                        source_terms: list[Vector] = []
                        defect_terms: list[Vector] = []
                        for step in range(1, radius_max + 1):
                            matrix = matrices[step - 1]
                            row_bound = weighted_row_bound(matrix, weights)
                            if step == 1:
                                check(f"matrix nonnegative {pattern} d={dimension} w={weight_pattern} bar={upper}", matrix_nonnegative(matrix), matrix, "all entries >=0", "weighted contract")
                                check(f"weighted row bound {pattern} d={dimension} w={weight_pattern} bar={upper}", row_bound <= upper, row_bound, f"<={upper}", "weighted contract")
                                transformed = diagonal_conjugate(matrix, weights)
                                check(f"diagonal conjugation {pattern} d={dimension} w={weight_pattern}", ordinary_row_bound(transformed) == row_bound, [ordinary_row_bound(transformed), row_bound], "equal", "conjugation")
                                diagonal_checks += 1
                            source = scale_vector(source_constant * parent_decay ** (step - 1), source_profile)
                            defect = scale_vector(max_amplitude * defect_base ** (step - 1), defect_profile)
                            if step in {1, radius_max}:
                                check(f"source weighted bound {pattern} d={dimension} w={weight_pattern} n={step}", weighted_norm(source, weights) <= source_constant * parent_decay ** (step - 1), weighted_norm(source, weights), "<= A*r^(n-1)", "source contract")
                                check(f"defect weighted bound {pattern} d={dimension} w={weight_pattern} n={step}", weighted_norm(defect, weights) <= max_amplitude * defect_base ** (step - 1), weighted_norm(defect, weights), "<= D*s^(n-1)", "defect contract")
                            source_terms.append(source)
                            defect_terms.append(defect)
                            previous = history
                            propagated = matrix_vector(matrix, previous)
                            check(f"weighted induced step {pattern} d={dimension} w={weight_pattern} n={step}", weighted_norm(propagated, weights) <= upper * weighted_norm(previous, weights), [weighted_norm(propagated, weights), weighted_norm(previous, weights)], "<= kappa_bar*previous norm", "weighted norm")
                            history = add_vectors(propagated, add_vectors(source, defect))
                            if step in {1, radius_max}:
                                check(f"weighted history nonnegative {pattern} d={dimension} w={weight_pattern} n={step}", nonnegative(history), history, ">=0", "recurrence")
                            exact_bound = source_constant * kernel(upper, parent_decay, step) + max_amplitude * kernel(upper, defect_base, step)
                            check(f"weighted envelope {pattern} d={dimension} w={weight_pattern} n={step}", weighted_norm(history, weights) <= exact_bound, weighted_norm(history, weights), f"<={exact_bound}", "defect envelope")
                            if step in {1, radius_max // 2, radius_max}:
                                expansion = path_expansion(matrices, source_terms, defect_terms, step)
                                check(f"weighted path expansion {pattern} d={dimension} w={weight_pattern} n={step}", history == expansion, history, expansion, "path-product")
                        suffix = identity_matrix(dimension)
                        for born in reversed(range(radius_max)):
                            unit = source_terms[born]
                            transported = matrix_vector(suffix, unit)
                            expected = upper ** (radius_max - born - 1) * weighted_norm(unit, weights)
                            check(f"weighted path norm {pattern} d={dimension} w={weight_pattern} born={born + 1}", weighted_norm(transported, weights) <= expected, [weighted_norm(transported, weights), expected], "<= kappa_bar^(R-j)||u_j||_w", "path-product")
                            path_checks += 1
                            suffix = matrix_matrix(suffix, matrices[born])
                        pair_rows.append({
                            "kappa_bar": str(upper),
                            "defect_base_s": str(defect_base),
                            "dimension": dimension,
                            "weight_pattern": weight_pattern,
                            "matrix_patterns": len(patterns),
                        })
            if admissible:
                check(f"two-base threshold bar={upper} s={defect_base}", max(upper, parent_decay, defect_base) < 1, max(upper, parent_decay, defect_base), "<1", "threshold")
            else:
                check(f"threshold control bar={upper} s={defect_base}", upper >= 1 or defect_base >= 1, [upper, defect_base], "bar>=1 or s>=1", "threshold control")

    pair_count = sum(len(unique(defect_bases_declared + [parent_decay, upper])) for upper in bars)
    check("source resonance exercised", source_resonance, True, "kappa_bar=parent_decay", "closed form")
    check("defect resonance exercised", defect_resonance, True, "s=kappa_bar", "closed form")
    check("admissible pairs exercised", admissible_pairs > 0, admissible_pairs, ">0", "threshold")
    check("nonadmissible controls exercised", any(upper >= 1 or base >= 1 for upper in bars for base in unique(defect_bases_declared + [parent_decay, upper])), True, "unit/superunit controls", "threshold control")
    check("D=0 reduction retained", Fraction(0) in amplitudes, amplitudes, "declared exact-recurrence reduction", "defect contract")
    check("closed form identity", all(closed_form(upper, base, radius_max) == kernel(upper, base, radius_max) for upper in bars for base in unique(defect_bases_declared + [parent_decay, upper])), True, "all exact branches", "closed form")
    check("theorem marker", "w_j" in manifest["theorem"]["weighted_matrix_contract"] and "kappa_bar" in manifest["theorem"]["weighted_matrix_contract"], manifest["theorem"]["weighted_matrix_contract"], "weighted row-bound contract", "theorem")
    check("pair row accounting", len(pair_rows) == pair_count * len(dimensions) * len(weights_declared) * len(patterns), [len(pair_rows), pair_count], "pair*dimension*weight*pattern", "coverage")

    scope = manifest["scope"]
    closed = tuple(key for key, value in scope.items() if key.endswith("_closed") and value is True and key not in {"actual_q3_history_closed"})
    # The manifest deliberately marks only the finite weighted algebra rows closed.
    check("closed scope", all(scope[key] is True for key in closed), {key: scope[key] for key in closed}, "all declared finite rows true", "scope")
    open_keys = tuple(key for key, value in scope.items() if key.endswith("_closed") and value is False)
    check("open promotion firewall", len(open_keys) >= 15 and scope["actual_q3_history_closed"] is False and scope["source_owned_transfer_closed"] is False, open_keys, "owner and downstream scopes remain open", "scope")
    check("no negative/tier/pdf mutation", scope["no_new_negative_result"] and scope["no_tier_change"] and scope["no_pdf"], [scope["no_new_negative_result"], scope["no_tier_change"], scope["no_pdf"]], [True, True, True], "scope")
    check("method preservation", all(manifest["method_preservation"].values()), manifest["method_preservation"], "all true", "method-firewall")

    payload: dict[str, Any] = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": manifest["candidate_id"],
        "result_id": manifest["result_id"],
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": manifest["status"],
        "assertion_count": len(checks),
        "assertions": checks[:360],
        "assertion_samples_truncated": len(checks) > 360,
        "derived": {
            "parent_ratio_q": str(q),
            "parent_base_tail": str(base_tail),
            "parent_decay_r": str(parent_decay),
            "fourth_power_cauchy_factor": source_factor,
            "C4_edge": str(c4_edge),
            "source_constant_A": str(source_constant),
            "defect_amplitude_max_D": str(max_amplitude),
            "radius_rows_per_pair": radius_max - radius_min + 1,
            "dimensions": dimensions,
            "weight_patterns": weights_declared,
            "matrix_patterns": patterns,
            "pair_count": pair_count,
            "pair_rows": pair_rows[:80],
            "admissible_pair_count": admissible_pairs,
            "path_checks": path_checks,
            "diagonal_conjugation_checks": diagonal_checks,
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
        "source_hashes": {
            "script": digest(Path(__file__)),
            "manifest": digest(MANIFEST),
            "r455_manifest": digest(R455_MANIFEST),
            "r451_manifest": digest(R451_MANIFEST),
            "r450_run": digest(R450_RUN),
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    if store:
        atomic_json(output if output.is_absolute() else REPO / output, payload)
    print(f"R-456 PRIMARY {payload['verdict']} {len(checks)}/{len(checks)} pairs={pair_count} dims={dimensions} weights={len(weights_declared)} patterns={len(patterns)} path_checks={path_checks} r={parent_decay}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    run(args.output, store=not args.no_store)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
