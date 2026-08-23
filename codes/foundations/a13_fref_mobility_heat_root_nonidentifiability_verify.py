"""Integrated verifier for the finite Gibbs mobility counterpair."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a13-fref-mobility-heat-root-nonidentifiability-manifest.json"
PRIMARY = ROOT / "codes/foundations/a13_fref_mobility_heat_root_nonidentifiability.py"
INDEPENDENT = ROOT / "codes/foundations/a13_fref_mobility_heat_root_nonidentifiability_independent.py"
DEFAULT_OUTPUT = ROOT / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-integrated-fref-mobility-heat-root-nonidentifiability/result.json"


def sha(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = []

    def check(name: str, ok: bool, actual, expected) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": str(actual), "expected": str(expected)})
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-FREF-MOBILITY-HEAT-ROOT-NONIDENTIFIABILITY", manifest["audit_id"], "A13-FREF-MOBILITY-HEAT-ROOT-NONIDENTIFIABILITY")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negative", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    for label, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        check(f"source {label}", path.is_file() and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    for label, item in manifest["files"].items():
        path = ROOT / item["path"]
        check(f"file {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    cert = (ROOT / manifest["files"]["certificate"]["path"]).read_text(encoding="utf-8")
    check("certificate scope", all(token in cert for token in ("same stationary density", "different heat rates", "R-192", "A13/T-050", "No PDF")), True, True)
    check("hostile mutations", len(manifest["hostile_mutations"]) == 8, len(manifest["hostile_mutations"]), 8)
    for path in (PRIMARY, INDEPENDENT):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append((node.module or "__future__").split(".")[0])
        check(f"stdlib imports {path.name}", all(name in sys.stdlib_module_names for name in imports), imports, "stdlib only")
        check(f"no lane imports {path.name}", not any(name.startswith("a13_fref_mobility_heat_root_nonidentifiability") for name in imports), imports, "no lane imports")
    with tempfile.TemporaryDirectory(prefix="a13-mobility-") as temp:
        p_out = Path(temp) / "primary.json"
        i_out = Path(temp) / "independent.json"
        common = [sys.executable, "-B"]
        p_run = subprocess.run(common + [str(PRIMARY), "--output", str(p_out)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False)
        i_run = subprocess.run(common + [str(INDEPENDENT), "--output", str(i_out)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False)
        check("primary exit", p_run.returncode == 0, p_run.returncode, 0)
        check("independent exit", i_run.returncode == 0, i_run.returncode, 0)
        p_payload = json.loads(p_out.read_text(encoding="utf-8"))
        i_payload = json.loads(i_out.read_text(encoding="utf-8"))
        check("derived agreement", p_payload.get("derived") == i_payload.get("derived"), p_payload.get("derived"), i_payload.get("derived"))
        check("child PASS", p_payload.get("verdict") == "PASS" and i_payload.get("verdict") == "PASS", [p_payload.get("verdict"), i_payload.get("verdict")], ["PASS", "PASS"])
        derived = p_payload["derived"]
    check("same stationary density", derived["same_stationary_density"] is True, derived["same_stationary_density"], True)
    check("different heat rates", derived["different_heat_rates"] is True, derived["different_heat_rates"], True)
    check("rate vector A", derived["mobility_a_rates"] == ["1", "1"], derived["mobility_a_rates"], ["1", "1"])
    check("rate vector B", derived["mobility_b_rates"] == ["2", "3"], derived["mobility_b_rates"], ["2", "3"])
    check("boundary", all(token in manifest["boundary"] for token in ("heat-root", "raw-current", "A13/T-050", "Sector-A", "Pre-A")), manifest["boundary"], "finite non-identifiability boundary")
    payload = {"schema": "tect/a13-fref-mobility-heat-root-nonidentifiability-integrated/1.0", "run_kind": "integrated", "audit_id": manifest["audit_id"], "exploration_id": manifest["exploration_id"], "claim_id": manifest["claim_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": derived, "primary_stdout": p_run.stdout[-500:], "independent_stdout": i_run.stdout[-500:], "boundary": manifest["boundary"]}
    if not args.no_store:
        target = args.output if args.output.is_absolute() else ROOT / args.output
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"A13 FREF MOBILITY HEAT ROOT NONIDENTIFIABILITY INTEGRATED PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
