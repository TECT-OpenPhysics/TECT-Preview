"""Primary exact audit for the F_ref/two-root Fourier frequency crosswalk."""

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
from pathlib import Path
from typing import Any

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a13-a1-fref-root-frequency-crosswalk-manifest.json"
LEAN_ROOT = ROOT / "verification/lean"
LEAN = LEAN_ROOT / "Tect/R203.lean"
DEFAULT_OUTPUT = ROOT / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-primary-fref-root-frequency-crosswalk/result.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def check(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
    if not condition:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")


def lake_path() -> str | None:
    pin = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    candidates = [
        Path.home() / ".elan" / "toolchains" / encoded / "bin" / "lake.exe",
        Path.home() / ".elan" / "toolchains" / encoded / "bin" / "lake",
        Path.home() / ".elan" / "bin" / "lake.exe",
        Path.home() / ".elan" / "bin" / "lake",
    ]
    for candidate in candidates:
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
    check(rows, "identity", manifest["audit_id"] == "A13-A1-FREF-ROOT-FREQUENCY-CROSSWALK", manifest["audit_id"], "A13-A1-FREF-ROOT-FREQUENCY-CROSSWALK")
    check(rows, "claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    for key, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        check(rows, f"source {key} hash", path.is_file() and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    a1 = json.loads((ROOT / manifest["source_authorities"]["a1_functional"]["path"]).read_text(encoding="utf-8"))
    r174 = json.loads((ROOT / manifest["source_authorities"]["r174_cylinder"]["path"]).read_text(encoding="utf-8"))
    r176 = json.loads((ROOT / manifest["source_authorities"]["r176_two_root"]["path"]).read_text(encoding="utf-8"))
    r192 = json.loads((ROOT / manifest["source_authorities"]["r192_owner"]["path"]).read_text(encoding="utf-8"))
    r197 = json.loads((ROOT / manifest["source_authorities"]["r197_fref_candidate"]["path"]).read_text(encoding="utf-8"))
    check(rows, "predecessors", [r174["result_id"], r192["result_id"]] == ["R-174", "R-192"], [r174["result_id"], r192["result_id"]], ["R-174", "R-192"])
    check(rows, "R-192 first missing slot", r192["registered_inputs"]["first_failure_slot"] == "heat_root_incidence", r192["registered_inputs"]["first_failure_slot"], "heat_root_incidence")
    params = a1["parameters"]
    L = sp.Rational(str(params["Lx"]))
    r = sp.Rational(str(params["r"]))
    z = sp.Rational(str(params["Z"]))
    y = sp.Rational(str(params["Y"]))
    h = 2 * sp.pi / L
    qstar2 = -z / (2 * y)
    ratio = sp.N(qstar2 / h**2, 40)
    k1 = sp.simplify(r + z * h**2 + y * h**4)
    k2 = sp.simplify(r + z * (2 * h)**2 + y * (2 * h)**4)
    k3 = sp.simplify(r + z * (sp.sqrt(3) * h)**2 + y * (sp.sqrt(3) * h)**4)
    registered = manifest["registered_inputs"]
    check(rows, "Fourier step", sp.simplify(h - sp.pi / 8) == 0, str(h), "pi/8")
    check(rows, "root norm squares", [1, 4] == [int(v) ** 2 for v in registered["root_multipliers"]], [1, 4], [1, 4])
    check(rows, "qstar ratio bracket", 2.9999999999 < float(ratio) < 3.0000000001, float(ratio), "(2.9999999999,3.0000000001)")
    check(rows, "nearest shell", int(round(float(ratio))) == 3, int(round(float(ratio))), 3)
    check(rows, "F_ref shell below roots", float(sp.N(k3, 30)) < float(sp.N(k2, 30)) < float(sp.N(k1, 30)), [float(sp.N(k3, 18)), float(sp.N(k2, 18)), float(sp.N(k1, 18))], "K3<K4<K1")
    formula = registered["r176_manifest_kinetic_formula"]
    executable = registered["r176_executable_formula"]
    check(rows, "manifest formula mismatch", formula != executable and "pi/L" in formula and "2*pi/L" in executable, [formula, executable], "different")
    check(rows, "R176 verifier does not pin formula string", "kinetic_formula" not in (ROOT / "codes/foundations/lean_a13_a1_two_root_cholesky_covariance_witness_verify.py").read_text(encoding="utf-8"), True, True)
    check(rows, "R197 candidate owner", r197["derived_contract"]["production_owner"] is False, r197["derived_contract"]["production_owner"], False)
    check(rows, "Lean source present", LEAN.is_file() and all(token not in LEAN.read_text(encoding="utf-8") for token in ("sorry", "admit", "axiom", "unsafe")), LEAN.is_file(), True)
    lake = lake_path()
    check(rows, "Lean compiler located", lake is not None, lake, "pinned lake")
    if lake:
        completed = subprocess.run([lake, "env", "lean", str(LEAN.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, capture_output=True, text=True, check=False)
        check(rows, "Lean R203 compile", completed.returncode == 0, completed.stdout + completed.stderr, "exit 0")
    derived = {
        "fourier_step": str(h),
        "fourier_step_numeric": float(sp.N(h, 18)),
        "qstar_square": str(qstar2),
        "qstar_square_numeric": float(sp.N(qstar2, 18)),
        "qstar_ratio_over_step_square": str(ratio),
        "qstar_ratio_over_step_square_numeric": float(ratio),
        "root_norm_squares": [1, 4],
        "nearest_fref_shell_norm_square": 3,
        "kinetic_n2_1": str(k1),
        "kinetic_n2_1_numeric": float(sp.N(k1, 18)),
        "kinetic_n2_3": str(k3),
        "kinetic_n2_3_numeric": float(sp.N(k3, 18)),
        "kinetic_n2_4": str(k2),
        "kinetic_n2_4_numeric": float(sp.N(k2, 18)),
        "manifest_formula_mismatch": True,
        "r192_first_missing_slot": "heat_root_incidence",
        "production_owner": False,
    }
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "audit_id": manifest["audit_id"], "run_kind": "primary", "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": derived, "boundary": manifest["boundary"]}
    if not args.no_store:
        atomic_json(args.output, payload)
    print(f"A13 FREF ROOT FREQUENCY CROSSWALK PRIMARY PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
