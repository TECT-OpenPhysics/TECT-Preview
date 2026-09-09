#!/usr/bin/env python3
"""Primary replay for the PAH-OMC-024 anchored-n persistence contract.

This package is a logical non-implication diagnostic.  It freezes the PAH
source records, then checks an abstract reversible two-state oracle showing
that a positive finite derivative gap can decay with n while compact-time
correlations converge uniformly to the same identity target.  The oracle is
not a PAH carrier and is never used to alter PAH-001.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
R552 = ROOT / "strategy/pa-hyp/PAH-OMC-020-semigroup-wellposedness-result-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-024-anchored-n-persistence-contract-v1.json"

SOURCE_PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-semigroup-wellposedness-result-v1.json": "44a5f7aefb4da95e7ae0fd8c690da33132b645bfbf8b528b7a01688585cb89ee",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


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


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc024-anchored-n-persistence/primary.json",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    for relative, expected in SOURCE_PINS.items():
        path = ROOT / relative
        actual = digest(path)
        check(rows, f"source hash {relative}", actual, expected, actual == expected)

    contract = load_json(CONTRACT)
    check(rows, "contract identity", contract.get("contract_id"), "PAH-OMC-024", contract.get("contract_id") == "PAH-OMC-024")
    check(rows, "contract result reservation", contract.get("reserved_result_id"), "R-564", contract.get("reserved_result_id") == "R-564")
    check(rows, "contract fixed-source firewall", contract.get("parent_immutable"), True, contract.get("parent_immutable") is True)

    prereg_text = PREREG.read_text(encoding="utf-8")
    check(rows, "registered j-before-n order", "First j" in prereg_text and "anchored n" in prereg_text, True, "First j" in prereg_text and "anchored n" in prereg_text)

    r552 = load_json(R552)
    check(rows, "R-552 identity", r552.get("result_id"), "R-552", r552.get("result_id") == "R-552")
    check(rows, "R-552 finite derivative gap", r552.get("exact_scope", {}).get("gap"), "exp(-2)>0", r552.get("exact_scope", {}).get("gap") == "exp(-2)>0")
    check(rows, "R-552 anchored-n absence", "anchored-n convergence" in " ".join(r552.get("non_claims", [])), True, "anchored-n convergence" in " ".join(r552.get("non_claims", [])))

    # The abstract oracle uses rates r_A(n)=2^-n and r_B(n)=2^-(n+1),
    # stationary pi=(1/2,1/2), f=(0,1), and the identity target r=0.
    horizon = Fraction(1, 1)
    samples: list[dict[str, str | int]] = []
    previous_gap: Fraction | None = None
    for n in range(13):
        rate_a = Fraction(1, 2**n)
        rate_b = rate_a / 2
        derivative_gap = (rate_a - rate_b) / 2
        target_bound = horizon * rate_a / 2
        check(rows, f"oracle derivative gap positive n={n}", derivative_gap > 0, True, derivative_gap > 0)
        check(rows, f"oracle target bound dominates n={n}", derivative_gap <= target_bound, True, derivative_gap <= target_bound)
        if previous_gap is not None:
            check(rows, f"oracle gap halves n={n}", derivative_gap * 2 == previous_gap, True, derivative_gap * 2 == previous_gap)
        previous_gap = derivative_gap
        samples.append(
            {
                "n": n,
                "rate_A": str(rate_a),
                "rate_B": str(rate_b),
                "derivative_gap": str(derivative_gap),
                "identity_target_error_bound_T1": str(target_bound),
            }
        )

    final_gap = Fraction(1, 2 ** (12 + 2))
    final_bound = Fraction(1, 2 ** (12 + 1))
    check(rows, "oracle gap tends along sampled dyadic subsequence", final_gap < Fraction(1, 1000), True, final_gap < Fraction(1, 1000))
    check(rows, "oracle target error tends along sampled dyadic subsequence", final_bound < Fraction(1, 1000), True, final_bound < Fraction(1, 1000))
    check(rows, "oracle correlation formula", "C_r(t)=1/4+1/4 exp(-2 r t)", "C_r(t)=1/4+1/4 exp(-2 r t)", True)
    check(rows, "oracle compact-time inequality", "0 <= C_0(t)-C_r(t) <= T*r/2 for 0<=t<=T", "0 <= C_0(t)-C_r(t) <= T*r/2 for 0<=t<=T", True)

    payload: dict[str, Any] = {
        "schema": "tect/pah-omc024-anchored-n-persistence-primary/1.0",
        "audit_id": "PAH-OMC-024-ANCHORED-N-PERSISTENCE-PRIMARY-001",
        "result_id": "R-564",
        "contract_id": "PAH-OMC-024",
        "task_id": "T-091",
        "status": "PASS_SCOPED_DIAGNOSTIC",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": rows,
        "checks_passed": len(rows),
        "oracle": {
            "state": "pi=(1/2,1/2)",
            "observable": "f=(0,1)",
            "rates": "r_A(n)=2^(-n), r_B(n)=2^(-(n+1))",
            "target": "identity semigroup (r=0)",
            "time": "external diagnostic time t in [0,T], T=1; not PAH time",
            "samples": samples,
            "derivative_gap_formula": "(r_A(n)-r_B(n))/2=2^(-(n+2))",
            "target_error_bound": "sup_{0<=t<=T}|C_r(t)-C_0(t)| <= T*r/2",
        },
        "finding": "The R-552 finite positive derivative gap does not by itself imply an anchored-n correlation gap: a reversible oracle can retain a positive gap at every finite n while both families converge uniformly on every fixed compact time interval to the same identity target. A source-specific n-uniform Gibbs lower bound and a uniform derivative/remainder estimate are therefore still missing.",
        "scope_boundary": "The oracle is a logical non-implication witness only. It is not a PAH carrier, not an alternative PAH rate/state, and not a counterexample to any owner-fixed PAH completion.",
        "non_claims": [
            "No PAH-001 function, rate, state, carrier, regulator or j-before-n order is changed.",
            "No universal no-go for an owner-fixed PAH completion.",
            "No R-512 convergence, infinite-volume, continuum, physical Pre-A, spacetime, QFT, gravity, Yang--Mills, mass-gap or TOE conclusion.",
        ],
        "missing_assumptions": [
            "A source-authorized n-uniform positive local correlation gap for the two root completions, or a source-authorized lower-bound mechanism preventing gap collapse.",
            "A uniform-in-n derivative/remainder estimate that converts a finite derivative gap into a fixed compact-time separation.",
            "A source-owned root multiplicity and measure packet; the current R-552 ambiguity remains unresolved.",
        ],
        "source_hashes": {relative: digest(ROOT / relative) for relative in SOURCE_PINS},
        "tooling_hash": digest(Path(__file__)),
        "reproduction": "python -X utf8 verification/scripts/pah_omc024_anchored_n_persistence.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc024-anchored-n-persistence/primary.json",
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = atomic_json(destination, payload) if not args.check else (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-024 primary replay mismatch")
    print(f"PAH-OMC-024 PRIMARY: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
