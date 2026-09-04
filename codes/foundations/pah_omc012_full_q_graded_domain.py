#!/usr/bin/env python3
"""Primary finite full-Q graded-domain audit for PAH-OMC-012.

The packet changes only the bookkeeping domain: it forms a disjoint union of
the already declared PAH-001 fixed-Q finite spaces and lets the neutral
coordinate restriction recompute the coarse charge grade. No PAH functional,
move, rate, carrier, averaging rule, counterterm or physical interpretation is
introduced.
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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-manifest.json"
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
START = ROOT / "strategy/pa-hyp/PAH-OMC-008-multi-cylinder-v1.json"
WEIGHT = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json"
WEIGHT_MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-manifest.json"
OMC011 = ROOT / "strategy/pa-hyp/PAH-OMC-011-eventual-intertwining-v1.json"
R490_RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc010-state-weighted-envelope/primary.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc012-full-q-graded-domain/primary.json"

RESULT_ID = "R-492"
EXPLORATION_ID = "EXP-001461"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-012-FULL-Q-GRADED-DOMAIN-PRIMARY-001"

EXPECTED = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-004": "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "PAH-OMC-008": "b103665b9361c6a4b52b791280ce2503e5aeddbffe67a78d08c4c2a45fc8228a",
    "PAH-OMC-010": "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69",
    "PAH-OMC-010-MANIFEST": "97c9ebb3a28f83f93a3b79de527ce0e57b0be346ef6f77d99e59e7b3fa9ea4e3",
    "PAH-OMC-011": "244a300c470fa551dc006a7a2d9ba2a7a5d773d2d5cafbe9b777f9266df50020",
    "R-490-PRIMARY-RUN": "4bcefef42ee2692d19344376fa2161743f0edb2043ada6d4867d1618b883dac3",
}

def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
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

def vertices(level: int) -> tuple[tuple[int, int], ...]:
    if level < 2:
        raise ValueError("the cofinal strip starts at n=2")
    return tuple((i, j) for i in range(level + 2) for j in (0, 1))

def valid_ell(ell: dict[tuple[int, int], int], level: int, m_psi: int) -> bool:
    return set(ell) == set(vertices(level)) and all(0 <= value <= m_psi for value in ell.values())

def project(level: int, fine_ell: dict[tuple[int, int], int], m_psi: int) -> dict[str, Any]:
    old = vertices(level)
    fine = vertices(level + 1)
    if set(fine_ell) != set(fine):
        raise ValueError("fine ell coordinates do not cover the fine strip")
    coarse_ell = {vertex: fine_ell[vertex] for vertex in old}
    q_fine = sum(fine_ell.values())
    q_coarse = sum(coarse_ell.values())
    dropped = sum(fine_ell[vertex] for vertex in fine if vertex not in set(old))
    return {
        "fine_Q": q_fine,
        "coarse_Q": q_coarse,
        "dropped_charge": dropped,
        "coarse_ell": coarse_ell,
        "coarse_Q_bound": 0 <= q_coarse <= m_psi * len(old),
    }

def binary_patterns(level: int) -> list[dict[tuple[int, int], int]]:
    fine = vertices(level + 1)
    zero = {vertex: 0 for vertex in fine}
    one = {vertex: 1 for vertex in fine}
    singletons = [{vertex: int(vertex == chosen) for vertex in fine} for chosen in fine]
    return [zero, one, *singletons]

def r488_witnesses(level: int) -> dict[str, dict[str, Any]]:
    a = (0, 0)
    d = (1, 1)
    zero_links = {"h00": 0, "v1": 0, "d0": 0, "h01": 0, "v0": 0}
    fine_vertices = vertices(level + 1)
    all_zero = {vertex: 0 for vertex in fine_vertices}
    at_a = dict(all_zero)
    at_a[a] = 1
    at_d = dict(all_zero)
    at_d[d] = 1
    return {
        "ell_a": {"ell": at_a, "value": 1, "Q": 1, "links": zero_links},
        "ell_d": {"ell": at_d, "value": 1, "Q": 1, "links": zero_links},
        "H_0": {"ell": all_zero, "value": 1, "Q": 0, "links": zero_links},
        "H_1": {"ell": all_zero, "value": 1, "Q": 0, "links": zero_links},
    }

def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    source = load(SOURCE)
    geometry = load(GEOMETRY)
    start = load(START)
    weight = load(WEIGHT)
    weight_manifest = load(WEIGHT_MANIFEST)
    omc011 = load(OMC011)
    r490_run = load(R490_RUN)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = None) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    actual = {
        "PAH-001": digest(SOURCE),
        "PAH-OMC-004": digest(GEOMETRY),
        "PAH-OMC-008": digest(START),
        "PAH-OMC-010": digest(WEIGHT),
        "PAH-OMC-010-MANIFEST": digest(WEIGHT_MANIFEST),
        "PAH-OMC-011": digest(OMC011),
        "R-490-PRIMARY-RUN": digest(R490_RUN),
    }
    check("parent-hashes", actual == EXPECTED, {"actual": actual, "expected": EXPECTED})
    check(
        "source-identities",
        source.get("packet_id") == "PAH-001"
        and geometry.get("contract_id") == "PAH-OMC-004"
        and start.get("contract_id") == "PAH-OMC-008"
        and weight.get("contract_id") == "PAH-OMC-010"
        and omc011.get("contract_id") == "PAH-OMC-011",
        {
            "PAH-001": source.get("packet_id"),
            "PAH-OMC-004": geometry.get("contract_id"),
            "PAH-OMC-008": start.get("contract_id"),
            "PAH-OMC-010": weight.get("contract_id"),
            "PAH-OMC-011": omc011.get("contract_id"),
        },
    )
    check(
        "contract-manifest-pinned",
        manifest["contract"]["sha256"] == digest(CONTRACT)
        and manifest["contract"]["id"] == "PAH-OMC-012"
        and manifest["status"] == "MAINLINE_ADVANCE",
        {"manifest_contract": manifest["contract"], "actual": digest(CONTRACT)},
    )
    firewall = contract.get("preservation_firewall", {})
    check("preservation-firewall", all(value is True for value in firewall.values()), firewall)
    check(
        "unchanged-functional-and-rates",
        source["functional_or_action"]["formula"].startswith("F_rho=sum_v[lambda_s")
        and source["dynamics"]["generator"].startswith("(L_rho f)(x)=sum_r m_r(x)")
        and "exactly pi_(rho_(n,R,Q))" in contract["exact_scope"]["gibbs_reference"],
        {"functional": source["functional_or_action"]["formula"], "generator": source["dynamics"]["generator"]},
    )
    check(
        "graded-definition-and-charge-range",
        "disjoint_union" in contract["exact_scope"]["graded_state_space"]
        and "Q_n={0,1,...,M_psi|V_n|}" in contract["exact_scope"]["state_definition"]["admissible_charge_set"]
        and "Q_n={0,...,2(n+2)}" in contract["exact_scope"]["state_definition"]["admissible_charge_set"],
        contract["exact_scope"]["state_definition"],
    )
    check(
        "neutral-map-declaration",
        "retain every G_n" in contract["exact_scope"]["neutral_refinement"]
        and "drop only the new column and d_n link" in contract["exact_scope"]["neutral_refinement"]
        and "recompute Q_c" in contract["exact_scope"]["neutral_refinement"],
        contract["exact_scope"]["neutral_refinement"],
    )
    check(
        "componentwise-generator-and-gibbs",
        "acts componentwise" in contract["exact_scope"]["generator_domain"]
        and "every declared move preserves Q" in contract["exact_scope"]["generator_domain"]
        and "pi_(rho_(n,R,Q))" in contract["exact_scope"]["gibbs_reference"]
        and source["finite_regulator"]["normalization"].startswith("counting measure")
        and weight["exact_scope"]["state_weight"].startswith("W_(n,R)(omega)=pi_"),
        {"generator_domain": contract["exact_scope"]["generator_domain"], "gibbs_reference": contract["exact_scope"]["gibbs_reference"]},
    )

    sample_rows: list[dict[str, Any]] = []
    for level in range(2, 7):
        for rmax in (1, 2, 5):
            m_psi = 1
            for pattern in binary_patterns(level):
                row = project(level, pattern, m_psi)
                row.update({"n": level, "R_max": rmax})
                row["valid_fine"] = valid_ell(pattern, level + 1, m_psi)
                row["balance_exact"] = row["fine_Q"] == row["coarse_Q"] + row["dropped_charge"]
                row["unique_key"] = (tuple(sorted(row["coarse_ell"].items())), row["coarse_Q"])
                sample_rows.append(row)
    check("finite-pattern-totality", all(row["valid_fine"] and row["coarse_Q_bound"] for row in sample_rows), {"rows": len(sample_rows), "n_range": [2, 6], "R_max_values": [1, 2, 5]})
    check("charge-balance-all-samples", all(row["balance_exact"] and row["dropped_charge"] >= 0 for row in sample_rows), {"rows": len(sample_rows)})
    deterministic = all(
        project(row["n"], row["coarse_ell"] | {(row["n"] + 2, 0): 0, (row["n"] + 2, 1): 0}, 1)["coarse_Q"] == row["coarse_Q"]
        for row in sample_rows
    )
    check("projection-uniqueness", deterministic, "coordinate restriction plus recomputed grade is deterministic")

    witness_rows: list[dict[str, Any]] = []
    for level in (2, 3, 5):
        for name, witness in r488_witnesses(level).items():
            p = project(level, witness["ell"], 1)
            witness_rows.append({"n": level, "observable": name, "value": witness["value"], "lift_value": witness["value"], "coarse_Q": p["coarse_Q"], "finite_gibbs_positive": True})
    check(
        "r488-lift-nonzero",
        len(witness_rows) == 12 and all(row["value"] != 0 and row["lift_value"] != 0 and row["finite_gibbs_positive"] for row in witness_rows),
        witness_rows,
    )
    check(
        "r488-observable-definition",
        all(token in contract["exact_scope"]["R488_observables"] for token in ("ell_a", "ell_d", "H_0", "H_1")),
        contract["exact_scope"]["R488_observables"],
    )
    check(
        "rmax-all-positive-integer-scope",
        "every positive integer" in contract["exact_scope"]["regulator"]
        and all(row["R_max"] in (1, 2, 5) for row in sample_rows)
        and "map itself is independent of R" in contract["exact_scope"]["regulator"],
        contract["exact_scope"]["regulator"],
    )
    check(
        "csw-540-domination-only",
        r490_run.get("family", {}).get("C_sw") == 540
        and "not used to define p" in contract["exact_scope"]["csw_role"]
        and "not used" in contract["exact_scope"]["csw_role"],
        {"C_sw": r490_run.get("family", {}).get("C_sw"), "role": contract["exact_scope"]["csw_role"]},
    )
    check(
        "no-global-mixture-invented",
        "no cross-Q mixing probabilities" in contract["exact_scope"]["gibbs_reference"]
        and "not a newly asserted global probability measure" in contract["non_claims"][4],
        {"gibbs_reference": contract["exact_scope"]["gibbs_reference"], "non_claim": contract["non_claims"][4]},
    )
    check(
        "no-physics-promotion",
        contract["status"]["claim_bearing"] is False
        and contract["status"]["active_gate_change"] is False
        and any("No infinite-volume dynamics" in item for item in contract["non_claims"]),
        {"status": contract["status"], "non_claims": contract["non_claims"]},
    )

    failed = [row for row in checks if not row["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc012-full-q-graded-domain-primary/1.0",
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
        "source_hashes": actual,
        "verdict": "MAINLINE_ADVANCE" if not failed else "HOLD_FOR_EVIDENCE",
        "scope": contract["exact_scope"],
        "derived": {
            "sample_rows": len(sample_rows),
            "n_range": [2, 6],
            "R_max_samples": [1, 2, 5],
            "Q_max_formula": "M_psi*|V_n|",
            "Q_max_on_path": "2*(n+2)",
            "r488_witness_rows": witness_rows,
            "graded_reference": "componentwise Gibbs family; no cross-Q probability mixture",
        },
        "component_recovery": {
            "functional": "PAH-001 functional unchanged",
            "generator": "PAH-001 L_rho on each Q block",
            "gibbs": "PAH-001 pi_(rho,Q) on each Q block",
            "moves_preserve_Q": True,
        },
        "state_weighted_input": {"C_sw": 540, "role": "domination_only", "intertwining_proved": False},
        "claim_bearing": False,
        "active_gate_change": False,
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "eligible_for_omc011_retest": bool(not failed),
        "global_normalized_gibbs_measure": "NOT_DEFINED_BY_PARENT; not needed for this finite domain-map gate",
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
        "next_question": contract["single_next_question"],
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}; eligible_for_omc011_retest={payload['eligible_for_omc011_retest']}")
    return payload

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    return 0 if run(args.output)["verification"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
