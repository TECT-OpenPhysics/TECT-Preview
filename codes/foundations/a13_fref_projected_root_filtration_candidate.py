"""Finite projected root-filtration candidate for the A1 F_ref heat proxy."""

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
MANIFEST = ROOT / "strategy/pre-a13-fref-projected-root-filtration-candidate-manifest.json"
LEAN_ROOT = ROOT / "verification/lean"
DEFAULT_OUTPUT = ROOT / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-primary-projected-root-filtration-candidate/result.json"


def sha(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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


def lake_path() -> str | None:
    pin = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    for name in ("lake.exe", "lake"):
        candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / name
        if candidate.is_file():
            return str(candidate)
    return None


def closure(support: set[int], side: int, power: int) -> set[int]:
    differences = {(x - y) % side for x in support for y in support}
    scaled = {(power * value) % side for value in differences}
    return {(x + value) % side for x in support for value in scaled}


def derive(manifest: dict[str, Any], a1: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["registered_inputs"]
    side = int(inputs["torus_side"])
    roots = {int(value) % side for value in inputs["root_modes"]}
    power = int(inputs["nonlinear_power"])
    supports = [sorted(roots)]
    current = roots
    for _ in range(2):
        current = closure(current, side, power)
        supports.append(sorted(current))
    params = a1["parameters"]
    r = F(str(params["r"]))
    z = F(str(params["Z"]))
    y = F(str(params["Y"]))
    lower_bound = r - z * z / (4 * y)
    all_residues = list(range(side))
    return {
        "supports": supports,
        "nested": set(supports[0]).issubset(set(supports[1])) and set(supports[1]).issubset(set(supports[2])),
        "level_one_proper": set(supports[1]) != set(all_residues),
        "level_two_full": set(supports[2]) == set(all_residues),
        "quadratic_core_lower_bound": str(lower_bound),
        "quadratic_core_positive": lower_bound > 0,
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
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": str(actual), "expected": str(expected)})
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-A1-FREF-PROJECTED-ROOT-FILTRATION-CANDIDATE", manifest["audit_id"], "A13-A1-FREF-PROJECTED-ROOT-FILTRATION-CANDIDATE")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for label, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        check(f"source {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    for label, item in manifest["files"].items():
        path = ROOT / item["path"]
        if label == "primary":
            expected_path = Path(__file__).resolve()
        else:
            expected_path = path
        check(f"file {label}", expected_path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(expected_path) == item["sha256"], sha(expected_path) if expected_path.is_file() else None, item["sha256"])

    a1_path = ROOT / manifest["source_authorities"]["a1_functional"]["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"), parse_float=str)
    derived = derive(manifest, a1)
    oracle = manifest["derived_contract"]["supports"]
    check("S0", derived["supports"][0] == oracle["S0"], derived["supports"][0], oracle["S0"])
    check("S1", derived["supports"][1] == oracle["S1"], derived["supports"][1], oracle["S1"])
    check("S2", derived["supports"][2] == oracle["S2"], derived["supports"][2], oracle["S2"])
    check("nested filtration", derived["nested"], derived["supports"], True)
    check("proper intermediate level", derived["level_one_proper"], derived["supports"][1], "proper subset of S2")
    check("full second level", derived["level_two_full"], derived["supports"][2], list(range(derived["side"])))
    check("positive quadratic core", derived["quadratic_core_positive"], derived["quadratic_core_lower_bound"], ">0")
    slots = manifest["derived_contract"]
    check("heat candidate is scoped", slots["heat_root_incidence"] == "finite quadratic-core candidate only", slots["heat_root_incidence"], "finite quadratic-core candidate only")
    check("root candidate is scoped", slots["root_filtration"] == "finite projected candidate only", slots["root_filtration"], "finite projected candidate only")
    check("replicas missing", slots["conditional_replicas"] is False, slots["conditional_replicas"], False)
    check("raw current missing", slots["raw_current_spatial_intertwiner"] is False, slots["raw_current_spatial_intertwiner"], False)
    check("q ledger missing", slots["production_one_use_q_ledger"] is False, slots["production_one_use_q_ledger"], False)
    check("production owner false", slots["production_owner"] is False, slots["production_owner"], False)

    lean = ROOT / manifest["files"]["lean"]["path"]
    lean_text = lean.read_text(encoding="utf-8")
    check("Lean markers", all(token in lean_text for token in ("diagonal_preserves_support", "quadratic_core_lower_bound_positive")), True, "markers present")
    check("Lean forbidden tokens", not any(token in lean_text.split() for token in ("sorry", "admit", "axiom", "unsafe")), True, "absent")
    lake = lake_path()
    check("pinned lake", lake is not None, lake, "pinned lake")
    completed = subprocess.run([lake, "env", "lean", str(lean.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean", completed.returncode == 0 and "error:" not in (completed.stdout + completed.stderr).lower(), completed.stderr, "no Lean error")
    payload = {
        "schema": "tect/a13-fref-projected-root-filtration-candidate-primary/1.0",
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
    print(f"A13 PROJECTED ROOT FILTRATION PRIMARY PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
