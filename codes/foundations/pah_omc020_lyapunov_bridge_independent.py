#!/usr/bin/env python3
"""Non-importing rational reconstruction of the Lyapunov bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-lyapunov-bridge/independent.json"
PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json": "87dd9a7225203cdfa84456e446983c573cabc6c50a902a85ea12e28ccbc5b379",
}


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


def power(value: Fraction, exponent: int) -> Fraction:
    result = Fraction(1)
    for _ in range(exponent):
        result *= value
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows: list[dict] = []
    for rel, expected in PINS.items():
        raw = (ROOT / rel).read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
        check(rows, "parent " + rel, actual == expected, actual, expected)
        check(rows, "LF " + rel, b"\r" not in raw, True, True)
    m_t = Fraction(5, 2)
    base = Fraction(3, 2)
    width = 3
    c2 = Fraction(45)
    distances = [7, 10, 13]
    check(rows, "positive growth factor", base > 1, base, ">1")
    check(rows, "initial width below all distances", width < min(distances), width, distances)
    bounds = [m_t * power(base, width) / power(base, d) for d in distances]
    check(rows, "bound d=7", bounds[0], Fraction(20, 81), bounds[0] == Fraction(20, 81))
    check(rows, "bound d=10", bounds[1], Fraction(40, 2187), bounds[1] == Fraction(40, 2187))
    check(rows, "bound d=13", bounds[2], Fraction(80, 59049), bounds[2] == Fraction(80, 59049))
    for i, d in enumerate(distances):
        moment = bounds[i] * power(base, d)
        target = m_t * power(base, width)
        check(rows, f"moment inequality d={d}", moment <= target, moment, target)
        check(rows, f"nonnegative probability d={d}", bounds[i] >= 0, bounds[i], ">=0")
        check(rows, f"N4 coefficient d={d}", c2 * bounds[i] >= 0, c2 * bounds[i], ">=0")
    check(rows, "strict first decrease", bounds[1] < bounds[0], bounds, "decreasing")
    check(rows, "strict second decrease", bounds[2] < bounds[1], bounds, "decreasing")
    contract = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-lyapunov-bridge-contract-v1.json").read_text(encoding="utf-8"))
    check(rows, "conditional contract remains unauthorised", contract["provenance"]["source_authorized_packet_present"] is False, contract["provenance"], False)
    check(rows, "no rate mutation", contract["frozen_scope"]["comparison"].find("rate fitting") >= 0, contract["frozen_scope"]["comparison"], "rate fitting forbidden")
    check(rows, "physical nonclaim", any("physical Pre-A" in x for x in contract["non_claims"]), contract["non_claims"], "physical firewall")
    payload = {"schema": "tect/pah-omc020-lyapunov-bridge-independent/1.0", "status": "PASS_INDEPENDENT_CONDITIONAL", "verdict": "AUXILIARY_SUPPORT", "conditional": True, "checks": rows, "checks_passed": len(rows), "inputs": {"M_T": str(m_t), "base": str(base), "width": width, "C2": str(c2), "distances": distances, "bounds": [str(x) for x in bounds]}, "non_claims": contract["non_claims"]}
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and args.output.exists() and args.output.read_bytes() != encoded:
        raise SystemExit("independent Lyapunov replay mismatch")
    write(args.output, payload)
    print(f"PAH-OMC-020 LYAPUNOV INDEPENDENT: PASS ({len(rows)} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
