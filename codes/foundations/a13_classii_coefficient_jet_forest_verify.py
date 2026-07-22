#!/usr/bin/env python3
"""Integrated non-importing verifier for the A13 jet forest subproof."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
__first_issued__ = "2026-07-22"
__version_issued__ = "2026-07-22"

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
DEFAULT_MANIFEST = CLAIM / "classii_coefficient_jet_forest_manifest.json"
DEFAULT_OUTPUT = (
    CLAIM
    / "runs"
    / "2026-07-22-integrated-coefficient-jet-forest-classification"
    / "result.json"
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    value.update(path.read_bytes())
    return value.hexdigest()


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name, suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def add(
    rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any
) -> None:
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def execute(script: Path, manifest: Path, output: Path) -> dict[str, Any]:
    process = subprocess.run(
        [
            sys.executable,
            str(script),
            "--manifest",
            str(manifest),
            "--output",
            str(output),
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if process.returncode != 0:
        raise RuntimeError(
            f"{script.name} failed ({process.returncode})\n"
            f"STDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
        )
    return json.loads(output.read_text(encoding="utf-8"))


def run(manifest_path: Path, output_path: Path, skip_execute: bool) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    for key, source in manifest["sources"].items():
        path = REPO / source["path"]
        actual = digest(path)
        add(rows, f"source_{key}_hash", actual == source["sha256"], actual, source["sha256"])

    primary_output = REPO / manifest["run_contract"]["primary_output"]
    independent_output = REPO / manifest["run_contract"]["independent_output"]
    primary_script = REPO / manifest["sources"]["primary"]["path"]
    independent_script = REPO / manifest["sources"]["independent"]["path"]

    if skip_execute:
        primary = json.loads(primary_output.read_text(encoding="utf-8"))
        independent = json.loads(independent_output.read_text(encoding="utf-8"))
    else:
        primary = execute(primary_script, manifest_path, primary_output)
        independent = execute(independent_script, manifest_path, independent_output)

    expected_primary = int(manifest["run_contract"]["primary_assertions"])
    expected_independent = int(manifest["run_contract"]["independent_assertions"])
    add(
        rows,
        "primary_verdict",
        primary.get("verdict") == "A13-CLASSII-COEFFICIENT-JET-FOREST-PRIMARY-PASS",
        primary.get("verdict"),
        "A13-CLASSII-COEFFICIENT-JET-FOREST-PRIMARY-PASS",
    )
    add(
        rows,
        "independent_verdict",
        independent.get("verdict") == "A13-CLASSII-COEFFICIENT-JET-FOREST-INDEPENDENT-PASS",
        independent.get("verdict"),
        "A13-CLASSII-COEFFICIENT-JET-FOREST-INDEPENDENT-PASS",
    )
    add(
        rows,
        "primary_assertion_count",
        primary["summary"]["total"] == expected_primary,
        primary["summary"]["total"],
        expected_primary,
    )
    add(
        rows,
        "independent_assertion_count",
        independent["summary"]["total"] == expected_independent,
        independent["summary"]["total"],
        expected_independent,
    )
    add(rows, "primary_zero_failures", primary["summary"]["failed"] == 0, primary["summary"]["failed"], 0)
    add(rows, "independent_zero_failures", independent["summary"]["failed"] == 0, independent["summary"]["failed"], 0)

    primary_counts = primary["derived"]["contraction_counts"]
    oracles = manifest["oracles"]["contraction_counts"]
    add(rows, "primary_counts_equal_manifest", primary_counts == oracles, primary_counts, oracles)
    projection_oracles = {
        "x_h2": {"1": 2.0, "3": 1.0},
        "h2_h2": {"0": 2.0, "2": 4.0, "4": 1.0},
        "x2_h2": {"0": 2.0, "2": 5.0, "4": 1.0},
        "x_h3": {"2": 3.0, "4": 1.0},
    }
    maximum_projection_error = 0.0
    projections = independent["derived"]["hermite_projections"]
    for name, expected in projection_oracles.items():
        for degree, target in expected.items():
            maximum_projection_error = max(
                maximum_projection_error,
                abs(float(projections[name][degree]) - target),
            )
    tolerance = float(manifest["integrated_audit"]["cross_tolerance"])
    add(
        rows,
        "independent_hermite_coefficients_match_forest",
        maximum_projection_error < tolerance,
        maximum_projection_error,
        f"<{tolerance}",
    )

    primary_gradient = primary["derived"]["mixed_gradient_covariance"]
    primary_gradient_max = max(abs(float(value)) for row in primary_gradient for value in row)
    independent_gradient = float(independent["derived"]["paired_gradient_norm"])
    add(
        rows,
        "cross_even_gradient_zero",
        primary_gradient_max < tolerance and independent_gradient < tolerance,
        [primary_gradient_max, independent_gradient],
        f"both <{tolerance}",
    )
    add(
        rows,
        "cross_asymmetric_controls_nonzero",
        float(primary["derived"]["asymmetric_gradient_norm"])
        > float(manifest["audit"]["asymmetric_minimum"])
        and float(independent["derived"]["asymmetric_gradient_norm"])
        > float(manifest["independent_audit"]["asymmetric_minimum"]),
        [
            primary["derived"]["asymmetric_gradient_norm"],
            independent["derived"]["asymmetric_gradient_norm"],
        ],
        "both nonzero above registered minima",
    )

    forest = primary["derived"]["second_zero_chaos_forest"]
    complete_values = [
        float(forest["sector_totals"][parent]["COMPLETE"])
        for parent in ("X_PI_X_Q", "PI_XX_Q")
    ]
    cone_values = [
        float(forest["positive_cone"][parent])
        for parent in ("X_PI_X_Q", "PI_XX_Q")
    ]
    add(rows, "cross_complete_p0_zero", max(map(abs, complete_values)) < tolerance, complete_values, f"absolute<{tolerance}")
    add(rows, "cross_localized_cones_negative", all(value < 0.0 for value in cone_values), cone_values, "both negative")

    own_expected = int(manifest["run_contract"]["integrated_own_assertions"])
    add(
        rows,
        "integrated_own_assertion_count",
        len(rows) + 1 == own_expected,
        len(rows) + 1,
        own_expected,
    )
    failures = [row for row in rows if row["status"] != "PASS"]
    passed = len(rows) - len(failures)
    total_aggregate = (
        primary["summary"]["total"] + independent["summary"]["total"] + len(rows)
    )
    expected_aggregate = int(manifest["run_contract"]["expected_total_assertions"])
    aggregate_ok = total_aggregate == expected_aggregate
    if not aggregate_ok:
        failures.append(
            {
                "name": "aggregate_assertion_count",
                "status": "FAIL",
                "actual": total_aggregate,
                "expected": expected_aggregate,
            }
        )

    payload = {
        "schema": "tect/a13-classii-coefficient-jet-forest-integrated-result/1.0",
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "platform": platform.platform(),
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "manifest_sha256": digest(manifest_path),
        "executed_children": not skip_execute,
        "child_summaries": {
            "primary": primary["summary"],
            "independent": independent["summary"],
        },
        "assertions": rows,
        "summary": {
            "passed": passed,
            "total": len(rows),
            "failed": len([row for row in rows if row["status"] != "PASS"]),
            "aggregate_total": total_aggregate,
            "aggregate_expected": expected_aggregate,
        },
        "verdict": (
            "A13-CLASSII-COEFFICIENT-JET-FOREST-INTEGRATED-PASS"
            if not failures
            else "FAIL"
        ),
        "consequence": manifest["consequence"],
        "honesty_boundary": manifest["honesty_boundary"],
    }
    atomic_json(output_path, payload)
    if failures:
        print(f"FAIL: integrated ({len(failures)} issue(s))")
        for failure in failures:
            print(f" - {failure['name']}: {failure['actual']}")
        return 1
    print(
        f"PASS: integrated ({passed}/{len(rows)} own; "
        f"aggregate {total_aggregate}/{expected_aggregate})"
    )
    print("A13-CLASSII-COEFFICIENT-JET-FOREST-INTEGRATED-PASS")
    print(f"Evidence: {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--skip-execute", action="store_true")
    arguments = parser.parse_args()
    return run(
        arguments.manifest.resolve(),
        arguments.output.resolve(),
        arguments.skip_execute,
    )


if __name__ == "__main__":
    raise SystemExit(main())
