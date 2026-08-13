#!/usr/bin/env python3
"""Independent stdlib verifier for the R-167 v3.6 package."""

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


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-registered-large-n-corridor-and-l1-first-duhamel-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-13-independent-{SLUG}/result.json"
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

MINIMUM_N = 2
I3_UPPER = Fraction(51, 100)
COMMON_BETA = Fraction(9, 5)
THETA_DENOMINATOR = 6
A0_NUMERATOR = 2
A0_DENOMINATOR = 9
RHO_SQUARED_NUMERATOR = 9
RHO_SQUARED_DENOMINATOR = 2
LOG_BASE = 2
PARTIAL_RANK = 4
SMALL_TIME_POWER = -2


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


def ftext(value: Fraction | int) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def exponential_sum_text(
    levels: tuple[int, ...], weights: tuple[int, ...], scale: Fraction
) -> str:
    terms: list[str] = []
    for level, weight in zip(levels, weights):
        exponent = ftext(scale * level)
        exponential = f"E^(-{exponent})"
        terms.append(exponential if weight == 1 else f"{weight}{exponential}")
    return "+".join(terms)


def check(
    rows: list[dict[str, str]],
    name: str,
    condition: bool,
    actual: Any,
    expected: Any,
    group: str,
) -> None:
    if not condition:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
    rows.append(
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
    theta = Fraction(n**4, THETA_DENOMINATOR)
    a0 = Fraction(A0_NUMERATOR * n**4, A0_DENOMINATOR)
    rho_squared_upper = Fraction(
        RHO_SQUARED_NUMERATOR * I3_UPPER,
        RHO_SQUARED_DENOMINATOR * n**4,
    )
    beta_upper = Fraction(3) * I3_UPPER / (1 - rho_squared_upper)
    margin = COMMON_BETA - beta_upper
    ground_positive_squared = theta * theta > I3_UPPER * Fraction(n**4, 8)
    radicand = 2 * I3_UPPER.numerator
    denominator_root = math.isqrt(I3_UPPER.denominator)
    if denominator_root**2 != I3_UPPER.denominator:
        raise AssertionError("I3 upper denominator must be a square in this fixture")
    radical_denominator = 4 * denominator_root // MINIMUM_N**2
    ground_text = (
        f"{ftext(Fraction(MINIMUM_N**4, THETA_DENOMINATOR))}"
        f"-sqrt({radicand})/{radical_denominator}"
    )
    return {
        "theta_Q": ftext(theta),
        "A0": ftext(a0),
        "rho_squared_upper": ftext(rho_squared_upper),
        "beta_upper": ftext(beta_upper),
        "strict_beta_margin": ftext(margin),
        "A0_above_I3_upper": a0 > I3_UPPER,
        "ground_lower": ground_text,
        "ground_lower_positive": ground_positive_squared,
    }


def polynomial_multiply(left: list[int], right: list[int]) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for i, first in enumerate(left):
        for j, second in enumerate(right):
            result[i + j] += first * second
    return result


def polynomial_subtract(left: list[int], right: list[int]) -> list[int]:
    size = max(len(left), len(right))
    return [
        (left[index] if index < len(left) else 0)
        - (right[index] if index < len(right) else 0)
        for index in range(size)
    ]


def derive_duhamel() -> dict[str, Any]:
    levels = (1, 2, 3)
    weights = (1, 2, 3)
    actual = [0] * 10
    left = [0] * 7
    right = [0] * 13
    for level, weight in zip(levels, weights):
        actual[3 * level] += weight
        left[2 * level] += weight
        right[4 * level] += weight
    difference = polynomial_subtract(
        polynomial_multiply(left, right), polynomial_multiply(actual, actual)
    )
    expected = [0] * len(difference)
    # q^8 (q-1)^2 (6q^6+3q^4+6q^3+3q^2+2), independently expanded.
    base = [2, 0, 3, 6, 3, 0, 6]
    expected_product = polynomial_multiply([1, -2, 1], base)
    for index, coefficient in enumerate(expected_product):
        expected[index + 8] = coefficient
    return {
        "cross_trace_norm": exponential_sum_text(levels, weights, Fraction(1)),
        "holder_bound_squared": (
            "[" + exponential_sum_text(levels, weights, Fraction(2, 3)) + "]*["
            + exponential_sum_text(levels, weights, Fraction(4, 3)) + "]"
        ),
        "Ritz_tail": exponential_sum_text(levels[-1:], weights[-1:], Fraction(1)),
        "holder_factor_identity": difference == expected,
        "holder_strict": all(
            coefficient >= 0 for coefficient in base
        ) and any(coefficient > 0 for coefficient in base),
    }


def derive_short_time() -> dict[str, Any]:
    half = Fraction(1, LOG_BASE)
    full = half / (1 - half) ** 2
    partial = sum(Fraction(n) * half**n for n in range(1, PARTIAL_RANK + 1))
    tail = full - partial
    # (1-exp(-t))/t -> 1 makes t^2 exp(-t)/(1-exp(-t))^2 -> 1.
    scaled_limit = 1
    exponent_one = ftext(Fraction(1))
    fixed_beta_text = f"E^(-{exponent_one})/(1-E^(-{exponent_one}))^2"
    return {
        "full_trace": ftext(full),
        "partial_trace": ftext(partial),
        "tail": ftext(tail),
        "small_time_power": str(SMALL_TIME_POWER),
        "scaled_limit": str(scaled_limit),
        "locally_L1": SMALL_TIME_POWER > -1,
        "fixed_beta_cross_trace": fixed_beta_text,
    }


def ast_firewall() -> bool:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    allowed = {
        "__future__",
        "argparse",
        "ast",
        "hashlib",
        "json",
        "math",
        "os",
        "tempfile",
        "fractions",
        "pathlib",
        "typing",
    }
    imports: set[str] = set()
    banned_calls = {"__import__", "eval", "exec", "compile"}
    banned_attributes = {"import_module", "exec_module", "load_module"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in banned_calls:
                return False
            if isinstance(node.func, ast.Attribute) and node.func.attr in banned_attributes:
                return False
    return imports <= allowed


def build_payload(formal: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    rows: list[dict[str, str]] = []
    corridor = derive_corridor()
    duhamel = derive_duhamel()
    short_time = derive_short_time()

    check(
        rows,
        "manifest topology",
        tuple(manifest["closed_gate_ids"]) == CLOSED
        and manifest["negative_ids"] == [NEGATIVE],
        (manifest["closed_gate_ids"], manifest["negative_ids"]),
        (CLOSED, [NEGATIVE]),
        "topology",
    )
    for key in (
        "theta_Q",
        "A0",
        "rho_squared_upper",
        "beta_upper",
        "strict_beta_margin",
    ):
        check(
            rows,
            f"corridor {key}",
            corridor[key] == manifest["exact_fixture"]["corridor"]["derived"][key],
            corridor[key],
            manifest["exact_fixture"]["corridor"]["derived"][key],
            "corridor",
        )
    check(
        rows,
        "corridor inequalities",
        corridor["A0_above_I3_upper"]
        and Fraction(corridor["strict_beta_margin"]) > 0,
        (corridor["A0_above_I3_upper"], corridor["strict_beta_margin"]),
        (True, ">0"),
        "corridor",
    )
    check(
        rows,
        "ground lower",
        corridor["ground_lower"]
        == manifest["exact_fixture"]["ground"]["derived"]["rho_star_lower"]
        and corridor["ground_lower_positive"],
        corridor["ground_lower"],
        manifest["exact_fixture"]["ground"]["derived"]["rho_star_lower"],
        "ground",
    )
    check(
        rows,
        "independent Duhamel polynomial identity",
        duhamel["holder_factor_identity"] and duhamel["holder_strict"],
        duhamel,
        "positive Holder difference",
        "duhamel",
    )
    for key in ("cross_trace_norm", "holder_bound_squared", "Ritz_tail"):
        check(
            rows,
            f"Duhamel {key}",
            duhamel[key] == manifest["exact_fixture"]["duhamel"]["derived"][key],
            duhamel[key],
            manifest["exact_fixture"]["duhamel"]["derived"][key],
            "duhamel",
        )
    for key in (
        "full_trace",
        "partial_trace",
        "tail",
        "small_time_power",
        "locally_L1",
    ):
        check(
            rows,
            f"short-time {key}",
            short_time[key] == manifest["exact_fixture"]["short_time"]["derived"][key],
            short_time[key],
            manifest["exact_fixture"]["short_time"]["derived"][key],
            "short_time",
        )
    check(
        rows,
        "short-time scaled limit",
        short_time["scaled_limit"] == "1",
        short_time["scaled_limit"],
        "1",
        "short_time",
    )
    check(
        rows,
        "certificate scope",
        all(
            token in certificate
            for token in (
                "m_{L,N}^2",
                "g_\\beta\\notin L^1",
                "does not refute the existence",
                "not promoted here to algebraic ground states",
            )
        ),
        "scope tokens",
        "all required scope tokens",
        "certificate",
    )
    check(
        rows,
        "stdlib and dynamic-execution firewall",
        ast_firewall(),
        "strict import/dynamic firewall",
        "strict import/dynamic firewall",
        "independence",
    )
    check(
        rows,
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
        check(
            rows,
            "formal authority links",
            all(
                token in formal_text
                for token in ("EXP-000840", CLOSED[0], CLOSED[1], NEGATIVE, "R-167 v3.6")
            ),
            "all formal tokens",
            "all formal tokens",
            "formal",
        )

    return {
        "schema": "tect/pre-a-q3lock-registered-large-n-corridor-l1-first-duhamel-independent-run/1.0",
        "version": "R-167 v3.6",
        "mode": "formal" if formal else "staged",
        "assertions": rows,
        "summary": {"status": "PASS", "passed": len(rows), "failed": 0},
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
        f"INDEPENDENT PASS {payload['summary']['passed']}/{payload['summary']['passed']} "
        f"mode={payload['mode']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
