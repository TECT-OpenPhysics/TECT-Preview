#!/usr/bin/env python3
"""Verify the future Pre-A prospective-holdout freeze protocol.

The script has two deliberately separate jobs.

1. It audits the exact current Round-1 tree.  At the issue checkpoint there is
   no machine freeze record or ``freeze/*`` tag, no admitted microscopic
   survivor, and no admitted M1/M2/M5 physical observable-map/prediction pair.
2. It validates a fail-closed machine schema for a *future* blind holdout and
   exercises hostile fixtures for exact field allowlists, leakage, temporal
   order, hashes, independence, map/prediction binding, input provenance, and
   remote anchoring.

The valid schema used below is a synthetic self-test fixture only.  It is not
an actual prediction, target commitment, freeze record, or authorization to
create a git tag.  In particular, this script does not close
``PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE``, Pre-A, or Sector A.

Version history:
  1.5.0 (2026-08-11): harden the physical-response schema with exact artifact
        refs, canonical rationals, source firewalls, three verifier bindings,
        unique error evidence, metamorphic checks, and hostile fuzz.
  1.4.0 (2026-08-11): prove finite-beta and ground-energy second-order
        response nonidentifiability for a fixed linear probe, and validate a
        fail-closed minimum physical-response successor contract.
  1.3.0 (2026-08-11): add the exact current-version map-empty-set proof,
        retrospective M2 response-map underdetermination, 48-component finite-
        torus dispersion fingerprint, and DESIGN_ONLY successor-schema audit.
  1.2.0 (2026-08-11): enforce exact nested target and input schemas, bind one
        frozen candidate prediction to an eligible admitted map, add hostile
        alias/type fixtures, and make live freeze-tag observation non-binding.
  1.1.0 (2026-08-11): bind the R-168 manifest/certificate and expose the
        complete result, gate, and negative-result provenance contract.
  1.0.0 (2026-08-11): first issue; current-tree readiness and hostile-schema
        fixtures.
"""

from __future__ import annotations

import argparse
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
__version_issued__ = "2026-08-11"

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
INDEPENDENT_SCRIPT = REPO / "codes/foundations/pre_a_round1_prospective_holdout_freeze_protocol_independent.py"
SLUG = "pre-a-round1-prospective-holdout-freeze-protocol"
RESULT_SCHEMA = f"tect/{SLUG}-primary-result/1.0"
FREEZE_SCHEMA = "tect/pre-a-round1-prospective-holdout-freeze/1.0"
PARENT_GATE = "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE"
AUDITED_COMMIT = "99157442831c0e44d425b5d5f8cd78856c57da53"
RESULT_ID = (
    "PA-ROUND1-PROSPECTIVE-HOLDOUT-FREEZE-PROTOCOL-AND-CURRENT-TREE-"
    "READINESS-AUDIT"
)
RESULT_NUMBER = "R-168"
RESULT_VERSION = "v1.2"
EXPLORATION_ID = "EXP-000812"
PRIOR_EXPLORATION_IDS = ("EXP-000807", "EXP-000808", "EXP-000810")
MAP_ONLY_NEGATIVE_ID = (
    "NG-2026-08-11-PRE-A-ROUND1-CURRENT-VERSION-MAP-ONLY-ADMISSION-REPAIR"
)
LINEAR_PROBE_NEGATIVE_ID = (
    "NG-2026-08-11-PRE-A-M2-LANE-Q-LINEAR-SOURCE-AUTOMATIC-PHYSICAL-"
    "STIFFNESS-RESPONSE"
)
PRIOR_NEGATIVE_IDS = (
    "NG-2026-08-11-PRE-A-ROUND1-CURRENT-TREE-PROSPECTIVE-HOLDOUT-"
    "NONEXISTENCE",
    MAP_ONLY_NEGATIVE_ID,
)
NEW_NEGATIVE_IDS = (LINEAR_PROBE_NEGATIVE_ID,)
NEGATIVE_IDS = PRIOR_NEGATIVE_IDS + NEW_NEGATIVE_IDS
REUSED_NEGATIVE_IDS = (
    "NG-2026-08-09-PRE-A-ROUND1-UNFROZEN-TOURNAMENT-SELECTION",
)
MAP_ONLY_CLOSED_CHILD = (
    "PA-ROUND1-CURRENT-VERSION-M1-M2-M5-MAP-ONLY-ADMISSION-EMPTY-SET"
)
FINGERPRINT_CLOSED_CHILD = "PA-M2-CI8-FINITE-TORUS-GAUSSIAN-DISPERSION-FINGERPRINT"
PRIOR_CLOSED_SUBGATES = (
    "PA-ROUND1-COMMON-ESTIMAND-AND-CANDIDATE-MAP-SCHEMA",
    "PA-ROUND1-PROSPECTIVE-FREEZE-PROVENANCE-PROTOCOL",
    "PA-ROUND1-TARGET-INDEPENDENCE-AND-ANTI-LEAKAGE-SCHEMA-VALIDATOR",
    "PA-ROUND1-CURRENT-CANDIDATE-MAP-ADMISSION-EMPTY-SET-AUDIT",
    MAP_ONLY_CLOSED_CHILD,
    FINGERPRINT_CLOSED_CHILD,
)
NEW_CLOSED_SUBGATES = (
    "PA-M2-CI8-LINEAR-PROBE-SECOND-ORDER-RESPONSE-NONIDENTIFIABILITY",
    "PA-M2-CI8-PHYSICAL-RESPONSE-SUCCESSOR-MINIMUM-CONTRACT-SCHEMA",
)
CLOSED_SUBGATES = PRIOR_CLOSED_SUBGATES + NEW_CLOSED_SUBGATES
PHYSICAL_RESPONSE_GATE = "PA-M2-CI8-PHYSICAL-RESPONSE-CHANNEL-AND-ERROR-BOUND"
OPEN_GATES = (
    PARENT_GATE,
    "PA-ROUND1-PER-PARAMETER-COMMON-INPUT-LEDGER",
    "PA-ROUND1-INDEPENDENT-CUSTODIAN-OPAQUE-TARGET-COMMITMENT",
    "PA-ROUND1-ADMISSIBLE-MICROSCOPIC-CANDIDATE-MAP-AND-FROZEN-PREDICTION",
    "PA-ROUND1-CRYPTOGRAPHIC-CUSTODIAN-SIGNATURE-AND-REMOTE-FREEZE-"
    "VERIFICATION",
    PHYSICAL_RESPONSE_GATE,
)
M2_SUCCESSOR_ID = "PA-M2-CI8-RS-DISPERSION-MAP-v1"

FREEZE_DIRECTORY = REPO / "predictions/freezes"
PREDICTION_LEDGER = REPO / "predictions/prediction-ledger.md"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
RESULTS_LEDGER = REPO / "RESULTS-LEDGER.md"
EXPLORATION_LOG = REPO / "explorations/log.jsonl"
GATE_REGISTRY = REPO / "claims/GATES.md"
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
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-11-primary-{SLUG}/result.json"
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
DISCLOSURE_FIELDS = (
    "status",
    "not_before_utc",
    "actual_at_utc",
)
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
ALLOWED_INPUT_FIELDS = (
    "id",
    "class",
    "source",
    "source_id",
    "used_for",
)
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
FORBIDDEN_TARGET_VALUE_KEYS = {
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
HASH_RE = re.compile(r"[0-9a-f]{64}")
OID_RE = re.compile(r"[0-9a-f]{40}")

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
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_safe(item) for item in value]
    return str(value)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
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


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{repo_path(path)} must contain a JSON object")
    return value


def git_output(*arguments: str) -> list[str]:
    run = subprocess.run(
        ["git", *arguments],
        cwd=REPO,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    return [line.strip() for line in run.stdout.splitlines() if line.strip()]


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


def git_show_json(commit: str, path: Path) -> dict[str, Any]:
    value = json.loads(git_text("show", f"{commit}:{repo_path(path)}"))
    if not isinstance(value, dict):
        raise TypeError(f"{repo_path(path)} at {commit} must contain an object")
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
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS",
                "actual": json_safe(actual),
                "expected": json_safe(expected),
            }
        )


def error(errors: list[dict[str, str]], code: str, message: str) -> None:
    if code not in {row["code"] for row in errors}:
        errors.append({"code": code, "message": message})


def exact_object(
    value: Any,
    fields: tuple[str, ...],
    errors: list[dict[str, str]],
    code: str,
    label: str,
) -> dict[str, Any]:
    """Return an object and record a structured exact-field failure."""

    if not isinstance(value, dict):
        error(errors, code, f"{label} must be an object with exact fields")
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
        error(errors, code, f"{label} fields invalid: " + "; ".join(details))
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


def path_hash_valid(path_text: Any, digest: Any) -> bool:
    if not isinstance(path_text, str) or not isinstance(digest, str):
        return False
    if HASH_RE.fullmatch(digest) is None:
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


