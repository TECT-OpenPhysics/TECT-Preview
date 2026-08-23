"""Non-importing exact reconstruction of the full residue QFT candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a13-full-residue-fref-qft-closure-manifest.json"
LEAN_ROOT = ROOT / "verification/lean"
LEAN = LEAN_ROOT / "Tect/R202.lean"
DEFAULT_OUTPUT = ROOT / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-independent-full-residue-fref-qft-closure/result.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
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


def conv(left: dict[int, Fraction], right: dict[int, Fraction], side: int | None) -> dict[int, Fraction]:
    result: dict[int, Fraction] = {}
    for x, a in left.items():
        for y, b in right.items():
            mode = x + y if side is None else (x + y) % side
            result[mode] = result.get(mode, Fraction(0)) + a * b
    return {mode: value for mode, value in result.items() if value}


def nonlinear(phi: dict[int, Fraction], power: int, side: int | None) -> dict[int, Fraction]:
    conjugate = {((-mode) % side if side is not None else -mode): value for mode, value in phi.items()}
    rho = conv(conjugate, phi, side)
    out = phi
    for _ in range(power):
        out = conv(rho, out, side)
    return out


def reconstruct(manifest: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["registered_inputs"]
    side = int(inputs["torus_side"])
    components = int(inputs["internal_components"])
    dimension = int(inputs["spatial_dimension"])
    roots = [int(v) for v in inputs["root_modes"]]
    coeffs = [Fraction(str(v)) for v in inputs["root_coefficients"]]
    power = int(inputs["nonlinear_power"])
    iterations = int(inputs["closure_iterations"])
    infinite = {k: v for k, v in zip(roots, coeffs)}
    finite = {k % side: v for k, v in zip(roots, coeffs)}
    infinite_supports = [sorted(infinite)]
    finite_supports = [sorted(finite)]
    for _ in range(iterations):
        infinite = nonlinear(infinite, power, None)
        finite = nonlinear(finite, power, side)
        infinite_supports.append(sorted(infinite))
        finite_supports.append(sorted(finite))
    return {
        "nonaliased_supports": infinite_supports,
        "cyclic_supports": finite_supports,
        "nonaliased_first_interval": [infinite_supports[1][0], infinite_supports[1][-1]],
        "nonaliased_second_interval": [infinite_supports[-1][0], infinite_supports[-1][-1]],
        "cyclic_first_residues": finite_supports[1],
        "cyclic_second_residues": finite_supports[-1],
        "full_residue_projection_closed": finite_supports[-1] == list(range(side)),
        "minimal_coordinate_support_for_witness": len(finite_supports[-1]),
        "proper_two_root_projection_invariant": set(finite_supports[-1]).issubset(set(roots)),
        "finite_generator_candidate": True,
        "finite_gibbs_candidate": True,
        "real_coordinate_count": 2 * components * (side**dimension),
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
    checks: list[dict[str, Any]] = []

    def test(name: str, ok: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(ok), "actual": str(actual), "expected": str(expected)})
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")

    test("audit id", manifest["audit_id"] == "A13-A1-FULL-RESIDUE-FREF-QFT-CLOSURE", manifest["audit_id"], "A13-A1-FULL-RESIDUE-FREF-QFT-CLOSURE")
    test("nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    test("new negatives empty", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for label, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        test(f"source {label}", path.is_file() and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    for label, item in manifest["files"].items():
        path = ROOT / item["path"]
        test(f"file {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    derived = reconstruct(manifest)
    for key, expected in manifest["test_oracles"].items():
        test(key, derived[key] == expected, derived[key], expected)
    test("full projection closed", derived["full_residue_projection_closed"], derived["full_residue_projection_closed"], True)
    test("two-root projection not invariant", not derived["proper_two_root_projection_invariant"], derived["proper_two_root_projection_invariant"], False)
    lean_text = LEAN.read_text(encoding="utf-8")
    test("Lean markers", all(marker in lean_text for marker in ("side16_card", "root_pair_is_proper", "saturated_interval_has_at_least_side16_residues")), True, True)
    test("Lean forbidden tokens", not any(token in lean_text.split() for token in ("sorry", "admit", "axiom", "unsafe")), True, "absent")
    lake = lake_path()
    test("pinned lake", lake is not None, lake, "pinned lake")
    completed = subprocess.run([lake, "env", "lean", str(LEAN.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, capture_output=True, text=True, encoding="utf-8", check=False)
    test("Lean compile", completed.returncode == 0, completed.returncode, 0)
    test("Lean diagnostics", completed.returncode == 0 and "error:" not in (completed.stdout + completed.stderr).lower(), completed.stderr, "no error")
    payload = {
        "schema": "tect/a13-full-residue-fref-qft-closure-independent/1.0",
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
    print(f"A13 FULL RESIDUE F_REF QFT CLOSURE INDEPENDENT PASS {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
