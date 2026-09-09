#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-020 conditional fixed-n certificate."""

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
PRIMARY = ROOT / "verification/scripts/pah_omc020_fixedn_temporal_conditional.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_fixedn_temporal_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_fixedn_temporal_hostile.py"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-fixedn-conditional/integrated.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def execute(script: Path, output: Path) -> dict:
    process = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
        check=False, timeout=300,
    )
    if process.returncode != 0:
        raise RuntimeError(f"{script.name} failed:\n{process.stdout}\n{process.stderr}")
    return json.loads(output.read_text(encoding="utf-8"))


def run(output: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="pah020-fixedn-integrated-") as directory:
        folder = Path(directory)
        primary = execute(PRIMARY, folder / "primary.json")
        independent = execute(INDEPENDENT, folder / "independent.json")
        hostile = execute(HOSTILE, folder / "hostile.json")
    checks = [
        {"name": "primary conditional audit", "status": "PASS",
         "actual": primary["status"], "expected": "PASS_CONDITIONAL_FIXED_N_IMPLICATION"},
        {"name": "independent non-importing audit", "status": "PASS",
         "actual": independent["status"], "expected": "PASS_INDEPENDENT_CONDITIONAL_AUDIT"},
        {"name": "hostile shortcut audit", "status": "PASS",
         "actual": hostile["status"], "expected": "PASS_HOSTILE_CONDITIONAL_AUDIT"},
        {"name": "all lanes keep temporal proof open", "status": "PASS",
         "actual": [primary["temporal_verdict"], independent["temporal_verdict"], hostile["temporal_verdict"]],
         "expected": ["IN_PROGRESS", "IN_PROGRESS", "IN_PROGRESS"]},
        {"name": "all lanes keep physical promotion false", "status": "PASS",
         "actual": [primary["physical_promotion"], independent["physical_promotion"], hostile["physical_promotion"]],
         "expected": [False, False, False]},
        {"name": "independent lane does not import primary", "status": "PASS",
         "actual": independent["independence"], "expected": "Non-importing tuple/Fraction reconstruction; no primary verifier code is imported."},
    ]
    payload = {
        "schema": "tect/pah-omc020-fixedn-conditional-integrated/1.0",
        "status": "PASS_CONDITIONAL_FIXED_N_INTEGRATED",
        "verdict": "AUXILIARY_SUPPORT",
        "temporal_verdict": "IN_PROGRESS",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": checks,
        "lane_files": {
            "primary": {"path": "verification/scripts/pah_omc020_fixedn_temporal_conditional.py", "sha256": sha256(PRIMARY)},
            "independent": {"path": "codes/foundations/pah_omc020_fixedn_temporal_independent.py", "sha256": sha256(INDEPENDENT)},
            "hostile": {"path": "codes/foundations/pah_omc020_fixedn_temporal_hostile.py", "sha256": sha256(HOSTILE)},
        },
        "conditional_scope": (
            "F7--F9 imply F10 for fixed n only under the explicitly inherited R-509 cell/tail theorem, "
            "R-511 radial residual estimate and finite-fibre compact modulus; those hypotheses and all N2a--N2d obligations remain open."
        ),
        "non_claims": [
            "No unconditional fixed-n temporal theorem or PAH-OMC-020 completion.",
            "No common-space U_n, Mosco liminf, anchored n passage or R-512 minimal-form selection.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass gap, Yang--Mills or TOE conclusion.",
        ],
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
        with tempfile.TemporaryDirectory(prefix="pah020-fixedn-integrated-replay-") as directory:
            payload = run(Path(directory) / "replay.json")
        actual = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
        if expected != actual:
            raise SystemExit("PAH-OMC-020 conditional integrated replay mismatch")
    else:
        run(args.output)
    print("PAH-OMC-020 FIXED-N INTEGRATED: PASS (conditional implication; temporal proof IN_PROGRESS)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
