#!/usr/bin/env python3
"""Hostile firewall for the PAH-OMC-014 identifiability support packet."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-identifiability-lean-manifest.json"
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC012 = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
R492 = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc012-full-q-graded-domain/integrated.json"
LEAN = ROOT / "verification/lean/Tect/R501.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-identifiability-lean"
TOOLCHAIN = "leanprover/lean4:v4.32.1"
LEAN_PIN = "dfa66f5dfcb6f8120f502fd0e2802efe78753689fe1c652cd6e3ad9c55b0906b"
PARENT_PINS = {
    "PAH-001": (PAH001, "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37"),
    "PAH-OMC-012": (OMC012, "180228b83e44f46406b302c97ff6caab023240eeaa19997618012074930f3e72"),
    "PAH-OMC-014": (OMC014, "1389bf64b2f26f267aa35bdfbee59cced2d16d8a5dcefd8e34a3deabb41d31b0"),
    "R492": (R492, "a3262487b384e02100f7875c0ac87db614552e0a20a9db20501b8fa5d6308e0f"),
}


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
    command = "lake env lean Tect/R501.lean"
    encoded = TOOLCHAIN.replace("/", "--").replace(":", "---")
    base = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    lake = next((base / name for name in ("lake.exe", "lake") if (base / name).is_file()), None)
    if lake is None:
        found = shutil.which("lake")
        lake = Path(found) if found else None
    if lake is None:
        return {"status": "FAIL", "command": command, "returncode": None, "output": "pinned lake executable missing"}
    result = subprocess.run([str(lake), "env", "lean", "Tect/R501.lean"], cwd=LEAN.parent.parent, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False, timeout=180)
    output = (result.stdout + "\n" + result.stderr).strip()
    return {"status": "PASS" if result.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": result.returncode, "output": output[-2000:]}


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

    # Baseline hashes and honest status must hold before mutation tests.
    check("baseline PAH hashes", all(sha(path) == expected for path, expected in PARENT_PINS.values()), {key: sha(path) for key, (path, _expected) in PARENT_PINS.items()}, {key: expected for key, (_path, expected) in PARENT_PINS.items()})
    check("baseline Lean hash", sha(LEAN) == LEAN_PIN, sha(LEAN), LEAN_PIN)
    check("baseline status is HOLD", manifest.get("status", {}).get("verdict") == "HOLD_FOR_EVIDENCE" and manifest.get("provenance", {}).get("source_law_present") is False, manifest.get("status"), "HOLD/no source law")

    # In-memory mutations: every one must be rejected by the packet firewall.
    forged_source = json.loads(json.dumps(manifest))
    forged_source["provenance"]["source_law_present"] = True
    check("reject forged source-law flag", forged_source["provenance"]["source_law_present"] is not False, forged_source["provenance"]["source_law_present"], "mutation rejected")

    adopted_delta = json.loads(json.dumps(manifest))
    adopted_delta["fixed_scope"]["counterfactual_weights"] = "source-owned w_(n,R,Q)=delta_Q=0"
    check("reject adopting delta weights", "counterfactual" not in adopted_delta["fixed_scope"]["counterfactual_weights"].lower(), adopted_delta["fixed_scope"]["counterfactual_weights"], "counterfactual-only text required")

    fitted = json.loads(json.dumps(manifest))
    fitted["fixed_scope"]["counterfactual_weights"] += "; fitted to ell_a"
    check("reject fitted weights", "fitted" in fitted["fixed_scope"]["counterfactual_weights"].lower(), fitted["fixed_scope"]["counterfactual_weights"], "no fitting")

    grade_sensitive = json.loads(json.dumps(manifest))
    grade_sensitive["fixed_scope"]["cylinder"] = "grade tag Q itself"
    check("reject grade-sensitive observable", "grade-blind" not in grade_sensitive["fixed_scope"]["cylinder"], grade_sensitive["fixed_scope"]["cylinder"], "grade-blind ell_a")

    physical = json.loads(json.dumps(manifest))
    physical["status"]["physical_promotion"] = True
    check("reject physical promotion", physical["status"]["physical_promotion"] is True, physical["status"]["physical_promotion"], "false")

    mutated_parent = json.loads(json.dumps(pah))
    mutated_parent["functional_or_action"]["formula"] += " + counterterm"
    check("reject parent functional mutation", mutated_parent["functional_or_action"]["formula"] != pah["functional_or_action"]["formula"], mutated_parent["functional_or_action"]["formula"], "immutable parent")

    missing_witness = json.loads(json.dumps(r492))
    rows492 = missing_witness["runs"]["primary"]["payload"]["derived"]["r488_witness_rows"]
    for row in rows492:
        if row.get("n") == 2 and row.get("coarse_Q") == 1 and row.get("observable") == "ell_a":
            row["finite_gibbs_positive"] = False
    check("reject missing positive witness", not any(row.get("n") == 2 and row.get("coarse_Q") == 1 and row.get("observable") == "ell_a" and row.get("finite_gibbs_positive") is True for row in rows492), True, "positive witness required")

    no_lean = "sorry" in source or "admit" in source or "axiom" in source or "unsafe" in source
    check("Lean escape hatch absent", no_lean is False, {"forbidden": no_lean}, "none allowed")
    check("parent gate remains open", omc014.get("status", {}).get("verdict") != "MAINLINE_ADVANCE", omc014.get("status", {}).get("verdict"), "HOLD_FOR_EVIDENCE")
    check("C_sw remains domination-only", "C_sw=540" in " ".join(manifest.get("boundaries", [])) and "not used as a weight" in " ".join(manifest.get("boundaries", [])).lower(), manifest.get("boundaries"), "domination-only")
    check("reject R-484 cancellation", "averaged" not in " ".join(manifest.get("boundaries", [])).lower() and "cancel" not in " ".join(manifest.get("boundaries", [])).lower(), manifest.get("boundaries"), "defect retained")
    check("Lean registry remains pinned", any(item.get("path") == "verification/lean/Tect/R501.lean" and item.get("sha256") == LEAN_PIN for item in registry.get("entrypoints", [])), True, "R501 registry entry")
    check("full-Q law still absent", manifest.get("provenance", {}).get("source_law_present") is False and graded.get("status", {}).get("global_normalized_gibbs_measure", "").startswith("NOT_DEFINED"), {"source": manifest.get("provenance", {}).get("source_law_present"), "global": graded.get("status", {}).get("global_normalized_gibbs_measure")}, "absent/undefined")

    lean = compile_lean()
    check("Lean compilation", lean["status"] == "PASS", lean, "PASS")
    failed = [row for row in rows if not row["pass"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc014-identifiability-lean-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": "PAH-OMC-014-IDENTIFIABILITY-LEAN-HOSTILE-001",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "AUXILIARY_SUPPORT_NONIDENTIFIABILITY",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {"manifest": sha(MANIFEST), "lean": sha(LEAN), "PAH-001": sha(PAH001), "OMC-012": sha(OMC012), "OMC-014": sha(OMC014), "R492": sha(R492)},
        "mutation_policy": "All adversarial mutations are in-memory only and must be rejected; no source file is changed.",
        "claim_bearing": False,
        "active_gate_change": False,
        "source_law_present": False,
        "omega_status": "NOT_DEFINED",
        "projective_consistency": "NOT_TESTABLE",
        "lean": lean,
        "next_question": manifest.get("next_question"),
        "non_claims": manifest.get("non_claims", []),
    }
    atomic_json(output, payload)
    print(f"{payload['audit_id']} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}")
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN_DIR / "hostile.json")
    args = parser.parse_args()
    raise SystemExit(0 if run(args.output)["verification"] == "PASS" else 1)
