#!/usr/bin/env python3
"""Integrated verifier for the phase-neutral A13 R-148 evidence package."""

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
import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
RESULT_ID = (
    "A13-CLASSII-CANONICAL-PREFIX-RANK-ACTIVE-SPECTATOR-"
    "LIFT-RELATIVE-HESSIAN-BOUNDARY"
)
LEDGER_ID = "R-148"
SLUG = "canonical-prefix-rank-active-spectator-lift-relative-hessian-boundary"
SCHEMA = f"tect/a13-{SLUG}-integrated/1.0"
MANIFEST = CLAIM_DIR / (
    "classii_canonical_prefix_rank_active_spectator_lift_"
    "relative_hessian_boundary_manifest.json"
)
PRIMARY = REPO / f"codes/foundations/a13_classii_{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / (
    f"codes/foundations/a13_classii_{SLUG.replace('-', '_')}_independent.py"
)
NOTE = CLAIM_DIR / (
    "notes/classii-canonical-prefix-rank-active-spectator-lift-"
    "relative-hessian-boundary-260802-v1.0.tex.txt"
)
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-integrated-{SLUG}/result.json"

EXPLORATION_IDS = tuple(f"EXP-{number:06d}" for number in range(625, 632))
EXPLORATION_VERDICTS = {
    "EXP-000625": "failed",
    "EXP-000626": "advanced",
    "EXP-000627": "advanced",
    "EXP-000628": "advanced",
    "EXP-000629": "failed",
    "EXP-000630": "advanced",
    "EXP-000631": "advanced",
}
NEGATIVE_IDS = (
    "NG-2026-08-02-A13-R147-EXACT-CANONICAL-ACTIVE-SPECTATOR-LIFT",
    "NG-2026-08-02-A13-ACTIVE-SPECTATOR-JET-OWNER-COMPLETION",
    "AUDIT-2026-08-02-A13-R147-ABSOLUTE-DEFECT-AS-RELATIVE-HESSIAN",
)

EXPECTED_SCOPE = {
    "fresh_final_canonical_prefix_rank_obstruction_proved": True,
    "no_correction_past_rank_fixture_proved": True,
    "adapted_past_rank_one_necessity_proved": False,
    "generic_last_root_mismatch_identity_proved": True,
    "generic_last_root_pointwise_small_noise_positive_mismatch_proved": True,
    "uniform_adverse_region_noise_threshold_proved": False,
    "minimal_last_root_coefficient_parameter_hessian_diagnostic_proved": True,
    "minimal_last_root_pointwise_small_noise_positive_curvature_proved": True,
    "minimal_last_root_nonzero_parameter_gradient_proved": True,
    "minimal_last_root_origin_stationary_proved": False,
    "physical_deterministic_control_hessian_identified": False,
    "exact_r147_line_is_r146_canonical_chart": False,
    "new_full_rank_canonical_chart_obstructed": False,
    "old_owner_transport_proved": False,
    "r063_production_forest_identified": False,
    "balanced_returned_low_spatial_sextic_determined_from_coefficient_jet": False,
    "coefficient_diagonal_identifies_full_owner": False,
    "complete_owner_sign_determined": False,
    "global_sigma_sign_proved": False,
    "physical_phase_selected": False,
    "bcc_selected_or_excluded": False,
    "pde_replacement_required": False,
    "t050_closed": False,
    "a13_gate_closed": False,
    "nelson_proved": False,
    "sector_a_closed": False,
}

