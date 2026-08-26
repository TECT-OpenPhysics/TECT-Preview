#!/usr/bin/env python3
"""Integrated verifier for EXP-001198 high-cutoff source-edge stress."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_source_edge_high_cutoff_commutator_stress"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-source-edge-high-cutoff-commutator-stress-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R357.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-29-integrated-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def lake_path() -> Path | None:
    registry = json.loads((REPO / "verification/lean/registry.json").read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file(): return candidate / name
    found = shutil.which("lake")
    return Path(found) if found else None


def lean_run() -> dict[str, Any]:
    command = "lake env lean Tect/R357.lean"; lake = lake_path()
    if lake is None: return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R357.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-3000:]}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []
    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(ok), "actual": str(actual), "expected": str(expected)})
        if not ok: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
    check("identity", manifest["exploration_id"] == "EXP-001198" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001198/T-054/false")
    check("source files", PRIMARY.is_file() and INDEPENDENT.is_file() and LEAN.is_file(), [PRIMARY, INDEPENDENT, LEAN], "present")
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""; markers = ["dimension_count_fixture", "slope_first_fixture", "slope_last_fixture", "high_core_vector_count_fixture", "source_edge_count_fixture", "scope_fixture"]
    check("Lean markers", all(marker in source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    check("independent source", sha256(PRIMARY) != sha256(INDEPENDENT), [sha256(PRIMARY), sha256(INDEPENDENT)], "distinct normalized SHA-256")
    with tempfile.TemporaryDirectory(prefix="q3-source-edge-high-cutoff-") as temporary:
        pp, primary = child(PRIMARY, Path(temporary) / "primary.json"); ip, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", pp.returncode == 0 and primary.get("verdict") == "PASS", pp.stdout + pp.stderr, "PASS")
        check("independent child", ip.returncode == 0 and independent.get("verdict") == "PASS", ip.stdout + ip.stderr, "PASS")
        p, i = primary.get("derived", {}), independent.get("derived", {})
        expected_dimensions = [int(value) for value in fixture["oscillator_dimensions"]]
        check("dimension count", p.get("dimension_count") == i.get("dimension_count") == len(expected_dimensions), [p.get("dimension_count"), i.get("dimension_count")], len(expected_dimensions))
        expected_vectors = len(expected_dimensions) * len(fixture["high_core_indices"])
        check("vector row count", p.get("vector_row_count") == i.get("vector_row_count") == expected_vectors, [p.get("vector_row_count"), i.get("vector_row_count")], expected_vectors)
        p_rows = {int(row["dimension"]): row for row in p.get("high_cutoff_rows", [])}; i_rows = {int(row["dimension"]): row for row in i.get("high_cutoff_rows", [])}
        check("dimension keys", set(p_rows) == set(i_rows) == set(expected_dimensions), [sorted(p_rows), sorted(i_rows)], expected_dimensions)
        tolerance = float(fixture["agreement_tolerance"])
        for dimension in expected_dimensions:
            left, right = p_rows[dimension], i_rows[dimension]
            for field in ("global_graph_constant", "form_constant", "global_commutator_constant", "diagonal_lower_bound"):
                check(f"lane {field} d={dimension}", abs(float(left[field]) - float(right[field])) <= tolerance * (1.0 + abs(float(left[field]))), [left[field], right[field]], f"within {tolerance}")
            lv = {item["label"]: item for item in left["vectors"]}; rv = {item["label"]: item for item in right["vectors"]}
            check(f"vector labels d={dimension}", set(lv) == set(rv), [set(lv), set(rv)], set(fixture["high_core_indices"]))
            for label in lv:
                check(f"lane vector d={dimension} {label}", abs(float(lv[label]["ratio"]) - float(rv[label]["ratio"])) <= tolerance * (1.0 + abs(float(lv[label]["ratio"]))), [lv[label]["ratio"], rv[label]["ratio"]], f"within {tolerance}")
        check("finite route scope", all(p.get(name) is True and i.get(name) is True for name in ("finite_high_cutoff_rows_closed", "explicit_high_core_lower_bound_rows_closed", "cutoff_growth_diagnostic_closed")), [p, i], "finite rows closed")
        check("QFT firewall", all(p.get(name) is False and i.get(name) is False for name in ("uniform_commutator_bound_closed", "cutoff_removal_closed", "unbounded_common_core_closed", "common_alpha_closed", "qft_promoted")), [p, i], "analytic/QFT gates open")
        check("linear diagnostic", float(p.get("diagonal_growth_ratio", 0.0)) >= 1.0 and float(i.get("diagonal_growth_ratio", 0.0)) >= 1.0, [p.get("diagonal_growth_ratio"), i.get("diagonal_growth_ratio")], ">=1")
    lean = lean_run(); check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-SOURCE-EDGE-HIGH-CUTOFF-COMMUTATOR-STRESS", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(checks), "assertions": checks, "lean": lean, "boundary": scope, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN)}}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--no-store", action="store_true"); parser.add_argument("--skip-lean", action="store_true"); args = parser.parse_args()
    if args.skip_lean: raise SystemExit("skip-lean is not allowed for the integrated proof checkpoint")
    payload = run()
    if not args.no_store: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED SOURCE-EDGE-HIGH-CUTOFF-COMMUTATOR PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__": raise SystemExit(main())