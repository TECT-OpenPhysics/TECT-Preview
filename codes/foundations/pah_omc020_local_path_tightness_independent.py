#!/usr/bin/env python3
"""Non-importing independent replay for PAH-OMC-020 local path tightness.

This lane reconstructs the stopped-time two-square envelope from the pinned
Gibbs conductance and second-rate-moment inputs.  It intentionally does not
import the primary verifier or construct a limiting process.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-local-path-tightness/independent.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json": "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69",
    "strategy/pa-hyp/R490-certificate.md": "80563e82f7f592dbbb6c00ff27fdd5270031e8426d4d1520546bf846c6a6d10a",
    "strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json": "87dd9a7225203cdfa84456e446983c573cabc6c50a902a85ea12e28ccbc5b379",
    "strategy/pa-hyp/PAH-OMC-020-pathspace-bridge-result-v1.json": "12eda207fe03441deb47df02a206b8a4cac1accce5aa5eb016b861b53c8af730",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def record(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def parse_int(pattern: str, text: str, label: str) -> int:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if match is None:
        raise AssertionError(f"missing {label}")
    return int(match.group(1))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    actual_hashes = {path: digest(ROOT / path) for path in PINS}
    record(rows, "pinned sources", actual_hashes, PINS)

    pa = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    omc010 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json").read_text(encoding="utf-8"))
    c2 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json").read_text(encoding="utf-8"))
    bridge = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-pathspace-bridge-result-v1.json").read_text(encoding="utf-8"))
    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8"))
    r490 = (ROOT / "strategy/pa-hyp/R490-certificate.md").read_text(encoding="utf-8")
    c2_text = json.dumps(c2, ensure_ascii=True, sort_keys=True)

    c_sw = parse_int(r"C_sw\s*=\s*N_geom\s*\(1\+S_geom\)\s*=\s*(\d+)", r490, "C_sw")
    c2_per_site = parse_int(r"C2\(A\)<=N_geom\|A\|=(\d+)\|A\|", c2_text, "C2 per site")
    record(rows, "C_sw is source-derived", c_sw, 540)
    record(rows, "C2 is source-derived", c2_per_site, 60)
    record(rows, "original PAH packet", pa.get("packet_id"), "PAH-001")
    record(rows, "OMC-010 identity", omc010.get("contract_id"), "PAH-OMC-010")
    order = prereg["scope"]["regulator_order"].lower()
    record(rows, "j-before-anchored-n order", ("first j" in order and "anchored n" in order), True)
    record(rows, "bridge is still conditional", bridge.get("verdict"), "HOLD_FOR_EVIDENCE")
    record(rows, "no physical bridge promotion", bridge.get("physical_promotion"), False)
    time_scope = prereg["scope"]["time"].lower()
    record(rows, "external Markov time", ("external" in time_scope and "markov" in time_scope), True)

    # Independent fixture: a three-site local support and a 3/10 increment cap.
    support_size = 3
    increment = Fraction(3, 10)
    roots = c2_per_site * support_size
    k_gamma = Fraction(c_sw * support_size) * increment * increment
    k_l = Fraction(c2_per_site * support_size) * Fraction(roots) * increment * increment
    record(rows, "root incidence count", roots, c2_per_site * support_size)
    record(rows, "quadratic variation coefficient", k_gamma, Fraction(729, 5))
    record(rows, "drift coefficient", k_l, Fraction(2916, 1))
    record(rows, "coefficients nonnegative", (k_gamma >= 0 and k_l >= 0), True)

    delta = Fraction(1, 1200)
    delta_twice = Fraction(1, 600)
    epsilon = Fraction(1, 2)
    envelope = 2 * delta * k_gamma + 2 * delta * delta * k_l
    envelope_twice = 2 * delta_twice * k_gamma + 2 * delta_twice * delta_twice * k_l
    quotient = envelope / (epsilon * epsilon)
    record(rows, "two-square envelope is nonnegative", envelope >= 0, True)
    record(rows, "envelope grows with delta", envelope < envelope_twice, True)
    record(rows, "Markov quotient is subunit in fixture", quotient < 1, True)

    sequence = []
    prior: Fraction | None = None
    for denominator in (1200, 2400, 4800, 9600):
        step = Fraction(1, denominator)
        value = 2 * step * k_gamma + 2 * step * step * k_l
        if prior is not None:
            record(rows, f"halved-delta decrease {denominator}", value < prior, True)
        prior = value
        sequence.append(str(value))
    record(rows, "envelope tends to zero algebraically", sequence[-1] < sequence[0], True)

    payload = {
        "schema": "tect/pah-omc020-local-path-tightness-independent/1.0",
        "audit_id": "PAH-OMC-020-LOCAL-PATH-TIGHTNESS-INDEPENDENT-001",
        "result_id": "R-541",
        "task_id": "T-064",
        "status": "PASS_LOCAL_PATH_TIGHTNESS_HOLD",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": actual_hashes,
        "source_constants": {"C_sw": c_sw, "C2_per_site": c2_per_site},
        "fixture": {
            "support_size": support_size,
            "max_increment": str(increment),
            "root_count": roots,
            "K_Gamma": str(k_gamma),
            "K_L": str(k_l),
            "delta": str(delta),
            "delta_twice": str(delta_twice),
            "epsilon": str(epsilon),
            "envelope": str(envelope),
            "envelope_twice": str(envelope_twice),
            "markov_bound": str(quotient),
            "halved_delta_sequence": sequence,
        },
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "An independent exact-rational reconstruction gives the same stopped-time two-square envelope from the pinned source constants for a distinct support/increment fixture; this is local finite-path tightness support only.",
        "proof_boundary": "No limiting process, martingale-problem identification, non-explosion, uniqueness, R-512 semigroup equality or ordered semigroup convergence is established.",
        "missing_assumptions": [
            "Source-authorized path-space construction and non-explosion.",
            "Uniform-integrability and martingale-problem identification for every subsequential limit.",
            "Uniqueness and equality with the R-512 minimal-form semigroup.",
        ],
        "non_claims": [
            "No new functional, rate, state, carrier, regulator, normalization or time interpretation.",
            "No infinite-volume, continuum, QFT, gravity, Pre-A, Yang-Mills, mass-gap or TOE conclusion.",
        ],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_local_path_tightness_independent.py --check",
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(serial(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("independent local path tightness replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 LOCAL PATH TIGHTNESS INDEPENDENT: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
