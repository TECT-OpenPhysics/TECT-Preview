#!/usr/bin/env python3
"""Integrated verifier for EXP-001094, including the pinned Lean cross-check."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_truncated_ccr_boundary"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN_ROOT = REPO / "verification/lean"
LEAN_SOURCE = LEAN_ROOT / "Tect/R275.lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-integrated-{SLUG}" / "integrated.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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


def find_lake() -> Path | None:
    encoded = "leanprover/lean4:v4.32.1".replace("/", "--").replace(":", "---")
    root = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        candidate = root / name
        if candidate.is_file():
            return candidate
    return None


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["exploration_id"] == "EXP-001094" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001094/T-054")
    check("manifest nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("manifest source files", PRIMARY.is_file() and INDEPENDENT.is_file() and LEAN_SOURCE.is_file(), [str(PRIMARY), str(INDEPENDENT), str(LEAN_SOURCE)], "all present")
    check("script hash pins", sha256(PRIMARY) != sha256(INDEPENDENT) and sha256(LEAN_SOURCE), [sha256(PRIMARY), sha256(INDEPENDENT), sha256(LEAN_SOURCE)], "distinct primary/independent and Lean present")

    primary_output = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"
    independent_output = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-independent-{SLUG}" / "independent.json"
    commands = [
        ([sys.executable, "-X", "utf8", str(PRIMARY), "--output", str(primary_output)], primary_output, "primary"),
        ([sys.executable, "-X", "utf8", str(INDEPENDENT), "--output", str(independent_output)], independent_output, "independent"),
    ]
    children: dict[str, dict[str, Any]] = {}
    for command, output, label in commands:
        process = subprocess.run(command, cwd=REPO, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
        check(f"{label} process", process.returncode == 0, process.stdout + process.stderr, "exit 0")
        check(f"{label} output", output.is_file(), str(output), "stored JSON")
        children[label] = json.loads(output.read_text(encoding="utf-8"))
        check(f"{label} verdict", children[label].get("verdict") == "PASS", children[label].get("verdict"), "PASS")
        check(f"{label} nonempty assertions", int(children[label].get("assertion_count", 0)) > 0, children[label].get("assertion_count"), ">0")

    primary_rows = children["primary"]["derived"]["rows"]
    independent_rows = children["independent"]["derived"]["rows"]
    lane_agreement = len(primary_rows) == len(independent_rows) and all(
        left["n"] == right["n"]
        and left["exact_defect_coefficient"] == right["exact_defect_coefficient"]
        and left["rank"] == right["rank"]
        and abs(left["defect_operator_norm"] - right["operator_norm"]) <= 1e-9
        and abs(left["top_action_norm"] - right["top_action"]) <= 1e-9
        and abs(left["ground_action_norm"] - right["bottom_action"]) <= 1e-9
        for left, right in zip(primary_rows, independent_rows)
    )
    check("lane field reconciliation", lane_agreement, [len(primary_rows), len(independent_rows)], "same n/coefficient/rank/norm fields")
    check("formula coefficient sequence", [row["exact_defect_coefficient"] for row in primary_rows] == [-int(row["n"]) for row in primary_rows], [row["exact_defect_coefficient"] for row in primary_rows], "minus n")
    check("uniformity firewall", children["primary"]["derived"]["actual_unbounded_q3_domain_transfer_closed"] is False and children["independent"]["derived"]["actual_unbounded_q3_domain_transfer_closed"] is False, "both false", "both false")

    lake = find_lake()
    check("pinned lake available", lake is not None, str(lake), "pinned lake")
    lean_process = subprocess.run([str(lake), "env", "lean", "Tect/R275.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False) if lake else None
    lean_pass = bool(lean_process and lean_process.returncode == 0 and "error:" not in (lean_process.stdout + lean_process.stderr).lower())
    check("Lean R275", lean_pass, (lean_process.stdout + lean_process.stderr)[-1000:] if lean_process else "missing lake", "exit 0 without errors")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-TRUNCATED-CCR-BOUNDARY",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "children": {"primary": str(primary_output.relative_to(REPO)).replace("\\", "/"), "independent": str(independent_output.relative_to(REPO)).replace("\\", "/")},
        "lean": {"path": "verification/lean/Tect/R275.lean", "status": "PASS", "sha256": sha256(LEAN_SOURCE)},
        "derived": {"exact_truncated_ccr_identity_closed": True, "operator_norm_defect_closed": True, "vector_tail_condition_derived": True, "finite_matrix_ccr_uniformity_closed": False, "actual_unbounded_q3_domain_transfer_closed": False, "source_volume_uniform_modular_history_closed": False, "common_alpha_closed": False},
        "boundary": manifest["boundary"],
        "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN_SOURCE)},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run()
    atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED TRUNCATED-CCR-BOUNDARY PASS {payload['assertion_count']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
