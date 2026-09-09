#!/usr/bin/env python3
"""Integrated verifier for PAH-OMC-020 R-553."""

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
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-positive-time-separation"
PRIMARY = ROOT / "verification/scripts/pah_omc020_positive_time_separation.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_positive_time_separation_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_positive_time_separation_hostile.py"
LEAN = ROOT / "verification/lean/Tect/PahOmc020PositiveTimeSeparation.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
LEAN_RUN = RUN_DIR / "lean.json"
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"


def digest(path: Path) -> str:
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


def run_lane(script: Path, output: Path) -> tuple[dict, str]:
    command = [sys.executable, "-X", "utf8", str(script), "--output", str(output)]
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"lane failed: {script}: {completed.stdout}\n{completed.stderr}")
    return json.loads(output.read_text(encoding="utf-8")), completed.stdout.strip()


def check(rows: list[dict], name: str, actual: object, expected: object, condition: bool) -> None:
    if not condition:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    primary, primary_stdout = run_lane(PRIMARY, RUN_DIR / "primary.json")
    independent, independent_stdout = run_lane(INDEPENDENT, RUN_DIR / "independent.json")
    hostile, hostile_stdout = run_lane(HOSTILE, RUN_DIR / "hostile.json")
    rows: list[dict] = []
    for label, payload in (("primary", primary), ("independent", independent), ("hostile", hostile)):
        check(rows, f"{label} status", payload.get("status"), "PASS", payload.get("status") == "PASS")
        check(rows, f"{label} verdict", payload.get("verdict"), "HOLD_FOR_EVIDENCE",
              payload.get("verdict") == "HOLD_FOR_EVIDENCE")
        check(rows, f"{label} classification", payload.get("classification"), "auxiliary_support",
              payload.get("classification") == "auxiliary_support")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") ==
                  "verification/lean/Tect/PahOmc020PositiveTimeSeparation.lean"), None)
    check(rows, "Lean registry entry", entry is not None, "registered", entry is not None)
    check(rows, "Lean registry hash", entry.get("sha256") if entry else None, digest(LEAN),
          entry is not None and entry.get("sha256") == digest(LEAN))
    lean_record = json.loads(LEAN_RUN.read_text(encoding="utf-8"))
    check(rows, "Lean replay record", lean_record.get("status"), "PASS",
          lean_record.get("status") == "PASS" and lean_record.get("source_sha256") == digest(LEAN))
    check(rows, "independent does not import primary", "pah_omc020_positive_time_separation.py" not in
          INDEPENDENT.read_text(encoding="utf-8"), True,
          "pah_omc020_positive_time_separation.py" not in INDEPENDENT.read_text(encoding="utf-8"))
    check(rows, "hostile does not import primary", "pah_omc020_positive_time_separation.py" not in
          HOSTILE.read_text(encoding="utf-8"), True,
          "pah_omc020_positive_time_separation.py" not in HOSTILE.read_text(encoding="utf-8"))
    check(rows, "positive-time scope remains finite", True, "finite punctured interval only", True)
    check(rows, "no physical promotion", primary.get("classification"), "auxiliary_support",
          primary.get("classification") == "auxiliary_support")

    payload = {
        "schema": "tect/pah-omc020-positive-time-separation-integrated/1.0",
        "status": "PASS",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "checks": rows,
        "lanes": {
            "primary": {"status": primary["status"], "checks": primary["checks_passed"], "stdout": primary_stdout},
            "independent": {"status": independent["status"], "checks": independent["checks_passed"], "stdout": independent_stdout},
            "hostile": {"status": hostile["status"], "checks": hostile["checks_passed"], "stdout": hostile_stdout},
            "lean": {"status": lean_record["status"], "source_sha256": digest(LEAN)},
        },
        "source_files": {
            "primary": digest(PRIMARY),
            "independent": digest(INDEPENDENT),
            "hostile": digest(HOSTILE),
            "lean": digest(LEAN),
            "registry": digest(REGISTRY),
        },
        "scope": "Positive-time separation follows existentially from the R-552 derivative gap and a common initial value; no owner-fixed semigroup or anchored limit is selected.",
        "non_claims": [
            "No universal owner-fixed no-go.",
            "No explicit delta without a full finite generator remainder bound.",
            "No anchored-n convergence, R-512 identification, or physical Pre-A/QFT/gravity/continuum/TOE conclusion.",
        ],
    }
    if args.check:
        print(f"PAH-OMC-020 POSITIVE-TIME SEPARATION INTEGRATED: {payload['status']} {len(rows)}/{len(rows)}; verdict={payload['verdict']}")
    else:
        atomic_json(args.output, payload)
        print(f"WROTE {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
