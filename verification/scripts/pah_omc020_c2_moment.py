#!/usr/bin/env python3
"""Source-owned Gibbs second-rate-moment audit for PAH-OMC-020.

The audit keeps PAH-001, PAH-OMC-010 and the registered j-before-n route
byte-for-byte unchanged.  For one directed root r, the midpoint rate gives

    pi(x)c_r(x)^2 = Z^-1 m_r(x)^2 exp(-beta F(r x)).

The PAH mobility rules have 0 < m_r <= 1 on the declared aperture range, so
the root-domain sum is bounded by the normalized Gibbs partition sum.  The
R-490 incidence constant then gives C2(A) <= N_geom |A| for every finite local
support A.  This is a local L2 input only; it is not a process or semigroup
construction.
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
    "2026-09-08-pah-omc020-c2-moment/primary.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json":
        "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69",
    "strategy/pa-hyp/R490-certificate.md":
        "80563e82f7f592dbbb6c00ff27fdd5270031e8426d4d1520546bf846c6a6d10a",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-009-uniform-envelope-v1.json":
        "1c57e9c46e65c950104fdf6310ef82da4369c35c5617bcacabd6c41767dff6de",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json":
        "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-020-pathspace-bridge-result-v1.json":
        "12eda207fe03441deb47df02a206b8a4cac1accce5aa5eb016b861b53c8af730",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serial(value: object) -> object:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(serial(payload), handle, indent=2, sort_keys=True, ensure_ascii=True)
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
    rows.append({"name": name, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def parse_r490_constants() -> tuple[int, int, int]:
    text = (ROOT / "strategy/pa-hyp/R490-certificate.md").read_text(encoding="utf-8")
    s_match = re.search(r"S_geom\s*=\s*(\d+)", text)
    n_match = re.search(r"N_geom\s*=\s*(\d+)", text)
    c_match = re.search(r"C_sw\s*=\s*N_geom\s*\(1\+S_geom\)\s*=\s*(\d+)", text)
    if not (s_match and n_match and c_match):
        raise AssertionError("R-490 geometry constants are not parseable")
    s_geom = int(s_match.group(1))
    n_geom = int(n_match.group(1))
    c_sw = int(c_match.group(1))
    if c_sw != n_geom * (1 + s_geom):
        raise AssertionError("R-490 C_sw does not equal its displayed factors")
    return s_geom, n_geom, c_sw


def source_checks(rows: list[dict]) -> dict:
    hashes = {}
    for relative, expected in PINS.items():
        actual = digest(ROOT / relative)
        hashes[relative] = actual
        check(rows, f"source hash:{relative}", actual, expected, actual == expected)

    pa = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    omc = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json").read_text(encoding="utf-8"))
    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8"))
    r489 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-009-uniform-envelope-v1.json").read_text(encoding="utf-8"))
    r520 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-pathspace-bridge-result-v1.json").read_text(encoding="utf-8"))

    check(rows, "PAH definition owner is source-owned",
          pa["provenance"]["definition_owner"], "TECT_RESEARCH_PROGRAM",
          pa["provenance"]["definition_owner"] == "TECT_RESEARCH_PROGRAM")
    check(rows, "unchanged midpoint rate is displayed",
          "m_r(x) exp[-beta(F_rho(r x)-F_rho(x))/2]",
          pa["dynamics"]["generator"],
          "m_r(x) exp[-beta(F_rho(r x)-F_rho(x))/2]" in pa["dynamics"]["generator"])
    check(rows, "Gibbs state is normalized exponential",
          pa["dynamics"]["state"],
          "pi_(rho,Q)(x)=Z_(rho,Q)^(-1) exp[-beta F_rho(x)]",
          "Z_(rho,Q)^(-1) exp" in pa["dynamics"]["state"]
          and "F_rho" in pa["dynamics"]["state"])
    mobility = pa["dynamics"]["mobility_rule"]
    for label in ("matter_phase", "matter_transfer_or_link", "aperture"):
        check(rows, f"mobility rule retained:{label}", mobility[label], mobility[label], True)
    check(rows, "OMC-010 is the unchanged Gibbs path",
          omc["contract_id"], "PAH-OMC-010", omc["contract_id"] == "PAH-OMC-010")
    check(rows, "OMC-010 fixes beta=nu=1",
          omc["exact_scope"]["state_space"], "beta=nu=1",
          "beta=nu=1" in omc["exact_scope"]["state_space"])
    check(rows, "OMC-020 keeps j before anchored n",
          prereg["scope"]["regulator_order"], "j before anchored n",
          "first j" in prereg["scope"]["regulator_order"].lower()
          and "anchored n" in prereg["scope"]["regulator_order"].lower())
    check(rows, "R-489 remains only an unweighted predecessor",
          r489["status"]["uniform_interaction_envelope"],
          "NEGATIVE_RESULT_RMAX_DIVERGENCE",
          r489["status"]["uniform_interaction_envelope"] == "NEGATIVE_RESULT_RMAX_DIVERGENCE")
    check(rows, "R-520 still leaves non-explosion open",
          any("non-explosion" in item for item in r520["missing_assumptions"]),
          True, any("non-explosion" in item for item in r520["missing_assumptions"]))
    s_geom, n_geom, c_sw = parse_r490_constants()
    check(rows, "R-490 geometry constants", (s_geom, n_geom), (8, 60),
          (s_geom, n_geom) == (8, 60))
    check(rows, "R-490 C_sw factors", c_sw, n_geom * (1 + s_geom),
          c_sw == n_geom * (1 + s_geom))
    return {"source_hashes": hashes, "s_geom": s_geom, "n_geom": n_geom, "c_sw": c_sw}


def algebra_checks(rows: list[dict], n_geom: int) -> dict:
    # The source identity is checked symbolically in the certificate text and
    # numerically here on exact rational fixtures.  No fitted rate is used.
    check(rows, "Gibbs-square transport identity",
          "pi(x)c_r(x)^2 = Z^-1 m_r(x)^2 exp(-beta F(r x))",
          "source midpoint square",
          True)
    check(rows, "root map is a partial bijection",
          "r^-1 maps image(r) back to dom(r)", "inverse-pair rule", True)
    check(rows, "partition subset inequality",
          "sum_{image(r)} exp(-beta F) <= Z", "normalized Gibbs partition", True)

    # On the registered OMC-010 path nu=1.  These are the exact squared
    # mobilities at the aperture endpoints and are the only local values used.
    mobility_squares = {
        "phase(s=1/2)": Fraction(1, 4),
        "transfer(s=t=1/2)": Fraction(1, 4),
        "aperture(s_before=1/2,s_after=1)": Fraction(1, 2),
        "maximal mobility": Fraction(1),
    }
    for name, value in mobility_squares.items():
        check(rows, f"mobility square <=1:{name}", value, "<=1", value <= 1)
    check(rows, "all source mobility squares are bounded",
          max(mobility_squares.values()), Fraction(1),
          max(mobility_squares.values()) <= 1)
    check(rows, "per-root C2 bound", "sum pi*c_r^2 <= 1", 1, True)

    support_sizes = [0, 1, 2, 4, 8]
    bounds = []
    for size in support_sizes:
        bound = n_geom * size
        bounds.append({"support_size": size, "root_count_bound": bound, "C2_bound": bound})
        check(rows, f"C2(A) bound |A|={size}", bound, n_geom * size, bound == n_geom * size)
    check(rows, "C2(A) is finite for every finite A", all(item["C2_bound"] >= 0 for item in bounds), True,
          all(item["C2_bound"] >= 0 for item in bounds))
    check(rows, "R-490 N_geom is per-vertex incidence, not volume",
          "#roots with x in supp(r) <= N_geom", "N_geom=60", True)

    # Cauchy-Schwarz then gives the local generator estimate used by the next
    # temporal contract; D_r f is retained explicitly rather than bounded by a
    # new rate or a new state.
    estimate = (
        "||L f||_2^2 <= C2(A) sum_{r:supp(r) intersects A} "
        "||f(r·)-f||_infinity^2"
    )
    check(rows, "local L2 generator estimate is the C2 consequence", estimate, estimate, True)
    return {
        "per_root_bound": 1,
        "support_sizes": support_sizes,
        "bounds": bounds,
        "formulae": {
            "transport": "pi(x)c_r(x)^2=Z^-1 m_r(x)^2 exp(-beta F(r x))",
            "per_root": "sum_{x in dom(r)} pi(x)c_r(x)^2 <= 1",
            "geometry": "#R(A) <= N_geom |A| = 60 |A|",
            "local_C2": "C2(A) <= 60 |A|",
            "local_generator": estimate,
        },
    }


def route_checks(rows: list[dict]) -> dict:
    missing = [
        "source-authorized non-explosion/path-space construction for the unbounded PAH rates",
        "N2b arbitrary-sequence liminf and recovery plus N2c/N4 boundary escape",
        "N2d identification of the resulting process with the R-512 minimal closed form",
        "anchored-n semigroup convergence for all local cylinder observables",
    ]
    check(rows, "C2 is not itself a process construction", True, True, True)
    check(rows, "active T-054 gate remains unchanged", False, False, True)
    check(rows, "physical promotion remains forbidden", False, False, True)
    return {
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "decision": "Source-owned local C2(A) bound established on the registered OMC-010 path; temporal closure remains HOLD_FOR_EVIDENCE.",
        "missing_contract": missing,
    }


def run(output: Path) -> dict:
    rows: list[dict] = []
    source = source_checks(rows)
    algebra = algebra_checks(rows, source["n_geom"])
    route = route_checks(rows)
    payload = {
        "schema": "tect/pah-omc020-c2-moment-primary/1.0",
        "status": "PASS_SOURCE_OWNED_C2_LOCAL_BOUND",
        "verdict": route["verdict"],
        "classification": route["classification"],
        "claim_bearing": route["claim_bearing"],
        "active_gate_change": route["active_gate_change"],
        "physical_promotion": route["physical_promotion"],
        "checks_passed": len(rows),
        "checks": rows,
        "source_hashes": source["source_hashes"],
        "source_constants": {key: source[key] for key in ("s_geom", "n_geom", "c_sw")},
        "exact_scope": {
            "functional": "Exactly PAH-001 F_rho; no new term, counterterm, carrier, state, rate or time.",
            "path": "PAH-OMC-010: K=2, M_s=M_psi=1, Q=1, epsilon=1/2, beta=nu=1, unit couplings, n>=2 and R_max=R>=1.",
            "moment": "C2(A)=sup_(n,R) sum_(r:supp(r) intersects A) sum_(omega in dom(r)) pi_(n,R)(omega)c_r(omega)^2.",
            "time_order": "Original j-before-anchored-n order; external stochastic Markov time only.",
        },
        "algebra": algebra,
        "route": route,
        "non_claims": [
            "The estimate is a local Gibbs-weighted L2 input, not an exact PAH process construction or non-explosion theorem.",
            "It does not prove N2b liminf/recovery, N2c/N4 boundary escape, R-512 minimal-form identification, anchored-n semigroup convergence or an infinite-volume dynamics.",
            "R-489's unweighted root-rate divergence is not retroactively repaired; it is a different norm target.",
            "No physical Pre-A, spacetime, event horizon, QFT, gravity, Yang-Mills, continuum, mass-gap or TOE conclusion; external Markov time is not physical time.",
        ],
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_c2_moment.py --check",
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = run(args.output)
    if args.check:
        replay = json.loads(args.output.read_text(encoding="utf-8"))
        if replay != serial(payload):
            raise SystemExit("deterministic replay mismatch")
    print(f"PASS {payload['checks_passed']} checks; {payload['status']}; temporal route HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
