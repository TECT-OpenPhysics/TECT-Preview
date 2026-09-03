#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-006 matter-cylinder replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc006-matter-cylinder"
PRIMARY = RUN_DIR / "primary.json"
INDEPENDENT = RUN_DIR / "independent.json"
HOSTILE = RUN_DIR / "hostile.json"
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
PREDECESSOR = ROOT / "strategy/pa-hyp/PAH-OMC-005-nonzero-q-generator-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-006-matter-cylinder-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-006-matter-cylinder-manifest.json"
REGISTRY = ROOT / "verification/lean/registry.json"
LEAN = ROOT / "verification/lean/Tect/R486.lean"
LEAN_ROOT = ROOT / "verification/lean"
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"

AUDIT_ID = "PAH-MATTER-CYLINDER-GENERATOR-001"
EXPLORATION_ID = "EXP-001378"
RESULT_ID = "R-486"
TASK_ID = "T-054"
REQUIRED_DECLARATIONS = {
    "nonzero_charge_exact",
    "neutral_inclusion_preserves_charge",
    "matter_observable_is_radial",
    "state_count_exact",
    "stable_endpoint_closure",
    "generator_root_identity",
    "boundary_defect_exact",
    "non_promotion_firewall",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def lake_path(registry: dict[str, Any]) -> Path | None:
    configured = registry.get("toolchain", {}).get("lake_executable")
    candidates = []
    if configured:
        candidates.append(Path(configured))
    candidates.append(Path.home() / ".elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe")
    return next((item for item in candidates if item.exists()), None)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source, geometry, predecessor, contract, manifest = (load(path) for path in (SOURCE, GEOMETRY, PREDECESSOR, CONTRACT, MANIFEST))
    primary, independent, hostile, registry = (load(path) for path in (PRIMARY, INDEPENDENT, HOSTILE, REGISTRY))
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {"PAH-001": sha(SOURCE), "PAH-OMC-004": sha(GEOMETRY), "PAH-OMC-005": sha(PREDECESSOR), "PAH-OMC-006": sha(CONTRACT), "PAH-OMC-006-MANIFEST": sha(MANIFEST)}
    check("source-hashes", all(run.get("source_hashes") == hashes for run in (primary, independent, hostile)), hashes)
    check("manifest-pins", hashes["PAH-001"] == manifest["functional_source"]["sha256"] and hashes["PAH-OMC-004"] == manifest["geometric_source"]["sha256"] and hashes["PAH-OMC-005"] == manifest["predecessor"]["sha256"] and hashes["PAH-OMC-006"] == manifest["contract"]["sha256"])
    check("identity", all(run.get("audit_id") == AUDIT_ID and run.get("exploration_id") == EXPLORATION_ID and run.get("result_id") == RESULT_ID and run.get("task_id") == TASK_ID for run in (primary, independent, hostile)))
    check("primary-independent-pass", primary.get("verification") == "PASS" and independent.get("verification") == "PASS")
    check("hostile-pass", hostile.get("verification") == "PASS" and hostile.get("all_mutations_rejected") is True and hostile.get("mutations_rejected") == hostile.get("mutations_attempted"), hostile.get("mutations"))
    check("finite-firewall", all(run.get("stage2_status") == "HOLD_FOR_EVIDENCE" and run.get("claim_bearing") is False and run.get("physical_progress") is False for run in (primary, independent, hostile)))
    p_identity = primary.get("row_identity", {})
    i_identity = independent.get("row_identity", {})
    check("digest-agreement", p_identity.get("canonical_digest_G2") == i_identity.get("canonical_digest_G2") and p_identity.get("canonical_digest_G3") == i_identity.get("canonical_digest_G3") and p_identity.get("all_equal") is True and i_identity.get("all_equal") is True, {"primary": p_identity, "independent": i_identity})
    expected_states = primary.get("fixture_dimensions", {}).get("state_count")
    expected_roots = primary.get("fixture_dimensions", {}).get("root_count")
    fixture = contract.get("exact_scope", {}).get("fixture", {})
    expected_states_from_contract = (int(fixture.get("M_s", 0)) + 1) ** primary.get("fixture_dimensions", {}).get("aperture_bits", 0) * int(fixture.get("K", 0)) ** primary.get("fixture_dimensions", {}).get("link_bits", 0) * int(fixture.get("K", 0)) ** primary.get("fixture_dimensions", {}).get("phase_bits", 0) * primary.get("fixture_dimensions", {}).get("radial_placements", 0)
    check("finite-domain-count", expected_states == expected_states_from_contract and p_identity.get("state_rows") == expected_states and i_identity.get("state_rows") == expected_states and p_identity.get("root_rows") == expected_roots and expected_roots > expected_states, {"actual": expected_states, "derived_from_contract": expected_states_from_contract, "roots": expected_roots})
    check("matter-cylinder-scope", contract.get("exact_scope", {}).get("observable", "").startswith("The common cylinder is f(x)=ell_a") and p_identity.get("levels") == [2, 3])
    check("nonzero-charge-scope", contract.get("exact_scope", {}).get("fixture", {}).get("Q") == 1 and "nonzero" in primary.get("scope", {}).get("volume", ""))
    check("genuine-incidence", primary.get("carrier_signatures", {}).get("G3", {}).get("edges", 0) > primary.get("carrier_signatures", {}).get("G2", {}).get("edges", 0) and primary.get("carrier_signatures", {}).get("G3", {}).get("faces", 0) > primary.get("carrier_signatures", {}).get("G2", {}).get("faces", 0))
    beta = Fraction(str(fixture.get("beta", "0")))
    check("midpoint-recomputed", all(root.get("rate_exponent") == str(-beta * Fraction(root.get("delta_F")) / 2) for sample in p_identity.get("bounded_samples_G2", []) for root in sample.get("roots", [])))
    check("support-stable", primary.get("support_audit", {}).get("equal") is True and independent.get("boundary_control", {}).get("nonzero_difference") is True)
    control = primary.get("boundary_control", {})
    check("boundary-control-exact", control.get("nonzero_difference") is True and control.get("difference_G2_minus_G1") == "-1", control)
    check("contract-firewall", contract.get("preservation_firewall", {}).get("parent_functional_unchanged") is True and contract.get("preservation_firewall", {}).get("no_new_term") is True and contract.get("preservation_firewall", {}).get("no_rate_fitting") is True)

    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R486.lean"), {})
    check("lean-registry", entry.get("sha256") == normalized_sha(LEAN) and REQUIRED_DECLARATIONS <= set(entry.get("declarations", [])), entry)
    lean_text = LEAN.read_text(encoding="utf-8")
    check("lean-source-firewall", not any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")))
    lake = lake_path(registry)
    if lake is None:
        lean_ok = False
        lean_detail = "pinned lake executable missing"
    else:
        process = subprocess.run([str(lake), "env", "lean", "Tect/R486.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False, timeout=180)
        lean_detail = (process.stdout + process.stderr).strip()
        lean_ok = process.returncode == 0 and "error:" not in lean_detail.lower()
    check("lean-compile", lean_ok, lean_detail[-2000:])
    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc006-matter-cylinder-integrated/1.0",
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
        "verdict": "EXACT_NONZERO_Q_MATTER_DENSITY_CYLINDER_COMPATIBILITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "scope": primary.get("scope", {}),
        "fixture_dimensions": primary.get("fixture_dimensions", {}),
        "verification_summary": {
            "primary": f"{primary.get('passed', 0)}/{primary.get('assertion_count', 0)}",
            "independent": f"{independent.get('passed', 0)}/{independent.get('assertion_count', 0)}",
            "hostile": f"{hostile.get('mutations_rejected', 0)}/{hostile.get('mutations_attempted', 0)} mutations rejected",
            "lean": "PASS" if lean_ok else "FAIL",
        },
        "row_identity": {"levels": [2, 3], "state_rows": p_identity.get("state_rows"), "root_rows": p_identity.get("root_rows"), "canonical_digest_G2": p_identity.get("canonical_digest_G2"), "canonical_digest_G3": p_identity.get("canonical_digest_G3"), "all_equal": p_identity.get("all_equal") is True and i_identity.get("all_equal") is True},
        "boundary_control": control,
        "non_claims": contract.get("non_claims", []),
        "next_question": contract.get("single_next_question"),
    }
    atomic_json(args.output, payload)
    print(f"{AUDIT_ID} INTEGRATED {payload['verification']} {payload['passed']}/{payload['assertion_count']}; Lean={'PASS' if lean_ok else 'FAIL'}; roots={p_identity.get('root_rows')}")
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
