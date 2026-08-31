#!/usr/bin/env python3
"""Primary contract audit for the A5 T6 Lean cross-check (R-475).

This sidecar checks the already operator-confirmed A5 conditional-composition
contract.  It does not replace the A5 proof package: the analytic premises,
the two branch theorems, and the operator confirmation remain authoritative in
the existing A5 files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import tempfile
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
__claims__ = ["A5-SECTOR-A-SYNTHESIS"]

getcontext().prec = 80
REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / __claims__[0]
MANIFEST = CLAIM / "conditional_composition_manifest.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-09-01-a5-r475-lean-crosscheck" / "primary.json"

# The A5 manifest retains compact compatibility aliases; resolve them to the
# canonical current claim directories before reading any authority.
PATH_ALIASES = (
    ("claims/a1k", "claims/A1-PRODUCTION-KERNEL-MANIFEST"),
    ("claims/a1f", "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION"),
    ("claims/a2", "claims/A2-FULL-PRODUCTION-WELLPOSED"),
    ("claims/a3f", "claims/A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"),
    ("claims/a3p", "claims/A3-PERTURBATIVE-CONTINUUM-CORRELATORS"),
    ("claims/a4", "claims/A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE"),
    ("claims/a5", "claims/A5-SECTOR-A-SYNTHESIS"),
)

# Explicit test oracles for the frozen A5 contract.  Derived numeric values are
# read from the source manifests below, never copied into the assertions.
EXPECTED_HYPOTHESES = [
    "A5-H1-CANONICAL-KERNEL-MANIFEST",
    "A1-KERNEL-CONV",
    "A1-SHELL-POSITIVITY",
    "A2-H2-SEXTIC-COERCIVITY",
    "A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL",
    "A3-H1-DIM3-Q4-KERNEL",
    "A3-H2-IR-POSITIVITY",
]
EXPECTED_FULL_CHAIN = [
    "A1-PRODUCTION-FUNCTIONAL-REALISATION",
    "A2-FULL-PRODUCTION-WELLPOSED",
    "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM",
]
EXPECTED_SCALAR_CHAIN = [
    "A3-PERTURBATIVE-CONTINUUM-CORRELATORS",
    "A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE",
]
EXPECTED_T6_PREMISES = {
    "A2-FULL-PRODUCTION-WELLPOSED",
    "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM",
    "A3-PERTURBATIVE-CONTINUUM-CORRELATORS",
    "A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE",
}
EXPECTED_EXCLUSION_TOKENS = [
    "parameter-identical",
    "derivative Class-II",
    "eta_shell",
    "t=0",
    "historical",
    "Route-B",
    "unsmeared",
    "infinite-volume",
    "phase transition",
    "BCC",
    "Sector-B",
    "T7",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_repo_path(value: str) -> Path:
    for alias, canonical in sorted(PATH_ALIASES, key=lambda row: -len(row[0])):
        if value == alias or value.startswith(alias + "/"):
            return REPO / (canonical + value[len(alias) :])
    return REPO / value


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def check(assertions: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    assertions.append(
        {
            "name": name,
            "status": "PASS" if passed else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = load_json(MANIFEST)
    contract = manifest["theorem_contract"]
    assertions: list[dict[str, Any]] = []

    check(
        assertions,
        "manifest_scope_is_operator_confirmed_t6",
        manifest.get("schema") == "tect/a5-t6-conditional-composition/1.1"
        and manifest.get("claim_id") == __claims__[0]
        and manifest.get("candidate_tier") == "T6"
        and manifest.get("publication_state") == "T6-PUBLISHED-OPERATOR-CONFIRMED",
        {
            "schema": manifest.get("schema"),
            "claim_id": manifest.get("claim_id"),
            "candidate_tier": manifest.get("candidate_tier"),
            "publication_state": manifest.get("publication_state"),
        },
        "tect/a5-t6-conditional-composition/1.1 + T6-PUBLISHED-OPERATOR-CONFIRMED",
    )

    contract_digest = canonical_digest(contract)
    check(
        assertions,
        "theorem_contract_digest_matches",
        contract_digest == manifest.get("theorem_contract_sha256"),
        contract_digest,
        manifest.get("theorem_contract_sha256"),
    )

    confirmation = manifest["operator_confirmation"]
    source = resolve_repo_path(confirmation["candidate_source"])
    pdf = resolve_repo_path(confirmation["candidate_pdf"])
    confirmation_ok = (
        confirmation.get("status") == "CONFIRMED"
        and confirmation.get("confirmed_by") == "Jusang Lee"
        and confirmation.get("confirmed_on") == "2026-07-20"
        and confirmation.get("published_bundle_authorized") is True
        and source.is_file()
        and pdf.is_file()
        and sha256(source) == confirmation.get("candidate_source_sha256")
        and sha256(pdf) == confirmation.get("candidate_pdf_sha256")
    )
    check(
        assertions,
        "operator_confirmation_source_and_pdf_are_hash_bound",
        confirmation_ok,
        {
            "status": confirmation.get("status"),
            "source_exists": source.is_file(),
            "pdf_exists": pdf.is_file(),
            "source_sha256": sha256(source) if source.is_file() else None,
            "pdf_sha256": sha256(pdf) if pdf.is_file() else None,
        },
        "confirmed source/PDF hashes and published_bundle_authorized=true",
    )

    authority_rows = []
    for key, row in manifest["authority"].items():
        path = resolve_repo_path(row["path"])
        actual = sha256(path) if path.is_file() else None
        authority_rows.append({"id": key, "path": row["path"], "actual": actual, "expected": row["sha256"]})
    check(
        assertions,
        "all_declared_a5_authorities_match",
        bool(authority_rows) and all(row["actual"] == row["expected"] for row in authority_rows),
        authority_rows,
        "every declared authority hash",
    )

    hypotheses = contract["named_hypotheses"]
    gates_text = (REPO / "claims" / "GATES.md").read_text(encoding="utf-8")
    registered = {name: f"### **{name}**" in gates_text for name in hypotheses}
    check(
        assertions,
        "exact_seven_hypotheses_are_registered",
        hypotheses == EXPECTED_HYPOTHESES and len(set(hypotheses)) == len(hypotheses) and all(registered.values()),
        {"hypotheses": hypotheses, "registered": registered},
        EXPECTED_HYPOTHESES,
    )

    lifts = contract["sub_t6_dependency_lifts"]
    check(
        assertions,
        "sub_t6_lifts_are_explicit_and_named",
        lifts == {
            "A1-PRODUCTION-KERNEL-MANIFEST": "A5-H1-CANONICAL-KERNEL-MANIFEST",
            "A1-PRODUCTION-FUNCTIONAL-REALISATION": "A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL",
        }
        and set(lifts.values()) <= set(hypotheses),
        lifts,
        "two explicit lifts into the seven-hypothesis set",
    )

    premises = contract["premises"]
    premise_tiers = {row["id"]: row["tier"] for row in premises}
    lift_ids = set(lifts)
    check(
        assertions,
        "six_premises_have_four_t6_rows_and_two_lifts",
        len(premises) == 6
        and {name for name, tier in premise_tiers.items() if tier == "T6"} == EXPECTED_T6_PREMISES
        and {name for name, tier in premise_tiers.items() if tier != "T6"} == lift_ids,
        {"premise_tiers": premise_tiers, "lifts": lifts},
        "six premises; four T6 and two lifted T5 premises",
    )

    full_chain = contract["branches"]["full_production"]["claim_chain"]
    scalar_chain = contract["branches"]["scalar_continuum"]["claim_conjunction"]
    check(
        assertions,
        "full_and_scalar_branch_topology_is_disjoint",
        full_chain == EXPECTED_FULL_CHAIN
        and scalar_chain == EXPECTED_SCALAR_CHAIN
        and not set(full_chain).intersection(scalar_chain),
        {"full_production": full_chain, "scalar_continuum": scalar_chain},
        {"full_production": EXPECTED_FULL_CHAIN, "scalar_continuum": EXPECTED_SCALAR_CHAIN},
    )

    scalar_source = resolve_repo_path(manifest["numeric_firewall"]["scalar_source"])
    full_source = resolve_repo_path(manifest["numeric_firewall"]["full_source"])
    scalar_data = load_json(scalar_source)
    full_data = load_json(full_source)
    scalar_mass = Decimal(str(scalar_data["mu2_shell"]))
    params = full_data["parameters"]
    full_mass = Decimal(str(params["r"])) - Decimal(str(params["Z"])) ** 2 / (Decimal(4) * Decimal(str(params["Y"])))
    firewall = manifest["numeric_firewall"]
    expected_scalar = Decimal(firewall["expected_scalar_shell_mass_squared"])
    expected_full = Decimal(firewall["expected_full_shell_mass_squared"])
    tolerance = Decimal(firewall["full_mass_match_tolerance"])
    separation = Decimal(firewall["required_absolute_difference_gt"])
    difference = abs(full_mass - scalar_mass)
    check(
        assertions,
        "shell_mass_fork_is_derived_and_separated",
        scalar_mass == expected_scalar and abs(full_mass - expected_full) < tolerance and difference > separation,
        {
            "scalar_mass_squared": str(scalar_mass),
            "full_mass_squared": str(full_mass),
            "absolute_difference": str(difference),
        },
        {"scalar": str(expected_scalar), "full": str(expected_full), "difference_gt": str(separation)},
    )

    exclusions = " | ".join(contract["exclusions"])
    missing_tokens = [token for token in EXPECTED_EXCLUSION_TOKENS if token.lower() not in exclusions.lower()]
    check(
        assertions,
        "exclusion_boundary_contains_no_overclaim_tokens",
        not missing_tokens,
        {"missing_tokens": missing_tokens},
        "all required exclusion tokens present",
    )

    weaknesses = manifest["sector_a_weakness_map"]
    weakness_ids = [row["id"] for row in weaknesses]
    weakness_statuses = {row["status"] for row in weaknesses}
    check(
        assertions,
        "weakness_map_separates_open_classii_and_bcc",
        len(weakness_ids) == len(set(weakness_ids))
        and weakness_statuses == {"CONTROLLED-BY-CONDITIONAL-T6", "OPEN-SEPARATE-CLAIM"}
        and "FULL-CLASSII-CONSTRUCTIVE-MEASURE" in weakness_ids
        and "BCC-EXISTENCE-AND-SELECTION" in weakness_ids,
        {"count": len(weakness_ids), "statuses": sorted(weakness_statuses)},
        "unique map with controlled/open statuses and required open rows",
    )

    status = load_json(CLAIM / "status.json")
    check(
        assertions,
        "claim_card_remains_confirmed_t6_without_open_operator_gate",
        status.get("tier") == "T6"
        and manifest["operator_gate"] not in status.get("open_gates", [])
        and status.get("hypotheses") == EXPECTED_HYPOTHESES,
        {"tier": status.get("tier"), "open_gates": status.get("open_gates"), "hypotheses": status.get("hypotheses")},
        "T6, operator gate absent, exact seven hypotheses",
    )

    # Re-run the enacted A5 package in a temporary output location.  The
    # temporary path prevents this sidecar from mutating historical run JSON.
    with tempfile.TemporaryDirectory(prefix="a5-r475-primary-") as temp:
        output = Path(temp) / "a5-primary.json"
        script = REPO / "codes" / "foundations" / "a5_t6_conditional_primary.py"
        run = subprocess.run(
            [sys.executable, str(script), "--output", str(output)],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        upstream = load_json(output) if output.is_file() else {}
        upstream_ok = run.returncode == 0 and upstream.get("verdict") == "A5-T6-CONDITIONAL-PRIMARY-PASS"
        check(
            assertions,
            "enacted_a5_primary_reexecutes_in_temp_output",
            upstream_ok,
            {"returncode": run.returncode, "verdict": upstream.get("verdict"), "summary": upstream.get("assertion_summary")},
            "A5-T6-CONDITIONAL-PRIMARY-PASS",
        )

    passed = sum(row["status"] == "PASS" for row in assertions)
    output = {
        "schema": "tect/a5-r475-lean-crosscheck-primary/1.0",
        "claim_id": __claims__[0],
        "result_id": "R-475",
        "exploration_id": "EXP-001354",
        "script_version": __version__,
        "verdict": "R475-A5-CONTRACT-PRIMARY-PASS" if passed == len(assertions) else "R475-A5-CONTRACT-PRIMARY-FAIL",
        "theorem_contract_sha256": contract_digest,
        "hypotheses": hypotheses,
        "branches": {"full_production": full_chain, "scalar_continuum": scalar_chain},
        "mass_fork": {
            "scalar_shell_mass_squared": str(scalar_mass),
            "full_shell_mass_squared": str(full_mass),
            "absolute_difference": str(difference),
        },
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "evidence_level": "T0 exact Lean/contract cross-check for the enacted A5 T6 conditional-composition boundary",
        "non_claims": [
            "No A5 analytic theorem is reproved by this sidecar.",
            "No full derivative Class-II constructive measure, BCC selection, physical closure, QFT, Yang--Mills, continuum or mass-gap result follows.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"R-475 PRIMARY: {output['verdict']} ({passed}/{len(assertions)} assertions)")
    print("Contract:", contract_digest)
    print("Evidence:", args.output.resolve())
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
