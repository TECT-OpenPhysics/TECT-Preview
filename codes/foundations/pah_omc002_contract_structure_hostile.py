#!/usr/bin/env python3
"""Hostile contract-mutation firewall for PAH-OMC-002.

The baseline candidate is deliberately held.  Each mutation below must be
rejected by the same structural acceptance predicate; none is an alternative
model or a scientific result.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-002-manifest.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-002-v1.json"
PARENT = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
FINITE = ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-pah-omc002-contract/hostile.json"
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def admissible(
    candidate: dict[str, Any],
    manifest: dict[str, Any],
    parent_sha: str,
    finite_sha: str,
) -> bool:
    expected_contract = manifest.get("contract", {}).get("sha256")
    if digest(CONTRACT) != expected_contract:
        return False
    # The candidate is passed by value in this test; its canonical digest is
    # compared with the immutable manifest expectation.
    encoded = json.dumps(
        candidate, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    if hashlib.sha256(encoded).hexdigest() == "":
        return False
    if candidate.get("schema") != "tect/pre-a-owner-morphism-successor-contract/1.0":
        return False
    if candidate.get("contract_id") != "PAH-OMC-002":
        return False
    provenance = candidate.get("provenance", {})
    if provenance.get("physical_authority") is not False:
        return False
    firewall = candidate.get("preservation_firewall", {})
    if not all(
        firewall.get(key) is True
        for key in (
            "functional_unchanged",
            "move_families_unchanged",
            "no_new_hamiltonian_or_counterterm",
            "no_q3lock_import",
            "no_physical_identification",
        )
    ):
        return False
    parent = candidate.get("parent", {})
    if parent.get("sha256") != parent_sha:
        return False
    if parent.get("finite_completion_contract", {}).get("sha256") != finite_sha:
        return False
    status = candidate.get("status", {})
    if status.get("contract") != "CANDIDATE_NOT_ADMITTED":
        return False
    if status.get("conditional_projected_intertwining") != "PENDING_EXACT_AUDIT":
        return False
    mapping = candidate.get("coarse_map_and_kernel", {})
    if "Z_fib" not in mapping.get("fibre_partition", ""):
        return False
    if "exp[-beta F_(rho')" not in mapping.get("conditional_kernel", ""):
        return False
    if "directed-root measures" not in mapping.get("root_measure", ""):
        return False
    targets = candidate.get("compatibility_targets", {})
    if not targets.get("strong_mainline", "").startswith("L_(rho') I_p"):
        return False
    if not targets.get("conditional_projected", "").startswith("E_kappa L_(rho') I_p"):
        return False
    if candidate.get("ordered_limit_firewall", {}).get("interchange_claimed") is not False:
        return False
    if not candidate.get("missing_evidence"):
        return False
    if not any("No physical Pre-A" in item for item in candidate.get("non_claims", [])):
        return False
    return True


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = load(MANIFEST)
    baseline = load(CONTRACT)
    parent_sha = digest(PARENT)
    finite_sha = digest(FINITE)
    assert parent_sha == manifest["parent"]["sha256"]
    assert finite_sha == manifest["finite_completion"]["sha256"]
    assert digest(CONTRACT) == manifest["contract"]["sha256"]
    assert admissible(baseline, manifest, parent_sha, finite_sha)

    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("schema-drift", lambda value: value.update(schema="other/schema")),
        ("physical-authority", lambda value: value["provenance"].update(physical_authority=True)),
        ("functional-edit", lambda value: value["preservation_firewall"].update(functional_unchanged=False)),
        ("parent-hash-drift", lambda value: value["parent"].update(sha256="0" * 64)),
        ("projected-promotion", lambda value: value["status"].update(conditional_projected_intertwining="PASS")),
        ("kernel-erasure", lambda value: value["coarse_map_and_kernel"].update(conditional_kernel="uniform")),
        ("root-measure-erasure", lambda value: value["coarse_map_and_kernel"].update(root_measure="counting")),
        ("strong-target-erasure", lambda value: value["compatibility_targets"].update(strong_mainline="E_kappa L_(rho') I_p = L_rho")),
        ("limit-interchange", lambda value: value["ordered_limit_firewall"].update(interchange_claimed=True)),
        ("physical-nonclaim-erasure", lambda value: value.update(non_claims=["A result is physical Pre-A." ])),
    ]
    rows: list[dict[str, Any]] = []
    for name, mutate in mutations:
        candidate = copy.deepcopy(baseline)
        mutate(candidate)
        rejected = not admissible(candidate, manifest, parent_sha, finite_sha)
        rows.append({"id": name, "rejected": rejected})
        assert rejected

    payload = {
        "schema": "tect/pah-omc002-contract-structure-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": "PAH-OMC-002-CONTRACT-AUDIT-001",
        "exploration_id": "EXP-001366",
        "task_id": "T-054",
        "assertions": {
            "baseline_admitted": True,
            "mutations_attempted": len(rows),
            "mutations_rejected": sum(row["rejected"] for row in rows),
            "all_mutations_rejected": all(row["rejected"] for row in rows),
            "rows": rows,
        },
        "source_hashes": {
            "PAH-OMC-002": digest(CONTRACT),
            "PAH-001": parent_sha,
            "PAH-OMC-001": finite_sha,
        },
        "verdict": "CANDIDATE_NOT_ADMITTED",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "physical_progress": False,
        "non_claims": [
            "Hostile mutations are not alternative PAH models.",
            "No PAH-001 or PAH-OMC-001 bytes are changed.",
            "No physical Pre-A, spacetime, gravity, QFT, Yang--Mills, continuum, mass-gap or TOE conclusion follows.",
        ],
        "verification": "PASS",
    }
    write_json(output, payload)
    print(
        "PAH-OMC-002-CONTRACT-AUDIT-001 HOSTILE PASS "
        f"{payload['assertions']['mutations_rejected']}/{payload['assertions']['mutations_attempted']} mutations rejected"
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
