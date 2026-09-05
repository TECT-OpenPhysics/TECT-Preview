#!/usr/bin/env python3
"""Integrated verifier for the conditional R503 mixture Cauchy bound."""
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
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-mixture-cauchy-lean-manifest.json"
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC012 = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
WEIGHT_INTAKE = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-limit-next-evidence-contract-v1.json"
LEAN = ROOT / "verification/lean/Tect/R503.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-mixture-cauchy-lean"
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"
TOOLCHAIN = "leanprover/lean4:v4.32.1"
LEAN_PIN = "0bf2dd8506c100d727bdc79e25b2d2fd06638093206c8657fb2cc3bb9ebb5ffc"
DECLARATIONS = ["finite_mixture_difference_bound"]
PINS = {
    "PAH-001": (PAH001, "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37"),
    "PAH-OMC-012": (OMC012, "180228b83e44f46406b302c97ff6caab023240eeaa19997618012074930f3e72"),
    "PAH-OMC-014": (OMC014, "1389bf64b2f26f267aa35bdfbee59cced2d16d8a5dcefd8e34a3deabb41d31b0"),
    "PAH-OMC-014-WEIGHT-INTAKE": (WEIGHT_INTAKE, "0ef41a6dd183458cea7ac45b84119dd820c7f5decdc8ef9ee393caca4031c502"),
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
    result = subprocess.run([str(lake), "env", "lean", "Tect/R503.lean"], cwd=LEAN.parent.parent, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False, timeout=180)
    output = (result.stdout + "\n" + result.stderr).strip()
    return {"status": "PASS" if result.returncode == 0 and "error:" not in output.lower() else "FAIL", "returncode": result.returncode, "command": "lake env lean Tect/R503.lean", "output": output[-2000:]}


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest, pah, graded, omc014, intake, registry = (read(path) for path in (MANIFEST, PAH001, OMC012, OMC014, WEIGHT_INTAKE, REGISTRY))
    source_bytes = LEAN.read_bytes()
    source = source_bytes.decode("utf-8")
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    for key, (path, expected) in PINS.items():
        check(f"{key} hash", sha(path) == expected, sha(path), expected)
    lean_meta = manifest.get("lean", {})
    item = next((entry for entry in registry.get("entrypoints", []) if entry.get("path") == "verification/lean/Tect/R503.lean"), None)
    declared = re.findall(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)", source)
    check("R503 source hash", sha(LEAN) == LEAN_PIN == lean_meta.get("sha256"), sha(LEAN), LEAN_PIN)
    check("R503 registry pin", item is not None and item.get("sha256") == LEAN_PIN and item.get("declarations") == DECLARATIONS, item, DECLARATIONS)
    check("R503 source policy", b"\r" not in source_bytes and source_bytes.endswith(b"\n") and not any(token in source for token in ("sorry", "admit", "axiom", "unsafe")), {"lf": b"\r" not in source_bytes, "final": source_bytes.endswith(b"\n")}, "LF/no escape")
    check("declaration marker", all(name in declared for name in DECLARATIONS), declared, DECLARATIONS)
    check("toolchain pin", lean_meta.get("toolchain") == TOOLCHAIN == registry.get("toolchain", {}).get("toolchain"), lean_meta.get("toolchain"), TOOLCHAIN)
    lean = compile_lean()
    check("Lean compilation", lean["status"] == "PASS", lean, "PASS")

    status = manifest.get("status", {})
    provenance = manifest.get("provenance", {})
    check("conditional HOLD firewall", status.get("verdict") == "HOLD_FOR_EVIDENCE" and status.get("active_gate_change") is False and status.get("claim_bearing") is False and provenance.get("source_law_present") is False and status.get("physical_promotion") is False, {"status": status, "provenance": provenance}, "HOLD/no law/no promotion")
    check("parent omega undefined", omc014.get("status", {}).get("omega_status") == "NOT_DEFINED" and graded.get("status", {}).get("global_normalized_gibbs_measure", "").startswith("NOT_DEFINED"), {"omega": omc014.get("status", {}).get("omega_status"), "global": graded.get("status", {}).get("global_normalized_gibbs_measure")}, "undefined")
    check("weight intake remains uninstantiated", intake.get("status", {}).get("verdict") == "HOLD_FOR_EVIDENCE" and intake.get("weight_law_status") in (None, "ABSENT"), intake.get("status"), "HOLD/absent")
    check("source law not invented", "must supply" in manifest.get("fixed_scope", {}).get("source_owner_obligation", "").lower() and provenance.get("source_law_present") is False, manifest.get("fixed_scope", {}).get("source_owner_obligation"), "symbolic future input")

    ew, ea, C = Fraction(1, 10), Fraction(1, 20), Fraction(2)
    w1 = (Fraction(1), Fraction(0), Fraction(0))
    w2 = (Fraction(9, 10), Fraction(1, 10), Fraction(0))
    a1 = (Fraction(1), Fraction(0), Fraction(2))
    a2 = (Fraction(19, 20), Fraction(1, 20), Fraction(2))
    drift_w = [abs(x - y) for x, y in zip(w1, w2)]
    drift_a = [abs(x - y) for x, y in zip(a1, a2)]
    component_bound = [abs(value) for value in a2]
    value1 = sum(w * a for w, a in zip(w1, a1))
    value2 = sum(w * a for w, a in zip(w2, a2))
    actual = abs(value1 - value2)
    bound = Fraction(3) * (C * ew + ea)
    check("finite drift hypotheses", max(drift_w) <= ew and max(drift_a) <= ea and max(component_bound) <= C and max(abs(w) for w in w1) <= 1, {"ew": str(ew), "ea": str(ea), "C": str(C), "drift_w": [str(x) for x in drift_w], "drift_a": [str(x) for x in drift_a]}, "all pointwise bounds")
    check("finite mixture bound", actual <= bound, {"actual": str(actual), "bound": str(bound), "value1": str(value1), "value2": str(value2)}, "actual <= card*(C*ew+ea)")
    check("error decomposition is explicit", "weight drift" in manifest.get("fixed_scope", {}).get("mixture", "").lower() and "component-cylinder drift" in manifest.get("fixed_scope", {}).get("mixture", "").lower(), manifest.get("fixed_scope", {}).get("mixture"), "separate drifts")
    check("growing-Q tail remains open", "tail" in manifest.get("fixed_scope", {}).get("source_owner_obligation", "").lower() and any("tail" in item.lower() for item in manifest.get("theorem_contract", {}).get("not_supplied", [])), manifest.get("fixed_scope", {}).get("source_owner_obligation"), "tail input required")
    check("R484/Csw non-claims", any("physical" in item.lower() for item in manifest.get("non_claims", [])) and "No PAH-specific" in " ".join(manifest.get("theorem_contract", {}).get("not_supplied", [])), manifest.get("non_claims"), "no promotion")

    failed = [row for row in rows if not row["pass"]]
    payload = {
        "schema": "tect/pah-omc014-mixture-cauchy-lean-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": "PAH-OMC-014-MIXTURE-CAUCHY-LEAN-INTEGRATED-001",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "CONDITIONAL_SUPPORT_ONLY",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {"manifest": sha(MANIFEST), "lean": sha(LEAN), **{key: expected for key, (_path, expected) in PINS.items()}},
        "scope": {"finite_index_card": 3, "weight_error": str(ew), "component_error": str(ea), "component_bound": str(C), "tail": "not supplied"},
        "derived": {"actual_mixture_drift": str(actual), "certified_upper_bound": str(bound), "formula": "card(ι)*(C*e_w+e_a)"},
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
    raise SystemExit(0 if run()["verification"] == "PASS" else 1)
