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
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable
from urllib.parse import urlparse


__version__ = "1.1.0"
__first_issued__ = "2026-08-11"

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-round1-prospective-holdout-freeze-protocol"
RESULT_SCHEMA = f"tect/{SLUG}-independent-result/1.0"
FREEZE_SCHEMA = "tect/pre-a-round1-prospective-holdout-freeze/1.0"
TASK_ID = "T-054"
CLAIM_IDS = ("C6-SPACETIME-SIGNATURE",)
RESULT_NUMBER = "R-168"
RESULT_VERSION = "v1.0"
RESULT_ID = (
    "PA-ROUND1-PROSPECTIVE-HOLDOUT-FREEZE-PROTOCOL-AND-CURRENT-TREE-"
    "READINESS-AUDIT"
)
EXPLORATION_ID = "EXP-000807"
AUDITED_COMMIT = "99157442831c0e44d425b5d5f8cd78856c57da53"
PARENT_GATE = "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE"
NEGATIVE_IDS = (
    "NG-2026-08-11-PRE-A-ROUND1-CURRENT-TREE-PROSPECTIVE-HOLDOUT-"
    "NONEXISTENCE",
)
REUSED_NEGATIVE_IDS = (
    "NG-2026-08-09-PRE-A-ROUND1-UNFROZEN-TOURNAMENT-SELECTION",
)
CLOSED_SUBGATES = (
    "PA-ROUND1-COMMON-ESTIMAND-AND-CANDIDATE-MAP-SCHEMA",
    "PA-ROUND1-PROSPECTIVE-FREEZE-PROVENANCE-PROTOCOL",
    "PA-ROUND1-TARGET-INDEPENDENCE-AND-ANTI-LEAKAGE-SCHEMA-VALIDATOR",
    "PA-ROUND1-CURRENT-CANDIDATE-MAP-ADMISSION-EMPTY-SET-AUDIT",
)
OPEN_GATES = (
    PARENT_GATE,
    "PA-ROUND1-PER-PARAMETER-COMMON-INPUT-LEDGER",
    "PA-ROUND1-INDEPENDENT-CUSTODIAN-OPAQUE-TARGET-COMMITMENT",
    "PA-ROUND1-ADMISSIBLE-MICROSCOPIC-CANDIDATE-MAP-AND-FROZEN-PREDICTION",
    "PA-ROUND1-CRYPTOGRAPHIC-CUSTODIAN-SIGNATURE-AND-REMOTE-FREEZE-"
    "VERIFICATION",
)
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
    if missing or extra:
        details = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if extra:
            details.append("extra=" + ",".join(extra))
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
    if not path_text or "\\" in path_text or ":" in path_text:
        return False
    pure = PurePosixPath(path_text)
    if pure.is_absolute() or pure.as_posix() != path_text:
        return False
    if any(part in {"", ".", ".."} for part in pure.parts):
        return False
    candidate = (REPO / Path(*pure.parts)).resolve()
    try:
        candidate.relative_to(REPO.resolve())
    except ValueError:
        return False
    return candidate.is_file() and normalized_sha256(candidate) == digest


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
        add_error(errors, "ROOT_FIELDS_EXTRA", ", ".join(extra))

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


