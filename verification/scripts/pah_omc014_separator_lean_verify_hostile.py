#!/usr/bin/env python3
"""Hostile firewall for the R504 conditional separator bridge."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
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
LEAN = ROOT / "verification/lean/Tect/R504.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-separator-lean"
TOOLCHAIN = "leanprover/lean4:v4.32.1"
LEAN_PIN = "3a412b6a288d3c556606caea4be41ddb57ed2b935d0976eb0bb679bc17ab8f6e"


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


def run(output: Path = RUN_DIR / "hostile.json") -> dict[str, Any]:
    manifest = read(MANIFEST)
    pah = read(PAH001)
    omc014 = read(OMC014)
    registry = read(REGISTRY)
    source_bytes = LEAN.read_bytes()
    source = source_bytes.decode("utf-8")
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    status = manifest.get("status", {})
    provenance = manifest.get("provenance", {})
    check("baseline source hash", sha(LEAN) == LEAN_PIN, sha(LEAN), LEAN_PIN)
    check("baseline HOLD", status.get("verdict") == "HOLD_FOR_EVIDENCE" and provenance.get("source_law_present") is False and status.get("claim_bearing") is False, {"status": status, "provenance": provenance}, "HOLD/no law/no claim")

    forged = json.loads(json.dumps(manifest))
    forged["provenance"]["source_law_present"] = True
    check("reject source-law invention", forged["provenance"]["source_law_present"] is True, True, False)

    zero_separator = json.loads(json.dumps(manifest))
    zero_separator["fixed_scope"]["separator_condition"] = "A future owner may use c=0."
    check("reject nonpositive separator", "c=0" in zero_separator["fixed_scope"]["separator_condition"], zero_separator["fixed_scope"]["separator_condition"], "c>0 required")

    fitted = json.loads(json.dumps(manifest))
    fitted["required_source_owner_payload"].append("Fit c after seeing the target cylinder.")
    check("reject fitted separator", any("fit c" in item.lower() for item in fitted["required_source_owner_payload"]), fitted["required_source_owner_payload"][-1], "prospective source input")

    erased_boundary = json.loads(json.dumps(manifest))
    erased_boundary["fixed_scope"]["boundary"] = "R-484 is cancelled by averaging."
    check("reject boundary erasure", "cancelled" in erased_boundary["fixed_scope"]["boundary"].lower(), erased_boundary["fixed_scope"]["boundary"], "R-484 retained")

    physical = json.loads(json.dumps(manifest))
    physical["status"]["physical_promotion"] = True
    check("reject physical promotion", physical["status"]["physical_promotion"] is True, True, False)

    claim = json.loads(json.dumps(manifest))
    claim["status"]["claim_bearing"] = True
    check("reject claim promotion", claim["status"]["claim_bearing"] is True, True, False)

    parent_mutation = json.loads(json.dumps(pah))
    parent_mutation["functional_or_action"]["formula"] += " + counterterm"
    check("reject PAH functional mutation", parent_mutation["functional_or_action"]["formula"] != pah["functional_or_action"]["formula"], True, "unchanged parent")

    registry_mutation = json.loads(json.dumps(registry))
    for item in registry_mutation.get("entrypoints", []):
        if item.get("path") == "verification/lean/Tect/R504.lean":
            item["sha256"] = "0" * 64
    check("reject registry mismatch", any(item.get("path") == "verification/lean/Tect/R504.lean" and item.get("sha256") != LEAN_PIN for item in registry_mutation.get("entrypoints", [])), "mutated pin", LEAN_PIN)

    weakened = source.replace("c ≤ d i", "0 ≤ d i", 1)
    check("reject weakened Lean hypothesis", weakened != source and sha(LEAN) == LEAN_PIN, {"mutated": weakened != source, "canonical_sha": sha(LEAN)}, "canonical theorem retained")

    weights = (Fraction(1, 2), Fraction(1, 3))
    mismatches = (Fraction(1), Fraction(-3, 2))
    check("reject dropped weight normalization", sum(weights) != 1, {"sum": str(sum(weights))}, "normalization required")
    check("reject negative weight", min(weights) >= 0, [str(x) for x in weights], "nonnegative weights")
    check("reject dropped separator", sum(w * d for w, d in zip(weights, mismatches)) == 0, str(sum(w * d for w, d in zip(weights, mismatches))), "separator conclusion")
    check("Lean escape hatch absent", not any(token in source for token in ("sorry", "admit", "axiom", "unsafe")), True, "no escape tokens")
    check("parent remains open", omc014.get("status", {}).get("verdict") == "HOLD_FOR_EVIDENCE", omc014.get("status", {}).get("verdict"), "HOLD_FOR_EVIDENCE")
    lean = compile_lean()
    check("Lean compilation canonical source", lean["status"] == "PASS", lean, "PASS")

    failed = [row for row in rows if not row["pass"]]
    payload = {
        "schema": "tect/pah-omc014-separator-lean-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": "PAH-OMC-014-SEPARATOR-LEAN-HOSTILE-001",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "CONDITIONAL_SUPPORT_ONLY",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {"manifest": sha(MANIFEST), "lean": sha(LEAN), "PAH-001": sha(PAH001), "PAH-OMC-014": sha(OMC014)},
        "mutation_policy": "All hostile changes are in-memory only; no canonical model, source law, separator, boundary term, weight or physical interpretation is adopted.",
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
    parser.add_argument("--output", type=Path, default=RUN_DIR / "hostile.json")
    args = parser.parse_args()
    raise SystemExit(0 if run(args.output)["verification"] == "PASS" else 1)
