"""Exact finite side-16 full-residue closure for the F_ref QFT candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a13-full-residue-fref-qft-closure-manifest.json"
LEAN_ROOT = ROOT / "verification/lean"
LEAN = LEAN_ROOT / "Tect/R202.lean"
DEFAULT_OUTPUT = ROOT / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-primary-full-residue-fref-qft-closure/result.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
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


def lake_path() -> str | None:
    pin = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    for name in ("lake.exe", "lake"):
        candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / name
        if candidate.is_file():
            return str(candidate)
    return None


def convolve(left: dict[int, F], right: dict[int, F], side: int | None) -> dict[int, F]:
    result: dict[int, F] = {}
    for x, a in left.items():
        for y, b in right.items():
            mode = x + y if side is None else (x + y) % side
            result[mode] = result.get(mode, F(0)) + a * b
    return {mode: value for mode, value in result.items() if value != 0}


def nonlinear_closure(phi: dict[int, F], power: int, side: int | None) -> dict[int, F]:
    conjugate = {((-mode) % side if side is not None else -mode): value for mode, value in phi.items()}
    rho = convolve(conjugate, phi, side)
    result = phi
    for _ in range(power):
        result = convolve(rho, result, side)
    return result


def derive(manifest: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["registered_inputs"]
    side = int(inputs["torus_side"])
    components = int(inputs["internal_components"])
    dimension = int(inputs["spatial_dimension"])
    roots = [int(value) for value in inputs["root_modes"]]
    coefficients = [F(str(value)) for value in inputs["root_coefficients"]]
    power = int(inputs["nonlinear_power"])
    iterations = int(inputs["closure_iterations"])
    nonaliased = {mode: coefficient for mode, coefficient in zip(roots, coefficients)}
    cyclic = {mode % side: coefficient for mode, coefficient in zip(roots, coefficients)}
    nonaliased_supports = [sorted(nonaliased)]
    cyclic_supports = [sorted(cyclic)]
    for _ in range(iterations):
        nonaliased = nonlinear_closure(nonaliased, power, None)
        cyclic = nonlinear_closure(cyclic, power, side)
        nonaliased_supports.append(sorted(nonaliased))
        cyclic_supports.append(sorted(cyclic))
    full_residues = list(range(side))
    r197 = json.loads((ROOT / manifest["source_authorities"]["r197_candidate"]["path"]).read_text(encoding="utf-8"))
    return {
        "nonaliased_supports": nonaliased_supports,
        "cyclic_supports": cyclic_supports,
        "nonaliased_first_interval": [nonaliased_supports[1][0], nonaliased_supports[1][-1]],
        "nonaliased_second_interval": [nonaliased_supports[-1][0], nonaliased_supports[-1][-1]],
        "cyclic_first_residues": cyclic_supports[1],
        "cyclic_second_residues": cyclic_supports[-1],
        "full_residue_projection_closed": set(cyclic_supports[-1]) == set(full_residues),
        "minimal_coordinate_support_for_witness": len(cyclic_supports[-1]),
        "proper_two_root_projection_invariant": set(cyclic_supports[-1]).issubset(set(roots)),
        "finite_generator_candidate": bool(r197["derived_contract"]["owner_slots"]["heat_generator"]),
        "finite_gibbs_candidate": bool(r197["derived_contract"]["owner_slots"]["heat_semigroup"]),
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
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-A1-FULL-RESIDUE-FREF-QFT-CLOSURE", manifest["audit_id"], "A13-A1-FULL-RESIDUE-FREF-QFT-CLOSURE")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for label, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        check(f"source {label}", path.is_file() and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    for label, item in manifest["files"].items():
        path = ROOT / item["path"]
        check(f"file {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    certificate = (ROOT / manifest["files"]["certificate"]["path"]).read_text(encoding="utf-8")
    check("certificate scope", all(token in certificate for token in ("cyclic convolution", "full-residue", "heat-root", "q_k", "OS/KMS")), True, True)
    check("hostile mutation count", len(manifest["hostile_mutations"]) == 8, len(manifest["hostile_mutations"]), 8)
    derived = derive(manifest)
    oracle = manifest["test_oracles"]
    for key in ("nonaliased_first_interval", "nonaliased_second_interval", "cyclic_first_residues", "cyclic_second_residues", "real_coordinate_count"):
        check(key, derived[key] == oracle[key], derived[key], oracle[key])
    check("full projection closed", derived["full_residue_projection_closed"], derived["full_residue_projection_closed"], True)
    check("two-root projection not invariant", not derived["proper_two_root_projection_invariant"], derived["proper_two_root_projection_invariant"], False)
    check("R-192 first slot", manifest["derived_contract"]["r192_first_missing_slot"] == "heat_root_incidence", manifest["derived_contract"]["r192_first_missing_slot"], "heat_root_incidence")
    check("production owner remains false", manifest["derived_contract"]["production_owner"] is False, manifest["derived_contract"]["production_owner"], False)
    lake = lake_path()
    check("pinned lake", lake is not None, lake, "pinned lake")
    completed = subprocess.run([lake, "env", "lean", str(LEAN.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean", completed.returncode == 0 and "error:" not in (completed.stdout + completed.stderr).lower(), completed.stderr, "no Lean error")
    payload = {
        "schema": "tect/a13-full-residue-fref-qft-closure-primary/1.0",
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
    print(f"A13 FULL RESIDUE F_REF QFT CLOSURE PRIMARY PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
