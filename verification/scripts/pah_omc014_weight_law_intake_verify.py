#!/usr/bin/env python3
"""Verify the PAH-OMC-014 next-evidence intake contract.

This is a specification audit.  It checks that the future source-owner
payload is explicit and that no sector-weight value has been smuggled into
the repository.  It does not instantiate a full-Q Gibbs state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-limit-next-evidence-contract-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-limit-next-evidence-manifest.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
OMC014_MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-manifest.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-weight-law-intake"
RESULT_ID = "R-494"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-014-WEIGHT-LAW-INTAKE-INTEGRATED-001"


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
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


def run(output: Path = RUN_DIR / "integrated.json") -> dict[str, Any]:
    contract = read(CONTRACT)
    manifest = read(MANIFEST)
    omc014 = read(OMC014)
    omc014_manifest = read(OMC014_MANIFEST)
    rows: list[dict[str, Any]] = []

    def check(name: str, passed: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(passed), "actual": actual, "expected": expected})

    current_contract = sha(CONTRACT)
    current_omc014 = sha(OMC014)
    current_omc014_manifest = sha(OMC014_MANIFEST)
    check("intake contract hash pin", manifest.get("contract", {}).get("sha256") == current_contract, manifest.get("contract"), current_contract)
    check("PAH-OMC-014 parent hash pin", manifest.get("parents", {}).get("PAH-OMC-014", {}).get("sha256") == current_omc014, manifest.get("parents", {}).get("PAH-OMC-014"), current_omc014)
    check("PAH-OMC-014 manifest parent hash pin", manifest.get("parents", {}).get("PAH-OMC-014-MANIFEST", {}).get("sha256") == current_omc014_manifest, manifest.get("parents", {}).get("PAH-OMC-014-MANIFEST"), current_omc014_manifest)
    check("intake identity", contract.get("contract_id") == "PAH-OMC-014-WEIGHT-INTAKE" and manifest.get("manifest_id") == "PAH-OMC-014-WEIGHT-INTAKE-MANIFEST", {"contract": contract.get("contract_id"), "manifest": manifest.get("manifest_id")}, "intake contract/manifest")
    check("intake is non-bearing HOLD", contract.get("status", {}).get("intake_ready") is True and contract.get("status", {}).get("source_law") == "ABSENT_IN_PARENT" and contract.get("status", {}).get("verdict") == "HOLD_FOR_EVIDENCE" and manifest.get("status") == "HOLD_FOR_EVIDENCE", contract.get("status"), "ready/HOLD/absent")
    check("no parent mutation", contract.get("provenance", {}).get("source_law_present") is False and manifest.get("no_parent_mutation") is True and manifest.get("claim_bearing") is False and manifest.get("active_gate_change") is False, {"provenance": contract.get("provenance"), "manifest": manifest}, "no source law/no mutation/no gate change")

    fixed = contract.get("fixed_scope", {})
    functional_text = fixed.get("functional_and_rates", "")
    check("functional and rate firewall", "exactly the PAH-001 functional" in functional_text and "no counterterm" in functional_text and "new carrier" in functional_text, functional_text, "unchanged model")
    check("full-Q domain firewall", "PAH-OMC-012 full-Q disjoint union" in fixed.get("finite_domain", "") and "neutral projection" in fixed.get("finite_domain", ""), fixed.get("finite_domain"), "unchanged graded domain")
    check("component states remain fixed-Q", "normalized fixed-Q states" in fixed.get("component_states", "") and "PAH-001" in fixed.get("component_states", ""), fixed.get("component_states"), "source component states")
    check("cylinder is unchanged", "grade-blind" in fixed.get("cylinder", "") and "R-488" in fixed.get("cylinder", ""), fixed.get("cylinder"), "common cylinder")
    order = fixed.get("limit_order", "")
    required_order = ["LOCAL_STATE_CUTOFF", "LATTICE_REFINEMENT", "VOLUME_EXHAUSTION", "PHASE_SELECTOR", "APERTURE_COLLAPSE", "OBSERVATION_TIME"]
    check("PAH-001 order is retained", all(token in order for token in required_order) and order.index("APERTURE_COLLAPSE") < order.index("OBSERVATION_TIME"), order, "declared order with aperture before observation")

    conditions = contract.get("symbolic_acceptance_conditions", {})
    required_conditions = {"sector_law", "finite_functional", "projective_consistency", "cauchy_error", "positivity_and_normalization", "r488_nonzero", "stationarity", "boundary_accounting", "uniformity_role"}
    check("all conditional tests are specified", required_conditions.issubset(conditions) and all(isinstance(conditions[key], str) and conditions[key].strip() for key in required_conditions), sorted(conditions), sorted(required_conditions))
    sector_law = conditions.get("sector_law", "")
    direct_weight_assignment = re.search(r"(?:^|[.;])\s*(?:define|set|let)?\s*w_\s*\(\s*n\s*,\s*R\s*,\s*Q\s*\)\s*=\s*[-+]?\d", sector_law, flags=re.IGNORECASE)
    check("no weight value is instantiated", "no values are instantiated here" in sector_law.lower() and direct_weight_assignment is None, sector_law, "symbolic law only")
    check("source-owner payload is explicit", len(contract.get("required_source_owner_payload", [])) >= 7 and any("versioned law file" in item for item in contract["required_source_owner_payload"]), contract.get("required_source_owner_payload"), "hash/normalization/topology/holdout/domain requirements")
    check("forbidden repairs are explicit", len(contract.get("forbidden_repairs", [])) >= 4 and any("Uniform weights" in item for item in contract["forbidden_repairs"]) and any("C_sw=540" in item for item in contract["forbidden_repairs"]), contract.get("forbidden_repairs"), "no fitting/averaging/counterterm")

    check("R-494 source audit remains absent", omc014.get("status", {}).get("omega_status") == "NOT_DEFINED" and omc014.get("exact_scope", {}).get("source_weight_law", "").startswith("ABSENT_IN_SOURCE"), omc014.get("status"), "R-494 absent source law")
    check("R-484 and C_sw constraints are retained", "16/9" in conditions.get("boundary_accounting", "") and "C_sw=540" in conditions.get("uniformity_role", ""), {"boundary": conditions.get("boundary_accounting"), "uniformity": conditions.get("uniformity_role")}, "defect retained/domination-only")
    check("non-claims include physical firewall", all(any(term in item for item in contract.get("non_claims", [])) for term in ("does not define", "No physical Pre-A", "Markov time")), contract.get("non_claims"), "no model/physical promotion")
    lean_reason = manifest.get("lean", {}).get("reason", "")
    check("manifest keeps Lean non-applicable honest", manifest.get("lean", {}).get("status") == "NOT_APPLICABLE" and "No theorem" in lean_reason, manifest.get("lean"), "no false Lean theorem")

    # Hostile checks: these mutations must remain rejected by the intake spec.
    forbidden = contract.get("forbidden_repairs", [])
    check("hostile uniform-weight repair rejected", any("Uniform weights" in item for item in forbidden), forbidden, "rejected")
    check("hostile fitted-weight repair rejected", any("fitted" in item.lower() for item in forbidden), forbidden, "rejected")
    boundary_text = " ".join(forbidden) + " " + conditions.get("boundary_accounting", "")
    check("hostile boundary repair rejected", "R-484" in boundary_text and "defect" in boundary_text.lower() and ("averaged" in boundary_text.lower() or "cancelled" in boundary_text.lower() or "cancellation" in boundary_text.lower()), forbidden, "rejected")
    check("hostile physical promotion rejected", manifest.get("physical_promotion") is False and contract.get("provenance", {}).get("physical_authority") is False, {"manifest": manifest.get("physical_promotion"), "provenance": contract.get("provenance")}, "rejected")

    failed = [row for row in rows if not row["pass"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc014-weight-law-intake-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": AUDIT_ID,
        "result_id": RESULT_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "NEXT_EVIDENCE_CONTRACT_READY",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {"PAH-OMC-014-WEIGHT-INTAKE": current_contract, "PAH-OMC-014-WEIGHT-INTAKE-MANIFEST": sha(MANIFEST), "PAH-OMC-014": current_omc014, "PAH-OMC-014-MANIFEST": current_omc014_manifest},
        "intake_ready": True,
        "source_law_present": False,
        "omega_status": "NOT_DEFINED",
        "claim_bearing": False,
        "active_gate_change": False,
        "non_claims": contract["non_claims"],
        "next_question": contract["single_next_question"],
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}; intake_ready={payload['intake_ready']}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN_DIR / "integrated.json")
    args = parser.parse_args()
    return 0 if run(args.output)["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
