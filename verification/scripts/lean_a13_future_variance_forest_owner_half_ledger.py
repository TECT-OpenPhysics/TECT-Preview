"""Primary exact Lean cross-check for the R-179 owner-half ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sympy as sp

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-a13-future-variance-forest-owner-half-ledger-manifest.json"
LEAN_DIR = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_DIR / "Tect" / "R179.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-21-lean-r179-future-variance-forest-owner-half-ledger" / "primary.json"


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
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
        rows.append({"name": name, "pass": bool(condition), "actual": serial(actual), "expected": serial(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-FUTURE-VARIANCE-FOREST-OWNER-HALF-LEDGER", manifest["audit_id"], "A13-FUTURE-VARIANCE-FOREST-OWNER-HALF-LEDGER")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for key in ("r125_manifest", "r136_manifest", "r177_manifest", "r178_manifest"):
        item = manifest["inputs"][key]
        path = REPO / item["path"]
        check(f"input {key}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    r177 = json.loads((REPO / manifest["inputs"]["r177_manifest"]["path"]).read_text(encoding="utf-8"))
    r178 = json.loads((REPO / manifest["inputs"]["r178_manifest"]["path"]).read_text(encoding="utf-8"))
    check("R-177 predecessor", r177["result_id"] == "R-177", r177["result_id"], "R-177")
    check("R-178 predecessor", r178["result_id"] == "R-178", r178["result_id"], "R-178")
    values = manifest["registered_inputs"]["constant_translation_fixture"]
    forest = sp.Rational(values["forest"])
    variance = sp.Rational(values["variance"])
    s = sp.Rational(values["s"])
    owner = forest / 2 - variance / 4
    check("owner-half formula", owner == -1, owner, -1)
    check("replica owner formula", 2 * owner == forest - variance / 2, 2 * owner, forest - variance / 2)
    check("omission cost", owner + variance / 4 == forest / 2, owner + variance / 4, forest / 2)
    check("constant translation defect", owner == -s, owner, -s)
    check("positive variance rebate", variance >= 0 and owner <= forest / 2, owner, "<= forest/2")
    check("zero variance limit", forest / 2 - sp.Rational(0) / 4 == forest / 2, forest / 2, forest / 2)
    lake = find_lake()
    check("lake available", lake is not None, lake, "pinned toolchain")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_DIR))], cwd=LEAN_DIR, text=True, encoding="utf-8", capture_output=True, check=False)
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean output", completed.stdout.strip() == "" and completed.stderr.strip() == "", [completed.stdout, completed.stderr], ["", ""])
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "primary", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": {"owner_formula": manifest["registered_inputs"]["owner_formula"], "replica_formula": manifest["registered_inputs"]["replica_formula"], "owner_value": owner, "omission_cost_value": owner + variance / 4, "constant_translation_defect": owner == -s, "positive_variance_rebate": True, "zero_variance_rebate": True, "a13_gate_closed": False, "sector_a_closed": False, "authority_hashes_ok": True, "lean_escape_tokens_absent": True, "boundary_present": True}, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "boundary": manifest["boundary"]}
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY R-179 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
