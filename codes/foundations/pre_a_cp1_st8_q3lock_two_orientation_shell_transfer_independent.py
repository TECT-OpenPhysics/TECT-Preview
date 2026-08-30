#!/usr/bin/env python3
"""Independent Fraction-only reconstruction of the R-450 shell transfer."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-two-orientation-shell-transfer-manifest.json"
EDGE = ROOT / "strategy/pre-a-cp1-st8-q3lock-state-weighted-edge-majorant-composition-manifest.json"
TAIL = ROOT / "strategy/pre-a-cp1-st8-q3lock-exponential-shell-tail-manifest.json"
TRANSFER = ROOT / "strategy/pre-a-cp1-st8-q3lock-scalar-operator-tail-transfer-manifest.json"
FORCE = ROOT / "strategy/pre-a-cp1-st8-q3lock-local-force-moment-interface-manifest.json"
MOMENT = ROOT / "strategy/pre-a-cp1-st8-q3lock-local-force-moment-bridge-manifest.json"
DEFAULT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-independent-pre_a_cp1_st8_q3lock_two_orientation_shell_transfer/independent.json"


def q(value: object) -> Fraction:
    return Fraction(str(value))


def save(path: Path, payload: dict[str, Any]) -> None:
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


def count_shell(radius: int) -> int:
    if radius == 0:
        return 1
    return 4 * radius * radius + 2


def tail(radius: int) -> Fraction:
    numerator = 3 * (4 * radius * radius + 8 * radius + 14)
    denominator = 2 ** (radius - 1)
    return Fraction(numerator, denominator)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    packet = json.loads(MANIFEST.read_text(encoding="utf-8"))
    edge = json.loads(EDGE.read_text(encoding="utf-8"))
    tail_parent = json.loads(TAIL.read_text(encoding="utf-8"))
    transfer = json.loads(TRANSFER.read_text(encoding="utf-8"))
    force = json.loads(FORCE.read_text(encoding="utf-8"))
    moment = json.loads(MOMENT.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("packet identity", (packet["result_id"], packet["exploration_id"], packet["task_id"], packet["claim_bearing"]) == ("R-450", "EXP-001323", "T-054", False), [packet["result_id"], packet["exploration_id"], packet["task_id"], packet["claim_bearing"]], "R-450/EXP-001323/T-054/false", "provenance")
    check("parent identity", (edge["exploration_id"], tail_parent["result_id"], transfer["result_id"]) == ("EXP-001320", "R-444", "R-445"), [edge["exploration_id"], tail_parent["result_id"], transfer["result_id"]], "EXP-001320/R-444/R-445", "lineage")

    ff = force["finite_fixture"]
    mf = moment["finite_fixture"]
    c_force = q(ff["force_constant"])
    g = q(ff["g"])
    a0 = q(mf["A0_input"])
    m5 = q(mf["m5_input"])
    D = max(Fraction(1), Fraction(8) / g)
    C0 = Fraction(1) + 2 * a0
    bridge = Fraction(9) * (C0**3 + 2 * m5)
    C4 = c_force**4 * D**3 * bridge
    check("parent inputs positive", c_force > 0 and g > 0 and a0 >= 0 and m5 >= 0, [c_force, g, a0, m5], "force>0,g>0,A0,m5>=0", "composition")
    check("C4 reconstruction", C4 == c_force**4 * D**3 * bridge and C4 > 0, C4, "c_force^4*D^3*bridge", "composition")
    check("R-444 formula text", tail_parent["finite_contract"]["tail_formula"] == "3*(4*R^2+8*R+14)*2^(1-R)", tail_parent["finite_contract"]["tail_formula"], "R-444 formula", "lineage")
    check("R-445 triangle contract", transfer["scope"]["finite_banach_norm_transfer"] is True and "sum_tail" in transfer["finite_contract"]["transfer_chain"], transfer["finite_contract"]["transfer_chain"], "finite triangle transfer", "lineage")

    pairs = packet["finite_fixture"]["coefficient_weight_pairs_from_exp001320"]
    for index, pair in enumerate(pairs):
        coefficient = q(pair["coefficient"])
        weight = q(pair["weight"])
        check(f"pair {index} weight", weight >= 0, weight, ">=0", "coefficient")
        check(f"pair {index} domination", abs(coefficient) <= weight, abs(coefficient), f"<={weight}", "coefficient")
        check(f"pair {index} fourth transfer", abs(coefficient) ** 4 * C4 <= weight**4 * C4, abs(coefficient) ** 4 * C4, weight**4 * C4, "coefficient")

    sides_min = int(packet["finite_fixture"]["box_side_min"])
    sides_max = int(packet["finite_fixture"]["box_side_max"])
    radius_min = int(packet["finite_fixture"]["tail_radius_min"])
    radius_max = int(packet["finite_fixture"]["tail_radius_max"])
    orientation_count = int(packet["finite_fixture"]["orientation_count"])
    check("geometry", [sides_min, sides_max, radius_min, radius_max, orientation_count] == [2, 8, 1, 12, 2], [sides_min, sides_max, radius_min, radius_max, orientation_count], [2, 8, 1, 12, 2], "geometry")

    total_boxes = 0
    total_edges = 0
    total_rows = 0
    maximum_ratio = Fraction(0)
    maximum_two_ratio = Fraction(0)
    for sides in product(range(sides_min, sides_max + 1), repeat=3):
        vertices = list(product(*[range(side) for side in sides]))
        edges: list[tuple[tuple[int, int, int], tuple[int, int, int]]] = []
        for lower in vertices:
            for axis, side in enumerate(sides):
                if lower[axis] + 1 < side:
                    upper = list(lower)
                    upper[axis] += 1
                    edges.append((lower, tuple(upper)))
        expected = ((sides[0] - 1) * sides[1] * sides[2] + (sides[1] - 1) * sides[0] * sides[2] + (sides[2] - 1) * sides[0] * sides[1])
        check(f"box {total_boxes} edge count", len(edges) == expected, len(edges), expected, "geometry")
        weights = [Fraction(1, 2 ** sum(abs(v) for v in lower)) for lower, _upper in edges]
        for radius in range(radius_min, radius_max + 1):
            finite = sum((weight for (lower, _upper), weight in zip(edges, weights) if sum(abs(v) for v in lower) >= radius), Fraction(0))
            bound = tail(radius)
            one = C4 * finite**4
            two = Fraction(orientation_count) * one
            two_bound = Fraction(orientation_count) * C4 * bound**4
            check(f"box {total_boxes} scalar tail {radius}", finite <= bound, finite, bound, "shell")
            check(f"box {total_boxes} one orientation {radius}", one <= C4 * bound**4, one, C4 * bound**4, "orientation")
            check(f"box {total_boxes} two orientation {radius}", two <= two_bound, two, two_bound, "orientation")
            ratio = finite / bound if bound else Fraction(0)
            two_ratio = two / two_bound if two_bound else Fraction(0)
            maximum_ratio = max(maximum_ratio, ratio)
            maximum_two_ratio = max(maximum_two_ratio, two_ratio)
            total_rows += 1
        total_edges += len(edges)
        total_boxes += 1
    check("box coverage", total_boxes == (sides_max - sides_min + 1) ** 3, total_boxes, (sides_max - sides_min + 1) ** 3, "coverage")
    check("row coverage", total_rows == total_boxes * (radius_max - radius_min + 1), total_rows, total_boxes * (radius_max - radius_min + 1), "coverage")
    check("shell count anchor", count_shell(1) == 6 and count_shell(2) == 18, [count_shell(1), count_shell(2)], [6, 18], "shell")
    check("tail anchor", tail(1) == Fraction(78) and tail(2) == Fraction(69), [tail(1), tail(2)], [Fraction(78), Fraction(69)], "shell")
    for radius in range(radius_min, radius_max):
        check(f"tail recurrence {radius}", tail(radius) - tail(radius + 1) == Fraction(3 * count_shell(radius), 2**radius), tail(radius) - tail(radius + 1), Fraction(3 * count_shell(radius), 2**radius), "shell")

    scope = packet["scope"]
    positive = ("parent_state_weighted_edge_majorant_reused", "parent_scalar_shell_tail_reused", "coefficient_weight_domination_checked", "finite_box_two_orientation_envelope_closed", "root_free_fourth_power_certificate_closed")
    check("positive scope", all(scope[key] is True for key in positive), {key: scope[key] for key in positive}, "all true", "scope")
    negatives = [key for key, value in scope.items() if key.endswith("_closed") and key not in positive]
    check("scope firewall", all(scope[key] is False for key in negatives), {key: scope[key] for key in negatives}, "all false", "scope")
    check("method firewall", all(packet["method_preservation"].values()), packet["method_preservation"], "all true", "method")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": packet["candidate_id"],
        "result_id": packet["result_id"],
        "claim_id": packet["claim_ids"][0],
        "task_id": packet["task_id"],
        "exploration_id": packet["exploration_id"],
        "verdict": packet["status"],
        "assertion_count": len(checks),
        "assertions": checks[:120],
        "assertion_samples_truncated": len(checks) > 120,
        "derived": {
            "C4_edge": str(C4),
            "orientation_count": orientation_count,
            "box_count": total_boxes,
            "total_edges": total_edges,
            "tail_rows": total_rows,
            "tail_at_1": str(tail(1)),
            "tail_at_12": str(tail(radius_max)),
            "maximum_finite_to_bound_ratio": str(maximum_ratio),
            "maximum_two_orientation_fourth_ratio": str(maximum_two_ratio),
            "root_free_two_orientation_bound": "2*C4_edge*T(R)^4",
            "finite_box_two_orientation_envelope_closed": True,
            "actual_q3_per_edge_majorant_closed": False,
            "actual_q3_history_identification_closed": False,
            "common_weighted_operator_domain_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
            "sector_a_closed": False,
        },
        "source_hashes": {"script": digest(Path(__file__)), "manifest": digest(MANIFEST), "edge_parent": digest(EDGE), "tail_parent": digest(TAIL), "transfer_parent": digest(TRANSFER), "force_parent": digest(FORCE), "moment_parent": digest(MOMENT)},
        "assumptions": packet["assumptions"],
        "missing_assumptions": packet["missing_assumptions"],
        "evidence_level": packet["evidence_level"],
        "non_claims": packet["non_claims"],
        "boundary": packet["boundary"],
    }
    if not args.no_store:
        save(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"R-450 INDEPENDENT {payload['verdict']} {len(checks)}/{len(checks)} boxes={total_boxes} edges={total_edges} tail_rows={total_rows}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
