#!/usr/bin/env python3
"""Primary exact audit of the PAH-001 plus PAH-OMC-001 composite model.

The finite fixture enumerates every state and directed root of a three-vertex
anchored path.  It checks fixed-Q inverse closure, gauge/anchor equivariance,
formal-exponential generator commutation, the directed-root Dirichlet identity,
and the exact free-vertex refinement obstruction.  PASS advances only the
finite common-dynamics stage; the uniform-refinement programme remains held.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Iterable


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "strategy/pa-hyp/owner-morphism-audit-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-r479-pah-omc001/primary.json"
)

K = 2
M_S = 1
M_PSI = 1
Q = 1
EPSILON = Fraction(1, 2)
BETA = Fraction(3, 2)
EDGES = ((0, 1), (1, 2))
VERTEX_IMAGE = (2, 1, 0)
EDGE_IMAGE = ((1, -1), (0, -1))

State = tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...], tuple[int, ...]]
Root = tuple[str, int, int]
Formal = dict[Fraction, Fraction]


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


def aperture(j: int) -> Fraction:
    return EPSILON + Fraction(j) * (1 - EPSILON) / M_S


def states() -> list[State]:
    occupations = [
        value
        for value in itertools.product(range(M_PSI + 1), repeat=3)
        if sum(value) == Q
    ]
    return [
        (j, ell, n, u)
        for j in itertools.product(range(M_S + 1), repeat=3)
        for ell in occupations
        for n in itertools.product(range(K), repeat=3)
        for u in itertools.product(range(K), repeat=len(EDGES))
    ]


def roots() -> list[Root]:
    result: list[Root] = []
    for vertex in range(3):
        for sign in (-1, 1):
            result.append(("PH", vertex, sign))
    for edge in range(len(EDGES)):
        for direction in (-1, 1):
            result.append(("TR", edge, direction))
        for sign in (-1, 1):
            result.append(("LK", edge, sign))
    for vertex in range(3):
        for sign in (-1, 1):
            result.append(("AP", vertex, sign))
    return result


def endpoints(root: Root) -> tuple[int, int]:
    _, edge, direction = root
    left, right = EDGES[edge]
    return (left, right) if direction == 1 else (right, left)


def admissible(state: State, root: Root) -> bool:
    j, ell, _, _ = state
    family, location, sign = root
    if family in {"PH", "LK"}:
        return True
    if family == "AP":
        return 0 <= j[location] + sign <= M_S
    if family == "TR":
        source, target = endpoints(root)
        return ell[source] >= 1 and ell[target] <= M_PSI - 1
    raise AssertionError(root)


def apply_root(state: State, root: Root) -> State:
    if not admissible(state, root):
        raise ValueError("inadmissible root")
    j, ell, n, u = map(list, state)
    family, location, sign = root
    if family == "PH":
        n[location] = (n[location] + sign) % K
    elif family == "TR":
        source, target = endpoints(root)
        ell[source] -= 1
        ell[target] += 1
    elif family == "LK":
        u[location] = (u[location] + sign) % K
    elif family == "AP":
        j[location] += sign
    else:
        raise AssertionError(root)
    return tuple(j), tuple(ell), tuple(n), tuple(u)


def inverse_root(root: Root) -> Root:
    family, location, sign = root
    return family, location, -sign


def gauge_action(state: State, gauge: tuple[int, ...]) -> State:
    j, ell, n, u = state
    transformed_n = tuple((n[v] + gauge[v]) % K for v in range(3))
    transformed_u = tuple(
        (u[index] + gauge[right] - gauge[left]) % K
        for index, (left, right) in enumerate(EDGES)
    )
    return j, ell, transformed_n, transformed_u


def automorphism_action(state: State) -> State:
    j, ell, n, u = state
    target_j = [0] * 3
    target_ell = [0] * 3
    target_n = [0] * 3
    target_u = [0] * len(EDGES)
    for source in range(3):
        target = VERTEX_IMAGE[source]
        target_j[target] = j[source]
        target_ell[target] = ell[source]
        target_n[target] = n[source]
    for source, value in enumerate(u):
        target, orientation = EDGE_IMAGE[source]
        target_u[target] = (orientation * value) % K
    return tuple(target_j), tuple(target_ell), tuple(target_n), tuple(target_u)


def automorphism_root(root: Root) -> Root:
    family, location, sign = root
    if family in {"PH", "AP"}:
        return family, VERTEX_IMAGE[location], sign
    target, orientation = EDGE_IMAGE[location]
    if family in {"TR", "LK"}:
        return family, target, orientation * sign
    raise AssertionError(root)


def symmetry_action(
    state: State, gauge: tuple[int, ...], reflect: bool
) -> State:
    transformed = gauge_action(state, gauge)
    return automorphism_action(transformed) if reflect else transformed


def symmetry_root(root: Root, reflect: bool) -> Root:
    return automorphism_root(root) if reflect else root


def energy(state: State) -> Fraction:
    j, ell, n, u = state
    s = tuple(aperture(value) for value in j)
    psi = tuple(Fraction(ell[v] * (-1 if n[v] else 1)) for v in range(3))
    total = Fraction(0)
    for v in range(3):
        total += (s[v] - 1) ** 2 / 2
        total += psi[v] ** 2 / 2
        total += psi[v] ** 4 / 4
        total += psi[v] ** 6 / 6
        total += s[v] ** 2 * psi[v] ** 2 / 2
    for index, (left, right) in enumerate(EDGES):
        stiffness = Fraction(2, 1) / (s[left] + s[right])
        link = -1 if u[index] else 1
        total += (s[left] - s[right]) ** 2 / 2
        total += stiffness * (psi[right] - link * psi[left]) ** 2 / 2
    return total


def mobility(state: State, root: Root) -> Fraction:
    j, _, _, _ = state
    family, location, sign = root
    s = tuple(aperture(value) for value in j)
    if family == "PH":
        return s[location] ** 2
    if family in {"TR", "LK"}:
        left, right = EDGES[location]
        return s[left] * s[right]
    if family == "AP":
        return s[location] * aperture(j[location] + sign)
    raise AssertionError(root)


def add_formal(target: Formal, source: Formal, scale: Fraction = Fraction(1)) -> None:
    for exponent, coefficient in source.items():
        target[exponent] = target.get(exponent, Fraction(0)) + scale * coefficient
        if target[exponent] == 0:
            del target[exponent]


def formal_generator(
    state: State, function: Callable[[State], Fraction], all_roots: list[Root]
) -> Formal:
    result: Formal = {}
    e_x = energy(state)
    for root in all_roots:
        if not admissible(state, root):
            continue
        target = apply_root(state, root)
        exponent = -BETA * (energy(target) - e_x) / 2
        coefficient = mobility(state, root) * (function(target) - function(state))
        if coefficient:
            result[exponent] = result.get(exponent, Fraction(0)) + coefficient
            if result[exponent] == 0:
                del result[exponent]
    return result


def average_function(
    function: Callable[[State], Fraction], state: State, gauges: list[tuple[int, ...]]
) -> Fraction:
    values = [
        function(symmetry_action(state, gauge, reflect))
        for gauge in gauges
        for reflect in (False, True)
    ]
    return sum(values, Fraction(0)) / len(values)


def average_formal(
    function: Callable[[State], Fraction],
    state: State,
    gauges: list[tuple[int, ...]],
    all_roots: list[Root],
) -> Formal:
    result: Formal = {}
    group_size = 2 * len(gauges)
    for gauge in gauges:
        for reflect in (False, True):
            add_formal(
                result,
                formal_generator(symmetry_action(state, gauge, reflect), function, all_roots),
                Fraction(1, group_size),
            )
    return result


def formal_gibbs_pair(
    left: Callable[[State], Fraction],
    right: Callable[[State], Fraction],
    all_states: Iterable[State],
) -> Formal:
    result: Formal = {}
    for state in all_states:
        coefficient = left(state) * right(state)
        if coefficient:
            exponent = -BETA * energy(state)
            result[exponent] = result.get(exponent, Fraction(0)) + coefficient
    return {key: value for key, value in result.items() if value}


def formal_dirichlet_pair(
    left: Callable[[State], Fraction],
    right: Callable[[State], Fraction],
    all_states: Iterable[State],
    all_roots: list[Root],
) -> tuple[Formal, Formal]:
    b_pair: Formal = {}
    minus_l_pair: Formal = {}
    for state in all_states:
        e_x = energy(state)
        for root in all_roots:
            if not admissible(state, root):
                continue
            target = apply_root(state, root)
            exponent = -BETA * (e_x + energy(target)) / 2
            delta_left = left(target) - left(state)
            delta_right = right(target) - right(state)
            b_pair[exponent] = b_pair.get(exponent, Fraction(0)) + (
                mobility(state, root) * delta_left * delta_right / 2
            )
            minus_l_pair[exponent] = minus_l_pair.get(exponent, Fraction(0)) - (
                left(state) * mobility(state, root) * delta_right
            )
    return (
        {key: value for key, value in b_pair.items() if value},
        {key: value for key, value in minus_l_pair.items() if value},
    )


def refinement_obstruction(
    kappa_s: Fraction, s: Fraction, delta: Fraction, z_1: Fraction, z_2: Fraction
) -> tuple[Fraction, Fraction]:
    def added_increment(z: Fraction) -> Fraction:
        return kappa_s * ((s + delta - z) ** 2 - (s - z) ** 2) / 2

    direct = added_increment(z_1) - added_increment(z_2)
    factored = -kappa_s * delta * (z_1 - z_2)
    return direct, factored


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    audit = load(AUDIT)
    parent_path = ROOT / audit["parent"]["path"]
    contract_path = ROOT / audit["contract"]["path"]
    parent = load(parent_path)
    contract = load(contract_path)
    all_states = states()
    state_set = set(all_states)
    all_roots = roots()
    gauges = list(itertools.product(range(K), repeat=3))
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("audit-schema", audit.get("schema") == "tect/pah-owner-morphism-audit/1.0")
    check("audit-id", audit.get("audit_id") == "PAH-OMC-AUDIT-001")
    check("result-id", audit.get("result_id") == "R-479")
    check("exploration-id", audit.get("exploration_id") == "EXP-001361")
    check("parent-hash", sha256_file(parent_path) == audit["parent"]["sha256"], sha256_file(parent_path))
    check("contract-hash", sha256_file(contract_path) == audit["contract"]["sha256"], sha256_file(contract_path))
    check("parent-identity", parent.get("packet_id") == "PAH-001")
    check("contract-identity", contract.get("contract_id") == "PAH-OMC-001")
    check("separate-successor", contract["parent"]["composition_rule"].startswith("This contract supplements"))
    check("parent-preserved", contract["preservation_firewall"]["functional_unchanged"] is True)
    check("no-q3lock", contract["preservation_firewall"]["no_q3lock_import"] is True)
    for firewall_key in (
        "gauge_group_unchanged",
        "move_families_unchanged",
        "mobility_exponent_nu_unchanged",
        "candidate_projection_unchanged",
        "regulator_unchanged",
        "limit_order_unchanged",
        "no_new_hamiltonian_or_counterterm",
    ):
        check(
            "firewall-" + firewall_key,
            contract["preservation_firewall"].get(firewall_key) is True,
        )
    check(
        "contract-finite-status",
        contract["status"]["finite_common_dynamics"]
        == "DEFINED_PENDING_EXACT_AUDIT",
    )
    check(
        "contract-refinement-status",
        contract["status"]["nontrivial_refinement"]
        == "WITHHELD_PENDING_NEW_OWNER_CHOICE",
    )
    check("finite-stage-advance", audit["finite_common_dynamics_verdict"] == "MAINLINE_ADVANCE")
    check("uniform-stage-hold", audit["uniform_refinement_verdict"] == "HOLD_FOR_EVIDENCE")
    check("active-gate-unchanged", audit["active_gate_changed"] is False)
    check("state-count", len(all_states) == 768, len(all_states))
    check("root-label-count", len(all_roots) == 20, len(all_roots))

    expected_families = {"phase", "matter_transfer", "link", "aperture"}
    check(
        "four-exact-families",
        set(contract["universal_directed_root_labels"]) == expected_families,
    )
    for field in (
        "invalid_partial_move",
        "parallel_edges",
        "K_equals_2",
        "zero_radius_phase",
        "channel_counting",
    ):
        check("convention-" + field, bool(contract["invalid_and_duplicate_conventions"].get(field)))

    inverse_cases = 0
    fixed_q_cases = 0
    for state in all_states:
        for root in all_roots:
            if not admissible(state, root):
                continue
            target = apply_root(state, root)
            inverse_cases += 1
            check_name = None
            if target not in state_set:
                check_name = "target-outside-state-space"
            elif not admissible(target, inverse_root(root)):
                check_name = "inverse-not-admissible"
            elif apply_root(target, inverse_root(root)) != state:
                check_name = "inverse-not-exact"
            elif sum(target[1]) != Q:
                check_name = "fixed-q-failure"
            if check_name:
                raise AssertionError((check_name, state, root, target))
            fixed_q_cases += 1
    check("all-partial-bijections-inverse-closed", inverse_cases == fixed_q_cases, inverse_cases)

    collision_state = all_states[0]
    for family in ("PH", "LK"):
        location = 0
        plus = (family, location, 1)
        minus = (family, location, -1)
        check(
            f"K2-{family.lower()}-duplicate-map",
            apply_root(collision_state, plus) == apply_root(collision_state, minus),
        )
        check(f"K2-{family.lower()}-labels-distinct", plus != minus)

    energy_cache = {state: energy(state) for state in all_states}
    equivariance_cases = 0
    for gauge_index, gauge in enumerate(gauges):
        passed = True
        for reflect in (False, True):
            for state in all_states:
                transformed_state = symmetry_action(state, gauge, reflect)
                if energy_cache[transformed_state] != energy_cache[state]:
                    passed = False
                    break
                for root in all_roots:
                    transformed_root = symmetry_root(root, reflect)
                    if admissible(state, root) != admissible(transformed_state, transformed_root):
                        passed = False
                        break
                    if admissible(state, root):
                        equivariance_cases += 1
                        left = symmetry_action(apply_root(state, root), gauge, reflect)
                        right = apply_root(transformed_state, transformed_root)
                        if left != right or mobility(state, root) != mobility(transformed_state, transformed_root):
                            passed = False
                            break
                if not passed:
                    break
            if not passed:
                break
        check(f"symmetry-equivariance-gauge-{gauge_index}", passed)

    def f_1(state: State) -> Fraction:
        j, ell, n, u = state
        return Fraction(sum((i + 1) * value for i, value in enumerate(j + ell + n + u)))

    def f_2(state: State) -> Fraction:
        j, ell, n, u = state
        return Fraction(sum(j) ** 2 + 3 * sum(ell) + 5 * sum(n) + 7 * sum(u))

    projected_1 = {state: average_function(f_1, state, gauges) for state in all_states}
    projected_2 = {state: average_function(f_2, state, gauges) for state in all_states}
    p_1 = lambda state: projected_1[state]
    p_2 = lambda state: projected_2[state]

    check(
        "projection-idempotent-f1",
        all(average_function(p_1, state, gauges) == p_1(state) for state in all_states),
    )
    check(
        "projection-idempotent-f2",
        all(average_function(p_2, state, gauges) == p_2(state) for state in all_states),
    )
    left_pair = formal_gibbs_pair(p_1, f_2, all_states)
    right_pair = formal_gibbs_pair(f_1, p_2, all_states)
    check("projection-self-adjoint-formal-gibbs", left_pair == right_pair)

    commutation_passed = True
    commutation_states = 0
    for state in all_states:
        l_p = formal_generator(state, p_1, all_roots)
        p_l = average_formal(f_1, state, gauges, all_roots)
        commutation_states += 1
        if l_p != p_l:
            commutation_passed = False
            break
    check("projection-generator-formal-commutation", commutation_passed, commutation_states)

    for index, (left, right) in enumerate(((f_1, f_1), (f_1, f_2), (f_2, f_2)), start=1):
        b_pair, minus_l_pair = formal_dirichlet_pair(
            left, right, all_states, all_roots
        )
        check(f"directed-root-dirichlet-pair-{index}", b_pair == minus_l_pair)

    incidence_count = sum(
        admissible(state, root) for state in all_states for root in all_roots
    )
    check("incidence-count-even", incidence_count % 2 == 0, incidence_count)
    check("incidence-count", incidence_count == inverse_cases, incidence_count)

    obstruction_cases = 0
    for kappa_s in (Fraction(1, 3), Fraction(1), Fraction(7, 2)):
        for s in (Fraction(1, 4), Fraction(1, 2)):
            for delta in (Fraction(1, 5), Fraction(1, 2)):
                for z_1, z_2 in ((Fraction(0), Fraction(1)), (Fraction(1, 3), Fraction(5, 6))):
                    direct, factored = refinement_obstruction(kappa_s, s, delta, z_1, z_2)
                    obstruction_cases += 1
                    check(
                        f"refinement-obstruction-{obstruction_cases}",
                        direct == factored and direct != 0,
                        [str(direct), str(factored)],
                    )

    statuses = {item["id"]: item["status"] for item in audit["conditions"]}
    expected_statuses = {
        "PAH-OMC-C1": "PASSED",
        "PAH-OMC-C2": "PASSED",
        "PAH-OMC-C3": "PASSED",
        "PAH-OMC-C4": "PASSED",
        "PAH-OMC-C5": "PASSED_BOUNDARY",
    }
    check("condition-statuses", statuses == expected_statuses, statuses)
    check(
        "refinement-not-global-no-go",
        audit["refinement_failure_boundary"]["non_global"] is True,
    )
    check(
        "no-physical-prea",
        any("No physical Pre-A" in item for item in audit["non_claims"]),
    )
    check(
        "single-next-question",
        "nontrivial anchor-preserving subdivision" in audit["single_next_question"]
        and "parameter transport" in audit["single_next_question"],
    )

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
        "schema": "tect/pah-omc001-primary-run/1.0",
        "run_kind": "primary",
        "audit_id": audit["audit_id"],
        "result_id": audit["result_id"],
        "exploration_id": audit["exploration_id"],
        "task_id": audit["task_id"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verification": "PASS" if not failed else "FAIL",
        "finite_common_dynamics_verdict": audit["finite_common_dynamics_verdict"],
        "uniform_refinement_verdict": audit["uniform_refinement_verdict"],
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "fixture_counts": {
            "states": len(all_states),
            "root_labels": len(all_roots),
            "admissible_incidences": incidence_count,
            "inverse_cases": inverse_cases,
            "equivariance_cases": equivariance_cases,
            "symmetry_elements": 2 * len(gauges),
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
        "PAH-OMC-AUDIT-001 PRIMARY "
        f"{result['verification']} {result['passed']}/{result['assertion_count']}; "
        f"finite={result['finite_common_dynamics_verdict']}; "
        f"refinement={result['uniform_refinement_verdict']}; "
        f"core={result['core_digest']}"
    )
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
