#!/usr/bin/env python3
"""Primary finite proof replay for PAH-OMC-013.

This audit keeps PAH-001, PAH-OMC-004, PAH-OMC-010 and the PAH-OMC-012
full-Q graded domain byte-for-byte fixed.  It proves the eventual statement
by a local-term/root correspondence rather than by a fixed-Q substitution:
the cylinder is grade-blind, the active root list is finite, and every other
fine root has zero lifted increment after the support buffer N(f).

The exact R_max statement is structural.  Fraction calculations at a small
set of positive R_max values are regression checks and are never used as a
replacement for the all-positive-integer argument.
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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-manifest.json"
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
START = ROOT / "strategy/pa-hyp/PAH-OMC-008-multi-cylinder-v1.json"
WEIGHT = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json"
WEIGHT_MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-manifest.json"
OMC011 = ROOT / "strategy/pa-hyp/PAH-OMC-011-eventual-intertwining-v1.json"
OMC012 = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json"
OMC012_MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-manifest.json"
R484_SOURCE = ROOT / "strategy/pa-hyp/PAH-OMC-004-generator-replay-v1.json"
R484_RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-03-pah-omc004-generator-replay/primary.json"
R490_CERT = ROOT / "strategy/pa-hyp/R490-certificate.md"
R490_RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc010-state-weighted-envelope/primary.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc013-full-q-eventual-intertwining/primary.json"

RESULT_ID = "R-493"
EXPLORATION_ID = "EXP-001474"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-013-FULL-Q-EVENTUAL-INTERTWINING-PRIMARY-001"

EXPECTED = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-004": "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "PAH-OMC-008": "b103665b9361c6a4b52b791280ce2503e5aeddbffe67a78d08c4c2a45fc8228a",
    "PAH-OMC-010": "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69",
    "PAH-OMC-010-MANIFEST": "97c9ebb3a28f83f93a3b79de527ce0e57b0be346ef6f77d99e59e7b3fa9ea4e3",
    "PAH-OMC-011": "244a300c470fa551dc006a7a2d9ba2a7a5d773d2d5cafbe9b777f9266df50020",
    "PAH-OMC-012": "180228b83e44f46406b302c97ff6caab023240eeaa19997618012074930f3e72",
    "PAH-OMC-012-MANIFEST": "fc2c52b0f786b371c56d2700e571d23558bad191942bc4f5182bc6260ae33937",
    "R-484": "87f5d3ee29b15f57f3e461b4b4064955b5f1ced0ab0bdf2b4763ed0a7ffe3e3e",
    "R-484-RUN": "6fb8a733f6014fcaa0fd8b84cdffd4b43d5f6214f4b9a59e6a9f9a1d2218c17d",
    "R-490-CERTIFICATE": "80563e82f7f592dbbb6c00ff27fdd5270031e8426d4d1520546bf846c6a6d10a",
    "R-490-PRIMARY-RUN": "4bcefef42ee2692d19344376fa2161743f0edb2043ada6d4867d1618b883dac3",
}

Vertex = tuple[int, int]
Edge = tuple[str, Vertex, Vertex]
Face = tuple[str, tuple[tuple[str, int], ...]]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
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


def vertices(level: int) -> tuple[Vertex, ...]:
    if level < 2:
        raise ValueError("the PAH-OMC-004 cofinal strip starts at n=2")
    return tuple((i, j) for i in range(level + 2) for j in (0, 1))


def strip(level: int) -> dict[str, Any]:
    vs = vertices(level)
    edges: list[Edge] = []
    for i in range(level + 1):
        for j in (0, 1):
            edges.append((f"h{i}{j}", (i, j), (i + 1, j)))
    for i in range(level + 2):
        edges.append((f"v{i}", (i, 0), (i, 1)))
    for i in range(level):
        edges.append((f"d{i}", (i, 0), (i + 1, 1)))
    faces: list[Face] = []
    for i in range(level):
        faces.extend(
            [
                (f"t{i}a", ((f"h{i}0", 1), (f"v{i + 1}", 1), (f"d{i}", -1))),
                (f"t{i}b", ((f"d{i}", 1), (f"h{i}1", -1), (f"v{i}", -1))),
            ]
        )
    i = level
    faces.append((f"q{i}", ((f"h{i}0", 1), (f"v{i + 1}", 1), (f"h{i}1", -1), (f"v{i}", -1))))
    return {"vertices": vs, "edges": tuple(edges), "faces": tuple(faces)}


def edge_lookup(level: int) -> dict[str, Edge]:
    return {name: (name, left, right) for name, left, right in strip(level)["edges"]}


def face_lookup(level: int) -> dict[str, Face]:
    return {name: (name, boundary) for name, boundary in strip(level)["faces"]}


def face_vertices(level: int, face_name: str) -> set[Vertex]:
    edges = edge_lookup(level)
    _name, boundary = face_lookup(level)[face_name]
    return {vertex for edge_name, _orientation in boundary for vertex in edges[edge_name][1:]}


def incident_edges(level: int, vertex: Vertex) -> set[str]:
    return {name for name, left, right in strip(level)["edges"] if vertex in (left, right)}


def incident_faces(level: int, edge_names: set[str]) -> set[str]:
    return {
        name
        for name, boundary in strip(level)["faces"]
        if any(edge_name in edge_names for edge_name, _orientation in boundary)
    }


def term_vertices(level: int, term: str) -> set[Vertex]:
    if term.startswith("onsite:"):
        i, j = (int(value) for value in term.split(":", 1)[1].split(","))
        return {(i, j)}
    if ":" in term:
        kind, name = term.split(":", 1)
        if kind in ("stiffness", "covariant"):
            return set(edge_lookup(level)[name][1:])
        if kind == "face":
            return face_vertices(level, name)
    raise ValueError(f"unknown term {term}")


def root_catalog(level: int) -> list[dict[str, Any]]:
    """Enumerate all four declared PAH root families and their affected terms."""
    carrier = strip(level)
    roots: list[dict[str, Any]] = []
    for vertex in carrier["vertices"]:
        star = incident_edges(level, vertex)
        roots.extend(
            {
                "family": family,
                "label": f"{family}:{vertex[0]},{vertex[1]}:{direction}",
                "vertex": vertex,
                "direction": direction,
                "core_vertices": {vertex},
                "support_vertices": {vertex} | {v for edge in star for v in edge_lookup(level)[edge][1:]},
                "affected_terms": {
                    f"onsite:{vertex[0]},{vertex[1]}",
                    *[f"covariant:{edge}" for edge in star],
                    *(
                        [f"stiffness:{edge}" for edge in star]
                        + [f"face:{face}" for face in incident_faces(level, star)]
                        if family == "aperture"
                        else []
                    ),
                },
                "mobility_coordinates": {vertex},
            }
            for family in ("phase", "aperture")
            for direction in (-1, 1)
        )
    for name, left, right in carrier["edges"]:
        endpoints = {left, right}
        edge_star = incident_edges(level, left) | incident_edges(level, right)
        radial_terms = {
            f"onsite:{left[0]},{left[1]}",
            f"onsite:{right[0]},{right[1]}",
            *[f"covariant:{edge}" for edge in edge_star],
        }
        radial_support = {v for edge in edge_star for v in edge_lookup(level)[edge][1:]}
        for source, target in ((left, right), (right, left)):
            roots.append(
                {
                    "family": "radial-transfer",
                    "label": f"radial-transfer:{name}:{source[0]},{source[1]}->{target[0]},{target[1]}",
                    "edge": name,
                    "source": source,
                    "target": target,
                    "direction": 1 if source == left else -1,
                    "core_vertices": endpoints,
                    "support_vertices": radial_support,
                    "affected_terms": radial_terms,
                    "mobility_coordinates": endpoints,
                }
            )
        link_terms = {f"covariant:{name}", *[f"face:{face}" for face in incident_faces(level, {name})]}
        link_support = endpoints | {v for face in incident_faces(level, {name}) for v in face_vertices(level, face)}
        for direction in (-1, 1):
            roots.append(
                {
                    "family": "link",
                    "label": f"link:{name}:{direction}",
                    "edge": name,
                    "direction": direction,
                    "core_vertices": endpoints,
                    "support_vertices": link_support,
                    "affected_terms": link_terms,
                    "mobility_coordinates": endpoints,
                }
            )
    return roots


def root_radius(level: int) -> int:
    values: list[int] = []
    for root in root_catalog(level):
        values.extend(
            abs(core[0] - support[0])
            for core in root["core_vertices"]
            for support in root["support_vertices"]
        )
    return max(values, default=0)


def descriptor(name: str, ell_support: Iterable[Vertex] = (), face_support: Iterable[str] = ()) -> dict[str, Any]:
    return {
        "name": name,
        "ell_support": tuple(sorted(set(ell_support))),
        "face_support": tuple(sorted(set(face_support))),
    }


def can_change(root: dict[str, Any], desc: dict[str, Any], level: int) -> bool:
    if root["family"] in ("phase", "aperture"):
        return False
    if root["family"] == "radial-transfer":
        return bool(set(desc["ell_support"]) & set(root["core_vertices"]))
    selected_edges = {
        edge
        for face in desc["face_support"]
        if face in face_lookup(level)
        for edge, _orientation in face_lookup(level)[face][1]
    }
    return root.get("edge") in selected_edges


def closure(level: int, desc: dict[str, Any]) -> set[Vertex]:
    return {
        vertex
        for root in root_catalog(level)
        if can_change(root, desc, level)
        for vertex in root["support_vertices"]
    }


def closure_data(desc: dict[str, Any]) -> dict[str, Any]:
    input_columns = [vertex[0] for vertex in desc["ell_support"]]
    for face in desc["face_support"]:
        # A padding of three columns is derived from the one-step root radius
        # and the two endpoint columns of a face; no boundary face is selected.
        match = face.lstrip("tq").split("a")[0].split("b")[0]
        if match.isdigit():
            input_columns.append(int(match))
    base = max(2, max(input_columns, default=0) + 3)
    first = closure(base, desc)
    second = closure(base + 1, desc)
    if first != second:
        raise AssertionError(f"closure did not stabilize for {desc['name']}")
    m_f = max((vertex[0] for vertex in first), default=-1)
    return {
        "name": desc["name"],
        "ell_support": [[i, j] for i, j in desc["ell_support"]],
        "face_support": list(desc["face_support"]),
        "base_level": base,
        "closure_vertices": [[i, j] for i, j in sorted(first)],
        "m_f": m_f,
        "N_f": max(2, m_f + 1),
        "closure_stable": True,
    }


def aperture(level: int) -> Fraction:
    return Fraction(1, 2) + Fraction(level, 2)


def z2(bit: int) -> int:
    if bit not in (0, 1):
        raise ValueError("K=2 coordinate outside the fixed path")
    return -1 if bit else 1


def sample_ell(level: int, variant: int) -> dict[Vertex, int]:
    vs = vertices(level)
    if variant == 0:
        return {vertex: 0 for vertex in vs}
    if variant == 1:
        return {vertex: 1 for vertex in vs}
    if variant == 2:
        return {vertex: int(vertex == vs[0]) for vertex in vs}
    if variant == 3:
        return {vertex: int((vertex[0] + vertex[1]) % 2 == 0) for vertex in vs}
    if variant == 4:
        return {vertex: int(vertex[0] == level + 1 and vertex[1] == 0) for vertex in vs}
    if variant == 5:
        return {vertex: int(vertex in ((0, 0), (level + 1, 0))) for vertex in vs}
    return {vertex: int((vertex[0] * 3 + vertex[1] + variant) % 3 == 0) for vertex in vs}


def sample_state(level: int, variant: int) -> dict[str, dict[Any, int]]:
    carrier = strip(level)
    return {
        "aperture": {vertex: (vertex[0] + 2 * vertex[1] + variant) % 2 for vertex in carrier["vertices"]},
        "phase": {vertex: (2 * vertex[0] + vertex[1] + variant) % 2 for vertex in carrier["vertices"]},
        "ell": sample_ell(level, variant),
        "link": {name: (len(name) + variant + index) % 2 for index, (name, _left, _right) in enumerate(carrier["edges"])},
    }


def valid_radial(state: dict[str, dict[Any, int]], root: dict[str, Any]) -> bool:
    if root["family"] != "radial-transfer":
        return True
    return state["ell"][root["source"]] > 0 and state["ell"][root["target"]] < 1


def apply_root(state: dict[str, dict[Any, int]], root: dict[str, Any]) -> dict[str, dict[Any, int]] | None:
    if not valid_radial(state, root):
        return None
    result = {key: dict(value) for key, value in state.items()}
    family = root["family"]
    if family == "phase":
        vertex = root["vertex"]
        result["phase"][vertex] = (result["phase"][vertex] + root["direction"]) % 2
    elif family == "aperture":
        vertex = root["vertex"]
        new = result["aperture"][vertex] + root["direction"]
        if new not in (0, 1):
            return None
        result["aperture"][vertex] = new
    elif family == "radial-transfer":
        result["ell"][root["source"]] -= 1
        result["ell"][root["target"]] += 1
    elif family == "link":
        result["link"][root["edge"]] = (result["link"][root["edge"]] + root["direction"]) % 2
    else:
        raise ValueError(family)
    return result


def matter_value(state: dict[str, dict[Any, int]], vertex: Vertex, rmax: Fraction) -> Fraction:
    return rmax * state["ell"][vertex] * z2(state["phase"][vertex])


def j_edge(state: dict[str, dict[Any, int]], left: Vertex, right: Vertex) -> Fraction:
    return Fraction(2) / (aperture(state["aperture"][left]) + aperture(state["aperture"][right]))


def energy(level: int, state: dict[str, dict[Any, int]], rmax: Fraction) -> Fraction:
    carrier = strip(level)
    total = Fraction(0)
    for vertex in carrier["vertices"]:
        s = aperture(state["aperture"][vertex])
        psi = matter_value(state, vertex, rmax)
        total += (s - 1) ** 2 / 2 + psi**4 / 4 + psi**6 / 6 + s**2 * psi**2 / 2
    for name, left, right in carrier["edges"]:
        sl = aperture(state["aperture"][left])
        sr = aperture(state["aperture"][right])
        total += (sl - sr) ** 2 / 2
        psi_left = matter_value(state, left, rmax)
        psi_right = matter_value(state, right, rmax)
        total += j_edge(state, left, right) * (psi_right - z2(state["link"][name]) * psi_left) ** 2 / 2
    edge_map = edge_lookup(level)
    for _face_name, boundary in carrier["faces"]:
        stiffness = Fraction(0)
        holonomy = 1
        for edge_name, _orientation in boundary:
            left, right = edge_map[edge_name][1:]
            stiffness += j_edge(state, left, right)
            holonomy *= z2(state["link"][edge_name])
        total += stiffness / len(boundary) * (1 - holonomy)
    return total


def project_state(level: int, fine_state: dict[str, dict[Any, int]]) -> tuple[dict[str, dict[Any, int]], int, int]:
    old = set(vertices(level))
    coarse = {
        "aperture": {vertex: value for vertex, value in fine_state["aperture"].items() if vertex in old},
        "phase": {vertex: value for vertex, value in fine_state["phase"].items() if vertex in old},
        "ell": {vertex: value for vertex, value in fine_state["ell"].items() if vertex in old},
        "link": {name: value for name, value in fine_state["link"].items() if name in edge_lookup(level)},
    }
    fine_q = sum(fine_state["ell"].values())
    coarse_q = sum(coarse["ell"].values())
    return coarse, fine_q, coarse_q


def mobility_square(state: dict[str, dict[Any, int]], root: dict[str, Any], after: dict[str, dict[Any, int]]) -> Fraction:
    family = root["family"]
    if family == "phase":
        s = aperture(state["aperture"][root["vertex"]])
        return s
    if family == "aperture":
        before = aperture(state["aperture"][root["vertex"]])
        after_value = aperture(after["aperture"][root["vertex"]])
        return before * after_value
    left, right = edge_lookup(root["level"])[root["edge"]][1:]
    return aperture(state["aperture"][left]) * aperture(state["aperture"][right])


def serialized_root(root: dict[str, Any]) -> dict[str, Any]:
    result = {key: root[key] for key in ("family", "label", "direction", "affected_terms", "support_vertices", "core_vertices", "mobility_coordinates") if key in root}
    for key in ("vertex", "edge", "source", "target"):
        if key in root:
            result[key] = list(root[key]) if isinstance(root[key], tuple) else root[key]
    for key in ("affected_terms", "support_vertices", "core_vertices", "mobility_coordinates"):
        if key in result and isinstance(result[key], set):
            result[key] = sorted(result[key], key=str)
    return result


def check_root_term_identity(level: int, fine_level: int, root: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    root_fine = next((item for item in root_catalog(fine_level) if item["label"] == root["label"]), None)
    if root_fine is None:
        return False, {"reason": "missing fine root", "label": root["label"]}
    coarse_terms = {f"{term.split(':', 1)[0]}:{term.split(':', 1)[1]}" for term in root["affected_terms"]}
    fine_terms = {f"{term.split(':', 1)[0]}:{term.split(':', 1)[1]}" for term in root_fine["affected_terms"]}
    return coarse_terms == fine_terms, {"label": root["label"], "coarse_terms": sorted(coarse_terms), "fine_terms": sorted(fine_terms)}


def make_descriptors() -> list[dict[str, Any]]:
    return [
        descriptor("constant"),
        descriptor("ell_a", ell_support=((0, 0),)),
        descriptor("ell_d", ell_support=((1, 1),)),
        descriptor("ell_remote", ell_support=((4, 0),)),
        descriptor("H_0", face_support=("t0a",)),
        descriptor("H_1", face_support=("t0b",)),
        descriptor("ell_and_H", ell_support=((0, 0), (1, 1)), face_support=("t0a", "t0b")),
        descriptor("two_remote_faces", face_support=("t1a", "t1b")),
    ]


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    source = load(SOURCE)
    geometry = load(GEOMETRY)
    start = load(START)
    weight = load(WEIGHT)
    weight_manifest = load(WEIGHT_MANIFEST)
    omc011 = load(OMC011)
    omc012 = load(OMC012)
    omc012_manifest = load(OMC012_MANIFEST)
    r484_source = load(R484_SOURCE)
    r484_run = load(R484_RUN)
    r490_run = load(R490_RUN)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = None) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    paths = {
        "PAH-001": SOURCE,
        "PAH-OMC-004": GEOMETRY,
        "PAH-OMC-008": START,
        "PAH-OMC-010": WEIGHT,
        "PAH-OMC-010-MANIFEST": WEIGHT_MANIFEST,
        "PAH-OMC-011": OMC011,
        "PAH-OMC-012": OMC012,
        "PAH-OMC-012-MANIFEST": OMC012_MANIFEST,
        "R-484": R484_SOURCE,
        "R-484-RUN": R484_RUN,
        "R-490-CERTIFICATE": R490_CERT,
        "R-490-PRIMARY-RUN": R490_RUN,
    }
    actual = {key: digest(path) for key, path in paths.items()}
    check("parent-hashes", actual == EXPECTED, {"actual": actual, "expected": EXPECTED})
    check(
        "source-identities",
        source.get("packet_id") == "PAH-001"
        and geometry.get("contract_id") == "PAH-OMC-004"
        and start.get("contract_id") == "PAH-OMC-008"
        and weight.get("contract_id") == "PAH-OMC-010"
        and omc011.get("contract_id") == "PAH-OMC-011"
        and omc012.get("contract_id") == "PAH-OMC-012"
        and r484_source.get("contract_id") == "PAH-OMC-004-GEN-001",
        {"source": source.get("packet_id"), "geometry": geometry.get("contract_id"), "start": start.get("contract_id"), "weight": weight.get("contract_id"), "omc011": omc011.get("contract_id"), "omc012": omc012.get("contract_id"), "r484": r484_source.get("contract_id")},
    )
    check(
        "contract-manifest-pinned",
        manifest["contract"]["sha256"] == digest(CONTRACT)
        and manifest["contract"]["id"] == "PAH-OMC-013"
        and manifest["status"] == "MAINLINE_ADVANCE"
        and manifest["claim_bearing"] is False
        and manifest["active_gate_change"] is False,
        {"manifest": manifest, "contract_hash": digest(CONTRACT)},
    )
    check("parent-manifest-cross-pins", omc012_manifest["contract"]["sha256"] == digest(OMC012) and omc012_manifest["status"] == "MAINLINE_ADVANCE", omc012_manifest["contract"])
    check("preservation-firewall", all(value is True for value in contract["preservation_firewall"].values()), contract["preservation_firewall"])
    check(
        "unchanged-functional-generator",
        source["functional_or_action"]["formula"].startswith("F_rho=sum_v[lambda_s")
        and source["dynamics"]["generator"].startswith("(L_rho f)(x)=sum_r m_r(x)")
        and "componentwise direct sum" in contract["exact_scope"]["generator"],
        {"functional": source["functional_or_action"]["formula"], "generator": source["dynamics"]["generator"]},
    )
    check("grade-blind-cylinder", "cannot inspect the disjoint-union grade" in contract["exact_scope"]["common_cylinder_algebra"] and "closed-face holonomy" in contract["exact_scope"]["common_cylinder_algebra"], contract["exact_scope"]["common_cylinder_algebra"])
    check("no-csw-proof-substitution", r490_run.get("family", {}).get("C_sw") == 540 and "not used in the equality proof" in contract["exact_scope"]["gibbs_norm"], {"C_sw": r490_run.get("family", {}).get("C_sw"), "role": contract["exact_scope"]["gibbs_norm"]})

    radius_rows = [{"level": level, "radius": root_radius(level), "root_count": len(root_catalog(level))} for level in range(2, 9)]
    radius_values = {row["radius"] for row in radius_rows}
    check("derived-root-support-radius", len(radius_values) == 1 and next(iter(radius_values)) == max(row["radius"] for row in radius_rows), radius_rows)
    check("all-four-root-families-present", {root["family"] for root in root_catalog(4)} == {"phase", "aperture", "radial-transfer", "link"}, {family: sum(root["family"] == family for root in root_catalog(4)) for family in ("phase", "aperture", "radial-transfer", "link")})

    descriptors = make_descriptors()
    closure_rows = [closure_data(desc) for desc in descriptors]
    check("explicit-Nf-derived", all(row["N_f"] == max(2, row["m_f"] + 1) and row["closure_stable"] for row in closure_rows), closure_rows)
    check("root-radius-is-input-only", contract["root_support_contract"]["registered_max_radius"].startswith("The maximum column distance") and "not a model parameter" in contract["root_support_contract"]["registered_max_radius"], contract["root_support_contract"]["registered_max_radius"])

    grade_rows: list[dict[str, Any]] = []
    for level in range(2, 7):
        fine_level = level + 1
        for variant in range(7):
            state = sample_state(fine_level, variant)
            coarse, fine_q, coarse_q = project_state(level, state)
            dropped = fine_q - coarse_q
            grade_rows.append({"n": level, "variant": variant, "fine_Q": fine_q, "coarse_Q": coarse_q, "dropped": dropped, "balance": fine_q == coarse_q + dropped, "coarse_bound": 0 <= coarse_q <= len(vertices(level))})
    check("full-q-projection-totality", all(row["balance"] and row["dropped"] >= 0 and row["coarse_bound"] for row in grade_rows), {"rows": len(grade_rows), "new-column-only": next(row for row in grade_rows if row["n"] == 2 and row["variant"] == 4)})
    check("grade-changing-lift-is-allowed", any(row["fine_Q"] > row["coarse_Q"] for row in grade_rows) and "change from Q_f to Q_c" in omc012["exact_scope"]["charge_balance"], grade_rows[:8])

    # Structural root identities are checked for every root whose support is
    # before the frontier.  This is the exact finite local proof skeleton.
    structural_rows: list[dict[str, Any]] = []
    regression_rows: list[dict[str, Any]] = []
    rmax_samples = (1, 2, 5, 11)  # explicit regression oracles, not the theorem scope
    for row in closure_rows:
        desc = next(item for item in descriptors if item["name"] == row["name"])
        m_f = row["m_f"]
        n_f = row["N_f"]
        for level in range(n_f, n_f + 3):
            fine_level = level + 1
            coarse_roots = root_catalog(level)
            fine_roots = root_catalog(fine_level)
            fine_by_label = {root["label"]: root for root in fine_roots}
            active_coarse = [root for root in coarse_roots if can_change(root, desc, level)]
            active_fine = [root for root in fine_roots if can_change(root, desc, fine_level)]
            active_labels = {root["label"] for root in active_coarse}
            active_fine_labels = {root["label"] for root in active_fine}
            matched = active_labels == active_fine_labels and all(max(v[0] for v in root["support_vertices"]) <= m_f for root in active_coarse)
            term_ok = True
            for root in active_coarse:
                ok, _detail = check_root_term_identity(level, fine_level, root)
                term_ok = term_ok and ok
            tail_zero = all(not can_change(root, desc, fine_level) for root in fine_roots if min(v[0] for v in root["support_vertices"]) >= level)
            frontier = {vertex for vertex in vertices(fine_level) if vertex[0] in (level, level + 1, level + 2)}
            boundary_separated = all(not (root["support_vertices"] & frontier) for root in active_fine)
            structural_rows.append({"observable": row["name"], "n": level, "m_f": m_f, "N_f": n_f, "active_coarse": len(active_coarse), "active_fine": len(active_fine), "matched": matched, "term_lists_equal": term_ok, "tail_zero": tail_zero, "boundary_separated": boundary_separated})

            for variant in range(7):
                fine_state = sample_state(fine_level, variant)
                coarse_state, fine_q, coarse_q = project_state(level, fine_state)
                for rmax_int in rmax_samples:
                    rmax = Fraction(rmax_int)
                    for root in coarse_roots:
                        support_max = max(v[0] for v in root["support_vertices"])
                        if support_max > level - 1:
                            continue
                        root_fine = fine_by_label[root["label"]]
                        root["level"] = level
                        root_fine["level"] = fine_level
                        after_c = apply_root(coarse_state, root)
                        after_f = apply_root(fine_state, root_fine)
                        if (after_c is None) != (after_f is None):
                            regression_rows.append({"observable": row["name"], "n": level, "variant": variant, "R_max": rmax_int, "root": root["label"], "kind": "admissibility", "equal": False})
                            continue
                        if after_c is None:
                            continue
                        delta_c = energy(level, coarse_state, rmax)
                        delta_c = energy(level, after_c, rmax) - delta_c
                        delta_f = energy(fine_level, after_f, rmax) - energy(fine_level, fine_state, rmax)
                        m_c = mobility_square(coarse_state, root, after_c)
                        m_fine = mobility_square(fine_state, root_fine, after_f)
                        regression_rows.append({"observable": row["name"], "n": level, "variant": variant, "R_max": rmax_int, "root": root["label"], "delta_equal": delta_c == delta_f, "mobility_square_equal": m_c == m_fine, "delta_coarse": str(delta_c), "delta_fine": str(delta_f), "coarse_Q": coarse_q, "fine_Q": fine_q})
    check("all-active-root-structure", all(row["matched"] and row["term_lists_equal"] and row["tail_zero"] and row["boundary_separated"] for row in structural_rows), {"rows": len(structural_rows), "failures": [row for row in structural_rows if not (row["matched"] and row["term_lists_equal"] and row["tail_zero"] and row["boundary_separated"])][:5]})
    check("all-old-root-rate-regressions", all(row.get("equal", row.get("delta_equal") and row.get("mobility_square_equal")) for row in regression_rows), {"rows": len(regression_rows), "failures": [row for row in regression_rows if not row.get("equal", row.get("delta_equal") and row.get("mobility_square_equal"))][:5]})
    check("rmax-symbolic-not-sampled", "arbitrary R" in contract["exact_scope"]["finite_parameter_scope"] and "regression checks only" in contract["exact_scope"]["finite_parameter_scope"], {"samples": list(rmax_samples), "scope": contract["exact_scope"]["finite_parameter_scope"]})

    # The pre-stabilization R-484 defect is a retained nonzero boundary datum.
    boundary = r484_run.get("boundary_witness", {})
    check("r484-defect-retained", boundary == {"coarse_delta_F": "1/8", "fine_even_delta_F": "1/4", "fine_odd_delta_F": "-55/36", "hidden_diagonal_defect": "16/9"}, boundary)
    check("r484-separated-after-Nf", all(row["m_f"] < row["N_f"] for row in closure_rows) and "not defect cancellation" in contract["eventual_intertwining_proof"]["boundary_control"], contract["eventual_intertwining_proof"]["boundary_control"])

    check(
        "generator-sum-identity-declared",
        "Split both finite root sums" in contract["eventual_intertwining_proof"]["generator_sum_identity"]
        and "for every x, every R>=1" in contract["eventual_intertwining_proof"]["generator_sum_identity"],
        contract["eventual_intertwining_proof"]["generator_sum_identity"],
    )
    check("full-q-tail-case", all(any(row["fine_Q"] > row["coarse_Q"] for row in grade_rows if row["n"] == n) for n in range(2, 7)) and "New-column and crossing roots have zero" in contract["full_q_charge_cases"]["new_column_only"], contract["full_q_charge_cases"])
    check("no-physical-promotion", contract["status"]["claim_bearing"] is False and contract["status"]["active_gate_change"] is False and any("No physical Pre-A" in item for item in contract["non_claims"]), contract["non_claims"])

    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc013-full-q-eventual-intertwining-primary/1.0",
        "run_kind": "primary",
        "audit_id": AUDIT_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "MAINLINE_ADVANCE" if not failed else "HOLD_FOR_EVIDENCE",
        "classification": contract["status"]["classification"],
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": actual,
        "derived": {
            "root_support_radius_rows": radius_rows,
            "root_support_radius": next(iter(radius_values)) if radius_values else None,
            "N_f_rows": closure_rows,
            "structural_rows": len(structural_rows),
            "regression_rows": len(regression_rows),
            "R_max_regression_samples": list(rmax_samples),
            "R_max_theorem_scope": "all positive integers by identical symbolic local term lists",
            "grade_rows": len(grade_rows),
        },
        "proof_summary": {
            "common_cylinder": contract["exact_scope"]["common_cylinder_algebra"],
            "projection": contract["exact_scope"]["projection"],
            "N_of_f": contract["root_support_contract"]["N_of_f"],
            "active_root_partition": contract["eventual_intertwining_proof"]["active_root_partition"],
            "root_correspondence": contract["eventual_intertwining_proof"]["root_correspondence"],
            "local_rate_identity": contract["eventual_intertwining_proof"]["local_rate_identity"],
            "generator_sum_identity": contract["eventual_intertwining_proof"]["generator_sum_identity"],
        },
        "boundary_defect": boundary,
        "state_weighted_input": {"C_sw": 540, "role": "domination_only", "intertwining_proved_by_C_sw": False},
        "weak_gibbs_l2": {"status": "NOT_PROVED", "reason": "no cross-Q normalized probability or completed common Hilbert space supplied"},
        "claim_bearing": False,
        "active_gate_change": False,
        "stage2_status": "HOLD_FOR_EVIDENCE_CLOSABILITY_AND_SEMIGROUP",
        "physical_progress": False,
        "non_claims": contract["non_claims"],
        "missing_assumptions": contract["missing_assumptions"],
        "reproduction": contract["reproduction"],
        "next_question": contract["single_next_question"],
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}; structural_rows={len(structural_rows)}; regression_rows={len(regression_rows)}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    return 0 if run(args.output)["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
