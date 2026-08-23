"""Non-importing exact reconstruction of two-step nonlinear support saturation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "strategy/pre-a13-nonlinear-root-filtration-saturation-manifest.json"
LEAN_ROOT = ROOT / "verification/lean"
LEAN_PATH = LEAN_ROOT / "Tect/R199.lean"
DEFAULT_OUTPUT = ROOT / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-independent-nonlinear-root-filtration-saturation/result.json"


def sha(path: Path) -> str:
    raw = path.read_bytes().replace(bytes([13, 10]), bytes([10])).replace(bytes([13]), bytes([10]))
    return hashlib.sha256(raw).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def lake_path() -> str | None:
    pin = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    for name in ("lake.exe", "lake"):
        candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / name
        if candidate.is_file():
            return str(candidate)
    return shutil.which("lake")


def conv(left: dict[int, Fraction], right: dict[int, Fraction]) -> dict[int, Fraction]:
    result: dict[int, Fraction] = {}
    for x, a in left.items():
        for y, b in right.items():
            result[x + y] = result.get(x + y, Fraction(0)) + a * b
    return {mode: value for mode, value in result.items() if value != 0}


def closure(phi: dict[int, Fraction], power: int) -> dict[int, Fraction]:
    rho = conv({-mode: value for mode, value in phi.items()}, phi)
    result = phi
    for _ in range(power):
        result = conv(rho, result)
    return result


def reconstruct(manifest: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["registered_inputs"]
    roots = [int(x) for x in inputs["root_modes"]]
    coeffs = [Fraction(str(x)) for x in inputs["root_coefficients"]]
    power = int(inputs["nonlinear_power"])
    iterations = int(inputs["closure_iterations"])
    side = int(inputs["torus_side"])
    current = {mode: coefficient for mode, coefficient in zip(roots, coeffs)}
    supports = [sorted(current)]
    coefficients = [{str(mode): str(value) for mode, value in sorted(current.items())}]
    for _ in range(iterations):
        current = closure(current, power)
        supports.append(sorted(current))
        coefficients.append({str(mode): str(value) for mode, value in sorted(current.items())})
    first_degree = 2 * power + 1
    second_degree = first_degree * (2 * power + 1)
    first_expected = {mode: Fraction(math.comb(first_degree, mode - supports[1][0])) for mode in supports[1]}
    second_expected = {mode: Fraction(math.comb(second_degree, mode - supports[2][0])) for mode in supports[2]}
    residues = sorted({mode % side for mode in supports[2]})
    return {
        "supports": supports,
        "coefficients": coefficients,
        "first_expected": {str(mode): str(value) for mode, value in sorted(first_expected.items())},
        "second_expected": {str(mode): str(value) for mode, value in sorted(second_expected.items())},
        "first_interval": [supports[1][0], supports[1][-1]],
        "second_interval": [supports[2][0], supports[2][-1]],
        "second_residues": residues,
        "all_side_residues": residues == list(range(side)),
        "side": side,
        "power": power,
        "iterations": iterations,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def test(name: str, ok: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(ok), "actual": str(actual), "expected": str(expected)})
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")

    test("audit id", manifest["audit_id"] == "A13-NONLINEAR-ROOT-FILTRATION-SATURATION", manifest["audit_id"], "A13-NONLINEAR-ROOT-FILTRATION-SATURATION")
    test("nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    test("new negatives empty", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for label, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        test(f"source {label}", path.is_file() and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    for label, item in manifest["files"].items():
        path = ROOT / item["path"]
        test(f"file {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])

    derived = reconstruct(manifest)
    test("first interval", derived["first_interval"] == [-1, 4], derived["first_interval"], [-1, 4])
    test("second interval", derived["second_interval"] == [-11, 14], derived["second_interval"], [-11, 14])
    test("first coefficients", derived["coefficients"][1] == derived["first_expected"], derived["coefficients"][1], derived["first_expected"])
    test("second coefficients", derived["coefficients"][2] == derived["second_expected"], derived["coefficients"][2], derived["second_expected"])
    test("residue saturation", derived["all_side_residues"], derived["second_residues"], list(range(derived["side"])))
    test("owner slots missing", all(value is False for value in manifest["derived_contract"]["owner_slots"].values()), manifest["derived_contract"]["owner_slots"], "all false")

    lean_text = LEAN_PATH.read_text(encoding="utf-8")
    markers = ["second_nonlinear_support_identity", "all_side16_residues"]
    test("Lean markers", all(marker in lean_text for marker in markers), markers, "present")
    test("Lean forbidden tokens", not any(token in lean_text.split() for token in ("sorry", "admit", "axiom", "unsafe")), True, "absent")
    lake = lake_path()
    test("pinned lake", lake is not None, lake, "pinned lake")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_PATH.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, capture_output=True, text=True, encoding="utf-8", check=False)
    test("Lean compile", completed.returncode == 0, completed.returncode, 0)
    test("Lean diagnostics", completed.returncode == 0 and "error:" not in (completed.stdout + completed.stderr).lower(), completed.stderr, "no error")

    payload = {
        "schema": "tect/a13-nonlinear-root-filtration-saturation-independent/1.0",
        "run_kind": "independent",
        "audit_id": manifest["audit_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_id"],
        "verdict": "PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": derived,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        write_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"A13 NONLINEAR ROOT FILTRATION SATURATION INDEPENDENT PASS {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
