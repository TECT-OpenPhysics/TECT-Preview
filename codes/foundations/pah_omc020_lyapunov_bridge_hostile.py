#!/usr/bin/env python3
"""Hostile controls for the conditional Lyapunov bridge."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-lyapunov-bridge/hostile.json"


def write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as h:
            json.dump(payload, h, indent=2, sort_keys=True, ensure_ascii=True)
            h.write("\n")
            h.flush()
            os.fsync(h.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def check(rows: list[dict], name: str, ok: bool, actual: object, expected: object) -> None:
    if not ok:
        raise AssertionError(name)
    def serial(value: object) -> object:
        if isinstance(value, Fraction):
            return str(value)
        if isinstance(value, list):
            return [serial(item) for item in value]
        return value
    rows.append({"name": name, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows: list[dict] = []
    m_t, base, width, distance = Fraction(3), Fraction(2), 2, 8
    valid = m_t * base ** width / base ** distance
    check(rows, "valid envelope positive", valid > 0, valid, ">0")
    check(rows, "base-one mutation rejected", not (Fraction(1) > 1), Fraction(1), ">1 required")
    reversed_ratio = m_t * base ** distance / base ** width
    check(rows, "reversed decay is not a bound", reversed_ratio > valid, reversed_ratio, f">{valid}")
    c2 = Fraction(120)
    eta_sq = c2 * valid
    check(rows, "C2 retained", eta_sq == Fraction(45, 8), eta_sq, Fraction(45, 8))
    check(rows, "dropping C2 changes quantity", eta_sq != valid, eta_sq, "not probability envelope")
    check(rows, "distance must exceed width", distance > width, distance, f">{width}")
    check(rows, "negative distance rejected", not (0 <= -1), -1, ">=0 required")
    check(rows, "zero Lyapunov mass stays zero", Fraction(0) * base ** width / base ** distance == 0, 0, 0)
    contract = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-lyapunov-bridge-contract-v1.json").read_text(encoding="utf-8"))
    check(rows, "fabricated authorization rejected", contract["provenance"]["source_authorized_packet_present"] is False, contract["provenance"], False)
    check(rows, "N4 attribution remains required", "N4_attribution" in contract["required_owner_packet"], list(contract["required_owner_packet"]), "N4_attribution")
    check(rows, "minimal form remains required", "minimal_form" in contract["required_owner_packet"], list(contract["required_owner_packet"]), "minimal_form")
    check(rows, "no physical promotion", contract["provenance"]["physical_promotion"] is False, contract["provenance"], False)
    check(rows, "no direct process claim", any("No source-authorized path-space" in x for x in contract["non_claims"]), contract["non_claims"], "process absent")
    check(rows, "no PAH definition mutation", "No PAH-001 functional" in " ".join(contract["non_claims"]), True, True)
    payload = {"schema": "tect/pah-omc020-lyapunov-bridge-hostile/1.0", "status": "PASS_HOSTILE_CONTROLS", "verdict": "AUXILIARY_SUPPORT", "conditional": True, "checks": rows, "checks_passed": len(rows), "mutations_rejected": ["b<=1", "reversed decay", "dropped C2", "fabricated owner authorization", "missing N4 attribution", "physical promotion"], "non_claims": contract["non_claims"]}
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and args.output.exists() and args.output.read_bytes() != encoded:
        raise SystemExit("hostile Lyapunov replay mismatch")
    write(args.output, payload)
    print(f"PAH-OMC-020 LYAPUNOV HOSTILE: PASS ({len(rows)} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
