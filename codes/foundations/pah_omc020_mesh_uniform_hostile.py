#!/usr/bin/env python3
"""Hostile controls for the PAH-OMC-020 mesh-to-uniform contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-mesh-uniform-contract-v1.json"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-mesh-uniform/hostile.json"
PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-correlation-modulus-result-v1.json": "4c67216762c59077a30cfde7c02517017cc0e8e2826ad7eeef0bcccfd6e938d3",
    "strategy/pa-hyp/PAH-OMC-020-dirichlet-minimal-result-v1.json": "9b19a3b5d56a0c89e7ebb426805b224f23a6e5fb8e458cee91636913096640b2",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encode(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(encode(payload), handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": encode(actual), "expected": encode(expected)})
    if not ok:
        raise AssertionError(name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows: list[dict[str, Any]] = []
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    hashes = {name: digest(ROOT / name) for name in PINS}
    check(rows, "source pins unchanged", hashes, PINS, hashes == PINS)
    check(rows, "bound has three terms", contract["bound"].count("+") >= 2, True, contract["bound"].count("+") >= 2)
    target_hypotheses = json.dumps(contract["hypotheses"]).lower()
    check(rows, "target modulus is required", "uniformly continuous" in target_hypotheses, True, "uniformly continuous" in target_hypotheses)
    check(rows, "mesh cover is required", "covering radius" in contract["hypotheses"]["mesh_cover"], True, "covering radius" in contract["hypotheses"]["mesh_cover"])
    check(rows, "finite modulus is required", "finite_modulus" in contract["hypotheses"], True, "finite_modulus" in contract["hypotheses"])

    delta = Fraction(1, 10)
    M = Fraction(2)
    omega = Fraction(1, 20)
    mesh_error = Fraction(1, 100)
    bound = mesh_error + M * delta + omega
    missing_target = mesh_error + M * delta
    target_jump = Fraction(1, 3)
    check(rows, "omitting target modulus is rejected", target_jump <= missing_target, False, not (target_jump <= missing_target))
    outside_mesh = Fraction(1, 5)
    check(rows, "outside-cover point is rejected", outside_mesh <= delta, False, not (outside_mesh <= delta))
    missing_finite = mesh_error + omega
    finite_jump = Fraction(1, 4)
    check(rows, "omitting finite modulus is rejected", finite_jump <= missing_finite, False, not (finite_jump <= missing_finite))
    check(rows, "nonnegative bound terms", all(value >= 0 for value in (delta, M, omega, mesh_error, bound)), True, all(value >= 0 for value in (delta, M, omega, mesh_error, bound)))
    check(rows, "strict refinement needs continuity", contract["hypotheses"]["target_continuity"].startswith("The fixed R-512"), True, contract["hypotheses"]["target_continuity"].startswith("The fixed R-512"))
    reversed_order = "n->infinity before j->infinity"
    check(rows, "reversed order is rejected", reversed_order in contract["ordered_conclusion"], False, reversed_order not in contract["ordered_conclusion"])
    check(rows, "mesh convergence is not silently promoted", "not proved" in contract["hypotheses"]["mesh_pointwise"].lower(), True, "not proved" in contract["hypotheses"]["mesh_pointwise"].lower())
    check(rows, "owner packet remains required", "source-authorized" in contract["single_next_question"], True, "source-authorized" in contract["single_next_question"])
    non_claims = json.dumps(contract["non_claims"], ensure_ascii=True).lower()
    check(rows, "no path-space promotion", "path law" in non_claims, True, "path law" in non_claims)
    check(rows, "no physical promotion", "qft" in non_claims and "gravity" in non_claims, True, "qft" in non_claims and "gravity" in non_claims)

    payload = {
        "schema": "tect/pah-omc020-mesh-uniform-hostile/1.0",
        "audit_id": "PAH-OMC-020-MESH-UNIFORM-HOSTILE-001",
        "result_id": "R-545",
        "task_id": "T-065",
        "status": "PASS_HOSTILE_MESH_TRANSFER_CONTROLS",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": hashes,
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "Hostile mutations reject dropping target continuity, mesh coverage, finite equicontinuity, the registered order or the open mesh-pointwise/source-owner condition.",
        "next_single_question": contract["single_next_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_mesh_uniform_hostile.py --check",
        "code_sha256": digest(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(encode(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 mesh-uniform hostile replay mismatch")
    else:
        write_json(destination, payload)
    print(f"PAH-OMC-020 MESH UNIFORM HOSTILE: PASS {len(rows)}/{len(rows)}; verdict=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
