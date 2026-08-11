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
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable
from urllib.parse import urlparse


__version__ = "1.2.0"
__first_issued__ = "2026-08-11"
__version_issued__ = "2026-08-11"

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
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
RESULT_VERSION = "v1.0"
EXPLORATION_ID = "EXP-000807"
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

FREEZE_DIRECTORY = REPO / "predictions/freezes"
PREDICTION_LEDGER = REPO / "predictions/prediction-ledger.md"
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
    if missing or extra:
        details = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if extra:
            details.append("extra=" + ",".join(extra))
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
    if not path_text or "\\" in path_text or ":" in path_text:
        return False
    pure = PurePosixPath(path_text)
    if pure.is_absolute() or pure.as_posix() != path_text:
        return False
    if any(part in {"", ".", ".."} for part in pure.parts):
        return False
    path = (REPO / Path(*pure.parts)).resolve()
    try:
        path.relative_to(REPO.resolve())
    except ValueError:
        return False
    return path.is_file() and normalized_sha256(path) == digest


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
        error(errors, "ROOT_FIELDS_EXTRA", ", ".join(extra))

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
    audit.check("current blockers exact", state["blockers"] == [
        "NO_MACHINE_FREEZE_RECORD",
        "NO_ADMITTED_MICROSCOPIC_SURVIVOR",
        "M1_MAP_AND_PREDICTION_ABSENT",
        "M2_PHYSICAL_PREDICTION_AND_HOLDOUT_ABSENT",
        "M5_MAP_AND_HOLDOUT_ABSENT",
        "PER_PARAMETER_COMMON_INPUT_LEDGER_INCOMPLETE",
        "PROSPECTIVE_PREDICTION_NOT_FROZEN",
    ], state["blockers"], "exact seven stable blockers", "current_tree")

    gate_text = GATE_REGISTRY.read_text(encoding="utf-8")
    prediction_text = PREDICTION_LEDGER.read_text(encoding="utf-8")
    audit.check("authority result ID", authority["result_id"] == RESULT_ID, authority["result_id"], RESULT_ID, "authority")
    audit.check("authority result number", authority["result_number"] == RESULT_NUMBER, authority["result_number"], RESULT_NUMBER, "authority")
    audit.check("authority result version", authority["result_version"] == RESULT_VERSION, authority["result_version"], RESULT_VERSION, "authority")
    audit.check("authority exploration", authority["exploration_id"] == EXPLORATION_ID, authority["exploration_id"], EXPLORATION_ID, "authority")
    audit.check("authority task", authority["task_id"] == "T-054", authority["task_id"], "T-054", "authority")
    audit.check("authority claim context", authority["claim_ids"] == ["C6-SPACETIME-SIGNATURE"], authority["claim_ids"], ["C6-SPACETIME-SIGNATURE"], "authority")
    audit.check("authority claim nonbearing", authority["claim_bearing"] is False, authority["claim_bearing"], False, "authority")
    audit.check("authority negative IDs", tuple(authority["negative_ids"]) == NEGATIVE_IDS, authority["negative_ids"], NEGATIVE_IDS, "authority")
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
    audit.check("authority protocol status", authority["status"] == "SCHEMA PROTOCOL READY; CURRENT TREE NOT FREEZE-READY; CRYPTOGRAPHIC REMOTE VERIFICATION AND PARENT PRE-A GATE OPEN", authority["status"], "schema protocol ready and verification gates open", "authority")
    audit.check("certificate result linkage", RESULT_NUMBER in certificate_text and RESULT_ID in certificate_text and EXPLORATION_ID in certificate_text, True, True, "authority")
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

    actual_validation: dict[str, Any]
    verdict = "PASS"
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
        verdict = "INCOMPLETE"
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
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "negative_ids": list(NEGATIVE_IDS),
        "reused_negative_ids": list(REUSED_NEGATIVE_IDS),
        "closed_subgates": list(CLOSED_SUBGATES),
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
            "Protocol/schema and exact current-tree absence audit only. No actual "
            "freeze record, tag, target, candidate map, prediction, parent-gate "
            "closure, Pre-A exit, or physical Sector-A selection follows."
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
    if payload["verdict"] == "INCOMPLETE":
        print("authority: " + payload["actual_freeze_validation"]["reason"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
