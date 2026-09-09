#!/usr/bin/env python3
"""All-finite-cylinder fixed-power locality envelope for PAH-OMC-020.

This is a conditional finite bridge.  It extends the R-561 ell_(0,0)
diagnostic to an arbitrary finite-support cylinder using the frozen OMC-013
root-radius bound.  It does not sum the exponential series or take an n limit.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-universal-locality-contract-v1.json"
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC013 = ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json"
OMC013_CODE = ROOT / "codes/foundations/pah_omc013_full_q_eventual_intertwining.py"
R561 = ROOT / "strategy/pa-hyp/PAH-OMC-020-iterate-locality-result-v1.json"
LEAN = ROOT / "verification/lean/Tect/PahOmc020UniversalLocality.lean"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-universal-locality/primary.json"

PINS = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-013": "e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc",
    "R-561": "f9cef0e147be1c9fc084392e34a02c41a1be1ae78ad31ec641123e719e0a9d8e",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("pah_omc013_universal_locality", OMC013_CODE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen OMC-013 implementation")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})


def support_maximum(module: Any, descriptor: dict[str, Any]) -> int:
    vertices = set(descriptor["ell_support"])
    face_names = set(descriptor["face_support"])
    if face_names:
        level = max(2, max((int(name[1:-1]) for name in face_names), default=0) + 3)
        for face in face_names:
            vertices.update(module.face_vertices(level, face))
    return max((vertex[0] for vertex in vertices), default=-1)


def threshold(support_max: int, power: int, radius: int) -> int:
    return max(2, support_max + radius * power + 1)


def run(output: Path | None = None) -> dict[str, Any]:
    module = load_module()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    pah = json.loads(PAH.read_text(encoding="utf-8"))
    omc013 = json.loads(OMC013.read_text(encoding="utf-8"))
    r561 = json.loads(R561.read_text(encoding="utf-8"))
    source_hashes = {
        "PAH-001": sha(PAH),
        "PAH-OMC-013": sha(OMC013),
        "OMC013-code": sha(OMC013_CODE),
        "R-561": sha(R561),
    }
    rows: list[dict[str, Any]] = []
    source_ok = source_hashes["PAH-001"] == PINS["PAH-001"] and source_hashes["PAH-OMC-013"] == PINS["PAH-OMC-013"] and source_hashes["R-561"] == PINS["R-561"]
    check(rows, "source pins", source_hashes, PINS, source_ok)
    check(rows, "contract identity", contract.get("result_id"), "R-562", contract.get("result_id") == "R-562")
    check(rows, "unchanged PAH generator", pah["packet_id"], "PAH-001", pah["packet_id"] == "PAH-001")
    check(rows, "OMC-013 eventual identity is conditional", omc013["status"]["stage2_status"], "HOLD_FOR_EVIDENCE_CLOSABILITY_AND_SEMIGROUP", omc013["status"]["stage2_status"] == "HOLD_FOR_EVIDENCE_CLOSABILITY_AND_SEMIGROUP")
    radius_rows = [{"level": level, "radius": module.root_radius(level), "root_count": len(module.root_catalog(level))} for level in range(2, 10)]
    radius = max(row["radius"] for row in radius_rows)
    check(rows, "derived radius is two", radius, 2, radius == 2 and all(row["radius"] == radius for row in radius_rows))

    descriptors = [
        module.descriptor("constant"),
        module.descriptor("ell_a", ell_support=((0, 0),)),
        module.descriptor("ell_d", ell_support=((1, 1),)),
        module.descriptor("ell_remote", ell_support=((4, 0),)),
        module.descriptor("ell_and_H", ell_support=((0, 0), (1, 1)), face_support=("t0a", "t0b")),
        module.descriptor("two_remote_faces", face_support=("t1a", "t1b")),
    ]
    support_rows = []
    for descriptor in descriptors:
        s = support_maximum(module, descriptor)
        for power in range(6):
            n_threshold = threshold(s, power, radius)
            envelope_max = s + radius * power
            support_rows.append({
                "name": descriptor["name"],
                "support_max": s,
                "k": power,
                "N_k": n_threshold,
                "envelope_max": envelope_max,
                "strictly_before_frontier": envelope_max < n_threshold,
            })
    check(rows, "all support families have finite maxima", sorted({row["name"] for row in support_rows}), sorted(descriptor["name"] for descriptor in descriptors), all(row["support_max"] >= -1 for row in support_rows))
    check(rows, "all fixed-power envelopes separate", sum(row["strictly_before_frontier"] for row in support_rows), len(support_rows), all(row["strictly_before_frontier"] for row in support_rows))
    check(rows, "threshold is nondecreasing with power", all(threshold(row["support_max"], row["k"] + 1, radius) >= row["N_k"] for row in support_rows if row["k"] < 5), True, all(threshold(row["support_max"], row["k"] + 1, radius) >= row["N_k"] for row in support_rows if row["k"] < 5))
    check(rows, "nonconstant thresholds eventually grow", all(threshold(row["support_max"], row["k"] + 1, radius) > row["N_k"] for row in support_rows if row["k"] < 5 and row["support_max"] >= 0), True, all(threshold(row["support_max"], row["k"] + 1, radius) > row["N_k"] for row in support_rows if row["k"] < 5 and row["support_max"] >= 0))
    ell_rows = [row for row in support_rows if row["name"] == "ell_a"]
    check(rows, "R-561 ell origin is recovered", [row["N_k"] for row in ell_rows], [max(2, 2 * k + 1) for k in range(6)], [row["N_k"] for row in ell_rows] == [max(2, 2 * k + 1) for k in range(6)])
    frontier_rows = []
    for row in support_rows:
        n = row["N_k"]
        frontier_rows.append({"name": row["name"], "k": row["k"], "n": n, "envelope_max": row["envelope_max"], "frontier_columns": [n, n + 1], "separated": row["envelope_max"] < n})
    check(rows, "successor frontier is separated", all(item["separated"] for item in frontier_rows), True, all(item["separated"] for item in frontier_rows))
    check(rows, "R-561 remains non-promoting", [r561["claim_bearing"], r561["active_gate_change"], r561["physical_promotion"]], [False, False, False], [r561["claim_bearing"], r561["active_gate_change"], r561["physical_promotion"]] == [False, False, False])
    check(rows, "contract preserves fixed-k boundary", "fixed finite k" in contract["fixed_scope"]["order"], True, "fixed finite k" in contract["fixed_scope"]["order"])
    firewall = [contract["provenance"]["claim_bearing"], contract["provenance"]["active_gate_change"], contract["provenance"]["physical_promotion"]]
    check(rows, "non-promotion firewall", firewall, [False, False, False], firewall == [False, False, False])
    failed = [row for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/pah-omc020-universal-locality-primary/1.0",
        "result_id": "R-562",
        "task_id": "T-086",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "PASS_CONDITIONAL" if not failed else "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": source_hashes,
        "radius_rows": radius_rows,
        "support_rows": support_rows,
        "frontier_rows": frontier_rows,
        "checks": rows,
        "checks_passed": len(rows) - len(failed),
        "checks_failed": len(failed),
        "finding": contract["conditional_statement"],
        "missing_assumptions": contract["missing_assumptions"],
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
        "code_sha256": sha(Path(__file__)),
    }
    if output is not None:
        atomic_json(output, payload)
    print(f"PAH-OMC-020 UNIVERSAL LOCALITY: {payload['verification']} {payload['checks_passed']}/{len(rows)}; verdict={payload['verdict']}")
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = None if args.check else (args.output if args.output.is_absolute() else ROOT / args.output)
    raise SystemExit(0 if run(output)["verification"] == "PASS" else 1)
