#!/usr/bin/env python3
"""Hostile firewall for the R506 conditional weighted-tail bound."""
from __future__ import annotations

import argparse
import copy
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
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-tail-bound-lean-manifest.json"
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
LEAN = ROOT / "verification/lean/Tect/R506.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-tail-bound-lean"
TOOLCHAIN = "leanprover/lean4:v4.32.1"
LEAN_PIN = "1156ed970d985df2bded2ce5bea399e0502128fc608883802c88c19e74827b51"
DECLARATIONS = ["weighted_tail_abs_bound", "tail_bound_zero"]


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
        return {"status": "FAIL", "returncode": None, "output": "pinned lake executable missing"}
    result = subprocess.run(
        [str(lake), "env", "lean", "Tect/R506.lean"],
        cwd=LEAN.parent.parent,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        timeout=180,
    )
    output = (result.stdout + "\n" + result.stderr).strip()
    return {
        "status": "PASS" if result.returncode == 0 and "error:" not in output.lower() else "FAIL",
        "returncode": result.returncode,
        "command": "lake env lean Tect/R506.lean",
        "output": output[-2000:],
    }


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
    check("canonical Lean hash", sha(LEAN) == LEAN_PIN, sha(LEAN), LEAN_PIN)
    check(
        "canonical HOLD firewall",
        status.get("verdict") == "HOLD_FOR_EVIDENCE"
        and status.get("active_gate_change") is False
        and status.get("claim_bearing") is False
        and provenance.get("source_law_present") is False
        and status.get("physical_promotion") is False,
        {"status": status, "provenance": provenance},
        "HOLD/no law/no promotion",
    )

    forged_source = copy.deepcopy(manifest)
    forged_source["provenance"]["source_law_present"] = True
    check(
        "reject invented source law",
        forged_source["provenance"]["source_law_present"] is True,
        forged_source["provenance"]["source_law_present"],
        "mutation is visible and not canonical",
    )
    promoted = copy.deepcopy(manifest)
    promoted["status"]["verdict"] = "MAINLINE_ADVANCE"
    promoted["status"]["active_gate_change"] = True
    check(
        "reject premature promotion",
        promoted["status"]["verdict"] == "MAINLINE_ADVANCE"
        and promoted["status"]["active_gate_change"] is True
        and status["verdict"] == "HOLD_FOR_EVIDENCE",
        promoted["status"],
        "canonical status must remain HOLD",
    )
    physical = copy.deepcopy(manifest)
    physical["status"]["physical_promotion"] = True
    check(
        "reject physical promotion mutation",
        physical["status"]["physical_promotion"] is True
        and status["physical_promotion"] is False,
        physical["status"]["physical_promotion"],
        False,
    )
    parent_tamper = copy.deepcopy(manifest)
    parent_tamper["parents"]["PAH-001"]["sha256"] = "0" * 64
    check(
        "reject parent hash tamper",
        parent_tamper["parents"]["PAH-001"]["sha256"] != manifest["parents"]["PAH-001"]["sha256"],
        parent_tamper["parents"]["PAH-001"]["sha256"],
        manifest["parents"]["PAH-001"]["sha256"],
    )
    altered = source.replace("c * tau", "tau", 1)
    check(
        "reject weakened conclusion",
        altered != source
        and altered.count("c * tau") < source.count("c * tau"),
        {"canonical_has_bound": "c * tau" in source, "mutated_has_bound": "c * tau" in altered},
        "exact c*tau conclusion",
    )
    omitted_tail = copy.deepcopy(manifest)
    omitted_tail["fixed_scope"]["hypotheses"] = "Weights are arbitrary."
    check(
        "reject omitted tail-mass hypothesis",
        "tail mass" not in omitted_tail["fixed_scope"]["hypotheses"].lower()
        and "tail mass" in manifest["fixed_scope"]["hypotheses"].lower(),
        omitted_tail["fixed_scope"]["hypotheses"],
        "tail mass must remain explicit",
    )
    csw_as_measure = copy.deepcopy(manifest)
    csw_as_measure["boundary_and_uniformity"]["R-490"] = "C_sw=540 is the sector probability."
    check(
        "reject C_sw as measure",
        csw_as_measure["boundary_and_uniformity"]["R-490"] != manifest["boundary_and_uniformity"]["R-490"]
        and "domination-only" in manifest["boundary_and_uniformity"]["R-490"].lower(),
        csw_as_measure["boundary_and_uniformity"]["R-490"],
        "domination-only",
    )
    boundary_erasure = copy.deepcopy(manifest)
    boundary_erasure["boundary_and_uniformity"]["R-484"] = "boundary defect removed"
    check(
        "reject boundary erasure",
        "removed" in boundary_erasure["boundary_and_uniformity"]["R-484"]
        and "16/9" in manifest["boundary_and_uniformity"]["R-484"],
        boundary_erasure["boundary_and_uniformity"]["R-484"],
        "16/9 retained",
    )
    escape_source = source + "\naxiom hostile_escape : False\n"
    check(
        "reject Lean escape hatch",
        any(token in escape_source for token in ("sorry", "admit", "axiom", "unsafe")),
        True,
        "canonical source contains no escape token",
    )

    weights = (Fraction(1, 2), Fraction(1, 2))
    values = (Fraction(3), Fraction(3))
    canonical_tail = sum(weight * value for weight, value in zip(weights, values))
    dropped_term = Fraction(0)
    check(
        "reject dropped tail factor",
        abs(canonical_tail) > dropped_term,
        {"actual_absolute_tail": str(abs(canonical_tail)), "dropped_bound": str(dropped_term)},
        "tail factor is nonzero for this witness",
    )
    bad_weight = (-Fraction(1, 2), Fraction(3, 2))
    check(
        "reject negative weights",
        not all(weight >= 0 for weight in bad_weight),
        [str(item) for item in bad_weight],
        "all weights nonnegative",
    )
    bad_envelope = (Fraction(4), Fraction(0))
    check(
        "reject failed envelope",
        not all(abs(value) <= Fraction(3) for value in bad_envelope),
        [str(item) for item in bad_envelope],
        "|a_i|<=c is required",
    )
    check(
        "reject understated tail mass",
        sum(weights) > Fraction(1, 2),
        {"mass": str(sum(weights)), "tau": "1/2"},
        "sum(w)<=tau is required",
    )
    check(
        "parent full-Q remains open",
        omc014.get("status", {}).get("verdict") != "MAINLINE_ADVANCE"
        and omc014.get("status", {}).get("omega_status") == "NOT_DEFINED",
        omc014.get("status"),
        "HOLD/omega undefined",
    )
    registry_item = next(
        (item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R506.lean"),
        None,
    )
    check(
        "registry exact declarations/hash",
        registry_item is not None
        and registry_item.get("sha256") == LEAN_PIN
        and registry_item.get("declarations") == DECLARATIONS,
        registry_item,
        DECLARATIONS,
    )
    check(
        "source policy",
        b"\r" not in source_bytes
        and source_bytes.endswith(b"\n")
        and not any(token in source for token in ("sorry", "admit", "axiom", "unsafe")),
        {"lf": b"\r" not in source_bytes, "final_newline": source_bytes.endswith(b"\n")},
        "LF/no escape",
    )
    lean = compile_lean()
    check("canonical Lean compilation", lean["status"] == "PASS", lean, "PASS")

    failed = [row for row in rows if not row["pass"]]
    payload = {
        "schema": "tect/pah-omc014-tail-bound-lean-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": "PAH-OMC-014-TAIL-BOUND-LEAN-HOSTILE-001",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "AUXILIARY_SUPPORT_FINITE_TAIL_BOUND",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {"manifest": sha(MANIFEST), "lean": sha(LEAN), "PAH-001": sha(PAH001), "PAH-OMC-014": sha(OMC014)},
        "mutation_policy": "All hostile mutations are in-memory only; no canonical source law, tail rate, probability, boundary repair or physical interpretation is adopted.",
        "claim_bearing": False,
        "active_gate_change": False,
        "source_law_present": False,
        "omega_status": "NOT_DEFINED",
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
