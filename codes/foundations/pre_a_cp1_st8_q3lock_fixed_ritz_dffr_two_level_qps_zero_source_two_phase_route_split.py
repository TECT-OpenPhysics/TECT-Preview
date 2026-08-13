#!/usr/bin/env python3
"""Primary symbolic verifier for the R-167 v3.3 fixed-Ritz DFFR package."""

from __future__ import annotations

import argparse
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
SLUG = "pre-a-cp1-st8-q3lock-fixed-ritz-dffr-two-level-qps-zero-source-two-phase-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-primary-{SLUG}/result.json"
FORMAL_PATHS = (
    REPO / "claims/GATES.md",
    REPO / "RESULTS-LEDGER.md",
    REPO / "negative-results/registry.md",
    REPO / "explorations/log.jsonl",
)

# Labelled fixture inputs. Every reported number below is derived from these.
OVERLAP = sp.Integer(8)
LOW_J = sp.Integer(1)
SAMPLE_N = sp.Integer(4)
SAMPLE_HIGH_SITES = sp.Integer(3)
SAMPLE_DISAGREEING_EDGES = sp.Integer(5)
LAMBDA_ZERO = sp.Rational(1, 2)
SUPPORT_SIZE = sp.Integer(2)
ONSITE_DIMENSION = sp.Integer(4)
LOW_BLOCK_COEFFICIENT = sp.Integer(2)
ADDITIVE_COEFFICIENT = sp.Integer(1)
HIGH_BLOCK_CONSTANT = sp.Integer(10)
THERMAL_EXPONENT_MULTIPLIER = sp.Integer(2)
ORDER_ERROR_TARGET = sp.Rational(1, 4)
PLUS_DERIVATIVE = sp.Integer(1)
MINUS_DERIVATIVE = sp.Integer(-1)


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
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


def exact_text(value: sp.Expr) -> str:
    return str(sp.factor(value)).replace("**", "^").replace(" ", "")


def expanded_rational_text(value: sp.Expr) -> str:
    numerator, denominator = sp.fraction(sp.together(value))
    numerator_text = str(sp.expand(numerator)).replace("**", "^").replace(" ", "")
    denominator_text = str(sp.expand(denominator)).replace("**", "^").replace(" ", "")
    if denominator_text == "1":
        return numerator_text
    if "+" in numerator_text or "-" in numerator_text[1:]:
        numerator_text = f"({numerator_text})"
    return f"{numerator_text}/{denominator_text}"


def peierls_fixture() -> tuple[dict[str, Any], sp.Expr]:
    kappa = sp.simplify(1 / (2 * OVERLAP))
    gamma = SAMPLE_N**2
    high_penalty = sp.simplify((gamma - 1) / (2 * OVERLAP))
    defective = OVERLAP * (SAMPLE_HIGH_SITES + SAMPLE_DISAGREEING_EDGES)
    high_defective = OVERLAP * SAMPLE_HIGH_SITES
    energy = gamma * SAMPLE_HIGH_SITES + 2 * LOW_J * SAMPLE_DISAGREEING_EDGES
    charged = sp.simplify(kappa * defective + high_penalty * high_defective)
    margin = sp.simplify(energy - charged)
    symbolic_gamma, symbolic_high, symbolic_low = sp.symbols(
        "Gamma H L", positive=True
    )
    symbolic_margin = sp.simplify(
        symbolic_gamma * symbolic_high
        + 2 * symbolic_low
        - kappa * OVERLAP * (symbolic_high + symbolic_low)
        - ((symbolic_gamma - 1) / (2 * OVERLAP)) * OVERLAP * symbolic_high
    )
    return (
        {
            "N": exact_text(SAMPLE_N),
            "high_sites": exact_text(SAMPLE_HIGH_SITES),
            "disagreeing_edges": exact_text(SAMPLE_DISAGREEING_EDGES),
            "defective_cubes_upper": exact_text(defective),
            "high_defect_cubes_upper": exact_text(high_defective),
            "energy_lower": exact_text(energy),
            "charged_upper": exact_text(charged),
            "strict_margin": exact_text(margin),
        },
        symbolic_margin,
    )


