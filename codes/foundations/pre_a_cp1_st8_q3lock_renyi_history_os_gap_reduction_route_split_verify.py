#!/usr/bin/env python3
"""Integrated verifier for EXP-000805 / R-167 v1.8.

The primary and non-importing independent engines are each executed twice by
their command-line interfaces in fresh child processes.  This verifier checks
determinism, stored-result freshness, the independent-source firewall, exact
cross-engine invariants, formal authority linkage, and the single gate-level
synthesis PDF contract.

``--staged`` is deliberately fail-closed but assembly-safe.  An authority that
does not yet exist (including the final v0.7 synthesis source/PDF pair) is a
``MISSING`` row and yields ``INCOMPLETE`` with exit code zero.  A malformed or
contradictory authority, a stale stored result, or a mathematical mismatch is
always ``FAIL``.  Strict mode requires every authority and the one hash-bound,
text-extractable checkpoint PDF.  This script never imports either component,
builds a note, renders a PDF, or edits any authority.
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

try:
    from pypdf import PdfReader
except ImportError:  # Reported by the audit when a PDF is present.
    PdfReader = None  # type: ignore[assignment]


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-renyi-history-os-gap-reduction-route-split"

RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-"
    "COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
RESULT_NUMBER = "R-167"
RESULT_VERSION = "v1.8"
EXPLORATION_ID = "EXP-000805"
TASK_ID = "T-054"
CLAIM_ID = "C6-SPACETIME-SIGNATURE"

CLOSED_GATES = (
    "PA-CP1-ST8-Q3LOCK-FIXED-TROTTER-LOCAL-STRICT-INDUCTIVE-"
    "EXHAUSTION-COMPATIBILITY",
    "PA-CP1-ST8-Q3LOCK-SANDWICHED-RENYI-TO-TWO-ORIENTATION-HISTORY-"
    "TAIL-CORRIDOR-REDUCTION",
    "PA-CP1-ST8-Q3LOCK-PHASEWISE-GNS-GAP-OS-TEMPORAL-MASS-EQUIVALENCE",
    "PA-CP1-ST8-Q3LOCK-ONE-SITE-Q3-INSTANTON-ACTION-MINIMUM",
    "PA-CP1-ST8-Q3LOCK-CONDITIONAL-DOUBLET-ISING-REFERENCE-GAP",
)
SUCCESSOR_GATES = (
    "PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-"
    "HISTORY-COMMON-ALPHA",
    "PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY",
)
ROUND1_GATE = "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE"
OPEN_GATES = (*SUCCESSOR_GATES, ROUND1_GATE)
SUPERSEDED_GATES = (
    "PA-CP1-ST8-Q3LOCK-QUASI-LOCAL-RAW-OSCILLATOR-ALL-EXHAUSTION-"
    "COMMON-ALPHA-AND-BROKEN-GNS-GAP",
)
RETAINED_GATES = (
    "PA-CP1-ST8-Q3LOCK-ALL-EXHAUSTION-MIXTURE-L2-LOCALITY-AND-"
    "BETA-INDEPENDENT-CSTAR-DYNAMICS",
    "PA-CP1-ST8-Q3LOCK-HAMILTONIAN-THERMODYNAMIC-IDENTIFICATION-IN-"
    "CANONICAL-OS-MIXTURE",
    "PA-CP1-ST8-Q3LOCK-PROJECTED-DUHAMEL-MODULAR-C1-MULTIPLIER-LOCALITY",
)
NEGATIVE_IDS = (
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-ENERGY-FORM-ENTROPY-FINITE-"
    "MOMENT-AUTOMATIC-SANDWICHED-RENYI-UPGRADE",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-DIRECT-YAROTSKY-TWO-PHASE-GAP-IMPORT",
)
REUSED_NEGATIVE_IDS = (
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-ENTROPY-FINITE-MOMENT-DYNAMIC-"
    "GAUSSIAN-TAIL-INFERENCE",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-ORDERED-GROUND-DOUBLETS-AUTOMATIC-"
    "GNS-GAP",
)

PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260811.md"
NOTE_SOURCE = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/notes/"
    "pre-a-q3lock-renyi-history-os-gap-reduction-route-split-260811-v0.7.tex.txt"
)
CHECKPOINT_PDF = NOTE_SOURCE.with_name(
    NOTE_SOURCE.name.removesuffix(".tex.txt") + ".pdf"
)
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

PRIMARY_SCHEMA = f"tect/{SLUG}-primary-result/1.0"
INDEPENDENT_SCHEMA = f"tect/{SLUG}-independent-result/1.0"
INTEGRATED_SCHEMA = f"tect/{SLUG}-integrated-result/1.0"
MINIMUM_PRIMARY_ASSERTIONS = 120
MINIMUM_INDEPENDENT_ASSERTIONS = 100


def json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
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


def portable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def portable_sha256(path: Path) -> str:
    return hashlib.sha256(portable_bytes(path)).hexdigest()


def artifact_sha256(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return hashlib.sha256(path.read_bytes()).hexdigest()
    return portable_sha256(path)


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


def canonical_payload(value: Any) -> bytes:
    return json.dumps(
        json_safe(value), sort_keys=True, ensure_ascii=True, separators=(",", ":")
    ).encode("ascii")


def compact_text(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower().replace("\\", ""))


def text_has(text: Any, token: Any) -> bool:
    return compact_text(token) in compact_text(text)


def as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def as_fraction(value: Any) -> Fraction | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        return Fraction(str(value))
    if isinstance(value, str) and re.fullmatch(r"[+-]?\d+(?:/\d+)?", value.strip()):
        return Fraction(value.strip())
    return None


class Audit:
    """Collect contradictions separately from not-yet-issued authorities."""

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
        reporter(f"{label} exists", False, path.relative_to(REPO), "file", "files")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        audit.check(f"{label} parses", False, str(error), "valid JSON", "files")
        return None
    if not isinstance(value, dict):
        audit.check(f"{label} object", False, type(value).__name__, "dict", "files")
        return None
    audit.check(f"{label} parses", True, path.relative_to(REPO), "dict", "files")
    return value


def read_text(
    path: Path, audit: Audit, label: str, *, core: bool = False
) -> str | None:
    reporter = audit.check if core else audit.pending
    if not path.is_file():
        reporter(f"{label} exists", False, path.relative_to(REPO), "file", "files")
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        audit.check(f"{label} UTF-8", False, str(error), "readable UTF-8", "files")
        return None
    reporter(f"{label} nonempty", bool(text), len(text), ">0", "files")
    return text


def jsonl_records(path: Path, audit: Audit, label: str) -> list[dict[str, Any]] | None:
    if not path.is_file():
        audit.pending(f"{label} exists", False, path.relative_to(REPO), "file", "formal")
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


def run_once(
    component: Path, directory: Path, audit: Audit, label: str
) -> tuple[dict[str, Any], str] | None:
    if not component.is_file():
        audit.check(
            f"{label} script exists",
            False,
            component.relative_to(REPO),
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
        timeout=480,
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
    sentinel = next(
        (line.strip() for line in completed.stdout.splitlines() if line.strip()), ""
    )
    audit.check(f"{label} execution", True, completed.returncode, 0, "freshness")
    audit.check(
        f"{label} CLI sentinel",
        bool(re.match(r"^(PASS|INCOMPLETE)\s+\d+/\d+$", sentinel)),
        sentinel,
        "PASS|INCOMPLETE count/count",
        "freshness",
    )
    return payload, sentinel


def run_fresh_pair(
    component: Path, temporary_root: Path, audit: Audit, label: str
) -> tuple[dict[str, Any], str] | None:
    first = run_once(component, temporary_root / f"{label}-a", audit, f"{label} A")
    second = run_once(component, temporary_root / f"{label}-b", audit, f"{label} B")
    if first is None or second is None:
        audit.check(
            f"{label} two fresh runs",
            False,
            [first is not None, second is not None],
            [True, True],
            "freshness",
        )
        return first or second
    first_bytes = canonical_payload(first[0])
    second_bytes = canonical_payload(second[0])
    audit.check(
        f"{label} deterministic payload",
        first_bytes == second_bytes,
        {
            "a": hashlib.sha256(first_bytes).hexdigest(),
            "b": hashlib.sha256(second_bytes).hexdigest(),
        },
        "equal canonical hashes",
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
            path.relative_to(REPO),
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
    stored_bytes = canonical_payload(stored)
    fresh_bytes = canonical_payload(fresh) if fresh is not None else b""
    # An existing mismatch is stale evidence, never a staged absence.
    audit.check(
        f"{label} stored equals fresh",
        fresh is not None and stored_bytes == fresh_bytes,
        {
            "stored": hashlib.sha256(stored_bytes).hexdigest(),
            "fresh": hashlib.sha256(fresh_bytes).hexdigest() if fresh else None,
        },
        "equal canonical hashes",
        "freshness",
    )
    return stored


def validate_independence(audit: Audit) -> None:
    source = read_text(INDEPENDENT, audit, "independent source", core=True)
    if source is None:
        return
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        audit.check("independent AST parses", False, str(error), "valid AST", "firewall")
        return
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    primary_module = PRIMARY.stem
    forbidden_imports = [
        name
        for name in imported
        if primary_module in name or name in {"importlib", "runpy", "subprocess"}
    ]
    audit.check(
        "independent import firewall",
        not forbidden_imports,
        forbidden_imports,
        [],
        "firewall",
    )
    literals = [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    primary_result_fragment = f"2026-08-11-primary-{SLUG}"
    audit.check(
        "independent primary-result firewall",
        all(primary_result_fragment not in value for value in literals),
        [value for value in literals if primary_result_fragment in value],
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
        "integrated executes components without import",
        "subprocess.run" in integrated_source
        and all(
            name not in {"importlib", "runpy", primary_module, INDEPENDENT.stem}
            for name in integrated_imports
        ),
        integrated_imports,
        "CLI subprocess and no component/importlib/runpy import",
        "firewall",
    )


def validate_component(
    payload: dict[str, Any], label: str, schema: str, minimum: int, audit: Audit
) -> None:
    expected_top = {
        "schema": schema,
        "task_id": TASK_ID,
        "claim_ids": [CLAIM_ID],
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "exploration_id": EXPLORATION_ID,
        "claim_bearing": False,
        "negative_ids": list(NEGATIVE_IDS),
        "reused_negative_ids": list(REUSED_NEGATIVE_IDS),
        "closed_gates": list(CLOSED_GATES),
        "closed_subgates": list(CLOSED_GATES),
        "open_gates": list(OPEN_GATES),
        "successor_gates": list(SUCCESSOR_GATES),
        "superseded_gate_ids": list(SUPERSEDED_GATES),
        "retained_gates": list(RETAINED_GATES),
    }
    for field, expected in expected_top.items():
        audit.check(
            f"{label} {field}",
            payload.get(field) == expected,
            payload.get(field),
            expected,
            "component",
        )
    summary = as_mapping(payload.get("summary"))
    assertions = [row for row in as_list(payload.get("assertions")) if isinstance(row, dict)]
    allowed_verdicts = {"PASS", "INCOMPLETE"} if audit.staged else {"PASS"}
    audit.check(
        f"{label} verdict",
        payload.get("verdict") in allowed_verdicts,
        payload.get("verdict"),
        sorted(allowed_verdicts),
        "component",
    )
    audit.check(
        f"{label} assertion floor",
        len(assertions) >= minimum
        and summary.get("failed") == 0
        and all(row.get("status") == "PASS" for row in assertions),
        {"rows": len(assertions), "summary": summary},
        {"rows": f">={minimum}", "failed": 0, "statuses": "PASS"},
        "component",
    )
    scope = as_mapping(payload.get("scope"))
    false_scope = (
        ["Pre_A_complete", "Sector_A_complete", "all_exhaustion_common_alpha"]
        if label == "independent"
        else [
            "Pre_A_complete",
            "Sector_A_complete",
            "all_exhaustion_common_alpha",
            "actual_Q3_Renyi_history_bound",
            "broken_sector_GNS_gap",
            "C6_advanced",
        ]
    )
    audit.check(
        f"{label} no-overclaim scope",
        all(scope.get(key) is False for key in false_scope),
        {key: scope.get(key) for key in false_scope},
        {key: False for key in false_scope},
        "component",
    )


def validate_hash_map(
    payload: dict[str, Any], owner: Path, audit: Audit, label: str
) -> None:
    hashes = as_mapping(payload.get("source_hashes"))
    expected_paths = (owner, MANIFEST, CERTIFICATE)
    expected = {
        path.relative_to(REPO).as_posix(): portable_sha256(path)
        for path in expected_paths
        if path.is_file()
    }
    audit.check(
        f"{label} source hashes exact",
        hashes == expected,
        hashes,
        expected,
        "freshness",
    )


def validate_manifest(manifest: dict[str, Any], audit: Audit) -> None:
    expected = {
        "task_id": TASK_ID,
        "claim_ids": [CLAIM_ID],
        "exploration_id": EXPLORATION_ID,
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "claim_bearing": False,
        "negative_ids": list(NEGATIVE_IDS),
        "reused_negative_ids": list(REUSED_NEGATIVE_IDS),
        "closed_subgates": list(CLOSED_GATES),
        "open_gates": list(OPEN_GATES),
        "retained_gate_ids": list(RETAINED_GATES),
        "superseded_gate_ids": list(SUPERSEDED_GATES),
    }
    for field, value in expected.items():
        audit.check(
            f"manifest {field}",
            manifest.get(field) == value,
            manifest.get(field),
            value,
            "manifest",
        )
    for section in (
        "fixed_trotter_level_compatibility",
        "renyi_history_sufficiency",
        "renyi_energy_form_no_go",
        "zero_temperature_os_gap_equivalence",
        "q3_instanton_low_doublet_reference",
        "yarotsky_qps_boundary",
        "route_status",
        "checkpoint_synthesis",
        "verification",
        "no_overclaim",
    ):
        audit.check(
            f"manifest section {section}",
            section in manifest,
            section in manifest,
            True,
            "manifest",
        )
    verification = as_mapping(manifest.get("verification"))
    expected_scripts = {
        "primary_script": PRIMARY.relative_to(REPO).as_posix(),
        "independent_script": INDEPENDENT.relative_to(REPO).as_posix(),
        "integrated_script": SCRIPT.relative_to(REPO).as_posix(),
        "certificate": CERTIFICATE.relative_to(REPO).as_posix(),
    }
    for field, value in expected_scripts.items():
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
            "actual Q3LOCK sandwiched-Renyi history estimate",
            "n-to-infinity Trotter convergence",
            "broken-sector temporal mass",
            "prospective blind validation",
            "Sector A",
            "Pre-A closure",
        ),
        audit,
        core=True,
        group="manifest",
    )


def validate_certificate(audit: Audit) -> str | None:
    text = read_text(CERTIFICATE, audit, "certificate", core=True)
    if text is None:
        return None
    require_tokens(
        text,
        "certificate theorem chain",
        (
            EXPLORATION_ID,
            RESULT_NUMBER,
            RESULT_VERSION,
            RESULT_ID,
            *CLOSED_GATES,
            *SUCCESSOR_GATES,
            *NEGATIVE_IDS,
            "fixed Trotter level",
            "sandwiched-Renyi",
            "zero-temperature OS",
            "S_{\\rm inst}=36",
            "Yarotsky",
            "does not close Pre-A",
        ),
        audit,
        core=True,
        group="certificate",
    )
    audit.check(
        "certificate has no bare CR",
        CERTIFICATE.read_bytes().count(b"\r") == 0,
        CERTIFICATE.read_bytes().count(b"\r"),
        0,
        "certificate",
    )
    return text


def compare_exact_core(
    primary: dict[str, Any], independent: dict[str, Any], audit: Audit
) -> dict[str, Any]:
    pd = as_mapping(primary.get("derived"))
    ider = as_mapping(independent.get("derived"))
    pt = as_mapping(pd.get("fixed_trotter_level_compatibility"))
    it = as_mapping(ider.get("fixed_trotter_level_compatibility"))
    expected_word = {
        "-3": ["1000/9261", "0/1"],
        "-2": ["0/1", "-100/441"],
        "-1": ["-1940/3087", "0/1"],
        "0": ["0/1", "241/441"],
        "1": ["-1940/3087", "0/1"],
        "2": ["0/1", "-100/441"],
        "3": ["1000/9261", "0/1"],
    }
    audit.check(
        "cross fixed-Trotter support balls",
        pt.get("support_sizes") == it.get("support_sizes") == [1, 7, 25, 63],
        [pt.get("support_sizes"), it.get("support_sizes")],
        [1, 7, 25, 63],
        "cross_core",
    )
    audit.check(
        "cross constructive fixed word",
        pt.get("linear_proxy_full_word")
        == it.get("linear_proxy_full_word")
        == expected_word,
        [pt.get("linear_proxy_full_word"), it.get("linear_proxy_full_word")],
        expected_word,
        "cross_core",
    )
    trotter_flags = (
        pt.get("exact_exhaustion_independence_for_fixed_n") is True
        and it.get("fixed_level_exhaustion_independent") is True
        and pt.get("all_prefix_ambient_equal") is True
        and it.get("all_prefix_ambient_equal") is True
        and pt.get("all_prefix_support_in_N_b") is True
        and it.get("all_prefix_support_in_N_b") is True
        and pt.get("outer_halo_sharp") is True
        and it.get("outer_halo_sharp") is True
        and pt.get("reverse_recovers_seed") is True
        and it.get("reverse_recovers_seed") is True
        and pt.get("too_small_ambient_rejected") is True
        and it.get("too_small_ambient_rejected") is True
        and pt.get("n_to_infinity_cauchy_proved") is False
        and it.get("growing_level_cauchy") is False
        and pt.get("local_weyl_or_resolvent_invariance") is False
        and it.get("local_weyl_or_resolvent_invariance") is False
    )
    audit.check(
        "cross fixed-Trotter scope flags",
        trotter_flags,
        trotter_flags,
        True,
        "cross_core",
    )

    pr = as_mapping(pd.get("renyi_history_sufficiency"))
    ir = as_mapping(ider.get("renyi_history_sufficiency"))
    po = as_mapping(pr.get("noncommuting_orientation_fixture"))
    io = as_mapping(ir.get("orientation_fixture"))
    audit.check(
        "cross Q2 and projection slack",
        as_fraction(as_mapping(pr.get("commuting_swap_fixture")).get("sandwiched_Q_alpha"))
        == as_fraction(ir.get("Q2"))
        == Fraction(7, 3)
        and as_fraction(as_mapping(pr.get("commuting_swap_fixture")).get("slack_squared"))
        == as_fraction(ir.get("slack_squared"))
        == Fraction(1, 48),
        {
            "primary_Q2": as_mapping(pr.get("commuting_swap_fixture")).get("sandwiched_Q_alpha"),
            "independent_Q2": ir.get("Q2"),
        },
        {"Q2": "7/3", "slack": "1/48"},
        "cross_core",
    )
    orientation_values = (
        as_fraction(po.get("sandwiched_Q2_plus")),
        as_fraction(po.get("sandwiched_Q2_minus")),
        as_fraction(io.get("sandwiched_Q2_plus")),
        as_fraction(io.get("sandwiched_Q2_minus")),
    )
    audit.check(
        "cross noncommuting sandwiched orientations",
        all(value == Fraction(7301, 3125) for value in orientation_values)
        and as_fraction(po.get("q_plus"))
        == as_fraction(io.get("q_plus"))
        == Fraction(197, 250)
        and as_fraction(po.get("q_minus"))
        == as_fraction(io.get("q_minus"))
        == Fraction(53, 250),
        {"Q2": orientation_values, "q": [po.get("q_plus"), po.get("q_minus")]},
        {"Q2": "7301/3125", "q": ["197/250", "53/250"]},
        "cross_core",
    )
    audit.check(
        "cross Petz hostile discriminator",
        as_fraction(po.get("petz_Q2_plus"))
        == as_fraction(io.get("Petz_Q2"))
        == Fraction(61, 25)
        and Fraction(61, 25) != Fraction(7301, 3125),
        [po.get("petz_Q2_plus"), io.get("Petz_Q2")],
        "61/25 distinct from sandwiched",
        "cross_core",
    )
    pe = as_mapping(as_mapping(pr.get("bond_tail")).get("exact_fixture"))
    ie = as_mapping(ir.get("edge_fixture"))
    edge_expected = {
        "layer_polynomial": Fraction(313, 18),
        "one_orientation_prefactor": Fraction(3888, 25),
        "two_orientation_prefactor": Fraction(7776, 25),
        "final_rational_coefficient": Fraction(135216, 25),
    }
    audit.check(
        "cross exact edge constants",
        all(
            as_fraction(pe.get(key)) == as_fraction(ie.get(key)) == value
            for key, value in edge_expected.items()
        )
        and as_mapping(pr.get("bond_tail")).get("finite_edge_sum_power") == 2
        and ie.get("edge_count_power") == 2,
        {key: [pe.get(key), ie.get(key)] for key in edge_expected},
        edge_expected,
        "cross_core",
    )

    pn = as_mapping(pd.get("renyi_energy_form_no_go"))
    ino = as_mapping(ider.get("renyi_energy_form_no_go"))
    pc = as_mapping(pn.get("exact_compact_oracle_n2_m3"))
    ic = as_mapping(ino.get("compact_oracle"))
    compact_expected = {
        "p0": "65536/65537",
        "p1": "1/65537",
        "cosine": "255/257",
        "sine": "32/257",
        "q": "261377/16843009",
        "trace_G": "2507810/1122833",
        "measured_Q2": "1106449/66049",
        "sandwiched_Q2": "106339353113/4328653313",
        "sandwiched_minus_measured": "33826005000/4328653313",
        "q_squared_over_p1": "68317936129/4328653313",
    }
    audit.check(
        "cross exact Renyi no-go compact oracle",
        pc == ic == compact_expected,
        {"primary": pc, "independent": ic},
        compact_expected,
        "cross_core",
    )
    audit.check(
        "cross no-go scope",
        pn.get("uniform_Renyi_inferred") is False
        and pn.get("actual_Q3_Renyi_rejected") is False
        and ino.get("uniform_Renyi") is False
        and ino.get("Q3_counterexample") is False,
        {
            "primary": [pn.get("uniform_Renyi_inferred"), pn.get("actual_Q3_Renyi_rejected")],
            "independent": [ino.get("uniform_Renyi"), ino.get("Q3_counterexample")],
        },
        [False, False],
        "cross_core",
    )

    pos = as_mapping(pd.get("zero_temperature_os_gap_equivalence"))
    ios = as_mapping(ider.get("zero_temperature_os_gap_equivalence"))
    audit.check(
        "primary OS exact fixture",
        as_fraction(pos.get("G_0")) == 1
        and as_fraction(pos.get("gap")) == 3
        and as_fraction(pos.get("hbar")) == 2
        and as_fraction(pos.get("decay_rate")) == Fraction(3, 2)
        and as_fraction(pos.get("coercivity_residual")) == Fraction(10, 9)
        and pos.get("requires_zero_temperature_sector_representation") is True
        and pos.get("current_beta_uniform_temporal_rate_proved") is False,
        pos,
        "exact primary OS fixture and open physical rate",
        "cross_core",
    )
    audit.check(
        "independent OS exact hostile fixture",
        as_fraction(ios.get("variance")) == Fraction(181, 225)
        and as_fraction(ios.get("energy")) == Fraction(113, 75)
        and as_fraction(ios.get("margin")) == Fraction(3, 10)
        and as_fraction(ios.get("decay_rate")) == Fraction(3, 4)
        and as_mapping(ios.get("hostile_kernel")).get("simple_kernel") is False
        and ios.get("actual_Q3_temporal_rate") is False
        and ios != pos,
        ios,
        "distinct exact independent OS fixture",
        "cross_core",
    )

    pq3 = as_mapping(pd.get("q3_instanton_low_doublet_reference"))
    pi = as_mapping(pq3.get("instanton"))
    ii = as_mapping(ider.get("q3_instanton"))
    audit.check(
        "cross exact instanton action",
        as_fraction(pi.get("action"))
        == as_fraction(ii.get("total_action"))
        == 36
        and pi.get("q3_edge_count") == ii.get("edge_count") == 12
        and pi.get("locked_minimizer_unique_up_to_common_translation_for_lambda_positive")
        is True
        and ii.get("lambda_positive_locked_unique_up_to_common_shift") is True
        and ii.get("tunnelling_bound_proved") is False,
        {"primary": pi, "independent": ii},
        {"action": 36, "edges": 12, "splitting": False},
        "cross_core",
    )
    plow = as_mapping(pq3.get("low_doublet"))
    ilow = as_mapping(ider.get("conditional_doublet_ising_reference"))
    audit.check(
        "primary conditional reference gap",
        as_fraction(plow.get("J")) == Fraction(6, 5)
        and plow.get("periodic_C3_cubed_min_cut") == 6
        and as_fraction(plow.get("reference_gap_lower_bound")) == 5
        and as_fraction(plow.get("low_sector_gap")) == Fraction(72, 5)
        and plow.get("bond_decomposition_residual_zero") is True,
        plow,
        {"J": "6/5", "cut": 6, "lower_bound": 5, "low_gap": "72/5"},
        "cross_core",
    )
    audit.check(
        "independent C4 reference gap",
        as_fraction(ilow.get("J")) == 4
        and ilow.get("kernel_dimension") == 2
        and as_fraction(ilow.get("C4_first_positive"))
        == as_fraction(ilow.get("predicted_C4_gap"))
        == 16
        and ilow.get("Z2_cube_multigraph_edge_connectivity") == 6
        and ilow.get("actual_Q3_reduction") is False
        and pq3.get("actual_relative_QPS_smallness_proved") is False
        and pq3.get("actual_broken_sector_gap_proved") is False,
        ilow,
        {"J": 4, "kernel": 2, "C4_gap": 16, "Q3_reduction": False},
        "cross_core",
    )
    return {
        "support_sizes": [1, 7, 25, 63],
        "linear_proxy_full_word": expected_word,
        "sandwiched_Q2": "7301/3125",
        "Petz_Q2": "61/25",
        "orientation_events": ["197/250", "53/250"],
        "edge_final_rational_coefficient": "135216/25",
        "compact_Renyi_no_go": compact_expected,
        "primary_OS_rate": "3/2",
        "independent_OS_rate": "3/4",
        "instanton_action": 36,
        "primary_reference_gap_lower_bound": 5,
        "independent_C4_reference_gap": 16,
        "actual_Q3_history_or_gap_closed": False,
    }


def validate_formal(manifest: dict[str, Any], audit: Audit) -> dict[str, Any]:
    explorations = jsonl_records(REPO / "explorations/log.jsonl", audit, "exploration ledger")
    matches = [] if explorations is None else [row for row in explorations if row.get("id") == EXPLORATION_ID]
    if len(matches) == 0:
        audit.pending("EXP-000805 unique record", False, 0, 1, "formal")
    else:
        audit.check("EXP-000805 unique record", len(matches) == 1, len(matches), 1, "formal")
    if len(matches) == 1:
        record = matches[0]
        serialized = json.dumps(record, sort_keys=True)
        audit.check(
            "EXP-000805 exact provenance",
            record.get("schema") == "tect/proof-exploration/1.0"
            and record.get("task_id") == TASK_ID
            and record.get("claim_ids") == [CLAIM_ID]
            and record.get("verdict") == "advanced"
            and as_mapping(record.get("formal_refs")).get("results") == [RESULT_NUMBER]
            and set(as_mapping(record.get("formal_refs")).get("negatives", ()))
            == set(NEGATIVE_IDS)
            and all(text_has(serialized, token) for token in (*CLOSED_GATES, *OPEN_GATES)),
            record,
            "exact claim/result/negative/gate provenance",
            "formal",
        )

    result_ledger = read_text(REPO / "RESULTS-LEDGER.md", audit, "result ledger")
    if result_ledger is not None:
        section = heading_section(result_ledger, RESULT_NUMBER)
        audit.pending("R-167 result section exists", section is not None, section, "section", "formal")
        if section is not None:
            require_tokens(
                section,
                "R-167 v1.8 result authority",
                (
                    RESULT_VERSION,
                    EXPLORATION_ID,
                    "fixed Trotter",
                    "sandwiched-Renyi",
                    "OS",
                    "instanton",
                    *CLOSED_GATES,
                    *SUCCESSOR_GATES,
                    *NEGATIVE_IDS,
                    "T0",
                ),
                audit,
            )

    negatives = read_text(REPO / "negative-results/registry.md", audit, "negative registry")
    if negatives is not None:
        require_tokens(negatives, "v1.8 negative authorities", NEGATIVE_IDS, audit)

    gates = read_text(REPO / "claims/GATES.md", audit, "gate registry")
    if gates is not None:
        for gate in CLOSED_GATES:
            section = heading_section(gates, gate)
            audit.pending(f"closed gate section {gate}", section is not None, section, "section", "formal")
            if section is not None:
                audit.pending(
                    f"closed gate scoped status {gate}",
                    re.search(r"\*\*Status:\*\*\s*CLOSED", section, re.I) is not None
                    and text_has(section, EXPLORATION_ID)
                    and text_has(section, RESULT_VERSION),
                    section,
                    "scoped CLOSED under EXP-000805/R-167 v1.8",
                    "formal",
                )
        for gate in OPEN_GATES:
            section = heading_section(gates, gate)
            audit.pending(f"open gate section {gate}", section is not None, section, "section", "formal")
            if section is not None:
                audit.pending(
                    f"open gate remains open {gate}",
                    re.search(r"\*\*Status:\*\*\s*OPEN", section, re.I) is not None,
                    section,
                    "OPEN",
                    "formal",
                )
        historical = heading_section(gates, SUPERSEDED_GATES[0])
        audit.pending(
            "historical combined gate split not closed",
            historical is not None
            and text_has(historical, "historical")
            and text_has(historical, "not closed"),
            historical,
            "historically split and not closed",
            "formal",
        )

    strategy_index = read_text(REPO / "strategy/INDEX.md", audit, "strategy index")
    if strategy_index is not None:
        require_tokens(
            strategy_index,
            "strategy v1.8 authority links",
            (MANIFEST.name, CERTIFICATE.name),
            audit,
        )

    roadmap = read_text(REPO / "ROADMAP.md", audit, "roadmap")
    if roadmap is not None:
        require_tokens(
            roadmap,
            "roadmap v1.8 linkage",
            (TASK_ID, EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, *SUCCESSOR_GATES, ROUND1_GATE),
            audit,
        )
    todo = load_json(REPO / "todo/todo.json", audit, "TODO authority")
    if todo is not None:
        tasks = [row for row in as_list(todo.get("tasks")) if isinstance(row, dict) and row.get("id") == TASK_ID]
        audit.pending("T-054 unique", len(tasks) == 1, len(tasks), 1, "formal")
        if len(tasks) == 1:
            serialized = json.dumps(tasks[0], sort_keys=True)
            note = str(tasks[0].get("note", ""))
            live_task_conditions = {
                "status": tasks[0].get("status") == "in_progress",
                "round1_gate": tasks[0].get("gate") == ROUND1_GATE,
                "common_alpha_successors_open": text_has(note, "common alpha")
                and text_has(note, "remain open"),
                "sector_a_and_pre_a_open": text_has(note, "physical Sector A")
                and text_has(note, "Pre-A"),
            }
            audit.pending(
                "T-054 current Round-1/common-alpha contract",
                all(live_task_conditions.values()),
                live_task_conditions,
                "current in-progress Round-1 task with common-alpha and Sector-A/Pre-A open boundary",
                "formal",
            )

    theorem_map = load_json(
        REPO / "governance/sector-a-theorem-map.json", audit, "Sector-A theorem map"
    )
    if theorem_map is not None:
        priority = as_mapping(theorem_map.get("research_priority"))
        current_contract = {
            "schema": theorem_map.get("schema") == "tect/sector-a-theorem-map/1.0",
            "status": theorem_map.get("status") == "ACTIVE",
            "priority_status": priority.get("status") == "IN_PROGRESS",
            "dynamics_successor": priority.get("parallel_cp1_gate") == SUCCESSOR_GATES[0],
            "gap_successor": priority.get("parallel_cp1_gap_gate") == SUCCESSOR_GATES[1],
            "pre_a_boundary": "Pre-A" in json.dumps(theorem_map, sort_keys=True)
            and "remain open" in json.dumps(theorem_map, sort_keys=True),
        }
        audit.pending(
            "Sector-A theorem map current successor contract",
            all(current_contract.values()),
            current_contract,
            "current Sector-A map with live successor gates and open Pre-A boundary",
            "formal",
        )

    changelog = jsonl_records(REPO / "changelog/log.jsonl", audit, "changelog")
    exp_events = [] if changelog is None else [event for event in changelog if text_has(json.dumps(event, sort_keys=True), EXPLORATION_ID)]
    required_scripts = {
        PRIMARY.relative_to(REPO).as_posix(),
        INDEPENDENT.relative_to(REPO).as_posix(),
        SCRIPT.relative_to(REPO).as_posix(),
    }
    theorem_events = [
        event
        for event in exp_events
        if set(event.get("neg_results", ())) == set(NEGATIVE_IDS)
        and required_scripts.issubset(set(event.get("scripts", ())))
        and event.get("notes") == []
    ]
    if not theorem_events:
        audit.pending("EXP-000805 theorem changelog unique", False, 0, 1, "formal")
    else:
        audit.check("EXP-000805 theorem changelog unique", len(theorem_events) == 1, len(theorem_events), 1, "formal")
    if len(theorem_events) == 1:
        event = theorem_events[0]
        raw = event.get("raw", "")
        audit.pending(
            "EXP-000805 theorem changelog complete",
            set(event.get("claim_ids", ())) == {CLAIM_ID, EXPLORATION_ID, RESULT_NUMBER}
            and all(
                text_has(raw, token)
                for token in (
                    RESULT_VERSION,
                    "fixed",
                    "Renyi",
                    "OS",
                    "Pre-A remain open",
                    "single later gate-level synthesis PDF",
                )
            )
            and ".tex.txt" not in raw.lower()
            and not re.search(r"claims/[A-Za-z0-9_./-]+\.pdf", raw, re.I),
            event,
            "claim/result/scope linkage with notes deferred",
            "formal",
        )

    proof_map = read_text(REPO / "theory/proof-evidence-map.md", audit, "proof-evidence map")
    if proof_map is not None:
        require_tokens(
            proof_map,
            "proof-evidence v1.8 linkage",
            (EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, *CLOSED_GATES, *OPEN_GATES, *NEGATIVE_IDS),
            audit,
        )
    proof_json = load_json(
        REPO / "verification/proof-evidence-map.json", audit, "proof-evidence JSON"
    )
    if proof_json is not None:
        coverage = proof_json.get("coverage", {})
        shards = proof_json.get("shards", [])
        shard_kinds = (
            {item.get("kind") for item in shards if isinstance(item, dict)}
            if isinstance(shards, list)
            else set()
        )
        digest = proof_json.get("logical_map_sha256")
        json_contract = {
            "index_schema": proof_json.get("schema") == "tect/proof-evidence-map-index/1.0",
            "map_schema": proof_json.get("map_schema") == "tect/proof-evidence-map/1.3",
            "generator_pinned": isinstance(proof_json.get("generator"), dict)
            and proof_json["generator"].get("path")
            == "verification/scripts/build_proof_evidence_map.py",
            "logical_digest": isinstance(digest, str)
            and len(digest) == 64
            and all(char in "0123456789abcdef" for char in digest.lower()),
            "coverage_fields": isinstance(coverage, dict)
            and {
                "proof_explorations",
                "reusable_results",
                "negative_records",
                "accepted_events",
                "tasks",
            }.issubset(coverage),
            "shards_present": {
                "proof_explorations",
                "reusable_results",
                "negative_records",
            }.issubset(shard_kinds),
        }
        audit.pending(
            "proof-evidence JSON current structural contract",
            all(json_contract.values()),
            json_contract,
            "current indexed proof-map schema, generator, digest, coverage fields and shards",
            "formal",
        )

    locator_specs = (
        (
            REPO / "results/index.json",
            "result locator",
            "tect/results-index/1.0",
            "RESULTS-LEDGER.md",
        ),
        (
            REPO / "negative-results/index.json",
            "negative locator",
            "tect/negative-index/1.0",
            "negative-results/registry.md",
        ),
        (
            REPO / "changelog/index.json",
            "changelog locator",
            "tect/changelog-index/2.0",
            "changelog/log.jsonl",
        ),
    )
    locator_counts: dict[str, int] = {}
    for path, label, schema, authority in locator_specs:
        payload = load_json(path, audit, label)
        if payload is None:
            continue
        entries = [
            row for row in as_list(payload.get("entries"))
            if isinstance(row, dict)
        ]
        if label == "changelog locator":
            entries = as_list(payload.get("recent"))
            count_ok = (
                payload.get("total") == len(changelog or [])
                and payload.get("recent_count") == len(entries)
                and isinstance(payload.get("recent_count"), int)
                and payload["recent_count"] <= payload.get("total", -1)
            )
            actual_count = payload.get("total")
        else:
            count_ok = payload.get("count") == len(entries)
            actual_count = payload.get("count")
        contract = {
            "schema": payload.get("schema") == schema,
            "authority": payload.get("authority") == authority,
            "count": count_ok,
            "entries_nonempty": len(entries) > 0,
        }
        audit.pending(
            f"{label} current structural contract",
            all(contract.values()),
            contract,
            "current generated locator with authority and consistent counts",
            "formal",
        )
        if isinstance(actual_count, int):
            locator_counts[label] = actual_count

    result_index = read_text(REPO / "results/INDEX.md", audit, "result index")
    if result_index is not None and "result locator" in locator_counts:
        require_tokens(
            result_index,
            "result index current generated projection",
            (
                "AUTO-GENERATED by verification/scripts/build_management_indexes.py",
                f"{locator_counts['result locator']} registered results",
            ),
            audit,
        )
    negative_index = read_text(REPO / "negative-results/INDEX.md", audit, "negative index")
    if negative_index is not None and "negative locator" in locator_counts:
        require_tokens(
            negative_index,
            "negative index current generated projection",
            (
                "AUTO-GENERATED by verification/scripts/build_management_indexes.py",
                f"{locator_counts['negative locator']} registered records",
            ),
            audit,
        )
    changelog_index = read_text(REPO / "changelog/INDEX.md", audit, "changelog index")
    if changelog_index is not None and "changelog locator" in locator_counts:
        require_tokens(
            changelog_index,
            "changelog index current generated projection",
            (
                "Compact generated reader surface",
                f"{locator_counts['changelog locator']} accepted events",
                "machine locator",
            ),
            audit,
        )

    gate_index = read_text(REPO / "claims/GATES-INDEX.md", audit, "gate index")
    if gate_index is not None and gates is not None:
        gate_definition_count = len(
            re.findall(r"^###\s+", gates, flags=re.MULTILINE)
        )
        require_tokens(
            gate_index,
            "gate index current definition count",
            (f"{gate_definition_count} registered definitions",),
            audit,
        )

    compact_proof = read_text(
        REPO / "theory/proof-evidence/INDEX.md", audit, "compact proof index"
    )
    if compact_proof is not None:
        require_tokens(
            compact_proof,
            "compact proof index current authority counts",
            (
                f"{len(explorations or [])} proof explorations",
                f"{len(changelog or [])} accepted events",
            ),
            audit,
        )

    catalog = load_json(REPO / "verification/catalog/index.json", audit, "catalog manifest")
    catalog_inventory = ""
    if catalog is not None:
        shards = as_list(catalog.get("shards"))
        valid = []
        payloads: list[dict[str, Any]] = []
        for shard in shards:
            if not isinstance(shard, dict) or not isinstance(shard.get("path"), str):
                valid.append(False)
                continue
            path = REPO / shard["path"]
            payload = load_json(path, audit, f"catalog shard {shard.get('kind', shard['path'])}")
            if payload is None:
                valid.append(False)
                continue
            payloads.append(payload)
            valid.append(
                hashlib.sha256(path.read_bytes()).hexdigest() == shard.get("sha256")
                and payload.get("count") == shard.get("count") == len(as_list(payload.get("entries")))
            )
        audit.pending(
            "catalog manifest and shards current",
            catalog.get("schema") == "tect/catalog-manifest/2.0"
            and bool(shards)
            and len(valid) == len(shards)
            and all(valid)
            and sum(int(shard.get("count", 0)) for shard in shards if isinstance(shard, dict)) == catalog.get("total"),
            {"shards": len(shards), "valid": sum(valid), "total": catalog.get("total")},
            "valid hashes/counts and total",
            "formal",
        )
        catalog_inventory = json.dumps(payloads, sort_keys=True)
        require_tokens(
            catalog_inventory,
            "catalog v1.8 core artifacts",
            (
                MANIFEST.relative_to(REPO).as_posix(),
                CERTIFICATE.relative_to(REPO).as_posix(),
                PRIMARY.relative_to(REPO).as_posix(),
                INDEPENDENT.relative_to(REPO).as_posix(),
                SCRIPT.relative_to(REPO).as_posix(),
            ),
            audit,
        )

    status = load_json(
        REPO / "claims/C6-SPACETIME-SIGNATURE/status.json", audit, "C6 status", core=True
    )
    if status is not None:
        audit.check("C6 tier unchanged", status.get("tier") == "T1", status.get("tier"), "T1", "claim_firewall")
        audit.check("C6 lifecycle unchanged", status.get("lifecycle") == "ACTIVE", status.get("lifecycle"), "ACTIVE", "claim_firewall")
        audit.check(
            "C6 open gate unchanged",
            status.get("open_gates") == ["C6-BCC-PREMISE-BLOCKED"],
            status.get("open_gates"),
            ["C6-BCC-PREMISE-BLOCKED"],
            "claim_firewall",
        )
    return {
        "exploration_matches": len(matches),
        "theorem_changelog_matches": len(theorem_events),
        "catalog_inventory": catalog_inventory,
        "changelog": changelog,
    }


def validate_pdf_checkpoint(
    manifest: dict[str, Any], certificate: str | None, formal: dict[str, Any], audit: Audit
) -> dict[str, Any]:
    checkpoint = as_mapping(manifest.get("checkpoint_synthesis"))
    note_relative = NOTE_SOURCE.relative_to(REPO).as_posix()
    pdf_relative = CHECKPOINT_PDF.relative_to(REPO).as_posix()
    note_matches = sorted(NOTE_SOURCE.parent.glob(f"{NOTE_SOURCE.stem.split('-260811-')[0]}-*.tex.txt"))
    pdf_matches = sorted(NOTE_SOURCE.parent.glob(f"{NOTE_SOURCE.stem.split('-260811-')[0]}-*.pdf"))
    audit.pending("single checkpoint source exists", NOTE_SOURCE.is_file(), note_matches, [NOTE_SOURCE], "pdf")
    audit.pending("single checkpoint PDF exists", CHECKPOINT_PDF.is_file(), pdf_matches, [CHECKPOINT_PDF], "pdf")
    if note_matches:
        audit.check("no intermediate synthesis sources", note_matches == [NOTE_SOURCE], note_matches, [NOTE_SOURCE], "pdf")
    if pdf_matches:
        audit.check("no intermediate synthesis PDFs", pdf_matches == [CHECKPOINT_PDF], pdf_matches, [CHECKPOINT_PDF], "pdf")

    for field, expected in (("source", note_relative), ("pdf", pdf_relative)):
        if field not in checkpoint:
            audit.pending(f"manifest checkpoint {field}", False, None, expected, "pdf")
        else:
            audit.check(
                f"manifest checkpoint {field}",
                checkpoint.get(field) == expected,
                checkpoint.get(field),
                expected,
                "pdf",
            )
    workflow = checkpoint.get("workflow", "")
    if not workflow or text_has(checkpoint.get("status", ""), "DEFERRED"):
        audit.pending("manifest checkpoint workflow finalized", False, checkpoint, "final checkpoint metadata", "pdf")
    else:
        audit.check(
            "manifest checkpoint workflow finalized",
            all(text_has(workflow, token) for token in ("No per-lemma", "single gate-level synthesis", "manifest", "certificate", "primary", "independent", "integrated")),
            workflow,
            "one post-validation synthesis with no intermediate PDF",
            "pdf",
        )

    source_hash = portable_sha256(NOTE_SOURCE) if NOTE_SOURCE.is_file() else None
    pdf_hash = hashlib.sha256(CHECKPOINT_PDF.read_bytes()).hexdigest() if CHECKPOINT_PDF.is_file() else None
    for field, actual in (("source_sha256", source_hash), ("pdf_sha256", pdf_hash)):
        if field not in checkpoint or actual is None:
            audit.pending(f"manifest checkpoint {field}", False, checkpoint.get(field), actual or "fresh hash", "pdf")
        else:
            audit.check(
                f"manifest checkpoint {field}",
                checkpoint.get(field) == actual,
                checkpoint.get(field),
                actual,
                "pdf",
            )

    source_text: str | None = None
    if NOTE_SOURCE.is_file():
        try:
            source_text = NOTE_SOURCE.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            audit.check("checkpoint source UTF-8", False, str(error), "readable UTF-8", "pdf")
        if source_text is not None:
            audit.check(
                "checkpoint source form",
                bool(source_text.strip())
                and "\\begin{document}" not in source_text
                and "\\end{document}" not in source_text
                and any(
                    text_has(source_text, token)
                    for token in ("remain open", "does not close", "does not prove")
                )
                and NOTE_SOURCE.read_bytes().count(b"\r") == 0,
                {
                    "nonempty": bool(source_text.strip()),
                    "has_begin_document": "\\begin{document}" in source_text,
                    "has_end_document": "\\end{document}" in source_text,
                    "explicit_open_boundary": any(
                        text_has(source_text, token)
                        for token in ("remain open", "does not close", "does not prove")
                    ),
                    "bare_CR": NOTE_SOURCE.read_bytes().count(b"\r"),
                },
                "nonempty LF-only TeX fragment with no document environment and an explicit open boundary",
                "pdf",
            )
            require_tokens(
                source_text,
                "checkpoint source theorem and boundary",
                (EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, "fixed Trotter", "sandwiched", "OS", "instanton", "Pre-A", *SUCCESSOR_GATES),
                audit,
                core=True,
                group="pdf",
            )

    pages = 0
    nonempty_pages = 0
    extracted = ""
    if CHECKPOINT_PDF.is_file():
        audit.check(
            "checkpoint PDF header",
            CHECKPOINT_PDF.read_bytes().startswith(b"%PDF-"),
            CHECKPOINT_PDF.read_bytes()[:8],
            b"%PDF-",
            "pdf",
        )
        if PdfReader is None:
            audit.check("pypdf available", False, None, "PdfReader", "pdf")
        else:
            try:
                reader = PdfReader(str(CHECKPOINT_PDF))
                texts = [(page.extract_text() or "").strip() for page in reader.pages]
                pages = len(texts)
                nonempty_pages = sum(bool(text) for text in texts)
                extracted = "\n".join(texts)
                audit.check("checkpoint PDF parses", pages > 0, pages, ">0", "pdf")
                audit.check("checkpoint PDF all pages extract", nonempty_pages == pages, nonempty_pages, pages, "pdf")
                require_tokens(
                    extracted,
                    "checkpoint PDF theorem and boundary text",
                    (EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, "fixed Trotter", "sandwiched", "OS", "instanton", "Pre-A"),
                    audit,
                    core=True,
                    group="pdf",
                )
            except Exception as error:  # pypdf exposes several parser exceptions.
                audit.check("checkpoint PDF parses", False, str(error), "readable PDF", "pdf")
        if NOTE_SOURCE.is_file():
            audit.check(
                "checkpoint PDF fresh after source",
                CHECKPOINT_PDF.stat().st_mtime_ns >= NOTE_SOURCE.stat().st_mtime_ns,
                [CHECKPOINT_PDF.stat().st_mtime_ns, NOTE_SOURCE.stat().st_mtime_ns],
                "pdf mtime >= source mtime",
                "pdf",
            )

    if "pages" not in checkpoint or pages == 0:
        audit.pending("manifest checkpoint page count", False, checkpoint.get("pages"), pages or ">0", "pdf")
    else:
        audit.check("manifest checkpoint page count", checkpoint.get("pages") == pages, checkpoint.get("pages"), pages, "pdf")
    visual = checkpoint.get("visual_qa", "")
    if not visual:
        audit.pending("manifest visual QA recorded", False, visual, "rendered-page visual review", "pdf")
    else:
        audit.check(
            "manifest visual QA recorded",
            all(text_has(visual, token) for token in ("rendered", "pages", "zero clipping", "overlap", "broken", "unreadable")),
            visual,
            "rendered pages with zero visual defects",
            "pdf",
        )

    inventory = formal.get("catalog_inventory", "")
    if inventory:
        require_tokens(inventory, "catalog checkpoint artifacts", (note_relative, pdf_relative), audit)
    changelog = formal.get("changelog")
    events = [] if not isinstance(changelog, list) else [
        event
        for event in changelog
        if note_relative in json.dumps(event, sort_keys=True)
        and pdf_relative in json.dumps(event, sort_keys=True)
    ]
    if not events:
        audit.pending("v1.8 checkpoint changelog unique", False, 0, 1, "pdf")
    else:
        audit.check("v1.8 checkpoint changelog unique", len(events) == 1, len(events), 1, "pdf")
    if len(events) == 1:
        event = events[0]
        raw = event.get("raw", "")
        audit.check(
            "v1.8 checkpoint changelog complete",
            {CLAIM_ID, RESULT_NUMBER}.issubset(set(event.get("claim_ids", ())))
            and note_relative in event.get("notes", ())
            and pdf_relative in event.get("notes", ())
            and all(text_has(raw, token) for token in ("No per-lemma", "one gate-level synthesis", "manifest", "certificate", "primary", "independent", "integrated", "render", "visual", "No result number", "gate status", "tier", "no-overclaim")),
            event,
            "single checkpoint workflow event",
            "pdf",
        )
    return {
        "source": note_relative,
        "pdf": pdf_relative,
        "source_sha256": source_hash,
        "pdf_sha256": pdf_hash,
        "pages": pages,
        "nonempty_pages": nonempty_pages,
        "manifest": checkpoint,
        "certificate_present": certificate is not None,
    }


def build_payload(staged: bool = False) -> dict[str, Any]:
    audit = Audit(staged)
    manifest = load_json(MANIFEST, audit, "manifest", core=True) or {}
    if manifest:
        validate_manifest(manifest, audit)
    certificate = validate_certificate(audit)
    validate_independence(audit)

    components: dict[str, dict[str, Any]] = {}
    sentinels: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="tect-exp805-integrated-") as directory:
        temporary = Path(directory)
        for label, component in (("primary", PRIMARY), ("independent", INDEPENDENT)):
            result = run_fresh_pair(component, temporary, audit, label)
            if result is not None:
                components[label], sentinels[label] = result

    stored_against_fresh(PRIMARY_STORED, components.get("primary"), audit, "primary")
    stored_against_fresh(INDEPENDENT_STORED, components.get("independent"), audit, "independent")

    if "primary" in components:
        validate_component(components["primary"], "primary", PRIMARY_SCHEMA, MINIMUM_PRIMARY_ASSERTIONS, audit)
        validate_hash_map(components["primary"], PRIMARY, audit, "primary")
    if "independent" in components:
        validate_component(components["independent"], "independent", INDEPENDENT_SCHEMA, MINIMUM_INDEPENDENT_ASSERTIONS, audit)
        validate_hash_map(components["independent"], INDEPENDENT, audit, "independent")

    cross: dict[str, Any] = {}
    if "primary" in components and "independent" in components:
        cross = compare_exact_core(components["primary"], components["independent"], audit)
    else:
        audit.check("fresh exact cross-comparison", False, sorted(components), ["primary", "independent"], "cross_core")

    formal = validate_formal(manifest, audit)
    pdf = validate_pdf_checkpoint(manifest, certificate, formal, audit)
    passed = sum(row["status"] == "PASS" for row in audit.rows)
    source_paths = (
        SCRIPT,
        PRIMARY,
        INDEPENDENT,
        MANIFEST,
        CERTIFICATE,
        PRIMARY_STORED,
        INDEPENDENT_STORED,
        NOTE_SOURCE,
        CHECKPOINT_PDF,
    )
    source_hashes = {
        path.relative_to(REPO).as_posix(): artifact_sha256(path)
        for path in source_paths
        if path.is_file()
    }
    return {
        "schema": INTEGRATED_SCHEMA,
        "script_version": __version__,
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "exploration_id": EXPLORATION_ID,
        "task_id": TASK_ID,
        "claim_ids": [CLAIM_ID],
        "claim_bearing": False,
        "negative_ids": list(NEGATIVE_IDS),
        "reused_negative_ids": list(REUSED_NEGATIVE_IDS),
        "closed_gates": list(CLOSED_GATES),
        "successor_gates": list(SUCCESSOR_GATES),
        "superseded_gate_ids": list(SUPERSEDED_GATES),
        "retained_gates": list(RETAINED_GATES),
        "open_gates": list(OPEN_GATES),
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
        "fresh_sentinels": sentinels,
        "cross_derived": cross,
        "scope": {
            "fixed_trotter_level_exhaustion_compatibility": True,
            "conditional_sandwiched_Renyi_history_reduction": True,
            "zero_temperature_OS_GNS_gap_equivalence": True,
            "one_site_instanton_action_minimum": True,
            "conditional_doublet_Ising_reference_gap": True,
            "actual_Q3_Renyi_history_bound": False,
            "n_to_infinity_split_limit": False,
            "all_exhaustion_common_alpha": False,
            "beta_infinity_phase_selection": False,
            "actual_broken_sector_temporal_mass": False,
            "actual_broken_sector_GNS_gap": False,
            "continuum_regulator_removal": False,
            "physical_empty_space_reference": False,
            "prospective_Pre_A_validation": False,
            "C6_advanced": False,
            "CP1_complete": False,
            "Sector_A_complete": False,
            "Pre_A_complete": False,
        },
        "source_hashes": source_hashes,
        "formal_workflow": {
            key: value for key, value in formal.items() if key not in {"catalog_inventory", "changelog"}
        },
        "pdf_efficiency": pdf,
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
        help="report absent run/formal/PDF authorities as MISSING and exit zero",
    )
    parser.add_argument(
        "--no-store", action="store_true", help="run without writing result JSON"
    )
    arguments = parser.parse_args()
    payload = build_payload(arguments.staged)
    if not arguments.no_store:
        atomic_json(arguments.output, payload)
    summary = payload["summary"]
    print(
        f"{EXPLORATION_ID}/{RESULT_NUMBER}-{RESULT_VERSION} INTEGRATED "
        f"{payload['verdict']} {summary['passed']}/{summary['total']} "
        f"failed={summary['failed']} missing={summary['missing']}"
    )
    print("NO-STORE" if arguments.no_store else arguments.output)
    print("script_sha256: " + payload["source_hashes"][SCRIPT.relative_to(REPO).as_posix()])
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
