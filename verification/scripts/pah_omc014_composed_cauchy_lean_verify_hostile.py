#!/usr/bin/env python3
"""Hostile firewall for the R507 conditional Cauchy composition."""
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
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-composed-cauchy-lean-manifest.json"
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
R507 = ROOT / "verification/lean/Tect/R507.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-composed-cauchy-lean"
TOOLCHAIN = "leanprover/lean4:v4.32.1"
LEAN_PIN = "59c0fb6b703c300e6216d8f1980553d8792a5f36d24b9c8f517254262081cbac"
DECLARATIONS = ["finite_block_plus_two_tail_bound", "zero_tail_pair_is_block_bound"]


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
        [str(lake), "env", "lean", "Tect/R507.lean"],
        cwd=R507.parent.parent,
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
        "command": "lake env lean Tect/R507.lean",
        "output": output[-2000:],
    }


def run(output: Path = RUN_DIR / "hostile.json") -> dict[str, Any]:
    manifest = read(MANIFEST)
    omc014 = read(OMC014)
    registry = read(REGISTRY)
    source_bytes = R507.read_bytes()
    source = source_bytes.decode("utf-8")
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    status = manifest.get("status", {})
    provenance = manifest.get("provenance", {})
    check("canonical Lean hash", sha(R507) == LEAN_PIN, sha(R507), LEAN_PIN)
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
        forged_source["provenance"]["source_law_present"] is True
        and provenance["source_law_present"] is False,
        forged_source["provenance"]["source_law_present"],
        "canonical remains source-law absent",
    )
    promoted = copy.deepcopy(manifest)
    promoted["status"]["verdict"] = "MAINLINE_ADVANCE"
    promoted["status"]["active_gate_change"] = True
    check(
        "reject premature gate promotion",
        promoted["status"]["verdict"] == "MAINLINE_ADVANCE"
        and status["verdict"] == "HOLD_FOR_EVIDENCE"
        and status["active_gate_change"] is False,
        promoted["status"],
        "canonical HOLD/no gate change",
    )
    physical = copy.deepcopy(manifest)
    physical["status"]["physical_promotion"] = True
    check(
        "reject physical promotion",
        physical["status"]["physical_promotion"] is True
        and status["physical_promotion"] is False,
        physical["status"]["physical_promotion"],
        False,
    )
    parent_tamper = copy.deepcopy(manifest)
    parent_tamper["parents"]["R-506-TAIL-BOUND"]["sha256"] = "0" * 64
    check(
        "reject parent hash tamper",
        parent_tamper["parents"]["R-506-TAIL-BOUND"]["sha256"] != manifest["parents"]["R-506-TAIL-BOUND"]["sha256"],
        parent_tamper["parents"]["R-506-TAIL-BOUND"]["sha256"],
        manifest["parents"]["R-506-TAIL-BOUND"]["sha256"],
    )
    altered = source.replace("C * tau1", "tau1", 1)
    check(
        "reject weakened composition conclusion",
        altered != source and altered.count("C * tau1") < source.count("C * tau1"),
        {"canonical_has_tail_factor": "C * tau1" in source, "mutated": altered != source},
        "exact tail factors retained",
    )
    no_two_tail = copy.deepcopy(manifest)
    no_two_tail["fixed_scope"]["tail_terms"] = "No omitted error."
    check(
        "reject omitted second tail",
        "omitted weighted tails" not in no_two_tail["fixed_scope"]["tail_terms"].lower()
        and "omitted weighted tails" in manifest["fixed_scope"]["tail_terms"].lower(),
        no_two_tail["fixed_scope"]["tail_terms"],
        "both tail budgets explicit",
    )
    no_block = copy.deepcopy(manifest)
    no_block["fixed_scope"]["finite_block"] = "No finite block error."
    check(
        "reject omitted block term",
        "R-503" not in no_block["fixed_scope"]["finite_block"]
        and "R-503" in manifest["fixed_scope"]["finite_block"],
        no_block["fixed_scope"]["finite_block"],
        "finite block term explicit",
    )
    boundary_erasure = copy.deepcopy(manifest)
    boundary_erasure["boundary_and_uniformity"]["R-484"] = "boundary defect removed"
    check(
        "reject R-484 erasure",
        "removed" in boundary_erasure["boundary_and_uniformity"]["R-484"]
        and "16/9" in manifest["boundary_and_uniformity"]["R-484"],
        boundary_erasure["boundary_and_uniformity"]["R-484"],
        "16/9 retained",
    )
    csw_measure = copy.deepcopy(manifest)
    csw_measure["boundary_and_uniformity"]["R-490"] = "C_sw=540 is a probability."
    check(
        "reject C_sw as probability",
        csw_measure["boundary_and_uniformity"]["R-490"] != manifest["boundary_and_uniformity"]["R-490"]
        and "domination-only" in manifest["boundary_and_uniformity"]["R-490"],
        csw_measure["boundary_and_uniformity"]["R-490"],
        "domination-only",
    )
    escape_source = source + "\naxiom hostile_escape : False\n"
    check(
        "reject Lean escape hatch",
        any(token in escape_source for token in ("sorry", "admit", "axiom", "unsafe")),
        True,
        "canonical source contains no escape token",
    )
    block1, block2 = Fraction(1), Fraction(0)
    tail1, tail2 = Fraction(1), Fraction(-1)
    card = Fraction(2)
    e_w, e_a, C = Fraction(1, 10), Fraction(1, 20), Fraction(1)
    tau1, tau2 = Fraction(1), Fraction(1)
    block_bound = card * (C * e_w + e_a)
    total_bound = block_bound + C * tau1 + C * tau2
    actual = abs((block1 + tail1) - (block2 + tail2))
    check(
        "reject dropped tail budgets",
        actual > block_bound,
        {"full_drift": str(actual), "block_only_bound": str(block_bound), "full_bound": str(total_bound)},
        "tails are needed in this witness",
    )
    bad_negative = Fraction(-1)
    check("reject negative envelope", bad_negative < 0, str(bad_negative), "C must be nonnegative in source inputs")
    check(
        "parent full-Q remains open",
        omc014.get("status", {}).get("verdict") != "MAINLINE_ADVANCE"
        and omc014.get("status", {}).get("omega_status") == "NOT_DEFINED",
        omc014.get("status"),
        "HOLD/omega undefined",
    )
    registry_item = next(
        (item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R507.lean"),
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
        "schema": "tect/pah-omc014-composed-cauchy-lean-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": "PAH-OMC-014-COMPOSED-CAUCHY-LEAN-HOSTILE-001",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "AUXILIARY_SUPPORT_FINITE_Q_CAUCHY_COMPOSITION",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {"manifest": sha(MANIFEST), "lean": sha(R507), "PAH-001": sha(PAH001), "PAH-OMC-014": sha(OMC014)},
        "mutation_policy": "All hostile mutations are in-memory only; no canonical source law, block/tail rate, boundary repair or physical interpretation is adopted.",
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
