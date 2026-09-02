#!/usr/bin/env python3
"""Non-importing independent reconstruction of PAH-FCC-001."""

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
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "strategy/pa-hyp/finite-common-core-audit-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-r478-pah001-common-core/independent.json"
)


def object_hash(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if type(value) is not dict:
        raise ValueError(path)
    return value


def follow(value: Any, address: str) -> Any:
    for token in address[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if type(value) is list else value[token]
    return value


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, staging = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(staging, path)
    except BaseException:
        try:
            os.unlink(staging)
        except FileNotFoundError:
            pass
        raise


Permutation = tuple[int, int, int]


def compose(p: Permutation, q: Permutation) -> Permutation:
    return tuple(p[q[index]] for index in range(3))  # type: ignore[return-value]


def inverse(p: Permutation) -> Permutation:
    result = [0, 0, 0]
    for index, image in enumerate(p):
        result[image] = index
    return tuple(result)  # type: ignore[return-value]


def parity(p: Permutation) -> int:
    inversions = sum(p[i] > p[j] for i in range(3) for j in range(i + 1, 3))
    return inversions % 2


def permutation_average(
    states: list[Permutation], actions: list[dict[Permutation, Permutation]]
) -> list[list[Fraction]]:
    index = {state: position for position, state in enumerate(states)}
    matrix = [[Fraction(0) for _ in states] for _ in states]
    for action in actions:
        for source in states:
            matrix[index[action[source]]][index[source]] += Fraction(1, len(actions))
    return matrix


def multiply(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [
            sum((a[i][k] * b[k][j] for k in range(len(b))), Fraction(0))
            for j in range(len(b[0]))
        ]
        for i in range(len(a))
    ]


def transposed(a: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*a)]


def s3_projection_fixture() -> dict[str, bool]:
    states = list(itertools.permutations(range(3)))
    identity: Permutation = (0, 1, 2)
    even = [state for state in states if parity(state) == 0]
    reflection: Permutation = (1, 0, 2)

    gauge_actions = [
        {state: compose(element, state) for state in states} for element in even
    ]
    aut_actions = [
        {state: state for state in states},
        {
            state: compose(compose(reflection, state), inverse(reflection))
            for state in states
        },
    ]
    p_g = permutation_average(states, gauge_actions)
    p_a = permutation_average(states, aut_actions)
    p = multiply(p_a, p_g)

    state_index = {state: index for index, state in enumerate(states)}
    transpositions = [state for state in states if parity(state) == 1]
    generator = [[Fraction(0) for _ in states] for _ in states]
    for state in states:
        source = state_index[state]
        for step in transpositions:
            target = state_index[compose(state, step)]
            generator[source][target] += 1
            generator[source][source] -= 1
    return {
        "pg_square": multiply(p_g, p_g) == p_g,
        "pa_square": multiply(p_a, p_a) == p_a,
        "commuting_averages": multiply(p_a, p_g) == multiply(p_g, p_a),
        "product_square": multiply(p, p) == p,
        "product_symmetric": transposed(p) == p,
        "equivariant_fixture": multiply(p, generator) == multiply(generator, p),
        "nonempty_group": identity in even,
    }


def bilinear_dirichlet_fixture(size: int, seed: int) -> bool:
    raw_pi = [Fraction((index + 1) * (seed + 2), seed + 5) for index in range(size)]
    total = sum(raw_pi, Fraction(0))
    pi = [value / total for value in raw_pi]
    conductance = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    for x in range(size):
        for y in range(x + 1, size):
            value = Fraction((x + y + seed + 2) ** 2, 7 + size + seed)
            conductance[x][y] = conductance[y][x] = value
    f = [Fraction((index + 2) * (seed + 1), index + seed + 2) for index in range(size)]
    g = [Fraction((index + 1) ** 2 - seed, index + 3) for index in range(size)]

    root_pairing = Fraction(0)
    generator_pairing = Fraction(0)
    for x in range(size):
        local = Fraction(0)
        for y in range(size):
            if x == y:
                continue
            rate = conductance[x][y] / pi[x]
            root_pairing += pi[x] * rate * (f[y] - f[x]) * (g[y] - g[x]) / 2
            local += rate * (g[y] - g[x])
        generator_pairing += pi[x] * f[x] * (-local)
    return root_pairing == generator_pairing


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    spec = load(SPEC_PATH)
    source_path = ROOT / spec["source"]["path"]
    source = load(source_path)
    tests: list[dict[str, Any]] = []

    def test(name: str, passed: bool, observed: Any = "") -> None:
        tests.append({"name": name, "passed": bool(passed), "observed": observed})

    test("identity", (spec.get("audit_id"), spec.get("result_id"), spec.get("exploration_id")) == ("PAH-FCC-001", "R-478", "EXP-001359"))
    test("source-digest", file_hash(source_path) == spec["source"]["sha256"], file_hash(source_path))
    test("immutable-version", source.get("version") == "0.1.0" and "immutable" in source.get("immutability", "").lower())
    test("researcher-hypothesis", source["provenance"].get("class") == "RESEARCHER_HYPOTHESIS")
    test("not-physical-authority", source["provenance"].get("physical_authority") is False)
    test("model-untouched", not any(spec.get("model_mutation", {}).values()))
    for item in spec["context_pins"]:
        actual = file_hash(ROOT / item["path"])
        test("pin-" + Path(item["path"]).stem, actual == item["sha256"], actual)

    exact = spec["exact_expressions"]
    pointer_pairs = {
        "functional_pointer": "functional",
        "gauge_action_pointer": None,
        "projection_pointer": "candidate_projection",
        "move_set_pointer": None,
        "mobility_pointer": None,
        "generator_pointer": "generator",
        "state_pointer": "state",
        "root_pointer": "root",
        "common_core_pointer": "common_core",
        "refinement_gap_pointer": None,
    }
    for pointer_name, literal_name in pointer_pairs.items():
        observed = follow(source, exact[pointer_name])
        test("pointer-" + pointer_name, observed is not None)
        if literal_name is not None:
            test("literal-" + literal_name, observed == exact[literal_name], observed)

    gauge_cases = 0
    for modulus in range(2, 9):
        for values in itertools.product(range(modulus), repeat=5):
            matter_v, matter_w, link, gauge_v, gauge_w = values
            original_pair = (matter_w, link + matter_v)
            transformed_pair = (
                matter_w + gauge_w,
                link + gauge_w - gauge_v + matter_v + gauge_v,
            )
            original_relative = (original_pair[0] - original_pair[1]) % modulus
            transformed_relative = (transformed_pair[0] - transformed_pair[1]) % modulus
            gauge_cases += 1
            if original_relative != transformed_relative:
                test("gauge-covariance-exhaustive", False, [modulus, values])
                break
        else:
            test(f"gauge-covariance-K{modulus}", True)

    for length in range(3, 10):
        coefficients = [0 for _ in range(length)]
        for edge in range(length):
            coefficients[edge] -= 1
            coefficients[(edge + 1) % length] += 1
        test(f"closed-loop-telescope-{length}", coefficients == [0] * length, coefficients)

    midpoint_cases = 0
    for beta, left_energy, right_energy in itertools.product(
        [Fraction(1, 7), Fraction(1), Fraction(11, 3)],
        [Fraction(-2), Fraction(-1, 4), Fraction(0), Fraction(5, 6)],
        [Fraction(-7, 5), Fraction(0), Fraction(2, 3), Fraction(3)],
    ):
        forward = -beta * left_energy - beta * (right_energy - left_energy) / 2
        reverse = -beta * right_energy - beta * (left_energy - right_energy) / 2
        midpoint_cases += 1
        test(f"midpoint-{midpoint_cases}", forward == reverse, [str(forward), str(reverse)])
    test("declared-inverse-rule", source["dynamics"]["inverse_pair_rule"] == "Every move r has an explicit inverse r^(-1).")
    test("declared-mobility-rule", source["dynamics"]["mobility_rule"]["symmetry"] == "m_r(x)=m_(r^(-1))(r x)")

    projection_checks = s3_projection_fixture()
    for name, passed in projection_checks.items():
        test("s3-" + name, passed)

    for size in range(2, 7):
        for seed in range(1, 5):
            test(f"bilinear-dirichlet-n{size}-s{seed}", bilinear_dirichlet_fixture(size, seed))

    move_set = source["dynamics"]["move_set"]
    root = source["r471_owner_slots"][4]
    common = source["common_core_and_uniform_contract"]
    refinement = source["ordered_limits"]["order"][1]
    test("move-types-prose-only", len(move_set) == 4 and all(type(item) is str for item in move_set))
    test("move-maps-absent", "move_maps" not in source["dynamics"])
    test("transition-equivariance-absent", "equivariance" not in source["dynamics"])
    test("root-slot", root.get("id") == "heat_root_incidence")
    test("root-adjoint-target-only", "target B^*B=-L_rho" in root.get("equation", "") and root.get("proof_status") == "UNPROVED_HYPOTHESIS")
    test("root-inner-product-absent", not any(key in root for key in ("inner_product", "measure", "multiplicity")))
    test("common-core-description-only", type(common.get("common_core")) is str)
    test("compatibility-self-declared-missing", all(word in common.get("missing_compatibility", "") for word in ("refinement embeddings", "generator agreement", "boundary-error decay", "Cauchy convergence")))
    test("refinement-object-absent", "refinement_embeddings" not in source)
    test("refinement-topology-unset", refinement.get("topology") == "to be specified")
    test("refinement-unproved", refinement.get("status") == "DECLARED_NOT_PROVED")

    statuses = {item["id"]: item["status"] for item in spec["conditions"]}
    reconstructed = {
        "PAH-FCC-C1": "PASSED",
        "PAH-FCC-C2": "PASSED",
        "PAH-FCC-C3": "PARTIAL_NOT_CLOSED",
        "PAH-FCC-C4": "PARTIAL_NOT_CLOSED",
        "PAH-FCC-C5": "NOT_DEFINED",
    }
    test("status-reconstruction", statuses == reconstructed, statuses)
    vector = [statuses[f"PAH-FCC-C{index}"] == "PASSED" for index in range(1, 6)]
    test("vector", vector == [True, True, False, False, False], vector)
    target_counterexample = False
    verdict = "MAINLINE_ADVANCE" if all(vector) else "NEGATIVE_RESULT" if target_counterexample else "HOLD_FOR_EVIDENCE"
    test("verdict", verdict == spec["verdict"], verdict)
    test("next-contract", all(text in spec["single_next_question"] for text in ("exact partial move maps", "directed-root Hilbert measure", "refinement embedding")))
    test("physical-firewall", any("No physical Pre-A" in text for text in spec["non_claims"]))
    test("q3lock-firewall", any("No Q3LOCK" in text for text in spec["non_claims"]))

    core = {
        "audit_id": spec["audit_id"],
        "result_id": spec["result_id"],
        "source_sha256": spec["source"]["sha256"],
        "condition_statuses": statuses,
        "condition_vector": vector,
        "verdict": verdict,
        "next_question": spec["single_next_question"],
        "non_claims": spec["non_claims"],
    }
    failures = [item for item in tests if not item["passed"]]
    result = {
        "schema": "tect/pah001-finite-common-core-audit-run/1.0",
        "run_kind": "independent",
        "audit_id": spec["audit_id"],
        "result_id": spec["result_id"],
        "exploration_id": spec["exploration_id"],
        "task_id": spec["task_id"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verification": "PASS" if not failures else "FAIL",
        "verdict": verdict,
        "assertion_count": len(tests),
        "passed": len(tests) - len(failures),
        "failed": len(failures),
        "assertions": tests,
        "fixture_counts": {
            "gauge_cases": gauge_cases,
            "midpoint_cases": midpoint_cases,
            "dirichlet_bilinear_cases": 20,
            "projection_assertions": len(projection_checks),
        },
        "core": core,
        "core_digest": object_hash(core),
        "claim_bearing": False,
        "gate_changed": False,
        "scientific_transition": False,
    }
    write(output, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    options = parser.parse_args()
    result = run(options.output)
    print(
        "PAH-FCC-001 INDEPENDENT "
        f"{result['verification']} {result['passed']}/{result['assertion_count']}; "
        f"verdict={result['verdict']}; core={result['core_digest']}"
    )
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
