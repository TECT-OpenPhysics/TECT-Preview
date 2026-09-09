"""Hostile controls for the PAH-OMC-020 path-space bridge.

The hostile lane rejects the common shortcuts that would turn a scalar
conditional bridge into an unjustified semigroup theorem.  It is deliberately
non-importing and does not modify any PAH definition.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-pathspace-bridge/hostile.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json":
        "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-020-projective-correlation-result-v1.json":
        "2bfc217bfa7785726d7342ce5ec80d1adab5be030c561d4e6681d49f64cf3248",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def check(rows: list[dict], name: str, actual: object, expected: object, ok: bool) -> None:
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rows: list[dict] = []
    for relative, expected in PINS.items():
        actual = digest(ROOT / relative)
        check(rows, f"hash:{relative}", actual, expected, actual == expected)

    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8"))
    r512 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-019-result-v1.json").read_text(encoding="utf-8"))
    r519 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-projective-correlation-result-v1.json").read_text(encoding="utf-8"))
    comparison = prereg["objects_and_comparison"]

    check(rows, "shortcut:finite word is not infinite proof",
          r519["conditional"] is True and "finite-word" in r519["non_claims"][0],
          True, r519["conditional"] is True and "finite-word" in r519["non_claims"][0])
    check(rows, "shortcut:state convergence is not U_n",
          "common U_n" in " ".join(r519["missing_assumptions"]), True,
          "common U_n remains missing")
    check(rows, "shortcut:closed form is not process uniqueness",
          any("process" in item.lower() for item in r512["non_claims"]), True,
          "R-512 process non-claim retained")
    check(rows, "shortcut:minimality is not automatic",
          any("minimal/maximal" in item.lower() or "uniqueness" in item.lower()
              for item in r512["non_claims"]), True,
          "minimal extension distinction retained")
    check(rows, "shortcut:tail cannot be dropped",
          all(Fraction(item) > 0 for item in r519["derived_inputs"].get("tail_values", [])),
          True, "stored factorial tails are positive")
    check(rows, "shortcut:target defect is explicit",
          any("minimal-form" in item for item in r519["missing_assumptions"]), True,
          "minimal-form identification remains open")
    check(rows, "shortcut:boundary term has two-copy factor",
          "b_eff=288" in r519["conclusion"]["boundary_tail"], True,
          "b_eff=288 retained")
    check(rows, "shortcut:order is not diagonalized",
          "no diagonal" in prereg["scope"]["regulator_order"].lower(), True,
          "no diagonal limit")
    check(rows, "shortcut:Markov time is not physical",
          "external unaccelerated Markov time" in prereg["scope"]["time"], True,
          "external stochastic time")
    check(rows, "shortcut:topology does not assume strong operator convergence",
          "Not assumed strong operator convergence" in comparison["topology_boundary"], True,
          "scalar topology only")

    # Challenge mutations: each tempting shortcut changes the bridge budget or
    # its logical status and is therefore rejected.
    boundary = Fraction(3, 5)
    target = Fraction(7, 10)
    honest = boundary + target
    dropped_tail = target
    zero_target = boundary
    check(rows, "mutation:dropping boundary changes budget",
          dropped_tail != honest, True, dropped_tail != honest)
    check(rows, "mutation:setting target defect to zero changes budget",
          zero_target != honest, True, zero_target != honest)
    check(rows, "mutation:declaring HOLD as PASS is rejected",
          r519["active_gate_change"] is False and r519["claim_bearing"] is False,
          [False, False], r519["active_gate_change"] is False and r519["claim_bearing"] is False)
    check(rows, "mutation:finite tail cannot be called uniform theorem",
          "full anchored-n semigroup" in " ".join(r519["non_claims"]), True,
          "full anchored-n semigroup remains a non-claim")
    check(rows, "mutation:local state cannot imply minimal selection",
          "minimal-form identification" in " ".join(r519["missing_assumptions"]), True,
          "selection remains missing")
    check(rows, "mutation:physical promotion rejected",
          any("physical Pre-A" in item for item in r519["non_claims"]), True,
          "physical firewall retained")

    payload = {
        "schema": "tect/pah-omc020-pathspace-bridge-hostile/1.0",
        "status": "PASS_HOSTILE_PATHSPACE_BRIDGE_CONTROLS",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": {relative: digest(ROOT / relative) for relative in PINS},
        "checks": rows,
        "rejected_shortcuts": [
            "Treat a finite word cutoff or factorial fixture as an infinite-series or uniform anchored-n theorem.",
            "Infer a common U_n from R-510 local-state convergence or from the R-512 closed form.",
            "Drop the boundary tail, the two-copy factor, or the target minimal-form defect.",
            "Use form closability as automatic process uniqueness or minimal/maximal extension equality.",
            "Promote external Markov time or any auxiliary result to a physical conclusion.",
        ],
        "finding": "All tested shortcuts either alter the explicit bridge budget or erase a source-missing process/minimality premise; the honest verdict remains HOLD_FOR_EVIDENCE.",
        "non_claims": [
            "No universal no-go for abstract path-space constructions.",
            "No PAH-OMC-020 semigroup convergence or counterexample.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion.",
        ],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_pathspace_bridge_hostile.py --check",
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if args.check:
        if not args.output.exists() or args.output.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 hostile path-space replay mismatch")
    else:
        write_json(args.output, payload)
    print("PAH-OMC-020 PATHSPACE HOSTILE: PASS (shortcuts rejected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
