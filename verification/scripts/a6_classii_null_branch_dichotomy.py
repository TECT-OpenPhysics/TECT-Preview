#!/usr/bin/env python3
"""Primary executable audit for the additive R-461 A6 null-branch lemma.

The audit keeps the existing A6/A7 Class-II functional fixed.  It derives the
coefficient matrix from the hash-pinned A1 production manifest, checks the
algebraic Bloch and positive-form identities on an exact rational grid, and
then exercises smooth local branch fixtures.  The resulting JSON is T0,
claim-nonbearing evidence; it is not a Gibbs, continuum, or physical-sector
calculation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
__claims__ = [
    "A6-CLASSII-UV-POWER-COUNTING",
    "A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE",
]

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "a6-classii-null-branch-dichotomy-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A6-CLASSII-UV-POWER-COUNTING"
    / "runs"
    / "2026-08-31-primary-a6-null-branch-dichotomy"
    / "primary.json"
)


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def exact_complex_grid(lo: int, hi: int) -> list[tuple[int, int, int, int]]:
    return [(x1, y1, x2, y2) for x1 in range(lo, hi + 1) for y1 in range(lo, hi + 1)
            for x2 in range(lo, hi + 1) for y2 in range(lo, hi + 1)]


def exact_s(z: tuple[int, int, int, int]) -> F:
    x1, y1, x2, y2 = z
    return F(x1 * x1 + y1 * y1 + x2 * x2 + y2 * y2)


def exact_m(z: tuple[int, int, int, int]) -> tuple[F, F, F]:
    x1, y1, x2, y2 = z
    return (
        F(2 * (x1 * x2 + y1 * y2)),
        F(2 * (x1 * y2 - y1 * x2)),
        F(x1 * x1 + y1 * y1 - x2 * x2 - y2 * y2),
    )


def derive_coefficients(a1: dict[str, Any]) -> dict[str, F]:
    p = a1["parameters"]
    alpha = F(str(p["alpha_X"]))
    beta = F(str(p["beta_X"]))
    mass = F(str(p["M_X"]))
    mass_reg = F(str(p["classii_mass_regularizer"]))
    denominator = mass * mass + mass_reg
    return {
        "a": F(str(p["cJJ"])) * alpha * alpha / denominator,
        "b": F(str(p["cJK"])) * alpha * beta / denominator,
        "c": F(str(p["cKK"])) * beta * beta / denominator,
        "rho_floor": F(str(p["rho_regularizer"])),
        "denominator": denominator,
    }


def pauli_apply(z: tuple[complex, complex], axis: int) -> tuple[complex, complex]:
    z1, z2 = z
    if axis == 1:
        return z2, z1
    if axis == 2:
        return -1j * z2, 1j * z1
    if axis == 3:
        return z1, -z2
    raise ValueError(axis)


def dot_conj(left: tuple[complex, ...], right: tuple[complex, ...]) -> complex:
    return sum(left_i.conjugate() * right_i for left_i, right_i in zip(left, right))


def local_currents(
    field: tuple[complex, complex, complex],
    derivative: tuple[complex, complex, complex],
    rho_floor: float,
) -> dict[str, Any]:
    z = (field[0], field[1])
    dz = (derivative[0], derivative[1])
    rho = sum(abs(value) ** 2 for value in field)
    drho = 2.0 * float(dot_conj(field, derivative).real)
    rows: list[dict[str, float]] = []
    for axis in (1, 2, 3):
        sigma_z = pauli_apply(z, axis)
        m = float(dot_conj(z, sigma_z).real)
        dm = 2.0 * float(dot_conj(sigma_z, dz).real)
        q = m / (rho + rho_floor)
        k = dm - q * drho
        rows.append({"m": m, "J": dm, "q": q, "K": k})
    return {"rho": rho, "drho": drho, "rows": rows}


def classii_energy(currents: dict[str, Any], coefficients: dict[str, F]) -> float:
    a, b, c = (float(coefficients[key]) for key in ("a", "b", "c"))
    return sum(0.5 * (a * row["J"] ** 2 + 2.0 * b * row["J"] * row["K"] + c * row["K"] ** 2)
               for row in currents["rows"])


def w_epsilon(field: tuple[complex, complex, complex], coefficients: dict[str, F]) -> float:
    """Compute the already-registered leading local contraction W_epsilon."""
    a, b, c = (float(coefficients[key]) for key in ("a", "b", "c"))
    eps = float(coefficients["rho_floor"])
    z = (field[0], field[1])
    rho = sum(abs(value) ** 2 for value in field)
    s = sum(abs(value) ** 2 for value in z)
    total = 0.0
    for axis in (1, 2, 3):
        sigma_field = (*pauli_apply(z, axis), 0j)
        m = float(dot_conj(z, pauli_apply(z, axis)).real)
        q = m / (rho + eps)
        v = tuple(sigma_field[index] - q * field[index] for index in range(3))
        tnorm = float(dot_conj(sigma_field, sigma_field).real)
        cross = float(dot_conj(sigma_field, v).real)
        vnorm = float(dot_conj(v, v).real)
        total += a * tnorm + 2.0 * b * cross + c * vnorm
    # Keep these computed values visible so a future edit cannot silently
    # replace the registered functional by a scalar-orientation shortcut.
    formula = 9.0 * (a + 2.0 * b + c) * s
    formula -= 6.0 * b * s * s / (rho + eps)
    formula -= 3.0 * c * s * s * (rho + 2.0 * eps) / ((rho + eps) ** 2)
    if not math.isclose(3.0 * total, formula, rel_tol=2e-12, abs_tol=2e-12):
        raise AssertionError((3.0 * total, formula))
    return formula


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1_item = manifest["inputs"]["a1_production_functional_manifest"]
    a1_path = REPO / a1_item["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    coefficients = derive_coefficients(a1)
    audit = manifest["audit"]
    tolerance = float(audit["float_tolerance"])
    strict_threshold = float(audit["strict_positive_threshold"])
    lo, hi = int(audit["grid_minimum"]), int(audit["grid_maximum"])
    grid = exact_complex_grid(lo, hi)
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A6-CLASSII-NULL-BRANCH-DICHOTOMY-v1", manifest["audit_id"], "A6-CLASSII-NULL-BRANCH-DICHOTOMY-v1")
    check("result identity", manifest["result_id"] == "R-461", manifest["result_id"], "R-461")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("tier is T0", manifest["tier"] == "T0", manifest["tier"], "T0")
    check("functional unchanged", manifest["methods_preserved"]["a6_a7_functional_unchanged"] is True, manifest["methods_preserved"], True)
    check("owner order unchanged", manifest["methods_preserved"]["owner_order_unchanged"] is True, manifest["methods_preserved"], True)
    check("no PDF", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"], True)
    check("A1 authority exists", a1_path.is_file(), a1_path, True)
    check("A1 authority hash", sha256(a1_path) == a1_item["sha256"], sha256(a1_path), a1_item["sha256"])
    p = a1["parameters"]
    check("eta shell fixed", F(str(p["eta_shell"])) == 0, p["eta_shell"], 0)
    check("rho floor positive", coefficients["rho_floor"] > 0, coefficients["rho_floor"], ">0")
    check("coefficient a positive", coefficients["a"] > 0, coefficients["a"], ">0")
    check("coefficient determinant positive", coefficients["a"] * coefficients["c"] - coefficients["b"] ** 2 > 0, coefficients, ">0")

    identity_count = 0
    zero_implication_count = 0
    for point in grid:
        s_value = exact_s(point)
        m1, m2, m3 = exact_m(point)
        check(f"Bloch identity {point}", m1 * m1 + m2 * m2 + m3 * m3 == s_value * s_value,
              (m1 * m1 + m2 * m2 + m3 * m3), s_value * s_value)
        identity_count += 1
        if (m1, m2, m3) == (0, 0, 0):
            check(f"Bloch-zero implication {point}", point == (0, 0, 0, 0), point, (0, 0, 0, 0))
            zero_implication_count += 1
    check("exhaustive Bloch grid count", identity_count == len(grid), identity_count, len(grid))
    check("zero-Bloch cases are exhausted", zero_implication_count >= 1, zero_implication_count, ">=1")

    a, b, c = coefficients["a"], coefficients["b"], coefficients["c"]
    form_count = 0
    form_zero_count = 0
    for j in range(lo, hi + 1):
        for k in range(lo, hi + 1):
            jf, kf = F(j), F(k)
            lhs = a * jf * jf + 2 * b * jf * kf + c * kf * kf
            rhs = (a * jf + b * kf) ** 2 / a + (a * c - b * b) * kf * kf / a
            check(f"positive-form decomposition ({j},{k})", lhs == rhs, lhs, rhs)
            form_count += 1
            if lhs == 0:
                check(f"positive-form zero ({j},{k})", (j, k) == (0, 0), (j, k), (0, 0))
                form_zero_count += 1
    check("exhaustive positive-form grid count", form_count == (hi - lo + 1) ** 2, form_count, (hi - lo + 1) ** 2)
    check("positive-form zero set", form_zero_count == 1, form_zero_count, 1)

    for point in grid:
        rho = exact_s(point)
        eps = coefficients["rho_floor"]
        check(f"floor denominator ({point})", rho + eps > 0, rho + eps, ">0")
    check("floor denominator grid count", len(grid) == (hi - lo + 1) ** 4, len(grid), (hi - lo + 1) ** 4)

    field_singlet = (0j, 0j, 0.7 - 0.2j)
    derivative_singlet = (0.0 + 0.0j, 0.0 + 0.0j, 0.31 - 0.11j)
    singlet = local_currents(field_singlet, derivative_singlet, float(coefficients["rho_floor"]))
    check("pure-singlet has zero J", all(abs(row["J"]) <= tolerance for row in singlet["rows"]), singlet, "all J=0")
    check("pure-singlet has zero K", all(abs(row["K"]) <= tolerance for row in singlet["rows"]), singlet, "all K=0")
    check("pure-singlet energy zero", classii_energy(singlet, coefficients) <= tolerance, classii_energy(singlet, coefficients), 0)

    field_active = (1.0 + 0.25j, -0.35 + 0.8j, 0.6 - 0.2j)
    # The doublet must carry one common local phase; separate component phases
    # rotate the Bloch projector and are intentionally not a null branch.
    phase_derivative = (1j * 0.4 * field_active[0], 1j * 0.4 * field_active[1], 1j * 0.7 * field_active[2])
    phase = local_currents(field_active, phase_derivative, float(coefficients["rho_floor"]))
    check("phase branch rho constant", abs(phase["drho"]) <= tolerance, phase["drho"], 0)
    check("phase branch Bloch moments constant", all(abs(row["J"]) <= tolerance for row in phase["rows"]), phase, "all J=0")
    check("phase branch K zero", all(abs(row["K"]) <= tolerance for row in phase["rows"]), phase, "all K=0")
    check("phase branch energy zero", classii_energy(phase, coefficients) <= tolerance, classii_energy(phase, coefficients), 0)

    rotating_field = (1.0 + 0j, 0j, 0j)
    rotating_derivative = (0j, 1.0 + 0j, 0j)
    rotating = local_currents(rotating_field, rotating_derivative, float(coefficients["rho_floor"]))
    rotating_energy = classii_energy(rotating, coefficients)
    check("rotating doublet has constant rho", abs(rotating["drho"]) <= tolerance, rotating["drho"], 0)
    check("rotating doublet is not null", rotating_energy > strict_threshold, rotating_energy, f">{strict_threshold}")
    check("rotating doublet detects nonconstant Bloch", any(abs(row["J"]) > strict_threshold for row in rotating["rows"]), rotating, "some J nonzero")

    plane_wave_field = (0.8 + 0.1j, -0.25 + 0.6j, 0.4 - 0.3j)
    plane_wave_derivative = tuple(1j * 1.7 * value for value in plane_wave_field)
    plane_wave = local_currents(plane_wave_field, plane_wave_derivative, float(coefficients["rho_floor"]))
    plane_wave_w = w_epsilon(plane_wave_field, coefficients)
    check("plane-wave pathwise energy zero", classii_energy(plane_wave, coefficients) <= tolerance, classii_energy(plane_wave, coefficients), 0)
    check("plane-wave W epsilon positive", plane_wave_w > strict_threshold, plane_wave_w, f">{strict_threshold}")
    check("plane-wave is active", sum(abs(value) ** 2 for value in plane_wave_field[:2]) > strict_threshold, plane_wave_field, "active doublet")

    # A generic quotient-derivative fixture makes the q*grad(rho) term visible;
    # this is a definition check, not a claim that this fixture is null.
    quotient_field = (0.9 + 0.2j, -0.3 + 0.4j, 0.5 - 0.1j)
    quotient_derivative = (0.17 - 0.08j, -0.05 + 0.12j, 0.21 + 0.03j)
    quotient = local_currents(quotient_field, quotient_derivative, float(coefficients["rho_floor"]))
    check("quotient derivative floor is finite", all(math.isfinite(row["K"]) for row in quotient["rows"]), quotient, "finite")
    check("quotient derivative uses q grad rho", any(abs(row["J"] - row["K"]) > strict_threshold for row in quotient["rows"]), quotient, "some J differs from K")

    derived = {
        "coefficients": {key: str(value) for key, value in coefficients.items()},
        "coefficient_determinant": str(coefficients["a"] * coefficients["c"] - coefficients["b"] ** 2),
        "grid": {"minimum": lo, "maximum": hi, "points": len(grid)},
        "identity_checks": identity_count,
        "zero_implication_checks": zero_implication_count,
        "positive_form_checks": form_count,
        "positive_form_zero_checks": form_zero_count,
        "pure_singlet": {"energy": classii_energy(singlet, coefficients), "currents": singlet},
        "phase_branch": {"energy": classii_energy(phase, coefficients), "currents": phase},
        "rotating_control": {"energy": rotating_energy, "currents": rotating},
        "plane_wave_control": {"energy": classii_energy(plane_wave, coefficients), "W_epsilon": plane_wave_w, "currents": plane_wave},
        "quotient_fixture": quotient,
        "scope": manifest["scope_firewall"],
    }
    payload = {
        "schema": "tect/a6-classii-null-branch-dichotomy-primary-result/1.0",
        "run_kind": "primary",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_ids": __claims__,
        "script_version": __version__,
        "verdict": "R-461-PRIMARY-PASS",
        "assertion_summary": {"passed": len(rows), "total": len(rows)},
        "assertions": rows,
        "derived": derived,
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if not args.no_store:
        output = args.output if args.output.is_absolute() else REPO / args.output
        atomic_json(output, payload)
    print(f"PRIMARY R-461 PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
