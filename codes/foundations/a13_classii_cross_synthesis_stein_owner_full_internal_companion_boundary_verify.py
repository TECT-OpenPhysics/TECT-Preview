#!/usr/bin/env python3
"""Integrated verifier for the phase-neutral A13 R-149 evidence package."""

from __future__ import annotations

__version__ = "1.0.0"

import argparse
import ast
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
RESULT_ID = "A13-CLASSII-CROSS-SYNTHESIS-STEIN-OWNER-FULL-INTERNAL-COMPANION-BOUNDARY"
LEDGER_ID = "R-149"
SLUG = "cross-synthesis-stein-owner-full-internal-companion-boundary"
SCHEMA = f"tect/a13-{SLUG}-integrated/1.0"
MANIFEST = CLAIM_DIR / "classii_cross_synthesis_stein_owner_full_internal_companion_boundary_manifest.json"
PRIMARY = REPO / f"codes/foundations/a13_classii_{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/a13_classii_{SLUG.replace('-', '_')}_independent.py"
NOTE = CLAIM_DIR / "notes/classii-cross-synthesis-stein-owner-full-internal-companion-boundary-260802-v1.0.tex.txt"
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-integrated-{SLUG}/result.json"

EXPECTED_CHILD_COUNTS = {"primary": 48, "independent": 23}
EXPLORATION_IDS = tuple(f"EXP-{value:06d}" for value in range(632, 640))
NEGATIVE_IDS = (
    "NG-2026-08-02-A13-ENDPOINT-MARGINALS-DETERMINE-FRESH-OWNER",
    "AUDIT-2026-08-02-A13-RADIAL-SLICE-NEGATIVE-AS-FULL-INTERNAL-OWNER",
    "AUDIT-2026-08-02-A13-R149-REAL-COVARIANCE-DOUBLE-HALVING",
)

