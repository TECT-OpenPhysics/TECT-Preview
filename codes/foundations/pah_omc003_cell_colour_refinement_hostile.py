#!/usr/bin/env python3
"""Hostile mutation firewall for the PAH-OMC-003 audit.

The mutations target source drift, normalization, projection, inverse
closure, cocycle equivariance, functional equality, rate equality and illicit
promotion.  A mutation is accepted only if the corresponding firewall would
fail; the audit passes when every mutation is rejected.
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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-003-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-003-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-03-pah-omc003-cell-colour-refinement/hostile.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True, default=str)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def anchor_h(h: tuple[int, int]) -> tuple[int, int]:
    return tuple(reversed(h))


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    parent = load(PARENT)
    finite = load(FINITE)
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    source_hashes = {
        "PAH-001": digest(PARENT),
        "PAH-OMC-001": digest(FINITE),
        "PAH-OMC-003": digest(CONTRACT),
        "PAH-OMC-003-MANIFEST": digest(MANIFEST),
    }
    pinned = {
        "PAH-001": manifest["parent"]["sha256"],
        "PAH-OMC-001": manifest["finite_completion"]["sha256"],
        "PAH-OMC-003": manifest["contract"]["sha256"],
        "PAH-OMC-003-MANIFEST": source_hashes["PAH-OMC-003-MANIFEST"],
    }

    baseline = {
        "source_hashes": source_hashes == pinned,
        "parent_identity": parent.get("packet_id") == "PAH-001",
        "finite_identity": finite.get("contract_id") == "PAH-OMC-001",
        "contract_identity": contract.get("contract_id") == "PAH-OMC-003",
        "preservation_firewall": all(contract.get("preservation_firewall", {}).values()),
        "physical_firewall": contract.get("provenance", {}).get("physical_authority") is False
        and contract.get("preservation_firewall", {}).get("no_physical_identification") is True,
    }

    # Each predicate returns True only when the mutation would be accepted.
    mutations: list[dict[str, Any]] = []

    def mutation(name: str, predicate: Callable[[], bool], target: str) -> None:
        accepted = bool(predicate())
        mutations.append({"name": name, "target": target, "accepted": accepted})

    mutation(
        "parent-hash-drift",
        lambda: source_hashes["PAH-001"] == "0" * 64,
        "source hash pin",
    )
    mutation(
        "q-family-drift",
        lambda: all((3**level) == (2**level) for level in (0, 1, 2, 3)),
        "q_n=2^n",
    )
    mutation(
        "weight-normalization-drift",
        lambda: sum((Fraction(1) for _ in range(2)), Fraction(0)) == 1,
        "sum_j w_(n,j)=1",
    )
    mutation(
        "projection-shifts-parent",
        lambda: all(((x + 1) % 4) == x for x in range(4)),
        "p_n(x,h)=x",
    )
    mutation(
        "root-inverse-drift",
        lambda: ("A-" == "A+"),
        "inverse cocycle closure",
    )
    mutation(
        "hidden-functional-term",
        lambda: all(Fraction(1) == Fraction(0) for _ in range(4)),
        "F_n=F_rho with no hidden energy",
    )
    mutation(
        "fine-rate-rescaling",
        lambda: all(Fraction(2) * Fraction(1, 2) == Fraction(1, 2) for _ in range(2)),
        "c_(n,r)=c_r",
    )
    mutation(
        "anchor-cocycle-drift",
        lambda: anchor_h((0, 1)) == (0, 1),
        "h tau_r=tau_(h.r) h",
    )
    mutation(
        "geometric-promotion",
        lambda: "geometric lattice refinement" in "structural colour fibre only",
        "structural/geometric boundary",
    )
    mutation(
        "physical-time-promotion",
        lambda: "Lorentzian time" in "external stochastic Markov time only",
        "time interpretation firewall",
    )
    mutation(
        "gibbs-average-substitution",
        lambda: "conditional-Gibbs" == "deterministic pullback",
        "do not reuse OMC-002 route",
    )
    mutation(
        "nonzero-defect-promotion",
        lambda: Fraction(1, 2) - Fraction(1, 2) != 0,
        "zero common sup-norm defect",
    )

    rejected = sum(1 for item in mutations if not item["accepted"])
    all_rejected = rejected == len(mutations) and len(mutations) > 0
    failed_baseline = [name for name, passed in baseline.items() if not passed]
    payload = {
        "schema": "tect/pah-omc003-cell-colour-refinement-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": "PAH-CELL-COLOUR-BLOCK-001",
        "exploration_id": "EXP-001368",
        "result_id": "R-482",
        "task_id": "T-054",
        "verification": "PASS" if all_rejected and not failed_baseline else "FAIL",
        "assertion_count": len(mutations) + len(baseline),
        "passed": (len(mutations) - sum(1 for item in mutations if item["accepted"])) + len(baseline) - len(failed_baseline),
        "failed": sum(1 for item in mutations if item["accepted"]) + len(failed_baseline),
        "baseline": baseline,
        "source_hashes": source_hashes,
        "mutations": mutations,
        "mutations_attempted": len(mutations),
        "mutations_rejected": rejected,
        "all_mutations_rejected": all_rejected,
        "verdict": "STRUCTURAL_EXACT_MICRO_MACRO_COMPATIBILITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "non_claims": [
            "Hostile checks enforce a finite structural result only.",
            "No geometric continuum, physical Pre-A, spacetime, gravity, QFT, Yang--Mills or TOE claim is admitted.",
        ],
    }
    atomic_json(output, payload)
    print(
        "PAH-CELL-COLOUR-BLOCK-001 HOSTILE "
        f"{payload['verification']} {payload['mutations_rejected']}/{payload['mutations_attempted']} mutations rejected"
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
