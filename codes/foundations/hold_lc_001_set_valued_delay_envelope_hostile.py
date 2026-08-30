#!/usr/bin/env python3
"""Hostile scope mutations for HOLD-LC-001 set-valued feasibility only."""

from __future__ import annotations

import argparse
import copy
import json
import os
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "strategy/hold-lc-001-set-valued-delay-envelope-v0.1.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-hold_lc_001_set_valued_delay_envelope/hostile.json"


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def valid(data: dict[str, Any]) -> bool:
    try:
        if data.get("claim_bearing") is not False or data.get("methods_unchanged") is not True:
            return False
        if data.get("status") != "SET_VALUED_FEASIBILITY_ONLY_NOT_SCORED":
            return False
        if data["nuisance_contract"].get("difference_convention") != "delta_t_prop = delta_t_det - tau_em":
            return False
        if data["derived_set_valued_rule"].get("operation") != "interval_subtraction":
            return False
        admission = data["admission"]
        if any(admission[key] is not False for key in ("likelihood_admitted", "covariance_admitted", "aggregate_scoring_allowed", "prospective_credit")):
            return False
        if set(admission["forward_map_stages"].values()) != {"NOT_ADMITTED"}:
            return False
        display = data["estimand_contract"]["display_envelope"]
        dlo, dhi = Fraction(display["lower"]), Fraction(display["upper"])
        if dlo > dhi:
            return False
        expected = {}
        for item in data["nuisance_contract"]["scenarios"]:
            ilo, ihi = Fraction(item["lower"]), Fraction(item["upper"])
            if ilo > ihi:
                return False
            expected[item["id"]] = (dlo - ihi, dhi - ilo)
        declared = data["derived_set_valued_rule"]["scenario_envelopes"]
        if any({"lower": str(bounds[0]), "upper": str(bounds[1])} != declared[sid] for sid, bounds in expected.items()):
            return False
        union = (min(bounds[0] for bounds in expected.values()), max(bounds[1] for bounds in expected.values()))
        du = data["derived_set_valued_rule"]["union_envelope"]
        return (str(union[0]), str(union[1])) == (du["lower"], du["upper"])
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    mutations: list[tuple[str, Any]] = []

    def add(name: str, change: Any) -> None:
        candidate = copy.deepcopy(data)
        change(candidate)
        mutations.append((name, candidate))

    add("Gaussian admission", lambda x: x["admission"].__setitem__("likelihood_admitted", True))
    add("covariance admission", lambda x: x["admission"].__setitem__("covariance_admitted", True))
    add("aggregate score", lambda x: x["admission"].__setitem__("aggregate_scoring_allowed", True))
    add("prospective credit", lambda x: x["admission"].__setitem__("prospective_credit", True))
    add("map admission", lambda x: x["admission"]["forward_map_stages"].__setitem__("F_obs", "ADMITTED"))
    add("claim promotion", lambda x: x.__setitem__("claim_bearing", True))
    add("method replacement", lambda x: x.__setitem__("methods_unchanged", False))
    add("scenario omission", lambda x: x["nuisance_contract"]["scenarios"].pop())
    add("interval inversion", lambda x: x["estimand_contract"]["display_envelope"].__setitem__("lower", "179/100"))
    add("derived mismatch", lambda x: x["derived_set_valued_rule"]["scenario_envelopes"]["simultaneous"].__setitem__("upper", "180/100"))
    add("wrong difference convention", lambda x: x["nuisance_contract"].__setitem__("difference_convention", "delta_t_prop = tau_em - delta_t_det"))
    add("speed substitution", lambda x: x["derived_set_valued_rule"].__setitem__("operation", "speed_conversion"))

    rejected = sum(not valid(candidate) for _, candidate in mutations)
    if rejected != len(mutations):
        failed = [name for name, candidate in mutations if valid(candidate)]
        raise AssertionError(f"hostile mutation accepted: {failed}")
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "hostile",
        "audit_id": "HOLD-LC-001-SET-VALUED-DELAY-ENVELOPE-HOSTILE",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "task_id": data["task_id"],
        "holdout_id": data["holdout_id"],
        "verdict": "PASS",
        "mutation_count": len(mutations),
        "mutations_rejected": rejected,
        "mutations": [{"name": name, "rejected": not valid(candidate)} for name, candidate in mutations],
        "boundary": data["non_claims"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if not args.self_test: store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"HOSTILE HOLD-LC-001 SET-VALUED ENVELOPE PASS {rejected}/{len(mutations)} mutations rejected")
    return 0


if __name__ == "__main__": raise SystemExit(main())
