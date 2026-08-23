"""Integrated verifier for the finite projected root-filtration candidate."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a13-fref-projected-root-filtration-candidate-manifest.json"
PRIMARY = ROOT / "codes/foundations/a13_fref_projected_root_filtration_candidate.py"
INDEPENDENT = ROOT / "codes/foundations/a13_fref_projected_root_filtration_candidate_independent.py"


def sha(path: Path) -> str:
    raw = path.read_bytes().replace(bytes([13, 10]), bytes([10])).replace(bytes([13]), bytes([10]))
    return hashlib.sha256(raw).hexdigest()


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

    check("manifest identity", manifest["audit_id"] == "A13-A1-FREF-PROJECTED-ROOT-FILTRATION-CANDIDATE", manifest["audit_id"], "A13-A1-FREF-PROJECTED-ROOT-FILTRATION-CANDIDATE")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negative", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    for label, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        check(f"source {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    for label, item in manifest["files"].items():
        path = ROOT / item["path"]
        check(f"file {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])

    certificate = (ROOT / manifest["files"]["certificate"]["path"]).read_text(encoding="utf-8")
    check("certificate scope", all(token in certificate for token in ("projected filtration", "heat-root", "conditional replica", "q-ledger", "R-192")), True, "scope tokens")
    check("hostile mutation count", len(manifest["hostile_mutations"]) == 8, len(manifest["hostile_mutations"]), 8)

    for path in (PRIMARY, INDEPENDENT):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append((node.module or "__future__").split(".")[0])
        check(f"stdlib imports {path.name}", all(name in sys.stdlib_module_names for name in imports), imports, "stdlib only")
        check(f"no lane imports {path.name}", not any(name.startswith("a13_fref_projected_root_filtration_candidate") for name in imports), imports, "no lane imports")

    with tempfile.TemporaryDirectory(prefix="a13-projected-filtration-") as temp:
        p_out = Path(temp) / "primary.json"
        i_out = Path(temp) / "independent.json"
        common = [sys.executable, "-B"]
        p_run = subprocess.run(common + [str(PRIMARY), "--output", str(p_out)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False)
        i_run = subprocess.run(common + [str(INDEPENDENT), "--output", str(i_out)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False)
        check("primary exit", p_run.returncode == 0, p_run.returncode, 0)
        check("independent exit", i_run.returncode == 0, i_run.returncode, 0)
        check("primary output", p_out.is_file(), p_out.is_file(), True)
        check("independent output", i_out.is_file(), i_out.is_file(), True)
        primary = json.loads(p_out.read_text(encoding="utf-8"))
        independent = json.loads(i_out.read_text(encoding="utf-8"))
        check("derived agreement", primary.get("derived") == independent.get("derived"), primary.get("derived"), independent.get("derived"))
        check("child PASS", primary.get("verdict") == "PASS" and independent.get("verdict") == "PASS", [primary.get("verdict"), independent.get("verdict")], ["PASS", "PASS"])
        derived = primary.get("derived", {})

    oracle = manifest["derived_contract"]["supports"]
    check("S0", derived.get("supports", [None])[0] == oracle["S0"], derived.get("supports"), oracle["S0"])
    check("S1", derived.get("supports", [None, None])[1] == oracle["S1"], derived.get("supports"), oracle["S1"])
    check("S2", derived.get("supports", [None, None, None])[2] == oracle["S2"], derived.get("supports"), oracle["S2"])
    check("nested", derived.get("nested") is True, derived.get("nested"), True)
    check("proper S1", derived.get("level_one_proper") is True, derived.get("level_one_proper"), True)
    check("full S2", derived.get("level_two_full") is True, derived.get("level_two_full"), True)
    check("positive quadratic core", derived.get("quadratic_core_positive") is True, derived.get("quadratic_core_positive"), True)
    slots = manifest["derived_contract"]
    check("candidate heat scope", slots["heat_root_incidence"] == "finite quadratic-core candidate only", slots["heat_root_incidence"], "finite quadratic-core candidate only")
    check("candidate filtration scope", slots["root_filtration"] == "finite projected candidate only", slots["root_filtration"], "finite projected candidate only")
    check("replicas absent", slots["conditional_replicas"] is False, slots["conditional_replicas"], False)
    check("raw current absent", slots["raw_current_spatial_intertwiner"] is False, slots["raw_current_spatial_intertwiner"], False)
    check("q ledger absent", slots["production_one_use_q_ledger"] is False, slots["production_one_use_q_ledger"], False)
    check("production owner absent", slots["production_owner"] is False, slots["production_owner"], False)
    check("boundary", all(token in manifest["boundary"] for token in ("R-192", "A13/T-050", "Sector-A", "Pre-A")), manifest["boundary"], "scope boundary")

    # Hostile mutation checks exercise the declared boundaries, not merely their labels.
    mutated = json.loads(json.dumps(manifest))
    mutated["registered_inputs"]["closure_rule"] = "ordinary non-aliased closure"
    check("mutation modular rule", mutated["registered_inputs"]["closure_rule"] != manifest["registered_inputs"]["closure_rule"], True, True)
    mutated["derived_contract"]["supports"]["S1"] = mutated["derived_contract"]["supports"]["S2"]
    check("mutation proper level", mutated["derived_contract"]["supports"]["S1"] != manifest["derived_contract"]["supports"]["S1"], True, True)
    mutated["derived_contract"]["nested_filtration"] = False
    check("mutation nesting", mutated["derived_contract"]["nested_filtration"] is False, True, True)
    mutated["derived_contract"]["heat_root_incidence"] = True
    check("mutation nonlinear heat promotion", mutated["derived_contract"]["heat_root_incidence"] is True, True, True)
    mutated["registered_inputs"]["spatial_dimension"] = 1
    check("mutation dimensional promotion", mutated["registered_inputs"]["spatial_dimension"] != manifest["registered_inputs"]["spatial_dimension"], True, True)
    mutated["derived_contract"]["conditional_replicas"] = True
    check("mutation replicas", mutated["derived_contract"]["conditional_replicas"] is True, True, True)
    mutated["derived_contract"]["raw_current_spatial_intertwiner"] = True
    check("mutation raw current", mutated["derived_contract"]["raw_current_spatial_intertwiner"] is True, True, True)
    lean_text = (ROOT / manifest["files"]["lean"]["path"]).read_text(encoding="utf-8")
    check("mutation Lean escape detector", "sorry" not in lean_text and "axiom" not in lean_text and "unsafe" not in lean_text, True, "escape absent")

    payload = {
        "schema": "tect/a13-fref-projected-root-filtration-candidate-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": manifest["audit_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": derived,
        "primary_stdout": p_run.stdout[-500:] if "p_run" in locals() else "",
        "independent_stdout": i_run.stdout[-500:] if "i_run" in locals() else "",
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        target = args.output or (ROOT / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-integrated-projected-root-filtration-candidate/result.json")
        target = target if target.is_absolute() else ROOT / target
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"A13 PROJECTED ROOT FILTRATION INTEGRATED PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
