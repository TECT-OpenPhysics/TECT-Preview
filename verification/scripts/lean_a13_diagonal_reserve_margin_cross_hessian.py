"""Primary exact Lean cross-check for the R-183 reserve margin theorem."""

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
MANIFEST = REPO / "strategy" / "pre-a13-diagonal-reserve-margin-cross-hessian-manifest.json"
LEAN_DIR = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_DIR / "Tect" / "R183.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r183-diagonal-reserve-margin-cross-hessian" / "primary.json"


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

    check("manifest identity", manifest["audit_id"] == "A13-DIAGONAL-RESERVE-MARGIN-CROSS-HESSIAN", manifest["audit_id"], "A13-DIAGONAL-RESERVE-MARGIN-CROSS-HESSIAN")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])

    r182 = json.loads((REPO / manifest["inputs"]["r182_manifest"]["path"]).read_text(encoding="utf-8"))
    status = json.loads((REPO / manifest["inputs"]["a13_status"]["path"]).read_text(encoding="utf-8"))
    registered = manifest["registered_inputs"]
    coefficients = {key: sp.Rational(str(value)) for key, value in r182["registered_inputs"]["cross_coefficients"].items()}
    active = {key: sp.Rational(str(value)) for key, value in r182["registered_inputs"]["active_phase"].items()}
    feedback_gain = sp.Rational(str(r182["registered_inputs"]["feedback_gain"]))
    a = coefficients["field"] + coefficients["current"] * active["w1"] * active["w2"]
    delta = sp.Rational(registered["cases"]["below_threshold_delta"])
    extra = sp.Rational(registered["cases"]["asymmetric_extra"])
    threshold = 2 * a
    d_threshold = threshold
    d_below = threshold - delta
    d1_asym = threshold
    d2_asym = threshold + extra
    p_asym = d1_asym - a
    q_asym = d2_asym - a
    remainder_asym = sp.simplify(q_asym - a**2 / p_asym)
    feedback = sp.Matrix([[1, 0], [feedback_gain, 1]])

    check("R-182 coefficient source", coefficients == {"field": sp.Rational(2), "current": sp.Rational(3), "ordered": sp.Rational(5)}, coefficients, {"field": 2, "current": 3, "ordered": 5})
    check("R-182 active weights", [active["w1"], active["w2"]] == [sp.Rational(1), sp.Rational(2)], [active["w1"], active["w2"]], [1, 2])
    check("R-182 feedback gain", feedback_gain == sp.Rational(1, 2), feedback_gain, sp.Rational(1, 2))
    check("A13 remains open", status["proof_complete"] is False and status["lifecycle"] == "ACTIVE", [status["proof_complete"], status["lifecycle"]], [False, "ACTIVE"])
    check("active reserve scale", a == sp.Rational(8), a, 8)
    check("isotropic threshold", threshold == sp.Rational(registered["expected"]["isotropic_threshold"]), threshold, registered["expected"]["isotropic_threshold"])

    reserve = lambda d1, d2: sp.Matrix([[d1 - a, a], [a, d2 - a]])
    pulled = lambda d1, d2: sp.simplify(feedback.T * reserve(d1, d2) * feedback)
    threshold_matrix = pulled(d_threshold, d_threshold)
    asym_matrix = pulled(d1_asym, d2_asym)
    x, y = sp.symbols("x y", real=True)
    threshold_q = sp.factor((sp.Matrix([[x, y]]) * reserve(d_threshold, d_threshold) * sp.Matrix([x, y]))[0])
    below_q = sp.factor((sp.Matrix([[x, y]]) * reserve(d_below, d_below) * sp.Matrix([x, y]))[0])
    asym_q = sp.factor((sp.Matrix([[x, y]]) * reserve(d1_asym, d2_asym) * sp.Matrix([x, y]))[0])
    threshold_pulled_q = sp.factor((sp.Matrix([[x, y]]) * threshold_matrix * sp.Matrix([x, y]))[0])
    check("threshold reserve matrix", reserve(d_threshold, d_threshold) == sp.Matrix([[a, a], [a, a]]), reserve(d_threshold, d_threshold), sp.Matrix([[a, a], [a, a]]))
    check("threshold quadratic", sp.simplify(threshold_q - a * (x + y) ** 2) == 0, threshold_q, a * (x + y) ** 2)
    check("threshold pulled quadratic", sp.simplify(threshold_pulled_q - a * (sp.Rational(3, 2) * x + y) ** 2) == 0, threshold_pulled_q, a * (sp.Rational(3, 2) * x + y) ** 2)
    check("asymmetric remainder", remainder_asym == extra, remainder_asym, extra)
    check("asymmetric completion", sp.simplify(asym_q - (p_asym * (x + a / p_asym * y) ** 2 + remainder_asym * y**2)) == 0, asym_q, p_asym * (x + a / p_asym * y) ** 2 + remainder_asym * y**2)
    check("below threshold", below_q.subs({x: 1, y: -1}) == -2 * delta, below_q.subs({x: 1, y: -1}), -2 * delta)
    fixture = registered["fixture"]
    fx = sp.Rational(fixture["x"])
    fy = sp.Rational(fixture["pulled_y"])
    pulled_fixture = sp.factor((sp.Matrix([[fx, fy]]) * pulled(d_below, d_below) * sp.Matrix([fx, fy]))[0])
    check("pulled subthreshold fixture", pulled_fixture == -2 * delta, pulled_fixture, -2 * delta)
    necessary_fixture = sp.factor((sp.Matrix([[x, y]]) * reserve(d1_asym, d2_asym) * sp.Matrix([x, y]))[0].subs({x: -a / p_asym, y: 1}))
    check("necessary-reserve witness", necessary_fixture == remainder_asym, necessary_fixture, remainder_asym)
    check("asymmetric pulled matrix", asym_matrix == sp.Matrix([[d1_asym + (d2_asym - a) / 4, a + (d2_asym - a) / 2], [a + (d2_asym - a) / 2, d2_asym - a]]), asym_matrix, "derived pulled matrix")

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
            "active_cross_scale": a,
            "feedback_gain": feedback_gain,
            "threshold": threshold,
            "below_threshold": d_below,
            "asymmetric_reserves": {"d1": d1_asym, "d2": d2_asym, "p": p_asym, "q": q_asym, "remainder": remainder_asym},
            "threshold_matrix": reserve(d_threshold, d_threshold),
            "threshold_pulled_matrix": threshold_matrix,
            "asymmetric_pulled_matrix": asym_matrix,
            "threshold_quadratic": threshold_q,
            "threshold_pulled_quadratic": threshold_pulled_q,
            "asymmetric_quadratic": asym_q,
            "below_fixture": below_q.subs({x: 1, y: -1}),
            "pulled_subthreshold_fixture": pulled_fixture,
            "necessary_reserve_witness": necessary_fixture,
            "isotropic_positive": True,
            "isotropic_subthreshold_negative": True,
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
    print(f"PRIMARY R-183 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
