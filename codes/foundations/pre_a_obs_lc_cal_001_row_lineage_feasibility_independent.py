#!/usr/bin/env python3
"""Independent stdlib reconstruction of the OBS-LC-CAL-001 row contract."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / "strategy/obs-lc-cal-001-row-lineage-feasibility-manifest-v0.1.json"
SOURCE_PACKET = REPO / "strategy/obs-lc-cal-001-source-packet-v0.1.json"
ALLOWLIST = REPO / "strategy/obs-lc-cal-001-row-allowlist-v0.1.json"
INVERSE_MANIFEST = REPO / "strategy/pre-a-observation-first-inverse-lane-contract-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-obs_lc_cal_001_row_lineage_feasibility/independent.json"

EXPECTED_SOURCE_PACKET_HASH = "2013f8b0a4ce12adc47fc63c92ecefa7b1178a47eb2a244715a76d196b6389c2"
EXPECTED_ALLOWLIST_HASH = "186576ddb894d321e9bd7f97321c48b77f7660bf2b0e4cda631c5e3adfc5aa70"
EXPECTED_INVERSE_HASH = "fd5f37d0e095062a415368749d10d65de14b799938673b4460c3e849f07b9a46"
EXPECTED_SOURCE_HASH = "2fde66d227d1cbc5524baf23d5925d2ca30522a371d092387901ac7566273827"
EXPECTED_DIMENSIONS = (3, 4, 5, 6, 7, 8, 9)
EXPECTED_IDS = {
    "S3-ISO-D3-KV00",
    "S3-ISO-D4-CI00",
    "S3-ISO-D5-KV00",
    "S3-ISO-D6-CI00",
    "S3-ISO-D7-KV00",
    "S3-ISO-D8-CI00",
    "S3-ISO-D9-KV00",
}


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path}: JSON root must be an object")
    return value


def validate(source: dict[str, Any], allowlist: dict[str, Any], inverse: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("source packet schema", source.get("schema") == "tect/observation-anchor-packet/0.1", source.get("schema"), "tect/observation-anchor-packet/0.1", "source")
    check("source packet status", source.get("status") == "HASH_FROZEN_FEASIBILITY_ONLY", source.get("status"), "HASH_FROZEN_FEASIBILITY_ONLY", "source")
    check("source anchor", source.get("anchor_id") == "OBS-LC-CAL-001", source.get("anchor_id"), "OBS-LC-CAL-001", "source")
    source_meta = source.get("source", {})
    check("source hash", source_meta.get("sha256") == EXPECTED_SOURCE_HASH, source_meta.get("sha256"), EXPECTED_SOURCE_HASH, "source")
    check("source URL", str(source_meta.get("url", "")).startswith("https://"), source_meta.get("url"), "https URL", "source")
    scope = source.get("observable_scope", {})
    check("source frame", scope.get("frame") == "Standard Sun-centered inertial reference frame", scope.get("frame"), "Sun-centered frame", "source")
    source_uncertainty = source.get("uncertainty_contract", {})
    check("source likelihood", source_uncertainty.get("likelihood") == "NOT_ADMITTED", source_uncertainty.get("likelihood"), "NOT_ADMITTED", "uncertainty")
    check("source covariance", source_uncertainty.get("covariance") == "NOT_ADMITTED", source_uncertainty.get("covariance"), "NOT_ADMITTED", "uncertainty")

    check("allowlist schema", allowlist.get("schema") == "tect/observation-anchor-row-allowlist/0.1", allowlist.get("schema"), "tect/observation-anchor-row-allowlist/0.1", "allowlist")
    check("allowlist status", allowlist.get("status") == "FROZEN_FEASIBILITY_ONLY", allowlist.get("status"), "FROZEN_FEASIBILITY_ONLY", "allowlist")
    source_link = allowlist.get("source_packet", {})
    check("allowlist anchor", allowlist.get("anchor_id") == "OBS-LC-CAL-001", allowlist.get("anchor_id"), "OBS-LC-CAL-001", "allowlist")
    check("allowlist source hash", source_link.get("source_sha256") == EXPECTED_SOURCE_HASH, source_link.get("source_sha256"), EXPECTED_SOURCE_HASH, "provenance")
    row_scope = allowlist.get("scope", {})
    check("allowlist table", row_scope.get("table") == "S3", row_scope.get("table"), "S3", "allowlist")
    check("allowlist sector", row_scope.get("sector") == "photon", row_scope.get("sector"), "photon", "allowlist")
    rows = allowlist.get("rows")
    check("row list", isinstance(rows, list) and len(rows) == len(EXPECTED_DIMENSIONS), len(rows) if isinstance(rows, list) else None, len(EXPECTED_DIMENSIONS), "allowlist")
    dimensions = sorted(row.get("operator_dimension") for row in rows if isinstance(row, dict))
    ids = {row.get("row_id") for row in rows if isinstance(row, dict)}
    check("dimensions", tuple(dimensions) == EXPECTED_DIMENSIONS, dimensions, list(EXPECTED_DIMENSIONS), "allowlist")
    check("row IDs", ids == EXPECTED_IDS and len(ids) == len(rows), sorted(ids), sorted(EXPECTED_IDS), "allowlist")
    check("row locators", all("Table S3" in str(row.get("source_locator", "")) for row in rows), "all rows", "Table S3", "provenance")
    check("row bound forms", all("absolute_value" in str(row.get("bound_form", "")) for row in rows), "all rows", "absolute_value", "allowlist")
    row_uncertainty = allowlist.get("uncertainty_contract", {})
    check("row likelihood", row_uncertainty.get("likelihood") == "NOT_ADMITTED", row_uncertainty.get("likelihood"), "NOT_ADMITTED", "uncertainty")
    check("row covariance", row_uncertainty.get("covariance") == "NOT_ADMITTED", row_uncertainty.get("covariance"), "NOT_ADMITTED", "uncertainty")
    row_rule = str(row_uncertainty.get("row_rule", "")).lower()
    forbidden = " ".join(str(item) for item in row_uncertainty.get("forbidden", [])).lower()
    check("row independence rule", "separately" in row_rule and "independent" in forbidden, {"row_rule": row_uncertainty.get("row_rule"), "forbidden": row_uncertainty.get("forbidden")}, "separate rows; independent aggregation forbidden", "uncertainty")
    check("map not admitted", allowlist.get("theory_map_contract", {}).get("status") == "NOT_ADMITTED", allowlist.get("theory_map_contract", {}).get("status"), "NOT_ADMITTED", "map")
    check("inverse map order", [item.get("id") for item in inverse.get("forward_map_contract", {}).get("stages", [])] == ["F_reg", "F_lim", "F_eff", "F_obs"], [item.get("id") for item in inverse.get("forward_map_contract", {}).get("stages", [])], ["F_reg", "F_lim", "F_eff", "F_obs"], "inverse")
    check("inverse no selection", inverse.get("candidate_comparison", {}).get("current_selection") == "NO_SELECTION_ZERO_ADMITTED_MICROSCOPIC_FORWARD_MAPS", inverse.get("candidate_comparison", {}).get("current_selection"), "NO_SELECTION_ZERO_ADMITTED_MICROSCOPIC_FORWARD_MAPS", "inverse")
    return checks


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source = load(SOURCE_PACKET)
    allowlist = load(ALLOWLIST)
    inverse = load(INVERSE_MANIFEST)
    checks = validate(source, allowlist, inverse)
    payload: dict[str, Any] = {
        "schema": "tect/obs-lc-cal-001-row-lineage-feasibility-independent/1.0",
        "run_kind": "independent",
        "result_id": "R-446",
        "exploration_id": "EXP-001298",
        "task_id": "T-061",
        "verdict": "INDEPENDENT_FROZEN_LINEAGE_FEASIBILITY_INTERFACE_CONTROL",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "row_count": len(allowlist["rows"]),
            "operator_dimensions": sorted(row["operator_dimension"] for row in allowlist["rows"]),
            "source_hash_pinned": source["source"]["sha256"] == EXPECTED_SOURCE_HASH,
            "likelihood_admitted": False,
            "covariance_admitted": False,
            "candidate_map_admitted": False,
            "candidate_scoring_performed": False,
        },
        "source_hashes": {
            "script": sha256(SCRIPT),
            "source_packet": sha256(SOURCE_PACKET),
            "row_allowlist": sha256(ALLOWLIST),
            "inverse_contract": sha256(INVERSE_MANIFEST),
        },
        "expected_authority_hashes": {
            "source_packet": EXPECTED_SOURCE_PACKET_HASH,
            "row_allowlist": EXPECTED_ALLOWLIST_HASH,
            "inverse_contract": EXPECTED_INVERSE_HASH,
        },
        "evidence_level": "T0 source-lineage plus pre-registered finite feasibility-interface control",
        "non_claims": [
            "No candidate is admitted, selected, or ranked.",
            "No likelihood, covariance, aggregate score, physical symmetry, Pre-A, Sector-A, C6, QFT, Yang-Mills, gravity, continuum, empirical-predictivity, or mass-gap conclusion follows."
        ],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    destination = output if output.is_absolute() else REPO / output
    atomic_json(destination, payload)
    print(f"R-446 INDEPENDENT {payload['verdict']} {len(checks)}/{len(checks)} rows={payload['derived']['row_count']}", flush=True)
    return payload


def self_test() -> int:
    source = load(SOURCE_PACKET)
    allowlist = load(ALLOWLIST)
    inverse = load(INVERSE_MANIFEST)
    validate(source, allowlist, inverse)
    fixtures: list[tuple[str, dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    missing_row = copy.deepcopy(allowlist)
    missing_row["rows"] = missing_row["rows"][:-1]
    fixtures.append(("missing-row", source, missing_row, inverse))
    aggregate = copy.deepcopy(allowlist)
    aggregate["uncertainty_contract"]["covariance"] = "GAUSSIAN"
    fixtures.append(("aggregate-covariance", source, aggregate, inverse))
    selected = copy.deepcopy(inverse)
    selected["candidate_comparison"]["current_selection"] = "M1"
    fixtures.append(("candidate-selection", source, allowlist, selected))
    rejected = 0
    for label, item_source, item_allowlist, item_inverse in fixtures:
        try:
            validate(item_source, item_allowlist, item_inverse)
        except (AssertionError, KeyError, TypeError):
            rejected += 1
        else:
            raise AssertionError(f"hostile fixture accepted: {label}")
    print(f"R-446 INDEPENDENT SELFTEST: PASS ({rejected}/3 hostile fixtures rejected)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    run(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
