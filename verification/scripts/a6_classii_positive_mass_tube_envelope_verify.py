#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean verifier for R-466."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import re
import shutil
import subprocess
import sys
import tempfile
sys.set_int_max_str_digits(1_000_000)
from fractions import Fraction
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "a6-classii-positive-mass-tube-envelope-manifest.json"
PRIMARY = REPO / "verification" / "scripts" / "a6_classii_positive_mass_tube_envelope.py"
INDEPENDENT = REPO / "codes" / "foundations" / "a6_classii_positive_mass_tube_envelope_independent.py"
HOSTILE = REPO / "codes" / "foundations" / "a6_classii_positive_mass_tube_envelope_hostile.py"
LEAN = REPO / "verification" / "lean" / "Tect" / "R466.lean"
CERTIFICATE = REPO / "strategy" / "a6-classii-positive-mass-tube-envelope-certificate-260831.md"
DEFAULT_OUTPUT = REPO / "claims" / "A6-CLASSII-UV-POWER-COUNTING" / "runs" / "2026-08-31-integrated-a6-positive-mass-tube-envelope" / "integrated.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def add(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "pass": bool(ok), "actual": str(actual), "expected": str(expected)})


def q(value: Any) -> Fraction:
    return Fraction(str(value))


def lake_path() -> Path | None:
    registry = json.loads((REPO / "verification" / "lean" / "registry.json").read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / "lake.exe"
    if candidate.is_file():
        return candidate
    found = shutil.which("lake")
    return Path(found) if found else None


def run_child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    proc = subprocess.run([sys.executable, str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    report = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return proc, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    add(rows, "manifest identity", manifest.get("audit_id") == "A6-CLASSII-POSITIVE-MASS-TUBE-ENVELOPE-v1", manifest.get("audit_id"), "A6-CLASSII-POSITIVE-MASS-TUBE-ENVELOPE-v1")
    add(rows, "result identity", manifest.get("result_id") == "R-466", manifest.get("result_id"), "R-466")
    add(rows, "exploration identity", manifest.get("exploration_id") == "EXP-001341", manifest.get("exploration_id"), "EXP-001341")
    add(rows, "T0 claim firewall", manifest.get("tier") == "T0" and manifest.get("claim_bearing") is False, (manifest.get("tier"), manifest.get("claim_bearing")), ("T0", False))
    add(rows, "methods preserved", all(manifest.get("methods_preserved", {}).values()), manifest.get("methods_preserved"), "all true")
    add(rows, "no unresolved placeholders", "PLACEHOLDER" not in json.dumps(manifest), "PLACEHOLDER" not in json.dumps(manifest), True)

    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        add(rows, f"input {key} exists", path.is_file(), path, True)
        add(rows, f"input {key} hash", path.is_file() and digest(path) == item["sha256"], digest(path) if path.is_file() else None, item["sha256"])

    file_paths = {"lean": LEAN, "primary": PRIMARY, "independent": INDEPENDENT, "hostile": HOSTILE, "integrated": Path(__file__).resolve(), "certificate": CERTIFICATE}
    for key, path in file_paths.items():
        expected = manifest["files"][key]["sha256"]
        add(rows, f"file {key} exists", path.is_file(), path, True)
        add(rows, f"file {key} hash", path.is_file() and digest(path) == expected, digest(path) if path.is_file() else None, expected)
    independent_source = INDEPENDENT.read_text(encoding="utf-8") if INDEPENDENT.is_file() else ""
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    cert_source = CERTIFICATE.read_text(encoding="utf-8") if CERTIFICATE.is_file() else ""
    add(rows, "independent is non-importing", "a6_classii_positive_mass_tube_envelope import" not in independent_source, "no primary import", True)
    add(rows, "Lean has no escape tokens", not any(re.search(rf"\b{token}\b", lean_source) for token in ("sorry", "admit", "axiom", "unsafe")), "escape tokens absent", True)
    add(rows, "certificate states conditional boundary", all(token in cert_source for token in ("owner-neutral", "conditional", "uniform")), "boundary language present", True)

    with tempfile.TemporaryDirectory(prefix="r466-audit-") as temp_dir:
        temp = Path(temp_dir)
        p_proc, primary = run_child(PRIMARY, temp / "primary.json")
        i_proc, independent = run_child(INDEPENDENT, temp / "independent.json")
        h_proc, hostile = run_child(HOSTILE, temp / "hostile.json")
    add(rows, "primary subprocess", p_proc.returncode == 0, p_proc.returncode, 0)
    add(rows, "independent subprocess", i_proc.returncode == 0, i_proc.returncode, 0)
    add(rows, "hostile subprocess", h_proc.returncode == 0, h_proc.returncode, 0)
    add(rows, "primary verdict", primary.get("verdict") == "R-466-PRIMARY-PASS", primary.get("verdict"), "R-466-PRIMARY-PASS")
    add(rows, "independent verdict", independent.get("verdict") == "R-466-INDEPENDENT-PASS", independent.get("verdict"), "R-466-INDEPENDENT-PASS")
    add(rows, "hostile verdict", hostile.get("verdict") == "HOSTILE_MUTATIONS_REJECTED", hostile.get("verdict"), "HOSTILE_MUTATIONS_REJECTED")
    p_count = int(primary.get("assertion_summary", {}).get("total", 0))
    i_count = int(independent.get("assertion_summary", {}).get("total", 0))
    h_count = int(hostile.get("assertion_summary", {}).get("total", 0))
    add(rows, "primary assertion minimum", p_count >= manifest["test_oracles"]["primary_minimum_assertions"], p_count, manifest["test_oracles"]["primary_minimum_assertions"])
    add(rows, "independent assertion minimum", i_count >= manifest["test_oracles"]["independent_minimum_assertions"], i_count, manifest["test_oracles"]["independent_minimum_assertions"])
    add(rows, "hostile mutation count", h_count == manifest["test_oracles"]["hostile_mutation_count"], h_count, manifest["test_oracles"]["hostile_mutation_count"])

    p_rows = primary.get("derived", {}).get("rows", [])
    i_rows = independent.get("derived", {}).get("rows", [])
    add(rows, "row count agrees", len(p_rows) == len(i_rows) == len(manifest["audit"]["cutoffs"]) * len(manifest["audit"]["betas"]), (len(p_rows), len(i_rows)), len(manifest["audit"]["cutoffs"]) * len(manifest["audit"]["betas"]))
    p_keys = {(row.get("beta"), row.get("cutoff")) for row in p_rows}
    i_keys = {(row.get("beta"), row.get("cutoff")) for row in i_rows}
    add(rows, "row keys agree", p_keys == i_keys, (p_keys, i_keys), "same beta/cutoff keys")
    add(rows, "exact rational rows agree", [(r.get("beta"), r.get("cutoff"), r.get("coefficient"), r.get("coefficient_times_sites_cubed"), r.get("tube_box_volume_exact")) for r in p_rows] == [(r.get("beta"), r.get("cutoff"), r.get("coefficient"), r.get("coefficient_times_sites_cubed"), r.get("tube_box_volume_exact")) for r in i_rows], "exact fields agree", True)
    close_logs = all(abs(float(a.get("log_probability_lower", 0.0)) - float(b.get("log_probability_lower", 0.0))) < 1e-8 for a, b in zip(p_rows, i_rows))
    add(rows, "log lower bounds agree", close_logs, "within 1e-8" if close_logs else "mismatch", True)
    add(rows, "positive volumes", all(q(row["tube_box_volume_exact"]) > 0 for row in p_rows), "all positive", True)
    add(rows, "finite lower logs", all(row.get("finite") and math.isfinite(float(row.get("log_probability_lower", 0.0))) for row in p_rows), "all finite", True)
    for beta in manifest["audit"]["betas"]:
        logs = [row["log_probability_lower"] for row in p_rows if row["beta"] == beta]
        add(rows, f"strict coarse decay beta={beta}", all(left > right for left, right in zip(logs, logs[1:])), logs, "strictly decreasing")
    firewall = manifest["scope_firewall"]
    add(rows, "conditional lower bound closed", firewall["finite_conditional_lower_bound_closed"] is True, firewall["finite_conditional_lower_bound_closed"], True)
    add(rows, "source owner and uniformity open", firewall["source_owned_tube_admitted"] is False and firewall["cutoff_uniform_closed"] is False, (firewall["source_owned_tube_admitted"], firewall["cutoff_uniform_closed"]), (False, False))
    add(rows, "downstream bridges open", all(firewall[key] is False for key in ("entropy_density_closed", "tightness_closed", "continuum_closed", "physical_branch_selected", "qft_identity_closed", "yang_mills_identity_closed", "mass_gap_closed")), "all false", True)
    add(rows, "no tier change", firewall["no_tier_change"] is True, firewall["no_tier_change"], True)
    add(rows, "Lean declaration markers", all(re.search(rf"\b(?:theorem|lemma|example)\s+{re.escape(marker)}\b", lean_source) for marker in manifest["test_oracles"]["lean_declarations"]), manifest["test_oracles"]["lean_declarations"], "all declarations")

    lake = lake_path()
    add(rows, "pinned lake exists", lake is not None, lake, "pinned lake")
    lean_proc = subprocess.run([str(lake), "env", "lean", str(LEAN.relative_to(REPO / "verification" / "lean"))], cwd=REPO / "verification" / "lean", text=True, encoding="utf-8", errors="replace", capture_output=True, check=False) if lake else None
    add(rows, "Lean compile", lean_proc is not None and lean_proc.returncode == 0, lean_proc.returncode if lean_proc else None, 0)
    add(rows, "Lean compiler no errors", lean_proc is not None and "error:" not in ((lean_proc.stdout + lean_proc.stderr).lower()), (lean_proc.stdout + lean_proc.stderr)[-500:] if lean_proc else None, "no error")

    passed = sum(item["pass"] for item in rows)
    total = len(rows)
    verdict = "R-466-INTEGRATED-PASS" if passed == total else "R-466-INTEGRATED-FAIL"
    output = {
        "schema": "tect/a6-classii-positive-mass-tube-envelope-integrated-result/1.0",
        "run_kind": "integrated",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "script_version": __version__,
        "verdict": verdict,
        "assertion_summary": {"passed": passed, "total": total, "primary": p_count, "independent": i_count, "hostile": h_count},
        "assertions": rows,
        "subprocesses": {"primary": {"returncode": p_proc.returncode, "stdout": p_proc.stdout, "stderr": p_proc.stderr}, "independent": {"returncode": i_proc.returncode, "stdout": i_proc.stdout, "stderr": i_proc.stderr}, "hostile": {"returncode": h_proc.returncode, "stdout": h_proc.stdout, "stderr": h_proc.stderr}, "lean": {"returncode": lean_proc.returncode if lean_proc else None, "stdout": lean_proc.stdout if lean_proc else "", "stderr": lean_proc.stderr if lean_proc else ""}},
        "source_reports": {"manifest": digest(MANIFEST), **{key: digest(path) if path.is_file() else None for key, path in file_paths.items()}},
        "evidence_level": manifest["evidence_level"],
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "non_claims": manifest["non_claims"],
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "failures": [item["name"] for item in rows if not item["pass"]],
    }
    output_path = args.output if args.output.is_absolute() else REPO / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"INTEGRATED R-466 {verdict} {passed}/{total}")
    print(f"Evidence: {output_path.resolve()}")
    return 0 if verdict.endswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
