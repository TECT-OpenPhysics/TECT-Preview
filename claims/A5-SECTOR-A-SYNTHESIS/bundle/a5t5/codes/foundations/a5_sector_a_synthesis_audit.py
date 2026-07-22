#!/usr/bin/env python3
"""Primary branch-aware audit for the Sector-A synthesis package.

The audit verifies the frozen P1-P4 claim cards, evidence, published support
bundle attestations, dependency interfaces, parameter compatibility, and the
two non-implication firewalls.  It does not rerun the component theorems; their
own reproduction commands and published bundle digests remain authoritative.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from pathlib import Path
from typing import Any

__version__ = "1.2.0"
__first_issued__ = "2026-07-18"
__version_issued__ = "2026-07-19"
__claims__ = ["A5-SECTOR-A-SYNTHESIS"]

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / __claims__[0]
MANIFEST = CLAIM / "sector_a_synthesis_manifest.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-19-t5-capstone-primary-preflight" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check(name: str, passed: bool, detail: Any, assertions: list[dict[str, Any]]) -> None:
    assertions.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})


def bundle_digest(bundle_manifest: dict[str, Any]) -> str:
    payload = "\n".join(f"{value}  {name}" for name, value in sorted(bundle_manifest["files"].items()))
    return hashlib.sha256(payload.encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = load_json(MANIFEST)
    authority = manifest["authority"]
    assertions: list[dict[str, Any]] = []

    check(
        "primary_source_hash_matches_manifest",
        sha256(Path(__file__)) == authority["primary_audit"]["sha256"],
        {"actual": sha256(Path(__file__)), "expected": authority["primary_audit"]["sha256"]},
        assertions,
    )
    check(
        "manifest_schema_and_review_gate_are_frozen",
        manifest.get("schema") == "tect/a5-sector-a-synthesis/1.2"
        and manifest.get("claim_id") == __claims__[0]
        and manifest["review_gate"]["id"] == "A5-SECTOR-A-SYNTHESIS-OPERATOR-CONFIRMATION"
        and manifest["review_gate"]["status"] == "CLOSED"
        and manifest["capstone_publication_review"]["status"] == "CLOSED-BATCH-AUTHORIZATION",
        {
            "schema": manifest.get("schema"),
            "review_gate": manifest.get("review_gate"),
            "capstone_publication_review": manifest.get("capstone_publication_review"),
        },
        assertions,
    )

    cards: dict[str, dict[str, Any]] = {}
    component_hash_rows = []
    component_status_rows = []
    bundle_rows = []
    evidence_rows = []
    for component in manifest["components"]:
        status_path = REPO / component["status_path"]
        status = load_json(status_path)
        cards[component["id"]] = status
        status_hash_ok = sha256(status_path) == component["status_sha256"]
        manifest_hash_ok = True
        if "manifest_path" in component:
            manifest_path = REPO / component["manifest_path"]
            manifest_hash_ok = sha256(manifest_path) == component["manifest_sha256"]
        evidence_hash_ok = True
        if "evidence_path" in component:
            evidence_path = REPO / component["evidence_path"]
            evidence_hash_ok = sha256(evidence_path) == component["evidence_sha256"]
            evidence_rows.append({"id": component["id"], "path": component["evidence_path"], "hash_ok": evidence_hash_ok})
        component_hash_rows.append(
            {
                "id": component["id"],
                "status_hash_ok": status_hash_ok,
                "manifest_hash_ok": manifest_hash_ok,
                "evidence_hash_ok": evidence_hash_ok,
            }
        )
        component_status_rows.append(
            {
                "id": component["id"],
                "tier": status.get("tier"),
                "expected_tier": component["expected_tier"],
                "lifecycle": status.get("lifecycle"),
                "open_gates": status.get("open_gates"),
                "reproduction": status.get("reproduction", {}).get("status"),
            }
        )
        if "published_bundle_manifest" in component:
            bundle_path = REPO / component["published_bundle_manifest"]
            bundle = load_json(bundle_path)
            manifest_hash_ok = sha256(bundle_path) == component["published_bundle_manifest_sha256"]
            digest_ok = bundle_digest(bundle) == bundle.get("bundle_digest")
            files_present = all((bundle_path.parent / name).is_file() for name in bundle.get("files", {}))
            files_hash_ok = files_present and all(
                sha256(bundle_path.parent / name) == expected for name, expected in bundle.get("files", {}).items()
            )
            readme_path = bundle_path.parent / "README.md"
            published_marker = readme_path.exists() and "PUBLISHED (operator-confirmed)" in readme_path.read_text(encoding="utf-8")
            runlog_ok = bool(bundle.get("runlog")) and all(
                row.get("exit") == 0 and "FAIL" not in row.get("pass_line", "") for row in bundle["runlog"].values()
            )
            bundle_rows.append(
                {
                    "id": component["id"],
                    "manifest_hash_ok": manifest_hash_ok,
                    "bundle_digest_ok": digest_ok,
                    "files_present": files_present,
                    "files_hash_ok": files_hash_ok,
                    "published_marker": published_marker,
                    "runlog_ok": runlog_ok,
                    "bundle_digest": bundle.get("bundle_digest"),
                }
            )

    check(
        "all_component_cards_manifests_and_evidence_are_hash_pinned",
        all(all(row[key] for key in ("status_hash_ok", "manifest_hash_ok", "evidence_hash_ok")) for row in component_hash_rows),
        component_hash_rows,
        assertions,
    )
    check(
        "component_tiers_lifecycles_gates_and_reproduction_match",
        len(bundle_rows) == 6
        and all(
            row["tier"] == row["expected_tier"]
            and row["lifecycle"] == "ACTIVE"
            and not row["open_gates"]
            and row["reproduction"] == "AVAILABLE"
            for row in component_status_rows
        ),
        component_status_rows,
        assertions,
    )
    check(
        "published_support_bundle_attestations_are_current",
        all(
            row["manifest_hash_ok"]
            and row["bundle_digest_ok"]
            and row["files_present"]
            and row["files_hash_ok"]
            and row["published_marker"]
            and row["runlog_ok"]
            for row in bundle_rows
        ),
        bundle_rows,
        assertions,
    )

    gates_text = (REPO / "claims" / "GATES.md").read_text(encoding="utf-8")
    hypothesis_rows = [
        {"hypothesis": name, "registered": f"### **{name}**" in gates_text}
        for name in manifest["named_hypotheses"]
    ]
    check("all_named_hypotheses_are_registered", all(row["registered"] for row in hypothesis_rows), hypothesis_rows, assertions)

    p1 = cards["A1-PRODUCTION-FUNCTIONAL-REALISATION"]
    p2 = cards["A2-FULL-PRODUCTION-WELLPOSED"]
    p3 = cards["A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"]
    pert = cards["A3-PERTURBATIVE-CONTINUUM-CORRELATORS"]
    constructive = cards["A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE"]
    check(
        "full_production_dependency_chain_is_explicit",
        "A1-PRODUCTION-FUNCTIONAL-REALISATION" in p2["dependencies"]
        and "A1-PRODUCTION-FUNCTIONAL-REALISATION" in p3["dependencies"]
        and "A2-FULL-PRODUCTION-WELLPOSED" in p3["dependencies"]
        and "A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL" in p2["hypotheses"]
        and "A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL" in p3["hypotheses"],
        {"P1": p1["id"], "P2_dependencies": p2["dependencies"], "P3_dependencies": p3["dependencies"]},
        assertions,
    )
    check(
        "scalar_continuum_branch_is_explicit_and_spectral",
        "scalar" in pert["scope"].lower()
        and "spectral" in pert["scope"].lower()
        and "scalar" in constructive["scope"].lower()
        and "spectral" in constructive["scope"].lower(),
        {"perturbative_scope": pert["scope"], "constructive_scope": constructive["scope"]},
        assertions,
    )

    kernel = load_json(REPO / "claims/a1k/canonical_n001_kernel.json")
    functional = load_json(REPO / "claims/a1f/production_functional_manifest.json")
    a4_manifest = load_json(REPO / "claims/a4/constructive_measure_manifest.json")
    params = functional["parameters"]
    shared = {
        "q0": [float(kernel["q0"]), float(params["q0"])],
        "Y": [float(kernel["Y"]), float(params["Y"])],
        "Z": [float(kernel["Z"]), float(params["Z"])],
        "eta_shell": [float(kernel["eta_shell"]), float(params["eta_shell"])],
        "periods": [float(params[name]) for name in ("Lx", "Ly", "Lz")],
    }
    check(
        "shared_fourier_and_shell_geometry_parameters_match",
        math.isclose(shared["q0"][0], shared["q0"][1], rel_tol=0.0, abs_tol=1.0e-12)
        and math.isclose(shared["Y"][0], shared["Y"][1], rel_tol=0.0, abs_tol=1.0e-14)
        and math.isclose(shared["Z"][0], shared["Z"][1], rel_tol=0.0, abs_tol=1.0e-10)
        and shared["eta_shell"] == [0.0, 0.0]
        and shared["periods"] == [16.0, 16.0, 16.0]
        and "Lx=Ly=Lz=16" in a4_manifest["theorem_scope"]["domain"],
        {**shared, "scalar_continuum_domain": a4_manifest["theorem_scope"]["domain"]},
        assertions,
    )

    scalar_mass2 = float(kernel["mu2_shell"])
    full_mass2 = float(params["r"]) - float(params["Z"]) ** 2 / (4.0 * float(params["Y"]))
    fork = manifest["branch_map"]["mass_fork"]
    check(
        "shell_mass_fork_is_reconstructed_and_not_erased",
        math.isclose(scalar_mass2, float(fork["scalar_perturbative_shell_mass_squared"]), rel_tol=0.0, abs_tol=1.0e-15)
        and math.isclose(full_mass2, float(fork["full_production_shell_mass_squared"]), rel_tol=0.0, abs_tol=2.0e-10)
        and abs(full_mass2 - scalar_mass2) > 0.2
        and "Equality is forbidden" in fork["rule"],
        {"scalar_mass_squared": scalar_mass2, "full_mass_squared": full_mass2, "difference": full_mass2 - scalar_mass2},
        assertions,
    )
    scalar_reduction_error = float(functional["verified_result"]["maxima"]["scalar_reduction_rel_error"])
    check(
        "full_functional_has_verified_scalar_local_reduction_but_not_measure_equivalence",
        scalar_reduction_error < 1.0e-12
        and float(params["gamma"]) > 0.0
        and "not a full three-component Class-II constructive measure" in manifest["branch_map"]["functional_fork"]["rule"],
        {"scalar_reduction_relative_error": scalar_reduction_error, "lambda": params["lambda"], "gamma": params["gamma"]},
        assertions,
    )

    a3_evidence = load_json(REPO / next(row["evidence_path"] for row in manifest["components"] if row["id"] == pert["id"]))
    a4_evidence = load_json(REPO / next(row["evidence_path"] for row in manifest["components"] if row["id"] == constructive["id"]))
    check(
        "scalar_perturbative_record_is_complete_pass",
        bool(a3_evidence.get("all_pass"))
        and len(a3_evidence.get("claims", [])) == 8
        and all(row.get("passed") for row in a3_evidence.get("claims", [])),
        {"all_pass": a3_evidence.get("all_pass"), "assertions": len(a3_evidence.get("claims", []))},
        assertions,
    )
    check(
        "scalar_constructive_operator_record_is_complete_pass",
        a4_evidence.get("verdict") == "A4-SCALAR-CONSTRUCTIVE-INTEGRATED-PASS"
        and a4_evidence.get("assertion_summary", {}).get("passed") == 31
        and a4_evidence.get("assertion_summary", {}).get("total") == 31
        and not a4_evidence.get("failures"),
        {"verdict": a4_evidence.get("verdict"), "assertions": a4_evidence.get("assertion_summary")},
        assertions,
    )

    no_overclaim_text = " ".join(card.get("no_overclaim", "") for card in cards.values()).lower()
    check(
        "bcc_route_b_infinite_volume_and_full_classii_measure_are_excluded",
        "bcc" in no_overclaim_text
        and "route b" in no_overclaim_text
        and "infinite volume" in no_overclaim_text
        and any("full three-component derivative Class-II constructive measure" in item for item in manifest["honesty_boundary"]),
        manifest["honesty_boundary"],
        assertions,
    )
    check(
        "termination_verdict_is_branch_aware_not_unified_physical_closure",
        manifest["termination_verdict"]["result"] == "PASS@BRANCH-AWARE-DECLARED-SCOPE"
        and "not a full three-component Class-II constructive measure" in manifest["branch_map"]["functional_fork"]["rule"]
        and "parameter-identical" in manifest["termination_verdict"]["not_meaning"],
        manifest["termination_verdict"],
        assertions,
    )
    a4_component = next(row for row in manifest["components"] if row["id"] == "A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE")
    a4_publication_ok = (
        sha256(REPO / a4_component["publication_preflight_path"]) == a4_component["publication_preflight_sha256"]
        and sha256(REPO / a4_component["referee_package_confirmed"]) == a4_component["referee_package_confirmed_sha256"]
        and sha256(REPO / a4_component["published_bundle_manifest"]) == a4_component["published_bundle_manifest_sha256"]
    )
    capstone_review = manifest["capstone_publication_review"]
    capstone_candidate_ok = (
        sha256(REPO / capstone_review["candidate_source"]["path"])
        == capstone_review["candidate_source"]["sha256"]
        and sha256(REPO / capstone_review["candidate_pdf"]["path"])
        == capstone_review["candidate_pdf"]["sha256"]
    )
    check(
        "a4_published_prerequisite_and_exact_capstone_review_are_closed",
        manifest["review_gate"]["status"] == "CLOSED"
        and manifest["review_gate"]["confirmed_on"] == "2026-07-19"
        and manifest["publication_prerequisites"][0]["claim_id"] == "A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE"
        and manifest["publication_prerequisites"][0]["status"] == "SATISFIED"
        and capstone_review["status"] == "CLOSED-BATCH-AUTHORIZATION"
        and capstone_review["confirmed_by"] == "Jusang Lee"
        and capstone_review["confirmed_on"] == "2026-07-19"
        and a4_publication_ok
        and capstone_candidate_ok,
        {
            "review_gate": manifest["review_gate"],
            "publication_prerequisites": manifest["publication_prerequisites"],
            "a4_publication_hashes_ok": a4_publication_ok,
            "capstone_candidate_hashes_ok": capstone_candidate_ok,
            "capstone_publication_review": capstone_review,
        },
        assertions,
    )

    passed = sum(row["status"] == "PASS" for row in assertions)
    verdict = "A5-SECTOR-A-SYNTHESIS-PRIMARY-PASS" if passed == len(assertions) else "A5-SECTOR-A-SYNTHESIS-PRIMARY-FAIL"
    output = {
        "schema": "tect/a5-sector-a-synthesis-primary-result/1.0",
        "claim_id": __claims__[0],
        "script_version": __version__,
        "verdict": verdict,
        "termination_verdict": manifest["termination_verdict"],
        "parameter_bridge": {"shared": shared, "scalar_mass_squared": scalar_mass2, "full_mass_squared": full_mass2},
        "component_hash_rows": component_hash_rows,
        "component_status_rows": component_status_rows,
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
    print("Mass fork:", scalar_mass2, "!=", full_mass2)
    print("Evidence:", args.output.resolve())
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
