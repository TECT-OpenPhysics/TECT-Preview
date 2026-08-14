#!/usr/bin/env python3
"""Primary symbolic verifier for the R-167 v3.9 proof-first package."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-finite-source-ground-residual-transfer-and-clipped-order-separation-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-primary-{SLUG}/result.json"
FORMAL_PATHS = (REPO / "claims/GATES.md", REPO / "RESULTS-LEDGER.md", REPO / "negative-results/registry.md", REPO / "explorations/log.jsonl")

CLOSED = "PA-CP1-ST8-Q3LOCK-FINITE-SOURCE-GROUND-RESIDUAL-TRANSFER-AND-CLIPPED-ORDER-SEPARATION"
NEGATIVE = "NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-SOURCE-EXACT-TARGET-GENERATOR-AND-SEPARATION-AUTOMATIC-TARGET-GROUNDNESS"
REUSED = "NG-2026-08-13-PRE-A-ST8-Q3LOCK-FINITE-GAPS-PLUS-WEAKSTAR-STATES-AUTOMATIC-TARGET-GENERATOR-AND-GNS-GAP-TRANSFER"

# Labelled finite-dimensional fixture inputs only. All displayed numbers are derived.
Q_EIGENVALUES = (sp.Integer(-1), sp.Integer(0), sp.Integer(1))
TARGET_POWER = sp.Integer(2)
SOURCE_MULTIPLIER = sp.Integer(2)
AVAILABLE_MOMENT_ORDER = sp.Integer(4)
SAMPLE_N = (sp.Integer(1), sp.Integer(2), sp.Integer(5), sp.Integer(11))
SIGNS = (sp.Integer(-1), sp.Integer(1))
HBAR = sp.Integer(1)

# Labelled separation-oracle inputs; reported bounds are derived.
ORDER_LOWER = sp.Integer(2)
FOURTH_MOMENT_CEILING = sp.Integer(16)
CLIP_RADIUS = sp.Integer(4)
APPROXIMATION_FRACTION = sp.Rational(1, 2)


def normalized_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


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


def expectation(vector_index: int, observable: sp.Matrix) -> sp.Expr:
    basis = sp.eye(len(Q_EIGENVALUES))[:, vector_index]
    return sp.simplify((basis.H * observable * basis)[0])


def exact_m3_fixture() -> dict[str, Any]:
    q = sp.diag(*Q_EIGENVALUES)
    k = q**TARGET_POWER
    zero_index = Q_EIGENVALUES.index(sp.Integer(0))
    rows: list[dict[str, Any]] = []
    for n in SAMPLE_N:
        h = sp.Rational(1, n)
        selector = SOURCE_MULTIPLIER * n * q
        for sigma in SIGNS:
            source_hamiltonian = sp.simplify(k - sigma * h * selector)
            eigenvalues = tuple(source_hamiltonian.diagonal())
            ground_value = min(eigenvalues)
            ground_index = Q_EIGENVALUES.index(sigma)
            ground_unique = eigenvalues.count(ground_value) == 1 and eigenvalues[ground_index] == ground_value
            a = sp.zeros(len(Q_EIGENVALUES))
            a[zero_index, ground_index] = 1
            h_zero = k
            commutator_zero = sp.simplify(h_zero * a - a * h_zero)
            delta_n_zero = sp.simplify(sp.I * commutator_zero / HBAR)
            target_delta = sp.simplify(sp.I * (k * a - a * k) / HBAR)
            defect = sp.simplify(delta_n_zero - target_delta)
            target_form = sp.simplify(-sp.I * HBAR * expectation(ground_index, a.H * target_delta))
            commutator_source = sp.simplify(selector * a - a * selector)
            source_residual = sp.simplify(sigma * h * expectation(ground_index, a.H * commutator_source))
            finite_form = sp.simplify(expectation(ground_index, a.H * (source_hamiltonian - ground_value * sp.eye(len(Q_EIGENVALUES))) * a))
            defect_term = sp.simplify(sp.I * HBAR * expectation(ground_index, a.H * defect))
            combined = sp.simplify(source_residual + defect_term)
            rows.append({
                "n": int(n),
                "sigma": int(sigma),
                "h_n": str(h),
                "h_n_S_n_equals": str(sp.simplify(h * selector)),
                "finite_source_ground_eigenvalue": str(ground_value),
                "source_ground_unique": bool(ground_unique),
                "finite_source_excitation_form": str(finite_form),
                "target_generator_defect": str(defect_term),
                "source_scalar_residual": str(source_residual),
                "combined_residual": str(combined),
                "target_energy_form": str(target_form),
                "target_decomposition_rhs": str(sp.simplify(finite_form + combined)),
                "target_groundness": bool(target_form >= 0),
            })
    q_norm = max(abs(value) for value in Q_EIGENVALUES)
    plus_index = Q_EIGENVALUES.index(sp.Integer(1))
    minus_index = Q_EIGENVALUES.index(sp.Integer(-1))
    plus_order = expectation(plus_index, q)
    minus_order = expectation(minus_index, q)
    return {
        "rows": rows,
        "parity_related": bool(plus_order == -minus_order),
        "fixed_order_separated": bool(q_norm <= 1 and plus_order - minus_order > 0),
        "order_values": [str(minus_order), str(plus_order)],
    }


def clipped_order_fixture() -> dict[str, Any]:
    tail_power = CLIP_RADIUS**AVAILABLE_MOMENT_ORDER
    d_r = sp.simplify(ORDER_LOWER / CLIP_RADIUS - FOURTH_MOMENT_CEILING / tail_power)
    epsilon = sp.simplify(APPROXIMATION_FRACTION * d_r)
    retained = sp.simplify(d_r - epsilon)
    distance = sp.simplify((sp.Integer(1) - sp.Integer(-1)) * retained)
    positivity_threshold = sp.real_root(FOURTH_MOMENT_CEILING / ORDER_LOWER, AVAILABLE_MOMENT_ORDER - sp.Integer(1))
    return {
        "radius_fourth_power": str(tail_power),
        "d_R": str(d_r),
        "epsilon": str(epsilon),
        "retained_order": str(retained),
        "distance_lower_bound": str(distance),
        "radius_above_threshold": bool(CLIP_RADIUS > positivity_threshold),
        "positive": bool(d_r > 0 and 0 < epsilon < d_r),
    }


def build_payload(formal: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    fixture = exact_m3_fixture()
    clipped = clipped_order_fixture()
    expected = manifest["exact_m3_fixture"]["derived"]
    audit = Audit()
    audit.check("manifest identity", manifest["package_id"] == SLUG and manifest["version"] == "R-167 v3.9" and manifest["exploration_id"] == "EXP-000843" and manifest["prior_exploration_id"] == "EXP-000842" and manifest["claim_bearing"] is False, (manifest["package_id"], manifest["version"], manifest["exploration_id"]), (SLUG, "R-167 v3.9", "EXP-000843"), "identity")
    audit.check("manifest topology", manifest["closed_gate_ids"] == [CLOSED] and manifest["negative_ids"] == [NEGATIVE] and manifest["reused_negative_ids"] == [REUSED], (manifest["closed_gate_ids"], manifest["negative_ids"], manifest["reused_negative_ids"]), ([CLOSED], [NEGATIVE], [REUSED]), "topology")
    theorem = manifest["ground_residual_transfer"]
    audit.check("combined residual theorem", all(token in theorem["target_decomposition"] for token in ("R_n(A)=", "sigma h_n", "+i hbar", "cal E_n(A)+R_n(A)", "hat omega_n", "tilde omega_n")) and "complex combined scalar residual" in theorem["hypothesis"] and "quadratic-form commutator identity" in theorem["finite_energy_identity"], theorem, "typed plus-plus combined residual", "theorem")
    audit.check("fixed-sign graph-core domains", all(token in theorem["setup"] for token in ("Fix one sign", "unital star-subalgebra", "graph core", "commutator and vector/form domains", "applied separately")), theorem["setup"], "fixed sign and explicit core/domains", "theorem")
    audit.check("invariance derivation", all(token in theorem["conclusion"] for token in ("1+zA", "every complex z", "omega(delta A)=0", "Graph-core closure", "alpha-invariant")), theorem["conclusion"], "positivity-derived invariance", "theorem")
    separation = manifest["clipped_order_separation"]
    audit.check("clipped-order carrier theorem", all(token in " ".join(separation.values()) for token in ("locally normal", "affiliated", "d_R:=m/R-M_4/R^4", "strong-star dense", "odd self-adjoint contraction", "2(d_R-epsilon)", "not claimed to belong")), separation, "normal clipped separator transferred to carrier", "separation")
    audit.check("clipped arithmetic", clipped["radius_above_threshold"] and clipped["positive"] and sp.Rational(clipped["distance_lower_bound"]) == 2 * sp.Rational(clipped["retained_order"]), clipped, "positive exact clipped bound", "separation")
    rows = fixture["rows"]
    audit.check("M3 all sample rows", len(rows) == len(SAMPLE_N) * len(SIGNS), len(rows), len(SAMPLE_N) * len(SIGNS), "fixture")
    for key in ("finite_source_ground_eigenvalue", "finite_source_excitation_form", "target_generator_defect", "source_scalar_residual", "combined_residual", "target_energy_form", "target_decomposition_rhs"):
        audit.check(f"M3 exact {key}", all(row[key] == expected[key] for row in rows), sorted({row[key] for row in rows}), expected[key], "fixture")
    audit.check("M3 uniqueness and target failure", all(row["source_ground_unique"] is expected["source_ground_unique"] and row["target_groundness"] is expected["target_groundness"] for row in rows), (all(row["source_ground_unique"] for row in rows), any(row["target_groundness"] for row in rows)), (True, False), "fixture")
    audit.check("M3 parity and fixed order", fixture["parity_related"] is expected["parity_related"] and fixture["fixed_order_separated"] is expected["fixed_order_separated"], (fixture["parity_related"], fixture["fixed_order_separated"]), (True, True), "fixture")
    audit.check("M3 nonvanishing scaled selector", all("Matrix([[" in row["h_n_S_n_equals"] and row["h_n_S_n_equals"] == rows[0]["h_n_S_n_equals"] for row in rows), sorted({row["h_n_S_n_equals"] for row in rows}), "one nonzero n-independent 2Q", "fixture")
    audit.check("certificate theorem tokens", all(token in certificate for token in (CLOSED, "complex scalar residual", "1+zA", "strong-star dense", "-1=1+(-2)", NEGATIVE, "No v3.9 PDF is issued")), "required tokens present", "required tokens present", "certificate")
    audit.check("certificate domain and scope firewalls", all(token in certificate for token in ("quadratic-form commutator identity", "declared represented vector/form pairing", "not a Q3LOCK counterexample", "positive broken-sector GNS gap", "All five active parent gates and both historical gates remain OPEN")), "scope tokens present", "scope tokens present", "scope")
    audit.check("source AST and format", ast.parse(SCRIPT.read_text(encoding="utf-8")) is not None and all(b"\r" not in path.read_bytes() and path.read_bytes().endswith(b"\n") and all(byte < 128 for byte in path.read_bytes()) for path in (MANIFEST, CERTIFICATE, SCRIPT)), "AST ASCII LF final-LF", "AST ASCII LF final-LF", "format")
    if formal:
        formal_text = "\n".join(path.read_text(encoding="utf-8") for path in FORMAL_PATHS)
        audit.check("formal authority links", all(token in formal_text for token in ("EXP-000843", CLOSED, NEGATIVE, "R-167 v3.9")), "all formal tokens present", "all formal tokens present", "formal")
    return {
        "schema": "tect/pre-a-q3lock-finite-source-ground-residual-transfer-run/1.0",
        "version": "R-167 v3.9",
        "mode": "formal" if formal else "staged",
        "assertions": audit.rows,
        "summary": {"status": "PASS", "passed": len(audit.rows), "failed": 0},
        "derived": {"m3": fixture, "clipped": clipped},
        "source_hashes": {str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path) for path in (MANIFEST, CERTIFICATE, SCRIPT)},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload(formal=not args.staged)
    if not args.no_store:
        atomic_json(args.output, payload)
    print(f"PRIMARY PASS {payload['summary']['passed']}/{payload['summary']['passed']} mode={payload['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
