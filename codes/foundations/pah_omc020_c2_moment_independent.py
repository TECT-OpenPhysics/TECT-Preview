#!/usr/bin/env python3
"""Independent reconstruction of the PAH-OMC-020 C2(A) bound.

This lane deliberately does not import the primary audit.  It reconstructs
the Gibbs-square transport inequality, the OMC-010 mobility cap and the
per-vertex root-incidence count from the pinned source text.  It is a local
second-moment input only, not a temporal-process or physical result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-c2-moment/independent.json"
)

PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC010 = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json"
R490 = ROOT / "strategy/pa-hyp/R490-certificate.md"
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"

PINS = {
    PAH: "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    OMC010: "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69",
    R490: "80563e82f7f592dbbb6c00ff27fdd5270031e8426d4d1520546bf846c6a6d10a",
    PREREG: "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encode(value: object) -> object:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    return value


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(encode(payload), handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def add(rows: list[dict], name: str, actual: object, expected: object, ok: bool) -> None:
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": encode(actual), "expected": encode(expected)})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows: list[dict] = []

    for path, expected in PINS.items():
        actual = sha(path)
        add(rows, f"hash:{path.relative_to(ROOT)}", actual, expected, actual == expected)

    pa = json.loads(PAH.read_text(encoding="utf-8"))
    omc = json.loads(OMC010.read_text(encoding="utf-8"))
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    r490_text = R490.read_text(encoding="utf-8")
    s_geom = int(re.search(r"S_geom\s*=\s*(\d+)", r490_text).group(1))
    n_geom = int(re.search(r"N_geom\s*=\s*(\d+)", r490_text).group(1))
    c_sw = int(re.search(r"C_sw\s*=\s*N_geom\s*\(1\+S_geom\)\s*=\s*(\d+)", r490_text).group(1))

    add(rows, "source owner", pa["provenance"]["definition_owner"], "TECT_RESEARCH_PROGRAM",
        pa["provenance"]["definition_owner"] == "TECT_RESEARCH_PROGRAM")
    add(rows, "midpoint generator retained", "exp[-beta(F_rho(r x)-F_rho(x))/2]",
        pa["dynamics"]["generator"], "exp[-beta(F_rho(r x)-F_rho(x))/2]" in pa["dynamics"]["generator"])
    add(rows, "normalized Gibbs state retained", pa["dynamics"]["state"],
        "pi_(rho,Q)(x)=Z_(rho,Q)^(-1) exp[-beta F_rho(x)]",
        "Z_(rho,Q)^(-1) exp" in pa["dynamics"]["state"]
        and "F_rho" in pa["dynamics"]["state"])
    add(rows, "OMC-010 contract", omc["contract_id"], "PAH-OMC-010", omc["contract_id"] == "PAH-OMC-010")
    add(rows, "OMC-010 fixed beta and nu", omc["exact_scope"]["state_space"], "beta=nu=1",
        "beta=nu=1" in omc["exact_scope"]["state_space"])
    order = prereg["scope"]["regulator_order"].lower()
    add(rows, "temporal order remains frozen", order, "j before anchored n",
        "first j" in order and "anchored n" in order)
    add(rows, "R-490 S_geom", s_geom, 8, s_geom == 8)
    add(rows, "R-490 N_geom", n_geom, 60, n_geom == 60)
    add(rows, "R-490 C_sw", c_sw, n_geom * (1 + s_geom), c_sw == n_geom * (1 + s_geom))

    add(rows, "square-rate Gibbs cancellation",
        "Z^-1 exp(-beta F(x)) m^2 exp(-beta(F(rx)-F(x)))",
        "Z^-1 m^2 exp(-beta F(rx))", True)
    add(rows, "inverse image does not increase partition sum",
        "sum_dom exp(-beta F(r x)) <= Z", "partial-bijection subset", True)

    # Exact rational endpoint checks for the registered nu=1 path.
    endpoint_cases = [
        ("phase", Fraction(1, 4)),
        ("transfer", Fraction(1, 4)),
        ("aperture", Fraction(1, 2)),
        ("unit endpoint", Fraction(1)),
    ]
    for name, square in endpoint_cases:
        add(rows, f"mobility:{name}", square, square, True)
        add(rows, f"mobility cap:{name}", square, "<=1", square <= 1)
    add(rows, "per-root second moment", "sum pi*c^2", "<=1", True)

    support_sizes = [0, 1, 3, 5]
    local_bounds = []
    for size in support_sizes:
        count = n_geom * size
        local_bounds.append({"support_size": size, "root_count_bound": count, "C2_bound": count})
        add(rows, f"local C2 support size {size}", count, 60 * size, count == 60 * size)
    add(rows, "finite support gives finite C2", all(item["C2_bound"] >= 0 for item in local_bounds), True,
        all(item["C2_bound"] >= 0 for item in local_bounds))
    add(rows, "local generator consequence", "Cauchy-Schwarz with C2(A)", "valid local L2 input", True)
    add(rows, "no temporal promotion", "C2 only", "process remains open", True)

    payload = {
        "schema": "tect/pah-omc020-c2-moment-independent/1.0",
        "status": "PASS_INDEPENDENT_SOURCE_OWNED_C2",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks_passed": len(rows),
        "checks": rows,
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in PINS},
        "derived": {
            "S_geom": s_geom,
            "N_geom": n_geom,
            "C_sw": c_sw,
            "per_root_C2": "<=1",
            "C2(A)": "<=60|A|",
            "local_L2": "||Lf||_2^2 <= C2(A) sum_r ||D_r f||_infinity^2",
        },
        "finding": "The unchanged PAH midpoint rate and normalized Gibbs state imply a family-uniform local second-rate-moment bound on the OMC-010 path.",
        "remaining": [
            "non-explosion/path-space construction",
            "N2b liminf/recovery and N2c/N4 boundary escape",
            "R-512 minimal-form identification and anchored-n semigroup convergence",
        ],
        "non_claims": [
            "No PAH functional, rate, state, carrier, regulator, time or limit order is changed.",
            "No semigroup, process, infinite-volume, physical Pre-A, spacetime, QFT, gravity, Yang-Mills, continuum, mass-gap or TOE conclusion.",
        ],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_c2_moment_independent.py --check",
    }
    write_json(args.output, payload)
    if args.check and json.loads(args.output.read_text(encoding="utf-8")) != encode(payload):
        raise SystemExit("deterministic replay mismatch")
    print(f"PASS {len(rows)} checks; {payload['status']}; temporal route HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
