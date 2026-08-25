#!/usr/bin/env python3
"""Independent Fraction-only lane for EXP-001127."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-local-tail-force-a34-operator-obstruction"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-independent-{SLUG}/independent.json"


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def bond(c: Fraction, lam: Fraction, x: Fraction, y: Fraction) -> Fraction:
    d = x - y
    return c * d * d / 2 + lam * d * d * (x * x + y * y) / 4


def force(c: Fraction, lam: Fraction, x: Fraction, y: Fraction) -> Fraction:
    d = x - y
    return c * d + lam * d * (2 * x * x - x * y + y * y) / 2


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assertions: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        assertions.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001127" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001127/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    c = Fraction(1)
    lam = Fraction(1, 10)
    gamma = Fraction(1, 20)
    radius = Fraction(1)
    rows: list[dict[str, Any]] = []
    previous: Fraction | None = None
    for q in (Fraction(4), Fraction(8), Fraction(16), Fraction(32)):
        check(f"tail q={q}", q >= 2 * radius, q, f">={2 * radius}", "cutoff")
        mixed = bond(c, lam, q, Fraction(0)) * force(c, lam, q, Fraction(0))
        expected = c * c * q**3 / 2 + 3 * c * lam * q**5 / 4 + lam * lam * q**7 / 4
        check(f"expansion q={q}", mixed == expected, mixed, expected, "exact polynomial")
        lower = lam * lam * q**7 / 4
        check(f"lower q={q}", mixed >= lower, mixed, f">={lower}", "quartic tail")
        ratio = mixed**4 / (1 + gamma * q**4) ** 3
        check(f"ratio positive q={q}", ratio > 0, ratio, ">0", "graph power")
        if previous is not None:
            check(f"ratio increasing q={q}", ratio > previous, ratio, f">{previous}", "unboundedness diagnostic")
        previous = ratio
        rows.append({"q": q, "mixed": mixed, "ratio_fourth": ratio})
    q0 = Fraction(20)
    zero = bond(c, Fraction(0), q0, Fraction(0)) * force(c, Fraction(0), q0, Fraction(0))
    check("lambda zero boundary", zero == c * c * q0**3 / 2, zero, c * c * q0**3 / 2, "boundary")
    check("power count", Fraction(7) - 4 * Fraction(3, 4) == 4, Fraction(7) - 4 * Fraction(3, 4), 4, "power count")
    check("scope", manifest["scope"]["quartic_lambda_positive_operator_route_rejected"] and manifest["scope"]["state_weighted_modular_route_open"], manifest["scope"], "route firewall", "scope")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-TAIL-FORCE-A34-OPERATOR-OBSTRUCTION",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(assertions),
        "assertion_count": len(assertions),
        "assertions": assertions,
        "derived": {"ratio_rows": rows, "quartic_operator_route_rejected": True, "lambda_zero_subcase_open": True, "state_weighted_route_open": True},
        "boundary": manifest["scope"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT LOCAL-TAIL-FORCE-A34 PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
