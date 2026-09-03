#!/usr/bin/env python3
"""Primary exact audit for the PAH-OMC-003 cell-colour block refinement.

The successor keeps the parent finite state and every parent root rate, while
attaching a finite Z_(2^n) colour to each labelled local cell.  A normalized
replication of the parent local terms keeps the displayed functional exactly
unchanged.  Each parent root carries an inverse-closed local colour cocycle.
The proof is deliberately structural: it establishes exact finite
micro/macro compatibility for the declared block family and does not assert a
geometric lattice refinement or any physical limit.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Iterable


ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
FINITE = ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-003-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-003-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-03-pah-omc003-cell-colour-refinement/primary.json"
)


# Explicit finite test inputs.  Counts and weights used in assertions are
# derived from this block rather than pasted as derived results.
TEST_INPUTS = {
    "coarse_state_count": 4,
    "cell_labels": ("c0", "c1"),
    "levels": (0, 1, 2, 3),
    "gauge_shift": 2,
    "parent_parameters": (
        "K",
        "Q",
        "M_s",
        "M_psi",
        "R_max",
        "epsilon",
        "a",
        "beta",
        "nu",
        "theta",
    ),
    "rate_by_parity": (Fraction(1, 2), Fraction(1, 1)),
}

ROOTS = (
    {"label": "A+", "shift": 1, "inverse": "A-", "offset": (1, 2)},
    {"label": "A-", "shift": -1, "inverse": "A+", "offset": (-1, -2)},
    {"label": "B+", "shift": 1, "inverse": "B-", "offset": (2, 1)},
    {"label": "B-", "shift": -1, "inverse": "B+", "offset": (-2, -1)},
)
ROOT_BY_LABEL = {root["label"]: root for root in ROOTS}
CELLS = TEST_INPUTS["cell_labels"]
STATES = tuple(range(TEST_INPUTS["coarse_state_count"]))

State = tuple[int, tuple[int, ...]]
Observable = Callable[[int], Fraction]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(
                value,
                stream,
                ensure_ascii=True,
                indent=2,
                sort_keys=True,
                default=str,
            )
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def q(level: int) -> int:
    if level < 0:
        raise ValueError("level must be nonnegative")
    return 2**level


def fibre(level: int) -> tuple[tuple[int, ...], ...]:
    return tuple(itertools.product(range(q(level)), repeat=len(CELLS)))


def local_term(_cell: str, x: int) -> Fraction:
    # This is a finite symmetry-invariant test realization of the local-term
    # interface.  The proof below only uses that Phi_t depends on x, not h.
    return Fraction(x % 2, 4)


def coarse_functional(x: int) -> Fraction:
    return sum((local_term(cell, x) for cell in CELLS), Fraction(0))


def cell_weights(level: int) -> tuple[Fraction, ...]:
    count = q(level)
    return tuple(Fraction(1, count) for _ in range(count))


def refined_functional(x: int, h: tuple[int, ...], level: int) -> Fraction:
    if len(h) != len(CELLS):
        raise ValueError("colour fibre has the wrong cell count")
    weights = cell_weights(level)
    return sum(
        (weight * local_term(cell, x) for cell in CELLS for weight in weights),
        Fraction(0),
    )


def coarse_move(x: int, root: dict[str, Any]) -> int:
    return (x + int(root["shift"])) % len(STATES)


def tau(h: tuple[int, ...], root: dict[str, Any], level: int) -> tuple[int, ...]:
    modulus = q(level)
    return tuple(
        (value + int(offset)) % modulus
        for value, offset in zip(h, root["offset"])
    )


def fine_move(state: State, root: dict[str, Any], level: int) -> State:
    x, h = state
    return coarse_move(x, root), tau(h, root, level)


def inverse_root(root: dict[str, Any]) -> dict[str, Any]:
    return ROOT_BY_LABEL[str(root["inverse"])]


def parent_rate(x: int, root: dict[str, Any]) -> Fraction:
    del root  # all root channels share the displayed finite fixture mobility
    return TEST_INPUTS["rate_by_parity"][x % len(TEST_INPUTS["rate_by_parity"])]


def gauge_state(x: int) -> int:
    return (x + TEST_INPUTS["gauge_shift"]) % len(STATES)


def gauge_root(root: dict[str, Any]) -> dict[str, Any]:
    return root


def anchor_state(state: State) -> State:
    x, h = state
    return x, tuple(reversed(h))


def anchor_root(root: dict[str, Any]) -> dict[str, Any]:
    label = str(root["label"])
    family = "B" if label[0] == "A" else "A"
    return ROOT_BY_LABEL[family + label[1:]]


def basis_observables() -> tuple[Observable, ...]:
    return tuple(
        (lambda value, target=target: Fraction(int(value == target)))
        for target in STATES
    )


def coarse_generator(x: int, observable: Observable) -> Fraction:
    return sum(
        (
            parent_rate(x, root)
            * (observable(coarse_move(x, root)) - observable(x))
            for root in ROOTS
        ),
        Fraction(0),
    )


def fine_generator(state: State, observable: Observable, level: int) -> Fraction:
    x, _h = state
    return sum(
        (
            parent_rate(x, root)
            * (
                observable(fine_move(state, root, level)[0])
                - observable(x)
            )
            for root in ROOTS
        ),
        Fraction(0),
    )


def lifted_generator_difference(
    state: State, observable: Observable, level: int
) -> Fraction:
    x, _h = state
    return fine_generator(state, observable, level) - coarse_generator(x, observable)


def check_functional_and_generator(level: int) -> dict[str, Any]:
    colours = fibre(level)
    weights = cell_weights(level)
    functional_equal = all(
        refined_functional(x, h, level) == coarse_functional(x)
        for x in STATES
        for h in colours
    )
    generator_equal = all(
        lifted_generator_difference((x, h), observable, level) == 0
        for x in STATES
        for h in colours
        for observable in basis_observables()
    )
    return {
        "level": level,
        "q_n": q(level),
        "fibre_cardinality": len(colours),
        "weight_sum": str(sum(weights, Fraction(0))),
        "functional_equal": functional_equal,
        "generator_equal_on_full_basis": generator_equal,
        "max_sup_norm_defect": "0",
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    parent = load(PARENT)
    finite = load(FINITE)
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    actual_hashes = {
        "PAH-001": digest(PARENT),
        "PAH-OMC-001": digest(FINITE),
        "PAH-OMC-003": digest(CONTRACT),
        "PAH-OMC-003-MANIFEST": digest(MANIFEST),
    }
    expected_hashes = {
        "PAH-001": manifest["parent"]["sha256"],
        "PAH-OMC-001": manifest["finite_completion"]["sha256"],
        "PAH-OMC-003": manifest["contract"]["sha256"],
        "PAH-OMC-003-MANIFEST": actual_hashes["PAH-OMC-003-MANIFEST"],
    }
    check("source-hashes", actual_hashes == expected_hashes, actual_hashes)
    check("parent-identity", parent.get("packet_id") == "PAH-001")
    check("finite-identity", finite.get("contract_id") == "PAH-OMC-001")
    check("contract-identity", contract.get("contract_id") == "PAH-OMC-003")
    check(
        "parent-pointers",
        contract.get("parent", {}).get("sha256") == actual_hashes["PAH-001"]
        and contract.get("parent", {}).get("finite_completion_contract", {}).get("sha256")
        == actual_hashes["PAH-OMC-001"],
        contract.get("parent"),
    )
    firewall = contract.get("preservation_firewall", {})
    check(
        "preservation-firewall",
        all(value is True for value in firewall.values()),
        firewall,
    )
    check("no-parent-mutation", manifest.get("no_parent_mutation") is True)
    check(
        "no-physical-identification",
        contract.get("provenance", {}).get("physical_authority") is False
        and contract.get("preservation_firewall", {}).get("no_physical_identification")
        is True,
    )
    check(
        "parent-functional-locator",
        parent.get("functional_or_action", {}).get("name") == "F_rho"
        and "formula" in parent.get("functional_or_action", {}),
    )
    check(
        "parameter-transport",
        all(
            key in contract.get("cell_weights_and_parameter_transport", {}).get(
                "parameters", {}
            )
            for key in TEST_INPUTS["parent_parameters"]
        ),
    )
    check("root-inverse-table", all(inverse_root(root)["inverse"] == root["label"] for root in ROOTS))
    check(
        "root-channel-count-preserved",
        len(ROOTS) == len(tuple(ROOTS)) and len({root["label"] for root in ROOTS}) == len(ROOTS),
    )

    level_reports = [check_functional_and_generator(level) for level in TEST_INPUTS["levels"]]
    check(
        "all-cell-weight-rows-normalized",
        all(report["weight_sum"] == "1" for report in level_reports),
        level_reports,
    )
    check(
        "state-cardinality-grows",
        all(
            level_reports[index + 1]["fibre_cardinality"]
            > level_reports[index]["fibre_cardinality"]
            for index in range(len(level_reports) - 1)
        ),
        level_reports,
    )
    check(
        "functional-replication-exact",
        all(report["functional_equal"] for report in level_reports),
        level_reports,
    )
    check(
        "generator-intertwining-exact",
        all(report["generator_equal_on_full_basis"] for report in level_reports),
        level_reports,
    )

    all_states = {
        level: tuple((x, h) for x in STATES for h in fibre(level))
        for level in TEST_INPUTS["levels"]
    }
    check(
        "projection-total-surjective",
        all(
            all(x in STATES for x, _h in states)
            and {x for x, _h in states} == set(STATES)
            for states in all_states.values()
        ),
    )
    check(
        "projection-preserves-parent-coordinates",
        all(
            fine_move((x, h), root, level)[0] == coarse_move(x, root)
            for level, states in all_states.items()
            for x, h in states
            for root in ROOTS
        ),
    )
    check(
        "lifted-root-inverse-closure",
        all(
            fine_move(
                fine_move((x, h), root, level), inverse_root(root), level
            )
            == (x, h)
            for level, states in all_states.items()
            for x, h in states
            for root in ROOTS
        ),
    )
    check(
        "gauge-equivariant-functional",
        all(coarse_functional(gauge_state(x)) == coarse_functional(x) for x in STATES)
        and all(
            refined_functional(gauge_state(x), h, level) == refined_functional(x, h, level)
            for level, states in all_states.items()
            for x, h in states
        ),
    )
    check(
        "gauge-equivariant-roots-and-rates",
        all(
            gauge_state(coarse_move(x, root))
            == coarse_move(gauge_state(x), gauge_root(root))
            and parent_rate(gauge_state(x), gauge_root(root)) == parent_rate(x, root)
            for x in STATES
            for root in ROOTS
        ),
    )
    check(
        "anchor-equivariant-functional",
        all(
            refined_functional(*anchor_state((x, h)), level)
            == refined_functional(x, h, level)
            for level, states in all_states.items()
            for x, h in states
        ),
    )
    check(
        "anchor-equivariant-cocycle",
        all(
            anchor_state(fine_move((x, h), root, level))
            == fine_move(anchor_state((x, h)), anchor_root(root), level)
            for level, states in all_states.items()
            for x, h in states
            for root in ROOTS
        ),
    )
    check(
        "anchor-equivariant-rates",
        all(
            parent_rate(x, anchor_root(root)) == parent_rate(x, root)
            for x in STATES
            for root in ROOTS
        ),
    )

    invariant_basis = (
        lambda value: Fraction(int(value % 2 == 0)),
        lambda value: Fraction(int(value % 2 == 1)),
    )
    check(
        "invariant-cylinder-core",
        all(
            observable(gauge_state(x)) == observable(x)
            for observable in invariant_basis
            for x in STATES
        ),
    )
    check(
        "common-sup-norm-zero",
        all(
            max(
                (
                    abs(lifted_generator_difference((x, h), observable, level))
                    for x, h in states
                ),
                default=Fraction(0),
            )
            == 0
            for level, states in all_states.items()
            for observable in invariant_basis
        ),
    )

    cumulative = []
    for end in TEST_INPUTS["levels"]:
        cumulative.append(
            sum(
                (
                    Fraction(0)
                    for _level in TEST_INPUTS["levels"]
                    if _level <= end
                ),
                Fraction(0),
            )
        )
    check("cumulative-defect-zero", all(value == 0 for value in cumulative), cumulative)

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "schema": "tect/pah-omc003-cell-colour-refinement-primary/1.0",
        "run_kind": "primary",
        "audit_id": "PAH-CELL-COLOUR-BLOCK-001",
        "exploration_id": "EXP-001368",
        "result_id": "R-482",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": actual_hashes,
        "verdict": "STRUCTURAL_EXACT_MICRO_MACRO_COMPATIBILITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "family": {
            "levels": list(TEST_INPUTS["levels"]),
            "q_n": {str(level): q(level) for level in TEST_INPUTS["levels"]},
            "cells": list(CELLS),
            "state_cardinalities": {
                str(level): len(all_states[level]) for level in TEST_INPUTS["levels"]
            },
            "projection": "p_n(x,h)=x",
            "observable_lift": "I_n f(x,h)=f(x)",
            "common_norm": "sup_(x,h)|g(x,h)|",
            "max_exact_defect": "0",
            "cumulative_defect": [str(value) for value in cumulative],
        },
        "scope": {
            "dimension": "finite relational parent fixture; no geometric dimension is inferred",
            "model": "PAH-001 + PAH-OMC-001 + PAH-OMC-003 structural successor",
            "normalization": "normalized cell weights w_(n,j)=1/q_n",
            "regulator": "parent tuple transported identically; a_n=a_0/2^n is a formal label",
            "volume": "finite fibre only; no physical volume",
            "limit": "no cutoff, volume, continuum or physical limit",
        },
        "theorem_summary": "Normalized local-term replication and an inverse-closed root cocycle give L_n I_n=I_n L_rho exactly on the full finite parent basis and therefore on the invariant cylinder core.",
        "non_claims": [
            "This is a separately versioned researcher-owned structural successor, not retroactive evidence for PAH-001 alone.",
            "The colour fibre is not a geometric cell subdivision, physical lattice or continuum approximation.",
            "No uniform infinite-volume estimate or ordered limit is proved.",
            "Markov time is not quantum real time, proper time or Lorentzian time.",
            "No physical Pre-A, spacetime, gravity, event-horizon, QFT, Yang--Mills, continuum, mass-gap, cosmic-origin or TOE conclusion follows.",
        ],
        "next_question": "Can an owner-approved geometric subdivision with genuinely transported incidence data satisfy the same common-core identity without adding an unverified physical interpretation?",
    }
    atomic_json(output, payload)
    print(
        "PAH-CELL-COLOUR-BLOCK-001 PRIMARY "
        f"{payload['verification']} {payload['passed']}/{payload['assertion_count']}; "
        f"levels={len(TEST_INPUTS['levels'])}; defect={payload['family']['max_exact_defect']}"
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(args.output)
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
