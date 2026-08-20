#!/usr/bin/env python3
"""Derive the exact R-169 v1.4 legacy common-Bohr route split.

Purpose: independently recount the declared signed supports, reconstruct the
corrected legacy scalar Bohr polynomial, and separate fixed-intensity,
unconstrained-radial, finite-grid, Hartree and current P1 owners.
Convention: Math396 cosine amplitude a_cos equals twice the signed Fourier
coefficient; HEX relation coordinates are used only for tuple counting.
Formula: f=(mu2/2)I+(lambda/2)K4 I^2+(gamma/3)K6 I^3, with
K4=N4/N2^2 and K6=N6/N2^3.
"""

from __future__ import annotations

import argparse
import base64
from collections import Counter
import hashlib
import itertools
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-t055-legacy-sma-common-bohr-moment-radial-owner-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-14-primary-{SLUG}/result.json"
)
FAMILY_ORDER = ("BCC", "FCC", "HEX", "LAM")


def normalized_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def source_content_sha256(path: Path) -> str:
    """Hash the preserved source payload, decoding ASCII wrappers when present."""
    raw = path.read_bytes()
    if path.name.endswith(".source.json"):
        wrapper = json.loads(raw.decode("ascii"))
        if wrapper.get("encoding") != "base64":
            raise AssertionError(f"unsupported source wrapper encoding: {path}")
        raw = base64.b64decode(wrapper["payload_base64"], validate=True)
        if int(wrapper["bytes"]) != len(raw) or wrapper["sha256"] != hashlib.sha256(raw).hexdigest():
            raise AssertionError(f"invalid source wrapper payload: {path}")
    return hashlib.sha256(raw).hexdigest()


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


def supports() -> dict[str, tuple[tuple[int, ...], ...]]:
    bcc = tuple(sorted(v for v in itertools.product((-1, 0, 1), repeat=3) if sum(x * x for x in v) == 2))
    fcc = tuple(sorted(itertools.product((-1, 1), repeat=3)))
    hex_positive = ((1, 0), (0, 1), (-1, -1))
    hex_support = tuple(sorted(set(hex_positive + tuple(tuple(-x for x in v) for v in hex_positive))))
    lam = ((-1,), (1,))
    return {"BCC": bcc, "FCC": fcc, "HEX": hex_support, "LAM": lam}


def zero_sum_count(support: tuple[tuple[int, ...], ...], order: int) -> int:
    dimension = len(support[0])
    counts: Counter[tuple[int, ...]] = Counter({(0,) * dimension: 1})
    for _ in range(order):
        updated: Counter[tuple[int, ...]] = Counter()
        for total, multiplicity in counts.items():
            for vector in support:
                updated[tuple(total[index] + vector[index] for index in range(dimension))] += multiplicity
        counts = updated
    return counts[(0,) * dimension]


def fraction_string(value: sp.Expr) -> str:
    value = sp.factor(value)
    if not value.is_Rational:
        raise AssertionError(f"expected rational, got {value}")
    return str(value)


def surd_parts(value: sp.Expr) -> dict[str, Any]:
    expanded = sp.expand(value)
    radicals = sorted(
        (
            power
            for power in expanded.atoms(sp.Pow)
            if power.exp == sp.Rational(1, 2) and power.base.is_Integer
        ),
        key=lambda item: int(item.base),
    )
    if not radicals:
        return {"rational": fraction_string(expanded), "sqrt_coefficient": "0", "sqrt_radicand": 1}
    if len(radicals) != 1:
        raise AssertionError(f"expected one radical, got {radicals}")
    radical = radicals[0]
    coefficient = sp.factor(expanded.coeff(radical))
    rational = sp.factor(expanded - coefficient * radical)
    if not rational.is_Rational or not coefficient.is_Rational:
        raise AssertionError(f"noncanonical surd {value}")
    return {
        "rational": str(rational),
        "sqrt_coefficient": str(coefficient),
        "sqrt_radicand": int(radical.base),
    }


def algebraic_floor_millionths(value: sp.Expr) -> int:
    return int(sp.floor(sp.factor(value) * sp.Integer(10**6)))


