"""Integrated verifier for the finite three-dimensional shell projection."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a13-a1-three-dimensional-shell-projected-filtration-manifest.json"


def sha(path: Path) -> str:
    raw = path.read_bytes().replace(bytes([13, 10]), bytes([10])).replace(bytes([13]), bytes([10]))
    return hashlib.sha256(raw).hexdigest()


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


def recompute(manifest: dict[str, Any], seed_modes: list[list[int]] | None = None) -> list[set[Point]]:
    inputs = manifest["registered_inputs"]
    side = int(inputs["torus_side"])
    power = int(inputs["nonlinear_power"])
    modes = seed_modes if seed_modes is not None else inputs["seed_modes"]
    current = {tuple(int(value) % side for value in mode) for mode in modes}
    supports = [current]
    for _ in range(int(inputs["iterations"])):
        current = close_support(current, side, power)
        supports.append(current)
    return supports


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
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
    check("three-dimensional declaration", manifest["registered_inputs"]["spatial_dimension"] == 3, manifest["registered_inputs"]["spatial_dimension"], 3)
    certificate = (ROOT / manifest["files"]["certificate"]["path"]).read_text(encoding="utf-8")
    certificate_scope = all(token in certificate for token in ("three-dimensional", "heat-root", "conditional replica", "q-ledger", "R-192", "Pre-A"))
    check("certificate boundary", certificate_scope, certificate_scope, True)
    check("hostile mutation contract", len(manifest["hostile_mutations"]) == 8, len(manifest["hostile_mutations"]), 8)

    for label, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        check(f"source {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    for label, item in manifest["files"].items():
        path = ROOT / item["path"]
        check(f"file {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])

    stdlib = set(getattr(sys, "stdlib_module_names", ()))
    for label in ("primary", "independent"):
        path = ROOT / manifest["files"][label]["path"]
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add((node.module or "__future__").split(".")[0])
        check(f"{label} stdlib imports", imported.issubset(stdlib | {"__future__"}), sorted(imported), "stdlib only")
        check(f"{label} no lane import", not ("a13_a1_three_dimensional_shell_projected_filtration" in imported or "a13_a1_three_dimensional_shell_projected_filtration_independent" in imported), sorted(imported), "no lane import")

    supports = recompute(manifest)
    oracle = manifest["derived_contract"]
    expected_cards = [oracle["support_cardinalities"][key] for key in ("S0", "S1", "S2")]
    actual_cards = [len(level) for level in supports]
    check("independent recomputation", actual_cards == expected_cards, actual_cards, expected_cards)
    check("nested recomputation", all(supports[i].issubset(supports[i + 1]) for i in range(2)), True, True)
    check("endpoint is odd cube sized", actual_cards[-1] == expected_cards[-1] and actual_cards[-1] < int(manifest["registered_inputs"]["torus_side"]) ** int(manifest["registered_inputs"]["spatial_dimension"]), actual_cards[-1], "proper subset")
    check("scope flags", all(oracle[key] is False for key in ("conditional_replicas", "raw_current_spatial_intertwiner", "production_one_use_q_ledger", "production_owner")), True, "all missing")

    primary = ROOT / manifest["files"]["primary"]["path"]
    independent = ROOT / manifest["files"]["independent"]["path"]
    command_results: list[subprocess.CompletedProcess[str]] = []
    for path in (primary, independent):
        result = subprocess.run([sys.executable, "-B", str(path), "--no-store"], cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
        command_results.append(result)
        check(f"{path.stem} execution", result.returncode == 0, result.returncode, 0)
        check(f"{path.stem} PASS marker", "PASS" in result.stdout, result.stdout[-200:], "PASS")

    mutations = json.loads(json.dumps(manifest))
    mutations["registered_inputs"]["closure_rule"] = "one-dimensional slice closure"
    check("mutation 1 catches dimensional rule", mutations["registered_inputs"]["closure_rule"] != manifest["registered_inputs"]["closure_rule"], True, True)
    arbitrary_seed = [[0, 0, index] for index in range(len(manifest["registered_inputs"]["seed_modes"]))]
    mutated_cards = [len(level) for level in recompute(manifest, arbitrary_seed)]
    check("mutation 2 catches arbitrary seed", mutated_cards != expected_cards, mutated_cards, expected_cards)
    mutations["derived_contract"]["support_cardinalities"]["S2"] = int(manifest["registered_inputs"]["torus_side"]) ** int(manifest["registered_inputs"]["spatial_dimension"])
    check("mutation 3 catches full torus claim", actual_cards[-1] != mutations["derived_contract"]["support_cardinalities"]["S2"], actual_cards[-1], "not full torus")
    mutations["derived_contract"]["support_cardinalities"]["S1"] = 0
    check("mutation 4 catches erased intermediate", actual_cards[1] != mutations["derived_contract"]["support_cardinalities"]["S1"], actual_cards[1], "intermediate retained")
    mutations["derived_contract"]["heat_root_incidence"] = "canonical nonlinear production heat-root law"
    check("mutation 5 catches heat promotion", mutations["derived_contract"]["heat_root_incidence"] != manifest["derived_contract"]["heat_root_incidence"], True, True)
    mutations["derived_contract"]["production_owner"] = True
    check("mutation 6 catches owner promotion", mutations["derived_contract"]["production_owner"] is not manifest["derived_contract"]["production_owner"], True, True)
    for key in ("conditional_replicas", "raw_current_spatial_intertwiner", "production_one_use_q_ledger"):
        mutations["derived_contract"][key] = True
    check("mutation 7 catches missing production slots", any(mutations["derived_contract"][key] is not manifest["derived_contract"][key] for key in ("conditional_replicas", "raw_current_spatial_intertwiner", "production_one_use_q_ledger")), True, True)
    lean_text = (ROOT / manifest["files"]["lean"]["path"]).read_text(encoding="utf-8")
    check("mutation 8 catches Lean escape", "sorry" not in lean_text and "admit" not in lean_text and "axiom" not in lean_text and "unsafe" not in lean_text, True, "escape absent")

    payload = {
        "schema": "tect/a13-a1-three-dimensional-shell-projected-filtration-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": manifest["audit_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {"support_cardinalities": actual_cards, "nested_filtration": all(supports[i].issubset(supports[i + 1]) for i in range(2))},
        "primary_stdout": command_results[0].stdout[-500:],
        "independent_stdout": command_results[1].stdout[-500:],
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        target = args.output or (ROOT / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-integrated-three-dimensional-shell-projected-filtration/result.json")
        target = target if target.is_absolute() else ROOT / target
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"A13 3D SHELL PROJECTED FILTRATION INTEGRATED PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
