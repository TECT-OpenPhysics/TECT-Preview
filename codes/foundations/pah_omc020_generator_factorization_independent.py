#!/usr/bin/env python3
"""Non-importing independent replay of the R-549 factorization algebra."""

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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-generator-factorization-contract-v1.json"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-generator-factorization/independent.json"
PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-result-v1.json": "0e40aeba3c6ab41b65842550163b26fc709e9aee8137258a7d630c54da8341d2",
    "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json": "dcee1aba3cb53607e6902829d28a0b79878f27a5de2eee79c131d6ab36dd393e",
    "strategy/pa-hyp/PAH-OMC-020-energy-intertwining-result-v1.json": "0e0268925eee2dd4b74ed5b279f4a56fb66637f86cb9faa608df1edbb99c7299",
    "strategy/pa-hyp/PAH-OMC-020-energy-intertwining-contract-v1.json": "37ffd8a1f82ac83b9dabb955f62a8e5b9bdb68ba5588ac9f30fdf154127883d1",
    "strategy/pa-hyp/PAH-OMC-020-core-duhamel-result-v1.json": "4062188d9419a42d74b0350d35a62950c987e5d7b5f38d329bb7f09d09844d01",
    "strategy/pa-hyp/PAH-OMC-020-core-duhamel-contract-v1.json": "1a56da4afc45c15357f9e2aee9e35216ca515aa618a6af6077f53444a3d73dcf"
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ser(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): ser(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [ser(v) for v in value]
    return value


def atomic(path: Path, payload: dict[str, Any]) -> None:
    encoded = (json.dumps(ser(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def check(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any = None, expected: Any = True) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": ser(actual), "expected": ser(expected)})
    if not ok:
        raise AssertionError(name)


def T(a: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(c) for c in zip(*a)]


def M(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def S(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[a[i][j] - b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def A(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def V(a: list[list[Fraction]], x: list[Fraction]) -> list[Fraction]:
    return [sum(a[i][j] * x[j] for j in range(len(x))) for i in range(len(a))]


def norm(x: list[Fraction]) -> Fraction:
    return sum((abs(y) for y in x), Fraction(0))


def run() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    hashes = {p: sha(ROOT / p) for p in PINS}
    check(rows, "contract identity", contract.get("result_id") == "R-549" and contract.get("task_id") == "T-081", (contract.get("result_id"), contract.get("task_id")), ("R-549", "T-081"))
    check(rows, "parent hashes", hashes == PINS, hashes, PINS)
    check(rows, "candidate remains unauthorized", contract["provenance"].get("source_authorized_packet_present") is False)
    check(rows, "order unchanged", "j-to-infinity" in contract["fixed_scope"]["order"] and "anchored n" in contract["fixed_scope"]["order"])
    check(rows, "physical non-claims", all(word in json.dumps(contract["non_claims"]).lower() for word in ("pre-a", "qft", "gravity", "continuum")))

    bs = [[Fraction(1), Fraction(2)], [Fraction(-1), Fraction(1)]]
    bt = [[Fraction(2), Fraction(1)], [Fraction(1), Fraction(3)]]
    ws = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(4)]]
    wt = [[Fraction(2), Fraction(0)], [Fraction(0), Fraction(5)]]
    u = [[Fraction(1), Fraction(1, 3)], [Fraction(2, 3), Fraction(1)]]
    c = [[Fraction(1), Fraction(1, 2)], [Fraction(0), Fraction(1)]]
    f = [Fraction(2, 5), Fraction(-1, 4)]
    ks = M(M(T(bs), ws), bs)
    kt = M(M(T(bt), wt), bt)
    g = S(M(bt, u), M(c, bs))
    d = S(M(M(T(bt), wt), c), M(M(u, T(bs)), ws))
    lhs = S(M(kt, u), M(u, ks))
    rhs = A(M(d, bs), M(M(T(bt), wt), g))
    lhsf = V(lhs, f)
    df = V(d, V(bs, f))
    gf = V(M(M(T(bt), wt), g), f)
    check(rows, "source factor K=B*WB", ks == [[Fraction(5), Fraction(-2)], [Fraction(-2), Fraction(8)]], ks, [[Fraction(5), Fraction(-2)], [Fraction(-2), Fraction(8)]])
    check(rows, "target factor K=B*WB", kt == [[Fraction(13), Fraction(19)], [Fraction(19), Fraction(47)]], kt, [[Fraction(13), Fraction(19)], [Fraction(19), Fraction(47)]])
    check(rows, "matrix identity", lhs == rhs, lhs, rhs)
    check(rows, "vector identity", lhsf == [df[i] + gf[i] for i in range(2)], lhsf, [df[i] + gf[i] for i in range(2)])
    check(rows, "both defects contribute", norm(df) > 0 and norm(gf) > 0, (norm(df), norm(gf)))
    check(rows, "divergence-only shortcut fails", norm(lhsf) != norm(df), (norm(lhsf), norm(df)))
    check(rows, "gradient-only shortcut fails", norm(lhsf) != norm(gf), (norm(lhsf), norm(gf)))
    return rows, {"source_B": bs, "target_B": bt, "source_W": ws, "target_W": wt, "U": u, "C": c, "f": f, "K_source": ks, "K_target": kt, "G": g, "D": d, "lhs_f": lhsf, "D_Bf": df, "BtWt_Gf": gf}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows, fixture = run()
    payload = {
        "schema": "tect/pah-omc020-generator-factorization-independent/1.0",
        "audit_id": "PAH-OMC-020-GENERATOR-FACTORIZATION-INDEPENDENT-001",
        "result_id": "R-549",
        "task_id": "T-081",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": {**{p: sha(ROOT / p) for p in PINS}},
        "fixture": fixture,
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "An independent rational fixture reproduces the weighted-incidence factorization and shows that both the gradient and adjoint-divergence defects are needed; no PAH owner packet is inferred.",
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_generator_factorization_independent.py --check",
        "code_sha256": sha(Path(__file__))
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(ser(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("R-549 independent replay mismatch")
    else:
        atomic(destination, payload)
    print(f"PAH-OMC-020 GENERATOR FACTORIZATION INDEPENDENT: PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
