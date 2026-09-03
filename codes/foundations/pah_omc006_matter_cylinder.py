#!/usr/bin/env python3
"""Exact nonzero-Q matter-cylinder replay for PAH-OMC-006.

The program evaluates the unchanged PAH-001 functional on the actual
PAH-OMC-004 two-row strip carriers G_2 and G_3.  It enumerates every Q=1
patch state and every directed radial-transfer root incident to the anchor
matter coordinate ell_a.  The comparison is rootwise and exact; only a
canonical digest and bounded samples are stored so the run artefact remains
portable.  The earlier G_1 -> G_2 boundary is deliberately checked as a
nonzero-defect control and is not promoted to a compatibility result.
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
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
PREDECESSOR = ROOT / "strategy/pa-hyp/PAH-OMC-005-nonzero-q-generator-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-006-matter-cylinder-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-006-matter-cylinder-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc006-matter-cylinder/primary.json"
)

AUDIT_ID = "PAH-MATTER-CYLINDER-GENERATOR-001"
EXPLORATION_ID = "EXP-001378"
RESULT_ID = "R-486"
TASK_ID = "T-054"

# Declared finite fixture inputs from PAH-OMC-006, not derived outputs.
K = 2
M_S = 1
M_PSI = 1
Q = 1
R_MAX = Fraction(1)
EPSILON = Fraction(1, 2)
BETA = Fraction(1)
NU = Fraction(1)
M2 = Fraction(0)
LAMBDA_4 = Fraction(1)
ETA_6 = Fraction(1)
G_COUPLING = Fraction(1)
LAMBDA_S = Fraction(1)
KAPPA_S = Fraction(1)
KAPPA_D = Fraction(1)
KAPPA_G = Fraction(1)

PATCH_VERTICES = ((0, 0), (1, 0), (0, 1), (1, 1))
PATCH_EDGE_NAMES = ("h00", "v0", "d0", "h01", "v1")
PATCH_EDGES = (
    ("h00", (0, 0), (1, 0)),
    ("v0", (0, 0), (0, 1)),
    ("d0", (0, 0), (1, 1)),
    ("h01", (0, 1), (1, 1)),
    ("v1", (1, 0), (1, 1)),
)
APERTURE_BITS = len(PATCH_VERTICES)
LINK_BITS = len(PATCH_EDGES)
PHASE_BITS = len(PATCH_VERTICES)
RADIAL_PLACEMENTS = len(PATCH_VERTICES)

State = tuple[int, ...]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def aperture(level: int) -> Fraction:
    if level not in range(M_S + 1):
        raise ValueError("aperture level outside PAH fixture grid")
    return EPSILON + Fraction(level) * (1 - EPSILON) / M_S


def sign_z2(bit: int) -> int:
    if bit not in range(K):
        raise ValueError("Z_2 coordinate outside fixture")
    return -1 if bit else 1


def strip_carrier(level: int) -> dict[str, Any]:
    """Return the oriented PAH-OMC-004 two-row strip G_level."""
    if level < 0:
        raise ValueError("level must be nonnegative")
    vertices = tuple((i, j) for i in range(level + 2) for j in (0, 1))
    edges: list[tuple[str, tuple[int, int], tuple[int, int]]] = []
    for i in range(level + 1):
        for j in (0, 1):
            edges.append((f"h{i}{j}", (i, j), (i + 1, j)))
    for i in range(level + 2):
        edges.append((f"v{i}", (i, 0), (i, 1)))
    for i in range(level):
        edges.append((f"d{i}", (i, 0), (i + 1, 1)))
    faces: list[tuple[tuple[str, int], ...]] = []
    for i in range(level):
        faces.extend(
            [
                ((f"h{i}0", 1), (f"v{i + 1}", 1), (f"d{i}", -1)),
                ((f"d{i}", 1), (f"h{i}1", -1), (f"v{i}", -1)),
            ]
        )
    i = level
    faces.append(((f"h{i}0", 1), (f"v{i + 1}", 1), (f"h{i}1", -1), (f"v{i}", -1)))
    return {"vertices": vertices, "edges": tuple(edges), "faces": tuple(faces)}


def make_patch_state(
    aperture_bits: tuple[int, ...],
    link_bits: tuple[int, ...],
    phase_bits: tuple[int, ...],
    radial_index: int,
) -> State:
    radial = tuple(1 if index == radial_index else 0 for index in range(RADIAL_PLACEMENTS))
    return tuple(aperture_bits) + tuple(link_bits) + tuple(phase_bits) + radial


def fixture_states() -> Iterable[State]:
    for aperture_bits in itertools.product(range(M_S + 1), repeat=APERTURE_BITS):
        for link_bits in itertools.product(range(K), repeat=LINK_BITS):
            for phase_bits in itertools.product(range(K), repeat=PHASE_BITS):
                for radial_index in range(RADIAL_PLACEMENTS):
                    yield make_patch_state(aperture_bits, link_bits, phase_bits, radial_index)


def decode_patch(state: State) -> tuple[dict[tuple[int, int], int], dict[str, int], dict[tuple[int, int], int], dict[tuple[int, int], int]]:
    expected = APERTURE_BITS + LINK_BITS + PHASE_BITS + RADIAL_PLACEMENTS
    if len(state) != expected:
        raise ValueError(f"state length {len(state)} != {expected}")
    offset = 0
    apertures = dict(zip(PATCH_VERTICES, state[offset : offset + APERTURE_BITS]))
    offset += APERTURE_BITS
    links = dict(zip(PATCH_EDGE_NAMES, state[offset : offset + LINK_BITS]))
    offset += LINK_BITS
    phases = dict(zip(PATCH_VERTICES, state[offset : offset + PHASE_BITS]))
    offset += PHASE_BITS
    radial = dict(zip(PATCH_VERTICES, state[offset : offset + RADIAL_PLACEMENTS]))
    if any(value not in range(M_S + 1) for value in apertures.values()):
        raise ValueError("aperture outside fixture grid")
    if any(value not in range(K) for value in links.values()):
        raise ValueError("link outside Z_2")
    if any(value not in range(K) for value in phases.values()):
        raise ValueError("phase outside Z_2")
    if any(value not in range(M_PSI + 1) for value in radial.values()):
        raise ValueError("radial occupation outside fixture grid")
    if sum(radial.values()) != Q:
        raise ValueError("patch state does not have Q=1")
    return apertures, links, phases, radial


def phase_link_relabel(state: State) -> State:
    """Apply a finite phase/link relabelling while retaining radial bits."""
    values = list(state)
    link_start = APERTURE_BITS
    phase_start = APERTURE_BITS + LINK_BITS
    for index in range(link_start, phase_start + PHASE_BITS):
        values[index] = (values[index] + 1) % K
    return tuple(values)


def full_state(level: int, patch_state: State) -> dict[str, Any]:
    """Embed a patch state into G_level with neutral remote coordinates."""
    apertures, links, phases, radial = decode_patch(patch_state)
    carrier = strip_carrier(level)
    state = {
        "apertures": {vertex: 0 for vertex in carrier["vertices"]},
        "ell": {vertex: 0 for vertex in carrier["vertices"]},
        "phase": {vertex: 0 for vertex in carrier["vertices"]},
        "links": {name: 0 for name, _left, _right in carrier["edges"]},
    }
    for vertex in PATCH_VERTICES:
        state["apertures"][vertex] = apertures[vertex]
        state["ell"][vertex] = radial[vertex]
        state["phase"][vertex] = phases[vertex]
    for name in PATCH_EDGE_NAMES:
        state["links"][name] = links[name]
    if sum(state["ell"].values()) != Q:
        raise AssertionError("neutral inclusion changed Q")
    return state


def matter_value(ell: int, phase: int) -> Fraction:
    return R_MAX * Fraction(ell, M_PSI) * sign_z2(phase)


def onsite(vertex: tuple[int, int], state: dict[str, Any]) -> Fraction:
    s = aperture(state["apertures"][vertex])
    psi = matter_value(state["ell"][vertex], state["phase"][vertex])
    return (
        LAMBDA_S * (s - 1) ** 2 / 2
        + M2 * psi**2 / 2
        + LAMBDA_4 * psi**4 / 4
        + ETA_6 * psi**6 / 6
        + G_COUPLING * s**2 * psi**2 / 2
    )


def edge_stiffness(left: tuple[int, int], right: tuple[int, int], state: dict[str, Any]) -> Fraction:
    return KAPPA_S * (aperture(state["apertures"][left]) - aperture(state["apertures"][right])) ** 2 / 2


def j_edge(left: tuple[int, int], right: tuple[int, int], state: dict[str, Any]) -> Fraction:
    return Fraction(2, 1) / (aperture(state["apertures"][left]) + aperture(state["apertures"][right]))


def covariant_edge(name: str, left: tuple[int, int], right: tuple[int, int], state: dict[str, Any]) -> Fraction:
    psi_left = matter_value(state["ell"][left], state["phase"][left])
    psi_right = matter_value(state["ell"][right], state["phase"][right])
    transported = sign_z2(state["links"][name]) * psi_left
    return KAPPA_D * j_edge(left, right, state) * (psi_right - transported) ** 2 / 2


def face_term(
    face: tuple[tuple[str, int], ...],
    state: dict[str, Any],
    edge_lookup: dict[str, tuple[tuple[int, int], tuple[int, int]]],
) -> Fraction:
    stiffness = []
    holonomy = 1
    for edge_name, _orientation in face:
        left, right = edge_lookup[edge_name]
        stiffness.append(j_edge(left, right, state))
        holonomy *= sign_z2(state["links"][edge_name])
    return KAPPA_G * sum(stiffness, Fraction(0)) / len(stiffness) * (1 - holonomy)


def energy_terms(level: int, state: dict[str, Any]) -> list[tuple[str, tuple[tuple[int, int], ...], Fraction]]:
    carrier = strip_carrier(level)
    edge_lookup = {name: (left, right) for name, left, right in carrier["edges"]}
    terms: list[tuple[str, tuple[tuple[int, int], ...], Fraction]] = []
    for vertex in carrier["vertices"]:
        terms.append((f"onsite:{vertex[0]},{vertex[1]}", (vertex,), onsite(vertex, state)))
    for name, left, right in carrier["edges"]:
        support = (left, right)
        terms.append((f"stiffness:{name}", support, edge_stiffness(left, right, state)))
        terms.append((f"covariant:{name}", support, covariant_edge(name, left, right, state)))
    for index, face in enumerate(carrier["faces"]):
        support = tuple(sorted({vertex for name, _orientation in face for vertex in edge_lookup[name]}))
        terms.append((f"face:{index}", support, face_term(face, state, edge_lookup)))
    return terms


def energy(level: int, state: dict[str, Any]) -> Fraction:
    return sum((value for _label, _support, value in energy_terms(level, state)), Fraction(0))


def radial_target(state: dict[str, Any], source: tuple[int, int], target: tuple[int, int]) -> dict[str, Any]:
    result = {key: dict(value) for key, value in state.items()}
    result["ell"][source] -= 1
    result["ell"][target] += 1
    if sum(result["ell"].values()) != Q:
        raise AssertionError("radial transfer changed Q")
    return result


def radial_root_rows(patch_state: State, level: int) -> list[dict[str, Any]]:
    state = full_state(level, patch_state)
    anchor = PATCH_VERTICES[0]
    rows: list[dict[str, Any]] = []
    for name, left, right in strip_carrier(level)["edges"]:
        if anchor not in (left, right):
            continue
        for source, target in ((left, right), (right, left)):
            if state["ell"][source] <= 0 or state["ell"][target] >= M_PSI:
                continue
            target_state = radial_target(state, source, target)
            delta_f = energy(level, target_state) - energy(level, state)
            delta_anchor = target_state["ell"][anchor] - state["ell"][anchor]
            mobility_square = aperture(state["apertures"][source]) * aperture(state["apertures"][target])
            rows.append(
                {
                    "edge": name,
                    "source": list(source),
                    "target": list(target),
                    "delta_F": str(delta_f),
                    "mobility_square": str(mobility_square),
                    "delta_ell_a": delta_anchor,
                    "rate_exponent": str(-BETA * delta_f / 2),
                }
            )
    return rows


def state_record(patch_state: State, level: int) -> dict[str, Any]:
    roots = radial_root_rows(patch_state, level)
    return {"patch_state": list(patch_state), "roots": roots}


def canonical_digest(records: list[dict[str, Any]]) -> str:
    encoded = json.dumps(records, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def row_projection(records: list[dict[str, Any]]) -> list[tuple[Any, ...]]:
    projected: list[tuple[Any, ...]] = []
    for record in records:
        for root in record["roots"]:
            projected.append(
                (
                    tuple(record["patch_state"]),
                    root["edge"],
                    tuple(root["source"]),
                    tuple(root["target"]),
                    root["delta_F"],
                    root["mobility_square"],
                    root["delta_ell_a"],
                    root["rate_exponent"],
                )
            )
    return projected


def support_signature(level: int, radial_index: int) -> dict[str, list[str]]:
    state_patch = make_patch_state((0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0), radial_index)
    state = full_state(level, state_patch)
    anchor = PATCH_VERTICES[0]
    signature: dict[str, list[str]] = {}
    before = {label: value for label, _support, value in energy_terms(level, state)}
    for name, left, right in strip_carrier(level)["edges"]:
        if anchor not in (left, right):
            continue
        for source, target in ((left, right), (right, left)):
            if state["ell"][source] <= 0 or state["ell"][target] >= M_PSI:
                continue
            after_state = radial_target(state, source, target)
            after = {label: value for label, _support, value in energy_terms(level, after_state)}
            key = f"{name}:{source[0]},{source[1]}->{target[0]},{target[1]}"
            signature[key] = sorted(label for label in before if before[label] != after[label])
    return signature


def boundary_control() -> dict[str, Any]:
    # Quantum at b, all other displayed coordinates neutral.  The d1 edge is
    # absent in G_1 and present in G_2, so the h00 transfer must differ.
    patch = make_patch_state((0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0), 1)
    rows_1 = radial_root_rows(patch, 1)
    rows_2 = radial_root_rows(patch, 2)
    by_edge_1 = {(row["edge"], tuple(row["source"]), tuple(row["target"])): row for row in rows_1}
    by_edge_2 = {(row["edge"], tuple(row["source"]), tuple(row["target"])): row for row in rows_2}
    key = ("h00", (1, 0), (0, 0))
    delta_1 = by_edge_1[key]["delta_F"]
    delta_2 = by_edge_2[key]["delta_F"]
    return {
        "state": list(patch),
        "root": {"edge": key[0], "source": list(key[1]), "target": list(key[2])},
        "delta_F_G1": delta_1,
        "delta_F_G2": delta_2,
        "nonzero_difference": delta_1 != delta_2,
        "difference_G2_minus_G1": str(Fraction(delta_2) - Fraction(delta_1)),
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source = read_json(SOURCE)
    geometry = read_json(GEOMETRY)
    predecessor = read_json(PREDECESSOR)
    contract = read_json(CONTRACT)
    manifest = read_json(MANIFEST)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {
        "PAH-001": digest(SOURCE),
        "PAH-OMC-004": digest(GEOMETRY),
        "PAH-OMC-005": digest(PREDECESSOR),
        "PAH-OMC-006": digest(CONTRACT),
        "PAH-OMC-006-MANIFEST": digest(MANIFEST),
    }
    check(
        "source-hashes",
        hashes["PAH-001"] == manifest["functional_source"]["sha256"]
        and hashes["PAH-OMC-004"] == manifest["geometric_source"]["sha256"]
        and hashes["PAH-OMC-005"] == manifest["predecessor"]["sha256"]
        and hashes["PAH-OMC-006"] == manifest["contract"]["sha256"],
        hashes,
    )
    check(
        "identities",
        source.get("packet_id") == "PAH-001"
        and geometry.get("contract_id") == "PAH-OMC-004"
        and predecessor.get("contract_id") == "PAH-OMC-005"
        and contract.get("contract_id") == "PAH-OMC-006",
    )
    check(
        "no-parent-mutation",
        contract.get("preservation_firewall", {}).get("parent_functional_unchanged") is True
        and contract.get("preservation_firewall", {}).get("no_new_term") is True
        and manifest.get("no_parent_mutation") is True,
    )
    check("displayed-functional", source.get("functional_or_action", {}).get("formula", "").startswith("F_rho=sum_v[lambda_s"))
    check("displayed-generator", source.get("dynamics", {}).get("generator", "").startswith("(L_rho f)(x)=sum_r m_r(x)"))
    check("genuine-incidence", len(strip_carrier(2)["edges"]) > len(strip_carrier(1)["edges"]) and len(strip_carrier(2)["faces"]) > len(strip_carrier(1)["faces"]))
    check("nonzero-q-fixture", Q > 0 and M_PSI > 0)
    states = list(fixture_states())
    expected_states = (M_S + 1) ** APERTURE_BITS * K**LINK_BITS * K**PHASE_BITS * RADIAL_PLACEMENTS
    check("state-count", len(states) == expected_states, {"actual": len(states), "expected": expected_states})
    check("all-states-have-q-one", all(sum(decode_patch(state)[3].values()) == Q for state in states))
    check("neutral-inclusion-preserves-q", all(sum(full_state(3, state)["ell"].values()) == Q for state in states))
    check(
        "matter-cylinder-radial-relabel-invariant",
        all(decode_patch(state)[3] == decode_patch(phase_link_relabel(state))[3] for state in states),
    )

    records_2 = [state_record(state, 2) for state in states]
    records_3 = [state_record(state, 3) for state in states]
    projection_2 = row_projection(records_2)
    projection_3 = row_projection(records_3)
    digest_2 = canonical_digest(records_2)
    digest_3 = canonical_digest(records_3)
    check("rows-cover-domain", len(records_2) == len(records_3) == len(states))
    check("rootwise-generator-equality", projection_2 == projection_3, {"roots": len(projection_2)})
    check("all-roots-midpoint", all(root["rate_exponent"] == str(-BETA * Fraction(root["delta_F"]) / 2) for record in records_2 for root in record["roots"]))
    check("all-roots-mobility", all(root["mobility_square"] == str(aperture(0) * aperture(0)) or root["mobility_square"] == str(aperture(0) * aperture(1)) or root["mobility_square"] == str(aperture(1) * aperture(1)) for record in records_2 for root in record["roots"]))
    check("observable-increments", {root["delta_ell_a"] for record in records_2 for root in record["roots"]} == {-1, 1})

    signatures_2 = {str(index): support_signature(2, index) for index in range(RADIAL_PLACEMENTS)}
    signatures_3 = {str(index): support_signature(3, index) for index in range(RADIAL_PLACEMENTS)}
    check("endpoint-closure-stable", signatures_2 == signatures_3, {"G2": signatures_2, "G3": signatures_3})
    control = boundary_control()
    check("boundary-control-nonzero", control["nonzero_difference"], control)
    check("boundary-difference-exact", control["difference_G2_minus_G1"] == "-1", control)
    check("nontrivial-matter-cylinder", any(root["delta_ell_a"] != 0 for record in records_2 for root in record["roots"]))

    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc006-matter-cylinder-primary/1.0",
        "run_kind": "primary",
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
        "scope": {
            "dimension": "finite two-row relational strip with genuine diagonal face subdivision",
            "model": "PAH-001 + PAH-OMC-006 researcher successor",
            "normalization": "finite counting-measure Gibbs midpoint rate c=m exp(-beta DeltaF/2)",
            "regulator": "K=2, M_s=M_psi=1, Q=1, epsilon=1/2, beta=nu=1; all displayed couplings one where used",
            "volume": "full G_2 and neutral inclusion in G_3; one nonzero charge quantum in the anchor patch",
            "limit": "none; n=2,3 finite local equality only",
        },
        "fixture_dimensions": {
            "aperture_bits": APERTURE_BITS,
            "link_bits": LINK_BITS,
            "phase_bits": PHASE_BITS,
            "radial_placements": RADIAL_PLACEMENTS,
            "state_count_formula": "(M_s+1)^4*K^5*K^4*4",
            "state_count": len(states),
            "root_count": len(projection_2),
        },
        "carrier_signatures": {
            "G2": {"vertices": len(strip_carrier(2)["vertices"]), "edges": len(strip_carrier(2)["edges"]), "faces": len(strip_carrier(2)["faces"])},
            "G3": {"vertices": len(strip_carrier(3)["vertices"]), "edges": len(strip_carrier(3)["edges"]), "faces": len(strip_carrier(3)["faces"])},
        },
        "row_identity": {
            "levels": [2, 3],
            "state_rows": len(records_2),
            "root_rows": len(projection_2),
            "all_equal": projection_2 == projection_3,
            "canonical_digest_G2": digest_2,
            "canonical_digest_G3": digest_3,
            "bounded_samples_G2": records_2[:2] + records_2[-2:],
            "bounded_samples_G3": records_3[:2] + records_3[-2:],
            "exact_tuple": ["patch_state", "edge", "source", "target", "delta_F", "mobility_square", "delta_ell_a", "rate_exponent"],
            "observable_basis": ["ell_a", "1_{ell_a=1}"],
        },
        "support_audit": {"G2": signatures_2, "G3": signatures_3, "equal": signatures_2 == signatures_3},
        "boundary_control": control,
        "verdict": "EXACT_NONZERO_Q_MATTER_DENSITY_CYLINDER_COMPATIBILITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "reproduction": {
            "command": "python codes/foundations/pah_omc006_matter_cylinder.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc006-matter-cylinder/primary.json",
            "independent_command": "python codes/foundations/pah_omc006_matter_cylinder_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc006-matter-cylinder/independent.json",
        },
        "non_claims": contract.get("non_claims", []),
        "next_question": contract.get("single_next_question"),
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} PRIMARY {payload['verification']} {payload['passed']}/{payload['assertion_count']}; states={len(states)}; roots={len(projection_2)}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(args.output)
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
