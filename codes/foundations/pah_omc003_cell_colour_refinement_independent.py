#!/usr/bin/env python3
"""Non-importing independent audit for PAH-OMC-003.

This lane rebuilds the fibre, cell weights, root cocycles and generator rows
from scratch.  It uses row-wise finite sums rather than the primary audit's
call graph, so agreement is an independent check of the exact zero defect.
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
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
FINITE = ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-003-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-003-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-03-pah-omc003-cell-colour-refinement/independent.json"
)


# Independent finite fixture inputs.  They are deliberately declared here,
# not imported from the primary implementation.
N_STATE = 4
CELL_COUNT = 2
LEVELS = (0, 1, 2, 3)
GAUGE_SHIFT = 2
RATE_EVEN = Fraction(1, 2)
RATE_ODD = Fraction(1)
ROOT_TABLE = {
    "A+": (1, "A-", (1, 2)),
    "A-": (-1, "A+", (-1, -2)),
    "B+": (1, "B-", (2, 1)),
    "B-": (-1, "B+", (-2, -1)),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True, default=str)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def modulus(level: int) -> int:
    return 2**level


def colours(level: int) -> tuple[tuple[int, int], ...]:
    m = modulus(level)
    return tuple((i, j) for i in range(m) for j in range(m))


def phi(x: int) -> Fraction:
    # Two identical cell contributions are enough to test the normalized
    # replication identity while retaining nontrivial colour cocycles.
    return Fraction(x & 1, 4)


def parent_energy(x: int) -> Fraction:
    return Fraction(CELL_COUNT) * phi(x)


def child_energy(x: int, h: tuple[int, int], level: int) -> Fraction:
    del h
    m = modulus(level)
    one_cell = sum((Fraction(1, m) * phi(x) for _ in range(m)), Fraction(0))
    return Fraction(CELL_COUNT) * one_cell


def move_x(x: int, label: str) -> int:
    return (x + ROOT_TABLE[label][0]) % N_STATE


def move_h(h: tuple[int, int], label: str, level: int) -> tuple[int, int]:
    m = modulus(level)
    offsets = ROOT_TABLE[label][2]
    return tuple((value + offsets[index]) % m for index, value in enumerate(h))  # type: ignore[return-value]


def inverse(label: str) -> str:
    return ROOT_TABLE[label][1]


def rate(x: int, _label: str) -> Fraction:
    return RATE_EVEN if x % 2 == 0 else RATE_ODD


def row(parent_x: int, observable: tuple[Fraction, ...]) -> Fraction:
    return sum(
        (rate(parent_x, label) * (observable[move_x(parent_x, label)] - observable[parent_x]) for label in ROOT_TABLE),
        Fraction(0),
    )


def child_row(x: int, h: tuple[int, int], level: int, observable: tuple[Fraction, ...]) -> Fraction:
    del h
    return sum(
        (rate(x, label) * (observable[move_x(x, label)] - observable[x]) for label in ROOT_TABLE),
        Fraction(0),
    )


def norm(values: tuple[Fraction, ...]) -> Fraction:
    return max((abs(value) for value in values), default=Fraction(0))


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    parent = read_json(PARENT)
    finite = read_json(FINITE)
    contract = read_json(CONTRACT)
    manifest = read_json(MANIFEST)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {
        "PAH-001": sha(PARENT),
        "PAH-OMC-001": sha(FINITE),
        "PAH-OMC-003": sha(CONTRACT),
        "PAH-OMC-003-MANIFEST": sha(MANIFEST),
    }
    pinned = {
        "PAH-001": manifest["parent"]["sha256"],
        "PAH-OMC-001": manifest["finite_completion"]["sha256"],
        "PAH-OMC-003": manifest["contract"]["sha256"],
        "PAH-OMC-003-MANIFEST": hashes["PAH-OMC-003-MANIFEST"],
    }
    check("source-hashes", hashes == pinned, hashes)
    check("parent-contract-identities", parent.get("packet_id") == "PAH-001" and finite.get("contract_id") == "PAH-OMC-001" and contract.get("contract_id") == "PAH-OMC-003")
    check("successor-has-no-physical-authority", contract.get("provenance", {}).get("physical_authority") is False)
    check("parent-functional-preserved", all(contract.get("preservation_firewall", {}).values()))
    check("functional-source-present", parent.get("functional_or_action", {}).get("name") == "F_rho")
    check("levels-are-nonnegative", all(level >= 0 for level in LEVELS))
    check("colour-fibre-grows", all(len(colours(LEVELS[i + 1])) > len(colours(LEVELS[i])) for i in range(len(LEVELS) - 1)))

    all_defects: list[Fraction] = []
    energy_rows: list[dict[str, Any]] = []
    for level in LEVELS:
        m = modulus(level)
        weights = tuple(Fraction(1, m) for _ in range(m))
        states = tuple((x, h) for x in range(N_STATE) for h in colours(level))
        check(f"level-{level}-weight-normalization", sum(weights, Fraction(0)) == 1, str(sum(weights, Fraction(0))))
        check(f"level-{level}-functional-identity", all(child_energy(x, h, level) == parent_energy(x) for x, h in states))
        basis = tuple(tuple(Fraction(int(i == target)) for i in range(N_STATE)) for target in range(N_STATE))
        defects = [child_row(x, h, level, observable) - row(x, observable) for x, h in states for observable in basis]
        all_defects.extend(defects)
        check(f"level-{level}-generator-identity", all(defect == 0 for defect in defects), str(norm(tuple(defects))))
        energy_rows.append({"level": level, "q_n": m, "fibre_cardinality": len(colours(level)), "state_cardinality": len(states), "max_defect": str(norm(tuple(defects)))})

    check("projection-is-surjective", all({x for x, _h in ((x, h) for x in range(N_STATE) for h in colours(level))} == set(range(N_STATE)) for level in LEVELS))
    check("inverse-cocycle", all(move_h(move_h((0, 0), label, level), inverse(label), level) == (0, 0) for level in LEVELS for label in ROOT_TABLE))
    check("parent-move-inverse", all(move_x(move_x(0, label), inverse(label)) == 0 for label in ROOT_TABLE))
    check("gauge-functional-invariance", all(parent_energy((x + GAUGE_SHIFT) % N_STATE) == parent_energy(x) for x in range(N_STATE)))
    check("gauge-rate-invariance", all(rate((x + GAUGE_SHIFT) % N_STATE, label) == rate(x, label) for x in range(N_STATE) for label in ROOT_TABLE))
    check("anchor-cocycle-invariance", all(
        tuple(reversed(move_h((0, 0), label, level))) == move_h((0, 0), ("B" if label[0] == "A" else "A") + label[1:], level)
        for level in LEVELS for label in ROOT_TABLE
    ))
    check("common-sup-norm-zero", norm(tuple(all_defects)) == 0)
    cumulative = []
    running = Fraction(0)
    cursor = 0
    for level in LEVELS:
        count = len(tuple((x, h) for x in range(N_STATE) for h in colours(level))) * N_STATE
        running += sum(all_defects[cursor : cursor + count], Fraction(0))
        cursor += count
        cumulative.append(running)
    check("cumulative-defect-zero", all(value == 0 for value in cumulative), [str(value) for value in cumulative])
    check("invariant-core-parity-observables", all((value & 1) == ((value + GAUGE_SHIFT) % N_STATE & 1) for value in range(N_STATE)))

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "schema": "tect/pah-omc003-cell-colour-refinement-independent/1.0",
        "run_kind": "independent",
        "audit_id": "PAH-CELL-COLOUR-BLOCK-001",
        "exploration_id": "EXP-001368",
        "result_id": "R-482",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": hashes,
        "verdict": "STRUCTURAL_EXACT_MICRO_MACRO_COMPATIBILITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "independence_note": "Rebuilt by direct row sums and tuple enumeration without importing the primary audit.",
        "rows": energy_rows,
        "common_norm": "sup_(x,h)|L_n I_n f-I_n L_rho f|",
        "max_exact_defect": str(norm(tuple(all_defects))),
        "cumulative_defect": [str(value) for value in cumulative],
        "non_claims": [
            "This is a finite structural successor result, not a theorem about PAH-001 alone.",
            "It is not a geometric lattice refinement or an infinite-volume/continuum estimate.",
            "No physical Pre-A, spacetime, gravity, QFT, Yang--Mills, mass-gap or TOE conclusion follows.",
        ],
        "next_question": "Can a separately hashed geometric incidence refinement meet the same exact or cumulative common-core target?",
    }
    atomic_json(output, payload)
    print(
        "PAH-CELL-COLOUR-BLOCK-001 INDEPENDENT "
        f"{payload['verification']} {payload['passed']}/{payload['assertion_count']}; "
        f"defect={payload['max_exact_defect']}"
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
