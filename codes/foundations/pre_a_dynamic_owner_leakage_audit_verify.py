#!/usr/bin/env python3
"""Integrated R-449 primary/independent/hostile/Lean verifier."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-dynamic-owner-leakage-audit-manifest.json"
PRIMARY = ROOT / "verification/scripts/pre_a_dynamic_owner_leakage_audit.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_dynamic_owner_leakage_audit_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_dynamic_owner_leakage_audit_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R449.lean"
LEAN_ROOT = ROOT / "verification/lean"
LAKE = Path(
    os.environ.get(
        "TECT_LAKE",
        "C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe",
    )
)
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-30-integrated-dynamic_owner_leakage_audit/integrated.json"
)


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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


def digest(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    ).hexdigest()


def child(script: Path, output: Path):
    process = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def lean_run() -> dict:
    if not LAKE.is_file():
        return {
            "status": "UNAVAILABLE",
            "command": "lake env lean Tect/R449.lean",
            "output": "pinned direct lake executable not found",
        }
    process = subprocess.run(
        [str(LAKE), "env", "lean", "Tect/R449.lean"],
        cwd=LEAN_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    output = (process.stdout + "\n" + process.stderr).strip()
    return {
        "status": "PASS"
        if process.returncode == 0 and "error:" not in output.lower()
        else "FAIL",
        "command": "lake env lean Tect/R449.lean",
        "returncode": process.returncode,
        "output": output[-2000:],
    }


def run(output: Path = DEFAULT_OUTPUT, skip_lean: bool = False) -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks = []

    def check(name, condition, actual, expected, group):
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": actual,
                "expected": expected,
            }
        )

    check(
        "identity",
        [
            manifest["result_id"],
            manifest["exploration_id"],
            manifest["task_id"],
            manifest["claim_bearing"],
            manifest["tier"],
        ]
        == ["R-449", "EXP-001322", "T-061", False, "T0"],
        [
            manifest["result_id"],
            manifest["exploration_id"],
            manifest["task_id"],
            manifest["claim_bearing"],
            manifest["tier"],
        ],
        ["R-449", "EXP-001322", "T-061", False, "T0"],
        "provenance",
    )
    check(
        "method firewall",
        all(
            manifest["scope"][key]
            for key in ("owner_intake_audited", "proof_owner_separated", "no_tier_change", "no_pdf")
        ),
        "preserved",
        "preserved",
        "method-firewall",
    )
    check(
        "owner branch parked",
        manifest["leakage_audit"]["owner_branch_verdict"]
        == "PARK_OWNER_BRANCH_SURVIVING_STATIC_EQUIVALENCE_CLASS"
        and not manifest["scope"]["physical_owner_complete"],
        manifest["leakage_audit"],
        "parked",
        "boundary",
    )
    check("Lean source", LEAN.is_file(), str(LEAN), True, "Lean")
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    check(
        "Lean markers",
        all(marker in source for marker in manifest["lean_crosscheck"]["theorem_markers"]),
        manifest["lean_crosscheck"]["theorem_markers"],
        "all present",
        "Lean",
    )
    check(
        "Lean firewall",
        not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")),
        "clean",
        "forbidden tokens absent",
        "Lean",
    )
    for key, item in manifest["files"].items():
        path = ROOT / item["path"]
        check(
            f"file {key} hash",
            path.is_file()
            and item["sha256"] != "TO_BE_FILLED"
            and digest(path) == item["sha256"],
            digest(path) if path.is_file() else None,
            item["sha256"],
            "provenance",
        )

    with tempfile.TemporaryDirectory(prefix="r449-integrated-") as directory:
        temporary = Path(directory)
        primary_process, primary = child(PRIMARY, temporary / "primary.json")
        independent_process, independent = child(INDEPENDENT, temporary / "independent.json")
        hostile_process, hostile = child(HOSTILE, temporary / "hostile.json")
        check(
            "primary child",
            primary_process.returncode == 0 and primary.get("verdict") == manifest["status"],
            primary_process.stdout + primary_process.stderr,
            manifest["status"],
            "executables",
        )
        check(
            "independent child",
            independent_process.returncode == 0
            and independent.get("verdict") == "INDEPENDENT_OWNER_INTAKE_LEAKAGE_CONTROL",
            independent_process.stdout + independent_process.stderr,
            "independent",
            "executables",
        )
        check(
            "hostile child",
            hostile_process.returncode == 0
            and hostile.get("verdict") == "HOSTILE_MUTATIONS_REJECTED",
            hostile_process.stdout + hostile_process.stderr,
            "hostile",
            "executables",
        )
        check(
            "independent non-importing",
            "pre_a_dynamic_owner_leakage_audit.py"
            not in INDEPENDENT.read_text(encoding="utf-8"),
            True,
            "independence",
            "independence",
        )
        for key in (
            "owner_slots",
            "first_failure_slot",
            "a2_owner_compatible",
            "a2_stochastic_heat",
            "r192_production_map_complete",
            "inverse_stages",
            "prospective_lock",
            "candidate_selection",
            "physical_owner_evidence",
            "proof_comparators",
            "leakage_blocked",
            "owner_branch_verdict",
            "methods_preserved",
            "claim_bearing",
        ):
            check(
                f"lane agreement {key}",
                primary.get("derived", {}).get(key)
                == independent.get("derived", {}).get(key),
                [primary.get("derived", {}).get(key), independent.get("derived", {}).get(key)],
                "equal",
                "cross-check",
            )
        check(
            "hostile count",
            hostile.get("mutations_rejected")
            == hostile.get("assertion_count")
            == manifest["test_oracles"]["hostile_mutation_count"],
            hostile.get("mutations_rejected"),
            manifest["test_oracles"]["hostile_mutation_count"],
            "hostile",
        )
        check(
            "primary minimum",
            primary.get("assertion_count", 0)
            >= manifest["test_oracles"]["primary_minimum_assertions"],
            primary.get("assertion_count"),
            manifest["test_oracles"]["primary_minimum_assertions"],
            "coverage",
        )
        check(
            "independent minimum",
            independent.get("assertion_count", 0)
            >= manifest["test_oracles"]["independent_minimum_assertions"],
            independent.get("assertion_count"),
            manifest["test_oracles"]["independent_minimum_assertions"],
            "coverage",
        )
        derived = primary["derived"]

    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R449.lean"} if skip_lean else lean_run()
    check("Lean compile", skip_lean or lean["status"] == "PASS", lean, "PASS", "Lean")
    payload = {
        "schema": "tect/pre-a-dynamic-owner-leakage-audit-integrated/1.0",
        "run_kind": "integrated",
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "claim_id": manifest["claim_ids"][0],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "verdict": "INTEGRATED_OWNER_INTAKE_LEAKAGE_AUDITED",
        "assertion_count": len(checks),
        "assertions": checks,
        "lean": lean,
        "derived": derived,
        "scope": manifest["scope"],
        "source_hashes": {
            path.relative_to(ROOT).as_posix(): digest(path)
            for path in (MANIFEST, PRIMARY, INDEPENDENT, HOSTILE, LEAN)
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    destination = output if output.is_absolute() else ROOT / output
    atomic_json(destination, payload)
    print(
        f"R-449 INTEGRATED {payload['verdict']} {len(checks)}/{len(checks)} "
        f"Lean={lean['status']}",
        flush=True,
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()
    payload = run(args.output, args.skip_lean)
    if args.self_test:
        assert payload["verdict"] == "INTEGRATED_OWNER_INTAKE_LEAKAGE_AUDITED"
        print("R-449 INTEGRATED SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
