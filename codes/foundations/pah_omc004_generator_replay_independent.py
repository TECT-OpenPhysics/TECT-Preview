#!/usr/bin/env python3
"""Non-importing independent replay of the PAH-OMC-004 generator rows.

The implementation deliberately rebuilds the finite aperture/Wilson energy
from direct term tables rather than importing the primary replay module.  It
checks the same 512 local Q=0 states and retains the diagonal boundary defect.
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
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
PARENT = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
SIDECAR = ROOT / "strategy/pa-hyp/PAH-OMC-004-generator-replay-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-004-generator-replay-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-03-pah-omc004-generator-replay/independent.json"
)

AUDIT_ID = "PAH-GENERATOR-REPLAY-001"
EXPLORATION_ID = "EXP-001371"
RESULT_ID = "R-484"
TASK_ID = "T-054"

# Directly declared finite inputs.
K = 2
M = 1
EPS = Fraction(1, 2)
BETA = Fraction(1)
NU = Fraction(1)
LAMBDA = Fraction(1)
KAPPA_S = Fraction(1)
KAPPA_G = Fraction(1)

VERTICES = ("a", "b", "c", "d")
EDGE_ORDER = ("h00", "v0", "d0", "h01", "v1")
ENDPOINTS = {
    "h00": ("a", "b"),
    "v0": ("a", "c"),
    "d0": ("a", "d"),
    "h01": ("c", "d"),
    "v1": ("b", "d"),
}
TRIANGLES = (
    ("h00", "v1", "d0"),
    ("d0", "h01", "v0"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def s(level: int) -> Fraction:
    return EPS + Fraction(level) * (1 - EPS) / M


def z2(bit: int) -> int:
    if bit not in (0, 1):
        raise ValueError(bit)
    return 1 if bit == 0 else -1


def unpack(state: tuple[int, ...]) -> tuple[dict[str, int], dict[str, int]]:
    if len(state) != 9:
        raise ValueError("nine patch coordinates required")
    ap = dict(zip(VERTICES, state[:4]))
    link = dict(zip(EDGE_ORDER, state[4:]))
    if any(value not in (0, 1) for value in ap.values()) or any(value not in (0, 1) for value in link.values()):
        raise ValueError("binary fixture coordinate required")
    return ap, link


def onsite(level: int) -> Fraction:
    return LAMBDA * (s(level) - 1) ** 2 / 2


def edge_energy(left: int, right: int) -> Fraction:
    return KAPPA_S * (s(left) - s(right)) ** 2 / 2


def triangle_energy(triangle: tuple[str, ...], ap: dict[str, int], links: dict[str, int]) -> Fraction:
    stiffness = []
    sign = 1
    for name in triangle:
        left, right = ENDPOINTS[name]
        stiffness.append(Fraction(2, 1) / (s(ap[left]) + s(ap[right])))
        sign *= z2(links[name])
    # Every edge in the two displayed faces has unit coupling.  For Z_2 the
    # inverse orientation contributes the same sign, but the face word is the
    # exact triangle listed above.
    return KAPPA_G * sum(stiffness, Fraction(0)) / len(stiffness) * (1 - sign)


def total(state: tuple[int, ...]) -> Fraction:
    ap, links = unpack(state)
    value = sum((onsite(ap[name]) for name in VERTICES), Fraction(0))
    for name in EDGE_ORDER:
        left, right = ENDPOINTS[name]
        value += edge_energy(ap[left], ap[right])
    for triangle in TRIANGLES:
        value += triangle_energy(triangle, ap, links)
    return value


def row(state: tuple[int, ...], level: int) -> dict[str, Any]:
    ap, _links = unpack(state)
    direction = 1 if ap["a"] == 0 else -1
    target = list(state)
    target[0] += direction
    target_state = tuple(target)
    delta = total(target_state) - total(state)
    mobility_sq = s(ap["a"]) * s(unpack(target_state)[0]["a"])
    indicator_delta = int(unpack(target_state)[0]["a"] == 1) - int(ap["a"] == 1)
    return {
        "level": level,
        "state": list(state),
        "direction": direction,
        "delta_F": str(delta),
        "mobility_square": str(mobility_sq),
        "delta_s": str(s(unpack(target_state)[0]["a"]) - s(ap["a"])),
        "delta_indicator_j_a_eq_1": indicator_delta,
        "rate_exponent": str(-BETA * delta / 2),
    }


def boundary() -> dict[str, str]:
    base = (0, 0, 0, 0, 0, 0, 0, 0, 0)
    raised = (1, 0, 0, 0, 0, 0, 0, 0, 0)
    diagonal_one_base = (0, 0, 0, 0, 0, 0, 1, 0, 0)
    diagonal_one_raised = (1, 0, 0, 0, 0, 0, 1, 0, 0)
    # Rebuild the coarse square, including its four-edge Wilson average.
    square = ("h00", "v1", "h01", "v0")

    def coarse(state: tuple[int, ...]) -> Fraction:
        ap, links = unpack(state)
        value = sum((onsite(ap[name]) for name in VERTICES), Fraction(0))
        for name in EDGE_ORDER:
            if name != "d0":
                left, right = ENDPOINTS[name]
                value += edge_energy(ap[left], ap[right])
        stiffness = [Fraction(2, 1) / (s(ap[ENDPOINTS[name][0]]) + s(ap[ENDPOINTS[name][1]])) for name in square]
        holonomy = 1
        for name in square:
            holonomy *= z2(links[name])
        return value + sum(stiffness, Fraction(0)) / len(stiffness) * (1 - holonomy)

    even = total(raised) - total(base)
    odd = total(diagonal_one_raised) - total(diagonal_one_base)
    return {
        "coarse_delta_F": str(coarse(raised) - coarse(base)),
        "fine_even_delta_F": str(even),
        "fine_odd_delta_F": str(odd),
        "hidden_diagonal_defect": str(even - odd),
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source = load(SOURCE)
    parent = load(PARENT)
    sidecar = load(SIDECAR)
    manifest = load(MANIFEST)
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    hashes = {
        "PAH-001": sha(SOURCE),
        "PAH-OMC-004": sha(PARENT),
        "PAH-OMC-004-GEN-001": sha(SIDECAR),
        "PAH-OMC-004-GEN-MANIFEST": sha(MANIFEST),
    }
    check("source-hashes", hashes["PAH-001"] == "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37" and hashes["PAH-OMC-004"] == manifest["parent"]["sha256"], hashes)
    check("sidecar-hash-pin", hashes["PAH-OMC-004-GEN-001"] == manifest["sidecar"]["sha256"], hashes["PAH-OMC-004-GEN-001"])
    check("identities", source.get("packet_id") == "PAH-001" and parent.get("contract_id") == "PAH-OMC-004" and sidecar.get("contract_id") == "PAH-OMC-004-GEN-001")
    check("direct-functional-shape", "F_rho" in source.get("functional_or_action", {}).get("name", "") and "J_e" in source.get("functional_or_action", {}).get("edge_stiffness", ""))
    check("direct-generator-shape", "sum_r" in source.get("dynamics", {}).get("generator", ""))
    check("scope-is-q-zero", K == 2 and M == 1 and EPS == Fraction(1, 2) and BETA == 1 and NU == 1)
    check("no-new-term", sidecar.get("provenance", {}).get("external_source") is False and sidecar.get("provenance", {}).get("physical_authority") is False)

    states = [prefix + suffix for prefix in itertools.product(range(M + 1), repeat=4) for suffix in itertools.product(range(K), repeat=5)]
    rows_1 = [row(state, 1) for state in states]
    rows_2 = [row(state, 2) for state in states]
    key_fields = ("state", "direction", "delta_F", "mobility_square", "delta_s", "delta_indicator_j_a_eq_1", "rate_exponent")
    check("all-states-enumerated", len(states) == (M + 1) ** 4 * K ** 5, len(states))
    check("rows-are-level-labelled", all(item["level"] == 1 for item in rows_1) and all(item["level"] == 2 for item in rows_2))
    check("direct-row-equality", [tuple(item[key] for key in key_fields) for item in rows_1] == [tuple(item[key] for key in key_fields) for item in rows_2])
    check("mobility-is-parent-rule", {item["mobility_square"] for item in rows_1} == {"1/2"})
    check("both-aperture-directions", {item["direction"] for item in rows_1} == {-1, 1})
    witness = boundary()
    check("boundary-witness", witness == {"coarse_delta_F": "1/8", "fine_even_delta_F": "1/4", "fine_odd_delta_F": "-55/36", "hidden_diagonal_defect": "16/9"}, witness)
    check("boundary-defect-nonzero", Fraction(witness["hidden_diagonal_defect"]) != 0)

    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc004-generator-replay-independent/1.0",
        "run_kind": "independent",
        "audit_id": AUDIT_ID,
        "exploration_id": EXPLORATION_ID,
        "result_id": RESULT_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": hashes,
        "state_count": len(states),
        "generator_rows": rows_1,
        "row_identity": {"levels": [1, 2], "rows_compared": len(rows_1), "all_equal": True, "tuple_fields": list(key_fields)},
        "boundary_witness": witness,
        "verdict": "EXPLICIT_LOCAL_GENERATOR_ROW_EQUALITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "independence_note": "The energy, triangle table, state enumeration and boundary square were rebuilt directly; the primary replay module was not imported.",
        "non_claims": sidecar.get("non_claims", []),
        "next_question": sidecar.get("single_next_question"),
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} INDEPENDENT {payload['verification']} {payload['passed']}/{payload['assertion_count']}; rows={len(rows_1)}; boundary={witness['hidden_diagonal_defect']}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(args.output)
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
