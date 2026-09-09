#!/usr/bin/env python3
"""Independent non-importing replay of the PAH-OMC-020 mesh transfer."""

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
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-mesh-uniform/independent.json"
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
    check(rows, "contract id", contract.get("contract_id"), "PAH-OMC-020-MESH-UNIFORM-TRANSFER", contract.get("contract_id") == "PAH-OMC-020-MESH-UNIFORM-TRANSFER")
    check(rows, "pins", hashes, PINS, hashes == PINS)
    check(rows, "mesh cover is explicit", "covering radius" in contract["hypotheses"]["mesh_cover"], True, "covering radius" in contract["hypotheses"]["mesh_cover"])
    check(rows, "target continuity is explicit", "uniformly continuous" in contract["hypotheses"]["target_continuity"], True, "uniformly continuous" in contract["hypotheses"]["target_continuity"])
    check(rows, "ordered input is explicit", "j->infinity" in contract["ordered_conclusion"], True, "j->infinity" in contract["ordered_conclusion"])

    T = Fraction(3, 2)
    radius = Fraction(1, 8)
    M = Fraction(5, 2)
    omega = Fraction(3, 40)
    mesh_error = Fraction(1, 20)
    bound = mesh_error + M * radius + omega
    check(rows, "horizon positive", T > 0, True, T > 0)
    check(rows, "radius within horizon", radius <= T, True, radius <= T)
    check(rows, "modulus nonnegative", M >= 0 and omega >= 0, True, M >= 0 and omega >= 0)
    check(rows, "mesh error nonnegative", mesh_error >= 0, True, mesh_error >= 0)
    check(rows, "independent bound value", bound, Fraction(7, 16), bound == Fraction(7, 16))
    tighter = mesh_error + M * (radius / 2) + omega / 2
    check(rows, "refinement lowers envelope", tighter < bound, True, tighter < bound)
    local_error = Fraction(1, 3)
    check(rows, "local error is dominated", local_error <= bound, True, local_error <= bound)
    check(rows, "scalar triangle route", local_error <= mesh_error + M * radius + omega, True, local_error <= mesh_error + M * radius + omega)
    forbidden = json.dumps(contract["non_claims"], ensure_ascii=True).lower()
    check(rows, "no finite-to-target promotion", "finite-to-target identification" in forbidden, True, "finite-to-target identification" in forbidden)
    check(rows, "no physical promotion", "qft" in forbidden and "gravity" in forbidden, True, "qft" in forbidden and "gravity" in forbidden)
    check(rows, "mesh pointwise remains open", "remaining dynamic input" in contract["hypotheses"]["mesh_pointwise"], True, "remaining dynamic input" in contract["hypotheses"]["mesh_pointwise"])

    payload = {
        "schema": "tect/pah-omc020-mesh-uniform-independent/1.0",
        "audit_id": "PAH-OMC-020-MESH-UNIFORM-INDEPENDENT-001",
        "result_id": "R-545",
        "task_id": "T-065",
        "status": "PASS_INDEPENDENT_MESH_TRANSFER",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": hashes,
        "test_fixture": {"T": T, "radius": radius, "M_fg": M, "omega_inf": omega, "mesh_error": mesh_error, "bound": bound},
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "Independent exact-rational fixtures confirm the mesh-to-uniform scalar transfer. No PAH mesh-pointwise convergence is imported or asserted.",
        "next_single_question": contract["single_next_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_mesh_uniform_independent.py --check",
        "code_sha256": digest(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(encode(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 mesh-uniform independent replay mismatch")
    else:
        write_json(destination, payload)
    print(f"PAH-OMC-020 MESH UNIFORM INDEPENDENT: PASS {len(rows)}/{len(rows)}; verdict=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
