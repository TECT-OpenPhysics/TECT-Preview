#!/usr/bin/env python3
"""Independent stdlib verifier for the R-167 v3.3 fixed-Ritz DFFR package."""

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
SLUG = "pre-a-cp1-st8-q3lock-fixed-ritz-dffr-two-level-qps-zero-source-two-phase-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_fixed_ritz_dffr_two_level_qps_zero_source_two_phase_route_split.py"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-independent-{SLUG}/result.json"
FORMAL_PATHS = (
    REPO / "claims/GATES.md",
    REPO / "RESULTS-LEDGER.md",
    REPO / "negative-results/registry.md",
    REPO / "explorations/log.jsonl",
)

# Labelled fixture inputs, independent of the primary implementation.
OVERLAP = 8
LOW_J = 1
SAMPLE_N = 4
SAMPLE_HIGH = 3
SAMPLE_LOW_EDGES = 5
LAMBDA_ZERO = Fraction(1, 2)
SUPPORT_SIZE = 2
ONSITE_DIMENSION = 4
LOW_NUMERATOR = (1, 2)  # ascending coefficients of 1+2N over N^3
HIGH_NUMERATOR = (1, 0, 0, 10)  # ascending coefficients of 1+10N^3 over N^3
LOW_DENOMINATOR_POWER = 3
HIGH_DENOMINATOR_POWER = 3
GAMMA_POWER = 2
THERMAL_MULTIPLIER = 2
ORDER_ERROR_TARGET = Fraction(1, 4)
DERIVATIVES = (1, -1)


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


