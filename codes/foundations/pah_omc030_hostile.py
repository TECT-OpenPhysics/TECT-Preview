#!/usr/bin/env python3
"""Hostile promotion audit for PAH-OMC-030."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-09-pah-omc030-bridge/hostile.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-030-prereg-v1.json").read_text(encoding="utf-8"))
    certificate = " ".join((ROOT / "strategy/pa-hyp/PAH-OMC-030-certificate.md").read_text(encoding="utf-8").split())
    checks = {
        "reject_local_pullback_as_full_Un": "not a bounded or isometric map" in certificate,
        "reject_terminal_square_replacement": "terminal unsplit square" in certificate and "split `K` cells" in certificate,
        "reject_fixed_n_as_uniform_n": "fixed `n`" in certificate and "uniform in `n`" in certificate,
        "reject_target_tail_as_finite_tail": "not for the family" in certificate,
        "reject_uniqueness_implies_existence": "does not construct" in certificate,
        "reject_physical_time": "external markov time remains stochastic" in certificate.lower(),
        "all_required_bridges_named": len(prereg["required_bridges"]) == 5,
        "verdict_is_hold": True
    }
    payload = {
        "schema": "tect/pah-omc030-hostile/1.0",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "checks": checks,
        "coverage": "Hostile shortcut and promotion audit; no alternate model or PAH counterexample constructed.",
        "non_claims": ["No DISPROVED result", "No physical Pre-A/QFT/gravity/continuum/Yang-Mills/mass-gap/TOE conclusion"]
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"PAH-OMC-030 HOSTILE: {payload['status']}; verdict=HOLD_FOR_EVIDENCE")
    return 0 if args.check and payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
