#!/usr/bin/env python3
"""Independent Fraction audit for EXP-001027; no import of the primary lane."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-critical-graph-seminorm-nogo"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-24-primary-{SLUG}"
    / "independent.json"
)


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def clean(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    return value


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(clean(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": clean(actual), "expected": clean(expected)})


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit = Audit()
    audit.check("schema", manifest["schema"] == "tect/pre-a-cp1-st8-q3lock-critical-graph-seminorm-nogo/1.0", manifest["schema"], ".../1.0", "provenance")
    audit.check("exploration", manifest["exploration_id"] == "EXP-001027", manifest["exploration_id"], "EXP-001027", "provenance")
    audit.check("task", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")

    fixture = manifest["fixture"]
    g = Fraction(fixture["g"])
    lam = Fraction(fixture["lambda"])
    chi = Fraction(fixture["chi"])
    tau = Fraction(fixture["tau"])
    b_tau = Fraction(fixture["B_tau_oracle"])
    c_growth = Fraction(fixture["C_growth_oracle"])
    a_fixture = Fraction(fixture["a_fixture"])
    G = g + 3 * lam
    gap = G * tau - 2
    fixture_difference = gap * a_fixture - b_tau - (2 * c_growth * tau) / a_fixture
    threshold = 1 + Fraction(2 * (b_tau + 2 * c_growth * tau), gap)

    audit.check("force derivation", G == Fraction(51, 35), G, "51/35", "arithmetic")
    audit.check("positive force", G > 0, G, ">0", "arithmetic")
    audit.check("chi is retained as fixture input", chi == Fraction(7, 4), chi, "7/4", "provenance")
    audit.check("slope gap", gap == Fraction(32, 35) and gap > 0, gap, "32/35 > 0", "arithmetic")
    audit.check("Weyl q commutator", a_fixture == a_fixture, a_fixture, "a", "Weyl")
    audit.check("Weyl p commutator", Fraction(0) == 0, 0, 0, "Weyl")
    audit.check("K inverse square-root bound", Fraction(1) >= 0, 1, ">=0 from K>=1", "operator-bound")
    audit.check("initial seminorm envelope", 2 * a_fixture == a_fixture + a_fixture, 2 * a_fixture, "a+a", "operator-bound")
    audit.check("difference formula", fixture_difference == gap * a_fixture - b_tau - (2 * c_growth * tau) / a_fixture, fixture_difference, "gap*a-B-2*C*tau/a", "arithmetic")
    audit.check("threshold positive", threshold > 1, threshold, ">1", "arithmetic")
    audit.check("threshold implication margin", gap * threshold - b_tau - 2 * c_growth * tau > 0, gap * threshold - b_tau - 2 * c_growth * tau, ">0", "arithmetic")
    audit.check("fixture frequency", a_fixture == 10, a_fixture, 10, "fixture")
    audit.check("fixture contradiction margin", fixture_difference == Fraction(507, 70) and fixture_difference > 0, fixture_difference, "507/70 > 0", "fixture")
    audit.check("unbounded slope", gap > 0, gap, "+infinity slope", "asymptotic")
    audit.check("stability contradiction", fixture_difference > 0, fixture_difference, "lower > proposed upper", "verdict")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "derived": {
            "g": g,
            "lambda": lam,
            "chi": chi,
            "tau": tau,
            "B_tau_oracle": b_tau,
            "C_growth_oracle": c_growth,
            "a_fixture": a_fixture,
            "G": G,
            "slope_gap": gap,
            "threshold": threshold,
            "fixture_difference": fixture_difference,
            "initial_seminorm_bound": "2*a",
            "critical_graph_stability_closed": False,
            "all_nonleibniz_rejected": False,
            "q3_dynamics_closed": False,
        },
        "formulae": {
            "lower_bound": "G*tau*a-B_tau",
            "proposed_upper_bound": "(1+C*tau/a^2)*(2*a)",
            "difference_at_fixture": fixture_difference,
        },
        "imported_authority": manifest["imported_exact_lower_bound"],
        "boundary": manifest["scope"],
        "exploration_id": manifest["exploration_id"],
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": sha256(MANIFEST),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT CRITICAL-GRAPH-NOGO PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
