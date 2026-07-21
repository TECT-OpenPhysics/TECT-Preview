#!/usr/bin/env python3
"""One-command integrated verifier for A12 source-square reduction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


VERSION = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO / "claims" / "A12-CLASSII-SOURCE-SQUARE-REDUCTION" / "classii_source_square_reduction_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A12-CLASSII-SOURCE-SQUARE-REDUCTION" / "runs" / "2026-07-21-integrated-source-square" / "result.json"


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if passed else "FAIL", "actual": actual, "expected": expected})


def run_child(script: Path, manifest: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(script), "--manifest", str(manifest), "--output", str(output)], cwd=REPO, text=True, capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    assertions: list[dict[str, Any]] = []

    primary_info = manifest["authority"]["primary_audit"]
    independent_info = manifest["authority"]["independent_audit"]
    primary_script = REPO / primary_info["path"]
    independent_script = REPO / independent_info["path"]
    primary_output = REPO / manifest["run_contract"]["primary_output"]
    independent_output = REPO / manifest["run_contract"]["independent_output"]

    primary_run = run_child(primary_script, args.manifest, primary_output)
    independent_run = run_child(independent_script, args.manifest, independent_output)
    add(assertions, "primary_exit_zero", primary_run.returncode == 0, {"returncode": primary_run.returncode, "stdout": primary_run.stdout, "stderr": primary_run.stderr}, 0)
    add(assertions, "independent_exit_zero", independent_run.returncode == 0, {"returncode": independent_run.returncode, "stdout": independent_run.stdout, "stderr": independent_run.stderr}, 0)

    primary = json.loads(primary_output.read_text(encoding="utf-8")) if primary_output.exists() else {}
    independent = json.loads(independent_output.read_text(encoding="utf-8")) if independent_output.exists() else {}
    add(assertions, "primary_status_pass", primary.get("status") == "PASS", primary.get("status"), "PASS")
    add(assertions, "independent_status_pass", independent.get("status") == "PASS", independent.get("status"), "PASS")
    add(assertions, "primary_assertion_count", int(primary.get("assertion_count", -1)) == int(manifest["run_contract"]["primary_assertions"]), primary.get("assertion_count"), manifest["run_contract"]["primary_assertions"])
    add(assertions, "independent_assertion_count", int(independent.get("assertion_count", -1)) == int(manifest["run_contract"]["independent_assertions"]), independent.get("assertion_count"), manifest["run_contract"]["independent_assertions"])

    for key in ("beta_operator", "c_symbol", "source_base_constant"):
        p_value = float(primary.get("derived", {}).get(key, float("nan")))
        i_value = float(independent.get("derived", {}).get(key, float("nan")))
        add(assertions, f"cross_{key}", abs(p_value - i_value) <= float(manifest["integrated_audit"]["cross_tolerance"]), {"primary": p_value, "independent": i_value}, "agree")

    p_threshold = next(
        row["source_only_H6_ceiling"]
        for row in primary.get("derived", {}).get("budget_rows", [])
        if abs(float(row["p"]) - float(manifest["derived_oracles"]["budget_reference_p"])) < 1e-15
    )
    i_threshold = float(independent.get("derived", {}).get("reference_H6_ceiling", float("nan")))
    add(assertions, "cross_reference_H6_ceiling", abs(float(p_threshold) - i_threshold) <= float(manifest["integrated_audit"]["budget_tolerance"]), {"primary": p_threshold, "independent": i_threshold}, "agree")

    for key in ("primary_audit", "independent_audit", "one_command_verifier", "proof_note", "proof_pdf"):
        info = manifest["authority"][key]
        path = REPO / info["path"]
        actual = sha256(path) if path.exists() else None
        add(assertions, f"package_{key}_hash", actual == info["sha256"], actual, info["sha256"])

    note_path = REPO / manifest["authority"]["proof_note"]["path"]
    note = note_path.read_text(encoding="utf-8")
    required_note_tokens = (
        "A12-CLASSII-SHARP-CUBE-L6-VECTOR-NORM-ENCLOSURE",
        "beta_{\\rm op}",
        "M_R^2",
        "N_{j-1}+1",
        "product Marcinkiewicz",
        "does not supply a certified decimal enclosure",
        "Result footer",
    )
    add(assertions, "proof_note_required_boundaries", all(token in note for token in required_note_tokens), [token for token in required_note_tokens if token not in note], "all present")
    add(assertions, "manifest_scope_is_t4_reduction", manifest["status"] == "T4 PROVED-ANALYTIC-REDUCTION", manifest["status"], "T4 PROVED-ANALYTIC-REDUCTION")
    add(assertions, "numeric_enclosure_remains_open", manifest["honesty_boundary"]["numerical_enclosure"] == "OPEN", manifest["honesty_boundary"]["numerical_enclosure"], "OPEN")
    add(assertions, "t047_not_claimed_closed", manifest["honesty_boundary"]["t047"] == "OPEN", manifest["honesty_boundary"]["t047"], "OPEN")

    own_count = len(assertions)
    expected_own = int(manifest["run_contract"]["integrated_own_assertions"])
    add(assertions, "integrated_own_assertion_count", own_count == expected_own, own_count, expected_own)
    passed = sum(row["status"] == "PASS" for row in assertions)
    child_total = int(primary.get("assertion_count", 0)) + int(independent.get("assertion_count", 0))
    total = child_total + len(assertions)
    total_passed = int(primary.get("passed", 0)) + int(independent.get("passed", 0)) + passed
    payload = {
        "schema": "tect/a12-classii-source-square-integrated-result/1.0",
        "claim_id": manifest["claim_id"],
        "script_version": VERSION,
        "status": "PASS" if total_passed == total else "FAIL",
        "assertion_count": total,
        "passed": total_passed,
        "failed": total - total_passed,
        "integrated_assertions": assertions,
        "primary": primary,
        "independent": independent,
        "child_stdout": {"primary": primary_run.stdout, "independent": independent_run.stdout},
        "conclusion": manifest["theorem"]["source_square"],
        "open_gate": manifest["open_followup"],
    }
    atomic_json(args.output, payload)
    if payload["status"] == "PASS":
        print(f"PASS: primary ({primary['passed']}/{primary['assertion_count']})")
        print(f"PASS: independent ({independent['passed']}/{independent['assertion_count']})")
        print(f"ASSERTS: {total_passed}/{total}")
        print("A12-CLASSII-SOURCE-SQUARE-REDUCTION-INTEGRATED-PASS")
        print(f"Evidence: {args.output}")
        return 0
    print(f"FAIL: integrated ({total_passed}/{total})")
    print(f"Evidence: {args.output}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
