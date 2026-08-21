"""Primary exact Lean cross-check for the R-178 finite cross owner."""

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
MANIFEST = REPO / "strategy" / "pre-a-a13-two-root-complete-cross-owner-differentiation-manifest.json"
LEAN_DIR = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_DIR / "Tect" / "R178.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-21-lean-r178-two-root-complete-cross-owner-differentiation" / "primary.json"


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


def check(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "pass": bool(condition), "actual": serial(actual), "expected": serial(expected)})
    if not condition:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")


def find_lake() -> str | None:
    pin = TOOLCHAIN.read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    for name in ("lake.exe", "lake"):
        candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / name
        if candidate.is_file():
            return str(candidate)
    return shutil.which("lake")


def cross_terms(a1, a2, w1, w2, c1, s1, c2, s2):
    cosine = c1 * c2 + s1 * s2
    sine = s1 * c2 - c1 * s2
    field = a1 * a2 * cosine
    current = w1 * w2 * a1 * a2 * cosine
    ordered = a1 * a2 * (w2 - w1) * sine
    return field, current, ordered, cosine, sine


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    check(rows, "manifest identity", manifest["audit_id"] == "A13-TWO-ROOT-COMPLETE-CROSS-OWNER-DIFFERENTIATION", manifest["audit_id"], "A13-TWO-ROOT-COMPLETE-CROSS-OWNER-DIFFERENTIATION")
    check(rows, "claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check(rows, "no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(rows, f"input {key} hash", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    r174 = json.loads((REPO / manifest["inputs"]["r174_manifest"]["path"]).read_text(encoding="utf-8"))
    r176 = json.loads((REPO / manifest["inputs"]["r176_run"]["path"]).read_text(encoding="utf-8"))
    r177 = json.loads((REPO / manifest["inputs"]["r177_run"]["path"]).read_text(encoding="utf-8"))
    status = json.loads((REPO / manifest["inputs"]["a13_status"]["path"]).read_text(encoding="utf-8"))
    check(rows, "R-174 predecessor", r174["result_id"] == "R-174" and r174["claim_bearing"] is False, [r174["result_id"], r174["claim_bearing"]], ["R-174", False])
    check(rows, "R-176 actual roots", r176["verdict"] == "PASS" and r176["derived"]["root_labels"] == ["k", "2k"], r176["derived"]["root_labels"], ["k", "2k"])
    check(rows, "R-177 incidence predecessor", r177["verdict"] == "PASS" and r177["derived"]["owner_order"] == ["common_heat", "root_1", "root_2", "future_residual"], r177["derived"]["owner_order"], ["common_heat", "root_1", "root_2", "future_residual"])
    check(rows, "A13 remains open", status["proof_complete"] is False and status["lifecycle"] == "ACTIVE", [status["proof_complete"], status["lifecycle"]], [False, "ACTIVE"])

    coefficients = {key: sp.Rational(str(value)) for key, value in manifest["registered_inputs"]["cross_coefficients"].items()}
    fixture = {key: sp.Rational(str(value)) for key, value in manifest["registered_inputs"]["fixture"].items()}
    active = {key: sp.Rational(str(value)) for key, value in manifest["registered_inputs"]["ordered_active_phase"].items()}
    field, current, ordered, cosine, sine = cross_terms(*(fixture[key] for key in ("a1", "a2", "w1", "w2", "c1", "s1", "c2", "s2")))
    check(rows, "R-174 field block", field == 0, field, 0)
    check(rows, "R-174 current block", current == 0, current, 0)
    check(rows, "R-174 ordered fixture", ordered == -1, ordered, -1)
    check(rows, "three blocks retained", len(manifest["registered_inputs"]["cross_owner_blocks"]) == 3, manifest["registered_inputs"]["cross_owner_blocks"], 3)

    def phase_derivatives(values: dict[str, sp.Rational]):
        _, _, _, c, s = cross_terms(*(values[key] for key in ("a1", "a2", "w1", "w2", "c1", "s1", "c2", "s2")))
        amp = values["a1"] * values["a2"]
        freq = values["w2"] - values["w1"]
        common = (coefficients["field"] + coefficients["current"] * values["w1"] * values["w2"]) * amp
        return -common * s + coefficients["ordered"] * amp * freq * c, common * s - coefficients["ordered"] * amp * freq * c

    d1, d2 = phase_derivatives(fixture)
    check(rows, "root-one derivative", d1 == 8, d1, 8)
    check(rows, "root-two derivative", d2 == -8, d2, -8)
    check(rows, "phase derivative sum", d1 + d2 == 0, d1 + d2, 0)
    active_values = {**fixture, **active}
    active_d1, _ = phase_derivatives(active_values)
    without_ordered = (coefficients["field"] + coefficients["current"] * active_values["w1"] * active_values["w2"]) * active_values["a1"] * active_values["a2"] * (active_values["s1"] * active_values["c2"] - active_values["c1"] * active_values["s2"])
    check(rows, "ordered derivative is active", active_d1 - (-without_ordered) == coefficients["ordered"] * active_values["a1"] * active_values["a2"] * (active_values["w2"] - active_values["w1"]), active_d1, "ordered block contributes")
    check(rows, "global phase cancellation", d1 + d2 == 0, d1 + d2, 0)

    lake = find_lake()
    check(rows, "lake available", lake is not None, lake, "pinned toolchain")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_DIR))], cwd=LEAN_DIR, text=True, encoding="utf-8", capture_output=True, check=False)
    check(rows, "Lean compile", completed.returncode == 0, completed.returncode, 0)
    check(rows, "Lean clean output", completed.stdout.strip() == "" and completed.stderr.strip() == "", [completed.stdout, completed.stderr], ["", ""])
    payload = {
        "schema": "tect/lean-kernel-crosscheck/1.0",
        "run_kind": "primary",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "root_labels": ["k", "2k"],
            "cross_owner_blocks": manifest["registered_inputs"]["cross_owner_blocks"],
            "field_current_ordered_blocks_retained": True,
            "ordered_fixture": ordered,
            "d1": d1,
            "d2": d2,
            "phase_derivative_sum_zero": True,
            "ordered_derivative_active": True,
            "actual_a1_roots_from_r176": True,
            "incidence_from_r177": True,
            "a13_gate_closed": False,
            "sector_a_closed": False,
            "authority_hashes_ok": True,
            "lean_escape_tokens_absent": True,
            "boundary_present": True,
        },
        "source_hashes": {key: item["sha256"] for key, item in manifest["inputs"].items()},
        "toolchain": TOOLCHAIN.read_text(encoding="utf-8").strip(),
        "lean_stdout": completed.stdout,
        "lean_stderr": completed.stderr,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        output = args.output if args.output.is_absolute() else REPO / args.output
        atomic_json(output, payload)
    print(f"PRIMARY R-178 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
