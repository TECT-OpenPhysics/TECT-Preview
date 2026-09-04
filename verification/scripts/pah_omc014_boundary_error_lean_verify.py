#!/usr/bin/env python3
"""Verify the PAH-OMC-014 R498 conditional boundary-error Lean packet.

This is support evidence only.  It checks source hashes, registry metadata,
boundary-defect semantics, and the pinned Lean compilation.  It does not
instantiate sector weights or a full-Q state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-boundary-error-lean-manifest.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
INTAKE = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-limit-next-evidence-contract-v1.json"
R484_CERT = ROOT / "strategy/pa-hyp/R484-certificate.md"
R484_RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-03-pah-omc004-generator-replay/primary.json"
R490_CERT = ROOT / "strategy/pa-hyp/R490-certificate.md"
LEAN_ROOT = ROOT / "verification/lean"
LEAN_PATH = ROOT / "verification/lean/Tect/R498.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-boundary-error-lean"
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"
AUDIT_ID = "PAH-OMC-014-BOUNDARY-ERROR-LEAN-INTEGRATED-001"
LEAN_HASH = "fa7cb4d28de1ffd19eb9bc2ddc8a89e24b0f93f6f070204d5872063770773ac5"
EXPECTED_DECLARATIONS = [
    "tendsto_add_error",
    "tendsto_zero_of_eventually_zero",
    "add_error_nonnegative",
    "cauchy_of_bulk_boundary",
    "limit_exists_of_bulk_boundary",
    "cauchy_of_eventual_boundary_zero",
    "no_tendsto_zero_of_eventual_floor",
]


def digest(path: Path, *, normalize_lf: bool = False) -> str:
    data = path.read_bytes()
    if normalize_lf:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> Any:
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


def find_lake(toolchain: str) -> Path | None:
    encoded = toolchain.replace("/", "--").replace(":", "---")
    pinned = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        candidate = pinned / name
        if candidate.is_file():
            return candidate
    found = shutil.which("lake")
    return Path(found) if found else None


def compile_lean(registry: dict[str, Any]) -> dict[str, Any]:
    toolchain = registry["toolchain"]["toolchain"]
    lake = find_lake(toolchain)
    command = "lake env lean Tect/R498.lean"
    if lake is None:
        return {"status": "FAIL", "returncode": None, "command": command, "output": "pinned lake executable missing"}
    completed = subprocess.run(
        [str(lake), "env", "lean", "Tect/R498.lean"],
        cwd=LEAN_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        timeout=180,
    )
    output = (completed.stdout + "\n" + completed.stderr).strip()
    return {
        "status": "PASS" if completed.returncode == 0 and "error:" not in output.lower() else "FAIL",
        "returncode": completed.returncode,
        "command": command,
        "output": output[-2000:],
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = read_json(MANIFEST)
    registry = read_json(REGISTRY)
    omc014 = read_json(OMC014)
    intake = read_json(INTAKE)
    r484_text = R484_CERT.read_text(encoding="utf-8")
    r490_text = R490_CERT.read_text(encoding="utf-8")
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})

    parents = manifest.get("parents", {})
    expected_parent_hashes = {
        "PAH-OMC-014": digest(OMC014),
        "PAH-OMC-014-WEIGHT-INTAKE": digest(INTAKE),
        "R-484-CERTIFICATE": digest(R484_CERT),
        "R-484-PRIMARY-RUN": digest(R484_RUN),
        "R-490-CERTIFICATE": digest(R490_CERT),
    }
    for name, actual_hash in expected_parent_hashes.items():
        recorded = parents.get(name, {}).get("sha256")
        check(f"{name} hash", actual_hash == recorded, actual_hash, recorded)

    lean_meta = manifest.get("lean", {})
    registry_item = next(
        (item for item in registry.get("entrypoints", [])
         if item.get("path") == "verification/lean/Tect/R498.lean"),
        None,
    )
    actual_lean_hash = digest(LEAN_PATH, normalize_lf=True) if LEAN_PATH.is_file() else "MISSING"
    check("Lean source hash", actual_lean_hash == LEAN_HASH == lean_meta.get("sha256"), actual_lean_hash, LEAN_HASH)
    check(
        "Lean registry declarations and hash",
        registry_item is not None
        and registry_item.get("sha256") == LEAN_HASH
        and registry_item.get("declarations") == EXPECTED_DECLARATIONS,
        registry_item,
        {"sha256": LEAN_HASH, "declarations": EXPECTED_DECLARATIONS},
    )
    check(
        "Lean toolchain pin",
        lean_meta.get("toolchain") == registry.get("toolchain", {}).get("toolchain"),
        lean_meta.get("toolchain"),
        registry.get("toolchain", {}).get("toolchain"),
    )

    provenance = manifest.get("provenance", {})
    status = manifest.get("status", {})
    check(
        "non-bearing/no parent mutation",
        provenance.get("claim_bearing") is False
        and provenance.get("physical_authority") is False
        and provenance.get("source_law_present") is False
        and provenance.get("model_change") is False
        and provenance.get("parent_mutation") is False
        and status.get("claim_bearing") is False
        and status.get("active_gate_change") is False,
        {"provenance": provenance, "status": status},
        "support-only with no parent mutation",
    )
    check(
        "HOLD verdict retained",
        status.get("verdict") == "HOLD_FOR_EVIDENCE"
        and status.get("classification") == "CONDITIONAL_SUPPORT_ONLY",
        status,
        "CONDITIONAL_SUPPORT_ONLY/HOLD_FOR_EVIDENCE",
    )
    check(
        "source-law absence retained",
        omc014.get("status", {}).get("omega_status") == "NOT_DEFINED"
        and intake.get("status", {}).get("source_law") == "ABSENT_IN_PARENT",
        {"omc014": omc014.get("status"), "intake": intake.get("status")},
        "no source-owned law",
    )

    boundary = manifest.get("boundary_contract", {})
    check("R-484 defect is explicit", boundary.get("r484_defect") == "At the all-zero square-to-split boundary, the exact hidden defect is 16/9.", boundary.get("r484_defect"), "exact 16/9")
    treatment = boundary.get("treatment", "")
    check(
        "boundary is not cancelled",
        all(term in treatment.lower() for term in ("not averaged", "cancelled", "counterterm", "nonnegative")),
        treatment,
        "explicit additive retained boundary",
    )
    check(
        "R-490 is domination-only",
        "C_sw=540" in boundary.get("csw", "")
        and "domination-only" in boundary.get("csw", ""),
        boundary.get("csw"),
        "C_sw=540 domination-only",
    )
    check(
        "source certificates retain boundary",
        "hidden defect" in " ".join(r484_text.lower().split())
        and "16/9" in r484_text
        and "not averaged away" in " ".join(r484_text.lower().split())
        and "C_sw" in r490_text and "540" in r490_text,
        {"r484": ["hidden defect", "16/9", "not averaged away"], "r490": "C_sw=540"},
        "source semantics retained",
    )

    theorem = manifest.get("theorem_contract", {})
    assumptions = theorem.get("assumptions", [])
    missing = theorem.get("not_supplied", [])
    check("theorem assumptions explicit", len(assumptions) == 5 and all(isinstance(item, str) and item.strip() for item in assumptions), assumptions, "five nonempty assumptions")
    required_missing = (
        "No source-owned w_(n,R,Q) law or projective cross-Q kernel.",
        "No proof that the R-484 16/9 defect decays in the declared n and R_max order.",
        "No R-488 nonzero estimate or stationarity passage.",
    )
    check("PAH inputs remain unsupplied", all(item in missing for item in required_missing), missing, list(required_missing))
    non_claims = manifest.get("non_claims", [])
    check(
        "non-claims include full-Q and physical boundaries",
        all(any(term in item for item in non_claims) for term in ("full-Q", "R-484", "physical Pre-A", "QFT", "TOE")),
        non_claims,
        "explicit non-claims",
    )

    forbidden = ("new Hamiltonian", "new counterterm", "fit weights", "physical real-time", "Yang--Mills conclusion")
    full_text = MANIFEST.read_text(encoding="utf-8").lower()
    check(
        "hostile mutation firewall",
        "model_change\": false" in full_text
        and "parent_mutation\": false" in full_text
        and "source_law_present\": false" in full_text
        and all(term not in full_text for term in forbidden),
        forbidden,
        "no model mutation or fitting",
    )

    lean = compile_lean(registry)
    check("R498 pinned Lean compile", lean.get("status") == "PASS", lean, "PASS")

    failed = [row for row in rows if not row["pass"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc014-boundary-error-lean-integrated/1.0",
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
            "manifest": digest(MANIFEST),
            "PAH-OMC-014": digest(OMC014),
            "weight_intake": digest(INTAKE),
            "R-484-certificate": digest(R484_CERT),
            "R-484-primary-run": digest(R484_RUN),
            "R-490-certificate": digest(R490_CERT),
            "R498": actual_lean_hash,
        },
        "assumptions": assumptions,
        "missing_assumptions": missing,
        "non_claims": non_claims,
        "next_question": "Can the source owner provide a nonnegative PAH-specific boundary_error(n) whose limit is zero in the declared n and R_max order, without cancelling the R-484 defect?",
    }
    target = output if output.is_absolute() else ROOT / output
    atomic_json(target, payload)
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