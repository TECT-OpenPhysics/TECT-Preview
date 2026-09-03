#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-004 geometric incidence result.

The verifier joins the four stored JSON lanes, checks every source pin and
scope firewall, confirms the genuine edge/face incidence change and exact
Q=0 witness, and compiles the pinned Lean cross-check.  It does not infer a
global limit or a physical interpretation from the local theorem.
"""

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
PARENT = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
FINITE = ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json"
REFERENCE = ROOT / "strategy/pa-hyp/PAH-OMC-003-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-004-manifest.json"
REGISTRY = ROOT / "verification/lean/registry.json"
LEAN_ROOT = ROOT / "verification/lean"
LEAN_PATH = LEAN_ROOT / "Tect/R483.lean"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-03-pah-omc004-geometric-incidence"
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"

AUDIT_ID = "PAH-GEOMETRIC-INCIDENCE-LOCAL-001"
EXPLORATION_ID = "EXP-001369"
RESULT_ID = "R-483"
TASK_ID = "T-054"


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
        json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True, default=str)
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
    parent = load(PARENT)
    finite = load(FINITE)
    reference = load(REFERENCE)
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    primary = load(RUN_DIR / "primary.json")
    independent = load(RUN_DIR / "independent.json")
    hostile = load(RUN_DIR / "hostile.json")
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {
        "PAH-001": sha(PARENT),
        "PAH-OMC-001": sha(FINITE),
        "PAH-OMC-003": sha(REFERENCE),
        "PAH-OMC-004": sha(CONTRACT),
        "PAH-OMC-004-MANIFEST": sha(MANIFEST),
    }
    expected = {
        "PAH-001": manifest["parent"]["sha256"],
        "PAH-OMC-001": manifest["finite_completion"]["sha256"],
        "PAH-OMC-003": manifest["reference_only"]["sha256"],
        "PAH-OMC-004": manifest["contract"]["sha256"],
        "PAH-OMC-004-MANIFEST": hashes["PAH-OMC-004-MANIFEST"],
    }
    check("source-hashes", hashes == expected, hashes)
    check("parent-identities", parent.get("packet_id") == "PAH-001" and finite.get("contract_id") == "PAH-OMC-001")
    check("reference-identity", reference.get("contract_id") == "PAH-OMC-003")
    check("successor-identity", contract.get("contract_id") == "PAH-OMC-004")
    check("parent-pointers", contract.get("parent", {}).get("sha256") == hashes["PAH-001"] and contract.get("parent", {}).get("finite_completion_contract", {}).get("sha256") == hashes["PAH-OMC-001"] and contract.get("parent", {}).get("reference_only", {}).get("sha256") == hashes["PAH-OMC-003"])
    check("no-parent-mutation", manifest.get("no_parent_mutation") is True)
    firewall = contract.get("preservation_firewall", {})
    check("preservation-firewall", all(value is True for value in firewall.values()), firewall)
    check("genuine-incidence-status", contract.get("status", {}).get("refinement_family") == "GENUINE_FACE_EDGE_INCIDENCE_STRIP")
    check("local-not-global", contract.get("status", {}).get("finite_block_compatibility") == "LOCAL_EVENTUAL_EXACTNESS_WITH_EXPLICIT_BOUNDARY_DEFECT" and contract.get("status", {}).get("uniform_limit") == "NOT_ADMITTED")
    check("pah-functional-source", parent.get("functional_or_action", {}).get("name") == "F_rho" and "formula" in parent.get("functional_or_action", {}))
    check("pah-dynamics-source", parent.get("dynamics", {}).get("generator") == "(L_rho f)(x)=sum_r m_r(x) exp[-beta(F_rho(r x)-F_rho(x))/2] [f(r x)-f(x)]")

    runs = (primary, independent, hostile)
    check("run-identities", all(item.get("audit_id") == AUDIT_ID and item.get("result_id") == RESULT_ID and item.get("task_id") == TASK_ID for item in runs))
    check("primary-pass", primary.get("verification") == "PASS" and primary.get("verdict") == "LOCAL_COMMON_CORE_GEOMETRIC_COMPATIBILITY")
    check("independent-pass", independent.get("verification") == "PASS" and independent.get("verdict") == "LOCAL_COMMON_CORE_GEOMETRIC_COMPATIBILITY")
    check("hostile-pass", hostile.get("verification") == "PASS" and hostile.get("all_mutations_rejected") is True and hostile.get("mutations_rejected") == hostile.get("mutations_attempted"))
    check("run-source-hashes", all(item.get("source_hashes") == hashes for item in runs))
    check("no-physical-promotion", all(item.get("claim_bearing") is False and item.get("physical_progress") is False and item.get("stage2_status") == "HOLD_FOR_EVIDENCE" for item in runs))
    check("same-verdict", primary.get("verdict") == independent.get("verdict") == hostile.get("verdict"))

    witness = primary.get("witness", {})
    independent_witness = independent.get("witness", {})
    check("local-edge-face-change", witness.get("coarse_incidence", {}).get("edges") == 4 and witness.get("fine_incidence", {}).get("edges") == 5 and witness.get("coarse_incidence", {}).get("faces") == 1 and witness.get("fine_incidence", {}).get("faces") == 2)
    check("new-diagonal-incidence", witness.get("fine_incidence", {}).get("vertices") == witness.get("coarse_incidence", {}).get("vertices") == 4)
    check("exact-witness-deltas", witness.get("delta_F") == {"coarse": "1/8", "fine_even": "1/4", "fine_odd": "-55/36"})
    check("independent-witness-agreement", independent_witness.get("delta_F") == witness.get("delta_F") and independent_witness.get("hidden_diagonal_defect") == "16/9")
    check("mobility-square", witness.get("mobility_square") == "1/2" and independent_witness.get("mobility_square") == "1/2")
    check("boundary-defect-nonzero", witness.get("hidden_diagonal_defect") == "16/9")

    envelope = primary.get("derived_envelope", {})
    independent_envelope = independent.get("derived_envelope", {})
    check("derived-envelope", envelope.get("ranges") == {"onsite_range": "1/8", "edge_range": "1/8", "face_range": "4"} and envelope.get("D_local") == "67/4" and envelope.get("rate_exponent") == "67/8")
    check("independent-envelope-agreement", independent_envelope.get("onsite_range") == "1/8" and independent_envelope.get("edge_range") == "1/8" and independent_envelope.get("face_range") == "4" and independent_envelope.get("D_local") == "67/4")
    rows = primary.get("locality", [])
    check("eventual-zero-rows", [(row.get("support_max_column"), row.get("exact_from_level"), row.get("exact_tail_rule")) for row in rows] == [(0, 1, True), (1, 2, True), (3, 4, True)])
    check("finite-cumulative-rows", [row.get("cumulative_bound") for row in rows] == ["8*exp(67/8)*||f||_infinity", "16*exp(67/8)*||f||_infinity", "32*exp(67/8)*||f||_infinity"])
    check("locality-source-contract", "delta_n(f)=0" in contract.get("compatibility_target", {}).get("local_eventual_exactness", "") and "sum_n delta_n(f)" in contract.get("compatibility_target", {}).get("finite_cumulative_bound", ""))
    check("no-physical-nonclaims", any("No physical Pre-A" in value for value in contract.get("non_claims", [])))

    registry = load(REGISTRY)
    entries = {entry.get("path"): entry for entry in registry.get("entrypoints", [])}
    entry = entries.get("verification/lean/Tect/R483.lean", {})
    required = {"coarse_delta_exact", "fine_even_delta_exact", "fine_odd_delta_exact", "hidden_diagonal_defect_exact", "hidden_diagonal_defect_nonzero", "incidence_edge_change", "incidence_face_change", "aperture_mobility_square", "local_energy_envelope", "local_rate_exponent", "eventual_zero_local_defect", "tail_cumulative_zero", "structural_firewall"}
    lean_hash = sha(LEAN_PATH)
    check("lean-registry", entry.get("sha256") == lean_hash and required <= set(entry.get("declarations", [])), entry)
    lean_source = LEAN_PATH.read_text(encoding="utf-8")
    forbidden = tuple(token for token in ("sorry", "admit", "axiom", "unsafe") if token in lean_source)
    check("lean-forbidden-tokens", not forbidden, forbidden)
    lake = pinned_lake(registry)
    if lake is None:
        lean_ok = False
        lean_detail = "pinned lake executable missing"
    else:
        process = subprocess.run([str(lake), "env", "lean", str(LEAN_PATH.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False, timeout=180)
        lean_detail = (process.stdout + process.stderr).strip()
        lean_ok = process.returncode == 0 and "error:" not in lean_detail.lower()
    check("lean-compile", lean_ok, lean_detail[-2000:])

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "schema": "tect/pah-omc004-geometric-incidence-integrated/1.0",
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
        "verdict": "LOCAL_COMMON_CORE_GEOMETRIC_COMPATIBILITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "lean": {"path": "verification/lean/Tect/R483.lean", "status": "PASS" if lean_ok else "FAIL", "output": lean_detail[-2000:], "scope": "Exact rational incidence witness, local energy envelope arithmetic, eventual-zero tail implication and structural firewall only."},
        "verification_summary": {"primary": f"{primary.get('passed', 0)}/{primary.get('assertion_count', 0)}", "independent": f"{independent.get('passed', 0)}/{independent.get('assertion_count', 0)}", "hostile": f"{hostile.get('mutations_rejected', 0)}/{hostile.get('mutations_attempted', 0)} mutations rejected"},
        "scope": {"dimension": "finite relational two-cell complexes and an anchored combinatorial strip", "model": "PAH-001 + PAH-OMC-001 + PAH-OMC-004; PAH-OMC-003 reference-only", "regulator": "K=2, M_s=M_psi=1, Q=0, epsilon=1/2, beta=nu=1 and displayed PAH couplings", "volume": "finite local carriers and strip levels", "limit": "no cutoff, volume, continuum, physical or observation limit"},
        "non_claims": ["This is a local finite structural successor result, not a global theorem about PAH-001 alone.", "The strip statement is not a volume-, regulator-, source- or phase-uniform estimate and does not close an ordered limit.", "Q=0 is a finite diagnostic sector, not the physical vacuum or Reading-H.", "No physical Pre-A, spacetime, event horizon, gravity, QFT, Yang--Mills, continuum, mass-gap, cosmic-origin or TOE conclusion follows."],
        "next_question": "Can the locality mechanism be extended to a source-authorized nonzero-Q geometric family with a uniform interaction-closure estimate?",
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} INTEGRATED {payload['verification']} {payload['passed']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(args.output)
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
