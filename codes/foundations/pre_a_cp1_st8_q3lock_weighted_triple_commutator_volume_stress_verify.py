#!/usr/bin/env python3
"""Integrated verifier for EXP-001088."""

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
SLUG = "pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
PRIMARY = REPO / "codes/foundations" / f"{SLUG}.py"
INDEPENDENT = REPO / "codes/foundations" / f"{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R270.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
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
    command = "lake env lean Tect/R270.lean"
    lake = lake_path()
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R270.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def close(left: Any, right: Any, tolerance: float = 1.0e-7) -> bool:
    return abs(float(left) - float(right)) <= tolerance * (1.0 + abs(float(left)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001088" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001088/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = ["modular_coefficient_fixture", "signed_orientation_fixture", "graph_fixture", "support_local_growth_threshold_fixture", "full_volume_growth_threshold_fixture", "scope_fixture"]
    check("Lean source", LEAN.is_file() and all(marker in source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="weighted-triple-commutator-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        p_volumes, i_volumes = primary["derived"]["volume_rows"], independent["derived"]["volume_rows"]
        check("volume sequence", [row["volume"] for row in p_volumes] == [row["volume"] for row in i_volumes] == fixture["volume_values"], [[row["volume"] for row in p_volumes], [row["volume"] for row in i_volumes]], fixture["volume_values"])
        numeric = ("D2_gibbs", "modular_D2_gibbs", "D2_weighted", "modular_weighted", "tail_operator_norm", "modular_identity_error")
        for p_volume, i_volume in zip(p_volumes, i_volumes):
            check(f"V={p_volume['volume']} dimension", p_volume["dimension"] == i_volume["dimension"], [p_volume["dimension"], i_volume["dimension"]], "equal")
            for p_row, i_row in zip(p_volume["radius_rows"], i_volume["radius_rows"]):
                check(f"V={p_volume['volume']} L={p_row['radius']} locality", close(p_row["source_commutator_norm"], i_row["source_commutator_norm"]) and close(p_row["disjoint_tail_commutator_norm"], i_row["disjoint_tail_commutator_norm"]), [p_row["source_commutator_norm"], i_row["source_commutator_norm"], p_row["disjoint_tail_commutator_norm"], i_row["disjoint_tail_commutator_norm"]], "within tolerance")
                for kind in ("local", "full"):
                    check(f"V={p_volume['volume']} L={p_row['radius']} {kind} agreement", all(close(p_row["weights"][kind][key], i_row["weights"][kind][key]) for key in numeric), [p_row["weights"][kind], i_row["weights"][kind]], "within 1e-7 relative")
        for field in ("local_modular_weighted_maxima", "full_modular_weighted_maxima", "local_D2_weighted_maxima", "full_D2_weighted_maxima"):
            check(f"{field} agreement", all(close(a, b) for a, b in zip(primary["derived"][field], independent["derived"][field])), [primary["derived"][field], independent["derived"][field]], "within 1e-7 relative")
        check("growth agreement", close(primary["derived"]["local_modular_volume_growth"], independent["derived"]["local_modular_volume_growth"]) and close(primary["derived"]["full_modular_volume_growth"], independent["derived"]["full_modular_volume_growth"]), [primary["derived"]["local_modular_volume_growth"], independent["derived"]["local_modular_volume_growth"], primary["derived"]["full_modular_volume_growth"], independent["derived"]["full_modular_volume_growth"]], "within 1e-7 relative")
        check("candidate growth", primary["derived"]["local_modular_volume_growth"] >= float(fixture["growth_threshold"]) and primary["derived"]["full_modular_volume_growth"] >= float(fixture["growth_threshold"]), [primary["derived"]["local_modular_volume_growth"], primary["derived"]["full_modular_volume_growth"]], f">={fixture['growth_threshold']}")
        check("support locality", all(float(row["source_commutator_norm"]) <= float(fixture["commutator_tolerance"]) and float(row["disjoint_tail_commutator_norm"]) <= float(fixture["commutator_tolerance"]) for volume in p_volumes for row in volume["radius_rows"]), "all rows", "tolerance")

    open_keys = ("candidate_volume_uniform_bound_closed", "weighted_modular_domain_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "positive_time_history_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open")
    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-WEIGHTED-TRIPLE-COMMUTATOR-VOLUME-STRESS",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "lean": lean,
        "boundary": scope,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN)},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()
    if args.skip_lean:
        raise SystemExit("skip-lean is not allowed for the integrated proof checkpoint")
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED WEIGHTED-TRIPLE-COMMUTATOR-VOLUME-STRESS PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
