#!/usr/bin/env python3
"""Integrated release verifier for the CP1a cubic-SOS common parent."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from pypdf import PdfReader


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1A-T3-CUBIC-SOS-COMMON-PARENT-v0"
SLUG = "pre-a-cp1a-t3-cubic-sos-common-parent"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
COMPARISON_CONTEXT = "A2-FULL-PRODUCTION-WELLPOSED"

PRIMARY = REPO / "codes" / "foundations" / f"{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / "codes" / "foundations" / f"{SLUG.replace('-', '_')}_independent.py"
PDF_BUILDER = REPO / "codes" / "foundations" / f"{SLUG.replace('-', '_')}_pdf.py"
MANIFEST = REPO / "strategy" / f"{SLUG}-manifest.json"
CERTIFICATE = REPO / "strategy" / f"{SLUG}-certificate-260803.md"
PDF = REPO / "output" / "pdf" / f"{SLUG}-certificate-260803-v0.1.pdf"
STORED_PRIMARY = (
    REPO
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-primary-{SLUG}"
    / "result.json"
)
STORED_INDEPENDENT = (
    REPO
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-independent-{SLUG}"
    / "result.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-integrated-{SLUG}"
    / "result.json"
)

NEGATIVE_ID = "NG-2026-08-03-PRE-A-CP1A-UNCHANGED-COMPONENTWISE-KERNEL-CALIBRATION"
EXPLORATION_IDS = (
    "EXP-000714",
    "EXP-000715",
    "EXP-000716",
    "EXP-000717",
    "EXP-000718",
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def relative(path: Path) -> str:
    return str(path.relative_to(REPO)).replace("\\", "/")


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
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {
                "name": name,
                "status": "PASS",
                "actual": serial(actual),
                "expected": serial(expected),
                "group": group,
            }
        )


def run_child(script: Path, output: Path) -> tuple[dict[str, Any], str]:
    process = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    if process.returncode != 0:
        raise AssertionError(
            f"child failed: {relative(script)}\nstdout={process.stdout}\nstderr={process.stderr}"
        )
    return json.loads(output.read_text(encoding="utf-8")), process.stdout.strip()


def derive() -> dict[str, Any]:
    audit = Audit()
    required_files = (
        PRIMARY,
        INDEPENDENT,
        PDF_BUILDER,
        MANIFEST,
        CERTIFICATE,
        PDF,
        STORED_PRIMARY,
        STORED_INDEPENDENT,
    )
    for path in required_files:
        audit.check(
            f"required artifact exists: {relative(path)}",
            path.is_file(),
            path.is_file(),
            True,
            "artifact_presence",
        )

    with tempfile.TemporaryDirectory(prefix="cp1a-verify-") as directory:
        temporary = Path(directory)
        primary, primary_stdout = run_child(PRIMARY, temporary / "primary.json")
        independent, independent_stdout = run_child(
            INDEPENDENT, temporary / "independent.json"
        )
        fresh_pdf = temporary / "certificate.pdf"
        pdf_process = subprocess.run(
            [sys.executable, str(PDF_BUILDER), "--output", str(fresh_pdf)],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        audit.check(
            "deterministic PDF builder exits zero",
            pdf_process.returncode == 0
            and "PASS | deterministic PDF |" in pdf_process.stdout
            and not pdf_process.stderr.strip(),
            {
                "returncode": pdf_process.returncode,
                "stdout_has_pass": "PASS | deterministic PDF |" in pdf_process.stdout,
                "stderr_empty": not pdf_process.stderr.strip(),
            },
            {"returncode": 0, "stdout_has_pass": True, "stderr_empty": True},
            "fresh_reproduction",
        )
        audit.check(
            "fresh deterministic PDF equals stored PDF byte for byte",
            fresh_pdf.read_bytes() == PDF.read_bytes(),
            sha256(fresh_pdf),
            sha256(PDF),
            "fresh_reproduction",
        )

    audit.check(
        "primary child stdout",
        "PASS 38/38" in primary_stdout and "CP1a compatibility only" in primary_stdout,
        primary_stdout,
        "PASS 38/38 and scoped verdict",
        "fresh_reproduction",
    )
    audit.check(
        "independent child stdout",
        "PASS 33/33" in independent_stdout and "independent CP1a audit" in independent_stdout,
        independent_stdout,
        "PASS 33/33 and independent verdict",
        "fresh_reproduction",
    )

    stored_primary = json.loads(STORED_PRIMARY.read_text(encoding="utf-8"))
    stored_independent = json.loads(STORED_INDEPENDENT.read_text(encoding="utf-8"))
    audit.check(
        "stored primary equals fresh primary",
        stored_primary == primary,
        stored_primary == primary,
        True,
        "stored_artifact_integrity",
    )
    audit.check(
        "stored independent equals fresh independent",
        stored_independent == independent,
        stored_independent == independent,
        True,
        "stored_artifact_integrity",
    )

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    identities = (
        ("primary", primary.get("candidate_id")),
        ("independent", independent.get("candidate_id")),
        ("manifest", manifest.get("candidate_id")),
    )
    for label, value in identities:
        audit.check(
            f"{label} candidate identity",
            value == CANDIDATE_ID,
            value,
            CANDIDATE_ID,
            "identity",
        )
    audit.check(
        "primary assertion contract",
        primary["assertions"]["passed"] == primary["assertions"]["total"] == 38,
        primary["assertions"]["passed"],
        38,
        "assertion_contract",
    )
    audit.check(
        "independent assertion contract",
        independent["assertions"]["passed"]
        == independent["assertions"]["total"]
        == 33,
        independent["assertions"]["passed"],
        33,
        "assertion_contract",
    )

    shared_values = (
        ("alpha", primary["kernel"]["alpha"], independent["derived"]["alpha"], "1/256"),
        ("beta", primary["kernel"]["beta"], independent["derived"]["beta"], "21/512"),
        (
            "relative beta",
            primary["kernel"]["relative_beta"],
            independent["derived"]["relative_beta"],
            "21/2",
        ),
        (
            "off-node gap",
            primary["kernel"]["off_node_lattice_gap"],
            independent["derived"]["off_node_lattice_gap"],
            9,
        ),
        (
            "node anisotropy",
            primary["kernel"]["node_anisotropy_ratio"],
            independent["derived"]["node_anisotropy_ratio"],
            "21/2",
        ),
        (
            "r-only match",
            primary["exact_results"]["pah1_frequency_ratio_match_values"][0],
            independent["derived"]["pah1_ratio_match_r"],
            0,
        ),
        (
            "unchanged componentwise axis",
            primary["exact_results"][
                "unchanged_componentwise_kernel_axis_value_after_constant_calibration"
            ],
            independent["derived"]["unchanged_componentwise_axis_value"],
            6,
        ),
    )
    for label, primary_value, independent_value, expected in shared_values:
        audit.check(
            f"shared exact value: {label}",
            str(primary_value) == str(independent_value) == str(expected),
            (primary_value, independent_value),
            (expected, expected),
            "cross_implementation",
        )

    audit.check(
        "primary node Hessian spectrum",
        primary["kernel"]["node_hessian_eigenvalues"] == ["3/2", "63/4", "63/4"],
        primary["kernel"]["node_hessian_eigenvalues"],
        ["3/2", "63/4", "63/4"],
        "cross_implementation",
    )
    audit.check(
        "independent node Hessian spectrum",
        independent["derived"]["node_hessian_spectrum"] == ["3/2", "63/4", "63/4"],
        independent["derived"]["node_hessian_spectrum"],
        ["3/2", "63/4", "63/4"],
        "cross_implementation",
    )
    audit.check(
        "primary verdict remains CP1a only",
        "CP1a structural compatibility benchmark" in primary["verdict"]
        and primary["hostile_controls"]["full_cp1_closed"] is False,
        primary["verdict"],
        "CP1a only and full CP1 false",
        "scope",
    )
    audit.check(
        "independent scope retains CP1 and Pre-A open",
        independent["scope"]["cp1_closed"] is False
        and independent["scope"]["pre_a_complete"] is False,
        independent["scope"],
        "cp1_closed=false and pre_a_complete=false",
        "scope",
    )

    declared_hashes = manifest["artifact_hashes"]
    for key, path in (
        ("primary_script", PRIMARY),
        ("independent_script", INDEPENDENT),
        ("pdf_builder", PDF_BUILDER),
        ("certificate", CERTIFICATE),
        ("pdf", PDF),
    ):
        audit.check(
            f"manifest hash: {key}",
            declared_hashes[key]["path"] == relative(path)
            and declared_hashes[key]["sha256"] == sha256(path),
            declared_hashes[key],
            {"path": relative(path), "sha256": sha256(path)},
            "manifest_hashes",
        )

    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    certificate_tokens = (
        "Authority: T0 kinematic/static common-parent compatibility certificate only",
        "delta_lattice",
        "Theorem CP1a-static",
        "3g/(2V)>0",
        "E_N(r)-E_N(0)<0",
        "DO NOT SELECT IT AS THE PHYSICAL EQUATION",
        "It does not prove a physical vacuum",
        "CP1b/CP2",
        "T-053",
    )
    for token in certificate_tokens:
        audit.check(
            f"certificate scope token: {token}",
            token in certificate_text,
            token in certificate_text,
            True,
            "certificate",
        )

    reader = PdfReader(str(PDF))
    root = reader.trailer["/Root"]
    pdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    normalized_pdf_text = " ".join(pdf_text.split())
    audit.check(
        "PDF page contract",
        len(reader.pages) == 7,
        len(reader.pages),
        7,
        "pdf",
    )
    audit.check(
        "PDF is nontrivial",
        PDF.stat().st_size > 20000,
        PDF.stat().st_size,
        "> 20000 bytes",
        "pdf",
    )
    audit.check(
        "PDF security surface is inert",
        not reader.is_encrypted
        and "/AcroForm" not in root
        and "/Names" not in root
        and "/OpenAction" not in root
        and "/AA" not in root,
        {
            "encrypted": reader.is_encrypted,
            "AcroForm": "/AcroForm" in root,
            "Names": "/Names" in root,
            "OpenAction": "/OpenAction" in root,
            "AA": "/AA" in root,
        },
        "all false",
        "pdf",
    )
    metadata = dict(reader.metadata or {})
    audit.check(
        "PDF deterministic metadata",
        metadata.get("/CreationDate") == "D:20000101000000+00'00'"
        and metadata.get("/Title")
        == "CP1a cubic-SOS common-parent compatibility certificate",
        metadata,
        "fixed creation date and title",
        "pdf",
    )
    for token in (
        "CP1a cubic-SOS common-parent compatibility certificate",
        "Exact zero set and lattice gap",
        "E_N(r)-E_N(0)<0",
        "DO NOT SELECT IT AS THE PHYSICAL EQUATION",
    ):
        audit.check(
            f"PDF extracted text token: {token}",
            token in normalized_pdf_text,
            token in normalized_pdf_text,
            True,
            "pdf",
        )

    negative_text = (REPO / "negative-results" / "registry.md").read_text(
        encoding="utf-8"
    )
    audit.check(
        "unchanged-kernel no-go is registered",
        f'<a id="{NEGATIVE_ID.lower()}"></a>' in negative_text
        and NEGATIVE_ID in negative_text
        and "a_cmp(4e_1)=2 c 4^4=6," in negative_text
        and "not `25`." in negative_text,
        {
            "anchor": f'<a id="{NEGATIVE_ID.lower()}"></a>' in negative_text,
            "id": NEGATIVE_ID in negative_text,
            "axis_value": "a_cmp(4e_1)=2 c 4^4=6," in negative_text,
            "target_rejected": "not `25`." in negative_text,
        },
        True,
        "records",
    )

    exploration_rows = [
        json.loads(line)
        for line in (REPO / "explorations" / "log.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    exploration_lookup = {row["id"]: row for row in exploration_rows}
    for exploration_id in EXPLORATION_IDS:
        audit.check(
            f"exploration record exists: {exploration_id}",
            exploration_id in exploration_lookup,
            exploration_id in exploration_lookup,
            True,
            "records",
        )
    audit.check(
        "CP1a exploration stays T0 and open",
        exploration_lookup["EXP-000714"]["verdict"] == "advanced"
        and "does not close CP1" in exploration_lookup["EXP-000714"]["boundary"],
        exploration_lookup["EXP-000714"]["boundary"],
        "advanced with CP1 open",
        "records",
    )
    audit.check(
        "A13 nonlinear forest shortcut is recorded failed",
        exploration_lookup["EXP-000718"]["verdict"] == "failed"
        and exploration_lookup["EXP-000718"]["task_id"] == "T-050",
        (
            exploration_lookup["EXP-000718"]["verdict"],
            exploration_lookup["EXP-000718"]["task_id"],
        ),
        ("failed", "T-050"),
        "records",
    )

    todo_text = (REPO / "TODO.md").read_text(encoding="utf-8")
    changelog_text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    changelog_log_text = (REPO / "changelog" / "log.jsonl").read_text(
        encoding="utf-8"
    )
    proof_map_text = (REPO / "theory" / "proof-evidence-map.md").read_text(
        encoding="utf-8"
    )
    catalog = json.loads((REPO / "verification" / "catalog.json").read_text(encoding="utf-8"))
    catalog_text = json.dumps(catalog, sort_keys=True)
    audit.check(
        "T-054 records CP1a and CP2 boundary",
        CANDIDATE_ID in todo_text and "CP1b/CP2" in todo_text and "T-053" in todo_text,
        CANDIDATE_ID in todo_text,
        True,
        "generated_surfaces",
    )
    audit.check(
        "changelog registers CP1a package",
        CANDIDATE_ID in changelog_text and NEGATIVE_ID in changelog_log_text,
        (CANDIDATE_ID in changelog_text, NEGATIVE_ID in changelog_log_text),
        (True, True),
        "generated_surfaces",
    )
    audit.check(
        "proof map projects all five explorations",
        all(exploration_id in proof_map_text for exploration_id in EXPLORATION_IDS),
        [exploration_id in proof_map_text for exploration_id in EXPLORATION_IDS],
        [True] * len(EXPLORATION_IDS),
        "generated_surfaces",
    )
    for path in (PRIMARY, INDEPENDENT, PDF_BUILDER, MANIFEST, CERTIFICATE, PDF):
        audit.check(
            f"catalog contains {relative(path)}",
            relative(path) in catalog_text,
            relative(path) in catalog_text,
            True,
            "generated_surfaces",
        )

    manifest_scope = manifest["scope"]
    false_scope_keys = (
        "full_cp1",
        "cp2",
        "pre_a_complete",
        "physical_model_selected",
        "exact_pah1_gaussian_state",
        "nonlinear_pah1_reduction",
        "quantum_symmetry_breaking",
        "thermodynamic_phase_transition",
        "isotropic_causal_cone",
        "bounded_uv_propagation",
        "regulator_removal",
        "absolute_empty_space_comparison",
        "sector_a_closed",
    )
    for key in false_scope_keys:
        audit.check(
            f"manifest no-overclaim flag false: {key}",
            manifest_scope.get(key) is False,
            manifest_scope.get(key),
            False,
            "scope",
        )

    source = Path(__file__).resolve()
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "version": __version__,
        "issued": "2026-08-03",
        "claim_context": CLAIM_CONTEXT,
        "comparison_context": COMPARISON_CONTEXT,
        "claim_bearing": False,
        "task_id": "T-054",
        "verdict": "PASS: CP1a finite-regulator compatibility benchmark reproduces; full CP1, CP2, Pre-A, physical selection, and Sector A remain open",
        "child_assertions": {
            "primary": primary["assertions"]["passed"],
            "independent": independent["assertions"]["passed"],
        },
        "pdf": {
            "path": relative(PDF),
            "sha256": sha256(PDF),
            "bytes": PDF.stat().st_size,
            "pages": len(reader.pages),
            "deterministic_rebuild_equal": True,
            "security_check": "no encryption, AcroForm, Names, OpenAction, or AA",
            "visual_qa": "all seven 120-dpi rendered pages inspected; no clipping, overlap, broken headings, or unreadable text",
        },
        "assertions": {
            "passed": len(audit.rows),
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "source": {
            "path": relative(source),
            "sha256": sha256(source),
        },
        "no_overclaim": (
            "The integrated PASS verifies only the declared T0 CP1a finite-regulator construction, static theorem, common-reference convention, and exact obstructions. It does not select a physical equation, recover the old PA-H1 Gaussian state, provide a nonlinear PA-H1 reduction, dynamic r history, total-work ledger, quantum or thermodynamic phase transition, isotropic causal cone, bounded ultraviolet propagation, regulator removal, physical vacuum, energy below empty space, CP1, CP2, Pre-A, T-050, or Sector A."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = derive()
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    print(
        f"PASS {payload['assertions']['passed']}/{payload['assertions']['total']} | "
        f"{CANDIDATE_ID} | integrated CP1a release audit"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
