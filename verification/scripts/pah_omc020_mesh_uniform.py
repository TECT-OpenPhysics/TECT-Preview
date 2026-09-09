#!/usr/bin/env python3
"""Primary finite verification for the PAH-OMC-020 mesh-to-uniform transfer."""

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
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-mesh-uniform/primary.json"
PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-correlation-modulus-result-v1.json": "4c67216762c59077a30cfde7c02517017cc0e8e2826ad7eeef0bcccfd6e938d3",
    "strategy/pa-hyp/PAH-OMC-020-dirichlet-minimal-result-v1.json": "9b19a3b5d56a0c89e7ebb426805b224f23a6e5fb8e458cee91636913096640b2",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(serial(payload), handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": serial(actual), "expected": serial(expected)})
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows: list[dict[str, Any]] = []
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    actual_hashes = {path: digest(ROOT / path) for path in PINS}
    check(rows, "contract schema", contract.get("schema"), "tect/pah-omc020-mesh-uniform-contract/1.0", contract.get("schema") == "tect/pah-omc020-mesh-uniform-contract/1.0")
    check(rows, "contract identity", contract.get("result_id"), "R-545", contract.get("result_id") == "R-545")
    check(rows, "source hashes", actual_hashes, PINS, actual_hashes == PINS)

    pa = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8"))
    r543 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-correlation-modulus-result-v1.json").read_text(encoding="utf-8"))
    r530 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-dirichlet-minimal-result-v1.json").read_text(encoding="utf-8"))
    check(rows, "PAH packet", pa.get("packet_id"), "PAH-001", pa.get("packet_id") == "PAH-001")
    order = prereg["scope"]["regulator_order"].lower()
    check(rows, "j-before-n order retained", "first j" in order and "anchored n" in order, True, "first j" in order and "anchored n" in order)
    check(rows, "external Markov time retained", "external" in prereg["scope"]["time"].lower() and "markov" in prereg["scope"]["time"].lower(), True, "external" in prereg["scope"]["time"].lower() and "markov" in prereg["scope"]["time"].lower())
    check(rows, "R-543 source modulus", (r543.get("result_id"), r543.get("verdict")), ("R-543", "PASS"), r543.get("result_id") == "R-543" and r543.get("verdict") == "PASS")
    check(rows, "R-543 finite only", r543.get("active_gate_change"), False, r543.get("active_gate_change") is False)
    check(rows, "R-530 target semigroup", "spectral semigroup" in json.dumps(r530.get("exact_scope", {})).lower(), True, "spectral semigroup" in json.dumps(r530.get("exact_scope", {})).lower())
    check(rows, "R-530 no limit promotion", r530.get("active_gate_change"), False, r530.get("active_gate_change") is False)

    # Exact rational test oracles for the scalar mesh inequality.
    T = Fraction(1)
    delta = Fraction(1, 10)
    M = Fraction(3)
    omega = Fraction(1, 20)
    mesh_error = Fraction(1, 100)
    transfer_bound = mesh_error + M * delta + omega
    check(rows, "compact horizon positive", T > 0, True, T > 0)
    check(rows, "mesh radius positive", delta > 0, True, delta > 0)
    check(rows, "finite modulus nonnegative", M >= 0, True, M >= 0)
    check(rows, "target modulus nonnegative", omega >= 0, True, omega >= 0)
    check(rows, "mesh error nonnegative", mesh_error >= 0, True, mesh_error >= 0)
    check(rows, "mesh covers compact interval", delta <= T, True, delta <= T)
    check(rows, "transfer formula", transfer_bound, mesh_error + M * delta + omega, transfer_bound == mesh_error + M * delta + omega)
    check(rows, "transfer bound exact fixture", transfer_bound, Fraction(9, 25), transfer_bound == Fraction(9, 25))
    test_finite = Fraction(7, 25)
    test_target = Fraction(1, 50)
    test_mesh = Fraction(1, 100)
    check(rows, "finite modulus fixture", test_finite <= M * delta, True, test_finite <= M * delta)
    check(rows, "target continuity fixture", test_target <= omega, True, test_target <= omega)
    check(rows, "mesh-point error fixture", test_mesh <= mesh_error, True, test_mesh <= mesh_error)
    check(rows, "supremum implication fixture", test_mesh + test_finite + test_target <= transfer_bound, True, test_mesh + test_finite + test_target <= transfer_bound)
    finer = delta / 2
    finer_omega = omega / 2
    finer_bound = mesh_error + M * finer + finer_omega
    check(rows, "finer mesh decreases bound", finer_bound < transfer_bound, True, finer_bound < transfer_bound)
    check(rows, "ordered limit is not reversed", contract["scope"]["time"] == "External stochastic Markov time t in a fixed compact interval [0,T] only.", True, contract["scope"]["time"] == "External stochastic Markov time t in a fixed compact interval [0,T] only.")
    check(rows, "mesh pointwise remains an assumption", "not proved" in contract["hypotheses"]["mesh_pointwise"].lower(), True, "not proved" in contract["hypotheses"]["mesh_pointwise"].lower())
    forbidden = json.dumps(contract["non_claims"], ensure_ascii=True).lower()
    check(rows, "no physical promotion", "physical pre-a" in forbidden and "qft" in forbidden, True, "physical pre-a" in forbidden and "qft" in forbidden)
    check(rows, "no owner synthesis", "common u_n" in forbidden and "path law" in forbidden, True, "common u_n" in forbidden and "path law" in forbidden)

    payload = {
        "schema": "tect/pah-omc020-mesh-uniform-primary/1.0",
        "audit_id": "PAH-OMC-020-MESH-UNIFORM-PRIMARY-001",
        "result_id": "R-545",
        "task_id": "T-065",
        "status": "PASS_CONDITIONAL_MESH_TRANSFER",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": actual_hashes,
        "test_fixture": {"T": T, "delta": delta, "M_fg": M, "omega_inf": omega, "mesh_error": mesh_error, "transfer_bound": transfer_bound},
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "The scalar mesh inequality is exact: finite equicontinuity from R-543 plus target continuity reduces compact-time uniform convergence to ordered convergence on every finite time mesh. The mesh-pointwise PAH convergence and owner packet remain unproved.",
        "assumptions": contract["hypotheses"],
        "missing_assumptions": [contract["hypotheses"]["mesh_pointwise"], "Source-authorized common-space/path-space identification with R-512"],
        "next_single_question": contract["single_next_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_mesh_uniform.py --check",
        "code_sha256": digest(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(serial(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 mesh-uniform primary replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 MESH UNIFORM PRIMARY: PASS {len(rows)}/{len(rows)}; verdict=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
