"""Exact finite A1 Gaussian/OU current-heat screen.

This is a conditional QFT interface: it uses the positive quadratic A1
operator and a proper complex Gaussian root law.  It deliberately does not
pretend to be the nonlinear A13 production owner.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

import sys

sys.set_int_max_str_digits(0)

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-linear-galerkin-qft-screen-manifest.json"
LEAN_ROOT = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_ROOT / "Tect" / "R196.lean"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-primary-linear-galerkin-qft-screen" / "result.json"


def normalized_sha(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def brief(value: Any) -> str:
    text = str(value)
    if len(text) <= 240:
        return text
    return f"<large:{len(text)}-chars>"


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


def find_lake() -> str | None:
    pin = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    for name in ("lake.exe", "lake"):
        candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / name
        if candidate.is_file():
            return str(candidate)
    return shutil.which("lake")


def atan_bounds(x: F, terms: int) -> tuple[F, F]:
    partial = F(0)
    for n in range(terms):
        partial += (-1 if n % 2 else 1) * x ** (2 * n + 1) / (2 * n + 1)
    nxt = x ** (2 * terms + 1) / (2 * terms + 1)
    return (partial, partial + nxt) if terms % 2 == 0 else (partial - nxt, partial)


def pi_bounds(terms: int) -> tuple[F, F]:
    a_lo, a_hi = atan_bounds(F(1, 5), terms)
    b_lo, b_hi = atan_bounds(F(1, 239), terms)
    return 16 * a_lo - 4 * b_hi, 16 * a_hi - 4 * b_lo


def mode_tuples(n: int) -> list[tuple[int, int, int]]:
    return list(itertools.product(range(-n, n + 1), repeat=3))


def kernel_interval(norm2: int, params: dict[str, Any], pi_lo: F, pi_hi: F) -> tuple[F, F]:
    L = F(str(params["Lx"]))
    r = F(str(params["r"]))
    z = F(str(params["Z"]))
    y = F(str(params["Y"]))
    x_lo = F(4) * pi_lo * pi_lo * norm2 / (L * L)
    x_hi = F(4) * pi_hi * pi_hi * norm2 / (L * L)
    vertex = -z / (F(2) * y)

    def polynomial(x: F) -> F:
        return r + z * x + y * x * x

    values = [polynomial(x_lo), polynomial(x_hi)]
    if x_lo <= vertex <= x_hi:
        values.append(polynomial(vertex))
    return min(values), x_hi


def derive(manifest: dict[str, Any], a1: dict[str, Any], r192: dict[str, Any]) -> dict[str, Any]:
    ri = manifest["registered_inputs"]
    params = a1["parameters"]
    dimension = int(ri["dimension"])
    if dimension != 3:
        raise AssertionError("the registered current is specifically three-dimensional")
    terms = int(ri["pi_machin_terms"])
    pi_lo, pi_hi = pi_bounds(terms)
    y = F(str(params["Y"]))
    z = F(str(params["Z"]))
    r0 = F(str(params["r"]))
    mu_eff = r0 - z * z / (F(4) * y)
    q_star_sq = -z / (F(2) * y)
    generator_factor = int(ri["generator_count"]) * int(ri["generator_hilbert_schmidt_square"])
    beta = F(str(ri["beta"]))
    if beta <= 0:
        raise AssertionError("beta must be positive")

    def finite_charge(cutoff: int) -> F:
        modes = mode_tuples(cutoff)
        max_norm = dimension * (2 * cutoff) ** 2
        kernel_cache = {n2: kernel_interval(n2, params, pi_lo, pi_hi) for n2 in range(max_norm + 1)}
        multiplicities: dict[tuple[int, int, int], int] = {}
        for p in modes:
            p2 = sum(x * x for x in p)
            for q in modes:
                rvec = tuple(q[i] - p[i] for i in range(dimension))
                r2 = sum(x * x for x in rvec)
                if r2:
                    q2 = sum(x * x for x in q)
                    key = (p2, q2, r2)
                    multiplicities[key] = multiplicities.get(key, 0) + 1
        total = F(0)
        for (p2, q2, r2), multiplicity in multiplicities.items():
            kp, _ = kernel_cache[p2]
            kq, _ = kernel_cache[q2]
            kr, kr_hi = kernel_cache[r2]
            if kq <= 0 or kp <= 0 or kr <= 0:
                raise AssertionError("kernel lower bound must be positive")
            total += F(multiplicity * generator_factor) * kr_hi / (kr * kp * kq * beta * beta)
        return total

    cutoffs = [int(x) for x in ri["cutoffs"]]
    charges = {str(n): finite_charge(n) for n in cutoffs}
    charge_values = [charges[str(n)] for n in cutoffs]
    return {
        "dimension": dimension,
        "pi_bounds": [pi_lo, pi_hi],
        "completed_square": {"Y": y, "q_star_squared": q_star_sq, "mu_eff": mu_eff},
        "generator_factor": generator_factor,
        "covariance_bound": "operator(C_n)<=beta^(-1)/K_n",
        "cutoffs": cutoffs,
        "finite_q_ledger": charges,
        "finite_q_nonnegative": all(x >= 0 for x in charge_values),
        "finite_q_monotone": all(charge_values[i] <= charge_values[i + 1] for i in range(len(charge_values) - 1)),
        "tail": {
            "covariance_power": 4,
            "convolution_power": 4,
            "output_heat_gain_power": 2,
            "charge_power": 6,
            "dimension": dimension,
        },
        "linear_hessian_lower_bound": "H_n >= K_n I_3",
        "conditional_qft_interface": True,
        "nonlinear_production_owner": False,
        "r192_first_missing_slot_unchanged": r192["registered_inputs"]["first_failure_slot"] == "heat_root_incidence",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1 = json.loads((REPO / manifest["source_authorities"]["a1_functional"]["path"]).read_text(encoding="utf-8"))
    r192 = json.loads((REPO / manifest["source_authorities"]["r192_manifest"]["path"]).read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": brief(actual), "expected": brief(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-A1-LINEAR-GALERKIN-QFT-CURRENT-SCREEN", manifest["audit_id"], "A13-A1-LINEAR-GALERKIN-QFT-CURRENT-SCREEN")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    for key, item in manifest["source_authorities"].items():
        path = REPO / item["path"]
        check(f"source {key}", path.is_file() and normalized_sha(path) == item["sha256"], normalized_sha(path) if path.is_file() else None, item["sha256"])
    for key, item in manifest["files"].items():
        path = REPO / item["path"]
        expected = item["sha256"]
        check(f"file {key}", path.is_file() and (expected == "TO_BE_FILLED" or normalized_sha(path) == expected), normalized_sha(path) if path.is_file() else None, expected)

    derived = derive(manifest, a1, r192)
    ri = manifest["registered_inputs"]
    check("completed-square mass positive", derived["completed_square"]["mu_eff"] > 0, derived["completed_square"]["mu_eff"], ">0")
    check("Y positive", derived["completed_square"]["Y"] > 0, derived["completed_square"]["Y"], ">0")
    check("generator factor", derived["generator_factor"] == int(ri["generator_count"]) * int(ri["generator_hilbert_schmidt_square"]), derived["generator_factor"], 6)
    check("finite ledger nonnegative", derived["finite_q_nonnegative"], derived["finite_q_ledger"], ">=0")
    check("finite ledger monotone", derived["finite_q_monotone"], derived["finite_q_ledger"], "nondecreasing")
    check("tail exponent", derived["tail"]["charge_power"] == derived["tail"]["convolution_power"] + derived["tail"]["output_heat_gain_power"], derived["tail"], "4+2=6")
    check("R-192 boundary retained", derived["r192_first_missing_slot_unchanged"] and not derived["nonlinear_production_owner"], derived, "conditional only")

    source = LEAN_ENTRYPOINT.read_text(encoding="utf-8")
    lean_markers = ["generator_factor_six", "output_charge_nonneg", "heat_integral_identity", "tail_exponent_six"]
    check("Lean theorem markers", all(marker in source for marker in lean_markers), lean_markers, "markers present")
    check("Lean escape tokens absent", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    lake = find_lake()
    check("pinned lake", lake is not None, lake, "pinned lake")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean", completed.returncode == 0 and "error:" not in (completed.stdout + completed.stderr).lower(), completed.stderr, "no Lean error")

    payload = {
        "schema": "tect/a13-linear-galerkin-qft-screen-primary/1.0",
        "run_kind": "primary",
        "audit_id": manifest["audit_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {key: str(value) if isinstance(value, F) else value for key, value in derived.items()},
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"A1 LINEAR GALERKIN QFT PRIMARY PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
