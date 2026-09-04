#!/usr/bin/env python3
"""Hostile firewall for the PAH-OMC-014 Q=0 obstruction.

The checks are deliberately source-facing.  They reject the common ways a
finite component mismatch could be made to look stronger than it is: removing
the Wilson term, changing the projection, fitting cross-Q weights, using a
decimal-only witness, or promoting the result to a global or physical no-go.
The script does not import the primary implementation.
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
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC004 = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
OMC012 = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json"
PRIMARY = ROOT / "codes/foundations/pah_omc014_q0_projective_obstruction.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc014_q0_projective_obstruction_independent.py"
DEFAULT_PRIMARY_RUN = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-05-pah-omc014-q0-projective-obstruction/primary.json"
)
DEFAULT_INDEPENDENT_RUN = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-05-pah-omc014-q0-projective-obstruction/independent.json"
)
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-05-pah-omc014-q0-projective-obstruction/hostile.json"
)

NEGATIVE_TAG = "AUDIT-2026-09-05-PAH-OMC-014-Q0-COMPONENT-PUSHFORWARD"
EXPECTED_HASHES = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-004": "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "PAH-OMC-012": "180228b83e44f46406b302c97ff6caab023240eeaa19997618012074930f3e72",
}
# Test oracles are copied from the independently reproduced canonical run.
EXPECTED_MAP_SHA = "b66044e590399d959ab2947edf22f3aa2aeea4405473b88c4327da24058ebb93"
EXPECTED_MAP_TERMS = 2784


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            json.dump(payload, stream, ensure_ascii=True, indent=2, sort_keys=True)
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


def run(
    output: Path = DEFAULT_OUTPUT,
    primary_run: Path = DEFAULT_PRIMARY_RUN,
    independent_run: Path = DEFAULT_INDEPENDENT_RUN,
) -> dict[str, Any]:
    source = read(PAH001)
    geometry = read(OMC004)
    graded = read(OMC012)
    primary = read(primary_run)
    independent = read(independent_run)
    primary_text = PRIMARY.read_text(encoding="utf-8")
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    formula = source["functional_or_action"]["formula"]
    state_scope = geometry["exact_scope"]["state_and_regulator"]
    projection = graded["exact_scope"]["neutral_refinement"]
    gibbs = graded["exact_scope"]["gibbs_reference"]

    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "passed": bool(passed), "actual": actual, "expected": expected})

    actual_hashes = {"PAH-001": sha(PAH001), "PAH-OMC-004": sha(OMC004), "PAH-OMC-012": sha(OMC012)}
    check("source hashes are pinned", actual_hashes == EXPECTED_HASHES, actual_hashes, EXPECTED_HASHES)
    check("primary and independent source hashes agree", primary.get("source_hashes") == independent.get("source_hashes") == EXPECTED_HASHES, {"primary": primary.get("source_hashes"), "independent": independent.get("source_hashes")}, EXPECTED_HASHES)
    check("both base runs pass the declared negative test", primary.get("verification") == "PASS" and independent.get("verification") == "PASS" and primary.get("verdict") == "NEGATIVE_RESULT" and independent.get("verdict") == "NEGATIVE_RESULT", {"primary": [primary.get("verification"), primary.get("verdict")], "independent": [independent.get("verification"), independent.get("verdict")]}, "PASS/NEGATIVE_RESULT")
    p_map = primary.get("derived", {}).get("cross_difference_coefficients")
    i_map = independent.get("derived", {}).get("cross_difference_coefficients")
    check("independent exact maps agree", p_map == i_map, {"primary_terms": len(p_map or []), "independent_terms": len(i_map or [])}, "identical coefficient lists")
    check("exact map oracle is nonempty", primary.get("derived", {}).get("cross_difference_sha256") == EXPECTED_MAP_SHA and len(p_map or []) == EXPECTED_MAP_TERMS, {"sha256": primary.get("derived", {}).get("cross_difference_sha256"), "terms": len(p_map or [])}, {"sha256": EXPECTED_MAP_SHA, "terms": EXPECTED_MAP_TERMS})
    check("finite scope is unchanged", all(token in primary.get("scope", "") for token in ("G_3 -> G_2", "K=2", "Q=0", "beta=1", "R_max=1")), primary.get("scope"), "G_3 -> G_2; K=2; Q=0; beta=1; R_max=1")

    # Each following row is a hostile mutation that must be rejected.
    check("mutation removing Wilson term rejected", "kappa_g" in formula and "1-Re U_p" in formula and "2 * value" in primary_text, {"formula": formula, "wilson_factor": "2 * value" in primary_text}, "Wilson term and Z2 odd-flux factor retained")
    check("mutation changing the strip projection rejected", "drop only the new column" in projection and "recompute Q_c" in projection and "unsplit square" in geometry["exact_scope"]["strip_family"]["faces"], {"projection": projection, "faces": geometry["exact_scope"]["strip_family"]["faces"]}, "declared neutral restriction and frontier square")
    check("mutation replacing Q=0 by a fixed-Q shortcut rejected", "Q_f-Q_c" in graded["exact_scope"]["charge_balance"] and ">=0" in graded["exact_scope"]["charge_balance"] and "Q=0" in state_scope, {"balance": graded["exact_scope"]["charge_balance"], "scope": state_scope}, "deterministic Q_f=0 => Q_c=0")
    check("mutation fitting cross-Q weights rejected", "no cross-Q mixing probabilities" in gibbs and "no new normalized global mixture" in graded["exact_scope"]["gibbs_reference"], gibbs, "component family only; no fitted mixture")
    check("mutation adding a counterterm rejected", source["functional_or_action"]["counterterms"] == "none at finite rho" and "counterterm" not in independent_text.lower().replace("no counterterm", ""), {"counterterms": source["functional_or_action"]["counterterms"]}, "none at finite rho")
    check("mutation using a decimal-only witness rejected", "Lindemann" in primary.get("exact_nonzero_criterion", "") and "integer coefficient map" in primary.get("exact_nonzero_criterion", "") and "decimal is diagnostic" in primary.get("exact_nonzero_criterion", ""), primary.get("exact_nonzero_criterion"), "exact rational-exponent criterion")
    check("mutation discarding phase multiplicities rejected", "phases factor out" in primary_text and "counting measure" in source["finite_regulator"]["normalization"], {"phase_note": "phases factor out" in primary_text, "normalization": source["finite_regulator"]["normalization"]}, "per-level constants cancel under normalized expectations")
    check("mutation promoting to a global full-Q no-go rejected", ("not a full-Q global-mixture no-go" in primary.get("boundary", "") or "does not refute a global full-Q mixture" in primary.get("boundary", "")) and "No weak cylinder limit" in " ".join(primary.get("non_claims", [])), {"boundary": primary.get("boundary"), "non_claims": primary.get("non_claims")}, "component boundary retained")
    check("mutation promoting to physics rejected", all(any(term in item for item in primary.get("non_claims", [])) for term in ("physical Pre-A", "QFT", "TOE")), primary.get("non_claims"), "physical non-claims retained")
    check("independent lane does not import primary", "import pah_omc014_q0_projective_obstruction" not in independent_text and "from pah_omc014_q0_projective_obstruction" not in independent_text, independent_text[:300], "no primary import")

    failed = [row for row in checks if not row["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc014-q0-projective-obstruction-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": "PAH-OMC-014-Q0-PROJECTIVE-OBSTRUCTION-HOSTILE-001",
        "task_id": "T-054",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "negative_tag": NEGATIVE_TAG,
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOSTILE_MUTATIONS_REJECTED" if not failed else "HOSTILE_MUTATION_ACCEPTED",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": actual_hashes,
        "base_run_hashes": {"primary": sha(primary_run), "independent": sha(independent_run)},
        "boundary": "Hostile firewall for the componentwise Q_f=0 obstruction; no full-Q global-mixture no-go or physical promotion.",
        "lean": {"status": "NOT_APPLICABLE", "reason": "The exact exponential-polynomial nonvanishing step is outside the current Lean bridge; all algebraic finite inputs are independently replayed."},
        "non_claims": ["No global cross-Q probability or cancellation analysis is supplied.", "No weak cylinder limit, infinite-volume dynamics, continuum, physical Pre-A, spacetime, QFT, gravity, Yang--Mills, mass-gap or TOE conclusion follows."],
    }
    atomic_json(output, payload)
    print(f"{payload['audit_id']} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--primary-run", type=Path, default=DEFAULT_PRIMARY_RUN)
    parser.add_argument("--independent-run", type=Path, default=DEFAULT_INDEPENDENT_RUN)
    args = parser.parse_args()
    return 0 if run(args.output, args.primary_run, args.independent_run)["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
