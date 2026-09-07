#!/usr/bin/env python3
"""DFFR source identity, exact comparison fixtures and compact manuscript replay.

This is not a new phase-theorem verifier. The source interpretation and
independent-review decisions remain outside the diagnostic's scope.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import runpy
import tempfile

from pypdf import PdfReader
import sympy as s

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "publish/papers/q3lock-phase-coexistence"
PRIOR = ROOT / "verification/scripts/q3lock_literature_addendum_snapshot.py"
RUNS = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs"
OLD_RUN = RUNS / "2026-09-07-q3lock-literature-qps-addendum/result.json"
OUT = RUNS / "2026-09-07-q3lock-dffr-source-audit/result.json"
SOURCE_URL = "https://luc-umass.github.io/pdf/ql2.pdf"
# Input identity of the inspected author-provided scan, not a derived number.
SOURCE_SHA256 = "7f130e15e90d75b49b193d75cc5f647f713f2abf1a90c0a795a930f3ccb11fbd"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_payload(source_pdf):
    assert digest(source_pdf) == SOURCE_SHA256, "Source bytes differ; reassess the source."
    reader = PdfReader(source_pdf)
    rows = []

    def check(name, condition, actual):
        assert bool(condition), (name, actual)
        rows.append({"name": name, "pass": True, "actual": str(actual)})

    # A comparison model only. The Gibbs ratio is an explicit fixture input.
    n, cut = s.symbols("n cut", integer=True, nonnegative=True)
    q = s.Rational(1, 2)
    check("gibbs-normalization", s.summation((1-q)*q**n, (n, 0, s.oo)) == 1, q)
    z = s.symbols("z", positive=True)
    # z=exp(t): below, at and above the geometric convergence boundary.
    fixture_z = (s.Integer(1), 1/q, 2/q)
    for input_z in fixture_z:
        ratio = q*input_z
        partial = s.summation((1-q)*ratio**n, (n, 0, cut))
        if ratio < 1:
            limit = s.limit(partial, cut, s.oo)
            check(f"convergent-{input_z}", limit == (1-q)/(1-ratio), limit)
        else:
            limit = s.limit(partial, cut, s.oo)
            check(f"divergent-{input_z}", limit is s.oo, limit)
        # Independently compare direct finite sums with the symbolic expression.
        for input_cut in (0, 1, 4):
            direct = sum((1-q)*ratio**j for j in range(input_cut+1))
            check(f"partial-{input_z}-{input_cut}",
                  s.simplify(direct-partial.subs(cut, input_cut)) == 0, direct)
    degree = s.symbols("degree", integer=True, nonnegative=True)
    ratio_limit = s.limit(q*((n+1)/n)**degree, n, s.oo)
    check("polynomial-ratio-test", ratio_limit == q and q < 1, ratio_limit)
    # These fixtures cannot infer that the actual Q3 number-operator law fails.

    previous_bytes = OLD_RUN.read_bytes()
    replay = runpy.run_path(str(PRIOR), run_name="q3lock_qps_readonly")["build_payload"]()
    assert OLD_RUN.read_bytes() == previous_bytes, "Historical snapshot changed."
    current = replay["current_manuscript_diagnostics"]
    hashes = {}
    summary = []

    def collect(node):
        if not isinstance(node, dict):
            return
        if "assertions_passed" in node:
            summary.append({key: node[key] for key in ("schema", "status", "assertions_passed")
                            if key in node})
        for path, value in node.get("source_hashes", {}).items():
            assert path not in hashes or hashes[path] == value, path
            assert digest(ROOT/path) == value, path
            hashes[path] = value
        for key, value in node.items():
            if key != "source_hashes":
                collect(value)

    collect(current)
    collect(replay)
    # collect(replay) visits current again; keep each diagnostic summary once.
    unique_summary = list({json.dumps(row, sort_keys=True): row for row in summary}.values())
    for path in (Path(__file__).resolve(), OLD_RUN):
        hashes[path.relative_to(ROOT).as_posix()] = digest(path)
    compact = json.dumps(current, sort_keys=True, separators=(",", ":")).encode()
    return {
        "schema": "tect/q3lock-dffr-source-audit/1.0", "status": "PASS",
        "claim_bearing": False, "manuscript_version": "0.1.7", "pdf_status": "DEFERRED",
        "source": {"url": SOURCE_URL, "sha256": digest(source_pdf),
                   "bytes": source_pdf.stat().st_size, "pdf_pages": len(reader.pages),
                   "visual_page_locators": [772, 776, 796, 797, 798, 799, 800],
                   "role": "comparison only; privately cached, not redistributed"},
        "fixture_assertions": rows, "fixture_assertions_passed": len(rows),
        "manuscript_replay": unique_summary,
        "manuscript_payload_sha256": hashlib.sha256(compact).hexdigest(),
        "source_hashes": dict(sorted(hashes.items())),
        "historical_snapshot_sha256": hashlib.sha256(previous_bytes).hexdigest(),
        "scope": "Exact harmonic comparison fixtures and source/provenance replay only; no Q3 regularity failure, analytic acceptance or novelty certificate."
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-pdf", type=Path, required=True)
    args = parser.parse_args()
    payload = build_payload(args.source_pdf)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=OUT.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
        os.replace(temporary, OUT)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print(f"DFFR source audit: PASS; exact comparison fixtures {payload['fixture_assertions_passed']}; "
          f"unchanged manuscript diagnostic groups {len(payload['manuscript_replay'])}")
    print(OUT.relative_to(ROOT).as_posix())
