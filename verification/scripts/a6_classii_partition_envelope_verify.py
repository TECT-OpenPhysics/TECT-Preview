#!/usr/bin/env python3
"""Integrated verifier for R-465 finite comparison-envelope diagnostic."""

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
from fractions import Fraction

__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "a6-classii-partition-envelope-manifest.json"
PRIMARY = REPO / "verification" / "scripts" / "a6_classii_partition_envelope.py"
INDEPENDENT = REPO / "codes" / "foundations" / "a6_classii_partition_envelope_independent.py"
HOSTILE = REPO / "codes" / "foundations" / "a6_classii_partition_envelope_hostile.py"
LEAN = REPO / "verification" / "lean" / "Tect" / "R465.lean"
CERTIFICATE = REPO / "strategy" / "a6-classii-partition-envelope-certificate-260831.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A6-CLASSII-UV-POWER-COUNTING"
    / "runs"
    / "2026-08-31-integrated-a6-partition-envelope"
    / "integrated.json"
)


def sha256_normalised(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def add(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "pass": bool(ok), "actual": str(actual), "expected": str(expected)})


def rational(value: Any) -> Fraction:
    return Fraction(str(value))


def pinned_lake() -> Path | None:
    registry_path = REPO / "verification" / "lean" / "registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    toolchain = registry["toolchain"]["toolchain"]
    encoded = toolchain.replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / "lake.exe"
    if candidate.is_file():
        return candidate
    found = shutil.which("lake")
    return Path(found) if found else None


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

    add(rows, "manifest identity", manifest.get("audit_id") == "A6-CLASSII-PARTITION-ENVELOPE-v1", manifest.get("audit_id"), "A6-CLASSII-PARTITION-ENVELOPE-v1")
    add(rows, "result identity", manifest.get("result_id") == "R-465", manifest.get("result_id"), "R-465")
    add(rows, "exploration identity", manifest.get("exploration_id") == "EXP-001340", manifest.get("exploration_id"), "EXP-001340")
    add(rows, "T0 claim firewall", manifest.get("tier") == "T0" and manifest.get("claim_bearing") is False, (manifest.get("tier"), manifest.get("claim_bearing")), ("T0", False))
    add(rows, "methods preserved", all(manifest.get("methods_preserved", {}).values()), manifest.get("methods_preserved"), "all true")
    add(rows, "no pending placeholders", "PENDING" not in json.dumps(manifest), "PENDING" not in json.dumps(manifest), True)

    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        add(rows, f"input {key} exists", path.is_file(), path, True)
        add(rows, f"input {key} hash", path.is_file() and sha256_normalised(path) == item["sha256"], sha256_normalised(path) if path.is_file() else None, item["sha256"])

    file_paths = {"lean": LEAN, "primary": PRIMARY, "independent": INDEPENDENT, "hostile": HOSTILE, "integrated": Path(__file__).resolve(), "certificate": CERTIFICATE}
    for key, path in file_paths.items():
        expected = manifest["files"][key]["sha256"]
        add(rows, f"file {key} exists", path.is_file(), path, True)
        add(rows, f"file {key} hash", path.is_file() and sha256_normalised(path) == expected, sha256_normalised(path) if path.is_file() else None, expected)

    independent_source = INDEPENDENT.read_text(encoding="utf-8") if INDEPENDENT.is_file() else ""
    add(rows, "independent is non-importing", "a6_classii_partition_envelope import" not in independent_source, "no primary import", True)
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    add(rows, "Lean has no escape tokens", not any(re.search(rf"\b{token}\b", lean_source) for token in ("sorry", "admit", "axiom", "unsafe")), "escape tokens absent", True)
    cert_source = CERTIFICATE.read_text(encoding="utf-8") if CERTIFICATE.is_file() else ""
    add(rows, "certificate records comparison boundary", "comparison" in cert_source and "actual correlated" in cert_source and "methods" in cert_source, "boundary language present", True)

    with tempfile.TemporaryDirectory(prefix="r465-audit-") as temp_dir:
        temp = Path(temp_dir)
        p_proc, primary = run_child(PRIMARY, temp / "primary.json")
        i_proc, independent = run_child(INDEPENDENT, temp / "independent.json")
        h_proc, hostile = run_child(HOSTILE, temp / "hostile.json")

    add(rows, "primary subprocess", p_proc.returncode == 0, p_proc.returncode, 0)
    add(rows, "independent subprocess", i_proc.returncode == 0, i_proc.returncode, 0)
    add(rows, "hostile subprocess", h_proc.returncode == 0, h_proc.returncode, 0)
    add(rows, "primary verdict", primary.get("verdict") == "R-465-PRIMARY-PASS", primary.get("verdict"), "R-465-PRIMARY-PASS")
    add(rows, "independent verdict", independent.get("verdict") == "R-465-INDEPENDENT-PASS", independent.get("verdict"), "R-465-INDEPENDENT-PASS")
    add(rows, "hostile verdict", hostile.get("verdict") == "HOSTILE_MUTATIONS_REJECTED", hostile.get("verdict"), "HOSTILE_MUTATIONS_REJECTED")
    p_count = int(primary.get("assertion_summary", {}).get("total", 0))
    i_count = int(independent.get("assertion_summary", {}).get("total", 0))
    h_count = int(hostile.get("assertion_summary", {}).get("total", 0))
    add(rows, "primary assertion minimum", p_count >= manifest["test_oracles"]["primary_minimum_assertions"], p_count, manifest["test_oracles"]["primary_minimum_assertions"])
    add(rows, "independent assertion minimum", i_count >= manifest["test_oracles"]["independent_minimum_assertions"], i_count, manifest["test_oracles"]["independent_minimum_assertions"])
    add(rows, "hostile mutation count", h_count == manifest["test_oracles"]["hostile_mutation_count"], h_count, manifest["test_oracles"]["hostile_mutation_count"])

    p_derived, i_derived = primary.get("derived", {}), independent.get("derived", {})
    for key in ("volume", "mu2", "gamma", "lambda_abs", "threshold_T"):
        add(rows, f"derived {key} agrees", p_derived.get(key) == i_derived.get(key), (p_derived.get(key), i_derived.get(key)), "exact agreement")
    add(rows, "derived comparison constant agrees", p_derived.get("comparison_constant_C_times_volume") == i_derived.get("comparison_constant_K"), (p_derived.get("comparison_constant_C_times_volume"), i_derived.get("comparison_constant_K")), "exact agreement")

    p_coeff = p_derived.get("coefficient_rows", [])
    i_coeff = i_derived.get("coefficient_rows", [])
    add(rows, "coefficient row count", len(p_coeff) == len(manifest["audit"]["cutoffs"]) and len(i_coeff) == len(p_coeff), (len(p_coeff), len(i_coeff)), len(manifest["audit"]["cutoffs"]))
    add(rows, "coefficient rows agree", p_coeff == i_coeff, "exact independent agreement" if p_coeff == i_coeff else (p_coeff, i_coeff), True)
    add(rows, "coefficient rows strictly decrease", all(rational(left["coefficient"]) > rational(right["coefficient"]) for left, right in zip(p_coeff, p_coeff[1:])), p_coeff, "strictly decreasing")
    add(rows, "coefficient rows have exact scale", all((rational(row["coefficient"]) * row["sites"] ** 3) > 0 for row in p_coeff), p_coeff, "positive scaled coefficients")

    p_env = p_derived.get("envelope_rows", [])
    i_env = i_derived.get("envelope_rows", [])
    expected_env_count = len(manifest["audit"]["cutoffs"]) * len(manifest["audit"]["betas"])
    add(rows, "envelope row count", len(p_env) == expected_env_count and len(i_env) == expected_env_count, (len(p_env), len(i_env)), expected_env_count)
    add(rows, "primary envelope rows finite", all(row.get("finite") and row.get("beta_times_coefficient", 0) > 0 and row.get("norm_volume_pressure", 0) > 0 for row in p_env), "all finite/positive pressure", True)
    add(rows, "independent envelope rows finite", all(row.get("finite") and row.get("beta_times_coefficient", 0) > 0 and row.get("norm_volume_pressure", 0) > 0 for row in i_env), "all finite/positive pressure", True)
    add(rows, "envelope row keys agree", {(row.get("beta"), row.get("cutoff")) for row in p_env} == {(row.get("beta"), row.get("cutoff")) for row in i_env}, "same beta/cutoff keys", True)

    firewall = manifest["scope_firewall"]
    add(rows, "partition asymptotic remains open", firewall["actual_partition_asymptotic_closed"] is False, firewall["actual_partition_asymptotic_closed"], False)
    add(rows, "entropy/tightness remain open", firewall["entropy_density_closed"] is False and firewall["tightness_closed"] is False, (firewall["entropy_density_closed"], firewall["tightness_closed"]), (False, False))
    add(rows, "continuum/physical bridges remain open", all(firewall[key] is False for key in ("continuum_closed", "physical_branch_selected", "qft_identity_closed", "yang_mills_identity_closed", "mass_gap_closed")), "all false", True)
    add(rows, "no tier change", firewall["no_tier_change"] is True, firewall["no_tier_change"], True)
    markers = manifest["test_oracles"]["lean_declarations"]
    add(rows, "Lean declaration markers", all(re.search(rf"\b(?:theorem|lemma|example)\s+{re.escape(marker)}\b", lean_source) for marker in markers), markers, "all declarations")

    lake = pinned_lake()
    add(rows, "pinned lake exists", lake is not None, lake, "pinned lake")
    lean_proc = subprocess.run(
        [str(lake), "env", "lean", str(LEAN.relative_to(REPO / "verification" / "lean"))],
        cwd=REPO / "verification" / "lean",
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    ) if lake else None
    add(rows, "Lean compile", lean_proc is not None and lean_proc.returncode == 0, lean_proc.returncode if lean_proc else None, 0)
    add(rows, "Lean compiler no errors", lean_proc is not None and "error:" not in (lean_proc.stdout + lean_proc.stderr).lower(), (lean_proc.stdout + lean_proc.stderr)[-500:] if lean_proc else None, "no error")

    passed = sum(1 for row in rows if row["pass"])
    total = len(rows)
    verdict = "R-465-INTEGRATED-PASS" if passed == total else "R-465-INTEGRATED-FAIL"
    output = {
        "schema": "tect/a6-classii-partition-envelope-integrated-result/1.0",
        "run_kind": "integrated",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "script_version": __version__,
        "verdict": verdict,
        "assertion_summary": {"passed": passed, "total": total, "primary": p_count, "independent": i_count, "hostile": h_count},
        "assertions": rows,
        "subprocesses": {
            "primary": {"returncode": p_proc.returncode, "stdout": p_proc.stdout, "stderr": p_proc.stderr},
            "independent": {"returncode": i_proc.returncode, "stdout": i_proc.stdout, "stderr": i_proc.stderr},
            "hostile": {"returncode": h_proc.returncode, "stdout": h_proc.stdout, "stderr": h_proc.stderr},
            "lean": {"returncode": lean_proc.returncode if lean_proc else None, "stdout": lean_proc.stdout if lean_proc else "", "stderr": lean_proc.stderr if lean_proc else ""},
        },
        "source_reports": {key: sha256_normalised(path) if path.is_file() else None for key, path in {"manifest": MANIFEST, **file_paths}.items()},
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
    print(f"INTEGRATED R-465 {verdict} {passed}/{total}")
    print(f"Evidence: {output_path.resolve()}")
    return 0 if verdict.endswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
