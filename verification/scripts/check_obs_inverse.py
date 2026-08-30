#!/usr/bin/env python3
"""Validate the Pre-A observation-first inverse-lane contract."""

__version__ = "1.0.0"
__first_issued__ = "2026-08-30"
__version_issued__ = "2026-08-30"

import argparse
import hashlib
import json
import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-observation-first-inverse-lane-contract-manifest.json"
SCHEMA = "tect/pre-a-observation-first-inverse-lane/1.0"
MAP_STAGES = ["F_reg", "F_lim", "F_eff", "F_obs"]
CARD_FIELDS = {
    "candidate_id",
    "role",
    "source_pointer",
    "layer_status",
    "microscopic_model",
    "dynamics_owner",
    "forward_map",
    "observation_partition",
    "uncertainty",
    "inverse_tests",
    "parameter_accounting",
    "evidence_level",
    "admission_status",
    "non_claims",
    "falsifiers",
    "stop_condition",
}
EXPECTED_CANDIDATES = {
    "PA-M0-ESTABLISHED-LOW-ENERGY-BASELINE-v0",
    "PA-M1-CURRENT-PINNED-PRODUCTION-FUNCTIONAL-v0",
    "PA-M2-CI8-RS-v0",
    "PA-M5-NL3-SV-v0",
    "CMP-FREF-IDMOB-LANGEVIN-v0",
    "GEO-T055-BCC-TRUNCATED-OCTAHEDRON-v0",
    "EXT-TECT-YM-FINITE-SUPPLIER-SNAPSHOT-v0",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    if data.get("claim_bearing") is not False or data.get("tier") != "T0":
        errors.append("registration must remain non-claim-bearing T0")
    if data.get("gate_id") != "PA-INVERSE-OBSERVATION-TARGET-MAP-HOLDOUT-FREEZE":
        errors.append("wrong inverse gate id")
    if "NO_ADMITTED_MICROSCOPIC_FORWARD_MAP" not in str(data.get("status", "")):
        errors.append("current zero-admission boundary missing")

    pointers = data.get("authority_pointers")
    if not isinstance(pointers, list) or not pointers:
        errors.append("authority pointers missing")
        pointers = []
    for pointer in pointers:
        if not isinstance(pointer, dict) or set(pointer) != {"path", "sha256", "role"}:
            errors.append(f"malformed authority pointer {pointer!r}")
            continue
        path = REPO / str(pointer["path"])
        if not path.is_file():
            errors.append(f"missing authority {pointer['path']}")
        elif sha256(path) != pointer["sha256"]:
            errors.append(f"authority hash drift {pointer['path']}")

    layers = data.get("layer_contract", {}).get("ordered_layers", [])
    if [item.get("id") for item in layers if isinstance(item, dict)] != [
        "L1_MATHEMATICAL_THEOREM",
        "L2_MODEL_CONSISTENCY",
        "L3_PHYSICAL_IDENTITY",
        "L4_EMPIRICAL_VALIDATION",
    ]:
        errors.append("four-layer order or identity changed")
    if data.get("layer_contract", {}).get("no_automatic_promotion") is not True:
        errors.append("automatic layer promotion must be forbidden")
    lanes = data.get("lane_contract", {})
    if set(lanes) != {"forward_lane", "inverse_lane", "independence_rule"}:
        errors.append("forward/inverse lane separation malformed")

    forward = data.get("forward_map_contract", {})
    if [item.get("id") for item in forward.get("stages", []) if isinstance(item, dict)] != MAP_STAGES:
        errors.append("forward-map stages must be F_reg/F_lim/F_eff/F_obs")
    if not str(forward.get("mathematical_form", "")).startswith("P_M("):
        errors.append("predictive or set-valued forward law missing")
    physical = set(data.get("dynamics_owner_contract", {}).get("physical_owner_required", []))
    proof = set(data.get("dynamics_owner_contract", {}).get("proof_owner_required", []))
    if not {"generator_L_or_transfer_T", "physical_projection", "limit_order"} <= physical:
        errors.append("physical owner minimum fields missing")
    if proof != {
        "filtration",
        "heat_root_map",
        "raw_current_spatial_intertwiner",
        "production_one_use_q_ledger",
    }:
        errors.append("proof owner contract drift")

    anchors = data.get("observation_anchor_manifest", {}).get("anchors", [])
    anchor_ids = {item.get("anchor_id") for item in anchors if isinstance(item, dict)}
    if anchor_ids != {
        "OBS-LC-CAL-001",
        "OBS-QFT-CAL-001",
        "OBS-GR-CAL-001",
        "OBS-CMB-CAL-001",
        "OBS-SCALE-CAL-001",
    }:
        errors.append("calibration anchor set drift")
    for anchor in anchors:
        if anchor.get("role") != "calibration":
            errors.append(f"{anchor.get('anchor_id')}: non-calibration role")
        source = anchor.get("source", {})
        if not str(source.get("url", "")).startswith("https://"):
            errors.append(f"{anchor.get('anchor_id')}: primary source URL missing")
        if not source.get("published_at") or not source.get("accessed_at"):
            errors.append(f"{anchor.get('anchor_id')}: source dates missing")
        if not anchor.get("lineage_group") or not anchor.get("falsifier"):
            errors.append(f"{anchor.get('anchor_id')}: lineage/falsifier missing")

    holdouts = data.get("holdout_manifest", {}).get("holdouts", [])
    holdout_ids = {item.get("holdout_id") for item in holdouts if isinstance(item, dict)}
    required_holdouts = {
        "HOLD-LC-001",
        "HOLD-GR-001",
        "HOLD-QCD-001",
        "HOLD-SPEC-001",
        "HOLD-BBN-001",
        "HOLD-LSS-001",
        "PROS-LOCK-001",
    }
    if holdout_ids != required_holdouts:
        errors.append("holdout set drift")
    prospective = [item for item in holdouts if item.get("role") == "prospective_locked"]
    if len(prospective) != 1 or prospective[0].get("holdout_id") != "PROS-LOCK-001":
        errors.append("exactly one empty prospective lock is required")
    elif any(
        prospective[0].get(field) is not False
        for field in ("target_visible", "commitment_present", "prediction_present")
    ):
        errors.append("prospective target must remain opaque, uncommitted, and empty")
    for item in holdouts:
        if item.get("holdout_id") != "PROS-LOCK-001" and item.get("role") != "retrospective_validation":
            errors.append(f"{item.get('holdout_id')}: public target promoted to prospective")
        if item.get("parameter_tuning_allowed") is not False:
            errors.append(f"{item.get('holdout_id')}: target tuning must be forbidden")

    cards = data.get("candidate_cards", [])
    candidate_ids = {item.get("candidate_id") for item in cards if isinstance(item, dict)}
    if candidate_ids != EXPECTED_CANDIDATES or len(cards) != len(EXPECTED_CANDIDATES):
        errors.append("candidate identity set drift or duplicate")
    allowed_admission = set(data.get("candidate_card_schema", {}).get("admission_values", []))
    for card in cards:
        if set(card) != CARD_FIELDS:
            errors.append(f"{card.get('candidate_id')}: card fields malformed")
        if list(card.get("forward_map", {})) != MAP_STAGES:
            errors.append(f"{card.get('candidate_id')}: forward map stage order/coverage invalid")
        if card.get("admission_status") not in allowed_admission:
            errors.append(f"{card.get('candidate_id')}: invalid admission value")
        if card.get("candidate_id") != "PA-M0-ESTABLISHED-LOW-ENERGY-BASELINE-v0" and card.get("admission_status") == "PASS":
            errors.append(f"{card.get('candidate_id')}: microscopic candidate prematurely admitted")
        tests = card.get("inverse_tests", {})
        if tests.get("identifiability") == "UNIQUE" or tests.get("predictivity") in {
            "PROSPECTIVE_PASS",
            "PROSPECTIVE_FAIL",
        }:
            errors.append(f"{card.get('candidate_id')}: unearned inverse verdict")
        for list_field in ("non_claims", "falsifiers"):
            if not isinstance(card.get(list_field), list) or not card.get(list_field):
                errors.append(f"{card.get('candidate_id')}: {list_field} missing")

    comparison = data.get("candidate_comparison", {})
    if comparison.get("scalar_total_score_allowed") is not False:
        errors.append("compensatory scalar score must be forbidden")
    if comparison.get("mandatory_baseline") != "PA-M0-ESTABLISHED-LOW-ENERGY-BASELINE-v0":
        errors.append("mandatory M0 baseline missing")
    if comparison.get("current_selection") != "NO_SELECTION_ZERO_ADMITTED_MICROSCOPIC_FORWARD_MAPS":
        errors.append("current no-selection verdict drift")
    if {row.get("candidate_id") for row in comparison.get("rows", [])} != EXPECTED_CANDIDATES:
        errors.append("comparison rows do not match candidate cards")
    if data.get("reference_only_crosswalk", {}).get("mode") != "POINTERS_ONLY_NO_MATRIX_COPY":
        errors.append("reference-only pointer rule missing")

    hostile = data.get("hostile_test_contract", [])
    hostile_ids = [item.get("id") for item in hostile if isinstance(item, dict)]
    if hostile_ids != [f"H{number:02d}-{suffix}" for number, suffix in [
        (1, "HOLDOUT-MUTATION"),
        (2, "DERIVED-DUPLICATE"),
        (3, "LABEL-PERMUTATION"),
        (4, "MOBILITY-TWINS"),
        (5, "CONTRACT-HASH-CHANGE"),
        (6, "REGULATOR-SURVIVAL-FLIP"),
        (7, "M0-SYNTHETIC"),
        (8, "INJECTED-EQUIVALENCE"),
        (9, "POST-UNSEAL-RETUNE"),
        (10, "PHYSICAL-EMPTY-SUBSTITUTION"),
        (11, "NO-UNIFORM-BOUND"),
        (12, "COMPENSATORY-SCORE"),
    ]]:
        errors.append("hostile fixture order or coverage drift")
    if any(set(item) != {"id", "mutation", "expected"} for item in hostile):
        errors.append("hostile fixture fields malformed")

    non_claims = " ".join(data.get("non_claims", []))
    for token in ("physical-empty", "Pre-A", "A13", "Yang-Mills", "mass-gap"):
        if token not in non_claims:
            errors.append(f"non-claim firewall missing {token}")
    if data.get("synthesis_policy", {}).get("current_pdf") != "NONE":
        errors.append("registration must not issue a PDF")
    return errors


def self_test(data: dict) -> int:
    assert not validate(data), "valid manifest rejected"
    mutations = []
    promoted = json.loads(json.dumps(data))
    promoted["candidate_cards"][1]["admission_status"] = "PASS"
    mutations.append(promoted)
    leaked = json.loads(json.dumps(data))
    leaked["holdout_manifest"]["holdouts"][-1]["target_visible"] = True
    mutations.append(leaked)
    scored = json.loads(json.dumps(data))
    scored["candidate_comparison"]["scalar_total_score_allowed"] = True
    mutations.append(scored)
    missing_stage = json.loads(json.dumps(data))
    del missing_stage["candidate_cards"][1]["forward_map"]["F_eff"]
    mutations.append(missing_stage)
    for mutation in mutations:
        assert validate(mutation), "hostile mutation accepted"
    print("OBS-INVERSE-SELFTEST: PASS (4 hostile mutations rejected)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"OBS-INVERSE: FAIL - {exc}")
        return 1
    if not isinstance(data, dict):
        print("OBS-INVERSE: FAIL - manifest root must be an object")
        return 1
    if args.self_test:
        return self_test(data)
    errors = validate(data)
    if errors:
        print("OBS-INVERSE: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    anchors = len(data["observation_anchor_manifest"]["anchors"])
    holdouts = len(data["holdout_manifest"]["holdouts"])
    candidates = len(data["candidate_cards"])
    hostile = len(data["hostile_test_contract"])
    print(
        "OBS-INVERSE: PASS "
        f"(anchors={anchors}; holdouts={holdouts}; candidates={candidates}; "
        f"hostile={hostile}; admitted_microscopic=0)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
