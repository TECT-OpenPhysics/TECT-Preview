#!/usr/bin/env python3
"""Integrated verifier for the R-463 active-branch tube-metric package."""

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
MANIFEST = REPO / "strategy" / "a6-classii-active-branch-tube-metric-manifest.json"
PRIMARY = REPO / "verification" / "scripts" / "a6_classii_active_branch_tube_metric.py"
INDEPENDENT = REPO / "codes" / "foundations" / "a6_classii_active_branch_tube_metric_independent.py"
HOSTILE = REPO / "codes" / "foundations" / "a6_classii_active_branch_tube_metric_hostile.py"
LEAN = REPO / "verification" / "lean" / "Tect" / "R463.lean"
CERTIFICATE = REPO / "strategy" / "a6-classii-active-branch-tube-metric-certificate-260831.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A6-CLASSII-UV-POWER-COUNTING"
    / "runs"
    / "2026-08-31-integrated-a6-active-branch-tube-metric"
    / "integrated.json"
)


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def add(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "pass": bool(ok), "actual": str(actual), "expected": str(expected)})


def pinned_lake() -> Path | None:
    registry = json.loads((REPO / "verification" / "lean" / "registry.json").read_text(encoding="utf-8"))
    toolchain = registry["toolchain"]["toolchain"]
    encoded = toolchain.replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / "lake.exe"
    if candidate.is_file():
        return candidate
    found = shutil.which("lake")
    return Path(found) if found else None


