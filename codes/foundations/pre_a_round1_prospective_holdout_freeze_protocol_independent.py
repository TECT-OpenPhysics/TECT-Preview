#!/usr/bin/env python3
"""Independent verifier for the R-168 prospective-holdout protocol.

This stdlib-only implementation reconstructs the audited Round-1 state and a
synthetic freeze-schema fixture without importing the primary verifier or
reading a primary result JSON.  Its most important fail-closed invariant is
that schema shape is not external verification: every purported real freeze
is rejected with ``EXTERNAL_VERIFICATION_REQUIRED`` until a separate process
cryptographically verifies the custodian signature and independently fetches
and verifies the remote commit, annotated tag object, and tag ref.

No target, freeze record, prediction, score, or git tag is created here.

Version history:
  1.5.0 (2026-08-11): independently derive the v1.3 U1/winding, phason/secant, tensor-contact, analytic-order, and relative log-slope suite with stdlib Fraction only.
  1.4.0 (2026-08-11): independently harden exact artifact roles, canonical
        reduced rationals, source firewalls, verifier/error bindings,
        order-insensitive metamorphics, and deterministic hostile fuzz.
  1.3.0 (2026-08-11): independently prove the fixed-linear-probe contact
        curvature shift by integer cross-products and validate the minimum
        physical-response successor contract with a separate parser.
  1.2.0 (2026-08-11): independently reconstruct the current-version map-empty
        set, integer 48-component fingerprint, response countermodels, and
        DESIGN_ONLY successor hostile suite.
  1.1.0 (2026-08-11): exact nested allowlists, candidate-bound prediction,
        source-ID firewall, repository-path confinement, hostile alias/type
        fixtures, and non-load-bearing live freeze-tag observation.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import os
import re
import subprocess
import tempfile
from fractions import Fraction
from itertools import product
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable
from urllib.parse import urlparse


__version__ = "1.5.0"
__first_issued__ = "2026-08-11"

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
PRIMARY_SCRIPT = REPO / "codes/foundations/pre_a_round1_prospective_holdout_freeze_protocol.py"
SLUG = "pre-a-round1-prospective-holdout-freeze-protocol"
RESULT_SCHEMA = f"tect/{SLUG}-independent-result/1.0"
FREEZE_SCHEMA = "tect/pre-a-round1-prospective-holdout-freeze/1.0"
TASK_ID = "T-054"
CLAIM_IDS = ("C6-SPACETIME-SIGNATURE",)
RESULT_NUMBER = "R-168"
RESULT_VERSION = "v1.3"
RESULT_ID = "PA-ROUND1-PROSPECTIVE-HOLDOUT-FREEZE-PROTOCOL-AND-CURRENT-TREE-READINESS-AUDIT"
EXPLORATION_ID = "EXP-000814"
PRIOR_EXPLORATION_IDS = ("EXP-000807", "EXP-000808", "EXP-000810", "EXP-000812")
AUDITED_COMMIT = "99157442831c0e44d425b5d5f8cd78856c57da53"
PARENT_GATE = "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE"
MAP_ONLY_NEGATIVE_ID = "NG-2026-08-11-PRE-A-ROUND1-CURRENT-VERSION-MAP-ONLY-ADMISSION-REPAIR"
LINEAR_PROBE_NEGATIVE_ID = "NG-2026-08-11-PRE-A-M2-LANE-Q-LINEAR-SOURCE-AUTOMATIC-PHYSICAL-STIFFNESS-RESPONSE"
PRIOR_NEGATIVE_IDS = (
    "NG-2026-08-11-PRE-A-ROUND1-CURRENT-TREE-PROSPECTIVE-HOLDOUT-NONEXISTENCE",
    MAP_ONLY_NEGATIVE_ID, LINEAR_PROBE_NEGATIVE_ID,
)
NEW_NEGATIVE_IDS = (
    "NG-2026-08-11-PRE-A-M2-V0-ONE-REAL-SCALAR-AUTOMATIC-INTERNAL-U1-WINDING-AND-HELICITY",
    "NG-2026-08-11-PRE-A-M2-ONE-Q-PHASON-AUTOMATIC-PHYSICAL-SUPERFLUID-DENSITY",
    "NG-2026-08-11-PRE-A-M2-POSITIVE-LOCAL-INVERTIBILITY-AUTOMATIC-UNIT-EXPONENT",
    "NG-2026-08-11-PRE-A-M2-SIX-ABSOLUTE-ERRORS-AUTOMATIC-LOG-SLOPE-CONTROL",
)
NEGATIVE_IDS = PRIOR_NEGATIVE_IDS + NEW_NEGATIVE_IDS
REUSED_NEGATIVE_IDS = ("NG-2026-08-09-PRE-A-ROUND1-UNFROZEN-TOURNAMENT-SELECTION",)
MAP_ONLY_CLOSED_CHILD = "PA-ROUND1-CURRENT-VERSION-M1-M2-M5-MAP-ONLY-ADMISSION-EMPTY-SET"
FINGERPRINT_CLOSED_CHILD = "PA-M2-CI8-FINITE-TORUS-GAUSSIAN-DISPERSION-FINGERPRINT"
LINEAR_PROBE_CLOSED_CHILD = "PA-M2-CI8-LINEAR-PROBE-SECOND-ORDER-RESPONSE-NONIDENTIFIABILITY"
PHYSICAL_CONTRACT_CLOSED_CHILD = "PA-M2-CI8-PHYSICAL-RESPONSE-SUCCESSOR-MINIMUM-CONTRACT-SCHEMA"
PRIOR_CLOSED_SUBGATES = (
    "PA-ROUND1-COMMON-ESTIMAND-AND-CANDIDATE-MAP-SCHEMA",
    "PA-ROUND1-PROSPECTIVE-FREEZE-PROVENANCE-PROTOCOL",
    "PA-ROUND1-TARGET-INDEPENDENCE-AND-ANTI-LEAKAGE-SCHEMA-VALIDATOR",
    "PA-ROUND1-CURRENT-CANDIDATE-MAP-ADMISSION-EMPTY-SET-AUDIT",
    MAP_ONLY_CLOSED_CHILD, FINGERPRINT_CLOSED_CHILD,
    LINEAR_PROBE_CLOSED_CHILD, PHYSICAL_CONTRACT_CLOSED_CHILD,
)
NEW_CLOSED_SUBGATES = (
    "PA-M2-CI8-V0-REAL-SCALAR-INTERNAL-U1-TRIVIALITY-AND-NO-INTRINSIC-WINDING",
    "PA-M2-CI8-ONE-Q-AUXILIARY-PHASON-CURVATURE-AND-FINITE-TORUS-SECANT",
    "PA-M2-CI8-HELICITY-TENSOR-CONTACT-SHIFT-NONIDENTIFIABILITY",
    "PA-M2-CI8-ANALYTIC-MAP-INTEGER-EXPONENT-TRANSPORT",
    "PA-M2-CI8-SIX-STAGE-RELATIVE-LOG-SLOPE-ERROR-TRANSPORT",
)
CLOSED_SUBGATES = PRIOR_CLOSED_SUBGATES + NEW_CLOSED_SUBGATES
PHYSICAL_RESPONSE_GATE = "PA-M2-CI8-PHYSICAL-RESPONSE-CHANNEL-AND-ERROR-BOUND"
OPEN_SUCCESSOR_GATES = (
    "PA-M2-SUCCESSOR-SUBSTANTIVE-COMPACT-ACTION-BACKGROUND-PROBE-AND-WINDING-LAW",
    "PA-M2-SUCCESSOR-ORDERED-STATE-PHYSICAL-MODE-AND-RESPONSE-LIMIT",
    "PA-M2-SUCCESSOR-SIX-TERM-CRITICAL-ESTIMAND-ERROR-BUDGET",
)
OPEN_GATES = (
    PARENT_GATE,
    "PA-ROUND1-PER-PARAMETER-COMMON-INPUT-LEDGER",
    "PA-ROUND1-INDEPENDENT-CUSTODIAN-OPAQUE-TARGET-COMMITMENT",
    "PA-ROUND1-ADMISSIBLE-MICROSCOPIC-CANDIDATE-MAP-AND-FROZEN-PREDICTION",
    "PA-ROUND1-CRYPTOGRAPHIC-CUSTODIAN-SIGNATURE-AND-REMOTE-FREEZE-VERIFICATION",
    PHYSICAL_RESPONSE_GATE, *OPEN_SUCCESSOR_GATES,
)
M2_SUCCESSOR_ID = "PA-M2-CI8-RS-DISPERSION-MAP-v1"
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
CONTESTANT_FIELDS = (
    "candidate_id",
    "role",
    "score_eligible_as_microscopic_winner",
    "path",
    "normalized_sha256",
)
EVIDENCE_FIELDS = (
    "path",
    "normalized_sha256",
    "discovery_ids",
    "forbidden_fit_ids",
    "discovery_independence_groups",
    "calibration_independence_groups",
)
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
OBSERVABLE_FIELDS = ("common_estimand", "candidate_maps")
ESTIMAND_FIELDS = ("id", "definition", "units", "raw_estimator")
RAW_ESTIMATOR_FIELDS = ("path", "sha256")
CANDIDATE_MAP_FIELDS = (
    "candidate_id",
    "status",
    "map_statement",
    "domain",
    "state_and_reference",
    "units_map",
    "limit_order",
    "nuisance_inputs",
    "proof_refs",
    "script_path",
    "script_sha256",
)
ROBUSTNESS_FIELDS = (
    "volume",
    "boundary",
    "regulator",
    "coefficients",
    "implementation",
)
PROVENANCE_FIELDS = (
    "freeze_commit_oid",
    "remote_url",
    "remote_commit_sha",
    "remote_observed_at_utc",
    "annotated_tag",
    "remote_ref",
    "tag_object_oid",
)
SCORING_FIELDS = (
    "status",
    "target_path",
    "result_path",
    "scorer_path",
    "scorer_sha256",
)

AUTHORITY_MANIFEST = (
    REPO / "strategy/pre-a-round1-prospective-holdout-freeze-protocol-manifest.json"
)
AUTHORITY_CERTIFICATE = (
    REPO
    / "strategy/pre-a-round1-prospective-holdout-freeze-protocol-certificate-260811.md"
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
GATES = REPO / "claims/GATES.md"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
RESULTS_LEDGER = REPO / "RESULTS-LEDGER.md"
EXPLORATION_LOG = REPO / "explorations/log.jsonl"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-11-independent-{SLUG}/result.json"
)

EXPECTED_CANDIDATES = (
    "PA-M0-ESTABLISHED-LOW-ENERGY-BASELINE-v0",
    "PA-M1-CURRENT-PINNED-PRODUCTION-FUNCTIONAL-v0",
    "PA-M2-CI8-RS-v0",
    "PA-M5-NL3-SV-v0",
)
MICROSCOPIC_CANDIDATES = EXPECTED_CANDIDATES[1:]
ELIGIBLE_ROLES = {
    "CURRENT_TECT_BENCHMARK",
    "LOCAL_FINITE_WAVENUMBER_ALTERNATIVE",
    "NONLOCAL_SCREENED_SHELL_ALTERNATIVE",
    "COMPACT_GAUGE_ALTERNATIVE",
    "GEOMETRIC_OR_TOPOLOGICAL_ALTERNATIVE",
}
INPUT_CLASSES = {
    "INSERTED",
    "FITTED",
    "MATCHED",
    "CALIBRATION",
    "DERIVED",
    "PREDICTED",
    "VISIBLE_VALIDATION",
    "NOT_AVAILABLE",
}
FORBIDDEN_VALUE_KEYS = {
    "target_value",
    "reported_value",
    "observed_value",
    "target_interval",
    "reported_interval",
    "observed_interval",
    "target_payload",
    "sealed_payload",
    "holdout_value",
    "holdout_interval",
    "disclosed_value",
    "disclosed_interval",
    "truth_value",
    "truth_interval",
}
HASH64 = re.compile(r"[0-9a-f]{64}\Z")
OID40 = re.compile(r"[0-9a-f]{40}\Z")
EXPECTED_BLOCKERS = (
    "NO_MACHINE_FREEZE_RECORD",
    "NO_ADMITTED_MICROSCOPIC_SURVIVOR",
    "M1_MAP_AND_PREDICTION_ABSENT",
    "M2_PHYSICAL_PREDICTION_AND_HOLDOUT_ABSENT",
    "M5_MAP_AND_HOLDOUT_ABSENT",
    "PER_PARAMETER_COMMON_INPUT_LEDGER_INCOMPLETE",
    "PROSPECTIVE_PREDICTION_NOT_FROZEN",
)
SUCCESSOR_DESIGN_SCHEMA = "tect/pre-a-m2-ci8-rs-dispersion-map-successor-design/1.0"
SUCCESSOR_DESIGN_FIELDS = (
    "schema",
    "design_id",
    "hypothetical_candidate_id",
    "parent_candidate_id",
    "status",
    "candidate_created",
    "candidate_manifest",
    "admission_status",
    "microscopic_map_status",
    "prediction_status",
    "target_status",
    "freeze_status",
    "tag_status",
    "score_status",
    "selection_status",
    "required_contract",
    "no_overclaim",
)
SUCCESSOR_MANIFEST_FIELDS = ("path", "sha256")
SUCCESSOR_REQUIRED_FIELDS = (
    "physical_response_channel",
    "candidate_neutral_estimand",
    "limit_order",
    "finite_torus_fingerprint",
    "error_budget",
    "prospective_input_firewall",
    "independent_verification",
    "open_gate",
)
SUCCESSOR_RESPONSE_FIELDS = (
    "status",
    "map",
    "state_and_reference",
    "units",
    "proof",
    "script",
)
SUCCESSOR_FINGERPRINT_FIELDS = (
    "closed_child_id",
    "ordered_component_count",
    "status",
)
SUCCESSOR_ERROR_FIELDS = (
    "status",
    "terms",
    "required_bound",
    "margin_condition",
)
EXPECTED_ERROR_TERMS = (
    "finite_torus_spacing",
    "regulator_removal",
    "nonlinear_remainder",
    "loop_or_renormalization",
    "state_reference_transfer",
    "raw_estimator",
)

PHYSICAL_CONTRACT_SCHEMA = (
    "tect/pre-a-m2-ci8-physical-response-successor-minimum-contract/1.1"
)
PHYSICAL_CONTRACT_FIELDS = (
    "schema", "contract_id", "candidate_id", "parent_candidate_id", "status",
    "fixture_only", "candidate_created", "version_delta", "physical_control_map",
    "probe_contract", "state_reference_contract", "response_definition",
    "estimand_binding", "critical_prediction", "error_budget",
    "common_input_ledger", "hard_row_rerun", "verification",
    "prospective_firewall", "no_overclaim",
)
ARTIFACT_REF_FIELDS = ("path", "sha256", "role", "media_type")
VERSION_DELTA_FIELDS = (
    "classification", "substantive_changes", "change_evidence",
    "all_ten_rows_required",
)
SUBSTANTIVE_CHANGE_ENUM = (
    "SECOND_ORDER_SOURCE_LAW", "COMPACT_OR_GAUGE_ACTION",
    "STATE_REFERENCE_CHANGE", "PHYSICAL_CONTROL_MAP",
    "REGULATOR_OR_LIMIT_CHANGE", "ERROR_BOUND_PROOF",
    "MICROSCOPIC_MAP_ONLY",
)
MANDATORY_SUBSTANTIVE_CHANGES = SUBSTANTIVE_CHANGE_ENUM[:-1]
CHANGE_EVIDENCE_FIELDS = MANDATORY_SUBSTANTIVE_CHANGES
CHANGE_EVIDENCE_ROLES = {
    "SECOND_ORDER_SOURCE_LAW": "SOURCE_LAW",
    "COMPACT_OR_GAUGE_ACTION": "COMPACT_OR_GAUGE_ACTION",
    "STATE_REFERENCE_CHANGE": "STATE_EXISTENCE",
    "PHYSICAL_CONTROL_MAP": "PHYSICAL_CONTROL_MAP",
    "REGULATOR_OR_LIMIT_CHANGE": "RESPONSE_MAP",
    "ERROR_BOUND_PROOF": "PROOF",
}
CONTROL_MAP_FIELDS = (
    "kind", "physical_variable", "r_of_t", "domain", "scaling_window",
    "units", "target_blind", "uncertainty_term", "map_ref", "source_ids",
)
PROBE_CONTRACT_FIELDS = (
    "source_id", "source_type", "source_units", "linear_operator",
    "source_law_ref", "linear_probe_ref", "quadratic_contact",
    "compact_or_gauge_action", "normalization", "source_ids",
)
QUADRATIC_CONTACT_FIELDS = ("kind", "operator", "artifact_ref")
COMPACT_ACTION_FIELDS = (
    "kind", "configuration", "winding_or_flux_law", "artifact_ref",
)
STATE_REFERENCE_FIELDS = (
    "kind", "ensemble", "phase", "reference", "volume_boundary_regulator",
    "existence_ref", "physical_modes_and_quotients", "source_ids",
)
RESPONSE_DEFINITION_FIELDS = (
    "kind", "definition", "sign_convention", "limit_order", "units",
    "common_estimand_id", "map_theorem_ref", "source_ids",
)
ESTIMAND_BINDING_FIELDS = (
    "id", "kind", "definition", "units", "raw_estimator_ref",
    "acceptance_margin", "source_ids",
)
CRITICAL_PREDICTION_FIELDS = (
    "kind", "prediction_id", "candidate_id", "estimand_id",
    "predicted_relation", "scaling_window", "corrections", "target_blind",
    "status", "source_ids",
)
PHYSICAL_ERROR_BUDGET_FIELDS = (
    "terms", "total_bound", "acceptance_margin", "strict_margin",
    "proof_refs", "source_ids",
)
PHYSICAL_ERROR_TERM_FIELDS = (
    "id", "bound", "script_ref", "run_ref", "result_key", "uniform_domain",
)
INPUT_LEDGER_FIELDS = (
    "id", "class", "source_id", "units", "range", "used_for",
)
HARD_ROW_RERUN_FIELDS = ("rows", "survival_rule", "all_pass")
VERIFICATION_CONTRACT_FIELDS = (
    "primary_ref", "independent_ref", "integrated_ref", "fixture_only",
)
PROSPECTIVE_FIREWALL_FIELDS = (
    "target_value_present", "allowed_input_source_ids", "forbidden_source_ids",
    "forbidden_target_dependent_choices", "external_commitment_status",
    "remote_verification_status",
)
HARD_ROWS = (
    "D00-ADMISSION", "D01-SAME-REFERENCE", "D02-KINETIC-TENSOR",
    "D03-PHYSICAL-ZERO-MODES", "D04-SPEED-DISPERSION",
    "D05-COMPACT-WINDING", "D06-CRITICAL-DATA", "D07-VALIDATION",
    "D08-ROBUSTNESS", "D09-PREDICTION-COST",
)
HELICITY_SIGN_CONVENTION = (
    "helicity_modulus=+V^-1*d2F/dJ2|J=0; "
    "scalar_susceptibility=-V^-1*d2F/dJ2|J=0"
)
LIMIT_ORDER = (
    "SOURCE_TO_ZERO", "THERMODYNAMIC_LIMIT", "REGULATOR_REMOVAL",
    "CRITICAL_LIMIT_FROM_ORDERED_SIDE",
)
PHYSICAL_INPUT_CLASSES = {
    "INSERTED", "MATCHED", "CALIBRATION", "DERIVED", "PREDICTED",
}
PLACEHOLDER_ENUM_VALUES = {
    "NONE", "ABSENT", "UNSPECIFIED", "NOT_SUPPLIED", "NOT_CREATED", "TBD",
    "PLACEHOLDER", "N/A", "NA", "NOT_AVAILABLE",
}
FORBIDDEN_SOURCE_TOKENS = ("TARGET", "HOLDOUT", "DISCOVERY", "FORBIDDEN")
FIXTURE_FORBIDDEN_SOURCE_IDS = (
    "DISCOVERY-FIXTURE-ONLY", "HOLDOUT-TARGET-FIXTURE-ONLY",
)
FORBIDDEN_TARGET_CHOICES = (
    "RESPONSE_MAP", "PHYSICAL_CONTROL_MAP", "SCALING_WINDOW",
    "ERROR_BOUNDS", "PREDICTION_VALUE",
)
CANONICAL_POSITIVE_RATIONAL_RE = re.compile(
    r"[1-9][0-9]*(?:/[1-9][0-9]*)?\Z"
)
MAX_CANONICAL_RATIONAL_LENGTH = 128
MAX_REPO_RELATIVE_PATH_LENGTH = 4096
ARTIFACT_ROLE_POLICIES = {
    "SOURCE_LAW": (("codes/",), (".py",), ("text/x-python",)),
    "LINEAR_PROBE": (("codes/",), (".py",), ("text/x-python",)),
    "QUADRATIC_CONTACT": (("codes/",), (".py",), ("text/x-python",)),
    "COMPACT_OR_GAUGE_ACTION": (("codes/",), (".py",), ("text/x-python",)),
    "PHYSICAL_CONTROL_MAP": (("codes/",), (".py",), ("text/x-python",)),
    "STATE_EXISTENCE": (
        ("strategy/", "claims/", "codes/", "theory/"),
        (".json", ".md", ".py"),
        ("application/json", "text/markdown", "text/x-python"),
    ),
    "RESPONSE_MAP": (("codes/",), (".py",), ("text/x-python",)),
    "RAW_ESTIMATOR": (("codes/",), (".py",), ("text/x-python",)),
    "PROOF": (
        ("strategy/", "claims/", "codes/", "theory/"),
        (".json", ".md", ".py"),
        ("application/json", "text/markdown", "text/x-python"),
    ),
    "VERIFIER_PRIMARY": (("codes/",), (".py",), ("text/x-python",)),
    "VERIFIER_INDEPENDENT": (("codes/",), (".py",), ("text/x-python",)),
    "VERIFIER_INTEGRATED": (("codes/",), (".py",), ("text/x-python",)),
    "ERROR_SCRIPT": (("codes/",), (".py",), ("text/x-python",)),
    "ERROR_RUN": (("claims/",), (".json",), ("application/json",)),
}
PHYSICAL_CONTRACT_HOSTILE_CODES = {
    "candidate_materialized": "PHYSICAL_CONTRACT_LIFECYCLE_INVALID",
    "substantive_change_mislabeled_map_only": "PHYSICAL_CONTRACT_VERSION_DELTA_INVALID",
    "control_map_missing": "PHYSICAL_CONTRACT_CONTROL_MAP_INVALID",
    "target_dependent_control": "PHYSICAL_CONTRACT_CONTROL_MAP_INVALID",
    "quadratic_contact_missing": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "compact_action_missing": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "state_reference_missing": "PHYSICAL_CONTRACT_STATE_INVALID",
    "scalar_susceptibility_relabel": "PHYSICAL_CONTRACT_RESPONSE_INVALID",
    "limit_order_missing": "PHYSICAL_CONTRACT_RESPONSE_INVALID",
    "estimand_mismatch": "PHYSICAL_CONTRACT_ESTIMAND_INVALID",
    "fingerprint_promoted_as_response": "PHYSICAL_CONTRACT_RESPONSE_INVALID",
    "error_term_dropped": "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
    "error_total_not_sum": "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
    "error_margin_not_strict": "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
    "hard_row_nonpass": "PHYSICAL_CONTRACT_HARD_ROWS_INVALID",
    "single_implementation": "PHYSICAL_CONTRACT_VERIFICATION_INVALID",
    "target_value_present": "PHYSICAL_CONTRACT_FIREWALL_INVALID",
    "map_only_payload_under_substantive_label": "PHYSICAL_CONTRACT_VERSION_DELTA_INVALID",
    "unknown_substantive_change": "PHYSICAL_CONTRACT_VERSION_DELTA_INVALID",
    "duplicate_substantive_change": "PHYSICAL_CONTRACT_VERSION_DELTA_INVALID",
    "unbound_probe_hash": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "probe_artifact_wrong_role": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "quadratic_contact_placeholder": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "compact_action_placeholder": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "state_existence_ref_unbound": "PHYSICAL_CONTRACT_STATE_INVALID",
    "response_map_ref_unbound": "PHYSICAL_CONTRACT_RESPONSE_INVALID",
    "limit_order_placeholder": "PHYSICAL_CONTRACT_RESPONSE_INVALID",
    "limit_order_permuted": "PHYSICAL_CONTRACT_RESPONSE_INVALID",
    "prediction_placeholder": "PHYSICAL_CONTRACT_PREDICTION_INVALID",
    "prediction_candidate_unbound": "PHYSICAL_CONTRACT_PREDICTION_INVALID",
    "proof_ref_unbound": "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
    "error_evidence_reused": "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
    "error_result_key_missing": "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
    "non_script_verifier": "PHYSICAL_CONTRACT_VERIFICATION_INVALID",
    "identical_verifier_hash": "PHYSICAL_CONTRACT_VERIFICATION_INVALID",
    "integrated_ref_missing": "PHYSICAL_CONTRACT_VERIFICATION_INVALID",
    "duplicate_input_id": "PHYSICAL_CONTRACT_INPUT_LEDGER_INVALID",
    "duplicate_source_id": "PHYSICAL_CONTRACT_INPUT_LEDGER_INVALID",
    "visible_validation_source": "PHYSICAL_CONTRACT_INPUT_LEDGER_INVALID",
    "forbidden_source_id": "PHYSICAL_CONTRACT_INPUT_LEDGER_INVALID",
    "source_section_unbound": "PHYSICAL_CONTRACT_SOURCE_BINDING_INVALID",
    "forbidden_choices_placeholder": "PHYSICAL_CONTRACT_FIREWALL_INVALID",
    "decimal_ratio": "PHYSICAL_CONTRACT_ESTIMAND_INVALID",
    "unreduced_ratio": "PHYSICAL_CONTRACT_ESTIMAND_INVALID",
    "whitespace_ratio": "PHYSICAL_CONTRACT_ESTIMAND_INVALID",
    "embedded_nul_artifact_path": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "overlong_artifact_path": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "overlong_rational_literal": "NUMERIC_LITERAL_INVALID",
    "trailing_dot_segment_artifact_path": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "trailing_space_segment_artifact_path": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "case_changed_artifact_path": "PHYSICAL_CONTRACT_PROBE_INVALID",
    "free_semantic_placeholder": "PHYSICAL_CONTRACT_PREDICTION_INVALID",
    "prediction_target_leakage": "PHYSICAL_CONTRACT_PREDICTION_INVALID",
    "scaling_window_holdout_leakage": "PHYSICAL_CONTRACT_PREDICTION_INVALID",
    "control_map_r_of_t_target_leakage": "PHYSICAL_CONTRACT_CONTROL_MAP_INVALID",
    "control_map_scaling_window_holdout_leakage": "PHYSICAL_CONTRACT_CONTROL_MAP_INVALID",
    "denominator_one_ratio": "NUMERIC_LITERAL_INVALID",
}
EXPECTED_PHYSICAL_CONTRACT_HOSTILES = tuple(PHYSICAL_CONTRACT_HOSTILE_CODES)


V13_SUITE_SCHEMA = "tect/pre-a-m2-ci8-v1-3-theorem-suite/1.0"
V13_SUITE_FIELDS = (
    "schema", "result", "exploration_id", "claim_bearing", "tier",
    "closed_child_ids", "negative_ids", "open_successor_gate_ids",
    "real_scalar_internal_u1_and_winding",
    "one_q_auxiliary_phason_curvature_and_finite_torus_secant",
    "helicity_tensor_contact_shift_nonidentifiability",
    "analytic_map_integer_exponent_transport",
    "six_stage_relative_log_slope_error_transport", "scope",
)
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
EXPECTED_V13_HOSTILES = tuple(V13_HOSTILE_CODES)

MAP_ONLY_SURVIVAL_SCHEMA = "tect/pre-a-round1-map-only-survival-contract/1.0"
MAP_ONLY_SURVIVAL_FIELDS = (
    "schema",
    "source_path",
    "source_sha256",
    "hard_rows",
    "survives_if",
    "hypothetical_map_only_change",
    "residual_hard_rows",
    "map_only_survivor_ids",
    "all_pass_after_map_only",
    "substantive_new_version_requirements",
    "boundary",
)
MAP_ONLY_CHANGE_FIELDS = (
    "hypothetical_only",
    "microscopic_map_after",
    "preserved_fields",
)
MAP_ONLY_PRESERVED_FIELDS = (
    "degrees_and_state_space",
    "law_and_parameter_domain",
    "reference_and_boundary",
    "regulator_and_limit_order",
    "kinetic_tensor_and_dynamics",
    "compactness_and_gauge_structure",
    "physical_modes_and_quotients",
    "critical_data",
    "prospective_prediction_and_validation",
    "robustness_envelope",
)
MAP_ONLY_RESIDUAL_ORACLE = {
    MICROSCOPIC_CANDIDATES[0]: {
        "D01-SAME-REFERENCE": "FAIL",
        "D02-KINETIC-TENSOR": "NOT_ADMITTED",
    },
    MICROSCOPIC_CANDIDATES[1]: {
        "D03-PHYSICAL-ZERO-MODES": "NOT_ADMITTED",
        "D05-COMPACT-WINDING": "NOT_ADMITTED",
        "D06-CRITICAL-DATA": "NOT_TESTED",
        "D08-ROBUSTNESS": "NOT_ADMITTED",
    },
    MICROSCOPIC_CANDIDATES[2]: {
        "D04-SPEED-DISPERSION": "FAIL",
        "D05-COMPACT-WINDING": "FAIL",
    },
}
MAP_ONLY_SUBSTANTIVE_REQUIREMENTS = {
    MICROSCOPIC_CANDIDATES[0]: (
        "repair D01 through state, law or ensemble data",
        "supply a conservative real-time kinetic law and tensor",
    ),
    MICROSCOPIC_CANDIDATES[1]: (
        "supply compact or gauge configuration and winding or flux data",
        "derive physical modes after constraints and quotients",
        "derive critical data and robustness",
    ),
    MICROSCOPIC_CANDIDATES[2]: (
        "change the law or nodes to repair rank-one D04 dispersion",
        "supply a genuine compact gauge connection",
    ),
}


def repo_path(path: Path) -> str:
    return str(path.relative_to(REPO)).replace("\\", "/")


def normalized_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{repo_path(path)} must contain a JSON object")
    return value


def git_text(*arguments: str) -> str:
    run = subprocess.run(
        ["git", *arguments],
        cwd=REPO,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    return run.stdout


def git_lines(*arguments: str) -> list[str]:
    return [line.strip() for line in git_text(*arguments).splitlines() if line.strip()]


def git_json_at(commit: str, path: Path) -> dict[str, Any]:
    value = json.loads(git_text("show", f"{commit}:{repo_path(path)}"))
    if not isinstance(value, dict):
        raise TypeError(f"{repo_path(path)} at {commit} is not an object")
    return value


def git_is_ancestor(ancestor: str, descendant: str) -> bool:
    run = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=REPO,
        capture_output=True,
        check=False,
    )
    return run.returncode == 0


def parse_utc(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None
    return parsed.astimezone(timezone.utc)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(
        self,
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
        group: str,
    ) -> None:
        if not condition:
            raise AssertionError(
                f"{group}: {name}: actual={actual!r}, expected={expected!r}"
            )
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS",
                "actual": actual,
                "expected": expected,
            }
        )


def add_error(errors: list[dict[str, str]], code: str, message: str) -> None:
    if code not in {row["code"] for row in errors}:
        errors.append({"code": code, "message": message})


def object_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def exact_object(
    value: Any,
    fields: tuple[str, ...],
    errors: list[dict[str, str]],
    code: str,
    label: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        add_error(errors, code, f"{label} must be an object with exact fields")
        return {}
    missing = [field for field in fields if field not in value]
    extra = [field for field in value if field not in fields]
    non_string_keys = [field for field in value if not isinstance(field, str)]
    if missing or extra or non_string_keys:
        details = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if non_string_keys:
            details.append(
                "non_string_keys="
                + ",".join(repr(field) for field in non_string_keys)
            )
        if extra:
            details.append("extra=" + ",".join(repr(field) for field in extra))
        add_error(errors, code, f"{label} fields invalid: " + "; ".join(details))
    return value


def nonempty_string_set(value: Any) -> set[str] | None:
    if not isinstance(value, list):
        return None
    if any(not isinstance(item, str) or not item.strip() for item in value):
        return None
    return set(value)


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_string_list(value: Any, *, nonempty: bool) -> bool:
    return (
        isinstance(value, list)
        and (bool(value) or not nonempty)
        and all(is_nonempty_string(item) for item in value)
    )


def is_https_url_with_host(value: Any) -> bool:
    if not is_nonempty_string(value):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.hostname)


def path_hash_matches(path_text: Any, digest: Any) -> bool:
    if not isinstance(path_text, str) or not isinstance(digest, str):
        return False
    if HASH64.fullmatch(digest) is None:
        return False
    if (
        not path_text
        or len(path_text) > MAX_REPO_RELATIVE_PATH_LENGTH
        or "\x00" in path_text
        or "\\" in path_text
        or ":" in path_text
    ):
        return False
    try:
        pure = PurePosixPath(path_text)
        if pure.is_absolute() or pure.as_posix() != path_text:
            return False
        if any(
            part in {"", ".", ".."}
            or part.endswith(" ")
            or part.endswith(".")
            for part in pure.parts
        ):
            return False
        repo_root = REPO.resolve()
        current = repo_root
        for part in pure.parts:
            if part not in os.listdir(current):
                return False
            current = current / part
        candidate = current.resolve()
        canonical_relative = candidate.relative_to(repo_root).as_posix()
        if canonical_relative != path_text:
            return False
        if not candidate.is_file():
            return False
        return normalized_sha256(candidate) == digest
    except (OSError, ValueError, RuntimeError):
        return False


def find_forbidden_keys(value: Any, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            location = f"{prefix}.{key}" if prefix else str(key)
            if key in FORBIDDEN_VALUE_KEYS:
                found.append(location)
            found.extend(find_forbidden_keys(item, location))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(find_forbidden_keys(item, f"{prefix}[{index}]"))
    return found


def validate_schema_shape(
    freeze: dict[str, Any], *, synthetic_fixture_mode: bool = False
) -> dict[str, Any]:
    """Validate local shape only and refuse every purported real freeze."""

    errors: list[dict[str, str]] = []
    missing = [field for field in ROOT_FIELDS if field not in freeze]
    extra = [field for field in freeze if field not in ROOT_FIELDS]
    if missing:
        add_error(errors, "ROOT_FIELDS_MISSING", ", ".join(missing))
        return {
            "valid": False,
            "error_codes": [row["code"] for row in errors],
            "errors": errors,
        }
    if extra:
        add_error(errors, "ROOT_FIELDS_EXTRA", ", ".join(repr(field) for field in extra))

    if freeze.get("schema") != FREEZE_SCHEMA:
        add_error(errors, "SCHEMA_INVALID", "unexpected freeze schema")
    if freeze.get("parent_gate") != PARENT_GATE:
        add_error(errors, "PARENT_GATE_INVALID", "unexpected parent gate")
    if freeze.get("status") != "FROZEN_UNSCORED" or freeze.get("claim_bearing") is not False:
        add_error(errors, "LIFECYCLE_INVALID", "freeze must be claim-nonbearing and unscored")
    root_identity_fields = ("freeze_id", "prediction_id", "round_id", "no_overclaim")
    if any(
        not isinstance(freeze.get(field), str) or not freeze.get(field).strip()
        for field in root_identity_fields
    ):
        add_error(
            errors,
            "ROOT_VALUES_INVALID",
            "freeze, prediction, round, and scope strings must be nonempty",
        )
    if freeze.get("fixture_only") is not True and freeze.get("fixture_only") is not False:
        add_error(errors, "LIFECYCLE_INVALID", "fixture_only must be a Boolean")
    if freeze.get("fixture_only") is True and not synthetic_fixture_mode:
        add_error(errors, "FIXTURE_FORBIDDEN", "synthetic fixture cannot be a real freeze")

    contestants = freeze.get("contestant_snapshot")
    if not isinstance(contestants, list):
        contestants = []
        add_error(errors, "CONTESTANTS_INVALID", "contestants must be a list")
    candidate_ids: list[str] = []
    baselines: list[str] = []
    eligible_ids: set[str] = set()
    for row_value in contestants:
        row = exact_object(
            row_value,
            CONTESTANT_FIELDS,
            errors,
            "CONTESTANTS_INVALID",
            "contestant_snapshot[]",
        )
        candidate_id = row.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            add_error(errors, "CONTESTANTS_INVALID", "candidate_id must be a nonempty string")
            candidate_id = ""
        else:
            candidate_ids.append(candidate_id)
        role = row.get("role")
        if not is_nonempty_string(role):
            add_error(errors, "CONTESTANTS_INVALID", "contestant role must be nonempty")
        eligible = row.get("score_eligible_as_microscopic_winner") is True
        eligibility_value = row.get("score_eligible_as_microscopic_winner")
        if eligibility_value is not True and eligibility_value is not False:
            add_error(errors, "CONTESTANTS_INVALID", "contestant eligibility must be Boolean")
        if role == "EFFECTIVE_NULL_BASELINE":
            baselines.append(candidate_id)
            if eligible:
                add_error(errors, "BASELINE_INVALID", "baseline cannot be a microscopic winner")
        elif eligible:
            eligible_ids.add(candidate_id)
            if not isinstance(role, str) or role not in ELIGIBLE_ROLES:
                add_error(errors, "ELIGIBLE_ROLE_INVALID", "unknown microscopic role")
        if not path_hash_matches(row.get("path"), row.get("normalized_sha256")):
            add_error(errors, "HASH_FAILURE", f"contestant {candidate_id}")
    if len(candidate_ids) != len(set(candidate_ids)):
        add_error(errors, "CANDIDATE_DUPLICATE", "contestant IDs are not unique")
    if len(baselines) != 1:
        add_error(errors, "BASELINE_MISSING", "exactly one effective baseline is required")
    if not eligible_ids:
        add_error(errors, "ELIGIBLE_CANDIDATE_MISSING", "no microscopic contestant is eligible")

    evidence = exact_object(
        freeze.get("evidence_snapshot"),
        EVIDENCE_FIELDS,
        errors,
        "EVIDENCE_SNAPSHOT_INVALID",
        "evidence_snapshot",
    )
    discovery_ids_value = nonempty_string_set(evidence.get("discovery_ids"))
    forbidden_fit_ids_value = nonempty_string_set(evidence.get("forbidden_fit_ids"))
    discovery_groups_value = nonempty_string_set(
        evidence.get("discovery_independence_groups")
    )
    calibration_groups_value = nonempty_string_set(
        evidence.get("calibration_independence_groups")
    )
    discovery_ids = discovery_ids_value or set()
    forbidden_fit_ids = forbidden_fit_ids_value or set()
    discovery_groups = discovery_groups_value or set()
    calibration_groups = calibration_groups_value or set()
    if any(
        value is None
        for value in (
            discovery_ids_value,
            forbidden_fit_ids_value,
            discovery_groups_value,
            calibration_groups_value,
        )
    ):
        add_error(
            errors,
            "DISCOVERY_FIREWALL_INVALID",
            "evidence IDs and groups must be nonempty string lists",
        )
    if not discovery_ids or not discovery_ids <= forbidden_fit_ids:
        add_error(errors, "DISCOVERY_FIREWALL_INVALID", "discovery set is not frozen out")
    if not path_hash_matches(evidence.get("path"), evidence.get("normalized_sha256")):
        add_error(errors, "HASH_FAILURE", "evidence snapshot")

    target = exact_object(
        freeze.get("target_contract"),
        TARGET_FIELDS,
        errors,
        "TARGET_CONTRACT_INVALID",
        "target_contract",
    )
    target_identity_fields = (
        "target_id",
        "custodian",
        "protocol_or_accession",
        "estimand_id",
        "units",
    )
    if any(
        not isinstance(target.get(field), str) or not target.get(field).strip()
        for field in target_identity_fields
    ):
        add_error(
            errors,
            "TARGET_CONTRACT_INVALID",
            "target identity, custodian, accession, estimand, and units must be nonempty",
        )
    leaked = find_forbidden_keys(freeze)
    if leaked or target.get("target_value_present") is not False:
        add_error(errors, "TARGET_LEAKAGE", ", ".join(leaked) or "target_value_present")
    if target.get("blind") is not True or target.get("predictor_access_before_freeze") is not False:
        add_error(errors, "BLINDNESS_INVALID", "predictor access or blindness flag invalid")
    target_group = target.get("independence_group")
    if (
        not is_nonempty_string(target_group)
        or target_group in discovery_groups | calibration_groups
    ):
        add_error(errors, "INDEPENDENCE_OVERLAP", "holdout evidence group is not independent")
    commitment = exact_object(
        target.get("commitment"),
        COMMITMENT_FIELDS,
        errors,
        "COMMITMENT_INVALID",
        "target_contract.commitment",
    )
    commitment_shape = (
        commitment.get("algorithm") == "HMAC-SHA256"
        and isinstance(commitment.get("commitment_hex"), str)
        and HASH64.fullmatch(commitment.get("commitment_hex", "")) is not None
        and commitment.get("secret_key_custody") == "EXTERNAL_CUSTODIAN"
        and commitment.get("payload_schema")
        == "tect/pre-a-round1-holdout-target-payload/1.0"
        and commitment.get("canonical_serialization") == "RFC8785-JCS"
        and commitment.get("domain_separation")
        == "TECT-PRE-A-ROUND1-HOLDOUT-TARGET-v1"
        and is_nonempty_string(commitment.get("custodian_signature"))
        and isinstance(commitment.get("public_key_fingerprint"), str)
        and HASH64.fullmatch(commitment.get("public_key_fingerprint", "")) is not None
        and is_nonempty_string(commitment.get("issued_at_utc"))
    )
    if not commitment_shape:
        add_error(
            errors,
            "COMMITMENT_INVALID",
            "externally keyed, custodian-signed canonical HMAC shape is incomplete",
        )
    disclosure = exact_object(
        target.get("disclosure"),
        DISCLOSURE_FIELDS,
        errors,
        "DISCLOSURE_INVALID",
        "target_contract.disclosure",
    )
    if (
        disclosure.get("status") != "SEALED"
        or not is_nonempty_string(disclosure.get("not_before_utc"))
        or disclosure.get("actual_at_utc") is not None
    ):
        add_error(errors, "TARGET_ALREADY_DISCLOSED", "freeze must precede disclosure")

    observable = exact_object(
        freeze.get("observable_contract"),
        OBSERVABLE_FIELDS,
        errors,
        "OBSERVABLE_CONTRACT_INVALID",
        "observable_contract",
    )
    estimand = exact_object(
        observable.get("common_estimand"),
        ESTIMAND_FIELDS,
        errors,
        "ESTIMAND_INVALID",
        "observable_contract.common_estimand",
    )
    if not all(is_nonempty_string(estimand.get(field)) for field in ("id", "definition", "units")):
        add_error(errors, "ESTIMAND_INVALID", "candidate-neutral estimand is incomplete")
    if (
        target.get("estimand_id") != estimand.get("id")
        or target.get("units") != estimand.get("units")
    ):
        add_error(
            errors,
            "TARGET_ESTIMAND_MISMATCH",
            "target estimand_id and units must equal the common estimand",
        )
    estimator = exact_object(
        estimand.get("raw_estimator"),
        RAW_ESTIMATOR_FIELDS,
        errors,
        "ESTIMAND_INVALID",
        "observable_contract.common_estimand.raw_estimator",
    )
    if not path_hash_matches(estimator.get("path"), estimator.get("sha256")):
        add_error(errors, "HASH_FAILURE", "raw estimator")
    admitted_map_ids: set[str] = set()
    maps = observable.get("candidate_maps")
    if not isinstance(maps, list):
        add_error(errors, "CANDIDATE_MAPS_INVALID", "candidate maps must be a list")
        maps = []
    map_candidate_ids: list[str] = []
    required_map_text_fields = (
        "map_statement",
        "domain",
        "state_and_reference",
        "units_map",
        "limit_order",
    )
    for map_value in maps:
        row = exact_object(
            map_value,
            CANDIDATE_MAP_FIELDS,
            errors,
            "CANDIDATE_MAPS_INVALID",
            "observable_contract.candidate_maps[]",
        )
        candidate_id_value = row.get("candidate_id")
        if not isinstance(candidate_id_value, str) or not candidate_id_value.strip():
            add_error(errors, "CANDIDATE_MAPS_INVALID", "candidate map ID must be nonempty")
            continue
        candidate_id = candidate_id_value
        map_candidate_ids.append(candidate_id)
        proof_refs = row.get("proof_refs")
        nuisance_inputs = row.get("nuisance_inputs")
        declared_map_types_valid = (
            is_nonempty_string(row.get("status"))
            and is_nonempty_string(row.get("script_path"))
            and isinstance(row.get("script_sha256"), str)
            and HASH64.fullmatch(row.get("script_sha256", "")) is not None
            and is_string_list(proof_refs, nonempty=True)
            and is_string_list(nuisance_inputs, nonempty=False)
        )
        if not declared_map_types_valid:
            add_error(errors, "CANDIDATE_MAPS_INVALID", f"candidate map types invalid for {candidate_id}")
        map_complete = (
            all(
                isinstance(row.get(field), str) and bool(row.get(field).strip())
                for field in required_map_text_fields
            )
            and declared_map_types_valid
        )
        if row.get("status") == "ADMITTED" and map_complete:
            if path_hash_matches(row.get("script_path"), row.get("script_sha256")):
                admitted_map_ids.add(candidate_id)
            else:
                add_error(errors, "HASH_FAILURE", f"candidate map {candidate_id}")
        elif row.get("status") == "ADMITTED":
            add_error(errors, "CANDIDATE_MAPS_INVALID", f"admitted map incomplete for {candidate_id}")
    if len(map_candidate_ids) != len(set(map_candidate_ids)):
        add_error(
            errors,
            "MAP_CANDIDATE_DUPLICATE",
            "candidate maps must be uniquely keyed by candidate_id",
        )
    if not eligible_ids or not eligible_ids <= admitted_map_ids:
        add_error(errors, "ELIGIBLE_MAP_MISSING", "eligible candidate has no admitted map")
    if set(map_candidate_ids) - set(candidate_ids):
        add_error(errors, "MAP_CANDIDATE_UNKNOWN", "map candidate is outside snapshot")

    prediction = exact_object(
        freeze.get("prediction_contract"),
        PREDICTION_FIELDS,
        errors,
        "PREDICTION_CONTRACT_INVALID",
        "prediction_contract",
    )
    required_prediction_text = (
        "predicted_relation",
        "theory_uncertainty",
        "acceptance_rule",
        "baseline_prediction",
    )
    forbidden_knobs = prediction.get("forbidden_knobs")
    if (
        prediction.get("physical_output") is not True
        or any(
            not isinstance(prediction.get(field), str)
            or not prediction.get(field).strip()
            for field in required_prediction_text
        )
        or not isinstance(forbidden_knobs, list)
        or not forbidden_knobs
        or any(not isinstance(item, str) or not item.strip() for item in forbidden_knobs)
    ):
        add_error(errors, "PREDICTION_INVALID", "physical prediction contract is incomplete")
    prediction_candidate_id = prediction.get("candidate_id")
    if (
        not isinstance(prediction_candidate_id, str)
        or not prediction_candidate_id.strip()
        or prediction_candidate_id not in eligible_ids
        or prediction_candidate_id not in admitted_map_ids
    ):
        add_error(
            errors,
            "PREDICTION_CANDIDATE_UNBOUND",
            "frozen prediction must name an eligible admitted-map candidate",
        )
    allowed_inputs = prediction.get("allowed_inputs")
    if not isinstance(allowed_inputs, list) or not allowed_inputs:
        add_error(errors, "INPUT_LEDGER_INVALID", "allowed-input ledger is empty")
    else:
        input_ids: list[str] = []
        for input_value in allowed_inputs:
            row = exact_object(
                input_value,
                ALLOWED_INPUT_FIELDS,
                errors,
                "INPUT_FIELDS_INVALID",
                "prediction_contract.allowed_inputs[]",
            )
            input_id = row.get("id")
            if not isinstance(input_id, str) or not input_id.strip():
                add_error(errors, "INPUT_LEDGER_INVALID", "input ID must be nonempty")
            else:
                input_ids.append(input_id)
            source = row.get("source")
            source_id = row.get("source_id")
            input_class = row.get("class")
            used_for = row.get("used_for")
            if (
                not is_nonempty_string(input_class)
                or input_class not in INPUT_CLASSES
                or not isinstance(source, str)
                or not source.strip()
                or not isinstance(source_id, str)
                or not source_id.strip()
                or not is_nonempty_string(used_for)
            ):
                add_error(errors, "INPUT_LEDGER_INVALID", "input class or source is invalid")
            if isinstance(source_id, str) and source_id in forbidden_fit_ids | discovery_ids:
                add_error(errors, "DISCOVERY_REUSE", "discovery datum reused")
        if len(input_ids) != len(set(input_ids)):
            add_error(errors, "INPUT_LEDGER_INVALID", "input IDs are not unique")

    robustness = exact_object(
        freeze.get("robustness_contract"),
        ROBUSTNESS_FIELDS,
        errors,
        "ROBUSTNESS_INVALID",
        "robustness_contract",
    )
    if any(
        not isinstance(robustness.get(field), str)
        or not robustness.get(field).strip()
        for field in ROBUSTNESS_FIELDS
    ):
        add_error(errors, "ROBUSTNESS_INVALID", "robustness envelope is incomplete")

    provenance = exact_object(
        freeze.get("provenance"),
        PROVENANCE_FIELDS,
        errors,
        "REMOTE_ANCHOR_INVALID",
        "provenance",
    )
    prediction_id = freeze.get("prediction_id")
    version = freeze.get("freeze_version")
    version_valid = isinstance(version, int) and not isinstance(version, bool) and version > 0
    if not version_valid:
        add_error(errors, "FREEZE_VERSION_INVALID", "freeze version must be a positive integer")
        version = 0
    expected_tag = f"freeze/{prediction_id}/v{version}"
    remote_shape = (
        isinstance(provenance.get("freeze_commit_oid"), str)
        and OID40.fullmatch(provenance.get("freeze_commit_oid", "")) is not None
        and is_https_url_with_host(provenance.get("remote_url"))
        and isinstance(provenance.get("remote_commit_sha"), str)
        and provenance.get("remote_commit_sha") == provenance.get("freeze_commit_oid")
        and is_nonempty_string(provenance.get("remote_observed_at_utc"))
        and is_nonempty_string(provenance.get("annotated_tag"))
        and provenance.get("annotated_tag") == expected_tag
        and is_nonempty_string(provenance.get("remote_ref"))
        and provenance.get("remote_ref") == f"refs/tags/{expected_tag}"
        and isinstance(provenance.get("tag_object_oid"), str)
        and OID40.fullmatch(provenance.get("tag_object_oid", "")) is not None
        and provenance.get("tag_object_oid") != provenance.get("freeze_commit_oid")
    )
    if not remote_shape:
        add_error(errors, "REMOTE_ANCHOR_INVALID", "remote commit/tag metadata is malformed")

    commitment_time = parse_utc(commitment.get("issued_at_utc"))
    remote_time = parse_utc(provenance.get("remote_observed_at_utc"))
    disclosure_time = parse_utc(disclosure.get("not_before_utc"))
    if (
        commitment_time is None
        or remote_time is None
        or disclosure_time is None
        or not commitment_time <= remote_time < disclosure_time
    ):
        add_error(errors, "TEMPORAL_ORDER_INVALID", "commitment <= remote freeze < disclosure required")

    scoring = exact_object(
        freeze.get("scoring"),
        SCORING_FIELDS,
        errors,
        "SCORING_STATE_INVALID",
        "scoring",
    )
    if (
        scoring.get("status") != "NOT_DISCLOSED"
        or scoring.get("target_path") is not None
        or scoring.get("result_path") is not None
        or not path_hash_matches(scoring.get("scorer_path"), scoring.get("scorer_sha256"))
    ):
        add_error(errors, "SCORING_STATE_INVALID", "unchanged scorer is not frozen")

    # Local shape checks cannot authenticate an external signer or remote refs.
    # This is unconditional for every purported real freeze, even when all
    # preceding fields have plausible values and valid local hashes.
    if not synthetic_fixture_mode:
        add_error(
            errors,
            "EXTERNAL_VERIFICATION_REQUIRED",
            "cryptographic custodian-signature and independent remote-object/ref verification are required",
        )

    return {
        "valid": not errors,
        "error_codes": [row["code"] for row in errors],
        "errors": errors,
    }


def synthetic_fixture() -> dict[str, Any]:
    script_hash = normalized_sha256(SCRIPT)
    baseline_hash = normalized_sha256(M0_MANIFEST)
    evidence_hash = normalized_sha256(ADMISSION_FREEZE)
    commitment = hashlib.sha256(b"independent-synthetic-opaque-commitment").hexdigest()
    fingerprint = hashlib.sha256(b"independent-synthetic-public-key").hexdigest()
    commit_oid = hashlib.sha256(b"independent-synthetic-freeze-commit").hexdigest()[:40]
    tag_oid = hashlib.sha256(b"independent-synthetic-tag-object").hexdigest()[:40]
    prediction_id = "PA-R1-INDEPENDENT-FIXTURE-001"
    return {
        "schema": FREEZE_SCHEMA,
        "freeze_id": "PA-ROUND1-INDEPENDENT-FIXTURE-v1",
        "prediction_id": prediction_id,
        "freeze_version": 1,
        "round_id": "PRE-A-ROUND1-INDEPENDENT-FIXTURE",
        "parent_gate": PARENT_GATE,
        "status": "FROZEN_UNSCORED",
        "claim_bearing": False,
        "fixture_only": True,
        "contestant_snapshot": [
            {
                "candidate_id": EXPECTED_CANDIDATES[0],
                "role": "EFFECTIVE_NULL_BASELINE",
                "score_eligible_as_microscopic_winner": False,
                "path": repo_path(M0_MANIFEST),
                "normalized_sha256": baseline_hash,
            },
            {
                "candidate_id": "INDEPENDENT-FIXTURE-MICRO-v1",
                "role": "COMPACT_GAUGE_ALTERNATIVE",
                "score_eligible_as_microscopic_winner": True,
                "path": repo_path(SCRIPT),
                "normalized_sha256": script_hash,
            },
        ],
        "evidence_snapshot": {
            "path": repo_path(ADMISSION_FREEZE),
            "normalized_sha256": evidence_hash,
            "discovery_ids": ["INDEPENDENT-DISCOVERY-001"],
            "forbidden_fit_ids": ["INDEPENDENT-DISCOVERY-001"],
            "discovery_independence_groups": ["INDEPENDENT-DISCOVERY-GROUP"],
            "calibration_independence_groups": ["INDEPENDENT-CALIBRATION-GROUP"],
        },
        "target_contract": {
            "target_id": "INDEPENDENT-SEALED-TARGET-001",
            "custodian": "SYNTHETIC EXTERNAL CUSTODIAN",
            "protocol_or_accession": "INDEPENDENT-FIXTURE-PROTOCOL",
            "estimand_id": "INDEPENDENT-ESTIMAND-001",
            "units": "dimensionless",
            "independence_group": "INDEPENDENT-HOLDOUT-GROUP",
            "blind": True,
            "predictor_access_before_freeze": False,
            "target_value_present": False,
            "commitment": {
                "algorithm": "HMAC-SHA256",
                "commitment_hex": commitment,
                "secret_key_custody": "EXTERNAL_CUSTODIAN",
                "payload_schema": "tect/pre-a-round1-holdout-target-payload/1.0",
                "canonical_serialization": "RFC8785-JCS",
                "domain_separation": "TECT-PRE-A-ROUND1-HOLDOUT-TARGET-v1",
                "custodian_signature": "PLAUSIBLE-SHAPE-BUT-NOT-CRYPTOGRAPHICALLY-VERIFIED",
                "public_key_fingerprint": fingerprint,
                "issued_at_utc": "2026-08-10T00:00:00Z",
            },
            "disclosure": {
                "status": "SEALED",
                "not_before_utc": "2026-08-12T00:00:00Z",
                "actual_at_utc": None,
            },
        },
        "observable_contract": {
            "common_estimand": {
                "id": "INDEPENDENT-ESTIMAND-001",
                "definition": "Synthetic candidate-neutral estimand",
                "units": "dimensionless",
                "raw_estimator": {"path": repo_path(SCRIPT), "sha256": script_hash},
            },
            "candidate_maps": [
                {
                    "candidate_id": "INDEPENDENT-FIXTURE-MICRO-v1",
                    "status": "ADMITTED",
                    "map_statement": "Synthetic independent map fixture",
                    "domain": "synthetic finite domain",
                    "state_and_reference": "synthetic fixed state and reference",
                    "units_map": "dimensionless to dimensionless",
                    "limit_order": "fixed synthetic order",
                    "nuisance_inputs": [],
                    "proof_refs": [repo_path(SCRIPT)],
                    "script_path": repo_path(SCRIPT),
                    "script_sha256": script_hash,
                }
            ],
        },
        "prediction_contract": {
            "candidate_id": "INDEPENDENT-FIXTURE-MICRO-v1",
            "predicted_relation": "independent_fixture_ratio = 1",
            "physical_output": True,
            "theory_uncertainty": "synthetic fixed interval",
            "acceptance_rule": "synthetic frozen interval membership",
            "baseline_prediction": "synthetic baseline interval",
            "allowed_inputs": [
                {
                    "id": "INDEPENDENT-CALIBRATION-001",
                    "class": "CALIBRATION",
                    "source": "synthetic units calibration",
                    "source_id": "INDEPENDENT-CAL-001",
                    "used_for": "units only",
                }
            ],
            "forbidden_knobs": [
                "target-dependent map choice",
                "target-dependent parameter choice",
                "post-disclosure uncertainty change",
            ],
        },
        "robustness_contract": {
            "volume": "synthetic fixed envelope",
            "boundary": "synthetic fixed envelope",
            "regulator": "synthetic fixed envelope",
            "coefficients": "synthetic fixed envelope",
            "implementation": "independent implementation required",
        },
        "provenance": {
            "freeze_commit_oid": commit_oid,
            "remote_url": "https://example.invalid/independent-fixture.git",
            "remote_commit_sha": commit_oid,
            "remote_observed_at_utc": "2026-08-11T00:00:00Z",
            "annotated_tag": f"freeze/{prediction_id}/v1",
            "remote_ref": f"refs/tags/freeze/{prediction_id}/v1",
            "tag_object_oid": tag_oid,
        },
        "scoring": {
            "status": "NOT_DISCLOSED",
            "target_path": None,
            "result_path": None,
            "scorer_path": repo_path(SCRIPT),
            "scorer_sha256": script_hash,
        },
        "no_overclaim": "Synthetic schema fixture only; no real freeze or prediction follows.",
    }


def hostile_reports(valid: dict[str, Any]) -> dict[str, dict[str, Any]]:
    fixtures: tuple[tuple[str, str, Callable[[dict[str, Any]], None]], ...] = (
        (
            "root_extra",
            "ROOT_FIELDS_EXTRA",
            lambda row: row.__setitem__("undeclared_payload", "forbidden"),
        ),
        (
            "empty_root_identity",
            "ROOT_VALUES_INVALID",
            lambda row: row.update(
                {"freeze_id": "", "prediction_id": "", "round_id": "", "no_overclaim": ""}
            ),
        ),
        (
            "empty_target_identity",
            "TARGET_CONTRACT_INVALID",
            lambda row: row["target_contract"].update(
                {
                    "target_id": "",
                    "custodian": "",
                    "protocol_or_accession": "",
                    "estimand_id": "",
                    "units": "",
                }
            ),
        ),
        (
            "target_estimand_mismatch",
            "TARGET_ESTIMAND_MISMATCH",
            lambda row: row["target_contract"].__setitem__(
                "estimand_id", "MISMATCHED-ESTIMAND"
            ),
        ),
        (
            "target_leakage",
            "TARGET_LEAKAGE",
            lambda row: row["target_contract"].__setitem__("target_value", "0.125"),
        ),
        (
            "hidden_sealed_payload",
            "TARGET_LEAKAGE",
            lambda row: row["target_contract"]["commitment"].__setitem__(
                "sealed_payload", "opaque-but-undeclared"
            ),
        ),
        (
            "target_alias",
            "TARGET_LEAKAGE",
            lambda row: row["target_contract"].__setitem__("holdout_value", "0.125"),
        ),
        (
            "temporal_order",
            "TEMPORAL_ORDER_INVALID",
            lambda row: row["provenance"].__setitem__(
                "remote_observed_at_utc", "2026-08-13T00:00:00Z"
            ),
        ),
        (
            "hash_mutation",
            "HASH_FAILURE",
            lambda row: row["contestant_snapshot"][1].__setitem__(
                "normalized_sha256", "0" * 64
            ),
        ),
        (
            "path_traversal",
            "HASH_FAILURE",
            lambda row: row["contestant_snapshot"][1].__setitem__(
                "path", "../outside-repository.py"
            ),
        ),
        (
            "independence",
            "INDEPENDENCE_OVERLAP",
            lambda row: row["target_contract"].__setitem__(
                "independence_group", "INDEPENDENT-DISCOVERY-GROUP"
            ),
        ),
        (
            "baseline_missing",
            "BASELINE_MISSING",
            lambda row: row.__setitem__("contestant_snapshot", row["contestant_snapshot"][1:]),
        ),
        (
            "duplicate_candidate_map",
            "MAP_CANDIDATE_DUPLICATE",
            lambda row: row["observable_contract"]["candidate_maps"].append(
                copy.deepcopy(row["observable_contract"]["candidate_maps"][0])
            ),
        ),
        (
            "eligible_map_missing",
            "ELIGIBLE_MAP_MISSING",
            lambda row: row["observable_contract"].__setitem__("candidate_maps", []),
        ),
        (
            "unbound_prediction",
            "PREDICTION_CANDIDATE_UNBOUND",
            lambda row: row["prediction_contract"].__setitem__(
                "candidate_id", "UNREGISTERED-CANDIDATE"
            ),
        ),
        (
            "input_source_id_missing",
            "INPUT_FIELDS_INVALID",
            lambda row: row["prediction_contract"]["allowed_inputs"][0].pop(
                "source_id"
            ),
        ),
        (
            "input_discovery_source_id",
            "DISCOVERY_REUSE",
            lambda row: row["prediction_contract"]["allowed_inputs"][0].__setitem__(
                "source_id", "INDEPENDENT-DISCOVERY-001"
            ),
        ),
        (
            "input_source_alias",
            "INPUT_FIELDS_INVALID",
            lambda row: row["prediction_contract"]["allowed_inputs"][0].__setitem__(
                "discovery_source_id", "INDEPENDENT-DISCOVERY-001"
            ),
        ),
        (
            "nested_wrong_type",
            "COMMITMENT_INVALID",
            lambda row: row["target_contract"].__setitem__("commitment", []),
        ),
        (
            "commitment_scalar_types",
            "COMMITMENT_INVALID",
            lambda row: row["target_contract"]["commitment"].update(
                {
                    "commitment_hex": int("1" * 64),
                    "public_key_fingerprint": int("2" * 64),
                    "custodian_signature": ["not-a-string"],
                }
            ),
        ),
        (
            "provenance_oid_scalar_types",
            "REMOTE_ANCHOR_INVALID",
            lambda row: row["provenance"].update(
                {
                    "freeze_commit_oid": int("1" * 40),
                    "remote_commit_sha": int("1" * 40),
                    "tag_object_oid": int("2" * 40),
                }
            ),
        ),
        (
            "remote_url_no_hostname",
            "REMOTE_ANCHOR_INVALID",
            lambda row: row["provenance"].__setitem__("remote_url", "https://"),
        ),
        (
            "input_scalar_types",
            "INPUT_LEDGER_INVALID",
            lambda row: row["prediction_contract"]["allowed_inputs"][0].update(
                {"class": ["CALIBRATION"], "used_for": None}
            ),
        ),
        (
            "estimand_scalar_type",
            "ESTIMAND_INVALID",
            lambda row: row["observable_contract"]["common_estimand"].__setitem__(
                "definition", ["not-a-string"]
            ),
        ),
        (
            "contestant_scalar_type",
            "CONTESTANTS_INVALID",
            lambda row: row["contestant_snapshot"][1].__setitem__(
                "role", ["COMPACT_GAUGE_ALTERNATIVE"]
            ),
        ),
        (
            "estimand_container_type",
            "ESTIMAND_INVALID",
            lambda row: row["observable_contract"].__setitem__("common_estimand", []),
        ),
        (
            "estimator_container_type",
            "ESTIMAND_INVALID",
            lambda row: row["observable_contract"]["common_estimand"].__setitem__(
                "raw_estimator", []
            ),
        ),
        (
            "remote_anchor",
            "REMOTE_ANCHOR_INVALID",
            lambda row: row["provenance"].__setitem__("remote_ref", ""),
        ),
    )
    reports: dict[str, dict[str, Any]] = {}
    for name, expected_code, mutation in fixtures:
        hostile = copy.deepcopy(valid)
        mutation(hostile)
        report = validate_schema_shape(hostile, synthetic_fixture_mode=True)
        reports[name] = {
            "valid": report["valid"],
            "error_codes": report["error_codes"],
            "expected_error_code": expected_code,
            "expected_code_observed": expected_code in report["error_codes"],
        }
    return reports




def construct_survival_contract_independent() -> dict[str, Any]:
    triage = load_json(ROUND1_MANIFEST)
    matrix = triage["categorical_matrix"]
    residual: dict[str, dict[str, str]] = {}
    for candidate_id in MICROSCOPIC_CANDIDATES:
        requested = MAP_ONLY_RESIDUAL_ORACLE[candidate_id]
        residual[candidate_id] = {}
        for row_id in requested:
            residual[candidate_id][row_id] = matrix[candidate_id][row_id]
    return {
        "schema": MAP_ONLY_SURVIVAL_SCHEMA,
        "source_path": repo_path(ROUND1_MANIFEST),
        "source_sha256": normalized_sha256(ROUND1_MANIFEST),
        "hard_rows": list(triage["survival_rule"]["hard_rows"]),
        "survives_if": triage["survival_rule"]["survives_if"],
        "hypothetical_map_only_change": {
            "hypothetical_only": True,
            "microscopic_map_after": "ADMITTED",
            "preserved_fields": list(MAP_ONLY_PRESERVED_FIELDS),
        },
        "residual_hard_rows": residual,
        "map_only_survivor_ids": [],
        "all_pass_after_map_only": False,
        "substantive_new_version_requirements": {
            key: list(value) for key, value in MAP_ONLY_SUBSTANTIVE_REQUIREMENTS.items()
        },
        "boundary": "Map-only extension leaves non-PASS hard rows.",
    }


def validate_survival_contract_independent(contract: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    row = exact_object(
        contract,
        MAP_ONLY_SURVIVAL_FIELDS,
        errors,
        "MAP_ONLY_SURVIVAL_FIELDS_INVALID",
        "map_only_survival_contract",
    )
    triage = load_json(ROUND1_MANIFEST)
    rule = triage["survival_rule"]
    rule_ok = (
        row.get("schema") == MAP_ONLY_SURVIVAL_SCHEMA
        and row.get("source_path") == repo_path(ROUND1_MANIFEST)
        and path_hash_matches(row.get("source_path"), row.get("source_sha256"))
        and row.get("hard_rows") == rule["hard_rows"]
        and row.get("survives_if") == rule["survives_if"]
    )
    if not rule_ok:
        add_error(errors, "MAP_ONLY_SURVIVAL_RULE_INVALID", "all-PASS rule mismatch")
    change = exact_object(
        row.get("hypothetical_map_only_change"),
        MAP_ONLY_CHANGE_FIELDS,
        errors,
        "MAP_ONLY_CHANGE_SCOPE_INVALID",
        "hypothetical_map_only_change",
    )
    change_ok = (
        change.get("hypothetical_only") is True
        and change.get("microscopic_map_after") == "ADMITTED"
        and isinstance(change.get("preserved_fields"), list)
        and tuple(change.get("preserved_fields", [])) == MAP_ONLY_PRESERVED_FIELDS
    )
    if not change_ok:
        add_error(errors, "MAP_ONLY_CHANGE_SCOPE_INVALID", "non-map field changed")
    actual_residual = {
        candidate_id: {
            row_id: triage["categorical_matrix"][candidate_id][row_id]
            for row_id in expected_rows
        }
        for candidate_id, expected_rows in MAP_ONLY_RESIDUAL_ORACLE.items()
    }
    residual = row.get("residual_hard_rows")
    if (
        residual != MAP_ONLY_RESIDUAL_ORACLE
        or residual != actual_residual
        or any(
            status == "PASS"
            for cells in actual_residual.values()
            for status in cells.values()
        )
    ):
        add_error(errors, "MAP_ONLY_RESIDUAL_INVALID", "residual cell mismatch")
    expected_requirements = {
        key: list(value) for key, value in MAP_ONLY_SUBSTANTIVE_REQUIREMENTS.items()
    }
    if row.get("substantive_new_version_requirements") != expected_requirements:
        add_error(
            errors,
            "MAP_ONLY_SUBSTANTIVE_CHANGE_INVALID",
            "substantive repair list mismatch",
        )
    if row.get("map_only_survivor_ids") != [] or row.get(
        "all_pass_after_map_only"
    ) is not False:
        add_error(
            errors,
            "MAP_ONLY_SURVIVOR_FALSE_PROMOTION",
            "map-only survivor fabricated",
        )
    if not is_nonempty_string(row.get("boundary")):
        add_error(errors, "MAP_ONLY_SURVIVAL_FIELDS_INVALID", "boundary missing")
    return {
        "valid": not errors,
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
    }


def survival_hostiles_independent(valid: dict[str, Any]) -> dict[str, dict[str, Any]]:
    fixtures: tuple[tuple[str, str, Callable[[dict[str, Any]], None]], ...] = (
        ("hard_row_removed", "MAP_ONLY_SURVIVAL_RULE_INVALID", lambda row: row["hard_rows"].pop(0)),
        ("survival_rule_softened", "MAP_ONLY_SURVIVAL_RULE_INVALID", lambda row: row.__setitem__("survives_if", "Any row may pass.")),
        ("m1_nonpass_promoted", "MAP_ONLY_RESIDUAL_INVALID", lambda row: row["residual_hard_rows"][MICROSCOPIC_CANDIDATES[0]].__setitem__("D01-SAME-REFERENCE", "PASS")),
        ("m2_nonpass_promoted", "MAP_ONLY_RESIDUAL_INVALID", lambda row: row["residual_hard_rows"][MICROSCOPIC_CANDIDATES[1]].__setitem__("D03-PHYSICAL-ZERO-MODES", "PASS")),
        ("m5_nonpass_promoted", "MAP_ONLY_RESIDUAL_INVALID", lambda row: row["residual_hard_rows"][MICROSCOPIC_CANDIDATES[2]].__setitem__("D05-COMPACT-WINDING", "PASS")),
        ("preserved_regulator_removed", "MAP_ONLY_CHANGE_SCOPE_INVALID", lambda row: row["hypothetical_map_only_change"]["preserved_fields"].remove("regulator_and_limit_order")),
        ("map_only_survivor_fabricated", "MAP_ONLY_SURVIVOR_FALSE_PROMOTION", lambda row: row["map_only_survivor_ids"].append(MICROSCOPIC_CANDIDATES[0])),
    )
    reports: dict[str, dict[str, Any]] = {}
    for name, expected, mutation in fixtures:
        hostile = copy.deepcopy(valid)
        mutation(hostile)
        report = validate_survival_contract_independent(hostile)
        reports[name] = {
            "valid": report["valid"],
            "error_codes": report["error_codes"],
            "expected_error_code": expected,
            "expected_code_observed": expected in report["error_codes"],
        }
    return reports


def current_version_map_audit_independent() -> dict[str, Any]:
    admission = load_json(ADMISSION_FREEZE)
    rows: list[dict[str, Any]] = []
    admitted: list[str] = []
    for frozen in admission["contestants"]:
        candidate_id = frozen["candidate_id"]
        if candidate_id not in MICROSCOPIC_CANDIDATES:
            continue
        path = REPO / frozen["path"]
        candidate = load_json(path)
        if candidate.get("candidate_id") != candidate_id:
            raise AssertionError(f"candidate identity mismatch: {candidate_id}")
        pin_matches = normalized_sha256(path) == frozen["normalized_sha256"]
        normalized_status = admission["normalized_candidate_contracts"][candidate_id][
            "microscopic_to_observable_map"
        ]
        if candidate_id.endswith("PRODUCTION-FUNCTIONAL-v0"):
            absent = candidate["observable_map"][
                "map_to_round1_measured_observables"
            ] is False
            source = "M1 direct false map field"
        elif candidate_id == "PA-M2-CI8-RS-v0":
            accounting = candidate["input_prediction_accounting"]
            absent = (
                "observable_map" not in candidate
                and accounting["physical_predictions"] == []
                and accounting["holdout_prediction"] is False
                and normalized_status.split(";", 1)[0] == "ABSENT"
            )
            source = "M2 missing map object plus empty physical/holdout outputs"
        else:
            absent = candidate["observable_map"]["map_to_measured_observables"] is False
            source = "M5 direct false map field"
        if not absent:
            admitted.append(candidate_id)
        rows.append(
            {
                "candidate_id": candidate_id,
                "path": frozen["path"],
                "pinned_sha256": frozen["normalized_sha256"],
                "pin_matches": pin_matches,
                "normalized_map_status": normalized_status,
                "map_absent": absent,
                "map_only_admitted": not absent,
                "source_test": source,
            }
        )
    return {
        "closed_child_id": MAP_ONLY_CLOSED_CHILD,
        "rows": rows,
        "admitted_candidate_ids": admitted,
        "cardinality": len(admitted),
        "same_version_repair_possible": False,
        "map_only_new_version_all_pass_repair_possible": False,
        "negative_id": MAP_ONLY_NEGATIVE_ID,
        "survival_contract": construct_survival_contract_independent(),
    }


def fingerprint_integer_engine(mode_index: int = 4) -> dict[str, Any]:
    if type(mode_index) is not int or mode_index < 1:
        raise ValueError("mode index must be positive integer")
    nodes: list[tuple[int, int, int]] = []
    for a in (-1, 1):
        for b in (-1, 1):
            for c in (-1, 1):
                nodes.append((a, b, c))
    records: list[dict[str, Any]] = []
    vector: list[str] = []
    for node in nodes:
        symmetric_values: list[int] = []
        axis_rows: list[tuple[int, int, int, int, int]] = []
        for zero_based_axis in range(3):
            sign = node[zero_based_axis]
            plus_base = mode_index * mode_index - (sign * mode_index + 1) ** 2
            minus_base = mode_index * mode_index - (sign * mode_index - 1) ** 2
            d_plus = plus_base * plus_base
            d_minus = minus_base * minus_base
            symmetric_twice = d_plus + d_minus
            antisymmetric_twice = d_plus - d_minus
            if symmetric_twice % 2 or antisymmetric_twice % 2:
                raise AssertionError("half-sums are not integral")
            symmetric = symmetric_twice // 2
            antisymmetric = antisymmetric_twice // 2
            symmetric_values.append(symmetric)
            axis_rows.append(
                (zero_based_axis + 1, sign, d_plus, d_minus, antisymmetric)
            )
        symmetric_sum = sum(symmetric_values)
        for (axis, sign, d_plus, d_minus, antisymmetric), symmetric in zip(
            axis_rows, symmetric_values
        ):
            r_numerator = antisymmetric * (4 * mode_index * mode_index + 1)
            r_denominator = symmetric * 4 * sign * mode_index
            u_numerator = 3 * symmetric
            u_denominator = symmetric_sum
            r_exact = r_numerator == r_denominator
            u_exact = u_numerator == u_denominator
            records.append(
                {
                    "node": list(node),
                    "axis": axis,
                    "d_plus": d_plus,
                    "d_minus": d_minus,
                    "S": symmetric,
                    "A": antisymmetric,
                    "R_cross_products": [r_numerator, r_denominator],
                    "U_cross_products": [u_numerator, u_denominator],
                    "R": "1" if r_exact else "NOT_ONE",
                    "U": "1" if u_exact else "NOT_ONE",
                }
            )
            vector.extend(("1" if r_exact else "NOT_ONE", "1" if u_exact else "NOT_ONE"))
    return {
        "closed_child_id": FINGERPRINT_CLOSED_CHILD,
        "mode_index_fixture": mode_index,
        "node_count": len(nodes),
        "node_axis_record_count": len(records),
        "ordered_component_count": len(vector),
        "component_vector": vector,
        "all_components_exactly_one": all(item == "1" for item in vector),
        "fingerprint_sha256": hashlib.sha256(canonical_bytes(vector)).hexdigest(),
        "records": records,
        "physical_prediction": False,
    }


def response_countermodels_independent() -> dict[str, Any]:
    # Use the integer scale t -> 2t.  If kappa is degree one, the identity
    # completion scales by 2 and the square completion by 4.
    t_units = 1
    doubled_units = 2
    stiffness_ratio = doubled_units // t_units
    identity_ratio = stiffness_ratio
    square_ratio = stiffness_ratio * stiffness_ratio
    return {
        "same_stiffness_ratio": stiffness_ratio,
        "identity_response_ratio": identity_ratio,
        "square_response_ratio": square_ratio,
        "exponents": [1, 2],
        "unique_physical_exponent_derivable": False,
        "admitted_map_created": False,
        "validation_credit": False,
    }


def validate_successor_design_independent(design: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    root = exact_object(
        design,
        SUCCESSOR_DESIGN_FIELDS,
        errors,
        "SUCCESSOR_FIELDS_INVALID",
        "m2_v1_successor_design",
    )
    identity_ok = (
        root.get("schema") == SUCCESSOR_DESIGN_SCHEMA
        and root.get("design_id")
        == "PA-M2-CI8-RS-DISPERSION-MAP-v1-SCHEMA-DESIGN"
        and root.get("hypothetical_candidate_id") == M2_SUCCESSOR_ID
        and root.get("parent_candidate_id") == "PA-M2-CI8-RS-v0"
        and root.get("status") == "DESIGN_ONLY"
    )
    if not identity_ok:
        add_error(errors, "SUCCESSOR_ID_INVALID", "design identity mismatch")
    manifest = exact_object(
        root.get("candidate_manifest"),
        SUCCESSOR_MANIFEST_FIELDS,
        errors,
        "SUCCESSOR_CREATION_FORBIDDEN",
        "candidate_manifest",
    )
    if root.get("candidate_created") is not False or any(
        manifest.get(field) is not None for field in SUCCESSOR_MANIFEST_FIELDS
    ):
        add_error(errors, "SUCCESSOR_CREATION_FORBIDDEN", "candidate was materialized")
    if [root.get("admission_status"), root.get("microscopic_map_status")] != [
        "NOT_CREATED",
        "NOT_CREATED",
    ]:
        add_error(errors, "SUCCESSOR_PROMOTION_FORBIDDEN", "map/admission promoted")
    downstream = [
        root.get(field)
        for field in (
            "prediction_status",
            "target_status",
            "freeze_status",
            "tag_status",
            "score_status",
            "selection_status",
        )
    ]
    if downstream != ["NOT_CREATED"] * 6:
        add_error(errors, "SUCCESSOR_OUTPUT_FORBIDDEN", "downstream object materialized")
    required = exact_object(
        root.get("required_contract"),
        SUCCESSOR_REQUIRED_FIELDS,
        errors,
        "SUCCESSOR_REQUIRED_CONTRACT_INVALID",
        "required_contract",
    )
    response = exact_object(
        required.get("physical_response_channel"),
        SUCCESSOR_RESPONSE_FIELDS,
        errors,
        "SUCCESSOR_REQUIRED_CONTRACT_INVALID",
        "physical_response_channel",
    )
    if response.get("status") != "REQUIRED_NOT_SUPPLIED" or any(
        response.get(field) is not None for field in SUCCESSOR_RESPONSE_FIELDS[1:]
    ):
        add_error(errors, "SUCCESSOR_REQUIRED_CONTRACT_INVALID", "response map supplied")
    required_scalars = [
        required.get("candidate_neutral_estimand"),
        required.get("limit_order"),
        required.get("independent_verification"),
    ]
    if (
        required_scalars != ["REQUIRED_NOT_SUPPLIED"] * 3
        or required.get("prospective_input_firewall")
        != "MUST_BE_FROZEN_BEFORE_TARGET_DISCLOSURE"
        or required.get("open_gate") != PHYSICAL_RESPONSE_GATE
    ):
        add_error(errors, "SUCCESSOR_REQUIRED_CONTRACT_INVALID", "required slots changed")
    fingerprint = exact_object(
        required.get("finite_torus_fingerprint"),
        SUCCESSOR_FINGERPRINT_FIELDS,
        errors,
        "SUCCESSOR_FINGERPRINT_INVALID",
        "finite_torus_fingerprint",
    )
    if (
        fingerprint.get("closed_child_id") != FINGERPRINT_CLOSED_CHILD
        or fingerprint.get("ordered_component_count") != 48
        or fingerprint.get("status") != "MATHEMATICAL_FINGERPRINT_ONLY"
    ):
        add_error(errors, "SUCCESSOR_FINGERPRINT_INVALID", "fingerprint slot changed")
    budget = exact_object(
        required.get("error_budget"),
        SUCCESSOR_ERROR_FIELDS,
        errors,
        "SUCCESSOR_ERROR_BUDGET_INVALID",
        "error_budget",
    )
    budget_ok = (
        budget.get("status") == "REQUIRED_NOT_SUPPLIED"
        and isinstance(budget.get("terms"), list)
        and tuple(budget.get("terms", [])) == EXPECTED_ERROR_TERMS
        and is_nonempty_string(budget.get("required_bound"))
        and is_nonempty_string(budget.get("margin_condition"))
    )
    if not budget_ok:
        add_error(errors, "SUCCESSOR_ERROR_BUDGET_INVALID", "error budget incomplete")
    if not is_nonempty_string(root.get("no_overclaim")):
        add_error(errors, "SUCCESSOR_FIELDS_INVALID", "scope string missing")
    return {
        "valid": not errors,
        "error_codes": [row["code"] for row in errors],
        "errors": errors,
    }


def successor_hostiles_independent(valid: dict[str, Any]) -> dict[str, dict[str, Any]]:
    fixtures: tuple[tuple[str, str, Callable[[dict[str, Any]], None]], ...] = (
        ("candidate_created", "SUCCESSOR_CREATION_FORBIDDEN", lambda row: row.__setitem__("candidate_created", True)),
        ("candidate_manifest_materialized", "SUCCESSOR_CREATION_FORBIDDEN", lambda row: row["candidate_manifest"].update({"path": "strategy/fake.json", "sha256": "0" * 64})),
        ("admission_promoted", "SUCCESSOR_PROMOTION_FORBIDDEN", lambda row: row.__setitem__("admission_status", "ADMITTED")),
        ("map_promoted", "SUCCESSOR_PROMOTION_FORBIDDEN", lambda row: row.__setitem__("microscopic_map_status", "ADMITTED")),
        ("prediction_materialized", "SUCCESSOR_OUTPUT_FORBIDDEN", lambda row: row.__setitem__("prediction_status", "PRESENT")),
        ("target_materialized", "SUCCESSOR_OUTPUT_FORBIDDEN", lambda row: row.__setitem__("target_status", "PRESENT")),
        ("freeze_or_tag_materialized", "SUCCESSOR_OUTPUT_FORBIDDEN", lambda row: row.update({"freeze_status": "FROZEN", "tag_status": "CREATED"})),
        ("score_or_selection_materialized", "SUCCESSOR_OUTPUT_FORBIDDEN", lambda row: row.update({"score_status": "SCORED", "selection_status": "SELECTED"})),
        ("response_channel_smuggled", "SUCCESSOR_REQUIRED_CONTRACT_INVALID", lambda row: row["required_contract"]["physical_response_channel"].update({"status": "SUPPLIED", "map": "posthoc"})),
        ("error_budget_term_dropped", "SUCCESSOR_ERROR_BUDGET_INVALID", lambda row: row["required_contract"]["error_budget"]["terms"].pop(0)),
        ("fingerprint_dimension_changed", "SUCCESSOR_FINGERPRINT_INVALID", lambda row: row["required_contract"]["finite_torus_fingerprint"].__setitem__("ordered_component_count", 49)),
    )
    reports: dict[str, dict[str, Any]] = {}
    for name, expected, mutation in fixtures:
        hostile = copy.deepcopy(valid)
        mutation(hostile)
        report = validate_successor_design_independent(hostile)
        reports[name] = {
            "valid": report["valid"],
            "error_codes": report["error_codes"],
            "expected_error_code": expected,
            "expected_code_observed": expected in report["error_codes"],
        }
    return reports


def _igcd(a: int, b: int) -> int:
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a or 1


def _rat(numerator: int, denominator: int = 1) -> tuple[int, int]:
    if denominator == 0:
        raise ZeroDivisionError("zero rational denominator")
    if denominator < 0:
        numerator, denominator = -numerator, -denominator
    divisor = _igcd(numerator, denominator)
    return numerator // divisor, denominator // divisor


def _radd(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return _rat(left[0] * right[1] + right[0] * left[1], left[1] * right[1])


def _rneg(value: tuple[int, int]) -> tuple[int, int]:
    return -value[0], value[1]


def _rsub(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return _radd(left, _rneg(right))


def _rmul(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return _rat(left[0] * right[0], left[1] * right[1])


def _rdiv(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return _rat(left[0] * right[1], left[1] * right[0])


def _rlt(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] * right[1] < right[0] * left[1]


def _rtext(value: tuple[int, int]) -> str:
    return str(value[0]) if value[1] == 1 else f"{value[0]}/{value[1]}"


def _parse_positive_ratio(value: Any) -> tuple[int, int] | None:
    if (
        not isinstance(value, str)
        or len(value) > MAX_CANONICAL_RATIONAL_LENGTH
        or CANONICAL_POSITIVE_RATIONAL_RE.fullmatch(value) is None
    ):
        return None
    try:
        parts = value.split("/")
        numerator = int(parts[0])
        denominator = int(parts[1]) if len(parts) == 2 else 1
    except ValueError:
        return None
    if (
        _igcd(numerator, denominator) != 1
        or (len(parts) == 2 and denominator == 1)
    ):
        return None
    return numerator, denominator


def _contract_positive_ratio(
    value: Any, errors: list[dict[str, str]], label: str,
) -> tuple[int, int] | None:
    parsed = _parse_positive_ratio(value)
    if parsed is None:
        add_error(
            errors, "NUMERIC_LITERAL_INVALID",
            f"{label} must be a canonical reduced positive rational of at "
            f"most {MAX_CANONICAL_RATIONAL_LENGTH} characters",
        )
    return parsed


def linear_probe_curvature_nonidentifiability_independent() -> dict[str, Any]:
    """Integer cross-product reconstruction of the contact-curvature theorem."""

    volume = _rat(7)
    beta = _rat(3, 2)
    step = _rat(1, 5)
    d_left = _rat(5, 7)
    d_right = _rat(11, 7)
    delta_d = _rsub(d_right, d_left)
    gap = _rat(4)
    q_ground = _rat(1)
    q_excited = _rat(-1)
    zero = _rat(0)
    two = _rat(2)

    def contact(d_value: tuple[int, int], source: tuple[int, int]) -> tuple[int, int]:
        return _rdiv(_rmul(_rmul(volume, d_value), _rmul(source, source)), two)

    def central_second(values: tuple[tuple[int, int], ...]) -> tuple[int, int]:
        numerator = _radd(_rsub(values[2], _rmul(two, values[1])), values[0])
        return _rdiv(numerator, _rmul(step, step))

    finite_values = (contact(delta_d, _rneg(step)), zero, contact(delta_d, step))
    finite_second = central_second(finite_values)
    finite_normalized = _rdiv(finite_second, volume)
    boltzmann_shift = _rneg(_rmul(beta, contact(delta_d, step)))

    def levels(source: tuple[int, int]) -> tuple[tuple[int, int], tuple[int, int]]:
        return (
            _rneg(_rmul(source, q_ground)),
            _rsub(gap, _rmul(source, q_excited)),
        )

    def minimum(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
        return left if _rlt(left, right) else right

    def ground(d_value: tuple[int, int], source: tuple[int, int]) -> tuple[int, int]:
        pair = levels(source)
        return _radd(minimum(pair[0], pair[1]), contact(d_value, source))

    sources = (_rneg(step), zero, step)
    branches = [0 if _rlt(levels(j)[0], levels(j)[1]) else 1 for j in sources]
    left_curvature = _rdiv(central_second(tuple(ground(d_left, j) for j in sources)), volume)
    right_curvature = _rdiv(central_second(tuple(ground(d_right, j) for j in sources)), volume)
    shift = _rsub(right_curvature, left_curvature)
    return {
        "closed_child_id": LINEAR_PROBE_CLOSED_CHILD,
        "negative_id": LINEAR_PROBE_NEGATIVE_ID,
        "engine": "independent integer rational cross-products",
        "sign_convention": {
            "free_energy": "F_beta(J)=-beta^{-1} log Tr exp[-beta H(J)]",
            "helicity_like_response": "+V^{-1} d_J^2 F_beta(J)|J=0",
            "scalar_susceptibility": "-V^{-1} d_J^2 F_beta(J)|J=0",
            "contract_literal": HELICITY_SIGN_CONVENTION,
        },
        "fixture": {
            "volume": _rtext(volume), "beta": _rtext(beta),
            "source_step": _rtext(step), "d_left": _rtext(d_left),
            "d_right": _rtext(d_right), "delta_d": _rtext(delta_d),
            "two_level_gap": _rtext(gap),
            "probe_diagonal": [_rtext(q_ground), _rtext(q_excited)],
        },
        "finite_beta": {
            "free_energy_difference_at_step": _rtext(contact(delta_d, step)),
            "boltzmann_exponent_shift_at_step": _rtext(boltzmann_shift),
            "central_second_difference": _rtext(finite_second),
            "normalized_curvature_shift": _rtext(finite_normalized),
            "expected_shift": _rtext(delta_d),
        },
        "beta_infinity": {
            "ground_branch_indices_minus_zero_plus": branches,
            "branch_stable": branches == [0, 0, 0],
            "normalized_curvature_left": _rtext(left_curvature),
            "normalized_curvature_right": _rtext(right_curvature),
            "normalized_curvature_shift": _rtext(shift),
            "expected_shift": _rtext(delta_d),
        },
        "invariants": {
            "same_zero_source_hamiltonian": True,
            "same_first_source_derivative": True,
            "same_zero_source_state_and_spectrum": True,
            "same_finite_torus_fingerprint": True,
            "physical_response_identified": False,
            "admitted_candidate_created": False,
        },
    }


def _artifact_media_type(path: Path) -> str:
    return {
        ".py": "text/x-python", ".json": "application/json",
        ".md": "text/markdown",
    }.get(path.suffix.lower(), "application/octet-stream")


def _artifact_ref(path: Path, role: str) -> dict[str, str]:
    return {
        "path": repo_path(path), "sha256": normalized_sha256(path),
        "role": role, "media_type": _artifact_media_type(path),
    }


def _nonplaceholder_text(value: Any) -> bool:
    return (
        is_nonempty_string(value)
        and str(value).strip().upper() not in PLACEHOLDER_ENUM_VALUES
    )


def _forbidden_source_id(value: Any) -> bool:
    return (
        not is_nonempty_string(value)
        or any(token in str(value).upper() for token in FORBIDDEN_SOURCE_TOKENS)
    )


def _target_blind_prediction_text(value: Any) -> bool:
    return (
        _nonplaceholder_text(value)
        and not any(
            token in str(value).upper() for token in FORBIDDEN_SOURCE_TOKENS
        )
    )


def _unique_nonplaceholder_string_list(
    value: Any, *, nonempty: bool = True,
) -> bool:
    return (
        isinstance(value, list)
        and (bool(value) or not nonempty)
        and all(_nonplaceholder_text(item) for item in value)
        and len(value) == len(set(value))
    )


def _artifact_ref_valid(
    value: Any, expected_role: str, errors: list[dict[str, str]],
    code: str, label: str,
) -> bool:
    ref = exact_object(value, ARTIFACT_REF_FIELDS, errors, code, label)
    policy = ARTIFACT_ROLE_POLICIES[expected_role]
    path_text = ref.get("path")
    valid = False
    try:
        if (
            not isinstance(path_text, str)
            or len(path_text) > MAX_REPO_RELATIVE_PATH_LENGTH
            or "\x00" in path_text
        ):
            raise ValueError("invalid repository-relative artifact path")
        pure = PurePosixPath(path_text)
        suffix = pure.suffix.lower()
        media_oracle = {
            ".py": "text/x-python", ".json": "application/json",
            ".md": "text/markdown",
        }.get(suffix)
        valid = (
            ref.get("role") == expected_role
            and path_hash_matches(path_text, ref.get("sha256"))
            and any(path_text.startswith(prefix) for prefix in policy[0])
            and suffix in policy[1]
            and ref.get("media_type") in policy[2]
            and ref.get("media_type") == media_oracle
        )
        if expected_role == "ERROR_RUN":
            valid = (
                valid
                and "/runs/" in path_text
                and pure.name == "result.json"
            )
    except (OSError, ValueError, RuntimeError):
        valid = False
    if not valid:
        add_error(
            errors, code,
            f"{label} is not an exact bound {expected_role} artifact",
        )
    return valid


def _run_result_key_exists(run_ref: Any, result_key: Any) -> bool:
    if not isinstance(run_ref, dict) or not _nonplaceholder_text(result_key):
        return False
    path_text = run_ref.get("path")
    if not isinstance(path_text, str):
        return False
    try:
        if (
            len(path_text) > MAX_REPO_RELATIVE_PATH_LENGTH
            or "\x00" in path_text
        ):
            return False
        pure = PurePosixPath(path_text)
        candidate = REPO / Path(*pure.parts)
        payload = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError):
        return False
    return isinstance(payload, dict) and result_key in payload


def synthetic_physical_response_contract_independent() -> dict[str, Any]:
    """Positive syntax fixture using existing artifacts only as fixture data."""

    primary = PRIMARY_SCRIPT
    independent = SCRIPT
    integrated = REPO / (
        "codes/foundations/"
        "pre_a_round1_prospective_holdout_freeze_protocol_verify.py"
    )
    primary_run = REPO / (
        "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-11-primary-"
        "pre-a-round1-prospective-holdout-freeze-protocol/result.json"
    )
    independent_run = REPO / (
        "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-11-independent-"
        "pre-a-round1-prospective-holdout-freeze-protocol/result.json"
    )
    integrated_run = REPO / (
        "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-11-integrated-"
        "pre-a-round1-prospective-holdout-freeze-protocol/result.json"
    )
    change_evidence = {
        "SECOND_ORDER_SOURCE_LAW": _artifact_ref(primary, "SOURCE_LAW"),
        "COMPACT_OR_GAUGE_ACTION": _artifact_ref(
            primary, "COMPACT_OR_GAUGE_ACTION"
        ),
        "STATE_REFERENCE_CHANGE": _artifact_ref(
            M2_MANIFEST, "STATE_EXISTENCE"
        ),
        "PHYSICAL_CONTROL_MAP": _artifact_ref(
            independent, "PHYSICAL_CONTROL_MAP"
        ),
        "REGULATOR_OR_LIMIT_CHANGE": _artifact_ref(
            independent, "RESPONSE_MAP"
        ),
        "ERROR_BOUND_PROOF": _artifact_ref(primary, "PROOF"),
    }
    term_specs = (
        (EXPECTED_ERROR_TERMS[0], primary, primary_run,
         "m2_finite_torus_dispersion_fingerprint"),
        (EXPECTED_ERROR_TERMS[1], independent, independent_run,
         "m2_v1_successor_design_validation"),
        (EXPECTED_ERROR_TERMS[2], integrated, integrated_run, "cross_derived"),
        (EXPECTED_ERROR_TERMS[3], primary, primary_run,
         "m2_retrospective_stiffness_map_underdetermination"),
        (EXPECTED_ERROR_TERMS[4], independent, independent_run,
         "current_version_map_only_audit"),
        (EXPECTED_ERROR_TERMS[5], integrated, integrated_run,
         "normalized_fresh_sentinels"),
    )
    terms = [
        {
            "id": identifier, "bound": "1/100",
            "script_ref": _artifact_ref(script, "ERROR_SCRIPT"),
            "run_ref": _artifact_ref(run, "ERROR_RUN"),
            "result_key": result_key,
            "uniform_domain": "SYNTHETIC_COMPACT_FIXTURE_DOMAIN",
        }
        for identifier, script, run, result_key in term_specs
    ]
    ledger = [
        {
            "id": "INPUT-CONTROL-001", "class": "CALIBRATION",
            "source_id": "SYNTHETIC-CAL-001", "units": "dimensionless",
            "range": "SYNTHETIC_FROZEN_INTERVAL",
            "used_for": "CONTROL_MAP_ONLY",
        },
        {
            "id": "INPUT-PROBE-001", "class": "INSERTED",
            "source_id": "SYNTHETIC-INPUT-001", "units": "fixture_units",
            "range": "SYNTHETIC_FROZEN_SINGLETON",
            "used_for": "PROBE_LAW_ONLY",
        },
        {
            "id": "INPUT-STATE-001", "class": "MATCHED",
            "source_id": "SYNTHETIC-STATE-001", "units": "dimensionless",
            "range": "SYNTHETIC_STATE_FAMILY",
            "used_for": "STATE_REFERENCE_ONLY",
        },
        {
            "id": "INPUT-DERIVED-001", "class": "DERIVED",
            "source_id": "SYNTHETIC-DERIVED-001", "units": "dimensionless",
            "range": "SYNTHETIC_DERIVED_DOMAIN",
            "used_for": "RESPONSE_AND_ERROR_ONLY",
        },
        {
            "id": "INPUT-PREDICTED-001", "class": "PREDICTED",
            "source_id": "SYNTHETIC-PREDICTED-001", "units": "dimensionless",
            "range": "SYNTHETIC_PREDICTION_SINGLETON",
            "used_for": "PREDICTION_ONLY",
        },
    ]
    candidate_id = "SYNTHETIC-M2-PHYSICAL-RESPONSE-CANDIDATE-v1"
    estimand_id = "SYNTHETIC-HELICITY-ESTIMAND-001"
    return {
        "schema": PHYSICAL_CONTRACT_SCHEMA,
        "contract_id": (
            "PA-M2-PHYSICAL-RESPONSE-MINIMUM-CONTRACT-SYNTAX-FIXTURE-v1"
        ),
        "candidate_id": candidate_id,
        "parent_candidate_id": "PA-M2-CI8-RS-v0",
        "status": "SCHEMA_FIXTURE_ONLY",
        "fixture_only": True,
        "candidate_created": False,
        "version_delta": {
            "classification": "SUBSTANTIVE_NEW_VERSION",
            "substantive_changes": list(MANDATORY_SUBSTANTIVE_CHANGES),
            "change_evidence": change_evidence,
            "all_ten_rows_required": True,
        },
        "physical_control_map": {
            "kind": "TARGET_BLIND_PHYSICAL_CONTROL_MAP",
            "physical_variable": "SYNTHETIC_REDUCED_CONTROL_T",
            "r_of_t": "SYNTHETIC_PREDECLARED_R_OF_T",
            "domain": "SYNTHETIC_ORDERED_SIDE_INTERVAL",
            "scaling_window": "SYNTHETIC_FROZEN_WINDOW",
            "units": "dimensionless", "target_blind": True,
            "uncertainty_term": "state_reference_transfer",
            "map_ref": _artifact_ref(independent, "PHYSICAL_CONTROL_MAP"),
            "source_ids": ["SYNTHETIC-CAL-001"],
        },
        "probe_contract": {
            "source_id": "SYNTHETIC-U1-TWIST-J",
            "source_type": "BOUNDARY_TWIST_OR_EXTERNAL_GAUGE_PROBE",
            "source_units": "dimensionless_twist",
            "linear_operator": "SYNTHETIC_DECLARED_CURRENT_OPERATOR_Q",
            "source_law_ref": _artifact_ref(primary, "SOURCE_LAW"),
            "linear_probe_ref": _artifact_ref(primary, "LINEAR_PROBE"),
            "quadratic_contact": {
                "kind": "DIAMAGNETIC_CONTACT_TERM",
                "operator": "SYNTHETIC_DECLARED_CONTACT_D",
                "artifact_ref": _artifact_ref(primary, "QUADRATIC_CONTACT"),
            },
            "compact_or_gauge_action": {
                "kind": "COMPACT_U1_GAUGE_ACTION",
                "configuration": "SYNTHETIC_COMPACT_U1_CONFIGURATION",
                "winding_or_flux_law": "SYNTHETIC_WINDING_FLUX_LAW",
                "artifact_ref": _artifact_ref(
                    primary, "COMPACT_OR_GAUGE_ACTION"
                ),
            },
            "normalization": "SYNTHETIC_FROZEN_FLUX_TWIST_NORMALIZATION",
            "source_ids": ["SYNTHETIC-INPUT-001"],
        },
        "state_reference_contract": {
            "kind": "SELECTED_PHASE_REFERENCE_FAMILY",
            "ensemble": "SYNTHETIC_FINITE_TEMPERATURE_GIBBS_FAMILY",
            "phase": "SYNTHETIC_SELECTED_ORDERED_PHASE",
            "reference": "SYNTHETIC_SOURCE_ZERO_REFERENCE",
            "volume_boundary_regulator": "SYNTHETIC_TORUS_REGULATOR_FAMILY",
            "existence_ref": _artifact_ref(M2_MANIFEST, "STATE_EXISTENCE"),
            "physical_modes_and_quotients": (
                "SYNTHETIC_DECLARED_MODE_QUOTIENT_LIST"
            ),
            "source_ids": ["SYNTHETIC-STATE-001"],
        },
        "response_definition": {
            "kind": "HELICITY_FREE_ENERGY_CURVATURE",
            "definition": "rho=+V^-1*d_J^2 F_beta(J)|J=0",
            "sign_convention": HELICITY_SIGN_CONVENTION,
            "limit_order": list(LIMIT_ORDER),
            "units": "dimensionless_fixture_response",
            "common_estimand_id": estimand_id,
            "map_theorem_ref": _artifact_ref(independent, "RESPONSE_MAP"),
            "source_ids": ["SYNTHETIC-DERIVED-001"],
        },
        "estimand_binding": {
            "id": estimand_id,
            "kind": "CANDIDATE_NEUTRAL_HELICITY_ESTIMAND",
            "definition": "SYNTHETIC_HELICITY_RESPONSE_CRITICAL_EXPONENT",
            "units": "dimensionless_fixture_response",
            "raw_estimator_ref": _artifact_ref(integrated, "RAW_ESTIMATOR"),
            "acceptance_margin": "1/10",
            "source_ids": ["SYNTHETIC-DERIVED-001"],
        },
        "critical_prediction": {
            "kind": "CRITICAL_EXPONENT_PREDICTION",
            "prediction_id": "SYNTHETIC-PREDICTION-001",
            "candidate_id": candidate_id, "estimand_id": estimand_id,
            "predicted_relation": "SYNTHETIC_ZETA_EQUALS_TWO_THIRDS",
            "scaling_window": "SYNTHETIC_FROZEN_WINDOW",
            "corrections": "SYNTHETIC_FROZEN_CORRECTION_CONVENTION",
            "target_blind": True, "status": "SYNTHETIC_FIXTURE_ONLY",
            "source_ids": ["SYNTHETIC-PREDICTED-001"],
        },
        "error_budget": {
            "terms": terms, "total_bound": "3/50",
            "acceptance_margin": "1/10", "strict_margin": True,
            "proof_refs": [
                _artifact_ref(primary, "PROOF"),
                _artifact_ref(independent, "PROOF"),
            ],
            "source_ids": ["SYNTHETIC-DERIVED-001"],
        },
        "common_input_ledger": ledger,
        "hard_row_rerun": {
            "rows": {identifier: "PASS" for identifier in HARD_ROWS},
            "survival_rule": "Every hard row is PASS.", "all_pass": True,
        },
        "verification": {
            "primary_ref": _artifact_ref(primary, "VERIFIER_PRIMARY"),
            "independent_ref": _artifact_ref(
                independent, "VERIFIER_INDEPENDENT"
            ),
            "integrated_ref": _artifact_ref(integrated, "VERIFIER_INTEGRATED"),
            "fixture_only": True,
        },
        "prospective_firewall": {
            "target_value_present": False,
            "allowed_input_source_ids": [row["source_id"] for row in ledger],
            "forbidden_source_ids": list(FIXTURE_FORBIDDEN_SOURCE_IDS),
            "forbidden_target_dependent_choices": list(
                FORBIDDEN_TARGET_CHOICES
            ),
            "external_commitment_status": "REQUIRED_EXTERNAL_NOT_SUPPLIED",
            "remote_verification_status": "REQUIRED_EXTERNAL_NOT_SUPPLIED",
        },
        "no_overclaim": (
            "Syntax-only fixture: artifact existence, hashes, roles, enums and "
            "bindings are checked; semantic physical correctness and external "
            "prospective commitment remain unproved, and no candidate or "
            "prediction is created."
        ),
    }


def validate_physical_response_contract_independent(contract: Any) -> dict[str, Any]:
    """Fail closed on syntax/provenance; do not infer physical semantics."""

    errors: list[dict[str, str]] = []
    root = exact_object(
        contract, PHYSICAL_CONTRACT_FIELDS, errors,
        "PHYSICAL_CONTRACT_FIELDS_INVALID", "physical_response_contract",
    )
    if (
        root.get("schema") != PHYSICAL_CONTRACT_SCHEMA
        or root.get("status") != "SCHEMA_FIXTURE_ONLY"
        or root.get("fixture_only") is not True
        or root.get("candidate_created") is not False
        or not _nonplaceholder_text(root.get("contract_id"))
        or not _nonplaceholder_text(root.get("candidate_id"))
        or root.get("parent_candidate_id") != "PA-M2-CI8-RS-v0"
    ):
        add_error(
            errors, "PHYSICAL_CONTRACT_LIFECYCLE_INVALID",
            "fixture lifecycle invalid",
        )

    delta = exact_object(
        root.get("version_delta"), VERSION_DELTA_FIELDS, errors,
        "PHYSICAL_CONTRACT_VERSION_DELTA_INVALID", "version_delta",
    )
    changes = delta.get("substantive_changes")
    change_set = (
        set(changes)
        if isinstance(changes, list)
        and all(isinstance(item, str) for item in changes)
        else set()
    )
    if (
        delta.get("classification") != "SUBSTANTIVE_NEW_VERSION"
        or not isinstance(changes, list)
        or not changes
        or len(changes) != len(change_set)
        or not change_set <= set(SUBSTANTIVE_CHANGE_ENUM)
        or not set(MANDATORY_SUBSTANTIVE_CHANGES) <= change_set
        or changes == ["MICROSCOPIC_MAP_ONLY"]
        or delta.get("all_ten_rows_required") is not True
    ):
        add_error(
            errors, "PHYSICAL_CONTRACT_VERSION_DELTA_INVALID",
            "substantive change enum/subset invalid",
        )
    change_evidence = exact_object(
        delta.get("change_evidence"), CHANGE_EVIDENCE_FIELDS, errors,
        "PHYSICAL_CONTRACT_VERSION_DELTA_INVALID",
        "version_delta.change_evidence",
    )
    for change_id, role in CHANGE_EVIDENCE_ROLES.items():
        _artifact_ref_valid(
            change_evidence.get(change_id), role, errors,
            "PHYSICAL_CONTRACT_VERSION_DELTA_INVALID",
            f"change_evidence.{change_id}",
        )

    control = exact_object(
        root.get("physical_control_map"), CONTROL_MAP_FIELDS, errors,
        "PHYSICAL_CONTRACT_CONTROL_MAP_INVALID", "physical_control_map",
    )
    if (
        control.get("kind") != "TARGET_BLIND_PHYSICAL_CONTROL_MAP"
        or any(
            not _target_blind_prediction_text(control.get(field))
            for field in (
                "physical_variable", "r_of_t", "domain", "scaling_window",
            )
        )
        or not _nonplaceholder_text(control.get("units"))
        or control.get("target_blind") is not True
        or control.get("uncertainty_term") not in EXPECTED_ERROR_TERMS
    ):
        add_error(
            errors, "PHYSICAL_CONTRACT_CONTROL_MAP_INVALID",
            "control map invalid",
        )
    _artifact_ref_valid(
        control.get("map_ref"), "PHYSICAL_CONTROL_MAP", errors,
        "PHYSICAL_CONTRACT_CONTROL_MAP_INVALID", "physical_control_map.map_ref",
    )

    probe = exact_object(
        root.get("probe_contract"), PROBE_CONTRACT_FIELDS, errors,
        "PHYSICAL_CONTRACT_PROBE_INVALID", "probe_contract",
    )
    if (
        probe.get("source_type")
        != "BOUNDARY_TWIST_OR_EXTERNAL_GAUGE_PROBE"
        or any(
            not _nonplaceholder_text(probe.get(field))
            for field in (
                "source_id", "source_units", "linear_operator", "normalization",
            )
        )
    ):
        add_error(
            errors, "PHYSICAL_CONTRACT_PROBE_INVALID",
            "probe enum/text invalid",
        )
    _artifact_ref_valid(
        probe.get("source_law_ref"), "SOURCE_LAW", errors,
        "PHYSICAL_CONTRACT_PROBE_INVALID", "probe_contract.source_law_ref",
    )
    _artifact_ref_valid(
        probe.get("linear_probe_ref"), "LINEAR_PROBE", errors,
        "PHYSICAL_CONTRACT_PROBE_INVALID", "probe_contract.linear_probe_ref",
    )
    contact = exact_object(
        probe.get("quadratic_contact"), QUADRATIC_CONTACT_FIELDS, errors,
        "PHYSICAL_CONTRACT_PROBE_INVALID", "probe_contract.quadratic_contact",
    )
    if (
        contact.get("kind") != "DIAMAGNETIC_CONTACT_TERM"
        or not _nonplaceholder_text(contact.get("operator"))
    ):
        add_error(
            errors, "PHYSICAL_CONTRACT_PROBE_INVALID",
            "quadratic contact placeholder/enum invalid",
        )
    _artifact_ref_valid(
        contact.get("artifact_ref"), "QUADRATIC_CONTACT", errors,
        "PHYSICAL_CONTRACT_PROBE_INVALID", "quadratic_contact.artifact_ref",
    )
    compact = exact_object(
        probe.get("compact_or_gauge_action"), COMPACT_ACTION_FIELDS, errors,
        "PHYSICAL_CONTRACT_PROBE_INVALID",
        "probe_contract.compact_or_gauge_action",
    )
    if (
        compact.get("kind") != "COMPACT_U1_GAUGE_ACTION"
        or not _nonplaceholder_text(compact.get("configuration"))
        or not _nonplaceholder_text(compact.get("winding_or_flux_law"))
    ):
        add_error(
            errors, "PHYSICAL_CONTRACT_PROBE_INVALID",
            "compact/gauge action placeholder/enum invalid",
        )
    _artifact_ref_valid(
        compact.get("artifact_ref"), "COMPACT_OR_GAUGE_ACTION", errors,
        "PHYSICAL_CONTRACT_PROBE_INVALID",
        "compact_or_gauge_action.artifact_ref",
    )

    state = exact_object(
        root.get("state_reference_contract"), STATE_REFERENCE_FIELDS, errors,
        "PHYSICAL_CONTRACT_STATE_INVALID", "state_reference_contract",
    )
    if (
        state.get("kind") != "SELECTED_PHASE_REFERENCE_FAMILY"
        or any(
            not _nonplaceholder_text(state.get(field))
            for field in (
                "ensemble", "phase", "reference",
                "volume_boundary_regulator", "physical_modes_and_quotients",
            )
        )
    ):
        add_error(
            errors, "PHYSICAL_CONTRACT_STATE_INVALID",
            "state/reference enum/text invalid",
        )
    _artifact_ref_valid(
        state.get("existence_ref"), "STATE_EXISTENCE", errors,
        "PHYSICAL_CONTRACT_STATE_INVALID",
        "state_reference_contract.existence_ref",
    )

    response = exact_object(
        root.get("response_definition"), RESPONSE_DEFINITION_FIELDS, errors,
        "PHYSICAL_CONTRACT_RESPONSE_INVALID", "response_definition",
    )
    if (
        response.get("kind") != "HELICITY_FREE_ENERGY_CURVATURE"
        or response.get("definition") != "rho=+V^-1*d_J^2 F_beta(J)|J=0"
        or response.get("sign_convention") != HELICITY_SIGN_CONVENTION
        or response.get("limit_order") != list(LIMIT_ORDER)
        or not _nonplaceholder_text(response.get("units"))
        or not _nonplaceholder_text(response.get("common_estimand_id"))
    ):
        add_error(
            errors, "PHYSICAL_CONTRACT_RESPONSE_INVALID",
            "response enum/sign/limit order invalid",
        )
    _artifact_ref_valid(
        response.get("map_theorem_ref"), "RESPONSE_MAP", errors,
        "PHYSICAL_CONTRACT_RESPONSE_INVALID",
        "response_definition.map_theorem_ref",
    )

    estimand = exact_object(
        root.get("estimand_binding"), ESTIMAND_BINDING_FIELDS, errors,
        "PHYSICAL_CONTRACT_ESTIMAND_INVALID", "estimand_binding",
    )
    estimand_margin = _contract_positive_ratio(
        estimand.get("acceptance_margin"), errors,
        "estimand_binding.acceptance_margin",
    )
    if (
        estimand.get("kind") != "CANDIDATE_NEUTRAL_HELICITY_ESTIMAND"
        or any(
            not _nonplaceholder_text(estimand.get(field))
            for field in ("id", "definition", "units")
        )
        or estimand.get("id") != response.get("common_estimand_id")
        or estimand.get("units") != response.get("units")
        or estimand_margin is None
    ):
        add_error(
            errors, "PHYSICAL_CONTRACT_ESTIMAND_INVALID",
            "estimand binding/rational invalid",
        )
    _artifact_ref_valid(
        estimand.get("raw_estimator_ref"), "RAW_ESTIMATOR", errors,
        "PHYSICAL_CONTRACT_ESTIMAND_INVALID",
        "estimand_binding.raw_estimator_ref",
    )

    prediction = exact_object(
        root.get("critical_prediction"), CRITICAL_PREDICTION_FIELDS, errors,
        "PHYSICAL_CONTRACT_PREDICTION_INVALID", "critical_prediction",
    )
    if (
        prediction.get("kind") != "CRITICAL_EXPONENT_PREDICTION"
        or prediction.get("status") != "SYNTHETIC_FIXTURE_ONLY"
        or any(
            not _nonplaceholder_text(prediction.get(field))
            for field in (
                "prediction_id", "candidate_id", "estimand_id",
                "predicted_relation", "scaling_window", "corrections",
            )
        )
        or any(
            not _target_blind_prediction_text(prediction.get(field))
            for field in ("predicted_relation", "scaling_window", "corrections")
        )
        or prediction.get("candidate_id") != root.get("candidate_id")
        or prediction.get("estimand_id") != estimand.get("id")
        or prediction.get("target_blind") is not True
    ):
        add_error(
            errors, "PHYSICAL_CONTRACT_PREDICTION_INVALID",
            "prediction enum/placeholder/binding invalid",
        )

    budget = exact_object(
        root.get("error_budget"), PHYSICAL_ERROR_BUDGET_FIELDS, errors,
        "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID", "error_budget",
    )
    terms = budget.get("terms")
    if not isinstance(terms, list):
        add_error(
            errors, "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
            "error terms must be a list",
        )
        terms = []
    parsed_bounds: list[tuple[int, int]] = []
    term_ids: list[Any] = []
    result_keys: list[Any] = []
    composites: list[tuple[Any, Any, Any]] = []
    for index, value in enumerate(terms):
        term = exact_object(
            value, PHYSICAL_ERROR_TERM_FIELDS, errors,
            "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
            f"error_budget.terms[{index}]",
        )
        term_ids.append(term.get("id"))
        parsed = _contract_positive_ratio(
            term.get("bound"), errors, f"error_budget.terms[{index}].bound"
        )
        if parsed is None:
            add_error(
                errors, "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
                "error bound rational invalid",
            )
        else:
            parsed_bounds.append(parsed)
        _artifact_ref_valid(
            term.get("script_ref"), "ERROR_SCRIPT", errors,
            "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
            f"error term {index} script",
        )
        run_ok = _artifact_ref_valid(
            term.get("run_ref"), "ERROR_RUN", errors,
            "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
            f"error term {index} run",
        )
        result_key = term.get("result_key")
        result_keys.append(result_key)
        if (
            not _nonplaceholder_text(result_key)
            or (run_ok and not _run_result_key_exists(
                term.get("run_ref"), result_key
            ))
        ):
            add_error(
                errors, "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
                "error result_key missing from bound run",
            )
        if not _nonplaceholder_text(term.get("uniform_domain")):
            add_error(
                errors, "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
                "uniform domain invalid",
            )
        script_ref = term.get("script_ref")
        run_ref = term.get("run_ref")
        composites.append((
            script_ref.get("path") if isinstance(script_ref, dict) else None,
            run_ref.get("path") if isinstance(run_ref, dict) else None,
            result_key,
        ))
    total = _contract_positive_ratio(
        budget.get("total_bound"), errors, "error_budget.total_bound"
    )
    margin = _contract_positive_ratio(
        budget.get("acceptance_margin"), errors, "error_budget.acceptance_margin"
    )
    proof_refs = budget.get("proof_refs")
    proof_paths: list[Any] = []
    if not isinstance(proof_refs, list) or len(proof_refs) < 2:
        add_error(
            errors, "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
            "at least two proof refs required",
        )
        proof_refs = []
    for index, proof_ref in enumerate(proof_refs):
        _artifact_ref_valid(
            proof_ref, "PROOF", errors,
            "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
            f"error_budget.proof_refs[{index}]",
        )
        proof_paths.append(
            proof_ref.get("path") if isinstance(proof_ref, dict) else None
        )
    summed = _rat(0)
    for parsed_bound in parsed_bounds:
        summed = _radd(summed, parsed_bound)
    if (
        len(terms) != len(EXPECTED_ERROR_TERMS)
        or not _unique_nonplaceholder_string_list(term_ids)
        or set(term_ids) != set(EXPECTED_ERROR_TERMS)
        or len(parsed_bounds) != len(EXPECTED_ERROR_TERMS)
        or not _unique_nonplaceholder_string_list(result_keys)
        or not all(
            all(isinstance(part, str) for part in composite)
            for composite in composites
        )
        or len(composites) != len(set(composites))
        or total is None
        or margin is None
        or total != summed
        or margin != estimand_margin
        or budget.get("strict_margin") is not True
        or not _rlt(total, margin)
        or not _unique_nonplaceholder_string_list(proof_paths)
    ):
        add_error(
            errors, "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
            "error evidence/total/margin contract invalid",
        )

    ledger = root.get("common_input_ledger")
    if not isinstance(ledger, list) or not ledger:
        add_error(
            errors, "PHYSICAL_CONTRACT_INPUT_LEDGER_INVALID",
            "input ledger absent",
        )
        ledger = []
    input_ids: list[Any] = []
    source_ids: list[Any] = []
    for index, value in enumerate(ledger):
        item = exact_object(
            value, INPUT_LEDGER_FIELDS, errors,
            "PHYSICAL_CONTRACT_INPUT_LEDGER_INVALID",
            f"common_input_ledger[{index}]",
        )
        input_ids.append(item.get("id"))
        source_ids.append(item.get("source_id"))
        if (
            any(
                not _nonplaceholder_text(item.get(field))
                for field in INPUT_LEDGER_FIELDS
            )
            or not isinstance(item.get("class"), str)
            or item.get("class") not in PHYSICAL_INPUT_CLASSES
            or _forbidden_source_id(item.get("source_id"))
        ):
            add_error(
                errors, "PHYSICAL_CONTRACT_INPUT_LEDGER_INVALID",
                "input row/source invalid",
            )
    if (
        not _unique_nonplaceholder_string_list(input_ids)
        or not _unique_nonplaceholder_string_list(source_ids)
    ):
        add_error(
            errors, "PHYSICAL_CONTRACT_INPUT_LEDGER_INVALID",
            "input/source IDs must be unique",
        )
    source_set = (
        set(source_ids)
        if _unique_nonplaceholder_string_list(source_ids)
        else set()
    )

    section_source_values = (
        ("physical_control_map", control.get("source_ids")),
        ("probe_contract", probe.get("source_ids")),
        ("state_reference_contract", state.get("source_ids")),
        ("response_definition", response.get("source_ids")),
        ("estimand_binding", estimand.get("source_ids")),
        ("critical_prediction", prediction.get("source_ids")),
        ("error_budget", budget.get("source_ids")),
    )
    for label, values in section_source_values:
        valid_sources = (
            isinstance(values, list)
            and bool(values)
            and all(
                is_nonempty_string(item) and not _forbidden_source_id(item)
                for item in values
            )
            and len(values) == len(set(values))
            and set(values) <= source_set
        )
        if not valid_sources:
            add_error(
                errors, "PHYSICAL_CONTRACT_SOURCE_BINDING_INVALID",
                f"{label}.source_ids unbound",
            )

    hard = exact_object(
        root.get("hard_row_rerun"), HARD_ROW_RERUN_FIELDS, errors,
        "PHYSICAL_CONTRACT_HARD_ROWS_INVALID", "hard_row_rerun",
    )
    rows = hard.get("rows")
    if (
        not isinstance(rows, dict)
        or len(rows) != len(HARD_ROWS)
        or set(rows) != set(HARD_ROWS)
        or any(rows.get(identifier) != "PASS" for identifier in HARD_ROWS)
        or hard.get("survival_rule") != "Every hard row is PASS."
        or hard.get("all_pass") is not True
    ):
        add_error(
            errors, "PHYSICAL_CONTRACT_HARD_ROWS_INVALID",
            "exact ten-row PASS set required",
        )

    verification = exact_object(
        root.get("verification"), VERIFICATION_CONTRACT_FIELDS, errors,
        "PHYSICAL_CONTRACT_VERIFICATION_INVALID", "verification",
    )
    verifier_specs = (
        ("primary_ref", "VERIFIER_PRIMARY"),
        ("independent_ref", "VERIFIER_INDEPENDENT"),
        ("integrated_ref", "VERIFIER_INTEGRATED"),
    )
    verifier_paths: list[Any] = []
    verifier_hashes: list[Any] = []
    for field, role in verifier_specs:
        ref = verification.get(field)
        _artifact_ref_valid(
            ref, role, errors, "PHYSICAL_CONTRACT_VERIFICATION_INVALID",
            f"verification.{field}",
        )
        verifier_paths.append(
            ref.get("path") if isinstance(ref, dict) else None
        )
        verifier_hashes.append(
            ref.get("sha256") if isinstance(ref, dict) else None
        )
    if (
        verification.get("fixture_only") is not True
        or not _unique_nonplaceholder_string_list(verifier_paths)
        or not _unique_nonplaceholder_string_list(verifier_hashes)
    ):
        add_error(
            errors, "PHYSICAL_CONTRACT_VERIFICATION_INVALID",
            "three distinct verifier paths/hashes required",
        )

    firewall = exact_object(
        root.get("prospective_firewall"), PROSPECTIVE_FIREWALL_FIELDS, errors,
        "PHYSICAL_CONTRACT_FIREWALL_INVALID", "prospective_firewall",
    )
    allowed_ids = firewall.get("allowed_input_source_ids")
    forbidden_ids = firewall.get("forbidden_source_ids")
    forbidden_choices = firewall.get("forbidden_target_dependent_choices")
    if (
        firewall.get("target_value_present") is not False
        or not _unique_nonplaceholder_string_list(allowed_ids)
        or set(allowed_ids) != source_set
        or any(_forbidden_source_id(item) for item in allowed_ids)
        or not _unique_nonplaceholder_string_list(forbidden_ids)
        or set(forbidden_ids) != set(FIXTURE_FORBIDDEN_SOURCE_IDS)
        or set(allowed_ids) & set(forbidden_ids)
        or not _unique_nonplaceholder_string_list(forbidden_choices)
        or set(forbidden_choices) != set(FORBIDDEN_TARGET_CHOICES)
        or any(
            str(item).strip().upper() in PLACEHOLDER_ENUM_VALUES
            for item in forbidden_choices
        )
        or firewall.get("external_commitment_status")
        != "REQUIRED_EXTERNAL_NOT_SUPPLIED"
        or firewall.get("remote_verification_status")
        != "REQUIRED_EXTERNAL_NOT_SUPPLIED"
    ):
        add_error(
            errors, "PHYSICAL_CONTRACT_FIREWALL_INVALID",
            "prospective source firewall invalid",
        )

    boundary = root.get("no_overclaim")
    if (
        not _nonplaceholder_text(boundary)
        or "syntax-only" not in str(boundary).lower()
        or "semantic" not in str(boundary).lower()
        or "external" not in str(boundary).lower()
    ):
        add_error(
            errors, "PHYSICAL_CONTRACT_FIELDS_INVALID",
            "syntax/semantic/external boundary absent",
        )
    return {
        "valid": not errors,
        "error_codes": [row["code"] for row in errors],
        "errors": errors,
    }


def physical_response_contract_hostiles_independent(
    valid: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    def map_only_payload(row: dict[str, Any]) -> None:
        row["version_delta"]["change_evidence"] = {
            "MICROSCOPIC_MAP_ONLY": copy.deepcopy(
                row["response_definition"]["map_theorem_ref"]
            )
        }

    def reuse_error_evidence(row: dict[str, Any]) -> None:
        first = row["error_budget"]["terms"][0]
        second = row["error_budget"]["terms"][1]
        second["script_ref"] = copy.deepcopy(first["script_ref"])
        second["run_ref"] = copy.deepcopy(first["run_ref"])
        second["result_key"] = first["result_key"]

    fixtures: dict[str, Callable[[dict[str, Any]], None]] = {
        "candidate_materialized": (
            lambda row: row.__setitem__("candidate_created", True)
        ),
        "substantive_change_mislabeled_map_only": (
            lambda row: row["version_delta"].__setitem__(
                "classification", "MAP_ONLY"
            )
        ),
        "control_map_missing": (
            lambda row: row["physical_control_map"].__setitem__("r_of_t", "")
        ),
        "target_dependent_control": (
            lambda row: row["physical_control_map"].__setitem__(
                "target_blind", False
            )
        ),
        "quadratic_contact_missing": (
            lambda row: row["probe_contract"].__setitem__(
                "quadratic_contact", None
            )
        ),
        "compact_action_missing": (
            lambda row: row["probe_contract"].__setitem__(
                "compact_or_gauge_action", None
            )
        ),
        "state_reference_missing": (
            lambda row: row["state_reference_contract"].__setitem__(
                "reference", ""
            )
        ),
        "scalar_susceptibility_relabel": (
            lambda row: row["response_definition"].__setitem__(
                "sign_convention", "scalar_susceptibility=-V^-1*d2F/dJ2"
            )
        ),
        "limit_order_missing": (
            lambda row: row["response_definition"].__setitem__(
                "limit_order", []
            )
        ),
        "estimand_mismatch": (
            lambda row: row["estimand_binding"].__setitem__(
                "id", "OTHER-ESTIMAND"
            )
        ),
        "fingerprint_promoted_as_response": (
            lambda row: row["response_definition"].__setitem__(
                "map_theorem_ref", FINGERPRINT_CLOSED_CHILD
            )
        ),
        "error_term_dropped": (
            lambda row: row["error_budget"]["terms"].pop()
        ),
        "error_total_not_sum": (
            lambda row: row["error_budget"].__setitem__("total_bound", "1/2")
        ),
        "error_margin_not_strict": (
            lambda row: row["error_budget"].__setitem__(
                "strict_margin", False
            )
        ),
        "hard_row_nonpass": (
            lambda row: row["hard_row_rerun"]["rows"].__setitem__(
                "D05-COMPACT-WINDING", "NOT_ADMITTED"
            )
        ),
        "single_implementation": (
            lambda row: row["verification"].__setitem__(
                "independent_ref",
                copy.deepcopy(row["verification"]["primary_ref"]),
            )
        ),
        "target_value_present": (
            lambda row: row["prospective_firewall"].__setitem__(
                "target_value_present", True
            )
        ),
        "map_only_payload_under_substantive_label": map_only_payload,
        "unknown_substantive_change": (
            lambda row: row["version_delta"]["substantive_changes"].append(
                "UNKNOWN_SUBSTANTIVE_CHANGE"
            )
        ),
        "duplicate_substantive_change": (
            lambda row: row["version_delta"]["substantive_changes"].append(
                row["version_delta"]["substantive_changes"][0]
            )
        ),
        "unbound_probe_hash": (
            lambda row: row["probe_contract"]["source_law_ref"].__setitem__(
                "sha256", "0" * 64
            )
        ),
        "probe_artifact_wrong_role": (
            lambda row: row["probe_contract"]["linear_probe_ref"].__setitem__(
                "role", "RESPONSE_MAP"
            )
        ),
        "quadratic_contact_placeholder": (
            lambda row: row["probe_contract"]["quadratic_contact"].__setitem__(
                "kind", "TBD"
            )
        ),
        "compact_action_placeholder": (
            lambda row: row["probe_contract"]["compact_or_gauge_action"].__setitem__(
                "kind", "NONE"
            )
        ),
        "state_existence_ref_unbound": (
            lambda row: row["state_reference_contract"]["existence_ref"].__setitem__(
                "sha256", "0" * 64
            )
        ),
        "response_map_ref_unbound": (
            lambda row: row["response_definition"]["map_theorem_ref"].__setitem__(
                "sha256", "0" * 64
            )
        ),
        "limit_order_placeholder": (
            lambda row: row["response_definition"].__setitem__(
                "limit_order", ["SOURCE_TO_ZERO", "TBD"]
            )
        ),
        "limit_order_permuted": (
            lambda row: row["response_definition"].__setitem__(
                "limit_order", list(reversed(LIMIT_ORDER))
            )
        ),
        "prediction_placeholder": (
            lambda row: row["critical_prediction"].__setitem__(
                "predicted_relation", "TBD"
            )
        ),
        "prediction_candidate_unbound": (
            lambda row: row["critical_prediction"].__setitem__(
                "candidate_id", "OTHER-CANDIDATE"
            )
        ),
        "proof_ref_unbound": (
            lambda row: row["error_budget"]["proof_refs"][0].__setitem__(
                "sha256", "0" * 64
            )
        ),
        "error_evidence_reused": reuse_error_evidence,
        "error_result_key_missing": (
            lambda row: row["error_budget"]["terms"][0].__setitem__(
                "result_key", "MISSING_RESULT_KEY"
            )
        ),
        "non_script_verifier": (
            lambda row: row["verification"].__setitem__(
                "primary_ref",
                _artifact_ref(AUTHORITY_MANIFEST, "VERIFIER_PRIMARY"),
            )
        ),
        "identical_verifier_hash": (
            lambda row: row["verification"]["independent_ref"].__setitem__(
                "sha256", row["verification"]["primary_ref"]["sha256"]
            )
        ),
        "integrated_ref_missing": (
            lambda row: row["verification"].__setitem__("integrated_ref", None)
        ),
        "duplicate_input_id": (
            lambda row: row["common_input_ledger"][1].__setitem__(
                "id", row["common_input_ledger"][0]["id"]
            )
        ),
        "duplicate_source_id": (
            lambda row: row["common_input_ledger"][1].__setitem__(
                "source_id", row["common_input_ledger"][0]["source_id"]
            )
        ),
        "visible_validation_source": (
            lambda row: row["common_input_ledger"][0].__setitem__(
                "class", "VISIBLE_VALIDATION"
            )
        ),
        "forbidden_source_id": (
            lambda row: row["common_input_ledger"][0].__setitem__(
                "source_id", "HOLDOUT-TARGET-001"
            )
        ),
        "source_section_unbound": (
            lambda row: row["physical_control_map"]["source_ids"].append(
                "SYNTHETIC-UNBOUND-001"
            )
        ),
        "forbidden_choices_placeholder": (
            lambda row: row["prospective_firewall"].__setitem__(
                "forbidden_target_dependent_choices", ["TBD"]
            )
        ),
        "decimal_ratio": (
            lambda row: row["estimand_binding"].__setitem__(
                "acceptance_margin", "0.1"
            )
        ),
        "unreduced_ratio": (
            lambda row: row["estimand_binding"].__setitem__(
                "acceptance_margin", "2/20"
            )
        ),
        "whitespace_ratio": (
            lambda row: row["estimand_binding"].__setitem__(
                "acceptance_margin", " 1/10"
            )
        ),
        "embedded_nul_artifact_path": (
            lambda row: row["probe_contract"]["source_law_ref"].__setitem__(
                "path", "codes/\x00.py"
            )
        ),
        "overlong_artifact_path": (
            lambda row: row["probe_contract"]["source_law_ref"].__setitem__(
                "path", "codes/" + "a" * 40000 + ".py"
            )
        ),
        "overlong_rational_literal": (
            lambda row: row["estimand_binding"].__setitem__(
                "acceptance_margin", "9" * 5000
            )
        ),
        "trailing_dot_segment_artifact_path": (
            lambda row: row["probe_contract"]["source_law_ref"].__setitem__(
                "path", row["probe_contract"]["source_law_ref"]["path"].replace(
                    "codes/foundations/", "codes/foundations./", 1
                )
            )
        ),
        "trailing_space_segment_artifact_path": (
            lambda row: row["probe_contract"]["source_law_ref"].__setitem__(
                "path", row["probe_contract"]["source_law_ref"]["path"].replace(
                    "codes/foundations/", "codes/foundations /", 1
                )
            )
        ),
        "case_changed_artifact_path": (
            lambda row: row["probe_contract"]["source_law_ref"].__setitem__(
                "path", row["probe_contract"]["source_law_ref"]["path"].replace(
                    "codes/foundations/", "codes/FOUNDATIONS/", 1
                )
            )
        ),
        "free_semantic_placeholder": (
            lambda row: row["critical_prediction"].__setitem__(
                "predicted_relation", "PLACEHOLDER"
            )
        ),
        "prediction_target_leakage": (
            lambda row: row["critical_prediction"].__setitem__(
                "predicted_relation", "ZETA_EQUALS_TARGET_VALUE"
            )
        ),
        "scaling_window_holdout_leakage": (
            lambda row: row["critical_prediction"].__setitem__(
                "scaling_window", "HOLDOUT_SELECTED_WINDOW"
            )
        ),
        "control_map_r_of_t_target_leakage": (
            lambda row: row["physical_control_map"].__setitem__(
                "r_of_t", "FIT_FROM_HOLDOUT_TARGET"
            )
        ),
        "control_map_scaling_window_holdout_leakage": (
            lambda row: row["physical_control_map"].__setitem__(
                "scaling_window", "HOLDOUT_SELECTED_WINDOW"
            )
        ),
        "denominator_one_ratio": (
            lambda row: row["estimand_binding"].__setitem__(
                "acceptance_margin", "1/1"
            )
        ),
    }
    reports: dict[str, dict[str, Any]] = {}
    for name, mutation in fixtures.items():
        hostile = copy.deepcopy(valid)
        mutation(hostile)
        report = validate_physical_response_contract_independent(hostile)
        expected = PHYSICAL_CONTRACT_HOSTILE_CODES[name]
        reports[name] = {
            "valid": report["valid"],
            "error_codes": report["error_codes"],
            "expected_error_code": expected,
            "expected_code_observed": expected in report["error_codes"],
        }
    return reports


def physical_response_contract_reordered_metamorphic_independent(
    valid: dict[str, Any],
) -> dict[str, Any]:
    reordered = copy.deepcopy(valid)
    reordered["version_delta"]["substantive_changes"].reverse()
    reordered["common_input_ledger"].reverse()
    reordered["hard_row_rerun"]["rows"] = dict(
        reversed(list(reordered["hard_row_rerun"]["rows"].items()))
    )
    reordered["error_budget"]["terms"].reverse()
    reordered["prospective_firewall"]["allowed_input_source_ids"].reverse()
    reordered["prospective_firewall"]["forbidden_source_ids"].reverse()
    reordered["prospective_firewall"][
        "forbidden_target_dependent_choices"
    ].reverse()
    return validate_physical_response_contract_independent(reordered)


def physical_response_contract_fuzz_reports_independent(
    valid: dict[str, Any],
) -> dict[str, Any]:
    cases: list[tuple[str, Callable[[dict[str, Any]], None]]] = []
    bad_ratios: tuple[Any, ...] = (
        "0.1", " 1/10", "1/10 ", "01/10", "2/20", "1/0", "0",
        "-1/10", "1//10", None, [], {},
    )
    for index, bad in enumerate(bad_ratios):
        cases.append((
            f"ratio_{index:02d}",
            lambda row, value=bad: row["error_budget"].__setitem__(
                "total_bound", value
            ),
        ))
    bad_paths = (
        "../escape.py", "/absolute.py", "codes\\bad.py", "codes/./bad.py",
        "C:/drive.py", "codes//double.py",
    )
    for index, bad_path in enumerate(bad_paths):
        cases.append((
            f"path_{index:02d}",
            lambda row, value=bad_path: row["probe_contract"][
                "source_law_ref"
            ].__setitem__("path", value),
        ))
    for index, bad_container in enumerate((None, [], "TBD", 0, True)):
        cases.append((
            f"container_{index:02d}",
            lambda row, value=bad_container: row["verification"].__setitem__(
                "integrated_ref", value
            ),
        ))
    cases.extend((
        ("nul_artifact_path", lambda row: row["probe_contract"]["source_law_ref"].__setitem__("path", "codes/\x00.py")),
        ("overlong_artifact_path", lambda row: row["probe_contract"]["source_law_ref"].__setitem__("path", "codes/" + "a" * 40000 + ".py")),
        ("overlong_rational_literal", lambda row: row["estimand_binding"].__setitem__("acceptance_margin", "9" * 5000)),
        ("trailing_dot_segment", lambda row: row["probe_contract"]["source_law_ref"].__setitem__("path", row["probe_contract"]["source_law_ref"]["path"].replace("codes/foundations/", "codes/foundations./", 1))),
        ("trailing_space_segment", lambda row: row["probe_contract"]["source_law_ref"].__setitem__("path", row["probe_contract"]["source_law_ref"]["path"].replace("codes/foundations/", "codes/foundations /", 1))),
        ("case_changed_segment", lambda row: row["probe_contract"]["source_law_ref"].__setitem__("path", row["probe_contract"]["source_law_ref"]["path"].replace("codes/foundations/", "codes/FOUNDATIONS/", 1))),
        ("semantic_na_placeholder", lambda row: row["critical_prediction"].__setitem__("predicted_relation", "N/A")),
        ("semantic_not_available_placeholder", lambda row: row["critical_prediction"].__setitem__("predicted_relation", "NOT_AVAILABLE")),
        ("prediction_target_token", lambda row: row["critical_prediction"].__setitem__("predicted_relation", "TARGET_VALUE_DEPENDENT")),
        ("scaling_holdout_token", lambda row: row["critical_prediction"].__setitem__("scaling_window", "HOLDOUT_WINDOW")),
        ("control_map_target_token", lambda row: row["physical_control_map"].__setitem__("r_of_t", "FIT_FROM_HOLDOUT_TARGET")),
        ("control_map_scaling_holdout_token", lambda row: row["physical_control_map"].__setitem__("scaling_window", "HOLDOUT_SELECTED_WINDOW")),
        ("denominator_one_ratio", lambda row: row["estimand_binding"].__setitem__("acceptance_margin", "3/1")),
        ("extra_key_root_int", lambda row: row.__setitem__(1, "unexpected")),
        ("extra_key_nested_none", lambda row: row["critical_prediction"].__setitem__(None, "unexpected")),
        ("extra_key_artifact_tuple", lambda row: row["probe_contract"]["source_law_ref"].__setitem__(("unexpected",), "unexpected")),
        ("term_id_unhashable", lambda row: row["error_budget"]["terms"][0].__setitem__("id", [])),
        ("result_key_unhashable", lambda row: row["error_budget"]["terms"][0].__setitem__("result_key", {})),
        ("proof_path_unhashable", lambda row: row["error_budget"]["proof_refs"][0].__setitem__("path", [])),
        ("input_id_unhashable", lambda row: row["common_input_ledger"][0].__setitem__("id", [])),
        ("input_class_unhashable", lambda row: row["common_input_ledger"][0].__setitem__("class", [])),
        ("source_id_unhashable", lambda row: row["common_input_ledger"][0].__setitem__("source_id", {})),
        ("allowed_source_unhashable", lambda row: row["prospective_firewall"]["allowed_input_source_ids"].__setitem__(0, [])),
        ("forbidden_choice_unhashable", lambda row: row["prospective_firewall"]["forbidden_target_dependent_choices"].__setitem__(0, {})),
        ("verifier_hash_unhashable", lambda row: row["verification"]["primary_ref"].__setitem__("sha256", [])),
    ))
    reports: list[dict[str, Any]] = []
    for name, mutation in cases:
        hostile = copy.deepcopy(valid)
        mutation(hostile)
        try:
            report = validate_physical_response_contract_independent(hostile)
            reports.append({
                "name": name, "rejected": report["valid"] is False,
                "error_codes": report["error_codes"],
            })
        except Exception as exc:
            reports.append({
                "name": name, "rejected": False,
                "exception": type(exc).__name__,
            })
    return {
        "case_count": len(reports),
        "rejected_count": sum(
            1 for row in reports if row.get("rejected") is True
        ),
        "all_rejected_without_exception": all(
            row.get("rejected") is True for row in reports
        ),
        "cases": reports,
    }

def reconstruct_checkpoint() -> dict[str, Any]:
    round1 = git_json_at(AUDITED_COMMIT, ROUND1_MANIFEST)
    admission = git_json_at(AUDITED_COMMIT, ADMISSION_FREEZE)
    m1 = git_json_at(AUDITED_COMMIT, M1_MANIFEST)
    m2 = git_json_at(AUDITED_COMMIT, M2_MANIFEST)
    m5 = git_json_at(AUDITED_COMMIT, M5_MANIFEST)

    records = sorted(
        path
        for path in git_lines(
            "ls-tree", "-r", "--name-only", AUDITED_COMMIT, "predictions/freezes"
        )
        if not path.endswith("/.gitkeep")
    )
    live_tags = sorted(git_lines("tag", "--list", "freeze/*"))
    survivors = list(round1["round1_verdict"]["admitted_microscopic_survivors"])
    normalized = admission["normalized_candidate_contracts"]
    m1_map = m1["observable_map"]["map_to_round1_measured_observables"]
    m1_prediction = m1["input_prediction_accounting"][
        "declared_non_fitting_validation_prediction"
    ]
    m2_predictions = list(m2["input_prediction_accounting"]["physical_predictions"])
    m2_holdout = m2["input_prediction_accounting"]["holdout_prediction"]
    m5_map = m5["observable_map"]["map_to_measured_observables"]
    m5_holdout = m5["input_prediction_accounting"]["holdout_prediction"]

    blockers: list[str] = []
    if not records:
        blockers.append(EXPECTED_BLOCKERS[0])
    if not survivors:
        blockers.append(EXPECTED_BLOCKERS[1])
    if m1_map is False and m1_prediction is False:
        blockers.append(EXPECTED_BLOCKERS[2])
    if not m2_predictions and m2_holdout is False:
        blockers.append(EXPECTED_BLOCKERS[3])
    if m5_map is False and m5_holdout is False:
        blockers.append(EXPECTED_BLOCKERS[4])
    if admission["completeness"]["per_parameter_common_input_ledger_complete"] is False:
        blockers.append(EXPECTED_BLOCKERS[5])
    if admission["completeness"]["visible_non_fitting_prediction_frozen"] is False:
        blockers.append(EXPECTED_BLOCKERS[6])

    head = git_lines("rev-parse", "HEAD")[0]
    return {
        "audited_commit": AUDITED_COMMIT,
        "current_head": head,
        "audited_commit_is_ancestor": git_is_ancestor(AUDITED_COMMIT, head),
        "freeze_record_count": len(records),
        "freeze_records": records,
        "local_freeze_tag_observation": {
            "count": len(live_tags),
            "tags": live_tags,
            "scope": "live local freeze/* refs at verification time",
            "load_bearing": False,
        },
        "contestant_ids": [row["candidate_id"] for row in admission["contestants"]],
        "normalized_map_status": {
            candidate_id: normalized[candidate_id]["microscopic_to_observable_map"]
            for candidate_id in MICROSCOPIC_CANDIDATES
        },
        "admitted_microscopic_survivor_count": len(survivors),
        "admitted_microscopic_survivors": survivors,
        "M1": {
            "microscopic_map": m1_map,
            "non_fitting_validation_prediction": m1_prediction,
        },
        "M2": {
            "physical_predictions": m2_predictions,
            "holdout_prediction": m2_holdout,
        },
        "M5": {"microscopic_map": m5_map, "holdout_prediction": m5_holdout},
        "per_parameter_common_input_ledger_complete": admission["completeness"][
            "per_parameter_common_input_ledger_complete"
        ],
        "prospective_prediction_frozen": admission["completeness"][
            "visible_non_fitting_prediction_frozen"
        ],
        "parent_freeze_gate_closed": round1["round1_verdict"]["freeze_gate_closed"],
        "pre_a_exit_conditions_met": round1["round1_verdict"][
            "pre_a_exit_conditions_met"
        ],
        "actual_freeze_ready": not blockers,
        "blockers": blockers,
    }


def _v13_fraction_text_independent(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _v13_order_independent(coefficients: tuple[Fraction, ...]) -> int:
    return next(index for index, coefficient in enumerate(coefficients) if coefficient)


def m2_v13_theorem_suite_independent() -> dict[str, Any]:
    """Reconstruct v1.3 with stdlib Fraction and coefficient identities only."""
    optimized_checks = []
    hessian_checks = []
    coefficient_fixtures = (
        (Fraction(-3), Fraction(2), Fraction(5), Fraction(7)),
        (Fraction(-5, 4), Fraction(11, 6), Fraction(3, 2), Fraction(13, 5)),
    )
    for signs in product((-1, 1), repeat=3):
        for r_value, c_value, q_value, g_value in coefficient_fixtures:
            optimum = -4 * r_value / (3 * g_value)
            density = optimum * r_value / 4 + 3 * g_value * optimum * optimum / 32
            optimized_checks.append(density == -r_value * r_value / (6 * g_value))
            for sign in signs:
                shear_quadratic_coefficient = 4 * sign * sign * q_value * q_value
                minimized_quadratic_coefficient = -(2 * r_value * c_value * shear_quadratic_coefficient) / (6 * g_value)
                hessian_coefficient = 2 * minimized_quadratic_coefficient
                hessian_checks.append(hessian_coefficient == -8 * r_value * c_value * q_value * q_value / (3 * g_value))
    base_laurent = {-1: Fraction(1, 2), 1: Fraction(1, 2)}
    cubic_laurent = {0: Fraction(1)}
    for _ in range(3):
        next_coefficients = {}
        for left_power, left_value in cubic_laurent.items():
            for right_power, right_value in base_laurent.items():
                power = left_power + right_power
                next_coefficients[power] = next_coefficients.get(power, Fraction(0)) + left_value * right_value
        cubic_laurent = next_coefficients
    expected_laurent = {-3: Fraction(1, 8), -1: Fraction(3, 8), 1: Fraction(3, 8), 3: Fraction(1, 8)}
    cubic_check = cubic_laurent == expected_laurent
    laurent_coefficients = {str(power): _v13_fraction_text_independent(cubic_laurent[power]) for power in (-3, -1, 1, 3)}
    inputs = {"r": Fraction(-3), "c": Fraction(2), "q": Fraction(5), "g": Fraction(7), "fundamental_reciprocal_step_h": Fraction(1)}
    amplitude_squared = -4 * inputs["r"] / (3 * inputs["g"])
    curvature = 2 * inputs["c"] * amplitude_squared * inputs["q"] ** 2
    h_value = inputs["fundamental_reciprocal_step_h"]
    shear_plus = (2 * inputs["q"] * h_value + h_value ** 2) ** 2
    shear_minus = (-2 * inputs["q"] * h_value + h_value ** 2) ** 2
    secant = inputs["c"] * amplitude_squared * (shear_plus + shear_minus) / (4 * h_value ** 2)
    correction = secant - curvature
    relative = correction / curvature
    x2 = (Fraction(0), Fraction(0), Fraction(1))
    x3 = (Fraction(0), Fraction(0), Fraction(0), Fraction(1))
    delta0 = tuple(Fraction(1, 10 * j) for j in range(1, 7))
    delta1 = tuple(Fraction(1, 10 * (j + 1)) for j in range(1, 7))
    floors0 = tuple(Fraction(j, 7) for j in range(1, 7))
    floors1 = tuple(Fraction(j + 1, 7) for j in range(1, 7))
    epsilon0 = tuple(delta * floor for delta, floor in zip(delta0, floors0))
    epsilon1 = tuple(delta * floor for delta, floor in zip(delta1, floors1))
    outputs0 = [Fraction(1)]
    outputs1 = [Fraction(1)]
    for floor in floors0: outputs0.append(outputs0[-1] * floor)
    for floor in floors1: outputs1.append(outputs1[-1] * floor)
    lower = Fraction(1)
    upper = Fraction(1)
    for left, right in zip(delta0, delta1):
        lower *= (1 - right) / (1 + left)
        upper *= (1 + right) / (1 - left)
    f = _v13_fraction_text_independent
    return {
        "schema": V13_SUITE_SCHEMA,
        "result": f"{RESULT_NUMBER} {RESULT_VERSION}",
        "exploration_id": EXPLORATION_ID,
        "claim_bearing": False,
        "tier": "T0",
        "closed_child_ids": list(NEW_CLOSED_SUBGATES),
        "negative_ids": list(NEW_NEGATIVE_IDS),
        "open_successor_gate_ids": list(OPEN_SUCCESSOR_GATES),
        "real_scalar_internal_u1_and_winding": {
            "closed_child_id": NEW_CLOSED_SUBGATES[0], "negative_id": NEW_NEGATIVE_IDS[0],
            "field_target": "R", "pointwise_linear_group": "GL(1,R)=R*", "orthogonal_corollary": "O(1)={-1,+1}",
            "theorem": "Every continuous real one-dimensional linear representation rho:U(1)->GL(1,R) is trivial: its image is compact and connected, lies in R_{>0}, and log sends it to a compact subgroup of (R,+), hence {0}. The O(1) statement is a corollary.",
            "configuration_space": "H^2(T^3;R)", "contraction": "C_s(phi)=(1-s)phi for 0<=s<=1",
            "intrinsic_winding_sectors": False,
            "scope_exclusions": ["spatial translation phase of a patterned state", "emergent complex amplitude or two-component reformulation", "defect-complement topology or an externally supplied compact field"],
        },
        "one_q_auxiliary_phason_curvature_and_finite_torus_secant": {
            "closed_child_id": NEW_CLOSED_SUBGATES[1], "negative_id": NEW_NEGATIVE_IDS[1],
            "sign_domain": "s in {-1,+1}^3", "trial_family": "phi=A*cos((q*s+a).x)",
            "density": "f=A^2*(r+c*S(a))/4+3*g*A^4/32", "shear_polynomial": "S(a)=sum_i(2*s_i*q*a_i+a_i^2)^2",
            "ordered_branch_condition": "r+c*S(a)<0 and g>0", "optimized_amplitude_squared": "-4*(r+c*S(a))/(3*g)",
            "optimized_density": "-(r+c*S(a))^2/(6*g)", "hessian_at_zero": "-8*r*c*q^2/(3*g)*I_3",
            "symbolic_all_eight_signs": all(hessian_checks), "symbolic_optimized_identity": all(optimized_checks),
            "finite_torus_rule": "At fixed L define the fundamental step h=2*pi/L, require q=m*h with integer m, and allow shifts only by integer multiples of h; use the fixed-amplitude central secant.",
            "fixed_amplitude_continuum_curvature": "2*c*A0^2*q^2",
            "fixed_amplitude_central_secant": "c*A0^2*(4*q^2+h^2)/2",
            "finite_torus_secant_excess": "c*A0^2*h^2/2",
            "relative_secant_correction": "h^2/(4*q^2)=1/(4*m^2) when q=m*h",
            "fraction_fixture": {"inputs": {key: f(value) for key, value in inputs.items()}, "optimized_amplitude_squared": f(amplitude_squared), "q_over_h_integer": int(inputs["q"] / inputs["fundamental_reciprocal_step_h"]), "continuum_curvature": f(curvature), "finite_torus_secant": f(secant), "secant_correction": f(correction), "relative_correction": f(relative)},
            "cubic_identity": "cos(theta)^3=(3*cos(theta)+cos(3*theta))/4", "cubic_laurent_coefficients": laurent_coefficients, "symbolic_cubic_identity": cubic_check,
            "euler_boundary": "For g*A!=0 the cubic Euler term generates a 3k harmonic; the one-Q family is a variational trial, not an exact Euler solution.",
            "physical_boundary": "This is auxiliary Bloch/supercell/thermodynamic phason elasticity, not an internal-U(1) helicity modulus or physical superfluid density.",
        },
        "helicity_tensor_contact_shift_nonidentifiability": {
            "closed_child_id": NEW_CLOSED_SUBGATES[2],
            "hamiltonian_family": "H(A)=H0-sum_i A_i*J_i+(1/2)*sum_ij A_i*T_ij*A_j",
            "hypotheses": ["finite regulator and finite volume", "norm-C2 self-adjoint family near A=0", "T_ij=T_ji self-adjoint", "finite beta, or an isolated simple ground state with positive gap"],
            "finite_beta_formula": "Upsilon_ij=V^-1*(<T_ij>_beta-integral_0^beta <delta J_i(-i tau) delta J_j>_beta d tau)",
            "isolated_ground_formula": "Upsilon_ij=V^-1*(<0|T_ij|0>-2*Re sum_{n>0} <0|J_i|n><n|J_j|0>/(E_n-E_0))",
            "symmetric_contact_shift": "T_ij -> T_ij+V*D_ij*I with D=D^T", "response_shift": "Upsilon -> Upsilon+D",
            "fixed_under_shift": ["H0", "J_i", "zero-source state", "zero-source spectrum"],
            "physical_boundary": "The formulas are a future finite-regulator contract; no Lane-Q compact action, background probe, state, or physical response is supplied.",
        },
        "analytic_map_integer_exponent_transport": {
            "closed_child_id": NEW_CLOSED_SUBGATES[3], "negative_id": NEW_NEGATIVE_IDS[2],
            "input_scaling": "kappa(tau)=C*tau*(1+o(1)) with C>0",
            "hypothesis": "R(0)=0 and R(kappa)=b_n*kappa^n+O(kappa^(n+1)), b_n>0, n>=1 the first nonzero analytic order",
            "transport": "R(kappa(tau))=b_n*C^n*tau^n*(1+o(1)); the transported exponent is the positive integer n.",
            "integer_order": True,
            "unit_order_sufficient_condition": "R is C1 (or analytic) through zero with R(0)=0 and R'(0)>0; then the inverse-function theorem gives n=1.",
            "positive_one_sided_local_invertibility_alone_sufficient": False,
            "hostile_polynomials": {"x_squared_coefficients": [f(v) for v in x2], "x_squared_order": _v13_order_independent(x2), "x_cubed_coefficients": [f(v) for v in x3], "x_cubed_order": _v13_order_independent(x3), "boundary": "x^2 is positive and invertible on [0,epsilon); x^3 is locally invertible through zero, yet their leading orders are 2 and 3."},
        },
        "six_stage_relative_log_slope_error_transport": {
            "closed_child_id": NEW_CLOSED_SUBGATES[4], "negative_id": NEW_NEGATIVE_IDS[3], "stage_count": len(delta0),
            "scale_domain": "lambda>0 and lambda!=1",
            "initial_stage_exact": True,
            "stage_ratio_definition": "g_j(s)=R_j(s)/R_(j-1)(s), ghat_j(s)=Rhat_j(s)/Rhat_(j-1)(s), j=1,...,6",
            "hypotheses": ["R_0,...,R_6 and Rhat_0,...,Rhat_6 are strictly positive at tau and lambda*tau, with Rhat_0=R_0.", "Each exact adjacent ratio g_j(s) has a positive floor m_j(s), and |ghat_j(s)-g_j(s)|<=epsilon_j(s).", "delta_j(s)=epsilon_j(s)/m_j(s)<1, hence |ghat_j(s)/g_j(s)-1|<=delta_j(s) and telescoping derives the final product."],
            "final_output_definition": "X(s)=R_6(s) and Xhat(s)=Rhat_6(s)",
            "log_slope_definition": "nu_lambda(tau)=log(X(lambda*tau)/X(tau))/log(lambda), with nuhat defined by Xhat",
            "ratio_envelope": "L=product_j[(1-delta_j(lambda*tau))/(1+delta_j(tau))] <= (Xhat(lambda*tau)/Xhat(tau))/(X(lambda*tau)/X(tau)) <= U=product_j[(1+delta_j(lambda*tau))/(1-delta_j(tau))]",
            "log_slope_bound": "|nuhat_lambda(tau)-nu_lambda(tau)| <= max(-log(L),log(U))/abs(log(lambda))",
            "exponent_transfer_condition": "For every stage j, delta_j(tau) and delta_j(lambda*tau) tend to zero.",
            "six_absolute_errors_alone_sufficient": False,
            "absolute_error_counterexample": "X(tau)=tau and Xhat(tau)=tau+epsilon have absolute error epsilon, but the dyadic log slope of Xhat tends to 0 while that of X is 1.",
            "fraction_fixture": {"lambda": "2", "positive_stage_outputs_tau": [f(v) for v in outputs0], "positive_stage_outputs_lambda_tau": [f(v) for v in outputs1], "adjacent_ratio_floors_tau": [f(v) for v in floors0], "adjacent_ratio_floors_lambda_tau": [f(v) for v in floors1], "adjacent_ratio_absolute_errors_tau": [f(v) for v in epsilon0], "adjacent_ratio_absolute_errors_lambda_tau": [f(v) for v in epsilon1], "delta_tau": [f(v) for v in delta0], "delta_lambda_tau": [f(v) for v in delta1], "lower_ratio": f(lower), "upper_ratio": f(upper), "all_stage_outputs_positive": all(v > 0 for v in (*outputs0, *outputs1)), "all_delta_strictly_below_one": all(0 <= v < 1 for v in (*delta0, *delta1))},
        },
        "scope": {"candidate_created": False, "physical_response_closed": False, "round1_freeze_closed": False, "pre_a_complete": False, "sector_a_complete": False, "checkpoint_synthesis": "PROOF-FIRST DEFERRED HISTORY; CURRENT COMBINED CHECKPOINT ISSUED"},
    }


def v13_suite_from_authority_independent(authority: dict[str, Any]) -> dict[str, Any]:
    identity = authority["m2_v1_3_identity_and_scope"]
    return {
        "schema": identity["schema"], "result": identity["result"], "exploration_id": identity["exploration_id"],
        "claim_bearing": identity["claim_bearing"], "tier": identity["tier"], "closed_child_ids": identity["closed_child_ids"],
        "negative_ids": identity["negative_ids"], "open_successor_gate_ids": identity["open_successor_gate_ids"],
        "real_scalar_internal_u1_and_winding": authority[V13_AUTHORITY_SECTION_KEYS[0]],
        "one_q_auxiliary_phason_curvature_and_finite_torus_secant": authority[V13_AUTHORITY_SECTION_KEYS[1]],
        "helicity_tensor_contact_shift_nonidentifiability": authority[V13_AUTHORITY_SECTION_KEYS[2]],
        "analytic_map_integer_exponent_transport": authority[V13_AUTHORITY_SECTION_KEYS[3]],
        "six_stage_relative_log_slope_error_transport": authority[V13_AUTHORITY_SECTION_KEYS[4]], "scope": identity["scope"],
    }


def validate_m2_v13_theorem_suite_independent(candidate: Any) -> dict[str, Any]:
    if not isinstance(candidate, dict) or tuple(candidate) != V13_SUITE_FIELDS:
        return {"valid": False, "error_codes": ["V13_ROOT_FIELDS_INVALID"]}
    expected = m2_v13_theorem_suite_independent()
    errors = []
    checks = (
        (("schema", "result", "exploration_id", "claim_bearing", "tier", "closed_child_ids", "negative_ids", "open_successor_gate_ids"), "V13_IDENTITY_INVALID"),
        (("real_scalar_internal_u1_and_winding",), "V13_U1_SCOPE_INVALID"),
        (("one_q_auxiliary_phason_curvature_and_finite_torus_secant",), "V13_PHASON_ALGEBRA_INVALID"),
        (("helicity_tensor_contact_shift_nonidentifiability",), "V13_RESPONSE_ALGEBRA_INVALID"),
        (("analytic_map_integer_exponent_transport",), "V13_MAP_ALGEBRA_INVALID"),
        (("six_stage_relative_log_slope_error_transport",), "V13_ERROR_ALGEBRA_INVALID"),
        (("scope",), "V13_GLOBAL_SCOPE_INVALID"),
    )
    for keys, code in checks:
        if any(candidate.get(key) != expected[key] for key in keys): errors.append(code)
    return {"valid": not errors, "error_codes": sorted(set(errors))}


def m2_v13_hostiles_independent(valid: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases = (
        ("nontrivial_real_line_u1", lambda x: x["real_scalar_internal_u1_and_winding"].__setitem__("theorem", "nontrivial")),
        ("intrinsic_real_h2_winding", lambda x: x["real_scalar_internal_u1_and_winding"].__setitem__("intrinsic_winding_sectors", True)),
        ("spatial_translation_promoted_internal", lambda x: x["real_scalar_internal_u1_and_winding"].__setitem__("scope_exclusions", [])),
        ("phason_promoted_physical_density", lambda x: x["one_q_auxiliary_phason_curvature_and_finite_torus_secant"].__setitem__("physical_boundary", "physical")),
        ("phason_hessian_sign_flip", lambda x: x["one_q_auxiliary_phason_curvature_and_finite_torus_secant"].__setitem__("hessian_at_zero", "wrong")),
        ("fixed_torus_continuous_twist", lambda x: x["one_q_auxiliary_phason_curvature_and_finite_torus_secant"].__setitem__("finite_torus_rule", "continuous")),
        ("optimized_amplitude_torus_secant", lambda x: x["one_q_auxiliary_phason_curvature_and_finite_torus_secant"].__setitem__("fixed_amplitude_central_secant", "optimized")),
        ("one_q_promoted_exact_euler_solution", lambda x: x["one_q_auxiliary_phason_curvature_and_finite_torus_secant"].__setitem__("euler_boundary", "exact")),
        ("cubic_third_harmonic_removed", lambda x: x["one_q_auxiliary_phason_curvature_and_finite_torus_secant"].__setitem__("cubic_identity", "fundamental only")),
        ("contact_shift_nonsymmetric", lambda x: x["helicity_tensor_contact_shift_nonidentifiability"].__setitem__("symmetric_contact_shift", "arbitrary")),
        ("contact_shift_sign_flip", lambda x: x["helicity_tensor_contact_shift_nonidentifiability"].__setitem__("response_shift", "minus")),
        ("finite_beta_contact_omitted", lambda x: x["helicity_tensor_contact_shift_nonidentifiability"].__setitem__("finite_beta_formula", "current only")),
        ("ground_gap_hypothesis_removed", lambda x: x["helicity_tensor_contact_shift_nonidentifiability"].__setitem__("hypotheses", x["helicity_tensor_contact_shift_nonidentifiability"]["hypotheses"][:-1])),
        ("positive_invertibility_forces_unit_order", lambda x: x["analytic_map_integer_exponent_transport"].__setitem__("positive_one_sided_local_invertibility_alone_sufficient", True)),
        ("x2_order_changed", lambda x: x["analytic_map_integer_exponent_transport"]["hostile_polynomials"].__setitem__("x_squared_order", 1)),
        ("x3_order_changed", lambda x: x["analytic_map_integer_exponent_transport"]["hostile_polynomials"].__setitem__("x_cubed_order", 1)),
        ("six_absolute_errors_promoted", lambda x: x["six_stage_relative_log_slope_error_transport"].__setitem__("six_absolute_errors_alone_sufficient", True)),
        ("delta_equal_one", lambda x: x["six_stage_relative_log_slope_error_transport"]["fraction_fixture"]["delta_tau"].__setitem__(0, "1")),
        ("positive_floor_removed", lambda x: x["six_stage_relative_log_slope_error_transport"].__setitem__("hypotheses", x["six_stage_relative_log_slope_error_transport"]["hypotheses"][1:])),
        ("vanishing_delta_not_required", lambda x: x["six_stage_relative_log_slope_error_transport"].__setitem__("exponent_transfer_condition", "fixed")),
        ("candidate_or_parent_promoted", lambda x: x["scope"].__setitem__("candidate_created", True)),
        ("gl1_compact_connected_argument_removed", lambda x: x["real_scalar_internal_u1_and_winding"].__setitem__("theorem", "orthogonal case only")),
        ("branch_amplitude_decoupled", lambda x: x["one_q_auxiliary_phason_curvature_and_finite_torus_secant"]["fraction_fixture"].__setitem__("optimized_amplitude_squared", "1/2")),
        ("analytic_zero_value_removed", lambda x: x["analytic_map_integer_exponent_transport"].__setitem__("hypothesis", "nonzero constant term allowed")),
        ("lambda_equal_one", lambda x: x["six_stage_relative_log_slope_error_transport"].__setitem__("scale_domain", "lambda=1")),
        ("initial_stage_unbound", lambda x: x["six_stage_relative_log_slope_error_transport"].__setitem__("initial_stage_exact", False)),
        ("adjacent_ratio_contract_removed", lambda x: x["six_stage_relative_log_slope_error_transport"].__setitem__("stage_ratio_definition", "final factorization assumed")),
    )
    reports = {}
    for name, mutation in cases:
        hostile = copy.deepcopy(valid); mutation(hostile)
        try:
            report = validate_m2_v13_theorem_suite_independent(hostile); expected = V13_HOSTILE_CODES[name]
            reports[name] = {"valid": report["valid"], "error_codes": report["error_codes"], "expected_error_code": expected, "expected_code_observed": expected in report["error_codes"]}
        except Exception as exc:
            reports[name] = {"valid": True, "exception": type(exc).__name__, "expected_error_code": V13_HOSTILE_CODES[name], "expected_code_observed": False}
    return reports


def section_for(text: str, identifier: str) -> str:
    marker = f"### **{identifier}**"
    start = text.find(marker)
    if start < 0:
        return ""
    end = text.find("\n### **", start + len(marker))
    return text[start:] if end < 0 else text[start:end]


def exploration_record(identifier: str) -> dict[str, Any] | None:
    if not EXPLORATION_LOG.is_file():
        return None
    for line in EXPLORATION_LOG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("id") == identifier:
            return row
    return None


def formal_authority_audit(audit: Audit, *, staged: bool) -> dict[str, Any]:
    missing = []
    gates = (REPO / "claims/GATES.md").read_text(encoding="utf-8")
    for identifier in NEW_CLOSED_SUBGATES:
        section = section_for(gates, identifier)
        if not section: missing.append(f"claims/GATES.md#{identifier}")
        else: audit.check(f"v1.3 closed gate {identifier}", "**Status:** CLOSED" in section, "CLOSED" if "**Status:** CLOSED" in section else section[:160], "CLOSED", "formal_authority")
    for identifier in OPEN_SUCCESSOR_GATES:
        section = section_for(gates, identifier)
        if not section: missing.append(f"claims/GATES.md#{identifier}")
        else: audit.check(f"v1.3 successor gate {identifier} open", "**Status:** OPEN" in section, "OPEN" if "**Status:** OPEN" in section else section[:160], "OPEN", "formal_authority")
    physical = section_for(gates, PHYSICAL_RESPONSE_GATE)
    audit.check("retained physical response gate open", bool(physical) and "**Status:** OPEN" in physical, "OPEN" if physical and "**Status:** OPEN" in physical else physical[:160], "OPEN", "formal_authority")
    for identifier in (LINEAR_PROBE_CLOSED_CHILD, PHYSICAL_CONTRACT_CLOSED_CHILD):
        retained = section_for(gates, identifier)
        audit.check(f"retained v1.2 closed gate {identifier}", bool(retained) and "**Status:** CLOSED" in retained, "CLOSED" if retained and "**Status:** CLOSED" in retained else retained[:160], "CLOSED", "formal_authority")

    negatives = NEGATIVE_REGISTRY.read_text(encoding="utf-8")
    audit.check("retained v1.2 negative", LINEAR_PROBE_NEGATIVE_ID in negatives, LINEAR_PROBE_NEGATIVE_ID in negatives, True, "formal_authority")
    for identifier in NEW_NEGATIVE_IDS:
        if identifier not in negatives: missing.append(f"negative-results/registry.md#{identifier}")
        else: audit.check(f"v1.3 negative {identifier}", negatives.count(identifier) >= 1, negatives.count(identifier), ">=1", "formal_authority")
    results = RESULTS_LEDGER.read_text(encoding="utf-8")
    audit.check("retained R-168 v1.2", "R-168 v1.2" in results and RESULT_ID in results, "R-168 v1.2" in results and RESULT_ID in results, True, "formal_authority")
    if f"{RESULT_NUMBER} {RESULT_VERSION}" not in results or RESULT_ID not in results: missing.append(f"RESULTS-LEDGER.md#{RESULT_NUMBER}-{RESULT_VERSION}")
    else: audit.check("v1.3 result authority", True, True, True, "formal_authority")
    retained = exploration_record("EXP-000812")
    audit.check("retained EXP-000812", retained is not None, retained is not None, True, "formal_authority")
    exploration = exploration_record(EXPLORATION_ID)
    if exploration is None: missing.append(f"explorations/log.jsonl#{EXPLORATION_ID}")
    else:
        audit.check("v1.3 exploration result", RESULT_NUMBER in exploration.get("formal_refs", {}).get("results", []), exploration.get("formal_refs", {}).get("results", []), RESULT_NUMBER, "formal_authority")
        audit.check("v1.3 exploration negatives", set(NEW_NEGATIVE_IDS) <= set(exploration.get("formal_refs", {}).get("negatives", [])), exploration.get("formal_refs", {}).get("negatives", []), list(NEW_NEGATIVE_IDS), "formal_authority")
        required = set(NEW_CLOSED_SUBGATES + OPEN_SUCCESSOR_GATES + (PARENT_GATE, PHYSICAL_RESPONSE_GATE))
        audit.check("v1.3 exploration gates", required <= set(exploration.get("gate_ids", [])), exploration.get("gate_ids", []), sorted(required), "formal_authority")
    for identifier in PRIOR_EXPLORATION_IDS[:-1]:
        row = exploration_record(identifier); audit.check(f"retained {identifier}", row is not None, row is not None, True, "formal_authority")
    return {"status": "COMPLETE" if not missing else ("STAGED" if staged else "INCOMPLETE"), "missing": missing, "staged": staged}


def validate_requested_freeze(
    freeze_path: Path | None, *, staged: bool
) -> dict[str, Any]:
    if freeze_path is None:
        return {
            "status": "ABSENT_BY_DESIGN",
            "path": None,
            "valid": False,
            "error_codes": ["EXTERNAL_VERIFICATION_REQUIRED"],
        }
    path = freeze_path if freeze_path.is_absolute() else REPO / freeze_path
    if not path.is_file():
        if staged:
            return {
                "status": "MISSING_STAGED",
                "path": str(freeze_path),
                "valid": False,
                "error_codes": ["EXTERNAL_VERIFICATION_REQUIRED"],
            }
        raise FileNotFoundError(path)
    report = validate_schema_shape(load_json(path), synthetic_fixture_mode=False)
    if "EXTERNAL_VERIFICATION_REQUIRED" not in report["error_codes"]:
        raise AssertionError("purported real freeze escaped the external-verification gate")
    return {
        "status": "REJECTED_FAIL_CLOSED",
        "path": repo_path(path),
        "sha256": normalized_sha256(path),
        "valid": False,
        "error_codes": report["error_codes"],
        "report": report,
    }


def build_payload(
    freeze_path: Path | None = None, *, staged: bool = False
) -> dict[str, Any]:
    audit = Audit()
    authority = load_json(AUTHORITY_MANIFEST)
    certificate = AUTHORITY_CERTIFICATE.read_text(encoding="utf-8")

    source = SCRIPT.read_text(encoding="utf-8")
    syntax = ast.parse(source)
    imported_roots: set[str] = set()
    for node in ast.walk(syntax):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])
    allowed_imports = {
        "__future__",
        "argparse",
        "ast",
        "copy",
        "hashlib",
        "json",
        "os",
        "re",
        "subprocess",
        "tempfile",
        "datetime",
        "fractions",
        "itertools",
        "pathlib",
        "typing",
        "urllib",
    }
    audit.check(
        "stdlib-only independent imports",
        imported_roots <= allowed_imports,
        sorted(imported_roots),
        sorted(allowed_imports),
        "independence",
    )
    audit.check(
        "no primary module import",
        not any(root.endswith("prospective_holdout_freeze_protocol") for root in imported_roots),
        sorted(imported_roots),
        "no primary verifier module",
        "independence",
    )

    audit.check("authority schema", authority.get("schema") == "tect/pre-a-route-split/1.0", authority.get("schema"), "tect/pre-a-route-split/1.0", "identity")
    audit.check("result ID", authority.get("result_id") == RESULT_ID, authority.get("result_id"), RESULT_ID, "identity")
    audit.check("result number", authority.get("result_number") == RESULT_NUMBER, authority.get("result_number"), RESULT_NUMBER, "identity")
    audit.check("result version", authority.get("result_version") == RESULT_VERSION, authority.get("result_version"), RESULT_VERSION, "identity")
    audit.check("exploration ID", authority.get("exploration_id") == EXPLORATION_ID, authority.get("exploration_id"), EXPLORATION_ID, "identity")
    audit.check("retained exploration IDs", tuple(authority.get("prior_exploration_ids", [])) == PRIOR_EXPLORATION_IDS, authority.get("prior_exploration_ids"), list(PRIOR_EXPLORATION_IDS), "identity")
    audit.check("task ID", authority.get("task_id") == TASK_ID, authority.get("task_id"), TASK_ID, "identity")
    audit.check("claim context", tuple(authority.get("claim_ids", [])) == CLAIM_IDS, authority.get("claim_ids"), list(CLAIM_IDS), "identity")
    audit.check("claim nonbearing", authority.get("claim_bearing") is False, authority.get("claim_bearing"), False, "scope")
    audit.check("negative IDs exact", tuple(authority.get("negative_ids", [])) == NEGATIVE_IDS, authority.get("negative_ids"), list(NEGATIVE_IDS), "identity")
    audit.check("new negative IDs exact", tuple(authority.get("new_negative_ids", [])) == NEW_NEGATIVE_IDS, authority.get("new_negative_ids"), list(NEW_NEGATIVE_IDS), "identity")
    audit.check("reused negative IDs exact", tuple(authority.get("reused_negative_ids", [])) == REUSED_NEGATIVE_IDS, authority.get("reused_negative_ids"), list(REUSED_NEGATIVE_IDS), "identity")
    audit.check("closed subgates exact", tuple(authority.get("closed_subgates", [])) == CLOSED_SUBGATES, authority.get("closed_subgates"), list(CLOSED_SUBGATES), "identity")
    audit.check("open gates exact", tuple(authority.get("open_gates", [])) == OPEN_GATES, authority.get("open_gates"), list(OPEN_GATES), "identity")
    audit.check("authority audited commit", authority["audited_checkpoint"]["commit"] == AUDITED_COMMIT, authority["audited_checkpoint"]["commit"], AUDITED_COMMIT, "identity")
    audit.check("freeze schema exact", authority["freeze_schema"]["schema"] == FREEZE_SCHEMA, authority["freeze_schema"]["schema"], FREEZE_SCHEMA, "schema")
    audit.check("root-field contract exact", tuple(authority["freeze_schema"]["root_fields"]) == ROOT_FIELDS, authority["freeze_schema"]["root_fields"], list(ROOT_FIELDS), "schema")
    audit.check("target-field contract exact", tuple(authority["freeze_schema"]["target_fields"]) == TARGET_FIELDS, authority["freeze_schema"]["target_fields"], list(TARGET_FIELDS), "schema")
    audit.check("commitment-field contract exact", tuple(authority["freeze_schema"]["commitment_fields"]) == COMMITMENT_FIELDS, authority["freeze_schema"]["commitment_fields"], list(COMMITMENT_FIELDS), "schema")
    audit.check("disclosure-field contract exact", tuple(authority["freeze_schema"]["disclosure_fields"]) == DISCLOSURE_FIELDS, authority["freeze_schema"]["disclosure_fields"], list(DISCLOSURE_FIELDS), "schema")
    audit.check("prediction-field contract exact", tuple(authority["freeze_schema"]["prediction_fields"]) == PREDICTION_FIELDS, authority["freeze_schema"]["prediction_fields"], list(PREDICTION_FIELDS), "schema")
    audit.check("allowed-input contract exact", tuple(authority["freeze_schema"]["allowed_input_fields"]) == ALLOWED_INPUT_FIELDS, authority["freeze_schema"]["allowed_input_fields"], list(ALLOWED_INPUT_FIELDS), "schema")
    audit.check("robustness-field contract exact", tuple(authority["freeze_schema"]["robustness_fields"]) == ROBUSTNESS_FIELDS, authority["freeze_schema"]["robustness_fields"], list(ROBUSTNESS_FIELDS), "schema")
    audit.check("independent path binding", authority["verification"]["independent_script"] == repo_path(SCRIPT), authority["verification"]["independent_script"], repo_path(SCRIPT), "identity")
    audit.check("external gate binding", authority["route_status"]["external_gate"] == OPEN_GATES[2], authority["route_status"]["external_gate"], OPEN_GATES[2], "identity")
    audit.check("internal gate binding", authority["route_status"]["internal_gate"] == OPEN_GATES[3], authority["route_status"]["internal_gate"], OPEN_GATES[3], "identity")
    audit.check("verification gate binding", authority["route_status"]["verification_gate"] == OPEN_GATES[4], authority["route_status"]["verification_gate"], OPEN_GATES[4], "identity")

    certificate_flat = " ".join(certificate.replace("`", "").split())
    for token in (RESULT_NUMBER, RESULT_VERSION, RESULT_ID, EXPLORATION_ID, *PRIOR_EXPLORATION_IDS, *NEGATIVE_IDS, *CLOSED_SUBGATES, *OPEN_GATES, M2_SUCCESSOR_ID):
        audit.check(f"certificate token {token}", token in certificate, token in certificate, True, "certificate")
    audit.check("certificate root fields", ", ".join(ROOT_FIELDS) in certificate_flat, ", ".join(ROOT_FIELDS) in certificate_flat, True, "certificate")
    certificate_shape_boundary = (
        "does not verify a custodian signature" in certificate_flat
        and "does not fetch the remote commit" in certificate_flat
    )
    audit.check(
        "certificate shape-only boundary",
        certificate_shape_boundary,
        certificate_shape_boundary,
        True,
        "certificate",
    )
    audit.check("certificate no real tag", "R-168 creates no tag" in certificate, "R-168 creates no tag" in certificate, True, "certificate")
    audit.check("certificate no physical closure", "physical Sector A or Pre-A" in certificate, "physical Sector A or Pre-A" in certificate, True, "certificate")
    audit.check("certificate v1.3 devil review independent", "## 28. V1.3 devil's-advocate review" in certificate and all(token in certificate for token in ("Sign and factor objection", "Units objection", "Convergence objection", "Hardcode-masking objection", "Limit-case objection", "Physical-promotion objection", "UPHELD", "VALID with mitigation", "DISMISSED")), True, True, "certificate")

    state = reconstruct_checkpoint()
    checkpoint = authority["audited_checkpoint"]
    map_only = current_version_map_audit_independent()
    map_only_survival = map_only["survival_contract"]
    map_only_survival_report = validate_survival_contract_independent(map_only_survival)
    map_only_survival_hostile = survival_hostiles_independent(map_only_survival)
    fingerprint = fingerprint_integer_engine()
    response_countermodels = response_countermodels_independent()
    successor_design = authority["m2_v1_successor_design"]
    successor_report = validate_successor_design_independent(successor_design)
    successor_hostile = successor_hostiles_independent(successor_design)
    linear_probe = linear_probe_curvature_nonidentifiability_independent()
    physical_contract_fixture = synthetic_physical_response_contract_independent()
    physical_contract_report = validate_physical_response_contract_independent(
        physical_contract_fixture
    )
    physical_contract_hostile = physical_response_contract_hostiles_independent(
        physical_contract_fixture
    )
    physical_contract_reordered = physical_response_contract_reordered_metamorphic_independent(
        physical_contract_fixture
    )
    physical_contract_fuzz = physical_response_contract_fuzz_reports_independent(
        physical_contract_fixture
    )
    v13_suite = m2_v13_theorem_suite_independent()
    v13_report = validate_m2_v13_theorem_suite_independent(v13_suite)
    authority_v13_suite = v13_suite_from_authority_independent(authority)
    authority_v13_report = validate_m2_v13_theorem_suite_independent(authority_v13_suite)
    v13_hostile = m2_v13_hostiles_independent(v13_suite)
    audit.check("audited commit ancestor", state["audited_commit_is_ancestor"], state["current_head"], f"descendant of {AUDITED_COMMIT}", "current_tree")
    audit.check("official freeze records zero", state["freeze_record_count"] == checkpoint["freeze_records"] == 0, state["freeze_record_count"], 0, "current_tree")
    audit.check("live freeze-tag observation non-load-bearing", state["local_freeze_tag_observation"]["load_bearing"] is authority["initial_local_observation"]["load_bearing"] is False, state["local_freeze_tag_observation"], "informational only", "current_tree")
    audit.check("admitted survivors zero", state["admitted_microscopic_survivor_count"] == checkpoint["admitted_microscopic_survivors"] == 0, state["admitted_microscopic_survivor_count"], 0, "current_tree")
    audit.check("contestant sequence exact", tuple(state["contestant_ids"]) == EXPECTED_CANDIDATES, state["contestant_ids"], list(EXPECTED_CANDIDATES), "current_tree")
    audit.check("M1 map absent", state["M1"]["microscopic_map"] is checkpoint["M1"]["microscopic_map"] is False, state["M1"], checkpoint["M1"], "current_tree")
    audit.check("M1 prediction absent", state["M1"]["non_fitting_validation_prediction"] is checkpoint["M1"]["non_fitting_validation_prediction"] is False, state["M1"], checkpoint["M1"], "current_tree")
    audit.check("M2 predictions empty", state["M2"]["physical_predictions"] == checkpoint["M2"]["physical_predictions"] == [], state["M2"], checkpoint["M2"], "current_tree")
    audit.check("M2 holdout absent", state["M2"]["holdout_prediction"] is checkpoint["M2"]["holdout_prediction"] is False, state["M2"], checkpoint["M2"], "current_tree")
    audit.check("M5 map absent", state["M5"]["microscopic_map"] is checkpoint["M5"]["microscopic_map"] is False, state["M5"], checkpoint["M5"], "current_tree")
    audit.check("M5 holdout absent", state["M5"]["holdout_prediction"] is checkpoint["M5"]["holdout_prediction"] is False, state["M5"], checkpoint["M5"], "current_tree")
    audit.check("M1 normalized map absent", state["normalized_map_status"][MICROSCOPIC_CANDIDATES[0]] == "ABSENT", state["normalized_map_status"][MICROSCOPIC_CANDIDATES[0]], "ABSENT", "current_tree")
    audit.check("M2 normalized map absent", state["normalized_map_status"][MICROSCOPIC_CANDIDATES[1]].startswith("ABSENT;"), state["normalized_map_status"][MICROSCOPIC_CANDIDATES[1]], "ABSENT; ...", "current_tree")
    audit.check("M5 normalized map absent", state["normalized_map_status"][MICROSCOPIC_CANDIDATES[2]] == "ABSENT", state["normalized_map_status"][MICROSCOPIC_CANDIDATES[2]], "ABSENT", "current_tree")
    audit.check("common input ledger incomplete", state["per_parameter_common_input_ledger_complete"] is False, state["per_parameter_common_input_ledger_complete"], False, "current_tree")
    audit.check("prospective prediction absent", state["prospective_prediction_frozen"] is False, state["prospective_prediction_frozen"], False, "current_tree")
    audit.check("parent gate open", state["parent_freeze_gate_closed"] is False, state["parent_freeze_gate_closed"], False, "scope")
    audit.check("Pre-A exit open", state["pre_a_exit_conditions_met"] is False, state["pre_a_exit_conditions_met"], False, "scope")
    audit.check("current tree not freeze ready", state["actual_freeze_ready"] is False, state["actual_freeze_ready"], False, "scope")
    audit.check("blocker set exact and ordered", tuple(state["blockers"]) == EXPECTED_BLOCKERS, state["blockers"], list(EXPECTED_BLOCKERS), "current_tree")
    audit.check("map-only set independently empty", map_only["admitted_candidate_ids"] == [] and map_only["cardinality"] == 0, map_only["admitted_candidate_ids"], [], "map_only")
    audit.check("map-only pins independently match", all(row["pin_matches"] for row in map_only["rows"]), [row["pin_matches"] for row in map_only["rows"]], [True, True, True], "map_only")
    audit.check("map-only exact row count", len(map_only["rows"]) == 3, len(map_only["rows"]), 3, "map_only")
    audit.check("same-version repair independently rejected", map_only["same_version_repair_possible"] is False and map_only["negative_id"] == MAP_ONLY_NEGATIVE_ID, map_only, "new version required", "map_only")
    audit.check("independent all-PASS contract valid", map_only_survival_report["valid"], map_only_survival_report, "valid", "map_only")
    audit.check("independent frozen survival rule exact", map_only_survival["survives_if"] == "Every hard row is PASS." and map_only_survival["hard_rows"] == load_json(ROUND1_MANIFEST)["survival_rule"]["hard_rows"], map_only_survival["survives_if"], "Every hard row is PASS.", "map_only")
    audit.check("independent residual blockers exact", map_only_survival["residual_hard_rows"] == MAP_ONLY_RESIDUAL_ORACLE, map_only_survival["residual_hard_rows"], MAP_ONLY_RESIDUAL_ORACLE, "map_only")
    audit.check("independent map-only survivor set empty", map_only["map_only_new_version_all_pass_repair_possible"] is False and map_only_survival["map_only_survivor_ids"] == [] and map_only_survival["all_pass_after_map_only"] is False, map_only_survival, "empty", "map_only")
    audit.check("independent substantive repair boundary", map_only_survival["substantive_new_version_requirements"] == {key: list(value) for key, value in MAP_ONLY_SUBSTANTIVE_REQUIREMENTS.items()}, map_only_survival["substantive_new_version_requirements"], MAP_ONLY_SUBSTANTIVE_REQUIREMENTS, "map_only")
    audit.check("integer fingerprint dimensions", [fingerprint["node_count"], fingerprint["node_axis_record_count"], fingerprint["ordered_component_count"]] == [8, 24, 48], [fingerprint["node_count"], fingerprint["node_axis_record_count"], fingerprint["ordered_component_count"]], [8, 24, 48], "fingerprint")
    audit.check("integer fingerprint all ones", fingerprint["all_components_exactly_one"] and fingerprint["component_vector"] == ["1"] * 48, fingerprint["component_vector"], ["1"] * 48, "fingerprint")
    for mode_index in (1, 2, 4, 7):
        mode_fingerprint = fingerprint_integer_engine(mode_index)
        audit.check(f"integer fingerprint m={mode_index}", mode_fingerprint["all_components_exactly_one"] and mode_fingerprint["ordered_component_count"] == 48, [mode_fingerprint["all_components_exactly_one"], mode_fingerprint["ordered_component_count"]], [True, 48], "fingerprint")
    audit.check("response countermodels differ", response_countermodels["identity_response_ratio"] == 2 and response_countermodels["square_response_ratio"] == 4 and response_countermodels["exponents"] == [1, 2], response_countermodels, "2 versus 4 / exponents 1 versus 2", "underdetermination")
    audit.check("response countermodels create no map", response_countermodels["admitted_map_created"] is False and response_countermodels["validation_credit"] is False, response_countermodels, "no map or credit", "underdetermination")
    audit.check("successor design independently valid", successor_report["valid"], successor_report, "valid DESIGN_ONLY schema", "successor")
    audit.check("successor ID and status exact", successor_design["hypothetical_candidate_id"] == M2_SUCCESSOR_ID and successor_design["status"] == "DESIGN_ONLY", [successor_design["hypothetical_candidate_id"], successor_design["status"]], [M2_SUCCESSOR_ID, "DESIGN_ONLY"], "successor")
    audit.check("independent linear-probe sign convention", linear_probe["sign_convention"]["contract_literal"] == HELICITY_SIGN_CONVENTION, linear_probe["sign_convention"], HELICITY_SIGN_CONVENTION, "linear_probe")
    audit.check("independent finite-beta contact factor", linear_probe["finite_beta"]["free_energy_difference_at_step"] == "3/25" and linear_probe["finite_beta"]["boltzmann_exponent_shift_at_step"] == "-9/50", linear_probe["finite_beta"], ["3/25", "-9/50"], "linear_probe")
    audit.check("independent finite-beta curvature shift", linear_probe["finite_beta"]["normalized_curvature_shift"] == linear_probe["finite_beta"]["expected_shift"] == "6/7", linear_probe["finite_beta"], "6/7", "linear_probe")
    audit.check("independent ground branch stable", linear_probe["beta_infinity"]["branch_stable"] and linear_probe["beta_infinity"]["ground_branch_indices_minus_zero_plus"] == [0, 0, 0], linear_probe["beta_infinity"], [0, 0, 0], "linear_probe")
    audit.check("independent ground curvatures", [linear_probe["beta_infinity"]["normalized_curvature_left"], linear_probe["beta_infinity"]["normalized_curvature_right"], linear_probe["beta_infinity"]["normalized_curvature_shift"]] == ["5/7", "11/7", "6/7"], linear_probe["beta_infinity"], ["5/7", "11/7", "6/7"], "linear_probe")
    audit.check("independent fixed zero/first source data", linear_probe["invariants"]["same_zero_source_hamiltonian"] and linear_probe["invariants"]["same_first_source_derivative"] and linear_probe["invariants"]["physical_response_identified"] is False, linear_probe["invariants"], "fixed data and no physical response", "linear_probe")
    audit.check("independent minimum contract valid", physical_contract_report["valid"], physical_contract_report, "valid schema fixture", "physical_contract")
    audit.check("independent contract fixture-only", physical_contract_fixture["fixture_only"] is True and physical_contract_fixture["candidate_created"] is False, [physical_contract_fixture["fixture_only"], physical_contract_fixture["candidate_created"]], [True, False], "physical_contract")
    audit.check("independent error sum strict", physical_contract_fixture["error_budget"]["total_bound"] == "3/50" and physical_contract_fixture["error_budget"]["acceptance_margin"] == "1/10" and physical_contract_fixture["error_budget"]["strict_margin"] is True, physical_contract_fixture["error_budget"], "3/50 < 1/10", "physical_contract")
    audit.check("independent ten PASS fixture rows", len(physical_contract_fixture["hard_row_rerun"]["rows"]) == len(HARD_ROWS) and set(physical_contract_fixture["hard_row_rerun"]["rows"]) == set(HARD_ROWS) and all(value == "PASS" for value in physical_contract_fixture["hard_row_rerun"]["rows"].values()), physical_contract_fixture["hard_row_rerun"], "exact ten PASS rows", "physical_contract")
    audit.check("independent reordered positive metamorphic", physical_contract_reordered["valid"], physical_contract_reordered, "valid after order-insensitive reordering", "physical_contract")
    audit.check("independent deterministic fuzz fail closed", physical_contract_fuzz["all_rejected_without_exception"] and physical_contract_fuzz["case_count"] >= 20, physical_contract_fuzz, "all malformed cases rejected without exception", "physical_contract")

    authority_linear = authority["m2_linear_probe_second_order_response_nonidentifiability"]
    audit.check("authority linear-probe child independent", authority_linear["closed_child_id"] == LINEAR_PROBE_CLOSED_CHILD and authority_linear["negative_id"] == LINEAR_PROBE_NEGATIVE_ID and authority_linear["fraction_fixture"]["normalized_curvature_shift"] == "6/7", authority_linear, [LINEAR_PROBE_CLOSED_CHILD, LINEAR_PROBE_NEGATIVE_ID, "6/7"], "authority")
    authority_contract = authority["m2_physical_response_successor_minimum_contract_schema"]
    audit.check("authority minimum contract independent", authority_contract["closed_child_id"] == PHYSICAL_CONTRACT_CLOSED_CHILD and authority_contract["schema"] == PHYSICAL_CONTRACT_SCHEMA and tuple(authority_contract["root_fields"]) == PHYSICAL_CONTRACT_FIELDS and tuple(authority_contract["artifact_ref_fields"]) == ARTIFACT_REF_FIELDS, authority_contract, PHYSICAL_CONTRACT_SCHEMA, "authority")
    audit.check("authority contract terms/rows independent", tuple(authority_contract["error_terms"]) == EXPECTED_ERROR_TERMS and tuple(authority_contract["hard_rows"]) == HARD_ROWS and tuple(authority_contract["mandatory_substantive_changes"]) == MANDATORY_SUBSTANTIVE_CHANGES, authority_contract, [EXPECTED_ERROR_TERMS, HARD_ROWS], "authority")
    audit.check("authority boundary layers independent", authority_contract["validation_boundary"]["syntax_and_binding"] == "VALIDATED" and authority_contract["validation_boundary"]["physical_semantics"] == "NOT_VALIDATED" and authority_contract["validation_boundary"]["external_prospective_freeze"] == "NOT_SUPPLIED", authority_contract["validation_boundary"], "syntax only; semantics/external open", "authority")

    fixture = synthetic_fixture()
    fixture_report = validate_schema_shape(fixture, synthetic_fixture_mode=True)
    non_string_root_fixture = copy.deepcopy(fixture)
    non_string_root_fixture[1] = "unexpected"
    non_string_root_report = validate_schema_shape(
        non_string_root_fixture, synthetic_fixture_mode=True
    )
    audit.check(
        "independent non-string freeze root key rejected without exception",
        non_string_root_report["valid"] is False
        and "ROOT_FIELDS_EXTRA" in non_string_root_report["error_codes"],
        non_string_root_report,
        "structured ROOT_FIELDS_EXTRA rejection",
        "schema",
    )
    audit.check("synthetic fixture root order", tuple(fixture) == ROOT_FIELDS, list(fixture), list(ROOT_FIELDS), "schema")
    audit.check("synthetic target order", tuple(fixture["target_contract"]) == TARGET_FIELDS, list(fixture["target_contract"]), list(TARGET_FIELDS), "schema")
    audit.check("synthetic commitment order", tuple(fixture["target_contract"]["commitment"]) == COMMITMENT_FIELDS, list(fixture["target_contract"]["commitment"]), list(COMMITMENT_FIELDS), "schema")
    audit.check("synthetic disclosure order", tuple(fixture["target_contract"]["disclosure"]) == DISCLOSURE_FIELDS, list(fixture["target_contract"]["disclosure"]), list(DISCLOSURE_FIELDS), "schema")
    audit.check("synthetic prediction order", tuple(fixture["prediction_contract"]) == PREDICTION_FIELDS, list(fixture["prediction_contract"]), list(PREDICTION_FIELDS), "schema")
    audit.check("synthetic input order", tuple(fixture["prediction_contract"]["allowed_inputs"][0]) == ALLOWED_INPUT_FIELDS, list(fixture["prediction_contract"]["allowed_inputs"][0]), list(ALLOWED_INPUT_FIELDS), "schema")
    audit.check("synthetic robustness order", tuple(fixture["robustness_contract"]) == ROBUSTNESS_FIELDS, list(fixture["robustness_contract"]), list(ROBUSTNESS_FIELDS), "schema")
    audit.check("candidate prediction bound", fixture["prediction_contract"]["candidate_id"] == fixture["observable_contract"]["candidate_maps"][0]["candidate_id"], fixture["prediction_contract"]["candidate_id"], fixture["observable_contract"]["candidate_maps"][0]["candidate_id"], "schema")
    audit.check("synthetic fixture shape valid", fixture_report["valid"], fixture_report, "valid synthetic shape", "schema")
    audit.check("target values absent", find_forbidden_keys(fixture) == [], find_forbidden_keys(fixture), [], "schema")
    audit.check("common estimand separate", set(fixture["observable_contract"]) == {"common_estimand", "candidate_maps"}, list(fixture["observable_contract"]), ["common_estimand", "candidate_maps"], "schema")

    purported_real = copy.deepcopy(fixture)
    purported_real["fixture_only"] = False
    real_report = validate_schema_shape(purported_real, synthetic_fixture_mode=False)
    audit.check("purported real freeze rejected", real_report["valid"] is False, real_report["valid"], False, "external_boundary")
    audit.check("real rejection code exact", real_report["error_codes"] == ["EXTERNAL_VERIFICATION_REQUIRED"], real_report["error_codes"], ["EXTERNAL_VERIFICATION_REQUIRED"], "external_boundary")
    audit.check("plausible signature not treated as verified", bool(purported_real["target_contract"]["commitment"]["custodian_signature"]) and not real_report["valid"], purported_real["target_contract"]["commitment"]["custodian_signature"], "shape present but verification absent", "external_boundary")

    hostile = hostile_reports(fixture)
    expected_hostile = (
        "root_extra",
        "empty_root_identity",
        "empty_target_identity",
        "target_estimand_mismatch",
        "target_leakage",
        "hidden_sealed_payload",
        "target_alias",
        "temporal_order",
        "hash_mutation",
        "path_traversal",
        "independence",
        "baseline_missing",
        "duplicate_candidate_map",
        "eligible_map_missing",
        "unbound_prediction",
        "input_source_id_missing",
        "input_discovery_source_id",
        "input_source_alias",
        "nested_wrong_type",
        "commitment_scalar_types",
        "provenance_oid_scalar_types",
        "remote_url_no_hostname",
        "input_scalar_types",
        "estimand_scalar_type",
        "contestant_scalar_type",
        "estimand_container_type",
        "estimator_container_type",
        "remote_anchor",
    )
    audit.check("hostile fixture names exact", tuple(hostile) == expected_hostile, list(hostile), list(expected_hostile), "hostile")
    for name in expected_hostile:
        report = hostile[name]
        audit.check(f"{name} rejected", report["valid"] is False, report["valid"], False, "hostile")
        audit.check(f"{name} expected code", report["expected_code_observed"], report["error_codes"], report["expected_error_code"], "hostile")

    expected_map_only_survival_hostile = (
        "hard_row_removed",
        "survival_rule_softened",
        "m1_nonpass_promoted",
        "m2_nonpass_promoted",
        "m5_nonpass_promoted",
        "preserved_regulator_removed",
        "map_only_survivor_fabricated",
    )
    authority_map_hostile = authority["map_only_repair_hostile_fixtures"]
    audit.check("independent map-only hostile names exact", tuple(map_only_survival_hostile) == expected_map_only_survival_hostile and tuple(authority_map_hostile["cases"]) == expected_map_only_survival_hostile, list(map_only_survival_hostile), list(expected_map_only_survival_hostile), "map_only_hostile")
    for name in expected_map_only_survival_hostile:
        report = map_only_survival_hostile[name]
        audit.check(f"map-only {name} rejected", report["valid"] is False, report["valid"], False, "map_only_hostile")
        audit.check(f"map-only {name} expected code", report["expected_code_observed"], report["error_codes"], report["expected_error_code"], "map_only_hostile")

    expected_successor_hostile = (
        "candidate_created",
        "candidate_manifest_materialized",
        "admission_promoted",
        "map_promoted",
        "prediction_materialized",
        "target_materialized",
        "freeze_or_tag_materialized",
        "score_or_selection_materialized",
        "response_channel_smuggled",
        "error_budget_term_dropped",
        "fingerprint_dimension_changed",
    )
    authority_successor_hostile = authority["m2_v1_successor_hostile_fixtures"]
    audit.check("successor hostile names exact", tuple(successor_hostile) == expected_successor_hostile, list(successor_hostile), list(expected_successor_hostile), "successor_hostile")
    audit.check("successor hostile authority exact", tuple(authority_successor_hostile["cases"]) == expected_successor_hostile and authority_successor_hostile["v1_0_freeze_schema_hostile_count_preserved"] == 28 and authority_successor_hostile["successor_hostile_count"] == len(expected_successor_hostile) and authority_successor_hostile["total_hostile_class_count"] == 28 + len(expected_successor_hostile), authority_successor_hostile, {"v1_0": 28, "successor": len(expected_successor_hostile)}, "successor_hostile")
    for name in expected_successor_hostile:
        report = successor_hostile[name]
        audit.check(f"successor {name} rejected", report["valid"] is False, report["valid"], False, "successor_hostile")
        audit.check(f"successor {name} expected code", report["expected_code_observed"], report["error_codes"], report["expected_error_code"], "successor_hostile")

    authority_physical_hostile = authority["m2_physical_response_successor_minimum_contract_hostile_fixtures"]
    audit.check("independent physical-contract hostile names", tuple(physical_contract_hostile) == EXPECTED_PHYSICAL_CONTRACT_HOSTILES and tuple(authority_physical_hostile["cases"]) == EXPECTED_PHYSICAL_CONTRACT_HOSTILES, list(physical_contract_hostile), list(EXPECTED_PHYSICAL_CONTRACT_HOSTILES), "physical_contract_hostile")
    for name in EXPECTED_PHYSICAL_CONTRACT_HOSTILES:
        report = physical_contract_hostile[name]
        audit.check(f"physical-contract {name} rejected", report["valid"] is False, report["valid"], False, "physical_contract_hostile")
        audit.check(f"physical-contract {name} expected code", report["expected_code_observed"], report["error_codes"], report["expected_error_code"], "physical_contract_hostile")

    actual = validate_requested_freeze(freeze_path, staged=staged)
    audit.check("actual freeze never accepted", actual["valid"] is False, actual["valid"], False, "external_boundary")
    audit.check("external code retained for actual path", "EXTERNAL_VERIFICATION_REQUIRED" in actual["error_codes"], actual["error_codes"], "contains EXTERNAL_VERIFICATION_REQUIRED", "external_boundary")

    audit.check("independent v1.3 suite valid", v13_report["valid"], v13_report, "valid", "v1_3")
    audit.check("independent v1.3 authority suite valid", authority_v13_report["valid"], authority_v13_report, "valid", "v1_3")
    audit.check("independent v1.3 authority exact", authority_v13_suite == v13_suite, authority_v13_suite, v13_suite, "v1_3")
    audit.check("independent v1.3 exact identities", tuple(v13_suite["closed_child_ids"]) == NEW_CLOSED_SUBGATES and tuple(v13_suite["negative_ids"]) == NEW_NEGATIVE_IDS and tuple(v13_suite["open_successor_gate_ids"]) == OPEN_SUCCESSOR_GATES, [v13_suite["closed_child_ids"], v13_suite["negative_ids"], v13_suite["open_successor_gate_ids"]], [NEW_CLOSED_SUBGATES, NEW_NEGATIVE_IDS, OPEN_SUCCESSOR_GATES], "v1_3")
    u1 = v13_suite["real_scalar_internal_u1_and_winding"]
    audit.check("independent GL1 compact-connected proof scope", "GL(1,R)" in u1["theorem"] and "compact" in u1["theorem"] and u1["intrinsic_winding_sectors"] is False, u1, "trivial GL1/no winding", "v1_3")
    phason = v13_suite["one_q_auxiliary_phason_curvature_and_finite_torus_secant"]
    fixture13 = phason["fraction_fixture"]
    audit.check("independent canonical branch fixture", fixture13["inputs"] == {"r": "-3", "c": "2", "q": "5", "g": "7", "fundamental_reciprocal_step_h": "1"} and fixture13["optimized_amplitude_squared"] == "4/7" and fixture13["q_over_h_integer"] == 5, fixture13, "canonical upstream fixture", "v1_3")
    audit.check("independent phason identities", phason["symbolic_all_eight_signs"] and phason["symbolic_optimized_identity"] and phason["symbolic_cubic_identity"], phason, "all exact", "v1_3")
    audit.check("independent phason outputs", [fixture13[key] for key in ("continuum_curvature", "finite_torus_secant", "secant_correction", "relative_correction")] == ["400/7", "404/7", "4/7", "1/100"], fixture13, ["400/7", "404/7", "4/7", "1/100"], "v1_3")
    response13 = v13_suite["helicity_tensor_contact_shift_nonidentifiability"]
    audit.check("independent tensor contact shift", response13["response_shift"] == "Upsilon -> Upsilon+D" and "positive gap" in response13["hypotheses"][-1], response13, "+D/gap", "v1_3")
    amap13 = v13_suite["analytic_map_integer_exponent_transport"]
    audit.check("independent analytic orders", [amap13["hostile_polynomials"]["x_squared_order"], amap13["hostile_polynomials"]["x_cubed_order"]] == [2, 3] and amap13["positive_one_sided_local_invertibility_alone_sufficient"] is False, amap13, [2, 3, False], "v1_3")
    transport13 = v13_suite["six_stage_relative_log_slope_error_transport"]
    audit.check("independent adjacent-ratio transport", transport13["stage_count"] == 6 and transport13["initial_stage_exact"] and transport13["scale_domain"] == "lambda>0 and lambda!=1" and "abs(log(lambda))" in transport13["log_slope_bound"] and transport13["fraction_fixture"]["all_stage_outputs_positive"] and transport13["fraction_fixture"]["all_delta_strictly_below_one"], transport13, "six adjacent ratios and positive floors", "v1_3")
    authority_hostile13 = authority["m2_v1_3_hostile_fixtures"]
    audit.check("independent v1.3 hostile names/count", tuple(v13_hostile) == EXPECTED_V13_HOSTILES and tuple(authority_hostile13["cases"]) == EXPECTED_V13_HOSTILES and authority_hostile13["count"] == len(EXPECTED_V13_HOSTILES), [tuple(v13_hostile), authority_hostile13], EXPECTED_V13_HOSTILES, "v1_3_hostile")
    for name in EXPECTED_V13_HOSTILES:
        report = v13_hostile[name]
        audit.check(f"independent v1.3 {name} rejected", report["valid"] is False, report["valid"], False, "v1_3_hostile")
        audit.check(f"independent v1.3 {name} code", report["expected_code_observed"], report["error_codes"], report["expected_error_code"], "v1_3_hostile")

    formal = formal_authority_audit(audit, staged=staged)
    verdict = (
        "PASS"
        if formal["status"] == "COMPLETE" and freeze_path is None
        else ("STAGED" if staged else "INCOMPLETE")
    )
    passed = len(audit.rows)
    source_paths = (
        SCRIPT,
        PRIMARY_SCRIPT,
        AUTHORITY_MANIFEST,
        AUTHORITY_CERTIFICATE,
        ROUND1_MANIFEST,
        ADMISSION_FREEZE,
        M0_MANIFEST,
        M1_MANIFEST,
        M2_MANIFEST,
        M5_MANIFEST,
    )
    return {
        "schema": RESULT_SCHEMA,
        "script_version": __version__,
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
        "verdict": verdict,
        "summary": {"passed": passed, "failed": 0, "total": passed},
        "authority": formal,
        "current_tree": state,
        "current_version_map_only_audit": map_only,
        "map_only_survival_validation": map_only_survival_report,
        "map_only_repair_hostile_fixtures": map_only_survival_hostile,
        "m2_retrospective_stiffness_map_underdetermination": response_countermodels,
        "m2_finite_torus_dispersion_fingerprint": fingerprint,
        "m2_v1_successor_design": successor_design,
        "m2_v1_successor_design_validation": successor_report,
        "successor_hostile_fixtures": successor_hostile,
        "m2_linear_probe_second_order_response_nonidentifiability": linear_probe,
        "m2_physical_response_successor_minimum_contract_validation": physical_contract_report,
        "m2_physical_response_successor_minimum_contract_fixture": physical_contract_fixture,
        "m2_physical_response_successor_minimum_contract_hostile_fixtures": physical_contract_hostile,
        "m2_physical_response_successor_minimum_contract_reordered_metamorphic": physical_contract_reordered,
        "m2_physical_response_successor_minimum_contract_fuzz": physical_contract_fuzz,
        "m2_v1_3_theorem_suite": v13_suite,
        "m2_v1_3_theorem_suite_validation": v13_report,
        "m2_v1_3_hostile_fixtures": v13_hostile,
        "freeze_schema_contract": {
            "schema": FREEZE_SCHEMA,
            "root_fields": list(ROOT_FIELDS),
            "target_fields": list(TARGET_FIELDS),
            "commitment_fields": list(COMMITMENT_FIELDS),
            "disclosure_fields": list(DISCLOSURE_FIELDS),
            "prediction_fields": list(PREDICTION_FIELDS),
            "allowed_input_fields": list(ALLOWED_INPUT_FIELDS),
            "robustness_fields": list(ROBUSTNESS_FIELDS),
            "candidate_neutral_object": "common estimand and raw estimator",
            "candidate_specific_object": (
                "microscopic-to-observable map plus candidate_id-bound frozen prediction"
            ),
            "commitment_definition": (
                "HMAC-SHA256(external custodian key, domain separator || 0x00 || "
                "RFC8785-JCS canonical target payload)"
            ),
            "path_policy": "relative normalized POSIX path resolved inside repository",
            "required_temporal_order": "custodian commitment <= public remote freeze < target disclosure",
            "official_record_path": "predictions/freezes/<PRED-ID>-freeze.md",
            "official_tag_pattern": "freeze/<PRED-ID>/v<N>",
        },
        "synthetic_schema_validation": {
            "valid": fixture_report["valid"],
            "fixture_digest": hashlib.sha256(canonical_bytes(fixture)).hexdigest(),
        },
        "hostile_fixtures": hostile,
        "actual_freeze_validation": actual,
        "real_freeze_verification_boundary": {
            "schema_shape_validated": True,
            "required_error_code": "EXTERNAL_VERIFICATION_REQUIRED",
            "custodian_signature_cryptographically_verified": False,
            "remote_commit_fetched_and_verified": False,
            "remote_annotated_tag_fetched_and_verified": False,
            "remote_tag_ref_fetched_and_verified": False,
            "independently_authenticated_receipt_present": False,
            "real_freeze_acceptance_enabled": False,
        },
        "scope": {
            "protocol_schema_shape_validated": True,
            "current_tree_readiness_audited": True,
            "cryptographic_signature_verifier_implemented": False,
            "independent_remote_ref_verifier_implemented": False,
            "actual_freeze_record_created": False,
            "git_tag_created": False,
            "external_target_commitment_present": False,
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
        },
        "source_hashes": {
            repo_path(path): normalized_sha256(path) for path in source_paths
        },
        "assertions": audit.rows,
        "boundary": (
            "Independent cumulative v1.0-v1.2 protocol/schema plus the v1.3 GL1 "
            "no-go, auxiliary phason, tensor-contact ambiguity, analytic integer-order "
            "transport, and six-stage adjacent-ratio error bound. No compact action, "
            "physical response, candidate, six-term error budget, freeze, parent "
            "closure, Pre-A exit, or physical Sector-A selection follows."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--freeze-manifest", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument(
        "--staged",
        action="store_true",
        help="allow not-yet-registered formal authorities and missing requested freeze",
    )
    arguments = parser.parse_args()

    payload = build_payload(arguments.freeze_manifest, staged=arguments.staged)
    encoded = canonical_bytes(payload)
    digest = hashlib.sha256(encoded).hexdigest()
    if arguments.self_test:
        repeated = build_payload(arguments.freeze_manifest, staged=arguments.staged)
        if encoded != canonical_bytes(repeated):
            raise AssertionError("independent self-test payload is nondeterministic")
        print(
            f"SELF-TEST {payload['verdict']} {payload['summary']['passed']}/"
            f"{payload['summary']['total']} | SHA256 {digest} | {RESULT_ID}"
        )
        if payload["authority"]["missing"]:
            print("STAGED-MISSING " + ", ".join(payload["authority"]["missing"]))
        return 0 if payload["verdict"] == "PASS" or arguments.staged else 1

    if payload["verdict"] != "PASS" and not arguments.staged:
        print(
            f"INCOMPLETE {payload['summary']['passed']}/{payload['summary']['total']} | "
            + ", ".join(payload["authority"]["missing"])
        )
        return 1
    if not arguments.no_store:
        atomic_json(arguments.output, payload)
    label = "PASS" if payload["verdict"] == "PASS" else "STAGED"
    print(
        f"{label} {payload['summary']['passed']}/{payload['summary']['total']} | "
        f"SHA256 {digest} | {RESULT_ID}"
    )
    print("NO-STORE" if arguments.no_store else arguments.output)
    if payload["authority"]["missing"]:
        print("STAGED-MISSING " + ", ".join(payload["authority"]["missing"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
