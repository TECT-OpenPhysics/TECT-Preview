"""Integrated verifier for the exact nonlinear root-filtration witness."""

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
MANIFEST = ROOT / "strategy" / "pre-a13-nonlinear-root-filtration-mixing-manifest.json"
PRIMARY = ROOT / "codes" / "foundations" / "a13_nonlinear_root_filtration_mixing.py"
INDEPENDENT = ROOT / "codes" / "foundations" / "a13_nonlinear_root_filtration_mixing_independent.py"
DEFAULT_OUTPUT = ROOT / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-integrated-nonlinear-root-filtration-mixing" / "result.json"


def sha(path: Path) -> str:
    raw = path.read_bytes().replace(bytes([13, 10]), bytes([10])).replace(bytes([13]), bytes([10]))
    return hashlib.sha256(raw).hexdigest()


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

    check("manifest identity", manifest["audit_id"] == "A13-NONLINEAR-ROOT-FILTRATION-MIXING", manifest["audit_id"], "A13-NONLINEAR-ROOT-FILTRATION-MIXING")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negative", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    for label, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        check(f"source {label}", path.is_file() and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    for label, item in manifest["files"].items():
        path = ROOT / item["path"]
        check(f"file {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])

    certificate = (ROOT / manifest["files"]["certificate"]["path"]).read_text(encoding="utf-8")
    check("exact identity in certificate", "rho^2\\phi=z^{-1}(1+z)^5" in certificate, True, True)
    owner_tokens_ok = all(token in certificate for token in ("heat-root incidence", "raw-current", "q-ledger", "A13/T-050"))
    check("owner boundary in certificate", owner_tokens_ok, owner_tokens_ok, True)
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
        check(f"no lane imports {path.name}", not any(name.startswith("a13_nonlinear_root_filtration_mixing") for name in imports), imports, "no lane imports")

    with tempfile.TemporaryDirectory(prefix="a13-nonlinear-mixing-") as temp:
        p_out = Path(temp) / "primary.json"
        i_out = Path(temp) / "independent.json"
        common = [sys.executable, "-B"]
        p_run = subprocess.run(common + [str(PRIMARY), "--output", str(p_out)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False)
        i_run = subprocess.run(common + [str(INDEPENDENT), "--output", str(i_out)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False)
        check("primary exit", p_run.returncode == 0, p_run.returncode, 0)
        check("independent exit", i_run.returncode == 0, i_run.returncode, 0)
        check("primary output", p_out.is_file(), p_out.is_file(), True)
        check("independent output", i_out.is_file(), i_out.is_file(), True)
        p_payload = json.loads(p_out.read_text(encoding="utf-8"))
        i_payload = json.loads(i_out.read_text(encoding="utf-8"))
        check("derived agreement", p_payload.get("derived") == i_payload.get("derived"), p_payload.get("derived"), i_payload.get("derived"))
        check("child PASS", p_payload.get("verdict") == "PASS" and i_payload.get("verdict") == "PASS", [p_payload.get("verdict"), i_payload.get("verdict")], ["PASS", "PASS"])
        core = p_payload.get("derived", {})

    check("lower leakage", core.get("lower_leakage") is True, core.get("lower_leakage"), True)
    check("upper leakage", core.get("upper_leakage") is True, core.get("upper_leakage"), True)
    check("zero leakage", core.get("zero_mode_created") is True, core.get("zero_mode_created"), True)
    check("naive filtration false", core.get("naive_root_subspace_invariant") is False, core.get("naive_root_subspace_invariant"), False)
    check("owner slots remain missing", all(value is False for value in manifest["derived_contract"]["owner_slots"].values()), manifest["derived_contract"]["owner_slots"], "all false")
    check("no A13 closure", all(token in manifest["boundary"] for token in ("A13/T-050", "Sector-A", "Pre-A")), manifest["boundary"], "scope boundary")

    payload = {
        "schema": "tect/a13-nonlinear-root-filtration-mixing-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": manifest["audit_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": core,
        "primary_stdout": p_run.stdout[-500:] if "p_run" in locals() else "",
        "independent_stdout": i_run.stdout[-500:] if "i_run" in locals() else "",
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        target = args.output if args.output.is_absolute() else ROOT / args.output
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"A13 NONLINEAR ROOT FILTRATION MIXING INTEGRATED PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
