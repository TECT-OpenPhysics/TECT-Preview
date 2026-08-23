#!/usr/bin/env python3
"""Integrated verifier for the weighted-conjugation envelope package."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-weighted-conjugation-envelope-manifest.json"
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_weighted_conjugation_envelope.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_weighted_conjugation_envelope_independent.py"
LEAN = REPO / "verification/lean/Tect/R207.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-24-primary-pre-a-cp1-st8-q3lock-weighted-conjugation-envelope/integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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


def run_child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    completed = subprocess.run(
        [str(PYTHON), "-X", "utf8", str(script), "--output", str(output)],
        cwd=REPO,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return completed, payload


def pinned_lake() -> Path | None:
    toolchain = json.loads((REPO / "verification/lean/registry.json").read_text(encoding="utf-8"))["toolchain"]["toolchain"]
    encoded = toolchain.replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file():
            return candidate / name
    return Path(shutil.which("lake")) if shutil.which("lake") else None


def run_lean() -> dict[str, Any]:
    lake = pinned_lake()
    if lake is None:
        return {"status": "UNAVAILABLE", "command": "lake env lean Tect/R207.lean", "output": "pinned lake executable not found"}
    completed = subprocess.run(
        [str(lake), "env", "lean", "Tect/R207.lean"],
        cwd=LEAN_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    return {
        "status": "PASS" if completed.returncode == 0 and "error:" not in (completed.stdout + completed.stderr).lower() else "FAIL",
        "command": "lake env lean Tect/R207.lean",
        "returncode": completed.returncode,
        "output": (completed.stdout + "\n" + completed.stderr).strip()[-2000:],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001023" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001023/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no formal promotion", manifest["formal_integration"] == {"events": [], "results": [], "negatives": [], "no_new_result": True, "no_new_negative": True, "no_pdf": True}, manifest["formal_integration"], "no event/result/negative/PDF")
    check("Lean source exists", LEAN.is_file(), str(LEAN), True)
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    check("Lean theorem markers", all(marker in source for marker in manifest["lean_crosscheck"]["theorem_markers"]), manifest["lean_crosscheck"]["theorem_markers"], "present")
    check("Lean forbidden tokens absent", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    check("adversarial review registered", len(manifest["adversarial_review"]) == 7, len(manifest["adversarial_review"]), 7)
    boundary = (manifest["boundary"] + " " + manifest["qft_interface"]["not_closed"] + " " + manifest["tect_boundary"]).lower()
    check("thermodynamic boundary", "thermodynamic" in boundary and "not" in boundary, boundary, "explicit open limit")
    check("QFT boundary", "kms" in boundary and "not" in boundary, boundary, "explicit KMS boundary")
    check("TECT firewall", "heat_root_incidence" in boundary and "not" in boundary, boundary, "explicit production-owner boundary")

    with tempfile.TemporaryDirectory(prefix="weighted-conjugation-integrated-") as temporary:
        primary_out = Path(temporary) / "primary.json"
        independent_out = Path(temporary) / "independent.json"
        primary_process, primary = run_child(PRIMARY, primary_out)
        independent_process, independent = run_child(INDEPENDENT, independent_out)
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("assertion totals positive", primary.get("total", 0) > 0 and independent.get("total", 0) > 0, [primary.get("total"), independent.get("total")], ">0")
        for key in ("M_left", "M_common", "weighted_conjugation_closed", "finite_two_orientation_fixture_closed", "thermodynamic_common_alpha_closed", "qft_kms_closed"):
            check(f"derived agreement {key}", primary.get("derived", {}).get(key) == independent.get("derived", {}).get(key), [primary.get("derived", {}).get(key), independent.get("derived", {}).get(key)], "equal")
        check("omitted orientation mutation caught", any(row.get("name") == "omitted reverse orientation fails" for row in primary.get("assertions", [])) and any(row.get("name") == "omitted reverse orientation fails" for row in independent.get("assertions", [])), True, True)

    lean_result = {"status": "SKIPPED", "command": "lake env lean Tect/R207.lean"} if args.skip_lean else run_lean()
    check("Lean compile", args.skip_lean or lean_result["status"] == "PASS", lean_result, "PASS")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-WEIGHTED-CONJUGATION-ENVELOPE",
        "claim_id": manifest["claim_id"],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "lean": lean_result,
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED WEIGHTED-CONJUGATION PASS {len(rows)}/{len(rows)}; Lean={lean_result['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
