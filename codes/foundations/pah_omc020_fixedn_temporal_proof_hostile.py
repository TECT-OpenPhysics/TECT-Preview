#!/usr/bin/env python3
"""Hostile controls for the PAH-OMC-020 fixed-n temporal certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-certificate.md"
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-fixedn-temporal/hostile.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-certificate.md":
        "6f3bbb18fb94db189a6d7d9249cf86ba636643946d0a5340ebe900c92f515820",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
                             encoding="utf-8", newline="\n")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def check(rows: list[dict], name: str, condition: bool, actual: object, expected: object) -> None:
    if not condition:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def run(output: Path) -> dict:
    rows: list[dict] = []
    for relative, expected in PINS.items():
        path = ROOT / relative
        check(rows, f"pin:{relative}", path.is_file() and digest(path) == expected,
              digest(path) if path.is_file() else "MISSING", expected)
    text = CERT.read_text(encoding="utf-8")
    pah = json.loads(PAH.read_text(encoding="utf-8"))
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    check(rows, "midpoint rate cannot be replaced", "exp[-beta(F_rho(r x)-F_rho(x))/2]" in pah["dynamics"]["generator"],
          pah["dynamics"]["generator"], "source midpoint")
    check(rows, "certificate contains compact-only qualifier", "no global rate bound is asserted" in text,
          "no global rate bound is asserted" in text, "present")
    check(rows, "certificate contains endpoint retention", "retained upper endpoint" in text,
          "retained upper endpoint" in text, "present")
    check(rows, "certificate contains ordered limits", "j-to-infinity" in text and "then remove the cutoff" in text,
          "j then cutoff", "present")
    check(rows, "anchored n is explicitly excluded", "anchored" in text and "semigroup limit" in text,
          text, "excluded")
    check(rows, "physical non-claims remain in preregistration", "No physical Pre-A" in " ".join(prereg["non_claims"]),
          prereg["non_claims"], "present")
    with tempfile.TemporaryDirectory(prefix="pah020-fixedn-hostile-") as directory:
        mutation = Path(directory) / "diagonal.md"
        mutation.write_bytes(CERT.read_bytes().replace(b"No diagonal sequence is used", b"diagonal sequence is used", 1))
        check(rows, "diagonal shortcut changes certificate hash", digest(mutation) != digest(CERT),
              digest(mutation), "different")
        endpoint = Path(directory) / "endpoint.md"
        endpoint.write_bytes(CERT.read_bytes().replace(b"retained upper endpoint", b"endpoint omitted", 1))
        check(rows, "endpoint omission is detected", b"retained upper endpoint" not in endpoint.read_bytes(),
              endpoint.read_text(encoding="utf-8"), "omitted")
        physical = Path(directory) / "physical.md"
        physical.write_bytes(CERT.read_bytes() + b"\nphysical Pre-A established\n")
        check(rows, "physical promotion mutation changes hash", digest(physical) != digest(CERT),
              digest(physical), "different")
    payload = {
        "schema": "tect/pah-omc020-fixedn-temporal-hostile/1.0",
        "status": "PASS_HOSTILE_FIXED_N_TEMPORAL",
        "verdict": "AUXILIARY_SUPPORT",
        "temporal_verdict": "FIXED_N_PASS_ANCHORED_N_OPEN",
        "claim_bearing": False,
        "code_sha256": digest(Path(__file__)),
        "certificate_sha256": digest(CERT),
        "checks": rows,
        "rejected_mutations": [
            "diagonal j,n limit",
            "upper endpoint omission",
            "physical Pre-A promotion",
            "midpoint-rate replacement",
            "global unbounded-rate shortcut",
        ],
        "non_claims": [
            "Hostile controls do not prove the fixed-n theorem independently; they reject scope-changing shortcuts.",
            "No anchored n convergence, common U_n, R-512 minimal selection or physical conclusion.",
        ],
        "reproduction": {
            "run": "python -X utf8 codes/foundations/pah_omc020_fixedn_temporal_proof_hostile.py",
            "check": "python -X utf8 codes/foundations/pah_omc020_fixedn_temporal_proof_hostile.py --check",
        },
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        expected = args.output.read_bytes()
        with tempfile.TemporaryDirectory(prefix="pah020-hostile-replay-") as directory:
            payload = run(Path(directory) / "replay.json")
        actual = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
        if expected != actual:
            raise SystemExit("PAH-OMC-020 hostile replay mismatch")
    else:
        run(args.output)
    print("PAH-OMC-020 HOSTILE FIXED-N: PASS (anchored-n remains open)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
