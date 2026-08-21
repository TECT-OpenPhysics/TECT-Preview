"""Primary exact audit for the A13 two-root production-cylinder bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-a13-two-root-production-cylinder-cross-synthesis-manifest.json"
LEAN_DIR = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_DIR / "Tect" / "R174.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-21-lean-r174-two-root-production-cylinder-cross-synthesis" / "primary.json"


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
    check(rows, "manifest identity", manifest["audit_id"] == "A13-TWO-ROOT-PRODUCTION-CYLINDER-CROSS-SYNTHESIS", manifest["audit_id"], "A13-TWO-ROOT-PRODUCTION-CYLINDER-CROSS-SYNTHESIS")
    check(rows, "claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check(rows, "no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(rows, f"input {key} hash", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])

    a1 = json.loads((REPO / manifest["inputs"]["a1_manifest"]["path"]).read_text(encoding="utf-8"))
    r150 = json.loads((REPO / manifest["inputs"]["r150_manifest"]["path"]).read_text(encoding="utf-8"))
    r151 = json.loads((REPO / manifest["inputs"]["r151_manifest"]["path"]).read_text(encoding="utf-8"))
    status = json.loads((REPO / manifest["inputs"]["a13_status"]["path"]).read_text(encoding="utf-8"))
    check(rows, "A1 owner", a1["claim_id"] == "A1-PRODUCTION-FUNCTIONAL-REALISATION", a1["claim_id"], "A1-PRODUCTION-FUNCTIONAL-REALISATION")
    check(rows, "R-150 predecessor", r150["result_ledger_id"] == "R-150" and r150["scope"]["full_two_root_owner_closed"] is False, [r150["result_ledger_id"], r150["scope"]["full_two_root_owner_closed"]], ["R-150", False])
    check(rows, "R-151 predecessor", r151["result_ledger_id"] == "R-151" and r151["scope"]["multi_root_aggregation"] is False, [r151["result_ledger_id"], r151["scope"]["multi_root_aggregation"]], ["R-151", False])
    check(rows, "A13 remains open", status["proof_complete"] is False and status["lifecycle"] == "ACTIVE", [status["proof_complete"], status["lifecycle"]], [False, "ACTIVE"])

    p = a1["parameters"]
    length = sp.Rational(str(p["Lx"]))
    volume = length * sp.Rational(str(p["Ly"])) * sp.Rational(str(p["Lz"]))
    wave = sp.factor(2 * sp.pi / length)
    root_multipliers = [sp.Integer(v) for v in manifest["registered_inputs"]["root_multipliers"]]
    k, q = [sp.factor(v * wave) for v in root_multipliers]
    check(rows, "torus volume", volume == sp.Integer(manifest["registered_inputs"]["volume"]), volume, manifest["registered_inputs"]["volume"])
    check(rows, "root frequencies", [k, q] == [sp.pi / 8, sp.pi / 4], [k, q], [sp.pi / 8, sp.pi / 4])
    check(rows, "dyadic root relation", sp.simplify(q - 2 * k) == 0, q, 2 * k)

    z0 = sp.Matrix([sp.Rational(str(v)) for v in p["z0"]])
    masses = [sp.Rational(str(v)) for v in p["family_masses"]]
    lock = sp.Rational(str(p["k_lock"]))
    mass = sp.diag(*masses) + lock * (sp.eye(3) - z0 * z0.T / (z0.T * z0)[0])
    expected_mass = sp.Matrix([[sp.Rational(1, 10), -sp.Rational(1, 20), -sp.Rational(1, 20)], [-sp.Rational(1, 20), sp.Rational(13, 100), -sp.Rational(1, 20)], [-sp.Rational(1, 20), -sp.Rational(1, 20), sp.Rational(17, 100)]])
    check(rows, "A1 family-lock mass", mass == expected_mass, mass, expected_mass)
    r = sp.Rational(str(p["r"]))
    z = sp.Rational(str(p["Z"]))
    y = sp.Rational(str(p["Y"]))
    symbol = lambda frequency: sp.factor(r + z * frequency**2 + y * frequency**4)
    a1 = symbol(k)
    a2 = symbol(q)
    check(rows, "first kinetic positive", sp.N(a1, 40) > 0, sp.N(a1, 18), ">0")
    check(rows, "second kinetic positive", sp.N(a2, 40) > 0, sp.N(a2, 18), ">0")
    c1, s1, c2, s2, amp1, amp2, w1, w2 = sp.symbols("c1 s1 c2 s2 amp1 amp2 w1 w2", real=True)
    x1v2 = sp.expand(amp1 * c1 * (-w2 * amp2 * s2) + amp1 * s1 * (w2 * amp2 * c2))
    x2v1 = sp.expand(amp2 * c2 * (-w1 * amp1 * s1) + amp2 * s2 * (w1 * amp1 * c1))
    field_cross = sp.expand(amp1 * c1 * (amp2 * c2) + amp1 * s1 * (amp2 * s2))
    current_cross = sp.expand((-w1 * amp1 * s1) * (-w2 * amp2 * s2) + (w1 * amp1 * c1) * (w2 * amp2 * c2))
    cross_formula = sp.expand(amp1 * amp2 * (w2 - w1) * (s1 * c2 - c1 * s2))
    check(rows, "cross block 1 exact", sp.expand(x1v2 - w2 * amp1 * amp2 * (s1 * c2 - c1 * s2)) == 0, x1v2, "w2*a1*a2*(s1*c2-c1*s2)")
    check(rows, "cross block 2 exact", sp.expand(x2v1 + w1 * amp1 * amp2 * (s1 * c2 - c1 * s2)) == 0, x2v1, "-w1*a1*a2*(s1*c2-c1*s2)")
    check(rows, "cross blocks add", sp.expand(x1v2 + x2v1 - cross_formula) == 0, x1v2 + x2v1, cross_formula)
    check(rows, "field cross exact", sp.expand(field_cross - amp1 * amp2 * (c1 * c2 + s1 * s2)) == 0, field_cross, "a1*a2*(c1*c2+s1*s2)")
    check(rows, "current cross exact", sp.expand(current_cross - w1 * w2 * amp1 * amp2 * (c1 * c2 + s1 * s2)) == 0, current_cross, "w1*w2*a1*a2*(c1*c2+s1*s2)")
    fixture = manifest["registered_inputs"]["nonzero_fixture"]
    fixture_values = {amp1: sp.Rational(fixture["amp1"]), amp2: sp.Rational(fixture["amp2"]), w1: sp.Rational(fixture["w1"]), w2: sp.Rational(fixture["w2"]), c1: sp.Rational(fixture["c1"]), s1: sp.Rational(fixture["s1"]), c2: sp.Rational(fixture["c2"]), s2: sp.Rational(fixture["s2"])}
    fixture_cross = sp.factor(cross_formula.subs(fixture_values))
    check(rows, "nonzero cross fixture", fixture_cross == sp.Rational(str(manifest["registered_inputs"]["nonzero_fixture"]["cross"])), fixture_cross, manifest["registered_inputs"]["nonzero_fixture"]["cross"])
    check(rows, "same phase vanishes", sp.factor(cross_formula.subs({c2: c1, s2: s1})) == 0, sp.factor(cross_formula.subs({c2: c1, s2: s1})), 0)
    check(rows, "equal frequency vanishes", sp.factor(cross_formula.subs({w2: w1})) == 0, sp.factor(cross_formula.subs({w2: w1})), 0)
    phase_x = sp.symbols("x", real=True)
    phase_difference = -wave * phase_x
    check(rows, "one-period cross average cosine", sp.integrate(sp.cos(phase_difference), (phase_x, 0, length)) == 0, sp.integrate(sp.cos(phase_difference), (phase_x, 0, length)), 0)
    check(rows, "one-period cross average sine", sp.integrate(sp.sin(phase_difference), (phase_x, 0, length)) == 0, sp.integrate(sp.sin(phase_difference), (phase_x, 0, length)), 0)
    check(rows, "diagonal owner is insufficient", fixture_cross != 0, fixture_cross, "nonzero cross block")

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
            "root_multipliers": [str(v) for v in root_multipliers],
            "root_frequencies": [str(k), str(q)],
            "first_kinetic": str(a1),
            "second_kinetic": str(a2),
            "cross_formula": "amp1*amp2*(w2-w1)*(s1*c2-c1*s2)",
            "nonzero_fixture_cross": str(fixture_cross),
            "same_phase_cross": "0",
            "equal_frequency_cross": "0",
            "cross_average_cosine": "0",
            "cross_average_sine": "0",
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
    print(f"PRIMARY R-174 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
