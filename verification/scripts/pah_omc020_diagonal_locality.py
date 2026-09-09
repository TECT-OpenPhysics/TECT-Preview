#!/usr/bin/env python3
"""Exact diagonal obstruction for the R-562 fixed-power locality route."""
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
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC013 = ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json"
R562 = ROOT / "strategy/pa-hyp/PAH-OMC-020-universal-locality-result-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-diagonal-locality-contract-v1.json"
OMC013_CODE = ROOT / "codes/foundations/pah_omc013_full_q_eventual_intertwining.py"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-diagonal-locality/primary.json"
MIN_LEVEL = 2
ROOT_LEVELS = range(2, 10)
PINS = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-013": "e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc",
    "R-562": "4474c3ecabe56ea08c6a9efe44d33cdd7f2cbc79d5ea891a70e89703171698bc",
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


def load_omc013() -> Any:
    spec = importlib.util.spec_from_file_location("pah_omc013_diagonal_radius", OMC013_CODE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen OMC-013 implementation")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def threshold(support_max: int, power: int, radius: int) -> int:
    return max(MIN_LEVEL, support_max + radius * power + 1)


def run(output: Path | None = None) -> dict[str, Any]:
    module = load_omc013()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    r562 = json.loads(R562.read_text(encoding="utf-8"))
    source_hashes = {
        "PAH-001": sha(PAH),
        "PAH-OMC-013": sha(OMC013),
        "R-562": sha(R562),
    }
    rows: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, ok: bool) -> None:
        rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})

    check("source pins", source_hashes, PINS, source_hashes == PINS)
    check("contract identity", contract.get("result_id"), "R-563", contract.get("result_id") == "R-563")
    check("R-562 parent is conditional", r562.get("verdict"), "PASS_CONDITIONAL", r562.get("verdict") == "PASS_CONDITIONAL")
    radius_rows = [{"level": level, "radius": module.root_radius(level)} for level in ROOT_LEVELS]
    radius = max(row["radius"] for row in radius_rows)
    check("source-derived radius two", radius, 2, radius == 2 and all(row["radius"] == 2 for row in radius_rows))

    diagonal_rows = []
    for support_max in (0, 1, 4, 10):
        for n in (2, 3, 5, 11):
            k = n + 1
            n_k = threshold(support_max, k, radius)
            diagonal_rows.append({"support_max": support_max, "n": n, "k": k, "N_k": n_k, "n_below_threshold": n < n_k})
    check("diagonal witness beats every sampled finite n", len(diagonal_rows), 16, len(diagonal_rows) == 16 and all(row["n_below_threshold"] for row in diagonal_rows))
    check("threshold strictly grows along diagonal", all(row["N_k"] > row["n"] for row in diagonal_rows), True, all(row["N_k"] > row["n"] for row in diagonal_rows))
    check("no fixed-n all-power premise in sampled range", all(not all(n >= threshold(s, k, radius) for k in range(0, n + 2)) for s in (0, 1, 4, 10) for n in (2, 3, 5, 11)), True, all(not all(n >= threshold(s, k, radius) for k in range(0, n + 2)) for s in (0, 1, 4, 10) for n in (2, 3, 5, 11)))
    check("route consequence is explicit", "termwise" in contract["route_consequence"] and "uniform" in contract["route_consequence"], True, "termwise" in contract["route_consequence"] and "uniform" in contract["route_consequence"])
    check("nonpromotion firewall", [contract["provenance"][key] for key in ("claim_bearing", "active_gate_change", "physical_promotion")], [False, False, False], [contract["provenance"][key] for key in ("claim_bearing", "active_gate_change", "physical_promotion")] == [False, False, False])
    failed = [row for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/pah-omc020-diagonal-locality-primary/1.0",
        "result_id": "R-563",
        "task_id": "T-086",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "NEGATIVE_RESULT" if not failed else "HOLD_FOR_EVIDENCE",
        "classification": "negative_result",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": source_hashes,
        "radius_rows": radius_rows,
        "diagonal_rows": diagonal_rows,
        "checks": rows,
        "checks_passed": len(rows) - len(failed),
        "checks_failed": len(failed),
        "finding": contract["exact_statement"],
        "route_consequence": contract["route_consequence"],
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
        "code_sha256": sha(Path(__file__)),
    }
    if output is not None:
        atomic_json(output, payload)
    print(f"PAH-OMC-020 DIAGONAL LOCALITY: {payload['verification']} {payload['checks_passed']}/{len(rows)}; verdict={payload['verdict']}")
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = None if args.check else (args.output if args.output.is_absolute() else ROOT / args.output)
    raise SystemExit(0 if run(output)["verification"] == "PASS" else 1)
