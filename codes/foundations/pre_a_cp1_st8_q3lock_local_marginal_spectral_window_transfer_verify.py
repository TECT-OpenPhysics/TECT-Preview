#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean verifier for R-390."""

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
SLUG = "pre_a_cp1_st8_q3lock_local_marginal_spectral_window_transfer"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-marginal-spectral-window-transfer-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
HOSTILE = REPO / f"codes/foundations/{SLUG}_hostile.py"
LEAN = REPO / "verification/lean/Tect/R390.lean"
REGISTRY = REPO / "verification/lean/registry.json"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def digest(path: Path) -> str:
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
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    root = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        candidate = root / name
        if candidate.is_file():
            return candidate
    found = shutil.which("lake")
    return Path(found) if found else None


def run_child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    return process, json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}


def compile_lean() -> dict[str, Any]:
    lake = lake_path()
    command = "lake env lean Tect/R390.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R390.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-3000:]}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001233" and manifest["result_id"] == "R-390" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001233/R-390/false")
    check("sources", all(path.is_file() for path in (PRIMARY, INDEPENDENT, HOSTILE, LEAN, REGISTRY)), "all present", "all present")
    check("independent source", digest(PRIMARY) != digest(INDEPENDENT), [digest(PRIMARY), digest(INDEPENDENT)], "distinct")
    markers = ["gibbs_tail_term_bound", "window_mass_split", "local_duality_scope", "scope_fixture"]
    lean_text = LEAN.read_text(encoding="utf-8")
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in lean_text.split() for token in ("sorry", "admit", "axiom", "unsafe")), "none", "none")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entries = [entry for entry in registry["entrypoints"] if entry["path"] == "verification/lean/Tect/R390.lean"]
    check("Lean registry unique", len(entries) == 1, len(entries), 1)
    check("Lean registry hash", entries[0]["sha256"] == digest(LEAN), entries[0]["sha256"], digest(LEAN))
    check("Lean declarations", entries[0]["declarations"] == markers, entries[0]["declarations"], markers)

    with tempfile.TemporaryDirectory(prefix="r390-") as temporary:
        root = Path(temporary)
        primary_process, primary = run_child(PRIMARY, root / "primary.json")
        independent_process, independent = run_child(INDEPENDENT, root / "independent.json")
        hostile_process, hostile = run_child(HOSTILE, root / "hostile.json")
    check("primary child", primary_process.returncode == 0 and "PASS" in primary_process.stdout, primary_process.stdout[-3000:], "PASS")
    check("independent child", independent_process.returncode == 0 and "PASS" in independent_process.stdout, independent_process.stdout[-3000:], "PASS")
    check("hostile child", hostile_process.returncode == 0 and "CAUGHT" in hostile_process.stdout, hostile_process.stdout[-3000:], "CAUGHT")
    pd, ind = primary["derived"], independent["derived"]
    tolerance = float(fixture["agreement_tolerance"])
    numeric_fields = ("maximum_duality_residual", "maximum_square_duality_residual", "minimum_window_mass", "maximum_window_mass", "maximum_volume_projected_ratio", "maximum_volume_conditional_ratio", "maximum_cutoff_projected_ratio", "maximum_cutoff_conditional_ratio")
    for field in numeric_fields:
        check(f"agreement {field}", abs(float(pd[field]) - float(ind[field])) <= tolerance * (1.0 + abs(float(pd[field]))), [pd[field], ind[field]], f"within scaled {tolerance}")
    integer_fields = ("system_count", "beta_pair_count", "duality_record_count", "row_count", "expected_row_count", "minimum_window_rank")
    for field in integer_fields:
        check(f"agreement {field}", pd[field] == ind[field], [pd[field], ind[field]], "equal")
    check("agreement pairs", pd["admissible_pairs"] == ind["admissible_pairs"], "same", "same")
    for field in ("operator_max_by_dimension",):
        check(f"agreement {field}", pd[field].keys() == ind[field].keys() and all(abs(float(pd[field][key]) - float(ind[field][key])) <= tolerance for key in pd[field]), [pd[field], ind[field]], f"within {tolerance}")
    for profile_name in ("volume_projected_profile", "volume_conditional_profile", "cutoff_projected_profile", "cutoff_conditional_profile"):
        pp, ii = pd[profile_name], ind[profile_name]
        check(f"agreement {profile_name} keys", [row["key"] for row in pp["profiles"]] == [row["key"] for row in ii["profiles"]], "same keys", "same")
        max_difference = max((abs(float(a["spread_ratio"]) - float(b["spread_ratio"])) for a, b in zip(pp["profiles"], ii["profiles"])), default=0.0)
        check(f"agreement {profile_name} values", max_difference <= tolerance * 2.0, max_difference, f"<={2.0 * tolerance}")
    finite_flags = ("finite_local_partial_trace_duality_closed", "finite_local_projection_positivity_closed", "finite_local_window_mass_rank_closed", "finite_volume_window_stability_closed", "finite_cutoff_stress_closed")
    open_flags = tuple(key for key in scope if key.endswith("_closed") and key not in finite_flags)
    for field in finite_flags:
        check(f"scope {field}", pd[field] is True and ind[field] is True, [pd[field], ind[field]], "true")
    for field in open_flags:
        check(f"scope {field}", pd[field] is False and ind[field] is False, [pd[field], ind[field]], "false")
    threshold = float(fixture["volume_stability_ratio_threshold"])
    check("volume corridor", float(pd["maximum_volume_projected_ratio"]) <= threshold and float(pd["maximum_volume_conditional_ratio"]) <= threshold, [pd["maximum_volume_projected_ratio"], pd["maximum_volume_conditional_ratio"]], f"<={threshold}")
    cutoff_threshold = float(fixture["cutoff_stress_ratio_threshold"])
    check("cutoff stress retained", float(pd["maximum_cutoff_projected_ratio"]) > cutoff_threshold and float(pd["maximum_cutoff_conditional_ratio"]) > cutoff_threshold, [pd["maximum_cutoff_projected_ratio"], pd["maximum_cutoff_conditional_ratio"]], f">{cutoff_threshold}")
    check("hostile separation", float(hostile["derived"]["minimum_wrong_duality_residual"]) > float(fixture["hostile_threshold"]), hostile["derived"]["minimum_wrong_duality_residual"], f">{fixture['hostile_threshold']}")
    check("hostile correct anchor", float(hostile["derived"]["maximum_correct_duality_residual"]) <= float(fixture["partial_trace_tolerance"]), hostile["derived"]["maximum_correct_duality_residual"], f"<={fixture['partial_trace_tolerance']}")
    lean = compile_lean()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    check("scope firewall", [field for field in open_flags if pd[field]] == [], "all open", "all false")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-MARGINAL-SPECTRAL-WINDOW-TRANSFER", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(checks), "assertions": checks, "lean": lean, "derived": {"primary": pd, "independent": ind, "hostile": hostile["derived"]}, "boundary": manifest["boundary"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED LOCAL-MARGINAL SPECTRAL-WINDOW PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']} volume_ratio={payload['derived']['primary']['maximum_volume_projected_ratio']:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
