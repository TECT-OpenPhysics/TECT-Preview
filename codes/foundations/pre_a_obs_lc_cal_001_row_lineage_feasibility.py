#!/usr/bin/env python3
"""Audit the frozen OBS-LC-CAL-001 row lineage and feasibility interface.

This is a source-interface result, not a candidate fit.  It verifies the
hash-pinned source and row packets, the complete pre-registered S3 isotropic
photon slice, and the uncertainty/map firewalls in the existing inverse-lane
contract.  It deliberately does not evaluate a microscopic prediction.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
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
INVERSE_CHECK = REPO / "verification/scripts/check_obs_inverse.py"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-obs_lc_cal_001_row_lineage_feasibility/primary.json"

EXPECTED_SOURCE_HASH = "2fde66d227d1cbc5524baf23d5925d2ca30522a371d092387901ac7566273827"
EXPECTED_DIMENSIONS = (3, 4, 5, 6, 7, 8, 9)
EXPECTED_ROW_IDS = {
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
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path}: JSON root must be an object")
    return value


def validate(
    manifest: dict[str, Any],
    source: dict[str, Any],
    allowlist: dict[str, Any],
    inverse: dict[str, Any],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check(
        "manifest identity",
        [manifest.get("result_id"), manifest.get("exploration_id"), manifest.get("task_id"), manifest.get("claim_bearing"), manifest.get("status")]
        == ["R-446", "EXP-001298", "T-061", False, "FROZEN_LINEAGE_FEASIBILITY_INTERFACE_AUDITED"],
        [manifest.get("result_id"), manifest.get("exploration_id"), manifest.get("task_id"), manifest.get("claim_bearing"), manifest.get("status")],
        "R-446/EXP-001298/T-061/false/audited",
        "provenance",
    )
    check("manifest methods firewall", manifest.get("checks", {}).get("methods_unchanged") is True, manifest.get("checks", {}).get("methods_unchanged"), True, "scope")
    pointers = manifest.get("authority_pointers")
    check("authority pointer count", isinstance(pointers, list) and len(pointers) == 3, len(pointers) if isinstance(pointers, list) else None, 3, "provenance")
    pointer_paths = {item.get("path") for item in pointers if isinstance(item, dict)}
    check("authority pointer set", pointer_paths == {p.relative_to(REPO).as_posix() for p in (SOURCE_PACKET, ALLOWLIST, INVERSE_MANIFEST)}, sorted(pointer_paths), "source, allowlist, inverse contract", "provenance")
    for pointer in pointers:
        if not isinstance(pointer, dict):
            raise AssertionError(f"malformed authority pointer: {pointer!r}")
        path = REPO / str(pointer["path"])
        check(f"authority exists {pointer['path']}", path.is_file(), path.is_file(), True, "provenance")
        check(f"authority hash {pointer['path']}", sha256(path) == pointer.get("sha256"), sha256(path), pointer.get("sha256"), "provenance")

    source_contract = manifest.get("source_contract", {})
    source_meta = source.get("source", {})
    check("source packet schema", source.get("schema") == "tect/observation-anchor-packet/0.1", source.get("schema"), "tect/observation-anchor-packet/0.1", "source")
    check("source packet status", source.get("status") == "HASH_FROZEN_FEASIBILITY_ONLY", source.get("status"), "HASH_FROZEN_FEASIBILITY_ONLY", "source")
    check("source anchor", source.get("anchor_id") == source_contract.get("anchor_id") == "OBS-LC-CAL-001", source.get("anchor_id"), "OBS-LC-CAL-001", "source")
    check("source edition", source_meta.get("edition") == source_contract.get("source_edition"), source_meta.get("edition"), source_contract.get("source_edition"), "source")
    check("source hash declaration", source_meta.get("sha256") == source_contract.get("source_sha256") == EXPECTED_SOURCE_HASH, source_meta.get("sha256"), EXPECTED_SOURCE_HASH, "source")
    check("source URL", str(source_meta.get("url", "")).startswith("https://"), source_meta.get("url"), "https URL", "source")
    check("source dates", bool(source_meta.get("published_at")) and bool(source_meta.get("retrieved_at")), {"published_at": source_meta.get("published_at"), "retrieved_at": source_meta.get("retrieved_at")}, "both dates", "source")
    observable = source.get("observable_scope", {})
    check("source frame", observable.get("frame") == source_contract.get("frame"), observable.get("frame"), source_contract.get("frame"), "source")
    uncertainty = source.get("uncertainty_contract", {})
    check("source likelihood firewall", uncertainty.get("likelihood") == "NOT_ADMITTED", uncertainty.get("likelihood"), "NOT_ADMITTED", "uncertainty")
    check("source covariance firewall", uncertainty.get("covariance") == "NOT_ADMITTED", uncertainty.get("covariance"), "NOT_ADMITTED", "uncertainty")
    forbidden_rule = str(uncertainty.get("forbidden_rule", "")).lower()
    check("source no synthetic likelihood", "multiply" in forbidden_rule and "independent" in forbidden_rule, uncertainty.get("forbidden_rule"), "independent aggregation forbidden", "uncertainty")

    check("allowlist schema", allowlist.get("schema") == "tect/observation-anchor-row-allowlist/0.1", allowlist.get("schema"), "tect/observation-anchor-row-allowlist/0.1", "allowlist")
    check("allowlist status", allowlist.get("status") == "FROZEN_FEASIBILITY_ONLY", allowlist.get("status"), "FROZEN_FEASIBILITY_ONLY", "allowlist")
    allow_source = allowlist.get("source_packet", {})
    check("allowlist source path", allow_source.get("path") == SOURCE_PACKET.relative_to(REPO).as_posix(), allow_source.get("path"), SOURCE_PACKET.relative_to(REPO).as_posix(), "provenance")
    check("allowlist source hash", allow_source.get("source_sha256") == EXPECTED_SOURCE_HASH, allow_source.get("source_sha256"), EXPECTED_SOURCE_HASH, "provenance")
    selection = allowlist.get("selection_principle", {})
    check("allowlist preregistration", "pre-registered" in str(selection.get("reason", "")), selection.get("reason"), "pre-registered selection", "allowlist")
    scope = allowlist.get("scope", {})
    check("allowlist scope", [scope.get("table"), scope.get("sector"), scope.get("frame")] == ["S3", "photon", source_contract.get("frame")], [scope.get("table"), scope.get("sector"), scope.get("frame")], ["S3", "photon", source_contract.get("frame")], "allowlist")
    rows = allowlist.get("rows")
    check("row list present", isinstance(rows, list) and bool(rows), len(rows) if isinstance(rows, list) else None, "nonempty row list", "allowlist")
    row_ids = {row.get("row_id") for row in rows if isinstance(row, dict)}
    dimensions = sorted(row.get("operator_dimension") for row in rows if isinstance(row, dict))
    check("complete dimension slice", tuple(dimensions) == EXPECTED_DIMENSIONS, dimensions, list(EXPECTED_DIMENSIONS), "allowlist")
    check("row identity set", row_ids == EXPECTED_ROW_IDS and len(row_ids) == len(rows), sorted(row_ids), sorted(EXPECTED_ROW_IDS), "allowlist")
    for row in rows:
        if not isinstance(row, dict):
            raise AssertionError(f"malformed row: {row!r}")
        check(f"row {row.get('row_id')} table", row.get("table") == "S3", row.get("table"), "S3", "allowlist")
        check(f"row {row.get('row_id')} locator", "Table S3" in str(row.get("source_locator", "")), row.get("source_locator"), "Table S3 locator", "provenance")
        check(f"row {row.get('row_id')} bound", "absolute_value" in str(row.get("bound_form", "")), row.get("bound_form"), "absolute_value bound", "allowlist")

    row_uncertainty = allowlist.get("uncertainty_contract", {})
    check("row likelihood firewall", row_uncertainty.get("likelihood") == "NOT_ADMITTED", row_uncertainty.get("likelihood"), "NOT_ADMITTED", "uncertainty")
    check("row covariance firewall", row_uncertainty.get("covariance") == "NOT_ADMITTED", row_uncertainty.get("covariance"), "NOT_ADMITTED", "uncertainty")
    check("row aggregation firewall", any("joint" in str(value).lower() for value in row_uncertainty.get("forbidden", [])), row_uncertainty.get("forbidden"), "joint aggregation forbidden", "uncertainty")
    theory_map = allowlist.get("theory_map_contract", {})
    check("candidate map firewall", theory_map.get("status") == "NOT_ADMITTED", theory_map.get("status"), "NOT_ADMITTED", "map")
    check("four-stage map requirement", set(theory_map.get("required_before_scoring", [])) >= {"complete F_reg/F_lim/F_eff/F_obs map"}, theory_map.get("required_before_scoring"), "complete four-stage map", "map")

    inverse_contract = inverse.get("forward_map_contract", {})
    check("inverse four-stage order", [item.get("id") for item in inverse_contract.get("stages", [])] == ["F_reg", "F_lim", "F_eff", "F_obs"], [item.get("id") for item in inverse_contract.get("stages", [])], ["F_reg", "F_lim", "F_eff", "F_obs"], "inverse contract")
    check("inverse zero-map status", "NO_ADMITTED_MICROSCOPIC_FORWARD_MAP" in str(inverse.get("status", "")), inverse.get("status"), "zero admitted microscopic maps", "inverse contract")
    check("inverse no selection", inverse.get("candidate_comparison", {}).get("current_selection") == "NO_SELECTION_ZERO_ADMITTED_MICROSCOPIC_FORWARD_MAPS", inverse.get("candidate_comparison", {}).get("current_selection"), "NO_SELECTION_ZERO_ADMITTED_MICROSCOPIC_FORWARD_MAPS", "inverse contract")
    check("manifest firewall flags", all(value is True for value in manifest.get("checks", {}).values()), manifest.get("checks"), "all declared checks true", "firewall")
    return checks


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = load(MANIFEST)
    source = load(SOURCE_PACKET)
    allowlist = load(ALLOWLIST)
    inverse = load(INVERSE_MANIFEST)
    checks = validate(manifest, source, allowlist, inverse)
    inverse_process = subprocess.run(
        [sys.executable, "-X", "utf8", str(INVERSE_CHECK), "--self-test"],
        cwd=REPO,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if inverse_process.returncode != 0:
        raise AssertionError(f"inverse contract validator failed: {inverse_process.stdout}\n{inverse_process.stderr}")
    payload: dict[str, Any] = {
        "schema": "tect/obs-lc-cal-001-row-lineage-feasibility-primary/1.0",
        "run_kind": "primary",
        "result_id": "R-446",
        "exploration_id": "EXP-001298",
        "task_id": "T-061",
        "verdict": "FROZEN_LINEAGE_FEASIBILITY_INTERFACE_AUDITED",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "row_count": len(allowlist["rows"]),
            "operator_dimension_min": min(row["operator_dimension"] for row in allowlist["rows"]),
            "operator_dimension_max": max(row["operator_dimension"] for row in allowlist["rows"]),
            "source_hash_pinned": True,
            "likelihood_admitted": False,
            "covariance_admitted": False,
            "candidate_map_admitted": False,
            "candidate_scoring_performed": False,
            "inverse_contract_selftest": "PASS",
        },
        "source_hashes": {
            path.relative_to(REPO).as_posix(): sha256(path)
            for path in (SCRIPT, MANIFEST, SOURCE_PACKET, ALLOWLIST, INVERSE_MANIFEST, INVERSE_CHECK)
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "boundary": manifest["boundary"],
        "non_claims": manifest["non_claims"],
        "inverse_validator_output": (inverse_process.stdout + inverse_process.stderr).strip(),
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    destination = output if output.is_absolute() else REPO / output
    atomic_json(destination, payload)
    print(f"R-446 PRIMARY {payload['verdict']} {len(checks)}/{len(checks)} rows={payload['derived']['row_count']} dims={payload['derived']['operator_dimension_min']}-{payload['derived']['operator_dimension_max']}", flush=True)
    return payload


def self_test() -> int:
    manifest = load(MANIFEST)
    source = load(SOURCE_PACKET)
    allowlist = load(ALLOWLIST)
    inverse = load(INVERSE_MANIFEST)
    validate(manifest, source, allowlist, inverse)
    mutations: list[tuple[str, dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    bad_hash = copy.deepcopy(manifest)
    bad_hash["authority_pointers"][0]["sha256"] = "0" * 64
    mutations.append(("authority hash", bad_hash, source, allowlist, inverse))
    bad_row = copy.deepcopy(allowlist)
    bad_row["rows"] = bad_row["rows"][:-1]
    mutations.append(("row omission", manifest, source, bad_row, inverse))
    bad_score = copy.deepcopy(allowlist)
    bad_score["uncertainty_contract"]["likelihood"] = "GAUSSIAN"
    mutations.append(("likelihood admission", manifest, source, bad_score, inverse))
    bad_map = copy.deepcopy(inverse)
    bad_map["candidate_comparison"]["current_selection"] = "PA-M1-CURRENT-PINNED-PRODUCTION-FUNCTIONAL-v0"
    mutations.append(("candidate selection", manifest, source, allowlist, bad_map))
    rejected = 0
    for label, item_manifest, item_source, item_allowlist, item_inverse in mutations:
        try:
            validate(item_manifest, item_source, item_allowlist, item_inverse)
        except (AssertionError, KeyError, TypeError):
            rejected += 1
        else:
            raise AssertionError(f"hostile mutation accepted: {label}")
    print(f"R-446 PRIMARY SELFTEST: PASS ({rejected}/4 hostile mutations rejected)")
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
