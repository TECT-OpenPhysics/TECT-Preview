#!/usr/bin/env python3
"""Primary exact audit of PAH-001 finite/common-core compatibility.

PASS certifies the recorded HOLD_FOR_EVIDENCE boundary.  It does not fill the
missing move-map, root-Hilbert, or refinement contracts and does not admit the
candidate as physical or production dynamics.
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


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pa-hyp/finite-common-core-audit-v1.json"
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-r478-pah001-common-core/primary.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    data = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def pointer(document: Any, value: str) -> Any:
    current = document
    for raw in value.lstrip("/").split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def matrix_multiply(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    rows = len(a)
    middle = len(b)
    columns = len(b[0])
    return [
        [sum((a[i][k] * b[k][j] for k in range(middle)), Fraction(0)) for j in range(columns)]
        for i in range(rows)
    ]


def matrix_add(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def matrix_scale(value: Fraction, a: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[value * item for item in row] for row in a]


def permutation_matrix(size: int, mapping: Callable[[int], int]) -> list[list[Fraction]]:
    result = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    for source in range(size):
        result[mapping(source)][source] = Fraction(1)
    return result


def transpose(a: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*a)]


def identity(size: int) -> list[list[Fraction]]:
    return [[Fraction(int(i == j)) for j in range(size)] for i in range(size)]


def exact_projection_fixture() -> dict[str, bool]:
    size = 4
    ident = identity(size)
    flip_both = permutation_matrix(size, lambda x: x ^ 3)
    swap_bits = permutation_matrix(size, lambda x: ((x & 1) << 1) | ((x & 2) >> 1))
    p_g = matrix_scale(Fraction(1, 2), matrix_add(ident, flip_both))
    p_aut = matrix_scale(Fraction(1, 2), matrix_add(ident, swap_bits))
    p_cand = matrix_multiply(p_aut, p_g)

    laplacian = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    for x in range(size):
        for bit in (1, 2):
            y = x ^ bit
            laplacian[x][y] += 1
            laplacian[x][x] -= 1
    return {
        "pg_idempotent": matrix_multiply(p_g, p_g) == p_g,
        "paut_idempotent": matrix_multiply(p_aut, p_aut) == p_aut,
        "averages_commute": matrix_multiply(p_g, p_aut) == matrix_multiply(p_aut, p_g),
        "pcand_idempotent": matrix_multiply(p_cand, p_cand) == p_cand,
        "pcand_self_adjoint": transpose(p_cand) == p_cand,
        "equivariant_fixture_commutes": matrix_multiply(p_cand, laplacian)
        == matrix_multiply(laplacian, p_cand),
    }


def exact_dirichlet_fixture(size: int) -> bool:
    total = sum(range(1, size + 1))
    pi = [Fraction(index + 1, total) for index in range(size)]
    conductance = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    for x in range(size):
        for y in range(x + 1, size):
            value = Fraction((x + 1) * (y + 2), 3 * size + 1)
            conductance[x][y] = value
            conductance[y][x] = value

    generator = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    gram = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    for x in range(size):
        for y in range(size):
            if x == y:
                continue
            rate = conductance[x][y] / pi[x]
            generator[x][y] = rate
            generator[x][x] -= rate
            weight = pi[x] * rate / 2
            gram[x][x] += weight
            gram[y][y] += weight
            gram[x][y] -= weight
            gram[y][x] -= weight

    b_star_b = [[gram[x][y] / pi[x] for y in range(size)] for x in range(size)]
    return all(
        b_star_b[x][y] == -generator[x][y]
        for x in range(size)
        for y in range(size)
    )


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = load_json(MANIFEST)
    source_path = REPO / manifest["source"]["path"]
    source = load_json(source_path)
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    check("manifest-schema", manifest.get("schema") == "tect/pah001-finite-common-core-audit/1.0")
    check("audit-id", manifest.get("audit_id") == "PAH-FCC-001")
    check("result-id", manifest.get("result_id") == "R-478")
    check("exploration-id", manifest.get("exploration_id") == "EXP-001359")
    check("task-id", manifest.get("task_id") == "T-054")
    check("claim-nonbearing", manifest.get("claim_bearing") is False)
    check("declared-hold", manifest.get("verdict") == "HOLD_FOR_EVIDENCE")
    check("gate-unchanged", manifest.get("gate_changed") is False)
    check("no-negative", manifest.get("negative_result_registered") is False)
    check("no-model-mutation", not any(manifest.get("model_mutation", {}).values()))

    actual_source_hash = sha256_file(source_path)
    check("source-hash", actual_source_hash == manifest["source"]["sha256"], actual_source_hash)
    check("source-packet", source.get("packet_id") == "PAH-001")
    check("source-candidate", source.get("candidate_id") == manifest["source"]["candidate_id"])
    check("source-immutable", "PAH-001-v2" in source.get("immutability", ""))
    for item in manifest["context_pins"]:
        actual = sha256_file(REPO / item["path"])
        check("context-hash-" + Path(item["path"]).name, actual == item["sha256"], actual)

    exact = manifest["exact_expressions"]
    for field, expected_field in (
        ("functional_pointer", "functional"),
        ("projection_pointer", "candidate_projection"),
        ("generator_pointer", "generator"),
        ("state_pointer", "state"),
        ("root_pointer", "root"),
        ("common_core_pointer", "common_core"),
    ):
        observed = pointer(source, exact[field])
        check("exact-" + expected_field, observed == exact[expected_field], observed)

    check("finite-counting-normalization", "counting measure" in source["finite_regulator"]["normalization"])
    check("fixed-q", "sum_v ell_v=Q" in source["microscopic_degrees_of_freedom"]["matter"])
    check("positive-epsilon", "0<epsilon<=1" in source["finite_regulator"]["aperture_floor"])
    check("markov-time-only", "external stochastic time" in source["dynamics"]["time"])
    check("no-quantum-time", "no quantum KMS or proper-time" in source["dynamics"]["thermal_boundary"])

    edge_cases = 0
    for modulus in range(2, 10):
        passed = True
        for n_v, n_w, edge, g_v, g_w in itertools.product(range(modulus), repeat=5):
            before = (n_w - edge - n_v) % modulus
            after = ((n_w + g_w) - (edge + g_w - g_v) - (n_v + g_v)) % modulus
            edge_cases += 1
            if before != after:
                passed = False
                break
        check(f"gauge-edge-covariance-K{modulus}", passed)

    plaquette_cases = 0
    for modulus in range(2, 7):
        for length in (3, 4, 5, 6):
            passed = True
            for gauge in itertools.product(range(modulus), repeat=length):
                edges = tuple((3 * index + 1) % modulus for index in range(length))
                transformed = tuple(
                    (edges[index] + gauge[(index + 1) % length] - gauge[index]) % modulus
                    for index in range(length)
                )
                plaquette_cases += 1
                if sum(transformed) % modulus != sum(edges) % modulus:
                    passed = False
                    break
            check(f"plaquette-telescope-K{modulus}-n{length}", passed)

    detailed_balance_cases = 0
    values = [Fraction(-3, 2), Fraction(-1, 3), Fraction(0), Fraction(2, 5), Fraction(7, 4)]
    for beta in (Fraction(1, 3), Fraction(1), Fraction(5, 2)):
        for f_x, f_y in itertools.product(values, repeat=2):
            left = -beta * f_x - beta * (f_y - f_x) / 2
            right = -beta * f_y - beta * (f_x - f_y) / 2
            detailed_balance_cases += 1
            check(f"detailed-balance-midpoint-{detailed_balance_cases}", left == right, [str(left), str(right)])
    check("inverse-mobility-symmetry", source["dynamics"]["mobility_rule"]["symmetry"] == "m_r(x)=m_(r^(-1))(r x)")
    check("generator-fixes-one", "[f(r x)-f(x)]" in source["dynamics"]["generator"])

    projection = exact_projection_fixture()
    for name, passed in projection.items():
        check("projection-fixture-" + name, passed)
    check("gauge-average-unitary-premise", source["functional_or_action"]["gauge_invariance_status"] == "THEOREM_TARGET_NOT_YET_AUDITED")
    check("move-set-is-prose", all(isinstance(item, str) for item in source["dynamics"]["move_set"]))
    check("move-set-has-four-types", len(source["dynamics"]["move_set"]) == 4)
    check("no-exact-move-map-object", "move_maps" not in source["dynamics"])
    check("no-move-equivariance-contract", "equivariance" not in source["dynamics"])

    for size in range(2, 7):
        check(f"conditional-dirichlet-factor-size-{size}", exact_dirichlet_fixture(size))
    root_slot = source["r471_owner_slots"][4]
    check("root-slot-identity", root_slot["id"] == "heat_root_incidence")
    check("root-target-unproved", root_slot["proof_status"] == "UNPROVED_HYPOTHESIS")
    check("root-no-inner-product", "inner_product" not in root_slot)
    check("root-no-measure", "measure" not in root_slot)
    check("root-no-multiplicity", "multiplicity" not in root_slot)
    check("root-codomain-only-name", root_slot["codomain"] == "the directed-move root Hilbert space")

    common = source["common_core_and_uniform_contract"]
    lattice = source["ordered_limits"]["order"][1]
    check("common-core-only-string", isinstance(common["common_core"], str))
    check("missing-compatibility-explicit", "refinement embeddings" in common["missing_compatibility"] and "generator agreement" in common["missing_compatibility"])
    check("no-refinement-map-object", "refinement_embeddings" not in source)
    check("lattice-refinement-id", lattice["id"] == "LATTICE_REFINEMENT")
    check("lattice-topology-unspecified", lattice["topology"] == "to be specified")
    check("lattice-status-unproved", lattice["status"] == "DECLARED_NOT_PROVED")
    check("no-continuum-uniform-estimate", common["continuum_uniform_estimate"] is False)

    statuses = {item["id"]: item["status"] for item in manifest["conditions"]}
    expected_statuses = {
        "PAH-FCC-C1": "PASSED",
        "PAH-FCC-C2": "PASSED",
        "PAH-FCC-C3": "PARTIAL_NOT_CLOSED",
        "PAH-FCC-C4": "PARTIAL_NOT_CLOSED",
        "PAH-FCC-C5": "NOT_DEFINED",
    }
    check("condition-statuses", statuses == expected_statuses, statuses)
    vector = [statuses[f"PAH-FCC-C{index}"] == "PASSED" for index in range(1, 6)]
    check("condition-vector", vector == manifest["decision_rule"]["condition_vector"], vector)
    check("no-exact-counterexample", manifest["decision_rule"]["exact_counterexample_found"] is False)
    derived = "MAINLINE_ADVANCE" if all(vector) else "NEGATIVE_RESULT" if manifest["decision_rule"]["exact_counterexample_found"] else "HOLD_FOR_EVIDENCE"
    check("derived-verdict", derived == manifest["decision_rule"]["derived_verdict"], derived)
    next_question = manifest["single_next_question"]
    check(
        "single-next-question",
        "finite common-core morphism contract" in next_question
        and "exact partial move maps" in next_question
        and "directed-root Hilbert measure" in next_question
        and "refinement embedding" in next_question,
    )
    check("physical-nonclaim", any("No physical Pre-A" in item for item in manifest["non_claims"]))
    check("q3lock-nonimport", any("No Q3LOCK" in item for item in manifest["non_claims"]))

    core = {
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "source_sha256": manifest["source"]["sha256"],
        "condition_statuses": statuses,
        "condition_vector": vector,
        "verdict": derived,
        "next_question": manifest["single_next_question"],
        "non_claims": manifest["non_claims"],
    }
    failed = [item for item in checks if not item["passed"]]
    payload = {
        "schema": "tect/pah001-finite-common-core-audit-run/1.0",
        "run_kind": "primary",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verification": "PASS" if not failed else "FAIL",
        "verdict": derived,
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "fixture_counts": {
            "gauge_edge_cases": edge_cases,
            "plaquette_cases": plaquette_cases,
            "detailed_balance_cases": detailed_balance_cases,
            "dirichlet_sizes": 5,
            "projection_assertions": len(projection),
        },
        "core": core,
        "core_digest": canonical_hash(core),
        "claim_bearing": False,
        "gate_changed": False,
        "scientific_transition": False,
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    options = parser.parse_args()
    result = run(options.output)
    print(
        "PAH-FCC-001 PRIMARY "
        f"{result['verification']} {result['passed']}/{result['assertion_count']}; "
        f"verdict={result['verdict']}; core={result['core_digest']}"
    )
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
