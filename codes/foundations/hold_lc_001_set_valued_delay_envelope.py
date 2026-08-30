#!/usr/bin/env python3
"""Primary exact set-valued feasibility envelope for HOLD-LC-001.

This is an additive T-059 interface.  It deliberately does not turn the
reported timing summary into a likelihood, covariance, speed observation, or
candidate score.
"""

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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-hold_lc_001_set_valued_delay_envelope/primary.json"


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def frac(value: str) -> Fraction:
    return Fraction(value)


def interval_difference(dlo: Fraction, dhi: Fraction, ilo: Fraction, ihi: Fraction) -> tuple[Fraction, Fraction]:
    if dlo > dhi or ilo > ihi:
        raise ValueError("invalid interval")
    return dlo - ihi, dhi - ilo


def run() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        checks.append({"name": name, "group": group, "status": "PASS" if condition else "FAIL", "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    base = REPO / contract["base_packet"]["path"]
    check("identity", contract["id"] == "HOLD-LC-001-SET-VALUED-DELAY-ENVELOPE-v0.1" and contract["holdout_id"] == "HOLD-LC-001" and contract["task_id"] == "T-061", [contract["id"], contract["holdout_id"], contract["task_id"]], "HOLD-LC-001/T-061", "provenance")
    check("claim nonbearing", contract["claim_bearing"] is False, contract["claim_bearing"], False, "scope")
    check("methods unchanged", contract["methods_unchanged"] is True, contract["methods_unchanged"], True, "method firewall")
    check("base packet exists", base.is_file(), base, True, "provenance")
    check("base packet hash", normalized_sha256(base) == contract["base_packet"]["sha256"], normalized_sha256(base), contract["base_packet"]["sha256"], "provenance")
    source = json.loads(base.read_text(encoding="utf-8"))
    check("source hash", source["source"]["sha256"] == contract["base_packet"]["source_sha256"], source["source"]["sha256"], contract["base_packet"]["source_sha256"], "provenance")
    check("source holdout", source["holdout_id"] == contract["holdout_id"], source["holdout_id"], contract["holdout_id"], "provenance")

    display = contract["estimand_contract"]["display_envelope"]
    dlo, dhi = frac(display["lower"]), frac(display["upper"])
    center, half = frac(contract["estimand_contract"]["reported_value"]), frac(contract["estimand_contract"]["reported_display_half_width"])
    check("display arithmetic", dlo == center - half and dhi == center + half, [dlo, dhi], [center - half, center + half], "interval")
    check("display ordered", dlo <= dhi, [dlo, dhi], "ordered", "interval")

    expected_scenarios: dict[str, tuple[Fraction, Fraction]] = {}
    for scenario in contract["nuisance_contract"]["scenarios"]:
        sid = str(scenario["id"])
        ilo, ihi = frac(scenario["lower"]), frac(scenario["upper"])
        check(f"nuisance ordered {sid}", ilo <= ihi, [ilo, ihi], "ordered", "nuisance")
        expected_scenarios[sid] = interval_difference(dlo, dhi, ilo, ihi)

    declared = contract["derived_set_valued_rule"]["scenario_envelopes"]
    derived: dict[str, dict[str, str]] = {}
    for sid, (lower, upper) in expected_scenarios.items():
        actual = {"lower": str(lower), "upper": str(upper)}
        check(f"scenario envelope {sid}", actual == declared[sid], actual, declared[sid], "interval")
        derived[sid] = actual

    union_lower = min(lower for lower, _ in expected_scenarios.values())
    union_upper = max(upper for _, upper in expected_scenarios.values())
    declared_union = contract["derived_set_valued_rule"]["union_envelope"]
    check("union envelope", {"lower": str(union_lower), "upper": str(union_upper)} == {"lower": declared_union["lower"], "upper": declared_union["upper"]}, [union_lower, union_upper], [frac(declared_union["lower"]), frac(declared_union["upper"])], "interval")
    broad = expected_scenarios["broad_exotic"]
    for sid, bounds in expected_scenarios.items():
        check(f"broad contains {sid}", broad[0] <= bounds[0] and bounds[1] <= broad[1], broad, bounds, "containment")

    admission = contract["admission"]
    check("no likelihood", admission["likelihood_admitted"] is False, admission["likelihood_admitted"], False, "firewall")
    check("no covariance", admission["covariance_admitted"] is False, admission["covariance_admitted"], False, "firewall")
    check("no score", admission["aggregate_scoring_allowed"] is False, admission["aggregate_scoring_allowed"], False, "firewall")
    check("no prospective", admission["prospective_credit"] is False, admission["prospective_credit"], False, "firewall")
    check("all map stages absent", all(value == "NOT_ADMITTED" for value in admission["forward_map_stages"].values()), admission["forward_map_stages"], "NOT_ADMITTED", "firewall")
    check("set-valued rule", contract["derived_set_valued_rule"]["operation"] == "interval_subtraction", contract["derived_set_valued_rule"]["operation"], "interval_subtraction", "scope")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "HOLD-LC-001-SET-VALUED-DELAY-ENVELOPE",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "task_id": contract["task_id"],
        "holdout_id": contract["holdout_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "detector_interval": {"lower": str(dlo), "upper": str(dhi)},
            "scenario_envelopes": derived,
            "union_envelope": {"lower": str(union_lower), "upper": str(union_upper)},
            "set_valued_feasibility_only": True,
            "likelihood_admitted": False,
            "covariance_admitted": False,
            "aggregate_scoring_allowed": False,
            "prospective_credit": False,
        },
        "boundary": contract["non_claims"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"contract_sha256": normalized_sha256(CONTRACT), "base_packet_sha256": normalized_sha256(base), "source_sha256": source["source"]["sha256"]},
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY HOLD-LC-001 SET-VALUED ENVELOPE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
