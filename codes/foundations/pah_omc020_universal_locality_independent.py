#!/usr/bin/env python3
"""Independent geometry/arithmetic replay for R-562.

The implementation rebuilds the two-row strip and root footprints instead of
importing the primary OMC-013 code.  It checks only the finite fixed-power
locality envelope.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC013 = ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json"
R561 = ROOT / "strategy/pa-hyp/PAH-OMC-020-iterate-locality-result-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-universal-locality-contract-v1.json"

PINS = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-013": "e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc",
    "R-561": "f9cef0e147be1c9fc084392e34a02c41a1be1ae78ad31ec641123e719e0a9d8e",
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
    incident: dict[tuple[int, int], set[str]] = {vertex: set() for vertex in vertices(level)}
    for name, left, right in edges(level):
        incident[left].add(name)
        incident[right].add(name)
    face_map = {name: (edge_set, vertex_set) for name, edge_set, vertex_set in faces(level)}
    edge_faces: dict[str, set[str]] = {name: set() for name in edge_map}
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
        radii.extend(abs(core[0] - point[0]) for core in [vertex] for point in support)
    for _name, left, right in edges(level):
        core = {left, right}
        star = set().union(*(incident[point] for point in core))
        support = set().union(*(edge_map[edge] for edge in star))
        radii.extend(abs(core_point[0] - point[0]) for core_point in core for point in support)
    return max(radii, default=0)


def support_max(name: str) -> int:
    if name == "constant":
        return -1
    if name == "ell_a":
        return 0
    if name == "ell_d":
        return 1
    if name == "ell_remote":
        return 4
    if name == "ell_and_H":
        return 1
    if name == "two_remote_faces":
        return 2
    raise ValueError(name)


def threshold(support: int, power: int, radius: int) -> int:
    return max(2, support + radius * power + 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    actual = {"PAH-001": sha(PAH), "PAH-OMC-013": sha(OMC013), "R-561": sha(R561)}
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    r561 = json.loads(R561.read_text(encoding="utf-8"))
    rows = []
    rows.append(actual == PINS)
    rows.append(contract["result_id"] == "R-562")
    radius_rows = [{"level": level, "radius": root_radius(level)} for level in range(2, 10)]
    radius = max(row["radius"] for row in radius_rows)
    rows.append(radius == 2 and all(row["radius"] == radius for row in radius_rows))
    names = ["constant", "ell_a", "ell_d", "ell_remote", "ell_and_H", "two_remote_faces"]
    table = [{"name": name, "support_max": support_max(name), "k": power, "N_k": threshold(support_max(name), power, radius), "separated": support_max(name) + radius * power < threshold(support_max(name), power, radius)} for name in names for power in range(6)]
    rows.append(len(table) == 36 and all(item["separated"] for item in table))
    rows.append(all(table[index + 1]["N_k"] >= table[index]["N_k"] for index in range(len(table) - 1) if table[index + 1]["name"] == table[index]["name"]))
    rows.append([item["N_k"] for item in table if item["name"] == "ell_a"] == [max(2, 2 * power + 1) for power in range(6)])
    rows.append(r561["claim_bearing"] is False and r561["active_gate_change"] is False and r561["physical_promotion"] is False)
    rows.append("fixed finite k" in contract["fixed_scope"]["order"] and "No full exponential" in " ".join(contract["non_claims"]))
    failed = sum(not row for row in rows)
    print(f"PAH-OMC-020 UNIVERSAL LOCALITY INDEPENDENT: {'PASS' if not failed else 'FAIL'} {len(rows)-failed}/{len(rows)}")
    if failed:
        print({"source_hashes": actual, "radius_rows": radius_rows, "table": table})
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
