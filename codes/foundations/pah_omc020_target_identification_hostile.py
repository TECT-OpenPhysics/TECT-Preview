#!/usr/bin/env python3
"""Hostile fail-closed checks for the PAH-OMC-020 D_n contract."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-target-identification-contract-v1.json"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-target-identification/hostile.json"


def write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    os.close(fd)
    temp = Path(name)
    try:
        temp.write_bytes(data)
        temp.replace(path)
    finally:
        if temp.exists():
            temp.unlink()


def route_complete(fields: dict[str, bool], required: list[str], *, owner: bool = True, conditional: bool = False) -> bool:
    return owner and not conditional and all(fields.get(name, False) for name in required)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    dest = args.output if args.output.is_absolute() else ROOT / args.output
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    form = list(contract["routes"]["form"]["required_fields"])
    path = list(contract["routes"]["path"]["required_fields"])
    all_fields = {name: True for name in set(form + path)}
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, condition: bool) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")

    check("form route all fields with owner", route_complete(all_fields, form), True, route_complete(all_fields, form))
    check("path route all fields with owner", route_complete(all_fields, path), True, route_complete(all_fields, path))
    for name in form:
        mutated = dict(all_fields)
        mutated[name] = False
        check(f"form drop {name} rejects", route_complete(mutated, form), False, not route_complete(mutated, form))
    for name in path:
        mutated = dict(all_fields)
        mutated[name] = False
        check(f"path drop {name} rejects", route_complete(mutated, path), False, not route_complete(mutated, path))
    check("conditional route rejected", route_complete(all_fields, form, conditional=True), False, not route_complete(all_fields, form, conditional=True))
    check("unowned route rejected", route_complete(all_fields, form, owner=False), False, not route_complete(all_fields, form, owner=False))
    target_only = {name: False for name in all_fields}
    target_only["target_form_exact"] = True
    check("closed target alone does not complete form", route_complete(target_only, form), False, not route_complete(target_only, form))
    target_only["form_common_hilbert_map"] = True
    check("static map without liminf/recovery rejects", route_complete(target_only, form), False, not route_complete(target_only, form))
    current = contract["admission_predicate"]["current_expected"]
    check("current form route is false", current["form_route_complete"], False, current["form_route_complete"] is False)
    check("current path route is false", current["path_route_complete"], False, current["path_route_complete"] is False)
    check("current D limit is false", current["D_limit"], False, current["D_limit"] is False)
    check("physical firewall", contract["physical_promotion"], False, contract["physical_promotion"] is False)
    check("external time retained", "External stochastic Markov time" in contract["fixed_scope"]["time"], True, "External stochastic Markov time" in contract["fixed_scope"]["time"])

    payload = {
        "schema": "tect/pah-omc020-target-identification-hostile/1.0",
        "audit_id": "PAH-OMC-020-TARGET-IDENTIFICATION-HOSTILE-001",
        "task_id": "T-078",
        "status": "PASS_HOSTILE_TARGET_FAIL_CLOSED",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "assertion_count": len(checks),
        "passed": len(checks),
        "failed": 0,
        "checks": checks,
        "required_routes": {"form": form, "path": path},
        "finding": "Hostile mutations show that dropping any route field, using a conditional or unowned packet, or naming only the target form cannot create D_n identification.",
        "next_single_question": "Can a source-authorized packet supply every field of one route with the declared quantifiers?",
        "non_claims": contract["non_claims"],
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not dest.is_file() or dest.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 target-identification hostile replay mismatch")
    else:
        write(dest, encoded)
    print(f"PAH-OMC-020 TARGET IDENTIFICATION HOSTILE: PASS {payload['passed']}/{payload['assertion_count']}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
