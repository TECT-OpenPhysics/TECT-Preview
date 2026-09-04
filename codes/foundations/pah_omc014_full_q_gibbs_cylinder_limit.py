#!/usr/bin/env python3
"""Primary source-scope audit for PAH-OMC-014.

This lane does not choose sector weights.  It checks the hash-pinned parent
packets for a source-owned full-Q law and records why the requested cylinder
functional cannot be evaluated when that law is absent.
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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-manifest.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc014-full-q-gibbs-cylinder-limit"
RESULT_ID = "R-494"
EXPLORATION_ID = "EXP-001504"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-014-FULL-Q-GIBBS-CYLINDER-LIMIT-PRIMARY-001"

PARENT_FILES = {
    "PAH-001": ROOT / "strategy/pa-hyp/PAH-001-v1.json",
    "PAH-OMC-004": ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json",
    "PAH-OMC-010": ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json",
    "PAH-OMC-010-MANIFEST": ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-manifest.json",
    "PAH-OMC-011": ROOT / "strategy/pa-hyp/PAH-OMC-011-eventual-intertwining-v1.json",
    "PAH-OMC-011-EXPLORATION": ROOT / "strategy/pa-hyp/PAH-OMC-011-eventual-intertwining-exploration.json",
    "PAH-OMC-012-EXPLORATION": ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-exploration.json",
    "PAH-OMC-012": ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json",
    "PAH-OMC-012-MANIFEST": ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-manifest.json",
    "PAH-OMC-013": ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json",
    "PAH-OMC-013-MANIFEST": ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-manifest.json",
    "R-493-INTEGRATED": ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc013-full-q-eventual-intertwining/integrated.json",
}


def load(path: Path) -> Any:
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


def walk(node: Any, path: str = "") -> list[tuple[str, str, Any]]:
    rows: list[tuple[str, str, Any]] = []
    if isinstance(node, dict):
        for key, value in node.items():
            child = f"{path}.{key}" if path else key
            rows.append((child, key, value))
            rows.extend(walk(value, child))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            rows.extend(walk(value, f"{path}[{index}]"))
    return rows


def apparent_sector_laws(parent_values: dict[str, Any]) -> list[dict[str, Any]]:
    """Find positive law declarations, excluding explicit absence prose."""
    law_keys = {
        "sector_weight_law", "cross_q_mixing_law", "global_mixture",
        "global_gibbs_measure", "weights_by_q", "sector_weights",
        "cross_q_weights", "full_q_weight_law", "w_(n,r,q)",
    }
    absence = re.compile(r"(?:absent|not_defined|not supplied|no cross.?q|no new normalized|open modeling input|not required)", re.I)
    found: list[dict[str, Any]] = []
    for source, value in parent_values.items():
        for location, key, item in walk(value):
            key_norm = str(key).lower().replace("-", "_")
            if key_norm in law_keys:
                text = json.dumps(item, ensure_ascii=True)
                if not absence.search(text):
                    found.append({"source": source, "location": location, "key": key, "value": item})
            if isinstance(item, str) and re.search(r"\bw_\s*\(?n\s*,\s*r\s*,\s*q\s*\)?\s*(?:=|:)", item, re.I):
                if not absence.search(item):
                    found.append({"source": source, "location": location, "text": item})
    return found


def run(output: Path = RUN_DIR / "primary.json") -> dict[str, Any]:
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    parents = {name: load(path) for name, path in PARENT_FILES.items()}
    rows: list[dict[str, Any]] = []

    def check(name: str, passed: bool, actual: Any = None, expected: Any = True) -> None:
        rows.append({"name": name, "pass": bool(passed), "actual": actual, "expected": expected})

    current_hashes = {name: sha(path) for name, path in PARENT_FILES.items()}
    current_hashes["PAH-OMC-014"] = sha(CONTRACT)
    current_hashes["PAH-OMC-014-MANIFEST"] = sha(MANIFEST)
    parent_pin_ok = all(
        manifest.get("parents", {}).get(name, {}).get("sha256") == digest
        for name, digest in current_hashes.items() if name in manifest.get("parents", {})
    )
    check("all declared parent hashes are current", parent_pin_ok, current_hashes, "manifest parent hashes")
    check("contract hash is pinned", manifest.get("contract", {}).get("sha256") == current_hashes["PAH-OMC-014"], manifest.get("contract"), current_hashes["PAH-OMC-014"])
    check("contract identity", contract.get("contract_id") == "PAH-OMC-014" and manifest.get("manifest_id") == "PAH-OMC-014-MANIFEST", {"contract": contract.get("contract_id"), "manifest": manifest.get("manifest_id")}, "PAH-OMC-014")
    check("hold status and non-bearing flags", contract["status"]["verdict"] == "HOLD_FOR_EVIDENCE" and contract["status"]["claim_bearing"] is False and contract["status"]["active_gate_change"] is False and manifest["status"] == "HOLD_FOR_EVIDENCE", contract["status"], "HOLD_FOR_EVIDENCE/non-bearing/no gate change")
    check("preservation firewall", all(value is True for value in contract["preservation_firewall"].values()) and manifest.get("no_parent_mutation") is True, contract["preservation_firewall"], "all true")

    pah = parents["PAH-001"]
    omc010 = parents["PAH-OMC-010"]
    omc012 = parents["PAH-OMC-012"]
    omc013 = parents["PAH-OMC-013"]
    order = pah.get("ordered_limits", {}).get("order", [])
    order_ids = [item.get("id") for item in order]
    expected_order = ["LOCAL_STATE_CUTOFF", "LATTICE_REFINEMENT", "VOLUME_EXHAUSTION", "PHASE_SELECTOR", "APERTURE_COLLAPSE", "GROUND_STATE", "OBSERVATION_TIME"]
    state_formula = pah.get("dynamics", {}).get("state", "")
    check("PAH-001 fixed-Q Gibbs formula", all(token in state_formula for token in ("pi_(rho,Q)", "Z_(rho,Q)^(-1)", "exp", "beta", "F_rho")), state_formula, "exact displayed fixed-Q formula")
    check("PAH-001 counting normalization", pah.get("finite_regulator", {}).get("normalization") == "counting measure on the fixed-Q finite configuration space and Z_(rho,Q)=sum_x exp(-beta F_rho(x))", pah.get("finite_regulator", {}).get("normalization"), "fixed-Q counting normalization")
    check("OMC-010 keeps fixed-Q state weight", omc010.get("exact_scope", {}).get("state_weight", "").startswith("W_(n,R)(omega)=pi_(rho_R,Q)"), omc010.get("exact_scope", {}).get("state_weight"), "fixed-Q pi")
    check("OMC-012 explicitly leaves global measure undefined", omc012.get("status", {}).get("global_normalized_gibbs_measure") == "NOT_DEFINED_BY_PARENT; not required for this domain-map gate", omc012.get("status", {}).get("global_normalized_gibbs_measure"), "NOT_DEFINED_BY_PARENT")
    check("OMC-012 explicitly supplies no cross-Q mixing", "no cross-Q mixing probabilities" in omc012.get("exact_scope", {}).get("gibbs_reference", "") and "no cross-Q mixture" in " ".join(omc012.get("non_claims", [])), omc012.get("exact_scope", {}).get("gibbs_reference"), "no source-owned cross-Q law")
    check("OMC-012 norm is direct-sum family, not a probability", "direct-sum family norm" in omc012.get("exact_scope", {}).get("graded_norm", "") and "single probability" in omc012.get("exact_scope", {}).get("graded_norm", ""), omc012.get("exact_scope", {}).get("graded_norm"), "component norms only")
    check("OMC-013 retains componentwise Gibbs norm", "component Gibbs weighted norm" in omc013.get("exact_scope", {}).get("gibbs_norm", "") and "cross-Q probability" in omc013.get("exact_scope", {}).get("gibbs_norm", ""), omc013.get("exact_scope", {}).get("gibbs_norm"), "component-only norm")
    check("declared PAH-001 order is hash-pinned and unproved", order_ids == expected_order and all(item.get("status") == "DECLARED_NOT_PROVED" for item in order), order_ids, expected_order)
    check("critical aperture-before-observation rule retained", pah.get("ordered_limits", {}).get("critical_order_rule") == "APERTURE_COLLAPSE precedes OBSERVATION_TIME; no reversed-order horizon claim is permitted.", pah.get("ordered_limits", {}).get("critical_order_rule"), "aperture before observation")

    laws = apparent_sector_laws(parents)
    check("no positive source-owned full-Q sector law found", not laws, laws, "empty source-scope law declarations")
    check("candidate measure is not instantiated", contract.get("status", {}).get("omega_status") == "NOT_DEFINED" and contract.get("status", {}).get("projective_consistency") == "NOT_TESTABLE", contract.get("status"), "not defined/not testable")
    check("Cauchy and stationarity are correctly withheld", contract.get("status", {}).get("weak_cylinder_limit") == "NOT_TESTABLE" and contract.get("status", {}).get("stationarity") == "NOT_TESTABLE", contract.get("status"), "not testable")
    check("R-484 defect retained", contract.get("status", {}).get("r484_boundary_defect") == "RETAINED_16_OVER_9" and "16/9" in contract.get("exact_scope", {}).get("boundary_input", ""), contract.get("exact_scope", {}).get("boundary_input"), "16/9 retained")
    check("R-490 C_sw role is domination-only", contract.get("status", {}).get("csw_role") == "DOMINATION_ONLY" and "cannot define cross-Q" in contract.get("exact_scope", {}).get("uniformity_input", ""), contract.get("exact_scope", {}).get("uniformity_input"), "domination only")
    check("physical non-claim firewall", contract.get("status", {}).get("physical_promotion") is False and any("No physical Pre-A" in item for item in contract.get("non_claims", [])), contract.get("non_claims"), True)

    failed = [row for row in rows if not row["pass"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc014-full-q-gibbs-cylinder-limit-primary/1.0",
        "run_kind": "primary",
        "audit_id": AUDIT_ID,
        "result_id": RESULT_ID,
        "exploration_id": contract.get("exploration_id", EXPLORATION_ID),
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "HOLD_FOR_EVIDENCE_SOURCE_OWNER_FULL_Q_WEIGHT_LAW_ABSENT",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": current_hashes,
        "candidate_sector_law": "ABSENT_IN_SOURCE",
        "omega_status": "NOT_DEFINED",
        "projective_consistency": "NOT_TESTABLE",
        "weak_cylinder_limit": "NOT_TESTABLE",
        "positivity_normalization": "NOT_TESTABLE",
        "stationarity": "NOT_TESTABLE",
        "boundary": {"R484_hidden_diagonal_defect": "16/9", "averaging": False, "counterterm": False},
        "uniformity": {"C_sw": 540, "role": "domination_only", "cauchy_bound": "not supplied"},
        "claim_bearing": False,
        "active_gate_change": False,
        "non_claims": contract["non_claims"],
        "missing_assumptions": contract["missing_assumptions"],
        "reproduction": contract["reproduction"],
        "next_question": contract["single_next_question"],
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}; source_law={payload['candidate_sector_law']}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN_DIR / "primary.json")
    args = parser.parse_args()
    payload = run(args.output)
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
