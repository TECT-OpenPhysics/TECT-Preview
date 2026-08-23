"""Non-importing exact reconstruction of the finite projected filtration."""

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
MANIFEST_PATH = ROOT / "strategy/pre-a13-fref-projected-root-filtration-candidate-manifest.json"
LEAN_ROOT = ROOT / "verification/lean"
DEFAULT_OUTPUT = ROOT / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-independent-projected-root-filtration-candidate/result.json"


def sha(path: Path) -> str:
    raw = path.read_bytes().replace(bytes([13, 10]), bytes([10])).replace(bytes([13]), bytes([10]))
    return hashlib.sha256(raw).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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


def close(support: set[int], side: int, power: int) -> set[int]:
    diff = {(left - right) % side for left in support for right in support}
    return {(left + power * delta) % side for left in support for delta in diff}


def reconstruct(manifest: dict[str, Any], a1: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["registered_inputs"]
    side = int(inputs["torus_side"])
    power = int(inputs["nonlinear_power"])
    current = {int(value) % side for value in inputs["root_modes"]}
    supports = [sorted(current)]
    for _ in range(2):
        current = close(current, side, power)
        supports.append(sorted(current))
    p = a1["parameters"]
    r = Fraction(str(p["r"]))
    z = Fraction(str(p["Z"]))
    y = Fraction(str(p["Y"]))
    lower = r - z * z / (4 * y)
    residues = list(range(side))
    return {
        "supports": supports,
        "nested": set(supports[0]).issubset(set(supports[1])) and set(supports[1]).issubset(set(supports[2])),
        "level_one_proper": set(supports[1]) != set(residues),
        "level_two_full": set(supports[2]) == set(residues),
        "quadratic_core_lower_bound": str(lower),
        "quadratic_core_positive": lower > 0,
        "side": side,
        "power": power,
        "spatial_dimension": int(inputs["spatial_dimension"]),
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

    test("audit id", manifest["audit_id"] == "A13-A1-FREF-PROJECTED-ROOT-FILTRATION-CANDIDATE", manifest["audit_id"], "A13-A1-FREF-PROJECTED-ROOT-FILTRATION-CANDIDATE")
    test("nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    test("new negatives empty", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for label, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        test(f"source {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    for label, item in manifest["files"].items():
        path = ROOT / item["path"]
        test(f"file {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])

    a1 = json.loads((ROOT / manifest["source_authorities"]["a1_functional"]["path"]).read_text(encoding="utf-8"), parse_float=str)
    derived = reconstruct(manifest, a1)
    oracle = manifest["derived_contract"]["supports"]
    test("S0 exact", derived["supports"][0] == oracle["S0"], derived["supports"][0], oracle["S0"])
    test("S1 exact", derived["supports"][1] == oracle["S1"], derived["supports"][1], oracle["S1"])
    test("S2 exact", derived["supports"][2] == oracle["S2"], derived["supports"][2], oracle["S2"])
    test("nested", derived["nested"], derived["supports"], True)
    test("proper S1", derived["level_one_proper"], derived["supports"][1], "proper subset")
    test("full S2", derived["level_two_full"], derived["supports"][2], list(range(derived["side"])))
    test("positive core", derived["quadratic_core_positive"], derived["quadratic_core_lower_bound"], ">0")
    slots = manifest["derived_contract"]
    test("heat candidate wording", slots["heat_root_incidence"] == "finite quadratic-core candidate only", slots["heat_root_incidence"], "finite quadratic-core candidate only")
    test("root candidate wording", slots["root_filtration"] == "finite projected candidate only", slots["root_filtration"], "finite projected candidate only")
    test("replica absent", slots["conditional_replicas"] is False, slots["conditional_replicas"], False)
    test("raw current absent", slots["raw_current_spatial_intertwiner"] is False, slots["raw_current_spatial_intertwiner"], False)
    test("q ledger absent", slots["production_one_use_q_ledger"] is False, slots["production_one_use_q_ledger"], False)
    test("production owner absent", slots["production_owner"] is False, slots["production_owner"], False)

    lean = ROOT / manifest["files"]["lean"]["path"]
    lean_text = lean.read_text(encoding="utf-8")
    test("Lean markers", all(token in lean_text for token in ("diagonal_preserves_support", "quadratic_core_lower_bound_positive")), True, "markers present")
    test("Lean forbidden", not any(token in lean_text.split() for token in ("sorry", "admit", "axiom", "unsafe")), True, "absent")
    lake = lake_path()
    test("pinned lake", lake is not None, lake, "pinned lake")
    compiled = subprocess.run([lake, "env", "lean", str(lean.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    test("Lean compile", compiled.returncode == 0, compiled.returncode, 0)
    test("Lean diagnostics", compiled.returncode == 0 and "error:" not in (compiled.stdout + compiled.stderr).lower(), compiled.stderr, "no error")

    payload = {
        "schema": "tect/a13-fref-projected-root-filtration-candidate-independent/1.0",
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
    print(f"A13 PROJECTED ROOT FILTRATION INDEPENDENT PASS {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
