#!/usr/bin/env python3
"""Hostile controls for the PAH-OMC-020 conditional fixed-n implication."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-fixedn-conditional/hostile.json"
)
WORK = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-work.md"
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"


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


def check(rows: list[dict], name: str, ok: bool, actual: object, expected: object) -> None:
    if not ok:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def run(output: Path) -> dict:
    rows: list[dict] = []
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    work = WORK.read_bytes()
    with tempfile.TemporaryDirectory(prefix="pah020-hostile-") as directory:
        altered_tail = Path(directory) / "tail.md"
        altered_tail.write_bytes(work.replace(b"stationary L1 contraction", b"pointwise envelope", 1))
        check(rows, "tail shortcut is detected", sha256(altered_tail) != sha256(WORK),
              sha256(altered_tail), "different from source")
        altered_order = Path(directory) / "order.json"
        altered_order.write_bytes(PREREG.read_bytes().replace(b"First j", b"First n", 1))
        check(rows, "reversed order mutation is detected", sha256(altered_order) != sha256(PREREG),
              sha256(altered_order), "different from source")
    generator = json.loads(PAH.read_text(encoding="utf-8"))["dynamics"]["generator"]
    check(rows, "full exponent mutation is rejected", "exp[-beta(F_rho(r x)-F_rho(x))/2]" in generator,
          generator, "midpoint exponent present")
    order = prereg["scope"]["regulator_order"]
    check(rows, "source order remains j-before-n", "First j" in order and "then" in order,
          order, "j then anchored n")
    check(rows, "conditional implication is not read as completion", "conditional" in WORK.read_text(encoding="utf-8").lower()
          and "not yet" in WORK.read_text(encoding="utf-8").lower(), "conditional/not yet", "present")
    check(rows, "physical promotion is fenced", "No physical Pre-A" in " ".join(prereg["non_claims"]),
          prereg["non_claims"], "physical non-claims")
    payload = {
        "schema": "tect/pah-omc020-fixedn-conditional-hostile/1.0",
        "status": "PASS_HOSTILE_CONDITIONAL_AUDIT",
        "verdict": "AUXILIARY_SUPPORT",
        "temporal_verdict": "IN_PROGRESS",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "code_sha256": sha256(Path(__file__)),
        "checks": rows,
        "scope": "Shortcut and overclaim rejection for the conditional fixed-n implication only.",
        "non_claims": [
            "No negative result for PAH-OMC-020; the controls only reject invalid proof shortcuts.",
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
        with tempfile.TemporaryDirectory(prefix="pah020-hostile-replay-") as directory:
            payload = run(Path(directory) / "replay.json")
        actual = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
        if expected != actual:
            raise SystemExit("PAH-OMC-020 hostile conditional replay mismatch")
    else:
        run(args.output)
    print("PAH-OMC-020 FIXED-N HOSTILE: PASS (conditional audit; temporal proof IN_PROGRESS)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
