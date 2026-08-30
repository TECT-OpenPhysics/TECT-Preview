#!/usr/bin/env python3
"""Primary exact audit for a nonnegative transfer-matrix history resolvent.

This is an additive T-054 interface.  It keeps the R-454 scalar recurrence
method and admits a coupled finite vector of orientation/observable errors when
each source-owned transfer matrix is nonnegative and has one common induced
infinity-norm bound.  No source-owned Q3 history is inferred.
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-transfer-matrix-defect-resolvent-manifest.json"
R454_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-variable-coefficient-defect-resolvent-manifest.json"
R451_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-two-sided-history-cauchy-transfer-manifest.json"
R450_RUN = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_two_orientation_shell_transfer/primary.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_transfer_matrix_defect_resolvent/primary.json"

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


def inf_norm(vector: Vector) -> Fraction:
    return max((abs(entry) for entry in vector), default=Fraction(0))


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


def matrix_row_sum(matrix: Matrix) -> Fraction:
    return max((sum(abs(entry) for entry in row) for row in matrix), default=Fraction(0))


def matrix_nonnegative(matrix: Matrix) -> bool:
    return all(entry >= 0 for row in matrix for entry in row)


def kernel(propagation: Fraction, base: Fraction, radius: int) -> Fraction:
    return sum(propagation ** (radius - 1 - j) * base**j for j in range(radius))


def closed_form(propagation: Fraction, base: Fraction, radius: int) -> Fraction:
    if radius == 0:
        return Fraction(0)
    if propagation == base:
        return Fraction(radius) * base ** (radius - 1)
    return (propagation**radius - base**radius) / (propagation - base)


def matrix_pattern(pattern: str, upper: Fraction, step: int, dimension: int) -> Matrix:
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
            row = [scale for _ in range(dimension)]
        elif mode == "triangular":
            share = scale / (row_index + 1)
            row[: row_index + 1] = [share for _ in range(row_index + 1)]
        else:
            row[(row_index + step) % dimension] = scale
        rows.append(tuple(row))
    return tuple(rows)


def path_apply(matrices: list[Matrix], vector: Vector) -> Vector:
    current = vector
    for matrix in matrices:
        current = matrix_vector(matrix, current)
    return current


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
    r454 = json.loads(R454_MANIFEST.read_text(encoding="utf-8"))
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
        == ["R-455", "EXP-001328", "T-054", False, "CONDITIONAL_NONNEGATIVE_TRANSFER_MATRIX_RESOLVENT_AUDITED"],
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]],
        ["R-455", "EXP-001328", "T-054", False, "CONDITIONAL_NONNEGATIVE_TRANSFER_MATRIX_RESOLVENT_AUDITED"],
        "provenance",
    )
    check("parent R-454", r454["result_id"] == "R-454" and r454["claim_bearing"] is False, r454["result_id"], "R-454", "lineage")
    check("parent R-451", r451["result_id"] == "R-451" and r451["claim_bearing"] is False, r451["result_id"], "R-451", "lineage")
    check("parent method firewall", all(r454["method_preservation"].values()), r454["method_preservation"], "all true", "method")

    finite = manifest["finite_fixture"]
    radius_min = int(finite["radius_min"])
    radius_max = int(finite["radius_max"])
    dimensions = [int(value) for value in finite["dimensions"]]
    patterns = list(finite["matrix_patterns"])
    check("radius contract", radius_min == 0 and radius_max == 64, [radius_min, radius_max], [0, 64], "coverage")
    check("dimension contract", dimensions == [1, 2, 3], dimensions, [1, 2, 3], "coverage")
    check("pattern contract", patterns == ["zero", "diagonal", "permutation", "averaging", "triangular", "alternating", "ramp-four"], patterns, "declared patterns", "coverage")
    check("no grid substitution", finite["no_new_finite_grid"] is True and "no finite grid" in finite["fixture_role"].lower(), finite, "exact matrix rows only", "scope")

    q = fraction(r451["finite_fixture"]["ratio_q"])
    base_tail = fraction(r451["finite_fixture"]["base_tail"])
    orientations = int(r451["finite_fixture"]["orientation_count"])
    c4_edge = fraction(r450["derived"]["C4_edge"])
    factor = 2 ** (4 - 1) * orientations
    parent_decay = q**4
    source_constant = Fraction(factor) * c4_edge * base_tail**4
    check("parent q", q == Fraction(23, 26), q, Fraction(23, 26), "parent decay")
    check("parent base", base_tail == Fraction(78), base_tail, Fraction(78), "parent decay")
    check("orientation count", orientations == 2, orientations, 2, "parent decay")
    check("source factor", factor == 16, factor, 16, "parent constants")
    check("parent decay", parent_decay == Fraction(279841, 456976) and 0 < parent_decay < 1, parent_decay, "279841/456976 and <1", "parent decay")
    check("source constant", source_constant > 0 and source_constant == Fraction(factor) * c4_edge * base_tail**4, source_constant, "16*C4_edge*78^4", "source envelope")

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
    for upper in bars:
        bases = unique(defect_bases_declared + [parent_decay, upper])
        for defect_base in bases:
            admissible = 0 <= upper < 1 and 0 <= defect_base < 1
            admissible_pairs += int(admissible)
            source_resonance = source_resonance or upper == parent_decay
            defect_resonance = defect_resonance or upper == defect_base
            source_kernel_terminal = kernel(upper, parent_decay, radius_max)
            defect_kernel_terminal = kernel(upper, defect_base, radius_max)
            for dimension in dimensions:
                source_profile = tuple(Fraction(index + 1, dimension) for index in range(dimension))
                defect_profile = tuple(Fraction(dimension - index, dimension) for index in range(dimension))
                for pattern in patterns:
                    matrices = [matrix_pattern(pattern, upper, step, dimension) for step in range(1, radius_max + 1)]
                    history = zero_vector(dimension)
                    source_terms: list[Vector] = []
                    defect_terms: list[Vector] = []
                    for step in range(1, radius_max + 1):
                        matrix = matrices[step - 1]
                        check(f"matrix nonnegative {pattern} d={dimension} bar={upper} n={step}", matrix_nonnegative(matrix), matrix, "all entries >=0", "matrix contract")
                        row_sum = matrix_row_sum(matrix)
                        check(f"matrix row bound {pattern} d={dimension} bar={upper} n={step}", row_sum <= upper, row_sum, f"<={upper}", "matrix contract")
                        source = scale_vector(source_constant * parent_decay ** (step - 1), source_profile)
                        defect = scale_vector(max_amplitude * defect_base ** (step - 1), defect_profile)
                        source_terms.append(source)
                        defect_terms.append(defect)
                        previous = history
                        propagated = matrix_vector(matrix, previous)
                        check(f"induced step bound {pattern} d={dimension} bar={upper} n={step}", inf_norm(propagated) <= upper * inf_norm(previous), [inf_norm(propagated), inf_norm(previous)], "<= kappa_bar*previous norm", "matrix norm")
                        history = add_vectors(propagated, add_vectors(source, defect))
                        exact_bound = source_constant * kernel(upper, parent_decay, step) + max_amplitude * kernel(upper, defect_base, step)
                        check(f"matrix envelope {pattern} d={dimension} bar={upper} s={defect_base} n={step}", inf_norm(history) <= exact_bound, inf_norm(history), f"<={exact_bound}", "defect envelope")
                        if step in {1, radius_max // 2, radius_max}:
                            expansion = path_expansion(matrices, source_terms, defect_terms, step)
                            check(f"path expansion {pattern} d={dimension} bar={upper} s={defect_base} n={step}", history == expansion, history, expansion, "path-product")
                    # Compute all terminal suffix products once, then audit every birth time.
                    suffix = identity_matrix(dimension)
                    for born in reversed(range(radius_max)):
                        unit = source_terms[born]
                        transported = matrix_vector(suffix, unit)
                        expected = upper ** (radius_max - born - 1) * inf_norm(unit)
                        check(f"path norm {pattern} d={dimension} bar={upper} born={born + 1}", inf_norm(transported) <= expected, [inf_norm(transported), expected], "<= kappa_bar^(R-j)||u_j||", "path-product")
                        path_checks += 1
                        suffix = matrix_matrix(suffix, matrices[born])
                    # A strict sub-envelope on even steps tests inequality rather than equality.
                    sub_history = zero_vector(dimension)
                    for step in range(1, radius_max + 1):
                        geometric = max_amplitude * defect_base ** (step - 1)
                        residual = geometric if step % 2 else geometric / 2
                        source = scale_vector(source_constant * parent_decay ** (step - 1), source_profile)
                        defect = scale_vector(residual, defect_profile)
                        sub_history = add_vectors(matrix_vector(matrices[step - 1], sub_history), add_vectors(source, defect))
                        bound = source_constant * kernel(upper, parent_decay, step) + max_amplitude * kernel(upper, defect_base, step)
                        check(f"sub-defect envelope {pattern} d={dimension} bar={upper} s={defect_base} n={step}", inf_norm(sub_history) <= bound, inf_norm(sub_history), f"<={bound}", "defect contract")
            if admissible:
                check(f"two-base threshold bar={upper} s={defect_base}", max(upper, parent_decay, defect_base) < 1, max(upper, parent_decay, defect_base), "<1", "threshold")
            else:
                check(f"threshold control bar={upper} s={defect_base}", upper >= 1 or defect_base >= 1, [upper, defect_base], "bar>=1 or s>=1", "threshold control")
            pair_rows.append({
                "kappa_bar": str(upper),
                "defect_base_s": str(defect_base),
                "admissible": admissible,
                "source_branch": "resonant" if upper == parent_decay else "nonresonant",
                "defect_branch": "resonant" if upper == defect_base else "nonresonant",
                "terminal_source_kernel": str(source_kernel_terminal),
                "terminal_defect_kernel": str(defect_kernel_terminal),
            })

    check("source resonance exercised", source_resonance, True, "kappa_bar=parent_decay", "closed form")
    check("defect resonance exercised", defect_resonance, True, "s=kappa_bar", "closed form")
    check("admissible pairs exercised", admissible_pairs > 0, admissible_pairs, ">0", "threshold")
    check("nonadmissible controls exercised", any(not row["admissible"] for row in pair_rows), True, "unit/superunit controls", "threshold control")
    check("D=0 reduction retained", Fraction(0) in amplitudes, amplitudes, "declared exact-recurrence reduction", "defect contract")
    check("closed form identity", all(closed_form(upper, base, radius_max) == kernel(upper, base, radius_max) for upper in bars for base in unique(defect_bases_declared + [parent_decay, upper])), True, "all exact branches", "closed form")
    check("theorem marker", "K_R" in manifest["theorem"]["matrix_recurrence"] and "kappa_bar" in manifest["theorem"]["matrix_recurrence"], manifest["theorem"]["matrix_recurrence"], "matrix upper-bound contract", "theorem")

    scope = manifest["scope"]
    closed = (
        "nonnegative_transfer_matrix_contract_closed",
        "induced_infinity_norm_step_closed",
        "variable_matrix_path_product_bound_closed",
        "general_vector_defect_convolution_closed",
        "geometric_vector_defect_envelope_closed",
        "nonresonant_closed_form_closed",
        "resonant_closed_form_closed",
        "two_base_less_than_one_threshold_closed",
    )
    open_keys = tuple(key for key, value in scope.items() if key not in closed and key not in {"no_new_negative_result", "no_tier_change", "no_pdf"} and isinstance(value, bool))
    check("closed scope", all(scope[key] is True for key in closed), {key: scope[key] for key in closed}, "all true", "scope")
    check("open promotion firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "all false", "scope")
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
        "assertions": checks[:320],
        "assertion_samples_truncated": len(checks) > 320,
        "derived": {
            "parent_ratio_q": str(q),
            "parent_base_tail": str(base_tail),
            "parent_decay_r": str(parent_decay),
            "fourth_power_cauchy_factor": factor,
            "C4_edge": str(c4_edge),
            "source_constant_A": str(source_constant),
            "defect_amplitude_max_D": str(max_amplitude),
            "radius_rows_per_pair": radius_max - radius_min + 1,
            "dimensions": dimensions,
            "matrix_patterns": patterns,
            "pair_rows": pair_rows,
            "pair_count": len(pair_rows),
            "admissible_pair_count": admissible_pairs,
            "path_checks": path_checks,
            "nonnegative_transfer_matrix_contract_closed": True,
            "induced_infinity_norm_step_closed": True,
            "variable_matrix_path_product_bound_closed": True,
            "general_vector_defect_convolution_closed": True,
            "geometric_vector_defect_envelope_closed": True,
            "nonresonant_closed_form_closed": True,
            "resonant_closed_form_closed": True,
            "two_base_less_than_one_threshold_closed": True,
            "actual_q3_history_closed": False,
            "source_owned_transfer_closed": False,
            "source_owned_matrix_bound_closed": False,
            "source_owned_defect_closed": False,
            "common_weighted_operator_domain_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
            "sector_a_closed": False,
        },
        "source_hashes": {
            "script": digest(Path(__file__)),
            "manifest": digest(MANIFEST),
            "r454_manifest": digest(R454_MANIFEST),
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
    print(f"R-455 PRIMARY {payload['verdict']} {len(checks)}/{len(checks)} pairs={len(pair_rows)} dims={dimensions} patterns={len(patterns)} path_checks={path_checks} r={parent_decay}", flush=True)
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
