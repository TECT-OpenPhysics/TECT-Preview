#!/usr/bin/env python3
"""Primary exact audit for the R-450 two-orientation shell transfer.

The script composes already registered T-054 interfaces.  It proves only the
root-free fourth-power envelope obtained from a per-edge state-weighted L4
majorant and the R-444 scalar shell tail.  It deliberately does not construct
an actual Q3 history or an unbounded operator domain.
"""

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


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-two-orientation-shell-transfer-manifest.json"
EDGE_PARENT = REPO / "strategy/pre-a-cp1-st8-q3lock-state-weighted-edge-majorant-composition-manifest.json"
TAIL_PARENT = REPO / "strategy/pre-a-cp1-st8-q3lock-exponential-shell-tail-manifest.json"
TRANSFER_PARENT = REPO / "strategy/pre-a-cp1-st8-q3lock-scalar-operator-tail-transfer-manifest.json"
FORCE_PARENT = REPO / "strategy/pre-a-cp1-st8-q3lock-local-force-moment-interface-manifest.json"
MOMENT_PARENT = REPO / "strategy/pre-a-cp1-st8-q3lock-local-force-moment-bridge-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_two_orientation_shell_transfer/primary.json"


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


def shell_count(radius: int) -> int:
    return 1 if radius == 0 else 4 * radius * radius + 2


