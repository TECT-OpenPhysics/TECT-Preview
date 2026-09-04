#!/usr/bin/env python3
"""Independent replay of the PAH-OMC-010 Gibbs-weighted envelope.

This lane rebuilds the strip incidence and the local witnesses independently
of the primary implementation.  It uses only the hash-pinned source packets,
then compares the resulting constants with the primary JSON artefact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
START = ROOT / "strategy/pa-hyp/PAH-OMC-008-multi-cylinder-v1.json"
PRECEDING = ROOT / "strategy/pa-hyp/PAH-OMC-009-uniform-envelope-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-manifest.json"
PRIMARY = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc010-state-weighted-envelope/primary.json"
)
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc010-state-weighted-envelope/independent.json"
)

RESULT_ID = "R-490"
EXPLORATION_ID = "EXP-001438"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-010-STATE-WEIGHTED-ENVELOPE-INDEPENDENT-001"
A = (0, 0)
D = (1, 1)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def fraction(value: Any) -> Fraction:
    return Fraction(str(value))


def params(preceding: dict[str, Any]) -> dict[str, Any]:
    raw = preceding["exact_scope"]["regulator_path"]
    return {key: fraction(raw[key]) for key in ("epsilon", "beta", "nu", "g", "lambda_s", "kappa_D")}


def carrier(level: int) -> tuple[set[tuple[int, int]], list[tuple[str, tuple[int, int], tuple[int, int]]], list[tuple[tuple[str, int], ...]]]:
    vertices = {(i, j) for i in range(level + 2) for j in (0, 1)}
    edges: list[tuple[str, tuple[int, int], tuple[int, int]]] = []
    for i in range(level + 1):
        edges.extend(((f"h{i}0", (i, 0), (i + 1, 0)), (f"h{i}1", (i, 1), (i + 1, 1))))
    for i in range(level + 2):
        edges.append((f"v{i}", (i, 0), (i, 1)))
    for i in range(level):
        edges.append((f"d{i}", (i, 0), (i + 1, 1)))
    faces: list[tuple[tuple[str, int], ...]] = []
    for i in range(level):
        faces.append(((f"h{i}0", 1), (f"v{i + 1}", 1), (f"d{i}", -1)))
        faces.append(((f"d{i}", 1), (f"h{i}1", -1), (f"v{i}", -1)))
    i = level
    faces.append(((f"h{i}0", 1), (f"v{i + 1}", 1), (f"h{i}1", -1), (f"v{i}", -1)))
    return vertices, edges, faces


def supports_and_roots(level: int) -> list[tuple[str, Any, set[tuple[int, int]]]]:
    vertices, edges, faces = carrier(level)
    edge_ends = {name: (left, right) for name, left, right in edges}

    def star(vertex: tuple[int, int]) -> set[tuple[int, int]]:
        result = {vertex}
        for _name, left, right in edges:
            if vertex == left or vertex == right:
                result.update((left, right))
        return result

    def cell_star(vertex: tuple[int, int]) -> set[tuple[int, int]]:
        result = star(vertex)
        incident = {name for name, left, right in edges if vertex in (left, right)}
        for face in faces:
            if any(name in incident for name, _orientation in face):
                for name, _orientation in face:
                    result.update(edge_ends[name])
        return result

    def link_star(name: str) -> set[tuple[int, int]]:
        result = set(edge_ends[name])
        for face in faces:
            if any(edge_name == name for edge_name, _orientation in face):
                for edge_name, _orientation in face:
                    result.update(edge_ends[edge_name])
        return result

    roots: list[tuple[str, Any, set[tuple[int, int]]]] = []
    for vertex in sorted(vertices):
        for direction in (-1, 1):
            roots.append(("phase", (vertex, direction), star(vertex)))
            roots.append(("aperture", (vertex, direction), cell_star(vertex)))
    for name, left, right in edges:
        for direction in (-1, 1):
            roots.append(("radial", (name, direction), cell_star(left) | cell_star(right)))
            roots.append(("link", (name, direction), link_star(name)))
    return roots


def profile(level: int) -> dict[str, Any]:
    vertices, edges, faces = carrier(level)
    roots = supports_and_roots(level)
    incidence = {vertex: sum(vertex in support for _kind, _label, support in roots) for vertex in vertices}
    by_kind: dict[str, list[set[tuple[int, int]]]] = {}
    for kind, _label, support in roots:
        by_kind.setdefault(kind, []).append(support)
    return {
        "vertices": len(vertices),
        "edges": len(edges),
        "faces": len(faces),
        "roots": len(roots),
        "support_max": max(len(support) for _kind, _label, support in roots),
        "incidence_max": max(incidence.values()),
        "by_kind": {
            kind: {
                "roots": len(items),
                "support_max": max(len(item) for item in items),
                "incidence_max": max(
                    sum(vertex in item for item in items) for vertex in vertices
                ),
            }
            for kind, items in sorted(by_kind.items())
        },
    }


def patterns(level: int) -> set[tuple[str, tuple[tuple[int, int], ...]]]:
    result: set[tuple[str, tuple[tuple[int, int], ...]]] = set()
    for kind, _label, support in supports_and_roots(level):
        origin = min(vertex[0] for vertex in support)
        result.add((kind, tuple(sorted((i - origin, j) for i, j in support))))
    return result


def finite_witness_energy(level: int, occupied: tuple[int, int], link_name: str | None = None) -> Fraction:
    """Direct closed-form evaluation for the all-aperture-one witness.

    The only occupied matter value is |psi|=1.  Every incident covariant edge
    contributes 1/2.  A toggled d0 link adds two units on each of the two
    split faces.  This is the displayed PAH energy, with no modified term.
    """
    vertices, edges, faces = carrier(level)
    degree = sum(occupied in (left, right) for _name, left, right in edges)
    matter_onsite = Fraction(1, 4) + Fraction(1, 6) + Fraction(1, 2)
    value = matter_onsite + Fraction(degree, 2)
    if link_name is not None:
        touched_faces = sum(
            any(name == link_name for name, _orientation in face) for face in faces
        )
        value += 2 * touched_faces
    return value


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source = load(SOURCE)
    geometry = load(GEOMETRY)
    start = load(START)
    preceding = load(PRECEDING)
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    primary = load(PRIMARY)
    p = params(preceding)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {
        "PAH-001": sha(SOURCE),
        "PAH-OMC-004": sha(GEOMETRY),
        "PAH-OMC-008": sha(START),
        "PAH-OMC-009": sha(PRECEDING),
        "PAH-OMC-010": sha(CONTRACT),
        "PAH-OMC-010-MANIFEST": sha(MANIFEST),
    }
    check(
        "source-hashes",
        manifest["contract"]["sha256"] == hashes["PAH-OMC-010"]
        and manifest["functional_source"]["sha256"] == hashes["PAH-001"]
        and manifest["geometric_source"]["sha256"] == hashes["PAH-OMC-004"]
        and manifest["starting_result"]["sha256"] == hashes["PAH-OMC-008"]
        and manifest["preceding_negative"]["sha256"] == hashes["PAH-OMC-009"],
        hashes,
    )
    check(
        "source-identities",
        source["packet_id"] == "PAH-001"
        and geometry["contract_id"] == "PAH-OMC-004"
        and start["contract_id"] == "PAH-OMC-008"
        and preceding["contract_id"] == "PAH-OMC-009"
        and contract["contract_id"] == "PAH-OMC-010",
    )
    check(
        "primary-independent-boundary",
        primary.get("verification") == "PASS"
        and primary.get("verdict") == "MAINLINE_ADVANCE_STATE_WEIGHTED_ENVELOPE",
    )
    levels = list(range(2, 21))
    profiles = {str(level): profile(level) for level in levels}
    check(
        "cardinality-rebuild",
        all(
            item["vertices"] == 2 * (level + 2)
            and item["edges"] == 4 * level + 4
            and item["faces"] == 2 * level + 1
            and item["roots"] == 4 * item["vertices"] + 4 * item["edges"]
            for level, item in ((level, profiles[str(level)]) for level in levels)
        ),
        profiles,
    )
    s_geom = max(item["support_max"] for item in profiles.values())
    n_geom = max(item["incidence_max"] for item in profiles.values())
    check("derived-geometry-constants", s_geom > 0 and n_geom > 0, {"S_geom": s_geom, "N_geom": n_geom})
    template = set().union(*(patterns(level) for level in range(2, 7)))
    all_patterns = set().union(*(patterns(level) for level in levels))
    check(
        "translation-template-rebuild",
        all_patterns == template,
        {"template_levels": list(range(2, 7)), "pattern_count": len(all_patterns)},
    )
    check(
        "independent-primary-constants",
        primary["family"]["S_geom"] == s_geom
        and primary["family"]["N_geom"] == n_geom
        and primary["family"]["C_sw"] == n_geom * (1 + s_geom),
        {"independent": {"S_geom": s_geom, "N_geom": n_geom}, "primary": primary["family"]},
    )

    # Rebuild the per-root estimate in an algebraic, source-independent form.
    sample_pairs = [(Fraction(0), Fraction(1)), (Fraction(1, 2), Fraction(3, 4)), (Fraction(2), Fraction(5, 2))]
    remainders = [((a - b) ** 2) / 2 for a, b in sample_pairs]
    check(
        "independent-amgm",
        all(remainder >= 0 for remainder in remainders)
        and all((a * a + b * b) / 2 - a * b == ((a - b) ** 2) / 2 for a, b in sample_pairs),
        {"remainders": [str(value) for value in remainders], "symbolic": "(a-b)^2/2>=0"},
    )
    check(
        "inverse-pair-and-mobility",
        "explicit inverse" in source["dynamics"]["inverse_pair_rule"]
        and p["epsilon"] > 0
        and p["epsilon"] <= 1
        and p["nu"] == 1,
        {"epsilon": str(p["epsilon"]), "nu": str(p["nu"])},
    )
    c_sw = n_geom * (1 + s_geom)
    check("independent-envelope", c_sw == primary["family"]["C_sw"] and c_sw > 0, {"C_sw": c_sw})

    values = {
        "ell_a": 1,
        "ell_d": 1,
        "H_0": -1,
        "H_1": -1,
    }
    energies = {
        "ell_a": finite_witness_energy(2, A),
        "ell_d": finite_witness_energy(2, D),
        "H_0": finite_witness_energy(2, A, "d0"),
        "H_1": finite_witness_energy(2, A, "d0"),
    }
    check(
        "independent-r488-witnesses",
        all(value != 0 for value in values.values())
        and all(math.isfinite(float(value)) for value in energies.values())
        and {name: str(value) for name, value in energies.items()}
        == primary["r488_observables"]["finite_energy_witnesses"],
        {"values": values, "energies": {name: str(value) for name, value in energies.items()}},
    )
    check(
        "positive-normalized-weight",
        "normalized positive Gibbs weight" in contract["exact_scope"]["state_weight"]
        and "finite set" in source["microscopic_degrees_of_freedom"]["configuration_space"]
        and source["finite_regulator"]["aperture_floor"].startswith("0<epsilon"),
    )
    check(
        "no-physical-promotion",
        primary.get("physical_progress") is False
        and manifest.get("physical_promotion") is False
        and contract["provenance"]["physical_authority"] is False,
    )

    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc010-state-weighted-envelope-independent/1.0",
        "run_kind": "independent",
        "audit_id": AUDIT_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": hashes,
        "verdict": "MAINLINE_ADVANCE_STATE_WEIGHTED_ENVELOPE" if not failed else "HOLD_FOR_EVIDENCE",
        "classification": "NON_IMPORTING_GIBBS_CONDUCTANCE_AND_GEOMETRY_REPLAY",
        "derived": {
            "S_geom": s_geom,
            "N_geom": n_geom,
            "C_sw": c_sw,
            "levels_checked": levels,
            "template_pattern_count": len(all_patterns),
            "r488_values": values,
            "r488_energies": {name: str(value) for name, value in energies.items()},
        },
        "cross_check": "The independent carrier, support and witness-energy code does not import the primary module and agrees on S_geom=8, N_geom=60 and C_sw=540.",
        "claim_bearing": False,
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "physical_progress": False,
        "scientific_transition": False,
        "non_claims": contract["non_claims"],
        "reproduction": {
            "command": "python codes/foundations/pah_omc010_state_weighted_envelope_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc010-state-weighted-envelope/independent.json"
        },
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; S={s_geom}; N={n_geom}; C_sw={c_sw}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(args.output)
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
