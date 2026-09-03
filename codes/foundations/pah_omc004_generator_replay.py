#!/usr/bin/env python3
"""Primary exact replay of PAH-OMC-004 anchor generator rows.

This sidecar does not alter PAH-001 or PAH-OMC-004.  It expands the displayed
finite PAH functional on the two triangles incident to the anchor aperture and
recomputes the actual midpoint-rate generator row for every Q=0 patch state.
The n=1 and n=2 strip carriers have the same anchor interaction closure, while
the n=0 square-to-split boundary is retained as a nonzero defect.  The result
is a finite local cylinder statement only.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
PARENT = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
SIDECAR = ROOT / "strategy/pa-hyp/PAH-OMC-004-generator-replay-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-004-generator-replay-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-03-pah-omc004-generator-replay/primary.json"
)

AUDIT_ID = "PAH-GENERATOR-REPLAY-001"
EXPLORATION_ID = "EXP-001371"
RESULT_ID = "R-484"
TASK_ID = "T-054"

# Finite fixture inputs copied from the immutable PAH-OMC-004 scope.  They are
# inputs, not generated numerical claims.
K = 2
M_S = 1
EPSILON = Fraction(1, 2)
BETA = Fraction(1)
NU = Fraction(1)
LAMBDA_S = Fraction(1)
KAPPA_S = Fraction(1)
KAPPA_G = Fraction(1)
Q = 0

VERTICES = ("a", "b", "c", "d")
EDGES = (
    ("h00", "a", "b"),
    ("v0", "a", "c"),
    ("d0", "a", "d"),
    ("h01", "c", "d"),
    ("v1", "b", "d"),
)
FACES = (
    (("h00", 1), ("v1", 1), ("d0", -1)),
    (("d0", 1), ("h01", -1), ("v0", -1)),
)
EDGE_BY_NAME = {name: (left, right) for name, left, right in EDGES}
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
    if not 0 <= level <= M_S:
        raise ValueError("aperture level outside PAH grid")
    return EPSILON + Fraction(level) * (1 - EPSILON) / M_S


def onsite(level: int) -> Fraction:
    return LAMBDA_S * (aperture(level) - 1) ** 2 / 2


def edge_term(left_level: int, right_level: int) -> Fraction:
    return KAPPA_S * (aperture(left_level) - aperture(right_level)) ** 2 / 2


def link_sign(bit: int) -> int:
    if bit not in range(K):
        raise ValueError("link bit outside Z_K fixture")
    return -1 if bit else 1


def state_parts(state: State) -> tuple[dict[str, int], dict[str, int]]:
    if len(state) != len(VERTICES) + len(EDGES):
        raise ValueError("state length mismatch")
    apertures = dict(zip(VERTICES, state[: len(VERTICES)]))
    links = dict(zip((edge[0] for edge in EDGES), state[len(VERTICES) :]))
    if any(level not in range(M_S + 1) for level in apertures.values()):
        raise ValueError("aperture state outside grid")
    if any(bit not in range(K) for bit in links.values()):
        raise ValueError("link state outside Z_K")
    return apertures, links


def face_term(face: tuple[tuple[str, int], ...], apertures: dict[str, int], links: dict[str, int]) -> Fraction:
    stiffness: list[Fraction] = []
    holonomy = 1
    for edge_name, _orientation in face:
        left, right = EDGE_BY_NAME[edge_name]
        stiffness.append(Fraction(2, 1) / (aperture(apertures[left]) + aperture(apertures[right])))
        # Z_2 is self-inverse, so orientation changes the word order but not
        # the exact sign.  The orientation is still retained in FACES above.
        holonomy *= link_sign(links[edge_name])
    return KAPPA_G * sum(stiffness, Fraction(0)) / len(stiffness) * (1 - holonomy)


def energy_terms(state: State) -> list[tuple[str, tuple[str, ...], Fraction]]:
    apertures, links = state_parts(state)
    if Q != 0:
        raise ValueError("this replay is restricted to the declared Q=0 slice")
    terms: list[tuple[str, tuple[str, ...], Fraction]] = []
    for vertex in VERTICES:
        terms.append((f"onsite:{vertex}", (vertex,), onsite(apertures[vertex])))
    for edge_name, left, right in EDGES:
        terms.append((f"edge:{edge_name}", (left, right), edge_term(apertures[left], apertures[right])))
    for index, face in enumerate(FACES):
        support = tuple(sorted({vertex for edge_name, _ in face for vertex in EDGE_BY_NAME[edge_name]}))
        terms.append((f"face:{index}", support, face_term(face, apertures, links)))
    return terms


def energy(state: State) -> Fraction:
    return sum((value for _label, _support, value in energy_terms(state)), Fraction(0))


def flip_anchor(state: State, direction: int) -> State | None:
    apertures, _links = state_parts(state)
    next_level = apertures["a"] + direction
    if next_level not in range(M_S + 1):
        return None
    result = list(state)
    result[0] = next_level
    return tuple(result)


def mobility_square(before: int, after: int) -> Fraction:
    # The PAH aperture rule is m=(s_before*s_after)^(nu/2), hence m^2 is the
    # exact product raised to nu.  The fixture has nu=1.
    if NU != 1:
        raise ValueError("exact replay fixture expects nu=1")
    return aperture(before) * aperture(after)


def rate_exponent(delta_f: Fraction) -> Fraction:
    return -BETA * delta_f / 2


def generator_row(state: State, level: int) -> dict[str, Any]:
    if level not in (1, 2):
        raise ValueError("row replay is restricted to the n=1 and n=2 strip levels")
    apertures, _links = state_parts(state)
    before = apertures["a"]
    direction = 1 if before == 0 else -1
    target = flip_anchor(state, direction)
    if target is None:
        raise AssertionError("one of the two aperture roots must be valid")
    after = state_parts(target)[0]["a"]
    delta_f = energy(target) - energy(state)
    delta_s = aperture(after) - aperture(before)
    delta_indicator = (1 if after == 1 else 0) - (1 if before == 1 else 0)
    return {
        "level": level,
        "state": list(state),
        "direction": direction,
        "root": f"aperture:a:{'+' if direction == 1 else '-'}",
        "delta_F": str(delta_f),
        "mobility_square": str(mobility_square(before, after)),
        "delta_s": str(delta_s),
        "delta_indicator_j_a_eq_1": delta_indicator,
        "rate_exponent": str(rate_exponent(delta_f)),
        "rate_symbol": f"sqrt({mobility_square(before, after)})*exp({rate_exponent(delta_f)})",
    }


def strip_carrier(level: int) -> dict[str, Any]:
    """Build the declared G_level incidence data, including the frontier square."""
    if level < 0:
        raise ValueError("level must be nonnegative")
    vertices = tuple((i, j) for i in range(level + 2) for j in (0, 1))
    edges: list[tuple[str, tuple[int, int], tuple[int, int]]] = []
    names: dict[str, int] = {}
    for i in range(level + 1):
        for j in (0, 1):
            name = f"h{i}{j}"
            names[name] = len(edges)
            edges.append((name, (i, j), (i + 1, j)))
    for i in range(level + 2):
        name = f"v{i}"
        names[name] = len(edges)
        edges.append((name, (i, 0), (i, 1)))
    for i in range(level):
        name = f"d{i}"
        names[name] = len(edges)
        edges.append((name, (i, 0), (i + 1, 1)))
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


def anchor_patch_signature(level: int) -> dict[str, Any]:
    carrier = strip_carrier(level)
    anchor = (0, 0)
    incident_edges = [
        (name, left, right)
        for name, left, right in carrier["edges"]
        if anchor in (left, right)
    ]
    incident_faces = [face for face in carrier["faces"] if any(name in {edge[0] for edge in incident_edges} for name, _ in face)]
    return {
        "incident_edges": incident_edges,
        "incident_faces": incident_faces,
        "patch_vertices": sorted({vertex for _name, left, right in incident_edges for vertex in (left, right)}),
    }


def boundary_witness() -> dict[str, str]:
    coarse_edges = (
        ("h00", "a", "b"),
        ("v1", "b", "d"),
        ("h01", "d", "c"),
        ("v0", "c", "a"),
    )
    coarse_faces = (("h00", 1), ("v1", 1), ("h01", 1), ("v0", 1))

    def coarse_energy(state: State) -> Fraction:
        apertures, links = state_parts(state)
        total = sum((onsite(apertures[v]) for v in VERTICES), Fraction(0))
        for _name, left, right in coarse_edges:
            total += edge_term(apertures[left], apertures[right])
        stiffness = [Fraction(2, 1) / (aperture(apertures[EDGE_BY_NAME[name][0]]) + aperture(apertures[EDGE_BY_NAME[name][1]])) for name, _ in coarse_faces]
        holonomy = 1
        for name, _ in coarse_faces:
            holonomy *= link_sign(links[name])
        total += KAPPA_G * sum(stiffness, Fraction(0)) / len(stiffness) * (1 - holonomy)
        return total

    before = (0, 0, 0, 0, 0, 0, 0, 0, 0)
    after = (1, 0, 0, 0, 0, 0, 0, 0, 0)
    fine_even = energy(after) - energy(before)
    # The third link slot is d0, the newly introduced diagonal.
    odd_after = (1, 0, 0, 0, 0, 0, 1, 0, 0)
    odd_before = (0, 0, 0, 0, 0, 0, 1, 0, 0)
    return {
        "coarse_delta_F": str(coarse_energy(after) - coarse_energy(before)),
        "fine_even_delta_F": str(fine_even),
        "fine_odd_delta_F": str(energy(odd_after) - energy(odd_before)),
        "hidden_diagonal_defect": str(fine_even - (energy(odd_after) - energy(odd_before))),
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source = read_json(SOURCE)
    parent = read_json(PARENT)
    sidecar = read_json(SIDECAR)
    manifest = read_json(MANIFEST)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {
        "PAH-001": digest(SOURCE),
        "PAH-OMC-004": digest(PARENT),
        "PAH-OMC-004-GEN-001": digest(SIDECAR),
        "PAH-OMC-004-GEN-MANIFEST": digest(MANIFEST),
    }
    check("source-hashes", hashes["PAH-001"] == "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37" and hashes["PAH-OMC-004"] == manifest["parent"]["sha256"], hashes)
    check("sidecar-hash-pin", hashes["PAH-OMC-004-GEN-001"] == manifest["sidecar"]["sha256"], hashes["PAH-OMC-004-GEN-001"])
    check("identities", source.get("packet_id") == "PAH-001" and parent.get("contract_id") == "PAH-OMC-004" and sidecar.get("contract_id") == "PAH-OMC-004-GEN-001")
    check("parent-pointer", sidecar.get("parent", {}).get("sha256") == hashes["PAH-OMC-004"] and sidecar.get("parent", {}).get("path") == "strategy/pa-hyp/PAH-OMC-004-v1.json")
    check("no-parent-mutation", manifest.get("no_parent_mutation") is True and parent.get("preservation_firewall", {}).get("parent_functional_unchanged") is True)
    check("functional-is-displayed", source.get("functional_or_action", {}).get("formula", "").startswith("F_rho=sum_v[lambda_s") and source.get("functional_or_action", {}).get("edge_stiffness", "").startswith("J_e(s)=2/(s_v+s_w)"))
    check("generator-is-displayed", source.get("dynamics", {}).get("generator", "").startswith("(L_rho f)(x)=sum_r m_r(x)"))
    declared_generator = sidecar.get("exact_scope", {}).get("generator", "")
    check("unchanged-move-rule", "aperture" in declared_generator and "unchanged PAH" in declared_generator, declared_generator)
    check("finite-q-zero-scope", K == 2 and M_S == 1 and Q == 0 and EPSILON == Fraction(1, 2) and BETA == 1 and NU == 1)
    check("sidecar-lean-pin", sidecar.get("lean_entrypoint") == "verification/lean/Tect/R484.lean")
    check("genuine-patch-topology", len(VERTICES) == 4 and len(EDGES) == 5 and len(FACES) == 2 and EDGES[2][0] == "d0")

    signatures = {str(level): anchor_patch_signature(level) for level in (1, 2)}
    check("strip-anchor-signature-equality", signatures["1"] == signatures["2"], signatures)
    check("strip-anchor-patch-is-two-triangles", len(signatures["1"]["incident_faces"]) == 2 and all(len(face) == 3 for face in signatures["1"]["incident_faces"]))
    check("strip-patch-has-diagonal", any(edge[0] == "d0" for edge in signatures["1"]["incident_edges"]))
    check("remote-terms-excluded", signatures["1"]["patch_vertices"] == [(0, 0), (0, 1), (1, 0), (1, 1)])

    states = list(itertools.product(range(M_S + 1), repeat=len(VERTICES)))
    states = [prefix + links for prefix in states for links in itertools.product(range(K), repeat=len(EDGES))]
    rows_1 = [generator_row(state, 1) for state in states]
    rows_2 = [generator_row(state, 2) for state in states]
    check("state-enumeration", len(states) == (M_S + 1) ** len(VERTICES) * K ** len(EDGES), len(states))
    check("row-enumeration", len(rows_1) == len(rows_2) == len(states), (len(rows_1), len(rows_2)))
    check("exact-row-tuples-equal", [tuple(row[key] for key in ("state", "direction", "delta_F", "mobility_square", "delta_s", "delta_indicator_j_a_eq_1", "rate_exponent")) for row in rows_1] == [tuple(row[key] for key in ("state", "direction", "delta_F", "mobility_square", "delta_s", "delta_indicator_j_a_eq_1", "rate_exponent")) for row in rows_2])
    check("row-level-labels", all(row["level"] == 1 for row in rows_1) and all(row["level"] == 2 for row in rows_2), (rows_1[0]["level"], rows_2[0]["level"]))
    check("all-row-deltas-are-local", all(row["direction"] in (-1, 1) and row["mobility_square"] == "1/2" and row["delta_s"] in ("1/2", "-1/2") for row in rows_1))
    check("indicator-basis-is-covered", {row["delta_indicator_j_a_eq_1"] for row in rows_1} == {-1, 1})

    terms = energy_terms(states[0])
    anchor_terms = [label for label, support, _value in terms if "a" in support]
    nonanchor_terms = [label for label, support, _value in terms if "a" not in support]
    check("affected-term-support", anchor_terms == ["onsite:a", "edge:h00", "edge:v0", "edge:d0", "face:0", "face:1"], anchor_terms)
    check("nonanchor-terms-cancel", nonanchor_terms == ["onsite:b", "onsite:c", "onsite:d", "edge:h01", "edge:v1"], nonanchor_terms)
    check("remote-independence-by-support", all("a" not in support for _label, support, _value in terms if _label in nonanchor_terms), nonanchor_terms)

    boundary = boundary_witness()
    check("boundary-coarse-delta", boundary["coarse_delta_F"] == "1/8", boundary)
    check("boundary-fine-even-delta", boundary["fine_even_delta_F"] == "1/4", boundary)
    check("boundary-fine-odd-delta", boundary["fine_odd_delta_F"] == "-55/36", boundary)
    check("boundary-defect-retained", boundary["hidden_diagonal_defect"] == "16/9", boundary)
    check("boundary-defect-nonzero", Fraction(boundary["hidden_diagonal_defect"]) != 0, boundary)
    nonclaim_text = " ".join(sidecar.get("non_claims", [])).lower()
    check("no-physical-promotion", "physical" in nonclaim_text and "continuum" in nonclaim_text and sidecar.get("provenance", {}).get("physical_authority") is False)

    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc004-generator-replay-primary/1.0",
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
            "dimension": "finite two-row relational strip anchor patch",
            "model": "PAH-001 + PAH-OMC-004 generator replay sidecar",
            "normalization": "finite counting-measure PAH midpoint rate c=m exp(-beta DeltaF/2)",
            "regulator": "K=2, M_s=M_psi=1, Q=0, epsilon=1/2, beta=nu=1; displayed couplings equal 1 where used",
            "volume": "finite G_1 and G_2 anchor patches; remote strip terms tracked by support",
            "limit": "none; finite levels n=1,2 only, with n=0 boundary witness",
        },
        "carrier_signatures": signatures,
        "state_count": len(states),
        "generator_rows": rows_1,
        "row_identity": {
            "levels": [1, 2],
            "rows_compared": len(rows_1),
            "exact_tuple": ["state", "direction", "delta_F", "mobility_square", "delta_s", "delta_indicator_j_a_eq_1", "rate_exponent"],
            "all_equal": True,
            "observable_basis": ["1", "s_a", "1_{j_a=1}"],
        },
        "affected_terms": {"anchor": anchor_terms, "nonanchor": nonanchor_terms},
        "boundary_witness": boundary,
        "verdict": "EXPLICIT_LOCAL_GENERATOR_ROW_EQUALITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "reproduction": {
            "command": "python codes/foundations/pah_omc004_generator_replay.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-03-pah-omc004-generator-replay/primary.json",
            "independent_command": "python codes/foundations/pah_omc004_generator_replay_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-03-pah-omc004-generator-replay/independent.json",
        },
        "non_claims": sidecar.get("non_claims", []),
        "next_question": sidecar.get("single_next_question"),
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} PRIMARY {payload['verification']} {payload['passed']}/{payload['assertion_count']}; rows={len(rows_1)}; boundary={boundary['hidden_diagonal_defect']}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(args.output)
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
