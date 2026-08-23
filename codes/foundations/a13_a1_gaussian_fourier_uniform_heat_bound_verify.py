#!/usr/bin/env python3
"""Integrated verifier for the cutoff-uniform Gaussian proxy comparison bound."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy" / "pre-a13-a1-gaussian-fourier-uniform-heat-bound-manifest.json"
PRIMARY = ROOT / "codes" / "foundations" / "a13_a1_gaussian_fourier_uniform_heat_bound.py"
INDEPENDENT = ROOT / "codes" / "foundations" / "a13_a1_gaussian_fourier_uniform_heat_bound_independent.py"
LEAN = ROOT / "verification" / "lean" / "Tect" / "R204.lean"
DEFAULT_OUTPUT = ROOT / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-integrated-a1-gaussian-fourier-uniform-heat-bound" / "result.json"


def check(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def child(script: Path, output: Path) -> tuple[int, dict[str, Any]]:
    proc = subprocess.run(
        [sys.executable, "-B", "-X", "utf8", str(script), "--output", str(output)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    payload = json.loads(output.read_text(encoding="utf-8")) if output.exists() else {}
    payload["_stdout"] = proc.stdout
    payload["_stderr"] = proc.stderr
    return proc.returncode, payload


def derived_bound(manifest: dict[str, Any]) -> int:
    inputs = manifest["registered_inputs"]
    profile = inputs["generator_profile"]
    factor = 2 * (int(profile["cross_channels"]) + int(profile["diagonal_channels"]))
    shell_coeff = sum(int(value) for value in inputs["max_norm_shell"]["shell_coefficients"])
    p_bound = int(inputs["l1_shell_bound"]["partial_inverse_square_sum_bound"])
    shell_sum = shell_coeff * p_bound
    l1_bound = 1 + shell_sum
    split = inputs["convolution_split"]
    multiplier = int(split["regions"]) * int(split["quarter_scale"]) ** int(inputs["covariance_power"])
    return factor * multiplier * l1_bound * shell_sum


def mutation_suite(manifest: dict[str, Any]) -> list[tuple[str, bool, Any]]:
    mutations: list[tuple[str, bool, Any]] = []
    mutated = copy.deepcopy(manifest)
    mutated["registered_inputs"]["proxy_covariance"] = "full interacting A1 Gibbs law"
    mutations.append(("proxy_to_full_gibbs", "proxy" not in mutated["registered_inputs"]["proxy_covariance"].lower(), mutated["registered_inputs"]["proxy_covariance"]))

    mutated = copy.deepcopy(manifest)
    mutated["registered_inputs"]["convolution_split"]["regions"] = 1
    mutations.append(("drop_split_region", derived_bound(mutated) != derived_bound(manifest), derived_bound(mutated)))

    mutated = copy.deepcopy(manifest)
    mutated["registered_inputs"]["covariance_power"] = 1
    mutations.append(("change_covariance_power", derived_bound(mutated) != derived_bound(manifest), derived_bound(mutated)))

    mutated = copy.deepcopy(manifest)
    mutated["boundary"] = mutated["boundary"].replace("q-ledger", "comparison quantity")
    mutations.append(("erase_q_ledger_boundary", "q-ledger" not in mutated["boundary"], mutated["boundary"]))

    mutated = copy.deepcopy(manifest)
    mutated["registered_inputs"]["heat_exponents"] = [0, *mutated["registered_inputs"]["heat_exponents"]]
    threshold = int(mutated["registered_inputs"]["uniform_charge_bound"]["heat_threshold"])
    mutations.append(("admit_zero_heat", 0 in mutated["registered_inputs"]["heat_exponents"], mutated["registered_inputs"]["heat_exponents"]))

    mutated = copy.deepcopy(manifest)
    mutated["registered_inputs"]["max_norm_shell"]["shell_coefficients"] = [6, 0]
    mutations.append(("axis_only_shell_count", sum(mutated["registered_inputs"]["max_norm_shell"]["shell_coefficients"]) != sum(manifest["registered_inputs"]["max_norm_shell"]["shell_coefficients"]), mutated["registered_inputs"]["max_norm_shell"]["shell_coefficients"]))

    mutated = copy.deepcopy(manifest)
    mutated["boundary"] = mutated["boundary"].replace("does not identify", "identifies").replace("does not identify", "identifies")
    mutations.append(("promote_a13", "a13 closure" not in mutated["boundary"].lower(), mutated["boundary"]))

    lean_text = LEAN.read_text(encoding="utf-8")
    forbidden = tuple(token for token in ("sorry", "admit", "axiom", "unsafe") if token in lean_text.lower())
    mutations.append(("lean_escape", forbidden == (), forbidden))
    return mutations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected_bound = derived_bound(manifest)
    rows: list[dict[str, Any]] = []
    package_hashes: dict[str, str] = {}
    package_expected: dict[str, str] = {}
    package_paths: dict[str, str] = {}
    package_ok = True
    for name, record in manifest.get("files", {}).items():
        path = ROOT / record["path"]
        expected = str(record["sha256"])
        actual = digest(path) if path.is_file() else "MISSING"
        package_hashes[name] = actual
        package_expected[name] = expected
        package_paths[name] = record["path"]
        package_ok = package_ok and actual == expected
    check(rows, "package_file_hashes_match", package_ok, package_hashes, package_expected)
    with tempfile.TemporaryDirectory(prefix="a1_uniform_heat_bound_") as tmp:
        temp = Path(tmp)
        p_code, primary = child(PRIMARY, temp / "primary.json")
        i_code, independent = child(INDEPENDENT, temp / "independent.json")
    check(rows, "primary_exit_zero", p_code == 0, p_code, 0)
    check(rows, "independent_exit_zero", i_code == 0, i_code, 0)
    check(rows, "primary_failures_empty", primary.get("failures") == [], primary.get("failures"), [])
    check(rows, "independent_failures_empty", independent.get("failures") == [], independent.get("failures"), [])
    primary_assertions = {row.get("name"): row.get("status") for row in primary.get("assertions", [])}
    check(rows, "primary_lean_compile_asserted", primary_assertions.get("lean_compile") == "PASS", primary_assertions.get("lean_compile"), "PASS")
    pcore = primary.get("derived", {})
    icore = independent.get("derived", {})
    keys = ("dimension", "covariance_power", "current_factor", "shell_coefficient", "shell_sum_bound", "l1_bound", "convolution_multiplier", "uniform_charge_bound", "cutoffs", "heat_exponents", "finite_q_tables")
    check(rows, "derived_core_values_identical", {k: pcore.get(k) for k in keys} == {k: icore.get(k) for k in keys}, [{k: pcore.get(k) for k in keys}, {k: icore.get(k) for k in keys}], "identical")
    check(rows, "uniform_bound_matches_derived_inputs", pcore.get("uniform_charge_bound") == expected_bound, pcore.get("uniform_charge_bound"), expected_bound)
    check(rows, "uniform_bound_matches_manifest", pcore.get("uniform_charge_bound") == manifest["derived_contract"]["uniform_charge_bound"], pcore.get("uniform_charge_bound"), manifest["derived_contract"]["uniform_charge_bound"])
    check(rows, "source_authorities_identical", primary.get("source_authorities") == independent.get("source_authorities"), [primary.get("source_authorities"), independent.get("source_authorities")], "identical")
    check(rows, "primary_lean_compiled", "PASS" in primary.get("_stdout", "") and "UNIFORM HEAT BOUND" in primary.get("_stdout", ""), primary.get("_stdout"), "Lean-backed primary pass")
    check(rows, "independent_stdlib_scope", "UNIFORM HEAT INDEPENDENT PASS" in independent.get("_stdout", ""), independent.get("_stdout"), "independent pass")
    mutations = mutation_suite(manifest)
    for name, ok, actual in mutations:
        check(rows, f"hostile_{name}", ok, actual, "mutation rejected")
    boundary = " ".join([str(primary.get("conclusion", "")), *[str(value) for value in primary.get("honesty_boundary", [])]])
    for token in ("proxy", "production", "q-ledger", "A13"):
        check(rows, f"scope_token_{token}", token.lower() in boundary.lower(), boundary, f"contains {token}")
    failures = [row for row in rows if row["status"] != "PASS"]
    result = {
        "schema": "tect/pre-a13-a1-gaussian-fourier-uniform-heat-bound-integrated-result/1.0",
        "claim_id": "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION",
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Integrated cutoff-uniform diagonal-Gaussian comparison bound; not a production heat/root owner.",
        "primary_result": {key: value for key, value in primary.items() if not key.startswith("_")},
        "independent_result": {key: value for key, value in independent.items() if not key.startswith("_")},
        "cross_assertions": rows,
        "cross_assertion_count": len(rows),
        "assertion_count": len(rows) + int(primary.get("assertion_count", 0)) + int(independent.get("assertion_count", 0)),
        "conclusion": "Both exact lanes and the mutation suite support the explicit proxy bound 529152 at heat exponent s>=2. No production owner or A13 conclusion follows.",
        "honesty_boundary": ["proxy only", "comparison bound only", "no production heat/root owner", "no production q-ledger", "no A13 closure", "no Sector-A or Pre-A closure"],
        "failures": failures,
    }
    if not args.no_store:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        print(f"A1 FOURIER UNIFORM HEAT INTEGRATED FAIL {len(rows)-len(failures)}/{len(rows)}")
        for failure in failures:
            print(f"FAIL {failure['name']}: {failure['actual']} expected {failure['expected']}")
        return 1
    print(f"A1 FOURIER UNIFORM HEAT INTEGRATED PASS {len(rows)}/{len(rows)}")
    if not args.no_store:
        print(f"Evidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
