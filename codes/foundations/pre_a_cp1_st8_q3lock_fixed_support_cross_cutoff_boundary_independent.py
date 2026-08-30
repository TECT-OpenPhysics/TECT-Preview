#!/usr/bin/env python3
"""Non-importing control for the R-435/R-436 support crossing audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-fixed-support-cross-cutoff-boundary-manifest.json"
R435_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-original-source-interval-d17-manifest.json"
R436_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-original-source-interval-d18-manifest.json"
R435_RUN = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-original_source_interval_d17/independent.json"
R436_RUN = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-original_source_interval_d18/independent.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-fixed_support_cross_cutoff_boundary/independent.json"


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
    check("independent parent identities", [r435["result_id"], r436["result_id"]] == ["R-435", "R-436"] and r435["verdict"] == "INDEPENDENT_FINITE_CONTROL_PASS" and r436["verdict"] == "INDEPENDENT_FINITE_CONTROL_PASS", [r435["result_id"], r436["result_id"], r435["verdict"], r436["verdict"]], "two independent controls", "parent")
    s435 = m435["source_contract"]
    s436 = m436["source_contract"]
    contract = manifest["comparison_contract"]
    common = ("volume", "beta", "orientation", "row_kind", "tail_threshold")
    check("same independent row rule", all(s435[field] == s436[field] == contract[field] for field in common) and s435["target_emission_ordinal"] == s436["target_emission_ordinal"] == contract["emission_ordinal"], {field: [s435[field], s436[field]] for field in common}, "same row contract", "contract")
    crossing_index = int(contract["crossing_index"])
    split435 = r435["derived"]["tail_split"]
    split436 = r436["derived"]["tail_split"]
    check("independent d17 core", crossing_index in split435["core"] and crossing_index not in split435["tail"], split435, "crossing index in d17 core", "support")
    check("independent d18 tail", crossing_index not in split436["core"] and crossing_index in split436["tail"], split436, "crossing index in d18 tail", "support")
    check("independent dimensions", r435["derived"]["fixed_row"]["cutoff_dimension"] != r436["derived"]["fixed_row"]["cutoff_dimension"], [r435["derived"]["fixed_row"]["cutoff_dimension"], r436["derived"]["fixed_row"]["cutoff_dimension"]], "distinct cutoffs", "contract")
    check("independent positive margins", float(r435["derived"]["lower_probe_margin"]) > 0.0 and float(r436["derived"]["lower_probe_margin"]) > 0.0, [r435["derived"]["lower_probe_margin"], r436["derived"]["lower_probe_margin"]], "positive finite lower-probe margins", "parent")
    check("fixed support remains open", manifest["scope"]["fixed_support_uniformity_closed"] is False and manifest["scope"]["increasing_core_tail_modulus_closed"] is False, manifest["scope"], "both uniform support flags false", "scope")
    check("physical promotion firewall", not any(manifest["scope"][key] for key in ("common_core_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), manifest["scope"], "all physical flags false", "scope")
    payload = {
        "schema": "tect/pre-a-r437-independent/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": "R-437",
        "exploration_id": "EXP-001282",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "independent",
        "verdict": "INDEPENDENT_FIXED_SUPPORT_BOUNDARY_CONTROL",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {"d17_split": split435, "d18_split": split436, "crossing_index": crossing_index, "fixed_support_uniformity_closed": False, "increasing_core_tail_modulus_closed": False},
        "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "r435_manifest": sha256(R435_MANIFEST), "r436_manifest": sha256(R436_MANIFEST), "r435_run": sha256(R435_RUN), "r436_run": sha256(R436_RUN)},
        "evidence_level": "T0 / EXECUTED INDEPENDENT FINITE SUPPORT CONTROL",
        "non_claims": manifest["non_claims"] + ["The independent control uses the parent independent rows; it does not supply a uniform modulus."],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-437 INDEPENDENT {payload['verdict']} {len(checks)}/{len(checks)} index={crossing_index} d17=core d18=tail", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else REPO / args.output
    payload = run(destination)
    if args.self_test:
        assert payload["verdict"] == "INDEPENDENT_FIXED_SUPPORT_BOUNDARY_CONTROL"
        print("R-437 INDEPENDENT SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
