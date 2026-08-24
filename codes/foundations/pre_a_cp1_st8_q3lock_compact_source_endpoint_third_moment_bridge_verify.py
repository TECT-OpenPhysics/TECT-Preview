#!/usr/bin/env python3
"""Integrated primary/independent/Lean verifier for EXP-001061."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-compact-source-endpoint-third-moment-bridge-manifest.json"
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_compact_source_endpoint_third_moment_bridge.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_compact_source_endpoint_third_moment_bridge_independent.py"
LEAN = REPO / "verification/lean/Tect/R243.lean"
LEAN_ROOT = REPO / "verification/lean"
GATES = REPO / "claims/GATES.md"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-local-measured-renyi-semiclassical-doublet-route-split-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    "2026-08-25-primary-pre-a-cp1-st8-q3lock-compact-source-endpoint-third-moment-bridge/integrated.json"
)
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
    command = "lake env lean Tect/R243.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run(
        [str(lake), "env", "lean", "Tect/R243.lean"],
        cwd=LEAN_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    output = (process.stdout + "\n" + process.stderr).strip()
    return {
        "status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL",
        "command": command,
        "returncode": process.returncode,
        "output": output[-2000:],
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
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001061" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001061/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    model = manifest["model"]
    check(
        "model bridge",
        all(
            token in model[key]
            for key, token in (
                ("onsite_split", "k_(x,h)>=1+gamma|q_x|^4"),
                ("form_domination", "a_gamma"),
                ("cube_majorant", "9*"),
                ("fifth_to_third", "k_(x,h)^3<=k_(x,h)^5"),
                ("bridge_bound", "M_bridge_compact"),
            )
        ),
        model,
        "source-uniform endpoint bridge",
    )
    scope = manifest["scope"]
    check("scope closed", scope["compact_source_endpoint_third_moment_bridge_closed"] is True and scope["registered_periodic_compact_source_scope_only"] is True, scope, "registered compact-source bridge")
    check("scope firewalls", all(scope[key] is False for key in ("arbitrary_boundary_extension_closed", "all_time_projected_d_duhamel_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), scope, "successor gates open")
    gates_text = GATES.read_text(encoding="utf-8") if GATES.is_file() else ""
    check("upstream m5 gate", "PA-CP1-ST8-Q3LOCK-TRANSLATE-UNIFORM-LOCAL-FIFTH-GIBBS-MOMENT-AND-ELLIPTIC-EMBEDDING" in gates_text and "CLOSED IN THE REGISTERED PERIODIC COMPACT-SOURCE SCOPE ONLY" in gates_text, GATES, "closed source-uniform m5 authority")
    upstream_text = UPSTREAM.read_text(encoding="utf-8") if UPSTREAM.is_file() else ""
    check("upstream compact source", "actual_q3_static_fifth_moment_and_elliptic_embedding" in upstream_text and "compact source set" in upstream_text, UPSTREAM, "R-167 compact-source m5")
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = ["coefficient_fixture", "shift_fixture", "pair_constant_fixture", "bridge_fixture", "endpoint_form_fixture", "scope_fixture"]
    check("Lean source", LEAN.is_file() and all(marker in source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="compact-source-endpoint-bridge-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("positive totals", primary.get("assertion_count", 0) > 0 and independent.get("assertion_count", 0) > 0, [primary.get("assertion_count"), independent.get("assertion_count")], ">0")
        keys = ("g", "r", "gamma", "m5", "a_gamma", "A_r", "C0", "M_bridge_compact", "form_grid_points", "cube_grid_points", "compact_source_endpoint_third_moment_bridge_closed", "arbitrary_boundary_extension_closed", "all_time_projected_d_duhamel_cauchy_closed", "delta_d_cauchy_closed")
        for key in keys:
            check(f"lane agreement {key}", primary.get("derived", {}).get(key) == independent.get("derived", {}).get(key), [primary.get("derived", {}).get(key), independent.get("derived", {}).get(key)], "equal")
        expected = manifest["finite_fixture"]
        derived = primary.get("derived", {})
        check("fixture constants", all(derived.get(key) == expected[field] for key, field in (("a_gamma", "derived_a_gamma"), ("A_r", "derived_A_r"), ("C0", "derived_C0"), ("M_bridge_compact", "derived_M_bridge_compact"))), derived, expected)

    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R243.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS")
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-COMPACT-SOURCE-ENDPOINT-THIRD-MOMENT-BRIDGE",
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
        },
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED COMPACT-SOURCE-ENDPOINT-BRIDGE PASS {len(rows)}/{len(rows)}; Lean={lean['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
