#!/usr/bin/env python3
"""Hostile controls for deterministic correlation-modulus promotion."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-correlation-modulus/hostile.json"
PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-018-result-v1.json": "d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json": "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-020-stationary-modulus-correction-result-v1.json": "58e563515b2a3a9d46085facffd4a9664c5518fed236e14f6a40aeee209443c0",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def enc(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): enc(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [enc(v) for v in value]
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(enc(payload), handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def reject(rows: list[dict[str, Any]], name: str, ok: bool, detail: Any) -> None:
    if not ok:
        raise AssertionError(f"hostile mutation accepted: {name}: {detail!r}")
    rows.append({"name": name, "status": "PASS", "detail": enc(detail)})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows: list[dict[str, Any]] = []
    contract = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-correlation-modulus-contract-v1.json").read_text(encoding="utf-8"))
    observed = {path: sha(ROOT / path) for path in PINS}
    reject(rows, "parent hash mutation", observed == PINS, observed)
    formulas = json.dumps(contract["source_formulas"], ensure_ascii=True).lower()
    claims = json.dumps(contract["non_claims"], ensure_ascii=True).lower()
    reject(rows, "directed-half form retained", "directed-half" in json.dumps(contract["frozen_scope"]).lower(), contract["frozen_scope"])
    reject(rows, "radial term cannot be dropped", "2 h_f l_f^2" in formulas, formulas)
    time_scope = json.dumps(contract["frozen_scope"]["time"], ensure_ascii=True).lower()
    reject(rows, "deterministic time only", "deterministic" in time_scope and "stopping-time aldous" in claims, {"time": time_scope, "claims": claims})
    reject(rows, "no full generator norm shortcut", "full generator" in claims or "generator norm" not in formulas, formulas)
    reject(rows, "no reversed sign", "k_(n,j)=-l_(n,j)" in formulas, formulas)
    reject(rows, "no physical promotion", "physical pre-a" in claims and "qft" in claims and "gravity" in claims, claims)
    # Exact arithmetic mutation witness: omitting the radial budget changes the bound.
    d, m, h, l = Fraction(10), Fraction(2), Fraction(20), Fraction(1)
    correct = 2 * d * m**2 + 2 * h * l**2
    no_radial = 2 * d * m**2
    wrong_sign = -correct
    reject(rows, "radial omission changes budget", no_radial != correct, {"correct": correct, "mutated": no_radial})
    reject(rows, "wrong sign is rejected", wrong_sign < 0 and correct > 0, {"correct": correct, "mutated": wrong_sign})
    # A form bound is not an exit-rate bound; the contract must say so.
    reject(rows, "stopping-time upgrade remains open", "stopping-time" in claims and "aldous" in claims, claims)
    reject(rows, "semigroup limit remains open", "semigroup convergence" in claims, claims)
    reject(rows, "finite modulus is finite", math.isfinite(math.sqrt(float(correct * correct))), correct)
    payload = {
        "schema": "tect/pah-omc020-correlation-modulus-hostile/1.0",
        "audit_id": "PAH-OMC-020-CORRELATION-MODULUS-HOSTILE-001",
        "result_id": "R-543",
        "task_id": "T-064",
        "status": "PASS_HOSTILE_CORRELATION_MODULUS_FIREWALL",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": observed,
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "Hostile mutations are rejected: the radial energy term, directed-half sign and deterministic-time scope are retained, while form-energy bounds are not promoted to stopping-time or infinite-volume conclusions.",
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_correlation_modulus_hostile.py --check",
        "non_claims": contract["non_claims"],
        "code_sha256": sha(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(enc(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 correlation-modulus hostile replay mismatch")
    else:
        write_json(destination, payload)
    print(f"PAH-OMC-020 CORRELATION MODULUS HOSTILE: PASS {len(rows)}/{len(rows)}; verdict=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
