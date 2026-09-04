#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-014 R499 conditional Lean bridge.

The packet proves only abstract finite-mixture positivity and real-sequence
error-to-zero implications.  It does not instantiate a PAH full-Q state.
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
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-witness-stationarity-lean-manifest.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
OMC010 = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json"
R488 = ROOT / "strategy/pa-hyp/R488-certificate.md"
R498_MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-boundary-error-lean-manifest.json"
LEAN = ROOT / "verification/lean/Tect/R499.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
LEAN_ROOT = ROOT / "verification/lean"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-witness-stationarity-lean"
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"
AUDIT_ID = "PAH-OMC-014-WITNESS-STATIONARITY-LEAN-INTEGRATED-001"
TOOLCHAIN = "leanprover/lean4:v4.32.1"
DECLARATIONS = [
    "mix_strictly_positive_of_witness",
    "stationarity_limit_of_abs_error",
    "stationarity_limit_of_eventual_zero",
]
PARENT_PINS = {
    "PAH-OMC-014": (
        "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json",
        "1389bf64b2f26f267aa35bdfbee59cced2d16d8a5dcefd8e34a3deabb41d31b0",
    ),
    "PAH-OMC-010": (
        "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json",
        "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69",
    ),
    "R-488-CERTIFICATE": (
        "strategy/pa-hyp/R488-certificate.md",
        "95af523293779dcd8b3ecdd676e7eb57d33eed53c0903676853a09e885cdbcb6",
    ),
    "R-498-MANIFEST": (
        "strategy/pa-hyp/PAH-OMC-014-boundary-error-lean-manifest.json",
        "efbdd3e2f430f074fef33677f7481d1096c0dd1b4ed4fdd3f3c7732d5e244458",
    ),
}
LEAN_PIN = "5be7c07c6ff6ac32c2bdbd91ebfc4f4c71e859aefc558a9db41c65f6525819e0"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def lake_path(toolchain: str) -> Path | None:
    encoded = toolchain.replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        path = candidate / name
        if path.is_file():
            return path
    found = shutil.which("lake")
    return Path(found) if found else None


