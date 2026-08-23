"""Exact finite nonlinear Fourier mode-mixing witness for the A1 F_ref term."""

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
MANIFEST = ROOT / "strategy" / "pre-a13-nonlinear-root-filtration-mixing-manifest.json"
LEAN_ROOT = ROOT / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_ROOT / "Tect" / "R198.lean"
DEFAULT_OUTPUT = ROOT / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-primary-nonlinear-root-filtration-mixing" / "result.json"


def sha(path: Path) -> str:
    data = path.read_bytes().replace(bytes([13, 10]), bytes([10])).replace(bytes([13]), bytes([10]))
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
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


def add_poly(left: dict[int, F], right: dict[int, F]) -> dict[int, F]:
    out = dict(left)
    for exponent, coefficient in right.items():
        out[exponent] = out.get(exponent, F(0)) + coefficient
    return {key: value for key, value in out.items() if value != 0}


def convolve(left: dict[int, F], right: dict[int, F]) -> dict[int, F]:
    out: dict[int, F] = {}
    for exponent_left, coefficient_left in left.items():
        for exponent_right, coefficient_right in right.items():
            exponent = exponent_left + exponent_right
            out[exponent] = out.get(exponent, F(0)) + coefficient_left * coefficient_right
    return {key: value for key, value in out.items() if value != 0}


def derive(manifest: dict[str, Any]) -> dict[str, Any]:
    roots = manifest["registered_inputs"]["root_modes"]
    coefficients = [F(str(value)) for value in manifest["registered_inputs"]["root_coefficients"]]
    power = int(manifest["registered_inputs"]["nonlinear_power"])
    phi = {int(mode): coefficient for mode, coefficient in zip(roots, coefficients)}
    conjugate = {-mode: coefficient for mode, coefficient in phi.items()}
    rho = convolve(conjugate, phi)
    drift = phi
    for _ in range(power):
        drift = convolve(rho, drift)
    degree = 2 * power + 1
    expected = {index - 1: F(math.comb(degree, index)) for index in range(degree + 1)}
    input_modes = sorted(phi)
    output_modes = sorted(drift)
    leakage_modes = sorted(set(output_modes) - set(input_modes))
    lower_leakage = min(output_modes) < min(input_modes)
    upper_leakage = max(output_modes) > max(input_modes)
    return {
        "phi": {str(key): str(value) for key, value in sorted(phi.items())},
        "rho": {str(key): str(value) for key, value in sorted(rho.items())},
        "drift": {str(key): str(value) for key, value in sorted(drift.items())},
        "expected_binomial_drift": {str(key): str(value) for key, value in sorted(expected.items())},
        "input_modes": input_modes,
        "output_modes": output_modes,
        "leakage_modes": leakage_modes,
        "lower_leakage": lower_leakage,
        "upper_leakage": upper_leakage,
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
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-NONLINEAR-ROOT-FILTRATION-MIXING", manifest["audit_id"], "A13-NONLINEAR-ROOT-FILTRATION-MIXING")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    for label, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        check(f"source {label}", path.is_file() and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    for label, item in manifest["files"].items():
        path = ROOT / item["path"]
        check(f"file {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])

    certificate = (ROOT / manifest["files"]["certificate"]["path"]).read_text(encoding="utf-8")
    check("certificate exact identity", "rho^2\\phi=z^{-1}(1+z)^5" in certificate, True, True)
    owner_tokens_ok = all(token in certificate for token in ("heat-root incidence", "raw-current", "q-ledger", "A13/T-050"))
    check("certificate owner boundary", owner_tokens_ok, owner_tokens_ok, True)
    check("hostile mutations", len(manifest["hostile_mutations"]) == 8, len(manifest["hostile_mutations"]), 8)

    derived = derive(manifest)
    check("rho convolution", derived["rho"] == {"-1": "1", "0": "2", "1": "1"}, derived["rho"], "exact conjugate convolution")
    check("binomial drift identity", derived["drift"] == derived["expected_binomial_drift"], derived["drift"], derived["expected_binomial_drift"])
    check("lower frequency leakage", derived["lower_leakage"], derived["output_modes"], "output below input roots")
    check("upper frequency leakage", derived["upper_leakage"], derived["output_modes"], "output above input roots")
    check("zero frequency leakage", derived["zero_mode_created"], derived["output_modes"], "zero mode present")
    check("naive root filtration fails", not derived["naive_root_subspace_invariant"], derived["output_modes"], "not contained in input roots")
    check("leakage nonempty", bool(derived["leakage_modes"]), derived["leakage_modes"], "nonempty")

    lake = find_lake()
    check("pinned lake", lake is not None, lake, "pinned lake")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean", completed.returncode == 0 and "error:" not in (completed.stdout + completed.stderr).lower(), completed.stderr, "no Lean error")

    payload = {
        "schema": "tect/a13-nonlinear-root-filtration-mixing-primary/1.0",
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
    print(f"A13 NONLINEAR ROOT FILTRATION MIXING PRIMARY PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
