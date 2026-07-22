#!/usr/bin/env python3
"""Primary audit for the A5 branch-aware T6 conditional-composition theorem.

The audit proves only implication composition and conjunction across the two
declared Sector-A branches.  It revalidates the immutable T5 capstone, every
component record and PUBLISHED support bundle, the named-hypothesis lifts, the
mass and functional firewalls, and the exact referee-package identity.
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
__first_issued__ = "2026-07-19"
__version_issued__ = "2026-07-20"
__claims__ = ["A5-SECTOR-A-SYNTHESIS"]

getcontext().prec = 80
REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / __claims__[0]
MANIFEST = CLAIM / "conditional_composition_manifest.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-20-t6-conditional-published-primary" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def digest_from_files(files: dict[str, str]) -> str:
    payload = "\n".join(f"{value}  {name}" for name, value in sorted(files.items()))
    return hashlib.sha256(payload.encode()).hexdigest()


def check(name: str, passed: bool, detail: Any, assertions: list[dict[str, Any]]) -> None:
    assertions.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})


def verify_bundle(bundle_root: Path, expected_digest: str | None = None) -> dict[str, Any]:
    manifest_path = bundle_root / "MANIFEST.json"
    if not manifest_path.is_file():
        return {"passed": False, "reason": "MANIFEST.json missing", "root": str(bundle_root)}
    bundle = load_json(manifest_path)
    files = bundle.get("files", {})
    rows = []
    for relative, expected in files.items():
        path = bundle_root / relative
        rows.append(path.is_file() and sha256(path) == expected)
    runlog = bundle.get("runlog", {})
    runlog_ok = bool(runlog) and all(
        row.get("exit") == 0 and "FAIL" not in row.get("pass_line", "") for row in runlog.values()
    )
    readme = (bundle_root / "README.md").read_text(encoding="utf-8") if (bundle_root / "README.md").is_file() else ""
    actual_digest = digest_from_files(files)
    return {
        "passed": bool(files)
        and all(rows)
        and actual_digest == bundle.get("bundle_digest")
        and (expected_digest is None or actual_digest == expected_digest)
        and runlog_ok
        and "PUBLISHED (operator-confirmed)" in readme,
        "file_count": len(files),
        "file_hashes_ok": bool(files) and all(rows),
        "actual_digest": actual_digest,
        "recorded_digest": bundle.get("bundle_digest"),
        "expected_digest": expected_digest,
        "runlog_ok": runlog_ok,
        "published_marker_ok": "PUBLISHED (operator-confirmed)" in readme,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = load_json(MANIFEST)
    assertions: list[dict[str, Any]] = []
    authority = manifest["authority"]
    contract = manifest["theorem_contract"]

    check(
        "manifest_identity_and_candidate_boundary",
        manifest.get("schema") == "tect/a5-t6-conditional-composition/1.1"
        and manifest.get("claim_id") == __claims__[0]
        and manifest.get("candidate_tier") == "T6"
        and manifest.get("publication_state")
        in {"T6-ENACTED-OPERATOR-CONFIRMED", "T6-PUBLISHED-OPERATOR-CONFIRMED"},
        {
            "schema": manifest.get("schema"),
            "candidate_tier": manifest.get("candidate_tier"),
            "publication_state": manifest.get("publication_state"),
        },
        assertions,
    )
    contract_actual = canonical_digest(contract)
    check(
        "canonical_theorem_contract_digest",
        contract_actual == manifest.get("theorem_contract_sha256"),
        {"actual": contract_actual, "expected": manifest.get("theorem_contract_sha256")},
        assertions,
    )
    confirmation = manifest.get("operator_confirmation", {})
    candidate_source = REPO / confirmation.get("candidate_source", "__missing__")
    candidate_pdf = REPO / confirmation.get("candidate_pdf", "__missing__")
    check(
        "exact_v1_0_operator_confirmation_is_bound_to_candidate_hashes",
        confirmation.get("status") == "CONFIRMED"
        and confirmation.get("confirmed_by") == "Jusang Lee"
        and confirmation.get("confirmed_on") == "2026-07-20"
        and confirmation.get("candidate_commit") == "fb776bff6b161178a6328570af3ef9529b44a2df"
        and candidate_source.is_file()
        and candidate_pdf.is_file()
        and sha256(candidate_source) == confirmation.get("candidate_source_sha256")
        and sha256(candidate_pdf) == confirmation.get("candidate_pdf_sha256")
        and confirmation.get("published_bundle_authorized") is True,
        confirmation,
        assertions,
    )

    source_rows = []
    for key in ("primary_audit", "independent_audit", "one_command_verifier"):
        row = authority[key]
        path = REPO / row["path"]
        source_rows.append(
            {"id": key, "exists": path.is_file(), "actual": sha256(path) if path.is_file() else None, "expected": row["sha256"]}
        )
    check(
        "all_three_audit_sources_are_hash_pinned",
        all(row["exists"] and row["actual"] == row["expected"] for row in source_rows),
        source_rows,
        assertions,
    )

    note_rows = []
    for key in ("referee_source", "referee_pdf"):
        row = authority[key]
        path = REPO / row["path"]
        note_rows.append(
            {"id": key, "exists": path.is_file(), "actual": sha256(path) if path.is_file() else None, "expected": row["sha256"]}
        )
    check(
        "exact_referee_package_source_and_pdf_are_hash_pinned",
        all(row["exists"] and row["actual"] == row["expected"] for row in note_rows),
        note_rows,
        assertions,
    )

    baseline = manifest["immutable_t5_baseline"]
    t5_manifest_path = REPO / baseline["synthesis_manifest_path"]
    t5_bundle_root = REPO / baseline["bundle_path"]
    t5_bundle_manifest = t5_bundle_root / "MANIFEST.json"
    check(
        "immutable_t5_manifest_and_bundle_manifest_are_unchanged",
        sha256(t5_manifest_path) == baseline["synthesis_manifest_sha256"]
        and sha256(t5_bundle_manifest) == baseline["bundle_manifest_sha256"],
        {
            "synthesis_manifest_actual": sha256(t5_manifest_path),
            "synthesis_manifest_expected": baseline["synthesis_manifest_sha256"],
            "bundle_manifest_actual": sha256(t5_bundle_manifest),
            "bundle_manifest_expected": baseline["bundle_manifest_sha256"],
        },
        assertions,
    )
    t5_bundle_report = verify_bundle(t5_bundle_root, baseline["bundle_digest"])
    check(
        "immutable_t5_capstone_reconstructs_all_files_and_digest",
        t5_bundle_report["passed"] and t5_bundle_report["file_count"] == baseline["bundle_file_count"],
        t5_bundle_report,
        assertions,
    )

    t5_manifest = load_json(t5_manifest_path)
    cards: dict[str, dict[str, Any]] = {}
    component_rows = []
    support_bundle_rows = []
    for component in t5_manifest["components"]:
        status_path = REPO / component["status_path"]
        card = load_json(status_path)
        cards[component["id"]] = card
        component_rows.append(
            {
                "id": component["id"],
                "hash_ok": sha256(status_path) == component["status_sha256"],
                "tier_ok": card.get("tier") == component["expected_tier"],
                "active": card.get("lifecycle") == "ACTIVE",
                "reproducible": card.get("reproduction", {}).get("status") == "AVAILABLE",
            }
        )
        bundle_manifest_path = REPO / component["published_bundle_manifest"]
        bundle_root = bundle_manifest_path.parent
        support_report = verify_bundle(bundle_root)
        support_bundle_rows.append(
            {
                "id": component["id"],
                "manifest_hash_ok": sha256(bundle_manifest_path) == component["published_bundle_manifest_sha256"],
                **support_report,
            }
        )
    check(
        "all_six_component_cards_remain_exact_active_and_reproducible",
        len(component_rows) == 6
        and all(all(value is True for key, value in row.items() if key != "id") for row in component_rows),
        component_rows,
        assertions,
    )
    check(
        "all_six_support_bundles_reconstruct_as_published",
        len(support_bundle_rows) == 6
        and all(row["manifest_hash_ok"] and row["passed"] for row in support_bundle_rows),
        support_bundle_rows,
        assertions,
    )

    exact_hypotheses = contract["named_hypotheses"]
    gates_text = (REPO / "claims" / "GATES.md").read_text(encoding="utf-8")
    hypothesis_rows = [{"id": item, "registered": f"### **{item}**" in gates_text} for item in exact_hypotheses]
    check(
        "seven_named_hypotheses_are_exact_and_registered",
        len(exact_hypotheses) == 7
        and len(set(exact_hypotheses)) == 7
        and all(row["registered"] for row in hypothesis_rows),
        hypothesis_rows,
        assertions,
    )
    expected_lifts = {
        "A1-PRODUCTION-KERNEL-MANIFEST": "A5-H1-CANONICAL-KERNEL-MANIFEST",
        "A1-PRODUCTION-FUNCTIONAL-REALISATION": "A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL",
    }
    check(
        "both_sub_t6_dependencies_are_explicitly_lifted",
        contract["sub_t6_dependency_lifts"] == expected_lifts
        and all(item in exact_hypotheses for item in expected_lifts.values()),
        contract["sub_t6_dependency_lifts"],
        assertions,
    )
    premise_rows = []
    for premise in contract["premises"]:
        card = cards[premise["id"]]
        premise_rows.append(
            {
                "id": premise["id"],
                "actual_tier": card.get("tier"),
                "expected_tier": premise["tier"],
                "lift": premise.get("lift"),
                "tier_ok": card.get("tier") == premise["tier"],
                "lift_ok": premise["tier"] == "T6" or premise.get("lift") in exact_hypotheses,
            }
        )
    check(
        "premise_tiers_and_tier_monotonicity_repairs_are_complete",
        len(premise_rows) == 6 and all(row["tier_ok"] and row["lift_ok"] for row in premise_rows),
        premise_rows,
        assertions,
    )

    full_ids = contract["branches"]["full_production"]["claim_chain"]
    scalar_ids = contract["branches"]["scalar_continuum"]["claim_conjunction"]
    p2, p3 = cards[full_ids[1]], cards[full_ids[2]]
    check(
        "full_production_implication_chain_is_a_valid_dag_path",
        full_ids == [
            "A1-PRODUCTION-FUNCTIONAL-REALISATION",
            "A2-FULL-PRODUCTION-WELLPOSED",
            "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM",
        ]
        and full_ids[0] in p2.get("dependencies", [])
        and full_ids[0] in p3.get("dependencies", [])
        and full_ids[1] in p3.get("dependencies", []),
        {"chain": full_ids, "A2_dependencies": p2.get("dependencies"), "A3_dependencies": p3.get("dependencies")},
        assertions,
    )
    check(
        "scalar_results_are_a_parallel_conjunction_not_a_cross_proof",
        scalar_ids == [
            "A3-PERTURBATIVE-CONTINUUM-CORRELATORS",
            "A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE",
        ]
        and scalar_ids[0] not in cards[scalar_ids[1]].get("dependencies", [])
        and scalar_ids[1] not in cards[scalar_ids[0]].get("dependencies", [])
        and not set(full_ids).intersection(scalar_ids),
        {
            "conjunction": scalar_ids,
            "A3_scalar_dependencies": cards[scalar_ids[0]].get("dependencies"),
            "A4_dependencies": cards[scalar_ids[1]].get("dependencies"),
        },
        assertions,
    )

    kernel = load_json(REPO / manifest["numeric_firewall"]["scalar_source"])
    functional = load_json(REPO / manifest["numeric_firewall"]["full_source"])
    a4_manifest = load_json(REPO / manifest["shared_domain"]["a4_manifest"])
    params = functional["parameters"]
    geometry = manifest["shared_domain"]
    q0_ok = Decimal(str(kernel["q0"])) == Decimal(str(params["q0"]))
    y_ok = Decimal(str(kernel["Y"])) == Decimal(str(params["Y"]))
    z_delta = abs(Decimal(str(kernel["Z"])) - Decimal(str(params["Z"])))
    periods = [Decimal(str(params[key])) for key in ("Lx", "Ly", "Lz")]
    check(
        "shared_domain_compatibility_does_not_assert_state_or_parameter_identity",
        q0_ok
        and y_ok
        and z_delta < Decimal(geometry["kernel_parameter_tolerance"])
        and periods == [Decimal(value) for value in geometry["periods"]]
        and Decimal(str(kernel["eta_shell"])) == 0
        and Decimal(str(params["eta_shell"])) == 0
        and "Lx=Ly=Lz=16" in a4_manifest["theorem_scope"]["domain"],
        {"q0_ok": q0_ok, "Y_ok": y_ok, "Z_delta": str(z_delta), "periods": [str(value) for value in periods]},
        assertions,
    )

    scalar_mass = Decimal(str(kernel["mu2_shell"]))
    full_mass = Decimal(str(params["r"])) - Decimal(str(params["Z"])) ** 2 / (Decimal(4) * Decimal(str(params["Y"])))
    mass_difference = abs(full_mass - scalar_mass)
    firewall = manifest["numeric_firewall"]
    check(
        "shell_mass_fork_is_independently_rederived_and_separated",
        scalar_mass == Decimal(firewall["expected_scalar_shell_mass_squared"])
        and abs(full_mass - Decimal(firewall["expected_full_shell_mass_squared"]))
        < Decimal(firewall["full_mass_match_tolerance"])
        and mass_difference > Decimal(firewall["required_absolute_difference_gt"]),
        {
            "scalar_mass_squared": str(scalar_mass),
            "full_mass_squared": str(full_mass),
            "absolute_difference": str(mass_difference),
        },
        assertions,
    )
    local_error = Decimal(str(functional["verified_result"]["maxima"]["scalar_reduction_rel_error"]))
    check(
        "local_scalar_reduction_is_accurate_but_not_measure_equivalence",
        local_error < Decimal(firewall["local_reduction_required_rel_error_lt"])
        and "does not imply" in contract["non_implications"][1]
        and "Class-II" in contract["non_implications"][1],
        {"relative_error": str(local_error), "firewall": contract["non_implications"][1]},
        assertions,
    )

    full_conclusions = contract["branches"]["full_production"]["conclusions"]
    scalar_conclusions = contract["branches"]["scalar_continuum"]["conclusions"]
    check(
        "conclusion_maps_are_nonempty_branch_local_and_scope_limited",
        len(full_conclusions) == 5
        and len(scalar_conclusions) == 4
        and all("Class-II measure" not in item for item in full_conclusions + scalar_conclusions)
        and all("BCC" not in item for item in full_conclusions + scalar_conclusions),
        {"full": full_conclusions, "scalar": scalar_conclusions},
        assertions,
    )
    boundary = " | ".join(contract["exclusions"]).lower()
    required_tokens = [
        "parameter-identical",
        "derivative class-ii",
        "eta_shell",
        "t=0",
        "historical",
        "route-b",
        "unsmeared",
        "infinite-volume",
        "phase transition",
        "bcc",
        "sector-b",
        "t7",
    ]
    check(
        "honesty_boundary_contains_every_required_non_implication",
        all(token in boundary for token in required_tokens),
        {"required_tokens": required_tokens, "exclusions": contract["exclusions"]},
        assertions,
    )

    weaknesses = manifest["sector_a_weakness_map"]
    closed = [row for row in weaknesses if row["status"] == "CONTROLLED-BY-CONDITIONAL-T6"]
    open_rows = [row for row in weaknesses if row["status"] == "OPEN-SEPARATE-CLAIM"]
    check(
        "sector_a_weakness_map_separates_controlled_interfaces_from_open_physics",
        len(closed) >= 5
        and len(open_rows) >= 6
        and any(row["id"] == "FULL-CLASSII-CONSTRUCTIVE-MEASURE" for row in open_rows)
        and any(row["id"] == "BCC-EXISTENCE-AND-SELECTION" for row in open_rows),
        weaknesses,
        assertions,
    )

    status = load_json(CLAIM / "status.json")
    gate = manifest["operator_gate"]
    candidate_state = status.get("tier") == "T5" and gate in status.get("open_gates", [])
    published_state = status.get("tier") == "T6" and gate not in status.get("open_gates", [])
    check(
        "claim_state_is_either_review_candidate_or_confirmed_t6",
        candidate_state or published_state,
        {"tier": status.get("tier"), "open_gates": status.get("open_gates"), "candidate": candidate_state, "published": published_state},
        assertions,
    )
    check(
        "claim_card_lists_all_seven_theorem_hypotheses",
        status.get("hypotheses") == exact_hypotheses,
        {"actual": status.get("hypotheses"), "expected": exact_hypotheses},
        assertions,
    )

    passed = sum(row["status"] == "PASS" for row in assertions)
    verdict = "A5-T6-CONDITIONAL-PRIMARY-PASS" if passed == len(assertions) else "A5-T6-CONDITIONAL-PRIMARY-FAIL"
    output = {
        "schema": "tect/a5-t6-conditional-primary-result/1.0",
        "claim_id": __claims__[0],
        "script_version": __version__,
        "verdict": verdict,
        "candidate_result": manifest["candidate_result"],
        "theorem_contract_sha256": contract_actual,
        "hypotheses": exact_hypotheses,
        "branches": {"full_production": full_ids, "scalar_continuum": scalar_ids},
        "mass_fork": {
            "scalar_shell_mass_squared": str(scalar_mass),
            "full_shell_mass_squared": str(full_mass),
            "absolute_difference": str(mass_difference),
        },
        "immutable_t5_bundle_digest": t5_bundle_report["actual_digest"],
        "component_rows": component_rows,
        "support_bundle_rows": support_bundle_rows,
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "promotion_boundary": "Exact v1.0 is operator-confirmed. T6 publication completeness additionally requires the bundle-last PUBLISHED package and final integrity gate.",
        "not_closed_here": contract["exclusions"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(assertions)} PASS")
    print(verdict)
    print("Contract:", contract_actual)
    print("Evidence:", args.output.resolve())
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
