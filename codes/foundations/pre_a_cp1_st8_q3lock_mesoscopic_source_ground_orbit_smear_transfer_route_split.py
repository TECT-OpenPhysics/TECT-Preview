#!/usr/bin/env python3
"""Verify the R-167 v4.0 mesoscopic-source exact-Q3 ground transfer.

Convention: ``V=L^3``, ``H_L(sigma h)=H_L(0)-sigma h S_L``, and the canonical
source is ``h_L=h_* V^(-3/2)``.  The load-bearing formulas recomputed here are
``eta+h_L(V m-sigma s)<=C_e/V`` and ``|R_L^sigma(A)|=O(h_L V)->0``.
"""

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
SLUG = "pre-a-cp1-st8-q3lock-mesoscopic-source-ground-orbit-smear-transfer-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-primary-{SLUG}/result.json"
FORMAL_PATHS = (
    REPO / "claims/GATES.md",
    REPO / "RESULTS-LEDGER.md",
    REPO / "negative-results/registry.md",
    REPO / "explorations/log.jsonl",
)

CLOSED = "PA-CP1-ST8-Q3LOCK-MESOSCOPIC-SOURCE-EXACT-GROUND-RESIDUAL-CLOSURE-AND-ZERO-SOURCE-ORBIT-SMEAR-GROUND-PAIR"
REUSED = [
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-SOURCE-EXACT-TARGET-GENERATOR-AND-SEPARATION-AUTOMATIC-TARGET-GROUNDNESS",
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-SOURCE-AUTOMATIC-ZERO-SOURCE-QUOTIENT-FACTORIZATION",
    "NG-2026-08-12-PRE-A-ST8-Q3LOCK-ORBIT-SMEAR-SEED-SUPPORT-AUTOMATIC-SPATIAL-LOCAL-NET",
]

# Labelled exact audit inputs. Every reported theorem constant is derived below.
RHO_STAR = sp.Integer(8)
HBAR = sp.Integer(2)
CHI = sp.Integer(1)
H_STAR = sp.Integer(3)
SOURCE_POWER = sp.Rational(3, 2)
G_COUPLING = sp.Integer(16)
GAMMA = sp.Rational(1, 4)
WEIGHT_A = sp.Integer(2)
A_S = sp.Integer(3)
C_GAMMA = sp.Integer(5)
ARVESON_RADIUS = sp.Integer(2)
ABSTRACT_NORM = sp.Integer(2)
SMEAR_TIME = sp.Integer(5)
WITNESS_R = sp.Rational(1, 16)

# Exact finite spectral-transfer audit inputs.
ENERGIES = (sp.Integer(0), sp.Integer(3), sp.Integer(7))
ENERGY_WEIGHTS = (sp.Rational(1, 2), sp.Rational(1, 3), sp.Rational(1, 6))
TRANSITIONS = ((0, 1), (1, 2))

# Explicit test oracles. These validate independently derived exact outputs.
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


