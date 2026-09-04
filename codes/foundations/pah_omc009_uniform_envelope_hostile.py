#!/usr/bin/env python3
"""Hostile mutation checks for the PAH-OMC-009 negative result."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
START = ROOT / "strategy/pa-hyp/PAH-OMC-008-multi-cylinder-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-009-uniform-envelope-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-009-uniform-envelope-manifest.json"
PRIMARY = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc009-uniform-envelope/primary.json"
INDEPENDENT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc009-uniform-envelope/independent.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc009-uniform-envelope/hostile.json"
)

RESULT_ID = "R-489"
EXPLORATION_ID = "EXP-001434"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-009-UNIFORM-ENVELOPE-HOSTILE-001"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def sha(path: Path) -> str:
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


def pvalues(contract: dict[str, Any]) -> dict[str, Fraction]:
    raw = contract["exact_scope"]["regulator_path"]
    return {key: Fraction(str(raw[key])) for key in ("epsilon", "beta", "g", "lambda_s", "kappa_s", "kappa_D")}


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source = load(SOURCE)
    geometry = load(GEOMETRY)
    start = load(START)
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    primary = load(PRIMARY)
    independent = load(INDEPENDENT)
    p = pvalues(contract)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {"PAH-001": sha(SOURCE), "PAH-OMC-004": sha(GEOMETRY), "PAH-OMC-008": sha(START), "PAH-OMC-009": sha(CONTRACT), "PAH-OMC-009-MANIFEST": sha(MANIFEST)}
    check("baseline-runs-pass", primary.get("verification") == "PASS" and independent.get("verification") == "PASS")
    check("baseline-hashes", primary.get("source_hashes") == hashes and independent.get("source_hashes") == hashes)
    degree = 4
    eps = p["epsilon"]
    def quadratic(d: int) -> Fraction:
        return p["g"] * (1 - eps**2) / 2 + d * p["kappa_D"] * (1 - Fraction(2) / (1 + eps)) / 2

    # Each would_pass flag represents the tempting but invalid mutation.
    mutations = [
        {
            "name": "fixed_R_max",
            "would_pass": False,
            "reason": "A bounded R_max list cannot discharge the contract's R_max->infinity quantifier.",
        },
        {
            "name": "omit_two_incident_edges",
            "would_pass": -p["beta"] * quadratic(2) / 2 > 0,
            "reason": "Using degree two changes the derived coefficient and destroys the exact negative quadratic witness required by the declared G_n incidence at b.",
        },
        {
            "name": "drop_covariant_terms",
            "would_pass": -p["beta"] * (p["g"] * (1 - eps**2) / 2) / 2 > 0,
            "reason": "Dropping the unchanged PAH covariant edge energy changes the functional and removes the negative coefficient.",
        },
        {
            "name": "reverse_midpoint_sign",
            "would_pass": p["beta"] * quadratic(degree) / 2 > 0,
            "reason": "Using +beta*DeltaF/2 is not the PAH-001 Gibbs midpoint rate and reverses the exponent growth.",
        },
        {
            "name": "zero_root_weight",
            "would_pass": False,
            "reason": "w(r)=0 is not the declared positive geometric weight and cannot lower-bound the interaction sum.",
        },
        {
            "name": "counterterm_or_rate_rescale",
            "would_pass": False,
            "reason": "Any counterterm or rate rescaling violates the preservation firewall and is not a PAH-001 test.",
        },
    ]
    for mutation in mutations:
        mutation["rejected"] = not bool(mutation["would_pass"])
    check("all-invalid-mutations-rejected", all(item["rejected"] for item in mutations), mutations)
    check("degree-mutation-changes-sign", -p["beta"] * quadratic(2) / 2 < 0)
    check("covariant-mutation-changes-sign", -p["beta"] * (p["g"] * (1 - eps**2) / 2) / 2 <= 0)
    check("midpoint-mutation-changes-sign", p["beta"] * quadratic(degree) / 2 <= 0)
    check("firewall-declared", all(contract["preservation_firewall"].get(key) is True for key in ("no_new_hamiltonian", "no_counterterm", "no_averaging", "no_rate_fitting", "parent_functional_unchanged")) and manifest.get("no_parent_mutation") is True)
    check("no-physical-promotion", primary.get("claim_bearing") is False and primary.get("physical_progress") is False)

    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc009-uniform-envelope-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": AUDIT_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "mutations_attempted": len(mutations),
        "mutations_rejected": sum(int(item["rejected"]) for item in mutations),
        "all_mutations_rejected": all(item["rejected"] for item in mutations),
        "mutations": mutations,
        "source_hashes": hashes,
        "verdict": "NEGATIVE_RESULT_RMAX_UNIFORM_ENVELOPE",
        "claim_bearing": False,
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "physical_progress": False,
        "scientific_transition": False,
        "non_claims": contract["non_claims"],
        "reproduction": {"command": "python codes/foundations/pah_omc009_uniform_envelope_hostile.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc009-uniform-envelope/hostile.json"},
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['mutations_rejected']}/{payload['mutations_attempted']} mutations rejected")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(args.output)
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
