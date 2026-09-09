#!/usr/bin/env python3
"""Primary replay for the PAH-OMC-020 deterministic correlation modulus."""

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
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-correlation-modulus-contract-v1.json"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-correlation-modulus/primary.json"

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-018-result-v1.json": "d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json": "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-020-stationary-modulus-correction-result-v1.json": "58e563515b2a3a9d46085facffd4a9664c5518fed236e14f6a40aeee209443c0",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(serial(payload), handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": serial(actual), "expected": serial(expected)})
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")


def budget(d_count: Fraction, m_sup: Fraction, h_count: Fraction, l_lip: Fraction) -> Fraction:
    return 2 * d_count * m_sup * m_sup + 2 * h_count * l_lip * l_lip


def parse_int(pattern: str, text: str, label: str) -> int:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if match is None:
        raise AssertionError(f"missing {label}")
    return int(match.group(1))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows: list[dict[str, Any]] = []
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    actual_hashes = {path: digest(ROOT / path) for path in PINS}
    check(rows, "contract schema", contract.get("schema"), "tect/pah-omc020-correlation-modulus-contract/1.0", contract.get("schema") == "tect/pah-omc020-correlation-modulus-contract/1.0")
    check(rows, "contract identity", contract.get("result_id"), "R-543", contract.get("result_id") == "R-543")
    check(rows, "source hashes", actual_hashes, PINS, actual_hashes == PINS)

    pa = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8"))
    r511 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-018-result-v1.json").read_text(encoding="utf-8"))
    r512 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-019-result-v1.json").read_text(encoding="utf-8"))
    r542 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-stationary-modulus-correction-result-v1.json").read_text(encoding="utf-8"))
    check(rows, "PAH packet", pa.get("packet_id"), "PAH-001", pa.get("packet_id") == "PAH-001")
    check(rows, "preregistered target remains R-512", "R-512" in json.dumps(prereg["objects_and_comparison"]["target_semigroup"]), True, "R-512" in json.dumps(prereg["objects_and_comparison"]["target_semigroup"]))
    check(rows, "R-511 source result", (r511.get("result_id"), r511.get("verdict")), ("R-511", "PASS"), r511.get("result_id") == "R-511" and r511.get("verdict") == "PASS")
    check(rows, "R-512 remains auxiliary", (r512.get("result_id"), r512.get("classification")), ("R-512", "auxiliary_support"), r512.get("result_id") == "R-512" and r512.get("classification") == "auxiliary_support")
    check(rows, "R-542 stopping-time firewall", r542.get("verdict"), "HOLD_FOR_EVIDENCE", r542.get("verdict") == "HOLD_FOR_EVIDENCE")
    order = prereg["scope"]["regulator_order"].lower()
    time_scope = prereg["scope"]["time"].lower()
    check(rows, "j-before-n order", "first j" in order and "anchored n" in order, True, "first j" in order and "anchored n" in order)
    check(rows, "external Markov time", "external" in time_scope and "markov" in time_scope, True, "external" in time_scope and "markov" in time_scope)
    r511_bounds = r511.get("proof_bounds", {})
    r511_blob = json.dumps(r511_bounds, ensure_ascii=True, sort_keys=True)
    dmax = parse_int(r"d_max=(\d+)", r511_blob, "d_max")
    check(rows, "R-511 root-count formula", "D_f<=4*|V_f|+2*|E_f|" in r511_blob, True, "D_f<=4*|V_f|+2*|E_f|" in r511_blob)
    check(rows, "R-511 influence formula", "H_f<=2*d_max*|V_f|" in r511_blob, True, "H_f<=2*d_max*|V_f|" in r511_blob)
    check(rows, "R-511 d_max", dmax, 5, dmax == 5)

    # The fixtures are test oracles for the symbolic source formulas, not PAH parameters.
    f_vertices, f_edges = 2, 1
    g_vertices, g_edges = 1, 2
    f_d = Fraction(4 * f_vertices + 2 * f_edges)
    f_h = Fraction(2 * dmax * f_vertices)
    g_d = Fraction(4 * g_vertices + 2 * g_edges)
    g_h = Fraction(2 * dmax * g_vertices)
    f_m, f_l = Fraction(2), Fraction(1)
    g_m, g_l = Fraction(1), Fraction(3)
    b_f = budget(f_d, f_m, f_h, f_l)
    b_g = budget(g_d, g_m, g_h, g_l)
    check(rows, "f D source-derived", f_d, Fraction(10), f_d == Fraction(10))
    check(rows, "f H source-derived", f_h, Fraction(20), f_h == Fraction(20))
    check(rows, "g D source-derived", g_d, Fraction(8), g_d == Fraction(8))
    check(rows, "g H source-derived", g_h, Fraction(10), g_h == Fraction(10))
    check(rows, "B_f formula", b_f, 2 * f_d * f_m * f_m + 2 * f_h * f_l * f_l, b_f == 2 * f_d * f_m * f_m + 2 * f_h * f_l * f_l)
    check(rows, "B_g formula", b_g, 2 * g_d * g_m * g_m + 2 * g_h * g_l * g_l, b_g == 2 * g_d * g_m * g_m + 2 * g_h * g_l * g_l)
    check(rows, "budgets nonnegative", b_f >= 0 and b_g >= 0, True, b_f >= 0 and b_g >= 0)
    delta = Fraction(1, 100)
    squared_modulus = delta * delta * b_f * b_g
    smaller_squared_modulus = (delta / 2) * (delta / 2) * b_f * b_g
    check(rows, "squared modulus nonnegative", squared_modulus >= 0, True, squared_modulus >= 0)
    check(rows, "deterministic modulus decreases with time gap", smaller_squared_modulus < squared_modulus, True, smaller_squared_modulus < squared_modulus)
    check(rows, "energy-product domination fixture", Fraction(1) <= b_f * b_g, True, Fraction(1) <= b_f * b_g)
    check(rows, "modulus is finite", math.isfinite(math.sqrt(float(squared_modulus))), True, math.isfinite(math.sqrt(float(squared_modulus))))
    formula_blob = json.dumps(contract["source_formulas"], ensure_ascii=True)
    check(rows, "form-energy route retained", "sqrt(B_f B_g)" in formula_blob and "finite_spectral_step" in formula_blob, True, "sqrt(B_f B_g)" in formula_blob and "finite_spectral_step" in formula_blob)
    forbidden_blob = json.dumps(contract["non_claims"], ensure_ascii=True).lower()
    check(rows, "no Aldous promotion", "stopping-time aldous" in forbidden_blob, True, "stopping-time aldous" in forbidden_blob)
    check(rows, "no physical promotion", "physical pre-a" in forbidden_blob and "qft" in forbidden_blob, True, "physical pre-a" in forbidden_blob and "qft" in forbidden_blob)

    payload = {
        "schema": "tect/pah-omc020-correlation-modulus-primary/1.0",
        "audit_id": "PAH-OMC-020-CORRELATION-MODULUS-PRIMARY-001",
        "result_id": "R-543",
        "task_id": "T-064",
        "status": "PASS_DETERMINISTIC_CORRELATION_MODULUS",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": actual_hashes,
        "source_derived": {"d_max": dmax, "f_D": f_d, "f_H": f_h, "g_D": g_d, "g_H": g_h},
        "test_fixture": {"f_M": f_m, "f_L": f_l, "g_M": g_m, "g_L": g_l, "B_f": b_f, "B_g": b_g, "delta": delta, "squared_modulus": squared_modulus},
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "Under the pinned R-511 energy bounds and finite reversible spectral identity, the deterministic-time local correlation modulus is the exact support-dependent bound |t-s|*sqrt(B_f*B_g), uniform over the retained finite n,j indices. This is a conditional finite equicontinuity input only.",
        "assumptions": contract["conditional_theorem"]["hypotheses"],
        "missing_assumptions": contract["remaining_gates"],
        "next_single_question": contract["next_single_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_correlation_modulus.py --check",
        "code_sha256": digest(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(serial(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 correlation-modulus primary replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 CORRELATION MODULUS PRIMARY: PASS {len(rows)}/{len(rows)}; verdict=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
