#!/usr/bin/env python3
"""Audit the fixed threshold-four support across the R-435/R-436 rows.

The parent interval certificates are the numerical authorities.  This script
does not recompute their matrices; it extracts their directed threshold
assertions, verifies the common row contract, and records the finite crossing
as a route-local boundary.  It does not claim that every increasing-core or
full-sector route fails.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-fixed-support-cross-cutoff-boundary-manifest.json"
R435_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-original-source-interval-d17-manifest.json"
R436_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-original-source-interval-d18-manifest.json"
R435_RUN = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-original_source_interval_d17/primary.json"
R436_RUN = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-original_source_interval_d18/primary.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-fixed_support_cross_cutoff_boundary/primary.json"


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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def interval_bounds(text: str) -> tuple[Decimal, Decimal]:
    match = re.fullmatch(r"\[\s*([^,]+),\s*([^\]]+)\s*\]", text.strip())
    if match is None:
        raise ValueError(f"not an interval: {text!r}")
    return Decimal(match.group(1)), Decimal(match.group(2))


def threshold_assertion(run: dict[str, Any], kind: str, index: int) -> tuple[Decimal, Decimal, dict[str, Any]]:
    name = f"{kind} threshold {index}"
    matches = [item for item in run["assertions"] if item.get("name") == name and item.get("status") == "PASS"]
    if len(matches) != 1:
        raise AssertionError(f"expected one PASS assertion {name!r}, found {len(matches)}")
    item = matches[0]
    return (*interval_bounds(item["actual"]), item)


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    m435 = json.loads(R435_MANIFEST.read_text(encoding="utf-8"))
    m436 = json.loads(R436_MANIFEST.read_text(encoding="utf-8"))
    r435 = json.loads(R435_RUN.read_text(encoding="utf-8"))
    r436 = json.loads(R436_RUN.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-437" and manifest["exploration_id"] == "EXP-001282" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-437/EXP-001282/false", "provenance")
    check("parent identities", [m435["result_id"], m436["result_id"]] == ["R-435", "R-436"] and [r435["result_id"], r436["result_id"]] == ["R-435", "R-436"], [m435["result_id"], m436["result_id"], r435["result_id"], r436["result_id"]], "R-435/R-436 manifests and runs", "provenance")
    check("parent interval verdicts", r435["verdict"] == "ORIGINAL_SOURCE_INTERVAL_CERTIFIED" and r436["verdict"] == "ORIGINAL_SOURCE_INTERVAL_CERTIFIED", [r435["verdict"], r436["verdict"]], "both certified", "parent")

    s435 = m435["source_contract"]
    s436 = m436["source_contract"]
    common_fields = ("volume", "beta", "orientation", "row_kind", "target_emission_ordinal", "tail_threshold")
    check("same row rule", all(s435[field] == s436[field] == manifest["comparison_contract"][field if field != "target_emission_ordinal" else "emission_ordinal"] for field in common_fields), {field: [s435[field], s436[field]] for field in common_fields}, "common V/beta/orientation/row/ordinal/threshold", "contract")
    check("distinct cutoffs", s435["cutoff_dimension"] != s436["cutoff_dimension"], [s435["cutoff_dimension"], s436["cutoff_dimension"]], "two cutoff dimensions", "contract")
    crossing_index = int(manifest["comparison_contract"]["crossing_index"])
    threshold = Decimal(str(manifest["comparison_contract"]["tail_threshold"]))
    check("fixed support source", manifest["comparison_contract"]["fixed_support_source"] == "R-435 core_indices" and crossing_index in m435["source_contract"]["core_indices"], m435["source_contract"]["core_indices"], "R-435 core containing crossing index", "support")
    check("d18 support changes", crossing_index not in m436["source_contract"]["core_indices"] and crossing_index in m436["source_contract"]["tail_indices"], m436["source_contract"], "crossing index in d18 tail", "support")

    d17_lower, d17_upper, d17_assertion = threshold_assertion(r435, "core", crossing_index)
    d18_lower, d18_upper, d18_assertion = threshold_assertion(r436, "tail", crossing_index)
    check("d17 interval below threshold", d17_upper < threshold, [str(d17_lower), str(d17_upper)], f"upper < {threshold}", "interval")
    check("d18 interval above threshold", d18_lower > threshold, [str(d18_lower), str(d18_upper)], f"lower > {threshold}", "interval")
    check("strict crossing", d17_upper < threshold < d18_lower, [str(d17_upper), str(d18_lower)], "d17 upper < threshold < d18 lower", "interval")
    check("parent derived splits", r435["derived"]["tail_split"] == {"core": s435["core_indices"], "tail": s435["tail_indices"]} and r436["derived"]["tail_split"] == {"core": s436["core_indices"], "tail": s436["tail_indices"]}, [r435["derived"]["tail_split"], r436["derived"]["tail_split"]], "manifest splits", "support")
    check("fixed-support verdict", manifest["expected_relation"]["fixed_support_uniformity_closed"] is False and manifest["scope"]["fixed_support_uniformity_closed"] is False, manifest["scope"]["fixed_support_uniformity_closed"], False, "scope")
    check("increasing-core remains open", manifest["scope"]["increasing_core_tail_modulus_closed"] is False, manifest["scope"]["increasing_core_tail_modulus_closed"], False, "scope")
    check("promotion firewall", not any(manifest["scope"][key] for key in ("cutoff_uniform_coarse_schur_closed", "volume_uniform_coarse_schur_closed", "phase_uniform_coarse_schur_closed", "exhaustion_uniform_coarse_schur_closed", "common_core_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), manifest["scope"], "all promotion flags false", "scope")

    payload = {
        "schema": "tect/pre-a-r437-primary/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": "R-437",
        "exploration_id": "EXP-001282",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "primary",
        "verdict": "FIXED_SUPPORT_ROUTE_LOCAL_BOUNDARY",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "comparison": manifest["comparison_contract"],
            "d17_index_interval": [str(d17_lower), str(d17_upper)],
            "d18_index_interval": [str(d18_lower), str(d18_upper)],
            "threshold": str(threshold),
            "d17_status": "core",
            "d18_status": "tail",
            "fixed_support_uniformity_closed": False,
            "increasing_core_tail_modulus_closed": False,
            "parent_run_hashes": {R435_RUN.relative_to(REPO).as_posix(): sha256(R435_RUN), R436_RUN.relative_to(REPO).as_posix(): sha256(R436_RUN)},
            "threshold_assertions": {"d17": d17_assertion, "d18": d18_assertion},
        },
        "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "r435_manifest": sha256(R435_MANIFEST), "r436_manifest": sha256(R436_MANIFEST), "r435_run": sha256(R435_RUN), "r436_run": sha256(R436_RUN)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-437 PRIMARY FIXED_SUPPORT_ROUTE_LOCAL_BOUNDARY {len(checks)}/{len(checks)} index={crossing_index} d17=core d18=tail", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else REPO / args.output
    payload = run(destination)
    if args.self_test:
        assert payload["verdict"] == "FIXED_SUPPORT_ROUTE_LOCAL_BOUNDARY"
        assert payload["derived"]["d17_status"] == "core" and payload["derived"]["d18_status"] == "tail"
        print("R-437 PRIMARY SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
