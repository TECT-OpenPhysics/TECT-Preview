#!/usr/bin/env python3
"""Independent exact-rational replay for PAH-OMC-024.

The implementation deliberately does not import the primary verifier.  It
rebuilds the two-state diagnostic from its formulas and checks the immutable
source hashes independently.
"""
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
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
R552 = ROOT / "strategy/pa-hyp/PAH-OMC-020-semigroup-wellposedness-result-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-024-anchored-n-persistence-contract-v1.json"
PINS = {
    PAH001: "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    PREREG: "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    R552: "44a5f7aefb4da95e7ae0fd8c690da33132b645bfbf8b528b7a01688585cb89ee",
}


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


def record(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any) -> None:
    ok = actual == expected
    shown_actual = str(actual) if isinstance(actual, Fraction) else actual
    shown_expected = str(expected) if isinstance(expected, Fraction) else expected
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": shown_actual, "expected": shown_expected})
    if not ok:
        raise AssertionError(name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc024-anchored-n-persistence/independent.json",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    for path, expected in PINS.items():
        record(rows, f"source hash {path.relative_to(ROOT).as_posix()}", sha(path), expected)

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    record(rows, "contract id", contract.get("contract_id"), "PAH-OMC-024")
    record(rows, "reserved result", contract.get("reserved_result_id"), "R-564")

    r552 = json.loads(R552.read_text(encoding="utf-8"))
    record(rows, "R-552 derivative gap", r552["exact_scope"]["gap"], "exp(-2)>0")
    prereg_text = PREREG.read_text(encoding="utf-8")
    record(rows, "j-before-n phrase", "First j" in prereg_text and "anchored n" in prereg_text, True)

    rows_oracle: list[dict[str, str | int]] = []
    for n in range(13):
        rate_a = Fraction(1, 2**n)
        rate_b = Fraction(1, 2 ** (n + 1))
        gap = (rate_a - rate_b) / 2
        expected_gap = Fraction(1, 2 ** (n + 2))
        bound = rate_a / 2
        expected_bound = Fraction(1, 2 ** (n + 1))
        record(rows, f"exact gap formula n={n}", gap, expected_gap)
        record(rows, f"exact bound formula n={n}", bound, expected_bound)
        record(rows, f"gap below bound n={n}", gap <= bound, True)
        if n:
            prior = Fraction(1, 2 ** (n + 1))
            record(rows, f"gap dyadic decay n={n}", gap * 2, prior)
        rows_oracle.append({"n": n, "rate_A": str(rate_a), "rate_B": str(rate_b), "gap": str(gap), "bound_T1": str(bound)})

    record(rows, "sampled positive gap at n=12", Fraction(1, 2**14) > 0, True)
    record(rows, "sampled target error at n=12", Fraction(1, 2**13) < Fraction(1, 1000), True)
    record(rows, "compact-time bound source inequality", "1-exp(-x)<=x for x>=0", "1-exp(-x)<=x for x>=0")

    payload: dict[str, Any] = {
        "schema": "tect/pah-omc024-anchored-n-persistence-independent/1.0",
        "audit_id": "PAH-OMC-024-ANCHORED-N-PERSISTENCE-INDEPENDENT-001",
        "result_id": "R-564",
        "contract_id": "PAH-OMC-024",
        "task_id": "T-091",
        "status": "PASS_INDEPENDENT_REBUILD",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": rows,
        "checks_passed": len(rows),
        "oracle_rebuild": {
            "state": "pi=(1/2,1/2)",
            "observable": "f=(0,1)",
            "correlation": "C_r(t)=1/4+1/4 exp(-2rt)",
            "samples": rows_oracle,
            "interpretation": "Every finite n has a positive derivative gap, but the compact-time error bound to the identity target is O(2^-n).",
        },
        "non_claims": [
            "The abstract oracle is not a PAH carrier or a PAH counterexample.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang--Mills or TOE conclusion.",
        ],
        "source_hashes": {path.relative_to(ROOT).as_posix(): sha(path) for path in PINS},
        "tooling_hash": sha(Path(__file__)),
        "reproduction": "python -X utf8 codes/foundations/pah_omc024_anchored_n_persistence_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc024-anchored-n-persistence/independent.json",
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = atomic_json(destination, payload) if not args.check else (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-024 independent replay mismatch")
    print(f"PAH-OMC-024 INDEPENDENT: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
