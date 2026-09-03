#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-004 generator replay sidecar."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
PARENT = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
SIDECAR = ROOT / "strategy/pa-hyp/PAH-OMC-004-generator-replay-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-004-generator-replay-manifest.json"
REGISTRY = ROOT / "verification/lean/registry.json"
LEAN_ROOT = ROOT / "verification/lean"
LEAN_PATH = LEAN_ROOT / "Tect/R484.lean"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-03-pah-omc004-generator-replay"
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"

AUDIT_ID = "PAH-GENERATOR-REPLAY-001"
EXPLORATION_ID = "EXP-001371"
RESULT_ID = "R-484"
TASK_ID = "T-054"
ROW_KEYS = ("state", "direction", "delta_F", "mobility_square", "delta_s", "delta_indicator_j_a_eq_1", "rate_exponent")
REQUIRED_DECLARATIONS = {
    "generator_row_level_identity",
    "aperture_mobility_square",
    "observable_basis_delta",
    "indicator_basis_delta",
    "state_count_exact",
    "coarse_boundary_delta_exact",
    "fine_even_boundary_delta_exact",
    "fine_odd_boundary_delta_exact",
    "boundary_defect_exact",
    "boundary_defect_nonzero",
    "incidence_edge_change",
    "incidence_face_change",
    "structural_firewall",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", prefix=path.name + ".", suffix=".tmp", dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
        stream.write("\n")
    temporary.replace(path)


def pinned_lake(registry: dict[str, Any]) -> Path | None:
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    root = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        candidate = root / name
        if candidate.is_file():
            return candidate
    found = shutil.which("lake")
    return Path(found) if found else None


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source = load(SOURCE)
    parent = load(PARENT)
    sidecar = load(SIDECAR)
    manifest = load(MANIFEST)
    primary = load(RUN_DIR / "primary.json")
    independent = load(RUN_DIR / "independent.json")
    hostile = load(RUN_DIR / "hostile.json")
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {
        "PAH-001": sha(SOURCE),
        "PAH-OMC-004": sha(PARENT),
        "PAH-OMC-004-GEN-001": sha(SIDECAR),
        "PAH-OMC-004-GEN-MANIFEST": sha(MANIFEST),
    }
    expected_sidecar_parent = sidecar.get("parent", {}).get("sha256")
    check("source-hash", hashes["PAH-001"] == "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37", hashes["PAH-001"])
    check("parent-hash", hashes["PAH-OMC-004"] == "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c" and expected_sidecar_parent == hashes["PAH-OMC-004"], hashes)
    check("sidecar-manifest-pin", manifest.get("sidecar", {}).get("sha256") == hashes["PAH-OMC-004-GEN-001"] and manifest.get("parent", {}).get("sha256") == hashes["PAH-OMC-004"], manifest)
    check("identities", source.get("packet_id") == "PAH-001" and parent.get("contract_id") == "PAH-OMC-004" and sidecar.get("contract_id") == "PAH-OMC-004-GEN-001")
    check("sidecar-scope", sidecar.get("exact_scope", {}).get("levels") == [1, 2] and "Q=0" in sidecar.get("exact_scope", {}).get("state", "") and sidecar.get("provenance", {}).get("physical_authority") is False)
    check("sidecar-generator-contract", "unchanged PAH" in sidecar.get("exact_scope", {}).get("generator", "") and "exp(-beta DeltaF/2)" in sidecar.get("exact_scope", {}).get("generator", ""))
    check("sidecar-lean-path", sidecar.get("lean_entrypoint") == "verification/lean/Tect/R484.lean")
    check("no-parent-mutation", manifest.get("no_parent_mutation") is True and parent.get("preservation_firewall", {}).get("parent_functional_unchanged") is True)

    runs = (primary, independent, hostile)
    check("run-identities", all(item.get("audit_id") == AUDIT_ID and item.get("exploration_id") == EXPLORATION_ID and item.get("result_id") == RESULT_ID and item.get("task_id") == TASK_ID for item in runs))
    check("primary-independent-pass", primary.get("verification") == "PASS" and independent.get("verification") == "PASS")
    check("hostile-pass", hostile.get("verification") == "PASS" and hostile.get("all_mutations_rejected") is True and hostile.get("mutations_rejected") == hostile.get("mutations_attempted"), hostile.get("mutations"))
    check("run-source-hashes", all(item.get("source_hashes") == hashes for item in runs), [item.get("source_hashes") for item in runs])
    check("finite-status", all(item.get("stage2_status") == "HOLD_FOR_EVIDENCE" and item.get("claim_bearing") is False and item.get("physical_progress") is False for item in runs))
    check("same-verdict", primary.get("verdict") == independent.get("verdict") == hostile.get("verdict") == "EXPLICIT_LOCAL_GENERATOR_ROW_EQUALITY")

    p_rows = primary.get("generator_rows", [])
    i_rows = independent.get("generator_rows", [])
    p_tuples = [tuple(item.get(key) for key in ROW_KEYS) for item in p_rows]
    i_tuples = [tuple(item.get(key) for key in ROW_KEYS) for item in i_rows]
    check("row-count", len(p_rows) == len(i_rows) == 512, (len(p_rows), len(i_rows)))
    check("row-levels", all(item.get("level") == 1 for item in p_rows) and all(item.get("level") == 1 for item in i_rows), (p_rows[0].get("level") if p_rows else None, i_rows[0].get("level") if i_rows else None))
    check("primary-independent-row-agreement", p_tuples == i_tuples)
    check("row-identity-declared", primary.get("row_identity", {}).get("levels") == [1, 2] and primary.get("row_identity", {}).get("all_equal") is True and independent.get("row_identity", {}).get("all_equal") is True)
    check("mobility-and-directions", {item.get("mobility_square") for item in p_rows} == {"1/2"} and {item.get("direction") for item in p_rows} == {-1, 1})

    boundary = primary.get("boundary_witness", {})
    check("boundary-values", boundary == {"coarse_delta_F": "1/8", "fine_even_delta_F": "1/4", "fine_odd_delta_F": "-55/36", "hidden_diagonal_defect": "16/9"}, boundary)
    check("independent-boundary-agreement", independent.get("boundary_witness") == boundary)
    check("boundary-not-erased", boundary.get("hidden_diagonal_defect") == "16/9")
    signatures = primary.get("carrier_signatures", {})
    check("incidence-signature-equality", signatures.get("1") == signatures.get("2"))
    check("two-triangle-anchor-closure", len(signatures.get("1", {}).get("incident_faces", [])) == 2 and all(len(face) == 3 for face in signatures.get("1", {}).get("incident_faces", [])))
    check("affected-support", primary.get("affected_terms", {}).get("anchor") == ["onsite:a", "edge:h00", "edge:v0", "edge:d0", "face:0", "face:1"])

    registry = load(REGISTRY)
    entries = {item.get("path"): item for item in registry.get("entrypoints", [])}
    entry = entries.get("verification/lean/Tect/R484.lean", {})
    lean_hash = hashlib.sha256(LEAN_PATH.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()
    check("lean-registry", entry.get("sha256") == lean_hash and REQUIRED_DECLARATIONS <= set(entry.get("declarations", [])), entry)
    lean_text = LEAN_PATH.read_text(encoding="utf-8")
    check("lean-source-firewall", not any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")))
    lake = pinned_lake(registry)
    if lake is None:
        lean_ok = False
        lean_detail = "pinned lake executable missing"
    else:
        process = subprocess.run([str(lake), "env", "lean", "Tect/R484.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False, timeout=180)
        lean_detail = (process.stdout + process.stderr).strip()
        lean_ok = process.returncode == 0 and "error:" not in lean_detail.lower()
    check("lean-compile", lean_ok, lean_detail[-2000:])

    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc004-generator-replay-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": AUDIT_ID,
        "exploration_id": EXPLORATION_ID,
        "result_id": RESULT_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": hashes,
        "verdict": "EXPLICIT_LOCAL_GENERATOR_ROW_EQUALITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "scope": {
            "dimension": "finite relational two-row strip anchor patch",
            "model": "PAH-001 + PAH-OMC-004 + PAH-OMC-004-GEN-001 sidecar",
            "normalization": "finite counting-measure Gibbs midpoint rate",
            "regulator": "K=2, M_s=M_psi=1, Q=0, epsilon=1/2, beta=nu=1",
            "volume": "G_1 and G_2 local patch; no volume exhaustion",
            "limit": "none; n=1,2 finite equality and n=0 boundary witness",
        },
        "verification_summary": {
            "primary": f"{primary.get('passed', 0)}/{primary.get('assertion_count', 0)}",
            "independent": f"{independent.get('passed', 0)}/{independent.get('assertion_count', 0)}",
            "hostile": f"{hostile.get('mutations_rejected', 0)}/{hostile.get('mutations_attempted', 0)} mutations rejected",
            "lean": "PASS" if lean_ok else "FAIL",
        },
        "non_claims": sidecar.get("non_claims", []),
        "next_question": sidecar.get("single_next_question"),
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} INTEGRATED {payload['verification']} {payload['passed']}/{payload['assertion_count']}; Lean={'PASS' if lean_ok else 'FAIL'}; rows={len(p_rows)}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(args.output)
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
