#!/usr/bin/env python3
"""Primary symbolic verifier for the R-167 v3.6 proof-first package."""

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
SLUG = "pre-a-cp1-st8-q3lock-registered-large-n-corridor-and-l1-first-duhamel-route-split"
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
    REPO / "negative-results/registry.md",
    REPO / "explorations/log.jsonl",
)

CLOSED = (
    "PA-CP1-ST8-Q3LOCK-REGISTERED-LARGE-N-CORRIDOR-FULL-OSCILLATOR-DLR-COEXISTENCE-GROUND-ORDER-CUSP-AND-TIME-ZERO-TANGENT-SPECIALIZATION",
    "PA-CP1-ST8-Q3LOCK-POSITIVE-TIME-TRACE-RITZ-REMOVAL-PLUS-L1-DOMINATED-FIRST-DUHAMEL-INTEGRAL-REDUCTION",
)
NEGATIVE = (
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-POINTWISE-POSITIVE-TIME-TRACE-CLASS-AUTOMATIC-SHORT-TIME-L1-DOMINATION"
)

# Labelled corridor inputs.
MINIMUM_N = sp.Integer(2)
I3_UPPER = sp.Rational(51, 100)
COMMON_BETA = sp.Rational(9, 5)
THETA_DENOMINATOR = sp.Integer(6)
A0_NUMERATOR = sp.Integer(2)
A0_DENOMINATOR = sp.Integer(9)
RHO_SQUARED_NUMERATOR = sp.Integer(9)
RHO_SQUARED_DENOMINATOR = sp.Integer(2)
PRESSURE_NORMALIZATION = sp.Integer(8)
GAP_NORMALIZATION = sp.Integer(2)

# Labelled finite Duhamel fixture.
H_LEVELS = (sp.Integer(1), sp.Integer(2), sp.Integer(3))
B_LEVELS = H_LEVELS
C_SIGNS = (sp.Integer(1), sp.Integer(-1), sp.Integer(1))
DUHAMEL_BETA = sp.Integer(1)
DUHAMEL_S = sp.Rational(1, 3)
RITZ_RANK = sp.Integer(2)

# Labelled short-time fixture.
LOG_BASE = sp.Integer(2)
PARTIAL_RANK = sp.Integer(4)
SPECTRAL_START = sp.Integer(1)
SMALL_TIME_POWER = sp.Integer(-2)


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


def exponential_sum_text(
    levels: tuple[sp.Integer, ...],
    coefficients: tuple[sp.Integer, ...],
    scale: sp.Rational | sp.Integer,
) -> str:
    terms: list[str] = []
    for level, coefficient in zip(levels, coefficients):
        exponent = exact_text(scale * level)
        exponential = f"E^(-{exponent})"
        terms.append(exponential if coefficient == 1 else f"{exact_text(coefficient)}{exponential}")
    return "+".join(terms)


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


def derive_corridor() -> dict[str, Any]:
    n = MINIMUM_N
    theta = n**4 / THETA_DENOMINATOR
    a0 = A0_NUMERATOR * n**4 / A0_DENOMINATOR
    rho_squared_upper = (
        RHO_SQUARED_NUMERATOR
        * I3_UPPER
        / (RHO_SQUARED_DENOMINATOR * n**4)
    )
    beta_upper = sp.factor(3 * I3_UPPER / (1 - rho_squared_upper))
    beta_margin = sp.factor(COMMON_BETA - beta_upper)
    ground_lower = sp.factor(
        n**4 / THETA_DENOMINATOR
        - sp.sqrt(I3_UPPER) * n**2 / (2 * sp.sqrt(2))
    )

    n_symbol = sp.symbols("N", integer=True, positive=True)
    i_symbol = sp.symbols("I_3", positive=True)
    j_symbol = sp.symbols("J_3", positive=True)
    theta_formula = n_symbol**4 / THETA_DENOMINATOR
    a0_formula = A0_NUMERATOR * n_symbol**4 / A0_DENOMINATOR
    rho_formula = 3 * sp.sqrt(i_symbol / 2) / n_symbol**2
    beta_formula = 3 * i_symbol * sp.atanh(rho_formula) / rho_formula
    ground_formula = (
        n_symbol**4 / THETA_DENOMINATOR
        - j_symbol * n_symbol**2 / (2 * sp.sqrt(2))
    )
    return {
        "theta_Q": exact_text(theta),
        "A0": exact_text(a0),
        "rho_squared_upper": exact_text(rho_squared_upper),
        "beta_upper": exact_text(beta_upper),
        "strict_beta_margin": exact_text(beta_margin),
        "ground_lower": str(sp.expand(ground_lower)).replace("**", "^").replace(" ", ""),
        "A0_above_I3_upper": bool(a0 > I3_UPPER),
        "ground_lower_positive": bool(ground_lower > 0),
        "symbolic": {
            "theta_Q": str(theta_formula),
            "A0": str(a0_formula),
            "rho_N": str(rho_formula),
            "beta_star_N": str(beta_formula),
            "rho_star_N": str(ground_formula),
        },
    }


