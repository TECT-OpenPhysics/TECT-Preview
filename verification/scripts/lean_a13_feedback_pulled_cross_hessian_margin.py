"""Primary exact Lean cross-check for the R-182 pulled cross-Hessian margin."""

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
MANIFEST = REPO / "strategy" / "pre-a13-feedback-pulled-cross-hessian-margin-manifest.json"
LEAN_DIR = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_DIR / "Tect" / "R182.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-21-lean-r182-feedback-pulled-cross-hessian-margin" / "primary.json"


def sha256(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return [[serial(cell) for cell in row] for row in value.tolist()]
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

    check("manifest identity", manifest["audit_id"] == "A13-FEEDBACK-PULLED-CROSS-HESSIAN-MARGIN", manifest["audit_id"], "A13-FEEDBACK-PULLED-CROSS-HESSIAN-MARGIN")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])

    r178 = json.loads((REPO / manifest["inputs"]["r178_manifest"]["path"]).read_text(encoding="utf-8"))
    r181 = json.loads((REPO / manifest["inputs"]["r181_manifest"]["path"]).read_text(encoding="utf-8"))
    status = json.loads((REPO / manifest["inputs"]["a13_status"]["path"]).read_text(encoding="utf-8"))
    registered = manifest["registered_inputs"]
    coefficients = {key: sp.Rational(str(value)) for key, value in r178["registered_inputs"]["cross_coefficients"].items()}
    active = {key: sp.Rational(str(value)) for key, value in registered["active_phase"].items()}
    feedback_gain = sp.Rational(r181["registered_inputs"]["feedback_gain"])
    weights = [sp.Rational(str(active[key])) for key in ("w1", "w2")]
    check("R-178 coefficients", coefficients == {"field": sp.Rational(2), "current": sp.Rational(3), "ordered": sp.Rational(5)}, coefficients, {"field": 2, "current": 3, "ordered": 5})
    check("R-178 active weights", weights == [sp.Rational(1), sp.Rational(2)], weights, [1, 2])
    check("R-181 feedback gain", feedback_gain == sp.Rational(1, 2), feedback_gain, sp.Rational(1, 2))
    check("A13 remains open", status["proof_complete"] is False and status["lifecycle"] == "ACTIVE", [status["proof_complete"], status["lifecycle"]], [False, "ACTIVE"])

    hessian_coefficient = -(coefficients["field"] + coefficients["current"] * active["w1"] * active["w2"])
    feedback = sp.Matrix([[1, 0], [feedback_gain, 1]])
    cross_hessian = sp.Matrix([[hessian_coefficient, -hessian_coefficient], [-hessian_coefficient, hessian_coefficient]])
    pulled_hessian = sp.simplify(feedback.T * cross_hessian * feedback)
    expected_cross = sp.Matrix([[-8, 8], [8, -8]])
    expected_pulled = sp.Matrix([[-2, 4], [4, -8]])
    check("active cross Hessian coefficient", hessian_coefficient == -8, hessian_coefficient, -8)
    check("cross Hessian", cross_hessian == expected_cross, cross_hessian, expected_cross)
    check("feedback pullback", pulled_hessian == expected_pulled, pulled_hessian, expected_pulled)
    x, y = sp.symbols("x y", real=True)
    cross_quadratic = sp.factor((sp.Matrix([[x, y]]) * cross_hessian * sp.Matrix([x, y]))[0])
    pulled_quadratic = sp.factor((sp.Matrix([[x, y]]) * pulled_hessian * sp.Matrix([x, y]))[0])
    check("cross quadratic factor", cross_quadratic == -8 * (x - y) ** 2, cross_quadratic, -8 * (x - y) ** 2)
    check("pulled quadratic factor", pulled_quadratic == -2 * (x - 2 * y) ** 2, pulled_quadratic, -2 * (x - 2 * y) ** 2)
    fixture = registered["fixture"]
    fx = sp.Rational(fixture["x"])
    fy = sp.Rational(fixture["y"])
    cross_fixture = sp.factor(cross_quadratic.subs({x: fx, y: fy}))
    pulled_fixture = sp.factor(pulled_quadratic.subs({x: fx, y: fy}))
    check("cross negative fixture", cross_fixture == sp.Rational(fixture["cross_defect"]), cross_fixture, fixture["cross_defect"])
    check("pulled negative fixture", pulled_fixture == sp.Rational(fixture["pulled_defect"]), pulled_fixture, fixture["pulled_defect"])
    eigenvalues = pulled_hessian.eigenvals()
    check("pulled eigenvalues", eigenvalues == {sp.Rational(-10): 1, sp.Rational(0): 1}, eigenvalues, {-10: 1, 0: 1})

    lake = find_lake()
    check("lake available", lake is not None, lake, "pinned toolchain")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_DIR))], cwd=LEAN_DIR, text=True, encoding="utf-8", capture_output=True, check=False)
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean output", completed.stdout.strip() == "" and completed.stderr.strip() == "", [completed.stdout, completed.stderr], ["", ""])
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
            "cross_coefficients": {key: coefficients[key] for key in ("field", "current", "ordered")},
            "active_weights": active,
            "feedback_gain": feedback_gain,
            "hessian_coefficient": hessian_coefficient,
            "cross_hessian": cross_hessian,
            "pulled_hessian": pulled_hessian,
            "cross_quadratic": cross_quadratic,
            "pulled_quadratic": pulled_quadratic,
            "cross_fixture": cross_fixture,
            "pulled_fixture": pulled_fixture,
            "pulled_eigenvalues": eigenvalues,
            "a13_gate_closed": False,
            "sector_a_closed": False,
            "authority_hashes_ok": True,
            "lean_escape_tokens_absent": True,
            "boundary_present": True,
        },
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY R-182 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
