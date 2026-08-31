#!/usr/bin/env python3
"""Integrated verifier for R-464 finite Gibbs integrability/conditioning."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "a6-classii-finite-gibbs-conditioning-manifest.json"
PRIMARY = REPO / "verification" / "scripts" / "a6_classii_finite_gibbs_conditioning.py"
INDEPENDENT = REPO / "codes" / "foundations" / "a6_classii_finite_gibbs_conditioning_independent.py"
HOSTILE = REPO / "codes" / "foundations" / "a6_classii_finite_gibbs_conditioning_hostile.py"
LEAN = REPO / "verification" / "lean" / "Tect" / "R464.lean"
CERTIFICATE = REPO / "strategy" / "a6-classii-finite-gibbs-conditioning-certificate-260831.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A6-CLASSII-UV-POWER-COUNTING"
    / "runs"
    / "2026-08-31-integrated-a6-finite-gibbs-conditioning"
    / "integrated.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def add(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "pass": bool(ok), "actual": str(actual), "expected": str(expected)})


def pinned_lake() -> Path | None:
    registry = json.loads((REPO / "verification" / "lean" / "registry.json").read_text(encoding="utf-8"))
    toolchain = registry["toolchain"]["toolchain"]
    encoded = toolchain.replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / "lake.exe"
    return candidate if candidate.is_file() else (Path(shutil.which("lake")) if shutil.which("lake") else None)


def run_child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    proc = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=REPO,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    report = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return proc, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    add(rows, "manifest identity", manifest.get("audit_id") == "A6-CLASSII-FINITE-GIBBS-CONDITIONING-v1", manifest.get("audit_id"), "A6-CLASSII-FINITE-GIBBS-CONDITIONING-v1")
    add(rows, "result identity", manifest.get("result_id") == "R-464", manifest.get("result_id"), "R-464")
    add(rows, "exploration identity", manifest.get("exploration_id") == "EXP-001339", manifest.get("exploration_id"), "EXP-001339")
    add(rows, "T0 claim firewall", manifest.get("tier") == "T0" and manifest.get("claim_bearing") is False, (manifest.get("tier"), manifest.get("claim_bearing")), ("T0", False))
    add(rows, "methods preserved", all(manifest.get("methods_preserved", {}).values()), manifest.get("methods_preserved"), "all true")
    add(rows, "no pending placeholders", "PENDING" not in json.dumps(manifest), "PENDING" not in json.dumps(manifest), True)

    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        add(rows, f"input {key} exists", path.is_file(), path, True)
        add(rows, f"input {key} hash", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])

    file_paths = {"lean": LEAN, "primary": PRIMARY, "independent": INDEPENDENT, "hostile": HOSTILE, "integrated": Path(__file__).resolve(), "certificate": CERTIFICATE}
    for key, path in file_paths.items():
        expected = manifest["files"][key]["sha256"]
        add(rows, f"file {key} exists", path.is_file(), path, True)
        add(rows, f"file {key} hash", path.is_file() and sha256(path) == expected, sha256(path) if path.is_file() else None, expected)

    independent_source = INDEPENDENT.read_text(encoding="utf-8") if INDEPENDENT.is_file() else ""
    add(rows, "independent is non-importing", "a6_classii_finite_gibbs_conditioning import" not in independent_source, "no primary import", True)
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    add(rows, "Lean has no escape tokens", not any(re.search(rf"\b{token}\b", lean_source) for token in ("sorry", "admit", "axiom", "unsafe")), "escape tokens absent", True)
    cert_source = CERTIFICATE.read_text(encoding="utf-8") if CERTIFICATE.is_file() else ""
    add(rows, "certificate records finite boundary", "positive-mass tube" in cert_source and "cutoff-uniform" in cert_source, "required boundary language", True)

    with tempfile.TemporaryDirectory(prefix="r464-audit-") as temp_dir:
        temp = Path(temp_dir)
        p_proc, primary = run_child(PRIMARY, temp / "primary.json")
        i_proc, independent = run_child(INDEPENDENT, temp / "independent.json")
        h_proc, hostile = run_child(HOSTILE, temp / "hostile.json")

    add(rows, "primary subprocess", p_proc.returncode == 0, p_proc.returncode, 0)
    add(rows, "independent subprocess", i_proc.returncode == 0, i_proc.returncode, 0)
    add(rows, "hostile subprocess", h_proc.returncode == 0, h_proc.returncode, 0)
    add(rows, "primary verdict", primary.get("verdict") == "R-464-PRIMARY-PASS", primary.get("verdict"), "R-464-PRIMARY-PASS")
    add(rows, "independent verdict", independent.get("verdict") == "R-464-INDEPENDENT-PASS", independent.get("verdict"), "R-464-INDEPENDENT-PASS")
    add(rows, "hostile verdict", hostile.get("verdict") == "HOSTILE_MUTATIONS_REJECTED", hostile.get("verdict"), "HOSTILE_MUTATIONS_REJECTED")
    p_count = int(primary.get("assertion_summary", {}).get("total", 0))
    i_count = int(independent.get("assertion_summary", {}).get("total", 0))
    h_count = int(hostile.get("assertion_summary", {}).get("total", 0))
    add(rows, "primary assertion minimum", p_count >= manifest["test_oracles"]["primary_minimum_assertions"], p_count, manifest["test_oracles"]["primary_minimum_assertions"])
    add(rows, "independent assertion minimum", i_count >= manifest["test_oracles"]["independent_minimum_assertions"], i_count, manifest["test_oracles"]["independent_minimum_assertions"])
    add(rows, "hostile mutation count", h_count == manifest["test_oracles"]["hostile_mutation_count"], h_count, manifest["test_oracles"]["hostile_mutation_count"])

    p_derived, i_derived = primary.get("derived", {}), independent.get("derived", {})
    for key in ("mu2", "lambda_abs", "gamma", "threshold_T", "lower_constant_C"):
        add(rows, f"derived {key} agrees", p_derived.get(key) == i_derived.get(key), (p_derived.get(key), i_derived.get(key)), "exact agreement")
    p_rows = p_derived.get("finite_cutoff_rows", [])
    add(rows, "finite cutoff rows present", len(p_rows) == len(manifest["audit"]["cutoffs"]), len(p_rows), len(manifest["audit"]["cutoffs"]))
    add(rows, "finite cutoff coefficients positive", all(row.get("positive") for row in p_rows), p_rows, "all true")
    branch_rows = p_derived.get("pure_singlet_branch_rows", [])
    add(rows, "pure-singlet rows present", len(branch_rows) == len(manifest["audit"]["cutoffs"]), len(branch_rows), len(manifest["audit"]["cutoffs"]))
    add(rows, "pure-singlet mass zero", all(row.get("pure_singlet_lebesgue_mass") == "0" for row in branch_rows), branch_rows, "all zero")
    add(rows, "tube contract remains open", manifest["scope_firewall"]["branch_tube_probability_closed"] is False and manifest["scope_firewall"]["entropy_closed"] is False, manifest["scope_firewall"], "false/false")
    add(rows, "uniformity remains open", manifest["scope_firewall"]["cutoff_uniform_closed"] is False and manifest["scope_firewall"]["tightness_closed"] is False, manifest["scope_firewall"], "false/false")

    markers = manifest["test_oracles"]["lean_declarations"]
    add(rows, "Lean declaration markers", all(re.search(rf"\b(?:theorem|lemma|example)\s+{re.escape(marker)}\b", lean_source) for marker in markers), markers, "all declarations")
    lake = pinned_lake()
    add(rows, "pinned lake exists", lake is not None, lake, "pinned lake")
    lean_proc = subprocess.run([str(lake), "env", "lean", str(LEAN.relative_to(REPO / "verification" / "lean"))], cwd=REPO / "verification" / "lean", text=True, encoding="utf-8", errors="replace", capture_output=True, check=False) if lake else None
    add(rows, "Lean compile", lean_proc is not None and lean_proc.returncode == 0, lean_proc.returncode if lean_proc else None, 0)
    add(rows, "Lean compiler no errors", lean_proc is not None and "error:" not in (lean_proc.stdout + lean_proc.stderr).lower(), (lean_proc.stdout + lean_proc.stderr)[-500:] if lean_proc else None, "no error")

    passed = sum(1 for row in rows if row["pass"])
    total = len(rows)
    verdict = "R-464-INTEGRATED-PASS" if passed == total else "R-464-INTEGRATED-FAIL"
    output = {
        "schema": "tect/a6-classii-finite-gibbs-conditioning-integrated-result/1.0",
        "run_kind": "integrated",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "script_version": __version__,
        "verdict": verdict,
        "assertion_summary": {"passed": passed, "total": total, "primary": p_count, "independent": i_count, "hostile": h_count},
        "assertions": rows,
        "subprocesses": {"primary": {"returncode": p_proc.returncode, "stdout": p_proc.stdout, "stderr": p_proc.stderr}, "independent": {"returncode": i_proc.returncode, "stdout": i_proc.stdout, "stderr": i_proc.stderr}, "hostile": {"returncode": h_proc.returncode, "stdout": h_proc.stdout, "stderr": h_proc.stderr}, "lean": {"returncode": lean_proc.returncode if lean_proc else None, "stdout": lean_proc.stdout if lean_proc else "", "stderr": lean_proc.stderr if lean_proc else ""}},
        "source_reports": {key: sha256(path) if path.is_file() else None for key, path in {"manifest": MANIFEST, **file_paths}.items()},
        "evidence_level": manifest["evidence_level"],
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "non_claims": manifest["non_claims"],
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "failures": [row["name"] for row in rows if not row["pass"]],
    }
    output_path = args.output if args.output.is_absolute() else REPO / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"INTEGRATED R-464 {verdict} {passed}/{total}")
    print(f"Evidence: {output_path.resolve()}")
    return 0 if verdict.endswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
