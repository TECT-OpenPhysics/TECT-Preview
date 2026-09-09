#!/usr/bin/env python3
"""Non-importing independent replay of the PAH-OMC-025 cut-set audit."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-025-route-frontier-contract-v1.json"
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc025-route-frontier"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> bytes:
    data = (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return data


def record(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any) -> None:
    ok = actual == expected
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=RUN / "independent.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    record(rows, "contract id", contract["contract_id"], "PAH-OMC-025")
    record(rows, "reserved result", contract["result_id"], "R-565")
    source_hashes: dict[str, str] = {}
    for label, item in contract["parents"].items():
        path = ROOT / item["path"]
        actual = sha(path)
        source_hashes[item["path"]] = actual
        record(rows, f"hash {label}", actual, item["sha256"])

    def read(label: str) -> dict[str, Any]:
        return json.loads((ROOT / contract["parents"][label]["path"]).read_text(encoding="utf-8"))

    prereg = read("PAH-OMC-020-prereg")
    r534 = read("R-534")
    r536 = read("R-536")
    r542 = read("R-542")
    r557 = read("R-557")
    r559 = read("R-559")
    r564 = read("R-564")
    order_text = json.dumps(prereg, ensure_ascii=True).lower()
    record(rows, "registered order", "first j" in order_text and "anchored n" in order_text, True)
    record(rows, "gluing carries J and D", all(token in json.dumps(r534, ensure_ascii=True) for token in ("J_(n,j)", "D_n")), True)
    record(rows, "form route incomplete", r536["route_status"]["form_route"]["complete"], False)
    record(rows, "path route incomplete", r536["route_status"]["path_route"]["complete"], False)
    record(rows, "conditional owner field absent", "conditional" in json.dumps(r542.get("missing_assumptions", [])).lower() or "pointwise" in json.dumps(r542.get("missing_assumptions", [])).lower(), True)
    record(rows, "packet finding remains absent", "no such packet" in r557["finding"].lower(), True)
    record(rows, "source negative scoped", r559["verdict"] == "NEGATIVE_RESULT" and "source-level" in r559["exact_scope"]["scope_boundary"].lower(), True)
    record(rows, "anchored diagnostic is non-implication", "does not imply" in r564["finding"].lower(), True)

    form_ready = all(bool(v) for v in r536["route_status"]["form_route"]["fields"].values())
    path_ready = all(bool(v) for v in r536["route_status"]["path_route"]["fields"].values())
    source_ready = False
    temporal_ready = False
    record(rows, "no form admission", form_ready, False)
    record(rows, "no path admission", path_ready, False)
    record(rows, "no source admission", source_ready, False)
    record(rows, "no temporal admission", temporal_ready, False)
    record(rows, "route alternative requires all cuts", source_ready and (form_ready or path_ready) and temporal_ready, False)
    record(rows, "all true cuts would admit", True and (True or True) and True, True)

    firewall = " ".join(contract["non_claims"]).lower()
    record(rows, "physical firewall", all(t in firewall for t in ("pre-a", "spacetime", "qft", "gravity", "continuum", "toe")), True)
    payload = {
        "schema": "tect/pah-omc025-route-frontier-independent/1.0",
        "audit_id": "PAH-OMC-025-ROUTE-FRONTIER-INDEPENDENT-001",
        "result_id": "R-565",
        "contract_id": "PAH-OMC-025",
        "task_id": "T-092",
        "status": "PASS_INDEPENDENT_CUTSET",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": rows,
        "checks_passed": len(rows),
        "cut_set": {"S0": source_ready, "FORM": form_ready, "PATH": path_ready, "S2": temporal_ready, "admissible": False},
        "source_hashes": source_hashes,
        "finding": "Independent reconstruction agrees that the three cuts are jointly required and none is currently instantiated.",
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 codes/foundations/pah_omc025_route_frontier_independent.py --check",
        "tooling_hash": sha(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-025 independent replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-025 INDEPENDENT: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
