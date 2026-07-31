#!/usr/bin/env python3
"""Integrated verifier for the scoped A13 R-140 evidence package.

The integrator reruns both independent certificates, embeds their assertion
rows exactly once, independently checks the load-bearing scalar/operator and
hostile-audit fixtures, validates the registered authorities and public
surfaces, and rebuilds/renders/audits the proof PDF.  It deliberately derives
the child assertion counts from the child payloads instead of freezing them in
this source.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
import ast
from fractions import Fraction
import hashlib
import itertools
import json
import math
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
RESULT_ID = (
    "A13-CLASSII-PREDICTABLE-TRIANGULAR-MIXED-GRAM-"
    "SOURCE-GRAPH-FESHBACH-BOUNDARY"
)
SCHEMA = (
    "tect/a13-predictable-triangular-mixed-gram-source-graph-"
    "feshbach-boundary-integrated/1.0"
)
LEDGER_ID = "R-140"
CLAIM_DIR = REPO / "claims" / CLAIM
SLUG = "predictable-triangular-mixed-gram-source-graph-feshbach-boundary"
NOTE = CLAIM_DIR / f"notes/classii-{SLUG}-260731-v1.0.tex.txt"
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
MANIFEST = CLAIM_DIR / "classii_predictable_triangular_mixed_gram_source_graph_feshbach_boundary_manifest.json"
EXPLORATION_IDS = tuple(f"EXP-{number:06d}" for number in range(559, 568))

PRIMARY = REPO / "codes/foundations/a13_classii_predictable_triangular_mixed_gram_source_graph_feshbach_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_predictable_triangular_mixed_gram_source_graph_feshbach_boundary_independent.py"
DEFAULT_PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-07-31-primary-{SLUG}/result.json"
DEFAULT_INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-07-31-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-07-31-integrated-{SLUG}/result.json"

AUTHORITIES = {
    "R-063": (
        "classii_balanced_coefficient_jet_continuum_manifest.json",
        "A13-CLASSII-BALANCED-COEFFICIENT-JET-CONTINUUM-AND-A7-RECONSTRUCTION",
    ),
    "R-067": (
        "classii_npc_cone_martingale_injection_reduction_manifest.json",
        "A13-CLASSII-NPC-CONE-MARTINGALE-INJECTION-REDUCTION",
    ),
    "R-079": (
        "classii_full_safe_packet_frame_current_doob_manifest.json",
        "A13-CLASSII-FULL-SAFE-PACKET-FRAME-CURRENT-DOOB-DECOMPOSITION",
    ),
    "R-087": (
        "classii_cartan_spatial_decay_rational_trace_variational_core_reduction_manifest.json",
        "A13-CLASSII-CARTAN-SPATIAL-DECAY-RATIONAL-TRACE-VARIATIONAL-CORE-REDUCTION",
    ),
    "R-099": (
        "classii_extended_state_cartan_doob_rational_recovery_manifest.json",
        "A13-CLASSII-EXTENDED-STATE-CARTAN-DOOB-RATIONAL-RECOVERY",
    ),
    "R-102": (
        "classii_full_hessian_laplace_wick_future_feedback_boundary_manifest.json",
        "A13-CLASSII-FULL-HESSIAN-LAPLACE-WICK-FUTURE-FEEDBACK-BOUNDARY",
    ),
    "R-103": (
        "classii_regular_complete_packet_ownership_hn_reg_closure_manifest.json",
        "A13-CLASSII-REGULAR-COMPLETE-PACKET-OWNERSHIP-HN-REG-CLOSURE",
    ),
    "R-104": (
        "classii_lossless_progressive_complete_owner_assembly_heat_boundary_manifest.json",
        "A13-CLASSII-LOSSLESS-PROGRESSIVE-COMPLETE-OWNER-ASSEMBLY-HEAT-BOUNDARY",
    ),
    "R-123": (
        "classii_six_row_trace_excess_direct_action_boundary_manifest.json",
        "A13-CLASSII-SIX-ROW-TRACE-EXCESS-DIRECT-ACTION-CORRELATION-BOUNDARY",
    ),
    "R-125": (
        "classii_conditional_variance_forest_bridge_root_shell_operator_boundary_manifest.json",
        "A13-CLASSII-CONDITIONAL-VARIANCE-FOREST-BRIDGE-ROOT-SHELL-OPERATOR-BOUNDARY",
    ),
    "R-128": (
        "classii_owner_complete_source_pullback_covariance_normal_force_boundary_manifest.json",
        "A13-CLASSII-OWNER-COMPLETE-SOURCE-PULLBACK-COVARIANCE-NORMAL-FORCE-BOUNDARY",
    ),
    "R-129": (
        "classii_endpoint_trace_excess_shell_coanalysis_shifted_douglas_boundary_manifest.json",
        "A13-CLASSII-ENDPOINT-TRACE-EXCESS-SHELL-COANALYSIS-SHIFTED-DOUGLAS-BOUNDARY",
    ),
    "R-131": (
        "classii_owner_complete_physical_response_mixed_gram_shell_boundary_manifest.json",
        "A13-CLASSII-OWNER-COMPLETE-PHYSICAL-RESPONSE-MIXED-GRAM-SHELL-BOUNDARY",
    ),
    "R-133": (
        "classii_affine_gaussian_score_feedback_collar_boundary_manifest.json",
        "A13-CLASSII-AFFINE-GAUSSIAN-SCORE-FEEDBACK-COLLAR-BOUNDARY",
    ),
    "R-136": (
        "classii_common_heat_replica_raw_sequential_owner_boundary_manifest.json",
        "A13-CLASSII-COMMON-HEAT-REPLICA-RAW-SEQUENTIAL-OWNER-BOUNDARY",
    ),
    "R-139": (
        "classii_signed_future_endpoint_graph_complement_boundary_manifest.json",
        "A13-CLASSII-SIGNED-FUTURE-ENDPOINT-GRAPH-COMPLEMENT-BOUNDARY",
    ),
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
        if not passed:
            raise AssertionError(f"{group}::{name}: {actual!r} != {expected!r}")


def atomic_json(path: Path, payload: dict[str, object]) -> None:
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO.resolve()))
    except ValueError:
        return str(path.resolve())


def run_child(script: Path, output: Path) -> tuple[int, str, str]:
    result = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    return result.returncode, result.stdout, result.stderr


def assertion_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    block = payload.get("assertions")
    if isinstance(block, dict) and isinstance(block.get("rows"), list):
        return block["rows"]
    if isinstance(block, list):
        return block
    raise TypeError("child assertions must be a row list or a mapping with rows")


def assertion_total(payload: dict[str, Any]) -> int:
    rows = assertion_rows(payload)
    block = payload.get("assertions")
    if isinstance(block, dict) and "total" in block:
        return int(block["total"])
    return len(rows)


def assertion_failed(payload: dict[str, Any]) -> int:
    block = payload.get("assertions")
    if isinstance(block, dict) and "failed" in block:
        return int(block["failed"])
    return sum(str(row.get("status")) != "PASS" for row in assertion_rows(payload))


def assertion_names(payload: dict[str, Any]) -> set[str]:
    return {
        f"{row.get('group')}::{row.get('name')}".lower()
        for row in assertion_rows(payload)
    }


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


def pdf_security_audit(reader: PdfReader) -> dict[str, Any]:
    findings: list[str] = []
    visited: set[tuple[int, int]] = set()
    unsafe_actions = {
        "/JavaScript",
        "/Launch",
        "/GoToR",
        "/SubmitForm",
        "/ImportData",
        "/Rendition",
        "/Movie",
        "/Sound",
        "/URI",
    }
    unsafe_keys = {
        "/JS",
        "/JavaScript",
        "/AA",
        "/Launch",
        "/AF",
        "/EF",
        "/EmbeddedFiles",
        "/RichMedia",
        "/Movie",
        "/Sound",
        "/XFA",
        "/SubmitForm",
        "/ImportData",
    }

    def resolve(value: Any) -> Any:
        return value.get_object() if isinstance(value, IndirectObject) else value

    def visit(value: Any, path: str) -> None:
        if isinstance(value, IndirectObject):
            marker = (value.idnum, value.generation)
            if marker in visited:
                return
            visited.add(marker)
            value = value.get_object()
        if isinstance(value, DictionaryObject):
            action_type = resolve(value.get("/S"))
            if str(action_type) in unsafe_actions:
                findings.append(f"{path}/S={action_type}")
            for key, child in value.items():
                key_text = str(key)
                if key_text in unsafe_keys:
                    findings.append(f"{path}{key_text}")
                visit(child, f"{path}{key_text}")
        elif isinstance(value, ArrayObject):
            for index, child in enumerate(value):
                visit(child, f"{path}[{index}]")

    root = resolve(reader.trailer["/Root"])
    visit(root, "/Root")
    open_action = resolve(root.get("/OpenAction"))
    if open_action is None:
        open_action_kind, safe_open_action = "absent", True
    elif isinstance(open_action, ArrayObject):
        open_action_kind, safe_open_action = "destination-array", True
    elif isinstance(open_action, DictionaryObject):
        open_action_kind = str(resolve(open_action.get("/S")))
        safe_open_action = open_action_kind == "/GoTo"
    else:
        open_action_kind, safe_open_action = type(open_action).__name__, False

    widgets = 0
    annotations: list[str] = []
    for page_index, page in enumerate(reader.pages, start=1):
        for annotation_index, annotation in enumerate(resolve(page.get("/Annots")) or []):
            annotation = resolve(annotation)
            subtype = str(resolve(annotation.get("/Subtype")))
            if subtype == "/Widget":
                widgets += 1
            if subtype in {"/FileAttachment", "/RichMedia", "/Movie", "/Sound"}:
                annotations.append(
                    f"page-{page_index}/annot-{annotation_index}:{subtype}"
                )
    return {
        "findings": sorted(set(findings + annotations)),
        "open_action": open_action_kind,
        "safe_open_action": safe_open_action,
        "widget_count": widgets,
    }


def find_pdftoppm() -> Path | None:
    runtime = Path.home() / ".cache" / "codex-runtimes"
    candidates = [
        runtime
        / "codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe"
    ]
    candidates.extend(
        runtime.glob("*/dependencies/native/poppler/Library/bin/pdftoppm.exe")
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    discovered = shutil.which("pdftoppm")
    return Path(discovered) if discovered else None


def build_pdf() -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = "1785456000"
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


def render_pdf(output_dir: Path) -> tuple[int, str, list[Path]]:
    renderer = find_pdftoppm()
    if renderer is None:
        return 127, "pdftoppm unavailable", []
    run = subprocess.run(
        [
            str(renderer),
            "-png",
            "-r",
            "130",
            str(PDF),
            str(output_dir / "page"),
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    return (
        run.returncode,
        "\n".join((run.stdout, run.stderr)).strip(),
        sorted(output_dir.glob("page-*.png")),
    )


def close(left: float, right: float, tolerance: float = 1.0e-12) -> bool:
    return abs(left - right) <= tolerance * max(1.0, abs(left), abs(right))


def triangular_majorant(collar: int) -> float:
    beta = 7.0 / 5.0
    regularity = 2.0 / 3.0
    gamma = 7.0 / 12.0
    delta = collar - 5
    q = 2.0 ** (2.0 * gamma)
    u = 2.0 ** (-(beta - 2.0 * gamma))
    v = 2.0 ** (-beta)
    rho = 2.0 ** (-2.0 * (regularity - gamma))
    z = 2.0 ** (-(beta - 2.0 * regularity))
    near = (
        q ** (-delta) * u ** (delta + 1) / (1.0 - u)
        - v ** (delta + 1) / (1.0 - v)
    ) / (q - 1.0)
    newly_far = (
        2.0 ** (-2.0 * regularity * delta)
        / (1.0 - rho)
        * sum(z**a for a in range(1, delta + 1))
    )
    far = (
        2.0 ** (-2.0 * gamma * delta)
        * u ** (delta + 1)
        / ((1.0 - rho) * (1.0 - u))
    )
    return near + newly_far + far


def finite_triangular_sum(collar: int, cutoff: int = 420) -> float:
    beta = 7.0 / 5.0
    regularity = 2.0 / 3.0
    gamma = 7.0 / 12.0
    delta = collar - 5
    total = 0.0
    for a in range(1, cutoff + 1):
        source_decay = 2.0 ** (-beta * a)
        for d in range(cutoff + 1):
            spatial = (
                2.0 ** (-2.0 * regularity * (d - a + delta))
                if d >= a - delta
                else 1.0
            )
            total += 2.0 ** (2.0 * gamma * d) * source_decay * spatial
    return total


def signature(vector: tuple[Fraction, Fraction]) -> Fraction:
    return vector[0] * vector[0] - vector[1] * vector[1]


def euclidean_square(vector: tuple[Fraction, Fraction]) -> Fraction:
    return vector[0] * vector[0] + vector[1] * vector[1]


def add(
    left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]
) -> tuple[Fraction, Fraction]:
    return left[0] + right[0], left[1] + right[1]


def subtract(
    left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]
) -> tuple[Fraction, Fraction]:
    return left[0] - right[0], left[1] - right[1]


def signature_pairing(
    left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]
) -> Fraction:
    return left[0] * right[0] - left[1] * right[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--primary-output", type=Path, default=DEFAULT_PRIMARY_OUTPUT)
    parser.add_argument(
        "--independent-output", type=Path, default=DEFAULT_INDEPENDENT_OUTPUT
    )
    args = parser.parse_args()
    audit = Audit()

    primary_code, primary_stdout, primary_stderr = run_child(
        PRIMARY, args.primary_output
    )
    independent_code, independent_stdout, independent_stderr = run_child(
        INDEPENDENT, args.independent_output
    )
    for name, code, stdout, stderr, banner in (
        (
            "primary",
            primary_code,
            primary_stdout,
            primary_stderr,
            "R-140 primary PASS",
        ),
        (
            "independent",
            independent_code,
            independent_stdout,
            independent_stderr,
            "R-140 independent PASS",
        ),
    ):
        audit.check("children", f"{name} exit code", code == 0, code, 0)
        audit.check("children", f"{name} stderr empty", stderr == "", stderr, "")
        audit.check(
            "children",
            f"{name} PASS banner",
            banner in stdout,
            stdout.strip(),
            banner,
        )

    primary = load_json(args.primary_output)
    independent = load_json(args.independent_output)
    child_counts: dict[str, int] = {}
    for name, child, suffix in (
        ("primary", primary, "-primary/1.0"),
        ("independent", independent, "-independent/1.0"),
    ):
        rows = assertion_rows(child)
        total = assertion_total(child)
        child_counts[name] = total
        audit.check(
            "children",
            f"{name} schema",
            str(child.get("schema", "")).endswith(suffix),
            child.get("schema"),
            f"*{suffix}",
        )
        audit.check(
            "children",
            f"{name} result id",
            child.get("result_id") == RESULT_ID,
            child.get("result_id"),
            RESULT_ID,
        )
        audit.check(
            "children",
            f"{name} status",
            child.get("status") == "PASS",
            child.get("status"),
            "PASS",
        )
        audit.check(
            "children",
            f"{name} dynamic assertion count",
            total == len(rows),
            total,
            len(rows),
        )
        audit.check(
            "children",
            f"{name} failures zero",
            assertion_failed(child) == 0,
            assertion_failed(child),
            0,
        )
        audit.check(
            "children",
            f"{name} every row passes",
            all(str(row.get("status")) == "PASS" for row in rows),
            [row.get("name") for row in rows if row.get("status") != "PASS"],
            [],
        )

    for name, child in (("primary", primary), ("independent", independent)):
        names = "\n".join(sorted(assertion_names(child)))
        for contract, alternatives in {
            "triangular one-use": ("triangular", "one-use", "one use"),
            "scalar shell majorant": ("majorant", "hilbert", "h5", "hs", "geometric total"),
            "Feshbach identity": ("feshbach", "completed square", "completion"),
            "low kernel firewall": ("kernel", "semidefinite"),
            "source gap": (
                "source gap",
                "source-gap",
                "source margin",
                "source-only",
                "mu",
            ),
        }.items():
            audit.check(
                "contracts",
                f"{name} covers {contract}",
                any(token in names for token in alternatives),
                contract,
                "covered by assertion row names",
            )

    primary_computed = primary.get("computed", {})
    independent_computed = independent.get("computed", {})
    audit.check(
        "cross",
        "primary exposes computed mapping",
        isinstance(primary_computed, dict) and len(primary_computed) >= 10,
        len(primary_computed) if isinstance(primary_computed, dict) else type(primary_computed),
        ">=10 keys",
    )
    audit.check(
        "cross",
        "independent exposes computed mapping",
        isinstance(independent_computed, dict) and len(independent_computed) >= 10,
        len(independent_computed) if isinstance(independent_computed, dict) else type(independent_computed),
        ">=10 keys",
    )

    # Exact exponent arithmetic and the independently summed triangular
    # Hilbert--Schmidt majorant.
    beta = Fraction(7, 5)
    regularity = Fraction(2, 3)
    gamma = Fraction(7, 12)
    margin_source = beta / 2 - gamma
    margin_output = regularity - gamma
    audit.check(
        "triangular",
        "source margin exact",
        margin_source == Fraction(7, 60),
        margin_source,
        Fraction(7, 60),
    )
    audit.check(
        "triangular",
        "output margin exact",
        margin_output == Fraction(1, 12),
        margin_output,
        Fraction(1, 12),
    )
    h5 = triangular_majorant(5)
    h6 = triangular_majorant(6)
    audit.check(
        "triangular",
        "H5 closed value",
        close(h5, 56.298154029170504, 2.0e-14),
        h5,
        56.298154029170504,
    )
    audit.check(
        "triangular",
        "H6 closed value",
        close(h6, 24.8061980695711, 2.0e-14),
        h6,
        24.8061980695711,
    )
    finite_h5 = finite_triangular_sum(5)
    finite_h6 = finite_triangular_sum(6)
    audit.check(
        "triangular",
        "finite double sum converges to H5",
        close(finite_h5, h5, 2.0e-11),
        finite_h5 - h5,
        "relative <=2e-11",
    )
    audit.check(
        "triangular",
        "finite double sum converges to H6",
        close(finite_h6, h6, 2.0e-11),
        finite_h6 - h6,
        "relative <=2e-11",
    )
    audit.check("triangular", "collar six improves scalar debt", h6 < h5, h6, f"<{h5}")
    production_p = 4.0 + 1.0e-12
    six_row_coefficient = 3.0 / (40.0 * production_p)
    half_debt_5 = 0.5 * six_row_coefficient * h5
    half_debt_6 = 0.5 * six_row_coefficient * h6
    audit.check(
        "triangular",
        "C5 conditional half debt",
        close(half_debt_5, 0.5277951940233415, 2.0e-13),
        half_debt_5,
        0.5277951940233415,
    )
    audit.check(
        "triangular",
        "C6 conditional half debt",
        close(half_debt_6, 0.2325581069021709, 2.0e-13),
        half_debt_6,
        0.2325581069021709,
    )
    cross_values = {
        "primary H5": (float(primary_computed["hs_c5_components"]["total"]), h5),
        "independent H5": (float(independent_computed["triangular"]["5"]["closed"]), h5),
        "primary H6": (float(primary_computed["hs_c6_components"]["total"]), h6),
        "independent H6": (float(independent_computed["triangular"]["6"]["closed"]), h6),
        "primary C5 half debt": (
            float(primary_computed["lambda_c5_squared"]) / 2.0,
            half_debt_5,
        ),
        "independent C5 half debt": (
            float(independent_computed["action_half_debt"]["5"]),
            half_debt_5,
        ),
        "primary C6 half debt": (
            float(primary_computed["action_half_debt_c6"]),
            half_debt_6,
        ),
        "independent C6 half debt": (
            float(independent_computed["action_half_debt"]["6"]),
            half_debt_6,
        ),
    }
    for label, (actual, expected) in cross_values.items():
        audit.check(
            "cross",
            label,
            close(actual, expected, 2.0e-12),
            actual,
            expected,
        )

    # Positive-low direct/completed-square Feshbach fixture.  Here
    # Z=(1,2), Lambda=3, D=4, K^*Z=5 and <Z,M2 Z>=56.
    m2_value = Fraction(56)
    low_value = Fraction(3)
    d_value = Fraction(4)
    kz = Fraction(5)
    direct_positive = m2_value - 2 * kz * low_value + d_value * low_value**2
    w_value = kz / 2
    delta_value = 2 * low_value - w_value
    completed_positive = m2_value - w_value**2 + delta_value**2
    audit.check(
        "feshbach",
        "positive D direct value",
        direct_positive == 62,
        direct_positive,
        62,
    )
    audit.check(
        "feshbach",
        "positive D completed square value",
        completed_positive == direct_positive,
        completed_positive,
        direct_positive,
    )
    audit.check(
        "cross",
        "primary positive D fixture",
        Fraction(primary_computed["spd_feshbach_direct"]) == direct_positive,
        primary_computed["spd_feshbach_direct"],
        direct_positive,
    )
    audit.check(
        "cross",
        "independent positive D direct and reduced fixtures",
        Fraction(independent_computed["spd_direct"]) == direct_positive
        and Fraction(independent_computed["spd_reduced"]) == direct_positive,
        (independent_computed["spd_direct"], independent_computed["spd_reduced"]),
        (direct_positive, direct_positive),
    )

    # Semidefinite low block: the kernel cross is -2*3*5=-30.  Omitting it
    # changes the value from -15 to +15.
    semidefinite_without_kernel = Fraction(15)
    kernel_cross = -2 * Fraction(3) * Fraction(5)
    semidefinite_true = semidefinite_without_kernel + kernel_cross
    audit.check(
        "feshbach",
        "semidefinite fixture retains kernel cross",
        semidefinite_true == -15,
        semidefinite_true,
        -15,
    )
    audit.check(
        "feshbach",
        "omitted kernel cross gives wrong sign",
        semidefinite_without_kernel == 15 and semidefinite_true != semidefinite_without_kernel,
        (semidefinite_true, semidefinite_without_kernel),
        (-15, 15),
    )
    audit.check(
        "cross",
        "primary semidefinite fixture",
        Fraction(primary_computed["semidefinite_feshbach_direct"])
        == semidefinite_true
        and Fraction(primary_computed["semidefinite_kernel_defect"])
        == kernel_cross,
        (
            primary_computed["semidefinite_feshbach_direct"],
            primary_computed["semidefinite_kernel_defect"],
        ),
        (semidefinite_true, kernel_cross),
    )
    audit.check(
        "cross",
        "independent semidefinite fixture",
        Fraction(independent_computed["semidefinite_direct"])
        == semidefinite_true
        and Fraction(independent_computed["semidefinite_completed"])
        == semidefinite_true
        and Fraction(independent_computed["semidefinite_without_kernel_defect"])
        == semidefinite_without_kernel,
        (
            independent_computed["semidefinite_direct"],
            independent_computed["semidefinite_completed"],
            independent_computed["semidefinite_without_kernel_defect"],
        ),
        (semidefinite_true, semidefinite_true, semidefinite_without_kernel),
    )

    # Source-only gap and the pinned R-128/R-131 headroom diagnostics.
    ambient_shift_matrix_determinant = Fraction(1) * Fraction(6) - Fraction(3) ** 2
    audit.check(
        "source_gap",
        "source-only shift identity",
        4 * 1**2 + 9 * 2**2 - 6 * 1 * 2 == 3 * 1**2 + (3 * 2 - 1) ** 2,
        4 + 36 - 12,
        3 + 25,
    )
    audit.check(
        "source_gap",
        "ambient shift by source gap is indefinite",
        ambient_shift_matrix_determinant < 0,
        ambient_shift_matrix_determinant,
        "<0",
    )
    eta_h = 9.0 / 20.0 - 3.0 / (125.0 * production_p) - 1.0 / 880.0
    zeta_h = 27.0 / 200.0
    e_value = 2.0 * eta_h
    f_value = 2.0 * zeta_h
    k0 = 4.0 * math.sqrt(
        (197.0 / 440.0 - 3.0 / (125.0 * production_p)) * 3.0 / 25.0
    )
    mu_zero = e_value - k0 * k0 / (4.0 * f_value)
    discriminant = math.sqrt((e_value - f_value) ** 2 + k0 * k0)
    sigma_root = (e_value + f_value - discriminant) / 2.0
    sigma_test = sigma_root / 2.0
    tail_test = 0.02
    mu_test = e_value - sigma_test - (k0 + tail_test) ** 2 / (
        4.0 * (f_value - sigma_test)
    )
    audit.check(
        "source_gap",
        "zero-low-tail source gap",
        close(mu_zero, 0.10043434343434376, 2.0e-13),
        mu_zero,
        0.10043434343434376,
    )
    audit.check(
        "source_gap",
        "first low-loss root",
        close(sigma_root, 0.02396011633137274, 2.0e-12),
        sigma_root,
        0.02396011633137274,
    )
    audit.check(
        "source_gap",
        "half-loss tail diagnostic",
        close(mu_test, 0.015912689545308223, 2.0e-12),
        mu_test,
        0.015912689545308223,
    )
    audit.check(
        "source_gap",
        "diagnostic remains positive only conditionally",
        mu_test > 0.0 and mu_test < mu_zero,
        mu_test,
        f"between 0 and {mu_zero}",
    )
    child_gap_values = {
        "primary zero-low-tail ceiling": float(
            Fraction(primary_computed["zero_low_tail_lambda_squared_ceiling"])
        ),
        "independent zero-low-tail ceiling": float(
            independent_computed["conditional_parameters"]["mu0"]
        ),
        "primary low-loss root": float(primary_computed["sigma_ceiling"]),
        "independent low-loss root": float(
            independent_computed["conditional_parameters"]["sigma_ceiling"]
        ),
        "independent illustrative ceiling": float(
            independent_computed["conditional_parameters"]["example_mu"]
        ),
    }
    expected_gap_values = {
        "primary zero-low-tail ceiling": mu_zero,
        "independent zero-low-tail ceiling": mu_zero,
        "primary low-loss root": sigma_root,
        "independent low-loss root": sigma_root,
        "independent illustrative ceiling": mu_test,
    }
    for label, actual in child_gap_values.items():
        audit.check(
            "cross",
            label,
            close(actual, expected_gap_values[label], 2.0e-11),
            actual,
            expected_gap_values[label],
        )

    # Hostile fixture 1: an exact scale-local absolute envelope.  Take
    # sigma=2/3, C=6, d=3 and only r=3j.  Then m=3j+9 and the weight is
    # exactly 2^(4j+12), so the finite sum is an integer geometric series.
    hostile_levels = 7
    absolute_direct = sum(2 ** (4 * j + 12) for j in range(hostile_levels))
    absolute_closed = 2**12 * (16**hostile_levels - 1) // 15
    audit.check(
        "hostile_absolute",
        "exact absolute envelope geometric growth",
        absolute_direct == absolute_closed,
        absolute_direct,
        absolute_closed,
    )
    audit.check(
        "hostile_absolute",
        "absolute envelope is exponentially cutoff dependent",
        absolute_direct > hostile_levels * 2**12,
        absolute_direct,
        f">{hostile_levels * 2**12}",
    )
    scale_zero_injections = [Fraction(1) for _ in range(13)]
    primitive_trace_sum = 2 * sum(scale_zero_injections, Fraction(0))
    audit.check(
        "hostile_absolute",
        "R-067 R-125 scale-zero trace grows linearly before spatial weight",
        primitive_trace_sum == 26,
        primitive_trace_sum,
        26,
    )

    # Hostile fixture 2: exact stationary-subtracted signature polarization
    # followed by the two-weight Cauchy/parallelogram inequality.  The cell is
    # kept at d=3, so its physical reveal weight is exactly 2^(7/2).
    z_stationary = (Fraction(2), Fraction(-1))
    z_terminal = (Fraction(3), Fraction(4))
    z_prefix = (Fraction(-2), Fraction(1))
    full_terminal = add(z_stationary, z_terminal)
    full_prefix = add(z_stationary, z_prefix)
    secant = subtract(z_terminal, z_prefix)
    control_sum = add(z_terminal, z_prefix)
    signature_delta = signature(full_terminal) - signature(full_prefix)
    stationary_part = 2 * signature_pairing(z_stationary, secant)
    control_part = signature_pairing(control_sum, secant)
    audit.check(
        "hostile_signed",
        "stationary-subtracted polarization exact",
        signature_delta == stationary_part + control_part == 16,
        (signature_delta, stationary_part, control_part),
        (16, 26, -10),
    )
    rho_aux = Fraction(4)
    a_stationary = euclidean_square(z_stationary) / rho_aux
    a_secant = rho_aux * euclidean_square(secant)
    a_control = euclidean_square(z_terminal) + euclidean_square(z_prefix)
    bilinear_bound = 2.0 * math.sqrt(float(a_stationary * a_secant)) + float(a_control)
    audit.check(
        "hostile_signed",
        "stationary-subtracted bilinear inequality",
        float(signature_delta) <= bilinear_bound,
        float(signature_delta),
        f"<={bilinear_bound}",
    )
    reveal_exponent = 2 * gamma * 3
    reveal_weight = 2.0 ** float(reveal_exponent)
    audit.check(
        "hostile_signed",
        "d3 reveal exponent exact",
        reveal_exponent == Fraction(7, 2),
        reveal_exponent,
        Fraction(7, 2),
    )
    audit.check(
        "hostile_signed",
        "weight is exactly square root 128",
        close(reveal_weight, math.sqrt(128.0), 1.0e-15),
        reveal_weight,
        math.sqrt(128.0),
    )
    audit.check(
        "hostile_signed",
        "zero-control secant vanishes despite nonzero stationary envelope",
        signature(z_stationary) - signature(z_stationary) == 0
        and euclidean_square(z_stationary) > 0,
        (0, euclidean_square(z_stationary)),
        (0, ">0"),
    )

    # Hostile fixture 3: a genuine reveal filtration.  Conditional means are
    # evaluated by exact enumeration, correcting the degenerate P_r=P_{r-1}
    # fixture.  Each endpoint p(r) uses J=xi_r e_m and the terminal is zero.
    reveal_count = 5
    states = list(itertools.product((-1, 1), repeat=reveal_count))
    rademacher_d0_deltas: list[Fraction] = []
    for r in range(reveal_count):
        by_past: dict[tuple[int, ...], list[int]] = {}
        by_current: dict[tuple[int, ...], list[int]] = {}
        for state in states:
            by_past.setdefault(state[:r], []).append(state[r])
            by_current.setdefault(state[: r + 1], []).append(state[r])
        past_means = {
            key: Fraction(sum(values), len(values)) for key, values in by_past.items()
        }
        current_means = {
            key: Fraction(sum(values), len(values))
            for key, values in by_current.items()
        }
        audit.check(
            "hostile_rademacher",
            f"reveal {r} strict-past mean zero",
            all(value == 0 for value in past_means.values()),
            sorted(set(past_means.values())),
            [Fraction(0)],
        )
        audit.check(
            "hostile_rademacher",
            f"reveal {r} current projection is xi_r",
            all(current_means[state[: r + 1]] == state[r] for state in states),
            "all states",
            "P_r xi_r=xi_r",
        )
        conditional_y2: dict[tuple[int, ...], list[Fraction]] = {}
        for state in states:
            past_key = state[:r]
            current_key = state[: r + 1]
            innovation = current_means[current_key] - past_means[past_key]
            conditional_y2.setdefault(past_key, []).append(innovation**2)
        prefix_d0 = {
            key: -sum(values, Fraction(0)) / len(values)
            for key, values in conditional_y2.items()
        }
        audit.check(
            "hostile_rademacher",
            f"reveal {r} prefix D0 is minus one",
            all(value == -1 for value in prefix_d0.values()),
            sorted(set(prefix_d0.values())),
            [Fraction(-1)],
        )
        terminal_d0 = Fraction(0)
        rademacher_d0_deltas.append(
            terminal_d0 - next(iter(prefix_d0.values()))
        )
    weighted_rademacher = reveal_weight * float(sum(rademacher_d0_deltas))
    audit.check(
        "hostile_rademacher",
        "each terminal-minus-prefix D0 delta is one",
        rademacher_d0_deltas == [Fraction(1)] * reveal_count,
        rademacher_d0_deltas,
        [Fraction(1)] * reveal_count,
    )
    audit.check(
        "hostile_rademacher",
        "corrected reveal fixture has M times exact d3 weight",
        close(weighted_rademacher / reveal_weight, float(reveal_count), 1.0e-15),
        weighted_rademacher,
        f"{reveal_count}*2^(7/2)",
    )

    shared_scope = {
        "predictable_triangular_one_use_conditional": True,
        "scalar_triangular_majorant_exact": True,
        "predictable_stopping_identity": True,
        "source_graph_feshbach_exact": True,
        "absolute_envelope_production_infeasible": True,
        "stationary_subtracted_bilinear_repair": True,
        "production_mixed_gram_envelope": False,
        "positive_production_source_gap": False,
        "a13_gate_closed": False,
        "nelson": False,
        "sector_a_closed": False,
    }
    for name, child in (("primary", primary), ("independent", independent)):
        child_scope = child.get("scope", {})
        for key, expected in shared_scope.items():
            if key in child_scope:
                audit.check(
                    "scope",
                    f"{name} {key}",
                    child_scope[key] is expected,
                    child_scope[key],
                    expected,
                )
    negative_scope_aliases = {
        "production mixed Gram": (
            "production_mixed_gram_envelope",
            "production_predictable_mixed_gram_envelope",
            "production_mixed_gram_bound",
        ),
        "positive production source gap": (
            "positive_production_source_gap",
            "production_graph_margin",
            "production_low_tail_constants",
        ),
        "A13 gate": ("a13_gate_closed",),
        "Nelson": ("nelson",),
        "Sector A": ("sector_a_closed",),
    }
    for label, aliases in negative_scope_aliases.items():
        primary_values = [primary.get("scope", {}).get(key) for key in aliases if key in primary.get("scope", {})]
        independent_values = [independent.get("scope", {}).get(key) for key in aliases if key in independent.get("scope", {})]
        audit.check(
            "scope",
            f"both children expose honest negative scope for {label}",
            bool(primary_values)
            and bool(independent_values)
            and all(value is False for value in primary_values + independent_values),
            (primary_values, independent_values),
            (False, False),
        )

    imports, has_relative_import = imported_roots(INDEPENDENT)
    allowed_imports = set(getattr(sys, "stdlib_module_names", set())) | {"__future__"}
    audit.check(
        "independence",
        "independent AST imports standard library only",
        imports <= allowed_imports,
        sorted(imports - allowed_imports),
        [],
    )
    audit.check(
        "independence",
        "independent has no relative import",
        not has_relative_import,
        has_relative_import,
        False,
    )
    independent_source = INDEPENDENT.read_text(encoding="utf-8")
    audit.check(
        "independence",
        "independent does not import primary or local verifier",
        PRIMARY.stem not in independent_source
        and Path(__file__).stem not in independent_source
        and "codes.foundations" not in independent_source,
        "local import tokens absent",
        "absent",
    )
    audit.check(
        "independence",
        "primary and independent hashes differ",
        sha256(PRIMARY) != sha256(INDEPENDENT),
        (sha256(PRIMARY), sha256(INDEPENDENT)),
        "different",
    )

    audit.check(
        "document",
        "proof note exists",
        NOTE.is_file(),
        relative(NOTE),
        "file",
    )
    note_text = NOTE.read_text(encoding="utf-8")
    compact_note = "".join(note_text.split())
    note_tokens = {
        "result id": RESULT_ID,
        "ledger id": "Ledger ID: R-140",
        "triangular theorem": "The predictable triangular one-use theorem",
        "one Doob square": "This is the only Doob-square use",
        "exact H5": "H_5=",
        "strict source margin": "{7\\over60}",
        "strict output margin": "{1\\over12}",
        "whole-product firewall": "The R-102 whole-product firewall",
        "predictable stopping": "Predictable stopping preserves the endpoint telescope",
        "Feshbach theorem": "Theorem 7.1",
        "kernel cross": "kernel cross",
        "source-only gap": "Sharp scalar source-gap corollary",
        "absolute hostile audit": "Absolute-envelope hostile audit and signed repair",
        "production infeasible": "production-infeasible",
        "stationary subtraction": "stationary subtraction",
        "Rademacher correction": "Rademacher variables",
        "exact d3 weight": "2^{7/2}",
        "no overclaim": "No-overclaim statement",
    }
    for label, token in note_tokens.items():
        haystack = compact_note if label == "result id" else note_text
        needle = "".join(token.split()) if label == "result id" else token
        audit.check(
            "document",
            label,
            needle in haystack,
            needle in haystack,
            True,
        )
    audit.check(
        "document",
        "both open production gates stated",
        "production mixed-Gram" in note_text
        and "Sector-A closure" in note_text
        and "does not prove" in note_text,
        "open-scope tokens",
        "present",
    )

    first_build = build_pdf()
    audit.check(
        "pdf",
        "first deterministic build exits zero",
        first_build.returncode == 0,
        (first_build.returncode, first_build.stderr),
        0,
    )
    audit.check(
        "pdf",
        "first form check",
        "FORM-CHECK: PASS" in first_build.stdout,
        first_build.stdout,
        "FORM-CHECK: PASS",
    )
    audit.check(
        "pdf",
        "first zero overfull boxes",
        "OVERFULL-HBOX: 0" in first_build.stdout,
        first_build.stdout,
        "OVERFULL-HBOX: 0",
    )
    first_hash = sha256(PDF) if PDF.is_file() else "missing"
    second_build = build_pdf()
    audit.check(
        "pdf",
        "second deterministic build exits zero",
        second_build.returncode == 0,
        (second_build.returncode, second_build.stderr),
        0,
    )
    audit.check(
        "pdf",
        "second form check",
        "FORM-CHECK: PASS" in second_build.stdout,
        second_build.stdout,
        "FORM-CHECK: PASS",
    )
    audit.check(
        "pdf",
        "second zero overfull boxes",
        "OVERFULL-HBOX: 0" in second_build.stdout,
        second_build.stdout,
        "OVERFULL-HBOX: 0",
    )
    audit.check("pdf", "PDF exists", PDF.is_file(), relative(PDF), "file")
    second_hash = sha256(PDF)
    audit.check(
        "pdf",
        "deterministic rebuild hash",
        first_hash == second_hash,
        (first_hash, second_hash),
        "equal",
    )

    reader = PdfReader(str(PDF))
    audit.check("pdf", "not encrypted", reader.is_encrypted is False, reader.is_encrypted, False)
    page_count = len(reader.pages)
    audit.check("pdf", "positive page count", page_count > 0, page_count, ">0")
    extracted_pages = [(page.extract_text() or "") for page in reader.pages]
    audit.check(
        "pdf",
        "all pages text nonblank",
        all(len(text.strip()) >= 20 for text in extracted_pages),
        [len(text.strip()) for text in extracted_pages],
        ">=20 each",
    )
    extracted = "\n".join(extracted_pages)
    compact_extracted = "".join(extracted.split())
    audit.check(
        "pdf",
        "no replacement glyph",
        "\ufffd" not in extracted,
        "\ufffd" in extracted,
        False,
    )
    audit.check(
        "pdf",
        "result id extracts",
        RESULT_ID in compact_extracted,
        RESULT_ID in compact_extracted,
        True,
    )
    audit.check(
        "pdf", "ledger id extracts", LEDGER_ID in extracted, LEDGER_ID in extracted, True
    )
    audit.check(
        "pdf",
        "hostile audit extracts",
        "Absolute-envelope hostile audit" in extracted
        and "stationary" in extracted
        and "subtraction" in extracted
        and "Rademacher" in extracted,
        "hostile tokens",
        "present",
    )
    fields = reader.get_fields()
    audit.check("pdf", "no form fields", fields in (None, {}), fields, None)
    security = pdf_security_audit(reader)
    audit.check(
        "pdf",
        "no unsafe actions or embedded files",
        security["findings"] == [],
        security["findings"],
        [],
    )
    audit.check(
        "pdf",
        "safe open action",
        security["safe_open_action"] is True,
        security["open_action"],
        "absent, destination-array, or GoTo",
    )
    audit.check("pdf", "no widgets", security["widget_count"] == 0, security["widget_count"], 0)
    with tempfile.TemporaryDirectory(prefix="tect-r140-render-") as temporary_render:
        render_code, render_log, rendered_pages = render_pdf(Path(temporary_render))
        audit.check(
            "pdf",
            "Poppler render exits zero",
            render_code == 0,
            (render_code, render_log),
            0,
        )
        audit.check(
            "pdf",
            "rendered page count",
            len(rendered_pages) == page_count,
            len(rendered_pages),
            page_count,
        )
        audit.check(
            "pdf",
            "rendered images nonempty",
            all(path.stat().st_size > 0 for path in rendered_pages),
            [path.stat().st_size for path in rendered_pages],
            "positive each",
        )
        rendered_hashes = [sha256(path) for path in rendered_pages]

    pdf_audit = {
        "path": relative(PDF),
        "sha256": second_hash,
        "size_bytes": PDF.stat().st_size,
        "pages": page_count,
        "deterministic_rebuild": True,
        "form_check": True,
        "overfull_hbox_count": 0,
        "all_pages_nonblank": True,
        "replacement_glyph": False,
        "encrypted": False,
        "form_fields": 0,
        "security_findings": security["findings"],
        "open_action": security["open_action"],
        "widget_count": security["widget_count"],
        "renderer": "Poppler pdftoppm",
        "dpi": 130,
        "rendered_pages": page_count,
        "page_sha256": rendered_hashes,
    }

    exploration_records: list[dict[str, Any]] = []
    for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            exploration_records.append(json.loads(line))
    exploration_by_id = {record.get("id"): record for record in exploration_records}
    for exploration_id in EXPLORATION_IDS:
        audit.check(
            "exploration",
            f"{exploration_id} registered",
            exploration_id in exploration_by_id,
            exploration_id in exploration_by_id,
            True,
        )
    exploration_window = "\n".join(
        json.dumps(exploration_by_id[item], sort_keys=True)
        for item in EXPLORATION_IDS
        if item in exploration_by_id
    ).lower()
    for label, token in (
        ("triangular route", "triangular"),
        ("Feshbach route", "feshbach"),
        ("absolute envelope audit", "absolute"),
        ("stationary repair", "stationary"),
        ("Rademacher correction", "rademacher"),
    ):
        audit.check(
            "exploration",
            label,
            token in exploration_window,
            token in exploration_window,
            True,
        )

    public_checks = {
        "result ledger": (REPO / "RESULTS-LEDGER.md", '<a id="r-140"></a>'),
        "claim status": (CLAIM_DIR / "status.json", RESULT_ID),
        "claim chronology": (CLAIM_DIR / "claim.md", "R-140"),
        "lineage narrative": (CLAIM_DIR / "lineage-narrative.md", "R-140"),
        "theorem map": (REPO / "governance/sector-a-theorem-map.json", RESULT_ID),
        "task ledger": (REPO / "todo/todo.json", "R-140"),
        "changelog": (REPO / "CHANGELOG.md", "R-140"),
        "proof evidence map": (REPO / "theory/proof-evidence-map.md", "R-140"),
        "catalog": (REPO / "CATALOG.md", MANIFEST.name),
    }
    for name, (path, token) in public_checks.items():
        audit.check("surface", f"{name} exists", path.is_file(), relative(path), "file")
        surface_text = path.read_text(encoding="utf-8")
        audit.check("surface", name, token in surface_text, token in surface_text, True)

    authority_hashes: dict[str, str] = {}
    for ledger_id, (filename, expected_result_id) in AUTHORITIES.items():
        path = CLAIM_DIR / filename
        audit.check(
            "authority",
            f"{ledger_id} manifest exists",
            path.is_file(),
            relative(path),
            "file",
        )
        authority = load_json(path)
        audit.check(
            "authority",
            f"{ledger_id} result id",
            authority.get("result_id") == expected_result_id,
            authority.get("result_id"),
            expected_result_id,
        )
        audit.check(
            "authority",
            f"{ledger_id} claim id",
            authority.get("claim_id") == CLAIM,
            authority.get("claim_id"),
            CLAIM,
        )
        authority_hashes[ledger_id] = sha256(path)

    audit.check(
        "manifest", "R-140 manifest exists", MANIFEST.is_file(), relative(MANIFEST), "file"
    )
    manifest = load_json(MANIFEST)
    audit.check(
        "manifest",
        "schema",
        str(manifest.get("schema", "")).endswith("-manifest/1.0"),
        manifest.get("schema"),
        "*-manifest/1.0",
    )
    audit.check(
        "manifest", "claim id", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM
    )
    audit.check(
        "manifest",
        "result id",
        manifest.get("result_id") == RESULT_ID,
        manifest.get("result_id"),
        RESULT_ID,
    )
    manifest_ledger = manifest.get("result_ledger_id", manifest.get("ledger_id"))
    audit.check(
        "manifest", "ledger id", manifest_ledger == LEDGER_ID, manifest_ledger, LEDGER_ID
    )
    manifest_explorations = set(manifest.get("exploration_ids", []))
    audit.check(
        "manifest",
        "exploration ids",
        set(EXPLORATION_IDS) <= manifest_explorations,
        sorted(set(EXPLORATION_IDS) - manifest_explorations),
        [],
    )
    # Most manifests spell authority keys as r063; normalize separately.
    normalized_manifest_authorities = {
        f"R-{str(key).lower().removeprefix('r').removeprefix('-')}"
        for key in manifest.get("authority_keys", [])
    }
    normalized_manifest_authorities |= {
        f"R-{str(key).lower().removeprefix('r').removeprefix('-')}"
        for key in manifest.get("authorities", {})
    }
    audit.check(
        "manifest",
        "authority set",
        set(AUTHORITIES) <= normalized_manifest_authorities,
        sorted(set(AUTHORITIES) - normalized_manifest_authorities),
        [],
    )
    manifest_files = manifest.get("files", {})
    expected_file_paths = {
        "primary": relative(PRIMARY),
        "independent": relative(INDEPENDENT),
        "verifier": relative(Path(__file__)),
        "note": relative(NOTE),
        "pdf": relative(PDF),
    }
    for key, expected_path in expected_file_paths.items():
        entry = manifest_files.get(key, {})
        audit.check(
            "manifest",
            f"{key} path",
            str(entry.get("path", "")).replace("\\", "/")
            == expected_path.replace("\\", "/"),
            entry.get("path"),
            expected_path,
        )
        if entry.get("sha256"):
            audit.check(
                "manifest",
                f"{key} hash",
                entry["sha256"] == sha256(Path(REPO / entry["path"])),
                entry["sha256"],
                sha256(Path(REPO / entry["path"])),
            )
    manifest_verification = manifest.get("verification", {})
    audit.check(
        "manifest",
        "primary count follows child payload",
        int(manifest_verification.get("primary_assertions", child_counts["primary"]))
        == child_counts["primary"],
        manifest_verification.get("primary_assertions"),
        child_counts["primary"],
    )
    audit.check(
        "manifest",
        "independent count follows child payload",
        int(manifest_verification.get("independent_assertions", child_counts["independent"]))
        == child_counts["independent"],
        manifest_verification.get("independent_assertions"),
        child_counts["independent"],
    )
    aggregation_note = str(manifest_verification.get("aggregation_note", "")).lower()
    audit.check(
        "manifest",
        "aggregation forbids child double counting",
        "embed" in aggregation_note and ("not added" in aggregation_note or "not add" in aggregation_note or "once" in aggregation_note),
        aggregation_note,
        "children embedded once and not added again",
    )
    audit.check(
        "manifest",
        "no proof completion",
        manifest.get("proof_complete") is False
        and manifest.get("sector_a_closed") is False,
        (manifest.get("proof_complete"), manifest.get("sector_a_closed")),
        (False, False),
    )

    child_rows: list[dict[str, object]] = []
    seen_embedded_names: set[str] = set()
    duplicate_embedded_names: list[str] = []
    for child_name, child in (("primary", primary), ("independent", independent)):
        for row in assertion_rows(child):
            embedded_name = f"{child_name}:{row.get('group')}::{row.get('name')}"
            if embedded_name in seen_embedded_names:
                duplicate_embedded_names.append(embedded_name)
            seen_embedded_names.add(embedded_name)
            child_rows.append(
                {
                    "group": f"{child_name}:{row.get('group')}",
                    "name": row.get("name"),
                    "status": row.get("status"),
                    "actual": row.get("actual"),
                    "expected": row.get("expected"),
                }
            )

    audit.check(
        "aggregation",
        "embedded child rows have unique prefixed identities",
        duplicate_embedded_names == [],
        duplicate_embedded_names,
        [],
    )

    embedded_child_assertions = len(child_rows)
    integrator_only_assertions = len(audit.rows)
    all_rows = child_rows + audit.rows
    unique_package_assertions = len(all_rows)
    audit_failed = sum(row["status"] != "PASS" for row in all_rows)
    audit.check(
        "aggregation",
        "embedded count equals dynamic child totals",
        embedded_child_assertions == child_counts["primary"] + child_counts["independent"],
        embedded_child_assertions,
        child_counts["primary"] + child_counts["independent"],
    )
    # The preceding accounting check is itself integrator-only; refresh the
    # final counts after appending it and rebuild the aggregate row list.
    integrator_only_assertions = len(audit.rows)
    all_rows = child_rows + audit.rows
    unique_package_assertions = len(all_rows)
    failed = sum(row["status"] != "PASS" for row in all_rows)

    computed = {
        "beta_half_minus_gamma": str(margin_source),
        "s_minus_gamma": str(margin_output),
        "triangular_h5": h5,
        "triangular_h6": h6,
        "conditional_half_debt_c5": half_debt_5,
        "conditional_half_debt_c6": half_debt_6,
        "positive_d_direct": str(direct_positive),
        "positive_d_completed": str(completed_positive),
        "semidefinite_with_kernel_cross": str(semidefinite_true),
        "semidefinite_without_kernel_cross": str(semidefinite_without_kernel),
        "mu_source_zero_low_tail": mu_zero,
        "first_low_loss_root": sigma_root,
        "mu_source_half_loss_tail": mu_test,
        "absolute_envelope_exact_integer": absolute_direct,
        "stationary_polarization_delta": str(signature_delta),
        "stationary_polarization_linear": str(stationary_part),
        "stationary_polarization_control": str(control_part),
        "rademacher_weight_exponent": str(reveal_exponent),
        "rademacher_weighted_sum": weighted_rademacher,
    }
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "result_id": RESULT_ID,
        "status": "PASS" if failed == 0 else "FAIL",
        "assertions": {
            "total": unique_package_assertions,
            "passed": unique_package_assertions - failed,
            "failed": failed,
            "rows": all_rows,
        },
        "children": {
            "primary": {
                "path": relative(args.primary_output),
                "sha256": sha256(args.primary_output),
                "assertions": child_counts["primary"],
                "stdout": primary_stdout,
            },
            "independent": {
                "path": relative(args.independent_output),
                "sha256": sha256(args.independent_output),
                "assertions": child_counts["independent"],
                "stdout": independent_stdout,
            },
        },
        "authority_hashes": authority_hashes,
        "source_hashes": {
            "primary": sha256(PRIMARY),
            "independent": sha256(INDEPENDENT),
            "verifier": sha256(Path(__file__)),
        },
        "manifest_sha256": sha256(MANIFEST),
        "pdf_audit": pdf_audit,
        "computed": computed,
        "child_computed": {
            "primary": primary_computed,
            "independent": independent_computed,
        },
        "assertion_accounting": {
            "embedded_child_assertions": embedded_child_assertions,
            "integrator_only_assertions": integrator_only_assertions,
            "unique_package_assertions": unique_package_assertions,
        },
        "scope": {
            "children_pass": True,
            **shared_scope,
            "matching": False,
            "absolute_anchor": False,
            "overlap_src": False,
            "removals": False,
            "interacting_measure": False,
        },
    }
    atomic_json(args.output, payload)
    print(
        f"R-140 integrated {payload['status']}: "
        f"{unique_package_assertions-failed}/{unique_package_assertions}"
    )
    print(
        "embedded_child_assertions="
        f"{embedded_child_assertions}; integrator_only_assertions="
        f"{integrator_only_assertions}; unique_package_assertions="
        f"{unique_package_assertions}"
    )
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
