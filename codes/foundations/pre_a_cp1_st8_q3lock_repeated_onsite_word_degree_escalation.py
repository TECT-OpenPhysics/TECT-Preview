#!/usr/bin/env python3
"""Primary symbolic audit for repeated onsite-word source-degree escalation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-repeated-onsite-word-degree-escalation"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, sp.Basic): return str(value)
    if isinstance(value, dict): return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [safe(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); fd, tmp = tempfile.mkstemp(prefix=path.name+".", suffix=".tmp", dir=path.parent)
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
        self.rows.append({"name":name,"group":group,"status":"PASS","actual":safe(actual),"expected":safe(expected)})


def run() -> dict[str, Any]:
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); audit=Audit()
    audit.check("schema", manifest["schema"].endswith("/1.0"), manifest["schema"], ".../1.0", "provenance")
    audit.check("exploration", manifest["exploration_id"]=="EXP-001031", manifest["exploration_id"], "EXP-001031", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    a,q,r=sp.symbols("a q r"); g=sp.Rational(3,5); lam=sp.Rational(2,7); c=sp.Rational(2,3); G=sp.expand(g+3*lam); degree_weight=5; amplitude=10
    delta=sp.expand(G*(q**4-(q-a)**4)/4-c*a*r); rows=[]
    audit.check("Q3 coefficient", G==sp.Rational(51,35), G, sp.Rational(51,35), "derivation")
    for m in manifest["fixture"]["word_lengths"]:
        word=sp.expand(sp.diff(delta**m,r).subs({q:0,r:0})); degree=int(sp.degree(word,a)); expected_degree=4*int(m)-3; expected=-int(m)*c*(-G/4)**(int(m)-1)*a**expected_degree
        audit.check(f"word identity m={m}", sp.expand(word-expected)==0, word, expected, "word")
        audit.check(f"word degree m={m}", degree==expected_degree, degree, expected_degree, "word")
        audit.check(f"weight gap m={m}", degree-degree_weight==4*int(m)-8, degree-degree_weight, 4*int(m)-8, "weight")
        value=sp.Abs(word.subs(a,amplitude)); weight=(1+amplitude)**degree_weight; rows.append({"word_length":int(m),"degree":degree,"response_at_10":value,"weight_at_10":weight,"degree_gap":degree-degree_weight})
    audit.check("m2 matches degree-five lane", rows[1]["degree"]==5, rows[1], 5, "cross-route")
    audit.check("m3 outruns w5", rows[2]["degree"]>degree_weight, rows[2]["degree"], f">{degree_weight}", "cross-route")
    audit.check("prescribed-word scope", "does not prove" in manifest["no_overclaim"], manifest["no_overclaim"], "explicit boundary", "scope")
    passed=len(audit.rows)
    return {"schema":"tect/foundation-audit/1.0","run_kind":"primary","verdict":"PASS","passed":passed,"total":passed,"failed":0,"assertions":audit.rows,"word_rows":rows,"derived":{"G":G,"weight_degree":degree_weight,"word_lengths":manifest["fixture"]["word_lengths"],"degree_formula":"4m-3","m2_degree":rows[1]["degree"],"m3_degree":rows[2]["degree"],"fixed_polynomial_weight_closed_for_all_words":False,"actual_q3_word_incidence_closed":False,"cancellation_closed":False,"entire_analytic_route_open":True},"provenance":{"script":str(SCRIPT.relative_to(REPO)).replace("\\","/"),"script_sha256":sha256(SCRIPT),"manifest":str(MANIFEST.relative_to(REPO)).replace("\\","/"),"manifest_sha256":sha256(MANIFEST)},"exploration_id":manifest["exploration_id"],"boundary":manifest["scope"]}


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT); parser.add_argument("--self-test",action="store_true"); args=parser.parse_args(); payload=run()
    if not args.self_test: atomic_json(args.output if args.output.is_absolute() else REPO/args.output,payload)
    print(f"PRIMARY REPEATED-ONSITE-WORD-DEGREE PASS {payload['passed']}/{payload['total']}"); return 0


if __name__=="__main__": raise SystemExit(main())
