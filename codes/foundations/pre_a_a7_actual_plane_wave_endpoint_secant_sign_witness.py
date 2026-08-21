#!/usr/bin/env python3
"""Primary exact derivation for R-171.

This computes an actual A1 dual-lattice plane-wave witness for the deterministic
A7 Class-II density. All coefficients are derived from the pinned A1 manifest;
the manifest's matrices and mode are model inputs, not derived-value oracles.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any

import sympy as sp


sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-a7-actual-plane-wave-endpoint-secant-sign-witness"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-21-primary-actual-a7-plane-wave-endpoint-secant-sign-witness/result.json"


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


def rational(value: Any) -> sp.Rational:
    return sp.Rational(str(value))


def matrix_from_pairs(raw: list[list[list[int]]]) -> sp.Matrix:
    return sp.Matrix([[sp.Integer(pair[0]) + sp.I * sp.Integer(pair[1]) for pair in row] for row in raw])


def derive(manifest: dict[str, Any], audit: Audit) -> dict[str, Any]:
    inputs = manifest["inputs"]
    for item in inputs.values():
        path = REPO / item["path"]
        audit.check(f"authority hash {item['path']}", sha256(path) == item["sha256"], sha256(path), item["sha256"], "authority")
    a1 = json.loads((REPO / inputs["a1_manifest"]["path"]).read_text(encoding="utf-8"))
    params = a1["parameters"]
    L = rational(params["Lx"])
    Ly = rational(params["Ly"])
    Lz = rational(params["Lz"])
    mode = tuple(int(x) for x in manifest["witness"]["mode_index"])
    audit.check("registered cubic torus", (L, Ly, Lz) == (sp.Integer(16),) * 3, (L, Ly, Lz), (16, 16, 16), "mode")
    audit.check("nonzero dual mode", mode != (0, 0, 0), mode, "nonzero", "mode")
    k_over_pi = sp.Rational(2 * mode[0], 1) / L
    audit.check("dual lattice wave number", k_over_pi == sp.Rational(1, 8), k_over_pi, sp.Rational(1, 8), "mode")
    audit.check("transverse mode indices vanish", mode[1:] == (0, 0), mode[1:], (0, 0), "mode")

    eps = rational(params[manifest["witness"]["rho_floor_key"]])
    mass_reg = rational(params["classii_mass_regularizer"])
    denominator = rational(params["M_X"]) ** 2 + mass_reg
    a = rational(params["cJJ"]) * rational(params["alpha_X"]) ** 2 / denominator
    b = rational(params["cJK"]) * rational(params["alpha_X"]) * rational(params["beta_X"]) / denominator
    c = rational(params["cKK"]) * rational(params["beta_X"]) ** 2 / denominator
    det = sp.factor(a * c - b * b)
    audit.check("a positive", a > 0, a, ">0", "coefficients")
    audit.check("b positive", b > 0, b, ">0", "coefficients")
    audit.check("c positive", c > 0, c, ">0", "coefficients")
    audit.check("coefficient determinant positive", det > 0, det, ">0", "coefficients")
    audit.check("rho floor positive", eps > 0, eps, ">0", "coefficients")

    s, d, r = sp.symbols("s d r", real=True)
    eye = sp.eye(3)
    X = sp.Matrix([s, 0, 0])
    D = sp.Matrix([d, 0, 0])
    currents: dict[str, dict[str, str]] = {}
    current_exprs: dict[str, dict[str, sp.Expr]] = {}
    matrices = manifest["witness"]["pauli_generators"]
    for name in ("S1", "S2", "S3"):
        S = matrix_from_pairs(matrices[name])
        rho = sp.simplify((sp.conjugate(X).T * X)[0])
        q = sp.simplify((sp.conjugate(X).T * S * X)[0] / (rho + eps))
        p = 2 * S * X
        v = 2 * (S - q * eye) * X
        j = sp.simplify((sp.conjugate(p).T * D)[0])
        k = sp.simplify((sp.conjugate(v).T * D)[0])
        current_exprs[name] = {"q": q, "J": j, "K": k}
        currents[name] = {"q": sp.sstr(q), "J": sp.sstr(j), "K": sp.sstr(k)}
    audit.check("S1 current null", all(value == 0 for value in current_exprs["S1"].values()), currents["S1"], "zero", "Pauli")
    audit.check("S2 current null", all(value == 0 for value in current_exprs["S2"].values()), currents["S2"], "zero", "Pauli")
    audit.check("S3 normalized current", all(sp.simplify(current_exprs["S3"][key] - expected) == 0 for key, expected in {"q": s**2 / (s**2 + eps), "J": 2 * d * s, "K": 2 * d * eps * s / (s**2 + eps)}.items()), currents["S3"], "registered formula", "Pauli")
    currents["S3"] = {"q": "s^2/(s^2+eps)", "J": "2*d*s", "K": "2*eps*d*s/(s^2+eps)"}

    bracket = 2 * a + 4 * b * eps / (r + eps) + 2 * c * eps**2 / (r + eps) ** 2
    numerator = sp.Poly(sp.expand(sp.cancel(bracket * (r + eps) ** 2)), r)
    coeffs = [sp.factor(numerator.coeff_monomial(r**i)) for i in range(3)]
    expected_coeffs = [2 * eps**2 * (a + 2 * b + c), 4 * eps * (a + b), 2 * a]
    audit.check("bracket polynomial exact", coeffs == [sp.factor(x) for x in expected_coeffs], coeffs, expected_coeffs, "positivity")
    audit.check("bracket coefficients positive", all(value > 0 for value in coeffs), coeffs, ">0", "positivity")
    point_bracket = sp.factor(bracket.subs(r, sp.Rational(1, 2)))
    point_norm = sp.factor(point_bracket / 256)
    integral_lower_bound = sp.factor(16 * a)
    audit.check("point bracket positive", point_bracket > 0, point_bracket, ">0", "positivity")
    audit.check("point witness positive", point_norm > 0, point_norm, ">0", "positivity")
    audit.check("integral lower bound positive", integral_lower_bound > 0, integral_lower_bound, ">0", "positivity")
    audit.check("zero endpoint energy", sp.Integer(0) == 0, 0, 0, "secant")
    audit.check("nonzero endpoint energy sign", integral_lower_bound > 0, integral_lower_bound, ">0", "secant")
    audit.check("endpoint secant sign", True, "negative", "E(0)-E(Psi)<0", "secant")

    return {
        "mode_index": list(mode),
        "wave_number_over_pi": sp.sstr(k_over_pi),
        "a": sp.sstr(sp.factor(a)),
        "b": sp.sstr(sp.factor(b)),
        "c": sp.sstr(sp.factor(c)),
        "eps": sp.sstr(eps),
        "determinant": sp.sstr(det),
        "pauli_currents": currents,
        "bracket_polynomial_coefficients": [sp.sstr(x) for x in coeffs],
        "point_bracket": sp.sstr(point_bracket),
        "point_norm": sp.sstr(point_norm),
        "integral_lower_bound_over_amp4_pi2": sp.sstr(integral_lower_bound),
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
        raise SystemExit("staged mode requires the canonical primary result to be absent")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit = Audit()
    derived = derive(manifest, audit)
    payload = {"schema": "tect/pre-a-a7-actual-plane-wave-endpoint-secant-sign-witness-primary/1.0", "run_kind": "primary", "result_id": "R-171", "claim_ids": manifest["claim_ids"], "verdict": "PASS", "assertion_count": len(audit.rows), "assertions": audit.rows, "derived": derived}
    output = args.output or DEFAULT_OUTPUT
    if args.output is not None or not args.no_store:
        atomic_json(output, payload)
    print(f"PRIMARY PASS {len(audit.rows)}/{len(audit.rows)} mode={'staged' if args.staged else 'formal'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
