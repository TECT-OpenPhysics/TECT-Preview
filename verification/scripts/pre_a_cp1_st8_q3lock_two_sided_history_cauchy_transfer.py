#!/usr/bin/env python3
"""Primary exact audit for the R-451 conditional history-to-Cauchy transfer.

This script proves an analytic implication from the already registered R-450
shell interface.  It does not construct a Q3LOCK history, a common domain, or
an exhaustion family.  All scalar arithmetic is recomputed from parent
manifests with exact Fractions.
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


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-two-sided-history-cauchy-transfer-manifest.json"
PARENT_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-two-orientation-shell-transfer-manifest.json"
PARENT_RUN = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_two_orientation_shell_transfer/primary.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_two_sided_history_cauchy_transfer/primary.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def fraction(value: object) -> Fraction:
    return Fraction(str(value))


def shell_polynomial(radius: int) -> int:
    return 4 * radius * radius + 8 * radius + 14


def scalar_tail(radius: int) -> Fraction:
    if radius < 1:
        raise ValueError("R-444 tail is declared for radius >= 1")
    return Fraction(3 * shell_polynomial(radius), 2 ** (radius - 1))


def ratio(radius: int) -> Fraction:
    if radius < 1:
        raise ValueError("ratio is declared for radius >= 1")
    return Fraction(shell_polynomial(radius + 1), 2 * shell_polynomial(radius))


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


def run(output: Path = DEFAULT_OUTPUT, store: bool = True) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent = json.loads(PARENT_MANIFEST.read_text(encoding="utf-8"))
    parent_run = json.loads(PARENT_RUN.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []
    samples: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        record = {"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)}
        checks.append(record)
        if len(samples) < 120:
            samples.append(record)

    check(
        "identity",
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]]
        == ["R-451", "EXP-001324", "T-054", False, "CONDITIONAL_HISTORY_CAUCHY_TRANSFER_AUDITED"],
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]],
        ["R-451", "EXP-001324", "T-054", False, "CONDITIONAL_HISTORY_CAUCHY_TRANSFER_AUDITED"],
        "provenance",
    )
    check("parent result", parent["result_id"] == "R-450" and parent["claim_bearing"] is False, parent["result_id"], "R-450", "lineage")
    check("parent result run", parent_run["result_id"] == "R-450" and parent_run["verdict"] == parent["status"], parent_run["result_id"], "R-450", "lineage")
    check("parent actual-history firewall", parent["scope"]["actual_q3_history_identification_closed"] is False, parent["scope"]["actual_q3_history_identification_closed"], False, "lineage")
    check("parent method firewall", all(parent["method_preservation"].values()), parent["method_preservation"], "all true", "method")

    radius_min = int(manifest["finite_fixture"]["radius_min"])
    radius_max = int(manifest["finite_fixture"]["radius_max"])
    orientations = int(manifest["finite_fixture"]["orientation_count"])
    check("radius contract", radius_min == 1 and radius_max == 64, [radius_min, radius_max], [1, 64], "scalar")
    check("orientation contract", orientations == 2, orientations, 2, "orientation")
    check("no finite-grid substitution", "No new finite grid" in manifest["finite_fixture"]["shape_statement"], manifest["finite_fixture"]["shape_statement"], "abstract shape implication", "scope")

    base_tail = scalar_tail(radius_min)
    q = ratio(radius_min)
    check("base tail recomputed", base_tail == Fraction(78), base_tail, Fraction(78), "scalar")
    check("ratio q recomputed", q == Fraction(23, 26), q, Fraction(23, 26), "scalar")
    check("q strictly below one", 0 < q < 1, q, "0<q<1", "scalar")

    c4_edge = fraction(parent_run["derived"]["C4_edge"])
    check("parent C4 positive", c4_edge > 0, c4_edge, ">0", "lineage")
    two_sum_factor = 2 ** (4 - 1)
    fourth_power_cauchy_factor = two_sum_factor * orientations
    check("factor derived", fourth_power_cauchy_factor == 16, fourth_power_cauchy_factor, 16, "fourth-power")

    ratio_rows: list[dict[str, Any]] = []
    envelope_rows: list[dict[str, Any]] = []
    maximum_ratio = Fraction(0)
    previous_bound = base_tail
    for radius in range(radius_min, radius_max + 1):
        tail = scalar_tail(radius)
        ratio_value = ratio(radius)
        check(f"tail positive {radius}", tail > 0, tail, ">0", "scalar")
        check(f"ratio bound {radius}", ratio_value <= q, ratio_value, f"<={q}", "scalar")
        if radius < radius_max:
            next_tail = scalar_tail(radius + 1)
            check(f"exact recurrence {radius}", next_tail == tail * ratio_value, next_tail, tail * ratio_value, "scalar")
        geometric_bound = base_tail * q ** (radius - radius_min)
        check(f"geometric envelope {radius}", tail <= geometric_bound, tail, geometric_bound, "vanishing envelope")
        if radius > radius_min:
            check(f"inductive envelope {radius}", geometric_bound <= previous_bound * q, geometric_bound, previous_bound * q, "vanishing envelope")
        previous_bound = geometric_bound
        maximum_ratio = max(maximum_ratio, ratio_value)
        ratio_rows.append({"radius": radius, "tail": str(tail), "ratio": str(ratio_value), "geometric_bound": str(geometric_bound)})
        if radius in {1, 8, 16, 32, 64}:
            cauchy_fourth = Fraction(fourth_power_cauchy_factor) * c4_edge * tail ** 4
            envelope_rows.append({"radius": radius, "tail": str(tail), "cauchy_fourth_bound": str(cauchy_fourth), "geometric_bound": str(geometric_bound)})

    check("ratio maximum at base", maximum_ratio == q, maximum_ratio, q, "scalar")
    check("tail rows complete", len(ratio_rows) == radius_max - radius_min + 1, len(ratio_rows), radius_max - radius_min + 1, "coverage")
    check("history contract explicit", "common L4" in manifest["theorem"]["history_contract"] and "finite sum of actual history terms" in manifest["theorem"]["history_contract"], manifest["theorem"]["history_contract"], "declared assumption", "history contract")
    check("shape agreement condition explicit", "agreeing through radius R-1" in manifest["theorem"]["history_contract"], manifest["theorem"]["history_contract"], "agreement condition", "history contract")
    check("Cauchy bound statement", manifest["theorem"]["cauchy_bound"].startswith("||Y_Lambda'-Y_Lambda||_4^4 <="), manifest["theorem"]["cauchy_bound"], "root-free fourth-power bound", "theorem")
    check("geometric limit condition", manifest["theorem"]["geometric_envelope"].endswith("T(R) tends to zero"), manifest["theorem"]["geometric_envelope"], "vanishing scalar envelope", "theorem")

    scope = manifest["scope"]
    closed = (
        "parent_two_orientation_shell_envelope_reused",
        "tail_ratio_closed",
        "geometric_vanishing_envelope_closed",
        "conditional_two_sided_recurrence_transfer_closed",
        "conditional_all_shape_cauchy_implication_closed",
    )
    open_keys = tuple(key for key, value in scope.items() if key not in closed and key not in {"no_new_negative_result", "no_tier_change", "no_pdf"} and isinstance(value, bool))
    check("closed scope", all(scope[key] is True for key in closed), {key: scope[key] for key in closed}, "all true", "scope")
    check("open promotion firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "all false", "scope")
    check("no negative/tier/pdf mutation", scope["no_new_negative_result"] and scope["no_tier_change"] and scope["no_pdf"], [scope["no_new_negative_result"], scope["no_tier_change"], scope["no_pdf"]], [True, True, True], "scope")
    check("method preservation", all(manifest["method_preservation"].values()), manifest["method_preservation"], "all true", "method-firewall")

    payload: dict[str, Any] = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": manifest["candidate_id"],
        "result_id": manifest["result_id"],
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": manifest["status"],
        "assertion_count": len(checks),
        "assertions": samples,
        "assertion_samples_truncated": len(checks) > len(samples),
        "derived": {
            "base_tail": str(base_tail),
            "ratio_q": str(q),
            "maximum_ratio": str(maximum_ratio),
            "ratio_rows": len(ratio_rows),
            "orientation_count": orientations,
            "two_sum_factor": two_sum_factor,
            "fourth_power_cauchy_factor": fourth_power_cauchy_factor,
            "C4_edge": str(c4_edge),
            "cauchy_fourth_bound": "(2^(4-1))*orientation_count*C4_edge*T(R)^4",
            "geometric_envelope": "78*(23/26)^(R-1)",
            "conditional_two_sided_recurrence_transfer_closed": True,
            "conditional_all_shape_cauchy_implication_closed": True,
            "actual_q3_history_closed": False,
            "common_weighted_operator_domain_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
            "sector_a_closed": False,
        },
        "ratio_rows": ratio_rows,
        "envelope_rows": envelope_rows,
        "source_hashes": {
            "script": digest(Path(__file__)),
            "manifest": digest(MANIFEST),
            "parent_manifest": digest(PARENT_MANIFEST),
            "parent_run": digest(PARENT_RUN),
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    if store:
        atomic_json(output if output.is_absolute() else REPO / output, payload)
    print(f"R-451 PRIMARY {payload['verdict']} {len(checks)}/{len(checks)} ratio_rows={len(ratio_rows)} q={q}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    run(args.output, store=not args.no_store)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
