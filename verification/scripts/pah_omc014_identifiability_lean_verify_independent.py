#!/usr/bin/env python3
"""Independent, non-importing replay of the PAH-OMC-014 identifiability test."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
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
TOOLCHAIN = "leanprover/lean4:v4.32.1"
LEAN_PIN = "dfa66f5dfcb6f8120f502fd0e2802efe78753689fe1c652cd6e3ad9c55b0906b"
R492_PIN = "a3262487b384e02100f7875c0ac87db614552e0a20a9db20501b8fa5d6308e0f"
PARENT_PINS = {
    "PAH-001": (PAH001, "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37"),
    "PAH-OMC-012": (OMC012, "180228b83e44f46406b302c97ff6caab023240eeaa19997618012074930f3e72"),
    "PAH-OMC-014": (OMC014, "1389bf64b2f26f267aa35bdfbee59cced2d16d8a5dcefd8e34a3deabb41d31b0"),
    "PAH-OMC-014-MANIFEST": (OMC014_MANIFEST, "072a55e76c47e2917a94e010682a82819eaf6e062a59d0a7733b654fb6c0e812"),
    "R492": (R492, R492_PIN),
}
DECLARATIONS = ["mix_deltaWeight", "delta_mixtures_separate", "positive_witness_implies_nonidentifiable"]


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
    command = "lake env lean Tect/R501.lean"
    encoded = TOOLCHAIN.replace("/", "--").replace(":", "---")
    base = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    lake = next((base / name for name in ("lake.exe", "lake") if (base / name).is_file()), None)
    if lake is None:
        found = shutil.which("lake")
        lake = Path(found) if found else None
    if lake is None:
        return {"status": "FAIL", "command": command, "returncode": None, "output": "pinned lake executable missing"}
    result = subprocess.run([str(lake), "env", "lean", "Tect/R501.lean"], cwd=LEAN.parent.parent, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False, timeout=180)
    output = (result.stdout + "\n" + result.stderr).strip()
    return {"status": "PASS" if result.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": result.returncode, "output": output[-2000:]}


def run(output: Path = RUN_DIR / "independent.json") -> dict[str, Any]:
    manifest = read(MANIFEST)
    pah = read(PAH001)
    graded = read(OMC012)
    omc014 = read(OMC014)
    r492 = read(R492)
    registry = read(REGISTRY)
    source = LEAN.read_text(encoding="utf-8")
    source_bytes = LEAN.read_bytes()
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    for key, (path, expected) in PARENT_PINS.items():
        actual = sha(path) if path.is_file() else "MISSING"
        check(f"{key} hash", actual == expected, actual, expected)
    check("manifest status", manifest.get("status", {}).get("verdict") == "HOLD_FOR_EVIDENCE" and manifest.get("provenance", {}).get("source_law_present") is False, manifest.get("status"), "HOLD/no source law")
    check("parent PAH status", omc014.get("status", {}).get("omega_status") == "NOT_DEFINED" and graded.get("status", {}).get("global_normalized_gibbs_measure", "").startswith("NOT_DEFINED"), {"omega": omc014.get("status", {}).get("omega_status"), "global": graded.get("status", {}).get("global_normalized_gibbs_measure")}, "undefined")
    check("fixed-Q source semantics", "Q=sum_vell_v" in pah.get("symmetry_and_constraint", {}).get("fixed_sector", "").replace(" ", "") and "ell_v in {0,...,M_psi}" in pah.get("finite_regulator", {}).get("matter_cutoff", ""), pah.get("symmetry_and_constraint", {}).get("fixed_sector"), "nonnegative bounded ell with fixed Q")
    check("finite positive Gibbs premise", "counting measure" in pah.get("finite_regulator", {}).get("normalization", "") and "finite" in pah.get("functional_or_action", {}).get("boundedness", ""), pah.get("finite_regulator", {}), "finite counting Gibbs state")

    n = 2
    vertices = 2 * (n + 2)
    assignments_q0 = [a for a in product((0, 1), repeat=vertices) if sum(a) == 0]
    assignments_q1 = [a for a in product((0, 1), repeat=vertices) if sum(a) == 1]
    q1_anchor = [a for a in assignments_q1 if a[0] == 1]
    check("Q=0 is uniquely zero", assignments_q0 == [(0,) * vertices], {"vertices": vertices, "count": len(assignments_q0), "assignments": assignments_q0[:2]}, "one all-zero assignment")
    check("Q=1 has anchor witness", len(q1_anchor) == 1 and q1_anchor[0][0] == 1, {"count": len(assignments_q1), "anchor_witnesses": len(q1_anchor)}, "one ell_a=1 assignment")

    r492_primary = r492.get("runs", {}).get("primary", {}).get("payload", {})
    witness_rows = r492_primary.get("derived", {}).get("r488_witness_rows", [])
    witness = next((row for row in witness_rows if row.get("n") == n and row.get("coarse_Q") == 1 and row.get("observable") == "ell_a"), None)
    check("R492 witness is current", witness is not None and witness.get("finite_gibbs_positive") is True and witness.get("lift_value") == 1, witness, "positive finite Gibbs Q=1 ell_a witness")
    check("R492 status", r492.get("verification") == "PASS" and r492.get("verdict") == "MAINLINE_ADVANCE", {"verification": r492.get("verification"), "verdict": r492.get("verdict")}, "PASS/MAINLINE_ADVANCE")
    check("cylinder declaration", "grade-blind" in manifest.get("fixed_scope", {}).get("cylinder", "") and "ell_a" in manifest.get("fixed_scope", {}).get("cylinder", ""), manifest.get("fixed_scope", {}).get("cylinder"), "declared ell_a cylinder")

    w0 = tuple(1 if i == 0 else 0 for i in (0, 1))
    w1 = tuple(1 if i == 1 else 0 for i in (0, 1))
    check("both delta rows are probability rows", w0 == (1, 0) and w1 == (0, 1) and all(v >= 0 for v in w0 + w1) and sum(w0) == 1 and sum(w1) == 1, {"w0": w0, "w1": w1}, "nonnegative normalized")
    check("separation has strict sign", assignments_q0[0][0] == 0 and bool(q1_anchor) and bool(witness and witness.get("finite_gibbs_positive")), {"phi_Q0": "0", "phi_Q1": ">0"}, "strictly separated component values")
    check("Lean source is independent theorem", all(re.search(rf"(?m)^\s*theorem\s+{name}\b", source) for name in DECLARATIONS) and registry.get("entrypoints", [{}])[-1].get("path") == "verification/lean/Tect/R501.lean", {"declarations": DECLARATIONS, "registry_tail": registry.get("entrypoints", [{}])[-1]}, "R501 declarations registered")
    check("Lean bytes", b"\r" not in source_bytes and source_bytes.endswith(b"\n") and sha(LEAN) == LEAN_PIN, {"hash": sha(LEAN), "lf": b"\r" not in source_bytes, "final": source_bytes.endswith(b"\n")}, "pinned LF source")
    lean = compile_lean()
    check("Lean compilation", lean["status"] == "PASS", lean, "PASS")
    check("no adopted source law", manifest.get("provenance", {}).get("source_law_present") is False and "not source-owned" in manifest.get("fixed_scope", {}).get("counterfactual_weights", "").lower(), manifest.get("fixed_scope", {}).get("counterfactual_weights"), "counterfactual only")
    check("no physical promotion", manifest.get("status", {}).get("physical_promotion") is False and all("physical" not in item.lower() or "no" in item.lower() for item in manifest.get("non_claims", [])), manifest.get("non_claims"), "no physical claim")

    failed = [row for row in rows if not row["pass"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc014-identifiability-lean-independent/1.0",
        "run_kind": "independent",
        "audit_id": "PAH-OMC-014-IDENTIFIABILITY-LEAN-INDEPENDENT-001",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "AUXILIARY_SUPPORT_NONIDENTIFIABILITY",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {"manifest": sha(MANIFEST), "lean": sha(LEAN), "R492": sha(R492), **{key: sha(path) for key, (path, _expected) in PARENT_PINS.items()}},
        "scope": {"carrier": "PAH-OMC-004 G_2 finite component", "cylinder": "f=ell_a", "grades": [0, 1], "enumeration": {"n": n, "vertices": vertices, "q0_states": len(assignments_q0), "q1_states": len(assignments_q1)}},
        "separation": {"phi_Q0": "0", "phi_Q1": ">0 from finite positive Gibbs witness", "counterfactual_laws": {"w0": list(w0), "w1": list(w1)}},
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
    print(f"{payload['audit_id']} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}")
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN_DIR / "independent.json")
    args = parser.parse_args()
    raise SystemExit(0 if run(args.output)["verification"] == "PASS" else 1)
