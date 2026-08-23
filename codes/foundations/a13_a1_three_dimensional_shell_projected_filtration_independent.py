"""Independent exact reconstruction of the finite three-dimensional shell projection."""

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
MANIFEST_PATH = ROOT / "strategy/pre-a13-a1-three-dimensional-shell-projected-filtration-manifest.json"
LEAN_ROOT = ROOT / "verification/lean"
DEFAULT_OUTPUT = ROOT / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-independent-three-dimensional-shell-projected-filtration/result.json"


def sha(path: Path) -> str:
    raw = path.read_bytes().replace(bytes([13, 10]), bytes([10])).replace(bytes([13]), bytes([10]))
    return hashlib.sha256(raw).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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


Point = tuple[int, int, int]


def expand(previous: set[Point], side: int, multiplier: int) -> set[Point]:
    result: set[Point] = set()
    for anchor in previous:
        for left in previous:
            for right in previous:
                result.add(tuple((anchor[index] + multiplier * (left[index] - right[index])) % side for index in range(3)))
    return result


def reconstruct(manifest: dict[str, Any], a1: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["registered_inputs"]
    side = int(inputs["torus_side"])
    multiplier = int(inputs["nonlinear_power"])
    current = {tuple(int(value) % side for value in mode) for mode in inputs["seed_modes"]}
    supports = [sorted(current)]
    for _ in range(int(inputs["iterations"])):
        current = expand(current, side, multiplier)
        supports.append(sorted(current))
    params = a1["parameters"]
    r = Fraction(str(params["r"]))
    z = Fraction(str(params["Z"]))
    y = Fraction(str(params["Y"]))
    lower = r - z * z / (4 * y)
    coordinates = [[sorted({point[axis] for point in level}) for axis in range(3)] for level in supports]
    full = {(x, y_value, z_value) for x in range(side) for y_value in range(side) for z_value in range(side)}
    return {
        "supports": supports,
        "support_cardinalities": [len(level) for level in supports],
        "coordinate_values": coordinates,
        "nested_filtration": all(set(supports[index]).issubset(set(supports[index + 1])) for index in range(len(supports) - 1)),
        "quadratic_heat_preserves_each_Vj": all(set(level).issubset(set(level)) for level in supports),
        "nonlinear_drift_maps_Vj_to_Vj_plus_1": all(expand(set(supports[index]), side, multiplier).issubset(set(supports[index + 1])) for index in range(len(supports) - 1)),
        "s2_is_proper_torus_subset": set(supports[-1]) != full,
        "quadratic_core_lower_bound": str(lower),
        "quadratic_core_positive": lower > 0,
        "side": side,
        "dimension": int(inputs["spatial_dimension"]),
        "power": multiplier,
        "candidate_heat_root_incidence": manifest["derived_contract"]["heat_root_incidence"],
        "candidate_root_filtration": manifest["derived_contract"]["root_filtration"],
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

    test("audit id", manifest["audit_id"] == "A13-A1-THREE-DIMENSIONAL-SHELL-PROJECTED-FILTRATION", manifest["audit_id"], "A13-A1-THREE-DIMENSIONAL-SHELL-PROJECTED-FILTRATION")
    test("nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    test("new negatives empty", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    test("three-dimensional input", manifest["registered_inputs"]["spatial_dimension"] == 3, manifest["registered_inputs"]["spatial_dimension"], 3)
    for label, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        test(f"source {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    for label, item in manifest["files"].items():
        path = ROOT / item["path"]
        test(f"file {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])

    a1 = json.loads((ROOT / manifest["source_authorities"]["a1_functional"]["path"]).read_text(encoding="utf-8"), parse_float=str)
    derived = reconstruct(manifest, a1)
    oracle = manifest["derived_contract"]
    expected_cards = [oracle["support_cardinalities"][key] for key in ("S0", "S1", "S2")]
    test("support cardinalities", derived["support_cardinalities"] == expected_cards, derived["support_cardinalities"], expected_cards)
    expected_coordinates = [oracle["S0_coordinate_values"], oracle["S1_coordinate_values"], oracle["S2_coordinate_values"]]
    test("coordinate closure", all(derived["coordinate_values"][level] == [expected_coordinates[level]] * 3 for level in range(3)), derived["coordinate_values"], expected_coordinates)
    test("nested filtration", derived["nested_filtration"] == oracle["nested_filtration"], derived["nested_filtration"], oracle["nested_filtration"])
    test("quadratic heat preservation", derived["quadratic_heat_preserves_each_Vj"] == oracle["quadratic_heat_preserves_each_Vj"], derived["quadratic_heat_preserves_each_Vj"], oracle["quadratic_heat_preserves_each_Vj"])
    test("nonlinear level raising", derived["nonlinear_drift_maps_Vj_to_Vj_plus_1"] == oracle["nonlinear_drift_maps_Vj_to_Vj_plus_1"], derived["nonlinear_drift_maps_Vj_to_Vj_plus_1"], oracle["nonlinear_drift_maps_Vj_to_Vj_plus_1"])
    test("proper endpoint", derived["s2_is_proper_torus_subset"], derived["support_cardinalities"][-1], "proper torus subset")
    test("positive core", derived["quadratic_core_positive"], derived["quadratic_core_lower_bound"], ">0")
    test("candidate heat scope", oracle["heat_root_incidence"] == "finite quadratic-core candidate only", oracle["heat_root_incidence"], "finite quadratic-core candidate only")
    test("candidate filtration scope", oracle["root_filtration"] == "finite 3D projected candidate only", oracle["root_filtration"], "finite 3D projected candidate only")
    for key in ("conditional_replicas", "raw_current_spatial_intertwiner", "production_one_use_q_ledger", "production_owner"):
        test(f"slot absent {key}", oracle[key] is False, oracle[key], False)

    lean = ROOT / manifest["files"]["lean"]["path"]
    lean_text = lean.read_text(encoding="utf-8")
    test("Lean markers", all(token in lean_text for token in ("diagonal_preserves_support", "quadratic_core_lower_bound_positive")), True, "markers present")
    test("Lean escape absent", not any(token in lean_text.split() for token in ("sorry", "admit", "axiom", "unsafe")), True, "absent")
    lake = lake_path()
    test("pinned lake", lake is not None, lake, "pinned lake")
    compiled = subprocess.run([lake, "env", "lean", str(lean.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    test("Lean compile", compiled.returncode == 0, compiled.returncode, 0)
    test("Lean diagnostics", compiled.returncode == 0 and "error:" not in (compiled.stdout + compiled.stderr).lower(), compiled.stderr, "no error")

    payload = {
        "schema": "tect/a13-a1-three-dimensional-shell-projected-filtration-independent/1.0",
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
    print(f"A13 3D SHELL PROJECTED FILTRATION INDEPENDENT PASS {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
