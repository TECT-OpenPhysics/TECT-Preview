"""Non-importing exact reconstruction of the nonlinear root leakage witness."""

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
MANIFEST_PATH = ROOT / "strategy" / "pre-a13-nonlinear-root-filtration-mixing-manifest.json"
LEAN_ROOT = ROOT / "verification" / "lean"
LEAN_PATH = LEAN_ROOT / "Tect" / "R198.lean"
DEFAULT_OUTPUT = ROOT / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-independent-nonlinear-root-filtration-mixing" / "result.json"


def sha(path: Path) -> str:
    raw = path.read_bytes()
    raw = raw.replace(bytes([13, 10]), bytes([10])).replace(bytes([13]), bytes([10]))
    return hashlib.sha256(raw).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
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


def convolution(left: dict[int, Fraction], right: dict[int, Fraction]) -> dict[int, Fraction]:
    result: dict[int, Fraction] = {}
    for left_mode, left_value in left.items():
        for right_mode, right_value in right.items():
            mode = left_mode + right_mode
            result[mode] = result.get(mode, Fraction(0)) + left_value * right_value
    return {mode: value for mode, value in result.items() if value != 0}


def reconstruct(manifest: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["registered_inputs"]
    roots = [int(value) for value in inputs["root_modes"]]
    values = [Fraction(str(value)) for value in inputs["root_coefficients"]]
    power = int(inputs["nonlinear_power"])
    phi = {mode: value for mode, value in zip(roots, values)}
    conjugate = {-mode: value for mode, value in phi.items()}
    rho = convolution(conjugate, phi)
    drift = phi
    for _ in range(power):
        drift = convolution(rho, drift)
    degree = 2 * power + 1
    expected = {index - 1: Fraction(math.comb(degree, index)) for index in range(degree + 1)}
    input_modes = sorted(phi)
    output_modes = sorted(drift)
    leakage = sorted(set(output_modes).difference(input_modes))
    return {
        "phi": {str(mode): str(value) for mode, value in sorted(phi.items())},
        "rho": {str(mode): str(value) for mode, value in sorted(rho.items())},
        "drift": {str(mode): str(value) for mode, value in sorted(drift.items())},
        "expected_binomial_drift": {str(mode): str(value) for mode, value in sorted(expected.items())},
        "input_modes": input_modes,
        "output_modes": output_modes,
        "leakage_modes": leakage,
        "lower_leakage": min(output_modes) < min(input_modes),
        "upper_leakage": max(output_modes) > max(input_modes),
        "zero_mode_created": 0 in output_modes,
        "naive_root_subspace_invariant": set(output_modes).issubset(set(input_modes)),
        "degree": degree,
        "nonlinear_power": power,
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

    test("audit id", manifest["audit_id"] == "A13-NONLINEAR-ROOT-FILTRATION-MIXING", manifest["audit_id"], "A13-NONLINEAR-ROOT-FILTRATION-MIXING")
    test("nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    test("empty negative route", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for label, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        test(f"source {label}", path.is_file() and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    for label, item in manifest["files"].items():
        path = ROOT / item["path"]
        test(f"file {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])

    derived = reconstruct(manifest)
    test("rho exact", derived["rho"] == {"-1": "1", "0": "2", "1": "1"}, derived["rho"], "conjugate convolution")
    test("binomial exact", derived["drift"] == derived["expected_binomial_drift"], derived["drift"], derived["expected_binomial_drift"])
    test("lower leak", derived["lower_leakage"], derived["output_modes"], "below input")
    test("upper leak", derived["upper_leakage"], derived["output_modes"], "above input")
    test("zero leak", derived["zero_mode_created"], derived["output_modes"], "zero present")
    test("naive filtration fails", not derived["naive_root_subspace_invariant"], derived["output_modes"], "not invariant")
    test("leakage exists", bool(derived["leakage_modes"]), derived["leakage_modes"], "nonempty")

    lean_text = LEAN_PATH.read_text(encoding="utf-8")
    markers = ["nonlinear_mode_mix_identity", "nonlinear_mode_mix_coefficients"]
    test("Lean markers", all(marker in lean_text for marker in markers), markers, "present")
    test("Lean forbidden tokens", not any(token in lean_text.split() for token in ("sorry", "admit", "axiom", "unsafe")), True, "absent")
    lake = lake_path()
    test("pinned lake", lake is not None, lake, "pinned lake")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_PATH.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, capture_output=True, text=True, encoding="utf-8", check=False)
    test("Lean compile", completed.returncode == 0, completed.returncode, 0)
    test("Lean diagnostics", completed.returncode == 0 and "error:" not in (completed.stdout + completed.stderr).lower(), completed.stderr, "no error")

    payload = {
        "schema": "tect/a13-nonlinear-root-filtration-mixing-independent/1.0",
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
    print(f"A13 NONLINEAR ROOT FILTRATION MIXING INDEPENDENT PASS {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
