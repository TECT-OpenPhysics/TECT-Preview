#!/usr/bin/env python3
"""Integrated verifier for the conditional R504 separator bridge."""
from __future__ import annotations

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
DECLARATIONS = ["weighted_mismatch_lower_bound", "weighted_mismatch_nonzero"]
PINS = {
    "PAH-001": (PAH001, "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37"),
    "PAH-OMC-014": (OMC014, "1389bf64b2f26f267aa35bdfbee59cced2d16d8a5dcefd8e34a3deabb41d31b0"),
    "PROJECTIVE-KERNEL-OBLIGATION": (KERNEL, "ea8495c9e12e464506ece41f4e75fe3044c922c1da71ea56dea0e387d8ac5d1e"),
    "Q0-COMPONENT-OBSTRUCTION": (Q0_RUN, "3938987009c2ccf1a81272655277f1fa21dbfddc47fd49e2497975dc86e7f6fe"),
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


def run(output: Path = RUN_DIR / "integrated.json") -> dict[str, Any]:
    manifest, pah, omc014, q0_run, registry = read(MANIFEST), read(PAH001), read(OMC014), read(Q0_RUN), read(REGISTRY)
    source_bytes = LEAN.read_bytes()
    source = source_bytes.decode("utf-8")
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    for key, (path, expected) in PINS.items():
        check(f"{key} hash", sha(path) == expected, sha(path), expected)
    status = manifest.get("status", {})
    provenance = manifest.get("provenance", {})
    check("R504 source hash", sha(LEAN) == LEAN_PIN == manifest.get("lean", {}).get("sha256"), sha(LEAN), LEAN_PIN)
    item = next((entry for entry in registry.get("entrypoints", []) if entry.get("path") == "verification/lean/Tect/R504.lean"), None)
    check("R504 registry pin", item is not None and item.get("sha256") == LEAN_PIN and item.get("declarations") == DECLARATIONS, item, DECLARATIONS)
    declared = re.findall(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)", source)
    check("declaration marker", all(name in declared for name in DECLARATIONS), declared, DECLARATIONS)
    check("toolchain pin", manifest.get("lean", {}).get("toolchain") == TOOLCHAIN == registry.get("toolchain", {}).get("toolchain"), manifest.get("lean", {}).get("toolchain"), TOOLCHAIN)
    check("Lean source policy", b"\r" not in source_bytes and source_bytes.endswith(b"\n") and not any(token in source for token in ("sorry", "admit", "axiom", "unsafe")), {"lf": b"\r" not in source_bytes, "final": source_bytes.endswith(b"\n")}, "LF/no escape")
    lean = compile_lean()
    check("Lean compilation", lean["status"] == "PASS", lean, "PASS")
    check("conditional HOLD firewall", status.get("verdict") == "HOLD_FOR_EVIDENCE" and status.get("active_gate_change") is False and status.get("claim_bearing") is False and status.get("physical_promotion") is False and provenance.get("source_law_present") is False, {"status": status, "provenance": provenance}, "HOLD/no law/no promotion")
    check("parent remains open", omc014.get("status", {}).get("verdict") == "HOLD_FOR_EVIDENCE" and omc014.get("status", {}).get("omega_status") == "NOT_DEFINED", omc014.get("status"), "HOLD/NOT_DEFINED")
    check("Q0 result remains scoped", q0_run.get("verification") == "PASS" and q0_run.get("verdict") == "NEGATIVE_RESULT" and "global" in q0_run.get("boundary", "").lower(), {"verification": q0_run.get("verification"), "verdict": q0_run.get("verdict"), "boundary": q0_run.get("boundary")}, "route-local negative")
    check("separator is future input", "must prove one common c>0" in manifest.get("fixed_scope", {}).get("separator_condition", "") and any("separator" in item.lower() for item in manifest.get("theorem_contract", {}).get("not_supplied", [])), manifest.get("fixed_scope", {}).get("separator_condition"), "not supplied")

    weights = (Fraction(1, 2), Fraction(1, 2))
    mismatch = (Fraction(1), Fraction(3, 2))
    c = Fraction(1)
    value = sum(w * d for w, d in zip(weights, mismatch))
    check("finite normalized fixture", sum(weights) == 1 and all(w >= 0 for w in weights) and all(c <= d for d in mismatch), {"weights": [str(x) for x in weights], "mismatch": [str(x) for x in mismatch], "c": str(c)}, "nonnegative normalized weights and common positive separator")
    check("separator arithmetic", value >= c and value != 0, {"weighted_mismatch": str(value), "lower_bound": str(c)}, "weighted mismatch >= c > 0")
    check("no weight selection", provenance.get("source_law_present") is False and "sector law" in " ".join(manifest.get("non_claims", [])).lower(), {"source_law_present": provenance.get("source_law_present"), "non_claims": manifest.get("non_claims", [])}, "symbolic only")
    check("boundary and C_sw firewall", "16/9" in manifest.get("fixed_scope", {}).get("boundary", "") and "domination-only" in manifest.get("fixed_scope", {}).get("boundary", ""), manifest.get("fixed_scope", {}).get("boundary"), "R-484 retained/C_sw domination-only")
    check("physical non-claims", any("physical" in item.lower() for item in manifest.get("non_claims", [])) and any("QFT" in item for item in manifest.get("non_claims", [])), manifest.get("non_claims", []), "no physical promotion")

    failed = [row for row in rows if not row["pass"]]
    payload = {
        "schema": "tect/pah-omc014-separator-lean-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": "PAH-OMC-014-SEPARATOR-LEAN-INTEGRATED-001",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "CONDITIONAL_SUPPORT_ONLY",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {"manifest": sha(MANIFEST), "lean": sha(LEAN), **{key: expected for key, (_path, expected) in PINS.items()}},
        "scope": {"finite_index_card": len(weights), "separator": str(c), "mismatch": [str(x) for x in mismatch], "tail": "not supplied"},
        "derived": {"weighted_mismatch": str(value), "lower_bound": str(c), "formula": "sum_i w_i d_i >= c"},
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
    raise SystemExit(0 if run()["verification"] == "PASS" else 1)
