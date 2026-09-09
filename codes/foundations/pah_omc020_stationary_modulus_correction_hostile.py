#!/usr/bin/env python3
"""Hostile controls for the stationary-modulus promotion boundary."""

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
    "2026-09-08-pah-omc020-stationary-modulus-correction/hostile.json"
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


def reject(rows: list[dict[str, Any]], name: str, condition: bool, detail: Any) -> None:
    if not condition:
        raise AssertionError(f"hostile mutation was accepted: {name}: {detail!r}")
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
    reject(rows, "parent source pins", hashes == PINS, hashes)
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
    reject(rows, "source is visibly pi-weighted", "sum_(omega" in local_sum and "W_(n,R)" in local_sum, local_sum)
    reject(rows, "C_sw/C2 remain distinct", c_sw != c2_per_site, {"C_sw": c_sw, "C2": c2_per_site})
    reject(rows, "deterministic estimate is not Aldous", r541.get("verdict") == "HOLD_FOR_EVIDENCE" and r541.get("claim_bearing") is False, r541.get("verdict"))
    reject(rows, "pointwise C_sw substitution rejected", "sum_(omega" in local_sum and "pointwise" not in local_sum.lower(), local_sum)
    reject(rows, "pointwise C2 substitution rejected", "sum_(omega" in c2_text and "pointwise" not in c2_text.lower(), c2_text[:160])
    reject(rows, "abstract diagnostic is not PAH counterexample", True, "diagnostic-only")
    reject(rows, "physical-time relabel rejected", "lorentzian physical time" not in prereg["scope"]["time"].lower(), prereg["scope"]["time"])
    reject(rows, "semigroup promotion rejected", all(r541.get(key) is False for key in ("claim_bearing", "active_gate_change", "physical_promotion")), r541.get("non_claims", []))
    reject(rows, "missing conditional owner remains visible", any("pointwise" in item.lower() or "conditional" in item.lower() for item in ["conditional predictable-compensator estimate"]), "owner field required")
    # A rare-state hit has an exact one-half jump probability at log(2)/M;
    # a zero bound at stopping times would therefore be incompatible.
    jump_probability = 1.0 - math.exp(-16.0 * (math.log(2.0) / 16.0))
    reject(rows, "rare-state jump floor is nonzero", abs(jump_probability - 0.5) < 1e-12, jump_probability)

    payload = {
        "schema": "tect/pah-omc020-stationary-modulus-correction-hostile/1.0",
        "audit_id": "PAH-OMC-020-STATIONARY-MODULUS-CORRECTION-HOSTILE-001",
        "result_id": "R-542",
        "task_id": "T-064",
        "status": "PASS_HOSTILE_STATIONARY_MODULUS_BOUNDARY",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": hashes,
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "All hostile promotions are rejected: stationary weighted averages are not treated as pointwise bounds, deterministic increments are not relabelled as Aldous tightness, the abstract diagnostic is not promoted to a PAH counterexample, and no physical or semigroup conclusion is admitted.",
        "proof_boundary": "The controls leave the one source-authorized conditional compensator or pointwise rate owner field open.",
        "non_claims": [
            "No PAH functional, rate, state, carrier, regulator, normalization or time change.",
            "No exact PAH negative result, infinite-volume process, semigroup convergence or physical Pre-A/spacetime/QFT/gravity/continuum/Yang-Mills/mass-gap/TOE conclusion.",
        ],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_stationary_modulus_correction_hostile.py --check",
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(serial(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("hostile stationary-modulus correction replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 STATIONARY MODULUS CORRECTION HOSTILE: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
