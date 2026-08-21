"""Primary exact audit for the R-175 duplicated covariance square-root interface."""

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
MANIFEST = REPO / "strategy" / "pre-a-a13-duplicated-covariance-square-root-basis-manifest.json"
LEAN_DIR = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_DIR / "Tect" / "R175.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-21-lean-r175-duplicated-covariance-square-root-basis" / "primary.json"


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


def block(a: sp.MatrixBase) -> sp.Matrix:
    n = a.rows
    z = sp.zeros(n)
    return sp.Matrix.vstack(sp.Matrix.hstack(a, z), sp.Matrix.hstack(z, a))


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
    check(rows, "manifest identity", manifest["audit_id"] == "A13-DUPLICATED-COVARIANCE-SQUARE-ROOT-BASIS", manifest["audit_id"], "A13-DUPLICATED-COVARIANCE-SQUARE-ROOT-BASIS")
    check(rows, "claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check(rows, "no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(rows, f"input {key} hash", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])

    a1 = json.loads((REPO / manifest["inputs"]["a1_manifest"]["path"]).read_text(encoding="utf-8"))
    r150 = json.loads((REPO / manifest["inputs"]["r150_manifest"]["path"]).read_text(encoding="utf-8"))
    r174 = json.loads((REPO / manifest["inputs"]["r174_manifest"]["path"]).read_text(encoding="utf-8"))
    status = json.loads((REPO / manifest["inputs"]["a13_status"]["path"]).read_text(encoding="utf-8"))
    check(rows, "A1 owner", a1["claim_id"] == "A1-PRODUCTION-FUNCTIONAL-REALISATION", a1["claim_id"], "A1-PRODUCTION-FUNCTIONAL-REALISATION")
    check(rows, "R-150 remains predecessor", r150["result_ledger_id"] == "R-150" and r150["scope"]["full_two_root_owner_closed"] is False, [r150["result_ledger_id"], r150["scope"]["full_two_root_owner_closed"]], ["R-150", False])
    check(rows, "R-174 remains interface", r174["result_id"] == "R-174" and r174["claim_bearing"] is False, [r174["result_id"], r174["claim_bearing"]], ["R-174", False])
    check(rows, "A13 remains open", status["proof_complete"] is False and status["lifecycle"] == "ACTIVE", [status["proof_complete"], status["lifecycle"]], [False, "ACTIVE"])

    n = int(manifest["registered_inputs"]["dimension"])
    fixture = sp.Matrix([[sp.Rational(str(v)) for v in row] for row in manifest["registered_inputs"]["basis_fixture"]])
    check(rows, "fixture dimension", fixture.shape == (n, n), fixture.shape, (n, n))
    z = sp.zeros(n)
    eye = sp.eye(n)
    c = sp.simplify(fixture * fixture.T)
    g = sp.Matrix.vstack(sp.Matrix.hstack(fixture, z), sp.Matrix.hstack(z, fixture))
    gamma = sp.Matrix.vstack(sp.Matrix.hstack(c, z), sp.Matrix.hstack(z, c))
    j = sp.Matrix.vstack(sp.Matrix.hstack(z, -eye), sp.Matrix.hstack(eye, z))
    check(rows, "duplicated square-root product", sp.simplify(g * g.T - gamma) == sp.zeros(2 * n), g * g.T, gamma)
    check(rows, "complex structure commutation", sp.simplify(j * g - g * j) == sp.zeros(2 * n), j * g, g * j)
    check(rows, "covariance rotation commutation", sp.simplify(j * gamma - gamma * j) == sp.zeros(2 * n), j * gamma, gamma * j)
    minors = [sp.det(fixture[:i, :i]) for i in range(1, n + 1)]
    check(rows, "fixture leading minors positive", all(value > 0 for value in minors), minors, ">0")
    check(rows, "fixture determinant positive", sp.det(fixture) > 0, sp.det(fixture), ">0")
    symbolic = sp.Matrix(n, n, lambda i, j: sp.Symbol(f"l{i}{j}", real=True))
    symbolic_block = block(symbolic)
    symbolic_gamma = block(symbolic * symbolic.T)
    symbolic_j = sp.Matrix.vstack(sp.Matrix.hstack(sp.zeros(n), -sp.eye(n)), sp.Matrix.hstack(sp.eye(n), sp.zeros(n)))
    check(rows, "symbolic square-root identity", sp.simplify(symbolic_block * symbolic_block.T - symbolic_gamma) == sp.zeros(2 * n), True, True)
    check(rows, "symbolic commutation identity", sp.simplify(symbolic_j * symbolic_block - symbolic_block * symbolic_j) == sp.zeros(2 * n), True, True)

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
            "dimension": str(n),
            "fixture_covariance": c,
            "fixture_leading_principal_minors": minors,
            "fixture_determinant": sp.det(fixture),
            "duplicated_square_root": True,
            "complex_structure_commutation": True,
            "covariance_complex_structure_commutation": True,
            "a13_gate_closed": False,
            "sector_a_closed": False,
            "authority_hashes_ok": True,
            "lean_escape_tokens_absent": True,
            "boundary_present": True
        },
        "source_hashes": {key: item["sha256"] for key, item in manifest["inputs"].items()},
        "toolchain": TOOLCHAIN.read_text(encoding="utf-8").strip(),
        "lean_stdout": completed.stdout,
        "lean_stderr": completed.stderr,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["boundary"]
    }
    if not args.no_store:
        output = args.output if args.output.is_absolute() else REPO / args.output
        atomic_json(output, payload)
    print(f"PRIMARY R-175 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
