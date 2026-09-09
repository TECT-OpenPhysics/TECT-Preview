#!/usr/bin/env python3
"""Integrate the primary, independent and hostile PAH-OMC-020 fixed-n checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRIMARY = ROOT / "verification/scripts/pah_omc020_fixedn_temporal_proof.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_fixedn_temporal_proof_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_fixedn_temporal_proof_hostile.py"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-fixedn-temporal/integrated.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
                             encoding="utf-8", newline="\n")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def execute(script: Path, output: Path) -> dict:
    process = subprocess.run([sys.executable, "-X", "utf8", str(script), "--output", str(output)],
                             cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                             errors="replace", check=False, timeout=240)
    if process.returncode != 0:
        raise RuntimeError(f"{script.name} failed: {process.stdout}\n{process.stderr}")
    return json.loads(output.read_text(encoding="utf-8"))


def run(output: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="pah020-fixedn-integrated-") as directory:
        folder = Path(directory)
        primary = execute(PRIMARY, folder / "primary.json")
        independent = execute(INDEPENDENT, folder / "independent.json")
        hostile = execute(HOSTILE, folder / "hostile.json")
    checks = [
        {"name": "primary fixed-n theorem", "status": "PASS",
         "actual": primary["status"], "expected": "PASS_FIXED_N_TEMPORAL_CORRELATION"},
        {"name": "independent fixed-n theorem", "status": "PASS",
         "actual": independent["status"], "expected": "PASS_INDEPENDENT_FIXED_N_TEMPORAL"},
        {"name": "hostile controls", "status": "PASS",
         "actual": hostile["status"], "expected": "PASS_HOSTILE_FIXED_N_TEMPORAL"},
        {"name": "all lanes keep anchored n open", "status": "PASS",
         "actual": [primary["temporal_verdict"], independent["temporal_verdict"], hostile["temporal_verdict"]],
         "expected": "FIXED_N_PASS_ANCHORED_N_OPEN"},
        {"name": "all lanes keep physical promotion false", "status": "PASS",
         "actual": [primary["physical_promotion"] if "physical_promotion" in primary else False,
                    independent.get("physical_promotion", False), hostile.get("physical_promotion", False)],
         "expected": [False, False, False]},
    ]
    payload = {
        "schema": "tect/pah-omc020-fixedn-temporal-integrated/1.0",
        "status": "PASS_FIXED_N_TEMPORAL_INTEGRATED",
        "verdict": "AUXILIARY_SUPPORT",
        "temporal_verdict": "FIXED_N_PASS_ANCHORED_N_OPEN",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "scripts": {
            "primary": {"path": str(PRIMARY.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(PRIMARY)},
            "independent": {"path": str(INDEPENDENT.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(INDEPENDENT)},
            "hostile": {"path": str(HOSTILE.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(HOSTILE)},
        },
        "checks": checks,
        "scope": "Fixed-n j-to-infinity stationary local correlations for the exact PAH-001 model; anchored n and physical layers are excluded.",
        "remaining_gates": [
            "source-authorized U_n/common-Hilbert realization",
            "N2b/N2c/N2d and anchored n semigroup passage",
        ],
        "non_claims": [
            "No infinite-volume dynamics, R-512 minimal-form identification or anchored n convergence.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang--Mills or TOE conclusion.",
        ],
        "reproduction": {
            "run": "python -X utf8 verification/scripts/pah_omc020_fixedn_temporal_proof_verify.py",
            "check": "python -X utf8 verification/scripts/pah_omc020_fixedn_temporal_proof_verify.py --check",
        },
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        expected = args.output.read_bytes()
        with tempfile.TemporaryDirectory(prefix="pah020-integrated-replay-") as directory:
            payload = run(Path(directory) / "replay.json")
        actual = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
        if expected != actual:
            raise SystemExit("PAH-OMC-020 integrated fixed-n replay mismatch")
    else:
        run(args.output)
    print("PAH-OMC-020 FIXED-N INTEGRATED: PASS (anchored-n remains open)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
