#!/usr/bin/env python3
"""Integrated verifier for the conditional R507 full-Q Cauchy composition."""
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
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-composed-cauchy-lean-manifest.json"
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
R503 = ROOT / "strategy/pa-hyp/PAH-OMC-014-mixture-cauchy-lean-manifest.json"
R504 = ROOT / "strategy/pa-hyp/PAH-OMC-014-separator-lean-manifest.json"
R505 = ROOT / "strategy/pa-hyp/PAH-OMC-014-sign-change-lean-manifest.json"
R506 = ROOT / "strategy/pa-hyp/PAH-OMC-014-tail-bound-lean-manifest.json"
R507 = ROOT / "verification/lean/Tect/R507.lean"
PROJECTIVE = ROOT / "strategy/pa-hyp/PAH-OMC-014-projective-kernel-obligation-260905.md"
Q0 = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-q0-projective-obstruction/integrated.json"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-composed-cauchy-lean"
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"
TOOLCHAIN = "leanprover/lean4:v4.32.1"
LEAN_PIN = "59c0fb6b703c300e6216d8f1980553d8792a5f36d24b9c8f517254262081cbac"
DECLARATIONS = ["finite_block_plus_two_tail_bound", "zero_tail_pair_is_block_bound"]
PINS = {
    "PAH-001": (PAH001, "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37"),
    "PAH-OMC-014": (OMC014, "1389bf64b2f26f267aa35bdfbee59cced2d16d8a5dcefd8e34a3deabb41d31b0"),
    "R-503": (R503, "25ae1c3e67444c4dcca73c93bb2ecb82b30d2750daf477feb0b7cafe4a393d2a"),
    "R-504": (R504, "83f0c578fb44de7e33b646ef2cee3a7d757c6ede6db40c60da31b9651e463186"),
    "R-505": (R505, "b7918dec2224b66523c5ed872c23b67a0a331d36d3765df65a242ae0457f8497"),
    "R-506": (R506, "310a73ea82b794b7aabe190de514764fe6ea5e45727bc623566dd3d64710686c"),
    "PROJECTIVE": (PROJECTIVE, "ea8495c9e12e464506ece41f4e75fe3044c922c1da71ea56dea0e387d8ac5d1e"),
    "Q0": (Q0, "3938987009c2ccf1a81272655277f1fa21dbfddc47fd49e2497975dc86e7f6fe"),
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


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = read(MANIFEST)
    omc014 = read(OMC014)
    r503 = read(R503)
    r504 = read(R504)
    r505 = read(R505)
    r506 = read(R506)
    registry = read(REGISTRY)
    source_bytes = R507.read_bytes()
    source = source_bytes.decode("utf-8")
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    for key, (path, expected) in PINS.items():
        actual = sha(path)
        check(f"{key} hash", actual == expected, actual, expected)
    lean_meta = manifest.get("lean", {})
    registry_item = next(
        (entry for entry in registry.get("entrypoints", []) if entry.get("path") == "verification/lean/Tect/R507.lean"),
        None,
    )
    declared = re.findall(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)", source)
    check("R507 source hash", sha(R507) == LEAN_PIN == lean_meta.get("sha256"), sha(R507), LEAN_PIN)
    check(
        "R507 registry pin",
        registry_item is not None
        and registry_item.get("sha256") == LEAN_PIN
        and registry_item.get("declarations") == DECLARATIONS,
        registry_item,
        DECLARATIONS,
    )
    check(
        "R507 source policy",
        b"\r" not in source_bytes
        and source_bytes.endswith(b"\n")
        and not any(token in source for token in ("sorry", "admit", "axiom", "unsafe")),
        {"lf": b"\r" not in source_bytes, "final_newline": source_bytes.endswith(b"\n")},
        "LF/no escape",
    )
    check("declaration markers", all(name in declared for name in DECLARATIONS), declared, DECLARATIONS)
    check("toolchain pin", lean_meta.get("toolchain") == TOOLCHAIN, lean_meta.get("toolchain"), TOOLCHAIN)
    lean = compile_lean()
    check("Lean compilation", lean["status"] == "PASS", lean, "PASS")

    status = manifest.get("status", {})
    provenance = manifest.get("provenance", {})
    check(
        "conditional HOLD firewall",
        status.get("verdict") == "HOLD_FOR_EVIDENCE"
        and status.get("classification") == "CONDITIONAL_SUPPORT_ONLY"
        and status.get("active_gate_change") is False
        and status.get("claim_bearing") is False
        and provenance.get("source_law_present") is False
        and status.get("physical_promotion") is False,
        {"status": status, "provenance": provenance},
        "HOLD/no law/no promotion",
    )
    check(
        "parent full-Q state remains open",
        omc014.get("status", {}).get("verdict") == "HOLD_FOR_EVIDENCE"
        and omc014.get("status", {}).get("omega_status") == "NOT_DEFINED",
        omc014.get("status"),
        "HOLD/omega undefined",
    )
    check(
        "prior conditional bridges remain open",
        all(item.get("status", {}).get("verdict") == "HOLD_FOR_EVIDENCE" for item in (r503, r504, r505, r506)),
        {name: item.get("status", {}).get("verdict") for name, item in (("R503", r503), ("R504", r504), ("R505", r505), ("R506", r506))},
        "all HOLD",
    )
    boundary = manifest.get("boundary_and_uniformity", {})
    check(
        "R484/C_sw roles retained",
        "16/9" in boundary.get("R-484", "")
        and "540" in boundary.get("R-490", "")
        and "domination-only" in boundary.get("R-490", ""),
        boundary,
        "defect retained; C_sw domination-only",
    )
    check(
        "source-owned instantiation remains absent",
        "source-owned" in manifest.get("fixed_scope", {}).get("source_owner_role", "")
        and "supplies no such instantiation" in manifest.get("fixed_scope", {}).get("source_owner_role", ""),
        manifest.get("fixed_scope", {}).get("source_owner_role"),
        "future source input only",
    )

    block1, block2 = Fraction(1), Fraction(41, 50)
    tail1, tail2 = Fraction(1, 2), Fraction(-1, 5)
    e_w, e_a, C = Fraction(1, 10), Fraction(1, 20), Fraction(1)
    tau1, tau2 = Fraction(1), Fraction(1)
    block_bound = Fraction(3) * (C * e_w + e_a)
    tail_bound1, tail_bound2 = C * tau1, C * tau2
    total_bound = block_bound + tail_bound1 + tail_bound2
    actual = abs((block1 + tail1) - (block2 + tail2))
    check(
        "finite block contract fixture",
        abs(block1 - block2) <= block_bound and C >= 0 and e_w >= 0,
        {"block1": str(block1), "block2": str(block2), "block_drift": str(abs(block1 - block2)), "bound": str(block_bound)},
        "block drift <= card(I)*(C*e_w+e_a)",
    )
    check(
        "two tail contract fixture",
        abs(tail1) <= tail_bound1 and abs(tail2) <= tail_bound2,
        {"tail1": str(tail1), "tail2": str(tail2), "bounds": [str(tail_bound1), str(tail_bound2)]},
        "|tail_j| <= C*tau_j",
    )
    check(
        "composed exact envelope",
        actual <= total_bound,
        {"actual": str(actual), "block_bound": str(block_bound), "tail_bound1": str(tail_bound1), "tail_bound2": str(tail_bound2), "total_bound": str(total_bound)},
        "|(b1+t1)-(b2+t2)| <= block + tails",
    )
    check(
        "tail terms remain separate",
        "omitted weighted tails" in manifest.get("fixed_scope", {}).get("tail_terms", "")
        and "C*tau1+C*tau2" in manifest.get("fixed_scope", {}).get("composition", ""),
        {"tail_terms": manifest.get("fixed_scope", {}).get("tail_terms"), "composition": manifest.get("fixed_scope", {}).get("composition")},
        "two explicit tail budgets",
    )
    check(
        "zero-tail corollary",
        abs((block1 + 0) - (block2 + 0)) <= block_bound,
        {"zero_tail_value": str(abs(block1 - block2)), "bound": str(block_bound)},
        "block bound survives zero tails",
    )
    check(
        "non-claim text",
        any("cauchy" in item.lower() for item in manifest.get("non_claims", []))
        and any("weak cylinder convergence" in item.lower() for item in manifest.get("non_claims", []))
        and any("physical" in item.lower() for item in manifest.get("non_claims", [])),
        manifest.get("non_claims", []),
        "no limit or physical promotion",
    )

    failed = [row for row in rows if not row["pass"]]
    payload = {
        "schema": "tect/pah-omc014-composed-cauchy-lean-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": "PAH-OMC-014-COMPOSED-CAUCHY-LEAN-INTEGRATED-001",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "AUXILIARY_SUPPORT_FINITE_Q_CAUCHY_COMPOSITION",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {"manifest": sha(MANIFEST), "lean": sha(R507), **{key: expected for key, (_path, expected) in PINS.items()}},
        "scope": {
            "finite_index_card": 3,
            "block_values": [str(block1), str(block2)],
            "tail_values": [str(tail1), str(tail2)],
            "e_w": str(e_w),
            "e_a": str(e_a),
            "C": str(C),
            "tau1": str(tau1),
            "tau2": str(tau2),
            "source_owned_law": "not supplied",
        },
        "derived": {
            "actual_full_drift": str(actual),
            "block_bound": str(block_bound),
            "tail_bound1": str(tail_bound1),
            "tail_bound2": str(tail_bound2),
            "certified_total_bound": str(total_bound),
            "formula": "card(I)*(C*e_w+e_a)+C*tau1+C*tau2",
        },
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
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    raise SystemExit(0 if run(args.output)["verification"] == "PASS" else 1)
