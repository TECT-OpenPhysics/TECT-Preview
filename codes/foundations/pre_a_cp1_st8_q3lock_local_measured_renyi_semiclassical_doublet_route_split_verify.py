#!/usr/bin/env python3
"""Integrated verifier for EXP-000806 / R-167 v1.9.

The primary and independent engines are each executed twice in fresh child
processes.  This file never imports either engine.  It normalizes only
invocation-specific metadata, requires deterministic component payloads, and
requires any later stored component result to equal the corresponding fresh
payload after the same narrow normalization.

The integrated checks bind the exact Renyi obstruction, pure-bond identities,
local measured-Renyi tail reduction, Q3 onsite semiclassics, exact low-band
compression, residual corridor, literature scope, no-overclaim boundary, and
formal repository authorities.  ``--staged`` reports authorities that have not
yet landed as ``MISSING``/``INCOMPLETE`` while treating every contradiction as
``FAIL``.  No proof-note source or PDF is created here.  Once the combined
R-167/R-168 gate-level checkpoint is issued, this verifier requires its exact
manifest metadata, raw hashes, freshness, page count, two independent text
extractions, required scope/reproduction tokens, and shared-manifest identity.
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


__version__ = "1.1.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = (
    "pre-a-cp1-st8-q3lock-local-measured-renyi-semiclassical-"
    "doublet-route-split"
)

RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-"
    "COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
RESULT_NUMBER = "R-167"
RESULT_VERSION = "v1.9"
EXPLORATION_ID = "EXP-000806"
TASK_ID = "T-054"
CLAIM_ID = "C6-SPACETIME-SIGNATURE"
CANDIDATE_ID = (
    "PA-CP1-ST8-Q3LOCK-LOCAL-MEASURED-RENYI-SEMICLASSICAL-"
    "DOUBLET-ROUTE-SPLIT-v0"
)

CLOSED_SUBGATES = (
    "PA-CP1-ST8-Q3LOCK-PURE-BOND-COORDINATE-TAIL-INVARIANCE-AND-"
    "STATE-WEIGHTED-CUTOFF-IDENTITY",
    "PA-CP1-ST8-Q3LOCK-LOCAL-MEASURED-RENYI-TO-HISTORY-TAIL-REDUCTION",
    "PA-CP1-ST8-Q3LOCK-SEMICLASSICAL-ONSITE-DOUBLET-AND-EXACT-"
    "LOW-BAND-TFIM-COMPRESSION",
)
OPEN_GATES = (
    "PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-"
    "HISTORY-COMMON-ALPHA",
    "PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY",
    "PA-CP1-ST8-Q3LOCK-INFINITE-DIMENSIONAL-RANK-TWO-BAND-"
    "BLOCK-DIAGONALIZATION-AND-TWO-PHASE-QPS",
    "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
)
NEGATIVE_IDS = (
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-GLOBAL-ALL-BOND-RENYI-"
    "VOLUME-UNIFORMITY",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-RANK-ONE-UNBOUNDED-"
    "BLOCK-DIAGONALIZATION-DIRECT-BROKEN-DOUBLET-IMPORT",
)
REUSED_NEGATIVE_IDS = (
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-ENERGY-FORM-ENTROPY-FINITE-"
    "MOMENT-AUTOMATIC-SANDWICHED-RENYI-UPGRADE",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-DIRECT-YAROTSKY-TWO-PHASE-GAP-IMPORT",
)
RETAINED_GATES = (
    "PA-CP1-ST8-Q3LOCK-FIXED-TROTTER-LOCAL-STRICT-INDUCTIVE-"
    "EXHAUSTION-COMPATIBILITY",
    "PA-CP1-ST8-Q3LOCK-PHASEWISE-GNS-GAP-OS-TEMPORAL-MASS-EQUIVALENCE",
    "PA-CP1-ST8-Q3LOCK-CONDITIONAL-DOUBLET-ISING-REFERENCE-GAP",
)
SUPERSEDED_GATES = (
    "PA-CP1-ST8-Q3LOCK-SANDWICHED-RENYI-TO-TWO-ORIENTATION-"
    "HISTORY-TAIL-CORRIDOR-REDUCTION",
)

SEMICLASSICAL_SOURCES = (
    "https://www.numdam.org/item/AIHPA_1983__38_3_295_0/",
    "https://www.numdam.org/item/AIHPA_1984__40_2_224_0/",
    "https://doi.org/10.1080/03605308408820335",
    "https://annals.math.princeton.edu/1984/120-1/p04",
    "https://www.numdam.org/item/AIHPA_1985__42_2_127_0/",
)
DFP_SOURCE = "https://arxiv.org/abs/2108.13907"

PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260811.md"
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
PROSPECTIVE_MANIFEST = (
    REPO / "strategy/pre-a-round1-prospective-holdout-freeze-protocol-manifest.json"
)
CHECKPOINT_SOURCE_REL = (
    "claims/C6-SPACETIME-SIGNATURE/notes/"
    "pre-a-q3lock-local-renyi-doublet-and-prospective-freeze-"
    "checkpoint-260811-v0.8.tex.txt"
)
CHECKPOINT_PDF_REL = (
    "claims/C6-SPACETIME-SIGNATURE/notes/"
    "pre-a-q3lock-local-renyi-doublet-and-prospective-freeze-"
    "checkpoint-260811-v0.8.pdf"
)
CHECKPOINT_SOURCE = REPO / CHECKPOINT_SOURCE_REL
CHECKPOINT_PDF = REPO / CHECKPOINT_PDF_REL
CHECKPOINT_SOURCE_SHA256 = (
    "89dae8bbf53f299676aa98a56db35fe8b00d1b672f7fb068f6c17810b985412e"
)
CHECKPOINT_PDF_SHA256 = (
    "a83084c2ad66210dddeac71f7ec8efb0705554a68362cec1c7055e20e0185e4a"
)
CHECKPOINT_PAGES = 15
CHECKPOINT_REQUIRED_TOKENS = (
    "R-167 v1.9",
    "R-168 v1.0",
    "EXP-000808",
    "PASS 181/181",
    "PASS 218/218",
    "physical Sector A",
    "Pre-A closure",
    "Reproduction command",
)
EXPECTED_CHECKPOINT = {
    "status": "ISSUED AS ONE COMBINED GATE-LEVEL CHECKPOINT AFTER PROOF VALIDATION",
    "source": CHECKPOINT_SOURCE_REL,
    "pdf": CHECKPOINT_PDF_REL,
    "source_sha256": CHECKPOINT_SOURCE_SHA256,
    "pdf_sha256": CHECKPOINT_PDF_SHA256,
    "pages": CHECKPOINT_PAGES,
    "workflow": (
        "No per-lemma or intermediate PDF was issued. One combined R-167 v1.9 / "
        "R-168 v1.0 gate-level synthesis source/PDF pair was issued only after "
        "the manifest, certificate, primary, non-importing independent, "
        "integrated, formal-authority, generated-surface, and source-form checks "
        "passed."
    ),
    "visual_qa": (
        "All 15 rendered pages were reviewed at readable resolution with zero "
        "clipping, overlap, broken equations, unreadable identifiers, black "
        "glyphs, or malformed page transitions; pypdf and pdfplumber each "
        "extracted 15 nonempty pages."
    ),
}

PRIMARY_SCHEMA = f"tect/{SLUG}-primary-result/1.0"
INDEPENDENT_SCHEMA = f"tect/{SLUG}-independent-result/1.0"
INTEGRATED_SCHEMA = f"tect/{SLUG}-integrated-result/1.0"
MINIMUM_PRIMARY_ASSERTIONS = 90
MINIMUM_INDEPENDENT_ASSERTIONS = 80


def json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, Fraction):
        return str(value)
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


def portable_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    """Separate contradictions from authorities that have not landed yet."""

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
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        audit.check(f"{label} parses", False, str(error), "valid JSON", "files")
        return None
    if not isinstance(payload, dict):
        audit.check(f"{label} object", False, type(payload).__name__, "dict", "files")
        return None
    audit.check(f"{label} parses", True, path.relative_to(REPO), "dict", "files")
    return payload


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
    reporter(label, not missing, missing, "all required tokens present", group)


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


VOLATILE_METADATA_KEYS = {
    "argv",
    "command",
    "command_line",
    "cwd",
    "elapsed_seconds",
    "generated_at",
    "invocation_output",
    "invocation_output_path",
    "output",
    "output_path",
    "pid",
    "result_path",
    "temporary_directory",
    "timestamp",
    "wall_time_seconds",
}


def normalize_invocation_metadata(value: Any, parent: str = "") -> Any:
    """Normalize only child-process invocation metadata, never proof data."""

    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            lowered = key.lower()
            if lowered in VOLATILE_METADATA_KEYS and parent.lower() in {
                "execution",
                "invocation",
                "metadata",
                "runtime",
            }:
                normalized[key] = "<NORMALIZED-INVOCATION-METADATA>"
            else:
                normalized[key] = normalize_invocation_metadata(item, key)
        return normalized
    if isinstance(value, list):
        return [normalize_invocation_metadata(item, parent) for item in value]
    return json_safe(value)


def canonical_component(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        normalize_invocation_metadata(dict(payload)),
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")


def run_once(
    component: Path, output_dir: Path, audit: Audit, label: str
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
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "result.json"
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
            "child exits zero and writes JSON",
            "freshness",
        )
        return None
    try:
        payload = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        audit.check(f"{label} JSON", False, str(error), "valid JSON", "freshness")
        return None
    if not isinstance(payload, dict):
        audit.check(f"{label} object", False, type(payload).__name__, "dict", "freshness")
        return None
    sentinel = next(
        (
            line.strip()
            for line in completed.stdout.splitlines()
            if re.match(r"^(PASS|INCOMPLETE|STAGED)\b", line.strip())
        ),
        "",
    )
    audit.check(f"{label} execution", True, completed.returncode, 0, "freshness")
    audit.check(
        f"{label} sentinel",
        bool(sentinel),
        sentinel,
        "PASS, INCOMPLETE, or STAGED sentinel",
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
    first_bytes = canonical_component(first[0])
    second_bytes = canonical_component(second[0])
    audit.check(
        f"{label} normalized deterministic payload",
        first_bytes == second_bytes,
        {
            "a": hashlib.sha256(first_bytes).hexdigest(),
            "b": hashlib.sha256(second_bytes).hexdigest(),
        },
        "equal normalized canonical hashes",
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
            "normalized fresh-equal JSON",
            "freshness",
        )
        return None
    try:
        stored = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        audit.check(f"{label} stored parses", False, str(error), "valid JSON", "freshness")
        return None
    if not isinstance(stored, dict):
        audit.check(
            f"{label} stored object", False, type(stored).__name__, "dict", "freshness"
        )
        return None
    stored_bytes = canonical_component(stored)
    fresh_bytes = canonical_component(fresh) if fresh is not None else b""
    audit.check(
        f"{label} stored equals fresh after invocation normalization",
        fresh is not None and stored_bytes == fresh_bytes,
        {
            "stored": hashlib.sha256(stored_bytes).hexdigest(),
            "fresh": hashlib.sha256(fresh_bytes).hexdigest() if fresh else None,
        },
        "equal normalized canonical hashes",
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
    audit.check("independent import firewall", not forbidden_imports, forbidden_imports, [], "firewall")
    literals = [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    forbidden_fragments = (
        f"2026-08-11-primary-{SLUG}",
        PRIMARY_STORED.relative_to(REPO).as_posix(),
    )
    consumed = [
        literal
        for literal in literals
        if any(fragment in literal.replace("\\", "/") for fragment in forbidden_fragments)
    ]
    audit.check("independent primary-result firewall", not consumed, consumed, [], "firewall")

    integrated_source = SCRIPT.read_text(encoding="utf-8")
    integrated_tree = ast.parse(integrated_source)
    integrated_imports: list[str] = []
    for node in ast.walk(integrated_tree):
        if isinstance(node, ast.Import):
            integrated_imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            integrated_imports.append(node.module or "")
    audit.check(
        "integrated subprocesses components without import",
        "subprocess.run" in integrated_source
        and all(
            name not in {"importlib", "runpy", primary_module, INDEPENDENT.stem}
            for name in integrated_imports
        ),
        integrated_imports,
        "subprocess execution and no component/importlib/runpy import",
        "firewall",
    )


def validate_checkpoint_synthesis(
    manifest: dict[str, Any], audit: Audit
) -> dict[str, Any]:
    """Bind the issued checkpoint in three count-stable, substantive rows."""

    artifact_failures: list[str] = []
    parser_failures: list[str] = []
    text_failures: list[str] = []
    details: dict[str, Any] = {}
    checkpoint = as_mapping(manifest.get("checkpoint_synthesis"))
    details["r167_checkpoint"] = checkpoint
    if checkpoint != EXPECTED_CHECKPOINT:
        artifact_failures.append("R-167 metadata is not the exact final block")

    prospective_checkpoint: dict[str, Any] = {}
    try:
        prospective_payload = json.loads(
            PROSPECTIVE_MANIFEST.read_text(encoding="utf-8")
        )
        if not isinstance(prospective_payload, dict):
            raise TypeError("prospective manifest root is not an object")
        prospective_checkpoint = as_mapping(
            prospective_payload.get("checkpoint_synthesis")
        )
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError) as error:
        artifact_failures.append(
            "R-168 manifest unreadable: "
            f"{type(error).__name__}: {error}"
        )
    details["r168_checkpoint"] = prospective_checkpoint
    shared_checkpoint = checkpoint == prospective_checkpoint == EXPECTED_CHECKPOINT
    details["shared_exact_checkpoint"] = shared_checkpoint
    if not shared_checkpoint:
        artifact_failures.append("R-167/R-168 exact checkpoint blocks differ")

    source_exists = CHECKPOINT_SOURCE.is_file()
    pdf_exists = CHECKPOINT_PDF.is_file()
    details["source_exists"] = source_exists
    details["pdf_exists"] = pdf_exists
    if not source_exists:
        artifact_failures.append("combined checkpoint source is missing")
    if not pdf_exists:
        artifact_failures.append("combined checkpoint PDF is missing")

    source_hash = raw_sha256(CHECKPOINT_SOURCE) if source_exists else None
    pdf_hash = raw_sha256(CHECKPOINT_PDF) if pdf_exists else None
    details["source_sha256"] = source_hash
    details["pdf_sha256"] = pdf_hash
    if source_hash != CHECKPOINT_SOURCE_SHA256:
        artifact_failures.append("combined source raw SHA256 mismatch")
    if pdf_hash != CHECKPOINT_PDF_SHA256:
        artifact_failures.append("combined PDF raw SHA256 mismatch")

    source_mtime = CHECKPOINT_SOURCE.stat().st_mtime_ns if source_exists else None
    pdf_mtime = CHECKPOINT_PDF.stat().st_mtime_ns if pdf_exists else None
    fresh = (
        source_mtime is not None
        and pdf_mtime is not None
        and pdf_mtime >= source_mtime
    )
    details["source_mtime_ns"] = source_mtime
    details["pdf_mtime_ns"] = pdf_mtime
    details["pdf_fresh_relative_to_source"] = fresh
    if not fresh:
        artifact_failures.append("combined PDF predates its source")

    source_text = ""
    if source_exists:
        try:
            source_text = CHECKPOINT_SOURCE.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            text_failures.append(
                "source UTF-8 read failed: "
                f"{type(error).__name__}: {error}"
            )

    pypdf_pages: list[str] | None = None
    if pdf_exists:
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(CHECKPOINT_PDF))
            pypdf_pages = [page.extract_text() or "" for page in reader.pages]
        except Exception as error:  # fail closed on dependency/parser errors
            parser_failures.append(
                "pypdf extraction failed: "
                f"{type(error).__name__}: {error}"
            )
    pypdf_count = len(pypdf_pages) if pypdf_pages is not None else None
    pypdf_nonempty = (
        sum(bool(page.strip()) for page in pypdf_pages)
        if pypdf_pages is not None
        else None
    )
    details["pypdf_pages"] = pypdf_count
    details["pypdf_nonempty"] = pypdf_nonempty
    if pypdf_count != CHECKPOINT_PAGES:
        parser_failures.append("pypdf page count is not 15")
    if pypdf_nonempty != CHECKPOINT_PAGES:
        parser_failures.append("pypdf did not extract 15 nonempty pages")

    pdfplumber_pages: list[str] | None = None
    if pdf_exists:
        try:
            import pdfplumber

            with pdfplumber.open(CHECKPOINT_PDF) as document:
                pdfplumber_pages = [
                    page.extract_text() or "" for page in document.pages
                ]
        except Exception as error:  # fail closed on dependency/parser errors
            parser_failures.append(
                "pdfplumber extraction failed: "
                f"{type(error).__name__}: {error}"
            )
    pdfplumber_count = (
        len(pdfplumber_pages) if pdfplumber_pages is not None else None
    )
    pdfplumber_nonempty = (
        sum(bool(page.strip()) for page in pdfplumber_pages)
        if pdfplumber_pages is not None
        else None
    )
    details["pdfplumber_pages"] = pdfplumber_count
    details["pdfplumber_nonempty"] = pdfplumber_nonempty
    if pdfplumber_count != CHECKPOINT_PAGES:
        parser_failures.append("pdfplumber page count is not 15")
    if pdfplumber_nonempty != CHECKPOINT_PAGES:
        parser_failures.append("pdfplumber did not extract 15 nonempty pages")

    required_tokens = CHECKPOINT_REQUIRED_TOKENS + (
        "No-overclaim statement",
        "all-exhaustion common alpha",
        "rank-two block diagonalization",
        "actual temporal mass/GNS gap",
        "cryptographic or remote freeze verification",
        "only synthesis source drafted",
        "No per-lemma or intermediate PDF",
    )
    extracted = {
        "source": source_text,
        "pypdf": "\n".join(pypdf_pages or []),
        "pdfplumber": "\n".join(pdfplumber_pages or []),
    }
    missing_by_reader = {
        label: [token for token in required_tokens if not text_has(body, token)]
        for label, body in extracted.items()
    }
    details["missing_tokens"] = missing_by_reader
    for label, missing in missing_by_reader.items():
        if missing:
            text_failures.append(f"{label} misses required scope tokens")

    details["artifact_failures"] = artifact_failures
    details["parser_failures"] = parser_failures
    details["text_failures"] = text_failures
    audit.check(
        "combined checkpoint exact shared artifact pins and freshness",
        not artifact_failures,
        {
            key: details[key]
            for key in (
                "shared_exact_checkpoint",
                "source_exists",
                "pdf_exists",
                "source_sha256",
                "pdf_sha256",
                "source_mtime_ns",
                "pdf_mtime_ns",
                "pdf_fresh_relative_to_source",
                "artifact_failures",
            )
        },
        "exact shared metadata, raw hashes, and fresh PDF",
        "pdf_efficiency",
    )
    audit.check(
        "combined checkpoint dual-parser 15/15 nonempty",
        not parser_failures,
        {
            "pypdf_pages": pypdf_count,
            "pypdf_nonempty": pypdf_nonempty,
            "pdfplumber_pages": pdfplumber_count,
            "pdfplumber_nonempty": pdfplumber_nonempty,
            "parser_failures": parser_failures,
        },
        {
            "pypdf_pages": CHECKPOINT_PAGES,
            "pypdf_nonempty": CHECKPOINT_PAGES,
            "pdfplumber_pages": CHECKPOINT_PAGES,
            "pdfplumber_nonempty": CHECKPOINT_PAGES,
        },
        "pdf_efficiency",
    )
    audit.check(
        "combined checkpoint scope, reproduction, no-overclaim, and exclusivity text",
        not text_failures,
        {
            "missing_tokens": missing_by_reader,
            "text_failures": text_failures,
        },
        "all required tokens in source and both PDF extractors",
        "pdf_efficiency",
    )
    return details


def validate_manifest(manifest: dict[str, Any], audit: Audit) -> None:
    expected = {
        "schema": "tect/pre-a-route-split/1.0",
        "candidate_id": CANDIDATE_ID,
        "task_id": TASK_ID,
        "claim_ids": [CLAIM_ID],
        "exploration_id": EXPLORATION_ID,
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "claim_bearing": False,
        "negative_ids": list(NEGATIVE_IDS),
        "reused_negative_ids": list(REUSED_NEGATIVE_IDS),
        "closed_subgates": list(CLOSED_SUBGATES),
        "retained_gate_ids": list(RETAINED_GATES),
        "superseded_gate_ids": list(SUPERSEDED_GATES),
        "open_gates": list(OPEN_GATES),
    }
    for field, value in expected.items():
        audit.check(f"manifest {field}", manifest.get(field) == value, manifest.get(field), value, "manifest")
    for section in (
        "pure_bond_tail_theorem",
        "local_measured_renyi_reduction",
        "global_renyi_product_no_go",
        "q3_semiclassical_onsite",
        "exact_low_band_compression",
        "unbounded_block_qps_boundary",
        "route_status",
        "checkpoint_synthesis",
        "verification",
        "no_overclaim",
    ):
        audit.check(f"manifest section {section}", section in manifest, section in manifest, True, "manifest")
    verification = as_mapping(manifest.get("verification"))
    expected_paths = {
        "primary_script": PRIMARY.relative_to(REPO).as_posix(),
        "independent_script": INDEPENDENT.relative_to(REPO).as_posix(),
        "integrated_script": SCRIPT.relative_to(REPO).as_posix(),
        "certificate": CERTIFICATE.relative_to(REPO).as_posix(),
    }
    for field, value in expected_paths.items():
        audit.check(
            f"manifest verification {field}",
            verification.get(field) == value,
            verification.get(field),
            value,
            "manifest",
        )
    require_tokens(
        manifest.get("no_overclaim", ""),
        "manifest no-overclaim boundary",
        (
            "onsite-interspersed local measured-Renyi",
            "n-to-infinity Trotter convergence",
            "all-exhaustion common alpha",
            "rank-two unbounded block diagonalization",
            "broken-sector temporal mass or GNS gap",
            "prospective blind validation",
            "physical Sector A",
            "Pre-A closure",
        ),
        audit,
        core=True,
        group="manifest",
    )
    validate_checkpoint_synthesis(manifest, audit)


def validate_certificate(audit: Audit) -> str | None:
    text = read_text(CERTIFICATE, audit, "certificate", core=True)
    if text is None:
        return None
    require_tokens(
        text,
        "certificate theorem and boundary chain",
        (
            EXPLORATION_ID,
            RESULT_NUMBER,
            RESULT_VERSION,
            RESULT_ID,
            *CLOSED_SUBGATES,
            OPEN_GATES[0],
            OPEN_GATES[1],
            "289\\over64",
            "24137569",
            "16\\sqrt{2}",
            "a_1-a_0&=O(v^2h)",
            "J=8cm^2",
            "24c",
            "cm\\sqrt{A_Q}=O(N^{-1})",
            "A_0\\sim {2\\over9}N^4",
            "rank-two",
            "No statement here closes C6, CP1, physical Sector A, or Pre-A",
        ),
        audit,
        core=True,
        group="certificate",
    )
    require_tokens(
        text,
        "certificate semiclassical primary sources",
        SEMICLASSICAL_SOURCES,
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


def validate_component(
    payload: dict[str, Any], label: str, schema: str, minimum: int, audit: Audit
) -> None:
    expected = {
        "schema": schema,
        "task_id": TASK_ID,
        "claim_ids": [CLAIM_ID],
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "exploration_id": EXPLORATION_ID,
        "claim_bearing": False,
        "negative_ids": list(NEGATIVE_IDS),
        "closed_subgates": list(CLOSED_SUBGATES),
        "open_gates": list(OPEN_GATES),
    }
    for field, value in expected.items():
        audit.check(f"{label} {field}", payload.get(field) == value, payload.get(field), value, "component")
    verdict_allowed = {"PASS", "INCOMPLETE"} if audit.staged else {"PASS"}
    audit.check(
        f"{label} verdict",
        payload.get("verdict") in verdict_allowed,
        payload.get("verdict"),
        sorted(verdict_allowed),
        "component",
    )
    summary = as_mapping(payload.get("summary"))
    rows_value = payload.get("assertions")
    rows = as_list(as_mapping(rows_value).get("rows")) if isinstance(rows_value, dict) else as_list(rows_value)
    passed = summary.get("passed")
    audit.check(
        f"{label} assertion floor",
        isinstance(passed, int) and passed >= minimum and len(rows) == passed,
        {"passed": passed, "rows": len(rows)},
        f">={minimum} all represented",
        "component",
    )
    audit.check(
        f"{label} assertions all pass",
        bool(rows) and all(as_mapping(row).get("status") == "PASS" for row in rows),
        sorted({as_mapping(row).get("status") for row in rows}),
        ["PASS"],
        "component",
    )


def validate_hash_map(payload: dict[str, Any], owner: Path, label: str, audit: Audit) -> None:
    expected = {
        path.relative_to(REPO).as_posix(): portable_sha256(path)
        for path in (owner, MANIFEST, CERTIFICATE)
        if path.is_file()
    }
    actual = as_mapping(payload.get("source_hashes"))
    audit.check(f"{label} exact source hashes", actual == expected, actual, expected, "freshness")


def compare_exact_core(
    primary: dict[str, Any], independent: dict[str, Any], manifest: dict[str, Any], audit: Audit
) -> dict[str, Any]:
    pd = as_mapping(primary.get("derived"))
    ider = as_mapping(independent.get("derived"))

    pa = as_mapping(pd.get("fixture_A_pure_bond_tail"))
    ipure = as_mapping(ider.get("pure_bond_diagonal"))
    audit.check(
        "cross pure-bond two-orientation identities",
        as_fraction(pa.get("left_orientation_hs_squared")) == Fraction(4, 3)
        and as_fraction(pa.get("right_orientation_hs_squared")) == Fraction(4, 3)
        and as_fraction(pa.get("spectral_sine_identity")) == Fraction(4, 3)
        and as_fraction(ipure.get("left_HS_square")) == Fraction(12, 5)
        and as_fraction(ipure.get("right_HS_square")) == Fraction(12, 5)
        and as_fraction(ipure.get("sine_functional")) == Fraction(12, 5),
        {
            "primary": [pa.get("left_orientation_hs_squared"), pa.get("right_orientation_hs_squared"), pa.get("spectral_sine_identity")],
            "independent": [ipure.get("left_HS_square"), ipure.get("right_HS_square"), ipure.get("sine_functional")],
        },
        {"primary": "4/3", "independent": "12/5"},
        "cross_math",
    )
    audit.check(
        "cross pure-bond commutation and honest scope",
        pa.get("commutator_zero") is True
        and pa.get("pure_layer_only") is True
        and pa.get("onsite_interspersed_history_tail_proved") is False
        and ipure.get("multiplier_commutator") == ["0", "0", "0", "0"]
        and ipure.get("operator_norm_exponential_paid") is False
        and ipure.get("onsite_interspersed_history_tail_proved") is False,
        {"primary": pa, "independent": ipure},
        "commuting pure layer, no onsite-history theorem",
        "cross_math",
    )

    pb = as_mapping(pd.get("fixture_B_local_and_global_renyi"))
    pglobal = as_mapping(pb.get("global_product_no_go"))
    iglobal = as_mapping(ider.get("global_Qtilde2_product_no_go"))
    expected_polynomial = [Fraction(1), Fraction(9, 2), Fraction(81, 16)]
    independent_polynomial = [as_fraction(item) for item in as_list(iglobal.get("Qtilde2_polynomial"))]
    three_bonds = Fraction(289, 64) ** 3
    audit.check(
        "cross exact global Renyi formula and fractions",
        text_has(pglobal.get("formula"), "(9*sin(angle)**2 + 4)**2/16")
        and independent_polynomial == expected_polynomial
        and as_fraction(pglobal.get("theta_pi_over_four")) == Fraction(289, 64)
        and as_fraction(iglobal.get("theta_pi_over_four_value")) == Fraction(289, 64)
        and as_fraction(pglobal.get("three_disjoint_bonds")) == three_bonds
        and as_fraction(iglobal.get("disjoint_product_value")) == three_bonds,
        {
            "primary_formula": pglobal.get("formula"),
            "independent_polynomial": independent_polynomial,
            "three_bonds": [pglobal.get("three_disjoint_bonds"), iglobal.get("disjoint_product_value")],
        },
        {"polynomial": ["1", "9/2", "81/16"], "one": "289/64", "three": str(three_bonds)},
        "cross_math",
    )
    audit.check(
        "cross complete eight-component bond factor",
        text_has(pglobal.get("full_bond_angle"), "8*c_bond*delta*m_bond**2/hbar_bond")
        and text_has(pglobal.get("J"), "8*c_bond*m_bond**2")
        and iglobal.get("physical_theta_coefficient_of_delta_c_m_squared_over_hbar") == 8
        and text_has(iglobal.get("physical_theta_relation"), "theta=8 delta c m^2/hbar=delta J/hbar")
        and iglobal.get("q3_coordinate_count") == 8,
        {"primary": pglobal, "independent": iglobal},
        "full-bond factor 8, not one coordinate channel",
        "cross_math",
    )
    audit.check(
        "cross global no-go boundary",
        pglobal.get("counterexample_is_full_interacting_Q3_Gibbs") is False
        and pglobal.get("local_coordinate_probability_invariant") is True
        and iglobal.get("global_volume_uniform_bound_rejected_in_fixture") is True
        and iglobal.get("full_interacting_Q3_Gibbs_counterexample") is False
        and iglobal.get("local_measured_Renyi_rejected") is False
        and iglobal.get("projected_full_coordinate_tail_claimed") is False,
        {"primary": pglobal, "independent": iglobal},
        "conditional global fixture only",
        "cross_math",
    )

    plocal = as_mapping(pb.get("local_measured_renyi"))
    ilocal = as_mapping(ider.get("local_measured_Renyi_reduction"))
    primary_poly = Fraction(3, 2) ** 4 + 2 * Fraction(3, 2) ** 2 / Fraction(2, 3) + 2 / Fraction(2, 3) ** 2
    independent_poly = Fraction(2) ** 4 + 2 * Fraction(2) ** 2 / Fraction(7) + 2 / Fraction(7) ** 2
    audit.check(
        "cross local measured-Renyi fourth-tail polynomial",
        primary_poly == Fraction(261, 16)
        and as_fraction(plocal.get("fourth_tail_polynomial")) == primary_poly
        and independent_poly == Fraction(842, 49)
        and as_fraction(ilocal.get("layer_cake_polynomial")) == independent_poly
        and as_fraction(ilocal.get("two_orientation_layer_cake_coefficient")) == 4 * independent_poly,
        {"primary": plocal.get("fourth_tail_polynomial"), "independent": ilocal.get("layer_cake_polynomial"), "two_orientation": ilocal.get("two_orientation_layer_cake_coefficient")},
        {"primary": "261/16", "independent": "842/49", "two_orientation": "3368/49"},
        "cross_math",
    )
    audit.check(
        "cross local measured-Renyi scope",
        plocal.get("onsite_interspersed_likelihood_bound_proved") is False
        and ilocal.get("onsite_interspersed_likelihood_bound_proved") is False
        and as_fraction(plocal.get("theta")) == as_fraction(ilocal.get("theta")) == Fraction(1, 2),
        {"primary": plocal, "independent": ilocal},
        "theta=1/2 and onsite history still open",
        "cross_math",
    )

    pc = as_mapping(pd.get("fixture_C_semiclassical_and_low_band"))
    pq3 = as_mapping(pc.get("q3_graph"))
    iq3 = as_mapping(ider.get("Q3_semiclassical_cube"))
    audit.check(
        "cross Q3 Hessian spectrum",
        text_has(
            pq3.get("hessian_characteristic"),
            "(lambda - 2)*(lambda - 6*mu - 2)*(lambda - 4*mu - 2)**3*(lambda - 2*mu - 2)**3",
        )
        and iq3.get("laplacian_spectrum") == [0, 2, 2, 2, 4, 4, 4, 6]
        and iq3.get("hessian_spectrum") == ["2", "4", "4", "4", "6", "6", "6", "8"]
        and iq3.get("hessian_multiplicity") == {"2": 1, "4": 3, "6": 3, "8": 1}
        and iq3.get("zero_sign_assignment_count") == 2,
        {"primary_characteristic": pq3.get("hessian_characteristic"), "independent_spectrum": iq3.get("hessian_spectrum")},
        "2, 2+2mu x3, 2+4mu x3, 2+6mu; two minima",
        "cross_math",
    )
    audit.check(
        "cross exact Q3 action",
        text_has(pq3.get("S0"), "16*sqrt(2)/3")
        and text_has(pq3.get("locked_collective_integral_raw"), "16*sqrt(2)/3")
        and as_fraction(iq3.get("S0_sqrt_coefficient")) == Fraction(16, 3)
        and iq3.get("S0_sqrt_radicand") == 2
        and as_fraction(iq3.get("S0_square")) == Fraction(512, 9),
        {"primary": pq3.get("S0"), "independent": [iq3.get("S0_sqrt_coefficient"), iq3.get("S0_sqrt_radicand")]},
        "16 sqrt(2)/3",
        "cross_math",
    )

    semiclassical = as_mapping(pc.get("semiclassical_import_scope"))
    manifest_semiclassical = as_mapping(manifest.get("q3_semiclassical_onsite"))
    audit.check(
        "semiclassical Simon-I erratum Simon-II source set",
        tuple(manifest_semiclassical.get("sources", ())) == SEMICLASSICAL_SOURCES,
        manifest_semiclassical.get("sources"),
        list(SEMICLASSICAL_SOURCES),
        "literature",
    )
    audit.check(
        "semiclassical safe small-h and d2 scope",
        semiclassical.get("fixed_mu_positive") is True
        and semiclassical.get("semiclassical_h0_explicit") is False
        and semiclassical.get("repository_r_minus_9_certified") is False
        and semiclassical.get("safe_d2_bound") == "O(v^2 h_sc)"
        and semiclassical.get("exponential_d2_requires_extra_weighted_Agmon_lemma") is True
        and semiclassical.get("extra_weighted_Agmon_lemma_registered") is False
        and iq3.get("numerical_h0_certified") is False
        and iq3.get("many_body_phase_proved") is False
        and text_has(manifest_semiclassical.get("imported_theorem"), "a_1-a_0=O(v^2 h_sc)"),
        {"primary": semiclassical, "independent": iq3.get("numerical_h0_certified"), "manifest": manifest_semiclassical.get("imported_theorem")},
        "existential fixed-mu small-h theorem and safe d2=O(v^2 h)",
        "literature",
    )

    plow = as_mapping(pc.get("low_band"))
    ilow = as_mapping(ider.get("exact_low_band_TFIM"))
    d2 = as_fraction(ilow.get("d_2"))
    c = as_fraction(ilow.get("c"))
    m = as_fraction(ilow.get("m"))
    delta1 = as_fraction(ilow.get("delta_1"))
    expected_j = None if c is None or m is None else 8 * c * m * m
    expected_shift = None if c is None or d2 is None else 24 * c * d2
    expected_delta = None if expected_shift is None or delta1 is None else delta1 + expected_shift
    audit.check(
        "cross exact low-band J and periodic z=6 field",
        text_has(plow.get("J"), "8*c*m**2")
        and text_has(plow.get("delta_eff"), "-24*a_0*c + 24*a_1*c + delta_1")
        and text_has(plow.get("delta_site"), "-4*a_0*c*deg_x + 4*a_1*c*deg_x + delta_1")
        and as_fraction(ilow.get("z")) == 6
        and expected_j == as_fraction(ilow.get("J")) == Fraction(4)
        and expected_shift == as_fraction(ilow.get("accumulated_site_field")) == Fraction(4, 75)
        and expected_delta == as_fraction(ilow.get("delta_eff")) == Fraction(23, 150),
        {"primary": plow, "independent": ilow},
        {"J": "8cm^2=4", "periodic_field": "24cd2=4/75", "delta_eff": "23/150", "boundary": "4c deg(x)d2"},
        "cross_math",
    )

    pmoment = as_mapping(plow.get("moment_fixture"))
    pres = as_mapping(plow.get("centered_form_fixture"))
    ires = as_mapping(ider.get("residual_bound"))
    audit.check(
        "cross residual fixtures and open theorem boundary",
        as_fraction(pmoment.get("a_squared")) == Fraction(4, 9)
        and as_fraction(pmoment.get("b_squared")) == Fraction(1, 9)
        and as_fraction(pmoment.get("one_bond_bound")) == Fraction(104, 15)
        and text_has(pres.get("A_Q"), "9/20 + sqrt(21)/5")
        and as_fraction(ires.get("a_squared")) == Fraction(13, 50)
        and as_fraction(ires.get("b_squared")) == Fraction(9, 25)
        and ires.get("sqrt_upper_certified_by_squaring") is True
        and ires.get("residual_inequality_proves_block_diagonalization") is False,
        {"primary_moment": pmoment, "primary_form": pres, "independent": ires},
        "two distinct exact residual fixtures; no block theorem",
        "cross_math",
    )

    pexponents = as_mapping(pc.get("corridor_exponents_in_N"))
    icorridor = as_mapping(ider.get("N_corridor"))
    iexponents = as_mapping(icorridor.get("derived_exponents"))
    iinputs = as_mapping(icorridor.get("input_exponents"))
    independent_A_Q_exponent = icorridor.get("A_Q_dominant_exponent")
    independent_mixed = (
        as_fraction(iinputs.get("c"))
        + as_fraction(iexponents.get("v"))
        + as_fraction(independent_A_Q_exponent) / 2
        if all(
            as_fraction(value) is not None
            for value in (iinputs.get("c"), iexponents.get("v"), independent_A_Q_exponent)
        )
        else None
    )
    audit.check(
        "cross semiclassical residual corridor",
        pexponents.get("J") == 0
        and pexponents.get("one_bond_low_high") == -3
        and pexponents.get("c_A_Q") == -2
        and pexponents.get("c_m_sqrt_A_Q") == -1
        and iexponents.get("J") == "0"
        and iexponents.get("one_bond_low_high") == "-3"
        and iexponents.get("cA_Q") == "-2"
        and independent_mixed == Fraction(-1)
        and icorridor.get("finite_N_enclosure") is False
        and icorridor.get("two_phase_QPS_proved") is False,
        {"primary": pexponents, "independent": iexponents, "independent_mixed": independent_mixed},
        {"J": 0, "one_bond": -3, "cA_Q": -2, "c*m*sqrt(A_Q)": -1},
        "cross_math",
    )
    audit.check(
        "cross registered infrared A0 asymptotic",
        text_has(pc.get("A0_corridor"), "2*N**4/9")
        and text_has(as_mapping(manifest.get("exact_low_band_compression")).get("corridor"), "A_0 asymptotic to (2/9)N^4"),
        {"primary": pc.get("A0_corridor"), "manifest": as_mapping(manifest.get("exact_low_band_compression")).get("corridor")},
        "A0~(2/9)N^4",
        "cross_math",
    )

    pdfp = as_mapping(pc.get("dfp_rank_one_boundary"))
    audit.check(
        "cross DFP rank-one boundary",
        pdfp.get("source") == DFP_SOURCE
        and pdfp.get("Q3_local_kernel_rank") == 2
        and pdfp.get("Q3_global_low_dimension") == "2^|Lambda|"
        and pdfp.get("published_main_theorem_rank_one_vacuum") is True
        and pdfp.get("published_main_theorem_unique_ground_state") is True
        and pdfp.get("introductory_degenerate_extension_is_rank2_band_theorem") is False
        and pdfp.get("direct_import_closes_broken_sector_gap") is False,
        pdfp,
        "published rank-one unique-vacuum theorem is not the rank-two Q3 band theorem",
        "literature",
    )

    primary_scope = as_mapping(primary.get("scope"))
    primary_false = (
        "finite_r_minus_9_onsite_doublet_certified",
        "rank_two_unbounded_block_elimination",
        "two_phase_QPS_for_exact_Q3LOCK",
        "broken_sector_GNS_gap",
        "Sector_A_complete",
        "Pre_A_complete",
    )
    independent_false = (
        "onsite_interspersed_history_bound_closed",
        "all_exhaustion_common_alpha_closed",
        "rank_two_block_diagonalization_closed",
        "two_phase_QPS_closed",
        "broken_sector_GNS_gap_closed",
        "physical_mass_gap_closed",
        "regulator_removal_closed",
        "continuum_closed",
        "physical_empty_comparison_closed",
        "C6_closed",
        "CP1_closed",
        "Sector_A_closed",
        "Pre_A_closed",
    )
    audit.check(
        "all component no-overclaim booleans",
        all(primary_scope.get(key) is False for key in primary_false)
        and all(ider.get(key) is False for key in independent_false),
        {
            "primary": {key: primary_scope.get(key) for key in primary_false},
            "independent": {key: ider.get(key) for key in independent_false},
        },
        "all false",
        "no_overclaim",
    )
    return {
        "global_Qtilde2_formula": "(4+9 sin^2 theta)^2/16",
        "theta_pi_over_four": "289/64",
        "three_disjoint_bonds": str(three_bonds),
        "full_bond_factor": 8,
        "pure_bond_primary_HS_squared": "4/3",
        "pure_bond_independent_HS_squared": "12/5",
        "primary_tail_polynomial": str(primary_poly),
        "independent_tail_polynomial": str(independent_poly),
        "Q3_hessian": ["2", "2+2mu x3", "2+4mu x3", "2+6mu"],
        "S0": "16 sqrt(2)/3",
        "safe_d2": "O(v^2 h_sc)",
        "J": "8 c m^2",
        "periodic_z": 6,
        "periodic_field": "24 c d2",
        "boundary_field": "4 c deg(x) d2",
        "mixed_form_exponent": -1,
        "A0": "(2/9) N^4",
        "actual_history_common_alpha_or_gap_closed": False,
    }


def validate_formal(audit: Audit) -> dict[str, Any]:
    explorations = jsonl_records(REPO / "explorations/log.jsonl", audit, "exploration ledger")
    matches = [] if explorations is None else [row for row in explorations if row.get("id") == EXPLORATION_ID]
    audit.pending(f"{EXPLORATION_ID} unique record", len(matches) == 1, len(matches), 1, "formal")
    if len(matches) == 1:
        record = matches[0]
        serialized = json.dumps(record, sort_keys=True)
        refs = as_mapping(record.get("formal_refs"))
        audit.pending(
            f"{EXPLORATION_ID} exact provenance",
            record.get("schema") == "tect/proof-exploration/1.0"
            and record.get("task_id") == TASK_ID
            and record.get("claim_ids") == [CLAIM_ID]
            and record.get("verdict") == "advanced"
            and RESULT_NUMBER in as_list(refs.get("results"))
            and set(NEGATIVE_IDS).issubset(set(as_list(refs.get("negatives"))))
            and all(text_has(serialized, token) for token in (*CLOSED_SUBGATES, *OPEN_GATES)),
            record,
            "exact task/claim/result/negative/gate provenance",
            "formal",
        )

    result_ledger = read_text(REPO / "RESULTS-LEDGER.md", audit, "result ledger")
    if result_ledger is not None:
        section = heading_section(result_ledger, RESULT_NUMBER)
        audit.pending(f"{RESULT_NUMBER} section exists", section is not None, section, "section", "formal")
        if section is not None:
            require_tokens(
                section,
                f"{RESULT_NUMBER} {RESULT_VERSION} authority",
                (RESULT_VERSION, EXPLORATION_ID, "pure-bond", "measured-Renyi", "semiclassical", "rank-two", *CLOSED_SUBGATES, *OPEN_GATES[:3], *NEGATIVE_IDS, "T0"),
                audit,
            )

    negatives = read_text(REPO / "negative-results/registry.md", audit, "negative registry")
    if negatives is not None:
        require_tokens(negatives, "v1.9 negative authorities", NEGATIVE_IDS, audit)

    gates = read_text(REPO / "claims/GATES.md", audit, "gate registry")
    if gates is not None:
        for gate in CLOSED_SUBGATES:
            section = heading_section(gates, gate)
            audit.pending(f"closed gate section {gate}", section is not None, section, "section", "formal")
            if section is not None:
                audit.pending(
                    f"closed gate scoped status {gate}",
                    re.search(r"\*\*Status:\*\*\s*CLOSED", section, re.I) is not None
                    and text_has(section, EXPLORATION_ID)
                    and text_has(section, RESULT_VERSION),
                    section,
                    "scoped CLOSED under EXP-000806/R-167 v1.9",
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

    strategy_index = read_text(REPO / "strategy/INDEX.md", audit, "strategy index")
    if strategy_index is not None:
        require_tokens(strategy_index, "strategy v1.9 links", (MANIFEST.name, CERTIFICATE.name), audit)

    todo = load_json(REPO / "todo/todo.json", audit, "TODO authority")
    if todo is not None:
        tasks = [row for row in as_list(todo.get("tasks")) if isinstance(row, dict) and row.get("id") == TASK_ID]
        audit.pending(f"{TASK_ID} unique", len(tasks) == 1, len(tasks), 1, "formal")
        if len(tasks) == 1:
            serialized = json.dumps(tasks[0], sort_keys=True)
            audit.pending(
                f"{TASK_ID} in-progress v1.9 linkage",
                tasks[0].get("status") == "in_progress"
                and all(text_has(serialized, token) for token in (EXPLORATION_ID, RESULT_VERSION, *OPEN_GATES)),
                tasks[0],
                "in_progress and linked to v1.9 open gates",
                "formal",
            )

    theorem_map = load_json(REPO / "governance/sector-a-theorem-map.json", audit, "Sector-A theorem map")
    if theorem_map is not None:
        require_tokens(
            json.dumps(theorem_map, sort_keys=True),
            "Sector-A theorem map v1.9 scope",
            (RESULT_NUMBER, RESULT_VERSION, EXPLORATION_ID, *CLOSED_SUBGATES, *OPEN_GATES, "Pre-A"),
            audit,
        )

    changelog = jsonl_records(REPO / "changelog/log.jsonl", audit, "changelog")
    events = (
        []
        if changelog is None
        else [
            event
            for event in changelog
            if text_has(json.dumps(event, sort_keys=True), EXPLORATION_ID)
        ]
    )
    event_by_id = {
        event.get("id"): event
        for event in events
        if isinstance(event.get("id"), str)
    }
    theorem_id = "20260811-r-167-v1-9-replaces-global-renyi-by-local-measu"
    correction_id = "20260811-r-167-v1-9-integrated-verifier-linkage-correcti"
    checkpoint_id = "20260811-r-167-v1-9-and-r-168-v1-0-combined-gate-level-s"
    theorem_event = as_mapping(event_by_id.get(theorem_id))
    correction_event = as_mapping(event_by_id.get(correction_id))
    checkpoint_event = as_mapping(event_by_id.get(checkpoint_id))
    primary_path = PRIMARY.relative_to(REPO).as_posix()
    independent_path = INDEPENDENT.relative_to(REPO).as_posix()
    integrated_path = SCRIPT.relative_to(REPO).as_posix()
    r168_slug = "pre_a_round1_prospective_holdout_freeze_protocol"
    r168_scripts = [
        f"codes/foundations/{r168_slug}.py",
        f"codes/foundations/{r168_slug}_independent.py",
        f"codes/foundations/{r168_slug}_verify.py",
    ]
    role_failures: list[str] = []
    exact_ids = {theorem_id, correction_id, checkpoint_id}
    if len(events) != 3 or set(event_by_id) != exact_ids:
        role_failures.append("EXP-000806 changelog roles are not exactly three")
    if (
        theorem_event.get("claim_ids") != [CLAIM_ID, EXPLORATION_ID, RESULT_NUMBER]
        or theorem_event.get("notes") != []
        or theorem_event.get("scripts") != [primary_path, independent_path]
        or theorem_event.get("neg_results") != list(NEGATIVE_IDS)
        or not all(
            text_has(theorem_event.get("raw", ""), token)
            for token in (
                RESULT_VERSION,
                "pure-bond",
                "measured-Renyi",
                "rank-two",
                "physical Sector A and Pre-A remain open",
                "No PDF event is issued",
            )
        )
    ):
        role_failures.append("theorem event exact role mismatch")
    if (
        correction_event.get("claim_ids")
        != [CLAIM_ID, EXPLORATION_ID, RESULT_NUMBER]
        or correction_event.get("notes") != []
        or correction_event.get("scripts")
        != [primary_path, independent_path, integrated_path]
        or correction_event.get("neg_results") != list(NEGATIVE_IDS)
        or not all(
            text_has(correction_event.get("raw", ""), token)
            for token in (
                "integrated-verifier linkage correction",
                "changes no mathematics",
                "remain open",
                "No note or PDF is issued",
            )
        )
    ):
        role_failures.append("correction event exact role mismatch")
    expected_notes = [
        CHECKPOINT_SOURCE_REL,
        CHECKPOINT_PDF_REL,
        CERTIFICATE.relative_to(REPO).as_posix(),
        "strategy/pre-a-round1-prospective-holdout-freeze-protocol-"
        "certificate-260811.md",
    ]
    expected_checkpoint_claims = [
        CLAIM_ID,
        EXPLORATION_ID,
        "EXP-000807",
        "EXP-000808",
        RESULT_NUMBER,
        "R-168",
    ]
    expected_checkpoint_negatives = [
        "NG-2026-08-11-PRE-A-ROUND1-CURRENT-TREE-PROSPECTIVE-"
        "HOLDOUT-NONEXISTENCE",
        *NEGATIVE_IDS,
    ]
    if (
        checkpoint_event.get("claim_ids") != expected_checkpoint_claims
        or checkpoint_event.get("notes") != expected_notes
        or checkpoint_event.get("scripts")
        != [primary_path, independent_path, integrated_path, *r168_scripts]
        or checkpoint_event.get("neg_results") != expected_checkpoint_negatives
        or not all(
            text_has(checkpoint_event.get("raw", ""), token)
            for token in (
                "combined gate-level synthesis PDF",
                "changes no mathematics",
                "15 rendered pages",
                "pypdf and pdfplumber each extracted 15 nonempty pages",
                "hashes and page count are pinned identically in both manifests",
                "physical Sector A and Pre-A remain open",
            )
        )
    ):
        role_failures.append("combined checkpoint event exact role mismatch")
    audit.pending(
        f"{EXPLORATION_ID} theorem/correction/checkpoint changelog roles exact",
        not role_failures,
        {
            "event_ids": sorted(event_by_id),
            "failures": role_failures,
            "checkpoint_notes": checkpoint_event.get("notes"),
            "checkpoint_scripts": checkpoint_event.get("scripts"),
            "checkpoint_negatives": checkpoint_event.get("neg_results"),
        },
        "exact theorem, append-only correction, and combined-PDF events",
        "formal",
    )

    proof_map = read_text(REPO / "theory/proof-evidence-map.md", audit, "proof-evidence map")
    if proof_map is not None:
        require_tokens(proof_map, "proof-evidence v1.9 linkage", (EXPLORATION_ID, RESULT_VERSION, *CLOSED_SUBGATES, *OPEN_GATES, *NEGATIVE_IDS), audit)
    proof_json = load_json(REPO / "verification/proof-evidence-map.json", audit, "proof-evidence JSON")
    if proof_json is not None:
        require_tokens(json.dumps(proof_json, sort_keys=True), "proof-evidence JSON v1.9 linkage", (EXPLORATION_ID, RESULT_VERSION, *CLOSED_SUBGATES, *OPEN_GATES, *NEGATIVE_IDS), audit)

    locator_specs = (
        (
            REPO / "results/index.json",
            "result locator",
            "tect/results-index/1.0",
            "RESULTS-LEDGER.md",
            (RESULT_NUMBER,),
        ),
        (
            REPO / "negative-results/index.json",
            "negative locator",
            "tect/negative-index/1.0",
            "negative-results/registry.md",
            (),
        ),
        (
            REPO / "claims/gates-index.json",
            "gate locator",
            "tect/gate-index/1.0",
            "claims/GATES.md + claims/*/status.json",
            (),
        ),
    )
    locator_counts: dict[str, int] = {}
    for path, label, schema, authority, required_ids in locator_specs:
        payload = load_json(path, audit, label)
        if payload is None:
            continue
        entries = [row for row in as_list(payload.get("entries")) if isinstance(row, dict)]
        identifiers = [row.get("id") for row in entries]
        audit.pending(
            f"{label} schema/count current",
            payload.get("schema") == schema
            and payload.get("authority") == authority
            and payload.get("count") == len(entries)
            and all(identifier in identifiers for identifier in required_ids),
            {
                "schema": payload.get("schema"),
                "authority": payload.get("authority"),
                "count": payload.get("count"),
                "entries": len(entries),
                "required_present": {
                    identifier: identifier in identifiers for identifier in required_ids
                },
            },
            {
                "schema": schema,
                "authority": authority,
                "count": "len(entries)",
                "required": list(required_ids),
            },
            "formal",
        )
        if isinstance(payload.get("count"), int):
            locator_counts[label] = payload["count"]

    generated_specs = (
        (REPO / "negative-results/INDEX.md", "negative index", NEGATIVE_IDS),
        (REPO / "changelog/INDEX.md", "changelog index", (EXPLORATION_ID, RESULT_VERSION)),
    )
    for path, label, tokens in generated_specs:
        text = read_text(path, audit, label)
        if text is not None:
            require_tokens(text, f"{label} current linkage", tokens, audit)

    result_count = locator_counts.get("result locator")
    negative_count = locator_counts.get("negative locator")
    gate_count = locator_counts.get("gate locator")
    result_index = read_text(REPO / "results/INDEX.md", audit, "result index")
    if result_index is not None and result_count is not None:
        require_tokens(
            result_index,
            "result index locator/count freshness",
            (RESULT_NUMBER, f"{result_count} registered results"),
            audit,
        )
    gate_index = read_text(REPO / "claims/GATES-INDEX.md", audit, "gate index")
    if gate_index is not None and gate_count is not None:
        require_tokens(
            gate_index,
            "gate index locator/count freshness",
            (f"{gate_count} registered definitions",),
            audit,
        )
    management_index = read_text(REPO / "management/INDEX.md", audit, "management index")
    if (
        management_index is not None
        and result_count is not None
        and negative_count is not None
        and gate_count is not None
    ):
        require_tokens(
            management_index,
            "management index authority/count freshness",
            (
                "AUTO-GENERATED by verification/scripts/build_management_indexes.py",
                "Authorities: claims/*/status.json, todo/todo.json, ROADMAP.md, RESULTS-LEDGER.md, negative-results/registry.md, claims/GATES.md",
                f"{result_count} reusable results",
                f"{negative_count} negative/audit records",
                f"{gate_count} registered gates/hypotheses",
            ),
            audit,
        )

    compact_proof = read_text(REPO / "theory/proof-evidence/INDEX.md", audit, "compact proof index")
    if compact_proof is not None:
        require_tokens(
            compact_proof,
            "compact proof index current counts",
            (f"{len(explorations or [])} proof explorations", f"{len(changelog or [])} accepted events"),
            audit,
        )

    catalog = load_json(REPO / "verification/catalog/index.json", audit, "catalog manifest")
    catalog_inventory = ""
    if catalog is not None:
        shards = as_list(catalog.get("shards"))
        valid: list[bool] = []
        payloads: list[dict[str, Any]] = []
        for shard in shards:
            if not isinstance(shard, dict) or not isinstance(shard.get("path"), str):
                valid.append(False)
                continue
            shard_path = REPO / shard["path"]
            payload = load_json(shard_path, audit, f"catalog shard {shard.get('kind', shard['path'])}")
            if payload is None:
                valid.append(False)
                continue
            payloads.append(payload)
            entries = as_list(payload.get("entries"))
            valid.append(
                hashlib.sha256(shard_path.read_bytes()).hexdigest() == shard.get("sha256")
                and payload.get("count") == shard.get("count") == len(entries)
            )
        audit.pending(
            "catalog manifest/shards current",
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
            "catalog v1.9 artifacts",
            (
                MANIFEST.relative_to(REPO).as_posix(),
                CERTIFICATE.relative_to(REPO).as_posix(),
                PRIMARY.relative_to(REPO).as_posix(),
                INDEPENDENT.relative_to(REPO).as_posix(),
                SCRIPT.relative_to(REPO).as_posix(),
            ),
            audit,
        )

    catalog_summary = load_json(REPO / "verification/catalog-summary.json", audit, "catalog summary")
    if catalog is not None and catalog_summary is not None:
        audit.pending(
            "catalog summary agrees with manifest",
            catalog_summary.get("schema") == "tect/catalog-summary/1.0"
            and catalog_summary.get("full_catalog") == "verification/catalog/index.json"
            and catalog_summary.get("total") == catalog.get("total"),
            catalog_summary,
            "matching v2 manifest total",
            "formal",
        )
    catalog_index = read_text(REPO / "catalog/INDEX.md", audit, "catalog reader index")
    if catalog_index is not None and catalog is not None:
        require_tokens(catalog_index, "catalog reader current total", (f"{catalog.get('total')} artefacts",), audit)

    status = load_json(REPO / f"claims/{CLAIM_ID}/status.json", audit, "C6 status", core=True)
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
        "changelog_matches": len(events),
        "catalog_inventory_bound": bool(catalog_inventory),
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
    with tempfile.TemporaryDirectory(prefix="tect-exp806-integrated-") as directory:
        temporary = Path(directory)
        for label, component in (("primary", PRIMARY), ("independent", INDEPENDENT)):
            result = run_fresh_pair(component, temporary, audit, label)
            if result is not None:
                components[label], sentinels[label] = result

    stored_against_fresh(PRIMARY_STORED, components.get("primary"), audit, "primary")
    stored_against_fresh(INDEPENDENT_STORED, components.get("independent"), audit, "independent")

    if "primary" in components:
        validate_component(components["primary"], "primary", PRIMARY_SCHEMA, MINIMUM_PRIMARY_ASSERTIONS, audit)
        validate_hash_map(components["primary"], PRIMARY, "primary", audit)
    if "independent" in components:
        validate_component(components["independent"], "independent", INDEPENDENT_SCHEMA, MINIMUM_INDEPENDENT_ASSERTIONS, audit)
        validate_hash_map(components["independent"], INDEPENDENT, "independent", audit)

    cross: dict[str, Any] = {}
    if "primary" in components and "independent" in components:
        cross = compare_exact_core(components["primary"], components["independent"], manifest, audit)
    else:
        audit.check("fresh exact cross-comparison", False, sorted(components), ["primary", "independent"], "cross_math")

    formal = validate_formal(audit)
    passed = sum(row["status"] == "PASS" for row in audit.rows)
    source_paths = (
        SCRIPT,
        PRIMARY,
        INDEPENDENT,
        MANIFEST,
        PROSPECTIVE_MANIFEST,
        CERTIFICATE,
        PRIMARY_STORED,
        INDEPENDENT_STORED,
    )
    source_hashes = {
        path.relative_to(REPO).as_posix(): portable_sha256(path)
        for path in source_paths
        if path.is_file()
    }
    for artifact in (CHECKPOINT_SOURCE, CHECKPOINT_PDF):
        if artifact.is_file():
            source_hashes[artifact.relative_to(REPO).as_posix()] = raw_sha256(artifact)
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
        "closed_subgates": list(CLOSED_SUBGATES),
        "retained_gates": list(RETAINED_GATES),
        "superseded_gate_ids": list(SUPERSEDED_GATES),
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
            "pure_bond_coordinate_tail_identity": True,
            "local_measured_renyi_sufficiency_reduction": True,
            "global_volume_uniform_renyi_target_rejected_in_conditional_product_fixture": True,
            "Q3_small_h_onsite_doublet_import": True,
            "exact_low_band_TFIM_compression": True,
            "onsite_interspersed_history_bound": False,
            "n_to_infinity_Trotter_convergence": False,
            "all_exhaustion_common_alpha": False,
            "finite_r_minus_9_doublet_certified": False,
            "rank_two_unbounded_block_diagonalization": False,
            "two_phase_QPS_for_exact_Q3LOCK": False,
            "beta_infinity_phase_selection": False,
            "actual_broken_sector_temporal_mass": False,
            "actual_broken_sector_GNS_gap": False,
            "regulator_removal": False,
            "continuum": False,
            "physical_empty_space_comparison": False,
            "prospective_blind_validation": False,
            "C6_advanced": False,
            "CP1_complete": False,
            "Sector_A_complete": False,
            "Pre_A_complete": False,
        },
        "source_hashes": source_hashes,
        "formal_workflow": formal,
        "pdf_efficiency": {
            "dedicated_R167_v1_9_PDF_required": False,
            "PDF_created_by_this_verifier": False,
            "PDF_read_by_this_verifier": True,
            "combined_gate_level_checkpoint_deferred": False,
            "combined_gate_level_checkpoint_issued": (
                as_mapping(manifest.get("checkpoint_synthesis"))
                == EXPECTED_CHECKPOINT
            ),
            "source": CHECKPOINT_SOURCE_REL,
            "pdf": CHECKPOINT_PDF_REL,
            "source_sha256": (
                raw_sha256(CHECKPOINT_SOURCE)
                if CHECKPOINT_SOURCE.is_file()
                else None
            ),
            "pdf_sha256": (
                raw_sha256(CHECKPOINT_PDF) if CHECKPOINT_PDF.is_file() else None
            ),
            "pages": CHECKPOINT_PAGES,
            "certificate_present": certificate is not None,
        },
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
        help="report absent run/formal/generated authorities as MISSING and exit zero",
    )
    parser.add_argument("--no-store", action="store_true", help="run without writing result JSON")
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
