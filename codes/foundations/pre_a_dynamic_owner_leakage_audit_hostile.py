#!/usr/bin/env python3
"""Hostile mutation firewall for R-449."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-dynamic-owner-leakage-audit-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-30-hostile-dynamic_owner_leakage_audit/hostile.json"
)


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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


def digest(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    ).hexdigest()


def accepted(document: dict) -> bool:
    slots = document["owner_intake"]["forward_owner_status"]
    inverse = document["source_crosswalk"]["inverse"]
    scope = document["scope"]
    a2 = document["source_crosswalk"]["a2"]
    return (
        all(value in ("MISSING", "MISSING_SOURCE_OWNER") for value in slots.values())
        and a2["owner_compatible"] is False
        and a2["stochastic_heat"] is False
        and inverse["f_reg"] == "PARTIAL_FINITE_CONTRACTS_ONLY"
        and inverse["f_lim"] == "NOT_ADMITTED"
        and inverse["f_eff"] == "NOT_ADMITTED"
        and inverse["f_obs"] == "NOT_ADMITTED"
        and inverse["prospective_lock"] == "EMPTY_NOT_FROZEN"
        and inverse["candidate_selection"]
        == "NO_SELECTION_ZERO_ADMITTED_MICROSCOPIC_FORWARD_MAPS"
        and scope["claim_bearing"] is False
        and scope["pre_a_closed"] is False
        and scope["sector_a_closed"] is False
        and scope["c6_closed"] is False
        and document["leakage_audit"]["leakage_detected_and_blocked"] is True
        and document["scope"]["physical_owner_complete"] is False
    )


def run(output: Path = DEFAULT_OUTPUT) -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks = []
    mutations = []

    def add(label, mutator):
        candidate = copy.deepcopy(manifest)
        mutator(candidate)
        rejected = not accepted(candidate)
        checks.append(
            {
                "name": label,
                "status": "PASS" if rejected else "FAIL",
                "mutation_rejected": rejected,
            }
        )
        mutations.append({"mutation": label, "rejected": rejected})

    add(
        "promote deterministic A2 flow",
        lambda document: document["source_crosswalk"]["a2"].update(
            stochastic_heat=True, owner_compatible=True
        ),
    )
    add(
        "complete structural R-192 map",
        lambda document: document["owner_intake"]["forward_owner_status"].update(
            {key: "COMPLETE" for key in document["owner_intake"]["forward_owner_status"]}
        ),
    )
    add(
        "promote proof comparators",
        lambda document: document["scope"].update(physical_owner_complete=True),
    )
    add(
        "fill slots without owner hash",
        lambda document: document["owner_intake"]["forward_owner_status"].update(
            {key: "COMPLETE" for key in document["owner_intake"]["forward_owner_status"]}
        ),
    )
    add(
        "admit later inverse stages",
        lambda document: document["source_crosswalk"]["inverse"].update(
            f_lim="ADMITTED", f_eff="ADMITTED", f_obs="ADMITTED"
        ),
    )
    add(
        "freeze prospective target",
        lambda document: document["source_crosswalk"]["inverse"].update(
            prospective_lock="FROZEN"
        ),
    )
    add(
        "select static representative",
        lambda document: document["source_crosswalk"]["inverse"].update(
            candidate_selection="PA-M1-CURRENT-PINNED-PRODUCTION-FUNCTIONAL-v0"
        ),
    )
    add(
        "promote claim and sectors",
        lambda document: document["scope"].update(
            claim_bearing=True, pre_a_closed=True, sector_a_closed=True, c6_closed=True
        ),
    )
    if not all(item["rejected"] for item in mutations):
        raise AssertionError("hostile mutation accepted")

    payload = {
        "schema": "tect/pre-a-dynamic-owner-leakage-audit-hostile/1.0",
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": "R-449",
        "exploration_id": "EXP-001322",
        "task_id": "T-061",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "run_kind": "hostile",
        "verdict": "HOSTILE_MUTATIONS_REJECTED",
        "assertion_count": len(checks),
        "mutations_rejected": sum(1 for item in mutations if item["rejected"]),
        "assertions": checks,
        "mutations": mutations,
        "source_hashes": {
            "script": digest(Path(__file__)),
            "manifest": digest(MANIFEST),
        },
    }
    destination = output if output.is_absolute() else ROOT / output
    atomic_json(destination, payload)
    print(
        f"R-449 HOSTILE {payload['verdict']} "
        f"{payload['mutations_rejected']}/{len(mutations)}",
        flush=True,
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output)
    if args.self_test:
        assert payload["mutations_rejected"] == len(payload["mutations"]) == 8
        print("R-449 HOSTILE SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
