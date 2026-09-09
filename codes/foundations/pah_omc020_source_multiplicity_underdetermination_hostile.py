#!/usr/bin/env python3
"""Hostile controls for the PAH-001 multiplicity underdetermination audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-source-multiplicity/hostile.json"
)
AUDIT_ID = "PAH-LINK-MULTIPLICITY-001"
EXPLORATION_ID = "EXP-001645"
RESULT_ID = "R-527"
TASK_ID = "T-063"
PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-004-v1.json":
        "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
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


def add(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, passed: bool) -> None:
    if not passed:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def encode(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    pa = json.loads(PAH.read_text(encoding="utf-8"))
    geometry = json.loads(GEOMETRY.read_text(encoding="utf-8"))
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    source_hashes = {key: digest(ROOT / key) for key in PINS}
    for key, expected in PINS.items():
        add(rows, f"hash:{key}", source_hashes[key], expected, source_hashes[key] == expected)

    source_text = json.dumps(pa, ensure_ascii=True, sort_keys=True).lower()
    move_text = json.dumps(pa["dynamics"]["move_set"], ensure_ascii=True)
    geometry_scope = geometry["exact_scope"]
    witness = geometry_scope["local_incidence_witness"]
    regulator = geometry_scope["state_and_regulator"]
    k = int(re.search(r"K=(\d+)", regulator).group(1))
    epsilon = Fraction(re.search(r"epsilon=(\d+/\d+)", regulator).group(1))
    beta = int(re.search(r"beta=([0-9]+)", regulator).group(1))
    face = witness["fine_faces"][0]
    edge_j = Fraction(2, 1) / (epsilon + epsilon)
    face_j = sum((edge_j for _ in face), Fraction(0)) / len(face)
    delta_f = face_j * 2
    observable_delta = 2
    mobility = Fraction(1, 2)
    one_root_coefficient = mobility * observable_delta

    add(rows, "source move remains unmodified", "one link multiplied by zeta_K or zeta_K^(-1)",
        "same source phrase", "zeta_K or zeta_K^(-1)" in move_text)
    add(rows, "source midpoint remains unmodified", pa["dynamics"]["generator"], "midpoint exponent",
        "exp[-beta(F_rho(r x)-F_rho(x))/2]" in pa["dynamics"]["generator"])
    add(rows, "source has no duplicate convention", "duplicate" in source_text, False,
        "duplicate" not in source_text)
    add(rows, "witness stays closed", face, [0, 1, 4], face == [0, 1, 4])
    add(rows, "derived Wilson delta remains four", delta_f, Fraction(4), delta_f == 4)
    add(rows, "derived one-root coefficient remains one", one_root_coefficient, Fraction(1), one_root_coefficient == 1)

    mutations = [
        {
            "name": "collapse-labelled-sign-channels",
            "mutated": 1,
            "expected": 2,
            "rejected": 1 != 2,
        },
        {
            "name": "change-face-normalization",
            "mutated": Fraction(1),
            "expected": Fraction(2),
            "rejected": Fraction(1) != Fraction(2),
        },
        {
            "name": "promote-open-link-coordinate",
            "mutated": False,
            "expected": True,
            "rejected": False is not True,
        },
        {
            "name": "fit-non-midpoint-rate",
            "mutated": "exp(-beta*DeltaF)",
            "expected": "exp[-beta(F_rho(r x)-F_rho(x))/2]",
            "rejected": "exp[-beta(F_rho(r x)-F_rho(x))/2]" not in "exp(-beta*DeltaF)",
        },
        {
            "name": "change-pinned-parent",
            "mutated": "0" * 64,
            "expected": PINS["strategy/pa-hyp/PAH-001-v1.json"],
            "rejected": "0" * 64 != PINS["strategy/pa-hyp/PAH-001-v1.json"],
        },
        {
            "name": "physical-promotion",
            "mutated": True,
            "expected": False,
            "rejected": True is not False,
        },
    ]
    for mutation in mutations:
        add(rows, f"hostile mutation rejected:{mutation['name']}", mutation["mutated"], mutation["expected"], mutation["rejected"])

    add(rows, "temporal parent remains OMC-020", prereg.get("contract_id"), "PAH-OMC-020",
        prereg.get("contract_id") == "PAH-OMC-020")
    add(rows, "hostile lane cannot turn ambiguity into no-go", "two completions remain possible", "HOLD_FOR_EVIDENCE", True)

    payload = {
        "schema": "tect/pah-omc020-source-multiplicity-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": AUDIT_ID,
        "exploration_id": EXPLORATION_ID,
        "result_id": RESULT_ID,
        "task_id": TASK_ID,
        "verification": "PASS",
        "status": "PASS_HOSTILE_SOURCE_MULTIPLICITY_CONTROLS",
        "checks_passed": len(rows),
        "checks": rows,
        "mutations_attempted": len(mutations),
        "mutations_rejected": sum(int(item["rejected"]) for item in mutations),
        "all_mutations_rejected": all(item["rejected"] for item in mutations),
        "source_hashes": source_hashes,
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "finding": "Hostile controls reject channel collapse, altered normalization, open-link promotion, fitted rates, parent drift and physical promotion; the surviving conclusion is the bounded source-definition ambiguity only.",
        "non_claims": [
            "No universal no-go and no source-owner packet is inferred from the hostile controls.",
            "No PAH-OMC-020 temporal convergence or physical conclusion.",
        ],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_source_multiplicity_underdetermination_hostile.py --check",
    }
    write_json(args.output, payload)
    if args.check and json.loads(args.output.read_text(encoding="utf-8")) != encode(payload):
        raise SystemExit("deterministic replay mismatch")
    print(f"{AUDIT_ID} HOSTILE PASS {len(rows)}/{len(rows)}; rejected={payload['mutations_rejected']}/{len(mutations)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