def dffr_fixture() -> tuple[dict[str, Any], dict[str, sp.Expr]]:
    n = sp.symbols("N", positive=True)
    kappa = sp.simplify(1 / (2 * OVERLAP))
    gamma = n**2
    high_penalty = sp.simplify((gamma - 1) / (2 * OVERLAP))
    hs_factor = ONSITE_DIMENSION**SUPPORT_SIZE
    decay_factor = sp.simplify(LAMBDA_ZERO ** (-SUPPORT_SIZE))
    combined = hs_factor * decay_factor
    low = LOW_BLOCK_COEFFICIENT / n**2 + ADDITIVE_COEFFICIENT / n**3
    high = HIGH_BLOCK_CONSTANT + ADDITIVE_COEFFICIENT / n**3
    cross_squared = sp.factor(low * high)
    epsilon_low = combined * low
    epsilon_high = combined * high
    epsilon_cross = combined * sp.sqrt(cross_squared)
    low_low_term = sp.simplify(LAMBDA_ZERO * epsilon_low / kappa)
    paired_term = sp.simplify(
        LAMBDA_ZERO
        * sp.sqrt(epsilon_cross * epsilon_cross / (kappa * (kappa + high_penalty)))
    )
    high_high_term = sp.simplify(LAMBDA_ZERO * epsilon_high / (kappa + high_penalty))
    one_way_term = sp.simplify(LAMBDA_ZERO * epsilon_cross / (kappa + high_penalty))
    limits = {
        "N2_low_low": sp.limit(n**2 * low_low_term, n, sp.oo),
        "N2_low_high_squared": sp.limit(n**4 * paired_term**2, n, sp.oo),
        "N2_high_high": sp.limit(n**2 * high_high_term, n, sp.oo),
        "N3_one_way_squared": sp.limit(n**6 * one_way_term**2, n, sp.oo),
    }
    kappa_bar = sp.simplify(kappa / 2)
    beta = sp.simplify(THERMAL_EXPONENT_MULTIPLIER * sp.log(2) / kappa_bar)
    thermal = sp.simplify(sp.exp(-beta * kappa_bar))
    inputs = {
        "overlap": exact_text(OVERLAP),
        "kappa": exact_text(kappa),
        "gamma": exact_text(gamma),
        "high_penalty": expanded_rational_text(high_penalty),
        "lambda": exact_text(LAMBDA_ZERO),
        "support_size": exact_text(SUPPORT_SIZE),
        "onsite_dimension": exact_text(ONSITE_DIMENSION),
        "hs_support_factor": exact_text(hs_factor),
        "decay_absorption_factor": exact_text(decay_factor),
        "combined_block_factor": exact_text(combined),
    }
    blocks = {
        "B_ll": f"{LOW_BLOCK_COEFFICIENT}/N^2+{ADDITIVE_COEFFICIENT}/N^3",
        "B_hh": f"{HIGH_BLOCK_CONSTANT}+{ADDITIVE_COEFFICIENT}/N^3",
        "B_lh_squared": (
            f"({LOW_BLOCK_COEFFICIENT}/N^2+{ADDITIVE_COEFFICIENT}/N^3)"
            f"*({HIGH_BLOCK_CONSTANT}+{ADDITIVE_COEFFICIENT}/N^3)"
        ),
    }
    derived = {
        "inputs": inputs,
        "block_bounds": blocks,
        "criterion_scaled_limits": {key: exact_text(value) for key, value in limits.items()},
        "thermal": {
            "kappa_bar": exact_text(kappa_bar),
            "beta": exact_text(beta),
            "term": exact_text(thermal),
            "role": "arithmetic identity only; epsilon_0 is unspecified, so this beta is not asserted to enter the theorem",
        },
    }
    raw = {
        "n": n,
        "kappa": kappa,
        "gamma": gamma,
        "high_penalty": high_penalty,
        "low": low,
        "high": high,
        "cross_squared": cross_squared,
        "low_low_term": low_low_term,
        "paired_term": paired_term,
        "high_high_term": high_high_term,
        "one_way_term": one_way_term,
        "thermal": thermal,
        "combined": combined,
    }
    return derived, raw


def order_and_parity_fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    plus_lower = sp.simplify(1 - ORDER_ERROR_TARGET)
    minus_upper = sp.simplify(-1 + ORDER_ERROR_TARGET)
    order_gap = sp.simplify(plus_lower - minus_upper)
    order = {
        "existential_error_target": exact_text(ORDER_ERROR_TARGET),
        "plus_order_lower": exact_text(plus_lower),
        "minus_order_upper": exact_text(minus_upper),
        "order_gap_lower": exact_text(order_gap),
        "role": "target arithmetic after q_(M,N,beta) is chosen sufficiently small; not a computed DFF constant",
    }
    derivative_difference = sp.simplify(PLUS_DERIVATIVE - MINUS_DERIVATIVE)
    source = sp.solve(sp.Eq(PLUS_DERIVATIVE * sp.Symbol("h"), MINUS_DERIVATIVE * sp.Symbol("h")))[0]
    parity = {
        "plus_derivative": exact_text(PLUS_DERIVATIVE),
        "minus_derivative": exact_text(MINUS_DERIVATIVE),
        "difference": exact_text(derivative_difference),
        "coexistence_source": exact_text(source),
    }
    return order, parity


