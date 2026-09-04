#!/usr/bin/env python3
"""Verify the non-bearing Lean support packet for PAH-OMC-014.

The checked theorem is conditional: if an external finite sector-weight law is
nonnegative and normalized, a finite mixture of positive normalized component
functionals is positive and normalized.  It deliberately does not supply the
missing PAH full-Q law, projective consistency, a topology, or any limit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-conditional-mixture-lean-manifest.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
INTAKE = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-limit-next-evidence-contract-v1.json"
OMC014_MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-manifest.json"
REGISTRY = ROOT / "verification/lean/registry.json"
LEAN_ROOT = ROOT / "verification/lean"
LEAN_PATH = ROOT / "verification/lean/Tect/R495.lean"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-conditional-mixture-lean"
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"
AUDIT_ID = "PAH-OMC-014-CONDITIONAL-MIXTURE-LEAN-INTEGRATED-001"


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
    return Path(shutil.which("lake")) if shutil.which("lake") else None


def compile_lean(registry: dict[str, Any]) -> dict[str, Any]:
    toolchain = registry["toolchain"]["toolchain"]
    lake = find_lake(toolchain)
    command = "lake env lean Tect/R495.lean"
    if lake is None:
        return {"status": "FAIL", "returncode": None, "command": command, "output": "pinned lake executable missing"}
    completed = subprocess.run(
        [str(lake), "env", "lean", "Tect/R495.lean"],
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
    omc014_manifest = read_json(OMC014_MANIFEST)
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})

    parent_hashes = manifest.get("parents", {})
    check("PAH-OMC-014 parent hash", digest(OMC014) == parent_hashes.get("PAH-OMC-014", {}).get("sha256"), digest(OMC014), parent_hashes.get("PAH-OMC-014", {}).get("sha256"))
    check("weight-intake parent hash", digest(INTAKE) == parent_hashes.get("PAH-OMC-014-WEIGHT-INTAKE", {}).get("sha256"), digest(INTAKE), parent_hashes.get("PAH-OMC-014-WEIGHT-INTAKE", {}).get("sha256"))
    check("OMC-014 manifest parent hash", digest(OMC014_MANIFEST) == parent_hashes.get("PAH-OMC-014-MANIFEST", {}).get("sha256"), digest(OMC014_MANIFEST), parent_hashes.get("PAH-OMC-014-MANIFEST", {}).get("sha256"))

    lean_meta = manifest.get("lean", {})
    declarations = ["mix_nonnegative", "mix_normalized", "mix_probability_pair"]
    registry_item = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R495.lean"), None)
    check("Lean source hash", LEAN_PATH.is_file() and digest(LEAN_PATH, normalize_lf=True) == lean_meta.get("sha256"), digest(LEAN_PATH, normalize_lf=True) if LEAN_PATH.is_file() else "MISSING", lean_meta.get("sha256"))
    check("Lean registry hash/declarations", registry_item is not None and registry_item.get("sha256") == lean_meta.get("sha256") and registry_item.get("declarations") == declarations, registry_item, {"sha256": lean_meta.get("sha256"), "declarations": declarations})
    check("Lean source is UTF-8 LF", LEAN_PATH.is_file() and b"\r" not in LEAN_PATH.read_bytes() and LEAN_PATH.read_bytes().endswith(b"\n"), str(LEAN_PATH), "LF-terminated source")
    check("Lean toolchain pin", lean_meta.get("toolchain") == registry.get("toolchain", {}).get("toolchain"), lean_meta.get("toolchain"), registry.get("toolchain", {}).get("toolchain"))

    provenance = manifest.get("provenance", {})
    status = manifest.get("status", {})
    check("support packet is non-bearing", provenance.get("claim_bearing") is False and provenance.get("physical_authority") is False and provenance.get("source_law_present") is False and status.get("claim_bearing") is False and status.get("active_gate_change") is False, {"provenance": provenance, "status": status}, "non-bearing/no parent mutation")
    check("HOLD verdict retained", status.get("verdict") == "HOLD_FOR_EVIDENCE" and status.get("classification") == "CONDITIONAL_SUPPORT_ONLY", status, "CONDITIONAL_SUPPORT_ONLY/HOLD_FOR_EVIDENCE")
    check("parents remain source-owned", omc014.get("status", {}).get("omega_status") == "NOT_DEFINED" and intake.get("status", {}).get("source_law") == "ABSENT_IN_PARENT", {"omc014": omc014.get("status"), "intake": intake.get("status")}, "no source law")

    theorem = manifest.get("theorem_contract", {})
    assumptions = theorem.get("assumptions", [])
    missing = theorem.get("not_supplied", [])
    check("conditional assumptions are explicit", len(assumptions) == 4 and all(isinstance(item, str) and item.strip() for item in assumptions), assumptions, "four nonempty supplied-law assumptions")
    required_missing = ("No w_(n,R,Q) values or formula.", "No projective consistency identity.", "No Cauchy error or topology.", "No R-488 lower bound or stationarity passage.")
    check("missing full-Q inputs are explicit", all(item in missing for item in required_missing), missing, list(required_missing))
    check("no sector law is instantiated", provenance.get("source_law_present") is False and "No w_(n,R,Q) values or formula." in missing, {"source_law_present": provenance.get("source_law_present"), "not_supplied": missing}, "absent")
    check("no model repair or physical promotion", provenance.get("model_change") is False and status.get("physical_promotion") is False, provenance, "false/false")
    non_claims = manifest.get("non_claims", [])
    check("physical and limit non-claims", all(any(term in item for item in non_claims) for term in ("projective consistency", "infinite-volume", "physical Pre-A", "QFT", "TOE")), non_claims, "explicit non-claims")

    lean = compile_lean(registry)
    check("R495 pinned Lean compile", lean.get("status") == "PASS", lean, "PASS")

    failed = [row for row in rows if not row["pass"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc014-conditional-mixture-lean-integrated/1.0",
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
        "source_hashes": {"manifest": digest(MANIFEST), "PAH-OMC-014": digest(OMC014), "weight_intake": digest(INTAKE), "OMC-014-manifest": digest(OMC014_MANIFEST), "R495": digest(LEAN_PATH, normalize_lf=True)},
        "assumptions": assumptions,
        "missing_assumptions": missing,
        "non_claims": non_claims,
        "next_question": "Can the source owner provide a hash-pinned nonnegative normalized cross-Q sector-weight law (or equivalent projective kernel) with a topology and Cauchy bound?",
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
