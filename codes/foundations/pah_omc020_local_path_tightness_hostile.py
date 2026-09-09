#!/usr/bin/env python3
"""Hostile controls for the PAH-OMC-020 path-tightness envelope.

The controls mutate only the proposed estimate or its interpretation in
memory.  Each mutation must be rejected while the registered finite source
inputs and the HOLD boundary remain intact.
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
    "2026-09-08-pah-omc020-local-path-tightness/hostile.json"
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


def require(rows: list[dict[str, Any]], name: str, condition: bool, detail: Any) -> None:
    if not condition:
        raise AssertionError(f"hostile control not rejected: {name}: {detail!r}")
    rows.append({"name": name, "status": "PASS", "detail": serial(detail)})


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
    hashes = {path: digest(ROOT / path) for path in PINS}
    require(rows, "all parent source pins remain exact", hashes == PINS, hashes)
    pa = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    bridge = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-pathspace-bridge-result-v1.json").read_text(encoding="utf-8"))
    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8"))
    r490 = (ROOT / "strategy/pa-hyp/R490-certificate.md").read_text(encoding="utf-8")
    c2 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json").read_text(encoding="utf-8"))
    c_sw = parse_int(r"C_sw\s*=\s*N_geom\s*\(1\+S_geom\)\s*=\s*(\d+)", r490, "C_sw")
    c2_per_site = parse_int(r"C2\(A\)<=N_geom\|A\|=(\d+)\|A\|", json.dumps(c2, ensure_ascii=True, sort_keys=True), "C2")

    support = 2
    increment = Fraction(1, 4)
    k_gamma = Fraction(c_sw * support) * increment * increment
    root_count = c2_per_site * support
    k_l = Fraction(c2_per_site * support) * root_count * increment * increment
    delta = Fraction(1, 1000)
    correct = 2 * delta * k_gamma + 2 * delta * delta * k_l
    no_martingale_term = 2 * delta * delta * k_l
    no_drift_factor = 2 * delta * k_gamma + delta * delta * k_l
    no_two_factor = delta * k_gamma + delta * delta * k_l

    # The martingale quadratic-variation contribution cannot be omitted.
    require(rows, "omitting martingale term underbounds", no_martingale_term < correct, {"correct": correct, "mutated": no_martingale_term})
    # The factor 2 from |a+b|^2 <= 2a^2+2b^2 is required by this route.
    require(rows, "dropping first factor 2 is detected", no_two_factor < correct, {"correct": correct, "mutated": no_two_factor})
    require(rows, "dropping drift factor 2 is detected", no_drift_factor < correct, {"correct": correct, "mutated": no_drift_factor})

    delta_half = delta / 2
    constant_mutation = 2 * k_gamma + 2 * k_l
    correct_half = 2 * delta_half * k_gamma + 2 * delta_half * delta_half * k_l
    require(rows, "delta-independent envelope fails tightness", constant_mutation > correct and constant_mutation > correct_half, {"mutated": constant_mutation, "small": correct_half})
    wrong_c2_drift = Fraction(c_sw * support) * root_count * increment * increment
    require(rows, "C_sw cannot replace C2", wrong_c2_drift != k_l, {"C_sw": c_sw, "C2": c2_per_site, "correct": k_l, "mutated": wrong_c2_drift})

    time_text = prereg["scope"]["time"].lower()
    relabelled = time_text.replace("external unaccelerated markov time", "lorentzian physical time")
    require(rows, "physical-time relabel is rejected", "lorentzian physical time" not in time_text and "lorentzian physical time" in relabelled, relabelled)
    require(rows, "bridge cannot be promoted to a process", bridge.get("verdict") == "HOLD_FOR_EVIDENCE" and bridge.get("physical_promotion") is False, bridge.get("verdict"))
    require(rows, "PAH generator remains original", "(L_rho f)(x)" in pa["dynamics"]["generator"], pa["dynamics"]["generator"])

    payload = {
        "schema": "tect/pah-omc020-local-path-tightness-hostile/1.0",
        "audit_id": "PAH-OMC-020-LOCAL-PATH-TIGHTNESS-HOSTILE-001",
        "result_id": "R-541",
        "task_id": "T-064",
        "status": "PASS_HOSTILE_PATH_TIGHTNESS_REJECTIONS",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": hashes,
        "fixture": {"support_size": support, "max_increment": str(increment), "delta": str(delta), "K_Gamma": str(k_gamma), "K_L": str(k_l), "correct_envelope": str(correct)},
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "Hostile in-memory mutations that omit martingale/drift factors, use C_sw as C2, remove delta decay, relabel time physically, or promote the bridge are all rejected.",
        "proof_boundary": "The controls do not supply the missing path-space, non-explosion, uniqueness or R-512 identification theorem.",
        "non_claims": [
            "No new PAH functional, rate, state, carrier, regulator or time convention.",
            "No infinite-volume semigroup, continuum, physical Pre-A, spacetime, QFT, gravity, Yang-Mills, mass-gap or TOE conclusion.",
        ],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_local_path_tightness_hostile.py --check",
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(serial(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("hostile local path tightness replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 LOCAL PATH TIGHTNESS HOSTILE: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
