#!/usr/bin/env python3
"""Integrated verifier for EXP-001079."""

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
SLUG = "pre-a-cp1-st8-q3lock-dual-state-fifth-moment-modular-cutoff-obstruction"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
LEAN = REPO / "verification/lean/Tect/R261.lean"
LEAN_ROOT = REPO / "verification/lean"
PREVIOUS = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-projected-delta-d-third-coefficient-"
    "gibbs-weighted-noncommutative-moment-transfer-obstruction-manifest.json"
)
DEFAULT_OUTPUT = (
    REPO / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-26-primary-{SLUG}"
    / "integrated.json"
)
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run(
        [str(PYTHON), "-X", "utf8", str(script), "--output", str(output)],
        cwd=REPO,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


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
    lake = lake_path()
    command = "lake env lean Tect/R261.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R261.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001079" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001079/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("previous authority", previous["exploration_id"] == "EXP-001078" and previous["scope"]["finite_gibbs_obstruction_closed"] is True, previous["exploration_id"], "EXP-001078 finite Gibbs obstruction")
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = [
        "gibbs_ratio_first", "gibbs_ratio_second", "gibbs_ratio_third",
        "reference_moment_first", "reference_moment_second", "reference_moment_third",
        "dual_moment_first", "dual_moment_second", "dual_moment_third",
        "tail_first", "tail_second", "tail_third",
        "reference_ceiling_first", "reference_ceiling_second", "reference_ceiling_third",
        "tail_floor_first", "tail_floor_second", "tail_floor_third",
        "relative_bound_fixture", "scope_fixture",
    ]
    check("Lean source", LEAN.is_file() and all(marker in lean_source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="dual-state-cutoff-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("positive totals", primary.get("passed", 0) > 0 and independent.get("passed", 0) > 0, [primary.get("passed"), independent.get("passed")], ">0")
        pderived = primary.get("derived", {})
        iderived = independent.get("derived", {})
        for key in ("gibbs_ratio_exponent", "reference_moment", "dual_moment", "opposite_tail", "relative_squared_norm"):
            check(f"lane agreement {key}", str(pderived.get(key)) == str(iderived.get(key)), [pderived.get(key), iderived.get(key)], "equal")
        check("fixture count", len(pderived.get("reference_moment", [])) == len(fixture["L_values"]) and len(pderived.get("dual_moment", [])) == len(fixture["L_values"]) and len(pderived.get("opposite_tail", [])) == len(fixture["L_values"]), pderived, "three L fixtures")
        check("L fixture", [int(value) for value in pderived.get("L_values", [])] == fixture["L_values"], pderived.get("L_values"), fixture["L_values"])
        check("Gibbs exponent fixture", pderived.get("gibbs_ratio_exponent") == fixture["gibbs_ratio_exponent"], pderived.get("gibbs_ratio_exponent"), fixture["gibbs_ratio_exponent"])
        check("cutoff fixture", int(pderived.get("cutoff_R")) == fixture["cutoff_R"], pderived.get("cutoff_R"), fixture["cutoff_R"])

    open_keys = tuple(key for key, value in scope.items() if isinstance(value, bool) and key.endswith("_closed") and key not in ("finite_dual_state_obstruction_closed", "one_sided_moment_shortcut_refuted", "conditional_dual_tail_theorem_identified"))
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "actual Q3 and QFT gates open")
    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R261.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS")
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-DUAL-STATE-FIFTH-MOMENT-MODULAR-CUTOFF-OBSTRUCTION",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "lean": lean,
        "boundary": scope,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {
            "primary_sha256": sha256(PRIMARY),
            "independent_sha256": sha256(INDEPENDENT),
            "manifest_sha256": sha256(MANIFEST),
            "lean_sha256": sha256(LEAN),
            "previous_manifest_sha256": sha256(PREVIOUS),
        },
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED DUAL-STATE FIFTH-MOMENT CUTOFF OBSTRUCTION PASS {len(rows)}/{len(rows)}; Lean={lean['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
