#!/usr/bin/env python3
"""Independent reconstruction audit for the PAH-OMC-014 R500 bridge.

This script deliberately does not import the integrated verifier.  It checks
the parent bytes, source declarations, theorem contract, and pinned compile
from an independent implementation.
"""
from __future__ import annotations

import hashlib
import json
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
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-projective-mixture-lean/independent.json"
AUDIT_ID = "PAH-OMC-014-PROJECTIVE-MIXTURE-LEAN-INDEPENDENT-001"
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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with open(fd, "w", encoding="utf-8", newline="", closefd=True) as stream:
            json.dump(payload, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        Path(tmp_name).replace(path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def lake_path() -> Path | None:
    encoded = TOOLCHAIN.replace("/", "--").replace(":", "---")
    root = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        candidate = root / name
        if candidate.is_file():
            return candidate
    found = shutil.which("lake")
    return Path(found) if found else None


def compile_lean() -> dict[str, Any]:
    command = "lake env lean Tect/R500.lean"
    lake = lake_path()
    if lake is None:
        return {"status": "FAIL", "returncode": None, "command": command, "output": "pinned lake executable missing"}
    result = subprocess.run([str(lake), "env", "lean", "Tect/R500.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False, timeout=180)
    output = (result.stdout + "\n" + result.stderr).strip()
    return {"status": "PASS" if result.returncode == 0 and "error:" not in output.lower() else "FAIL", "returncode": result.returncode, "command": command, "output": output[-2000:]}


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    omc010 = json.loads(OMC010.read_text(encoding="utf-8"))
    omc012 = json.loads(OMC012.read_text(encoding="utf-8"))
    omc014 = json.loads(OMC014.read_text(encoding="utf-8"))
    source = LEAN.read_text(encoding="utf-8")
    raw = LEAN.read_bytes()
    obligation = " ".join(OBLIGATION.read_text(encoding="utf-8").lower().split())
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    parents = manifest.get("parents", {})
    parent_data = {}
    for key, (relative, expected) in PARENT_PINS.items():
        record = parents.get(key, {})
        path = ROOT / relative
        parent_data[key] = {"path": record.get("path"), "record_hash": record.get("sha256"), "actual_hash": digest(path) if path.is_file() else "MISSING"}
    check("parent locators exact", all(parent_data[k]["path"] == PARENT_PINS[k][0] for k in PARENT_PINS), parent_data, {k: PARENT_PINS[k][0] for k in PARENT_PINS})
    check("parent hashes exact", all(parent_data[k]["actual_hash"] == PARENT_PINS[k][1] == parent_data[k]["record_hash"] for k in PARENT_PINS), parent_data, {k: PARENT_PINS[k][1] for k in PARENT_PINS})

    registry_item = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R500.lean"), None)
    declared = re.findall(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)", source)
    check("R500 bytes pinned", b"\r" not in raw and raw.endswith(b"\n") and digest(LEAN) == LEAN_PIN, {"sha256": digest(LEAN), "lf": b"\r" not in raw, "final_newline": raw.endswith(b"\n")}, LEAN_PIN)
    check("registry entry exact", registry_item is not None and registry_item.get("sha256") == LEAN_PIN and registry_item.get("declarations") == DECLARATIONS, registry_item, {"sha256": LEAN_PIN, "declarations": DECLARATIONS})
    check("source declarations exact", all(name in declared for name in DECLARATIONS), declared, DECLARATIONS)
    check("toolchain exact", manifest.get("lean", {}).get("toolchain") == TOOLCHAIN == registry.get("toolchain", {}).get("toolchain"), {"manifest": manifest.get("lean", {}).get("toolchain"), "registry": registry.get("toolchain", {}).get("toolchain")}, TOOLCHAIN)
    check("source has no unsafe placeholders", not any(re.search(rf"\b{token}\b", source) for token in ("sorry", "admit", "axiom", "unsafe")), True, "none")

    check("parent PAH states open", omc014.get("status", {}).get("omega_status") == "NOT_DEFINED" and omc014.get("status", {}).get("projective_consistency") == "NOT_TESTABLE" and omc012.get("status", {}).get("global_normalized_gibbs_measure", "").startswith("NOT_DEFINED"), {"omc012": omc012.get("status"), "omc014": omc014.get("status")}, "undefined/not-testable")
    check("OMC-010 remains pending", omc010.get("status", {}).get("uniform_interaction_envelope") == "PENDING_VERIFICATION" and omc010.get("status", {}).get("physical_promotion") is False, omc010.get("status"), "pending/nonphysical")

    status = manifest.get("status", {})
    provenance = manifest.get("provenance", {})
    check("HOLD and non-bearing", status.get("verdict") == "HOLD_FOR_EVIDENCE" and status.get("classification") == "CONDITIONAL_SUPPORT_ONLY" and status.get("claim_bearing") is False and provenance.get("source_law_present") is False and provenance.get("model_change") is False and provenance.get("parent_mutation") is False, {"status": status, "provenance": provenance}, "HOLD/non-bearing/no-law/no-mutation")
    assumptions = manifest.get("theorem_contract", {}).get("assumptions", [])
    missing = manifest.get("theorem_contract", {}).get("not_supplied", [])
    check("kernel hypotheses explicit", len(assumptions) == 5 and all(any(term in item.lower() for item in assumptions) for term in ("kernel", "row", "weights", "push-forward")), assumptions, "five kernel/row/weights/push-forward hypotheses")
    check("missing inputs explicit", all(any(term in item.lower() for item in missing) for term in ("source-owned", "gibbs", "cauchy", "r-484", "r-488")), missing, "source-owned/Gibbs/Cauchy/R-484/R-488")
    nonclaims = manifest.get("non_claims", [])
    check("non-claims explicit", "full-q" in json.dumps(manifest, ensure_ascii=True).lower() and all(any(term in item.lower() for item in nonclaims) for term in ("projective kernel", "weak cylinder", "physical pre-a", "qft", "toe")), nonclaims, "projective/weak/physical boundaries")
    check("obligation has exact kernel language", all(term in obligation for term in ("stochastic kernel", "weight recursion", "every bounded cylinder", "no sector weights")), obligation, "kernel/recursion/cylinder/no weights")
    check("source exposes finite-sum algebra", all(term in source for term in ("def weightedSum", "Finset.sum_comm", "hrec", "hpush", "hK_row")), source, "weighted sum and finite reindexing")

    compilation = compile_lean()
    check("independent Lean compile", compilation.get("status") == "PASS", compilation, "PASS")
    failed = [row for row in rows if not row["pass"]]
    payload = {
        "schema": "tect/pah-omc014-projective-mixture-lean-independent/1.0",
        "run_kind": "independent_support_audit",
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
        "lean": compilation,
        "source_hashes": {"manifest": digest(MANIFEST), "PAH-001": digest(PAH001), "PAH-OMC-010": digest(OMC010), "PAH-OMC-012": digest(OMC012), "PAH-OMC-014": digest(OMC014), "projective-obligation": digest(OBLIGATION), "R500": digest(LEAN)},
        "assumptions": assumptions,
        "missing_assumptions": missing,
        "non_claims": nonclaims,
        "next_question": "Can a source owner provide the pinned K_n(q_c | q_f), component Gibbs push-forward identity, and induced weight recursion for every finite-support cylinder?",
    }
    atomic_json(OUTPUT, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}; claim_bearing={payload['claim_bearing']}")
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
