#!/usr/bin/env python3
"""Integrated verifier for EXP-001197 source-local graph-norm transfer stress."""

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
SLUG = "pre_a_cp1_st8_q3lock_source_local_graph_norm_transfer_stress"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-source-local-graph-norm-transfer-stress-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R356.lean"
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
            stream.write("\n")
            stream.flush(); os.fsync(stream.fileno())
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
    command = "lake env lean Tect/R356.lean"
    lake = lake_path()
    if lake is None: return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R356.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-3000:]}


def key(row: dict[str, Any]) -> tuple[int, int, tuple[int, ...], str]:
    return int(row["volume"]), int(row["oscillator_dimension"]), tuple(int(site) for site in row["support"]), str(row["kind"])


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(ok), "actual": str(actual), "expected": str(expected)})
        if not ok: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001197" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001197/T-054/false")
    check("source files", PRIMARY.is_file() and INDEPENDENT.is_file() and LEAN.is_file(), [PRIMARY, INDEPENDENT, LEAN], "present")
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = ["volume_fixture", "source_support_fixture", "cutoff_case_fixture", "core_count_fixture", "graph_transfer_identity_fixture", "source_edge_count_fixture", "scope_fixture"]
    check("Lean markers", all(marker in lean_source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    check("independent source", sha256(PRIMARY) != sha256(INDEPENDENT), [sha256(PRIMARY), sha256(INDEPENDENT)], "distinct normalized SHA-256")

    with tempfile.TemporaryDirectory(prefix="q3-source-local-graph-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        p, i = primary.get("derived", {}), independent.get("derived", {})
        expected_scenarios = sum(len(fixture["oscillator_dimensions_by_volume"][str(v)]) * len(fixture["source_supports_by_volume"][str(v)]) * 2 for v in fixture["volume_values"])
        check("scenario count", p.get("scenario_count") == i.get("scenario_count") == expected_scenarios, [p.get("scenario_count"), i.get("scenario_count")], expected_scenarios)
        expected_core = sum(len([idx for idx in __import__("itertools").product(range(int(d)), repeat=int(v)) if sum(idx) <= int(fixture["core_total_occupation"])]) for v in fixture["volume_values"] for d in fixture["oscillator_dimensions_by_volume"][str(v)] for _ in fixture["source_supports_by_volume"][str(v)] for _ in (0, 1))
        check("core row count", p.get("core_row_count") == i.get("core_row_count") == expected_core, [p.get("core_row_count"), i.get("core_row_count")], expected_core)
        p_rows = {key(row): row for row in p.get("summary_rows", [])}
        i_rows = {key(row): row for row in i.get("summary_rows", [])}
        check("summary keys", set(p_rows) == set(i_rows) and len(p_rows) == expected_scenarios, [len(p_rows), len(i_rows)], expected_scenarios)
        tolerance = float(fixture["agreement_tolerance"])
        numeric = ("form_constant", "graph_constant", "commutator_constant")
        for row_key in sorted(p_rows):
            left, right = p_rows[row_key], i_rows[row_key]
            check(f"support metadata {row_key}", left.get("internal_edges") == right.get("internal_edges"), [left.get("internal_edges"), right.get("internal_edges")], "equal")
            for field in numeric:
                check(f"lane {field} {row_key}", abs(float(left[field]) - float(right[field])) <= tolerance * (1.0 + abs(float(left[field]))), [left[field], right[field]], f"within {tolerance}")
            check(f"lane core count {row_key}", int(left["core_count"]) == int(right["core_count"]), [left["core_count"], right["core_count"]], "equal")
        check("cutoff sequence", [int(row["dimension"]) for row in p.get("cutoff_edge_commutator_rows", [])] == [int(value) for value in fixture["oscillator_dimensions_by_volume"]["2"]], p.get("cutoff_edge_commutator_rows"), "manifest dimensions")
        check("cutoff agreement", abs(float(p.get("cutoff_commutator_growth", 0.0)) - float(i.get("cutoff_commutator_growth", 0.0))) <= tolerance, [p.get("cutoff_commutator_growth"), i.get("cutoff_commutator_growth")], f"within {tolerance}")
        check("finite transfer scope", all(p.get(name) is True and i.get(name) is True for name in ("finite_source_graph_form_rows_closed", "finite_source_graph_norm_rows_closed", "finite_source_commutator_rows_closed", "explicit_polynomial_core_rows_closed")), [p, i], "finite rows closed")
        check("uniformity firewall", all(p.get(name) is False and i.get(name) is False for name in ("uniform_common_core_graph_bound_closed", "uniform_commutator_bound_closed", "cutoff_removal_closed", "common_alpha_closed", "qft_promoted")), [p, i], "analytic/QFT gates open")
        check("cutoff diagnostic", float(p.get("cutoff_commutator_growth", 0.0)) >= float(fixture["cutoff_growth_threshold"]), p.get("cutoff_commutator_growth"), f">={fixture['cutoff_growth_threshold']}")

    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-SOURCE-LOCAL-GRAPH-NORM-TRANSFER-STRESS", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(checks), "assertions": checks, "lean": lean, "boundary": scope, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN)}
    }


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--no-store", action="store_true"); parser.add_argument("--skip-lean", action="store_true"); args = parser.parse_args()
    if args.skip_lean: raise SystemExit("skip-lean is not allowed for the integrated proof checkpoint")
    payload = run()
    if not args.no_store: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED SOURCE-LOCAL-GRAPH-NORM-TRANSFER PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__": raise SystemExit(main())