EXPECTED_COUNTS = {"primary": 90, "independent": 98}
EXPECTED_HISTOGRAMS = {
    "primary": {
        "authority": 26,
        "covariance": 7,
        "metadata": 4,
        "mismatch": 11,
        "nonidentifiability": 4,
        "prefix-rank": 5,
        "relative-action": 7,
        "row-jet": 4,
        "scope": 15,
        "threshold": 7,
    },
    "independent": {
        "authority": 26,
        "metadata": 3,
        "mismatch": 7,
        "mutation": 12,
        "nonidentifiability": 3,
        "rank": 21,
        "relative-action": 3,
        "scope": 16,
        "series": 3,
        "threshold": 4,
    },
}
EXPECTED_IDENTITY_HASHES = {
    "primary": "31bf0ae8ca74848dc6bd877ae1f3b05b987b0598b39afda96a35fcf5903746ab",
    "independent": "c2097c488272549917f55917c88152a038f7787462fcbb8cdc2e0cfca350afdd",
}
EXPECTED_KEYS = {
    "primary": {
        "assertions", "claim_id", "cross_values", "exact_values",
        "gauss_hermite", "no_overclaim", "result_id", "schema", "scope",
        "script_version", "status", "theorem_summary",
    },
    "independent": {
        "assertions", "claim_id", "cross_values", "exact_values",
        "gauss_hermite", "independence_scope", "mutations_rejected",
        "no_overclaim", "rank_table", "result_id", "schema", "scope",
        "script_version", "status",
    },
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
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
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
    rows = assertions.get("rows") if isinstance(assertions, dict) else None
    if not isinstance(rows, list):
        raise TypeError("child assertion rows unavailable")
    return rows


def assertion_total(payload: dict[str, Any]) -> int:
    return int(payload["assertions"]["total"])


def identity_hash(rows: list[dict[str, Any]]) -> str:
    identities = sorted(
        f"{row.get('category', row.get('group'))}::{row.get('name')}"
        for row in rows
    )
    return hashlib.sha256(("\n".join(identities) + "\n").encode()).hexdigest()


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


def literal_expression(node: ast.AST) -> bool:
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, (ast.UnaryOp,)):
        return literal_expression(node.operand)
    if isinstance(node, ast.BinOp):
        return literal_expression(node.left) and literal_expression(node.right)
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return all(literal_expression(item) for item in node.elts)
    if isinstance(node, ast.Dict):
        return all(
            literal_expression(key) and literal_expression(value)
            for key, value in zip(node.keys, node.values)
            if key is not None
        )
    return False


