"""Integrated verifier for the finite F_ref nonlinear candidate screen."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy" / "pre-a13-fref-nonlinear-gibbs-candidate-manifest.json"
PRIMARY = ROOT / "codes" / "foundations" / "a13_fref_nonlinear_gibbs_candidate.py"
INDEPENDENT = ROOT / "codes" / "foundations" / "a13_fref_nonlinear_gibbs_candidate_independent.py"
DEFAULT_OUTPUT = ROOT / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-integrated-fref-nonlinear-gibbs-candidate" / "result.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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

    check("manifest identity", manifest["audit_id"] == "A13-A1-FREF-NONLINEAR-GIBBS-CANDIDATE", manifest["audit_id"], "A13-A1-FREF-NONLINEAR-GIBBS-CANDIDATE")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    for label, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        check(f"source {label}", path.is_file() and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    for label, item in manifest["files"].items():
        path = ROOT / item["path"]
        expected = item["sha256"]
        check(f"file {label}", path.is_file() and expected != "TO_BE_FILLED" and sha(path) == expected, sha(path) if path.is_file() else None, expected)

    check("hostile mutation contract", len(manifest["hostile_mutations"]) == 8, len(manifest["hostile_mutations"]), 8)
    required_scope = ["F_ref", "F_decl", "canonical", "filtration", "raw-current", "q-ledger", "continuum"]
    cert_text = (ROOT / manifest["files"]["certificate"]["path"]).read_text(encoding="utf-8")
    check("certificate scope tokens", all(token.lower() in cert_text.lower() for token in required_scope), required_scope, "all present")
    check("boundary tokens", all(token in manifest["boundary"] for token in ("T0", "claim-nonbearing", "R-192", "A13/T-050", "Sector-A", "Pre-A")), True, "all present")

    for path in (PRIMARY, INDEPENDENT):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        imported = []
        for node in imports:
            if isinstance(node, ast.Import):
                imported.extend(alias.name.split(".")[0] for alias in node.names)
            else:
                imported.append((node.module or "__future__").split(".")[0])
        check(f"stdlib-only imports {path.name}", all(name in sys.stdlib_module_names for name in imported), imported, "stdlib only")
        check(f"no cross-lane import {path.name}", not any(name in {"a13_fref_nonlinear_gibbs_candidate", "a13_fref_nonlinear_gibbs_candidate_independent", "a13_fref_nonlinear_gibbs_candidate_verify"} for name in imported), imported, "no lane imports")

    with tempfile.TemporaryDirectory(prefix="a13-fref-integrated-") as temp:
        p_out = Path(temp) / "primary.json"
        i_out = Path(temp) / "independent.json"
        common = [sys.executable, "-B"]
        p_run = subprocess.run(common + [str(PRIMARY), "--output", str(p_out)], cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
        i_run = subprocess.run(common + [str(INDEPENDENT), "--output", str(i_out)], cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
        check("primary exit", p_run.returncode == 0, p_run.returncode, 0)
        check("independent exit", i_run.returncode == 0, i_run.returncode, 0)
        check("primary output", p_out.is_file(), p_out.is_file(), True)
        check("independent output", i_out.is_file(), i_out.is_file(), True)
        p_payload = json.loads(p_out.read_text(encoding="utf-8"))
        i_payload = json.loads(i_out.read_text(encoding="utf-8"))
        check("derived cores agree", p_payload.get("derived") == i_payload.get("derived"), p_payload.get("derived"), i_payload.get("derived"))
        check("both PASS", p_payload.get("verdict") == "PASS" and i_payload.get("verdict") == "PASS", [p_payload.get("verdict"), i_payload.get("verdict")], ["PASS", "PASS"])
        core = p_payload.get("derived", {})

    check("coercivity diagnostic", core.get("finite_coercive_candidate") is True, core.get("finite_coercive_candidate"), True)
    check("generator/semigroup only", core.get("heat_generator_candidate") is True and core.get("heat_semigroup_candidate") is True, core, "both true")
    check("missing filtration", core.get("filtration_supplied") is False, core.get("filtration_supplied"), False)
    check("missing raw-current map", core.get("raw_current_intertwiner_supplied") is False, core.get("raw_current_intertwiner_supplied"), False)
    check("missing q ledger", core.get("production_q_ledger_supplied") is False, core.get("production_q_ledger_supplied"), False)
    check("R-192 first slot", core.get("r192_first_missing_slot") == "heat_root_incidence", core.get("r192_first_missing_slot"), "heat_root_incidence")
    check("not owner", core.get("production_owner") is False, core.get("production_owner"), False)

    payload = {
        "schema": "tect/a13-fref-nonlinear-gibbs-candidate-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": manifest["audit_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": core,
        "primary_stdout": p_run.stdout[-500:] if 'p_run' in locals() else "",
        "independent_stdout": i_run.stdout[-500:] if 'i_run' in locals() else "",
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        target = args.output if args.output.is_absolute() else ROOT / args.output
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(f"A1 F_REF NONLINEAR GIBBS INTEGRATED PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
