#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-005 nonzero-Q generator replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc005-nonzero-q-generator"
PRIMARY = RUN_DIR / "primary.json"
INDEPENDENT = RUN_DIR / "independent.json"
HOSTILE = RUN_DIR / "hostile.json"
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-005-nonzero-q-generator-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-005-nonzero-q-generator-manifest.json"
REGISTRY = ROOT / "verification/lean/registry.json"
LEAN = ROOT / "verification/lean/Tect/R485.lean"
LEAN_ROOT = ROOT / "verification/lean"
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"

AUDIT_ID = "PAH-NONZERO-Q-GENERATOR-001"
EXPLORATION_ID = "EXP-001374"
RESULT_ID = "R-485"
TASK_ID = "T-054"
ROW_KEYS = ("patch_state", "direction", "delta_F", "mobility_square", "delta_s", "delta_indicator_j_a_eq_1", "rate_exponent")
REQUIRED_DECLARATIONS = {
    "nonzero_charge_exact",
    "neutral_inclusion_preserves_charge",
    "aperture_mobility_square",
    "state_count_exact",
    "generator_row_level_identity",
    "anchor_closure_card",
    "incidence_edge_change",
    "incidence_face_change",
    "stable_anchor_closure",
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
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temp, path)
    except BaseException:
        try:
            os.unlink(temp)
        except FileNotFoundError:
            pass
        raise


def row_projection(rows: list[dict[str, Any]]) -> list[tuple[Any, ...]]:
    return [tuple(row.get(key) for key in ROW_KEYS) for row in rows]


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
    source = load(SOURCE)
    geometry = load(GEOMETRY)
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    primary = load(PRIMARY)
    independent = load(INDEPENDENT)
    hostile = load(HOSTILE)
    registry = load(REGISTRY)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {"PAH-001": sha(SOURCE), "PAH-OMC-004": sha(GEOMETRY), "PAH-OMC-005": sha(CONTRACT), "PAH-OMC-005-GEN-MANIFEST": sha(MANIFEST)}
    check("source-hashes", primary.get("source_hashes") == hashes and independent.get("source_hashes") == hashes and hostile.get("source_hashes") == hashes, hashes)
    check("manifest-pins", hashes["PAH-001"] == manifest["functional_source"]["sha256"] and hashes["PAH-OMC-004"] == manifest["geometric_source"]["sha256"] and hashes["PAH-OMC-005"] == manifest["contract"]["sha256"])
    check("identity", all(item.get("audit_id") == AUDIT_ID and item.get("exploration_id") == EXPLORATION_ID and item.get("result_id") == RESULT_ID and item.get("task_id") == TASK_ID for item in (primary, independent, hostile)))
    check("primary-independent-pass", primary.get("verification") == "PASS" and independent.get("verification") == "PASS")
    check("hostile-pass", hostile.get("verification") == "PASS" and hostile.get("all_mutations_rejected") is True and hostile.get("mutations_rejected") == hostile.get("mutations_attempted"), hostile.get("mutations"))
    check("finite-firewall", all(item.get("stage2_status") == "HOLD_FOR_EVIDENCE" and item.get("claim_bearing") is False and item.get("physical_progress") is False for item in (primary, independent, hostile)))
    p_rows = primary.get("generator_rows", [])
    i_rows = independent.get("generator_rows", [])
    dimensions = primary.get("fixture_dimensions", {})
    expected = (dimensions.get("aperture_bits", 0) + 1) ** 1  # checked below from the declared factorization
    expected = (2 ** dimensions.get("aperture_bits", 0)) * (2 ** dimensions.get("link_bits", 0)) * (2 ** dimensions.get("phase_bits", 0)) * dimensions.get("radial_placements", 0)
    check("state-count-factorization", len(p_rows) == expected and len(i_rows) == expected, {"actual": (len(p_rows), len(i_rows)), "expected": expected})
    check("independent-row-agreement", row_projection(p_rows) == row_projection(i_rows))
    check("row-levels", all(row.get("level") == 1 for row in p_rows) and all(row.get("level") == 1 for row in i_rows))
    check("nonzero-charge-fixture", contract.get("exact_scope", {}).get("fixture", {}).get("Q") == 1 and primary.get("scope", {}).get("volume", "").find("nonzero") >= 0)
    check("genuine-geometric-incidence", any(edge[0] == "d0" for edge in primary.get("carrier_signatures", {}).get("1", {}).get("incident_edges", [])) and len(primary.get("carrier_signatures", {}).get("1", {}).get("incident_faces", [])) == 2)
    check("support-stability", primary.get("support_audit", {}).get("changed_terms_equal") is True and primary.get("support_audit", {}).get("nonanchor_terms_unchanged") is True and primary.get("support_audit", {}).get("delta_energy_level_a") == primary.get("support_audit", {}).get("delta_energy_level_b"))
    check("midpoint-rate-recomputed", all(row.get("mobility_square") == "1/2" for row in p_rows) and all(row.get("rate_exponent") == str(-__import__("fractions").Fraction(row.get("delta_F")) / 2) for row in p_rows))
    check("contract-firewall", contract.get("preservation_firewall", {}).get("parent_functional_unchanged") is True and contract.get("preservation_firewall", {}).get("no_new_term") is True and contract.get("preservation_firewall", {}).get("no_rate_fitting") is True)

    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R485.lean"), {})
    check("lean-registry", entry.get("sha256") == normalized_sha(LEAN) and REQUIRED_DECLARATIONS <= set(entry.get("declarations", [])), entry)
    lean_text = LEAN.read_text(encoding="utf-8")
    check("lean-source-firewall", not any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")))
    lake = lake_path(registry)
    if lake is None:
        lean_ok = False
        lean_detail = "pinned lake executable missing"
    else:
        process = subprocess.run([str(lake), "env", "lean", "Tect/R485.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False, timeout=180)
        lean_detail = (process.stdout + process.stderr).strip()
        lean_ok = process.returncode == 0 and "error:" not in lean_detail.lower()
    check("lean-compile", lean_ok, lean_detail[-2000:])

    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc005-nonzero-q-generator-integrated/1.0",
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
        "verdict": "EXACT_NONZERO_Q_ANCHOR_GENERATOR_COMPATIBILITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "scope": primary.get("scope", {}),
        "fixture_dimensions": dimensions,
        "verification_summary": {
            "primary": f"{primary.get('passed', 0)}/{primary.get('assertion_count', 0)}",
            "independent": f"{independent.get('passed', 0)}/{independent.get('assertion_count', 0)}",
            "hostile": f"{hostile.get('mutations_rejected', 0)}/{hostile.get('mutations_attempted', 0)} mutations rejected",
            "lean": "PASS" if lean_ok else "FAIL",
        },
        "row_identity": {"rows_compared": len(p_rows), "all_equal": row_projection(p_rows) == row_projection(i_rows), "exact_tuple": list(ROW_KEYS)},
        "non_claims": contract.get("non_claims", []),
        "next_question": contract.get("single_next_question"),
    }
    atomic_json(args.output, payload)
    print(f"{AUDIT_ID} INTEGRATED {payload['verification']} {payload['passed']}/{payload['assertion_count']}; Lean={'PASS' if lean_ok else 'FAIL'}; rows={len(p_rows)}")
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
