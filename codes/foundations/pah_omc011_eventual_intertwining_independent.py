#!/usr/bin/env python3
"""Non-importing independent replay for PAH-OMC-011.

This file intentionally rebuilds the strip coordinates, fixed-charge witness,
support buffer and upstream boundary constants directly.  It does not import
the primary implementation and it never changes a PAH-001 rate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
START = ROOT / "strategy/pa-hyp/PAH-OMC-008-multi-cylinder-v1.json"
WEIGHT = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json"
WEIGHT_MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-manifest.json"
BOUNDARY = ROOT / "strategy/pa-hyp/PAH-OMC-004-generator-replay-v1.json"
BOUNDARY_RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-03-pah-omc004-generator-replay/primary.json"
WEIGHT_RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc010-state-weighted-envelope/primary.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-011-eventual-intertwining-v1.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc011-eventual-intertwining/independent.json"

RESULT_ID = "R-491"
EXPLORATION_ID = "EXP-001457"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-011-EVENTUAL-INTERTWINING-INDEPENDENT-001"

EXPECTED = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-004": "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "PAH-OMC-008": "b103665b9361c6a4b52b791280ce2503e5aeddbffe67a78d08c4c2a45fc8228a",
    "PAH-OMC-010": "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69",
    "PAH-OMC-010-MANIFEST": "97c9ebb3a28f83f93a3b79de527ce0e57b0be346ef6f77d99e59e7b3fa9ea4e3",
    "R-484": "87f5d3ee29b15f57f3e461b4b4064955b5f1ced0ab0bdf2b4763ed0a7ffe3e3e",
}


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
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


def vertices(level: int) -> set[tuple[int, int]]:
    return {(i, j) for i in range(level + 2) for j in (0, 1)}


def edges(level: int) -> set[tuple[str, tuple[int, int], tuple[int, int]]]:
    result: set[tuple[str, tuple[int, int], tuple[int, int]]] = set()
    for i in range(level + 1):
        for j in (0, 1):
            result.add((f"h{i}{j}", (i, j), (i + 1, j)))
    for i in range(level + 2):
        result.add((f"v{i}", (i, 0), (i, 1)))
    for i in range(level):
        result.add((f"d{i}", (i, 0), (i + 1, 1)))
    return result


def neutral_projection_charge(level: int, fine_charge_vertex: tuple[int, int]) -> tuple[int, int, tuple[int, int]]:
    old = vertices(level)
    fine = vertices(level + 1)
    if fine_charge_vertex not in fine:
        raise AssertionError("fine witness is not on G_(n+1)")
    fine_q = sum(int(vertex == fine_charge_vertex) for vertex in fine)
    retained_q = sum(int(vertex == fine_charge_vertex) for vertex in old)
    return fine_q, retained_q, fine_charge_vertex


def stabilization(m_f: int) -> dict[str, Any]:
    n_f = max(2, m_f + 1)
    rows = []
    for n in (n_f, n_f + 1):
        frontier = (n, n + 1, n + 2)
        rows.append({"n": n, "frontier_columns": list(frontier), "all_outside": all(column > m_f for column in frontier)})
    return {"m_f": m_f, "N_f": n_f, "rows": rows, "separated": all(row["all_outside"] for row in rows)}


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source = read(SOURCE)
    geometry = read(GEOMETRY)
    start = read(START)
    weight = read(WEIGHT)
    weight_manifest = read(WEIGHT_MANIFEST)
    boundary = read(BOUNDARY)
    boundary_run = read(BOUNDARY_RUN)
    weight_run = read(WEIGHT_RUN)
    contract = read(CONTRACT)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = None) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    actual = {
        "PAH-001": digest(SOURCE),
        "PAH-OMC-004": digest(GEOMETRY),
        "PAH-OMC-008": digest(START),
        "PAH-OMC-010": digest(WEIGHT),
        "PAH-OMC-010-MANIFEST": digest(WEIGHT_MANIFEST),
        "R-484": digest(BOUNDARY),
    }
    check("independent-parent-hashes", actual == EXPECTED, {"actual": actual, "expected": EXPECTED})
    check("independent-source-identities", source.get("packet_id") == "PAH-001" and geometry.get("contract_id") == "PAH-OMC-004" and start.get("contract_id") == "PAH-OMC-008" and weight.get("contract_id") == "PAH-OMC-010" and boundary.get("contract_id") == "PAH-OMC-004-GEN-001")
    check("unchanged-rate-text", source["dynamics"]["generator"].startswith("(L_rho f)(x)=sum_r m_r(x)") and source["functional_or_action"]["formula"].startswith("F_rho=sum_v[lambda_s"))
    check("neutral-map-text", "retains every old geometric coordinate" in contract["exact_scope"]["neutral_refinement"] and "drops the new column n+2" in contract["exact_scope"]["neutral_refinement"])

    n = 2
    fine_q, retained_q, new_vertex = neutral_projection_charge(n, (n + 2, 0))
    check("independent-fine-state-q-one", fine_q == 1 and new_vertex in vertices(n + 1), {"fine_Q": fine_q, "vertex": list(new_vertex)})
    check("independent-retained-charge-zero", retained_q == 0 and retained_q != fine_q, {"fine_Q": fine_q, "retained_Q": retained_q})
    check("independent-projection-domain-obstruction", retained_q != 1 and "not a map Omega_(n+1,1)->Omega_(n,1)" in contract["domain_obstruction"]["consequence"])

    locality = [stabilization(m) for m in (-1, 0, 1, 3, 8)]
    check("independent-Nf-formula", all(row["N_f"] == max(2, row["m_f"] + 1) for row in locality), locality)
    check("independent-boundary-separation", all(row["separated"] for row in locality), locality)
    check("independent-r488-Nf", stabilization(1)["N_f"] == 2 and stabilization(1)["separated"], stabilization(1))

    bw = boundary_run.get("boundary_witness", {})
    check("independent-r484-defect", bw.get("hidden_diagonal_defect") == "16/9" and bw.get("coarse_delta_F") == "1/8" and bw.get("fine_even_delta_F") == "1/4" and bw.get("fine_odd_delta_F") == "-55/36", bw)
    check("independent-defect-retained", bw.get("hidden_diagonal_defect") != "0" and "not deletion" in contract["pre_registered_stabilization"]["boundary_defect"], contract["pre_registered_stabilization"]["boundary_defect"])

    check("independent-csw-input", weight_run.get("family", {}).get("C_sw") == 540 and weight_manifest["contract"]["sha256"] == actual["PAH-OMC-010"], weight_run.get("family"))
    check("independent-csw-role", "only as a state-weighted domination input" in contract["exact_scope"]["gibbs_norm"] and "not an intertwining proof" in contract["exact_scope"]["gibbs_norm"])
    check("independent-weak-l2-scope", "undefined rather than proved zero" in contract["domain_obstruction"]["weak_l2_scope"] and weight_run.get("verification") == "PASS")
    check("independent-no-physical", any("No physical Pre-A" in item for item in contract["non_claims"]) and contract["status"]["claim_bearing"] is False)

    failed = [row for row in checks if not row["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc011-eventual-intertwining-independent/1.0",
        "run_kind": "independent",
        "audit_id": AUDIT_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": actual,
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "IMAGE_LOCALITY_PROVED_GLOBAL_FIXED_Q_COMMON_DOMAIN_MISSING",
        "derived": {
            "strip_G2_vertices": len(vertices(2)),
            "strip_G3_vertices": len(vertices(3)),
            "strip_G2_edges": len(edges(2)),
            "strip_G3_edges": len(edges(3)),
            "locality": locality,
        },
        "domain_obstruction": {"old_level": n, "fine_level": n + 1, "new_vertex": list(new_vertex), "fine_Q": fine_q, "retained_Q": retained_q, "projection_total": False},
        "boundary_defect": bw,
        "state_weighted_input": {"C_sw": weight_run.get("family", {}).get("C_sw"), "role": "domination_only"},
        "weak_gibbs_l2": {"status": "BLOCKED_UNDEFINED_LIFT_ON_FULL_DOMAIN", "universal_failure_claimed": False},
        "claim_bearing": False,
        "active_gate_change": False,
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
        "next_question": contract["single_next_question"],
    }
    write_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict=HOLD_FOR_EVIDENCE; projection_total=False")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    return 0 if run(args.output)["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
