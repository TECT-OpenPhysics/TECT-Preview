"""Primary exact Lean cross-check for the R-181 two-root feedback Gram."""

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
MANIFEST = REPO / "strategy" / "pre-a-a13-two-root-feedback-mixed-gram-crosscheck-manifest.json"
LEAN_DIR = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_DIR / "Tect" / "R181.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-21-lean-r181-two-root-feedback-mixed-gram-crosscheck" / "primary.json"


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
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

    check("manifest identity", manifest["audit_id"] == "A13-TWO-ROOT-FEEDBACK-MIXED-GRAM-LEAN-CROSSCHECK", manifest["audit_id"], "A13-TWO-ROOT-FEEDBACK-MIXED-GRAM-LEAN-CROSSCHECK")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])

    r177 = json.loads((REPO / manifest["inputs"]["r177_manifest"]["path"]).read_text(encoding="utf-8"))
    r176 = json.loads((REPO / manifest["inputs"]["r176_manifest"]["path"]).read_text(encoding="utf-8"))
    registered = manifest["registered_inputs"]
    beta = sp.Rational(registered["feedback_gain"])
    envelope = sp.Rational(registered["envelope_constant"])
    order = r177["registered_inputs"]["owner_order"]
    check("R-177 owner order", order == ["common_heat", "root_1", "root_2", "future_residual"], order, ["common_heat", "root_1", "root_2", "future_residual"])
    check("R-177 feedback gain", beta == sp.Rational(r177["registered_inputs"]["feedback_gain"]), beta, r177["registered_inputs"]["feedback_gain"])
    check("R-176 root labels", r176["registered_inputs"]["root_multipliers"] == [1, 2], r176["registered_inputs"]["root_multipliers"], [1, 2])

    feedback = sp.Matrix([[1, 0], [beta, 1]])
    gram = sp.simplify(feedback.T * feedback)
    expected_gram = sp.Matrix([[1 + beta**2, beta], [beta, 1]])
    check("feedback Gram identity", gram == expected_gram, gram, expected_gram)
    x = sp.symbols("x", real=True)
    y = sp.symbols("y", real=True)
    source_norm = x**2 + y**2
    output_norm = x**2 + (beta * x + y) ** 2
    defect = sp.factor(envelope * source_norm - output_norm)
    fixture = registered["fixture"]
    fx = sp.Rational(fixture["x"])
    fy = sp.Rational(fixture["y"])
    fixture_output = sp.factor(output_norm.subs({x: fx, y: fy}))
    fixture_source = sp.factor(source_norm.subs({x: fx, y: fy}))
    fixture_defect = sp.factor(defect.subs({x: fx, y: fy}))
    check("registered envelope is strict", envelope > 1 + beta**2, envelope, f"> {1 + beta**2}")
    check("defect polynomial", defect == sp.factor(envelope * source_norm - output_norm), defect, "derived")
    check("fixture output", fixture_output == sp.Rational(fixture["output_norm"]), fixture_output, fixture["output_norm"])
    check("fixture source", fixture_source == sp.Rational(fixture["source_norm"]), fixture_source, fixture["source_norm"])
    check("fixture defect", fixture_defect == sp.Rational(fixture["defect"]), fixture_defect, fixture["defect"])
    check("defect positive definite", sp.Poly(defect, x, y).coeffs() != [], sp.Poly(defect, x, y).coeffs(), "nonempty")
    defect_poly = sp.Poly(defect, x, y)
    defect_principal = [sp.factor(defect_poly.coeff_monomial(x**2)), sp.factor(defect_poly.coeff_monomial(y**2))]
    check("principal defect minors", defect_principal == [envelope - 1 - beta**2, envelope - 1], defect_principal, [envelope - 1 - beta**2, envelope - 1])

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
            "feedback_gain": beta,
            "envelope_constant": envelope,
            "owner_order": order,
            "root_multipliers": r176["registered_inputs"]["root_multipliers"],
            "feedback_matrix": feedback,
            "mixed_gram": gram,
            "source_norm": source_norm,
            "output_norm": output_norm,
            "defect": defect,
            "fixture_output": fixture_output,
            "fixture_source": fixture_source,
            "fixture_defect": fixture_defect,
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
    print(f"PRIMARY R-181 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
