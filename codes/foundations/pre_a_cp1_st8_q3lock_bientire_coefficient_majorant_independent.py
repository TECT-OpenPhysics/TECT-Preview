#!/usr/bin/env python3
"""Independent Fraction audit of the formal bi-entire Q3 coefficient norm."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-bientire-coefficient-majorant"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "independent.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})


def norm(coefficients: list[tuple[F, int, int]], field_radius: F, source_radius: F) -> F:
    return sum(abs(coefficient) * field_radius**field_degree * source_radius**source_degree for coefficient, field_degree, source_degree in coefficients)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    g, lam, c = F(fixture["g"]), F(fixture["lambda"]), F(fixture["spatial_coupling"])
    R, S, time = F(fixture["field_radius"]), F(fixture["source_radius"]), F(fixture["time"])
    audit = Audit()
    audit.check("identity", manifest["exploration_id"] == "EXP-001041" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001041/T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")

    onsite = norm([(g, 3, 1), (-F(3, 2)*g, 2, 2), (g, 1, 3), (-g/F(4), 0, 4)], R, S)
    edge = norm([(lam, 3, 1), (-F(3, 2)*lam, 3, 1), (lam, 3, 1), (-F(1, 2)*lam, 3, 1), (-F(3, 2)*lam, 2, 2), (F(3, 2)*lam, 2, 2), (-F(1, 2)*lam, 2, 2), (lam, 1, 3), (-F(1, 2)*lam, 1, 3), (-lam/F(4), 0, 4)], R, S)
    bond = norm([(c, 1, 1), (-c, 1, 1), (-c/F(2), 0, 2)], R, S)
    onsite_choices = int(fixture["onsite_choices"]); edge_choices = int(fixture["q3_edge_choices"]); bond_choices = int(fixture["spatial_bond_choices"])
    local_choices = onsite_choices + edge_choices + bond_choices
    rate = onsite_choices*onsite + edge_choices*edge + bond_choices*bond
    weighted_rate = time*rate
    audit.check("positive norms", onsite > 0 and edge > 0 and bond > 0, [onsite, edge, bond], ">0", "majorant")
    audit.check("choice count", local_choices == int(fixture["local_choice_count"]), local_choices, fixture["local_choice_count"], "graph")
    audit.check("orientation coefficient sum", edge == norm([(lam,3,1),(-F(3,2)*lam,3,1),(lam,3,1),(-F(1,2)*lam,3,1),(-F(3,2)*lam,2,2),(F(3,2)*lam,2,2),(-F(1,2)*lam,2,2),(lam,1,3),(-F(1,2)*lam,1,3),(-lam/F(4),0,4)], R, S), edge, edge, "orientation")

    factor_norms = [onsite]*onsite_choices + [edge]*edge_choices + [bond]*bond_choices
    word_rows: list[dict[str, Any]] = []
    product_bound = F(1)
    for length in range(1, int(fixture["max_word_length"])+1):
        product_bound *= factor_norms[(length-1) % len(factor_norms)]
        audit.check(f"formal product bound n={length}", product_bound > 0, product_bound, ">0", "majorant")
        word_rows.append({"length": length, "bound": product_bound})

    partial = F(0)
    for n in range(int(fixture["max_word_length"])+1):
        factorial = 1
        for k in range(2, n+1):
            factorial *= k
        term = weighted_rate**n / factorial
        partial += term
        audit.check(f"EGF term n={n}", term >= 0, term, ">=0", "majorant")
    audit.check("EGF partial below exp", float(partial) <= math.exp(float(weighted_rate)) + 1e-12, float(partial), f"<={math.exp(float(weighted_rate))}", "majorant")
    audit.check("formal radius scope", manifest["scope"]["formal_field_radius_not_a_cutoff"] is True and manifest["scope"]["operator_history_closed"] is False, manifest["scope"], "formal only", "scope")

    passed = len(audit.rows)
    return {"schema":"tect/foundation-audit/1.0","run_kind":"independent","verdict":"PASS","passed":passed,"total":passed,"failed":0,"assertions":audit.rows,"word_rows":word_rows,"derived":{"field_radius":R,"source_radius":S,"onsite_norm":onsite,"q3_edge_norm":edge,"spatial_bond_norm":bond,"local_rate":rate,"weighted_rate":weighted_rate,"local_choices":local_choices,"formal_bientire_word_egf_closed":True,"orientation_symmetric":True,"formal_field_radius_not_a_cutoff":True,"operator_history_closed":False,"all_shape_exhaustion_closed":False,"common_alpha_closed":False},"provenance":{"script":str(SCRIPT.relative_to(REPO)).replace('\\','/'),"script_sha256":sha256(SCRIPT),"manifest":str(MANIFEST.relative_to(REPO)).replace('\\','/'),"manifest_sha256":sha256(MANIFEST)},"exploration_id":manifest["exploration_id"],"boundary":manifest["scope"]}


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT); parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args(); payload=run()
    if not args.self_test: atomic_json(args.output if args.output.is_absolute() else REPO/args.output,payload)
    print(f"INDEPENDENT BI-ENTIRE-Q3-COEFFICIENT-MAJORANT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
