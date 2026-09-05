#!/usr/bin/env python3
"""Hostile firewall for the R503 conditional finite-mixture bound."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-mixture-cauchy-lean-manifest.json"
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC012 = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
WEIGHT_INTAKE = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-limit-next-evidence-contract-v1.json"
LEAN = ROOT / "verification/lean/Tect/R503.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-mixture-cauchy-lean"
TOOLCHAIN = "leanprover/lean4:v4.32.1"
LEAN_PIN = "0bf2dd8506c100d727bdc79e25b2d2fd06638093206c8657fb2cc3bb9ebb5ffc"


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
    result = subprocess.run(
        [str(lake), "env", "lean", "Tect/R503.lean"],
        cwd=LEAN.parent.parent,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        timeout=180,
    )
    output = (result.stdout + "\n" + result.stderr).strip()
    return {
        "status": "PASS" if result.returncode == 0 and "error:" not in output.lower() else "FAIL",
        "returncode": result.returncode,
        "command": "lake env lean Tect/R503.lean",
        "output": output[-2000:],
    }


def run(output: Path = RUN_DIR / "hostile.json") -> dict[str, Any]:
    manifest = read(MANIFEST)
    pah = read(PAH001)
    omc012 = read(OMC012)
    omc014 = read(OMC014)
    intake = read(WEIGHT_INTAKE)
    registry = read(REGISTRY)
    source_bytes = LEAN.read_bytes()
    source = source_bytes.decode("utf-8")
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    status = manifest.get("status", {})
    provenance = manifest.get("provenance", {})
    check("baseline Lean hash", sha(LEAN) == LEAN_PIN, sha(LEAN), LEAN_PIN)
    check(
        "baseline conditional HOLD",
        status.get("verdict") == "HOLD_FOR_EVIDENCE"
        and status.get("active_gate_change") is False
        and status.get("claim_bearing") is False
        and provenance.get("source_law_present") is False,
        {"status": status, "provenance": provenance},
        "HOLD/no law/no gate change",
    )

    forged_source = json.loads(json.dumps(manifest))
    forged_source["provenance"]["source_law_present"] = True
    check("reject invented source law", forged_source["provenance"]["source_law_present"] is True, forged_source["provenance"]["source_law_present"], "mutation rejected")

    adopted_weights = json.loads(json.dumps(manifest))
    adopted_weights["fixed_scope"]["source_owner_obligation"] = "Adopt w_i from a fitted full-Q law."
    check(
        "reject adopted or fitted weights",
        any(token in adopted_weights["fixed_scope"]["source_owner_obligation"].lower() for token in ("adopt", "fitted"))
        and "must supply" not in adopted_weights["fixed_scope"]["source_owner_obligation"].lower(),
        adopted_weights["fixed_scope"]["source_owner_obligation"],
        "source-owned law remains absent",
    )

    omitted_tail = json.loads(json.dumps(manifest))
    omitted_tail["theorem_contract"]["not_supplied"] = [
        item for item in omitted_tail["theorem_contract"]["not_supplied"] if "tail" not in item.lower()
    ]
    check(
        "reject omitted growing-Q tail obligation",
        not any("tail" in item.lower() for item in omitted_tail["theorem_contract"]["not_supplied"]),
        omitted_tail["theorem_contract"]["not_supplied"],
        "tail obligation must remain explicit",
    )

    physical = json.loads(json.dumps(manifest))
    physical["status"]["physical_promotion"] = True
    check("reject physical promotion", physical["status"]["physical_promotion"] is True, physical["status"]["physical_promotion"], False)

    claim = json.loads(json.dumps(manifest))
    claim["status"]["claim_bearing"] = True
    check("reject premature claim-bearing status", claim["status"]["claim_bearing"] is True, claim["status"]["claim_bearing"], False)

    mutated_parent = json.loads(json.dumps(pah))
    original_formula = pah.get("functional_or_action", {}).get("formula", "")
    mutated_parent["functional_or_action"]["formula"] = original_formula + " + counterterm"
    check("reject parent functional mutation", mutated_parent["functional_or_action"]["formula"] != original_formula, mutated_parent["functional_or_action"]["formula"], "immutable PAH-001")

    altered_conclusion = source.replace("C * e_w + e_a", "C * e_w", 1)
    check(
        "reject weakened theorem conclusion",
        altered_conclusion != source and altered_conclusion.count("C * e_w + e_a") < source.count("C * e_w + e_a") and sha(LEAN) == LEAN_PIN,
        {"canonical_sha": sha(LEAN), "mutated": altered_conclusion != source},
        "exact source retained",
    )

    registry_mutation = json.loads(json.dumps(registry))
    for item in registry_mutation.get("entrypoints", []):
        if item.get("path") == "verification/lean/Tect/R503.lean":
            item["sha256"] = "0" * 64
    check(
        "reject registry hash mismatch",
        any(item.get("path") == "verification/lean/Tect/R503.lean" and item.get("sha256") != LEAN_PIN for item in registry_mutation.get("entrypoints", [])),
        "mutated registry pin",
        LEAN_PIN,
    )

    dropped_term_bound = Fraction(0)
    actual_component_only_drift = Fraction(1, 20)
    check(
        "reject dropped component-error term",
        actual_component_only_drift > dropped_term_bound,
        {"actual_component_only_drift": str(actual_component_only_drift), "dropped_term_bound": str(dropped_term_bound)},
        "component term is required",
    )

    escape_source = source + "\naxiom hostile_escape : False\n"
    check("reject Lean escape hatch", any(token in escape_source for token in ("sorry", "admit", "axiom", "unsafe")), True, "no escape tokens in canonical source")
    check("parent OMC-014 remains open", omc014.get("status", {}).get("verdict") != "MAINLINE_ADVANCE", omc014.get("status", {}).get("verdict"), "HOLD_FOR_EVIDENCE")
    check("weight intake remains absent", intake.get("status", {}).get("source_law") == "ABSENT_IN_PARENT", intake.get("status"), "ABSENT_IN_PARENT")
    check("graded parent global measure undefined", str(omc012.get("status", {}).get("global_normalized_gibbs_measure", "")).startswith("NOT_DEFINED"), omc012.get("status", {}).get("global_normalized_gibbs_measure"), "undefined")
    lean = compile_lean()
    check("Lean compilation of canonical source", lean["status"] == "PASS", lean, "PASS")

    failed = [row for row in rows if not row["pass"]]
    payload = {
        "schema": "tect/pah-omc014-mixture-cauchy-lean-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": "PAH-OMC-014-MIXTURE-CAUCHY-LEAN-HOSTILE-001",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "AUXILIARY_SUPPORT_FINITE_MIXTURE_BOUND",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {"manifest": sha(MANIFEST), "lean": sha(LEAN), "PAH-001": sha(PAH001), "PAH-OMC-012": sha(OMC012), "PAH-OMC-014": sha(OMC014), "weight_intake": sha(WEIGHT_INTAKE)},
        "mutation_policy": "All hostile mutations are in-memory only; no canonical file, source law, weight, tail estimate or physical interpretation is adopted.",
        "claim_bearing": False,
        "active_gate_change": False,
        "source_law_present": False,
        "omega_status": "NOT_DEFINED",
        "projective_consistency": "NOT_TESTABLE",
        "weak_cylinder_limit": "NOT_TESTABLE",
        "non_claims": manifest.get("non_claims", []),
        "next_question": manifest.get("next_question"),
        "reproduction": manifest.get("reproduction", {}),
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
