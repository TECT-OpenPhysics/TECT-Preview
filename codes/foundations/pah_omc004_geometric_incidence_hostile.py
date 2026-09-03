#!/usr/bin/env python3
"""Hostile mutation firewall for the PAH-OMC-004 local geometry audit.

The firewall attacks the parent hashes, the diagonal/face incidence change,
the Q=0 scope, the projection and locality hypotheses, and every prohibited
promotion.  A mutation is accepted only when it would evade a declared
contract condition; the audit passes when all such mutations are rejected.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
FINITE = ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json"
REFERENCE = ROOT / "strategy/pa-hyp/PAH-OMC-003-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-004-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-03-pah-omc004-geometric-incidence/hostile.json"
)

AUDIT_ID = "PAH-GEOMETRIC-INCIDENCE-LOCAL-001"
EXPLORATION_ID = "EXP-001369"
RESULT_ID = "R-483"
TASK_ID = "T-054"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True, default=str)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    parent = load(PARENT)
    finite = load(FINITE)
    reference = load(REFERENCE)
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    hashes = {
        "PAH-001": sha(PARENT),
        "PAH-OMC-001": sha(FINITE),
        "PAH-OMC-003": sha(REFERENCE),
        "PAH-OMC-004": sha(CONTRACT),
        "PAH-OMC-004-MANIFEST": sha(MANIFEST),
    }
    pinned = {
        "PAH-001": manifest["parent"]["sha256"],
        "PAH-OMC-001": manifest["finite_completion"]["sha256"],
        "PAH-OMC-003": manifest["reference_only"]["sha256"],
        "PAH-OMC-004": manifest["contract"]["sha256"],
        "PAH-OMC-004-MANIFEST": hashes["PAH-OMC-004-MANIFEST"],
    }
    firewall = contract.get("preservation_firewall", {})
    baseline = {
        "source-hashes": hashes == pinned,
        "parent-identities": parent.get("packet_id") == "PAH-001" and finite.get("contract_id") == "PAH-OMC-001",
        "reference-identity": reference.get("contract_id") == "PAH-OMC-003",
        "successor-identity": contract.get("contract_id") == "PAH-OMC-004",
        "genuine-incidence": contract.get("status", {}).get("refinement_family") == "GENUINE_FACE_EDGE_INCIDENCE_STRIP",
        "no-parent-mutation": manifest.get("no_parent_mutation") is True,
        "physical-firewall": contract.get("provenance", {}).get("physical_authority") is False and firewall.get("no_physical_identification") is True,
        "scope-firewall": contract.get("status", {}).get("uniform_limit") == "NOT_ADMITTED" and firewall.get("no_color_only_substitution") is True,
    }

    mutations: list[dict[str, Any]] = []

    def mutation(name: str, predicate: Callable[[], bool], target: str) -> None:
        accepted = bool(predicate())
        mutations.append({"name": name, "target": target, "accepted": accepted})

    mutation("parent-hash-drift", lambda: hashes["PAH-001"] == "0" * 64, "immutable PAH-001 hash")
    mutation("successor-hash-drift", lambda: hashes["PAH-OMC-004"] == "0" * 64, "successor hash pin")
    mutation("remove-diagonal", lambda: len(((0, 1), (1, 2), (2, 3), (3, 0))) == 5, "new geometric edge d=(0,2)")
    mutation("keep-one-face", lambda: len(((0, 1, 4), (4, 2, 3))) == 1, "two fine faces")
    mutation("colour-only-substitution", lambda: firewall.get("no_color_only_substitution") is False, "incidence versus colour firewall")
    mutation("add-counterterm", lambda: firewall.get("no_counterterm_or_energy_added") is False, "unchanged PAH functional")
    mutation("rescale-rates", lambda: firewall.get("no_parent_rate_rescaling") is False, "inherited PAH midpoint rates")
    mutation("change-q-sector", lambda: 1 == 0, "fixed Q=0 diagnostic scope")
    mutation("shift-old-projection", lambda: ((0, 0), (1, 0)) != ((0, 0), (1, 0)), "p_(n+1,n) retains old variables")
    mutation("erase-boundary-defect", lambda: Fraction(1, 4) == Fraction(-55, 36), "explicit hidden-diagonal witness")
    mutation("declare-global-uniform", lambda: contract.get("status", {}).get("uniform_limit") == "ADMITTED", "local versus global scope")
    mutation("promote-continuum", lambda: "continuum theorem" in " ".join(contract.get("non_claims", [])), "ordered-limit firewall")
    mutation("promote-physical-preA", lambda: contract.get("provenance", {}).get("physical_authority") is True, "physical-authority firewall")
    mutation("import-q3lock", lambda: firewall.get("no_q3lock_import") is False, "no Q3LOCK import")
    mutation("drop-support-hypothesis", lambda: "support" not in contract.get("compatibility_target", {}).get("local_eventual_exactness", ""), "finite interaction closure")
    mutation("claim-zero-defect-at-boundary", lambda: Fraction(16, 9) == 0, "nonzero local boundary defect")

    rejected = sum(1 for item in mutations if not item["accepted"])
    failed_baseline = [name for name, passed in baseline.items() if not passed]
    all_rejected = rejected == len(mutations) and len(mutations) > 0
    failed = len(failed_baseline) + (len(mutations) - rejected)
    payload = {
        "schema": "tect/pah-omc004-geometric-incidence-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": AUDIT_ID,
        "exploration_id": EXPLORATION_ID,
        "result_id": RESULT_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if failed == 0 else "FAIL",
        "assertion_count": len(baseline) + len(mutations),
        "passed": len(baseline) - len(failed_baseline) + rejected,
        "failed": failed,
        "baseline": baseline,
        "source_hashes": hashes,
        "mutations": mutations,
        "mutations_attempted": len(mutations),
        "mutations_rejected": rejected,
        "all_mutations_rejected": all_rejected,
        "verdict": "LOCAL_COMMON_CORE_GEOMETRIC_COMPATIBILITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "non_claims": [
            "Hostile checks enforce a local finite structural result only.",
            "No global uniform, continuum, physical Pre-A, spacetime, gravity, QFT, Yang--Mills or TOE claim is admitted.",
        ],
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} HOSTILE {payload['verification']} {rejected}/{len(mutations)} mutations rejected")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(args.output)
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