def run_child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    completed = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=REPO,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    report = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return completed, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    add(rows, "manifest identity", manifest.get("audit_id") == "A6-CLASSII-ACTIVE-BRANCH-TUBE-METRIC-v1", manifest.get("audit_id"), "A6-CLASSII-ACTIVE-BRANCH-TUBE-METRIC-v1")
    add(rows, "result identity", manifest.get("result_id") == "R-463", manifest.get("result_id"), "R-463")
    add(rows, "T0 claim firewall", manifest.get("tier") == "T0" and manifest.get("claim_bearing") is False, (manifest.get("tier"), manifest.get("claim_bearing")), ("T0", False))
    add(rows, "functional method preserved", manifest["methods_preserved"]["a6_a7_functional_unchanged"] is True, manifest["methods_preserved"], True)
    add(rows, "owner order preserved", manifest["methods_preserved"]["owner_order_unchanged"] is True, manifest["methods_preserved"], True)
    add(rows, "no placeholders", "PENDING" not in json.dumps(manifest), manifest, "no pending placeholders")

    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        add(rows, f"input {key} exists", path.is_file(), path, True)
        add(rows, f"input {key} hash", path.is_file() and item["sha256"] != "PENDING" and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])

    file_paths = {"lean": LEAN, "primary": PRIMARY, "independent": INDEPENDENT, "hostile": HOSTILE, "integrated": Path(__file__).resolve(), "certificate": CERTIFICATE}
    for key, path in file_paths.items():
        expected = manifest["files"][key]["sha256"]
        add(rows, f"file {key} exists", path.is_file(), path, True)
        add(rows, f"file {key} hash", path.is_file() and expected != "PENDING" and sha256(path) == expected, sha256(path) if path.is_file() else None, expected)

    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    add(rows, "Lean source has no escape tokens", not any(re.search(rf"\b{re.escape(token)}\b", lean_source) for token in ("sorry", "admit", "axiom", "unsafe")), lean_source, "none")
    independent_source = INDEPENDENT.read_text(encoding="utf-8") if INDEPENDENT.is_file() else ""
    add(rows, "independent does not import primary", "a6_classii_active_branch_tube_metric import" not in independent_source, independent_source[:160], "no primary import")

    with tempfile.TemporaryDirectory(prefix="r463-audit-") as temp_dir:
        temp = Path(temp_dir)
        primary_proc, primary = run_child(PRIMARY, temp / "primary.json")
        independent_proc, independent = run_child(INDEPENDENT, temp / "independent.json")
        hostile_proc, hostile = run_child(HOSTILE, temp / "hostile.json")

    add(rows, "primary subprocess", primary_proc.returncode == 0, primary_proc.returncode, 0)
    add(rows, "independent subprocess", independent_proc.returncode == 0, independent_proc.returncode, 0)
    add(rows, "hostile subprocess", hostile_proc.returncode == 0, hostile_proc.returncode, 0)
    add(rows, "primary verdict", primary.get("verdict") == "R-463-PRIMARY-PASS", primary.get("verdict"), "R-463-PRIMARY-PASS")
    add(rows, "independent verdict", independent.get("verdict") == "R-463-INDEPENDENT-PASS", independent.get("verdict"), "R-463-INDEPENDENT-PASS")
    add(rows, "hostile verdict", hostile.get("verdict") == "HOSTILE_MUTATIONS_REJECTED", hostile.get("verdict"), "HOSTILE_MUTATIONS_REJECTED")

    p_count = int(primary.get("assertion_summary", {}).get("total", 0))
    i_count = int(independent.get("assertion_summary", {}).get("total", 0))
    h_count = int(hostile.get("assertion_summary", {}).get("total", 0))
    add(rows, "primary assertion minimum", p_count >= int(manifest["test_oracles"]["primary_minimum_assertions"]), p_count, manifest["test_oracles"]["primary_minimum_assertions"])
    add(rows, "independent assertion minimum", i_count >= int(manifest["test_oracles"]["independent_minimum_assertions"]), i_count, manifest["test_oracles"]["independent_minimum_assertions"])
    add(rows, "hostile mutation count", h_count == int(manifest["test_oracles"]["hostile_mutation_count"]), h_count, manifest["test_oracles"]["hostile_mutation_count"])

    p_derived = primary.get("derived", {})
    i_derived = independent.get("derived", {})
    for key in ("coefficients", "determinant", "trace", "lambda_radial", "kappa_angular"):
        add(rows, f"{key} agrees exactly", p_derived.get(key) == i_derived.get(key), (p_derived.get(key), i_derived.get(key)), "same exact value")
    add(rows, "active grid diagnostics present", int(p_derived.get("active_grid_points", 0)) > 0 and int(i_derived.get("active_grid_points", 0)) > 0, (p_derived.get("active_grid_points"), i_derived.get("active_grid_points")), ">0")
    add(rows, "shell diagnostics present", len(p_derived.get("shell_reports", [])) == len(manifest["audit"]["tube_thresholds"]), len(p_derived.get("shell_reports", [])), len(manifest["audit"]["tube_thresholds"]))
    add(rows, "subunit proxy recorded", any(item.get("bound_lt_one") for report in p_derived.get("shell_reports", []) for item in report.get("proxy_bounds", [])), True, True)
    add(rows, "flat barrier agrees", p_derived.get("flat_energy_barrier") == "0" and i_derived.get("flat_energy_barrier") == "0", (p_derived.get("flat_energy_barrier"), i_derived.get("flat_energy_barrier")), "0")
    add(rows, "flat no-suppression agrees", p_derived.get("flat_proxy_bound") == i_derived.get("flat_proxy_bound"), (p_derived.get("flat_proxy_bound"), i_derived.get("flat_proxy_bound")), "same bound")
    add(rows, "tube remains unclosed", manifest["scope_firewall"]["branch_tube_probability_closed"] is False and manifest["scope_firewall"]["entropy_closed"] is False and manifest["scope_firewall"]["tightness_closed"] is False, manifest["scope_firewall"], "false/false/false")

    markers = manifest["test_oracles"]["lean_declarations"]
    add(rows, "Lean declaration markers", all(re.search(rf"\b(?:theorem|lemma|example)\s+{re.escape(marker)}\b", lean_source) for marker in markers), markers, "all declarations")
    lake = pinned_lake()
    add(rows, "pinned lake exists", lake is not None, lake, "pinned elan lake")
    lean_proc = subprocess.run([str(lake), "env", "lean", str(LEAN.relative_to(REPO / "verification" / "lean"))], cwd=REPO / "verification" / "lean", text=True, encoding="utf-8", errors="replace", capture_output=True, check=False) if lake is not None else None
    add(rows, "Lean compile", lean_proc is not None and lean_proc.returncode == 0, lean_proc.returncode if lean_proc else None, 0)
    add(rows, "Lean compiler clean", lean_proc is not None and "error:" not in (lean_proc.stdout + lean_proc.stderr).lower(), (lean_proc.stdout + lean_proc.stderr)[-500:] if lean_proc else None, "no error")

    passed = sum(1 for row in rows if row["pass"])
    total = len(rows)
    verdict = "R-463-INTEGRATED-PASS" if passed == total else "R-463-INTEGRATED-FAIL"
    output = {
        "schema": "tect/a6-classii-active-branch-tube-metric-integrated-result/1.0",
        "run_kind": "integrated",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "script_version": __version__,
        "verdict": verdict,
        "assertion_summary": {"passed": passed, "total": total, "primary": p_count, "independent": i_count, "hostile": h_count},
        "assertions": rows,
        "subprocesses": {
            "primary": {"returncode": primary_proc.returncode, "stdout": primary_proc.stdout, "stderr": primary_proc.stderr},
            "independent": {"returncode": independent_proc.returncode, "stdout": independent_proc.stdout, "stderr": independent_proc.stderr},
            "hostile": {"returncode": hostile_proc.returncode, "stdout": hostile_proc.stdout, "stderr": hostile_proc.stderr},
            "lean": {"returncode": lean_proc.returncode if lean_proc else None, "stdout": lean_proc.stdout if lean_proc else "", "stderr": lean_proc.stderr if lean_proc else ""},
        },
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
    print(f"INTEGRATED R-463 {verdict} {passed}/{total}")
    print(f"Evidence: {output_path.resolve()}")
    return 0 if verdict.endswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
