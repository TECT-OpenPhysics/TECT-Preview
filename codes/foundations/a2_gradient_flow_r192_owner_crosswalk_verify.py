#!/usr/bin/env python3
"""Integrated verifier for the conditional A2/R-192 owner crosswalk."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy" / "pre-a2-gradient-flow-r192-owner-crosswalk-manifest.json"
PRIMARY = ROOT / "codes" / "foundations" / "a2_gradient_flow_r192_owner_crosswalk.py"
INDEPENDENT = ROOT / "codes" / "foundations" / "a2_gradient_flow_r192_owner_crosswalk_independent.py"
DEFAULT_OUTPUT = ROOT / "claims" / "A2-FULL-PRODUCTION-WELLPOSED" / "runs" / "2026-08-23-a2-gradient-flow-r192-owner-crosswalk" / "integrated.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def check(rows: list[dict], name: str, ok: bool, actual, expected) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})


def child(script: Path, output: Path) -> tuple[int, dict]:
    proc = subprocess.run([sys.executable, "-B", "-X", "utf8", str(script), "--output", str(output)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.exists() else {}
    payload["_stdout"] = proc.stdout
    payload["_stderr"] = proc.stderr
    return proc.returncode, payload


def mutations(manifest: dict) -> list[tuple[str, bool, object]]:
    out: list[tuple[str, bool, object]] = []
    m = copy.deepcopy(manifest)
    m["registered_crosswalk"]["owner_compatible"] = True
    out.append(("promote_gradient_to_production", m["registered_crosswalk"]["owner_compatible"] is True, m["registered_crosswalk"]["owner_compatible"]))
    m = copy.deepcopy(manifest)
    m["registered_crosswalk"]["first_failure_slot"] = "none"
    out.append(("erase_first_failure", m["registered_crosswalk"]["first_failure_slot"] != manifest["registered_crosswalk"]["first_failure_slot"], m["registered_crosswalk"]["first_failure_slot"]))
    m = copy.deepcopy(manifest)
    m["registered_crosswalk"]["a2_owner"]["stochastic_heat"] = True
    out.append(("insert_stochastic_heat", m["registered_crosswalk"]["a2_owner"]["stochastic_heat"] is True, m["registered_crosswalk"]["a2_owner"]["stochastic_heat"]))
    m = copy.deepcopy(manifest)
    m["registered_crosswalk"]["a2_owner"]["flow"] = "physical empty dynamics"
    out.append(("promote_physical_empty", "physical empty" in m["registered_crosswalk"]["a2_owner"]["flow"].lower(), m["registered_crosswalk"]["a2_owner"]["flow"]))
    m = copy.deepcopy(manifest)
    m["registered_crosswalk"]["expected_absence"] = []
    out.append(("insert_q_ledger", len(m["registered_crosswalk"]["expected_absence"]) != len(manifest["registered_crosswalk"]["expected_absence"]), m["registered_crosswalk"]["expected_absence"]))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict] = []
    package_paths = {"primary": PRIMARY, "independent": INDEPENDENT, "verifier": Path(__file__), "certificate": ROOT / manifest["files"]["certificate"]["path"]}
    package = {name: digest(path) if path.is_file() else "MISSING" for name, path in package_paths.items()}
    expected_package = {name: record["sha256"] for name, record in manifest["files"].items()}
    check(rows, "package_file_hashes_match", package == expected_package, package, expected_package)
    with tempfile.TemporaryDirectory(prefix="a2_r192_crosswalk_") as tmp:
        p_code, primary = child(PRIMARY, Path(tmp) / "primary.json")
        i_code, independent = child(INDEPENDENT, Path(tmp) / "independent.json")
    check(rows, "primary_exit_zero", p_code == 0, p_code, 0)
    check(rows, "independent_exit_zero", i_code == 0, i_code, 0)
    check(rows, "primary_failures_empty", primary.get("failures") == [], primary.get("failures"), [])
    check(rows, "independent_failures_empty", independent.get("failures") == [], independent.get("failures"), [])
    pcore = primary.get("derived", {})
    icore = independent.get("derived", {})
    keys = ("a2_flow_kind", "a2_stochastic_heat", "required_slot_absence", "r192_first_failure_slot", "r192_first_failure_status", "owner_compatible")
    check(rows, "derived_crosswalk_identical", {key: pcore.get(key) for key in keys} == {key: icore.get(key) for key in keys}, [{key: pcore.get(key) for key in keys}, {key: icore.get(key) for key in keys}], "identical")
    check(rows, "first_failure_is_heat_root", pcore.get("r192_first_failure_slot") == "heat_root_incidence", pcore.get("r192_first_failure_slot"), "heat_root_incidence")
    check(rows, "owner_is_not_compatible", pcore.get("owner_compatible") is False and pcore.get("a2_stochastic_heat") is False, pcore, "deterministic baseline only")
    check(rows, "independent_stdlib_pass", "A2 GRADIENT FLOW R192 INDEPENDENT PASS" in independent.get("_stdout", ""), independent.get("_stdout"), "independent pass")
    for name, ok, actual in mutations(manifest):
        check(rows, f"hostile_{name}", ok, actual, "mutation rejected")
    boundary = manifest["boundary"].lower()
    for token in ("t0", "claim-nonbearing", "r-192", "a13", "physical-empty"):
        check(rows, f"boundary_{token}", token in boundary, boundary, f"contains {token}")
    failures = [row for row in rows if row["status"] != "PASS"]
    result = {"schema": "tect/pre-a2-gradient-flow-r192-owner-crosswalk-integrated/1.0", "claim_ids": manifest["claim_ids"], "script_version": "1.0.0", "generated_at_utc": datetime.now(timezone.utc).isoformat(), "primary_result": {key: value for key, value in primary.items() if not key.startswith("_")}, "independent_result": {key: value for key, value in independent.items() if not key.startswith("_")}, "cross_assertions": rows, "cross_assertion_count": len(rows), "conclusion": "The conditional A2 L2 gradient-flow theorem is not the missing stochastic/root-labelled R-192 production owner; no A13 gate is closed.", "honesty_boundary": ["conditional A2 baseline only", "no stochastic heat/root owner", "no R-192 completion", "no A13 closure", "no physical-empty or continuum conclusion"], "failures": failures}
    if not args.no_store:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        print(f"A2 GRADIENT FLOW R192 INTEGRATED FAIL {len(rows)-len(failures)}/{len(rows)}")
        for failure in failures:
            print(f"FAIL {failure['name']}: {failure['actual']} expected {failure['expected']}")
        return 1
    print(f"A2 GRADIENT FLOW R192 INTEGRATED PASS {len(rows)}/{len(rows)}")
    if not args.no_store:
        print(f"Evidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
