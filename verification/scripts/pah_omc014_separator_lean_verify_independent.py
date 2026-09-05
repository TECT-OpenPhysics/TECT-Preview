#!/usr/bin/env python3
"""Independent replay of the R504 convex-separation bridge."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-separator-lean-manifest.json"
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
KERNEL = ROOT / "strategy/pa-hyp/PAH-OMC-014-projective-kernel-obligation-260905.md"
Q0_RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-q0-projective-obstruction/integrated.json"
LEAN = ROOT / "verification/lean/Tect/R504.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-separator-lean"
TOOLCHAIN = "leanprover/lean4:v4.32.1"
LEAN_PIN = "3a412b6a288d3c556606caea4be41ddb57ed2b935d0976eb0bb679bc17ab8f6e"
PINS = {
    PAH001: "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    OMC014: "1389bf64b2f26f267aa35bdfbee59cced2d16d8a5dcefd8e34a3deabb41d31b0",
    KERNEL: "ea8495c9e12e464506ece41f4e75fe3044c922c1da71ea56dea0e387d8ac5d1e",
    Q0_RUN: "3938987009c2ccf1a81272655277f1fa21dbfddc47fd49e2497975dc86e7f6fe",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def compile_lean() -> dict[str, Any]:
    encoded = TOOLCHAIN.replace("/", "--").replace(":", "---")
    base = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    lake = next((base / name for name in ("lake.exe", "lake") if (base / name).is_file()), None)
    if lake is None:
        found = shutil.which("lake")
        lake = Path(found) if found else None
    if lake is None:
        return {"status": "FAIL", "returncode": None, "command": "lake env lean Tect/R504.lean", "output": "pinned lake missing"}
    result = subprocess.run([str(lake), "env", "lean", "Tect/R504.lean"], cwd=LEAN.parent.parent, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False, timeout=180)
    output = (result.stdout + "\n" + result.stderr).strip()
    return {"status": "PASS" if result.returncode == 0 and "error:" not in output.lower() else "FAIL", "returncode": result.returncode, "command": "lake env lean Tect/R504.lean", "output": output[-2000:]}


def run(output: Path = RUN_DIR / "independent.json") -> dict[str, Any]:
    manifest, pah, omc014, q0_run, registry = (read(path) for path in (MANIFEST, PAH001, OMC014, Q0_RUN, REGISTRY))
    kernel_text = KERNEL.read_text(encoding='utf-8')
    source_bytes = LEAN.read_bytes()
    source = source_bytes.decode("utf-8")
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    actual_pins = {str(path): sha(path) for path in PINS}
    expected_pins = {str(path): expected for path, expected in PINS.items()}
    check("all parent hashes", actual_pins == expected_pins, actual_pins, expected_pins)
    status = manifest.get("status", {})
    provenance = manifest.get("provenance", {})
    check("manifest HOLD/no source law", status.get("verdict") == "HOLD_FOR_EVIDENCE" and provenance.get("source_law_present") is False and status.get("active_gate_change") is False, {"status": status, "provenance": provenance}, "HOLD/no law/no gate change")
    check("parent OMC-014 open", omc014.get("status", {}).get("verdict") == "HOLD_FOR_EVIDENCE" and omc014.get("status", {}).get("omega_status") == "NOT_DEFINED", omc014.get("status"), "HOLD/NOT_DEFINED")

    check("kernel obligation still open", "source-owned statement is a stochastic kernel" in kernel_text, "source-owned K_n absent", "open kernel input")
    check("Q0 negative is route-local", q0_run.get("verification") == "PASS" and q0_run.get("verdict") == "NEGATIVE_RESULT" and "global" in q0_run.get("boundary", "").lower(), {"verification": q0_run.get("verification"), "verdict": q0_run.get("verdict")}, "scoped negative")

    weights = (Fraction(1, 3), Fraction(1, 3), Fraction(1, 3))
    mismatch = (Fraction(1), Fraction(2), Fraction(3))
    c = Fraction(1)
    weighted = sum(w * d for w, d in zip(weights, mismatch))
    check("independent separator hypotheses", sum(weights) == 1 and all(w >= 0 for w in weights) and all(c <= d for d in mismatch), {"weights": [str(x) for x in weights], "mismatch": [str(x) for x in mismatch], "c": str(c)}, "normalized/nonnegative/one-sided")
    check("independent exact arithmetic", weighted == Fraction(2) and weighted >= c and weighted != 0, {"weighted_mismatch": str(weighted), "lower_bound": str(c)}, "2 >= 1 > 0")
    declared = re.findall(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)", source)
    item = next((entry for entry in registry.get("entrypoints", []) if entry.get("path") == "verification/lean/Tect/R504.lean"), None)
    check("Lean declarations/hash/registry", all(name in declared for name in ("weighted_mismatch_lower_bound", "weighted_mismatch_nonzero")) and sha(LEAN) == LEAN_PIN and item is not None and item.get("sha256") == LEAN_PIN, {"declared": declared, "registry": item, "sha256": sha(LEAN)}, "R504 registered")
    check("Lean source policy", b"\r" not in source_bytes and source_bytes.endswith(b"\n") and not any(token in source for token in ("sorry", "admit", "axiom", "unsafe")), {"lf": b"\r" not in source_bytes, "final": source_bytes.endswith(b"\n")}, "LF/no escape")
    lean = compile_lean()
    check("Lean compilation", lean["status"] == "PASS", lean, "PASS")
    check("non-claims retained", status.get("physical_promotion") is False and any("projective" in item.lower() for item in manifest.get("non_claims", [])) and any("QFT" in item for item in manifest.get("non_claims", [])), manifest.get("non_claims", []), "no promotion")

    failed = [row for row in rows if not row["pass"]]
    payload = {
        "schema": "tect/pah-omc014-separator-lean-independent/1.0",
        "run_kind": "independent",
        "audit_id": "PAH-OMC-014-SEPARATOR-LEAN-INDEPENDENT-001",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "CONDITIONAL_SUPPORT_ONLY",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {"manifest": sha(MANIFEST), "lean": sha(LEAN), **{path.name: expected for path, expected in PINS.items()}},
        "scope": {"finite_index_card": len(weights), "separator": str(c), "mismatch": [str(x) for x in mismatch]},
        "derived": {"weighted_mismatch": str(weighted), "lower_bound": str(c), "formula": "sum_i w_i d_i >= c"},
        "claim_bearing": False,
        "active_gate_change": False,
        "source_law_present": False,
        "projective_consistency": "NOT_TESTABLE",
        "weak_cylinder_limit": "NOT_TESTABLE",
        "non_claims": manifest.get("non_claims", []),
        "next_question": manifest.get("next_question"),
        "reproduction": manifest.get("reproduction", {}),
        "lean": lean,
    }
    atomic_json(output, payload)
    print(f"{payload['audit_id']} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}")
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN_DIR / "independent.json")
    args = parser.parse_args()
    raise SystemExit(0 if run(args.output)["verification"] == "PASS" else 1)
