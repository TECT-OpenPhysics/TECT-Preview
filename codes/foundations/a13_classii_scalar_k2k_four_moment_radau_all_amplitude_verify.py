#!/usr/bin/env python3
"""Integrated fail-closed verifier for the scoped R-115 theorem.

The verifier executes four non-importing children: the primary centered-form
Arb cover, the independent exact-algebraic Bernstein audit, and two exact
method-boundary engines.  It then enforces their deterministic contracts and
all manifest hash pins.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

from flint import arb
from pypdf import PdfReader


VERSION = "1.0.0"
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-SCALAR-K2K-FOUR-MOMENT-RADAU-ALL-AMPLITUDE-CLOSURE"
PRIMARY_EVALUATIONS = 46_714
PRIMARY_LEAVES = 23_613
PRIMARY_PENDING = 0
INDEPENDENT_CERTIFICATES = {
    "A": (2_850, "f0299230e3b8c646a5d6ff4b3d32f33df893849f9965b3ec06f20ad9562d13fa"),
    "minus_B": (2_145, "18ff73c987cd0c1b74dd95958cada6f014ee2ab9f1231239bd2b87ff11e51b54"),
    "A2_minus_DB2": (11_175, "a62af661d7f4af9e35d9499624e90d8c79f1f7444b87e600859ab68af266d8db"),
}
STRUCTURAL_NAMES = {
    "H", "D", "J", "J2_minus_D", "E", "W", "minus_Z",
    "weight_product", "nine_D_minus_J2", "v_side_L",
    "v_ge_b_over_4", "u_ge_b_over_2", "a_ge_1_over_6",
    "p_side_M", "p_ge_1_over_200", "q_side_N",
    "q_ge_15_over_32", "k_ge_2", "k_le_6",
    "kq_le_9a_side", "kq_le_9a",
}
STRUCTURAL_LEAVES = 24
STRUCTURAL_COEFFICIENTS = 8_298
STRUCTURAL_POSITIVE = 8_286
STRUCTURAL_ZEROS = 12
WEIGHT_LEAVES = 5
WEIGHT_COEFFICIENTS = 4_231
WEIGHT_HASHES = (
    "2a8e49a6c1980925febd15274e209ea67abb7018f6c42492f04fbb614ed4b9b1",
    "2fb1d862521b618578ee15cc501908cc4b26c0af2fa021da286fb8fea5559b7b",
    "98d2d9d7e040238aa1d72646271872bb20d83f665e4eb02953804fa39156fbc0",
    "847875d8a943808f02fed8e0a838b66bd6001c2dc4b579326cf152040fcf36c4",
    "0bea5dcddf5ebf76efbf14cc30b9e8cbf2a17107c806f656dca11f135b623c73",
)
BOUNDARY_COEFFICIENTS = 1_655
KS_UPPER_MARGIN = "-72442776419046601199446847233957478399499392897/392881140792574918584021697067765836104000000000000000"
GENERIC_RESERVE_GAP = "2789/273600"

REPO = Path(__file__).resolve().parents[2]
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_PRIMARY = REPO / "codes/foundations/a13_classii_scalar_k2k_four_moment_radau_all_amplitude.py"
DEFAULT_INDEPENDENT = REPO / "codes/foundations/a13_classii_scalar_k2k_four_moment_radau_all_amplitude_independent.py"
DEFAULT_BOUNDARY_PRIMARY = REPO / "codes/foundations/a13_classii_scalar_k2k_four_moment_radau_method_boundaries.py"
DEFAULT_BOUNDARY_INDEPENDENT = REPO / "codes/foundations/a13_classii_scalar_k2k_four_moment_radau_method_boundaries_independent.py"
DEFAULT_NOTE = CLAIM_DIR / "notes/classii-scalar-k2k-four-moment-radau-all-amplitude-closure-260728-v1.0.tex.txt"
DEFAULT_PDF = CLAIM_DIR / "notes/classii-scalar-k2k-four-moment-radau-all-amplitude-closure-260728-v1.0.pdf"
DEFAULT_MANIFEST = CLAIM_DIR / "classii_scalar_k2k_four_moment_radau_all_amplitude_manifest.json"
DEFAULT_PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-28-primary-scalar-k2k-four-moment-radau-all-amplitude/result.json"
DEFAULT_INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-28-independent-scalar-k2k-four-moment-radau-all-amplitude/result.json"
DEFAULT_BOUNDARY_PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-28-primary-scalar-k2k-four-moment-radau-method-boundaries/result.json"
DEFAULT_BOUNDARY_INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-28-independent-scalar-k2k-four-moment-radau-method-boundaries/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-28-integrated-scalar-k2k-four-moment-radau-all-amplitude/result.json"

NOTE_TOKENS = (
    "R-115",
    RESULT_ID,
    "Lemma 3.1 (left Radau majorant)",
    "Lemma 4.1 (sufficient nonnegative skew)",
    "46714",
    "23613",
    "8298",
    "4231/4231",
    "11175/11175",
    "1655/1655",
    "2789/273600",
    "Sector A remain open",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def write_json_atomic(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def positive_ball(text: object) -> bool:
    try:
        value = arb(str(text))
        return value.is_finite() and value.lower() > 0
    except (ValueError, TypeError):
        return False


def execute_child(script: Path, timeout: int) -> tuple[dict[str, Any], str, str]:
    with tempfile.TemporaryDirectory(prefix="tect-r115-child-") as directory:
        output = Path(directory) / "result.json"
        try:
            process = subprocess.run(
                [sys.executable, str(script), "--output", str(output)],
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except (subprocess.TimeoutExpired, OSError) as error:
            return ({"status": "EXECUTION_ERROR", "error": str(error)}, "", str(error))
        if process.returncode != 0:
            return (
                {"status": "EXECUTION_ERROR", "returncode": process.returncode},
                process.stdout,
                process.stderr,
            )
        if not output.is_file():
            return ({"status": "MISSING_OUTPUT", "returncode": process.returncode}, process.stdout, process.stderr)
        return load_json(output), process.stdout, process.stderr


def recursively_all_true(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, dict):
        booleans = [item for item in value.values() if isinstance(item, (bool, dict, list))]
        return bool(booleans) and all(recursively_all_true(item) for item in booleans)
    if isinstance(value, list):
        booleans = [item for item in value if isinstance(item, (bool, dict, list))]
        return bool(booleans) and all(recursively_all_true(item) for item in booleans)
    return True


def exact_leaf_ok(leaf: object, *, strict: bool = False) -> bool:
    if not isinstance(leaf, dict):
        return False
    try:
        minimum = Fraction(str(leaf.get("minimum")))
        count = int(leaf.get("coefficient_count"))
        positive = int(leaf.get("positive_count"))
        zero = int(leaf.get("zero_count"))
        negative = int(leaf.get("negative_count"))
    except (ValueError, TypeError, ZeroDivisionError):
        return False
    return (
        negative == 0
        and positive + zero == count
        and (minimum > 0 if strict else minimum >= 0)
        and (zero == 0 if strict else True)
    )


def certificate_totals(certificates: object) -> tuple[int, int, int, int, int] | None:
    if not isinstance(certificates, dict):
        return None
    leaves: list[dict[str, object]] = []
    for certificate in certificates.values():
        if not isinstance(certificate, dict) or not isinstance(certificate.get("leaves"), list):
            return None
        leaves.extend(certificate["leaves"])
    if not all(exact_leaf_ok(leaf) for leaf in leaves):
        return None
    return (
        len(leaves),
        sum(int(leaf["coefficient_count"]) for leaf in leaves),
        sum(int(leaf["positive_count"]) for leaf in leaves),
        sum(int(leaf["zero_count"]) for leaf in leaves),
        sum(int(leaf["negative_count"]) for leaf in leaves),
    )


def boundary_contract(result: object) -> tuple[bool, dict[str, object]]:
    if not isinstance(result, dict):
        return False, {"error": "not an object"}
    certificates = result.get("certificates", {})
    if not isinstance(certificates, dict):
        return False, {"error": "certificates missing"}
    try:
        coefficient_total = sum(int(item["coefficient_count"]) for item in certificates.values())
        positive_tables = all(isinstance(item, dict) for item in certificates.values()) and all(
            item.get("reconstruction") == "PASS" and Fraction(str(item.get("minimum"))) > 0
            for item in certificates.values()
        ) and len(certificates) > 0
        witness = result["exact_KS_failure_witness"]
        reserve = result["generic_four_moment_reserve_counterexample"]
        time_inside = (
            Fraction(str(witness["tau_star_upper_below_one_eighth_gap"])) > 0
            and Fraction(str(witness["residual_tau_cap_above_two_gap"])) > 0
        )
        exact_values = (
            witness.get("b") == "3219/1000"
            and witness.get("c") == "31/100"
            and witness.get("distance_above_certified_endpoint") == "1/4000"
            and witness.get("upper_KS_margin") == KS_UPPER_MARGIN
            and reserve.get("variance") == "3/2"
            and reserve.get("K") == "16/5"
            and reserve.get("positive_rational_gap") == GENERIC_RESERVE_GAP
        )
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False, {"error": "malformed exact boundary payload"}
    summary = {
        "status": result.get("status"),
        "certificate_tables": len(certificates),
        "coefficient_total": coefficient_total,
        "positive_tables": positive_tables,
        "time_inside": time_inside,
        "exact_values": exact_values,
    }
    return (
        result.get("status") == "PASS"
        and result.get("total_exact_positive_coefficients") == BOUNDARY_COEFFICIENTS
        and coefficient_total == BOUNDARY_COEFFICIENTS
        and positive_tables
        and time_inside
        and exact_values,
        summary,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary-script", type=Path, default=DEFAULT_PRIMARY)
    parser.add_argument("--independent-script", type=Path, default=DEFAULT_INDEPENDENT)
    parser.add_argument("--boundary-primary-script", type=Path, default=DEFAULT_BOUNDARY_PRIMARY)
    parser.add_argument("--boundary-independent-script", type=Path, default=DEFAULT_BOUNDARY_INDEPENDENT)
    parser.add_argument("--note", type=Path, default=DEFAULT_NOTE)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--primary-result", type=Path, default=DEFAULT_PRIMARY_RESULT)
    parser.add_argument("--independent-result", type=Path, default=DEFAULT_INDEPENDENT_RESULT)
    parser.add_argument("--boundary-primary-result", type=Path, default=DEFAULT_BOUNDARY_PRIMARY_RESULT)
    parser.add_argument("--boundary-independent-result", type=Path, default=DEFAULT_BOUNDARY_INDEPENDENT_RESULT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--child-timeout", type=int, default=600)
    args = parser.parse_args()

    rows: list[dict[str, object]] = []

    def add(group: str, name: str, condition: bool, actual: object, expected: object) -> None:
        rows.append({
            "group": group,
            "name": name,
            "status": "PASS" if condition else "FAIL",
            "actual": str(actual),
            "expected": str(expected),
        })

    required_paths = {
        "primary": args.primary_script,
        "independent": args.independent_script,
        "boundary_primary": args.boundary_primary_script,
        "boundary_independent": args.boundary_independent_script,
        "verifier": Path(__file__).resolve(),
        "proof_note": args.note,
        "proof_pdf": args.pdf,
        "manifest": args.manifest,
        "primary_result": args.primary_result,
        "independent_result": args.independent_result,
        "boundary_primary_result": args.boundary_primary_result,
        "boundary_independent_result": args.boundary_independent_result,
    }
    for label, path in required_paths.items():
        add("preflight", f"{label} exists", path.is_file(), path, "existing file")
    if not all(path.is_file() for path in required_paths.values()):
        payload = {
            "schema": "tect/a13-scalar-k2k-four-moment-radau-all-amplitude-integrated/1.0",
            "version": VERSION,
            "status": "FAIL",
            "assertions_total": len(rows),
            "assertions_passed": sum(row["status"] == "PASS" for row in rows),
            "assertions_failed": sum(row["status"] == "FAIL" for row in rows),
            "assertions": rows,
            "failure": "preflight files missing; children were not executed",
        }
        write_json_atomic(args.output, payload)
        print("Integrated R-115 FAIL: preflight files missing", file=sys.stderr)
        return 1

    manifest = load_json(args.manifest)
    pinned_primary = load_json(args.primary_result)
    pinned_independent = load_json(args.independent_result)
    pinned_boundary_primary = load_json(args.boundary_primary_result)
    pinned_boundary_independent = load_json(args.boundary_independent_result)
    add("manifest", "claim id", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    add("manifest", "result id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add("manifest", "tier remains T4", manifest.get("tier_before") == "T4" and manifest.get("tier_after") == "T4", (manifest.get("tier_before"), manifest.get("tier_after")), ("T4", "T4"))
    add("manifest", "repository claim remains incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)

    source_paths = {
        "primary": args.primary_script,
        "independent": args.independent_script,
        "boundary_primary": args.boundary_primary_script,
        "boundary_independent": args.boundary_independent_script,
        "verifier": Path(__file__).resolve(),
        "proof_note": args.note,
    }
    for label, path in source_paths.items():
        entry = manifest.get("sources", {}).get(label, {})
        add("hash-pin", f"{label} path", entry.get("path") == relative(path), entry.get("path"), relative(path))
        add("hash-pin", f"{label} sha256", entry.get("sha256") == digest(path), entry.get("sha256"), digest(path))
    child_paths = {
        "primary": args.primary_result,
        "independent": args.independent_result,
        "boundary_primary": args.boundary_primary_result,
        "boundary_independent": args.boundary_independent_result,
    }
    for label, path in child_paths.items():
        entry = manifest.get("child_results", {}).get(label, {})
        add("hash-pin", f"{label} result path", entry.get("path") == relative(path), entry.get("path"), relative(path))
        add("hash-pin", f"{label} result sha256", entry.get("sha256") == digest(path), entry.get("sha256"), digest(path))

    pdf_entry = manifest.get("proof_pdf", {})
    add("hash-pin", "pdf path", pdf_entry.get("path") == relative(args.pdf), pdf_entry.get("path"), relative(args.pdf))
    add("hash-pin", "pdf sha256", pdf_entry.get("sha256") == digest(args.pdf), pdf_entry.get("sha256"), digest(args.pdf))
    add("hash-pin", "manifest recorded", bool(digest(args.manifest)), digest(args.manifest), "nonempty sha256")

    contract = manifest.get("run_contract", {})
    expected_contract = {
        "primary_evaluations": PRIMARY_EVALUATIONS,
        "primary_accepted_leaves": PRIMARY_LEAVES,
        "primary_pending_leaves": PRIMARY_PENDING,
        "primary_top_level_assertions": 4,
        "independent_structural_polynomials": len(STRUCTURAL_NAMES),
        "independent_structural_leaves": STRUCTURAL_LEAVES,
        "independent_structural_coefficients": STRUCTURAL_COEFFICIENTS,
        "independent_structural_positive": STRUCTURAL_POSITIVE,
        "independent_structural_endpoint_zeros": STRUCTURAL_ZEROS,
        "independent_weight_leaves": WEIGHT_LEAVES,
        "independent_weight_coefficients": WEIGHT_COEFFICIENTS,
        "boundary_coefficients_per_child": BOUNDARY_COEFFICIENTS,
        "boundary_exact_KS_upper_margin": KS_UPPER_MARGIN,
        "boundary_generic_reserve_gap": GENERIC_RESERVE_GAP,
        "independent_A_coefficients": INDEPENDENT_CERTIFICATES["A"][0],
        "independent_minus_B_coefficients": INDEPENDENT_CERTIFICATES["minus_B"][0],
        "independent_A2_minus_DB2_coefficients": INDEPENDENT_CERTIFICATES["A2_minus_DB2"][0],
        "independent_phi_coefficients": sum(value[0] for value in INDEPENDENT_CERTIFICATES.values()),
    }
    for field, expected in expected_contract.items():
        add("contract", field, contract.get(field) == expected, contract.get(field), expected)

    schema_contract = {
        "primary_schema": (pinned_primary, "tect/a13-scalar-k2k-four-moment-radau-all-amplitude-primary/1.0"),
        "independent_schema": (pinned_independent, "tect/a13-scalar-k2k-four-moment-radau-all-amplitude-independent/1.0"),
        "boundary_primary_schema": (pinned_boundary_primary, "tect/a13-scalar-k2k-four-moment-radau-method-boundaries-primary/1.0"),
        "boundary_independent_schema": (pinned_boundary_independent, "tect/a13-scalar-k2k-four-moment-radau-method-boundaries-independent/1.0"),
    }
    for field, (payload, expected) in schema_contract.items():
        observed = (contract.get(field), payload.get("schema"))
        add("contract", field, observed == (expected, expected), observed, (expected, expected))
    integrated_schema = "tect/a13-scalar-k2k-four-moment-radau-all-amplitude-integrated/1.0"
    add(
        "contract",
        "integrated_schema",
        contract.get("integrated_schema") == integrated_schema,
        contract.get("integrated_schema"),
        integrated_schema,
    )

    primary_cover = pinned_primary.get("cover", {})
    add("primary-pinned", "status", pinned_primary.get("status") == "PASS", pinned_primary.get("status"), "PASS")
    add("primary-pinned", "evaluations", primary_cover.get("evaluations") == PRIMARY_EVALUATIONS, primary_cover.get("evaluations"), PRIMARY_EVALUATIONS)
    add("primary-pinned", "accepted leaves", primary_cover.get("accepted_leaves") == PRIMARY_LEAVES, primary_cover.get("accepted_leaves"), PRIMARY_LEAVES)
    add("primary-pinned", "zero pending", primary_cover.get("pending_boxes") == PRIMARY_PENDING, primary_cover.get("pending_boxes"), PRIMARY_PENDING)
    add("primary-pinned", "positive outward margin", positive_ball(primary_cover.get("weakest_outward_lower")), primary_cover.get("weakest_outward_lower"), ">0")
    add("primary-pinned", "self tests", recursively_all_true(pinned_primary.get("assertions", {})), pinned_primary.get("assertions", {}), "all declared assertions true")
    add("primary-pinned", "source digest", pinned_primary.get("environment", {}).get("source_sha256") == digest(args.primary_script), pinned_primary.get("environment", {}).get("source_sha256"), digest(args.primary_script))

    add("independent-pinned", "status", pinned_independent.get("status") == "PASS", pinned_independent.get("status"), "PASS")
    calculus = pinned_independent.get("calculus_bound", {})
    try:
        calculus_ok = arb(str(calculus.get("arb_value"))).upper() < arb(25) / 8
    except (ValueError, TypeError):
        calculus_ok = False
    add("independent-pinned", "calculus constant", calculus_ok, calculus.get("arb_value"), "<25/8")
    structural_raw = pinned_independent.get("structural_certificates", {})
    structural = structural_raw if isinstance(structural_raw, dict) else {}
    structural_totals = certificate_totals(structural)
    add("independent-pinned", "all structural names", set(structural) == STRUCTURAL_NAMES, sorted(structural), sorted(STRUCTURAL_NAMES))
    add(
        "independent-pinned",
        "complete structural coefficient contract",
        structural_totals == (
            STRUCTURAL_LEAVES,
            STRUCTURAL_COEFFICIENTS,
            STRUCTURAL_POSITIVE,
            STRUCTURAL_ZEROS,
            0,
        ),
        structural_totals,
        (STRUCTURAL_LEAVES, STRUCTURAL_COEFFICIENTS, STRUCTURAL_POSITIVE, STRUCTURAL_ZEROS, 0),
    )
    weight = pinned_independent.get("weight_order_joint_certificate", {})
    weight_leaves = weight.get("leaves", []) if isinstance(weight, dict) else []
    weight_ok = (
        isinstance(weight_leaves, list)
        and weight.get("leaf_count") == WEIGHT_LEAVES
        and weight.get("max_depth") == 4
        and len(weight_leaves) == WEIGHT_LEAVES
        and all(exact_leaf_ok(leaf, strict=True) for leaf in weight_leaves)
        and sum(int(leaf["coefficient_count"]) for leaf in weight_leaves) == WEIGHT_COEFFICIENTS
        and tuple(leaf.get("sha256") for leaf in weight_leaves) == WEIGHT_HASHES
    )
    add("independent-pinned", "five-leaf p<=a cover", weight_ok, (weight.get("leaf_count") if isinstance(weight, dict) else None, [leaf.get("sha256") for leaf in weight_leaves] if isinstance(weight_leaves, list) else None), (WEIGHT_LEAVES, list(WEIGHT_HASHES)))
    certificates = pinned_independent.get("phi_certificates", {})
    for label, (count, expected_hash) in INDEPENDENT_CERTIFICATES.items():
        certificate = certificates.get(label, {})
        leaves = certificate.get("leaves", [])
        item = leaves[0] if isinstance(leaves, list) and len(leaves) == 1 and isinstance(leaves[0], dict) else {}
        add("independent-pinned", f"{label} one root leaf", certificate.get("leaf_count") == 1 and certificate.get("max_depth") == 0, (certificate.get("leaf_count"), certificate.get("max_depth")), (1, 0))
        add("independent-pinned", f"{label} coefficient count", item.get("coefficient_count") == count, item.get("coefficient_count"), count)
        add("independent-pinned", f"{label} coefficient hash", item.get("sha256") == expected_hash, item.get("sha256"), expected_hash)
        minimum = item.get("minimum")
        try:
            minimum_ok = int(str(minimum).split("/")[0]) > 0
        except (ValueError, AttributeError):
            minimum_ok = False
        add("independent-pinned", f"{label} positive minimum", minimum_ok, minimum, ">0")

    for label, result, script, schema in (
        ("boundary-primary", pinned_boundary_primary, args.boundary_primary_script, "tect/a13-scalar-k2k-four-moment-radau-method-boundaries-primary/1.0"),
        ("boundary-independent", pinned_boundary_independent, args.boundary_independent_script, "tect/a13-scalar-k2k-four-moment-radau-method-boundaries-independent/1.0"),
    ):
        boundary_ok, boundary_summary = boundary_contract(result)
        add(label, "schema", result.get("schema") == schema, result.get("schema"), schema)
        add(label, "complete exact method-boundary contract", boundary_ok, boundary_summary, "1655 positive signs, exact KS failure inside live time, and reserve-only rational violation")
        add(label, "source digest", result.get("source", {}).get("sha256") == digest(script), result.get("source", {}).get("sha256"), digest(script))

    fresh_primary, primary_stdout, primary_stderr = execute_child(args.primary_script, args.child_timeout)
    fresh_independent, independent_stdout, independent_stderr = execute_child(args.independent_script, args.child_timeout)
    fresh_boundary_primary, boundary_primary_stdout, boundary_primary_stderr = execute_child(args.boundary_primary_script, args.child_timeout)
    fresh_boundary_independent, boundary_independent_stdout, boundary_independent_stderr = execute_child(args.boundary_independent_script, args.child_timeout)
    add("execution", "primary subprocess PASS", fresh_primary.get("status") == "PASS", fresh_primary.get("status"), "PASS")
    add("execution", "independent subprocess PASS", fresh_independent.get("status") == "PASS", fresh_independent.get("status"), "PASS")
    add("execution", "boundary primary subprocess PASS", fresh_boundary_primary.get("status") == "PASS", fresh_boundary_primary.get("status"), "PASS")
    add("execution", "boundary independent subprocess PASS", fresh_boundary_independent.get("status") == "PASS", fresh_boundary_independent.get("status"), "PASS")
    fresh_primary_bytes = json.dumps(fresh_primary, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    fresh_independent_bytes = json.dumps(fresh_independent, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    fresh_boundary_primary_bytes = json.dumps(fresh_boundary_primary, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    fresh_boundary_independent_bytes = json.dumps(fresh_boundary_independent, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    add("execution", "primary fresh equals pinned", hashlib.sha256(fresh_primary_bytes).hexdigest() == digest(args.primary_result), hashlib.sha256(fresh_primary_bytes).hexdigest(), digest(args.primary_result))
    add("execution", "independent fresh equals pinned", hashlib.sha256(fresh_independent_bytes).hexdigest() == digest(args.independent_result), hashlib.sha256(fresh_independent_bytes).hexdigest(), digest(args.independent_result))
    add("execution", "boundary primary fresh equals pinned", hashlib.sha256(fresh_boundary_primary_bytes).hexdigest() == digest(args.boundary_primary_result), hashlib.sha256(fresh_boundary_primary_bytes).hexdigest(), digest(args.boundary_primary_result))
    add("execution", "boundary independent fresh equals pinned", hashlib.sha256(fresh_boundary_independent_bytes).hexdigest() == digest(args.boundary_independent_result), hashlib.sha256(fresh_boundary_independent_bytes).hexdigest(), digest(args.boundary_independent_result))
    add("execution", "primary fresh exact cover", fresh_primary.get("cover", {}).get("evaluations") == PRIMARY_EVALUATIONS and fresh_primary.get("cover", {}).get("accepted_leaves") == PRIMARY_LEAVES and fresh_primary.get("cover", {}).get("pending_boxes") == 0 and positive_ball(fresh_primary.get("cover", {}).get("weakest_outward_lower")), fresh_primary.get("cover", {}), "46714/23613/0 and margin>0")
    fresh_structural_raw = fresh_independent.get("structural_certificates", {})
    fresh_structural = fresh_structural_raw if isinstance(fresh_structural_raw, dict) else {}
    fresh_structural_totals = certificate_totals(fresh_structural)
    add("execution", "independent fresh structural certificate set", set(fresh_structural) == STRUCTURAL_NAMES and fresh_structural_totals == (STRUCTURAL_LEAVES, STRUCTURAL_COEFFICIENTS, STRUCTURAL_POSITIVE, STRUCTURAL_ZEROS, 0), (sorted(fresh_structural), fresh_structural_totals), (sorted(STRUCTURAL_NAMES), (STRUCTURAL_LEAVES, STRUCTURAL_COEFFICIENTS, STRUCTURAL_POSITIVE, STRUCTURAL_ZEROS, 0)))
    fresh_weight = fresh_independent.get("weight_order_joint_certificate", {})
    fresh_weight_leaves = fresh_weight.get("leaves", []) if isinstance(fresh_weight, dict) else []
    fresh_weight_ok = (
        isinstance(fresh_weight_leaves, list)
        and len(fresh_weight_leaves) == WEIGHT_LEAVES
        and all(exact_leaf_ok(leaf, strict=True) for leaf in fresh_weight_leaves)
        and sum(int(leaf["coefficient_count"]) for leaf in fresh_weight_leaves) == WEIGHT_COEFFICIENTS
        and tuple(leaf.get("sha256") for leaf in fresh_weight_leaves) == WEIGHT_HASHES
    )
    add("execution", "independent fresh p<=a cover", fresh_weight_ok, (len(fresh_weight_leaves) if isinstance(fresh_weight_leaves, list) else None, [leaf.get("sha256") for leaf in fresh_weight_leaves] if isinstance(fresh_weight_leaves, list) else None), (WEIGHT_LEAVES, list(WEIGHT_HASHES)))
    fresh_certificates = fresh_independent.get("phi_certificates", {})
    def fresh_count(label: str) -> object:
        leaves = fresh_certificates.get(label, {}).get("leaves")
        if not isinstance(leaves, list) or len(leaves) != 1 or not isinstance(leaves[0], dict):
            return None
        return leaves[0].get("coefficient_count")
    add("execution", "independent fresh exact certificate set", all(fresh_count(label) == count for label, (count, _) in INDEPENDENT_CERTIFICATES.items()), {label: fresh_count(label) for label in INDEPENDENT_CERTIFICATES}, {label: value[0] for label, value in INDEPENDENT_CERTIFICATES.items()})
    for label, result in (("boundary primary", fresh_boundary_primary), ("boundary independent", fresh_boundary_independent)):
        boundary_ok, boundary_summary = boundary_contract(result)
        add("execution", f"{label} fresh exact contract", boundary_ok, boundary_summary, "complete exact method-boundary contract")

    note_text = args.note.read_text(encoding="utf-8")
    for token in NOTE_TOKENS:
        add("note", f"contains {token}", token in note_text, token in note_text, True)
    add("note", "fixed expectation delimiter", r"\E\!left" not in note_text, r"\E\!left" in note_text, False)
    add("note", "devil objections", note_text.count(r"\textbf{Objection:}") >= 6, note_text.count(r"\textbf{Objection:}"), ">=6")
    add("note", "independent algebraic route documented", "25q" in note_text and "2850" in note_text and "11175" in note_text, ("25q" in note_text, "2850" in note_text, "11175" in note_text), (True, True, True))

    reader = PdfReader(str(args.pdf))
    pdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    add("pdf", "page count", pdf_entry.get("pages") == len(reader.pages) and len(reader.pages) >= 8, (pdf_entry.get("pages"), len(reader.pages)), "matching and >=8")
    add("pdf", "size", pdf_entry.get("size_bytes") == args.pdf.stat().st_size, pdf_entry.get("size_bytes"), args.pdf.stat().st_size)
    add("pdf", "render/form gates", pdf_entry.get("form_check") == "PASS" and pdf_entry.get("overfull_hbox_count") == 0 and pdf_entry.get("visual_qa") == "PASS", (pdf_entry.get("form_check"), pdf_entry.get("overfull_hbox_count"), pdf_entry.get("visual_qa")), ("PASS", 0, "PASS"))
    add("pdf", "extracts theorem", "R-115" in pdf_text and "46714" in pdf_text and "Sector A remain open" in pdf_text, ("R-115" in pdf_text, "46714" in pdf_text, "Sector A remain open" in pdf_text), (True, True, True))

    expected_assertion_total = contract.get("integrated_assertions")
    add(
        "contract",
        "integrated assertion total",
        expected_assertion_total == len(rows) + 1,
        expected_assertion_total,
        len(rows) + 1,
    )
    status = "PASS" if all(row["status"] == "PASS" for row in rows) else "FAIL"
    results: dict[str, object] = {
        "result_id": RESULT_ID,
        "primary_cover": {"evaluations": PRIMARY_EVALUATIONS, "accepted_leaves": PRIMARY_LEAVES, "pending": 0},
        "independent_structural_certificate": {
            "polynomials": len(STRUCTURAL_NAMES),
            "leaves": STRUCTURAL_LEAVES,
            "coefficients": STRUCTURAL_COEFFICIENTS,
            "positive": STRUCTURAL_POSITIVE,
            "endpoint_zeros": STRUCTURAL_ZEROS,
        },
        "independent_weight_certificate": {"leaves": WEIGHT_LEAVES, "coefficients": WEIGHT_COEFFICIENTS},
        "independent_exact_coefficients": {label: value[0] for label, value in INDEPENDENT_CERTIFICATES.items()},
        "primary_result_sha256": digest(args.primary_result),
        "independent_result_sha256": digest(args.independent_result),
        "boundary_primary_result_sha256": digest(args.boundary_primary_result),
        "boundary_independent_result_sha256": digest(args.boundary_independent_result),
        "method_boundaries": {
            "fifth_order_exact_coefficients_per_child": BOUNDARY_COEFFICIENTS,
            "exact_KS_upper_margin": KS_UPPER_MARGIN,
            "generic_reserve_only_gap": GENERIC_RESERVE_GAP,
        },
        "manifest_sha256": digest(args.manifest),
        "proof_note_sha256": digest(args.note),
        "proof_pdf_sha256": digest(args.pdf),
        "scalar_all_amplitude_closed": True,
        "full_a1_embedding": False,
        "one_use_source_sextic_aggregation": False,
        "sector_a_closed": False,
    }
    payload: dict[str, object] = {
        "schema": "tect/a13-scalar-k2k-four-moment-radau-all-amplitude-integrated/1.0",
        "version": VERSION,
        "status": status,
        "assertions_total": len(rows),
        "assertions_passed": sum(row["status"] == "PASS" for row in rows),
        "assertions_failed": sum(row["status"] == "FAIL" for row in rows),
        "assertion_names": [f"{row['group']}::{row['name']}" for row in rows],
        "assertions": rows,
        "results": results,
        "results_sha256": hashlib.sha256(json.dumps(results, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
    }
    write_json_atomic(args.output, payload)
    print(f"Integrated R-115 {status}: {payload['assertions_passed']}/{payload['assertions_total']} assertions")
    print(f"primary cover {PRIMARY_EVALUATIONS}/{PRIMARY_LEAVES}/0; independent structural/weight/Phi signs {STRUCTURAL_COEFFICIENTS}+{WEIGHT_COEFFICIENTS}+2850+2145+11175")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