def formal_authority_audit(audit: Audit, staged: bool) -> dict[str, Any]:
    missing: list[str] = []

    gates_text = GATES.read_text(encoding="utf-8")
    for identifier in CLOSED_SUBGATES:
        section = section_for(gates_text, identifier)
        if not section:
            missing.append(f"claims/GATES.md#{identifier}")
        else:
            audit.check(
                f"closed formal gate {identifier}",
                "**Status:** CLOSED" in section,
                "CLOSED" if "**Status:** CLOSED" in section else section[:160],
                "CLOSED",
                "formal_authority",
            )
    for identifier in OPEN_GATES:
        section = section_for(gates_text, identifier)
        if not section:
            missing.append(f"claims/GATES.md#{identifier}")
        else:
            audit.check(
                f"open formal gate {identifier}",
                "**Status:** OPEN" in section,
                "OPEN" if "**Status:** OPEN" in section else section[:160],
                "OPEN",
                "formal_authority",
            )

    negative_text = NEGATIVE_REGISTRY.read_text(encoding="utf-8")
    for identifier in NEGATIVE_IDS:
        if identifier not in negative_text:
            missing.append(f"negative-results/registry.md#{identifier}")
        else:
            audit.check(
                f"negative authority {identifier}",
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
            "results ledger result/version/ID binding",
            all(token in result_text for token in (RESULT_NUMBER, RESULT_VERSION, RESULT_ID)),
            True,
            True,
            "formal_authority",
        )

    exploration = exploration_record(EXPLORATION_ID)
    if exploration is None:
        missing.append(f"explorations/log.jsonl#{EXPLORATION_ID}")
    else:
        audit.check(
            "exploration task binding",
            exploration.get("task_id") == TASK_ID,
            exploration.get("task_id"),
            TASK_ID,
            "formal_authority",
        )
        audit.check(
            "exploration result binding",
            exploration.get("formal_refs", {}).get("results") == [RESULT_NUMBER],
            exploration.get("formal_refs", {}).get("results"),
            [RESULT_NUMBER],
            "formal_authority",
        )
        audit.check(
            "exploration negative binding",
            exploration.get("formal_refs", {}).get("negatives") == list(NEGATIVE_IDS),
            exploration.get("formal_refs", {}).get("negatives"),
            list(NEGATIVE_IDS),
            "formal_authority",
        )
        required_gates = set(CLOSED_SUBGATES + OPEN_GATES)
        audit.check(
            "exploration gate binding",
            required_gates <= set(exploration.get("gate_ids", [])),
            exploration.get("gate_ids", []),
            sorted(required_gates),
            "formal_authority",
        )

    if not missing:
        status = "COMPLETE"
    elif staged:
        status = "STAGED"
    else:
        status = "INCOMPLETE"
    return {"status": status, "missing": missing, "staged": staged}


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
    audit.check("task ID", authority.get("task_id") == TASK_ID, authority.get("task_id"), TASK_ID, "identity")
    audit.check("claim context", tuple(authority.get("claim_ids", [])) == CLAIM_IDS, authority.get("claim_ids"), list(CLAIM_IDS), "identity")
    audit.check("claim nonbearing", authority.get("claim_bearing") is False, authority.get("claim_bearing"), False, "scope")
    audit.check("negative IDs exact", tuple(authority.get("negative_ids", [])) == NEGATIVE_IDS, authority.get("negative_ids"), list(NEGATIVE_IDS), "identity")
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
    for token in (RESULT_NUMBER, RESULT_VERSION, RESULT_ID, EXPLORATION_ID, *NEGATIVE_IDS, *CLOSED_SUBGATES, *OPEN_GATES):
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

    state = reconstruct_checkpoint()
    checkpoint = authority["audited_checkpoint"]
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

    fixture = synthetic_fixture()
    fixture_report = validate_schema_shape(fixture, synthetic_fixture_mode=True)
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

    actual = validate_requested_freeze(freeze_path, staged=staged)
    audit.check("actual freeze never accepted", actual["valid"] is False, actual["valid"], False, "external_boundary")
    audit.check("external code retained for actual path", "EXTERNAL_VERIFICATION_REQUIRED" in actual["error_codes"], actual["error_codes"], "contains EXTERNAL_VERIFICATION_REQUIRED", "external_boundary")

    formal = formal_authority_audit(audit, staged=staged)
    verdict = "PASS" if formal["status"] == "COMPLETE" and freeze_path is None else "INCOMPLETE"
    passed = len(audit.rows)
    source_paths = (
        SCRIPT,
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
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "negative_ids": list(NEGATIVE_IDS),
        "reused_negative_ids": list(REUSED_NEGATIVE_IDS),
        "closed_subgates": list(CLOSED_SUBGATES),
        "open_gates": list(OPEN_GATES),
        "parent_gate": PARENT_GATE,
        "verdict": verdict,
        "summary": {"passed": passed, "failed": 0, "total": passed},
        "authority": formal,
        "current_tree": state,
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
            "parent_gate_closed": False,
            "Pre_A_complete": False,
            "Sector_A_complete": False,
        },
        "source_hashes": {
            repo_path(path): normalized_sha256(path) for path in source_paths
        },
        "assertions": audit.rows,
        "boundary": (
            "Independent schema-shape and audited-current-tree verification only. "
            "No cryptographic signature or remote-ref verification, real freeze, "
            "tag, target, prediction, score, parent-gate closure, Pre-A exit, or "
            "physical Sector-A selection follows."
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