def published_expression(text: str) -> sp.Expr:
    """Parse the manifest's compact radical notation into an exact expression."""
    explicit_products = re.sub(r"(?<=\d)sqrt\(", "*sqrt(", text)
    return sp.factor(sp.sympify(explicit_products, locals={"sqrt": sp.sqrt}))


def v2(value: int) -> int:
    """Return the exact two-adic valuation of a positive integer."""
    if value <= 0:
        raise ValueError("v2 requires a positive integer")
    exponent = 0
    while value % 2 == 0:
        value //= 2
        exponent += 1
    return exponent


def derive_exact(manifest: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["registered_inputs"]
    mu2 = sp.Rational(inputs["mu2"])
    lam = sp.Rational(inputs["lambda"])
    gamma = sp.Rational(inputs["gamma"])
    intensity = sp.Rational(inputs["production_intensity"])
    cap_marker = sp.Rational(inputs["b1_intensity_cap"])
    conversion = sp.Integer(inputs["amplitude_conversion"])

    support_map = supports()
    moments: dict[str, dict[str, Any]] = {}
    coefficients: dict[str, list[str]] = {}
    fixed_values: dict[str, str] = {}
    fixed_derivatives: dict[str, str] = {}
    radial_minimizers: dict[str, dict[str, Any]] = {}
    radial_minimum_energies: dict[str, dict[str, Any]] = {}
    root_brackets: dict[str, list[int]] = {}
    energy_brackets: dict[str, list[int]] = {}
    cap_separation: dict[str, bool] = {}
    raw_roots: dict[str, sp.Expr] = {}
    raw_energies: dict[str, sp.Expr] = {}

    symbol = sp.Symbol("I", real=True)
    for family in FAMILY_ORDER:
        support = support_map[family]
        n2 = zero_sum_count(support, 2)
        n4 = zero_sum_count(support, 4)
        n6 = zero_sum_count(support, 6)
        k4 = sp.Rational(n4, n2**2)
        k6 = sp.Rational(n6, n2**3)
        moments[family] = {"N2": n2, "N4": n4, "N6": n6, "K4": str(k4), "K6": str(k6)}

        a = sp.factor(mu2 / 2)
        b = sp.factor(lam * k4 / 2)
        c = sp.factor(gamma * k6 / 3)
        polynomial = sp.expand(a * symbol + b * symbol**2 + c * symbol**3)
        derivative = sp.diff(polynomial, symbol)
        coefficients[family] = [str(a), str(b), str(c)]
        fixed_values[family] = fraction_string(polynomial.subs(symbol, intensity))
        fixed_derivatives[family] = fraction_string(derivative.subs(symbol, intensity))

        discriminant = sp.factor(b * b - 3 * a * c)
        smaller = sp.factor((-b - sp.sqrt(discriminant)) / (3 * c))
        larger = sp.factor((-b + sp.sqrt(discriminant)) / (3 * c))
        second = sp.diff(polynomial, symbol, 2)
        minimum_energy = sp.factor(polynomial.subs(symbol, larger))
        if sp.simplify(second.subs(symbol, smaller) < 0) is not sp.true:
            raise AssertionError(f"{family} smaller root is not a local maximum")
        if sp.simplify(second.subs(symbol, larger) > 0) is not sp.true:
            raise AssertionError(f"{family} larger root is not a local minimum")
        radial_minimizers[family] = {
            **surd_parts(larger),
            "f_second_positive": True,
            "smaller_f_second_negative": True,
        }
        radial_minimum_energies[family] = surd_parts(minimum_energy)
        root_floor = algebraic_floor_millionths(larger)
        energy_floor = algebraic_floor_millionths(minimum_energy)
        root_brackets[family] = [root_floor, root_floor + 1]
        energy_brackets[family] = [energy_floor, energy_floor + 1]
        cap_separation[family] = bool(sp.simplify(larger > cap_marker))
        raw_roots[family] = larger
        raw_energies[family] = minimum_energy

    fixed_order = sorted(FAMILY_ORDER, key=lambda family: sp.Rational(fixed_values[family]))
    radial_order = sorted(FAMILY_ORDER, key=lambda family: energy_brackets[family][0])

    hex_vectors = []
    for vector in inputs["hex_euclidean_vectors_r_plus_s_sqrt3"]:
        parsed = []
        for rational, sqrt_coefficient in vector:
            parsed.append(sp.Rational(rational) + sp.Rational(sqrt_coefficient) * sp.sqrt(3))
        hex_vectors.append(sp.Matrix(parsed))
    hex_gram = sp.Matrix([[sp.factor(left.dot(right)) for right in hex_vectors] for left in hex_vectors])
    hex_equal_shell = all(hex_gram[index, index] == 1 for index in range(3))
    hex_pair_angles = sorted({str(hex_gram[i, j]) for i in range(3) for j in range(i + 1, 3)})

    amplitude_checks = {}
    amplitude = sp.Symbol("a_cos", real=True)
    for family in FAMILY_ORDER:
        n2 = moments[family]["N2"]
        positive_cosines = sp.Rational(n2, 2)
        signed_coefficient = amplitude / conversion
        amplitude_checks[family] = bool(
            sp.simplify(n2 * signed_coefficient**2 - positive_cosines * amplitude**2 / 2) == 0
        )

    grid_n = sp.Integer(inputs["math396_grid_N"])
    box_length = sp.Rational(inputs["math396_box_length"])
    q0 = sp.Rational(inputs["math396_q0"])
    shell_ratio = sp.factor(q0 * box_length / (2 * sp.pi))
    offgrid_form = bool(shell_ratio.has(sp.pi) and q0 != 0 and box_length != 0 and grid_n > 0)

    bcc_norm = int(inputs["bcc_norm_square"])
    fcc_norm = int(inputs["fcc_norm_square"])
    valuation_left_parity = v2(bcc_norm) % 2
    valuation_right_parity = v2(fcc_norm) % 2
    standard_torus_obstruction = bcc_norm == 2 and fcc_norm == 3 and valuation_left_parity != valuation_right_parity

    return {
        "moments": moments,
        "polynomial_coefficients": coefficients,
        "fixed_values": fixed_values,
        "fixed_derivatives": fixed_derivatives,
        "fixed_order": fixed_order,
        "radial_minimizers": radial_minimizers,
        "radial_minimum_energies": radial_minimum_energies,
        "root_brackets_millionths": root_brackets,
        "energy_brackets_millionths": energy_brackets,
        "radial_order": radial_order,
        "all_radial_energies_negative": all(bool(sp.simplify(raw_energies[name] < 0)) for name in FAMILY_ORDER),
        "all_radial_minima_above_cap_marker": all(cap_separation.values()),
        "amplitude_crosswalk": all(amplitude_checks.values()),
        "hex_equal_shell": hex_equal_shell,
        "hex_pair_angles": hex_pair_angles,
        "offgrid_transcendence_form": offgrid_form,
        "standard_cubic_torus_valuation_obstruction": standard_torus_obstruction,
        "math396_grid_N": int(grid_n),
        "shell_ratio_form": str(shell_ratio),
    }


def run(staged: bool) -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    certificate = CERTIFICATE.read_text(encoding="ascii")
    derived = derive_exact(manifest)
    oracle = manifest["test_oracles"]

    identity_ok = (
        manifest.get("schema") == "tect/pre-a-t055-legacy-sma-common-bohr-moment-radial-owner-route-split/1.0"
        and manifest.get("version") == "R-169 v1.4"
        and manifest.get("exploration_id") == "EXP-000862"
        and manifest.get("tier") == "T0"
        and manifest.get("claim_bearing") is False
        and manifest.get("new_negative_ids") == []
    )
    audit.check("manifest identity", identity_ok, manifest.get("version"), "exact R-169 v1.4 T0 identity", "identity")

    source_hashes = {
        name: normalized_sha256(REPO / authority["path"])
        for name, authority in manifest["source_authorities"].items()
    }
    expected_hashes = {name: authority["sha256"] for name, authority in manifest["source_authorities"].items()}
    audit.check("frozen source hashes", source_hashes == expected_hashes, source_hashes, expected_hashes, "provenance")

    content_hashes = {
        name: source_content_sha256(REPO / authority["path"])
        for name, authority in manifest["source_authorities"].items()
        if "source_content_sha256" in authority
    }
    expected_content_hashes = {
        name: authority["source_content_sha256"]
        for name, authority in manifest["source_authorities"].items()
        if "source_content_sha256" in authority
    }
    audit.check(
        "preserved source-content hashes",
        content_hashes == expected_content_hashes,
        content_hashes,
        expected_content_hashes,
        "provenance",
    )

    oracle_moments = {
        family: {"N2": values[0], "N4": values[1], "N6": values[2], "K4": values[3], "K6": values[4]}
        for family, values in oracle["moments"].items()
    }
    audit.check("exact zero-sum moments", derived["moments"] == oracle_moments, derived["moments"], oracle_moments, "moments")

    manifest_moments = manifest["exact_moments"]
    manifest_moments = {
        family: {key: value for key, value in values.items()}
        for family, values in manifest_moments.items()
        if family in FAMILY_ORDER
    }
    audit.check("manifest moment crosswalk", derived["moments"] == manifest_moments, derived["moments"], manifest_moments, "moments")

    audit.check(
        "corrected polynomial coefficients",
        derived["polynomial_coefficients"] == manifest["polynomials"],
        derived["polynomial_coefficients"],
        manifest["polynomials"],
        "polynomial",
    )

    oracle_values = dict(zip(FAMILY_ORDER, oracle["fixed_values"], strict=True))
    oracle_derivatives = dict(zip(FAMILY_ORDER, oracle["fixed_derivatives"], strict=True))
    fixed_ok = (
        derived["fixed_values"] == oracle_values
        and derived["fixed_derivatives"] == oracle_derivatives
        and derived["fixed_order"] == oracle["fixed_order"]
    )
    audit.check("fixed-intensity endpoint", fixed_ok, {k: derived[k] for k in ("fixed_values", "fixed_derivatives", "fixed_order")}, oracle, "endpoint")

    root_oracle = dict(zip(FAMILY_ORDER, oracle["root_brackets_millionths"], strict=True))
    energy_oracle = dict(zip(oracle["radial_order"], oracle["energy_brackets_millionths"], strict=True))
    radial_ok = (
        derived["root_brackets_millionths"] == root_oracle
        and derived["energy_brackets_millionths"] == energy_oracle
        and derived["radial_order"] == oracle["radial_order"]
        and derived["all_radial_energies_negative"]
    )
    audit.check("exact radial minima and ordering", radial_ok, {k: derived[k] for k in ("root_brackets_millionths", "energy_brackets_millionths", "radial_order")}, {"roots": root_oracle, "energies": energy_oracle, "order": oracle["radial_order"]}, "radial")

    published_roots = {
        family: surd_parts(published_expression(value))
        for family, value in manifest["radial_owner"]["positive_radial_minimizers"].items()
    }
    published_energies = {
        family: surd_parts(published_expression(value))
        for family, value in manifest["radial_owner"]["minimum_energies"].items()
    }
    derived_root_forms = {
        family: {key: value for key, value in data.items() if key in {"rational", "sqrt_coefficient", "sqrt_radicand"}}
        for family, data in derived["radial_minimizers"].items()
    }
    audit.check(
        "published exact radical formulas",
        derived_root_forms == published_roots and derived["radial_minimum_energies"] == published_energies,
        {"roots": derived_root_forms, "energies": derived["radial_minimum_energies"]},
        {"roots": published_roots, "energies": published_energies},
        "radial",
    )

    audit.check("larger-root Hessian signs", all(value["f_second_positive"] and value["smaller_f_second_negative"] for value in derived["radial_minimizers"].values()), derived["radial_minimizers"], "larger roots are minima; smaller roots are maxima", "radial")

    representation_ok = (
        derived["amplitude_crosswalk"]
        and derived["hex_equal_shell"]
        and derived["hex_pair_angles"] == ["-1/2"]
    )
    audit.check("amplitude and HEX representation firewalls", representation_ok, {k: derived[k] for k in ("amplitude_crosswalk", "hex_equal_shell", "hex_pair_angles")}, "factor two and exact equal-shell Gram", "convention")

    owner_ok = (
        derived["all_radial_minima_above_cap_marker"]
        and derived["offgrid_transcendence_form"]
        and derived["standard_cubic_torus_valuation_obstruction"]
    )
    audit.check("owner and applicability firewalls", owner_ok, {k: derived[k] for k in ("all_radial_minima_above_cap_marker", "offgrid_transcendence_form", "standard_cubic_torus_valuation_obstruction", "shell_ratio_form")}, "cross-owner marker only; exact off-grid form; standard torus obstruction", "scope")

    certificate_flat = " ".join(certificate.split())
    certificate_tokens = (
        "reconstructed and corrected equal-amplitude",
        "a_cos=2c",
        "relation coordinates as Euclidean momenta would be a type error",
        "0 < BCC < FCC < HEX < LAM",
        "LAM < HEX < FCC < BCC < 0",
        "registered rationalized/rounded cross-owner marker",
        "off-grid-confounded",
        "only nonapplicability is established",
        "B3 remains `REFUTED/RETIRED`",
        "Devil's-advocate audit",
        "External review is invited",
        "No v1.4 PDF is issued",
    )
    audit.check("certificate theorem and scope", all(token in certificate_flat for token in certificate_tokens), [token for token in certificate_tokens if token in certificate_flat], list(certificate_tokens), "scope")

    legacy = manifest["legacy_assessment"]
    legacy_ok = (
        legacy["record_id"] == "LEG-T055-COMMON-BOHR-FDECL-001"
        and legacy["pinned_source_ids_sha256"] == hashlib.sha256("\n".join(legacy["source_ids"]).encode("utf-8")).hexdigest()
        and legacy["gates"] == ["C6-BCC-PREMISE-BLOCKED"]
        and "A1-PRODUCTION-FUNCTIONAL-REALISATION" not in legacy["claims"]
    )
    audit.check("narrow legacy record contract", legacy_ok, legacy, "nine pinned sources and existing views only", "legacy")

    if staged:
        authority_text = "\n".join(
            (REPO / path).read_text(encoding="utf-8")
            for path in ("claims/GATES.md", "RESULTS-LEDGER.md", "explorations/log.jsonl", "changelog/log.jsonl")
        )
        absent_paths = [
            DEFAULT_OUTPUT,
            REPO / legacy["path"],
            REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-independent-{SLUG}/result.json",
            REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-integrated-{SLUG}/result.json",
        ]
        events = [json.loads(line) for line in (REPO / "changelog/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        matches = [(ordinal, event) for ordinal, event in enumerate(events, start=1) if event.get("id") == manifest["formal_integration"]["event_id"]]
        if matches:
            audit.check("integrated historical authority revalidation", len(matches) == 1, matches, "one immutable event-id match", "lifecycle")
        else:
            lifecycle_ok = (
                manifest["exploration_id"] not in authority_text
                and manifest["version"] not in authority_text
                and all(gate not in authority_text for gate in manifest["closed_gate_ids"])
                and not any(path.exists() for path in absent_paths)
            )
            audit.check("preformal authority absence", lifecycle_ok, {"tokens_absent": lifecycle_ok, "paths": [str(path) for path in absent_paths]}, "new authorities, assessment and runs absent", "lifecycle")

    return {
        "schema": "tect/pre-a-t055-legacy-sma-common-bohr-moment-radial-owner-route-split-primary/1.0",
        "version": __version__,
        "mode": "staged" if staged else "formal",
        "assertions": len(audit.rows),
        "checks": audit.rows,
        "derived": derived,
        "source_hash": normalized_sha256(SCRIPT),
        "manifest_hash": normalized_sha256(MANIFEST),
        "certificate_hash": normalized_sha256(CERTIFICATE),
        "verdict": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(args.staged)
    if not args.no_store:
        atomic_json(args.output, payload)
    print(f"PRIMARY PASS {payload['assertions']}/{payload['assertions']} mode={payload['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
