#!/usr/bin/env python3
"""Integrated verifier for EXP-000807 / R-168 v1.0.

The primary and non-importing independent engines are each executed twice via
their public command-line interfaces in fresh child processes.  This verifier
checks exact deterministic payload equality, stored-result freshness, the AST
independence firewall, the commit-pinned empty current-tree audit, the future
freeze schema and hostile fixtures, and the formal/generated authority chain.

``--staged`` is assembly-safe and fail-closed.  A not-yet-issued formal,
stored-result, or regenerated reader authority is reported as ``MISSING`` and
produces ``INCOMPLETE`` with exit code zero.  A contradiction, malformed
authority, existing stale result, or cross-engine mismatch is always ``FAIL``.
The normalized invocation metadata is ``authority.staged`` plus the explicitly
informational live local-tag observation; no mathematical, audited-checkpoint,
or provenance field is removed.

R-168 deliberately has no dedicated proof-note PDF contract.  Its schema and
run records remain development evidence until the surrounding Pre-A/Sector-A
lane issues one combined gate-level synthesis checkpoint.  Once issued, strict
validation binds the exact shared source/PDF pair, hashes, freshness, page/text
extraction, scope, and reproduction contract.  This script never creates a
freeze, prediction, tag, note source, PDF, or formal authority.
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
from pathlib import Path
from typing import Any, Iterable, Mapping


__version__ = "1.0.1"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-round1-prospective-holdout-freeze-protocol"

TASK_ID = "T-054"
CLAIM_IDS = ("C6-SPACETIME-SIGNATURE",)
RESULT_NUMBER = "R-168"
RESULT_VERSION = "v1.0"
RESULT_ID = (
    "PA-ROUND1-PROSPECTIVE-HOLDOUT-FREEZE-PROTOCOL-AND-CURRENT-TREE-"
    "READINESS-AUDIT"
)
EXPLORATION_ID = "EXP-000807"
HARDENING_EXPLORATION_ID = "EXP-000808"
PARENT_EXPLORATIONS = ("EXP-000791",)
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
ALL_GATE_IDS = (*CLOSED_SUBGATES, *OPEN_GATES)
HARDENING_GATE_IDS = (
    "PA-ROUND1-TARGET-INDEPENDENCE-AND-ANTI-LEAKAGE-SCHEMA-VALIDATOR",
    PARENT_GATE,
    "PA-ROUND1-ADMISSIBLE-MICROSCOPIC-CANDIDATE-MAP-AND-FROZEN-PREDICTION",
    "PA-ROUND1-CRYPTOGRAPHIC-CUSTODIAN-SIGNATURE-AND-REMOTE-FREEZE-"
    "VERIFICATION",
)

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
EXPECTED_CHECKPOINT_SYNTHESIS = {
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
    RESULT_VERSION,
    EXPLORATION_ID,
    HARDENING_EXPLORATION_ID,
    *CLOSED_SUBGATES,
    *OPEN_GATES,
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


def checkpoint_lifecycle_diagnostics(
    synthesis: Mapping[str, Any],
) -> dict[str, Any]:
    """Read-only validation of the issued combined checkpoint.

    The caller deliberately compresses this complete diagnostic into the two
    pre-existing PDF-economy audit rows, preserving the advertised 218-row
    integrated contract while strengthening those rows fail-closed.
    """

    diagnostics: dict[str, Any] = {
        "metadata_exact": dict(synthesis) == EXPECTED_CHECKPOINT_SYNTHESIS,
        "expected_metadata": EXPECTED_CHECKPOINT_SYNTHESIS,
        "shared_manifest_exact": False,
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
        diagnostics["shared_manifest_exact"] = (
            other_checkpoint == EXPECTED_CHECKPOINT_SYNTHESIS
            and dict(synthesis) == other_checkpoint
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        diagnostics["shared_manifest_error"] = str(error)

    source_text = ""
    if diagnostics["source_exists"]:
        try:
            source_text = CHECKPOINT_SOURCE.read_text(encoding="utf-8")
            source_stat = CHECKPOINT_SOURCE.stat()
            diagnostics["source_sha256"] = artifact_sha256(CHECKPOINT_SOURCE)
            diagnostics["source_mtime_ns"] = source_stat.st_mtime_ns
            diagnostics["source_missing_tokens"] = [
                token
                for token in CHECKPOINT_REQUIRED_TOKENS
                if not text_has(source_text, token)
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
            diagnostics["pypdf_nonempty_pages"] = sum(bool(text.strip()) for text in texts)
            diagnostics["pypdf_missing_tokens"] = [
                token
                for token in CHECKPOINT_REQUIRED_TOKENS
                if not text_has(joined, token)
            ]
        except Exception as error:  # parser failures must become audited FAILs
            diagnostics["pypdf_error"] = f"{type(error).__name__}: {error}"

        try:
            import pdfplumber

            with pdfplumber.open(CHECKPOINT_PDF) as document:
                texts = [(page.extract_text() or "") for page in document.pages]
            joined = "\n".join(texts)
            diagnostics["pdfplumber_pages"] = len(texts)
            diagnostics["pdfplumber_nonempty_pages"] = sum(
                bool(text.strip()) for text in texts
            )
            diagnostics["pdfplumber_missing_tokens"] = [
                token
                for token in CHECKPOINT_REQUIRED_TOKENS
                if not text_has(joined, token)
            ]
        except Exception as error:  # independent parser failures fail closed
            diagnostics["pdfplumber_error"] = f"{type(error).__name__}: {error}"

    return diagnostics


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


def invocation_view(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    """Remove invocation-only metadata, never theorem/provenance content.

    ``authority.staged`` records CLI mode.  The live local ``freeze/*`` tag
    observation is explicitly informational and may change after a legitimate
    future freeze, so it is also excluded from stored-result freshness.
    """

    if payload is None:
        return None
    copied = json.loads(json.dumps(payload))
    authority = copied.get("authority")
    if isinstance(authority, dict):
        authority.pop("staged", None)
    current_tree = copied.get("current_tree")
    if isinstance(current_tree, dict):
        current_tree.pop("local_freeze_tag_observation", None)
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
    authority = as_mapping(first[0].get("authority"))
    if authority:
        audit.check(
            f"{label} staged invocation metadata explicit",
            authority.get("staged") is audit.staged,
            authority.get("staged"),
            audit.staged,
            "freshness",
        )
        audit.check(
            f"{label} normalization removes staged flag",
            "staged" not in as_mapping(invocation_view(first[0]).get("authority")),
            as_mapping(invocation_view(first[0]).get("authority")),
            "authority without staged",
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


def validate_firewall(audit: Audit) -> None:
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
    audit.check(
        "independent primary-result firewall",
        all(primary_run_fragment not in value for value in literals),
        [value for value in literals if primary_run_fragment in value],
        [],
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


def validate_component(
    payload: dict[str, Any], label: str, schema: str, expected_count: int, audit: Audit
) -> None:
    expected = {
        "schema": schema,
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
    }
    for field, value in expected.items():
        audit.check(
            f"{label} exact {field}",
            payload.get(field) == value,
            payload.get(field),
            value,
            "component",
        )
    allowed = {"PASS", "INCOMPLETE"} if audit.staged else {"PASS"}
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
    audit.check(
        f"{label} exact no-overclaim scope",
        all(
            scope.get(key) is False
            for key in (
                "actual_freeze_record_created",
                "git_tag_created",
                "external_target_commitment_present",
                "admitted_current_microscopic_map_present",
                "prospective_prediction_present",
                "parent_gate_closed",
                "Pre_A_complete",
                "Sector_A_complete",
            )
        ),
        scope,
        "all promotion/issuance flags false",
        "component",
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


def compare_components(
    primary: dict[str, Any], independent: dict[str, Any], audit: Audit
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
        == EXPECTED_BLOCKERS,
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
    }


def validate_manifest(manifest: dict[str, Any], audit: Audit) -> dict[str, Any]:
    expected = {
        "schema": "tect/pre-a-route-split/1.0",
        "task_id": TASK_ID,
        "claim_ids": list(CLAIM_IDS),
        "parent_explorations": list(PARENT_EXPLORATIONS),
        "correction_exploration_ids": [HARDENING_EXPLORATION_ID],
        "exploration_id": EXPLORATION_ID,
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "claim_bearing": False,
        "negative_ids": list(NEGATIVE_IDS),
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
    checkpoint = as_mapping(manifest.get("audited_checkpoint"))
    audit.check(
        "manifest commit-pinned empty checkpoint",
        checkpoint.get("commit") == AUDITED_COMMIT
        and checkpoint.get("freeze_records") == 0
        and checkpoint.get("admitted_microscopic_survivors") == 0
        and checkpoint.get("verdict") == "NOT_CLOSABLE_CURRENT_TREE"
        and "freeze_tags" not in checkpoint
        and "freeze_tag_scope" not in checkpoint,
        checkpoint,
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
            tuple(freeze.get(field, ())) == expected
            for field, expected in NESTED_FIELD_CONTRACTS.items()
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
        (
            "candidate_id",
            "score-eligible",
            "admitted map",
            "predicted_relation",
            "uniquely keyed",
        ),
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
    audit.check(
        "manifest exact 28 hostile classes",
        len(as_mapping(manifest.get("hostile_fixtures"))) == 28
        and set(as_mapping(manifest.get("hostile_fixtures"))) == set(HOSTILE_CODES),
        list(as_mapping(manifest.get("hostile_fixtures"))),
        list(HOSTILE_CODES),
        "manifest",
    )
    route = as_mapping(manifest.get("route_status"))
    audit.check(
        "manifest route gates exact",
        route.get("parent_gate") == OPEN_GATES[0]
        and route.get("external_gate") == OPEN_GATES[2]
        and route.get("internal_gate") == OPEN_GATES[3]
        and route.get("verification_gate") == OPEN_GATES[4],
        route,
        {
            "parent": OPEN_GATES[0],
            "external": OPEN_GATES[2],
            "internal": OPEN_GATES[3],
            "verification": OPEN_GATES[4],
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
        "manifest no-overclaim",
        (
            "not a cryptographic signature verifier",
            "not an actual freeze",
            "does not authorize a tag",
            "physical Sector A",
            "Pre-A",
        ),
        audit,
        core=True,
        group="manifest",
    )

    synthesis = as_mapping(manifest.get("checkpoint_synthesis"))
    checkpoint = checkpoint_lifecycle_diagnostics(synthesis)
    audit.check(
        "manifest exact shared combined R-167/R-168 checkpoint",
        checkpoint["metadata_exact"] and checkpoint["shared_manifest_exact"],
        {
            "metadata": synthesis,
            "shared_manifest_exact": checkpoint["shared_manifest_exact"],
            "shared_manifest_error": checkpoint["shared_manifest_error"],
        },
        EXPECTED_CHECKPOINT_SYNTHESIS,
        "pdf_economy",
    )
    lifecycle_ok = (
        checkpoint["source_exists"]
        and checkpoint["pdf_exists"]
        and checkpoint["source_sha256"] == CHECKPOINT_SOURCE_SHA256
        and checkpoint["pdf_sha256"] == CHECKPOINT_PDF_SHA256
        and checkpoint["pdf_fresh_relative_to_source"]
        and checkpoint["source_missing_tokens"] == []
        and checkpoint["pypdf_error"] is None
        and checkpoint["pypdf_pages"] == CHECKPOINT_PAGES
        and checkpoint["pypdf_nonempty_pages"] == CHECKPOINT_PAGES
        and checkpoint["pypdf_missing_tokens"] == []
        and checkpoint["pdfplumber_error"] is None
        and checkpoint["pdfplumber_pages"] == CHECKPOINT_PAGES
        and checkpoint["pdfplumber_nonempty_pages"] == CHECKPOINT_PAGES
        and checkpoint["pdfplumber_missing_tokens"] == []
    )
    audit.check(
        "combined checkpoint hashes freshness pages extraction scope reproduction",
        lifecycle_ok,
        checkpoint,
        {
            "source_sha256": CHECKPOINT_SOURCE_SHA256,
            "pdf_sha256": CHECKPOINT_PDF_SHA256,
            "pdf_mtime_ns": ">= source_mtime_ns",
            "pypdf": f"{CHECKPOINT_PAGES}/{CHECKPOINT_PAGES} nonempty pages",
            "pdfplumber": f"{CHECKPOINT_PAGES}/{CHECKPOINT_PAGES} nonempty pages",
            "required_tokens": list(CHECKPOINT_REQUIRED_TOKENS),
        },
        "pdf_economy",
    )
    return synthesis


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
                    section[:500],
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
                    section[:500],
                    "explicit OPEN status",
                    "formal",
                )

    result_section = heading_section(results, RESULT_NUMBER) if results else None
    if result_section is None:
        audit.pending("R-168 result authority", False, None, "unique section", "formal")
    else:
        require_tokens(
            result_section,
            "R-168 result authority",
            (
                RESULT_NUMBER,
                RESULT_VERSION,
                RESULT_ID,
                EXPLORATION_ID,
                HARDENING_EXPLORATION_ID,
                "T0",
                *NEGATIVE_IDS,
                *CLOSED_SUBGATES,
                *OPEN_GATES,
                "actual freeze",
                "Pre-A",
            ),
            audit,
            core=True,
        )

    if negatives is not None:
        section = heading_section(negatives, NEGATIVE_IDS[0])
        if section is None:
            audit.pending("R-168 negative authority", False, None, "unique section", "formal")
        else:
            require_tokens(
                section,
                "R-168 negative authority",
                (NEGATIVE_IDS[0], EXPLORATION_ID, RESULT_NUMBER, "current", "future"),
                audit,
                core=True,
            )
        reused = heading_section(negatives, REUSED_NEGATIVE_IDS[0])
        audit.check(
            "reused negative authority retained",
            reused is not None,
            REUSED_NEGATIVE_IDS[0],
            "existing section",
            "formal",
        )

    matches = (
        []
        if explorations is None
        else [row for row in explorations if row.get("id") == EXPLORATION_ID]
    )
    if not matches:
        audit.pending("EXP-000807 unique record", False, 0, 1, "formal")
    else:
        audit.check("EXP-000807 unique record", len(matches) == 1, len(matches), 1, "formal")
    if len(matches) == 1:
        record = matches[0]
        formal_refs = as_mapping(record.get("formal_refs"))
        audit.check(
            "EXP-000807 exact identity sets",
            record.get("task_id") == TASK_ID
            and record.get("claim_ids") == list(CLAIM_IDS)
            and formal_refs.get("results") == [RESULT_NUMBER]
            and formal_refs.get("negatives") == list(NEGATIVE_IDS)
            and set(record.get("gate_ids", [])) == set(ALL_GATE_IDS)
            and len(record.get("gate_ids", [])) == len(ALL_GATE_IDS),
            {
                "task": record.get("task_id"),
                "claims": record.get("claim_ids"),
                "formal_refs": formal_refs,
                "gates": record.get("gate_ids"),
            },
            {
                "task": TASK_ID,
                "claims": CLAIM_IDS,
                "results": [RESULT_NUMBER],
                "negatives": NEGATIVE_IDS,
                "gates": ALL_GATE_IDS,
            },
            "formal",
        )
        require_tokens(
            json.dumps(record, sort_keys=True),
            "EXP-000807 scope boundary",
            (
                "current-tree",
                "cryptographic",
                "remote",
                "custodian signature",
                "remote ref",
                "no target",
                "Pre-A",
            ),
            audit,
            core=True,
        )

    hardening_matches = (
        []
        if explorations is None
        else [
            row
            for row in explorations
            if row.get("id") == HARDENING_EXPLORATION_ID
        ]
    )
    if not hardening_matches:
        audit.pending("EXP-000808 unique repair record", False, 0, 1, "formal")
    else:
        audit.check(
            "EXP-000808 unique repair record",
            len(hardening_matches) == 1,
            len(hardening_matches),
            1,
            "formal",
        )
    if len(hardening_matches) == 1:
        repair = hardening_matches[0]
        repair_refs = as_mapping(repair.get("formal_refs"))
        audit.check(
            "EXP-000808 exact repair identity sets",
            repair.get("task_id") == TASK_ID
            and repair.get("claim_ids") == list(CLAIM_IDS)
            and repair_refs.get("results") == [RESULT_NUMBER]
            and repair_refs.get("negatives") == []
            and tuple(repair.get("gate_ids", ())) == HARDENING_GATE_IDS,
            {
                "task": repair.get("task_id"),
                "claims": repair.get("claim_ids"),
                "formal_refs": repair_refs,
                "gates": repair.get("gate_ids"),
            },
            {
                "task": TASK_ID,
                "claims": CLAIM_IDS,
                "results": [RESULT_NUMBER],
                "negatives": [],
                "gates": HARDENING_GATE_IDS,
            },
            "formal",
        )
        require_tokens(
            json.dumps(repair, sort_keys=True),
            "EXP-000808 repair and boundary",
            (
                "exact declared fields and types",
                "candidate-bound",
                "discovery-source",
                "repository",
                "parsed HTTPS",
                "HMAC-SHA256",
                "informational only",
                "does not cryptographically verify",
                "actual freeze",
                "Pre-A closure",
            ),
            audit,
            core=True,
        )

    theorem_events = (
        []
        if changelog is None
        else [
            event
            for event in changelog
            if set(event.get("claim_ids", []))
            == {CLAIM_IDS[0], EXPLORATION_ID, RESULT_NUMBER}
        ]
    )
    if not theorem_events:
        audit.pending("R-168 theorem changelog", False, 0, 1, "formal")
    else:
        audit.check(
            "R-168 theorem changelog unique",
            len(theorem_events) == 1,
            len(theorem_events),
            1,
            "formal",
        )
    if len(theorem_events) == 1:
        event = theorem_events[0]
        audit.check(
            "R-168 theorem changelog exact sets",
            set(event.get("claim_ids", []))
            == {CLAIM_IDS[0], EXPLORATION_ID, RESULT_NUMBER}
            and event.get("neg_results") == list(NEGATIVE_IDS)
            and set(event.get("scripts", []))
            == {repo_path(PRIMARY), repo_path(INDEPENDENT)},
            event,
            "exact claim/result/exploration, negative, and verifier sets",
            "formal",
        )
        require_tokens(
            event.get("raw", ""),
            "R-168 theorem changelog boundary",
            ("No target", "cryptographic", "remote", "Sector A", "Pre-A"),
            audit,
            core=True,
        )
    repair_event_ids = {
        CLAIM_IDS[0],
        EXPLORATION_ID,
        HARDENING_EXPLORATION_ID,
        RESULT_NUMBER,
    }
    repair_events = (
        []
        if changelog is None
        else [
            event
            for event in changelog
            if set(event.get("claim_ids", [])) == repair_event_ids
        ]
    )
    if not repair_events:
        audit.pending("R-168 hardening changelog", False, 0, 1, "formal")
    else:
        audit.check(
            "R-168 hardening changelog unique",
            len(repair_events) == 1,
            len(repair_events),
            1,
            "formal",
        )
    if len(repair_events) == 1:
        repair_event = repair_events[0]
        audit.check(
            "R-168 hardening changelog exact sets",
            set(repair_event.get("claim_ids", []))
            == {
                CLAIM_IDS[0],
                EXPLORATION_ID,
                HARDENING_EXPLORATION_ID,
                RESULT_NUMBER,
            }
            and repair_event.get("neg_results") == list(NEGATIVE_IDS)
            and set(repair_event.get("scripts", []))
            == {repo_path(PRIMARY), repo_path(INDEPENDENT), repo_path(SCRIPT)},
            repair_event,
            "exact repair/exploration/result, negative, and verifier sets",
            "formal",
        )
        require_tokens(
            repair_event.get("raw", ""),
            "R-168 hardening changelog boundary",
            (
                "exact nested field sets and declared types",
                "candidate-bound",
                "discovery-source",
                "repo-confined",
                "parsed HTTPS",
                "canonical keyed-HMAC",
                "28 hostile classes",
                "informational and non-load-bearing",
                "no semantic free-text attestation",
                "Pre-A open",
            ),
            audit,
            core=True,
        )
    return {
        "exploration_count": len(explorations or []),
        "changelog_count": len(changelog or []),
        "exploration_matches": len(matches),
        "hardening_exploration_matches": len(hardening_matches),
        "theorem_event_matches": len(theorem_events),
        "hardening_event_matches": len(repair_events),
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
            "current total and recent R-168 theorem event",
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
    synthesis: dict[str, Any] = {}
    if manifest:
        synthesis = validate_manifest(manifest, audit)
    validate_certificate(audit)
    validate_firewall(audit)

    components: dict[str, dict[str, Any]] = {}
    sentinels: dict[str, dict[str, Any]] = {}
    with tempfile.TemporaryDirectory(prefix="tect-exp807-integrated-") as directory:
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
        validate_component(
            components["primary"], "primary", PRIMARY_SCHEMA, 125, audit
        )
        validate_source_hashes(
            components["primary"], (PRIMARY, MANIFEST, CERTIFICATE), audit, "primary"
        )
    if "independent" in components:
        validate_component(
            components["independent"],
            "independent",
            INDEPENDENT_SCHEMA,
            153,
            audit,
        )
        validate_source_hashes(
            components["independent"],
            INDEPENDENT_HASH_INPUTS,
            audit,
            "independent",
        )

    cross: dict[str, Any] = {}
    if "primary" in components and "independent" in components:
        cross = compare_components(components["primary"], components["independent"], audit)
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
        "hardening_exploration_id": HARDENING_EXPLORATION_ID,
        "parent_explorations": list(PARENT_EXPLORATIONS),
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "negative_ids": list(NEGATIVE_IDS),
        "reused_negative_ids": list(REUSED_NEGATIVE_IDS),
        "closed_subgates": list(CLOSED_SUBGATES),
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
            "combined_gate_level_checkpoint_deferred_during_development": False,
            "combined_gate_level_checkpoint_strictly_validated": (
                synthesis == EXPECTED_CHECKPOINT_SYNTHESIS
            ),
            "shared_with_R167_manifest": True,
            "manifest_checkpoint_synthesis": synthesis,
        },
        "scope": {
            "freeze_schema_shape_validated": True,
            "current_tree_readiness_audited": True,
            "actual_freeze_record_created": False,
            "git_tag_created": False,
            "external_target_commitment_present": False,
            "custodian_signature_cryptographically_verified": False,
            "remote_commit_fetched_and_verified": False,
            "remote_annotated_tag_fetched_and_verified": False,
            "remote_tag_ref_fetched_and_verified": False,
            "admitted_current_microscopic_map_present": False,
            "prospective_prediction_present": False,
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
