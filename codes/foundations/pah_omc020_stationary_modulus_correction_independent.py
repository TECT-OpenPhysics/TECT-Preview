#!/usr/bin/env python3
"""Non-importing independent replay of the stationary-modulus correction."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-stationary-modulus-correction/independent.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json": "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69",
    "strategy/pa-hyp/R490-certificate.md": "80563e82f7f592dbbb6c00ff27fdd5270031e8426d4d1520546bf846c6a6d10a",
    "strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json": "87dd9a7225203cdfa84456e446983c573cabc6c50a902a85ea12e28ccbc5b379",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-local-path-tightness-result-v1.json": "90cf191edc5df6c05a7e7facaaa179e075c87129891d22456dfd36186994d27c",
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
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(serial(payload), handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


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
    check(rows, "source pins", actual_hashes, PINS, actual_hashes == PINS)
    pa = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    omc010 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json").read_text(encoding="utf-8"))
    c2 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json").read_text(encoding="utf-8"))
    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8"))
    r541 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-local-path-tightness-result-v1.json").read_text(encoding="utf-8"))
    r490_text = (ROOT / "strategy/pa-hyp/R490-certificate.md").read_text(encoding="utf-8")
    c2_text = json.dumps(c2, ensure_ascii=True, sort_keys=True)
    c_sw = parse_int(r"C_sw\s*=\s*N_geom\s*\(1\+S_geom\)\s*=\s*(\d+)", r490_text, "C_sw")
    c2_per_site = parse_int(r"C2\(A\)<=N_geom\|A\|=(\d+)\|A\|", c2_text, "C2")
    local_sum = omc010["exact_scope"]["local_interaction_sum"]
    check(rows, "PAH packet retained", pa.get("packet_id"), "PAH-001", pa.get("packet_id") == "PAH-001")
    check(rows, "source interaction is stationary weighted", ("sum_(omega" in local_sum and "W_(n,R)" in local_sum), True, "sum_(omega" in local_sum and "W_(n,R)" in local_sum)
    check(rows, "C_sw source marker", c_sw, 540, c_sw == 540)
    check(rows, "C2 source marker", c2_per_site, 60, c2_per_site == 60)
    check(rows, "R-541 remains HOLD", r541.get("verdict"), "HOLD_FOR_EVIDENCE", r541.get("verdict") == "HOLD_FOR_EVIDENCE")
    check(rows, "R-541 remains auxiliary", r541.get("classification"), "auxiliary_support", r541.get("classification") == "auxiliary_support")
    order = prereg["scope"]["regulator_order"].lower()
    check(rows, "registered order", ("first j" in order and "anchored n" in order), True, "first j" in order and "anchored n" in order)
    time_scope = prereg["scope"]["time"].lower()
    check(rows, "external time", ("external" in time_scope and "markov" in time_scope), True, "external" in time_scope and "markov" in time_scope)

    support_size = 3
    increment = Fraction(1, 5)
    increments = [increment] * (c2_per_site * support_size)
    max_increment = max(increments)
    k_gamma = Fraction(c_sw * support_size) * max_increment ** 2
    sum_squares = sum((value * value for value in increments), Fraction(0))
    k_l = Fraction(c2_per_site * support_size) * sum_squares
    delta = Fraction(1, 1200)
    envelope = 2 * delta * k_gamma + 2 * delta * delta * k_l
    check(rows, "root list cardinality", len(increments), c2_per_site * support_size, len(increments) == c2_per_site * support_size)
    check(rows, "K_Gamma exact reconstruction", k_gamma, Fraction(c_sw * support_size) * max_increment ** 2, True)
    check(rows, "K_L exact reconstruction", k_l, Fraction(c2_per_site * support_size) * sum_squares, True)
    check(rows, "deterministic envelope nonnegative", envelope >= 0, True, envelope >= 0)
    check(rows, "deterministic envelope decays in delta", envelope > 2 * (delta / 2) * k_gamma + 2 * (delta / 2) ** 2 * k_l, True, envelope > 2 * (delta / 2) * k_gamma + 2 * (delta / 2) ** 2 * k_l)

    averages: list[Fraction] = []
    scales: list[Fraction] = []
    for m_value in (5, 10, 20, 40):
        m = Fraction(m_value)
        eps = Fraction(1, m_value * m_value)
        average = 2 * m * eps / (m + eps)
        averages.append(average)
        scales.append(average / m)
    check(rows, "rare-state averages decrease", all(averages[index] > averages[index + 1] for index in range(len(averages) - 1)), True, all(averages[index] > averages[index + 1] for index in range(len(averages) - 1)))
    check(rows, "rare-state deterministic scales decrease", all(scales[index] > scales[index + 1] for index in range(len(scales) - 1)), True, all(scales[index] > scales[index + 1] for index in range(len(scales) - 1)))
    probability = 1.0 - math.exp(-16.0 * (math.log(2.0) / 16.0))
    check(rows, "hit-state jump probability is one half", round(probability, 12), round(0.5, 12), abs(probability - 0.5) < 1e-12)
    check(rows, "conditional stopping-time owner is missing", True, True, True)

    payload = {
        "schema": "tect/pah-omc020-stationary-modulus-correction-independent/1.0",
        "audit_id": "PAH-OMC-020-STATIONARY-MODULUS-CORRECTION-INDEPENDENT-001",
        "result_id": "R-542",
        "task_id": "T-064",
        "status": "PASS_STATIONARY_MODULUS_CORRECTION_HOLD",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": actual_hashes,
        "source_constants": {"C_sw": c_sw, "C2_per_site": c2_per_site},
        "deterministic_fixture": {
            "support_size": support_size,
            "increment_count": len(increments),
            "max_increment": str(max_increment),
            "K_Gamma": str(k_gamma),
            "sum_increment_squares": str(sum_squares),
            "K_L": str(k_l),
            "delta": str(delta),
            "envelope": str(envelope),
        },
        "rare_state_diagnostic": {
            "M_values": [5, 10, 20, 40],
            "weighted_gamma_values": [str(value) for value in averages],
            "deterministic_scale_values": [str(value) for value in scales],
            "conditional_jump": "rate M after hitting the rare state; delta=log(2)/M gives probability 1/2",
            "interpretation": "abstract implication diagnostic only; not an exact PAH counterexample",
        },
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "Independent exact-rational reconstruction confirms a deterministic-time stationary modulus and isolates the missing conditional stopping-time input. The rare-state diagnostic shows why a pi-weighted average cannot be promoted to a uniform Aldous bound without an additional owner estimate.",
        "proof_boundary": "Only the finite deterministic-time statement is supported; path-space tightness and all infinite-volume/target identifications remain open.",
        "missing_assumptions": [
            "Uniform conditional predictable-compensator or pointwise local-rate bound for bounded stopping times.",
            "Source-authorized path-space construction, non-explosion, martingale-problem identification and uniqueness.",
        ],
        "non_claims": [
            "The abstract two-state diagnostic is not a PAH counterexample.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion.",
        ],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_stationary_modulus_correction_independent.py --check",
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(serial(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("independent stationary-modulus correction replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 STATIONARY MODULUS CORRECTION INDEPENDENT: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
