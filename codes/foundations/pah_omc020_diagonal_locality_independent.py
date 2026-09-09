#!/usr/bin/env python3
"""Independent arithmetic and two-row geometry replay for R-563."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC013 = ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json"
R562 = ROOT / "strategy/pa-hyp/PAH-OMC-020-universal-locality-result-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-diagonal-locality-contract-v1.json"
PINS = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-013": "e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc",
    "R-562": "4474c3ecabe56ea08c6a9efe44d33cdd7f2cbc79d5ea891a70e89703171698bc",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vertices(level: int) -> set[tuple[int, int]]:
    return {(column, row) for column in range(level + 2) for row in (0, 1)}


def edges(level: int) -> list[tuple[str, tuple[int, int], tuple[int, int]]]:
    result = []
    for column in range(level + 1):
        result.extend([(f"h{column}0", (column, 0), (column + 1, 0)), (f"h{column}1", (column, 1), (column + 1, 1))])
    for column in range(level + 2):
        result.append((f"v{column}", (column, 0), (column, 1)))
    for column in range(level):
        result.append((f"d{column}", (column, 0), (column + 1, 1)))
    return result


def faces(level: int) -> list[tuple[str, set[str], set[tuple[int, int]]]]:
    endpoint = {name: {left, right} for name, left, right in edges(level)}
    result = []
    for column in range(level):
        lower = {f"h{column}0", f"v{column + 1}", f"d{column}"}
        upper = {f"d{column}", f"h{column}1", f"v{column}"}
        result.extend([(f"t{column}a", lower, set().union(*(endpoint[e] for e in lower))), (f"t{column}b", upper, set().union(*(endpoint[e] for e in upper)))])
    square = {f"h{level}0", f"v{level + 1}", f"h{level}1", f"v{level}"}
    result.append((f"q{level}", square, set().union(*(endpoint[e] for e in square))))
    return result


def root_radius(level: int) -> int:
    edge_map = {name: {left, right} for name, left, right in edges(level)}
    incident = {vertex: set() for vertex in vertices(level)}
    for name, left, right in edges(level):
        incident[left].add(name)
        incident[right].add(name)
    face_map = {name: (edge_set, vertex_set) for name, edge_set, vertex_set in faces(level)}
    edge_faces = {name: set() for name in edge_map}
    for name, edge_set, _ in faces(level):
        for edge in edge_set:
            edge_faces[edge].add(name)
    radii = []
    for vertex in vertices(level):
        star = incident[vertex]
        support = {vertex} | set().union(*(edge_map[edge] for edge in star))
        for edge in star:
            for face_name in edge_faces[edge]:
                if face_name.startswith("q"):
                    continue
                support |= face_map[face_name][1]
        radii.extend(abs(vertex[0] - point[0]) for point in support)
    for _name, left, right in edges(level):
        core = {left, right}
        star = set().union(*(incident[point] for point in core))
        support = set().union(*(edge_map[edge] for edge in star))
        radii.extend(abs(core_point[0] - point[0]) for core_point in core for point in support)
    return max(radii, default=0)


def threshold(support_max: int, power: int, radius: int) -> int:
    return max(2, support_max + radius * power + 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    actual = {"PAH-001": sha(PAH), "PAH-OMC-013": sha(OMC013), "R-562": sha(R562)}
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    r562 = json.loads(R562.read_text(encoding="utf-8"))
    checks = []
    checks.append(actual == PINS)
    checks.append(contract["result_id"] == "R-563")
    radius_rows = [{"level": level, "radius": root_radius(level)} for level in range(2, 10)]
    radius = max(row["radius"] for row in radius_rows)
    checks.append(radius == 2 and all(row["radius"] == 2 for row in radius_rows))
    diagonal = [{"s": s, "n": n, "k": n + 1, "N_k": threshold(s, n + 1, radius)} for s in (0, 1, 4, 10) for n in (2, 3, 5, 11)]
    checks.append(len(diagonal) == 16 and all(row["n"] < row["N_k"] for row in diagonal))
    checks.append(all(not all(n >= threshold(s, k, radius) for k in range(n + 2)) for s in (0, 1, 4, 10) for n in (2, 3, 5, 11)))
    checks.append("No full" in " ".join(contract["non_claims"]) or "not a no-go" in " ".join(contract["non_claims"]))
    checks.append(r562["claim_bearing"] is False and r562["active_gate_change"] is False and r562["physical_promotion"] is False)
    failed = sum(not check for check in checks)
    print(f"PAH-OMC-020 DIAGONAL LOCALITY INDEPENDENT: {'PASS' if not failed else 'FAIL'} {len(checks)-failed}/{len(checks)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
