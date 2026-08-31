#!/usr/bin/env python3
"""Fail-closed mutation lane for the R-474 ordered-limit contract."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-q3lock-ordered-limit-rectangle-manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "C6-SPACETIME-SIGNATURE" / "runs" / "2026-08-31-hostile-r474-ordered-limit-rectangle" / "hostile.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fraction(value: str | int) -> Fraction:
    return Fraction(str(value))


def canonical_fixture(manifest: dict[str, Any]) -> dict[str, Any]:
    fixture = manifest["fixture"]
    limit = fraction(fixture["limit"])
    cutoff_base = int(fixture["cutoff_base"])
    volume_base = int(fixture["volume_base"])
    split = int(fixture["epsilon_split_denominator"])
    maximum = int(fixture["max_index"])
    records: list[dict[str, Any]] = []
    for raw in fixture["epsilon_values"]:
        epsilon = fraction(raw)
        half = epsilon / split
        cutoff_candidates = [n for n in range(maximum + 1) if Fraction(1, cutoff_base ** (n + 1)) < half]
        volume_candidates = [m for m in range(maximum + 1) if Fraction(1, volume_base ** (m + 1)) < half]
        if not cutoff_candidates or not volume_candidates:
            raise AssertionError("fixture threshold missing")
        n0 = min(cutoff_candidates)
        m0 = min(volume_candidates)
        cutoff_tail = Fraction(1, cutoff_base ** (n0 + 1))
        volume_tail = Fraction(1, volume_base ** (m0 + 1))
        records.append({"epsilon": str(epsilon), "half": str(half), "cutoff_threshold": n0, "volume_threshold": m0, "rectangle": str(cutoff_tail + volume_tail)})
    return {"limit": str(limit), "cutoff_base": cutoff_base, "volume_base": volume_base, "split": split, "records": records}


def valid_contract(payload: dict[str, Any]) -> bool:
    if payload.get("result_id") != "R-474" or payload.get("exploration_id") != "EXP-001353":
        return False
    if payload.get("tier") != "T0" or payload.get("claim_bearing") is not False:
        return False
    fixture = payload.get("fixture", {})
    if fixture.get("epsilon_split_denominator") != 2:
        return False
    if fixture.get("cutoff_base", 0) <= 1 or fixture.get("volume_base", 0) <= 1:
        return False
    if fixture.get("cutoff_error_formula") != "1/(cutoff_base^(n+1))":
        return False
    if fixture.get("volume_error_formula") != "1/(volume_base^(m+1))":
        return False
    if payload.get("model", {}).get("order_forward") != ["cutoff", "volume"]:
        return False
    if payload.get("model", {}).get("order_reverse") != ["volume", "cutoff"]:
        return False
    if not all(payload.get("method_preservation", {}).values()):
        return False
    scope = payload.get("scope", {})
    for key in ("source_owned_functional_closed", "source_owned_dynamics_closed", "common_core_closed", "common_norm_closed", "uniform_cutoff_bound_closed", "uniform_volume_bound_closed", "ordered_limit_closed", "physical_sector_closed", "continuum_closed", "pre_a_closed", "sector_a_closed", "qft_yang_mills_closed"):
        if scope.get(key) is not False:
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = read(MANIFEST)
    if not valid_contract(manifest):
        print("R-474 HOSTILE: FAIL (base contract rejected)")
        return 1
    mutations: list[tuple[str, dict[str, Any]]] = []
    def mutate(name: str, path: tuple[str, ...], value: Any) -> None:
        item = copy.deepcopy(manifest)
        target: Any = item
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        mutations.append((name, item))
    mutate("wrong result id", ("result_id",), "R-999")
    mutate("claim-bearing promotion", ("claim_bearing",), True)
    mutate("tier promotion", ("tier",), "T1")
    mutate("wrong epsilon split", ("fixture", "epsilon_split_denominator"), 3)
    mutate("cutoff base no decay", ("fixture", "cutoff_base"), 1)
    mutate("volume base no decay", ("fixture", "volume_base"), 1)
    mutate("cutoff formula mutation", ("fixture", "cutoff_error_formula"), "1/(cutoff_base^n)")
    mutate("forward order swap", ("model", "order_forward"), ["volume", "cutoff"])
    mutate("owner uniformity promotion", ("scope", "uniform_cutoff_bound_closed"), True)
    mutate("method mutation", ("method_preservation", "t054_forward_method_unchanged"), False)
    rows = [{"name": name, "rejected": not valid_contract(item), "expected": "rejected"} for name, item in mutations]
    if any(not row["rejected"] for row in rows):
        print("R-474 HOSTILE: FAIL (mutation accepted)")
        return 1
    core = canonical_fixture(manifest)
    fingerprint = hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    payload = {
        "schema": "tect/r474-ordered-limit-rectangle-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": "R474-ORDERED-LIMIT-RECTANGLE-HOSTILE-v1",
        "result_id": "R-474",
        "exploration_id": "EXP-001353",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "task_id": "T-054",
        "tier": "T0",
        "claim_bearing": False,
        "verdict": "HOSTILE_MUTATIONS_REJECTED",
        "mutations": rows,
        "mutation_summary": {"rejected": sum(row["rejected"] for row in rows), "total": len(rows)},
        "base_core_fingerprint": fingerprint,
        "source_hashes": {"manifest": digest(MANIFEST), "hostile": digest(Path(__file__))},
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["boundary"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, args.output)
    print(f"R-474 HOSTILE: PASS ({payload['mutation_summary']['rejected']}/{payload['mutation_summary']['total']} mutations rejected; fingerprint={fingerprint})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
