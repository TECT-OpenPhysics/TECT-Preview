#!/usr/bin/env python3
"""Independent reconstruction audit for PAH-OMC-014 R498.

The script does not import the integrated verifier.  It independently checks
the pinned parents, R-484/R-490 semantics, R498 declarations, and compilation.
It remains conditional support only.
"""
from __future__ import annotations

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
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-boundary-error-lean-manifest.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
INTAKE = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-limit-next-evidence-contract-v1.json"
R484 = ROOT / "strategy/pa-hyp/R484-certificate.md"
R484_RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-03-pah-omc004-generator-replay/primary.json"
R490 = ROOT / "strategy/pa-hyp/R490-certificate.md"
LEAN = ROOT / "verification/lean/Tect/R498.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
LEAN_ROOT = ROOT / "verification/lean"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-boundary-error-lean/independent.json"
AUDIT_ID = "PAH-OMC-014-BOUNDARY-ERROR-LEAN-INDEPENDENT-001"
LEAN_HASH = "fa7cb4d28de1ffd19eb9bc2ddc8a89e24b0f93f6f070204d5872063770773ac5"
DECLARATIONS = [
    "tendsto_add_error",
    "tendsto_zero_of_eventually_zero",
    "add_error_nonnegative",
    "cauchy_of_bulk_boundary",
    "limit_exists_of_bulk_boundary",
    "cauchy_of_eventual_boundary_zero",
    "no_tendsto_zero_of_eventual_floor",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def lake_path(toolchain: str) -> Path | None:
    encoded = toolchain.replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        path = candidate / name
        if path.is_file():
            return path
    found = shutil.which("lake")
    return Path(found) if found else None


def compile_lean(toolchain: str) -> dict[str, Any]:
    lake = lake_path(toolchain)
    command = "lake env lean Tect/R498.lean"
    if lake is None:
        return {"status": "FAIL", "command": command, "returncode": None, "output": "pinned lake missing"}
    result = subprocess.run(
        [str(lake), "env", "lean", "Tect/R498.lean"],
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
        "command": command,
        "returncode": result.returncode,
        "output": output[-2000:],
    }


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    omc014 = json.loads(OMC014.read_text(encoding="utf-8"))
    intake = json.loads(INTAKE.read_text(encoding="utf-8"))
    r484_text = " ".join(R484.read_text(encoding="utf-8").lower().split())
    r490_text = " ".join(R490.read_text(encoding="utf-8").lower().split())
    lean_text = LEAN.read_text(encoding="utf-8")
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    parents = manifest.get("parents", {})
    source_paths = {
        "PAH-OMC-014": OMC014,
        "PAH-OMC-014-WEIGHT-INTAKE": INTAKE,
        "R-484-CERTIFICATE": R484,
        "R-484-PRIMARY-RUN": R484_RUN,
        "R-490-CERTIFICATE": R490,
    }
    for key, path in source_paths.items():
        check(f"{key} digest", sha(path) == parents.get(key, {}).get("sha256"), sha(path), parents.get(key, {}).get("sha256"))

    lean_meta = manifest.get("lean", {})
    item = next((x for x in registry.get("entrypoints", []) if x.get("path") == "verification/lean/Tect/R498.lean"), None)
    check("R498 LF and digest", b"\r" not in LEAN.read_bytes() and LEAN.read_bytes().endswith(b"\n") and sha(LEAN) == LEAN_HASH, {"sha": sha(LEAN), "lf": b"\r" not in LEAN.read_bytes(), "final_lf": LEAN.read_bytes().endswith(b"\n")}, LEAN_HASH)
    check("registry declaration list", item is not None and item.get("sha256") == LEAN_HASH and item.get("declarations") == DECLARATIONS, item, {"sha256": LEAN_HASH, "declarations": DECLARATIONS})
    declarations = re.findall(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)", lean_text)
    check("source declares every theorem", all(name in declarations for name in DECLARATIONS), declarations, DECLARATIONS)
    check("parents retain HOLD/no law", omc014.get("status", {}).get("omega_status") == "NOT_DEFINED" and intake.get("status", {}).get("source_law") == "ABSENT_IN_PARENT", {"omega": omc014.get("status", {}).get("omega_status"), "law": intake.get("status", {}).get("source_law")}, "NOT_DEFINED/ABSENT_IN_PARENT")
    status = manifest.get("status", {})
    provenance = manifest.get("provenance", {})
    check("support-only status", status.get("verdict") == "HOLD_FOR_EVIDENCE" and status.get("claim_bearing") is False and provenance.get("source_law_present") is False and provenance.get("model_change") is False and provenance.get("parent_mutation") is False, {"status": status, "provenance": provenance}, "HOLD/non-bearing/no-law/no-mutation")
    boundary = manifest.get("boundary_contract", {})
    check("R-484 defect retained", "16/9" in boundary.get("r484_defect", "") and "not averaged" in " ".join(boundary.get("treatment", "").lower().split()), boundary, "16/9 retained")
    check("R-490 domination-only", "c_sw" in r490_text and "540" in r490_text and "not a claim that the generators already intertwine" in r490_text, r490_text[r490_text.find("c_sw"):r490_text.find("c_sw") + 120], "C_sw=540 domination")
    check("source wording retained", "hidden defect" in r484_text and "16/9" in r484_text and "not averaged away" in r484_text, True, "R-484 source semantics")
    check("no fitted or physical promotion", all(term not in MANIFEST.read_text(encoding="utf-8").lower() for term in ("fit weights", "new hamiltonian", "physical real-time", "yang--mills conclusion")), True, "forbidden mutations absent")
    lean = compile_lean(lean_meta.get("toolchain", ""))
    check("independent Lean compilation", lean.get("status") == "PASS", lean, "PASS")

    failed = [row for row in rows if not row["pass"]]
    payload = {
        "schema": "tect/pah-omc014-boundary-error-lean-independent/1.0",
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
        "lean": lean,
        "source_hashes": {"manifest": sha(MANIFEST), "PAH-OMC-014": sha(OMC014), "weight_intake": sha(INTAKE), "R-484-certificate": sha(R484), "R-484-primary-run": sha(R484_RUN), "R-490-certificate": sha(R490), "R498": sha(LEAN)},
        "non_claims": manifest.get("non_claims", []),
        "next_question": "Can a source owner provide boundary_error(n,R,f) with a proof of convergence to zero in the declared order, without cancelling the R-484 defect?",
    }
    atomic_json(OUTPUT, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}")
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())