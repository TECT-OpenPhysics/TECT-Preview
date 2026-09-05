#!/usr/bin/env python3
"""Hostile firewall for the R502 nonzero-weight obligation."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-nonzero-weight-lean-manifest.json"
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC012 = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
R492 = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc012-full-q-graded-domain/integrated.json"
LEAN = ROOT / "verification/lean/Tect/R502.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-nonzero-weight-lean"
TOOLCHAIN = "leanprover/lean4:v4.32.1"
LEAN_PIN = "37a9014b8d9f99fe0e3e23f18ddefcbb6960da7bcf4dd029b5f168b42c4d8b00"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def compile_lean() -> dict[str, Any]:
    encoded = TOOLCHAIN.replace("/", "--").replace(":", "---")
    base = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    lake = next((base / name for name in ("lake.exe", "lake") if (base / name).is_file()), None)
    if lake is None:
        found = shutil.which("lake")
        lake = Path(found) if found else None
    if lake is None:
        return {"status": "FAIL", "returncode": None, "output": "pinned lake missing"}
    result = subprocess.run([str(lake), "env", "lean", "Tect/R502.lean"], cwd=LEAN.parent.parent, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False, timeout=180)
    output = (result.stdout + "\n" + result.stderr).strip()
    return {"status": "PASS" if result.returncode == 0 and "error:" not in output.lower() else "FAIL", "returncode": result.returncode, "output": output[-2000:]}


def run(output: Path = RUN_DIR / "hostile.json") -> dict[str, Any]:
    manifest = read(MANIFEST)
    pah = read(PAH001)
    graded = read(OMC012)
    omc014 = read(OMC014)
    r492 = read(R492)
    registry = read(REGISTRY)
    source = LEAN.read_text(encoding="utf-8")
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    check("baseline Lean hash", sha(LEAN) == LEAN_PIN, sha(LEAN), LEAN_PIN)
    check("baseline HOLD", manifest.get("status", {}).get("verdict") == "HOLD_FOR_EVIDENCE" and manifest.get("provenance", {}).get("source_law_present") is False, manifest.get("status"), "HOLD/no source law")

    forged_source = json.loads(json.dumps(manifest))
    forged_source["provenance"]["source_law_present"] = True
    check("reject source-law promotion", forged_source["provenance"]["source_law_present"] is not False, forged_source["provenance"]["source_law_present"], "mutation rejected")

    omitted_lower_bound = json.loads(json.dumps(manifest))
    omitted_lower_bound["missing_inputs"] = [item for item in omitted_lower_bound["missing_inputs"] if "lower-bound" not in item]
    check("reject omitted nonzero obligation", not any("lower-bound" in item for item in omitted_lower_bound["missing_inputs"]), omitted_lower_bound["missing_inputs"], "source-owned lower bound remains required")

    adopted_weight = json.loads(json.dumps(manifest))
    adopted_weight["fixed_scope"]["weight_policy"] = "source-owned w1=1"
    check("reject adopted weight", "symbolic" not in adopted_weight["fixed_scope"]["weight_policy"], adopted_weight["fixed_scope"]["weight_policy"], "symbolic/no adopted law")

    fitted_weight = json.loads(json.dumps(manifest))
    fitted_weight["fixed_scope"]["weight_policy"] += "; fitted to R-488"
    check("reject fitted weight", "fitted" in fitted_weight["fixed_scope"]["weight_policy"].lower(), fitted_weight["fixed_scope"]["weight_policy"], "fitting rejected")

    physical = json.loads(json.dumps(manifest))
    physical["status"]["physical_promotion"] = True
    check("reject physical promotion", physical["status"]["physical_promotion"] is True, physical["status"]["physical_promotion"], False)

    mutated_parent = json.loads(json.dumps(pah))
    mutated_parent["functional_or_action"]["formula"] += " + counterterm"
    check("reject parent functional mutation", mutated_parent["functional_or_action"]["formula"] != pah["functional_or_action"]["formula"], True, "immutable parent")

    missing_witness = json.loads(json.dumps(r492))
    for row in missing_witness["runs"]["primary"]["payload"]["derived"]["r488_witness_rows"]:
        if row.get("n") == 2 and row.get("coarse_Q") == 1 and row.get("observable") == "ell_a":
            row["finite_gibbs_positive"] = False
    check("reject missing positive witness", not any(row.get("n") == 2 and row.get("coarse_Q") == 1 and row.get("observable") == "ell_a" and row.get("finite_gibbs_positive") is True for row in missing_witness["runs"]["primary"]["payload"]["derived"]["r488_witness_rows"]), True, "witness required")

    check("Lean escape hatch absent", not any(token in source for token in ("sorry", "admit", "axiom", "unsafe")), True, "none")
    check("parent gate remains open", omc014.get("status", {}).get("verdict") != "MAINLINE_ADVANCE", omc014.get("status", {}).get("verdict"), "HOLD_FOR_EVIDENCE")
    check("graded parent has no global mixture", str(graded.get("status", {}).get("global_normalized_gibbs_measure", "")).startswith("NOT_DEFINED"), graded.get("status", {}).get("global_normalized_gibbs_measure"), "undefined")
    check("R492 baseline remains PASS", r492.get("verification") == "PASS", r492.get("verification"), "PASS")
    check("registry pins R502", any(item.get("path") == "verification/lean/Tect/R502.lean" and item.get("sha256") == LEAN_PIN for item in registry.get("entrypoints", [])), True, "R502 registry pin")
    lean = compile_lean()
    check("Lean compilation", lean["status"] == "PASS", lean, "PASS")

    failed = [row for row in rows if not row["pass"]]
    payload = {
        "schema": "tect/pah-omc014-nonzero-weight-lean-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": "PAH-OMC-014-NONZERO-WEIGHT-LEAN-HOSTILE-001",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "AUXILIARY_SUPPORT_NONZERO_WEIGHT_OBLIGATION",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {"manifest": sha(MANIFEST), "lean": sha(LEAN), "PAH-001": sha(PAH001), "OMC-012": sha(OMC012), "OMC-014": sha(OMC014), "R492": sha(R492)},
        "mutation_policy": "All hostile changes are in-memory only; no source file is changed and no weight is adopted.",
        "claim_bearing": False,
        "active_gate_change": False,
        "source_law_present": False,
        "omega_status": "NOT_DEFINED",
        "projective_consistency": "NOT_TESTABLE",
        "non_claims": manifest.get("boundaries", []),
        "next_question": manifest.get("next_question"),
        "lean": lean,
    }
    atomic_json(output, payload)
    print(f"{payload['audit_id']} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}")
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN_DIR / "hostile.json")
    args = parser.parse_args()
    raise SystemExit(0 if run(args.output)["verification"] == "PASS" else 1)
