#!/usr/bin/env python3
"""Independent numerical replay of the PAH-OMC-020 second-order witness.

This implementation deliberately uses the frozen full source energy and a
different floating-point/nested-generator path from the primary exact
exponential-polynomial implementation.  It does not import the primary
verifier or its residual terms.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import tempfile
from functools import lru_cache
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-second-order-defect-contract-v1.json"
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC013 = ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json"
OMC013_CODE = ROOT / "codes/foundations/pah_omc013_full_q_eventual_intertwining.py"
R493_LEAN = ROOT / "verification/lean/Tect/R493.lean"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-second-order-defect/independent.json"
PINS = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-013": "e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc",
    "OMC013-code": "bda0c7bd7ed5f8b3871fd7590b600458589c4b5feba0a147219e94cdae0526a0",
    "R493-Lean": "c350035719b939c429a9e09d163015d34a471c3e6ea7c4678d4a88049060bc88",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def module() -> Any:
    spec = importlib.util.spec_from_file_location("pah_omc013_independent_source", OMC013_CODE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load source implementation")
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def key(state: dict[str, dict[Any, int]]) -> tuple[tuple[str, tuple[tuple[Any, int], ...]], ...]:
    return tuple((name, tuple(sorted(values.items()))) for name, values in sorted(state.items()))


def unkey(value: tuple[tuple[str, tuple[tuple[Any, int], ...]], ...]) -> dict[str, dict[Any, int]]:
    return {name: dict(values) for name, values in value}


def observable(state: dict[str, dict[Any, int]]) -> int:
    return state["ell"][(0, 0)]


def mobility(source: Any, before: dict[str, dict[Any, int]], after: dict[str, dict[Any, int]], root: dict[str, Any]) -> float:
    if root["family"] == "phase":
        return float(source.aperture(before["aperture"][root["vertex"]]))
    if root["family"] == "aperture":
        return math.sqrt(float(source.aperture(before["aperture"][root["vertex"]]) * source.aperture(after["aperture"][root["vertex"]])))
    left, right = source.edge_lookup(root["level"])[root["edge"]][1:]
    return math.sqrt(float(source.aperture(before["aperture"][left]) * source.aperture(before["aperture"][right])))


@lru_cache(maxsize=None)
def transition_table_cached(source: Any, level: int, state_key: tuple[tuple[str, tuple[tuple[Any, int], ...]], ...], r_max: int) -> tuple[tuple[Any, float], ...]:
    state = unkey(state_key)
    rows = []
    for root0 in source.root_catalog(level):
        root = dict(root0)
        root["level"] = level
        after = source.apply_root(state, root)
        if after is None:
            continue
        delta = source.energy(level, after, Fraction(r_max)) - source.energy(level, state, Fraction(r_max))
        rows.append((key(after), mobility(source, state, after, root) * math.exp(-float(delta) / 2.0)))
    return tuple(rows)


def transition_table(source: Any, level: int, state: dict[str, dict[Any, int]], r_max: int) -> tuple[tuple[Any, float], ...]:
    return transition_table_cached(source, level, key(state), r_max)


def generator(source: Any, level: int, state: dict[str, dict[Any, int]], r_max: int, value_fn: Any) -> float:
    base = value_fn(state)
    result = 0.0
    for target, rate in transition_table(source, level, state, r_max):
        result += rate * (value_fn(unkey(target)) - base)
    return result


def lifted_generator(source: Any, coarse_level: int, fine: dict[str, dict[Any, int]], r_max: int) -> float:
    coarse = source.project_state(coarse_level, fine)[0]
    base = observable(coarse)
    value_fn = lambda state: observable(source.project_state(coarse_level, state)[0])
    result = 0.0
    for target, rate in transition_table(source, coarse_level + 1, fine, r_max):
        result += rate * (value_fn(unkey(target)) - base)
    return result


def second_fine(source: Any, coarse_level: int, fine: dict[str, dict[Any, int]], r_max: int) -> float:
    base = lifted_generator(source, coarse_level, fine, r_max)
    result = 0.0
    for target, rate in transition_table(source, coarse_level + 1, fine, r_max):
        result += rate * (lifted_generator(source, coarse_level, unkey(target), r_max) - base)
    return result


def second_coarse(source: Any, coarse_level: int, coarse: dict[str, dict[Any, int]], r_max: int) -> float:
    base = generator(source, coarse_level, coarse, r_max, observable)
    result = 0.0
    for target, rate in transition_table(source, coarse_level, coarse, r_max):
        result += rate * (generator(source, coarse_level, unkey(target), r_max, observable) - base)
    return result


def run(output: Path = OUTPUT) -> dict[str, Any]:
    contract = read(CONTRACT)
    source = module()
    paths = {"PAH-001": PAH001, "PAH-OMC-013": OMC013, "OMC013-code": OMC013_CODE, "R493-Lean": R493_LEAN}
    actual = {name: sha(path) for name, path in paths.items()}
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, detail: Any) -> None:
        rows.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": detail})

    check("independent parent hashes", actual == PINS, {"actual": actual, "expected": PINS})
    check("unchanged firewall", all(contract["preservation_firewall"].values()), contract["preservation_firewall"])
    check("registered witness", contract["witness"]["coarse_level"] == 3 and contract["witness"]["R_max"] == 1 and contract["witness"]["sample_variant"] == 3, contract["witness"])

    n, r_max = 3, 1
    fine = source.sample_state(n + 1, 3)
    coarse = source.project_state(n, fine)[0]
    first = lifted_generator(source, n, fine, r_max) - generator(source, n, coarse, r_max, observable)
    second = second_fine(source, n, fine, r_max) - second_coarse(source, n, coarse, r_max)
    expected = 0.5 * (math.exp(-67 / 24) + math.exp(-59 / 24) - math.exp(-25 / 8) - math.exp(-17 / 8))
    check("first-order direct replay is zero", abs(first) < 1e-12, first)
    check("second-order direct replay is negative", second < -1e-6, second)
    check("independent residual matches factorized oracle", abs(second - expected) < 1e-10, {"actual": second, "expected": expected})
    check("threshold is not below N(f)", n == contract["witness"]["N_f"], {"n": n, "N_f": contract["witness"]["N_f"]})
    check("no physical promotion", not contract["status"]["physical_promotion"] and not contract["status"]["claim_bearing"], contract["status"])

    failed = [row for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/pah-omc020-second-order-defect-independent/1.0",
        "audit_id": "PAH-OMC-020-SECOND-ORDER-DEFECT-INDEPENDENT-001",
        "result_id": "R-551",
        "task_id": "T-083",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "NEGATIVE_RESULT" if not failed else "HOLD_FOR_EVIDENCE",
        "source_hashes": actual,
        "first_order_residual": first,
        "second_order_residual": second,
        "factorized_oracle": expected,
        "checks": rows,
        "checks_passed": len(rows) - len(failed),
        "checks_failed": len(failed),
        "finding": contract["finding"],
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
        "code_sha256": sha(Path(__file__)),
    }
    atomic(output, payload)
    print(f"PAH-OMC-020 SECOND-ORDER DEFECT INDEPENDENT: {payload['verification']} {payload['checks_passed']}/{len(rows)}; residual={second}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    return 0 if run(destination)["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
