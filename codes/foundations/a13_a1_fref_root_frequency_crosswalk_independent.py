"""Stdlib-only independent audit for the F_ref/root frequency crosswalk."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a13-a1-fref-root-frequency-crosswalk-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-independent-fref-root-frequency-crosswalk/result.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assertions = []
    def test(name, condition, actual, expected):
        assertions.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        assert condition, f"{name}: {actual!r} != {expected!r}"
    for key, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        test(f"source {key} hash", path.is_file() and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    a1 = json.loads((ROOT / manifest["source_authorities"]["a1_functional"]["path"]).read_text(encoding="utf-8"))
    r192 = json.loads((ROOT / manifest["source_authorities"]["r192_owner"]["path"]).read_text(encoding="utf-8"))
    test("R-192 first missing slot", r192["registered_inputs"]["first_failure_slot"] == "heat_root_incidence", r192["registered_inputs"]["first_failure_slot"], "heat_root_incidence")
    p = a1["parameters"]
    L = Fraction(str(p["Lx"]))
    r = Fraction(str(p["r"]))
    z = Fraction(str(p["Z"]))
    y = Fraction(str(p["Y"]))
    h = 2.0 * math.pi / float(L)
    qstar2 = float(-z / (2 * y))
    ratio = qstar2 / (h * h)
    k = lambda n2: float(r) + float(z) * (h * h * n2) + float(y) * (h**4 * n2**2)
    test("Fourier step", abs(h - math.pi / 8.0) < 1e-15, h, math.pi / 8.0)
    test("root norm squares", [int(v) ** 2 for v in manifest["registered_inputs"]["root_multipliers"]] == [1, 4], [1, 4], [1, 4])
    test("qstar ratio bracket", 2.9999999999 < ratio < 3.0000000001, ratio, "(2.9999999999,3.0000000001)")
    test("nearest shell", round(ratio) == 3, round(ratio), 3)
    values = {1: k(1), 3: k(3), 4: k(4)}
    test("F_ref shell below roots", values[3] < values[4] < values[1], values, "K3<K4<K1")
    registered = manifest["registered_inputs"]
    test("manifest formula mismatch", registered["r176_manifest_kinetic_formula"] != registered["r176_executable_formula"], True, True)
    test("production owner absent", manifest["derived_contract"]["production_owner"] is False, manifest["derived_contract"]["production_owner"], False)
    derived = {"fourier_step": h, "qstar_square": qstar2, "qstar_ratio_over_step_square": ratio, "root_norm_squares": [1, 4], "nearest_fref_shell_norm_square": 3, "kinetic_n2_1": values[1], "kinetic_n2_3": values[3], "kinetic_n2_4": values[4], "manifest_formula_mismatch": True, "r192_first_missing_slot": "heat_root_incidence", "production_owner": False}
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "audit_id": manifest["audit_id"], "run_kind": "independent", "verdict": "PASS", "assertion_count": len(assertions), "assertions": assertions, "derived": derived, "boundary": manifest["boundary"]}
    if not args.no_store:
        atomic_json(args.output, payload)
    print(f"A13 FREF ROOT FREQUENCY CROSSWALK INDEPENDENT PASS {len(assertions)}/{len(assertions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
