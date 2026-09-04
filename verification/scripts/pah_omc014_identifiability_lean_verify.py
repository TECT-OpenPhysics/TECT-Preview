#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-014 identifiability bridge.

The test is deliberately counterfactual: it proves that two admissible delta
weight assignments would disagree on the declared ``ell_a`` cylinder when the
Q=0 component is zero and the Q=1 component has a positive finite Gibbs
witness.  It never adopts either assignment as a PAH sector law.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-identifiability-lean-manifest.json"
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC012 = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
OMC014_MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-manifest.json"
R492 = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc012-full-q-graded-domain/integrated.json"
LEAN = ROOT / "verification/lean/Tect/R501.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-identifiability-lean"
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"
TOOLCHAIN = "leanprover/lean4:v4.32.1"
LEAN_PIN = "dfa66f5dfcb6f8120f502fd0e2802efe78753689fe1c652cd6e3ad9c55b0906b"
R492_PIN = "a3262487b384e02100f7875c0ac87db614552e0a20a9db20501b8fa5d6308e0f"
DECLARATIONS = [
    "mix_deltaWeight",
    "delta_mixtures_separate",
    "positive_witness_implies_nonidentifiable",
]
PARENT_PINS = {
    "PAH-001": ("strategy/pa-hyp/PAH-001-v1.json", "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37"),
    "PAH-OMC-012": ("strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json", "180228b83e44f46406b302c97ff6caab023240eeaa19997618012074930f3e72"),
    "PAH-OMC-014": ("strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json", "1389bf64b2f26f267aa35bdfbee59cced2d16d8a5dcefd8e34a3deabb41d31b0"),
    "PAH-OMC-014-MANIFEST": ("strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-manifest.json", "072a55e76c47e2917a94e010682a82819eaf6e062a59d0a7733b654fb6c0e812"),
    "R-492-INTEGRATED": ("claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc012-full-q-graded-domain/integrated.json", R492_PIN),
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


def lake_for(toolchain: str) -> Path | None:
    encoded = toolchain.replace("/", "--").replace(":", "---")
    base = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        candidate = base / name
        if candidate.is_file():
            return candidate
    found = shutil.which("lake")
    return Path(found) if found else None


def compile_lean() -> dict[str, Any]:
    command = "lake env lean Tect/R501.lean"
    lake = lake_for(TOOLCHAIN)
    if lake is None:
        return {"status": "FAIL", "returncode": None, "command": command, "output": "pinned lake executable missing"}
    result = subprocess.run([str(lake), "env", "lean", "Tect/R501.lean"], cwd=LEAN.parent.parent, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False, timeout=180)
    output = (result.stdout + "\n" + result.stderr).strip()
    return {"status": "PASS" if result.returncode == 0 and "error:" not in output.lower() else "FAIL", "returncode": result.returncode, "command": command, "output": output[-2000:]}


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = read(MANIFEST)
    pah = read(PAH001)
    graded = read(OMC012)
    omc014 = read(OMC014)
    omc014_manifest = read(OMC014_MANIFEST)
    r492 = read(R492)
    registry = read(REGISTRY)
    source = LEAN.read_text(encoding="utf-8")
    source_bytes = LEAN.read_bytes()
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    parent_rows = []
    for key, (relative, expected) in PARENT_PINS.items():
        path = ROOT / relative
        actual = sha(path) if path.is_file() else "MISSING"
        record = manifest.get("parents", {}).get(key, {})
        parent_rows.append({"id": key, "path": relative, "actual": actual, "expected": expected})
        check(f"{key} locator", record.get("path") == relative, record.get("path"), relative)
        check(f"{key} hash", actual == expected == record.get("sha256"), actual, expected)

    lean_meta = manifest.get("lean", {})
    registry_item = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R501.lean"), None)
    check("R501 LF/final newline", b"\r" not in source_bytes and source_bytes.endswith(b"\n"), {"lf": b"\r" not in source_bytes, "final_newline": source_bytes.endswith(b"\n")}, True)
    check("R501 source hash", sha(LEAN) == LEAN_PIN == lean_meta.get("sha256"), sha(LEAN), LEAN_PIN)
    check("registry declaration/hash pin", registry_item is not None and registry_item.get("sha256") == LEAN_PIN and registry_item.get("declarations") == DECLARATIONS, registry_item, {"sha256": LEAN_PIN, "declarations": DECLARATIONS})
    declared = re.findall(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)", source)
    check("source declarations", all(name in declared for name in DECLARATIONS), declared, DECLARATIONS)
    check("toolchain pin", lean_meta.get("toolchain") == TOOLCHAIN == registry.get("toolchain", {}).get("toolchain"), {"manifest": lean_meta.get("toolchain"), "registry": registry.get("toolchain", {}).get("toolchain")}, TOOLCHAIN)
    check("Lean forbidden tokens", not any(re.search(rf"\b{token}\b", source) for token in ("sorry", "admit", "axiom", "unsafe")), True, "none")
    lean = compile_lean()
    check("Lean compilation", lean["status"] == "PASS", lean, "PASS")

    provenance = manifest.get("provenance", {})
    status = manifest.get("status", {})
    check("conditional/non-bearing firewall", provenance.get("source_law_present") is False and provenance.get("claim_bearing") is False and provenance.get("physical_authority") is False and provenance.get("model_change") is False and status.get("verdict") == "HOLD_FOR_EVIDENCE" and status.get("active_gate_change") is False and status.get("physical_promotion") is False, {"provenance": provenance, "status": status}, "no source law/HOLD/no promotion")
    check("parent status remains open", omc014.get("status", {}).get("omega_status") == "NOT_DEFINED" and graded.get("status", {}).get("global_normalized_gibbs_measure", "").startswith("NOT_DEFINED"), {"omega": omc014.get("status", {}).get("omega_status"), "global": graded.get("status", {}).get("global_normalized_gibbs_measure")}, "undefined")
    check("PAH-001 fixed-Q declaration", "Q=sum_vell_v" in pah.get("symmetry_and_constraint", {}).get("fixed_sector", "").replace(" ", "") and "ell_v in {0,...,M_psi}" in pah.get("finite_regulator", {}).get("matter_cutoff", ""), {"fixed_sector": pah.get("symmetry_and_constraint", {}).get("fixed_sector"), "matter_cutoff": pah.get("finite_regulator", {}).get("matter_cutoff")}, "fixed nonnegative bounded charge")
    check("finite Gibbs positivity premise", pah.get("finite_regulator", {}).get("normalization", "").startswith("counting measure") and "F_rho and Z_(rho,Q) are finite" in pah.get("functional_or_action", {}).get("boundedness", ""), {"normalization": pah.get("finite_regulator", {}).get("normalization"), "boundedness": pah.get("finite_regulator", {}).get("boundedness")}, "finite positive Gibbs weights")

    r492_primary = r492.get("runs", {}).get("primary", {}).get("payload", {})
    witness_rows = r492_primary.get("derived", {}).get("r488_witness_rows", [])
    witness = next((row for row in witness_rows if row.get("n") == 2 and row.get("coarse_Q") == 1 and row.get("observable") == "ell_a"), None)
    check("R492 hash and PASS", sha(R492) == R492_PIN and r492.get("verification") == "PASS", {"hash": sha(R492), "verification": r492.get("verification")}, {"hash": R492_PIN, "verification": "PASS"})
    check("R492 Q=1 ell_a witness", witness is not None and witness.get("finite_gibbs_positive") is True and witness.get("lift_value") == 1, witness, "n=2,Q=1,ell_a,value=1,positive Gibbs mass")

    n = 2
    vertex_count = 2 * (n + 2)
    q0 = [assignment for assignment in product((0, 1), repeat=vertex_count) if sum(assignment) == 0]
    q1 = [assignment for assignment in product((0, 1), repeat=vertex_count) if sum(assignment) == 1]
    check("exact Q=0 enumeration", len(q0) == 1 and q0[0] == (0,) * vertex_count, {"vertex_count": vertex_count, "states": len(q0), "assignment": q0[0] if q0 else None}, "one all-zero assignment")
    q1_anchor = [assignment for assignment in q1 if assignment[0] == 1]
    check("exact Q=1 anchor witness", len(q1_anchor) == 1 and q1_anchor[0][0] == 1, {"states": len(q1), "anchor_one": len(q1_anchor)}, "at least one allowed ell_a=1 state")
    check("cylinder is declared grade-blind", "grade-blind" in manifest.get("fixed_scope", {}).get("cylinder", "") and "ell_a" in manifest.get("fixed_scope", {}).get("cylinder", ""), manifest.get("fixed_scope", {}).get("cylinder"), "ell_a grade-blind cylinder")
    h0 = Fraction(0)
    h1_positive = bool(witness and witness.get("finite_gibbs_positive") and witness.get("lift_value") == 1 and q1_anchor)
    check("component values separate", h0 == 0 and h1_positive, {"phi_Q0": str(h0), "phi_Q1": ">0" if h1_positive else "not established"}, "0 and strictly positive")

    grades = (0, 1)
    w0 = tuple(1 if grade == 0 else 0 for grade in grades)
    w1 = tuple(1 if grade == 1 else 0 for grade in grades)
    check("counterfactual delta weights normalized", all(value >= 0 for value in w0 + w1) and sum(w0) == 1 and sum(w1) == 1, {"w0": w0, "w1": w1}, "nonnegative rows summing to one")
    check("delta weights remain unadopted", "not source-owned" in manifest.get("fixed_scope", {}).get("counterfactual_weights", "") and provenance.get("source_law_present") is False, manifest.get("fixed_scope", {}).get("counterfactual_weights"), "counterfactual/no source law")
    check("Lean separation assumption matches finite witness", "delta_mixtures_separate" in declared and h1_positive, {"declared": declared, "h1_positive": h1_positive}, "conditional separation theorem applicable")
    check("physical firewall", all("physical" not in item.lower() or "no" in item.lower() for item in manifest.get("non_claims", [])) and manifest.get("status", {}).get("physical_promotion") is False, manifest.get("non_claims"), "no physical promotion")

    failed = [row for row in rows if not row["pass"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc014-identifiability-lean-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": "PAH-OMC-014-IDENTIFIABILITY-LEAN-INTEGRATED-001",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "AUXILIARY_SUPPORT_NONIDENTIFIABILITY",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {"manifest": sha(MANIFEST), "lean": sha(LEAN), "R492": sha(R492), **{key: value[1] for key, value in PARENT_PINS.items()}},
        "scope": {"carrier": "PAH-OMC-004 G_2 finite component at R=1 path", "cylinder": "f=ell_a", "grades": [0, 1], "counterfactual_weights": {"w0": list(w0), "w1": list(w1)}},
        "separation": {"phi_Q0": "0", "phi_Q1": ">0 from finite Gibbs witness", "conclusion": "component family does not identify a unique full-Q mixture"},
        "lean": lean,
        "claim_bearing": False,
        "active_gate_change": False,
        "source_law_present": False,
        "omega_status": "NOT_DEFINED",
        "projective_consistency": "NOT_TESTABLE",
        "non_claims": manifest.get("non_claims", []),
        "next_question": manifest.get("next_question"),
        "reproduction": manifest.get("reproduction", {}),
    }
    atomic_json(output, payload)
    print(f"{payload['audit_id']} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}; nonidentifiable={h1_positive}")
    return payload


def main() -> int:
    payload = run()
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
