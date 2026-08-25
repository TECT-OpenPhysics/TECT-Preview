#!/usr/bin/env python3
"""Integrated verifier for EXP-001106."""

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
SLUG = "pre_a_cp1_st8_q3lock_finite_q3_actual_number_moment_bridge"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R279.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-integrated-{SLUG}" / "integrated.json"
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
    command = "lake env lean Tect/R279.lean"
    lake = lake_path()
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R279.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def close(left: Any, right: Any, tolerance: float) -> bool:
    return abs(float(left) - float(right)) <= tolerance * (1.0 + abs(float(left)) + abs(float(right)))


def compare(primary: dict[str, Any], independent: dict[str, Any], tolerance: float, check: Any) -> None:
    p_volumes = primary.get("derived", {}).get("volume_rows", [])
    i_volumes = independent.get("derived", {}).get("volume_rows", [])
    check("volume row count", len(p_volumes) == len(i_volumes), [len(p_volumes), len(i_volumes)], "equal")
    for p_volume, i_volume in zip(p_volumes, i_volumes):
        check(f"V={p_volume['volume']} metadata", p_volume["volume"] == i_volume["volume"] and p_volume["edge_count"] == i_volume["edge_count"], [p_volume["volume"], p_volume["edge_count"]], [i_volume["volume"], i_volume["edge_count"]])
        p_rows, i_rows = p_volume["n_rows"], i_volume["n_rows"]
        check(f"V={p_volume['volume']} n row count", len(p_rows) == len(i_rows), [len(p_rows), len(i_rows)], "equal")
        for p_row, i_row in zip(p_rows, i_rows):
            label = f"V={p_volume['volume']} n={p_row['n']}"
            check(label + " metadata", p_row["n"] == i_row["n"] and p_row["dimension"] == i_row["dimension"], [p_row["n"], p_row["dimension"]], [i_row["n"], i_row["dimension"]])
            for key in ("local_k_min", "gibbs_max_n_to_k_ratio", "history_max_n_to_k_ratio"):
                check(label + " " + key, close(p_row[key], i_row[key], tolerance), p_row[key], i_row[key])
            p_gibbs, i_gibbs = p_row["gibbs_rows"], i_row["gibbs_rows"]
            check(label + " Gibbs row count", len(p_gibbs) == len(i_gibbs), [len(p_gibbs), len(i_gibbs)], "equal")
            for p_item, i_item in zip(p_gibbs, i_gibbs):
                for key in ("site", "top_probability", "weighted_top_tail", "n_moment", "k_moment", "markov_ratio", "n_to_k_ratio"):
                    if key == "site":
                        check(label + f" Gibbs site {p_item['site']} site", p_item[key] == i_item[key], p_item[key], i_item[key])
                    else:
                        check(label + f" Gibbs site {p_item['site']} {key}", close(p_item[key], i_item[key], tolerance), p_item[key], i_item[key])
            p_history, i_history = p_row["history_rows"], i_row["history_rows"]
            check(label + " history row count", len(p_history) == len(i_history), [len(p_history), len(i_history)], "equal")
            for p_history_row, i_history_row in zip(p_history, i_history):
                hlabel = label + f" sign={p_history_row['sign']} t={p_history_row['time']}"
                check(hlabel + " metadata", p_history_row["sign"] == i_history_row["sign"] and close(p_history_row["time"], i_history_row["time"], tolerance), [p_history_row["sign"], p_history_row["time"]], [i_history_row["sign"], i_history_row["time"]])
                check(hlabel + " unitarity", close(p_history_row["unitarity_residual"], i_history_row["unitarity_residual"], tolerance), p_history_row["unitarity_residual"], i_history_row["unitarity_residual"])
                for p_item, i_item in zip(p_history_row["site_rows"], i_history_row["site_rows"]):
                    for key in ("site", "top_probability", "weighted_top_tail", "n_moment", "k_moment", "markov_ratio", "n_to_k_ratio"):
                        if key == "site":
                            check(hlabel + f" site {p_item['site']} index", p_item[key] == i_item[key], p_item[key], i_item[key])
                        else:
                            check(hlabel + f" site {p_item['site']} {key}", close(p_item[key], i_item[key], tolerance), p_item[key], i_item[key])


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    scope = manifest["scope"]
    tolerance = float(manifest["finite_fixture"]["agreement_tolerance"])
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001106" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001106/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("source distinct", normalized_sha256(PRIMARY) != normalized_sha256(INDEPENDENT), [normalized_sha256(PRIMARY), normalized_sha256(INDEPENDENT)], "different source hashes")
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = ["fifth_moment_to_weighted_top_tail", "fifth_moment_fixture"]
    check("Lean source markers", LEAN.is_file() and all(marker in lean_source for marker in markers), markers, "present")
    check("Lean forbidden tokens", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    with tempfile.TemporaryDirectory(prefix="finite-q3-number-moment-") as temporary:
        p_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        i_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", p_process.returncode == 0 and primary.get("verdict") == "PASS", p_process.stdout + p_process.stderr, "PASS")
        check("independent child", i_process.returncode == 0 and independent.get("verdict") == "PASS", i_process.stdout + i_process.stderr, "PASS")
        compare(primary, independent, tolerance, check)
    open_keys = ("energy_to_number_uniform_form_domination_closed", "q3_gibbs_weighted_tail_uniformity_closed", "q3_evolved_history_weighted_tail_uniformity_closed", "actual_unbounded_q3_domain_transfer_closed", "source_volume_orientation_history_uniform_closed", "direct_d_delta_d_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open")
    check("finite actual-state scope", all(scope[key] is True for key in ("finite_actual_gibbs_number_moment_closed", "finite_actual_history_number_moment_closed", "finite_markov_top_tail_bridge_closed", "finite_shifted_onsite_energy_comparison_closed")), scope, "finite PASS")
    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-Q3-ACTUAL-NUMBER-MOMENT-BRIDGE", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "lean": lean, "boundary": scope, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"primary_sha256": normalized_sha256(PRIMARY), "independent_sha256": normalized_sha256(INDEPENDENT), "manifest_sha256": normalized_sha256(MANIFEST), "lean_sha256": normalized_sha256(LEAN)}}


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
    print(f"INTEGRATED FINITE-Q3-ACTUAL-NUMBER-MOMENT-BRIDGE PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
