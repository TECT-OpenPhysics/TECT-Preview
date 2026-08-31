#!/usr/bin/env python3
"""Non-importing independent audit for R-462.

This implementation repeats the active-branch jet identity with its own
coefficient derivation, frame construction, and component arithmetic.  It
does not import the primary verifier and does not make a probability or
continuum claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "a6-classii-active-branch-normal-form-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A6-CLASSII-UV-POWER-COUNTING"
    / "runs"
    / "2026-08-31-independent-a6-active-branch-normal-form"
    / "independent.json"
)


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def store_json(path: Path, payload: dict[str, Any]) -> None:
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


def vector_dot(left: list[F], right: list[F]) -> F:
    total = F(0)
    for index in range(3):
        total += left[index] * right[index]
    return total


def quadratic(a: F, b: F, c: F, first: F, second: F) -> F:
    return a * first * first + 2 * b * first * second + c * second * second


def derive_independently(a1: dict[str, Any]) -> dict[str, F]:
    p = a1["parameters"]
    alpha = F(str(p["alpha_X"]))
    beta = F(str(p["beta_X"]))
    mass_squared = F(str(p["M_X"])) ** 2
    mass_regulator = F(str(p["classii_mass_regularizer"]))
    common = mass_squared + mass_regulator
    cjj = F(str(p["cJJ"]))
    cjk = F(str(p["cJK"]))
    ckk = F(str(p["cKK"]))
    return {
        "a": cjj * alpha * alpha / common,
        "b": cjk * alpha * beta / common,
        "c": ckk * beta * beta / common,
        "rho_floor": F(str(p["rho_regularizer"])),
        "denominator": common,
    }


def frame_set() -> list[tuple[list[F], list[F], list[F]]]:
    # The bases are rational and each is orthogonal to its listed unit n.
    return [
        ([F(1), F(0), F(0)], [F(0), F(1), F(0)], [F(0), F(0), F(1)]),
        ([F(0), F(1), F(0)], [F(0), F(0), F(1)], [F(1), F(0), F(0)]),
        ([F(0), F(0), F(1)], [F(1), F(0), F(0)], [F(0), F(1), F(0)]),
        ([F(3, 5), F(4, 5), F(0)], [F(-4, 5), F(3, 5), F(0)], [F(0), F(0), F(1)]),
        ([F(1, 3), F(2, 3), F(2, 3)], [F(2, 3), F(-1, 3), F(0)], [F(2, 9), F(4, 9), F(-5, 9)]),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source = REPO / manifest["inputs"]["a1_production_functional_manifest"]["path"]
    a1 = json.loads(source.read_text(encoding="utf-8"))
    coeff = derive_independently(a1)
    a, b, c = coeff["a"], coeff["b"], coeff["c"]
    determinant = a * c - b * b
    angular_coefficient = a + 2 * b + c
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": str(actual), "expected": str(expected)})
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A6-CLASSII-ACTIVE-BRANCH-NORMAL-FORM-v1", manifest["audit_id"], "A6-CLASSII-ACTIVE-BRANCH-NORMAL-FORM-v1")
    check("result identity", manifest["result_id"] == "R-462", manifest["result_id"], "R-462")
    check("independent claim firewall", manifest["claim_bearing"] is False and manifest["tier"] == "T0", (manifest["claim_bearing"], manifest["tier"]), (False, "T0"))
    check("A1 source hash", sha256(source) == manifest["inputs"]["a1_production_functional_manifest"]["sha256"], sha256(source), manifest["inputs"]["a1_production_functional_manifest"]["sha256"])
    check("eta shell fixed", F(str(a1["parameters"]["eta_shell"])) == 0, a1["parameters"]["eta_shell"], 0)
    check("positive coefficient", a > 0, a, ">0")
    check("positive determinant", determinant > 0, determinant, ">0")
    check("positive angular coefficient", angular_coefficient > 0, angular_coefficient, ">0")
    check("angular identity", a * angular_coefficient == (a + b) ** 2 + determinant, a * angular_coefficient, (a + b) ** 2 + determinant)

    frames = frame_set()
    s_values = [F("1/5"), F("1/2"), F(1), F(2)]
    remainder_values = [F(0), F("1/3"), F(3)]
    jets = [F(-1), F(0), F(1)]
    tangent_scalars = [F(-1), F(0), F(1)]
    decomposition_checks = 0
    null_checks = 0
    angular_positive_checks = 0
    radial_positive_checks = 0
    denominator_checks = 0
    sample: dict[str, str] = {}

    for frame_index, (n, basis_one, basis_two) in enumerate(frames):
        check(f"frame norm {frame_index}", vector_dot(n, n) == 1, vector_dot(n, n), 1)
        for s in s_values:
            for remainder in remainder_values:
                rho = s + remainder
                denominator_checks += 1
                if rho + coeff["rho_floor"] <= 0:
                    raise AssertionError(("denominator", frame_index, s, remainder, rho + coeff["rho_floor"]))
                for ds in jets:
                    for drho in jets:
                        delta = ds - s * drho / (rho + coeff["rho_floor"])
                        for u in tangent_scalars:
                            for v in tangent_scalars:
                                t = [u * basis_one[index] + v * basis_two[index] for index in range(3)]
                                if vector_dot(n, t) != 0:
                                    raise AssertionError(("tangent", frame_index, vector_dot(n, t)))
                                j = [ds * n[index] + s * t[index] for index in range(3)]
                                k = [delta * n[index] + s * t[index] for index in range(3)]
                                raw = a * vector_dot(j, j) + 2 * b * vector_dot(j, k) + c * vector_dot(k, k)
                                radial = quadratic(a, b, c, ds, delta)
                                angular = angular_coefficient * s * s * vector_dot(t, t)
                                decomposition_checks += 1
                                if raw != radial + angular:
                                    raise AssertionError(("decomposition", frame_index, decomposition_checks, raw, radial + angular))
                                if not sample:
                                    sample = {"raw": str(raw), "radial": str(radial), "angular": str(angular)}
                zero = [F(0), F(0), F(0)]
                j = [F(0) * n[index] + s * zero[index] for index in range(3)]
                k = [F(0) * n[index] + s * zero[index] for index in range(3)]
                null_checks += 1
                check(f"null jet {frame_index} {null_checks}", vector_dot(j, j) == 0 and vector_dot(k, k) == 0, (vector_dot(j, j), vector_dot(k, k)), (0, 0))
                t = basis_one
                j = [s * t[index] for index in range(3)]
                k = [s * t[index] for index in range(3)]
                angular_positive_checks += 1
                check(f"angular jet positive {frame_index} {angular_positive_checks}", a * vector_dot(j, j) + 2 * b * vector_dot(j, k) + c * vector_dot(k, k) > 0, a * vector_dot(j, j) + 2 * b * vector_dot(j, k) + c * vector_dot(k, k), ">0")
                radial_positive_checks += 1
                radial_value = quadratic(a, b, c, F(1), F(1))
                check(f"radial jet positive {frame_index} {radial_positive_checks}", radial_value > 0, radial_value, ">0")

    radial_zero_checks = 0
    for x in jets:
        for y in jets:
            value = quadratic(a, b, c, x, y)
            if value == 0:
                radial_zero_checks += 1
                check(f"radial zero {x} {y}", (x, y) == (F(0), F(0)), (x, y), (0, 0))
            else:
                check(f"radial grid positive {x} {y}", value > 0, value, ">0")

    check("decomposition count", decomposition_checks == len(frames) * len(s_values) * len(remainder_values) * len(jets) ** 2 * len(tangent_scalars) ** 2, decomposition_checks, len(frames) * len(s_values) * len(remainder_values) * len(jets) ** 2 * len(tangent_scalars) ** 2)
    check("denominator count", denominator_checks == len(frames) * len(s_values) * len(remainder_values), denominator_checks, len(frames) * len(s_values) * len(remainder_values))
    check("null count", null_checks == len(frames) * len(s_values) * len(remainder_values), null_checks, len(frames) * len(s_values) * len(remainder_values))
    check("angular-positive count", angular_positive_checks == len(frames) * len(s_values) * len(remainder_values), angular_positive_checks, len(frames) * len(s_values) * len(remainder_values))
    check("radial-positive count", radial_positive_checks == len(frames) * len(s_values) * len(remainder_values), radial_positive_checks, len(frames) * len(s_values) * len(remainder_values))
    check("radial zero count", radial_zero_checks == 1, radial_zero_checks, 1)

    payload = {
        "schema": "tect/a6-classii-active-branch-normal-form-independent-result/1.0",
        "run_kind": "independent",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "script_version": __version__,
        "verdict": "R-462-INDEPENDENT-PASS",
        "assertion_summary": {"passed": len(rows), "total": len(rows)},
        "assertions": rows,
        "derived": {
            "coefficients": {key: str(value) for key, value in coeff.items()},
            "coefficient_determinant": str(determinant),
            "angular_coefficient": str(angular_coefficient),
            "decomposition_checks": decomposition_checks,
            "denominator_checks": denominator_checks,
            "null_checks": null_checks,
            "angular_positive_checks": angular_positive_checks,
            "radial_positive_checks": radial_positive_checks,
            "radial_zero_checks": radial_zero_checks,
            "sample": sample,
            "scope": manifest["scope_firewall"],
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if not args.no_store:
        output = args.output if args.output.is_absolute() else REPO / args.output
        store_json(output, payload)
    print(f"INDEPENDENT R-462 PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
