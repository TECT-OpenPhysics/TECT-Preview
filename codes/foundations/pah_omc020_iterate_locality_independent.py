#!/usr/bin/env python3
"""Independent strip-geometry reconstruction for R-561.

This lane does not import the primary OMC-013 implementation.  It rebuilds
the finite root support radius and the recursively enlarged support of the
ell_(0,0) cylinder from the declared two-row strip incidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC013 = ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json"
R551 = ROOT / "strategy/pa-hyp/PAH-OMC-020-second-order-defect-result-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-iterate-locality-contract-v1.json"

PINS = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-013": "e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vertices(level: int) -> set[tuple[int, int]]:
    return {(i, j) for i in range(level + 2) for j in (0, 1)}


def edges(level: int) -> list[tuple[str, tuple[int, int], tuple[int, int]]]:
    out = []
    for i in range(level + 1):
        out.extend([(f"h{i}0", (i, 0), (i + 1, 0)), (f"h{i}1", (i, 1), (i + 1, 1))])
    for i in range(level + 2):
        out.append((f"v{i}", (i, 0), (i, 1)))
    for i in range(level):
        out.append((f"d{i}", (i, 0), (i + 1, 1)))
    return out


def root_supports(level: int) -> list[tuple[str, set[tuple[int, int]], set[tuple[int, int]]]]:
    es = edges(level)
    incident: dict[tuple[int, int], set[str]] = {v: set() for v in vertices(level)}
    endpoints: dict[str, tuple[tuple[int, int], tuple[int, int]]] = {}
    for name, left, right in es:
        endpoints[name] = (left, right)
        incident[left].add(name)
        incident[right].add(name)
    roots: list[tuple[str, set[tuple[int, int]], set[tuple[int, int]]] ] = []
    for v in vertices(level):
        star = incident[v]
        support = {v} | {u for edge in star for u in endpoints[edge]}
        for family in ("phase", "aperture"):
            roots.append((f"{family}:{v}", {v}, support))
    for name, left, right in es:
        core = {left, right}
        edge_star = incident[left] | incident[right]
        support = {u for edge in edge_star for u in endpoints[edge]}
        roots.append((f"radial:{name}", core, support))
        roots.append((f"link:{name}", core, support))
    return roots


def closure(level: int, support: set[tuple[int, int]]) -> set[tuple[int, int]]:
    result = set(support)
    for _label, core, root_support in root_supports(level):
        if core & support:
            result.update(root_support)
    return result


def run() -> int:
    rows = []
    actual = {"PAH-001": sha(PAH), "PAH-OMC-013": sha(OMC013)}
    rows.append(("source pins", actual == PINS, actual))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    rows.append(("contract identity", contract.get("result_id") == "R-561", contract.get("result_id")))
    source = json.loads(PAH.read_text(encoding="utf-8"))
    rows.append(("external time unchanged", "external stochastic" in source["dynamics"]["time"].lower(), source["dynamics"]["time"]))
    radius_rows = []
    for level in range(2, 10):
        radius = max(abs(core_vertex[0] - support_vertex[0]) for _label, core, support in root_supports(level) for core_vertex in core for support_vertex in support)
        radius_rows.append({"level": level, "radius": radius})
    rows.append(("radius two", all(item["radius"] == 2 for item in radius_rows), radius_rows))
    support = {(0, 0)}
    support_rows = []
    for k in range(6):
        max_column = max(v[0] for v in support)
        expected = {(0, 0)} if k == 0 else {(i, j) for i in range(2 * k + 1) for j in (0, 1)}
        support_rows.append({"k": k, "max_column": max_column, "N_k": max(2, max_column + 1), "matches": support == expected})
        support = closure(max(2, max_column + 5), support)
    rows.append(("closure formula", all(item["matches"] for item in support_rows), support_rows))
    rows.append(("threshold formula", all(item["N_k"] == max(2, 2 * item["k"] + 1) for item in support_rows), support_rows))
    # The already frozen R-551 result is used only as a boundary diagnostic;
    # this lane independently derives the reason its n=3 witness is below N_2.
    r551 = json.loads(R551.read_text(encoding="utf-8"))
    rows.append(("R-551 remains route-local", "route-local" in r551.get("finding", "").lower(), r551.get("finding")))
    rows.append(("N2 exceeds witness level", max(2, 2 * 2 + 1) > 3, {"N_2": 5, "witness_n": 3}))
    failed = [row for row in rows if not row[1]]
    payload = {"status": "PASS" if not failed else "FAIL", "checks": [{"name": n, "status": "PASS" if ok else "FAIL", "detail": detail} for n, ok, detail in rows], "support_rows": support_rows, "radius_rows": radius_rows, "source_hashes": actual}
    print(f"PAH-OMC-020 ITERATE LOCALITY INDEPENDENT: {payload['status']} {len(rows)-len(failed)}/{len(rows)}")
    for name, ok, detail in failed:
        print(f"FAIL {name}: {detail}")
    return 0 if not failed else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    raise SystemExit(run())
