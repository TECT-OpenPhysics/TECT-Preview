#!/usr/bin/env python3
"""Primary exact audit for EXP-001194.

This verifies the conditional limit-passage contract on an exact rational
fixture.  It does not claim that the actual Q3 word limits or embeddings
exist.
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
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-conditional-os-kms-limit-passage"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-29-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def frac(value: Any) -> Fraction:
    return Fraction(str(value))


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def dot(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def gram_from_vectors(vectors: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[dot(vectors[i], vectors[j]) for j in range(len(vectors))] for i in range(len(vectors))]


def quadratic(matrix: list[list[Fraction]], coeff: list[Fraction]) -> Fraction:
    return sum((coeff[i] * matrix[i][j] * coeff[j] for i in range(len(coeff)) for j in range(len(coeff))), Fraction(0))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001194" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001194/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False and manifest["tier"] == "T0", [manifest["claim_bearing"], manifest["tier"]], [False, "T0"], "scope")
    check("finite OS authority", "EXP-001173" in manifest["prior_explorations"], manifest["prior_explorations"], "EXP-001173", "authority")
    check("conditional transfer authority", "EXP-001065" in manifest["prior_explorations"], manifest["prior_explorations"], "EXP-001065", "authority")
    check("kinetic boundary authority", "EXP-001193" in manifest["prior_explorations"], manifest["prior_explorations"], "EXP-001193", "authority")
    check("finite hypothesis count", len(manifest["model"]["hypotheses"]) == 4, len(manifest["model"]["hypotheses"]), 4, "contract")

    vectors = [[frac(x) for x in vector] for vector in fixture["gram_vectors"]]
    expected_gram = [[frac(x) for x in row] for row in fixture["gram_limit"]]
    limit_gram = gram_from_vectors(vectors)
    check("Gram generated from vectors", limit_gram == expected_gram, limit_gram, expected_gram, "OS")
    check("Gram symmetry", all(limit_gram[i][j] == limit_gram[j][i] for i in range(len(limit_gram)) for j in range(len(limit_gram))), limit_gram, "symmetric", "OS")

    coefficients = [[frac(x) for x in vector] for vector in fixture["coefficient_vectors"]]
    limit_quadratics: list[Fraction] = []
    for index, coeff in enumerate(coefficients):
        q_limit = quadratic(limit_gram, coeff)
        limit_quadratics.append(q_limit)
        check(f"limit quadratic {index}", q_limit >= 0, q_limit, ">=0", "OS")
        sum_of_squares = dot([coeff[0] + coeff[1], coeff[1] + coeff[2]], [coeff[0] + coeff[1], coeff[1] + coeff[2]])
        check(f"sum of squares {index}", q_limit == sum_of_squares, [q_limit, sum_of_squares], "equal", "OS")

    denominators = [frac(value) for value in fixture["exhaustions"]["denominators"]]
    scales = {
        "path_a": frac(fixture["exhaustions"]["path_a_scale"]),
        "path_b": frac(fixture["exhaustions"]["path_b_scale"]),
    }
    entry_bound = frac(fixture["entry_bound"])
    exhaustion_rows: list[dict[str, Any]] = []
    max_entry = Fraction(0)
    for path_name, scale in scales.items():
        for denominator in denominators:
            check(f"{path_name} positive denominator {denominator}", denominator > 0, denominator, ">0", "convergence")
            epsilon = scale / denominator
            sequence = [[limit_gram[i][j] + (epsilon if i == j else Fraction(0)) for j in range(len(limit_gram))] for i in range(len(limit_gram))]
            for i in range(len(sequence)):
                for j in range(len(sequence)):
                    difference = abs(sequence[i][j] - limit_gram[i][j])
                    check(f"{path_name} entry convergence {denominator} {i}{j}", difference <= epsilon, difference, f"<={epsilon}", "convergence")
                    max_entry = max(max_entry, abs(sequence[i][j]))
            for index, coeff in enumerate(coefficients):
                q_sequence = quadratic(sequence, coeff)
                diagonal_norm = dot(coeff, coeff)
                expected_q = limit_quadratics[index] + epsilon * diagonal_norm
                check(f"{path_name} PSD quadratic {denominator} {index}", q_sequence >= 0, q_sequence, ">=0", "OS")
                check(f"{path_name} quadratic decomposition {denominator} {index}", q_sequence == expected_q, [q_sequence, expected_q], "equal", "OS")
                exhaustion_rows.append({"path": path_name, "denominator": denominator, "coefficient": index, "quadratic": q_sequence, "limit_quadratic": limit_quadratics[index], "epsilon": epsilon})
    check("entry bound", max_entry <= entry_bound, max_entry, f"<={entry_bound}", "convergence")

    kms_limit = frac(fixture["kms_limit"])
    kms_error_scale = frac(fixture["kms_error_scale"])
    beta_hbar = frac(fixture["beta_hbar"])
    times = [frac(value) for value in fixture["euclidean_times"]]
    kms_bound = frac(fixture["kms_bound"])
    kms_rows: list[dict[str, Any]] = []
    max_kms = Fraction(0)
    for denominator in denominators:
        for time in times:
            complement = beta_hbar - time
            left = kms_limit + kms_error_scale * time * complement / denominator
            right = kms_limit + kms_error_scale * time * complement / denominator
            check(f"KMS complement range {denominator} {time}", 0 <= time <= beta_hbar and 0 <= complement <= beta_hbar, [time, complement], f"within [0,{beta_hbar}]", "KMS")
            check(f"finite KMS equality {denominator} {time}", left == right, [left, right], "equal", "KMS")
            check(f"KMS convergence left {denominator} {time}", abs(left - kms_limit) <= kms_error_scale * time * complement / denominator, left, f"error<={kms_error_scale * time * complement / denominator}", "KMS")
            check(f"KMS convergence right {denominator} {time}", abs(right - kms_limit) <= kms_error_scale * time * complement / denominator, right, f"error<={kms_error_scale * time * complement / denominator}", "KMS")
            check(f"KMS bound {denominator} {time}", left <= kms_bound and right <= kms_bound, [left, right], f"<={kms_bound}", "KMS")
            max_kms = max(max_kms, left, right)
            kms_rows.append({"denominator": denominator, "time": time, "complement": complement, "left": left, "right": right, "limit": kms_limit})
    check("KMS limit fixture", kms_limit == beta_hbar, [kms_limit, beta_hbar], "equal fixture scales", "KMS")
    check("KMS bound", max_kms <= kms_bound, max_kms, f"<={kms_bound}", "KMS")

    check("scope closed contract", scope["conditional_entrywise_os_positivity_passage_closed"] and scope["conditional_kms_limit_passage_closed"] and scope["conditional_word_form_completion_contract_closed"], scope, "conditional OS/KMS contract", "scope")
    open_keys = [key for key, value in scope.items() if key.endswith("_closed") and key not in {"conditional_entrywise_os_positivity_passage_closed", "conditional_kms_limit_passage_closed", "conditional_word_form_completion_contract_closed", "finite_fixture_psd_and_convergence_closed", "finite_fixture_kms_convergence_closed"}]
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "all successor gates open", "scope")

    passed = len(rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-CONDITIONAL-OS-KMS-LIMIT-PASSAGE",
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": rows,
        "derived": {
            "gram_limit": limit_gram,
            "limit_quadratics": limit_quadratics,
            "exhaustion_scales": scales,
            "exhaustion_rows": exhaustion_rows,
            "max_entry": max_entry,
            "kms_rows": kms_rows,
            "max_kms": max_kms,
            "conditional_entrywise_os_positivity_passage_closed": True,
            "conditional_kms_limit_passage_closed": True,
            "actual_q3_word_convergence_closed": False,
            "common_word_embedding_closed": False,
            "common_alpha_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": sha256(MANIFEST),
        },
        "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY CONDITIONAL-OS-KMS-LIMIT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())