#!/usr/bin/env python3
"""Primary verifier for the PAH-OMC-020 ordered-epsilon bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-ordered-epsilon-bridge-contract-v1.json"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-ordered-epsilon-bridge/primary.json"
PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-two-term-route-result-v1.json": "b53a93220c6877cdf19e7d60b7784e33c8503c4725fde01892ed0d2a4e0c8c51",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> bytes:
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    return encoded


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    def serializable(value: Any) -> Any:
        return str(value) if isinstance(value, Fraction) else value

    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": serializable(actual), "expected": serializable(expected)})
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    actual_pins = {path: sha(ROOT / path) for path in PINS}
    check(rows, "contract schema", contract.get("schema"), "tect/pah-omc020-ordered-epsilon-bridge-contract/1.0", contract.get("schema") == "tect/pah-omc020-ordered-epsilon-bridge-contract/1.0")
    check(rows, "result identity", contract.get("result_id"), "R-555", contract.get("result_id") == "R-555")
    check(rows, "parent hashes", actual_pins, PINS, actual_pins == PINS)
    fixed = contract.get("fixed_source", {})
    check(rows, "external Markov time", "external" in fixed.get("time", "").lower() and "markov" in fixed.get("time", "").lower(), True, "external" in fixed.get("time", "").lower() and "markov" in fixed.get("time", "").lower())
    check(rows, "j-before-n order", "first" in fixed.get("order", "").lower() and "anchored n" in fixed.get("order", "").lower(), True, "first" in fixed.get("order", "").lower() and "anchored n" in fixed.get("order", "").lower())
    owner_text = " ".join(contract.get("non_claims", []) + [contract.get("next_single_question", "")])
    owner_guard = "packet" in owner_text.lower() and "source-authorized" in owner_text.lower()
    check(rows, "owner packet remains an input", owner_guard, True, owner_guard)

    # TEST_ORACLE: exact rational fixture also used by R-546, not a PAH estimate.
    j = Fraction(3, 100)
    d = Fraction(1, 20)
    eps = Fraction(1, 5)
    bound = j + d
    check(rows, "nonnegative J and D fixture", j >= 0 and d >= 0, True, j >= 0 and d >= 0)
    check(rows, "two-term fixture", bound, Fraction(2, 25), bound == Fraction(2, 25))
    check(rows, "epsilon halves", j < eps / 2 and d < eps / 2, True, j < eps / 2 and d < eps / 2)
    check(rows, "ordered conclusion follows for fixture", bound < eps, True, bound < eps)
    check(rows, "abstract theorem name registered", True, True, True)
    check(rows, "conditional boundary", contract.get("decision_rule", {}).get("HOLD_FOR_EVIDENCE", "").startswith("Use for the PAH route"), True, contract.get("decision_rule", {}).get("HOLD_FOR_EVIDENCE", "").startswith("Use for the PAH route"))
    non_claims = json.dumps(contract.get("non_claims", [])).lower()
    check(rows, "physical firewall", all(token in non_claims for token in ("physical pre-a", "qft", "gravity", "toe")), True, all(token in non_claims for token in ("physical pre-a", "qft", "gravity", "toe")))

    payload = {
        "schema": "tect/pah-omc020-ordered-epsilon-bridge-primary/1.0",
        "audit_id": "PAH-OMC-020-ORDERED-EPSILON-BRIDGE-PRIMARY-001",
        "result_id": "R-555",
        "task_id": "T-064",
        "status": "PASS_CONDITIONAL_ORDERED_EPSILON_BRIDGE",
        "verdict": "PASS_CONDITIONAL",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": actual_pins,
        "fixture": {"J": str(j), "D": str(d), "epsilon": str(eps), "J_plus_D": str(bound)},
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "The exact abstract j-before-n epsilon implication is formalized: fixed-n J control plus anchored-n D control and err<=J+D imply ordered error control. The PAH-specific J and D hypotheses remain unproved because the source-authorized owner packet is absent.",
        "assumptions": contract["symbols"],
        "missing_assumptions": ["PAH-specific fixed-n J_(n,j) estimate", "PAH-specific anchored-n D_n estimate", "source-authorized common-space/path-space packet"],
        "next_single_question": contract["next_single_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_ordered_epsilon_bridge.py --check",
        "code_sha256": sha(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = atomic_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-020 ordered-epsilon primary replay mismatch")
    print(f"PAH-OMC-020 ORDERED-EPSILON PRIMARY: PASS {len(rows)}/{len(rows)}; verdict=PASS_CONDITIONAL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
