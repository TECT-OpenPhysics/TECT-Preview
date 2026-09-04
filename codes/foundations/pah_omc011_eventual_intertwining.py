#!/usr/bin/env python3
"""Primary PAH-OMC-011 domain/locality audit.

The parent PAH-001 functional and midpoint rates are immutable.  This audit
does not introduce a new carrier or a new transition.  It checks the declared
PAH-OMC-004 neutral projection on the full fixed-Q state spaces and records
the exact charge-loss witness that prevents an all-state lift for Q>0.  The
same calculation also derives the conditional image-locality stabilization
stage N(f) and retains the R-484 boundary defect.
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
BOUNDARY_MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-004-generator-replay-manifest.json"
BOUNDARY_RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-03-pah-omc004-generator-replay/primary.json"
WEIGHT_RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc010-state-weighted-envelope/primary.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-011-eventual-intertwining-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-011-eventual-intertwining-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc011-eventual-intertwining/primary.json"

RESULT_ID = "R-491"
EXPLORATION_ID = "EXP-001457"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-011-EVENTUAL-INTERTWINING-PRIMARY-001"

EXPECTED_HASHES = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-004": "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "PAH-OMC-008": "b103665b9361c6a4b52b791280ce2503e5aeddbffe67a78d08c4c2a45fc8228a",
    "PAH-OMC-010": "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69",
    "PAH-OMC-010-MANIFEST": "97c9ebb3a28f83f93a3b79de527ce0e57b0be346ef6f77d99e59e7b3fa9ea4e3",
    "R-484": "87f5d3ee29b15f57f3e461b4b4064955b5f1ced0ab0bdf2b4763ed0a7ffe3e3e",
    "R-484-MANIFEST": "88a07db1123a229733bdf7ab4fa413d0e6eb903001bc7faa1e44497ae31e9e57",
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
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


def strip_carrier(level: int) -> dict[str, Any]:
    if level < 2:
        raise ValueError("PAH-OMC-010 cofinal strip starts at n=2")
    vertices = tuple((i, j) for i in range(level + 2) for j in (0, 1))
    edges: list[tuple[str, tuple[int, int], tuple[int, int]]] = []
    for i in range(level + 1):
        for j in (0, 1):
            edges.append((f"h{i}{j}", (i, j), (i + 1, j)))
    for i in range(level + 2):
        edges.append((f"v{i}", (i, 0), (i, 1)))
    for i in range(level):
        edges.append((f"d{i}", (i, 0), (i + 1, 1)))
    faces: list[tuple[tuple[str, int], ...]] = []
    for i in range(level):
        faces.extend(
            [
                ((f"h{i}0", 1), (f"v{i + 1}", 1), (f"d{i}", -1)),
                ((f"d{i}", 1), (f"h{i}1", -1), (f"v{i}", -1)),
            ]
        )
    i = level
    faces.append(((f"h{i}0", 1), (f"v{i + 1}", 1), (f"h{i}1", -1), (f"v{i}", -1)))
    return {"vertices": vertices, "edges": tuple(edges), "faces": tuple(faces)}


def q_one_state(level: int, charge_vertex: tuple[int, int]) -> dict[str, Any]:
    carrier = strip_carrier(level)
    vertices = carrier["vertices"]
    if charge_vertex not in vertices:
        raise ValueError("charge vertex is not on the displayed carrier")
    ell = {vertex: int(vertex == charge_vertex) for vertex in vertices}
    return {
        "ell": ell,
        "sum_ell": sum(ell.values()),
        "M_psi": 1,
        "Q": 1,
    }


def state_summary(state: dict[str, Any]) -> dict[str, Any]:
    """Return a JSON-safe witness summary without changing the state."""
    return {
        "ell": {f"{vertex[0]},{vertex[1]}": value for vertex, value in state["ell"].items()},
        "sum_ell": state["sum_ell"],
        "M_psi": state["M_psi"],
        "Q": state["Q"],
    }


def neutral_projection_charge(level: int, state: dict[str, Any]) -> int:
    old_vertices = set(strip_carrier(level)["vertices"])
    return sum(value for vertex, value in state["ell"].items() if vertex in old_vertices)


def stabilization_data(m_f: int) -> dict[str, Any]:
    # m_f is the maximum column in the already-defined PAH interaction closure;
    # m_f=-1 denotes the constant cylinder.  This is a derived support rule.
    n_f = max(2, m_f + 1)
    return {
        "m_f": m_f,
        "N_f": n_f,
        "tested_n": [n_f, n_f + 1],
        "frontier_columns": [[n, n + 1, n + 2] for n in (n_f, n_f + 1)],
        "separated": all(all(column > m_f for column in (n, n + 1, n + 2)) for n in (n_f, n_f + 1)),
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source = load_json(SOURCE)
    geometry = load_json(GEOMETRY)
    start = load_json(START)
    weight = load_json(WEIGHT)
    weight_manifest = load_json(WEIGHT_MANIFEST)
    boundary = load_json(BOUNDARY)
    boundary_manifest = load_json(BOUNDARY_MANIFEST)
    contract = load_json(CONTRACT)
    boundary_run = load_json(BOUNDARY_RUN)
    weight_run = load_json(WEIGHT_RUN)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = None) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {
        "PAH-001": sha(SOURCE),
        "PAH-OMC-004": sha(GEOMETRY),
        "PAH-OMC-008": sha(START),
        "PAH-OMC-010": sha(WEIGHT),
        "PAH-OMC-010-MANIFEST": sha(WEIGHT_MANIFEST),
        "R-484": sha(BOUNDARY),
        "R-484-MANIFEST": sha(BOUNDARY_MANIFEST),
    }
    check("parent-hashes", hashes == EXPECTED_HASHES, {"actual": hashes, "expected": EXPECTED_HASHES})
    check(
        "source-identities",
        source.get("packet_id") == "PAH-001"
        and geometry.get("contract_id") == "PAH-OMC-004"
        and start.get("contract_id") == "PAH-OMC-008"
        and weight.get("contract_id") == "PAH-OMC-010"
        and boundary.get("contract_id") == "PAH-OMC-004-GEN-001",
        {"PAH-001": source.get("packet_id"), "geometry": geometry.get("contract_id"), "start": start.get("contract_id"), "weight": weight.get("contract_id"), "boundary": boundary.get("contract_id")},
    )
    firewall = contract.get("preservation_firewall", {})
    check("preservation-firewall", all(value is True for value in firewall.values()) and weight_manifest.get("no_parent_mutation") is True, firewall)
    check(
        "displayed-functional-and-generator-unchanged",
        source.get("functional_or_action", {}).get("formula", "").startswith("F_rho=sum_v[lambda_s")
        and source.get("dynamics", {}).get("generator", "").startswith("(L_rho f)(x)=sum_r m_r(x)"),
    )
    check(
        "declared-domain-and-algebra",
        "D_(n,Q)" in contract["exact_scope"]["generator_domain"]
        and "ell_v" in contract["exact_scope"]["common_cylinder_algebra"]
        and "H_0" in contract["exact_scope"]["common_cylinder_algebra"]
        and "H_1" in contract["exact_scope"]["common_cylinder_algebra"],
        contract["exact_scope"],
    )
    check(
        "neutral-map-frozen",
        "drops the new column n+2" in contract["exact_scope"]["neutral_refinement"]
        and "d_n" in contract["exact_scope"]["neutral_refinement"]
        and "retains every old geometric coordinate" in contract["exact_scope"]["neutral_refinement"],
        contract["exact_scope"]["neutral_refinement"],
    )
    check(
        "r488-generator-included",
        all(token in start["exact_scope"]["joint_observable"] for token in ("ell_a", "ell_d", "H_0", "H_1")),
        start["exact_scope"]["joint_observable"],
    )

    # The witness uses the existing G_2 -> G_3 strip, not a new carrier.
    n = 2
    fine_level = n + 1
    new_vertex = (n + 2, 0)
    fine_state = q_one_state(fine_level, new_vertex)
    projected_charge = neutral_projection_charge(n, fine_state)
    check("fine-witness-valid-Q-one", fine_state["sum_ell"] == fine_state["Q"] == 1 and new_vertex in strip_carrier(fine_level)["vertices"], state_summary(fine_state))
    check("neutral-projection-charge-loss", projected_charge == 0 and projected_charge != fine_state["Q"], {"fine_Q": fine_state["Q"], "projected_Q": projected_charge, "new_vertex": list(new_vertex)})
    check(
        "projection-not-total-on-full-Q-one",
        projected_charge != fine_state["Q"] and "not a map Omega_(n+1,1)->Omega_(n,1)" in contract["domain_obstruction"]["consequence"],
        contract["domain_obstruction"],
    )

    # The exact image-locality rule is tested at representative closure bounds,
    # including the R-488 first-square closure m_f=1 and the constant cylinder.
    locality_rows = [stabilization_data(m_f) for m_f in (-1, 0, 1, 4, 9)]
    check("explicit-Nf-rule", all(row["N_f"] == max(2, row["m_f"] + 1) for row in locality_rows), locality_rows)
    check("frontier-separated-after-Nf", all(row["separated"] for row in locality_rows), locality_rows)
    check(
        "r488-closure-stage",
        stabilization_data(1)["N_f"] == 2 and stabilization_data(1)["separated"],
        stabilization_data(1),
    )

    boundary_witness = boundary_run.get("boundary_witness", {})
    check(
        "r484-boundary-defect-retained",
        boundary_witness.get("coarse_delta_F") == "1/8"
        and boundary_witness.get("fine_even_delta_F") == "1/4"
        and boundary_witness.get("fine_odd_delta_F") == "-55/36"
        and boundary_witness.get("hidden_diagonal_defect") == "16/9",
        boundary_witness,
    )
    check(
        "boundary-separation-is-not-erasure",
        "outside cl(f) once n>=N(f)" in contract["pre_registered_stabilization"]["boundary_defect"]
        and boundary_witness.get("hidden_diagonal_defect") != "0",
        contract["pre_registered_stabilization"]["boundary_defect"],
    )

    csw = weight_run.get("family", {}).get("C_sw")
    check("csw-540-source-input", csw == 540 and weight_manifest["contract"]["sha256"] == hashes["PAH-OMC-010"], {"C_sw": csw, "role": contract["exact_scope"]["gibbs_norm"]})
    check(
        "csw-not-intertwining-proof",
        "not an intertwining proof" in contract["exact_scope"]["gibbs_norm"]
        and "cannot define" in contract["known_boundaries"][2],
        contract["exact_scope"]["gibbs_norm"],
    )
    check(
        "weak-l2-domain-scope",
        "undefined rather than proved zero" in contract["domain_obstruction"]["weak_l2_scope"]
        and weight_run.get("verification") == "PASS",
        {"weak_l2": contract["domain_obstruction"]["weak_l2_scope"], "R490": weight_run.get("verification")},
    )
    check("no-physical-promotion", contract["status"]["claim_bearing"] is False and any("No physical Pre-A" in item for item in contract["non_claims"]), contract["non_claims"])

    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc011-eventual-intertwining-primary/1.0",
        "run_kind": "primary",
        "audit_id": AUDIT_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": hashes,
        "verdict": "HOLD_FOR_EVIDENCE" if not failed else "HOLD_FOR_EVIDENCE",
        "classification": "IMAGE_LOCALITY_PROVED_GLOBAL_FIXED_Q_COMMON_DOMAIN_MISSING",
        "scope": contract["exact_scope"],
        "stabilization": {
            "rule": contract["pre_registered_stabilization"]["N_of_f"],
            "rows": locality_rows,
            "image_restricted_statement": contract["pre_registered_stabilization"]["conditional_locality_statement"],
        },
        "domain_obstruction": {
            "fine_level": fine_level,
            "old_level": n,
            "new_vertex": list(new_vertex),
            "fine_charge": fine_state["Q"],
            "projected_charge": projected_charge,
            "projection_total": False,
            "exact_scope": contract["domain_obstruction"],
        },
        "boundary_defect": boundary_witness,
        "state_weighted_input": {"C_sw": csw, "role": "domination_only", "intertwining_proved": False},
        "weak_gibbs_l2": {"status": "BLOCKED_UNDEFINED_LIFT_ON_FULL_DOMAIN", "universal_failure_claimed": False},
        "claim_bearing": False,
        "active_gate_change": False,
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "physical_progress": False,
        "scientific_transition": False,
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
        "next_question": contract["single_next_question"],
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict=HOLD_FOR_EVIDENCE; projection_total=False; C_sw={csw}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(args.output)
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
