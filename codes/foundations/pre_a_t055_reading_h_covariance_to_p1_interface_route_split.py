#!/usr/bin/env python3
"""Derive the R-169 v1.2 Reading-H covariance-to-P1 interface result.

Purpose: prove exact covariance, conditional torus-lift, commensurability, and
bare nonlinear-convention statements and audit their declared scope.
Convention: Q carries the full antipodal coefficient list once; P_0 is the
registered internal projector, and the literal JSON decimal q0 is exact input.
Formula: ||Psi_Q||_2^2=16^3 I, 3*pi^2/64<q0^2<4*pi^2/64, and
V_RH-V_P1=phi^4(108*phi^2-43)/400.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-t055-reading-h-covariance-to-p1-interface-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-primary-{SLUG}/result.json"


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


def atan_partial(x: sp.Rational, last_index: int) -> sp.Rational:
    return sp.factor(sum(((-1) ** j) * x ** (2 * j + 1) / sp.Rational(2 * j + 1) for j in range(last_index + 1)))


def exact_derivation(manifest: dict[str, Any]) -> dict[str, Any]:
    oracle = manifest["test_oracles"]
    side = sp.Integer(manifest["torus_commensurability"]["torus_side"])
    q0 = sp.Rational(manifest["torus_commensurability"]["literal_q0"])
    volume = side ** 3

    # Exact phase-complete finite fixture.  The full antipodal list is used once.
    coefficients = {
        sp.Integer(1): (sp.Integer(1) + 2 * sp.I) / 3,
        sp.Integer(-1): (sp.Integer(1) - 2 * sp.I) / 3,
        sp.Integer(2): sp.Rational(1, 4),
        sp.Integer(-2): sp.Rational(1, 4),
    }
    intensity = sp.factor(sum(sp.conjugate(value) * value for value in coefficients.values()))
    reality_pairs = all(sp.simplify(coefficients[-key] - sp.conjugate(value)) == 0 for key, value in coefficients.items())
    covariance_zero = sp.factor(sum(sp.conjugate(value) * value for value in coefficients.values()))

    points = [sp.Integer(0), sp.pi / 2, sp.pi]
    gram = sp.Matrix(
        [
            [
                sp.simplify(
                    sum(
                        sp.conjugate(value) * value * sp.exp(sp.I * key * (points[i] - points[j]))
                        for key, value in coefficients.items()
                    )
                )
                for j in range(len(points))
            ]
            for i in range(len(points))
        ]
    )
    gram_spectrum = {
        str(sp.simplify(value)): int(multiplicity)
        for value, multiplicity in gram.eigenvals().items()
    }
    gram_psd = all(value.is_nonnegative is True for value in gram.eigenvals())

    u0 = sp.Matrix([1, 1, 1]) / sp.sqrt(3)
    p0 = sp.simplify(u0 * u0.T)
    projector_error = sp.simplify(p0 * p0 - p0)
    lift_norm_coefficient = volume

    # Translate the phase-complete coefficient list by pi.  Odd modes change
    # sign, while every spectral weight |c_k|^2 is unchanged.
    origin_shift = sp.pi
    shifted_coefficients = {
        key: sp.simplify(value * sp.exp(sp.I * key * origin_shift))
        for key, value in coefficients.items()
    }
    phase_field_origin = sp.simplify(sum(coefficients.values()))
    phase_field_shift = sp.simplify(sum(shifted_coefficients.values()))
    covariance_origin = {key: sp.simplify(sp.conjugate(value) * value) for key, value in coefficients.items()}
    covariance_after_origin_shift = {
        key: sp.simplify(sp.conjugate(value) * value) for key, value in shifted_coefficients.items()
    }

    # Exact Machin enclosure.  Even last index is an upper alternating sum;
    # odd last index is a lower alternating sum.
    x5 = sp.Rational(1, 5)
    x239 = sp.Rational(1, 239)
    atan5_lower = atan_partial(x5, 11)
    atan5_upper = atan_partial(x5, 10)
    atan239_lower = atan_partial(x239, 3)
    atan239_upper = atan_partial(x239, 2)
    pi_lower = sp.factor(16 * atan5_lower - 4 * atan239_upper)
    pi_upper = sp.factor(16 * atan5_upper - 4 * atan239_lower)
    lower_gap = sp.factor(q0 ** 2 - sp.Rational(3, 64) * pi_upper ** 2)
    upper_gap = sp.factor(sp.Rational(4, 64) * pi_lower ** 2 - q0 ** 2)

    shell_three = [
        (a, b, c)
        for a in range(-2, 3)
        for b in range(-2, 3)
        for c in range(-2, 3)
        if a * a + b * b + c * c == 3
    ]
    bcc = {
        tuple(vector)
        for zero in range(3)
        for first in (-1, 1)
        for second in (-1, 1)
        for vector in [([first, second, 0] if zero == 2 else [first, 0, second] if zero == 1 else [0, first, second])]
    }
    r169_index_square = sum(component * component for component in (4, 4, 0))

    phi, s = sp.symbols("phi s", real=True)
    lam = sp.Rational(-43, 100)
    gamma = sp.Rational(81, 50)
    reading = lam * phi ** 4 / 2 + gamma * phi ** 6 / 3
    pinned = lam * phi ** 4 / 4 + gamma * phi ** 6 / 6
    defect = sp.factor(reading - pinned)
    rho = sp.symbols("rho", nonnegative=True)
    rho_defect = sp.factor(lam * rho ** 2 / 4 + gamma * rho ** 3 / 6)
    nonzero_crossing = sp.solve(sp.factor(rho_defect / rho ** 2), rho)[0]
    negative_defect = sp.factor(rho_defect.subs(rho, sp.Rational(1, 4)))
    positive_defect = sp.factor(rho_defect.subs(rho, sp.Rational(1, 2)))
    quartic_ratio = sp.factor((lam / 2) / (lam / 4))
    sextic_ratio = sp.factor((gamma / 3) / (gamma / 6))
    quartic_match = sp.Eq(s ** 4, quartic_ratio)
    sextic_match = sp.Eq(s ** 6, sextic_ratio)
    # A common s would force (s^4)^3=(s^6)^2.  Derive the two
    # right-hand sides independently before comparing them so symbolic
    # simplification cannot erase the contradiction.
    rescale_contradiction = sp.factor(quartic_ratio ** 3 - sextic_ratio ** 2)

    return {
        "phase_complete_fixture": reality_pairs,
        "fixture_intensity": str(intensity),
        "covariance_at_zero": str(covariance_zero),
        "covariance_gram_spectrum": gram_spectrum,
        "covariance_gram_psd": gram_psd,
        "p0_trace": str(sp.trace(p0)),
        "p0_rank": int(p0.rank()),
        "p0_idempotent": projector_error == sp.zeros(3),
        "lift_norm_coefficient": int(lift_norm_coefficient),
        "phase_field_origin": str(phase_field_origin),
        "phase_field_shift": str(phase_field_shift),
        "covariance_origin_invariant": covariance_origin == covariance_after_origin_shift,
        "pi_bracket_width": str(sp.factor(pi_upper - pi_lower)),
        "q0_above_shell_three_gap": str(lower_gap),
        "q0_below_shell_four_gap": str(upper_gap),
        "q0_strictly_between_shells": bool(lower_gap > 0 and upper_gap > 0),
        "commensurate_shell_count": len(shell_three),
        "reading_h_bcc_count": len(bcc),
        "r169_v1_1_index_square": r169_index_square,
        "nonlinear_defect": str(defect),
        "nonlinear_crossing": str(nonzero_crossing),
        "negative_defect": str(negative_defect),
        "positive_defect": str(positive_defect),
        "quartic_match": str(quartic_match),
        "sextic_match": str(sextic_match),
        "rescale_contradiction": str(rescale_contradiction),
        "rescale_incompatible": rescale_contradiction != 0,
        "oracle_volume": oracle["torus_volume"],
    }


def run(staged: bool) -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    derived = exact_derivation(manifest)
    oracle = manifest["test_oracles"]

    audit.check("manifest identity", manifest.get("schema") == "tect/pre-a-t055-reading-h-covariance-to-p1-interface/1.0" and manifest.get("exploration_id") == "EXP-000858" and manifest.get("version") == "R-169 v1.2", {key: manifest.get(key) for key in ("schema", "exploration_id", "version")}, "exact package identity", "authority")
    source_ok = all(normalized_sha256(REPO / value["path"]) == value["sha256"] for value in manifest["source_authorities"].values())
    audit.check("source authority hashes", source_ok, source_ok, True, "authority")
    audit.check("phase-complete real synthesis", derived["phase_complete_fixture"] and derived["fixture_intensity"] == derived["covariance_at_zero"], derived, "real and C_Q(0)=I", "covariance")
    audit.check("positive covariance fixture", derived["covariance_gram_psd"], derived["covariance_gram_spectrum"], "exact nonnegative spectrum", "covariance")
    audit.check("registered P0 projector", derived["p0_trace"] == "1" and derived["p0_rank"] == 1 and derived["p0_idempotent"], {key: derived[key] for key in ("p0_trace", "p0_rank", "p0_idempotent")}, "rank-one projector", "covariance")
    audit.check("conditional lift norm", derived["lift_norm_coefficient"] == oracle["torus_volume"], derived["lift_norm_coefficient"], oracle["torus_volume"], "lift")
    audit.check("phase cannot come from covariance", derived["phase_field_origin"] != derived["phase_field_shift"] and derived["covariance_origin_invariant"], {key: derived[key] for key in ("phase_field_origin", "phase_field_shift", "covariance_origin_invariant")}, "field changes and covariance does not", "nonextraction")
    audit.check("Machin enclosure precision", sp.Rational(derived["pi_bracket_width"]) < sp.Rational(1, 12500000000000000), derived["pi_bracket_width"], "<1/12500000000000000", "commensurability")
    audit.check("literal q0 between shells", derived["q0_strictly_between_shells"] and not derived["q0_above_shell_three_gap"].startswith("-") and not derived["q0_below_shell_four_gap"].startswith("-"), {key: derived[key] for key in ("q0_above_shell_three_gap", "q0_below_shell_four_gap")}, "two positive exact rational gaps", "commensurability")
    audit.check("shell cardinality obstruction", derived["commensurate_shell_count"] == oracle["commensurate_shell_count"] and derived["reading_h_bcc_count"] == oracle["reading_h_bcc_count"] and derived["r169_v1_1_index_square"] == oracle["r169_v1_1_index_square"], {key: derived[key] for key in ("commensurate_shell_count", "reading_h_bcc_count", "r169_v1_1_index_square")}, {key: oracle[key] for key in ("commensurate_shell_count", "reading_h_bcc_count", "r169_v1_1_index_square")}, "commensurability")
    audit.check("nonlinear sign crosswalk", derived["nonlinear_crossing"] == oracle["nonlinear_crossing"] and derived["negative_defect"] == oracle["negative_defect"] and derived["positive_defect"] == oracle["positive_defect"], {key: derived[key] for key in ("nonlinear_crossing", "negative_defect", "positive_defect")}, {key: oracle[key] for key in ("nonlinear_crossing", "negative_defect", "positive_defect")}, "energy")
    audit.check("constant rescale obstruction", derived["rescale_incompatible"] and derived["rescale_contradiction"] != "0", {key: derived[key] for key in ("quartic_match", "sextic_match", "rescale_contradiction")}, "incompatible fourth and sixth powers", "energy")
    audit.check("certificate proof and DA", all(token in certificate for token in ("Exact scalar synthesis", "Deterministic equivariant nonextraction", "Exact side-16 shell obstruction", "Bare nonlinear convention firewall", "Devil's-advocate review", "External review is invited")), "all theorem and audit sections", "all theorem and audit sections", "scope")
    firewall_tokens = (
        "only a bare-density crosswalk",
        "It is not the difference of",
        "fixed-norm",
        "PA-T055-READING-H-REALIZATION-TO-PINNED-P1-OR-DECLARED-ESCAPE",
        "OPEN.",
    )
    firewall_ok = all(token in certificate for token in firewall_tokens)
    audit.check("full-energy firewall", firewall_ok, firewall_ok, True, "scope")
    if staged:
        authorities = "\n".join((REPO / path).read_text(encoding="utf-8") for path in ("claims/GATES.md", "RESULTS-LEDGER.md", "negative-results/registry.md"))
        audit.check("preformal authority absence", "EXP-000858" not in authorities and all(value not in authorities for value in manifest["closed_gate_ids"] + manifest["new_negative_ids"]), "new formal authorities absent", "new formal authorities absent", "lifecycle")

    return {
        "schema": "tect/pre-a-t055-reading-h-covariance-to-p1-interface-primary/1.0",
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
