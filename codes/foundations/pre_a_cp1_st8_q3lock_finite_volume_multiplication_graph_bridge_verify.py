#!/usr/bin/env python3
"""Integrated primary/independent/Lean verifier for EXP-001055."""

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
SLUG = "pre-a-cp1-st8-q3lock-finite-volume-multiplication-graph-bridge"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-multivariate-energy-weighted-source-bound-manifest.json"
FIXTURE = REPO / "strategy/pre-a-cp1-st8-q3lock-weighted-mixed-graph-lift-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
LEAN = REPO / "verification/lean/Tect/R237.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "integrated.json"
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
    command = "lake env lean Tect/R237.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run(
        [str(lake), "env", "lean", "Tect/R237.lean"],
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
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))["fixture"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check(
        "identity",
        manifest["exploration_id"] == "EXP-001055" and manifest["task_id"] == "T-054",
        [manifest["exploration_id"], manifest["task_id"]],
        "EXP-001055/T-054",
    )
    check("upstream identity", upstream["exploration_id"] == "EXP-001054", upstream["exploration_id"], "EXP-001054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    scope = manifest["scope"]
    check(
        "potential-only scope",
        scope["potential_multiplication_graph_bound_closed"] is True
        and scope["commuting_product_bound_closed_conditionally"] is True
        and scope["full_q3_energy_comparison_proved"] is False
        and scope["actual_q3_common_core_map_proved"] is False
        and scope["operator_domain_closure_proved"] is False,
        scope,
        "potential graph closed; full Q3 open",
    )
    check(
        "history/QFT scope",
        scope["factorial_incidence_supplied"] is False
        and scope["actual_q3_history_closed"] is False
        and scope["common_alpha_closed"] is False
        and scope["kms_os_closed"] is False
        and scope["gns_gap_closed"] is False
        and scope["continuum_closed"] is False,
        scope,
        "history and QFT interfaces open",
    )
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = [
        "graph_constant_fixture",
        "product_fixture",
        "volume_monotone_fixture",
        "source_radius_fixture",
        "scope_fixture",
    ]
    check("Lean source", LEAN.is_file() and all(marker in source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="finite-multiplication-graph-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("positive totals", primary.get("total", 0) > 0 and independent.get("total", 0) > 0, [primary.get("total"), independent.get("total")], ">0")
        keys = (
            "C",
            "volumes_checked",
            "local_rows",
            "product_rows",
            "word_lengths_checked",
            "potential_multiplication_graph_bound_closed",
            "commuting_product_bound_closed_conditionally",
            "full_q3_energy_comparison_proved",
            "actual_q3_common_core_map_proved",
            "operator_domain_closure_proved",
            "factorial_incidence_supplied",
            "actual_q3_history_closed",
            "common_alpha_closed",
        )
        for key in keys:
            check(
                f"lane agreement {key}",
                primary.get("derived", {}).get(key) == independent.get("derived", {}).get(key),
                [primary.get("derived", {}).get(key), independent.get("derived", {}).get(key)],
                "equal",
            )
        expected_c = manifest["operator_model"]["constant"].split("=")[-1]
        check(
            "canonical graph constant",
            primary.get("derived", {}).get("C") == expected_c and independent.get("derived", {}).get("C") == expected_c,
            [primary.get("derived", {}).get("C"), independent.get("derived", {}).get("C")],
            expected_c,
        )
        check(
            "canonical volumes",
            primary.get("derived", {}).get("volumes_checked") == manifest["finite_fixture"]["volumes"]
            and independent.get("derived", {}).get("volumes_checked") == manifest["finite_fixture"]["volumes"],
            [primary.get("derived", {}).get("volumes_checked"), independent.get("derived", {}).get("volumes_checked")],
            manifest["finite_fixture"]["volumes"],
        )
        check(
            "upstream route identity",
            manifest["upstream_input"]["multivariate_exploration"] == "EXP-001054"
            and upstream["exploration_id"] == "EXP-001054"
            and bool(fixture["expected_local_rate"]),
            [manifest["upstream_input"].get("multivariate_exploration"), fixture["expected_local_rate"]],
            "registered",
        )

    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R237.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS")
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-VOLUME-MULTIPLICATION-GRAPH",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "lean": lean,
        "boundary": manifest["scope"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {
            "primary_sha256": sha256(PRIMARY),
            "independent_sha256": sha256(INDEPENDENT),
            "manifest_sha256": sha256(MANIFEST),
            "upstream_manifest_sha256": sha256(UPSTREAM),
            "fixture_manifest_sha256": sha256(FIXTURE),
            "lean_sha256": sha256(LEAN),
        },
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED Q3-FINITE-MULTIPLICATION-GRAPH PASS {len(rows)}/{len(rows)}; Lean={lean['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
