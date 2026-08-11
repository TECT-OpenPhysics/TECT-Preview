#!/usr/bin/env python3
"""Integrated verifier for EXP-000814 / R-168 v1.3.

Both independent engines run twice through their public CLIs. This verifier
pins the normalized v1.3 four-file package, accepts the exact proof-first
407/407 and 430/430 contracts or authority-complete 423/423 and 446/446
contracts, and preserves every v1.0--v1.2 contract. It cross-checks five new
T0 children, four negatives, three open successors, and all 27 v1.3 hostile
classes while retaining the 28/7/11/57/48 hostile-count contracts.

``--staged`` reports stale or missing formal, stored, generated, changelog, or
checkpoint authorities without weakening contradiction checks. The issued
v1.9/v1.0, v2.0/v1.1, and v2.1/v1.2 source/PDF pairs remain historical. The
R-167 ``v2_2_checkpoint_synthesis`` and R-168 ``v1_3_checkpoint_synthesis``
fields preserve their proof-first deferred history and now form exactly one
issued checkpoint row. This script creates no candidate, response, map,
prediction, freeze, tag, PDF, or formal authority.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping


__version__ = "1.3.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-round1-prospective-holdout-freeze-protocol"

TASK_ID = "T-054"
CLAIM_IDS = ("C6-SPACETIME-SIGNATURE",)
RESULT_NUMBER = "R-168"
RESULT_VERSION = "v1.3"
RESULT_ID = (
    "PA-ROUND1-PROSPECTIVE-HOLDOUT-FREEZE-PROTOCOL-AND-CURRENT-TREE-"
    "READINESS-AUDIT"
)
V1_0_EXPLORATION_ID = "EXP-000807"
HARDENING_EXPLORATION_ID = "EXP-000808"
V1_1_EXPLORATION_ID = "EXP-000810"
V1_2_EXPLORATION_ID = "EXP-000812"
EXPLORATION_ID = "EXP-000814"
PRIOR_EXPLORATION_IDS = (
    V1_0_EXPLORATION_ID,
    HARDENING_EXPLORATION_ID,
    V1_1_EXPLORATION_ID,
    V1_2_EXPLORATION_ID,
)
PARENT_EXPLORATIONS = ("EXP-000791", *PRIOR_EXPLORATION_IDS)
AUDITED_COMMIT = "99157442831c0e44d425b5d5f8cd78856c57da53"
PARENT_GATE = "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE"

V1_0_NEGATIVE_IDS = (
    "NG-2026-08-11-PRE-A-ROUND1-CURRENT-TREE-PROSPECTIVE-HOLDOUT-"
    "NONEXISTENCE",
)
V1_1_NEGATIVE_IDS = (
    "NG-2026-08-11-PRE-A-ROUND1-CURRENT-VERSION-MAP-ONLY-ADMISSION-REPAIR",
)
V1_2_NEGATIVE_IDS = (
    "NG-2026-08-11-PRE-A-M2-LANE-Q-LINEAR-SOURCE-AUTOMATIC-PHYSICAL-"
    "STIFFNESS-RESPONSE",
)
PRIOR_NEGATIVE_IDS = (*V1_0_NEGATIVE_IDS, *V1_1_NEGATIVE_IDS, *V1_2_NEGATIVE_IDS)
NEW_NEGATIVE_IDS = (
    "NG-2026-08-11-PRE-A-M2-V0-ONE-REAL-SCALAR-AUTOMATIC-INTERNAL-U1-"
    "WINDING-AND-HELICITY",
    "NG-2026-08-11-PRE-A-M2-ONE-Q-PHASON-AUTOMATIC-PHYSICAL-"
    "SUPERFLUID-DENSITY",
    "NG-2026-08-11-PRE-A-M2-POSITIVE-LOCAL-INVERTIBILITY-AUTOMATIC-UNIT-"
    "EXPONENT",
    "NG-2026-08-11-PRE-A-M2-SIX-ABSOLUTE-ERRORS-AUTOMATIC-LOG-SLOPE-"
    "CONTROL",
)
NEGATIVE_IDS = (*PRIOR_NEGATIVE_IDS, *NEW_NEGATIVE_IDS)
REUSED_NEGATIVE_IDS = (
    "NG-2026-08-09-PRE-A-ROUND1-UNFROZEN-TOURNAMENT-SELECTION",
)
V1_0_CLOSED_SUBGATES = (
    "PA-ROUND1-COMMON-ESTIMAND-AND-CANDIDATE-MAP-SCHEMA",
    "PA-ROUND1-PROSPECTIVE-FREEZE-PROVENANCE-PROTOCOL",
    "PA-ROUND1-TARGET-INDEPENDENCE-AND-ANTI-LEAKAGE-SCHEMA-VALIDATOR",
    "PA-ROUND1-CURRENT-CANDIDATE-MAP-ADMISSION-EMPTY-SET-AUDIT",
)
V1_1_CLOSED_SUBGATES = (
    "PA-ROUND1-CURRENT-VERSION-M1-M2-M5-MAP-ONLY-ADMISSION-EMPTY-SET",
    "PA-M2-CI8-FINITE-TORUS-GAUSSIAN-DISPERSION-FINGERPRINT",
)
V1_2_CLOSED_SUBGATES = (
    "PA-M2-CI8-LINEAR-PROBE-SECOND-ORDER-RESPONSE-NONIDENTIFIABILITY",
    "PA-M2-CI8-PHYSICAL-RESPONSE-SUCCESSOR-MINIMUM-CONTRACT-SCHEMA",
)
NEW_CLOSED_SUBGATES = (
    "PA-M2-CI8-V0-REAL-SCALAR-INTERNAL-U1-TRIVIALITY-AND-NO-INTRINSIC-"
    "WINDING",
    "PA-M2-CI8-ONE-Q-AUXILIARY-PHASON-CURVATURE-AND-FINITE-TORUS-SECANT",
    "PA-M2-CI8-HELICITY-TENSOR-CONTACT-SHIFT-NONIDENTIFIABILITY",
    "PA-M2-CI8-ANALYTIC-MAP-INTEGER-EXPONENT-TRANSPORT",
    "PA-M2-CI8-SIX-STAGE-RELATIVE-LOG-SLOPE-ERROR-TRANSPORT",
)
CLOSED_SUBGATES = (
    *V1_0_CLOSED_SUBGATES,
    *V1_1_CLOSED_SUBGATES,
    *V1_2_CLOSED_SUBGATES,
    *NEW_CLOSED_SUBGATES,
)
PHYSICAL_RESPONSE_GATE = "PA-M2-CI8-PHYSICAL-RESPONSE-CHANNEL-AND-ERROR-BOUND"
V1_0_OPEN_GATES = (
    PARENT_GATE,
    "PA-ROUND1-PER-PARAMETER-COMMON-INPUT-LEDGER",
    "PA-ROUND1-INDEPENDENT-CUSTODIAN-OPAQUE-TARGET-COMMITMENT",
    "PA-ROUND1-ADMISSIBLE-MICROSCOPIC-CANDIDATE-MAP-AND-FROZEN-PREDICTION",
    "PA-ROUND1-CRYPTOGRAPHIC-CUSTODIAN-SIGNATURE-AND-REMOTE-FREEZE-"
    "VERIFICATION",
)
OPEN_SUCCESSOR_GATES = (
    "PA-M2-SUCCESSOR-SUBSTANTIVE-COMPACT-ACTION-BACKGROUND-PROBE-AND-"
    "WINDING-LAW",
    "PA-M2-SUCCESSOR-ORDERED-STATE-PHYSICAL-MODE-AND-RESPONSE-LIMIT",
    "PA-M2-SUCCESSOR-SIX-TERM-CRITICAL-ESTIMAND-ERROR-BUDGET",
)
OPEN_GATES = (*V1_0_OPEN_GATES, PHYSICAL_RESPONSE_GATE, *OPEN_SUCCESSOR_GATES)
ALL_GATE_IDS = (*CLOSED_SUBGATES, *OPEN_GATES)
V1_0_ALL_GATE_IDS = (*V1_0_CLOSED_SUBGATES, *V1_0_OPEN_GATES)
V1_1_EXPLORATION_GATES = (
    *V1_1_CLOSED_SUBGATES,
    PHYSICAL_RESPONSE_GATE,
    *V1_0_OPEN_GATES,
)
V1_2_EXPLORATION_GATES = (
    *V1_2_CLOSED_SUBGATES,
    PHYSICAL_RESPONSE_GATE,
    PARENT_GATE,
)
HARDENING_GATE_IDS = (
    "PA-ROUND1-TARGET-INDEPENDENCE-AND-ANTI-LEAKAGE-SCHEMA-VALIDATOR",
    PARENT_GATE,
    "PA-ROUND1-ADMISSIBLE-MICROSCOPIC-CANDIDATE-MAP-AND-FROZEN-PREDICTION",
    "PA-ROUND1-CRYPTOGRAPHIC-CUSTODIAN-SIGNATURE-AND-REMOTE-FREEZE-"
    "VERIFICATION",
)
M2_SUCCESSOR_ID = "PA-M2-CI8-RS-DISPERSION-MAP-v1"
FINGERPRINT_COMPONENT_SHA256 = (
    "a00d2c537ba82ba12324d4b48d9a8190c84c1f071971d22dd37793ec36253eb9"
)
PRIMARY_SCRIPT_SHA256 = (
    "69a9486b060c711679314806b302af85652c6d8317fccebba83578b5b2d397a9"
)
INDEPENDENT_SCRIPT_SHA256 = (
    "6b100dd08e3daac385fc67fa5627f0c9f8c5d9ff8aa2a416d30018e72a033c26"
)
MANIFEST_SHA256 = "fdecf5dd6285e8bbe7115cabd59c2b86a8b2ba8d295acddf3fd18cdcb06cb676"
CERTIFICATE_SHA256 = "d365ae6d1de71d01745063ada47d81279b9892b65e1dc9e0f013b6bb79c411f3"
PROOF_FIRST_MANIFEST_STATUS = (
    "R-168 v1.3 PROOF-FIRST T0 NON-CLAIM-BEARING FIVE-CHILD THEOREM PACKAGE; "
    "FORMAL AUTHORITIES REGISTERED; COMBINED CHECKPOINT ISSUED; PHYSICAL RESPONSE, "
    "ROUND-1, C6, CP1, PHYSICAL SECTOR A AND PRE-A OPEN"
)
PRIMARY_PROOF_FIRST_ASSERTION_COUNT = 407
PRIMARY_FORMAL_ASSERTION_COUNT = 423
INDEPENDENT_PROOF_FIRST_ASSERTION_COUNT = 430
INDEPENDENT_FORMAL_ASSERTION_COUNT = 446
HARD_ROWS = (
    "D00-ADMISSION",
    "D01-SAME-REFERENCE",
    "D02-KINETIC-TENSOR",
    "D03-PHYSICAL-ZERO-MODES",
    "D04-SPEED-DISPERSION",
    "D05-COMPACT-WINDING",
    "D06-CRITICAL-DATA",
    "D07-VALIDATION",
    "D08-ROBUSTNESS",
    "D09-PREDICTION-COST",
)
RESIDUAL_HARD_ROWS = {
    "PA-M1-CURRENT-PINNED-PRODUCTION-FUNCTIONAL-v0": {
        "D01-SAME-REFERENCE": "FAIL",
        "D02-KINETIC-TENSOR": "NOT_ADMITTED",
    },
    "PA-M2-CI8-RS-v0": {
        "D03-PHYSICAL-ZERO-MODES": "NOT_ADMITTED",
        "D05-COMPACT-WINDING": "NOT_ADMITTED",
        "D06-CRITICAL-DATA": "NOT_TESTED",
        "D08-ROBUSTNESS": "NOT_ADMITTED",
    },
    "PA-M5-NL3-SV-v0": {
        "D04-SPEED-DISPERSION": "FAIL",
        "D05-COMPACT-WINDING": "FAIL",
    },
}
MAP_ONLY_HOSTILE_CODES = {
    "hard_row_removed": "MAP_ONLY_SURVIVAL_RULE_INVALID",
    "survival_rule_softened": "MAP_ONLY_SURVIVAL_RULE_INVALID",
    "m1_nonpass_promoted": "MAP_ONLY_RESIDUAL_INVALID",
    "m2_nonpass_promoted": "MAP_ONLY_RESIDUAL_INVALID",
    "m5_nonpass_promoted": "MAP_ONLY_RESIDUAL_INVALID",
    "preserved_regulator_removed": "MAP_ONLY_CHANGE_SCOPE_INVALID",
    "map_only_survivor_fabricated": "MAP_ONLY_SURVIVOR_FALSE_PROMOTION",
}
SUCCESSOR_HOSTILE_CODES = {
    "candidate_created": "SUCCESSOR_CREATION_FORBIDDEN",
    "candidate_manifest_materialized": "SUCCESSOR_CREATION_FORBIDDEN",
    "admission_promoted": "SUCCESSOR_PROMOTION_FORBIDDEN",
    "map_promoted": "SUCCESSOR_PROMOTION_FORBIDDEN",
    "prediction_materialized": "SUCCESSOR_OUTPUT_FORBIDDEN",
    "target_materialized": "SUCCESSOR_OUTPUT_FORBIDDEN",
    "freeze_or_tag_materialized": "SUCCESSOR_OUTPUT_FORBIDDEN",
    "score_or_selection_materialized": "SUCCESSOR_OUTPUT_FORBIDDEN",
    "response_channel_smuggled": "SUCCESSOR_REQUIRED_CONTRACT_INVALID",
    "error_budget_term_dropped": "SUCCESSOR_ERROR_BUDGET_INVALID",
    "fingerprint_dimension_changed": "SUCCESSOR_FINGERPRINT_INVALID",
}
SUCCESSOR_NOT_CREATED_FIELDS = (
    "admission_status",
    "microscopic_map_status",
    "prediction_status",
    "target_status",
    "freeze_status",
    "tag_status",
    "score_status",
    "selection_status",
)
PRIMARY_SCOPE_EXPECTED = {
    "protocol_schema_validated": True,
    "current_tree_readiness_audited": True,
    "actual_freeze_record_created": False,
    "git_tag_created": False,
    "external_target_commitment_present": False,
    "cryptographic_signature_verifier_implemented": False,
    "independent_remote_ref_verifier_implemented": False,
    "admitted_current_microscopic_map_present": False,
    "prospective_prediction_present": False,
    "m2_v1_candidate_created": False,
    "m2_minimum_physical_response_contract_schema_validated": True,
    "m2_linear_probe_response_nonidentifiability_closed": True,
    "m2_physical_response_channel_present": False,
    "m2_controlled_physical_error_bound_present": False,
    "m2_real_scalar_internal_u1_present": False,
    "m2_intrinsic_winding_present": False,
    "m2_auxiliary_phason_curvature_scoped": True,
    "m2_physical_superfluid_density_identified": False,
    "m2_tensor_contact_nonidentifiability_closed": True,
    "m2_analytic_integer_order_transport_closed": True,
    "m2_six_stage_relative_error_transport_closed": True,
    "parent_gate_closed": False,
    "Pre_A_complete": False,
    "Sector_A_complete": False,
}
INDEPENDENT_SCOPE_EXPECTED = {
    **{
        key: value
        for key, value in PRIMARY_SCOPE_EXPECTED.items()
        if key != "protocol_schema_validated"
    },
    "protocol_schema_shape_validated": True,
}

V13_SUITE_SCHEMA = "tect/pre-a-m2-ci8-v1-3-theorem-suite/1.0"
V13_AUTHORITY_SECTION_KEYS = (
    "m2_v0_real_scalar_internal_u1_and_winding_audit",
    "m2_one_q_auxiliary_phason_curvature_and_finite_torus_secant",
    "m2_helicity_tensor_contact_shift_nonidentifiability",
    "m2_analytic_map_integer_exponent_transport",
    "m2_six_stage_relative_log_slope_error_transport",
)
V13_HOSTILE_CODES = {
    "nontrivial_real_line_u1": "V13_U1_SCOPE_INVALID",
    "intrinsic_real_h2_winding": "V13_U1_SCOPE_INVALID",
    "spatial_translation_promoted_internal": "V13_U1_SCOPE_INVALID",
    "phason_promoted_physical_density": "V13_PHASON_ALGEBRA_INVALID",
    "phason_hessian_sign_flip": "V13_PHASON_ALGEBRA_INVALID",
    "fixed_torus_continuous_twist": "V13_PHASON_ALGEBRA_INVALID",
    "optimized_amplitude_torus_secant": "V13_PHASON_ALGEBRA_INVALID",
    "one_q_promoted_exact_euler_solution": "V13_PHASON_ALGEBRA_INVALID",
    "cubic_third_harmonic_removed": "V13_PHASON_ALGEBRA_INVALID",
    "contact_shift_nonsymmetric": "V13_RESPONSE_ALGEBRA_INVALID",
    "contact_shift_sign_flip": "V13_RESPONSE_ALGEBRA_INVALID",
    "finite_beta_contact_omitted": "V13_RESPONSE_ALGEBRA_INVALID",
    "ground_gap_hypothesis_removed": "V13_RESPONSE_ALGEBRA_INVALID",
    "positive_invertibility_forces_unit_order": "V13_MAP_ALGEBRA_INVALID",
    "x2_order_changed": "V13_MAP_ALGEBRA_INVALID",
    "x3_order_changed": "V13_MAP_ALGEBRA_INVALID",
    "six_absolute_errors_promoted": "V13_ERROR_ALGEBRA_INVALID",
    "delta_equal_one": "V13_ERROR_ALGEBRA_INVALID",
    "positive_floor_removed": "V13_ERROR_ALGEBRA_INVALID",
    "vanishing_delta_not_required": "V13_ERROR_ALGEBRA_INVALID",
    "candidate_or_parent_promoted": "V13_GLOBAL_SCOPE_INVALID",
    "gl1_compact_connected_argument_removed": "V13_U1_SCOPE_INVALID",
    "branch_amplitude_decoupled": "V13_PHASON_ALGEBRA_INVALID",
    "analytic_zero_value_removed": "V13_MAP_ALGEBRA_INVALID",
    "lambda_equal_one": "V13_ERROR_ALGEBRA_INVALID",
    "initial_stage_unbound": "V13_ERROR_ALGEBRA_INVALID",
    "adjacent_ratio_contract_removed": "V13_ERROR_ALGEBRA_INVALID",
}

FREEZE_SCHEMA = "tect/pre-a-round1-prospective-holdout-freeze/1.0"

ROOT_FIELDS = (
    "schema",
    "freeze_id",
    "prediction_id",
    "freeze_version",
    "round_id",
    "parent_gate",
    "status",
    "claim_bearing",
    "fixture_only",
    "contestant_snapshot",
    "evidence_snapshot",
    "target_contract",
    "observable_contract",
    "prediction_contract",
    "robustness_contract",
    "provenance",
    "scoring",
    "no_overclaim",
)
EXPECTED_CANDIDATES = (
    "PA-M0-ESTABLISHED-LOW-ENERGY-BASELINE-v0",
    "PA-M1-CURRENT-PINNED-PRODUCTION-FUNCTIONAL-v0",
    "PA-M2-CI8-RS-v0",
    "PA-M5-NL3-SV-v0",
)
EXPECTED_BLOCKERS = (
    "NO_MACHINE_FREEZE_RECORD",
    "NO_ADMITTED_MICROSCOPIC_SURVIVOR",
    "M1_MAP_AND_PREDICTION_ABSENT",
    "M2_PHYSICAL_PREDICTION_AND_HOLDOUT_ABSENT",
    "M5_MAP_AND_HOLDOUT_ABSENT",
    "PER_PARAMETER_COMMON_INPUT_LEDGER_INCOMPLETE",
    "PROSPECTIVE_PREDICTION_NOT_FROZEN",
)
HOSTILE_CODES = {
    "baseline_missing": "BASELINE_MISSING",
    "commitment_scalar_types": "COMMITMENT_INVALID",
    "contestant_scalar_type": "CONTESTANTS_INVALID",
    "duplicate_candidate_map": "MAP_CANDIDATE_DUPLICATE",
    "eligible_map_missing": "ELIGIBLE_MAP_MISSING",
    "empty_root_identity": "ROOT_VALUES_INVALID",
    "empty_target_identity": "TARGET_CONTRACT_INVALID",
    "estimand_container_type": "ESTIMAND_INVALID",
    "estimand_scalar_type": "ESTIMAND_INVALID",
    "estimator_container_type": "ESTIMAND_INVALID",
    "hash_mutation": "HASH_FAILURE",
    "hidden_sealed_payload": "TARGET_LEAKAGE",
    "independence": "INDEPENDENCE_OVERLAP",
    "input_discovery_source_id": "DISCOVERY_REUSE",
    "input_scalar_types": "INPUT_LEDGER_INVALID",
    "input_source_alias": "INPUT_FIELDS_INVALID",
    "input_source_id_missing": "INPUT_FIELDS_INVALID",
    "nested_wrong_type": "COMMITMENT_INVALID",
    "path_traversal": "HASH_FAILURE",
    "provenance_oid_scalar_types": "REMOTE_ANCHOR_INVALID",
    "remote_anchor": "REMOTE_ANCHOR_INVALID",
    "remote_url_no_hostname": "REMOTE_ANCHOR_INVALID",
    "root_extra": "ROOT_FIELDS_EXTRA",
    "target_alias": "TARGET_LEAKAGE",
    "target_estimand_mismatch": "TARGET_ESTIMAND_MISMATCH",
    "target_leakage": "TARGET_LEAKAGE",
    "temporal_order": "TEMPORAL_ORDER_INVALID",
    "unbound_prediction": "PREDICTION_CANDIDATE_UNBOUND",
}

PHYSICAL_CONTRACT_SCHEMA = (
    "tect/pre-a-m2-ci8-physical-response-successor-minimum-contract/1.1"
)
PHYSICAL_CONTRACT_ROOT_FIELDS = (
    "schema", "contract_id", "candidate_id", "parent_candidate_id", "status",
    "fixture_only", "candidate_created", "version_delta", "physical_control_map",
    "probe_contract", "state_reference_contract", "response_definition",
    "estimand_binding", "critical_prediction", "error_budget",
    "common_input_ledger", "hard_row_rerun", "verification",
    "prospective_firewall", "no_overclaim",
)
PHYSICAL_CONTRACT_ARTIFACT_REF_FIELDS = ("path", "sha256", "role", "media_type")
PHYSICAL_CONTRACT_ARTIFACT_ROLES = (
    "SOURCE_LAW", "LINEAR_PROBE", "QUADRATIC_CONTACT",
    "COMPACT_OR_GAUGE_ACTION", "PHYSICAL_CONTROL_MAP", "STATE_EXISTENCE",
    "RESPONSE_MAP", "RAW_ESTIMATOR", "PROOF", "VERIFIER_PRIMARY",
    "VERIFIER_INDEPENDENT", "VERIFIER_INTEGRATED", "ERROR_SCRIPT", "ERROR_RUN",
)
PHYSICAL_CONTRACT_MANDATORY_CHANGES = (
    "SECOND_ORDER_SOURCE_LAW", "COMPACT_OR_GAUGE_ACTION",
    "STATE_REFERENCE_CHANGE", "PHYSICAL_CONTROL_MAP",
    "REGULATOR_OR_LIMIT_CHANGE", "ERROR_BOUND_PROOF",
)
PHYSICAL_CONTRACT_CHANGE_ENUM = (
    *PHYSICAL_CONTRACT_MANDATORY_CHANGES, "MICROSCOPIC_MAP_ONLY",
)
PHYSICAL_CONTRACT_ERROR_TERMS = (
    "finite_torus_spacing", "regulator_removal", "nonlinear_remainder",
    "loop_or_renormalization", "state_reference_transfer", "raw_estimator",
)
PHYSICAL_CONTRACT_LIMIT_ORDER = (
    "SOURCE_TO_ZERO", "THERMODYNAMIC_LIMIT", "REGULATOR_REMOVAL",
    "CRITICAL_LIMIT_FROM_ORDERED_SIDE",
)
PHYSICAL_RESPONSE_SIGN_CONVENTION = (
    "helicity_modulus=+V^-1*d2F/dJ2|J=0; "
    "scalar_susceptibility=-V^-1*d2F/dJ2|J=0"
)
PHYSICAL_CONTRACT_HOSTILE_CODES = {
    "candidate_materialized": "PHYSICAL_CONTRACT_LIFECYCLE_INVALID",
    "case_changed_artifact_path": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "compact_action_missing": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "compact_action_placeholder": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "control_map_missing": "PHYSICAL_CONTRACT_CONTROL_MAP_INVALID",
    "control_map_r_of_t_target_leakage": "PHYSICAL_CONTRACT_CONTROL_MAP_INVALID",
    "control_map_scaling_window_holdout_leakage": "PHYSICAL_CONTRACT_CONTROL_MAP_INVALID",
    "decimal_ratio": "PHYSICAL_CONTRACT_ESTIMAND_INVALID",
    "denominator_one_ratio": "NUMERIC_LITERAL_INVALID",
    "duplicate_input_id": "PHYSICAL_CONTRACT_INPUT_LEDGER_INVALID",
    "duplicate_source_id": "PHYSICAL_CONTRACT_INPUT_LEDGER_INVALID",
    "duplicate_substantive_change": "PHYSICAL_CONTRACT_VERSION_DELTA_INVALID",
    "embedded_nul_artifact_path": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "error_evidence_reused": "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
    "error_margin_not_strict": "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
    "error_result_key_missing": "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
    "error_term_dropped": "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
    "error_total_not_sum": "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
    "estimand_mismatch": "PHYSICAL_CONTRACT_ESTIMAND_INVALID",
    "fingerprint_promoted_as_response": "PHYSICAL_CONTRACT_RESPONSE_INVALID",
    "forbidden_choices_placeholder": "PHYSICAL_CONTRACT_FIREWALL_INVALID",
    "forbidden_source_id": "PHYSICAL_CONTRACT_INPUT_LEDGER_INVALID",
    "free_semantic_placeholder": "PHYSICAL_CONTRACT_PREDICTION_INVALID",
    "hard_row_nonpass": "PHYSICAL_CONTRACT_HARD_ROWS_INVALID",
    "identical_verifier_hash": "PHYSICAL_CONTRACT_VERIFICATION_INVALID",
    "integrated_ref_missing": "PHYSICAL_CONTRACT_VERIFICATION_INVALID",
    "limit_order_missing": "PHYSICAL_CONTRACT_RESPONSE_INVALID",
    "limit_order_permuted": "PHYSICAL_CONTRACT_RESPONSE_INVALID",
    "limit_order_placeholder": "PHYSICAL_CONTRACT_RESPONSE_INVALID",
    "map_only_payload_under_substantive_label": "PHYSICAL_CONTRACT_VERSION_DELTA_INVALID",
    "non_script_verifier": "PHYSICAL_CONTRACT_VERIFICATION_INVALID",
    "overlong_artifact_path": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "overlong_rational_literal": "NUMERIC_LITERAL_INVALID",
    "prediction_candidate_unbound": "PHYSICAL_CONTRACT_PREDICTION_INVALID",
    "prediction_placeholder": "PHYSICAL_CONTRACT_PREDICTION_INVALID",
    "prediction_target_leakage": "PHYSICAL_CONTRACT_PREDICTION_INVALID",
    "probe_artifact_wrong_role": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "proof_ref_unbound": "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
    "quadratic_contact_missing": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "quadratic_contact_placeholder": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "response_map_ref_unbound": "PHYSICAL_CONTRACT_RESPONSE_INVALID",
    "scalar_susceptibility_relabel": "PHYSICAL_CONTRACT_RESPONSE_INVALID",
    "scaling_window_holdout_leakage": "PHYSICAL_CONTRACT_PREDICTION_INVALID",
    "single_implementation": "PHYSICAL_CONTRACT_VERIFICATION_INVALID",
    "source_section_unbound": "PHYSICAL_CONTRACT_SOURCE_BINDING_INVALID",
    "state_existence_ref_unbound": "PHYSICAL_CONTRACT_STATE_INVALID",
    "state_reference_missing": "PHYSICAL_CONTRACT_STATE_INVALID",
    "substantive_change_mislabeled_map_only": "PHYSICAL_CONTRACT_VERSION_DELTA_INVALID",
    "target_dependent_control": "PHYSICAL_CONTRACT_CONTROL_MAP_INVALID",
    "target_value_present": "PHYSICAL_CONTRACT_FIREWALL_INVALID",
    "trailing_dot_segment_artifact_path": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "trailing_space_segment_artifact_path": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "unbound_probe_hash": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "unknown_substantive_change": "PHYSICAL_CONTRACT_VERSION_DELTA_INVALID",
    "unreduced_ratio": "PHYSICAL_CONTRACT_ESTIMAND_INVALID",
    "visible_validation_source": "PHYSICAL_CONTRACT_INPUT_LEDGER_INVALID",
    "whitespace_ratio": "PHYSICAL_CONTRACT_ESTIMAND_INVALID",
}
PHYSICAL_CONTRACT_FUZZ_CODES = {
    **{
        f"ratio_{index:02d}": (
            "NUMERIC_LITERAL_INVALID", "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID"
        )
        for index in range(12)
    },
    **{
        f"path_{index:02d}": ("PHYSICAL_CONTRACT_PROBE_INVALID",)
        for index in range(6)
    },
    **{
        f"container_{index:02d}": ("PHYSICAL_CONTRACT_VERIFICATION_INVALID",)
        for index in range(5)
    },
    "nul_artifact_path": ("PHYSICAL_CONTRACT_PROBE_INVALID",),
    "overlong_artifact_path": ("PHYSICAL_CONTRACT_PROBE_INVALID",),
    "overlong_rational_literal": (
        "NUMERIC_LITERAL_INVALID", "PHYSICAL_CONTRACT_ESTIMAND_INVALID",
        "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
    ),
    "trailing_dot_segment": ("PHYSICAL_CONTRACT_PROBE_INVALID",),
    "trailing_space_segment": ("PHYSICAL_CONTRACT_PROBE_INVALID",),
    "case_changed_segment": ("PHYSICAL_CONTRACT_PROBE_INVALID",),
    "semantic_na_placeholder": ("PHYSICAL_CONTRACT_PREDICTION_INVALID",),
    "semantic_not_available_placeholder": ("PHYSICAL_CONTRACT_PREDICTION_INVALID",),
    "prediction_target_token": ("PHYSICAL_CONTRACT_PREDICTION_INVALID",),
    "scaling_holdout_token": ("PHYSICAL_CONTRACT_PREDICTION_INVALID",),
    "control_map_target_token": ("PHYSICAL_CONTRACT_CONTROL_MAP_INVALID",),
    "control_map_scaling_holdout_token": ("PHYSICAL_CONTRACT_CONTROL_MAP_INVALID",),
    "denominator_one_ratio": (
        "NUMERIC_LITERAL_INVALID", "PHYSICAL_CONTRACT_ESTIMAND_INVALID",
        "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
    ),
    "extra_key_root_int": ("PHYSICAL_CONTRACT_FIELDS_INVALID",),
    "extra_key_nested_none": ("PHYSICAL_CONTRACT_PREDICTION_INVALID",),
    "extra_key_artifact_tuple": ("PHYSICAL_CONTRACT_PROBE_INVALID",),
    "term_id_unhashable": ("PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",),
    "result_key_unhashable": ("PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",),
    "proof_path_unhashable": ("PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",),
    "input_id_unhashable": ("PHYSICAL_CONTRACT_INPUT_LEDGER_INVALID",),
    "input_class_unhashable": ("PHYSICAL_CONTRACT_INPUT_LEDGER_INVALID",),
    "source_id_unhashable": (
        "PHYSICAL_CONTRACT_INPUT_LEDGER_INVALID",
        "PHYSICAL_CONTRACT_SOURCE_BINDING_INVALID",
        "PHYSICAL_CONTRACT_FIREWALL_INVALID",
    ),
    "allowed_source_unhashable": ("PHYSICAL_CONTRACT_FIREWALL_INVALID",),
    "forbidden_choice_unhashable": ("PHYSICAL_CONTRACT_FIREWALL_INVALID",),
    "verifier_hash_unhashable": ("PHYSICAL_CONTRACT_VERIFICATION_INVALID",),
}

TARGET_FIELDS = (
    "target_id",
    "custodian",
    "protocol_or_accession",
    "estimand_id",
    "units",
    "independence_group",
    "blind",
    "predictor_access_before_freeze",
    "target_value_present",
    "commitment",
    "disclosure",
)
COMMITMENT_FIELDS = (
    "algorithm",
    "commitment_hex",
    "secret_key_custody",
    "payload_schema",
    "canonical_serialization",
    "domain_separation",
    "custodian_signature",
    "public_key_fingerprint",
    "issued_at_utc",
)
DISCLOSURE_FIELDS = ("status", "not_before_utc", "actual_at_utc")
PREDICTION_FIELDS = (
    "candidate_id",
    "predicted_relation",
    "physical_output",
    "theory_uncertainty",
    "acceptance_rule",
    "baseline_prediction",
    "allowed_inputs",
    "forbidden_knobs",
)
ALLOWED_INPUT_FIELDS = ("id", "class", "source", "source_id", "used_for")
ROBUSTNESS_FIELDS = (
    "volume",
    "boundary",
    "regulator",
    "coefficients",
    "implementation",
)
NESTED_FIELD_CONTRACTS = {
    "root_fields": ROOT_FIELDS,
    "target_fields": TARGET_FIELDS,
    "commitment_fields": COMMITMENT_FIELDS,
    "disclosure_fields": DISCLOSURE_FIELDS,
    "prediction_fields": PREDICTION_FIELDS,
    "allowed_input_fields": ALLOWED_INPUT_FIELDS,
    "robustness_fields": ROBUSTNESS_FIELDS,
}
COMMITMENT_DEFINITION = (
    "HMAC-SHA256(external custodian key, domain separator || 0x00 || "
    "RFC8785-JCS canonical target payload)"
)
PATH_POLICY = "relative normalized POSIX path resolved inside repository"

PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260811.md"
PRIMARY_SCHEMA = f"tect/{SLUG}-primary-result/1.0"
INDEPENDENT_SCHEMA = f"tect/{SLUG}-independent-result/1.0"
INTEGRATED_SCHEMA = f"tect/{SLUG}-integrated-result/1.0"

PRIMARY_STORED = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    f"2026-08-11-primary-{SLUG}/result.json"
)
INDEPENDENT_STORED = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    f"2026-08-11-independent-{SLUG}/result.json"
)
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    f"2026-08-11-integrated-{SLUG}/result.json"
)
R167_MANIFEST = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-local-measured-renyi-semiclassical-"
    "doublet-route-split-manifest.json"
)
CHECKPOINT_SOURCE = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/notes/pre-a-q3lock-local-renyi-doublet-"
    "and-prospective-freeze-checkpoint-260811-v0.8.tex.txt"
)
CHECKPOINT_PDF = CHECKPOINT_SOURCE.with_suffix("").with_suffix(".pdf")
CHECKPOINT_SOURCE_SHA256 = (
    "89dae8bbf53f299676aa98a56db35fe8b00d1b672f7fb068f6c17810b985412e"
)
CHECKPOINT_PDF_SHA256 = (
    "a83084c2ad66210dddeac71f7ec8efb0705554a68362cec1c7055e20e0185e4a"
)
CHECKPOINT_PAGES = 15
EXPECTED_HISTORICAL_CHECKPOINT_CORE = {
    "status": "ISSUED AS ONE COMBINED GATE-LEVEL CHECKPOINT AFTER PROOF VALIDATION",
    "source": CHECKPOINT_SOURCE.relative_to(REPO).as_posix(),
    "pdf": CHECKPOINT_PDF.relative_to(REPO).as_posix(),
    "source_sha256": CHECKPOINT_SOURCE_SHA256,
    "pdf_sha256": CHECKPOINT_PDF_SHA256,
    "pages": CHECKPOINT_PAGES,
    "workflow": (
        "No per-lemma or intermediate PDF was issued. One combined R-167 v1.9 / "
        "R-168 v1.0 gate-level synthesis source/PDF pair was issued only after the "
        "manifest, certificate, primary, non-importing independent, integrated, "
        "formal-authority, generated-surface, and source-form checks passed."
    ),
    "visual_qa": (
        "All 15 rendered pages were reviewed at readable resolution with zero "
        "clipping, overlap, broken equations, unreadable identifiers, black glyphs, "
        "or malformed page transitions; pypdf and pdfplumber each extracted 15 "
        "nonempty pages."
    ),
}
CHECKPOINT_REQUIRED_TOKENS = (
    RESULT_NUMBER,
    "v1.0",
    PRIOR_EXPLORATION_IDS[0],
    HARDENING_EXPLORATION_ID,
    *V1_0_CLOSED_SUBGATES,
    *V1_0_OPEN_GATES,
    "EXTERNAL_VERIFICATION_REQUIRED",
    "exactly seven stable blockers",
    "Reproduction and evidence contract",
    PRIMARY.relative_to(REPO).as_posix(),
    INDEPENDENT.relative_to(REPO).as_posix(),
    SCRIPT.relative_to(REPO).as_posix(),
    "PASS 125/125",
    "PASS 153/153",
    "PASS 218/218",
    "cryptographic or remote freeze verification",
    "semantic free-text target-independence proof",
    "physical Sector A",
    "Pre-A closure",
)

V2_HISTORICAL_CHECKPOINT_FIELD = "v2_checkpoint_synthesis"
V2_CHECKPOINT_SOURCE = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/notes/pre-a-q3lock-gibbs-feshbach-tfim-"
    "and-round1-map-fingerprint-checkpoint-260811-v0.9.tex.txt"
)
V2_CHECKPOINT_PDF = V2_CHECKPOINT_SOURCE.with_suffix("").with_suffix(".pdf")
V2_CHECKPOINT_SOURCE_SHA256 = (
    "ca8b0fdc1c4881aa13e3311851c719d0b6a0dfb4b27e0bb30906f7bc77b04239"
)
V2_CHECKPOINT_PDF_SHA256 = (
    "346595c8609be1e49fb33d87e5a469b01f9083c78d7a1fc89d3648b88ea4d243"
)
V2_CHECKPOINT_PAGES = 10
EXPECTED_V2_HISTORICAL_CHECKPOINT_CORE = {
    "status": "ISSUED AS ONE COMBINED GATE-LEVEL CHECKPOINT AFTER PROOF VALIDATION",
    "source": V2_CHECKPOINT_SOURCE.relative_to(REPO).as_posix(),
    "pdf": V2_CHECKPOINT_PDF.relative_to(REPO).as_posix(),
    "source_sha256": V2_CHECKPOINT_SOURCE_SHA256,
    "pdf_sha256": V2_CHECKPOINT_PDF_SHA256,
    "pages": V2_CHECKPOINT_PAGES,
    "workflow": (
        "No per-lemma or intermediate PDF was issued. One combined R-167 v2.0 / "
        "R-168 v1.1 gate-level synthesis source/PDF pair was issued only after the "
        "primary, non-importing independent, integrated, formal-authority, "
        "generated-surface, and source-form checks passed."
    ),
    "visual_qa": (
        "All 10 rendered pages were reviewed at readable resolution with zero "
        "clipping, overlap, broken equations, unreadable identifiers, black glyphs, "
        "or malformed page transitions; pypdf and pdfplumber each extracted 10 "
        "nonempty pages."
    ),
}
V2_HISTORICAL_CHECKPOINT_REQUIRED_TOKENS = (
    "R-167 v2.0", "EXP-000809", "R-168 v1.1", V1_1_EXPLORATION_ID,
    RESULT_ID, *V1_1_NEGATIVE_IDS, *V1_1_CLOSED_SUBGATES,
    PHYSICAL_RESPONSE_GATE, "205/205", "223/223",
    PRIMARY.relative_to(REPO).as_posix(),
    INDEPENDENT.relative_to(REPO).as_posix(),
    SCRIPT.relative_to(REPO).as_posix(),
    "no per-lemma or intermediate", "physical Sector A", "Pre-A",
)

NEXT_CHECKPOINT_FIELD = "v1_2_checkpoint_synthesis"
R167_NEXT_CHECKPOINT_FIELD = "v2_1_checkpoint_synthesis"
R167_V2_1_PRIMARY = (
    "codes/foundations/pre_a_cp1_st8_q3lock_local_measured_renyi_"
    "semiclassical_doublet_route_split.py"
)
R167_V2_1_INDEPENDENT = (
    "codes/foundations/pre_a_cp1_st8_q3lock_local_measured_renyi_"
    "semiclassical_doublet_route_split_independent.py"
)
R167_V2_1_INTEGRATED = (
    "codes/foundations/pre_a_cp1_st8_q3lock_local_measured_renyi_"
    "semiclassical_doublet_route_split_verify.py"
)
R167_V2_1_NEW_NEGATIVES = (
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-UNIFORM-QUADRATIC-IN-M-ALL-MOMENT-"
    "BOND-SHEAR-GRAPH-TRANSPORT",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-STATIC-MOMENTS-AND-LOW-GRAPH-"
    "AUTOMATIC-TWENTIETH-HISTORY-MOMENT",
)
R167_V2_1_CLOSED_GATES = (
    "PA-CP1-ST8-Q3LOCK-TWO-ORIENTATION-TWENTIETH-MOMENT-FIXED-EDGE-"
    "CORRIDOR-REDUCTION",
    "PA-CP1-ST8-Q3LOCK-FULL-OSCILLATOR-EDGE-BLOCK-PARITY-DOUBLET-CLUSTER-"
    "AND-UNIFORM-ONSITE-SPECTRAL-CUTOFF-REMOVAL",
)
R167_V2_1_OPEN_GATES = (
    "PA-CP1-ST8-Q3LOCK-TRANSLATE-UNIFORM-LOCAL-FIFTH-GIBBS-MOMENT-AND-"
    "ELLIPTIC-EMBEDDING",
    "PA-CP1-ST8-Q3LOCK-SIMULTANEOUS-BOND-SHEAR-FIFTH-GRAPH-PROPAGATION",
)
NEXT_CHECKPOINT_REQUIRED_TOKENS = (
    "R-167 v2.1", "EXP-000811", "R-168 v1.2", V1_2_EXPLORATION_ID, RESULT_ID,
    *R167_V2_1_NEW_NEGATIVES, *R167_V2_1_CLOSED_GATES,
    *R167_V2_1_OPEN_GATES, *V1_2_NEGATIVE_IDS, *V1_2_CLOSED_SUBGATES,
    PHYSICAL_RESPONSE_GATE, "209/209", "138/138", "340/340", "361/361",
    R167_V2_1_PRIMARY, R167_V2_1_INDEPENDENT, R167_V2_1_INTEGRATED,
    PRIMARY.relative_to(REPO).as_posix(),
    INDEPENDENT.relative_to(REPO).as_posix(),
    SCRIPT.relative_to(REPO).as_posix(),
    "no per-lemma or intermediate", "physical Sector A", "Pre-A",
)

R167_V2_2_COMPONENT_SCRIPT_SHA256 = (
    "d9d65080f84c0408200ba64c81449263cfd87095d8bdf1620211bc6fab6d1058",
    "74dc4a8758d204587963c4e41e720902fd0b66931c35024f7784adaaa09d0b38",
)
V1_3_FUTURE_CHECKPOINT_REQUIRED_TOKENS = (
    "R-167 v2.2", "EXP-000813", "R-168 v1.3", EXPLORATION_ID,
    *R167_V2_2_COMPONENT_SCRIPT_SHA256,
    "253/253", "154/154",
    PRIMARY_SCRIPT_SHA256,
    INDEPENDENT_SCRIPT_SHA256,
    R167_V2_1_PRIMARY,
    R167_V2_1_INDEPENDENT,
    R167_V2_1_INTEGRATED,
    PRIMARY.relative_to(REPO).as_posix(),
    INDEPENDENT.relative_to(REPO).as_posix(),
    SCRIPT.relative_to(REPO).as_posix(),
    "physical Sector A", "Pre-A",
)
V1_3_COMPONENT_COUNT_TOKEN_PAIRS = (
    ("407/407", "430/430"),
    ("423/423", "446/446"),
)

ROUND1_MANIFEST = (
    REPO / "strategy/pre-a-round1-frozen-quadratic-causal-admission-triage-manifest.json"
)
ADMISSION_FREEZE = (
    REPO / "strategy/pre-a-round1-admission-discriminator-freeze-260810-v1.0.json"
)
M0_MANIFEST = REPO / "strategy/pre-a-m0-established-low-energy-baseline-manifest.json"
M1_MANIFEST = (
    REPO / "strategy/pre-a-m1-current-production-functional-candidate-manifest.json"
)
M2_MANIFEST = REPO / "strategy/pre-a-pa-m2-ci8-rs-dual-lane-manifest.json"
M5_MANIFEST = REPO / "strategy/pre-a-pa-m5-nl3-sv-candidate-manifest.json"
INDEPENDENT_HASH_INPUTS = (
    INDEPENDENT,
    PRIMARY,
    MANIFEST,
    CERTIFICATE,
    ROUND1_MANIFEST,
    ADMISSION_FREEZE,
    M0_MANIFEST,
    M1_MANIFEST,
    M2_MANIFEST,
    M5_MANIFEST,
)


def repo_path(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def normalized_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(normalized_bytes(path)).hexdigest()


def artifact_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, Mapping):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, set):
        items = [json_safe(item) for item in value]
        return sorted(items, key=lambda item: json.dumps(item, sort_keys=True))
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def canonical_payload(value: Any) -> bytes:
    return json.dumps(
        json_safe(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(json_safe(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def compact_text(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower().replace("\\", ""))


def text_has(text: Any, token: Any) -> bool:
    return compact_text(token) in compact_text(text)


def as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _historical_core(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value.get(key)
        for key in EXPECTED_HISTORICAL_CHECKPOINT_CORE
    }


def _confined_checkpoint_path(raw: Any, suffix: str) -> Path | None:
    if not isinstance(raw, str) or not raw or "\\" in raw:
        return None
    pure = Path(raw)
    if pure.is_absolute() or pure.as_posix() != raw or any(part in {"", ".", ".."} for part in pure.parts):
        return None
    candidate = (REPO / pure).resolve()
    try:
        candidate.relative_to(REPO.resolve())
    except ValueError:
        return None
    if not candidate.as_posix().endswith(suffix):
        return None
    return candidate


def historical_checkpoint_lifecycle_diagnostics(
    synthesis: Mapping[str, Any],
) -> dict[str, Any]:
    """Strictly revalidate the issued v1.9/v1.0 shared checkpoint."""

    diagnostics: dict[str, Any] = {
        "metadata_core_exact": _historical_core(synthesis)
        == EXPECTED_HISTORICAL_CHECKPOINT_CORE,
        "expected_metadata_core": EXPECTED_HISTORICAL_CHECKPOINT_CORE,
        "r168_history_label_exact": set(synthesis)
        == set(EXPECTED_HISTORICAL_CHECKPOINT_CORE)
        | {"v1_1_pdf_policy", "v1_2_pdf_policy"}
        and text_has(synthesis.get("v1_1_pdf_policy", ""), "No intermediate R-168 v1.1 PDF")
        and text_has(synthesis.get("v1_1_pdf_policy", ""), "later logical gate-level synthesis")
        and text_has(synthesis.get("v1_1_pdf_policy", ""), "formal, independent and integrated verification")
        and text_has(synthesis.get("v1_2_pdf_policy", ""), "No intermediate R-168 v1.2 PDF")
        and text_has(synthesis.get("v1_2_pdf_policy", ""), "proof-first package")
        and text_has(synthesis.get("v1_2_pdf_policy", ""), "integrated verifier")
        and text_has(synthesis.get("v1_2_pdf_policy", ""), "now present")
        and text_has(synthesis.get("v1_2_pdf_policy", ""), "pending full render and release QA"),
        "shared_manifest_core_exact": False,
        "r167_history_label_exact": False,
        "shared_manifest_error": None,
        "source_exists": CHECKPOINT_SOURCE.is_file(),
        "pdf_exists": CHECKPOINT_PDF.is_file(),
        "source_sha256": None,
        "pdf_sha256": None,
        "source_mtime_ns": None,
        "pdf_mtime_ns": None,
        "pdf_fresh_relative_to_source": False,
        "source_missing_tokens": list(CHECKPOINT_REQUIRED_TOKENS),
        "pypdf_pages": None,
        "pypdf_nonempty_pages": None,
        "pypdf_missing_tokens": list(CHECKPOINT_REQUIRED_TOKENS),
        "pypdf_error": None,
        "pdfplumber_pages": None,
        "pdfplumber_nonempty_pages": None,
        "pdfplumber_missing_tokens": list(CHECKPOINT_REQUIRED_TOKENS),
        "pdfplumber_error": None,
    }

    try:
        other = json.loads(R167_MANIFEST.read_text(encoding="utf-8"))
        other_checkpoint = as_mapping(as_mapping(other).get("checkpoint_synthesis"))
        diagnostics["shared_manifest_core_exact"] = (
            _historical_core(other_checkpoint)
            == EXPECTED_HISTORICAL_CHECKPOINT_CORE
            == _historical_core(synthesis)
        )
        diagnostics["r167_history_label_exact"] = (
            set(other_checkpoint)
            == set(EXPECTED_HISTORICAL_CHECKPOINT_CORE) | {"historical_scope"}
            and text_has(other_checkpoint.get("historical_scope", ""), "Historical combined R-167 v1.9 / R-168 v1.0 checkpoint")
            and text_has(other_checkpoint.get("historical_scope", ""), "not a v2.0 issue")
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        diagnostics["shared_manifest_error"] = str(error)

    if diagnostics["source_exists"]:
        try:
            source_text = CHECKPOINT_SOURCE.read_text(encoding="utf-8")
            source_stat = CHECKPOINT_SOURCE.stat()
            diagnostics["source_sha256"] = artifact_sha256(CHECKPOINT_SOURCE)
            diagnostics["source_mtime_ns"] = source_stat.st_mtime_ns
            diagnostics["source_missing_tokens"] = [
                token for token in CHECKPOINT_REQUIRED_TOKENS if not text_has(source_text, token)
            ]
        except (OSError, UnicodeError) as error:
            diagnostics["source_read_error"] = str(error)

    if diagnostics["pdf_exists"]:
        try:
            pdf_stat = CHECKPOINT_PDF.stat()
            diagnostics["pdf_sha256"] = artifact_sha256(CHECKPOINT_PDF)
            diagnostics["pdf_mtime_ns"] = pdf_stat.st_mtime_ns
            diagnostics["pdf_fresh_relative_to_source"] = (
                diagnostics["source_mtime_ns"] is not None
                and pdf_stat.st_mtime_ns >= diagnostics["source_mtime_ns"]
            )
        except OSError as error:
            diagnostics["pdf_read_error"] = str(error)

        try:
            from pypdf import PdfReader

            reader = PdfReader(str(CHECKPOINT_PDF))
            texts = [(page.extract_text() or "") for page in reader.pages]
            joined = "\n".join(texts)
            diagnostics["pypdf_pages"] = len(texts)
            diagnostics["pypdf_nonempty_pages"] = sum(bool(item.strip()) for item in texts)
            diagnostics["pypdf_missing_tokens"] = [
                token for token in CHECKPOINT_REQUIRED_TOKENS if not text_has(joined, token)
            ]
        except Exception as error:
            diagnostics["pypdf_error"] = f"{type(error).__name__}: {error}"

        try:
            import pdfplumber

            with pdfplumber.open(CHECKPOINT_PDF) as document:
                texts = [(page.extract_text() or "") for page in document.pages]
            joined = "\n".join(texts)
            diagnostics["pdfplumber_pages"] = len(texts)
            diagnostics["pdfplumber_nonempty_pages"] = sum(bool(item.strip()) for item in texts)
            diagnostics["pdfplumber_missing_tokens"] = [
                token for token in CHECKPOINT_REQUIRED_TOKENS if not text_has(joined, token)
            ]
        except Exception as error:
            diagnostics["pdfplumber_error"] = f"{type(error).__name__}: {error}"

    diagnostics["valid"] = (
        diagnostics["metadata_core_exact"]
        and diagnostics["r168_history_label_exact"]
        and diagnostics["shared_manifest_core_exact"]
        and diagnostics["r167_history_label_exact"]
        and diagnostics["source_exists"]
        and diagnostics["pdf_exists"]
        and diagnostics["source_sha256"] == CHECKPOINT_SOURCE_SHA256
        and diagnostics["pdf_sha256"] == CHECKPOINT_PDF_SHA256
        and diagnostics["pdf_fresh_relative_to_source"]
        and diagnostics["source_missing_tokens"] == []
        and diagnostics["pypdf_error"] is None
        and diagnostics["pypdf_pages"] == CHECKPOINT_PAGES
        and diagnostics["pypdf_nonempty_pages"] == CHECKPOINT_PAGES
        and diagnostics["pypdf_missing_tokens"] == []
        and diagnostics["pdfplumber_error"] is None
        and diagnostics["pdfplumber_pages"] == CHECKPOINT_PAGES
        and diagnostics["pdfplumber_nonempty_pages"] == CHECKPOINT_PAGES
        and diagnostics["pdfplumber_missing_tokens"] == []
    )
    return diagnostics


def issued_checkpoint_lifecycle_diagnostics(
    synthesis: Mapping[str, Any],
    *,
    other_field: str,
    required_tokens: tuple[str, ...],
    workflow_versions: tuple[str, str],
) -> dict[str, Any]:
    """Strictly validate one already-issued or future shared checkpoint."""

    diagnostics: dict[str, Any] = {
        "metadata": dict(synthesis),
        "shared_manifest_exact": False,
        "shared_manifest_error": None,
        "issued_metadata": False,
        "source_path_valid": False,
        "pdf_path_valid": False,
        "paired_paths": False,
        "declared_hashes_valid": False,
        "declared_pages_positive": False,
        "workflow_exact_scope": False,
        "visual_qa_declared": False,
        "source_exists": False,
        "pdf_exists": False,
        "source_sha256": None,
        "pdf_sha256": None,
        "source_mtime_ns": None,
        "pdf_mtime_ns": None,
        "pdf_fresh_relative_to_source": False,
        "source_missing_tokens": list(required_tokens),
        "pypdf_pages": None,
        "pypdf_nonempty_pages": None,
        "pypdf_missing_tokens": list(required_tokens),
        "pypdf_error": None,
        "pdfplumber_pages": None,
        "pdfplumber_nonempty_pages": None,
        "pdfplumber_missing_tokens": list(required_tokens),
        "pdfplumber_error": None,
        "valid": False,
    }
    try:
        other = json.loads(R167_MANIFEST.read_text(encoding="utf-8"))
        other_checkpoint = as_mapping(as_mapping(other).get(other_field))
        diagnostics["shared_manifest_exact"] = (
            bool(synthesis) and dict(synthesis) == other_checkpoint
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        diagnostics["shared_manifest_error"] = str(error)

    required_fields = {
        "status", "source", "pdf", "source_sha256", "pdf_sha256", "pages",
        "workflow", "visual_qa",
    }
    diagnostics["issued_metadata"] = (
        set(synthesis) == required_fields
        and text_has(synthesis.get("status", ""), "ISSUED")
        and text_has(synthesis.get("status", ""), "GATE-LEVEL CHECKPOINT")
    )
    source = _confined_checkpoint_path(synthesis.get("source"), ".tex.txt")
    pdf = _confined_checkpoint_path(synthesis.get("pdf"), ".pdf")
    diagnostics["source_path_valid"] = source is not None
    diagnostics["pdf_path_valid"] = pdf is not None
    diagnostics["paired_paths"] = (
        source is not None
        and pdf is not None
        and source.with_suffix("").with_suffix(".pdf") == pdf
    )
    hash_re = re.compile(r"^[0-9a-f]{64}$")
    diagnostics["declared_hashes_valid"] = (
        isinstance(synthesis.get("source_sha256"), str)
        and hash_re.fullmatch(synthesis.get("source_sha256", "")) is not None
        and isinstance(synthesis.get("pdf_sha256"), str)
        and hash_re.fullmatch(synthesis.get("pdf_sha256", "")) is not None
    )
    pages = synthesis.get("pages")
    diagnostics["declared_pages_positive"] = (
        isinstance(pages, int) and not isinstance(pages, bool) and pages > 0
    )
    diagnostics["workflow_exact_scope"] = all(
        text_has(synthesis.get("workflow", ""), token)
        for token in (
            "No per-lemma or intermediate", *workflow_versions,
            "primary", "independent", "integrated", "formal",
        )
    )
    diagnostics["visual_qa_declared"] = all(
        text_has(synthesis.get("visual_qa", ""), token)
        for token in (
            "All", "rendered pages", "clipping", "overlap", "pypdf", "pdfplumber"
        )
    )

    if source is not None and source.is_file():
        diagnostics["source_exists"] = True
        try:
            source_text = source.read_text(encoding="utf-8")
            diagnostics["source_sha256"] = artifact_sha256(source)
            diagnostics["source_mtime_ns"] = source.stat().st_mtime_ns
            diagnostics["source_missing_tokens"] = [
                token for token in required_tokens if not text_has(source_text, token)
            ]
        except (OSError, UnicodeError) as error:
            diagnostics["source_read_error"] = str(error)

    if pdf is not None and pdf.is_file():
        diagnostics["pdf_exists"] = True
        try:
            diagnostics["pdf_sha256"] = artifact_sha256(pdf)
            diagnostics["pdf_mtime_ns"] = pdf.stat().st_mtime_ns
            diagnostics["pdf_fresh_relative_to_source"] = (
                diagnostics["source_mtime_ns"] is not None
                and diagnostics["pdf_mtime_ns"] >= diagnostics["source_mtime_ns"]
            )
        except OSError as error:
            diagnostics["pdf_read_error"] = str(error)
        try:
            from pypdf import PdfReader

            texts = [
                (page.extract_text() or "")
                for page in PdfReader(str(pdf)).pages
            ]
            joined = "\n".join(texts)
            diagnostics["pypdf_pages"] = len(texts)
            diagnostics["pypdf_nonempty_pages"] = sum(
                bool(item.strip()) for item in texts
            )
            diagnostics["pypdf_missing_tokens"] = [
                token for token in required_tokens if not text_has(joined, token)
            ]
        except Exception as error:
            diagnostics["pypdf_error"] = f"{type(error).__name__}: {error}"
        try:
            import pdfplumber

            with pdfplumber.open(pdf) as document:
                texts = [(page.extract_text() or "") for page in document.pages]
            joined = "\n".join(texts)
            diagnostics["pdfplumber_pages"] = len(texts)
            diagnostics["pdfplumber_nonempty_pages"] = sum(
                bool(item.strip()) for item in texts
            )
            diagnostics["pdfplumber_missing_tokens"] = [
                token for token in required_tokens if not text_has(joined, token)
            ]
        except Exception as error:
            diagnostics["pdfplumber_error"] = f"{type(error).__name__}: {error}"

    diagnostics["valid"] = (
        diagnostics["shared_manifest_exact"]
        and diagnostics["issued_metadata"]
        and diagnostics["source_path_valid"]
        and diagnostics["pdf_path_valid"]
        and diagnostics["paired_paths"]
        and diagnostics["declared_hashes_valid"]
        and diagnostics["declared_pages_positive"]
        and diagnostics["workflow_exact_scope"]
        and diagnostics["visual_qa_declared"]
        and diagnostics["source_exists"]
        and diagnostics["pdf_exists"]
        and diagnostics["source_sha256"] == synthesis.get("source_sha256")
        and diagnostics["pdf_sha256"] == synthesis.get("pdf_sha256")
        and diagnostics["pdf_fresh_relative_to_source"]
        and diagnostics["source_missing_tokens"] == []
        and diagnostics["pypdf_error"] is None
        and diagnostics["pypdf_pages"] == pages
        and diagnostics["pypdf_nonempty_pages"] == pages
        and diagnostics["pypdf_missing_tokens"] == []
        and diagnostics["pdfplumber_error"] is None
        and diagnostics["pdfplumber_pages"] == pages
        and diagnostics["pdfplumber_nonempty_pages"] == pages
        and diagnostics["pdfplumber_missing_tokens"] == []
    )
    return diagnostics


def future_checkpoint_pair_diagnostics(
    synthesis: Mapping[str, Any],
) -> dict[str, Any]:
    """Cross-bind the R-168 v1.2 and R-167 v2.1 checkpoint lifecycle."""

    other_checkpoint: dict[str, Any] = {}
    error: str | None = None
    try:
        other = json.loads(R167_MANIFEST.read_text(encoding="utf-8"))
        other_checkpoint = as_mapping(other.get(R167_NEXT_CHECKPOINT_FIELD))
    except (OSError, UnicodeError, json.JSONDecodeError) as caught:
        error = str(caught)
    deferred_keys = {"status", "pdf_issued", "statement"}
    deferred_pair_valid = (
        set(synthesis) == deferred_keys
        and set(other_checkpoint) == deferred_keys
        and synthesis.get("status") == other_checkpoint.get("status")
        == "DEFERRED DURING PROOF-FIRST DEVELOPMENT"
        and synthesis.get("pdf_issued") is False
        and other_checkpoint.get("pdf_issued") is False
        and text_has(synthesis.get("statement", ""), "No v1.2 PDF")
        and text_has(other_checkpoint.get("statement", ""), "No v2.1 PDF")
        and text_has(synthesis.get("statement", ""), "later logical gate-level synthesis")
        and text_has(other_checkpoint.get("statement", ""), "later logical gate-level synthesis")
    )
    issued = issued_checkpoint_lifecycle_diagnostics(
        synthesis,
        other_field=R167_NEXT_CHECKPOINT_FIELD,
        required_tokens=NEXT_CHECKPOINT_REQUIRED_TOKENS,
        workflow_versions=("R-167 v2.1", "R-168 v1.2"),
    )
    return {
        "r168_field": NEXT_CHECKPOINT_FIELD,
        "r167_field": R167_NEXT_CHECKPOINT_FIELD,
        "r168_metadata": dict(synthesis),
        "r167_metadata": other_checkpoint,
        "shared_manifest_error": error,
        "deferred_pair_valid": deferred_pair_valid,
        "issued": issued,
        "valid": issued["valid"],
    }


def _checkpoint_reader_texts(synthesis: Mapping[str, Any]) -> dict[str, str]:
    texts = {"source": "", "pypdf": "", "pdfplumber": ""}
    source = _confined_checkpoint_path(synthesis.get("source"), ".tex.txt")
    pdf = _confined_checkpoint_path(synthesis.get("pdf"), ".pdf")
    if source is not None and source.is_file():
        try:
            texts["source"] = source.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            pass
    if pdf is not None and pdf.is_file():
        try:
            from pypdf import PdfReader

            texts["pypdf"] = "\n".join(
                page.extract_text() or "" for page in PdfReader(str(pdf)).pages
            )
        except Exception:
            pass
        try:
            import pdfplumber

            with pdfplumber.open(pdf) as document:
                texts["pdfplumber"] = "\n".join(
                    page.extract_text() or "" for page in document.pages
                )
        except Exception:
            pass
    return texts


def future_v1_3_checkpoint_diagnostics(synthesis: Mapping[str, Any]) -> dict[str, Any]:
    other_checkpoint: dict[str, Any] = {}
    error: str | None = None
    try:
        other = json.loads(R167_MANIFEST.read_text(encoding="utf-8"))
        other_checkpoint = as_mapping(other.get("v2_2_checkpoint_synthesis"))
    except (OSError, UnicodeError, json.JSONDecodeError) as caught:
        error = str(caught)
    deferred = (
        set(synthesis) == {
            "status", "source", "pdf", "source_sha256", "pdf_sha256", "pages", "workflow"
        }
        and set(other_checkpoint) == {"status", "workflow"}
        and synthesis.get("status") == other_checkpoint.get("status") == "DEFERRED"
        and all(synthesis.get(key) is None for key in (
            "source", "pdf", "source_sha256", "pdf_sha256", "pages"
        ))
        and text_has(synthesis.get("workflow", ""), "No v1.3 PDF")
        and text_has(synthesis.get("workflow", ""), "later combined gate-level synthesis")
        and text_has(other_checkpoint.get("workflow", ""), "No intermediate PDF")
        and text_has(other_checkpoint.get("workflow", ""), "R-167 v2.2")
        and text_has(other_checkpoint.get("workflow", ""), "one combined gate-level synthesis")
    )
    issued = issued_checkpoint_lifecycle_diagnostics(
        synthesis,
        other_field="v2_2_checkpoint_synthesis",
        required_tokens=V1_3_FUTURE_CHECKPOINT_REQUIRED_TOKENS,
        workflow_versions=("R-167 v2.2", "R-168 v1.3"),
    )
    reader_texts = _checkpoint_reader_texts(synthesis)
    count_contract = {
        label: any(
            all(text_has(value, token) for token in pair)
            for pair in V1_3_COMPONENT_COUNT_TOKEN_PAIRS
        )
        for label, value in reader_texts.items()
    }
    issued["r168_count_contract"] = count_contract
    issued["r168_count_contract_valid"] = (
        bool(reader_texts["source"]) and all(count_contract.values())
    )
    issued["valid"] = issued["valid"] and issued["r168_count_contract_valid"]
    return {
        "r168_field": "v1_3_checkpoint_synthesis",
        "r167_field": "v2_2_checkpoint_synthesis",
        "r168_metadata": dict(synthesis),
        "r167_metadata": other_checkpoint,
        "shared_manifest_error": error,
        "deferred_pair_valid": deferred,
        "issued": issued,
        "valid": issued["valid"],
    }


class Audit:
    """Separate contradictions from not-yet-issued staged authorities."""

    def __init__(self, staged: bool) -> None:
        self.staged = staged
        self.rows: list[dict[str, Any]] = []
        self.failures: list[str] = []
        self.missing: list[str] = []

    def _row(
        self, name: str, status: str, actual: Any, expected: Any, group: str
    ) -> None:
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": status,
                "actual": json_safe(actual),
                "expected": json_safe(expected),
            }
        )

    def check(
        self, name: str, condition: bool, actual: Any, expected: Any, group: str
    ) -> bool:
        if condition:
            self._row(name, "PASS", actual, expected, group)
            return True
        self._row(name, "FAIL", actual, expected, group)
        self.failures.append(f"{group}: {name}")
        return False

    def pending(
        self, name: str, condition: bool, actual: Any, expected: Any, group: str
    ) -> bool:
        if condition:
            self._row(name, "PASS", actual, expected, group)
            return True
        if self.staged:
            self._row(name, "MISSING", actual, expected, group)
            self.missing.append(f"{group}: {name}")
            return False
        return self.check(name, False, actual, expected, group)

    @property
    def verdict(self) -> str:
        if self.failures:
            return "FAIL"
        if self.missing:
            return "INCOMPLETE"
        return "PASS"


def load_json(
    path: Path, audit: Audit, label: str, *, core: bool = False
) -> dict[str, Any] | None:
    reporter = audit.check if core else audit.pending
    if not path.is_file():
        reporter(f"{label} exists", False, repo_path(path), "file", "files")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        audit.check(f"{label} parses", False, str(error), "valid JSON", "files")
        return None
    if not isinstance(value, dict):
        audit.check(f"{label} object", False, type(value).__name__, "dict", "files")
        return None
    reporter(f"{label} parses", True, repo_path(path), "dict", "files")
    return value


def read_text(
    path: Path, audit: Audit, label: str, *, core: bool = False
) -> str | None:
    reporter = audit.check if core else audit.pending
    if not path.is_file():
        reporter(f"{label} exists", False, repo_path(path), "file", "files")
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        audit.check(f"{label} UTF-8", False, str(error), "readable UTF-8", "files")
        return None
    reporter(f"{label} nonempty", bool(text), len(text), ">0", "files")
    return text


def jsonl_records(
    path: Path, audit: Audit, label: str
) -> list[dict[str, Any]] | None:
    if not path.is_file():
        audit.pending(f"{label} exists", False, repo_path(path), "file", "formal")
        return None
    records: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"line {line_number} is not an object")
                records.append(value)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        audit.check(f"{label} parses", False, str(error), "valid JSONL", "formal")
        return None
    audit.check(f"{label} parses", bool(records), len(records), ">=1", "formal")
    return records


def require_tokens(
    text: Any,
    label: str,
    tokens: Iterable[str],
    audit: Audit,
    *,
    core: bool = False,
    group: str = "formal",
) -> None:
    missing = [token for token in tokens if not text_has(text, token)]
    reporter = audit.check if core else audit.pending
    reporter(
        f"{label} required tokens",
        not missing,
        missing,
        "all required tokens present",
        group,
    )


def heading_section(text: str, identifier: str) -> str | None:
    lines = text.splitlines()
    start: int | None = None
    level = 0
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+", line)
        if match and identifier in line:
            start = index
            level = len(match.group(1))
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        match = re.match(r"^(#{1,6})\s+", lines[index])
        if match and len(match.group(1)) <= level:
            end = index
            break
    return "\n".join(lines[start:end])


def _normalize_fixture_hashes(value: Any) -> Any:
    """Normalize only mutable hashes in the explicitly syntax-only fixture."""

    if isinstance(value, dict):
        return {
            key: "<CURRENT-FIXTURE-SHA256>"
            if key == "sha256"
            else _normalize_fixture_hashes(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_normalize_fixture_hashes(item) for item in value]
    return value


def invocation_view(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    """Remove CLI-only state and mutable syntax-fixture hashes.

    ``authority.staged`` records CLI mode.  The live local ``freeze/*`` tag
    observation is informational.  The minimum-contract positive fixture
    deliberately hashes the current proof scripts and stored run oracles;
    those hashes test syntax/existence only and include the result files being
    refreshed, so their values are normalized while every theorem, identity,
    path, role, result key, formal binding, and non-fixture hash remains exact.
    """

    if payload is None:
        return None
    copied = json.loads(json.dumps(payload))
    for authority_field in ("authority", "formal_authority"):
        authority = copied.get(authority_field)
        if isinstance(authority, dict):
            authority.pop("staged", None)
    current_tree = copied.get("current_tree")
    if isinstance(current_tree, dict):
        current_tree.pop("local_freeze_tag_observation", None)
    fixture_field = "m2_physical_response_successor_minimum_contract_fixture"
    if fixture_field in copied:
        copied[fixture_field] = _normalize_fixture_hashes(copied[fixture_field])
    assertions = copied.get("assertions")
    if isinstance(assertions, list):
        for assertion in assertions:
            if (
                isinstance(assertion, dict)
                and assertion.get("group") == "physical_contract"
                and isinstance(assertion.get("name"), str)
                and (
                    assertion["name"].startswith("minimum contract")
                    or assertion["name"] == "independent error sum strict"
                )
            ):
                for field in ("actual", "expected"):
                    if field in assertion:
                        assertion[field] = _normalize_fixture_hashes(
                            assertion[field]
                        )
    return copied


def run_once(
    component: Path, directory: Path, audit: Audit, label: str
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    if not component.is_file():
        audit.check(
            f"{label} script exists",
            False,
            repo_path(component),
            "file",
            "freshness",
        )
        return None
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / "result.json"
    command = [
        sys.executable,
        "-X",
        "utf8",
        str(component),
        "--output",
        str(output),
    ]
    if audit.staged:
        command.append("--staged")
    completed = subprocess.run(
        command,
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=240,
    )
    if completed.returncode != 0 or not output.is_file():
        audit.check(
            f"{label} execution",
            False,
            {
                "returncode": completed.returncode,
                "stdout": completed.stdout[-2000:],
                "stderr": completed.stderr[-2000:],
                "output_exists": output.is_file(),
            },
            "CLI child exits zero and writes JSON",
            "freshness",
        )
        return None
    try:
        payload = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        audit.check(f"{label} JSON", False, str(error), "valid JSON", "freshness")
        return None
    if not isinstance(payload, dict):
        audit.check(
            f"{label} object", False, type(payload).__name__, "dict", "freshness"
        )
        return None
    first_line = next(
        (line.strip() for line in completed.stdout.splitlines() if line.strip()), ""
    )
    sentinel_match = re.match(
        r"^(PASS|STAGED|INCOMPLETE)\s+(\d+)/(\d+)(?:\s+\||$)", first_line
    )
    sentinel = {
        "status": sentinel_match.group(1) if sentinel_match else None,
        "passed": int(sentinel_match.group(2)) if sentinel_match else None,
        "total": int(sentinel_match.group(3)) if sentinel_match else None,
    }
    audit.check(f"{label} execution", True, completed.returncode, 0, "freshness")
    audit.check(
        f"{label} normalized CLI sentinel",
        sentinel_match is not None,
        first_line,
        "PASS|STAGED|INCOMPLETE count/count",
        "freshness",
    )
    return payload, sentinel


def run_fresh_pair(
    component: Path, temporary: Path, audit: Audit, label: str
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    first = run_once(component, temporary / f"{label}-a", audit, f"{label} A")
    second = run_once(component, temporary / f"{label}-b", audit, f"{label} B")
    if first is None or second is None:
        audit.check(
            f"{label} two fresh runs",
            False,
            [first is not None, second is not None],
            [True, True],
            "freshness",
        )
        return first or second
    first_raw = canonical_payload(first[0])
    second_raw = canonical_payload(second[0])
    first_view = canonical_payload(invocation_view(first[0]))
    second_view = canonical_payload(invocation_view(second[0]))
    audit.check(
        f"{label} exact deterministic payload",
        first_raw == second_raw,
        {
            "a": hashlib.sha256(first_raw).hexdigest(),
            "b": hashlib.sha256(second_raw).hexdigest(),
        },
        "equal canonical hashes",
        "freshness",
    )
    audit.check(
        f"{label} normalized deterministic payload",
        first_view == second_view and first[1] == second[1],
        {
            "a": hashlib.sha256(first_view).hexdigest(),
            "b": hashlib.sha256(second_view).hexdigest(),
            "sentinels": [first[1], second[1]],
        },
        "equal normalized hashes and sentinels",
        "freshness",
    )
    authority_field = (
        "authority" if isinstance(first[0].get("authority"), dict) else "formal_authority"
    )
    authority = as_mapping(first[0].get(authority_field))
    if authority:
        audit.check(
            f"{label} staged invocation metadata explicit",
            authority.get("staged") is audit.staged,
            authority.get("staged"),
            audit.staged,
            "freshness",
        )
        normalized_authority = as_mapping(
            as_mapping(invocation_view(first[0])).get(authority_field)
        )
        audit.check(
            f"{label} normalization removes staged flag",
            "staged" not in normalized_authority,
            normalized_authority,
            f"{authority_field} without staged",
            "freshness",
        )
    normalized = invocation_view(first[0]) or {}
    audit.check(
        f"{label} normalization removes non-load-bearing live tags",
        "local_freeze_tag_observation"
        not in as_mapping(normalized.get("current_tree")),
        as_mapping(normalized.get("current_tree")),
        "current tree without live tag observation",
        "freshness",
    )
    return first


def stored_against_fresh(
    path: Path, fresh: dict[str, Any] | None, audit: Audit, label: str
) -> dict[str, Any] | None:
    if not path.is_file():
        audit.pending(
            f"{label} stored result exists",
            False,
            repo_path(path),
            "fresh-equal JSON",
            "freshness",
        )
        return None
    try:
        stored = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        audit.check(
            f"{label} stored parses", False, str(error), "valid JSON", "freshness"
        )
        return None
    if not isinstance(stored, dict):
        audit.check(
            f"{label} stored object",
            False,
            type(stored).__name__,
            "dict",
            "freshness",
        )
        return None
    stored_view = canonical_payload(invocation_view(stored))
    fresh_view = canonical_payload(invocation_view(fresh)) if fresh is not None else b""
    # During assembly a pre-hardening stored payload is an explicitly staged
    # freshness omission.  Strict mode still turns the same mismatch into a
    # failure through ``pending``; no stale payload can pass release mode.
    audit.pending(
        f"{label} stored equals fresh",
        fresh is not None and stored_view == fresh_view,
        {
            "stored": hashlib.sha256(stored_view).hexdigest(),
            "fresh": hashlib.sha256(fresh_view).hexdigest() if fresh else None,
        },
        "equal canonical hashes after staged-flag normalization",
        "freshness",
    )
    return stored


def v1_3_issuance_firewall_diagnostics() -> dict[str, Any]:
    """Bind issued mutable authorities to the exact shared checkpoint contract."""

    diagnostics: dict[str, Any] = {
        "checkpoint": {},
        "deferred_pair_valid": False,
        "issued_checkpoint_valid": False,
        "certificate_readable": False,
        "certificate_tokens": {},
        "certificate_issuance_valid": False,
    }
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        synthesis = as_mapping(manifest.get("v1_3_checkpoint_synthesis"))
        checkpoint = future_v1_3_checkpoint_diagnostics(synthesis)
        diagnostics["checkpoint"] = checkpoint
        diagnostics["deferred_pair_valid"] = checkpoint["deferred_pair_valid"]
        diagnostics["issued_checkpoint_valid"] = checkpoint["valid"]
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError) as error:
        diagnostics["checkpoint_error"] = f"{type(error).__name__}: {error}"
        return diagnostics

    if not diagnostics["issued_checkpoint_valid"]:
        return diagnostics

    try:
        certificate = CERTIFICATE.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        diagnostics["certificate_error"] = f"{type(error).__name__}: {error}"
        return diagnostics
    diagnostics["certificate_readable"] = True

    metadata = as_mapping(
        as_mapping(diagnostics["checkpoint"]).get("r168_metadata")
    )
    source = _confined_checkpoint_path(metadata.get("source"), ".tex.txt")
    pdf = _confined_checkpoint_path(metadata.get("pdf"), ".pdf")
    pages = metadata.get("pages")
    if source is None or pdf is None or not source.is_file() or not pdf.is_file():
        diagnostics["certificate_artifact_error"] = "checkpoint artefact unavailable"
        return diagnostics

    component_contracts = (
        (
            "R-167 primary",
            REPO / R167_V2_1_PRIMARY,
            253,
        ),
        (
            "R-167 non-importing independent",
            REPO / R167_V2_1_INDEPENDENT,
            154,
        ),
        (
            "R-167 integrated",
            REPO / R167_V2_1_INTEGRATED,
            279,
        ),
        ("R-168 primary", PRIMARY, PRIMARY_FORMAL_ASSERTION_COUNT),
        (
            "R-168 non-importing independent",
            INDEPENDENT,
            INDEPENDENT_FORMAL_ASSERTION_COUNT,
        ),
        ("R-168 integrated", SCRIPT, 349),
    )
    component_tokens = {
        label: (
            path.is_file()
            and text_has(
                certificate,
                (
                    f"{label}: {count}/{count}; raw script SHA-256 "
                    f"{artifact_sha256(path)}"
                ),
            )
        )
        for label, path, count in component_contracts
    }
    source_token = text_has(
        certificate,
        (
            f"Source: {metadata.get('source')} ({source.stat().st_size} bytes; "
            f"raw SHA-256 {metadata.get('source_sha256')})"
        ),
    )
    pdf_token = text_has(
        certificate,
        (
            f"PDF: {metadata.get('pdf')} ({pdf.stat().st_size} bytes; raw SHA-256 "
            f"{metadata.get('pdf_sha256')}; {pages} pages"
        ),
    )
    qa_token = text_has(
        certificate,
        (
            f"pypdf {pages}/{pages} nonempty pages; pdfplumber {pages}/{pages} "
            f"nonempty pages; 77/77 required tokens in each extraction; all "
            f"{pages} rendered pages were visually reviewed with zero clipping, "
            "overlap, broken equations, unreadable identifiers, black glyphs, or "
            "malformed page transitions; the one-pass MiKTeX build reported "
            "OVERFULL-HBOX 0"
        ),
    )
    exact_tokens = {
        "heading": text_has(
            certificate,
            "Combined R-167 v2.2 / R-168 v1.3 gate-level checkpoint issuance",
        ),
        "proof_first_superseded_only_at_checkpoint": text_has(
            certificate,
            "superseded for the current result by this single gate-level issuance",
        ),
        "source_pin": source_token,
        "pdf_pin_and_pages": pdf_token,
        "component_counts_and_pins": all(component_tokens.values()),
        "dual_extraction_and_visual_qa": qa_token,
        "single_checkpoint_workflow": text_has(
            certificate,
            (
                "issued one combined source/PDF pair only after the primary, "
                "non-importing independent, integrated, formal-authority, "
                "generated-surface, source-form, freshness, dual-extraction, "
                "and visual-review checks passed"
            ),
        ),
        "parents_remain_open": text_has(
            certificate,
            (
                "physical-response, prospective-freeze, Round-1, C6, CP1, "
                "physical Sector A, and Pre-A parents remain OPEN"
            ),
        ),
    }
    diagnostics["certificate_tokens"] = {
        **exact_tokens,
        "components": component_tokens,
    }
    diagnostics["certificate_issuance_valid"] = (
        all(exact_tokens.values())
        and CERTIFICATE.read_bytes().count(b"\r") == 0
    )
    return diagnostics


def validate_firewall(audit: Audit) -> None:
    for label, path, expected in (
        ("primary", PRIMARY, PRIMARY_SCRIPT_SHA256),
        ("independent", INDEPENDENT, INDEPENDENT_SCRIPT_SHA256),
    ):
        raw = artifact_sha256(path)
        normalized = normalized_sha256(path)
        audit.check(
            f"{label} frozen v1.3 raw and LF-normalized SHA exact",
            raw == normalized == expected,
            {"raw": raw, "LF_normalized": normalized},
            {"raw": expected, "LF_normalized": expected},
            "firewall",
        )

    lifecycle = v1_3_issuance_firewall_diagnostics()
    issued_guard = (
        lifecycle["issued_checkpoint_valid"]
        and lifecycle["certificate_issuance_valid"]
    )
    for label, path, deferred_hash in (
        ("manifest", MANIFEST, MANIFEST_SHA256),
        ("certificate", CERTIFICATE, CERTIFICATE_SHA256),
    ):
        raw = artifact_sha256(path)
        normalized = normalized_sha256(path)
        deferred_exact = (
            lifecycle["deferred_pair_valid"]
            and raw == normalized == deferred_hash
        )
        issued_exact = issued_guard and raw == normalized
        audit.check(
            f"{label} v1.3 deferred hash or issued lifecycle exact",
            deferred_exact or issued_exact,
            {
                "raw": raw,
                "LF_normalized": normalized,
                "deferred_exact": deferred_exact,
                "issued_exact": issued_exact,
                "lifecycle": lifecycle,
            },
            {
                "deferred": {
                    "raw": deferred_hash,
                    "LF_normalized": deferred_hash,
                    "cross_bound": True,
                },
                "issued": {
                    "shared_exact_8_field_checkpoint": True,
                    "certificate_issuance_tokens_exact": True,
                    "raw_equals_LF_normalized": True,
                },
            },
            "firewall",
        )
    source = read_text(INDEPENDENT, audit, "independent source", core=True)
    if source is None:
        return
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        audit.check("independent AST parses", False, str(error), "valid AST", "firewall")
        return
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    primary_module = PRIMARY.stem
    forbidden = [
        name
        for name in imports
        if primary_module in name or name in {"importlib", "runpy"}
    ]
    audit.check("independent AST import firewall", not forbidden, forbidden, [], "firewall")
    literals = [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    primary_run_fragment = f"2026-08-11-primary-{SLUG}"
    primary_run_literals = [
        value for value in literals if primary_run_fragment in value
    ]
    fixture_functions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "synthetic_physical_response_contract_independent"
    ]
    fixture_literals = [
        node.value
        for function in fixture_functions
        for node in ast.walk(function)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and primary_run_fragment in node.value
    ]
    audit.check(
        "independent primary-result theorem firewall with syntax-fixture exception",
        len(fixture_functions) == 1
        and primary_run_literals == fixture_literals
        and len(primary_run_literals) == 1
        and primary_run_literals[0]
        == (
            "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-11-primary-"
            "pre-a-round1-prospective-holdout-freeze-protocol/result.json"
        ),
        {
            "all_primary_run_literals": primary_run_literals,
            "fixture_primary_run_literals": fixture_literals,
        },
        "one exact syntax-only fixture literal and none elsewhere",
        "firewall",
    )

    integrated_source = SCRIPT.read_text(encoding="utf-8")
    integrated_tree = ast.parse(integrated_source)
    integrated_imports: list[str] = []
    for node in ast.walk(integrated_tree):
        if isinstance(node, ast.Import):
            integrated_imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            integrated_imports.append(node.module or "")
    audit.check(
        "integrated CLI-only component execution",
        "subprocess.run" in integrated_source
        and all(
            name not in {"importlib", "runpy", primary_module, INDEPENDENT.stem}
            for name in integrated_imports
        ),
        integrated_imports,
        "subprocess CLI with no component/importlib/runpy import",
        "firewall",
    )


def expected_component_assertion_count(payload: Mapping[str, Any], label: str) -> int:
    field = "formal_authority" if label == "primary" else "authority"
    complete = as_mapping(payload.get(field)).get("status") == "COMPLETE"
    if label == "primary":
        return PRIMARY_FORMAL_ASSERTION_COUNT if complete else PRIMARY_PROOF_FIRST_ASSERTION_COUNT
    return INDEPENDENT_FORMAL_ASSERTION_COUNT if complete else INDEPENDENT_PROOF_FIRST_ASSERTION_COUNT


def validate_component(
    payload: dict[str, Any], label: str, schema: str, expected_count: int, audit: Audit
) -> None:
    expected = {
        "schema": schema,
        "task_id": TASK_ID,
        "claim_ids": list(CLAIM_IDS),
        "claim_bearing": False,
        "exploration_id": EXPLORATION_ID,
        "prior_exploration_ids": list(PRIOR_EXPLORATION_IDS),
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "negative_ids": list(NEGATIVE_IDS),
        "prior_negative_ids": list(PRIOR_NEGATIVE_IDS),
        "new_negative_ids": list(NEW_NEGATIVE_IDS),
        "reused_negative_ids": list(REUSED_NEGATIVE_IDS),
        "closed_subgates": list(CLOSED_SUBGATES),
        "new_closed_subgates": list(NEW_CLOSED_SUBGATES),
        "open_gates": list(OPEN_GATES),
        "parent_gate": PARENT_GATE,
    }
    for field, value in expected.items():
        audit.check(
            f"{label} exact {field}",
            payload.get(field) == value,
            payload.get(field),
            value,
            "component",
        )
    allowed = {"PASS", "INCOMPLETE", "STAGED"} if audit.staged else {"PASS"}
    audit.check(
        f"{label} verdict",
        payload.get("verdict") in allowed,
        payload.get("verdict"),
        sorted(allowed),
        "component",
    )
    assertions = [row for row in as_list(payload.get("assertions")) if isinstance(row, dict)]
    summary = as_mapping(payload.get("summary"))
    audit.check(
        f"{label} exact assertion count",
        len(assertions) == expected_count
        and summary.get("failed") == 0
        and summary.get("passed") == len(assertions)
        and summary.get("total") == len(assertions)
        and all(row.get("status") == "PASS" for row in assertions),
        {"rows": len(assertions), "summary": summary},
        {"rows": expected_count, "failed": 0, "all": "PASS"},
        "component",
    )
    assertion_names = {str(row.get("name")) for row in assertions}
    required_firewall_names = {
        "candidate prediction bound",
        "target fields exact" if label == "primary" else "synthetic target order",
        "commitment fields exact" if label == "primary" else "synthetic commitment order",
        "prediction fields exact" if label == "primary" else "synthetic prediction order",
        "allowed-input fields exact" if label == "primary" else "synthetic input order",
        "robustness fields exact" if label == "primary" else "synthetic robustness order",
        "live tag observation is non-load-bearing"
        if label == "primary"
        else "live freeze-tag observation non-load-bearing",
    }
    audit.check(
        f"{label} firewall assertions present",
        required_firewall_names <= assertion_names,
        sorted(required_firewall_names - assertion_names),
        [],
        "component",
    )
    scope = as_mapping(payload.get("scope"))
    expected_scope = (
        PRIMARY_SCOPE_EXPECTED if label == "primary" else INDEPENDENT_SCOPE_EXPECTED
    )
    audit.check(
        f"{label} all scope booleans exact",
        scope == expected_scope
        and all(isinstance(value, bool) for value in scope.values()),
        scope,
        expected_scope,
        "component",
    )


def validate_fresh_sentinel(
    sentinel: Mapping[str, Any], label: str, expected_count: int, audit: Audit
) -> None:
    expected_statuses = {"PASS", "STAGED"} if audit.staged else {"PASS"}
    audit.check(
        f"{label} fresh-twice exact CLI count",
        sentinel.get("status") in expected_statuses
        and sentinel.get("passed") == expected_count
        and sentinel.get("total") == expected_count,
        dict(sentinel),
        {
            "status": sorted(expected_statuses),
            "passed": expected_count,
            "total": expected_count,
        },
        "freshness",
    )


def validate_source_hashes(
    payload: dict[str, Any], paths: Iterable[Path], audit: Audit, label: str
) -> None:
    expected = {repo_path(path): normalized_sha256(path) for path in paths}
    actual = as_mapping(payload.get("source_hashes"))
    audit.check(
        f"{label} source hashes exact", actual == expected, actual, expected, "freshness"
    )


def normalize_hostiles(payload: dict[str, Any], label: str) -> dict[str, Any]:
    raw = as_mapping(payload.get("hostile_fixtures"))
    return {name: as_mapping(raw.get(name)) for name in HOSTILE_CODES}


def _iter_artifact_refs(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        if set(value) == set(PHYSICAL_CONTRACT_ARTIFACT_REF_FIELDS):
            yield value
        for item in value.values():
            yield from _iter_artifact_refs(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_artifact_refs(item)


def _linear_probe_view(value: Any) -> dict[str, Any]:
    theorem = as_mapping(value)
    finite = as_mapping(theorem.get("finite_beta"))
    ground = as_mapping(theorem.get("beta_infinity"))
    return {
        "closed_child_id": theorem.get("closed_child_id"),
        "negative_id": theorem.get("negative_id"),
        "fixture": theorem.get("fixture"),
        "finite_beta": {
            key: finite.get(key)
            for key in (
                "free_energy_difference_at_step", "boltzmann_exponent_shift_at_step",
                "central_second_difference", "normalized_curvature_shift",
                "expected_shift",
            )
        },
        "beta_infinity": ground,
        "invariants": theorem.get("invariants"),
        "sign_convention": theorem.get("sign_convention"),
    }


def compare_v1_2(
    primary: dict[str, Any],
    independent: dict[str, Any],
    manifest: dict[str, Any],
    audit: Audit,
) -> dict[str, Any]:
    expected_fixture = {
        "beta": "3/2", "d_left": "5/7", "d_right": "11/7",
        "delta_d": "6/7", "probe_diagonal": ["1", "-1"],
        "source_step": "1/5", "two_level_gap": "4", "volume": "7",
    }
    expected_finite = {
        "free_energy_difference_at_step": "3/25",
        "boltzmann_exponent_shift_at_step": "-9/50",
        "central_second_difference": "6",
        "normalized_curvature_shift": "6/7",
        "expected_shift": "6/7",
    }
    expected_ground = {
        "branch_stable": True,
        "expected_shift": "6/7",
        "ground_branch_indices_minus_zero_plus": [0, 0, 0],
        "normalized_curvature_left": "5/7",
        "normalized_curvature_right": "11/7",
        "normalized_curvature_shift": "6/7",
    }
    expected_invariants = {
        "admitted_candidate_created": False,
        "physical_response_identified": False,
        "same_finite_torus_fingerprint": True,
        "same_first_source_derivative": True,
        "same_zero_source_hamiltonian": True,
        "same_zero_source_state_and_spectrum": True,
    }
    expected_linear = {
        "closed_child_id": V1_2_CLOSED_SUBGATES[0],
        "negative_id": V1_2_NEGATIVE_IDS[0],
        "fixture": expected_fixture,
        "finite_beta": expected_finite,
        "beta_infinity": expected_ground,
        "invariants": expected_invariants,
        "sign_convention": {
            "contract_literal": PHYSICAL_RESPONSE_SIGN_CONVENTION,
            "free_energy": "F_beta(J)=-beta^{-1} log Tr exp[-beta H(J)]",
            "helicity_like_response": "+V^{-1} d_J^2 F_beta(J)|J=0",
            "scalar_susceptibility": "-V^{-1} d_J^2 F_beta(J)|J=0",
        },
    }
    p_linear = _linear_probe_view(
        primary.get("m2_linear_probe_second_order_response_nonidentifiability")
    )
    i_linear = _linear_probe_view(
        independent.get("m2_linear_probe_second_order_response_nonidentifiability")
    )
    audit.check(
        "cross v1.2 exact linear-probe curvature theorem",
        p_linear == i_linear == expected_linear,
        {"primary": p_linear, "independent": i_linear},
        expected_linear,
        "cross_v1_2",
    )
    m_linear = as_mapping(
        manifest.get("m2_linear_probe_second_order_response_nonidentifiability")
    )
    m_fraction = as_mapping(m_linear.get("fraction_fixture"))
    audit.check(
        "manifest v1.2 exact curvature rationals branches and boundary",
        m_linear.get("closed_child_id") == V1_2_CLOSED_SUBGATES[0]
        and m_linear.get("negative_id") == V1_2_NEGATIVE_IDS[0]
        and m_linear.get("candidate_created") is False
        and m_linear.get("physical_response_gate_closed") is False
        and m_fraction
        == {
            "beta": "3/2", "boltzmann_exponent_shift_at_step": "-9/50",
            "d_left": "5/7", "d_right": "11/7", "delta_d": "6/7",
            "free_energy_difference_at_step": "3/25",
            "ground_branch_indices_minus_zero_plus": [0, 0, 0],
            "normalized_curvature_left": "5/7",
            "normalized_curvature_right": "11/7",
            "normalized_curvature_shift": "6/7", "source_step": "1/5",
            "volume": "7",
        }
        and as_mapping(m_linear.get("sign_convention")).get("helicity_like_response")
        == "+V^-1 d_J^2 F_beta(J)|J=0"
        and as_mapping(m_linear.get("sign_convention")).get("scalar_susceptibility")
        == "-V^-1 d_J^2 F_beta(J)|J=0",
        m_linear,
        "exact fraction fixture, stable branch [0,0,0], and response gate false",
        "cross_v1_2",
    )
    require_tokens(
        json.dumps(m_linear, sort_keys=True),
        "manifest v1.2 contact theorem and physical boundary",
        (
            "H_d(t,J)=H(t)-JQ", "+V^-1 partial_J^2 F_beta shifts by +d(t)",
            "scalar J*phi source", "not automatically", "compact or gauge action",
            "state/reference", "error budget",
        ),
        audit,
        core=True,
        group="cross_v1_2",
    )

    p_contract = as_mapping(
        primary.get("m2_physical_response_successor_minimum_contract_fixture")
    )
    i_contract = as_mapping(
        independent.get("m2_physical_response_successor_minimum_contract_fixture")
    )
    p_valid = primary.get(
        "m2_physical_response_successor_minimum_contract_validation"
    )
    i_valid = independent.get(
        "m2_physical_response_successor_minimum_contract_validation"
    )
    audit.check(
        "cross v1.2 independently reconstructed minimum contract exact",
        p_contract == i_contract
        and p_valid == i_valid == {"valid": True, "errors": [], "error_codes": []},
        {"fixture_equal": p_contract == i_contract, "primary": p_valid, "independent": i_valid},
        "equal positive fixture and two valid reports",
        "cross_v1_2",
    )
    audit.check(
        "cross v1.2 minimum contract root lifecycle and substantive delta exact",
        set(p_contract) == set(PHYSICAL_CONTRACT_ROOT_FIELDS)
        and len(p_contract) == len(PHYSICAL_CONTRACT_ROOT_FIELDS)
        and p_contract.get("schema") == PHYSICAL_CONTRACT_SCHEMA
        and p_contract.get("status") == "SCHEMA_FIXTURE_ONLY"
        and p_contract.get("fixture_only") is True
        and p_contract.get("candidate_created") is False
        and as_mapping(p_contract.get("version_delta")).get("classification")
        == "SUBSTANTIVE_NEW_VERSION"
        and set(as_list(as_mapping(p_contract.get("version_delta")).get("substantive_changes")))
        == set(PHYSICAL_CONTRACT_MANDATORY_CHANGES)
        and len(as_list(as_mapping(p_contract.get("version_delta")).get("substantive_changes")))
        == len(PHYSICAL_CONTRACT_MANDATORY_CHANGES)
        and "MICROSCOPIC_MAP_ONLY"
        not in as_list(as_mapping(p_contract.get("version_delta")).get("substantive_changes")),
        {
            "keys": list(p_contract),
            "schema": p_contract.get("schema"),
            "status": p_contract.get("status"),
            "version_delta": p_contract.get("version_delta"),
        },
        {
            "keys": PHYSICAL_CONTRACT_ROOT_FIELDS,
            "schema": PHYSICAL_CONTRACT_SCHEMA,
            "changes": PHYSICAL_CONTRACT_MANDATORY_CHANGES,
        },
        "cross_v1_2",
    )
    response = as_mapping(p_contract.get("response_definition"))
    estimand = as_mapping(p_contract.get("estimand_binding"))
    prediction = as_mapping(p_contract.get("critical_prediction"))
    control = as_mapping(p_contract.get("physical_control_map"))
    hard = as_mapping(p_contract.get("hard_row_rerun"))
    firewall = as_mapping(p_contract.get("prospective_firewall"))
    audit.check(
        "cross v1.2 response estimand prediction firewall and hard rows exact",
        response.get("kind") == "HELICITY_FREE_ENERGY_CURVATURE"
        and response.get("sign_convention") == PHYSICAL_RESPONSE_SIGN_CONVENTION
        and tuple(response.get("limit_order", ())) == PHYSICAL_CONTRACT_LIMIT_ORDER
        and response.get("common_estimand_id") == estimand.get("id")
        == prediction.get("estimand_id")
        and prediction.get("candidate_id") == p_contract.get("candidate_id")
        and prediction.get("target_blind") is True
        and control.get("target_blind") is True
        and hard.get("all_pass") is True
        and tuple(as_mapping(hard.get("rows"))) == HARD_ROWS
        and set(as_mapping(hard.get("rows")).values()) == {"PASS"}
        and firewall.get("target_value_present") is False
        and firewall.get("external_commitment_status")
        == firewall.get("remote_verification_status")
        == "REQUIRED_EXTERNAL_NOT_SUPPLIED",
        {
            "response": response,
            "estimand": estimand,
            "prediction": prediction,
            "control": control,
            "hard": hard,
            "firewall": firewall,
        },
        "helicity curvature, ordered limits, bound target-blind prediction, ten PASS rows, external inputs absent",
        "cross_v1_2",
    )
    budget = as_mapping(p_contract.get("error_budget"))
    terms = [as_mapping(item) for item in as_list(budget.get("terms"))]
    composites = [
        (
            as_mapping(term.get("script_ref")).get("path"),
            as_mapping(term.get("run_ref")).get("path"),
            term.get("result_key"),
        )
        for term in terms
    ]
    audit.check(
        "cross v1.2 exact six-term rational error budget and distinct evidence",
        tuple(term.get("id") for term in terms) == PHYSICAL_CONTRACT_ERROR_TERMS
        and all(term.get("bound") == "1/100" for term in terms)
        and budget.get("total_bound") == "3/50"
        and budget.get("acceptance_margin") == "1/10"
        and budget.get("strict_margin") is True
        and len(composites) == len(set(composites)) == 6,
        {"terms": terms, "composites": composites, "budget": budget},
        {
            "ids": PHYSICAL_CONTRACT_ERROR_TERMS,
            "bounds": ["1/100"] * 6,
            "total": "3/50",
            "margin": "1/10",
            "distinct": 6,
        },
        "cross_v1_2",
    )

    refs = list(_iter_artifact_refs(p_contract))
    role_counts: dict[str, int] = {}
    refs_valid = True
    for ref in refs:
        role = ref.get("role")
        role_counts[str(role)] = role_counts.get(str(role), 0) + 1
        raw_path = ref.get("path")
        if not isinstance(raw_path, str) or "\\" in raw_path:
            refs_valid = False
            continue
        candidate = REPO / raw_path
        refs_valid = (
            refs_valid
            and role in PHYSICAL_CONTRACT_ARTIFACT_ROLES
            and candidate.is_file()
            and ref.get("sha256") == normalized_sha256(candidate)
        )
    audit.check(
        "cross v1.2 all 31 role-bound artifact refs current",
        len(refs) == 31
        and refs_valid
        and role_counts
        == {
            "ERROR_RUN": 6, "ERROR_SCRIPT": 6, "PROOF": 3,
            "PHYSICAL_CONTROL_MAP": 2, "COMPACT_OR_GAUGE_ACTION": 2,
            "SOURCE_LAW": 2, "RESPONSE_MAP": 2, "STATE_EXISTENCE": 2,
            "RAW_ESTIMATOR": 1, "LINEAR_PROBE": 1, "QUADRATIC_CONTACT": 1,
            "VERIFIER_INDEPENDENT": 1, "VERIFIER_INTEGRATED": 1,
            "VERIFIER_PRIMARY": 1,
        },
        {"count": len(refs), "valid": refs_valid, "roles": role_counts},
        "31 current exact refs with declared roles and hashes",
        "cross_v1_2",
    )
    verification = as_mapping(p_contract.get("verification"))
    verifier_refs = {
        name: as_mapping(verification.get(name))
        for name in ("primary_ref", "independent_ref", "integrated_ref")
    }
    audit.check(
        "cross v1.2 distinct frozen verifier bindings exact",
        verifier_refs["primary_ref"].get("path") == repo_path(PRIMARY)
        and verifier_refs["primary_ref"].get("sha256") == PRIMARY_SCRIPT_SHA256
        and verifier_refs["independent_ref"].get("path") == repo_path(INDEPENDENT)
        and verifier_refs["independent_ref"].get("sha256") == INDEPENDENT_SCRIPT_SHA256
        and verifier_refs["integrated_ref"].get("path") == repo_path(SCRIPT)
        and verifier_refs["integrated_ref"].get("sha256") == normalized_sha256(SCRIPT)
        and len({ref.get("path") for ref in verifier_refs.values()}) == 3
        and len({ref.get("sha256") for ref in verifier_refs.values()}) == 3,
        verifier_refs,
        "current distinct primary, independent, integrated .py refs and hashes",
        "cross_v1_2",
    )

    p_hostile = as_mapping(
        primary.get("m2_physical_response_successor_minimum_contract_hostile_fixtures")
    )
    i_hostile = as_mapping(
        independent.get("m2_physical_response_successor_minimum_contract_hostile_fixtures")
    )
    audit.check(
        "cross v1.2 exact 57 hostile names and reports",
        p_hostile == i_hostile
        and tuple(p_hostile) == tuple(PHYSICAL_CONTRACT_HOSTILE_CODES)
        and len(p_hostile) == 57
        and all(
            as_mapping(p_hostile.get(name)).get("valid") is False
            and as_mapping(p_hostile.get(name)).get("expected_code_observed") is True
            and as_mapping(p_hostile.get(name)).get("expected_error_code") == code
            and code in as_list(as_mapping(p_hostile.get(name)).get("error_codes"))
            for name, code in PHYSICAL_CONTRACT_HOSTILE_CODES.items()
        ),
        {"primary_names": list(p_hostile), "independent_names": list(i_hostile)},
        PHYSICAL_CONTRACT_HOSTILE_CODES,
        "cross_v1_2_hostile",
    )
    reordered = {"valid": True, "errors": [], "error_codes": []}
    audit.check(
        "cross v1.2 reordered positive metamorphic accepted",
        primary.get("m2_physical_response_successor_minimum_contract_reordered_metamorphic")
        == independent.get("m2_physical_response_successor_minimum_contract_reordered_metamorphic")
        == reordered,
        {
            "primary": primary.get("m2_physical_response_successor_minimum_contract_reordered_metamorphic"),
            "independent": independent.get("m2_physical_response_successor_minimum_contract_reordered_metamorphic"),
        },
        reordered,
        "cross_v1_2",
    )
    p_fuzz = as_mapping(primary.get("m2_physical_response_successor_minimum_contract_fuzz"))
    i_fuzz = as_mapping(independent.get("m2_physical_response_successor_minimum_contract_fuzz"))
    fuzz_codes = {
        as_mapping(row).get("name"): tuple(as_list(as_mapping(row).get("error_codes")))
        for row in as_list(p_fuzz.get("cases"))
    }
    audit.check(
        "cross v1.2 exact 48 malformed fuzz cases rejected without exception",
        p_fuzz == i_fuzz
        and p_fuzz.get("case_count") == p_fuzz.get("rejected_count") == 48
        and p_fuzz.get("all_rejected_without_exception") is True
        and all(as_mapping(row).get("rejected") is True for row in as_list(p_fuzz.get("cases")))
        and fuzz_codes == PHYSICAL_CONTRACT_FUZZ_CODES,
        {"summary": {key: p_fuzz.get(key) for key in ("case_count", "rejected_count", "all_rejected_without_exception")}, "codes": fuzz_codes},
        PHYSICAL_CONTRACT_FUZZ_CODES,
        "cross_v1_2_fuzz",
    )

    m_schema = as_mapping(
        manifest.get("m2_physical_response_successor_minimum_contract_schema")
    )
    m_hostiles = as_mapping(
        manifest.get("m2_physical_response_successor_minimum_contract_hostile_fixtures")
    )
    audit.check(
        "manifest v1.2 minimum-contract exact schema enums and counts",
        m_schema.get("closed_child_id") == V1_2_CLOSED_SUBGATES[1]
        and m_schema.get("schema") == PHYSICAL_CONTRACT_SCHEMA
        and tuple(m_schema.get("root_fields", ())) == PHYSICAL_CONTRACT_ROOT_FIELDS
        and tuple(m_schema.get("artifact_ref_fields", ())) == PHYSICAL_CONTRACT_ARTIFACT_REF_FIELDS
        and tuple(m_schema.get("artifact_roles", ())) == PHYSICAL_CONTRACT_ARTIFACT_ROLES
        and tuple(m_schema.get("mandatory_substantive_changes", ()))
        == PHYSICAL_CONTRACT_MANDATORY_CHANGES
        and tuple(m_schema.get("substantive_change_enum", ()))
        == PHYSICAL_CONTRACT_CHANGE_ENUM
        and tuple(m_schema.get("error_terms", ())) == PHYSICAL_CONTRACT_ERROR_TERMS
        and tuple(m_schema.get("hard_rows", ())) == HARD_ROWS
        and tuple(as_mapping(m_schema.get("structured_enums")).get("limit_order", ()))
        == PHYSICAL_CONTRACT_LIMIT_ORDER
        and m_schema.get("max_canonical_rational_length") == 128
        and m_schema.get("max_repository_relative_path_length") == 4096
        and m_schema.get("candidate_created") is False
        and m_schema.get("fixture_only") is True
        and m_hostiles.get("count") == 57
        and as_mapping(m_hostiles.get("cases")) == PHYSICAL_CONTRACT_HOSTILE_CODES
        and as_mapping(m_hostiles.get("deterministic_fuzz")).get("case_count") == 48,
        {"schema": m_schema, "hostiles": m_hostiles},
        "exact 1.1 schema, enums, limits, 57 hostiles, and 48 fuzz cases",
        "cross_v1_2",
    )
    require_tokens(
        json.dumps(m_schema, sort_keys=True),
        "manifest v1.2 hardened minimum-contract boundaries",
        (
            "embedded NUL", "4096", "case-sensitive", "space or dot",
            "OSError, ValueError and RuntimeError", "128", "coprime",
            "denominator at least 2", "Exactly six unique error IDs",
            "unique top-level result key", "order-insensitive exact equality",
            "semantic truth", "NOT_MACHINE_PROVED", "physical semantics",
            "FORMAL", "parent gate remain open",
        ),
        audit,
        core=True,
        group="cross_v1_2",
    )
    return {
        "linear_probe": {
            "free_energy_difference": "3/25",
            "boltzmann_exponent_shift": "-9/50",
            "curvatures": ["5/7", "11/7"],
            "shift": "6/7",
            "ground_branches": [0, 0, 0],
        },
        "minimum_contract_schema": PHYSICAL_CONTRACT_SCHEMA,
        "hostile_count": 57,
        "fuzz_count": 48,
        "artifact_ref_count": 31,
        "new_closed_children": list(V1_2_CLOSED_SUBGATES),
        "new_negative": V1_2_NEGATIVE_IDS[0],
        "physical_response_gate_closed": False,
        "parent_gate_closed": False,
    }



def _manifest_v1_3_suite(manifest: Mapping[str, Any]) -> dict[str, Any]:
    identity = as_mapping(manifest.get("m2_v1_3_identity_and_scope"))
    keys = (
        "schema", "result", "exploration_id", "claim_bearing", "tier",
        "closed_child_ids", "negative_ids", "open_successor_gate_ids",
    )
    suite = {key: identity.get(key) for key in keys}
    suite.update({
        "real_scalar_internal_u1_and_winding": manifest.get(V13_AUTHORITY_SECTION_KEYS[0]),
        "one_q_auxiliary_phason_curvature_and_finite_torus_secant": manifest.get(V13_AUTHORITY_SECTION_KEYS[1]),
        "helicity_tensor_contact_shift_nonidentifiability": manifest.get(V13_AUTHORITY_SECTION_KEYS[2]),
        "analytic_map_integer_exponent_transport": manifest.get(V13_AUTHORITY_SECTION_KEYS[3]),
        "six_stage_relative_log_slope_error_transport": manifest.get(V13_AUTHORITY_SECTION_KEYS[4]),
        "scope": identity.get("scope"),
    })
    return suite


def compare_v1_3(
    primary: dict[str, Any],
    independent: dict[str, Any],
    manifest: dict[str, Any],
    audit: Audit,
) -> dict[str, Any]:
    p = as_mapping(primary.get("m2_v1_3_theorem_suite"))
    i = as_mapping(independent.get("m2_v1_3_theorem_suite"))
    m = _manifest_v1_3_suite(manifest)
    pv = as_mapping(primary.get("m2_v1_3_theorem_suite_validation"))
    iv = as_mapping(independent.get("m2_v1_3_theorem_suite_validation"))
    audit.check(
        "cross v1.3 primary independent manifest suites exact",
        p == i == m and pv.get("valid") is True and iv.get("valid") is True
        and as_list(pv.get("error_codes")) == [] and as_list(iv.get("error_codes")) == [],
        {"p=m": p == m, "i=m": i == m, "pv": pv, "iv": iv},
        "three equal suites and two valid reports", "cross_v1_3",
    )
    audit.check(
        "cross v1.3 five children four negatives three successors T0 exact",
        p.get("schema") == V13_SUITE_SCHEMA
        and p.get("result") == f"{RESULT_NUMBER} {RESULT_VERSION}"
        and p.get("exploration_id") == EXPLORATION_ID
        and p.get("claim_bearing") is False and p.get("tier") == "T0"
        and tuple(p.get("closed_child_ids", ())) == NEW_CLOSED_SUBGATES
        and tuple(p.get("negative_ids", ())) == NEW_NEGATIVE_IDS
        and tuple(p.get("open_successor_gate_ids", ())) == OPEN_SUCCESSOR_GATES,
        {key: p.get(key) for key in (
            "schema", "result", "exploration_id", "claim_bearing", "tier",
            "closed_child_ids", "negative_ids", "open_successor_gate_ids",
        )},
        {"children": 5, "negatives": 4, "successors": 3, "tier": "T0"},
        "cross_v1_3",
    )

    u1 = as_mapping(p.get("real_scalar_internal_u1_and_winding"))
    audit.check(
        "cross v1.3 GL1 theorem and H2 contractibility exact",
        u1.get("closed_child_id") == NEW_CLOSED_SUBGATES[0]
        and u1.get("negative_id") == NEW_NEGATIVE_IDS[0]
        and u1.get("field_target") == "R"
        and u1.get("pointwise_linear_group") == "GL(1,R)=R*"
        and all(t in str(u1.get("theorem")) for t in (
            "continuous real one-dimensional linear representation",
            "compact and connected", "log", "compact subgroup", "trivial",
        ))
        and u1.get("configuration_space") == "H^2(T^3;R)"
        and u1.get("contraction") == "C_s(phi)=(1-s)phi for 0<=s<=1"
        and u1.get("intrinsic_winding_sectors") is False
        and len(as_list(u1.get("scope_exclusions"))) == 3,
        u1, "trivial GL1 image and contractible real H2 with three exclusions",
        "cross_v1_3",
    )

    ph = as_mapping(p.get("one_q_auxiliary_phason_curvature_and_finite_torus_secant"))
    fx = as_mapping(ph.get("fraction_fixture"))
    audit.check(
        "cross v1.3 one-Q general symbolic Hessian and 3k boundary exact",
        ph.get("closed_child_id") == NEW_CLOSED_SUBGATES[1]
        and ph.get("negative_id") == NEW_NEGATIVE_IDS[1]
        and ph.get("sign_domain") == "s in {-1,+1}^3"
        and ph.get("trial_family") == "phi=A*cos((q*s+a).x)"
        and ph.get("density") == "f=A^2*(r+c*S(a))/4+3*g*A^4/32"
        and ph.get("shear_polynomial") == "S(a)=sum_i(2*s_i*q*a_i+a_i^2)^2"
        and ph.get("optimized_amplitude_squared") == "-4*(r+c*S(a))/(3*g)"
        and ph.get("optimized_density") == "-(r+c*S(a))^2/(6*g)"
        and ph.get("hessian_at_zero") == "-8*r*c*q^2/(3*g)*I_3"
        and ph.get("symbolic_all_eight_signs") is True
        and ph.get("symbolic_optimized_identity") is True
        and ph.get("cubic_identity") == "cos(theta)^3=(3*cos(theta)+cos(3*theta))/4"
        and ph.get("cubic_laurent_coefficients")
        == {"-3": "1/8", "-1": "3/8", "1": "3/8", "3": "1/8"}
        and ph.get("symbolic_cubic_identity") is True
        and "3k harmonic" in str(ph.get("euler_boundary"))
        and "not an exact Euler solution" in str(ph.get("euler_boundary")),
        ph, "all signs, optimized Hessian, Laurent cube, third harmonic retained",
        "cross_v1_3",
    )
    audit.check(
        "cross v1.3 continuous-a auxiliary and fixed-torus discrete secant exact",
        "auxiliary Bloch/supercell/thermodynamic" in str(ph.get("physical_boundary"))
        and "not an internal-U(1) helicity modulus" in str(ph.get("physical_boundary"))
        and all(t in str(ph.get("finite_torus_rule")) for t in (
            "h=2*pi/L", "q=m*h", "integer multiples of h", "fixed-amplitude central secant",
        ))
        and ph.get("fixed_amplitude_continuum_curvature") == "2*c*A0^2*q^2"
        and ph.get("fixed_amplitude_central_secant") == "c*A0^2*(4*q^2+h^2)/2"
        and ph.get("finite_torus_secant_excess") == "c*A0^2*h^2/2"
        and ph.get("relative_secant_correction") == "h^2/(4*q^2)=1/(4*m^2) when q=m*h",
        ph, "continuous auxiliary; fixed torus only discrete fixed-amplitude secant",
        "cross_v1_3",
    )
    audit.check(
        "cross v1.3 canonical phason fixture exact",
        fx.get("inputs") == {
            "r": "-3", "c": "2", "q": "5", "g": "7",
            "fundamental_reciprocal_step_h": "1",
        }
        and fx.get("optimized_amplitude_squared") == "4/7"
        and fx.get("q_over_h_integer") == 5
        and [fx.get(k) for k in (
            "continuum_curvature", "finite_torus_secant",
            "secant_correction", "relative_correction",
        )] == ["400/7", "404/7", "4/7", "1/100"],
        fx, ["4/7", "400/7", "404/7", "4/7", "1/100"], "cross_v1_3",
    )

    response = as_mapping(p.get("helicity_tensor_contact_shift_nonidentifiability"))
    audit.check(
        "cross v1.3 Kubo ground tensor contact shift exact",
        response.get("closed_child_id") == NEW_CLOSED_SUBGATES[2]
        and response.get("hamiltonian_family")
        == "H(A)=H0-sum_i A_i*J_i+(1/2)*sum_ij A_i*T_ij*A_j"
        and all(t in str(response.get("finite_beta_formula")) for t in (
            "<T_ij>_beta", "integral_0^beta", "delta J_i(-i tau) delta J_j",
        ))
        and all(t in str(response.get("isolated_ground_formula")) for t in (
            "<0|T_ij|0>", "2*Re sum_{n>0}", "E_n-E_0",
        ))
        and "positive gap" in str(as_list(response.get("hypotheses"))[-1])
        and response.get("symmetric_contact_shift")
        == "T_ij -> T_ij+V*D_ij*I with D=D^T"
        and response.get("response_shift") == "Upsilon -> Upsilon+D"
        and response.get("fixed_under_shift")
        == ["H0", "J_i", "zero-source state", "zero-source spectrum"],
        response, "finite-beta and gapped-ground formulas, symmetric +D ambiguity",
        "cross_v1_3",
    )

    amap = as_mapping(p.get("analytic_map_integer_exponent_transport"))
    poly = as_mapping(amap.get("hostile_polynomials"))
    audit.check(
        "cross v1.3 analytic R0 integer order x2 x3 local-diffeo boundary exact",
        amap.get("closed_child_id") == NEW_CLOSED_SUBGATES[3]
        and amap.get("negative_id") == NEW_NEGATIVE_IDS[2]
        and amap.get("input_scaling") == "kappa(tau)=C*tau*(1+o(1)) with C>0"
        and all(t in str(amap.get("hypothesis")) for t in (
            "R(0)=0", "b_n*kappa^n", "b_n>0", "n>=1", "first nonzero analytic order",
        ))
        and "positive integer n" in str(amap.get("transport"))
        and amap.get("integer_order") is True
        and all(t in str(amap.get("unit_order_sufficient_condition")) for t in (
            "R(0)=0", "R'(0)>0", "inverse-function theorem", "n=1",
        ))
        and amap.get("positive_one_sided_local_invertibility_alone_sufficient") is False
        and poly.get("x_squared_coefficients") == ["0", "0", "1"]
        and poly.get("x_squared_order") == 2
        and poly.get("x_cubed_coefficients") == ["0", "0", "0", "1"]
        and poly.get("x_cubed_order") == 3
        and "locally invertible through zero" in str(poly.get("boundary")),
        amap, "R(0)=0, n>=1, unit order only at nonzero derivative; x2/x3 hostiles",
        "cross_v1_3",
    )

    transport = as_mapping(p.get("six_stage_relative_log_slope_error_transport"))
    tf = as_mapping(transport.get("fraction_fixture"))
    d0 = [Fraction(1, 10 * j) for j in range(1, 7)]
    d1 = [Fraction(1, 10 * (j + 1)) for j in range(1, 7)]
    lower = Fraction(1)
    upper = Fraction(1)
    for left, right in zip(d0, d1):
        lower *= (1 - right) / (1 + left)
        upper *= (1 + right) / (1 - left)
    q = lambda x: str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    audit.check(
        "cross v1.3 R0-R6 adjacent floors rational envelope and lambda<1 abs-log exact",
        transport.get("closed_child_id") == NEW_CLOSED_SUBGATES[4]
        and transport.get("negative_id") == NEW_NEGATIVE_IDS[3]
        and transport.get("stage_count") == 6 and transport.get("initial_stage_exact") is True
        and transport.get("scale_domain") == "lambda>0 and lambda!=1"
        and "R_0,...,R_6" in str(as_list(transport.get("hypotheses"))[0])
        and "Rhat_0=R_0" in str(as_list(transport.get("hypotheses"))[0])
        and "positive floor" in str(as_list(transport.get("hypotheses"))[1])
        and "epsilon_j(s)/m_j(s)<1" in str(as_list(transport.get("hypotheses"))[2])
        and transport.get("final_output_definition") == "X(s)=R_6(s) and Xhat(s)=Rhat_6(s)"
        and "product_j" in str(transport.get("ratio_envelope"))
        and "abs(log(lambda))" in str(transport.get("log_slope_bound"))
        and tf.get("lower_ratio") == q(lower) == "9720191/14498297"
        and tf.get("upper_ratio") == q(upper) == "93579917/62124699"
        and tf.get("all_stage_outputs_positive") is True
        and tf.get("all_delta_strictly_below_one") is True
        and transport.get("six_absolute_errors_alone_sufficient") is False
        and "tend to zero" in str(transport.get("exponent_transfer_condition")),
        {"transport": transport, "derived": [q(lower), q(upper)]},
        "six adjacent floors; exact L/U; lambda<1 covered by abs(log lambda)",
        "cross_v1_3",
    )

    phost = as_mapping(primary.get("m2_v1_3_hostile_fixtures"))
    ihost = as_mapping(independent.get("m2_v1_3_hostile_fixtures"))
    mhost = as_mapping(manifest.get("m2_v1_3_hostile_fixtures"))
    audit.check(
        "cross v1.3 exact 27 hostile names and manifest codes",
        set(phost) == set(ihost) == set(V13_HOSTILE_CODES)
        and mhost.get("count") == 27 and as_mapping(mhost.get("cases")) == V13_HOSTILE_CODES,
        {"primary": list(phost), "independent": list(ihost), "manifest": mhost},
        V13_HOSTILE_CODES, "cross_v1_3_hostile",
    )
    for name, code in V13_HOSTILE_CODES.items():
        pr = as_mapping(phost.get(name)); ir = as_mapping(ihost.get(name))
        audit.check(
            f"cross v1.3 hostile {name}",
            pr.get("valid") is False and ir.get("valid") is False
            and pr.get("expected_code_observed") is True
            and ir.get("expected_code_observed") is True
            and pr.get("expected_error_code") == ir.get("expected_error_code") == code
            and code in as_list(pr.get("error_codes")) and code in as_list(ir.get("error_codes")),
            {"primary": pr, "independent": ir}, {"valid": False, "code": code},
            "cross_v1_3_hostile",
        )

    schema = as_mapping(manifest.get("m2_physical_response_successor_minimum_contract_schema"))
    counts = [
        len(as_mapping(primary.get("hostile_fixtures"))),
        len(as_mapping(primary.get("map_only_repair_hostile_fixtures"))),
        len(as_mapping(primary.get("successor_hostile_fixtures"))),
        len(as_mapping(primary.get("m2_physical_response_successor_minimum_contract_hostile_fixtures"))),
        as_mapping(primary.get("m2_physical_response_successor_minimum_contract_fuzz")).get("case_count"),
    ]
    audit.check(
        "cross v1.3 retained 28 7 11 57 48 counts and 4096 path envelope",
        counts == [28, 7, 11, 57, 48]
        and schema.get("max_repository_relative_path_length") == 4096,
        {"counts": counts, "path_envelope": schema.get("max_repository_relative_path_length")},
        {"counts": [28, 7, 11, 57, 48], "path_envelope": 4096}, "cross_v1_3",
    )
    scope = as_mapping(p.get("scope"))
    audit.check(
        "cross v1.3 T0 no-overclaim parents open",
        scope == {
            "candidate_created": False, "physical_response_closed": False,
            "round1_freeze_closed": False, "pre_a_complete": False,
            "sector_a_complete": False, "checkpoint_synthesis": "PROOF-FIRST DEFERRED HISTORY; CURRENT COMBINED CHECKPOINT ISSUED",
        }
        and as_mapping(primary.get("scope")) == PRIMARY_SCOPE_EXPECTED
        and as_mapping(independent.get("scope")) == INDEPENDENT_SCOPE_EXPECTED
        and all(g in as_list(manifest.get("open_gates")) for g in (
            PARENT_GATE, PHYSICAL_RESPONSE_GATE, *OPEN_SUCCESSOR_GATES,
        ))
        and all(t in str(manifest.get("no_overclaim")) for t in (
            "T0", "claim_bearing:false", "No candidate", "physical response",
            "Round-1", "C6", "CP1", "physical Sector A", "Pre-A",
        )),
        {"scope": scope, "open": manifest.get("open_gates"), "boundary": manifest.get("no_overclaim")},
        "all physical and parent gates open", "cross_v1_3",
    )
    return {
        "schema": V13_SUITE_SCHEMA, "closed_children": list(NEW_CLOSED_SUBGATES),
        "negative_ids": list(NEW_NEGATIVE_IDS),
        "open_successor_gates": list(OPEN_SUCCESSOR_GATES), "hostile_count": 27,
        "retained_hostile_counts": counts, "path_length_envelope": 4096,
        "phason_fixture": ["4/7", "400/7", "404/7", "4/7", "1/100"],
        "log_slope_envelope": [q(lower), q(upper)],
        "lambda_below_one_supported_by_absolute_log": True,
        "claim_bearing": False, "tier": "T0", "parent_gate_closed": False,
    }

def compare_components(
    primary: dict[str, Any],
    independent: dict[str, Any],
    manifest: dict[str, Any],
    audit: Audit,
) -> dict[str, Any]:
    pstate = as_mapping(primary.get("current_tree"))
    istate = as_mapping(independent.get("current_tree"))
    audit.check(
        "cross audited commit exact",
        pstate.get("audited_commit")
        == istate.get("audited_commit")
        == AUDITED_COMMIT,
        [pstate.get("audited_commit"), istate.get("audited_commit")],
        AUDITED_COMMIT,
        "cross_core",
    )
    audit.check(
        "cross audited commit remains ancestor",
        istate.get("audited_commit_is_ancestor") is True
        and pstate.get("current_head") == istate.get("current_head"),
        [
            istate.get("audited_commit_is_ancestor"),
            pstate.get("current_head"),
            istate.get("current_head"),
        ],
        "ancestor and equal observed HEAD",
        "cross_core",
    )
    zero_fields = ("freeze_record_count", "admitted_microscopic_survivor_count")
    audit.check(
        "cross exact empty commit-pinned registered state",
        all(pstate.get(field) == istate.get(field) == 0 for field in zero_fields)
        and pstate.get("freeze_records") == istate.get("freeze_records") == []
        and pstate.get("admitted_microscopic_survivors")
        == istate.get("admitted_microscopic_survivors")
        == [],
        {
            "primary": {field: pstate.get(field) for field in zero_fields},
            "independent": {field: istate.get(field) for field in zero_fields},
        },
        "zero commit-pinned records and admitted microscopic survivors",
        "cross_core",
    )
    plive = as_mapping(pstate.get("local_freeze_tag_observation"))
    ilive = as_mapping(istate.get("local_freeze_tag_observation"))
    live_shape = all(
        observation.get("load_bearing") is False
        and isinstance(observation.get("count"), int)
        and observation.get("count") >= 0
        and isinstance(observation.get("tags"), list)
        and observation.get("count") == len(observation.get("tags"))
        and text_has(observation.get("scope", ""), "live local freeze")
        for observation in (plive, ilive)
    )
    audit.check(
        "cross live freeze tags informational and non-load-bearing",
        live_shape,
        {"primary": plive, "independent": ilive},
        "internally consistent live observations with load_bearing=false",
        "cross_core",
    )
    audit.check(
        "cross canonical contestants and blockers",
        tuple(pstate.get("contestant_ids", ()))
        == tuple(istate.get("contestant_ids", ()))
        == EXPECTED_CANDIDATES
        and tuple(pstate.get("blockers", ()))
        == tuple(istate.get("blockers", ()))
        == EXPECTED_BLOCKERS
        and len(EXPECTED_BLOCKERS) == 7,
        {
            "primary_candidates": pstate.get("contestant_ids"),
            "independent_candidates": istate.get("contestant_ids"),
            "primary_blockers": pstate.get("blockers"),
            "independent_blockers": istate.get("blockers"),
        },
        {"candidates": EXPECTED_CANDIDATES, "blockers": EXPECTED_BLOCKERS},
        "cross_core",
    )
    audit.check(
        "cross current tree remains unready",
        pstate.get("actual_freeze_ready") is False
        and istate.get("actual_freeze_ready") is False
        and pstate.get("parent_freeze_gate_closed") is False
        and istate.get("parent_freeze_gate_closed") is False
        and pstate.get("pre_a_exit_conditions_met") is False
        and istate.get("pre_a_exit_conditions_met") is False
        and pstate.get("per_parameter_common_input_ledger_complete") is False
        and istate.get("per_parameter_common_input_ledger_complete") is False
        and pstate.get("prospective_prediction_frozen") is False
        and istate.get("prospective_prediction_frozen") is False,
        {"primary": pstate, "independent": istate},
        "all readiness/promotion flags false",
        "cross_core",
    )
    audit.check(
        "cross candidate maps and predictions absent",
        as_mapping(pstate.get("M1")).get("map_to_round1_measured_observables")
        is False
        and as_mapping(istate.get("M1")).get("microscopic_map") is False
        and as_mapping(pstate.get("M1")).get(
            "declared_non_fitting_validation_prediction"
        )
        is False
        and as_mapping(istate.get("M1")).get(
            "non_fitting_validation_prediction"
        )
        is False
        and as_mapping(pstate.get("M2")).get("physical_predictions")
        == as_mapping(istate.get("M2")).get("physical_predictions")
        == []
        and as_mapping(pstate.get("M2")).get("holdout_prediction") is False
        and as_mapping(istate.get("M2")).get("holdout_prediction") is False
        and as_mapping(pstate.get("M5")).get("map_to_measured_observables")
        is False
        and as_mapping(istate.get("M5")).get("microscopic_map") is False
        and as_mapping(pstate.get("M5")).get("holdout_prediction") is False
        and as_mapping(istate.get("M5")).get("holdout_prediction") is False,
        {"primary": [pstate.get("M1"), pstate.get("M2"), pstate.get("M5")],
         "independent": [istate.get("M1"), istate.get("M2"), istate.get("M5")]},
        "all M1/M2/M5 admitted-map and prediction fields absent",
        "cross_core",
    )

    pcontract = as_mapping(primary.get("freeze_schema_contract"))
    icontract = as_mapping(independent.get("freeze_schema_contract"))
    audit.check(
        "cross freeze schema exact",
        pcontract.get("schema") == icontract.get("schema") == FREEZE_SCHEMA
        and all(
            tuple(pcontract.get(field, ()))
            == tuple(icontract.get(field, ()))
            == expected
            for field, expected in NESTED_FIELD_CONTRACTS.items()
        ),
        {"primary": pcontract, "independent": icontract},
        {"schema": FREEZE_SCHEMA, "nested_fields": NESTED_FIELD_CONTRACTS},
        "cross_core",
    )
    audit.check(
        "cross candidate prediction and input-source firewall contract",
        pcontract.get("candidate_specific_object")
        == icontract.get("candidate_specific_object")
        == "microscopic-to-observable map plus candidate_id-bound frozen prediction"
        and tuple(pcontract.get("prediction_fields", ())) == PREDICTION_FIELDS
        and tuple(icontract.get("prediction_fields", ())) == PREDICTION_FIELDS
        and tuple(pcontract.get("allowed_input_fields", ())) == ALLOWED_INPUT_FIELDS
        and tuple(icontract.get("allowed_input_fields", ())) == ALLOWED_INPUT_FIELDS,
        {"primary": pcontract, "independent": icontract},
        {
            "prediction_fields": PREDICTION_FIELDS,
            "allowed_input_fields": ALLOWED_INPUT_FIELDS,
        },
        "cross_core",
    )
    audit.check(
        "cross keyed canonical commitment and confined path contract",
        pcontract.get("commitment_definition")
        == icontract.get("commitment_definition")
        == COMMITMENT_DEFINITION
        and pcontract.get("path_policy")
        == icontract.get("path_policy")
        == PATH_POLICY,
        {
            "primary_commitment": pcontract.get("commitment_definition"),
            "independent_commitment": icontract.get("commitment_definition"),
            "primary_path": pcontract.get("path_policy"),
            "independent_path": icontract.get("path_policy"),
        },
        {"commitment": COMMITMENT_DEFINITION, "path": PATH_POLICY},
        "cross_core",
    )
    audit.check(
        "cross synthetic fixtures shape-valid and independent",
        as_mapping(primary.get("synthetic_schema_validation")).get("valid") is True
        and as_mapping(independent.get("synthetic_schema_validation")).get("valid")
        is True
        and as_mapping(primary.get("synthetic_schema_validation")).get(
            "fixture_digest"
        )
        != as_mapping(independent.get("synthetic_schema_validation")).get(
            "fixture_digest"
        ),
        [
            primary.get("synthetic_schema_validation"),
            independent.get("synthetic_schema_validation"),
        ],
        "two valid, independently reconstructed synthetic fixtures",
        "cross_core",
    )

    primary_hostile_raw = as_mapping(primary.get("hostile_fixtures"))
    independent_hostile_raw = as_mapping(independent.get("hostile_fixtures"))
    audit.check(
        "cross exact 28 hostile fixture names",
        tuple(primary_hostile_raw) == tuple(independent_hostile_raw) == tuple(HOSTILE_CODES),
        {
            "primary": list(primary_hostile_raw),
            "independent": list(independent_hostile_raw),
        },
        list(HOSTILE_CODES),
        "cross_hostile",
    )
    phostile = normalize_hostiles(primary, "primary")
    ihostile = normalize_hostiles(independent, "independent")
    for name, code in HOSTILE_CODES.items():
        audit.check(
            f"cross hostile {name}",
            phostile[name].get("valid") is False
            and ihostile[name].get("valid") is False
            and phostile[name].get("expected_code_observed") is True
            and ihostile[name].get("expected_code_observed") is True
            and phostile[name].get("expected_error_code") == code
            and ihostile[name].get("expected_error_code") == code
            and code in phostile[name].get("error_codes", [])
            and code in ihostile[name].get("error_codes", [])
            and phostile[name].get("error_codes")
            == ihostile[name].get("error_codes"),
            {"primary": phostile[name], "independent": ihostile[name]},
            {"valid": False, "error": code},
            "cross_hostile",
        )


    p_map_audit = as_mapping(primary.get("current_version_map_only_audit"))
    i_map_audit = as_mapping(independent.get("current_version_map_only_audit"))
    m_map_audit = as_mapping(manifest.get("current_version_map_only_audit"))
    p_survival = as_mapping(p_map_audit.get("survival_contract"))
    i_survival = as_mapping(i_map_audit.get("survival_contract"))
    m_survival = as_mapping(m_map_audit.get("frozen_survival_rule"))
    audit.check(
        "cross exact ten frozen hard rows",
        tuple(p_survival.get("hard_rows", ()))
        == tuple(i_survival.get("hard_rows", ()))
        == tuple(m_survival.get("hard_rows", ()))
        == HARD_ROWS
        and len(HARD_ROWS) == 10,
        {
            "primary": p_survival.get("hard_rows"),
            "independent": i_survival.get("hard_rows"),
            "manifest": m_survival.get("hard_rows"),
        },
        list(HARD_ROWS),
        "cross_v1_1",
    )
    p_residual = as_mapping(p_survival.get("residual_hard_rows"))
    i_residual = as_mapping(i_survival.get("residual_hard_rows"))
    m_residual = as_mapping(
        m_map_audit.get("map_independent_or_non_map_only_residual_hard_rows")
    )
    residual_count = sum(len(as_mapping(cells)) for cells in RESIDUAL_HARD_ROWS.values())
    audit.check(
        "cross exact eight residual hard-row cells",
        p_residual == i_residual == m_residual == RESIDUAL_HARD_ROWS
        and residual_count == 8,
        {"primary": p_residual, "independent": i_residual, "manifest": m_residual},
        {"cells": RESIDUAL_HARD_ROWS, "count": 8},
        "cross_v1_1",
    )

    def normalized_map_rows(payload: Mapping[str, Any], manifest_rows: bool = False) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for raw in as_list(payload.get("rows")):
            row = as_mapping(raw)
            rows.append(
                {
                    "candidate_id": row.get("candidate_id"),
                    "path": row.get("path"),
                    "sha256": row.get("normalized_sha256")
                    if manifest_rows
                    else row.get("pinned_sha256"),
                    "map_only_admitted": row.get("map_only_admitted"),
                }
            )
        return rows

    expected_map_rows = normalized_map_rows(m_map_audit, True)
    audit.check(
        "cross exact current-version map-only admitted cardinality zero",
        p_map_audit.get("cardinality")
        == i_map_audit.get("cardinality")
        == m_map_audit.get("cardinality")
        == 0
        and p_map_audit.get("admitted_candidate_ids")
        == i_map_audit.get("admitted_candidate_ids")
        == m_map_audit.get("admitted_candidate_ids")
        == []
        and p_survival.get("map_only_survivor_ids")
        == i_survival.get("map_only_survivor_ids")
        == m_map_audit.get("map_only_new_version_survivor_ids")
        == []
        and normalized_map_rows(p_map_audit) == expected_map_rows
        and normalized_map_rows(i_map_audit) == expected_map_rows
        and len(expected_map_rows) == 3
        and all(row.get("map_only_admitted") is False for row in expected_map_rows),
        {
            "primary": p_map_audit.get("admitted_candidate_ids"),
            "independent": i_map_audit.get("admitted_candidate_ids"),
            "manifest": m_map_audit.get("admitted_candidate_ids"),
            "rows": expected_map_rows,
        },
        {"cardinality": 0, "admitted": [], "rows": 3},
        "cross_v1_1",
    )
    audit.check(
        "cross map-only survival validators exact and valid",
        primary.get("map_only_survival_validation")
        == independent.get("map_only_survival_validation")
        == {"valid": True, "errors": [], "error_codes": []},
        [
            primary.get("map_only_survival_validation"),
            independent.get("map_only_survival_validation"),
        ],
        {"valid": True, "errors": [], "error_codes": []},
        "cross_v1_1",
    )

    p_fingerprint = as_mapping(primary.get("m2_finite_torus_dispersion_fingerprint"))
    i_fingerprint = as_mapping(independent.get("m2_finite_torus_dispersion_fingerprint"))
    m_fingerprint = as_mapping(manifest.get("m2_finite_torus_dispersion_fingerprint"))
    exact_ones = ["1"] * 48
    audit.check(
        "cross ordered 48-component fingerprint all ones and SHA exact",
        p_fingerprint.get("ordered_component_count")
        == i_fingerprint.get("ordered_component_count")
        == m_fingerprint.get("ordered_component_count")
        == 48
        and p_fingerprint.get("component_vector")
        == i_fingerprint.get("component_vector")
        == m_fingerprint.get("expected_component_vector")
        == exact_ones
        and p_fingerprint.get("all_components_exactly_one") is True
        and i_fingerprint.get("all_components_exactly_one") is True
        and p_fingerprint.get("fingerprint_sha256")
        == i_fingerprint.get("fingerprint_sha256")
        == FINGERPRINT_COMPONENT_SHA256
        and p_fingerprint.get("physical_prediction") is False
        and i_fingerprint.get("physical_prediction") is False,
        {
            "primary_count": p_fingerprint.get("ordered_component_count"),
            "independent_count": i_fingerprint.get("ordered_component_count"),
            "manifest_count": m_fingerprint.get("ordered_component_count"),
            "primary_sha": p_fingerprint.get("fingerprint_sha256"),
            "independent_sha": i_fingerprint.get("fingerprint_sha256"),
            "vector": p_fingerprint.get("component_vector"),
        },
        {"count": 48, "vector": exact_ones, "sha256": FINGERPRINT_COMPONENT_SHA256},
        "cross_v1_1",
    )

    p_map_hostile = as_mapping(primary.get("map_only_repair_hostile_fixtures"))
    i_map_hostile = as_mapping(independent.get("map_only_repair_hostile_fixtures"))
    m_map_hostile = as_mapping(manifest.get("map_only_repair_hostile_fixtures"))
    audit.check(
        "cross exact seven map-only hostile classes",
        p_map_hostile == i_map_hostile
        and len(p_map_hostile) == 7
        and set(p_map_hostile) == set(MAP_ONLY_HOSTILE_CODES)
        and m_map_hostile.get("count") == 7
        and as_mapping(m_map_hostile.get("cases")) == MAP_ONLY_HOSTILE_CODES
        and all(
            as_mapping(report).get("valid") is False
            and as_mapping(report).get("expected_code_observed") is True
            and as_mapping(report).get("expected_error_code") == MAP_ONLY_HOSTILE_CODES[name]
            and MAP_ONLY_HOSTILE_CODES[name] in as_list(as_mapping(report).get("error_codes"))
            for name, report in p_map_hostile.items()
        ),
        {"primary": p_map_hostile, "independent": i_map_hostile, "manifest": m_map_hostile},
        {"count": 7, "cases": MAP_ONLY_HOSTILE_CODES},
        "cross_v1_1",
    )

    p_successor = as_mapping(primary.get("m2_v1_successor_design"))
    i_successor = as_mapping(independent.get("m2_v1_successor_design"))
    m_successor = as_mapping(manifest.get("m2_v1_successor_design"))
    audit.check(
        "cross DESIGN_ONLY successor and all NOT_CREATED states exact",
        p_successor == i_successor == m_successor
        and p_successor.get("hypothetical_candidate_id") == M2_SUCCESSOR_ID
        and p_successor.get("status") == "DESIGN_ONLY"
        and p_successor.get("candidate_created") is False
        and all(p_successor.get(field) == "NOT_CREATED" for field in SUCCESSOR_NOT_CREATED_FIELDS)
        and as_mapping(p_successor.get("candidate_manifest"))
        == {"path": None, "sha256": None}
        and as_mapping(p_successor.get("required_contract")).get("open_gate")
        == PHYSICAL_RESPONSE_GATE,
        {"primary": p_successor, "independent": i_successor, "manifest": m_successor},
        {"status": "DESIGN_ONLY", "candidate_created": False, "states": "NOT_CREATED"},
        "cross_v1_1",
    )
    audit.check(
        "cross successor design validators exact and valid",
        primary.get("m2_v1_successor_design_validation")
        == independent.get("m2_v1_successor_design_validation")
        == {"valid": True, "errors": [], "error_codes": []},
        [
            primary.get("m2_v1_successor_design_validation"),
            independent.get("m2_v1_successor_design_validation"),
        ],
        {"valid": True, "errors": [], "error_codes": []},
        "cross_v1_1",
    )
    p_successor_hostile = as_mapping(primary.get("successor_hostile_fixtures"))
    i_successor_hostile = as_mapping(independent.get("successor_hostile_fixtures"))
    m_successor_hostile = as_mapping(manifest.get("m2_v1_successor_hostile_fixtures"))
    audit.check(
        "cross exact eleven successor hostile classes",
        p_successor_hostile == i_successor_hostile
        and len(p_successor_hostile) == 11
        and set(p_successor_hostile) == set(SUCCESSOR_HOSTILE_CODES)
        and m_successor_hostile.get("successor_hostile_count") == 11
        and m_successor_hostile.get("v1_0_freeze_schema_hostile_count_preserved") == 28
        and m_successor_hostile.get("total_hostile_class_count") == 39
        and as_mapping(m_successor_hostile.get("cases")) == SUCCESSOR_HOSTILE_CODES
        and all(
            as_mapping(report).get("valid") is False
            and as_mapping(report).get("expected_code_observed") is True
            and as_mapping(report).get("expected_error_code") == SUCCESSOR_HOSTILE_CODES[name]
            and SUCCESSOR_HOSTILE_CODES[name] in as_list(as_mapping(report).get("error_codes"))
            for name, report in p_successor_hostile.items()
        ),
        {
            "primary": p_successor_hostile,
            "independent": i_successor_hostile,
            "manifest": m_successor_hostile,
        },
        {"v1_0": 28, "successor": 11, "total": 39},
        "cross_v1_1",
    )
    audit.check(
        "cross all component scope booleans exact",
        as_mapping(primary.get("scope")) == PRIMARY_SCOPE_EXPECTED
        and as_mapping(independent.get("scope")) == INDEPENDENT_SCOPE_EXPECTED
        and all(isinstance(value, bool) for value in as_mapping(primary.get("scope")).values())
        and all(isinstance(value, bool) for value in as_mapping(independent.get("scope")).values()),
        {"primary": primary.get("scope"), "independent": independent.get("scope")},
        {"primary": PRIMARY_SCOPE_EXPECTED, "independent": INDEPENDENT_SCOPE_EXPECTED},
        "cross_v1_1",
    )
    p_under = as_mapping(primary.get("m2_retrospective_stiffness_map_underdetermination"))
    i_under = as_mapping(independent.get("m2_retrospective_stiffness_map_underdetermination"))
    audit.check(
        "cross retrospective missing-response countermodels exact boundary",
        as_mapping(p_under.get("completion_identity")).get("exponent") == 1
        and as_mapping(p_under.get("completion_square")).get("exponent") == 2
        and as_mapping(p_under.get("completion_identity")).get("exact_scale_ratio") == "2"
        and as_mapping(p_under.get("completion_square")).get("exact_scale_ratio") == "4"
        and i_under.get("exponents") == [1, 2]
        and i_under.get("identity_response_ratio") == 2
        and i_under.get("square_response_ratio") == 4
        and p_under.get("unique_physical_exponent_derivable")
        == i_under.get("unique_physical_exponent_derivable")
        is False
        and p_under.get("admitted_map_created")
        == i_under.get("admitted_map_created")
        is False
        and p_under.get("validation_credit") == i_under.get("validation_credit") is False,
        {"primary": p_under, "independent": i_under},
        {"exponents": [1, 2], "ratios": [2, 4], "map": False, "credit": False},
        "cross_v1_1",
    )

    v1_2 = compare_v1_2(primary, independent, manifest, audit)
    v1_3 = compare_v1_3(primary, independent, manifest, audit)

    pboundary = as_mapping(primary.get("real_freeze_verification_boundary"))
    iboundary = as_mapping(independent.get("real_freeze_verification_boundary"))
    audit.check(
        "cross real freeze fails closed",
        pboundary.get("required_error_code")
        == iboundary.get("required_error_code")
        == "EXTERNAL_VERIFICATION_REQUIRED"
        and pboundary.get("real_freeze_acceptance_enabled") is False
        and iboundary.get("real_freeze_acceptance_enabled") is False
        and as_mapping(primary.get("actual_freeze_validation")).get("valid") is False
        and as_mapping(independent.get("actual_freeze_validation")).get("valid")
        is False
        and "EXTERNAL_VERIFICATION_REQUIRED"
        in as_mapping(independent.get("actual_freeze_validation")).get(
            "error_codes", []
        ),
        {
            "primary": pboundary,
            "independent": iboundary,
            "independent_actual": independent.get("actual_freeze_validation"),
        },
        "EXTERNAL_VERIFICATION_REQUIRED and no acceptance",
        "cross_external",
    )
    audit.check(
        "cross cryptographic and remote verification open",
        pboundary.get("custodian_signature_cryptographically_verified") is False
        and iboundary.get("custodian_signature_cryptographically_verified")
        is False
        and pboundary.get("remote_commit_fetched_and_verified") is False
        and iboundary.get("remote_commit_fetched_and_verified") is False
        and pboundary.get("remote_annotated_tag_fetched_and_verified") is False
        and iboundary.get("remote_annotated_tag_fetched_and_verified") is False
        and iboundary.get("remote_tag_ref_fetched_and_verified") is False
        and iboundary.get("independently_authenticated_receipt_present") is False,
        {"primary": pboundary, "independent": iboundary},
        "signature, remote commit, annotated tag, tag ref, and receipt false",
        "cross_external",
    )
    return {
        "audited_commit": AUDITED_COMMIT,
        "freeze_records": 0,
        "live_freeze_tag_observation_load_bearing": False,
        "admitted_microscopic_survivors": 0,
        "actual_freeze_ready": False,
        "freeze_schema": FREEZE_SCHEMA,
        "root_fields": list(ROOT_FIELDS),
        "nested_field_contracts": NESTED_FIELD_CONTRACTS,
        "candidate_prediction_bound": True,
        "allowed_input_source_id_firewall": True,
        "repository_confined_POSIX_paths": True,
        "parsed_HTTPS_hostname_required": True,
        "keyed_RFC8785_JCS_HMAC_shape_required": True,
        "hostile_error_codes": HOSTILE_CODES,
        "real_freeze_required_error": "EXTERNAL_VERIFICATION_REQUIRED",
        "custodian_signature_cryptographically_verified": False,
        "remote_commit_fetched_and_verified": False,
        "remote_annotated_tag_fetched_and_verified": False,
        "remote_tag_ref_fetched_and_verified": False,
        "parent_gate_closed": False,
        "Pre_A_complete": False,
        "Sector_A_complete": False,
        "hard_row_count": 10,
        "residual_hard_row_cell_count": 8,
        "map_only_admitted_count": 0,
        "fingerprint_ordered_component_count": 48,
        "fingerprint_sha256": FINGERPRINT_COMPONENT_SHA256,
        "base_hostile_count": 28,
        "successor_hostile_count": 11,
        "map_only_hostile_count": 7,
        "stable_blocker_count": 7,
        "successor_status": "DESIGN_ONLY",
        "successor_candidate_created": False,
        "v1_2": v1_2,
        "v1_3": v1_3,
    }


def validate_manifest(manifest: dict[str, Any], audit: Audit) -> dict[str, Any]:
    expected = {
        "schema": "tect/pre-a-route-split/1.0",
        "task_id": TASK_ID,
        "claim_ids": list(CLAIM_IDS),
        "parent_explorations": list(PARENT_EXPLORATIONS),
        "prior_exploration_ids": list(PRIOR_EXPLORATION_IDS),
        "correction_exploration_ids": [HARDENING_EXPLORATION_ID],
        "exploration_id": EXPLORATION_ID,
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "claim_bearing": False,
        "negative_ids": list(NEGATIVE_IDS),
        "prior_negative_ids": list(PRIOR_NEGATIVE_IDS),
        "new_negative_ids": list(NEW_NEGATIVE_IDS),
        "reused_negative_ids": list(REUSED_NEGATIVE_IDS),
        "closed_subgates": list(CLOSED_SUBGATES),
        "open_gates": list(OPEN_GATES),
    }
    for field, value in expected.items():
        audit.check(
            f"manifest exact {field}",
            manifest.get(field) == value,
            manifest.get(field),
            value,
            "manifest",
        )
    audit.check(
        "manifest v1.3 proof-first T0 status exact",
        manifest.get("status") == PROOF_FIRST_MANIFEST_STATUS,
        manifest.get("status"),
        PROOF_FIRST_MANIFEST_STATUS,
        "manifest",
    )

    audited = as_mapping(manifest.get("audited_checkpoint"))
    audit.check(
        "manifest commit-pinned empty checkpoint",
        audited.get("commit") == AUDITED_COMMIT
        and audited.get("freeze_records") == 0
        and audited.get("admitted_microscopic_survivors") == 0
        and audited.get("verdict") == "NOT_CLOSABLE_CURRENT_TREE"
        and "freeze_tags" not in audited
        and "freeze_tag_scope" not in audited,
        audited,
        "pinned commit and two stable zero counts with no live-tag field",
        "manifest",
    )
    initial_live = as_mapping(manifest.get("initial_local_observation"))
    audit.check(
        "manifest initial live-tag observation informational",
        initial_live.get("freeze_tags") == 0
        and initial_live.get("load_bearing") is False
        and text_has(initial_live.get("scope", ""), "informational live local")
        and text_has(initial_live.get("scope", ""), "not an audited-commit fact")
        and text_has(initial_live.get("future_compatibility", ""), "future legitimate")
        and text_has(initial_live.get("future_compatibility", ""), "without invalidating"),
        initial_live,
        "separate non-load-bearing initial observation with future compatibility",
        "manifest",
    )

    freeze = as_mapping(manifest.get("freeze_schema"))
    audit.check(
        "manifest nested field allowlists exact",
        freeze.get("schema") == FREEZE_SCHEMA
        and all(
            tuple(freeze.get(field, ())) == expected_fields
            for field, expected_fields in NESTED_FIELD_CONTRACTS.items()
        ),
        freeze,
        {"schema": FREEZE_SCHEMA, "nested_fields": NESTED_FIELD_CONTRACTS},
        "manifest",
    )
    require_tokens(
        freeze.get("declared_type_contract", ""),
        "manifest exact type firewall",
        (
            "exact Boolean",
            "positive-integer",
            "nonempty-string",
            "digest/OID",
            "UTC-time",
            "container",
            "reject undeclared keys",
            "scheme https",
            "parsed hostname",
        ),
        audit,
        core=True,
        group="manifest",
    )
    require_tokens(
        freeze.get("minimum_candidate_condition", ""),
        "manifest candidate prediction binding",
        ("candidate_id", "score-eligible", "admitted map", "predicted_relation", "uniquely keyed"),
        audit,
        core=True,
        group="manifest",
    )
    provenance = as_mapping(manifest.get("provenance_protocol"))
    require_tokens(
        provenance.get("commitment", ""),
        "manifest keyed canonical HMAC shape",
        (
            "HMAC-SHA256",
            "K_custodian",
            "domain_separator",
            "0x00",
            "RFC8785-JCS",
            "EXTERNAL_CUSTODIAN",
            "plain unkeyed hash",
        ),
        audit,
        core=True,
        group="manifest",
    )
    require_tokens(
        provenance.get("path_policy", ""),
        "manifest repository-confined path policy",
        (
            "normalized relative POSIX",
            "no drive",
            "backslash",
            "absolute",
            "dot segment",
            "parent traversal",
            "inside the repository",
        ),
        audit,
        core=True,
        group="manifest",
    )
    base_hostiles = as_mapping(manifest.get("hostile_fixtures"))
    audit.check(
        "manifest exact retained 28 hostile classes",
        len(base_hostiles) == 28 and set(base_hostiles) == set(HOSTILE_CODES),
        list(base_hostiles),
        list(HOSTILE_CODES),
        "manifest",
    )

    map_audit = as_mapping(manifest.get("current_version_map_only_audit"))
    frozen_rule = as_mapping(map_audit.get("frozen_survival_rule"))
    audit.check(
        "manifest exact map-only empty-set and frozen all-PASS contract",
        map_audit.get("closed_child_id") == V1_1_CLOSED_SUBGATES[0]
        and map_audit.get("cardinality") == 0
        and map_audit.get("admitted_candidate_ids") == []
        and map_audit.get("map_only_new_version_survivor_ids") == []
        and map_audit.get("all_pass_after_map_only") is False
        and frozen_rule.get("hard_rows") == list(HARD_ROWS)
        and frozen_rule.get("survives_if") == "Every hard row is PASS."
        and as_mapping(map_audit.get("map_independent_or_non_map_only_residual_hard_rows"))
        == RESIDUAL_HARD_ROWS
        and len(as_list(map_audit.get("rows"))) == 3
        and all(as_mapping(row).get("map_only_admitted") is False for row in as_list(map_audit.get("rows"))),
        map_audit,
        {"cardinality": 0, "hard_rows": HARD_ROWS, "residual_cells": 8},
        "manifest",
    )
    map_hostiles = as_mapping(manifest.get("map_only_repair_hostile_fixtures"))
    audit.check(
        "manifest exact seven map-only hostile classes",
        map_hostiles.get("count") == 7
        and as_mapping(map_hostiles.get("cases")) == MAP_ONLY_HOSTILE_CODES
        and map_hostiles.get("total_hostile_class_count_with_v1_0_and_successor") == 46,
        map_hostiles,
        {"count": 7, "cases": MAP_ONLY_HOSTILE_CODES, "total": 46},
        "manifest",
    )

    fingerprint = as_mapping(manifest.get("m2_finite_torus_dispersion_fingerprint"))
    audit.check(
        "manifest exact ordered 48-component Gaussian fingerprint contract",
        fingerprint.get("closed_child_id") == V1_1_CLOSED_SUBGATES[1]
        and fingerprint.get("node_count") == 8
        and fingerprint.get("axes_per_node") == 3
        and fingerprint.get("components_per_axis") == 2
        and fingerprint.get("ordered_component_count") == 48
        and fingerprint.get("expected_component_vector") == ["1"] * 48
        and text_has(fingerprint.get("boundary", ""), "not a physical dispersion prediction"),
        fingerprint,
        {"nodes": 8, "axes": 3, "components": 2, "ordered": 48, "vector": ["1"] * 48},
        "manifest",
    )
    require_tokens(
        json.dumps(fingerprint, sort_keys=True),
        "manifest fingerprint definitions",
        ("d_minus", "d_plus", "S_bar", "R", "U", "4*m^2+1"),
        audit,
        core=True,
        group="manifest",
    )
    underdetermination = as_mapping(
        manifest.get("m2_retrospective_stiffness_map_underdetermination")
    )
    require_tokens(
        json.dumps(underdetermination, sort_keys=True),
        "manifest retrospective missing-map underdetermination",
        (
            "EXACT_LOGICAL_UNDERDETERMINATION",
            "exponent 1",
            "exponent 2",
            "not admitted maps",
            "validation_credit",
        ),
        audit,
        core=True,
        group="manifest",
    )
    successor = as_mapping(manifest.get("m2_v1_successor_design"))
    audit.check(
        "manifest DESIGN_ONLY successor creates nothing",
        successor.get("hypothetical_candidate_id") == M2_SUCCESSOR_ID
        and successor.get("status") == "DESIGN_ONLY"
        and successor.get("candidate_created") is False
        and all(successor.get(field) == "NOT_CREATED" for field in SUCCESSOR_NOT_CREATED_FIELDS)
        and as_mapping(successor.get("candidate_manifest")) == {"path": None, "sha256": None}
        and as_mapping(successor.get("required_contract")).get("open_gate")
        == PHYSICAL_RESPONSE_GATE,
        successor,
        {"status": "DESIGN_ONLY", "candidate_created": False, "all outputs": "NOT_CREATED"},
        "manifest",
    )
    successor_hostiles = as_mapping(manifest.get("m2_v1_successor_hostile_fixtures"))
    audit.check(
        "manifest exact retained-plus-successor hostile counts",
        successor_hostiles.get("v1_0_freeze_schema_hostile_count_preserved") == 28
        and successor_hostiles.get("successor_hostile_count") == 11
        and successor_hostiles.get("total_hostile_class_count") == 39
        and as_mapping(successor_hostiles.get("cases")) == SUCCESSOR_HOSTILE_CODES,
        successor_hostiles,
        {"v1_0": 28, "successor": 11, "total": 39},
        "manifest",
    )

    v13_identity = as_mapping(manifest.get("m2_v1_3_identity_and_scope"))
    placeholders = as_mapping(manifest.get("new_formal_authority_placeholders"))
    audit.check(
        "manifest v1.3 exact identity and formal placeholders",
        v13_identity.get("schema") == V13_SUITE_SCHEMA
        and v13_identity.get("result") == f"{RESULT_NUMBER} {RESULT_VERSION}"
        and v13_identity.get("exploration_id") == EXPLORATION_ID
        and v13_identity.get("claim_bearing") is False
        and v13_identity.get("tier") == "T0"
        and tuple(v13_identity.get("closed_child_ids", ())) == NEW_CLOSED_SUBGATES
        and tuple(v13_identity.get("negative_ids", ())) == NEW_NEGATIVE_IDS
        and tuple(v13_identity.get("open_successor_gate_ids", ())) == OPEN_SUCCESSOR_GATES
        and placeholders.get("exploration_id") == EXPLORATION_ID
        and tuple(placeholders.get("closed_child_ids", ())) == NEW_CLOSED_SUBGATES
        and tuple(placeholders.get("negative_ids", ())) == NEW_NEGATIVE_IDS
        and tuple(placeholders.get("open_gate_ids", ())) == OPEN_SUCCESSOR_GATES
        and placeholders.get("result") == f"{RESULT_NUMBER} {RESULT_VERSION}",
        {"identity": v13_identity, "placeholders": placeholders},
        "five/four/three T0 non-claim-bearing placeholders", "manifest",
    )

    route = as_mapping(manifest.get("route_status"))
    audit.check(
        "manifest route gates exact",
        route.get("parent_gate") == OPEN_GATES[0]
        and route.get("external_gate") == OPEN_GATES[2]
        and route.get("internal_gate") == OPEN_GATES[3]
        and route.get("verification_gate") == OPEN_GATES[4]
        and route.get("m2_successor_gate") == PHYSICAL_RESPONSE_GATE
        and tuple(route.get("open_successor_gates", ())) == OPEN_SUCCESSOR_GATES,
        route,
        {
            "parent": OPEN_GATES[0],
            "external": OPEN_GATES[2],
            "internal": OPEN_GATES[3],
            "verification": OPEN_GATES[4],
            "m2_successor": PHYSICAL_RESPONSE_GATE,
            "open_successors": OPEN_SUCCESSOR_GATES,
        },
        "manifest",
    )
    verification = as_mapping(manifest.get("verification"))
    scripts = {
        "primary_script": repo_path(PRIMARY),
        "independent_script": repo_path(INDEPENDENT),
        "integrated_script": repo_path(SCRIPT),
        "certificate": repo_path(CERTIFICATE),
    }
    for field, value in scripts.items():
        audit.check(
            f"manifest verification {field}",
            verification.get(field) == value,
            verification.get(field),
            value,
            "manifest",
        )
    require_tokens(
        manifest.get("no_overclaim", ""),
        "manifest v1.3 no-overclaim",
        (
            "T0", "claim_bearing:false", "real-line", "spatial phasons",
            "one-Q", "not an exact Euler state", "contact nonidentifiability",
            "analytic theorem", "six-stage theorem", "No candidate",
            "physical response", "Round-1", "C6", "CP1",
            "physical Sector A", "Pre-A",
        ),
        audit,
        core=True,
        group="manifest",
    )

    historical_metadata = as_mapping(manifest.get("checkpoint_synthesis"))
    historical = historical_checkpoint_lifecycle_diagnostics(historical_metadata)
    audit.check(
        "historical shared v1.9/v1.0 checkpoint metadata and labels exact",
        historical["metadata_core_exact"]
        and historical["r168_history_label_exact"]
        and historical["shared_manifest_core_exact"]
        and historical["r167_history_label_exact"],
        historical,
        EXPECTED_HISTORICAL_CHECKPOINT_CORE,
        "pdf_history",
    )
    audit.check(
        "historical v1.9/v1.0 checkpoint hashes freshness pages and two-parser extraction",
        historical["valid"],
        historical,
        {
            "source_sha256": CHECKPOINT_SOURCE_SHA256,
            "pdf_sha256": CHECKPOINT_PDF_SHA256,
            "pages": CHECKPOINT_PAGES,
            "scope": "historical only",
        },
        "pdf_history",
    )

    v2_metadata = as_mapping(manifest.get(V2_HISTORICAL_CHECKPOINT_FIELD))
    v2_historical = issued_checkpoint_lifecycle_diagnostics(
        v2_metadata,
        other_field=V2_HISTORICAL_CHECKPOINT_FIELD,
        required_tokens=V2_HISTORICAL_CHECKPOINT_REQUIRED_TOKENS,
        workflow_versions=("R-167 v2.0", "R-168 v1.1"),
    )
    audit.check(
        "historical shared v2.0/v1.1 checkpoint fixed metadata exact",
        dict(v2_metadata) == EXPECTED_V2_HISTORICAL_CHECKPOINT_CORE,
        v2_metadata,
        EXPECTED_V2_HISTORICAL_CHECKPOINT_CORE,
        "pdf_history",
    )
    audit.check(
        "historical v2.0/v1.1 checkpoint hashes freshness pages and two-parser extraction",
        v2_historical["valid"]
        and v2_historical.get("source_sha256") == V2_CHECKPOINT_SOURCE_SHA256
        and v2_historical.get("pdf_sha256") == V2_CHECKPOINT_PDF_SHA256
        and v2_historical.get("pypdf_pages") == V2_CHECKPOINT_PAGES
        and v2_historical.get("pdfplumber_pages") == V2_CHECKPOINT_PAGES,
        v2_historical,
        {
            "source_sha256": V2_CHECKPOINT_SOURCE_SHA256,
            "pdf_sha256": V2_CHECKPOINT_PDF_SHA256,
            "pages": V2_CHECKPOINT_PAGES,
            "scope": "historical only",
        },
        "pdf_history",
    )

    future_metadata = as_mapping(manifest.get(NEXT_CHECKPOINT_FIELD))
    future = future_checkpoint_pair_diagnostics(future_metadata)
    audit.check(
        "historical R-168 v1.2 / R-167 v2.1 checkpoint fields cross-bound",
        future["deferred_pair_valid"]
        or as_mapping(future.get("issued")).get("shared_manifest_exact") is True,
        future,
        "two explicit deferred records or identical issued shared metadata",
        "pdf_checkpoint",
    )
    audit.pending(
        "historical combined R-167 v2.1 / R-168 v1.2 checkpoint lifecycle",
        future["valid"],
        future,
        {
            "shared": True,
            "issued": True,
            "confined paired source/PDF": True,
            "hashes": "metadata-derived and exact",
            "pages": "positive metadata-derived count",
            "fresh": True,
            "pypdf": "all pages nonempty and all tokens",
            "pdfplumber": "all pages nonempty and all tokens",
        },
        "pdf_checkpoint",
    )
    v13_checkpoint_metadata = as_mapping(manifest.get("v1_3_checkpoint_synthesis"))
    v13_checkpoint = future_v1_3_checkpoint_diagnostics(v13_checkpoint_metadata)
    audit.check(
        "future R-168 v1.3 / R-167 v2.2 checkpoint fields cross-bound",
        v13_checkpoint["deferred_pair_valid"]
        or as_mapping(v13_checkpoint.get("issued")).get("shared_manifest_exact") is True,
        v13_checkpoint,
        "one exact deferred pair or identical issued shared metadata",
        "pdf_checkpoint",
    )
    audit.pending(
        "combined R-167 v2.2 / R-168 v1.3 checkpoint lifecycle",
        v13_checkpoint["valid"],
        v13_checkpoint,
        "one issued shared source/PDF pair after formal, generated, release and render gates",
        "pdf_checkpoint",
    )
    return {
        "historical_metadata": historical_metadata,
        "historical_valid": historical["valid"],
        "v2_historical_metadata": v2_metadata,
        "v2_historical_valid": v2_historical["valid"],
        "v3_historical_metadata": future_metadata,
        "v3_historical_valid": future["valid"],
        "future_metadata": v13_checkpoint_metadata,
        "future_cross_bound": v13_checkpoint["deferred_pair_valid"],
        "future_valid": v13_checkpoint["valid"],
    }


def validate_certificate(audit: Audit) -> str | None:
    text = read_text(CERTIFICATE, audit, "certificate", core=True)
    if text is None:
        return None
    require_tokens(
        text,
        "certificate exact authority chain",
        (
            EXPLORATION_ID,
            RESULT_NUMBER,
            RESULT_VERSION,
            RESULT_ID,
            AUDITED_COMMIT,
            FREEZE_SCHEMA,
            *NEGATIVE_IDS,
            *CLOSED_SUBGATES,
            *OPEN_GATES,
            "R-168 creates no tag",
            "does not verify a custodian signature",
            "does not fetch the remote commit",
            "physical Sector A or Pre-A",
            "all 28 hostile classes",
            "candidate_id",
            "source_id",
            "RFC 8785",
            "HMAC-SHA256",
            "EXTERNAL_CUSTODIAN",
            "normalized relative POSIX repository path",
            "HTTPS URL with no parsed hostname",
            "seven stable blockers",
            "non-load-bearing live observation",
            "not required to remain zero",
        ),
        audit,
        core=True,
        group="certificate",
    )
    audit.check(
        "certificate exact root-field list",
        ", ".join(ROOT_FIELDS) in " ".join(text.replace("`", "").split()),
        ", ".join(ROOT_FIELDS),
        "literal root-field sequence",
        "certificate",
    )
    flattened = " ".join(text.replace("`", "").split())
    for label, fields in (
        ("target", TARGET_FIELDS),
        ("commitment", COMMITMENT_FIELDS),
        ("disclosure", DISCLOSURE_FIELDS),
        ("prediction", PREDICTION_FIELDS),
        ("allowed input", ALLOWED_INPUT_FIELDS),
    ):
        audit.check(
            f"certificate exact {label} field list",
            ", ".join(fields) in flattened,
            ", ".join(fields),
            "literal field sequence",
            "certificate",
        )
    require_tokens(
        text,
        "certificate nested type and source firewall",
        (
            "exact field allowlists",
            "exact Boolean",
            "positive-integer",
            "digest/OID",
            "object or list before descent",
            "prediction is being issued",
            "score-eligible",
            "backed by an admitted map",
            "source_id in either discovery_ids or forbidden_fit_ids",
            "parent-traversing repository path",
            "structured rejection reports",
        ),
        audit,
        core=True,
        group="certificate",
    )
    require_tokens(
        text,
        "certificate v1.2 additive proof and no-overclaim contract",
        (
            *PRIOR_EXPLORATION_IDS,
            EXPLORATION_ID,
            *NEW_NEGATIVE_IDS,
            *NEW_CLOSED_SUBGATES,
            PHYSICAL_RESPONSE_GATE,
            "all ten hard rows",
            "seven hostile attempts",
            "8*3*2=48",
            "all exactly one",
            M2_SUCCESSOR_ID,
            "status=DESIGN_ONLY",
            "NOT_CREATED",
            "physical response channel",
            "controlled error budget",
            "No intermediate v1.2 PDF is issued",
            "3/25", "-9/50", "5/7", "11/7", "6/7",
            "57 exact", "48 deterministic", "embedded NUL", "4096",
            "128 characters", "denominator-one", "formal gate authority",
        ),
        audit,
        core=True,
        group="certificate",
    )
    require_tokens(
        text,
        "certificate v1.3 theorem hostile and no-overclaim contract",
        (
            EXPLORATION_ID, RESULT_VERSION, "T0", "claim_bearing: false",
            *NEW_CLOSED_SUBGATES, *NEW_NEGATIVE_IDS, *OPEN_SUCCESSOR_GATES,
            "GL(1", "H^2(T^3;R)", "3k harmonic", "fixed-amplitude",
            "400/7", "404/7", "1/100", "Upsilon -> Upsilon+D",
            "R(0)=0", "x^2", "x^3", "R_0(s),...,R_6(s)",
            "abs(log(lambda))", "4096", "v1_3_checkpoint_synthesis",
            "DEFERRED", "physical Sector A", "Pre-A",
        ),
        audit, core=True, group="certificate",
    )

    audit.check(
        "certificate exact residual hard-row cells",
        all(
            token in text.replace("`", "")
            for token in (
                "D01=FAIL",
                "D02=NOT_ADMITTED",
                "D03=NOT_ADMITTED",
                "D05=NOT_ADMITTED",
                "D06=NOT_TESTED",
                "D08=NOT_ADMITTED",
                "D04=FAIL",
            )
        ),
        True,
        True,
        "certificate",
    )
    audit.check(
        "certificate LF-only",
        CERTIFICATE.read_bytes().count(b"\r") == 0,
        CERTIFICATE.read_bytes().count(b"\r"),
        0,
        "certificate",
    )
    return text


def validate_formal(audit: Audit) -> dict[str, Any]:
    gates = read_text(REPO / "claims/GATES.md", audit, "gate registry", core=True)
    results = read_text(REPO / "RESULTS-LEDGER.md", audit, "results ledger", core=True)
    negatives = read_text(
        REPO / "negative-results/registry.md", audit, "negative registry", core=True
    )
    explorations = jsonl_records(
        REPO / "explorations/log.jsonl", audit, "exploration ledger"
    )
    changelog = jsonl_records(REPO / "changelog/log.jsonl", audit, "changelog")

    if gates is not None:
        for gate in CLOSED_SUBGATES:
            section = heading_section(gates, gate)
            if section is None:
                audit.pending(f"closed gate {gate}", False, None, "heading", "formal")
            else:
                audit.check(
                    f"closed gate {gate}",
                    "**Status:**" in section and text_has(section, "CLOSED"),
                    section[:700],
                    "explicit CLOSED status",
                    "formal",
                )
        for gate in OPEN_GATES:
            section = heading_section(gates, gate)
            if section is None:
                audit.pending(f"open gate {gate}", False, None, "heading", "formal")
            else:
                audit.check(
                    f"open gate {gate}",
                    "**Status:**" in section and text_has(section, "OPEN"),
                    section[:700],
                    "explicit OPEN status",
                    "formal",
                )

    result_section = heading_section(results, RESULT_NUMBER) if results else None
    result_ready = (
        result_section is not None
        and text_has(result_section, f"{RESULT_NUMBER} {RESULT_VERSION}")
        and text_has(result_section, RESULT_ID)
        and text_has(result_section, EXPLORATION_ID)
    )
    if not result_ready:
        audit.pending(
            "R-168 v1.3 result authority",
            False,
            None if result_section is None else result_section[:900],
            f"{RESULT_NUMBER} {RESULT_VERSION} / {RESULT_ID} / {EXPLORATION_ID}",
            "formal",
        )
        if result_section is not None:
            audit.check(
                "R-168 v1.2 authority retained while v1.3 is staged",
                text_has(result_section, "R-168 v1.2")
                and text_has(result_section, V1_2_EXPLORATION_ID),
                result_section[:900],
                "historical v1.2/EXP-000812 linkage",
                "formal_history",
            )
    else:
        require_tokens(
            result_section,
            "R-168 v1.3 result authority",
            (
                RESULT_NUMBER, RESULT_VERSION, RESULT_ID, EXPLORATION_ID,
                *PRIOR_EXPLORATION_IDS, "T0", *NEGATIVE_IDS,
                *NEW_CLOSED_SUBGATES, *OPEN_SUCCESSOR_GATES, PHYSICAL_RESPONSE_GATE,
                "real", "scalar", "one-Q", "tensor", "analytic", "six-stage",
                "physical Sector A", "Pre-A",
            ),
            audit,
            core=True,
        )

    negative_tokens = {
        V1_0_NEGATIVE_IDS[0]: (
            V1_0_NEGATIVE_IDS[0], V1_0_EXPLORATION_ID, RESULT_NUMBER,
            "current", "future",
        ),
        V1_1_NEGATIVE_IDS[0]: (
            V1_1_NEGATIVE_IDS[0], V1_1_EXPLORATION_ID, RESULT_NUMBER,
            "map-only", "substantively new", "not a no-go",
        ),
        V1_2_NEGATIVE_IDS[0]: (
            V1_2_NEGATIVE_IDS[0], V1_2_EXPLORATION_ID, RESULT_NUMBER,
            "linear", "quadratic", "contact", "physical", "not",
        ),
        NEW_NEGATIVE_IDS[0]: (NEW_NEGATIVE_IDS[0], EXPLORATION_ID, RESULT_NUMBER, "real", "scalar", "U1", "winding"),
        NEW_NEGATIVE_IDS[1]: (NEW_NEGATIVE_IDS[1], EXPLORATION_ID, RESULT_NUMBER, "one-Q", "phason", "physical"),
        NEW_NEGATIVE_IDS[2]: (NEW_NEGATIVE_IDS[2], EXPLORATION_ID, RESULT_NUMBER, "invertibility", "unit", "x^2", "x^3"),
        NEW_NEGATIVE_IDS[3]: (NEW_NEGATIVE_IDS[3], EXPLORATION_ID, RESULT_NUMBER, "six", "absolute", "relative", "log"),
    }
    if negatives is not None:
        for negative, tokens in negative_tokens.items():
            section = heading_section(negatives, negative)
            if section is None:
                audit.pending(
                    f"negative authority {negative}", False, None,
                    "unique section", "formal",
                )
            else:
                require_tokens(
                    section,
                    f"negative authority {negative}",
                    tokens,
                    audit,
                    core=True,
                )
        reused = heading_section(negatives, REUSED_NEGATIVE_IDS[0])
        audit.check(
            "reused negative authority retained",
            reused is not None,
            REUSED_NEGATIVE_IDS[0],
            "existing section",
            "formal_history",
        )

    records_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in explorations or []:
        identifier = row.get("id")
        if isinstance(identifier, str):
            records_by_id.setdefault(identifier, []).append(row)

    def one_record(identifier: str, group: str) -> dict[str, Any] | None:
        matches = records_by_id.get(identifier, [])
        if not matches:
            audit.pending(f"{identifier} unique record", False, 0, 1, group)
            return None
        audit.check(
            f"{identifier} unique record", len(matches) == 1, len(matches), 1, group
        )
        return matches[0] if len(matches) == 1 else None

    legacy = one_record(V1_0_EXPLORATION_ID, "formal_history")
    if legacy is not None:
        refs = as_mapping(legacy.get("formal_refs"))
        audit.check(
            "EXP-000807 retained exact identity sets",
            legacy.get("task_id") == TASK_ID
            and legacy.get("claim_ids") == list(CLAIM_IDS)
            and refs.get("results") == [RESULT_NUMBER]
            and refs.get("negatives") == list(V1_0_NEGATIVE_IDS)
            and set(legacy.get("gate_ids", [])) == set(V1_0_ALL_GATE_IDS),
            legacy,
            "historical v1.0 exact task, claim, result, negative and gate sets",
            "formal_history",
        )
    repair = one_record(HARDENING_EXPLORATION_ID, "formal_history")
    if repair is not None:
        refs = as_mapping(repair.get("formal_refs"))
        audit.check(
            "EXP-000808 retained exact repair identity sets",
            repair.get("task_id") == TASK_ID
            and repair.get("claim_ids") == list(CLAIM_IDS)
            and refs.get("results") == [RESULT_NUMBER]
            and refs.get("negatives") == []
            and tuple(repair.get("gate_ids", ())) == HARDENING_GATE_IDS,
            repair,
            "historical repair identity and gate sets",
            "formal_history",
        )
    v1_1 = one_record(V1_1_EXPLORATION_ID, "formal_history")
    if v1_1 is not None:
        refs = as_mapping(v1_1.get("formal_refs"))
        audit.check(
            "EXP-000810 retained exact v1.1 identity sets",
            v1_1.get("task_id") == TASK_ID
            and v1_1.get("claim_ids") == list(CLAIM_IDS)
            and refs.get("results") == [RESULT_NUMBER]
            and refs.get("negatives") == list(V1_1_NEGATIVE_IDS)
            and tuple(v1_1.get("gate_ids", ())) == V1_1_EXPLORATION_GATES,
            v1_1,
            "historical v1.1 exact task, claim, result, negative and gate order",
            "formal_history",
        )

    v1_2 = one_record(V1_2_EXPLORATION_ID, "formal_history")
    if v1_2 is not None:
        refs = as_mapping(v1_2.get("formal_refs"))
        audit.check(
            "EXP-000812 retained exact v1.2 identity sets",
            v1_2.get("task_id") == TASK_ID
            and v1_2.get("claim_ids") == list(CLAIM_IDS)
            and refs.get("results") == [RESULT_NUMBER]
            and refs.get("negatives") == list(V1_2_NEGATIVE_IDS)
            and tuple(v1_2.get("gate_ids", ())) == V1_2_EXPLORATION_GATES,
            v1_2, "historical v1.2 exact identity order", "formal_history",
        )

    current = one_record(EXPLORATION_ID, "formal")
    if current is not None:
        refs = as_mapping(current.get("formal_refs"))
        required_gates = {*NEW_CLOSED_SUBGATES, *OPEN_SUCCESSOR_GATES, PARENT_GATE, PHYSICAL_RESPONSE_GATE}
        audit.check(
            "EXP-000814 exact additive authority bindings",
            current.get("task_id") == TASK_ID
            and current.get("claim_ids") == list(CLAIM_IDS)
            and refs.get("results") == [RESULT_NUMBER]
            and refs.get("negatives") == list(NEW_NEGATIVE_IDS)
            and required_gates <= set(as_list(current.get("gate_ids"))),
            current,
            {
                "task": TASK_ID, "claims": CLAIM_IDS, "result": RESULT_NUMBER,
                "negative": NEW_NEGATIVE_IDS, "required_gates": sorted(required_gates),
            },
            "formal",
        )
        require_tokens(
            json.dumps(current, sort_keys=True),
            "EXP-000814 proof and boundary",
            (
                "real", "scalar", "U1", "one-Q", "phason", "tensor",
                "analytic", "six-stage", "x^2", "x^3", "hostile",
                "physical response", "candidate", "external freeze",
                "physical Sector A", "Pre-A",
            ),
            audit,
            core=True,
        )

    def event_claim_set(event: Mapping[str, Any]) -> set[str]:
        return set(as_list(event.get("claim_ids")))

    expected_events = (
        (
            "R-168 v1.0 theorem changelog retained",
            {CLAIM_IDS[0], V1_0_EXPLORATION_ID, RESULT_NUMBER},
            V1_0_NEGATIVE_IDS,
            {repo_path(PRIMARY), repo_path(INDEPENDENT)},
            "formal_history",
        ),
        (
            "R-168 v1.0 hardening changelog retained",
            {CLAIM_IDS[0], V1_0_EXPLORATION_ID, HARDENING_EXPLORATION_ID, RESULT_NUMBER},
            V1_0_NEGATIVE_IDS,
            {repo_path(PRIMARY), repo_path(INDEPENDENT), repo_path(SCRIPT)},
            "formal_history",
        ),
        (
            "R-168 v1.1 theorem changelog retained",
            {CLAIM_IDS[0], V1_1_EXPLORATION_ID, RESULT_NUMBER},
            V1_1_NEGATIVE_IDS,
            {repo_path(PRIMARY), repo_path(INDEPENDENT), repo_path(SCRIPT)},
            "formal_history",
        ),        (
            "R-168 v1.2 theorem changelog retained",
            {CLAIM_IDS[0], V1_2_EXPLORATION_ID, RESULT_NUMBER},
            V1_2_NEGATIVE_IDS,
            {repo_path(PRIMARY), repo_path(INDEPENDENT), repo_path(SCRIPT)},
            "formal_history",
        ),
    )
    historical_event_counts: dict[str, int] = {}
    for label, identities, negative_set, scripts, group in expected_events:
        matches = [event for event in changelog or [] if event_claim_set(event) == identities]
        historical_event_counts[label] = len(matches)
        audit.check(f"{label} unique", len(matches) == 1, len(matches), 1, group)
        if len(matches) == 1:
            event = matches[0]
            audit.check(
                f"{label} exact authorities",
                event.get("neg_results") == list(negative_set)
                and scripts <= set(as_list(event.get("scripts"))),
                event,
                {"negatives": negative_set, "scripts": scripts},
                group,
            )

    v1_3_events = [
        event
        for event in changelog or []
        if event_claim_set(event) == {CLAIM_IDS[0], EXPLORATION_ID, RESULT_NUMBER}
    ]
    if not v1_3_events:
        audit.pending("R-168 v1.3 changelog", False, 0, 1, "formal")
    else:
        audit.check(
            "R-168 v1.3 changelog unique",
            len(v1_3_events) == 1,
            len(v1_3_events),
            1,
            "formal",
        )
    if len(v1_3_events) == 1:
        event = v1_3_events[0]
        event_negatives = as_list(event.get("neg_results"))
        event_scripts = as_list(event.get("scripts"))
        expected_event_scripts = {repo_path(PRIMARY), repo_path(INDEPENDENT)}
        audit.check(
            "R-168 v1.3 changelog theorem authority sets",
            len(event_negatives) == len(NEW_NEGATIVE_IDS)
            and set(event_negatives) == set(NEW_NEGATIVE_IDS)
            and set(event_scripts) == expected_event_scripts,
            {"negatives": event_negatives, "scripts": event_scripts},
            {
                "negatives": sorted(NEW_NEGATIVE_IDS),
                "theorem_scripts": sorted(expected_event_scripts),
            },
            "formal",
        )
        require_tokens(
            event.get("raw", ""),
            "R-168 v1.3 changelog boundary",
            (
                "raw real-line", "internal-U1", "one-Q", "tensor", "analytic",
                "six-stage", "creates no compact action", "physical response",
                "physical Sector A", "Pre-A remain open",
            ),
            audit,
            core=True,
        )

    return {
        "exploration_count": len(explorations or []),
        "changelog_count": len(changelog or []),
        "v1_3_exploration_matches": len(records_by_id.get(EXPLORATION_ID, [])),
        "v1_2_exploration_matches": len(records_by_id.get(V1_2_EXPLORATION_ID, [])),
        "v1_1_exploration_matches": len(records_by_id.get(V1_1_EXPLORATION_ID, [])),
        "legacy_exploration_matches": len(records_by_id.get(V1_0_EXPLORATION_ID, [])),
        "hardening_exploration_matches": len(records_by_id.get(HARDENING_EXPLORATION_ID, [])),
        "v1_3_event_matches": len(v1_3_events),
        "historical_event_counts": historical_event_counts,
    }


def validate_locator(
    path: Path,
    schema: str,
    required_ids: Iterable[str],
    audit: Audit,
    label: str,
) -> dict[str, Any] | None:
    payload = load_json(path, audit, label)
    if payload is None:
        return None
    entries = [row for row in as_list(payload.get("entries")) if isinstance(row, dict)]
    identifiers = [row.get("id") for row in entries]
    audit.pending(
        f"{label} current",
        payload.get("schema") == schema
        and payload.get("count") == len(entries)
        and all(identifier in identifiers for identifier in required_ids),
        {
            "schema": payload.get("schema"),
            "count": payload.get("count"),
            "entries": len(entries),
            "required_present": {
                identifier: identifier in identifiers for identifier in required_ids
            },
        },
        {"schema": schema, "count": "len(entries)", "required": list(required_ids)},
        "generated",
    )
    return payload


def validate_catalog(audit: Audit) -> dict[str, Any]:
    manifest = load_json(
        REPO / "verification/catalog/index.json", audit, "catalog manifest"
    )
    if manifest is None:
        return {"total": 0, "inventory": ""}
    shards = [row for row in as_list(manifest.get("shards")) if isinstance(row, dict)]
    valid: list[bool] = []
    payloads: list[dict[str, Any]] = []
    for shard in shards:
        relative = shard.get("path")
        if not isinstance(relative, str):
            valid.append(False)
            continue
        path = REPO / relative
        payload = load_json(path, audit, f"catalog shard {relative}")
        if payload is None:
            valid.append(False)
            continue
        entries = as_list(payload.get("entries"))
        payloads.append(payload)
        valid.append(
            artifact_sha256(path) == shard.get("sha256")
            and payload.get("count") == shard.get("count") == len(entries)
        )
    audit.pending(
        "catalog manifest and shards current",
        manifest.get("schema") == "tect/catalog-manifest/2.0"
        and bool(shards)
        and len(valid) == len(shards)
        and all(valid)
        and sum(int(row.get("count", 0)) for row in shards)
        == manifest.get("total"),
        {
            "shards": len(shards),
            "valid": sum(valid),
            "total": manifest.get("total"),
        },
        "valid shard hashes/counts and total",
        "generated",
    )
    inventory = json.dumps(payloads, sort_keys=True)
    all_entries = [
        row
        for payload in payloads
        for row in as_list(payload.get("entries"))
        if isinstance(row, dict)
    ]
    catalog_bindings: dict[str, Any] = {}
    catalog_current = True
    for artifact in (
        PRIMARY,
        INDEPENDENT,
        SCRIPT,
        MANIFEST,
        CERTIFICATE,
        PRIMARY_STORED,
        INDEPENDENT_STORED,
        DEFAULT_OUTPUT,
    ):
        relative = repo_path(artifact)
        matches = [row for row in all_entries if row.get("path") == relative]
        expected_binding = (
            {
                "bytes": artifact.stat().st_size,
                "sha256_12": artifact_sha256(artifact)[:12],
            }
            if artifact.is_file()
            else None
        )
        exact = (
            len(matches) == 1
            and expected_binding is not None
            and matches[0].get("bytes") == expected_binding["bytes"]
            and matches[0].get("sha256_12") == expected_binding["sha256_12"]
        )
        catalog_current = catalog_current and exact
        catalog_bindings[relative] = {
            "catalog": matches,
            "expected": expected_binding,
            "exact": exact,
        }
    audit.pending(
        "catalog R-168 artifact bytes and hashes current",
        catalog_current,
        catalog_bindings,
        "one exact current bytes/sha256_12 entry per proof, verifier, authority, and run artifact",
        "generated",
    )
    require_tokens(
        inventory,
        "catalog R-168 artifacts",
        (
            repo_path(PRIMARY),
            repo_path(INDEPENDENT),
            repo_path(SCRIPT),
            repo_path(MANIFEST),
            repo_path(CERTIFICATE),
            repo_path(PRIMARY_STORED),
            repo_path(INDEPENDENT_STORED),
            repo_path(DEFAULT_OUTPUT),
        ),
        audit,
        group="generated",
    )
    index = read_text(REPO / "catalog/INDEX.md", audit, "catalog reader")
    if index is not None:
        require_tokens(
            index,
            "catalog reader total",
            (f"{manifest.get('total')} artefacts",),
            audit,
            group="generated",
        )
    return {"total": manifest.get("total", 0), "inventory": inventory}


def validate_generated(formal: dict[str, Any], audit: Audit) -> dict[str, Any]:
    results = validate_locator(
        REPO / "results/index.json",
        "tect/results-index/1.0",
        (RESULT_NUMBER,),
        audit,
        "result locator",
    )
    negatives = validate_locator(
        REPO / "negative-results/index.json",
        "tect/negative-index/1.0",
        NEGATIVE_IDS,
        audit,
        "negative locator",
    )
    gates = validate_locator(
        REPO / "claims/gates-index.json",
        "tect/gate-index/1.0",
        ALL_GATE_IDS,
        audit,
        "gate locator",
    )
    changelog = load_json(REPO / "changelog/index.json", audit, "changelog locator")
    if changelog is not None:
        recent = as_list(changelog.get("recent"))
        audit.pending(
            "changelog locator current",
            changelog.get("schema") == "tect/changelog-index/2.0"
            and changelog.get("total") == formal.get("changelog_count")
            and any(
                isinstance(row, dict)
                and EXPLORATION_ID in row.get("claim_ids", [])
                for row in recent
            ),
            {
                "schema": changelog.get("schema"),
                "total": changelog.get("total"),
                "expected_total": formal.get("changelog_count"),
                "recent": len(recent),
            },
            "current total and recent R-168 v1.3 theorem event",
            "generated",
        )

    result_count = as_mapping(results).get("count")
    negative_count = as_mapping(negatives).get("count")
    gate_count = as_mapping(gates).get("count")
    generated_texts = (
        (
            REPO / "results/INDEX.md",
            "result reader",
            (RESULT_NUMBER, f"{result_count} registered results"),
        ),
        (
            REPO / "negative-results/INDEX.md",
            "negative reader",
            (*NEGATIVE_IDS, f"{negative_count} registered records"),
        ),
        (
            REPO / "claims/GATES-INDEX.md",
            "gate reader",
            (f"{gate_count} registered definitions",),
        ),
        (
            REPO / "management/INDEX.md",
            "management reader",
            (
                f"{result_count} reusable results",
                f"{negative_count} negative/audit records",
                f"{gate_count} registered gates/hypotheses",
            ),
        ),
        (
            REPO / "changelog/INDEX.md",
            "changelog reader",
            (RESULT_NUMBER, EXPLORATION_ID, f"{formal.get('changelog_count')} accepted events"),
        ),
    )
    for path, label, tokens in generated_texts:
        text = read_text(path, audit, label)
        if text is not None:
            require_tokens(text, label, tokens, audit, group="generated")

    proof_tokens = (
        RESULT_NUMBER,
        EXPLORATION_ID,
        HARDENING_EXPLORATION_ID,
        *NEGATIVE_IDS,
        *ALL_GATE_IDS,
    )
    proof_text = read_text(
        REPO / "theory/proof-evidence-map.md", audit, "proof-evidence map"
    )
    if proof_text is not None:
        require_tokens(
            proof_text, "proof-evidence map R-168 linkage", proof_tokens, audit, group="generated"
        )
    proof_json = load_json(
        REPO / "verification/proof-evidence-map.json", audit, "proof-evidence JSON"
    )
    if proof_json is not None:
        require_tokens(
            json.dumps(proof_json, sort_keys=True),
            "proof-evidence JSON R-168 linkage",
            proof_tokens,
            audit,
            group="generated",
        )
    compact = read_text(
        REPO / "theory/proof-evidence/INDEX.md", audit, "compact proof reader"
    )
    if compact is not None:
        require_tokens(
            compact,
            "compact proof reader counts",
            (
                f"{result_count} results",
                f"{negative_count} negatives/audits",
                f"{formal.get('exploration_count')} proof explorations",
                f"{formal.get('changelog_count')} accepted events",
            ),
            audit,
            group="generated",
        )

    status = load_json(
        REPO / "claims/C6-SPACETIME-SIGNATURE/status.json",
        audit,
        "C6 status",
        core=True,
    )
    if status is not None:
        audit.check("C6 tier unchanged", status.get("tier") == "T1", status.get("tier"), "T1", "claim_firewall")
        audit.check("C6 lifecycle unchanged", status.get("lifecycle") == "ACTIVE", status.get("lifecycle"), "ACTIVE", "claim_firewall")
        audit.check(
            "C6 open gates unchanged",
            status.get("open_gates") == ["C6-BCC-PREMISE-BLOCKED"],
            status.get("open_gates"),
            ["C6-BCC-PREMISE-BLOCKED"],
            "claim_firewall",
        )
    catalog = validate_catalog(audit)
    return {
        "result_count": result_count,
        "negative_count": negative_count,
        "gate_count": gate_count,
        "exploration_count": formal.get("exploration_count"),
        "changelog_count": formal.get("changelog_count"),
        "catalog_total": catalog.get("total"),
    }


def build_payload(staged: bool = False) -> dict[str, Any]:
    audit = Audit(staged)
    manifest = load_json(MANIFEST, audit, "manifest", core=True) or {}
    checkpoint_state: dict[str, Any] = {}
    if manifest:
        checkpoint_state = validate_manifest(manifest, audit)
    validate_certificate(audit)
    validate_firewall(audit)

    components: dict[str, dict[str, Any]] = {}
    sentinels: dict[str, dict[str, Any]] = {}
    with tempfile.TemporaryDirectory(prefix="tect-exp814-integrated-") as directory:
        temporary = Path(directory)
        for label, component in (("primary", PRIMARY), ("independent", INDEPENDENT)):
            result = run_fresh_pair(component, temporary, audit, label)
            if result is not None:
                components[label], sentinels[label] = result

    stored_against_fresh(PRIMARY_STORED, components.get("primary"), audit, "primary")
    stored_against_fresh(
        INDEPENDENT_STORED, components.get("independent"), audit, "independent"
    )
    if "primary" in components:
        primary_count = expected_component_assertion_count(components["primary"], "primary")
        validate_fresh_sentinel(sentinels["primary"], "primary", primary_count, audit)
        validate_component(
            components["primary"], "primary", PRIMARY_SCHEMA, primary_count, audit
        )
        validate_source_hashes(
            components["primary"], (PRIMARY, MANIFEST, CERTIFICATE), audit, "primary"
        )
    if "independent" in components:
        independent_count = expected_component_assertion_count(
            components["independent"], "independent"
        )
        validate_fresh_sentinel(
            sentinels["independent"], "independent", independent_count, audit
        )
        validate_component(
            components["independent"], "independent", INDEPENDENT_SCHEMA,
            independent_count, audit,
        )
        validate_source_hashes(
            components["independent"],
            INDEPENDENT_HASH_INPUTS,
            audit,
            "independent",
        )

    cross: dict[str, Any] = {}
    if "primary" in components and "independent" in components:
        cross = compare_components(
            components["primary"], components["independent"], manifest, audit
        )
    else:
        audit.check(
            "fresh cross-comparison available",
            False,
            sorted(components),
            ["independent", "primary"],
            "cross_core",
        )

    formal = validate_formal(audit)
    generated = validate_generated(formal, audit)
    passed = sum(row["status"] == "PASS" for row in audit.rows)
    source_paths = (
        SCRIPT,
        PRIMARY,
        INDEPENDENT,
        MANIFEST,
        R167_MANIFEST,
        CERTIFICATE,
        CHECKPOINT_SOURCE,
        CHECKPOINT_PDF,
        V2_CHECKPOINT_SOURCE,
        V2_CHECKPOINT_PDF,
        PRIMARY_STORED,
        INDEPENDENT_STORED,
        DEFAULT_OUTPUT,
    )
    source_hashes = {
        repo_path(path): artifact_sha256(path)
        for path in source_paths
        if path.is_file()
    }
    return {
        "schema": INTEGRATED_SCHEMA,
        "script_version": __version__,
        "task_id": TASK_ID,
        "claim_ids": list(CLAIM_IDS),
        "claim_bearing": False,
        "exploration_id": EXPLORATION_ID,
        "prior_exploration_ids": list(PRIOR_EXPLORATION_IDS),
        "hardening_exploration_id": HARDENING_EXPLORATION_ID,
        "parent_explorations": list(PARENT_EXPLORATIONS),
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "negative_ids": list(NEGATIVE_IDS),
        "prior_negative_ids": list(PRIOR_NEGATIVE_IDS),
        "new_negative_ids": list(NEW_NEGATIVE_IDS),
        "reused_negative_ids": list(REUSED_NEGATIVE_IDS),
        "closed_subgates": list(CLOSED_SUBGATES),
        "new_closed_subgates": list(NEW_CLOSED_SUBGATES),
        "open_gates": list(OPEN_GATES),
        "parent_gate": PARENT_GATE,
        "verdict": audit.verdict,
        "summary": {
            "passed": passed,
            "failed": len(audit.failures),
            "missing": len(audit.missing),
            "total": len(audit.rows),
        },
        "assertions": {
            "passed": passed,
            "failed": len(audit.failures),
            "missing": len(audit.missing),
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "component_summaries": {
            label: {
                "schema": payload.get("schema"),
                "verdict": payload.get("verdict"),
                "summary": payload.get("summary"),
            }
            for label, payload in sorted(components.items())
        },
        "normalized_fresh_sentinels": sentinels,
        "cross_derived": cross,
        "formal_workflow": formal,
        "generated_surfaces": generated,
        "pdf_efficiency": {
            "dedicated_R168_source_required": False,
            "dedicated_R168_PDF_required": False,
            "dedicated_R168_PDF_created_by_verifier": False,
            "per_lemma_or_intermediate_v1_3_PDF_issued": False,
            "historical_v1_9_v1_0_checkpoint_strictly_validated": checkpoint_state.get(
                "historical_valid", False
            ),
            "later_v2_2_v1_3_checkpoint_deferred_until_layers_pass": not checkpoint_state.get(
                "future_valid", False
            ),
            "later_v2_2_v1_3_checkpoint_strictly_validated": checkpoint_state.get(
                "future_valid", False
            ),
            "shared_with_R167_manifest": True,
            "historical_manifest_metadata": checkpoint_state.get("historical_metadata", {}),
            "historical_v2_v1_1_checkpoint_strictly_validated": checkpoint_state.get("v2_historical_valid", False),
            "historical_v2_v1_1_manifest_metadata": checkpoint_state.get("v2_historical_metadata", {}),
            "historical_v2_1_v1_2_checkpoint_strictly_validated": checkpoint_state.get("v3_historical_valid", False),
            "historical_v2_1_v1_2_manifest_metadata": checkpoint_state.get("v3_historical_metadata", {}),
            "future_cross_bound": checkpoint_state.get("future_cross_bound", False),
            "future_manifest_metadata": checkpoint_state.get("future_metadata", {}),
        },
        "scope": {
            "freeze_schema_shape_validated": True,
            "current_tree_readiness_audited": True,
            "current_version_map_only_empty_set_closed": True,
            "finite_torus_mathematical_fingerprint_closed": True,
            "linear_probe_second_order_response_nonidentifiability_closed": True,
            "minimum_physical_response_contract_schema_closed": True,
            "real_scalar_internal_u1_triviality_and_no_intrinsic_winding_closed": True,
            "one_q_auxiliary_phason_curvature_and_finite_torus_secant_closed": True,
            "tensor_contact_shift_nonidentifiability_closed": True,
            "analytic_integer_exponent_transport_closed": True,
            "six_stage_relative_log_slope_error_transport_closed": True,
            "actual_freeze_record_created": False,
            "git_tag_created": False,
            "external_target_commitment_present": False,
            "custodian_signature_cryptographically_verified": False,
            "remote_commit_fetched_and_verified": False,
            "remote_annotated_tag_fetched_and_verified": False,
            "remote_tag_ref_fetched_and_verified": False,
            "admitted_current_microscopic_map_present": False,
            "prospective_prediction_present": False,
            "m2_v1_candidate_created": False,
            "m2_physical_response_channel_present": False,
            "m2_controlled_physical_error_bound_present": False,
            "parent_gate_closed": False,
            "C6_advanced": False,
            "CP1_complete": False,
            "physical_Sector_A_complete": False,
            "Pre_A_complete": False,
        },
        "source_hashes": source_hashes,
        "missing_authorities": audit.missing,
        "failures": audit.failures,
        "boundary": manifest.get("no_overclaim"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--staged",
        action="store_true",
        help="report absent stored/formal/generated authorities as MISSING",
    )
    parser.add_argument(
        "--no-store", action="store_true", help="run without writing result JSON"
    )
    arguments = parser.parse_args()
    payload = build_payload(arguments.staged)
    digest = hashlib.sha256(canonical_payload(payload)).hexdigest()
    if not arguments.no_store:
        atomic_json(arguments.output, payload)
    summary = payload["summary"]
    print(
        f"{EXPLORATION_ID}/{RESULT_NUMBER}-{RESULT_VERSION} INTEGRATED "
        f"{payload['verdict']} {summary['passed']}/{summary['total']} "
        f"failed={summary['failed']} missing={summary['missing']}"
    )
    print("NO-STORE" if arguments.no_store else arguments.output)
    print("payload_sha256: " + digest)
    print("script_sha256: " + normalized_sha256(SCRIPT))
    for blocker in payload["missing_authorities"]:
        print("BLOCKER " + blocker)
    for failure in payload["failures"]:
        print("FAILURE " + failure)
    if payload["verdict"] == "FAIL":
        return 1
    if payload["verdict"] != "PASS" and not arguments.staged:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
