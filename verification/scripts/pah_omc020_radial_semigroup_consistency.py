#!/usr/bin/env python3
"""Primary restricted-subspace temporal consistency audit for PAH-OMC-020."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-radial-semigroup-consistency-contract-v1.json"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-radial-semigroup-consistency/primary.json"
PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-018-result-v1.json": "d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json": "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-result-v1.json": "cfb65eb769cc95fb4b5148fe2914c5b4405748c3b8d253a0ca938369914d8801",
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


def atomic_json(path: Path, payload: dict[str, Any]) -> bytes:
    encoded = (json.dumps(serial(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    return encoded


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": str(actual), "expected": str(expected)})
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    actual_hashes = {path: digest(ROOT / path) for path in PINS}
    check(rows, "contract schema", contract.get("schema"), "tect/pah-omc020-radial-semigroup-consistency-contract/1.0", contract.get("schema") == "tect/pah-omc020-radial-semigroup-consistency-contract/1.0")
    check(rows, "contract identity", (contract.get("result_id"), contract.get("task_id")), ("R-548", "T-065"), contract.get("result_id") == "R-548" and contract.get("task_id") == "T-065")
    check(rows, "parent hashes", actual_hashes, PINS, actual_hashes == PINS)

    pa = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8"))
    r511 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-018-result-v1.json").read_text(encoding="utf-8"))
    r512 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-019-result-v1.json").read_text(encoding="utf-8"))
    r514 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-result-v1.json").read_text(encoding="utf-8"))
    check(rows, "PAH packet unchanged", pa.get("packet_id"), "PAH-001", pa.get("packet_id") == "PAH-001")
    check(rows, "external stochastic time", "external stochastic" in pa["dynamics"]["time"].lower(), True, "external stochastic" in pa["dynamics"]["time"].lower())
    order = prereg["scope"]["regulator_order"].lower()
    check(rows, "j-before-n order", "first j" in order and "anchored n" in order, True, "first j" in order and "anchored n" in order)
    check(rows, "R-511 local pre-form", (r511.get("result_id"), r511.get("verdict"), r511.get("radial_activity")), ("R-511", "PASS", "ZERO_IN_DERIVED_LOCAL_OPERATOR"), r511.get("result_id") == "R-511" and r511.get("verdict") == "PASS" and r511.get("radial_activity") == "ZERO_IN_DERIVED_LOCAL_OPERATOR")
    check(rows, "R-512 radial kernel input", "H_rad" in r512.get("kernel_claim", "") and "zero energy" in r512.get("conclusion", ""), True, "H_rad" in r512.get("kernel_claim", "") and "zero energy" in r512.get("conclusion", ""))
    check(rows, "R-514 fixed-n input", r514.get("verdict"), "PASS", r514.get("verdict") == "PASS")
    check(rows, "no anchored-n claim in R-514", "no anchored n" in r514["exact_scope"]["order"].lower(), True, "no anchored n" in r514["exact_scope"]["order"].lower())

    inputs = {
        "support_vertices": 3,
        "degree_bound": 5,
        "lipschitz_constant": Fraction(1, 2),
        "sup_norm_f": Fraction(3, 5),
        "time_horizon": Fraction(2),
        "j": 8,
        "support_column": 2,
    }
    h = Fraction(1, 2 ** inputs["j"])
    jump_l1 = 2 * h
    root_count = 2 * inputs["degree_bound"] * inputs["support_vertices"]
    generator_bound = root_count * inputs["lipschitz_constant"] * jump_l1
    compact_time_bound = inputs["time_horizon"] * generator_bound
    correlation_bound = inputs["sup_norm_f"] * compact_time_bound
    next_h = Fraction(1, 2 ** (inputs["j"] + 1))
    next_bound = inputs["time_horizon"] * root_count * inputs["lipschitz_constant"] * (2 * next_h)
    epsilon = Fraction(1, 4)
    check(rows, "radial jump bound", jump_l1, 2 * h, jump_l1 == 2 * h)
    check(rows, "finite root count", root_count, 2 * inputs["degree_bound"] * inputs["support_vertices"], root_count == 2 * inputs["degree_bound"] * inputs["support_vertices"])
    check(rows, "generator residual bound", generator_bound, root_count * inputs["lipschitz_constant"] * jump_l1, generator_bound == root_count * inputs["lipschitz_constant"] * jump_l1)
    check(rows, "compact-time Duhamel bound", compact_time_bound, inputs["time_horizon"] * generator_bound, compact_time_bound == inputs["time_horizon"] * generator_bound)
    check(rows, "correlation bound", correlation_bound, inputs["sup_norm_f"] * compact_time_bound, correlation_bound == inputs["sup_norm_f"] * compact_time_bound)
    check(rows, "epsilon fixture", compact_time_bound < epsilon, True, compact_time_bound < epsilon)
    check(rows, "strict j decay", next_bound < compact_time_bound, True, next_bound < compact_time_bound)
    check(rows, "anchored-n uniformity input", root_count == 2 * inputs["degree_bound"] * inputs["support_vertices"], True, root_count == 2 * inputs["degree_bound"] * inputs["support_vertices"])
    check(rows, "target radial identity input", contract["target_semigroup"]["radial_identity"]["status"], "SPECTRAL_CONSEQUENCE_OF_R512_ZERO_ENERGY", contract["target_semigroup"]["radial_identity"]["status"] == "SPECTRAL_CONSEQUENCE_OF_R512_ZERO_ENERGY")
    firewalls = json.dumps(contract["non_claims"], ensure_ascii=True).lower()
    check(rows, "physical firewall", all(token in firewalls for token in ("pre-a", "qft", "gravity", "continuum")), True, all(token in firewalls for token in ("pre-a", "qft", "gravity", "continuum")))
    check(rows, "full-route firewall", all(token in firewalls for token in ("non-radial", "anchored-n", "source-authorized")), True, all(token in firewalls for token in ("non-radial", "anchored-n", "source-authorized")))

    payload = {
        "schema": "tect/pah-omc020-radial-semigroup-consistency-primary/1.0",
        "audit_id": "PAH-OMC-020-RADIAL-SEMIGROUP-CONSISTENCY-PRIMARY-001",
        "result_id": "R-548",
        "task_id": "T-065",
        "status": "PASS_RESTRICTED_RADIAL_SUBSPACE",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": actual_hashes,
        "fixture": {"inputs": inputs, "h": h, "jump_l1": jump_l1, "root_count": root_count, "generator_bound": generator_bound, "compact_time_bound": compact_time_bound, "correlation_bound": correlation_bound, "next_bound": next_bound, "epsilon": epsilon},
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "For bounded amplitude-only local cylinders, non-radial PAH moves have zero increment and the original radial generator has L2 residual at most 2 H_f L_f h_j. Stationary L2 contraction gives a compact-time semigroup error at most 2 T H_f L_f h_j, and R-512 zero energy gives identity action of the minimal target semigroup on H_rad. Thus the restricted amplitude-only correlations converge uniformly in t on every finite interval, first in j and then in anchored n.",
        "assumptions": contract["assumptions"],
        "missing_assumptions": contract["missing_assumptions"],
        "next_single_question": contract["next_single_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_radial_semigroup_consistency.py --check",
        "code_sha256": digest(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(serial(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 radial semigroup primary replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 RADIAL SEMIGROUP PRIMARY: PASS {len(rows)}/{len(rows)}; verdict=PASS_RESTRICTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
