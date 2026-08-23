#!/usr/bin/env python3
"""Integrated primary/independent/Lean gate for HYB-TECT-U1-CHARGED-SPECTRAL-0002."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-hyb-u1-charged-spectral-covariant-manifest.json"
LEAN_ROOT = REPO / "verification" / "lean"
LEAN_ENTRY = LEAN_ROOT / "Tect" / "HYB0002.lean"
PRIMARY = REPO / "codes" / "foundations" / "pre_a_hyb_u1_charged_spectral_covariant.py"
INDEPENDENT = REPO / "codes" / "foundations" / "pre_a_hyb_u1_charged_spectral_covariant_independent.py"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-integrated-hyb-u1-charged-spectral-covariant" / "integrated.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".charged-integrated-", suffix=".tmp", dir=str(path.parent))
    os.close(fd)
    tmp = Path(name)
    try:
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(path)
    finally:
        if tmp.exists():
            tmp.unlink()


def lake_path() -> Path | None:
    found = shutil.which("lake")
    if found:
        return Path(found)
    pin = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / "lake.exe"
    return candidate if candidate.is_file() else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any) -> None:
        checks.append({"name": name, "pass": bool(ok), "actual": str(actual)})
        if not ok:
            raise AssertionError(f"{name}: {actual}")

    check("candidate identity", manifest["candidate_id"] == "HYB-TECT-U1-CHARGED-SPECTRAL-0002", manifest.get("candidate_id"))
    check("finite T0 boundary", manifest["tier"] == "T0" and manifest["claim_bearing"] is False and manifest["selection"]["admission"] == "comparison_candidate_only", manifest.get("tier"))
    for key, item in manifest["source_authorities"].items():
        p = REPO / item["path"]
        check(f"authority {key}", p.is_file() and digest(p) == item["sha256"], digest(p) if p.is_file() else None)
    for rel, expected in manifest.get("artifact_hashes", {}).items():
        p = REPO / rel
        check(f"artifact {rel}", p.is_file() and digest(p) == expected, digest(p) if p.is_file() else None)
    with tempfile.TemporaryDirectory(prefix="hyb0002-integrated-") as td:
        tmp = Path(td)
        primary_out = tmp / "primary.json"
        independent_out = tmp / "independent.json"
        p_run = subprocess.run([sys.executable, str(PRIMARY), "--output", str(primary_out)], cwd=REPO, text=True, capture_output=True, check=False)
        i_run = subprocess.run([sys.executable, str(INDEPENDENT), "--output", str(independent_out)], cwd=REPO, text=True, capture_output=True, check=False)
        check("primary subprocess", p_run.returncode == 0 and primary_out.is_file(), {"returncode": p_run.returncode, "stdout": p_run.stdout[-500:], "stderr": p_run.stderr[-500:]})
        check("independent subprocess", i_run.returncode == 0 and independent_out.is_file(), {"returncode": i_run.returncode, "stdout": i_run.stdout[-500:], "stderr": i_run.stderr[-500:]})
        primary = json.loads(primary_out.read_text(encoding="utf-8")) if primary_out.is_file() else {}
        independent = json.loads(independent_out.read_text(encoding="utf-8")) if independent_out.is_file() else {}
        check("primary PASS verdict", primary.get("verdict") == "HYB-TECT-U1-CHARGED-SPECTRAL-PRIMARY-PASS", primary.get("verdict"))
        check("independent PASS verdict", independent.get("verdict") == "HYB-TECT-U1-CHARGED-SPECTRAL-INDEPENDENT-PASS", independent.get("verdict"))
        check("all child assertions pass", all(x.get("pass") for x in primary.get("assertions", []) + independent.get("assertions", [])), {"primary": len(primary.get("assertions", [])), "independent": len(independent.get("assertions", []))})
        check("cross-run covariance bounds", primary.get("derived", {}).get("D_covariance_max_error", 1.0) < 5e-12 and independent.get("derived", {}).get("D_covariance_max_error", 1.0) < 7e-12, {"primary": primary.get("derived"), "independent": independent.get("derived")})
        check("cross-run R-192 boundary", primary.get("derived", {}).get("r192_first_missing_slot") == independent.get("derived", {}).get("r192_first_missing_slot") == "heat_root_incidence", {"primary": primary.get("derived"), "independent": independent.get("derived")})
    lake = lake_path()
    lean = subprocess.run([str(lake), "env", "lean", str(LEAN_ENTRY.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, text=True, capture_output=True, check=False) if lake else None
    lean_text = LEAN_ENTRY.read_text(encoding="utf-8")
    check("Lean subprocess", lean is not None and lean.returncode == 0, {"returncode": lean.returncode if lean else None, "stderr": lean.stderr[-500:] if lean else None})
    check("Lean source policy", not any(token in lean_text.split() for token in ("sorry", "admit", "axiom", "unsafe")), "clean")
    passed = sum(int(x["pass"]) for x in checks)
    verdict = "HYB-TECT-U1-CHARGED-SPECTRAL-INTEGRATED-PASS" if passed == len(checks) else "HYB-TECT-U1-CHARGED-SPECTRAL-INTEGRATED-FAIL"
    payload = {"schema": "tect/pre-a-hyb-u1-charged-spectral-covariant-integrated/1.0", "candidate_id": manifest["candidate_id"], "verdict": verdict, "assertion_count": len(checks), "assertions": checks, "children": {"primary": "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-integrated-hyb-u1-charged-spectral-covariant/primary.json", "independent": "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-integrated-hyb-u1-charged-spectral-covariant/independent.json", "lean": "verification/lean/Tect/HYB0002.lean"}, "derived": {"r192_first_missing_slot": "heat_root_incidence", "production_owner": False, "child_assertions": 35}, "boundary": manifest["boundary"]}
    atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"{passed}/{len(checks)} PASS")
    print(verdict)
    print("R-192 first missing: heat_root_incidence")
    return 0 if verdict.endswith("-PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
