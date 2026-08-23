"""Primary exact witness that static finite Gibbs data do not select mobility."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a13-fref-mobility-heat-root-nonidentifiability-manifest.json"
LEAN_ROOT = ROOT / "verification/lean"
LEAN = LEAN_ROOT / "Tect/R200.lean"
DEFAULT_OUTPUT = ROOT / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-primary-fref-mobility-heat-root-nonidentifiability/result.json"


def sha(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


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


def find_lake() -> str | None:
    pin = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    for name in ("lake.exe", "lake"):
        candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / name
        if candidate.is_file():
            return str(candidate)
    return None


def derive(manifest: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["registered_inputs"]
    hessian = [F(str(v)) for v in inputs["hessian_diagonal"]]
    ma = [F(str(v)) for v in inputs["mobility_a"]]
    mb = [F(str(v)) for v in inputs["mobility_b"]]
    beta = F(str(inputs["beta"]))
    rates_a = [m * h for m, h in zip(ma, hessian)]
    rates_b = [m * h for m, h in zip(mb, hessian)]
    residual_a = [m * (h + beta**-1 * (-beta * h)) for m, h in zip(ma, hessian)]
    residual_b = [m * (h + beta**-1 * (-beta * h)) for m, h in zip(mb, hessian)]
    covariance = [h**-1 for h in hessian]
    return {
        "hessian": [str(v) for v in hessian],
        "gibbs_covariance": [str(v) for v in covariance],
        "mobility_a_rates": [str(v) for v in rates_a],
        "mobility_b_rates": [str(v) for v in rates_b],
        "stationary_current_a": [str(v) for v in residual_a],
        "stationary_current_b": [str(v) for v in residual_b],
        "same_stationary_density": residual_a == [F(0)] * len(residual_a) and residual_b == [F(0)] * len(residual_b),
        "different_heat_rates": rates_a != rates_b,
        "root_labels": list(inputs["root_labels"]),
        "root_rate_pairs": {"A": dict(zip(inputs["root_labels"], [str(v) for v in rates_a])), "B": dict(zip(inputs["root_labels"], [str(v) for v in rates_b]))},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": str(actual), "expected": str(expected)})
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-FREF-MOBILITY-HEAT-ROOT-NONIDENTIFIABILITY", manifest["audit_id"], "A13-FREF-MOBILITY-HEAT-ROOT-NONIDENTIFIABILITY")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negative", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for label, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        check(f"source {label}", path.is_file() and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    for label, item in manifest["files"].items():
        path = ROOT / item["path"]
        check(f"file {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    cert = (ROOT / manifest["files"]["certificate"]["path"]).read_text(encoding="utf-8")
    check("certificate scope", all(token in cert for token in ("same stationary density", "different heat rates", "R-192", "A13/T-050", "No PDF")), True, True)
    check("hostile mutations", len(manifest["hostile_mutations"]) == 8, len(manifest["hostile_mutations"]), 8)
    derived = derive(manifest)
    check("stationary currents vanish", derived["same_stationary_density"], derived["stationary_current_a"], ["0", "0"])
    check("rates A", derived["mobility_a_rates"] == ["1", "1"], derived["mobility_a_rates"], ["1", "1"])
    check("rates B", derived["mobility_b_rates"] == ["2", "3"], derived["mobility_b_rates"], ["2", "3"])
    check("rates differ", derived["different_heat_rates"], True, True)
    check("covariance unchanged", derived["gibbs_covariance"] == ["1", "1"], derived["gibbs_covariance"], ["1", "1"])
    lake = find_lake()
    check("pinned lake", lake is not None, lake, "pinned lake")
    completed = subprocess.run([lake, "env", "lean", str(LEAN.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean", completed.returncode == 0 and "error:" not in (completed.stdout + completed.stderr).lower(), completed.stderr, "no Lean error")
    payload = {"schema": "tect/a13-fref-mobility-heat-root-nonidentifiability-primary/1.0", "run_kind": "primary", "audit_id": manifest["audit_id"], "exploration_id": manifest["exploration_id"], "claim_id": manifest["claim_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": derived, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "boundary": manifest["boundary"]}
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"A13 FREF MOBILITY HEAT ROOT NONIDENTIFIABILITY PRIMARY PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
