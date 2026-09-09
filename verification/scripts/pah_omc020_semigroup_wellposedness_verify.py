#!/usr/bin/env python3
"""Integrated verifier for PAH-OMC-020 R-552."""

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
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-semigroup-wellposedness"
PRIMARY = ROOT / "verification/scripts/pah_omc020_semigroup_wellposedness.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_semigroup_wellposedness_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_semigroup_wellposedness_hostile.py"
LEAN = ROOT / "verification/lean/Tect/PahOmc020SemigroupWellposedness.lean"
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
    cmd = [sys.executable, "-X", "utf8", str(script), "--output", str(output)]
    completed = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"lane failed: {script}: {completed.stdout}\n{completed.stderr}")
    return json.loads(output.read_text(encoding="utf-8")), completed.stdout.strip()


def check(rows: list[dict], name: str, condition: bool, actual: object, expected: object) -> None:
    if not condition:
        raise AssertionError(name)
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
        check(rows, f"{label} status", payload.get("status") == "PASS", payload.get("status"), "PASS")
        check(rows, f"{label} verdict", payload.get("verdict") == "HOLD_FOR_EVIDENCE",
              payload.get("verdict"), "HOLD_FOR_EVIDENCE")
        check(rows, f"{label} no physical promotion", payload.get("classification") == "auxiliary_support",
              payload.get("classification"), "auxiliary_support")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((item for item in registry["entrypoints"] if item["path"] ==
                  "verification/lean/Tect/PahOmc020SemigroupWellposedness.lean"), None)
    check(rows, "Lean registry entry", entry is not None, entry, "registered")
    check(rows, "Lean registry hash", entry and entry["sha256"] == digest(LEAN),
          entry["sha256"] if entry else "missing", digest(LEAN))
    lean_record = json.loads(LEAN_RUN.read_text(encoding="utf-8"))
    check(rows, "Lean replay record", lean_record.get("status") == "PASS" and
          lean_record.get("source_sha256") == digest(LEAN), lean_record.get("status"), "PASS/hash-pinned")
    check(rows, "independent does not import primary", "pah_omc020_semigroup_wellposedness.py" not in
          INDEPENDENT.read_text(encoding="utf-8"), True, "no primary import")
    check(rows, "hostile does not import primary", "pah_omc020_semigroup_wellposedness.py" not in
          HOSTILE.read_text(encoding="utf-8"), True, "no primary import")

    payload = {
        "schema": "tect/pah-omc020-semigroup-wellposedness-integrated/1.0",
        "status": "PASS",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "checks": rows,
        "lanes": {
            "primary": {"status": primary["status"], "checks": len(primary["checks"]), "stdout": primary_stdout},
            "independent": {"status": independent["status"], "checks": len(independent["checks"]), "stdout": independent_stdout},
            "hostile": {"status": hostile["status"], "checks": len(hostile["checks"]), "stdout": hostile_stdout},
            "lean": {"status": lean_record["status"], "source_sha256": digest(LEAN)},
        },
        "source_files": {
            "primary": digest(PRIMARY),
            "independent": digest(INDEPENDENT),
            "hostile": digest(HOSTILE),
            "lean": digest(LEAN),
            "registry": digest(REGISTRY),
        },
        "scope": "The current PAH source admits two finite root-multiplicity completions with different t=0 semigroup derivatives; this is a definition-level HOLD_FOR_EVIDENCE boundary, not a universal convergence no-go.",
        "non_claims": [
            "No source-authorized owner convention is selected.",
            "No anchored-n semigroup convergence or R-512 minimal-form identification is proved or refuted for an owner-fixed completion.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang--Mills or TOE conclusion follows.",
        ],
    }
    if args.check:
        print(f"PAH-OMC-020 SEMIGROUP WELL-POSEDNESS INTEGRATED: {payload['status']} {len(rows)}/{len(rows)}; verdict={payload['verdict']}")
    else:
        atomic_json(args.output, payload)
        print(f"WROTE {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
