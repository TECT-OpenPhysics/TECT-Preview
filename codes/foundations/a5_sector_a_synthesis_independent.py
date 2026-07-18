#!/usr/bin/env python3
"""Non-importing adversarial audit for the branch-aware Sector-A synthesis.

This implementation does not import the primary A5 audit.  It reconstructs
the dependency graph, parameter fork, component and support-bundle hashes,
and the two scalar-continuum evidence totals directly from frozen records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any

__version__ = "1.1.0"
__first_issued__ = "2026-07-18"
__version_issued__ = "2026-07-19"
__claims__ = ["A5-SECTOR-A-SYNTHESIS"]

getcontext().prec = 80
REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / __claims__[0]
MANIFEST = CLAIM / "sector_a_synthesis_manifest.json"
DEFAULT_PRIMARY = CLAIM / "runs" / "2026-07-19-t5-primary-preflight" / "result.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-19-t5-independent-preflight" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check(name: str, passed: bool, detail: Any, assertions: list[dict[str, Any]]) -> None:
    assertions.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})


def digest_from_files(bundle: dict[str, Any]) -> str:
    payload = "\n".join(f"{value}  {name}" for name, value in sorted(bundle["files"].items()))
    return hashlib.sha256(payload.encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary-result", type=Path, default=DEFAULT_PRIMARY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = load_json(MANIFEST)
    authority = manifest["authority"]
    assertions: list[dict[str, Any]] = []

    check(
        "independent_source_hash_matches_manifest",
        sha256(Path(__file__)) == authority["independent_audit"]["sha256"],
        {"actual": sha256(Path(__file__)), "expected": authority["independent_audit"]["sha256"]},
        assertions,
    )
    primary_source = REPO / authority["primary_audit"]["path"]
    primary = load_json(args.primary_result)
    primary_summary = primary.get("assertion_summary", {})
    check(
        "fresh_primary_record_and_source_are_complete",
        sha256(primary_source) == authority["primary_audit"]["sha256"]
        and primary.get("verdict") == "A5-SECTOR-A-SYNTHESIS-PRIMARY-PASS"
        and int(primary_summary.get("total", 0)) > 0
        and int(primary_summary.get("passed", -1)) == int(primary_summary.get("total", 0)),
        {"source_sha256": sha256(primary_source), "verdict": primary.get("verdict"), "summary": primary_summary},
        assertions,
    )
    check(
        "manifest_records_confirmed_t5_with_deferred_capstone_packaging",
        manifest.get("schema") == "tect/a5-sector-a-synthesis/1.1"
        and manifest.get("source_commit") == "77c2431"
        and "T5 CLOSED@BRANCH-AWARE-SECTOR-A-SYNTHESIS" in manifest.get("status", "")
        and manifest["review_gate"]["status"] == "CLOSED"
        and manifest["publication_prerequisites"][0]["status"] == "PENDING-OPERATOR-CONFIRMATION",
        {"schema": manifest.get("schema"), "status": manifest.get("status"), "gate": manifest["review_gate"]},
        assertions,
    )

    cards: dict[str, dict[str, Any]] = {}
    record_rows = []
    for component in manifest["components"]:
        status_path = REPO / component["status_path"]
        card = load_json(status_path)
        cards[component["id"]] = card
        row = {
            "id": component["id"],
            "status_hash_ok": sha256(status_path) == component["status_sha256"],
            "tier_ok": card.get("tier") == component["expected_tier"],
            "active": card.get("lifecycle") == "ACTIVE",
            "no_open_gates": not card.get("open_gates"),
            "reproducible": card.get("reproduction", {}).get("status") == "AVAILABLE",
        }
        if "manifest_path" in component:
            row["manifest_hash_ok"] = sha256(REPO / component["manifest_path"]) == component["manifest_sha256"]
        if "evidence_path" in component:
            row["evidence_hash_ok"] = sha256(REPO / component["evidence_path"]) == component["evidence_sha256"]
        record_rows.append(row)
    check(
        "all_six_component_records_are_current_and_closed_in_scope",
        len(record_rows) == 6 and all(all(value is True for key, value in row.items() if key != "id") for row in record_rows),
        record_rows,
        assertions,
    )

    expected_full = [
        "A1-PRODUCTION-FUNCTIONAL-REALISATION",
        "A2-FULL-PRODUCTION-WELLPOSED",
        "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM",
    ]
    expected_scalar = [
        "A3-PERTURBATIVE-CONTINUUM-CORRELATORS",
        "A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE",
    ]
    check(
        "branch_membership_is_exact_and_disjoint",
        manifest["branch_map"]["full_production"] == expected_full
        and manifest["branch_map"]["scalar_continuum"] == expected_scalar
        and not set(expected_full).intersection(expected_scalar),
        {"full_production": manifest["branch_map"]["full_production"], "scalar_continuum": manifest["branch_map"]["scalar_continuum"]},
        assertions,
    )
    p2 = cards[expected_full[1]]
    p3 = cards[expected_full[2]]
    check(
        "full_production_dependency_dag_is_reconstructed",
        expected_full[0] in p2.get("dependencies", [])
        and expected_full[0] in p3.get("dependencies", [])
        and expected_full[1] in p3.get("dependencies", [])
        and expected_scalar[1] not in p3.get("dependencies", [])
        and "No arrow from full-production P3" in manifest["interface_contracts"][-1],
        {"P2_dependencies": p2.get("dependencies"), "P3_dependencies": p3.get("dependencies")},
        assertions,
    )
    scalar_scopes = {name: cards[name].get("scope", "") for name in expected_scalar}
    check(
        "scalar_continuum_claims_are_scalar_spectral_not_full_classii",
        all("scalar" in scope.lower() and "spectral" in scope.lower() for scope in scalar_scopes.values())
        and all(
            any(
                token in cards[name].get("no_overclaim", "").lower()
                for token in ("full class-ii", "full three-component", "derivative class-ii")
            )
            for name in expected_scalar
        ),
        scalar_scopes,
        assertions,
    )

    kernel = load_json(REPO / "claims/A1-PRODUCTION-KERNEL-MANIFEST/canonical_n001_kernel.json")
    functional = load_json(REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json")
    a4_manifest = load_json(REPO / "claims/A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE/constructive_measure_manifest.json")
    params = functional["parameters"]
    q0_match = Decimal(str(kernel["q0"])) == Decimal(str(params["q0"]))
    y_match = Decimal(str(kernel["Y"])) == Decimal(str(params["Y"]))
    z_difference = abs(Decimal(str(kernel["Z"])) - Decimal(str(params["Z"])))
    check(
        "shared_geometry_is_verified_on_both_branches",
        q0_match
        and y_match
        and z_difference < Decimal("1e-9")
        and Decimal(str(kernel["eta_shell"])) == 0
        and Decimal(str(params["eta_shell"])) == 0
        and [Decimal(str(params[name])) for name in ("Lx", "Ly", "Lz")] == [Decimal(16)] * 3
        and "Lx=Ly=Lz=16" in a4_manifest["theorem_scope"]["domain"],
        {"q0_match": q0_match, "Y_match": y_match, "Z_difference": str(z_difference), "A4_domain": a4_manifest["theorem_scope"]["domain"]},
        assertions,
    )

    scalar_mass = Decimal(str(kernel["mu2_shell"]))
    r_value = Decimal(str(params["r"]))
    z_value = Decimal(str(params["Z"]))
    y_value = Decimal(str(params["Y"]))
    full_mass = r_value - z_value * z_value / (Decimal(4) * y_value)
    mass_fork = manifest["branch_map"]["mass_fork"]
    check(
        "mass_fork_is_rederived_with_decimal_arithmetic",
        scalar_mass == Decimal(str(mass_fork["scalar_perturbative_shell_mass_squared"]))
        and abs(full_mass - Decimal(str(mass_fork["full_production_shell_mass_squared"]))) < Decimal("1e-9")
        and abs(full_mass - scalar_mass) > Decimal("0.2")
        and "Equality is forbidden" in mass_fork["rule"],
        {"scalar_mass_squared": str(scalar_mass), "full_mass_squared": str(full_mass), "difference": str(full_mass - scalar_mass)},
        assertions,
    )
    local_error = Decimal(str(functional["verified_result"]["maxima"]["scalar_reduction_rel_error"]))
    functional_rule = manifest["branch_map"]["functional_fork"]["rule"]
    check(
        "local_scalar_reduction_does_not_imply_measure_equivalence",
        local_error < Decimal("1e-12")
        and Decimal(str(params["gamma"])) > 0
        and "not a full three-component Class-II constructive measure" in functional_rule,
        {"scalar_reduction_relative_error": str(local_error), "rule": functional_rule},
        assertions,
    )

    a3_result = load_json(REPO / next(row["evidence_path"] for row in manifest["components"] if row["id"] == expected_scalar[0]))
    a4_result = load_json(REPO / next(row["evidence_path"] for row in manifest["components"] if row["id"] == expected_scalar[1]))
    check(
        "scalar_continuum_evidence_totals_are_reconstructed",
        a3_result.get("all_pass") is True
        and len(a3_result.get("claims", [])) == 8
        and all(row.get("passed") is True for row in a3_result.get("claims", []))
        and a4_result.get("verdict") == "A4-SCALAR-CONSTRUCTIVE-INTEGRATED-PASS"
        and a4_result.get("assertion_summary") == {"passed": 31, "total": 31}
        and not a4_result.get("failures"),
        {"A3": {"all_pass": a3_result.get("all_pass"), "count": len(a3_result.get("claims", []))}, "A4": a4_result.get("assertion_summary")},
        assertions,
    )

    bundle_rows = []
    for component in manifest["components"]:
        if "published_bundle_manifest" not in component:
            continue
        bundle_path = REPO / component["published_bundle_manifest"]
        bundle = load_json(bundle_path)
        runlog = bundle.get("runlog", {})
        bundle_rows.append(
            {
                "id": component["id"],
                "manifest_hash_ok": sha256(bundle_path) == component["published_bundle_manifest_sha256"],
                "digest_ok": digest_from_files(bundle) == bundle.get("bundle_digest"),
                "runlog_ok": bool(runlog) and all(row.get("exit") == 0 and "FAIL" not in row.get("pass_line", "") for row in runlog.values()),
            }
        )
    check(
        "all_five_available_support_bundle_attestations_are_valid",
        len(bundle_rows) == 5 and all(all(value is True for key, value in row.items() if key != "id") for row in bundle_rows),
        bundle_rows,
        assertions,
    )

    gates = (REPO / "claims/GATES.md").read_text(encoding="utf-8")
    hypothesis_rows = [{"id": name, "registered": f"### **{name}**" in gates} for name in manifest["named_hypotheses"]]
    check("named_hypotheses_are_registered", all(row["registered"] for row in hypothesis_rows), hypothesis_rows, assertions)

    boundary = " | ".join(manifest["honesty_boundary"]).lower()
    required_boundary = ["historical", "full three-component", "0.005 and 0.26", "eta_shell", "t=0", "route b", "infinite volume", "bcc", "sector b", "t7"]
    check(
        "termination_firewall_has_all_required_exclusions",
        all(token in boundary for token in required_boundary),
        {"required": required_boundary, "boundary": manifest["honesty_boundary"]},
        assertions,
    )
    verdict_record = manifest["termination_verdict"]
    check(
        "branch_aware_termination_is_not_parameter_identical_physical_closure",
        verdict_record["result"] == "PASS@BRANCH-AWARE-DECLARED-SCOPE"
        and "separate scalar" in verdict_record["meaning"]
        and "parameter-identical" in verdict_record["not_meaning"]
        and "BCC" in verdict_record["not_meaning"],
        verdict_record,
        assertions,
    )
    a4_component = next(row for row in manifest["components"] if row["id"] == "A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE")
    a4_preflight_ok = (
        sha256(REPO / a4_component["publication_preflight_path"]) == a4_component["publication_preflight_sha256"]
        and sha256(REPO / a4_component["referee_package_candidate"]) == a4_component["referee_package_candidate_sha256"]
    )
    check(
        "operator_confirmation_is_recorded_and_a4_bundle_precedes_capstone_publication",
        manifest["review_gate"]["id"] == "A5-SECTOR-A-SYNTHESIS-OPERATOR-CONFIRMATION"
        and manifest["review_gate"]["status"] == "CLOSED"
        and manifest["review_gate"]["confirmed_on"] == "2026-07-19"
        and manifest["publication_prerequisites"][0]["claim_id"] == "A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE"
        and manifest["publication_prerequisites"][0]["status"] == "PENDING-OPERATOR-CONFIRMATION"
        and a4_preflight_ok,
        {"review_gate": manifest["review_gate"], "publication_prerequisites": manifest["publication_prerequisites"], "a4_candidate_hashes_ok": a4_preflight_ok},
        assertions,
    )

    passed = sum(row["status"] == "PASS" for row in assertions)
    verdict = "A5-SECTOR-A-SYNTHESIS-INDEPENDENT-PASS" if passed == len(assertions) else "A5-SECTOR-A-SYNTHESIS-INDEPENDENT-FAIL"
    output = {
        "schema": "tect/a5-sector-a-synthesis-independent-result/1.0",
        "claim_id": __claims__[0],
        "script_version": __version__,
        "verdict": verdict,
        "branch_map": {"full_production": expected_full, "scalar_continuum": expected_scalar},
        "mass_fork": {"scalar_mass_squared": str(scalar_mass), "full_mass_squared": str(full_mass)},
        "record_rows": record_rows,
        "bundle_rows": bundle_rows,
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "honesty_boundary": manifest["honesty_boundary"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(assertions)} PASS")
    print(verdict)
    print("Termination:", manifest["termination_verdict"]["result"])
    print("Evidence:", args.output.resolve())
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
