#!/usr/bin/env python3
"""Integrated verifier for the Q3 matching-layer common-core envelope."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-common-core-matching-layer-envelope-manifest.json"
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_common_core_matching_layer_envelope.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_common_core_matching_layer_envelope_independent.py"
LEAN = REPO / "verification/lean/Tect/R208.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-24-primary-pre-a-cp1-st8-q3lock-common-core-matching-layer-envelope/integrated.json"
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


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    result = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    return result, json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}


def pinned_lake() -> Path | None:
    toolchain = json.loads((REPO / "verification/lean/registry.json").read_text(encoding="utf-8"))["toolchain"]["toolchain"]
    encoded = toolchain.replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file():
            return candidate / name
    return Path(shutil.which("lake")) if shutil.which("lake") else None


def lean_run() -> dict[str, Any]:
    lake = pinned_lake()
    if lake is None:
        return {"status": "UNAVAILABLE", "command": "lake env lean Tect/R208.lean", "output": "pinned lake executable not found"}
    result = subprocess.run([str(lake), "env", "lean", "Tect/R208.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (result.stdout + "\n" + result.stderr).strip()
    return {"status": "PASS" if result.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": "lake env lean Tect/R208.lean", "returncode": result.returncode, "output": output[-2000:]}


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

    check("identity", manifest["exploration_id"] == "EXP-001024" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001024/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no formal promotion", manifest["formal_integration"] == {"events": [], "results": [], "negatives": [], "no_new_result": True, "no_new_negative": True, "no_pdf": True}, manifest["formal_integration"], "no event/result/negative/PDF")
    check("Lean source exists", LEAN.is_file(), str(LEAN), True)
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    check("Lean markers", all(marker in source for marker in manifest["lean_crosscheck"]["theorem_markers"]), manifest["lean_crosscheck"]["theorem_markers"], "present")
    check("Lean forbidden tokens absent", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    boundary = (manifest["boundary"] + " " + manifest["qft_interface"]["not_closed"] + " " + manifest["tect_boundary"]).lower()
    check("exhaustion boundary", "exhaustion" in boundary and "not" in boundary, boundary, "explicit open exhaustion")
    check("KMS boundary", "kms" in boundary and "not" in boundary, boundary, "explicit open KMS")
    check("TECT firewall", "heat_root_incidence" in boundary and "not" in boundary, boundary, "explicit production-owner boundary")

    with tempfile.TemporaryDirectory(prefix="matching-layer-integrated-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("positive assertion totals", primary.get("total", 0) > 0 and independent.get("total", 0) > 0, [primary.get("total"), independent.get("total")], ">0")
        for key in ("box_vertices", "box_edges", "layer_count", "layer_sizes", "C_match", "endpoint_exponent", "finite_common_core_induced_norm_closed", "volume_uniform_split_envelope_closed", "exhaustion_cauchy_closed", "common_alpha_closed", "qft_kms_closed"):
            check(f"lane agreement {key}", primary.get("derived", {}).get(key) == independent.get("derived", {}).get(key), [primary.get("derived", {}).get(key), independent.get("derived", {}).get(key)], "equal")

    lean_result = {"status": "SKIPPED", "command": "lake env lean Tect/R208.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean_result["status"] == "PASS", lean_result, "PASS")
    payload = {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-COMMON-CORE-MATCHING-LAYER-ENVELOPE", "claim_id": manifest["claim_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "lean": lean_result, "boundary": manifest["boundary"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED MATCHING-LAYER PASS {len(rows)}/{len(rows)}; Lean={lean_result['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