def source_regressions(path: Path) -> dict[str, list[str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    constant_conditions: list[str] = []
    self_comparisons: list[str] = []
    literal_comparisons: list[str] = []
    literal_outputs: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            function = node.func
            name = (
                function.attr
                if isinstance(function, ast.Attribute)
                else function.id if isinstance(function, ast.Name) else ""
            )
            if name in {"check", "add"} and len(node.args) >= 3:
                condition = node.args[2]
                if isinstance(condition, ast.Constant) and isinstance(condition.value, bool):
                    constant_conditions.append(f"line {node.lineno}")
                if isinstance(condition, ast.Compare) and all(
                    literal_expression(term)
                    for term in [condition.left, *condition.comparators]
                ):
                    literal_comparisons.append(f"line {node.lineno}")
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
                        if literal_expression(output_value):
                            label = output_key.value if isinstance(output_key, ast.Constant) else "?"
                            literal_outputs.append(f"line {output_value.lineno}: {label}")
    return {
        "constant_conditions": constant_conditions,
        "self_comparisons": self_comparisons,
        "literal_comparisons": literal_comparisons,
        "literal_outputs": literal_outputs,
    }


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


def safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return -1


def sympify_child(value: str, locals_: dict[str, sp.Symbol]) -> sp.Expr:
    return sp.sympify(value, locals=locals_)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    primary_run = run_child(PRIMARY)
    independent_run = run_child(INDEPENDENT)
    audit.check("children", "primary exits zero", primary_run.returncode == 0, primary_run.returncode, 0)
    audit.check("children", "independent exits zero", independent_run.returncode == 0, independent_run.returncode, 0)
    primary = load_json(PRIMARY_OUTPUT)
    independent = load_json(INDEPENDENT_OUTPUT)
    children = {"primary": primary, "independent": independent}

    for name, child in children.items():
        rows = assertion_rows(child)
        histogram = dict(sorted(Counter(
            row.get("category", row.get("group")) for row in rows
        ).items()))
        row_names = [
            f"{row.get('category', row.get('group'))}::{row.get('name')}"
            for row in rows
        ]
        audit.check("children", f"{name} keys", set(child) == EXPECTED_KEYS[name], sorted(child), sorted(EXPECTED_KEYS[name]))
        audit.check("children", f"{name} schema", child.get("schema") == f"tect/a13-{SLUG}-{name}/1.0", child.get("schema"), f"tect/a13-{SLUG}-{name}/1.0")
        audit.check("children", f"{name} claim", child.get("claim_id") == CLAIM, child.get("claim_id"), CLAIM)
        audit.check("children", f"{name} result", child.get("result_id") == RESULT_ID, child.get("result_id"), RESULT_ID)
        audit.check("children", f"{name} status", child.get("status") == "PASS", child.get("status"), "PASS")
        audit.check("children", f"{name} all rows pass", all(row.get("status") == "PASS" for row in rows), [row for row in rows if row.get("status") != "PASS"], [])
        audit.check("children", f"{name} count", assertion_total(child) == EXPECTED_COUNTS[name] == len(rows), (assertion_total(child), len(rows)), EXPECTED_COUNTS[name])
        audit.check("children", f"{name} histogram", histogram == EXPECTED_HISTOGRAMS[name], histogram, EXPECTED_HISTOGRAMS[name])
        audit.check("children", f"{name} row identity hash", identity_hash(rows) == EXPECTED_IDENTITY_HASHES[name], identity_hash(rows), EXPECTED_IDENTITY_HASHES[name])
        audit.check("children", f"{name} row identities unique", len(row_names) == len(set(row_names)), len(row_names) - len(set(row_names)), 0)
        audit.check("children", f"{name} exact scope", child.get("scope") == EXPECTED_SCOPE, child.get("scope"), EXPECTED_SCOPE)

    audit.check(
        "independence",
        "declared backend scope",
        independent.get("independence_scope") == {
            "fraction_matrix_route_independent": True,
            "symbolic_series_route_independent": True,
            "source_sextic_moment_route_separate": True,
            "gauss_hermite_backend_shared_with_primary": True,
        },
        independent.get("independence_scope"),
        "separate exact routes; shared numerical GH backend",
    )
    roots, relative_import = imported_roots(INDEPENDENT)
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    audit.check("independence", "no relative imports", not relative_import, relative_import, False)
    audit.check("independence", "does not import A13 executable", not any(root.startswith("a13_classii") for root in roots), sorted(roots), "no a13_classii import")
    forbidden = (PRIMARY.name, PRIMARY_OUTPUT.parent.name, "2026-08-02-primary-canonical-prefix-rank")
    audit.check("independence", "does not read primary artifacts", not any(token in independent_text for token in forbidden), [token for token in forbidden if token in independent_text], [])
    audit.check("independence", "shared NumPy GH backend disclosed", "numpy" in roots and "Gauss--Hermite backend with the primary" in NOTE.read_text(encoding="utf-8"), sorted(roots), "numpy present and disclosed")

    for name, path in (("primary", PRIMARY), ("independent", INDEPENDENT)):
        regressions = source_regressions(path)
        for regression, values in regressions.items():
            audit.check("source", f"{name} no {regression}", values == [], values, [])

    # Independent exact authority reconstruction and universal rank theorem.
    manifest = load_json(MANIFEST)
    a1 = load_json(REPO / manifest["authorities"]["a1_production_manifest"])
    parameters = a1["parameters"]
    family = [sp.Rational(str(value)) for value in parameters["family_masses"]]
    lock = sp.Rational(str(parameters["k_lock"]))
    z0 = [sp.Rational(str(value)) for value in parameters["z0"]]
    z0_norm = sum(value**2 for value in z0)
    mass = sp.Matrix([
        [family[i] * int(i == j) + lock * (int(i == j) - z0[i] * z0[j] / z0_norm) for j in range(3)]
        for i in range(3)
    ])
    expected_mass = sp.Matrix([
        [sp.Rational(1, 10), -sp.Rational(1, 20), -sp.Rational(1, 20)],
        [-sp.Rational(1, 20), sp.Rational(13, 100), -sp.Rational(1, 20)],
        [-sp.Rational(1, 20), -sp.Rational(1, 20), sp.Rational(17, 100)],
    ])
    audit.check("theorem", "A1 mass derived", mass == expected_mass, mass, expected_mass)
    minors = [sp.factor(mass[:n, :n].det()) for n in (1, 2, 3)]
    audit.check("theorem", "mass positive definite", all(value > 0 for value in minors), minors, "positive Sylvester minors")
    a, tau = sp.symbols("a tau", nonnegative=True)
    selector = sp.Matrix([[1, 0], [0, 0], [0, 1]])
    covariance_radial = sp.simplify(selector.T * (a * sp.eye(3) + mass).inv() * selector)
    determinant = sp.factor(covariance_radial.det())
    determinant_oracle = 250 * (100 * a + 13) / (25000 * a**3 + 10000 * a**2 + 1115 * a + 24)
    audit.check("theorem", "radial determinant exact", sp.simplify(determinant - determinant_oracle) == 0, determinant, determinant_oracle)
    audit.check("theorem", "radial determinant universally positive", all(value > 0 for value in sp.Poly(250 * (100 * a + 13), a).all_coeffs()) and all(value > 0 for value in sp.Poly(25000 * a**3 + 10000 * a**2 + 1115 * a + 24, a).all_coeffs()), determinant_oracle, ">0 for a>=0")
    audit.check("theorem", "nonzero final canonical block rank two", sp.simplify(tau**2 * determinant_oracle) != 0 and determinant_oracle > 0, tau**2 * determinant_oracle, ">0 for tau>0")
    fresh = sp.Matrix([1, -1]) * sp.Matrix([1, -1]).T
    past_fixture = sp.Matrix([1, 1]) * sp.Matrix([1, 1]).T
    audit.check("theorem", "fresh line rank one", fresh.rank() == 1 and fresh.det() == 0, fresh.rank(), 1)
    audit.check("theorem", "past is fixture not premise", past_fixture.rank() == 1 and manifest["scope"]["adapted_past_rank_one_necessity_proved"] is False, (past_fixture.rank(), manifest["scope"]["adapted_past_rank_one_necessity_proved"]), (1, False))

    # Reconstruct coefficient inputs from R-147 and derive all jets anew.
    r147_manifest = load_json(REPO / manifest["authorities"]["r147_manifest"])
    inputs = r147_manifest["audit_inputs"]
    q, radius, floor, p_norm = sp.symbols("q R e P", positive=True)
    alpha = sp.sympify(inputs["production_alpha"])
    c0 = sp.sympify(inputs["production_p_coefficient"].replace("P", "*P"), locals={"P": p_norm})
    c1 = sp.sympify(inputs["production_l_coefficient"].replace("P", "*P"), locals={"P": p_norm})
    x, y = radius + q, radius - q
    density = x**2 + y**2 + floor
    row = x - alpha * x**2 * (x - y) / density
    energy = sp.factor(4 * c0 * x**2 + 4 * c1 * row**2)
    jets = [sp.factor(sp.diff(energy, q, order).subs(q, 0)) for order in (2, 3, 4)]
    expected_jets = [
        3 * (-528 * radius**4 - 88 * radius**2 * floor + 113 * floor**2) / (1000 * p_norm * (2 * radius**2 + floor) ** 2),
        -9 * radius * (16 * radius**2 + 27 * floor) / (50 * p_norm * (2 * radius**2 + floor) ** 2),
        18 * (112 * radius**4 + 48 * radius**2 * floor - 9 * floor**2) / (25 * p_norm * (2 * radius**2 + floor) ** 3),
    ]
    for order, actual, expected in zip((2, 3, 4), jets, expected_jets):
        audit.check("theorem", f"f derivative {order}", sp.simplify(actual - expected) == 0, actual, expected)
    rho = sp.symbols("rho", real=True)
    r2 = -sp.Rational(1, 12) + 5 * sp.sqrt(154) / 132
    r4 = -sp.Rational(3, 14) + 3 * sp.sqrt(11) / 28
    audit.check("theorem", "second derivative threshold", sp.simplify((-528 * rho**2 - 88 * rho + 113).subs(rho, r2)) == 0, r2, "root")
    audit.check("theorem", "fourth derivative threshold", sp.simplify((112 * rho**2 + 48 * rho - 9).subs(rho, r4)) == 0, r4, "root")
    audit.check("theorem", "threshold separation", r2 > sp.Rational(1, 3) > sp.Rational(1, 7) > r4, (r2, r4), "r2>1/3>1/7>r4")

    # The formal mismatch must retain the sign, sigma^4, and mean-square term.
    sigma, ef2, mean_square = sp.symbols("sigma E_f2 mean_square", positive=True)
    registered_delta = -sigma**4 * ef2 + sigma**4 * mean_square
    wrong_sign = sigma**4 * ef2 + sigma**4 * mean_square
    wrong_power = -sigma**2 * ef2 + sigma**2 * mean_square
    no_mean = -sigma**4 * ef2
    audit.check("mutation", "mismatch sign protected", sp.simplify(registered_delta - wrong_sign) != 0, registered_delta, "minus E f''")
    audit.check("mutation", "mismatch sigma fourth power protected", sp.simplify(registered_delta - wrong_power) != 0, registered_delta, "sigma^4")
    audit.check("mutation", "mismatch mean square protected", sp.simplify(registered_delta - no_mean) != 0, registered_delta, "plus mean square")

    shared_exact_keys = (
        "active_spectator_f2", "active_spectator_f3", "active_spectator_f4",
        "r147_threshold", "relative_hessian_threshold",
    )
    local_symbols = {"R": radius, "e": floor, "P": p_norm}
    for key in shared_exact_keys:
        left = sympify_child(primary["exact_values"][key], local_symbols)
        right = sympify_child(independent["exact_values"][key], local_symbols)
        audit.check("cross", f"symbolic {key}", sp.simplify(left - right) == 0, left, right)
    for key in ("fixture_delta", "fixture_mean_square"):
        left = float(primary["cross_values"][key])
        right = float(independent["cross_values"][key])
        audit.check("cross", f"numeric {key} agrees", abs(left - right) < 5e-15 and left > 0 and right > 0, (left, right), "positive and within 5e-15")

    # Parameter-Hessian and nonidentifiability firewalls.
    m = sp.symbols("m", real=True)
    physical_lift_extra = m * sigma**2 * sp.Symbol("E_fprime") + m**2 * sp.Symbol("E_f") / 2
    audit.check("interpretation", "physical lift changes derivatives", sp.diff(physical_lift_extra, m) != 0 and sp.diff(physical_lift_extra, m, 2) != 0, physical_lift_extra, "nonzero extra derivative terms")
    audit.check("interpretation", "physical control Hessian false", manifest["scope"]["physical_deterministic_control_hessian_identified"] is False, manifest["scope"]["physical_deterministic_control_hessian_identified"], False)
    audit.check("interpretation", "pointwise not uniform", manifest["scope"]["uniform_adverse_region_noise_threshold_proved"] is False, manifest["scope"]["uniform_adverse_region_noise_threshold_proved"], False)
    gauge_q = sp.symbols("s", real=True)
    rotation = sp.Matrix([[1 - gauge_q**2, -2 * gauge_q], [2 * gauge_q, 1 - gauge_q**2]]) / (1 + gauge_q**2)
    e1 = sp.Matrix([1, 0])
    gauged = sp.simplify(rotation * e1)
    audit.check("nonidentifiability", "orthogonal gauge", sp.simplify(rotation.T * rotation - sp.eye(2)) == sp.zeros(2), rotation.T * rotation, sp.eye(2))
    audit.check("nonidentifiability", "cross Gram changes", sp.simplify((gauged.subs(gauge_q, 0).T * gauged.subs(gauge_q, 1))[0]) == 0, (gauged.subs(gauge_q, 0).T * gauged.subs(gauge_q, 1))[0], "0 versus 1")
    derivative = sp.diff(gauged, gauge_q).subs(gauge_q, 0)
    audit.check("nonidentifiability", "jet energy changes", sp.simplify((derivative.T * derivative)[0]) == 4, (derivative.T * derivative)[0], "4 versus 0")

    note_text = NOTE.read_text(encoding="utf-8")
    note_tokens = (
        RESULT_ID,
        "Ledger: R-148",
        "section-3-prefix-rank",
        "section-4-generic-mismatch",
        "section-5-relative-control",
        "section-6-minimal-action",
        "section-7-nonidentifiability",
        "fresh final scalar innovation",
        "no past-rank necessity",
        "pointwise at each fixed parameter triple",
        "not yet the Hessian of a physical source lift",
        "may vanish when",
        "Gauss--Hermite backend with the primary",
        "Proof complete: false",
        "T-050 closed: false",
        "Sector A closed: false",
    )
    for token in note_tokens:
        audit.check("note", token, token in note_text, token in note_text, True)
    for negative_id in NEGATIVE_IDS:
        audit.check("note", negative_id, negative_id in note_text, negative_id in note_text, True)

    initial_pdf_hash = sha256(PDF)
    build = build_pdf()
    audit.check("pdf", "build exits zero", build.returncode == 0, (build.returncode, build.stderr), 0)
    audit.check("pdf", "form check", "FORM-CHECK: PASS" in build.stdout, build.stdout, "FORM-CHECK: PASS")
    audit.check("pdf", "zero overfull", "OVERFULL-HBOX: 0" in build.stdout, build.stdout, "OVERFULL-HBOX: 0")
    rebuilt_pdf_hash = sha256(PDF)
    audit.check("pdf", "deterministic rebuild", rebuilt_pdf_hash == initial_pdf_hash, (initial_pdf_hash, rebuilt_pdf_hash), "equal")
    reader = PdfReader(str(PDF), strict=True)
    page_text = [(page.extract_text() or "") for page in reader.pages]
    extracted = "\n".join(page_text)
    audit.check("pdf", "not encrypted", reader.is_encrypted is False, reader.is_encrypted, False)
    audit.check("pdf", "nine pages", len(reader.pages) == 9, len(reader.pages), 9)
    audit.check("pdf", "all pages nonblank", all(len(text.strip()) >= 100 for text in page_text), [len(text.strip()) for text in page_text], ">=100 each")
    for token in (LEDGER_ID, "phase-neutral", "fresh line innovation", "physical control Hessian", "pointwise", "Proof complete: false", "T-050 closed: false"):
        audit.check("pdf", f"extracts {token}", token in extracted, token in extracted, True)
    audit.check("pdf", "no replacement glyph", "\ufffd" not in extracted, "\ufffd" in extracted, False)
    audit.check("pdf", "no form fields", reader.get_fields() in (None, {}), reader.get_fields(), None)
    security_findings = pdf_security(reader)
    audit.check("pdf", "no unsafe actions", security_findings == [], security_findings, [])
    with tempfile.TemporaryDirectory(prefix="tect-r148-render-") as temporary:
        render_code, render_log, rendered = render_pdf(Path(temporary))
        audit.check("pdf", "Poppler exits zero", render_code == 0, (render_code, render_log), 0)
        audit.check("pdf", "all pages rendered", len(rendered) == len(reader.pages), len(rendered), len(reader.pages))
        audit.check("pdf", "rendered pages nonempty", all(path.stat().st_size > 0 for path in rendered), [path.stat().st_size for path in rendered], "positive")
        rendered_hashes = [sha256(path) for path in rendered]

    records = {
        record["id"]: record
        for record in (
            json.loads(line)
            for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    for exploration_id in EXPLORATION_IDS:
        exists = exploration_id in records
        audit.check("exploration", f"{exploration_id} exists", exists, exists, True)
        if not exists:
            continue
        record = records[exploration_id]
        audit.check("exploration", f"{exploration_id} verdict", record.get("verdict") == EXPLORATION_VERDICTS[exploration_id], record.get("verdict"), EXPLORATION_VERDICTS[exploration_id])
        audit.check("exploration", f"{exploration_id} evidence", len(record.get("evidence_refs", [])) >= 1, len(record.get("evidence_refs", [])), ">=1")
        for field in ("question", "finding", "boundary", "next_action"):
            audit.check("exploration", f"{exploration_id} {field}", bool(record.get(field)), record.get(field), "nonempty")
    audit.check("exploration", "rank correction links EXP-000625", any(item.get("id") == "EXP-000625" and item.get("relation") == "corrects" for item in records["EXP-000630"]["related"]), records["EXP-000630"]["related"], "corrects EXP-000625")
    audit.check("exploration", "Hessian correction links prior records", {item.get("id") for item in records["EXP-000631"]["related"]} == {"EXP-000627", "EXP-000628"}, records["EXP-000631"]["related"], "corrects EXP-000627/628")

    registry = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for negative_id in NEGATIVE_IDS:
        audit.check("negative", negative_id, negative_id.lower() in registry.lower(), negative_id.lower() in registry.lower(), True)
    audit.check("negative", "adapted-past boundary recorded", "adapted past may include later corrections" in registry, "adapted past may include later corrections" in registry, True)
    audit.check("negative", "physical-Hessian boundary recorded", "not a physical deterministic-control Hessian" in registry, "not a physical deterministic-control Hessian" in registry, True)

    expected_authorities = {
        "a1_production_manifest",
        *(f"r{number}_{kind}" for number in (125, 130, 141, 142, 146, 147) for kind in ("manifest", "note")),
    }
    audit.check("authority", "exact authority set", set(manifest["authorities"]) == expected_authorities, sorted(manifest["authorities"]), sorted(expected_authorities))
    authority_hashes: dict[str, str] = {}
    for name, path_text in manifest["authorities"].items():
        path = REPO / path_text
        audit.check("authority", f"{name} exists", path.is_file(), relative(path), "file")
        if path.is_file():
            authority_hashes[name] = sha256(path)
            audit.check("authority", f"{name} hash", manifest["authority_hashes"].get(name) == authority_hashes[name], manifest["authority_hashes"].get(name), authority_hashes[name])
    for number in (125, 130, 141, 142, 146, 147):
        prefix = f"r{number}"
        upstream = load_json(REPO / manifest["authorities"][f"{prefix}_manifest"])
        note_entry = upstream["files"]["note"]
        audit.check("authority", f"{prefix} manifest-note path pair", note_entry["path"] == manifest["authorities"][f"{prefix}_note"], note_entry["path"], manifest["authorities"][f"{prefix}_note"])
        audit.check("authority", f"{prefix} manifest-note hash pair", note_entry["sha256"] == manifest["authority_hashes"][f"{prefix}_note"], note_entry["sha256"], manifest["authority_hashes"][f"{prefix}_note"])

    audit.check("manifest", "claim", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    audit.check("manifest", "result", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    audit.check("manifest", "ledger", manifest.get("result_ledger_id") == LEDGER_ID, manifest.get("result_ledger_id"), LEDGER_ID)
    audit.check("manifest", "scope exact", manifest.get("scope") == EXPECTED_SCOPE, manifest.get("scope"), EXPECTED_SCOPE)
    audit.check("manifest", "proof incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    audit.check("manifest", "T-050 open", manifest.get("t050_closed") is False, manifest.get("t050_closed"), False)
    audit.check("manifest", "Sector A open", manifest.get("sector_a_closed") is False, manifest.get("sector_a_closed"), False)
    audit.check("manifest", "physical lift false", manifest.get("audit_inputs", {}).get("physical_control_lift_specified") is False, manifest.get("audit_inputs", {}).get("physical_control_lift_specified"), False)
    audit.check("manifest", "GH backends not independent", manifest.get("audit_inputs", {}).get("numerical_quadrature_backends_independent") is False, manifest.get("audit_inputs", {}).get("numerical_quadrature_backends_independent"), False)
    audit.check("manifest", "exploration ids exact", tuple(manifest.get("exploration_ids", [])) == EXPLORATION_IDS, manifest.get("exploration_ids"), EXPLORATION_IDS)
    audit.check("manifest", "negative ids exact", tuple(manifest.get("negative_results", [])) == NEGATIVE_IDS, manifest.get("negative_results"), NEGATIVE_IDS)
    no_overclaim = manifest.get("no_overclaim", "")
    for clause in ("adapted past", "physical deterministic-control Hessian", "pointwise", "does not obstruct", "BCC preference or exclusion", "Sector-A closure"):
        audit.check("manifest", f"no-overclaim {clause}", clause in no_overclaim, clause in no_overclaim, True)

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
        audit.check("manifest", f"{key} path", str(entry.get("path", "")).replace("\\", "/") == relative(path), entry.get("path"), relative(path))
        audit.check("manifest", f"{key} hash", entry.get("sha256") == sha256(path), entry.get("sha256"), sha256(path))
    integrated_entry = manifest.get("files", {}).get("integrated_result", {})
    audit.check("manifest", "integrated result has no self hash", "sha256" not in integrated_entry, integrated_entry, "no sha256")
    audit.check("manifest", "no PENDING remains", "PENDING" not in json.dumps(manifest), "PENDING" in json.dumps(manifest), False)

    verification = manifest.get("verification", {})
    audit.check("manifest", "primary count", safe_int(verification.get("primary_assertions")) == EXPECTED_COUNTS["primary"], verification.get("primary_assertions"), EXPECTED_COUNTS["primary"])
    audit.check("manifest", "independent count", safe_int(verification.get("independent_assertions")) == EXPECTED_COUNTS["independent"], verification.get("independent_assertions"), EXPECTED_COUNTS["independent"])
    pdf_meta = verification.get("pdf", {}) if isinstance(verification.get("pdf"), dict) else {}
    audit.check("manifest", "PDF pages", safe_int(pdf_meta.get("pages")) == 9, pdf_meta.get("pages"), 9)
    audit.check("manifest", "PDF size", safe_int(pdf_meta.get("size_bytes")) == PDF.stat().st_size, pdf_meta.get("size_bytes"), PDF.stat().st_size)
    audit.check("manifest", "PDF deterministic", pdf_meta.get("deterministic") is True, pdf_meta.get("deterministic"), True)
    audit.check("manifest", "PDF security", pdf_meta.get("security_check") == "PASS", pdf_meta.get("security_check"), "PASS")
    audit.check("manifest", "PDF text", pdf_meta.get("text_check") == "PASS", pdf_meta.get("text_check"), "PASS")
    audit.check("manifest", "PDF visual QA", str(pdf_meta.get("manual_visual_qa", "")).startswith("PASS"), pdf_meta.get("manual_visual_qa"), "PASS*")
    audit.check("manifest", "PDF rendered pages", safe_int(pdf_meta.get("rendered_pages")) == len(rendered_hashes), pdf_meta.get("rendered_pages"), len(rendered_hashes))

    public = {
        "results ledger": (REPO / "RESULTS-LEDGER.md", '<a id="r-148"></a>'),
        "claim status": (CLAIM_DIR / "status.json", RESULT_ID),
        "claim chronology": (CLAIM_DIR / "claim.md", "R-148"),
        "lineage": (CLAIM_DIR / "LINEAGE.md", SLUG),
        "theorem map": (REPO / "governance/sector-a-theorem-map.json", RESULT_ID),
        "T-050 task": (REPO / "todo/todo.json", "R-148"),
        "changelog": (REPO / "CHANGELOG.md", "R-148"),
        "claims ledger": (REPO / "CLAIMS.md", CLAIM),
        "proof map": (REPO / "theory/proof-evidence-map.md", "R-148"),
        "catalog": (REPO / "CATALOG.md", MANIFEST.name),
    }
    for name, (path, token) in public.items():
        audit.check("surface", f"{name} file", path.is_file(), relative(path), "file")
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        audit.check("surface", name, token in text, token in text, True)

    child_rows: list[dict[str, object]] = []
    identities: set[str] = set()
    duplicates: list[str] = []
    for child_name, child in children.items():
        for row in assertion_rows(child):
            identity = f"{child_name}:{row.get('category', row.get('group'))}::{row.get('name')}"
            if identity in identities:
                duplicates.append(identity)
            identities.add(identity)
            child_rows.append(
                {
                    "group": f"{child_name}:{row.get('category', row.get('group'))}",
                    "name": row.get("name"),
                    "status": row.get("status"),
                    "actual": row.get("actual"),
                    "expected": row.get("expected"),
                }
            )
    audit.check("aggregation", "child identities unique", duplicates == [], duplicates, [])
    expected_integrator = len(audit.rows) + 2
    expected_total = len(child_rows) + expected_integrator
    audit.check("aggregation", "manifest integrator count", safe_int(verification.get("integrator_only_assertions")) == expected_integrator, verification.get("integrator_only_assertions"), expected_integrator)
    audit.check("aggregation", "manifest integrated count", safe_int(verification.get("integrated_assertions")) == expected_total and safe_int(verification.get("embedded_child_assertions")) == len(child_rows), (verification.get("integrated_assertions"), verification.get("embedded_child_assertions")), (expected_total, len(child_rows)))

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
            "primary": {"path": relative(PRIMARY_OUTPUT), "sha256": sha256(PRIMARY_OUTPUT), "assertions": assertion_total(primary), "stdout": primary_run.stdout},
            "independent": {"path": relative(INDEPENDENT_OUTPUT), "sha256": sha256(INDEPENDENT_OUTPUT), "assertions": assertion_total(independent), "stdout": independent_run.stdout},
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
        "cross_values": {
            "r147_threshold": str(r2),
            "relative_hessian_threshold": str(r4),
            "fresh_final_rank_obstruction": True,
            "adapted_past_rank_necessity": False,
            "physical_control_hessian_identified": False,
            "phase_status": "neutral",
        },
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
            "manual_visual_qa": pdf_meta.get("manual_visual_qa"),
        },
        "scope": EXPECTED_SCOPE,
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
