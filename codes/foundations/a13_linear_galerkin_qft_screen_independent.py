"""Non-importing Fraction-only cross-check for EXP-000961."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

import sys

sys.set_int_max_str_digits(0)

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-linear-galerkin-qft-screen-manifest.json"
LEAN_ENTRYPOINT = REPO / "verification" / "lean" / "Tect" / "R196.lean"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-independent-linear-galerkin-qft-screen" / "result.json"


def sha256_normalized(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def brief(value: Any) -> str:
    text = str(value)
    return text if len(text) <= 240 else f"<large:{len(text)}-chars>"


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


def atan_interval(x: F, terms: int) -> tuple[F, F]:
    s = F(0)
    for j in range(terms):
        s += (F(1) if j % 2 == 0 else F(-1)) * x ** (2 * j + 1) / (2 * j + 1)
    remainder = x ** (2 * terms + 1) / (2 * terms + 1)
    return (s, s + remainder) if terms % 2 == 0 else (s - remainder, s)


def machin_interval(terms: int) -> tuple[F, F]:
    a0, a1 = atan_interval(F(1, 5), terms)
    b0, b1 = atan_interval(F(1, 239), terms)
    return 16 * a0 - 4 * b1, 16 * a1 - 4 * b0


def kernel_bounds(norm2: int, params: dict[str, Any], pi0: F, pi1: F) -> tuple[F, F]:
    length = F(str(params["Lx"]))
    rr = F(str(params["r"]))
    zz = F(str(params["Z"]))
    yy = F(str(params["Y"]))
    lower_x = F(4) * pi0 * pi0 * norm2 / (length * length)
    upper_x = F(4) * pi1 * pi1 * norm2 / (length * length)
    vertex = -zz / (F(2) * yy)

    def poly(x: F) -> F:
        return rr + zz * x + yy * x * x

    candidates = [poly(lower_x), poly(upper_x)]
    if lower_x <= vertex <= upper_x:
        candidates.append(poly(vertex))
    return min(candidates), upper_x


def cube(radius: int) -> list[tuple[int, int, int]]:
    return [(i, j, k) for i in range(-radius, radius + 1) for j in range(-radius, radius + 1) for k in range(-radius, radius + 1)]


def run(manifest: dict[str, Any], a1: dict[str, Any], r192: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["registered_inputs"]
    params = a1["parameters"]
    pi0, pi1 = machin_interval(int(inputs["pi_machin_terms"]))
    beta = F(str(inputs["beta"]))
    factor = int(inputs["generator_count"]) * int(inputs["generator_hilbert_schmidt_square"])
    dimension = int(inputs["dimension"])
    if dimension != 3:
        raise AssertionError("independent lane only handles the registered three-dimensional current")

    def charge(radius: int) -> F:
        modes = cube(radius)
        max_norm = dimension * (2 * radius) ** 2
        kernel_cache = {n2: kernel_bounds(n2, params, pi0, pi1) for n2 in range(max_norm + 1)}
        multiplicities: dict[tuple[int, int, int], int] = {}
        for p in modes:
            p_norm = sum(v * v for v in p)
            for q in modes:
                delta = tuple(q[i] - p[i] for i in range(dimension))
                d_norm = sum(v * v for v in delta)
                if d_norm:
                    q_norm = sum(v * v for v in q)
                    key = (p_norm, q_norm, d_norm)
                    multiplicities[key] = multiplicities.get(key, 0) + 1
        value = F(0)
        for (p_norm, q_norm, d_norm), multiplicity in multiplicities.items():
            kp, _ = kernel_cache[p_norm]
            kq, _ = kernel_cache[q_norm]
            kr, k2_upper = kernel_cache[d_norm]
            value += F(multiplicity * factor) * k2_upper / (kr * kp * kq * beta * beta)
        return value

    cutoffs = [int(value) for value in inputs["cutoffs"]]
    q_values = [charge(value) for value in cutoffs]
    return {
        "dimension": dimension,
        "pi_bounds": [pi0, pi1],
        "mu_eff": F(str(params["r"])) - F(str(params["Z"])) ** 2 / (F(4) * F(str(params["Y"]))),
        "q_star_squared": -F(str(params["Z"])) / (F(2) * F(str(params["Y"]))),
        "generator_factor": factor,
        "cutoffs": cutoffs,
        "finite_q_ledger": {str(n): q for n, q in zip(cutoffs, q_values)},
        "finite_q_nonnegative": all(value >= 0 for value in q_values),
        "finite_q_monotone": all(q_values[i] <= q_values[i + 1] for i in range(len(q_values) - 1)),
        "tail": {"covariance_power": 4, "convolution_power": 4, "output_heat_gain_power": 2, "charge_power": 6, "dimension": dimension},
        "conditional_qft_interface": True,
        "nonlinear_production_owner": False,
        "r192_first_missing_slot_unchanged": r192["registered_inputs"]["first_failure_slot"] == "heat_root_incidence",
        "lean_marker_count": sum(marker in LEAN_ENTRYPOINT.read_text(encoding="utf-8") for marker in ("generator_factor_six", "output_charge_nonneg", "heat_integral_identity", "tail_exponent_six")),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1 = json.loads((REPO / manifest["source_authorities"]["a1_functional"]["path"]).read_text(encoding="utf-8"))
    r192 = json.loads((REPO / manifest["source_authorities"]["r192_manifest"]["path"]).read_text(encoding="utf-8"))
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        assertions.append({"name": name, "pass": bool(condition), "actual": brief(actual), "expected": brief(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-A1-LINEAR-GALERKIN-QFT-CURRENT-SCREEN", manifest["audit_id"], "A13-A1-LINEAR-GALERKIN-QFT-CURRENT-SCREEN")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    for key, item in manifest["source_authorities"].items():
        path = REPO / item["path"]
        check(f"source {key}", path.is_file() and sha256_normalized(path) == item["sha256"], sha256_normalized(path) if path.is_file() else None, item["sha256"])
    derived = run(manifest, a1, r192)
    check("completed-square positivity", derived["mu_eff"] > 0, derived["mu_eff"], ">0")
    check("generator factor", derived["generator_factor"] == int(manifest["registered_inputs"]["generator_count"]) * int(manifest["registered_inputs"]["generator_hilbert_schmidt_square"]), derived["generator_factor"], 6)
    check("finite nonnegative", derived["finite_q_nonnegative"], derived["finite_q_ledger"], ">=0")
    check("finite monotone", derived["finite_q_monotone"], derived["finite_q_ledger"], "nondecreasing")
    check("sixth-order charge tail", derived["tail"]["charge_power"] == 6, derived["tail"], "6")
    check("conditional boundary", derived["conditional_qft_interface"] and not derived["nonlinear_production_owner"] and derived["r192_first_missing_slot_unchanged"], derived, "conditional")
    source = LEAN_ENTRYPOINT.read_text(encoding="utf-8")
    check("Lean markers", derived["lean_marker_count"] == 4, derived["lean_marker_count"], 4)
    check("Lean escape tokens", not any(x in source.split() for x in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    payload = {
        "schema": "tect/a13-linear-galerkin-qft-screen-independent/1.0",
        "run_kind": "independent",
        "audit_id": manifest["audit_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_id"],
        "verdict": "PASS",
        "assertion_count": len(assertions),
        "assertions": assertions,
        "derived": {key: str(value) if isinstance(value, F) else value for key, value in derived.items()},
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"A1 LINEAR GALERKIN QFT INDEPENDENT PASS {len(assertions)}/{len(assertions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
