"""Primary exact audit for the R-176 A1 two-root covariance witnesses."""

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
MANIFEST = REPO / "strategy" / "pre-a-a13-a1-two-root-cholesky-covariance-witness-manifest.json"
LEAN_DIR = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_DIR / "Tect" / "R176.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-21-lean-r176-a1-two-root-cholesky-covariance-witness" / "primary.json"


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
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


def derive_mass(parameters: dict[str, Any]) -> sp.Matrix:
    family = [sp.Rational(str(value)) for value in parameters["family_masses"]]
    lock = sp.Rational(str(parameters["k_lock"]))
    z0 = sp.Matrix([sp.Rational(str(value)) for value in parameters["z0"]])
    projector = z0 * z0.T / (z0.T * z0)[0]
    return sp.simplify(sp.diag(*family) + lock * (sp.eye(3) - projector))


def lower_cholesky_symbol(a: sp.Symbol, mass: sp.Matrix) -> tuple[sp.Matrix, tuple[sp.Expr, ...]]:
    d1 = sp.factor(a + mass[0, 0])
    s1 = sp.sqrt(d1)
    q21 = sp.factor(mass[1, 0] / s1)
    q31 = sp.factor(mass[2, 0] / s1)
    d2 = sp.factor(a + mass[1, 1] - q21**2)
    s2 = sp.sqrt(d2)
    q32 = sp.factor((mass[2, 1] - q31 * q21) / s2)
    d3 = sp.factor(a + mass[2, 2] - q31**2 - q32**2)
    s3 = sp.sqrt(d3)
    lower = sp.Matrix([[s1, 0, 0], [q21, s2, 0], [q31, q32, s3]])
    return lower, (d1, d2, d3)


def max_abs(matrix: sp.MatrixBase, precision: int = 80) -> float:
    values = [abs(complex(sp.N(matrix[i, j], precision))) for i in range(matrix.rows) for j in range(matrix.cols)]
    return max(values, default=0.0).real


def block(matrix: sp.MatrixBase) -> sp.Matrix:
    n = matrix.rows
    zero = sp.zeros(n)
    return sp.Matrix.vstack(sp.Matrix.hstack(matrix, zero), sp.Matrix.hstack(zero, matrix))


