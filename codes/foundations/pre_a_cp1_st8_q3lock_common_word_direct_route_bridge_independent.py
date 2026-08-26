#!/usr/bin/env python3
"""Independent provenance-linked bridge for EXP-001176.

Only independent upstream run JSONs are consumed; no primary code is imported.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-common-word-direct-route-bridge"
MANIFEST = ROOT / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-independent-{SLUG}" / "independent.json"


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read_input(relative: str, expected_exploration: str) -> dict[str, Any]:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"missing input: {relative}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("verdict") != "PASS" or payload.get("exploration_id") != expected_exploration:
        raise AssertionError(f"input provenance mismatch: {relative}")
    return payload


def analyse(os_run: dict[str, Any], direct_run: dict[str, Any], weighted_run: dict[str, Any], fixture: dict[str, Any]) -> dict[str, Any]:
    beta = float(fixture["os_beta_for_sequence"])
    roles = ["endpoint_left", "center", "endpoint_right"]
    pairs = [("path4", "path5"), ("path5", "path6")]
    sequences: dict[str, list[float]] = {}
    for role in roles:
        rows = [row for row in os_run.get("comparisons", []) if row.get("source_role") == role and float(row.get("beta")) == beta]
        rows.sort(key=lambda row: (row["from_graph"], row["to_graph"]))
        if [(row["from_graph"], row["to_graph"]) for row in rows] != pairs:
            raise AssertionError(f"OS pair coverage for {role}: {rows!r}")
        sequences[role] = [float(row["max_context_delta"]) for row in rows]
    if not all(np.isfinite(value) and value > 0.0 for values in sequences.values() for value in values):
        raise AssertionError("nonpositive or nonfinite OS context delta")
    endpoint_rows = [row for row in os_run["comparisons"] if row["source_role"] in ("endpoint_left", "endpoint_right") and float(row["beta"]) == beta]
    endpoint_symmetry = []
    for pair in pairs:
        left = next(row for row in endpoint_rows if row["source_role"] == "endpoint_left" and (row["from_graph"], row["to_graph"]) == pair)
        right = next(row for row in endpoint_rows if row["source_role"] == "endpoint_right" and (row["from_graph"], row["to_graph"]) == pair)
        endpoint_symmetry.append({"from_graph": pair[0], "to_graph": pair[1], "absolute_delta_difference": abs(left["max_context_delta"] - right["max_context_delta"])})

    direct = direct_run["derived"]["maxima_by_volume"]
    direct_volumes = sorted(int(key) for key in direct)
    direct_d = [float(direct[str(volume)]["D_norm"]) for volume in direct_volumes]
    direct_delta = [float(direct[str(volume)]["delta_D_norm"]) for volume in direct_volumes]
    weighted = weighted_run["derived"]
    weighted_volumes = [int(row["volume"]) for row in weighted["summary_rows"] if float(row["amplitude"]) == 1.0]
    weighted_rows = [row for row in weighted["summary_rows"] if float(row["amplitude"]) == 1.0]
    weighted_rows.sort(key=lambda row: int(row["volume"]))
    weighted_d = [float(row["max_D_gibbs_normalized"]) for row in weighted_rows]
    weighted_delta = [float(row["max_delta_H_D_gibbs_normalized"]) for row in weighted_rows]
    direct_increasing = all(one < two for one, two in zip(direct_d, direct_d[1:]))
    direct_delta_increasing = all(one < two for one, two in zip(direct_delta, direct_delta[1:]))
    weighted_increasing = all(one < two for one, two in zip(weighted_d, weighted_d[1:]))
    weighted_delta_increasing = all(one < two for one, two in zip(weighted_delta, weighted_delta[1:]))
    os_decreasing = {role: all(one > two for one, two in zip(values, values[1:])) for role, values in sequences.items()}
    return {
        "os_sequences": sequences,
        "endpoint_symmetry": endpoint_symmetry,
        "direct_profile": {"volumes": direct_volumes, "D_norm": direct_d, "delta_D_norm": direct_delta},
        "source_weight_profile": {"volumes": weighted_volumes, "normalized_D_gibbs": weighted_d, "normalized_delta_H_D_gibbs": weighted_delta},
        "bridge_metrics": {
            "os_decreasing_by_role": os_decreasing,
            "all_os_roles_decrease": all(os_decreasing.values()),
            "direct_D_increasing": direct_increasing,
            "direct_delta_D_increasing": direct_delta_increasing,
            "source_weight_D_increasing": weighted_increasing,
            "source_weight_delta_H_D_increasing": weighted_delta_increasing,
            "mixed_finite_signal": all(os_decreasing.values()) and (direct_increasing or direct_delta_increasing or weighted_increasing or weighted_delta_increasing),
            "direct_D_last_first_ratio": direct_d[-1] / direct_d[0],
            "direct_delta_D_last_first_ratio": direct_delta[-1] / direct_delta[0],
            "source_weight_D_last_first_ratio": weighted_d[-1] / weighted_d[0],
            "source_weight_delta_H_D_last_first_ratio": weighted_delta[-1] / weighted_delta[0],
        },
    }


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    scope = manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", manifest["exploration_id"] == "EXP-001176" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001176/T-054", "provenance")
    check("claim firewall", manifest["claim_bearing"] is False and not scope["volume_uniform_direct_d_cauchy_closed"], [manifest["claim_bearing"], scope["volume_uniform_direct_d_cauchy_closed"]], "nonbearing/open", "scope")
    inputs = manifest["inputs"]
    os_run = read_input(inputs["direction_source_independent"], "EXP-001175")
    direct_run = read_input(inputs["extended_direct_independent"], "EXP-001169")
    weighted_run = read_input(inputs["source_weight_independent"], "EXP-001149")
    check("input provenance", True, list(inputs), "six committed upstream paths", "provenance")
    analysis = analyse(os_run, direct_run, weighted_run, manifest["fixture"])
    os_pairs = {(row.get("from_graph"), row.get("to_graph")) for row in os_run.get("comparisons", [])}
    os_roles = {row.get("source_role") for row in os_run.get("comparisons", [])}
    os_betas = {float(row.get("beta")) for row in os_run.get("comparisons", [])}
    expected_os_comparisons = len(os_pairs) * len(os_roles) * len(os_betas)
    check("OS role coverage", len(os_run.get("comparisons", [])) == expected_os_comparisons, len(os_run.get("comparisons", [])), expected_os_comparisons, "coverage")
    check("OS sequence coverage", all(len(values) == 2 for values in analysis["os_sequences"].values()), analysis["os_sequences"], "two nested pairs per role", "coverage")
    check("direct volume coverage", len(analysis["direct_profile"]["volumes"]) >= 2, analysis["direct_profile"]["volumes"], "at least two declared volumes", "coverage")
    check("source-weight volume coverage", len(analysis["source_weight_profile"]["volumes"]) >= 2, analysis["source_weight_profile"]["volumes"], "at least two declared volumes", "coverage")
    check("positive OS witness", all(value >= float(manifest["fixture"]["minimum_positive_witness"]) for values in analysis["os_sequences"].values() for value in values), analysis["os_sequences"], "positive", "adversarial")
    check("mixed finite signal", analysis["bridge_metrics"]["mixed_finite_signal"], analysis["bridge_metrics"], "OS decrease and direct growth visible", "route bridge")
    check("scope firewall", scope["finite_input_provenance_closed"] and scope["os_context_decay_diagnostic_closed"] and scope["direct_seminorm_growth_diagnostic_closed"] and scope["cross_route_bridge_closed"] and not scope["uniform_common_word_closed"] and not scope["volume_uniform_direct_d_cauchy_closed"] and not scope["volume_uniform_os_cauchy_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "finite route bridge", "scope")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-COMMON-WORD-DIRECT-ROUTE-BRIDGE", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, **analysis, "derived": {"finite_input_provenance_closed": True, "os_context_decay_diagnostic_closed": True, "direct_seminorm_growth_diagnostic_closed": True, "cross_route_bridge_closed": True, "uniform_common_word_closed": False, "volume_uniform_direct_d_cauchy_closed": False, "volume_uniform_os_cauchy_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False, "no_new_negative_result": True, "no_tier_change": True, "no_pdf": True}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        save_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INDEPENDENT COMMON-WORD-DIRECT-ROUTE-BRIDGE PASS {payload['passed']}/{payload['assertion_count']} mixed_signal={payload['bridge_metrics']['mixed_finite_signal']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
