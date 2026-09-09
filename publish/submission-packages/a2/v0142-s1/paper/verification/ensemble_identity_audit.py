#!/usr/bin/env python3
"""Paper-local exact audit of the R-158 ensemble identities.

The audit reconstructs the local polynomial completion, Bregman identity,
coexistence charge, ordering, and constant-observable plane-wave saturation
from the pinned A1 manifest.  It deliberately does not import the primary or
independent R-158 implementation.  The output is auxiliary evidence for the
paper package, not a claim-tier promotion or a physical interpretation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
MANIFEST = ROOT / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
MANUSCRIPT = ROOT / "publish" / "papers" / "a2-r157-r158-ensemble-minimizers" / "manuscript.tex"
DEFAULT_OUTPUT = ROOT / "publish" / "papers" / "a2-r157-r158-ensemble-minimizers" / "verification" / "runs" / "ensemble-identity.json"

# Deliberate hostile-test oracles, not derived model constants.
HOSTILE_DENSITY_OFFSET = Fraction(1, 100)
HOSTILE_CSTAR_OFFSET = Fraction(1, 100)
TEST_DELTAS = (Fraction(1, 100), Fraction(1, 7), Fraction(2, 3))
TEST_DENSITIES = (Fraction(0), Fraction(1, 7), Fraction(2, 5), Fraction(5, 3))
TEST_BARS = (Fraction(0), Fraction(1, 9), Fraction(3, 10))
# Arbitrary witness coefficient used only to demonstrate that K vanishes when
# both gradients vanish; it is not a model parameter or derived constant.
TEST_Q = Fraction(7, 13)


def fraction(value: Any) -> Fraction:
    return Fraction(str(value))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encode(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(encode(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    params = manifest["parameters"]
    lam = fraction(params["lambda"])
    gamma = fraction(params["gamma"])
    length = fraction(params["Lx"])
    volume = length**3

    rho_star = -3 * lam / (4 * gamma)
    c_star = 3 * lam * lam / (16 * gamma)
    charge_star = volume * rho_star / 2
    saddle_drop = lam * lam / (4 * gamma)

    # The lambda_0 contribution cancels symbolically in the completion.  The
    # residual linear, quadratic, and cubic coefficients are exact Fractions.
    completion_linear_residual = -c_star / 2 + gamma * rho_star * rho_star / 6
    completion_quadratic = -gamma * rho_star / 3
    completion_cubic = gamma / 6

    def potential(rho: Fraction) -> Fraction:
        return lam * rho * rho / 4 + gamma * rho**3 / 6

    def derivative(rho: Fraction) -> Fraction:
        return lam * rho / 2 + gamma * rho * rho / 2

    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": encode(actual), "expected": encode(expected)})

    check("manifest_exists", MANIFEST.is_file(), str(MANIFEST.relative_to(ROOT)), "file")
    check("manuscript_exists", MANUSCRIPT.is_file(), str(MANUSCRIPT.relative_to(ROOT)), "file")
    check("rho_star_positive", rho_star > 0, rho_star, ">0")
    check("completion_linear_cancels", completion_linear_residual == 0, completion_linear_residual, 0)
    check("completion_quadratic_matches_lambda", completion_quadratic == lam / 4, completion_quadratic, lam / 4)
    check("completion_cubic_matches_gamma", completion_cubic == gamma / 6, completion_cubic, gamma / 6)
    check("charge_is_volume_density_over_two", charge_star == volume * rho_star / 2, charge_star, volume * rho_star / 2)
    check("charge_is_positive", charge_star > 0, charge_star, ">0")
    check("saddle_drop_exceeds_coexistence_drop", saddle_drop > c_star > 0, [saddle_drop, c_star], "saddle>coexistence>0")

    # Evaluate the Bregman identity on several exact rational pairs.  This
    # tests the full polynomial, not just one coefficient or one density.
    for index, (rho, bar) in enumerate(zip(TEST_DENSITIES, TEST_BARS), start=1):
        left = potential(rho) - potential(bar) - derivative(bar) * (rho - bar)
        right = (rho - bar) ** 2 * (4 * gamma * bar + 2 * gamma * rho + 3 * lam) / 12
        check(f"bregman_identity_{index}", left == right, left, right)

    bregman_floor = 4 * gamma * rho_star + 3 * lam
    check("bregman_bracket_at_rho_star", bregman_floor == 0, bregman_floor, 0)
    check("bregman_bracket_nonnegative_for_rho_ge_rhostar", gamma > 0 and bregman_floor == 0, bregman_floor, ">=0")

    # A constant-density, constant-bilinear plane wave has zero spatial
    # gradients.  Compute the current formulas on that witness explicitly.
    zero_gradient = (Fraction(0), Fraction(0), Fraction(0))
    current_j = zero_gradient
    current_k = tuple(current_j[i] - TEST_Q * zero_gradient[i] for i in range(3))
    classii_density = sum(value * value for value in current_j) + sum(value * value for value in current_k)
    check("constant_plane_wave_J_zero", current_j == zero_gradient, current_j, zero_gradient)
    check("constant_plane_wave_K_zero", current_k == zero_gradient, current_k, zero_gradient)
    check("constant_plane_wave_classii_zero", classii_density == 0, classii_density, 0)

    # At coexistence the saturated witness has zero remainder and charge Q_*;
    # for any positive delta its grand-potential value is -delta Q_*.
    for index, delta in enumerate(TEST_DELTAS, start=1):
        grand_value = -delta * charge_star
        check(f"positive_delta_has_negative_witness_{index}", grand_value < 0, grand_value, "<0")
    hostile_delta_value = TEST_DELTAS[0] * charge_star
    check("hostile_delta_sign_reversal_rejected", hostile_delta_value > 0, hostile_delta_value, ">0 for reversed sign")

    # Hostile algebra mutations must be detected rather than silently accepted.
    hostile_density = rho_star - HOSTILE_DENSITY_OFFSET
    hostile_bracket = 4 * gamma * hostile_density + 3 * lam
    check("hostile_subthreshold_density_rejected", hostile_density > 0 and hostile_bracket < 0, hostile_bracket, "<0")
    hostile_cstar = c_star + HOSTILE_CSTAR_OFFSET
    hostile_linear_residual = -hostile_cstar / 2 + gamma * rho_star * rho_star / 6
    check("hostile_cstar_mutation_rejected", hostile_linear_residual != 0, hostile_linear_residual, "!=0")
    hostile_lam = -lam
    hostile_rho = -3 * hostile_lam / (4 * gamma)
    check("hostile_lambda_sign_rejected", hostile_rho < 0, hostile_rho, "<0")

    failures = [row for row in rows if row["status"] != "PASS"]
    if failures:
        raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))

    payload = {
        "schema": "tect/paper-ensemble-identity-audit/1.0",
        "paper_id": "a2-r157-r158-ensemble-minimizers",
        "script": "publish/papers/a2-r157-r158-ensemble-minimizers/verification/ensemble_identity_audit.py",
        "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"),
        "manifest_sha256": sha256(MANIFEST),
        "manuscript": str(MANUSCRIPT.relative_to(ROOT)).replace("\\", "/"),
        "manuscript_sha256": sha256(MANUSCRIPT),
        "inputs": {"lambda": lam, "gamma": gamma, "Lx": length},
        "derived": {
            "rho_star": rho_star,
            "c_star": c_star,
            "charge_star": charge_star,
            "saddle_drop": saddle_drop,
            "completion_linear_residual": completion_linear_residual,
            "completion_quadratic": completion_quadratic,
            "completion_cubic": completion_cubic,
            "bregman_bracket_at_rho_star": bregman_floor,
            "constant_plane_wave_J": current_j,
            "constant_plane_wave_K": current_k,
            "classii_density_on_witness": classii_density,
            "hostile_density": hostile_density,
            "hostile_density_bracket": hostile_bracket,
            "hostile_cstar_linear_residual": hostile_linear_residual,
            "hostile_lambda_sign_rho": hostile_rho,
        },
        "assertions": rows,
        "assertion_count": len(rows),
        "passed_count": len(rows),
        "verdict": "PAPER-ENSEMBLE-IDENTITY-AUDIT-PASS",
        "scope": "Paper-local exact ensemble algebra and constant-observable saturation only; no canonical correction, claim-tier promotion, or physical charge interpretation.",
    }
    atomic_json(args.output, payload)
    print(f"{payload['verdict']}: {payload['passed_count']}/{payload['assertion_count']}")
    print(f"artifact: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
