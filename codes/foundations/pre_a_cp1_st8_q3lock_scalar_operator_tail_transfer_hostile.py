#!/usr/bin/env python3
"""Adversarial scope-firewall checks for the R-445 package."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-scalar-operator-tail-transfer-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-scalar_operator_tail_transfer/hostile.json"


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
    normalized = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(normalized).hexdigest()


def contract_is_safe(candidate: dict[str, Any]) -> bool:
    scope = candidate["scope"]
    required_false = (
        "operator_norm_of_actual_q3_terms",
        "q3lock_commutator_identification",
        "history_tail_closed",
        "weighted_operator_form_closed",
        "common_core_closed",
        "common_alpha_closed",
        "exhaustion_cauchy_closed",
        "kms_gns_gap_closed",
        "physical_empty_closed",
        "continuum_closed",
        "c6_closed",
        "sector_a_closed",
        "pre_a_closed",
    )
    return (
        candidate.get("result_id") == "R-445"
        and candidate.get("claim_bearing") is False
        and candidate.get("status") == "CONDITIONAL_WEIGHTED_NORM_TRANSFER_AUDITED"
        and scope.get("per_edge_majorant_assumed") is True
        and all(scope.get(key) is False for key in required_false)
        and candidate["finite_contract"].get("term_bound") == "||K_e|| <= C*w(e)"
        and "C*T(R)" in candidate["finite_contract"].get("transfer_chain", "")
        and candidate["scope"].get("no_new_negative_result") is True
        and candidate["scope"].get("no_tier_change") is True
        and candidate["scope"].get("no_pdf") is True
    )


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not contract_is_safe(manifest):
        raise AssertionError("baseline R-445 contract failed its own scope firewall")
    mutations: list[tuple[str, Any]] = []

    mutation = copy.deepcopy(manifest)
    mutation["claim_bearing"] = True
    mutations.append(("claim-bearing promotion", mutation))
    mutation = copy.deepcopy(manifest)
    mutation["scope"]["q3lock_commutator_identification"] = True
    mutations.append(("Q3LOCK identification promotion", mutation))
    mutation = copy.deepcopy(manifest)
    mutation["scope"]["continuum_closed"] = True
    mutations.append(("continuum promotion", mutation))
    mutation = copy.deepcopy(manifest)
    mutation["finite_contract"].pop("term_bound")
    mutations.append(("missing per-edge majorant", mutation))
    mutation = copy.deepcopy(manifest)
    mutation["finite_contract"]["transfer_chain"] = "triangle inequality only"
    mutations.append(("missing ambient transfer", mutation))
    mutation = copy.deepcopy(manifest)
    mutation["scope"]["physical_empty_closed"] = True
    mutations.append(("physical-empty promotion", mutation))
    mutation = copy.deepcopy(manifest)
    mutation["status"] = "CLOSED"
    mutations.append(("status overclaim", mutation))
    mutation = copy.deepcopy(manifest)
    mutation["scope"]["no_pdf"] = False
    mutations.append(("PDF policy mutation", mutation))

    checks: list[dict[str, Any]] = []
    for label, candidate in mutations:
        accepted = contract_is_safe(candidate)
        if accepted:
            raise AssertionError(f"hostile mutation was accepted: {label}")
        checks.append({"mutation": label, "status": "REJECTED", "scope_firewall": "PASS"})

    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r445-hostile/1.0",
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": "R-445",
        "exploration_id": "EXP-001297",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "hostile",
        "verdict": "HOSTILE_MUTATIONS_REJECTED",
        "mutations_rejected": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST)},
        "tested_boundaries": [
            "claim-bearing promotion",
            "Q3LOCK operator identification",
            "continuum and physical-empty promotion",
            "removal of the explicit per-edge majorant",
            "removal of the C*T(R) transfer chain",
            "status and PDF-policy mutation",
        ],
        "scope": {"claim_bearing": False, "tier_change": False, "physical_or_continuum_promotion": False},
        "boundary": manifest["boundary"],
    }
    destination = output if output.is_absolute() else ROOT / output
    atomic_json(destination, payload)
    print(f"R-445 HOSTILE {payload['verdict']} {len(checks)}/{len(checks)}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output)
    if args.self_test:
        assert payload["verdict"] == "HOSTILE_MUTATIONS_REJECTED"
        assert payload["mutations_rejected"] == 8
        print("R-445 HOSTILE SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
