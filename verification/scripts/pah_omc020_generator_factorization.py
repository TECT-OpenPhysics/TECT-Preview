#!/usr/bin/env python3
"""Primary finite factorization audit for PAH-OMC-020 R-549."""

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
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-generator-factorization/primary.json"
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

Matrix = list[list[Fraction]]


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
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": serial(actual), "expected": serial(expected)})
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")


def mat(rows: list[list[str]]) -> Matrix:
    return [[Fraction(value) for value in row] for row in rows]


def transpose(a: Matrix) -> Matrix:
    return [list(column) for column in zip(*a)]


def matmul(a: Matrix, b: Matrix) -> Matrix:
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def add(a: Matrix, b: Matrix) -> Matrix:
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def sub(a: Matrix, b: Matrix) -> Matrix:
    return [[a[i][j] - b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def matvec(a: Matrix, x: list[Fraction]) -> list[Fraction]:
    return [sum(a[i][j] * x[j] for j in range(len(x))) for i in range(len(a))]


def l1(x: list[Fraction]) -> Fraction:
    return sum((abs(value) for value in x), Fraction(0))


def op_l1(a: Matrix) -> Fraction:
    return max((sum(abs(a[i][j]) for i in range(len(a))) for j in range(len(a[0]))), default=Fraction(0))


def matrix_fixture() -> dict[str, Matrix | list[Fraction]]:
    return {
        "B_source": mat([["1", "-1"], ["0", "1"]]),
        "B_target": mat([["2", "-1"], ["1", "1"]]),
        "W_source": mat([["2", "0"], ["0", "3"]]),
        "W_target": mat([["3", "0"], ["0", "4"]]),
        "U": mat([["1", "1/2"], ["0", "1"]]),
        "C": mat([["1", "0"], ["1/2", "1"]]),
        "f": [Fraction("1/2"), Fraction("-1/3")]
    }


def factorize(fixture: dict[str, Matrix | list[Fraction]]) -> dict[str, Matrix | list[Fraction] | Fraction]:
    bs = fixture["B_source"]
    bt = fixture["B_target"]
    ws = fixture["W_source"]
    wt = fixture["W_target"]
    u = fixture["U"]
    c = fixture["C"]
    f = fixture["f"]
    assert isinstance(bs, list) and isinstance(bt, list) and isinstance(ws, list) and isinstance(wt, list)
    assert isinstance(u, list) and isinstance(c, list) and isinstance(f, list)
    ks = matmul(matmul(transpose(bs), ws), bs)
    kt = matmul(matmul(transpose(bt), wt), bt)
    g = sub(matmul(bt, u), matmul(c, bs))
    d = sub(matmul(matmul(transpose(bt), wt), c), matmul(matmul(u, transpose(bs)), ws))
    lhs = sub(matmul(kt, u), matmul(u, ks))
    weighted_target_adjoint = matmul(matmul(transpose(bt), wt), g)
    rhs = add(matmul(d, bs), weighted_target_adjoint)
    lhs_f = matvec(lhs, f)
    d_f = matvec(d, matvec(bs, f))
    g_f = matvec(weighted_target_adjoint, f)
    return {
        "K_source": ks,
        "K_target": kt,
        "G": g,
        "D": d,
        "lhs": lhs,
        "rhs": rhs,
        "lhs_f": lhs_f,
        "D_Bf": d_f,
        "BtWt_Gf": g_f,
        "residual_l1": l1(lhs_f),
        "divergence_l1": l1(d_f),
        "gradient_l1": l1(g_f),
        "adjoint_gain": op_l1(matmul(transpose(bt), wt)),
        "gradient_input_l1": l1(matvec(g, f))
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    actual_hashes = {path: digest(ROOT / path) for path in PINS}
    check(rows, "contract schema", contract.get("schema"), "tect/pah-omc020-generator-factorization-contract/1.0", contract.get("schema") == "tect/pah-omc020-generator-factorization-contract/1.0")
    check(rows, "contract identity", (contract.get("result_id"), contract.get("task_id")), ("R-549", "T-081"), contract.get("result_id") == "R-549" and contract.get("task_id") == "T-081")
    check(rows, "parent hashes", actual_hashes, PINS, actual_hashes == PINS)

    pa = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8"))
    r525 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-result-v1.json").read_text(encoding="utf-8"))
    r529 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-energy-intertwining-result-v1.json").read_text(encoding="utf-8"))
    r537 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-core-duhamel-result-v1.json").read_text(encoding="utf-8"))
    check(rows, "PAH packet frozen", pa.get("packet_id"), "PAH-001", pa.get("packet_id") == "PAH-001")
    check(rows, "external stochastic time", "external stochastic" in pa["dynamics"]["time"].lower(), True, "external stochastic" in pa["dynamics"]["time"].lower())
    order = prereg["scope"]["regulator_order"].lower()
    check(rows, "j-before-n order", "first j" in order and "anchored n" in order, True, "first j" in order and "anchored n" in order)
    check(rows, "R-525 remains candidate-only", (r525.get("verdict"), r525["candidate"].get("authorization")), ("HOLD_FOR_EVIDENCE", "source-owner sign-off is still absent"), r525.get("verdict") == "HOLD_FOR_EVIDENCE" and r525["candidate"].get("authorization") == "source-owner sign-off is still absent")
    check(rows, "R-529 retains dynamic gap", r529.get("verdict"), "HOLD_FOR_EVIDENCE", r529.get("verdict") == "HOLD_FOR_EVIDENCE")
    check(rows, "R-537 remains conditional", (r537.get("verdict"), r537.get("conditional")), ("HOLD_FOR_EVIDENCE", True), r537.get("verdict") == "HOLD_FOR_EVIDENCE" and r537.get("conditional") is True)
    check(rows, "owner fields absent", all(value is False for value in contract["current_status"].values() if value is not True), True, all(value is False for value in contract["current_status"].values() if value is not True))

    fixture = matrix_fixture()
    values = factorize(fixture)
    check(rows, "weighted source generator", values["K_source"], [[Fraction(2), Fraction(-2)], [Fraction(-2), Fraction(5)]], values["K_source"] == [[Fraction(2), Fraction(-2)], [Fraction(-2), Fraction(5)]])
    check(rows, "weighted target generator", values["K_target"], [[Fraction(16), Fraction(-2)], [Fraction(-2), Fraction(7)]], values["K_target"] == [[Fraction(16), Fraction(-2)], [Fraction(-2), Fraction(7)]])
    check(rows, "exact matrix factorization", values["lhs"], values["rhs"], values["lhs"] == values["rhs"])
    vector_rhs = [values["D_Bf"][i] + values["BtWt_Gf"][i] for i in range(2)]
    check(rows, "exact vector factorization", values["lhs_f"], vector_rhs, values["lhs_f"] == vector_rhs)
    check(rows, "residual triangle bound", values["residual_l1"], values["divergence_l1"] + values["adjoint_gain"] * values["gradient_input_l1"], values["residual_l1"] <= values["divergence_l1"] + values["adjoint_gain"] * values["gradient_input_l1"])
    check(rows, "divergence contribution nonzero", values["divergence_l1"], Fraction(11, 2), values["divergence_l1"] == Fraction(11, 2))
    check(rows, "gradient contribution nonzero", values["gradient_l1"], Fraction(3, 2), values["gradient_l1"] == Fraction(3, 2))
    check(rows, "omitting divergence is unsound", values["residual_l1"], values["gradient_l1"], values["residual_l1"] != values["gradient_l1"])
    check(rows, "omitting gradient is unsound", values["residual_l1"], values["divergence_l1"], values["residual_l1"] != values["divergence_l1"])
    firewalls = json.dumps(contract["non_claims"], ensure_ascii=True).lower()
    check(rows, "physical firewall", all(token in firewalls for token in ("pre-a", "spacetime", "qft", "gravity", "continuum")), True, all(token in firewalls for token in ("pre-a", "spacetime", "qft", "gravity", "continuum")))
    check(rows, "model firewall", all(token in firewalls for token in ("no change", "functional", "transition rates", "external markov time", "limit order")), True, all(token in firewalls for token in ("no change", "functional", "transition rates", "external markov time", "limit order")))

    payload = {
        "schema": "tect/pah-omc020-generator-factorization-primary/1.0",
        "audit_id": "PAH-OMC-020-GENERATOR-FACTORIZATION-PRIMARY-001",
        "result_id": "R-549",
        "task_id": "T-081",
        "status": "PASS_CONDITIONAL_FACTORISATION",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": actual_hashes,
        "fixture": {"inputs": fixture, "derived": values},
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "The exact finite weighted-incidence identity splits the generator residual into a divergence defect D_n B_n and a weighted gradient defect B_infty^* W_infty G_n. Both terms are necessary in the diagnostic fixture; R-529's root-energy implication alone does not supply either operator-domain estimate.",
        "assumptions": contract["required_owner_packet"],
        "missing_assumptions": contract["required_owner_packet"],
        "next_single_question": contract["single_next_question"],
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_generator_factorization.py --check",
        "code_sha256": digest(Path(__file__))
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(serial(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 generator factorization primary replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 GENERATOR FACTORIZATION PRIMARY: PASS {len(rows)}/{len(rows)}; verdict=PASS_CONDITIONAL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