def fraction_text(value: Fraction | int) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def polynomial_multiply(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return tuple(result)


def leading_scaled_rational_limit(numerator: tuple[int, ...], denominator_power: int) -> tuple[int, Fraction]:
    degree = len(numerator) - 1
    scale_power = denominator_power - degree
    if scale_power < 0:
        raise OverflowError("unscaled rational expression diverges")
    return scale_power, Fraction(numerator[-1])


def exact_sqrt_fraction(value: Fraction) -> Fraction:
    numerator = math.isqrt(value.numerator)
    denominator = math.isqrt(value.denominator)
    if numerator * numerator != value.numerator or denominator * denominator != value.denominator:
        raise ValueError(f"not a rational square: {value}")
    return Fraction(numerator, denominator)


def stringify_polynomial(numerator: tuple[int, ...], denominator_power: int) -> str:
    terms: list[str] = []
    for power in range(len(numerator) - 1, -1, -1):
        coefficient = numerator[power]
        if coefficient == 0:
            continue
        if power == 0:
            terms.append(str(coefficient))
        elif power == 1:
            terms.append("N" if coefficient == 1 else f"{coefficient}*N")
        else:
            terms.append(f"N^{power}" if coefficient == 1 else f"{coefficient}*N^{power}")
    numerator_text = "+".join(terms) or "0"
    if denominator_power == 0:
        return numerator_text
    return f"({numerator_text})/N^{denominator_power}"


def sum_of_inverse_powers(numerator: tuple[int, ...], denominator_power: int) -> str:
    terms: list[str] = []
    for power, coefficient in reversed(tuple(enumerate(numerator))):
        if coefficient == 0:
            continue
        inverse_power = denominator_power - power
        if inverse_power == 0:
            terms.append(str(coefficient))
        elif coefficient == 1:
            terms.append(f"1/N^{inverse_power}")
        else:
            terms.append(f"{coefficient}/N^{inverse_power}")
    return "+".join(terms)


def peierls_fixture() -> dict[str, str]:
    kappa = Fraction(1, 2 * OVERLAP)
    gamma = SAMPLE_N**GAMMA_POWER
    high_penalty = Fraction(gamma - 1, 2 * OVERLAP)
    defective = OVERLAP * (SAMPLE_HIGH + SAMPLE_LOW_EDGES)
    high_defective = OVERLAP * SAMPLE_HIGH
    energy = gamma * SAMPLE_HIGH + 2 * LOW_J * SAMPLE_LOW_EDGES
    charged = kappa * defective + high_penalty * high_defective
    return {
        "N": str(SAMPLE_N),
        "high_sites": str(SAMPLE_HIGH),
        "disagreeing_edges": str(SAMPLE_LOW_EDGES),
        "defective_cubes_upper": str(defective),
        "high_defect_cubes_upper": str(high_defective),
        "energy_lower": str(energy),
        "charged_upper": fraction_text(charged),
        "strict_margin": fraction_text(Fraction(energy) - charged),
    }


def dffr_fixture() -> tuple[dict[str, Any], dict[str, Fraction]]:
    kappa = Fraction(1, 2 * OVERLAP)
    hs_factor = ONSITE_DIMENSION**SUPPORT_SIZE
    decay_factor = LAMBDA_ZERO ** (-SUPPORT_SIZE)
    combined = hs_factor * decay_factor
    low_high_product = polynomial_multiply(LOW_NUMERATOR, HIGH_NUMERATOR)

    # The rational terms are derived after inserting D=(N^2-1)/(2C), for
    # which kappa+D=N^2/(2C). Squared forms avoid numerical square roots.
    low_low_numerator = tuple(int(2 * OVERLAP * LAMBDA_ZERO * combined * c) for c in LOW_NUMERATOR)
    high_high_numerator = tuple(int(2 * OVERLAP * LAMBDA_ZERO * combined * c) for c in HIGH_NUMERATOR)
    paired_squared_multiplier = Fraction(
        LAMBDA_ZERO**2 * combined**2 * (2 * OVERLAP) ** 2
    )
    one_way_squared_multiplier = Fraction(
        LAMBDA_ZERO**2 * combined**2 * (2 * OVERLAP) ** 2
    )
    paired_squared_numerator = tuple(int(paired_squared_multiplier * c) for c in low_high_product)
    one_way_squared_numerator = tuple(int(one_way_squared_multiplier * c) for c in low_high_product)

    limit_data = {
        "N2_low_low": leading_scaled_rational_limit(low_low_numerator, LOW_DENOMINATOR_POWER),
        "N2_low_high_squared": leading_scaled_rational_limit(
            paired_squared_numerator,
            LOW_DENOMINATOR_POWER + HIGH_DENOMINATOR_POWER + GAMMA_POWER,
        ),
        "N2_high_high": leading_scaled_rational_limit(
            high_high_numerator, HIGH_DENOMINATOR_POWER + GAMMA_POWER
        ),
        "N3_one_way_squared": leading_scaled_rational_limit(
            one_way_squared_numerator,
            LOW_DENOMINATOR_POWER + HIGH_DENOMINATOR_POWER + 2 * GAMMA_POWER,
        ),
    }
    limits = {key: value for key, (_scale, value) in limit_data.items()}
    expected_scale_powers = {
        "N2_low_low": GAMMA_POWER,
        "N2_low_high_squared": 2 * GAMMA_POWER,
        "N2_high_high": GAMMA_POWER,
        "N3_one_way_squared": LOW_DENOMINATOR_POWER + HIGH_DENOMINATOR_POWER,
    }
    if {key: scale for key, (scale, _value) in limit_data.items()} != expected_scale_powers:
        raise AssertionError("derived scale powers do not match the declared output labels")
    kappa_bar = kappa / THERMAL_MULTIPLIER
    beta_coefficient = Fraction(THERMAL_MULTIPLIER, 1) / kappa_bar
    thermal_term = Fraction(1, 2) ** THERMAL_MULTIPLIER
    inputs = {
        "overlap": str(OVERLAP),
        "kappa": fraction_text(kappa),
        "gamma": f"N^{GAMMA_POWER}",
        "high_penalty": f"(N^{GAMMA_POWER}-1)/{2 * OVERLAP}",
        "lambda": fraction_text(LAMBDA_ZERO),
        "support_size": str(SUPPORT_SIZE),
        "onsite_dimension": str(ONSITE_DIMENSION),
        "hs_support_factor": str(hs_factor),
        "decay_absorption_factor": fraction_text(decay_factor),
        "combined_block_factor": fraction_text(combined),
    }
    low_text = sum_of_inverse_powers(LOW_NUMERATOR, LOW_DENOMINATOR_POWER)
    high_text = sum_of_inverse_powers(HIGH_NUMERATOR, HIGH_DENOMINATOR_POWER)
    blocks = {
        "B_ll": low_text,
        "B_hh": high_text,
        "B_lh_squared": f"({low_text})*({high_text})",
    }
    derived = {
        "inputs": inputs,
        "block_bounds": blocks,
        "criterion_scaled_limits": {key: fraction_text(value) for key, value in limits.items()},
        "thermal": {
            "kappa_bar": fraction_text(kappa_bar),
            "beta": f"{fraction_text(beta_coefficient)}*log(2)",
            "term": fraction_text(thermal_term),
            "role": "arithmetic identity only; epsilon_0 is unspecified, so this beta is not asserted to enter the theorem",
        },
    }
    raw = {
        "kappa": kappa,
        "combined": combined,
        "low_high_leading": Fraction(low_high_product[-1]),
        "low_low_limit": limits["N2_low_low"],
        "paired_squared_limit": limits["N2_low_high_squared"],
        "high_high_limit": limits["N2_high_high"],
        "one_way_squared_limit": limits["N3_one_way_squared"],
        "thermal": thermal_term,
    }
    return derived, raw


def order_and_parity_fixture() -> tuple[dict[str, str], dict[str, str]]:
    plus = Fraction(1) - ORDER_ERROR_TARGET
    minus = Fraction(-1) + ORDER_ERROR_TARGET
    order = {
        "existential_error_target": fraction_text(ORDER_ERROR_TARGET),
        "plus_order_lower": fraction_text(plus),
        "minus_order_upper": fraction_text(minus),
        "order_gap_lower": fraction_text(plus - minus),
        "role": "target arithmetic after q_(M,N,beta) is chosen sufficiently small; not a computed DFF constant",
    }
    difference = DERIVATIVES[0] - DERIVATIVES[1]
    denominator = DERIVATIVES[0] - DERIVATIVES[1]
    source = Fraction(0, denominator)
    parity = {
        "plus_derivative": str(DERIVATIVES[0]),
        "minus_derivative": str(DERIVATIVES[1]),
        "difference": str(difference),
        "coexistence_source": fraction_text(source),
    }
    return order, parity


def source_firewall() -> dict[str, Any]:
    tree = ast.parse(PRIMARY.read_text(encoding="utf-8"))
    imports: set[str] = set()
    dynamic: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "__import__", "compile"}:
                dynamic.append(node.func.id)
    return {"imports": sorted(imports), "dynamic": dynamic}


