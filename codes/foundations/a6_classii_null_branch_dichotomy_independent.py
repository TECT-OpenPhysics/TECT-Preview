#!/usr/bin/env python3
"""Independent non-importing audit for the R-461 null-branch dichotomy.

This file intentionally implements the algebra and local complex arithmetic
again rather than importing the primary audit.  It shares only the frozen
manifest and the A1 parameter source.  It remains a finite T0 cross-check.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

F = Fraction
__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "a6-classii-null-branch-dichotomy-manifest.json"
DEFAULT_OUTPUT = (
    REPO / "claims" / "A6-CLASSII-UV-POWER-COUNTING" / "runs"
    / "2026-08-31-independent-a6-null-branch-dichotomy" / "independent.json"
)


def normalised_sha(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def save_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def pauli(axis: int) -> tuple[tuple[complex, complex], tuple[complex, complex]]:
    if axis == 1:
        return ((0j, 1 + 0j), (1 + 0j, 0j))
    if axis == 2:
        return ((0j, -1j), (1j, 0j))
    if axis == 3:
        return ((1 + 0j, 0j), (0j, -1 + 0j))
    raise ValueError(axis)


def matvec(matrix: tuple[tuple[complex, complex], tuple[complex, complex]], vector: tuple[complex, complex]) -> tuple[complex, complex]:
    return (
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1],
    )


def sesquilinear(left: tuple[complex, ...], right: tuple[complex, ...]) -> complex:
    return sum(x.conjugate() * y for x, y in zip(left, right))


def coefficients(a1: dict[str, Any]) -> dict[str, F]:
    p = a1["parameters"]
    den = F(str(p["M_X"])) ** 2 + F(str(p["classii_mass_regularizer"]))
    alpha, beta = F(str(p["alpha_X"])), F(str(p["beta_X"]))
    return {
        "a": F(str(p["cJJ"])) * alpha ** 2 / den,
        "b": F(str(p["cJK"])) * alpha * beta / den,
        "c": F(str(p["cKK"])) * beta ** 2 / den,
        "rho_floor": F(str(p["rho_regularizer"])),
    }


def complex_moments(field: tuple[complex, complex, complex], derivative: tuple[complex, complex, complex], eps: float) -> tuple[float, list[dict[str, float]]]:
    z = (field[0], field[1])
    dz = (derivative[0], derivative[1])
    rho = float(sesquilinear(field, field).real)
    drho = 2.0 * float(sesquilinear(field, derivative).real)
    rows: list[dict[str, float]] = []
    for axis in range(1, 4):
        sigma_z = matvec(pauli(axis), z)
        m = float(sesquilinear(z, sigma_z).real)
        dm = 2.0 * float(sesquilinear(sigma_z, dz).real)
        q = m / (rho + eps)
        rows.append({"m": m, "J": dm, "q": q, "K": dm - q * drho})
    return rho, rows


def energy(rows: list[dict[str, float]], cfs: dict[str, F]) -> float:
    aa, bb, cc = (float(cfs[name]) for name in ("a", "b", "c"))
    return sum(0.5 * (aa * row["J"] ** 2 + 2.0 * bb * row["J"] * row["K"] + cc * row["K"] ** 2) for row in rows)


def w_value(field: tuple[complex, complex, complex], cfs: dict[str, F]) -> float:
    aa, bb, cc = (float(cfs[name]) for name in ("a", "b", "c"))
    eps = float(cfs["rho_floor"])
    z = (field[0], field[1])
    rho = float(sesquilinear(field, field).real)
    total = 0.0
    for axis in range(1, 4):
        sz = matvec(pauli(axis), z)
        embedded = (sz[0], sz[1], 0j)
        m = float(sesquilinear(z, sz).real)
        q = m / (rho + eps)
        residual = tuple(embedded[i] - q * field[i] for i in range(3))
        total += aa * float(sesquilinear(embedded, embedded).real)
        total += 2.0 * bb * float(sesquilinear(embedded, residual).real)
        total += cc * float(sesquilinear(residual, residual).real)
    return 3.0 * total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1_ref = manifest["inputs"]["a1_production_functional_manifest"]
    a1_path = REPO / a1_ref["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    cfs = coefficients(a1)
    lo, hi = int(manifest["audit"]["grid_minimum"]), int(manifest["audit"]["grid_maximum"])
    tolerance = float(manifest["audit"]["float_tolerance"])
    threshold = float(manifest["audit"]["strict_positive_threshold"])
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": str(actual), "expected": str(expected)})
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")

    check("manifest audit id", manifest.get("audit_id") == "A6-CLASSII-NULL-BRANCH-DICHOTOMY-v1", manifest.get("audit_id"), "A6-CLASSII-NULL-BRANCH-DICHOTOMY-v1")
    check("nonclaim tier", manifest.get("claim_bearing") is False and manifest.get("tier") == "T0", manifest.get("tier"), "T0/nonbearing")
    check("A1 bytes", a1_path.is_file(), a1_path, True)
    check("A1 hash", normalised_sha(a1_path) == a1_ref["sha256"], normalised_sha(a1_path), a1_ref["sha256"])
    check("fixed eta", F(str(a1["parameters"]["eta_shell"])) == 0, a1["parameters"]["eta_shell"], 0)
    check("a1-derived a", cfs["a"] > 0, cfs["a"], ">0")
    check("a1-derived determinant", cfs["a"] * cfs["c"] - cfs["b"] ** 2 > 0, cfs, ">0")
    check("positive floor", cfs["rho_floor"] > 0, cfs["rho_floor"], ">0")

    identity_checks = 0
    zero_cases = 0
    for x1 in range(lo, hi + 1):
        for y1 in range(lo, hi + 1):
            for x2 in range(lo, hi + 1):
                for y2 in range(lo, hi + 1):
                    z = (complex(x1, y1), complex(x2, y2))
                    vals = []
                    for axis in range(1, 4):
                        vals.append(float(sesquilinear(z, matvec(pauli(axis), z)).real))
                    s = float(sesquilinear(z, z).real)
                    check(f"independent Bloch identity ({x1},{y1},{x2},{y2})", abs(sum(v * v for v in vals) - s * s) <= 0.0, sum(v * v for v in vals), s * s)
                    identity_checks += 1
                    if all(value == 0.0 for value in vals):
                        check(f"independent zero implication ({x1},{y1},{x2},{y2})", (x1, y1, x2, y2) == (0, 0, 0, 0), (x1, y1, x2, y2), (0, 0, 0, 0))
                        zero_cases += 1
    check("independent identity grid", identity_checks == (hi - lo + 1) ** 4, identity_checks, (hi - lo + 1) ** 4)
    check("independent zero cases", zero_cases == 1, zero_cases, 1)

    form_checks = 0
    form_zeros = 0
    aa, bb, cc = cfs["a"], cfs["b"], cfs["c"]
    for j in range(lo, hi + 1):
        for k in range(lo, hi + 1):
            jf, kf = F(j), F(k)
            form = aa * jf * jf + 2 * bb * jf * kf + cc * kf * kf
            cholesky = (aa * jf + bb * kf) ** 2 / aa + (aa * cc - bb ** 2) * kf * kf / aa
            check(f"independent form decomposition ({j},{k})", form == cholesky, form, cholesky)
            form_checks += 1
            if form == 0:
                check(f"independent form zero ({j},{k})", (j, k) == (0, 0), (j, k), (0, 0))
                form_zeros += 1
    check("independent form grid", form_checks == (hi - lo + 1) ** 2, form_checks, (hi - lo + 1) ** 2)
    check("independent form zero set", form_zeros == 1, form_zeros, 1)

    singlet_field = (0j, 0j, 0.35 + 0.62j)
    singlet_derivative = (0j, 0j, 0.17 - 0.09j)
    rho_s, singlet_rows = complex_moments(singlet_field, singlet_derivative, float(cfs["rho_floor"]))
    singlet_energy = energy(singlet_rows, cfs)
    check("independent singlet rho", rho_s > 0, rho_s, ">0")
    check("independent singlet J", all(abs(row["J"]) <= tolerance for row in singlet_rows), singlet_rows, "zero")
    check("independent singlet K", all(abs(row["K"]) <= tolerance for row in singlet_rows), singlet_rows, "zero")
    check("independent singlet energy", singlet_energy <= tolerance, singlet_energy, 0)

    active = (0.7 - 0.2j, -0.4 + 0.9j, 0.2 + 0.5j)
    # One common phase preserves the doublet projector; a relative phase would
    # be a rotating, non-null orientation and is kept for the hostile audit.
    phase_d = (1j * 0.2 * active[0], 1j * 0.2 * active[1], 1j * 0.65 * active[2])
    rho_p, phase_rows = complex_moments(active, phase_d, float(cfs["rho_floor"]))
    phase_energy = energy(phase_rows, cfs)
    check("independent phase drho", abs(2.0 * sesquilinear(active, phase_d).real) <= tolerance, 2.0 * sesquilinear(active, phase_d).real, 0)
    check("independent phase J", all(abs(row["J"]) <= tolerance for row in phase_rows), phase_rows, "zero")
    check("independent phase K", all(abs(row["K"]) <= tolerance for row in phase_rows), phase_rows, "zero")
    check("independent phase energy", phase_energy <= tolerance, phase_energy, 0)

    rotate = (1 + 0j, 0j, 0j)
    rotate_d = (0j, 1 + 0j, 0j)
    rho_r, rotate_rows = complex_moments(rotate, rotate_d, float(cfs["rho_floor"]))
    rotate_energy = energy(rotate_rows, cfs)
    check("independent rotate rho", abs(2.0 * sesquilinear(rotate, rotate_d).real) <= tolerance, rho_r, "constant")
    check("independent rotate nonnull", rotate_energy > threshold, rotate_energy, f">{threshold}")

    plane = (0.8 + 0.1j, -0.25 + 0.6j, 0.4 - 0.3j)
    plane_d = tuple(1j * 1.3 * value for value in plane)
    rho_pw, plane_rows = complex_moments(plane, plane_d, float(cfs["rho_floor"]))
    plane_energy = energy(plane_rows, cfs)
    plane_w = w_value(plane, cfs)
    check("independent plane energy null", plane_energy <= tolerance, plane_energy, 0)
    check("independent plane W positive", plane_w > threshold, plane_w, f">{threshold}")
    check("independent plane active", rho_pw > threshold, rho_pw, ">0")

    payload = {
        "schema": "tect/a6-classii-null-branch-dichotomy-independent-result/1.0",
        "run_kind": "independent",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "script_version": __version__,
        "verdict": "R-461-INDEPENDENT-PASS",
        "assertion_summary": {"passed": len(rows), "total": len(rows)},
        "assertions": rows,
        "derived": {
            "coefficients": {key: str(value) for key, value in cfs.items()},
            "identity_checks": identity_checks,
            "zero_implication_checks": zero_cases,
            "positive_form_checks": form_checks,
            "positive_form_zero_checks": form_zeros,
            "pure_singlet_energy": singlet_energy,
            "phase_branch_energy": phase_energy,
            "rotating_control_energy": rotate_energy,
            "plane_wave_energy": plane_energy,
            "plane_wave_W_epsilon": plane_w,
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if not args.no_store:
        save_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT R-461 PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
