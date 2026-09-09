#!/usr/bin/env python3
"""Non-importing current-byte replay of the PAH-OMC-020 N2b audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = BASE / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-n2b-common-space-audit-v1.1/independent.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json": "e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc",
    "strategy/pa-hyp/PAH-OMC-017-result-v1.json": "4e2884d43a15846069a3ead9682d35e8321674a5d2ca3be727a1d411aae831fb",
    "strategy/pa-hyp/PAH-OMC-018-result-v1.json": "d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json": "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-019-closure-certificate.md": "593785ba86d0bf1b36541e62879a966062282c55cfbb990a805539b27955b8af",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-temporal-work.md": "2eeaa12411cba9525bfb6672fdae73d47a113349236639e0c3aa2e9ed8fbd9ab",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-inventory-stable/result.json": "e4ed74bed72b1b30a13ea059e51fab87af540ce85bc45515da6384b0e2a2ecf2",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-n-mosco-contract/n-mosco.json": "5864d7e10312a3a220d4fd7766f7bbd1d260287eb3441bc844e172a26026c96a",
    "verification/lean/Tect/PahOmc020.lean": "f269428a0732204cf37cdec2dd9e87ea094329a7150fdfba6b08ffb762ad9b3c",
}

MARKERS = {
    "path-space": re.compile(r"path[ -]?space", re.I),
    "martingale": re.compile(r"martingale", re.I),
    "non-explosion": re.compile(r"non[ -]?explosion", re.I),
    "lyapunov": re.compile(r"lyapunov", re.I),
    "N2c": re.compile(r"N2c", re.I),
    "N4": re.compile(r"N4", re.I),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load(relative: str) -> Any:
    return json.loads((BASE / relative).read_text(encoding="utf-8"))


def inventory() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted((BASE / "strategy/pa-hyp").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".json", ".md"}:
            continue
        # Exclude this audit's own successor artifacts irrespective of the
        # filename's case; otherwise adding the v1.1 contract/result changes
        # the inventory and makes an otherwise identical replay fail.
        lowered_name = path.name.lower()
        if "n2b-common-space-audit" in lowered_name or "n2c-owner-audit" in lowered_name:
            continue
        text = path.read_text(encoding="utf-8")
        found = sorted(name for name, pattern in MARKERS.items() if pattern.search(text))
        if found:
            records.append({"path": path.relative_to(BASE).as_posix(), "markers": found})
    return records


def strict_candidates(records: list[dict[str, Any]]) -> list[str]:
    required = ("source_authorized", "common", "u_n", "liminf", "recovery", "n2b", "lean")
    candidates: list[str] = []
    for item in records:
        if not item["path"].lower().endswith(".json"):
            continue
        text = (BASE / item["path"]).read_text(encoding="utf-8").lower()
        if "pah-omc-020" not in item["path"].lower():
            continue
        if not all(token in text for token in required):
            continue
        # Do not infer authority from prose such as
        # "only an explicit source_authorized_packet_present=true field
        # counts" inside a contract.  Admission requires an actual parsed
        # boolean provenance/status value in the packet JSON.
        try:
            payload = json.loads((BASE / item["path"]).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        nested = [
            payload,
            payload.get("provenance", {}) if isinstance(payload, dict) else {},
            payload.get("snapshot", {}) if isinstance(payload, dict) else {},
            payload.get("current_status", {}) if isinstance(payload, dict) else {},
        ]
        explicit_authority = any(
            isinstance(section, dict)
            and (
                section.get("source_authorized_packet_present") is True
                or section.get("source_authorized") is True
            )
            for section in nested
        )
        if explicit_authority:
            candidates.append(item["path"])
    return candidates


def compute() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, ok: bool) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})

    actual_pins = {relative: sha(BASE / relative) for relative in PINS}
    check("current-byte parent pins", actual_pins, PINS, actual_pins == PINS)
    pah = load("strategy/pa-hyp/PAH-001-v1.json")
    prereg = load("strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json")
    omc013 = load("strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json")
    omc017 = load("strategy/pa-hyp/PAH-OMC-017-result-v1.json")
    omc018 = load("strategy/pa-hyp/PAH-OMC-018-result-v1.json")
    omc019 = load("strategy/pa-hyp/PAH-OMC-019-result-v1.json")
    intake = load("strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.1.json")
    owner = load("claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-inventory-stable/result.json")
    mosco = load("claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-n-mosco-contract/n-mosco.json")
    work = (BASE / "strategy/pa-hyp/PAH-OMC-020-temporal-work.md").read_text(encoding="utf-8")

    check("PAH packet identity", pah.get("packet_id"), "PAH-001", pah.get("packet_id") == "PAH-001")
    check("j-before-n order", "first j" in prereg["scope"]["regulator_order"].lower() and "anchored n" in prereg["scope"]["regulator_order"].lower(), True,
          "first j" in prereg["scope"]["regulator_order"].lower() and "anchored n" in prereg["scope"]["regulator_order"].lower())
    check("external Markov time", "external unaccelerated markov time" in prereg["scope"]["time"].lower(), True,
          "external unaccelerated markov time" in prereg["scope"]["time"].lower())
    check("R-510/R-511/R-512 chain", [omc017.get("result_id"), omc018.get("result_id"), omc019.get("result_id")], ["R-510", "R-511", "R-512"],
          [omc017.get("result_id"), omc018.get("result_id"), omc019.get("result_id")] == ["R-510", "R-511", "R-512"])
    check("OMC-013 finite status", omc013.get("status", {}).get("stage2_status"), "HOLD_FOR_EVIDENCE_CLOSABILITY_AND_SEMIGROUP",
          omc013.get("status", {}).get("stage2_status") == "HOLD_FOR_EVIDENCE_CLOSABILITY_AND_SEMIGROUP")
    check("N2a intake not source-authorized", intake["provenance"]["source_authorized_packet_present"], False,
          intake["provenance"]["source_authorized_packet_present"] is False)
    check("owner inventory is hold", owner.get("verdict"), "HOLD_FOR_EVIDENCE", owner.get("verdict") == "HOLD_FOR_EVIDENCE")
    check("owner inventory finding", "no source-authorized" in owner.get("finding", "").lower(), True,
          "no source-authorized" in owner.get("finding", "").lower())
    check("N2b/N2d separation", all(token in work for token in ("(N2b)", "(N2d)", "arbitrary sequences")), True,
          all(token in work for token in ("(N2b)", "(N2d)", "arbitrary sequences")))
    local_pullback_firewall = "no assertion" in work.lower() and "bounded" in work.lower() and "full-space" in work.lower()
    check("local pullback not full map", local_pullback_firewall, True, local_pullback_firewall)
    check("N2c/N4 remains open", mosco.get("temporal_verdict"), "IN_PROGRESS", mosco.get("temporal_verdict") == "IN_PROGRESS")
    check("open obligations nonempty", len(mosco.get("open_obligations", [])) >= 1, True, len(mosco.get("open_obligations", [])) >= 1)
    records = inventory()
    candidates = strict_candidates(records)
    check("strict source-owner admission empty", candidates, [], not candidates)
    check("inventory nonempty", len(records) > 0, True, len(records) > 0)
    no_physical_promotion = all(item is False for item in (owner.get("physical_promotion", False), intake["provenance"]["physical_promotion"]))
    check("no physical promotion", no_physical_promotion, True, no_physical_promotion)
    return {
        "schema": "tect/pah-omc020-n2b-common-space-audit-independent/1.1",
        "audit_id": "PAH-OMC-020-N2B-COMMON-SPACE-AUDIT-001-V1.1-INDEPENDENT",
        "task_id": "T-064",
        "status": "PASS_INDEPENDENT_N2B_CURRENT_BYTE_HOLD",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": actual_pins,
        "checks": checks,
        "checks_passed": len(checks),
        "inventory": records,
        "strict_owner_candidates": candidates,
        "finding": "Independent current-byte replay agrees that the N2b common-space owner packet is absent; the old T-064 mismatch was provenance drift only, not a mathematical counterexample.",
        "missing_assumptions": [
            "Source-authorized common H/U_n and equicoercive minimizer bounds.",
            "Arbitrary-sequence N2b liminf and all-local recovery/data recovery.",
            "N2c/N4 unbounded-rate boundary escape and R-512 minimal-form identification.",
        ],
        "non_claims": [
            "No PAH-OMC-020 semigroup convergence or universal impossibility theorem.",
            "No PAH functional, rate, state, carrier, regulator, normalization, time or order change.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang-Mills or TOE conclusion.",
        ],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_n2b_common_space_audit_v11_independent.py --check",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    destination = args.output if args.output.is_absolute() else BASE / args.output
    if args.check:
        if not destination.is_file() or json.loads(destination.read_text(encoding="utf-8")) != payload:
            raise SystemExit("PAH-OMC-020 N2b independent v1.1 replay mismatch")
    else:
        write_json(destination, payload)
    print(f"PAH-OMC-020 N2B INDEPENDENT V1.1: PASS {payload['checks_passed']}/{payload['checks_passed']}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
