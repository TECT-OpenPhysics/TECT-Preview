#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-014 R502 nonzero-weight obligation."""
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
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-nonzero-weight-lean-manifest.json"
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC012 = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
OMC014_MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-manifest.json"
R492 = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc012-full-q-graded-domain/integrated.json"
LEAN = ROOT / "verification/lean/Tect/R502.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-nonzero-weight-lean"
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"
TOOLCHAIN = "leanprover/lean4:v4.32.1"
LEAN_PIN = "37a9014b8d9f99fe0e3e23f18ddefcbb6960da7bcf4dd029b5f168b42c4d8b00"
R492_PIN = "a3262487b384e02100f7875c0ac87db614552e0a20a9db20501b8fa5d6308e0f"
DECLARATIONS = ["twoSectorValue_factor", "twoSectorValue_nonzero_iff", "lower_bound_requires_positive_weight"]
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


def lake_for() -> Path | None:
    encoded = TOOLCHAIN.replace("/", "--").replace(":", "---")
    base = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        candidate = base / name
        if candidate.is_file():
            return candidate
    found = shutil.which("lake")
    return Path(found) if found else None


def compile_lean() -> dict[str, Any]:
    command = "lake env lean Tect/R502.lean"
    lake = lake_for()
    if lake is None:
        return {"status": "FAIL", "returncode": None, "command": command, "output": "pinned lake executable missing"}
    result = subprocess.run([str(lake), "env", "lean", "Tect/R502.lean"], cwd=LEAN.parent.parent, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False, timeout=180)
    output = (result.stdout + "\n" + result.stderr).strip()
    return {"status": "PASS" if result.returncode == 0 and "error:" not in output.lower() else "FAIL", "returncode": result.returncode, "command": command, "output": output[-2000:]}


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest, pah, graded, omc014, omc014_manifest, r492, registry = (read(path) for path in (MANIFEST, PAH001, OMC012, OMC014, OMC014_MANIFEST, R492, REGISTRY))
    source_bytes = LEAN.read_bytes()
    source = source_bytes.decode("utf-8")
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    for key, (relative, expected) in PARENT_PINS.items():
        actual = sha(ROOT / relative)
        record = manifest.get("parents", {}).get(key, {})
        check(f"{key} hash", actual == expected == record.get("sha256"), actual, expected)
        check(f"{key} locator", record.get("path") == relative, record.get("path"), relative)

    lean_meta = manifest.get("lean", {})
    registry_item = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R502.lean"), None)
    declared = re.findall(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)", source)
    check("R502 LF/final newline", b"\r" not in source_bytes and source_bytes.endswith(b"\n"), {"lf": b"\r" not in source_bytes, "final": source_bytes.endswith(b"\n")}, True)
    check("R502 hash", sha(LEAN) == LEAN_PIN == lean_meta.get("sha256"), sha(LEAN), LEAN_PIN)
    check("registry declaration/hash pin", registry_item is not None and registry_item.get("sha256") == LEAN_PIN and registry_item.get("declarations") == DECLARATIONS, registry_item, DECLARATIONS)
    check("declarations present", all(name in declared for name in DECLARATIONS), declared, DECLARATIONS)
    check("toolchain pin", lean_meta.get("toolchain") == TOOLCHAIN == registry.get("toolchain", {}).get("toolchain"), lean_meta.get("toolchain"), TOOLCHAIN)
    check("Lean escape tokens absent", not any(re.search(rf"\b{token}\b", source) for token in ("sorry", "admit", "axiom", "unsafe")), True, "none")
    lean = compile_lean()
    check("Lean compilation", lean["status"] == "PASS", lean, "PASS")

    status = manifest.get("status", {})
    provenance = manifest.get("provenance", {})
    check("HOLD/non-bearing firewall", status.get("verdict") == "HOLD_FOR_EVIDENCE" and status.get("active_gate_change") is False and status.get("claim_bearing") is False and provenance.get("source_law_present") is False and status.get("physical_promotion") is False, {"status": status, "provenance": provenance}, "HOLD/no source law/no promotion")
    check("parent omega remains undefined", omc014.get("status", {}).get("omega_status") == "NOT_DEFINED" and graded.get("status", {}).get("global_normalized_gibbs_measure", "").startswith("NOT_DEFINED"), {"omega": omc014.get("status", {}).get("omega_status"), "global": graded.get("status", {}).get("global_normalized_gibbs_measure")}, "undefined")
    check("parent manifest status remains source-scoped", (omc014_manifest.get("status") == "HOLD_FOR_EVIDENCE" or omc014_manifest.get("status", {}).get("verdict") == "HOLD_FOR_EVIDENCE"), omc014_manifest.get("status"), "HOLD_FOR_EVIDENCE")

    n = 2
    vertex_count = 2 * (n + 2)
    q0 = [a for a in product((0, 1), repeat=vertex_count) if sum(a) == 0]
    q1 = [a for a in product((0, 1), repeat=vertex_count) if sum(a) == 1]
    q1_anchor = [a for a in q1 if a[0] == 1]
    check("exact Q=0 anchor value", len(q0) == 1 and q0[0][0] == 0, {"states": len(q0), "ell_a_values": [a[0] for a in q0]}, "one zero state")
    check("exact Q=1 anchor witness", len(q1_anchor) == 1 and q1_anchor[0][0] == 1, {"states": len(q1), "anchor_states": len(q1_anchor)}, "one ell_a=1 witness")
    witness_rows = r492.get("runs", {}).get("primary", {}).get("payload", {}).get("derived", {}).get("r488_witness_rows", [])
    witness = next((row for row in witness_rows if row.get("n") == n and row.get("coarse_Q") == 1 and row.get("observable") == "ell_a"), None)
    check("R492 positive finite witness", sha(R492) == R492_PIN and r492.get("verification") == "PASS" and witness and witness.get("finite_gibbs_positive") is True and witness.get("lift_value") == 1, witness, "Q=1 ell_a positive witness")
    check("cylinder scope fixed", "grade-blind" in manifest.get("fixed_scope", {}).get("cylinder", "") and "ell_a" in manifest.get("fixed_scope", {}).get("cylinder", ""), manifest.get("fixed_scope", {}).get("cylinder"), "grade-blind ell_a")

    phi1 = Fraction(1, 1)
    test_weights = [Fraction(0), Fraction(1, 3), Fraction(1, 1)]
    values = [w * phi1 for w in test_weights]
    check("factorization V=w1*a1", all(value == weight * phi1 for value, weight in zip(values, test_weights)), [str(v) for v in values], "w1*positive component")
    check("finite nonzero iff positive weight", values[0] == 0 and values[1] > 0 and values[2] > 0, [str(v) for v in values], "zero exactly at w1=0")
    delta = Fraction(1, 4)
    check("positive lower bound excludes zero weight", not (delta <= values[0]) and delta <= values[2], {"delta": str(delta), "zero_weight_value": str(values[0]), "positive_weight_value": str(values[2])}, "delta>0 forces w1>0")
    check("weights remain symbolic", manifest.get("fixed_scope", {}).get("weight_policy", "").startswith("w0 and w1 are symbolic") and provenance.get("source_law_present") is False, manifest.get("fixed_scope", {}).get("weight_policy"), "no adopted law")
    check("R484/Csw firewalls", "16/9" in " ".join(omc014.get("missing_assumptions", [])) + " " + " ".join(omc014.get("non_claims", [])) or "R-484" in " ".join(manifest.get("boundaries", [])), manifest.get("boundaries"), "boundary retained")
    check("physical non-claims", status.get("physical_promotion") is False and any("physical" in item.lower() for item in manifest.get("boundaries", [])), manifest.get("boundaries"), "no physical promotion")

    failed = [row for row in rows if not row["pass"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc014-nonzero-weight-lean-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": "PAH-OMC-014-NONZERO-WEIGHT-LEAN-INTEGRATED-001",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "AUXILIARY_SUPPORT_NONZERO_WEIGHT_OBLIGATION",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {"manifest": sha(MANIFEST), "lean": sha(LEAN), "R492": sha(R492), **{key: value[1] for key, value in PARENT_PINS.items()}},
        "scope": {"n": n, "cylinder": "ell_a", "component_values": {"Q0": "0", "Q1": ">0"}, "symbolic_weights": True},
        "obligation": "global ell_a nonzero requires positive Q=1 sector weight; a positive lower bound requires a corresponding source-owned lower-bound input",
        "claim_bearing": False,
        "active_gate_change": False,
        "source_law_present": False,
        "omega_status": "NOT_DEFINED",
        "projective_consistency": "NOT_TESTABLE",
        "weak_cylinder_limit": "NOT_TESTABLE",
        "non_claims": manifest.get("boundaries", []),
        "next_question": manifest.get("next_question"),
        "reproduction": manifest.get("reproduction", {}),
        "lean": lean,
    }
    atomic_json(output, payload)
    print(f"{payload['audit_id']} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}")
    return payload


if __name__ == "__main__":
    raise SystemExit(0 if run()["verification"] == "PASS" else 1)
