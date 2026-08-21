"""Primary Lean bridge for the A1 Class-II owner mismatch."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
LEAN_DIR = REPO / "verification" / "lean"
ENTRYPOINT = LEAN_DIR / "Tect" / "A1ClassIIOwnerMismatch.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
LAKEFILE = LEAN_DIR / "lakefile.toml"
LOCKFILE = LEAN_DIR / "lake-manifest.json"
MANIFEST = REPO / "strategy" / "pre-a-a1-classii-owner-mismatch-lean-crosscheck-manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "runs" / "2026-08-21-a1-classii-owner-mismatch-lean-crosscheck" / "primary.json"
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
    return str(candidate) if candidate.is_file() else shutil.which("lake")


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


def frac(value: Any) -> Fraction:
    return Fraction(str(value))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1_path = REPO / manifest["inputs"]["a1_manifest"]["path"]
    lean_source = ENTRYPOINT.read_text(encoding="ascii")
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    params = a1["parameters"]
    inputs = manifest["lean_inputs"]
    rows: list[dict[str, Any]] = []
    check(rows, "A1 manifest hash", sha256(a1_path) == manifest["inputs"]["a1_manifest"]["sha256"], sha256(a1_path), manifest["inputs"]["a1_manifest"]["sha256"])
    check(rows, "Lean source hash", sha256(ENTRYPOINT) == manifest["inputs"]["lean_entrypoint"]["sha256"], sha256(ENTRYPOINT), manifest["inputs"]["lean_entrypoint"]["sha256"])
    values = {key: frac(params[inputs[key]]) for key in ("alpha_key", "beta_key", "mass_key", "mass_regularizer_key", "cjk_key", "ckk_key")}
    for name, key in (("alpha", "alpha_key"), ("beta", "beta_key"), ("mass", "mass_key"), ("mass_regularizer", "mass_regularizer_key"), ("cjk", "cjk_key"), ("ckk", "ckk_key")):
        check(rows, f"{name} crosswalk", values[key] == frac(inputs[name]), values[key], frac(inputs[name]))
    declared_num = values["ckk_key"] * values["beta_key"] ** 2
    residual_num = values["cjk_key"] * values["alpha_key"] * values["beta_key"]
    denominator = values["mass_key"] ** 2 + values["mass_regularizer_key"]
    declared = declared_num / denominator
    residual = residual_num / denominator
    difference = declared - residual
    check(rows, "declared numerator", declared_num == frac(inputs["expected_declared_numerator"]), declared_num, frac(inputs["expected_declared_numerator"]))
    check(rows, "residual numerator", residual_num == frac(inputs["expected_residual_numerator"]), residual_num, frac(inputs["expected_residual_numerator"]))
    check(rows, "numerator difference", declared_num - residual_num == frac(inputs["expected_numerator_difference"]), declared_num - residual_num, frac(inputs["expected_numerator_difference"]))
    check(rows, "mass denominator positive", denominator > 0, denominator, ">0")
    check(rows, "coefficient mismatch nonzero", declared != residual, difference, "nonzero")
    check(rows, "Lean theorem markers", all(marker in lean_source for marker in manifest["theorem_markers"]), manifest["theorem_markers"], manifest["theorem_markers"])
    forbidden = [token for token in FORBIDDEN if re.search(rf"\b{token}\b", lean_source)]
    check(rows, "Lean escape tokens absent", forbidden == [], forbidden, [])
    lake = find_lake()
    check(rows, "lake executable available", lake is not None, lake, "pinned toolchain or PATH")
    lock = json.loads(LOCKFILE.read_text(encoding="utf-8"))
    mathlib = [row for row in lock.get("packages", []) if row.get("name") == "mathlib"]
    check(rows, "Mathlib pin", len(mathlib) == 1 and mathlib[0].get("inputRev") == "v4.32.1", mathlib[0].get("inputRev") if mathlib else None, "v4.32.1")
    completed = subprocess.run([lake, "env", "lean", str(ENTRYPOINT.relative_to(LEAN_DIR))], cwd=LEAN_DIR, text=True, encoding="utf-8", capture_output=True, check=False)
    check(rows, "Lean compile", completed.returncode == 0, completed.returncode, 0)
    check(rows, "Lean stdout clean", completed.stdout.strip() == "", completed.stdout, "")
    check(rows, "Lean stderr clean", completed.stderr.strip() == "", completed.stderr, "")
    payload: dict[str, Any] = {
        "schema": "tect/a1-classii-owner-mismatch-lean-crosscheck/1.0",
        "run_kind": "primary",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "alpha": f"{values['alpha_key'].numerator}/{values['alpha_key'].denominator}",
            "beta": f"{values['beta_key'].numerator}/{values['beta_key'].denominator}",
            "mass": f"{values['mass_key'].numerator}/{values['mass_key'].denominator}",
            "mass_regularizer": f"{values['mass_regularizer_key'].numerator}/{values['mass_regularizer_key'].denominator}",
            "cjk": f"{values['cjk_key'].numerator}/{values['cjk_key'].denominator}",
            "ckk": f"{values['ckk_key'].numerator}/{values['ckk_key'].denominator}",
            "declared_numerator": f"{declared_num.numerator}/{declared_num.denominator}",
            "residual_numerator": f"{residual_num.numerator}/{residual_num.denominator}",
            "numerator_difference": f"{(declared_num - residual_num).numerator}/{(declared_num - residual_num).denominator}",
            "mass_denominator": f"{denominator.numerator}/{denominator.denominator}",
            "declared_coefficient": f"{declared.numerator}/{declared.denominator}",
            "residual_coefficient": f"{residual.numerator}/{residual.denominator}",
            "coefficient_difference": f"{difference.numerator}/{difference.denominator}",
            "mass_denominator_positive": denominator > 0,
            "coefficients_are_not_equal": declared != residual,
        },
        "command": [lake, "env", "lean", str(ENTRYPOINT.relative_to(LEAN_DIR))],
        "toolchain": TOOLCHAIN.read_text(encoding="utf-8").strip(),
        "source_hashes": {"entrypoint": sha256(ENTRYPOINT), "toolchain": sha256(TOOLCHAIN), "lakefile": sha256(LAKEFILE), "lake_manifest": sha256(LOCKFILE)},
        "lean_stdout": completed.stdout,
        "lean_stderr": completed.stderr,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["no_overclaim"],
    }
    if not args.no_store:
        atomic_json(args.output, payload)
    print(f"PRIMARY A1 CLASS-II LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
