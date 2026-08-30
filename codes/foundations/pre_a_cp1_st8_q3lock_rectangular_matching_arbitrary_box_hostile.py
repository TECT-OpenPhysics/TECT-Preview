#!/usr/bin/env python3
"""Hostile mutation firewall for the R-443 arbitrary-box theorem."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-rectangular-matching-arbitrary-box-manifest.json"
PRIMARY = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-rectangular_matching_arbitrary_box/primary.json"
INDEPENDENT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-rectangular_matching_arbitrary_box/independent.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-rectangular_matching_arbitrary_box/hostile.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def accepts(candidate: dict[str, Any], baseline: dict[str, Any]) -> bool:
    f, b = candidate.get("finite_contract", {}), baseline["finite_contract"]
    scope = candidate.get("scope", {})
    return (
        candidate.get("claim_bearing") is False
        and f.get("dimension") == b["dimension"]
        and f.get("parity_modulus") == b["parity_modulus"]
        and f.get("side_min") == b["side_min"]
        and f.get("side_max") == b["side_max"]
        and f.get("lower_endpoint_colour") == b["lower_endpoint_colour"]
        and candidate.get("derived_rule", {}).get("layer_keys") == "all (axis, parity) pairs"
        and scope.get("arbitrary_box_edge_colouring_closed") is True
        and all(scope.get(key) is False for key in ("weighted_operator_form_closed", "boundary_commutator_decay_closed", "history_tail_closed", "exhaustion_cauchy_closed", "common_core_closed", "common_alpha_closed", "kms_gns_gap_closed", "physical_empty_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed"))
    )


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    baseline = json.loads(MANIFEST.read_text(encoding="utf-8"))
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT.read_text(encoding="utf-8"))
    if not accepts(baseline, baseline): raise AssertionError("baseline contract is not accepted")
    if primary.get("verdict") != "ARBITRARY_BOX_MATCHING_THEOREM_AUDITED": raise AssertionError("primary control missing")
    if independent.get("verdict") != "INDEPENDENT_ARBITRARY_BOX_MATCHING_CONTROL": raise AssertionError("independent control missing")
    rows: list[dict[str, Any]] = []

    def reject(name: str, mutation: dict[str, Any], candidate: dict[str, Any]) -> None:
        accepted = accepts(candidate, baseline)
        if accepted: raise AssertionError(f"hostile mutation accepted: {name}")
        rows.append({"name": name, "status": "REJECTED", "mutation": mutation, "accepted": accepted})

    m = copy.deepcopy(baseline); m["scope"]["arbitrary_box_edge_colouring_closed"] = False; reject("erase arbitrary-box theorem", {"arbitrary_box_edge_colouring_closed": False}, m)
    m = copy.deepcopy(baseline); m["finite_contract"]["parity_modulus"] = 1; reject("collapse parity", {"parity_modulus": 1}, m)
    m = copy.deepcopy(baseline); m["finite_contract"]["lower_endpoint_colour"] = "(axis, upper_coordinate[axis] mod parity_modulus)"; reject("upper endpoint substitution", {"colour_rule": "upper endpoint parity"}, m)
    m = copy.deepcopy(baseline); m["derived_rule"]["layer_keys"] = "nonempty layers only"; m["scope"]["layer_keys_retained_including_empty"] = False; reject("drop empty slots", {"retain_empty_layers": False}, m)
    m = copy.deepcopy(baseline); m["finite_contract"]["side_min"] = 1; reject("allow side length one", {"side_min": 1}, m)
    m = copy.deepcopy(baseline); m["claim_bearing"] = True; reject("claim promotion", {"claim_bearing": True}, m)
    m = copy.deepcopy(baseline); m["scope"]["weighted_operator_form_closed"] = True; reject("operator promotion", {"weighted_operator_form_closed": True}, m)
    m = copy.deepcopy(baseline); m["scope"]["physical_empty_closed"] = True; m["scope"]["pre_a_closed"] = True; reject("physical and Pre-A promotion", {"physical_empty_closed": True, "pre_a_closed": True}, m)
    payload: dict[str, Any] = {"schema": "tect/pre-a-r443-hostile/1.0", "manifest": MANIFEST.relative_to(ROOT).as_posix(), "result_id": "R-443", "exploration_id": "EXP-001288", "claim_id": baseline["claim_ids"][0], "run_kind": "hostile", "verdict": "HOSTILE_MUTATIONS_REJECTED", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "mutations_rejected": len(rows), "scope": {"hostile_mutations_rejected": True, "claim_bearing": False, "operator_or_physical_promotion_rejected": True}, "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "primary": sha256(PRIMARY), "independent": sha256(INDEPENDENT)}, "evidence_level": "T0 / EXECUTED ADVERSARIAL CONTRACT FIREWALL", "non_claims": baseline["non_claims"], "boundary": baseline["boundary"]}
    destination = output if output.is_absolute() else ROOT / output
    atomic_json(destination, payload)
    print(f"R-443 HOSTILE {payload['verdict']} {len(rows)}/{len(rows)}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args()
    payload = run(args.output)
    if args.self_test:
        assert payload["verdict"] == "HOSTILE_MUTATIONS_REJECTED" and payload["assertion_count"] == 8
        print("R-443 HOSTILE SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
