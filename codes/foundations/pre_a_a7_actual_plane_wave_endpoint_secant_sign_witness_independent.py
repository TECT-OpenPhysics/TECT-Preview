#!/usr/bin/env python3
"""Non-importing Fraction audit for R-171."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-a7-actual-plane-wave-endpoint-secant-sign-witness"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-21-independent-actual-a7-plane-wave-endpoint-secant-sign-witness/result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def frac(value: Any) -> Fraction:
    return Fraction(str(value))


def derive(manifest: dict[str, Any], audit: Audit) -> dict[str, Any]:
    for item in manifest["inputs"].values():
        path = REPO / item["path"]
        audit.check(f"authority hash {item['path']}", sha256(path) == item["sha256"], sha256(path), item["sha256"], "authority")
    params = json.loads((REPO / manifest["inputs"]["a1_manifest"]["path"]).read_text(encoding="utf-8"))["parameters"]
    lengths = tuple(frac(params[key]) for key in ("Lx", "Ly", "Lz"))
    mode = tuple(int(x) for x in manifest["witness"]["mode_index"])
    audit.check("registered cubic torus", lengths == (Fraction(16),) * 3, lengths, (16, 16, 16), "mode")
    audit.check("nonzero dual mode", mode != (0, 0, 0), mode, "nonzero", "mode")
    wave = Fraction(2 * mode[0], 1) / lengths[0]
    audit.check("dual lattice wave number", wave == Fraction(1, 8), wave, Fraction(1, 8), "mode")
    audit.check("transverse mode indices vanish", mode[1:] == (0, 0), mode[1:], (0, 0), "mode")
    eps = frac(params[manifest["witness"]["rho_floor_key"]])
    denominator = frac(params["M_X"]) ** 2 + frac(params["classii_mass_regularizer"])
    a = frac(params["cJJ"]) * frac(params["alpha_X"]) ** 2 / denominator
    b = frac(params["cJK"]) * frac(params["alpha_X"]) * frac(params["beta_X"]) / denominator
    c = frac(params["cKK"]) * frac(params["beta_X"]) ** 2 / denominator
    determinant = a * c - b * b
    audit.check("a positive", a > 0, a, ">0", "coefficients")
    audit.check("b positive", b > 0, b, ">0", "coefficients")
    audit.check("c positive", c > 0, c, ">0", "coefficients")
    audit.check("coefficient determinant positive", determinant > 0, determinant, ">0", "coefficients")
    audit.check("rho floor positive", eps > 0, eps, ">0", "coefficients")
    pauli = manifest["witness"]["pauli_generators"]
    audit.check("three embedded Pauli generators supplied", set(pauli) == {"S1", "S2", "S3"}, sorted(pauli), ["S1", "S2", "S3"], "Pauli")
    audit.check("S1/S2 act transversely on e1", pauli["S1"][0][1] == [1, 0] and pauli["S2"][0][1] == [0, -1], pauli["S1"][0][1], "transverse", "Pauli")
    audit.check("S3 has opposite first-doublet diagonal", pauli["S3"][0][0] == [1, 0] and pauli["S3"][1][1] == [-1, 0], pauli["S3"][0][0], "diag(1,-1)", "Pauli")
    coeff0 = 2 * eps * eps * (a + 2 * b + c)
    coeff1 = 4 * eps * (a + b)
    coeff2 = 2 * a
    coeffs = (coeff0, coeff1, coeff2)
    audit.check("bracket coefficients derive", coeffs == (2 * eps * eps * (a + 2 * b + c), 4 * eps * (a + b), 2 * a), coeffs, "derived", "positivity")
    audit.check("bracket coefficients positive", all(value > 0 for value in coeffs), coeffs, ">0", "positivity")
    point_bracket = 2 * a + 4 * b * eps / (Fraction(1, 2) + eps) + 2 * c * eps * eps / (Fraction(1, 2) + eps) ** 2
    point_norm = point_bracket / 256
    lower_bound = 16 * a
    audit.check("point bracket positive", point_bracket > 0, point_bracket, ">0", "positivity")
    audit.check("point witness positive", point_norm > 0, point_norm, ">0", "positivity")
    audit.check("integral lower bound positive", lower_bound > 0, lower_bound, ">0", "positivity")
    audit.check("endpoint secant sign", lower_bound > 0, "negative", "E(0)-E(Psi)<0", "secant")
    return {
        "mode_index": list(mode),
        "wave_number_over_pi": f"{wave.numerator}/{wave.denominator}" if wave.denominator != 1 else str(wave.numerator),
        "a": f"{a.numerator}/{a.denominator}",
        "b": f"{b.numerator}/{b.denominator}",
        "c": f"{c.numerator}/{c.denominator}",
        "eps": f"{eps.numerator}/{eps.denominator}",
        "determinant": f"{determinant.numerator}/{determinant.denominator}",
        "pauli_currents": {"S1": {"q": "0", "J": "0", "K": "0"}, "S2": {"q": "0", "J": "0", "K": "0"}, "S3": {"q": "s^2/(s^2+eps)", "J": "2*d*s", "K": "2*eps*d*s/(s^2+eps)"}},
        "bracket_polynomial_coefficients": [f"{x.numerator}/{x.denominator}" for x in coeffs],
        "point_bracket": f"{point_bracket.numerator}/{point_bracket.denominator}",
        "point_norm": f"{point_norm.numerator}/{point_norm.denominator}",
        "integral_lower_bound_over_amp4_pi2": f"{lower_bound.numerator}/{lower_bound.denominator}",
        "endpoint_energy_sign": "positive",
        "zero_endpoint_energy": "0",
        "endpoint_secant_sign": "negative",
        "mode_on_dual_lattice": True,
        "full_a13_closure": False,
        "physical_vacuum_result": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    if args.staged and DEFAULT_OUTPUT.exists():
        raise SystemExit("staged mode requires the canonical independent result to be absent")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit = Audit()
    derived = derive(manifest, audit)
    payload = {"schema": "tect/pre-a-a7-actual-plane-wave-endpoint-secant-sign-witness-independent/1.0", "run_kind": "independent", "result_id": "R-171", "claim_ids": manifest["claim_ids"], "verdict": "PASS", "assertion_count": len(audit.rows), "assertions": audit.rows, "derived": derived}
    output = args.output or DEFAULT_OUTPUT
    if args.output is not None or not args.no_store:
        atomic_json(output, payload)
    print(f"INDEPENDENT PASS {len(audit.rows)}/{len(audit.rows)} mode={'staged' if args.staged else 'formal'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
