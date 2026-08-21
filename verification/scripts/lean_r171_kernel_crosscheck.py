"""Run the repository-pinned Lean kernel cross-check for R-171.

The Lean theorem checks the exact bracket identity and positivity hypotheses
used by R-171.  This runner does not replace the R-171 primary or independent
Python lanes and it does not assert the full A1 action or any physical limit.
It records the toolchain, dependency lock, source hashes, command output and
the result JSON so a later integrated verifier can fail closed on drift.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
LEAN_DIR = REPO / "verification" / "lean"
ENTRYPOINT = LEAN_DIR / "Tect" / "R171.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
LAKEFILE = LEAN_DIR / "lakefile.toml"
LOCKFILE = LEAN_DIR / "lake-manifest.json"
MANIFEST = REPO / "strategy" / (
    "pre-a-a7-actual-plane-wave-endpoint-secant-sign-witness-manifest.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
    / "runs"
    / "2026-08-21-lean-r171-kernel-crosscheck"
    / "result.json"
)
THEOREM_MARKERS = (
    "bracket_numerator_identity",
    "bracket_positive",
    "bracket_numerator_coefficients_positive",
    "endpoint_secant_sign",
)
FORBIDDEN_SOURCE_TOKENS = ("sorry", "admit", "axiom", "unsafe")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_lake() -> str | None:
    found = shutil.which("lake")
    if found:
        return found
    candidates = []
    home = Path.home()
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    source_text = ENTRYPOINT.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    lake = find_lake()

    check(ENTRYPOINT.is_file(), "Lean entrypoint exists", str(ENTRYPOINT), True, rows)
    check(TOOLCHAIN.is_file(), "Lean toolchain pin exists", str(TOOLCHAIN), True, rows)
    check(LAKEFILE.is_file(), "Lakefile exists", str(LAKEFILE), True, rows)
    check(LOCKFILE.is_file(), "Lake dependency lock exists", str(LOCKFILE), True, rows)
    check(lake is not None, "lake executable is available", lake, "PATH or elan bin", rows)
    check(manifest.get("result_id") == "R-171", "R-171 manifest identity", manifest.get("result_id"), "R-171", rows)
    for key, reference in manifest.get("inputs", {}).items():
        input_path = REPO / reference["path"]
        check(
            input_path.is_file() and sha256(input_path) == reference["sha256"],
            f"manifest input hash {key}",
            sha256(input_path) if input_path.is_file() else None,
            reference["sha256"],
            rows,
        )
    lock = json.loads(LOCKFILE.read_text(encoding="utf-8"))
    mathlib_rows = [row for row in lock.get("packages", []) if row.get("name") == "mathlib"]
    check(len(mathlib_rows) == 1, "Mathlib lock entry unique", len(mathlib_rows), 1, rows)
    check(mathlib_rows[0].get("inputRev") == "v4.32.1", "Mathlib lock revision", mathlib_rows[0].get("inputRev"), "v4.32.1", rows)
    check(
        all(marker in source_text for marker in THEOREM_MARKERS),
        "Lean theorem markers present",
        [marker for marker in THEOREM_MARKERS if marker in source_text],
        list(THEOREM_MARKERS),
        rows,
    )
    forbidden_hits = [token for token in FORBIDDEN_SOURCE_TOKENS if re.search(rf"\b{token}\b", source_text)]
    check(forbidden_hits == [], "Lean escape tokens absent", forbidden_hits, [], rows)

    command = [lake, "env", "lean", str(ENTRYPOINT.relative_to(LEAN_DIR))]
    completed = subprocess.run(
        command,
        cwd=LEAN_DIR,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    check(completed.returncode == 0, "Lean kernel compile", completed.returncode, 0, rows)
    check(completed.stdout.strip() == "", "Lean stdout is clean", completed.stdout, "", rows)
    check(completed.stderr.strip() == "", "Lean stderr is clean", completed.stderr, "", rows)

    payload: dict[str, Any] = {
        "schema": "tect/lean-kernel-crosscheck/1.0",
        "run_kind": "lean-kernel-crosscheck",
        "result_id": "R-171",
        "claim_ids": manifest["claim_ids"],
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
        },
        "lean_stdout": completed.stdout,
        "lean_stderr": completed.stderr,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "python": sys.version,
        "boundary": (
            "Kernel-checks only the exact R-171 bracket identity and positivity "
            "route; no full A1 action, A13/T-050 closure, physical-empty sign, "
            "Gibbs/Nelson estimate, or continuum limit follows."
        ),
    }

    if not args.no_store:
        output = args.output if args.output.is_absolute() else REPO / args.output
        payload["artifact"] = str(output.relative_to(REPO)).replace("\\", "/")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    print(f"LEAN R-171 PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
