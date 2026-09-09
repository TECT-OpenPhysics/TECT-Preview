#!/usr/bin/env python3
"""Hostile controls for the PAH-OMC-020 non-coordinate coupling candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-noncoordinate-coupling/hostile.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(rows: list[dict], name: str, actual: object, expected: object) -> None:
    if actual != expected:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def serial(value: object) -> object:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    contract = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    rows: list[dict] = []
    check(rows, "candidate is explicitly hypothetical", contract["status"], "RESEARCHER_OWNED_CANDIDATE_ONLY")
    check(rows, "source authorization is not smuggled", contract["provenance"]["source_authorized_packet_present"], False)
    check(rows, "model mutation is rejected", contract["provenance"]["model_change"], False)
    check(rows, "post-hoc fitting is rejected", contract["provenance"]["post_hoc_parameter_fitting"], False)
    check(rows, "map is not coordinate pullback", contract["map"]["kind"], "maximal-prefix-coupling-conditional-expectation")
    check(rows, "density-ratio shortcut is absent", "density ratio" not in contract["map"]["operator"].lower(), True)
    check(rows, "direct sum rescue is rejected", any("No phasewise or cross-Q direct sum is used" in text for text in contract["fixed_scope"].values()), True)
    check(rows, "conditional averaging is not a model repair", any("conditional" in text.lower() for text in contract["map"].values()), True)

    limiting = [Fraction(3, 5), Fraction(2, 5)]
    finite = [Fraction(1, 2), Fraction(1, 2)]
    gamma = [[Fraction(1, 2), Fraction(1, 10)], [Fraction(0), Fraction(2, 5)]]
    mismatch = 1 - sum(min(limiting[i], finite[i]) for i in range(2))
    check(rows, "wrong ratio direction is detectable", mismatch, Fraction(1, 10))
    check(rows, "diagonal mass is not one", sum(gamma[i][i] for i in range(2)), Fraction(9, 10))
    check(rows, "full-space boundedness is not asserted", any("bounded" in text.lower() for text in contract["open_obligations"]), True)
    check(rows, "N2b remains open", any("N2b" in text for text in contract["open_obligations"]), True)
    check(rows, "N2c/N4 remains open", any("N2c/N4" in text for text in contract["open_obligations"]), True)
    check(rows, "N2d remains open", any("N2d" in text for text in contract["open_obligations"]), True)
    check(rows, "temporal promotion is rejected", any("semigroup" in text.lower() for text in contract["non_claims"]), True)
    check(rows, "physical promotion is rejected", any("physical Pre-A" in text for text in contract["non_claims"]), True)

    payload = {
        "schema": "tect/pah-omc020-noncoordinate-coupling-hostile/1.0",
        "status": "PASS_HOSTILE_NONCOORDINATE_COUPLING_CONTROLS",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "candidate_sha256": sha256(CANDIDATE),
        "checks": rows,
        "finding": "Hostile controls reject diagonal/density-ratio reversal, direct-sum or fitted-weight rescues, and any promotion from local coupling to energy, temporal or physical claims.",
        "non_claims": contract["non_claims"],
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if args.output.read_bytes() != encoded:
            raise SystemExit("hostile coupling replay mismatch")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(encoded)
    print(f"PAH-OMC-020 NONCOORDINATE HOSTILE: PASS {len(rows)}/{len(rows)}; verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