def compile_lean() -> dict[str, Any]:
    lake = lake_path(TOOLCHAIN)
    command = "lake env lean Tect/R499.lean"
    if lake is None:
        return {"status": "FAIL", "returncode": None, "command": command, "output": "pinned lake executable missing"}
    result = subprocess.run(
        [str(lake), "env", "lean", "Tect/R499.lean"],
        cwd=LEAN_ROOT,
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
        "command": command,
        "output": output[-2000:],
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = load_json(MANIFEST)
    registry = load_json(REGISTRY)
    omc014 = load_json(OMC014)
    omc010 = load_json(OMC010)
    r488_text = " ".join(R488.read_text(encoding="utf-8").lower().split())
    source_text = LEAN.read_text(encoding="utf-8")
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    parents = manifest.get("parents", {})
    for key, (relative, expected_hash) in PARENT_PINS.items():
        record = parents.get(key, {})
        path_ok = record.get("path") == relative
        path = ROOT / relative
        exists = path.is_file()
        actual_hash = sha(path) if exists else "MISSING"
        check(f"{key} locator", path_ok, record.get("path"), relative)
        check(f"{key} hash", exists and actual_hash == expected_hash == record.get("sha256"), actual_hash, expected_hash)

    lean_meta = manifest.get("lean", {})
    registry_item = next(
        (item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R499.lean"),
        None,
    )
    lean_bytes = LEAN.read_bytes()
    actual_lean = sha(LEAN) if LEAN.is_file() else "MISSING"
    check("R499 LF and final newline", b"\r" not in lean_bytes and lean_bytes.endswith(b"\n"), {"lf": b"\r" not in lean_bytes, "final_newline": lean_bytes.endswith(b"\n")}, True)
    check("R499 source hash", actual_lean == LEAN_PIN == lean_meta.get("sha256"), actual_lean, LEAN_PIN)
    check(
        "R499 registry hash/declarations",
        registry_item is not None
        and registry_item.get("sha256") == LEAN_PIN
        and registry_item.get("declarations") == DECLARATIONS,
        registry_item,
        {"sha256": LEAN_PIN, "declarations": DECLARATIONS},
    )
    declared = re.findall(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)", source_text)
    check("R499 source declaration list", all(name in declared for name in DECLARATIONS), declared, DECLARATIONS)
    check("toolchain is pinned", lean_meta.get("toolchain") == TOOLCHAIN and registry.get("toolchain", {}).get("toolchain") == TOOLCHAIN, {"manifest": lean_meta.get("toolchain"), "registry": registry.get("toolchain", {}).get("toolchain")}, TOOLCHAIN)
    check("Lean forbidden tokens absent", not any(re.search(rf"\b{token}\b", source_text) for token in ("sorry", "admit", "axiom", "unsafe")), True, "no sorry/admit/axiom/unsafe")

    provenance = manifest.get("provenance", {})
    status = manifest.get("status", {})
    check(
        "conditional non-bearing firewall",
        provenance.get("external_source") is False
        and provenance.get("source_law_present") is False
        and provenance.get("claim_bearing") is False
        and provenance.get("physical_authority") is False
        and provenance.get("model_change") is False
        and provenance.get("parent_mutation") is False
        and status.get("claim_bearing") is False
        and status.get("active_gate_change") is False
        and status.get("physical_promotion") is False,
        {"provenance": provenance, "status": status},
        "research-owned conditional support only",
    )
    check("HOLD status retained", status.get("classification") == "CONDITIONAL_SUPPORT_ONLY" and status.get("verdict") == "HOLD_FOR_EVIDENCE", status, "CONDITIONAL_SUPPORT_ONLY/HOLD_FOR_EVIDENCE")
    check("parent OMC-014 remains open", omc014.get("status", {}).get("omega_status") == "NOT_DEFINED" and omc014.get("status", {}).get("weak_cylinder_limit") == "NOT_TESTABLE", omc014.get("status"), "NOT_DEFINED/NOT_TESTABLE")
    check("parent OMC-010 remains pending", omc010.get("status", {}).get("uniform_interaction_envelope") == "PENDING_VERIFICATION" and omc010.get("status", {}).get("physical_promotion") is False, omc010.get("status"), "pending/nonphysical")

    theorem = manifest.get("theorem_contract", {})
    assumptions = theorem.get("assumptions", [])
    check("five explicit hypotheses", len(assumptions) == 5 and all(isinstance(item, str) and item.strip() for item in assumptions), assumptions, "five nonempty assumptions")
    required_phrases = ("witness sector", "absolute error bound", "nonnegative")
    check("hypotheses name witness and error", all(any(phrase in item.lower() for item in assumptions) for phrase in required_phrases), assumptions, required_phrases)
    missing = theorem.get("not_supplied", [])
    missing_phrases = ("source-owned cross-Q", "R-488 witness", "generator error", "full-Q")
    check("missing PAH inputs are explicit", all(any(phrase.lower() in item.lower() for item in missing) for phrase in missing_phrases), missing, missing_phrases)
    non_claims = manifest.get("non_claims", [])
    nonclaim_terms = ("full-Q", "physical Pre-A", "QFT", "TOE")
    check("physical non-claims are explicit", "full-q" in json.dumps(manifest, ensure_ascii=True).lower() and all(any(term.lower() in item.lower() for item in non_claims) for term in ("physical pre-a", "qft", "toe")), non_claims, nonclaim_terms)

    check("R-488 finite witness is scoped", all(term in r488_text for term in ("q=1", "32,768 states", "(ell_a, ell_d, h_0, h_1)", "417,792 roots total")), r488_text, "Q=1 witness tuple and finite counts")
    manifest_text = MANIFEST.read_text(encoding="utf-8").lower()
    check("R-488 witness is not promoted", "does not prove" in manifest_text or "not a full-q state" in manifest_text, True, "conditional wording")
    theorem_text = json.dumps(theorem, ensure_ascii=True).lower()
    check("no law/weight fitting or model mutation", all(term not in theorem_text for term in ("fit weights", "new hamiltonian", "counterterm", "physical real-time")), theorem_text, "abstract bridge only")

    lean = compile_lean()
    check("R499 pinned Lean compilation", lean.get("status") == "PASS", lean, "PASS")
    failed = [row for row in rows if not row["pass"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc014-witness-stationarity-lean-integrated/1.0",
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
        "source_hashes": {
            "manifest": sha(MANIFEST),
            "PAH-OMC-014": sha(OMC014),
            "PAH-OMC-010": sha(OMC010),
            "R-488": sha(R488),
            "R-498-manifest": sha(R498_MANIFEST),
            "R499": actual_lean,
        },
        "assumptions": assumptions,
        "missing_assumptions": missing,
        "non_claims": non_claims,
        "next_question": "Can the source owner provide a positive asymptotic weight for an R-488 witness and a PAH-specific generator-error bound tending to zero in the declared order?",
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
