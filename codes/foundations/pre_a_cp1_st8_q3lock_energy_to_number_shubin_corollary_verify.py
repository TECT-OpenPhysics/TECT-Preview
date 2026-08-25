#!/usr/bin/env python3
"""Integrated verifier for EXP-001110."""

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
SLUG = "pre_a_cp1_st8_q3lock_energy_to_number_shubin_corollary"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
PRIMARY = REPO / "codes/foundations" / f"{SLUG}.py"
INDEPENDENT = REPO / "codes/foundations" / f"{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R282.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-integrated-{SLUG}" / "integrated.json"
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
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def lake_path() -> Path | None:
    registry = json.loads((REPO / "verification/lean/registry.json").read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file():
            return candidate / name
    found = shutil.which("lake")
    return Path(found) if found else None


def lean_run() -> dict[str, Any]:
    command = "lake env lean Tect/R282.lean"
    lake = lake_path()
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R282.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def close(left: Any, right: Any, tolerance: float = 1.0e-12) -> bool:
    return abs(float(left) - float(right)) <= tolerance * (1.0 + abs(float(left)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    scope = manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001110" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001110/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("Lean source", LEAN.is_file() and all(token in LEAN.read_text(encoding="utf-8") for token in ("young_with_equal_scales", "energy_to_number_form_constant", "top_tail_decay", "history_top_tail_decay", "scope_fixture")), LEAN, "R282 declarations")
    check("Lean forbidden", not any(token in LEAN.read_text(encoding="utf-8").split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    check("scope firewall", scope["energy_to_number_form_corollary_closed"] and scope["registered_gibbs_top_tail_closed"] and scope["registered_split_history_top_tail_closed"] and not scope["all_shape_exhaustion_top_tail_closed"] and not scope["common_alpha_closed"], scope, "registered scope with open QFT successors")

    with tempfile.TemporaryDirectory(prefix="energy-to-number-shubin-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        p_rows, i_rows = primary["derived"]["component_rows"], independent["derived"]["component_rows"]
        check("component row count", len(p_rows) == len(i_rows), [len(p_rows), len(i_rows)], "equal")
        for p_row, i_row in zip(p_rows, i_rows):
            check(f"component {p_row['components']} agreement", p_row == i_row, [p_row, i_row], "equal")
        check("coefficient sum agreement", primary["derived"]["eight_component_coefficient_l1"] == independent["derived"]["eight_component_coefficient_l1"] == 87496, [primary["derived"]["eight_component_coefficient_l1"], independent["derived"]["eight_component_coefficient_l1"]], "87496")
        check("static tail agreement", primary["derived"]["static_tail_rows"] == independent["derived"]["static_tail_rows"], [primary["derived"]["static_tail_rows"], independent["derived"]["static_tail_rows"]], "equal")
        p_history, i_history = primary["derived"]["history_tail_rows"], independent["derived"]["history_tail_rows"]
        check("history row count", len(p_history) == len(i_history), [len(p_history), len(i_history)], "equal")
        for p_row, i_row in zip(p_history, i_history):
            check(f"history cutoff {p_row['cutoff']} agreement", p_row["cutoff"] == i_row["cutoff"] and close(p_row["bound"], i_row["bound"]), [p_row, i_row], "within tolerance")
        check("derived flags", all(primary["derived"][key] and independent["derived"][key] for key in ("energy_to_number_form_corollary_closed", "registered_gibbs_top_tail_closed", "registered_split_history_top_tail_closed")), primary["derived"], "closed")

    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-ENERGY-TO-NUMBER-SHUBIN-COROLLARY",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "lean": lean,
        "boundary": scope,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN)}
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED ENERGY-TO-NUMBER-SHUBIN-COROLLARY PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
