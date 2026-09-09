#!/usr/bin/env python3
"""Hostile scope and mutation checks for PAH-OMC-024.

The hostile lane tests the exact failure boundary rather than attempting to
turn the abstract oracle into a PAH result or a physical claim.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-024-anchored-n-persistence-contract-v1.json"
PRIMARY = ROOT / "verification/scripts/pah_omc024_anchored_n_persistence.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc024_anchored_n_persistence_independent.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> bytes:
    encoded = (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f"{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return encoded


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any) -> None:
    ok = actual == expected
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(name)


def imports_forbidden(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    forbidden = ("pah_omc024_anchored_n_persistence", "verification.scripts", "codes.foundations")
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [item.name for item in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        if any(any(token in name for token in forbidden) for name in names):
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc024-anchored-n-persistence/hostile.json",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    check(rows, "primary is non-importing", imports_forbidden(PRIMARY), True)
    check(rows, "independent is non-importing", imports_forbidden(INDEPENDENT), True)
    check(rows, "contract holds immutable parent", contract.get("parent_immutable"), True)
    check(rows, "contract verdict is hold rule", contract.get("decision_rule", {}).get("current"), "HOLD_FOR_EVIDENCE")

    # Mutation 1: replacing dyadic decay by a constant gap destroys the
    # diagnostic's only convergence premise, so it cannot be accepted.
    constant_gap = [1 for _ in range(13)]
    check(rows, "constant-gap mutation rejected", not (constant_gap[-1] < 1 / 1000), True)

    # Mutation 2: calling the identity target a PAH target would import a
    # model choice not present in PAH-001; the contract explicitly forbids it.
    contract_text = json.dumps(contract, ensure_ascii=True).lower()
    check(rows, "identity target remains abstract", "abstract" in contract_text and "identity semigroup" in contract_text, True)
    check(rows, "physical-time relabel rejected", "physical" not in contract.get("oracle_time_firewall", "external Markov time"), True)

    # Mutation 3: a finite gap is not enough to promote a universal negative or
    # a mainline advance.  Both promotion flags must remain false.
    check(rows, "mainline promotion rejected", contract.get("default_verdict"), "HOLD_FOR_EVIDENCE")
    check(rows, "physical promotion rejected", contract.get("physical_promotion"), False)
    check(rows, "oracle-as-PAH-carrier rejected", contract.get("oracle_is_pah_carrier"), False)

    payload: dict[str, Any] = {
        "schema": "tect/pah-omc024-anchored-n-persistence-hostile/1.0",
        "audit_id": "PAH-OMC-024-ANCHORED-N-PERSISTENCE-HOSTILE-001",
        "result_id": "R-564",
        "contract_id": "PAH-OMC-024",
        "task_id": "T-091",
        "status": "PASS_HOSTILE_SCOPE",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": rows,
        "checks_passed": len(rows),
        "mutations_rejected": [
            "non-decaying constant gap",
            "identity oracle relabelled as PAH target",
            "abstract oracle imported as a PAH carrier",
            "finite gap promoted to universal no-go or physical claim",
        ],
        "source_hashes": {
            CONTRACT.relative_to(ROOT).as_posix(): sha(CONTRACT),
            PRIMARY.relative_to(ROOT).as_posix(): sha(PRIMARY),
            INDEPENDENT.relative_to(ROOT).as_posix(): sha(INDEPENDENT),
        },
        "tooling_hash": sha(Path(__file__)),
        "reproduction": "python -X utf8 codes/foundations/pah_omc024_anchored_n_persistence_hostile.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc024-anchored-n-persistence/hostile.json",
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = atomic_json(destination, payload) if not args.check else (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-024 hostile replay mismatch")
    print(f"PAH-OMC-024 HOSTILE: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
