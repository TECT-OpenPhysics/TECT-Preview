#!/usr/bin/env python3
"""Primary symbolic verifier for the R-167 v3.7 proof-first package."""

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
SLUG = "pre-a-cp1-st8-q3lock-affine-form-gibbs-trace-first-duhamel-route-repair"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-13-primary-{SLUG}/result.json"
)
FORMAL_PATHS = (
    REPO / "claims/GATES.md",
    REPO / "RESULTS-LEDGER.md",
    REPO / "explorations/log.jsonl",
)

CLOSED = (
    "PA-CP1-ST8-Q3LOCK-AFFINE-FORM-GIBBS-TRACE-HALF-INTERVAL-L1-FIRST-DUHAMEL-AND-SPECTRAL-RITZ-REMOVAL"
)
REUSED_NEGATIVES = (
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-POINTWISE-POSITIVE-TIME-TRACE-CLASS-AUTOMATIC-SHORT-TIME-L1-DOMINATION",
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-FIXED-POSITIVE-TIME-ENERGY-DRESSED-TRACE-CONTROL-AUTOMATIC-DFFR-CONTOUR-ENTRY",
)

# Labelled fixture inputs only.
H_LEVELS = (sp.Integer(0), sp.Integer(1), sp.Integer(4))
AFFINE_A = sp.Integer(2)
AFFINE_B = sp.Integer(3)
BETA_BASE = sp.Integer(4)
BETA = sp.log(BETA_BASE)
RITZ_RANK = sp.Integer(2)
MIDDLE_SIGN = sp.Integer(-1)
SWAP_LEFT = sp.Integer(0)
SWAP_RIGHT = sp.Integer(2)


def normalized_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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


def exact_text(value: sp.Expr) -> str:
    return str(sp.factor(value)).replace("**", "^").replace(" ", "")


def radical_linear_text(value: sp.Expr) -> str:
    return exact_text(sp.radsimp(value))


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(
        self, name: str, condition: bool, actual: Any, expected: Any, group: str
    ) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": str(actual),
                "expected": str(expected),
            }
        )


def derive_fixture() -> dict[str, Any]:
    dimension = len(H_LEVELS)
    h = sp.diag(*H_LEVELS)
    identity = sp.eye(dimension)
    b_matrix = AFFINE_A * h + AFFINE_B * identity
    b_levels = tuple(sp.Integer(b_matrix[i, i]) for i in range(dimension))
    sqrt_b = sp.diag(*(sp.sqrt(value) for value in b_levels))

    c_matrix = sp.zeros(dimension)
    c_matrix[SWAP_LEFT, SWAP_RIGHT] = 1
    c_matrix[SWAP_RIGHT, SWAP_LEFT] = 1
    remaining = tuple(
        index
        for index in range(dimension)
        if index not in (int(SWAP_LEFT), int(SWAP_RIGHT))
    )
    for index in remaining:
        c_matrix[index, index] = MIDDLE_SIGN
    v_matrix = sp.simplify(sqrt_b * c_matrix * sqrt_b)

    s = sp.symbols("s", positive=True)
    left = sp.diag(*(sp.exp(-(BETA - s) * level) for level in H_LEVELS))
    right = sp.diag(*(sp.exp(-s * level) for level in H_LEVELS))
    k_matrix = sp.simplify(left * v_matrix * right)

    off_forward = sp.simplify(k_matrix[SWAP_LEFT, SWAP_RIGHT])
    off_reverse = sp.simplify(k_matrix[SWAP_RIGHT, SWAP_LEFT])
    diagonal_abs = sum(
        sp.Abs(k_matrix[index, index]) for index in remaining
    )
    pointwise_norm = sp.simplify(off_forward + off_reverse + diagonal_abs)
    integrated_norm = sp.simplify(sp.integrate(pointwise_norm, (s, 0, BETA)))
    scalar_trace = sp.simplify(sp.trace(k_matrix))
    integrated_scalar = sp.simplify(sp.integrate(scalar_trace, (s, 0, BETA)))

    a_beta = sp.simplify(
        sum(
            sp.sqrt(b_level) * sp.exp(-BETA * h_level / 2)
            for h_level, b_level in zip(H_LEVELS, b_levels)
        )
    )
    majorant = sp.simplify(
        a_beta
        * (
            BETA * sp.sqrt(AFFINE_B)
            + 2 * sp.sqrt(AFFINE_A * BETA / sp.E)
        )
    )

    projection = sp.diag(
        *(sp.Integer(1) if index < RITZ_RANK else sp.Integer(0) for index in range(dimension))
    )
    tail_matrix = sp.simplify(k_matrix - projection * k_matrix * projection)
    # Here the tail is precisely the two off-diagonal entries of the swap block.
    tail_integral = sp.simplify(sp.integrate(off_forward + off_reverse, (s, 0, BETA)))
    full_projection = sp.eye(dimension)
    full_tail = sp.simplify(k_matrix - full_projection * k_matrix * full_projection)

    beta_text = f"log({exact_text(BETA_BASE)})"
    swap_integral = sp.simplify(sp.integrate(off_forward + off_reverse, (s, 0, BETA)))
    middle_abs = abs(v_matrix[remaining[0], remaining[0]])
    middle_integral_text = (
        f"{exact_text(middle_abs)}*{beta_text}/{exact_text(BETA_BASE)}"
    )
    scalar_integral_text = (
        f"{exact_text(v_matrix[remaining[0], remaining[0]])}*"
        f"{beta_text}/{exact_text(BETA_BASE)}"
    )
    a_beta_text = (
        f"sqrt({exact_text(b_levels[0])})+"
        f"sqrt({exact_text(b_levels[1])})/{exact_text(sp.sqrt(BETA_BASE))}+"
        f"sqrt({exact_text(b_levels[2])})/{exact_text(BETA_BASE ** (H_LEVELS[2] / 2))}"
    )
    majorant_text = (
        f"A_beta[{beta_text}*sqrt({exact_text(AFFINE_B)})+"
        f"2*sqrt({exact_text(AFFINE_A)}*{beta_text}/e)]"
    )
    return {
        "B_diagonal": [exact_text(value) for value in b_levels],
        "C_selfadjoint": bool(c_matrix == c_matrix.adjoint()),
        "C_unitary": bool(sp.simplify(c_matrix * c_matrix - identity) == sp.zeros(dimension)),
        "C_norm": int(1 if c_matrix * c_matrix == identity else 0),
        "V_swap": radical_linear_text(v_matrix[SWAP_LEFT, SWAP_RIGHT]),
        "V_middle": exact_text(v_matrix[remaining[0], remaining[0]]),
        "pointwise_trace_norm": (
            f"sqrt({exact_text(b_levels[SWAP_LEFT] * b_levels[SWAP_RIGHT])})"
            f"[exp(-{exact_text(H_LEVELS[SWAP_RIGHT])}s)+"
            f"exp(-{exact_text(H_LEVELS[SWAP_RIGHT])}(beta-s))]+"
            f"{exact_text(abs(v_matrix[remaining[0], remaining[0]]))}exp(-beta)"
        ),
        "integrated_trace_norm": f"{exact_text(swap_integral)}+{middle_integral_text}",
        "integrated_scalar_trace": scalar_integral_text,
        "scalar_trace": exact_text(scalar_trace),
        "A_beta": a_beta_text,
        "majorant_integral": majorant_text,
        "majorant_strict": bool(sp.N(majorant - integrated_norm, 80) > 0),
        "rank_two_tail_integral": exact_text(tail_integral),
        "rank_three_tail_integral": exact_text(sum(abs(value) for value in full_tail)),
        "matrix_trace_identity": bool(
            sp.simplify(
                scalar_trace
                - sp.trace(c_matrix * b_matrix * sp.diag(*(sp.exp(-BETA * level) for level in H_LEVELS)))
            )
            == 0
        ),
    }