def derive_duhamel() -> dict[str, Any]:
    q = sp.symbols("q", positive=True)
    actual_polynomial = sum(
        b * q ** (3 * h) for h, b in zip(H_LEVELS, B_LEVELS)
    )
    left_polynomial = sum(
        b * q ** (2 * h) for h, b in zip(H_LEVELS, B_LEVELS)
    )
    right_polynomial = sum(
        b * q ** (4 * h) for h, b in zip(H_LEVELS, B_LEVELS)
    )
    holder_difference = sp.factor(
        left_polynomial * right_polynomial - actual_polynomial**2
    )
    expected_factor = q**8 * (q - 1) ** 2 * (
        6 * q**6 + 3 * q**4 + 6 * q**3 + 3 * q**2 + 2
    )

    actual = sum(
        b * sp.exp(-DUHAMEL_BETA * h)
        for h, b in zip(H_LEVELS, B_LEVELS)
    )
    f_left = sum(
        b * sp.exp(-2 * DUHAMEL_S * h)
        for h, b in zip(H_LEVELS, B_LEVELS)
    )
    f_right = sum(
        b * sp.exp(-2 * (DUHAMEL_BETA - DUHAMEL_S) * h)
        for h, b in zip(H_LEVELS, B_LEVELS)
    )
    tail = sum(
        b * sp.exp(-DUHAMEL_BETA * h)
        for h, b in zip(H_LEVELS[int(RITZ_RANK) :], B_LEVELS[int(RITZ_RANK) :])
    )
    return {
        "cross_trace_norm": exponential_sum_text(H_LEVELS, B_LEVELS, DUHAMEL_BETA),
        "holder_bound_squared": (
            "["
            + exponential_sum_text(H_LEVELS, B_LEVELS, 2 * DUHAMEL_S)
            + "]*["
            + exponential_sum_text(
                H_LEVELS, B_LEVELS, 2 * (DUHAMEL_BETA - DUHAMEL_S)
            )
            + "]"
        ),
        "Ritz_tail": exponential_sum_text(
            H_LEVELS[int(RITZ_RANK) :],
            B_LEVELS[int(RITZ_RANK) :],
            DUHAMEL_BETA,
        ),
        "holder_difference_factor": str(holder_difference),
        "holder_factor_identity": bool(
            sp.expand(holder_difference - expected_factor) == 0
        ),
        "holder_strict": bool(
            sp.N(f_left * f_right - actual**2, 50) > 0
        ),
        "contraction_norm": int(max(abs(sign) for sign in C_SIGNS)),
    }


