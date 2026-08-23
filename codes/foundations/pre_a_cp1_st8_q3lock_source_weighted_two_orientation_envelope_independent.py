#!/usr/bin/env python3
"""Independent Fraction audit for EXP-001030 without symbolic imports."""

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
SLUG = "pre-a-cp1-st8-q3lock-source-weighted-two-orientation-envelope"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "independent.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, Fraction): return str(value)
    if isinstance(value, dict): return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [safe(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


class Audit:
    def __init__(self) -> None: self.rows: list[dict[str, Any]] = []
    def check(self, name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        if not ok: raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})


def coeffs(G: Fraction, c: Fraction, q: Fraction, r: Fraction) -> tuple[Fraction, ...]:
    return (Fraction(0), Fraction(0), -2*c*G*q**3 + 2*c**2*r, 3*c*G*q**2, -2*c*G*q, c*G/2)


def eval_poly(values: tuple[Fraction, ...], a: int) -> Fraction:
    return sum(value * a**degree for degree, value in enumerate(values))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); audit = Audit()
    audit.check("schema", manifest["schema"].endswith("/1.0"), manifest["schema"], ".../1.0", "provenance")
    audit.check("exploration", manifest["exploration_id"] == "EXP-001030", manifest["exploration_id"], "EXP-001030", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    g, lam, c = Fraction(3, 5), Fraction(2, 7), Fraction(2, 3)
    G = g + 3*lam; leading = c*G/2; degree = 5; C = Fraction(1); J = Fraction(1); delta = Fraction(1, 5); orientations = 2; steps = 6
    amplitudes = [0, 1, 2, 5, 10, 25]; points = [(Fraction(0),Fraction(0)),(Fraction(1),Fraction(0)),(Fraction(0),Fraction(1)),(Fraction(1,2),Fraction(1,3)),(Fraction(-1),Fraction(2))]
    audit.check("coefficient fixture", G == Fraction(51,35), G, Fraction(51,35), "derivation")
    audit.check("leading fixture", leading == Fraction(17,35), leading, Fraction(17,35), "derivation")
    rows: list[dict[str, Any]] = []
    for q, r in points:
        values = coeffs(G, c, q, r); bound_coeff = sum(abs(value) for value in values)
        for a in amplitudes:
            weight = (1+abs(a))**degree; actual = abs(eval_poly(values, a)); bound = bound_coeff*weight
            audit.check(f"independent weighted q={q} r={r} a={a}", actual <= bound, actual, f"<={bound}", "source-weight")
            rows.append({"q":q,"r":r,"a":a,"actual":actual,"bound":bound})
    fixture = eval_poly(coeffs(G,c,Fraction(0),Fraction(0)), 10); ratio = fixture/Fraction(11**5); linear = fixture/10
    audit.check("fixture response", fixture == Fraction(17,35)*10**5, fixture, Fraction(17,35)*10**5, "fixture")
    audit.check("weighted ratio", ratio < leading, ratio, f"<{leading}", "fixture")
    audit.check("linear ratio", linear > leading, linear, f">{leading}", "fixture")
    factor = 1 + (C + orientations*J)*delta; mass = Fraction(1); branch: list[dict[str, Any]] = []
    for index in range(steps):
        onsite = (1+C*delta)*mass; first = J*delta*mass; second = J*delta*mass; after = onsite+first+second
        audit.check(f"independent branch {index+1}", after == factor*mass, after, factor*mass, "two-orientation")
        audit.check(f"independent symmetry {index+1}", first == second, [first,second], "equal", "two-orientation")
        branch.append({"step":index+1,"before":mass,"after":after}); mass=after
    audit.check("factor", factor == Fraction(8,5), factor, Fraction(8,5), "two-orientation")
    audit.check("iterated", mass == factor**steps, mass, factor**steps, "two-orientation")
    passed = len(audit.rows)
    return {"schema":"tect/foundation-audit/1.0","run_kind":"independent","verdict":"PASS","passed":passed,"total":passed,"failed":0,"assertions":audit.rows,"weighted_rows":rows,"branch_rows":branch,"derived":{"G":G,"leading_coefficient":leading,"weight_degree":degree,"orientation_count":orientations,"C":C,"J":J,"delta":delta,"steps":steps,"two_orientation_factor":factor,"iterated_factor":factor**steps,"fixture_weighted_ratio":ratio,"fixture_linear_ratio":linear,"source_weight_absorption_closed":True,"finite_two_orientation_algebra_closed":True,"actual_q3_recurrence_closed":False,"all_bond_volume_uniform_recurrence_closed":False,"exhaustion_cauchy_closed":False,"common_alpha_closed":False},"provenance":{"script":str(SCRIPT.relative_to(REPO)).replace("\\","/"),"script_sha256":sha256(SCRIPT),"manifest":str(MANIFEST.relative_to(REPO)).replace("\\","/"),"manifest_sha256":sha256(MANIFEST)},"exploration_id":manifest["exploration_id"],"boundary":manifest["scope"]}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args=parser.parse_args(); payload=run()
    if not args.self_test: atomic_json(args.output if args.output.is_absolute() else REPO/args.output, payload)
    print(f"INDEPENDENT SOURCE-WEIGHTED-TWO-ORIENTATION PASS {payload['passed']}/{payload['total']}"); return 0


if __name__ == "__main__": raise SystemExit(main())
