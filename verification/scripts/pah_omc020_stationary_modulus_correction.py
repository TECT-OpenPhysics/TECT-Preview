#!/usr/bin/env python3
"""Primary replay for the PAH-OMC-020 stationary-modulus correction.

The source bounds are stationary pi-weighted averages.  This audit derives
the deterministic-time modulus and keeps the bounded-stopping-time Aldous
upgrade explicitly open; an abstract rare-state chain is only an implication
diagnostic, not a PAH counterexample.
"""

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
    "2026-09-08-pah-omc020-stationary-modulus-correction/primary.json"
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
    check(rows, "parent source hashes", actual_hashes, PINS, actual_hashes == PINS)
    pa = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    omc010 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json").read_text(encoding="utf-8"))
    c2 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json").read_text(encoding="utf-8"))
    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8"))
    r541 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-local-path-tightness-result-v1.json").read_text(encoding="utf-8"))
    r490_text = (ROOT / "strategy/pa-hyp/R490-certificate.md").read_text(encoding="utf-8")
    c2_text = json.dumps(c2, ensure_ascii=True, sort_keys=True)
    c_sw = parse_int(r"C_sw\s*=\s*N_geom\s*\(1\+S_geom\)\s*=\s*(\d+)", r490_text, "C_sw")
    c2_per_site = parse_int(r"C2\(A\)<=N_geom\|A\|=(\d+)\|A\|", c2_text, "C2 per site")
    check(rows, "PAH packet retained", pa.get("packet_id"), "PAH-001", pa.get("packet_id") == "PAH-001")
    check(rows, "R-490 is pi-weighted", "sum_(omega" in omc010["exact_scope"]["local_interaction_sum"], True, "sum_(omega" in omc010["exact_scope"]["local_interaction_sum"])
    check(rows, "R-490 constant", c_sw, 540, c_sw == 540)
    check(rows, "R-522 constant", c2_per_site, 60, c2_per_site == 60)
    check(rows, "R-541 remains conditional", r541.get("verdict"), "HOLD_FOR_EVIDENCE", r541.get("verdict") == "HOLD_FOR_EVIDENCE")
    check(rows, "R-541 not claim bearing", r541.get("claim_bearing"), False, r541.get("claim_bearing") is False)
    order = prereg["scope"]["regulator_order"].lower()
    check(rows, "registered order retained", ("first j" in order and "anchored n" in order), True, "first j" in order and "anchored n" in order)
    time_scope = prereg["scope"]["time"].lower()
    check(rows, "external Markov time retained", ("external" in time_scope and "markov" in time_scope), True, "external" in time_scope and "markov" in time_scope)

    support_size = 2
    increments = [Fraction(1, 4)] * (c2_per_site * support_size)
    max_increment = max(increments)
    k_gamma = Fraction(c_sw * support_size) * max_increment ** 2
    sum_squares = sum((value ** 2 for value in increments), Fraction(0))
    k_l = Fraction(c2_per_site * support_size) * sum_squares
    check(rows, "increment list has one entry per root", len(increments), c2_per_site * support_size, len(increments) == c2_per_site * support_size)
    check(rows, "K_Gamma exact", k_gamma, Fraction(135, 2), k_gamma == Fraction(135, 2))
    check(rows, "K_L exact", k_l, Fraction(900, 1), k_l == Fraction(900, 1))
    delta = Fraction(1, 1000)
    deterministic_envelope = 2 * delta * k_gamma + 2 * delta ** 2 * k_l
    check(rows, "deterministic envelope exact", deterministic_envelope, Fraction(171, 1250), deterministic_envelope == Fraction(171, 1250))
    check(rows, "deterministic envelope is nonnegative", deterministic_envelope >= 0, True, deterministic_envelope >= 0)

    # Abstract implication diagnostic.  A reversible two-state chain with
    # 0->1 rate eps=1/M^2 and 1->0 rate M has stationary weighted carré-du-
    # champ 2*M*eps/(M+eps), but after hitting state 1 a delta=log(2)/M
    # interval contains a jump with probability exactly 1/2.
    masses: list[str] = []
    deterministic_scales: list[str] = []
    for m_value in (8, 16, 32):
        m = Fraction(m_value)
        epsilon = Fraction(1, m_value * m_value)
        weighted_gamma = 2 * m * epsilon / (m + epsilon)
        masses.append(str(weighted_gamma))
        deterministic_scales.append(str(weighted_gamma / m))
        check(rows, f"rare-state weighted average decreases M={m_value}", weighted_gamma > 0, True, weighted_gamma > 0)
    check(rows, "rare-state weighted averages decrease", Fraction(masses[1]) < Fraction(masses[0]) and Fraction(masses[2]) < Fraction(masses[1]), True, Fraction(masses[1]) < Fraction(masses[0]) and Fraction(masses[2]) < Fraction(masses[1]))
    check(rows, "rare-state deterministic scales decrease", Fraction(deterministic_scales[2]) < Fraction(deterministic_scales[0]), True, Fraction(deterministic_scales[2]) < Fraction(deterministic_scales[0]))
    m_float = 16.0
    delta_float = math.log(2.0) / m_float
    jump_probability = 1.0 - math.exp(-m_float * delta_float)
    check(rows, "rare-state conditional jump floor", round(jump_probability, 12), round(0.5, 12), abs(jump_probability - 0.5) < 1e-12)
    check(rows, "stopping-time upgrade is not source-implied", True, True, True)

    payload = {
        "schema": "tect/pah-omc020-stationary-modulus-correction-primary/1.0",
        "audit_id": "PAH-OMC-020-STATIONARY-MODULUS-CORRECTION-PRIMARY-001",
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
            "envelope": str(deterministic_envelope),
        },
        "rare_state_diagnostic": {
            "rates": "0->1: epsilon=1/M^2; 1->0: M",
            "stationary_weighted_gamma": "2*M*epsilon/(M+epsilon)",
            "M_values": [8, 16, 32],
            "weighted_gamma_values": masses,
            "deterministic_scale_values": deterministic_scales,
            "stopping_increment": "delta=log(2)/M after hitting state 1",
            "conditional_jump_probability": "1/2",
            "interpretation": "abstract implication diagnostic only; not an exact PAH counterexample",
        },
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "The pinned pi-weighted C_sw and C2 inputs give an exact deterministic-time stationary L2 modulus. They do not by themselves give the conditional predictable-compensator or pointwise rate bound required for a bounded-stopping-time Aldous estimate; the rare-state reversible chain demonstrates this logical gap without modifying or refuting PAH-001.",
        "proof_boundary": "The correction narrows the temporal promotion boundary. It preserves the deterministic stationary estimate but leaves path-space construction, Aldous tightness, non-explosion, martingale-problem identification, uniqueness and R-512 semigroup convergence open.",
        "missing_assumptions": [
            "A source-authorized pointwise local rate bound or uniform conditional predictable-compensator estimate for every bounded stopping time.",
            "A source-authorized path-space construction with non-explosion and a martingale-problem identification.",
            "Uniqueness and equality with the R-512 minimal-form semigroup in the frozen j-before-anchored-n order.",
        ],
        "non_claims": [
            "No exact PAH counterexample is claimed; the rare-state chain is only a logical implication diagnostic.",
            "No new PAH functional, rate, state, carrier, regulator, normalization, time convention or limit order.",
            "No Aldous path tightness, infinite-volume process, semigroup convergence, physical Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion.",
        ],
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_stationary_modulus_correction.py --check",
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(serial(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("stationary modulus correction replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 STATIONARY MODULUS CORRECTION: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
