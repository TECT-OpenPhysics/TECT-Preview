#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean audit for R-473.

The package verifies one finite, candidate-neutral detector-frame feature
index.  It intentionally leaves the statistical, owner, physical and
prospective gates closed.
"""

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
MANIFEST = REPO / "strategy/hold-lc-001-tte-event-feature-index-v0.1.json"
PRIMARY = REPO / "verification/scripts/hold_lc_001_tte_event_feature_index.py"
INDEPENDENT = REPO / "codes/foundations/hold_lc_001_tte_event_feature_index_independent.py"
HOSTILE = REPO / "codes/foundations/hold_lc_001_tte_event_feature_index_hostile.py"
LEAN = REPO / "verification/lean/Tect/R473.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-integrated-hold-lc-tte-event-feature-index/integrated.json"
)
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def digest(path: Path, *, normalise_lf: bool = False) -> str:
    data = path.read_bytes()
    if normalise_lf:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
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
        errors="replace",
        capture_output=True,
        check=False,
        timeout=240,
    )
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def lake_path() -> Path | None:
    registry = json.loads((LEAN_ROOT / "registry.json").read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file():
            return candidate / name
    found = shutil.which("lake")
    return Path(found) if found else None


def lean_run() -> dict[str, Any]:
    lake = lake_path()
    if lake is None:
        return {"status": "FAIL", "returncode": 1, "command": "lake env lean Tect/R473.lean", "output": "pinned lake executable missing"}
    process = subprocess.run(
        [str(lake), "env", "lean", "Tect/R473.lean"],
        cwd=LEAN_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        timeout=240,
    )
    output = (process.stdout + "\n" + process.stderr).strip()
    status = "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL"
    return {"status": status, "returncode": process.returncode, "command": "lake env lean Tect/R473.lean", "output": output[-2000:]}


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check(
        "manifest identity",
        [manifest.get("result_id"), manifest.get("exploration_id"), manifest.get("task_id"), manifest.get("claim_bearing"), manifest.get("tier")]
        == ["R-473", "EXP-001348", "T-061", False, "T0"],
        [manifest.get("result_id"), manifest.get("exploration_id"), manifest.get("task_id"), manifest.get("claim_bearing"), manifest.get("tier")],
        ["R-473", "EXP-001348", "T-061", False, "T0"],
    )
    check("methods unchanged", all(value is True for value in manifest["methods_preserved"].values()), manifest["methods_preserved"], "all true")
    check(
        "formal integration firewall",
        manifest["formal_integration"]["no_new_negative_ids"] == []
        and manifest["formal_integration"]["no_tier_change"] is True
        and manifest["formal_integration"]["no_pdf"] is True,
        manifest["formal_integration"],
        "no negatives, no tier change, no PDF",
    )
    for name, item in manifest["files"].items():
        if name.endswith("_run"):
            continue
        path = REPO / item["path"]
        expected = item.get("sha256")
        actual = digest(path) if path.is_file() else "MISSING"
        check(f"file {name}", path.is_file() and (not expected or actual == expected), actual, expected or "present")

    with tempfile.TemporaryDirectory(prefix="hold-lc-001-tte-feature-") as temporary:
        temp = Path(temporary)
        primary_process, primary = child(PRIMARY, temp / "primary.json")
        independent_process, independent = child(INDEPENDENT, temp / "independent.json")
        hostile_process, hostile = child(HOSTILE, temp / "hostile.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("hostile child", hostile_process.returncode == 0 and hostile.get("verdict") == "PASS", hostile_process.stdout + hostile_process.stderr, "PASS")
        check("primary/independent exact parity", primary.get("derived_core") == independent.get("derived_core"), [primary.get("derived_core"), independent.get("derived_core")], "equal derived core")
        check("primary assertions", primary.get("assertion_count", 0) >= manifest["test_oracles"]["primary_minimum_assertions"], primary.get("assertion_count"), ">= primary minimum")
        check("independent assertions", independent.get("assertion_count", 0) >= manifest["test_oracles"]["independent_minimum_assertions"], independent.get("assertion_count"), ">= independent minimum")
        check("hostile mutations", hostile.get("all_mutations_rejected") is True and hostile.get("assertion_count", 0) >= manifest["test_oracles"]["hostile_mutation_minimum"], hostile.get("assertion_count"), ">= hostile minimum and all rejected")
        check("two products", len(primary.get("products", [])) == manifest["exact_scope"]["products"], len(primary.get("products", [])), manifest["exact_scope"]["products"])
        check("row total", sum(item["events_hdu"]["row_count"] for item in primary["products"]) == 667116, sum(item["events_hdu"]["row_count"] for item in primary["products"]), 667116)
        derived = primary["derived_core"]
        check("common derived edges", derived["lower_bin"] < derived["upper_bin_exclusive"] and derived["upper_bin_exclusive"] - derived["lower_bin"] == 263, [derived["lower_bin"], derived["upper_bin_exclusive"]], "263 one-second bins")
        check("histogram conservation", all(item["histogram"]["count_sum"] + item["event_summary"]["events_outside_histogram"] == item["events_hdu"]["row_count"] for item in primary["products"]), True, True)
        check("histogram nonnegative", all(all(value >= 0 for value in item["histogram"]["counts"]) for item in primary["products"]), True, True)
        check("response and statistics stopped", all(item["response_matrix_values_read"] is False for item in primary["products"]) and primary["admission"]["timing_likelihood_admitted"] is False and primary["admission"]["component_covariance_admitted"] is False, primary["admission"], "all not admitted")
        check("prospective lock empty", primary["admission"]["prospective_lock"] == "EMPTY", primary["admission"]["prospective_lock"], "EMPTY")

    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    scope = manifest["scope_firewall"]
    forbidden_true = [key for key in ("statistical_model_closed", "physical_owner_closed", "complete_f_reg_f_lim_f_eff_f_obs", "candidate_selection", "prospective_prediction", "physical_sector_closed", "pre_a_closed", "sector_a_closed", "c6_closed", "qft_identity_closed", "yang_mills_identity_closed", "continuum_closed", "mass_gap_closed") if scope.get(key)]
    check("no physical promotion", not forbidden_true, forbidden_true, [])

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "HOLD-LC-001-TTE-EVENT-FEATURE-INDEX-INTEGRATED",
        "result_id": "R-473",
        "exploration_id": "EXP-001348",
        "claim_id": manifest["claim_ids"][0],
        "task_id": "T-061",
        "holdout_id": "HOLD-LC-001",
        "verdict": "PASS",
        "tier": "T0",
        "claim_bearing": False,
        "methods_unchanged": True,
        "assertion_count": len(checks),
        "passed": len(checks),
        "assertions": checks,
        "lean": lean,
        "scope": manifest["scope_firewall"],
        "admission": manifest["admission"],
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "falsifiers": manifest["falsifiers"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {
            "manifest_sha256": digest(MANIFEST),
            "primary_sha256": digest(PRIMARY),
            "independent_sha256": digest(INDEPENDENT),
            "hostile_sha256": digest(HOSTILE),
            "lean_sha256": digest(LEAN, normalise_lf=True),
        },
    }
    atomic_json(output if output.is_absolute() else REPO / output, payload)
    print(f"HOLD-LC-001 TTE FEATURE INTEGRATED PASS {len(checks)}/{len(checks)}; Lean={lean['status']}; methods unchanged")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        run(args.output)
    except (AssertionError, OSError, KeyError, TypeError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as error:
        print(f"HOLD-LC-001 TTE FEATURE INTEGRATED: FAIL - {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