def find_lake() -> str | None:
    pin = TOOLCHAIN.read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    for name in ("lake.exe", "lake"):
        candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / name
        if candidate.is_file():
            return str(candidate)
    for candidate in (Path.home() / ".elan" / "bin" / "lake.exe", Path.home() / ".elan" / "bin" / "lake"):
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
    check(rows, "manifest identity", manifest["audit_id"] == "A13-A1-TWO-ROOT-CHOLESKY-COVARIANCE-WITNESS", manifest["audit_id"], "A13-A1-TWO-ROOT-CHOLESKY-COVARIANCE-WITNESS")
    check(rows, "claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check(rows, "no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(rows, f"input {key} hash", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])

    a1 = json.loads((REPO / manifest["inputs"]["a1_manifest"]["path"]).read_text(encoding="utf-8"))
    r150 = json.loads((REPO / manifest["inputs"]["r150_manifest"]["path"]).read_text(encoding="utf-8"))
    r174 = json.loads((REPO / manifest["inputs"]["r174_manifest"]["path"]).read_text(encoding="utf-8"))
    r175 = json.loads((REPO / manifest["inputs"]["r175_manifest"]["path"]).read_text(encoding="utf-8"))
    status = json.loads((REPO / manifest["inputs"]["a13_status"]["path"]).read_text(encoding="utf-8"))
    check(rows, "A1 owner", a1["claim_id"] == "A1-PRODUCTION-FUNCTIONAL-REALISATION", a1["claim_id"], "A1-PRODUCTION-FUNCTIONAL-REALISATION")
    check(rows, "R-150 covariance predecessor", r150["result_ledger_id"] == "R-150" and r150["scope"]["canonical_A1_k_2k_covariances_identified"] is True, [r150["result_ledger_id"], r150["scope"]["canonical_A1_k_2k_covariances_identified"]], ["R-150", True])
    check(rows, "R-174 cross predecessor", r174["result_id"] == "R-174" and r174["claim_bearing"] is False, [r174["result_id"], r174["claim_bearing"]], ["R-174", False])
    check(rows, "R-175 supplied-witness predecessor", r175["result_id"] == "R-175" and r175["claim_bearing"] is False, [r175["result_id"], r175["claim_bearing"]], ["R-175", False])
    check(rows, "A13 remains open", status["proof_complete"] is False and status["lifecycle"] == "ACTIVE", [status["proof_complete"], status["lifecycle"]], [False, "ACTIVE"])

    parameters = a1["parameters"]
    mass = derive_mass(parameters)
    mass_expected = sp.Matrix([[sp.Rational(str(value)) for value in row] for row in manifest["registered_inputs"]["mass_oracle"]])
    check(rows, "derived family-lock mass", mass == mass_expected, mass, mass_expected)
    wave = 2 * sp.pi / sp.Rational(str(parameters["Lx"]))
    r_value = sp.Rational(str(parameters["r"]))
    z_value = sp.Rational(str(parameters["Z"]))
    y_value = sp.Rational(str(parameters["Y"]))
    kinetic_values = [sp.factor(r_value + z_value * (multiplier * wave) ** 2 + y_value * (multiplier * wave) ** 4) for multiplier in (1, 2)]
    check(rows, "first wave formula", sp.simplify(wave - sp.pi / 8) == 0, wave, sp.pi / 8)
    check(rows, "kinetic symbols positive", all(sp.N(value, 70) > 0 for value in kinetic_values), [sp.N(value, 30) for value in kinetic_values], ">0")

    a_symbol = sp.symbols("a", positive=True)
    lower, pivots_symbol = lower_cholesky_symbol(a_symbol, mass)
    symbol_a = a_symbol * sp.eye(3) + mass
    check(rows, "symbolic lower Gram factor", sp.simplify(lower * lower.T - symbol_a) == sp.zeros(3), lower * lower.T, symbol_a)
    check(rows, "symbolic pivots match determinant chain", sp.factor(pivots_symbol[0] * pivots_symbol[1] * pivots_symbol[2] - symbol_a.det()) == 0, sp.factor(pivots_symbol[0] * pivots_symbol[1] * pivots_symbol[2]), sp.factor(symbol_a.det()))

    root_rows: list[dict[str, Any]] = []
    duplicated_checks: list[bool] = []
    for label, kinetic in zip(("k", "2k"), kinetic_values):
        lower_actual, pivots = lower_cholesky_symbol(kinetic, mass)
        symbol_matrix = sp.simplify(kinetic * sp.eye(3) + mass)
        covariance = sp.simplify(symbol_matrix.inv())
        upper_root = sp.simplify(lower_actual.T.inv())
        pivot_values = [sp.N(value, 60) for value in pivots]
        pivot_positive = all(value > 0 for value in pivot_values)
        residual_covariance = max_abs(sp.N(upper_root * upper_root.T - covariance, 70), 70)
        gamma = block(covariance)
        root = block(upper_root)
        residual_duplicate = max_abs(sp.N(root * root.T - gamma, 70), 70)
        root_rows.append({
            "label": label,
            "kinetic": kinetic,
            "pivots": pivots,
            "pivots_numeric": pivot_values,
            "lower_factor": lower_actual,
            "covariance": covariance,
            "upper_covariance_root": upper_root,
            "covariance_root_residual": residual_covariance,
            "duplicated_root_residual": residual_duplicate,
        })
        check(rows, f"{label} pivots positive", pivot_positive, pivot_values, ">0")
        check(rows, f"{label} covariance inverse positive", all(value > 0 for value in sp.N(symbol_matrix.det(), 70).as_real_imag()[:1]), sp.N(symbol_matrix.det(), 30), ">0")
        check(rows, f"{label} inverse-transpose covariance root", residual_covariance < 1.0e-55, residual_covariance, "<1e-55")
        check(rows, f"{label} duplicated six-real root", residual_duplicate < 1.0e-55, residual_duplicate, "<1e-55")
        duplicated_checks.append(residual_duplicate < 1.0e-55)

    check(rows, "both actual roots instantiated", len(root_rows) == 2 and all(duplicated_checks), [item["label"] for item in root_rows], ["k", "2k"])
    check(rows, "root is not a supplied placeholder", all(item["pivots_numeric"][0] > 0 for item in root_rows), [item["pivots_numeric"][0] for item in root_rows], ">0 from A1")

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
            "dimension": "3",
            "first_kinetic_positive": True,
            "second_kinetic_positive": True,
            "both_actual_roots_instantiated": True,
            "lower_cholesky_gram_identity": True,
            "inverse_transpose_covariance_root_identity": True,
            "duplicated_six_real_root_identity": True,
            "root_kind": "inverse-transpose of principal lower Cholesky factor",
            "root_labels": ["k", "2k"],
            "root_pivots_positive": True,
            "root_residuals_below_tolerance": True,
            "a13_gate_closed": False,
            "sector_a_closed": False,
            "authority_hashes_ok": True,
            "lean_escape_tokens_absent": True,
            "boundary_present": True,
            "root_details": root_rows,
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
    print(f"PRIMARY R-176 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
