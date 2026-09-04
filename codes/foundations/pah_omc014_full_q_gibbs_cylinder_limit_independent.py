#!/usr/bin/env python3
"""Independent source-scope reconstruction for PAH-OMC-014.

The implementation intentionally does not import the primary verifier.  It
rebuilds the finite-component versus full-Q distinction from raw JSON and
checks that a global functional cannot be evaluated without an admitted
sector law.
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
AUDIT_ID = "PAH-OMC-014-FULL-Q-GIBBS-CYLINDER-LIMIT-INDEPENDENT-001"

PARENTS = {
    "PAH-001": ROOT / "strategy/pa-hyp/PAH-001-v1.json",
    "PAH-OMC-004": ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json",
    "PAH-OMC-010": ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json",
    "PAH-OMC-011": ROOT / "strategy/pa-hyp/PAH-OMC-011-eventual-intertwining-v1.json",
    "PAH-OMC-011-EXPLORATION": ROOT / "strategy/pa-hyp/PAH-OMC-011-eventual-intertwining-exploration.json",
    "PAH-OMC-012-EXPLORATION": ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-exploration.json",
    "PAH-OMC-012": ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json",
    "PAH-OMC-013": ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json",
    "R-493-INTEGRATED": ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc013-full-q-eventual-intertwining/integrated.json",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
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


def flatten_strings(node: Any, location: str = "") -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if isinstance(node, dict):
        for key, value in node.items():
            child = f"{location}.{key}" if location else key
            if isinstance(value, str):
                rows.append((child, value))
            rows.extend(flatten_strings(value, child))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            rows.extend(flatten_strings(value, f"{location}[{index}]"))
    return rows


def run(output: Path = RUN_DIR / "independent.json") -> dict[str, Any]:
    contract = read_json(CONTRACT)
    manifest = read_json(MANIFEST)
    pah = read_json(PARENTS["PAH-001"])
    omc010 = read_json(PARENTS["PAH-OMC-010"])
    omc012 = read_json(PARENTS["PAH-OMC-012"])
    omc013 = read_json(PARENTS["PAH-OMC-013"])
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(passed), "actual": actual, "expected": expected})

    actual_hashes = {name: digest(path) for name, path in PARENTS.items()}
    check("independent parent hash reconstruction", all(manifest["parents"][name]["sha256"] == actual_hashes[name] for name in PARENTS), actual_hashes, "all manifest parent hashes")
    check("finite component state is normalized by source", "counting measure on the fixed-Q finite configuration space" in pah.get("finite_regulator", {}).get("normalization", "") and "Z_(rho,Q)=sum_x exp(-beta F_rho(x))" in pah.get("finite_regulator", {}).get("normalization", ""), pah.get("finite_regulator", {}).get("normalization"), "fixed-Q Z formula")
    state_formula = pah.get("dynamics", {}).get("state", "")
    check("finite component Gibbs state is positive form", all(token in state_formula for token in ("exp", "beta", "F_rho(x)", "Z_(rho,Q)^(-1)")), state_formula, "positive normalized component state")
    check("OMC-010 path is unchanged", omc010.get("exact_scope", {}).get("functional", "").startswith("Exactly PAH-001 F_rho") and "R_max=R" in omc010.get("exact_scope", {}).get("state_space", ""), {"functional": omc010.get("exact_scope", {}).get("functional"), "state_space": omc010.get("exact_scope", {}).get("state_space")}, "unchanged PAH path")
    check("full-Q domain is a disjoint union", omc012.get("exact_scope", {}).get("graded_state_space", "").startswith("Omega_n^gr(R)=disjoint_union_") and "grade is part" in omc012.get("exact_scope", {}).get("graded_state_space", ""), omc012.get("exact_scope", {}).get("graded_state_space"), "disjoint union over Q")
    check("source expressly omits the mixing law", omc012.get("status", {}).get("global_normalized_gibbs_measure", "").startswith("NOT_DEFINED_BY_PARENT") and "no cross-Q mixing probabilities" in omc012.get("exact_scope", {}).get("gibbs_reference", ""), {"status": omc012.get("status", {}).get("global_normalized_gibbs_measure"), "reference": omc012.get("exact_scope", {}).get("gibbs_reference")}, "explicit source omission")
    check("direct-sum norm does not supply sector probabilities", "direct-sum family norm" in omc012.get("exact_scope", {}).get("graded_norm", "") and "single probability measure" in omc012.get("exact_scope", {}).get("graded_norm", ""), omc012.get("exact_scope", {}).get("graded_norm"), "norm is not a measure")
    check("OMC-013 remains componentwise", "component Gibbs weighted norm" in omc013.get("exact_scope", {}).get("gibbs_norm", "") and "cross-Q probability" in omc013.get("exact_scope", {}).get("gibbs_norm", ""), omc013.get("exact_scope", {}).get("gibbs_norm"), "no global Gibbs law")

    parent_text = "\n".join(path.read_text(encoding="utf-8") for path in PARENTS.values())
    actual_law_patterns = [
        r"\bsector_weight_law\b\s*[:=]\s*(?!\"?(?:ABSENT|NONE|NOT_DEFINED))",
        r"\bcross_q_mixing_law\b\s*[:=]\s*(?!\"?(?:ABSENT|NONE|NOT_DEFINED))",
        r"\bweights_by_q\b\s*[:=]\s*(?!\"?(?:ABSENT|NONE|NOT_DEFINED))",
        r"w_\s*\(\s*n\s*,\s*R\s*,\s*Q\s*\)\s*(?:=|:)\s*[^\s\"}]",
    ]
    hits = [pattern for pattern in actual_law_patterns if re.search(pattern, parent_text, re.I)]
    check("no actual sector-law equation in parent corpus", not hits, hits, "no positive law declaration")
    check("contract refuses to instantiate weights", contract.get("exact_scope", {}).get("source_weight_law", "").startswith("ABSENT_IN_SOURCE") and contract.get("status", {}).get("omega_status") == "NOT_DEFINED", {"source_weight_law": contract.get("exact_scope", {}).get("source_weight_law"), "omega_status": contract.get("status", {}).get("omega_status")}, "absence retained")
    check("required Cauchy estimate is withheld", contract.get("status", {}).get("weak_cylinder_limit") == "NOT_TESTABLE" and "explicit Cauchy error" in contract.get("missing_assumptions", [""])[3], contract.get("missing_assumptions"), "no unsupported limit")
    check("boundary datum is not cancelled", contract.get("status", {}).get("r484_boundary_defect") == "RETAINED_16_OVER_9" and "no averaging" in contract.get("exact_scope", {}).get("boundary_input", ""), contract.get("exact_scope", {}).get("boundary_input"), "16/9 retained")
    check("C_sw is not promoted to a weight", contract.get("status", {}).get("csw_role") == "DOMINATION_ONLY" and "cannot define cross-Q" in contract.get("exact_scope", {}).get("uniformity_input", ""), contract.get("exact_scope", {}).get("uniformity_input"), "domination only")
    check("no physical promotion", contract.get("status", {}).get("physical_promotion") is False and any("No physical Pre-A" in item for item in contract.get("non_claims", [])), contract.get("non_claims"), True)

    failed = [row for row in checks if not row["pass"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc014-full-q-gibbs-cylinder-limit-independent/1.0",
        "run_kind": "independent",
        "audit_id": AUDIT_ID,
        "result_id": RESULT_ID,
        "exploration_id": contract.get("exploration_id", EXPLORATION_ID),
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "INDEPENDENT_SOURCE_SCOPE_RECONSTRUCTION",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": actual_hashes,
        "candidate_sector_law": "ABSENT_IN_SOURCE",
        "omega_status": "NOT_DEFINED",
        "projective_consistency": "NOT_TESTABLE",
        "weak_cylinder_limit": "NOT_TESTABLE",
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
    parser.add_argument("--output", type=Path, default=RUN_DIR / "independent.json")
    args = parser.parse_args()
    return 0 if run(args.output)["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