def factorization_fixture(raw: dict[str, sp.Expr]) -> dict[str, sp.Expr]:
    low = raw["low"]
    high = raw["high"]
    root = sp.sqrt(low * high)
    b_matrix = sp.diag(low, high)
    c_matrix = sp.Matrix([[0, 1], [1, 0]])
    b_root = sp.diag(sp.sqrt(low), sp.sqrt(high))
    v_matrix = sp.simplify(b_root * c_matrix * b_root)
    plus = sp.simplify(b_matrix + v_matrix)
    minus = sp.simplify(b_matrix - v_matrix)
    auxiliary_lambda = sp.symbols("lambda", positive=True)
    auxiliary_v = sp.simplify((auxiliary_lambda / LAMBDA_ZERO) ** SUPPORT_SIZE * root)
    epsilon_cross = sp.simplify(LAMBDA_ZERO ** (-SUPPORT_SIZE) * root)
    return {
        "c_squared": sp.simplify(c_matrix * c_matrix)[0, 0],
        "cross_squared": sp.simplify(v_matrix[0, 1] * v_matrix[1, 0]),
        "plus_determinant": sp.factor(plus.det()),
        "minus_determinant": sp.factor(minus.det()),
        "plus_trace": sp.simplify(sp.trace(plus)),
        "minus_trace": sp.simplify(sp.trace(minus)),
        "lambda_identity": sp.simplify(auxiliary_v - epsilon_cross * auxiliary_lambda**SUPPORT_SIZE),
    }


