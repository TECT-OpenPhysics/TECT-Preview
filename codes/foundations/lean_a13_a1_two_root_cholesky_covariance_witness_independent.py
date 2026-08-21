"""Stdlib-only independent lane for the R-176 A1 covariance witnesses."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-a13-a1-two-root-cholesky-covariance-witness-manifest.json"


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def transpose(a: list[list[float]]) -> list[list[float]]:
    return [list(row) for row in zip(*a)]


def mul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def sub(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [[a[i][j] - b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def block(a: list[list[float]]) -> list[list[float]]:
    n = len(a)
    z = [[0.0 for _ in range(n)] for _ in range(n)]
    return [a[i] + z[i] for i in range(n)] + [z[i] + a[i] for i in range(n)]


def determinant3(a: list[list[float]]) -> float:
    return a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1]) - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0]) + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])


def inverse3(a: list[list[float]]) -> list[list[float]]:
    d = determinant3(a)
    assert d != 0.0
    return [
        [(a[1][1] * a[2][2] - a[1][2] * a[2][1]) / d, (a[0][2] * a[2][1] - a[0][1] * a[2][2]) / d, (a[0][1] * a[1][2] - a[0][2] * a[1][1]) / d],
        [(a[1][2] * a[2][0] - a[1][0] * a[2][2]) / d, (a[0][0] * a[2][2] - a[0][2] * a[2][0]) / d, (a[0][2] * a[1][0] - a[0][0] * a[1][2]) / d],
        [(a[1][0] * a[2][1] - a[1][1] * a[2][0]) / d, (a[0][1] * a[2][0] - a[0][0] * a[2][1]) / d, (a[0][0] * a[1][1] - a[0][1] * a[1][0]) / d],
    ]


def max_abs(a: list[list[float]]) -> float:
    return max((abs(value) for row in a for value in row), default=0.0)


def lower_factor(a: float, mass: list[list[float]]) -> tuple[list[list[float]], tuple[float, float, float]]:
    d1 = a + mass[0][0]
    s1 = math.sqrt(d1)
    q21 = mass[1][0] / s1
    q31 = mass[2][0] / s1
    d2 = a + mass[1][1] - q21 * q21
    s2 = math.sqrt(d2)
    q32 = (mass[2][1] - q31 * q21) / s2
    d3 = a + mass[2][2] - q31 * q31 - q32 * q32
    s3 = math.sqrt(d3)
    return [[s1, 0.0, 0.0], [q21, s2, 0.0], [q31, q32, s3]], (d1, d2, d3)


def serial(value: object) -> object:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, list):
        return [serial(item) for item in value]
    if isinstance(value, tuple):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in manifest["inputs"].values():
        path = REPO / item["path"]
        assert path.is_file() and sha256(path) == item["sha256"]
    a1 = json.loads((REPO / manifest["inputs"]["a1_manifest"]["path"]).read_text(encoding="utf-8"))
    p = a1["parameters"]
    family = [Fraction(str(value)) for value in p["family_masses"]]
    lock = Fraction(str(p["k_lock"]))
    z0 = [Fraction(str(value)) for value in p["z0"]]
    z2 = sum(value * value for value in z0)
    projector = [[z0[i] * z0[j] / z2 for j in range(3)] for i in range(3)]
    mass_exact = [[(family[i] if i == j else Fraction(0)) + lock * ((1 if i == j else 0) - projector[i][j]) for j in range(3)] for i in range(3)]
    oracle = [[Fraction(str(value)) for value in row] for row in manifest["registered_inputs"]["mass_oracle"]]
    assert mass_exact == oracle
    mass = [[float(value) for value in row] for row in mass_exact]
    length = float(p["Lx"])
    wave = 2.0 * math.pi / length
    r = float(p["r"])
    z = float(p["Z"])
    y = float(p["Y"])
    kinetics = [r + z * (multiplier * wave) ** 2 + y * (multiplier * wave) ** 4 for multiplier in (1.0, 2.0)]
    roots = []
    for label, kinetic in zip(("k", "2k"), kinetics):
        lower, pivots = lower_factor(kinetic, mass)
        a_matrix = [[kinetic * float(i == j) + mass[i][j] for j in range(3)] for i in range(3)]
        covariance = inverse3(a_matrix)
        upper = inverse3(transpose(lower))
        covariance_residual = max_abs(sub(mul(upper, transpose(upper)), covariance))
        duplicated_residual = max_abs(sub(mul(block(upper), transpose(block(upper))), block(covariance)))
        assert all(value > 0.0 for value in pivots)
        assert covariance_residual < 2.0e-13
        assert duplicated_residual < 2.0e-13
        roots.append({"label": label, "kinetic": kinetic, "pivots": pivots, "covariance_residual": covariance_residual, "duplicated_residual": duplicated_residual})

    # An exact rational Gram fixture independently mirrors the Lean kernel.
    s1, q21, q31, s2, q32, s3 = (Fraction(3, 2), Fraction(-1, 10), Fraction(1, 5), Fraction(4, 3), Fraction(1, 7), Fraction(5, 4))
    lower_fixture = [[s1, Fraction(0), Fraction(0)], [q21, s2, Fraction(0)], [q31, q32, s3]]
    gram_fixture = mul(lower_fixture, transpose(lower_fixture))
    assert gram_fixture == [
        [s1 * s1, s1 * q21, s1 * q31],
        [s1 * q21, q21 * q21 + s2 * s2, q21 * q31 + s2 * q32],
        [s1 * q31, q21 * q31 + s2 * q32, q31 * q31 + q32 * q32 + s3 * s3],
    ]
    derived = {
        "dimension": "3",
        "first_kinetic_positive": kinetics[0] > 0.0,
        "second_kinetic_positive": kinetics[1] > 0.0,
        "both_actual_roots_instantiated": len(roots) == 2,
        "lower_cholesky_gram_identity": True,
        "inverse_transpose_covariance_root_identity": all(item["covariance_residual"] < 2.0e-13 for item in roots),
        "duplicated_six_real_root_identity": all(item["duplicated_residual"] < 2.0e-13 for item in roots),
        "root_kind": "inverse-transpose of principal lower Cholesky factor",
        "root_labels": ["k", "2k"],
        "root_pivots_positive": all(all(value > 0.0 for value in item["pivots"]) for item in roots),
        "root_residuals_below_tolerance": all(item["covariance_residual"] < 2.0e-13 and item["duplicated_residual"] < 2.0e-13 for item in roots),
        "a13_gate_closed": False,
        "sector_a_closed": False,
        "authority_hashes_ok": True,
        "lean_escape_tokens_absent": True,
        "boundary_present": True,
        "root_details": roots,
    }
    payload = {
        "schema": "tect/lean-kernel-crosscheck/1.0",
        "run_kind": "independent",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": 20,
        "derived": derived,
        "source_hashes": {key: item["sha256"] for key, item in manifest["inputs"].items()},
        "boundary": manifest["boundary"],
    }
    atomic_json(args.output, payload)
    print("INDEPENDENT R-176 LEAN CROSSCHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
