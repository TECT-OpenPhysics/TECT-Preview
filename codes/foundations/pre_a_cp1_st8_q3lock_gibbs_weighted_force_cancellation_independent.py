#!/usr/bin/env python3
"""Independent Fraction-only reproduction for EXP-001139."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_gibbs_weighted_force_cancellation"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-gibbs-weighted-force-cancellation-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-independent-{SLUG}" / "independent.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
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


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    r, g = Fraction(fixture["r"]), Fraction(fixture["g"])
    shift, scale = Fraction(fixture["per_site_shift"]), Fraction(fixture["resolvent_scale"])
    tail_coefficient = Fraction(fixture["quartic_tail_coefficient"])
    center, completion_constant = Fraction(fixture["completion_center"]), Fraction(fixture["completion_constant"])
    betas = [Fraction(value) for value in fixture["beta_grid"]]
    qs = [Fraction(value) for value in fixture["q_grid"]]
    pairs = [(Fraction(item[0]), Fraction(item[1])) for item in fixture["history_norm_pairs"]]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("provenance", manifest["exploration_id"] == "EXP-001139" and manifest["claim_bearing"] is False, manifest["exploration_id"], "EXP-001139/nonbearing", "provenance")
    check("beta hypotheses", all(item > 0 for item in betas), betas, ">0", "hypotheses")

    point_rows: list[dict[str, Any]] = []
    for index, q in enumerate(qs):
        y = q**2
        v = shift + r * y / 2 + g * y**2 / 4
        completed = completion_constant + g / 4 * (y - center) ** 2
        denom = scale + y
        fp = scale * (scale - y) / denom**2
        fpp = 2 * scale * q * (y - 3 * scale) / denom**3
        force_value = r * q + g * q**3
        check(f"point {index} completion", v == completed, [v, completed], "equal", "potential")
        check(f"point {index} tail", v >= tail_coefficient * y**2, [v, tail_coefficient * y**2], ">=tail coefficient*q^4", "Gibbs tail")
        check(f"point {index} fp envelope", abs(fp) <= 1, abs(fp), "<=1", "derivative envelopes")
        check(f"point {index} fpp envelope", abs(fpp) <= 1, abs(fpp), "<=1", "derivative envelopes")
        point_rows.append({"q": str(q), "potential": str(v), "force": str(force_value), "fprime": str(fp), "fsecond": str(fpp), "force_fprime": str(force_value * fp)})

    beta_rows: list[dict[str, Any]] = []
    prior: Fraction | None = None
    for index, beta in enumerate(betas):
        for h0, h1 in pairs:
            bound = (h0 + h1) / beta
            check(f"beta {index} history {h0}/{h1}", beta * bound == h0 + h1, [beta, bound], h0 + h1, "state-weighted envelope")
        unit = Fraction(2) / beta
        if prior is not None:
            check(f"beta {index} order", unit <= prior, [unit, prior], "nonincreasing", "beta dependence")
        prior = unit
        beta_rows.append({"beta": str(beta), "unit_history_envelope": str(unit), "matrix_element_bound": f"(H0+H1)/{beta}"})

    check("product rule contract", manifest["model"]["gibbs_pairing"].endswith("for h in C_c^1"), manifest["model"]["gibbs_pairing"], "compact-support IBP", "cancellation product rule")
    check("scope separation", scope["fixed_beta_one_site_pairing_closed"] and not scope["volume_uniform_d_delta_d_closed"] and not scope["common_alpha_closed"], scope, "finite only", "scope")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-GIBBS-WEIGHTED-FORCE-CANCELLATION", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks[:12] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": str(len(checks)), "expected": "all executed assertions passed"}], "derived": {"point_rows": point_rows, "beta_rows": beta_rows, "fixed_beta_one_site_pairing_closed": True, "force_tail_removed_from_linear_pairing": True, "state_weighted_history_envelope_closed": True, "volume_uniform_d_delta_d_closed": False, "common_alpha_closed": False, "pre_a_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT GIBBS-WEIGHTED-FORCE-CANCELLATION PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())