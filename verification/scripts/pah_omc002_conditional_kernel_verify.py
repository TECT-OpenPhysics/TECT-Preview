#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-002 conditional-kernel audit."""

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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-002-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-002-manifest.json"
REGISTRY = ROOT / "verification/lean/registry.json"
LEAN_ROOT = ROOT / "verification/lean"
LEAN_PATH = LEAN_ROOT / "Tect/R480.lean"
RUN_DIR = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-pah-omc002-conditional-kernel"
)
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    manifest = load(MANIFEST)
    contract = load(CONTRACT)
    primary = load(RUN_DIR / "primary.json")
    independent = load(RUN_DIR / "independent.json")
    hostile = load(RUN_DIR / "hostile.json")
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    actual = {
        "PAH-001": digest(PARENT),
        "PAH-OMC-001": digest(FINITE),
        "PAH-OMC-002": digest(CONTRACT),
        "PAH-OMC-002-MANIFEST": digest(MANIFEST),
    }
    expected = {
        "PAH-001": manifest["parent"]["sha256"],
        "PAH-OMC-001": manifest["finite_completion"]["sha256"],
        "PAH-OMC-002": manifest["contract"]["sha256"],
        "PAH-OMC-002-MANIFEST": actual["PAH-OMC-002-MANIFEST"],
    }
    check("source-hashes", actual == expected, actual)
    check("primary-source-hashes", primary.get("source_hashes") == actual, primary.get("source_hashes"))
    check("independent-source-hashes", independent.get("source_hashes") == actual, independent.get("source_hashes"))
    check("hostile-source-hashes", hostile.get("source_hashes") == actual, hostile.get("source_hashes"))
    check("primary-pass", primary.get("verification") == "PASS" and primary.get("verdict") == "ROUTE_LOCAL_CONDITIONAL_PROJECTED_INTERTWINING_FAIL")
    check("independent-pass", independent.get("verification") == "PASS" and independent.get("verdict") == "ROUTE_LOCAL_CONDITIONAL_PROJECTED_INTERTWINING_FAIL")
    check("hostile-pass", hostile.get("verification") == "PASS" and hostile.get("all_mutations_rejected") is True and hostile.get("mutations_rejected") == hostile.get("mutations_attempted"), hostile.get("mutations"))
    check("same-verdict", primary.get("verdict") == independent.get("verdict") == hostile.get("verdict"))
    check("same-result-and-task", all(item.get("result_id") == "R-480" and item.get("task_id") == "T-054" for item in (primary, independent, hostile)))
    check("stage2-held", all(item.get("stage2_status") == "HOLD_FOR_EVIDENCE" for item in (primary, independent, hostile)))
    check("claim-and-physical-firewall", all(item.get("claim_bearing") is False and item.get("physical_progress") is False for item in (primary, independent, hostile)))

    pw = primary.get("witness", {})
    iw = independent.get("derivation", {})
    check("primary-witness-exact", pw.get("coarse_delta_F") == "0" and pw.get("fine_delta_F_by_hidden_j_z") == {"0": "1/8", "1": "-1/8"} and pw.get("fibre_energy_by_hidden_j_z") == {"0": "3/8", "1": "3/8"}, pw)
    check("independent-witness-exact", iw.get("coarse_delta_F") == "0" and iw.get("hidden_delta_F") == {"0": "1/8", "1": "-1/8"}, iw)
    check("positive-defect-witness", "(exp(-1/16)+exp(1/16))/2 - 1 > 0" in pw.get("normalized_defect_exact", "") and pw.get("numeric_defect_observed", 0) > 0, pw)
    check("no-strong-substitution", contract.get("compatibility_targets", {}).get("strong_mainline") != contract.get("compatibility_targets", {}).get("conditional_projected"))

    registry = load(REGISTRY)
    entries = {entry.get("path"): entry for entry in registry.get("entrypoints", [])}
    expected_lean_hash = "91454ec24fbd365e5ce44cf8399254148b7c6659d18da78017042af1bc06175f"
    lean_entry = entries.get("verification/lean/Tect/R480.lean", {})
    required_declarations = {
        "aperture_grid_values",
        "hidden_edge_increment_low",
        "hidden_edge_increment_high",
        "hidden_increment_difference",
        "coarse_increment_cancellation",
        "conditional_factor_gt_one",
        "witness_factor_gt_one",
        "witness_normalized_defect_positive",
        "witness_mobility_square",
        "conditional_defect_keeps_stage2_closed",
    }
    check("lean-registry", lean_entry.get("sha256") == expected_lean_hash and required_declarations <= set(lean_entry.get("declarations", [])), lean_entry)
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
        "schema": "tect/pah-omc002-conditional-kernel-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": "PAH-COND-GIBBS-BLOCK-001",
        "exploration_id": "EXP-001367",
        "result_id": "R-480",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": actual,
        "verdict": "ROUTE_LOCAL_CONDITIONAL_PROJECTED_INTERTWINING_FAIL",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "lean": {
            "path": "verification/lean/Tect/R480.lean",
            "status": "PASS" if lean_ok else "FAIL",
            "output": lean_detail[-2000:],
            "scope": "Exact aperture increments, conditional exponential defect positivity, and stage-2 hold firewall only.",
        },
        "non_claims": [
            "This integrated result is a route-local finite defect for the PAH-OMC-002 projected diagnostic.",
            "It is not a global PAH-001 no-go and does not admit any refinement family or uniform limit.",
            "No physical Pre-A, spacetime, gravity, event-horizon, continuum, QFT, Yang--Mills, mass-gap or TOE conclusion follows.",
            "No Q3LOCK result is imported; Markov time remains external stochastic time.",
        ],
        "next_question": "Can an owner-authorized block kernel other than the exact PAH-OMC-002 Gibbs fibre average satisfy the projected identity without changing the strong target or adding a new functional term?",
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    atomic_json(output, payload)
    print(
        "PAH-COND-GIBBS-BLOCK-001 INTEGRATED "
        f"{payload['verification']} {payload['passed']}/{payload['assertion_count']}; "
        f"Lean={payload['lean']['status']}; verdict={payload['verdict']}"
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
