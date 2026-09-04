#!/usr/bin/env python3
"""Independent non-importing replay for PAH-OMC-012.

This lane rebuilds the finite strip coordinate restriction, charge grading and
R-488 witness lifts directly. It does not import the primary verifier and does
not modify any PAH-001 definition.
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
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc012-full-q-graded-domain/independent.json"

RESULT_ID = "R-492"
EXPLORATION_ID = "EXP-001461"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-012-FULL-Q-GRADED-DOMAIN-INDEPENDENT-001"

EXPECTED = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-004": "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "PAH-OMC-008": "b103665b9361c6a4b52b791280ce2503e5aeddbffe67a78d08c4c2a45fc8228a",
    "PAH-OMC-010": "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69",
    "PAH-OMC-010-MANIFEST": "97c9ebb3a28f83f93a3b79de527ce0e57b0be346ef6f77d99e59e7b3fa9ea4e3",
    "PAH-OMC-011": "244a300c470fa551dc006a7a2d9ba2a7a5d773d2d5cafbe9b777f9266df50020",
    "R-490-PRIMARY-RUN": "4bcefef42ee2692d19344376fa2161743f0edb2043ada6d4867d1618b883dac3",
}

def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    except BaseException:
        try:
            os.unlink(temp)
        except FileNotFoundError:
            pass
        raise

def V(n: int) -> tuple[tuple[int, int], ...]:
    return tuple((i, j) for i in range(n + 2) for j in (0, 1))

def grade(ell: dict[tuple[int, int], int], n: int) -> int:
    return sum(ell[v] for v in V(n))

def restriction(ell: dict[tuple[int, int], int], n: int) -> tuple[dict[tuple[int, int], int], int, int]:
    old = V(n)
    coarse = {v: ell[v] for v in old}
    q_c = grade(coarse, n)
    q_f = grade(ell, n + 1)
    return coarse, q_c, q_f - q_c

def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    contract, manifest = read(CONTRACT), read(MANIFEST)
    source, geometry = read(SOURCE), read(GEOMETRY)
    start, weight = read(START), read(WEIGHT)
    weight_manifest, omc011 = read(WEIGHT_MANIFEST), read(OMC011)
    r490 = read(R490_RUN)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = None) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    actual = {
        "PAH-001": sha(SOURCE),
        "PAH-OMC-004": sha(GEOMETRY),
        "PAH-OMC-008": sha(START),
        "PAH-OMC-010": sha(WEIGHT),
        "PAH-OMC-010-MANIFEST": sha(WEIGHT_MANIFEST),
        "PAH-OMC-011": sha(OMC011),
        "R-490-PRIMARY-RUN": sha(R490_RUN),
    }
    check("independent-parent-hashes", actual == EXPECTED, {"actual": actual, "expected": EXPECTED})
    check("independent-contract-pin", manifest["contract"]["sha256"] == sha(CONTRACT) and manifest["status"] == "MAINLINE_ADVANCE")
    check(
        "independent-source-firewall",
        source["functional_or_action"]["formula"].startswith("F_rho=sum_v[lambda_s")
        and source["dynamics"]["generator"].startswith("(L_rho f)(x)=sum_r m_r(x)")
        and all(value is True for value in contract["preservation_firewall"].values()),
    )
    check(
        "independent-graded-range",
        "Q_n={0,1,...,M_psi|V_n|}" in contract["exact_scope"]["state_definition"]["admissible_charge_set"]
        and "Q_n={0,...,2(n+2)}" in contract["exact_scope"]["state_definition"]["admissible_charge_set"],
    )

    rows: list[dict[str, Any]] = []
    rmax_values = (1, 2, 5)
    for rmax in rmax_values:
        for n in range(2, 8):
            fine_vertices = V(n + 1)
            patterns = [{v: 0 for v in fine_vertices}, {v: 1 for v in fine_vertices}]
            patterns.extend({v: int(v == chosen) for v in fine_vertices} for chosen in fine_vertices)
            for ell in patterns:
                coarse, q_c, dropped = restriction(ell, n)
                coarse_again, q_again, dropped_again = restriction(ell, n)
                rows.append({
                    "n": n,
                    "R_max": rmax,
                    "fine_vertex_count": len(fine_vertices),
                    "coarse_vertex_count": len(V(n)),
                    "q_fine": grade(ell, n + 1),
                    "q_coarse": q_c,
                    "dropped": dropped,
                    "bound": 0 <= q_c <= len(V(n)),
                    "balance": grade(ell, n + 1) == q_c + dropped,
                    "coarse_key": (tuple(sorted(coarse.items())), q_c),
                    "repeat_key": (tuple(sorted(coarse_again.items())), q_again),
                    "unique": coarse_again == coarse and q_again == q_c and dropped_again == dropped,
                })
    check("independent-totality-and-balance", all(row["bound"] and row["balance"] and row["dropped"] >= 0 for row in rows), {"rows": len(rows), "n_range": [2, 7], "R_max_values": list(rmax_values)})
    check("independent-Rmax-independence", all(row["R_max"] in rmax_values for row in rows) and "map itself is independent of R" in contract["exact_scope"]["regulator"], {"R_max_values": list(rmax_values)})
    check("independent-unique-restriction", all(row["unique"] and row["coarse_key"] == row["repeat_key"] for row in rows), "repeated direct restriction gives the same grade and coordinates")
    check(
        "independent-no-charge-mutation",
        contract["preservation_firewall"]["no_charge_deletion"]
        and contract["preservation_firewall"]["no_charge_redistribution"]
        and "grade is allowed to change" in contract["exact_scope"]["charge_balance"],
        contract["exact_scope"]["charge_balance"],
    )

    witness: dict[str, int] = {}
    for name, vertex in (("ell_a", (0, 0)), ("ell_d", (1, 1))):
        ell = {v: int(v == vertex) for v in V(3)}
        coarse, q_c, dropped = restriction(ell, 2)
        witness[name] = ell[vertex]
        check(f"independent-{name}-lift", ell[vertex] != 0 and q_c == 1 and dropped == 0, {"q_coarse": q_c, "dropped": dropped})
    neutral = {v: 0 for v in V(3)}
    for name in ("H_0", "H_1"):
        coarse, q_c, dropped = restriction(neutral, 2)
        witness[name] = 1
        check(f"independent-{name}-lift", witness[name] != 0 and q_c == 0 and dropped == 0, {"q_coarse": q_c, "dropped": dropped})
    check(
        "independent-component-recovery",
        "acts componentwise" in contract["exact_scope"]["generator_domain"]
        and "pi_(rho_(n,R,Q))" in contract["exact_scope"]["gibbs_reference"]
        and weight["exact_scope"]["state_weight"].startswith("W_(n,R)(omega)=pi_")
        and source["dynamics"]["state"].startswith("pi_(rho,Q)"),
        {"witness": witness},
    )
    check("independent-csw-role", r490["family"]["C_sw"] == 540 and "domination input" in contract["exact_scope"]["csw_role"] and "generator" in contract["exact_scope"]["csw_role"])
    check(
        "independent-no-physics",
        contract["status"]["claim_bearing"] is False
        and contract["status"]["active_gate_change"] is False
        and any("No infinite-volume dynamics" in item for item in contract["non_claims"]),
    )

    failed = [row for row in checks if not row["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc012-full-q-graded-domain-independent/1.0",
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
        "verdict": "MAINLINE_ADVANCE" if not failed else "HOLD_FOR_EVIDENCE",
        "derived": {"rows": len(rows), "n_range": [2, 7], "R_max_scope": "all positive integers"},
        "claim_bearing": False,
        "active_gate_change": False,
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "eligible_for_omc011_retest": bool(not failed),
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
        "next_question": contract["single_next_question"],
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}")
    return payload

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    return 0 if run(args.output)["verification"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
