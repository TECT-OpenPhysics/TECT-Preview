#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-014 R500 projective-mixture bridge.

This audit checks a conditional finite algebra only.  It does not instantiate
the missing source-owned cross-Q kernel or PAH sector weights.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-projective-mixture-lean-manifest.json"
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC010 = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json"
OMC012 = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
OBLIGATION = ROOT / "strategy/pa-hyp/PAH-OMC-014-projective-kernel-obligation-260905.md"
LEAN = ROOT / "verification/lean/Tect/R500.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
LEAN_ROOT = ROOT / "verification/lean"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-projective-mixture-lean"
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"
AUDIT_ID = "PAH-OMC-014-PROJECTIVE-MIXTURE-LEAN-INTEGRATED-001"
TOOLCHAIN = "leanprover/lean4:v4.32.1"
LEAN_PIN = "2afe710dee80fe6a11ed5a0e97199f396d76fd301618697d6629eb40c740a2c1"
DECLARATIONS = [
    "coarse_weight_nonnegative",
    "coarse_weight_normalized",
    "projective_mixture_identity",
    "projective_mixture_preserves_probability",
]
PARENT_PINS = {
    "PAH-001": ("strategy/pa-hyp/PAH-001-v1.json", "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37"),
    "PAH-OMC-010": ("strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json", "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69"),
    "PAH-OMC-012": ("strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json", "180228b83e44f46406b302c97ff6caab023240eeaa19997618012074930f3e72"),
    "PAH-OMC-014": ("strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json", "1389bf64b2f26f267aa35bdfbee59cced2d16d8a5dcefd8e34a3deabb41d31b0"),
    "PROJECTIVE-KERNEL-OBLIGATION": ("strategy/pa-hyp/PAH-OMC-014-projective-kernel-obligation-260905.md", "ea8495c9e12e464506ece41f4e75fe3044c922c1da71ea56dea0e387d8ac5d1e"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
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
    command = "lake env lean Tect/R500.lean"
    lake = lake_for(TOOLCHAIN)
    if lake is None:
        return {"status": "FAIL", "returncode": None, "command": command, "output": "pinned lake executable missing"}
    result = subprocess.run([str(lake), "env", "lean", "Tect/R500.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False, timeout=180)
    output = (result.stdout + "\n" + result.stderr).strip()
    return {"status": "PASS" if result.returncode == 0 and "error:" not in output.lower() else "FAIL", "returncode": result.returncode, "command": command, "output": output[-2000:]}


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = load(MANIFEST)
    registry = load(REGISTRY)
    omc010 = load(OMC010)
    omc012 = load(OMC012)
    omc014 = load(OMC014)
    source = LEAN.read_text(encoding="utf-8")
    source_bytes = LEAN.read_bytes()
    obligation_text = " ".join(OBLIGATION.read_text(encoding="utf-8").lower().split())
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    parents = manifest.get("parents", {})
    for key, (relative, expected) in PARENT_PINS.items():
        record = parents.get(key, {})
        path = ROOT / relative
        actual = sha(path) if path.is_file() else "MISSING"
        check(f"{key} locator", record.get("path") == relative, record.get("path"), relative)
        check(f"{key} hash", actual == expected == record.get("sha256"), actual, expected)

    lean_meta = manifest.get("lean", {})
    registry_item = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R500.lean"), None)
    check("R500 LF/final newline", b"\r" not in source_bytes and source_bytes.endswith(b"\n"), {"lf": b"\r" not in source_bytes, "final_newline": source_bytes.endswith(b"\n")}, True)
    check("R500 source hash", sha(LEAN) == LEAN_PIN == lean_meta.get("sha256"), sha(LEAN), LEAN_PIN)
    check("registry declaration/hash pin", registry_item is not None and registry_item.get("sha256") == LEAN_PIN and registry_item.get("declarations") == DECLARATIONS, registry_item, {"sha256": LEAN_PIN, "declarations": DECLARATIONS})
    declared = re.findall(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)", source)
    check("source declarations", all(name in declared for name in DECLARATIONS), declared, DECLARATIONS)
    check("toolchain pin", lean_meta.get("toolchain") == TOOLCHAIN == registry.get("toolchain", {}).get("toolchain"), {"manifest": lean_meta.get("toolchain"), "registry": registry.get("toolchain", {}).get("toolchain")}, TOOLCHAIN)
    check("Lean forbidden tokens", not any(re.search(rf"\b{token}\b", source) for token in ("sorry", "admit", "axiom", "unsafe")), True, "none")

    provenance = manifest.get("provenance", {})
    status = manifest.get("status", {})
    check("conditional support firewall", provenance.get("source_law_present") is False and provenance.get("claim_bearing") is False and provenance.get("physical_authority") is False and provenance.get("model_change") is False and provenance.get("parent_mutation") is False and status.get("verdict") == "HOLD_FOR_EVIDENCE" and status.get("active_gate_change") is False and status.get("physical_promotion") is False, {"provenance": provenance, "status": status}, "no source law/no mutation/HOLD")
    check("parent gates remain open", omc010.get("status", {}).get("uniform_interaction_envelope") == "PENDING_VERIFICATION" and omc012.get("status", {}).get("global_normalized_gibbs_measure", "").startswith("NOT_DEFINED") and omc014.get("status", {}).get("omega_status") == "NOT_DEFINED", {"omc010": omc010.get("status"), "omc012": omc012.get("status"), "omc014": omc014.get("status")}, "pending/undefined/undefined")

    theorem = manifest.get("theorem_contract", {})
    assumptions = theorem.get("assumptions", [])
    not_supplied = theorem.get("not_supplied", [])
    check("five hypotheses explicit", len(assumptions) == 5 and all(isinstance(item, str) and item.strip() for item in assumptions), assumptions, "five nonempty hypotheses")
    check("kernel and push-forward hypotheses named", all(any(term in item.lower() for item in assumptions) for term in ("kernel", "row", "push-forward", "weights")), assumptions, "kernel/row/push-forward/weights")
    check("missing source inputs explicit", all(any(term in item.lower() for item in not_supplied) for term in ("source-owned", "gibbs", "cauchy", "r-484", "r-488")), not_supplied, "source-owned/Gibbs/Cauchy/R-484/R-488")
    nonclaims = manifest.get("non_claims", [])
    check("non-claims explicit", all(any(term in item.lower() for item in nonclaims) for term in ("projective kernel", "weak cylinder", "physical pre-a", "qft", "toe")), nonclaims, "projective/weak/physical boundaries")

    check("obligation matches theorem scope", all(term in obligation_text for term in ("stochastic kernel", "weight recursion", "every bounded cylinder", "no sector weights")), obligation_text, "kernel/recursion/cylinder/non-instantiated")
    check("finite theorem algebra is visible", all(term in source for term in ("def weightedSum", "Finset.sum_comm", "hrec", "hpush", "hK_row")), source, "weighted sum, finite sum commutation, recursion, push-forward, row sum")

    lean = compile_lean()
    check("R500 pinned Lean compilation", lean.get("status") == "PASS", lean, "PASS")
    failed = [row for row in rows if not row["pass"]]
    payload = {
        "schema": "tect/pah-omc014-projective-mixture-lean-integrated/1.0",
        "run_kind": "integrated_support_audit",
        "audit_id": AUDIT_ID,
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "result_id": None,
        "exploration_id": None,
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "CONDITIONAL_SUPPORT_ONLY",
        "claim_bearing": False,
        "active_gate_change": False,
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "lean": lean,
        "source_hashes": {"manifest": sha(MANIFEST), "PAH-001": sha(PAH001), "PAH-OMC-010": sha(OMC010), "PAH-OMC-012": sha(OMC012), "PAH-OMC-014": sha(OMC014), "projective-obligation": sha(OBLIGATION), "R500": sha(LEAN)},
        "assumptions": assumptions,
        "missing_assumptions": not_supplied,
        "non_claims": nonclaims,
        "next_question": "Can a source owner provide the pinned K_n(q_c | q_f), component Gibbs push-forward identity, and induced weight recursion for every finite-support cylinder without changing PAH-001?",
    }
    atomic_json(output if output.is_absolute() else ROOT / output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}; claim_bearing={payload['claim_bearing']}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(args.output)
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
