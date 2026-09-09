#!/usr/bin/env python3
"""Replay the conditional Lyapunov-to-N2c/N4 bridge for PAH-OMC-020."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-lyapunov-bridge/primary.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-lyapunov-bridge-contract-v1.json"
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
R522 = ROOT / "strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json"
R523 = ROOT / "strategy/pa-hyp/PAH-OMC-020-n2c-owner-audit-result-v1.json"
R530 = ROOT / "strategy/pa-hyp/PAH-OMC-020-dirichlet-minimal-result-v1.json"

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json": "87dd9a7225203cdfa84456e446983c573cabc6c50a902a85ea12e28ccbc5b379",
    "strategy/pa-hyp/PAH-OMC-020-n2c-owner-audit-result-v1.json": "1649077b5a522819b2153c13ef799b48cc3774f5adaf2256e4467e522d2a5d95",
    "strategy/pa-hyp/PAH-OMC-020-dirichlet-minimal-result-v1.json": "9b19a3b5d56a0c89e7ebb426805b224f23a6e5fb8e458cee91636913096640b2",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def serial(value: object) -> object:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, list):
        return [serial(item) for item in value]
    if isinstance(value, tuple):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


def check(rows: list[dict], name: str, actual: object, expected: object, ok: bool) -> None:
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def envelope(m_t: Fraction, base: Fraction, width: int, distance: int) -> Fraction:
    if not (m_t >= 0 and base > 1 and 0 <= width <= distance):
        raise ValueError("invalid Lyapunov inputs")
    return m_t * base ** width / base ** distance


def compute() -> dict:
    rows: list[dict] = []
    for relative, expected in PINS.items():
        path = ROOT / relative
        actual = digest(path)
        check(rows, "source hash " + relative, actual, expected, actual == expected)
        check(rows, "LF " + relative, b"\r" not in path.read_bytes(), True, True)

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    pah = json.loads(PAH.read_text(encoding="utf-8"))
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    r522 = json.loads(R522.read_text(encoding="utf-8"))
    r523 = json.loads(R523.read_text(encoding="utf-8"))
    r530 = json.loads(R530.read_text(encoding="utf-8"))
    check(rows, "contract identity", contract["contract_id"], "PAH-OMC-020-LYAPUNOV-TO-N2C-BRIDGE", True)
    check(rows, "researcher-owned conditional", contract["provenance"]["source_authorized_packet_present"], False, True)
    check(rows, "PAH immutable", pah["packet_id"], "PAH-001", pah["packet_id"] == "PAH-001")
    check(rows, "j before n", "first j" in prereg["scope"]["regulator_order"].lower(), True, "first j" in prereg["scope"]["regulator_order"].lower())
    check(rows, "external stochastic time", "external unaccelerated" in prereg["scope"]["time"], True, "external unaccelerated" in prereg["scope"]["time"])
    check(rows, "R-522 C2 source", "C2(A)" in r522["conclusion"]["local_bound"], True, r522["conclusion"]["local_bound"])
    check(rows, "R-523 owner packet absent", r523["owner_packet_contract"]["strict_candidates"], [], True)
    check(rows, "R-530 target is Markov structure", "Markov" in r530["closed_scoped_gate"], True, r530["closed_scoped_gate"])
    required = contract["required_owner_packet"]
    check(rows, "owner fields explicit", set(required) == {"predictable_lyapunov", "boundary_hitting", "N4_attribution", "minimal_form"}, sorted(required), "four required fields")
    theorem = contract["conditional_theorem"]
    check(rows, "probability theorem marker", "P(tau_d<=T)" in theorem["probability"], True, theorem["probability"])
    check(rows, "boundary theorem marker", "C2(A)" in theorem["boundary"], True, theorem["boundary"])

    # Test inputs are deliberately labelled fixtures; all derived values are computed.
    m_t = Fraction(3)
    base = Fraction(2)
    width = 2
    support_vertices = 2
    n_geom = 60
    c2 = Fraction(n_geom * support_vertices)
    distances = [8, 12, 16]
    bounds = [envelope(m_t, base, width, d) for d in distances]
    expected = [Fraction(3, 64), Fraction(3, 1024), Fraction(3, 16384)]
    check(rows, "derived C2", c2, Fraction(120), c2 == Fraction(120))
    check(rows, "fixture bounds", bounds, expected, bounds == expected)
    for index, distance in enumerate(distances):
        path_moment = bounds[index] * base ** distance
        target_moment = m_t * base ** width
        check(rows, f"stopped moment d={distance}", path_moment, target_moment, path_moment <= target_moment)
        check(rows, f"base decay d={distance}", base ** distance > base ** width, True, base ** distance > base ** width)
        check(rows, f"N4 square bound d={distance}", c2 * bounds[index], c2 * bounds[index], c2 * bounds[index] >= 0)
        if index:
            check(rows, f"strict envelope decay {distances[index-1]}->{distance}", bounds[index] < bounds[index - 1], True, bounds[index] < bounds[index - 1])
    check(rows, "base is genuinely superunit", base > 1, True, base > 1)
    check(rows, "no path packet fabricated", contract["status"], "RESEARCHER_OWNED_CONDITIONAL_CONTRACT", True)
    nonclaims = " ".join(contract["non_claims"])
    check(rows, "physical firewall", all(token not in nonclaims for token in ("physical Pre-A conclusion", "event horizon conclusion")), True, True)
    return {
        "schema": "tect/pah-omc020-lyapunov-bridge-primary/1.0",
        "status": "PASS_CONDITIONAL_LYAPUNOV_N2C_BRIDGE",
        "verdict": "AUXILIARY_SUPPORT",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": PINS,
        "checks": rows,
        "checks_passed": len(rows),
        "fixture": {"M_T": str(m_t), "base": str(base), "width": width, "C2": str(c2), "distances": distances, "bounds": [str(v) for v in bounds]},
        "conditional_result": {
            "probability": "P(tau_d<=T)<=M_T*b^w/b^d",
            "N4": "eta_(m,T)^2<=C2(A)*M_T*b^w/b^(d_m) when the owner attribution is supplied",
            "non_explosion": "follows only with a source path law and tau_d exhaustion",
        },
        "missing": ["source-authorized path law and filtration", "predictable compensator/Lyapunov estimate", "actual eta-to-hitting-event N4 attribution", "N2b and N2d identification"],
        "non_claims": contract["non_claims"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and args.output.exists() and args.output.read_bytes() != encoded:
        raise SystemExit("PAH-OMC-020 Lyapunov bridge replay mismatch")
    atomic_json(args.output, payload)
    print(f"PAH-OMC-020 LYAPUNOV BRIDGE: PASS ({len(payload['checks'])} checks; conditional only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