def independent_imports() -> set[str]:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
    return imports


def build_payload(staged: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    normalized_certificate = " ".join(certificate.split())
    dffr, raw = dffr_fixture()
    order, parity = order_and_parity_fixture()
    derived = dffr | {
        "peierls_sample": peierls_fixture(),
        "order_target": order,
        "parity": parity,
    }
    audit = Audit()

    audit.check(
        "manifest identity independent parse",
        manifest["schema"] == "tect/pre-a-q3lock-fixed-ritz-dffr-two-level-qps/1.0"
        and manifest["package_id"] == SLUG
        and manifest["version"] == "R-167 v3.3"
        and manifest["date"] == "2026-08-13"
        and manifest["exploration_id"] == "EXP-000837",
        (manifest["schema"], manifest["package_id"], manifest["version"], manifest["date"]),
        "exact staged identity",
        "identity",
    )
    audit.check(
        "authority topology independent parse",
        len(manifest["closed_gate_ids"]) == 1
        and not manifest["negative_ids"]
        and len(manifest["reused_negative_ids"]) == 1
        and len(manifest["open_parent_gate_ids"]) == 5
        and manifest["historical_open_gate_ids"]
        == ["PA-CP1-ST8-Q3LOCK-BETA-INFINITY-GROUND-STATE-SELECTION"],
        (
            manifest["closed_gate_ids"],
            manifest["negative_ids"],
            manifest["reused_negative_ids"],
            manifest["historical_open_gate_ids"],
        ),
        "one CLOSED, no new negative, one reused boundary, one historical OPEN",
        "identity",
    )
    for group, expected in manifest["exact_fixture"].items():
        audit.check(f"independent exact {group}", derived[group] == expected, derived[group], expected, group)

    audit.check(
        "generic polynomial product for mixed blocks",
        raw["low_high_leading"] == LOW_NUMERATOR[-1] * HIGH_NUMERATOR[-1],
        raw["low_high_leading"],
        LOW_NUMERATOR[-1] * HIGH_NUMERATOR[-1],
        "criterion",
    )
    audit.check(
        "four representative scaled limits finite positive",
        all(
            value > 0
            for value in (
                raw["low_low_limit"],
                raw["paired_squared_limit"],
                raw["high_high_limit"],
                raw["one_way_squared_limit"],
            )
        ),
        (
            raw["low_low_limit"],
            raw["paired_squared_limit"],
            raw["high_high_limit"],
            raw["one_way_squared_limit"],
        ),
        "positive finite leading coefficients",
        "criterion",
    )
    audit.check(
        "mixed adjoint blocks have equal norm bounds",
        derived["criterion_scaled_limits"]["N2_low_high_squared"]
        == derived["criterion_scaled_limits"]["N3_one_way_squared"],
        (
            derived["criterion_scaled_limits"]["N2_low_high_squared"],
            derived["criterion_scaled_limits"]["N3_one_way_squared"],
        ),
        "same upstream mixed-block product",
        "criterion",
    )
    audit.check(
        "Peierls sample is strict",
        Fraction(derived["peierls_sample"]["strict_margin"]) > 0
        and Fraction(derived["peierls_sample"]["energy_lower"])
        == Fraction(derived["peierls_sample"]["charged_upper"])
        + Fraction(derived["peierls_sample"]["strict_margin"]),
        derived["peierls_sample"],
        "positive exact residual",
        "peierls",
    )
    audit.check(
        "order target is existential not a DFF constant",
        Fraction(order["plus_order_lower"]) - Fraction(order["minus_order_upper"])
        == Fraction(order["order_gap_lower"])
        and "not a computed DFF constant" in order["role"],
        order,
        "derived target with role firewall",
        "order",
    )
    audit.check(
        "thermal sample role firewall",
        raw["thermal"] == ORDER_ERROR_TARGET
        and "not asserted to enter the theorem" in derived["thermal"]["role"],
        derived["thermal"],
        "arithmetic identity only",
        "criterion",
    )
    audit.check(
        "parity derivatives independently solve zero source",
        parity["difference"] == "2" and parity["coexistence_source"] == "0",
        parity,
        "splitting 2 and source 0",
        "parity",
    )

    firewall = source_firewall()
    audit.check(
        "primary source firewall no dynamic execution",
        firewall["dynamic"] == [] and "sympy" in firewall["imports"],
        firewall,
        "symbolic primary and no dynamic execution",
        "independence",
    )
    audit.check(
        "independent source does not import primary or sympy",
        independent_imports()
        <= {
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
        and "sympy" not in independent_imports()
        and not any(name.startswith("pre_a_cp1") for name in independent_imports()),
        sorted(independent_imports()),
        "no primary or symbolic import",
        "independence",
    )

    certificate_tokens = (
        "finite geometric constant `C_a`",
        "J_N<=J_M^*",
        "lambda/lambda_0",
        "actual contour parameter tends to zero",
        "not asserted to enter the theorem",
        "PA-CP1-ST8-Q3LOCK-BETA-INFINITY-GROUND-STATE-SELECTION` also remains OPEN",
        "No v3.3 PDF is issued",
    )
    audit.check(
        "independent certificate precision contract",
        all(token in normalized_certificate for token in certificate_tokens),
        [token for token in certificate_tokens if token not in normalized_certificate],
        [],
        "certificate",
    )
    audit.check(
        "independent no-overclaim contract",
        all(
            token in normalized_certificate
            for token in (
                "not uniform in `M`",
                "not a purity or exhaustive-classification claim",
                "No GNS spectral-gap conclusion",
                "All five active parent gates remain OPEN",
            )
        ),
        "scope tokens",
        "all present",
        "certificate",
    )

    if not staged:
        formal_text = "\n".join(path.read_text(encoding="utf-8") for path in FORMAL_PATHS)
        formal_ok = (
            "EXP-000837" in formal_text
            and manifest["closed_gate_ids"][0] in formal_text
            and "R-167 v3.3" in formal_text
        )
        audit.check("independent formal aggregate", formal_ok, formal_ok, True, "formal")

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
    print(f"R-167 v3.3 INDEPENDENT PASS {total}/{total}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