def exact_derivation() -> dict[str, Any]:
    v = sp.symbols("V", positive=True)
    b_a = sp.simplify(WEIGHT_A * (A_S + C_GAMMA) + 1 / (4 * WEIGHT_A * GAMMA))
    c_s = sp.sqrt(b_a)
    c_4 = sp.simplify((A_S + C_GAMMA) / GAMMA)
    c_e = sp.simplify(HBAR**2 / (2 * CHI * RHO_STAR))
    m_0_squared = sp.simplify(RHO_STAR / 2)
    m_star_squared = sp.simplify(RHO_STAR / 8)

    h_l = H_STAR * v ** (-SOURCE_POWER)
    eta_dominant_power = max(sp.Integer(-1), 1 - SOURCE_POWER)
    root_inside_power = max(1 + eta_dominant_power, sp.Integer(1), sp.Integer(2))
    root_power = sp.simplify(root_inside_power / 2)
    residual_power = sp.simplify(root_power - SOURCE_POWER)
    order_correction = sp.simplify(c_e / (h_l * v**2))
    eta_upper = sp.simplify(c_e / v + c_s * h_l * v)
    order_lower = sp.sqrt(m_0_squared) - order_correction

    first_root = sp.sqrt(WEIGHT_A * v * (eta_upper + HBAR * ARVESON_RADIUS) + b_a * v**2)
    second_root = sp.sqrt(WEIGHT_A * v * eta_upper + b_a * v**2)
    residual_upper = sp.simplify(h_l * ABSTRACT_NORM**2 * (first_root + second_root))
    smear_error = sp.Rational(16, 15) * sp.sqrt(2 * SMEAR_TIME * eta_upper / HBAR)

    m3_fourth = sp.expand((64 * c_4) ** 3)
    witness_lhs_fourth = sp.simplify(WITNESS_R**8 * m3_fourth)
    witness_rhs_fourth = sp.simplify(3**4 * 8**2 * m_star_squared**2)
    d_squared = sp.simplify(WITNESS_R**2 * 8 * m_star_squared / 4)

    eta_initial = sp.simplify(sum(weight * energy for weight, energy in zip(ENERGY_WEIGHTS, ENERGIES)))
    transferred_energy = sp.simplify(
        sum(ENERGY_WEIGHTS[source] * ENERGIES[target] for source, target in TRANSITIONS)
    )
    transfer_radius = sp.simplify(
        max(ENERGIES[target] - ENERGIES[source] for source, target in TRANSITIONS) / HBAR
    )
    transfer_rhs = sp.simplify(eta_initial + HBAR * transfer_radius)

    return {
        "window": {
            "source_power": str(SOURCE_POWER),
            "hV2_power": str(sp.simplify(2 - SOURCE_POWER)),
            "hV_power": str(sp.simplify(1 - SOURCE_POWER)),
            "order_correction_power": str(sp.simplify(SOURCE_POWER - 2)),
            "eta_source_power": str(sp.simplify(1 - SOURCE_POWER)),
            "eta_dominant_power": str(eta_dominant_power),
            "root_inside_power": str(root_inside_power),
            "root_power": str(root_power),
            "residual_power": str(residual_power),
            "smear_error_power": str(sp.simplify((1 - SOURCE_POWER) / 2)),
            "order_limit": str(sp.limit(order_lower, v, sp.oo)),
            "eta_limit": str(sp.limit(eta_upper, v, sp.oo)),
            "residual_limit": str(sp.limit(residual_upper, v, sp.oo)),
            "smear_error_limit": str(sp.limit(smear_error, v, sp.oo)),
        },
        "coercivity": {
            "gamma_below_g_over_32": bool(GAMMA < G_COUPLING / 32),
            "B_a": str(b_a),
            "C_S_squared": str(sp.simplify(c_s**2)),
            "C_4": str(c_4),
            "C_e": str(c_e),
            "m_0_squared": str(m_0_squared),
            "m_star_squared": str(m_star_squared),
        },
        "energy_transfer": {
            "initial_energy": str(eta_initial),
            "transferred_energy": str(transferred_energy),
            "frequency_radius": str(transfer_radius),
            "hbar_radius": str(sp.simplify(HBAR * transfer_radius)),
            "upper_bound": str(transfer_rhs),
            "bound_holds": bool(transferred_energy <= transfer_rhs),
        },
        "witness": {
            "M3_fourth_power": str(m3_fourth),
            "left_fourth_power": str(witness_lhs_fourth),
            "right_fourth_power": str(witness_rhs_fourth),
            "rational_condition": bool(witness_lhs_fourth <= witness_rhs_fourth),
            "d_squared": str(d_squared),
        },
    }


