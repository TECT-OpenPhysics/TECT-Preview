"""Primary Lean/Fraction audit for the bounded T-058 cylinder trial."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-t058-bounded-complete-production-cylinder-manifest.json"
LEAN_ROOT = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_ROOT / "Tect" / "R192.lean"
TOOLCHAIN = LEAN_ROOT / "lean-toolchain"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r192-t058-bounded-complete-production-cylinder" / "primary.json"


def normalised_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(normalised_bytes(path)).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, F):
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


def pinned_lean() -> Path | None:
    encoded = TOOLCHAIN.read_text(encoding="utf-8").strip().replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / ("lean.exe" if os.name == "nt" else "lean")
    return candidate if candidate.is_file() else None


def compile_lean() -> subprocess.CompletedProcess[str]:
    lean = pinned_lean()
    if lean is None:
        return subprocess.CompletedProcess([], 1, "", "pinned lean executable missing")
    search = [LEAN_ROOT / ".lake" / "build" / "lib" / "lean"]
    packages = LEAN_ROOT / ".lake" / "packages"
    if packages.is_dir():
        search.extend(p / ".lake" / "build" / "lib" / "lean" for p in packages.iterdir() if (p / ".lake" / "build" / "lib" / "lean").is_dir())
    env = os.environ.copy()
    env["LEAN_PATH"] = os.pathsep.join(str(path) for path in search if path.is_dir())
    return subprocess.run([str(lean), "Tect/R192.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False, env=env)


def finite_fixtures(manifest: dict[str, Any]) -> dict[str, Any]:
    ri = manifest["registered_inputs"]
    reserve = ri["reserve_fixture"]
    a = F(reserve["cross_scale"])
    threshold_d = F(reserve["threshold_diagonal"])
    below_d = F(reserve["below_diagonal"])

    def qform(d: F, x: F, y: F) -> F:
        p = d - a
        return x * (p * x + a * y) + y * (a * x + p * y)

    temporal = ri["temporal_fixture"]
    s1, s2 = F(temporal["s1"]), F(temporal["s2"])
    h1, h2 = F(temporal["h1"]), F(temporal["h2"])
    pairing = s1 * h1 + s2 * h2
    wedge = s1 * h2 - s2 * h1
    total = (s1**2 + s2**2) * (h1**2 + h2**2)
    return {
        "reserve_threshold_value": qform(threshold_d, F(1), F(-1)),
        "reserve_below_value": qform(below_d, F(1), F(-1)),
        "temporal_pairing": pairing,
        "temporal_wedge": wedge,
        "temporal_total": total,
        "temporal_gap": total - pairing**2,
        "douglas_identity": pairing**2 + wedge**2 == total,
    }


def derive(manifest: dict[str, Any]) -> dict[str, Any]:
    slots = manifest["registered_inputs"]["slot_audit"]
    first = next((row["slot"] for row in slots if not row["mapped"]), None)
    fixtures = finite_fixtures(manifest)
    return {
        "slot_order": [row["slot"] for row in slots],
        "mapped_slots": [row["slot"] for row in slots if row["mapped"]],
        "complete_owner": all(row["mapped"] for row in slots),
        "first_missing_slot": first,
        "trial_verdict": "PASS_COMPLETE_OWNER" if first is None else "FAIL_FIRST_MISSING_PRODUCTION_MAP",
        "reserve_threshold_value": fixtures["reserve_threshold_value"],
        "reserve_below_value": fixtures["reserve_below_value"],
        "temporal_pairing": fixtures["temporal_pairing"],
        "temporal_wedge": fixtures["temporal_wedge"],
        "temporal_total": fixtures["temporal_total"],
        "temporal_gap": fixtures["temporal_gap"],
        "douglas_identity": fixtures["douglas_identity"],
        "a13_gate_closed": False,
        "sector_a_closed": False,
    }


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

    check("identity", manifest["audit_id"] == "A13-T058-BOUNDED-COMPLETE-PRODUCTION-CYLINDER" and manifest["result_id"] == "R-192", [manifest["audit_id"], manifest["result_id"]], "R-192 identity")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negative", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    check("eight owner slots", len(manifest["registered_inputs"]["slot_audit"]) == 8, len(manifest["registered_inputs"]["slot_audit"]), 8)
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key} hash", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    for key, item in manifest["files"].items():
        path = REPO / item["path"]
        check(f"file {key} hash", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    for key, item in manifest["inputs"].items():
        if key.endswith("_run"):
            data = json.loads((REPO / item["path"]).read_text(encoding="utf-8"))
            check(f"{key} PASS", data.get("verdict") == "PASS", data.get("verdict"), "PASS")
    lean_source = LEAN_ENTRYPOINT.read_text(encoding="utf-8")
    check("Lean markers", all(marker in lean_source for marker in manifest["theorem_markers"]), manifest["theorem_markers"], "all present")
    check("Lean escape absence", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    completed = compile_lean()
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean", completed.returncode == 0 and "error:" not in (completed.stdout + completed.stderr).lower(), completed.stderr, "no Lean error")
    derived = derive(manifest)
    oracle = manifest["test_oracles"]
    check("first missing slot", derived["first_missing_slot"] == oracle["first_failure_slot"], derived["first_missing_slot"], oracle["first_failure_slot"])
    check("trial failure", derived["trial_verdict"] == oracle["audit_verdict"], derived["trial_verdict"], oracle["audit_verdict"])
    check("reserve threshold", derived["reserve_threshold_value"] == F(oracle["reserve_threshold_value"]), derived["reserve_threshold_value"], oracle["reserve_threshold_value"])
    check("reserve below threshold", derived["reserve_below_value"] == F(oracle["reserve_below_value"]), derived["reserve_below_value"], oracle["reserve_below_value"])
    check("Douglas identity", derived["douglas_identity"] and derived["temporal_gap"] == F(oracle["douglas_gap"]), derived, {"identity": True, "gap": oracle["douglas_gap"]})
    check("owner incomplete", not derived["complete_owner"], derived["complete_owner"], False)
    check("A13 boundary", not derived["a13_gate_closed"] and not derived["sector_a_closed"], derived, "gates remain open")
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "primary", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": derived, "toolchain": TOOLCHAIN.read_text(encoding="utf-8").strip(), "lean_stdout": completed.stdout, "lean_stderr": completed.stderr, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "boundary": manifest["boundary"]}
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY R-192 LEAN PASS {len(rows)}/{len(rows)} trial={derived['trial_verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
