#!/usr/bin/env python3
"""Independent reconstruction audit for the PAH-OMC-014 R499 Lean bridge.

No integrated verifier is imported.  This lane re-parses the manifest and
source, checks the immutable parent pins, and compiles the pinned theorem.
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
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-witness-stationarity-lean-manifest.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
OMC010 = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json"
R488 = ROOT / "strategy/pa-hyp/R488-certificate.md"
R498 = ROOT / "strategy/pa-hyp/PAH-OMC-014-boundary-error-lean-manifest.json"
LEAN = ROOT / "verification/lean/Tect/R499.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
LEAN_ROOT = ROOT / "verification/lean"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-witness-stationarity-lean/independent.json"
AUDIT_ID = "PAH-OMC-014-WITNESS-STATIONARITY-LEAN-INDEPENDENT-001"
TOOLCHAIN = "leanprover/lean4:v4.32.1"
DECLARATIONS = [
    "mix_strictly_positive_of_witness",
    "stationarity_limit_of_abs_error",
    "stationarity_limit_of_eventual_zero",
]
PINNED = {
    "PAH-OMC-014": ("strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json", "1389bf64b2f26f267aa35bdfbee59cced2d16d8a5dcefd8e34a3deabb41d31b0"),
    "PAH-OMC-010": ("strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json", "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69"),
    "R-488-CERTIFICATE": ("strategy/pa-hyp/R488-certificate.md", "95af523293779dcd8b3ecdd676e7eb57d33eed53c0903676853a09e885cdbcb6"),
    "R-498-MANIFEST": ("strategy/pa-hyp/PAH-OMC-014-boundary-error-lean-manifest.json", "efbdd3e2f430f074fef33677f7481d1096c0dd1b4ed4fdd3f3c7732d5e244458"),
}
LEAN_PIN = "5be7c07c6ff6ac32c2bdbd91ebfc4f4c71e859aefc558a9db41c65f6525819e0"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with open(fd, "w", encoding="utf-8", newline="\n", closefd=True) as stream:
            json.dump(payload, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        Path(tmp_name).replace(path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
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


def lean_compile(toolchain: str) -> dict[str, Any]:
    lake = lake_for(toolchain)
    command = "lake env lean Tect/R499.lean"
    if lake is None:
        return {"status": "FAIL", "returncode": None, "command": command, "output": "pinned lake executable missing"}
    result = subprocess.run([str(lake), "env", "lean", "Tect/R499.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False, timeout=180)
    output = (result.stdout + "\n" + result.stderr).strip()
    return {"status": "PASS" if result.returncode == 0 and "error:" not in output.lower() else "FAIL", "returncode": result.returncode, "command": command, "output": output[-2000:]}


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    omc014 = json.loads(OMC014.read_text(encoding="utf-8"))
    omc010 = json.loads(OMC010.read_text(encoding="utf-8"))
    source = LEAN.read_text(encoding="utf-8")
    source_bytes = LEAN.read_bytes()
    r488_text = " ".join(R488.read_text(encoding="utf-8").lower().split())
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    parents = manifest.get("parents", {})
    parent_rows = {}
    for key, (relative, expected) in PINNED.items():
        record = parents.get(key, {})
        path = ROOT / relative
        actual = digest(path) if path.is_file() else "MISSING"
        parent_rows[key] = {"record_path": record.get("path"), "actual_hash": actual, "record_hash": record.get("sha256")}
    check("all immutable parent locators", all(parent_rows[k]["record_path"] == PINNED[k][0] for k in PINNED), parent_rows, {k: PINNED[k][0] for k in PINNED})
    check("all immutable parent hashes", all(parent_rows[k]["actual_hash"] == PINNED[k][1] == parent_rows[k]["record_hash"] for k in PINNED), parent_rows, {k: PINNED[k][1] for k in PINNED})

    registry_item = next((entry for entry in registry.get("entrypoints", []) if entry.get("path") == "verification/lean/Tect/R499.lean"), None)
    declarations = re.findall(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)", source)
    check("R499 exact source bytes", b"\r" not in source_bytes and source_bytes.endswith(b"\n") and digest(LEAN) == LEAN_PIN, {"sha256": digest(LEAN), "lf": b"\r" not in source_bytes, "final_newline": source_bytes.endswith(b"\n")}, LEAN_PIN)
    check("registry pins source", registry_item is not None and registry_item.get("sha256") == LEAN_PIN and registry_item.get("declarations") == DECLARATIONS, registry_item, {"sha256": LEAN_PIN, "declarations": DECLARATIONS})
    check("source theorem names", all(name in declarations for name in DECLARATIONS), declarations, DECLARATIONS)
    check("toolchain agreement", manifest.get("lean", {}).get("toolchain") == TOOLCHAIN == registry.get("toolchain", {}).get("toolchain"), {"manifest": manifest.get("lean", {}).get("toolchain"), "registry": registry.get("toolchain", {}).get("toolchain")}, TOOLCHAIN)

    status = manifest.get("status", {})
    provenance = manifest.get("provenance", {})
    check("parent states are still open", omc014.get("status", {}).get("omega_status") == "NOT_DEFINED" and omc010.get("status", {}).get("uniform_interaction_envelope") == "PENDING_VERIFICATION", {"omc014": omc014.get("status"), "omc010": omc010.get("status")}, "open/pending")
    check("support-only status", status.get("verdict") == "HOLD_FOR_EVIDENCE" and status.get("classification") == "CONDITIONAL_SUPPORT_ONLY" and status.get("claim_bearing") is False and provenance.get("source_law_present") is False and provenance.get("model_change") is False and provenance.get("parent_mutation") is False, {"status": status, "provenance": provenance}, "HOLD/non-bearing/no-law/no-mutation")

    assumptions = manifest.get("theorem_contract", {}).get("assumptions", [])
    missing = manifest.get("theorem_contract", {}).get("not_supplied", [])
    check("witness/error hypotheses explicit", len(assumptions) == 5 and any("positive" in item.lower() and "witness" in item.lower() for item in assumptions) and any("absolute error" in item.lower() for item in assumptions), assumptions, "five hypotheses with witness and error")
    check("remaining PAH inputs explicit", all(any(term in item.lower() for item in missing) for term in ("source-owned cross-q", "r-488 witness", "generator error", "full-q")), missing, "source law/witness/error/state absent")
    nonclaims = manifest.get("non_claims", [])
    check("non-claim firewall", "full-q" in json.dumps(manifest, ensure_ascii=True).lower() and all(any(term in item.lower() for item in nonclaims) for term in ("physical pre-a", "qft", "toe")), nonclaims, "physical boundaries explicit")
    check("finite R-488 witness remains finite", all(term in r488_text for term in ("q=1", "32,768 states", "(ell_a, ell_d, h_0, h_1)", "417,792 roots total")), r488_text, "finite Q=1 witness")
    manifest_text = MANIFEST.read_text(encoding="utf-8").lower()
    check("no model or fitted-weight language", all(term not in manifest_text for term in ("new hamiltonian", "counterterm", "fit weights", "physical real-time")), True, "forbidden mutations absent")

    compilation = lean_compile(manifest.get("lean", {}).get("toolchain", ""))
    check("independent pinned Lean compile", compilation.get("status") == "PASS", compilation, "PASS")

    failed = [row for row in rows if not row["pass"]]
    payload = {
        "schema": "tect/pah-omc014-witness-stationarity-lean-independent/1.0",
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
        "source_hashes": {"manifest": digest(MANIFEST), "PAH-OMC-014": digest(OMC014), "PAH-OMC-010": digest(OMC010), "R-488": digest(R488), "R-498-manifest": digest(R498), "R499": digest(LEAN)},
        "assumptions": assumptions,
        "missing_assumptions": missing,
        "non_claims": nonclaims,
        "next_question": "Can a source owner supply a positive asymptotic weight for an R-488 witness together with a PAH-specific generator-error bound tending to zero in the declared order?",
    }
    atomic_json(OUTPUT, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}; claim_bearing={payload['claim_bearing']}")
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
