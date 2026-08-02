#!/usr/bin/env python3
"""Integrated verifier for the scoped A13 R-147 evidence package."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-08-02"
__version_issued__ = "2026-08-02"

import argparse
import ast
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any

from pypdf import PdfReader
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
RESULT_ID = (
    "A13-CLASSII-CANONICAL-SIGNED-COMMON-TERMINAL-"
    "DOOB-BRACKET-DEFECT-BOUNDARY"
)
LEDGER_ID = "R-147"
SLUG = "canonical-signed-common-terminal-doob-bracket-defect-boundary"
SCHEMA = f"tect/a13-{SLUG}-integrated/1.0"
MANIFEST = CLAIM_DIR / (
    "classii_canonical_signed_common_terminal_doob_bracket_"
    "defect_boundary_manifest.json"
)
PRIMARY = REPO / (
    "codes/foundations/a13_classii_canonical_signed_common_terminal_"
    "doob_bracket_defect_boundary.py"
)
INDEPENDENT = REPO / (
    "codes/foundations/a13_classii_canonical_signed_common_terminal_"
    "doob_bracket_defect_boundary_independent.py"
)
NOTE = CLAIM_DIR / (
    "notes/classii-canonical-signed-common-terminal-doob-bracket-"
    "defect-boundary-260802-v1.0.tex.txt"
)
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-integrated-{SLUG}/result.json"
EXPLORATION_IDS = tuple(f"EXP-{number:06d}" for number in range(615, 623))
NEGATIVE_IDS = (
    "NG-2026-08-02-A13-COMMON-TERMINAL-AUTOMATIC-SCALAR-SIGN",
    "NG-2026-08-02-A13-ENDPOINT-LAW-OWNER-TRANSFER",
    "NG-2026-08-02-A13-PRODUCTION-PAIR-GLOBAL-CONVEXITY",
    "AUDIT-2026-08-02-A13-R147-R063-FOREST-BRACKET-CONFLATION",
)

# Calibrated only after every substantive integrator check is present.  The
# final check below makes accidental assertion-count drift a hard failure.
FROZEN_INTEGRATOR_ONLY = 218

EXPECTED_SCOPE = {
    "canonical_signed_terminal_doob_proved": True,
    "canonical_signed_conditional_recursion_proved": True,
    "continuous_signed_martingale_representation_proved": True,
    "three_feature_to_two_feature_compression_proved": True,
    "filtration_nest_transfer_criterion_proved": True,
    "polarized_trace_bracket_defect_identity_proved": True,
    "production_affine_collinear_coefficient_slice_proved": True,
    "endpoint_law_owner_transfer_proved": False,
    "old_owner_transfer_proved": False,
    "production_trace_bracket_matching_proved": False,
    "registered_r063_forest_identification_in_canonical_chart_proved": False,
    "production_pair_global_coefficient_convexity_proved": False,
    "production_pair_global_coefficient_convexity_refuted": True,
    "complete_noncollinear_scalar_owner_bound_proved": False,
    "physical_phase_or_bcc_selection_proved": False,
    "t050_closed": False,
    "a13_gate_closed": False,
    "nelson_proved": False,
    "sector_a_closed": False,
}

EXPECTED_CROSS_VALUES = {
    "production_affine_ray_curvature_lower": "2223/(25000*P)",
    "production_l_only_curvature_witness": "-56/2187",
    "production_noncollinear_threshold": "-1/12 + 5*sqrt(154)/132",
    "production_noncollinear_zero_floor_curvature": "-99/(250*P)",
}

EXPECTED_EXACT_VALUES = {
    "primary": {
        "centred_common_terminal_ratio_at_t2": "4/5",
        "linear_owner_energies_chart_a": ["1", "0"],
        "linear_owner_energies_chart_b": ["1/2", "1/2"],
        "matched_relative_negative_fixture": "-3/4",
        "matched_relative_positive_fixture": "3/4",
        "production_affine_ray_curvature_lower": "2223/(25000*P)",
        "production_l_only_curvature_witness": "-56/2187",
        "production_noncollinear_threshold": "-1/12 + 5*sqrt(154)/132",
        "production_noncollinear_zero_floor_curvature": "-99/(250*P)",
        "production_zero_ray_pair_defect_upper": "-18/(125*P)",
        "quadratic_owner_energies_chart_a": ["2", "0"],
        "quadratic_owner_energies_chart_b": ["1/2", "3/2"],
        "signed_base_cross": "15/16",
        "signed_step_crosses": ["-1/16", "15/8"],
        "signed_terminal_cross": "11/4",
    },
    "independent": {
        "causal_prefix_ranks": [1, 2],
        "centred_common_terminal_ratio_at_t3": "6/7",
        "eight_atom_base_cross": "-11/32",
        "eight_atom_step_crosses": ["-123/32", "-3/16", "-53/8"],
        "eight_atom_terminal_cross": "-11",
        "piecewise_signed_bracket": "27/10",
        "production_affine_ray_curvature_lower": "2223/(25000*P)",
        "production_noncollinear_zero_floor_curvature": "-99/(250*P)",
    },
}

EXPECTED_HISTOGRAMS = {
    "primary": {
        "authority": 20,
        "doob": 9,
        "law-boundary": 4,
        "matching": 9,
        "metadata": 4,
        "nogo": 6,
        "production-boundary": 8,
        "production-coefficients": 3,
        "production-ray": 16,
        "relative": 3,
        "scope": 6,
        "signature": 9,
        "transfer": 4,
    },
    "independent": {
        "authority": 20,
        "continuous": 2,
        "doob": 12,
        "law-boundary": 4,
        "matching": 5,
        "metadata": 3,
        "nogo": 3,
        "production-boundary": 7,
        "production-coefficients": 3,
        "production-ray": 10,
        "scope": 9,
        "signature": 11,
        "transfer": 4,
    },
}

EXPECTED_IDENTITY_HASHES = {
    "primary": "580773f767083d1e42e2569f732eb377be942a9b2fa778be17dd863cc5f18674",
    "independent": "a5c308379cf10e6cc13c6b4c9fd68d9f55aa1e66b75992cbc7fac5fc589a59e4",
}


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(
        self,
        group: str,
        name: str,
        condition: bool,
        actual: object,
        expected: object,
    ) -> None:
        passed = bool(condition)
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if passed else "FAIL",
                "actual": str(actual),
                "expected": str(expected),
            }
        )


def atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")


def assertion_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    assertions = payload.get("assertions", {})
    rows = assertions.get("rows") if isinstance(assertions, dict) else assertions
    if not isinstance(rows, list):
        raise TypeError("child assertion rows unavailable")
    return rows


def assertion_total(payload: dict[str, Any]) -> int:
    assertions = payload.get("assertions", {})
    if isinstance(assertions, dict) and "total" in assertions:
        return int(assertions["total"])
    return len(assertion_rows(payload))


def run_child(script: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script)],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )


def imported_roots(path: Path) -> tuple[set[str], bool]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    relative_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            relative_import = relative_import or node.level > 0
            if node.module:
                roots.add(node.module.split(".")[0])
    return roots, relative_import


def literal_container(node: ast.AST) -> bool:
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return all(literal_container(item) for item in node.elts)
    if isinstance(node, ast.Dict):
        return all(
            literal_container(key) and literal_container(value)
            for key, value in zip(node.keys, node.values)
            if key is not None
        )
    return False


def source_regressions(path: Path) -> dict[str, list[str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    constant_conditions: list[str] = []
    self_comparisons: list[str] = []
    literal_outputs: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            function = node.func
            function_name = (
                function.attr
                if isinstance(function, ast.Attribute)
                else function.id if isinstance(function, ast.Name) else ""
            )
            if function_name in {"check", "add"} and len(node.args) >= 3:
                condition = node.args[2]
                if isinstance(condition, ast.Constant) and isinstance(
                    condition.value, bool
                ):
                    constant_conditions.append(f"line {node.lineno}")
        if isinstance(node, ast.Compare) and len(node.comparators) == 1:
            if ast.dump(node.left) == ast.dump(node.comparators[0]):
                self_comparisons.append(f"line {node.lineno}")
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if (
                    isinstance(key, ast.Constant)
                    and key.value in {"exact_values", "cross_values"}
                    and isinstance(value, ast.Dict)
                ):
                    for output_key, output_value in zip(value.keys, value.values):
                        if literal_container(output_value):
                            label = (
                                output_key.value
                                if isinstance(output_key, ast.Constant)
                                else ast.dump(output_key)
                            )
                            literal_outputs.append(f"line {output_value.lineno}: {label}")
    return {
        "constant_conditions": constant_conditions,
        "self_comparisons": self_comparisons,
        "literal_outputs": literal_outputs,
    }


def identity_hash(rows: list[dict[str, Any]]) -> str:
    identities = sorted(
        f"{row.get('category', row.get('group'))}::{row.get('name')}"
        for row in rows
    )
    payload = ("\n".join(identities) + "\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_pdf() -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = "1785628800"
    environment["FORCE_SOURCE_DATE"] = "1"
    return subprocess.run(
        [sys.executable, str(PDF_BUILDER), str(NOTE.relative_to(REPO))],
        cwd=REPO,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )


def find_poppler(name: str) -> Path | None:
    runtime = Path.home() / ".cache" / "codex-runtimes"
    for candidate in runtime.glob(
        f"*/dependencies/native/poppler/Library/bin/{name}.exe"
    ):
        if candidate.is_file():
            return candidate
    discovered = shutil.which(name)
    return Path(discovered) if discovered else None


def render_pdf(directory: Path) -> tuple[int, str, list[Path]]:
    renderer = find_poppler("pdftoppm")
    if renderer is None:
        return 127, "pdftoppm unavailable", []
    run = subprocess.run(
        [str(renderer), "-png", "-r", "130", str(PDF), str(directory / "page")],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    return run.returncode, "\n".join((run.stdout, run.stderr)).strip(), sorted(
        directory.glob("page-*.png")
    )


def pdf_security(reader: PdfReader) -> list[str]:
    findings: list[str] = []
    visited: set[tuple[int, int]] = set()
    unsafe_keys = {
        "/JS", "/JavaScript", "/AA", "/Launch", "/AF", "/EF",
        "/EmbeddedFiles", "/RichMedia", "/Movie", "/Sound", "/XFA",
        "/SubmitForm", "/ImportData",
    }
    unsafe_actions = {
        "/JavaScript", "/Launch", "/GoToR", "/SubmitForm", "/ImportData",
        "/Rendition", "/Movie", "/Sound", "/URI",
    }

    def resolve(value: Any) -> Any:
        return value.get_object() if isinstance(value, IndirectObject) else value

    def visit(value: Any, location: str) -> None:
        if isinstance(value, IndirectObject):
            marker = (value.idnum, value.generation)
            if marker in visited:
                return
            visited.add(marker)
            value = value.get_object()
        if isinstance(value, DictionaryObject):
            action = resolve(value.get("/S"))
            if str(action) in unsafe_actions:
                findings.append(f"{location}/S={action}")
            for key, child in value.items():
                if str(key) in unsafe_keys:
                    findings.append(f"{location}{key}")
                visit(child, f"{location}{key}")
        elif isinstance(value, ArrayObject):
            for index, child in enumerate(value):
                visit(child, f"{location}[{index}]")

    visit(resolve(reader.trailer["/Root"]), "/Root")
    return sorted(set(findings))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    primary_run = run_child(PRIMARY)
    independent_run = run_child(INDEPENDENT)
    audit.check(
        "children", "primary exits zero", primary_run.returncode == 0,
        primary_run.returncode, 0,
    )
    audit.check(
        "children", "independent exits zero", independent_run.returncode == 0,
        independent_run.returncode, 0,
    )
    primary = load_json(PRIMARY_OUTPUT)
    independent = load_json(INDEPENDENT_OUTPUT)
    children = {"primary": primary, "independent": independent}
    expected_counts = {"primary": 101, "independent": 93}
    expected_schemas = {
        "primary": f"tect/a13-{SLUG}-primary/1.0",
        "independent": f"tect/a13-{SLUG}-independent/1.0",
    }
    expected_top_keys = {
        "primary": {
            "assertions", "claim_id", "cross_values", "exact_values",
            "no_overclaim", "result_id", "schema", "scope",
            "script_version", "status", "theorem_summary",
        },
        "independent": {
            "assertions", "claim_id", "cross_values", "exact_values",
            "independence", "no_overclaim", "result_id", "schema", "scope",
            "script_version", "status",
        },
    }
    for name, child in children.items():
        rows = assertion_rows(child)
        histogram = dict(sorted(Counter(
            row.get("category", row.get("group")) for row in rows
        ).items()))
        audit.check(
            "children", f"{name} top-level schema keys",
            set(child) == expected_top_keys[name], sorted(child),
            sorted(expected_top_keys[name]),
        )
        audit.check(
            "children", f"{name} schema",
            child.get("schema") == expected_schemas[name], child.get("schema"),
            expected_schemas[name],
        )
        audit.check(
            "children", f"{name} claim", child.get("claim_id") == CLAIM,
            child.get("claim_id"), CLAIM,
        )
        audit.check(
            "children", f"{name} result", child.get("result_id") == RESULT_ID,
            child.get("result_id"), RESULT_ID,
        )
        audit.check(
            "children", f"{name} status", child.get("status") == "PASS",
            child.get("status"), "PASS",
        )
        audit.check(
            "children", f"{name} all pass",
            all(row.get("status") == "PASS" for row in rows),
            [row for row in rows if row.get("status") != "PASS"], [],
        )
        audit.check(
            "children", f"{name} frozen count",
            assertion_total(child) == expected_counts[name],
            assertion_total(child), expected_counts[name],
        )
        audit.check(
            "children", f"{name} count self-consistent",
            len(rows) == assertion_total(child), len(rows), assertion_total(child),
        )
        audit.check(
            "children", f"{name} assertion histogram",
            histogram == EXPECTED_HISTOGRAMS[name], histogram,
            EXPECTED_HISTOGRAMS[name],
        )
        audit.check(
            "children", f"{name} row identity hash",
            identity_hash(rows) == EXPECTED_IDENTITY_HASHES[name],
            identity_hash(rows), EXPECTED_IDENTITY_HASHES[name],
        )
        audit.check(
            "children", f"{name} exact values",
            child.get("exact_values") == EXPECTED_EXACT_VALUES[name],
            child.get("exact_values"), EXPECTED_EXACT_VALUES[name],
        )
        audit.check(
            "children", f"{name} exact scope",
            child.get("scope") == EXPECTED_SCOPE, child.get("scope"),
            EXPECTED_SCOPE,
        )

    audit.check(
        "aggregation", "embedded child count",
        sum(assertion_total(child) for child in children.values()) == 194,
        sum(assertion_total(child) for child in children.values()), 194,
    )
    audit.check(
        "cross", "child cross values agree",
        primary.get("cross_values") == independent.get("cross_values"),
        (primary.get("cross_values"), independent.get("cross_values")), "equal",
    )
    audit.check(
        "cross", "shared exact production values",
        primary.get("cross_values") == EXPECTED_CROSS_VALUES,
        primary.get("cross_values"), EXPECTED_CROSS_VALUES,
    )

    independent_roots, relative_import = imported_roots(INDEPENDENT)
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    audit.check(
        "independence", "no relative imports", not relative_import,
        relative_import, False,
    )
    audit.check(
        "independence", "no forbidden numerical libraries",
        not (independent_roots & {"numpy", "scipy"}),
        sorted(independent_roots & {"numpy", "scipy"}), [],
    )
    audit.check(
        "independence", "SymPy explicitly permitted",
        "sympy" in independent_roots, sorted(independent_roots), "contains sympy",
    )
    audit.check(
        "independence", "does not import another A13 executable",
        not any(root.startswith("a13_classii") for root in independent_roots),
        sorted(independent_roots), "no a13_classii import",
    )
    forbidden_artifact_tokens = (
        PRIMARY.name,
        PRIMARY_OUTPUT.parent.name,
        "2026-08-02-primary-canonical-signed-common-terminal",
    )
    audit.check(
        "independence", "does not name or read primary artifacts",
        not any(token in independent_text for token in forbidden_artifact_tokens),
        [token for token in forbidden_artifact_tokens if token in independent_text],
        [],
    )
    for name, path in (("primary", PRIMARY), ("independent", INDEPENDENT)):
        regressions = source_regressions(path)
        audit.check(
            "source", f"{name} no constant-boolean assertions",
            regressions["constant_conditions"] == [],
            regressions["constant_conditions"], [],
        )
        audit.check(
            "source", f"{name} no direct self-comparisons",
            regressions["self_comparisons"] == [],
            regressions["self_comparisons"], [],
        )
        audit.check(
            "source", f"{name} no literal derived outputs",
            regressions["literal_outputs"] == [],
            regressions["literal_outputs"], [],
        )

    manifest = load_json(MANIFEST)
    note_text = NOTE.read_text(encoding="utf-8")
    note_tokens = (
        RESULT_ID,
        "Ledger: R-147",
        "section-2-feature",
        "section-3-signed-doob",
        "section-4-transfer",
        "section-5-bracket-defect",
        "section-6-common-terminal-nogo",
        "section-7-production-ray",
        "section-8-noncollinear",
        "section-9-roadmap",
        "martingale-representation",
        r"\bar\tau",
        "2223",
        "25000P",
        r"-{1\over12}",
        r"5\sqrt{154}\over132",
        "Devil's-advocate",
        "Result footer",
        "phase selection",
        "T-050 closed: false",
        "Sector A closed: false",
    )
    for token in note_tokens:
        audit.check("note", token, token in note_text, token in note_text, True)
    for negative_id in NEGATIVE_IDS:
        audit.check(
            "note", negative_id, negative_id in note_text,
            negative_id in note_text, True,
        )

    initial_pdf_hash = sha256(PDF)
    build = build_pdf()
    audit.check(
        "pdf", "build exits zero", build.returncode == 0,
        (build.returncode, build.stderr), 0,
    )
    audit.check(
        "pdf", "form check", "FORM-CHECK: PASS" in build.stdout,
        build.stdout, "FORM-CHECK: PASS",
    )
    audit.check(
        "pdf", "zero overfull", "OVERFULL-HBOX: 0" in build.stdout,
        build.stdout, "OVERFULL-HBOX: 0",
    )
    rebuilt_pdf_hash = sha256(PDF)
    audit.check(
        "pdf", "deterministic rebuild", rebuilt_pdf_hash == initial_pdf_hash,
        (initial_pdf_hash, rebuilt_pdf_hash), "equal",
    )
    reader = PdfReader(str(PDF), strict=True)
    page_text = [(page.extract_text() or "") for page in reader.pages]
    extracted = "\n".join(page_text)
    audit.check(
        "pdf", "not encrypted", reader.is_encrypted is False,
        reader.is_encrypted, False,
    )
    audit.check("pdf", "ten pages", len(reader.pages) == 10, len(reader.pages), 10)
    audit.check(
        "pdf", "all pages nonblank",
        all(len(text.strip()) >= 100 for text in page_text),
        [len(text.strip()) for text in page_text], ">=100 each",
    )
    for token in (
        LEDGER_ID,
        "not to force BCC",
        "Proof complete: false",
        "T-050 closed: false",
        "Sector A closed: false",
        "common-terminal",
        "trace-bracket",
        "global convexity",
        "2223",
    ):
        audit.check(
            "pdf", f"extracts {token}", token in extracted,
            token in extracted, True,
        )
    audit.check(
        "pdf", "no replacement glyph", "\ufffd" not in extracted,
        "\ufffd" in extracted, False,
    )
    audit.check(
        "pdf", "no form fields", reader.get_fields() in (None, {}),
        reader.get_fields(), None,
    )
    security_findings = pdf_security(reader)
    audit.check(
        "pdf", "no unsafe actions", security_findings == [],
        security_findings, [],
    )
    with tempfile.TemporaryDirectory(prefix="tect-r147-render-") as temporary:
        render_code, render_log, rendered = render_pdf(Path(temporary))
        audit.check(
            "pdf", "Poppler exits zero", render_code == 0,
            (render_code, render_log), 0,
        )
        audit.check(
            "pdf", "all pages rendered", len(rendered) == len(reader.pages),
            len(rendered), len(reader.pages),
        )
        audit.check(
            "pdf", "rendered pages nonempty",
            all(path.stat().st_size > 0 for path in rendered),
            [path.stat().st_size for path in rendered], "positive",
        )
        rendered_hashes = [sha256(path) for path in rendered]

    exploration_records = {
        record["id"]: record
        for record in (
            json.loads(line)
            for line in (REPO / "explorations/log.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        )
    }
    expected_verdicts = {
        "EXP-000615": "advanced",
        "EXP-000616": "advanced",
        "EXP-000617": "failed",
        "EXP-000618": "advanced",
        "EXP-000619": "failed",
        "EXP-000620": "failed",
        "EXP-000621": "advanced",
        "EXP-000622": "failed",
    }
    for exploration_id in EXPLORATION_IDS:
        exists = exploration_id in exploration_records
        audit.check(
            "exploration", f"{exploration_id} exists", exists, exists, True,
        )
        if not exists:
            continue
        record = exploration_records[exploration_id]
        audit.check(
            "exploration", f"{exploration_id} verdict",
            record.get("verdict") == expected_verdicts[exploration_id],
            record.get("verdict"), expected_verdicts[exploration_id],
        )
        audit.check(
            "exploration", f"{exploration_id} evidence",
            len(record.get("evidence_refs", [])) >= 1,
            len(record.get("evidence_refs", [])), ">=1",
        )
        for field in ("question", "finding", "boundary", "next_action"):
            audit.check(
                "exploration", f"{exploration_id} {field}",
                bool(record.get(field)), record.get(field), "nonempty",
            )

    registry = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for negative_id in NEGATIVE_IDS:
        audit.check(
            "negative", negative_id, negative_id.lower() in registry.lower(),
            negative_id.lower() in registry.lower(), True,
        )

    authority_hashes: dict[str, str] = {}
    audit.check(
        "authority", "exact authority set",
        set(manifest.get("authorities", {})) == {
            "A1", "R-075", "R-063", "R-104", "R-125", "R-130",
            "R-136", "R-141", "R-142", "R-146",
        },
        sorted(manifest.get("authorities", {})),
        sorted({
            "A1", "R-075", "R-063", "R-104", "R-125", "R-130",
            "R-136", "R-141", "R-142", "R-146",
        }),
    )
    for name, path_text in manifest.get("authorities", {}).items():
        path = REPO / path_text
        audit.check(
            "authority", f"{name} exists", path.is_file(),
            relative(path), "file",
        )
        if path.is_file():
            authority_hashes[name] = sha256(path)
    audit.check(
        "authority", "hashes pinned",
        manifest.get("authority_hashes") == authority_hashes,
        manifest.get("authority_hashes"), authority_hashes,
    )

    audit.check(
        "manifest", "claim", manifest.get("claim_id") == CLAIM,
        manifest.get("claim_id"), CLAIM,
    )
    audit.check(
        "manifest", "result", manifest.get("result_id") == RESULT_ID,
        manifest.get("result_id"), RESULT_ID,
    )
    audit.check(
        "manifest", "ledger", manifest.get("result_ledger_id") == LEDGER_ID,
        manifest.get("result_ledger_id"), LEDGER_ID,
    )
    audit.check(
        "manifest", "scope exact", manifest.get("scope") == EXPECTED_SCOPE,
        manifest.get("scope"), EXPECTED_SCOPE,
    )
    audit.check(
        "manifest", "proof incomplete", manifest.get("proof_complete") is False,
        manifest.get("proof_complete"), False,
    )
    audit.check(
        "manifest", "T-050 open", manifest.get("t050_closed") is False,
        manifest.get("t050_closed"), False,
    )
    audit.check(
        "manifest", "Sector A open", manifest.get("sector_a_closed") is False,
        manifest.get("sector_a_closed"), False,
    )
    audit.check(
        "manifest", "phase-neutral no-overclaim",
        "select BCC or any physical phase" in manifest.get("no_overclaim", ""),
        manifest.get("no_overclaim"), "contains explicit non-selection",
    )
    audit.check(
        "manifest", "visual QA",
        str(manifest.get("verification", {}).get("pdf", {})
            .get("manual_visual_qa", "")).startswith("PASS"),
        manifest.get("verification", {}).get("pdf", {})
        .get("manual_visual_qa"), "PASS*",
    )
    audit.check(
        "manifest", "exploration ids",
        set(EXPLORATION_IDS) <= set(manifest.get("exploration_ids", [])),
        sorted(set(EXPLORATION_IDS) - set(manifest.get("exploration_ids", []))), [],
    )
    audit.check(
        "manifest", "negative ids",
        set(NEGATIVE_IDS) <= set(manifest.get("negative_results", [])),
        sorted(set(NEGATIVE_IDS) - set(manifest.get("negative_results", []))), [],
    )
    expected_files = {
        "primary": PRIMARY,
        "independent": INDEPENDENT,
        "verifier": Path(__file__),
        "note": NOTE,
        "pdf": PDF,
        "primary_result": PRIMARY_OUTPUT,
        "independent_result": INDEPENDENT_OUTPUT,
    }
    for key, path in expected_files.items():
        entry = manifest.get("files", {}).get(key, {})
        audit.check(
            "manifest", f"{key} path",
            str(entry.get("path", "")).replace("\\", "/") == relative(path),
            entry.get("path"), relative(path),
        )
        audit.check(
            "manifest", f"{key} hash", entry.get("sha256") == sha256(path),
            entry.get("sha256"), sha256(path),
        )
    verification = manifest.get("verification", {})
    audit.check(
        "manifest", "primary count",
        int(verification.get("primary_assertions", -1)) == 101,
        verification.get("primary_assertions"), 101,
    )
    audit.check(
        "manifest", "independent count",
        int(verification.get("independent_assertions", -1)) == 93,
        verification.get("independent_assertions"), 93,
    )
    audit.check(
        "manifest", "embedded count",
        int(verification.get("embedded_child_assertions", -1)) == 194,
        verification.get("embedded_child_assertions"), 194,
    )
    audit.check(
        "manifest", "integrator count",
        int(verification.get("integrator_only_assertions", -1))
        == FROZEN_INTEGRATOR_ONLY,
        verification.get("integrator_only_assertions"), FROZEN_INTEGRATOR_ONLY,
    )
    audit.check(
        "manifest", "integrated count",
        int(verification.get("integrated_assertions", -1))
        == 194 + FROZEN_INTEGRATOR_ONLY,
        verification.get("integrated_assertions"),
        194 + FROZEN_INTEGRATOR_ONLY,
    )
    audit.check(
        "manifest", "PDF hash",
        manifest["files"]["pdf"]["sha256"] == rebuilt_pdf_hash,
        manifest["files"]["pdf"]["sha256"], rebuilt_pdf_hash,
    )
    pdf_meta = verification.get("pdf", {})
    audit.check(
        "manifest", "PDF deterministic", pdf_meta.get("deterministic") is True,
        pdf_meta.get("deterministic"), True,
    )
    audit.check(
        "manifest", "PDF security", pdf_meta.get("security_check") == "PASS",
        pdf_meta.get("security_check"), "PASS",
    )
    audit.check(
        "manifest", "PDF text", pdf_meta.get("text_check") == "PASS",
        pdf_meta.get("text_check"), "PASS",
    )
    audit.check(
        "manifest", "PDF pages", int(pdf_meta.get("pages", -1)) == 10,
        pdf_meta.get("pages"), 10,
    )
    audit.check(
        "manifest", "PDF size",
        int(pdf_meta.get("size_bytes", -1)) == PDF.stat().st_size,
        pdf_meta.get("size_bytes"), PDF.stat().st_size,
    )
    audit.check(
        "manifest", "PDF rendered pages",
        int(pdf_meta.get("rendered_pages", -1)) == len(rendered_hashes),
        pdf_meta.get("rendered_pages"), len(rendered_hashes),
    )

    public = {
        "results ledger": (REPO / "RESULTS-LEDGER.md", '<a id="r-147"></a>'),
        "claim status": (CLAIM_DIR / "status.json", RESULT_ID),
        "claim chronology": (CLAIM_DIR / "claim.md", "R-147"),
        "lineage": (CLAIM_DIR / "LINEAGE.md", SLUG),
        "theorem map": (REPO / "governance/sector-a-theorem-map.json", RESULT_ID),
        "T-050 task": (REPO / "todo/todo.json", "R-147"),
        "changelog": (REPO / "CHANGELOG.md", "R-147"),
        "claims ledger": (REPO / "CLAIMS.md", CLAIM),
        "proof map": (REPO / "theory/proof-evidence-map.md", "R-147"),
        "catalog": (REPO / "CATALOG.md", MANIFEST.name),
    }
    for name, (path, token) in public.items():
        audit.check(
            "surface", f"{name} file", path.is_file(), relative(path), "file",
        )
        surface_text = path.read_text(encoding="utf-8") if path.is_file() else ""
        audit.check(
            "surface", name, token in surface_text, token in surface_text, True,
        )

    child_rows: list[dict[str, object]] = []
    identities: set[str] = set()
    duplicates: list[str] = []
    for child_name, child in children.items():
        for row in assertion_rows(child):
            identity = (
                f"{child_name}:{row.get('category', row.get('group'))}::"
                f"{row.get('name')}"
            )
            if identity in identities:
                duplicates.append(identity)
            identities.add(identity)
            child_rows.append(
                {
                    "group": (
                        f"{child_name}:"
                        f"{row.get('category', row.get('group'))}"
                    ),
                    "name": row.get("name"),
                    "status": row.get("status"),
                    "actual": row.get("actual"),
                    "expected": row.get("expected"),
                }
            )
    audit.check(
        "aggregation", "child identities unique", duplicates == [], duplicates, [],
    )
    predicted_integrator_only = len(audit.rows) + 1
    audit.check(
        "aggregation", "frozen integrator-only count",
        predicted_integrator_only == FROZEN_INTEGRATOR_ONLY,
        predicted_integrator_only, FROZEN_INTEGRATOR_ONLY,
    )
    integrator_only = len(audit.rows)
    all_rows = child_rows + audit.rows
    failed = sum(row["status"] != "PASS" for row in all_rows)
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "issued": __version_issued__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "tier": "T4",
        "status": "PASS" if failed == 0 else "FAIL",
        "assertions": {
            "total": len(all_rows),
            "passed": len(all_rows) - failed,
            "failed": failed,
            "rows": all_rows,
        },
        "assertion_accounting": {
            "embedded_child_assertions": len(child_rows),
            "integrator_only_assertions": integrator_only,
            "unique_package_assertions": len(all_rows),
        },
        "children": {
            "primary": {
                "path": relative(PRIMARY_OUTPUT),
                "sha256": sha256(PRIMARY_OUTPUT),
                "assertions": assertion_total(primary),
                "stdout": primary_run.stdout,
            },
            "independent": {
                "path": relative(INDEPENDENT_OUTPUT),
                "sha256": sha256(INDEPENDENT_OUTPUT),
                "assertions": assertion_total(independent),
                "stdout": independent_run.stdout,
            },
        },
        "source_hashes": {
            "primary": sha256(PRIMARY),
            "independent": sha256(INDEPENDENT),
            "verifier": sha256(Path(__file__)),
            "note": sha256(NOTE),
            "pdf": rebuilt_pdf_hash,
            "manifest": sha256(MANIFEST),
            "authorities": authority_hashes,
        },
        "cross_values": EXPECTED_CROSS_VALUES,
        "pdf_audit": {
            "path": relative(PDF),
            "sha256": rebuilt_pdf_hash,
            "size_bytes": PDF.stat().st_size,
            "pages": len(reader.pages),
            "deterministic_rebuild": True,
            "form_check": True,
            "overfull_hbox_count": 0,
            "security_findings": security_findings,
            "renderer": "Poppler pdftoppm",
            "dpi": 130,
            "rendered_pages": len(rendered_hashes),
            "page_sha256": rendered_hashes,
            "manual_visual_qa": manifest["verification"]["pdf"]
            ["manual_visual_qa"],
        },
        "scope": manifest["scope"],
        "no_overclaim": manifest["no_overclaim"],
    }
    atomic_json(args.output, payload)
    print(
        f"{RESULT_ID}: {'PASS' if failed == 0 else 'FAIL'} "
        f"({len(all_rows) - failed}/{len(all_rows)}; "
        f"children={len(child_rows)}, integrator={integrator_only})"
    )
    print(f"output: {args.output}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
