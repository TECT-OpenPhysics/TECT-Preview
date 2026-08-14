#!/usr/bin/env python3
"""Independently verify the R-167 v4.0 exact-Q3 ground-pair arithmetic.

Convention: ``V=L^3``, ``H_L(sigma h)=H_L(0)-sigma h S_L``, and all oracle
arithmetic is exact stdlib rational arithmetic.  The checked formulas are
``eta+h_L(V m-sigma s)<=C_e/V`` and ``|R_L^sigma(A)|=O(h_L V)->0``.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-mesoscopic-source-ground-orbit-smear-transfer-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-independent-{SLUG}/result.json"

CLOSED = "PA-CP1-ST8-Q3LOCK-MESOSCOPIC-SOURCE-EXACT-GROUND-RESIDUAL-CLOSURE-AND-ZERO-SOURCE-ORBIT-SMEAR-GROUND-PAIR"
REUSED = [
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-SOURCE-EXACT-TARGET-GENERATOR-AND-SEPARATION-AUTOMATIC-TARGET-GROUNDNESS",
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-SOURCE-AUTOMATIC-ZERO-SOURCE-QUOTIENT-FACTORIZATION",
    "NG-2026-08-12-PRE-A-ST8-Q3LOCK-ORBIT-SMEAR-SEED-SUPPORT-AUTOMATIC-SPATIAL-LOCAL-NET",
]

# Independent labelled inputs matching the primary audit, not its derived values.
RHO_STAR = Fraction(8)
HBAR = Fraction(2)
CHI = Fraction(1)
H_STAR = Fraction(3)
SOURCE_POWER = Fraction(3, 2)
G_COUPLING = Fraction(16)
GAMMA = Fraction(1, 4)
WEIGHT_A = Fraction(2)
A_S = Fraction(3)
C_GAMMA = Fraction(5)
ARVESON_RADIUS = Fraction(2)
SMEAR_TIME = Fraction(5)
WITNESS_R = Fraction(1, 16)

ENERGIES = (Fraction(0), Fraction(3), Fraction(7))
ENERGY_WEIGHTS = (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))
TRANSITIONS = ((0, 1), (1, 2))

# Explicit test oracles. The stdlib path still derives every value independently.
TEST_ORACLE_WINDOW = {
    "source_power": "3/2",
    "hV2_power": "1/2",
    "hV_power": "-1/2",
    "order_correction_power": "-1/2",
    "eta_source_power": "-1/2",
    "eta_dominant_power": "-1/2",
    "root_inside_power": "2",
    "root_power": "1",
    "residual_power": "-1/2",
    "smear_error_power": "-1/4",
    "order_limit": "2",
    "eta_limit": "0",
    "residual_limit": "0",
    "smear_error_limit": "0",
}
TEST_ORACLE_COERCIVITY = {
    "B_a": "33/2",
    "C_4": "32",
    "C_e": "1/4",
    "m_0_squared": "4",
    "m_star_squared": "1",
}
TEST_ORACLE_TRANSFER = {
    "initial_energy": "13/6",
    "transferred_energy": "23/6",
    "frequency_radius": "2",
    "hbar_radius": "4",
    "upper_bound": "37/6",
}
TEST_ORACLE_D_SQUARED = "1/128"


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


def exact_sqrt(value: Fraction) -> Fraction:
    numerator = math.isqrt(value.numerator)
    denominator = math.isqrt(value.denominator)
    if numerator * numerator != value.numerator or denominator * denominator != value.denominator:
        raise AssertionError(f"non-square exact input: {value}")
    return Fraction(numerator, denominator)


def ast_firewall(path: Path) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    forbidden_calls: list[str] = []
    forbidden_complex_literals: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {
            "float",
            "complex",
            "eval",
            "exec",
            "compile",
            "__import__",
        }:
            forbidden_calls.append(node.func.id)
        elif isinstance(node, ast.Constant) and isinstance(node.value, complex):
            forbidden_complex_literals.append(repr(node.value))
    return {
        "imports": sorted(imports),
        "forbidden_calls": forbidden_calls,
        "forbidden_complex_literals": forbidden_complex_literals,
    }


def exact_derivation() -> dict[str, Any]:
    b_a = WEIGHT_A * (A_S + C_GAMMA) + Fraction(1, 1) / (4 * WEIGHT_A * GAMMA)
    c_4 = (A_S + C_GAMMA) / GAMMA
    c_e = HBAR**2 / (2 * CHI * RHO_STAR)
    m_0_squared = RHO_STAR / 2
    m_star_squared = RHO_STAR / 8

    h_v2_power = 2 - SOURCE_POWER
    h_v_power = 1 - SOURCE_POWER
    order_power = SOURCE_POWER - 2
    eta_source_power = 1 - SOURCE_POWER
    eta_dominant_power = max(Fraction(-1), eta_source_power)
    root_inside_power = max(1 + eta_dominant_power, Fraction(1), Fraction(2))
    root_power = root_inside_power / 2
    residual_power = root_power - SOURCE_POWER
    smear_power = eta_source_power / 2
    order_limit = exact_sqrt(m_0_squared) if order_power < 0 else None
    zero_limit = Fraction(0)

    m3_fourth = (64 * c_4) ** 3
    witness_lhs_fourth = WITNESS_R**8 * m3_fourth
    witness_rhs_fourth = Fraction(3**4 * 8**2) * m_star_squared**2
    d_squared = WITNESS_R**2 * 8 * m_star_squared / 4

    eta_initial = sum((weight * energy for weight, energy in zip(ENERGY_WEIGHTS, ENERGIES)), Fraction(0))
    transferred_energy = sum(
        (ENERGY_WEIGHTS[source] * ENERGIES[target] for source, target in TRANSITIONS),
        Fraction(0),
    )
    maximum_energy_increase = max(ENERGIES[target] - ENERGIES[source] for source, target in TRANSITIONS)
    transfer_radius = maximum_energy_increase / HBAR
    transfer_rhs = eta_initial + HBAR * transfer_radius

    return {
        "window": {
            "source_power": str(SOURCE_POWER),
            "hV2_power": str(h_v2_power),
            "hV_power": str(h_v_power),
            "order_correction_power": str(order_power),
            "eta_source_power": str(eta_source_power),
            "eta_dominant_power": str(eta_dominant_power),
            "root_inside_power": str(root_inside_power),
            "root_power": str(root_power),
            "residual_power": str(residual_power),
            "smear_error_power": str(smear_power),
            "order_limit": str(order_limit),
            "eta_limit": str(zero_limit if eta_source_power < 0 else None),
            "residual_limit": str(zero_limit if residual_power < 0 else None),
            "smear_error_limit": str(zero_limit if smear_power < 0 else None),
        },
        "coercivity": {
            "gamma_below_g_over_32": GAMMA < G_COUPLING / 32,
            "B_a": str(b_a),
            "C_S_squared": str(b_a),
            "C_4": str(c_4),
            "C_e": str(c_e),
            "m_0_squared": str(m_0_squared),
            "m_star_squared": str(m_star_squared),
        },
        "energy_transfer": {
            "initial_energy": str(eta_initial),
            "transferred_energy": str(transferred_energy),
            "frequency_radius": str(transfer_radius),
            "hbar_radius": str(HBAR * transfer_radius),
            "upper_bound": str(transfer_rhs),
            "bound_holds": transferred_energy <= transfer_rhs,
        },
        "witness": {
            "M3_fourth_power": str(m3_fourth),
            "left_fourth_power": str(witness_lhs_fourth),
            "right_fourth_power": str(witness_rhs_fourth),
            "rational_condition": witness_lhs_fourth <= witness_rhs_fourth,
            "d_squared": str(d_squared),
        },
    }


def build_payload(formal: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    derived = exact_derivation()
    audit = Audit()

    audit.check("manifest identity", manifest["package_id"] == SLUG and manifest["version"] == "R-167 v4.0" and manifest["exploration_id"] == "EXP-000844" and manifest["prior_exploration_id"] == "EXP-000843" and manifest["claim_bearing"] is False, (manifest["package_id"], manifest["version"], manifest["exploration_id"]), (SLUG, "R-167 v4.0", "EXP-000844"), "identity")
    audit.check("manifest exact topology", manifest["closed_gate_ids"] == [CLOSED] and manifest["negative_ids"] == [] and manifest["reused_negative_ids"] == REUSED, (manifest["closed_gate_ids"], manifest["negative_ids"], manifest["reused_negative_ids"]), ([CLOSED], [], REUSED), "topology")
    source = " ".join(manifest["mesoscopic_source_selection"].values())
    audit.check("source sign and window contract", all(token in source for token in ("h_L<=h_0", "eta_L^sigma+h_L(V m_L-sigma s_L^sigma)", "h_L V^2->infinity", "h_L V->0", "h_L=h_* V^(-3/2)")), source, "exact mesoscopic source contract", "theorem")
    forms = " ".join(manifest["source_uniform_coercivity"].values()) + " " + " ".join(manifest["form_domain_and_energy_transfer"].values())
    audit.check("source coercivity and form domains", all(token in forms for token in ("B_a=a(A_s+C_gamma)+(4 a gamma)^(-1)", "C_S:=sqrt(B_a)", "C_4:=(A_s+C_gamma)/gamma", "eta_L+hbar R_A", "share one form domain", "represented form pairing", "not asserted to be a bounded operator commutator")), forms, "exact constants and typed form pairing", "forms")
    target = " ".join(manifest["zero_source_target"].values()) + " " + " ".join(manifest["combined_residual_closure"].values())
    audit.check("target core and residual", all(token in target for token in ("compact Fourier support", "graph core", "d_L(A) is exactly zero", "quadratic-form commutator identity", "O(h_L V)->0", "algebraic ground states")), target, "zero-source exact target residual closure", "target")
    witness = " ".join(manifest["fixed_witness_separation"].values())
    audit.check("fixed witness contract", all(token in witness for token in ("positive rational r_w", "M_3=(64 C_4)^(3/4)", "16/15", "||omega_+-omega_-||>=d")), witness, "fixed odd sine-smear", "separation")
    scope = manifest["no_overclaim"]
    audit.check("scope firewall", all(token in scope for token in ("new diagonal h_L clusters", "no zero-source quotient factorization", "no beta-infinity KMS limit", "no spatial all-exhaustion", "positive broken-sector GNS gap", "remain OPEN", "no new negative result")), scope, "categorical diagonal scope only", "scope")

    window = derived["window"]
    audit.check("independent window exponents", all(window[key] == TEST_ORACLE_WINDOW[key] for key in ("source_power", "hV2_power", "hV_power", "order_correction_power", "eta_source_power", "eta_dominant_power", "root_inside_power", "root_power", "residual_power", "smear_error_power")), window, TEST_ORACLE_WINDOW, "derivation")
    audit.check("independent window limits", all(window[key] == TEST_ORACLE_WINDOW[key] for key in ("order_limit", "eta_limit", "residual_limit", "smear_error_limit")), window, TEST_ORACLE_WINDOW, "derivation")
    exact = derived["coercivity"]
    audit.check("independent coercivity derivation", exact["gamma_below_g_over_32"] and exact["C_S_squared"] == exact["B_a"] and all(exact[key] == value for key, value in TEST_ORACLE_COERCIVITY.items()), exact, TEST_ORACLE_COERCIVITY, "derivation")
    transfer = derived["energy_transfer"]
    audit.check("independent energy-transfer factor", transfer["bound_holds"] and all(transfer[key] == value for key, value in TEST_ORACLE_TRANSFER.items()), transfer, TEST_ORACLE_TRANSFER, "derivation")
    fixed = derived["witness"]
    audit.check("independent rational witness", fixed["rational_condition"] and fixed["d_squared"] == TEST_ORACLE_D_SQUARED, fixed, TEST_ORACLE_D_SQUARED, "derivation")
    firewall = ast_firewall(SCRIPT)
    allowed_imports = {"__future__", "argparse", "ast", "hashlib", "json", "math", "os", "tempfile", "fractions", "pathlib", "typing"}
    audit.check("stdlib exact AST firewall", set(firewall["imports"]) <= allowed_imports and not firewall["forbidden_calls"] and not firewall["forbidden_complex_literals"], firewall, "stdlib allowlist and no float/complex/dynamic execution", "independence")
    audit.check("certificate contract", all(token in certificate for token in (CLOSED, "0<h_L<=h_0", "B_a:=a(A_s+C_gamma)+(4 a gamma)^(-1)", "unital star graph core", "No claim is made that", "|R_L^sigma(A)|->0", "No new negative result is needed", "No v4.0 PDF is issued")), "required tokens present", "required tokens present", "certificate")
    audit.check("source AST and exact format", ast.parse(SCRIPT.read_text(encoding="utf-8")) is not None and all(b"\r" not in path.read_bytes() and path.read_bytes().endswith(b"\n") and all(byte < 128 for byte in path.read_bytes()) for path in (MANIFEST, CERTIFICATE, SCRIPT)), "AST ASCII LF final-LF", "AST ASCII LF final-LF", "format")
    if formal:
        formal_paths = (REPO / "claims/GATES.md", REPO / "RESULTS-LEDGER.md", REPO / "negative-results/registry.md", REPO / "explorations/log.jsonl")
        formal_text = "\n".join(path.read_text(encoding="utf-8") for path in formal_paths)
        audit.check("formal authority links", all(token in formal_text for token in ("EXP-000844", CLOSED, "R-167 v4.0") + tuple(REUSED)), "all formal tokens present", "all formal tokens present", "formal")

    return {
        "schema": "tect/pre-a-q3lock-mesoscopic-source-ground-orbit-smear-transfer-independent-run/1.0",
        "version": "R-167 v4.0",
        "mode": "formal" if formal else "staged",
        "assertions": audit.rows,
        "summary": {"status": "PASS", "passed": len(audit.rows), "failed": 0},
        "derived": derived,
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
    print(f"INDEPENDENT PASS {payload['summary']['passed']}/{payload['summary']['passed']} mode={payload['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
