"""Exact two-step support saturation for the nonlinear A1 F_ref term."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy" / "pre-a13-nonlinear-root-filtration-saturation-manifest.json"
LEAN_ROOT = ROOT / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_ROOT / "Tect" / "R199.lean"
DEFAULT_OUTPUT = ROOT / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-primary-nonlinear-root-filtration-saturation" / "result.json"


def sha(path: Path) -> str:
    raw = path.read_bytes().replace(bytes([13, 10]), bytes([10])).replace(bytes([13]), bytes([10]))
    return hashlib.sha256(raw).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def find_lake() -> str | None:
    pin = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    for name in ("lake.exe", "lake"):
        candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / name
        if candidate.is_file():
            return str(candidate)
    return None


def convolve(left: dict[int, F], right: dict[int, F]) -> dict[int, F]:
    out: dict[int, F] = {}
    for left_mode, left_value in left.items():
        for right_mode, right_value in right.items():
            mode = left_mode + right_mode
            out[mode] = out.get(mode, F(0)) + left_value * right_value
    return {mode: value for mode, value in out.items() if value != 0}


def nonlinear_closure(phi: dict[int, F], power: int) -> dict[int, F]:
    conjugate = {-mode: value for mode, value in phi.items()}
    rho = convolve(conjugate, phi)
    out = phi
    for _ in range(power):
        out = convolve(rho, out)
    return out


def derive(manifest: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["registered_inputs"]
    roots = [int(value) for value in inputs["root_modes"]]
    coefficients = [F(str(value)) for value in inputs["root_coefficients"]]
    power = int(inputs["nonlinear_power"])
    iterations = int(inputs["closure_iterations"])
    side = int(inputs["torus_side"])
    phi = {mode: value for mode, value in zip(roots, coefficients)}
    supports: list[list[int]] = [sorted(phi)]
    values: list[dict[str, str]] = [{str(mode): str(value) for mode, value in sorted(phi.items())}]
    for _ in range(iterations):
        phi = nonlinear_closure(phi, power)
        supports.append(sorted(phi))
        values.append({str(mode): str(value) for mode, value in sorted(phi.items())})
    second = supports[-1]
    residues = sorted({mode % side for mode in second})
    all_residues = list(range(side))
    degree_first = 2 * power + 1
    degree_second = degree_first * (2 * power + 1)
    expected_first = {index - 1: F(math.comb(degree_first, index)) for index in range(degree_first + 1)}
    second_start = second[0]
    expected_second = {second_start + index: F(math.comb(degree_second, index)) for index in range(degree_second + 1)}
    return {
        "supports": supports,
        "coefficients": values,
        "first_expected": {str(mode): str(value) for mode, value in sorted(expected_first.items())},
        "second_expected": {str(mode): str(value) for mode, value in sorted(expected_second.items())},
        "first_interval": [supports[1][0], supports[1][-1]],
        "second_interval": [second[0], second[-1]],
        "second_residues": residues,
        "all_side_residues": residues == all_residues,
        "side": side,
        "power": power,
        "iterations": iterations,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-NONLINEAR-ROOT-FILTRATION-SATURATION", manifest["audit_id"], "A13-NONLINEAR-ROOT-FILTRATION-SATURATION")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negative", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for label, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        check(f"source {label}", path.is_file() and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    for label, item in manifest["files"].items():
        path = ROOT / item["path"]
        check(f"file {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])

    certificate = (ROOT / manifest["files"]["certificate"]["path"]).read_text(encoding="utf-8")
    certificate_tokens_ok = all(token in certificate for token in ("z^{-11}(1+z)^{25}", "side-16", "heat-root", "q_k", "A13/T-050"))
    check("certificate scope", certificate_tokens_ok, certificate_tokens_ok, True)
    check("hostile mutation count", len(manifest["hostile_mutations"]) == 8, len(manifest["hostile_mutations"]), 8)

    derived = derive(manifest)
    check("first support interval", derived["first_interval"] == [-1, 4], derived["first_interval"], [-1, 4])
    check("second support interval", derived["second_interval"] == [-11, 14], derived["second_interval"], [-11, 14])
    check("first binomial identity", derived["coefficients"][1] == derived["first_expected"], derived["coefficients"][1], derived["first_expected"])
    check("second binomial identity", derived["coefficients"][2] == derived["second_expected"], derived["coefficients"][2], derived["second_expected"])
    check("all side residues", derived["all_side_residues"], derived["second_residues"], list(range(derived["side"])))
    check("owner slots remain missing", all(value is False for value in manifest["derived_contract"]["owner_slots"].values()), manifest["derived_contract"]["owner_slots"], "all false")

    lake = find_lake()
    check("pinned lake", lake is not None, lake, "pinned lake")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean", completed.returncode == 0 and "error:" not in (completed.stdout + completed.stderr).lower(), completed.stderr, "no Lean error")

    payload = {
        "schema": "tect/a13-nonlinear-root-filtration-saturation-primary/1.0",
        "run_kind": "primary",
        "audit_id": manifest["audit_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": derived,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"A13 NONLINEAR ROOT FILTRATION SATURATION PRIMARY PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
