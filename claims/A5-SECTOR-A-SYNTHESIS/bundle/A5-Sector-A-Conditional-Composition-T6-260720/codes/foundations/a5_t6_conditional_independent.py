#!/usr/bin/env python3
"""Non-importing audit of the A5 T6 conditional-composition contract.

This file intentionally does not import the primary audit.  It reconstructs
the canonical contract digest, dependency and hypothesis map, T5 baseline
bundle integrity, Decimal mass fork, referee-package boundary, and weakness
classification directly from frozen records.
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
DEFAULT_PRIMARY = CLAIM / "runs" / "2026-07-20-t6-conditional-published-primary" / "result.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-20-t6-conditional-published-independent" / "result.json"


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary-result", type=Path, default=DEFAULT_PRIMARY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = load_json(MANIFEST)
    contract = manifest["theorem_contract"]
    authority = manifest["authority"]
    assertions: list[dict[str, Any]] = []

    check(
        "independent_source_hash_matches_authority",
        sha256(Path(__file__)) == authority["independent_audit"]["sha256"],
        {"actual": sha256(Path(__file__)), "expected": authority["independent_audit"]["sha256"]},
        assertions,
    )
    primary = load_json(args.primary_result)
    primary_source = REPO / authority["primary_audit"]["path"]
    primary_summary = primary.get("assertion_summary", {})
    check(
        "fresh_primary_result_and_source_are_complete",
        sha256(primary_source) == authority["primary_audit"]["sha256"]
        and primary.get("verdict") == "A5-T6-CONDITIONAL-PRIMARY-PASS"
        and int(primary_summary.get("total", 0)) > 0
        and int(primary_summary.get("passed", -1)) == int(primary_summary.get("total", 0)),
        {"source_sha256": sha256(primary_source), "verdict": primary.get("verdict"), "summary": primary_summary},
        assertions,
    )

    actual_contract_digest = canonical_digest(contract)
    check(
        "theorem_contract_is_canonical_and_agrees_with_primary",
        actual_contract_digest == manifest["theorem_contract_sha256"]
        and actual_contract_digest == primary.get("theorem_contract_sha256"),
        {
            "actual": actual_contract_digest,
            "manifest": manifest["theorem_contract_sha256"],
            "primary": primary.get("theorem_contract_sha256"),
        },
        assertions,
    )
    confirmation = manifest.get("operator_confirmation", {})
    candidate_source = REPO / confirmation.get("candidate_source", "__missing__")
    candidate_pdf = REPO / confirmation.get("candidate_pdf", "__missing__")
    check(
        "operator_confirmation_reconstructs_exact_v1_0_candidate",
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

    baseline = manifest["immutable_t5_baseline"]
    bundle_root = REPO / baseline["bundle_path"]
    bundle_manifest_path = bundle_root / "MANIFEST.json"
    bundle = load_json(bundle_manifest_path)
    file_rows = []
    for relative, expected in bundle["files"].items():
        path = bundle_root / relative
        file_rows.append(path.is_file() and sha256(path) == expected)
    reconstructed_digest = digest_from_files(bundle["files"])
    check(
        "t5_history_bundle_is_independently_reconstructed",
        sha256(bundle_manifest_path) == baseline["bundle_manifest_sha256"]
        and len(bundle["files"]) == baseline["bundle_file_count"]
        and bool(file_rows)
        and all(file_rows)
        and reconstructed_digest == bundle["bundle_digest"] == baseline["bundle_digest"],
        {
            "file_count": len(bundle["files"]),
            "file_hashes_ok": bool(file_rows) and all(file_rows),
            "reconstructed_digest": reconstructed_digest,
            "expected_digest": baseline["bundle_digest"],
        },
        assertions,
    )

    hypotheses = contract["named_hypotheses"]
    gates = (REPO / "claims" / "GATES.md").read_text(encoding="utf-8")
    registered = {name: f"### **{name}**" in gates for name in hypotheses}
    expected_hypotheses = [
        "A5-H1-CANONICAL-KERNEL-MANIFEST",
        "A1-KERNEL-CONV",
        "A1-SHELL-POSITIVITY",
        "A2-H2-SEXTIC-COERCIVITY",
        "A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL",
        "A3-H1-DIM3-Q4-KERNEL",
        "A3-H2-IR-POSITIVITY",
    ]
    check(
        "exact_seven_hypothesis_set_is_registered",
        hypotheses == expected_hypotheses and all(registered.values()),
        {"actual": hypotheses, "expected": expected_hypotheses, "registered": registered},
        assertions,
    )

    premise_tiers = {row["id"]: row["tier"] for row in contract["premises"]}
    lifts = contract["sub_t6_dependency_lifts"]
    expected_t6 = {
        "A2-FULL-PRODUCTION-WELLPOSED",
        "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM",
        "A3-PERTURBATIVE-CONTINUUM-CORRELATORS",
        "A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE",
    }
    sub_t6 = {name for name, tier in premise_tiers.items() if tier != "T6"}
    check(
        "tier_matrix_has_four_t6_premises_and_two_named_lifts",
        {name for name, tier in premise_tiers.items() if tier == "T6"} == expected_t6
        and sub_t6 == set(lifts)
        and set(lifts.values()) <= set(hypotheses),
        {"premise_tiers": premise_tiers, "lifts": lifts},
        assertions,
    )

    full_chain = contract["branches"]["full_production"]["claim_chain"]
    scalar_conjunction = contract["branches"]["scalar_continuum"]["claim_conjunction"]
    check(
        "branch_topology_is_exact_and_disjoint",
        full_chain == [
            "A1-PRODUCTION-FUNCTIONAL-REALISATION",
            "A2-FULL-PRODUCTION-WELLPOSED",
            "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM",
        ]
        and scalar_conjunction == [
            "A3-PERTURBATIVE-CONTINUUM-CORRELATORS",
            "A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE",
        ]
        and not set(full_chain).intersection(scalar_conjunction),
        {"full": full_chain, "scalar": scalar_conjunction},
        assertions,
    )

    kernel = load_json(REPO / manifest["numeric_firewall"]["scalar_source"])
    functional = load_json(REPO / manifest["numeric_firewall"]["full_source"])
    params = functional["parameters"]
    scalar_mass = Decimal(str(kernel["mu2_shell"]))
    full_mass = Decimal(str(params["r"])) - Decimal(str(params["Z"])) ** 2 / (Decimal(4) * Decimal(str(params["Y"])))
    difference = abs(full_mass - scalar_mass)
    firewall = manifest["numeric_firewall"]
    check(
        "decimal_mass_fork_matches_manifest_and_primary",
        scalar_mass == Decimal(firewall["expected_scalar_shell_mass_squared"])
        and abs(full_mass - Decimal(firewall["expected_full_shell_mass_squared"]))
        < Decimal(firewall["full_mass_match_tolerance"])
        and difference > Decimal(firewall["required_absolute_difference_gt"])
        and primary.get("mass_fork", {}).get("scalar_shell_mass_squared") == str(scalar_mass)
        and primary.get("mass_fork", {}).get("full_shell_mass_squared") == str(full_mass),
        {"scalar": str(scalar_mass), "full": str(full_mass), "difference": str(difference)},
        assertions,
    )

    note_source = REPO / authority["referee_source"]["path"]
    note_pdf = REPO / authority["referee_pdf"]["path"]
    note_text = note_source.read_text(encoding="utf-8") if note_source.is_file() else ""
    required_note_tokens = [
        "T6 CONDITIONAL-THEOREM",
        "seven named hypotheses",
        "A5-H1-CANONICAL-KERNEL-MANIFEST",
        "0.005",
        "0.260000000009475",
        "full three-component derivative Class-II constructive measure",
        "BCC existence, selection",
        "operator-confirmed 2026-07-20",
    ]
    check(
        "referee_package_states_the_exact_conditional_boundary",
        note_source.is_file()
        and note_pdf.is_file()
        and sha256(note_source) == authority["referee_source"]["sha256"]
        and sha256(note_pdf) == authority["referee_pdf"]["sha256"]
        and all(token in note_text for token in required_note_tokens),
        {"required_tokens": required_note_tokens, "source_exists": note_source.is_file(), "pdf_exists": note_pdf.is_file()},
        assertions,
    )

    non_implications = " | ".join(contract["non_implications"] + contract["exclusions"]).lower()
    check(
        "non_implication_firewall_blocks_the_three_invalid_crossings",
        "shell-mass identity" in non_implications
        and "class-ii" in non_implications
        and "resummation" in non_implications
        and "t=0" in non_implications,
        contract["non_implications"],
        assertions,
    )

    weaknesses = manifest["sector_a_weakness_map"]
    ids = [row["id"] for row in weaknesses]
    status_values = {row["status"] for row in weaknesses}
    check(
        "weakness_map_is_unique_complete_and_fail_closed",
        len(ids) == len(set(ids))
        and status_values == {"CONTROLLED-BY-CONDITIONAL-T6", "OPEN-SEPARATE-CLAIM"}
        and "FULL-CLASSII-CONSTRUCTIVE-MEASURE" in ids
        and "INFINITE-VOLUME-AND-PHASE-TRANSITION" in ids
        and "BCC-EXISTENCE-AND-SELECTION" in ids,
        weaknesses,
        assertions,
    )

    status = load_json(CLAIM / "status.json")
    gate = manifest["operator_gate"]
    candidate_state = status.get("tier") == "T5" and gate in status.get("open_gates", [])
    published_state = status.get("tier") == "T6" and gate not in status.get("open_gates", [])
    reproduction = status.get("reproduction", {})
    current_t5_reproduction_ok = (
        candidate_state
        and reproduction.get("status") == "AVAILABLE"
        and reproduction.get("command") == "python codes/foundations/a5_sector_a_synthesis_verify.py"
    )
    confirmed_t6_reproduction_ok = (
        published_state
        and reproduction.get("status") == "AVAILABLE"
        and reproduction.get("command") == "python codes/foundations/a5_t6_conditional_verify.py"
    )
    check(
        "claim_state_preserves_t5_reproduction_until_t6_is_confirmed",
        (candidate_state or published_state)
        and status.get("hypotheses") == hypotheses
        and (current_t5_reproduction_ok or confirmed_t6_reproduction_ok),
        {
            "tier": status.get("tier"),
            "open_gates": status.get("open_gates"),
            "reproduction": reproduction,
            "current_t5_reproduction_ok": current_t5_reproduction_ok,
            "confirmed_t6_reproduction_ok": confirmed_t6_reproduction_ok,
        },
        assertions,
    )

    passed = sum(row["status"] == "PASS" for row in assertions)
    verdict = "A5-T6-CONDITIONAL-INDEPENDENT-PASS" if passed == len(assertions) else "A5-T6-CONDITIONAL-INDEPENDENT-FAIL"
    output = {
        "schema": "tect/a5-t6-conditional-independent-result/1.0",
        "claim_id": __claims__[0],
        "script_version": __version__,
        "verdict": verdict,
        "theorem_contract_sha256": actual_contract_digest,
        "hypotheses": hypotheses,
        "branches": {"full_production": full_chain, "scalar_continuum": scalar_conjunction},
        "mass_fork": {
            "scalar_shell_mass_squared": str(scalar_mass),
            "full_shell_mass_squared": str(full_mass),
            "absolute_difference": str(difference),
        },
        "immutable_t5_bundle_digest": reconstructed_digest,
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "promotion_boundary": "Operator confirmation is bound to exact v1.0; publication completeness additionally requires the bundle-last PUBLISHED package.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(assertions)} PASS")
    print(verdict)
    print("Contract:", actual_contract_digest)
    print("Evidence:", args.output.resolve())
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
