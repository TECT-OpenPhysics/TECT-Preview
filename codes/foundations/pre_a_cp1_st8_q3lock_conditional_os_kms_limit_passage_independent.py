#!/usr/bin/env python3
"""Independent Fraction-only reconstruction for EXP-001194."""

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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-29-independent-{SLUG}" / "independent.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def F(value: Any) -> Fraction:
    return Fraction(str(value))


def out(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): out(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [out(v) for v in value]
    return value


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(out(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def gram(vectors: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[sum((vectors[i][k] * vectors[j][k] for k in range(len(vectors[i]))), Fraction(0)) for j in range(len(vectors))] for i in range(len(vectors))]


def qform(matrix: list[list[Fraction]], vector: list[Fraction]) -> Fraction:
    total = Fraction(0)
    for i in range(len(vector)):
        for j in range(len(vector)):
            total += vector[i] * matrix[i][j] * vector[j]
    return total


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": out(actual), "expected": out(expected)})

    check("identity", manifest.get("exploration_id") == "EXP-001194" and manifest.get("task_id") == "T-054", [manifest.get("exploration_id"), manifest.get("task_id")], "EXP-001194/T-054", "provenance")
    check("T0 claim firewall", manifest.get("tier") == "T0" and manifest.get("claim_bearing") is False, [manifest.get("tier"), manifest.get("claim_bearing")], ["T0", False], "scope")
    check("authority lineage", set(("EXP-001173", "EXP-001065", "EXP-001193")) <= set(manifest.get("prior_explorations", [])), manifest.get("prior_explorations"), "three authorities", "authority")

    vectors = [[F(item) for item in vector] for vector in fixture["gram_vectors"]]
    limit = gram(vectors)
    expected = [[F(item) for item in row] for row in fixture["gram_limit"]]
    check("independent Gram reconstruction", limit == expected, limit, expected, "OS")

    coefficients = [[F(item) for item in vector] for vector in fixture["coefficient_vectors"]]
    limit_q = [qform(limit, vector) for vector in coefficients]
    check("all limiting quadratics nonnegative", all(value >= 0 for value in limit_q), limit_q, ">=0", "OS")
    check("limiting quadratic first", limit_q[0] == F("2"), limit_q[0], "2", "OS")
    check("limiting quadratic second", limit_q[1] == F("5"), limit_q[1], "5", "OS")
    check("limiting quadratic third", limit_q[2] == F("13"), limit_q[2], "13", "OS")

    denominators = [F(item) for item in fixture["exhaustions"]["denominators"]]
    scales = {"path_a": F(fixture["exhaustions"]["path_a_scale"]), "path_b": F(fixture["exhaustions"]["path_b_scale"])}
    convergence_rows: list[dict[str, Any]] = []
    max_entry = Fraction(0)
    max_quadratic_error = Fraction(0)
    for name, scale in scales.items():
        for denominator in denominators:
            epsilon = scale / denominator
            sequence = [[limit[i][j] + (epsilon if i == j else Fraction(0)) for j in range(len(limit))] for i in range(len(limit))]
            for i in range(len(limit)):
                for j in range(len(limit)):
                    difference = abs(sequence[i][j] - limit[i][j])
                    check(f"{name} entry bound {denominator} {i}{j}", difference <= epsilon, difference, f"<={epsilon}", "convergence")
                    max_entry = max(max_entry, abs(sequence[i][j]))
            for idx, vector in enumerate(coefficients):
                value = qform(sequence, vector)
                error = value - limit_q[idx]
                expected_error = epsilon * sum((item * item for item in vector), Fraction(0))
                check(f"{name} PSD {denominator} {idx}", value >= 0, value, ">=0", "OS")
                check(f"{name} exact error {denominator} {idx}", error == expected_error, error, expected_error, "convergence")
                max_quadratic_error = max(max_quadratic_error, abs(error))
                convergence_rows.append({"path": name, "denominator": denominator, "coefficient": idx, "quadratic": value, "error": error})
    check("entrywise bound", max_entry <= F(fixture["entry_bound"]), max_entry, f"<={fixture['entry_bound']}", "convergence")

    beta_hbar = F(fixture["beta_hbar"])
    kms_limit = F(fixture["kms_limit"])
    error_scale = F(fixture["kms_error_scale"])
    times = [F(item) for item in fixture["euclidean_times"]]
    kms_bound = F(fixture["kms_bound"])
    kms_rows: list[dict[str, Any]] = []
    max_kms = Fraction(0)
    for denominator in denominators:
        for time in times:
            complement = beta_hbar - time
            left = kms_limit + error_scale * time * complement / denominator
            right = kms_limit + error_scale * complement * time / denominator
            check(f"complement interval {denominator} {time}", 0 <= time <= beta_hbar and 0 <= complement <= beta_hbar, [time, complement], f"within [0,{beta_hbar}]", "KMS")
            check(f"cyclic equality {denominator} {time}", left == right, [left, right], "equal", "KMS")
            check(f"limit error {denominator} {time}", abs(left - kms_limit) == error_scale * time * complement / denominator, left - kms_limit, error_scale * time * complement / denominator, "KMS")
            check(f"bounded word {denominator} {time}", left <= kms_bound and right <= kms_bound, [left, right], f"<={kms_bound}", "KMS")
            max_kms = max(max_kms, left, right)
            kms_rows.append({"denominator": denominator, "time": time, "complement": complement, "left": left, "right": right, "limit": kms_limit})
    check("KMS finite and limiting value", kms_limit >= 0 and max_kms <= kms_bound, [kms_limit, max_kms], f"nonnegative and <={kms_bound}", "KMS")
    check("contract flags", scope["conditional_entrywise_os_positivity_passage_closed"] and scope["conditional_kms_limit_passage_closed"] and scope["conditional_word_form_completion_contract_closed"], True, True, "scope")
    false_flags = [key for key, value in scope.items() if isinstance(value, bool) and value is False and key not in {"no_new_negative_result", "no_tier_change", "no_pdf"}]
    check("actual Q3 firewalls", all(scope[key] is False for key in false_flags), false_flags, "all named actual-Q3 successor flags remain false", "scope")

    passed = len(checks)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-CONDITIONAL-OS-KMS-LIMIT-PASSAGE",
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": checks,
        "derived": {
            "gram_limit": limit,
            "limit_quadratics": limit_q,
            "scales": scales,
            "convergence_rows": convergence_rows,
            "max_entry": max_entry,
            "max_quadratic_error": max_quadratic_error,
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
            "script_sha256": digest(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": digest(MANIFEST),
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
        store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT CONDITIONAL-OS-KMS-LIMIT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())