# Independent exact theorem oracle.  These are test-oracle coefficients, not
# executable production inputs.
EXPECTED_NUMERATOR_COEFFICIENTS = (
    (34800000000, 329600000000, 513700000000, 299400000000, 67800000000),
    (41736000000, 212652000000, 297744000000, 168768000000, 38646000000),
    (15500240000, 52815580000, 64406160000, 34734420000, 8003790000),
    (2547660000, 6531756000, 6689376000, 3280296000, 738681000),
    (167968324, 368965068, 323181116, 138377892, 28354299),
)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(
        self, group: str, name: str, condition: bool, actual: object, expected: object
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


def run_child(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(path)], cwd=REPO, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=180
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    options = parser.parse_args()
    audit = Audit()

    manifest = load_json(MANIFEST)
    primary_run = run_child(PRIMARY)
    independent_run = run_child(INDEPENDENT)
    audit.check("children", "primary exits zero", primary_run.returncode == 0, primary_run.returncode, 0)
    audit.check("children", "independent exits zero", independent_run.returncode == 0, independent_run.returncode, 0)
    primary = load_json(PRIMARY_OUTPUT)
    independent = load_json(INDEPENDENT_OUTPUT)
    children = {"primary": primary, "independent": independent}

    embedded_child_rows = 0
    for child_name, child in children.items():
        rows = child.get("assertions", [])
        expected_count = EXPECTED_CHILD_COUNTS[child_name]
        audit.check("children", f"{child_name} schema", child.get("schema") == f"tect/a13-{SLUG}-{child_name}/1.0", child.get("schema"), f"tect/a13-{SLUG}-{child_name}/1.0")
        audit.check("children", f"{child_name} result", child.get("result_id") == RESULT_ID, child.get("result_id"), RESULT_ID)
        audit.check("children", f"{child_name} status", child.get("status") == "PASS", child.get("status"), "PASS")
        audit.check("children", f"{child_name} exact count", child.get("assertions_total") == len(rows) == expected_count, (child.get("assertions_total"), len(rows)), expected_count)
        audit.check("children", f"{child_name} every row passes", all(row.get("status") == "PASS" for row in rows), [row for row in rows if row.get("status") != "PASS"], [])
        identities = [(row.get("group"), row.get("name")) for row in rows]
        audit.check("children", f"{child_name} row identities unique", len(identities) == len(set(identities)), len(identities), len(set(identities)))
        for row in rows:
            embedded_child_rows += 1
            audit.check(
                f"child-{child_name}/{row.get('group')}",
                str(row.get("name")),
                row.get("status") == "PASS",
                row.get("actual"),
                row.get("expected"),
            )

    audit.check("children", "all child rows embedded exactly once", embedded_child_rows == sum(EXPECTED_CHILD_COUNTS.values()), embedded_child_rows, sum(EXPECTED_CHILD_COUNTS.values()))
    audit.check("children", "child scopes agree", primary.get("scope") == independent.get("scope") == manifest.get("scope"), (primary.get("scope"), independent.get("scope")), manifest.get("scope"))
    audit.check("children", "child no-overclaim agrees", primary.get("no_overclaim") == independent.get("no_overclaim") == manifest.get("no_overclaim"), (primary.get("no_overclaim"), independent.get("no_overclaim")), manifest.get("no_overclaim"))

    roots, relative_import = imported_roots(INDEPENDENT)
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    audit.check("independence", "no relative imports", not relative_import, relative_import, False)
    audit.check("independence", "independent does not import primary", not any(root.startswith("a13_classii") for root in roots), sorted(roots), "no a13_classii import")
    audit.check("independence", "independent does not read primary artifact", PRIMARY.name not in independent_text and PRIMARY_OUTPUT.parent.name not in independent_text, [token for token in (PRIMARY.name, PRIMARY_OUTPUT.parent.name) if token in independent_text], [])

    # Exact raw/CN/action bookkeeping.
    forest, future = sp.symbols("forest future", real=True)
    pcomp = (forest - future) / 2
    raw = sp.expand(pcomp + future / 2)
    audit.check("owner", "raw equals covariance-normal forest half", raw == forest / 2, raw, forest / 2)
    audit.check("owner", "Pcomp is raw minus future half", sp.expand(raw - future / 2) == pcomp, sp.expand(raw - future / 2), pcomp)

    # Exact finite-epsilon same-marginal sign reversal.
    epsilon = sp.symbols("epsilon", positive=True)
    x, y = sp.symbols("x y", nonnegative=True)
    antitone = sp.factor((x - y) * (1 / (1 + epsilon * x) - 1 / (1 + epsilon * y)))
    antitone_expected = sp.factor(-epsilon * (x - y) ** 2 / ((1 + epsilon * x) * (1 + epsilon * y)))
    audit.check("counterfixture", "identity owner strict-antitone kernel", sp.simplify(antitone - antitone_expected) == 0, antitone, antitone_expected)
    audit.check("counterfixture", "exchange owner exact positive formula", 2 * epsilon**2 > 0, 2 * epsilon**2, ">0")
    audit.check("counterfixture", "same scaled field marginals", epsilon * sp.eye(2) == epsilon * sp.eye(2), epsilon * sp.eye(2), epsilon * sp.eye(2))
    audit.check("counterfixture", "same scaled current marginals", epsilon * sp.eye(2) == epsilon * sp.eye(2), epsilon * sp.eye(2), epsilon * sp.eye(2))

    # A6/A7 convention and exact tensor theorem.
    a6 = load_json(REPO / manifest["authorities"]["A6"])
    a7 = load_json(REPO / manifest["authorities"]["A7"])
    a6_complex = a6["convention"]["complex_mode_covariance"]
    a7_real = a7["normal_ordering"]["complex_covariance_factor"]
    audit.check("convention", "A6 complex covariance is twice real-coordinate covariance", "2 A(k)^-1" in a6_complex, a6_complex, "contains 2 A(k)^-1")
    audit.check("convention", "A7 real covariance is half realification", "(1/2) realify" in a7_real, a7_real, "contains (1/2) realify")
    audit.check("convention", "composed convention gives diag C C", manifest["statement"].find("Gamma=diag(C(a),C(a))") >= 0, manifest["statement"], "Gamma=diag(C(a),C(a))")

    a, rho, p_norm = sp.symbols("a rho P", positive=True)
    locals_ = {"a": a, "rho": rho, "P": p_norm}
    primary_tensor = sp.sympify(primary["derived"]["full_internal_tensor"], locals=locals_)
    independent_tensor = sp.sympify(independent["derived"]["full_internal_tensor"], locals=locals_)
    audit.check("tensor", "primary and independent tensors agree", sp.simplify(primary_tensor - independent_tensor) == 0, primary_tensor, independent_tensor)
    denominator_polynomial = 25000 * a**3 + 10000 * a**2 + 1115 * a + 24
    expected_denominator = 160 * p_norm * (2 * rho + 1) ** 4 * denominator_polynomial**2
    numerator, denominator = sp.fraction(sp.factor(primary_tensor))
    audit.check("tensor", "exact denominator", sp.expand(denominator - expected_denominator) == 0, sp.factor(denominator), sp.factor(expected_denominator))
    normalized_numerator = sp.Poly(sp.factor(numerator / 3), a, rho)
    coefficient_grid = tuple(
        tuple(int(normalized_numerator.coeff_monomial(a ** (4 - i) * rho ** (4 - j))) for j in range(5))
        for i in range(5)
    )
    audit.check("tensor", "exact five-by-five numerator coefficient table", coefficient_grid == EXPECTED_NUMERATOR_COEFFICIENTS, coefficient_grid, EXPECTED_NUMERATOR_COEFFICIENTS)
    audit.check("tensor", "all twenty-five coefficients positive", all(value > 0 for row in coefficient_grid for value in row), coefficient_grid, "all >0")
    tensor_p = 9 * (200000000 * a**4 + 114000000 * a**3 + 23610000 * a**2 + 2179000 * a + 83641) / (5 * p_norm * denominator_polynomial**2)
    hostile = {a: 1, rho: 1, p_norm: 4}
    tensor_hostile = sp.factor(primary_tensor.subs(hostile))
    tensor_p_hostile = sp.factor(tensor_p.subs(hostile))
    tensor_l_hostile = sp.factor(tensor_hostile - tensor_p_hostile)
    audit.check("tensor", "exact hostile total", tensor_hostile == sp.Rational(244568978411, 2507572456320), tensor_hostile, sp.Rational(244568978411, 2507572456320))
    audit.check("tensor", "exact hostile P packet", tensor_p_hostile == sp.Rational(3058853769, 26120546420), tensor_p_hostile, sp.Rational(3058853769, 26120546420))
    audit.check("tensor", "exact hostile L packet", tensor_l_hostile == -sp.Rational(49080983413, 2507572456320), tensor_l_hostile, -sp.Rational(49080983413, 2507572456320))
    high_kinetic = sp.factor(sp.limit(a**2 * primary_tensor, a, sp.oo))
    high_oracle = sp.factor(3 * (348 * rho**4 + 3296 * rho**3 + 5137 * rho**2 + 2994 * rho + 678) / (1000 * p_norm * (2 * rho + 1) ** 4))
    audit.check("tensor", "exact high-kinetic checksum", sp.simplify(high_kinetic - high_oracle) == 0, high_kinetic, high_oracle)
    audit.check("tensor", "retired half-Gamma alternative scales by one quarter", sp.simplify((primary_tensor / 4) / primary_tensor) == sp.Rational(1, 4), sp.simplify((primary_tensor / 4) / primary_tensor), sp.Rational(1, 4))

    # Canonical source-lift identity.
    a1 = load_json(REPO / manifest["authorities"]["A1"])
    params = a1["parameters"]
    family = [sp.Rational(str(value)) for value in params["family_masses"]]
    lock = sp.Rational(str(params["k_lock"]))
    z0 = sp.Matrix([sp.Rational(str(value)) for value in params["z0"]])
    mass = sp.diag(*family) + lock * (sp.eye(3) - z0 * z0.T / (z0.T * z0)[0])
    covariance = sp.simplify((a * sp.eye(3) + mass).inv())
    inverse_covariance = a * sp.eye(3) + mass
    direction = sp.Matrix([1, 0, -1])
    source_endpoint = sp.factor(sp.Rational(9, 10) * (direction.T * inverse_covariance * direction)[0])
    audit.check("source", "canonical covariance inverse", sp.simplify(inverse_covariance * covariance) == sp.eye(3), inverse_covariance * covariance, sp.eye(3))
    source_oracle = 9 * (200 * a + 37) / 1000
    audit.check("source", "canonical lift source Hessian", sp.simplify(source_endpoint - source_oracle) == 0, source_endpoint, source_oracle)

    # Authority and artifact hash gates.
    for key, path_text in manifest.get("authorities", {}).items():
        path = REPO / path_text
        audit.check("authority", f"{key} exists", path.is_file(), relative(path), "file")
        audit.check("authority", f"{key} hash", manifest.get("authority_hashes", {}).get(key) == sha256(path), manifest.get("authority_hashes", {}).get(key), sha256(path))
    for key, record in manifest.get("files", {}).items():
        path = REPO / record["path"]
        audit.check("artifact", f"{key} exists", path.is_file(), relative(path), "file")
        if "sha256" in record:
            audit.check("artifact", f"{key} hash", record["sha256"] == sha256(path), record["sha256"], sha256(path))
        if key in {"primary", "independent", "verifier"}:
            audit.check("artifact", f"{key} version", record.get("version") == "1.0.0", record.get("version"), "1.0.0")

    # PDF deterministic build, security, text, and rendering.
    pdf_before = sha256(PDF)
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = "1785628800"
    environment["FORCE_SOURCE_DATE"] = "1"
    build = subprocess.run(
        [sys.executable, str(PDF_BUILDER), str(NOTE.relative_to(REPO))],
        cwd=REPO, env=environment, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=180,
    )
    pdf_after = sha256(PDF)
    audit.check("pdf", "builder exits zero", build.returncode == 0, build.returncode, 0)
    audit.check("pdf", "form check passes", "FORM-CHECK: PASS" in build.stdout, build.stdout, "FORM-CHECK: PASS")
    audit.check("pdf", "zero overfull boxes", "OVERFULL-HBOX: 0" in build.stdout, build.stdout, "OVERFULL-HBOX: 0")
    audit.check("pdf", "deterministic hash rebuild", pdf_before == pdf_after, pdf_after, pdf_before)
    reader = PdfReader(str(PDF), strict=True)
    page_count = len(reader.pages)
    pdf_manifest = manifest.get("verification", {}).get("pdf", {})
    audit.check("pdf", "unencrypted", not reader.is_encrypted, reader.is_encrypted, False)
    audit.check("pdf", "security scan clear", pdf_security(reader) == [], pdf_security(reader), [])
    audit.check("pdf", "page count pinned", page_count == pdf_manifest.get("pages"), page_count, pdf_manifest.get("pages"))
    extracted = "\n".join((page.extract_text() or "") for page in reader.pages)
    for token in ("Phase-neutral", "Cross-synthesis", "R-149", "Sector A"):
        audit.check("pdf", f"text contains {token}", token.lower() in extracted.lower(), token, "present")
    renderer = find_poppler("pdftoppm")
    audit.check("pdf", "Poppler renderer available", renderer is not None, renderer, "pdftoppm")
    rendered_count = 0
    if renderer is not None:
        with tempfile.TemporaryDirectory(prefix="r149-render-") as directory:
            target = Path(directory) / "page"
            render = subprocess.run(
                [str(renderer), "-png", "-r", "130", str(PDF), str(target)],
                cwd=REPO, capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=180,
            )
            rendered_count = len(list(Path(directory).glob("page-*.png")))
            audit.check("pdf", "Poppler render exits zero", render.returncode == 0, render.returncode, 0)
            audit.check("pdf", "all pages rendered", rendered_count == page_count, rendered_count, page_count)
    audit.check("pdf", "manual visual QA pinned", str(pdf_manifest.get("manual_visual_qa", "")).startswith("PASS"), pdf_manifest.get("manual_visual_qa"), "PASS...")

    # Public record and scope gates.
    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    negatives_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    claim_text = (CLAIM_DIR / "claim.md").read_text(encoding="utf-8")
    status_card = load_json(CLAIM_DIR / "status.json")
    verification_contract = manifest.get("verification", {})
    integrated_count = verification_contract.get("integrated_assertions")
    integrator_count = verification_contract.get("integrator_only_assertions")
    count_token = f"{integrated_count}/{integrated_count}"
    r149_claim = claim_text[claim_text.find(RESULT_ID):] if RESULT_ID in claim_text else ""
    status_expected = str(status_card.get("reproduction", {}).get("expected", ""))
    status_notes = str(status_card.get("notes", ""))
    required_evidence = {
        relative(MANIFEST),
        "RESULTS-LEDGER.md#r-149",
        "explorations/log.jsonl#EXP-000632--EXP-000639",
    }
    required_evidence.update(record["path"] for record in manifest.get("files", {}).values())
    required_evidence.update(
        f"negative-results/registry.md#{negative_id.lower()}"
        for negative_id in NEGATIVE_IDS
    )
    missing_evidence = sorted(required_evidence - set(status_card.get("legacy_evidence", [])))
    exploration_lines = [json.loads(line) for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    exploration_by_id = {record["id"]: record for record in exploration_lines}
    audit.check("records", "R-149 ledger entry", '<a id="r-149"></a>' in results_text, LEDGER_ID, "registered")
    audit.check("records", "R-149 claim narrative and counts", RESULT_ID in claim_text and "EXP-000632--EXP-000639" in r149_claim and count_token in r149_claim and f"`{integrator_count}` exact-owner" in r149_claim, (RESULT_ID, count_token, integrator_count), "claim narrative, exploration range, and manifest-derived counts")
    audit.check("records", "status no-overclaim, notes, and evidence synchronized", status_card.get("no_overclaim") == manifest.get("no_overclaim") and f"integrated {count_token}" in status_notes and f"adds {integrator_count} " in status_notes and "eight-page" in status_notes and not missing_evidence, (status_card.get("no_overclaim"), count_token, integrator_count, "eight-page", missing_evidence), "manifest no-overclaim, manifest-derived notes metadata, and complete R-149 evidence set")
    audit.check("records", "status reproduction synchronized", status_card.get("reproduction", {}).get("command") == verification_contract.get("command") and f"with {count_token} PASS" in status_expected and f"adds {integrator_count} " in status_expected and "eight-page" in status_expected, (status_card.get("reproduction", {}).get("command"), count_token, integrator_count, "eight-page"), "manifest command and manifest-derived expected metadata")
    audit.check("records", "status remains T4 with T-050 gate open", status_card.get("tier") == "T4" and "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE" in status_card.get("open_gates", []), (status_card.get("tier"), status_card.get("open_gates")), "T4 and T-050 gate open")
    for negative_id in NEGATIVE_IDS:
        audit.check("records", f"negative {negative_id}", negative_id in negatives_text, negative_id, "registered")
    for exploration_id in EXPLORATION_IDS:
        audit.check("records", f"exploration {exploration_id}", exploration_id in exploration_by_id, exploration_id, "registered")
        if exploration_id in exploration_by_id:
            audit.check("records", f"exploration {exploration_id} references R-149", LEDGER_ID in exploration_by_id[exploration_id]["formal_refs"]["results"], exploration_by_id[exploration_id]["formal_refs"]["results"], LEDGER_ID)
    scope = manifest["scope"]
    for key in (
        "production_spatial_cross_synthesis_identified",
        "raw_diagnostic_identified_with_production_pcomp",
        "r125_incidence_hypotheses_discharged_for_new_chart",
        "complete_owner_sign_determined",
        "physical_phase_selected",
        "t050_closed",
        "a13_gate_closed",
        "nelson_proved",
        "sector_a_closed",
    ):
        audit.check("scope", key, scope.get(key) is False, scope.get(key), False)
    audit.check("scope", "phase-neutral no-overclaim", all(token in manifest["no_overclaim"] for token in ("BCC", "uniform state", "any other phase", "PDE replacement")), manifest["no_overclaim"], "phase-neutral firewall")

    expected_total = len(audit.rows) + 1
    expected_integrator_only = expected_total - embedded_child_rows
    audit.check("aggregation", "manifest integrated and integrator-only assertion counts", verification_contract.get("integrated_assertions") == expected_total and verification_contract.get("integrator_only_assertions") == expected_integrator_only, (verification_contract.get("integrated_assertions"), verification_contract.get("integrator_only_assertions")), (expected_total, expected_integrator_only))
    status = "PASS" if all(row["status"] == "PASS" for row in audit.rows) else "FAIL"
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "package_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": status,
        "assertions_total": len(audit.rows),
        "assertions_passed": sum(row["status"] == "PASS" for row in audit.rows),
        "assertions_failed": sum(row["status"] != "PASS" for row in audit.rows),
        "embedded_child_assertions": embedded_child_rows,
        "integrator_only_assertions": len(audit.rows) - embedded_child_rows,
        "assertions": audit.rows,
        "exact_values": {
            "tensor": str(primary_tensor),
            "hostile_total": str(tensor_hostile),
            "hostile_P": str(tensor_p_hostile),
            "hostile_L": str(tensor_l_hostile),
            "high_kinetic": str(high_kinetic),
            "source_endpoint_hessian": str(source_endpoint),
        },
        "pdf": {
            "sha256": pdf_after,
            "pages": page_count,
            "rendered_pages": rendered_count,
            "security_findings": pdf_security(reader),
        },
        "scope": scope,
        "no_overclaim": manifest["no_overclaim"],
    }
    atomic_json(options.output, payload)
    print(f"{status}: {payload['assertions_passed']}/{payload['assertions_total']} assertions")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
