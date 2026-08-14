#!/usr/bin/env python3
"""Independently verify the R-169 v1.2 covariance-to-P1 route split.

Purpose: recompute the coefficient, projector, shell, Machin-bound, and bare
nonlinear fixtures without importing the primary lane or a CAS.
Convention: antipodal coefficients are counted once as a full list, the
literal decimal q0 is an exact rational, and candidate-minus-P1 is used.
Formula: ||Psi_Q||_2^2=16^3 I and
V_RH-V_P1=rho^2(108*rho-43)/400.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-t055-reading-h-covariance-to-p1-interface-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-independent-{SLUG}/result.json"


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


def gaussian_norm_square(value: tuple[Fraction, Fraction]) -> Fraction:
    real, imaginary = value
    return real * real + imaginary * imaginary


def atan_partial(x: Fraction, last_index: int) -> Fraction:
    return sum(
        (Fraction(-1) if index % 2 else Fraction(1)) * x ** (2 * index + 1) / (2 * index + 1)
        for index in range(last_index + 1)
    )


def exact_derivation(manifest: dict[str, Any]) -> dict[str, Any]:
    side = int(manifest["torus_commensurability"]["torus_side"])
    q0 = Fraction(manifest["torus_commensurability"]["literal_q0"])

    coefficients = {
        1: (Fraction(1, 3), Fraction(2, 3)),
        -1: (Fraction(1, 3), Fraction(-2, 3)),
        2: (Fraction(1, 4), Fraction(0)),
        -2: (Fraction(1, 4), Fraction(0)),
    }
    conjugate_pairs = all(
        coefficients[-mode] == (value[0], -value[1]) for mode, value in coefficients.items()
    )
    intensity = sum(gaussian_norm_square(value) for value in coefficients.values())
    shifted_coefficients = {
        mode: ((-value[0], -value[1]) if mode % 2 else value)
        for mode, value in coefficients.items()
    }
    phase_field_origin = (
        sum(value[0] for value in coefficients.values()),
        sum(value[1] for value in coefficients.values()),
    )
    phase_field_shift = (
        sum(value[0] for value in shifted_coefficients.values()),
        sum(value[1] for value in shifted_coefficients.values()),
    )
    covariance_origin = {mode: gaussian_norm_square(value) for mode, value in coefficients.items()}
    covariance_after_origin_shift = {
        mode: gaussian_norm_square(value) for mode, value in shifted_coefficients.items()
    }

    projector = [[Fraction(1, 3) for _ in range(3)] for _ in range(3)]
    projector_square = [
        [sum(projector[row][inner] * projector[inner][column] for inner in range(3)) for column in range(3)]
        for row in range(3)
    ]
    projector_trace = sum(projector[index][index] for index in range(3))
    projector_rank_one = all(row == projector[0] for row in projector) and any(projector[0])

    x5 = Fraction(1, 5)
    x239 = Fraction(1, 239)
    pi_lower = 16 * atan_partial(x5, 11) - 4 * atan_partial(x239, 2)
    pi_upper = 16 * atan_partial(x5, 10) - 4 * atan_partial(x239, 3)
    lower_gap = q0 * q0 - Fraction(3, 64) * pi_upper * pi_upper
    upper_gap = Fraction(4, 64) * pi_lower * pi_lower - q0 * q0

    shell_three = [
        (first, second, third)
        for first in range(-2, 3)
        for second in range(-2, 3)
        for third in range(-2, 3)
        if first * first + second * second + third * third == 3
    ]
    bcc = {
        tuple(vector)
        for zero_index in range(3)
        for first in (-1, 1)
        for second in (-1, 1)
        for vector in [
            [first, second, 0]
            if zero_index == 2
            else [first, 0, second]
            if zero_index == 1
            else [0, first, second]
        ]
    }

    lam = Fraction(-43, 100)
    gamma = Fraction(81, 50)
    phi4_coefficient = lam / 4
    phi6_coefficient = gamma / 6
    crossing = -phi4_coefficient / phi6_coefficient

    def defect_at(rho: Fraction) -> Fraction:
        return phi4_coefficient * rho * rho + phi6_coefficient * rho * rho * rho

    quartic_ratio = (lam / 2) / (lam / 4)
    sextic_ratio = (gamma / 3) / (gamma / 6)
    rescale_contradiction = quartic_ratio**3 - sextic_ratio**2

    return {
        "phase_complete_fixture": conjugate_pairs,
        "fixture_intensity": str(intensity),
        "covariance_at_zero": str(intensity),
        "covariance_positive_by_feature_sum": all(gaussian_norm_square(value) >= 0 for value in coefficients.values()),
        "p0_trace": str(projector_trace),
        "p0_rank": 1 if projector_rank_one else 0,
        "p0_idempotent": projector_square == projector,
        "lift_norm_coefficient": side**3,
        "phase_field_origin": str(phase_field_origin[0]) if phase_field_origin[1] == 0 else str(phase_field_origin),
        "phase_field_shift": str(phase_field_shift[0]) if phase_field_shift[1] == 0 else str(phase_field_shift),
        "phase_field_changes_under_origin_shift": phase_field_origin != phase_field_shift,
        "covariance_origin_invariant": covariance_origin == covariance_after_origin_shift,
        "pi_bracket_width": str(pi_upper - pi_lower),
        "q0_above_shell_three_gap": str(lower_gap),
        "q0_below_shell_four_gap": str(upper_gap),
        "q0_strictly_between_shells": lower_gap > 0 and upper_gap > 0,
        "commensurate_shell_count": len(shell_three),
        "reading_h_bcc_count": len(bcc),
        "r169_v1_1_index_square": sum(component * component for component in (4, 4, 0)),
        "nonlinear_phi4_coefficient": str(phi4_coefficient),
        "nonlinear_phi6_coefficient": str(phi6_coefficient),
        "nonlinear_crossing": str(crossing),
        "negative_defect": str(defect_at(Fraction(1, 4))),
        "positive_defect": str(defect_at(Fraction(1, 2))),
        "quartic_ratio": str(quartic_ratio),
        "sextic_ratio": str(sextic_ratio),
        "rescale_contradiction": str(rescale_contradiction),
        "rescale_incompatible": rescale_contradiction != 0,
    }


def run(staged: bool) -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    derived = exact_derivation(manifest)
    oracle = manifest["test_oracles"]

    for name, authority in manifest["source_authorities"].items():
        path = REPO / authority["path"]
        actual = normalized_sha256(path) if path.is_file() else "missing"
        audit.check(f"source hash {name}", actual == authority["sha256"], actual, authority["sha256"], "provenance")

    audit.check("phase-complete covariance", derived["phase_complete_fixture"] and derived["fixture_intensity"] == derived["covariance_at_zero"] and derived["covariance_positive_by_feature_sum"], {key: derived[key] for key in ("fixture_intensity", "covariance_at_zero")}, "real synthesis and positive covariance", "covariance")
    audit.check("registered P0 projector", derived["p0_trace"] == "1" and derived["p0_rank"] == 1 and derived["p0_idempotent"], {key: derived[key] for key in ("p0_trace", "p0_rank", "p0_idempotent")}, "rank-one projector", "covariance")
    audit.check("conditional lift norm", derived["lift_norm_coefficient"] == oracle["torus_volume"], derived["lift_norm_coefficient"], oracle["torus_volume"], "lift")
    audit.check("covariance phase loss", derived["phase_field_changes_under_origin_shift"] and derived["covariance_origin_invariant"], {key: derived[key] for key in ("phase_field_changes_under_origin_shift", "covariance_origin_invariant")}, "field changes; covariance fixed", "nonextraction")
    audit.check("Machin enclosure precision", Fraction(derived["pi_bracket_width"]) < Fraction(1, 12500000000000000), derived["pi_bracket_width"], "<1/12500000000000000", "commensurability")
    audit.check("literal q0 exact bracket", derived["q0_strictly_between_shells"], {key: derived[key] for key in ("q0_above_shell_three_gap", "q0_below_shell_four_gap")}, "two positive rational gaps", "commensurability")
    audit.check("shell cardinalities", derived["commensurate_shell_count"] == oracle["commensurate_shell_count"] and derived["reading_h_bcc_count"] == oracle["reading_h_bcc_count"] and derived["r169_v1_1_index_square"] == oracle["r169_v1_1_index_square"], {key: derived[key] for key in ("commensurate_shell_count", "reading_h_bcc_count", "r169_v1_1_index_square")}, "8, 12, 32", "commensurability")
    audit.check("nonlinear sign crosswalk", derived["nonlinear_crossing"] == oracle["nonlinear_crossing"] and derived["negative_defect"] == oracle["negative_defect"] and derived["positive_defect"] == oracle["positive_defect"], {key: derived[key] for key in ("nonlinear_crossing", "negative_defect", "positive_defect")}, "43/108, -1/400, 11/1600", "energy")
    audit.check("constant rescale obstruction", derived["quartic_ratio"] == "2" and derived["sextic_ratio"] == "2" and derived["rescale_incompatible"], {key: derived[key] for key in ("quartic_ratio", "sextic_ratio", "rescale_contradiction")}, "2^3 differs from 2^2", "energy")
    covariance_statement = manifest["reading_h_type_split"]["composite_embedding"]
    nonextraction_statement = manifest["equivariant_nonextraction"]["statement"]
    audit.check("semantic type firewall", "not deterministic P1 fields" in covariance_statement and "translation-equivariant" in nonextraction_statement and "translation-fixed output" in nonextraction_statement, {"composite": covariance_statement, "section": nonextraction_statement}, "covariance is not a selected mean", "scope")
    audit.check("certificate full-energy scope", all(token in certificate for token in ("only a bare-density crosswalk", "It is not the difference of", "fixed-norm", "No R-169 v1.2 PDF is issued")), "scope tokens present", "scope tokens present", "scope")

    if staged:
        authorities = "\n".join(
            (REPO / path).read_text(encoding="utf-8")
            for path in ("claims/GATES.md", "RESULTS-LEDGER.md", "negative-results/registry.md")
        )
        absent = "EXP-000858" not in authorities and all(
            identifier not in authorities for identifier in manifest["closed_gate_ids"] + manifest["new_negative_ids"]
        )
        audit.check("preformal authority absence", absent, absent, True, "lifecycle")

    return {
        "schema": "tect/pre-a-t055-reading-h-covariance-to-p1-interface-independent/1.0",
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
    print(f"INDEPENDENT PASS {payload['assertions']}/{payload['assertions']} mode={payload['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
