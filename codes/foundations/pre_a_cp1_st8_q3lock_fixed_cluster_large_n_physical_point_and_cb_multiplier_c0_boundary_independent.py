#!/usr/bin/env python3
"""Non-importing standard-library audit for the R-167 v2.8 package."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import sys
import tempfile
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
PRIMARY = SCRIPT.with_name(SCRIPT.name.replace("_independent.py", ".py"))
SLUG = "pre-a-cp1-st8-q3lock-fixed-cluster-large-n-physical-point-and-cb-multiplier-c0-boundary"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
GATES = REPO / "claims/GATES.md"
RESULTS = REPO / "RESULTS-LEDGER.md"
NEGATIVES = REPO / "negative-results/registry.md"
EXPLORATIONS = REPO / "explorations/log.jsonl"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-independent-{SLUG}/result.json"

CLOSED_GATE = "PA-CP1-ST8-Q3LOCK-ZERO-SOURCE-FIXED-COMPLETE-SPECTRAL-CLUSTER-RITZ-LARGE-N-PHYSICAL-LAMBDA-ONE-LOCAL-SW-STRETCHED-EXPONENTIAL-EXTENSIVE-REMAINDER"
NEGATIVE_ID = "NG-2026-08-13-PRE-A-ST8-Q3LOCK-NONCONSTANT-CB-CONFIGURATION-MULTIPLIER-FULL-HAMILTONIAN-POINT-NORM-C0"


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def derive_fixture() -> dict[str, Any]:
    coordination = 6
    onsite_dimension = 8
    coordinate_offset = Fraction(5, 4)
    coordinate_constant = onsite_dimension * coordinate_offset
    bond_base = 2 * coordinate_constant
    strength_ceiling = coordination * bond_base + 1
    smallness_factor = 32 * strength_ceiling
    order_denominator = 8 * strength_ceiling
    envelope_prefactor = 16 * strength_ceiling
    lattice_scale = 74
    quarter_scale = lattice_scale * lattice_scale // 4
    quarter_threshold = smallness_factor // 4
    square_margin = quarter_scale * quarter_scale - 2 * quarter_threshold * quarter_threshold

    # x^2=N^2/(968 sqrt(2)); exact comparisons show 4<=x^2<9.
    lower_order_test = lattice_scale**4 > 2 * (2**4) * order_denominator**2
    upper_order_test = lattice_scale**4 < 2 * (3**4) * order_denominator**2
    n_star = 2 if lower_order_test and upper_order_test else -1
    rho_coefficient = Fraction(lattice_scale * lattice_scale, n_star * n_star)
    # rho=rho_coefficient/sqrt(2), so ratio=J*sqrt(2)/rho_coefficient.
    ratio_square = Fraction(strength_ceiling**2 * 2, rho_coefficient**2)
    fixed_order = 2 * strength_ceiling * ratio_square
    return {
        "coordinate_constant": coordinate_constant,
        "bond_base": bond_base,
        "strength_ceiling": strength_ceiling,
        "smallness_factor": smallness_factor,
        "order_denominator": order_denominator,
        "envelope_prefactor": envelope_prefactor,
        "square_margin": square_margin,
        "n_star": n_star,
        "rho_coefficient": rho_coefficient,
        "ratio_square": ratio_square,
        "fixed_order": fixed_order,
    }


def derive_cosine_fixture() -> dict[str, Any]:
    getcontext().prec = 50
    log_two = Decimal(2).ln()
    variance = 2 * log_two
    gaussian_multiplier = (-variance / 2).exp()
    left = gaussian_multiplier
    right = -gaussian_multiplier
    range_supremum = Decimal(1)
    range_infimum = -Decimal(1)
    return {
        "variance": variance,
        "left": left,
        "right": right,
        "gap": left - right,
        "oscillation": range_supremum - range_infimum,
    }


def exploration_exists() -> bool:
    if not EXPLORATIONS.exists():
        return False
    matches = []
    for line in EXPLORATIONS.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("id") == "EXP-000831":
            matches.append(record)
    return len(matches) == 1


def run(staged: bool = False) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    audit = Audit()

    imports: set[str] = set()
    forbidden_calls: list[str] = []
    allowed_imports = {
        "__future__",
        "argparse",
        "ast",
        "decimal",
        "fractions",
        "hashlib",
        "json",
        "math",
        "os",
        "pathlib",
        "sys",
        "tempfile",
        "typing",
    }
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {
                "__import__",
                "compile",
                "eval",
                "exec",
            }:
                forbidden_calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute) and node.func.attr in {
                "exec_module",
                "import_module",
                "load_module",
            }:
                forbidden_calls.append(node.func.attr)
    independent = (
        imports == allowed_imports
        and imports.issubset(set(sys.stdlib_module_names) | {"__future__"})
        and PRIMARY.stem not in imports
        and not forbidden_calls
    )
    audit.check(
        "stdlib non-importing engine",
        independent,
        {"imports": sorted(imports), "forbidden_calls": sorted(forbidden_calls)},
        {"imports": sorted(allowed_imports), "forbidden_calls": []},
        "independence",
    )

    audit.check("exact package identity", manifest["result_version"] == "v2.8" and manifest["exploration_id"] == "EXP-000831", (manifest["result_version"], manifest["exploration_id"]), ("v2.8", "EXP-000831"), "identity")
    audit.check("continuation identity", manifest["continues_exploration_id"] == "EXP-000828", manifest["continues_exploration_id"], "EXP-000828", "identity")
    audit.check("exact gate and negative", manifest["closed_gate_id"] == CLOSED_GATE and manifest["negative_ids"] == [NEGATIVE_ID], (manifest["closed_gate_id"], manifest["negative_ids"]), (CLOSED_GATE, [NEGATIVE_ID]), "identity")

    fixture = derive_fixture()
    expected = {
        "coordinate_constant": Fraction(10),
        "bond_base": Fraction(20),
        "strength_ceiling": Fraction(121),
        "smallness_factor": Fraction(3872),
        "order_denominator": Fraction(968),
        "envelope_prefactor": Fraction(1936),
        "square_margin": 113,
        "n_star": 2,
        "rho_coefficient": Fraction(1369),
        "ratio_square": Fraction(2 * 121**2, 1369**2),
        "fixed_order": Fraction(7086244, 1874161),
    }
    for key, oracle in expected.items():
        audit.check(f"exact fixture {key}", fixture[key] == oracle, fixture[key], oracle, "fixture")
    audit.check("ratio below one eighth", fixture["ratio_square"] < Fraction(1, 64), fixture["ratio_square"], "<1/64", "fixture")
    audit.check("manifest exact fixed-order oracle", manifest["exact_fixture"]["fixed_order_bound"] == f"{fixture['fixed_order']} |Lambda|", manifest["exact_fixture"]["fixed_order_bound"], f"{fixture['fixed_order']} |Lambda|", "fixture")

    cosine = derive_cosine_fixture()
    tolerance = Decimal("1e-45")
    audit.check("Gaussian cosine left", abs(cosine["left"] - Decimal("0.5")) < tolerance, cosine["left"], Decimal("0.5"), "multiplier")
    audit.check("Gaussian cosine right", abs(cosine["right"] + Decimal("0.5")) < tolerance, cosine["right"], Decimal("-0.5"), "multiplier")
    audit.check("Gaussian cosine gap", abs(cosine["gap"] - Decimal(1)) < tolerance, cosine["gap"], Decimal(1), "multiplier")
    audit.check("real oscillation", cosine["oscillation"] == Decimal(2), cosine["oscillation"], Decimal(2), "multiplier")

    tokens = (
        CLOSED_GATE,
        NEGATIVE_ID,
        "H_(M,N)(1)=Pi_Lambda[H_N-|Lambda|epsilon_(0,N)]Pi_Lambda",
        "whole finite-dimensional\nonsite Ritz Hilbert space",
        "rank two",
        "D_M>e_well+C_M",
        "Rerun the BDL Proposition 4.2/Lemma 4.2 majorant",
        "7086244/1874161",
        "diam f(R^d)",
        "osc(f)",
        "strictly strengthens",
        "No per-lemma or intermediate v2.8 PDF is issued",
    )
    audit.check("certificate semantic ledger", all(token in certificate for token in tokens), [token for token in tokens if token not in certificate], [], "certificate")
    audit.check("deferred lifecycle", manifest["checkpoint_synthesis"]["pdf_issued"] is False and manifest["checkpoint_synthesis"]["status"].startswith("DEFERRED"), manifest["checkpoint_synthesis"], "deferred and no PDF", "scope")
    audit.check("five parents remain open", len(manifest["gate_resolution"]["retained_open_parents"]) == 5 and "All five parent gates remain OPEN" in certificate, manifest["gate_resolution"]["retained_open_parents"], "five open parents", "scope")

    if not staged:
        formal = exploration_exists() and CLOSED_GATE in GATES.read_text(encoding="utf-8") and NEGATIVE_ID in NEGATIVES.read_text(encoding="utf-8")
        results = RESULTS.read_text(encoding="utf-8")
        formal = formal and "R-167 v2.8" in results and "EXP-000831" in results
        audit.check("formal authorities present", formal, formal, True, "formal")

    return {
        "schema": f"tect/{SLUG}-independent-result/1.0",
        "script_version": __version__,
        "result_number": "R-167",
        "result_version": "v2.8",
        "verdict": "PASS",
        "summary": {"passed": len(audit.rows), "failed": 0, "total": len(audit.rows)},
        "derived": {
            "large_n_fixture": {key: str(value) for key, value in fixture.items()},
            "multiplier_fixture": {key: str(value) for key, value in cosine.items()},
            "uniform_in_M": False,
            "full_oscillator_cutoff_removed": False,
            "standard_sw_growing_order": False,
            "common_alpha_closed": False,
        },
        "source_hashes": {
            path.relative_to(REPO).as_posix(): normalized_sha256(path)
            for path in (SCRIPT, PRIMARY, MANIFEST, CERTIFICATE)
        },
        "assertions": audit.rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run(staged=args.staged)
    if not args.self_test and not args.no_store:
        atomic_json(args.output, payload)
    print(f"INDEPENDENT PASS {payload['summary']['passed']}/{payload['summary']['total']}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
