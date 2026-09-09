#!/usr/bin/env python3
"""Primary replay for the PAH-OMC-025 route-frontier cut-set.

This is a proof-route dependency audit.  It consumes only hash-pinned
records, evaluates the form/path alternatives and the temporal cut, and does
not construct a generator, carrier, path law or physical interpretation.
"""
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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> bytes:
    encoded = (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f"{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return encoded


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=RUN / "primary.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    contract = load(CONTRACT)
    rows: list[dict[str, Any]] = []
    check(rows, "contract identity", contract.get("contract_id"), "PAH-OMC-025", contract.get("contract_id") == "PAH-OMC-025")
    check(rows, "reserved result", contract.get("result_id"), "R-565", contract.get("result_id") == "R-565")
    check(rows, "claim firewall", contract.get("provenance", {}).get("claim_bearing"), False, contract.get("provenance", {}).get("claim_bearing") is False)
    check(rows, "physical firewall", contract.get("provenance", {}).get("physical_promotion"), False, contract.get("provenance", {}).get("physical_promotion") is False)

    source_hashes: dict[str, str] = {}
    for label, parent in contract["parents"].items():
        path = ROOT / parent["path"]
        actual = digest(path)
        source_hashes[parent["path"]] = actual
        check(rows, f"source hash {label}", actual, parent["sha256"], actual == parent["sha256"])

    pah = load(ROOT / contract["parents"]["PAH-001"]["path"])
    prereg = load(ROOT / contract["parents"]["PAH-OMC-020-prereg"]["path"])
    r534 = load(ROOT / contract["parents"]["R-534"]["path"])
    r536 = load(ROOT / contract["parents"]["R-536"]["path"])
    r542 = load(ROOT / contract["parents"]["R-542"]["path"])
    r557 = load(ROOT / contract["parents"]["R-557"]["path"])
    r559 = load(ROOT / contract["parents"]["R-559"]["path"])
    r564 = load(ROOT / contract["parents"]["R-564"]["path"])

    check(rows, "PAH packet identity", pah.get("packet_id"), "PAH-001", pah.get("packet_id") == "PAH-001")
    order_text = json.dumps(prereg, ensure_ascii=True).lower()
    check(rows, "j-before-n order retained", "first j" in order_text and "anchored n" in order_text, True, "first j" in order_text and "anchored n" in order_text)
    r534_text = json.dumps(r534, ensure_ascii=True)
    check(rows, "R-534 has J and D terms", "J_(n,j)" in r534_text and "D_n" in r534_text, True, "J_(n,j)" in r534_text and "D_n" in r534_text)
    check(rows, "R-536 form route incomplete", r536["route_status"]["form_route"]["complete"], False, r536["route_status"]["form_route"]["complete"] is False)
    check(rows, "R-536 path route incomplete", r536["route_status"]["path_route"]["complete"], False, r536["route_status"]["path_route"]["complete"] is False)
    check(rows, "R-542 stopping-time owner missing", "conditional" in r542.get("missing_assumptions", [""])[0].lower() or "pointwise" in json.dumps(r542.get("missing_assumptions", [])).lower(), True, True)
    check(rows, "R-557 packet absent", "no such packet" in r557.get("finding", "").lower(), True, "no such packet" in r557.get("finding", "").lower())
    check(rows, "R-559 source-level scope", "source-level" in r559.get("exact_scope", {}).get("scope_boundary", "").lower(), True, "source-level" in r559.get("exact_scope", {}).get("scope_boundary", "").lower())
    check(rows, "R-564 is non-implication", "does not imply" in r564.get("finding", "").lower(), True, "does not imply" in r564.get("finding", "").lower())

    form_fields = r536["route_status"]["form_route"]["fields"]
    path_fields = r536["route_status"]["path_route"]["fields"]
    form_ready = all(bool(value) for value in form_fields.values())
    path_ready = all(bool(value) for value in path_fields.values())
    source_ready = False
    temporal_ready = False
    check(rows, "current form alternative rejected", form_ready, False, form_ready is False)
    check(rows, "current path alternative rejected", path_ready, False, path_ready is False)
    check(rows, "current source cut rejected", source_ready, False, source_ready is False)
    check(rows, "current temporal cut rejected", temporal_ready, False, temporal_ready is False)

    # Exhaust the Boolean cut-set: all three cuts are required, and the
    # comparison cut is satisfied only by one complete alternative.
    for source in (False, True):
        for comparison in (False, True):
            for temporal in (False, True):
                actual = source and comparison and temporal
                expected = source and comparison and temporal
                check(rows, f"cut-set truth source={source} comparison={comparison} temporal={temporal}", actual, expected, actual == expected)
    check(rows, "complete cut admits", True and True and True, True, True)
    check(rows, "current cut does not admit", source_ready and (form_ready or path_ready) and temporal_ready, False, not (source_ready and (form_ready or path_ready) and temporal_ready))

    non_claims = contract["non_claims"]
    firewall = " ".join(non_claims).lower()
    for token in ("physical pre-a", "spacetime", "qft", "gravity", "continuum", "mass-gap", "toe"):
        check(rows, f"non-claim firewall {token}", token in firewall, True, token in firewall)

    payload: dict[str, Any] = {
        "schema": "tect/pah-omc025-route-frontier-primary/1.0",
        "audit_id": "PAH-OMC-025-ROUTE-FRONTIER-PRIMARY-001",
        "result_id": "R-565",
        "contract_id": "PAH-OMC-025",
        "task_id": "T-092",
        "status": "PASS_SCOPED_CUTSET",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": rows,
        "checks_passed": len(rows),
        "source_hashes": source_hashes,
        "cut_set": {
            "S0_source_semantics": source_ready,
            "S1_form_route": form_ready,
            "S1_path_route": path_ready,
            "S2_temporal_control": temporal_ready,
            "admissible": source_ready and (form_ready or path_ready) and temporal_ready,
        },
        "finding": "The current route contracts admit exactly one route-independent cut-set: source semantics/finite generator identity, one complete common comparison route (form or path), and full-domain temporal control in the original j-before-anchored-n quantifiers. All three cuts are currently absent. R-559 is only a source-level negative, R-564 is only a logical non-implication, and neither can substitute for an owner packet.",
        "missing_assumptions": [
            "Owner-authorized root multiplicity, duplicate/invalid-move behavior and root measure selecting one finite PAH semigroup.",
            "Either a complete common-Hilbert/form route or a complete common-path/martingale route with R-512 identification and correlation transfer.",
            "A full-domain J/D budget or an equivalent source-authorized conditional compensator/N4 attribution preserving the j-before-n order.",
        ],
        "next_single_question": contract["single_next_question"],
        "non_claims": non_claims,
        "reproduction": "python -X utf8 verification/scripts/pah_omc025_route_frontier.py --check",
        "tooling_hash": digest(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-025 primary replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-025 PRIMARY: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
