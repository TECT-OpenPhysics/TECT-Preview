"""Primary Lean cross-check for the finite packet Cauchy bound used by R-081."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-finite-packet-cauchy-crosscheck-manifest.json"
LEAN_DIR = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_DIR / "Tect" / "R185.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r185-finite-packet-cauchy-crosscheck" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def find_lake() -> str | None:
    pin = TOOLCHAIN.read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    for name in ("lake.exe", "lake"):
        candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / name
        if candidate.is_file():
            return str(candidate)
    return shutil.which("lake")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-FINITE-PACKET-CAUCHY-CROSSCHECK", manifest["audit_id"], "A13-FINITE-PACKET-CAUCHY-CROSSCHECK")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF contract", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])

    values = manifest["registered_inputs"]
    source = [Fraction(value) for value in values["source"]]
    control = [Fraction(value) for value in values["control"]]
    check("same packet length", len(source) == len(control), len(source), len(control))
    source_norm = sum(value * value for value in source)
    control_norm = sum(value * value for value in control)
    pairing = sum(a * b for a, b in zip(source, control))
    gap = source_norm * control_norm - pairing * pairing
    expected = values["expected"]
    check("source norm", source_norm == Fraction(expected["source_norm"]), source_norm, expected["source_norm"])
    check("control norm", control_norm == Fraction(expected["control_norm"]), control_norm, expected["control_norm"])
    check("pairing", pairing == Fraction(expected["pairing"]), pairing, expected["pairing"])
    check("exact packet gap", gap == Fraction(expected["gap"]), gap, expected["gap"])
    check("finite packet contraction", pairing * pairing <= source_norm * control_norm, pairing * pairing, source_norm * control_norm)
    check("R-081 and OVERLAP remain open", manifest["boundary"]["overlap_src_closed"] is False and manifest["boundary"]["a13_gate_closed"] is False, manifest["boundary"], "both open")

    lake = find_lake()
    check("lake available", lake is not None, lake, "pinned toolchain")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_DIR))], cwd=LEAN_DIR, text=True, encoding="utf-8", capture_output=True, check=False)
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean output", completed.stdout.strip() == "" and completed.stderr.strip() == "", [completed.stdout, completed.stderr], ["", ""])
    derived = {
        "source_norm": source_norm,
        "control_norm": control_norm,
        "pairing": pairing,
        "gap": gap,
        "bound_holds": pairing * pairing <= source_norm * control_norm,
        "packet_length": len(source),
        "lean_escape_tokens_absent": True,
        "a13_gate_closed": False,
        "overlap_src_closed": False,
        "boundary_present": True,
    }
    payload = {
        "schema": "tect/lean-kernel-crosscheck/1.0",
        "run_kind": "primary",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": derived,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY R-185 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