def build_payload(staged: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    normalized_certificate = " ".join(certificate.split())
    dffr, raw = dffr_fixture()
    peierls, symbolic_margin = peierls_fixture()
    order, parity = order_and_parity_fixture()
    derived = dffr | {"peierls_sample": peierls, "order_target": order, "parity": parity}
    factor = factorization_fixture(raw)
    audit = Audit()

    audit.check(
        "manifest exact identity and UTC date",
        manifest["package_id"] == SLUG
        and manifest["version"] == "R-167 v3.3"
        and manifest["date"] == "2026-08-13"
        and manifest["exploration_id"] == "EXP-000837"
        and manifest["prior_exploration_id"] == "EXP-000836"
        and manifest["claim_bearing"] is False,
        (manifest["package_id"], manifest["version"], manifest["date"], manifest["exploration_id"]),
        (SLUG, "R-167 v3.3", "2026-08-13", "EXP-000837"),
        "identity",
    )
    audit.check(
        "one CLOSED child no new negative",
        len(manifest["closed_gate_ids"]) == len(set(manifest["closed_gate_ids"])) == 1
        and manifest["negative_ids"] == []
        and manifest["reused_negative_ids"]
        == ["NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-DEFECT-AUTOMATIC-N-DEPENDENT-TWO-PHASE-RADIUS-ENTRY"],
        (manifest["closed_gate_ids"], manifest["negative_ids"], manifest["reused_negative_ids"]),
        "one child, no new negative, one reused boundary",
        "identity",
    )
    audit.check(
        "five parents remain OPEN",
        len(manifest["open_parent_gate_ids"]) == len(set(manifest["open_parent_gate_ids"])) == 5
        and "All five active parent gates remain OPEN" in manifest["no_overclaim"],
        manifest["open_parent_gate_ids"],
        "five unique OPEN parents",
        "identity",
    )
    audit.check(
        "historical beta-infinity gate remains OPEN",
        manifest["historical_open_gate_ids"]
        == ["PA-CP1-ST8-Q3LOCK-BETA-INFINITY-GROUND-STATE-SELECTION"]
        and manifest["historical_open_gate_ids"][0] in manifest["no_overclaim"],
        manifest["historical_open_gate_ids"],
        "one historical exact-Q3/common-alpha OPEN gate",
        "identity",
    )
    for group, expected in manifest["exact_fixture"].items():
        audit.check(f"exact {group} fixture", derived[group] == expected, derived[group], expected, group)

    expected_symbolic_margin = (
        sp.Symbol("Gamma", positive=True) * sp.Symbol("H", positive=True) / 2
        + 3 * sp.Symbol("L", positive=True) / 2
    )
    audit.check(
        "strict bounded-overlap Peierls margin",
        sp.simplify(symbolic_margin - expected_symbolic_margin) == 0,
        symbolic_margin,
        expected_symbolic_margin,
        "peierls",
    )
    audit.check(
        "two-sided form factorization fixture",
        factor["c_squared"] == 1
        and factor["cross_squared"] == raw["cross_squared"]
        and factor["plus_determinant"] == factor["minus_determinant"] == 0
        and factor["plus_trace"] == factor["minus_trace"] == raw["low"] + raw["high"],
        factor,
        "selfadjoint contraction and B plus/minus V positive semidefinite",
        "factorization",
    )
    audit.check(
        "auxiliary lambda family exact support identity",
        factor["lambda_identity"] == 0,
        factor["lambda_identity"],
        0,
        "lambda",
    )
    audit.check(
        "all five nonthermal DFFR terms vanish",
        all(
            sp.limit(term, raw["n"], sp.oo) == 0
            for term in (
                raw["low_low_term"], raw["paired_term"], raw["high_high_term"], raw["one_way_term"]
            )
        ),
        [
            sp.limit(term, raw["n"], sp.oo)
            for term in (raw["low_low_term"], raw["paired_term"], raw["high_high_term"], raw["one_way_term"])
        ],
        [0, 0, 0, 0],
        "criterion",
    )
    audit.check(
        "thermal fixture is arithmetic only",
        raw["thermal"] == ORDER_ERROR_TARGET
        and "not asserted to enter the theorem" in derived["thermal"]["role"],
        (raw["thermal"], derived["thermal"]["role"]),
        "1/4 and explicit non-entry role",
        "criterion",
    )
    audit.check(
        "parity source splitting",
        parity == manifest["exact_fixture"]["parity"] and parity["difference"] == "2" and parity["coexistence_source"] == "0",
        parity,
        manifest["exact_fixture"]["parity"],
        "parity",
    )

    theorem_tokens = (
        "DFFR Theorem 5.2",
        "E(gamma) > kappa s(gamma) + D s(gamma_high)",
        "Q_(X,N)(lambda)",
        "lambda/lambda_0",
        "DFF I Theorem 2.2 and equation (2.81)",
        "actual contour parameter tends to zero",
        manifest["closed_gate_ids"][0],
        "No v3.3 PDF is issued",
    )
    audit.check(
        "certificate theorem contract",
        all(token in normalized_certificate for token in theorem_tokens),
        [token for token in theorem_tokens if token not in normalized_certificate],
        [],
        "certificate",
    )
    boundary_tokens = (
        "not uniform in `M`",
        "not a purity or exhaustive-classification claim",
        "No GNS spectral-gap conclusion",
        "All five active parent gates remain OPEN",
        "PA-CP1-ST8-Q3LOCK-BETA-INFINITY-GROUND-STATE-SELECTION` also remains OPEN",
        "physical Sector A, or Pre-A",
    )
    audit.check(
        "certificate no-overclaim contract",
        all(token in normalized_certificate for token in boundary_tokens),
        [token for token in boundary_tokens if token not in normalized_certificate],
        [],
        "certificate",
    )

    if not staged:
        formal_text = "\n".join(path.read_text(encoding="utf-8") for path in FORMAL_PATHS)
        formal_ok = (
            formal_text.count("EXP-000837") > 0
            and manifest["closed_gate_ids"][0] in formal_text
            and "R-167 v3.3" in formal_text
        )
        audit.check("formal authority aggregate", formal_ok, formal_ok, True, "formal")

    return {
        "schema": "tect/verification-run/1.0",
        "script_version": __version__,
        "package_id": SLUG,
        "mode": "staged" if staged else "formal",
        "verdict": "PASS",
        "assertions": audit.rows,
        "summary": {"total": len(audit.rows), "passed": len(audit.rows), "failed": 0, "missing": 0},
        "derived": derived,
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in (SCRIPT, MANIFEST, CERTIFICATE)
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = build_payload(args.staged)
    if not args.no_store:
        atomic_json(args.output, payload)
    total = payload["summary"]["total"]
    print(f"R-167 v3.3 PRIMARY PASS {total}/{total}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