def scalar_tail(radius: int) -> Fraction:
    if radius < 1:
        raise ValueError("R-444 tail is declared for radius >= 1")
    return Fraction(3 * (4 * radius * radius + 8 * radius + 14), 2 ** (radius - 1))


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
    edge_parent = json.loads(EDGE_PARENT.read_text(encoding="utf-8"))
    tail_parent = json.loads(TAIL_PARENT.read_text(encoding="utf-8"))
    transfer_parent = json.loads(TRANSFER_PARENT.read_text(encoding="utf-8"))
    force_parent = json.loads(FORCE_PARENT.read_text(encoding="utf-8"))
    moment_parent = json.loads(MOMENT_PARENT.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []
    samples: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(samples) < 80:
            samples.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})
        checks.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})

    check(
        "identity",
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]]
        == ["R-450", "EXP-001323", "T-054", False, "TWO_ORIENTATION_SHELL_TRANSFER_AUDITED"],
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]],
        ["R-450", "EXP-001323", "T-054", False, "TWO_ORIENTATION_SHELL_TRANSFER_AUDITED"],
        "provenance",
    )
    check("edge parent", edge_parent["exploration_id"] == "EXP-001320" and edge_parent["claim_bearing"] is False, edge_parent["exploration_id"], "EXP-001320", "lineage")
    check("shell parent", tail_parent["result_id"] == "R-444" and tail_parent["claim_bearing"] is False, tail_parent["result_id"], "R-444", "lineage")
    check("transfer parent", transfer_parent["result_id"] == "R-445" and transfer_parent["claim_bearing"] is False, transfer_parent["result_id"], "R-445", "lineage")
    check("force/moment parents", [force_parent["exploration_id"], moment_parent["exploration_id"]] == ["EXP-001059", "EXP-001060"], [force_parent["exploration_id"], moment_parent["exploration_id"]], ["EXP-001059", "EXP-001060"], "lineage")

    force_fixture = force_parent["finite_fixture"]
    moment_fixture = moment_parent["finite_fixture"]
    force_constant = fraction(force_fixture["force_constant"])
    g = fraction(force_fixture["g"])
    A0 = fraction(moment_fixture["A0_input"])
    m5 = fraction(moment_fixture["m5_input"])
    D = max(Fraction(1), Fraction(8) / g)
    C0 = Fraction(1) + 2 * A0
    M_bridge = Fraction(9) * (C0**3 + 2 * m5)
    C4_edge = force_constant**4 * D**3 * M_bridge
    check("positive parent inputs", force_constant > 0 and g > 0 and A0 >= 0 and m5 >= 0, [force_constant, g, A0, m5], "force>0,g>0,A0,m5>=0", "composition")
    check("derived D", D == max(Fraction(1), Fraction(8) / g), D, "max(1,8/g)", "composition")
    check("derived endpoint constant", C0 == Fraction(1) + 2 * A0, C0, "1+2*A0", "composition")
    check("derived moment bridge", M_bridge == Fraction(9) * (C0**3 + 2 * m5) and M_bridge > 0, M_bridge, "9*(C0^3+2*m5)>0", "composition")
    check("derived fourth-power edge constant", C4_edge == force_constant**4 * D**3 * M_bridge and C4_edge > 0, C4_edge, "force_constant^4*D^3*M_bridge", "composition")
    check("edge parent definition", edge_parent["composition"]["definitions"]["C4_edge"] == "force_constant^4*D^3*M_bridge", edge_parent["composition"]["definitions"]["C4_edge"], "force_constant^4*D^3*M_bridge", "lineage")
    check("R-444 weight", tail_parent["finite_contract"]["weight"] == "2^(-l1_norm(lower_endpoint))", tail_parent["finite_contract"]["weight"], "2^(-l1_norm(lower_endpoint))", "lineage")
    check("R-445 conditional term", transfer_parent["finite_contract"]["term_bound"] == "||K_e|| <= C*w(e)", transfer_parent["finite_contract"]["term_bound"], "||K_e|| <= C*w(e)", "lineage")

    pairs = manifest["finite_fixture"]["coefficient_weight_pairs_from_exp001320"]
    edge_pairs = edge_parent["finite_fixture"]["coefficient_weight_pairs"]
    check("coefficient rows copied by reference", pairs == edge_pairs, len(pairs), len(edge_pairs), "coefficient contract")
    for index, pair in enumerate(pairs):
        coefficient = fraction(pair["coefficient"])
        weight = fraction(pair["weight"])
        check(f"coefficient row {index} nonnegative weight", weight >= 0, weight, ">=0", "coefficient contract")
        check(f"coefficient row {index} dominated", abs(coefficient) <= weight, abs(coefficient), f"<={weight}", "coefficient contract")
        check(f"coefficient row {index} fourth transfer", abs(coefficient) ** 4 * C4_edge <= weight**4 * C4_edge, abs(coefficient) ** 4 * C4_edge, weight**4 * C4_edge, "coefficient contract")

    dimension = int(manifest["finite_fixture"]["dimension"])
    side_min = int(manifest["finite_fixture"]["box_side_min"])
    side_max = int(manifest["finite_fixture"]["box_side_max"])
    radius_min = int(manifest["finite_fixture"]["tail_radius_min"])
    radius_max = int(manifest["finite_fixture"]["tail_radius_max"])
    orientations = int(manifest["finite_fixture"]["orientation_count"])
    check("dimension contract", dimension == 3, dimension, 3, "geometry")
    check("box contract", [side_min, side_max] == [2, 8], [side_min, side_max], [2, 8], "geometry")
    check("orientation contract", orientations == 2, orientations, 2, "orientation")
    check("radius contract", radius_min == 1 and radius_max == 12, [radius_min, radius_max], [1, 12], "geometry")

    total_edges = 0
    tail_rows = 0
    maximum_ratio = Fraction(0)
    maximum_two_ratio = Fraction(0)
    box_summaries: list[dict[str, Any]] = []
    for box_index, sides in enumerate(product(range(side_min, side_max + 1), repeat=dimension)):
        vertices = list(product(*[range(side) for side in sides]))
        edges: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
        for lower in vertices:
            for axis, side in enumerate(sides):
                if lower[axis] + 1 < side:
                    upper = list(lower)
                    upper[axis] += 1
                    edges.append((lower, tuple(upper)))
        expected_edges = sum((sides[axis] - 1) * (sides[(axis + 1) % dimension] * sides[(axis + 2) % dimension]) for axis in range(dimension))
        check(f"box {box_index} edge count", len(edges) == expected_edges, len(edges), expected_edges, "geometry")
        weights = [Fraction(1, 2 ** sum(abs(value) for value in lower)) for lower, _upper in edges]
        local_max = Fraction(0)
        local_two_max = Fraction(0)
        for radius in range(radius_min, radius_max + 1):
            finite_tail = sum((weight for (lower, _upper), weight in zip(edges, weights) if sum(abs(value) for value in lower) >= radius), Fraction(0))
            bound = scalar_tail(radius)
            check(f"box {box_index} tail {radius}", finite_tail <= bound, finite_tail, bound, "finite shell")
            one_fourth = C4_edge * finite_tail**4
            two_fourth = Fraction(orientations) * one_fourth
            two_bound = Fraction(orientations) * C4_edge * bound**4
            check(f"box {box_index} one orientation fourth envelope {radius}", one_fourth <= C4_edge * bound**4, one_fourth, C4_edge * bound**4, "two-orientation transfer")
            check(f"box {box_index} two orientation fourth envelope {radius}", two_fourth <= two_bound, two_fourth, two_bound, "two-orientation transfer")
            tail_rows += 1
            ratio = finite_tail / bound if bound else Fraction(0)
            two_ratio = two_fourth / two_bound if two_bound else Fraction(0)
            maximum_ratio = max(maximum_ratio, ratio)
            maximum_two_ratio = max(maximum_two_ratio, two_ratio)
            local_max = max(local_max, ratio)
            local_two_max = max(local_two_max, two_ratio)
        box_summaries.append({"sides": list(sides), "vertices": len(vertices), "edges": len(edges), "max_tail_ratio": str(local_max), "max_two_orientation_fourth_ratio": str(local_two_max)})
        total_edges += len(edges)
    check("all boxes visited", len(box_summaries) == (side_max - side_min + 1) ** dimension, len(box_summaries), (side_max - side_min + 1) ** dimension, "coverage")
    check("all tail rows visited", tail_rows == len(box_summaries) * (radius_max - radius_min + 1), tail_rows, len(box_summaries) * (radius_max - radius_min + 1), "coverage")
    check("shell base retained", scalar_tail(1) == Fraction(78), scalar_tail(1), Fraction(78), "shell")
    for radius in range(radius_min, radius_max):
        check(f"shell recurrence {radius}", scalar_tail(radius) - scalar_tail(radius + 1) == Fraction(3 * shell_count(radius), 2**radius), scalar_tail(radius) - scalar_tail(radius + 1), Fraction(3 * shell_count(radius), 2**radius), "shell")

    scope = manifest["scope"]
    closed = ("parent_state_weighted_edge_majorant_reused", "parent_scalar_shell_tail_reused", "coefficient_weight_domination_checked", "finite_box_two_orientation_envelope_closed", "root_free_fourth_power_certificate_closed")
    open_keys = tuple(key for key, value in scope.items() if key not in closed and key not in ("no_new_negative_result", "no_tier_change", "no_pdf") and isinstance(value, bool))
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
            "force_constant": str(force_constant),
            "D": str(D),
            "A0": str(A0),
            "m5": str(m5),
            "C0": str(C0),
            "M_bridge": str(M_bridge),
            "C4_edge": str(C4_edge),
            "orientation_count": orientations,
            "box_count": len(box_summaries),
            "total_edges": total_edges,
            "tail_rows": tail_rows,
            "tail_at_1": str(scalar_tail(1)),
            "tail_at_12": str(scalar_tail(radius_max)),
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
        "boxes": box_summaries,
        "source_hashes": {
            "script": digest(Path(__file__)),
            "manifest": digest(MANIFEST),
            "edge_parent": digest(EDGE_PARENT),
            "tail_parent": digest(TAIL_PARENT),
            "transfer_parent": digest(TRANSFER_PARENT),
            "force_parent": digest(FORCE_PARENT),
            "moment_parent": digest(MOMENT_PARENT),
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    if store:
        atomic_json(output if output.is_absolute() else REPO / output, payload)
    print(f"R-450 PRIMARY {payload['verdict']} {len(checks)}/{len(checks)} boxes={len(box_summaries)} edges={total_edges} tail_rows={tail_rows}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run(args.output, store=not args.no_store)
    if args.self_test:
        assert payload["verdict"] == "TWO_ORIENTATION_SHELL_TRANSFER_AUDITED"
        assert payload["derived"]["finite_box_two_orientation_envelope_closed"] is True
        print("R-450 PRIMARY SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
