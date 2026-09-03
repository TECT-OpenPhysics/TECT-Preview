#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-003 finite block-refinement result."""

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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-003-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-003-manifest.json"
REGISTRY = ROOT / "verification/lean/registry.json"
LEAN_ROOT = ROOT / "verification/lean"
LEAN_PATH = LEAN_ROOT / "Tect/R482.lean"
RUN_DIR = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-03-pah-omc003-cell-colour-refinement"
)
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        prefix=path.name + ".",
        suffix=".tmp",
        dir=path.parent,
        delete=False,
    ) as stream:
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
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    primary = load(RUN_DIR / "primary.json")
    independent = load(RUN_DIR / "independent.json")
    hostile = load(RUN_DIR / "hostile.json")
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    actual = {
        "PAH-001": digest(PARENT),
        "PAH-OMC-001": digest(FINITE),
        "PAH-OMC-003": digest(CONTRACT),
        "PAH-OMC-003-MANIFEST": digest(MANIFEST),
    }
    expected = {
        "PAH-001": manifest["parent"]["sha256"],
        "PAH-OMC-001": manifest["finite_completion"]["sha256"],
        "PAH-OMC-003": manifest["contract"]["sha256"],
        "PAH-OMC-003-MANIFEST": actual["PAH-OMC-003-MANIFEST"],
    }
    check("source-hashes", actual == expected, actual)
    check("parent-identities", parent.get("packet_id") == "PAH-001" and finite.get("contract_id") == "PAH-OMC-001")
    check("successor-identity", contract.get("contract_id") == "PAH-OMC-003")
    check("parent-pointers", contract.get("parent", {}).get("sha256") == actual["PAH-001"] and contract.get("parent", {}).get("finite_completion_contract", {}).get("sha256") == actual["PAH-OMC-001"])
    check("no-parent-mutation", manifest.get("no_parent_mutation") is True)
    firewall = contract.get("preservation_firewall", {})
    check("preservation-firewall", all(firewall.values()), firewall)
    check("structural-boundary", contract.get("status", {}).get("refinement_family") == "STRUCTURAL_CELL_COLOUR_FIBRE_ONLY" and contract.get("status", {}).get("uniform_limit") == "NOT_ADMITTED")
    check("parent-functional-source", parent.get("functional_or_action", {}).get("name") == "F_rho")

    runs = (primary, independent, hostile)
    check("run-identities", all(item.get("audit_id") == "PAH-CELL-COLOUR-BLOCK-001" and item.get("result_id") == "R-482" and item.get("task_id") == "T-054" for item in runs))
    check("primary-pass", primary.get("verification") == "PASS" and primary.get("verdict") == "STRUCTURAL_EXACT_MICRO_MACRO_COMPATIBILITY")
    check("independent-pass", independent.get("verification") == "PASS" and independent.get("verdict") == "STRUCTURAL_EXACT_MICRO_MACRO_COMPATIBILITY")
    check("hostile-pass", hostile.get("verification") == "PASS" and hostile.get("all_mutations_rejected") is True and hostile.get("mutations_rejected") == hostile.get("mutations_attempted"))
    check("run-source-hashes", all(item.get("source_hashes") == actual for item in runs), [item.get("source_hashes") for item in runs])
    check("no-physical-promotion", all(item.get("claim_bearing") is False and item.get("physical_progress") is False and item.get("stage2_status") == "HOLD_FOR_EVIDENCE" for item in runs))
    check("same-verdict", primary.get("verdict") == independent.get("verdict") == hostile.get("verdict"))

    family = primary.get("family", {})
    rows = independent.get("rows", [])
    check("family-levels", family.get("levels") == [0, 1, 2, 3] and len(rows) == len(family.get("levels", [])))
    check("family-cardinality-growth", all(family["state_cardinalities"][str(level + 1)] > family["state_cardinalities"][str(level)] for level in family.get("levels", [])[:-1]))
    check("exact-zero-defects", family.get("max_exact_defect") == "0" and primary.get("family", {}).get("cumulative_defect") == ["0"] * len(family.get("levels", [])) and independent.get("max_exact_defect") == "0" and independent.get("cumulative_defect") == ["0"] * len(family.get("levels", [])))
    check("independent-row-agreement", all(row.get("max_defect") == "0" for row in rows))
    check(
        "deterministic-pullback-not-gibbs-average",
        primary.get("family", {}).get("observable_lift") == "I_n f(x,h)=f(x)"
        and "deterministic pullback" in contract.get("known_boundaries", {}).get(
            "not_gibbs_average", ""
        ),
    )

    registry = load(REGISTRY)
    entries = {entry.get("path"): entry for entry in registry.get("entrypoints", [])}
    lean_entry = entries.get("verification/lean/Tect/R482.lean", {})
    required = {"normalized_local_replication", "generator_intertwining", "inverse_cocycle_preserves_fibre", "cumulative_zero", "q_family_is_strictly_refining", "structural_firewall"}
    lean_hash = digest(LEAN_PATH)
    check("lean-registry", lean_entry.get("sha256") == lean_hash and required <= set(lean_entry.get("declarations", [])), lean_entry)
    lake = pinned_lake(registry)
    if lake is None:
        lean_ok = False
        lean_detail = "pinned lake executable missing"
    else:
        process = subprocess.run(
            [str(lake), "env", "lean", str(LEAN_PATH.relative_to(LEAN_ROOT))],
            cwd=LEAN_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
            timeout=180,
        )
        lean_detail = (process.stdout + process.stderr).strip()
        lean_ok = process.returncode == 0 and "error:" not in lean_detail.lower()
    check("lean-compile", lean_ok, lean_detail[-2000:])

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "schema": "tect/pah-omc003-cell-colour-refinement-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": "PAH-CELL-COLOUR-BLOCK-001",
        "exploration_id": "EXP-001368",
        "result_id": "R-482",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": actual,
        "verdict": "STRUCTURAL_EXACT_MICRO_MACRO_COMPATIBILITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "lean": {
            "path": "verification/lean/Tect/R482.lean",
            "status": "PASS" if lean_ok else "FAIL",
            "output": lean_detail[-2000:],
            "scope": "Abstract finite normalized replication, generator intertwining, inverse cocycle, cumulative-zero and structural firewall only.",
        },
        "verification_summary": {
            "primary": f"{primary.get('passed', 0)}/{primary.get('assertion_count', 0)}",
            "independent": f"{independent.get('passed', 0)}/{independent.get('assertion_count', 0)}",
            "hostile": f"{hostile.get('mutations_rejected', 0)}/{hostile.get('mutations_attempted', 0)} mutations rejected",
        },
        "non_claims": [
            "The result is a finite structural fibre refinement for a separately versioned successor, not PAH-001 alone.",
            "It is not a geometric lattice subdivision, common infinite-volume dynamics, continuum estimate or ordered limit.",
            "Markov time is not quantum real time, proper time or Lorentzian time.",
            "No physical Pre-A, spacetime, gravity, event-horizon, QFT, Yang--Mills, mass-gap, cosmic-origin or TOE conclusion follows.",
        ],
        "next_question": "Can an owner-approved geometric incidence refinement satisfy the same exact or cumulatively controlled common-core target?",
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    atomic_json(output, payload)
    print(
        "PAH-CELL-COLOUR-BLOCK-001 INTEGRATED "
        f"{payload['verification']} {payload['passed']}/{payload['assertion_count']}; "
        f"Lean={payload['lean']['status']}"
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(args.output)
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
