#!/usr/bin/env python3
"""Fail-closed one-command verifier for the A10 structural package."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


__version__ = "1.0.1"
ROOT = Path(__file__).resolve().parents[2]
CLAIM = "A10-CLASSII-RELATIVE-COMMUTATOR-REDUCTION"
DEFAULT_MANIFEST = ROOT / "claims" / CLAIM / "classii_relative_structural_reduction_manifest.json"
DEFAULT_OUTPUT = ROOT / "claims" / CLAIM / "runs" / "2026-07-21-integrated-relative-structural-reduction" / "result.json"
HEX = re.compile(r"^[0-9a-f]{64}$")

EXPECTED_AUTHORITY = {
    "production_functional_manifest": "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
    "a7_composite_manifest": "claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/classii_renormalised_energy_manifest.json",
    "a9_smart_path_manifest": "claims/A9-CLASSII-SMART-PATH-CANCELLATION/classii_smart_path_manifest.json",
    "a9_nogo_manifest": "claims/A9-CLASSII-SMART-PATH-CANCELLATION/tilted_commutator_nogo_manifest.json",
    "primary_audit": "codes/foundations/a10_classii_relative_structural_reduction.py",
    "independent_audit": "codes/foundations/a10_classii_relative_structural_reduction_independent.py",
    "one_command_verifier": "codes/foundations/a10_classii_relative_structural_reduction_verify.py",
    "proof_note": "claims/A10-CLASSII-RELATIVE-COMMUTATOR-REDUCTION/notes/classii-relative-structural-reduction-260721-v1.0.tex.txt",
    "proof_pdf": "claims/A10-CLASSII-RELATIVE-COMMUTATOR-REDUCTION/notes/classii-relative-structural-reduction-260721-v1.0.pdf",
}
SCRIPT_KEYS = {"primary_audit", "independent_audit", "one_command_verifier"}


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def script_version(path: Path) -> str | None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__version__" and isinstance(node.value.value, str):
                    return node.value.value
    return None


def atomic_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if passed else "FAIL", "actual": actual, "expected": expected})


def relative(left: float, right: float) -> float:
    return abs(left - right) / max(1.0, abs(left), abs(right))


def validate_manifest(manifest: dict[str, Any]) -> tuple[list[str], dict[str, dict[str, str]]]:
    errors: list[str] = []
    hashes: dict[str, dict[str, str]] = {}
    if manifest.get("schema") != "tect/a10-classii-relative-structural-reduction/1.0":
        errors.append("manifest schema mismatch")
    if manifest.get("package_version") != "1.0.1":
        errors.append("package version mismatch")
    if manifest.get("claim_id") != CLAIM:
        errors.append("claim id mismatch")
    if manifest.get("status") != "T4 PROVED-STRUCTURAL-REDUCTION@FIXED-FLOOR-FINITE-CUTOFF":
        errors.append("status mismatch")
    authority = manifest.get("authority")
    if not isinstance(authority, dict) or set(authority) != set(EXPECTED_AUTHORITY):
        errors.append("authority set mismatch")
        return errors, hashes
    for key, expected_path in EXPECTED_AUTHORITY.items():
        item = authority.get(key)
        if not isinstance(item, dict) or item.get("path") != expected_path:
            errors.append(f"{key}: path mismatch")
            continue
        expected_hash = item.get("sha256")
        if not isinstance(expected_hash, str) or not HEX.fullmatch(expected_hash):
            errors.append(f"{key}: invalid SHA-256")
            continue
        path = (ROOT / expected_path).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"{key}: path escapes repository")
            continue
        if not path.is_file():
            errors.append(f"{key}: missing file")
            continue
        actual = sha256(path)
        hashes[key] = {"path": expected_path, "expected": expected_hash, "actual": actual}
        if actual != expected_hash:
            errors.append(f"{key}: hash mismatch")
        if key in SCRIPT_KEYS and script_version(path) != item.get("version"):
            errors.append(f"{key}: version mismatch")
    expected_schemas = {
        "production_functional_manifest": "tect/a1-production-functional-realisation/1.0",
        "a7_composite_manifest": "tect/a7-classii-renormalised-energy/1.1",
        "a9_smart_path_manifest": "tect/a9-classii-smart-path-cancellation/1.0",
        "a9_nogo_manifest": "tect/a9-tilted-commutator-nogo/1.0",
    }
    for key, expected_schema in expected_schemas.items():
        try:
            upstream = json.loads((ROOT / EXPECTED_AUTHORITY[key]).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            errors.append(f"{key}: invalid JSON")
            continue
        if upstream.get("schema") != expected_schema or authority[key].get("schema") != expected_schema:
            errors.append(f"{key}: schema mismatch")
    frozen = manifest.get("frozen_shell_convention", {})
    if frozen.get("trace") != "Gamma_j" or frozen.get("commutator_trace") != "Gamma_le_j":
        errors.append("frozen-shell trace convention mismatch")
    expected_open = [
        "A10-CLASSII-MULTISCALE-ACTION-DECOMPOSITION",
        "A10-CLASSII-STABILISED-RELATIVE-LOG-LAPLACE",
    ]
    if manifest.get("open_followups") != expected_open or manifest.get("closed_subgates") != ["A10-CLASSII-DYADIC-FILTRATION-REALISATION"]:
        errors.append("open prerequisite firewall mismatch")
    target = manifest.get("composition_target", {})
    if "NOT AN ESTABLISHED RELATIVE BOUND" not in target.get("classification", ""):
        errors.append("conditional target is not labelled")
    if not (float(target.get("alpha_f", 0.0)) > 0.0 and float(target.get("alpha_d", 0.0)) > 0.0 and float(target.get("epsilon_d", 0.0)) > 0.0 and float(target.get("p", 0.0)) > 1.0):
        errors.append("composition target basic inequalities fail")
    pdf = authority.get("proof_pdf", {})
    if not isinstance(pdf.get("pages"), int) or pdf.get("pages", 0) <= 0:
        errors.append("proof PDF page count invalid")
    if pdf.get("form_check") != "PASS" or pdf.get("overfull_hbox") != 0 or pdf.get("visual_qa") != "PASS":
        errors.append("proof PDF QA contract open")
    integrated = manifest.get("integrated_audit", {})
    expected_counts = {"primary_assertions": 47, "independent_assertions": 34, "cross_assertions": 20, "expected_aggregate_assertions": 101}
    for key, value in expected_counts.items():
        if integrated.get(key) != value:
            errors.append(f"{key} mismatch")
    expected_contract = {
        "primary_result_schema": "tect/a10-classii-relative-structural-reduction-primary-result/1.0",
        "independent_result_schema": "tect/a10-classii-relative-structural-reduction-independent-result/1.0",
        "integrated_result_schema": "tect/a10-classii-relative-structural-reduction-integrated-result/1.0",
    }
    for key, value in expected_contract.items():
        if manifest.get("run_contract", {}).get(key) != value:
            errors.append(f"{key} mismatch")
    excluded = manifest.get("honesty_boundary", {}).get("excluded", [])
    for phrase in ("a production-valid multiscale reconstruction of the actual A7 action", "the all-field stabilised relative log-Laplace estimate", "the self-coupled A7 Nelson bound", "a full three-component interacting Gibbs measure", "T6 or T7"):
        if phrase not in excluded:
            errors.append(f"missing exclusion: {phrase}")
    return errors, hashes


def run_child(script: Path, manifest: Path, output: Path) -> dict[str, Any]:
    process = subprocess.run(
        [sys.executable, str(script), "--manifest", str(manifest), "--output", str(output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        result = json.loads(output.read_text(encoding="utf-8"))
        error = None
    except (OSError, json.JSONDecodeError) as exc:
        result = None
        error = str(exc)
    return {"command": [sys.executable, str(script), "--manifest", str(manifest), "--output", str(output)], "returncode": process.returncode, "stdout": process.stdout, "stderr": process.stderr, "result": result, "load_error": error}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    options = parser.parse_args()
    manifest = json.loads(options.manifest.read_text(encoding="utf-8"))
    errors, hashes = validate_manifest(manifest)
    rows: list[dict[str, Any]] = []
    add(rows, "manifest_preflight", not errors, errors, [])

    with tempfile.TemporaryDirectory(prefix="tect-a10-relative-") as directory:
        temporary = Path(directory)
        primary_run = run_child(ROOT / EXPECTED_AUTHORITY["primary_audit"], options.manifest, temporary / "primary.json")
        independent_run = run_child(ROOT / EXPECTED_AUTHORITY["independent_audit"], options.manifest, temporary / "independent.json")
    primary = primary_run.get("result") or {}
    independent = independent_run.get("result") or {}
    integrated = manifest["integrated_audit"]
    contract = manifest["run_contract"]
    tolerance = float(integrated["numeric_relative_tolerance"])

    add(rows, "primary_exit_zero", primary_run["returncode"] == 0, primary_run["returncode"], 0)
    add(rows, "independent_exit_zero", independent_run["returncode"] == 0, independent_run["returncode"], 0)
    add(rows, "primary_contract", primary.get("schema") == contract["primary_result_schema"] and primary.get("verdict") == "A10-CLASSII-RELATIVE-STRUCTURAL-REDUCTION-PRIMARY-PASS" and primary.get("assertion_count") == integrated["primary_assertions"], {"schema": primary.get("schema"), "verdict": primary.get("verdict"), "count": primary.get("assertion_count")}, {"schema": contract["primary_result_schema"], "verdict": "PRIMARY-PASS", "count": 47})
    add(rows, "independent_contract", independent.get("schema") == contract["independent_result_schema"] and independent.get("verdict") == "A10-CLASSII-RELATIVE-STRUCTURAL-REDUCTION-INDEPENDENT-PASS" and independent.get("assertion_count") == integrated["independent_assertions"], {"schema": independent.get("schema"), "verdict": independent.get("verdict"), "count": independent.get("assertion_count")}, {"schema": contract["independent_result_schema"], "verdict": "INDEPENDENT-PASS", "count": 34})

    primary_coefficients = primary.get("derived", {}).get("coefficients", {})
    independent_coefficients = independent.get("derived", {}).get("coefficients", {})
    for key in ("a", "b", "c"):
        gap = relative(float(primary_coefficients.get(key, float("nan"))), float(independent_coefficients.get(key, float("nan"))))
        add(rows, f"cross_coefficient_{key}", gap <= tolerance, gap, f"<={tolerance}")
    primary_bounds = primary.get("derived", {}).get("bounds", {})
    add(rows, "cross_beta_B", relative(float(primary_bounds.get("beta_B", float("nan"))), float(independent.get("derived", {}).get("beta_B", float("nan")))) <= tolerance, {"primary": primary_bounds.get("beta_B"), "independent": independent.get("derived", {}).get("beta_B")}, "agree")
    add(rows, "cross_beta_1", relative(float(primary_bounds.get("beta_1", float("nan"))), float(independent.get("derived", {}).get("beta_1", float("nan")))) <= tolerance, {"primary": primary_bounds.get("beta_1"), "independent": independent.get("derived", {}).get("beta_1")}, "agree")

    p_blaschke = primary.get("derived", {}).get("blaschke", [])
    i_blaschke = independent.get("derived", {}).get("blaschke", [])
    p_ratio = float(p_blaschke[-1]["negative_commutator_ratio"]) if p_blaschke else float("nan")
    i_ratio = float(i_blaschke[-1]["ratio"]) if i_blaschke else float("nan")
    add(rows, "cross_strict_dyadic_ratio", relative(p_ratio, i_ratio) <= tolerance and min(p_ratio, i_ratio) > 0.9998, {"primary": p_ratio, "independent": i_ratio}, "agree and >0.9998")
    p_plane = primary.get("derived", {}).get("plane_wave", {}).get("rows", [])
    i_plane = independent.get("derived", {}).get("plane_wave", [])
    add(rows, "cross_plane_wave_trace_sign", bool(p_plane and i_plane) and all(row["commutator_complete"] < 0.0 for row in p_plane) and all(row["complete_C"] < 0.0 for row in i_plane), {"primary": [row["commutator_complete"] for row in p_plane], "independent": [row["complete_C"] for row in i_plane]}, "all negative")

    p_triad = primary.get("derived", {}).get("triad", {})
    i_triad = independent.get("derived", {}).get("triad", {})
    add(rows, "cross_triad_M6", relative(float(p_triad.get("M6", float("nan"))), float(i_triad.get("M6", float("nan")))) <= tolerance, {"primary": p_triad.get("M6"), "independent": i_triad.get("M6")}, "agree")
    p_composition = primary.get("derived", {}).get("composition", {})
    i_composition = independent.get("derived", {}).get("composition", {})
    for key in ("p_alpha", "B6", "Kf_over_Cfr"):
        gap = relative(float(p_composition.get(key, float("nan"))), float(i_composition.get(key, float("nan"))))
        add(rows, f"cross_composition_{key}", gap <= tolerance, gap, f"<={tolerance}")

    independent_source = (ROOT / EXPECTED_AUTHORITY["independent_audit"]).read_text(encoding="utf-8")
    forbidden = ("import a10_classii_relative_structural_reduction", "from a10_classii_relative_structural_reduction")
    add(rows, "independent_route_nonimporting", not any(token in independent_source for token in forbidden), [token for token in forbidden if token in independent_source], [])
    proof_text = (ROOT / EXPECTED_AUTHORITY["proof_note"]).read_text(encoding="utf-8") if (ROOT / EXPECTED_AUTHORITY["proof_note"]).is_file() else ""
    required_note_tokens = ("Gamma_j", "Gamma_{\\le j}", "Blaschke", "A10-CLASSII-MULTISCALE-ACTION-DECOMPOSITION", "A10-CLASSII-DYADIC-FILTRATION-REALISATION", "A10-CLASSII-STABILISED-RELATIVE-LOG-LAPLACE", "does not prove the relative form bound")
    add(rows, "proof_note_boundary_tokens", all(token in proof_text for token in required_note_tokens), [token for token in required_note_tokens if token not in proof_text], [])
    pdf = manifest["authority"]["proof_pdf"]
    add(rows, "proof_pdf_QA_closed", pdf.get("pages", 0) > 0 and pdf.get("form_check") == "PASS" and pdf.get("overfull_hbox") == 0 and pdf.get("visual_qa") == "PASS", pdf, "closed PDF QA")
    expected_open = ["A10-CLASSII-MULTISCALE-ACTION-DECOMPOSITION", "A10-CLASSII-STABILISED-RELATIVE-LOG-LAPLACE"]
    excluded = manifest["honesty_boundary"]["excluded"]
    closed = manifest["honesty_boundary"]["closed"]
    add(rows, "open_gate_firewall", manifest.get("open_followups") == expected_open and "a production-valid multiscale reconstruction of the actual A7 action" in excluded and "the all-field stabilised relative log-Laplace estimate" in excluded and "a sharp rectangular-cube filtration with independent innovations and a uniform terminal L4 projection bound" in closed, {"gates": manifest.get("open_followups"), "excluded": excluded, "closed": closed}, "two prerequisites open; cube filtration closed")

    cross_count = len(rows)
    aggregate = int(primary.get("assertion_count", 0)) + int(independent.get("assertion_count", 0)) + cross_count
    failures = [row["name"] for row in rows if row["status"] != "PASS"]
    if cross_count != integrated["cross_assertions"]:
        failures.append("cross_assertion_count")
    if aggregate != integrated["expected_aggregate_assertions"]:
        failures.append("aggregate_assertion_count")
    payload = {
        "schema": contract["integrated_result_schema"],
        "verdict": "A10-CLASSII-RELATIVE-STRUCTURAL-REDUCTION-INTEGRATED-PASS" if not failures else "FAIL",
        "claim_id": CLAIM,
        "version": __version__,
        "git_commit": commit(),
        "platform": platform.platform(),
        "python": sys.version,
        "manifest_sha256": sha256(options.manifest),
        "authority_hashes": hashes,
        "assertion_count": aggregate,
        "cross_assertion_count": cross_count,
        "failed": failures,
        "assertions": rows,
        "primary_run": primary_run,
        "independent_run": independent_run,
    }
    atomic_json(options.output, payload)
    if failures:
        print(f"FAIL: {len(failures)}: {', '.join(failures)}")
        print(f"Evidence: {options.output.resolve()}")
        return 1
    print(f"PASS: primary ({primary['assertion_count']}/{primary['assertion_count']})")
    print(f"PASS: independent ({independent['assertion_count']}/{independent['assertion_count']})")
    print(f"ASSERTS: {aggregate}/{aggregate}")
    print("A10-CLASSII-RELATIVE-STRUCTURAL-REDUCTION-INTEGRATED-PASS")
    print(f"Evidence: {options.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
