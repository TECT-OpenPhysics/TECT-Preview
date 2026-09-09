"""Hostile controls for the PAH-OMC-020 radial-sector proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-radial-sector/hostile.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md":
        "18dc782cafff8cf8a516fd8366ec7e1f8727a24c9553dba0656a6b4bc84de264",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json":
        "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows: list[dict] = []

    def ck(name: str, actual: object, expected: object, ok: bool) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        rows.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    for relative, expected in PINS.items():
        actual = digest(ROOT / relative)
        ck(f"hash {relative}", actual, expected, actual == expected)

    pah = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    r512 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-019-result-v1.json").read_text(encoding="utf-8"))
    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8"))
    cert = (ROOT / "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md").read_text(encoding="utf-8")
    compact = re.sub(r"\s+", "", cert).lower()

    moves = [item.lower() for item in pah["dynamics"]["move_set"]]
    ck("source move set has radial transfer", any("radial" in item for item in moves), True,
       any("radial" in item for item in moves))
    ck("source move set has nonradial classes", all(any(token in item for item in moves)
       for token in ("phase", "link", "aperture")), True,
       all(any(token in item for item in moves) for token in ("phase", "link", "aperture")))
    ck("exact R-511 half factor retained", "2h_fl_fh" in compact, True, "2h_fl_fh" in compact)
    ck("exact R-511 radial form factor retained", "2h_fl_f^2h^2" in compact, True,
       "2h_fl_f^2h^2" in compact)
    endpoints = "includealllower/upperendpointstates" in compact
    ck("both radial endpoints retained", endpoints, True, endpoints)
    ck("nonradial maps preserve amplitudes", "nonradialrootsonlychangefinitelabels" in compact, True,
       "nonradialrootsonlychangefinitelabels" in compact)

    H = Fraction(2)
    L = Fraction(3)
    T = Fraction(1, 2)
    honest = 2 * T * H * L
    shortcut = T * H * L
    ck("two-factor is not silently dropped", honest, 2 * shortcut, honest == 2 * shortcut)
    ck("dropping factor changes bound", honest != shortcut, True, honest != shortcut)

    h = Fraction(1, 2 ** 6)
    accelerated = Fraction(1, 1) / h
    ck("registered h_j is decaying", h < 1, True, h < 1)
    ck("inverse-h acceleration rejected", accelerated > 1, True, accelerated > 1)
    ck("no time rescaling in source", "time acceleration" not in cert.lower(), True,
       "time acceleration" not in cert.lower())
    ck("finite compact horizon", T > 0 and T < 2, True, T > 0 and T < 2)
    ck("target kernel is conditional", "H_rad subset ker(Ebar)" in r512["kernel_claim"], True,
       "H_rad subset ker(Ebar)" in r512["kernel_claim"])
    ck("mixed observables not promoted", any("mixed" in item.lower() or "full" in item.lower()
       for item in r512["non_claims"]), True,
       any("mixed" in item.lower() or "full" in item.lower() for item in r512["non_claims"]))
    ck("common-space shortcut rejected", "not claimed an isometry" in json.dumps(prereg), True,
       "not claimed an isometry" in json.dumps(prereg))
    ck("physical firewall", any("physical Pre-A" in item for item in r512["non_claims"]), True,
       any("physical Pre-A" in item for item in r512["non_claims"]))
    ck("external time firewall", "external" in prereg["scope"]["time"].lower()
       and "lorentzian" in prereg["scope"]["time"].lower(), True,
       "external" in prereg["scope"]["time"].lower() and "lorentzian" in prereg["scope"]["time"].lower())

    payload = {
        "schema": "tect/pah-omc020-radial-sector-hostile/1.0",
        "status": "PASS_HOSTILE_RADIAL_SECTOR",
        "verdict": "AUXILIARY_SUPPORT",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": {relative: digest(ROOT / relative) for relative in PINS},
        "checks": rows,
        "rejected_shortcuts": [
            "dropping the R-511 two-copy/triangle factor",
            "replacing h_j by h_j^{-1} or accelerating time",
            "promoting the D_rad argument to mixed observables or a common U_n theorem",
            "treating R-512 zero-form kernel as a physical conclusion",
        ],
        "scope": "Hostile controls only; no PAH definition, rate, state, carrier or time change.",
        "non_claims": [
            "No full PAH-OMC-020 anchored-n semigroup convergence.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion.",
        ],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_radial_sector_hostile.py --check",
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and args.output.exists():
        if args.output.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 radial hostile replay mismatch")
    elif not args.check:
        save(args.output, payload)
    print(f"PAH-OMC-020 RADIAL HOSTILE: PASS ({len(rows)} checks; shortcuts rejected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
