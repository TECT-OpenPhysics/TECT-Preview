#!/usr/bin/env python3
"""Hostile mutations for the frozen OBS-LC-CAL-001 interface."""

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
SOURCE_PACKET = REPO / "strategy/obs-lc-cal-001-source-packet-v0.1.json"
ALLOWLIST = REPO / "strategy/obs-lc-cal-001-row-allowlist-v0.1.json"
INVERSE_MANIFEST = REPO / "strategy/pre-a-observation-first-inverse-lane-contract-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-obs_lc_cal_001_row_lineage_feasibility/hostile.json"
SOURCE_HASH = "2fde66d227d1cbc5524baf23d5925d2ca30522a371d092387901ac7566273827"
DIMENSIONS = (3, 4, 5, 6, 7, 8, 9)
ROW_IDS = {
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


def valid(source: dict[str, Any], allowlist: dict[str, Any], inverse: dict[str, Any]) -> bool:
    source_meta = source.get("source", {})
    rows = allowlist.get("rows", [])
    row_uncertainty = allowlist.get("uncertainty_contract", {})
    return all(
        [
            source.get("schema") == "tect/observation-anchor-packet/0.1",
            source.get("status") == "HASH_FROZEN_FEASIBILITY_ONLY",
            source.get("anchor_id") == "OBS-LC-CAL-001",
            source_meta.get("sha256") == SOURCE_HASH,
            allowlist.get("schema") == "tect/observation-anchor-row-allowlist/0.1",
            allowlist.get("status") == "FROZEN_FEASIBILITY_ONLY",
            allowlist.get("anchor_id") == "OBS-LC-CAL-001",
            allowlist.get("source_packet", {}).get("source_sha256") == SOURCE_HASH,
            allowlist.get("scope", {}).get("table") == "S3",
            allowlist.get("scope", {}).get("sector") == "photon",
            len(rows) == len(DIMENSIONS),
            tuple(sorted(row.get("operator_dimension") for row in rows if isinstance(row, dict))) == DIMENSIONS,
            {row.get("row_id") for row in rows if isinstance(row, dict)} == ROW_IDS,
            len({row.get("row_id") for row in rows if isinstance(row, dict)}) == len(rows),
            all("Table S3" in str(row.get("source_locator", "")) for row in rows),
            source.get("uncertainty_contract", {}).get("likelihood") == "NOT_ADMITTED",
            source.get("uncertainty_contract", {}).get("covariance") == "NOT_ADMITTED",
            row_uncertainty.get("likelihood") == "NOT_ADMITTED",
            row_uncertainty.get("covariance") == "NOT_ADMITTED",
            allowlist.get("theory_map_contract", {}).get("status") == "NOT_ADMITTED",
            [item.get("id") for item in inverse.get("forward_map_contract", {}).get("stages", [])] == ["F_reg", "F_lim", "F_eff", "F_obs"],
            inverse.get("candidate_comparison", {}).get("current_selection") == "NO_SELECTION_ZERO_ADMITTED_MICROSCOPIC_FORWARD_MAPS",
        ]
    )


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source = load(SOURCE_PACKET)
    allowlist = load(ALLOWLIST)
    inverse = load(INVERSE_MANIFEST)
    if not valid(source, allowlist, inverse):
        raise AssertionError("unmutated authority input rejected")
    fixtures: list[tuple[str, dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    mutated = copy.deepcopy(source)
    mutated["source"]["sha256"] = "0" * 64
    fixtures.append(("source-hash-drift", mutated, allowlist, inverse))
    mutated = copy.deepcopy(allowlist)
    mutated["rows"] = mutated["rows"][:-1]
    fixtures.append(("row-omission", source, mutated, inverse))
    mutated = copy.deepcopy(allowlist)
    mutated["rows"][0]["row_id"] = "S3-ISO-D3-ALIAS"
    fixtures.append(("row-alias", source, mutated, inverse))
    mutated = copy.deepcopy(allowlist)
    mutated["rows"][0]["table"] = "S4"
    mutated["rows"][0]["source_locator"] = "PDF p.24, Table S4"
    fixtures.append(("table-substitution", source, mutated, inverse))
    mutated = copy.deepcopy(source)
    mutated["uncertainty_contract"]["likelihood"] = "GAUSSIAN"
    fixtures.append(("likelihood-injection", mutated, allowlist, inverse))
    mutated = copy.deepcopy(allowlist)
    mutated["uncertainty_contract"]["covariance"] = "DIAGONAL"
    fixtures.append(("covariance-injection", source, mutated, inverse))
    mutated = copy.deepcopy(allowlist)
    mutated["theory_map_contract"]["status"] = "ADMITTED"
    fixtures.append(("map-admission", source, mutated, inverse))
    mutated = copy.deepcopy(inverse)
    mutated["candidate_comparison"]["current_selection"] = "PA-M1-CURRENT-PINNED-PRODUCTION-FUNCTIONAL-v0"
    fixtures.append(("candidate-selection", source, allowlist, mutated))
    records: list[dict[str, Any]] = []
    for label, item_source, item_allowlist, item_inverse in fixtures:
        rejected = not valid(item_source, item_allowlist, item_inverse)
        if not rejected:
            raise AssertionError(f"hostile mutation accepted: {label}")
        records.append({"mutation": label, "status": "REJECTED"})
    payload: dict[str, Any] = {
        "schema": "tect/obs-lc-cal-001-row-lineage-feasibility-hostile/1.0",
        "run_kind": "hostile",
        "result_id": "R-446",
        "exploration_id": "EXP-001298",
        "task_id": "T-061",
        "verdict": "HOSTILE_LINEAGE_FEASIBILITY_MUTATIONS_REJECTED",
        "assertion_count": len(records),
        "mutations_rejected": len(records),
        "mutations": records,
        "source_hashes": {
            "script": sha256(SCRIPT),
            "source_packet": sha256(SOURCE_PACKET),
            "row_allowlist": sha256(ALLOWLIST),
            "inverse_contract": sha256(INVERSE_MANIFEST),
        },
        "scope": {"claim_bearing": False, "candidate_scoring": False, "method_overhaul": False},
        "evidence_level": "T0 adversarial schema/interface control",
        "non_claims": [
            "Hostile rejection does not establish a microscopic candidate, physical symmetry, continuum limit, or mass gap.",
            "No source likelihood or covariance is manufactured by this test."
        ],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    destination = output if output.is_absolute() else REPO / output
    atomic_json(destination, payload)
    print(f"R-446 HOSTILE {payload['verdict']} {len(records)}/{len(records)}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output)
    if args.self_test:
        assert payload["mutations_rejected"] == 8
        print("R-446 HOSTILE SELFTEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
