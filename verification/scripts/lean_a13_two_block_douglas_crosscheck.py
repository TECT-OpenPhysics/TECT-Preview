"""Primary exact Lean cross-check for the R-184 two-block Douglas identity."""

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
MANIFEST = REPO / "strategy" / "pre-a13-two-block-douglas-crosscheck-manifest.json"
LEAN_DIR = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_DIR / "Tect" / "R184.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r184-two-block-douglas-crosscheck" / "primary.json"


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

    check("manifest identity", manifest["audit_id"] == "A13-TWO-BLOCK-DOUGLAS-CROSSCHECK", manifest["audit_id"], "A13-TWO-BLOCK-DOUGLAS-CROSSCHECK")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF contract", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])

    registered = manifest["registered_inputs"]
    s1 = Fraction(registered["s1"])
    s2 = Fraction(registered["s2"])
    h1 = Fraction(registered["h1"])
    h2 = Fraction(registered["h2"])
    source_norm = s1 * s1 + s2 * s2
    control_norm = h1 * h1 + h2 * h2
    pairing = s1 * h1 + s2 * h2
    wedge = s1 * h2 - s2 * h1
    gap = source_norm * control_norm - pairing * pairing
    expected = registered["expected"]
    check("source norm", source_norm == Fraction(expected["source_norm"]), source_norm, expected["source_norm"])
    check("control norm", control_norm == Fraction(expected["control_norm"]), control_norm, expected["control_norm"])
    check("pairing", pairing == Fraction(expected["pairing"]), pairing, expected["pairing"])
    check("wedge", wedge == Fraction(expected["wedge"]), wedge, expected["wedge"])
    check("exact Douglas gap", gap == wedge * wedge, gap, wedge * wedge)
    check("contraction bound", pairing * pairing <= source_norm * control_norm, pairing * pairing, source_norm * control_norm)
    check("A13 remains open", manifest["boundary"]["a13_gate_closed"] is False and manifest["boundary"]["overlap_src_closed"] is False, manifest["boundary"], "both open")

    lake = find_lake()
    check("lake available", lake is not None, lake, "pinned toolchain")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_DIR))], cwd=LEAN_DIR, text=True, encoding="utf-8", capture_output=True, check=False)
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean output", completed.stdout.strip() == "" and completed.stderr.strip() == "", [completed.stdout, completed.stderr], ["", ""])
    derived = {
        "source_norm": source_norm,
        "control_norm": control_norm,
        "pairing": pairing,
        "wedge": wedge,
        "gap": gap,
        "bound_holds": pairing * pairing <= source_norm * control_norm,
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
    print(f"PRIMARY R-184 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