def derive_short_time() -> dict[str, Any]:
    t = sp.symbols("t", positive=True)
    z = sp.exp(-t)
    closed = sp.factor(z / (1 - z) ** 2)
    small_time_limit = sp.limit(t ** (-SMALL_TIME_POWER) * closed, t, 0, dir="+")
    sample_weight = sp.Rational(1, LOG_BASE)
    partial = sum(
        n * sample_weight**n
        for n in range(int(SPECTRAL_START), int(PARTIAL_RANK) + 1)
    )
    full = sp.factor(sample_weight / (1 - sample_weight) ** 2)
    tail = sp.factor(full - partial)
    beta_exponent = exact_text(sp.Integer(SPECTRAL_START))
    beta_cross = f"E^(-{beta_exponent})/(1-E^(-{beta_exponent}))^2"
    return {
        "closed_form": str(closed),
        "full_trace": exact_text(full),
        "partial_trace": exact_text(partial),
        "tail": exact_text(tail),
        "small_time_power": exact_text(SMALL_TIME_POWER),
        "scaled_limit": exact_text(small_time_limit),
        "locally_L1": bool(SMALL_TIME_POWER > -1),
        "fixed_beta_cross_trace": beta_cross,
    }


def build_payload(formal: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    certificate_normalized = " ".join(certificate.split())
    audit = Audit()

    corridor = derive_corridor()
    duhamel = derive_duhamel()
    short_time = derive_short_time()

    audit.check(
        "manifest topology",
        tuple(manifest["closed_gate_ids"]) == CLOSED
        and manifest["negative_ids"] == [NEGATIVE]
        and manifest["exploration_id"] == "EXP-000840",
        (manifest["closed_gate_ids"], manifest["negative_ids"]),
        (CLOSED, [NEGATIVE]),
        "topology",
    )
    audit.check(
        "corridor theta and A0",
        corridor["theta_Q"] == manifest["exact_fixture"]["corridor"]["derived"]["theta_Q"]
        and corridor["A0"] == manifest["exact_fixture"]["corridor"]["derived"]["A0"],
        (corridor["theta_Q"], corridor["A0"]),
        (
            manifest["exact_fixture"]["corridor"]["derived"]["theta_Q"],
            manifest["exact_fixture"]["corridor"]["derived"]["A0"],
        ),
        "corridor",
    )
    audit.check(
        "corridor phase inequality",
        corridor["A0_above_I3_upper"],
        corridor["A0"],
        f">{I3_UPPER}",
        "corridor",
    )
    audit.check(
        "rho squared upper",
        corridor["rho_squared_upper"]
        == manifest["exact_fixture"]["corridor"]["derived"]["rho_squared_upper"],
        corridor["rho_squared_upper"],
        manifest["exact_fixture"]["corridor"]["derived"]["rho_squared_upper"],
        "corridor",
    )
    audit.check(
        "common beta exact upper",
        corridor["beta_upper"]
        == manifest["exact_fixture"]["corridor"]["derived"]["beta_upper"],
        corridor["beta_upper"],
        manifest["exact_fixture"]["corridor"]["derived"]["beta_upper"],
        "corridor",
    )
    audit.check(
        "common beta strict margin",
        corridor["strict_beta_margin"]
        == manifest["exact_fixture"]["corridor"]["derived"]["strict_beta_margin"]
        and sp.sympify(corridor["strict_beta_margin"]) > 0,
        corridor["strict_beta_margin"],
        manifest["exact_fixture"]["corridor"]["derived"]["strict_beta_margin"],
        "corridor",
    )
    audit.check(
        "ground lower",
        corridor["ground_lower"]
        == manifest["exact_fixture"]["ground"]["derived"]["rho_star_lower"]
        and corridor["ground_lower_positive"],
        corridor["ground_lower"],
        manifest["exact_fixture"]["ground"]["derived"]["rho_star_lower"],
        "ground",
    )
    audit.check(
        "Duhamel contraction",
        duhamel["contraction_norm"] == 1,
        duhamel["contraction_norm"],
        1,
        "duhamel",
    )
    audit.check(
        "Duhamel trace fixture",
        duhamel["cross_trace_norm"]
        == manifest["exact_fixture"]["duhamel"]["derived"]["cross_trace_norm"],
        duhamel["cross_trace_norm"],
        manifest["exact_fixture"]["duhamel"]["derived"]["cross_trace_norm"],
        "duhamel",
    )
    audit.check(
        "Duhamel Holder fixture",
        duhamel["holder_bound_squared"]
        == manifest["exact_fixture"]["duhamel"]["derived"]["holder_bound_squared"]
        and duhamel["holder_factor_identity"]
        and duhamel["holder_strict"],
        duhamel["holder_bound_squared"],
        manifest["exact_fixture"]["duhamel"]["derived"]["holder_bound_squared"],
        "duhamel",
    )
    audit.check(
        "Duhamel Ritz tail",
        duhamel["Ritz_tail"]
        == manifest["exact_fixture"]["duhamel"]["derived"]["Ritz_tail"],
        duhamel["Ritz_tail"],
        manifest["exact_fixture"]["duhamel"]["derived"]["Ritz_tail"],
        "duhamel",
    )
    audit.check(
        "short-time full and partial traces",
        short_time["full_trace"]
        == manifest["exact_fixture"]["short_time"]["derived"]["full_trace"]
        and short_time["partial_trace"]
        == manifest["exact_fixture"]["short_time"]["derived"]["partial_trace"],
        (short_time["full_trace"], short_time["partial_trace"]),
        (
            manifest["exact_fixture"]["short_time"]["derived"]["full_trace"],
            manifest["exact_fixture"]["short_time"]["derived"]["partial_trace"],
        ),
        "short_time",
    )
    audit.check(
        "short-time tail",
        short_time["tail"]
        == manifest["exact_fixture"]["short_time"]["derived"]["tail"],
        short_time["tail"],
        manifest["exact_fixture"]["short_time"]["derived"]["tail"],
        "short_time",
    )
    audit.check(
        "short-time power and nonintegrability",
        short_time["small_time_power"]
        == manifest["exact_fixture"]["short_time"]["derived"]["small_time_power"]
        and short_time["scaled_limit"] == "1"
        and short_time["locally_L1"]
        is manifest["exact_fixture"]["short_time"]["derived"]["locally_L1"],
        (short_time["small_time_power"], short_time["locally_L1"]),
        (
            manifest["exact_fixture"]["short_time"]["derived"]["small_time_power"],
            manifest["exact_fixture"]["short_time"]["derived"]["locally_L1"],
        ),
        "short_time",
    )
    audit.check(
        "certificate theorem tokens",
        all(
            token in certificate_normalized
            for token in (
                CLOSED[0],
                CLOSED[1],
                NEGATIVE,
                "4896\\over2741",
                "m_{L,N}^2",
                "g_\\beta\\notin L^1",
                "does not refute the existence",
            )
        ),
        "required tokens present",
        "all required tokens present",
        "certificate",
    )
    audit.check(
        "no-overclaim",
        all(
            token in manifest["no_overclaim"]
            for token in (
                "no common phase-independent real-time alpha",
                "algebraic ground-state",
                "DFFR/Ritz branch identity",
                "GNS gap",
                "Sector A or Pre-A",
                "remain OPEN",
            )
        ),
        manifest["no_overclaim"],
        "scope firewalls",
        "scope",
    )
    audit.check(
        "source format",
        all(
            b"\r" not in path.read_bytes()
            and path.read_bytes().endswith(b"\n")
            and all(byte < 128 for byte in path.read_bytes())
            for path in (MANIFEST, CERTIFICATE, SCRIPT)
        ),
        "ASCII LF final-LF",
        "ASCII LF final-LF",
        "format",
    )

    if formal:
        formal_text = "\n".join(path.read_text(encoding="utf-8") for path in FORMAL_PATHS)
        audit.check(
            "formal authority links",
            all(token in formal_text for token in ("EXP-000840", CLOSED[0], CLOSED[1], NEGATIVE, "R-167 v3.6")),
            "all formal tokens present",
            "all formal tokens present",
            "formal",
        )

    return {
        "schema": "tect/pre-a-q3lock-registered-large-n-corridor-l1-first-duhamel-run/1.0",
        "version": "R-167 v3.6",
        "mode": "formal" if formal else "staged",
        "assertions": audit.rows,
        "summary": {
            "status": "PASS",
            "passed": len(audit.rows),
            "failed": 0,
        },
        "derived": {
            "corridor": corridor,
            "duhamel": duhamel,
            "short_time": short_time,
        },
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
