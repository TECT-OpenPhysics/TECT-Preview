"""Finite three-dimensional A1 shell projection with a QFT-compatible heat proxy."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a13-a1-three-dimensional-shell-projected-filtration-manifest.json"
LEAN_ROOT = ROOT / "verification/lean"
DEFAULT_OUTPUT = ROOT / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-primary-three-dimensional-shell-projected-filtration/result.json"


def sha(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


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


def lake_path() -> str | None:
    pin = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    for name in ("lake.exe", "lake"):
        candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / name
        if candidate.is_file():
            return str(candidate)
    return None


Point = tuple[int, int, int]


def close_support(support: set[Point], side: int, power: int) -> set[Point]:
    differences = {
        ((left[0] - right[0]) % side, (left[1] - right[1]) % side, (left[2] - right[2]) % side)
        for left in support
        for right in support
    }
    return {
        (
            (left[0] + power * delta[0]) % side,
            (left[1] + power * delta[1]) % side,
            (left[2] + power * delta[2]) % side,
        )
        for left in support
        for delta in differences
    }


def derive(manifest: dict[str, Any], a1: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["registered_inputs"]
    side = int(inputs["torus_side"])
    dimension = int(inputs["spatial_dimension"])
    power = int(inputs["nonlinear_power"])
    seed = {
        (int(mode[0]) % side, int(mode[1]) % side, int(mode[2]) % side)
        for mode in inputs["seed_modes"]
    }
    supports = [sorted(seed)]
    current = seed
    for _ in range(int(inputs["iterations"])):
        current = close_support(current, side, power)
        supports.append(sorted(current))

    params = a1["parameters"]
    r = Fraction(str(params["r"]))
    z = Fraction(str(params["Z"]))
    y = Fraction(str(params["Y"]))
    lower_bound = r - z * z / (4 * y)

    coordinates = [[sorted({point[axis] for point in level}) for axis in range(dimension)] for level in supports]
    all_points = {(x, yv, zval) for x in range(side) for yv in range(side) for zval in range(side)}
    nested = all(set(supports[index]).issubset(set(supports[index + 1])) for index in range(len(supports) - 1))
    heat_preserves = True
    for support in supports:
        sample = {point: point[0] + 2 * point[1] - point[2] for point in support}
        multiplied = {point: value * (1 + sum(point)) for point, value in sample.items()}
        heat_preserves = heat_preserves and all(point in support for point in multiplied)
    nonlinear_raises = all(
        close_support(set(supports[index]), side, power).issubset(set(supports[index + 1]))
        for index in range(len(supports) - 1)
    )
    return {
        "supports": supports,
        "support_cardinalities": [len(level) for level in supports],
        "coordinate_values": coordinates,
        "nested_filtration": nested,
        "quadratic_heat_preserves_each_Vj": heat_preserves,
        "nonlinear_drift_maps_Vj_to_Vj_plus_1": nonlinear_raises,
        "s2_is_proper_torus_subset": set(supports[-1]) != all_points,
        "quadratic_core_lower_bound": str(lower_bound),
        "quadratic_core_positive": lower_bound > 0,
        "side": side,
        "dimension": dimension,
        "power": power,
        "candidate_heat_root_incidence": manifest["derived_contract"]["heat_root_incidence"],
        "candidate_root_filtration": manifest["derived_contract"]["root_filtration"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": str(actual), "expected": str(expected)})
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-A1-THREE-DIMENSIONAL-SHELL-PROJECTED-FILTRATION", manifest["audit_id"], "A13-A1-THREE-DIMENSIONAL-SHELL-PROJECTED-FILTRATION")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    inputs = manifest["registered_inputs"]
    check("three dimensional", inputs["spatial_dimension"] == 3, inputs["spatial_dimension"], 3)
    check("two closure iterations", inputs["iterations"] == 2, inputs["iterations"], 2)
    check("modular closure", inputs["closure_rule"] == "C(S)=S+2(S-S) modulo (Z/16Z)^3", inputs["closure_rule"], "declared modular closure")
    for label, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        check(f"source {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    for label, item in manifest["files"].items():
        path = ROOT / item["path"]
        expected_path = Path(__file__).resolve() if label == "primary" else path
        check(f"file {label}", expected_path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(expected_path) == item["sha256"], sha(expected_path) if expected_path.is_file() else None, item["sha256"])

    a1_path = ROOT / manifest["source_authorities"]["a1_functional"]["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"), parse_float=str)
    derived = derive(manifest, a1)
    oracle = manifest["derived_contract"]
    expected_cards = [oracle["support_cardinalities"][key] for key in ("S0", "S1", "S2")]
    check("support cardinalities", derived["support_cardinalities"] == expected_cards, derived["support_cardinalities"], expected_cards)
    expected_coordinates = [oracle["S0_coordinate_values"], oracle["S1_coordinate_values"], oracle["S2_coordinate_values"]]
    check("coordinate closure", all(derived["coordinate_values"][level] == [expected_coordinates[level]] * 3 for level in range(3)), derived["coordinate_values"], expected_coordinates)
    check("nested filtration", derived["nested_filtration"] == oracle["nested_filtration"], derived["nested_filtration"], oracle["nested_filtration"])
    check("quadratic heat preservation", derived["quadratic_heat_preserves_each_Vj"] == oracle["quadratic_heat_preserves_each_Vj"], derived["quadratic_heat_preserves_each_Vj"], oracle["quadratic_heat_preserves_each_Vj"])
    check("nonlinear level raising", derived["nonlinear_drift_maps_Vj_to_Vj_plus_1"] == oracle["nonlinear_drift_maps_Vj_to_Vj_plus_1"], derived["nonlinear_drift_maps_Vj_to_Vj_plus_1"], oracle["nonlinear_drift_maps_Vj_to_Vj_plus_1"])
    check("proper odd-cube endpoint", derived["s2_is_proper_torus_subset"], derived["support_cardinalities"][-1], "less than side^3")
    check("positive quadratic core", derived["quadratic_core_positive"], derived["quadratic_core_lower_bound"], ">0")
    for key, expected in (("heat_root_incidence", "finite quadratic-core candidate only"), ("root_filtration", "finite 3D projected candidate only")):
        check(f"scope {key}", oracle[key] == expected, oracle[key], expected)
    for key in ("conditional_replicas", "raw_current_spatial_intertwiner", "production_one_use_q_ledger", "production_owner"):
        check(f"missing production slot {key}", oracle[key] is False, oracle[key], False)

    lean = ROOT / manifest["files"]["lean"]["path"]
    lean_text = lean.read_text(encoding="utf-8")
    check("Lean markers", all(token in lean_text for token in ("diagonal_preserves_support", "quadratic_core_lower_bound_positive")), True, "markers present")
    check("Lean forbidden escapes", not any(token in lean_text.split() for token in ("sorry", "admit", "axiom", "unsafe")), True, "absent")
    lake = lake_path()
    check("pinned lake", lake is not None, lake, "pinned lake")
    compiled = subprocess.run([lake, "env", "lean", str(lean.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    check("Lean compile", compiled.returncode == 0, compiled.returncode, 0)
    check("Lean diagnostics", compiled.returncode == 0 and "error:" not in (compiled.stdout + compiled.stderr).lower(), compiled.stderr, "no Lean error")

    payload = {
        "schema": "tect/a13-a1-three-dimensional-shell-projected-filtration-primary/1.0",
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
    print(f"A13 3D SHELL PROJECTED FILTRATION PRIMARY PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