def forbidden_value_keys(value: Any, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            location = f"{prefix}.{key}" if prefix else str(key)
            if key in FORBIDDEN_TARGET_VALUE_KEYS:
                found.append(location)
            found.extend(forbidden_value_keys(item, location))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(forbidden_value_keys(item, f"{prefix}[{index}]"))
    return found


def validate_freeze_manifest(
    manifest: dict[str, Any], *, allow_fixture: bool = False
) -> dict[str, Any]:
    """Return a complete fail-closed validation report for one freeze object."""

    errors: list[dict[str, str]] = []
    missing = [field for field in ROOT_FIELDS if field not in manifest]
    extra = [field for field in manifest if field not in ROOT_FIELDS]
    if missing:
        error(errors, "ROOT_FIELDS_MISSING", ", ".join(missing))
        return {"valid": False, "error_codes": [row["code"] for row in errors], "errors": errors}
    if extra:
        error(errors, "ROOT_FIELDS_EXTRA", ", ".join(repr(field) for field in extra))

    if manifest["schema"] != FREEZE_SCHEMA:
        error(errors, "SCHEMA_INVALID", "unexpected freeze schema")
    if manifest["parent_gate"] != PARENT_GATE:
        error(errors, "PARENT_GATE_INVALID", "unexpected parent gate")
    if manifest["status"] != "FROZEN_UNSCORED" or manifest["claim_bearing"] is not False:
        error(errors, "LIFECYCLE_INVALID", "freeze must be claim-nonbearing and unscored")
    root_identity_fields = ("freeze_id", "prediction_id", "round_id", "no_overclaim")
    if any(
        not isinstance(manifest[field], str) or not manifest[field].strip()
        for field in root_identity_fields
    ):
        error(errors, "ROOT_VALUES_INVALID", "freeze, prediction, round, and scope strings must be nonempty")
    if manifest["fixture_only"] is not True and manifest["fixture_only"] is not False:
        error(errors, "LIFECYCLE_INVALID", "fixture_only must be a Boolean")
    if bool(manifest["fixture_only"]) and not allow_fixture:
        error(errors, "FIXTURE_FORBIDDEN", "synthetic fixtures cannot become real freezes")

    contestants = manifest["contestant_snapshot"]
    if not isinstance(contestants, list):
        contestants = []
        error(errors, "CONTESTANTS_INVALID", "contestant_snapshot must be a list")
    candidate_ids: list[str] = []
    eligible_ids: set[str] = set()
    baselines: list[str] = []
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
            error(errors, "CONTESTANTS_INVALID", "candidate_id must be a nonempty string")
            candidate_id = ""
        else:
            candidate_ids.append(candidate_id)
        role = row.get("role")
        if not is_nonempty_string(role):
            error(errors, "CONTESTANTS_INVALID", "contestant role must be nonempty")
        eligibility = row.get("score_eligible_as_microscopic_winner")
        if eligibility is not True and eligibility is not False:
            error(errors, "CONTESTANTS_INVALID", "contestant eligibility must be Boolean")
        if role == "EFFECTIVE_NULL_BASELINE":
            baselines.append(candidate_id)
            if row.get("score_eligible_as_microscopic_winner") is not False:
                error(errors, "BASELINE_INVALID", "baseline cannot be a microscopic winner")
        elif row.get("score_eligible_as_microscopic_winner") is True:
            if not isinstance(role, str) or role not in ELIGIBLE_ROLES:
                error(errors, "ELIGIBLE_ROLE_INVALID", "eligible contestant has an unknown role")
            eligible_ids.add(candidate_id)
        if not path_hash_valid(row.get("path"), row.get("normalized_sha256")):
            error(errors, "HASH_FAILURE", f"invalid contestant hash for {candidate_id}")
    if len(candidate_ids) != len(set(candidate_ids)):
        error(errors, "CANDIDATE_DUPLICATE", "candidate IDs must be unique")
    if len(baselines) != 1:
        error(errors, "BASELINE_MISSING", "exactly one effective null baseline is required")
    if not eligible_ids:
        error(errors, "ELIGIBLE_CANDIDATE_MISSING", "at least one microscopic contestant is required")

    evidence = exact_object(
        manifest["evidence_snapshot"],
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
        error(
            errors,
            "DISCOVERY_FIREWALL_INVALID",
            "evidence ID and independence-group fields must be nonempty string lists",
        )
    if not discovery_ids or not discovery_ids <= forbidden_fit_ids:
        error(errors, "DISCOVERY_FIREWALL_INVALID", "every discovery input must be forbidden for fitting")
    if not path_hash_valid(evidence.get("path"), evidence.get("normalized_sha256")):
        error(errors, "HASH_FAILURE", "invalid evidence snapshot hash")

    target = exact_object(
        manifest["target_contract"],
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
        error(
            errors,
            "TARGET_CONTRACT_INVALID",
            "target identity, custodian, accession, estimand, and units must be nonempty",
        )
    leaked_keys = forbidden_value_keys(manifest)
    if leaked_keys or target.get("target_value_present") is not False:
        error(errors, "TARGET_LEAKAGE", ", ".join(leaked_keys) or "target_value_present")
    if target.get("blind") is not True or target.get("predictor_access_before_freeze") is not False:
        error(errors, "BLINDNESS_INVALID", "target must be blind with no predictor access")
    target_group = target.get("independence_group")
    if (
        not is_nonempty_string(target_group)
        or target_group in discovery_groups | calibration_groups
    ):
        error(errors, "INDEPENDENCE_OVERLAP", "target group overlaps discovery or calibration")
    commitment = exact_object(
        target.get("commitment"),
        COMMITMENT_FIELDS,
        errors,
        "COMMITMENT_INVALID",
        "target_contract.commitment",
    )
    if (
        commitment.get("algorithm") != "HMAC-SHA256"
        or not isinstance(commitment.get("commitment_hex"), str)
        or HASH_RE.fullmatch(commitment.get("commitment_hex", "")) is None
        or commitment.get("secret_key_custody") != "EXTERNAL_CUSTODIAN"
        or commitment.get("payload_schema")
        != "tect/pre-a-round1-holdout-target-payload/1.0"
        or commitment.get("canonical_serialization") != "RFC8785-JCS"
        or commitment.get("domain_separation")
        != "TECT-PRE-A-ROUND1-HOLDOUT-TARGET-v1"
        or not is_nonempty_string(commitment.get("custodian_signature"))
        or not isinstance(commitment.get("public_key_fingerprint"), str)
        or HASH_RE.fullmatch(commitment.get("public_key_fingerprint", "")) is None
        or not is_nonempty_string(commitment.get("issued_at_utc"))
    ):
        error(
            errors,
            "COMMITMENT_INVALID",
            "externally keyed, custodian-signed canonical HMAC commitment required",
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
        error(errors, "TARGET_ALREADY_DISCLOSED", "freeze must precede actual disclosure")

    observable = exact_object(
        manifest["observable_contract"],
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
    if not all(is_nonempty_string(estimand.get(key)) for key in ("id", "definition", "units")):
        error(errors, "ESTIMAND_INVALID", "common estimand is incomplete")
    if (
        target.get("estimand_id") != estimand.get("id")
        or target.get("units") != estimand.get("units")
    ):
        error(
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
    if not path_hash_valid(estimator.get("path"), estimator.get("sha256")):
        error(errors, "HASH_FAILURE", "raw estimator hash is invalid")
    maps = observable.get("candidate_maps", [])
    admitted_map_ids: set[str] = set()
    map_candidate_ids: list[str] = []
    if not isinstance(maps, list):
        error(errors, "CANDIDATE_MAPS_INVALID", "candidate_maps must be a list")
        maps = []
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
            error(errors, "CANDIDATE_MAPS_INVALID", "candidate map ID must be nonempty")
            continue
        candidate_id = candidate_id_value
        map_candidate_ids.append(candidate_id)
        required_map_text_fields = (
            "map_statement",
            "domain",
            "state_and_reference",
            "units_map",
            "limit_order",
        )
        proof_refs = row.get("proof_refs")
        nuisance_inputs = row.get("nuisance_inputs")
        declared_map_types_valid = (
            is_nonempty_string(row.get("status"))
            and is_nonempty_string(row.get("script_path"))
            and isinstance(row.get("script_sha256"), str)
            and HASH_RE.fullmatch(row.get("script_sha256", "")) is not None
            and is_string_list(proof_refs, nonempty=True)
            and is_string_list(nuisance_inputs, nonempty=False)
        )
        if not declared_map_types_valid:
            error(errors, "CANDIDATE_MAPS_INVALID", f"candidate map types invalid for {candidate_id}")
        map_complete = (
            all(
                isinstance(row.get(key), str) and bool(row.get(key).strip())
                for key in required_map_text_fields
            )
            and declared_map_types_valid
        )
        if row.get("status") == "ADMITTED" and map_complete:
            if path_hash_valid(row.get("script_path"), row.get("script_sha256")):
                admitted_map_ids.add(candidate_id)
            else:
                error(errors, "HASH_FAILURE", f"map script hash invalid for {candidate_id}")
        elif row.get("status") == "ADMITTED":
            error(errors, "CANDIDATE_MAPS_INVALID", f"admitted map incomplete for {candidate_id}")
    if len(map_candidate_ids) != len(set(map_candidate_ids)):
        error(
            errors,
            "MAP_CANDIDATE_DUPLICATE",
            "candidate maps must be uniquely keyed by candidate_id",
        )
    if not eligible_ids or not eligible_ids <= admitted_map_ids:
        error(
            errors,
            "ELIGIBLE_MAP_MISSING",
            "every eligible microscopic contestant needs an admitted map",
        )
    if set(map_candidate_ids) - set(candidate_ids):
        error(errors, "MAP_CANDIDATE_UNKNOWN", "map refers to an unregistered candidate")

    prediction = exact_object(
        manifest["prediction_contract"],
        PREDICTION_FIELDS,
        errors,
        "PREDICTION_CONTRACT_INVALID",
        "prediction_contract",
    )
    prediction_candidate_id = prediction.get("candidate_id")
    prediction_text_fields = (
        "predicted_relation",
        "theory_uncertainty",
        "acceptance_rule",
        "baseline_prediction",
    )
    forbidden_knobs = prediction.get("forbidden_knobs")
    if (
        any(
            not isinstance(prediction.get(key), str) or not prediction.get(key).strip()
            for key in prediction_text_fields
        )
        or prediction.get("physical_output") is not True
        or not isinstance(forbidden_knobs, list)
        or not forbidden_knobs
        or any(not isinstance(item, str) or not item.strip() for item in forbidden_knobs)
    ):
        error(errors, "PREDICTION_INVALID", "physical relation and scoring rule are incomplete")
    if (
        not isinstance(prediction_candidate_id, str)
        or not prediction_candidate_id.strip()
        or prediction_candidate_id not in eligible_ids
        or prediction_candidate_id not in admitted_map_ids
    ):
        error(
            errors,
            "PREDICTION_CANDIDATE_UNBOUND",
            "the frozen candidate prediction must name an eligible admitted-map candidate",
        )
    allowed_inputs = prediction.get("allowed_inputs", [])
    if not isinstance(allowed_inputs, list) or not allowed_inputs:
        error(errors, "INPUT_LEDGER_INVALID", "allowed input ledger is empty")
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
                error(errors, "INPUT_LEDGER_INVALID", "input ID must be nonempty")
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
                error(errors, "INPUT_LEDGER_INVALID", "input class or source is invalid")
            if isinstance(source_id, str) and source_id in forbidden_fit_ids | discovery_ids:
                error(errors, "DISCOVERY_REUSE", "discovery datum reused as prediction input")
        if len(input_ids) != len(set(input_ids)):
            error(errors, "INPUT_LEDGER_INVALID", "input IDs are not unique")

    robustness = exact_object(
        manifest["robustness_contract"],
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
        error(errors, "ROBUSTNESS_INVALID", "robustness envelope is incomplete")

    provenance = exact_object(
        manifest["provenance"],
        PROVENANCE_FIELDS,
        errors,
        "REMOTE_ANCHOR_INVALID",
        "provenance",
    )
    prediction_id = manifest["prediction_id"]
    freeze_version = manifest["freeze_version"]
    if not isinstance(freeze_version, int) or isinstance(freeze_version, bool) or freeze_version < 1:
        error(errors, "FREEZE_VERSION_INVALID", "freeze_version must be a positive integer")
        freeze_version = 0
    expected_tag = f"freeze/{prediction_id}/v{freeze_version}"
    remote_valid = (
        isinstance(provenance.get("freeze_commit_oid"), str)
        and OID_RE.fullmatch(provenance.get("freeze_commit_oid", "")) is not None
        and is_https_url_with_host(provenance.get("remote_url"))
        and isinstance(provenance.get("remote_commit_sha"), str)
        and provenance.get("remote_commit_sha") == provenance.get("freeze_commit_oid")
        and is_nonempty_string(provenance.get("remote_observed_at_utc"))
        and is_nonempty_string(provenance.get("annotated_tag"))
        and provenance.get("annotated_tag") == expected_tag
        and is_nonempty_string(provenance.get("remote_ref"))
        and provenance.get("remote_ref") == f"refs/tags/{expected_tag}"
        and isinstance(provenance.get("tag_object_oid"), str)
        and OID_RE.fullmatch(provenance.get("tag_object_oid", "")) is not None
        and provenance.get("tag_object_oid") != provenance.get("freeze_commit_oid")
    )
    if not remote_valid:
        error(errors, "REMOTE_ANCHOR_INVALID", "public commit and annotated tag anchor required")

    commitment_time = parse_utc(commitment.get("issued_at_utc"))
    remote_time = parse_utc(provenance.get("remote_observed_at_utc"))
    disclosure_time = parse_utc(disclosure.get("not_before_utc"))
    if (
        commitment_time is None
        or remote_time is None
        or disclosure_time is None
        or not commitment_time <= remote_time < disclosure_time
    ):
        error(errors, "TEMPORAL_ORDER_INVALID", "require commitment <= remote freeze < disclosure")

    scoring = exact_object(
        manifest["scoring"],
        SCORING_FIELDS,
        errors,
        "SCORING_STATE_INVALID",
        "scoring",
    )
    if (
        scoring.get("status") != "NOT_DISCLOSED"
        or scoring.get("target_path") is not None
        or scoring.get("result_path") is not None
        or not path_hash_valid(scoring.get("scorer_path"), scoring.get("scorer_sha256"))
    ):
        error(errors, "SCORING_STATE_INVALID", "scorer must be frozen before target access")

    if not allow_fixture:
        error(
            errors,
            "EXTERNAL_VERIFICATION_REQUIRED",
            "schema validation cannot replace cryptographic custodian-signature "
            "verification and independent remote commit/tag/ref verification",
        )

    return {
        "valid": not errors,
        "error_codes": [row["code"] for row in errors],
        "errors": errors,
    }


def synthetic_valid_manifest() -> dict[str, Any]:
    """Build a valid synthetic schema fixture from live file hashes."""

    script_hash = normalized_sha256(SCRIPT)
    m0_hash = normalized_sha256(M0_MANIFEST)
    evidence_hash = normalized_sha256(ADMISSION_FREEZE)
    commitment = hashlib.sha256(b"synthetic-opaque-custodian-commitment").hexdigest()
    fingerprint = hashlib.sha256(b"synthetic-custodian-public-key").hexdigest()
    freeze_commit = hashlib.sha256(b"synthetic-freeze-commit").hexdigest()[:40]
    tag_object = hashlib.sha256(b"synthetic-annotated-tag-object").hexdigest()[:40]
    prediction_id = "PA-R1-HO-FIXTURE-001"
    return {
        "schema": FREEZE_SCHEMA,
        "freeze_id": "PA-ROUND1-PROSPECTIVE-HOLDOUT-FREEZE-FIXTURE-v1",
        "prediction_id": prediction_id,
        "freeze_version": 1,
        "round_id": "PRE-A-ROUND1-FIXTURE",
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
                "normalized_sha256": m0_hash,
            },
            {
                "candidate_id": "FIXTURE-MICROSCOPIC-CANDIDATE-v1",
                "role": "COMPACT_GAUGE_ALTERNATIVE",
                "score_eligible_as_microscopic_winner": True,
                "path": repo_path(SCRIPT),
                "normalized_sha256": script_hash,
            },
        ],
        "evidence_snapshot": {
            "path": repo_path(ADMISSION_FREEZE),
            "normalized_sha256": evidence_hash,
            "discovery_ids": ["FIXTURE-DISCOVERY-001"],
            "forbidden_fit_ids": ["FIXTURE-DISCOVERY-001"],
            "discovery_independence_groups": ["FIXTURE-DISCOVERY-GROUP"],
            "calibration_independence_groups": ["FIXTURE-CALIBRATION-GROUP"],
        },
        "target_contract": {
            "target_id": "FIXTURE-SEALED-TARGET-001",
            "custodian": "SYNTHETIC EXTERNAL CUSTODIAN",
            "protocol_or_accession": "FIXTURE-PROTOCOL-001",
            "estimand_id": "FIXTURE-ESTIMAND-001",
            "units": "dimensionless",
            "independence_group": "FIXTURE-HOLDOUT-GROUP",
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
                "custodian_signature": "SYNTHETIC-SIGNATURE-NOT-A-REAL-FREEZE",
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
                "id": "FIXTURE-ESTIMAND-001",
                "definition": "Synthetic dimensionless holdout estimand",
                "units": "dimensionless",
                "raw_estimator": {
                    "path": repo_path(SCRIPT),
                    "sha256": script_hash,
                },
            },
            "candidate_maps": [
                {
                    "candidate_id": "FIXTURE-MICROSCOPIC-CANDIDATE-v1",
                    "status": "ADMITTED",
                    "map_statement": "Synthetic fixture map only",
                    "domain": "synthetic fixture domain",
                    "state_and_reference": "synthetic fixed state and reference",
                    "units_map": "dimensionless to dimensionless",
                    "limit_order": "synthetic fixed finite order",
                    "nuisance_inputs": [],
                    "proof_refs": [repo_path(SCRIPT)],
                    "script_path": repo_path(SCRIPT),
                    "script_sha256": script_hash,
                }
            ],
        },
        "prediction_contract": {
            "candidate_id": "FIXTURE-MICROSCOPIC-CANDIDATE-v1",
            "predicted_relation": "fixture_ratio = 1",
            "physical_output": True,
            "theory_uncertainty": "synthetic closed fixture interval",
            "acceptance_rule": "PASS iff disclosed fixture ratio lies in the frozen interval",
            "baseline_prediction": "synthetic baseline interval",
            "allowed_inputs": [
                {
                    "id": "FIXTURE-CALIBRATION-001",
                    "class": "CALIBRATION",
                    "source": "synthetic fixture calibration",
                    "source_id": "FIXTURE-CAL-001",
                    "used_for": "units only",
                }
            ],
            "forbidden_knobs": [
                "target-dependent map choice",
                "target-dependent parameter choice",
                "post-disclosure error-band change",
            ],
        },
        "robustness_contract": {
            "volume": "synthetic fixed envelope",
            "boundary": "synthetic fixed envelope",
            "regulator": "synthetic fixed envelope",
            "coefficients": "synthetic fixed envelope",
            "implementation": "two independent implementations required",
        },
        "provenance": {
            "freeze_commit_oid": freeze_commit,
            "remote_url": "https://example.invalid/fixture.git",
            "remote_commit_sha": freeze_commit,
            "remote_observed_at_utc": "2026-08-11T00:00:00Z",
            "annotated_tag": f"freeze/{prediction_id}/v1",
            "remote_ref": f"refs/tags/freeze/{prediction_id}/v1",
            "tag_object_oid": tag_object,
        },
        "scoring": {
            "status": "NOT_DISCLOSED",
            "target_path": None,
            "result_path": None,
            "scorer_path": repo_path(SCRIPT),
            "scorer_sha256": script_hash,
        },
        "no_overclaim": (
            "Synthetic schema fixture only; no target, physical candidate, prediction, "
            "Pre-A exit, Sector-A selection, or tag authorization follows."
        ),
    }


def hostile_fixture_reports(valid: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Mutate one contract dimension at a time and return rejection reports."""

    fixtures: dict[str, tuple[str, Callable[[dict[str, Any]], None]]] = {
        "root_extra": (
            "ROOT_FIELDS_EXTRA",
            lambda row: row.__setitem__("undeclared_payload", "forbidden"),
        ),
        "empty_root_identity": (
            "ROOT_VALUES_INVALID",
            lambda row: row.update(
                {"freeze_id": "", "prediction_id": "", "round_id": "", "no_overclaim": ""}
            ),
        ),
        "empty_target_identity": (
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
        "target_estimand_mismatch": (
            "TARGET_ESTIMAND_MISMATCH",
            lambda row: row["target_contract"].__setitem__(
                "estimand_id", "MISMATCHED-ESTIMAND"
            ),
        ),
        "target_leakage": (
            "TARGET_LEAKAGE",
            lambda row: row["target_contract"].__setitem__("target_value", "0.123"),
        ),
        "hidden_sealed_payload": (
            "TARGET_LEAKAGE",
            lambda row: row["target_contract"]["commitment"].__setitem__(
                "sealed_payload", "opaque-but-undeclared"
            ),
        ),
        "target_alias": (
            "TARGET_LEAKAGE",
            lambda row: row["target_contract"].__setitem__("holdout_value", "0.123"),
        ),
        "temporal_order": (
            "TEMPORAL_ORDER_INVALID",
            lambda row: row["provenance"].__setitem__(
                "remote_observed_at_utc", "2026-08-13T00:00:00Z"
            ),
        ),
        "hash_mutation": (
            "HASH_FAILURE",
            lambda row: row["contestant_snapshot"][1].__setitem__(
                "normalized_sha256", "0" * 64
            ),
        ),
        "path_traversal": (
            "HASH_FAILURE",
            lambda row: row["contestant_snapshot"][1].__setitem__(
                "path", "../outside-repository.py"
            ),
        ),
        "independence": (
            "INDEPENDENCE_OVERLAP",
            lambda row: row["target_contract"].__setitem__(
                "independence_group", "FIXTURE-DISCOVERY-GROUP"
            ),
        ),
        "baseline_missing": (
            "BASELINE_MISSING",
            lambda row: row.__setitem__(
                "contestant_snapshot", row["contestant_snapshot"][1:]
            ),
        ),
        "duplicate_candidate_map": (
            "MAP_CANDIDATE_DUPLICATE",
            lambda row: row["observable_contract"]["candidate_maps"].append(
                copy.deepcopy(row["observable_contract"]["candidate_maps"][0])
            ),
        ),
        "eligible_map_missing": (
            "ELIGIBLE_MAP_MISSING",
            lambda row: row["observable_contract"].__setitem__("candidate_maps", []),
        ),
        "unbound_prediction": (
            "PREDICTION_CANDIDATE_UNBOUND",
            lambda row: row["prediction_contract"].__setitem__(
                "candidate_id", "UNREGISTERED-CANDIDATE"
            ),
        ),
        "input_source_id_missing": (
            "INPUT_FIELDS_INVALID",
            lambda row: row["prediction_contract"]["allowed_inputs"][0].pop(
                "source_id"
            ),
        ),
        "input_discovery_source_id": (
            "DISCOVERY_REUSE",
            lambda row: row["prediction_contract"]["allowed_inputs"][0].__setitem__(
                "source_id", "FIXTURE-DISCOVERY-001"
            ),
        ),
        "input_source_alias": (
            "INPUT_FIELDS_INVALID",
            lambda row: row["prediction_contract"]["allowed_inputs"][0].__setitem__(
                "discovery_source_id", "FIXTURE-DISCOVERY-001"
            ),
        ),
        "nested_wrong_type": (
            "COMMITMENT_INVALID",
            lambda row: row["target_contract"].__setitem__("commitment", []),
        ),
        "commitment_scalar_types": (
            "COMMITMENT_INVALID",
            lambda row: row["target_contract"]["commitment"].update(
                {
                    "commitment_hex": int("1" * 64),
                    "public_key_fingerprint": int("2" * 64),
                    "custodian_signature": ["not-a-string"],
                }
            ),
        ),
        "provenance_oid_scalar_types": (
            "REMOTE_ANCHOR_INVALID",
            lambda row: row["provenance"].update(
                {
                    "freeze_commit_oid": int("1" * 40),
                    "remote_commit_sha": int("1" * 40),
                    "tag_object_oid": int("2" * 40),
                }
            ),
        ),
        "remote_url_no_hostname": (
            "REMOTE_ANCHOR_INVALID",
            lambda row: row["provenance"].__setitem__("remote_url", "https://"),
        ),
        "input_scalar_types": (
            "INPUT_LEDGER_INVALID",
            lambda row: row["prediction_contract"]["allowed_inputs"][0].update(
                {"class": ["CALIBRATION"], "used_for": None}
            ),
        ),
        "estimand_scalar_type": (
            "ESTIMAND_INVALID",
            lambda row: row["observable_contract"]["common_estimand"].__setitem__(
                "definition", ["not-a-string"]
            ),
        ),
        "contestant_scalar_type": (
            "CONTESTANTS_INVALID",
            lambda row: row["contestant_snapshot"][1].__setitem__(
                "role", ["COMPACT_GAUGE_ALTERNATIVE"]
            ),
        ),
        "estimand_container_type": (
            "ESTIMAND_INVALID",
            lambda row: row["observable_contract"].__setitem__("common_estimand", []),
        ),
        "estimator_container_type": (
            "ESTIMAND_INVALID",
            lambda row: row["observable_contract"]["common_estimand"].__setitem__(
                "raw_estimator", []
            ),
        ),
        "remote_anchor": (
            "REMOTE_ANCHOR_INVALID",
            lambda row: row["provenance"].__setitem__("remote_url", ""),
        ),
    }
    reports: dict[str, dict[str, Any]] = {}
    for name, (expected_code, mutate) in fixtures.items():
        hostile = copy.deepcopy(valid)
        mutate(hostile)
        report = validate_freeze_manifest(hostile, allow_fixture=True)
        reports[name] = {
            "expected_error_code": expected_code,
            "valid": report["valid"],
            "error_codes": report["error_codes"],
            "expected_code_observed": expected_code in report["error_codes"],
        }
    return reports



def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"



def build_map_only_survival_contract() -> dict[str, Any]:
    triage = load_json(ROUND1_MANIFEST)
    matrix = triage["categorical_matrix"]
    hard_rows = list(triage["survival_rule"]["hard_rows"])
    residual: dict[str, dict[str, str]] = {}
    for candidate_id, row_oracle in MAP_ONLY_RESIDUAL_ORACLE.items():
        residual[candidate_id] = {
            row_id: matrix[candidate_id][row_id] for row_id in row_oracle
        }
    requirements = {
        candidate_id: list(items)
        for candidate_id, items in MAP_ONLY_SUBSTANTIVE_REQUIREMENTS.items()
    }
    return {
        "schema": MAP_ONLY_SURVIVAL_SCHEMA,
        "source_path": repo_path(ROUND1_MANIFEST),
        "source_sha256": normalized_sha256(ROUND1_MANIFEST),
        "hard_rows": hard_rows,
        "survives_if": triage["survival_rule"]["survives_if"],
        "hypothetical_map_only_change": {
            "hypothetical_only": True,
            "microscopic_map_after": "ADMITTED",
            "preserved_fields": list(MAP_ONLY_PRESERVED_FIELDS),
        },
        "residual_hard_rows": residual,
        "map_only_survivor_ids": [],
        "all_pass_after_map_only": False,
        "substantive_new_version_requirements": requirements,
        "boundary": (
            "A response-map-only extension preserving parent law/state/reference/"
            "regulator data cannot clear the listed non-PASS hard rows."
        ),
    }


def validate_map_only_survival_contract(contract: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    row = exact_object(
        contract,
        MAP_ONLY_SURVIVAL_FIELDS,
        errors,
        "MAP_ONLY_SURVIVAL_FIELDS_INVALID",
        "map_only_survival_contract",
    )
    triage = load_json(ROUND1_MANIFEST)
    source_rule = triage["survival_rule"]
    if (
        row.get("schema") != MAP_ONLY_SURVIVAL_SCHEMA
        or row.get("source_path") != repo_path(ROUND1_MANIFEST)
        or not path_hash_valid(row.get("source_path"), row.get("source_sha256"))
        or row.get("hard_rows") != source_rule["hard_rows"]
        or row.get("survives_if") != source_rule["survives_if"]
    ):
        error(errors, "MAP_ONLY_SURVIVAL_RULE_INVALID", "frozen all-PASS rule changed")
    change = exact_object(
        row.get("hypothetical_map_only_change"),
        MAP_ONLY_CHANGE_FIELDS,
        errors,
        "MAP_ONLY_CHANGE_SCOPE_INVALID",
        "hypothetical_map_only_change",
    )
    if (
        change.get("hypothetical_only") is not True
        or change.get("microscopic_map_after") != "ADMITTED"
        or not isinstance(change.get("preserved_fields"), list)
        or tuple(change.get("preserved_fields", [])) != MAP_ONLY_PRESERVED_FIELDS
    ):
        error(errors, "MAP_ONLY_CHANGE_SCOPE_INVALID", "non-map structures were changed")
    residual = row.get("residual_hard_rows")
    source_residual = {
        candidate_id: {
            row_id: triage["categorical_matrix"][candidate_id][row_id]
            for row_id in expected
        }
        for candidate_id, expected in MAP_ONLY_RESIDUAL_ORACLE.items()
    }
    if (
        not isinstance(residual, dict)
        or residual != MAP_ONLY_RESIDUAL_ORACLE
        or residual != source_residual
        or any(
            verdict == "PASS"
            for candidate_rows in source_residual.values()
            for verdict in candidate_rows.values()
        )
    ):
        error(errors, "MAP_ONLY_RESIDUAL_INVALID", "residual non-map hard rows changed")
    requirements = row.get("substantive_new_version_requirements")
    expected_requirements = {
        candidate_id: list(items)
        for candidate_id, items in MAP_ONLY_SUBSTANTIVE_REQUIREMENTS.items()
    }
    if requirements != expected_requirements:
        error(
            errors,
            "MAP_ONLY_SUBSTANTIVE_CHANGE_INVALID",
            "substantive non-map repair requirements changed",
        )
    if (
        row.get("map_only_survivor_ids") != []
        or row.get("all_pass_after_map_only") is not False
    ):
        error(
            errors,
            "MAP_ONLY_SURVIVOR_FALSE_PROMOTION",
            "map-only extension cannot be an all-PASS survivor",
        )
    if not is_nonempty_string(row.get("boundary")):
        error(errors, "MAP_ONLY_SURVIVAL_FIELDS_INVALID", "scope boundary missing")
    return {
        "valid": not errors,
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
    }


def map_only_survival_hostile_reports(
    valid: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    fixtures: dict[str, tuple[str, Callable[[dict[str, Any]], None]]] = {
        "hard_row_removed": (
            "MAP_ONLY_SURVIVAL_RULE_INVALID",
            lambda row: row["hard_rows"].pop(),
        ),
        "survival_rule_softened": (
            "MAP_ONLY_SURVIVAL_RULE_INVALID",
            lambda row: row.__setitem__("survives_if", "At least one hard row is PASS."),
        ),
        "m1_nonpass_promoted": (
            "MAP_ONLY_RESIDUAL_INVALID",
            lambda row: row["residual_hard_rows"][MICROSCOPIC_CANDIDATES[0]].__setitem__(
                "D01-SAME-REFERENCE", "PASS"
            ),
        ),
        "m2_nonpass_promoted": (
            "MAP_ONLY_RESIDUAL_INVALID",
            lambda row: row["residual_hard_rows"][MICROSCOPIC_CANDIDATES[1]].__setitem__(
                "D05-COMPACT-WINDING", "PASS"
            ),
        ),
        "m5_nonpass_promoted": (
            "MAP_ONLY_RESIDUAL_INVALID",
            lambda row: row["residual_hard_rows"][MICROSCOPIC_CANDIDATES[2]].__setitem__(
                "D04-SPEED-DISPERSION", "PASS"
            ),
        ),
        "preserved_regulator_removed": (
            "MAP_ONLY_CHANGE_SCOPE_INVALID",
            lambda row: row["hypothetical_map_only_change"]["preserved_fields"].remove(
                "regulator_and_limit_order"
            ),
        ),
        "map_only_survivor_fabricated": (
            "MAP_ONLY_SURVIVOR_FALSE_PROMOTION",
            lambda row: row["map_only_survivor_ids"].append(MICROSCOPIC_CANDIDATES[1]),
        ),
    }
    reports: dict[str, dict[str, Any]] = {}
    for name, (expected_code, mutation) in fixtures.items():
        hostile = copy.deepcopy(valid)
        mutation(hostile)
        report = validate_map_only_survival_contract(hostile)
        reports[name] = {
            "valid": report["valid"],
            "error_codes": report["error_codes"],
            "expected_error_code": expected_code,
            "expected_code_observed": expected_code in report["error_codes"],
        }
    return reports


def current_version_map_only_audit() -> dict[str, Any]:
    """Derive exact current maps and the stronger map-only survivor no-go."""

    admission = load_json(ADMISSION_FREEZE)
    contestants = admission["contestants"]
    microscopic = [
        row for row in contestants if row["candidate_id"] in MICROSCOPIC_CANDIDATES
    ]
    if [row["candidate_id"] for row in microscopic] != list(MICROSCOPIC_CANDIDATES):
        raise AssertionError("current microscopic candidate order changed")

    rows: list[dict[str, Any]] = []
    admitted: list[str] = []
    for frozen in microscopic:
        candidate_id = frozen["candidate_id"]
        path = REPO / frozen["path"]
        candidate = load_json(path)
        pin_matches = normalized_sha256(path) == frozen["normalized_sha256"]
        if candidate.get("candidate_id") != candidate_id or not pin_matches:
            raise AssertionError(f"current candidate pin mismatch: {candidate_id}")

        normalized_status = admission["normalized_candidate_contracts"][candidate_id][
            "microscopic_to_observable_map"
        ]
        if candidate_id == MICROSCOPIC_CANDIDATES[0]:
            direct_value = candidate["observable_map"][
                "map_to_round1_measured_observables"
            ]
            evidence = "observable_map.map_to_round1_measured_observables=false"
            map_only_admitted = direct_value is not False
        elif candidate_id == MICROSCOPIC_CANDIDATES[1]:
            direct_value = {
                "observable_map_key_present": "observable_map" in candidate,
                "physical_predictions": candidate["input_prediction_accounting"][
                    "physical_predictions"
                ],
                "holdout_prediction": candidate["input_prediction_accounting"][
                    "holdout_prediction"
                ],
                "normalized_status": normalized_status,
            }
            evidence = (
                "no observable_map; physical_predictions=[]; holdout_prediction=false; "
                "normalized status ABSENT/conditional-posthoc"
            )
            map_only_admitted = not (
                direct_value["observable_map_key_present"] is False
                and direct_value["physical_predictions"] == []
                and direct_value["holdout_prediction"] is False
                and normalized_status.startswith("ABSENT;")
            )
        else:
            direct_value = candidate["observable_map"]["map_to_measured_observables"]
            evidence = "observable_map.map_to_measured_observables=false"
            map_only_admitted = direct_value is not False

        if map_only_admitted:
            admitted.append(candidate_id)
        rows.append(
            {
                "candidate_id": candidate_id,
                "path": frozen["path"],
                "pinned_sha256": frozen["normalized_sha256"],
                "pin_matches": pin_matches,
                "normalized_map_status": normalized_status,
                "direct_value": direct_value,
                "exact_map_evidence": evidence,
                "map_only_admitted": map_only_admitted,
                "canonical_record_digest": canonical_digest(candidate),
            }
        )

    survival_contract = build_map_only_survival_contract()
    return {
        "closed_child_id": MAP_ONLY_CLOSED_CHILD,
        "source_freeze_path": repo_path(ADMISSION_FREEZE),
        "source_freeze_sha256": normalized_sha256(ADMISSION_FREEZE),
        "rows": rows,
        "admitted_candidate_ids": admitted,
        "cardinality": len(admitted),
        "negative_id": MAP_ONLY_NEGATIVE_ID,
        "same_version_repair_possible": False,
        "map_only_new_version_all_pass_repair_possible": False,
        "survival_contract": survival_contract,
        "boundary": (
            "Current maps are absent; even a hypothetical response-map-only new "
            "version preserving parent law/state data retains non-PASS hard rows."
        ),
    }


def exact_dispersion_fingerprint(mode_index: int = 3) -> dict[str, Any]:
    """Compute the ordered 48-component M2 finite-torus fingerprint exactly."""

    if not isinstance(mode_index, int) or isinstance(mode_index, bool) or mode_index < 1:
        raise ValueError("mode_index must be a positive integer")
    records: list[dict[str, Any]] = []
    component_vector: list[str] = []
    for node in product((-1, 1), repeat=3):
        preliminary: list[dict[str, Any]] = []
        for axis, sign in enumerate(node, start=1):
            d_plus = (mode_index * mode_index - (sign * mode_index + 1) ** 2) ** 2
            d_minus = (mode_index * mode_index - (sign * mode_index - 1) ** 2) ** 2
            symmetric = Fraction(d_plus + d_minus, 2)
            antisymmetric = Fraction(d_plus - d_minus, 2)
            preliminary.append(
                {
                    "axis": axis,
                    "sign": sign,
                    "d_plus": d_plus,
                    "d_minus": d_minus,
                    "S": symmetric,
                    "A": antisymmetric,
                }
            )
        mean_symmetric = sum(
            (row["S"] for row in preliminary), start=Fraction(0, 1)
        ) / 3
        for row in preliminary:
            sign = row["sign"]
            symmetric = row["S"]
            antisymmetric = row["A"]
            ratio_r = (
                antisymmetric
                / symmetric
                * Fraction(4 * mode_index * mode_index + 1, 4 * sign * mode_index)
            )
            ratio_u = symmetric / mean_symmetric
            records.append(
                {
                    "node": list(node),
                    "axis": row["axis"],
                    "d_plus": row["d_plus"],
                    "d_minus": row["d_minus"],
                    "S": fraction_text(symmetric),
                    "A": fraction_text(antisymmetric),
                    "S_bar": fraction_text(mean_symmetric),
                    "R": fraction_text(ratio_r),
                    "U": fraction_text(ratio_u),
                }
            )
            component_vector.extend((fraction_text(ratio_r), fraction_text(ratio_u)))
    return {
        "closed_child_id": FINGERPRINT_CLOSED_CHILD,
        "mode_index_fixture": mode_index,
        "node_count": len({tuple(row["node"]) for row in records}),
        "node_axis_record_count": len(records),
        "ordered_component_count": len(component_vector),
        "component_order": "lexicographic node, axis 1..3, R then U",
        "component_vector": component_vector,
        "all_components_exactly_one": all(value == "1" for value in component_vector),
        "records": records,
        "fingerprint_sha256": canonical_digest(component_vector),
        "physical_prediction": False,
    }


def retrospective_response_underdetermination() -> dict[str, Any]:
    """Give two exact completions of the absent M2 response-map slot."""

    t = Fraction(1, 8)
    doubled = 2 * t
    kappa = lambda value: value
    identity = lambda value: value
    square = lambda value: value * value
    identity_ratio = identity(kappa(doubled)) / identity(kappa(t))
    square_ratio = square(kappa(doubled)) / square(kappa(t))
    return {
        "current_candidate_id": MICROSCOPIC_CANDIDATES[1],
        "fixture_t": fraction_text(t),
        "same_stiffness_ratio": fraction_text(kappa(doubled) / kappa(t)),
        "completion_identity": {
            "definition": "R_1(kappa)=kappa/kappa_0",
            "exact_scale_ratio": fraction_text(identity_ratio),
            "exponent": 1,
        },
        "completion_square": {
            "definition": "R_2(kappa)=(kappa/kappa_0)^2",
            "exact_scale_ratio": fraction_text(square_ratio),
            "exponent": 2,
        },
        "unique_physical_exponent_derivable": False,
        "validation_credit": False,
        "admitted_map_created": False,
        "boundary": (
            "Logical completions of a missing response slot only; neither completion "
            "is an M2 candidate map or prediction."
        ),
    }


def validate_successor_design(design: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    root = exact_object(
        design,
        SUCCESSOR_DESIGN_FIELDS,
        errors,
        "SUCCESSOR_FIELDS_INVALID",
        "m2_v1_successor_design",
    )
    if (
        root.get("schema") != SUCCESSOR_DESIGN_SCHEMA
        or root.get("design_id")
        != "PA-M2-CI8-RS-DISPERSION-MAP-v1-SCHEMA-DESIGN"
        or root.get("hypothetical_candidate_id") != M2_SUCCESSOR_ID
        or root.get("parent_candidate_id") != MICROSCOPIC_CANDIDATES[1]
        or root.get("status") != "DESIGN_ONLY"
    ):
        error(errors, "SUCCESSOR_ID_INVALID", "successor design identity changed")
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
        error(errors, "SUCCESSOR_CREATION_FORBIDDEN", "no candidate record may be materialized")
    if root.get("admission_status") != "NOT_CREATED" or root.get(
        "microscopic_map_status"
    ) != "NOT_CREATED":
        error(errors, "SUCCESSOR_PROMOTION_FORBIDDEN", "design cannot admit a map")
    output_fields = (
        "prediction_status",
        "target_status",
        "freeze_status",
        "tag_status",
        "score_status",
        "selection_status",
    )
    if any(root.get(field) != "NOT_CREATED" for field in output_fields):
        error(errors, "SUCCESSOR_OUTPUT_FORBIDDEN", "design cannot contain downstream outputs")
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
        error(errors, "SUCCESSOR_REQUIRED_CONTRACT_INVALID", "response map must remain absent")
    if (
        required.get("candidate_neutral_estimand") != "REQUIRED_NOT_SUPPLIED"
        or required.get("limit_order") != "REQUIRED_NOT_SUPPLIED"
        or required.get("prospective_input_firewall")
        != "MUST_BE_FROZEN_BEFORE_TARGET_DISCLOSURE"
        or required.get("independent_verification") != "REQUIRED_NOT_SUPPLIED"
        or required.get("open_gate") != PHYSICAL_RESPONSE_GATE
    ):
        error(errors, "SUCCESSOR_REQUIRED_CONTRACT_INVALID", "required placeholders changed")
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
        error(errors, "SUCCESSOR_FINGERPRINT_INVALID", "fingerprint contract changed")
    budget = exact_object(
        required.get("error_budget"),
        SUCCESSOR_ERROR_FIELDS,
        errors,
        "SUCCESSOR_ERROR_BUDGET_INVALID",
        "error_budget",
    )
    if (
        budget.get("status") != "REQUIRED_NOT_SUPPLIED"
        or not isinstance(budget.get("terms"), list)
        or tuple(budget.get("terms", [])) != EXPECTED_ERROR_TERMS
        or not is_nonempty_string(budget.get("required_bound"))
        or not is_nonempty_string(budget.get("margin_condition"))
    ):
        error(errors, "SUCCESSOR_ERROR_BUDGET_INVALID", "error budget is incomplete")
    if not is_nonempty_string(root.get("no_overclaim")):
        error(errors, "SUCCESSOR_FIELDS_INVALID", "successor scope is empty")
    return {
        "valid": not errors,
        "error_codes": [row["code"] for row in errors],
        "errors": errors,
    }


def successor_hostile_reports(valid: dict[str, Any]) -> dict[str, dict[str, Any]]:
    fixtures: dict[str, tuple[str, Callable[[dict[str, Any]], None]]] = {
        "candidate_created": (
            "SUCCESSOR_CREATION_FORBIDDEN",
            lambda row: row.__setitem__("candidate_created", True),
        ),
        "candidate_manifest_materialized": (
            "SUCCESSOR_CREATION_FORBIDDEN",
            lambda row: row["candidate_manifest"].update(
                {"path": "strategy/fake-m2-v1.json", "sha256": "0" * 64}
            ),
        ),
        "admission_promoted": (
            "SUCCESSOR_PROMOTION_FORBIDDEN",
            lambda row: row.__setitem__("admission_status", "ADMITTED"),
        ),
        "map_promoted": (
            "SUCCESSOR_PROMOTION_FORBIDDEN",
            lambda row: row.__setitem__("microscopic_map_status", "ADMITTED"),
        ),
        "prediction_materialized": (
            "SUCCESSOR_OUTPUT_FORBIDDEN",
            lambda row: row.__setitem__("prediction_status", "PRESENT"),
        ),
        "target_materialized": (
            "SUCCESSOR_OUTPUT_FORBIDDEN",
            lambda row: row.__setitem__("target_status", "PRESENT"),
        ),
        "freeze_or_tag_materialized": (
            "SUCCESSOR_OUTPUT_FORBIDDEN",
            lambda row: row.update({"freeze_status": "FROZEN", "tag_status": "CREATED"}),
        ),
        "score_or_selection_materialized": (
            "SUCCESSOR_OUTPUT_FORBIDDEN",
            lambda row: row.update({"score_status": "SCORED", "selection_status": "SELECTED"}),
        ),
        "response_channel_smuggled": (
            "SUCCESSOR_REQUIRED_CONTRACT_INVALID",
            lambda row: row["required_contract"]["physical_response_channel"].update(
                {"status": "SUPPLIED", "map": "posthoc identity"}
            ),
        ),
        "error_budget_term_dropped": (
            "SUCCESSOR_ERROR_BUDGET_INVALID",
            lambda row: row["required_contract"]["error_budget"]["terms"].pop(),
        ),
        "fingerprint_dimension_changed": (
            "SUCCESSOR_FINGERPRINT_INVALID",
            lambda row: row["required_contract"]["finite_torus_fingerprint"].__setitem__(
                "ordered_component_count", 47
            ),
        ),
    }
    reports: dict[str, dict[str, Any]] = {}
    for name, (expected_code, mutation) in fixtures.items():
        hostile = copy.deepcopy(valid)
        mutation(hostile)
        report = validate_successor_design(hostile)
        reports[name] = {
            "expected_error_code": expected_code,
            "valid": report["valid"],
            "error_codes": report["error_codes"],
            "expected_code_observed": expected_code in report["error_codes"],
        }
    return reports


def linear_probe_curvature_nonidentifiability() -> dict[str, Any]:
    """Exact finite-beta and ground-curvature witness for a fixed linear probe.

    The free-energy sign convention is F=-beta^{-1} log Z and the helicity-like
    response is +V^{-1} d_J^2 F at J=0.  Therefore adding the scalar contact
    +(V/2)d(t)J^2 I shifts that response by +d(t); the conventional scalar
    susceptibility -V^{-1}d_J^2F shifts by -d(t).
    """

    volume = Fraction(7, 1)
    beta = Fraction(3, 2)
    step = Fraction(1, 5)
    d_left = Fraction(5, 7)
    d_right = Fraction(11, 7)
    delta_d = d_right - d_left
    gap = Fraction(4, 1)
    q_ground = Fraction(1, 1)
    q_excited = Fraction(-1, 1)

    def contact(d_value: Fraction, source: Fraction) -> Fraction:
        return volume * d_value * source * source / 2

    def central_second(values: tuple[Fraction, Fraction, Fraction]) -> Fraction:
        minus, zero, plus = values
        return (plus - 2 * zero + minus) / (step * step)

    # For any finite-dimensional H_J^0, the scalar contact commutes with it and
    # Z_d/Z_0=exp[-beta*V*d*J^2/2].  We verify the resulting free-energy
    # difference and its curvature entirely in exact Fraction arithmetic.
    finite_difference_values = (
        contact(delta_d, -step),
        contact(delta_d, Fraction(0, 1)),
        contact(delta_d, step),
    )
    finite_second = central_second(finite_difference_values)
    finite_normalized = finite_second / volume
    boltzmann_exponent_shift_at_step = -beta * contact(delta_d, step)

    def base_levels(source: Fraction) -> tuple[Fraction, Fraction]:
        return (-source * q_ground, gap - source * q_excited)

    def ground_energy(d_value: Fraction, source: Fraction) -> Fraction:
        levels = base_levels(source)
        return min(levels) + contact(d_value, source)

    sources = (-step, Fraction(0, 1), step)
    ground_branch_indices = [
        0 if base_levels(source)[0] < base_levels(source)[1] else 1
        for source in sources
    ]
    ground_left = central_second(tuple(ground_energy(d_left, j) for j in sources))
    ground_right = central_second(tuple(ground_energy(d_right, j) for j in sources))
    ground_left_normalized = ground_left / volume
    ground_right_normalized = ground_right / volume

    return {
        "closed_child_id": NEW_CLOSED_SUBGATES[0],
        "negative_id": LINEAR_PROBE_NEGATIVE_ID,
        "scope": "finite-dimensional regulated Lane-Q source family",
        "sign_convention": {
            "free_energy": "F_beta(J)=-beta^{-1} log Tr exp[-beta H(J)]",
            "helicity_like_response": "+V^{-1} d_J^2 F_beta(J)|J=0",
            "scalar_susceptibility": "-V^{-1} d_J^2 F_beta(J)|J=0",
            "contract_literal": HELICITY_SIGN_CONVENTION,
        },
        "fixture": {
            "volume": fraction_text(volume),
            "beta": fraction_text(beta),
            "source_step": fraction_text(step),
            "d_left": fraction_text(d_left),
            "d_right": fraction_text(d_right),
            "delta_d": fraction_text(delta_d),
            "two_level_gap": fraction_text(gap),
            "probe_diagonal": [fraction_text(q_ground), fraction_text(q_excited)],
        },
        "finite_beta": {
            "partition_factorization": (
                "Z_d(J)=exp[-beta*V*d*J^2/2]*Z_0(J)"
            ),
            "free_energy_difference_at_step": fraction_text(
                contact(delta_d, step)
            ),
            "boltzmann_exponent_shift_at_step": fraction_text(
                boltzmann_exponent_shift_at_step
            ),
            "central_second_difference": fraction_text(finite_second),
            "normalized_curvature_shift": fraction_text(finite_normalized),
            "expected_shift": fraction_text(delta_d),
        },
        "beta_infinity": {
            "ground_branch_indices_minus_zero_plus": ground_branch_indices,
            "branch_stable": ground_branch_indices == [0, 0, 0],
            "normalized_curvature_left": fraction_text(ground_left_normalized),
            "normalized_curvature_right": fraction_text(ground_right_normalized),
            "normalized_curvature_shift": fraction_text(
                ground_right_normalized - ground_left_normalized
            ),
            "expected_shift": fraction_text(delta_d),
        },
        "invariants": {
            "same_zero_source_hamiltonian": True,
            "same_first_source_derivative": True,
            "same_zero_source_state_and_spectrum": True,
            "same_finite_torus_fingerprint": True,
            "physical_response_identified": False,
            "admitted_candidate_created": False,
        },
        "finding": (
            "A fixed linear probe Q does not identify a second-order response: "
            "the target-blind quadratic contact d(t) shifts +V^-1 F'' and "
            "+V^-1 E0'' by exactly d(t), while leaving H(0), H'(0), the "
            "zero-source state/spectrum and the 48-component fingerprint fixed."
        ),
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
            and path_hash_valid(path_text, ref.get("sha256"))
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
        error(
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


def synthetic_physical_response_contract() -> dict[str, Any]:
    """Positive syntax fixture using existing artifacts only as fixture data."""

    primary = SCRIPT
    independent = INDEPENDENT_SCRIPT
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


def _positive_fraction(value: Any) -> Fraction | None:
    if (
        not isinstance(value, str)
        or len(value) > MAX_CANONICAL_RATIONAL_LENGTH
        or CANONICAL_POSITIVE_RATIONAL_RE.fullmatch(value) is None
    ):
        return None
    try:
        parsed = Fraction(value)
    except (ValueError, ZeroDivisionError):
        return None
    return parsed if parsed > 0 and fraction_text(parsed) == value else None


def _contract_positive_fraction(
    value: Any, errors: list[dict[str, str]], label: str,
) -> Fraction | None:
    parsed = _positive_fraction(value)
    if parsed is None:
        error(
            errors, "NUMERIC_LITERAL_INVALID",
            f"{label} must be a canonical reduced positive rational of at "
            f"most {MAX_CANONICAL_RATIONAL_LENGTH} characters",
        )
    return parsed
def validate_physical_response_contract(contract: Any) -> dict[str, Any]:
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
        error(
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
        error(
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
        error(
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
        error(
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
        error(
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
        error(
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
        error(
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
        error(
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
    estimand_margin = _contract_positive_fraction(
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
        error(
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
        error(
            errors, "PHYSICAL_CONTRACT_PREDICTION_INVALID",
            "prediction enum/placeholder/binding invalid",
        )

    budget = exact_object(
        root.get("error_budget"), PHYSICAL_ERROR_BUDGET_FIELDS, errors,
        "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID", "error_budget",
    )
    terms = budget.get("terms")
    if not isinstance(terms, list):
        error(
            errors, "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
            "error terms must be a list",
        )
        terms = []
    parsed_bounds: list[Fraction] = []
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
        parsed = _contract_positive_fraction(
            term.get("bound"), errors, f"error_budget.terms[{index}].bound"
        )
        if parsed is None:
            error(
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
            error(
                errors, "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
                "error result_key missing from bound run",
            )
        if not _nonplaceholder_text(term.get("uniform_domain")):
            error(
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
    total = _contract_positive_fraction(
        budget.get("total_bound"), errors, "error_budget.total_bound"
    )
    margin = _contract_positive_fraction(
        budget.get("acceptance_margin"), errors, "error_budget.acceptance_margin"
    )
    proof_refs = budget.get("proof_refs")
    proof_paths: list[Any] = []
    if not isinstance(proof_refs, list) or len(proof_refs) < 2:
        error(
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
        or total != sum(parsed_bounds, Fraction(0, 1))
        or margin != estimand_margin
        or budget.get("strict_margin") is not True
        or not total < margin
        or not _unique_nonplaceholder_string_list(proof_paths)
    ):
        error(
            errors, "PHYSICAL_CONTRACT_ERROR_BUDGET_INVALID",
            "error evidence/total/margin contract invalid",
        )

    ledger = root.get("common_input_ledger")
    if not isinstance(ledger, list) or not ledger:
        error(
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
            error(
                errors, "PHYSICAL_CONTRACT_INPUT_LEDGER_INVALID",
                "input row/source invalid",
            )
    if (
        not _unique_nonplaceholder_string_list(input_ids)
        or not _unique_nonplaceholder_string_list(source_ids)
    ):
        error(
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
            error(
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
        error(
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
        error(
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
        error(
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
        error(
            errors, "PHYSICAL_CONTRACT_FIELDS_INVALID",
            "syntax/semantic/external boundary absent",
        )
    return {
        "valid": not errors,
        "error_codes": [row["code"] for row in errors],
        "errors": errors,
    }


def physical_response_contract_hostile_reports(
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
        report = validate_physical_response_contract(hostile)
        expected = PHYSICAL_CONTRACT_HOSTILE_CODES[name]
        reports[name] = {
            "valid": report["valid"],
            "error_codes": report["error_codes"],
            "expected_error_code": expected,
            "expected_code_observed": expected in report["error_codes"],
        }
    return reports


def physical_response_contract_reordered_metamorphic(
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
    return validate_physical_response_contract(reordered)


def physical_response_contract_fuzz_reports(
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
            report = validate_physical_response_contract(hostile)
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
    """Require additive v1.2 authorities, while supporting assembly staging."""

    missing: list[str] = []
    gates_text = GATE_REGISTRY.read_text(encoding="utf-8")
    for identifier in NEW_CLOSED_SUBGATES:
        section = section_for(gates_text, identifier)
        if not section:
            missing.append(f"claims/GATES.md#{identifier}")
        else:
            audit.check(
                f"new closed gate {identifier}",
                "**Status:** CLOSED" in section,
                "CLOSED" if "**Status:** CLOSED" in section else section[:160],
                "CLOSED",
                "formal_authority",
            )
    section = section_for(gates_text, PHYSICAL_RESPONSE_GATE)
    if not section:
        missing.append(f"claims/GATES.md#{PHYSICAL_RESPONSE_GATE}")
    else:
        audit.check(
            "physical response gate open",
            "**Status:** OPEN" in section,
            "OPEN" if "**Status:** OPEN" in section else section[:160],
            "OPEN",
            "formal_authority",
        )

    negative_text = NEGATIVE_REGISTRY.read_text(encoding="utf-8")
    for identifier in NEW_NEGATIVE_IDS:
        if identifier not in negative_text:
            missing.append(f"negative-results/registry.md#{identifier}")
        else:
            audit.check(
                f"new negative {identifier}",
                negative_text.count(identifier) >= 1,
                negative_text.count(identifier),
                ">=1",
                "formal_authority",
            )

    result_text = RESULTS_LEDGER.read_text(encoding="utf-8")
    if f"{RESULT_NUMBER} {RESULT_VERSION}" not in result_text or RESULT_ID not in result_text:
        missing.append(f"RESULTS-LEDGER.md#{RESULT_NUMBER}-{RESULT_VERSION}")
    else:
        audit.check(
            "v1.2 result authority",
            f"{RESULT_NUMBER} {RESULT_VERSION}" in result_text and RESULT_ID in result_text,
            True,
            True,
            "formal_authority",
        )

    exploration = exploration_record(EXPLORATION_ID)
    if exploration is None:
        missing.append(f"explorations/log.jsonl#{EXPLORATION_ID}")
    else:
        audit.check(
            "v1.2 exploration result binding",
            RESULT_NUMBER in exploration.get("formal_refs", {}).get("results", []),
            exploration.get("formal_refs", {}).get("results", []),
            f"contains {RESULT_NUMBER}",
            "formal_authority",
        )
        audit.check(
            "v1.2 exploration negative binding",
            set(NEW_NEGATIVE_IDS)
            <= set(exploration.get("formal_refs", {}).get("negatives", [])),
            exploration.get("formal_refs", {}).get("negatives", []),
            list(NEW_NEGATIVE_IDS),
            "formal_authority",
        )
        required_gates = set(NEW_CLOSED_SUBGATES + (PARENT_GATE, PHYSICAL_RESPONSE_GATE))
        audit.check(
            "v1.2 exploration gate binding",
            required_gates <= set(exploration.get("gate_ids", [])),
            exploration.get("gate_ids", []),
            sorted(required_gates),
            "formal_authority",
        )

    for identifier in PRIOR_EXPLORATION_IDS:
        prior = exploration_record(identifier)
        audit.check(
            f"retained exploration {identifier}",
            prior is not None,
            prior is not None,
            True,
            "formal_authority",
        )
    status = "COMPLETE" if not missing else ("STAGED" if staged else "INCOMPLETE")
    return {"status": status, "missing": missing, "staged": staged}


def current_tree_state() -> dict[str, Any]:
    round1 = git_show_json(AUDITED_COMMIT, ROUND1_MANIFEST)
    admission = git_show_json(AUDITED_COMMIT, ADMISSION_FREEZE)
    m1 = git_show_json(AUDITED_COMMIT, M1_MANIFEST)
    m2 = git_show_json(AUDITED_COMMIT, M2_MANIFEST)
    m5 = git_show_json(AUDITED_COMMIT, M5_MANIFEST)

    records = sorted(
        path
        for path in git_output(
            "ls-tree", "-r", "--name-only", AUDITED_COMMIT, "predictions/freezes"
        )
        if not path.endswith("/.gitkeep")
    )
    live_tags = sorted(git_output("tag", "--list", "freeze/*"))
    contestants = admission["contestants"]
    contestant_ids = [row["candidate_id"] for row in contestants]
    normalized = admission["normalized_candidate_contracts"]
    survivors = list(round1["round1_verdict"]["admitted_microscopic_survivors"])

    m1_map = m1["observable_map"]["map_to_round1_measured_observables"]
    m1_prediction = m1["input_prediction_accounting"][
        "declared_non_fitting_validation_prediction"
    ]
    m2_predictions = list(m2["input_prediction_accounting"]["physical_predictions"])
    m2_holdout = m2["input_prediction_accounting"]["holdout_prediction"]
    m5_map = m5["observable_map"]["map_to_measured_observables"]
    m5_holdout = m5["input_prediction_accounting"]["holdout_prediction"]

    blockers = []
    if not records:
        blockers.append("NO_MACHINE_FREEZE_RECORD")
    if not survivors:
        blockers.append("NO_ADMITTED_MICROSCOPIC_SURVIVOR")
    if m1_map is False and m1_prediction is False:
        blockers.append("M1_MAP_AND_PREDICTION_ABSENT")
    if not m2_predictions and m2_holdout is False:
        blockers.append("M2_PHYSICAL_PREDICTION_AND_HOLDOUT_ABSENT")
    if m5_map is False and m5_holdout is False:
        blockers.append("M5_MAP_AND_HOLDOUT_ABSENT")
    if admission["completeness"]["per_parameter_common_input_ledger_complete"] is False:
        blockers.append("PER_PARAMETER_COMMON_INPUT_LEDGER_INCOMPLETE")
    if admission["completeness"]["visible_non_fitting_prediction_frozen"] is False:
        blockers.append("PROSPECTIVE_PREDICTION_NOT_FROZEN")

    return {
        "audited_commit": AUDITED_COMMIT,
        "current_head": git_output("rev-parse", "HEAD")[0],
        "freeze_record_count": len(records),
        "freeze_records": records,
        "local_freeze_tag_observation": {
            "count": len(live_tags),
            "tags": live_tags,
            "scope": "live local freeze/* refs at verification time",
            "load_bearing": False,
        },
        "contestant_ids": contestant_ids,
        "normalized_map_status": {
            candidate_id: normalized[candidate_id]["microscopic_to_observable_map"]
            for candidate_id in MICROSCOPIC_CANDIDATES
        },
        "admitted_microscopic_survivor_count": len(survivors),
        "admitted_microscopic_survivors": survivors,
        "M1": {
            "map_to_round1_measured_observables": m1_map,
            "declared_non_fitting_validation_prediction": m1_prediction,
        },
        "M2": {
            "physical_predictions": m2_predictions,
            "holdout_prediction": m2_holdout,
        },
        "M5": {
            "map_to_measured_observables": m5_map,
            "holdout_prediction": m5_holdout,
        },
        "canonical_candidate_semantic_completeness": admission["completeness"][
            "canonical_candidate_semantic_completeness"
        ],
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


def run_audit(
    freeze_manifest: Path | None = None, *, staged: bool = False
) -> dict[str, Any]:
    audit = Audit()
    state = current_tree_state()
    authority = load_json(AUTHORITY_MANIFEST)
    certificate_text = AUTHORITY_CERTIFICATE.read_text(encoding="utf-8")
    map_only = current_version_map_only_audit()
    map_only_survival = map_only["survival_contract"]
    map_only_survival_report = validate_map_only_survival_contract(map_only_survival)
    map_only_survival_hostile = map_only_survival_hostile_reports(map_only_survival)
    fingerprint = exact_dispersion_fingerprint()
    underdetermination = retrospective_response_underdetermination()
    successor_design = authority["m2_v1_successor_design"]
    successor_report = validate_successor_design(successor_design)
    successor_hostile = successor_hostile_reports(successor_design)
    linear_probe = linear_probe_curvature_nonidentifiability()
    physical_contract_fixture = synthetic_physical_response_contract()
    physical_contract_report = validate_physical_response_contract(
        physical_contract_fixture
    )
    physical_contract_hostile = physical_response_contract_hostile_reports(
        physical_contract_fixture
    )
    physical_contract_reordered = physical_response_contract_reordered_metamorphic(
        physical_contract_fixture
    )
    physical_contract_fuzz = physical_response_contract_fuzz_reports(
        physical_contract_fixture
    )

    audit.check(
        "canonical contestant order",
        tuple(state["contestant_ids"]) == EXPECTED_CANDIDATES,
        state["contestant_ids"],
        EXPECTED_CANDIDATES,
        "current_tree",
    )
    audit.check("machine freeze records absent", state["freeze_record_count"] == 0, state["freeze_record_count"], 0, "current_tree")
    audit.check(
        "live tag observation is non-load-bearing",
        state["local_freeze_tag_observation"]["load_bearing"] is False,
        state["local_freeze_tag_observation"],
        "informational only",
        "current_tree",
    )
    audit.check("admitted survivors absent", state["admitted_microscopic_survivor_count"] == 0, state["admitted_microscopic_survivor_count"], 0, "current_tree")
    audit.check("M1 map absent", state["M1"]["map_to_round1_measured_observables"] is False, state["M1"], "map false", "current_tree")
    audit.check("M1 prediction absent", state["M1"]["declared_non_fitting_validation_prediction"] is False, state["M1"], "prediction false", "current_tree")
    audit.check("M2 physical predictions absent", state["M2"]["physical_predictions"] == [], state["M2"], "empty", "current_tree")
    audit.check("M2 holdout absent", state["M2"]["holdout_prediction"] is False, state["M2"], "false", "current_tree")
    audit.check("M5 map absent", state["M5"]["map_to_measured_observables"] is False, state["M5"], "false", "current_tree")
    audit.check("M5 holdout absent", state["M5"]["holdout_prediction"] is False, state["M5"], "false", "current_tree")
    audit.check("M1 normalized map status absent", state["normalized_map_status"][MICROSCOPIC_CANDIDATES[0]] == "ABSENT", state["normalized_map_status"][MICROSCOPIC_CANDIDATES[0]], "ABSENT", "current_tree")
    audit.check("M2 normalized map status absent", state["normalized_map_status"][MICROSCOPIC_CANDIDATES[1]].startswith("ABSENT;"), state["normalized_map_status"][MICROSCOPIC_CANDIDATES[1]], "ABSENT; ...", "current_tree")
    audit.check("M5 normalized map status absent", state["normalized_map_status"][MICROSCOPIC_CANDIDATES[2]] == "ABSENT", state["normalized_map_status"][MICROSCOPIC_CANDIDATES[2]], "ABSENT", "current_tree")
    audit.check("candidate semantic completeness open", state["canonical_candidate_semantic_completeness"] is False, state["canonical_candidate_semantic_completeness"], False, "current_tree")
    audit.check("per-parameter ledger open", state["per_parameter_common_input_ledger_complete"] is False, state["per_parameter_common_input_ledger_complete"], False, "current_tree")
    audit.check("prospective prediction open", state["prospective_prediction_frozen"] is False, state["prospective_prediction_frozen"], False, "current_tree")
    audit.check("parent freeze gate open", state["parent_freeze_gate_closed"] is False, state["parent_freeze_gate_closed"], False, "current_tree")
    audit.check("Pre-A exit open", state["pre_a_exit_conditions_met"] is False, state["pre_a_exit_conditions_met"], False, "current_tree")
    audit.check("current tree not freeze ready", state["actual_freeze_ready"] is False, state["actual_freeze_ready"], False, "current_tree")
    audit.check("current blockers exact", tuple(state["blockers"]) == EXPECTED_BLOCKERS, state["blockers"], "exact seven stable blockers", "current_tree")

    audit.check("current-version map set empty", map_only["admitted_candidate_ids"] == [] and map_only["cardinality"] == 0, map_only["admitted_candidate_ids"], [], "map_only")
    audit.check("current-version candidate pins exact", all(row["pin_matches"] for row in map_only["rows"]), [row["pin_matches"] for row in map_only["rows"]], [True, True, True], "map_only")
    audit.check("current-version rows derived", [row["candidate_id"] for row in map_only["rows"]] == list(MICROSCOPIC_CANDIDATES), [row["candidate_id"] for row in map_only["rows"]], list(MICROSCOPIC_CANDIDATES), "map_only")
    audit.check("same-version repair rejected", map_only["same_version_repair_possible"] is False and map_only["negative_id"] == MAP_ONLY_NEGATIVE_ID, map_only, "new version required", "map_only")
    audit.check("frozen all-PASS survival contract valid", map_only_survival_report["valid"], map_only_survival_report, "valid", "map_only")
    audit.check("frozen survival rule exact", map_only_survival["hard_rows"] == load_json(ROUND1_MANIFEST)["survival_rule"]["hard_rows"] and map_only_survival["survives_if"] == "Every hard row is PASS.", map_only_survival["survives_if"], "Every hard row is PASS.", "map_only")
    audit.check("map-independent residual rows exact", map_only_survival["residual_hard_rows"] == MAP_ONLY_RESIDUAL_ORACLE, map_only_survival["residual_hard_rows"], MAP_ONLY_RESIDUAL_ORACLE, "map_only")
    audit.check("map-only new version still has no survivor", map_only["map_only_new_version_all_pass_repair_possible"] is False and map_only_survival["map_only_survivor_ids"] == [] and map_only_survival["all_pass_after_map_only"] is False, map_only_survival, "empty survivor set", "map_only")
    audit.check("non-map repairs require substantive new version", map_only_survival["substantive_new_version_requirements"] == {key: list(value) for key, value in MAP_ONLY_SUBSTANTIVE_REQUIREMENTS.items()}, map_only_survival["substantive_new_version_requirements"], MAP_ONLY_SUBSTANTIVE_REQUIREMENTS, "map_only")
    audit.check("fingerprint node count", fingerprint["node_count"] == 8, fingerprint["node_count"], 8, "fingerprint")
    audit.check("fingerprint node-axis count", fingerprint["node_axis_record_count"] == 24, fingerprint["node_axis_record_count"], 24, "fingerprint")
    audit.check("fingerprint dimension", fingerprint["ordered_component_count"] == 48, fingerprint["ordered_component_count"], 48, "fingerprint")
    audit.check("fingerprint all exact ones", fingerprint["all_components_exactly_one"] and fingerprint["component_vector"] == ["1"] * 48, fingerprint["component_vector"], ["1"] * 48, "fingerprint")
    for mode_index in (1, 2, 3, 5):
        mode_fingerprint = exact_dispersion_fingerprint(mode_index)
        audit.check(f"fingerprint exact mode m={mode_index}", mode_fingerprint["all_components_exactly_one"] and mode_fingerprint["ordered_component_count"] == 48, [mode_fingerprint["all_components_exactly_one"], mode_fingerprint["ordered_component_count"]], [True, 48], "fingerprint")
    audit.check("retrospective response exponents differ", underdetermination["completion_identity"]["exponent"] == 1 and underdetermination["completion_square"]["exponent"] == 2, underdetermination, "1 versus 2", "underdetermination")
    audit.check("retrospective exact scale ratios", [underdetermination["completion_identity"]["exact_scale_ratio"], underdetermination["completion_square"]["exact_scale_ratio"]] == ["2", "4"], underdetermination, ["2", "4"], "underdetermination")
    audit.check("retrospective map remains absent", underdetermination["admitted_map_created"] is False and underdetermination["validation_credit"] is False, underdetermination, "no map or credit", "underdetermination")
    audit.check("successor design valid", successor_report["valid"], successor_report, "valid DESIGN_ONLY schema", "successor")
    audit.check("successor exact hypothetical ID", successor_design["hypothetical_candidate_id"] == M2_SUCCESSOR_ID and successor_design["status"] == "DESIGN_ONLY", [successor_design["hypothetical_candidate_id"], successor_design["status"]], [M2_SUCCESSOR_ID, "DESIGN_ONLY"], "successor")
    audit.check("successor creates nothing", successor_design["candidate_created"] is False and all(successor_design[field] == "NOT_CREATED" for field in ("admission_status", "microscopic_map_status", "prediction_status", "target_status", "freeze_status", "tag_status", "score_status", "selection_status")), successor_design, "all creation/promotion states absent", "successor")
    audit.check("linear-probe sign convention exact", linear_probe["sign_convention"]["contract_literal"] == HELICITY_SIGN_CONVENTION, linear_probe["sign_convention"], HELICITY_SIGN_CONVENTION, "linear_probe")
    audit.check("finite-beta contact factor exact", linear_probe["finite_beta"]["free_energy_difference_at_step"] == "3/25" and linear_probe["finite_beta"]["boltzmann_exponent_shift_at_step"] == "-9/50", linear_probe["finite_beta"], {"free": "3/25", "exponent": "-9/50"}, "linear_probe")
    audit.check("finite-beta curvature shift exact", linear_probe["finite_beta"]["normalized_curvature_shift"] == linear_probe["finite_beta"]["expected_shift"] == "6/7", linear_probe["finite_beta"], "6/7", "linear_probe")
    audit.check("ground branch stable", linear_probe["beta_infinity"]["branch_stable"] and linear_probe["beta_infinity"]["ground_branch_indices_minus_zero_plus"] == [0, 0, 0], linear_probe["beta_infinity"], [0, 0, 0], "linear_probe")
    audit.check("ground curvatures exact", [linear_probe["beta_infinity"]["normalized_curvature_left"], linear_probe["beta_infinity"]["normalized_curvature_right"], linear_probe["beta_infinity"]["normalized_curvature_shift"]] == ["5/7", "11/7", "6/7"], linear_probe["beta_infinity"], ["5/7", "11/7", "6/7"], "linear_probe")
    audit.check("linear probe leaves zero and first source data fixed", linear_probe["invariants"]["same_zero_source_hamiltonian"] and linear_probe["invariants"]["same_first_source_derivative"] and linear_probe["invariants"]["same_finite_torus_fingerprint"], linear_probe["invariants"], "all true", "linear_probe")
    audit.check("linear probe creates no physical map", linear_probe["invariants"]["physical_response_identified"] is False and linear_probe["invariants"]["admitted_candidate_created"] is False, linear_probe["invariants"], "no physical map/candidate", "linear_probe")
    audit.check("minimum physical-response contract fixture valid", physical_contract_report["valid"], physical_contract_report, "valid schema fixture", "physical_contract")
    audit.check("minimum contract remains fixture-only", physical_contract_fixture["fixture_only"] is True and physical_contract_fixture["candidate_created"] is False, [physical_contract_fixture["fixture_only"], physical_contract_fixture["candidate_created"]], [True, False], "physical_contract")
    audit.check("minimum contract six-term error sum exact", physical_contract_fixture["error_budget"]["total_bound"] == "3/50" and physical_contract_fixture["error_budget"]["acceptance_margin"] == "1/10" and physical_contract_fixture["error_budget"]["strict_margin"] is True, physical_contract_fixture["error_budget"], "3/50 < 1/10", "physical_contract")
    audit.check("minimum contract all ten synthetic rows PASS", len(physical_contract_fixture["hard_row_rerun"]["rows"]) == len(HARD_ROWS) and set(physical_contract_fixture["hard_row_rerun"]["rows"]) == set(HARD_ROWS) and all(value == "PASS" for value in physical_contract_fixture["hard_row_rerun"]["rows"].values()), physical_contract_fixture["hard_row_rerun"], "exact ten PASS fixture rows", "physical_contract")
    audit.check("minimum contract reordered positive metamorphic", physical_contract_reordered["valid"], physical_contract_reordered, "valid after order-insensitive reordering", "physical_contract")
    audit.check("minimum contract deterministic fuzz fail closed", physical_contract_fuzz["all_rejected_without_exception"] and physical_contract_fuzz["case_count"] >= 20, physical_contract_fuzz, "all malformed cases rejected without exception", "physical_contract")

    gate_text = GATE_REGISTRY.read_text(encoding="utf-8")
    prediction_text = PREDICTION_LEDGER.read_text(encoding="utf-8")
    audit.check("authority result ID", authority["result_id"] == RESULT_ID, authority["result_id"], RESULT_ID, "authority")
    audit.check("authority result number", authority["result_number"] == RESULT_NUMBER, authority["result_number"], RESULT_NUMBER, "authority")
    audit.check("authority result version", authority["result_version"] == RESULT_VERSION, authority["result_version"], RESULT_VERSION, "authority")
    audit.check("authority exploration", authority["exploration_id"] == EXPLORATION_ID, authority["exploration_id"], EXPLORATION_ID, "authority")
    audit.check("authority retained explorations", tuple(authority["prior_exploration_ids"]) == PRIOR_EXPLORATION_IDS, authority["prior_exploration_ids"], PRIOR_EXPLORATION_IDS, "authority")
    audit.check("authority task", authority["task_id"] == "T-054", authority["task_id"], "T-054", "authority")
    audit.check("authority claim context", authority["claim_ids"] == ["C6-SPACETIME-SIGNATURE"], authority["claim_ids"], ["C6-SPACETIME-SIGNATURE"], "authority")
    audit.check("authority claim nonbearing", authority["claim_bearing"] is False, authority["claim_bearing"], False, "authority")
    audit.check("authority negative IDs", tuple(authority["negative_ids"]) == NEGATIVE_IDS, authority["negative_ids"], NEGATIVE_IDS, "authority")
    audit.check("authority new negative IDs", tuple(authority["new_negative_ids"]) == NEW_NEGATIVE_IDS, authority["new_negative_ids"], NEW_NEGATIVE_IDS, "authority")
    audit.check("authority reused negatives", tuple(authority["reused_negative_ids"]) == REUSED_NEGATIVE_IDS, authority["reused_negative_ids"], REUSED_NEGATIVE_IDS, "authority")
    audit.check("authority closed subgates", tuple(authority["closed_subgates"]) == CLOSED_SUBGATES, authority["closed_subgates"], CLOSED_SUBGATES, "authority")
    audit.check("authority open gates", tuple(authority["open_gates"]) == OPEN_GATES, authority["open_gates"], OPEN_GATES, "authority")
    audit.check("authority audited commit", authority["audited_checkpoint"]["commit"] == AUDITED_COMMIT, authority["audited_checkpoint"]["commit"], AUDITED_COMMIT, "authority")
    audit.check("authority exact stable zero counts", [authority["audited_checkpoint"][key] for key in ("freeze_records", "admitted_microscopic_survivors")] == [0, 0], authority["audited_checkpoint"], [0, 0], "authority")
    audit.check("authority live tag observation nonbinding", authority["initial_local_observation"]["load_bearing"] is False, authority["initial_local_observation"], "informational only", "authority")
    audit.check("authority target fields exact", tuple(authority["freeze_schema"]["target_fields"]) == TARGET_FIELDS, authority["freeze_schema"]["target_fields"], TARGET_FIELDS, "authority")
    audit.check("authority commitment fields exact", tuple(authority["freeze_schema"]["commitment_fields"]) == COMMITMENT_FIELDS, authority["freeze_schema"]["commitment_fields"], COMMITMENT_FIELDS, "authority")
    audit.check("authority disclosure fields exact", tuple(authority["freeze_schema"]["disclosure_fields"]) == DISCLOSURE_FIELDS, authority["freeze_schema"]["disclosure_fields"], DISCLOSURE_FIELDS, "authority")
    audit.check("authority prediction fields exact", tuple(authority["freeze_schema"]["prediction_fields"]) == PREDICTION_FIELDS, authority["freeze_schema"]["prediction_fields"], PREDICTION_FIELDS, "authority")
    audit.check("authority allowed-input fields exact", tuple(authority["freeze_schema"]["allowed_input_fields"]) == ALLOWED_INPUT_FIELDS, authority["freeze_schema"]["allowed_input_fields"], ALLOWED_INPUT_FIELDS, "authority")
    audit.check("authority robustness fields exact", tuple(authority["freeze_schema"]["robustness_fields"]) == ROBUSTNESS_FIELDS, authority["freeze_schema"]["robustness_fields"], ROBUSTNESS_FIELDS, "authority")
    audit.check("authority protocol status", authority["status"].startswith("R-168 v1.2 THEOREM-READY"), authority["status"], "R-168 v1.2 THEOREM-READY ...", "authority")
    audit.check("authority map-only child", authority["current_version_map_only_audit"]["closed_child_id"] == MAP_ONLY_CLOSED_CHILD and authority["current_version_map_only_audit"]["admitted_candidate_ids"] == [], authority["current_version_map_only_audit"], MAP_ONLY_CLOSED_CHILD, "authority")
    audit.check("authority frozen survival rule", authority["current_version_map_only_audit"]["frozen_survival_rule"]["hard_rows"] == map_only_survival["hard_rows"] and authority["current_version_map_only_audit"]["map_independent_or_non_map_only_residual_hard_rows"] == MAP_ONLY_RESIDUAL_ORACLE and authority["current_version_map_only_audit"]["map_only_new_version_survivor_ids"] == [], authority["current_version_map_only_audit"]["map_independent_or_non_map_only_residual_hard_rows"], MAP_ONLY_RESIDUAL_ORACLE, "authority")
    audit.check("authority fingerprint child", authority["m2_finite_torus_dispersion_fingerprint"]["closed_child_id"] == FINGERPRINT_CLOSED_CHILD and authority["m2_finite_torus_dispersion_fingerprint"]["expected_component_vector"] == ["1"] * 48, authority["m2_finite_torus_dispersion_fingerprint"]["ordered_component_count"], 48, "authority")
    audit.check("authority successor gate", authority["route_status"]["m2_successor_gate"] == PHYSICAL_RESPONSE_GATE, authority["route_status"]["m2_successor_gate"], PHYSICAL_RESPONSE_GATE, "authority")
    authority_linear = authority["m2_linear_probe_second_order_response_nonidentifiability"]
    audit.check("authority linear-probe child", authority_linear["closed_child_id"] == NEW_CLOSED_SUBGATES[0] and authority_linear["negative_id"] == LINEAR_PROBE_NEGATIVE_ID, authority_linear, [NEW_CLOSED_SUBGATES[0], LINEAR_PROBE_NEGATIVE_ID], "authority")
    audit.check("authority linear-probe exact fixture", authority_linear["fraction_fixture"]["normalized_curvature_shift"] == "6/7" and authority_linear["sign_convention"]["helicity_like_response"].startswith("+V^-1"), authority_linear["fraction_fixture"], "6/7 and positive helicity curvature", "authority")
    authority_contract = authority["m2_physical_response_successor_minimum_contract_schema"]
    audit.check("authority minimum-contract schema", authority_contract["closed_child_id"] == NEW_CLOSED_SUBGATES[1] and authority_contract["schema"] == PHYSICAL_CONTRACT_SCHEMA and tuple(authority_contract["root_fields"]) == PHYSICAL_CONTRACT_FIELDS and tuple(authority_contract["artifact_ref_fields"]) == ARTIFACT_REF_FIELDS, authority_contract, PHYSICAL_CONTRACT_SCHEMA, "authority")
    audit.check("authority minimum-contract error terms", tuple(authority_contract["error_terms"]) == EXPECTED_ERROR_TERMS and tuple(authority_contract["hard_rows"]) == HARD_ROWS and tuple(authority_contract["mandatory_substantive_changes"]) == MANDATORY_SUBSTANTIVE_CHANGES, authority_contract, {"errors": EXPECTED_ERROR_TERMS, "rows": HARD_ROWS}, "authority")
    audit.check("authority syntax-semantic-external boundary", authority_contract["validation_boundary"]["syntax_and_binding"] == "VALIDATED" and authority_contract["validation_boundary"]["physical_semantics"] == "NOT_VALIDATED" and authority_contract["validation_boundary"]["external_prospective_freeze"] == "NOT_SUPPLIED", authority_contract["validation_boundary"], {"syntax_and_binding": "VALIDATED", "physical_semantics": "NOT_VALIDATED", "external_prospective_freeze": "NOT_SUPPLIED"}, "authority")
    audit.check("certificate result linkage", RESULT_NUMBER in certificate_text and RESULT_ID in certificate_text and EXPLORATION_ID in certificate_text and all(item in certificate_text for item in PRIOR_EXPLORATION_IDS), True, True, "authority")
    audit.check("certificate v1.2 identities", all(item in certificate_text for item in (*NEW_CLOSED_SUBGATES, *NEW_NEGATIVE_IDS, PHYSICAL_RESPONSE_GATE, M2_SUCCESSOR_ID, PHYSICAL_CONTRACT_SCHEMA)), True, True, "authority")
    audit.check("certificate fingerprint formula", "R_{s,i}" in certificate_text and "U_{s,i}" in certificate_text and "8*3*2=48" in certificate_text, True, True, "authority")
    audit.check("certificate exact stable empty counts", "N_{\\rm records}=0" in certificate_text and "N_{\\rm admitted\\ microscopic\\ survivors}=0" in certificate_text, True, True, "authority")
    audit.check("certificate live-tag boundary", "non-load-bearing live observation" in certificate_text and "future legitimate freeze tag" in certificate_text, True, True, "authority")
    audit.check("certificate temporal order", "t_{\\rm custodian}" in certificate_text and "t_{\\rm public\\ freeze}" in certificate_text and "t_{\\rm disclosure}" in certificate_text, True, True, "authority")
    audit.check("certificate no-overclaim", "No cryptographic custodian-signature check" in certificate_text and "physical Sector A or Pre-A" in certificate_text, True, True, "authority")
    audit.check("audited commit exact", state["audited_commit"] == authority["audited_checkpoint"]["commit"], state["audited_commit"], authority["audited_checkpoint"]["commit"], "authority")
    audit.check("audited commit is ancestor", git_is_ancestor(state["audited_commit"], state["current_head"]), [state["audited_commit"], state["current_head"]], "audited commit ancestor of current HEAD", "authority")
    audit.check("parent gate authority present", PARENT_GATE in gate_text and "microscopic observable map" in gate_text, PARENT_GATE, "gate plus map", "authority")
    audit.check("freeze record path policy present", "predictions/freezes/<PRED-ID>-freeze.md" in prediction_text, True, True, "authority")
    audit.check("freeze tag policy present", "freeze/<PRED-ID>/v<N>" in prediction_text, True, True, "authority")
    audit.check("posthoc invalidation policy present", "post-hoc comparison can never be promoted" in prediction_text, True, True, "authority")

    valid_fixture = synthetic_valid_manifest()
    valid_report = validate_freeze_manifest(valid_fixture, allow_fixture=True)
    non_string_root_fixture = copy.deepcopy(valid_fixture)
    non_string_root_fixture[1] = "unexpected"
    non_string_root_report = validate_freeze_manifest(
        non_string_root_fixture, allow_fixture=True
    )
    audit.check(
        "non-string freeze root key rejected without exception",
        non_string_root_report["valid"] is False
        and "ROOT_FIELDS_EXTRA" in non_string_root_report["error_codes"],
        non_string_root_report,
        "structured ROOT_FIELDS_EXTRA rejection",
        "schema",
    )
    promoted_fixture = copy.deepcopy(valid_fixture)
    promoted_fixture["fixture_only"] = False
    promoted_report = validate_freeze_manifest(promoted_fixture, allow_fixture=False)
    audit.check("synthetic schema fixture valid", valid_report["valid"], valid_report, "valid", "schema")
    audit.check("root fields exact", tuple(valid_fixture) == ROOT_FIELDS, tuple(valid_fixture), ROOT_FIELDS, "schema")
    audit.check("target fields exact", tuple(valid_fixture["target_contract"]) == TARGET_FIELDS, tuple(valid_fixture["target_contract"]), TARGET_FIELDS, "schema")
    audit.check("commitment fields exact", tuple(valid_fixture["target_contract"]["commitment"]) == COMMITMENT_FIELDS, tuple(valid_fixture["target_contract"]["commitment"]), COMMITMENT_FIELDS, "schema")
    audit.check("disclosure fields exact", tuple(valid_fixture["target_contract"]["disclosure"]) == DISCLOSURE_FIELDS, tuple(valid_fixture["target_contract"]["disclosure"]), DISCLOSURE_FIELDS, "schema")
    audit.check("prediction fields exact", tuple(valid_fixture["prediction_contract"]) == PREDICTION_FIELDS, tuple(valid_fixture["prediction_contract"]), PREDICTION_FIELDS, "schema")
    audit.check("allowed-input fields exact", tuple(valid_fixture["prediction_contract"]["allowed_inputs"][0]) == ALLOWED_INPUT_FIELDS, tuple(valid_fixture["prediction_contract"]["allowed_inputs"][0]), ALLOWED_INPUT_FIELDS, "schema")
    audit.check("robustness fields exact", tuple(valid_fixture["robustness_contract"]) == ROBUSTNESS_FIELDS, tuple(valid_fixture["robustness_contract"]), ROBUSTNESS_FIELDS, "schema")
    audit.check("candidate prediction bound", valid_fixture["prediction_contract"]["candidate_id"] == valid_fixture["observable_contract"]["candidate_maps"][0]["candidate_id"], valid_fixture["prediction_contract"]["candidate_id"], valid_fixture["observable_contract"]["candidate_maps"][0]["candidate_id"], "schema")
    audit.check("freeze schema exact", valid_fixture["schema"] == FREEZE_SCHEMA, valid_fixture["schema"], FREEZE_SCHEMA, "schema")
    audit.check("common estimand separated from maps", "common_estimand" in valid_fixture["observable_contract"] and "candidate_maps" in valid_fixture["observable_contract"], list(valid_fixture["observable_contract"]), ["common_estimand", "candidate_maps"], "schema")
    audit.check("target value absent from valid fixture", forbidden_value_keys(valid_fixture["target_contract"]) == [], forbidden_value_keys(valid_fixture["target_contract"]), [], "schema")
    audit.check("synthetic fixture cannot be promoted", promoted_report["valid"] is False and "EXTERNAL_VERIFICATION_REQUIRED" in promoted_report["error_codes"], promoted_report, "external verification required", "schema")

    hostile = hostile_fixture_reports(valid_fixture)
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
    audit.check("hostile fixture names exact", tuple(hostile) == expected_hostile, tuple(hostile), expected_hostile, "hostile")
    for name in expected_hostile:
        report = hostile[name]
        audit.check(f"{name} fixture rejected", report["valid"] is False, report["valid"], False, "hostile")
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
    audit.check("map-only survival hostile names exact", tuple(map_only_survival_hostile) == expected_map_only_survival_hostile and tuple(authority_map_hostile["cases"]) == expected_map_only_survival_hostile, tuple(map_only_survival_hostile), expected_map_only_survival_hostile, "map_only_hostile")
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
    audit.check("successor hostile names exact", tuple(successor_hostile) == expected_successor_hostile, tuple(successor_hostile), expected_successor_hostile, "successor_hostile")
    audit.check("successor hostile authority exact", tuple(authority_successor_hostile["cases"]) == expected_successor_hostile and authority_successor_hostile["v1_0_freeze_schema_hostile_count_preserved"] == 28 and authority_successor_hostile["successor_hostile_count"] == len(expected_successor_hostile) and authority_successor_hostile["total_hostile_class_count"] == 28 + len(expected_successor_hostile), authority_successor_hostile, {"v1_0": 28, "successor": len(expected_successor_hostile)}, "successor_hostile")
    for name in expected_successor_hostile:
        report = successor_hostile[name]
        audit.check(f"successor {name} rejected", report["valid"] is False, report["valid"], False, "successor_hostile")
        audit.check(f"successor {name} expected code", report["expected_code_observed"], report["error_codes"], report["expected_error_code"], "successor_hostile")

    authority_physical_hostile = authority["m2_physical_response_successor_minimum_contract_hostile_fixtures"]
    audit.check("physical-contract hostile names exact", tuple(physical_contract_hostile) == EXPECTED_PHYSICAL_CONTRACT_HOSTILES and tuple(authority_physical_hostile["cases"]) == EXPECTED_PHYSICAL_CONTRACT_HOSTILES, tuple(physical_contract_hostile), EXPECTED_PHYSICAL_CONTRACT_HOSTILES, "physical_contract_hostile")
    for name in EXPECTED_PHYSICAL_CONTRACT_HOSTILES:
        report = physical_contract_hostile[name]
        audit.check(f"physical-contract {name} rejected", report["valid"] is False, report["valid"], False, "physical_contract_hostile")
        audit.check(f"physical-contract {name} expected code", report["expected_code_observed"], report["error_codes"], report["expected_error_code"], "physical_contract_hostile")

    formal = formal_authority_audit(audit, staged=staged)
    actual_validation: dict[str, Any]
    verdict = "PASS" if formal["status"] == "COMPLETE" else formal["status"]
    if freeze_manifest is None:
        actual_validation = {
            "status": "ABSENT_BY_DESIGN",
            "path": None,
            "valid": False,
            "reason": "No actual freeze manifest was requested; current-tree readiness remains false.",
        }
    elif not freeze_manifest.is_file():
        if not staged:
            raise FileNotFoundError(freeze_manifest)
        actual_validation = {
            "status": "MISSING_STAGED",
            "path": str(freeze_manifest),
            "valid": False,
            "reason": "Requested future freeze manifest does not yet exist.",
        }
        verdict = "STAGED" if staged else "INCOMPLETE"
    else:
        actual = load_json(freeze_manifest)
        report = validate_freeze_manifest(actual, allow_fixture=False)
        if not report["valid"]:
            raise AssertionError(
                "actual freeze manifest invalid: " + ", ".join(report["error_codes"])
            )
        actual_validation = {
            "status": "VALIDATED",
            "path": repo_path(freeze_manifest),
            "valid": True,
            "sha256": normalized_sha256(freeze_manifest),
            "report": report,
        }

    audit.check("no actual freeze inferred from schema fixture", valid_fixture["fixture_only"] is True and state["actual_freeze_ready"] is False, [valid_fixture["fixture_only"], state["actual_freeze_ready"]], [True, False], "scope")
    audit.check("parent remains open", state["parent_freeze_gate_closed"] is False, state["parent_freeze_gate_closed"], False, "scope")
    audit.check("no Pre-A exit", state["pre_a_exit_conditions_met"] is False, state["pre_a_exit_conditions_met"], False, "scope")

    passed = len(audit.rows)
    return {
        "schema": RESULT_SCHEMA,
        "script_version": __version__,
        "task_id": "T-054",
        "claim_ids": ["C6-SPACETIME-SIGNATURE"],
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
        "passed": passed,
        "failed": 0,
        "total": passed,
        "summary": {
            "passed": passed,
            "failed": 0,
            "total": passed,
            "current_tree_ready": state["actual_freeze_ready"],
            "actual_freeze_status": actual_validation["status"],
        },
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
            "required_temporal_order": (
                "custodian commitment <= public remote freeze < target disclosure"
            ),
            "official_record_path": "predictions/freezes/<PRED-ID>-freeze.md",
            "official_tag_pattern": "freeze/<PRED-ID>/v<N>",
            "synthetic_fixture_only": True,
        },
        "current_tree": state,
        "current_version_map_only_audit": map_only,
        "map_only_survival_validation": map_only_survival_report,
        "map_only_repair_hostile_fixtures": map_only_survival_hostile,
        "m2_retrospective_stiffness_map_underdetermination": underdetermination,
        "m2_finite_torus_dispersion_fingerprint": fingerprint,
        "m2_v1_successor_design_validation": successor_report,
        "m2_v1_successor_design": successor_design,
        "successor_hostile_fixtures": successor_hostile,
        "m2_linear_probe_second_order_response_nonidentifiability": linear_probe,
        "m2_physical_response_successor_minimum_contract_validation": physical_contract_report,
        "m2_physical_response_successor_minimum_contract_fixture": physical_contract_fixture,
        "m2_physical_response_successor_minimum_contract_hostile_fixtures": physical_contract_hostile,
        "m2_physical_response_successor_minimum_contract_reordered_metamorphic": physical_contract_reordered,
        "m2_physical_response_successor_minimum_contract_fuzz": physical_contract_fuzz,
        "formal_authority": formal,
        "synthetic_schema_validation": {
            "valid": valid_report["valid"],
            "error_codes": valid_report["error_codes"],
            "fixture_digest": hashlib.sha256(
                json.dumps(valid_fixture, sort_keys=True, separators=(",", ":")).encode(
                    "utf-8"
                )
            ).hexdigest(),
        },
        "real_freeze_verification_boundary": {
            "schema_shape_validated": True,
            "custodian_signature_cryptographically_verified": False,
            "remote_commit_fetched_and_verified": False,
            "remote_annotated_tag_fetched_and_verified": False,
            "real_freeze_acceptance_enabled": False,
            "required_error_code": "EXTERNAL_VERIFICATION_REQUIRED",
        },
        "hostile_fixtures": hostile,
        "actual_freeze_validation": actual_validation,
        "scope": {
            "protocol_schema_validated": True,
            "cryptographic_signature_verifier_implemented": False,
            "independent_remote_ref_verifier_implemented": False,
            "current_tree_readiness_audited": True,
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
            "parent_gate_closed": False,
            "Pre_A_complete": False,
            "Sector_A_complete": False,
        },
        "source_hashes": {
            repo_path(SCRIPT): normalized_sha256(SCRIPT),
            repo_path(AUTHORITY_MANIFEST): normalized_sha256(AUTHORITY_MANIFEST),
            repo_path(AUTHORITY_CERTIFICATE): normalized_sha256(AUTHORITY_CERTIFICATE),
        },
        "assertions": audit.rows,
        "boundary": (
            "Cumulative v1.0/v1.1 protocol, current-version map-empty-set, "
            "finite-torus fingerprint, exact fixed-linear-probe second-order response "
            "nonidentifiability, and schema-only minimum successor contract. "
            "No M2-v1 candidate, admitted map, physical response/error bound, "
            "freeze, tag, target, prediction, score, selection, parent-gate closure, "
            "Pre-A exit, or physical Sector-A selection follows."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--freeze-manifest", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument(
        "--staged",
        action="store_true",
        help="report a requested missing future freeze manifest as INCOMPLETE",
    )
    arguments = parser.parse_args()

    payload = run_audit(arguments.freeze_manifest, staged=arguments.staged)
    if arguments.self_test:
        repeated = run_audit(arguments.freeze_manifest, staged=arguments.staged)
        if payload != repeated:
            raise AssertionError("self-test payload is not deterministic")
    if not arguments.self_test and not arguments.no_store:
        atomic_json(arguments.output, payload)

    print(f"{payload['verdict']} {payload['passed']}/{payload['total']}")
    print("schema: " + payload["schema"])
    print("freeze_schema: " + payload["freeze_schema_contract"]["schema"])
    script_key = repo_path(SCRIPT)
    print("script_sha256: " + payload["source_hashes"][script_key])
    state = payload["current_tree"]
    print(
        "current: "
        f"freeze_records={state['freeze_record_count']} "
        f"live_freeze_tags={state['local_freeze_tag_observation']['count']} "
        f"admitted_survivors={state['admitted_microscopic_survivor_count']} "
        f"ready={str(state['actual_freeze_ready']).lower()}"
    )
    if payload["formal_authority"]["missing"]:
        print("STAGED-MISSING " + ", ".join(payload["formal_authority"]["missing"]))
    if payload["verdict"] == "INCOMPLETE" and "reason" in payload["actual_freeze_validation"]:
        print("authority: " + payload["actual_freeze_validation"]["reason"])
    return 0 if payload["verdict"] == "PASS" or arguments.staged else 1


if __name__ == "__main__":
    raise SystemExit(main())
