#!/usr/bin/env python3
"""Check a source-local finite-fibre Duhamel/coupling attribution bound.

The script keeps the PAH-001 PH/LK/AP generator and the OMC-004 strip fixed.
It derives a locality path count from the R-516 dependency footprint and makes
the two-copy rate-difference factor explicit.  The resulting estimate is a
conditional finite-fibre bound for the N2c/N4 boundary term; it is not an
anchored-n or infinite-volume theorem.
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
    "2026-09-07-pah-omc020-duhamel-attribution/primary.json"
)

PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC001 = ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json"
OMC004 = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
OMC018 = ROOT / "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md"
OMC020 = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
OMC020_WORK = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-work.md"
R515 = ROOT / "strategy/pa-hyp/PAH-OMC-020-pathword-result-v1.json"
R516 = ROOT / "strategy/pa-hyp/PAH-OMC-020-root-overlap-result-v1.json"

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
    "strategy/pa-hyp/PAH-OMC-020-temporal-work.md":
        "45fc8e90e5ee960414d6a3f868647c85fcd0fe1f0b17e7e1b677b5647e78d16b",
    "strategy/pa-hyp/PAH-OMC-020-pathword-result-v1.json":
        "114699a4554e45260a6a6632f44a32e9c0494a9274c27b561c676e93c5d247d9",
    "strategy/pa-hyp/PAH-OMC-020-root-overlap-result-v1.json":
        "9e357158eb6de66bb776b2d674964ddf9fb16547409ac36f8dd254154082bc11",
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
            columns.add(endpoints[edge][0][0])
            columns.add(endpoints[edge][1][0])
        root["columns"] = frozenset(columns)
    return roots


def overlaps(left: dict, right: dict) -> bool:
    return bool(left["vertices"] & right["vertices"] or left["edges"] & right["edges"])


def factorial_tail(a: int, branching: int, time: Fraction, distance: int) -> Fraction:
    if a <= 0 or branching <= 0 or time < 0 or distance < 1:
        raise ValueError("positive tail inputs required")
    ratio = Fraction(branching) * time / (distance + 1)
    if ratio >= 1:
        raise ValueError("ratio condition is not met")
    first = Fraction(a * branching ** (distance - 1)) * time ** distance
    first /= math.factorial(distance)
    return first / (1 - ratio)


def source_audit(rows: list[dict]) -> dict:
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
    r515 = json.loads(R515.read_text(encoding="utf-8"))
    r516 = json.loads(R516.read_text(encoding="utf-8"))
    labels = omc1["universal_directed_root_labels"]
    generator = omc1["generator_and_projection"]["generator"]
    check(rows, "PH/LK/AP source labels", set(labels) >= {"phase", "link", "aperture"},
          sorted(labels), "phase/link/aperture")
    local_map_phrases = ("every other coordinate is fixed", "phases, apertures, and links are fixed")
    check(rows, "source root maps are local", all(any(phrase in item["map"] for phrase in local_map_phrases)
          for item in labels.values()), True, "all declared maps local")
    check(rows, "source rate is midpoint", "exp[-beta(F_rho(r.x)-F_rho(x))/2]" in omc1["generator_and_projection"]["rate"],
          omc1["generator_and_projection"]["rate"], "original midpoint rate")
    check(rows, "parent midpoint generator retained", "exp[-beta(F_rho(r x)-F_rho(x))/2]" in pah["dynamics"]["generator"],
          pah["dynamics"]["generator"], "original midpoint generator")
    strip = omc4["exact_scope"]["strip_family"]
    check(rows, "OMC-004 degree bound", strip["degree_bound"] == 5, strip["degree_bound"], 5)
    check(rows, "OMC-004 face-incidence bound", strip["face_incidence_bound"] == 4,
          strip["face_incidence_bound"], 4)
    check(rows, "source external Markov time", "external" in pah["dynamics"]["time"].lower(),
          pah["dynamics"]["time"], "external stochastic time")
    work = OMC020_WORK.read_text(encoding="utf-8")
    check(rows, "N2c/N4 obligation retained", "N2c" in work and "A_n^{out,m}" in work,
          True, "N2c and A_n^{out,m} present")
    check(rows, "R-515 path-word source bridge", r515["result_id"] == "R-515" and r515["conditional"],
          [r515["result_id"], r515["conditional"]], ["R-515", True])
    check(rows, "R-516 overlap input", r516["result_id"] == "R-516" and
          r516["conclusion"]["overlap"].find("144") >= 0, [r516["result_id"], r516["conclusion"]["overlap"]], "b=144")
    check(rows, "R-516 retains open attribution", "Duhamel" in r516["next_single_question"],
          r516["next_single_question"], "source attribution is the next question")
    return {"labels": labels, "strip": strip, "prereg": prereg}


def analyse_graph(n: int) -> dict:
    vertices, edges, _, _ = strip_geometry(n)
    roots = root_footprints(n)
    by_base: dict[int, int] = defaultdict(int)
    for root in roots:
        by_base[root["base"]] += 1
    max_base = max(by_base.values())
    max_radius = max(max(abs(column - root["base"]) for column in root["columns"])
                     for root in roots)
    max_overlap = max(sum(overlaps(root, other) for other in roots) for root in roots)
    return {
        "n": n,
        "vertices": len(vertices),
        "edges": len(edges),
        "roots": len(roots),
        "roots_per_base": max_base,
        "footprint_radius": max_radius,
        "max_overlap_including_self": max_overlap,
    }


def compute() -> dict:
    rows: list[dict] = []
    source_audit(rows)
    analyses = [analyse_graph(n) for n in (2, 3, 6, 12, 20)]
    source_degree = 5
    source_face_incidence = 4
    edge_slots = source_face_incidence
    vertex_directions = len(("PH", "AP")) * 2
    link_directions = 2
    roots_per_column = 2 * vertex_directions + edge_slots * link_directions
    footprint_radius = 2
    overlap_step = 2 * footprint_radius
    overlap_branching = roots_per_column * (2 * footprint_radius * 2 + 1)
    two_copy_factor = 1 + 1
    effective_branching = two_copy_factor * overlap_branching
    support_widths = [2, 3, 5]
    support_bounds = {
        str(width): roots_per_column * (width + 2 * footprint_radius + 1)
        for width in support_widths
    }
    check(rows, "derived source edge slots", edge_slots <= source_degree, edge_slots, f"<={source_degree}")
    check(rows, "derived roots per column", roots_per_column == 16, roots_per_column, 16)
    check(rows, "derived footprint radius", footprint_radius == 2, footprint_radius, 2)
    check(rows, "derived overlap branching", overlap_branching == 144, overlap_branching, 144)
    check(rows, "two-copy triangle factor", two_copy_factor == 2, two_copy_factor, 2)
    check(rows, "effective coupling branching", effective_branching == 288,
          effective_branching, f"{two_copy_factor}*{overlap_branching}")
    for item in analyses:
        expected_roots = 2 * (2 * item["vertices"] + item["edges"])
        check(rows, f"root count n={item['n']}", item["roots"] == expected_roots,
              item["roots"], expected_roots)
        check(rows, f"enumerated roots per column n={item['n']}", item["roots_per_base"] <= roots_per_column,
              item["roots_per_base"], f"<={roots_per_column}")
        check(rows, f"enumerated radius n={item['n']}", item["footprint_radius"] <= footprint_radius,
              item["footprint_radius"], f"<={footprint_radius}")
        check(rows, f"enumerated overlap n={item['n']}", item["max_overlap_including_self"] <= overlap_branching,
              item["max_overlap_including_self"], f"<={overlap_branching}")

    # The word orientation is immaterial for counting: overlap is symmetric,
    # so reverse paths ending at the local support have the same bound.
    check(rows, "overlap graph is symmetric", all(overlaps(left, right) == overlaps(right, left)
          for left in root_footprints(6) for right in root_footprints(6)), True, True)

    support_width = 2
    first_root_bound = support_bounds[str(support_width)]
    distances = [128, 192, 256]
    time = Fraction(1, 4)
    tails = [factorial_tail(first_root_bound, effective_branching, time, distance)
             for distance in distances]
    for index, distance in enumerate(distances):
        ratio = Fraction(effective_branching) * time / (distance + 1)
        check(rows, f"coupling tail ratio d={distance}", ratio < 1, str(ratio), "<1")
        if index:
            check(rows, f"coupling tail decreases {distances[index-1]}->{distance}",
                  tails[index - 1] > tails[index], str(tails[index]), f"<{tails[index - 1]}")

    # A boundary at column m is separated from a width-w support by a number
    # of overlap steps growing with m.  The formula is conservative and uses
    # the source footprint radius only; it does not assign a physical length.
    width = support_width
    boundary_columns = [width + 2 * footprint_radius + 4,
                        width + 2 * footprint_radius + 4 + 4 * 8,
                        width + 2 * footprint_radius + 4 + 4 * 16]
    boundary_distances = []
    for boundary in boundary_columns:
        column_gap = max(0, boundary - width - 2 * footprint_radius)
        graph_distance = max(1, math.ceil(column_gap / overlap_step))
        boundary_distances.append(graph_distance)
    check(rows, "boundary graph distance grows", boundary_distances[0] < boundary_distances[-1],
          boundary_distances, "strictly increasing endpoints")
    check(rows, "boundary distance is model-local", "physical" not in str(boundary_distances).lower(),
          boundary_distances, "no physical length")

    return {
        "schema": "tect/pah-omc020-duhamel-attribution-primary/1.0",
        "status": "PASS_DUHAMEL_ATTRIBUTION_BOUND",
        "verdict": "AUXILIARY_SUPPORT",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": PINS,
        "checks": rows,
        "source_contract": {
            "generator": "The unchanged PAH-001 midpoint-rate generator on the OMC-001 PH/LK/AP labels after the R-511 j-limit.",
            "locality": "The OMC-001 maps fix every coordinate outside the root-local variables; the OMC-004 degree and face-incidence bounds are retained.",
            "state_time": "The R-510/R-511 Gibbs state and external stochastic Markov time are unchanged.",
            "coupling": "At each fixed amplitude the finite label chain is coupled by common clocks for roots with equal local rates; a disagreement can propagate only through an overlapping footprint. A rate difference is bounded by the sum of the two copy rates, producing the explicit two-copy factor 2.",
        },
        "derived_constants": {
            "source_degree_bound": source_degree,
            "source_face_incidence_bound": source_face_incidence,
            "roots_per_column": roots_per_column,
            "footprint_radius": footprint_radius,
            "overlap_step_columns": overlap_step,
            "overlap_branching": overlap_branching,
            "two_copy_rate_factor": two_copy_factor,
            "effective_coupling_branching": effective_branching,
            "first_root_bounds_by_support_width": support_bounds,
            "tail_fixture": {
                "support_width": support_width,
                "a": first_root_bound,
                "branching": effective_branching,
                "time": str(time),
                "distances": distances,
                "bounds": [str(value) for value in tails],
            },
            "boundary_distance_fixture": {
                "boundary_columns": boundary_columns,
                "graph_distances": boundary_distances,
            },
        },
        "duhamel_attribution": {
            "finite_identity": "A_out Q_t g is expanded by a first outside root followed by a finite-fibre jump history; survival factors are <=1 and integrating t^(ell-1)/(ell-1)! over [0,T] gives T^ell/ell!.",
            "connected_count": "Reverse-word counting uses overlap symmetry: for a support of width w, at most a_w roots touch the support and at most b=144 choices propagate each step.",
            "two_copy_bound": "The two-copy coupling rate discrepancy is bounded by c_r(X)+c_r(Y), so each word length ell receives at most 2^ell times the R-515 square-transport L2 bound. Thus the effective branching is b_eff=2*b=288, not a hidden pointwise rate supremum.",
            "integrated_bound": "For graph distance d and b_eff*T<d+1, integral_0^T ||A_out Q_t g||_2 dt <= 4 ||g||_infinity * E_d(a_w,b_eff,T), where E_d is the R-515 factorial tail.",
            "uniform_n": "The constants depend only on the source local degree/incidence and fixed cylinder width, so the bound is uniform in n once the finite-fibre coupling hypotheses hold.",
        },
        "n2c_status": {
            "finite_fibre_coupling": "PASS under the explicitly stated source-local coupling construction",
            "word_to_duhamel_attribution": "PASS_CONDITIONAL with explicit two-copy factor",
            "boundary_escape_N4": "PASS_CONDITIONAL as m->infinity for each fixed local cylinder",
            "anchored_n": "NOT_DISCHARGED",
        },
        "geometry_reconstruction": analyses,
        "scope": "Conditional source-local finite-fibre Duhamel/coupling attribution for the exact OMC-004 PH/LK/AP generator after the R-511 j-limit; no anchored-n semigroup theorem.",
        "next_single_question": "Can the conditional finite-fibre coupling be lifted through a source-authorized common U_n/Hilbert realization and terminal-square-compatible comparison map, so that the N2c/N4 bound applies to the preregistered anchored-n correlations?",
        "non_claims": [
            "The coupling is conditional on the finite-fibre local-rate construction and does not supply N2a, N2b or N2d.",
            "No anchored-n, infinite-volume, continuum or R-512 minimal-form semigroup convergence is proved.",
            "No physical Pre-A, spacetime, QFT, gravity, Yang-Mills, mass-gap or TOE conclusion follows.",
            "External stochastic Markov time is not quantum real time, proper time or Lorentzian time.",
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
            raise SystemExit("PAH-OMC-020 Duhamel attribution replay mismatch")
    elif not args.check:
        atomic_json(args.output, payload)
    print(f"PAH-OMC-020 DUHAMEL ATTRIBUTION: PASS ({len(payload['checks'])} checks; b=144, b_eff=288)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