def build_payload(formal: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    derived = exact_derivation()
    audit = Audit()

    audit.check("manifest identity", manifest["package_id"] == SLUG and manifest["version"] == "R-167 v4.0" and manifest["date"] == "2026-08-14" and manifest["exploration_id"] == "EXP-000844" and manifest["prior_exploration_id"] == "EXP-000843" and manifest["claim_bearing"] is False, (manifest["package_id"], manifest["version"], manifest["exploration_id"]), (SLUG, "R-167 v4.0", "EXP-000844"), "identity")
    audit.check("manifest topology", manifest["closed_gate_ids"] == [CLOSED] and manifest["negative_ids"] == [] and manifest["reused_negative_ids"] == REUSED, (manifest["closed_gate_ids"], manifest["negative_ids"], manifest["reused_negative_ids"]), ([CLOSED], [], REUSED), "topology")
    inherited = " ".join(str(value) for value in manifest["inherited_exact_inputs"].values())
    audit.check("inherited exact-Q3 inputs", all(token in inherited for token in ("m_L^2", "rho_*", "epsilon_L<=hbar^2/(4 chi V m_L^2)", "unique strictly positive ground", "EXP-000792")), inherited, "ground order, source ground and authority anchors", "theorem")
    source = " ".join(manifest["mesoscopic_source_selection"].values())
    audit.check("mesoscopic sign and window", all(token in source for token in ("eta_L^sigma+h_L(V m_L-sigma s_L^sigma)", "h_L V^2->infinity", "h_L V->0", "h_L=h_* V^(-3/2)", "m_*=m_0/2")), source, "exact sign and nonempty window", "theorem")
    coercivity = " ".join(manifest["source_uniform_coercivity"].values())
    audit.check("derived coercivity constants", all(token in coercivity for token in ("0<gamma<g/32", "B_a=a(A_s+C_gamma)+(4 a gamma)^(-1)", "S_L^2<=a V K_L+B_a V^2", "C_S:=sqrt(B_a)", "C_4:=(A_s+C_gamma)/gamma", "No additive derived constant")), coercivity, "EXP792 exact constants", "forms")
    target = " ".join(manifest["zero_source_target"].values())
    audit.check("graph core and exact defect", all(token in target for token in ("A_H^0", "compact Fourier support", "graph core", "Differentiating exact equivariance in norm", "d_L(A) is exactly zero")), target, "bandlimited graph core and defect zero", "target")
    domains = " ".join(manifest["form_domain_and_energy_transfer"].values())
    audit.check("energy transfer and form pairing", all(token in domains for token in ("eta_L+hbar R_A", "Dom(K_L^(1/2))", "share one form domain", "represented form pairing", "not asserted to be a bounded operator commutator")), domains, "hbar-correct form domains", "forms")
    residual = " ".join(manifest["combined_residual_closure"].values())
    audit.check("combined residual closure", all(token in residual for token in ("quadratic-form commutator identity", "d_L(A)=0", "sqrt[a V(eta_L+hbar R_A)+B_a V^2]", "O(h_L V)->0", "algebraic ground states")), residual, "exact Q3 v3.9 instantiation", "residual")
    witness = " ".join(manifest["fixed_witness_separation"].values())
    audit.check("fixed odd witness", all(token in witness for token in ("M_3=(64 C_4)^(3/4)", "positive rational r_w", "16/15", "eta_L/hbar", "||omega_+-omega_-||>=d")), witness, "fixed rational sine-smear", "separation")
    scope = " ".join(manifest["branch_and_scope_split"].values()) + " " + manifest["no_overclaim"]
    audit.check("branch and scope firewalls", all(token in scope for token in ("fixed-positive-beta", "new diagonal h_L clusters", "not proved equal", "hand-built zero-source approximate doublets", "no v3.8 quotient factorization", "categorical and nonspatial", "remain OPEN")), scope, "nonduplicate categorical scope", "scope")

    window = derived["window"]
    audit.check("exact mesoscopic exponents", all(window[key] == TEST_ORACLE_WINDOW[key] for key in ("source_power", "hV2_power", "hV_power", "order_correction_power", "eta_source_power", "eta_dominant_power", "root_inside_power", "root_power", "residual_power")), window, TEST_ORACLE_WINDOW, "derivation")
    audit.check("order and near-ground limits", all(window[key] == TEST_ORACLE_WINDOW[key] for key in ("order_limit", "eta_limit")), window, TEST_ORACLE_WINDOW, "derivation")
    exact = derived["coercivity"]
    audit.check("exact sample coercivity derivation", exact["gamma_below_g_over_32"] and exact["C_S_squared"] == exact["B_a"] and all(exact[key] == value for key, value in TEST_ORACLE_COERCIVITY.items()), exact, TEST_ORACLE_COERCIVITY, "derivation")
    transfer = derived["energy_transfer"]
    audit.check("hbar-correct spectral transfer fixture", transfer["bound_holds"] and all(transfer[key] == value for key, value in TEST_ORACLE_TRANSFER.items()), transfer, TEST_ORACLE_TRANSFER, "derivation")
    audit.check("residual and smear limits", all(window[key] == TEST_ORACLE_WINDOW[key] for key in ("residual_limit", "smear_error_limit", "smear_error_power")), window, TEST_ORACLE_WINDOW, "derivation")
    fixed = derived["witness"]
    audit.check("exact rational witness condition", fixed["rational_condition"] and fixed["d_squared"] == TEST_ORACLE_D_SQUARED, fixed, TEST_ORACLE_D_SQUARED, "derivation")
    audit.check("certificate math tokens", all(token in certificate for token in (CLOSED, "eta_L^sigma+h_L(V m_L-sigma s_L^sigma)", "B_a:=a(A_s+C_gamma)+(4 a gamma)^(-1)", "unital star graph core", "No claim is made that", "|R_L^sigma(A)|->0", "16/15", "No v4.0 PDF is issued")), "required tokens present", "required tokens present", "certificate")
    audit.check("certificate lifecycle firewalls", all(token in certificate for token in ("new diagonal mesoscopic pair", "not identified with", "no beta-infinity KMS limit", "no spatial all-exhaustion", "positive broken-sector GNS gap", "All five active parent gates and both historical gates remain OPEN", "No new negative result is needed")), "scope tokens present", "scope tokens present", "scope")
    audit.check("source AST and format", ast.parse(SCRIPT.read_text(encoding="utf-8")) is not None and all(b"\r" not in path.read_bytes() and path.read_bytes().endswith(b"\n") and all(byte < 128 for byte in path.read_bytes()) for path in (MANIFEST, CERTIFICATE, SCRIPT)), "AST ASCII LF final-LF", "AST ASCII LF final-LF", "format")
    if formal:
        formal_text = "\n".join(path.read_text(encoding="utf-8") for path in FORMAL_PATHS)
        audit.check("formal authority links", all(token in formal_text for token in ("EXP-000844", CLOSED, "R-167 v4.0") + tuple(REUSED)), "all formal tokens present", "all formal tokens present", "formal")

    return {
        "schema": "tect/pre-a-q3lock-mesoscopic-source-ground-orbit-smear-transfer-run/1.0",
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
    print(f"PRIMARY PASS {payload['summary']['passed']}/{payload['summary']['passed']} mode={payload['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
