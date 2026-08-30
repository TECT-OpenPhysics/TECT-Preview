#!/usr/bin/env python3
"""Independent Fraction-only reconstruction of the HOLD-LC-001 envelope."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "strategy/hold-lc-001-set-valued-delay-envelope-v0.1.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-hold_lc_001_set_valued_delay_envelope/independent.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def run() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        rows.append({"name": name, "group": group, "status": "PASS" if condition else "FAIL", "actual": str(actual), "expected": str(expected)})
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    packet_path = REPO / contract["base_packet"]["path"]
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    check("contract identity", contract["holdout_id"] == "HOLD-LC-001" and contract["task_id"] == "T-061", [contract["holdout_id"], contract["task_id"]], "HOLD-LC-001/T-061", "provenance")
    check("contract status", contract["status"] == "SET_VALUED_FEASIBILITY_ONLY_NOT_SCORED", contract["status"], "SET_VALUED_FEASIBILITY_ONLY_NOT_SCORED", "scope")
    check("contract hash", digest(packet_path) == contract["base_packet"]["sha256"], digest(packet_path), contract["base_packet"]["sha256"], "provenance")
    check("source hash", packet["source"]["sha256"] == contract["base_packet"]["source_sha256"], packet["source"]["sha256"], contract["base_packet"]["source_sha256"], "provenance")

    display = contract["estimand_contract"]["display_envelope"]
    low, high = Fraction(display["lower"]), Fraction(display["upper"])
    check("display interval", low == Fraction("169/100") and high == Fraction("179/100") and low <= high, [low, high], "169/100 <= 179/100", "interval")

    expected: dict[str, tuple[Fraction, Fraction]] = {}
    for item in contract["nuisance_contract"]["scenarios"]:
        sid = str(item["id"])
        ilo, ihi = Fraction(item["lower"]), Fraction(item["upper"])
        expected[sid] = (low - ihi, high - ilo)
        declared = contract["derived_set_valued_rule"]["scenario_envelopes"][sid]
        check(f"scenario {sid}", {"lower": str(expected[sid][0]), "upper": str(expected[sid][1])} == declared, expected[sid], declared, "interval")

    union = (min(value[0] for value in expected.values()), max(value[1] for value in expected.values()))
    declared_union = contract["derived_set_valued_rule"]["union_envelope"]
    check("union", (str(union[0]), str(union[1])) == (declared_union["lower"], declared_union["upper"]), union, declared_union, "interval")
    broad = expected["broad_exotic"]
    check("broad contains simultaneous", broad[0] <= expected["simultaneous"][0] and expected["simultaneous"][1] <= broad[1], broad, expected["simultaneous"], "containment")
    check("broad contains ten second", broad[0] <= expected["ten_second"][0] and expected["ten_second"][1] <= broad[1], broad, expected["ten_second"], "containment")

    admission = contract["admission"]
    check("score firewall", not admission["likelihood_admitted"] and not admission["covariance_admitted"] and not admission["aggregate_scoring_allowed"], admission, "all false", "firewall")
    check("map firewall", set(admission["forward_map_stages"].values()) == {"NOT_ADMITTED"}, admission["forward_map_stages"], "NOT_ADMITTED", "firewall")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "HOLD-LC-001-SET-VALUED-DELAY-ENVELOPE-INDEPENDENT",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "task_id": contract["task_id"],
        "holdout_id": contract["holdout_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {"detector_interval": {"lower": str(low), "upper": str(high)}, "scenario_envelopes": {sid: {"lower": str(value[0]), "upper": str(value[1])} for sid, value in expected.items()}, "union_envelope": {"lower": str(union[0]), "upper": str(union[1])}, "set_valued_feasibility_only": True, "likelihood_admitted": False, "covariance_admitted": False, "aggregate_scoring_allowed": False, "prospective_credit": False},
        "boundary": contract["non_claims"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"contract_sha256": digest(CONTRACT), "base_packet_sha256": digest(packet_path), "source_sha256": packet["source"]["sha256"]},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test: store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT HOLD-LC-001 SET-VALUED ENVELOPE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
