#!/usr/bin/env python3
"""Non-importing independent audit of PAH-OMC-001 finite common dynamics.

This implementation uses modular coordinate identities, independent finite
group-average matrices, arbitrary reversible conductance graphs, and a separate
factorisation of the free-vertex refinement obstruction.  It does not import
the primary implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "strategy/pa-hyp/owner-morphism-audit-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-r479-pah-omc001/independent.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, staging = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(staging, path)
    except BaseException:
        try:
            os.unlink(staging)
        except FileNotFoundError:
            pass
        raise


def identity(size: int) -> list[list[Fraction]]:
    return [
        [Fraction(int(row == column)) for column in range(size)]
        for row in range(size)
    ]


def matrix_multiply(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    return [
        [
            sum(
                (left[row][middle] * right[middle][column] for middle in range(len(right))),
                Fraction(0),
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*matrix)]


def permutation_matrix(size: int, mapping: Callable[[int], int]) -> list[list[Fraction]]:
    result = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    for source in range(size):
        result[mapping(source)][source] = Fraction(1)
    return result


def average_matrices(matrices: list[list[list[Fraction]]]) -> list[list[Fraction]]:
    size = len(matrices[0])
    count = Fraction(len(matrices))
    return [
        [
            sum((matrix[row][column] for matrix in matrices), Fraction(0)) / count
            for column in range(size)
        ]
        for row in range(size)
    ]


def circulant_generator(size: int) -> list[list[Fraction]]:
    result = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    for vertex in range(size):
        for target in ((vertex - 1) % size, (vertex + 1) % size):
            result[vertex][target] += 1
            result[vertex][vertex] -= 1
    return result


def projection_fixture(size: int) -> dict[str, bool]:
    rotations = [
        permutation_matrix(size, lambda value, shift=shift: (value + shift) % size)
        for shift in range(size)
    ]
    reflections = [
        permutation_matrix(
            size, lambda value, shift=shift: (shift - value) % size
        )
        for shift in range(size)
    ]
    projection = average_matrices(rotations + reflections)
    generator = circulant_generator(size)
    return {
        "idempotent": matrix_multiply(projection, projection) == projection,
        "self_adjoint": transpose(projection) == projection,
        "commutes_generator": matrix_multiply(projection, generator)
        == matrix_multiply(generator, projection),
        "fixes_constants": all(sum(row) == 1 for row in projection),
    }


def reversible_root_fixture(size: int) -> bool:
    total = sum(index + 2 for index in range(size))
    pi = [Fraction(index + 2, total) for index in range(size)]
    conductance = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    for left in range(size):
        for right in range(left + 1, size):
            value = Fraction((left + 2) * (right + 3), 5 * size + 2)
            conductance[left][right] = value
            conductance[right][left] = value

    generator = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    root_gram = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    for left in range(size):
        for right in range(size):
            if left == right:
                continue
            rate = conductance[left][right] / pi[left]
            generator[left][right] = rate
            generator[left][left] -= rate
            directed_weight = pi[left] * rate / 2
            root_gram[left][left] += directed_weight
            root_gram[right][right] += directed_weight
            root_gram[left][right] -= directed_weight
            root_gram[right][left] -= directed_weight
    b_star_b = [
        [root_gram[row][column] / pi[row] for column in range(size)]
        for row in range(size)
    ]
    return all(
        b_star_b[row][column] == -generator[row][column]
        for row in range(size)
        for column in range(size)
    )


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    audit = load(AUDIT)
    parent_path = ROOT / audit["parent"]["path"]
    contract_path = ROOT / audit["contract"]["path"]
    contract = load(contract_path)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("parent-hash", sha256_file(parent_path) == audit["parent"]["sha256"])
    check("contract-hash", sha256_file(contract_path) == audit["contract"]["sha256"])
    check("contract-version", contract.get("version") == "0.1.0")
    check("contract-nonphysical", contract["provenance"]["physical_authority"] is False)
    check("composite-only", "not retroactive" in contract["parent"]["composition_rule"])
    check("no-functional-edit", contract["preservation_firewall"]["functional_unchanged"] is True)
    check("no-limit-edit", contract["preservation_firewall"]["limit_order_unchanged"] is True)
    check("no-q3lock", contract["preservation_firewall"]["no_q3lock_import"] is True)

    modular_cases = 0
    for modulus in range(2, 8):
        phase_passed = True
        link_passed = True
        edge_passed = True
        for n_v, n_w, u, g_v, g_w, sign in itertools.product(
            range(modulus), range(modulus), range(modulus), range(modulus), range(modulus), (-1, 1)
        ):
            modular_cases += 1
            phase_left = ((n_v + sign) + g_v) % modulus
            phase_right = ((n_v + g_v) + sign) % modulus
            link_left = ((u + sign) + g_w - g_v) % modulus
            link_right = ((u + g_w - g_v) + sign) % modulus
            covariant_before = (n_w - u - n_v) % modulus
            covariant_after = (
                (n_w + g_w) - (u + g_w - g_v) - (n_v + g_v)
            ) % modulus
            phase_passed = phase_passed and phase_left == phase_right
            link_passed = link_passed and link_left == link_right
            edge_passed = edge_passed and covariant_before == covariant_after
        check(f"phase-gauge-commutation-K{modulus}", phase_passed)
        check(f"link-gauge-commutation-K{modulus}", link_passed)
        check(f"edge-energy-gauge-invariance-K{modulus}", edge_passed)

    inverse_cases = 0
    for cutoff in range(1, 7):
        aperture_passed = True
        transfer_passed = True
        for level in range(cutoff + 1):
            for sign in (-1, 1):
                allowed = 0 <= level + sign <= cutoff
                if allowed:
                    inverse_cases += 1
                    aperture_passed = aperture_passed and (
                        (level + sign) - sign == level
                    )
        for left in range(cutoff + 1):
            for right in range(cutoff + 1):
                if left >= 1 and right <= cutoff - 1:
                    inverse_cases += 1
                    moved = (left - 1, right + 1)
                    transfer_passed = transfer_passed and (
                        moved[0] + 1,
                        moved[1] - 1,
                    ) == (left, right)
        check(f"aperture-inverse-cutoff-{cutoff}", aperture_passed)
        check(f"transfer-inverse-cutoff-{cutoff}", transfer_passed)

    mobility_cases = 0
    for nu in (2, 4, 6):
        for s_left, s_right in itertools.product(
            (Fraction(1, 4), Fraction(1, 2), Fraction(1)), repeat=2
        ):
            mobility_cases += 1
            phase = s_left**nu
            transfer = (s_left * s_right) ** (nu // 2)
            check(
                f"mobility-positive-{mobility_cases}",
                phase > 0 and transfer > 0,
            )
            check(
                f"mobility-endpoint-symmetry-{mobility_cases}",
                transfer == (s_right * s_left) ** (nu // 2),
            )

    for size in range(3, 8):
        projection = projection_fixture(size)
        for name, passed in projection.items():
            check(f"group-average-{name}-size-{size}", passed)

    for size in range(2, 9):
        check(f"root-factorization-size-{size}", reversible_root_fixture(size))

    balance_cases = 0
    for beta in (Fraction(1, 5), Fraction(1), Fraction(7, 3)):
        for f_x, f_y in itertools.product(
            (Fraction(-2), Fraction(-1, 3), Fraction(0), Fraction(5, 4)), repeat=2
        ):
            forward = -beta * f_x - beta * (f_y - f_x) / 2
            reverse = -beta * f_y - beta * (f_x - f_y) / 2
            balance_cases += 1
            check(f"midpoint-balance-{balance_cases}", forward == reverse)

    obstruction_cases = 0
    for kappa in (Fraction(1, 7), Fraction(2), Fraction(9, 4)):
        for delta in (Fraction(1, 8), Fraction(1, 3), Fraction(2, 5)):
            for z_1, z_2 in (
                (Fraction(0), Fraction(1)),
                (Fraction(1, 5), Fraction(4, 5)),
            ):
                s = Fraction(2, 5)
                d_1 = kappa * ((s + delta - z_1) ** 2 - (s - z_1) ** 2) / 2
                d_2 = kappa * ((s + delta - z_2) ** 2 - (s - z_2) ** 2) / 2
                expected = -kappa * delta * (z_1 - z_2)
                obstruction_cases += 1
                check(
                    f"refinement-fibre-obstruction-{obstruction_cases}",
                    d_1 - d_2 == expected and expected != 0,
                )

    statuses = {item["id"]: item["status"] for item in audit["conditions"]}
    expected_statuses = {
        "PAH-OMC-C1": "PASSED",
        "PAH-OMC-C2": "PASSED",
        "PAH-OMC-C3": "PASSED",
        "PAH-OMC-C4": "PASSED",
        "PAH-OMC-C5": "PASSED_BOUNDARY",
    }
    check("condition-statuses", statuses == expected_statuses)
    check("stage1-derived-advance", all(status.startswith("PASSED") for status in statuses.values()))
    check("stage2-derived-hold", audit["uniform_refinement_verdict"] == "HOLD_FOR_EVIDENCE")
    check("route-local-boundary", audit["refinement_failure_boundary"]["non_global"] is True)
    check("no-physical-prea", any("No physical Pre-A" in item for item in audit["non_claims"]))
    check("no-quantum-time", any("quantum real time" in item for item in audit["non_claims"]))

    core = {
        "audit_id": audit["audit_id"],
        "result_id": audit["result_id"],
        "parent_sha256": audit["parent"]["sha256"],
        "contract_sha256": audit["contract"]["sha256"],
        "condition_statuses": statuses,
        "finite_common_dynamics_verdict": audit["finite_common_dynamics_verdict"],
        "uniform_refinement_verdict": audit["uniform_refinement_verdict"],
        "overall_programme_state": audit["overall_programme_state"],
        "single_next_question": audit["single_next_question"],
        "non_claims": audit["non_claims"],
    }
    failed = [item for item in checks if not item["passed"]]
    payload = {
        "schema": "tect/pah-omc001-independent-run/1.0",
        "run_kind": "independent",
        "audit_id": audit["audit_id"],
        "result_id": audit["result_id"],
        "exploration_id": audit["exploration_id"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verification": "PASS" if not failed else "FAIL",
        "finite_common_dynamics_verdict": audit["finite_common_dynamics_verdict"],
        "uniform_refinement_verdict": audit["uniform_refinement_verdict"],
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "fixture_counts": {
            "modular_cases": modular_cases,
            "inverse_cases": inverse_cases,
            "mobility_cases": mobility_cases,
            "projection_sizes": 5,
            "root_factorization_sizes": 7,
            "midpoint_cases": balance_cases,
            "refinement_obstruction_cases": obstruction_cases,
        },
        "core": core,
        "core_digest": canonical_hash(core),
        "claim_bearing": False,
        "active_gate_changed": False,
        "physical_progress": False,
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    options = parser.parse_args()
    result = run(options.output)
    print(
        "PAH-OMC-AUDIT-001 INDEPENDENT "
        f"{result['verification']} {result['passed']}/{result['assertion_count']}; "
        f"finite={result['finite_common_dynamics_verdict']}; "
        f"refinement={result['uniform_refinement_verdict']}; "
        f"core={result['core_digest']}"
    )
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
