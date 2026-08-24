#!/usr/bin/env python3
"""Integrated verifier for EXP-001080, including the pinned Lean R262 check."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-structured-cutoff-orbit-modular-derivative"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
LEAN = REPO / "verification/lean/Tect/R262.lean"
LEAN_ROOT = REPO / "verification/lean"
PREVIOUS = REPO / "strategy/pre-a-cp1-st8-q3lock-dual-state-fifth-moment-modular-cutoff-obstruction-manifest.json"
ROUTE = REPO / "strategy/pre-a-cp1-st8-q3lock-modular-cutoff-unitary-resummation-route-split-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    f"2026-08-24-integrated-{SLUG}/integrated.json"
)
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def normalized_sha256(path: Path) -> str:
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


def run_child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
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
    command = "lake env lean Tect/R262.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R262.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def compare_summaries(primary: dict[str, Any], independent: dict[str, Any], tolerance: float, check: Any) -> None:
    p = primary.get("derived", {}).get("dimension_summary", [])
    q = independent.get("derived", {}).get("dimension_summary", [])
    check("dimension summary count", len(p) == len(q) and len(p) > 0, [len(p), len(q)], "equal positive count")
    for index, (pdim, qdim) in enumerate(zip(p, q)):
        check(f"lane n {index}", pdim.get("n") == qdim.get("n") and pdim.get("dimension") == qdim.get("dimension"), [pdim.get("n"), qdim.get("n")], "equal")
        for key in ("max_modular_to_tail_ratio", "max_difference_to_time_tail_ratio"):
            check(f"lane summary {pdim.get('n')} {key}", math.isclose(float(pdim[key]), float(qdim[key]), rel_tol=tolerance, abs_tol=tolerance), [pdim[key], qdim[key]], f"within {tolerance}")
        prows = pdim.get("rows", [])
        qrows = qdim.get("rows", [])
        check(f"lane radius count {pdim.get('n')}", len(prows) == len(qrows), [len(prows), len(qrows)], "equal")
        for ridx, (prow, qrow) in enumerate(zip(prows, qrows)):
            check(f"lane radius {pdim.get('n')} {ridx}", math.isclose(float(prow["radius"]), float(qrow["radius"]), rel_tol=tolerance, abs_tol=tolerance), [prow["radius"], qrow["radius"]], f"within {tolerance}")
            for key in ("tail_root", "max_modular_to_tail_ratio", "max_difference_to_time_tail_ratio"):
                check(f"lane radius value {pdim.get('n')} {ridx} {key}", math.isclose(float(prow[key]), float(qrow[key]), rel_tol=tolerance, abs_tol=tolerance), [prow[key], qrow[key]], f"within {tolerance}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    route = json.loads(ROUTE.read_text(encoding="utf-8"))
    scope = manifest["scope"]
    tolerance = float(manifest["finite_fixture"]["lane_agreement_tolerance"])
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        assertions.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001080" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001080/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("previous authority", previous["exploration_id"] == "EXP-001079" and previous["scope"]["finite_dual_state_obstruction_closed"] is True, previous["exploration_id"], "EXP-001079")
    check("coordinate-cutoff authority", route["exploration_id"] == "EXP-000798" and route["scope"] if "scope" in route else route["exploration_id"] == "EXP-000798", route["exploration_id"], "EXP-000798")
    check("Lean source markers", LEAN.is_file() and all(marker in LEAN.read_text(encoding="utf-8") for marker in ("two_sided_identity", "finite_fixture_positive", "q3_bond_fixture", "scope_fixture")), LEAN.is_file(), "R262 source markers")
    check("Lean forbidden", LEAN.is_file() and not any(token in LEAN.read_text(encoding="utf-8").split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    open_keys = ("oscillator_dimension_uniformity_proved", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "actual_ccr_domain_closed", "smooth_cutoff_infinite_volume_closed", "four_context_history_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "all successor gates open")

    with tempfile.TemporaryDirectory(prefix="finite-structured-q3-") as temporary:
        primary_process, primary = run_child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = run_child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("lane assertion counts", primary.get("assertion_count", 0) > 0 and independent.get("assertion_count", 0) > 0, [primary.get("assertion_count"), independent.get("assertion_count")], ">0")
        compare_summaries(primary, independent, tolerance, check)
        check("modular ratio diagnostic", float(primary.get("derived", {}).get("max_modular_to_tail_ratio", 0.0)) > float(manifest["finite_fixture"]["modular_ratio_floor"]), primary.get("derived", {}).get("max_modular_to_tail_ratio"), f">{manifest['finite_fixture']['modular_ratio_floor']}")
        check("tail floor diagnostic", all(float(row["tail_root"]) > float(manifest["finite_fixture"]["tail_floor"]) for row in primary.get("derived", {}).get("dimension_summary", []) for row in row.get("rows", [])), primary.get("derived", {}).get("dimension_summary"), "all above floor")

    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R262.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS")
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-STRUCTURED-CUTOFF-ORBIT-MODULAR-DERIVATIVE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(assertions),
        "assertions": assertions,
        "lean": lean,
        "boundary": scope,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"primary_sha256": normalized_sha256(PRIMARY), "independent_sha256": normalized_sha256(INDEPENDENT), "manifest_sha256": normalized_sha256(MANIFEST), "lean_sha256": normalized_sha256(LEAN), "previous_manifest_sha256": normalized_sha256(PREVIOUS), "route_manifest_sha256": normalized_sha256(ROUTE)},
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED FINITE-STRUCTURED-CUTOFF-Q3 PASS {len(assertions)}/{len(assertions)}; Lean={lean['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
