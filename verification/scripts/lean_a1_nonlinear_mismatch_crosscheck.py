"""Primary Lean bridge for the A1 nonlinear-owner mismatch cross-check."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
LEAN_DIR = REPO / "verification" / "lean"
ENTRYPOINT = LEAN_DIR / "Tect" / "A1NonlinearMismatch.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
LAKEFILE = LEAN_DIR / "lakefile.toml"
LOCKFILE = LEAN_DIR / "lake-manifest.json"
MANIFEST = REPO / "strategy" / "pre-a-a1-nonlinear-gradient-mismatch-lean-crosscheck-manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "runs" / "2026-08-21-lean-a1-nonlinear-mismatch-crosscheck" / "primary.json"
MARKERS = ("declared_is_twice_residual", "manifest_fixture", "equality_zeroes")
FORBIDDEN = ("sorry", "admit", "axiom", "unsafe")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def find_lake() -> str | None:
    pin = TOOLCHAIN.read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / ("lake.exe" if os.name == "nt" else "lake")
    if candidate.is_file():
        return str(candidate)
    return shutil.which("lake")


def check(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    def clean(value: Any) -> Any:
        if isinstance(value, Fraction):
            return f"{value.numerator}/{value.denominator}"
        if isinstance(value, dict):
            return {str(key): clean(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [clean(item) for item in value]
        return value
    rows.append({"name": name, "pass": bool(condition), "actual": clean(actual), "expected": clean(expected)})
    if not condition:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")


def fraction(value: Any) -> Fraction:
    return Fraction(str(value))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1_path = REPO / manifest["inputs"]["a1_manifest"]["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    params = a1["parameters"]
    rows: list[dict[str, Any]] = []
    check(rows, "A1 manifest hash", sha256(a1_path) == manifest["inputs"]["a1_manifest"]["sha256"], sha256(a1_path), manifest["inputs"]["a1_manifest"]["sha256"])
    lam = fraction(params[manifest["lean_inputs"]["lambda_key"]])
    gamma = fraction(params[manifest["lean_inputs"]["gamma_key"]])
    expected_lam = fraction(manifest["lean_inputs"]["lambda"])
    expected_gamma = fraction(manifest["lean_inputs"]["gamma"])
    rho = fraction(manifest["lean_inputs"]["fixture_rho"])
    check(rows, "lambda crosswalk", lam == expected_lam, lam, expected_lam)
    check(rows, "gamma crosswalk", gamma == expected_gamma, gamma, expected_gamma)
    residual = lam * rho + gamma * rho * rho
    declared = 2 * lam * rho + 2 * gamma * rho * rho
    check(rows, "declared coefficient is twice residual", declared == 2 * residual, declared, 2 * residual)
    check(rows, "fixture mismatch is nonzero", declared != residual, declared - residual, "nonzero")
    check(rows, "fixture rho positive", rho > 0, rho, ">0")
    check(rows, "Lean source markers", all(marker in ENTRYPOINT.read_text(encoding="ascii") for marker in MARKERS), MARKERS, MARKERS)
    forbidden = [token for token in FORBIDDEN if re.search(rf"\b{token}\b", ENTRYPOINT.read_text(encoding="ascii"))]
    check(rows, "Lean escape tokens absent", forbidden == [], forbidden, [])
    lake = find_lake()
    check(rows, "lake executable available", lake is not None, lake, "pinned toolchain or PATH")
    lock = json.loads(LOCKFILE.read_text(encoding="utf-8"))
    mathlib = [row for row in lock.get("packages", []) if row.get("name") == "mathlib"]
    check(rows, "Mathlib pin", len(mathlib) == 1 and mathlib[0].get("inputRev") == "v4.32.1", mathlib[0].get("inputRev") if mathlib else None, "v4.32.1")
    command = [lake, "env", "lean", str(ENTRYPOINT.relative_to(LEAN_DIR))]
    completed = subprocess.run(command, cwd=LEAN_DIR, text=True, encoding="utf-8", capture_output=True, check=False)
    check(rows, "Lean compile", completed.returncode == 0, completed.returncode, 0)
    check(rows, "Lean stdout clean", completed.stdout.strip() == "", completed.stdout, "")
    check(rows, "Lean stderr clean", completed.stderr.strip() == "", completed.stderr, "")
    payload: dict[str, Any] = {
        "schema": "tect/a1-nonlinear-gradient-mismatch-lean-crosscheck/1.0",
        "run_kind": "primary",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "lambda": f"{lam.numerator}/{lam.denominator}",
            "gamma": f"{gamma.numerator}/{gamma.denominator}",
            "rho": f"{rho.numerator}/{rho.denominator}",
            "residual_coefficient": f"{residual.numerator}/{residual.denominator}",
            "declared_gradient_coefficient": f"{declared.numerator}/{declared.denominator}",
            "difference": f"{(declared - residual).numerator}/{(declared - residual).denominator}",
            "declared_equals_twice_residual": declared == 2 * residual,
        },
        "command": command,
        "toolchain": TOOLCHAIN.read_text(encoding="utf-8").strip(),
        "source_hashes": {"entrypoint": sha256(ENTRYPOINT), "toolchain": sha256(TOOLCHAIN), "lakefile": sha256(LAKEFILE), "lake_manifest": sha256(LOCKFILE)},
        "lean_stdout": completed.stdout,
        "lean_stderr": completed.stderr,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["no_overclaim"],
    }
    if not args.no_store:
        atomic_json(args.output, payload)
    print(f"PRIMARY A1 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
