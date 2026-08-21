"""Run the pinned Lean kernel cross-check for the exact R-058 budget implication.

The registered primary and independent R-058 engines supply the numerical
certificate c > 0.9.  Lean checks only the ordered-field consequence for
gamma = 81/50 and p >= 1: c > gamma/(3p) and c - gamma/3 > 0.3.  It does not
reprove the degree-65536 source ratio, Fierz/resolvent estimates, or any
joint-source, measure, physical-empty, or limit statement.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
LEAN_DIR = REPO / "verification" / "lean"
ENTRYPOINT = LEAN_DIR / "Tect" / "R058.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
LAKEFILE = LEAN_DIR / "lakefile.toml"
LOCKFILE = LEAN_DIR / "lake-manifest.json"
A13_MANIFEST = (
    REPO
    / "claims"
    / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
    / "classii_relative_phase_source_obstruction_manifest.json"
)
A13_STATUS = (
    REPO
    / "claims"
    / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
    / "status.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
    / "runs"
    / "2026-08-21-lean-r058-budget-crosscheck"
    / "result.json"
)
REGISTERED_A13_MANIFEST_SHA256 = "fb64119fcc65f73643d8fd3f9beb64f6c07fd72d373b613c6cbcc8463dbd62bb"
REGISTERED_A13_STATUS_SHA256 = "1f18f688c5f9dfa5ecaeb4bec8072c7cc67d751b6b4cc5ea938ebd879947c1b1"
THEOREM_MARKERS = (
    "allowance_le_gamma_third",
    "budget_gap",
    "gamma_third_exact",
)
FORBIDDEN_SOURCE_TOKENS = ("sorry", "admit", "axiom", "unsafe")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_lake() -> str | None:
    home = Path.home()
    pin = TOOLCHAIN.read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    toolchain_bin = home / ".elan" / "toolchains" / encoded / "bin"
    local_name = "lake.exe" if os.name == "nt" else "lake"
    local_lake = toolchain_bin / local_name
    if local_lake.is_file():
        return str(local_lake)
    found = shutil.which("lake")
    if found:
        return found
    candidates = []
    if os.name == "nt":
        candidates.extend((home / ".elan" / "bin" / "lake.exe", home / ".elan" / "bin" / "lake"))
    else:
        candidates.append(home / ".elan" / "bin" / "lake")
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def check(condition: bool, name: str, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
    if not condition:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")


def exact_decimal(value: Any) -> Fraction:
    return Fraction(Decimal(str(value)))


def fraction_marker(value: Fraction) -> str:
    return f"{value.numerator} / {value.denominator}"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    source_text = ENTRYPOINT.read_text(encoding="utf-8")
    manifest = json.loads(A13_MANIFEST.read_text(encoding="utf-8"))
    lake = find_lake()

    check(ENTRYPOINT.is_file(), "Lean entrypoint exists", str(ENTRYPOINT), True, rows)
    check(TOOLCHAIN.is_file(), "Lean toolchain pin exists", str(TOOLCHAIN), True, rows)
    check(LAKEFILE.is_file(), "Lakefile exists", str(LAKEFILE), True, rows)
    check(LOCKFILE.is_file(), "Lake dependency lock exists", str(LOCKFILE), True, rows)
    check(lake is not None, "lake executable is available", lake, "PATH or pinned local toolchain", rows)
    manifest_sha = sha256(A13_MANIFEST)
    status_sha = sha256(A13_STATUS)
    check(manifest_sha == REGISTERED_A13_MANIFEST_SHA256, "R-058 manifest hash", manifest_sha, REGISTERED_A13_MANIFEST_SHA256, rows)
    check(status_sha == REGISTERED_A13_STATUS_SHA256, "R-058 status hash", status_sha, REGISTERED_A13_STATUS_SHA256, rows)
    check(
        manifest.get("schema") == "tect/a13-classii-relative-phase-source-obstruction/1.0",
        "R-058 authority schema",
        manifest.get("schema"),
        "tect/a13-classii-relative-phase-source-obstruction/1.0",
        rows,
    )
    check(
        manifest.get("claim_id") == "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION",
        "R-058 claim identity",
        manifest.get("claim_id"),
        "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION",
        rows,
    )

    for key in ("a1_manifest", "a12_status", "a12_obstruction_manifest"):
        reference = manifest["authority"][key]
        path = REPO / reference["path"]
        actual = sha256(path) if path.is_file() else None
        check(path.is_file() and actual == reference["sha256"], f"authority hash {key}", actual, reference["sha256"], rows)
    for key in ("primary", "independent", "verifier", "proof_note"):
        reference = manifest["sources"][key]
        path = REPO / reference["path"]
        actual = sha256(path) if path.is_file() else None
        check(path.is_file() and actual == reference["sha256"], f"source hash {key}", actual, reference["sha256"], rows)

    check(all(marker in source_text for marker in THEOREM_MARKERS), "Lean theorem markers present", [m for m in THEOREM_MARKERS if m in source_text], list(THEOREM_MARKERS), rows)
    forbidden_hits = [token for token in FORBIDDEN_SOURCE_TOKENS if re.search(rf"\b{token}\b", source_text)]
    check(forbidden_hits == [], "Lean escape tokens absent", forbidden_hits, [], rows)

    decision_floor = exact_decimal(manifest["certificate"]["decision_floor"])
    required_margin = exact_decimal(manifest["certificate"]["required_margin_over_gamma_third"])
    gamma_third = exact_decimal(manifest["derived_oracles"]["gamma_over_three"])
    reference_p = exact_decimal(manifest["budget"]["reference_p"])
    primary_ratio = exact_decimal(manifest["derived_oracles"]["primary_source_ratio"])
    independent_ratio = exact_decimal(manifest["derived_oracles"]["independent_source_ratio"])
    gamma = 3 * gamma_third
    reference_allowance = gamma / (3 * reference_p)
    check(primary_ratio == independent_ratio, "primary and independent source ratios agree", str(primary_ratio), str(independent_ratio), rows)
    check(primary_ratio > decision_floor, "registered certificate clears decision floor", str(primary_ratio), f"> {decision_floor}", rows)
    check(reference_p >= 1, "reference p is in all-p domain", str(reference_p), ">= 1", rows)
    check(reference_allowance <= gamma_third, "all-p allowance is at most gamma/3", str(reference_allowance), f"<= {gamma_third}", rows)
    check(primary_ratio > reference_allowance, "certificate clears reference allowance", str(primary_ratio), f"> {reference_allowance}", rows)
    check(primary_ratio - gamma_third > required_margin, "certificate clears required margin", str(primary_ratio - gamma_third), f"> {required_margin}", rows)
    decision_marker = f"({decision_floor.numerator} : ℚ) / {decision_floor.denominator}"
    gamma_marker = f"({gamma.numerator} : ℚ) / ({gamma.denominator} * (3 * p))"
    margin_marker = f"({required_margin.numerator} : ℚ) / {required_margin.denominator}"
    check(decision_marker in source_text, "Lean decision-floor marker", decision_marker, True, rows)
    check(gamma_marker in source_text, "Lean gamma marker", gamma_marker, True, rows)
    check(margin_marker in source_text, "Lean margin marker", margin_marker, True, rows)
    check("50 * (3 * p)" in source_text, "Lean allowance denominator marker", "50 * (3 * p)", True, rows)

    command = [lake, "env", "lean", str(ENTRYPOINT.relative_to(LEAN_DIR))]
    completed = subprocess.run(command, cwd=LEAN_DIR, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    check(completed.returncode == 0, "Lean kernel compile", completed.returncode, 0, rows)
    check(completed.stdout.strip() == "", "Lean stdout is clean", completed.stdout, "", rows)
    check(completed.stderr.strip() == "", "Lean stderr is clean", completed.stderr, "", rows)

    payload: dict[str, Any] = {
        "schema": "tect/lean-kernel-crosscheck/1.0",
        "run_kind": "lean-kernel-crosscheck",
        "result_id": "R-058-LEAN-KERNEL-CROSSCHECK",
        "claim_ids": ["A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"],
        "formal_refs": {"results": ["R-058"], "negatives": ["NG-2026-07-21-A13-RELATIVE-PHASE-SOURCE-BUDGET"], "events": []},
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "command": command,
        "toolchain": TOOLCHAIN.read_text(encoding="utf-8").strip(),
        "source_hashes": {
            "toolchain": sha256(TOOLCHAIN),
            "lakefile": sha256(LAKEFILE),
            "lake_manifest": sha256(LOCKFILE),
            "entrypoint": sha256(ENTRYPOINT),
            "a13_manifest": manifest_sha,
            "a13_status": status_sha,
        },
        "registered_certificate": {
            "primary_source_ratio": str(primary_ratio),
            "decision_floor": str(decision_floor),
            "gamma": str(gamma),
            "gamma_over_three": str(gamma_third),
            "reference_p": str(reference_p),
            "reference_allowance": str(reference_allowance),
            "required_margin": str(required_margin),
        },
        "lean_stdout": completed.stdout,
        "lean_stderr": completed.stderr,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "python": sys.version,
        "boundary": (
            "Kernel-checks only the exact ordered-field budget implication from "
            "the registered executed lower-bound certificate. It does not reprove "
            "the degree-65536 source ratio, Fierz/resolvent estimates, joint-source "
            "cancellation, A11/A13 one-use, Nelson/measure, physical-empty, Sector-A, "
            "Pre-A, or any regulator/thermodynamic/continuum limit."
        ),
    }
    if not args.no_store:
        output = args.output if args.output.is_absolute() else REPO / args.output
        payload["artifact"] = str(output.relative_to(REPO)).replace("\\", "/")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"LEAN R-058 PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
