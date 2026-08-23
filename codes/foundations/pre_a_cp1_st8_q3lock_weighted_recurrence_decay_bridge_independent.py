#!/usr/bin/env python3
"""Independent Fraction implementation of EXP-001026."""

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
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-weighted-recurrence-decay-bridge"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "independent.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def clean(value: Any) -> Any:
    if isinstance(value, Fraction): return str(value)
    if isinstance(value, dict): return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [clean(v) for v in value]
    return value


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(clean(payload), stream, indent=2, sort_keys=True, ensure_ascii=True); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


class Audit:
    def __init__(self) -> None: self.rows: list[dict[str, Any]] = []
    def check(self, name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        if not ok: raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": clean(actual), "expected": clean(expected)})


def graph(side: int) -> tuple[list[tuple[int, int]], list[int]]:
    vertices = list(product(range(side), repeat=3)); index = {v: i for i, v in enumerate(vertices)}; edges: list[tuple[int, int]] = []
    for v in vertices:
        for axis in range(3):
            if v[axis] + 1 >= side: continue
            u = list(v); u[axis] += 1; edges.append((index[v], index[tuple(u)]))
    center = tuple((side - 1) // 2 for _ in range(3)); distance = [sum(abs(a-b) for a,b in zip(v, center)) for v in vertices]
    return edges, distance


def next_values(values: list[Fraction], edges: list[tuple[int, int]], C: Fraction, J: Fraction, delta: Fraction) -> list[Fraction]:
    out = [(1+C*delta)*value for value in values]
    for left, right in edges:
        out[left] += J*delta*values[right]; out[right] += J*delta*values[left]
    return out


def weight(values: list[Fraction], distances: list[int], base: int) -> Fraction:
    return sum(Fraction(base**d)*value for value,d in zip(values, distances))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); audit = Audit()
    audit.check("schema", manifest["schema"] == "tect/pre-a-cp1-st8-q3lock-weighted-recurrence-decay-bridge/1.0", manifest["schema"], ".../1.0", "provenance")
    audit.check("exploration", manifest["exploration_id"] == "EXP-001026", manifest["exploration_id"], "EXP-001026", "provenance")
    audit.check("conditional", manifest["recurrence_hypothesis"]["supplied_by_q3"] is False, manifest["recurrence_hypothesis"], "supplied_by_q3=false", "scope")
    C, J, delta, z, base = Fraction(1), Fraction(1), Fraction(1,5), 6, 2
    edges, distances = graph(5); values = [Fraction(int(d == 0)) for d in distances]; rows: list[dict[str, Any]] = []
    audit.check("center mass", weight(values, distances, base) == 1, weight(values, distances, base), 1, "initial")
    for n in range(1,7):
        before = weight(values, distances, base); values = next_values(values, edges, C, J, delta); after = weight(values, distances, base); bound = (1+(C+J*z*base)*delta)*before
        audit.check(f"recurrence {n}", after <= bound, after, f"<={bound}", "recurrence"); rows.append({"step":n,"weight_before":before,"weight_after":after,"bound":bound})
    total = weight(values, distances, base); bound = (1+(C+J*z*base)*delta)**6
    audit.check("iteration", total <= bound, total, f"<={bound}", "recurrence")
    decay: list[dict[str, Any]] = []
    for d in range(5):
        b = total/Fraction(base**d); actual = max((value for value,radius in zip(values,distances) if radius>=d), default=Fraction(0)); audit.check(f"decay {d}", actual <= b, actual, f"<={b}", "decay"); decay.append({"distance":d,"actual_max":actual,"bound":b})
    for side in (3,5):
        test_edges, _ = graph(side); degrees=[0]*(side**3)
        for left,right in test_edges: degrees[left]+=1; degrees[right]+=1
        audit.check(f"degree {side}", max(degrees)<=z, max(degrees), f"<={z}", "volume")
    audit.check("boundary conditional", manifest["conclusion"]["boundary_decay_is_conditional"] is True, manifest["conclusion"], True, "scope")
    audit.check("Q3 hypothesis open", manifest["recurrence_hypothesis"]["status"] == "OPEN", manifest["recurrence_hypothesis"], "OPEN", "scope")
    passed=len(audit.rows)
    return {"schema":"tect/foundation-audit/1.0","run_kind":"independent","verdict":"PASS","passed":passed,"total":passed,"failed":0,"assertions":audit.rows,"derived":{"side":5,"max_degree":z,"weight_base":base,"C":C,"J":J,"delta":delta,"weighted_recurrence_to_decay_closed":True,"volume_uniform_conditional":True,"recurrence_hypothesis_supplied_by_q3":False,"boundary_commutator_decay_closed":False,"exhaustion_cauchy_closed":False,"common_alpha_closed":False},"recurrence_rows":rows,"decay_rows":decay,"provenance":{"script":str(SCRIPT.relative_to(REPO)).replace('\\','/'),"script_sha256":sha256(SCRIPT),"manifest":str(MANIFEST.relative_to(REPO)).replace('\\','/'),"manifest_sha256":sha256(MANIFEST)},"boundary":manifest["boundary"],"exploration_id":manifest["exploration_id"]}


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT); parser.add_argument("--self-test",action="store_true"); args=parser.parse_args(); payload=run()
    if not args.self_test: store(args.output if args.output.is_absolute() else REPO/args.output,payload)
    print(f"INDEPENDENT RECURRENCE-DECAY PASS {payload['passed']}/{payload['total']}"); return 0


if __name__ == "__main__": raise SystemExit(main())
