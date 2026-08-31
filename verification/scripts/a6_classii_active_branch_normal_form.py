#!/usr/bin/env python3
"""Primary exact audit for the additive R-462 active-branch normal form.

The script keeps the registered A6/A7 fixed-floor functional unchanged.  It
derives the positive coefficients from the hash-pinned A1 manifest and checks
the angular/radial jet decomposition with exact rational arithmetic.  It is a
local T0 input to a later tube/entropy argument, not a Gibbs or continuum
calculation.
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
__claims__ = [
    "A6-CLASSII-UV-POWER-COUNTING",
    "A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE",
]

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "a6-classii-active-branch-normal-form-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A6-CLASSII-UV-POWER-COUNTING"
    / "runs"
    / "2026-08-31-primary-a6-active-branch-normal-form"
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


def dot(left: tuple[F, F, F], right: tuple[F, F, F]) -> F:
    return sum((x * y for x, y in zip(left, right)), F(0))


def qform(a: F, b: F, c: F, x: F, y: F) -> F:
    return a * x * x + 2 * b * x * y + c * y * y


def frames() -> list[tuple[tuple[F, F, F], tuple[F, F, F], tuple[F, F, F]]]:
    return [
        ((F(1), F(0), F(0)), (F(0), F(1), F(0)), (F(0), F(0), F(1))),
        ((F(0), F(1), F(0)), (F(0), F(0), F(1)), (F(1), F(0), F(0))),
        ((F(0), F(0), F(1)), (F(1), F(0), F(0)), (F(0), F(1), F(0))),
        ((F(3, 5), F(4, 5), F(0)), (F(-4, 5), F(3, 5), F(0)), (F(0), F(0), F(1))),
        ((F(5, 13), F(12, 13), F(0)), (F(-12, 13), F(5, 13), F(0)), (F(0), F(0), F(1))),
        ((F(1, 3), F(2, 3), F(2, 3)), (F(2, 3), F(-1, 3), F(0)), (F(2, 9), F(4, 9), F(-5, 9))),
    ]


def local_normal_form(
    a: F,
    b: F,
    c: F,
    s: F,
    ds: F,
    delta: F,
    n: tuple[F, F, F],
    t: tuple[F, F, F],
) -> tuple[F, F, F, F, F, F]:
    j = tuple(ds * n_i + s * t_i for n_i, t_i in zip(n, t))
    k = tuple(delta * n_i + s * t_i for n_i, t_i in zip(n, t))
    j2 = dot(j, j)
    k2 = dot(k, k)
    jk = dot(j, k)
    raw = a * j2 + 2 * b * jk + c * k2
    radial = qform(a, b, c, ds, delta)
    angular = (a + 2 * b + c) * s * s * dot(t, t)
    return raw, radial, angular, j2, jk, k2


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
    a, b, c = (coefficients[key] for key in ("a", "b", "c"))
    eps = coefficients["rho_floor"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A6-CLASSII-ACTIVE-BRANCH-NORMAL-FORM-v1", manifest["audit_id"], "A6-CLASSII-ACTIVE-BRANCH-NORMAL-FORM-v1")
    check("result identity", manifest["result_id"] == "R-462", manifest["result_id"], "R-462")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("tier is T0", manifest["tier"] == "T0", manifest["tier"], "T0")
    check("functional unchanged", manifest["methods_preserved"]["a6_a7_functional_unchanged"] is True, manifest["methods_preserved"], True)
    check("owner order unchanged", manifest["methods_preserved"]["owner_order_unchanged"] is True, manifest["methods_preserved"], True)
    check("A1 authority exists", a1_path.is_file(), a1_path, True)
    check("A1 authority hash", sha256(a1_path) == a1_item["sha256"], sha256(a1_path), a1_item["sha256"])
    p = a1["parameters"]
    check("eta shell fixed", F(str(p["eta_shell"])) == 0, p["eta_shell"], 0)
    determinant = a * c - b * b
    check("coefficient a positive", a > 0, a, ">0")
    check("coefficient determinant positive", determinant > 0, determinant, ">0")
    angular_coefficient = a + 2 * b + c
    check("angular coefficient positive", angular_coefficient > 0, angular_coefficient, ">0")
    check(
        "angular coefficient identity",
        a * angular_coefficient == (a + b) ** 2 + determinant,
        a * angular_coefficient,
        (a + b) ** 2 + determinant,
    )

    s_values = [F(value) for value in manifest["audit"]["positive_s_values"]]
    remainder_values = [F(value) for value in manifest["audit"]["singlet_densities"]]
    jet_values = [F(value) for value in manifest["audit"]["jet_values"]]
    tangent_values = [F(-2), F(0), F(2)]
    frame_list = frames()
    frame_checks = 0
    decomposition_checks = 0
    denominator_checks = 0
    null_checks = 0
    angular_positive_checks = 0
    radial_positive_checks = 0
    samples: dict[str, str] = {}

    for frame_index, (n, basis_one, basis_two) in enumerate(frame_list):
        if dot(n, n) != 1:
            raise AssertionError(("frame norm", frame_index, dot(n, n)))
        frame_checks += 1
        for s in s_values:
            for remainder in remainder_values:
                rho = s + remainder
                denominator_checks += 1
                if rho + eps <= 0:
                    raise AssertionError(("active denominator", frame_index, s, remainder, rho + eps))
                for ds in jet_values:
                    for drho in jet_values:
                        delta = ds - s * drho / (rho + eps)
                        for u in tangent_values:
                            for v in tangent_values:
                                t = tuple(u * one + v * two for one, two in zip(basis_one, basis_two))
                                decomposition_checks += 1
                                if dot(n, t) != 0:
                                    raise AssertionError(("frame tangent", frame_index, decomposition_checks, dot(n, t)))
                                raw, radial, angular, j2, jk, k2 = local_normal_form(a, b, c, s, ds, delta, n, t)
                                if raw != radial + angular:
                                    raise AssertionError(("normal form", frame_index, decomposition_checks, raw, radial + angular))
                                if not samples:
                                    samples = {"raw": str(raw), "radial": str(radial), "angular": str(angular), "j2": str(j2), "jk": str(jk), "k2": str(k2)}

                t_zero = (F(0), F(0), F(0))
                raw_null, radial_null, angular_null, *_ = local_normal_form(a, b, c, s, F(0), F(0), n, t_zero)
                null_checks += 1
                if not (raw_null == 0 and radial_null == 0 and angular_null == 0):
                    raise AssertionError(("active null jet", frame_index, null_checks, raw_null, radial_null, angular_null))
                raw_ang, _, _, *_ = local_normal_form(a, b, c, s, F(0), F(0), n, basis_one)
                angular_positive_checks += 1
                if raw_ang <= 0:
                    raise AssertionError(("angular nonnull jet", frame_index, angular_positive_checks, raw_ang))
                raw_rad, _, _, *_ = local_normal_form(a, b, c, s, F(1), F(0), n, t_zero)
                radial_positive_checks += 1
                if raw_rad <= 0:
                    raise AssertionError(("radial nonnull jet", frame_index, radial_positive_checks, raw_rad))

    radial_grid_checks = 0
    radial_zero_checks = 0
    for x in jet_values:
        for y in jet_values:
            radial_grid_checks += 1
            value = qform(a, b, c, x, y)
            if value == 0:
                radial_zero_checks += 1
                check(f"radial zero {x} {y}", (x, y) == (0, 0), (x, y), (0, 0))
            else:
                check(f"radial positive {x} {y}", value > 0, value, ">0")

    check("frame count", frame_checks == len(frame_list), frame_checks, len(frame_list))
    check("decomposition count", decomposition_checks == len(frame_list) * len(s_values) * len(remainder_values) * len(jet_values) ** 2 * len(tangent_values) ** 2, decomposition_checks, len(frame_list) * len(s_values) * len(remainder_values) * len(jet_values) ** 2 * len(tangent_values) ** 2)
    check("denominator count", denominator_checks == len(frame_list) * len(s_values) * len(remainder_values), denominator_checks, len(frame_list) * len(s_values) * len(remainder_values))
    check("null-jet count", null_checks == len(frame_list) * len(s_values) * len(remainder_values), null_checks, len(frame_list) * len(s_values) * len(remainder_values))
    check("angular-positive count", angular_positive_checks == len(frame_list) * len(s_values) * len(remainder_values), angular_positive_checks, len(frame_list) * len(s_values) * len(remainder_values))
    check("radial-positive count", radial_positive_checks == len(frame_list) * len(s_values) * len(remainder_values), radial_positive_checks, len(frame_list) * len(s_values) * len(remainder_values))
    check("radial zero count", radial_zero_checks == 1, radial_zero_checks, 1)
    check("radial grid count", radial_grid_checks == len(jet_values) ** 2, radial_grid_checks, len(jet_values) ** 2)

    derived = {
        "coefficients": {key: str(value) for key, value in coefficients.items()},
        "coefficient_determinant": str(determinant),
        "angular_coefficient": str(angular_coefficient),
        "frame_checks": frame_checks,
        "decomposition_checks": decomposition_checks,
        "denominator_checks": denominator_checks,
        "null_checks": null_checks,
        "angular_positive_checks": angular_positive_checks,
        "radial_positive_checks": radial_positive_checks,
        "radial_grid_checks": radial_grid_checks,
        "radial_zero_checks": radial_zero_checks,
        "sample": samples,
        "scope": manifest["scope_firewall"],
    }
    payload = {
        "schema": "tect/a6-classii-active-branch-normal-form-primary-result/1.0",
        "run_kind": "primary",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_ids": __claims__,
        "script_version": __version__,
        "verdict": "R-462-PRIMARY-PASS",
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
    print(f"PRIMARY R-462 PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
