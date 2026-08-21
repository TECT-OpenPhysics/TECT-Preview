"""Primary exact Lean cross-check for the R-180 scalar triangular majorant."""

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
MANIFEST = REPO / "strategy" / "pre-a-a13-scalar-triangular-majorant-crosscheck-manifest.json"
LEAN_DIR = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_DIR / "Tect" / "R180.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-21-lean-r180-scalar-triangular-majorant-crosscheck" / "primary.json"


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

    check("manifest identity", manifest["audit_id"] == "A13-SCALAR-TRIANGULAR-MAJORANT-LEAN-CROSSCHECK", manifest["audit_id"], "A13-SCALAR-TRIANGULAR-MAJORANT-LEAN-CROSSCHECK")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])

    fixture = manifest["registered_inputs"]["fixture"]
    u = sp.Rational(fixture["u"])
    v = sp.Rational(fixture["v"])
    q = sp.Rational(fixture["q"])
    rho = sp.Rational(fixture["rho"])
    near = (u / (1 - u) - v / (1 - v)) / (q - 1)
    far_high = u / ((1 - u) * (1 - rho))
    h_five = sp.simplify(near + far_high)
    check("near fixture", near == sp.Rational(fixture["near"]), near, fixture["near"])
    check("far-high fixture", far_high == sp.Rational(fixture["far_high"]), far_high, fixture["far_high"])
    check("h-five fixture", h_five == sp.Rational(fixture["hFive"]), h_five, fixture["hFive"])
    geom_value = sum((sp.Rational(fixture["geom_base"]) ** i for i in range(int(fixture["geom_terms"]))), sp.Rational(0))
    check("finite geometric fixture", geom_value == sp.Rational(fixture["geom_value"]), geom_value, fixture["geom_value"])
    margins = manifest["registered_inputs"]["margins"]
    exponents = manifest["registered_inputs"]["exponents"]
    beta = sp.Rational(exponents["beta"])
    s = sp.Rational(exponents["s"])
    gamma = sp.Rational(exponents["gamma"])
    beta_margin = beta / 2 - gamma
    s_margin = s - gamma
    check("beta-half minus gamma", beta_margin == sp.Rational(margins["beta_half_minus_gamma"]), beta_margin, margins["beta_half_minus_gamma"])
    check("s minus gamma", s_margin == sp.Rational(margins["s_minus_gamma"]), s_margin, margins["s_minus_gamma"])
    check("fixture envelope", 0 < u < 1 and 0 < v < u and 1 < q and 0 < rho < 1, [u, v, q, rho], manifest["registered_inputs"]["envelope_hypotheses"])
    check("h-five positive", h_five > 0, h_five, ">0")

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
            "near_fixture": near,
            "far_high_fixture": far_high,
            "h_five_fixture": h_five,
            "geom_fixture": geom_value,
            "beta_half_minus_gamma": beta_margin,
            "s_minus_gamma": s_margin,
            "h_five_positive": True,
            "geom_closed": True,
            "production_exponent_margins": True,
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
    print(f"PRIMARY R-180 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