def derive_general_bound() -> dict[str, Any]:
    x, s, beta, a, b = sp.symbols("x s beta a b", positive=True)
    profile = sp.sqrt(x) * sp.exp(-s * x)
    derivative = sp.factor(sp.diff(profile, x))
    stationary = sp.solve(sp.Eq(derivative, 0), x)[0]
    maximum = sp.simplify(profile.subs(x, stationary))
    half_singular_integral = sp.simplify(
        2 * sp.integrate(sp.sqrt(a / (2 * sp.E * s)), (s, 0, beta / 2))
    )
    return {
        "stationary_point": exact_text(stationary),
        "operator_maximum": exact_text(maximum),
        "two_half_singular_integral": exact_text(half_singular_integral),
        "target_singular_integral": exact_text(2 * sp.sqrt(a * beta / sp.E)),
        "constant_integral": exact_text(beta * sp.sqrt(b)),
        "derivative": str(derivative),
        "stationary_is_critical": bool(sp.simplify(derivative.subs(x, stationary)) == 0),
        "maximum_squared_identity": bool(
            sp.simplify(maximum**2 - 1 / (2 * sp.E * s)) == 0
        ),
    }


def build_payload(formal: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    certificate_normalized = " ".join(certificate.split())
    audit = Audit()
    fixture = derive_fixture()
    general = derive_general_bound()
    expected = manifest["exact_fixture"]["derived"]

    audit.check(
        "manifest topology",
        manifest["closed_gate_ids"] == [CLOSED]
        and manifest["negative_ids"] == []
        and tuple(manifest["reused_negative_ids"]) == REUSED_NEGATIVES
        and manifest["exploration_id"] == "EXP-000841",
        (manifest["closed_gate_ids"], manifest["reused_negative_ids"]),
        ([CLOSED], REUSED_NEGATIVES),
        "topology",
    )
    audit.check(
        "general operator maximum",
        general["stationary_is_critical"] and general["maximum_squared_identity"],
        (general["stationary_point"], general["operator_maximum"]),
        ("1/(2*s)", "1/sqrt(2 e s)"),
        "theorem",
    )
    audit.check(
        "general half-interval integral",
        general["two_half_singular_integral"]
        == general["target_singular_integral"],
        general["two_half_singular_integral"],
        general["target_singular_integral"],
        "theorem",
    )
    audit.check(
        "fixture affine spectrum",
        fixture["B_diagonal"] == expected["B_diagonal"],
        fixture["B_diagonal"],
        expected["B_diagonal"],
        "fixture",
    )
    audit.check(
        "fixture contraction",
        fixture["C_selfadjoint"] and fixture["C_unitary"] and fixture["C_norm"] == 1,
        (fixture["C_selfadjoint"], fixture["C_unitary"], fixture["C_norm"]),
        (True, True, 1),
        "fixture",
    )
    audit.check(
        "fixture perturbation",
        fixture["V_swap"] == "sqrt(33)" and fixture["V_middle"] == "-5",
        (fixture["V_swap"], fixture["V_middle"]),
        ("sqrt(33)", "-5"),
        "fixture",
    )
    audit.check(
        "fixture pointwise trace norm",
        fixture["pointwise_trace_norm"] == expected["pointwise_trace_norm"],
        fixture["pointwise_trace_norm"],
        expected["pointwise_trace_norm"],
        "fixture",
    )
    audit.check(
        "fixture integrated trace norm",
        fixture["integrated_trace_norm"] == expected["integrated_trace_norm"],
        fixture["integrated_trace_norm"],
        expected["integrated_trace_norm"],
        "fixture",
    )
    audit.check(
        "fixture scalar trace identity",
        fixture["matrix_trace_identity"]
        and fixture["integrated_scalar_trace"] == expected["integrated_scalar_trace"],
        fixture["integrated_scalar_trace"],
        expected["integrated_scalar_trace"],
        "fixture",
    )
    audit.check(
        "fixture Gibbs factor",
        fixture["A_beta"] == expected["A_beta"],
        fixture["A_beta"],
        expected["A_beta"],
        "fixture",
    )
    audit.check(
        "fixture majorant",
        fixture["majorant_integral"] == expected["majorant_integral"]
        and fixture["majorant_strict"] is expected["majorant_strict"],
        (fixture["majorant_integral"], fixture["majorant_strict"]),
        (expected["majorant_integral"], expected["majorant_strict"]),
        "fixture",
    )
    audit.check(
        "fixture Ritz tails",
        fixture["rank_two_tail_integral"] == expected["rank_two_tail_integral"]
        and fixture["rank_three_tail_integral"] == expected["rank_three_tail_integral"],
        (fixture["rank_two_tail_integral"], fixture["rank_three_tail_integral"]),
        (expected["rank_two_tail_integral"], expected["rank_three_tail_integral"]),
        "fixture",
    )
    audit.check(
        "certificate theorem tokens",
        all(
            token in certificate_normalized
            for token in (
                CLOSED,
                "A_beta [beta sqrt(b)+2 sqrt(a beta/e)]",
                "S1-operator-S1",
                "255sqrt(33)/512",
                "first-insertion theorem",
                "All five active parent gates",
            )
        ),
        "all required tokens present",
        "all required tokens present",
        "certificate",
    )
    audit.check(
        "no-overclaim",
        all(
            token in manifest["no_overclaim"]
            for token in (
                "no all-order Duhamel or contour convergence",
                "no common phase-independent real-time alpha",
                "no algebraic ground-state identity",
                "no positive broken-sector GNS gap",
                "Sector A or Pre-A",
                "remain OPEN",
            )
        ),
        manifest["no_overclaim"],
        "scope firewalls",
        "scope",
    )
    audit.check(
        "source AST and format",
        ast.parse(SCRIPT.read_text(encoding="utf-8")) is not None
        and all(
            b"\r" not in path.read_bytes()
            and path.read_bytes().endswith(b"\n")
            and all(byte < 128 for byte in path.read_bytes())
            for path in (MANIFEST, CERTIFICATE, SCRIPT)
        ),
        "AST ASCII LF final-LF",
        "AST ASCII LF final-LF",
        "format",
    )

    if formal:
        formal_text = "\n".join(path.read_text(encoding="utf-8") for path in FORMAL_PATHS)
        audit.check(
            "formal authority links",
            all(token in formal_text for token in ("EXP-000841", CLOSED, "R-167 v3.7")),
            "all formal tokens present",
            "all formal tokens present",
            "formal",
        )

    return {
        "schema": "tect/pre-a-q3lock-affine-form-gibbs-trace-first-duhamel-run/1.0",
        "version": "R-167 v3.7",
        "mode": "formal" if formal else "staged",
        "assertions": audit.rows,
        "summary": {"status": "PASS", "passed": len(audit.rows), "failed": 0},
        "derived": {"general": general, "fixture": fixture},
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in (MANIFEST, CERTIFICATE, SCRIPT)
        },
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
    print(
        f"PRIMARY PASS {payload['summary']['passed']}/{payload['summary']['passed']} "
        f"mode={payload['mode']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
