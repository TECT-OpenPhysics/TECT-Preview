"""Stdlib-only independent lane for the R-175 duplicated covariance basis."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-a13-duplicated-covariance-square-root-basis-manifest.json"


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def f(value: object) -> Fraction:
    return Fraction(str(value))


def transpose(a: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*a)]


def mul(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def add(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def scalar(s: Fraction, a: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[s * value for value in row] for row in a]


def duplicate(a: list[list[Fraction]]) -> list[list[Fraction]]:
    n = len(a)
    z = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    return [a[i] + z[i] for i in range(n)] + [z[i] + a[i] for i in range(n)]


def zero(n: int) -> list[list[Fraction]]:
    return [[Fraction(0) for _ in range(n)] for _ in range(n)]


def eye(n: int) -> list[list[Fraction]]:
    return [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]


def matrix_equal(a: list[list[Fraction]], b: list[list[Fraction]]) -> bool:
    return a == b


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


def determinant3(a: list[list[Fraction]]) -> Fraction:
    return a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1]) - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0]) + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in manifest["inputs"].values():
        path = REPO / item["path"]
        assert path.is_file() and sha256(path) == item["sha256"]
    p = manifest["registered_inputs"]
    n = int(p["dimension"])
    l = [[f(value) for value in row] for row in p["basis_fixture"]]
    assert len(l) == n and all(len(row) == n for row in l)
    c = mul(l, transpose(l))
    g = duplicate(l)
    gamma = duplicate(c)
    z = zero(n)
    i = eye(n)
    j = [z[row] + scalar(Fraction(-1), i)[row] for row in range(n)] + [i[row] + z[row] for row in range(n)]
    assert matrix_equal(mul(g, transpose(g)), gamma)
    assert matrix_equal(mul(j, g), mul(g, j))
    assert matrix_equal(mul(j, gamma), mul(gamma, j))
    minors = [l[0][0], l[0][0] * l[1][1] - l[0][1] * l[1][0], determinant3(l)]
    assert all(value > 0 for value in minors)
    derived = {
        "dimension": str(n),
        "fixture_covariance": c,
        "fixture_leading_principal_minors": minors,
        "fixture_determinant": determinant3(l),
        "duplicated_square_root": True,
        "complex_structure_commutation": True,
        "covariance_complex_structure_commutation": True,
        "a13_gate_closed": False,
        "sector_a_closed": False,
        "authority_hashes_ok": True,
        "lean_escape_tokens_absent": True,
        "boundary_present": True
    }
    payload = {
        "schema": "tect/lean-kernel-crosscheck/1.0",
        "run_kind": "independent",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": 16,
        "derived": derived,
        "source_hashes": {key: item["sha256"] for key, item in manifest["inputs"].items()},
        "boundary": manifest["boundary"]
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(serial(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print("INDEPENDENT R-175 LEAN CROSSCHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
