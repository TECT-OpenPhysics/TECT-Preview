#!/usr/bin/env python3
"""Derive a conservative n-uniform PH/LK/AP root-overlap bound.

The footprint is reconstructed directly from the immutable OMC-004 strip:
PH roots see incident matter edges, LK roots see their edge and incident
faces, and AP roots see incident edges and all faces touching them.  This is a
dependency footprint for a locality estimate, not a new carrier or a changed
generator.  The resulting overlap bound is an input to R-515; it is not the
connected-word-to-Duhamel theorem needed for N2c/N4.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from collections import defaultdict
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-overlap/primary.json"
)

PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC001 = ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json"
OMC004 = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
OMC018 = ROOT / "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md"
OMC020 = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
OMC020_WORK = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-work.md"

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-001-v1.json":
        "948a87092f7393e5214a375d66295237e5c8be1b018b8788d3e6785d696e774f",
    "strategy/pa-hyp/PAH-OMC-004-v1.json":
        "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md":
        "18dc782cafff8cf8a516fd8366ec7e1f8727a24c9553dba0656a6b4bc84de264",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def check(rows: list[dict], name: str, condition: bool, actual: object, expected: object) -> None:
    if not condition:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def strip_geometry(n: int) -> tuple[list[tuple[int, int]], list[tuple], dict, list[tuple]]:
    vertices = [(i, j) for i in range(n + 2) for j in (0, 1)]
    edges: list[tuple] = []
    for i in range(n + 1):
        for j in (0, 1):
            edges.append(("h", i, j))
    for i in range(n + 2):
        edges.append(("v", i))
    for i in range(n):
        edges.append(("d", i))
    endpoints: dict[tuple, tuple[tuple[int, int], tuple[int, int]]] = {}
    for edge in edges:
        if edge[0] == "h":
            endpoints[edge] = ((edge[1], edge[2]), (edge[1] + 1, edge[2]))
        elif edge[0] == "v":
            endpoints[edge] = ((edge[1], 0), (edge[1], 1))
        else:
            endpoints[edge] = ((edge[1], 0), (edge[1] + 1, 1))
    faces: list[tuple] = []
    for i in range(n):
        faces.append(("t", i, 0, [("h", i, 0), ("v", i + 1), ("d", i)]))
        faces.append(("t", i, 1, [("d", i), ("h", i, 1), ("v", i)]))
    faces.append(("q", n, [("h", n, 0), ("v", n + 1), ("h", n, 1), ("v", n)]))
    return vertices, edges, endpoints, faces


def root_footprints(n: int) -> list[dict]:
    vertices, edges, endpoints, faces = strip_geometry(n)
    incident_edges: dict[tuple[int, int], list[tuple]] = defaultdict(list)
    for edge, ends in endpoints.items():
        for vertex in ends:
            incident_edges[vertex].append(edge)
    edge_faces: dict[tuple, list[tuple]] = defaultdict(list)
    for face in faces:
        for edge in face[-1]:
            edge_faces[edge].append(face)

    def footprint(kind: str, obj: tuple) -> tuple[frozenset, frozenset]:
        support_edges: set[tuple] = set()
        support_vertices: set[tuple[int, int]] = set()
        if kind in {"PH", "AP"}:
            support_vertices.add(obj)
            support_edges.update(incident_edges[obj])
            if kind == "AP":
                for edge in list(support_edges):
                    for face in edge_faces[edge]:
                        support_edges.update(face[-1])
        else:
            support_edges.add(obj)
            for face in edge_faces[obj]:
                support_edges.update(face[-1])
        for edge in support_edges:
            support_vertices.update(endpoints[edge])
        return frozenset(support_vertices), frozenset(support_edges)

    roots: list[dict] = []
    for vertex in vertices:
        for sigma in (-1, 1):
            verts, links = footprint("PH", vertex)
            roots.append({"kind": "PH", "base": vertex[0], "sigma": sigma,
                          "vertices": verts, "edges": links})
        for sigma in (-1, 1):
            verts, links = footprint("AP", vertex)
            roots.append({"kind": "AP", "base": vertex[0], "sigma": sigma,
                          "vertices": verts, "edges": links})
    for edge in edges:
        for sigma in (-1, 1):
            verts, links = footprint("LK", edge)
            roots.append({"kind": "LK", "base": edge[1], "sigma": sigma,
                          "vertices": verts, "edges": links})
    for root in roots:
        columns = {vertex[0] for vertex in root["vertices"]}
        for edge in root["edges"]:
            columns.update(endpoints[edge][0][0] for _ in (0,))
            columns.update(endpoints[edge][1][0] for _ in (0,))
        root["columns"] = frozenset(columns)
    return roots


def overlaps(left: dict, right: dict) -> bool:
    return bool(left["vertices"] & right["vertices"] or left["edges"] & right["edges"])


def analyse(n: int) -> dict:
    vertices, edges, endpoints, _ = strip_geometry(n)
    roots = root_footprints(n)
    by_base: dict[int, int] = defaultdict(int)
    for root in roots:
        by_base[root["base"]] += 1
    max_base = max(by_base.values())
    max_radius = max(max(abs(column - root["base"]) for column in root["columns"])
                     for root in roots)
    max_overlap = max(sum(overlaps(root, other) for other in roots) for root in roots)
    max_edges_per_base = max(sum(1 for edge in edges if edge[1] == column)
                             for column in range(n + 2))
    expected_roots = 2 * (2 * len(vertices) + len(edges))
    return {
        "n": n,
        "vertices": len(vertices),
        "edges": len(edges),
        "roots": len(roots),
        "expected_roots": expected_roots,
        "max_roots_per_base_column": max_base,
        "max_edges_per_base_column": max_edges_per_base,
        "max_footprint_radius": max_radius,
        "max_overlap_degree_including_self": max_overlap,
    }


def tail_bound(a: int, b: int, time: Fraction, distance: int) -> Fraction:
    ratio = Fraction(b) * time / (distance + 1)
    if ratio >= 1:
        raise ValueError("ratio condition")
    first = Fraction(a * b ** (distance - 1)) * time ** distance / math.factorial(distance)
    return first / (1 - ratio)


def compute() -> dict:
    rows: list[dict] = []
    for relative, expected in PINS.items():
        path = ROOT / relative
        check(rows, "source:" + relative, path.is_file() and digest(path) == expected,
              digest(path) if path.is_file() else "MISSING", expected)
        if path.is_file() and path.suffix in {".json", ".md"}:
            check(rows, "LF:" + relative, b"\r" not in path.read_bytes(), True, "LF-only")

    pah = json.loads(PAH.read_text(encoding="utf-8"))
    omc1 = json.loads(OMC001.read_text(encoding="utf-8"))
    omc4 = json.loads(OMC004.read_text(encoding="utf-8"))
    prereg = json.loads(OMC020.read_text(encoding="utf-8"))
    labels = omc1["universal_directed_root_labels"]
    check(rows, "source PH/LK/AP labels present",
          set(labels) >= {"phase", "link", "aperture"}, list(labels), "phase/link/aperture")
    check(rows, "source midpoint generator retained",
          "exp[-beta(F_rho(r x)-F_rho(x))/2]" in pah["dynamics"]["generator"],
          pah["dynamics"]["generator"], "original midpoint rate")
    check(rows, "source degree bound", omc4["exact_scope"]["strip_family"]["degree_bound"] == 5,
          omc4["exact_scope"]["strip_family"]["degree_bound"], 5)
    check(rows, "source N2c work contract retained", "N2c" in OMC020_WORK.read_text(encoding="utf-8"),
          True, "N2c present")
    check(rows, "source N2c proof obligation retained", "anchored n temporal limit" in prereg["proof_obligations"][3],
          prereg["proof_obligations"][3], "anchored n temporal limit")

    ns = [2, 3, 4, 6, 10, 20]
    analyses = [analyse(n) for n in ns]
    for item in analyses:
        check(rows, f"root count n={item['n']}", item["roots"] == item["expected_roots"],
              item["roots"], item["expected_roots"])
        check(rows, f"base-column edge slots n={item['n']}", item["max_edges_per_base_column"] <= 4,
              item["max_edges_per_base_column"], "<=4")
        check(rows, f"base-column root count n={item['n']}", item["max_roots_per_base_column"] <= 16,
              item["max_roots_per_base_column"], "<=16")
        check(rows, f"footprint radius n={item['n']}", item["max_footprint_radius"] <= 2,
              item["max_footprint_radius"], "<=2")

    base_root_bound = 2 * (2 + 2) + 4 * 2
    radius_bound = 2
    overlap_bound = base_root_bound * (4 * radius_bound + 1)
    check(rows, "derived roots per base column", base_root_bound == 16, base_root_bound, 16)
    check(rows, "derived overlap branching bound", overlap_bound == 144, overlap_bound, 144)
    check(rows, "enumerated overlap fits derived bound",
          max(item["max_overlap_degree_including_self"] for item in analyses) <= overlap_bound,
          max(item["max_overlap_degree_including_self"] for item in analyses), f"<={overlap_bound}")

    support_columns = 2
    first_root_bound = base_root_bound * (support_columns + 2 * radius_bound + 1)
    check(rows, "derived fixed-support first-root bound", first_root_bound == 112,
          first_root_bound, 112)
    distances = [600, 800, 1000]
    time = Fraction(1)
    tails = [tail_bound(first_root_bound, overlap_bound, time, distance) for distance in distances]
    for index in range(len(tails) - 1):
        check(rows, f"connected tail decreases {distances[index]}->{distances[index+1]}",
              tails[index] > tails[index + 1], str(tails[index + 1]), f"< {tails[index]}")

    return {
        "schema": "tect/pah-omc020-overlap-primary/1.0",
        "status": "PASS_ROOT_OVERLAP_BOUND",
        "verdict": "AUXILIARY_SUPPORT",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": PINS,
        "checks": rows,
        "geometry_reconstruction": {
            "n_values": ns,
            "root_families": "PH(v, +/-), AP(v, +/-), LK(q, +/-) exactly; radial TR omitted only because this is the R-511 j-limit non-radial generator.",
            "footprint_definition": "PH incident edges; LK edge plus incident face edges; AP incident edges plus all incident face edges, with all endpoint vertices retained.",
            "analyses": analyses,
        },
        "derived_constants": {
            "roots_per_base_column": base_root_bound,
            "footprint_radius_columns": radius_bound,
            "overlap_branching_bound": overlap_bound,
            "first_root_bound_for_support_columns_2": first_root_bound,
            "connected_tail": {
                "a": first_root_bound,
                "b": overlap_bound,
                "time": str(time),
                "distances": distances,
                "bounds": [str(value) for value in tails],
            },
        },
        "n2c_status": {
            "overlap_bound": "PASS for the declared dependency footprint",
            "connected_word_count": "PASS conditionally from the footprint bound",
            "word_to_duhamel_attribution": "NOT_PROVED",
            "boundary_escape": "NOT_DISCHARGED",
        },
        "scope": "Combinatorial dependency-footprint and overlap bound for exact OMC-004 finite strips after the R-511 j-limit; no semigroup limit theorem.",
        "next_single_question": "Can a source-valid coupling or Duhamel construction identify the exact A_n^(out,m)Q_n(s)g term with the connected-word event controlled by b=144?",
        "non_claims": [
            "No N2c/N4 boundary-escape theorem, anchored-n convergence, common U_n or R-512 minimal-form selection.",
            "No infinite-volume, continuum, physical Pre-A, spacetime, QFT, gravity, Yang-Mills, mass-gap or TOE conclusion.",
            "The footprint is a proof dependency set, not a new interaction or carrier."
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and args.output.exists():
        if args.output.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 root-overlap replay mismatch")
    elif not args.check:
        atomic_json(args.output, payload)
    print(f"PAH-OMC-020 ROOT OVERLAP: PASS ({len(payload['checks'])} checks; b=144; Duhamel attribution open)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
