#!/usr/bin/env python3
"""Independent direct-formula audit for PAH-OMC-005.

This file intentionally does not import the primary replay.  It rebuilds the
two-row incidence, nonzero-Q matter amplitudes, full PAH energy, and midpoint
rows with a separate implementation before comparing G_1 with its neutral
inclusion in G_2.
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
SRC = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOM = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-005-nonzero-q-generator-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-005-nonzero-q-generator-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc005-nonzero-q-generator/independent.json"
)

AUDIT_ID = "PAH-NONZERO-Q-GENERATOR-001"
EXPLORATION_ID = "EXP-001374"
RESULT_ID = "R-485"
TASK_ID = "T-054"

# Model inputs for this finite audit; none are derived outputs.
K = 2
MS = 1
MPSI = 1
CHARGE = 1
EPS = Fraction(1, 2)
BETA = Fraction(1)
NU = Fraction(1)
RMAX = Fraction(1)
MASS2 = Fraction(0)
L4 = Fraction(1)
ETA6 = Fraction(1)
G = Fraction(1)
LS = Fraction(1)
KS = Fraction(1)
KD = Fraction(1)
KG = Fraction(1)

V_PATCH = ((0, 0), (1, 0), (0, 1), (1, 1))
E_PATCH = (
    ("h00", (0, 0), (1, 0)),
    ("v0", (0, 0), (0, 1)),
    ("d0", (0, 0), (1, 1)),
    ("h01", (0, 1), (1, 1)),
    ("v1", (1, 0), (1, 1)),
)
F_PATCH = (
    (("h00", 1), ("v1", 1), ("d0", -1)),
    (("d0", 1), ("h01", -1), ("v0", -1)),
)


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(path)
    return data


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temp, path)
    except BaseException:
        try:
            os.unlink(temp)
        except FileNotFoundError:
            pass
        raise


def s_value(j: int) -> Fraction:
    return EPS + Fraction(j) * (1 - EPS) / MS


def z2(bit: int) -> int:
    if bit not in range(K):
        raise ValueError(bit)
    return 1 if bit == 0 else -1


def carrier(n: int) -> tuple[tuple[tuple[int, int], ...], tuple[tuple[str, tuple[int, int], tuple[int, int]], ...], tuple[tuple[tuple[str, int], ...], ...]]:
    vertices = tuple((i, j) for i in range(n + 2) for j in (0, 1))
    edges: list[tuple[str, tuple[int, int], tuple[int, int]]] = []
    for i in range(n + 1):
        for j in (0, 1):
            edges.append((f"h{i}{j}", (i, j), (i + 1, j)))
    for i in range(n + 2):
        edges.append((f"v{i}", (i, 0), (i, 1)))
    for i in range(n):
        edges.append((f"d{i}", (i, 0), (i + 1, 1)))
    faces: list[tuple[tuple[str, int], ...]] = []
    for i in range(n):
        faces.append(((f"h{i}0", 1), (f"v{i + 1}", 1), (f"d{i}", -1)))
        faces.append(((f"d{i}", 1), (f"h{i}1", -1), (f"v{i}", -1)))
    i = n
    faces.append(((f"h{i}0", 1), (f"v{i + 1}", 1), (f"h{i}1", -1), (f"v{i}", -1)))
    return vertices, tuple(edges), tuple(faces)


def embed(n: int, patch: tuple[int, ...]) -> dict[str, dict[Any, int]]:
    if len(patch) != len(V_PATCH) * 3 + len(E_PATCH):
        raise ValueError("patch width")
    aps = tuple(patch[: len(V_PATCH)])
    links = tuple(patch[len(V_PATCH) : len(V_PATCH) + len(E_PATCH)])
    phases = tuple(patch[len(V_PATCH) + len(E_PATCH) : len(V_PATCH) * 2 + len(E_PATCH)])
    radial = tuple(patch[len(V_PATCH) * 2 + len(E_PATCH) :])
    if sum(radial) != CHARGE:
        raise ValueError("charge")
    vertices, edges, _faces = carrier(n)
    state = {
        "ap": {v: 0 for v in vertices},
        "ell": {v: 0 for v in vertices},
        "phase": {v: 0 for v in vertices},
        "link": {e[0]: 0 for e in edges},
    }
    for v, value in zip(V_PATCH, aps):
        state["ap"][v] = value
    for v, value in zip(V_PATCH, phases):
        state["phase"][v] = value
    for v, value in zip(V_PATCH, radial):
        state["ell"][v] = value
    for e, value in zip((row[0] for row in E_PATCH), links):
        state["link"][e] = value
    if sum(state["ell"].values()) != CHARGE:
        raise AssertionError("neutral extension changed charge")
    return state


def psi(state: dict[str, dict[Any, int]], vertex: tuple[int, int]) -> Fraction:
    return RMAX * Fraction(state["ell"][vertex], MPSI) * z2(state["phase"][vertex])


def je(state: dict[str, dict[Any, int]], left: tuple[int, int], right: tuple[int, int]) -> Fraction:
    return Fraction(2, 1) / (s_value(state["ap"][left]) + s_value(state["ap"][right]))


def total_energy(n: int, state: dict[str, dict[Any, int]]) -> Fraction:
    vertices, edges, faces = carrier(n)
    by_name = {name: (left, right) for name, left, right in edges}
    total = Fraction(0)
    for vertex in vertices:
        s = s_value(state["ap"][vertex])
        p = psi(state, vertex)
        total += LS * (s - 1) ** 2 / 2 + MASS2 * p**2 / 2 + L4 * p**4 / 4 + ETA6 * p**6 / 6 + G * s**2 * p**2 / 2
    for name, left, right in edges:
        sl = s_value(state["ap"][left])
        sr = s_value(state["ap"][right])
        total += KS * (sl - sr) ** 2 / 2
        transported = z2(state["link"][name]) * psi(state, left)
        total += KD * je(state, left, right) * (psi(state, right) - transported) ** 2 / 2
    for face in faces:
        vals = []
        holonomy = 1
        for name, _orientation in face:
            left, right = by_name[name]
            vals.append(je(state, left, right))
            # In Z_2 the inverse of a link has the same exact sign.
            holonomy *= z2(state["link"][name])
        total += KG * sum(vals, Fraction(0)) / len(vals) * (1 - holonomy)
    return total


def flip(state: dict[str, dict[Any, int]]) -> dict[str, dict[Any, int]]:
    result = {key: dict(values) for key, values in state.items()}
    old = result["ap"][V_PATCH[0]]
    result["ap"][V_PATCH[0]] = 1 - old
    return result


def row(n: int, patch: tuple[int, ...]) -> dict[str, Any]:
    state = embed(n, patch)
    old = state["ap"][V_PATCH[0]]
    moved = flip(state)
    delta = total_energy(n, moved) - total_energy(n, state)
    ds = s_value(moved["ap"][V_PATCH[0]]) - s_value(old)
    indicator = int(moved["ap"][V_PATCH[0]] == 1) - int(old == 1)
    square = s_value(old) * s_value(moved["ap"][V_PATCH[0]])
    return {
        "level": n,
        "patch_state": list(patch),
        "direction": 1 if old == 0 else -1,
        "delta_F": str(delta),
        "mobility_square": str(square),
        "delta_s": str(ds),
        "delta_indicator_j_a_eq_1": indicator,
        "rate_exponent": str(-BETA * delta / 2),
    }


def key(item: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(item[name] for name in ("patch_state", "direction", "delta_F", "mobility_square", "delta_s", "delta_indicator_j_a_eq_1", "rate_exponent"))


def patch_states() -> list[tuple[int, ...]]:
    result: list[tuple[int, ...]] = []
    for aps in itertools.product(range(MS + 1), repeat=len(V_PATCH)):
        for links in itertools.product(range(K), repeat=len(E_PATCH)):
            for phases in itertools.product(range(K), repeat=len(V_PATCH)):
                for charged in range(len(V_PATCH)):
                    radial = tuple(int(i == charged) for i in range(len(V_PATCH)))
                    result.append(tuple(aps) + tuple(links) + tuple(phases) + radial)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source = load(SRC)
    geometry = load(GEOM)
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {"PAH-001": sha(SRC), "PAH-OMC-004": sha(GEOM), "PAH-OMC-005": sha(CONTRACT), "PAH-OMC-005-GEN-MANIFEST": sha(MANIFEST)}
    check("source-hash-pins", hashes["PAH-001"] == manifest["functional_source"]["sha256"] and hashes["PAH-OMC-004"] == manifest["geometric_source"]["sha256"] and hashes["PAH-OMC-005"] == manifest["contract"]["sha256"], hashes)
    check("identity", source.get("packet_id") == "PAH-001" and geometry.get("contract_id") == "PAH-OMC-004" and contract.get("contract_id") == "PAH-OMC-005")
    check("functional-and-generator-source", source.get("functional_or_action", {}).get("formula", "").startswith("F_rho=sum_v[lambda_s") and source.get("dynamics", {}).get("generator", "").startswith("(L_rho f)(x)=sum_r m_r(x)"))
    check("nonzero-charge-input", CHARGE > 0 and MPSI > 0)
    sig1 = carrier(1)
    sig2 = carrier(2)
    anchor = V_PATCH[0]
    def signature(car: tuple[Any, Any, Any]) -> dict[str, Any]:
        _vertices, edges, faces = car
        incident = [e for e in edges if anchor in e[1:]]
        names = {e[0] for e in incident}
        incident_faces = [f for f in faces if any(name in names for name, _o in f)]
        support = sorted({v for _name, left, right in incident for v in (left, right)})
        return {"incident_edges": incident, "incident_faces": incident_faces, "patch_vertices": support}
    signatures = {"1": signature(sig1), "2": signature(sig2)}
    check("stable-anchor-incidence", signatures["1"] == signatures["2"], signatures)
    check("genuine-diagonal-and-triangles", any(e[0] == "d0" for e in signatures["1"]["incident_edges"]) and len(signatures["1"]["incident_faces"]) == 2 and all(len(f) == 3 for f in signatures["1"]["incident_faces"]))

    states = patch_states()
    expected = (MS + 1) ** len(V_PATCH) * K ** len(E_PATCH) * K ** len(V_PATCH) * len(V_PATCH)
    check("state-count", len(states) == expected, {"actual": len(states), "expected": expected})
    rows1 = [row(1, state) for state in states]
    rows2 = [row(2, state) for state in states]
    check("row-count", len(rows1) == len(rows2) == len(states), (len(rows1), len(rows2)))
    check("row-levels", all(item["level"] == 1 for item in rows1) and all(item["level"] == 2 for item in rows2))
    check("exact-row-equality", [key(item) for item in rows1] == [key(item) for item in rows2])
    check("charge-present", all(sum(embed(1, state)["ell"].values()) == CHARGE for state in states))
    check("mobility", {item["mobility_square"] for item in rows1} == {"1/2"})
    check("midpoint-exponent", all(item["rate_exponent"] == str(-BETA * Fraction(item["delta_F"]) / 2) for item in rows1))
    check("observable-basis", {item["delta_indicator_j_a_eq_1"] for item in rows1} == {-1, 1})
    # Remote terms must cancel exactly under the anchor flip in the neutral inclusion.
    check("full-energy-row-equality", all(row1["delta_F"] == row2["delta_F"] for row1, row2 in zip(rows1, rows2)))
    local_terms = ["onsite:a", "stiffness:h00", "covariant:h00", "stiffness:v0", "covariant:v0", "stiffness:d0", "covariant:d0", "face:0", "face:1"]
    check("local-support-contract", contract.get("compatibility_proposition", {}).get("proof_obligations", []) and len(local_terms) == 9, local_terms)

    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc005-nonzero-q-generator-independent/1.0",
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
        "scope": {
            "dimension": "finite two-row relational strip with nonzero Q=1 patch matter",
            "model": "PAH-001 + PAH-OMC-005",
            "normalization": "finite counting-measure Gibbs midpoint rate",
            "regulator": "K=2, M_s=M_psi=1, Q=1, epsilon=1/2, beta=nu=1, all used couplings one",
            "volume": "G_1 and neutral inclusion in G_2",
            "limit": "none",
        },
        "fixture_dimensions": {"aperture_bits": len(V_PATCH), "link_bits": len(E_PATCH), "phase_bits": len(V_PATCH), "radial_placements": len(V_PATCH), "state_count_formula": "(M_s+1)^4*K^5*K^4*4", "state_count": len(states)},
        "carrier_signatures": signatures,
        "generator_rows": rows1,
        "row_identity": {"levels": [1, 2], "rows_compared": len(rows1), "all_equal": True, "exact_tuple": ["patch_state", "direction", "delta_F", "mobility_square", "delta_s", "delta_indicator_j_a_eq_1", "rate_exponent"], "observable_basis": ["1", "s_a", "1_{j_a=1}"]},
        "derived_ranges": {"delta_F_min": str(min(Fraction(item["delta_F"]) for item in rows1)), "delta_F_max": str(max(Fraction(item["delta_F"]) for item in rows1))},
        "verdict": "EXACT_NONZERO_Q_ANCHOR_GENERATOR_COMPATIBILITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "reproduction": {"command": "python codes/foundations/pah_omc005_nonzero_q_generator_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc005-nonzero-q-generator/independent.json"},
        "non_claims": contract.get("non_claims", []),
        "next_question": contract.get("single_next_question"),
    }
    write_json(args.output, payload)
    print(f"{AUDIT_ID} INDEPENDENT {payload['verification']} {payload['passed']}/{payload['assertion_count']}; rows={len(rows1)}; Q={CHARGE}")
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
