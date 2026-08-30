#!/usr/bin/env python3
"""Adversarial contract firewall for the R-442 matching lemma audit."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-rectangular-matching-general-lemma-manifest.json"
PRIMARY = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-rectangular_matching_general_lemma/primary.json"
INDEPENDENT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-rectangular_matching_general_lemma/independent.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-rectangular_matching_general_lemma/hostile.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def accepts(candidate: dict[str, Any], baseline: dict[str, Any]) -> bool:
    """The narrow acceptance contract used by this hostile test."""
    fixture = candidate.get("finite_contract", {})
    base = baseline["finite_contract"]
    scope = candidate.get("scope", {})
    required_scope = (
        "arbitrary_box_edge_colouring_closed",
        "weighted_operator_form_closed",
        "boundary_commutator_decay_closed",
        "history_tail_closed",
        "exhaustion_cauchy_closed",
        "common_core_closed",
        "common_alpha_closed",
        "kms_gns_gap_closed",
        "physical_empty_closed",
        "continuum_closed",
        "c6_closed",
        "sector_a_closed",
        "pre_a_closed",
    )
    return (
        candidate.get("claim_bearing") is False
        and fixture.get("dimension") == base["dimension"]
        and fixture.get("parity_modulus") == base["parity_modulus"]
        and fixture.get("side_min") == base["side_min"]
        and fixture.get("side_max") == base["side_max"]
        and fixture.get("lower_endpoint_colour") == base["lower_endpoint_colour"]
        and candidate.get("derived_rule", {}).get("layer_keys") == "all (axis, parity) pairs"
        and all(scope.get(key) is False for key in required_scope)
    )


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    baseline = json.loads(MANIFEST.read_text(encoding="utf-8"))
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    if not accepts(baseline, baseline):
        raise AssertionError("unmutated R-442 contract must be accepted")
    if primary.get("verdict") != "GENERAL_RECTANGULAR_MATCHING_LEMMA_AUDITED":
        raise AssertionError("hostile control requires the audited primary output")
    if independent.get("verdict") != "INDEPENDENT_GENERAL_RECTANGULAR_MATCHING_CONTROL":
        raise AssertionError("hostile control requires the independent output")

    def reject(name: str, mutation: dict[str, Any], candidate: dict[str, Any]) -> None:
        accepted = accepts(candidate, baseline)
        if accepted:
            raise AssertionError(f"hostile mutation accepted: {name}")
        rows.append({"name": name, "status": "REJECTED", "mutation": mutation, "accepted": accepted})

    wrong_modulus = copy.deepcopy(baseline)
    wrong_modulus["finite_contract"]["parity_modulus"] = 1
    reject("parity modulus collapse", {"parity_modulus": 1}, wrong_modulus)

    merged_layers = copy.deepcopy(baseline)
    merged_layers["derived_rule"]["layer_keys"] = "axis only"
    reject("axis-only colour merge", {"layer_keys": "axis only"}, merged_layers)

    upper_endpoint = copy.deepcopy(baseline)
    upper_endpoint["finite_contract"]["lower_endpoint_colour"] = "(axis, upper_coordinate[axis] mod parity_modulus)"
    reject("upper-endpoint colour substitution", {"colour_rule": "upper endpoint parity"}, upper_endpoint)

    dropped_empty = copy.deepcopy(baseline)
    dropped_empty["scope"]["layer_keys_retained_including_empty"] = False
    dropped_empty["derived_rule"]["layer_keys"] = "nonempty (axis, parity) pairs only"
    reject("drop empty colour slots", {"retain_empty_layers": False}, dropped_empty)

    invalid_range = copy.deepcopy(baseline)
    invalid_range["finite_contract"]["side_min"] = 1
    reject("invalid side range", {"side_min": 1}, invalid_range)

    promoted_claim = copy.deepcopy(baseline)
    promoted_claim["claim_bearing"] = True
    reject("claim-bearing promotion", {"claim_bearing": True}, promoted_claim)

    promoted_box = copy.deepcopy(baseline)
    promoted_box["scope"]["arbitrary_box_edge_colouring_closed"] = True
    reject("arbitrary-box theorem promotion", {"arbitrary_box_edge_colouring_closed": True}, promoted_box)

    promoted_physics = copy.deepcopy(baseline)
    promoted_physics["scope"]["common_core_closed"] = True
    promoted_physics["scope"]["physical_empty_closed"] = True
    reject("operator/physical promotion", {"common_core_closed": True, "physical_empty_closed": True}, promoted_physics)

    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r442-hostile/1.0",
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": "R-442",
        "exploration_id": "EXP-001287",
        "claim_id": baseline["claim_ids"][0],
        "run_kind": "hostile",
        "verdict": "HOSTILE_MUTATIONS_REJECTED",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "mutations_rejected": len(rows),
        "scope": {"hostile_mutations_rejected": True, "claim_bearing": False, "operator_or_physical_promotion_rejected": True},
        "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "primary": sha256(PRIMARY), "independent": sha256(INDEPENDENT)},
        "evidence_level": "T0 / EXECUTED ADVERSARIAL CONTRACT FIREWALL",
        "non_claims": baseline["non_claims"],
        "boundary": baseline["boundary"],
    }
    destination = output if output.is_absolute() else ROOT / output
    atomic_json(destination, payload)
    print(f"R-442 HOSTILE {payload['verdict']} {len(rows)}/{len(rows)}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output)
    if args.self_test:
        assert payload["verdict"] == "HOSTILE_MUTATIONS_REJECTED"
        assert payload["assertion_count"] == 8
        print("R-442 HOSTILE SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
